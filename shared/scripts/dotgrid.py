"""dotgrid.py: measure from a photo taken on the user's 5 mm dot-grid paper (shared/dot-paper.md).
Finds the dots, fits a homography from each dot to its grid position, and writes the photo flattened into paper
coordinates at 20 px/mm, so tilt and zoom drop out. Only things lying in the paper's plane are to scale.
Needs: opencv-contrib-python-headless, scipy and pillow (the start hook's setup-env.sh installs them)
Run:   python3 -I dotgrid.py PHOTO [--pitch 5.0] [--ppmm 20] [--outline X0 Y0 X1 Y1]
       --outline fits a rounded rectangle to the darkest drawn line inside that box (mm, in the flattened image).
"""
import sys, json, argparse, numpy as np, cv2
from scipy.spatial import cKDTree
from scipy.optimize import least_squares

def exif(path):
    try:
        from PIL import Image; from PIL.ExifTags import TAGS
        e=Image.open(path)._getexif() or {}; d={TAGS.get(k,k):v for k,v in e.items()}
        return {k:(float(d[k]) if k in d else None) for k in ('SubjectDistance','DigitalZoomRatio','FocalLength')}
    except Exception: return {}

def find_dots(g):
    p=cv2.SimpleBlobDetector_Params()
    p.filterByArea=True; p.minArea=8; p.maxArea=600; p.filterByCircularity=True; p.minCircularity=0.6
    p.filterByInertia=False; p.filterByConvexity=False; p.minThreshold=40; p.maxThreshold=220
    return np.array([k.pt for k in cv2.SimpleBlobDetector_create(p).detect(g)])

def pitch_px(pts):
    d,_=cKDTree(pts).query(pts,k=2); return float(np.median(d[:,1]))   # nearest-neighbor spacing

def grid_homography(pts,P):
    """dot index -> image px; keeps the largest consistent lattice"""
    c=pts[np.argmin(((pts-np.median(pts,0))**2).sum(1))]
    d,i=cKDTree(pts).query(c,k=5); v=pts[i[1:]]-c
    ax=v[np.argmin([abs(np.arctan2(y,x)) if x>0 else 9 for x,y in v])]          # neighbor along +x
    ang=np.arctan2(ax[1],ax[0]); R=np.array([[np.cos(ang),np.sin(ang)],[-np.sin(ang),np.cos(ang)]])
    idx=np.round(((pts-c)@R.T)/P); inl=np.ones(len(pts),bool)
    for _ in range(5):
        Hm,mask=cv2.findHomography(idx[inl].astype(np.float32),pts[inl].astype(np.float32),cv2.RANSAC,0.15*P)
        q=cv2.perspectiveTransform(pts[None].astype(np.float64),np.linalg.inv(Hm))[0]
        idx=np.round(q); res=np.linalg.norm(q-idx,axis=1); inl=res<0.2
    return Hm,idx,res,inl

def rect_dist(p,Q):
    cx,cy,a,L,W,R=p; c,s=np.cos(a),np.sin(a); d=Q-[cx,cy]
    x=d[:,0]*c+d[:,1]*s; y=-d[:,0]*s+d[:,1]*c
    qx=np.abs(x)-(W/2-R); qy=np.abs(y)-(L/2-R)
    return np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-R

def fit_outline(flat,ppmm,box,thr=130):
    x0,y0,x1,y1=[int(round(v*ppmm)) for v in box]; sub=flat[y0:y1,x0:x1]
    n,lab,st,_=cv2.connectedComponentsWithStats((sub<thr).astype(np.uint8),8)
    keep=np.zeros(n,bool); keep[1:]=st[1:,cv2.CC_STAT_AREA]>(2*ppmm)**2   # drop the dots
    ys,xs=np.nonzero(keep[lab]); Q=np.c_[xs+x0,ys+y0]/ppmm
    ext=Q.max(0)-Q.min(0); tall=ext[1]>=ext[0]
    p0=[*Q.mean(0),0.0,max(ext),min(ext),min(ext)/6] if tall else [*Q.mean(0),np.pi/2,max(ext),min(ext),min(ext)/6]
    r=least_squares(lambda p: rect_dist(p,Q),p0,loss='soft_l1',f_scale=0.3)
    e=np.abs(rect_dist(r.x,Q))
    return dict(center_mm=r.x[:2].round(2).tolist(),angle_deg=round(float(np.degrees(r.x[2])),2),
                length_mm=round(float(r.x[3]),2),width_mm=round(float(r.x[4]),2),corner_r_mm=round(float(r.x[5]),2),
                resid_median_mm=round(float(np.median(e)),3),resid_p90_mm=round(float(np.percentile(e,90)),3),points=int(len(Q)))

def main():
    a=argparse.ArgumentParser(); a.add_argument('photo'); a.add_argument('--pitch',type=float,default=5.0)
    a.add_argument('--ppmm',type=float,default=20.0); a.add_argument('--outline',type=float,nargs=4)
    o=a.parse_args()
    g=cv2.cvtColor(cv2.imread(o.photo),cv2.COLOR_BGR2GRAY)
    ex=exif(o.photo); pts=find_dots(g); P=pitch_px(pts)
    Hm,idx,res,inl=grid_homography(pts,P)
    i0=idx[inl].min(0)-2; i1=idx[inl].max(0)+2; S=o.pitch*o.ppmm
    T=np.array([[S,0,-i0[0]*S],[0,S,-i0[1]*S],[0,0,1]])@np.linalg.inv(Hm)
    W,H=int((i1[0]-i0[0])*S),int((i1[1]-i0[1])*S)
    flat=cv2.warpPerspective(g,T,(W,H),flags=cv2.INTER_LINEAR,borderValue=255)
    out=o.photo.rsplit('.',1)[0]+'_flat.png'; cv2.imwrite(out,flat)
    rep=dict(photo=o.photo,exif=ex,dots=int(len(pts)),dots_on_grid=int(inl.sum()),pitch_px=round(P,2),
             grid_resid_median_cells=round(float(np.median(res[inl])),3),grid_resid_max_cells=round(float(res[inl].max()),3),
             flat_image=out,flat_ppmm=o.ppmm,flat_size_mm=[round(W/o.ppmm,1),round(H/o.ppmm,1)])
    if ex.get('DigitalZoomRatio') and ex['DigitalZoomRatio']>1.05: rep['note']='photo used digital zoom; the dot mapping still corrects scale'
    if o.outline: rep['outline']=fit_outline(flat,o.ppmm,o.outline)
    print(json.dumps(rep,indent=1))
if __name__=='__main__': main()

# Clean redraw of the small calibration stand: changes 2-23, light clips cut from the real Barrina clip mesh.
# Run from this folder: python3 clean7.py   (reads /mnt/project-files/3mfs/barrinaClip_rev2.3mf)
import sys, zipfile, re, numpy as np, trimesh
sys.argv=[sys.argv[0]]
exec(open("final_lib.py").read())
from shapely.geometry import Polygon as SP, Point, LineString
from shapely.ops import polygonize
sys.path.insert(0, os.path.abspath("../../../../../barrina-clips/build"))  # barrina-clips build, run from small/
import barrinaClip_rev2 as B
CLIP3MF="/mnt/project-files/3mfs/barrinaClip_rev2.3mf"
# ---------------- values (mm; x from the board's center line, right side; mirrored for the left) ----------------
H=170; BH=18; TB0,TB1=H-3,H+15; HB=BW/2; DEP=30; GLUE=0.15; LAP=20
PX0,PX1=149,165; HX,HZ=131,120; LX=125
U_TOP=17.4; U_HALF=12.36           # clip-local: bar centered at 0, back face y=10, U top y=17.4, outer wall faces x=+-12.36
LZ=31.0                            # change 18: light stays at 31; the block fills the 0.64 under the fixed wall
# ---------------- 1. the clip profile, read from the 3mf mesh ----------------
def load_mesh(p):
    t=zipfile.ZipFile(p).read([n for n in zipfile.ZipFile(p).namelist() if n.startswith("3D/Objects/")][0]).decode()
    v=np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"',t),float); f=np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"',t),int)
    return trimesh.Trimesh(v,f,process=True)
def section(m,z):
    L=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1]); segs=[LineString(L.vertices[e.points][:,:2]) for e in L.entities]
    ps=list(polygonize(unary_union(segs))); g=ps[0]
    for p in ps[1:]: g=g.symmetric_difference(p)
    return g
mesh=load_mesh(CLIP3MF)
sec=max(getattr(section(mesh,-8.0),"geoms",[None]),key=lambda g:g.area)    # z -8 = 8.2 mm into the clip: U body only (no neck)
ref=B.profile(); sec=affinity.translate(sec,ref["body"].bounds[0]-sec.bounds[0],ref["body"].bounds[1]-sec.bounds[1])
MISMATCH=sec.symmetric_difference(ref["body"]).area
c=ref["bar"].centroid
CLIP=affinity.rotate(affinity.translate(sec,-c.x,-c.y),-B.TH,origin=(0,0))     # untilted: bar -10..10 square
# keep the snap U as printed (walls, bumps, hinge slot + bridge, tab, rounded edges); drop the shelf-only parts above the U top and the tilt wedge
SNAP=CLIP.intersection(sbox(-30,-30,U_HALF,U_TOP))
SLOT_TOP=U_TOP-B.HINGE_BRIDGE                                         # 14.92
FREE_SWING=SP([(-U_HALF,-17),(-U_HALF-3,-17),(-U_HALF-3,-10),(-U_HALF,SLOT_TOP)])  # air the free wall swings into: 3 mm at its tip, 0 at its root
CLIP_ZONE=unary_union([sbox(-U_HALF,-17,-B.HALF_IN+B.SLOT_W,U_TOP),   # free wall + hinge slot + bridge, as in the 3mf
                       sbox(-B.HALF_IN+B.SLOT_W,-17,U_HALF,10),          # bar pocket, bumps and fixed wall (block may meet the back face and fixed wall)
                       FREE_SWING,sbox(-10.5,-40,10.5,-10)])             # swing room + mouth
SLOT=sbox(-B.HALF_IN+0.05,10.05,-B.HALF_IN+B.SLOT_W-0.05,U_TOP-B.HINGE_BRIDGE-0.05)   # the 3mf hinge slot
FREE_AIR=sbox(-U_HALF-1.2,-9.0,-U_HALF-0.05,U_TOP-B.HINGE_BRIDGE-0.3)      # air the free wall needs outside it, up to its hinge root
def place(g,ang,cx,cz,mirror):
    if mirror: g=affinity.scale(g,xfact=-1,origin=(0,0))
    return affinity.translate(affinity.rotate(g,ang,origin=(0,0)),cx,cz)
P=lambda x,y,ang,cx,cz,m: place(Point(x,y),ang,cx,cz,m)
# low clip: back toward the post, free wall on top, opening toward the board (rotate -90)
LOW=dict(ang=-90,c=(LX,LZ),m=False); HIGH=dict(ang=-45,c=(HX,HZ),m=True)   # high: lit face 45 deg down-in, free wall lower
def plc(g,k): return place(g,k["ang"],*k["c"],k["m"])
# ---------------- 2. side frame (change 23: post + foot + top-bar end + both clips, one piece, printed on its side) ----------------
CUT_TOP=None
PIECES=[0]
def side_frame():
    lowU,highU=plc(SNAP,LOW),plc(SNAP,HIGH)
    # low block: from the U's back face to the post, top wall height; plus the 0.64 strip under the fixed wall
    lb=plc(sbox(-U_HALF,10,U_HALF,U_TOP),LOW)                               # the U's back plate
    lowfill=unary_union([sbox(lb.bounds[0],BH,PX0+1,lb.bounds[3]),sbox(LX-10,BH,PX0+1,LZ-U_HALF+0.01)])
    # high block: from the back plate's top edge straight across to the post
    a=P(-U_HALF,U_TOP,**{"ang":-45,"cx":HX,"cz":HZ,"m":True}); b=P(U_HALF,U_TOP,**{"ang":-45,"cx":HX,"cz":HZ,"m":True})
    hb=plc(sbox(-U_HALF,10,U_HALF,U_TOP),HIGH)
    from shapely.geometry import MultiPoint
    highfill=unary_union([hb,MultiPoint([(a.x,a.y),(b.x,b.y),(PX0+1,b.y),(PX0+1,a.y)]).convex_hull])
    post=sbox(PX0,BH,PX1,TB0)
    foot=SP([(HB,0),(PX1-6,0),(PX1,6),(PX1,BH),(HB,BH)]).buffer(3,join_style=1).buffer(-3,join_style=1).intersection(sbox(HB,0,PX1,BH))
    topend=topbar().intersection(sbox(CUT_X,TB0,PX1+1,TB1+1))
    solid=unary_union([post,foot,topend,lowfill,highfill]).buffer(2,join_style=1).buffer(-2,join_style=1)   # r2 inside corners
    # inside each clip's zone only the 3mf U exists: the block may touch just the back plate's outer face (local y>=17.4)
    # and the fixed wall's outer face (local x>=12.36); the hinge slot, the free wall and 3 mm of air outside it stay as in the 3mf
    keep=unary_union([plc(CLIP_ZONE,LOW),plc(CLIP_ZONE,HIGH)])
    solid=solid.difference(keep)
    body=unary_union([solid,lowU,highU]).buffer(0)
    PIECES[0]=len(getattr(body,"geoms",[body]))                          # counted before keeping the largest
    if body.geom_type!="Polygon": body=max(body.geoms,key=lambda g:g.area)
    body=SP(body.exterior,[i for i in body.interiors if SP(i).area>1.0])    # drop boolean slivers
    return body
def topbar():
    s=sbox(-PX1,TB0,PX1,TB1)
    for sg in (-1,1):
        cx=sg*(PX1-16); cor=sbox(min(cx,sg*PX1),H-1,max(cx,sg*PX1),TB1).difference(Point(cx,H-1).buffer(16,64)); s=s.difference(cor)
    return s
# ---------------- 3. cradle (change 21, turned 90 deg) and the top middle ----------------
PH_L,PH_W=152.8,72.0; LENS_END,LENS_SIDE=26.0,28.0; WALL=1.86
PCX=PH_L/2-LENS_END; PCY=PH_W/2-LENS_SIDE                    # phone center from the lens point (lens over board center)
CRL,CRW=PH_L+1+2*WALL+2,PH_W+1+2*WALL+2
CRAD=sbox(PCX-CRL/2,PCY-CRW/2,PCX+CRL/2,PCY+CRW/2).buffer(-12,join_style=1).buffer(12,join_style=1)   # plan, y from board center
POCKET=sbox(PCX-PH_L/2-0.5,PCY-PH_W/2-0.5,PCX+PH_L/2+0.5,PCY+PH_W/2+0.5).buffer(-4,join_style=1).buffer(4,join_style=1)
CAMWIN=sbox(-PH_L/2+PCX+13-0.5,PCY-65/2-0.5,-PH_L/2+PCX+13+22+0.5,PCY+65/2+0.5)
CUT_L,CUT_R=CRAD.bounds[0],CRAD.bounds[2]                     # top cuts at the cradle's ends
CUT_X=None
# ---------------- 4. camera and glare ----------------
LENS_Z=H-4.0; D0=LENS_Z-FL; KL,KS=0.6955,0.5215
def frame_half(z): return KL*(LENS_Z-z), KS*(LENS_Z-z)
def lapzone(side,kind):
    if kind=="top": x0=(CUT_R if side>0 else -CUT_L); return sbox(x0,TB0-1,x0+LAP,TB1+1)
    return sbox(HB,-1,HB+LAP,BH+1)
def parts():
    global CUT_X
    out={}
    for side,cut in ((1,CUT_R),(-1,-CUT_L)):
        CUT_X=cut; out[f"{'right' if side>0 else 'left'} side frame (on its side)"]=side_frame()
    bar=topbar().intersection(sbox(CUT_L-LAP,TB0-1,CUT_R+LAP,TB1+1))
    out["top middle + cradle (flat, plan)"]=unary_union([CRAD,sbox(CUT_L-LAP,-15,CUT_R+LAP,15)])
    out["board + base middle (flat, plan)"]=unary_union([sbox(-HB,-CY,HB,CY),sbox(-HB-LAP,0,HB+LAP,15)])
    return out
fails=[]
def chk(n,cnd,i=""):
    print(("PASS " if cnd else "FAIL ")+n+(" "+i if i else ""));
    if not cnd: fails.append(n)
if __name__=="__main__":
    chk("clip profile = 3mf mesh section",MISMATCH<0.01,f"(mismatch {MISMATCH:.3f} mm2)")
    frames={}
    for side,cut in ((1,CUT_R),(-1,-CUT_L)):
        CUT_X=cut; f=side_frame(); frames[side]=f
        chk(f"{'right' if side>0 else 'left'} side frame is one solid",PIECES[0]==1,f"({PIECES[0]} piece)")
    f=frames[1]
    for nm,k in (("low",LOW),("high",HIGH)):
        bar=plc(sbox(-10,-10,10,10),k); ov=bar.intersection(f).area
        chk(f"{nm} light touches only the snap bumps",ov<8.5,f"({ov:.1f} mm2; two bumps = 8.0)")
        U=plc(SNAP,k); mis=U.difference(f).area
        chk(f"{nm} clip keeps every part of the 3mf snap U",mis<0.05,f"({mis:.2f} mm2 missing)")
        same=plc(CLIP_ZONE,k).intersection(f).symmetric_difference(plc(CLIP_ZONE,k).intersection(U)).area
        chk(f"{nm} clip zone holds exactly the 3mf U (nothing added, nothing removed)",same<0.1,f"({same:.2f} mm2 different)")
        sl=plc(SLOT,k).intersection(f).area; chk(f"{nm} hinge slot open, where the 3mf has it",sl<0.01,f"({sl:.2f} mm2 filled)")
        air=plc(FREE_SWING,k).difference(U).intersection(f).area
        chk(f"{nm} free wall: swing room outside it (3 mm at the tip to 0 at the hinge)",air<0.05,f"({air:.2f})")
    gapz=sbox(LX-9,BH,LX+9,LZ-U_HALF); chk("low fixed wall sits on solid block (no gap under it)",gapz.difference(f).area<0.01)
    hbar=plc(sbox(-10,-10,10,10),HIGH); chk("high light clears the top bar",hbar.distance(topbar())>5,f"({hbar.distance(topbar()):.1f})")
    # camera: nothing of the stand or lights inside the frame at its height
    worst=99
    for g in (f,plc(sbox(-10,-10,10,10),LOW),hbar):
        for x,z in np.array(g.exterior.coords):
            if BH+0.01<z<LENS_Z-5: worst=min(worst,x-frame_half(z)[0])
    chk("clips, posts and lights out of the photo (long side across)",worst>0,f"(closest {worst:.1f} mm outside)")
    fo=max(frame_half(z)[0]-x for x,z in np.array(f.exterior.coords) if z<=BH+0.01)
    print(f"NOTE foot blocks reach {fo:.1f} mm into the photo's side edges, beside the board (x {HB:.0f} to {HB+fo:.0f}, 0 to {BH} high)")
    # glare rule on every lit-face point
    def lit(k): return [np.array(p) for p in plc(sbox(-7,-10.0,7,-10.0+0.01),k).exterior.coords]
    g=min(p[0]-(67.5*(1+(p[1]-FL)/D0)+3) for k in (LOW,HIGH) for p in lit(k))
    chk("glare rule, every lit-face point, 3 mm margin",g>0,f"(margin {g:.1f})")
    # parts and plate fit (P1S 256 x 256, excluded corner 18 x 28, 0.5 margin)
    plate=sbox(0,0,256,256).difference(sbox(0,0,18,28)).buffer(-0.5)
    def fits(g):
        for ang in range(0,180,3):
            r=affinity.rotate(g,ang,origin=(0,0)); b=r.bounds
            for ox in np.arange(0.5,256-(b[2]-b[0]),4):
                for oy in np.arange(0.5,256-(b[3]-b[1]),4):
                    if plate.contains(affinity.translate(r,ox-b[0],oy-b[1])): return ang
        return None
    for nm,g in parts().items(): a=fits(g); chk(f"{nm} fits the plate",a is not None,f"({g.bounds[2]-g.bounds[0]:.0f} x {g.bounds[3]-g.bounds[1]:.0f}, turned {a} deg)")
    print("cradle x",round(CUT_L,1),round(CUT_R,1)," fails:",fails)

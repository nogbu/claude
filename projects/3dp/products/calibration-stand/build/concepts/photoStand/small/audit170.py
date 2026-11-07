import numpy as np
from shapely.geometry import box
BW,BD,FL,RL=170,132,6.6,8.7
H=170; BUMP=(3.3,4.0)                  # cradle floor top above table; camera bump sources disagree
LENS=H-max(BUMP)                        # worst case: lowest lens
D0=LENS-FL                              # lens to board floor
TX,TY=np.tan(np.radians(41))*0.8/1.0,None
# 82 deg diagonal, 4:3 -> half-widths per unit distance
diag=2*np.tan(np.radians(41)); kL=diag*0.8/2; kS=diag*0.6/2        # half-width factors (long, short)
PX=8160
CX,CY=BW/2,BD/2
def frame(z,long_axis):                  # z above board floor
    d=D0-z; hx,hy=(kL*d,kS*d) if long_axis=="x" else (kS*d,kL*d)
    return box(CX-hx,CY-hy,CX+hx,CY+hy),d
markers=[]
for i in range(3):
    for x in (3.2,BW-14.4): markers.append(("rail",box(x,10+25*i,x+11.16,21.16+25*i),RL-FL))
for i in range(5): markers.append(("back row",box(28+25*i,BD-20,39.16+25*i,BD-8.84),RL-FL))
for x0 in (0.8,BW-15.8):
    markers.append(("15 mm step",box(x0+1.9,BD-35.1,x0+13.06,BD-23.94),15)); markers.append(("30 mm column",box(x0+1.9,BD-19.1,x0+13.06,BD-7.94),30))
stop=BD-27
pieces=[("temperature (5 blocks)",44.5,50,10),("max vol. speed comb, 50% (on its back)",90,65,50),("pressure advance pattern",98.8,55.4,1.2),
        ("flow ratio YOLO Recommended",123,94,2),("retraction tower (on its back)",40,80,15)]
chan=box(17.5,0,BW-17.5,stop)
out=[]
for la in ("y","x"):
    print(f"\n=== phone long axis along {la} ({'current cradle' if la=='y' else 'cradle turned 90 deg'}) ; lens-to-floor {D0:.1f} mm ===")
    f0,_=frame(0,la); print(f"frame at board floor: {f0.bounds[2]-f0.bounds[0]:.1f} x {f0.bounds[3]-f0.bounds[1]:.1f} mm (x by y)")
    bad=[]
    for nm,m,z in markers:
        f,_=frame(z,la)
        if not f.contains(m.buffer(1.86)): bad.append((nm,round(z,1),round(m.bounds[0],1)))
    print("markers out of frame (incl. 1 white cell margin):",bad if bad else "none", f"({len(markers)} total)")
    for nm,w,dep,z in pieces:
        p=box(CX-w/2,stop-dep,CX+w/2,stop)
        f,d=frame(z,la)
        fits=chan.contains(p); inf=f.contains(p)
        mar=min(p.bounds[0]-f.bounds[0],f.bounds[2]-p.bounds[2],p.bounds[1]-f.bounds[1],f.bounds[3]-p.bounds[3])
        long=(f.bounds[2]-f.bounds[0]) if la=="x" else (f.bounds[3]-f.bounds[1])
        print(f"  {nm}: fits channel {fits}; face in frame {inf} (margin {mar:.1f}); {PX/long:.0f} px/mm at its face")
# glare (lens axis at board center; r measured horizontally from lens axis)
a=(BW-35)/2
for nm,r,z in (("high lights",132,120-FL),("low lights",125,31-FL)):
    need=a*(1+z/D0)+3
    print(f"glare {nm}: r={r} vs needed {need:.1f} -> {'PASS' if r>need else 'FAIL'}")
# view cone vs stand parts (long axis x worst for x)
for nm,x,z in (("post inner face",149,0),("high light lit face",132-14.1,120-FL),("low light lit face",115,21-FL),("low clip pull tab",125-4-4.24-0.93,31+10.5+1.86+4.24-FL),("high clip pull tab",137.9-0.93,120-11.6-6-FL)):
    for la in ("x","y"):
        f,d=frame(z,la); hx=(f.bounds[2]-f.bounds[0])/2
        print(f"in view? {nm} (x {x:.1f} from center... ) long axis {la}: view half-width at its height {hx:.1f} -> {'IN VIEW' if x<hx else 'clear'}")

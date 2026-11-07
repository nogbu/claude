import sys, os; sys.path.insert(0, os.path.abspath(".."))  # photoStand/, run from small/
import numpy as np, matplotlib, trimesh
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import box as sbox, Point
from shapely import affinity
from shapely.ops import unary_union
import renderlib as R
import rev1_concept as A
BONE=np.array([0.86,0.84,0.78]); BAR=np.array([0.62,0.62,0.64]); LED=np.array([1.0,0.85,0.25]); PHONE=np.array([0.55,0.62,0.72]); MK=np.array([0.1,0.1,0.1])
BW,BD=170,132; CX,CY=BW/2,BD/2; H=160; FL=6.6; RL=FL+2.1          # placeholders
PX0,PX1=149,165; LX,HX,HZ=125,140,120
def bx(a,b,c,d): return sbox(a,c,b,d)
def rsq(cx,cz,half,ang): return affinity.rotate(sbox(cx-half,cz-half,cx+half,cz+half),ang,origin=(cx,cz))
def mesh_faces(m,col):
    for f,n in zip(m.vertices[m.faces],m.face_normals): R.FACES.append((f.copy(),n.copy(),col,False))
def ext_z(poly,z0,z1,col,dx=0,dy=0):
  for poly in getattr(poly,"geoms",[poly]):
    m=trimesh.creation.extrude_polygon(poly,z1-z0,engine="earcut"); m.apply_translation([dx,dy,z0]); mesh_faces(m,col)
def ext_y(poly,y0,y1,col,dx=0):
  for poly in getattr(poly,"geoms",[poly]):
    m=trimesh.creation.extrude_polygon(poly,y1-y0,engine="earcut"); v=m.vertices.copy(); m.vertices=np.c_[v[:,0]+dx,y0+v[:,2],v[:,1]]; m.fix_normals(); mesh_faces(m,col)
def biggest(s): return max(getattr(s,'geoms',[s]),key=lambda g:g.area)
def high_clip():
    return [rsq(HX,HZ,14,45), bx(146,PX0+1,110,130)]
def keepouts(low=True):
    k=[rsq(HX,HZ,10.5,45)]; n=np.array([-1,-1])/np.sqrt(2); c=np.array([HX,HZ])+n*12
    k.append(affinity.rotate(bx(c[0]-7,c[0]+7,c[1]-4,c[1]+4),-45,origin=tuple(c)))
    if low: k+= [bx(LX-10.5,LX+10.5,14,34.5), bx(70,LX-10.5,14,40)]
    return unary_union(k)
def finish(parts,keep,extra=()):
    s=unary_union(parts).buffer(8,join_style=1).buffer(-8,join_style=1)
    s=unary_union([s,*extra]).difference(keep)
    return biggest(s.buffer(-1,join_style=1).buffer(1,join_style=1))
def side_feet():      # option 1: foot + post + both clips
    parts=[bx(86,PX1,0,14),bx(74,86,RL,14),bx(PX0,PX1,0,H-3),bx(135.5,140,14,37),bx(128,140,34.5,38)]+high_clip()
    return finish(parts,keepouts(),[bx(77,83,RL-4,RL),bx(153,161,H-3,H+5)])
def post_plain():     # option 2: post + high clip, tenons both ends
    parts=[bx(PX0,PX1,12,H-3)]+high_clip()
    return finish(parts,keepouts(False),[bx(153,161,4,12),bx(153,161,H-3,H+5)])
def base_half():      # option 2: C-shaped caddy half (plan view), right half
    w=10.4; c=[bx(85.5,95.9,-10.9,BD+10.9),bx(0,95.9,-10.9,-0.5),bx(0,95.9,BD+0.5,BD+10.9),bx(95.9,PX1+4,CY-20,CY+20)]
    s=unary_union(c).buffer(3,join_style=1).buffer(-3,join_style=1)
    return s.difference(bx(-5,0,-20,BD+20))
def topbar_profile():
    s=bx(-PX1,PX1,H-3,H+15)
    for sg in (-1,1):
        cx=sg*(PX1-16); cor=bx(*sorted([cx,sg*PX1]),H-1,H+15).difference(Point(cx,H-1).buffer(16))
        s=s.difference(cor)
    return s.difference(bx(-46,46,H-10,H+30))
CR=bx(-46,46,CY-82,CY+82).buffer(-5,join_style=1).buffer(5,join_style=1)
def board():
    A.box(0,BW,0,BD,0,FL,A.BOARD); A.box(0,17.5,0,BD,FL,RL,A.BOARD); A.box(BW-17.5,BW,0,BD,FL,RL,A.BOARD); A.box(17.5,BW-17.5,BD-27,BD,FL,RL,A.BOARD)
    for x in (8.8,BW-8.8): A.box(x-7.45,x+7.45,BD-21,BD-6,0,30+FL-4.2,A.BOARD)
    for i in range(4):
        for x in (3.2,BW-14.4): A.box(x,x+11.2,10+25*i,21.2+25*i,RL,RL+0.2,MK)
    A.box(17.5,BW-17.5,BD-27-40,BD-27-38.5,FL-0.05,FL+0.05,MK)          # brim groove
def common():
    ext_y(topbar_profile(),CY-15,CY+15,BONE,dx=CX)
    ext_z(CR.difference(bx(-38,38,CY-78,CY+78)),H-3,H+12.6,BONE,dx=CX); ext_z(CR.difference(bx(-20,20,CY-30,CY+10).buffer(4)),H-3,H,BONE,dx=CX)
    A.box(CX-36,CX+36,CY-76,CY+76,H+0.3,H+8.9,PHONE)
    for s in (-1,1):
        A.rbox(CX+s*HX,HZ,20,20,45*s,CY-149,CY+149,BAR)
        nn=np.array([-s,-1])/np.sqrt(2); c=np.array([CX+s*HX,HZ])+nn*10.15; A.rbox(c[0],c[1],14,0.3,45*s,CY-149,CY+149,LED)
def lowbar(s,z):
    lx=CX+s*LX; A.box(lx-10,lx+10,CY-149,CY+149,z,z+20,BAR); A.box(*sorted([lx-s*10,lx-s*10.3]),CY-149,CY+149,z+3,z+17,LED)
def build(opt):
    R.FACES.clear(); board(); common()
    for s in (-1,1):
        if opt==1:
            ext_y(affinity.scale(side_feet(),xfact=s,origin=(0,0)),CY-15,CY+15,BONE,dx=CX); lowbar(s,14)
        else:
            ext_y(affinity.scale(post_plain(),xfact=s,origin=(0,0)),CY-15,CY+15,BONE,dx=CX)
            ext_z(affinity.scale(base_half(),xfact=s,origin=(0,0)),0,12,BONE,dx=CX)
            lx=CX+s*LX; A.box(*sorted([lx+s*10.5,lx+s*14.5]),CY-20,CY+20,12,20,BONE); lowbar(s,12)
def render(opt,ax):
    build(opt)
    pv=np.vstack([F for F,_,c,_ in R.FACES if c is BONE]); av=np.vstack([F for F,_,_,_ in R.FACES]); pmin,pmax=pv.min(0),pv.max(0); pd=pmax-pmin
    eye=(-1.0,-1.6,0.8); e=np.array(eye); e=e/np.linalg.norm(e); rt=np.cross(-e,[0,0,1.]); rt/=np.linalg.norm(rt); up=np.cross(rt,-e)
    sx,sy=av@rt,av@up
    img,cam=R.render(eye,2.6,(0.3,-0.7,1.0),(sx.min()-60,sx.max()+70,sy.min()-40,sy.max()+40)); ax.imshow(img); ax.axis("off")
    def P2(p): return np.array(R.proj(cam,np.array(p,float)))
    def dim(a,b,off,txt):
        a=np.array(a,float); b=np.array(b,float); o=np.array(off,float); A2,B2,A3,B3=P2(a),P2(b),P2(a+o),P2(b+o)
        for p,q in ((A2,A3),(B2,B3)): ax.plot([p[0],q[0]],[p[1],q[1]],color="#c0392b",lw=0.7,ls=(0,(3,2)))
        ax.annotate("",xy=B3,xytext=A3,arrowprops=dict(arrowstyle="<|-|>",color="#c0392b",lw=1.2,shrinkA=0,shrinkB=0))
        m=(A3+B3)/2; ax.text(m[0],m[1],txt,color="#c0392b",fontsize=10,fontweight="bold",ha="center",va="center",bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none",alpha=0.9))
    dim([CX-PX1,CY-15,H+15],[CX+PX1,CY-15,H+15],[0,0,30],f"W {pd[0]:.0f}")
    dim([CX+PX1,pmin[1],0],[CX+PX1,pmin[1],pmax[2]],[40,0,0],f"H {pd[2]:.0f}")
    dim([CX+PX1,pmin[1],0],[CX+PX1,pmax[1],0],[35,0,0],f"D {pd[1]:.0f}")
    dim([0,0,0],[BW,0,0],[0,-28,0],f"board {BW} x {BD}")
    dim([CX-46,CY-82,0],[CX-46,CY-82,H],[0,0,0],f"lens {H}")
    return pd
def outline(ax,g,col=BONE):
    for p in getattr(g,'geoms',[g]):
        x,y=p.exterior.xy; ax.fill(x,y,color=col,ec="k",lw=0.7)
        for i in p.interiors: xi,yi=i.xy; ax.fill(xi,yi,color="#eee",ec="k",lw=0.5)
def plate(ax,items,title):
    ax.add_patch(plt.Rectangle((0,0),256,256,fc="#eee",ec="#888")); ax.add_patch(plt.Rectangle((0,0),18,28,fc="#c8c8c8",ec="none"))
    for g in items: outline(ax,g)
    ax.set_xlim(-4,260); ax.set_ylim(-4,260); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title,fontsize=9.5)
def place(g,x,y,ang=0):
    g=affinity.rotate(g,ang,origin="centroid"); b=g.bounds; return affinity.translate(g,x-b[0],y-b[1])
def topbar_plan():
    return unary_union([bx(-PX1,-46,-15,15),bx(46,PX1,-15,15),CR.buffer(0).difference(bx(-38,38,CY-78,CY+78)) if False else affinity.translate(bx(-46,46,-82,82).buffer(-5,join_style=1).buffer(5,join_style=1),0,0)])
def centered(g,ang):
    g=affinity.rotate(g,ang,origin=(0,0)); c=g.centroid; return affinity.translate(g,128-c.x,128-c.y)
RIN=float(sys.argv[1]) if len(sys.argv)>1 else 2
def finish2(parts,keep,extra=()):
    s=unary_union(parts).buffer(RIN,join_style=1).buffer(-RIN,join_style=1)
    s=unary_union([s,*extra]).difference(keep)
    s=biggest(s.buffer(-0.5,join_style=1).buffer(0.5,join_style=1))
    return s
def post_v2():
    # clip arm meets post with small inner fillet; clip ring outer corners softened
    ring=rsq(HX,HZ,14,45).buffer(-3,join_style=1).buffer(3,join_style=1)
    parts=[bx(PX0,PX1,12,H-3),ring,bx(146,PX0+1,113,127),unary_union([ring.intersection(bx(HX-3,PX0+1,90,150)),bx(PX0,PX0+1,100,140)]).convex_hull]
    return finish2(parts,keepouts(False),[bx(153,161,4,12),bx(153,161,H-3,H+5)])
def base_v2():
    c=[bx(85.5,95.9,-10.9,BD+10.9),bx(-1,95.9,-10.9,-0.5),bx(-1,95.9,BD+0.5,BD+10.9),bx(95.9,PX1+4,CY-20,CY+20)]
    s=unary_union(c)
    s=s.buffer(-5,join_style=1).buffer(5,join_style=1)          # outside corners r5 (arms are 10.4 wide)
    s=s.buffer(RIN,join_style=1).buffer(-RIN,join_style=1)      # inside corners r2
    return s.difference(bx(-5,0,-20,BD+20))
def lip_v2():
    return bx(80.5,85.5,-0.5,BD+0.5).union(bx(0,85.5,-0.5,4.5)).union(bx(0,85.5,BD-4.5,BD+0.5)).difference(bx(-5,0,-20,BD+20))
CR2=bx(-46,46,CY-82,CY+82).buffer(-12,join_style=1).buffer(12,join_style=1)
def common2():
    ext_y(topbar_profile(),CY-15,CY+15,BONE,dx=CX)
    ext_z(CR2.difference(bx(-38,38,CY-78,CY+78).buffer(-4,join_style=1).buffer(4,join_style=1)),H-3,H+12.6,BONE,dx=CX)
    ext_z(CR2.difference(bx(-20,20,CY-30,CY+10).buffer(4)),H-3,H,BONE,dx=CX)
    A.box(CX-36,CX+36,CY-76,CY+76,H+0.3,H+8.9,PHONE)
def build2():
    R.FACES.clear()
    for k in (0,):
        pass
    # board raised by lip
    A.box(0,BW,0,BD,1.2,FL+1.2,A.BOARD); A.box(0,17.5,0,BD,FL+1.2,RL+1.2,A.BOARD); A.box(BW-17.5,BW,0,BD,FL+1.2,RL+1.2,A.BOARD); A.box(17.5,BW-17.5,BD-27,BD,FL+1.2,RL+1.2,A.BOARD)
    for x in (8.8,BW-8.8): A.box(x-7.45,x+7.45,BD-21,BD-6,1.2,30+FL-3,A.BOARD)
    for i in range(4):
        for x in (3.2,BW-14.4): A.box(x,x+11.2,10+25*i,21.2+25*i,RL+1.2,RL+1.4,MK)
    common2()
    for s in (-1,1):
        ext_y(affinity.scale(post_v2(),xfact=s,origin=(0,0)),CY-15,CY+15,BONE,dx=CX)
        ext_z(affinity.scale(base_v2(),xfact=s,origin=(0,0)),0,12,BONE,dx=CX)
        ext_z(affinity.scale(lip_v2(),xfact=s,origin=(0,0)),0,1.2,BONE,dx=CX)
        lx=CX+s*LX
        rest=bx(*sorted([lx+s*10.5,lx+s*15.5]),CY-20,CY+20).buffer(-2,join_style=1).buffer(2,join_style=1)
        ext_z(rest,12,20,BONE)

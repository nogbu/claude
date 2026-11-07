import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import renderlib as R
import rev1_concept as A
import rev1_consumer as C
from rev1_consumer import sweep, arc, prism_y, prism_z
BONE=np.array([0.86,0.84,0.78]); BLACK=np.array([0.17,0.17,0.18]); LED=np.array([1.0,0.85,0.25])
PHONE=np.array([0.55,0.62,0.72]); CX,CY=125.5,111.5
TW,TD=23.5,22.5      # slim tube
def tprof(rl=0.6,rb=6,k=6):
    w,h=TW,TD; P=[]
    for cx,cy,r,a0 in ((w/2-rl,rl,rl,270),(w/2-rb,h-rb,rb,0),(-w/2+rb,h-rb,rb,90),(-w/2+rl,rl,rl,180)):
        for t in np.radians(np.linspace(a0,a0+90,k)): P.append((cx+r*np.cos(t),cy+r*np.sin(t)))
    return np.array(P)
def stube(cx,cz,n,y0=-37,y1=265,col=None):
    n=np.array(n,float); n/=np.linalg.norm(n); t=np.array([-n[1],n[0]]); lc=np.array([cx,cz])+n*TD/2
    S=tprof(); Q=[]
    for y in (y0,y1): Q.append([[ (lc+t*u-n*v)[0],y,(lc+t*u-n*v)[1]] for (u,v) in S])
    c=np.array([cx,(y0+y1)/2,cz]); M=len(S)
    for k in range(M): C.add([Q[0][k],Q[0][(k+1)%M],Q[1][(k+1)%M],Q[1][k]],c,BONE)
    C.add(Q[0],c,BONE); C.add(Q[1],c,BONE)
    fc=lc+n*0.15; L=[]
    for y in (y0,y1):
        for u in (-(TW/2-0.8),TW/2-0.8):
            for d in (0,0.3): L.append([*(fc+t*u+n*d)][:1]+[y]+[(fc+t*u+n*d)[1]])
    A.hexa(L,LED)
def tube(cx,cz,ang,lit_dir):
    prism_y(cx,cz,TW/2,TD/2,0.6,ang,-37,265,BONE)
    c=np.array([cx,cz])+np.array(lit_dir)*(TD/2+0.15)
    A.rbox(c[0],c[1],TW-1.5,0.4,ang,-37,265,LED) if ang else A.box(*sorted([c[0]-0.2,c[0]+0.2]),-37,265,cz-TW/2+0.75,cz+TW/2-0.75,LED)
def model(postcol):
    R.FACES.clear()
    A.box(0,251,0,223,0,4.2,A.BOARD)
    # base: two side plates (inner edge 0.5 mm from board) + 30 mm back box behind the board
    xl,xr,yb_,R0=-31.25,282.25,243.5,45
    U=[[xl,-30,4.05],[xl,yb_-R0-30,4.05]]
    U+=[[xl+R0+R0*np.cos(t),yb_-R0+R0*np.sin(t),4.05+11*(1-np.cos(t-np.pi))/2*0+11*np.sin((t-np.pi)/2*-1+0)] for t in []]
    for t in np.linspace(np.pi,np.pi/2,10): U.append([xl+R0+R0*np.cos(t),yb_-R0+R0*np.sin(t),0])
    for x in np.linspace(xl+R0+10,xr-R0-10,6): U.append([x,yb_,0])
    for t in np.linspace(np.pi/2,0,10): U.append([xr-R0+R0*np.cos(t),yb_-R0+R0*np.sin(t),0])
    U+=[[xr,yb_-R0-30,4.05],[xr,-30,4.05]]
    U=np.array(U,float); secs=[]
    for p in U:
        f=np.clip((p[1]-(yb_-R0-30))/(R0+30),0,1)**1.5            # blend low side -> tall back
        hz=4.05+f*(15-4.05); U_z=hz
        p[2]=U_z; secs.append((hz, 31-f*11, 3.5+f*4))
    C.sweep(U,[0,0,1],secs,BLACK)
    A.box(CX-12,CX+12,263.5,272,10,22,BLACK)                     # cord clamp at the single exit
    # low tubes: lit face 159 mm from center, in black saddles
    for s in (-1,1):
        cx=CX+s*(159+TD/2); cz=8.1+2+TW/2
        for y in (20,180): prism_y(cx,cz-4,TD/2+3,TW/2-4+4,4,0,y-10,y+10,BLACK)
        stube(cx,cz,(-s,0))
    # post (black or Bone White) from the back box, elbow, then the flat beam + cradle
    yb,top,rc=243.5,298.5,40
    P=[[CX,yb,30],[CX,yb,top-rc]]+arc((yb-rc,top-rc),rc,0,90,10,lambda p:[CX,p[0],p[1]])
    secs=[(20.4,18-7*min(1,p[2]/top),8) for p in P]
    sweep(P,[1,0,0],secs,postcol)
    prism_y(CX,top,23,13,4,0,yb-rc-40,yb-rc+2,postcol)           # sleeve over the beam root
    B=[[CX,yb-rc,top],[CX,-22,top]]; sweep(B,[1,0,0],[(17,9,6)]*2,BONE)
    prism_z(CX,61,46,85,10,top-8,top+9,BONE)                     # cradle pad
    px0,px1,py0,py1=CX-36.5,CX+36.5,-15.8,137.5
    z0,z1=top+9,top+13
    A.box(px0-1.86,px0,py0-1.86,40,z0,z1,BONE); A.box(px0-1.86,px0,75,py1+1.86,z0,z1,BONE)   # left lip, thumb notch
    A.box(px0-1.86,px1+1.86,py1,py1+1.86,z0,z1,BONE)                                        # back lip
    A.box(px0-1.86,CX-8,py0-1.86,py0,z0,z1,BONE); A.box(CX+8,px1+1.86,py0-1.86,py0,z0,z1,BONE)  # front lip, USB notch
    A.box(px1,px1+1.86,py0-1.86,py0+35,z0,z1,BONE)                                          # short right stop
    A.box(px0+0.5,px1-0.5,py0+0.5,py1-0.5,z0,z0+8.6,PHONE)
    # arms: one piece, floor run from the base side, rounded elbows, into a clip behind each high tube
    for s in (-1,1):
        hx=CX+s*205; hz=204; back=np.array([s,1])/np.sqrt(2)
        clip=np.array([hx,hz])+back*(TD/2+5)
        xc=hx+s*30; zf=9; r1=20; r2=14
        Q=[[CX+s*187.5,CY,zf],[xc-s*r1,CY,zf]]
        Q+=arc((xc-s*r1,zf+r1),r1,-90,0,8,lambda p:[p[0],CY,p[1]]) if s>0 else arc((xc+r1,zf+r1),r1,270,180,8,lambda p:[p[0],CY,p[1]])
        Q+=[[xc,CY,clip[1]-r2]]
        Q+=arc((xc-s*r2,clip[1]-r2),r2,0,90,8,lambda p:[p[0],CY,p[1]]) if s>0 else arc((xc+r2,clip[1]-r2),r2,180,90,8,lambda p:[p[0],CY,p[1]])
        Q+=[[clip[0],CY,clip[1]]]
        sweep(Q,[0,1,0],[(13,9,6)]*len(Q),BONE)
        prism_y(clip[0]-back[0]*2,clip[1]-back[1]*2,TW/2+3,6,3,45*s,CY-15,CY+15,BONE)     # clip head
        stube(hx,hz,-back)
    R.FACES[:]=[(F,n,c,True) if c is LED else (F,n,c,k) for F,n,c,k in R.FACES]
def v(eye,light):
    pts=np.array([[x,y,z] for x in (-110,361) for y in (-45,280) for z in (0,315)])
    e=np.array(eye,float); e/=np.linalg.norm(e); r=np.cross(-e,[0,0,1.]); r/=np.linalg.norm(r); u=np.cross(r,-e)
    sx,sy=pts@r,pts@u
    return R.render(eye,2.2,light,(sx.min()-8,sx.max()+8,sy.min()-8,sy.max()+8))[0]
EYE=(-1.0,-1.5,0.9); LT=(0.3,-0.6,1.0)
model(BLACK); i1=v(EYE,LT); i3=v((1.2,1.4,0.5),(-0.3,0.6,1.0))
model(BONE); i2=v(EYE,LT)
fig=plt.figure(figsize=(21,8.4),dpi=110)
gs=fig.add_gridspec(1,3,left=0.01,right=0.99,top=0.86,bottom=0.11,wspace=0.02)
fig.suptitle("photoStand rev2 concept on the consumer model: agreed changes 1-13 applied (unsaved), both post colors for card 14",fontsize=16,fontweight="bold")
for k,(im,t) in enumerate(((i1,"Black post (recommended)"),(i2,"Bone White post"),(i1*0+i3 if False else i3,"Black post, from the back"))):
    ax=fig.add_subplot(gs[k]); ax.imshow(im); ax.axis("off"); ax.set_title(t,loc="left",fontsize=13)
fig.text(0.5,0.025,"Low tubes moved out of the photo and seated in black saddles; base fits the board (0.5 mm) with a 30 mm back box; arch split at the beam root with a sleeve; slim tubes on all four bars;\n"
 "high tubes clip onto the arms; phone pocket with thumb and USB notches and a short right stop; cord clamp at the back. Keys and labels not drawn. Sizes are placeholders.",ha="center",fontsize=10.5,color="#444")
fig.savefig("/mnt/project-files/images/photoStand_rev2_concept.png",facecolor="white"); print("ok")

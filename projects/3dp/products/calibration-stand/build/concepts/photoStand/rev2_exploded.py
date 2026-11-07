import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import renderlib as R
import rev1_concept as A
import rev1_consumer as C
from rev1_consumer import sweep, arc, prism_y, prism_z
BONE=np.array([0.86,0.84,0.78]); BLACK=np.array([0.17,0.17,0.18]); LED=np.array([1.0,0.85,0.25])
PHONE=np.array([0.55,0.62,0.72]); OR=np.array([0.95,0.45,0.10]); CX,CY=125.5,111.5
TW,TD=23.5,22.5
B=A.box
def tprof(rl=0.6,rb=6,k=6):
    w,h=TW,TD; P=[]
    for cx,cy,r,a0 in ((w/2-rl,rl,rl,270),(w/2-rb,h-rb,rb,0),(-w/2+rb,h-rb,rb,90),(-w/2+rl,rl,rl,180)):
        for t in np.radians(np.linspace(a0,a0+90,k)): P.append((cx+r*np.cos(t),cy+r*np.sin(t)))
    return np.array(P)
def stube(cx,cz,n,y0=-37,y1=265):
    n=np.array(n,float); n/=np.linalg.norm(n); t=np.array([-n[1],n[0]]); lc=np.array([cx,cz])+n*TD/2
    S=tprof(); Q=[]
    for y in (y0,y1): Q.append([[(lc+t*u-n*v)[0],y,(lc+t*u-n*v)[1]] for (u,v) in S])
    c=np.array([cx,(y0+y1)/2,cz]); M=len(S)
    for k in range(M): C.add([Q[0][k],Q[0][(k+1)%M],Q[1][(k+1)%M],Q[1][k]],c,BONE)
    C.add(Q[0],c,BONE); C.add(Q[1],c,BONE)
    fc=lc+n*0.15; L=[]
    for y in (y0,y1):
        for u in (-(TW/2-0.8),TW/2-0.8):
            for d in (0,0.3): L.append([(fc+t*u+n*d)[0],y,(fc+t*u+n*d)[1]])
    A.hexa(L,LED)
    # keyed bore: rail key at the open back end
    m=np.array([cx,cz])-n*(TD/2-2); B(m[0]-2,m[0]+2,y1-2,y1+0.5,m[1]-2,m[1]+2,OR)
PARTS=[]
def part(label,off,fn):
    i=len(R.FACES); fn(); j=len(R.FACES); off=np.array(off,float)
    for k in range(i,j):
        F,n,c,cut=R.FACES[k]; R.FACES[k]=(np.asarray(F)+off,n,c,cut)
    if label: PARTS.append((label,np.vstack([R.FACES[k][0] for k in range(i,j)]).mean(0)))
R.FACES.clear()
# ---- base: soft U, low sides blending into a 30 mm tall back box; split at the back straight
xl,xr,yb_,R0=-31.25,282.25,243.5,45
U=[[xl,-30,0],[xl,yb_-R0-30,0]]
for t in np.linspace(np.pi,np.pi/2,10): U.append([xl+R0+R0*np.cos(t),yb_-R0+R0*np.sin(t),0])
for x in np.linspace(xl+R0+10,xr-R0-10,6): U.append([x,yb_,0])
for t in np.linspace(np.pi/2,0,10): U.append([xr-R0+R0*np.cos(t),yb_-R0+R0*np.sin(t),0])
U+=[[xr,yb_-R0-30,0],[xr,-30,0]]
U=np.array(U,float); secs=[]
for p in U:
    f=np.clip((p[1]-(yb_-R0-30))/(R0+30),0,1)**1.5; hz=4.05+f*(15-4.05)
    p[2]=hz; secs.append((hz,31-f*11,3.5+f*4))
jl,jr=U[12][0],U[17][0]
def bside(a,b,s):
    sweep(U[a:b],[0,0,1],secs[a:b],BLACK)
    j=jl if s<0 else jr
    B(j-s*0.0-(14 if s<0 else -1)*1,j+(1 if s<0 else 14),yb_-8,yb_+4,10,20,OR)          # offset tongue into the back box (one-way)
    for y in (20,180):                                                                     # keyed saddle sockets
        x=CX+s*(159+TD/2); B(x-6,x+6,y-4,y+4,8.1,8.6,OR); B(x-2,x+2,y+4,y+7,8.1,8.6,OR)
    B(CX+s*187.5-6,CX+s*187.5+6,CY-8,CY+8,8.1,8.6,OR)                                    # arm foot socket
def bback():
    sweep(U[12:18],[0,0,1],secs[12:18],BLACK)
    for j in (jl,jr): B(j-1,j+1,yb_-8,yb_+4,10,20,OR)                                   # tongue slots
    B(CX-12,CX+12,yb_-10,yb_+10,29.4,30,OR); B(CX+10,CX+14,yb_-3,yb_+3,29.4,30,OR)     # 30 mm post socket + key
    B(CX-4,CX+4,yb_,yb_+14,0,1.5,OR)                                                     # cord groove underneath
part("1 base, left",(-120,-40,-150),lambda: bside(0,13,-1))
part("2 base, back box",(0,110,-150),bback)
part("3 base, right",(120,-40,-150),lambda: bside(17,30,1))
part("13 cord clamp",(0,200,-150),lambda: B(CX-12,CX+12,263.5,272,10,22,BLACK))
# ---- saddles (4, glued) and low tubes
for s,nm in ((-1,"left"),(1,"right")):
    cx=CX+s*(159+TD/2); cz=8.1+2+TW/2
    for y in (20,180):
        def sad(y=y,cx=cx,cz=cz):
            prism_y(cx,cz-4,TD/2+3,TW/2,4,0,y-10,y+10,BLACK)
            B(cx-6,cx+6,y-4,y+4,-6+cz-4-TW/2,cz-4-TW/2,OR); B(cx-2,cx+2,y+4,y+7,-6+cz-4-TW/2,cz-4-TW/2,OR)
        part("4 saddle (4 total)" if (s>0 and y==180) else "",(s*55,-20,-75),sad)
    part(f"{5 if s<0 else 6} low tube, {nm}",(s*40,-270,0),lambda cx=cx,cz=cz,s=s: stube(cx,cz,(-s,0)))
# ---- post + elbow, beam + cradle
yb,top,rc=243.5,298.5,40
P=[[CX,yb,30],[CX,yb,top-rc]]+arc((yb-rc,top-rc),rc,0,90,10,lambda p:[CX,p[0],p[1]])
ps=[(20.4,18-7*min(1,p[2]/top),8) for p in P]
def post():
    sweep(P,[1,0,0],ps,BLACK); prism_y(CX,top,23,13,4,0,yb-rc-40,yb-rc+2,BLACK)
    B(CX-11.5,CX+11.5,yb-9.5,yb+9.5,0,30,OR); B(CX+11.5,CX+13.5,yb-2.5,yb+2.5,0,30,OR)      # 30 mm foot tenon + key
    B(CX-17,CX+17,yb-rc-40,yb-rc-39.4,top-9,top+9,OR)                                     # sleeve mouth
part("7 post + elbow (black, card 14)",(0,110,-40),post)
def beam():
    sweep([[CX,yb-rc-40,top],[CX,-22,top]],[1,0,0],[(17,9,6)]*2,BONE)
    B(CX-14,CX+14,yb-rc-40,yb-rc-2,top-7,top+7,OR); B(CX-4,CX+4,yb-rc-40,yb-rc-2,top+7,top+9,OR)  # 30+ mm keyed tenon
    prism_z(CX,61,46,85,10,top-8,top+9,BONE)
    px0,px1,py0,py1=CX-36.5,CX+36.5,-15.8,137.5; z0,z1=top+9,top+13
    B(px0-1.86,px0,py0-1.86,40,z0,z1,OR); B(px0-1.86,px0,75,py1+1.86,z0,z1,OR)
    B(px0-1.86,px1+1.86,py1,py1+1.86,z0,z1,OR)
    B(px0-1.86,CX-8,py0-1.86,py0,z0,z1,OR); B(CX+8,px1+1.86,py0-1.86,py0,z0,z1,OR)
    B(px1,px1+1.86,py0-1.86,py0+35,z0,z1,OR)
part("8 beam + phone pocket",(0,-90,70),beam)
part("",(0,-90,110),lambda: B(CX-36,CX+36,-15.3,137,top+9.5,top+18,PHONE))
# ---- arms with clip heads, high tubes
for s,nm in ((-1,"left"),(1,"right")):
    hx=CX+s*205; hz=204; back=np.array([s,1])/np.sqrt(2); clip=np.array([hx,hz])+back*(TD/2+5)
    xc=hx+s*30; zf=9; r1=20; r2=14
    Q=[[CX+s*187.5,CY,zf],[xc-s*r1,CY,zf]]
    Q+=arc((xc-s*r1,zf+r1),r1,-90,0,8,lambda p:[p[0],CY,p[1]]) if s>0 else arc((xc+r1,zf+r1),r1,270,180,8,lambda p:[p[0],CY,p[1]])
    Q+=[[xc,CY,clip[1]-r2]]
    Q+=arc((xc-s*r2,clip[1]-r2),r2,0,90,8,lambda p:[p[0],CY,p[1]]) if s>0 else arc((xc+r2,clip[1]-r2),r2,180,90,8,lambda p:[p[0],CY,p[1]])
    Q+=[[clip[0],CY,clip[1]]]
    Q=[q for i,q in enumerate(Q) if i==0 or np.linalg.norm(np.subtract(q,Q[i-1]))>1e-6]
    def arm(Q=Q,s=s,clip=clip,back=back):
        sweep(Q,[0,1,0],[(13,9,6)]*len(Q),BONE)
        prism_y(clip[0]-back[0]*2,clip[1]-back[1]*2,TW/2+3,6,3,45*s,CY-15,CY+15,BONE)
        B(CX+s*187.5-6,CX+s*187.5+6,CY-8,CY+8,zf-9-6,zf-9,OR)                              # foot peg
        m=clip-back*7; B(m[0]-2,m[0]+2,CY-15,CY+15,m[1]-2,m[1]+2,OR)                       # clip key rib
    part(f"{9 if s<0 else 10} arm + clip, {nm}",(s*230,0,0),arm)
    part(f"{11 if s<0 else 12} high tube, {nm}",(s*290,0,90),lambda hx=hx,hz=hz,back=back: stube(hx,hz,-back))
R.FACES[:]=[(F,n,c,True) if c is LED else (F,n,c,k) for F,n,c,k in R.FACES]
eye=(-1.0,-1.5,0.9); e=np.array(eye); e=e/np.linalg.norm(e); rt=np.cross(-e,[0,0,1.]); rt/=np.linalg.norm(rt); up=np.cross(rt,-e)
allv=np.vstack([F for F,_,_,_ in R.FACES]); sx,sy=allv@rt,allv@up
img,cam=R.render(eye,2.0,(0.3,-0.6,1.0),(sx.min()-70,sx.max()+70,sy.min()-10,sy.max()+10))
fig=plt.figure(figsize=(16,13),dpi=120); ax=fig.add_axes([0.01,0.08,0.98,0.86]); ax.imshow(img); ax.axis("off")
fig.suptitle("photoStand rev2 concept (consumer model), exploded: 13 part types with guide features (orange)",fontsize=16,fontweight="bold")
BX=dict(boxstyle="round,pad=0.3",fc="white",ec="#888",lw=0.8); AR=dict(arrowstyle="-|>",color="#222",lw=1.0)
H,W=img.shape[:2]
for lb,p in PARTS:
    x,y=R.proj(cam,p); d=np.array([x-W/2,y-H/2]); d=d/(np.linalg.norm(d)+1e-9)
    ax.annotate(lb,xy=(x,y),xytext=(x+d[0]*110,y+d[1]*80),fontsize=11,arrowprops=AR,bbox=BX,ha="center",va="center")
fig.text(0.5,0.012,"Guides (orange): offset tongues key the base sides into the back box; the post sits in a 30 mm keyed socket and the beam's keyed tenon goes 30+ mm into the post's sleeve.\n"
 "Saddles have keyed pegs into the base; each arm has a foot peg and a keyed rib in its clip; each tube has a rail key at its open end so the bar only goes in LEDs toward the lit face.\n"
 "Phone pocket lips with thumb and USB notches and a short right stop. Glued joints: saddles, post socket, beam sleeve. Labels and L/R/FRONT debossing not drawn. Sizes are placeholders.",ha="center",fontsize=10.5,color="#444")
fig.savefig("/mnt/project-files/images/photoStand_rev2_exploded.png",facecolor="white"); print("ok",[l for l,_ in PARTS])

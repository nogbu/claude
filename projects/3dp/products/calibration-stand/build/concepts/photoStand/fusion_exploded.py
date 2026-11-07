import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import renderlib as R
import rev1_concept as A
from rev1_consumer import prism_y
B=A.box
BLK=np.array([0.17,0.17,0.18]); BAR=np.array([0.30,0.30,0.32]); LED=np.array([1.0,0.85,0.25]); OR=np.array([0.95,0.45,0.10])
PHONE=np.array([0.55,0.62,0.72]); CX,CY=125.5,111.5
PARTS=[]
def part(label,off,fn):
    i=len(R.FACES); fn(); j=len(R.FACES); off=np.array(off,float)
    for k in range(i,j):
        F,n,c,cut=R.FACES[k]; R.FACES[k]=(np.asarray(F)+off,n,c,cut)
    if label: PARTS.append((label,np.vstack([R.FACES[k][0] for k in range(i,j)]).mean(0)))
R.FACES.clear()
w=10.4; x0,x1,y0,y1=-0.5,251.5,-0.5,223.5
def side(s):
    xa,xb=(x0-w,x0) if s<0 else (x1,x1+w)
    B(xa,xb,y0-w,y1,0,11.2,BLK)
    B(*sorted([CX+s*126.25,CX+s*245]),CY-40,CY+40,0,11.2,BLK)          # outrigger to the post
    px=CX+s*225; B(px-9.5,px+9.5,CY-9.5,CY+9.5,10.6,11.2,OR)              # post socket
    bx=CX+s*169
    for y in (0,223): B(bx-6,bx+6,y-4,y+4,10.6,11.2,OR)                  # bar-holder sockets
    B(*sorted([xa,xb]),y1-6,y1,11.2,17,OR)                               # tongue into the back rail (offset)
def back():
    B(x0-w,x1+w,y1,y1+w,0,11.2,BLK)
    for x in (x0-w/2,x1+w/2): B(x-2,x+2,y1-0.6,y1,11.2,17,OR)            # tongue slots
part("1 base, left side + foot",(-90,-40,-120),lambda: side(-1))
part("2 base, right side + foot",(90,-40,-120),lambda: side(1))
part("3 base, back rail",(0,120,-120),back)
for s,nm in ((-1,"L"),(1,"R")):
    px=CX+s*225
    def lower(px=px): B(px-9,px+9,CY-9,CY+9,11.2,160,BLK); B(px-15.5,px+15.5,CY-40,CY+40,11.2,30,BLK); B(px-9,px+9,CY-9,CY+9,-30,11.2,OR); B(px-5,px+5,CY-5,CY+5,160,190,OR)
    def upper(px=px,s=s): B(px-9,px+9,CY-9,CY+9,160,312,BLK); B(*sorted([CX+s*213,px]),CY-8,CY+8,212,224,BLK); B(px-5,px+5,CY-5,CY+5,312,340,OR); B(CX+s*213-3,CX+s*213+3,CY-8,CY+8,224,226,OR)
    part(f"{4 if s<0 else 5} post, lower {nm}",(s*170,0,-40),lower)
    part(f"{6 if s<0 else 7} post, upper + light arm {nm}",(s*175,60,60),upper)
    bx=CX+s*169
    def holders(bx=bx):
        for y in (0,223): B(bx-13,bx+13,y-6,y+6,11.2,26,BLK); B(bx-6,bx+6,y-4,y+4,5.2,11.2,OR)
    part("8 low bar holders (4)" if s>0 else "",(s*120,0,-60),holders)
    hx=CX+s*205
    def clip(hx=hx,s=s):
        prism_y(hx,204,12,12,2,45*s,CY-15,CY+15,BLK)
        m=np.array([hx,204])+np.array([s,1])/np.sqrt(2)*14; B(m[0]-3,m[0]+3,CY-8,CY+8,m[1]-3,m[1]+3,OR)
    part("9 high bar clips (2)" if s>0 else "",(s*215,-60,120),clip)
def bar(s):
    xa,xb=(CX-234,CX) if s<0 else (CX,CX+234)
    B(xa,xb,CY-9,CY+9,312,330,BLK)
    px=CX+s*225; B(px-5.5,px+5.5,CY-5.5,CY+5.5,311.4,312,OR)              # post-top socket
    if s<0: B(CX,CX+30,CY-5,CY+5,316,326,OR)                               # center splice tenon
part("10 crossbar, left half",(-40,0,90),lambda: bar(-1))
part("11 crossbar, right half",(40,0,90),lambda: bar(1))
def carriage():
    B(CX-40,CX+40,CY-17.7,CY+17.7,330,342,BLK); B(CX-40,CX+40,CY-17.7,CY-14,300,330,BLK); B(CX-40,CX+40,CY+14,CY+17.7,300,330,BLK)
    B(CX-3,CX+3,CY+17.7,CY+21,322,340,OR)
part("12 carriage + center pin",(0,0,150),carriage)
def cradle():
    B(CX-42,CX+42,CY-58,CY+102,300.4,303.4,BLK)
    B(CX-42,CX-38,CY-58,CY+102,303.4,313,BLK); B(CX-42,CX+42,CY+98,CY+102,303.4,313,BLK); B(CX-42,CX+42,CY-58,CY-54,303.4,313,BLK)
    B(CX-12,CX+12,CY-14,CY+14,313,316,OR)
part("13 Pixel 10 Pro cradle",(0,-200,40),cradle)
part("",(0,-200,70),lambda: B(CX-36,CX+36,CY-48,CY+96,304.2,312.8,PHONE))
part("photo board (existing)",(0,0,-60),lambda: B(0,251,0,223,0,4.2,A.BOARD))
R.FACES[:]=[(F,n,c,True) if c is LED else (F,n,c,k) for F,n,c,k in R.FACES]
eye=(-1.0,-1.5,0.9); e=np.array(eye); e=e/np.linalg.norm(e); rt=np.cross(-e,[0,0,1.]); rt/=np.linalg.norm(rt); up=np.cross(rt,-e)
allv=np.vstack([F for F,_,_,_ in R.FACES]); sx,sy=allv@rt,allv@up
img,cam=R.render(eye,1.8,(0.3,-0.6,1.0),(sx.min()-160,sx.max()+160,sy.min()-10,sy.max()+10))
fig=plt.figure(figsize=(16,13),dpi=120); ax=fig.add_axes([0.01,0.08,0.98,0.86]); ax.imshow(img); ax.axis("off")
fig.suptitle("Fusion Buddy optimized for calibration photos, exploded: 13 part types (17 pieces) with guide features (orange)",fontsize=16,fontweight="bold")
BX=dict(boxstyle="round,pad=0.3",fc="white",ec="#888",lw=0.8); AR=dict(arrowstyle="-|>",color="#222",lw=1.0)
H,W=img.shape[:2]
for lb,p in PARTS:
    x,y=R.proj(cam,p); d=np.array([x-W/2,y-H/2]); d=d/(np.linalg.norm(d)+1e-9)
    ax.annotate(lb,xy=(x,y),xytext=(min(max(x+d[0]*120,150),W-150),y+d[1]*70),fontsize=11,arrowprops=AR,bbox=BX,ha="center",va="center")
fig.text(0.5,0.012,"Guides (orange): offset tongues key the base sides into the back rail; each lower post has a square tenon into its base socket and up into the upper post; the upper posts' tenons\n"
 "go into sockets under the crossbar halves, which splice at the center; the carriage's pin locks it at center; the cradle has a keyed boss into the carriage; holders and clips peg in one way.\n"
 "Split so every part fits the 256 mm plate (posts and crossbar are in two pieces). Barrina bars not shown. Sizes are placeholders.",ha="center",fontsize=10.5,color="#444")
fig.savefig("/mnt/project-files/images/fusionBuddy_calibration_exploded.png",facecolor="white"); print("ok",len(PARTS))

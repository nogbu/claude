import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import renderlib as R
import rev1_concept as A
from rev1_consumer import prism_y
B=A.box
BLK=np.array([0.17,0.17,0.18]); BAR=np.array([0.30,0.30,0.32]); LED=np.array([1.0,0.85,0.25]); OR=np.array([0.95,0.45,0.10])
PHONE=np.array([0.55,0.62,0.72]); CX,CY=125.5,111.5; MK=np.array([0.1,0.1,0.1])
def model():
    R.FACES.clear()
    B(0,251,0,223,0,4.2,A.BOARD)
    for x in (10.8,245.2):                       # board posts
        B(x-7.45,x+7.45,240.5-7.45-17,240.5+7.45-17,0,30,A.BOARD)
    for i in range(8): B(4,15,40-17+25*i-5.5,40-17+25*i+5.5,4.2,4.4,MK)     # marker hints
    # widened base frame (0.5 mm around the board), black
    w=10.4; x0,x1,y0,y1=-0.5,251.5,-0.5,223.5
    B(x0-w,x0,y0-w,y1+w,0,11.2,BLK); B(x1,x1+w,y0-w,y1+w,0,11.2,BLK)
    B(x0,x1,y1,y1+w,0,11.2,BLK)                 # back rail; front left open for sliding pieces in
    for s in (-1,1):
        px=CX+s*225
        B(*sorted([CX+s*(126.25),px+s*20]),CY-40,CY+40,0,11.2,BLK)            # outrigger foot
        B(px-9,px+9,CY-9,CY+9,11.2,312,BLK)                                    # taller post (+100 mm)
        B(px-15.5,px+15.5,CY-40,CY+40,11.2,30,BLK)                            # post foot
        # low bar holder + bar: lit face 159 mm from center, facing in
        bx=CX+s*(159+10)
        for y in (0,223): B(bx-13,bx+13,y-6,y+6,11.2,26,BLK)
        B(bx-10,bx+10,-37,261,14,34,BAR); B(*sorted([bx-s*10,bx-s*10.4]),-37,261,15,33,LED)
        # high bar on an arm from the post, 45 deg down, r 205, z 204
        hx=CX+s*205
        B(*sorted([hx+s*8,px]),CY-8,CY+8,212,224,BLK)
        prism_y(hx,204,10,10,1,45*s,-37,261,BAR)
        n=np.array([-s,-1])/np.sqrt(2); c=np.array([hx,204])+n*10.2
        A.rbox(c[0],c[1],16,0.4,45*s,-37,261,LED)
    # top crossbar with sliding carriage locked at center
    B(CX-225-9,CX+225+9,CY-9,CY+9,312,330,BLK)
    B(CX-40,CX+40,CY-17.7,CY+17.7,330,342,BLK)                                 # carriage
    B(CX-3,CX+3,CY+17.7,CY+21,322,340,OR)                                       # center detent pin
    # Pixel 10 Pro cradle hanging below the bar, lens over board center, lens face at 304.2
    B(CX-42,CX+42,CY-58,CY+102,300.4,303.4,BLK)                                 # cradle floor (lens window)
    B(CX-42,CX-38,CY-58,CY+102,303.4,313,BLK); B(CX-42,CX+42,CY+98,CY+102,303.4,313,BLK)
    B(CX-42,CX+42,CY-58,CY-54,303.4,313,BLK)
    B(CX-36,CX+36,CY-48,CY+96,304.2,312.8,PHONE)
    R.FACES[:]=[(F,n,c,True) if c is LED else (F,n,c,k) for F,n,c,k in R.FACES]
def view(eye,light):
    pts=np.array([[x,y,z] for x in (-120,371) for y in (-45,280) for z in (0,345)])
    e=np.array(eye,float); e/=np.linalg.norm(e); r=np.cross(-e,[0,0,1.]); r/=np.linalg.norm(r); u=np.cross(r,-e)
    sx,sy=pts@r,pts@u
    return R.render(eye,2.2,light,(sx.min()-8,sx.max()+8,sy.min()-8,sy.max()+8))[0]
model()
i1=view((-1.0,-1.5,0.9),(0.3,-0.6,1.0)); i2=view((0,-1,0.12),(0.3,-0.6,1.0))
fig=plt.figure(figsize=(20,9),dpi=110)
gs=fig.add_gridspec(1,2,left=0.01,right=0.99,top=0.86,bottom=0.13,wspace=0.03)
fig.suptitle("Fusion Buddy, optimized for reading the calibration tests (concept, sizes are placeholders)",fontsize=16,fontweight="bold")
for k,(im,t) in enumerate(((i1,"From the front left"),(i2,"From the front"))):
    ax=fig.add_subplot(gs[k]); ax.imshow(im); ax.axis("off"); ax.set_title(t,loc="left",fontsize=13)
fig.text(0.5,0.02,"Base frame widened to hold the 251 x 223 mm photo board (0.5 mm clearance, open front). Posts moved outside the lights and 100 mm taller: lens about 300 mm above the board.\n"
 "Pixel 10 Pro cradle under a top crossbar, carriage locked at center by a pin (orange). Low bars beside the board for raking light (lit face 159 mm out);\n"
 "high bars on post arms at 45 deg, 205 mm out and 204 mm up. All frame parts matte black. Green tray dropped. Barrina bars shown dark gray with their lit faces yellow.",ha="center",fontsize=10.5,color="#444")
fig.savefig("/mnt/project-files/images/fusionBuddy_calibration_concept.png",facecolor="white"); print("ok")

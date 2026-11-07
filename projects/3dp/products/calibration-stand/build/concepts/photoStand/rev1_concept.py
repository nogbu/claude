import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import renderlib as R
BONE=np.array([0.80,0.78,0.72]); BLACK=np.array([0.16,0.16,0.17]); BOARD=np.array([0.88,0.87,0.83])
PHONE=np.array([0.55,0.62,0.72]); LENS=np.array([0.03,0.03,0.03]); BAR=np.array([0.92,0.92,0.92])
LED=np.array([1.0,0.85,0.25]); CORD=np.array([0.25,0.25,0.25])
def hexa(V,col):
    V=np.asarray(V,float); c=V.mean(0)
    for q in [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]:
        F=V[q]; n=R.newell(F); ln=np.linalg.norm(n)
        if ln<1e-9: continue
        n/=ln
        if np.dot(n,F.mean(0)-c)<0: n=-n
        R.FACES.append((F,n,col,False))
def box(x0,x1,y0,y1,z0,z1,col): hexa([[x,y,z] for x in (x0,x1) for y in (y0,y1) for z in (z0,z1)],col)
def rbox(cx,cz,w,h,ang,y0,y1,col):   # box along y, rotated in the xz plane
    a=np.radians(ang); u=np.array([np.cos(a),np.sin(a)]); v=np.array([-np.sin(a),np.cos(a)])
    P=[]
    for s in (-1,1):
        for y in (y0,y1):
            for t in (-1,1):
                p=np.array([cx,cz])+s*w/2*u+t*h/2*v; P.append([p[0],y,p[1]])
    hexa(P,col)
CX,CY,LZ=125.5,111.5,304.2
def model():
    box(0,251,0,223,0,4.2,BOARD)                                   # board rev2
    for s,(x0,x1) in ((-1,(-40.5,-0.5)),(1,(251.5,291.5))):
        box(x0,x1,-40,263,0,6,BLACK)                               # side strip
        bc=-14.5 if s<0 else 265.5
        box(bc-10,bc+10,-37,261,14.2,34.2,BAR)                     # low bar
        lf=bc+10 if s<0 else bc-10
        box(min(lf,lf-s*0.6),max(lf,lf-s*0.6),-30,254,16,32.4,LED)  # lit face toward board
        for y in (-10,111.5,233):                                  # 3 clips
            box(bc-12.4,bc+12.4,y-10,y+10,6,37,BLACK)
        # tower
        hx=CX+s*205; hz=204
        fx0,fx1=(hx-14,x0) if s<0 else (x1,hx+14)
        box(fx0,fx1,CY-12,CY+12,0,10,BONE)                         # foot keyed into strip
        tx=hx+s*(-6)-s*0
        box(min(hx+s*4,hx+s*20),max(hx+s*4,hx+s*20),CY-10,CY+10,10,200,BONE)  # column
        rbox(hx+s*12,hz-2,28,28,-s*45+0,CY-12,CY+12,BONE)          # 45° clip head
        rbox(hx,hz,20,20,45*s,-37,261,BAR)                          # high bar
        # lit face: normal points down and toward the board
        n=np.array([-s,-1])/np.sqrt(2); c=np.array([hx,hz])+n*10.2
        rbox(c[0],c[1],16,0.6,45*s,-30,254,LED)
        # cords out the back
        box(bc-3,bc+3,261,294,21,27,CORD); 
        rbox(hx,hz,6,6,0,261,294,CORD)
    box(-20,271,-25.5,-0.5,0,6,BLACK); box(-20,271,223.5,248.5,0,6,BLACK)   # rails
    for y0,y1 in ((-21.3,-1.5),(224.5,244.3)): box(95.5,139.5,y0,y1,6,292.5,BONE)  # legs
    box(79.3,155.7,-21.3,244.3,292.5,307.5,BONE)                   # crossbar
    box(81.5,153.5,-15.3,137.5,300,308.5,PHONE)                    # phone in pocket
    box(79.3,81.5,-21.3,141.5,307.5,312,BONE); box(153.5,155.7,-21.3,141.5,307.5,312,BONE) # lips
    box(79.3,155.7,137.5,141.5,307.5,312,BONE)
    box(CX-6,CX+6,CY-6,CY+6,292.4,292.5,LENS)                      # lens hole
if __name__ == "__main__":
    R.FACES.clear(); model()
    def view(eye,ppm,light,pts):
        e=np.array(eye,float); e/=np.linalg.norm(e); r=np.cross(-e,[0,0,1.]); r/=np.linalg.norm(r); u=np.cross(r,-e)
        sx,sy=pts@r,pts@u
        return R.render(eye,ppm,light,(sx.min()-8,sx.max()+8,sy.min()-8,sy.max()+8))
    pts=np.array([[x,y,z] for x in (-110,361) for y in (-45,300) for z in (0,315)])
    img1,c1=view((-1.0,-1.5,0.9),2.2,(0.3,-0.6,1.0),pts)
    img2,c2=view((0,-1,0.0001),1.9,(0.2,-1,0.6),pts)
    fig=plt.figure(figsize=(18,9.5),dpi=120)
    gs=fig.add_gridspec(1,2,width_ratios=[1.15,1],left=0.01,right=0.99,top=0.9,bottom=0.1,wspace=0.03)
    fig.suptitle("photoStand_rev1 concept: 9 parts (sizes are placeholders until the build script)",fontsize=16,fontweight="bold")
    BX=dict(boxstyle="round,pad=0.3",fc="white",ec="#888",lw=0.8); AR=dict(arrowstyle="-|>",color="#222",lw=1.1)
    def lab(ax,cam,p,t,d):
        x,y=R.proj(cam,np.array(p,float)); ax.annotate(t,xy=(x,y),xytext=(x+d[0],y+d[1]),fontsize=10,arrowprops=AR,bbox=BX,ha="center",va="center")
    a1=fig.add_subplot(gs[0]); a1.imshow(img1); a1.axis("off"); a1.set_title("3/4 view from the front",loc="left",fontsize=13)
    lab(a1,c1,(117,60,309),"1 crossbar + pocket (phone top to back,\nbuttons right, open right side)",(-60,-70))
    lab(a1,c1,(117,-11,150),"2 front leg (3 back leg)",(-170,0))
    lab(a1,c1,(-20,100,3),"4 side strip, black, 3 clips + low bar",(-120,90))
    lab(a1,c1,(130,-13,3),"6 front rail (7 back), black",(120,90))
    lab(a1,c1,(-88,CY,120),"8 tower (9 opposite),\n45° high bar at r 205, z 204",(-90,-120))
    lab(a1,c1,(265,280,24),"cords out the back",(110,-40))
    a2=fig.add_subplot(gs[1]); a2.imshow(img2); a2.axis("off"); a2.set_title("Front view",loc="left",fontsize=13)
    pa,pb=R.proj(c2,np.array([CX,-60,4.2])),R.proj(c2,np.array([CX,-60,LZ]))
    a2.annotate("",xy=pa,xytext=pb,arrowprops=dict(arrowstyle="<->",color="#c0392b",lw=1.5))
    a2.text(pa[0]+10,(pa[1]+pb[1])/2-40,"300 mm\nlens to board",color="#c0392b",fontsize=11,fontweight="bold")
    fig.text(0.5,0.03,"Black: side strips, clips, rails. Bone White: legs, crossbar, towers. Gold: lit faces. Low bars glare-free to ~87 mm; high bars outside the glare cone (inference).",ha="center",fontsize=10.5,color="#444")
    fig.savefig("/mnt/project-files/images/photoStand_rev1_concept.png",facecolor="white"); print("ok")

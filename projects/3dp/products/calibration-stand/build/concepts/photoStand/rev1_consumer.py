import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import renderlib as R
import rev1_concept as A
BONE=np.array([0.86,0.84,0.78]); BLACK=np.array([0.17,0.17,0.18]); BOARD=np.array([0.88,0.87,0.83])
PHONE=np.array([0.55,0.62,0.72]); LED=np.array([1.0,0.85,0.25]); DARK=np.array([0.3,0.3,0.32])
CX,CY=125.5,111.5
def add(F,ctr,col):
    F=np.asarray(F,float); n=R.newell(F); ln=np.linalg.norm(n)
    if ln<1e-9: return
    n/=ln
    if np.dot(n,F.mean(0)-ctr)<0: n=-n
    R.FACES.append((F,n,col,False))
def rr(a,b,r,k=5):   # rounded-rect outline, half sizes a,b
    r=min(r,a-1e-3,b-1e-3); P=[]
    for cx,cy,a0 in ((a-r,b-r,0),(-a+r,b-r,90),(-a+r,-b+r,180),(a-r,-b+r,270)):
        for t in np.linspace(a0,a0+90,k): P.append((cx+r*np.cos(np.radians(t)),cy+r*np.sin(np.radians(t))))
    return np.array(P)
def sweep(path,U,secs,col,closed=False,caps=True):
    """path: Nx3 points; U: fixed unit axis normal to the path plane; secs: list of (a,b,r)."""
    path=np.asarray(path,float); N=len(path); U=np.asarray(U,float); rings=[]
    for i in range(N):
        if closed: t=path[(i+1)%N]-path[i-1]
        else: t=path[min(i+1,N-1)]-path[max(i-1,0)]
        t/=np.linalg.norm(t); V=np.cross(t,U); V/=np.linalg.norm(V)
        a,b,r=secs[i]; S=rr(a,b,r); rings.append(path[i]+S[:,:1]*U+S[:,1:]*V)
    M=len(rings[0]); last=N if closed else N-1
    for i in range(last):
        j=(i+1)%N; c=(path[i]+path[j])/2
        for k in range(M):
            add([rings[i][k],rings[i][(k+1)%M],rings[j][(k+1)%M],rings[j][k]],c,col)
    if caps and not closed:
        add(rings[0],path[0]-(path[1]-path[0]),col); add(rings[-1],path[-1]+(path[-1]-path[-2]),col)
def arc(c,r,a0,a1,n,plane):
    out=[]
    for t in np.linspace(np.radians(a0),np.radians(a1),n):
        p=[c[0]+r*np.cos(t),c[1]+r*np.sin(t)]
        out.append(plane(p))
    return out
def prism_y(cx,cz,a,b,r,ang,y0,y1,col):  # rounded prism along y, rotated in xz
    th=np.radians(ang); S=rr(a,b,r); P=[]
    for y in (y0,y1):
        P.append([[cx+s[0]*np.cos(th)-s[1]*np.sin(th),y,cz+s[0]*np.sin(th)+s[1]*np.cos(th)] for s in S])
    c=np.array([cx,(y0+y1)/2,cz]); M=len(S)
    for k in range(M): add([P[0][k],P[0][(k+1)%M],P[1][(k+1)%M],P[1][k]],c,col)
    add(P[0],c,col); add(P[1],c,col)
def prism_z(cx,cy,a,b,r,z0,z1,col):
    S=rr(a,b,r); P=[[[cx+p[0],cy+p[1],z] for p in S] for z in (z0,z1)]; c=np.array([cx,cy,(z0+z1)/2]); M=len(S)
    for k in range(M): add([P[0][k],P[0][(k+1)%M],P[1][(k+1)%M],P[1][k]],c,col)
    add(P[0],c,col); add(P[1],c,col)
def consumer():
    R.FACES.clear()
    A.box(0,251,0,223,0,4.2,BOARD)
    # base ring: soft-section loop around the board, cords hidden inside
    a,b,r=150.5,136.5,26; cx,cy=CX,CY
    ring=[[cx+a,-30,4]]+[[cx+a-r+r*np.cos(t),cy+b-r+r*np.sin(t),4] for t in np.radians(np.linspace(0,90,8))]
    ring+=[[cx-a+r+r*np.cos(t),cy+b-r+r*np.sin(t),4] for t in np.radians(np.linspace(90,180,8))]+[[cx-a,-30,4]]
    sweep(ring,[0,0,1],[(4,16,3.5)]*len(ring),BLACK)
    # low-light housings: the bars hide in soft pods, a diffuser slot faces the board
    for s in (-1,1):
        bx=CX+s*140
        prism_y(bx,22,15,15,7,0,-38,262,BONE)
        A.box(*sorted([bx-s*15.05,bx-s*14.4]),-30,254,15,29,LED)
    # arch: one sweep front to back, legs taper and flare into a cradle on top
    yf,yb,top=-22,236,292; rc=40
    P=[[CX,yf,top]]
    for y in np.linspace(yf+15,yb-rc-5,10): P.append([CX,y,top])
    P+=arc((yb-rc,top-rc),rc,90,0,10,lambda p:[CX,p[0],p[1]])
    P+=[[CX,yb,top-rc-30],[CX,yb,0]]
    P=np.array(P); secs=[]
    for p in P:
        h=p[2]/top; secs.append((17+11*(1-h), 9+6*(1-h)+5*(p[1]>yb-rc-1), 8))
    sweep(P,[1,0,0],secs,BONE)
    # phone sits flush in the cradle
    prism_z(CX,61,46,85,16,top-8,top+9,BONE)              # cradle pad
    A.box(81.5,153.5,-15.3,137.5,top+4,top+11.6,PHONE)
    # towers: curved arms rising from the ring, lamp heads at r 205, z 204, 45 deg
    for s in (-1,1):
        hx=CX+s*205; xc=hx+s*24; zf=9; r1=22; r2=26; ztop=204
        Q=[[CX+s*150,CY,zf],[xc-s*r1,CY,zf]]
        Q+=arc((xc-s*r1,zf+r1),r1,-90,0,9,lambda p:[p[0],CY,p[1]]) if s>0 else arc((xc+r1,zf+r1),r1,270,180,9,lambda p:[p[0],CY,p[1]])
        Q+=[[xc,CY,ztop-r2+5]]
        Q+=arc((xc-s*r2,ztop-r2+5),r2,0,90,9,lambda p:[p[0],CY,p[1]]) if s>0 else arc((xc+r2,ztop-r2+5),r2,180,90,9,lambda p:[p[0],CY,p[1]])
        Q+=[[hx,CY,ztop+5]]
        Q=[q for i,q in enumerate(Q) if i==0 or np.linalg.norm(np.subtract(q,Q[i-1]))>1e-6]
        sweep(Q,[0,1,0],[(13,9,6)]*len(Q),BONE)
        prism_y(CX+s*205,204,17,15,7,45*s,-40,264,BONE)
        n=np.array([-s,-1])/np.sqrt(2); c=np.array([CX+s*205,204])+n*15.1
        A.rbox(c[0],c[1],0.6,22,45*s,-32,256,LED)
    A.box(CX-4,CX+4,248,300,1,9,DARK)   # one cord out the back
def view(eye,ppm,light):
    pts=np.array([[x,y,z] for x in (-110,361) for y in (-45,300) for z in (0,315)])
    e=np.array(eye,float); e/=np.linalg.norm(e); r=np.cross(-e,[0,0,1.]); r/=np.linalg.norm(r); u=np.cross(r,-e)
    sx,sy=pts@r,pts@u
    return R.render(eye,ppm,light,(sx.min()-8,sx.max()+8,sy.min()-8,sy.max()+8))
if __name__=="__main__":
    consumer()
    i1,_=view((-1.0,-1.5,0.9),2.2,(0.3,-0.6,1.0)); i2,_=view((1.2,1.4,0.5),2.2,(-0.3,0.6,1.0)); i3,_=view((0,-1,0.0001),1.9,(0.2,-1,0.6))
    fig=plt.figure(figsize=(21,8.6),dpi=110)
    gs=fig.add_gridspec(1,3,width_ratios=[1,1,0.9],left=0.01,right=0.99,top=0.86,bottom=0.1,wspace=0.02)
    fig.suptitle("photoStand_rev1 base design (consumer-styled): proposed open front (cantilever from one back post)",fontsize=16,fontweight="bold")
    for k,(im,t) in enumerate(((i1,"3/4 view from the front"),(i2,"From the back"),(i3,"Front view"))):
        ax=fig.add_subplot(gs[k]); ax.imshow(im); ax.axis("off"); ax.set_title(t,loc="left",fontsize=13)
    fig.text(0.5,0.03,"Proposed, not agreed yet: front leg dropped, the arch cantilevers forward from one tapered back post; base ring is a U open at the front. Post size comes from the load check in the build script. Sizes are placeholders.",ha="center",fontsize=10.5,color="#444")
    fig.savefig("/mnt/project-files/images/photoStand_rev1_base.png",facecolor="white"); print("ok")

# render8.py: clean7 geometry + agreed unsaved changes (2026-10-05): frame lap half 15.0, tongues 14.85 (0.15 glue gap),
# cradle walls 1.86 with outside corners r5.86, pocket and camera window cut through the top bar, no light bars.
exec(open("render7.py").read().split("fig=plt.figure")[0])
from shapely.geometry import MultiPoint
import matplotlib.patches as mp
CW=1.86; pb=POCKET.bounds
CRAD=sbox(pb[0]-CW,pb[1]-CW,pb[2]+CW,pb[3]+CW).buffer(-(4+CW),join_style=1).buffer(4+CW,join_style=1)
CUT_L,CUT_R=CRAD.bounds[0],CRAD.bounds[2]
FRH=15.0                                    # frame half of each lap (50 layers); tongue = 30-15-GLUE
def lapz(side,cut):
    t=sbox(cut,TB0-1,cut+LAP,TB1+1) if side>0 else sbox(cut-LAP,TB0-1,cut,TB1+1)
    b=sbox(HB,-1,HB+LAP,BH+1) if side>0 else sbox(-HB-LAP,-1,-HB,BH+1)
    return unary_union([t,b])
def frame_parts(side):
    global CUT_X
    CUT_X=CUT_R if side>0 else -CUT_L
    prof=side_frame()
    if side<0: prof=affinity.scale(prof,xfact=-1,origin=(0,0))
    lz=lapz(side,CUT_R if side>0 else CUT_L)
    return prof,lz
def tm_layers():
    bar=sbox(CUT_L,-15,CUT_R,15); s=unary_union([bar,CRAD])
    return s.difference(CAMWIN), s.difference(POCKET)
def draw(off):
    R.FACES.clear(); o=lambda k: np.array(off.get(k,(0,0,0)),float)
    # board + base middle (flat)
    d=o("board"); col=MID
    A.box(d[0],BW+d[0],d[1],BD+d[1],d[2],FL+d[2],col); A.box(d[0],17.5+d[0],d[1],BD+d[1],FL+d[2],RL+d[2],col); A.box(BW-17.5+d[0],BW+d[0],d[1],BD+d[1],FL+d[2],RL+d[2],col)
    A.box(17.5+d[0],BW-17.5+d[0],BD-27+d[1],BD+d[1],FL+d[2],RL+d[2],col)
    for i in range(3):
        for x in (3.2,BW-14.4): marker3d(x+d[0],10+25*i+d[1],RL+d[2])
    for i in range(5): marker3d(28+25*i+d[0],BD-20+d[1],RL+d[2])
    for x0 in (0.8,BW-15.8):
        A.box(x0+d[0],x0+15+d[0],BD-37+d[1],BD-21+d[1],d[2],15+FL+d[2],col); marker3d(x0+1.9+d[0],BD-35.1+d[1],15+FL+d[2])
        A.box(x0+d[0],x0+15+d[0],BD-21+d[1],BD-5+d[1],d[2],30+FL+d[2],col); marker3d(x0+1.9+d[0],BD-19.1+d[1],30+FL+d[2])
    for s in (-1,1):
        x0,x1=sorted([CX+s*HB,CX+s*(HB+LAP)]); A.box(x0+d[0],x1+d[0],CY+GLUE+d[1],CY+15+d[1],d[2],BH+d[2],col)
    # side frames (printed on their sides): full depth outside the laps, front half (15.0) in them
    for s in (-1,1):
        d=o("right" if s>0 else "left"); prof,lz=frame_parts(s)
        ext_y(prof.difference(lz),CY-15+d[1],CY+15+d[1],FR,dx=CX+d[0]); ext_y(prof.intersection(lz),CY-15+d[1],CY-15+FRH+d[1],FR,dx=CX+d[0])
        for g in (prof.difference(lz),prof.intersection(lz)):
            for F,n,c,b in R.FACES[-0:]: pass
    # top middle + cradle (flat): floor with camera window, walls/bar around the pocket, back-half tongues
    d=o("top"); fl,wl=tm_layers()
    ext_z(fl,TB0+d[2],H+d[2],MID,dx=CX+d[0],dy=CY+d[1]); ext_z(wl,H+d[2],TB1+d[2],MID,dx=CX+d[0],dy=CY+d[1])
    for x0 in (CUT_R,CUT_L-LAP): ext_y(sbox(x0,TB0,x0+LAP,TB1),CY+GLUE+d[1],CY+15+d[1],MID,dx=CX+d[0],dz=d[2]) if False else A.box(CX+x0+d[0],CX+x0+LAP+d[0],CY+GLUE+d[1],CY+15+d[1],TB0+d[2],TB1+d[2],MID)
def view(ax,title,phone=True,off={}):
    draw(off)
    if phone and not off: A.box(CX+PCX-PH_L/2,CX+PCX+PH_L/2,CY+PCY-PH_W/2,CY+PCY+PH_W/2,H,H+8.6,PHONE)
    av=np.vstack([F for F,_,_,_ in R.FACES]); eye=(-1.0,-1.6,0.8); e=np.array(eye); e=e/np.linalg.norm(e); rt=np.cross(-e,[0,0,1.]); rt/=np.linalg.norm(rt); up=np.cross(rt,-e)
    img,cam=R.render(eye,2.4,(0.3,-0.7,1.0),((av@rt).min()-10,(av@rt).max()+10,(av@up).min()-10,(av@up).max()+10)); ax.imshow(img); ax.axis("off"); ax.set_title(title,fontsize=15,fontweight="bold")
    return cam
fig=plt.figure(figsize=(24,26),dpi=80)
fig.suptitle("Calibration stand: agreed changes through 2026-10-05 (Bone White; mm; concept, sizes Estimated; light bars and fillets not drawn)",fontsize=18,fontweight="bold",y=0.998)
ax=fig.add_axes([0.0,0.6,0.5,0.37]); cam=view(ax,"Assembled (phone in the cradle)")
ax=fig.add_axes([0.5,0.6,0.47,0.35])
EX={"left":(-70,-40,0),"right":(70,-40,0),"top":(0,40,60),"board":(0,0,0)}
cam=view(ax,"Exploded: 4 parts, glued half-laps",False,EX)
P2=lambda p: np.array(R.proj(cam,np.array(p,float)))
def call(p,off,t): ax.annotate(t,xy=P2(p),xytext=off,textcoords="offset points",fontsize=12,fontweight="bold",color="#1f5fa8",ha="center",arrowprops=dict(arrowstyle="-",color="#1f5fa8"),bbox=dict(fc="white",ec="none",alpha=.9))
call([CX+157+70,CY-55,60],(-30,-150),"right side frame\n(prints on its side,\nfront face down)")
call([CX+40,CY+40+40,TB1+60],(-160,30),"top middle + cradle\n(prints flat)")
call([CX,0,FL],(0,-60),"board + base middle (prints flat)")
call([CX+CUT_R+10,CY+40+10,TB0+60],(60,60),"back-half tongue")
# front view
ax2=fig.add_axes([0.03,0.33,0.6,0.25])
def fv(axx,g,c=BONE,ec="k",lw=0.9):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; axx.fill(x,y,fc=c,ec=ec,lw=lw)
        for i in p.interiors: xi,yi=i.xy; axx.fill(xi,yi,fc="white",ec=ec,lw=lw)
fv(ax2,sbox(-HB,0,HB,FL),MID); fv(ax2,sbox(-HB,FL,-HB+17.5,RL),MID); fv(ax2,sbox(HB-17.5,FL,HB,RL),MID)
fv(ax2,sbox(CUT_L,TB0,CUT_R,H),MID); fv(ax2,sbox(CUT_L,H,CRAD.bounds[0]+0.0+ (POCKET.bounds[0]-CRAD.bounds[0]),TB1),MID); fv(ax2,sbox(POCKET.bounds[2],H,CUT_R,TB1),MID)
ax2.add_patch(mp.Rectangle((CAMWIN.bounds[0],TB0),CAMWIN.bounds[2]-CAMWIN.bounds[0],H-TB0,fc="white",ec="#c0392b",lw=1,ls="--"))
for s in (-1,1):
    prof,lz=frame_parts(s); fv(ax2,prof)
    for x in ((CUT_R,CUT_R+LAP) if s>0 else (CUT_L,CUT_L-LAP)): ax2.plot([x,x],[TB0,TB1],color="#c0392b",lw=1,ls="--")
    for x in (s*HB,s*(HB+LAP)): ax2.plot([x,x],[0,BH],color="#c0392b",lw=1,ls="--")
ax2.add_patch(mp.Rectangle((PCX-PH_L/2,H),PH_L,8.6,fc="#8b9bb0",ec="k",lw=0.8))
def d2(a,b,off,t,vert=False,fs=11):
    a=np.array(a,float); b=np.array(b,float); o=np.array(off,float)
    ax2.annotate("",xy=b+o,xytext=a+o,arrowprops=dict(arrowstyle="<|-|>",color="#555",lw=1.1,shrinkA=0,shrinkB=0))
    m=(a+b)/2+o; ax2.text(m[0],m[1],t,fontsize=fs,fontweight="bold",ha="center",va="center",rotation=90 if vert else 0,bbox=dict(fc="white",ec="none",pad=1.2))
d2([-PX1,0],[PX1,0],[0,-16],f"{2*PX1:.0f} overall"); d2([-HB,0],[HB,0],[0,-7],f"board {BW}",fs=10)
d2([PX1,0],[PX1,TB1],[22,0],f"{TB1:.0f} overall",True); d2([0,FL],[0,LENS_Z],[-8,0],f"lens {D0:.0f} above board floor",True,10)
d2([CUT_L,TB1],[CUT_R,TB1],[0,10],f"top middle {CUT_R-CUT_L:.1f} (+{LAP} laps)",fs=10)
ax2.text(0,-27,"red dashed: half-lap cuts (frame keeps the front 15.0, tongue is the back 14.85: 0.15 glue gap) and the camera window",ha="center",fontsize=11,color="#c0392b")
ax2.set_xlim(-PX1-30,PX1+35); ax2.set_ylim(-32,TB1+22); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("Front view (section at the lens)",fontsize=14,fontweight="bold")
# cradle plan
ax3=fig.add_axes([0.66,0.33,0.32,0.25]); fv(ax3,unary_union([sbox(CUT_L,-15,CUT_R,15),CRAD]),MID); fv(ax3,POCKET,"white"); fv(ax3,CAMWIN,"#ddd")
ax3.text(CAMWIN.centroid.x,CAMWIN.centroid.y,"camera\nwindow",ha="center",va="center",fontsize=10)
ax3.text(POCKET.centroid.x+30,POCKET.centroid.y,f"phone pocket (+0.5 per side)\nwalls {CW}, corners r{4+CW:.2f} outside / r4 inside",ha="center",va="center",fontsize=10)
ax3.set_aspect("equal"); ax3.axis("off"); ax3.set_title(f"Top middle, top view: {CUT_R-CUT_L:.1f} x {CRAD.bounds[3]-CRAD.bounds[1]:.1f} cradle",fontsize=13,fontweight="bold")
# plates, with Orca's convex-outline check against the excluded corner
plate=sbox(0,0,256,256).buffer(-0.5); corner=sbox(0,0,18,28)
CUT_X=CUT_R; fr=side_frame(); CUT_X=-CUT_L; fl_=affinity.scale(side_frame(),xfact=-1,origin=(0,0))
pl={"right side frame (on its side)":fr,"left side frame (on its side)":fl_,"top middle + cradle (flat)":unary_union([sbox(CUT_L,-15,CUT_R,15),CRAD,sbox(CUT_L-LAP,0,CUT_R+LAP,15)]),"board + base middle (flat)":unary_union([sbox(-HB,-CY,HB,CY),sbox(-HB-LAP,0,HB+LAP,15)])}
for i,(nm,g) in enumerate(pl.items()):
    b=g.bounds; best=None
    for ang in (0,90,180,270):
        r=affinity.rotate(g,ang,origin=(0,0)); rb=r.bounds; w,h=rb[2]-rb[0],rb[3]-rb[1]
        if w>255 or h>255: continue
        r=affinity.translate(r,256-0.5-rb[2],256-0.5-rb[3])          # push to the far corner
        hull=r.convex_hull
        if plate.contains(r) and not hull.intersects(corner): best=(ang,r); break
    print(nm,"fits, Orca convex-outline clear of the corner" if best else "DOES NOT FIT", f"{b[2]-b[0]:.1f} x {b[3]-b[1]:.1f}", "turned", best[0] if best else None)
    axp=fig.add_axes([0.03+i*0.24,0.03,0.22,0.26]); axp.add_patch(mp.Rectangle((0,0),256,256,fc="#eee",ec="#888")); axp.add_patch(mp.Rectangle((0,0),18,28,fc="#c8c8c8",ec="none"))
    if best:
        fv(axp,best[1]); x,y=best[1].convex_hull.exterior.xy; axp.plot(x,y,color="#c0392b",lw=0.8,ls=":")
    axp.set_xlim(-4,260); axp.set_ylim(-4,260); axp.set_aspect("equal"); axp.axis("off"); axp.set_title(f"{nm}\n{b[2]-b[0]:.0f} x {b[3]-b[1]:.0f} (dotted: Orca's outline check)",fontsize=11)
print("cuts",round(CUT_L,2),round(CUT_R,2),"cradle",round(CRAD.bounds[2]-CRAD.bounds[0],2),"x",round(CRAD.bounds[3]-CRAD.bounds[1],2))
fig.savefig("/mnt/project-files/images/calibrationStand_audit8.png",facecolor="white"); print("saved")

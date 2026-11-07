# Clean render of clean7.py's design. Run from this folder: python3 render7.py
exec(open("clean7.py").read().split('if __name__')[0])
import matplotlib.patches as mp
BAR3=np.array([0.42,0.42,0.45]); LEDC=np.array([1.0,0.85,0.25]); WHITEM=np.array([0.97,0.96,0.92]); SEAM=np.array([0.55,0.52,0.45])
FR=BONE; MID=BONE*0.94                      # same Bone White filament; middles drawn a shade darker so the parts read
def marker3d(x0,y0,z,s=11.16):
    A.box(x0-0.9,x0+s+0.9,y0-0.9,y0+s+0.9,z,z+0.15,WHITEM); rng=np.random.default_rng(int(x0*7+y0*3+z)); c=s/6
    for a in ((x0,x0+s,y0,y0+c),(x0,x0+s,y0+s-c,y0+s),(x0,x0+c,y0,y0+s),(x0+s-c,x0+s,y0,y0+s)): A.box(*a,z+0.15,z+0.2,MK)
    for i in range(4):
        for j in range(4):
            if rng.random()<0.5: A.box(x0+c*(1+i),x0+c*(2+i),y0+c*(1+j),y0+c*(2+j),z+0.15,z+0.2,MK)
def board3d():
    col=MID
    A.box(0,BW,0,BD,0,FL,col); A.box(0,17.5,0,BD,FL,RL,col); A.box(BW-17.5,BW,0,BD,FL,RL,col); A.box(17.5,BW-17.5,BD-27,BD,FL,RL,col)
    A.box(17.5,BW-17.5,BD-67,BD-65.5,FL-0.05,FL+0.05,MK)
    for i in range(3):
        for x in (3.2,BW-14.4): marker3d(x,10+25*i,RL)
    for i in range(5): marker3d(28+25*i,BD-20,RL)
    for x0 in (0.8,BW-15.8):
        A.box(x0,x0+15,BD-37,BD-21,0,15+FL,col); marker3d(x0+1.9,BD-35.1,15+FL)
        A.box(x0,x0+15,BD-21,BD-5,0,30+FL,col); marker3d(x0+1.9,BD-19.1,30+FL)
    for s in (-1,1):                                           # board's lap tongues (back half of the foot)
        x0,x1=sorted([CX+s*HB,CX+s*(HB+LAP)]); A.box(x0,x1,CY,CY+15,0,BH,col)
def stand3d():
    global CUT_X
    for s,cut in ((1,CUT_R),(-1,-CUT_L)):
        CUT_X=cut; prof=side_frame(); sc=lambda g: affinity.scale(g,xfact=s,origin=(0,0))
        lz=unary_union([lapzone(1,"top") if s>0 else sbox(cut,TB0-1,cut+LAP,TB1+1),lapzone(1,"base")])
        ext_y(sc(prof.difference(lz)),CY-15,CY+15,FR,dx=CX); ext_y(sc(prof.intersection(lz)),CY-15,CY-GLUE,FR,dx=CX)
        # lights
        hb=place(sbox(-10,-10,10,10),-45,HX,HZ,True); x,z=hb.centroid.x,hb.centroid.y
        A.rbox(CX+s*x,z,20,20,45*s,CY-149,CY+149,BAR3)
        led=sc(place(sbox(-7,-10.3,7,-10),-45,HX,HZ,True)); A.rbox(CX+led.centroid.x,led.centroid.y,14,0.3,45*s,CY-149,CY+149,LEDC)
        lx=CX+s*LX; A.box(lx-10,lx+10,CY-149,CY+149,LZ-10,LZ+10,BAR3); A.box(*sorted([lx-s*10,lx-s*10.3]),CY-149,CY+149,LZ-7,LZ+7,LEDC)
    # top middle: bar between the cuts + back-half tongues + cradle
    mid=topbar().intersection(sbox(CUT_L,TB0-1,CUT_R,TB1+1)); ext_y(mid,CY-15,CY+15,MID,dx=CX)
    for x0 in (CUT_R,CUT_L-LAP): ext_y(topbar().intersection(sbox(x0,TB0-1,x0+LAP,TB1+1)),CY+GLUE,CY+15,MID,dx=CX)
    ext_z(CRAD.difference(POCKET),TB0,TB1,MID,dx=CX,dy=CY); ext_z(CRAD.difference(CAMWIN).difference(sbox(CUT_L,-15,CUT_R,15)),TB0,H,MID,dx=CX,dy=CY)
    A.box(CX+PCX-PH_L/2,CX+PCX+PH_L/2,CY+PCY-PH_W/2,CY+PCY+PH_W/2,H,H+8.6,PHONE)
fig=plt.figure(figsize=(22,27),dpi=90)
fig.suptitle("Calibration stand, clean redraw: changes 2-23 (Bone White; mm; concept, sizes Estimated)",fontsize=20,fontweight="bold",y=0.995)
R.FACES.clear(); board3d(); stand3d()
ax=fig.add_axes([0.0,0.55,1.0,0.43])
av=np.vstack([F for F,_,_,_ in R.FACES]); eye=(-1.0,-1.6,0.8); e=np.array(eye); e=e/np.linalg.norm(e); rt=np.cross(-e,[0,0,1.]); rt/=np.linalg.norm(rt); up=np.cross(rt,-e)
img,cam=R.render(eye,2.6,(0.3,-0.7,1.0),((av@rt).min()-20,(av@rt).max()+20,(av@up).min()-15,(av@up).max()+15)); ax.imshow(img); ax.axis("off")
P2=lambda p: np.array(R.proj(cam,np.array(p,float)))
def call(p,off,t):
    ax.annotate(t,xy=P2(p),xytext=off,textcoords="offset points",fontsize=13,fontweight="bold",color="#1f5fa8",ha="center",va="center",arrowprops=dict(arrowstyle="-",color="#1f5fa8",lw=1.2),bbox=dict(fc="white",ec="none",alpha=.92,pad=1.5))
call([CX+PX1,CY-15,90],(110,0),"side frame: post, foot, bar end, both clips\n(one piece, printed on its side)")
call([CX+CUT_R+10,CY-15,TB1],(70,70),"glued half-lap")
call([CX-CUT_L-10,CY-15,TB1],(-40,80),"glued half-lap")
call([CX+40,CY-40,TB1],(-120,90),"top middle + cradle (flat)")
call([CX-60,0,FL],(-90,-70),"board + base middle (flat)")
call([CX+HB+10,CY-15,9],(60,-80),"glued half-lap")
call([CX+LX-4,CY-15,LZ+14],(160,-10),"low clip (Barrina snap U from the 3mf)")
call([CX+HX+10,CY-15,HZ+14],(160,40),"high clip (Barrina snap U from the 3mf)")
# ---- front view ----
ax2=fig.add_axes([0.03,0.27,0.62,0.27])
def fv(axx,g,c=BONE,ec="k",lw=0.9,ls="-",dx=0):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; axx.fill(np.array(x)+dx,y,fc=c,ec=ec,lw=lw,ls=ls)
        for i in p.interiors: xi,yi=i.xy; axx.fill(np.array(xi)+dx,yi,fc="white",ec=ec,lw=lw)
fv(ax2,sbox(-HB,0,HB,FL),MID); fv(ax2,sbox(-HB,FL,-HB+17.5,RL),MID); fv(ax2,sbox(HB-17.5,FL,HB,RL),MID)
fv(ax2,topbar().intersection(sbox(CUT_L,TB0-1,CUT_R,TB1+1)),MID)
for s,cut in ((1,CUT_R),(-1,-CUT_L)):
    CUT_X=cut; sc=lambda g: affinity.scale(g,xfact=s,origin=(0,0)); fv(ax2,sc(side_frame()))
    for k in (LOW,HIGH): fv(ax2,sc(plc(sbox(-10,-10,10,10),k)),"#8a8a90")
    for x in ((cut, cut+LAP) if s>0 else (-cut,-cut-LAP)):
        ax2.plot([x,x],[TB0,TB1],color="#c0392b",lw=1,ls="--")
    for x in (s*HB,s*(HB+LAP)): ax2.plot([x,x],[0,BH],color="#c0392b",lw=1,ls="--")
ax2.add_patch(mp.Rectangle((PCX-PH_L/2,H),PH_L,8.6,fc="#8b9bb0",ec="k",lw=0.8))
def d2(a,b,off,t,vert=False,fs=11):
    a=np.array(a,float); b=np.array(b,float); o=np.array(off,float)
    for p in (a,b): ax2.plot([p[0],p[0]+o[0]],[p[1],p[1]+o[1]],color="#555",lw=0.6,ls=(0,(3,2)))
    ax2.annotate("",xy=b+o,xytext=a+o,arrowprops=dict(arrowstyle="<|-|>",color="#555",lw=1.1,shrinkA=0,shrinkB=0))
    m=(a+b)/2+o; ax2.text(m[0],m[1],t,color="#222",fontsize=fs,fontweight="bold",ha="center",va="center",rotation=90 if vert else 0,bbox=dict(fc="white",ec="none",pad=1.2))
d2([-PX1,0],[PX1,0],[0,-16],f"{2*PX1:.0f} overall"); d2([-HB,0],[HB,0],[0,-7],f"board {BW}",fs=10)
d2([PX1,0],[PX1,TB1],[22,0],f"{TB1:.0f} overall",True); d2([PX1,0],[PX1,HZ],[10,0],f"{HZ}",True,10)
d2([-PX1,0],[-PX1,LZ],[-10,0],f"{LZ:.1f}",True,10); d2([0,FL],[0,LENS_Z],[-8,0],f"lens {D0:.0f} above board floor",True,10)
d2([CUT_L,TB1],[CUT_R,TB1],[0,10],f"top middle {CUT_R-CUT_L:.0f} (+{LAP} laps)",fs=10)
ax2.text(0,-27,"red dashed: half-lap cuts (20 mm overlap, 0.15 mm glue gap per side); gray: light bars",ha="center",fontsize=11,color="#c0392b")
ax2.set_xlim(-PX1-30,PX1+35); ax2.set_ylim(-32,TB1+22); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("Front view",fontsize=14,fontweight="bold")
# ---- clip close-ups: 3mf section vs stand clip ----
CUT_X=CUT_R; F=side_frame()
axa=fig.add_axes([0.67,0.41,0.31,0.13]); fv(axa,CLIP,"#e6e1d3"); fv(axa,sbox(-10,-10,10,10),"#8a8a90",lw=0.6)
axa.set_aspect("equal"); axa.axis("off"); axa.set_title("Source: barrinaClip_rev2.3mf, mesh section\n(untilted; matches its build script to 0.000 mm²)",fontsize=11)
axb=fig.add_axes([0.67,0.27,0.15,0.13]); fv(axb,F); fv(axb,plc(sbox(-10,-10,10,10),HIGH),"#8a8a90")
axb.set_xlim(HX-22,PX1+2); axb.set_ylim(HZ-24,HZ+24); axb.set_aspect("equal"); axb.axis("off"); axb.set_title("High clip",fontsize=11,fontweight="bold")
axc=fig.add_axes([0.83,0.27,0.15,0.13]); fv(axc,F); fv(axc,plc(sbox(-10,-10,10,10),LOW),"#8a8a90")
axc.set_xlim(LX-22,PX1+2); axc.set_ylim(BH-6,LZ+24); axc.set_aspect("equal"); axc.axis("off"); axc.set_title("Low clip",fontsize=11,fontweight="bold")
# ---- parts on the plate ----
pr=parts(); names=list(pr)
for i,nm in enumerate(names):
    axp=fig.add_axes([0.03+i*0.24,0.04,0.22,0.2]); axp.add_patch(mp.Rectangle((0,0),256,256,fc="#eee",ec="#888")); axp.add_patch(mp.Rectangle((0,0),18,28,fc="#c8c8c8",ec="none"))
    g=pr[nm]; b=g.bounds; g=affinity.translate(g,128-(b[0]+b[2])/2,128-(b[1]+b[3])/2); fv(axp,g)
    axp.set_xlim(-4,260); axp.set_ylim(-4,260); axp.set_aspect("equal"); axp.axis("off"); axp.set_title(f"{nm}\n{b[2]-b[0]:.0f} x {b[3]-b[1]:.0f}",fontsize=11)
fig.savefig("/mnt/project-files/images/calibrationStand_clean7.png",facecolor="white"); print("saved")

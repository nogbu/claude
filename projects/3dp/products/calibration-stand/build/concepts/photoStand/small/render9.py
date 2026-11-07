# render9.py: picture of clean8.py's geometry (agreed changes 2 to 63).
# Run from this folder: python3 render9.py  ->  /mnt/project-files/images/calibrationStand_clean8.png
# No light bars (the user's rule for this product). Not drawn: the 0.9 edges (54), the step chamfer (50), the V-slots (hidden under the parts).
exec(open("render7.py").read().split("fig=plt.figure")[0])
exec(open("clean8.py").read().split("\nif __name__")[0])
import matplotlib.patches as mp
MIDC=BONE*0.94
def ext_x(poly_yz,x0,x1,col,dz=0):
    for p in getattr(poly_yz,"geoms",[poly_yz]):
        m=trimesh.creation.extrude_polygon(p,x1-x0,engine="earcut"); v=m.vertices.copy(); m.vertices=np.c_[x0+v[:,2],v[:,0],v[:,1]+dz]; m.fix_normals(); mesh_faces(m,col)
def ridge3d(xc,sign,z0,col,d):
    sec=ridge_section(RG_Y+d[1]); x0,x1=sorted([xc,xc+sign*RG_L]); ext_x(affinity.translate(sec,0,z0+d[2]),CX+x0+d[0],CX+x1+d[0],col)
def draw(off={},phone=True):
    R.FACES.clear(); o=lambda k: np.array(off.get(k,(0,0,0)),float)
    # board part (prints flat)
    d=o("board"); col=MIDC; tr=lambda g: affinity.translate(g,CX+d[0],d[1])
    ext_z(tr(board_plan().intersection(sbox(-HB,0,HB,BD))),d[2],FL+d[2],col)
    ext_z(tr(sbox(-HB,0,HB,BD).buffer(-BOARD_R,join_style=1).buffer(BOARD_R,join_style=1).difference(channel())),FL+d[2],RL+d[2],col)
    for s in (1,-1): ext_y(affinity.translate(bx(s*HB,s*CUT_B,0,BH),CX+d[0],0),Y0+d[1],Y1+d[1],col)
    ext_z(tr(side_end_fillets()),d[2],RL+d[2],col)
    for nm,p,z in posts(): ext_z(tr(p),RL+d[2],z+d[2],col)
    for nm,m,z in markers(): b=m.bounds; marker3d(CX+b[0]+d[0],b[1]+d[1],z+d[2])
    A.box(CX-HB+RAILW+d[0],CX+HB-RAILW+d[0],GROOVE[0]+d[1],GROOVE[1]+d[1],FL-0.05+d[2],FL+0.05+d[2],np.array([0.35,0.33,0.3]))
    for s in (1,-1): ridge3d(s*CUT_B,s,0,col,d)
    # side frames (print on their sides, front face down)
    for s,cut,k in ((1,CUT_R,"right"),(-1,-CUT_L,"left")):
        d=o(k); prof=affinity.scale(frame_profile(cut),xfact=s,origin=(0,0))
        ext_y(affinity.translate(prof,0,d[2]),Y0+d[1],Y1+d[1],BONE,dx=CX+d[0])
    # top middle (prints flat): floor with the camera window, walls around the pocket, ridges at both ends
    d=o("top"); fl,wl=top_layers(); tr=lambda g: affinity.translate(g,CX+d[0],d[1])
    ext_z(tr(fl),TB0+d[2],TB0+FLOOR_T+d[2],MIDC); ext_z(tr(wl),TB0+FLOOR_T+d[2],TB1+d[2],MIDC)
    ridge3d(CUT_R,1,TB0,MIDC,d); ridge3d(CUT_L,-1,TB0,MIDC,d)
    if phone and not off: A.box(CX+PCX-PH_L/2,CX+PCX+PH_L/2,CY+PCY-PH_W/2,CY+PCY+PH_W/2,H,H+8.6,PHONE)
def view(ax,title,off={},eye=(-1.0,-1.6,0.8)):
    draw(off)
    av=np.vstack([F for F,_,_,_ in R.FACES]); e=np.array(eye); e=e/np.linalg.norm(e); rt=np.cross(-e,[0,0,1.]); rt/=np.linalg.norm(rt); up=np.cross(rt,-e)
    img,cam=R.render(eye,2.4,(0.3,-0.7,1.0),((av@rt).min()-10,(av@rt).max()+10,(av@up).min()-10,(av@up).max()+10)); ax.imshow(img); ax.axis("off"); ax.set_title(title,fontsize=15,fontweight="bold")
    return cam
def fv(axx,g,c=BONE,ec="k",lw=0.9):
    for p in getattr(g,"geoms",[g]):
        if p.is_empty: continue
        x,y=p.exterior.xy; axx.fill(x,y,fc=c,ec=ec,lw=lw)
        for i in p.interiors: xi,yi=i.xy; axx.fill(xi,yi,fc="white",ec=ec,lw=lw)
fig=plt.figure(figsize=(24,30),dpi=75)
fig.suptitle("Calibration stand, clean8: agreed changes 2 to 63 drawn together (Bone White; mm; concept, nothing built)\n"
             "Not drawn: light bars, the 0.9 edges (54), the step chamfer (50), the r0.9 rail/end fillet (61) and the V-slots under the frames",fontsize=16,fontweight="bold",y=0.997)
ax=fig.add_axes([0.0,0.66,0.5,0.3]); cam=view(ax,"Assembled, phone in the cradle")
ax=fig.add_axes([0.5,0.66,0.5,0.3]); EX={"left":(-60,0,0),"right":(60,0,0),"top":(0,0,70),"board":(0,0,0)}
cam=view(ax,"Exploded: 4 parts, glued ridge joints",EX)
P2=lambda p: np.array(R.proj(cam,np.array(p,float)))
def call(p,off,t): ax.annotate(t,xy=P2(p),xytext=off,textcoords="offset points",fontsize=12,fontweight="bold",color="#1f5fa8",ha="center",arrowprops=dict(arrowstyle="-",color="#1f5fa8"),bbox=dict(fc="white",ec="none",alpha=.9))
call([CX+PX1+60,Y0,100],(-130,-150),"side frames: print on their side,\nfront face down (76.8 = 256 layers)")
call([CX+40,Y0,TB1+70],(-60,60),"top middle + cradle: prints flat")
call([CX-60,0,FL],(-40,-60),"board part: prints flat")
call([CX+CUT_R+4,RG_Y,TB0+70+3],(80,40),"ridge 12 x 6 x 8")
# front view at the ridge (y 90.5)
ax2=fig.add_axes([0.02,0.37,0.62,0.27])
fv(ax2,sbox(-HB,0,HB,FL),MIDC); fv(ax2,sbox(-HB,FL,-HB+RAILW,RL),MIDC); fv(ax2,sbox(HB-RAILW,FL,HB,RL),MIDC)
for s in (1,-1): fv(ax2,bx(s*HB,s*CUT_B,0,BH),MIDC)
fv(ax2,sbox(CUT_L,TB0,CUT_R,TB1),MIDC)
for s,cut in ((1,CUT_R),(-1,-CUT_L)): fv(ax2,affinity.scale(frame_profile(cut),xfact=s,origin=(0,0)))
for x in (CUT_L,CUT_R): ax2.plot([x,x],[TB0,TB1],color="#c0392b",lw=1.2,ls="--")
for x in (-CUT_B,CUT_B): ax2.plot([x,x],[0,BH],color="#c0392b",lw=1.2,ls="--")
for xc,sg,z0 in ((CUT_R,1,TB0),(CUT_L,-1,TB0),(CUT_B,1,0),(-CUT_B,-1,0)):
    ax2.add_patch(mp.Rectangle((min(xc,xc+sg*RG_L),z0),RG_L,RG_TOP,fc="#1f5fa8",ec="none",alpha=0.7))
ax2.add_patch(mp.Rectangle((PCX-PH_L/2,H),PH_L,8.6,fc="#8b9bb0",ec="k",lw=0.8))
def d2(a,b,off,t,vert=False,fs=11):
    a=np.array(a,float); b=np.array(b,float); o=np.array(off,float)
    ax2.annotate("",xy=b+o,xytext=a+o,arrowprops=dict(arrowstyle="<|-|>",color="#555",lw=1.1,shrinkA=0,shrinkB=0))
    m=(a+b)/2+o; ax2.text(m[0],m[1],t,fontsize=fs,fontweight="bold",ha="center",va="center",rotation=90 if vert else 0,bbox=dict(fc="white",ec="none",pad=1.2))
d2([-PX1,0],[PX1,0],[0,-16],f"{2*PX1:.0f} overall"); d2([-CUT_B,0],[CUT_B,0],[0,-7],f"board part {2*CUT_B:.0f} (board {BW})",fs=10)
d2([PX1,0],[PX1,TB1],[20,0],f"{TB1:.0f} overall",True); d2([0,FL],[0,LENS_Z],[-8,0],f"lens {D0:.1f} above the board floor",True,10)
d2([CUT_L,TB1],[CUT_R,TB1],[0,10],f"top middle {CUT_R-CUT_L:.2f} (cuts x {CUT_L:.2f} / {CUT_R:.2f})",fs=10)
ax2.text(0,-27,"red dashed: glued cuts (top x -29.60 / 130.40, base x ±105); blue: ridges (12 x 6 x 8) on the middle parts' bed faces, 21.9 from the back",ha="center",fontsize=11,color="#c0392b")
ax2.annotate("r6 (60)",xy=(PX0-1.8,43.36+1.8),xytext=(95,60),fontsize=10,color="#e6550d",fontweight="bold",arrowprops=dict(arrowstyle="-",color="#e6550d"))
ax2.annotate("r6 (60)",xy=(PX0-1.8,141.04+1.8),xytext=(95,150),fontsize=10,color="#e6550d",fontweight="bold",arrowprops=dict(arrowstyle="-",color="#e6550d"))
ax2.annotate("r3.7 (60)",xy=(134.6,140.5),xytext=(95,125),fontsize=10,color="#e6550d",fontweight="bold",arrowprops=dict(arrowstyle="-",color="#e6550d"))
ax2.set_xlim(-PX1-25,PX1+30); ax2.set_ylim(-32,TB1+20); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("Front view (right frame's clip corners marked)",fontsize=14,fontweight="bold")
# top middle plan
ax3=fig.add_axes([0.66,0.47,0.33,0.15]); fv(ax3,unary_union([TOPMID,ridge_plan(CUT_R,1),ridge_plan(CUT_L,-1)]),MIDC); fv(ax3,POCKET,"white"); fv(ax3,CAMWIN,"#ddd")
ax3.text(CAMWIN.centroid.x,CAMWIN.centroid.y,"camera\nwindow",ha="center",va="center",fontsize=9)
ax3.text(POCKET.centroid.x+35,POCKET.centroid.y,f"pocket {PKL:.1f} x {PKW:.2f}, r4 corners\nwalls 1.86, end walls 3.10",ha="center",va="center",fontsize=10)
ax3.set_aspect("equal"); ax3.axis("off"); ax3.set_title(f"Top middle, top view: {CUT_R-CUT_L:.2f} x {DEP} plus ridges",fontsize=12,fontweight="bold")
# board plan
ax4=fig.add_axes([0.66,0.29,0.33,0.2]); fv(ax4,unary_union([board_plan(),side_end_fillets(),ridge_plan(CUT_B,1),ridge_plan(-CUT_B,-1)]),MIDC); fv(ax4,channel(),"#f4f1e8")
for nm,p,z in posts(): fv(ax4,p,MIDC)
for nm,m,z in markers(): fv(ax4,m.buffer(1.86,join_style=2),"white",lw=0.3); fv(ax4,m,"#222",lw=0)
ax4.add_patch(mp.Rectangle((-HB+RAILW,GROOVE[0]),2*(HB-RAILW),GROOVE[1]-GROOVE[0],fc="#555",ec="none"))
ax4.text(0,GROOVE[0]-8,"brim groove 1.5 x 5.7 deep",ha="center",fontsize=9); ax4.text(0,STOP+3,"stop",ha="center",fontsize=9)
ax4.set_aspect("equal"); ax4.axis("off"); ax4.set_title(f"Board part, top view: {2*CUT_B} x {BD}, ends {DEP} deep",fontsize=12,fontweight="bold")
# plates
plate=sbox(0,0,256,256).buffer(-0.5); corner=sbox(0,0,18,28)
pl={"right side frame (on its side)":frame_profile(CUT_R),"left side frame (on its side)":frame_profile(-CUT_L),
    "top middle (flat)":unary_union([TOPMID,ridge_plan(CUT_R,1),ridge_plan(CUT_L,-1)]),"board part (flat)":unary_union([board_plan(),side_end_fillets(),ridge_plan(CUT_B,1),ridge_plan(-CUT_B,-1)])}
for i,(nm,g) in enumerate(pl.items()):
    b=g.bounds; best=None
    for ang in (0,90,180,270):
        r=affinity.rotate(g,ang,origin=(0,0)); rb=r.bounds; r=affinity.translate(r,256-0.5-rb[2],256-0.5-rb[3])
        if plate.contains(r) and not r.convex_hull.intersects(corner): best=r; break
    axp=fig.add_axes([0.03+i*0.24,0.02,0.22,0.24]); axp.add_patch(mp.Rectangle((0,0),256,256,fc="#eee",ec="#888")); axp.add_patch(mp.Rectangle((0,0),18,28,fc="#c8c8c8",ec="none"))
    if best is not None:
        fv(axp,best); x,y=best.convex_hull.exterior.xy; axp.plot(x,y,color="#c0392b",lw=0.8,ls=":")
    axp.set_xlim(-4,260); axp.set_ylim(-4,260); axp.set_aspect("equal"); axp.axis("off"); axp.set_title(f"{nm}\n{b[2]-b[0]:.1f} x {b[3]-b[1]:.1f} (dotted: Orca's outline check)",fontsize=11)
fig.savefig("/mnt/project-files/images/calibrationStand_clean8.png",facecolor="white"); print("saved")

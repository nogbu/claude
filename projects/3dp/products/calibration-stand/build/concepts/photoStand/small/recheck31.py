# Recheck of changes 31-38: side-frame profile with change 31 (post 147-165) and 32 (r19 / r1), top cut 130.40 (change 41), base cut 105 (change 49).
exec(open("clean7.py").read().split('if __name__')[0])
from shapely.geometry import MultiPoint
PX0=147; CUTT=130.40; CUTB=105
def frame():
    lowU,highU=plc(SNAP,LOW),plc(SNAP,HIGH)
    lb=plc(sbox(-U_HALF,10,U_HALF,U_TOP),LOW)
    lowfill=unary_union([sbox(lb.bounds[0],BH,PX0+1,lb.bounds[3]),sbox(LX-10,BH,PX0+1,LZ-U_HALF+0.01)])
    a=P(-U_HALF,U_TOP,**{"ang":-45,"cx":HX,"cz":HZ,"m":True}); b=P(U_HALF,U_TOP,**{"ang":-45,"cx":HX,"cz":HZ,"m":True})
    hb=plc(sbox(-U_HALF,10,U_HALF,U_TOP),HIGH)
    highfill=unary_union([hb,MultiPoint([(a.x,a.y),(b.x,b.y),(PX0+1,b.y),(PX0+1,a.y)]).convex_hull])
    post=sbox(PX0,BH,PX1,TB0); foot=sbox(CUTB,0,PX1,BH); top=sbox(CUTT,TB0,PX1,TB1)
    s=unary_union([post,foot,top,lowfill,highfill])
    # r19 outer corners (top and bottom), r1 inside elbow at (147,167)
    for cx,cz in ((PX1-19,TB1-19),(PX1-19,19)):
        q=sbox(cx,cz,PX1,TB1) if cz>100 else sbox(cx,0,PX1,cz)
        s=s.difference(q.difference(Point(cx,cz).buffer(19,256)))
    s=unary_union([s,sbox(PX0-1,TB0-1,PX0,TB0).difference(Point(PX0-1,TB0-1).buffer(1,64))])
    s=s.difference(unary_union([plc(CLIP_ZONE,LOW),plc(CLIP_ZONE,HIGH)]))
    body=unary_union([s,lowU,highU]).buffer(0)
    return body
if __name__=="__main__":
    f=frame(); print("pieces",len(getattr(f,"geoms",[f])))
    post=sbox(PX0,BH,PX1,TB0)
    # how much of the post band x147-165 the clip zones remove
    for nm,k in (("low",LOW),("high",HIGH)):
        z=plc(CLIP_ZONE,k); print(nm,"clip zone x max",round(z.bounds[2],2),"cuts post area",round(z.intersection(post).area,2))
        print(nm,"U bounds",[round(v,2) for v in plc(SNAP,k).bounds])
    print("lowfill top", )
    # is the foot/post inside corner filled? sample the 1x1 square at (146,18)-(147,19)
    print("foot-post inside corner filled:",round(sbox(146,18,147,19).intersection(f).area,3),"(1.0 = solid)")
    print("elbow inside corner region (146,166)-(147,167) solid:",round(sbox(146,166,147,167).intersection(f).area,3))
    # what's solid in the band between high block and bar underside near the post
    for z in (140,150,160,166):
        seg=LineString([(CUTT,z),(PX0,z)]).intersection(f); print("z",z,"solid along x 130.4-147:",round(seg.length,1))
    hz=max(y for x,y in np.array(highfill.exterior.coords)) if False else None
# ---------------- pictures ----------------
import matplotlib.patches as mp
FRC="#e8e2d0"; MIDC="#cfc8b4"; BAD="#c0392b"; OK="#1e7d32"; MAR="#9ecae1"; BLK="#222"
def fill(ax,g,fc,ec="k",lw=0.8,hatch=None):
    for p in getattr(g,"geoms",[g]):
        if p.is_empty: continue
        x,y=p.exterior.xy; ax.fill(x,y,fc=fc,ec=ec,lw=lw,hatch=hatch)
        for i in p.interiors: xi,yi=i.xy; ax.fill(xi,yi,fc="white",ec=ec,lw=lw)
def cham(g,corner,c,sx,sz):        # 45 deg chamfer c at corner (x,z); sx,sz point into the material
    x,z=corner; return g.difference(SP([(x,z),(x+sx*c,z),(x,z+sz*c)]).buffer(0.001))
def sec_rail(ax,outer,inner,postx,title,good):
    # left rail section at a post (y in the post range) and at a marker; board coords x 0-22
    g=unary_union([sbox(0,0,22,FL),sbox(0,FL,17.5,RL)])
    g=cham(g,(0,RL),outer,1,-1); g=cham(g,(0,0),outer,1,1); g=cham(g,(17.5,RL),inner,-1,-1)
    fill(ax,g,MIDC)
    fill(ax,sbox(3.2,RL-0.6,14.4,RL),BLK,lw=0)
    for a,b in ((3.2-1.86,3.2),(14.4,14.4+1.86)): ax.add_patch(mp.Rectangle((a,RL),b-a,0.5,fc=MAR,ec="#3182bd",lw=0.6))
    clrL=3.2-1.86-outer; clrR=17.5-inner-(14.4+1.86)
    ax.text(8.8,RL+1.6,"marker (black) and its one-cell white margin (blue, 1.86)",ha="center",fontsize=9)
    ax.text(1.34-0.2,RL+3.3,f"outer {outer}: margin {'clear by '+format(clrL,'.2f') if clrL>=0 else 'cut by '+format(-clrL,'.2f')}",fontsize=9.5,color=OK if clrL>=0.2 else BAD,fontweight="bold")
    ax.text(17.5,RL+5.3,f"inner {inner}: margin {'clear by '+format(clrR,'.2f') if clrR>=0 else 'cut by '+format(-clrR,'.2f')}",fontsize=9.5,ha="right",color=OK if clrR>=0.2 else BAD,fontweight="bold")
    # the corner post, drawn behind (dashed) at its x
    ax.add_patch(mp.Rectangle((postx,RL),15,6,fc="none",ec="#555",ls="--",lw=1))
    ax.text(postx+7.5,RL+6.6 if False else RL+7.2,f"corner post x {postx}-{postx+15} (behind)",ha="center",fontsize=9,color="#555")
    if postx>0 and postx<outer: ax.annotate("post stands on the chamfer:\n0.8 ledge sliver",xy=(postx,RL-postx),xytext=(-1,RL-6),fontsize=9,color=BAD,arrowprops=dict(arrowstyle="-",color=BAD))
    ax.text(19.5,FL/2,"channel\nfloor 6.6",fontsize=9,ha="center",va="center")
    ax.set_xlim(-2,23); ax.set_ylim(-1.5,RL+9); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title,fontsize=12,fontweight="bold",color=good)
def post_plan(ax,r,title,good):
    g=sbox(0,0,15,16).buffer(-r,join_style=1).buffer(r,join_style=1); fill(ax,g,MIDC)
    fill(ax,sbox(1.9,1.9,13.1,13.1),BLK,lw=0)
    band=unary_union([sbox(0.04,1.9,1.9,13.1),sbox(1.9,0.04,13.1,1.9),sbox(13.1,1.9,14.96,13.1)])
    cut=band.difference(g).area
    fill(ax,band,MAR,ec="#3182bd",lw=0.5)
    ax.text(7.5,-2.2,f"r{r}: white margin cut {cut:.2f} mm²",ha="center",fontsize=10,fontweight="bold",color=OK if cut<0.01 else BAD)
    ax.text(7.5,17,"column face (y BD-21)",ha="center",fontsize=8.5,color="#555"); ax.text(7.5,-0.9,"front",ha="center",fontsize=8,color="#555")
    ax.set_xlim(-1.5,16.5); ax.set_ylim(-3.2,18); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title,fontsize=12,fontweight="bold",color=good)
def wall(ax,outc,inc,title,good):
    g=unary_union([sbox(-6,0,0,3),sbox(-1.86,3,0,18)])        # front wall (outside at x 0), floor under the pocket
    g=cham(g,(0,18),outc,-1,-1); g=cham(g,(0,0),outc,-1,1)
    if inc: g=cham(g,(-1.86,18),inc,1,-1)
    fill(ax,g,MIDC); top=1.86-outc-inc
    ax.text(-0.93,19.0,f"wall top {top:.2f} wide",ha="center",fontsize=10,fontweight="bold",color=OK if top>=0.6 else BAD)
    ax.text(-4,10,"phone\npocket",ha="center",fontsize=9); ax.text(1.2,10,"outside\n(front face)",fontsize=9)
    ax.set_xlim(-6.5,5); ax.set_ylim(-1,20.5); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title,fontsize=12,fontweight="bold",color=good)
def chan(ax,r,title,good):
    ch=sbox(-67.5,40,67.5,105); ch=ch.difference(unary_union([sbox(sg*67.5-(r if sg>0 else 0),105-r,sg*67.5+(0 if sg>0 else r),105).difference(Point(sg*(67.5-r),105-r).buffer(r,128)) for sg in (-1,1)]))
    fill(ax,sbox(-85,40,85,132),MIDC); fill(ax,ch,"white")
    for i,(off,col) in enumerate(((0,"#555"),(1.5,"#e6550d"))):
        xc=62+off; a=67.5-r; d=0 if xc<=a else (105-(105-r+(r*r-(xc-a)**2)**0.5))
        fill(ax,sbox(-62+off,40,62+off,105-d),"none",ec=col,lw=1.3)
        ax.text(41,88-8*i,f"124-wide flow-ratio piece,\n{off} mm off center: {d:.2f} off the stop",fontsize=10,color=OK if d<0.05 else BAD,fontweight="bold")
    ax.set_xlim(40,86); ax.set_ylim(70,112); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title,fontsize=12,fontweight="bold",color=good)
def edges(ax,rec):
    f=frame(); fill(ax,f,FRC,lw=0.6)
    tm=sbox(-CUTT,TB0,CUTT,TB1); fill(ax,tm.intersection(sbox(40,TB0,CUTT,TB1)),MIDC,lw=0.6)
    fill(ax,unary_union([sbox(40,0,85,FL),sbox(85,0,CUTB,BH)]),MIDC,lw=0.6)
    loop=f.exterior
    if rec:
        ax.plot(*loop.xy,color=OK,lw=3); ax.plot([40,CUTT],[TB1,TB1],color=OK,lw=3); ax.plot([40,CUTT],[TB0,TB0],color=OK,lw=3)
        ax.text(100,200,"0.9 chamfer + fillet on every face edge, front and back:\none size through both seams (frames, top middle, board ends)",ha="center",fontsize=10,color=OK,fontweight="bold")
    else:
        ax.plot(*loop.xy,color="#3182bd",lw=3)
        ax.plot([40,CUTT],[TB1,TB1],color="#e6550d",lw=3); ax.plot([40,CUTT],[TB0,TB0],color="#e6550d",lw=3)
        ax.plot([CUTT,146],[TB1,TB1],color="#e6550d",lw=3); ax.plot([CUTT,147],[TB0,TB0],color="#e6550d",lw=3)
        for x,z in ((146,TB1),(147,TB0),(CUTB,0),(CUTB,BH)): ax.plot(x,z,"x",color=BAD,ms=12,mew=3)
        ax.text(100,200,"blue 6.0 (change 35), orange 0.9 (change 36);\nred x: size jumps where no rule says how",ha="center",fontsize=10,color=BAD,fontweight="bold")
        ax.text(95,BH+6,"board ends: 2.1 (change 37)\nvs foot 6.0 at x 105",ha="center",fontsize=9,color=BAD)
    ax.text(155,95,"post",rotation=90,fontsize=9,ha="center"); ax.text(80,TB0+9,"top middle",fontsize=9,ha="center")
    ax.set_xlim(38,172); ax.set_ylim(-5,215); ax.set_aspect("equal"); ax.axis("off")
def frameview(ax):
    f=frame(); fill(ax,f,FRC)
    for k in (LOW,HIGH): fill(ax,plc(sbox(-10,-10,10,10),k),"#ccc",ec="#999",lw=0.5)
    ax.add_patch(mp.Circle((146,166),19,fc="none",ec=OK,ls=":",lw=1)); ax.add_patch(mp.Circle((146,166),1,fc="none",ec=OK,lw=1.5))
    ax.plot(146,166,"+",color=OK,ms=10); ax.text(118,190,"top elbow r19 / r1, one center:\nwalls 18 / 18 (change 31 checks out)",fontsize=9.5,color=OK,fontweight="bold")
    ax.plot(146,19,"+",color=OK,ms=10); ax.text(120,-14,"foot corner r19 matches the top (32 ok)",fontsize=9.5,color=OK,fontweight="bold",ha="center")
    ax.annotate("change 32's r1 here doesn't exist:\nthe low clip block fills this corner",xy=(146,24),xytext=(60,60),fontsize=9.5,color=BAD,fontweight="bold",arrowprops=dict(arrowstyle="->",color=BAD))
    ax.annotate("high clip U reaches x 151.8,\npost wall outside it 13.2",xy=(151.8,120),xytext=(168,140),fontsize=9,arrowprops=dict(arrowstyle="-"))
    ax.plot([PX0,PX0],[44,100],color="#3182bd",lw=2); ax.text(144,72,"post 147-165 (18)",rotation=90,fontsize=9,ha="center",color="#3182bd")
    ax.set_xlim(55,200); ax.set_ylim(-20,200); ax.set_aspect("equal"); ax.axis("off")
fig=plt.figure(figsize=(22,30),dpi=75)
fig.suptitle("Calibration stand: recheck of changes 31 to 38 against learnings.building, stand-inputs and photo-board's marker margins\nmm; drawn from recheck31.py (clean7 geometry + changes 31, 32, 41, 49); right frame, front view unless noted",fontsize=17,fontweight="bold",y=0.995)
gs=fig.add_gridspec(5,4,hspace=0.25,wspace=0.08,top=0.955,bottom=0.01,left=0.01,right=0.99)
ax=fig.add_subplot(gs[0,0:2]); frameview(ax); ax.set_title("31, 32: elbows and foot corners",fontsize=13,fontweight="bold")
ax=fig.add_subplot(gs[0,2]); edges(ax,False); ax.set_title("35, 36: edge sizes as agreed",fontsize=13,fontweight="bold",color=BAD)
ax=fig.add_subplot(gs[0,3]); edges(ax,True); ax.set_title("Recommended: 0.9 everywhere",fontsize=13,fontweight="bold",color=OK)
ax=fig.add_subplot(gs[1,0:2]); sec_rail(ax,2.1,1.2,0.8,"33, 37 as agreed: left rail section (outer 2.1, inner 1.2, post at 0.8)",BAD)
ax=fig.add_subplot(gs[1,2:4]); sec_rail(ax,0.9,0.9,0,"Recommended: 0.9 both sides, post flush at x 0",OK)
ax=fig.add_subplot(gs[2,0]); post_plan(ax,4,"37 as agreed: post r4 (plan)",BAD)
ax=fig.add_subplot(gs[2,1]); post_plan(ax,1.5,"Recommended: post r1.5",OK)
ax=fig.add_subplot(gs[2,2]); wall(ax,0.9,0.9,"36 as agreed: 0.9 both wall-top edges",BAD)
ax=fig.add_subplot(gs[2,3]); wall(ax,0.9,0,"Recommended: pocket edge sharp",OK)
ax=fig.add_subplot(gs[3,0:2]); chan(ax,5.8,"37 as agreed: channel back corner r5.8 (plan)",BAD)
ax=fig.add_subplot(gs[3,2:4]); chan(ax,3.0,"Recommended: r3 (as on the rev2 board)",OK)
# 38: ridge in V-slot, section across the ridge (y along the depth, z up), frame side
ax=fig.add_subplot(gs[4,0:2])
fill(ax,sbox(40,0,76.8,8),FRC); fill(ax,SP([(48.9,0),(60.9,0),(54.9,6)]),"white")
fill(ax,SP([(54.9-5.79,0),(54.9+5.79,0),(54.9+0.088,5.7),(54.9-0.088,5.7)]),"#1f5fa8")
ax.text(54.9,-2,"V-slot 12.0 x 6.0 (layers 163-203), ridge base 11.58, top at 5.7: 0.15 glue gap on each slope, 0.3 at the apex",ha="center",fontsize=10)
ax.text(70,6.5,"frame prints with this face vertical: slot roof 45 deg, ridge sits on the middle part's bed",fontsize=9.5,ha="center",color=OK,fontweight="bold")
ax.set_xlim(40,80); ax.set_ylim(-4,9); ax.set_aspect("equal"); ax.axis("off"); ax.set_title("38: stub tenon (ridge) section, checks out",fontsize=13,fontweight="bold",color=OK)
fig.savefig("/mnt/project-files/images/calibrationStand_recheck31-38.png",facecolor="white"); print("saved")

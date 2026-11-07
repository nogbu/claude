# Close-up of the stand clips next to the 3mf clip. Run from this folder: python3 clips7.py
exec(open("clean7.py").read().split('if __name__')[0])
CUT_X=CUT_R; F=side_frame()
fig,axs=plt.subplots(1,3,figsize=(21,8.5),dpi=95)
def draw(ax,g,c="#ddd6c4"):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; ax.fill(x,y,fc=c,ec="k",lw=1)
        for i in p.interiors: xi,yi=i.xy; ax.fill(xi,yi,fc="white",ec="k",lw=1)
def lab(ax,p,off,t): ax.annotate(t,xy=p,xytext=off,textcoords="offset points",fontsize=12,fontweight="bold",color="#1f5fa8",ha="center",arrowprops=dict(arrowstyle="-",color="#1f5fa8"),bbox=dict(fc="white",ec="none",pad=1))
# 1: source
ax=axs[0]; draw(ax,SNAP,"#e6e1d3"); draw(ax,CLIP.difference(SNAP),"#f3f3f3"); ax.add_patch(plt.Rectangle((-10,-10),20,20,fc="#8a8a90",alpha=.5,ec="k"))
lab(ax,(-10,12.5),(-70,40),"hinge slot 1.0 wide"); lab(ax,(-10.9,16.2),(-90,10),"bridge 2.48"); lab(ax,(-14.5,-13.5),(-40,-40),"pull tab 45°")
lab(ax,(9.6,6.3),(60,-20),"snap bumps"); lab(ax,(-11.4,0),(-70,0),"free wall"); lab(ax,(11.4,-4),(60,-40),"fixed hook")
ax.set_title("barrinaClip_rev2.3mf, mesh section\n(shaded: the snap U used; pale: shelf parts left out)",fontsize=13,fontweight="bold",pad=20)
# 2/3: stand clips, U drawn over the frame to show it's unchanged
for ax,k,nm,xl,zl in ((axs[1],HIGH,"High clip",(HX-26,PX1+3),(HZ-28,HZ+32)),(axs[2],LOW,"Low clip",(LX-24,PX1+3),(BH-8,LZ+26))):
    draw(ax,F.difference(plc(SNAP,k)),"#cfc8b4"); draw(ax,plc(SNAP,k),"#e6e1d3")
    b=plc(sbox(-10,-10,10,10),k); x,y=b.exterior.xy; ax.fill(x,y,fc="#8a8a90",alpha=.5,ec="k")
    sl=plc(SLOT,k).centroid; lab(ax,(sl.x,sl.y),(-80,60) if k is HIGH else (-60,60),"hinge slot (as 3mf)")
    t=plc(Point(-14.5,-13.5),k); lab(ax,(t.x,t.y),(-40,-50) if k is HIGH else (-50,30),"pull tab")
    blk=F.difference(plc(SNAP,k)).intersection(sbox(*xl[:1],zl[0],PX0,zl[1])).representative_point() if False else None
    ax.set_xlim(*xl); ax.set_ylim(*zl); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{nm} on the side frame\nlight: the 3mf U, unchanged\ndarker: new block (meets only the U's back and fixed wall)",fontsize=13,fontweight="bold")
axs[0].set_aspect("equal"); axs[0].axis("off")
fig.tight_layout(); fig.savefig("/mnt/project-files/images/calibrationStand_clips7.png",facecolor="white"); print("saved")

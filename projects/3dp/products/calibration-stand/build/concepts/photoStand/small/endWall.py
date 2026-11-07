exec(open("render8.py").read().split("def draw")[0])
Y0,Y1=CRAD.bounds[1],CRAD.bounds[3]; FRC="#e8e2d0"; MIDC="#cfc8b4"; TEN="#1f5fa8"; PIN=147
def fill(ax,g,fc,lw=0.8):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; ax.fill(x,y,fc=fc,ec="k",lw=lw)
fig,axs=plt.subplots(1,3,figsize=(21,8),dpi=80)
fig.suptitle("End wall between the phone pocket and each top cut (whole 0.62 beads); right cut shown, top view; ridge 6.0 tall x 12 x 8 (agreed)",fontsize=15,fontweight="bold")
for ax,(n,w) in zip(axs,((4,2.48),(5,3.10),(6,3.72))):
    pe=POCKET.bounds[2]; cut=pe+w; lcut=POCKET.bounds[0]-w; xl=pe-14
    mid=unary_union([CRAD,sbox(CRAD.bounds[0],Y0,cut,Y1)]).intersection(sbox(xl,Y0,cut,Y1))
    fill(ax,mid,MIDC); fill(ax,sbox(cut,Y0,PX1,Y1),FRC); fill(ax,POCKET.intersection(sbox(xl,Y0,cut,Y1)),"white")
    yc=Y1-22; fill(ax,sbox(cut,yc-6,cut+8,yc+6),TEN)
    ax.plot([cut,cut],[Y0-3,Y1+3],color="#c0392b",ls="--",lw=1.5); ax.plot([PIN,PIN],[Y0,Y1],"k:",lw=1)
    ax.text(cut,Y0-7,f"cut x {cut:.2f}",color="#c0392b",ha="center",fontsize=12,fontweight="bold")
    ax.text(pe-7,(Y0+Y1)/2,"phone\npocket",ha="center",va="center",fontsize=11)
    ax.set_title(f"{n} beads = {w:.2f} wall\ntop middle {cut-lcut:.2f} long (left cut x {lcut:.2f})",fontsize=13,fontweight="bold")
    ax.set_xlim(xl,PX1+3); ax.set_ylim(Y0-10,Y1+4); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(rect=(0,0,1,0.92)); fig.savefig("/mnt/project-files/images/calibrationStand_endWall.png",facecolor="white"); print("ok")

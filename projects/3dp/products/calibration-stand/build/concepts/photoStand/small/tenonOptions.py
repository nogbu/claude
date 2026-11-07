# Concept: which part carries the stub tenons (change 38). Placeholder sizes. Run from the small/ folder.
exec(open("render8.py").read().split("def draw")[0])
import matplotlib.patches as mp
from shapely.geometry import Polygon as SP
Y0,Y1=CRAD.bounds[1],CRAD.bounds[3]           # frame depth after change 30 (cradle depth)
PIN=147                                        # post inner face after change 31
WALLE=3.0; TL=8.0; MD=8.5                      # placeholders: end wall, tenon length, mortise depth
def fill(ax,g,fc,ec="k",lw=0.8,hatch=None,alpha=1):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; ax.fill(x,y,fc=fc,ec=ec,lw=lw,hatch=hatch,alpha=alpha)
        for i in p.interiors: xi,yi=i.xy; ax.fill(xi,yi,fc="white",ec=ec,lw=lw)
FRC="#e8e2d0"; MIDC="#cfc8b4"; TEN="#1f5fa8"; BAD="#c0392b"
fig,axs=plt.subplots(2,3,figsize=(22,13),dpi=80,gridspec_kw=dict(width_ratios=[1.25,1.35,1.25]))
fig.suptitle("Stub tenons (change 38): which part carries them?   mm; concept, sizes are placeholders; fillets not drawn",fontsize=17,fontweight="bold")
yc=(Y0+Y1)/2
# ---------- option A: diamond tenon on the frames, centered ----------
dA=10
diaA=SP([(yc,TB0+9-dA/2),(yc+dA/2,TB0+9),(yc,TB0+9+dA/2),(yc-dA/2,TB0+9)])
ax=axs[0,0]; fill(ax,sbox(Y0,TB0,Y1,TB1),MIDC); fill(ax,diaA,TEN)
ax.plot([yc],[TB0+9-dA/2],"o",ms=12,mfc="none",mec=BAD,mew=2.5)
ax.annotate("first layer of the tenon: an 8 mm strand\nover air, held only at the frame (breaks dp 4)",xy=(yc,TB0+9-dA/2),xytext=(yc-2,TB0-12),ha="center",fontsize=11,color=BAD,fontweight="bold",arrowprops=dict(arrowstyle="-",color=BAD))
ax.annotate("",xy=(Y0+8,TB1+6),xytext=(Y0-2,TB1+6),arrowprops=dict(arrowstyle="-|>",color="k",lw=2)); ax.text(Y0+10,TB1+6,"frame's up as printed (front face down)",va="center",fontsize=10)
ax.set_title("A. Diamond tenon on the frames (doc's proposal)\njoint face at a top cut, looking along the bar",fontsize=13,fontweight="bold")
# ---------- option B: 45 deg ridge on the middle parts, on their bed face, offset to the back ----------
aB=6; ycB=Y1-22
ridgeB=SP([(ycB-aB,TB0),(ycB+aB,TB0),(ycB,TB0+aB)])
ax=axs[1,0]; fill(ax,sbox(Y0,TB0,Y1,TB1),FRC); fill(ax,ridgeB,TEN)
ax.text(ycB,TB0-4,"ridge sits on the bed: no overhang",ha="center",fontsize=11,color=TEN,fontweight="bold")
ax.text(yc-14,TB0+12,"V-slot in the frame, open at the bar's\nunderside; its roof is 45 deg as the frame prints",ha="center",fontsize=10.5)
ax.annotate("",xy=(Y0+3,TB1+8),xytext=(Y0+3,TB1+1),arrowprops=dict(arrowstyle="-|>",color="k",lw=2)); ax.text(Y0+6,TB1+5,"middle part's up as printed (flat)",va="center",fontsize=10)
ax.text(ycB,TB1+5,"offset to the back: the middle part\ncan't go in turned around (dp 10)",ha="center",fontsize=10.5,color=TEN)
ax.set_title("B. 45 deg ridge on the middle parts\njoint face at a top cut, looking along the bar",fontsize=13,fontweight="bold")
for ax in axs[:,0]:
    ax.set_xlim(Y0-6,Y1+6); ax.set_ylim(TB0-18,TB1+12); ax.set_aspect("equal"); ax.axis("off")
    ax.text(Y0,TB0-16,"front",fontsize=10); ax.text(Y1,TB0-16,"back",fontsize=10,ha="right")
# ---------- top views at the right top cut ----------
for r,(nm,cut) in enumerate((("A",POCKET.bounds[2]+WALLE+MD),("B",POCKET.bounds[2]+WALLE))):
    ax=axs[r,1]; xl,xr=POCKET.bounds[2]-20,PX1+4
    mid=unary_union([CRAD,sbox(CRAD.bounds[0],Y0,cut,Y1)]).intersection(sbox(xl,Y0-1,cut,Y1+1))
    fr=sbox(cut,Y0,PX1,Y1)
    fill(ax,mid,MIDC); fill(ax,fr,FRC); fill(ax,POCKET.intersection(sbox(xl,Y0,cut,Y1)),"white")
    ax.plot([PIN,PIN],[Y0,Y1],"k:",lw=1); ax.text(PIN+1,Y1+2,"post inner face 147",fontsize=9.5)
    if nm=="A":
        t=sbox(cut-MD,yc-dA/2,cut,yc+dA/2); fill(ax,t,TEN); ax.text(cut-MD/2,yc+dA/2+2,f"mortise {MD} deep\n+ {WALLE:.0f} wall",ha="center",fontsize=9.5)
    else:
        t=sbox(cut,ycB-aB,cut+TL,ycB+aB); fill(ax,t,TEN); ax.text(cut+TL/2,ycB+aB+2,f"ridge {TL:.0f} long\ninto the frame",ha="center",fontsize=9.5)
    ax.plot([cut,cut],[Y0-4,Y1+4],color=BAD,lw=1.6,ls="--"); ax.text(cut,Y0-8,f"cut x {cut:.1f}",color=BAD,ha="center",fontsize=11,fontweight="bold")
    ax.text(POCKET.bounds[2]-10,yc,"phone\npocket",ha="center",va="center",fontsize=10)
    ax.text((cut+PX1)/2+3,Y0+6,"side frame",ha="center",fontsize=10); ax.text(POCKET.bounds[2]-12,Y0+4,"top middle",ha="center",fontsize=10)
    L=2*cut if False else None
    lcut=-(abs(POCKET.bounds[0])+(cut-POCKET.bounds[2]))
    ax.set_title(f"{nm}: right top cut, top view (top middle {cut-lcut:.1f} long, left cut x {lcut:.1f})",fontsize=12,fontweight="bold")
    ax.set_xlim(xl,xr); ax.set_ylim(Y0-12,Y1+8); ax.set_aspect("equal"); ax.axis("off")
# ---------- base joint face at x 85: board edge (rail, 8.7) against the 18 mm foot ----------
for r,nm in enumerate("AB"):
    ax=axs[r,2]; fill(ax,sbox(Y0,0,Y1,BH),FRC,lw=0.6); fill(ax,sbox(Y0,0,Y1,RL),MIDC,lw=0.8)
    ax.text(yc,RL+(BH-RL)/2,"foot above the rail (step open: Depth follow-ups)",ha="center",va="center",fontsize=9.5)
    if nm=="A":
        d=5; g=SP([(yc,RL/2-d/2),(yc+d/2,RL/2),(yc,RL/2+d/2),(yc-d/2,RL/2)]); fill(ax,g,TEN)
        ax.text(yc,-4.5,"5 mm diamond fits the 8.7 rail with 1.85 above and below;\nsame strand over air at its lowest point",ha="center",fontsize=10,color=BAD)
    else:
        a=5; g=SP([(ycB-a,0),(ycB+a,0),(ycB,a)]); fill(ax,g,TEN)
        ax.text(yc,-4.5,"ridge on the board's bed face; its V-slot in the foot\nopens on the foot's underside, hidden on the desk",ha="center",fontsize=10,color=TEN)
    ax.set_xlim(Y0-6,Y1+6); ax.set_ylim(-10,BH+6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{nm}: base joint face at x 85 (board edge vs foot)",fontsize=12,fontweight="bold")
fig.text(0.5,0.01,"Blue: tenon or ridge (placeholder sizes). Light: side frame; darker: middle part. Both options glue flat shoulders; strength didn't decide change 38.",ha="center",fontsize=12)
fig.tight_layout(rect=(0,0.03,1,0.95))
fig.savefig("/mnt/project-files/images/calibrationStand_tenonOptions.png",facecolor="white"); print("saved")

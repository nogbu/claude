# Base cut options at the 76.8 frame depth (change 48), ridge joints (changes 39-47). Front view of the right base, plus the glue face.
# Run from this folder. Concept: fillets other than the foot's r19 / r1 not drawn.
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.geometry import Polygon as SP, Point, box as sbox
from shapely.ops import unary_union
BW,BD=170,132; HB=BW/2; FL=6.6; RL=FL+2.1; BH=18; PX0,PX1=147,165; DEPTH=76.8
FRC="#e8e2d0"; MIDC="#cfc8b4"; TEN="#1f5fa8"; BAD="#c0392b"
M=30*185/2                                     # half the 30 N side push at the top (z 185), per base joint (inference)
def sig(h): return M/(DEPTH*h*h/6)
def foot(x0):
    s=unary_union([sbox(x0,0,PX1,BH),sbox(PX0,BH-1,PX1,60)])
    cor=sbox(PX1-19,0,PX1,19).difference(Point(PX1-19,19).buffer(19,128)); s=s.difference(cor)        # r19 outer bottom corner
    s=unary_union([s,sbox(PX0-1,BH,PX0,BH+1).difference(Point(PX0-1,BH+1).buffer(1,32))])              # r1 inside corner
    return s
def fill(ax,g,fc,ec="k",lw=0.9):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; ax.fill(x,y,fc=fc,ec=ec,lw=lw)
fig,axs=plt.subplots(2,2,figsize=(20,11),dpi=80,gridspec_kw=dict(width_ratios=[1.7,1]))
fig.suptitle("Base cut options at the 76.8 frame depth (right side; mirrored on the left)   mm; concept; front view at the lens",fontsize=16,fontweight="bold")
for r,(nm,cut) in enumerate((("A. Cut at the board's edge (x 85)",HB),("B. Cut moved out to x 105: board part's ends stand 18 tall",HB+20))):
    ax=axs[r,0]
    board=unary_union([sbox(40,0,HB,FL),sbox(HB-17.5,FL,HB,RL)])
    if cut>HB: board=unary_union([board,sbox(HB,0,cut,BH)])
    fill(ax,board,MIDC); fill(ax,foot(cut),FRC)
    ax.plot([cut,cut],[-3,BH+3],color=BAD,lw=2,ls="--"); ax.text(cut,-6,f"glue face x {cut:.0f}: {RL if cut==HB else BH} tall",color=BAD,ha="center",fontsize=12,fontweight="bold")
    ax.annotate("step 9.3 above the rail\n(kept, change 29; chamfer not sized)",xy=(HB,(RL+BH)/2),xytext=(HB-32,BH+12),fontsize=11,ha="center",arrowprops=dict(arrowstyle="-",color="k"))
    ax.text(HB-8.75,RL+1.5,"rail 8.7",ha="center",fontsize=10); ax.text(60,FL/2,"board floor 6.6",ha="center",va="center",fontsize=10)
    ax.text((PX0+PX1)/2,40,"post",ha="center",fontsize=10,rotation=90); ax.text(max(cut,HB)+(PX0-max(cut,HB))/2,BH/2,"foot (side frame)",ha="center",va="center",fontsize=11)
    if cut>HB: ax.text((HB+cut)/2,BH/2,"board part\n20 x 18",ha="center",va="center",fontsize=10.5)
    ax.text(40,BH+20,f"{nm}\nboard part {2*cut:.0f} wide",fontsize=13,fontweight="bold",va="top")
    ax.set_xlim(38,172); ax.set_ylim(-10,BH+22); ax.set_aspect("equal"); ax.axis("off")
    # glue face, seen from the side (y along the depth)
    ax=axs[r,1]; h=RL if cut==HB else BH; y0=0
    fill(ax,sbox(0,0,DEPTH,h),MIDC); yc=DEPTH-22
    fill(ax,SP([(yc-6,0),(yc+6,0),(yc,6)]),TEN)
    ax.text(DEPTH/2,h+3,f"glue face {DEPTH} x {h} = {DEPTH*h:.0f} mm²",ha="center",fontsize=12,fontweight="bold")
    ax.text(yc,-4,"ridge 12 x 6, 22 from the back",ha="center",fontsize=10,color=TEN)
    ax.text(DEPTH/2,-11,f"bending stress about {sig(h):.1f} MPa (inference)",ha="center",fontsize=12,color=BAD if h<10 else "#1e7d32",fontweight="bold")
    ax.text(0,-16,"front",fontsize=9); ax.text(DEPTH,-16,"back",fontsize=9,ha="right")
    ax.set_xlim(-4,DEPTH+4); ax.set_ylim(-18,24); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.5,0.01,f"Stress model (inference): each base joint takes half the 30 N side push at the top (z 185) as bending across its face, {M:.0f} N·mm; the 60 N down goes through the feet to the desk.",ha="center",fontsize=11.5)
fig.tight_layout(rect=(0,0.03,1,0.95)); fig.savefig("/mnt/project-files/images/calibrationStand_baseCut.png",facecolor="white"); print("saved",round(sig(RL),2),round(sig(BH),2))

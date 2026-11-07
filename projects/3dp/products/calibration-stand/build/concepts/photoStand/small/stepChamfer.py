# Step chamfer (dp 3) on the board part's 18-tall end at x 85 (changes 29, 49): 3.0 vs 3.3. Front view, right side. Run from this folder.
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.geometry import Polygon as SP, box as sbox
from shapely.ops import unary_union
HB=85; FL=6.6; RL=8.7; BH=18; CUT=105
fig,axs=plt.subplots(1,2,figsize=(16,6),dpi=80)
fig.suptitle("Step chamfer on the board part's end (x 85), 45 deg, top edge; front view, right side; mm; concept, chamfer-corner fillets not drawn",fontsize=13,fontweight="bold")
for ax,c in zip(axs,(3.0,3.3)):
    g=unary_union([sbox(55,0,HB,FL),sbox(HB-17.5,FL,HB,RL),sbox(HB,0,CUT,BH)]).difference(SP([(HB-1,BH+1),(HB+c+1,BH+1),(HB-1,BH-c-1)]).intersection(sbox(HB,BH-c,HB+c,BH+1)))
    g=g.difference(SP([(HB,BH-c),(HB,BH+1),(HB+c+1,BH+1),(HB+c,BH)]))
    x,y=g.exterior.xy; ax.fill(x,y,fc="#cfc8b4",ec="k",lw=1); ax.fill([CUT,125,125,CUT],[0,0,BH,BH],fc="#e8e2d0",ec="k",lw=1)
    ax.plot([CUT,CUT],[-2,BH+2],color="#c0392b",ls="--",lw=1.5); ax.text(CUT,-4,"glue cut x 105",color="#c0392b",ha="center",fontsize=10)
    ax.annotate(f"{c} x 45 deg ({round(c/0.3)} layers)",xy=(HB+c/2,BH-c/2),xytext=(HB-18,BH+4),fontsize=12,fontweight="bold",arrowprops=dict(arrowstyle="-"))
    ax.text(HB-8.75,RL+1,"rail 8.7",ha="center",fontsize=10); ax.text(95,BH/2,"board part",ha="center",fontsize=10); ax.text(115,BH/2,"foot",ha="center",fontsize=10)
    ax.text(HB+1,RL+(BH-RL-c)/2,f"{BH-RL-c:.1f}\nflat",fontsize=9.5,va="center")
    ax.set_xlim(55,126); ax.set_ylim(-6,BH+8); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"{c}" + ("  (nearest to a third of the 9.3 step)" if c==3.0 else ""),fontsize=12)
fig.tight_layout(rect=(0,0,1,0.93)); fig.savefig("/mnt/project-files/images/calibrationStand_stepChamfer.png",facecolor="white"); print("saved")

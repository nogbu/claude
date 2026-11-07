import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.geometry import Polygon as SP, box
FRC="#e8e2d0"; MIDC="#cfc8b4"; TEN="#1f5fa8"; G=0.15; s2=np.sqrt(2)
def fill(ax,g,fc,ec="k",lw=0.8):
    for p in getattr(g,"geoms",[g]):
        x,y=p.exterior.xy; ax.fill(x,y,fc=fc,ec=ec,lw=lw)
fig,axs=plt.subplots(1,2,figsize=(20,8.5),dpi=80)
fig.suptitle("Ridge glue fit (proposal): close-up, mm, gaps drawn to scale",fontsize=15,fontweight="bold")
# section: looking along the bar (Y across, Z up)
ax=axs[0]
slot=SP([(-6,0),(6,0),(0,6)]); hw=6-G*s2; top=5.7
ridge=SP([(-hw,0),(hw,0),(hw-top,top),(-hw+top,top)])
fill(ax,box(-12,0,12,10),FRC); fill(ax,slot,"white"); fill(ax,ridge,TEN)
ax.plot([-12,12],[0,0],"k",lw=1.5)
ax.annotate("V-slot in the frame: 12.0 wide (40 layers as the frame prints), 6.0 tall",xy=(3,3),xytext=(5,8.6),fontsize=11,arrowprops=dict(arrowstyle="-"))
ax.annotate(f"ridge: sides offset 0.15 square to each face,\nbase {2*hw:.2f} wide, flat top at 5.7 (19 layers)",xy=(-2,4),xytext=(-11.5,8.3),fontsize=11,color=TEN,arrowprops=dict(arrowstyle="-",color=TEN))
ax.annotate("0.3 at the apex",xy=(0,5.85),xytext=(4,6.6),fontsize=10,arrowprops=dict(arrowstyle="-"))
ax.text(0,-1.2,"bar underside / bed face of the middle part",ha="center",fontsize=11)
ax.set_xlim(-12.5,12.5); ax.set_ylim(-2,10.5); ax.set_aspect("equal"); ax.axis("off"); ax.set_title("Section across the ridge (looking along the bar)",fontsize=13,fontweight="bold")
# plan: top view at the right top cut, X along the bar
ax=axs[1]; cut=0; L=8; E=0.5; LI=1.0
fill(ax,box(-6,-10,cut,10),MIDC); fill(ax,box(cut,-10,14,10),FRC)
fill(ax,box(cut,-6,cut+L+E,6),"white")
r=SP([(cut,-hw),(cut+L-LI,-hw),(cut+L,-hw+LI),(cut+L,hw-LI),(cut+L-LI,hw),(cut,hw)]); fill(ax,r,TEN)
ax.plot([cut,cut],[-10.5,10.5],color="#c0392b",ls="--",lw=1.5)
ax.text(cut,-11.6,"shoulders: flat, glued face to face (no gap)",ha="center",fontsize=11,color="#c0392b")
ax.annotate(f"{E} end gap: room for glue pushed ahead,\nand the ridge can't bottom out before the shoulders close",xy=(cut+L+E/2,0),xytext=(9.5,7.5),fontsize=10.5,arrowprops=dict(arrowstyle="-"))
ax.annotate(f"{LI} x 45 deg lead-in on the ridge's tip",xy=(cut+L-LI/2,hw-LI/2),xytext=(-5.5,8.0),fontsize=10.5,color=TEN,arrowprops=dict(arrowstyle="-",color=TEN))
ax.text(-3,0,"top\nmiddle",ha="center",va="center",fontsize=11); ax.text(11.5,-7,"side\nframe",ha="center",fontsize=11)
ax.text(cut+4,-8.3,"slot open underneath:\nglue and air escape there",ha="center",fontsize=10.5)
ax.set_xlim(-6.5,16); ax.set_ylim(-12.5,10.8); ax.set_aspect("equal"); ax.axis("off"); ax.set_title("Top view at a top cut (ridge 8 long, slot 8.5 deep)",fontsize=13,fontweight="bold")
fig.tight_layout(rect=(0,0,1,0.93)); fig.savefig("/mnt/project-files/images/calibrationStand_ridgeGlue.png",facecolor="white"); print("ok",2*hw)

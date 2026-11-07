exec(open("render8.py").read().split("def draw")[0])
from shapely.geometry import Polygon as SP
Y0,Y1=CRAD.bounds[1],CRAD.bounds[3]; FRC="#e8e2d0"; MIDC="#cfc8b4"; TEN="#1f5fa8"
def fill(ax,g,fc,lw=0.8):
    x,y=g.exterior.xy; ax.fill(x,y,fc=fc,ec="k",lw=lw)
opts=[("4.5 tall (15 layers), 9 wide, 6 long",4.5,6),("6.0 tall (20 layers), 12 wide, 8 long",6.0,8),("7.5 tall (25 layers), 15 wide, 10 long",7.5,10)]
fig,axs=plt.subplots(3,2,figsize=(20,12),dpi=80)
fig.suptitle("Ridge size (change 38, ridge on the middle parts): joint faces looking along the bar; mm; glue gaps not drawn",fontsize=16,fontweight="bold")
for r,(nm,a,L) in enumerate(opts):
    yc=Y1-22
    for c,(ztop,lab) in enumerate(((BH,"top cut: bar end, 18 tall"),(RL,"base cut: board edge (8.7 rail) under the 18 foot"))):
        ax=axs[r,c]
        if c==0: fill(ax,sbox(Y0,0,Y1,BH),FRC)
        else: fill(ax,sbox(Y0,0,Y1,BH),FRC,0.5); fill(ax,sbox(Y0,0,Y1,RL),MIDC)
        fill(ax,SP([(yc-a,0),(yc+a,0),(yc,a)]),TEN)
        txt=f"{BH-a:.1f} of bar above the apex" if c==0 else f"apex {RL-a:.1f} below the rail top; slot in the foot leaves {BH-a:.1f}"
        ax.text(Y0+2,BH+2,f"{nm}: {lab}",fontsize=12,fontweight="bold"); ax.text(yc,-3.5,txt,ha="center",fontsize=11)
        ax.set_xlim(Y0-3,Y1+3); ax.set_ylim(-6,BH+5); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(rect=(0,0,1,0.95)); fig.savefig("/mnt/project-files/images/calibrationStand_ridgeSizes.png",facecolor="white"); print("ok")

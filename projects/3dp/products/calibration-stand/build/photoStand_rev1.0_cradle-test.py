"""photoStand rev1.0 cradle test (writes photoStand_rev1.0_cradle-test.pdf, Letter, print at 100%): a paper card the size of the pocket's inside, with the
camera-bar window cut out. Laid on the BACK of the phone (phone face down), so it is drawn
as seen from below: phone top edge at left, button edge at the bottom."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
W,H=215.9,279.4
PL,PW=152.8,72.0; C=0.5              # phone (Listed, Google) and clearance per side
IL,IW=PL+2*C,PW+2*C                  # pocket inside 153.8 x 73.0
BAR0,BAR1,BARW=13.0,35.0,65.0        # camera bar from top edge, and its width (Measured)
LX,LY=26.0,28.0                      # main lens from top edge / from button edge (Measured)
fig=plt.figure(figsize=(W/25.4,H/25.4)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(0,H); ax.axis("off")
x0,y0=(W-IL)/2,150                   # card lower-left; phone edge = card edge + C
k=dict(color="black")
ax.add_patch(Rectangle((x0,y0),IL,IW,fill=False,lw=0.9,**k))
wx0,wx1=x0+C+BAR0-1,x0+C+BAR1+1
wy0=y0+C+(PW-BARW)/2-1; wy1=wy0+BARW+2
ax.add_patch(Rectangle((wx0,wy0),wx1-wx0,wy1-wy0,fill=False,lw=0.9,**k))
lx=x0+C+LX; ly=y0+C+LY               # button edge is at the bottom in this view
for (a,b) in (((lx,wy0),(lx,wy0+4)),((lx,wy1),(lx,wy1-4)),((wx0,ly),(wx0+4,ly)),((wx1,ly),(wx1-4,ly))):
    ax.plot([a[0],b[0]],[a[1],b[1]],lw=0.8,**k)
t=dict(fontsize=7.5,ha="center",va="center")
ax.text(x0+IL/2+25,y0+IW/2,"CUT on the solid outline: 153.8 x 73.0 mm\n(Pixel 10 Pro 152.8 x 72.0 mm + 0.5 mm per side)",**t)
ax.text((wx0+wx1)/2,y0+IW+6,"CUT OUT window\n(camera bar + 1 mm)",**t)
ax.text(x0-3,y0+IW/2,"phone's top edge",fontsize=7.5,rotation=90,ha="right",va="center")
ax.text(x0+IL/2,y0-5,"button edge",**t)
ax.text(lx+30,ly-12,"ticks = main lens center\n(26 mm from top, 28 mm from button edge)",fontsize=6.5,ha="left")
sx,sy=20,60
ax.plot([sx,sx+100],[sy,sy],lw=1,**k)
for d in range(0,101,10): ax.plot([sx+d,sx+d],[sy,sy+(4 if d%50==0 else 2)],lw=0.6,**k)
ax.text(sx+50,sy-6,"100 mm",**t)
ax.plot([sx+125,sx+125],[sy,sy+50],lw=1,**k); ax.text(sx+130,sy+25,"50 mm",fontsize=7.5,va="center")
ax.text(W/2,H-15,"photoStand cradle test, rev1.0 (paper)",fontsize=11,ha="center",fontweight="bold")
ax.text(W/2,H-23,"1. Print at Actual size / 100%, then check both scale bars with a ruler.\n"
        "2. Cut out the card on the solid outline, then cut out the window.\n"
        "3. Lay the phone FACE DOWN, top edge to your left. Lay the card on its back, matching edges.\n"
        "Pass: the camera bar comes up through the window without touching it, the main lens sits at the\n"
        "ticks, and the card overhangs the phone by about 0.5 mm on every side.",fontsize=7.5,ha="center",va="top")
fig.savefig("photoStand_rev1.0_cradle-test.pdf"); fig.savefig("photoStand_rev1.0_cradle-test.png",dpi=110)

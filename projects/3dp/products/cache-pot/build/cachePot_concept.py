import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
t=np.tan(np.radians(5.03))
# nursery pot outer profile (3.5in rev10.2), z from pot bottom
wall=lambda z: 45.88-(100.8-z)*t
P0=np.array([30,0]);P1=np.array([35.12,5.12]);C=np.array([37.68,7.68]);P2=np.array([wall(11.31),11.31])
s=np.linspace(0,1,30)[:,None];bez=(1-s)**2*P1+2*(1-s)*s*C+s**2*P2
outer=np.vstack([[0,0],[23.5,0],[23.5,0.72],[25,0.72],[25,0],P0,bez,[wall(100.8),100.8],[48.07,103.09],[48.07,105.12],[wall(105.12)-1.0,105.12]])
inner=[[wall(z)-1.0,z] for z in np.linspace(105.12,11.31,10)]+[[36.0,7.0],[33.0,4.5],[30.5,1.8],[0,1.8]]
pot=np.vstack([outer,inner])
FL,CH=2.0,8.0;Z0=FL+CH;RI=48.4;RO=RI+2.0;TOP=Z0+105.12+3;RH,RC=12.5,20.0
def corner(xw,c,R):
    # 45 deg line z=r-c meets vertical r=xw; fillet radius R tangent to both
    zi=xw-c; tl=R*np.tan(np.radians(22.5))
    p1=np.array([xw-tl/np.sqrt(2),zi-tl/np.sqrt(2)]); cen=np.array([xw-R,zi+tl])
    a0=np.arctan2(*(p1-cen)[::-1]); arc=[cen+R*np.array([np.cos(a),np.sin(a)]) for a in np.linspace(a0,0,12)]
    return np.array(arc)
o=corner(RO,RO-10,10); w=2.0; ci=RO-10+w*np.sqrt(2); i=corner(RI,ci,10-w)
cache=np.vstack([[RH,0],[RO-10,0],o,[RO,TOP],[RI,TOP],i[::-1],[FL+ci,FL],[RC,FL],[RC,Z0],[RH,Z0]])
fig,ax=plt.subplots(figsize=(9,10))
for sg in (1,-1):
    ax.add_patch(Polygon(cache*[sg,1],fc="#9aa7b3",ec="#3d4a57",lw=1))
    ax.add_patch(Polygon((pot+[0,Z0])*[sg,1],fc="#d8eef5",ec="#2a7a99",lw=1,alpha=.9))
    ax.add_patch(Polygon(np.array([[RC,FL],[FL+ci,FL],[FL+ci+2.6,FL+2.6],[FL+ci+2.6,FL+2.6],[RC,FL+2.6]])*[sg,1],fc="#4aa3df",alpha=.45,lw=0))
    # water path
    zs=np.linspace(33.48,11.31,12);ax.plot(sg*(wall(zs)+0.8),zs+Z0,color="#1565c0",lw=2)
    b=bez+[0.8,0];ax.plot(sg*b[:,0],b[:,1]+Z0,color="#1565c0",lw=2)
    ax.plot(sg*np.array([35.9,30.8,25,25]),Z0+np.array([5.12,-0.2,-0.2,0.5]),color="#1565c0",lw=2)
    for k in range(3): ax.plot(sg*24.6,Z0-2.2-k*2.0,"o",color="#1565c0",ms=4)
ax.annotate("overflow leaves the slots\n(bottom at 33.48 mm)",(wall(33.48)+1,Z0+33.48),(60,Z0+45),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("drip groove r 23.5–25:\nwater drips off here",(24.6,Z0-1),(55,Z0+20),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("collar, pot rests on it\n(Ø 40 mm, placeholder)",(18,Z0-3),(55,-12),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("drip tray",(35,FL+2),(55,4),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("finger hole Ø 25 mm\n(placeholder)",(0,1),(-15,-15),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("snug at the lip",(48.2,Z0+104),(58,Z0+92),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("rim 3 mm above the lip",(49.4,TOP),(58,TOP+6),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.annotate("10 mm chamfer, then\n10 mm round into the wall",(-(RO-5.5),4.5),(-58,-24),arrowprops=dict(arrowstyle="->"),fontsize=9)
ax.set_xlim(-60,95);ax.set_ylim(-28,TOP+14);ax.set_aspect("equal");ax.axis("off")
ax.set_title("Cache pot concept, section through center (3.5in pot)\nGray: cache pot · light blue: nursery pot · blue: overflow path\nCache sizes are placeholders",fontsize=10)
plt.savefig("cachePot_concept.png",dpi=130,bbox_inches="tight")

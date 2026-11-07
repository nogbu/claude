# Tipping at printed weight (change 28, 2026-10-05). tipping48.py's parts, with each part's weight cut to what the
# process settings print: 2 walls (0.62 lines), 3 top/bottom layers (0.3), 15% sparse infill (process-settings).
# Inference: frames from their section profile (shell + infill); top middle kept solid (thin walls); board at 0.4 of solid.
# Also the turned-down fixes: feet extended back, and 255-deep runners on the board part's end blocks.
# Run from this folder.
exec(open("tipping48.py").read().split("def tip(")[0])
T_SIDE=2*0.62; T_TB=0.9; F=0.15; h=185
ratio={}
for side,cut in ((1,CR),(-1,-CLc)):
    CUT_X=cut; p=side_frame(); a=p.area; V=a*DEP; shell=2*a*T_TB+p.length*DEP*T_SIDE
    ratio[side]=(shell+(V-shell)*F)/V
printed=[]
for m,x,y,n in parts:
    r=ratio[1] if n.startswith("right") else ratio[-1] if n.startswith("left") else 0.4 if n=="board part" else 1
    printed.append((m*r,x,y,n)); print(f"  {n}: {m*r:.0f} g printed (solid {m:.0f})")
def tip(ps,lab,yf=0,yb=132):
    m=sum(p[0] for p in ps); x=sum(p[0]*p[1] for p in ps)/m; y=sum(p[0]*p[2] for p in ps)/m; W=m*g
    print(f"{lab}: {m:.0f} g, tips at the top front to back {W*(yb-y)/h:.1f} N, back to front {W*(y-yf)/h:.1f} N, sideways {W*(146-abs(x))/h:.1f} N")
bars=[(63,s*x,YC,"bar") for s in (1,-1) for x in (HX,LX)]
tip(printed,"no light bars"); tip(printed+bars,"with four 1 ft bars")
d=100; foot=[(d*60*18*RHO*0.35,s*135,112.4+d/2,"foot ext") for s in (1,-1)]
tip(printed+bars+foot,f"turned down: feet extended {d} back",0,112.4+d)
tip(printed+bars,"turned down: runners 255 deep (runner weight left out)",-61.5,193.5)

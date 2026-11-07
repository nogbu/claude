# Tipping at the 76.8 frame depth (changes 30, 31, 32, 41, 48, 49). Solid parts (no infill), so weights are upper bounds.
# Frame profiles from clean7.py's side_frame() at the change 41 top cuts, then adjusted by hand for changes 31, 32 and 49 (inference).
# Run from this folder.
exec(open("clean7.py").read().split('if __name__')[0])
RHO=1.32e-3                      # g/mm3, Bambu PLA Matte (Listed, Orca's "Bambu PLA Matte @base" profile)
DEP=76.8; g=9.81/1000
CR,CLc=130.40,-29.60             # change 41 top cuts
Y0=35.6; YC=Y0+DEP/2             # frame front face and center on the board (board y 0 to 132)
parts=[]                         # (mass g, x, y, name)
for side,cut in ((1,CR),(-1,-CLc)):
    CUT_X=cut; p=side_frame(); a=p.area; cx=p.centroid.x*a
    # change 31: post widened 2 inward (x 147 to 149, z 18 to 167)
    da=2*(TB0-BH); a+=da; cx+=148*da
    # change 49: foot x 85 to 105 moves to the board part
    da=-20*BH; a+=da; cx+=95*da
    # change 32: r19 outer bottom corner replaces the 6 mm chamfer + fillet (net, about)
    da=-(19**2*(1-np.pi/4)-18); a+=da; cx+=160*da
    parts.append((a*DEP*RHO,side*cx/a,YC,f"{'right' if side>0 else 'left'} frame"))
pocket=73.08*153.8-(4-np.pi)*16; camwin=(22+1)*(65+1)
tm=160*DEP*18-pocket*15-camwin*3; parts.append((tm*RHO,(CR+CLc)/2,YC,"top middle"))
bd=[(170*132*6.6,0,66),(2*17.5*132*2.1,0,66),(135*27*2.1,0,132-13.5),(2*15*16*15,0,132-29),(2*15*16*30,0,132-13),(2*20*DEP*18,0,YC)]
v=sum(b[0] for b in bd); parts.append((v*RHO,0,sum(b[0]*b[2] for b in bd)/v,"board part"))
parts.append((207,50.4,YC,"phone (Listed)"))
def tip(ps,lab):
    m=sum(p[0] for p in ps); x=sum(p[0]*p[1] for p in ps)/m; y=sum(p[0]*p[2] for p in ps)/m; W=m*g; h=185
    print(f"{lab}: {m:.0f} g = {W:.1f} N, CG x {x:.1f} y {y:.1f}")
    print(f"  tips at the top pushed front to back {W*(132-y)/h:.1f} N, back to front {W*y/h:.1f} N, sideways {W*(146-abs(x))/h:.1f} N (toward the CG side) / {W*(146+abs(x))/h:.1f} N")
for p in parts: print(f"  {p[3]}: {p[0]:.0f} g")
tip(parts,"no light bars")
tip(parts+[(63,s*x,YC,"bar") for s in (1,-1) for x in (HX,LX)],"with four 1 ft bars at about 63 g each (half the measured 2 ft bar, inference)")

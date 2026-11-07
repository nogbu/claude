# clean8.py: the small calibration stand with every agreed change through 63 (concept geometry and checks; nothing built).
# Run from projects/3dp/products/calibration-stand/build/concepts/photoStand/small: python3 clean8.py
# Reads /mnt/project-files/3mfs/barrinaClip_rev2.3mf through clean7.py's clip code (the snap U is copied unchanged, change 11).
# Coordinates (mm): x from the board's center line (right side; the left is mirrored), z up from the desk,
# y front to back on the board (0 to 132). Profiles: side frames in x-z (extruded in y), flat parts in plan x-y.
import numpy as np
exec(open("clean7.py").read().split("\nif __name__")[0])
from shapely.geometry import MultiPoint, Polygon as SP, LineString, box as sbox, Point
from shapely.ops import unary_union
from shapely import affinity
LAYER,BEAD=0.3,0.62
def bx(x0,x1,y0,y1): return sbox(min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1))
# ---------------- values ----------------
H=170; BH=18; TB0,TB1=H-3,H+15                 # cradle floor top at H (22); bar 18 tall, flush with the cradle walls (17)
PX0,PX1=147,165                                # post 18 wide (31); stand 330 wide
R_EL,R_IN=19,1                                 # outer elbow and foot corners r19, inside elbow r1, one center (31, 32, 53)
CUT_R,CUT_L=130.40,-29.60                      # top cuts (41)
CUT_B=105                                      # base cuts at x +-105 (49)
BW,BD=170,132; HB=BW/2; FL=6.6; RL=8.7; RAILW=17.5; STOP=105
DEP=76.8                                       # frames, top middle and board ends (48)
CY=BD/2
# phone and cradle (21, 26, 27, 41, 48, 58); lens over the board's center
PH_L,PH_W=152.8,72.0; LENS_END,LENS_SIDE=26.0,28.0
PCX=PH_L/2-LENS_END; PCY=PH_W/2-LENS_SIDE      # phone center from the lens
CW=1.86; ENDW=3.10                             # cradle walls 3 beads, end walls 5 beads
PKW=DEP-2*CW                                   # pocket 73.08 wide (48)
PKL=PH_L+1.0                                   # pocket 153.8 long (0.5 per end)
Y0=CY+PCY-DEP/2; Y1=Y0+DEP                     # 35.6 to 112.4 on the board
POCKET=sbox(PCX-PKL/2,CY+PCY-PKW/2,PCX+PKL/2,CY+PCY+PKW/2).buffer(-4,join_style=1).buffer(4,join_style=1)   # r4 corners
CAMWIN=sbox(PCX-PH_L/2+13-0.5,CY+PCY-65/2-0.5,PCX-PH_L/2+13+22+0.5,CY+PCY+65/2+0.5)                          # camera bar 65 x 22 + 0.5
TOPMID=sbox(CUT_L,Y0,CUT_R,Y1)                 # 160.00 x 76.8 block between the cuts (41, 48)
FLOOR_T=3.0                                    # cradle floor z 167 to 170 (27)
LENS_Z=H-4.0; LENS_Z33=H-3.3; D0=LENS_Z-FL     # camera bump 3.3 to 4.0 (sources disagree); worst case 4.0
# ridge joints (39 to 47, 52)
SLOT_W,SLOT_H,SLOT_D=12.0,6.0,8.5
RG_GAP=0.15; RG_B=SLOT_W-2*RG_GAP*np.sqrt(2); RG_TOP=5.7; RG_L=8.0; RG_LEAD=1.0
RG_Y=Y1-21.9                                   # ridge and slot center, 21.9 from the back face (52)
EDGE=0.9                                       # one edge size on every outer face edge, all four parts (54)
STEP_CH=3.0                                    # step chamfer on the board ends' top inner edge (50)
GROOVE=(BD-67,BD-65.5,5.7)                     # brim groove y 65 to 66.5, 5.7 deep (51)
POST_R=1.5; CH_R=3.0; BOARD_R=5.8              # corner posts' vertical edges (57), channel back corners (59), board plan corners (37)
# clip block corners (change 53's note): a third of the thinnest feature meeting at the edge, at least 1 mm (vertical as printed). change 60.
R_LOWPOST=6.0    # low block top meets the post: post 18 is the thinner (block 25.4 tall)
R_HIGHPOST=6.0   # high block top meets the post: post 18 vs block 18.6
R_HIGHTOP=3.7    # high block top meets its 45 deg face (convex): block 11.0 thick under the corner
# (the three above are change 60, the user's yes 2026-10-05)
R_RAILEND=0.9    # change 61: inside edge, rail top (8.7) to the board end's inner face (x 85): 3 layers; margins stop 1.38 short
R_SIDEEND=5.8    # change 62: vertical inside corners, board side (x 85) to the board ends' front and back faces, z 0 to 8.7 (a third of the 17.5 rail)
RAMP=0.64        # change 63: 45 deg ramp on the 0.64 step where the foot top meets the fill under the low clip's fixed wall (dp 3)
# ---------------- side frames (23, 31, 32, 49, 53) ----------------
def round_concave(g,p,r,sx,sz):
    """fill an inside corner at p; (sx,sz) point from p into the open air along the two faces"""
    x,z=p; sq=bx(x,x+sx*r,z,z+sz*r); return unary_union([g,sq.difference(Point(x+sx*r,z+sz*r).buffer(r,256))])
def round_convex(g,p,r):
    loc=Point(p).buffer(4*r,256); part=g.intersection(loc); rd=part.buffer(-r,join_style=1).buffer(r,join_style=1)
    return g.difference(part.difference(rd).intersection(Point(p).buffer(1.1*r,256)))
PIECES={}
def frame_profile(cut):
    """right-side profile; cut is the top cut's distance from the center line (130.40 right, 29.60 left)"""
    lowU,highU=plc(SNAP,LOW),plc(SNAP,HIGH)
    lb=plc(sbox(-U_HALF,10,U_HALF,U_TOP),LOW)
    lowfill=unary_union([sbox(lb.bounds[0],BH,PX0+1,lb.bounds[3]),sbox(LX-10,BH,PX0+1,LZ-U_HALF+0.01)])
    a=P(-U_HALF,U_TOP,**{"ang":-45,"cx":HX,"cz":HZ,"m":True}); b=P(U_HALF,U_TOP,**{"ang":-45,"cx":HX,"cz":HZ,"m":True})
    hb=plc(sbox(-U_HALF,10,U_HALF,U_TOP),HIGH)
    highfill=unary_union([hb,MultiPoint([(a.x,a.y),(b.x,b.y),(PX0+1,b.y),(PX0+1,a.y)]).convex_hull])
    stepx=LX-10; ramp=SP([(stepx-RAMP,BH),(stepx,BH),(stepx,BH+RAMP)])
    s=unary_union([sbox(PX0,BH,PX1,TB0),sbox(CUT_B,0,PX1,BH),sbox(cut,TB0,PX1,TB1),lowfill,highfill,ramp])
    for cz in (TB1-R_EL,R_EL):                                     # r19 outer corners, top and bottom
        q=sbox(PX1-R_EL,cz,PX1,TB1) if cz>100 else sbox(PX1-R_EL,0,PX1,cz)
        s=s.difference(q.difference(Point(PX1-R_EL,cz).buffer(R_EL,256)))
    s=round_concave(s,(PX0,TB0),R_IN,-1,-1)                        # r1 inside elbow, same center as the r19
    zl=lb.bounds[3]; zh=a.y if a.y>b.y else b.y
    s=round_concave(s,(PX0,zl),R_LOWPOST,-1,1)
    s=round_concave(s,(PX0,highfill.bounds[3]),R_HIGHPOST,-1,1)
    top=max(highfill.exterior.coords,key=lambda c:(c[1],-c[0])); s=round_convex(s,(top[0],top[1]),R_HIGHTOP)
    s=s.difference(unary_union([plc(CLIP_ZONE,LOW),plc(CLIP_ZONE,HIGH)]))
    body=unary_union([s,lowU,highU]).buffer(0)
    PIECES[cut]=len(getattr(body,"geoms",[body]))
    if body.geom_type!="Polygon": body=max(body.geoms,key=lambda g:g.area)
    return SP(body.exterior,[i for i in body.interiors if SP(i).area>1.0])
def ridge_section(y0=0.0):
    """ridge cross-section across its length (y, z up from the bed face), centered on y0"""
    hw=RG_B/2; return SP([(y0-hw,0),(y0+hw,0),(y0+hw-RG_TOP,RG_TOP),(y0-hw+RG_TOP,RG_TOP)])
def slot_section(y0=0.0): return SP([(y0-SLOT_W/2,0),(y0+SLOT_W/2,0),(y0,SLOT_H)])
def ridge_plan(xc,sign):
    """ridge footprint at its base, sticking out from the cut at xc in direction sign"""
    hw=RG_B/2; x1=xc+sign*RG_L; xl=x1-sign*RG_LEAD
    return SP([(xc,RG_Y-hw),(xl,RG_Y-hw),(x1,RG_Y-hw+RG_LEAD),(x1,RG_Y+hw-RG_LEAD),(xl,RG_Y+hw),(xc,RG_Y+hw)])
# ---------------- top middle (26, 27, 36, 41, 48, 58) ----------------
def top_layers():
    floor=TOPMID.difference(CAMWIN); walls=TOPMID.difference(POCKET); return floor,walls
# ---------------- board part (2, 5, 6, 33, 49 to 51, 55 to 57, 59) ----------------
def board_plan():
    b=sbox(-HB,0,HB,BD).buffer(-BOARD_R,join_style=1).buffer(BOARD_R,join_style=1)
    return unary_union([b]+[bx(s*HB,s*CUT_B,Y0,Y1) for s in (1,-1)])
def side_end_fillets():
    """change 62: plan fillets, z 0 to 8.7, where the board's sides meet the board ends' front and back faces"""
    out=[]
    for sx in (1,-1):
        for yc,sy in ((Y0,-1),(Y1,1)):
            sq=bx(sx*HB,sx*(HB+R_SIDEEND),yc,yc+sy*R_SIDEEND); out.append(sq.difference(Point(sx*(HB+R_SIDEEND),yc+sy*R_SIDEEND).buffer(R_SIDEEND,128)))
    return unary_union(out)
def channel():
    ch=sbox(-HB+RAILW,-1,HB-RAILW,STOP)
    for s in (1,-1):
        cx=s*(HB-RAILW-CH_R); q=bx(cx,s*(HB-RAILW),STOP-CH_R,STOP)
        ch=ch.difference(q.difference(Point(cx,STOP-CH_R).buffer(CH_R,128)))
    return ch
def posts():
    out=[]
    for s in (1,-1):
        x0,x1=sorted([s*HB,s*(HB-15)])
        out.append(("step",sbox(x0,BD-37,x1,BD-21).buffer(-POST_R,join_style=1).buffer(POST_R,join_style=1),FL+15))
        out.append(("column",sbox(x0,BD-21,x1,BD-5).buffer(-POST_R,join_style=1).buffer(POST_R,join_style=1),FL+30))
    return out
def markers():
    m=[]
    for i in range(3):
        for x in (3.2,BW-14.4): m.append(("rail",sbox(x-HB,10+25*i,x-HB+11.16,21.16+25*i),RL))
    for i in range(5): m.append(("back row",sbox(28+25*i-HB,BD-20,39.16+25*i-HB,BD-8.84),RL))
    for nm,p,z in posts():
        b=p.bounds; y0=b[1]+1.9; x0=b[0]+1.9; m.append((f"{nm} post",sbox(x0,y0,x0+11.16,y0+11.16),z))
    return m
# ---------------- checks ----------------
fails=[]; notes=[]
def chk(n,cnd,i=""):
    print(("PASS " if cnd else "FAIL ")+n+(" "+i if i else ""))
    if not cnd: fails.append(n)
def note(t): print("NOTE "+t); notes.append(t)
def frame_half(z,lz=None): lz=LENS_Z if lz is None else lz; return KL*(lz-z),KS*(lz-z)
if __name__=="__main__":
    print(f"frames y {Y0:.2f} to {Y1:.2f}; pocket {PKL:.2f} x {PKW:.2f}; cuts {CUT_L:.2f} / {CUT_R:.2f}; end walls {POCKET.bounds[0]-CUT_L:.2f} / {CUT_R-POCKET.bounds[2]:.2f}")
    chk("clip profile = 3mf mesh section",MISMATCH<0.01,f"(mismatch {MISMATCH:.3f} mm2)")
    FR={}
    for nm,cut in (("right",CUT_R),("left",-CUT_L)):
        f=frame_profile(cut); FR[nm]=f
        chk(f"{nm} side frame is one solid",PIECES[cut]==1,f"({PIECES[cut]} piece, {f.bounds[2]-f.bounds[0]:.1f} x {f.bounds[3]-f.bounds[1]:.1f})")
        for cn,k in (("low",LOW),("high",HIGH)):
            bar=plc(sbox(-10,-10,10,10),k); ov=bar.intersection(f).area
            chk(f"{nm} {cn} light touches only the snap bumps",ov<8.5,f"({ov:.1f} mm2; two bumps = 8.0)")
            U=plc(SNAP,k); chk(f"{nm} {cn} clip keeps every part of the 3mf snap U",U.difference(f).area<0.05,f"({U.difference(f).area:.2f} mm2 missing)")
            same=plc(CLIP_ZONE,k).intersection(f).symmetric_difference(plc(CLIP_ZONE,k).intersection(U)).area
            chk(f"{nm} {cn} clip zone holds exactly the 3mf U, voids included",same<0.1,f"({same:.2f} mm2 different)")
            chk(f"{nm} {cn} hinge slot open",plc(SLOT,k).intersection(f).area<0.01)
            chk(f"{nm} {cn} free wall swing room clear",plc(FREE_SWING,k).difference(U).intersection(f).area<0.05)
        chk(f"{nm} low fixed wall sits on solid block",sbox(LX-9,BH,LX+9,LZ-U_HALF).difference(f).area<0.01)
        slot_top=sbox(cut,TB0,cut+SLOT_D,TB0+SLOT_H); slot_base=sbox(CUT_B,0,CUT_B+SLOT_D,SLOT_H)
        chk(f"{nm} V-slots sit inside solid frame (top and base)",slot_top.difference(f).area<1e-6 and slot_base.difference(f).area<1e-6)
        sides=[f.boundary.intersection(LineString([(cut,TB0+0.01),(cut,TB1-0.01)])).length,f.boundary.intersection(LineString([(CUT_B,0.01),(CUT_B,BH-0.01)])).length]
        chk(f"{nm} shoulder faces full height at both cuts (18 x 76.8)",abs(sides[0]-18+0.02)<0.05 and abs(sides[1]-18+0.02)<0.05,f"({sides[0]+0.02:.2f}, {sides[1]+0.02:.2f})")
    f=FR["right"]
    hbar=plc(sbox(-10,-10,10,10),HIGH); chk("high light clears the top bar",hbar.distance(sbox(-PX1,TB0,PX1,TB1))>5,f"({hbar.distance(sbox(-PX1,TB0,PX1,TB1)):.1f})")
    # --- camera: lens height, things in view
    chk("lens below the cradle floor's underside, so the camera window's walls can't show",max(LENS_Z,LENS_Z33)<TB0,f"(lens z {LENS_Z:.1f} to {LENS_Z33:.1f}, floor underside {TB0})")
    print(f"INFO lens {D0:.1f} above the board floor (bump 4.0) to {LENS_Z33-FL:.1f} (bump 3.3)")
    worst=99
    for g in (f,plc(sbox(-10,-10,10,10),LOW),hbar):
        for x,z in np.array(g.exterior.coords):
            if BH+0.01<z<LENS_Z-0.01: worst=min(worst,x-frame_half(z)[0])
    chk("clips, posts and lights out of the photo (long side across)",worst>0,f"(closest {worst:.1f} outside)")
    note(f"board part ends and feet show at the photo's side edges (change 24): x 85 to {frame_half(BH)[0]:.1f} at their 18 mm tops, out to {frame_half(0)[0]:.1f} at the desk")
    # markers (with their one-cell margin) and test pieces in frame (audit170's list)
    bad=[]
    for nm,m,z in markers():
        hx,hy=frame_half(z); fr=sbox(-hx,CY-hy,hx,CY+hy)
        if not fr.contains(m.buffer(1.86,join_style=2)): bad.append(nm)
    chk("all 15 markers and their white margins in frame",not bad and len(markers())==15,f"({len(markers())} markers; out: {bad})")
    ch=channel()
    pieces=[("temperature",44.5,50,10),("MVS comb 50%",90,65,50),("PA pattern",98.8,55.4,1.2),("flow ratio YOLO",123,94,2),("retraction tower",40,80,15)]
    for nm,w,dep,z in pieces:
        p=sbox(-w/2,STOP-dep,w/2,STOP); hx,hy=frame_half(FL+z); fr=sbox(-hx,CY-hy,hx,CY+hy)
        mar=min(p.bounds[0]-fr.bounds[0],fr.bounds[2]-p.bounds[2],p.bounds[1]-fr.bounds[1],fr.bounds[3]-p.bounds[3])
        chk(f"test piece in channel and in frame: {nm}",ch.contains(p) and fr.contains(p),f"(margin {mar:.1f}; {8160/(2*hx):.0f} px/mm)")
    # --- glare rule on every lit-face point, 3 mm margin (a = channel half-width 67.5)
    def lit(k): return [np.array(p) for p in plc(sbox(-7,-10.0,7,-10.0+0.01),k).exterior.coords]
    g=min(p[0]-(67.5*(1+(p[1]-FL)/D0)+3) for k in (LOW,HIGH) for p in lit(k))
    chk("glare rule, every lit-face point, 3 mm margin",g>0,f"(margin {g:.1f})")
    # --- marker margins vs edges (33, 54 to 57, 59)
    mk=markers(); marg=[m.buffer(1.86,join_style=2) for _,m,_ in mk]
    def clr(geom): return min(g.distance(geom) for g in marg)
    rails=[sbox(-HB,0,-HB+RAILW,BD),sbox(HB-RAILW,0,HB,BD)]
    rmg=[g for g,(n,_,_) in zip(marg,mk) if n=='rail']; out_ch=min(min(g.bounds[0]+HB for g in rmg),min(HB-g.bounds[2] for g in rmg))-EDGE
    in_ch=min(min((HB-RAILW)-g.bounds[2] for g,(n,_,_) in zip(marg,mk) if n=="rail" and g.bounds[0]<0),min(g.bounds[0]-(-HB+RAILW) for g,(n,_,_) in zip(marg,mk) if n=="rail" and g.bounds[0]>0))
    print(f"INFO rail markers' margins: outer 0.9 chamfer clear by {out_ch:.2f}")
    lm=[g for g,(n,_,_) in zip(marg,mk) if n=="rail"]
    cl_l=min(-HB+RAILW-EDGE-g.bounds[2] for g in lm if g.bounds[0]<0); cl_r=min(g.bounds[0]-(HB-RAILW+EDGE) for g in lm if g.bounds[0]>0)
    chk("rail inner 0.9 chamfer clear of the marker margins",min(cl_l,cl_r)>0,f"(left {cl_l:.2f}, right {cl_r:.2f})")
    chk("rail outer 0.9 chamfer clear of the marker margins",out_ch>0,f"({out_ch:.2f})")
    br=[g for g,(n,_,_) in zip(marg,mk) if n=="back row"]
    chk("stop's 0.9 chamfer and the back edge clear of the back-row margins",min(g.bounds[1] for g in br)-(STOP+EDGE)>0 and BD-EDGE-max(g.bounds[3] for g in br)>0,
        f"({min(g.bounds[1] for g in br)-(STOP+EDGE):.2f} / {BD-EDGE-max(g.bounds[3] for g in br):.2f})")
    def sides(m):
        b=m.bounds; return unary_union([bx(b[0]-1.86,b[0],b[1],b[3]),bx(b[2],b[2]+1.86,b[1],b[3]),bx(b[0],b[2],b[1]-1.86,b[1]),bx(b[0],b[2],b[3],b[3]+1.86)])
    pmk=[m for n,m,_ in mk if "post" in n]; pp=[p for _,p,_ in posts()]
    cut=[sides(m).difference(p).area for m,p in zip(pmk,pp)]
    chk("post r1.5 corners leave the post markers' margin sides whole",max(cut)<1e-6,f"({max(cut):.3f} mm2 cut; margin corners: {max(m.buffer(1.86,join_style=2).difference(p).area for m,p in zip(pmk,pp)):.2f} mm2, as on the rev2 board)")
    # end block's step chamfer (50) and the inside edge at its foot (rail top meets the end face)
    rm=min(HB-g.bounds[2] for g in lm if g.bounds[0]>0)
    print(f"INFO rail markers' margins stop {rm:.2f} short of the board end's inner face (x 85)")
    chk("change 61: r0.9 rail/end fillet clear of the rail markers' margins",rm-R_RAILEND>0,f"({rm-R_RAILEND:.2f}); 3 layers on the grid: {abs(R_RAILEND/LAYER-round(R_RAILEND/LAYER))<1e-9}")
    sef=side_end_fillets()
    chk("change 62: side/end fillets outside the frames' footprint and the marker margins",all(sef.intersection(bx(s*CUT_B,s*PX1,Y0,Y1)).area<1e-6 for s in (1,-1)) and min(g.distance(sef) for g in marg)>0,f"({sef.area/4:.2f} mm2 each)")
    for nm in ("right","left"):
        chk(f"change 63: {nm} frame's 0.64 step at x {LX-10:.0f} is a 45 deg ramp, clip zone unchanged",FR[nm].contains(Point(LX-10-0.2,BH+0.1)))
    # --- one-way assembly (47): every wrong placement leaves a ridge against a flat face
    def seats(ry,sy): return ridge_section(ry).difference(slot_section(sy)).area<1e-6
    flip=Y0+Y1-RG_Y
    chk("right way: ridges seat in the V-slots (0.15 on each slope, 0.3 at the apex)",seats(RG_Y,RG_Y) and abs(SLOT_H-RG_TOP-0.3)<1e-9)
    chk("middle part turned around: ridge can't seat",not seats(flip,RG_Y),f"(ridge at {flip-Y0:.1f} from the front vs slot at {RG_Y-Y0:.1f})")
    chk("frames swapped (slot at the other face): ridge can't seat",not seats(RG_Y,flip))
    chk("ridge 0.5 short of the slot's end (shoulders close first)",abs(SLOT_D-RG_L-0.5)<1e-9)
    # --- top middle: end walls, cradle walls, layer support (prints flat)
    fl,wl=top_layers()
    chk("end walls 5 beads (3.10) between the pocket and each cut",abs(POCKET.bounds[0]-CUT_L-ENDW)<0.005 and abs(CUT_R-POCKET.bounds[2]-ENDW)<0.005)
    chk("cradle front and back walls 3 beads (1.86)",abs(POCKET.bounds[1]-Y0-CW)<0.005 and abs(Y1-POCKET.bounds[3]-CW)<0.005)
    chk("camera window inside the pocket (walls never over the window)",POCKET.contains(CAMWIN) and wl.intersection(CAMWIN).area<1e-6)
    chk("top middle 160.00 long",abs(CUT_R-CUT_L-160)<0.005)
    # --- board part: posts and ends stand on the floor, groove leaves 0.9 under it
    chk("brim groove leaves 0.9 (3 layers) of floor",abs(FL-GROOVE[2]-0.9)<1e-9)
    chk("brim groove inside the channel, clear of the rail and marker margins",channel().contains(sbox(-HB+RAILW+0.01,GROOVE[0],HB-RAILW-0.01,GROOVE[1])))
    # --- grid lock: Z values of the flat parts, print-Z values of the frames (y), bead walls
    zs={"board floor":FL,"rails/back strip":RL,"step post top":FL+15,"column top":FL+30,"board ends":BH,"groove floor":FL-GROOVE[2],"marker inlay (2 layers)":0.6,
        "step chamfer":STEP_CH,"edge chamfer":EDGE,"ridge top":RG_TOP,"top middle height":TB1-TB0,"cradle floor":FLOOR_T,
        "frame depth (print Z)":DEP,"V-slot edges from the front (print Z)":RG_Y-Y0-SLOT_W/2,"V-slot width (print Z)":SLOT_W}
    off=[k for k,v in zs.items() if abs(v/LAYER-round(v/LAYER))>1e-6]
    chk("grid lock: every Z value on the 0.3 layer grid",not off,"("+", ".join(f"{k} {v:g} = {v/LAYER:.0f}" for k,v in zs.items())+")" if not off else str(off))
    bw={"cradle walls":CW,"end walls":ENDW,"marker cells":1.86}
    chk("grid lock: bead walls whole beads at 0.62",all(abs(v/BEAD-round(v/BEAD))<0.01 for v in bw.values()),"("+", ".join(f"{k} {v} = {v/BEAD:.0f}" for k,v in bw.items())+")")
    # --- overhangs as printed: frames are prisms in print Z (front face down); flat parts are checked layer on layer
    chk("top middle walls stand on its floor (no overhang printed flat)",wl.difference(TOPMID).area<1e-6)
    chk("board posts stand on the rails and back strip",all(p.difference(unary_union(rails+[sbox(-HB,STOP,HB,BD)])).area<1e-6 for _,p,_ in posts()))
    print("INFO frames print front face down: every profile wall is vertical; only the V-slot roofs (45 deg) and the 0.9 bed-edge chamfers (45 deg) lean")
    # --- plate fit (P1S 256 x 256, excluded corner 18 x 28, 0.5 margin; Orca checks the convex outline)
    plate=sbox(0,0,256,256).buffer(-0.5); corner=sbox(0,0,18,28)
    parts={"right side frame (on its side)":FR["right"],"left side frame (on its side)":FR["left"],
           "top middle (flat)":unary_union([TOPMID,ridge_plan(CUT_R,1),ridge_plan(CUT_L,-1)]),
           "board part (flat)":unary_union([board_plan(),side_end_fillets(),ridge_plan(CUT_B,1),ridge_plan(-CUT_B,-1)])}
    for nm,g in parts.items():
        ok=None
        for ang in (0,90,180,270):
            r=affinity.rotate(g,ang,origin=(0,0)); rb=r.bounds
            r=affinity.translate(r,256-0.5-rb[2],256-0.5-rb[3])
            if plate.contains(r) and not r.convex_hull.intersects(corner): ok=ang; break
        b=g.bounds; chk(f"{nm} fits the plate, outline clear of the excluded corner",ok is not None,f"({b[2]-b[0]:.1f} x {b[3]-b[1]:.1f}, turned {ok})")
    chk("print heights under 256",max(DEP,FL+30,TB1-TB0)<256,f"(frames {DEP}, board part {FL+30}, top middle {TB1-TB0})")
    print(f"INFO clip block corners (change 60): low block/post r{R_LOWPOST}, high block/post r{R_HIGHPOST}, high block top r{R_HIGHTOP}")
    print("fails:",fails)

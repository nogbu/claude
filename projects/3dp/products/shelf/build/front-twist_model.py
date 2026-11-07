"""Twist-lock front piece, working model (concept, user 2026-10-10: "rod slides in the bore and then twist locks behind the first
crosswire"). Coords as front-piece_model.py: x along the front edge rod (rod end 0, first crosswire W1, second W2), y front (-) to
rear (+), z up in use; bore center at y 0, z 0, the rod resting on the bore bottom (center z RC).
Parts: body and 45-deg step (x X0..0) and closed stub sleeve (x 0..J0) as front-piece_model.py; past J0 only a front wall (spine)
in front of the crosswire ends (x J0..XH0), then a hook (x XH0..XH1) that curls from the spine over the rod top, between the first and
second crosswires, its top flush with the crosswire tops (agreed change 6), its tip cut at 45 deg at the bore's 45-deg point.
Installing: the piece is turned THETA about the rod (top toward the front) so the hook and spine pass under the first crosswire,
slid on until the stub sleeve meets that crosswire, then turned back; the spine's top meets the crosswire's front end (C gap) as the
stop, and the hook sits behind (inboard of) the crosswire, so the piece can't slide off. build() -> (manifold, sizes)."""
import importlib.util, os, numpy as np, manifold3d as m
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fpm", os.path.join(HERE, "front-piece_model.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
ROD, WIRE, BORE, C, RC, WB, TOP = F.ROD, F.WIRE, F.BORE, F.C, F.RC, F.WB, F.TOP
W1, W2, X0, H, ZB, J0, LEAD = F.W1, F.W2, F.X0, F.H, F.ZB, F.J0, F.LEAD
box, cyl, prism, tm = F.box, F.cyl, F.prism, F.tm
YI = -ROD - C                       # spine's inner face: C in front of the crosswire ends (they end flush with the rod's front face)
XH0 = W1 + WIRE + C                 # hook start, C behind the first crosswire
XH1 = W2 - 0.7 - WIRE - C           # hook end, C short of the second crosswire at its nearest (spacing irregular to 0.7)

def build(fw=3.0, tr=2.35, tz=2.48, peak=3.65, xh1=XH1, zs=ZB, fy=None, hh=0.0, hx0=None, bd=0.0):
    """fw: front wall thickness from YI (print layers); tr, tz: stub sleeve rear and bottom walls (agreed changes 21, 22);
    peak: stub bore roof flat (agreed change 20), cut only along the stub (x 0..J0; the bore is open to the rear beyond it);
    zs: must be ZB: the front wall runs the full 20 mm depth from the rod end, so the front face is one band (other depths dropped
    2026-10-10). Along the hook the front wall's inner face is at the bore (y -BORE) below z 0, tangent to the bore, not 0.15
    farther forward at YI (no crosswire there), so the curl's inner face has no step at its root (2026-10-10, for the 3D check).
    Built as one envelope minus voids, so no two solids touch face to face (touching boxes left zero-length edges that tetgen
    can't mesh, 2026-10-10). fy: None, or a floor under the rod past the stub, full depth from the wall back to y fy (stiffening
    trial, 2026-10-10); beside the first crosswire the wall's inner face runs
    from YI at z 0.6 straight onto the bore's front at z 0 (a 0.15 ledge there read as a sharp-corner hot spot, 2026-10-11). hh: the top raised that far above the crosswire tops (agreed change 6's exception, as the J-slot's roof
    strip; user 2026-10-11 picked a raised hook) from x hx0 (default XH0, the hook only; J0 also raises the front wall in front of
    the first crosswire) to the hook end, full depth YF..OR. bd: the bore (and its peaked roof) runs on that far past x 0 into the body,
    so a stub longer than the modeled 12 still lets the stub sleeve reach the first crosswire (agreed change 5; options 2026-10-10).
    Returns (manifold, dict of sizes)."""
    assert zs == ZB
    YF = YI - fw; OR = BORE + tr; OZ = BORE + tz; XS = -ZB - OZ        # XS: where the 45-deg step under the stub sleeve ends
    hx0 = XH0 if hx0 is None else hx0; ZT = TOP + hh + 1                # ZT: void tops clear the raised top
    p = prism([(X0, ZB), (xh1, ZB), (xh1, TOP + hh), (hx0, TOP + hh), (hx0, TOP), (X0, TOP)], "y", YF, OR) if hh else box(X0, xh1, YF, OR, ZB, TOP)
    if fy is None:
        p = p - prism([(-1, ZB - 1), (XS, -OZ), (J0 + 1, -OZ), (J0 + 1, ZB - 1)], "y", YI, OR + 1)   # under the stub sleeve (the 45-deg line run on past the bottom face)
        p = p - box(J0, XH0, YI, OR + 1, ZB - 1, ZT)                                                    # beside the first crosswire
        p = p - prism([(-BORE, ZB - 1), (-BORE, 0), (0, 0), (OR + 1, OR + 1), (OR + 1, ZB - 1)], "x", XH0, xh1 + 1)  # under and behind the hook
    else:
        p = p - prism([(-1, ZB - 1), (XS, -OZ), (J0 + 1, -OZ), (J0 + 1, ZB - 1)], "y", fy, OR + 1)
        p = p - prism([(YI, ZT), (YI, 0.6), (-BORE, 0), (fy, 0), (fy, ZB - 1), (OR + 1, ZB - 1), (OR + 1, ZT)], "x", J0, XH0)   # wall face eased onto the bore (no 0.15 ledge at z 0; 2026-10-11)
        p = p - prism([(fy, ZB - 1), (fy, 0), (0, 0), (OR + 1, OR + 1), (OR + 1, ZB - 1)], "x", XH0, xh1 + 1)
    p = p - cyl(BORE, xh1 + 1 + bd, "x").translate([-bd, 0, 0])
    if peak:
        tt = BORE / np.sqrt(2); a = BORE * np.sqrt(2); h = max(a - peak, 0.0)
        p = p - prism([(0, 0), (tt, -tt), (peak, -h), (peak, h), (tt, tt)] if h > 0 else [(0, 0), (tt, -tt), (a, 0), (tt, tt)], "x", -bd, J0 + 1)
    p = p - cyl(BORE, LEAD + 0.01, "x", BORE + LEAD).translate([xh1 - LEAD, 0, 0])       # lead-in at the hook's inboard mouth
    return p, dict(YF=YF, OR=OR, OZ=OZ, XH0=XH0, XH1=xh1, t=BORE / np.sqrt(2), hh=hh, hx0=hx0, bd=bd)

def turned(man, deg):
    """The piece turned deg about the rod's axis (y 0, z RC), top toward the front."""
    return man.translate([0, 0, -RC]).rotate([deg, 0, 0]).translate([0, 0, RC])

def rod(L=70.0):
    return cyl(ROD, L, "x").translate([0, 0, RC])

def wires(L=60.0, grow=0.0):
    """First and second crosswires, lying on the rod top and running back from its front face; grow adds to the radius (clearance checks)."""
    return m.Manifold.batch_boolean([cyl(WIRE + grow, L, "y").translate([x, -ROD - grow, WB + WIRE]) for x in (W1, W2)], m.OpType.Add)

def path_check(p, theta, grow=0.25, step=0.5, dstep=2.0):
    """Overlap volumes (mm^3) with the crosswires grown by grow: sliding on at theta from 45 mm out to seated, then turning back to 0.
    Returns (worst slide overlap, worst turn overlap, worst rod overlap)."""
    w = wires(grow=grow); r = cyl(ROD - 0.02, 70, "x").translate([0, 0, RC]); q = turned(p, theta)
    s_bad = max((q.translate([-s, 0, 0]) ^ w).volume() for s in np.arange(0, 45.01, step))
    t_bad = max((turned(p, d) ^ w).volume() for d in np.arange(0, theta + 0.01, dstep))
    r_bad = max((turned(p, d) ^ r).volume() for d in (0, theta / 2, theta))
    return s_bad, t_bad, r_bad

if __name__ == "__main__":
    p, d = build(); print({k: round(v, 2) for k, v in d.items()}, "volume", round(p.volume(), 1), "solid g", round(p.volume() * 1.27e-3, 2))
    print("seated overlap with true wires", round((p ^ wires()).volume(), 3), "rod", round((p ^ rod()).volume(), 3))
    for th in (80, 90, 100, 110, 120, 130, 140):
        print(th, [round(v, 3) for v in path_check(p, th, step=1.0, dstep=5.0)])

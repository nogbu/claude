"""Rear piece working model (shelf state.md agreed changes 1, 3, 4, 5, 27): stub sleeves on the rear corner rod and lip outer rod,
body on the clip, a drop around the lip rod below the clip seat, and the lip-rod sleeve run on inside the bend to x reach,
open at the rear for the lip crosswires. Unsized where not agreed; fillets left out except the sleeve-root fillet.
Coords: rear corner bore center at y 0, z 0 (deck toward -y), lip bore center 32.3 below it; rod ends at x 0, glass side at -x.
Prints on its side, front face on the bed (open decision 1's leader), so z and x widths are bead widths and y is layers."""
import importlib.util, os, numpy as np, manifold3d as m
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("front_piece_model", os.path.join(HERE, "front-piece_model.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
ROD, WIRE, BORE, C, RC, WB, TOP, ZB, X0, W1, J0 = F.ROD, F.WIRE, F.BORE, F.C, F.RC, F.WB, F.TOP, F.ZB, F.X0, F.W1, F.J0
LIPB = -32.3; LIPZ = LIPB + RC                   # lip bore center; lip rod center (rod rests on the bore floor, as the front)
box, cyl, prism, tm = F.box, F.cyl, F.prism, F.tm
def bore_z(yc):
    """Height above the bore center where the faceted bore (the cyl in use) crosses y = yc. A cut to the true circle's height
    left a 0.02 mm step on the facets, a notch that read 136 MPa in 3D (2026-10-10)."""
    v = tm(cyl(BORE, 1.0, "x")).vertices[:, 1:]; v = np.unique(np.round(v, 9), axis=0)
    v = v[np.argsort(np.arctan2(v[:, 1], v[:, 0]))]
    for a, b in zip(v, np.roll(v, -1, 0)):
        if (a[0] - yc) * (b[0] - yc) <= 0 and a[0] != b[0] and a[1] + b[1] > 0:
            return a[1] + (yc - a[0]) / (b[0] - a[0]) * (b[1] - a[1])
    raise ValueError(yc)
def build(reach=40.0, tr=2.35, tz=2.48, ttop=2.48, xd=-15.0, rear=ROD - C, fil=1.0, close_below=None, trim=False, lead=None, lead_c=None, peak=None, yr=None, lip=None, ch45=False):
    """reach: sleeve end x; tr: front wall beyond the bores (front face y -(BORE+tr)), rear face y BORE+tr in the stub zone;
    tz: wall under the lip bore; ttop: wall over the lip bore in the sleeve; xd: drop's outboard face; rear: sleeve rear face y
    (short of the lip wires at ROD + 0); fil: fillet where the sleeve top meets the drop; close_below: z (relative to the lip
    bore center) below which the sleeve's rear wall runs out to the full rear face y BORE+tr (None: open the whole height);
    trim: cut each knife-edge lip of the rear opening back to one bead (BEAD 0.62), as the front piece's agreed change 24;
    lead: 45-deg lead-in at the sleeve mouth (x reach) on the lip bore and both edges of the rear opening (None: none);
    lead_c: 45-deg lead-in on the rear corner rod bore's mouth (x J0) (None: none);
    peak: both stub bores' roofs (x 0 to J0; print up is +y) peaked at 45 deg and cut flat this far from the bore center
    (None: round), as the front piece's agreed change 20; yr: rear face y (None: BORE + tr);
    lip: the upper lip's trimmed thickness in y, i.e. in layers (None: BEAD 0.62, agreed change 28);
    ch45: straight cut where the closed rear wall's top (close_below) meets the lip bore, from the wall top's rear edge (y rear) to
    the bore at y rear - 0.6, both on the layer grid, so that corner doesn't overhang past 45 deg in print (dpcheck 2026-10-10: 53 deg);
    35 deg from vertical at close_below -1.90 (from the bore center: 1.75 under the rod center, agreed change 28)."""
    yf = -(BORE + tr); yr = BORE + tr if yr is None else yr; zb = LIPB - BORE - tz; zt = LIPB + BORE + ttop
    body = box(X0, J0, yf, yr, ZB, TOP) + box(xd, J0, yf, yr, zb, ZB)
    sleeve = box(J0, reach, yf, rear, zb, zt)                    # faces meet exactly: 0.01 overlaps left sliver edges that stalled the 3D solver
    root = box(J0, J0 + fil, yf, rear, zt, zt + fil) - cyl(fil, rear - yf + 2, "y").translate([J0 + fil, yf - 1, zt + fil])
    p = body + sleeve + root
    if close_below is not None:
        p = p + box(J0, reach, rear, yr, zb, LIPB + close_below)
    p = p - cyl(BORE, J0 + 1, "x") - cyl(BORE, reach + 1, "x").translate([0, 0, LIPB])
    if peak is not None:
        t = BORE / np.sqrt(2); h = max(BORE * np.sqrt(2) - peak, 0.0)
        pk = prism([(0, 0), (t, -t), (peak, -h), (peak, h), (t, t)], "x", 0.0, J0)   # (y, z); F.peak_cut runs to the front piece's XE
        p = p - pk - pk.translate([0, 0, LIPB])
    lipt = F.BEAD if lip is None else lip
    if trim:                                                      # lips: where the wall from the bore to the rear face is under one bead
        dz = bore_z(rear - lipt)                                # the cut runs from the opening's lower edge (or -dz) to dz, the rest of it in the bore
        p = p - box(J0, reach + 1, rear - lipt, rear + 1, LIPB + (-dz if close_below is None else close_below), LIPB + dz)
    if ch45 and close_below is not None:                          # straight cut from the bore at y rear - 0.6 (layer 25) to the wall
        y0 = rear - 0.6; S = (y0, -bore_z(y0))                    # top's rear edge at y rear (layer 27): both ends on the grid;
                                                                  # S on the faceted bore (as bore_z), so no micro-step
        p = p - prism([(S[0], LIPB + S[1]), (rear, LIPB + close_below), (S[0], LIPB + close_below)], "x", J0, reach + 1)
    if lead_c:                                                    # kept inside a peaked roof's profile, so the cone neither pockets
        cone = cyl(BORE, lead_c + 0.01, "x", BORE + lead_c).translate([J0 - lead_c, 0, 0])   # the roof nor widens its bridge
        if peak is not None:
            t = BORE / np.sqrt(2); h = max(BORE * np.sqrt(2) - peak, 0.0); x0, x1 = J0 - lead_c - 1, J0 + 1
            w = h + peak + BORE + 2                                   # below the flat, inside the roof's 45-deg lines carried down
            keep = prism([(peak, -h), (peak, h), (-BORE - 2, w), (-BORE - 2, -w)], "x", x0, x1)
            cone = cone ^ keep
        p = p - cone
    if lead:
        p = p - cyl(BORE, lead + 0.01, "x", BORE + lead).translate([reach - lead, 0, LIPB])
        if trim:                                                  # the opening's edges, as the front piece's channel mouth
            lo = LIPB + (-dz if close_below is None else close_below); hi = LIPB + dz
            for zc, d in ((lo, -1), (hi, 1)):
                q = lambda dd: [(rear - lipt, zc), (yr + 1, zc), (yr + 1, zc + d * dd), (rear - lipt, zc + d * dd)]
                p = p - m.Manifold.hull(prism(q(lead), "x", reach, reach + 0.01) + prism(q(0.01), "x", reach - lead, reach - lead + 0.01))
    return p, dict(yf=yf, yr=yr, zb=zb, zt=zt, reach=reach, xd=xd, rear=rear)
def rods(length=70.0):
    return cyl(ROD, length, "x").translate([0, 0, RC]) + cyl(ROD, length, "x").translate([0, 0, LIPZ])
def letter(ch, h=6.0, font="DejaVu Sans"):
    """Outline of one letter h mm tall (cap height), centered on (0, 0), as a CrossSection (holes kept)."""
    from matplotlib.textpath import TextPath; from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), ch, size=1.0, prop=FontProperties(family=font, weight="bold"))
    polys = [np.asarray(p) for p in tp.to_polygons() if len(p) > 2]
    cs = m.CrossSection(polys, m.FillRule.EvenOdd)
    lo, hi = cs.bounds()[:2], cs.bounds()[2:]; s = h / (hi[1] - lo[1])
    return cs.scale([s, s]).translate([-(lo[0] + hi[0]) / 2 * s, -(lo[1] + hi[1]) / 2 * s])
def hand(piece, d, side="L", depth=0.4, h=6.0):
    """The left piece is the model (glass at -x); the right piece is its mirror in x. Debosses side's letter, depth deep,
    in the glass-end face (x X0), reading upright seen from the glass side (text right = -y, up = +z), centered on the face."""
    yc = (d["yf"] + d["yr"]) / 2; zc = (ZB + TOP) / 2
    L = side == "L"; cs = letter(side, h)
    e = m.Manifold.extrude(cs.scale([-1, 1]) if L else cs, depth + 0.01)   # left: text right = -y seen from -x; right: +y seen from +x
    e = e.rotate([90, 0, 0]).rotate([0, 0, 90])                     # letter x -> +y, letter y -> +z, depth -> +x
    e = e.translate([X0 - 0.01, yc, zc])
    p = piece if L else piece.mirror([1, 0, 0])
    return p - (e if L else e.mirror([1, 0, 0]))

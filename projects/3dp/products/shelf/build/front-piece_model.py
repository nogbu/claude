"""Front piece working model (shelf state.md agreed changes 15-18: sizes, 45-deg ridge ramp, root C: 3.0 front wall, r1.35 root fillet, 7-bead roof); r0.6 channel floor fillet (agreed change 19), bore roof peak cut flat 3.65 (agreed change 20), bed-side knife edge trimmed (24), open corner along the opening (40: build(open_corner=True)).
Walls per side: front (use -y, print Z layers), rear (use +y, layers), bottom (use -z, beads). Coords as front-piece_concept.py."""
import numpy as np, manifold3d as m, trimesh
ROD = 5.9 / 2; WIRE = 2.9 / 2; BORE = 6.2 / 2; C = 0.3
RC = -(BORE - ROD); WB = RC + ROD; TOP = WB + 2 * WIRE
ROOF = 4.34; W1 = 12.0; W2 = W1 + 25.3; XE = W2 + 0.7 + WIRE + 2.5; X0 = -45.0
GAPF = 1.5; FRONT = -ROD - GAPF; FILLET = 1.35; FLOORF = 0.6; H = 20.0; ZB = TOP - H; LEAD = 0.6; BEAD = 0.62; J0 = W1 - WIRE - C
def cyl(r, h, axis, r2=None):
    c = m.Manifold.cylinder(h, r, r if r2 is None else r2, 64)
    return c.rotate([0, 90, 0]) if axis == "x" else c.rotate([-90, 0, 0])
def box(x0, x1, y0, y1, z0, z1): return m.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def tm(man):
    g = man.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts))
def prism(pts, axis, a0, a1):                 # extrude a polygon: axis "x" (pts in YZ) or "y" (pts in XZ)
    a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    cs = m.CrossSection([pts if a > 0 else pts[::-1]]); e = m.Manifold.extrude(cs, a1 - a0)
    return e.rotate([90, 0, 90]).translate([a0, 0, 0]) if axis == "x" else e.rotate([90, 0, 0]).translate([0, a1, 0])
def build(fw=3.0, tr=2.35, tz=2.48, overlap=2.1, peak=3.65, trim_top=False, open_corner=False):
    """peak: None = round bore; a number = 45-deg peaked roof toward use +y (print up), cut flat that far from the bore center.
    trim_top: trim the +y (print-top) knife edge too (agreed change 24 until 2026-10-10); False (agreed 2026-10-10) leaves the peak's 45-deg line to carry it (the trim's flat underside
    there prints as a 0.6-wide ledge over air, anchored only at x J0: Orca's floating cantilever, 2026-10-10).
    open_corner (agreed change 40, 2026-10-10): along the opening (x J0 to XE+1) cut away the strip between the channel and the
    peak's near 45-deg face and the flat, so the far face runs on at 45 deg to the rear face; untrimmed, that strip started over air
    and printed as strings (front-fit-test_rev1). Needs peak."""
    OF = FRONT - (-fw) if False else fw - FRONT; OR = BORE + tr; OZ = BORE + tz; RT = -ROD + overlap
    body = box(X0, 0, -OF, OR, ZB, TOP)
    slope = m.Manifold.hull(box(0, 0.01, -OF, OR, ZB, TOP) + box(-ZB - OZ, -ZB - OZ + 0.01, -OF, OR, -OZ, TOP))
    sleeve = box(0, XE, -OF, OR, -OZ, TOP)
    rise = C + ROOF; ramp = prism([(J0 - rise, TOP), (J0 + 0.01, TOP), (J0 + 0.01, TOP + rise)], "y", -OF, RT)
    roof = box(J0, XE, -OF, RT, TOP, TOP + rise)
    p = body + slope + sleeve + roof + ramp
    p = p - cyl(BORE, XE + 1, "x") - (peak_cut(peak) if peak else m.Manifold()) - box(J0, XE + 1, FRONT, OR + 1, WB - C, TOP + C)
    fz = TOP + C
    p = p + (box(J0, XE, FRONT, FRONT + FILLET, fz - FILLET, fz) - cyl(FILLET, XE - J0 + 2, "x").translate([J0 - 1, FRONT + FILLET, fz - FILLET]))
    zf = WB - C
    p = p + (box(J0, XE, FRONT, FRONT + FLOORF, zf, zf + FLOORF) - cyl(FLOORF, XE - J0 + 2, "x").translate([J0 - 1, FRONT + FLOORF, zf + FLOORF]))
    yk = np.sqrt(BORE ** 2 - (WB - C - BEAD) ** 2)               # trim the bore/channel-floor knife edge(s) to one bead (agreed change 24)
    p = p - box(J0 - 0.01, XE + 1, -yk, yk if trim_top else 0.0, WB - C - BEAD, WB - C + 0.01)
    if open_corner:                                              # far face line z = y - a; top edge in the channel (air)
        a = BORE * np.sqrt(2); zt = WB - C + 0.4
        p = p - prism([(1.5, zt), (zt + a, zt), (peak, peak - a), (1.5, peak - a)], "x", J0, XE + 1)
    p = p - cyl(BORE, LEAD + 0.01, "x", BORE + LEAD).translate([XE - LEAD, 0, 0])
    for zc, d in ((WB - C, -1), (TOP + C, 1)):
        q = lambda dd: [(FRONT, zc), (OR + 1, zc), (OR + 1, zc + d * dd), (FRONT, zc + d * dd)]
        p = p - m.Manifold.hull(prism(q(LEAD), "x", XE, XE + 0.01) + prism(q(0.01), "x", XE - LEAD, XE - LEAD + 0.01))
    return p, dict(OF=OF, OR=OR, OZ=OZ, RT=RT)
def peak_cut(flat):
    t = BORE / np.sqrt(2); a = BORE * np.sqrt(2); h = max(a - flat, 0.0)
    pts = [(0, 0), (t, -t), (flat, -h), (flat, h), (t, t)] if h > 0 else [(0, 0), (t, -t), (a, 0), (t, t)]
    return prism(pts, "x", 0.0, XE + 1)
rod = cyl(ROD, 70, "x").translate([0, 0, RC])
wires = m.Manifold.batch_boolean([cyl(WIRE, 26, "y").translate([x, -ROD, WB + WIRE]) for x in (W1, W2)], m.OpType.Add)

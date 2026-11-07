"""Scratch working model, front piece optimization pass: raised roof sized for printing on its side (3.10, 5 beads),
lead-ins on the bore and wire channel mouths, body full shelf height (20, Measured factory shelf) where it sits on the clip.
Use coords: X along the rod (cut end 0, interior +X), Y front(-) to back(+), Z up, bore center 0.
Corner footprint (how far the body reaches back and to the glass) isn't set: body depth and length are placeholders.
Writes front_pass.png and front_pass.stl beside it (concept only, not a build). Roof thickness from front-roof_size.py."""
import os, sys
import numpy as np, manifold3d as m, trimesh
sys.path.insert(0, "/home/claude/claude/projects/3dp/scripts")
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))

ROD = 5.9 / 2; WIRE = 2.9 / 2; BORE = 6.2 / 2; C = 0.3
RC = -(BORE - ROD); WB = RC + ROD; WT = WB + 2 * WIRE; TOP = WT
ROOF = 3.10                                  # 5 beads: roof bends across the layers on its side (needs 2.76, roof_size.py)
W1 = 12.0; W2 = W1 + 25.3
XE = W2 + 0.7 + WIRE + 2.5; X0 = -45.0
OUT = BORE + 3.0; GAPF = 0.6; FRONT = -ROD - GAPF; FILLET = 0.6; OVER = 2.0; RT = -ROD + OVER
H = 20.0; ZB = TOP - H                       # body bottom on the clip: factory shelf 20 thick (Measured)
LEAD = 0.6                                   # 45-deg lead-ins at the sleeve mouth (as on the bore test)
J0 = W1 - WIRE - C

def cyl(r, h, axis, r2=None):
    c = m.Manifold.cylinder(h, r, r if r2 is None else r2, 64)
    return c.rotate([0, 90, 0]) if axis == "x" else c.rotate([-90, 0, 0])
def box(x0, x1, y0, y1, z0, z1):
    return m.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def tm(man):
    g = man.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts))
def prism_x(pts, x0, x1):                    # extrude a YZ polygon along X
    a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    cs = m.CrossSection([pts if a > 0 else pts[::-1]]); return m.Manifold.extrude(cs, x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])

# body: full height outboard of the stub's cut end, stepping down with a 45-deg slope under the rod to the sleeve
body = box(X0, 0, -OUT, OUT, ZB, TOP)
slope = m.Manifold.hull(box(0, 0.01, -OUT, OUT, ZB, TOP) + box(-ZB - OUT + 0, -ZB - OUT + 0.01, -OUT, OUT, -OUT, TOP))
sleeve = box(0, XE, -OUT, OUT, -OUT, TOP)
piece = body + slope + sleeve + box(J0, XE, -OUT, RT, TOP, TOP + C + ROOF)
piece = piece - cyl(BORE, XE + 1, "x") - box(J0, XE + 1, FRONT, OUT + 1, WB - C, TOP + C)
fz = TOP + C; fy = FRONT
piece = piece + (box(J0, XE, fy, fy + FILLET, fz - FILLET, fz) - cyl(FILLET, XE - J0 + 2, "x").translate([J0 - 1, fy + FILLET, fz - FILLET]))
# lead-ins at the inboard mouth: bore cone, and 45-deg chamfers opening the wire channel
piece = piece - cyl(BORE, LEAD + 0.01, "x", BORE + LEAD).translate([XE - LEAD, 0, 0])
# channel mouth chamfer: a wedge whose depth grows to LEAD at the face
wedge_pts = lambda zc, d: [(FRONT, zc), (OUT + 1, zc), (OUT + 1, zc + d * LEAD), (FRONT, zc + d * LEAD)]
for zc, d in ((WB - C, -1), (TOP + C, 1)):
    w = m.Manifold.hull(prism_x(wedge_pts(zc, d), XE, XE + 0.01) + prism_x([(FRONT, zc), (OUT + 1, zc), (OUT + 1, zc + d * 0.01), (FRONT, zc + d * 0.01)], XE - LEAD, XE - LEAD + 0.01))
    piece = piece - w
tm(piece).export(os.path.join(HERE, "front_pass.stl"))

rod = cyl(ROD, 70, "x").translate([0, 0, RC])
wires = m.Manifold.batch_boolean([cyl(WIRE, 26, "y").translate([x, -ROD, WB + WIRE]) for x in (W1, W2)], m.OpType.Add)
cl = piece ^ (rod + wires)
print("clash with rod or wires mm3", 0 if cl.is_empty() else round(tm(cl).volume, 3))
print("bounds", tm(piece).bounds.round(2).tolist())

SIDE = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])          # (x, y, z) -> (x, -z, y): front face on the bed (rotation)
ROD_C = np.array([.25, .25, .27]); WIRE_C = np.array([.45, .45, .5]); HI = np.array([.95, .55, .15])
def add(man, col, clip=None, T=None, sh=0.0):
    if clip is not None: man = man ^ clip
    if man.is_empty(): return
    g = tm(man); V = g.vertices if T is None else g.vertices @ T.T
    R.mesh(trimesh.Trimesh(V + [0, 0, sh], g.faces), col)

fig, axs = plt.subplots(2, 2, figsize=(18, 18)); fig.subplots_adjust(bottom=0.08, hspace=0.2)
R.FACES.clear(); add(piece, R.BONE); add(rod, ROD_C); add(wires - piece, WIRE_C)
cam = R.view(axs[0, 0], eye=(-1.0, -1.4, 0.9), pad=4, title="In use, from the front", edge_depth=0.5)
R.call(axs[0, 0], cam, (W1 + 6, -OUT, TOP + C + ROOF), (60, 40), "roof ridge, 3.4 above the wire tops", color="#c0392b", size=11)
R.call(axs[0, 0], cam, (X0 + 5, -OUT, ZB), (0, -50), "body to the glass (length and depth not set)", color="#555", size=10)
R.FACES.clear(); add(piece, R.BONE); add(rod, ROD_C); add(wires - piece, WIRE_C)
cam = R.view(axs[0, 1], eye=(1.2, 1.3, 0.8), pad=4, title="In use, from inside the shelf (back)", edge_depth=0.5)
R.call(axs[0, 1], cam, (XE, OUT, WB), (70, -60), "lead-ins on the bore and channel mouth", color="#1f5fa8", size=11)
R.call(axs[0, 1], cam, (J0, OUT, TOP), (-60, 70), "stops against the last crosswire", color="#1f5fa8", size=11)
# close-up of the mouth
clip = box(XE - 8, XE + 1, -OUT - 1, OUT + 1, -OUT - 1, TOP + 5)
R.FACES.clear(); add(piece, HI, clip); add(rod, ROD_C, clip)
cam = R.view(axs[1, 0], eye=(1.0, 0.5, 0.35), pad=3, title="Close-up: sleeve mouth (orange), looking out toward the glass", edge_depth=0.3)
sh = -(tm(piece).vertices @ SIDE.T)[:, 2].min()
R.FACES.clear(); add(piece, R.BONE, T=SIDE, sh=sh)
V = tm(piece).vertices @ SIDE.T
R.box(V[:, 0].min() - 8, V[:, 0].max() + 8, V[:, 1].min() - 8, V[:, 1].max() + 8, -1.0, 0.0, np.array([.75, .78, .8]))
R.view(axs[1, 1], eye=(-0.6, -1.4, 0.9), pad=4, title="Prints on its side: front face on the bed, no supports", edge_depth=0.5)
fig.text(0.01, 0.01, "Scratch model front_pass.py (front_pass.stl beside it). Roof 3.10 (5 beads), 2.0 over the wire, r0.6 root fillet; 0.6 lead-ins; "
         "body 20 tall. Body length and depth, 3 mm sleeve walls and the peaked bore roof (not drawn) are still open; other fillets left out.", fontsize=9, color="#555")
R.save(fig, os.path.join(HERE, "front_pass.png"))

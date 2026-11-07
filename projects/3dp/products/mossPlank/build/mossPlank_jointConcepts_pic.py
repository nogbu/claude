"""mossPlank stacking-joint concepts (not sized: design load pending). Two 200 mm sections on the 3.5in pot rev10.2 +
insert rev4; the lower one in the pot (back flush with the wall, constant above the lip base), the upper one a prism of
that top outline with a 25 mm spigot sliding into the lower one's open top (0.2 mm gap per side, design principle 6 snug).
A: two snap tabs on the spigot's side walls catching windows in the lower section. B: one removable pin through both."""
import sys, math, numpy as np, trimesh, manifold3d as mf
sys.path.insert(0, "/home/user/claude/projects/3dp/scripts"); sys.path.insert(0, sys.argv[1])
import render3d as R
from dpcheck import load_3mf
from nurseryPots_lib import pot_profile
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S = sys.argv[1]
P = pot_profile(105.12, 48.07, 1.0); rin = P['r_in']
def get(p):
    it = load_3mf(p)[0][0]; V = it["V"].copy(); c = (V.min(0) + V.max(0)) / 2; V[:, 0] -= c[0]; V[:, 1] -= c[1]; V[:, 2] -= V[:, 2].min()
    return trimesh.Trimesh(V, it["T"], process=False)
pot = get(S + "/3.5inPot_rev10.2.3mf"); ins = get(S + "/3.5inInsert_rev4.3mf")
ins.vertices[:, 2] = 36.0 - ins.vertices[:, 2] + 1.80
zb, H, W = 37.80, 200.0, 60.0; zl = P['z_lb']; zt = zb + H
r0, r1 = rin(zb), rin(zl)
d = math.sqrt(r0**2 - 900) - 15.0
FRONT, SIDE, FLOOR, GAP, SPIG = 2.0, 1.24, 1.2, 0.2, 25.0
a = SIDE / math.cos(math.radians(5.03))
def outline_lower(off, front, side, z0, z1):
    cone = mf.Manifold.cylinder(zl - zb, r0 - off, r1 - off, 512).translate([0, 0, zb])
    cap = mf.Manifold.cylinder(500, r1 - off, r1 - off, 512).translate([0, 0, zl])
    box = mf.Manifold.cube([W - 2 * side, 200, z1 - z0]).translate([-W / 2 + side, d + front, z0])
    return (cone + cap) ^ box
def prism(off, front, side, z0, z1):
    cyl = mf.Manifold.cylinder(z1 - z0, r1 - off, r1 - off, 512).translate([0, 0, z0])
    box = mf.Manifold.cube([W - 2 * side, 200, z1 - z0]).translate([-W / 2 + side, d + front, z0])
    return cyl ^ box
lower = outline_lower(0, 0, 0, zb, zt) - outline_lower(a, FRONT, SIDE, zb + FLOOR, zt + 1)
def upper(z0):
    body = prism(0, 0, 0, z0, z0 + H) - prism(a, FRONT, SIDE, z0 - 1, z0 + H + 1)
    s_out = prism(a + GAP, FRONT + GAP, SIDE + GAP, z0 - SPIG, z0 + 0.01)
    s_in = prism(a + GAP + SIDE, FRONT + GAP + SIDE, SIDE + GAP + SIDE, z0 - SPIG - 1, z0 + 1)
    return body + (s_out - s_in)
EX = 45.0; zu = zt + EX
def tm(m):
    m = m.to_mesh(); return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
yc = d + 8.0; zj = zt - 12.5                           # joint feature centre (depth, height below the lower top)
# A: windows in the lower side walls; tabs (U-cut cantilevers with an outward hook) on the spigot
win = mf.Manifold.cube([W + 10, 8, 5]).translate([-W / 2 - 5, yc - 4, zj - 2.5])
lowA = lower - win
up = upper(zu)
xs = W / 2 - SIDE - GAP                                # spigot outer side face
cut = mf.Manifold.cube([W + 10, 10, 14]).translate([-W / 2 - 5, yc - 5, zu - 22]) - mf.Manifold.cube([W + 10, 8, 13]).translate([-W / 2 - 5, yc - 4, zu - 22])
hooks = mf.Manifold.cube([1.0, 7, 4]).translate([xs, yc - 3.5, zu - 12.5 - 2]) + mf.Manifold.cube([1.0, 7, 4]).translate([-xs - 1.0, yc - 3.5, zu - 12.5 - 2])
upA = (up - cut) + hooks
# B: one pin across both side walls and the spigot
hole = mf.Manifold.cylinder(W + 10, 2.6, 2.6, 48).rotate([0, 90, 0]).translate([-W / 2 - 5, yc, zj])
lowB = lower - hole
upB = up - mf.Manifold.cylinder(W + 10, 2.6, 2.6, 48).rotate([0, 90, 0]).translate([-W / 2 - 5, yc, zu - 12.5])
pin = mf.Manifold.cylinder(W + 6, 2.4, 2.4, 48).rotate([0, 90, 0]).translate([-W / 2 - 3 - 25, yc, zj])
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); UP = np.array([0.40, 0.55, 0.70]); PIN = np.array([0.85, 0.55, 0.25])
CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
fig, axs = plt.subplots(2, 2, figsize=(15, 17), gridspec_kw=dict(height_ratios=[1.5, 1]))
crop = mf.Manifold.cube([W + 80, 120, 110]).translate([-W / 2 - 40, -20, zt - 45])
for j, (lo, upx, extra, title) in enumerate([
        (lowA, upA, None, "A: snap tabs (press both in to separate)"),
        (lowB, upB, pin, "B: one removable pin through both")]):
    ax = axs[0, j]; R.FACES.clear(); R.mesh(half, CLEAR); R.mesh(ins, INS); R.mesh(tm(lo), GREEN); R.mesh(tm(upx), UP)
    if extra is not None: R.mesh(tm(extra), PIN)
    cam = R.view(ax, eye=(-1.0, -1.6, 0.55), pad=8); ax.set_title(title + "\nupper section lifted %d mm; spigot 25 mm" % EX, fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax = axs[1, j]; R.FACES.clear(); R.mesh(tm(lo ^ crop), GREEN); R.mesh(tm(upx ^ crop), UP)
    if extra is not None: R.mesh(tm(extra ^ crop), PIN)
    cam = R.view(ax, eye=(-1.6, -1.0, 0.5), pad=6); ax.set_title("joint close-up, from front left", fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
fig.suptitle("Stacking joint concepts, 200 mm sections (not sized yet: design load pending)\nlower section green, upper section blue; open spigot keeps the moss and roots continuous", fontsize=14)
R.save(fig, sys.argv[2])

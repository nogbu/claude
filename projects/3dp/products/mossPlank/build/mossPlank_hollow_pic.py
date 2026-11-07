"""mossPlank flush-back readings on the 3.5in pot rev10.2 + insert rev4: a 60 mm wide plank, bottom at the insert top
(37.80 mm), back cut to the pot's inner wall at every height (wall radius from nurseryPots_lib.pot_profile).
R1: front face 5.45 mm back (agreed rectangle's), back extended to the wall. R2: 20 mm deep at center, front face moved back."""
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
zb, ztop, W = 37.80, 37.80 + 70, 60.0; zl = P['z_lb']
r0, r1 = rin(zb), rin(zl)
FRONT, SIDE, FLOOR = 2.0, 1.24, 1.2
def solid(d, a, front, side, floor, top):
    """Plank outline shrunk by a (horizontal) at the back, front and side walls moved in, floor raised."""
    cone = mf.Manifold.cylinder(zl - zb, r0 - a, r1 - a, 512).translate([0, 0, zb])
    cap = mf.Manifold.cylinder(ztop - zl + 2, r1 - a, r1 - a, 512).translate([0, 0, zl])
    box = mf.Manifold.cube([W - 2 * side, 200, top - zb - floor]).translate([-W / 2 + side, d + front, zb + floor])
    return (cone + cap) ^ box
def plank(d):
    a = SIDE / math.cos(math.radians(5.03))
    m = (solid(d, 0, 0, 0, 0, ztop) - solid(d, a, FRONT, SIDE, FLOOR, ztop + 1)).to_mesh()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
dR1 = math.sqrt(r0**2 - 900) - 15.0
edge = lambda d: math.sqrt(r0**2 - 900) - d
cases = [(dR1, "Hollow, open top: front 2 mm, sides and back 1.24 mm, floor 1.2 mm\n60 wide, 15 deep at the edges, front face %.2f mm behind center" % dR1)]
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); low = pot.slice_plane([0, 0, zb + 30], [0, 0, -1], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
fig, axs = plt.subplots(2, 1, figsize=(8, 13)); axs = axs.reshape(2, 1)
for j, (d, title) in enumerate(cases):
    pl = plank(d)
    for i, (eye, p) in enumerate([((-1.0, -1.6, 0.9), half), ((0, -1e-3, 1), low)]):
        ax = axs[i, j]; R.FACES.clear(); R.mesh(p, CLEAR); R.mesh(ins, INS)
        R.mesh(pl if i == 0 else pl.slice_plane([0, 0, zb + 30], [0, 0, -1], cap=True), GREEN)
        cam = R.view(ax, eye=eye, pad=6)
        ax.set_title(title if i == 0 else "top view, plank cut at 67.80 mm, back up", fontsize=13)
        R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
fig.suptitle("Back flush with the pot wall at every height;\nbottom at the insert top (37.80 mm)", fontsize=14)
R.save(fig, sys.argv[2])
print(r0, dR1, r0 - dR1, pl.volume, pl.is_watertight)

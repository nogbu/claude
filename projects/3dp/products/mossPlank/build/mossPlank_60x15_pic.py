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
def plank(d):
    cone = mf.Manifold.cylinder(zl - zb, r0, r1, 512).translate([0, 0, zb])
    cap = mf.Manifold.cylinder(ztop - zl + 1, r1, r1, 512).translate([0, 0, zl])   # above the lip base: no wall, keep the lip-base outline
    box = mf.Manifold.cube([W, 200, ztop - zb]).translate([-W / 2, d, zb])
    m = ((cone + cap) ^ box).to_mesh()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
dR1 = math.sqrt(r0**2 - 900) - 15.0
edge = lambda d: math.sqrt(r0**2 - 900) - d
cases = [(dR1, "60 mm wide, 15 mm deep at the edges, pushed back to the wall\nfront face %.2f mm behind center, %.1f mm deep at center" % (dR1, r0 - dR1))]
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); low = pot.slice_plane([0, 0, zb], [0, 0, -1], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
fig, axs = plt.subplots(2, 1, figsize=(8, 13)); axs = axs.reshape(2, 1)
for j, (d, title) in enumerate(cases):
    pl = plank(d)
    for i, (eye, p) in enumerate([((-1.0, -1.6, 0.9), half), ((0, -1e-3, 1), low)]):
        ax = axs[i, j]; R.FACES.clear(); R.mesh(p, CLEAR); R.mesh(ins, INS)
        R.mesh(pl if i == 0 else pl.slice_plane([0, 0, zb + 1], [0, 0, -1], cap=True), GREEN)
        cam = R.view(ax, eye=eye, pad=6)
        ax.set_title(title if i == 0 else "top view at 37.80 mm, back up", fontsize=13)
        R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
fig.suptitle("Back flush with the pot wall at every height;\nbottom at the insert top (37.80 mm)", fontsize=14)
R.save(fig, sys.argv[2])
print(r0, dR1, r0 - dR1)

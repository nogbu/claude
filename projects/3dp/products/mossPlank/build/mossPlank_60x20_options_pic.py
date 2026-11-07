"""mossPlank 60 x 20 mm options on the 3.5in pot rev10.2 + insert rev4 (plank bottom at the insert top, 37.80 mm).
A: front face 15.74 mm back (20% of inner Ø), back corners cut along the pot wall (wall radius at 37.80 mm, 39.338).
B: plain 60 x 20 rectangle, front face moved forward until the back corners touch the wall."""
import sys, math, numpy as np, trimesh
from shapely.geometry import Polygon, Point, box as sbox
sys.path.insert(0, "/home/user/claude/projects/3dp/scripts")
import render3d as R
from dpcheck import load_3mf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S = sys.argv[1]
def get(p):
    it = load_3mf(p)[0][0]; V = it["V"].copy(); c = (V.min(0) + V.max(0)) / 2; V[:, 0] -= c[0]; V[:, 1] -= c[1]; V[:, 2] -= V[:, 2].min()
    return trimesh.Trimesh(V, it["T"], process=False)
pot = get(S + "/3.5inPot_rev10.2.3mf"); ins = get(S + "/3.5inInsert_rev4.3mf")
ins.vertices[:, 2] = 36.0 - ins.vertices[:, 2] + 1.80
Rin = 39.338; zb = 37.80; ztop = zb + 70; W, T = 60.0, 20.0
dA = 0.4 * Rin
polyA = sbox(-W / 2, dA, W / 2, dA + T).intersection(Point(0, 0).buffer(Rin, 256))
dB = math.sqrt(Rin**2 - (W / 2)**2) - T
polyB = sbox(-W / 2, dB, W / 2, dB + T)
edgeA = math.sqrt(Rin**2 - (W / 2)**2) - dA
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); low = pot.slice_plane([0, 0, zb], [0, 0, -1], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
titles = ["A: back follows the wall\nfront face %.2f mm back (20%% of Ø), 60 wide,\n20 deep at center, %.1f deep at the edges" % (dA, edgeA),
          "B: plain 60 x 20 rectangle\nfront face only %.2f mm back (%.0f%% of Ø)" % (dB, 100 * dB / (2 * Rin))]
fig, axs = plt.subplots(2, 2, figsize=(14, 13))
for j, poly in enumerate([polyA, polyB]):
    for i, (eye, p, z1) in enumerate([((-1.0, -1.6, 0.9), half, ztop), ((0, -1e-3, 1), low, zb + 1)]):
        ax = axs[i, j]; R.FACES.clear(); R.mesh(p, CLEAR); R.mesh(ins, INS)
        R.extrude(poly, "z", zb, z1, GREEN)
        cam = R.view(ax, eye=eye, pad=6)
        ax.set_title(titles[j] if i == 0 else "top view at 37.80 mm, back up", fontsize=13)
        R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
fig.suptitle("60 x 20 mm plank on the 3.5in pot, bottom at the insert top (pot inner Ø 78.68 mm there)", fontsize=15)
R.save(fig, sys.argv[2])
print(dA, edgeA, dB, polyA.area, polyB.area)

"""mossPlank thickness options on the 3.5in pot rev10.2 + insert rev4: front face 20% of the inner diameter
(15.74 mm) behind center, plank bottom at the insert top (37.80 mm), back corners touching the wall."""
import sys, math, numpy as np, trimesh
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
Rin = 39.338; d = 0.4 * Rin; zb = 37.80; ztop = zb + 70
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); low = pot.slice_plane([0, 0, zb], [0, 0, -1], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
fig, axs = plt.subplots(2, 4, figsize=(22, 12))
for j, t in enumerate([5, 10, 15, 20]):
    w = 2 * math.sqrt(Rin**2 - (d + t)**2)
    for i, (eye, p, z1) in enumerate([((-1.0, -1.6, 0.9), half, ztop), ((0, -1e-3, 1), low, zb + 1)]):
        ax = axs[i, j]; R.FACES.clear(); R.mesh(p, CLEAR); R.mesh(ins, INS)
        R.box(-w / 2, w / 2, d, d + t, zb, z1, GREEN)
        cam = R.view(ax, eye=eye, pad=6)
        ax.set_title(("%d mm thick, %.1f mm wide" % (t, w)) if i == 0 else "top view at 37.80 mm, back up", fontsize=13)
        R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=7)
fig.suptitle("Front face 15.74 mm behind center (20% of inner Ø 78.68 mm); back corners touching the wall", fontsize=15)
R.save(fig, sys.argv[2])

"""mossPlank base-fit picture: 3.5in pot rev10.2 (cut in half) with insert rev4 in place and an example plank.
Usage: python3 mossPlank_baseFit_pic.py [dir] [out.png]. [dir] holds 3.5inPot_rev10.2.3mf and 3.5inInsert_rev4.3mf,
built by running their nursery-pots build scripts there. Needs numpy, trimesh, matplotlib and projects/3dp/scripts.
Plank: front face 20% of the pot's inner radius (39.338 mm at the insert top, 37.80 mm) behind center, 10 mm thick,
back corners touching the wall."""
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
ins.vertices[:, 2] = 36.0 - ins.vertices[:, 2] + 1.80          # ceiling up, sitting on the floor
Rin = 39.338; d = 0.2 * Rin; t = 10.0; w = 2 * math.sqrt(Rin**2 - (d + t)**2); zb = 37.80; ztop = 37.8 + 70
GREEN = np.array([0.45, 0.62, 0.40]); CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
fig, axs = plt.subplots(1, 2, figsize=(16, 8.5))
for ax, eye, half in [(axs[0], (-1.0, -1.6, 0.9), True), (axs[1], (0, -1e-3, 1), False)]:
    R.FACES.clear()
    p = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False) if half else pot.slice_plane([0, 0, zb], [0, 0, -1], cap=False)
    R.mesh(p, CLEAR); R.mesh(ins, INS)
    R.box(-w / 2, w / 2, d, d + t, zb, ztop if half else zb + 1, GREEN)
    cam = R.view(ax, eye=eye, pad=6)
    if half:
        R.call(ax, cam, (0, d, ztop), (-60, 30), "example plank, 10 mm thick:\n%.1f mm wide, front face %.2f mm behind center" % (w, d))
        R.call(ax, cam, (0, 0, zb), (-150, 40), "insert top 37.80 mm\n(pot inner Ø %.2f mm there)" % (2 * Rin))
        ax.set_title("3D view, pot cut in half (front half removed)")
    else:
        R.call(ax, cam, (w / 2, d + t, zb + 1), (60, -70), "back corners touch the pot wall\n(plank %.1f mm wide)" % w)
        R.call(ax, cam, (0, d, zb + 1), (-170, 80), "front face %.2f mm behind center\n(20%% of the pot's inner radius)" % d)
        R.call(ax, cam, (0, 0, zb + 1), (120, 90), "pot center")
        ax.set_title("Top view at the insert top (pot cut at 37.80 mm); back is up")
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam)
R.save(fig, sys.argv[2])

"""Picture of rear-fit-test_rev1 as it prints (shelf agreed change 38), drawn from the built 3mf with render3d.load:
the plate from two sides and the glass-end faces with their grooves. Also draws front-fit-test_rev1 (pass its title and label).
Usage: python3 rear-fit-test_rev1_plate.py FILE.3mf [out.png] [title] [label format, e.g. "{v} mm gap"]"""
import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
f = sys.argv[1]; LAB = sys.argv[4] if len(sys.argv) > 4 else "{v} mm"; PIECE = np.array([0.93, 0.62, 0.30])
fig, axes = plt.subplots(1, 3, figsize=(36, 12))
views = [("Plate from the front left, above (front faces on the bed)", (-0.7, -1.0, 0.8)),
         ("Plate from the rear right, above (same three, unlabeled)", (0.8, 1.0, 0.8)),
         ("Glass-end faces (-x): grooves count the step", (-1.0, -0.25, 0.25))]
for ax, (t, eye) in zip(axes, views):
    R.FACES.clear(); objs = R.load(f, PIECE)
    cam = R.view(ax, eye=eye, ppm=8.0, pad=8); ax.set_title(t, fontsize=15, loc="left", fontweight="bold")
    for name, lo, hi in (objs if eye[0] < 0 else []):   # labels only where the glass-end faces show
        sp, g = name.split("_")[1], name.split("_")[2][0]
        p = (lo[0], (lo[1] + hi[1]) / 2, hi[2])
        R.call(ax, cam, p, (0, -60), LAB.format(v=sp) + f", {g} groove{'s' if g != '1' else ''}", color="#555", size=12)
R.source(axes[0], f, cam)
fig.suptitle(sys.argv[3] if len(sys.argv) > 3 else "rear-fit-test_rev1: three left rear pieces cut to the rod ends and lip sleeve, lip rod spacing 31.8 / 32.3 / 32.8. "
             "PETG Basic, on their sides, no supports, sharp (design principles exception). Grooves 1.5 wide, 1.0 deep, 3.0 apart.", fontsize=14)
R.save(fig, sys.argv[2] if len(sys.argv) > 2 else "/mnt/project-files/images/shelf_rearFitTest_rev1_plate.png")

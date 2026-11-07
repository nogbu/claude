"""Why the dovetail slot-fit test piece couldn't print: the groove's upper lip starts in midair. Drawn from the dovetail
parts rail_slottest.py makes (as slotFit_rev1 first built them), in the bar's print position. Whole bar seen from the
strip side and a little below, the lip's underside bright, beside a cut through zone 2 seen end-on with anchor 1
seated and the layers where the lip starts drawn.
Writes T/lip/*.stl and /mnt/project-files/images/rail_slotFit_lip.png."""
import os, sys
import numpy as np, trimesh, manifold3d as m
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE[:HERE.index("/projects/")]
sys.path.insert(0, os.path.join(REPO, "projects/3dp/scripts")); sys.path.insert(0, HERE)
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import rail_slottest as S
from rail_concepts import SW, SLOT_W
T = os.path.join(HERE, "T", "lip"); os.makedirs(T, exist_ok=True)
TAN = np.array([0.80, 0.74, 0.62]); RED = np.array([0.90, 0.15, 0.15]); ORANGE = np.array([0.95, 0.60, 0.25])
SCRIPT = os.path.join(HERE, "rail_slottest.py")

X0, Y0 = 90.5, 128.0; YB = Y0 + S.RD                        # print Y of the bar's back face (strip side)
ZM = S.XS - S.RX0                                        # print Z of the groove's center line, 8.4
def placed(man):                                         # cabinet frame -> the bar's print position (as to_print does for bar(0))
    t = S.tm(man); M = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)
    t.vertices = t.vertices @ M.T + [X0, YB, -S.RX0]; return t
bar = placed(S.bar(0.0))
ZC2 = 37.5                                               # zone 2 center (cabinet z from the beveled end)
anc = placed(S.anchor(ZC2 + S.SLOT_H - S.NECK_H / 2, S.HOOKS[0], 1))                 # anchor 1 seated, head centered in zone 2
def is_lip(t):
    c, n = t.triangles_center, t.face_normals
    return (n[:, 2] < -0.5) & (n[:, 1] < -0.5) & (c[:, 2] > ZM) & (c[:, 1] > YB - 2)  # 45 deg underside of the upper lip
def add(t, col, hi=None, cutx=None):
    V = t.vertices[t.faces]; N = t.face_normals
    for i, (F, nn) in enumerate(zip(V, N)):
        cut = cutx is not None and nn[0] < -0.999 and abs(F[:, 0].mean() - cutx) < 1e-3
        R.FACES.append((F, nn, (RED if hi is not None and hi[i] else col) * (0.8 if cut else 1.0), cut))
def crop(t, x):
    g = (m.Manifold(m.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
         ^ m.Manifold.cube([200, 200, 60]).translate([x, 0, -10])).to_mesh()
    return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts))
bar.export(os.path.join(T, "bar.stl")); anc.export(os.path.join(T, "anchor1_zone2.stl"))

strip = placed(m.Manifold.cube([SW, 1.5, 60]).translate([-SW / 2, -1.5, 0])
               - m.Manifold.cube([SLOT_W, 4, S.SLOT_H]).translate([-SW / 2 + 3.5, -3, ZC2 - S.NECK_H / 2]))   # steel, slot at the neck
GRAY = np.array([0.55, 0.56, 0.58])
fig, axs = plt.subplots(1, 3, figsize=(24, 9), gridspec_kw=dict(width_ratios=[1.25, 1, 1]))
R.FACES.clear(); add(bar, TAN, is_lip(bar))
cam = R.view(axs[0], eye=(-1.0, 0.3, -0.45), pad=4, edge_depth=0.5,
             title="Groove bar as it prints, seen from its beveled end,\nthe strip side and a little below: lip underside red")
R.call(axs[0], cam, (X0 + 40, YB - 0.6, ZM + 3.6), (60, 110), "upper lip's underside, seen\nthrough the groove (holds the anchor head)", color="#c0392b", size=11)
R.call(axs[0], cam, (X0 + 0.5, YB - 2, ZM - 3.0), (-40, -90), "lower lip: builds up from below", color="#2e7d32", size=11)
R.source(axs[0], SCRIPT, cam)

XC = X0 + ZC2                                            # cut through zone 2 (0.3 gap)
FR = (-(YB + 4.5), -(YB - 5.5), ZM - 5.5, ZM + 5.0)
a = S.HN + S.ZONES[1]; zt = ZM + a                       # lip tip height in zone 2
k0 = int(np.floor(zt / 0.3 + 1e-6))                     # first layer holding lip (0-based)
def closeup(ax, parts, title):
    R.FACES.clear()
    for t, col, hi in parts:
        c = crop(t, XC); add(c, col, is_lip(c) if hi else None, XC)
    img, cam2 = R.render((-1.0, 0.0, 0.0), frame=FR, edge_depth=0.3)
    ax.imshow(img); ax.axis("off"); ax.set_title(title, fontsize=13, fontweight="bold")
    return cam2
c1 = closeup(axs[1], [(bar, TAN, True)], "Close-up 1, as it prints: cut through zone 2,\nlooking along the bar from the beveled end")
for k in range(k0 - 1, k0 + 5):
    p, q = R.proj(c1, (XC, YB + 4.4, 0.3 * k)), R.proj(c1, (XC, YB - 5.4, 0.3 * k))
    axs[1].plot([p[0], q[0]], [p[1], q[1]], color="#777", lw=0.6, ls=(0, (2, 2)))
R.call(axs[1], c1, (XC, YB - 0.12, 0.3 * k0 + 0.15), (-60, -150),
       f"layer {k0 + 1} ({0.3 * k0:.1f}-{0.3 * k0 + 0.3:.1f} mm): the lip starts\nas a 0.25 mm strip with nothing under it", color="#c0392b", size=11)
R.call(axs[1], c1, (XC, YB + 1.5, ZM - 1.0), (-10, -60), "open groove mouth\n(strip side)", size=11)
R.call(axs[1], c1, (XC, YB - 1.8, ZM - 3.2), (40, -60), "lower lip: fine", color="#2e7d32", size=11)
R.call(axs[1], c1, (XC, YB - 3.0, ZM + 3.9), (40, 40), "groove ceiling", size=11)
c2 = closeup(axs[2], [(bar, TAN, True), (anc, ORANGE, False), (strip, GRAY, False)],
             "Close-up 2, in use: same cut with anchor 1\nseated and the steel strip")
R.call(axs[2], c2, (XC, YB - 1.0, ZM + 3.3), (70, 60), "upper lip holds\nthe head here", color="#c0392b", size=11)
R.call(axs[2], c2, (XC, YB - 1.6, ZM), (80, -30), "anchor head", color="#c0602a", size=11)
R.call(axs[2], c2, (XC, YB + 3.0, ZM + 1.0), (-40, 120), "anchor neck and drop\n(in and behind the steel)", color="#c0602a", size=11)
R.call(axs[2], c2, (XC, YB + 0.75, ZM - 4.6), (-70, 20), "steel strip", color="#444", size=11)
fig.suptitle("slotFit_rev1 as drawn: the groove's upper lip can't print (the slicer also flags it as floating)", fontsize=15, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.95))
R.save(fig, "/mnt/project-files/images/rail_slotFit_lip.png"); plt.close(fig)

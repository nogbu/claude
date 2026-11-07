"""The groove fix for slotFit_rev1, drawn from the parts slotFit_rev1.py builds (fix) and concepts/rail_slottest.py
(as drawn before, dovetail). Row 1: the plate as it prints and the fixed anchor's head. Row 2: cut through zone 2
with anchor 1 seated on the strip, before and after, same frame. Row 3: the fixed bar and anchor cut as they
print, with the layers. Writes T/hook/*.stl and /mnt/project-files/images/rail_slotFit_hookGroove.png."""
import os, sys
import numpy as np, trimesh, manifold3d as m
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE[:HERE.index("/projects/")]
sys.path.insert(0, os.path.join(REPO, "projects/3dp/scripts")); sys.path.insert(0, os.path.join(REPO, "projects/3dp/products/rail/build"))
sys.path.insert(0, HERE)
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import slotFit_rev1 as S
import rail_slottest as S0
T = os.path.join(HERE, "T", "hook"); os.makedirs(T, exist_ok=True)
TAN = np.array([0.80, 0.74, 0.62]); ORANGE = np.array([0.95, 0.60, 0.25]); GRAY = np.array([0.55, 0.56, 0.58])
RED = np.array([0.90, 0.15, 0.15]); GREEN = np.array([0.25, 0.65, 0.35])
SCRIPT = os.path.join(REPO, "projects/3dp/products/rail/build/slotFit_rev1.py")
assert (S0.XS, S0.RX0, S0.RD, S0.HEAD_D) == (S.XS, S.RX0, S.RD, S.HEAD_D)

X0, Y0 = S.BAR_AT; YB = Y0 + S.RD; ZM = S.XS - S.RX0     # bar's back face (print Y) and groove center (print Z)
ZC2 = 37.5                                               # zone 2 center (cabinet z from the beveled end)
def placed(man):                                         # cabinet frame -> the bar's print position
    t = S.tm(man); M = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)
    t.vertices = t.vertices @ M.T + [X0, YB, -S.RX0]; return t
def crop(t, x):
    g = (m.Manifold(m.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
         ^ m.Manifold.cube([400, 400, 60]).translate([x, -100, -10])).to_mesh()
    return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts))
def add(t, col, cutx=None, hi=None):
    for i, (F, nn) in enumerate(zip(t.vertices[t.faces], t.face_normals)):
        cut = cutx is not None and nn[0] < -0.999 and abs(F[:, 0].mean() - cutx) < 1e-3
        c = hi(F, nn) if hi else None
        R.FACES.append((F, nn, (c if c is not None else col) * (0.8 if cut else 1.0), cut))
strip = placed(m.Manifold.cube([S.SW, 1.5, 60]).translate([-S.SW / 2, -1.5, 0])
               - m.Manifold.cube([S.SLOT_W, 4, S.SLOT_H]).translate([-S.SW / 2 + 3.5, -3, ZC2 - S.NECK_H / 2]))
top = ZC2 + S.SLOT_H - S.NECK_H / 2                     # slot top that centers anchor 1's head in zone 2
old_bar, old_anc = placed(S0.bar(0.0)), placed(S0.anchor(top, S.HOOKS[0], 1))
new_bar, new_anc = placed(S.bar(0.0)), placed(S.anchor(top, S.HOOKS[0], 1))
for n, t in [("old_bar", old_bar), ("old_anchor1", old_anc), ("bar", new_bar), ("anchor1", new_anc), ("strip", strip)]:
    t.export(os.path.join(T, n + ".stl"))
parts = S.build()
for n, t in parts.items():
    t.export(os.path.join(T, n + ".stl"))

fig = plt.figure(figsize=(22, 27))
gs = fig.add_gridspec(3, 2, height_ratios=[0.8, 1, 1])
# ---- row 1: plate as it prints; anchor head close-up ----
ax = fig.add_subplot(gs[0, 0])
R.FACES.clear()
for n, t in parts.items():
    add(t, TAN if n.endswith("bar") else ORANGE)
cam = R.view(ax, eye=(-0.5, -1.0, 0.9), pad=5, edge_depth=0.5, title="Fix, as it prints: bar on its fold side, anchors on their glass side")
R.call(ax, cam, (X0 + 12.5, Y0 + 8, 16.8), (0, 60), "zone 1: 0.5", color="#2e7d32", size=11)
R.call(ax, cam, (X0 + 37.5, Y0 + 8, 16.8), (0, 60), "zone 2: 0.3", color="#2e7d32", size=11)
R.call(ax, cam, (X0 + 62.5, Y0 + 8, 16.8), (0, 60), "zone 3: 0.2", color="#2e7d32", size=11)
R.call(ax, cam, (X0 + 2, Y0 + 3, 8), (-90, 20), "beveled end", color="#c0392b", size=11)
for k, (ax0, ay0) in enumerate(S.ANCHOR_AT):
    R.call(ax, cam, (ax0 + 10, ay0 + 3, 7.8), (0, -70), f"anchor {k + 1}: hook {S.HOOKS[k]}", color="#c0602a", size=11)
R.source(ax, SCRIPT, cam)
ax = fig.add_subplot(gs[0, 1])
a1 = parts["slotFit_rev1_anchor1"]
def hook_faces(F, nn):                                   # anchor 1 in print position: hook face (faces -Y... toward the strip) on top
    c = F.mean(0)
    return RED if (abs(nn[1] + 1) < 1e-3 and c[2] > 7.8 - 1.6 and c[1] > S.ANCHOR_AT[0][1] + 3.6 + 0.5) else None
R.FACES.clear(); add(a1, ORANGE, hi=hook_faces)
cam = R.view(ax, eye=(-0.5, -1.0, 0.9), pad=2, edge_depth=0.3, title="Fixed anchor 1 as it prints, seen from the strip side\n(hook face red)")
ay = S.ANCHOR_AT[0][1] + 3.6                             # print Y of the strip face (anchor Y = cab y)
R.call(ax, cam, (S.ANCHOR_AT[0][0] + 5, ay + S.T_A, 7.0), (-40, 80), "hook face (holds the rail on)", color="#c0392b", size=11)
R.call(ax, cam, (S.ANCHOR_AT[0][0] + 5, ay + 0.8, 7.0), (-120, 30), "notch: the bar's lip\nslides in here", size=11)
R.call(ax, cam, (S.ANCHOR_AT[0][0] + 3, ay + 0.6, 0.3), (-60, -60), "foot on the bed, then 45 deg up", size=11)
R.call(ax, cam, (S.ANCHOR_AT[0][0] + 10, ay - 2.6, 4.0), (90, -40), "neck and drop\n(unchanged)", color="#c0602a", size=11)
# ---- row 2: mounted cuts, before and after, one frame ----
XC = X0 + ZC2
FR = (-(YB + 4.5), -(YB - 5.5), ZM - 6.0, ZM + 6.6)
def mounted(ax, bar, anc, title):
    R.FACES.clear()
    for t, col in [(bar, TAN), (anc, ORANGE), (strip, GRAY)]:
        add(crop(t, XC), col, XC)
    img, c = R.render((-1.0, 0.0, 0.0), frame=FR, edge_depth=0.3)
    ax.imshow(img); ax.axis("off"); ax.set_title(title, fontsize=14, fontweight="bold"); return c
ax0, ax1 = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
c0 = mounted(ax0, old_bar, old_anc, "As drawn (dovetail), in use: cut through zone 2\nlooking along the bar; left is the strip, up is up as the bar prints")
c1 = mounted(ax1, new_bar, new_anc, "Fix (hook groove), in use: same cut, same frame")
R.call(ax0, c0, (XC, YB - 0.4, ZM + 3.3), (70, 70), "upper lip: starts in midair\nwhen the bar prints", color="#c0392b", size=11)
u = lambda v: ZM + v                                     # print Z of a cabinet u (across the strip) in the bar's frame
R.call(ax1, c1, (XC, YB - 0.5, u(-3.5)), (-130, -90), "lip: builds up from the\ngroove floor", color="#2e7d32", size=11)
R.call(ax1, c1, (XC, YB - (S.T_A - 0.3), u(-3.2)), (120, -110), "hook face: gap 0.5 / 0.3 / 0.2\nby zone (holds the rail on)", color="#c0392b", size=11)
R.call(ax1, c1, (XC, YB - 0.8, u(-2.55)), (150, -20), "lip top: 0.3 (one layer)", size=11)
R.call(ax1, c1, (XC, YB - 2.0, u(-4.05)), (140, -40), "groove floor: 0.3", size=11)
R.call(ax1, c1, (XC, YB - 1.8, u(4.5)), (90, 70), f"roof: 45 deg, {S.R_CL:.2f} clear\n(not a fit face)", size=11)
R.call(ax1, c1, (XC, YB + 2.5, u(4.2)), (-60, 60), "steel strip", color="#444", size=11)
# ---- row 3: the fix cut as it prints, with layers ----
ax0, ax1 = fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])
def layers(ax, c, x, y0, y1, z0, z1):
    for k in range(int(z0 / 0.3), int(z1 / 0.3) + 1):
        p, q = R.proj(c, (x, y0, 0.3 * k)), R.proj(c, (x, y1, 0.3 * k))
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#999", lw=0.5, ls=(0, (2, 2)))
R.FACES.clear(); add(crop(new_bar, XC), TAN, XC)
cb = R.render((-1.0, 0.0, 0.0), frame=(-(YB + 1.0), -(YB - 6.0), ZM - 5.2, ZM + 6.6), edge_depth=0.3)
ax0.imshow(cb[0]); ax0.axis("off"); cb = cb[1]
ax0.set_title("Fixed bar as it prints: cut through zone 2 (bed below)", fontsize=14, fontweight="bold")
layers(ax0, cb, XC, YB + 0.9, YB - 5.9, ZM - 5.0, ZM + 6.3)
R.call(ax0, cb, (XC, YB - 0.5, u(-2.7)), (-100, -80), "lip top", size=11)
R.call(ax0, cb, (XC, YB - 2.0, u(4.0)), (110, 60), "roof rises 45 deg from the\ngroove bottom: no bridge", size=11)
XA = S.ANCHOR_AT[0][0] + 5.5                            # anchor 1 cut 5 mm from its end: head only, away from the neck
R.FACES.clear(); add(crop(a1, XA), ORANGE, XA)
ca = R.render((-1.0, 0.0, 0.0), frame=(-(ay + 3.4), -(ay - 4.0), -0.6, 8.4), edge_depth=0.3)
ax1.imshow(ca[0]); ax1.axis("off"); ca = ca[1]
ax1.set_title("Fixed anchor 1 as it prints: cut through the head away\nfrom the neck (bed below; strip side on the right)", fontsize=14, fontweight="bold")
layers(ax1, ca, XA, ay - 3.9, ay + 3.3, 0.0, 7.8)
R.call(ax1, ca, (XA, ay + 0.8, 0.15), (-60, -50), "foot on the bed", size=11)
R.call(ax1, ca, (XA, ay + 2.0, 1.5), (-120, 30), "45 deg up from the foot", size=11)
R.call(ax1, ca, (XA, ay + 2.2, 7.8), (-70, 50), "hook on top", color="#c0392b", size=11)
R.call(ax1, ca, (XA, ay + 0.8, 6.6), (90, 50), "notch open upward", size=11)
R.call(ax1, ca, (XA, ay - 2.6, 3.9), (80, -60), "neck and drop,\nbeyond the cut", color="#c0602a", size=11)
fig.suptitle("slotFit_rev1 groove fix: a square hook on the fold side replaces the dovetail (agreed 2026-10-09)",
             fontsize=16, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.975))
R.save(fig, "/mnt/project-files/images/rail_slotFit_hookGroove.png"); plt.close(fig)

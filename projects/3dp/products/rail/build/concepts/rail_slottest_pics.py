"""Pictures of the slot-fit test piece, drawn from the STLs rail_slottest.py writes into ./T (crops cut from them).
Fig 1: the plate as it prints, each anchor's hook cut down the slot center, and each groove zone cut level with
the neck. Fig 2: on the strip, assembled and pulled off. Every row of matched panels shares one frame (same scale)."""
import os, sys
import numpy as np, trimesh, manifold3d as m
sys.path.insert(0, "/home/claude/claude/projects/3dp/scripts")
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from rail_concepts import XS, SLOT_H
from rail_slottest import HOOKS, ZONES, ZL, NECK_H, HEAD_D, RD, RX1
HERE = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(HERE, "T")
OUT = "/mnt/project-files/images"
GRAY = np.array([0.55, 0.56, 0.58]); ORANGE = np.array([0.95, 0.60, 0.25]); TAN = np.array([0.80, 0.74, 0.62])
LOWER = [389.8, 355.0, 320.2]                   # slot tops holding anchors 1, 2, 3
ZC = LOWER[0] - SLOT_H + NECK_H / 2            # anchor 1's neck center = its head center

def man(path):
    t = trimesh.load(path); return m.Manifold(m.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
def put(name, col, lo, hi, shift=(0, 0, 0)):
    """Crop T/name.stl to [lo, hi] in final coordinates (after shift) and add it to the picture."""
    s = np.asarray(shift, float)
    c = man(os.path.join(T, name + ".stl")) ^ m.Manifold.cube(list(np.subtract(hi, lo))).translate(list(np.subtract(lo, s)))
    if c.is_empty():
        return
    g = c.translate(list(s)).to_mesh(); q = os.path.join(T, "crop", name + ".stl"); os.makedirs(os.path.dirname(q), exist_ok=True)
    trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts)).export(q)
    R.load(q, col)
def row(axs, scenes, eye, pad=1.5, edge=0.3):
    """Render each scene into its axis in one shared frame; returns the cams."""
    frames = []
    for sc in scenes:
        R.FACES.clear(); sc(); frames.append(R.fit(eye, pad))
    fr = (min(f[0] for f in frames), max(f[1] for f in frames), min(f[2] for f in frames), max(f[3] for f in frames))
    cams = []
    for ax, sc in zip(axs, scenes):
        R.FACES.clear(); sc(); img, cam = R.render(eye, frame=fr, edge_depth=edge)
        ax.imshow(img); ax.axis("off"); cams.append(cam)
    return cams

# ================= Fig 1: what prints, hooks and groove zones =================
fig = plt.figure(figsize=(16, 22))
gs = fig.add_gridspec(3, 3, height_ratios=[1.25, 1.0, 0.8])
ax = fig.add_subplot(gs[0, :])
R.FACES.clear(); R.load(os.path.join(T, "print_bar.stl"), TAN)
for k in range(3):
    R.load(os.path.join(T, f"print_anchor{k + 1}.stl"), ORANGE)
cam = R.view(ax, eye=(-0.55, -1.0, 0.95), pad=6, edge_depth=0.5,
             title="As it prints: groove bar and three anchors, all on their side (no supports)")
for i, c in enumerate(ZONES):
    R.call(ax, cam, (90 + ZL * (i + 0.5), 108, 16.8), (0, 80), f"zone {i + 1}: {c} gap", color="#2e7d32", size=12)
R.call(ax, cam, (92.5, 102.5, 10), (-130, 60), "beveled end (marked end)", color="#c0392b", size=12)
R.call(ax, cam, (90 + 2 * ZL, 100, 12), (150, 30), "V marks at zone ends", size=11)
for k in range(3):
    R.call(ax, cam, (90 + 27 * k + 18, 80, 7.8), (0, -60), f"anchor {k + 1}: {k + 1} notch{'es' if k else ''}, hook {HOOKS[k]}",
           color="#c0602a", size=11)
R.source(ax, os.path.join(HERE, "rail_slottest.py"), cam)

# hooks: each anchor seated in its slot, cut down the slot center, shifted to one height so they share a frame
def hook_scene(k):
    t = LOWER[k]; s = (0, 0, LOWER[0] - t)           # crop box in final coordinates, at anchor 1's slot
    lo, hi = (XS, -7, LOWER[0] - 9), (XS + 12, 6, LOWER[0] + 5)
    return lambda: (put("strip", R.BONE * 0.85, lo, hi, s), put(f"anchor{k + 1}", ORANGE, lo, hi, s))
axs = [fig.add_subplot(gs[1, k]) for k in range(3)]
cams = row(axs, [hook_scene(k) for k in range(3)], eye=(-1.0, 0.02, 0.02), pad=1.0)
for k, (a, c) in enumerate(zip(axs, cams)):
    a.set_title(f"Anchor {k + 1}: hook {HOOKS[k]} = neck {NECK_H} + drop {HOOKS[k] - NECK_H:.1f}", fontsize=13, fontweight="bold")
    zb = LOWER[0] - SLOT_H
    R.dim(a, c, (XS, -3.6, zb - (HOOKS[k] - NECK_H)), (XS, -3.6, zb + NECK_H), (0, -1.6, 0), text=f"{HOOKS[k]}")
    R.call(a, c, (XS, -0.75, LOWER[0] + 3), (-70, -10), "steel strip\n(cut)", color="#444", size=10)
    R.call(a, c, (XS, -0.75, LOWER[0] - SLOT_H / 2), (-80, -60), f"slot, {SLOT_H} tall as drawn\n(reads 3.3-4)", color="#444", size=10)
    if k == 0:
        R.call(a, c, (XS, 1.4, LOWER[0] - 8), (-30, -45), "head (cut)", color="#c0602a", size=10)
        R.call(a, c, (XS, -2.6, LOWER[0] - SLOT_H - 0.6), (-70, -40), "drop behind\nthe steel", color="#c0602a", size=10)

# groove zones: the bar placed so anchor 1 sits in zone i, cut level with its neck, seen from above
def zone_scene(i):
    lo, hi = (XS - 13, -6.5, ZC - 12), (XS + 13, RD + 1, ZC)
    return lambda: (put("strip", R.BONE * 0.85, lo, hi), put("anchor1", ORANGE, lo, hi), put(f"bar_zone{i + 1}", TAN, lo, hi))
axs = [fig.add_subplot(gs[2, k]) for k in range(3)]
cams = row(axs, [zone_scene(i) for i in range(3)], eye=(0.0, -0.02, 1.0), pad=1.0)
for i, (a, c) in enumerate(zip(axs, cams)):
    a.set_title(f"Zone {i + 1}, {ZL * i:.0f}-{ZL * (i + 1):.0f} mm from the bevel:\n{ZONES[i]} gap on the 45 deg faces",
                fontsize=13, fontweight="bold")
    if i == 0:
        R.call(a, c, (XS + 3.9, 0.6, ZC), (70, 30), "dovetail faces", color="#2e7d32", size=10)
        R.call(a, c, (XS, -2.6, ZC), (-80, -30), "neck and drop\nthrough the slot", color="#c0602a", size=10)
        R.call(a, c, (XS + 9, 8, ZC), (60, 40), "bar (cut)", size=10)
fig.suptitle("Slot-fit test piece for the rail (layout A): fillets drawn as modeled", fontsize=15, fontweight="bold")
fig.tight_layout(rect=(0, 0.035, 1, 0.975))
fig.text(0.03, 0.006, "How it prints: the bar lies on its fold-side face (16.8 tall) and the anchors lie on one side (7.8 tall), as the rail and its anchors will,\n"
         "so hook profiles, notches, groove depth and marks are in the layer outline and hook loads run along the layers. Rail shown light; prints black.", fontsize=11)
R.save(fig, os.path.join(OUT, "rail_slotTest_parts.png")); plt.close(fig)

# ================= Fig 2: on the strip =================
fig, axs = plt.subplots(1, 2, figsize=(15, 13))
LO, HI = (-30, -30, 290), (30, 90, 470)
def mounted(pull):
    return lambda: (put("strip", GRAY, LO, HI), [put(f"anchor{k + 1}", ORANGE, LO, HI) for k in range(3)],
                    put("bar_zone1", TAN, LO, HI, (0, pull, 0)))
c1 = row([axs[0]], [mounted(0)], eye=(-1.0, 1.6, 0.45), pad=4, edge=0.5)[0]
c2 = row([axs[1]], [mounted(45)], eye=(1.0, -0.6, 0.4), pad=4, edge=0.5)[0]
axs[0].set_title("Bar slid down over anchor 1, which sits in zone 1\n(seen from the shelf side)", fontsize=13, fontweight="bold")
axs[1].set_title("Bar pulled 45 mm off the strip, seen from behind:\nanchors hooked in the three lower slots", fontsize=13, fontweight="bold")
zb0 = ZC - ZL / 2
R.call(axs[0], c1, (XS - 3, RD, zb0 + 2.5), (-110, -20), "beveled end down", color="#c0392b", size=11)
R.call(axs[0], c1, (XS, 2.8, LOWER[1] - 8), (-110, 0), "anchor 2", color="#c0602a", size=11)
R.call(axs[0], c1, (XS, 2.8, LOWER[2] - 8), (-110, 0), "anchor 3", color="#c0602a", size=11)
for k in range(3):
    R.call(axs[1], c2, (XS, -2.6, LOWER[k] - SLOT_H), (100, -10), f"anchor {k + 1} drop", color="#c0602a", size=11)
R.call(axs[1], c2, (XS + 3.5, 45, zb0 + 60), (-90, 20), "groove, 3 zones", size=11)
R.source(axs[0], os.path.join(HERE, "rail_slottest.py"), c1)
fig.suptitle("Slot-fit test piece on the lower slot group (strip drawn from unicoly values; slot 3.6 tall as drawn)", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.96)); R.save(fig, os.path.join(OUT, "rail_slotTest_mounted.png")); plt.close(fig)

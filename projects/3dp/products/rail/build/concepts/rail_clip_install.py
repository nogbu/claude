"""Concept A clip install/removal beside the side glass, drawn from the STLs rail_concepts.py writes.
The glass is added here as a slab whose inner face lines up with the strip's glass-side edge (x 8.5):
its position and thickness are not measured. Every clip move is in Y (in/out) or Z (up/down), parallel to the glass."""
import os, sys
import numpy as np, trimesh, manifold3d as m
sys.path.insert(0, "/home/claude/claude/projects/3dp/scripts")
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/project-files/images"
GRAY = np.array([0.55, 0.56, 0.58]); BLUE = np.array([0.55, 0.70, 0.90]); ORANGE = np.array([0.95, 0.60, 0.25])
TAN = np.array([0.80, 0.74, 0.62]); GREEN = np.array([0.55, 0.80, 0.55]); GLASS = np.array([0.72, 0.86, 0.88])
XS = -0.75
GLASS_X0, GLASS_T = 8.5, 5.0     # assumed: inner face at the strip's glass edge, 5 thick (not measured)

def man(path):
    t = trimesh.load(path); return m.Manifold(m.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
def put(sub, name, col, lo, hi, shift=(0, 0, 0)):
    s = np.asarray(shift, float)
    c = man(os.path.join(HERE, sub, name + ".stl")) ^ m.Manifold.cube(list(np.subtract(hi, lo))).translate(list(np.subtract(lo, s)))
    if c.is_empty():
        return
    g = c.translate(list(s)).to_mesh()
    q = os.path.join(HERE, sub, "crop", name + ".stl"); os.makedirs(os.path.dirname(q), exist_ok=True)
    trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts)).export(q)
    R.load(q, col)

g = m.Manifold.cube([GLASS_T, 85, 400]).translate([GLASS_X0, -20, 100]).to_mesh()
trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts)).export(os.path.join(HERE, "A", "glass.stl"))

LO, HI = (-30, -25, 262), (20, 80, 340)
CLIP_LO, CLIP_HI = (-30, -25, 270), (20, 80, 312)      # the 12in clip only
def scene(clip_shift, glass=True):
    R.FACES.clear()
    put("A", "strip", GRAY, LO, HI); put("A", "anchors", ORANGE, LO, HI)
    put("A", "rail_p2", TAN, LO, HI)
    if glass:
        put("A", "glass", GLASS, LO, HI)
    put("A", "clips", GREEN, np.add(CLIP_LO, clip_shift), np.add(CLIP_HI, clip_shift), clip_shift)

STEPS = [((0, 22, 3), "1. Hold it 3 mm high in front of its\nnotch, then push it straight in"),
         ((0, 0, 3), "2. Pushed in: now let it\ndrop 3 mm"),
         ((0, 0, 0), "3. Seated: the hook sits in\nthe pocket below the lip")]
EYE = (-1.0, 1.3, 0.55)          # from the shelf side, over the cabinet interior, looking toward the glass
fig, axs = plt.subplots(2, 2, figsize=(15, 15))
frames = []
for s, _ in STEPS:
    scene(s); frames.append(R.fit(EYE, 4))
fr = (min(f[0] for f in frames), max(f[1] for f in frames), min(f[2] for f in frames), max(f[3] for f in frames))
for ax, (s, t) in zip(axs.flat[:3], STEPS):
    scene(s)
    img, cam = R.render(EYE, frame=fr, edge_depth=0.5); ax.imshow(img); ax.axis("off")
    ax.set_title(t, fontsize=13, fontweight="bold")
    R.call(ax, cam, (GLASS_X0 + GLASS_T, 60, 330), (60, 30), "side glass", color="#2a7f8a", size=10)
    tip = np.add((XS, 31, 300), s)
    if s[1] > 0:
        a, b = R.proj(cam, tip), R.proj(cam, np.subtract(tip, (0, 14, 0)))
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.5))
    elif s[2] > 0:
        a, b = R.proj(cam, tip), R.proj(cam, np.subtract(tip, (0, 0, 3)))
        ax.annotate("", xy=b, xytext=(a[0], a[1] - 40), arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.5))
    if ax is axs[0, 0]:
        R.source(ax, os.path.join(HERE, "rail_concepts.py"), cam)
# plan view from above: every move stays on the shelf side of the glass
ax = axs[1, 1]
scene(STEPS[0][0])
cam = R.view(ax, eye=(0.0, -0.02, 1.0), pad=4, title="Seen from above (clip at step 1):\nit moves along the glass, never into it", edge_depth=0.5)
a, b = R.proj(cam, (XS, 45, 315)), R.proj(cam, (XS, 31, 315))
ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.5))
R.call(ax, cam, (GLASS_X0 + GLASS_T / 2, 50, 340), (-60, 40), "side glass", color="#2a7f8a", size=10)
R.call(ax, cam, (XS - 5, 40, 315), (-90, 0), "clip", color="#2e7d32", size=10)
R.call(ax, cam, (XS - 5, 8, 340), (-90, 20), "rail", size=10)
R.call(ax, cam, (-5, -0.75, 340), (-90, -30), "strip", color="#444", size=10)
fig.suptitle("Concept A: putting a clip on next to the side glass (removal is the same steps backward: lift 3, pull straight out)\n"
             "Glass drawn with its inner face at the strip's edge, 0.75 from the rail; its position and thickness aren't measured. Fillets not drawn.",
             fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.95)); R.save(fig, os.path.join(OUT, "rail_conceptA_clipInstall.png")); plt.close(fig)

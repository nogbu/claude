"""Clip grip next to the side glass: the braced clip as drawn vs a plain-ledge clip, same views and scale.
Drawn from the STLs rail_concepts.py writes; glass as in rail_clip_install.py (position not measured)."""
import os, sys
import numpy as np, trimesh, manifold3d as m
sys.path.insert(0, "/home/claude/claude/projects/3dp/scripts")
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/project-files/images"
GRAY = np.array([0.55, 0.56, 0.58]); ORANGE = np.array([0.95, 0.60, 0.25])
TAN = np.array([0.80, 0.74, 0.62]); GREEN = np.array([0.55, 0.80, 0.55]); GLASS = np.array([0.72, 0.86, 0.88])
XS, RD, POS = -0.75, 16.0, 304.8

def man(path):
    t = trimesh.load(path); return m.Manifold(m.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
def put(name, col, lo, hi):
    c = man(os.path.join(HERE, "A", name + ".stl")) ^ m.Manifold.cube(list(np.subtract(hi, lo))).translate(list(lo))
    if c.is_empty():
        return
    g = c.to_mesh(); q = os.path.join(HERE, "A", "crop", name + ".stl"); os.makedirs(os.path.dirname(q), exist_ok=True)
    trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts)).export(q)
    R.load(q, col)
def scene(clipfile, lo, hi, glass=True):
    R.FACES.clear()
    put("strip", GRAY, lo, hi); put("anchors", ORANGE, lo, hi); put("rail_p2", TAN, lo, hi)
    if glass:
        put("glass", GLASS, lo, hi)
    put(clipfile, GREEN, np.maximum(lo, (-30, -25, 270)), np.minimum(hi, (20, 80, 312)))

COLS = [("clips", "As drawn: brace runs to the ledge tip"), ("clip_plain12", "Fix: plain ledge, no brace")]
VIEWS = [((-1.0, 1.3, 0.55), (-30, -25, 262), (20, 60, 340), "From the open side (glass behind), shelf off"),
         ((-1.0, 0.12, 0.08), (XS, -25, 262), (20, 60, 340), "Cut down the middle, from the open side")]
fig, axs = plt.subplots(2, 2, figsize=(15, 15))
for r, (eye, lo, hi, rt) in enumerate(VIEWS):
    frames = []
    for f, _ in COLS:
        scene(f, lo, hi, glass=(r == 0)); frames.append(R.fit(eye, 4))
    fr = (min(a[0] for a in frames), max(a[1] for a in frames), min(a[2] for a in frames), max(a[3] for a in frames))
    for c, (f, ct) in enumerate(COLS):
        ax = axs[r, c]; scene(f, lo, hi, glass=(r == 0))
        img, cam = R.render(eye, frame=fr, edge_depth=0.5); ax.imshow(img); ax.axis("off")
        ax.set_title((ct + "\n\n" if r == 0 else "") + rt, fontsize=13, fontweight="bold")
        if r == 1:
            top, under = (XS, RD + 11, POS), (XS, RD + 11, POS - 6)
            if c == 0:
                under = (XS, RD + 11, POS - 10.5)          # the brace face below the ledge
            t2, u2 = np.array(R.proj(cam, top)), np.array(R.proj(cam, under))
            ax.annotate("thumb", xy=t2, xytext=t2 + (0, -110), color="#c0392b", fontsize=12, fontweight="bold", ha="center",
                        arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.5))
            if c == 1:
                ax.annotate("finger under the ledge:\nlift 3, pull out", xy=u2, xytext=u2 + (-330, 170), color="#c0392b", fontsize=12,
                            fontweight="bold", ha="center", arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.5))
            else:
                ax.annotate("finger has only the\nsloped brace to push on", xy=u2, xytext=u2 + (-330, 170), color="#c0392b", fontsize=12,
                            fontweight="bold", ha="center", arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=2.5))
            if c == 1:
                R.call(ax, cam, (XS, RD + 3, POS - 20), (-150, -70), "plate 6 thick\n(was 3 + brace)", color="#2e7d32", size=11)
                R.call(ax, cam, (XS, RD + 12, POS - 3), (-150, 60), "ledge 6 thick, 9 of\nunderside to pinch", color="#2e7d32", size=11)
        else:
            R.call(ax, cam, (8.5 + 5, 50, 335), (70, 30), "side glass", color="#2a7f8a", size=10)
        if r == 0 and c == 0:
            R.source(ax, os.path.join(HERE, "rail_concepts.py"), cam)
fig.suptitle("Gripping a clip with the glass on one side: same views and scale (12in clip, fillets not drawn)\n"
             "Glass drawn with its inner face at the strip's edge; its position and thickness aren't measured.", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.95)); R.save(fig, os.path.join(OUT, "rail_conceptA_clipGrip.png")); plt.close(fig)

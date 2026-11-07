"""Side-by-side pictures of rail concepts A and C, drawn from the STLs rail_concepts.py writes.
Every row draws both concepts from the same eye, the same crop and the same frame (same scale), with the
strip and its slots in every panel so each shows how it mounts. Shelves at 12in, 34in and 44in in both."""
import os, sys
import numpy as np, trimesh, manifold3d as m
sys.path.insert(0, "/home/claude/claude/projects/3dp/scripts")
import render3d as R
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/project-files/images"
GRAY = np.array([0.55, 0.56, 0.58]); BLUE = np.array([0.55, 0.70, 0.90]); ORANGE = np.array([0.95, 0.60, 0.25])
TAN = np.array([0.80, 0.74, 0.62]); GREEN = np.array([0.55, 0.80, 0.55])
XS = -0.75
LEDGES = [304.8, 863.6, 1117.6]
EYE = (-1.0, 1.6, 0.45)        # assembled and pulled-off views: from the shelf side, toward the glass
EYE_CUT = (-1.0, 0.3, 0.2)     # sections: looking at the cut face down the slot center
EYE_BACK = (1.0, -0.6, 0.4)    # pulled-off views: from behind the strip, so hooks and groove on the parts' backs show

def man(path):
    t = trimesh.load(path); return m.Manifold(m.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
def put(sub, name, col, lo, hi, shift=(0, 0, 0)):
    """Crop one model file to [lo, hi] in final coordinates (after shift) and add it to the picture."""
    s = np.asarray(shift, float)
    c = man(os.path.join(HERE, sub, name + ".stl")) ^ m.Manifold.cube(list(np.subtract(hi, lo))).translate(list(np.subtract(lo, s)))
    if c.is_empty():
        return
    g = c.translate(list(s)).to_mesh()
    q = os.path.join(HERE, sub, "crop", name + ".stl"); os.makedirs(os.path.dirname(q), exist_ok=True)
    trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts)).export(q)
    R.load(q, col)

PIECES = [("rail_bottom", R.BONE), ("rail_p2", TAN), ("rail_p3", R.BONE), ("rail_p4", TAN), ("rail_p5", R.BONE), ("rail_top", TAN)]
def scene_A(lo, hi, pull=0.0):
    R.FACES.clear()
    put("A", "strip", GRAY, lo, hi); put("A", "buttons", BLUE, lo, hi); put("A", "anchors", ORANGE, lo, hi)
    for n, c in PIECES:
        put("A", n, c, lo, hi, (0, pull, 0))
    put("A", "clips", GREEN, lo, hi, (0, pull, 0))
def scene_C(lo, hi, pull=0.0):
    R.FACES.clear()
    put("C", "strip", GRAY, lo, hi); put("C", "buttons", BLUE, lo, hi)
    put("C", "brackets", GREEN, lo, hi, (0, pull, 0))

def pair(axA, axC, lo, hi, eye, pull=0.0, pad=4.0, edge=5.0):
    """Render A and C in one frame so both panels share scale and position."""
    scene_A(lo, hi, pull); fa = R.fit(eye, pad)
    scene_C(lo, hi, pull); fc = R.fit(eye, pad)
    fr = (min(fa[0], fc[0]), max(fa[1], fc[1]), min(fa[2], fc[2]), max(fa[3], fc[3]))
    cams = []
    for ax, scene in ((axA, scene_A), (axC, scene_C)):
        scene(lo, hi, pull)
        img, cam = R.render(eye, frame=fr, edge_depth=edge)
        ax.imshow(img); ax.axis("off"); cams.append(cam)
    return cams

def head(ax, text):
    ax.set_title(text, fontsize=14, fontweight="bold")

# ---------- 1: whole corner ----------
fig, (aA, aC) = plt.subplots(1, 2, figsize=(12, 16))
lo, hi = (-40, -30, -1), (40, 90, 1500)
cA, cC = pair(aA, aC, lo, hi, EYE, pad=15)
head(aA, "A: rail on anchors"); head(aC, "C: height clips, no rail")
for ax, cam, yl in ((aA, cA, 31), (aC, cC, 21)):
    for z, t in zip(LEDGES, ("shelf at 12in", "shelf at 34in", "shelf at 44in")):
        R.call(ax, cam, (XS, yl, z), (95, 0), t, color="#2e7d32", size=11)
    R.call(ax, cam, (8.5, 1, 1359), (-85, 0), "glass button", color="#1f5fa8", size=10)
    R.call(ax, cam, (-8.5, 0, 1250), (-85, 0), "slotted strip", color="#444", size=10)
R.call(aA, cA, (XS, 16, 560), (90, 0), "6 rail pieces\nstanding on the floor", size=11)
R.source(aA, os.path.join(HERE, "rail_concepts.py"), cA)
fig.suptitle("Whole corner, same view and scale (plain-ledge clips; fillets not drawn; parts print black, drawn light so edges show)", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.97)); R.save(fig, os.path.join(OUT, "rail_compare_corner_plainLedge.png")); plt.close(fig)

# ---------- 2: close-ups at the lower slots and the 12in shelf ----------
fig, axs = plt.subplots(3, 2, figsize=(14, 21))
lo, hi = (-30, -25, 245), (30, 90, 402)
rows = []
rows.append(pair(axs[0, 0], axs[0, 1], lo, hi, EYE, edge=0.5))
rows.append(pair(axs[1, 0], axs[1, 1], lo, hi, EYE_BACK, pull=50, edge=0.5))
lo_c = (XS, -25, 245)
rows.append(pair(axs[2, 0], axs[2, 1], lo_c, hi, EYE_CUT, edge=0.5))
head(axs[0, 0], "A: rail on anchors\n\nMounted (lower slot group, 12in shelf)"); head(axs[0, 1], "C: height clips, no rail\n\nMounted (lower slot group, 12in shelf)")
head(axs[1, 0], "Pulled 50 mm off the strip, seen from behind"); head(axs[1, 1], "Pulled 50 mm off the strip, seen from behind")
head(axs[2, 0], "Cut down the slot center"); head(axs[2, 1], "Cut down the slot center")
(cA, cC) = rows[0]
for ax, cam, yl in ((axs[0, 0], cA, 31), (axs[0, 1], cC, 21)):
    R.call(ax, cam, (XS, yl, 304.8), (90, 30), "ledge top = shelf height", color="#2e7d32", size=10)
R.call(axs[0, 1], cC, (8.5, 1, 255), (-90, -10), "glass button", color="#1f5fa8", size=10)
R.call(axs[0, 0], cA, (7.75, 8, 255), (-110, -10), "glass button hidden\nin the rail's back relief", color="#1f5fa8", size=10)
R.call(axs[0, 0], cA, (XS, 16, 360), (90, 0), "rail", size=10)
(cA, cC) = rows[1]
R.call(axs[1, 0], cA, (XS, -2.6, 353), (90, 20), "anchors stay\nhooked in the slots", color="#c0602a", size=10)
R.call(axs[1, 0], cA, (XS + 3.5, 50, 300), (-100, 0), "groove up the\nrail's back", size=10)
R.call(axs[1, 1], cC, (XS, 50 - 2.6, 386), (-100, 20), "load hook", color="#2e7d32", size=10)
R.call(axs[1, 1], cC, (XS, 50 - 2.6, 351.5), (-100, -20), "keeper hook", color="#2e7d32", size=10)
for ax, cam in ((axs[1, 0], cA), (axs[1, 1], cC)):
    R.call(ax, cam, (3.0, -1.5, 270), (90, -10), "back of the strip", color="#444", size=10)
(cA, cC) = rows[2]
R.call(axs[2, 0], cA, (XS, -2.6, 384.8), (-90, 30), "anchor drop\nbehind the steel", color="#c0602a", size=10)
R.call(axs[2, 0], cA, (XS, 10.5, 293), (100, -30), "clip hook in\na 3 mm pocket", color="#2e7d32", size=10)
R.call(axs[2, 1], cC, (XS, -2.6, 386.2), (-90, 30), "load hook\nbehind the steel", color="#2e7d32", size=10)
R.call(axs[2, 1], cC, (XS, -2.6, 351.7), (-90, -30), "keeper hook", color="#2e7d32", size=10)
R.source(axs[2, 0], os.path.join(HERE, "rail_concepts.py"), cA)
fig.suptitle("Close-ups: each row is the same view, crop and scale for both (fillets not drawn)", fontsize=13)
fig.tight_layout(rect=(0, 0.04, 1, 0.97))
fig.text(0.03, 0.01, "How they print: rail pieces, clips and anchors all lie on their side, so every hook, notch, pocket and groove is in the layer\n"
         "outline (no supports) and hook loads run along the layers. A's 304.8 top piece prints diagonally.", fontsize=11)
R.save(fig, os.path.join(OUT, "rail_compare_closeups_plainLedge.png")); plt.close(fig)

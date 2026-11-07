"""Shelf body footprint options (open decision 6): one side band, front piece from front-piece_model.build()."""
import importlib.util, os, sys, numpy as np, manifold3d as m, trimesh, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("front_piece_model", os.path.join(HERE, "front-piece_model.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
fp, d = F.build(); OF, OR = d["OF"], d["OR"]
X0, ZB, TOP, RC, ROD, WIRE, WB = F.X0, F.ZB, F.TOP, F.RC, F.ROD, F.WIRE, F.WB
YR = 290.0; LIPZ = RC - 32.3; DEPTH = 50.0          # rear corner rod; lip outer rod; pad depth from the front face
def mirror_rear(man): return man.mirror([0, 1, 0]).translate([0, YR, 0])
def rear_placeholder(depth):
    b = F.box(X0, 0, YR - depth + OF, YR + OF, ZB, TOP) + F.box(-15, 0, YR + OF - 13, YR + OF, LIPZ - 6, ZB)
    return b
def pieces(opt):
    front = fp; rear = rear_placeholder(OF + OR)
    if opt == "B":
        front = front + F.box(X0, 0, -OF, -OF + DEPTH, ZB, TOP); rear = rear_placeholder(DEPTH)
    if opt == "C":
        rail = F.box(X0, X0 + 4, -OF, YR + OF, ZB, TOP)
        bars = [F.box(X0, F.W1, y - 2, y + 2, F.TOP - 3.1, F.TOP) for y in np.arange(25.3, YR - 5, 25.3)]
        return F.tm(front), F.tm(rear_placeholder(OF + OR)), F.tm(rail + m.Manifold.batch_boolean(bars, m.OpType.Add) - front)
    return F.tm(front), F.tm(rear), None
def wires():
    parts = [F.cyl(ROD, 75, "x").translate([0, y, RC]) for y in (0, 188, 240, YR)]
    parts += [F.cyl(ROD, 75, "x").translate([0, YR, LIPZ])]
    for x in (F.W1, F.W1 + 25.3, F.W1 + 50.6):
        parts.append(F.cyl(WIRE, YR + ROD, "y").translate([x, -ROD, WB + WIRE]))
        parts.append(m.Manifold.cylinder(WB + WIRE - LIPZ, WIRE, WIRE, 24).translate([x, YR + ROD + WIRE, LIPZ]))
    return F.tm(m.Manifold.batch_boolean(parts, m.OpType.Add))
clips = [F.box(X0 + 0.5, X0 + 15.5, y0, y0 + 12.4, ZB - 0.9, ZB) for y0 in (-OF, YR + OF - 12.4)]
STEEL = np.array([0.55, 0.6, 0.66]); WIREC = np.array([0.22, 0.22, 0.24]); PIECE = np.array([0.93, 0.62, 0.30]); PH = np.array([0.80, 0.80, 0.86])
def grams(man, shell=1.24, infill=0.15):        # inference: shell 2 beads over the surface, 15% infill inside, PETG 1.27 g/cm3
    t = F.tm(man) if not isinstance(man, trimesh.Trimesh) else man
    s = t.area * shell; v = t.volume
    return 1.27 * (min(s, v) + infill * max(v - s, 0)) / 1000
SIDE = np.array([0.95, 0.80, 0.45])
titles = {"A": "A  Strip: rod band only (working model now)", "B": f"B  Corner pad: {DEPTH:.0f} deep from the shelf's front face", "C": "C  Full side: rail along the glass, top bars over the gap (new piece, not sized)"}
fig, axes = plt.subplots(3, 2, figsize=(24, 22), gridspec_kw=dict(width_ratios=[1.35, 1]))
top, under = (-0.9, -0.28, 1.0), (-0.9, -0.28, -0.75)
for row, opt in zip(axes, "ABC"):
    for ax, eye in zip(row, (top, under)):
        R.FACES.clear(); f, r, side = pieces(opt)
        R.mesh(f, PIECE); R.mesh(r, PH); R.mesh(wires(), WIREC)
        if side is not None: R.mesh(side, SIDE)
        for c in clips: R.mesh(F.tm(c), STEEL)
        cam = R.view(ax, eye=eye, ppm=3.0, pad=6)
        if eye is top:
            ax.set_title(titles[opt], fontsize=16, loc="left", fontweight="bold")
            R.call(ax, cam, (0, -OF, ZB), (70, -10), "front piece")
            R.call(ax, cam, (X0 / 2, YR + OF, TOP), (-30, 40), "rear piece (placeholder, not designed)", color="#555")
            R.call(ax, cam, (50, 150, WB + 2 * WIRE), (20, 40), "wire section", color="#222")
            R.call(ax, cam, (X0, 150, TOP), (-20, -60), "glass side (1.5 to glass)", color="#555", size=10)
            R.dim(ax, cam, (X0, -OF, TOP), (0, -OF, TOP), (0, -12, 0))
            if opt == "B": R.dim(ax, cam, (X0, -OF, TOP), (X0, -OF + DEPTH, TOP), (-10, 0, 0))
            if opt == "C": R.call(ax, cam, (X0 + 2, 120, TOP), (-30, 50), "side rail", color="#8a5a00")
        else:
            ax.set_title("same, seen from below (clips show)", fontsize=12, loc="left")
            R.call(ax, cam, (X0 + 8, -OF + 6, ZB - 0.9), (-40, -40), "stock clip (front-to-back spot unconfirmed)", color="#3a4a5a", size=10)
            R.call(ax, cam, (X0 + 8, YR + OF - 6, ZB - 0.9), (-40, 40), "rear clip", color="#3a4a5a", size=10)
R.source(axes[2][0], REPO + "/products/shelf/build/front-piece_model.py", cam)
fig.suptitle("Shelf body footprint options: left side band (right side mirrors). Fillets left out.", fontsize=18)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_footprint_options.png")
for opt in "ABC":
    f, r, side = pieces(opt); g = 2 * (grams(f) + grams(r) + (grams(side) if side is not None else 0)); print(opt, "per shelf g %.0f" % g)

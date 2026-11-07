"""Rear piece lip sleeve: fixes for dpcheck's findings (2026-10-10) where the closed rear wall and the upper lip meet the lip bore.
  chamfer: as is (a 53-deg overhang strip, 16.7 mm2, where the wall top meets the bore) vs a 45-deg chamfer there (ch45).
  lip:     the upper lip's trim on the layer grid: 0.60 (2 layers, lip=0.6) vs 0.90 (3 layers, lip=0.9); agreed 0.62 is off the grid.
Each option: the whole piece with a window cut through the sleeve at x 25 (spot in red), and the sleeve section there end-on with
the lip rod and a lip crosswire. Prints on its side, front face on the bed: print up is +y. From rear-piece_model.py.
Usage: python3 rear-sleeve_gridfix_options.py chamfer|lip [roof flat, default 3.55] [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
ROD, WIRE, BORE, LIPB, LIPZ, W1, J0 = RP.ROD, RP.WIRE, RP.BORE, RP.LIPB, RP.LIPZ, RP.W1, RP.J0
WHICH = sys.argv[1] if len(sys.argv) > 1 else "chamfer"; PK = float(sys.argv[2]) if len(sys.argv) > 2 else 3.55
CB = RP.RC - (WIRE + 0.3)            # 1.75 under the lip rod's center (agreed change 28); the rod rests 0.15 under the bore center
K = dict(close_below=CB, trim=True, lead=0.6, lead_c=0.6, peak=PK, yr=PK + 1.8)
if WHICH == "chamfer":
    opts = [("As is: 53° overhang strip where the wall top meets the bore", dict(lip=0.6)),
            ("Straight cut, 35° from vertical, from the bore to the wall top's rear edge", dict(lip=0.6, ch45=True))]
else:
    opts = [("Upper lip 0.60 (2 layers), trim at layer 25", dict(lip=0.6, ch45=True)),
            ("Upper lip 0.90 (3 layers), trim at layer 24", dict(lip=0.9, ch45=True))]
PIECE = np.array([0.93, 0.62, 0.30]); HOT = np.array([0.90, 0.10, 0.10]); RODC = np.array([0.22, 0.22, 0.24])
XC = 25.0
def hot(F, n, d, kw):
    cx, cy, cz = F.mean(0); zr = cz - LIPB
    if not (J0 < cx < d["reach"] + 0.01): return False
    if WHICH == "chamfer":                                         # as is: bore facets past 45 deg; cut: the cut's own face
        if not (1.9 < cy < d["rear"] + 0.01 and -2.6 < zr < CB + 0.01): return False
        if not kw.get("ch45"): return n[1] < -0.70 and n[2] > 0.3
        y0 = d["rear"] - 0.6; v = np.array([d["rear"] - y0, CB + RP.bore_z(y0)]); v = np.array([-v[1], v[0]]) / np.linalg.norm(v)
        return abs(n[1] - v[0]) < 0.03 and abs(n[2] - v[1]) < 0.03
    lt = kw["lip"]; return d["rear"] - lt - 0.01 < cy < d["rear"] + 0.01 and zr > 1.0 and n[2] < -0.5   # the lip's underside
def add(p, d, kw):
    n0 = len(R.FACES); R.mesh(RP.tm(p), PIECE)
    for i in range(n0, len(R.FACES)):
        F, n, c, cut = R.FACES[i]
        if hot(F, n, d, kw): R.FACES[i] = (F, n, HOT, cut)
wire = m.Manifold.cylinder(RP.WB + WIRE - LIPZ + 6, WIRE, WIRE, 24).translate([W1 + 25.3 * 0, ROD + WIRE, LIPZ])
fig, axes = plt.subplots(2, 3, figsize=(34, 20), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.0]))
ZEYE = (1.0, -0.45, 0.6) if WHICH == "chamfer" else (1.0, 0.35, -0.6)
for row, (title, kw) in enumerate(opts):
    p, d = RP.build(**K, **kw)
    ax = axes[row][0]; R.FACES.clear()
    add(p - RP.box(XC, d["reach"] + 1, -20, 20, LIPB - 8, LIPB + 8), d, kw)
    cam = R.view(ax, eye=(1.0, -0.45, 0.6), ppm=7.0, pad=14)
    ax.set_title(("AB"[row]) + "  " + title, fontsize=16, loc="left", fontweight="bold")
    R.call(ax, cam, (XC, d["rear"], LIPB + CB), (120, -40), "spot: zoomed at right (x 15 to 25)", color="#b00", size=12)
    ax.text(0.0, 0.0, "Whole piece with the sleeve cut off at x 25 (its last 15 mm hidden); seen from the inboard end, the front and above.\nPrint up = +y (rear face).", transform=ax.transAxes, fontsize=11, va="bottom")
    xy = np.array([R.proj(cam, q) for q in ((15, -6, LIPB - 6), (XC, -6, LIPB - 6), (XC, 6, LIPB + 6), (15, 6, LIPB + 6), (15, -6, LIPB - 6))])
    ax.plot(xy[:, 0], xy[:, 1], color="#e01010", lw=1.5, ls="--")
    ax = axes[row][1]; R.FACES.clear()
    add((p - RP.box(XC, d["reach"] + 1, -20, 20, LIPB - 8, LIPB + 8)) ^ RP.box(15, XC, -10, 10, LIPB - 7, LIPB + 7), d, kw)
    cam = R.view(ax, eye=ZEYE, ppm=40.0, pad=1.0)
    ax.set_title("Zoom: sleeve from x 15 to the cut at x 25, spot faces in red;\n" + ("seen from the inboard end, the front and above" if WHICH == "chamfer" else "seen from the inboard end, the rear and below"), fontsize=13, loc="left")
    ax = axes[row][2]; R.FACES.clear()
    slab = RP.box(XC - 1.0, XC, -9, 9, LIPB - 7, LIPB + 7)
    add(p ^ slab, d, kw); R.mesh(RP.tm(RP.rods(55) ^ slab), RODC); R.mesh(RP.tm(wire.translate([XC - W1 - 0.5, 0, 0]) ^ slab), RODC)
    cam = R.view(ax, eye=(1.0, 0.0, 0.0), ppm=60.0, pad=0.6)
    ax.set_title("Close-up: sleeve section at x 25, looking toward the glass;\nprint up is to the right; lip rod and a lip crosswire in dark gray", fontsize=13, loc="left")
    if WHICH == "chamfer":
        y0 = d["rear"] - 0.6; zc = LIPB + CB
        if kw.get("ch45"):
            y0 = d["rear"] - 0.6; S0 = (y0, LIPB - RP.bore_z(y0))
            xy = np.array([R.proj(cam, (XC, a, b)) for a, b in (S0, (d["rear"], zc))]); ax.plot(xy[:, 0], xy[:, 1], color="#e01010", lw=2.5)
            R.call(ax, cam, (XC, 2.35, zc - 0.2), (150, -70), "cut: layer 25 to layer 27, removes at most 0.12 mm", color="#b00", size=12)
        else:
            a = np.linspace(np.arctan2(zc - LIPB, np.sqrt(BORE ** 2 - (zc - LIPB) ** 2)), -np.pi / 4, 12)   # past 45 deg in print
            xy = np.array([R.proj(cam, (XC, BORE * np.cos(t), LIPB + BORE * np.sin(t))) for t in a]); ax.plot(xy[:, 0], xy[:, 1], color="#e01010", lw=2.5)
            R.call(ax, cam, (XC, 2.4, zc - 0.25), (150, -70), "overhang strip past 45° (dpcheck: 53°)", color="#b00", size=12)
        R.dim(ax, cam, (XC, d["rear"], zc), (XC, d["rear"], LIPZ - WIRE), (0, 1.2, 0), text=f"wire clearance {LIPZ - WIRE - zc:.2f}")
    else:
        lt = kw["lip"]; dz = RP.bore_z(d["rear"] - lt)
        xy = np.array([R.proj(cam, (XC, y, LIPB + dz)) for y in (d["rear"] - lt, d["rear"])]); ax.plot(xy[:, 0], xy[:, 1], color="#e01010", lw=3)
        R.dim(ax, cam, (XC, d["rear"] - lt, LIPB + dz + 0.6), (XC, d["rear"], LIPB + dz + 0.6), (0, 0, 1.6), text=f"lip {lt:.2f}")
        R.dim(ax, cam, (XC, d["rear"] + 0.3, LIPB + CB), (XC, d["rear"] + 0.3, LIPB + dz), (0, 1.0, 0), text=f"opening {dz - CB:.2f}")
R.source(axes[1][0], os.path.abspath(__file__), cam)
fig.suptitle(f"Rear piece lip sleeve, {'overhang fix' if WHICH == 'chamfer' else 'upper lip on the layer grid'} (roof flat {PK:g}). Lead-ins 0.6, no marks (agreed, unsaved); fillets left out except the sleeve root.", fontsize=14)
R.save(fig, sys.argv[3] if len(sys.argv) > 3 else f"/mnt/project-files/images/shelf_rearSleeve_{'chamferOptions' if WHICH == 'chamfer' else 'lipGridOptions'}.png")

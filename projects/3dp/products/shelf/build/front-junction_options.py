"""Front piece bore/channel junction in print (shelf agreed changes 14, 20, 24): sections across the sleeve at x 20, print up
(model +y) up, for the agreed knife-edge trim on both sides (A) and with the print-top trim dropped (B), each layer region with
nothing under it marked red. Usage: python3 front-junction_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
spec = importlib.util.spec_from_file_location("front_piece_model", os.path.join(HERE, "front-piece_model.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
LH = 0.3
def section(tt, x=20.0):
    p, d = F.build(trim_top=tt); t = F.tm(p)
    sec = t.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    polys = [Polygon(np.c_[-e[:, 2], e[:, 1] + d["OF"]]) for e in sec.discrete if len(e) > 3]
    shape = polys[0]
    for q in polys[1:]: shape = shape.symmetric_difference(q)
    return shape, d
def unsupported(shape, top=12.9):
    """Parts of each layer band with nothing in the band below (per-layer floating test on the section)."""
    out = []
    for k in range(1, int(round(top / LH))):
        band = shape.intersection(Polygon([(-20, k * LH), (20, k * LH), (20, (k + 1) * LH), (-20, (k + 1) * LH)]))
        below = shape.intersection(Polygon([(-20, (k - 1) * LH), (20, (k - 1) * LH), (20, k * LH), (-20, k * LH)]))
        if band.is_empty: continue
        sx = unary_union([Polygon([(g.bounds[0] - 0.0, k * LH), (g.bounds[2], k * LH), (g.bounds[2], (k + 1) * LH), (g.bounds[0], (k + 1) * LH)])
                          for g in getattr(below, "geoms", [below]) if not g.is_empty and g.area > 1e-6]) if not below.is_empty else Polygon()
        for g in getattr(band, "geoms", [band]):
            if g.area > 1e-4 and (sx.is_empty or g.intersection(sx).area < 0.05 * g.area): out.append(g)
    return out
fig, axes = plt.subplots(1, 2, figsize=(22, 10))
for ax, (tt, title) in zip(axes, [(True, "A  As agreed (change 24): both knife edges trimmed"), (False, "B  Print-top trim dropped; the bore roof's 45° line carries that edge")]):
    shape, d = section(tt)
    for g in getattr(shape, "geoms", [shape]):
        ax.fill(*g.exterior.xy, color=(0.93, 0.62, 0.30), ec="k", lw=1)
        for h in g.interiors: ax.fill(*h.xy, color="white", ec="k", lw=1)
    for g in unsupported(shape):
        ax.fill(*g.exterior.xy, color="red", ec="red", lw=0.5)
    ax.add_patch(plt.Circle((0, 7.45 + F.RC), F.ROD, color=(0.3, 0.3, 0.33)))
    for y in (2.8, 5.7):
        pass
    ax.add_patch(plt.Rectangle((-(F.TOP), 7.45 - F.ROD), 2 * F.WIRE, 30, color=(0.3, 0.3, 0.33), alpha=0.35))
    ax.set_aspect("equal"); ax.set_xlim(-11, 7); ax.set_ylim(-0.5, 14); ax.axis("off")
    ax.set_title(title, fontsize=15, loc="left", fontweight="bold")
    ax.annotate("bed (front face)", (-10.3, 0), (-10.3, -0.45), fontsize=11)
    ax.annotate("rod", (0, 7.3), (3.6, 7.0), fontsize=11, arrowprops=dict(arrowstyle="-", color="#555"))
    ax.annotate("crosswire band\n(runs to the rear, print up)", (-4.25, 12), (-10.5, 12.3), fontsize=11, arrowprops=dict(arrowstyle="-", color="#555"))
    ax.annotate("roof", (-8, 4), (-8.6, 7.4), fontsize=11, arrowprops=dict(arrowstyle="-", color="#555"))
    ax.annotate("red: 0.6 ledge with nothing under it,\nalong the sleeve (x 10.25 to 42)" if tt else "hairline start where the 45° bore roof\nmeets the channel wall (OrcaSlicer still\nflags a floating cantilever here, inference)",
                (-2.3, 9.95 if tt else 9.3), (1.2, 1.6), fontsize=11, color="red", arrowprops=dict(arrowstyle="-", color="red"))
fig.suptitle("Front piece sleeve, section at x 20 in print orientation (front face on the bed, up = print up, 0.3 layers). "
             "Drawn from front-piece_model.py build(trim_top).", fontsize=14)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_frontPiece_junctionOptions.png")

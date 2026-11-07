"""Rear piece print orientation options for the card (open decision 1): the working model (closed rear wall, agreed change 28)
set on the bed each way, with its height and footprint and the largest tension across the layers away from the rod contacts
from the 3D runs (fe/rear_tet.py pickles; across = the stress along the build direction). Usage:
python3 rear-piece_orientation_options.py [reach] [out.png]"""
import importlib.util, os, sys, pickle, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
reach = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
piece, d = RP.build(reach=reach, close_below=-1.75, trim=True)
def across(k):                                                    # largest stress along build axis k away from the contacts, coarse and fine meshes
    out = []
    for tag in ("", "_fine0.2_n24"):
        pk = os.path.join(HERE, "fe", f"rear_tet_{reach:g}_close1.75_trim{tag}.pkl")
        if not os.path.exists(pk): continue
        D = pickle.load(open(pk, "rb")); ec = D["ec"]; B, L = RP.BORE, RP.LIPB
        cp = np.array([(x, B * np.sin(t), z0 + sg * B * np.cos(t)) for x in np.arange(0, reach + 0.01, 0.1) for t in np.linspace(-0.6, 0.6, 13)
                       for z0, sg, ok in ((L, 1, x >= reach - 2.5), (L, -1, x <= 10), (0.0, -1, x <= 10)) if ok])
        away = cKDTree(cp).query(ec, distance_upper_bound=1.5)[0] >= 1.5
        out.append(max(v["S"][away, k].max() for v in D["out"].values()))
    return out
OPTS = [("On its side, front face on the bed", [90, 0, 0], 1, "layers stack front to rear"),
        ("Sleeve vertical, glass end on the bed", [0, -90, 0], 0, "layers stack along the rods"),
        ("Upright, drop on the bed (left out; upside down is the same across the layers)", [0, 0, 0], 2, "layers stack bottom to top")]
OVER = {1: "bore roofs; the stub bores take the front piece's 45° peak", 0: "the drop's and clip seat's undersides", 2: "the body over the clip and the bore roofs"}
PIECE = np.array([0.93, 0.62, 0.30]); BED = np.array([0.80, 0.80, 0.82])
import textwrap
fig = plt.figure(figsize=(30, 14)); gs = fig.add_gridspec(2, 3, height_ratios=[3, 1], width_ratios=[1.2, 0.8, 1.0])
axes = [fig.add_subplot(gs[0, i]) for i in range(3)]; taxes = [fig.add_subplot(gs[1, i]) for i in range(3)]
for ax, tax, (title, rot, k, lay) in zip(axes, taxes, OPTS):
    p = piece.rotate(rot); lo, hi = np.array(p.bounding_box()[:3]), np.array(p.bounding_box()[3:]); p = p.translate([0, 0, -lo[2]])
    bed = RP.box(lo[0] - 8, hi[0] + 8, lo[1] - 8, hi[1] + 8, -1.0, 0.0)
    R.FACES.clear(); R.mesh(RP.tm(bed), BED); R.mesh(RP.tm(p), PIECE)
    cam = R.view(ax, eye=(-0.8, -1.3, 0.75), ppm=5.0, pad=6)
    ax.set_title(textwrap.fill(title, 48), fontsize=15, loc="left", fontweight="bold")
    s = across(k); h = hi[2] - lo[2]; t = RP.tm(p); n = t.face_normals; ar = t.area_faces; zc = t.triangles_center[:, 2]
    onbed = ar[(n[:, 2] < -0.99) & (zc < 0.05)].sum()                 # bed contact
    over = ar[(n[:, 2] < -np.cos(np.radians(45))) & (zc > 0.05)].sum()  # faces overhanging more than 45 degrees off the bed
    txt = (f"{lay}\nPrint height {h:.1f} mm, {onbed:.0f} mm2 on the bed, {over:.0f} mm2 overhanging past 45° ({OVER[k]})\n"
           f"Largest tension across the layers: {' / '.join(f'{v:.0f}' for v in s)} MPa (coarse / fine; limit 56 bending, 35 pulled straight)")
    tax.axis("off"); tax.text(0.0, 1.0, "\n".join(textwrap.fill(l, 62) for l in txt.split("\n")), transform=tax.transAxes, fontsize=13,
                              va="top", ha="left", bbox=dict(fc="#f6f6f6", ec="#999"))
R.source(axes[2], os.path.abspath(__file__), cam)
fig.suptitle(f"Rear piece print orientations (reach {reach:g}, rear wall closed below the wires). Stresses at 15 lb x 3 per corner, "
             "away from the rod contacts; inference.", fontsize=16)
R.save(fig, sys.argv[2] if len(sys.argv) > 2 else "/mnt/project-files/images/shelf_rearPiece_orientationOptions.png")

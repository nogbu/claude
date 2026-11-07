"""Rear piece stub bore roof options for the card (state.md open decision 8; agreed change 30 gives both stub bores a 45-deg peak).
The piece prints on its side, front face on the bed, so print up is +y and the layer grid runs from the front face (y -5.45).
The front piece's flat (3.65 from the bore center) lands between layers here, so the options are the two flats on the grid, each
with the front piece's 1.80 (6 layers) of rear wall beyond it: A 3.55 (layer 30, piece 36 layers thick), B 3.85 (layer 31, 37).
Each option: the piece cut at x 5 (stub zone) in 3D, roof faces in red, and the corner rod bore's section with its sizes.
From rear-piece_model.py. Usage: python3 rear-piece_roof_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
BORE, LIPB, J0, TOP, WIRE, LAYER = RP.BORE, RP.LIPB, RP.J0, RP.TOP, RP.WIRE, 0.3
K = dict(close_below=-(WIRE + 0.3), trim=True, lead=0.6, lead_c=0.6)
opts = [("A  Flat 3.55 from the bore center (layer 30)", 3.55), ("B  Flat 3.85 from the bore center (layer 31)", 3.85)]
PIECE = np.array([0.93, 0.62, 0.30]); HOT = np.array([0.90, 0.10, 0.10]); RODC = np.array([0.22, 0.22, 0.24])
XC = 5.0
def color_roofs(n0, peak):
    """Red: the peaked roof's faces (the two 45-deg slopes and the flat) of either stub bore, found by centroid and normal."""
    for i in range(n0, len(R.FACES)):
        F, n, c, cut = R.FACES[i]; cx, cy, cz = F.mean(0)
        for zc in (0.0, LIPB):
            if cx < J0 + 0.01 and 1.0 < cy <= peak + 0.01 and abs(cz - zc) < 3.0 and n[1] < -0.6:
                R.FACES[i] = (F, n, HOT, cut)
fig, axes = plt.subplots(2, 2, figsize=(26, 20), gridspec_kw=dict(width_ratios=[1.25, 1]))
for row, (title, pk) in enumerate(opts):
    piece, d = RP.build(peak=pk, yr=pk + 1.8, **K)
    ax = axes[row][0]; R.FACES.clear()
    part = piece - RP.box(XC, J0 + 1, -20, 20, -7, 9)               # window into the corner rod bore; the rest of the piece kept
    R.mesh(RP.tm(part), PIECE); color_roofs(0, pk)
    cam = R.view(ax, eye=(1.0, -0.55, 0.35), ppm=7.0, pad=14)
    ax.set_title(title, fontsize=16, loc="left", fontweight="bold")
    R.call(ax, cam, (2.5, pk, 0.0), (-120, 60), "corner rod bore roof (red)", color="#b00", size=12)
    R.call(ax, cam, (30, d["yf"], LIPB - 2), (-40, -80), "lip rod bore: same roof in its stub zone\n(x 0 to 10.25), hidden behind the sleeve", color="#555", size=11)
    R.call(ax, cam, (-30, d["yf"], RP.ZB + 4), (-60, -70), "front face, on the bed", color="#555", size=11)
    ax.text(0.0, 0.0, f"Whole piece, window cut at x {XC:g} to {J0:g} around the corner rod bore; seen from the inboard end and the front. Print up = +y (rear face).", transform=ax.transAxes, fontsize=11, va="bottom")
    ax = axes[row][1]; R.FACES.clear()
    slab = RP.box(XC - 1.0, XC, -9, 9, -6, 7)
    R.mesh(RP.tm(piece ^ slab), PIECE); color_roofs(0, pk)
    R.mesh(RP.tm(RP.rods(55) ^ slab), RODC)
    cam = R.view(ax, eye=(1.0, 0.0, 0.0), ppm=60.0, pad=0.6)
    ax.set_title("Close-up: corner rod bore end-on at the window (x 5),\nlooking toward the glass; roof outlined in red; print up is to the right", fontsize=13, loc="left")
    t = BORE * np.sqrt(2) - pk
    R.dim(ax, cam, (XC, 0, 0), (XC, pk, 0), (0, 0, 4.4), text=f"flat {pk:.2f} from center")
    R.dim(ax, cam, (XC, BORE, 0), (XC, pk, 0), (0, 0, -4.4), text=f"sag room {pk - BORE:.2f}")
    R.dim(ax, cam, (XC, pk, -t), (XC, pk, t), (0, 1.0, 0), text=f"bridge {2 * t:.2f}")
    R.dim(ax, cam, (XC, pk, 4.2), (XC, d["yr"], 4.2), (0, 0, 0.0), text=f"{d['yr'] - pk:.2f} (6 layers)")
    t0 = BORE / np.sqrt(2)                                           # where the 45-deg slopes leave the bore circle
    xy = np.array([R.proj(cam, (XC, a, b)) for a, b in ((t0, -t0), (pk, -t), (pk, t), (t0, t0))]); ax.plot(xy[:, 0], xy[:, 1], color="#e01010", lw=2.5)
    R.dim(ax, cam, (XC, d["yf"], -5.4), (XC, d["yr"], -5.4), (0, 0, 0.0), text=f"piece {d['yr'] - d['yf']:.2f} ({(d['yr'] - d['yf']) / LAYER:.0f} layers)")
R.source(axes[1][0], os.path.abspath(__file__), cam)
fig.suptitle("Rear piece stub bore roofs, 45° peak cut flat on the layer grid (bed at the front face). Lead-ins 0.6, no marks (agreed, unsaved); fillets left out except the sleeve root.", fontsize=14)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearPiece_roofOptions.png")

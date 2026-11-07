"""Rear piece lead-in options for the card (state.md open decision 8). A: 0.6 on every mouth (the front piece's, agreed change 15).
B: 0.6 at the sleeve mouth, 1.0 on the rear corner rod bore, which the rod finds blind after the lip rod is in. Each option: 3D from
the inboard end with the lead-in faces in red, and close-up sections of both bore mouths at y 0 with the rods in place.
From rear-piece_model.py (agreed changes 27-31). Usage: python3 rear-piece_leadin_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
BORE, LIPB, J0, TOP, WIRE = RP.BORE, RP.LIPB, RP.J0, RP.TOP, RP.WIRE
CLOSE = -(WIRE + 0.3)
opts = [("A  0.6 on every mouth (the front piece's)", 0.6, 0.6), ("B  0.6 at the sleeve mouth, 1.0 on the corner rod bore", 0.6, 1.0)]
PIECE = np.array([0.93, 0.62, 0.30]); HOT = np.array([0.90, 0.10, 0.10]); RODC = np.array([0.22, 0.22, 0.24])
def add_piece(piece, mouths):
    n0 = len(R.FACES); R.mesh(RP.tm(piece), PIECE)
    for i in range(n0, len(R.FACES)):                       # recolor lead-in faces by centroid and normal (learnings/design)
        F, n, c, cut = R.FACES[i]; cx = F.mean(0)[0]
        if 0.4 < abs(n[0]) < 0.95 and any(x - L - 0.02 <= cx <= x + 0.02 for x, L in mouths):
            R.FACES[i] = (F, n, HOT, cut)
fig, axes = plt.subplots(2, 3, figsize=(30, 17), gridspec_kw=dict(width_ratios=[1.4, 1, 1]))
for row, (title, lead, lc) in enumerate(opts):
    piece, d = RP.build(close_below=CLOSE, trim=True, lead=lead, lead_c=lc); mouths = [(d["reach"], lead), (J0, lc)]
    ax = axes[row][0]; R.FACES.clear(); add_piece(piece, mouths)
    cam = R.view(ax, eye=(1.0, 0.75, 0.4), ppm=6.0, pad=6)
    ax.set_title(title, fontsize=16, loc="left", fontweight="bold")
    R.call(ax, cam, (J0, 0, BORE), (60, 70), f"corner rod bore mouth ({lc:g})", color="#b00", size=12)
    R.call(ax, cam, (d["reach"], 0, LIPB + BORE), (90, 60), f"lip bore mouth ({lead:g})", color="#b00", size=12)
    R.call(ax, cam, (d["reach"], d["rear"], LIPB + 2.3), (110, -40), f"rear opening edges ({lead:g})", color="#b00", size=12)
    cut = RP.box(-50, 60, -20, 0, -60, 20); rods = RP.rods(55) ^ cut
    for col, (x, L, zc0, name) in enumerate(((J0, lc, 0.0, "corner rod bore mouth"), (d["reach"], lead, LIPB, "lip bore mouth"))):
        ax = axes[row][col + 1]; R.FACES.clear()
        win = RP.box(x - 7, x + 3, -20, 0, zc0 - 7, zc0 + 7)       # close-up: the model cropped, not its faces filtered
        add_piece(piece ^ cut ^ win, mouths); R.mesh(RP.tm(rods ^ win), RODC)
        cam = R.view(ax, eye=(0.0, 1.0, 0.0), ppm=60.0, pad=0.5)
        ax.set_title(f"{name}: section at y 0 (bore center), looking forward; rod in place", fontsize=13, loc="left")
        R.dim(ax, cam, (x - L, 0, zc0 + BORE), (x, 0, zc0 + BORE), (0, 0, 1.2))
        if col == 0:
            R.dim(ax, cam, (x + 0.2, 0, BORE + L), (x + 0.2, 0, TOP), (1.0, 0, 0), text=f"{TOP - BORE - L:.2f} wall left")
            ax.text(0.0, -0.03, f"Front and rear walls (across this cut, in layers): {2.35 - L:.2f} left at the mouth", transform=ax.transAxes,
                    fontsize=12, color="#b00", fontweight="bold", va="top")
R.source(axes[1][0], os.path.abspath(__file__), cam)
fig.suptitle("Rear piece lead-ins (45°), working model: reach 40, walls 2.48 / 2.35, rear wall closed below the wire ends. Fillets left out except the sleeve root; stub bore roofs not yet peaked.", fontsize=15)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearPiece_leadinOptions.png")

"""Rear piece left/right marks for the card (state.md open decision 8). Both options: the right piece is the left piece mirrored
in x. A: L / R debossed 0.4 deep, 6 tall, in the glass-end face (hidden against the glass in use). B: no marks. Each panel: the
piece seen from its glass side, letter faces in red. From rear-piece_model.py (hand()). Usage: python3 rear-piece_marks_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
PIECE = np.array([0.93, 0.62, 0.30]); HOT = np.array([0.90, 0.10, 0.10])
base, d = RP.build(close_below=-(RP.WIRE + 0.3), trim=True, lead=0.6, lead_c=0.6)
fig, axes = plt.subplots(2, 2, figsize=(22, 18))
for row, marked in enumerate((True, False)):
    for col, side in enumerate("LR"):
        p = RP.hand(base, d, side) if marked else (base if side == "L" else base.mirror([1, 0, 0]))
        sx = -1 if side == "L" else 1; xe = RP.X0 if side == "L" else -RP.X0      # glass side, glass-end face x
        ax = axes[row][col]; R.FACES.clear(); R.mesh(RP.tm(p), PIECE)
        for i, (F, n, c, cut) in enumerate(R.FACES):
            cx, cy, cz = F.mean(0)
            if 0.005 < -sx * (cx - xe) <= 0.42 and abs(cy) < 3.5 and abs(cz - (RP.ZB + RP.TOP) / 2) < 3.5:
                R.FACES[i] = (F, n, HOT, cut)
        cam = R.view(ax, eye=(sx * 1.0, -0.55, 0.35), ppm=8.0, pad=5)
        ax.set_title(("A  L / R debossed in the glass-end face: " if marked else "B  No marks: ") + ("left piece" if side == "L" else "right piece (mirror)"),
                     fontsize=14, loc="left", fontweight="bold")
        R.call(ax, cam, (xe, d["yf"], RP.ZB + 2), (90 * sx, -60), "glass-end face (against the glass)", color="#555", size=11)
        R.call(ax, cam, (-30 * sx, d["yf"], RP.LIPB), (0, -70), "lip sleeve (inboard)", color="#555", size=11)
R.source(axes[1][0], os.path.abspath(__file__), cam)
fig.suptitle("Rear piece left and right, seen from the glass side and the front. Lead-ins 0.6 (agreed, unsaved); fillets left out except the sleeve root.", fontsize=14)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearPiece_marksOptions.png")

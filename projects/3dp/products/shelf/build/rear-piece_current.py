"""Rear piece as agreed so far (state.md agreed changes 27-31 and open decision 8's answers, 2026-10-10): whole piece from the
inboard end and from the glass side, every face edge drawn, with the left and right pieces (mirror). Fillets left out except the
sleeve root r1.0 (design principle 2 sizes come at build). From rear-piece_model.py. Usage: python3 rear-piece_current.py [lip] [out.png]"""
import importlib.util, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
LIP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
KW = dict(close_below=RP.RC - (RP.WIRE + 0.3), trim=True, lead=0.6, lead_c=0.6, peak=3.55, yr=3.55 + 1.8, lip=LIP, ch45=True)
PIECE = np.array([0.93, 0.62, 0.30]); RODC = np.array([0.22, 0.22, 0.24])
p, d = RP.build(**KW)
fig, axes = plt.subplots(1, 3, figsize=(33, 12))
views = [("Left piece, from the inboard end, the front and above", p, (1.0, -0.6, 0.5)),
         ("Left piece, from the glass side, the rear and below", p, (-1.0, 0.7, -0.4)),
         ("Right piece (mirror), from the inboard end, the front and above", p.mirror([1, 0, 0]), (-1.0, -0.6, 0.5))]
for ax, (title, q, eye) in zip(axes, views):
    R.FACES.clear(); R.mesh(RP.tm(q), PIECE)
    cam = R.view(ax, eye=eye, ppm=8.0, pad=8); ax.set_title(title, fontsize=14, loc="left", fontweight="bold")
    s = 1 if q is p else -1
    R.call(ax, cam, (s * 25, d["yf"], RP.LIPB - 5), (0, -70), "lip sleeve (reach 40)", color="#555", size=11)
    if eye[2] < 0: R.call(ax, cam, (s * -30, 0, RP.ZB), (60, -60), "clip seat (underside)", color="#555", size=11)
R.source(axes[0], os.path.abspath(__file__), cam)
fig.suptitle(f"Rear piece as agreed: lead-ins 0.6, no marks, stub bore roofs flat 3.55, wall top 1.75 under the lip rod's center with the 35° cut, upper lip {LIP:.2f}. "
             "Prints on its side, front face on the bed. Fillets left out except the sleeve root r1.0.", fontsize=13)
R.save(fig, sys.argv[2] if len(sys.argv) > 2 else "/mnt/project-files/images/shelf_rearPiece_agreed.png")

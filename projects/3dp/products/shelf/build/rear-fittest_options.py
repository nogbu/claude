"""Rear piece fit test options (shelf state.md Planned files; agreed changes 7, 30, 37): the agreed rear piece
(rear-piece_model.py build with rear-piece_current.py's KW) cut down to the rod-end zone and lip sleeve, closed by an end wall
at the rod ends, with the lip bore set below the rear corner bore by a test spacing. The lip rod spacing reads 31.6-32.9 across
photos (photos.unicoly 233546-233601, 143642-143746; 32.3 used), and a 5.9 rod in a 6.2 bore takes about +/-0.3 of it (inference).
piece(spacing, cut=True, marks=0) returns (manifold, dims); marks: vertical grooves on the end face between the bores, counted
to identify a step. Usage: python3 rear-fittest_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
KW = dict(close_below=RP.RC - (RP.WIRE + 0.3), trim=True, lead=0.6, lead_c=0.6, peak=3.55, yr=3.55 + 1.8, lip=0.6, ch45=True)
END = 2.48                                     # end wall at the rod ends: 4 beads (x is a bead direction on its side)
GW, GD, GP = 1.5, 1.0, 3.0                     # mark groove width (z), depth (x), pitch
DENS = 1.27                                    # g/cm3, PETG Basic (Bambu data sheet V3.0); solid grams, infill lowers it

def piece(spacing=32.3, cut=True, marks=0):
    RP.LIPB = -spacing; RP.LIPZ = RP.LIPB + RP.RC   # build() reads these module globals
    p, d = RP.build(**KW)
    if cut:
        p = p ^ RP.box(-END, d["reach"] + 1, d["yf"] - 1, d["yr"] + 1, d["zb"] - 1, RP.TOP + 1)
        zc = -spacing / 2                       # between the bores
        for k in range(marks):
            z = zc + (k - (marks - 1) / 2) * GP
            p = p - RP.box(-END - 1, -END + GD, d["yf"] - 1, d["yr"] + 1, z - GW / 2, z + GW / 2)
    return p, d

def grams(p): return p.volume() / 1000 * DENS

if __name__ == "__main__":
    PIECE = np.array([0.93, 0.62, 0.30]); RODC = np.array([0.22, 0.22, 0.24]); PPM = 9.0; STACK = 55.0
    R.MIN_PX = 0                                   # one scale for every panel: images placed by pixel extent in shared limits
    opts = [("A  Three cut-down pieces: lip rod spacing 31.8 / 32.3 / 32.8 (top to bottom; 1, 2, 3 grooves)", [(31.8, 1), (32.3, 2), (32.8, 3)], True),
            ("B  One cut-down piece at 32.3", [(32.3, 0)], True),
            ("C  One full left rear piece at 32.3", [(32.3, 0)], False)]
    views = [("on the rods, from the inboard end, the front and above", (1.0, -0.6, 0.5), True),
             ("off the rods, from the glass end, the front and above", (-1.0, -0.5, 0.35), False)]
    panels = []
    for title, steps, cut in opts:
        parts = [piece(s, cut, mk) for s, mk in steps]
        g = sum(grams(p) for p, _ in parts)
        for vi, (vt, eye, withrods) in enumerate(views):
            R.FACES.clear()
            for i, ((p, d), (s, mk)) in enumerate(zip(parts, steps)):
                dz = -i * STACK; R.mesh(RP.tm(p.translate([0, 0, dz])), PIECE)
                if withrods:
                    RP.LIPB = -s; RP.LIPZ = RP.LIPB + RP.RC
                    R.mesh(RP.tm(RP.rods(60.0).translate([0, 0, dz])), RODC)
            img, cam = R.render(eye, PPM, frame=R.fit(eye, 6.0))
            panels.append((title, g, cut, vi, vt, img, cam, parts[0][1]))
    Hm = max(p[5].shape[0] for p in panels); Wm = max(p[5].shape[1] for p in panels)
    fig, axes = plt.subplots(2, 3, figsize=(36, 36 * 2 * Hm / (3 * Wm) + 3))
    for k, (title, g, cut, vi, vt, img, cam, d0) in enumerate(panels):
        ax = axes[vi, k // 2]; R.place(ax, img, Wm, Hm)
        head = f"{title}\n{g:.0f} g solid in all (inference), {'rod ends to the sleeve tip (x -2.48 to 40)' if cut else 'whole piece'}\n" if vi == 0 else f"{title[0]}  "
        ax.set_title(head + vt.capitalize(), fontsize=14, loc="left", fontweight="bold")
        if vi == 0:
            R.call(ax, cam, (30, d0["yf"], -32.3 - 5), (60, 50), "lip sleeve, reach 40", color="#555", size=11)
            R.call(ax, cam, (55, 0, RP.RC), (40, -40), "rear corner rod", color="#555", size=11)
        elif cut:
            R.call(ax, cam, (-2.48, d0["yf"], 1.5), (-60, -40), "end wall 2.48 at the rod ends", color="#555", size=11)
    R.source(axes[1, 0], os.path.abspath(__file__), cam)
    fig.suptitle("Rear fit test options, all at one scale: each piece is the agreed rear piece (changes 27-37), printed on its side, front face on the bed, "
                 "slid onto a section's rear corner. Fillets left out (design principle 2 sizes come at build).", fontsize=15)
    R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearFitTest_options.png")

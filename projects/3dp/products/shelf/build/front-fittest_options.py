"""Front piece fit test options (shelf state.md Planned files; agreed changes 7, 14-26): the agreed front piece (front-piece_model.py
build(), root C) cut down to the rod-end zone and J-slot sleeve, closed by an end wall at the rod ends, with the gap C over and under
the crosswire band set per test step (0.3 agreed; the crosswire is 2.9 +/- 0.2, Key data). piece(c, cut=True, marks=0) returns
(manifold, dims); marks: grooves on the end face across the bore axis, counted to identify a step.
Usage: python3 front-fittest_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
spec = importlib.util.spec_from_file_location("front_piece_model", os.path.join(HERE, "front-piece_model.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
END = 2.48                                     # end wall at the rod ends: 4 beads
GW, GD, GP = 1.5, 0.6, 3.0                     # mark groove width (z), depth (x; leaves 1.88 = 3 beads over the bore end), pitch
DENS = 1.27                                    # g/cm3, PETG Basic (Bambu data sheet V3.0); solid grams

def piece(c=0.3, cut=True, marks=0, **kw):
    F.C = c; F.J0 = F.W1 - F.WIRE - c            # build() reads these module globals; kw goes to build() (e.g. open_corner)
    p, d = F.build(**kw)
    if cut:
        p = p ^ F.box(-END, F.XE + 1, -d["OF"] - 1, d["OR"] + 1, -d["OZ"], F.TOP + c + F.ROOF + 1)
        for k in range(marks):
            z = (k - (marks - 1) / 2) * GP
            p = p - F.box(-END - 1, -END + GD, -d["OF"] - 1, d["OR"] + 1, z - GW / 2, z + GW / 2)
    return p, d

def grams(p): return p.volume() / 1000 * DENS

def section(L=70.0):
    ws = [F.cyl(F.WIRE, 40, "y").translate([x, -F.ROD, F.WB + F.WIRE]) for x in (F.W1, F.W2)]
    return m.Manifold.batch_boolean([F.rod] + ws, m.OpType.Add)

if __name__ == "__main__":
    PIECE = np.array([0.93, 0.62, 0.30]); WIREC = np.array([0.30, 0.30, 0.33]); PPM = 9.0; STACK = 30.0
    R.MIN_PX = 0
    opts = [("A  Three cut-down pieces: gap over the crosswire 0.2 / 0.3 / 0.4 (top to bottom; 1, 2, 3 grooves)", [(0.2, 1), (0.3, 2), (0.4, 3)], True),
            ("B  One cut-down piece at 0.3", [(0.3, 0)], True),
            ("C  One full left front piece at 0.3", [(0.3, 0)], False)]
    views = [("on the front edge rod and crosswires, from the inboard end, the rear and above", (1.0, 0.8, 0.6), True),
             ("off the rod, from the glass end, the front and above", (-1.0, -0.6, 0.5), False)]
    panels = []
    for title, steps, cut in opts:
        parts = [piece(s, cut, mk) for s, mk in steps]
        g = sum(grams(p) for p, _ in parts)
        for vi, (vt, eye, withrods) in enumerate(views):
            R.FACES.clear()
            for i, (p, d) in enumerate(parts):
                dz = -i * STACK; R.mesh(F.tm(p.translate([0, 0, dz])), PIECE)
                if withrods: R.mesh(F.tm(section().translate([0, 0, dz])), WIREC)
            img, cam = R.render(eye, PPM, frame=R.fit(eye, 6.0))
            panels.append((title, g, cut, vi, vt, img, cam, parts[0][1]))
    Hm = max(p[5].shape[0] for p in panels); Wm = max(p[5].shape[1] for p in panels)
    fig, axes = plt.subplots(2, 3, figsize=(36, 36 * 2 * Hm / (3 * Wm) + 4))
    for k, (title, g, cut, vi, vt, img, cam, d0) in enumerate(panels):
        ax = axes[vi, k // 2]; R.place(ax, img, Wm, Hm)
        head = f"{title}\n{g:.0f} g solid in all (inference), {'rod end to the sleeve tip (x -2.48 to %.1f)' % F.XE if cut else 'whole piece'}\n" if vi == 0 else f"{title[0]}  "
        ax.set_title(head + vt.capitalize(), fontsize=13, loc="left", fontweight="bold")
        if vi == 0:
            R.call(ax, cam, (F.W2, 30, F.WB + F.WIRE), (60, -40), "crosswires (run to the rear)", color="#555", size=11)
            R.call(ax, cam, (65, 0, F.RC - F.ROD), (40, 50), "front edge rod", color="#555", size=11)
    R.source(axes[1, 0], os.path.abspath(__file__), cam)
    fig.suptitle("Front fit test options, all at one scale: each piece is the agreed front piece (root C, changes 14-26), printed on its side, front face on the bed, "
                 "slid onto a section's front edge rod. Fillets left out.", fontsize=15)
    R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_frontFitTest_options.png")

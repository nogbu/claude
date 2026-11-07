"""Separate or joined side pieces (user ask 2026-10-10: "should the front and back just connect in the middle with a dovetail?",
and reaching the front piece back to a support rod instead of the twist-lock). One left side band of a shelf section:
A  separate pieces (now): the twist-lock front piece D (front-twist_model.py build(fw=4.5, fy=-1, hh=4.6)) and the rear piece
   (rear-piece_model.py, rear-piece_current.py's agreed sizes), each on its stock clip;
B  joined side: the same two pieces joined along the band by a rail (closed box, 2.5 walls; not sized) split by a dovetail
   in the middle, with closed stub sleeves on the two support rods.
Each row: the whole side from above, the glass side and the front, and the front corner cut on the front rod's axis (y 0) and
seen from the front, with the tipping couple: the clip pushes up 37 out past the rod end, the rod presses down on the stub
bore floor, and the hook holds the rod down past the first crosswire (loads from the 3D check, build/fe/front_twist_tet.py).
share(): how much of the front corner's tipping a joined rail could take to the rear piece, as torsion (inference, printed).
Usage: python3 side-joining_options.py [out.png] [page_dir]. Written 2026-10-10 (shelf thread, open decision 9)."""
import importlib.util, json, os, sys, numpy as np, manifold3d as m, trimesh, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
def mod(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, path)); mm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mm); return mm
TW = mod("ftm", "front-twist_model.py"); RP = mod("rpm", "rear-piece_model.py"); F = TW.F
X0, ZB, TOP, RC, ROD, WIRE, WB, BORE, J0 = F.X0, F.ZB, F.TOP, F.RC, F.ROD, F.WIRE, F.WB, F.BORE, F.J0
YR = 290.0; LIPZ = RC - 32.3; SUPPORT = (188.0, 240.0)            # Key data: rod positions, lip 32.3 below the rear corner rod
KW = dict(close_below=RP.RC - (RP.WIRE + 0.3), trim=True, lead=0.6, lead_c=0.6, peak=3.55, yr=3.55 + 1.8, lip=0.6, ch45=True)   # rear-piece_current.py
front, fd = TW.build(fw=4.5, fy=-1, hh=4.6)
rear = RP.build(**KW)[0].translate([0, YR, 0])
YF = fd["YF"]; YRF = YR - (BORE + 2.35)                              # front piece's front face; rear piece's front face (stub zone, tr 2.35)
YFR = fd["OR"]                                                       # front piece's rear face
CLIPC = X0 + 8.0                                                     # clip patch x -44.5..-29.5 (Key data), center -37
clips = [F.box(X0 + 0.5, X0 + 15.5, y0, y0 + 12.4, ZB - 0.9, ZB) for y0 in (YF, YR + KW["yr"] - 12.4)]

def wires():
    """Rods (front, two support, rear corner, lip) from their cut ends at x 0, and the first three crosswires on their tops (footprint_options.py)."""
    parts = [F.cyl(ROD, 75, "x").translate([0, y, RC]) for y in (0,) + SUPPORT + (YR,)] + [F.cyl(ROD, 75, "x").translate([0, YR, LIPZ])]
    for x in (F.W1, F.W1 + 25.3, F.W1 + 50.6):
        parts.append(F.cyl(WIRE, YR + ROD, "y").translate([x, -ROD, WB + WIRE]))
        parts.append(m.Manifold.cylinder(WB + WIRE - LIPZ, WIRE, WIRE, 24).translate([x, YR + ROD + WIRE, LIPZ]))
    return m.Manifold.batch_boolean(parts, m.OpType.Add)

def zprism(pts, z0, z1):
    return m.Manifold.extrude(m.CrossSection([pts]), z1 - z0).translate([0, 0, z0])

def joined():
    """Rail along the band from the front piece's rear face to the rear piece's front face, split at mid-length by a dovetail
    (tab on the front half, 0.3 gap drawn so the joint shows), plus closed stub sleeves (x 0..J0) on the support rods."""
    ym = (YFR + YRF) / 2; x0, x1 = X0, 0.0
    tab = [(-30.0, ym), (-15.0, ym), (-12.0, ym + 9.0), (-33.0, ym + 9.0)]          # dovetail tab: tip wider than its root, so it locks along y
    tabm = zprism(tab, ZB, TOP)
    gap = zprism([(-30.3, ym - 0.01), (-14.7, ym - 0.01), (-11.7, ym + 9.3), (-33.3, ym + 9.3)], ZB - 1, TOP + 1)
    fh = F.box(x0, x1, YFR, ym, ZB, TOP) + tabm
    rh = F.box(x0, x1, ym, YRF, ZB, TOP) - gap
    sleeves = []
    for y in SUPPORT:
        s = F.box(0.0, J0, y - (BORE + 2.35), y + (BORE + 2.35), -(BORE + 2.48), TOP) - F.cyl(BORE, J0 + 1, "x").translate([0, y, 0])
        sleeves.append(s)
    rh = rh + m.Manifold.batch_boolean(sleeves, m.OpType.Add)
    return fh, rh

def share(front=15.0, rear=5.0, b=45.0, h=20.0, t=2.5, solid=False, support=False, kr_mult=1.0):
    """Fraction of the front corner's tipping moment the front grip keeps when a printed rail joins the front and rear
    pieces (inference). Both corners tip the same way (each clip sits 37 out past the rod ends), so the rail twists only
    with the difference: a chain of torsion springs along y (rail GJ per length) between grips held to ground, the front
    grip (kf), optional support-rod grips at y 188 and 240 (each taken as stiff as the front grip, a generous bound: a
    stub-only sleeve is far weaker) and the rear grip (kr = kr_mult kf, not computed). Corner moments scale with the corner
    loads in lb (agreed change 11: 15 on the front pair and 5 on the rear when 75% of the shelf load sits at the front).
    kf from the 3D check of D (refined, end case): 7656 N mm turns the hook's bearing line 1.52 mm at 31.75 mm.
    Box J = 4 Am^2 t / s; solid J = beta b h^3. The dovetail's slop and slide are left out, so the rail is taken as unbroken."""
    G = 1900 / (2 * 1.38); kf = 7656 / (1.52 / 31.75); kr = kr_mult * kf
    if solid:
        J = np.interp(b / h, [1, 1.5, 2, 2.5, 3], [0.141, 0.196, 0.229, 0.249, 0.263]) * b * h ** 3
    else:
        J = 4 * ((b - t) * (h - t)) ** 2 * t / (2 * ((b - t) + (h - t)))
    ys = [YFR] + (list(SUPPORT) if support else []) + [YRF]; kg = [kf] + ([kf] * len(SUPPORT) if support else []) + [kr]
    Mn = np.zeros(len(ys)); Mn[0] = 7656 * front / 15; Mn[-1] = 7656 * rear / 15
    K = np.diag(kg).astype(float)
    for i in range(len(ys) - 1):
        k = G * J / (ys[i + 1] - ys[i]); K[i, i] += k; K[i + 1, i + 1] += k; K[i, i + 1] -= k; K[i + 1, i] -= k
    th = np.linalg.solve(K, Mn)
    return kf * th[0] / Mn[0], YRF - YFR

def grams(man, shell=1.24, infill=0.15):        # footprint_options.py: shell 2 beads over the surface, 15% infill inside (inference)
    t = F.tm(man); s = t.area * shell; v = t.volume
    return 1.27 * (min(s, v) + infill * max(v - s, 0)) / 1000

PIECE = np.array([0.93, 0.62, 0.30]); REAR = np.array([0.86, 0.66, 0.42]); RAIL = np.array([0.55, 0.72, 0.86]); RAIL2 = np.array([0.42, 0.62, 0.80])
WIREC = np.array([0.22, 0.22, 0.24]); RODC = np.array([0.50, 0.52, 0.56]); STEEL = np.array([0.55, 0.6, 0.66])
UP, DOWN, HOLD = "#1e8449", "#c0392b", "#1f5fa8"

def cut(man, ylo=0.0, box=(-48, 40, 0, 14, -18, 13)):
    """Keep y >= ylo inside the close-up's box (the front corner cut on the bore axis)."""
    x0, x1, y0, y1, z0, z1 = box
    return man ^ F.box(x0, x1, max(y0, ylo), y1, z0, z1)

def arrow(ax, cam, p, d, text, color, off, length=34):
    """Force arrow ending at 3D point p, pointing along image direction d (pixels, +y down), with its label offset in points."""
    x, y = R.proj(cam, p); d = np.asarray(d, float); d /= np.linalg.norm(d)
    ax.annotate("", xy=(x, y), xytext=(x - d[0] * length, y - d[1] * length), arrowprops=dict(arrowstyle="-|>", color=color, lw=3.0, mutation_scale=22))
    ax.annotate(text, xy=(x - d[0] * length, y - d[1] * length), xytext=off, textcoords="offset points", fontsize=11, fontweight="bold",
                color=color, ha="center", va="center", bbox=dict(fc="white", ec="none", alpha=0.9))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_side_joinOptions.png"
    page_dir = sys.argv[2] if len(sys.argv) > 2 else None
    fh, rh = joined(); W = wires()
    sh = {(ld, sol, sup): share(*ld, solid=sol, support=sup)[0] for ld in ((15, 5), (10, 10)) for sol in (False, True) for sup in (False, True)}
    Lr = share()[1]
    for kk, v in sh.items(): print(f"front {kk[0][0]} lb, rear {kk[0][1]} lb, {'solid' if kk[1] else 'box'} rail, {'with' if kk[2] else 'no'} support grips: front grip keeps {v:.0%}")
    for mlt in (2.0, 1e6): print(f"rear grip x{mlt:g}: front keeps {share(kr_mult=mlt)[0]:.0%} (box, 15/5)")
    gA = 2 * (grams(front) + grams(rear)); gB = gA + 2 * (grams(fh) + grams(rh))
    print(f"grams per shelf (two sides; shell plus 15% infill, inference): A {gA:.0f}, B {gB:.0f}")
    rows = {"A": ([(front, PIECE), (rear, REAR)], "A  Separate pieces (now): twist-lock front piece D and the rear piece, each on its clip"),
            "B": ([(front, PIECE), (rear, REAR), (fh, RAIL), (rh, RAIL2)], "B  Joined side: a rail with a dovetail mid-way, stub sleeves on the support rods")}
    notes = {"A": f"The front corner's tipping is held by the front grip alone (hook past the first crosswire).\nAbout {gA:.0f} g a shelf (inference).",
             "B": f"With 15 lb on the front corner and 5 on the rear, the front grip still keeps about {sh[((15, 5), False, False)]:.0%} of its tipping (box rail),\n"
                  f"and all of it when both corners carry the same; support-rod grips as stiff as the hook leave {sh[((15, 5), False, True)]:.0%}.\n"
                  f"Rail not sized; about {gB:.0f} g a shelf as a 2.5-wall box (inference)."}
    whole, close = (-0.95, -0.55, 0.9), (-0.10, -1.0, 0.16)
    PPM_W, PPM_C = 9.5, 30.0; R.MIN_PX = 0                           # one scale per column (render3d.place)
    def scene(k, which):
        parts = rows[k][0]; R.FACES.clear()
        if which == "w":
            for p, c in parts: R.mesh(F.tm(p), c)
            R.mesh(F.tm(W), WIREC)
            for c in clips: R.mesh(F.tm(c), STEEL)
        else:
            for p, c in parts:
                q = cut(p)
                if q.volume() > 1e-6: R.mesh(F.tm(q), c)
            R.mesh(F.tm(cut(W - F.cyl(ROD + 0.01, 80, "x").translate([-1, 0, RC]))), WIREC)
            R.mesh(F.tm(cut(F.cyl(ROD, 75, "x").translate([0, 0, RC]))), RODC); R.mesh(F.tm(cut(clips[0])), STEEL)
    frames = {}
    for which, eye, pad in (("w", whole, 6), ("c", close, 4)):
        fs = []
        for k in rows: scene(k, which); fs.append(R.fit(eye, pad))
        fs = np.array(fs); frames[which] = (fs[:, 0].min(), fs[:, 1].max(), fs[:, 2].min(), fs[:, 3].max())
    imgs = {}
    for k in rows:
        for which, eye, ppm in (("w", whole, PPM_W), ("c", close, PPM_C)):
            scene(k, which); imgs[(k, which)] = R.render(eye, ppm, frame=frames[which])
    Ww = max(imgs[(k, "w")][0].shape[1] for k in rows); Hw = max(imgs[(k, "w")][0].shape[0] for k in rows)
    Wc = max(imgs[(k, "c")][0].shape[1] for k in rows); Hc = max(imgs[(k, "c")][0].shape[0] for k in rows)
    fig, axes = plt.subplots(2, 2, figsize=(26, 15), gridspec_kw=dict(width_ratios=[Ww / Hw, Wc / Hc * 0.95]))
    for row, k in zip(axes, rows):
        parts, title = rows[k]
        ax = row[0]; img, cam = imgs[(k, "w")]; R.place(ax, img, Ww, Hw)
        ax.set_title(title, fontsize=15, loc="left", fontweight="bold")
        R.call(ax, cam, (X0 + 20, YF, ZB + 6), (-60, -40), "front piece D", color="#8a4b00")
        R.call(ax, cam, (X0 + 20, YR + 3, ZB + 6), (-70, 40), "rear piece", color="#8a4b00")
        R.call(ax, cam, (40, SUPPORT[0], RC + ROD), (90, 30), "support rods: crosswires\nlie on top, as on the front rod", color="#222", size=11)
        R.call(ax, cam, (X0 + 8, YF + 6, ZB - 0.9), (-40, 50), "stock clip", color="#3a4a5a", size=11)
        if k == "B":
            ym = (YFR + YRF) / 2
            R.call(ax, cam, (-22.5, ym + 4, TOP), (-120, -20), "dovetail", color="#1a4f7a", size=11)
            R.call(ax, cam, (J0, SUPPORT[1], TOP), (110, -10), "stub sleeve (10-13 mm stub only)", color="#1a4f7a", size=11)
        ax.text(0.0, -0.03, notes[k], transform=ax.transAxes, fontsize=13, va="top")
        ax = row[1]; img, cam = imgs[(k, "c")]; R.place(ax, img, Wc, Hc)
        ax.set_title("Front corner, cut on the front rod's axis, from the front", fontsize=13, loc="left")
        arrow(ax, cam, (CLIPC, 0.0, ZB - 0.9), (0, -1), "clip pushes up 200 N", UP, (0, -16))
        arrow(ax, cam, (1.25, 0.0, -BORE), (0, 1), "rod end pushes down on the\nstub bore's floor, 441-757 N", DOWN, (-10, 26))
        arrow(ax, cam, (24.0, 0.0, BORE), (0, -1), "rod pushes up on the hook past the\ncrosswire, 241 N at its end to 557 at its start", HOLD, (30, -40))
        R.dim(ax, cam, (CLIPC, 0.0, ZB - 0.9), (0.0, 0.0, ZB - 0.9), (0, 0, -3.0))
        if k == "B": R.call(ax, cam, (-20, 10, TOP), (60, 40), "rail (behind)", color="#1a4f7a", size=11)
        ax.text(0.0, -0.03, "Forces on the piece. Loads: 15 lb x 3 at the corner, hook load at its end (241 N)\nto its start (557 N), from the 3D check (inference).", transform=ax.transAxes, fontsize=11, va="top")
    R.source(axes[1][1], os.path.join(HERE, "front-twist_model.py"), imgs[("B", "c")][1]); axes[1][1].texts[-1].set_position((0.0, -0.13))
    R.source(axes[1][1], os.path.join(HERE, "rear-piece_model.py")); axes[1][1].texts[-1].set_position((0.0, -0.17))
    fig.suptitle("Shelf side: separate front and rear pieces, or joined (left side; the right mirrors). Fillets left out.", fontsize=18)
    R.save(fig, out)
    if page_dir:
        import zoompage as Z
        ctx = [(Z.tris(F.tm(W)), (0.30, 0.30, 0.33), "rods and crosswires")] + [(Z.tris(F.tm(c)), (0.62, 0.67, 0.72), "stock clips") for c in clips]
        def model(name, parts, note):
            tr = np.concatenate([Z.tris(F.tm(p)) for p, _ in parts]); col = np.concatenate([np.tile(c, (len(Z.tris(F.tm(p))), 1)) for p, c in parts])
            return Z.Model(name, tr, rgb=col, note=note)
        models = [model("A · separate pieces", rows["A"][0], notes["A"]), model("B · joined side", rows["B"][0], notes["B"])]
        intro = ("One side of a shelf section, left side. A is now: the twist-lock front piece D and the rear piece, each on its own clip. "
                 f"B joins them with a rail along the band (dovetail mid-way) and adds sleeves on the support rods' stubs. Each corner tips because its clip "
                 f"sits 37 mm out past the rod ends; a joined rail could pass the front corner's tipping to the rear piece only by twisting "
                 f"{Lr:.0f} mm, and the rear corner tips the same way, so with 15 lb on the front corner and 5 on the rear the front grip still keeps about "
                 f"{sh[((15, 5), False, False)]:.0%} of its tipping, and all of it under an even load. All values are inference.")
        html, files = Z.page(page_dir, "Side Joining Options", intro, pictures=[(out, "Rows A and B share each view and scale.")], models=models,
                             context=ctx, eyebrow="Shelf · front and rear pieces · separate or joined",
                             source="Made by build/side-joining_options.py from front-twist_model.py and rear-piece_model.py, projects/3dp/products/shelf in nogbu/claude.")
        json.dump(dict(html=html, files=files), open(os.path.join(page_dir, "page.json"), "w")); print("page", html)

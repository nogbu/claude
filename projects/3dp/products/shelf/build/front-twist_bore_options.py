"""Bore depth options for the twist-lock front piece D (front-twist_model.py build(fw=4.5, fy=-1, hh=4.6, bd=...); shelf state.md
open decision 9, agreed change 5: each piece stops against the last crosswire, bores deeper than the longest stub).
One row per option (Now bd 0, A 2.0, B 3.5, C 5.0: how far the bore and its roof run past the modeled rod end at x 0), each on the
rod with a 13 mm stub (the longest measured, photos 233619 / 233643; rod end at x W1 - 13 in the model's wire frame) and the first
two crosswires, at the position where it stops sliding on, found from the model: turned THETA, slid on in 0.01 steps until it
touches the rod (ROD - 0.02, as path_check) or a crosswire. A piece whose stop leaves it short of the crosswire is drawn turned back
to 0 deg with its overlap with the crosswires red (the reason it can't turn back). The piece (not the rod or wires) is cut on the
vertical plane through the bore axis (y 0), its rear half removed, and seen from the rear, inboard and a little above, so the cut
face shows the bore, the rod in it, the bore end (bright) and the stub sleeve end at the crosswire. Panels: the whole piece and a
close-up of the stub zone, one view, crop and scale per column. Numbers below each row are measured from the model: bore end
(probe on the bore axis), stub sleeve end and crosswire near face (mesh bounds), longest stub (bisection with the rod slid in at
crosswire contact), solid mass at 1.27 g/cm3.
Usage: python3 front-twist_bore_options.py [out.png] [--page out_dir]   (--page also writes a zoom page, zoompage.py, and prints
its files map as JSON). Written 2026-10-11 (shelf thread, open decision 9)."""
import importlib.util, json, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
spec = importlib.util.spec_from_file_location("ftm", os.path.join(HERE, "front-twist_model.py"))
TW = importlib.util.module_from_spec(spec); spec.loader.exec_module(TW)
OPTIONS = (("Now", 0.0), ("A", 2.0), ("B", 3.5), ("C", 5.0))
D_ARGS = dict(fw=4.5, fy=-1, hh=4.6)                  # variant D
STUB = 13.0; THETA = 100.0; DENS = 1.27e-3            # g/mm3
EYE = (0.45, 1.0, 0.55)                               # from the rear (+y), inboard (+x) and a little above
PIECE = np.array([0.80, 0.77, 0.70]); BRIGHT = np.array([0.05, 0.55, 1.0]); RED = np.array([0.88, 0.08, 0.08]); STEEL = np.array([0.30, 0.30, 0.33])
WIRE_L = 9.0                                          # crosswires drawn from the rod's front face 9 mm back (context only)

def rod(L=STUB, r=TW.ROD, length=41.0):
    """The front edge rod with an L mm stub: its end at x W1 - L."""
    return TW.cyl(r, length, "x").translate([TW.W1 - L, 0, TW.RC])

def probe(p, y, z, x0, x1):
    """Bounding box of the material on a thin line along x at (y, z), from x0 to x1."""
    return (p ^ TW.box(x0, x1, y - 0.05, y + 0.05, z - 0.05, z + 0.05)).bounding_box()

def measure(bd):
    """Everything the picture and page print, from the model."""
    p, d = TW.build(bd=bd, **D_ARGS); W = TW.wires(L=60)
    bore_end = probe(p, 0, 0, TW.X0 + 1, 0.5)[3]                          # end of the material on the bore axis, outboard
    sleeve_end = probe(p, -0.5, 4.5, 0, TW.W1)[3]                         # stub sleeve end, above the bore
    w1 = (W ^ TW.box(0, (TW.W1 + TW.W2) / 2, -10, 70, -10, 20)).bounding_box(); w1_near, w1_c = w1[0], (w1[0] + w1[3]) / 2
    contact = w1_near - sleeve_end                                        # shift from the model seat to crosswire contact
    q = TW.turned(p, THETA); r13 = rod(r=TW.ROD - 0.02)
    hit = lambda s: ("rod" if (q.translate([s, 0, 0]) ^ r13).volume() > 1e-4 else "crosswire" if (q.translate([s, 0, 0]) ^ W).volume() > 1e-4 else None)
    s = -3.0
    while hit(s + 0.01) is None: s = round(s + 0.01, 2)
    by = hit(s + 0.01)
    qc = q.translate([contact, 0, 0]); lo, hi = 8.0, 25.0                  # longest stub that still lets it reach the crosswire
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if (qc ^ rod(mid, TW.ROD - 0.02)).volume() > 1e-4 else (mid, hi)
    ps = p.translate([s, 0, 0]); ov = ps ^ TW.wires(L=60)
    return dict(p=p, d=d, bd=0.0 - bore_end + 0.0, bore_end=bore_end, sleeve_end=sleeve_end, w1_near=w1_near, w1_c=w1_c, contact=contact, stop=s, by=by,
                lmax_formula=w1_c - (bore_end + contact), lmax=lo, ps=ps, ov=ov.volume(), ov_box=ov.bounding_box() if ov.volume() > 0 else None,
                grams=p.volume() * DENS, rod_end=rod().bounding_box()[0], short=w1_near - (sleeve_end + s))

def parts(M, grow=0.0):
    """(cut piece minus the wires, red overlap of the whole piece with the wires, wires minus the piece, rod) at the stop, turned back to 0."""
    ps = M["ps"]; W = TW.wires(L=WIRE_L)
    cut = ps ^ TW.box(TW.X0 - 5, 60, -30, 0, -30, 30)
    ov = ps ^ TW.wires(L=WIRE_L, grow=grow)
    return cut - W, ov, W - ps, rod()

def face_colors(V, N, xb, base=PIECE):
    """Per-face colors by centroid and normal (render3d load drops degenerate faces, so never by index): bore end faces bright."""
    c = V.mean(1); col = np.tile(base, (len(V), 1))
    end = (np.abs(c[:, 0] - xb) < 0.02) & (N[:, 0] > 0.99) & (c[:, 1] > -TW.BORE - 0.1) & (c[:, 1] < 0.01) & (np.abs(c[:, 2]) < TW.BORE + 0.1)
    col[end] = BRIGHT
    return col, end

def scene(M):
    R.FACES.clear(); cut, ov, w, r = parts(M); xb = M["bore_end"] + M["stop"]
    t = TW.tm(cut); V = t.vertices[t.faces]; N = t.face_normals; col, _ = face_colors(V, N, xb)
    c = V.mean(1); iscut = (np.abs(c[:, 1]) < 0.01) & (N[:, 1] > 0.99)
    R.FACES.extend((f, n, cc, bool(k)) for f, n, cc, k in zip(V, N, col, iscut))
    if M["ov"] > 1e-3: R.mesh(TW.tm(ov), RED)
    R.mesh(TW.tm(w), STEEL); R.mesh(TW.tm(r), STEEL)

def box_frame(lo, hi):
    """Frame (xmin, xmax, ymin, ymax) in view mm holding the box lo..hi seen from EYE."""
    e, right, up = R.camera(EYE); cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    u, v = cs @ right, cs @ up; return (u.min(), u.max(), v.min(), v.max())

def show(ax, frame, ppm):
    img, cam = R.render(EYE, ppm, frame=frame, edge_depth=1.0); ax.imshow(img); ax.axis("off"); return cam

def fmt(v): return f"{v:.1f}".replace("-", "\u2212")
def bdtxt(M): return "0" if abs(M["bd"]) < 0.05 else f"{M['bd']:.1f}"

CLOSE = (np.array([-8.0, -8.0, -6.0]), np.array([16.0, 4.0, 10.0]))      # the stub zone, x -8 to 16
PPM_WHOLE, PPM_CLOSE = 24.0, 80.0                                       # supersampled px per mm (images have half)

def picture(out, Ms):
    R.MIN_PX = 0
    fr = []
    for M in Ms:                                                        # one frame for every whole-piece panel: the union of the four scenes
        scene(M); fr.append(R.fit(EYE, pad=1.5))
    fr = np.array(fr); FW = (fr[:, 0].min(), fr[:, 1].max(), fr[:, 2].min(), fr[:, 3].max()); FC = box_frame(*CLOSE)
    H = 7.0; ww = H * (FW[1] - FW[0]) / (FW[3] - FW[2]); wc = H * (FC[1] - FC[0]) / (FC[3] - FC[2])
    TT, NB, GAP, ML, MID, TOPM, BOTM = 0.55, 0.75, 0.35, 0.25, 0.35, 1.0, 0.45
    FWd = ML + ww + MID + wc + ML; FH = TOPM + 4 * (TT + H + NB + GAP) + BOTM
    fig = plt.figure(figsize=(FWd, FH)); cam0 = camc = None
    for i, ((name, _), M) in enumerate(zip(OPTIONS, Ms)):
        scene(M); s = M["stop"]; xb = M["bore_end"] + s; xs = M["sleeve_end"] + s; xr = M["rod_end"]
        y0 = FH - TOPM - i * (TT + H + NB + GAP) - TT - H               # bottom of this row's images, inches
        top = f"{name}  bd {bdtxt(M)}" + (" (as modeled)" if abs(M["bd"]) < 0.05 else "")
        how = (f"stopped by the rod end on the bore end ({fmt(s)} from the model seat), shown turned back" if M["by"] == "rod"
               else f"stopped by the stub sleeve end on the first crosswire (+{M['contact']:.1f} from the model seat)")
        ax = fig.add_axes([ML / FWd, y0 / FH, ww / FWd, H / FH]); cam = show(ax, FW, PPM_WHOLE); cam0 = cam0 or cam
        ax.set_title(f"{top}: whole piece, {how}", fontsize=15, loc="left", fontweight="bold")
        R.call(ax, cam, (xb, -1.6, 2.2), (80, 120), "bore end" + (" (rod end on it)" if M["by"] == "rod" else ""), color=BRIGHT * 0.8, size=13)
        R.call(ax, cam, (TW.W1, WIRE_L - 4, TW.TOP), (-30, 75), "first crosswire", color="#222", size=12)
        R.call(ax, cam, (TW.W2, WIRE_L - 4, TW.TOP), (-10, 95), "second crosswire", color="#222", size=12)
        if M["ov"] > 1e-3:
            ob = M["ov_box"]; R.call(ax, cam, ((ob[0] + ob[3]) / 2, 1.5, ob[5]), (130, 75), "red: hook overlaps the first crosswire", color="#b00000", size=12)
        ax = fig.add_axes([(ML + ww + MID) / FWd, y0 / FH, wc / FWd, H / FH]); cam = show(ax, FC, PPM_CLOSE); camc = camc or cam
        ax.set_title(f"{top}: stub zone close-up, same direction", fontsize=15, loc="left", fontweight="bold")
        R.call(ax, cam, (xb, -1.6, 2.2), (95, 115), "bore end" + (" (rod end on it)" if M["by"] == "rod" else ""), color=BRIGHT * 0.8, size=13)
        R.call(ax, cam, (xr, 1.2, TW.RC - 1.0), (60, -120), f"rod end, {STUB:g} mm stub", color="#222", size=12)
        if xr - xb > 0.05:                                              # bore end to rod end, measured
            R.dim(ax, cam, (xb, 0, TW.BORE - 0.1), (xr, 0, TW.BORE - 0.1), (0, 0, TW.TOP + 1.6 - TW.BORE), color="#0b4f9c")
        if M["short"] > 0.05:                                           # stub sleeve end to the crosswire, measured
            a, b = np.array((xs, 0, TW.TOP)), np.array((M["w1_near"], 0, TW.TOP))
            R.dim(ax, cam, a, b, (0, 0, 1.6), text=f"{np.linalg.norm(b - a):.1f} short", color="#b00000")
            ob = M["ov_box"]; R.call(ax, cam, ((ob[0] + ob[3]) / 2, 1.0, ob[5] - 0.6), (-40, 105),
                                     f"red: hook overlaps the crosswire\n{ob[3] - ob[0]:.1f} along the rod: can't turn back", color="#b00000", size=12)
        else:
            R.call(ax, cam, (xs, -0.3, -4.4), (-80, -55), "stub sleeve end\non the first crosswire", color="#222", size=12)
        tx = fig.add_axes([ML / FWd, (y0 - NB) / FH, (ww + MID + wc) / FWd, NB * 0.8 / FH]); tx.axis("off")
        spare = M["lmax"] - STUB
        txt = (f"{name}:  bore runs {bdtxt(M)} past the modeled rod end   |   longest stub it takes {M['lmax_formula']:.1f} "
               f"({M['w1_c'] - M['contact']:.1f} + {bdtxt(M)}; slid in on the model: {M['lmax']:.2f})   |   "
               + (f"13 mm stub: {spare:.1f} to spare" if spare >= 0 else f"13 mm stub: {-spare:.1f} too long, stops {M['short']:.1f} short of the crosswire")
               + f"   |   {M['grams']:.1f} g (solid, 1.27 g/cm\u00b3)")
        tx.text(0.0, 0.5, txt, transform=tx.transAxes, fontsize=15, va="center", ha="left", bbox=dict(fc="#f6f6f6", ec="#999"))
    sax = fig.add_axes([ML / FWd, BOTM * 0.8 / FH, (ww + MID + wc) / FWd, 0.001]); sax.axis("off"); R.source(sax, os.path.abspath(__file__), None, size=11)
    sax.text(1.0, -0.02, f"1 px = {1 / cam0['ppm']:.3f} mm in the whole-piece panels, {1 / camc['ppm']:.3f} mm in the close-ups", transform=sax.transAxes,
             fontsize=11, color="#555", va="top", ha="right")
    fig.suptitle(f"Twist-lock front piece D: bore depth options on a {STUB:g} mm stub (the longest measured), each where it stops sliding on.\n"
                 f"Piece cut through the bore axis, rear half removed, seen from the rear, inboard and above; rod and crosswires not cut. "
                 f"Bore end bright blue. One view and scale per column.", fontsize=17, y=1 - 0.15 / FH, va="top")
    R.save(fig, out)

def page(out_dir, png, Ms):
    import zoompage as Z
    models = []
    for (name, _), M in zip(OPTIONS, Ms):
        cut, ov, _, _ = parts(M, grow=0.03)                 # the red overlap 0.03 over the wire surface, so it shows over the context wire
        T = Z.tris(cut); N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        col, _ = face_colors(T, N, M["bore_end"] + M["stop"])
        if M["ov"] > 1e-3:
            To = Z.tris(ov); T = np.concatenate([T, To]); col = np.concatenate([col, np.tile(RED, (len(To), 1))])
        xb = M["bore_end"] + M["stop"]
        labs = [((M["rod_end"], 0.0, TW.RC + TW.ROD), f"rod end, {STUB:g} mm stub"), ((xb, -1.5, 1.5), f"bore end, bd {bdtxt(M)}")]
        spare = M["lmax"] - STUB
        note = (f"{name}: bore runs {bdtxt(M)} past the modeled rod end; takes stubs up to {M['lmax_formula']:.1f}; "
                + (f"the 13 mm stub leaves {spare:.1f} to spare; stopped by the stub sleeve end on the first crosswire." if spare >= 0 else
                   f"the 13 mm stub is {-spare:.1f} too long: the rod end stops it on the bore end {M['short']:.1f} short of the crosswire, and turned back "
                   f"the hook overlaps the first crosswire (red, {M['ov']:.1f} mm\u00b3).") + f" {M['grams']:.1f} g solid.")
        if M["ov"] > 1e-3:
            ob = M["ov_box"]; labs.append((((ob[0] + ob[3]) / 2, 0.0, ob[5]), "hook overlaps the crosswire"))
        models.append(Z.Model(f"{name}  bd {bdtxt(M)}", T, rgb=col, labels=labs, note=note))
    ctx = [(Z.tris(rod()), tuple(STEEL + 0.12), "rod and crosswires"), (Z.tris(TW.wires(L=WIRE_L)), tuple(STEEL + 0.12), "rod and crosswires")]
    short = [(n, M) for (n, _), M in zip(OPTIONS, Ms) if M["by"] == "rod"]
    names = lambda L: ", ".join(L[:-1]) + " and " + L[-1] if len(L) > 1 else L[0]
    intro = (f"Four bore depths for the twist-lock front piece D, each cut through the bore axis and placed where it stops sliding onto a {STUB:g} mm stub "
             f"(the longest measured): {OPTIONS[0][0]} ends the bore at the modeled {Ms[0]['w1_c'] + Ms[0]['bore_end']:g} mm rod end, and "
             f"{names([n for (n, _), M in zip(OPTIONS[1:], Ms[1:])])} run it {names([bdtxt(M) for M in Ms[1:]])} mm deeper. "
             f"{names([n for (n, _), M in zip(OPTIONS, Ms) if M['by'] == 'crosswire'])} all reach the first crosswire with the {STUB:g} mm stub; "
             + " ".join(f"{n} stops {M['short']:.1f} short, so its hook hits the crosswire (red) when turned back." for n, M in short))
    html, files = Z.page(out_dir, "Bore Depth Options", intro, pictures=[(png, "Bore depth options Now, A, B, C: whole piece and stub zone close-up, "
                         "cut through the bore axis, seen from the rear; bore end bright blue, Now's overlap red.")], models=models, context=ctx,
                         eyebrow="Shelf · twist-lock front piece · bore depth", view=EYE,
                         source="Made by build/front-twist_bore_options.py from build/front-twist_model.py build(fw=4.5, fy=-1, hh=4.6, bd), "
                                "projects/3dp/products/shelf in nogbu/claude. Bore end bright blue; Now's overlap with the crosswire red.")
    return html, files

if __name__ == "__main__":
    a = sys.argv[1:]; pdir = None
    if "--page" in a:
        i = a.index("--page"); pdir = a[i + 1]; del a[i:i + 2]
    out = a[0] if a else "/mnt/project-files/images/shelf_frontTwist_boreDepth_options.png"
    Ms = [measure(bd) for _, bd in OPTIONS]
    for (name, _), M in zip(OPTIONS, Ms):
        print(f"{name}: bd {M['bd']:.2f}  bore end x {M['bore_end']:.2f}  sleeve end {M['sleeve_end']:.2f}  crosswire near {M['w1_near']:.2f} center {M['w1_c']:.2f}  "
              f"contact shift {M['contact']:.2f}  stop {M['stop']:+.2f} by {M['by']}  longest stub {M['lmax_formula']:.2f} (slid in {M['lmax']:.3f})  "
              f"spare {M['lmax'] - STUB:+.2f}  short {M['short']:.2f}  turned-back overlap {M['ov']:.2f} mm3  {M['grams']:.2f} g")
    picture(out, Ms)
    if pdir:
        html, files = page(pdir, out, Ms); print(json.dumps(dict(html=html, files=files)))

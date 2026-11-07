"""Front piece roof-strip fix options (front-fit-test_rev1 printed 2026-10-10: strings where the bore roof meets the channel,
the strip OrcaSlicer flags as a floating cantilever; log.md front-fit-test_rev1). All panels at one scale, print orientation
(front face on the bed, up = print up):
  A  support painted on the strip's underside (tree, manual), as OrcaSlicer slices it: support and interface toolpaths over
     x J0..XE from the slice, drawn on the section at x 20. The command-line slicer refuses the support-material interface
     (learnings/slicing-checks), so the slice uses PETG for the interface with 0.3 gaps; the GUI slice uses the preset's.
  B  open corner: the strip and the roof flat cut away, the bore's far roof face carried at 45 degrees to the rear face
     (section cut by hand here; the model's is front-piece_model.py open_corner, agreed change 40).
  C  sleeve standing up: the fit test piece on its glass-end face, bore vertical, side silhouette (reverses change 14).
painted(gap) returns (V, T, paint) for one fit test piece with the strip's underside painted.
Usage: python3 front-roof-fix_options.py [out.png]  (slices with /opt/orca/slice into a temporary folder)"""
import importlib.util, json, os, re, subprocess, sys, tempfile, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R, write3mf as W
spec = importlib.util.spec_from_file_location("fft", os.path.join(HERE, "front-fit-test_rev1.py"))
FT = importlib.util.module_from_spec(spec); spec.loader.exec_module(FT)
F = FT.O.F
OF = 7.45                                       # bore center height in print (model y 0)
PIECE = (0.93, 0.62, 0.30); ROD = (0.30, 0.30, 0.33)

def painted(gap=0.3):
    """Fit test piece in print orientation with paint_supports on the strip's 45-degree underside (x J0..XE, z 9.2-11.2)."""
    V, T = FT.printed(gap, 2); P = V[T]
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); L = np.linalg.norm(n, axis=1); n = n / np.where(L > 0, L, 1)[:, None]; c = P.mean(1)
    sel = (n[:, 2] < -0.5) & (n[:, 1] > 0.5) & (c[:, 2] > 9.2) & (c[:, 2] < 11.2) & (c[:, 1] > -2.6) & (c[:, 1] < -0.6) & (c[:, 0] > F.J0 - 0.5)
    return V, T, ['paint_supports="4"' if k else "" for k in sel]

def support_paths(gcode, c):
    """Support and interface extrusion points, mapped back to print coordinates (object centered at 128, 128; Orca's G-code
    y sits 2.0 below the 3mf's, measured on this piece's walls 2026-10-10)."""
    X = Y = z = 0.0; t = ""; out = []
    for ln in open(gcode):
        if ln.startswith("; Z_HEIGHT:"): z = float(ln.split(":")[1])
        elif ln.startswith("; FEATURE:"): t = ln.split(":", 1)[1].strip()
        elif ln.startswith("G1"):
            d = dict(re.findall(r"([XYE])(-?[\d.]+)", ln.split(";")[0])); nx, ny = float(d.get("X", X)), float(d.get("Y", Y))
            if float(d.get("E", 0)) > 0 and t.startswith("Support"):
                for s in np.linspace(0, 1, max(2, int(np.hypot(nx - X, ny - Y) / 0.3) + 1)):
                    out.append((X + (nx - X) * s - 128 + c[0], Y + (ny - Y) * s - 128 + c[1] + 2.0, z, t == "Support interface"))
            X, Y = nx, ny
    return np.array(out)

def section(V, T, x=20.0):
    import trimesh
    sec = trimesh.Trimesh(V, T).section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    polys = [Polygon(np.c_[e[:, 1], e[:, 2]]) for e in sec.discrete if len(e) > 3]
    shape = polys[0]
    for q in polys[1:]: shape = shape.symmetric_difference(q)
    return shape

def draw(ax, shape, col=PIECE):
    for g in getattr(shape, "geoms", [shape]):
        ax.fill(*g.exterior.xy, color=col, ec="k", lw=1)
        for h in g.interiors: ax.fill(*h.xy, color="white", ec="k", lw=1)

if __name__ == "__main__":
    V, T, paint = painted(0.3); c = (V.min(0) + V.max(0)) / 2
    tmp = tempfile.mkdtemp()
    st = dict(json.load(open(os.path.join(HERE, "petgBasic_settings_base.json"))), support_interface_filament="1",
              support_top_z_distance="0.3", support_bottom_z_distance="0.3")
    W.write(os.path.join(tmp, "a.3mf"), [W.Obj("front-fit-test_0.3_painted", [W.Part(V, T, paint=paint)], at=[(128, 128)])], st)
    print(subprocess.run(["/opt/orca/slice", os.path.join(tmp, "a.3mf"), os.path.join(tmp, "out")], capture_output=True, text=True).stdout)
    S = support_paths(os.path.join(tmp, "out", "plate_1.gcode"), c)
    shape = section(V, T)
    # B: cut away the strip and flat above the 45-degree line through the far roof face (z_rel = 4.38 - y), y < 0.73, z_rel > 1.5
    cut = Polygon([(-2.9, OF + 1.5), (-2.9, OF + 4.38 + 2.9), (0.73, OF + 4.38 - 0.73), (0.73, OF + 1.5)])
    shapeB = shape.difference(cut)
    # C: side silhouette standing on the glass-end face: print y across, model x up
    P = V[T]; sil = unary_union([Polygon(np.c_[p[:, 1], p[:, 0] + 2.48]).buffer(0) for p in P if Polygon(np.c_[p[:, 1], p[:, 0]]).area > 1e-6])
    S_IN = 0.36                                  # inches per mm, every panel
    xl = (-11.0, 7.0); ylA = (-0.5, 14.5); ylC = (-0.5, 46.0)
    wmm = xl[1] - xl[0]; hA = ylA[1] - ylA[0]; hC = ylC[1] - ylC[0]
    Wf = 3 * wmm * S_IN + 3.0; Hf = hC * S_IN + 3.2
    fig = plt.figure(figsize=(Wf, Hf))
    axes = []
    for k, h in enumerate((hA, hA, hC)):
        left = (0.6 + k * (wmm * S_IN + 1.0)) / Wf; bottom = (Hf - 1.9 - h * S_IN) / Hf
        axes.append(fig.add_axes([left, bottom, wmm * S_IN / Wf, h * S_IN / Hf]))
    a, b, cc = axes
    draw(a, shape); m = (S[:, 0] > F.J0) & (S[:, 0] < F.XE)
    a.scatter(S[m & (S[:, 3] == 0), 1], S[m & (S[:, 3] == 0), 2], s=3, c="#1f5fa8", label="support (all of x 10.25 to 42 projected)")
    a.scatter(S[m & (S[:, 3] == 1), 1], S[m & (S[:, 3] == 1), 2], s=3, c="#c0392b", label="support interface")
    a.legend(loc="upper left", fontsize=10, markerscale=4, frameon=False)
    a.set_title("A  Support painted on the strip's underside\nAgreed shape kept. Support stands on the channel floor and the\n"
                "bore floor along the sleeve and is picked out after printing.\nFrom OrcaSlicer's slice of one piece (PETG interface here).",
                fontsize=12, loc="left")
    draw(b, shapeB)
    b.annotate("strip and roof flat cut away; the far roof\nface runs on at 45° to the rear face", (-1.4, OF + 5.0), (-10.8, 11.3), fontsize=11,
               arrowprops=dict(arrowstyle="->", color="#555"))
    b.set_title("B  Open corner\nNo support and no bridge; same depth. The rod is then pressed\ndown only by the near edge of the bore "
                "opening and the roof\nover the crosswire (inference; stress check before build).", fontsize=12, loc="left")
    draw(cc, sil)
    for y in (-F.BORE, F.BORE): cc.plot([y, y], [2.48, F.XE + 2.48], "--", color="#333", lw=1)
    cc.annotate("bore (dashed) runs\nstraight up; no overhangs", (F.BORE, 30), (1.0, 45.0), fontsize=11, arrowprops=dict(arrowstyle="->", color="#555"))
    cc.annotate("glass-end face on the bed", (-4, 0), (-10.8, 2.0), fontsize=11, arrowprops=dict(arrowstyle="->", color="#555"))
    cc.set_title("C  Sleeve standing up (fit test piece, side view)\nNo overhangs. Reverses change 14: the full piece stands 87 tall,\n"
                 "and the bore size needs retesting upright.", fontsize=12, loc="left")
    for ax, yl in zip(axes, (ylA, ylA, ylC)):
        ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect("equal"); ax.axis("off")
    for ax in (a, b):
        ax.add_patch(plt.Circle((0.15, OF), F.ROD, color=ROD, alpha=0.5))
        ax.annotate("bed (front face)", (-10.3, 0), (-10.3, -0.45), fontsize=10)
    fig.suptitle("Front piece roof strip fixes, all at one scale (1 mm = %.2f in), print orientation. A and B: section at x 20, rod grey. "
                 "Drawn from front-fit-test_rev1.py's piece (0.3 gap)." % S_IN, fontsize=13, y=1 - 0.4 / Hf)
    R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_frontRoofFix_options.png")

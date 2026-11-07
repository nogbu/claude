"""Front piece roof-strip fixes in 3D, all panels at one scale (companion to front-roof-fix_options.py's sections): the
front fit test piece (0.3 gap) as printed, with the strip that starts over air in red; A with the support OrcaSlicer
slices for it (PETG interface in this slice); B the open corner (strip and roof flat cut away along x J0..XE);
C standing on its glass-end face. strip_split(p) works on front-fittest_options.piece() manifolds; B is piece(..., open_corner=True) (agreed change 40).
Usage: python3 front-roof-fix_3d.py [out.png]  (slices the painted piece with /opt/orca/slice into a temporary folder)"""
import importlib.util, json, os, re, subprocess, sys, tempfile, numpy as np, trimesh, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R, write3mf as W
spec = importlib.util.spec_from_file_location("frfo", os.path.join(HERE, "front-roof-fix_options.py"))
FO = importlib.util.module_from_spec(spec); spec.loader.exec_module(FO)
FT, F, OF = FO.FT, FO.F, FO.OF
PIECE = np.array([0.93, 0.62, 0.30]); RED = np.array([0.85, 0.15, 0.12]); RODC = np.array([0.45, 0.45, 0.48])
SUP = np.array([0.25, 0.45, 0.80]); IFACE = np.array([0.55, 0.75, 0.95])

def strip_split(p):
    """(rest, strip): the strip is the material between the channel and the bore roof's near 45-degree face, print z 9.3-11.1
    (model y 1.85-3.65), print y -2.6 to -0.7 (model z 0.7-2.6), along the opening x J0..XE."""
    s = p ^ F.box(F.J0, F.XE + 1, 1.85, 3.65, 0.7, 2.6)
    return p - s, s


def printed(man):
    """trimesh in print orientation: print (x, y, z) = model (x, -z, y + OF)."""
    t = F.tm(man); v = t.vertices
    return trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1] + OF], t.faces)

def standing(man):
    """trimesh standing on the glass-end face: (print y, print z, model x + 2.48)."""
    t = F.tm(man); v = t.vertices
    return trimesh.Trimesh(np.c_[-v[:, 2], v[:, 1] + OF, v[:, 0] + 2.48], t.faces)

def support_cubes(gcode, c, size=0.45):
    """Small cubes along the slice's support and interface lines, in print coordinates (see FO.support_paths)."""
    S = FO.support_paths(gcode, c)
    for x, y, z, iface in S[::2]:
        R.box(x - size / 2, x + size / 2, y - size / 2, y + size / 2, z - 0.3, z, IFACE if iface else SUP)
    return len(S)

if __name__ == "__main__":
    p, d = FT.O.piece(0.3, True, 2)
    rest, strip = strip_split(p); B, _ = FT.O.piece(0.3, True, 2, open_corner=True)
    rod = F.cyl(F.ROD, 52.0, "x").translate([-0.5, 0, F.RC])
    V, T, paint = FO.painted(0.3); c = (V.min(0) + V.max(0)) / 2
    tmp = tempfile.mkdtemp()
    st = dict(json.load(open(os.path.join(HERE, "petgBasic_settings_base.json"))), support_interface_filament="1",
              support_top_z_distance="0.3", support_bottom_z_distance="0.3")
    W.write(os.path.join(tmp, "a.3mf"), [W.Obj("front-fit-test_0.3_painted", [W.Part(V, T, paint=paint)], at=[(128, 128)])], st)
    subprocess.run(["/opt/orca/slice", os.path.join(tmp, "a.3mf"), os.path.join(tmp, "out")], capture_output=True)
    R.MIN_PX = 0; PPM = 14.0
    EYE = (1.0, -0.62, 0.62)                    # from the sleeve tip, the channel side and above (the photo's end)
    EYE_S = (-0.75, -0.55, 0.5)                 # standing piece: from the channel side and above
    panels = []
    R.FACES.clear(); R.mesh(printed(rest), PIECE); R.mesh(printed(strip), RED); R.mesh(printed(rod), RODC)
    img, cam = R.render(EYE, PPM, frame=R.fit(EYE, 2.0)); panels.append(("As printed: the red strip starts over air", img, cam))
    R.FACES.clear(); R.mesh(printed(rest), PIECE); R.mesh(printed(strip), RED)
    n = support_cubes(os.path.join(tmp, "out", "plate_1.gcode"), c)
    img, cam = R.render(EYE, PPM, frame=R.fit(EYE, 2.0)); panels.append(("A  Support under the strip (blue; light blue = interface)", img, cam))
    R.FACES.clear(); R.mesh(printed(B), PIECE)
    img, cam = R.render(EYE, PPM, frame=R.fit(EYE, 2.0)); panels.append(("B  Open corner: strip and roof flat cut away", img, cam))
    R.FACES.clear(); R.mesh(standing(rest), PIECE); R.mesh(standing(strip), RED)
    img, cam = R.render(EYE_S, PPM, frame=R.fit(EYE_S, 2.0)); panels.append(("C  Sleeve up: standing on the glass end", img, cam))
    Wm = max(q[1].shape[1] for q in panels); Hm = max(q[1].shape[0] for q in panels)
    fig, axes = plt.subplots(1, 4, figsize=(40, 40 * Hm / (4 * Wm) + 3.5))
    for ax, (title, img, cam) in zip(axes, panels):
        R.place(ax, img, Wm, Hm); ax.set_title(title, fontsize=15, loc="left", fontweight="bold")
    c0 = panels[0][2]
    R.call(axes[0], c0, (F.XE - 8.0, -2.4, 10.6), (-150, 120), "failed strip: x 10.25 to 42,\nprint height 9.3 to 11.1", color="#c0392b", size=12)
    R.call(axes[0], c0, (F.XE - 4.0, -4.2, 3.4), (-190, -10), "channel (crosswires)", color="#555", size=12)
    R.call(axes[0], c0, (48.0, 0.15, OF - 2.0), (40, 60), "front edge rod", color="#555", size=12)
    R.call(axes[2], panels[2][2], (F.XE, -1.0, 12.0), (-80, -80), "far roof face runs on at 45°", color="#555", size=12)
    R.call(axes[3], panels[3][2], (-2.0, 7.45, 44.4), (-60, -60), "sleeve tip (top)", color="#555", size=12)
    R.call(axes[3], panels[3][2], (2.0, 0.0, 0.5), (-160, -40), "glass-end face on the bed", color="#555", size=12)
    R.source(axes[0], os.path.abspath(__file__), c0)
    fig.suptitle("Front fit test piece (0.3 gap) and the three roof-strip fixes, all at one scale. As printed, A and B lie on the front face "
                 "(print orientation), seen from the sleeve tip, the channel side and above. A's support is from OrcaSlicer's slice.", fontsize=16)
    R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_frontRoofFix_3d.png")
    print("support points", n, "strip volume", round(strip.volume(), 1), "B removed", round(p.volume() - B.volume(), 1))

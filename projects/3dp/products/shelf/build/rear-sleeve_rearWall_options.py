"""Rear piece lip-rod sleeve: rear wall options for the card (after the 2026-10-10 3D check found the open C's knife-edge lips at
80-93 MPa). A: open the whole height, lips trimmed to one bead. B: rear wall closed below the lip crosswires' ends (1.75 under the
rod center: the wire's radius plus 0.3), upper lip trimmed. Each option: 3D from the rear with the rods and a lip crosswire, and the
section at x 20 end-on. From rear-piece_model.py. Usage: python3 rear-sleeve_rearWall_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
ROD, WIRE, BORE, LIPB, LIPZ, W1, J0 = RP.ROD, RP.WIRE, RP.BORE, RP.LIPB, RP.LIPZ, RP.W1, RP.J0
CLOSE = -(WIRE + 0.3)
opts = [("A  Open the whole height, lips trimmed to one bead", dict(trim=True)),
        (f"B  Rear wall closed below the wire ends ({-CLOSE:.2f} under the rod center), upper lip trimmed", dict(close_below=CLOSE, trim=True))]
PIECE = np.array([0.93, 0.62, 0.30]); WIREC = np.array([0.22, 0.22, 0.24]); CUT = np.array([0.80, 0.80, 0.86])
def section_parts():
    rods = RP.rods(55)
    wires = [m.Manifold.cylinder(RP.WB + WIRE - LIPZ, WIRE, WIRE, 24).translate([x, ROD + WIRE, LIPZ]) for x in (W1, W1 + 25.3)]
    return rods, m.Manifold.batch_boolean(wires, m.OpType.Add)
fig, axes = plt.subplots(2, 2, figsize=(24, 20), gridspec_kw=dict(height_ratios=[1.1, 1]))
for col, (title, kw) in enumerate(opts):
    piece, d = RP.build(**kw); rods, wires = section_parts()
    ax = axes[0][col]; R.FACES.clear()
    R.mesh(RP.tm(piece), PIECE); R.mesh(RP.tm(rods), WIREC); R.mesh(RP.tm(wires), WIREC)
    cam = R.view(ax, eye=(0.7, 1.0, 0.45), ppm=5.0, pad=6)
    ax.set_title(title, fontsize=15, loc="left", fontweight="bold")
    R.call(ax, cam, (W1, ROD + 2 * WIRE, LIPZ + 12), (90, 40), "lip crosswire (runs down to the rod's rear, center height)", color="#222", size=11)
    R.call(ax, cam, (30, d["rear"], LIPB), (80, -60), "rear opening" if kw.get("close_below") is None else "rear opening, above the wire ends only", color="#a85a00", size=11)
    R.call(ax, cam, (-5, d["yr"], RP.ZB - 10), (-70, -50), "drop (stub zone)", color="#555", size=11)
    ax = axes[1][col]; R.FACES.clear()
    cutbox = RP.box(18.5, 20.0, -20, 20, -42, -20)                # a 1.5 mm slab of the sleeve at x 20, seen from +x
    R.mesh(RP.tm(piece ^ cutbox), PIECE); R.mesh(RP.tm(rods ^ cutbox), WIREC); R.mesh(RP.tm(wires ^ RP.box(-60, 60, -20, 20, -42, -20)), WIREC)
    cam = R.view(ax, eye=(1.0, 0.0, 0.0), ppm=24.0, pad=2.5)
    ax.set_title("Sleeve section at x 20, end-on from the inboard end (rear to the right)", fontsize=13, loc="left")
    R.call(ax, cam, (20, d["rear"], LIPB + 1.8), (90, 50), "upper lip (one bead)", color="#a85a00", size=11)
    R.call(ax, cam, (20, d["rear"] if kw.get("close_below") is None else d["yr"], LIPB - 2.5), (90, -50),
           "lower lip (one bead)" if kw.get("close_below") is None else "rear wall, full thickness", color="#a85a00", size=11)
    R.call(ax, cam, (20, ROD + WIRE, LIPZ + 4), (70, 50), "crosswire (slides along the opening)", color="#222", size=11)
    dz = np.sqrt(BORE ** 2 - (d["rear"] - RP.F.BEAD) ** 2)
    R.dim(ax, cam, (20, d["rear"], LIPB + dz), (20, d["rear"], LIPB + (CLOSE if kw.get("close_below") is not None else -dz)), (0, 5.5, 0))
R.source(axes[1][0], os.path.abspath(__file__), cam)
fig.suptitle("Lip-rod sleeve rear wall options (reach 40, walls 2.48 / 2.35). Fillets left out except the sleeve root.", fontsize=16)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearSleeve_rearWallOptions.png")

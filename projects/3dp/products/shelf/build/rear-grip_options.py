"""Rear piece grip options, quick end-on view (shelf state.md open decision 3); unsized concept blocks.
Rear corner rod at y 0 (deck runs toward -y), lip outer rod 32.3 below it; crosswires over the rear corner rod and down the
lip's rear face, rods inside the bend (photo 20260930_142030). Constants from front-piece_model.py.
Grey: stub sleeves (agreed change 1). Orange: grip past the first crosswire. Usage: python3 rear-grip_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("front_piece_model", os.path.join(HERE, "front-piece_model.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
ROD, WIRE, BORE, C, RC, WB, TOP, ZB, X0, W1, XE, J0, ROOF = (F.ROD, F.WIRE, F.BORE, F.C, F.RC, F.WB, F.TOP, F.ZB, F.X0,
                                                            F.W1, F.XE, F.J0, F.ROOF)
LIPZ = RC - 32.3; OF = 7.45; YW = ROD + 2 * WIRE          # lip outer rod; rear face behind the rod (front piece's); wire rear face
box, cyl = F.box, F.cyl
def bores(x1): return cyl(BORE, x1 + 1, "x").translate([0, 0, RC]) + cyl(BORE, x1 + 1, "x").translate([0, 0, LIPZ])
def stub():                                                  # agreed change 1 placeholder: body on the clip, drop around the lip rod
    b = box(X0, J0, -13, OF, ZB, TOP) + box(-15, J0, OF - 13, OF, LIPZ - 6, ZB)
    return b - bores(J0) + cyl(BORE, 0.01, "x")
def inside():                                                # lip-rod sleeve run past the crosswires, inside the bend, open at the rear
    b = box(J0, XE, -13, ROD - C, LIPZ - ROD - 3, LIPZ + ROD + 4)
    return b - bores(XE)
def cap():                                                   # corner cap outside the bend: roof over the deck wires, wall behind the lip wires
    roof = box(J0, XE, -10, YW + C + 3, TOP + C, TOP + C + ROOF)
    wall = box(J0, XE, YW + C, YW + C + 3, ZB, TOP + C)
    return roof + wall
def section():
    parts = [cyl(ROD, 70, "x").translate([0, 0, RC]), cyl(ROD, 70, "x").translate([0, 0, LIPZ])]
    for x in (W1, W1 + 25.3, W1 + 50.6):
        parts.append(cyl(WIRE, 28 + ROD + WIRE, "y").translate([x, -28, WB + WIRE]))
        parts.append(m.Manifold.cylinder(WB + WIRE - LIPZ, WIRE, WIRE, 24).translate([x, ROD + WIRE, LIPZ]))
    return m.Manifold.batch_boolean(parts, m.OpType.Add)
clip = box(X0 + 0.5, X0 + 15.5, OF - 12.4, OF, ZB - 0.9, ZB)
STEEL = np.array([0.55, 0.6, 0.66]); WIREC = np.array([0.22, 0.22, 0.24]); GREY = np.array([0.80, 0.80, 0.86]); GRIP = np.array([0.93, 0.62, 0.30])
opts = [("A  Lip-rod sleeve inside the bend", [inside()]), ("B  Both: lip-rod sleeve plus corner cap", [inside(), cap()])]
fig, axes = plt.subplots(1, 2, figsize=(22, 12))
eye = (1.0, -0.42, 0.22)
for ax, (title, grips) in zip(axes, opts):
    R.FACES.clear()
    R.mesh(F.tm(stub()), GREY); R.mesh(F.tm(section()), WIREC); R.mesh(F.tm(clip), STEEL)
    for g in grips: R.mesh(F.tm(g), GRIP)
    cam = R.view(ax, eye=eye, ppm=6.0, pad=8)
    ax.set_title(title, fontsize=17, loc="left", fontweight="bold")
    R.call(ax, cam, (XE, -13, LIPZ - 4), (-120, -50), "lip-rod sleeve past the crosswires;\nthe lip rod pushes up on its top", color="#a85a00", size=11)
    R.call(ax, cam, (W1 + 25.3, ROD + 2 * WIRE, LIPZ + 14), (120, 10), "lip crosswires pass\nbehind (open at the rear)", color="#222", size=11)
    R.call(ax, cam, (J0, -13, ZB + 4), (-120, 40), "stub sleeves (agreed change 1)", color="#555", size=11)
    R.call(ax, cam, (70, 0, RC + ROD), (60, 50), "rear corner rod", color="#222", size=11)
    R.call(ax, cam, (70, 0, LIPZ - ROD), (70, -40), "lip outer rod", color="#222", size=11)
    R.call(ax, cam, (W1 + 50.6, -28, TOP), (-60, 50), "deck crosswires", color="#222", size=11)
    if len(grips) > 1:
        R.call(ax, cam, (J0 + 5, -10, TOP + C + ROOF), (-60, 60), "corner cap: roof over the deck crosswires,\nwall behind the lip (rear face moves back)", color="#a85a00", size=11)
R.source(axes[0], os.path.abspath(__file__), cam)
fig.suptitle("Rear piece grip options, left end, seen from inside the shelf (front of the shelf to the left). Unsized, fillets left out.\n"
             "Grey: stub sleeves. Orange: the grip past the first crosswire.", fontsize=16)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearGrip_quick.png")

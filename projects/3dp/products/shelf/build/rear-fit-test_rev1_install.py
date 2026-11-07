"""How rear-fit-test_rev1 goes on (shelf agreed change 38): the 32.3 piece slid onto a section's left rear corner, rod ends at
x 0 (glass side -x), in three steps at one scale: lined up, the lip rod in its sleeve with the rear corner rod at its bore's mouth,
and seated with the lip crosswires through the rear opening. Rods and crosswires as rear-grip_options.py. Usage:
python3 rear-fit-test_rev1_install.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
spec = importlib.util.spec_from_file_location("opts", os.path.join(HERE, "rear-fittest_options.py"))
O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)
RP = O.RP; SP = 32.3
p, d = O.piece(SP, True, 2)                                    # sets RP.LIPB / LIPZ for this spacing
PIECE = np.array([0.93, 0.62, 0.30]); WIREC = np.array([0.30, 0.30, 0.33])
def section(L=90.0):
    parts = [RP.rods(L)]
    for x in (RP.W1, RP.W1 + 25.3, RP.W1 + 50.6):
        parts.append(RP.cyl(RP.WIRE, 30 + RP.ROD + RP.WIRE, "y").translate([x, -30, RP.WB + RP.WIRE]))         # deck crosswire on the rod
        parts.append(m.Manifold.cylinder(RP.WB + RP.WIRE - RP.LIPZ, RP.WIRE, RP.WIRE, 24).translate([x, RP.ROD + RP.WIRE, RP.LIPZ]))  # down the lip's rear face
    return m.Manifold.batch_boolean(parts, m.OpType.Add)
SEC = RP.tm(section())
steps = [(55.0, "1  Line it up: bores toward the rod ends, open slot toward the lip crosswires"),
         (RP.J0, f"2  Slide it on: the lip rod goes in first; after about {40 - RP.J0:.0f} mm the rear corner rod reaches its bore"),
         (0.0, "3  Push until the end wall meets the rod ends: both rods in, crosswires through the slot, no rocking")]
EYE = (0.75, 1.0, 0.55); R.MIN_PX = 0; PPM = 8.0
imgs = []
for s, t in steps:
    R.FACES.clear(); R.mesh(SEC, WIREC); R.mesh(RP.tm(p.translate([-s, 0, 0])), PIECE)
    if not imgs: FRAME = R.fit(EYE, 6.0)                     # step 1 spans the most; every panel uses its frame
    img, cam = R.render(EYE, PPM, frame=FRAME); imgs.append((s, t, img, cam))
Wm = max(i[2].shape[1] for i in imgs); Hm = max(i[2].shape[0] for i in imgs)
fig, axes = plt.subplots(1, 3, figsize=(36, 36 / 3 * Hm / Wm + 2))
for ax, (s, t, img, cam) in zip(axes, imgs):
    R.place(ax, img, Wm, Hm); ax.set_title(t, fontsize=13, loc="left", fontweight="bold", wrap=True)
    R.call(ax, cam, (80, 0, RP.RC + RP.ROD), (40, -50), "rear corner rod", color="#222", size=11)
    R.call(ax, cam, (85, 0, RP.LIPZ - RP.ROD), (40, 50), "lip outer rod", color="#222", size=11)
    if s > 0:
        a = R.proj(cam, (-s + 5, d["yr"], RP.LIPB - 8)); b = R.proj(cam, (-s + 30, d["yr"], RP.LIPB - 8))
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=3, color="#a85a00", mutation_scale=30))
        R.call(ax, cam, (-s + 5, d["yr"], RP.LIPB - 8), (-20, 80), "test piece (2 grooves = 32.3),\nslides on along the rods", color="#a85a00", size=11)
    else:
        R.call(ax, cam, (RP.W1 + 25.3, RP.ROD + RP.WIRE, RP.LIPZ + 10), (60, 110), "lip crosswires pass\nthrough the open slot", color="#222", size=11)
R.source(axes[0], os.path.abspath(__file__), imgs[0][3])
fig.suptitle("rear-fit-test_rev1 going onto a section's left rear corner, seen from the rear, inboard and above (lip hanging down). "
             "Do each piece the same way; the lip is the section's rear edge, bent down.", fontsize=14)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearFitTest_rev1_install.png")

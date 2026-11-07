"""Lip-rod sleeve reach options for the card (open decision 3): the rear piece (closed rear wall, agreed change 28) at each reach,
from the rear and a little below with the rods and lip crosswires, with its loads, beam root stress, Hertz contact and solid grams from
rear-sleeve_beam.py options() (inference). Usage: python3 rear-sleeve_reach_options.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_sleeve_beam", os.path.join(HERE, "rear-sleeve_beam.py"))
BM = importlib.util.module_from_spec(spec); spec.loader.exec_module(BM); RP = BM.RP
REACHES = (20.0, 30.0, 40.0); THREE_D = {40.0: "3D: 34 coarse / 41 fine along, 16 / 14 across"}
PIECE = np.array([0.93, 0.62, 0.30]); WIREC = np.array([0.22, 0.22, 0.24]); STEEL = np.array([0.55, 0.6, 0.66])
def wires():
    return m.Manifold.batch_boolean([m.Manifold.cylinder(RP.WB + RP.WIRE - RP.LIPZ, RP.WIRE, RP.WIRE, 24).translate([x, RP.ROD + RP.WIRE, RP.LIPZ])
                                     for x in (RP.W1, RP.W1 + 25.3, RP.W1 + 50.6)], m.OpType.Add)
def zoom(ax, eye, lo, hi, ppm):
    """Render the scene framed on the box lo..hi (same scale in every panel)."""
    e, right, up = R.camera(eye); cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    u, v = cs @ right, cs @ up
    img, cam = R.render(eye, ppm, frame=(u.min(), u.max(), v.min(), v.max())); ax.imshow(img); ax.axis("off"); return cam
fig = plt.figure(figsize=(30, 13)); gs = fig.add_gridspec(2, 3, height_ratios=[3.2, 1])
axes = [fig.add_subplot(gs[0, i]) for i in range(3)]; taxes = [fig.add_subplot(gs[1, i]) for i in range(3)]
for ax, tax, reach in zip(axes, taxes, REACHES):
    o = BM.options(reach); piece, d = RP.build(reach=reach, close_below=BM.CLOSE, trim=True)
    clip = RP.box(RP.X0 + 0.5, RP.X0 + 15.5, d["yr"] - 12.4, d["yr"], RP.ZB - 0.9, RP.ZB)
    R.FACES.clear(); R.mesh(RP.tm(piece), PIECE); R.mesh(RP.tm(RP.rods(70)), WIREC); R.mesh(RP.tm(wires()), WIREC); R.mesh(RP.tm(clip), STEEL)
    cam = zoom(ax, (0.45, 1.0, -0.2), np.array([-14, -6, -42]), np.array([46, 8, 7]), 14.0)
    ax.set_title(f"Reach {reach:g} (sleeve end x {reach:g}, {reach - RP.J0:.1f} past the first crosswire)", fontsize=15, loc="left", fontweight="bold")
    a = np.array(R.proj(cam, (reach - 1.25, 0, d["zt"]))); b = np.array(R.proj(cam, (reach - 1.25, 0, d["zt"] + 9)))
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=3, mutation_scale=25))
    ax.text(b[0] - 12, b[1] + 6, f"lip rod pushes up\n{o['P']:.0f} N at the tip", color="#c0392b", fontsize=12, fontweight="bold", ha="right", va="top",
            bbox=dict(fc="white", ec="none", alpha=0.9))
    R.call(ax, cam, (5, d["yr"], RP.LIPB - 3), (-90, 40), f"rod ends push down {o['stubs']:.0f} N", color="#c0392b", size=11)
    R.call(ax, cam, (RP.W1 + 25.3, RP.ROD + RP.WIRE, RP.LIPZ + 14), (70, 50), "second lip crosswire", color="#222", size=11)
    R.call(ax, cam, (reach - 3, d["yr"], RP.LIPB - 3), (60, -75), "lip-rod sleeve, rear wall closed below the wires", color="#a85a00", size=11)
    txt = (f"Sleeve root (beam): {o['root']:.0f} MPa along the layers (limit 75)\n"
           f"Contact at the tip (Hertz): {o['tip25'][1]:.0f} MPa over 2.5 mm, {o['tip15'][1]:.0f} over 1.5 (first yield about 58)\n"
           f"Stub floors (Hertz): {o['stub'][1]:.0f} MPa\nSolid weight: {o['grams']:.1f} g a piece\n" + THREE_D.get(reach, "3D: not run"))
    tax.axis("off"); tax.text(0.0, 1.0, txt, transform=tax.transAxes, fontsize=13, va="top", ha="left", bbox=dict(fc="#f6f6f6", ec="#999"))
R.source(axes[0], os.path.abspath(__file__), cam)
fig.suptitle("Lip-rod sleeve reach options: rear piece seen from the rear and a little below, rear wall closed below the wires (agreed change 28). "
             "15 lb x 3 per corner; inference.", fontsize=16)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearSleeve_reachOptions.png")

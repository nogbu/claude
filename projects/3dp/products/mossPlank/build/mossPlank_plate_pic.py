"""mossPlank sliding hex plate (my ask 2026-10-10: "make the hexagon face a plate that slides in from the top of the pole",
its face flush with the side rails' faces, printed face down). Read as: plates drop down the assembled pole from its top,
each resting on the one below and the lowest on the post's top edge (inference from "from the top of the pole").
Section: D body without its front wall; at each front corner a rail, 2.0 mm at the face (change 7's strip width), whose lip
holds the plate's edge in a dovetail groove: plate edge straight for 1.2 mm (4 layers, fit feature 1 mm above the bed),
then a 45 deg flank 0.6 mm out to the plate's back face at 1.8 mm (6 layers at 0.30). Clearance 0.2 mm (dp 6 snug) at the
face slot, the groove's outer side and the back; the flank is where the plate bears, so moss pushing out leaves it flush.
A back lip (1.24 mm, 2 beads) behind each plate edge keeps it from falling in (top end a 45 deg run-out); cut away in the top socket, where the next
section's spigot sits behind the plate. Spigot, tabs and windows unchanged; spigot front wall keeps its hexes, the hidden ramp behind the plate goes solid.
Plate: 199.6 mm tall (0.4 mm short of the section, inference), hexes option B clipped 2.0 mm in from its side edges and
1.0 mm in from its ends (two stacked ends make a 2.0 mm rib). Fillets left out.
Usage: python3 mossPlank_plate_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
WR, TP, YS, E, C, BL = 2.0, 1.8, 1.2, 0.6, 0.2, 1.24      # rail face, plate thickness, straight edge, flank, clearance, back lip
HP = H - 0.4
xp = W / 2 - WR - C                                        # plate half-width at the face
def sym(pts):                                              # right-side points (x > 0, front to back) -> closed symmetric polygon
    return ccw([(x, y) for x, y in pts] + [(-x, y) for x, y in reversed(pts)])
def ext_xy(poly, z0, z1):
    return mf.Manifold.extrude(mf.CrossSection([poly]), z1 - z0).translate([0, 0, z0])
plate2d = sym([(xp, d), (xp, d + YS), (xp + E, d + TP)][::-1])
xg = xp + E + C                                            # groove's outer side
chan2d = sym([(W / 2 - WR, d - 5), (W / 2 - WR, d + YS + C), (xg - C + C, d + YS + C + (xg - (W / 2 - WR))) if False else (W / 2 - WR, d + YS + C),
              (xg, d + YS + C + (xg - (W / 2 - WR))), (xg, d + TP + C), (0.01, d + TP + C)][::-1])
# body: the D section without front wall (old outer minus inner, minus the channel), back lips, spigot with its hexes
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
def section(zsh):
    body, hooks = extension(zsh)
    body = body - ext_xy(chan2d, zsh - 1, zsh + H + 1)
    for sg in (1, -1):
        x0, x1 = sorted((sg * (W / 2 - SIDE), sg * (W / 2 - WR - 1.2)))
        # top end runs out at 45 deg from the side wall, so printed upside down it grows out of the wall (no roof)
        xo, xi = sg * (W / 2 - SIDE), sg * (W / 2 - WR - 1.2); zt = zsh + H - SPIG - 1.0
        body = body + mf.Manifold.hull_points([(x, y, z) for y in (d + TP + C, d + TP + C + BL)
                                               for x, z in ((xo, zsh + PROT), (xi, zsh + PROT), (xo, zt), (xi, zt - abs(xo - xi)))])
    cut, cnt, _ = hex_holes(zsh, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=RIB_)
    body = body - (cut ^ mf.Manifold.cube([200, 200, SPIG + 1]).translate([-100, -100, zsh - SPIG - 1]))
    return body, hooks
def plate(zsh):
    p = ext_xy(plate2d, zsh, zsh + HP)
    # hexes B, lattice as in hex_holes, clipped to the plate's open window
    s, f, h = S_AF, 4.78, S_AF / 2; ac = f + 2 * h; pp = s + RIB_
    L = math.hypot(h, s / 2); c1 = h * s / 2 + (s / 2) * (f / 2)
    dz = (RIB_ * L + c1 - h * (pp / 2 - s / 2)) / (s / 2) + f / 2
    xb, zb0, zb1 = xp - RIB_, zsh + 1.0, zsh + HP - 1.0
    pts = [(0, ac / 2), (-s / 2, f / 2), (-s / 2, -f / 2), (0, -ac / 2), (s / 2, -f / 2), (s / 2, f / 2)]
    cut, n = mf.Manifold(), 0
    n_rows = int((zb1 - zb0) // dz) + 2; z0 = (zb0 + zb1) / 2 - (n_rows - 1) * dz / 2
    for i in range(n_rows):
        zc = z0 + i * dz; off = 0.0 if i % 2 == 0 else pp / 2
        for k in range(-10, 11):
            xc = off + k * pp
            if abs(xc) - s / 2 >= xb - 1.0 or zc - ac / 2 >= zb1 - 1.0 or zc + ac / 2 <= zb0 + 1.0:
                continue
            cs = mf.CrossSection([ccw([(xc + x, zc + z) for x, z in pts])])
            cut = cut + mf.Manifold.extrude(cs, 10).warp(lambda v: (v[0], d + 7 - v[2], v[1])); n += 1   # swap plus mirror keeps it right side out
    win = mf.Manifold.cube([2 * xb, 20, zb1 - zb0]).translate([-xb, d - 5, zb0])
    return p - (cut ^ win), n
secM, hooks = section(ZC)
plM, nh = plate(ZC)
secU, hooksU = section(ZC + H); plU, _ = plate(ZC + H)
print("plate hexes %d, plate %.1f cm3, section %.1f cm3" % (nh, plM.volume() / 1000, secM.volume() / 1000))
print("overlaps (mm3): plate/section %.3f, plate/upper spigot %.3f, upper plate/section %.3f, post/plate %.3f" % (
    (plM ^ secM).volume(), (plM ^ (secU + hooksU[0] + hooksU[1])).volume(), (plU ^ secM).volume(),
    ((lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)) ^ plM).volume()))
# along the slide path: plate lifted in 5 mm steps through the upper section
worst = max((plM.translate([0, 0, t]) ^ (secM + secU)).volume() for t in range(0, int(H) + 1, 25))
print("worst overlap along the slide path %.3f mm3" % worst)
if len(sys.argv) > 3:
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    base = W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json"))
    m = tm(plM); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))   # face (y = d) down
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    W3.write(os.path.join(sys.argv[3], "plate.3mf"), [W3.Obj("plate", [W3.Part(m.vertices, m.faces)])], base, thumbnails=False)
    m = tm(secM + hooks[0] + hooks[1]); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    W3.write(os.path.join(sys.argv[3], "platesec.3mf"), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])], base, thumbnails=False)
PL = np.array([0.45, 0.62, 0.40])
fig, axs = plt.subplots(1, 4, figsize=(34, 13), gridspec_kw=dict(width_ratios=[1, 1, 0.9, 1.1]))
LIFT = 120.0
ax = axs[0]; R.FACES.clear()
R.mesh(tm(secM), UP); R.mesh(tm(hooks[0] + hooks[1]), HOOK); R.mesh(tm(plM.translate([0, 0, LIFT])), PL)
cam = R.view(ax, eye=(-0.9, -1.5, 0.55), pad=8)
ax.set_title("Section (blue) with its plate (green) slid %d mm up out of the top,\nfrom the front left; plate drops in from the top" % LIFT, fontsize=13)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
ax = axs[1]; R.FACES.clear()
R.mesh(tm(secM), UP); R.mesh(tm(hooks[0] + hooks[1]), HOOK); R.mesh(tm(plM), PL)
cam = R.view(ax, eye=(-0.9, -1.5, 0.35), pad=8)
ax.set_title("Seated, from the front left: %d hexes (B, 13.1 x 17.9);\nplate face flush with the 2.0 mm rail faces" % nh, fontsize=13)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
ax = axs[2]; R.FACES.clear()
R.mesh(tm(secM.translate([0, 0, 0])), UP); R.mesh(tm(plM), PL)
R.mesh(tm(secM.translate([0, 0, 0]) ^ mf.Manifold.cube([1, 1, 1]).translate([0, 0, -900])), UP) if False else None
cam = R.view(ax, eye=(0.9, 1.5, 0.45), pad=8)
ax.set_title("From the back right: back and sides solid as before,\nplate top edge seen in the open-top socket", fontsize=13)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
# top-down cut of the right rail at mid-height
zc = ZC + 100
cutz = lambda m: tm(m ^ mf.Manifold.cube([300, 300, 4]).translate([-150, -150, zc - 4]))
ax = axs[3]; R.FACES.clear()
R.mesh(cutz(secM), UP); R.mesh(cutz(plM), PL)
_, right, up = R.camera((0, -0.02, 1))
P3 = np.array([[W / 2 - 6, d - 1.0, zc], [W / 2 + 0.8, d + TP + C + BL + 1.5, zc]])
sx, sy = P3 @ right, P3 @ up
img, cam = R.render((0, -0.02, 1), frame=(sx.min(), sx.max(), sy.min(), sy.max()), edge_depth=0.5)
ax.imshow(img); ax.axis("off")
R.dim(ax, cam, (W / 2 - WR, d - 0.4, zc), (W / 2, d - 0.4, zc), (0, -0.6, 0))
R.dim(ax, cam, (W / 2 - 5.5, d, zc), (W / 2 - 5.5, d + TP, zc), (-0.8, 0, 0))
R.dim(ax, cam, (xg, d + TP + 0.6, zc), (W / 2, d + TP + 0.6, zc), (0, 0, 0))
R.dim(ax, cam, (W / 2 - WR - 1.2, d + TP + C + BL + 0.6, zc), (W / 2 - SIDE, d + TP + C + BL + 0.6, zc), (0, 0.4, 0))
ax.set_title("Right rail cut across at mid-height, from above (front at the bottom):\nrail 2.0, plate 1.8 (6 layers), 0.6 mm 45 deg catch, 0.2 mm gaps, back lip", fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: sliding hex plate (fillets left out)", fontsize=17)
R.save(fig, sys.argv[2])

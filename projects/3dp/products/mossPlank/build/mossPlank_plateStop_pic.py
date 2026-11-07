"""mossPlank sliding hex plate, reading B (my pick 2026-10-11: "b. sections are assembled and then clipped onto the main
pole"): each section takes its own plate from its top, then clips on, so each section needs a stop at its bottom.
Printed upside down (top end on the bed), anything at a section's bottom front must grow at 45 deg from the side rails:
nothing else is under it there once the front wall is gone. The earlier plate model (mossPlank_plate_pic.py) kept the
hidden front ramp and the spigot's front wall; with no front wall to grow from, the ramp starts as a hairline over air and
Orca lays a 58 mm wall line across it (slice of platesec.3mf, layer 199.2 to 199.5; dpcheck and Orca's warnings missed it).
This model (inference, my sizes):
- Corner stops: a 45 deg gusset in each bottom corner of the plate channel, 3.0 mm tall at the rail's inner face (more in
  the dovetail groove), grown from the rail when printed upside down. The plate's four corners are cut at 45 deg to match,
  0.2 mm gap square to the slope, so the plate fits either end down and sits on the two stops.
- Spigot front wall and the front part of the hidden ramp removed (they had nothing to print from); the spigot is a U,
  open at the front, behind the lower section's plate.
- Plate as before (1.8 mm, dovetail edges, hexes B) from 0.2 mm above the section's bottom to 0.2 mm below its top;
  hexes clipped 2.0 mm from its sides and the corner cuts and 1.0 mm from its ends.
Usage: python3 mossPlank_plateStop_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_plate_pic.py")).read().split("PL = np.array")[0])
G_STOP, GAP45 = 3.0, 0.2 * math.sqrt(2)                   # stop height at the rail's inner face; 0.2 mm square to a 45 deg face
KG = W / 2 - WR - G_STOP                                   # stop face: |x| - (z - zsh) = KG
KC = KG - GAP45 + 0.2                                      # plate corner cut: |x| - (z - z0p) = KC, z0p = zsh + 0.2
def xz_prism(pts, y0, y1):
    """Prism of an (x, z) polygon from y0 to y1 (a rotation, so it stays right side out)."""
    return mf.Manifold.extrude(mf.CrossSection([ccw(pts)]), y1 - y0).warp(lambda v: (v[0], y1 - v[2], v[1]))
def octagon(K, z0, z1):
    return [(-K, z0), (K, z0), (K + 40, z0 + 40), (K + 40, z1 - 40), (K, z1), (-K, z1), (-K - 40, z1 - 40), (-K - 40, z0 + 40)]
def stops(zsh):
    ch = ext_xy(chan2d, zsh, zsh + G_STOP + 2) ^ mf.Manifold.cube([200, TP + C + 0.01, 50]).translate([-100, d, zsh - 1])
    out = mf.Manifold()
    for sg in (1, -1):
        tri = [(sg * KG, 0), (sg * (KG + 20), 0), (sg * (KG + 20), 20)]
        out = out + (ch ^ xz_prism([(x, zsh + z) for x, z in tri], d - 1, d + 5))
    return out
def front_cut(zsh):
    """Spigot front wall and the front ramp, between the spigot side walls' inner faces."""
    xi = W / 2 - SIDE - GAP - T
    return mf.Manifold.cube([2 * xi, FRONT + GAP + T + 0.01 - (TP + C) + 0.01, SPIG + PROT + 1.5]).translate([-xi, d + TP + C - 0.01, zsh - SPIG - 1])
def sectionB(zsh):
    body, hk = section(zsh)
    return body - front_cut(zsh) + stops(zsh), hk
def plateB(zsh):
    z0p, z1p = zsh + 0.2, zsh + H - 0.2
    p = ext_xy(plate2d, z0p, z1p) ^ xz_prism(octagon(KC, z0p, z1p), d - 1, d + TP + 1)
    s, f, h = S_AF, 4.78, S_AF / 2; ac = f + 2 * h; pp = s + RIB_
    L = math.hypot(h, s / 2); c1 = h * s / 2 + (s / 2) * (f / 2)
    dz = (RIB_ * L + c1 - h * (pp / 2 - s / 2)) / (s / 2) + f / 2
    xb, zb0, zb1 = xp - RIB_, z0p + 1.0, z1p - 1.0
    win = mf.Manifold.cube([2 * xb, 20, zb1 - zb0]).translate([-xb, d - 5, zb0]) ^ \
        xz_prism(octagon(KC - RIB_ * math.sqrt(2), z0p, z1p), d - 6, d + 16)
    pts = [(0, ac / 2), (-s / 2, f / 2), (-s / 2, -f / 2), (0, -ac / 2), (s / 2, -f / 2), (s / 2, f / 2)]
    cut, n = mf.Manifold(), 0
    n_rows = int((zb1 - zb0) // dz) + 2; zc0 = (zb0 + zb1) / 2 - (n_rows - 1) * dz / 2
    for i in range(n_rows):
        zc = zc0 + i * dz; off = 0.0 if i % 2 == 0 else pp / 2
        for k in range(-10, 11):
            xc = off + k * pp
            if abs(xc) - s / 2 >= xb or zc - ac / 2 >= zb1 or zc + ac / 2 <= zb0:
                continue
            hx = xz_prism([(xc + x, zc + z) for x, z in pts], d - 5, d + 5) ^ win
            if hx.volume() > 0.5:
                cut = cut + hx; n += 1
    return p - cut, n
secB, hkB = sectionB(ZC); plB, nB = plateB(ZC)
secBU, hkBU = sectionB(ZC + H); plBU, _ = plateB(ZC + H)
stB = stops(ZC)
postB = lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postB = postB - window(zlo_p, sg)
hk2 = hkB[0] + hkB[1]; hk2U = hkBU[0] + hkBU[1]
print("plate B: %d hexes, %.2f cm3; section B %.2f cm3 (earlier: plate %.2f, section %.2f); stops %.3f cm3 each pair" % (
    nB, plB.volume() / 1000, secB.volume() / 1000, plM.volume() / 1000, secM.volume() / 1000, stB.volume() / 1000))
ov = lambda A_, B_: (A_ ^ B_).volume()
print("overlaps (mm3): plate/section %.3f, plate/upper section+hooks %.3f, upper plate/section %.3f, plate/post %.3f, "
      "upper section/section %.3f, upper hooks/section %.3f, section/post %.3f" % (
    ov(plB, secB), ov(plB, secBU + hk2U), ov(plBU, secB), ov(plB, postB), ov(secBU, secB), ov(hk2U, secB), ov(secB + hk2, postB)))
slide = max(ov(plB.translate([0, 0, t]), secB) for t in list(range(1, int(H) + 1, 10)) + [0.05, 0.2])
print("worst overlap sliding the plate in from the top (lifted 0.05 to %d mm): %.3f mm3" % (H, slide))
print("plate pushed 0.3 mm down into its stops: overlap %.3f mm3 (a stop catches it)" % ov(plB.translate([0, 0, -0.3]), secB))
print("plate turned end for end: overlap %.3f mm3" % ov(plB.mirror([0, 0, 1]).translate([0, 0, 2 * ZC + H]), secB))
if len(sys.argv) > 3:
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    base = W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json"))
    m = tm(plB); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))   # face (y = d) down
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    W3.write(os.path.join(sys.argv[3], "plateB.3mf"), [W3.Obj("plate", [W3.Part(m.vertices, m.faces)])], base, thumbnails=False)
    m = tm(secB + hk2); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    W3.write(os.path.join(sys.argv[3], "sectionB.3mf"), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])], base, thumbnails=False)
if sys.argv[2] == "/dev/null":
    sys.exit(0)
# ---- picture
PL = np.array([0.45, 0.62, 0.40]); SPOT = np.array([0.95, 0.10, 0.75]); BAD = np.array([0.90, 0.15, 0.10])
back_pot = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); back_ins = ins.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
clipz = lambda m, z0_, z1_: m ^ mf.Manifold.cube([300, 300, z1_ - z0_]).translate([-150, -150, z0_])
flip = lambda m, zt_: m.rotate([180, 0, 0]).translate([0, 0, 0]).translate([0, 0, zt_])    # (x, -y, -z): a rotation
fig, axs = plt.subplots(1, 4, figsize=(36, 15), gridspec_kw=dict(width_ratios=[0.8, 1.1, 1, 1]))
# 1: whole design, stops bright
ax = axs[0]; R.FACES.clear()
R.mesh(back_pot, CLEAR); R.mesh(back_ins, INS); R.mesh(tm(postB), POST)
for zs_, sec_, hk_, pl_ in ((ZC, secB, hk2, plB), (ZC + H, secBU, hk2U, plBU)):
    R.mesh(tm(sec_ - stops(zs_)), UP); R.mesh(tm(stops(zs_)), SPOT); R.mesh(tm(hk_), HOOK); R.mesh(tm(pl_), PL)
cam = R.view(ax, eye=(-0.9, -1.5, 0.35), pad=8)
for zs_ in (ZC, ZC + H):
    R.call(ax, cam, (-(W / 2 - WR) + 0.5, d, zs_ + 1.0), (-110, 40 if zs_ == ZC else -40), "stops (pink)", color="#b0127a")
ax.set_title("Whole design: two sections clipped on the 93 mm post,\nplates seated; corner stops pink, from the front left", fontsize=13)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
# 2: bottom of a section on its own, plate slid 12 mm up, from the front left and a little below
LIFT2 = 12.0; z0_, z1_ = ZC - SPIG - 1, ZC + 40
ax = axs[1]; R.FACES.clear()
R.mesh(tm(clipz(secB - stB, z0_, z1_)), UP); R.mesh(tm(stB), SPOT); R.mesh(tm(clipz(hk2, z0_, z1_)), HOOK)
R.mesh(tm(clipz(plB.translate([0, 0, LIFT2]), z0_, z1_)), PL)
cam = R.view(ax, eye=(-0.75, -1.5, -0.15), pad=5, edge_depth=0.5)
R.call(ax, cam, (-(W / 2 - WR) + 1.0, d, ZC + 1.0), (-90, -60), "stop: 45 deg, 3.0 mm tall\nat the rail, grows from it\nwhen printed upside down", color="#b0127a", size=11)
R.call(ax, cam, (-(xp) + 1.4, d, ZC + 0.2 + LIFT2 + 1.4), (-120, 70), "plate corner cut 45 deg\n(0.2 mm gap to the stop);\nall four corners, so either\nend goes down", color="#2e6b2a", size=11)
R.call(ax, cam, (0, d + TP + C + 0.6, ZC - 10), (60, -80), "spigot: U, open at the front\n(front wall and ramp removed)", size=11)
ax.set_title("Bottom of a section on its own, plate slid %d mm up out of its stops,\nfrom the front left, a little below (bottom 70 mm)" % LIFT2, fontsize=13)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
# 3, 4: printed upside down, the last 36 mm printed (shoulder and spigot), cut at x = 0 to show the front, from the front right above
zt_ = ZC + H
def printed(sec_, hk_, spot_, spotcol):
    keep = mf.Manifold.cube([200, 300, 60]).translate([0, -150, ZC - SPIG - 5])     # x >= 0 half, bottom 65 mm
    R.mesh(tm(flip((sec_ - spot_) ^ keep, zt_)), UP); R.mesh(tm(flip(hk_ ^ keep, zt_)), HOOK)
    if spot_.volume() > 0: R.mesh(tm(flip(spot_ ^ keep, zt_)), spotcol)
ramp_old = secM ^ mf.Manifold.cube([2 * (W / 2 - SIDE - GAP - T), FRONT + GAP + T - (TP + C) + 0.02, PROT + 0.5]).translate([-(W / 2 - SIDE - GAP - T), d + TP + C - 0.01, ZC])
for ax, sec_, hk_, spot_, col, t in ((axs[2], secM, hooks[0] + hooks[1], ramp_old, BAD,
                                       "Earlier plate model, printed upside down (right half, cut at the center):\nthe hidden front ramp (red) starts as a hairline over air; Orca lays a\n58 mm wall line across it at layer 199.5 (dpcheck and Orca's warnings missed it)"),
                                      (axs[3], secB, hk2, stB, SPOT,
                                       "This model, same view: spigot open at the front, nothing starts over air;\nstops (pink) grow from the rail at 45 deg. dpcheck islands, overhang,\nbridge pass; Orca: no warning, no full-width line over air")):
    R.FACES.clear(); printed(sec_, hk_, spot_, col)
    cam = R.view(ax, eye=(0.35, 1.2, 0.9), pad=4, edge_depth=0.5)
    ax.set_title(t, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank sliding hex plate, reading B: corner stops at each section's bottom (%d hexes per plate; plate %.1f cm3, section %.1f cm3; fillets left out)"
             % (nB, plB.volume() / 1000, secB.volume() / 1000), fontsize=16)
R.save(fig, sys.argv[2])

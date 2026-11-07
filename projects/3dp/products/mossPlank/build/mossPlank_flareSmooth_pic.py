"""mossPlank post flare, D to box above the rim (box back from log.md, Box back): the blended flare (B in mossPlank_flare_pic.py,
side walls flat, back sloping straight at up to 45 deg, creases where the slope starts and ends) next to a smooth one:
S. Each back point moves straight back on a cosine curve, so the slope leaves the D's wall and meets the box's vertical
   wall tangent, with no crease; steepest at mid-height, held to 45 deg, so it takes pi/2 times the height.
Rows: post from the rim up, from behind at the side; a cut down the middle (x = 0) from the side, near the rim.
Usage: python3 mossPlank_flareSmooth_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
NS = 40                                                       # slices through the flare
def outline(off_f, off_s, off_r, off_b, t, z):
    """D (front, sides, round back) with each back point moved a share t straight back toward the box's flat back."""
    xs_ = W / 2 - off_s; rr = r1 - off_r; yb = r1 - off_b
    xs = np.linspace(xs_, -xs_, 129)
    yd = np.sqrt(np.maximum(rr**2 - xs**2, 0))
    y = (1 - t) * yd + t * yb
    return [(-xs_, d + off_f, z), (xs_, d + off_f, z)] + [(x, yy, z) for x, yy in zip(xs, y)]
def flare_lin(off_f, off_s, off_r, off_b, z0):
    trav = (r1 - off_b) - math.sqrt((r1 - off_r)**2 - (W / 2 - off_s)**2); h = trav + 0.05
    return mf.Manifold.hull_points(outline(off_f, off_s, off_r, off_b, 0, z0) + outline(off_f, off_s, off_r, off_b, 1, z0 + h)), h
def flare_cos(off_f, off_s, off_r, off_b, z0, h):
    m = mf.Manifold()
    for i in range(NS):
        u0, u1 = i / NS, (i + 1) / NS
        t0, t1 = (1 - math.cos(math.pi * u0)) / 2, (1 - math.cos(math.pi * u1)) / 2
        m = m + mf.Manifold.hull_points(outline(off_f, off_s, off_r, off_b, t0, z0 + u0 * h) + outline(off_f, off_s, off_r, off_b, t1, z0 + u1 * h))
    return m
trav_o = r1 - math.sqrt(r1**2 - (W / 2)**2)
HS = trav_o * math.pi / 2 + 0.1                               # cosine's steepest slope = trav * pi / (2 h) <= 1 (45 deg)
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
def post_with(kind):
    if kind == "B":
        fo, h_o = flare_lin(0, 0, 0, 0, RIM); fi, h_i = flare_lin(FRONT, SIDE, a, SIDE, RIM)
    else:
        fo = flare_cos(0, 0, 0, 0, RIM, HS); fi = flare_cos(FRONT, SIDE, a, SIDE, RIM, HS); h_o = h_i = HS
    outer = lower_out(0, 0, 0, zb, RIM + 0.01) + fo + boxprism(0, 0, 0, RIM + h_o - 0.01, ZC)
    inner = lower_out(a, FRONT, SIDE, zb - 1, RIM + 0.01) + fi + boxprism(FRONT, SIDE, SIDE, RIM + h_i - 0.01, ZC + 1)
    p = outer - inner
    for sg in (1, -1):
        p = p - window(zlo_p, sg)
    return p, h_o
secB0, hooksB, Hr = box_extension(ZC)
OPT = {k: post_with(k) for k in ("B", "S")}
for k, (p, h) in OPT.items():
    print(k, "flare height %.2f, post volume %.0f mm3, overlap with section %.3f mm3" % (h, p.volume(), (p ^ (secB0 + hooksB[0] + hooksB[1])).volume()))
    if len(sys.argv) > 3:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
        m = tm(p); m.apply_translation([128, 128, -zb])
        W3.write(os.path.join(sys.argv[3], "flarepost_%s.3mf" % k), [W3.Obj("post", [W3.Part(m.vertices, m.faces)])],
                 W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
TT = {"B": "B. Straight slope: creases where it leaves the D and meets the box wall",
      "S": "S. Smooth: the slope leaves the D and meets the box wall tangent, no creases"}
fig, axs = plt.subplots(2, 2, figsize=(18, 18))
for j, k in enumerate("BS"):
    p, h = OPT[k]
    top = tm(p ^ mf.Manifold.cube([200, 200, ZC - (RIM - 10)]).translate([-100, -100, RIM - 10]))
    ax = axs[0][j]; R.FACES.clear(); R.mesh(top, POST)
    cam = R.view(ax, eye=(1.3, 1.1, 0.45), ppm=9.0, pad=6)
    R.dim(ax, cam, (W / 2, r1, RIM), (W / 2, r1, RIM + h), (6, 6, 0), "%.1f" % h)
    ax.set_title("%s\npost from 10 mm below the rim up, from behind at the right side" % TT[k], fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
    ax = axs[1][j]; R.FACES.clear()
    win = mf.Manifold.cube([200, 200, 45]).translate([-100, -100, RIM - 10])
    R.mesh(tm(p ^ win).slice_plane([0, 0, 0], [-1, 0, 0], cap=True), POST)
    cam = R.view(ax, eye=(1, 0.0001, 0.0001), ppm=12.0, pad=3)
    ax.set_title("%s: cut down the middle, seen from the right (back to the right),\nrim - 10 to rim + 35 mm" % k, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank (box back): the post's flare from the D to the box, straight or smooth", fontsize=15)
R.save(fig, sys.argv[2])

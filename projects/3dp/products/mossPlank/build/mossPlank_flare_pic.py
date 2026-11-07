"""mossPlank post flare, D to box above the rim (agreed change 6 post, box back from mossPlank_hex_pic.py), two ways side by side:
A. Current: the D grown outward at 45 deg (a round offset, hull) and clipped by the box, so the flare's rounded corner meets
   the flat side wall at a crease.
B. Blended: a hull of the D at the rim and the box at the flare's top, so the side walls run on flat and only the back
   slopes (the back corners travel straight back, at 45 deg at most); the side wall is one flat face.
Rows: post top from behind at the side, and a cut across the flare at mid-height from above. Prints each option's numbers.
Usage: python3 mossPlank_flare_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "mossPlank_hex_pic.py")).read()
exec(src.split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])           # geometry, flare() (option A)
def flare_blend(off_f, off_s, off_r, off_b, z0):
    """Hull of the D outline at z0 and the box outline at z0 + h; h = the back corners' straight-back travel, so 45 deg at most."""
    from shapely.geometry import Point as SP, box as SB
    D2 = SB(-W / 2 + off_s, d + off_f, W / 2 - off_s, 300).intersection(SP(0, 0).buffer(r1 - off_r, 256))
    h = (r1 - off_b) - math.sqrt((r1 - off_r)**2 - (W / 2 - off_s)**2) + 0.05
    lo = [(x, y, z0) for x, y in D2.exterior.coords]
    hi = [(x, y, z0 + h) for x in (-W / 2 + off_s, W / 2 - off_s) for y in (d + off_f, r1 - off_b)]
    return mf.Manifold.hull_points(lo + hi), h
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
def post_with(fl):
    fo, h_o = fl(0, 0, 0, 0, RIM); fi, h_i = fl(FRONT, SIDE, a, SIDE, RIM)
    outer = lower_out(0, 0, 0, zb, RIM + 0.01) + fo + boxprism(0, 0, 0, RIM + h_o - 0.01, ZC)
    inner = lower_out(a, FRONT, SIDE, zb - 1, RIM + 0.01) + fi + boxprism(FRONT, SIDE, SIDE, RIM + h_i - 0.01, ZC + 1)
    p = outer - inner
    for sg in (1, -1):
        p = p - window(zlo_p, sg)
    return p, h_o, h_i
OPT = {"A": post_with(flare), "B": post_with(flare_blend)}
secB0, hooksB, Hr = box_extension(ZC)
for k, (p, h_o, h_i) in OPT.items():
    print(k, "flare %.2f out / %.2f in, post volume %.0f mm3, overlap with section %.3f mm3" % (h_o, h_i, p.volume(), (p ^ (secB0 + hooksB[0] + hooksB[1])).volume()))
    if len(sys.argv) > 3:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
        m = tm(p); m.apply_translation([128, 128, -zb])
        W3.write(os.path.join(sys.argv[3], "flarepost_%s.3mf" % k), [W3.Obj("post", [W3.Part(m.vertices, m.faces)])],
                 W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
TT = {"A": "A. Current: round 45 deg offset, clipped by the box", "B": "B. Blended: side walls run on flat, only the back slopes"}
fig, axs = plt.subplots(2, 2, figsize=(18, 17))
for j, k in enumerate("AB"):
    p, h_o, h_i = OPT[k]
    top = tm(p ^ mf.Manifold.cube([200, 200, ZC - (RIM - 15)]).translate([-100, -100, RIM - 15]))
    ax = axs[0][j]; R.FACES.clear(); R.mesh(top, POST)
    cam = R.view(ax, eye=(1.3, 1.1, 0.45), pad=6)
    R.dim(ax, cam, (W / 2, r1, RIM), (W / 2, r1, RIM + h_o), (6, 6, 0), "%.1f" % h_o)
    R.call(ax, cam, (W / 2, r1 - 4, RIM + h_o * 0.5), (70, -40), "side wall", size=11)
    ax.set_title("%s\npost from the rim up, from behind at the right side (cut off 15 mm below the rim)" % TT[k], fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
    zm = RIM + h_o / 2
    ax = axs[1][j]; R.FACES.clear()
    R.mesh(tm(p ^ mf.Manifold.cube([200, 200, 4]).translate([-100, -100, zm - 4])), POST)
    cam = R.view(ax, eye=(0, -0.02, 1), pad=4)
    ax.set_title("%s: cut across at mid-flare (%.1f mm above the rim), from above" % (k, h_o / 2), fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: the post's flare from the D to the box above the rim, two ways", fontsize=15)
R.save(fig, sys.argv[2])

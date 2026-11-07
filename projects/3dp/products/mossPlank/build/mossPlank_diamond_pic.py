"""mossPlank hole-shape options side by side (first drawn for my ask 2026-10-10: "is there a better shape for this?"), on the current design:
93 mm D post (change 6), D section with 2.0 mm side strips (change 7). B: 13.1 x 17.9 hexes, flats 4.78, 45 deg roofs.
A: regular point-up hexes, 13.1 across the flats (the photo's hex; roofs 60 deg from vertical, fails dp 1).
C 13.1 x 20.6, D 13.1 x 15.1 (45 deg roofs). E: 13.1 x 13.1 diamonds (hex_holes with flats 0), every rib at 45 deg, no flats, no bridges.
Rows: in the 3.5in pot from the front; a front close-up of the same patch. Prints hex count, open share, section volume and
the front-back section modulus of the body cut through a row of holes (weakest spot, inference).
Usage: python3 mossPlank_diamond_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [option letters, default BE] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
postD = lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postD = postD - window(zlo_p, sg)
s0, hk = extension(ZC)
h45 = S_AF / 2
ALL = {"A": (None, None, "regular hexes 13.1 x 15.1 (the photo's),\nroofs 60 deg from vertical"), "B": (4.78, h45, "hexes 13.1 x 17.9, flats 4.78"),
       "C": (20.6 - 2 * h45, h45, "hexes 13.1 x 20.6, flats %.2f" % (20.6 - 2 * h45)), "D": (15.1 - 2 * h45, h45, "hexes 13.1 x 15.1, flats %.2f" % (15.1 - 2 * h45)),
       "E": (0.0, h45, "diamonds 13.1 x 13.1, all ribs at 45 deg")}
SHAPES = [(k,) + ALL[k] for k in (sys.argv[3] if len(sys.argv) > 3 else "BE")]
OUT3 = sys.argv[4] if len(sys.argv) > 4 else None
face = (W - 2 * SIDE) * H

def zmod(s, z):
    """Front-back bending section modulus (mm3) of the solid cut at height z (thin slice, inference)."""
    sl = (s ^ mf.Manifold.cube([300, 300, 0.2]).translate([-150, -150, z - 0.1]))
    m = tm(sl); A = sl.volume() / 0.2
    if A <= 0: return 0
    import numpy as np
    pts, _ = trimesh.sample.volume_mesh(m, 200000), None
    y = pts[:, 1]; yc = y.mean(); I = A * ((y - yc) ** 2).mean()
    return I / max(y.max() - yc, yc - y.min())

OPT = {}
for k, f, hh, lab in SHAPES:
    cut, cnt, geo = hex_holes(ZC, S_AF, RIB_, True, True, False, True, f, hh, strip=RIB_)
    s = s0 - cut
    open_ = (s0.volume() - s.volume()) / FRONT / face
    z0, n, dz, p, ac = geo
    zrow = z0 + round((ZC + 100 - z0) / dz) * dz
    zs = [zrow + t for t in (-dz / 2, -dz / 4, 0, dz / 4)]
    zm_ = min(zmod(s, z) for z in zs)
    OPT[k] = (s, cnt, lab)
    print(k, lab, "holes", cnt, "open %.0f%%" % (100 * open_), "section %.1f cm3" % (s.volume() / 1000),
          "body Z min %.0f mm3" % zm_, "overlap %.3f" % (s ^ postD).volume())
    if OUT3:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
        m = tm(s + hk[0] + hk[1]); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
        W3.write(os.path.join(OUT3, "holesec_%s.3mf" % k), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])],
                 W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
fig, axs = plt.subplots(2, len(SHAPES), figsize=(9.5 * len(SHAPES), 24), gridspec_kw=dict(height_ratios=[1.5, 1]))
back_half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
zm = ZC + 100
for j, (k, f, hh, lab) in enumerate(SHAPES):
    s, cnt, _ = OPT[k]
    ax = axs[0][j]; R.FACES.clear()
    R.mesh(back_half, CLEAR); R.mesh(tm(postD), POST); R.mesh(tm(s), UP); R.mesh(tm(hk[0] + hk[1]), HOOK)
    cam = R.view(ax, eye=(-0.9, -1.5, 0.6), ppm=3.0, pad=8)
    ax.set_title("%s. %s\n%d holes; in the 3.5in pot from the front" % (k, lab, cnt), fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax = axs[1][j]; R.FACES.clear()
    R.mesh(tm(s ^ mf.Manifold.cube([200, 200, 50]).translate([-100, -100, zm - 25])), UP)
    cam = R.view(ax, eye=(0, -1, 0), ppm=14.0, pad=2)
    ax.set_title("%s: front close-up, 50 mm of the section's middle (same scale)" % k, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank hole shapes %s (13.1 mm wide, 2.0 mm ribs, side strips)" % ", ".join(s[0] for s in SHAPES), fontsize=16)
R.save(fig, sys.argv[2])

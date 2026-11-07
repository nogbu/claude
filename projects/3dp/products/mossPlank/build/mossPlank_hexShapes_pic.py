"""mossPlank hex shape options (agreed change 5's open shape question), redrawn on the current design: 93 mm D post (change 6),
D section with 2.0 mm side strips (change 7). All 13.1 mm wide with 45 deg roofs, 2.0 mm ribs:
B 13.1 x 17.9 (flats 4.78, closest to the photo's hex), C 13.1 x 20.6 (photo's side length, flats 7.5),
D 13.1 x 15.1 (photo's height, flats 2.0). Rows: in the 3.5in pot from the front; a front close-up of the same patch.
Prints each option's hex count, open share of the patterned face and section volume.
Usage: python3 mossPlank_hexShapes_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
postD = lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postD = postD - window(zlo_p, sg)
s0, hk = extension(ZC)
h45 = S_AF / 2
SHAPES = (("B", 4.78, "13.1 x 17.9, flats 4.78"), ("C", 20.6 - 2 * h45, "13.1 x 20.6, flats %.2f" % (20.6 - 2 * h45)),
          ("D", 15.1 - 2 * h45, "13.1 x 15.1, flats %.2f" % (15.1 - 2 * h45)))
face = (W - 2 * SIDE) * H                                      # patterned face area, for the open share (inference)
OPT = {}
for k, f, lab in SHAPES:
    cut, cnt, geo = hex_holes(ZC, S_AF, RIB_, True, True, False, True, f, h45, strip=RIB_)
    s = s0 - cut
    open_ = (s0.volume() - s.volume()) / FRONT / face          # removed volume over face thickness ~ open area (spigot cuts add a little)
    OPT[k] = (s, cnt, lab, geo)
    print(k, lab, "hexes", cnt, "open %.0f%%" % (100 * open_), "section %.1f cm3" % (s.volume() / 1000), "overlap %.3f" % (s ^ postD).volume())
    if len(sys.argv) > 3:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
        m = tm(s + hk[0] + hk[1]); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
        W3.write(os.path.join(sys.argv[3], "hexsec_%s.3mf" % k), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])],
                 W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
fig, axs = plt.subplots(2, 3, figsize=(27, 24), gridspec_kw=dict(height_ratios=[1.5, 1]))
back_half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
zm = ZC + 100
for j, (k, f, lab) in enumerate(SHAPES):
    s, cnt, _, geo = OPT[k]
    ax = axs[0][j]; R.FACES.clear()
    R.mesh(back_half, CLEAR); R.mesh(tm(postD), POST); R.mesh(tm(s), UP); R.mesh(tm(hk[0] + hk[1]), HOOK)
    cam = R.view(ax, eye=(-0.9, -1.5, 0.6), ppm=3.0, pad=8)
    ax.set_title("%s. %s\n%d hexes; in the 3.5in pot from the front" % (k, lab, cnt), fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax = axs[1][j]; R.FACES.clear()
    R.mesh(tm(s ^ mf.Manifold.cube([200, 200, 50]).translate([-100, -100, zm - 25])), UP)
    cam = R.view(ax, eye=(0, -1, 0), ppm=14.0, pad=2)
    ax.set_title("%s: front close-up, 50 mm of the section's middle (same scale)" % k, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank hex shape options on the current design (13.1 mm wide, 45 deg roofs, 2.0 mm ribs, side strips)", fontsize=16)
R.save(fig, sys.argv[2])

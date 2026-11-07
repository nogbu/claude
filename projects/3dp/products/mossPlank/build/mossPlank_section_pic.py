"""mossPlank standard section on its own, without the post (my ask 2026-10-10: "show me the design without the post").
Current design: D section (agreed changes 1 to 3), 200 mm, open spigot with two snap tabs at the bottom, socket at the top
(change 6), hexes option B 13.1 x 17.9 with 45 deg roofs (change 5), 2.0 mm side strips (change 7). Geometry from
mossPlank_strips_pic.py (option B). Views: front, back, side; close-ups of the spigot with a tab and of the top socket edge.
Usage: python3 mossPlank_section_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_strips_pic.py")).read().split("zc = z0 + round")[0])
s, cnt = OPT["B"]
hooks = tm(hk[0] + hk[1]); sec = tm(s)
zmin, zmax = sec.bounds[0][2], sec.bounds[1][2]
fig, axs = plt.subplots(1, 5, figsize=(36, 13), gridspec_kw=dict(width_ratios=[1, 1, 0.6, 1, 1]))
VIEWS = [((-0.9, -1.5, 0.5), "From the front left"), ((0.9, 1.5, 0.5), "From the back right"), ((1, 0, 0.15), "From the right side")]
for ax, (eye, t) in zip(axs[:3], VIEWS):
    R.FACES.clear(); R.mesh(sec, UP); R.mesh(hooks, HOOK)
    cam = R.view(ax, eye=eye, pad=8)
    ax.set_title("%s\n(section %.0f mm tall incl. the 30 mm spigot)" % (t, zmax - zmin), fontsize=13)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
# close-ups: the spigot (bottom 45 mm) and the socket top (top 35 mm), cut out of the model
clip = lambda m, z0_, z1_: tm(m ^ mf.Manifold.cube([300, 300, z1_ - z0_]).translate([-150, -150, z0_]))
for ax, (z0_, z1_, eye, t) in zip(axs[3:], [(zmin - 1, zmin + 45, (-1.0, -1.2, 0.35), "Close-up: spigot and snap tab (orange),\nfrom the front left, bottom 45 mm"),
                                            (zmax - 35, zmax + 1, (-0.8, -1.0, 0.9), "Close-up: top edge and socket,\nfrom above front left, top 35 mm")]):
    R.FACES.clear(); R.mesh(clip(s, z0_, z1_), UP)
    hz = clip(hk[0] + hk[1], z0_, z1_)
    if len(hz.faces): R.mesh(hz, HOOK)
    cam = R.view(ax, eye=eye, pad=6)
    ax.set_title(t, fontsize=13)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: one standard section without the post (changes 1 to 7; hexes B, %d per section, %.1f cm3)" % (cnt, s.volume() / 1000), fontsize=17)
R.save(fig, sys.argv[2])

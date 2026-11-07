"""mossPlank box back without a flare (agreed change 8): the 93 mm plain D post (change 6) with two box sections stacked on it,
hexes option B with side strips (change 7), on the 3.5in pot. Panels: whole stack from behind; from the front; the joint
from the side, cut 3 mm in from the right side wall (the box back's step out over the post); from above at the joint.
Usage: python3 mossPlank_box3_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
postD = lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postD = postD - window(zlo_p, sg)
secs, hooks = [], []
for i in range(2):
    zs = ZC + i * H
    s0, hk, _ = box_extension(zs)
    cut, cnt, _ = hex_holes(zs, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=RIB_)
    secs.append(s0 - cut); hooks.append(hk[0] + hk[1])
print("overlaps: post/section1 %.3f, section1/section2 %.3f mm3" % ((postD ^ (secs[0] + hooks[0])).volume(), ((secs[0]) ^ (secs[1] + hooks[1])).volume()))
step = r1 - math.sqrt(r1**2 - (W / 2)**2)
UP2 = np.array([0.55, 0.70, 0.82])
fig, axs = plt.subplots(1, 4, figsize=(34, 13), gridspec_kw=dict(width_ratios=[1, 1, 1.1, 1]))
def stack(ax, eye, title, pot_half):
    R.FACES.clear(); R.mesh(pot_half, CLEAR); R.mesh(tm(postD), POST)
    for s, h, c in ((secs[0], hooks[0], UP), (secs[1], hooks[1], UP2)):
        R.mesh(tm(s), c); R.mesh(tm(h), HOOK)
    cam = R.view(ax, eye=eye, ppm=1.6, pad=8); ax.set_title(title, fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    return cam
cam = stack(axs[0], (-0.9, 1.5, 0.6), "From behind (front half of the pot shown):\nplain D post (brown), two box sections", pot.slice_plane([0, 0, 0], [0, -1, 0], cap=False))
R.call(axs[0], cam, (W / 2, r1, ZC), (90, 30), "step at the joint", color="#c0392b", size=12)
stack(axs[1], (-0.9, -1.5, 0.6), "From the front (back half of the pot shown):\nhexes option B, side strips", pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False))
ax = axs[2]; R.FACES.clear()
win = mf.Manifold.cube([200, 200, 60]).translate([-100, -100, ZC - 30])
cutx = lambda m: tm(m ^ win).slice_plane([W / 2 - 3, 0, 0], [-1, 0, 0], cap=True)
R.mesh(cutx(postD), POST); R.mesh(cutx(secs[0]), UP)
cam = R.view(ax, eye=(1, 0.0001, 0.0001), ppm=10.0, pad=3)
yD = math.sqrt(r1**2 - (W / 2 - 3)**2)
R.dim(ax, cam, (W / 2 - 3, yD, ZC - 3), (W / 2 - 3, r1, ZC - 3), (0, 0, 0), "%.1f" % (r1 - yD))
ax.set_title("The joint, cut 3 mm in from the right side wall, seen from the right\n(back to the right; joint at the middle): box back overhangs the post", fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
ax = axs[3]; R.FACES.clear()
R.mesh(pot, CLEAR); R.mesh(tm(postD ^ mf.Manifold.cube([200, 200, 5]).translate([-100, -100, ZC - 5])), POST)
R.mesh(tm(secs[0] ^ mf.Manifold.cube([200, 200, 5]).translate([-100, -100, ZC + 40])), UP)
cam = R.view(ax, eye=(0, -0.02, 1), pad=4)
ax.set_title("From above: the box section (blue) over the post's D top (brown);\nback corners %.1f mm past the D, %.1f mm past the rim" % (step, math.hypot(W / 2, r1) - 48.07), fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: box sections on a plain D post, no flare (agreed change 8)", fontsize=16)
R.save(fig, sys.argv[2])

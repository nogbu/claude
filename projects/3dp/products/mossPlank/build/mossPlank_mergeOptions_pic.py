"""mossPlank: three readings of "change it back to the way it was originally and merge it with the box shape" (2026-10-10),
drawn side by side on the 3.5in pot with the post and the first box section seated (hexes option B, box from mossPlank_hex_pic.py):
A. Plain D post: the 93 mm post (agreed change 6) stays a D up to its cut; the box starts with the first section, whose back
   steps out over the post's back at the joint.
B. D plus box: the 93 mm post is the union of the D and the box, no flare: a flat step out at the rim.
C. Short post: back to the 63 mm post cut at the lip base (agreed change 4), box section from there.
Rows: in the pot from behind (front half of the pot shown); cut down the middle from the side, close to the rim and the joint.
Prints each option's overhang at the step, and its overlaps with the pot and between post and section.
Usage: python3 mossPlank_mergeOptions_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
def post(zc, kind):
    _, _, (zlo, _) = spigot_with_tabs(zc)
    outer = lower_out(0, 0, 0, zb, zc); inner = lower_out(a, FRONT, SIDE, zb - 1, zc + 1)
    if kind == "B":
        outer = outer + boxprism(0, 0, 0, RIM, zc); inner = lower_out(a, FRONT, SIDE, zb - 1, RIM) + boxprism(FRONT, SIDE, SIDE, RIM - 0.01, zc + 1)
    p = outer - inner
    for sg in (1, -1):
        p = p - window(zlo, sg)
    return p
potM = mf.Manifold.of_trimesh if hasattr(mf.Manifold, "of_trimesh") else None
OPTS = {}
for k, zc in (("A", ZC), ("B", ZC), ("C", zl)):
    p = post(zc, k)
    s0, hk, _ = box_extension(zc)
    cut, _, _ = hex_holes(zc, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=RIB_)
    s = s0 - cut
    ov = (p ^ (s + hk[0] + hk[1])).volume()
    OPTS[k] = (p, s, hk, zc, ov)
    print(k, "post %.1f mm, cut %.1f (%.1f above the rim), post/section overlap %.2f mm3" % (zc - zb, zc, zc - RIM, ov))
step = r1 - math.sqrt(r1**2 - (W / 2)**2)
print("box back corner past the D back corner: %.2f mm" % step)
TT = {"A": "A. Plain D post (93 mm), box from the first section:\nthe section's back steps out %.1f mm at its corners over the post" % step,
      "B": "B. Post is D plus box (93 mm), no flare:\nflat step out at the rim, %.1f mm at the corners, unsupported printed upright" % step,
      "C": "C. Short post (63 mm, cut at the lip base), box section:\nsocket tapers (rev1 jam) and the box hits the pot's lip below the rim"}
fig, axs = plt.subplots(2, 3, figsize=(27, 22))
front_half = pot.slice_plane([0, 0, 0], [0, -1, 0], cap=False)
for j, k in enumerate("ABC"):
    p, s, hk, zc, ov = OPTS[k]
    clipH = lambda m: m ^ mf.Manifold.cube([200, 200, zc + 90 - zb]).translate([-100, -100, zb - 1])
    ax = axs[0][j]; R.FACES.clear()
    R.mesh(front_half, CLEAR); R.mesh(tm(p), POST); R.mesh(tm(clipH(s)), UP); R.mesh(tm(hk[0] + hk[1]), HOOK)
    cam = R.view(ax, eye=(-0.9, 1.5, 0.75), ppm=4.0, pad=8)
    R.call(ax, cam, (W / 2, r1, (RIM if k == "B" else zc) + 1), (90, 20), "step" if k != "C" else "lip", color="#c0392b", size=12)
    ax.set_title(TT[k], fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax = axs[1][j]; R.FACES.clear()
    win = mf.Manifold.cube([200, 200, 60]).translate([-100, -100, RIM - 30])
    half = lambda m: tm(m ^ win).slice_plane([W / 2 - 3, 0, 0], [-1, 0, 0], cap=True)
    R.mesh(pot.slice_plane([0, 0, RIM - 30], [0, 0, 1], cap=False).slice_plane([0, 0, RIM + 30], [0, 0, -1], cap=False).slice_plane([W / 2 - 3, 0, 0], [-1, 0, 0], cap=False), CLEAR)
    R.mesh(half(p), POST); R.mesh(half(s), UP)
    cam = R.view(ax, eye=(1, 0.02, 0.05), ppm=9.0, pad=4)
    ax.set_title("%s: cut 3 mm in from the right side, seen from the right\n(rim - 30 to rim + 30 mm; the back is to the right)" % k, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: three readings of \"change it back to the way it was originally and merge it with the box shape\"", fontsize=16)
R.save(fig, sys.argv[2])

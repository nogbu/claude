"""mossPlank box back with no flare and no step (my ask 2026-10-10: "no flare and no step"), two ways side by side:
A. Box 15: the whole plank (post and sections) is one 60 x 15 mm box prism, flat back at the side edges' depth, so its back
   corners touch the pot wall at the insert top (agreed change 1) and it clears the pot everywhere above; straight sockets and
   spigots, box-shaped; no flare, no step anywhere. Gives up the D's deeper back.
B. Box on the post at the rim: post D below the rim (follows the pot), box from the rim up; sections are boxes, so no step at
   the joint and no flare; the post has a flat step at the rim (sitting at the rim), printed upside down so it faces up.
Rows: in the 3.5in pot from behind; from above, a section cut at mid-height over the pot. Prints volumes and the solid-walled
section modulus front to back (hexes left out) for the D, box (B) and box 15 (A) outlines.
Usage: python3 mossPlank_noStep_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
from shapely.geometry import Polygon
def zmod(m, z):
    """Section modulus about the left-right axis (front-back bending) of the solid's cut at z, by grid integration."""
    sec = tm(m).section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p2, _ = sec.to_planar(to_2D=np.eye(4))
    polys = p2.polygons_full
    xs_ = np.arange(-40, 40, 0.05); ys_ = np.arange(-10, 70, 0.05); X, Y = np.meshgrid(xs_, ys_)
    from shapely import contains_xy
    inside = np.zeros_like(X, bool)
    for pg in polys:
        inside |= contains_xy(pg, X, Y)
    A = inside.sum() * 0.0025; yc_ = (Y[inside].sum() * 0.0025) / A
    I = ((Y[inside] - yc_)**2).sum() * 0.0025
    return I / max(Y[inside].max() - yc_, yc_ - Y[inside].min())
# B: post D below the rim, box above; box sections (current box geometry)
def hexcut(zs): return hex_holes(zs, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=RIB_)[0]
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
postB = (lower_out(0, 0, 0, zb, RIM) + boxprism(0, 0, 0, RIM - 0.01, ZC)) - (lower_out(a, FRONT, SIDE, zb - 1, RIM) + boxprism(FRONT, SIDE, SIDE, RIM - 0.02, ZC + 1))
for sg in (1, -1):
    postB = postB - window(zlo_p, sg)
sB0, hB, _ = box_extension(ZC); secB = sB0 - hexcut(ZC)
mid = ZC + 100
SM = {"D": zmod(prism(0, 0, 0, mid - 1, mid + 1) - prism(a, FRONT, SIDE, mid - 2, mid + 2), mid),
      "box": zmod(boxprism(0, 0, 0, mid - 1, mid + 1) - boxprism(FRONT, SIDE, SIDE, mid - 2, mid + 2), mid)}
# A: everything a 60 x 15 box: override the D-based outlines with a flat back at YB
YB = d + 15.0
def prism(off, front, side, z0, z1):
    return mf.Manifold.cube([W - 2 * side, YB - off - d - front, z1 - z0]).translate([-W / 2 + side, d + front, z0])
def lower_out(off, front, side, z0, z1): return prism(off, front, side, z0, z1)
def ramp(zsh):
    def e_at(z): return PROT - (z - zsh)
    z0, z1 = zsh - 1.0, zsh + PROT + 1.0
    def rect(z):
        e = e_at(z); return [(x, y, z) for x in (-W / 2 + SIDE + e, W / 2 - SIDE - e) for y in (d + FRONT + e, YB - SIDE - e)]
    return prism(SIDE, FRONT, SIDE, zsh, zsh + PROT) - mf.Manifold.hull_points(rect(z0) + rect(z1))
a = SIDE; so = a + GAP
y_back = YB - so; yc = (y_front + y_back) / 2
_, _, (zlo_a, _) = spigot_with_tabs(ZC)
postA = prism(0, 0, 0, zb, ZC) - prism(SIDE, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postA = postA - window(zlo_a, sg)
sA0, hA = extension(ZC); secA = sA0 - hexcut(ZC)
SM["box 15"] = zmod(prism(0, 0, 0, mid - 1, mid + 1) - prism(SIDE, FRONT, SIDE, mid - 2, mid + 2), mid)
potM = mf.Manifold(mf.Mesh(vert_properties=np.asarray(pot.vertices, np.float32), tri_verts=np.asarray(pot.faces, np.uint32)))
OPT = {"A": (postA, secA, hA), "B": (postB, secB, hB)}
for k, (p, s, h) in OPT.items():
    print(k, "post %.1f cm3, section %.1f cm3, overlap post/section %.3f, post/pot %.3f, section/pot %.3f mm3" % (
        p.volume() / 1000, s.volume() / 1000, (p ^ (s + h[0] + h[1])).volume(), (p ^ potM).volume(), (s ^ potM).volume()))
print("solid-walled section modulus front-back at mid-section: " + ", ".join("%s %.0f mm3" % kv for kv in SM.items()))
if len(sys.argv) > 3:
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    base = W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json"))
    for nm, m, flip in (("A_post", postA, False), ("A_sec", secA + hA[0] + hA[1], True), ("B_post", postB, True)):
        t = tm(m)
        if flip: t.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        t.apply_translation([128 - (t.bounds[0][0] + t.bounds[1][0]) / 2, 128 - (t.bounds[0][1] + t.bounds[1][1]) / 2, -t.bounds[0][2]])
        W3.write(os.path.join(sys.argv[3], "nostep_%s.3mf" % nm), [W3.Obj(nm, [W3.Part(t.vertices, t.faces)])], base, thumbnails=False)
TT = {"A": "A. Box 15: post and sections one 60 x 15 mm box\n(back corners touch the pot at the insert top)",
      "B": "B. Box on the post from the rim up: D below the rim,\nflat step at the rim, post printed upside down"}
fig, axs = plt.subplots(2, 2, figsize=(20, 22), gridspec_kw=dict(height_ratios=[1.5, 1]))
front_half = pot.slice_plane([0, 0, 0], [0, -1, 0], cap=False)
for j, k in enumerate("AB"):
    p, s, h = OPT[k]
    clipS = s ^ mf.Manifold.cube([200, 200, 120]).translate([-100, -100, ZC - 40])
    ax = axs[0][j]; R.FACES.clear()
    R.mesh(front_half, CLEAR); R.mesh(tm(p), POST); R.mesh(tm(clipS), UP); R.mesh(tm(h[0] + h[1]), HOOK)
    cam = R.view(ax, eye=(-0.9, 1.5, 0.6), ppm=2.6, pad=8)
    ax.set_title(TT[k] + "\nfrom behind (front half of the pot shown); section cut off 80 mm up", fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax = axs[1][j]; R.FACES.clear()
    R.mesh(pot, CLEAR); R.mesh(tm(s ^ mf.Manifold.cube([200, 200, 5]).translate([-100, -100, mid - 5])), UP)
    R.mesh(tm(p ^ mf.Manifold.cube([200, 200, 3]).translate([-100, -100, zb])), POST)
    cam = R.view(ax, eye=(0, -0.02, 1), ppm=4.0, pad=4)
    ax.set_title("%s: from above, a section cut at mid-height (blue)\nover the post's bottom (brown) and the pot" % k, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: box with no flare and no step, two ways", fontsize=16)
R.save(fig, sys.argv[2])

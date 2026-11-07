"""mossPlank box sized to the pot, no flare and no step (my asks 2026-10-10: "make it boxy above the lip of the pot",
"no flare and no step", "remove the step"). The box's back is flat at the depth where its back corners meet the pot's inner
wall at the lip base, so it fits the straight lip and needs no step: sections and the post above the lip base are that
box; below the lip base the post's flat back leans with the pot so its back corners stay on the pot wall down to the insert
top (agreed change 1's corners), so its outline meets the box at the lip base without a step. Straight box spigot and
socket, 0.2 mm gap, tabs as before; post cut 30 mm past the lip base (change 6); hexes option B with side strips (change 7).
Panels: in the pot from behind; from the side, cut 3 mm in from the right wall, around the lip and the joint; from above at
the lip base. Prints depths, volumes, overlaps and the solid-walled section modulus front-back.
Usage: python3 mossPlank_boxFit_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
def hexcut(zs): return hex_holes(zs, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=RIB_)[0]
Y0 = math.sqrt(r0**2 - (W / 2)**2); YB = math.sqrt(r1**2 - (W / 2)**2)   # back at the insert top and from the lip base up
tilt = math.atan((YB - Y0) / (zl - zb)); bk = SIDE / math.cos(tilt)
def prism(off, front, side, z0, z1):                          # the box, back offset 'off' inward
    return mf.Manifold.cube([W - 2 * side, YB - off - d - front, z1 - z0]).translate([-W / 2 + side, d + front, z0])
def lean(off, front, side, z0, z1):                           # post below the lip base: back plane through the wall corners
    pts = lambda z, yb: [(x, y, z) for x in (-W / 2 + side, W / 2 - side) for y in (d + front, yb - off)]
    yb = lambda z: Y0 + (YB - Y0) * (z - zb) / (zl - zb)
    return mf.Manifold.hull_points(pts(z0, yb(z0)) + pts(z1, yb(z1)))
def ramp(zsh):
    def e_at(z): return PROT - (z - zsh)
    z0, z1 = zsh - 1.0, zsh + PROT + 1.0
    def rect(z):
        e = e_at(z); return [(x, y, z) for x in (-W / 2 + SIDE + e, W / 2 - SIDE - e) for y in (d + FRONT + e, YB - SIDE - e)]
    return prism(SIDE, FRONT, SIDE, zsh, zsh + PROT) - mf.Manifold.hull_points(rect(z0) + rect(z1))
a = SIDE; so = a + GAP
y_back = YB - so; yc = (y_front + y_back) / 2
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
post = (lean(0, 0, 0, zb, zl + 0.01) + prism(0, 0, 0, zl, ZC)) - (lean(bk, FRONT, SIDE, zb - 1, zl + 0.01) + prism(SIDE, FRONT, SIDE, zl, ZC + 1))
for sg in (1, -1):
    post = post - window(zlo_p, sg)
s0, hk = extension(ZC); sec = s0 - hexcut(ZC)
s20, hk2 = extension(ZC + H); sec2 = s20 - hexcut(ZC + H)
potM = mf.Manifold(mf.Mesh(vert_properties=np.asarray(pot.vertices, np.float32), tri_verts=np.asarray(pot.faces, np.uint32)))
mid = ZC + 100
from shapely import contains_xy
def zmod(m, z):
    sec_ = tm(m).section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]); p2, _ = sec_.to_2D(to_2D=np.eye(4))
    X, Y = np.meshgrid(np.arange(-40, 40, 0.05), np.arange(-10, 70, 0.05)); ins_ = np.zeros_like(X, bool)
    for pg in p2.polygons_full: ins_ |= contains_xy(pg, X, Y)
    A = ins_.sum() * 0.0025; yc_ = Y[ins_].sum() * 0.0025 / A; I = ((Y[ins_] - yc_)**2).sum() * 0.0025
    return I / max(Y[ins_].max() - yc_, yc_ - Y[ins_].min())
print("box depth %.2f mm from the lip base up (back %.2f from center, corners on the wall at R %.2f); %.2f at the insert top; back leans %.2f deg below the lip base"
      % (YB - d, YB, r1, Y0 - d, math.degrees(tilt)))
print("post %.1f cm3, section %.1f cm3; overlaps post/section %.3f, section/section %.3f, post/pot %.3f, section/pot %.3f mm3"
      % (post.volume() / 1000, sec.volume() / 1000, (post ^ (sec + hk[0] + hk[1])).volume(), (sec ^ (sec2 + hk2[0] + hk2[1])).volume(), (post ^ potM).volume(), (sec ^ potM).volume()))
print("solid-walled section modulus front-back: box %.0f mm3" % zmod(prism(0, 0, 0, mid - 1, mid + 1) - prism(SIDE, FRONT, SIDE, mid - 2, mid + 2), mid))
if len(sys.argv) > 3:
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    base = W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json"))
    for nm, m, flip in (("post", post, False), ("section", sec + hk[0] + hk[1], True)):
        t = tm(m)
        if flip: t.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        t.apply_translation([128 - (t.bounds[0][0] + t.bounds[1][0]) / 2, 128 - (t.bounds[0][1] + t.bounds[1][1]) / 2, -t.bounds[0][2]])
        W3.write(os.path.join(sys.argv[3], "boxfit_%s.3mf" % nm), [W3.Obj(nm, [W3.Part(t.vertices, t.faces)])], base, thumbnails=False)
UP2 = np.array([0.55, 0.70, 0.82])
fig, axs = plt.subplots(1, 3, figsize=(30, 13), gridspec_kw=dict(width_ratios=[1, 1.1, 1]))
ax = axs[0]; R.FACES.clear()
R.mesh(pot.slice_plane([0, 0, 0], [0, -1, 0], cap=False), CLEAR); R.mesh(tm(post), POST); R.mesh(tm(sec), UP); R.mesh(tm(sec2), UP2)
R.mesh(tm(hk[0] + hk[1]), HOOK); R.mesh(tm(hk2[0] + hk2[1]), HOOK)
cam = R.view(ax, eye=(-0.9, 1.5, 0.6), ppm=1.6, pad=8)
R.call(ax, cam, (W / 2, YB, zl), (90, -10), "lip base: back turns straight up", color="#c0392b", size=12)
R.call(ax, cam, (W / 2, YB, ZC), (90, 20), "joint: flush", color="#c0392b", size=12)
ax.set_title("From behind (front half of the pot shown):\npost (brown) and two box sections, no step, no flare", fontsize=13)
R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
ax = axs[1]; R.FACES.clear()
win = mf.Manifold.cube([200, 200, 80]).translate([-100, -100, zl - 30])
cutx = lambda m: tm(m ^ win).slice_plane([W / 2 - 3, 0, 0], [-1, 0, 0], cap=True)
R.mesh(pot.slice_plane([0, 0, zl - 30], [0, 0, 1], cap=False).slice_plane([W / 2 - 3, 0, 0], [-1, 0, 0], cap=False), CLEAR)
R.mesh(cutx(post), POST); R.mesh(cutx(sec), UP)
cam = R.view(ax, eye=(1, 0.0001, 0.0001), ppm=8.0, pad=3)
ax.set_title("Cut 3 mm in from the right side wall, seen from the right (back to the right),\nlip base - 30 to + 50 mm: the back runs flush past the lip and the joint", fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
ax = axs[2]; R.FACES.clear()
R.mesh(pot, CLEAR); R.mesh(tm(sec ^ mf.Manifold.cube([200, 200, 5]).translate([-100, -100, mid - 5])), UP)
cam = R.view(ax, eye=(0, -0.0001, 1), ppm=4.0, pad=4)
R.dim(ax, cam, (W / 2, d, mid), (W / 2, YB, mid), (4, 0, 0), "%.1f" % (YB - d))
ax.set_title("From above, a section cut at mid-height over the pot:\n60 x %.1f mm box, back corners on the lip's inner wall" % (YB - d), fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: box sized to fit the pot, no flare, no step", fontsize=16)
R.save(fig, sys.argv[2])

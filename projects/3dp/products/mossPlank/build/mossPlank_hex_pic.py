"""mossPlank hexagon cutouts through the front face (my ask 2026-10-10: hexagons cut out in a pattern; then "mirror the size
and spacing in the picture"). Cases list below: each (across the flats, rib, name) is drawn side by side. Hexes point up (their roof
sides at 30 deg from vertical, within 45 deg; flat-topped hexes would need a bridge), honeycomb rows offset half a pitch,
ribs between holes; holes either stay a rib clear of the side walls or run to them, clipped at their inner faces. Holes only on the standard sections' front face, kept 3 mm clear of
the ramp at the bottom and either 3 mm clear of the 30 mm socket at the top or run through it to the top edge; the post stays solid (inference). Drawn on the 3.5in pot:
post (cut at the lip base) with one standard section seated on it. Joint geometry from mossPlank_postCut_pic.py.
Usage: python3 mossPlank_hex_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_postCut_pic.py")).read().split("def tm(m)")[0])   # pot, insert, joint geometry

def hex_holes(zsh, s, RIB, to_walls=False, to_top=False, to_bottom=False, to_spigot=False, f=None, h=None, strip=None):
    """Point-up hexes, s across the flats, cut through the front face of the section whose shoulder is at zsh. f is the
    flats' length and h each roof's rise (default regular: roofs 60 deg from vertical); h = s / 2 makes 45 deg roofs.
    Rows are spaced so the slanted ribs are RIB wide, like the upright ones."""
    if f is None:
        f, h = s / math.sqrt(3), s / (2 * math.sqrt(3))
    ac = f + 2 * h; p = s + RIB
    L = math.hypot(h, s / 2); c1 = h * s / 2 + (s / 2) * (f / 2)
    dz = (RIB * L + c1 - h * (p / 2 - s / 2)) / (s / 2) + f / 2
    lim = W / 2 - SIDE - RIB                                 # holes stay a rib clear of the side walls' inner faces
    wi = W / 2 - SIDE                                        # with to_walls, holes run to the side walls' inner faces, clipped there
    z_lo, z_hi = zsh + PROT + RIB + ac / 2, zsh + H - SPIG - RIB - ac / 2
    n = int((z_hi - z_lo) // dz) + 1; z0 = (z_lo + z_hi) / 2 - (n - 1) * dz / 2
    if to_top:                                               # rows from the bottom band up through the socket, cut off by the top edge
        z0 = z_lo; n = int((zsh + H - 1.0 + ac / 2 - z0) // dz) + 1   # last row reaches at least 1 mm below the top edge
    shift = 0                                                # rows added below row 0, so the lattice keeps its phase
    if to_bottom:                                            # one more row below, cut off flat at the upright shoulder's top (prints upright only)
        z0 -= dz; n += 1; shift = 1
    if to_spigot:                                            # rows on down through the shoulder and the spigot to its bottom edge
        while z0 - dz + ac / 2 > zsh - SPIG + 1.0:
            z0 -= dz; n += 1; shift += 1
    depth = (FRONT + GAP + T + 0.5) if to_spigot else FRONT + 0.5   # deep enough for the spigot's front wall, inset behind the face
    pts = [(0, ac / 2), (-s / 2, f / 2), (-s / 2, -f / 2), (0, -ac / 2), (s / 2, -f / 2), (s / 2, f / 2)]
    cut, count = mf.Manifold(), 0
    for i in range(n):
        zc = z0 + i * dz; off = 0.0 if (i - shift) % 2 == 0 else p / 2
        for k in range(-10, 11):
            xc = off + k * p
            if (abs(xc) - s / 2 >= wi - 1.0) if to_walls else (abs(xc) + s / 2 > lim + 1e-9):   # to_walls: skip slivers under 1 mm
                continue
            cs = mf.CrossSection([ccw([(xc + x, zc + z) for x, z in pts])])
            cut = cut + mf.Manifold.extrude(cs, depth + 1.0).warp(lambda v: (v[0], d + depth - v[2], v[1]))   # swap plus mirror keeps it right side out
            count += 1
    if to_walls and to_spigot:
        # body: to the side walls' inner faces; shoulder and spigot: to the spigot's inner side faces, which keeps the side ramp
        # and the spigot's side walls; between, the clip runs out at 45 deg over PROT so no hole edge overhangs
        ws = W / 2 - SIDE - GAP - T
        def band(w0, w1, z0_, z1_):
            return mf.Manifold.hull_points([(sx * w, y, z) for (w, z) in ((w0, z0_), (w1, z1_)) for sx in (-1, 1) for y in (d - 50, d + 50)])
        if strip is None:
            keep = (mf.Manifold.cube([2 * ws, 100, SPIG + PROT + 1]).translate([-ws, d - 50, zsh - SPIG - 1]) +
                    band(ws, wi, zsh + PROT, zsh + 2 * PROT) +
                    mf.Manifold.cube([2 * wi, 100, H]).translate([-wi, d - 50, zsh + 2 * PROT]))
        else:
            # strip: the front face keeps a strip this wide at each side, tapering through the face's thickness to the
            # side wall's inner face (my ask 2026-10-10: side rails as wide as the ribs, side walls no thicker)
            xs_f = W / 2 - strip
            trap = [(xs_f, d - 50), (xs_f, d), (wi, d + FRONT), (wi, d + 50), (-wi, d + 50), (-wi, d + FRONT), (-xs_f, d), (-xs_f, d - 50)]
            body_keep = mf.Manifold.extrude(mf.CrossSection([ccw(trap)]), H).translate([0, 0, zsh + 2 * PROT])
            run = mf.Manifold.hull_points([(sx * ws, y, zsh + PROT) for sx in (-1, 1) for y in (d - 50, d + 50)] +
                                          [(x, y, zsh + 2 * PROT) for x, y in trap])
            keep = mf.Manifold.cube([2 * ws, 100, SPIG + PROT + 1]).translate([-ws, d - 50, zsh - SPIG - 1]) + run + body_keep
        cut = cut ^ keep
    elif to_walls:
        cut = cut ^ mf.Manifold.cube([2 * wi, 200, 2 * H + 400]).translate([-wi, d - 50, zsh - 200])
    if to_bottom:
        cut = cut ^ mf.Manifold.cube([200, 200, 2 * H]).translate([-100, d - 50, zsh + FRONT + GAP])
    return cut, count, (z0, n, dz, p, ac)

def boxprism(off_f, off_s, off_b, z0, z1):
    """Boxy section outline (my ask 2026-10-10: the back boxy above the pot's lip): flat front, sides and back, the back at
    the D outline's deepest point (y = r1); offsets inward from the front, the sides and the back."""
    return mf.Manifold.cube([W - 2 * off_s, r1 - off_b - d - off_f, z1 - z0]).translate([-W / 2 + off_s, d + off_f, z0])

def box_extension(zsh):
    """Box section: flat back, 1.24 mm back and side walls, the same D spigot as now (so it fits the post's D socket and
    the box socket above, where it bears on the front, the sides and the middle of the back). At the shoulder a hidden
    45 deg funnel runs from the box's inside to the spigot's inside: the D grown outward at 45 deg (a hull, exact for a
    convex D) until it covers the box's inside."""
    from shapely.geometry import Point as SP, box as SB
    body = boxprism(0, 0, 0, zsh, zsh + H) - boxprism(FRONT, SIDE, SIDE, zsh - 1, zsh + H + 1)
    o = so + T; f_ = FRONT + GAP + T; s_ = SIDE + GAP + T
    D2 = SB(-W / 2 + s_, d + f_, W / 2 - s_, 300).intersection(SP(0, 0).buffer(r1 - o, 256))
    inner = SB(-W / 2 + SIDE, d + FRONT, W / 2 - SIDE, r1 - SIDE)
    Hr = max(D2.distance(SP(x, y)) for x, y in inner.exterior.coords) + 0.05
    lo = [(x, y, zsh) for x, y in D2.exterior.coords]; hi = [(x, y, zsh + Hr) for x, y in D2.buffer(Hr, 64).exterior.coords]
    funnel = boxprism(FRONT, SIDE, SIDE, zsh, zsh + Hr) - mf.Manifold.hull_points(lo + hi)
    sp, hooks, (zlo, _) = spigot_with_tabs(zsh)
    body = body + funnel + sp
    for sg in (1, -1):
        body = body - window(zlo + H, sg)
    return body, hooks, Hr

HT = FRONT + GAP                                             # upright shoulder height: the front's 2.06 mm step at 45 deg

def upright_extension(zsh):
    """Extension printed upright (spigot on the bed): body from zsh + HT; between zsh and zsh + HT a shell whose outer face runs
    out from the spigot's outer face to the body's and whose inner face from the spigot's inner face to the body's, each at
    45 deg or steeper, so nothing overhangs past 45 deg (the outer one is a visible chamfer)."""
    def loft(o0, o1, z0, z1):                                # o = (round offset, front offset, side offset), lerped z0 -> z1
        cone = mf.Manifold.cylinder(z1 - z0, r1 - o0[0], r1 - o1[0], 512).translate([0, 0, z0])
        def rect(z, o):
            return [(-W / 2 + o[2], d + o[1], z), (W / 2 - o[2], d + o[1], z), (W / 2 - o[2], 200, z), (-W / 2 + o[2], 200, z)]
        return cone ^ mf.Manifold.hull_points(rect(z0, o0) + rect(z1, o1))
    body = prism(0, 0, 0, zsh + HT, zsh + H) - prism(a, FRONT, SIDE, zsh - 1, zsh + H + 1)
    outer = loft((so, FRONT + GAP, SIDE + GAP), (0, 0, 0), zsh, zsh + HT)
    inner = loft((so + T, FRONT + GAP + T, SIDE + GAP + T), (a, FRONT, SIDE), zsh - 0.001, zsh + HT + 0.001)
    sp, hooks, (zlo, _) = spigot_with_tabs(zsh)
    body = body + (outer - inner) + sp
    for sg in (1, -1):
        body = body - window(zlo + H, sg)
    return body, hooks

def tm(m):
    m = m.to_mesh(); return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=False)
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
UP = np.array([0.40, 0.55, 0.70]); HOOK = np.array([0.90, 0.55, 0.20]); POST = np.array([0.62, 0.48, 0.32])
CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
_, _, (zlo, _) = spigot_with_tabs(zl)
post = lower_out(0, 0, 0, zb, zl) - lower_out(a, FRONT, SIDE, zb - 1, zl + 1)
for sg in (1, -1):
    post = post - window(zlo, sg)
# Hex size and rib from the photo's panel (PXL_20261010_043608293.jpg, my ask 2026-10-10 "mirror the size and spacing in the
# picture"): 15.1 mm corner to corner (13.1 across the flats), 2.0 mm ribs (inference, ruler scale). The pattern runs to the
# side walls, the top edge and on down through the shoulder and the spigot to its bottom edge (my asks 2026-10-10: "to the
# walls", "up to the top", "to the bottom bottom", "not the post"); the post stays solid. A regular point-up hex's roofs sit
# 60 deg from vertical (dp 1 fails), so the options keep the photo's width and give the roofs 45 deg.
# Each option: (title, across the flats, flats length, roof rise). Usage adds an optional folder for per-option dpcheck 3mfs.
S_AF, RIB_ = 15.1 * math.sqrt(3) / 2, 2.0
REG_F = S_AF / math.sqrt(3)
REG_H = S_AF / (2 * math.sqrt(3))
# Current pass (my asks 2026-10-10): side rails as wide as the ribs, tapering into the 1.24 mm side walls; back boxy above
# the pot's lip. The box can't fit inside the lip, so it starts at the rim (105.12). Post cut 30 mm past the lip base (agreed
# change 6, fix A), so the post's socket is straight: D outline up to the rim, then a 45 deg flare (D grown outward, a hull,
# exact for a convex D) out to the box, then box up to the cut; inside, the same flare from the D's inside to the box's
# inside, so the walls keep their thickness. Hexes drawn as option B (13.1 x 17.9, 45 deg roofs) while the shape question is open.
RIM = 105.12
ZC = zl + SPIG
def flare(off_f, off_s, off_r, off_b, z0):
    """Box outline (offsets off_f, off_s, off_b) above z0, grown at 45 deg from the D outline (offsets off_f, off_s, round
    off_r) at z0; returns (solid from z0 to z0 + h, h)."""
    from shapely.geometry import Point as SP, box as SB
    D2 = SB(-W / 2 + off_s, d + off_f, W / 2 - off_s, 300).intersection(SP(0, 0).buffer(r1 - off_r, 256))
    bx = SB(-W / 2 + off_s, d + off_f, W / 2 - off_s, r1 - off_b)
    h = max(D2.distance(SP(x, y)) for x, y in bx.exterior.coords) + 0.05
    lo = [(x, y, z0) for x, y in D2.exterior.coords]; hi = [(x, y, z0 + h) for x, y in D2.buffer(h, 64).exterior.coords]
    return boxprism(off_f, off_s, off_b, z0, z0 + h) ^ mf.Manifold.hull_points(lo + hi), h
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
fo, h_o = flare(0, 0, 0, 0, RIM); fi, h_i = flare(FRONT, SIDE, a, SIDE, RIM)
outer = lower_out(0, 0, 0, zb, RIM + 0.01) + fo + boxprism(0, 0, 0, RIM + h_o - 0.01, ZC)
inner = lower_out(a, FRONT, SIDE, zb - 1, RIM + 0.01) + fi + boxprism(FRONT, SIDE, SIDE, RIM + h_i - 0.01, ZC + 1)
postR = outer - inner
for sg in (1, -1):
    postR = postR - window(zlo_p, sg)
secB0, hooksB, Hr = box_extension(ZC)
cutB, countB, (z0, n, dz, p, ac) = hex_holes(ZC, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=RIB_)
secB = secB0 - cutB
print("post %.2f mm (cut %.2f, %.2f above the rim), flare %.2f out / %.2f in, post volume %.0f mm3, post/section overlap %.3f mm3"
      % (ZC - zb, ZC, ZC - RIM, h_o, h_i, postR.volume(), (postR ^ (secB + hooksB[0] + hooksB[1])).volume()))
if len(sys.argv) > 4:                                        # post as printed (upright) for dpcheck
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    m = tm(postR); m.apply_translation([128, 128, -zb])
    W3.write(os.path.join(sys.argv[4], "boxpost.3mf"), [W3.Obj("post", [W3.Part(m.vertices, m.faces)])],
             W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
if len(sys.argv) > 3:                                        # box section as printed (upside down) for dpcheck
    m = tm(secB + hooksB[0] + hooksB[1]); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    W3.write(os.path.join(sys.argv[3], "boxsec.3mf"), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])],
             W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
corner = math.hypot(W / 2, r1)
fig, axs = plt.subplots(1, 4, figsize=(32, 12), gridspec_kw=dict(width_ratios=[1, 1.15, 1, 0.8]))
ax = axs[0]; R.FACES.clear()
LIFT = 50.0; up_ = lambda m: tm(m.translate([0, 0, LIFT]))
R.mesh(tm(postR), POST); R.mesh(up_(secB), UP); R.mesh(up_(hooksB[0] + hooksB[1]), HOOK)
cam = R.view(ax, eye=(-1.1, 1.3, 0.55), pad=8)
R.call(ax, cam, (W / 2, r1, RIM + h_o / 2), (60, 10), "45 deg flare, D to box\n(rim to %.1f mm above it)" % h_o, size=11)
R.call(ax, cam, (-W / 2, 30, (zb + RIM) / 2), (-60, -30), "post below the rim:\nD, follows the pot", size=11)
ax.set_title("Post and a box section pulled %d mm apart, from behind:\n%d hexes (option B), 2.0 mm side strips; post solid" % (LIFT, countB), fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
ax = axs[1]; R.FACES.clear()
front_half = pot.slice_plane([0, 0, 0], [0, -1, 0], cap=False)
R.mesh(front_half, CLEAR); R.mesh(tm(postR), POST); R.mesh(tm(secB), UP); R.mesh(tm(hooksB[0] + hooksB[1]), HOOK)
cam = R.view(ax, eye=(-0.9, 1.5, 0.75), pad=8)
ax.set_title("In the 3.5in pot from behind (front half of the pot shown):\npost %.1f mm, cut %.1f mm above the rim; 45 deg flare to the box at the rim" % (ZC - zb, ZC - RIM), fontsize=12)
R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
# top-down cut at a hex row, with the pot, then a close-up of one side strip
zc = z0 + round((ZC + 100 - z0) / dz) * dz                 # a hex row near mid-height
cutz = lambda m: tm(m ^ mf.Manifold.cube([300, 300, 6]).translate([-150, -150, zc - 6]))
ax = axs[2]; R.FACES.clear()
R.mesh(pot, CLEAR); R.mesh(cutz(secB), UP)
cam = R.view(ax, eye=(0, -0.02, 1), pad=4)
R.dim(ax, cam, (0, 0, zc), (W / 2, r1, zc), (0, 0, 0), "%.1f" % corner)
R.dim(ax, cam, (0, 0, zc), (-48.07 * math.sin(math.radians(30)), 48.07 * math.cos(math.radians(30)), zc), (0, 0, 0), "rim 48.07")
ax.set_title("From above, the section cut across at a hex row: back corners %.1f mm\nfrom center vs the rim's 48.07, so %.1f mm past it (inside the rim at the middle)" % (corner, corner - 48.07), fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
ax = axs[3]; R.FACES.clear()
R.mesh(cutz(secB), UP)
x0f, y0f = W / 2 - 9, d - 1.5
fr = (x0f, x0f + 11, -(y0f + 11), -y0f)                     # frame in view coordinates (right = +x, up = +y seen from above)
_, right, up = R.camera((0, -0.02, 1))
pts = np.array([[x0f, y0f, zc], [x0f + 11, y0f + 11, zc]])
sx, sy = pts @ right, pts @ up
img, cam = R.render((0, -0.02, 1), frame=(sx.min(), sx.max(), sy.min(), sy.max()), edge_depth=0.5)
ax.imshow(img); ax.axis("off")
R.dim(ax, cam, (W / 2 - RIB_, d, zc), (W / 2, d, zc), (0, -0.8, 0))
R.dim(ax, cam, (W / 2 - SIDE, d + FRONT + 5, zc), (W / 2, d + FRONT + 5, zc), (0, 0, 0))
R.dim(ax, cam, (W / 2 - 4, d, zc), (W / 2 - 4, d + FRONT, zc), (-1.5, 0, 0))
ax.set_title("Close-up of the right front corner, same cut:\n2.0 mm strip at the face tapering to the 1.24 mm side wall", fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
print("box section hexes", countB, "funnel height %.2f" % Hr, "corner radius %.2f" % corner, "post %.2f" % (ZC - zb))
fig.suptitle("mossPlank: tapered 2.0 mm side strips and a boxy back above the pot", fontsize=15)
R.save(fig, sys.argv[2])

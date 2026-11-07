"""mossPlank post-to-section joint fixes (the post's socket follows the pot's taper while the spigot is straight, so the first
section jams; found 2026-10-10 in joint test piece rev1). Two options side by side, same views:
A. The post runs on 30 mm past the lip base, where the pot is straight, so its socket is a section's straight socket.
B. The post stays cut at the lip base; every spigot's round back tapers like the pot, and every section's socket back
   thickens to match (a wedge, 0 at the top to the taper's 2.6 mm at the socket's bottom, with a 45 deg run-out below).
Rows: the 3.5in pot (cut in half down the middle) with the post and a section seated, from the side; a cut down the middle through the
post's joint; a cut through a section-to-section joint. Sections are drawn 70 mm tall (the rest cut off); hexes left out.
Joint geometry from mossPlank_postCut_pic.py. Prints each option's numbers.
Usage: python3 mossPlank_jointFix_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_postCut_pic.py")).read().split("def tm(m)")[0])   # pot, joint geometry
def tm(m):
    m = m.to_mesh(); return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=False)
rim = 105.12
k = (r1 - r0) / (zl - zb)                                    # pot taper, mm of radius per mm of height
DT = k * SPIG                                                # radius lost over a spigot's length
SHOW = 70.0                                                  # section height drawn
UP = np.array([0.40, 0.55, 0.70]); HOOK = np.array([0.90, 0.55, 0.20]); POST = np.array([0.62, 0.48, 0.32])
CLEAR = np.array([0.80, 0.86, 0.90]); UP2 = np.array([0.55, 0.70, 0.82])

def dbox(front, side, z0, z1):
    return mf.Manifold.cube([W - 2 * side, 200, z1 - z0]).translate([-W / 2 + side, d + front, z0])
def cone_d(off, front, side, zbot, ztop, rbot, rtop):        # D with a round back running from rbot to rtop
    return mf.Manifold.cylinder(ztop - zbot, rbot - off, rtop - off, 512).translate([0, 0, zbot]) ^ dbox(front, side, zbot, ztop)
def spigot_B(zsh):
    """Straight spigot's front and sides, round back tapering like the pot (radius r1 at zsh, r1 - DT at zsh - SPIG)."""
    sp, hooks, zz = spigot_with_tabs(zsh)
    z0 = zsh - SPIG
    trim = prism(so, FRONT + GAP, SIDE + GAP, z0, zsh) - cone_d(so, FRONT + GAP, SIDE + GAP, z0, zsh, r1 - DT, r1)
    inner = cone_d(so + T, FRONT + GAP + T, SIDE + GAP + T, z0 - 0.001, zsh + 0.001, r1 - DT, r1)
    return sp - trim - inner, hooks, zz
def wedge_B(ztop):
    """Socket-back wedge for option B inside a section whose top is ztop: matches spigot_B's taper, 45 deg run-out below."""
    zm = ztop - SPIG
    taper = cone_d(a, FRONT, SIDE, zm, ztop + 0.001, r1 - DT, r1) + cone_d(a, FRONT, SIDE, zm - DT, zm, r1, r1 - DT)
    return prism(a, FRONT, SIDE, zm - DT, ztop) - taper
def section(zsh, opt):
    body = prism(0, 0, 0, zsh, zsh + H) - prism(a, FRONT, SIDE, zsh - 1, zsh + H + 1)
    sp, hooks, (zlo, _) = (spigot_with_tabs if opt == "A" else spigot_B)(zsh)
    body = body + ramp(zsh) + sp
    if opt == "B":
        body = body + wedge_B(zsh + H)
    for sg in (1, -1):
        body = body - window(zlo + H, sg)
    return body, hooks
def post_for(opt):
    zc = zl + SPIG if opt == "A" else zl                    # post cut
    _, _, (zlo, _) = spigot_with_tabs(zc)
    p = lower_out(0, 0, 0, zb, zc) - lower_out(a, FRONT, SIDE, zb - 1, zc + 1)
    for sg in (1, -1):
        p = p - window(zlo, sg)
    return p, zc
clip = lambda m, z: m ^ mf.Manifold.cube([200, 200, z - zb + 1]).translate([-100, -100, zb - 1])
half = lambda m: tm(m).slice_plane([0, 0, 0], [-1, 0, 0], cap=True)
left_half = pot.slice_plane([0, 0, 0], [-1, 0, 0], cap=False)
OPTS = {}
for opt in ("A", "B"):
    p, zc = post_for(opt)
    s1, h1 = section(zc, opt)
    s2, h2 = section(zc + H, opt)                            # next section up, for the section-to-section row
    hooks = h1[0] + h1[1]
    over_p = (p ^ (s1 + hooks)).volume()
    over_s = (s1 ^ s2).volume()
    OPTS[opt] = (p, zc, s1, h1, s2, h2)
    extra = (wedge_B(zc + H).volume() if opt == "B" else 0.0)
    print(opt, "post cut %.2f (post %.2f mm, %.2f above the rim), post volume %.0f mm3, overlap post/section %.2f, section/section %.2f mm3, wedge per section %.0f mm3 (%.2f g PETG at 1.27)"
          % (zc, zc - zb, zc - rim, p.volume(), over_p, over_s, extra, extra * 1.27e-3))
TITLES = {"A": "A. Post runs 30 mm past the lip base: straight socket",
          "B": "B. Post at the lip base; spigot backs taper like the pot"}
def row(axrow, eye, pad, builders):
    """Draw each option's panel in one row with the same frame and scale: build, fit, union the frames, then render."""
    frames = []
    for b in builders:
        R.FACES.clear(); b(); frames.append(R.fit(eye, pad))
    U = (min(f[0] for f in frames), max(f[1] for f in frames), min(f[2] for f in frames), max(f[3] for f in frames))
    cams = []
    for ax, b in zip(axrow, builders):
        R.FACES.clear(); b(); img, cam = R.render(eye, frame=U); ax.imshow(img); ax.axis("off"); cams.append(cam)
    return cams
fig, axs = plt.subplots(3, 2, figsize=(20, 30), gridspec_kw=dict(height_ratios=[1.3, 1, 1]))
def b1(opt):
    p, zc, s1, h1, s2, h2 = OPTS[opt]
    return lambda: (R.mesh(left_half, CLEAR), R.mesh(tm(p), POST), R.mesh(tm(clip(s1, zl + SPIG + SHOW)), UP), R.mesh(tm(h1[0] + h1[1]), HOOK))
def b2(opt):
    p, zc, s1, h1, s2, h2 = OPTS[opt]
    return lambda: (R.mesh(half(clip(p, zc + 5)), POST), R.mesh(half(clip(s1, zc + 15)), UP))
def b3(opt):
    p, zc, s1, h1, s2, h2 = OPTS[opt]
    win = mf.Manifold.cube([200, 200, 50]).translate([-100, -100, zc + H - 38])
    return lambda: (R.mesh(half((s1 ^ win).translate([0, 0, -zc])), UP), R.mesh(half((s2 ^ win).translate([0, 0, -zc])), UP2))
c1 = row(axs[0], (1.4, 0.9, 0.35), 8, [b1("A"), b1("B")])
c2 = row(axs[1], (1, 0, 0), 6, [b2("A"), b2("B")])
c3 = row(axs[2], (1, 0, 0), 6, [b3("A"), b3("B")])
for j, opt in enumerate(("A", "B")):
    p, zc, s1, h1, s2, h2 = OPTS[opt]
    ax, cam = axs[0][j], c1[j]
    R.call(ax, cam, (0.0, -P["r_lb"] - 1.0, rim), (-40, 30), "rim", size=10)
    R.dim(ax, cam, (W / 2, d + 2, zb), (W / 2, d + 2, zc), (0, -14, 0), "post %.1f" % (zc - zb))
    ax.set_title("%s\nin the pot (cut in half down the middle), section above it cut off" % TITLES[opt], fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax, cam = axs[1][j], c2[j]
    z0 = zc - SPIG
    gb = (rin(z0) if opt == "B" else r1) - a - ((r1 - DT) if opt == "B" else r1) + so
    ax.set_title("%s: post-to-section joint, cut down the middle, from the side\nback gap at the spigot's bottom %.2f mm (0.20 all the way up)" % (opt, gb), fontsize=13)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
    ax, cam = axs[2][j], c3[j]
    zt = H
    if opt == "B":
        R.call(ax, cam, (0, r1 - a - DT / 2, zt - SPIG + 2), (-140, -40), "back thickened to match (%.1f mm at the bottom)" % (SIDE + DT), size=10)
    ax.set_title("%s: section-to-section joint, same cut\n%s" % (opt, "unchanged" if opt == "A" else "every socket back carries the taper wedge"), fontsize=13)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: two fixes for the post's tapered socket (hexes left out; neither fix touches them)", fontsize=16)
R.save(fig, sys.argv[2])

"""mossPlank side strips on the D sections (box back dropped 2026-10-10), two ways side by side:
A. Agreed change 5 as is: hexes run to the side walls' inner faces, clipped there.
B. Side strips (my asks 2026-10-10: side rails as thick as the ribs, side walls no thicker, side face tapering into the wall):
   the front face keeps a 2.0 mm strip at each side, tapering through the face's thickness to the 1.24 mm side wall.
Both on the 3.5in pot with the 93 mm D post (agreed change 6) and one D section seated, hexes option B (13.1 x 17.9).
Rows: in the pot from the front; a cut across at a hex row from above, close to the right front corner.
Usage: python3 mossPlank_strips_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_hex_pic.py")).read().split("_, _, (zlo_p, _) = spigot_with_tabs(ZC)")[0])
_, _, (zlo_p, _) = spigot_with_tabs(ZC)
postD = lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postD = postD - window(zlo_p, sg)
s0, hk = extension(ZC)
OPT = {}
for k, strip in (("A", None), ("B", RIB_)):
    cut, cnt, (z0, n, dz, p, ac) = hex_holes(ZC, S_AF, RIB_, True, True, False, True, 4.78, S_AF / 2, strip=strip)
    s = s0 - cut
    OPT[k] = (s, cnt)
    print(k, "hexes", cnt, "section volume %.1f cm3" % (s.volume() / 1000), "overlap with post %.3f" % (s ^ postD).volume())
    if len(sys.argv) > 3:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
        m = tm(s + hk[0] + hk[1]); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
        W3.write(os.path.join(sys.argv[3], "stripsec_%s.3mf" % k), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])],
                 W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json")), thumbnails=False)
zc = z0 + round((ZC + 100 - z0) / dz) * dz
TT = {"A": "A. Agreed change 5: hexes run to the side walls,\nclipped at their inner faces", "B": "B. Side strips: 2.0 mm at the face,\ntapering to the 1.24 mm side wall"}
fig, axs = plt.subplots(2, 2, figsize=(20, 22), gridspec_kw=dict(height_ratios=[1.5, 1]))
back_half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
for j, k in enumerate("AB"):
    s, cnt = OPT[k]
    ax = axs[0][j]; R.FACES.clear()
    R.mesh(back_half, CLEAR); R.mesh(tm(postD), POST); R.mesh(tm(s), UP); R.mesh(tm(hk[0] + hk[1]), HOOK)
    cam = R.view(ax, eye=(-0.9, -1.5, 0.6), ppm=3.0, pad=8)
    ax.set_title("%s\nin the 3.5in pot from the front (back half of the pot shown), %d hexes" % (TT[k], cnt), fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
    ax = axs[1][j]; R.FACES.clear()
    R.mesh(tm(s ^ mf.Manifold.cube([300, 300, 6]).translate([-150, -150, zc - 6])), UP)
    x0f, y0f = W / 2 - 9, d - 1.5
    _, right, up = R.camera((0, -0.02, 1))
    pts = np.array([[x0f, y0f, zc], [x0f + 11, y0f + 11, zc]])
    sx, sy = pts @ right, pts @ up
    img, cam = R.render((0, -0.02, 1), frame=(sx.min(), sx.max(), sy.min(), sy.max()), edge_depth=0.5)
    ax.imshow(img); ax.axis("off")
    if k == "B":
        R.dim(ax, cam, (W / 2 - RIB_, d, zc), (W / 2, d, zc), (0, -0.8, 0))
    R.dim(ax, cam, (W / 2 - SIDE, d + FRONT + 5, zc), (W / 2, d + FRONT + 5, zc), (0, 0, 0))
    R.dim(ax, cam, (W / 2 - 4.5, d, zc), (W / 2 - 4.5, d + FRONT, zc), (-1.5, 0, 0))
    ax.set_title("%s: cut across at a hex row, right front corner, from above" % k, fontsize=12)
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank: side strips on the D sections (hexes option B)", fontsize=16)
R.save(fig, sys.argv[2])

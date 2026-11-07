"""mossPlank sliding hex plate sized for its design load (agreed 2026-10-11, my pick on a card: 1 kg at the plate's center,
pulled or pushed, safety factor 3). The 45 deg catch can't hold it at any plate thickness: its flank pushes the 1.24 mm
side walls out (hand check about 0.56 mm per kg) past the most overlap the 2.0 rail and the 1.24 wall leave (0.56 mm).
This model (inference, my sizes): a square catch, so a pull on the plate pulls straight on the rail lip and pushes nothing
sideways. A square step can't print face down (its catch face would be a flat roof), so the plate prints face UP (back on
the bed). Plate 3.0 mm (10 layers at 0.30): front part 1.5 mm (5 layers) through the slot, 27.8 half-width (0.2 to the
lip); flange 1.5 mm behind the 1.24 rail lip (0.26 gap), 28.56 half-width (0.2 to the side wall), its back outer corner
cut 1.2 at 45 deg so the fit starts 1.2 mm above the bed (design principle 1). Groove out to the side wall's inner face, so
the wall stays 1.24 there. Back lips move back behind the flange. The next section's spigot side walls start 0.2 behind
the plate (y = d + 3.2) so the thicker plate clears them in the socket; tabs unchanged. Corner stops and corner cuts as in
mossPlank_plateStop_pic.py. Hand check as mossPlank_plateLoad_pic.py (simply supported strip, net section, L / 2 wide).
Usage: python3 mossPlank_plateCatch_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png] [3mf folder, optional]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
_out = sys.argv[2:]; sys.argv[2:] = ["/dev/null"]
exec(open(os.path.join(HERE, "mossPlank_plateStop_pic.py")).read().split("# ---- picture")[0].replace("    sys.exit(0)", "    pass"))
sys.argv[2:] = _out
old = dict(sec=secB, pl=plB, hk=hk2, n=nB, TP=TP, xg=xg)
TP, TF, YL, CH = 3.0, 1.5, 1.24, 1.2                       # plate, front part, rail lip, flange back chamfer
xf = W / 2 - SIDE - C                                      # flange half-width
xg = W / 2 - SIDE                                          # groove's outer side = side wall's inner face
plate2d = sym([(xp, d), (xp, d + TF), (xf, d + TF), (xf, d + TP - CH), (xf - CH, d + TP)][::-1])
chan2d = sym([(W / 2 - WR, d - 5), (W / 2 - WR, d + YL), (xg, d + YL), (xg, d + TP + C), (0.01, d + TP + C)][::-1])
def front_cut(zsh):
    xi = W / 2 - SIDE - GAP - T
    return mf.Manifold.cube([2 * xi, FRONT + GAP + T + 1.02, SPIG + PROT + 1.5]).translate([-xi, d - 1, zsh - SPIG - 1])
def spigot_trim(zsh):
    """Front of the spigot's side walls, so they start 0.2 behind the plate's back."""
    out = mf.Manifold()
    for sg in (1, -1):
        out = out + mf.Manifold.cube([T + 0.1, TP + C + 1, SPIG + 1.01]).translate([sg * (W / 2 - SIDE - GAP - T / 2) - (T + 0.1) / 2, d - 1, zsh - SPIG - 1])
    return out
def sectionS(zsh):
    body, hk = section(zsh)
    return body - front_cut(zsh) - spigot_trim(zsh) + stops(zsh), hk
secS, hkS = sectionS(ZC); plS, nS = plateB(ZC)
secSU, hkSU = sectionS(ZC + H); plSU, _ = plateB(ZC + H)
hkS2, hkSU2 = hkS[0] + hkS[1], hkSU[0] + hkSU[1]
print("square catch: plate %.1f mm, %d hexes, %.2f cm3; section %.2f cm3 (45 deg catch: plate %.2f, section %.2f)" % (
    TP, nS, plS.volume() / 1000, secS.volume() / 1000, old["pl"].volume() / 1000, old["sec"].volume() / 1000))
ov = lambda A_, B_: (A_ ^ B_).volume()
print("overlaps (mm3): plate/section %.3f, plate/upper section+hooks %.3f, upper plate/section %.3f, plate/post %.3f, upper section/section %.3f, upper hooks/section %.3f" % (
    ov(plS, secS), ov(plS, secSU + hkSU2), ov(plSU, secS), ov(plS, postB), ov(secSU, secS), ov(hkSU2, secS)))
print("worst overlap sliding the plate in from the top: %.3f mm3; pushed 0.3 down: %.3f (a stop catches it); end for end: %.3f" % (
    max(ov(plS.translate([0, 0, t]), secS) for t in list(range(1, int(H) + 1, 10)) + [0.05, 0.2]),
    ov(plS.translate([0, 0, -0.3]), secS), ov(plS.mirror([0, 0, 1]).translate([0, 0, 2 * ZC + H]), secS)))
print("plate pulled 0.3 forward: overlap with section %.3f mm3 (the catch holds it); pushed 0.3 back: %.3f (back lips hold it)" % (
    ov(plS.translate([0, -0.3, 0]), secS), ov(plS.translate([0, 0.3, 0]), secS)))
# hand check (inference): as mossPlank_plateLoad_pic.py
EMOD, SIG = 2050.0, 64.0
mm_ = tm(plS); zmid = ZC + H / 2; samp = np.linspace(zmid - 30, zmid + 30, 1201)
phi = min(mm_.contains(np.c_[np.full_like(samp, c), np.full_like(samp, d + TP / 2), samp]).mean() for c in np.linspace(0, S_AF + RIB_, 31))
Lsp = 2 * xp; ovl = xf - (W / 2 - WR)
def strip(t, L, b):
    S = phi * b * t * t / 6; I = phi * b * t ** 3 / 12
    return 4 * SIG * S / L / 9.81, 9.81 * L ** 3 / (48 * EMOD * I)
brk, dkg = strip(TP, Lsp, Lsp / 2); dslip = math.sqrt(3 * Lsp * ovl / 4)
print("hand check: solid share %.3f, span %.1f, overlap %.2f: breaks at %.2f kg (%.2f at SF 3), bows %.2f mm per kg, slips at %.2f kg (%.2f at SF 3)" % (
    phi, Lsp, ovl, brk, brk / 3, dkg, dslip / dkg, dslip / dkg / 3))
if len(_out) > 1:
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts")); import write3mf as W3
    base = W3.base(os.path.join(HERE, "..", "..", "rail", "build", "rail_settings_base.json"))
    m = tm(plS); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))   # back (y = d + TP) down
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    W3.write(os.path.join(_out[1], "plateS.3mf"), [W3.Obj("plate", [W3.Part(m.vertices, m.faces)])], base, thumbnails=False)
    m = tm(secS + hkS2); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    m.apply_translation([128 - (m.bounds[0][0] + m.bounds[1][0]) / 2, 128 - (m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]])
    W3.write(os.path.join(_out[1], "sectionS.3mf"), [W3.Obj("section", [W3.Part(m.vertices, m.faces)])], base, thumbnails=False)
if _out[0] == "/dev/null":
    sys.exit(0)
# ---- picture
PL = np.array([0.45, 0.62, 0.40]); SPOT = np.array([0.95, 0.10, 0.75]); UP2 = np.array([0.55, 0.68, 0.80])
back_pot = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); back_ins = ins.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
edge = lambda m: m ^ (mf.Manifold.cube([10, 40, 400]).translate([W / 2 - 3.2, d - 10, 0]) + mf.Manifold.cube([10, 40, 400]).translate([-W / 2 - 6.8, d - 10, 0]))
OPTS = {"now": dict(sec=old["sec"], pl=old["pl"], hk=old["hk"], secU=secBU, hkU=hk2U, plU=plBU, TP=old["TP"]),
        "sq": dict(sec=secS, pl=plS, hk=hkS2, secU=secSU, hkU=hkSU2, plU=plSU, TP=TP)}
def row(axrow, eye, pad, builders, **kw):
    frames = []
    for b in builders:
        R.FACES.clear(); b(); frames.append(R.fit(eye, pad))
    U = (min(f[0] for f in frames), max(f[1] for f in frames), min(f[2] for f in frames), max(f[3] for f in frames))
    cams = []
    for ax, b in zip(axrow, builders):
        R.FACES.clear(); b(); img, cam = R.render(eye, frame=U, **kw); ax.imshow(img); ax.axis("off"); cams.append(cam)
    return cams
fig, axs = plt.subplots(4, 2, figsize=(26, 46), gridspec_kw=dict(height_ratios=[1.25, 0.8, 0.8, 0.8]))
# row 0: whole design, plate edges bright
def b0(k):
    o = OPTS[k]
    return lambda: (R.mesh(back_pot, CLEAR), R.mesh(back_ins, INS), R.mesh(tm(postB), POST), R.mesh(tm(o["sec"]), UP), R.mesh(tm(o["hk"]), HOOK),
                    R.mesh(tm(o["pl"] - edge(o["pl"])), PL), R.mesh(tm(edge(o["pl"])), SPOT))
c0 = row(axs[0], (-0.9, -1.5, 0.35), 8, [b0("now"), b0("sq")])
axs[0][0].set_title("A: 45 deg catch, plate 1.8 mm printed face down (as now)\nwhole design, plate edges pink, from the front left", fontsize=14)
axs[0][1].set_title("B: square catch, plate 3.0 mm printed face up\nwhole design, plate edges pink, from the front left", fontsize=14)
# row 1: right rail corner cut at mid-height, from above, front at the bottom
zc_ = ZC + H / 2
cut_ = lambda m, z: tm(m ^ mf.Manifold.cube([300, 300, 2]).translate([-150, -150, z - 2]))
P3 = np.array([[W / 2 - 6.5, d - 2.2, zc_], [W / 2 + 0.6, d + 6.5, zc_]])
def b1(k):
    o = OPTS[k]
    return lambda: (R.mesh(cut_(o["sec"], zc_), UP), R.mesh(cut_(o["pl"], zc_), PL))
fr = (P3 @ R.camera((0, -0.02, 1))[1]).tolist(); fu = (P3 @ R.camera((0, -0.02, 1))[2]).tolist()
c1 = []
for ax, k in zip(axs[1], ("now", "sq")):
    R.FACES.clear(); b1(k)(); img, cam = R.render((0, -0.02, 1), frame=(min(fr), max(fr), min(fu), max(fu)), edge_depth=0.5); ax.imshow(img); ax.axis("off"); c1.append(cam)
cam = c1[0]
R.dim(ax=axs[1][0], cam=cam, a=(W / 2 - WR, d - 0.4, zc_), b=(W / 2, d - 0.4, zc_), off=(0, -0.8, 0))
R.dim(axs[1][0], cam, (W / 2 - 5.0, d, zc_), (W / 2 - 5.0, d + 1.8, zc_), (-0.8, 0, 0))
R.dim(axs[1][0], cam, (old["xg"], d + 2.3, zc_), (W / 2, d + 2.3, zc_), (0, 1.2, 0))
cam = c1[1]
R.dim(axs[1][1], cam, (W / 2 - WR, d - 0.4, zc_), (W / 2, d - 0.4, zc_), (0, -0.8, 0))
R.dim(axs[1][1], cam, (W / 2 - 5.0, d, zc_), (W / 2 - 5.0, d + TP, zc_), (-0.8, 0, 0))
R.dim(axs[1][1], cam, (W / 2 - 3.6, d, zc_), (W / 2 - 3.6, d + TF, zc_), (-0.4, 0, 0))
R.dim(axs[1][1], cam, (xg, d + TP + C + 1.5, zc_), (W / 2, d + TP + C + 1.5, zc_), (0, 1.0, 0))
R.dim(axs[1][1], cam, (W / 2 - WR, d + YL + 0.1, zc_), (xf, d + YL + 0.1, zc_), (0, -0.1, 0), "%.2f" % (xf - (W / 2 - WR)))
for ax, cam, pts, t in ((axs[1][0], c1[0], ((W / 2 - WR + 0.2, d + 1.6, zc_), (W / 2 - WR + 1.6, d + 0.2, zc_)), "pull pushes the\nwall out 45 deg"),
                        (axs[1][1], c1[1], ((W / 2 - WR + 0.28, d + YL + 1.6, zc_), (W / 2 - WR + 0.28, d + YL + 0.15, zc_)), "pull goes straight\ninto the lip")):
    A2, B2 = np.array(R.proj(cam, pts[0])), np.array(R.proj(cam, pts[1]))
    ax.annotate("", xy=B2, xytext=A2, arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=3, mutation_scale=22))
    ax.text(B2[0] + 30, B2[1] - 10, t, color="#c0392b", fontsize=12, fontweight="bold", ha="left", va="bottom", bbox=dict(fc="white", ec="none", alpha=0.85))
axs[1][0].set_title("A: right rail cut across at mid-height, from above (front at the bottom):\n0.6 mm 45 deg flank, 0.4 overlap behind the lip; side wall 1.4 at the groove", fontsize=13)
axs[1][1].set_title("B: same cut: front part 1.5, flange 1.5 behind the 1.24 lip (0.26 gap),\n0.56 overlap; groove to the side wall's inner face, wall 1.24", fontsize=13)
# row 2: in the socket, cut 12 mm below the lower section's top: lower section, its plate, the upper section's spigot
zs_ = ZC + H - 12
def b2(k):
    o = OPTS[k]
    return lambda: (R.mesh(cut_(o["sec"], zs_), UP), R.mesh(cut_(o["pl"], zs_), PL), R.mesh(cut_(o["secU"], zs_), UP2))
P3s = np.array([[W / 2 - 9.5, d - 2.2, zs_], [W / 2 + 0.6, d + 8.0, zs_]]); fr = (P3s @ R.camera((0, -0.02, 1))[1]).tolist(); fu = (P3s @ R.camera((0, -0.02, 1))[2]).tolist()
for ax, k, t in zip(axs[2], ("now", "sq"), ("A: in the socket, 12 mm below the lower section's top, from above:\nupper section's spigot (light blue) behind the plate",
                                            "B: same cut: the spigot's side walls now start 0.2 behind the 3.0 plate\n(front 1.14 trimmed; tabs unchanged)")):
    R.FACES.clear(); b2(k)(); img, cam = R.render((0, -0.02, 1), frame=(min(fr), max(fr), min(fu), max(fu)), edge_depth=0.5); ax.imshow(img); ax.axis("off")
    ax.set_title(t, fontsize=13); R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
# row 3: the plate's right edge as printed, cut across at mid-height, seen end-on with the bed at the bottom
def pedge(k):
    o = OPTS[k]; m = o["pl"] ^ mf.Manifold.cube([9, 20, 2]).translate([W / 2 - 8.5, d - 5, zc_ - 2])
    m = m.rotate([90, 0, 0]) if k == "now" else m.rotate([-90, 0, 0])     # face down (z' = y) or back down (z' = -y): rotations
    b = m.bounding_box(); return m.translate([0, 0, -b[2]])
c3 = []
for ax, k in zip(axs[3], ("now", "sq")):
    R.FACES.clear(); R.mesh(tm(pedge(k)), PL)
    P3e = np.array([[W / 2 - 9.0, 0, -0.8], [W / 2 + 0.8, 0, 3.6]]); _, rt, upv = R.camera((0, -1, 0.0001))
    fx, fz = (P3e @ rt).tolist(), (P3e @ upv).tolist()
    img, cam = R.render((0, -1, 0.0001), frame=(min(fx), max(fx), min(fz), max(fz)), edge_depth=0.3); ax.imshow(img); ax.axis("off"); c3.append(cam)
    A2, B2 = np.array(R.proj(cam, (W / 2 - 9.0, 0, 0))), np.array(R.proj(cam, (W / 2 + 0.8, 0, 0)))
    ax.plot([A2[0], B2[0]], [A2[1], B2[1]], color="#333", lw=3); ax.text(A2[0] + 10, A2[1] + 25, "bed", fontsize=12, color="#333", va="top")
R.dim(axs[3][0], c3[0], (xp + E + 0.3, 0, 0), (xp + E + 0.3, 0, YS), (0.4, 0, 0)); R.dim(axs[3][0], c3[0], (xp + E + 0.3, 0, YS), (xp + E + 0.3, 0, old["TP"]), (0.4, 0, 0))
R.dim(axs[3][1], c3[1], (xf + 0.3, 0, 0), (xf + 0.3, 0, CH), (0.4, 0, 0)); R.dim(axs[3][1], c3[1], (xf + 0.3, 0, CH), (xf + 0.3, 0, TP - TF), (0.4, 0, 0))
R.dim(axs[3][1], c3[1], (xf + 0.3, 0, TP - TF), (xf + 0.3, 0, TP), (0.4, 0, 0))
axs[3][0].set_title("A: plate's right edge as printed, face down, cut across (bed at the bottom):\nstraight 1.2 at the bed, then the 45 deg flank widening up", fontsize=13)
axs[3][1].set_title("B: plate's right edge as printed, face up (back on the bed), same cut:\n1.2 mm 45 deg cut at the bed, flange to 1.5, square step (a top surface), front part 1.5", fontsize=13)
for ax, cam in zip(list(axs[0]) + list(axs[1]) + list(axs[3]), c0 + c1 + c3):
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank slide for 1 kg at the plate's center, safety factor 3 (hand check, inference; fillets left out)\n"
             "A, 45 deg catch: breaks at 1.3 kg, slips at about 0.4 kg (fails at any thickness: walls pushed out).   "
             "B, square catch: breaks at %.1f kg, slips at %.1f kg, bows %.1f mm per kg; plate %.1f cm3 vs 6.3" % (brk, dslip / dkg, dkg, plS.volume() / 1000), fontsize=16)
R.save(fig, _out[0])

"""mossPlank sliding hex plate: the plate's loads, where they act and the space it can grow into (picture before the
design-load card, build-3dp), plus a first-pass hand check of what the current slide holds (all inference).
Loads drawn: a pull or push square to the plate at its center (a stem tied to it, a hand or moss packing pressing it).
Hand check: the plate spans between its two dovetail edges (bearing at the flank's middle) as a simply supported strip of
effective width L / 2, its net section the lowest solid share on a line along its length (measured on the model); PETG HF
64 MPa along layers (it prints flat), E 2,050 MPa (data sheet, config.3dp). It slips out of the rails when the bow pulls each edge in
by the catch overlap behind the rail lip (chord shortening 4/3 * bow^2 / L per edge), and the 45 deg flank pushes each side
wall out (cantilever from the back, 15 mm, over 30 mm of height, no friction), which uses the same overlap.
Usage: python3 mossPlank_plateLoad_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
_out = sys.argv[2]; sys.argv[2] = "/dev/null"
_src = open(os.path.join(HERE, "mossPlank_plateStop_pic.py")).read().split("# ---- picture")[0].replace("    sys.exit(0)", "    pass")
exec(_src); sys.argv[2] = _out
EMOD, SIG = 2050.0, 64.0
PL = np.array([0.45, 0.62, 0.40])
back_pot = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); back_ins = ins.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
mm = tm(plB); zmid = ZC + H / 2
samp = np.linspace(zmid - 30, zmid + 30, 1201)
phi = min(mm.contains(np.c_[np.full_like(samp, c), np.full_like(samp, d + TP / 2), samp]).mean() for c in np.linspace(0, S_AF + RIB_, 31))
Lsp = 2 * (xp + E / 2); ov = (xp + E) - (W / 2 - WR)
def strip(t, b=Lsp / 2):
    S = phi * b * t * t / 6; I = phi * b * t ** 3 / 12
    Pb = 4 * SIG * S / Lsp; dkg = 9.81 * Lsp ** 3 / (48 * EMOD * I)
    return Pb / 9.81, dkg
brk, dkg = strip(TP)
dpop = math.sqrt(3 * Lsp * ov / 4)
Iw = SIDE ** 3 / 12; splay = (9.81 / 2 / 30.0) * 15.0 ** 3 / (3 * EMOD * Iw)
# slip-out: splay (linear in load) + bow chord shortening (quadratic) = overlap
kg = 0.0
while splay * kg + 4 / 3 * (dkg * kg) ** 2 / Lsp < ov: kg += 0.005
print("solid share on the weakest line along the plate %.3f; span %.1f mm; catch overlap %.2f mm" % (phi, Lsp, ov))
print("plate %.1f mm: breaks at %.2f kg at its center (%.2f kg at SF 3); bows %.2f mm per kg" % (TP, brk, brk / 3, dkg))
print("slips out of the rails at about %.2f kg (bow alone %.2f kg; side wall splay %.2f mm per kg alone %.2f kg)" % (kg, dpop / dkg, splay, ov / splay))
# ---- picture: the plate's loads and the space it can grow into
fig, axs = plt.subplots(1, 2, figsize=(26, 14), gridspec_kw=dict(width_ratios=[0.8, 1.4]))
ax = axs[0]; R.FACES.clear()
R.mesh(back_pot, CLEAR); R.mesh(back_ins, INS); R.mesh(tm(postB), POST); R.mesh(tm(secB), UP); R.mesh(tm(hk2), HOOK); R.mesh(tm(plB), PL)
cam = R.view(ax, eye=(-1.0, -1.0, 0.3), pad=8)
pc = np.array([0, d, zmid])
for sgn, col, lab, dz_ in ((-1, "#c0392b", "pull out (stem tied on)", 6.0), (1, "#1f5fa8", "push in (hand, moss packing)", -6.0)):
    p0 = pc + [0, 0, dz_]; p1 = p0 + [0, -60, 0]
    tail, head = (p1, p0) if sgn > 0 else (p0, p1)
    A2, B2 = np.array(R.proj(cam, tail)), np.array(R.proj(cam, head))
    ax.annotate("", xy=B2, xytext=A2, arrowprops=dict(arrowstyle="-|>", color=col, lw=3.5, mutation_scale=28))
    P0, P1 = np.array(R.proj(cam, p0)), np.array(R.proj(cam, p1)); right = P1[0] > P0[0]
    ax.text(P1[0] + (10 if right else -10), P1[1], lab, color=col, fontsize=12, fontweight="bold", ha="left" if right else "right", va="center",
            bbox=dict(fc="white", ec="none", alpha=0.9))
ax.set_title("Design load at the plate's center, square to it, either way;\nshown on the lower section, from the front left", fontsize=13)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
# top-down cut across the whole width at mid-height, front at the bottom
zc_ = zmid; cut_ = lambda m: tm(m ^ mf.Manifold.cube([300, 300, 3]).translate([-150, -150, zc_ - 3]))
ax = axs[1]; R.FACES.clear(); R.mesh(cut_(secB), UP); R.mesh(cut_(plB), PL)
img, cam = R.render((0, -0.02, 1), frame=None, pad=4, edge_depth=0.5)
ax.imshow(img); ax.axis("off")
R.dim(ax, cam, (-(xp + E / 2), d, zc_), (xp + E / 2, d, zc_), (0, -3.5, 0), "span %.1f between the edges' bearing" % Lsp)
R.dim(ax, cam, (W / 2 - WR, d, zc_), (W / 2, d, zc_), (0, -1.2, 0))
R.dim(ax, cam, (-W / 2 + 6, d, zc_), (-W / 2 + 6, d + TP, zc_), (-1.0, 0, 0))
R.dim(ax, cam, (xg, d + TP + 0.5, zc_), (W / 2, d + TP + 0.5, zc_), (0, 1.5, 0))
R.call(ax, cam, (0, d, zc_), (0, -120), "face flush with the 2.0 rail faces (your ask): fixed", color="#444", size=11)
R.call(ax, cam, (W / 2 - 0.6, d + 8, zc_), (90, 40), "side walls 1.24 (your ask: no thicker); 1.4 at the groove", color="#444", size=11)
R.call(ax, cam, (W / 2 - WR - 0.3, d + TP - 0.2, zc_), (60, -90), "catch: 45 deg flank, %.1f out;\n%.1f overlap behind the rail lip" % (E, ov), color="#2e6b2a", size=11)
A2 = np.array(R.proj(cam, (-12, d + TP + 0.3, zc_))); B2 = np.array(R.proj(cam, (-12, d + TP + 9, zc_)))
ax.annotate("", xy=B2, xytext=A2, arrowprops=dict(arrowstyle="-|>", color="#8e44ad", lw=3, mutation_scale=22))
ax.text(B2[0], B2[1] - 25, "room to grow: back into the moss hollow\n(thicker plate, deeper ribs, deeper catch)", color="#8e44ad", fontsize=12, fontweight="bold", ha="center")
ax.set_title("Cut across at mid-height, from above (front at the bottom): plate 1.8 (6 layers) spanning the rails, cut through a hex row.\n"
             "First-pass hand check (inference): breaks at about %.1f kg at its center (%.2f kg at safety factor 3);\n"
             "bows %.1f mm per kg and slips out of the rails at about %.1f kg (bow plus side walls pushed out by the 45 deg catch)" % (brk, brk / 3, dkg, kg), fontsize=12)
R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank sliding hex plate: its loads and the room it can grow into (corner-stop model; fillets left out)", fontsize=16)
R.save(fig, sys.argv[2])

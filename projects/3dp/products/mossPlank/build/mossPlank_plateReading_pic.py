"""mossPlank sliding hex plate: the two readings of my ask "make the hexagon face a plate that slides in from the top of the
pole" (2026-10-10), drawn side by side on a two-section pole on its post in the 3.5in pot, same view and scale.
A: plates drop down the assembled pole from its very top, each resting on the one below, the lowest on the post's top edge
   (the reading mossPlank_plate_pic.py drew); refilling lifts the plates out the top without unstacking.
B: each section's plate slides in from that section's own top before the next section stacks on; a section handled alone
   needs a stop at its bottom to keep its plate in (not modeled), and that stop blocks A's path down the pole.
Seated geometry is the same in both (mossPlank_plate_pic.py). Fillets left out.
Usage: python3 mossPlank_plateReading_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "mossPlank_plate_pic.py")).read().split("PL = np.array")[0])
PL = np.array([0.45, 0.62, 0.40])
postD = lower_out(0, 0, 0, zb, ZC) - lower_out(a, FRONT, SIDE, zb - 1, ZC + 1)
for sg in (1, -1):
    postD = postD - window(zlo_p, sg)
back_pot = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False); back_ins = ins.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
def base():
    R.mesh(back_pot, CLEAR); R.mesh(back_ins, INS); R.mesh(tm(postD), POST)
LA1, LA2 = 100.0, 260.0            # A: lower plate part way up the upper section's rails, upper plate above the top
LBS, LBP = 90.0, 110.0             # B: upper section held above, its plate lifted out of its own top
def bA():
    base(); R.mesh(tm(secM), UP); R.mesh(tm(hooks[0] + hooks[1]), HOOK); R.mesh(tm(secU), UP); R.mesh(tm(hooksU[0] + hooksU[1]), HOOK)
    R.mesh(tm(plM.translate([0, 0, LA1])), PL); R.mesh(tm(plU.translate([0, 0, LA2])), PL)
def bB():
    base(); R.mesh(tm(secM), UP); R.mesh(tm(hooks[0] + hooks[1]), HOOK); R.mesh(tm(plM), PL)
    R.mesh(tm(secU.translate([0, 0, LBS])), UP); R.mesh(tm((hooksU[0] + hooksU[1]).translate([0, 0, LBS])), HOOK)
    R.mesh(tm(plU.translate([0, 0, LBS + LBP])), PL)
def row(axrow, eye, pad, builders):
    frames = []
    for b in builders:
        R.FACES.clear(); b(); frames.append(R.fit(eye, pad))
    U = (min(f[0] for f in frames), max(f[1] for f in frames), min(f[2] for f in frames), max(f[3] for f in frames))
    cams = []
    for ax, b in zip(axrow, builders):
        R.FACES.clear(); b(); img, cam = R.render(eye, frame=U); ax.imshow(img); ax.axis("off"); cams.append(cam)
    return cams
fig, axs = plt.subplots(1, 2, figsize=(20, 24))
EYE = (-0.9, -1.5, 0.35)
cams = row(axs, EYE, 10, [bA, bB])
axs[0].set_title("A: plates drop down the whole assembled pole from its top\nEach plate rests on the one below, the lowest on the post's top edge.\n"
                 "Shown: upper plate (green) lifted %d mm, lower plate %d mm, part way up\nthe upper section's rails. Refill: lift the plates out the top, no unstacking." % (LA2, LA1), fontsize=13)
axs[1].set_title("B: each section's plate slides in from its own top, then the next section stacks on\n"
                 "Shown: lower plate seated; upper section held %d mm up, its plate %d mm above it.\n"
                 "Needs a stop at each section's bottom (not drawn yet), which blocks A's path.\nRefill a lower section: unstack the sections above it." % (LBS, LBP), fontsize=13)
for ax, cam in zip(axs, cams):
    R.source(ax, os.path.abspath(sys.argv[0]), cam, size=8)
fig.suptitle("mossPlank sliding hex plate: two readings of \"slides in from the top of the pole\"\n"
             "two sections on the 93 mm post, 3.5in pot (back half), from the front left; same scale; fillets left out", fontsize=16)
R.save(fig, sys.argv[2])

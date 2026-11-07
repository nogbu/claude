"""rfid spring: concept picture of the one-piece guided zigzag spring (not a build).

Writes rfidSpring_concept.png. Product doc: product.rfid (Claude/3dp/products/).

Renders a free-length view, two cutaways (free and compressed) and a section
through one fold, using a small numpy z-buffer renderer.
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly

# ---------------- concept geometry (mm), placeholders only ----------------
W = 20.0          # width (Y)
HZ = 20.0         # height (Z)
L0 = 80.0         # free length (X)
LC = 50.0         # compressed length
D = L0 - LC       # travel
EP = 3.0          # end block thickness
N = 26            # folds (placeholder)
G0 = 0.5          # smallest gap (placeholder)
WU = 1.2          # width of the bend joining two folds
DELTA = D / N
C1, C2 = 7.4, 12.6            # rail centers (Y)
RAIL_LEN = LC - 2 * EP        # rail tip meets the far block at 50 mm


def gap_side(j):
    return "R" if j % 2 == 0 else "L"


def gap_vals(j):
    gopen = G0 + (DELTA if j in (0, N) else 2 * DELTA)
    return (gopen, G0) if gap_side(j) == "R" else (G0, gopen)


TL = sum(gap_vals(j)[0] for j in range(N + 1))
T = (L0 - 2 * EP - TL) / N
FOLD_NEAR = []
_cl = _cr = EP
for _j in range(N + 1):
    _a, _b = gap_vals(_j)
    _cl += _a
    _cr += _b
    if _j < N:
        FOLD_NEAR.append((_cl, _cr))
        _cl += T
        _cr += T


def S(s):
    return 3 * s * s - 2 * s ** 3


def u_fold(k, y, comp):
    span = W - 2 * WU
    s = (y - WU) / span if gap_side(k - 1) == "L" else (W - WU - y) / span
    s = min(max(s, 0.0), 1.0)
    return comp * ((k - 1) * DELTA + DELTA * S(s))


def near_x(k, y, comp):
    xl, xr = FOLD_NEAR[k - 1]
    return xl + (xr - xl) * y / W - u_fold(k, y, comp)


def solid_intervals(y, ref):
    for c in (C1, C2):
        rm, r = abs(ref - c), abs(y - c)
        if rm < 1.0:
            return [(5.8 - r, HZ)]
        if rm <= 2.0:
            return [(0.0, r - 0.2), (5.8 - r, HZ)]
    return [(0.0, HZ)]


def strips(maxw):
    bps = {0.0, W}
    for c in (C1, C2):
        for d in (-2, -1, 0, 1, 2):
            bps.add(c + d)
    bps = sorted(bps)
    out = []
    for a, b in zip(bps[:-1], bps[1:]):
        n = max(1, int(math.ceil((b - a) / maxw - 1e-9)))
        for i in range(n):
            out.append((a + (b - a) * i / n, a + (b - a) * (i + 1) / n))
    return out


def clip_poly_z(P, zmax):
    out = []
    n = len(P)
    for i in range(n):
        A, B = P[i], P[(i + 1) % n]
        ina, inb = A[1] <= zmax + 1e-9, B[1] <= zmax + 1e-9
        if ina:
            out.append(A)
        if ina != inb:
            tt = (zmax - A[1]) / (B[1] - A[1])
            out.append((A[0] + tt * (B[0] - A[0]), zmax))
    clean = []
    for p in out:
        if not clean or abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1]) > 1e-9:
            clean.append(p)
    if len(clean) > 1 and abs(clean[0][0] - clean[-1][0]) + abs(clean[0][1] - clean[-1][1]) < 1e-9:
        clean.pop()
    return clean


def newell(F):
    n = np.zeros(3)
    m = len(F)
    for i in range(m):
        a, b = F[i], F[(i + 1) % m]
        n[0] += (a[1] - b[1]) * (a[2] + b[2])
        n[1] += (a[2] - b[2]) * (a[0] + b[0])
        n[2] += (a[0] - b[0]) * (a[1] + b[1])
    return n


FACES = []
COL_FOLD = np.array([0.82, 0.82, 0.80])
COL_A = np.array([0.27, 0.49, 0.76])   # fixed end and its rail
COL_B = np.array([0.93, 0.55, 0.18])   # moving end and its rail


def add_piece(P, x0f, x1f, color, zclip=None):
    if zclip is not None:
        P = clip_poly_z(P, zclip)
    if len(P) < 3:
        return
    V0 = np.array([(x0f(y), y, z) for y, z in P])
    V1 = np.array([(x1f(y), y, z) for y, z in P])
    cen = np.vstack([V0, V1]).mean(0)
    n = len(P)
    faces = [V0, V1] + [np.array([V0[i], V0[(i + 1) % n], V1[(i + 1) % n], V1[i]]) for i in range(n)]
    for F in faces:
        nrm = newell(F)
        ln = np.linalg.norm(nrm)
        if ln < 1e-10:
            continue
        nrm = nrm / ln
        if np.dot(nrm, F.mean(0) - cen) < 0:
            nrm = -nrm
        cut = zclip is not None and nrm[2] > 0.999 and abs(F[:, 2].mean() - zclip) < 1e-6
        FACES.append((F, nrm, color, cut))


def build(comp, zclip=None):
    FACES.clear()
    sq = [(0, 0), (W, 0), (W, HZ), (0, HZ)]
    add_piece(sq, lambda y: 0.0, lambda y: EP, COL_A, zclip)
    xb = L0 - EP - D * comp
    add_piece(sq, lambda y: xb, lambda y: xb + EP, COL_B, zclip)
    maxw = 0.8 if comp > 0 else 50.0
    for k in range(1, N + 1):
        for ya, yb in strips(maxw):
            mid = 0.5 * (ya + yb)
            for (za0, za1), (zb0, zb1) in zip(solid_intervals(ya, mid), solid_intervals(yb, mid)):
                P = [(ya, za0), (yb, zb0), (yb, zb1), (ya, za1)]
                add_piece(P, lambda y, k=k: near_x(k, y, comp),
                          lambda y, k=k: near_x(k, y, comp) + T, COL_FOLD, zclip)
    for j in range(N + 1):
        y0, y1 = (0.0, WU) if gap_side(j) == "L" else (W - WU, W)
        P = [(y0, 0), (y1, 0), (y1, HZ), (y0, HZ)]
        x0f = (lambda y: EP) if j == 0 else (lambda y, j=j: near_x(j, y, comp) + T)
        x1f = (lambda y: L0 - EP - D * comp) if j == N else (lambda y, j=j: near_x(j + 1, y, comp))
        add_piece(P, x0f, x1f, COL_FOLD, zclip)
    xbe = L0 - EP - D * comp
    for c, col, x0, x1 in ((C1, COL_A, EP, EP + RAIL_LEN), (C2, COL_B, xbe - RAIL_LEN, xbe)):
        neck = [(c - 0.6, 0), (c + 0.6, 0), (c + 0.6, 1.2), (c - 0.6, 1.2)]
        head = [(c - 0.6, 1.2), (c + 0.6, 1.2), (c + 1.6, 2.2), (c + 1.6, 3.6), (c, 5.2),
                (c - 1.6, 3.6), (c - 1.6, 2.2)]
        for P in (neck, head):
            add_piece(P, lambda y, x0=x0: x0, lambda y, x1=x1: x1, col)


def rasterize(tri, dz, c, nrm, img, zbuf, nbuf):
    x0 = int(max(0, math.floor(tri[:, 0].min())))
    x1 = int(min(img.shape[1] - 1, math.ceil(tri[:, 0].max())))
    y0 = int(max(0, math.floor(tri[:, 1].min())))
    y1 = int(min(img.shape[0] - 1, math.ceil(tri[:, 1].max())))
    if x1 < x0 or y1 < y0:
        return
    X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    (ax, ay), (bx, by), (cx, cy) = tri
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-12:
        return
    w0 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den
    w1 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den
    w2 = 1 - w0 - w1
    m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
    if not m.any():
        return
    Z = w0 * dz[0] + w1 * dz[1] + w2 * dz[2]
    sub = zbuf[y0:y1 + 1, x0:x1 + 1]
    m &= Z > sub + 1e-7
    if not m.any():
        return
    sub[m] = Z[m]
    img[y0:y1 + 1, x0:x1 + 1][m] = c
    nbuf[y0:y1 + 1, x0:x1 + 1][m] = nrm


def render(eye, ppm, light, frame=None, pad=3.0):
    e = np.asarray(eye, float)
    e /= np.linalg.norm(e)
    f = -e
    right = np.cross(f, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, f)
    if frame is None:
        allv = np.vstack([F for F, _, _, _ in FACES])
        sx, sy = allv @ right, allv @ up
        frame = (sx.min() - pad, sx.max() + pad, sy.min() - pad, sy.max() + pad)
    xmin, xmax, ymin, ymax = frame
    Wp, Hp = int(math.ceil((xmax - xmin) * ppm)), int(math.ceil((ymax - ymin) * ppm))
    img = np.ones((Hp, Wp, 3))
    zbuf = np.full((Hp, Wp), -np.inf)
    nbuf = np.zeros((Hp, Wp, 3))
    Lt = np.asarray(light, float)
    Lt /= np.linalg.norm(Lt)
    for F, nrm, col, cut in FACES:
        if np.dot(nrm, e) <= 1e-9:
            continue
        shade = 0.45 + 0.40 * max(0.0, float(nrm @ Lt)) + 0.25 * max(0.0, float(nrm @ e))
        c = np.clip(col * shade, 0, 1)
        if cut:
            c = np.clip(col * 0.45 + 0.52, 0, 1)
        P2 = np.stack([(F @ right - xmin) * ppm, (ymax - F @ up) * ppm], 1)
        dep = F @ e
        for i in range(1, len(F) - 1):
            idx = [0, i, i + 1]
            rasterize(P2[idx], dep[idx], c, nrm, img, zbuf, nbuf)
    # outlines
    fg = np.isfinite(zbuf)
    E = np.zeros(fg.shape, bool)
    thr = 0.45
    for dy, dx in ((0, 1), (1, 0)):
        a = (slice(0, Hp - dy), slice(0, Wp - dx))
        b = (slice(dy, Hp), slice(dx, Wp))
        both = fg[a] & fg[b]
        dz = np.where(both, zbuf[a] - np.where(both, zbuf[b], 0), 0)
        dot = (nbuf[a] * nbuf[b]).sum(-1)
        ed = (fg[a] != fg[b]) | (both & ((np.abs(dz) > thr) | (dot < 0.93)))
        E[a] |= ed
        E[b] |= ed
    img[E] = img[E] * 0.22
    # 2x downsample
    H2, W2 = Hp // 2, Wp // 2
    small = img[:H2 * 2, :W2 * 2].reshape(H2, 2, W2, 2, 3).mean((1, 3))
    cam = dict(right=right, up=up, xmin=xmin, ymax=ymax, ppm=ppm / 2.0, frame=frame)
    return small, cam


def proj(cam, p):
    p = np.asarray(p, float)
    return ((p @ cam["right"] - cam["xmin"]) * cam["ppm"], (cam["ymax"] - p @ cam["up"]) * cam["ppm"])


def frame_for(eye, pad=3.0):
    """Common frame using the free-length full part so panels share a scale."""
    e = np.asarray(eye, float)
    e /= np.linalg.norm(e)
    right = np.cross(-e, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, -e)
    box = np.array([[x, y, z] for x in (0, L0) for y in (0, W) for z in (0, HZ)])
    sx, sy = box @ right, box @ up
    return (sx.min() - pad, sx.max() + pad, sy.min() - pad, sy.max() + pad)


# ---------------- figure ----------------
PPM = 26.0
EYE_TOP = (0.22, -0.55, 1.5)
EYE_CUT = (0.18, -0.55, 1.6)
LIGHT = (0.35, -0.25, 1.0)

build(0.0)
img1, cam1 = render(EYE_TOP, PPM, LIGHT, frame_for(EYE_TOP))
ZCUT = 7.5
build(0.0, zclip=ZCUT)
fr = frame_for(EYE_CUT)
img2, cam2 = render(EYE_CUT, PPM, LIGHT, fr)
build(1.0, zclip=ZCUT)
img3, cam3 = render(EYE_CUT, PPM, LIGHT, fr)

fig = plt.figure(figsize=(16, 11.2), dpi=150)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(2, 2, left=0.02, right=0.98, top=0.90, bottom=0.07, wspace=0.06, hspace=0.16,
                      width_ratios=[1.35, 1.0])
fig.suptitle("Spring concept: 80 mm free, 50 mm compressed, 20 × 20 mm, one piece in PETG",
             fontsize=17, fontweight="bold", y=0.975)
fig.text(0.5, 0.93, "Concept only: fold count, thickness and gaps are placeholders until the load and safety factor are set. "
         "Colors only show which end each rail belongs to; it all prints as one piece.",
         ha="center", fontsize=10.5, color="#444")

ARW = dict(arrowstyle="-|>", color="#222", lw=1.2, shrinkA=0, shrinkB=2)
BOX = dict(boxstyle="round,pad=0.3", fc="white", ec="#888", lw=0.8)


def label(ax, cam, p3, text, dxy, **kw):
    x, y = proj(cam, p3)
    ax.annotate(text, xy=(x, y), xytext=(x + dxy[0], y + dxy[1]), fontsize=11, arrowprops=ARW,
                bbox=BOX, ha="center", va="center", **kw)


# Panel 1: full part at free length
ax1 = fig.add_subplot(gs[0, 0])
ax1.imshow(img1)
ax1.set_title("At rest: 80 mm", fontsize=13.5, loc="left")
label(ax1, cam1, (1.5, 0, HZ), "fixed end", (-40, -110))
label(ax1, cam1, (78.5, 0, HZ), "moving end", (40, -110))
xm = FOLD_NEAR[12][0]
label(ax1, cam1, (xm, 0.6, HZ), "zigzag folds\n(each bends ~1 mm)", (-60, -150))
pa, pb = proj(cam1, (0, -1.5, 0)), proj(cam1, (L0, -1.5, 0))
ax1.annotate("", xy=pa, xytext=pb, arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
ax1.text((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2 + 26, "80 mm", color="#c0392b", fontsize=12,
         ha="center", va="center", fontweight="bold")
pc, pd = proj(cam1, (L0 + 1.5, 0, 0)), proj(cam1, (L0 + 1.5, W, 0))
ax1.annotate("", xy=pc, xytext=pd, arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
ax1.text((pc[0] + pd[0]) / 2 + 58, (pc[1] + pd[1]) / 2 + 8, "20 mm", color="#c0392b", fontsize=12,
         ha="center", va="center", fontweight="bold")
pe, pf = proj(cam1, (0, -1.5, 0)), proj(cam1, (0, -1.5, HZ))
ax1.annotate("", xy=pe, xytext=pf, arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
ax1.text(pe[0] - 62, (pe[1] + pf[1]) / 2, "20 mm", color="#c0392b", fontsize=12,
         ha="center", va="center", fontweight="bold")
ax1.axis("off")

# Panel 2: section through one fold
ax4 = fig.add_subplot(gs[0, 1])
ax4.set_title("Cut through one fold", fontsize=13.5, loc="left")
ax4.add_patch(MPoly([(0, 0), (W, 0), (W, HZ), (0, HZ)], closed=True, fc="#d8d8d4", ec="#333", lw=1.2))
for c in (C1, C2):
    notch = [(c - 1.0, 0), (c - 1.0, 0.8), (c - 2.0, 1.8), (c - 2.0, 3.8), (c, 5.8), (c + 2.0, 3.8),
             (c + 2.0, 1.8), (c + 1.0, 0.8), (c + 1.0, 0)]
    ax4.add_patch(MPoly(notch, closed=True, fc="white", ec="#333", lw=1.0))
for c, col in ((C1, COL_A), (C2, COL_B)):
    rail = [(c - 0.6, 0), (c + 0.6, 0), (c + 0.6, 1.2), (c + 1.6, 2.2), (c + 1.6, 3.6), (c, 5.2),
            (c - 1.6, 3.6), (c - 1.6, 2.2), (c - 0.6, 1.2)]
    ax4.add_patch(MPoly(rail, closed=True, fc=col, ec="#222", lw=1.0))
ax4.set_xlim(-11, 31)
ax4.set_ylim(-4.5, 22)
ax4.set_aspect("equal")
ax4.axis("off")
kw = dict(fontsize=11, bbox=BOX, ha="center", va="center", arrowprops=ARW)
ax4.annotate("fold, 20 mm tall\n(cut face)", xy=(4, 14), xytext=(-5.5, 17.5), **kw)
ax4.annotate("rail from\nfixed end", xy=(C1 - 0.9, 3.0), xytext=(-5.5, 5.5), **kw)
ax4.annotate("rail from\nmoving end", xy=(C2 + 0.9, 3.0), xytext=(25.5, 5.5), **kw)
ax4.annotate("fold hooks under each rail head\nand roofs over it, so the folds\ncan't move sideways, up or down",
             xy=(C2, 5.9), xytext=(22.5, 13.5), **kw)
ax4.annotate("45° faces: no supports", xy=(C1 + 1.0, 4.85), xytext=(10, -2.7), **kw)
ax4.plot([-0.5, W + 0.5], [0, 0], color="#888", lw=0.8, ls="--")

# Panel 3: cutaway at free length
ax2 = fig.add_subplot(gs[1, 0])
ax2.imshow(img2)
ax2.set_title("Folds cut away to show the guide: a rail from each end runs through a notch in every fold",
              fontsize=13.5, loc="left")
label(ax2, cam2, (EP + RAIL_LEN * 0.35, C1, 4.0), "rail from fixed end", (-120, -95))
label(ax2, cam2, (L0 - EP - RAIL_LEN * 0.30, C2, 4.0), "rail from moving end", (60, -120))
label(ax2, cam2, (FOLD_NEAR[17][0], 0.0, 3.0), "notch in each fold", (40, 95))
ax2.axis("off")

# Panel 4: cutaway compressed
ax3 = fig.add_subplot(gs[1, 1])
ax3.imshow(img3)
ax3.set_title("Compressed: 50 mm", fontsize=13.5, loc="left")
label(ax3, cam3, (EP + RAIL_LEN, C1, 4.6), "rail tips hit the far ends:\nbuilt-in stop at 50 mm", (40, -150))
qa, qb = proj(cam3, (0, -1.5, 0)), proj(cam3, (LC, -1.5, 0))
ax3.annotate("", xy=qa, xytext=qb, arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
ax3.text((qa[0] + qb[0]) / 2, (qa[1] + qb[1]) / 2 + 24, "50 mm", color="#c0392b", fontsize=12,
         ha="center", va="center", fontweight="bold")
ax3.set_xlim(0, img3.shape[1] * 0.72)
ax3.set_ylim(img3.shape[0], 0)
ax3.axis("off")

fig.savefig("rfidSpring_concept.png", dpi=150, facecolor="white")
print("saved", T, len(FACES))

"""3dp concept renderer: shaded solids with dark outlines on white, the style of every 3dp concept picture.

One vectorized numpy z-buffer (no per-triangle Python loop), 2x supersampled, then averaged down.
It replaces calibration-stand's renderlib.py (now a shim onto this file); rfid's rfidSpring_concept.py
keeps its own early copy as history. Needs numpy; the mesh and extrude helpers also need trimesh and shapely.

  import sys; sys.path.insert(0, "[repo]/projects/3dp/scripts")
  import render3d as R
  R.FACES.clear(); R.box(0, 10, 0, 10, 0, 5, R.BONE); R.extrude(poly, "z", 0, 12, R.BONE)
  img, cam = R.render(eye=(-1, -1.6, 0.8), ppm=2.4)    # ppm: supersampled pixels per mm
  ax.imshow(img); x, y = R.proj(cam, (10, 0, 5))      # 3D point -> image pixel, for labels
  R.load("part_rev3.3mf"); cam = R.view(ax); R.source(ax, "part_rev3.3mf", cam)   # true to the built model
  R.label(ax, x, y, "rim")                            # dark text on a white box; layout_check flags one over the part
  R.save(fig, "out.png")                              # keeps every rendered pixel (dpi set from the image)

FACES holds (polygon vertices (k,3), outward normal, RGB color, cut) per face; cut faces
(section cuts) are drawn flat and pale.
"""
import math
import sys
import numpy as np

FACES = []
BONE = np.array([0.86, 0.84, 0.78])
MIN_PX = 1400        # every image is at least this many pixels on its long side (render raises ppm to reach it)
CHUNK = 3_000_000  # fragments per pass: bounds memory at about 250 MB


def newell(F):
    """Unnormalized normal of a planar polygon (k,3), counter-clockwise seen from outside."""
    F = np.asarray(F, float)
    G = np.roll(F, -1, 0)
    return np.array([((F[:, 1] - G[:, 1]) * (F[:, 2] + G[:, 2])).sum(),
                     ((F[:, 2] - G[:, 2]) * (F[:, 0] + G[:, 0])).sum(),
                     ((F[:, 0] - G[:, 0]) * (F[:, 1] + G[:, 1])).sum()])


def add(F, col, cut=False, nrm=None):
    """Add one planar polygon face."""
    F = np.asarray(F, float)
    n = newell(F) if nrm is None else np.asarray(nrm, float)
    FACES.append((F, n / (np.linalg.norm(n) or 1.0), np.asarray(col, float), cut))


def box(x0, x1, y0, y1, z0, z1, col):
    """Axis-aligned box."""
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    for F in (((x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)), ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)),
              ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)), ((x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)),
              ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)), ((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1))):
        add(F, col)


def mesh(m, col, cut=False):
    """Add a trimesh mesh's triangles in one step."""
    V = m.vertices[m.faces]
    FACES.extend((f, n, np.asarray(col, float), cut) for f, n in zip(V, m.face_normals))


def extrude(poly, axis, a0, a1, col, offset=(0, 0, 0)):
    """Extrude a shapely (Multi)Polygon between a0 and a1 along axis "x", "y" or "z".
    The polygon's (u, v) map to (x, y) for "z", (x, z) for "y" and (y, z) for "x"."""
    import trimesh
    for p in getattr(poly, "geoms", [poly]):
        if p.is_empty:
            continue
        m = trimesh.creation.extrude_polygon(p, a1 - a0, engine="earcut")
        u, v, w = m.vertices.T
        w = w + a0
        m.vertices = {"z": np.c_[u, v, w], "y": np.c_[u, w, v], "x": np.c_[w, u, v]}[axis] + offset
        m.fix_normals()
        mesh(m, col)


def camera(eye):
    e = np.asarray(eye, float); e = e / np.linalg.norm(e)
    right = np.cross(-e, [0, 0, 1.0]); right /= np.linalg.norm(right)
    return e, right, np.cross(right, -e)


def fit(eye, pad=3.0, faces=None):
    """Frame (xmin, xmax, ymin, ymax) in mm that holds every face seen from eye, plus pad."""
    _, right, up = camera(eye)
    V = np.vstack([F for F, *_ in (faces or FACES)])
    sx, sy = V @ right, V @ up
    return sx.min() - pad, sx.max() + pad, sy.min() - pad, sy.max() + pad


def _triangles(e, Lt):
    """Fan-triangulate the faces that look toward the eye; return vertices (n,3,3), shaded colors, normals."""
    if not FACES:
        return np.zeros((0, 3, 3)), np.zeros((0, 3)), np.zeros((0, 3))
    nrm = np.array([f[1] for f in FACES]); col = np.array([f[2] for f in FACES]); cut = np.array([f[3] for f in FACES])
    seen = np.nonzero(nrm @ e > 1e-9)[0]
    shade = 0.45 + 0.40 * np.maximum(0, nrm @ Lt) + 0.25 * np.maximum(0, nrm @ e)
    c = np.clip(np.where(cut[:, None], col * 0.45 + 0.52, col * shade[:, None]), 0, 1)
    tris, src = [], []
    k3 = np.array([len(FACES[i][0]) == 3 for i in seen], bool)   # triangles (loaded meshes) stack in one step
    if k3.any():
        s3 = seen[k3]; tris.append(np.stack([FACES[i][0] for i in s3])); src.append(s3)
    for i in seen[~k3]:
        F = FACES[i][0]
        k = len(F) - 2
        j = np.arange(1, k + 1)
        tris.append(np.stack([np.repeat(F[:1], k, 0), F[j], F[j + 1]], 1)); src.append(np.full(k, i))
    if not tris:
        return np.zeros((0, 3, 3)), np.zeros((0, 3)), np.zeros((0, 3))
    src = np.concatenate(src)
    return np.concatenate(tris), c[src], nrm[src]


def _rasterize(P, D, H, W):
    """Nearest triangle per pixel center, by scanline spans (only covered pixels become fragments).
    P (n,3,2) pixel coordinates, D (n,3) depth toward the eye. Returns the triangle id per pixel
    (-1 for background) and the depth buffer. On equal depth the earlier triangle wins."""
    zbuf = np.full(H * W, -np.inf)
    ids = np.full(H * W, -1, np.int64)
    X, Y = P[..., 0], P[..., 1]
    den = (Y[:, 1] - Y[:, 2]) * (X[:, 0] - X[:, 2]) + (X[:, 2] - X[:, 1]) * (Y[:, 0] - Y[:, 2])
    r0 = np.maximum(np.ceil(Y.min(1) - 0.5 - 1e-6), 0).astype(np.int64)
    r1 = np.minimum(np.floor(Y.max(1) - 0.5 + 1e-6), H - 1).astype(np.int64)
    ok = (np.abs(den) >= 1e-12) & (r1 >= r0) & (X.max(1) >= 0) & (X.min(1) <= W)
    tri = np.nonzero(ok)[0]
    if not len(tri):
        return ids, zbuf
    # depth plane z = gx*x + gy*y + g0 per triangle
    M = np.concatenate([P[tri], np.ones((len(tri), 3, 1))], 2)
    G = np.linalg.solve(M, D[tri][..., None])[..., 0]
    rows = r1[tri] - r0[tri] + 1
    ends = np.cumsum(rows)
    start = 0
    while start < len(tri):
        # chunk by rows; spans are expanded to pixels below
        stop = max(start + 1, int(np.searchsorted(ends, (ends[start - 1] if start else 0) + CHUNK // 64, "right")))
        ti, rc = np.arange(start, stop), rows[start:stop]
        k = np.repeat(ti, rc)                                  # index into tri
        y = r0[tri[k]] + np.arange(rc.sum()) - np.repeat(np.cumsum(rc) - rc, rc)
        yc = y + 0.5
        Xk, Yk = X[tri[k]], Y[tri[k]]
        lo = np.full(len(k), np.inf); hi = np.full(len(k), -np.inf)
        for i, j in ((0, 1), (1, 2), (2, 0)):
            ya, yb, xa, xb = Yk[:, i], Yk[:, j], Xk[:, i], Xk[:, j]
            cross = ((yc - ya) * (yc - yb) <= 0) & (ya != yb)
            with np.errstate(divide="ignore", invalid="ignore"):
                x = xa + (yc - ya) * (xb - xa) / (yb - ya)
            lo = np.where(cross, np.minimum(lo, x), lo); hi = np.where(cross, np.maximum(hi, x), hi)
        c0 = np.maximum(np.ceil(lo - 0.5 - 1e-6), 0)
        c1 = np.minimum(np.floor(hi - 0.5 + 1e-6), W - 1)
        n = np.where(np.isfinite(c0) & np.isfinite(c1) & (c1 >= c0), c1 - c0 + 1, 0).astype(np.int64)
        f = np.repeat(np.arange(len(k)), n)
        x = c0[f].astype(np.int64) + np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
        yy = y[f]; t = tri[k[f]]; g = G[k[f]]
        z = g[:, 0] * (x + 0.5) + g[:, 1] * (yy + 0.5) + g[:, 2]
        pid = yy * W + x
        u, inv = np.unique(pid, return_inverse=True)        # only the pixels this chunk touches
        zm = zbuf[u].copy(); np.maximum.at(zm, inv, z)
        win = (z >= zm[inv]) & (z > zbuf[pid] + 1e-7)
        best = np.full(len(u), np.iinfo(np.int64).max)
        np.minimum.at(best, inv[win], t[win])
        k = best != np.iinfo(np.int64).max
        zbuf[u[k]] = zm[k]; ids[u[k]] = best[k]
        start = stop
    return ids, zbuf


def render(eye, ppm=None, light=(0.3, -0.7, 1.0), frame=None, pad=3.0, edge_depth=5.0, ss=2, edge_px=1):
    """Render FACES seen from direction eye. ppm is supersampled pixels per mm (the image has ppm / ss);
    it is raised, never lowered, so the image is at least MIN_PX on its long side.
    frame (xmin, xmax, ymin, ymax) in mm, or None to fit with pad. edge_depth (mm) is the depth jump
    drawn as an outline; use about 0.5 for small parts. ss is the supersampling factor and edge_px the
    outline width in image pixels (picture.py draws at 3x with wider outlines). Returns (RGB image, cam for proj)."""
    e, right, up = camera(eye)
    frame = fit(eye, pad) if frame is None else frame
    xmin, xmax, ymin, ymax = frame
    ppm = max(ppm or 0.0, ss * MIN_PX / max(xmax - xmin, ymax - ymin))
    Wp, Hp = int(math.ceil((xmax - xmin) * ppm)), int(math.ceil((ymax - ymin) * ppm))
    Lt = np.asarray(light, float); Lt = Lt / np.linalg.norm(Lt)
    T, C, N = _triangles(e, Lt)
    P = np.stack([(T @ right - xmin) * ppm, (ymax - T @ up) * ppm], -1)
    ids, zbuf = _rasterize(P, T @ e, Hp, Wp)
    ids, zbuf = ids.reshape(Hp, Wp), zbuf.reshape(Hp, Wp)
    fg = ids >= 0
    C, N = C.astype(np.float32), N.astype(np.float32)
    img = np.ones((Hp, Wp, 3), np.float32); img[fg] = C[ids[fg]]
    nbuf = np.zeros((Hp, Wp, 3), np.float32); nbuf[fg] = N[ids[fg]]
    # outlines: silhouettes, depth jumps and creases
    E = np.zeros((Hp, Wp), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = (slice(0, Hp - dy), slice(0, Wp - dx)); b = (slice(dy, Hp), slice(dx, Wp))
        both = fg[a] & fg[b]
        dz = np.where(both, zbuf[a] - np.where(both, zbuf[b], 0), 0)
        ed = (fg[a] != fg[b]) | (both & ((np.abs(dz) > edge_depth) | ((nbuf[a] * nbuf[b]).sum(-1) < 0.93)))
        E[a] |= ed; E[b] |= ed
    for _ in range(max(0, int(round((edge_px * ss - 2) / 2)))):   # each edge marks 2 supersampled pixels; widen to edge_px
        D = E.copy(); D[1:] |= E[:-1]; D[:-1] |= E[1:]; D[:, 1:] |= E[:, :-1]; D[:, :-1] |= E[:, 1:]; E = D
    img[E] *= 0.22
    H2, W2 = Hp // ss, Wp // ss
    small = img[:H2 * ss, :W2 * ss].reshape(H2, ss, W2, ss, 3).mean((1, 3))
    return small, dict(right=right, up=up, xmin=xmin, ymax=ymax, ppm=ppm / ss, frame=frame)


def proj(cam, p):
    """Image pixel (x, y) of 3D point(s) p in a picture render returned cam for."""
    p = np.asarray(p, float)
    return ((p @ cam["right"] - cam["xmin"]) * cam["ppm"], (cam["ymax"] - p @ cam["up"]) * cam["ppm"])


def view(ax, eye=(-1.0, -1.6, 0.8), ppm=None, pad=10.0, title=None, **kw):
    """Render FACES into a matplotlib axis, fitted with pad mm, and return cam."""
    img, cam = render(eye, ppm, frame=fit(eye, pad), **kw)
    ax.imshow(img); ax.axis("off")
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold")
    return cam


def place(ax, img, W, H):
    """Show img in ax inside a W x H pixel frame, so option panels share one scale: set MIN_PX = 0, render every panel
    with render(eye, ppm, frame=fit(eye, pad)) at one ppm, then place each with the largest W, H (proj stays valid)."""
    h, w = img.shape[:2]
    ax.imshow(img, extent=[0, w, h, 0]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")


def row(axes, eye, builders, pad=3.0):
    """Draw each builder's scene (a function that adds faces) in its axes with one shared frame and scale: option panels
    and step-by-step panels, with no anchor box. Fits each scene, renders all in the union of the frames; returns the cams.
    From mossPlank_jointFix_pic.py's row() (2026-10-11)."""
    frames = []
    for b in builders:
        FACES.clear(); b(); frames.append(fit(eye, pad))
    U = (min(f[0] for f in frames), max(f[1] for f in frames), min(f[2] for f in frames), max(f[3] for f in frames))
    cams = []
    for ax, b in zip(axes, builders):
        FACES.clear(); b(); img, cam = render(eye, frame=U); ax.imshow(img); ax.axis("off"); cams.append(cam)
    return cams


def layout_check(fig):
    """Flag text cut off by the figure edge, text that overlaps other text, a panel's text drawn over another panel, a label that
    runs out of its own picture panel (an axes holding an image; its titles and source() caption excepted), and a label covering
    the part in a render (over 20% of its box on non-white pixels of an image with a white border; dim() labels and text with
    gid="onpart" excepted, and photos, which have no white border); each text is measured with its label box when it has one.
    Returns the problems (empty when clean)."""
    import matplotlib.text
    def ext(t):   # the label box when drawn, else the text alone (an annotation's leader line is never counted)
        bp = t.get_bbox_patch()
        return bp.get_window_extent(r) if bp is not None and bp.get_visible() else matplotlib.text.Text.get_window_extent(t, r)
    fig.canvas.draw(); r = fig.canvas.get_renderer(); W, H = fig.canvas.get_width_height()
    skip = set()
    for ax in fig.axes:   # tick labels of hidden axes, or outside the shown range, aren't drawn
        for lab, lim, ticks in ((ax.get_xticklabels(), ax.get_xlim(), ax.get_xticks()), (ax.get_yticklabels(), ax.get_ylim(), ax.get_yticks())):
            lo, hi = min(lim), max(lim)
            for t, v in zip(lab, ticks):
                if not ax.axison or not (lo - 1e-9 <= v <= hi + 1e-9): skip.add(id(t))
    boxes, bad = [], []
    for t in fig.findobj(matplotlib.text.Text):   # legends hold TextArea boxes, which wrap Text objects found here anyway
        txt = str(t.get_text()).strip()
        if id(t) in skip or not t.get_visible() or not txt: continue
        bb = ext(t); name = txt[:40].replace("\n", " ")
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > W + 1 or bb.y1 > H + 1: bad.append(f"cut off: '{name}'")
        ax = t.axes
        if ax is not None and ax.get_images() and t not in (ax.title, ax._left_title, ax._right_title) and t.get_gid() != "source":
            pb = ax.get_window_extent(r)
            if bb.x0 < pb.x0 - 2 or bb.y0 < pb.y0 - 2 or bb.x1 > pb.x1 + 2 or bb.y1 > pb.y1 + 2: bad.append(f"outside its panel: '{name}'")
            elif t.get_gid() not in ("dim", "onpart") and _on_part(ax, bb) > 0.2: bad.append(f"over the part: '{name}'")
        boxes.append((bb, name))
    panels = [(ax, ax.get_window_extent(r)) for ax in fig.axes if ax.get_visible()]
    for t in fig.findobj(matplotlib.text.Text):   # a panel's label drawn over a neighboring panel
        own = t.axes
        if own is None or id(t) in skip or not t.get_visible() or not str(t.get_text()).strip(): continue
        bb = ext(t)
        for ax, pb in panels:
            if ax is not own and min(bb.x1, pb.x1) - max(bb.x0, pb.x0) > 2 and min(bb.y1, pb.y1) - max(bb.y0, pb.y0) > 2:
                bad.append(f"crosses into another panel: '{str(t.get_text()).strip()[:40]}'"); break
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][0], boxes[j][0]
            if min(a.x1, b.x1) - max(a.x0, b.x0) > 2 and min(a.y1, b.y1) - max(a.y0, b.y0) > 2:
                bad.append(f"overlap: '{boxes[i][1]}' / '{boxes[j][1]}'")
    return bad


def _on_part(ax, bb):
    """Share of display box bb lying on non-white pixels of ax's last image, when that image is a render (white border)."""
    im = ax.get_images()[-1]; A = np.asarray(im.get_array(), float)
    if A.ndim != 3: return 0.0
    A = A[..., :3] / (255.0 if A.max() > 1.0 else 1.0); h, w = A.shape[:2]
    edge = np.concatenate([A[0], A[-1], A[:, 0], A[:, -1]])
    if (edge.min(1) > 0.97).mean() < 0.9: return 0.0          # a photo or a cropped render: no background to measure against
    l, r_, b, t = im.get_extent()
    inv = ax.transData.inverted()
    (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
    cols = sorted(int(np.clip((v - l) / (r_ - l) * w, 0, w)) for v in (x0, x1))
    rows = sorted(int(np.clip((v - t) / (b - t) * h, 0, h)) for v in (y0, y1))
    P = A[rows[0]:rows[1], cols[0]:cols[1]]
    return float((P.min(2) < 0.9).mean()) if P.size else 0.0


def label(ax, x, y, text, size=11, **kw):
    """A label as dark text on a white box, the default on photos and renders (light or colored text on a photo didn't read)."""
    kw.setdefault("bbox", dict(boxstyle="round,pad=0.25", fc="white", ec="#888", lw=0.6, alpha=0.95))
    return ax.text(x, y, text, fontsize=size, color=kw.pop("color", "#222"), ha=kw.pop("ha", "center"), va=kw.pop("va", "center"), **kw)


def save(fig, path, **kw):
    """Save a figure at a dpi high enough that no rendered image in it is shrunk (150 dpi at least).
    Prints LAYOUT OK, or LAYOUT FLAG with each cut-off or overlapping text; look at the picture again only when flagged."""
    bad = layout_check(fig)
    print("LAYOUT OK (no need to look at the picture again)" if not bad else
          "LAYOUT FLAG (" + path.rsplit("/", 1)[-1] + "): look at the picture and fix these\n  " + "\n  ".join(bad))
    dpi = 150.0
    for ax in fig.axes:
        box = ax.get_window_extent()
        w_in, h_in = box.width / fig.dpi, box.height / fig.dpi
        for im in ax.get_images():
            h, w = im.get_array().shape[:2]
            if w_in > 0 and h_in > 0:   # the image is shown at the smaller of the two fits
                dpi = max(dpi, max(w / w_in, h / h_in))
    fig.savefig(path, dpi=min(dpi, 600), facecolor="white", **kw)


def load(path, col=BONE, colors=None):
    """Add a built model's own meshes (3mf in its plate placement, or STL) to FACES, so the picture is the model.
    colors maps an object name to a color. Returns [(name, min corner, max corner)] per object."""
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dpcheck import load_3mf, load_stl
    items, _ = load_3mf(path) if path.lower().endswith(".3mf") else load_stl(path)
    out = []
    for it in items:
        name = it["over"].get("name", it["name"])
        c = np.asarray((colors or {}).get(name, col), float)
        V, T = it["V"], it["T"]
        tri = V[T]
        N = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n = np.linalg.norm(N, axis=1); k = n > 1e-12
        FACES.extend((f, nn, c, False) for f, nn in zip(tri[k], N[k] / n[k, None]))
        out.append((name, V.min(0), V.max(0)))
    return out


def source(ax, path, cam=None, size=9):
    """Caption naming the file the picture was drawn from, its content hash and the pixel size, under the panel
    (gid "source": layout_check lets it out of its panel)."""
    import hashlib, os
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:8]
    px = f", 1 px = {1 / cam['ppm']:.2f} mm" if cam else ""
    ax.text(0.0, -0.02, f"Drawn from {os.path.basename(path)} ({h}){px}", transform=ax.transAxes,
            fontsize=size, color="#555", va="top", gid="source")


def dim(ax, cam, a, b, off, text=None, color="#c0392b"):
    """Dimension line between 3D points a and b, drawn offset by the 3D vector off.
    With no text, the label is the measured distance between a and b, so it can't disagree with the model."""
    a, b, off = (np.asarray(v, float) for v in (a, b, off))
    if text is None:
        text = f"{np.linalg.norm(b - a):.2f}".rstrip("0").rstrip(".")
    A2, B2, A3, B3 = (np.array(proj(cam, p)) for p in (a, b, a + off, b + off))
    for p, q in ((A2, A3), (B2, B3)):
        ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=0.7, ls=(0, (3, 2)))
    ax.annotate("", xy=B3, xytext=A3, arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.2, shrinkA=0, shrinkB=0))
    m = (A3 + B3) / 2
    ax.text(m[0], m[1], text, color=color, fontsize=10, fontweight="bold", ha="center", va="center", gid="dim",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))


def call(ax, cam, p, off, text, color="#1f5fa8", size=12):
    """Callout: text offset by off (points) with a leader line to 3D point p."""
    ax.annotate(text, xy=proj(cam, p), xytext=off, textcoords="offset points", fontsize=size, fontweight="bold",
                color=color, ha="center", arrowprops=dict(arrowstyle="-", color=color), bbox=dict(fc="white", ec="none", alpha=.9))

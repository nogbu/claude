"""Roof-root corner, 2D models of the wire-channel section (inference throughout).
 - sec():    channel section for the 'bigger root' family: wall moved forward (a = gap in front of the wire end),
             roof raised (b = gap above the wire top), root = fillet r / 45-deg chamfer c with blend fillets rb / ellipse.
 - plane strain (unit line load 1 N/mm, bottom face clamped)
 - Fourier prism: infinite prism, patch load 0.6 long in x (as fe_wedge.roof_load), sigma(x=0) by a wavenumber integral
   over 2D solves of u_x sin(kx), u_y, u_z cos(kx).  Catches the x-spreading that plane strain can't.
Meshes from fe_wedge.mesh2d (same generator as the 3D runs); peaks measured like arc_peak.py:
across = max sigma_yy on the root surface band, along = max sigma_zz on the root band + 1.0 of wall face below it."""
import sys, os, time, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl, shapely, shapely.affinity
from shapely.geometry import box as B, Point, Polygon, LineString
STRUCT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, STRUCT)
import fe_wedge as W
ROD = 2.95; BORE = 3.1; WB = 2.8; TOP = 5.7; FLOOR = 2.5; WEND = -2.95
E, NU = 1900.0, 0.38
Q = (WEND, TOP)                                   # wire's swept front-top corner

def corner_fill(kind, FRONT, zR, r=0.6, c=0.0, rb=0.0, ry=0.0, rz=0.0, res=256):
    """Material added in the inside corner (FRONT, zR). kind: 'none', 'fillet' (r), 'chamfer' (45-deg leg c, blend rb),
    'ellipse' (quarter-ellipse semi-axes ry along the roof, rz down the wall)."""
    if kind == "none": return Polygon()
    if kind == "fillet":
        return B(FRONT, zR - r, FRONT + r, zR).difference(Point(FRONT + r, zR - r).buffer(r, res))
    if kind == "ellipse":
        ell = shapely.affinity.translate(shapely.affinity.scale(Point(0, 0).buffer(1.0, res), ry, rz), FRONT + ry, zR - rz)
        return B(FRONT, zR - rz, FRONT + ry, zR).difference(ell)
    if kind == "chamfer":
        tri = Polygon([(FRONT, zR), (FRONT, zR - c), (FRONT + c, zR)])
        if rb <= 0: return tri
        L = 4.0
        local = B(FRONT - L, zR - L, FRONT, zR + L).union(B(FRONT - L, zR, FRONT + L, zR + L)).union(tri)
        closed = local.buffer(rb, quad_segs=res // 4, join_style="round").buffer(-rb, quad_segs=res // 4, join_style="round")
        return closed.intersection(B(FRONT, zR - L / 2, FRONT + L / 2, zR)).buffer(0)
    raise ValueError(kind)

def sec(a=0.6, b=0.3, kind="fillet", fw=2.4, tr=2.35, tz=2.48, ov=2.0, roof=3.10, rf=0.0, **kw):
    """Returns dict: s (section polygon), OF, OR, OZ, RT, FRONT, zR, fill, root (LineString of the exposed root surface)."""
    FRONT = WEND - a; zR = TOP + b; OF = fw - FRONT; OR = BORE + tr; OZ = BORE + tz; RT = WEND + ov
    s = B(-OF, -OZ, OR, TOP).union(B(-OF, TOP, RT, zR + roof)).difference(B(FRONT, FLOOR, OR + 1, zR))
    fill = corner_fill(kind, FRONT, zR, **kw)
    if not fill.is_empty: s = s.union(fill)
    if rf > 0:                                    # floor fillet in the channel's lower inside corner (FRONT, FLOOR)
        s = s.union(B(FRONT, FLOOR, FRONT + rf, FLOOR + rf).difference(Point(FRONT + rf, FLOOR + rf).buffer(rf, 720)))
    s = s.difference(Point(0, 0).buffer(BORE, 720)).simplify(0.0005)
    if not fill.is_empty:
        flats = LineString([(FRONT, FLOOR), (FRONT, zR), (RT + 1, zR)]).buffer(1e-6)
        root = fill.exterior.difference(flats)
        root = shapely.line_merge(root) if root.geom_type == "MultiLineString" else root
    else:
        root = Point(FRONT, zR).buffer(0.02).exterior
    return dict(s=s, OF=OF, OR=OR, OZ=OZ, RT=RT, FRONT=FRONT, zR=zR, fill=fill, root=root, a=a, b=b, roof=roof, kind=kind, kw=kw)

def clearances(d):
    """Clearance of the root fill (and of the whole roof/wall) to the wire's swept rectangle y >= -2.95, z 2.8..5.7 (+0.2 oversize)."""
    rect = B(WEND, WB, WEND + 20, TOP); rect2 = B(WEND, WB, WEND + 20, TOP + 0.2)
    f = d["fill"]
    cf = f.distance(rect) if not f.is_empty else np.inf
    cq = f.distance(Point(Q)) if not f.is_empty else np.inf
    cf2 = f.distance(rect2) if not f.is_empty else np.inf
    # vertical gap at the wire end (y -2.95) from the fill / roof underside
    line = LineString([(WEND, TOP), (WEND, d["zR"] + 1)])
    hit = d["s"].intersection(line)
    zg = min([p[1] for g in getattr(hit, "geoms", [hit]) for p in g.coords]) if not hit.is_empty else d["zR"]
    return dict(fill_to_wire=cf, fill_to_corner=cq, fill_to_oversize=cf2, bearing_gap=d["b"], vgap_at_end=zg - TOP)

def mesh(d, h0=0.02, hzone=0.12, focus="root"):
    """focus 'wmodel': as fe_wedge.WModel (circle r0.45 at FRONT+0.3, zR-0.3); 'root': that plus a 0.45 band on the root surface."""
    wf = Point(d["FRONT"] + 0.3, d["zR"] - 0.3).buffer(0.45) if not d["fill"].is_empty else Point(d["FRONT"], d["zR"]).buffer(0.05)
    focus = wf if focus == "wmodel" else wf.union(d["root"].buffer(0.45))
    zone = B(-d["OF"], FLOOR - 0.6, d["RT"], d["zR"] + d["roof"])
    np.random.seed(0)
    P, T = W.mesh2d(d["s"], focus, h0=h0, zone=zone, hzone=hzone)
    global BOUNDARY; BOUNDARY = d["s"].boundary
    return P, T

def geom(P, T):
    y, z = P[T, 0], P[T, 1]
    A2 = (y[:, 1] - y[:, 0]) * (z[:, 2] - z[:, 0]) - (y[:, 2] - y[:, 0]) * (z[:, 1] - z[:, 0])
    dLy = np.c_[z[:, 1] - z[:, 2], z[:, 2] - z[:, 0], z[:, 0] - z[:, 1]] / A2[:, None]
    dLz = np.c_[y[:, 2] - y[:, 1], y[:, 0] - y[:, 2], y[:, 1] - y[:, 0]] / A2[:, None]
    return dLy, dLz, A2 / 2

BOUNDARY = None
def load_vec(P, zR, y0, y1, ndof, comp):
    """Unit total line load (1 N/mm), upward, on underside flat nodes z = zR, y in [y0, y1], tributary weights (as roof_load)."""
    on = np.where(np.isclose(P[:, 1], zR, rtol=0, atol=1e-3) & (P[:, 0] >= y0 - 1e-9) & (P[:, 0] <= y1 + 1e-9))[0]
    if BOUNDARY is not None: on = on[shapely.distance(BOUNDARY, shapely.points(P[on])) < 1e-6]   # surface nodes only
    ys = P[on, 0]; o = np.argsort(ys); on, ys = on[o], ys[o]
    wy = np.zeros(len(ys))
    for i in range(len(ys) - 1):
        seg = ys[i + 1] - ys[i]; wy[i] += seg / 2; wy[i + 1] += seg / 2
    if wy.sum() == 0: wy[:] = 1
    f = np.zeros(ndof); f[ndof // len(P) * on + comp] = wy / wy.sum()
    return f, ys

def bands(d, P, T):
    c = P[T].mean(1)
    e = np.stack([np.linalg.norm(P[T[:, i]] - P[T[:, (i + 1) % 3]], axis=1) for i in range(3)], 1).max(1)
    pts = shapely.points(c)
    root = d["root"]
    zlo = min(p[1] for p in root.coords) if root.geom_type == "LineString" else d["zR"]
    yhi = max(p[0] for p in root.coords) if root.geom_type == "LineString" else d["FRONT"]
    on_root = shapely.distance(root, pts) < 0.6 * e + 1e-9
    wall = LineString([(d["FRONT"], zlo - 1.0), (d["FRONT"], zlo)])
    on_wall = shapely.distance(wall, pts) < 0.6 * e + 1e-9
    flat = LineString([(yhi, d["zR"]), (yhi + 1.0, d["zR"])])
    on_flat = shapely.distance(flat, pts) < 0.6 * e + 1e-9
    return c, on_root, on_wall, on_flat

def peaks(syy, szz, c, on_root, on_wall, on_flat):
    out = {}
    j = np.argmax(np.where(on_root, syy, -1e9)); out["across"] = (syy[j], c[j])
    m = on_root | on_wall; j = np.argmax(np.where(m, szz, -1e9)); out["along"] = (szz[j], c[j])
    j = np.argmax(np.where(on_flat, syy, -1e9)); out["across_flat"] = (syy[j], c[j])
    return out

# ---------------- plane strain ----------------
def plane_strain(d, P, T, cases):
    """cases: {name: (y0, y1)}; unit line load each. Returns {name: peaks}."""
    dLy, dLz, A = geom(P, T)
    D = E / ((1 + NU) * (1 - 2 * NU)) * np.array([[1 - NU, NU, 0], [NU, 1 - NU, 0], [0, 0, (1 - 2 * NU) / 2]])
    ne = len(T); Bm = np.zeros((ne, 3, 6))
    Bm[:, 0, 0::2] = dLy; Bm[:, 1, 1::2] = dLz; Bm[:, 2, 0::2] = dLz; Bm[:, 2, 1::2] = dLy
    Ke = np.einsum("eki,kl,elj->eij", Bm, D, Bm) * A[:, None, None]
    dof = np.stack([2 * T[:, 0], 2 * T[:, 0] + 1, 2 * T[:, 1], 2 * T[:, 1] + 1, 2 * T[:, 2], 2 * T[:, 2] + 1], 1); n = 2 * len(P)
    K = sp.csr_matrix((Ke.ravel(), (np.repeat(dof, 6, 1).ravel(), np.tile(dof, (1, 6)).ravel())), shape=(n, n))
    fix = np.where(np.isclose(P[:, 1], -d["OZ"]))[0]; fd = np.r_[2 * fix, 2 * fix + 1]
    free = np.setdiff1d(np.arange(n), fd); lu = spl.splu(K[free][:, free].tocsc())
    c, on_root, on_wall, on_flat = bands(d, P, T)
    out = {}
    for name, (y0, y1) in cases.items():
        f, _ = load_vec(P, d["zR"], y0, y1, n, 1); u = np.zeros(n); u[free] = lu.solve(f[free])
        st = np.einsum("kl,elj,ej->ek", D, Bm, u[dof])
        out[name] = peaks(st[:, 0], st[:, 1], c, on_root, on_wall, on_flat)
    return out

# ---------------- Fourier prism ----------------
TRI_Q = np.array([[2/3, 1/6, 1/6], [1/6, 2/3, 1/6], [1/6, 1/6, 2/3]])
def fourier_parts(P, T):
    D = W.Dmat(); dLy, dLz, A = geom(P, T); ne = len(T)
    B0 = np.zeros((ne, 6, 9))
    for n in range(3):
        B0[:, 1, 3*n+1] = dLy[:, n]; B0[:, 2, 3*n+2] = dLz[:, n]; B0[:, 3, 3*n] = dLy[:, n]
        B0[:, 4, 3*n+1] = dLz[:, n]; B0[:, 4, 3*n+2] = dLy[:, n]; B0[:, 5, 3*n] = dLz[:, n]
    def B1(L):
        b = np.zeros((6, 9))
        for n in range(3):
            b[0, 3*n] = L[n]; b[3, 3*n+1] = -L[n]; b[5, 3*n+2] = -L[n]
        return b
    K0 = np.einsum("eki,kl,elj->eij", B0, D, B0) * A[:, None, None]
    K1 = np.zeros_like(K0); K2 = np.zeros_like(K0)
    for L in TRI_Q:
        b1 = B1(L)
        K1 += (np.einsum("eki,kl,lj->eij", B0, D, b1) + np.einsum("ki,kl,elj->eij", b1, D, B0)) * (A / 3)[:, None, None]
        K2 += np.einsum("ki,kl,lj->ij", b1, D, b1)[None] * (A / 3)[:, None, None]
    dof = (3 * T[:, :, None] + np.arange(3)).reshape(-1, 9); n = 3 * len(P)
    I = np.repeat(dof, 9, 1).ravel(); J = np.tile(dof, (1, 9)).ravel()
    mk = lambda Ke: sp.csr_matrix((Ke.ravel(), (I, J)), shape=(n, n))
    return mk(K0), mk(K1), mk(K2), B0, B1(np.ones(3) / 3), D, dof

KGRID = np.r_[0.01 * 1.18 ** np.arange(0, 48)]          # 0.01 .. ~24 /mm
def fourier(d, P, T, cases, Ptot=187.0, wx=0.6, xs=(0.0, 0.15, 0.3), kgrid=KGRID, verbose=False):
    """Peak stresses at the root for a patch load Ptot (N) over wx in x and y0..y1 in y, infinite prism (inference)."""
    K0, K1, K2, B0, B1c, D, dof = fourier_parts(P, T); n = 3 * len(P)
    c, on_root, on_wall, on_flat = bands(d, P, T)
    sel = np.where(on_root | on_wall | on_flat)[0]
    F = {name: load_vec(P, d["zR"], y0, y1, n, 2)[0] for name, (y0, y1) in cases.items()}
    Fm = np.stack(list(F.values()), 1)
    Syy = np.zeros((len(kgrid), len(F), len(sel))); Szz = np.zeros_like(Syy)
    t0 = time.time()
    for i, k in enumerate(kgrid):
        K = (K0 + k * K1 + k * k * K2).tocsc()
        U = spl.splu(K).solve(Fm)
        for j in range(len(F)):
            ue = U[:, j][dof[sel]]
            Bk = B0[sel] + k * B1c[None]
            st = np.einsum("kl,elj,ej->ek", D, Bk, ue)
            Syy[i, j] = st[:, 1]; Szz[i, j] = st[:, 2]
    if verbose: print(f"   fourier: {len(kgrid)} wavenumbers, {n} dofs, {time.time()-t0:.0f}s", flush=True)
    # integrate sigma(x) = int_0^inf A(k) s(k) cos(kx) dk, A = Ptot/pi * sinc(k wx/2); s(k) taken flat below kgrid[0]
    kk = np.r_[np.linspace(0, kgrid[0], 20)[:-1], np.exp(np.linspace(np.log(kgrid[0]), np.log(kgrid[-1]), 6000))]
    lk = np.log(np.maximum(kk, kgrid[0]))
    Ak = Ptot / np.pi * np.sinc(kk * wx / 2 / np.pi)
    out = {}
    cs = c[sel]; r_, w_, f_ = on_root[sel], on_wall[sel], on_flat[sel]
    for j, name in enumerate(F):
        best = {}
        for x in xs:
            wgt = Ak * np.cos(kk * x)
            def integ(S):
                Si = np.stack([np.interp(lk, np.log(kgrid), S[:, m]) for m in range(S.shape[1])], 1)
                return np.trapezoid(wgt[:, None] * Si, kk, axis=0)
            syy = integ(Syy[:, j]); szz = integ(Szz[:, j])
            pk = peaks(syy, szz, cs, r_, w_, f_)
            for key, v in pk.items():
                if key not in best or v[0] > best[key][0]: best[key] = (v[0], v[1], x)
        out[name] = best
    return out, (kgrid, Syy, Szz, sel)

def std_cases(d, which=("spread", "tip", "mid")):
    RT = d["RT"]
    allc = {"spread": (-ROD + 0.1, RT), "tip": (RT - 0.3, RT), "mid": (-2.1, -1.8), "spread295": (-ROD, RT)}
    return {k: allc[k] for k in which}

# ---------------- metrics v2: root surface incl. 0.3 of flat past the tangent point ----------------
def bands2(d, P, T, flat_len=0.3):
    c = P[T].mean(1)
    e = np.stack([np.linalg.norm(P[T[:, i]] - P[T[:, (i + 1) % 3]], axis=1) for i in range(3)], 1).max(1)
    pts = shapely.points(c); root = d["root"]
    if root.geom_type == "LineString" and not d["fill"].is_empty:
        zlo = min(p[1] for p in root.coords); yhi = max(p[0] for p in root.coords)
    else:
        zlo, yhi = d["zR"], d["FRONT"]
    tol = 0.6 * e + 1e-9
    arc = shapely.distance(root, pts) < tol
    flat = shapely.distance(LineString([(yhi, d["zR"]), (yhi + flat_len, d["zR"])]), pts) < tol
    wall = shapely.distance(LineString([(d["FRONT"], zlo - 1.0), (d["FRONT"], zlo)]), pts) < tol
    floor = shapely.distance(Point(d["FRONT"], FLOOR), pts) < 0.35
    return dict(c=c, arc=arc, flat=flat, wall=wall, floor=floor, yhi=yhi, zlo=zlo)

def metrics2(bd, syy, szz, sel=None):
    """sel: indices of elements the stress arrays refer to (None = all)."""
    c = bd["c"] if sel is None else bd["c"][sel]
    g = (lambda m: m) if sel is None else (lambda m: m[sel])
    out = {}
    for key, m, s in (("across_arc", g(bd["arc"]), syy), ("across_root", g(bd["arc"]) | g(bd["flat"]), syy),
                      ("along", g(bd["arc"]) | g(bd["wall"]), szz), ("floor_szz", g(bd["floor"]), szz), ("floor_syy", g(bd["floor"]), syy)):
        if not m.any(): out[key] = (np.nan, (np.nan, np.nan)); continue
        j = np.argmax(np.where(m, s, -1e9)); out[key] = (s[j], tuple(np.round(c[j], 3)))
    return out

def fourier2(d, P, T, cases, Ptot=187.0, wx=0.6, xs=(0.0, 0.1, 0.2, 0.3), kgrid=None, bd=None):
    """As fourier(), metrics v2; returns {case: {metric: (value, (y, z), x)}}."""
    kgrid = KGRID if kgrid is None else kgrid
    K0, K1, K2, B0, B1c, D, dof = fourier_parts(P, T); n = 3 * len(P)
    bd = bands2(d, P, T) if bd is None else bd
    sel = np.where(bd["arc"] | bd["flat"] | bd["wall"] | bd["floor"])[0]
    LV = [load_vec(P, d["zR"], y0, y1, n, 2) for (y0, y1) in cases.values()]
    F = np.stack([lv[0] for lv in LV], 1)
    global LOADSPAN; LOADSPAN = {nm: (float(lv[1].min()), float(lv[1].max()), len(lv[1])) if len(lv[1]) else (np.nan, np.nan, 0) for nm, lv in zip(cases, LV)}
    Syy = np.zeros((len(kgrid), F.shape[1], len(sel))); Szz = np.zeros_like(Syy)
    for i, k in enumerate(kgrid):
        U = spl.splu((K0 + k * K1 + k * k * K2).tocsc()).solve(F)
        if U.ndim == 1: U = U[:, None]
        Bk = B0[sel] + k * B1c[None]
        for j in range(F.shape[1]):
            st = np.einsum("kl,elj,ej->ek", D, Bk, U[:, j][dof[sel]]); Syy[i, j] = st[:, 1]; Szz[i, j] = st[:, 2]
    kk = np.r_[np.linspace(0, kgrid[0], 20)[:-1], np.exp(np.linspace(np.log(kgrid[0]), np.log(kgrid[-1]), 6000))]
    lk = np.log(np.maximum(kk, kgrid[0])); Ak = Ptot / np.pi * np.sinc(kk * wx / 2 / np.pi)
    out = {}
    for j, name in enumerate(cases):
        Iy = np.stack([np.interp(lk, np.log(kgrid), Syy[:, j, m]) for m in range(len(sel))], 1)
        Iz = np.stack([np.interp(lk, np.log(kgrid), Szz[:, j, m]) for m in range(len(sel))], 1)
        best = {}
        for x in xs:
            w = (Ak * np.cos(kk * x))[:, None]
            syy = np.trapezoid(w * Iy, kk, axis=0); szz = np.trapezoid(w * Iz, kk, axis=0)
            for key, v in metrics2(bd, syy, szz, sel).items():
                if key not in best or v[0] > best[key][0]: best[key] = (v[0], v[1], x)
        out[name] = best
    return out

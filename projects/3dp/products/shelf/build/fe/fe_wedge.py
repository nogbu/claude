"""3D FE with the r0.6 roof-root fillet resolved: the channel section (graded triangle mesh) extruded along x into 6-node
wedges, x XA..XE (mouth lead-ins left out), clamped at x XA. Isotropic E 1900, nu 0.38 (inference).
Written by the 2026-10-09 strength check (shelf thread). Needs pyamg: pip install pyamg (or a pylib folder beside it)."""
import sys, os, time, numpy as np, scipy.sparse as sp, shapely
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylib"))
import pyamg
from shapely.geometry import box as B, Point
from scipy.spatial import Delaunay
ROD = 2.95; BORE = 3.1; C = 0.3; WB = 2.8; TOP = 5.7; ROOF = 3.10; FRONT = -ROD - 0.6; FIL = 0.6; XE = 41.95
E, NU = 1900.0, 0.38
def section(fw, tr, tz, ov=2.0, fil=FIL):
    OF = fw - FRONT; OR = BORE + tr; OZ = BORE + tz; RT = -ROD + ov
    s = B(-OF, -OZ, OR, TOP).union(B(-OF, TOP, RT, TOP + C + ROOF)).difference(B(FRONT, WB - C, OR + 1, TOP + C))
    if fil > 0:
        s = s.union(B(FRONT, TOP + C - fil, FRONT + fil, TOP + C).difference(Point(FRONT + fil, TOP + C - fil).buffer(fil, 720)))
    s = s.difference(Point(0, 0).buffer(BORE, 720)).simplify(0.0005)
    return s, OF, OR, OZ, RT
def size_fn(p, focus, h0, grade, hmax, zone, hzone):
    d = shapely.distance(focus, shapely.points(p))
    h = np.minimum(h0 + grade * d, hmax)
    inz = shapely.contains_xy(zone, p[:, 0], p[:, 1])
    return np.where(inz, np.minimum(h, hzone), h)
def mesh2d(s, focus, h0=0.02, grade=0.35, hmax=0.3, zone=None, hzone=0.12):
    pts = []
    for ring in [s.exterior] + list(s.interiors):
        L = ring.length; t = 0.0
        while t < L:
            p = ring.interpolate(t); pts.append((p.x, p.y))
            t += size_fn(np.array([[p.x, p.y]]), focus, h0, grade, hmax, zone, hzone)[0] * 0.7
        cs = np.asarray(ring.coords)[:-1]; a = np.roll(cs, 1, 0); b = np.roll(cs, -1, 0)
        v1 = cs - a; v2 = b - cs; ang = np.degrees(np.abs(np.arctan2(v1[:, 0] * v2[:, 1] - v1[:, 1] * v2[:, 0], (v1 * v2).sum(1))))
        for q in cs[ang > 15]: pts.append(tuple(q))                # keep the sharp corners only
    pts = np.array(pts)
    inner = []
    y0, z0, y1, z1 = s.bounds
    levels = [h0 * 1.5 ** k for k in range(12) if h0 * 1.5 ** k < hmax * 1.6]
    for k, h in enumerate(levels):
        Y, Z = np.meshgrid(np.arange(y0, y1 + h, h), np.arange(z0, z1 + h, h))
        P = np.c_[Y.ravel(), Z.ravel()]
        P = P + (np.random.default_rng(k).random(P.shape) - 0.5) * h * 0.05
        hp = size_fn(P, focus, h0, grade, hmax, zone, hzone)
        lo = levels[k - 1] if k else 0; hi = h
        sel = (hp > lo * 1.0) & (hp <= hi * 1.0001) | ((k == len(levels) - 1) & (hp > hi))
        sel &= shapely.contains_xy(s.buffer(-0.55 * h), P[:, 0], P[:, 1])
        inner.append(P[sel])
    allp = np.unique(np.round(np.vstack([pts] + inner), 7), axis=0)
    from scipy.spatial import cKDTree
    hp = size_fn(allp, focus, h0, grade, hmax, zone, hzone); keep = np.ones(len(allp), bool); tree = cKDTree(allp)
    nb = len(pts)
    isb = shapely.distance(s.boundary, shapely.points(allp)) < 1e-6
    order = np.argsort(~isb)                                       # boundary points first
    for i in order:
        if not keep[i]: continue
        for j in tree.query_ball_point(allp[i], 0.35 * hp[i]):
            if j != i and keep[j] and not (isb[j] and not isb[i]): keep[j] = False
    allp = allp[keep]
    tri = Delaunay(allp).simplices
    c = allp[tri].mean(1); ok = shapely.contains_xy(s, c[:, 0], c[:, 1])
    tri = tri[ok]
    u1 = allp[tri[:, 1]] - allp[tri[:, 0]]; u2 = allp[tri[:, 2]] - allp[tri[:, 0]]; a2 = u1[:, 0] * u2[:, 1] - u1[:, 1] * u2[:, 0]
    tri = tri[np.abs(a2) > 1e-9]; a2 = a2[np.abs(a2) > 1e-9]
    tri[a2 < 0] = tri[a2 < 0][:, [0, 2, 1]]
    used = np.unique(tri); remap = -np.ones(len(allp), int); remap[used] = np.arange(len(used))
    return allp[used], remap[tri]
def Dmat():
    l = E * NU / ((1 + NU) * (1 - 2 * NU)); mu = E / (2 * (1 + NU))
    D = np.zeros((6, 6)); D[:3, :3] = l; D[np.arange(3), np.arange(3)] += 2 * mu; D[3:, 3:] = np.eye(3) * mu
    return D
TRI_Q = np.array([[2/3, 1/6, 1/6], [1/6, 2/3, 1/6], [1/6, 1/6, 2/3]]); TRI_W = np.array([1/3, 1/3, 1/3])
GZ = np.array([-1, 1]) / np.sqrt(3)
def wedge_parts(P, T):
    """Ke(dx) = Ka*dx + Kb/dx + Kc for each triangle. DOF order: node n (0-2 at x0, 3-5 at x1), comps (x, y, z)."""
    D = Dmat(); y, z = P[T, 0], P[T, 1]
    A2 = (y[:, 1] - y[:, 0]) * (z[:, 2] - z[:, 0]) - (y[:, 2] - y[:, 0]) * (z[:, 1] - z[:, 0]); A = A2 / 2
    dLy = np.c_[z[:, 1] - z[:, 2], z[:, 2] - z[:, 0], z[:, 0] - z[:, 1]] / A2[:, None]
    dLz = np.c_[y[:, 2] - y[:, 1], y[:, 0] - y[:, 2], y[:, 1] - y[:, 0]] / A2[:, None]
    ne = len(T); Ka = np.zeros((ne, 18, 18)); Kb = np.zeros_like(Ka); Kc = np.zeros_like(Ka)
    for L, wq in zip(TRI_Q, TRI_W):
        for zeta in GZ:
            g = np.r_[(1 - zeta) / 2 * np.ones(3), (1 + zeta) / 2 * np.ones(3)]     # x-weight per node
            s = np.r_[-np.ones(3), np.ones(3)]                                      # d/dx sign (times 1/dx)
            Lr = np.r_[L, L]
            # B = B_in (no dx) + B_x / dx ; in-plane derivative for node n: dL * g ; x derivative: Lr * s / dx  (dzeta/dx = 2/dx, dN/dzeta = Lr*s/2)
            Bin = np.zeros((ne, 6, 18)); Bx = np.zeros((ne, 6, 18))
            for n in range(6):
                k = n % 3; Ny = dLy[:, k] * g[n]; Nz = dLz[:, k] * g[n]; Nx = Lr[n] * s[n]
                Bx[:, 0, 3*n] = Nx; Bin[:, 1, 3*n+1] = Ny; Bin[:, 2, 3*n+2] = Nz
                Bin[:, 3, 3*n] = Ny; Bx[:, 3, 3*n+1] = Nx
                Bin[:, 4, 3*n+1] = Nz; Bin[:, 4, 3*n+2] = Ny
                Bin[:, 5, 3*n] = Nz; Bx[:, 5, 3*n+2] = Nx
            w = (A * wq * 0.5)[:, None, None]           # volume = A * dx; dzeta weight 1, Jacobian dx/2 -> factor dx * 0.5 per point
            Ka += w * np.einsum("eki,kl,elj->eij", Bin, D, Bin)
            Kb += w * np.einsum("eki,kl,elj->eij", Bx, D, Bx)
            Kc += w * (np.einsum("eki,kl,elj->eij", Bin, D, Bx) + np.einsum("eki,kl,elj->eij", Bx, D, Bin))
    return Ka, Kb, Kc, dLy, dLz, A
class WModel:
    def __init__(s, fw=2.4, tr=2.35, tz=2.48, XA=18.0, loads_x=(37.3, 38.0), fil=FIL, h0=0.02):
        s.sec, s.OF, s.OR, s.OZ, s.RT = section(fw, tr, tz, fil=fil)
        focus = Point(FRONT + 0.3, TOP + C - 0.3).buffer(0.45) if fil > 0 else Point(FRONT, TOP + C).buffer(0.05)
        zone = B(-s.OF, WB - C - 0.6, s.RT, TOP + C + ROOF)                          # front wall and roof
        s.P, s.T = mesh2d(s.sec, focus, h0=h0, zone=zone, hzone=0.12)
        xs = [XA]
        x = XA
        while x < XE - 1e-9:
            near = min(abs(x - lx) for lx in loads_x)
            h = 0.15 if near < 1.5 else (0.3 if near < 5 or x > 36 else 0.6)
            x = min(x + h, XE); xs.append(x)
        for lx in loads_x:
            for d in (-0.3, 0.3): xs.append(lx + d)
        s.X = np.unique(np.round(xs, 5)); s.XA = XA; s.fw, s.tr, s.tz = fw, tr, tz
        print(f"section: {len(s.T)} triangles, {len(s.P)} nodes; {len(s.X)} x-planes -> {len(s.T)*(len(s.X)-1)} wedges, {3*len(s.P)*len(s.X)} dofs", flush=True)
    def assemble(s):
        t = time.time(); Ka, Kb, Kc, s.dLy, s.dLz, s.A = wedge_parts(s.P, s.T); s.parts = (Ka, Kb, Kc)
        nP = len(s.P); n = 3 * nP * len(s.X)
        loc = np.c_[s.T, s.T + nP]                                     # 6 nodes, layer offset added per layer
        rows = []; K = None
        for k in range(len(s.X) - 1):
            dx = s.X[k + 1] - s.X[k]; Ke = Ka * dx + Kb / dx + Kc
            nodes = loc + k * nP; dofs = (3 * nodes[:, :, None] + np.arange(3)).reshape(-1, 18)
            Kl = sp.csr_matrix((Ke.ravel(), (np.repeat(dofs, 18, 1).ravel(), np.tile(dofs, (1, 18)).ravel())), shape=(n, n))
            K = Kl if K is None else K + Kl
        s.K = K.tocsr(); print(f"assembled {time.time()-t:.0f}s, nnz {s.K.nnz}", flush=True)
    def xyz(s):
        nP = len(s.P); k = np.repeat(np.arange(len(s.X)), nP)
        return np.c_[s.X[k], np.tile(s.P[:, 0], len(s.X)), np.tile(s.P[:, 1], len(s.X))]
    def roof_load(s, xc, wx, y0, y1, P):
        """Upward P on the roof underside (z TOP+C) over x xc+-wx/2 and y y0..y1, by tributary length/area."""
        nP = len(s.P); zU = TOP + C
        on = np.where(np.isclose(s.P[:, 1], zU, atol=1e-6) & (s.P[:, 0] >= y0 - 1e-9) & (s.P[:, 0] <= y1 + 1e-9))[0]
        ys = s.P[on, 0]; o = np.argsort(ys); on, ys = on[o], ys[o]
        wy = np.zeros(len(ys))
        for i in range(len(ys) - 1):
            seg = ys[i + 1] - ys[i]; wy[i] += seg / 2; wy[i + 1] += seg / 2
        kx = np.where((s.X >= xc - wx / 2 - 1e-9) & (s.X <= xc + wx / 2 + 1e-9))[0]; xs = s.X[kx]
        wxv = np.zeros(len(xs))
        for i in range(len(xs) - 1):
            seg = xs[i + 1] - xs[i]; wxv[i] += seg / 2; wxv[i + 1] += seg / 2
        f = np.zeros(3 * nP * len(s.X)); W = np.outer(wxv, wy); W *= P / W.sum()
        for a, k in enumerate(kx):
            f[3 * (k * nP + on) + 2] += W[a]
        return f
    def solve(s, loads):
        nP = len(s.P); n = 3 * nP * len(s.X)
        free = np.arange(3 * nP, n)                                     # clamp the x XA plane
        Kf = s.K[free][:, free].tocsr(); xyz = s.xyz()[free // 3]; comp = free % 3
        Bm = np.zeros((len(free), 6))
        for k in range(3): Bm[comp == k, k] = 1
        x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]
        Bm[comp == 1, 3] = -z[comp == 1]; Bm[comp == 2, 3] = y[comp == 2]
        Bm[comp == 0, 4] = z[comp == 0]; Bm[comp == 2, 4] = -x[comp == 2]
        Bm[comp == 0, 5] = -y[comp == 0]; Bm[comp == 1, 5] = x[comp == 1]
        t = time.time(); ml = pyamg.smoothed_aggregation_solver(Kf, B=Bm, max_coarse=2000); print(f"AMG setup {time.time()-t:.0f}s", flush=True)
        U = []
        for f in loads:
            t = time.time(); res = []
            u = ml.solve(f[free], tol=1e-9, accel="cg", maxiter=600, residuals=res)
            print(f"  solve {time.time()-t:.0f}s, {len(res)} it, rel res {res[-1]/res[0]:.1e}", flush=True)
            full = np.zeros(n); full[free] = u; U.append(full)
        return U
    def stress_layer(s, u, k):
        """Element-centre stresses (L = 1/3, zeta = 0) of x-layer k: array (ntri, 6) xx yy zz xy yz xz."""
        nP = len(s.P); dx = s.X[k + 1] - s.X[k]; D = Dmat()
        nodes = np.c_[s.T, s.T + nP] + k * nP; ue = u[(3 * nodes[:, :, None] + np.arange(3)).reshape(-1, 18)]
        ne = len(s.T); Bm = np.zeros((ne, 6, 18)); g = 0.5; L = 1 / 3
        for nn in range(6):
            kk = nn % 3; sg = -1 if nn < 3 else 1
            Ny = s.dLy[:, kk] * g; Nz = s.dLz[:, kk] * g; Nx = L * sg / dx
            Bm[:, 0, 3*nn] = Nx; Bm[:, 1, 3*nn+1] = Ny; Bm[:, 2, 3*nn+2] = Nz
            Bm[:, 3, 3*nn] = Ny; Bm[:, 3, 3*nn+1] = Nx; Bm[:, 4, 3*nn+1] = Nz; Bm[:, 4, 3*nn+2] = Ny
            Bm[:, 5, 3*nn] = Nz; Bm[:, 5, 3*nn+2] = Nx
        return np.einsum("kl,elj,ej->ek", D, Bm, ue)

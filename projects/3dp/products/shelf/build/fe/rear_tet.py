"""3D check of the rear piece (rear-piece_model.py) with 10-node tets (tetgen) and pyamg; isotropic E 1900, nu 0.38 (inference,
as fe_wedge.py). The clip patch (x -44.5..-29.5 on the body's underside) is held; the rods load the bores: stub ends push down
along the stub (x 0..stub, default 10, the shorter measured stub; the first run used 2.5), the lip rod pushes up on the sleeve
top (tip: the last 2.5 mm; spread: growing linearly from the sleeve root). 15 lb x 3 per corner (agreed change 11), moments about
the stub ends (x 0). Prints element-center stresses by zone; pickles rear_tet_[reach][tag].pkl for rear-sleeve_stress.py.
Rod contacts are bands as wide as Hertz line contact (rod 2.95 in the 3.1 bore), elliptical pressure; --hertz 0 loads the
whole bore arc beyond 1.5 mm of the center height instead (the 2026-10-10 first runs).
Needs: pip install tetgen pyamg. Usage: python3 rear_tet.py [reach tz ttop tr xd] [--stub 10] [--close -1.75] [--trim] [--hertz 0]
[--fine 0.3 --nseg 48] [--taper 1.0] (contact pressure ramps up over that length at each contact end) (mesh refined to that size at the rod contacts, circles of that many segments) [--meshonly]
(--close: rear wall closed below that z from the lip bore center; --trim: knife-edge lips cut to one bead; rear-piece_model.py).
About 3-5 min on 4 CPUs, 6.6 GB. Written 2026-10-10 (shelf thread, open decision 3). Shape gradients fixed 2026-10-10 (einsum nl,ekl):
the earlier runs used inv(J) transposed, which fails a linear-field test, so their stresses and deflections (agreed change 31) are invalid."""
import importlib.util, os, sys, time, numpy as np, scipy.sparse as sp, manifold3d as m, tetgen, pyamg
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "..", "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
argv = sys.argv[1:]; flags = {}; a = []
while argv:
    w = argv.pop(0)
    if w in ("--trim", "--meshonly"): flags[w[2:]] = True
    elif w.startswith("--"): flags[w[2:]] = float(argv.pop(0))
    else: a.append(float(w))
NSEG = int(flags.get("nseg", 24)); FINE = flags.get("fine"); GROW = flags.get("grow", 1.0)   # circle segments; element size at the rod contacts (None: uniform mesh)
def cyl(r, h, axis, r2=None, n=None):                     # coarser circles keep the tet count down; NSEG for the bores only
    c = m.Manifold.cylinder(h, r, r if r2 is None else r2, n or (NSEG if r > 2 else 24)); return c.rotate([0, 90, 0]) if axis == "x" else c.rotate([-90, 0, 0])
RP.cyl = cyl
reach, tz, ttop, tr, xd = (a + [40.0, 2.48, 2.48, 2.35, -15.0][len(a):])[:5]
STUB = flags.get("stub", 10.0); CLOSE = flags.get("close"); TRIM = flags.get("trim", False); HERTZ = flags.get("hertz", 1.0) > 0
RS = 2.95; ES = 1900.0 / (1 - 0.38 ** 2)                      # rod radius (5.9 measured); PETG on steel, steel taken as rigid (inference)
TAG = ("" if CLOSE is None else f"_close{-CLOSE:g}") + ("_trim" if TRIM else "") + ("" if FINE is None else f"_fine{FINE:g}_n{NSEG}") + (f"_taper{flags['taper']:g}" if flags.get("taper") else "")
E, NU = 1900.0, 0.38
Fc = 15 * 4.448 * 3; XC = RP.X0 + 8.0; M = Fc * -XC; J0 = RP.J0; LIPB = RP.LIPB; BORE = RP.BORE
piece, d = RP.build(reach=reach, tz=tz, ttop=ttop, tr=tr, xd=xd, close_below=CLOSE, trim=TRIM)
t0 = time.time(); surf = RP.tm(piece.refine_to_length(2.0))
from scipy.spatial import cKDTree
CPTS = np.array([(x, BORE * np.sin(t), z0 + sg * BORE * np.cos(t)) for x in np.arange(0, reach + 0.01, 0.1) for t in np.linspace(-0.6, 0.6, 13)
                 for z0, sg, ok in ((LIPB, 1, x >= reach - 2.5), (LIPB, -1, x <= STUB), (0.0, -1, x <= STUB)) if ok])   # rod contact bands
def refine_near(V, F, size):
    """Split surface edges longer than size(midpoint), longest first, never two edges of one face in a pass, so the surface stays
    conforming. tetgen's background sizing mesh (bgmesh) crashed (segfault, tetgen 0.8.4), so the fine surface sets the tet size."""
    V = [tuple(v) for v in V]; F = [list(f) for f in F]
    while True:
        E = {}
        for fi, f in enumerate(F):
            for i in range(3):
                a, b = f[i], f[(i + 1) % 3]; E.setdefault((min(a, b), max(a, b)), []).append(fi)
        keys = list(E); P = np.array(V); A = np.array([k[0] for k in keys]); B = np.array([k[1] for k in keys])
        L = np.linalg.norm(P[A] - P[B], axis=1); H = size((P[A] + P[B]) / 2); cand = np.flatnonzero(L > H)
        if not len(cand): return np.array(V), np.array(F)
        used = set(); newF = {}
        for e in cand[np.argsort(-L[cand])]:
            fs = E[keys[e]]
            if any(fi in used for fi in fs): continue
            used.update(fs); a, b = keys[e]; V.append(tuple((P[a] + P[b]) / 2)); mi = len(V) - 1
            for fi in fs:
                f = F[fi]; i = next(j for j in range(3) if {f[j], f[(j + 1) % 3]} == {a, b})
                p0, p1, p2 = f[i], f[(i + 1) % 3], f[(i + 2) % 3]; newF[fi] = [[p0, mi, p2], [mi, p1, p2]]
        F = [g for fi, f in enumerate(F) for g in (newF[fi] if fi in newF else [f])]
SV, SF = surf.vertices, surf.faces
if FINE:                                                  # surface edges FINE at the rod contacts, growing GROW per mm away
    tree = cKDTree(CPTS); SV, SF = refine_near(SV, SF, lambda q: np.clip(FINE + GROW * tree.query(q)[0], FINE, 2.5))
    print(f"surface refined at the contacts: {len(surf.faces)} -> {len(SF)} faces ({time.time()-t0:.0f}s)", flush=True)
X, T = tetgen.TetGen(SV, SF).tetrahedralize(order=2, mindihedral=15, minratio=1.6, maxvolume=2.0)[:2]
X = np.asarray(X, float); T = np.asarray(T, np.int64)
cor = T[:, :4]; EDGES = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
mid = X[T[0, 4:]]; perm = []                              # map tetgen's edge-node order onto EDGES
for i, j in EDGES:
    target = (X[T[0, i]] + X[T[0, j]]) / 2; perm.append(4 + int(np.argmin(np.linalg.norm(mid - target, axis=1))))
T = np.c_[cor, T[:, perm]]
print(f"mesh {len(T)} tets, {len(X)} nodes, {3*len(X)} dofs ({time.time()-t0:.0f}s)", flush=True)
if flags.get("meshonly"):
    Xc = X[T[:, :4]]; ed = np.linalg.norm(Xc[:, 1] - Xc[:, 0], axis=1); near = cKDTree(CPTS).query(Xc.mean(1))[0] < 0.5
    print(f"edge length at the contacts: median {np.median(ed[near]):.2f}, elsewhere {np.median(ed[~near]):.2f}"); sys.exit()
# shape function derivatives at 4 Gauss points (barycentric L0 = 1 - xi - eta - zeta)
ga, gb = 0.5854101966249685, 0.1381966011250105
QP = np.array([[gb, gb, gb], [ga, gb, gb], [gb, ga, gb], [gb, gb, ga]]); QW = np.full(4, 1 / 24)
def dN(xi):
    L = np.r_[1 - xi.sum(), xi]; dL = np.array([[-1, -1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    out = np.zeros((10, 3))
    for k in range(4): out[k] = (4 * L[k] - 1) * dL[k]
    for e, (i, j) in enumerate(EDGES): out[4 + e] = 4 * (L[i] * dL[j] + L[j] * dL[i])
    return out
lam = E * NU / ((1 + NU) * (1 - 2 * NU)); mu = E / (2 * (1 + NU))
D = np.zeros((6, 6)); D[:3, :3] = lam; D[np.arange(3), np.arange(3)] += 2 * mu; D[3:, 3:] = np.eye(3) * mu
def dNdx(Xe, G):                                          # Xe (ne, 10, 3), G = dN(xi) (10, 3) -> dN/dx (ne, 10, 3), det J
    J = np.transpose(np.einsum("enk,nl->ekl", Xe, G), (0, 2, 1))   # J[e, l, k] = dx_k / dxi_l
    return np.einsum("nl,ekl->enk", G, np.linalg.inv(J)), np.linalg.det(J)
def Bmat(dNx):                                            # dNx (ne, 10, 3) -> B (ne, 6, 30); strain order xx yy zz xy yz xz
    ne = len(dNx); Bm = np.zeros((ne, 6, 30)); x, y, z = dNx[:, :, 0], dNx[:, :, 1], dNx[:, :, 2]
    Bm[:, 0, 0::3] = x; Bm[:, 1, 1::3] = y; Bm[:, 2, 2::3] = z
    Bm[:, 3, 0::3] = y; Bm[:, 3, 1::3] = x; Bm[:, 4, 1::3] = z; Bm[:, 4, 2::3] = y; Bm[:, 5, 0::3] = z; Bm[:, 5, 2::3] = x
    return Bm
t0 = time.time(); Xe = X[T]; ne = len(T)
_q = QP[1]; _x = Xe[0]; _A = np.array([[1.0, 0.3, -0.2], [0.1, -0.7, 0.4], [0.5, 0.2, 0.9]]); _b = np.array([0.3, -1.1, 0.6])
_p = np.r_[1 - _q.sum(), _q] @ _x[:4]; _g = (_A + _A.T) @ _p + _b       # a quadratic field's gradient must come out exact
assert np.allclose((np.einsum("ni,ij,nj->n", _x, _A, _x) + _x @ _b) @ dNdx(_x[None], dN(_q))[0][0], _g, rtol=1e-7, atol=1e-7 * abs(_g).max()), "shape gradient check failed"
dofs = (3 * T[:, :, None] + np.arange(3)).reshape(ne, 30).astype(np.int64)
n = 3 * len(X); K = None
for c0 in range(0, ne, 20000):                            # in chunks: the whole COO triplet set ran to about 13 GB at 270k tets
    sl = slice(c0, c0 + 20000); Ke = np.zeros((len(Xe[sl]), 30, 30))
    for q, w in zip(QP, QW):
        dNx, detJ = dNdx(Xe[sl], dN(q))
        Bm = Bmat(dNx); Ke += (w * detJ)[:, None, None] * np.einsum("eki,kl,elj->eij", Bm, D, Bm)
    dc = dofs[sl].astype(np.int32)
    Kc = sp.csr_matrix((Ke.ravel(), (np.repeat(dc, 30, 1).ravel(), np.tile(dc, (1, 30)).ravel())), shape=(n, n))
    K = Kc if K is None else K + Kc
del Ke, Kc
print(f"assembled ({time.time()-t0:.0f}s), nnz {K.nnz}", flush=True)
# boundary faces (6-node): face opposite corner k
fc = np.array([[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]])
def edge_id(i, j): return EDGES.index((min(i, j), max(i, j))) + 4
fm = np.array([[edge_id(f[0], f[1]), edge_id(f[1], f[2]), edge_id(f[0], f[2])] for f in fc])
allf = np.concatenate([T[:, fc[k]] for k in range(4)]); allm = np.concatenate([T[:, fm[k]] for k in range(4)])
key = np.sort(allf, 1); _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
bnd = cnt[inv.ravel()] == 1; BF, BM = allf[bnd], allm[bnd]
P0, P1, P2 = X[BF[:, 0]], X[BF[:, 1]], X[BF[:, 2]]; cr = np.cross(P1 - P0, P2 - P0); area = np.linalg.norm(cr, axis=1) / 2
cen = (P0 + P1 + P2) / 3
def bore(zc): r = np.hypot(cen[:, 1], cen[:, 2] - zc); return (r > BORE - 0.06) & (r < BORE + 0.01)
def patch_load(sel, wts, total, comp):
    f = np.zeros(n); wa = area[sel] * wts; wa *= total / wa.sum()
    for k in range(3): np.add.at(f, 3 * BM[sel, k] + comp, wa / 3)
    return f
clip = (np.abs(cen[:, 2] - RP.ZB) < 1e-3) & (cen[:, 0] > XC - 7.5) & (cen[:, 0] < XC + 7.5)
fixed_nodes = np.unique(np.r_[BF[clip].ravel(), BM[clip].ravel()])
def halfw(q):                                              # line-contact half-width (Hertz) for q N/mm, rod RS in the bore
    return np.sqrt(4 * q * (1 / (1 / RS - 1 / BORE)) / (np.pi * ES))
def band(sel, b):                                          # elliptical pressure across the contact band |y| < b (all faces if --hertz 0)
    if not HERTZ: return sel, np.ones(sel.sum())
    yy = cen[:, 1]; keep = sel & (np.abs(yy) < b if np.isscalar(b) else np.abs(yy) < b)
    bb = b if np.isscalar(b) else b[keep]
    return keep, np.sqrt(np.clip(1 - (yy[keep] / bb) ** 2, 0.05, 1)) / bb
lipfloor = bore(LIPB) & (cen[:, 0] < STUB) & (cen[:, 2] < LIPB - 1.5)   # the stub bears along its length (tilt about 0.003 rad)
cfloor = bore(0.0) & (cen[:, 0] < STUB) & (cen[:, 2] < -1.5)
liptop = bore(LIPB) & (cen[:, 2] > LIPB + 1.5)
tip = liptop & (cen[:, 0] > reach - 2.5); spread = liptop & (cen[:, 0] > J0)
P_tip = M / reach
k = 3 * M / (reach ** 3 - J0 ** 3); P_spr = k * (reach ** 2 - J0 ** 2) / 2
bt, bs = halfw(P_tip / 2.5), halfw((Fc + P_tip) / STUB); bsp = halfw((Fc + P_spr) / STUB)
tip, wt = band(tip, bt); lipF, wl = band(lipfloor, bs); corF, wc = band(cfloor, bs); lipF2, wl2 = band(lipfloor, bsp)
spread, ws = band(spread, halfw(k * np.maximum(cen[:, 0], J0 + 0.1)))
ws = ws * cen[spread, 0]
TAPER = flags.get("taper", 0.0)                           # pressure ramps from 0 over this length at each end of a contact (lead-in, rod end chamfer)
def ramp(sel, x0, x1):
    return 1.0 if TAPER <= 0 else np.clip(np.minimum(cen[sel, 0] - x0, x1 - cen[sel, 0]) / TAPER, 0.02, 1)
wt = wt * ramp(tip, reach - 2.5, reach); wl = wl * ramp(lipF, 0, STUB); wc = wc * ramp(corF, 0, STUB); wl2 = wl2 * ramp(lipF2, 0, STUB)
ws = ws * ramp(spread, J0, reach)
print(f"contact half-widths (Hertz, inference): tip {bt:.2f}, stubs {bs:.2f}, spread at the tip {halfw(k * reach):.2f} mm" if HERTZ else "wide patches", flush=True)
lipfloor, cfloor = lipF, corF
cases = {"tip, stubs on the lip rod": patch_load(tip, wt, P_tip, 2) + patch_load(lipF, wl, -(Fc + P_tip), 2),
         "tip, stubs on the corner rod": patch_load(tip, wt, P_tip, 2) + patch_load(corF, wc, -(Fc + P_tip), 2),
         "spread, stubs on the lip rod": patch_load(spread, ws, P_spr, 2) + patch_load(lipF2, wl2, -(Fc + P_spr), 2)}
print(f"stub bearing x 0..{STUB:g}, close {CLOSE}, trim {TRIM}; clip {Fc:.0f} N at x {XC:.0f}; tip P {P_tip:.0f} N, spread P {P_spr:.0f} N; patches: clip {clip.sum()}, tip {tip.sum()}, "
      f"spread {spread.sum()}, lip floor {lipfloor.sum()}, corner floor {cfloor.sum()}", flush=True)
fixed = (3 * fixed_nodes[:, None] + np.arange(3)).ravel(); free = np.setdiff1d(np.arange(n), fixed)
Kf = K[free][:, free].tocsr(); xyz = X[free // 3]; comp = free % 3
Bn = np.zeros((len(free), 6))
for c in range(3): Bn[comp == c, c] = 1
x_, y_, z_ = xyz.T
Bn[comp == 1, 3] = -z_[comp == 1]; Bn[comp == 2, 3] = y_[comp == 2]; Bn[comp == 0, 4] = z_[comp == 0]; Bn[comp == 2, 4] = -x_[comp == 2]
Bn[comp == 0, 5] = -y_[comp == 0]; Bn[comp == 1, 5] = x_[comp == 1]
import resource
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
t0 = time.time(); ml = pyamg.smoothed_aggregation_solver(Kf, B=Bn, smooth=None, max_coarse=1000)   # unsmoothed: the smoothed hierarchy ran out of memory (14 GB)
print(f"AMG setup {time.time()-t0:.0f}s, levels {[l.A.shape[0] for l in ml.levels]}, peak RSS {rss():.1f} GB", flush=True)
dNc = dNdx(Xe, dN(np.full(3, 0.25)))[0]
Bc = Bmat(dNc); ec = Xe[:, :4].mean(1)
zones = {"sleeve body (x root+3 .. end-3)": (ec[:, 0] > J0 + 3) & (ec[:, 0] < reach - 3),
         "sleeve root and fillet (x J0-1 .. J0+3)": (ec[:, 0] > J0 - 1) & (ec[:, 0] < J0 + 3) & (ec[:, 2] < RP.ZB - 0.5),
         "drop below the body (z < clip seat), x < J0-1": (ec[:, 0] < J0 - 1) & (ec[:, 2] < RP.ZB - 0.5),
         "body over the clip and drop (z >= clip seat)": ec[:, 2] >= RP.ZB - 0.5}
near_load = cKDTree(cen[tip | lipfloor | cfloor]).query(ec, distance_upper_bound=1.5)[0] < 1.5
zones["sleeve tip (x end-3 .. end)"] = ec[:, 0] >= reach - 3
for nm, sel in (("contact: lip rod on the sleeve top at the tip", tip), ("contact: stub on the lip bore floor", lipfloor),
                ("contact: stub on the corner bore floor", cfloor)):
    zones[nm] = cKDTree(cen[sel]).query(ec, distance_upper_bound=1.0)[0] < 1.0
print(f"Hertz peak pressure (inference): tip {2 * P_tip / 2.5 / (np.pi * bt):.0f}, stubs {2 * (Fc + P_tip) / STUB / (np.pi * bs):.0f} MPa", flush=True)
out = {}
for name, f in cases.items():
    t0 = time.time(); res = []
    def cb(xk):
        if len(res) % 50 == 0: print(f"   it {len(res)} rel res {res[-1]/res[0]:.1e} {time.time()-t0:.0f}s RSS {rss():.1f} GB", flush=True)
    u = ml.solve(f[free], tol=1e-6, accel="cg", maxiter=1500, residuals=res, callback=cb)
    U = np.zeros(n); U[free] = u
    S = np.einsum("kl,elj,ej->ek", D, Bc, U[dofs])
    s1 = np.linalg.eigvalsh(np.stack([np.stack([S[:, 0], S[:, 3], S[:, 5]], -1), np.stack([S[:, 3], S[:, 1], S[:, 4]], -1),
                                      np.stack([S[:, 5], S[:, 4], S[:, 2]], -1)], -2))
    print(f"== {name}: {len(res)} it, rel res {res[-1]/res[0]:.1e}, {time.time()-t0:.0f}s; max uz {U[2::3].max():.3f} / min {U[2::3].min():.3f} mm")
    for zn, sel in zones.items():
        for lab, s2 in (("away from load patches", sel & ~near_load), ("at load patches", sel & near_load)):
            if not s2.any(): continue
            i1 = np.argmax(np.where(s2, s1[:, 2], -1e9)); i3 = np.argmin(np.where(s2, s1[:, 0], 1e9)); iy = np.argmax(np.where(s2, S[:, 1], -1e9))
            print(f"   {zn}, {lab}: max tension {s1[i1, 2]:5.1f} at {np.round(ec[i1], 1)}, max compression {s1[i3, 0]:6.1f} at "
                  f"{np.round(ec[i3], 1)}, across layers (syy) {S[iy, 1]:5.1f} at {np.round(ec[iy], 1)}")
    out[name] = dict(S=S, s1=s1, U=U)
import pickle; pickle.dump(dict(X=X, T=T, ec=ec, d=d, args=(reach, tz, ttop, tr, xd), opts=dict(stub=STUB, close_below=CLOSE, trim=TRIM, hertz=HERTZ), out={k: dict(S=v["S"], s1=v["s1"]) for k, v in out.items()}),
                         open(os.path.join(HERE, f"rear_tet_{reach:g}{TAG}{'' if HERTZ else '_wide'}.pkl"), "wb"))

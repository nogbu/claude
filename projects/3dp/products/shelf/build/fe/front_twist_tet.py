"""3D check of the twist-lock front piece (front-twist_model.py build(zs=ZB)) with 10-node tets (tetgen) and pyamg, as rear_tet.py:
isotropic E 1900, nu 0.38 (inference). The clip patch (x -44.5..-29.5 on the body's underside) is held; the rod loads the bore:
the stub pushes down on the stub bore floor near the rod end (x 0..STUB, default 2.5: under the tilt the floor reaction gathers there), moments taken about its centroid, and the rod pushes up on the hook's inner top (bore top, z > 1.5)
in three placements: "start" (the first 2.5 mm of the hook), "end" (the last 2.5 mm before the lead-in) and "spread" (growing
linearly from the hook start, as a rigid tilt about the stub would). 15 lb x 3 per corner (agreed change 11), moments about the
floor load's centroid (x 1.25). Layers stack in model y (prints on its front face), so across the layers is syy and the shear between layers is
sqrt(sxy^2 + syz^2). Rod contacts are elliptical Hertz bands (rod 2.95 in the 3.1 bore); read 3D away from them (learnings/fe).
Needs: pip install tetgen pyamg. Usage: python3 front_twist_tet.py [--fine 0.5] [--nseg 32] [--fw 3.0] [--fy -1.0] [--stub 2.5] [--hh 4.6 [--hx0 10.25]] [--rl 2.0] [--meshonly]
(--hh, --hx0: the raised top, front-twist_model.py build(); --rl: surface edge length before refining (another value
when tetgen fails on slivers); --fine: surface edges that long at the front wall beside the crosswire and along the hook root, growing 1 per mm away).
Pickles front_twist_tet[tag].pkl. Written 2026-10-10 (shelf thread, open decision 9). Shape gradients fixed 2026-10-10: the first runs used\ninv(J) transposed (einsum nl,elk), copied from rear_tet.py, which fails a linear-field test; peaks at the two sharp inside edges are read at 0.5 and 1 mm."""
import importlib.util, os, sys, time, numpy as np, scipy.sparse as sp, manifold3d as m, tetgen, pyamg, resource
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("front_twist_model", os.path.join(HERE, "..", "front-twist_model.py"))
TW = importlib.util.module_from_spec(spec); spec.loader.exec_module(TW)
argv = sys.argv[1:]; flags = {}
while argv:
    w = argv.pop(0)
    if w == "--meshonly": flags["meshonly"] = True
    else: flags[w[2:]] = float(argv.pop(0))
NSEG = int(flags.get("nseg", 32)); FINE = flags.get("fine"); GROW = 1.0; FW = flags.get("fw", 3.0); FY = flags.get("fy"); HH = flags.get("hh", 0.0); HX0 = flags.get("hx0"); RL = flags.get("rl", 2.0)
def cyl(r, h, axis, r2=None, n=None):
    c = m.Manifold.cylinder(h, r, r if r2 is None else r2, n or NSEG); return c.rotate([0, 90, 0]) if axis == "x" else c.rotate([-90, 0, 0])
TW.cyl = cyl
BORE, J0, XH0, ZB, X0 = TW.BORE, TW.J0, TW.XH0, TW.ZB, TW.X0
STUB = flags.get("stub", 2.5); RS = 2.95; E, NU = 1900.0, 0.38; ES = E / (1 - NU ** 2)
Fc = 15 * 4.448 * 3; XC = X0 + 8.0; M = Fc * -XC
piece, d = TW.build(fw=FW, fy=FY, hh=HH, hx0=HX0); XH1 = d["XH1"]; XE = XH1 - TW.LEAD            # bore ends where the hook's lead-in starts
TAG = f"_fw{FW:g}" + ("" if FY is None else f"_fy{FY:g}") + (f"_hh{HH:g}_hx{d['hx0']:g}" if HH else "") + ("" if FINE is None else f"_fine{FINE:g}") + f"_n{NSEG}"
t0 = time.time(); surf = TW.tm(piece.refine_to_length(RL))
surf.merge_vertices(digits_vertex=4); surf.update_faces(surf.nondegenerate_faces()); surf.remove_unreferenced_vertices()   # manifold leaves float32 twins (zero-length edges)
assert surf.is_watertight and surf.is_winding_consistent
L = np.linalg.norm(surf.vertices[surf.edges_unique[:, 0]] - surf.vertices[surf.edges_unique[:, 1]], axis=1)
print(f"model {piece.volume():.0f} mm3, shortest edge {L.min():.3f} mm (under 0.05 is a sliver)", flush=True)
# zones to refine: the front wall beside the crosswire (x J0..XH0) and the hook root (inner face from the bore top round to the wall)
RPTS = np.array([(x, y, z) for x in np.arange(J0 - 1, XH0 + 1.01, 0.5) for y in np.linspace(d["YF"], TW.YI, 4) for z in np.linspace(ZB, TW.TOP, 21)] +
                [(x, BORE * np.cos(a), BORE * np.sin(a)) for x in np.arange(XH0, XH1 + 0.01, 0.5) for a in np.linspace(np.pi / 4, np.pi, 10)])
def refine_near(V, F, size):
    """Split surface edges longer than size(midpoint), longest first, never two edges of one face in a pass (rear_tet.py)."""
    V = [tuple(v) for v in V]; F = [list(f) for f in F]
    while True:
        Ed = {}
        for fi, f in enumerate(F):
            for i in range(3):
                a, b = f[i], f[(i + 1) % 3]; Ed.setdefault((min(a, b), max(a, b)), []).append(fi)
        keys = list(Ed); P = np.array(V); A = np.array([k[0] for k in keys]); B = np.array([k[1] for k in keys])
        Ln = np.linalg.norm(P[A] - P[B], axis=1); H = size((P[A] + P[B]) / 2); cand = np.flatnonzero(Ln > H)
        if not len(cand): return np.array(V), np.array(F)
        used = set(); newF = {}
        for e in cand[np.argsort(-Ln[cand])]:
            fs = Ed[keys[e]]
            if any(fi in used for fi in fs): continue
            used.update(fs); a, b = keys[e]; V.append(tuple((P[a] + P[b]) / 2)); mi = len(V) - 1
            for fi in fs:
                f = F[fi]; i = next(j for j in range(3) if {f[j], f[(j + 1) % 3]} == {a, b})
                p0, p1, p2 = f[i], f[(i + 1) % 3], f[(i + 2) % 3]; newF[fi] = [[p0, mi, p2], [mi, p1, p2]]
        F = [g for fi, f in enumerate(F) for g in (newF[fi] if fi in newF else [f])]
SV, SF = surf.vertices, surf.faces
if FINE:
    tree = cKDTree(RPTS); SV, SF = refine_near(SV, SF, lambda q: np.clip(FINE + GROW * tree.query(q)[0], FINE, 2.0))
    print(f"surface refined: {len(surf.faces)} -> {len(SF)} faces ({time.time()-t0:.0f}s)", flush=True)
X, T = tetgen.TetGen(SV, SF).tetrahedralize(order=2, mindihedral=15, minratio=1.6, maxvolume=1.0 if FINE else 2.0)[:2]
X = np.asarray(X, float); T = np.asarray(T, np.int64)
cor = T[:, :4]; EDGES = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
mid = X[T[0, 4:]]; perm = []
for i, j in EDGES:
    target = (X[T[0, i]] + X[T[0, j]]) / 2; perm.append(4 + int(np.argmin(np.linalg.norm(mid - target, axis=1))))
T = np.c_[cor, T[:, perm]]
print(f"mesh {len(T)} tets, {len(X)} nodes, {3*len(X)} dofs ({time.time()-t0:.0f}s)", flush=True)
if flags.get("meshonly"): sys.exit()
ga, gb = 0.5854101966249685, 0.1381966011250105
QP = np.array([[gb, gb, gb], [ga, gb, gb], [gb, ga, gb], [gb, gb, ga]]); QW = np.full(4, 1 / 24)
def dN(xi):
    Lb = np.r_[1 - xi.sum(), xi]; dL = np.array([[-1, -1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    out = np.zeros((10, 3))
    for k in range(4): out[k] = (4 * Lb[k] - 1) * dL[k]
    for e, (i, j) in enumerate(EDGES): out[4 + e] = 4 * (Lb[i] * dL[j] + Lb[j] * dL[i])
    return out
lam = E * NU / ((1 + NU) * (1 - 2 * NU)); mu = E / (2 * (1 + NU))
D = np.zeros((6, 6)); D[:3, :3] = lam; D[np.arange(3), np.arange(3)] += 2 * mu; D[3:, 3:] = np.eye(3) * mu
def dNdx(Xe, G):                                          # Xe (ne, 10, 3), G = dN(xi) (10, 3) -> dN/dx (ne, 10, 3), det J
    J = np.transpose(np.einsum("enk,nl->ekl", Xe, G), (0, 2, 1))   # J[e, l, k] = dx_k / dxi_l
    return np.einsum("nl,ekl->enk", G, np.linalg.inv(J)), np.linalg.det(J)
def Bmat(dNx):                                            # strain order xx yy zz xy yz xz
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
for c0 in range(0, ne, 20000):
    sl = slice(c0, c0 + 20000); Ke = np.zeros((len(Xe[sl]), 30, 30))
    for q, w in zip(QP, QW):
        dNx, detJ = dNdx(Xe[sl], dN(q))
        Bm = Bmat(dNx); Ke += (w * detJ)[:, None, None] * np.einsum("eki,kl,elj->eij", Bm, D, Bm)
    dc = dofs[sl].astype(np.int32)
    Kc = sp.csr_matrix((Ke.ravel(), (np.repeat(dc, 30, 1).ravel(), np.tile(dc, (1, 30)).ravel())), shape=(n, n))
    K = Kc if K is None else K + Kc
del Ke, Kc
print(f"assembled ({time.time()-t0:.0f}s), nnz {K.nnz}", flush=True)
fc = np.array([[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]])
def edge_id(i, j): return EDGES.index((min(i, j), max(i, j))) + 4
fm = np.array([[edge_id(f[0], f[1]), edge_id(f[1], f[2]), edge_id(f[0], f[2])] for f in fc])
allf = np.concatenate([T[:, fc[k]] for k in range(4)]); allm = np.concatenate([T[:, fm[k]] for k in range(4)])
key = np.sort(allf, 1); _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
bnd = cnt[inv.ravel()] == 1; BF, BM = allf[bnd], allm[bnd]
P0, P1, P2 = X[BF[:, 0]], X[BF[:, 1]], X[BF[:, 2]]; area = np.linalg.norm(np.cross(P1 - P0, P2 - P0), axis=1) / 2
cen = (P0 + P1 + P2) / 3
rr = np.hypot(cen[:, 1], cen[:, 2]); onbore = (rr > BORE - 0.06) & (rr < BORE + 0.01)
def patch_load(sel, wts, total, comp):
    f = np.zeros(n); wa = area[sel] * wts; wa *= total / wa.sum()
    for k in range(3): np.add.at(f, 3 * BM[sel, k] + comp, wa / 3)
    return f
clip = (np.abs(cen[:, 2] - ZB) < 1e-3) & (cen[:, 0] > XC - 7.5) & (cen[:, 0] < XC + 7.5)
fixed_nodes = np.unique(np.r_[BF[clip].ravel(), BM[clip].ravel()])
def halfw(q): return np.sqrt(4 * q * (1 / (1 / RS - 1 / BORE)) / (np.pi * ES))
def band(sel, b):
    yy = cen[:, 1]; keep = sel & (np.abs(yy) < b); bb = b if np.isscalar(b) else b[keep]
    return keep, np.sqrt(np.clip(1 - (yy[keep] / bb) ** 2, 0.05, 1)) / bb
floor = onbore & (cen[:, 0] < STUB) & (cen[:, 2] < -1.5)
htop = onbore & (cen[:, 2] > 1.5) & (cen[:, 0] > XH0) & (cen[:, 0] < XE)
start = htop & (cen[:, 0] < XH0 + 2.5); end = htop & (cen[:, 0] > XE - 2.5)
XB = STUB / 2; MB = Fc * (XB - XC)                      # moments about the floor reaction's centroid, so the held clip carries no moment
P_start = MB / (XH0 + 1.25 - XB); P_end = MB / (XE - 1.25 - XB)
k = MB / ((XE ** 3 - XH0 ** 3) / 3 - XB * (XE ** 2 - XH0 ** 2) / 2); P_spr = k * (XE ** 2 - XH0 ** 2) / 2   # p(x) = k x over XH0..XE (rigid tilt)
cases = {}
for nm, sel, P, wx in (("start", start, P_start, None), ("end", end, P_end, None), ("spread", htop, P_spr, True)):
    if wx: s2, w2 = band(sel, halfw(k * np.maximum(cen[:, 0], XH0 + 0.1))); w2 = w2 * cen[s2, 0]
    else: s2, w2 = band(sel, halfw(P / 2.5))
    fs, wf = band(floor, halfw((Fc + P) / STUB))
    cases[nm] = (patch_load(s2, w2, P, 2) + patch_load(fs, wf, -(Fc + P), 2), P, s2, fs)
print(f"clip {Fc:.0f} N at x {XC:.0f} (moment {M/1000:.2f} N m); hook loads: start {P_start:.0f}, end {P_end:.0f}, spread {P_spr:.0f} N; "
      f"patches: clip {clip.sum()}, start {cases['start'][2].sum()}, end {cases['end'][2].sum()}, spread {cases['spread'][2].sum()}, floor {cases['start'][3].sum()}", flush=True)
fixed = (3 * fixed_nodes[:, None] + np.arange(3)).ravel(); free = np.setdiff1d(np.arange(n), fixed)
Kf = K[free][:, free].tocsr(); xyz = X[free // 3]; comp = free % 3
Bn = np.zeros((len(free), 6))
for c in range(3): Bn[comp == c, c] = 1
x_, y_, z_ = xyz.T
Bn[comp == 1, 3] = -z_[comp == 1]; Bn[comp == 2, 3] = y_[comp == 2]; Bn[comp == 0, 4] = z_[comp == 0]; Bn[comp == 2, 4] = -x_[comp == 2]
Bn[comp == 0, 5] = -y_[comp == 0]; Bn[comp == 1, 5] = x_[comp == 1]
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
t0 = time.time(); ml = pyamg.smoothed_aggregation_solver(Kf, B=Bn, smooth=None, max_coarse=1000)
print(f"AMG setup {time.time()-t0:.0f}s, peak RSS {rss():.1f} GB", flush=True)
Bc = Bmat(dNdx(Xe, dN(np.full(3, 0.25)))[0])
ec = Xe[:, :4].mean(1)
YI = TW.YI
dc1 = np.hypot(ec[:, 0] - J0, ec[:, 1] - YI); dc2 = np.hypot(ec[:, 0] - XH0, ec[:, 1] - YI)     # distance to the two sharp inside edges
zones = {"body over the clip (x < 0)": ec[:, 0] < 0,
         "stub sleeve (x 0 .. J0-1)": (ec[:, 0] >= 0) & (ec[:, 0] < J0 - 1),
         "bare front wall (x J0+0.5 .. XH0-0.5)": (ec[:, 0] > J0 + 0.5) & (ec[:, 0] < XH0 - 0.5),
         "hook (x XH0+0.5 .. end)": ec[:, 0] > XH0 + 0.5}
corners = {"sleeve-end inside edge (x J0, y YI)": dc1, "hook-start inside edge (x XH0, y YI)": dc2}
rb = np.hypot(ec[:, 1], ec[:, 2]); ang = np.degrees(np.arctan2(ec[:, 2], ec[:, 1]))
curl = (ec[:, 0] > XH0 + 0.5) & (ec[:, 0] < XE) & (rb < BORE + 0.6) & (ang > 100) & (ang < 150)   # the curl's inner face, front-top
out = {}
for name, (f, P, _, _) in cases.items():
    t0 = time.time(); res = []
    u = ml.solve(f[free], tol=1e-6, accel="cg", maxiter=1500, residuals=res)
    U = np.zeros(n); U[free] = u
    S = np.einsum("kl,elj,ej->ek", D, Bc, U[dofs])
    s1 = np.linalg.eigvalsh(np.stack([np.stack([S[:, 0], S[:, 3], S[:, 5]], -1), np.stack([S[:, 3], S[:, 1], S[:, 4]], -1),
                                      np.stack([S[:, 5], S[:, 4], S[:, 2]], -1)], -2))
    tl = np.hypot(S[:, 3], S[:, 4])                       # shear on the layer planes (normal y)
    print(f"== hook load at the {name}: {P:.0f} N; {len(res)} it, rel res {res[-1]/res[0]:.1e}, {time.time()-t0:.0f}s; max uz {U[2::3].max():.3f} at {np.round(X[np.argmax(U[2::3])], 1)} / min {U[2::3].min():.3f} mm")
    near_load = cKDTree(np.r_[cen[cases[name][2]], cen[cases[name][3]]]).query(ec, distance_upper_bound=2.0)[0] < 2.0
    for zn, dd in corners.items():
        for r0 in (0.5, 1.0):
            sel = (dd > r0 - 0.15) & (dd < r0 + 0.15) & ~near_load
            if sel.any(): print(f"   {zn}, {r0:g} mm from it: max tension {s1[sel, 2].max():5.1f}, across layers (syy) {S[sel, 1].max():5.1f}, shear between layers {tl[sel].max():5.1f}")
    sel = curl & ~near_load
    if sel.any():
        i1 = np.argmax(np.where(sel, s1[:, 2], -1e9)); iy = np.argmax(np.where(sel, S[:, 1], -1e9))
        print(f"   curl inner face 100-150 deg, away from contacts: max tension {s1[i1, 2]:5.1f} at {np.round(ec[i1], 1)}; syy {S[iy, 1]:5.1f} at {np.round(ec[iy], 1)}")
    for zn, sel in zones.items():
        sel = sel & (dc1 > 0.4) & (dc2 > 0.4)
        for lab, s2 in (("away from contacts and edges", sel & ~near_load), ("at contacts", sel & near_load)):
            if not s2.any(): continue
            i1 = np.argmax(np.where(s2, s1[:, 2], -1e9)); iy = np.argmax(np.where(s2, S[:, 1], -1e9)); it = np.argmax(np.where(s2, tl, -1e9))
            print(f"   {zn}, {lab}: max tension {s1[i1, 2]:5.1f} at {np.round(ec[i1], 1)}; across layers (syy) {S[iy, 1]:5.1f} at "
                  f"{np.round(ec[iy], 1)}; shear between layers {tl[it]:5.1f} at {np.round(ec[it], 1)}")
    out[name] = dict(S=S, s1=s1, P=P, U=U)
import pickle; pickle.dump(dict(X=X, T=T, ec=ec, d=d, fw=FW, fy=FY, hh=HH, out=out), open(os.path.join(HERE, f"front_twist_tet{TAG}.pkl"), "wb"))
print(f"peak RSS {rss():.1f} GB")

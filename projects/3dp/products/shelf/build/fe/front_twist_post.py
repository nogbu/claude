"""Hot spots in a twist-lock 3D check (front_twist_tet.py pickles), for reading a variant whose shape the run's own zones don't cover
(e.g. the raised hook's new inside edge where the raise starts). Per load case: the hook's lift (largest uz on the hook, and at the
hook's inner top where the rod bears), the inside edge where the raise starts (x hx0, z TOP) read 0.5 and 1 mm from it, and the five
highest tensions at least 2 mm apart, away from the rod contacts (within 2 mm of the run's Hertz load bands on the bore's top over the hook and its floor at
the rod end) and 0.4 mm clear of the sharp inside edges the run already reads. Inference, like the run.
and the bore front's profile into the load bands (profile()).
Usage: python3 front_twist_post.py pkl [pkl ...]. Written 2026-10-11 (shelf thread, open decision 9)."""
import importlib.util, os, sys, pickle, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ftm", os.path.join(HERE, "..", "front-twist_model.py"))
TW = importlib.util.module_from_spec(spec); spec.loader.exec_module(TW)
B, J0, XH0, YI, TOP = TW.BORE, TW.J0, TW.XH0, TW.YI, TW.TOP
from scipy.spatial import cKDTree
ES = 1900.0 / (1 - 0.38 ** 2); FC = 15 * 4.448 * 3
def halfw(q): return np.sqrt(4 * q * (1 / (1 / 2.95 - 1 / B)) / (np.pi * ES))                    # front_twist_tet.py halfw()
def bands(D, case):
    """Points on the run's Hertz load bands for a case: the bore top over the hook and the floor at the rod end (front_twist_tet.py)."""
    d = D["d"]; XE = d["XH1"] - TW.LEAD; o = D["out"][case]
    lo, hi = {"start": (XH0, XH0 + 2.5), "end": (XE - 2.5, XE), "spread": (XH0, XE)}[case]
    q = o["P"] / 2.5 if case != "spread" else o["P"] / ((XE ** 2 - XH0 ** 2) / 2) * XE        # line load (N/mm) at the band's widest
    b, bf = halfw(q), halfw((FC + o["P"]) / 2.5)                                                   # Hertz half-widths, as the run's bands
    return np.array([(x, B * np.cos(a), B * np.sin(a)) for x in np.arange(lo, hi + 0.01, 0.25) for a in np.linspace(0, np.pi, 91) if B * np.sin(a) > 1.5 and abs(B * np.cos(a)) < b] + \
          [(x, B * np.cos(a), -B * np.sin(a)) for x in np.arange(0, 2.51, 0.25) for a in np.linspace(0, np.pi, 91) if B * np.sin(a) > 1.5 and abs(B * np.cos(a)) < bf])
def profile(D, case):
    """Largest tension per 1 mm x slab on the bore's front (the curl root: within 0.6 of the bore or the wall's inner face, z -1..1.6), x 14..34,
    each (x, tension, within 2 mm of a load band): a readout that excludes the bands can land on their edge while the stress keeps
    rising into them (independent check 2026-10-10), so profile it before quoting a start-load peak."""
    ec = D["ec"]; t = D["out"][case]["s1"][:, 2]; rb = np.hypot(ec[:, 1], ec[:, 2])
    depth = np.where(ec[:, 2] >= 0, rb - B, -B - ec[:, 1])
    reg = (depth > -0.01) & (depth < 0.6) & (ec[:, 1] < -1.5) & (ec[:, 2] > -1.0) & (ec[:, 2] < 1.6) & (ec[:, 0] > XH0 + 0.4)
    dl = cKDTree(bands(D, case)).query(ec)[0]; out = []
    for x0 in np.arange(14.0, 34.0, 1.0):
        sl = reg & (ec[:, 0] >= x0) & (ec[:, 0] < x0 + 1)
        if sl.any(): i = np.flatnonzero(sl)[np.argmax(t[sl])]; out.append((x0, t[i], dl[i] < 2.0))
    return out
def hot(D, case, n=5, xmin=None):
    """(spots, edge): the n highest tensions at least 2 mm apart away from the contacts and sharp edges, each
    (tension, across layers, shear between layers, element center), and the raise-start edge readings {0.5: (...), 1.0: (...)};
    xmin: only elements past that x (e.g. the hook)."""
    X, ec, d = D["X"], D["ec"], D["d"]; hh = D.get("hh", 0.0); hx0 = d.get("hx0", XH0)
    XE = d["XH1"] - TW.LEAD; rb = np.hypot(ec[:, 1], ec[:, 2]); o = D["out"][case]
    edges = (np.hypot(ec[:, 0] - J0, ec[:, 1] - YI) < 0.4) | (np.hypot(ec[:, 0] - XH0, ec[:, 1] - YI) < 0.4)
    yhi = YI if hx0 > J0 - 0.01 else d["OR"]                          # where the raise starts over the bare front wall, the edge runs only in front of the crosswire
    dr = np.where((ec[:, 1] > d["YF"]) & (ec[:, 1] < yhi), np.hypot(ec[:, 0] - hx0, ec[:, 2] - TOP), 99) if hh else np.full(len(ec), 99.0)
    S, s1 = o["S"], o["s1"]; tl = np.hypot(S[:, 3], S[:, 4]); ten = s1[:, 2]
    near = cKDTree(bands(D, case)).query(ec, distance_upper_bound=2.0)[0] < 2.0                  # within 2 mm of the load patches, as the run
    edge = {}
    for r0 in (0.5, 1.0):
        sel = (dr > r0 - 0.15) & (dr < r0 + 0.15) & ~near & ~edges
        if sel.any(): edge[r0] = (ten[sel].max(), S[sel, 1].max(), tl[sel].max())
    ok = ~near & ~edges & (dr > 0.4) & (ec[:, 0] > (-1e9 if xmin is None else xmin)); idx = np.flatnonzero(ok)[np.argsort(-ten[ok])]; picked = []
    for i in idx:
        if all(np.linalg.norm(ec[i] - ec[j]) > 2.0 for j in picked): picked.append(i)
        if len(picked) == n: break
    return [(ten[i], S[i, 1], tl[i], ec[i]) for i in picked], edge

if __name__ == "__main__":
  for pk in sys.argv[1:]:
    D = pickle.load(open(pk, "rb")); X, d = D["X"], D["d"]; hh = D.get("hh", 0.0); hx0 = d.get("hx0", XH0); XE = d["XH1"] - TW.LEAD
    print(f"== {os.path.basename(pk)}: raise {hh:g} from x {hx0:g}")
    hook_top_nodes = (X[:, 0] > XH0) & (X[:, 0] < XE) & (np.abs(np.hypot(X[:, 1], X[:, 2]) - B) < 0.05) & (X[:, 2] > B - 0.2)
    for case, o in D["out"].items():
        U = o.get("U"); line = f"  {case} ({o['P']:.0f} N):"
        if U is not None:
            uz = U[2::3]; hk = X[:, 0] > XH0
            line += f" lift: hook max {uz[hk].max():.2f} at {np.round(X[hk][np.argmax(uz[hk])], 1)}, at the rod's bearing line {uz[hook_top_nodes].max():.2f}"
        print(line); spots, edge = hot(D, case)
        for r0, (t, sy, sh) in edge.items():
            print(f"    raise-start edge (x {hx0:g}, z TOP), {r0:g} mm: max tension {t:5.1f}, across layers {sy:5.1f}, shear between layers {sh:5.1f}")
        for t, sy, sh, c in spots:
            print(f"    hot spot {t:5.1f} tension, {sy:5.1f} across layers, {sh:5.1f} shear between layers at {np.round(c, 1)}")
        print("    bore front, x slab: " + " ".join(f"{x:.0f}:{t:.0f}{'*' if nb else ''}" for x, t, nb in profile(D, case)) + "  (* within 2 mm of a load band)")

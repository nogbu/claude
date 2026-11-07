import sys, pickle, numpy as np, shapely
from shapely.geometry import box as B, Point
d = pickle.load(open(sys.argv[1], "rb"))
P, T, X = d["P"], d["T"], d["X"]; c = P[T].mean(1); FRONT = d.get("FRONT", -3.55); TOP = 5.7; C = 0.3; RT = d["RT"]; OF = d["OF"]
A = 0.5 * np.abs((P[T[:,1],0]-P[T[:,0],0])*(P[T[:,2],1]-P[T[:,0],1])-(P[T[:,2],0]-P[T[:,0],0])*(P[T[:,1],1]-P[T[:,0],1]))
fil = d.get("fil", 0.6)
corner = B(FRONT - 0.15, 6.0 - float(sys.argv[2]) - 0.3 if len(sys.argv) > 2 else 5.2, FRONT + (float(sys.argv[2]) if len(sys.argv) > 2 else 0.6) + 0.2, 6.05)             # fillet zone
cz = shapely.contains_xy(corner, c[:, 0], c[:, 1])
sec_b = shapely.Polygon(P[np.unique(T)][:0]) if False else None
print(f"model fw {d['fw']} tr {d['tr']} tz {d['tz']}")
for ci, name in enumerate(d["names"]):
    best = {}
    for k, Ss in d["layers"].items():
        S = Ss[ci]; xm = (X[k] + X[k + 1]) / 2
        syy, szz, tyz = S[:, 1], S[:, 2], S[:, 4]
        s1 = (syy + szz) / 2 + np.sqrt(((syy - szz) / 2) ** 2 + tyz ** 2)
        for key, v in (("syy corner", syy), ("szz corner", szz), ("s1(yz) corner", s1)):
            vv = np.where(cz, v, -1e9); j = np.argmax(vv)
            if key not in best or vv[j] > best[key][0]: best[key] = (vv[j], xm, c[j, 0], c[j, 1])
        # nominal resultants: roof sigma_yy on the strip y in [-2.95, -2.85] (fillet end), wall sigma_zz on z in [4.2, 4.4]
        for key, sel, comp, axis in (("roof m @y-2.9", (c[:, 0] > -2.95) & (c[:, 0] < -2.85) & (c[:, 1] > 5.9), 1, 1),
                                     ("wall m @z4.3", (c[:, 1] > 4.2) & (c[:, 1] < 4.4) & (c[:, 0] < FRONT), 2, 0)):
            w = A[sel] / (0.1 if axis == 1 else 0.2)                 # strip widths: integrate per unit length of the cut
            coord = c[sel, axis]; lo, hi = (6.0, 9.1) if axis == 1 else (-OF, FRONT); t = hi - lo; mid = (lo + hi) / 2
            n = (S[sel, comp] * w).sum(); mm = (S[sel, comp] * (coord - mid) * w).sum()
            snom = n / t + (-1 if axis == 1 else 1) * 6 * mm / t ** 2 * (1 if axis == 0 else 1)
            sb = n / t - 6 * mm / t ** 2 if axis == 1 else n / t + 6 * mm / t ** 2
            if key not in best or sb > best[key][0]: best[key] = (sb, xm, n, mm)
    print(f"== {name}")
    for key, v in best.items():
        if "corner" in key: print(f"   peak {key:14s} {v[0]:6.1f} MPa at x {v[1]:.2f}, (y {v[2]:.3f}, z {v[3]:.3f})")
        else: print(f"   nominal {key:13s} {v[0]:6.1f} MPa at x {v[1]:.2f} (n {v[2]:.1f} N/mm, m {v[3]:.1f} N*mm/mm)")
for k, v in d["uz_underside"].items(): print(k, round(v, 3))

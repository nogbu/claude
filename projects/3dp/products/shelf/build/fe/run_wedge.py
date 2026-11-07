"""One 3D run (about 5 min, 4 CPUs): python3 run_wedge.py fw tr tz h0 fillet roof -> wedge4_*.pkl; read with post_wedge.py. Needs pyamg (pip install pyamg)."""
import sys, pickle, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fe_wedge as W
fw, tr, tz, h0, fil, roof = map(float, sys.argv[1:7])
W.ROOF = roof
m = W.WModel(fw, tr, tz, h0=h0, fil=fil); m.assemble(); RT = m.RT
cases = {"tip 37.3": m.roof_load(37.3, 0.6, RT - 0.3, RT, 187.0)}
U = m.solve(list(cases.values()))
ks = [k for k in range(len(m.X) - 1) if 35.5 < (m.X[k] + m.X[k + 1]) / 2 < 39.5]
out = dict(names=list(cases), P=m.P, T=m.T, X=m.X, OF=m.OF, RT=RT, fw=fw, tr=tr, tz=tz, roof=roof,
           layers={k: [m.stress_layer(u, k) for u in U] for k in ks}, uz_underside={})
pickle.dump(out, open(f"wedge4_{fw}_{fil}_{roof}.pkl", "wb")); print("saved", flush=True)

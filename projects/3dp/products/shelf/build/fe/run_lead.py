"""3D check of the open decision 2 lead root (about 5 min, 4 CPUs): front wall a mm in front of the wire ends, fillet r, overlap ov.
python3 run_lead.py a fil ov [fw roof] -> lead_*.pkl; read with post_wedge.py <pkl> <fil>. Needs pyamg. Written 2026-10-09 (shelf thread)."""
import sys, pickle, functools
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fe_wedge as W
a, fil, ov = map(float, sys.argv[1:4]); fw, roof = (map(float, sys.argv[4:6]) if len(sys.argv) > 5 else (2.4, 3.10))
W.ROOF = roof
W.FRONT = -W.ROD - a
W.section = functools.partial(W.section, ov=ov)
m = W.WModel(fw, 2.35, 2.48, fil=fil); m.assemble(); RT = m.RT
cases = {"spread": m.roof_load(37.3, 0.6, -W.ROD + 0.1, RT, 187.0), "tip": m.roof_load(37.3, 0.6, RT - 0.3, RT, 187.0)}
U = m.solve(list(cases.values()))
ks = [k for k in range(len(m.X) - 1) if 35.5 < (m.X[k] + m.X[k + 1]) / 2 < 39.5]
out = dict(names=list(cases), P=m.P, T=m.T, X=m.X, OF=m.OF, RT=RT, fw=fw, roof=roof, tr=2.35, tz=2.48, fil=fil, FRONT=W.FRONT,
           layers={k: [m.stress_layer(u, k) for u in U] for k in ks}, uz_underside={})
pickle.dump(out, open(f"lead_{a}_{fil}_{ov}_{fw}_{roof}.pkl", "wb")); print("saved", flush=True)

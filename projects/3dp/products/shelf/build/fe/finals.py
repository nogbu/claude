"""Finalists on 3 meshes each (mesh noise of the element-max metric), cases spread/tip/mid/spread295, 187 N (inference)."""
import json, sys, numpy as np, explore
CFG = json.loads(sys.argv[1]); out = []
for cfg in CFG:
    runs = []
    for h0 in (0.017, 0.02, 0.024):
        r = explore.evaluate(h0=h0, cases=("spread", "tip", "mid", "spread295"), **cfg); runs.append(r)
    s = f"{json.dumps(cfg):70s} clr {runs[0]['clear']['fill_to_wire']:.3f} load y0 " + ",".join(f"{q['loadspan']['spread'][0]:.2f}" for q in runs) + " |"
    agg = {}
    for c in ("spread", "tip", "mid", "spread295"):
        A = np.array([q[c]["across"] for q in runs]); L = np.array([q[c]["along"] for q in runs]); F = np.array([q[c]["floor_szz"] for q in runs])
        agg[c] = dict(across=A.tolist(), along=L.tolist(), floor=F.tolist())
        s += f" {c} {A.mean():5.1f}({A.min():.0f}-{A.max():.0f})/{L.mean():5.1f}({L.min():.0f}-{L.max():.0f}) fl{F.mean():.0f} |"
    print(s, flush=True); out.append(dict(cfg=cfg, agg=agg, clear=runs[0]["clear"], OF=runs[0]["OF"], RT=runs[0]["RT"], yt=runs[0]["yt"], zlo=runs[0]["zlo"]))
json.dump(out, open(sys.argv[2], "w"), indent=1, default=float)

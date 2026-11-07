"""Roof-root 2D corner model (c2d.py Fourier prism) calibrated to the 3D runs. Written 2026-10-09. Explore the 'bigger root' family with the Fourier prism, calibrated to 3D: across x1.05 (range 1.00-1.10), along x1.21 (1.17-1.26). Inference."""
import sys, json, time, numpy as np, c2d
KA, KL = 1.05, 1.21
VERB = True
def rmax(a, b, kind="fillet", clr=0.3, **kw):
    lo, hi = 0.05, 4.0
    for _ in range(40):
        m = (lo + hi) / 2
        d = c2d.sec(a, b, kind, r=m, **kw) if kind == "fillet" else None
        if c2d.clearances(d)["fill_to_wire"] >= clr: lo = m
        else: hi = m
    return lo
def evaluate(a, b, kind="fillet", ov=2.0, roof=3.10, fw=2.4, h0=0.02, cases=("spread", "tip", "mid"), P=187.0, rf=0.0, **kw):
    t = time.time()
    d = c2d.sec(a, b, kind, ov=ov, roof=roof, fw=fw, rf=rf, **kw); cl = c2d.clearances(d)
    Pm, Tm = c2d.mesh(d, h0=h0, focus="root")
    cs = c2d.std_cases(d, cases)
    fo = c2d.fourier2(d, Pm, Tm, cs, Ptot=P, xs=(-0.15, 0.0, 0.15))
    res = dict(a=a, b=b, kind=kind, kw=kw, rf=rf, ov=ov, roof=roof, fw=fw, h0=h0, P=P, OF=d["OF"], RT=d["RT"], zR=d["zR"],
               yt=float(max(p[0] for p in d["root"].coords)) if not d["fill"].is_empty else d["FRONT"],
               zlo=float(min(p[1] for p in d["root"].coords)) if not d["fill"].is_empty else d["zR"], clear=cl, ntri=len(Tm))
    for c in cases:
        f = fo[c]
        res[c] = dict(across=KA * f["across_root"][0], across_arc=KA * f["across_arc"][0], along=KL * f["along"][0],
                      at_across=f["across_root"][1], at_along=f["along"][1], floor_szz=KL * f["floor_szz"][0], floor_syy=KA * f["floor_syy"][0])
    res["loadspan"] = dict(c2d.LOADSPAN)
    res["sec"] = time.time() - t
    return res
def show(r):
    kw = ",".join(f"{k}{v:.3g}" for k, v in r["kw"].items())
    s = f"a {r['a']:.2f} b {r['b']:.2f} {r['kind']}({kw}) ov{r['ov']} h{r['h0']} rf{r.get('rf', 0)} | clr {r['clear']['fill_to_wire']:.3f} vgap@end {r['clear']['vgap_at_end']:.3f} yt {r['yt']:.2f} zlo {r['zlo']:.2f} |"
    for c in ("spread", "tip", "mid"):
        if c in r: s += f" {c} {r[c]['across']:5.1f}/{r[c]['along']:5.1f}" + (f" @{r[c]['at_across']}/{r[c]['at_along']} fl {r[c]['floor_szz']:.0f}/{r[c]['floor_syy']:.0f}" if VERB else "")
    return s + f" | {r['sec']:.0f}s"
if __name__ == "__main__":
    out = []
    configs = json.loads(sys.argv[1])
    for cfg in configs:
        r = evaluate(**cfg); out.append(r); print(show(r), flush=True)
    fn = sys.argv[2] if len(sys.argv) > 2 else "explore_out.json"
    old = json.load(open(fn)) if __import__("os").path.exists(fn) else []
    json.dump(old + out, open(fn, "w"), indent=1, default=float)

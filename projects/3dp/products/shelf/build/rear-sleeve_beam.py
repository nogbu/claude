"""Beam sizing of the rear piece's lip-rod sleeve (agreed changes 27, 28), inference throughout.
Load: 15 lb x 3 per corner (agreed change 11) at the clip center x -37 (rear-piece_model X0 + 8); moments about the stub ends (x 0).
Tip case: the lip rod bears on the sleeve top at its end; spread case: bearing grows linearly with x from the sleeve root (rigid tilt).
Section: the model's sleeve (rear wall closed below the wire ends, upper lip trimmed) cut across, bending about its own centroid.
PETG Basic V3.0 bending 75 along / 56 across the layers; printed on its side (front face down), this bending runs along the layers.
Contact: Hertz line contact of the rod (ROD) in the bore (BORE), steel on PETG; b/R over about 0.5 makes Hertz approximate.
options(reach) gives one reach's loads, stresses, contact and solid grams (density 1.25, OrcaSlicer's Bambu PETG Basic profile).
Usage: python3 rear-sleeve_beam.py [tz ttop tr]"""
import importlib.util, os, sys, numpy as np, shapely
from shapely.geometry import box as B, Point
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
CLOSE = -1.75; DENS = 1.25e-3                                     # agreed change 28; g per mm3
Fc = 15 * 4.448 * 3; XC = RP.X0 + 8.0; M = Fc * -XC; J0 = RP.J0
Es = 1950.0; Er = 200e3; nu = 0.38; Estar = 1 / ((1 - nu ** 2) / Es + (1 - 0.3 ** 2) / Er)
Rst = RP.ROD * RP.BORE / (RP.BORE - RP.ROD)
def section(tz=2.48, ttop=2.48, tr=2.35):
    _, d = RP.build(tz=tz, ttop=ttop, tr=tr, close_below=CLOSE, trim=True)
    dz = RP.bore_z(d["rear"] - RP.F.BEAD)
    sec = (B(d["yf"], d["zb"], d["rear"], d["zt"]).union(B(d["rear"], d["zb"], d["yr"], RP.LIPB + CLOSE))
           .difference(Point(0, RP.LIPB).buffer(RP.BORE, 256)).difference(B(d["rear"] - RP.F.BEAD, RP.LIPB + CLOSE, d["rear"] + 1, RP.LIPB + dz)))
    g = np.mgrid[d["yf"]:d["yr"]:0.01, d["zb"]:d["zt"]:0.01].reshape(2, -1).T + 0.005
    z = g[shapely.contains_xy(sec, g[:, 0], g[:, 1]), 1]; zc = z.mean()
    return sec, d, ((z - zc) ** 2).sum() * 1e-4, max(d["zt"] - zc, zc - d["zb"])
def hertz(q):                                                     # q N/mm -> half-width b, peak pressure p0
    b = np.sqrt(4 * q * Rst / (np.pi * Estar)); return b, 2 * q / (np.pi * b)
def options(reach, tz=2.48, ttop=2.48, tr=2.35):
    sec, d, I, c = section(tz, ttop, tr); P = M / reach; Mr = P * (reach - J0)
    piece, _ = RP.build(reach=reach, tz=tz, ttop=ttop, tr=tr, close_below=CLOSE, trim=True)
    return dict(reach=reach, P=P, stubs=Fc + P, Mr=Mr, root=Mr * c / I, tip25=hertz(P / 2.5), tip15=hertz(P / 1.5),
                stub=hertz((Fc + P) / 10.0), grams=piece.volume() * DENS)
if __name__ == "__main__":
    tz, ttop, tr = (map(float, sys.argv[1:4]) if len(sys.argv) > 3 else (2.48, 2.48, 2.35))
    sec, d, I, c = section(tz, ttop, tr)
    print(f"Sleeve section: {sec.bounds[2]-sec.bounds[0]:.2f} wide x {d['zt']-d['zb']:.2f} deep, A {sec.area:.1f} mm2, I {I:.0f} mm4, c {c:.2f}")
    print(f"Clip {Fc:.0f} N at x {XC:.0f}: tipping {M/1000:.2f} N*m")
    print(f"{'reach':>6} {'case':>7} {'P up N':>7} {'stubs N':>8} {'root M N*m':>10} {'root MPa':>9} {'contact MPa':>11}")
    for R in (20.0, 25.0, 30.0, 40.0):
        for case in ("tip", "spread"):
            if case == "tip":
                P = M / R; Mr = P * (R - J0); q = P / 2.5
            else:
                k = 3 * M / (R ** 3 - J0 ** 3); P = k * (R ** 2 - J0 ** 2) / 2; Mr = M - J0 * P; q = k * R
            print(f"{R:6.0f} {case:>7} {P:7.0f} {Fc + P:8.0f} {Mr/1000:10.2f} {Mr * c / I:9.1f} {hertz(q)[1]:11.0f}")
    print(f"\n{'reach':>6} {'grams':>6} {'tip p0 (2.5 / 1.5 mm)':>22} {'b/R':>5} {'stub p0':>8}")
    for R in (20.0, 25.0, 30.0, 40.0):
        o = options(R, tz, ttop, tr)
        print(f"{R:6.0f} {o['grams']:6.2f} {o['tip25'][1]:10.0f} / {o['tip15'][1]:4.0f} {o['tip15'][0] / RP.BORE:5.2f} {o['stub'][1]:8.0f}")

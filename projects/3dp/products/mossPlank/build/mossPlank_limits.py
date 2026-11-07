"""mossPlank height limits (inference): bending stress at the body and spigot sections, and pot tipping."""
import math
from shapely.geometry import Point, box
r0 = 39.33797346008349; r1 = 44.883; W = 60.0; d = math.sqrt(r0**2 - 900) - 15.0
a = 1.24 / math.cos(math.radians(5.03)); F2, S1, G = 2.0, 1.24, 0.2
def outline(off, front, side):
    return box(-W / 2 + side, d + front, W / 2 - side, 200).intersection(Point(0, 0).buffer(r1 - off, 720))
body = outline(0, 0, 0).difference(outline(a, F2, S1))
spig = outline(a + G, F2 + G, S1 + G).difference(outline(a + G + S1, F2 + G + S1, S1 + G + S1))
def props(p):
    # second moments about the centroid, by triangulating the polygon boundary (Green's theorem on rings)
    cx, cy = p.centroid.x, p.centroid.y
    def ring(c):
        Ix = Iy = 0.0; pts = list(c.coords)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            x0 -= cx; x1 -= cx; y0 -= cy; y1 -= cy; k = x0 * y1 - x1 * y0
            Ix += (y0 * y0 + y0 * y1 + y1 * y1) * k; Iy += (x0 * x0 + x0 * x1 + x1 * x1) * k
        return Ix / 12, Iy / 12
    Ix, Iy = ring(p.exterior)
    for h in p.interiors:
        a_, b_ = ring(h); Ix += a_; Iy += b_
    Ix, Iy = abs(Ix), abs(Iy)
    minx, miny, maxx, maxy = p.bounds
    cyd = max(maxy - cy, cy - miny); cxd = max(maxx - cx, cx - minx)
    return p.area, Ix / cyd, Iy / cxd           # area, section modulus for a front-back lean, for a sideways lean
for n, p in [("body", body), ("spigot", spig)]:
    A, Sfb, Ss = props(p); print(n, "A %.0f mm2  S front-back %.0f mm3  S sideways %.0f mm3" % (A, Sfb, Ss))
A, Sfb, Ss = props(spig); Smin = min(Sfb, Ss)
allow = 48.0                                     # MPa across layers (Bambu PETG HF data sheet, config.3dp)
for sf in (2, 3):
    for kg in (0.5, 1, 2):
        L = allow / sf * Smin / (kg * 9.81)
        print("SF %d, %.1f kg: lever above the lowest joint up to %.0f mm" % (sf, kg, L))
W_pot, R6 = 2.5, 52.7
for top in (248, 448, 648, 848):
    print("plank top %d mm: pot tips at %.2f kg sideways at the top" % (top, W_pot * R6 / top))

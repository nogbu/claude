"""hookGauge_rev1 build script (unicoly-rail). Self-contained: geometry helpers + gauge.
Frame: x=depth (0=rail back face, negative=behind steel), y=height, w=across rail (prints on w=0).
Run: python3 hookGauge_rev1.py -> out/hook_gauge_*rib_G*.stl
"""

import struct
import numpy as np
from scipy.spatial import HalfspaceIntersection, ConvexHull


def prism_halfspaces(poly_xy, w0, w1, extra=()):
    """Half-spaces (a.p + b <= 0) for a convex CCW polygon in (x,y) extruded over w.
    extra: list of (a_x, a_y, a_w, b) additional cutting planes."""
    hs = []
    n = len(poly_xy)
    for i in range(n):
        (x0, y0), (x1, y1) = poly_xy[i], poly_xy[(i + 1) % n]
        # outward normal of CCW edge is (dy, -dx)
        nx, ny = (y1 - y0), -(x1 - x0)
        L = np.hypot(nx, ny)
        nx, ny = nx / L, ny / L
        hs.append([nx, ny, 0.0, -(nx * x0 + ny * y0)])
    hs.append([0, 0, -1.0, w0])
    hs.append([0, 0, 1.0, -w1])
    hs.extend(extra)
    return np.array(hs, float)


def solid(poly_xy, w0, w1, extra=()):
    hs = prism_halfspaces(poly_xy, w0, w1, extra)
    # find interior point by LP (Chebyshev center)
    from scipy.optimize import linprog
    A = hs[:, :3]
    b = -hs[:, 3]
    norm = np.linalg.norm(A, axis=1)
    res = linprog([0, 0, 0, -1], A_ub=np.hstack([A, norm[:, None]]), b_ub=b,
                  bounds=[(None, None)] * 3 + [(0, None)])
    assert res.success and res.x[3] > 1e-6, "empty solid"
    pts = HalfspaceIntersection(hs, res.x[:3]).intersections
    hull = ConvexHull(pts)
    c = pts.mean(axis=0)
    tris = []
    for s in hull.simplices:
        p = pts[s]
        nrm = np.cross(p[1] - p[0], p[2] - p[0])
        if np.dot(nrm, p[0] - c) < 0:
            p = p[[0, 2, 1]]
        tris.append(p)
    return np.array(tris)


def box(x0, x1, y0, y1, w0, w1, extra=()):
    return solid([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w0, w1, extra)


def to_print_frame(tris):
    x, y, w = tris[..., 0], tris[..., 1], tris[..., 2]
    out = np.stack([y, -x, w], axis=-1)  # proper rotation, det=+1
    return out


def write_stl(path, solids, name="part"):
    tris = np.concatenate([to_print_frame(s) for s in solids])
    tris = tris - tris.reshape(-1, 3).min(axis=0)
    with open(path, "wb") as f:
        f.write(name.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            nrm = np.cross(t[1] - t[0], t[2] - t[0])
            L = np.linalg.norm(nrm)
            nrm = nrm / L if L else nrm
            f.write(struct.pack("<3f", *nrm))
            for v in t:
                f.write(struct.pack("<3f", *v))
            f.write(b"\0\0")
    ext = tris.reshape(-1, 3).max(axis=0)
    return ext

"""Hook gauge: four short rail stubs, one hook each, with different gaps
between the rail back face and the hook's drop (steel thickness + clearance).
Hang each in a slot; the one that seats snug without rattle sets G.
"""

# ---- parameters (mm) ----
RAIL_W = 17.0      # rail width (strip 17.5 - 0.5)
RAIL_D = 10.0      # rail depth
STUB_H = 40.0      # gauge stub height
HOOK_W = 8.5       # across width (slot 9)
SHANK_T = 1.8      # vertical thickness of shank
DROP_L = 1.6       # how far the drop hangs below the shank (lip behind steel)
DROP_T = 2.0       # drop thickness front-to-back
LEAD = 0.5         # lead-in chamfer on the hook's leading corners
HOOK_Y = 30.0      # shank bottom height on the stub
GAPS = [1.0, 1.3, 1.6, 2.0]

w0 = (RAIL_W - HOOK_W) / 2          # 4.25
w1 = w0 + HOOK_W                    # 12.75
# 45 deg print chamfer under the hook: keep w + x >= w0  (x negative behind steel)
CHAMFER = [(-1.0, 0.0, -1.0, w0)]   # -x - w + w0 <= 0


def hook(G, y0=HOOK_Y):
    back = -(G + DROP_T)
    shank = solid([(back, y0), (0.5, y0), (0.5, y0 + SHANK_T),
                   (back + LEAD, y0 + SHANK_T), (back, y0 + SHANK_T - LEAD)],
                  w0, w1, CHAMFER)
    yb = y0 - DROP_L
    drop = solid([(back + LEAD, yb), (-G, yb), (-G, y0 + 0.2),
                  (back, y0 + 0.2), (back, yb + LEAD)],
                 w0, w1, CHAMFER)
    return [shank, drop]


def gauge(G, idx):
    parts = [box(0, RAIL_D, 0, STUB_H, 0, RAIL_W)]
    parts += hook(G)
    # ID ribs on the front face, full width so they print without overhang
    for i in range(idx + 1):
        y = 4 + 2.5 * i
        parts.append(box(RAIL_D - 0.5, RAIL_D + 0.6, y, y + 1.0, 0, RAIL_W))
    return parts


if __name__ == "__main__":
    import os
    os.makedirs("out", exist_ok=True)
    for i, G in enumerate(GAPS):
        p = f"out/hook_gauge_{i+1}rib_G{G:.1f}mm.stl"
        ext = write_stl(p, gauge(G, i), f"hook gauge G={G}")
        print(p, "extents", ext.round(2))

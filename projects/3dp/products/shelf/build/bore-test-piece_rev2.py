"""bore-test-piece_rev2 (shelf, agreed change 13): six blind bores, 6.0-6.5 mm in 0.1 mm steps, in one bar.
Count bores from the chamfered 6.0 end; no pips. Peaked bore roofs (45 deg, flat at z 9.6), 0.6 mm lead-ins.
Needs numpy, shapely, manifold3d, trimesh and shelf_settings_base.json beside it (made by shelf_settings_base.py).
Run: python3 bore-test-piece_rev2.py OUTDIR. Print coords: X along the bar (6.0 end at x=0),
Y along the bores (open end y=0), Z up from the bed; bores horizontal, no supports."""
import json, os, sys
import numpy as np, manifold3d as m, trimesh
from shapely.geometry import Polygon, Point, box as sbox
from shapely.geometry.polygon import orient
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import write3mf as W

LH = 0.3                                   # layer height: every Z value below sits on this grid
SIZES = [6.0, 6.1, 6.2, 6.3, 6.4, 6.5]
PITCH = 12.0; H = 12.0                     # bar 72 x L x 12, bore centers at z 6
BORE = 15.0; END = 2.48; L = BORE + END    # end wall: 4 beads of 0.62 (two wall loops from each side)
ROOF = 9.6                                 # bore roof flat, 32 layers
MARK = 3.9                                 # 45-deg chamfer on the top edge at the 6.0 end, from z 8.1 (27 layers)
LEAD = 0.6                                 # 45-deg lead-in at each bore mouth; its roof flat lands at z 10.2
VENT = 2.4                                 # bottom at z 4.8 (16 layers)
RV = 2.0                                   # vertical corner radius
TOP_R = 0.9                                # top edge fillet (3 layers)
FOOT = 0.9                                 # bed edge 45-deg chamfer (3 layers, elephant foot)
NX = len(SIZES) * PITCH

T22 = np.tan(np.radians(22.5))
FOOT_T = 0.3                               # bed chamfer meets the wall through a fillet ending at z 1.2
MARK_T = 0.6                               # end mark meets the end face through a fillet starting at z 7.5

def blend(z, zc, t):                       # 45-deg turn at height zc, rounded with tangent length t: offset at z
    R = t / T22; z0 = zc + t
    return R - np.sqrt(max(R**2 - (z - z0)**2, 0.0))

def inset(z):                              # how far the outline steps in at height z
    v = 0.0
    if z < FOOT - FOOT_T / np.sqrt(2): v = FOOT - z
    elif z < FOOT + FOOT_T: v = blend(z, FOOT, FOOT_T)
    if z > H - TOP_R:
        d = z - (H - TOP_R); v = TOP_R - np.sqrt(max(TOP_R**2 - d**2, 0.0))
    return v

def mark(z):                               # end-mark offset at the x=0 end (45 deg from z = H - MARK)
    zc = H - MARK
    if z < zc - MARK_T: return 0.0
    if z < zc + MARK_T / np.sqrt(2): return blend(-(z - 2 * zc), zc, MARK_T)   # mirror: the turn bends the other way
    return z - zc

def ring(z, n=24):                         # XY outline at height z: rounded rectangle, same point count at every z
    x0 = mark(z) + inset(z); e = inset(z); r = RV - e
    pts = []
    for cx, cy, a0 in ((NX - RV, RV, -90), (NX - RV, L - RV, 0), (x0 + r, L - RV, 90), (x0 + r, RV, 180)):
        for k in range(n + 1):
            a = np.radians(a0 + 90 * k / n); pts.append((cx + r * np.cos(a), cy + r * np.sin(a), z))
    return np.array(pts)

def loft(rings):                           # closed solid through rings of equal point count, capped at both ends
    R = np.array(rings); nz, n, _ = R.shape
    V = list(R.reshape(-1, 3)) + [R[0].mean(0), R[-1].mean(0)]
    T = []
    for i in range(nz - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            T += [(a, b, b + n), (a, b + n, a + n)]
    c0, c1 = len(V) - 2, len(V) - 1
    for j in range(n):
        T += [(c0, (j + 1) % n, j), (c1, (nz - 1) * n + j, (nz - 1) * n + (j + 1) % n)]
    V = np.array(V, float); T = np.array(T)
    tm = trimesh.Trimesh(V, T, process=False)
    if tm.volume < 0: T = T[:, ::-1]
    return m.Manifold(m.Mesh(vert_properties=V.astype(np.float32), tri_verts=T.astype(np.uint32)))

def outer():
    zs = set(np.linspace(0, FOOT + FOOT_T, 13)) | set(np.linspace(H - TOP_R, H, 13)) | set(np.linspace(H - MARK - MARK_T, H - MARK + 1, 13))
    zs = sorted(z for z in zs | set(np.linspace(FOOT, H - TOP_R, 3)) if 0 <= z <= H)
    return loft([ring(z) for z in zs])

def star(poly, cx, cz, n=360):             # distances from (cx, cz) to poly's edge at n angles
    from shapely.geometry import LineString
    out = []
    for k in range(n):
        a = 2 * np.pi * k / n; far = (cx + 20 * np.cos(a), cz + 20 * np.sin(a))
        hit = LineString([(cx, cz), far]).intersection(poly.exterior)
        pts = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
        out.append(max(np.hypot(q.x - cx, q.y - cz) for q in pts))
    return np.array(out)

def lead_in(prof, cx):                     # 45-deg flare from the bore profile (y = LEAD) to LEAD wider (y = 0)
    n = 360; a = 2 * np.pi * np.arange(n) / n
    r1 = star(prof, cx, 6, n); r0 = star(prof.buffer(LEAD, 64), cx, 6, n)
    rg = lambda r, y: np.stack([cx + r * np.cos(a), np.full(n, y), 6 + r * np.sin(a)], 1)
    return loft([rg(r0 + 0.04, -0.03), rg(r0, 0.0), rg(r1, LEAD), rg(r1 - 0.01, LEAD + 0.01)])

def solid(poly):
    poly = orient(poly, 1.0)
    return m.CrossSection([list(poly.exterior.coords)[:-1]])

def prism_y(poly, y0, y1):                 # XZ polygon extruded along +Y
    s = m.Manifold.extrude(solid(poly), y1 - y0)
    return s.transform([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]])

def bore_profile(cx, d):                   # XZ: circle with a 45-deg peaked roof cut flat at ROOF
    r = d / 2; c = Point(cx, 6).buffer(r, 256)
    t = r / np.sqrt(2); a = r * np.sqrt(2)
    roof = Polygon([(cx - t, 6 + t), (cx, 6 + a), (cx + t, 6 + t), (cx, 6)])
    return c.union(roof).intersection(sbox(cx - 9, 0, cx + 9, ROOF)).simplify(0.001)

def vent_profile(cx):                     # 2 mm vent with a 45-deg peak, so nothing overhangs
    r = VENT / 2; t = r / np.sqrt(2)
    return Point(cx, 6).buffer(r, 64).union(Polygon([(cx - t, 6 + t), (cx, 6 + r * np.sqrt(2)), (cx + t, 6 + t), (cx, 6)]))

def build():
    bar = outer()
    cuts = []
    for i, d in enumerate(SIZES):
        cx = PITCH / 2 + i * PITCH; prof = bore_profile(cx, d)
        cuts += [prism_y(prof, 0.0, BORE), lead_in(prof, cx),
                 prism_y(vent_profile(cx), BORE - 0.5, L + 1)]
    bar = bar - m.Manifold.batch_boolean(cuts, m.OpType.Add)
    mm = bar.to_mesh()
    tm = trimesh.Trimesh(np.array(mm.vert_properties)[:, :3], np.array(mm.tri_verts), process=False)   # merging welds near-touching vertices
    return tm

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    tm = build()
    print("watertight", tm.is_watertight, "volume mm3", round(tm.volume, 1), "size", np.round(tm.extents, 2).tolist())
    for d in SIZES:
        print(f"bore {d}: roof {ROOF - 6 - d/2:.2f} above circle, bridge {2*(d/2*np.sqrt(2)-(ROOF-6)):.2f}, "
              f"bottom {6 - d/2:.2f} above bed")
    s = json.load(open(os.path.join(HERE, "shelf_settings_base.json")))
    name = "bore-test-piece_rev2"
    tm.export(os.path.join(out, name + ".stl"))
    W.write(os.path.join(out, name + ".3mf"), [W.Obj(name, [W.Part(tm.vertices, tm.faces)], at=[(128, 128)])], s)
    print("wrote", os.path.join(out, name + ".3mf"))

"""nurseryPots_lib.py - shared build library for the nursery-pots family (3dp project).

Builds the self-watering pots and their inserts as watertight meshes and packages
each one as an OrcaSlicer 2.4.2 3mf with the project's settings, object settings,
height-range modifiers, fan-ramp G-code and the painted seam strip.

Needs beside it: nurseryPots_settings_base.json (the pot files' project_settings.config).
Needs: numpy, scipy (Delaunay for the insert ceilings), matplotlib (thumbnails only).

Geometry conventions (see nursery-pots state.md, "Shared design", and log.md, "Measured geometry and 4.5in/6in derivation"):
- Surfaces of revolution with 720 segments (0.5 deg). z = 0 is the bed.
- Pot: the inner surface is the outer surface moved inward horizontally by the wall
  thickness. Slots are stadium-shaped with parallel straight sides, centered at
  22.5 + n*45 deg so a slot midpoint faces +Y (90 deg).
- Insert: printed ceiling-down, so z = 0 is the ceiling's outer face. Side notches
  at 0/90/180/270 deg are open at the rim. Radial slots, diagonal holes and the
  ceiling-edge chamfer and curve are in the ceiling.
- Vertices are written with z centered (z - H/2); the build item is translated by
  (128, 128, H/2), as Orca does.
"""
import json, math, os, uuid, zipfile, io, datetime
from collections import defaultdict
import numpy as np

SEG = 720
STEP = 360.0 / SEG
EPS_DEG = 0.05
HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------------- mesh
class Mesh:
    def __init__(self):
        self.V = []
        self.T = []
        self.tag = []

    def add(self, x, y, z):
        self.V.append((float(x), float(y), float(z)))
        return len(self.V) - 1

    def add_polar(self, r, theta_deg, z):
        t = math.radians(theta_deg)
        return self.add(r * math.cos(t), r * math.sin(t), z)

    def tri(self, a, b, c, tag=''):
        if a == b or b == c or a == c:
            return
        self.T.append((a, b, c))
        self.tag.append(tag)

    def quad(self, a, b, c, d, tag=''):
        self.tri(a, b, c, tag)
        self.tri(a, c, d, tag)


def ring(M, r, z, centers, hw=0.0):
    """One ring of vertices at radius r, height z, split into len(centers) arcs.
    centers: angles (deg) of the slots/notches, each a multiple of STEP.
    hw: half-width (mm) of the gap at each center (0 = no gap, split only).
    Returns (arcs, edges): arcs = list of [(theta, vid), ...] in increasing theta;
    edges = list of (vid_minus, vid_plus) per center (equal when hw == 0)."""
    n = len(centers)
    a = math.degrees(math.asin(hw / r)) if hw > 0 else 0.0
    edges = []
    for tc in centers:
        if hw > 0:
            edges.append((M.add_polar(r, tc - a, z), M.add_polar(r, tc + a, z)))
        else:
            v = M.add_polar(r, tc, z)
            edges.append((v, v))
    arcs = []
    for i in range(n):
        tc0 = centers[i]
        tc1 = centers[(i + 1) % n] + (360.0 if i == n - 1 else 0.0)
        s, e = tc0 + a, tc1 - a
        arc = [(s, edges[i][1])]
        k0 = int(math.floor(s / STEP)) + 1
        k1 = int(math.ceil(e / STEP))
        for k in range(k0, k1 + 1):
            th = k * STEP
            if s + EPS_DEG < th < e - EPS_DEG:
                arc.append((th, M.add_polar(r, th % 360.0, z)))
        arc.append((e, edges[(i + 1) % n][0]))
        arcs.append(arc)
    return arcs, edges


def closed_ring_xy(M, xy, z):
    """A closed ring from explicit xy points (used for the insert's ceiling holes).
    Returns one arc parametrized by index, with the first vertex repeated at the end."""
    vids = [M.add(x, y, z) for x, y in xy]
    arc = [(k, v) for k, v in enumerate(vids)] + [(len(vids), vids[0])]
    return [arc]


def strip(M, arcsA, arcsB, tag=''):
    """Triangulate between two rings with the same arc structure."""
    assert len(arcsA) == len(arcsB), (len(arcsA), len(arcsB))
    for A, B in zip(arcsA, arcsB):
        i = j = 0
        while i < len(A) - 1 or j < len(B) - 1:
            if j == len(B) - 1 or (i < len(A) - 1 and A[i + 1][0] <= B[j + 1][0]):
                M.tri(A[i][1], A[i + 1][1], B[j][1], tag)
                i += 1
            else:
                M.tri(A[i][1], B[j + 1][1], B[j][1], tag)
                j += 1


def fan(M, center, arcs, tag=''):
    for arc in arcs:
        for k in range(len(arc) - 1):
            M.tri(center, arc[k][1], arc[k + 1][1], tag)


def side_walls(M, outer_edges, inner_edges, tag='slotwall'):
    """Walls of a through-cut between matching outer and inner rings.
    outer_edges[k][s] = (vm, vp) at level k for slot s."""
    nslot = len(outer_edges[0])
    for s in range(nslot):
        for k in range(len(outer_edges) - 1):
            om0, op0 = outer_edges[k][s]
            om1, op1 = outer_edges[k + 1][s]
            im0, ip0 = inner_edges[k][s]
            im1, ip1 = inner_edges[k + 1][s]
            M.quad(op0, op1, ip1, ip0, tag)
            M.quad(om0, im0, im1, om1, tag)


# ----------------------------------------------------------------------------- checks
def orient_and_check(M):
    """Make the winding consistent and outward, and verify the mesh is a closed
    2-manifold (every edge shared by exactly two triangles, once each way)."""
    T = M.T
    n = len(T)
    emap = defaultdict(list)
    for ti, (a, b, c) in enumerate(T):
        for u, v in ((a, b), (b, c), (c, a)):
            emap[(u, v) if u < v else (v, u)].append(ti)
    bad = [(e, len(l)) for e, l in emap.items() if len(l) != 2]
    if bad:
        raise RuntimeError('non-manifold edges: %d, e.g. %s' % (len(bad), bad[:5]))
    seen = [False] * n
    seen[0] = True
    stack = [0]
    while stack:
        t = stack.pop()
        a, b, c = T[t]
        for u, v in ((a, b), (b, c), (c, a)):
            key = (u, v) if u < v else (v, u)
            for t2 in emap[key]:
                if t2 == t or seen[t2]:
                    continue
                a2, b2, c2 = T[t2]
                if (u, v) in ((a2, b2), (b2, c2), (c2, a2)):
                    T[t2] = (a2, c2, b2)
                seen[t2] = True
                stack.append(t2)
    if not all(seen):
        raise RuntimeError('mesh is not connected: %d unreached triangles' % seen.count(False))
    V = np.array(M.V)
    Tn = np.array(T)
    vol = np.einsum('ij,ij->i', V[Tn[:, 0]], np.cross(V[Tn[:, 1]], V[Tn[:, 2]])).sum() / 6.0
    if vol < 0:
        M.T = [(a, c, b) for a, b, c in T]
        vol = -vol
    Tn = np.array(M.T)
    d = np.concatenate([Tn[:, [0, 1]], Tn[:, [1, 2]], Tn[:, [2, 0]]])
    key = d[:, 0] * len(V) + d[:, 1]
    rkey = d[:, 1] * len(V) + d[:, 0]
    if len(np.unique(key)) != len(key) or not np.array_equal(np.sort(key), np.sort(rkey)):
        raise RuntimeError('directed-edge check failed')
    return vol


def normals_and_centroids(M):
    V = np.array(M.V)
    T = np.array(M.T)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    nrm = np.cross(b - a, c - a)
    ln = np.linalg.norm(nrm, axis=1)
    nrm = nrm / np.where(ln == 0, 1, ln)[:, None]
    cen = (a + b + c) / 3.0
    return nrm, cen


def paint_seam(M, span_deg):
    """Return a bool array: triangles in the enforcer strip. Outward-facing faces
    (normal has a positive radial component) whose centroid angle lies in span."""
    nrm, cen = normals_and_centroids(M)
    r = np.hypot(cen[:, 0], cen[:, 1])
    rad = (nrm[:, 0] * cen[:, 0] + nrm[:, 1] * cen[:, 1]) / np.where(r == 0, 1, r)
    ang = np.degrees(np.arctan2(cen[:, 1], cen[:, 0])) % 360.0
    lo, hi = span_deg
    return (rad > 0.1) & (ang >= lo) & (ang <= hi)


# ----------------------------------------------------------------------------- pot geometry
def pot_profile(H, R_lip, t):
    """Outer and inner profile functions for a pot. Returns a dict of key values
    and the functions r_out(z), r_in(z)."""
    alpha = math.radians(5.03)
    ta = math.tan(alpha)
    z_lb = H - 4.32                  # lip base
    r_lb = R_lip - 2.187             # outer wall radius at the lip base
    lip_rise = 2.288                 # chamfer rise (not changed when the lip shortened)
    def r_wall(z):
        return r_lb - (z_lb - z) * ta
    Rf = 10.0
    z_ce = 5.12                      # foot chamfer end
    zc = z_ce + Rf / math.sqrt(2)    # foot arc center height
    z_t = zc - Rf * math.sin(alpha)  # arc meets the wall
    rc = r_wall(z_t) - Rf * math.cos(alpha)
    r_ce = rc + Rf / math.sqrt(2)
    r_base = r_ce - z_ce
    def r_out(z):
        if z <= z_ce:
            return r_base + z
        if z <= z_t:
            return rc + math.sqrt(max(Rf * Rf - (z - zc) ** 2, 0.0))
        if z <= z_lb:
            return r_wall(z)
        if z <= z_lb + lip_rise:
            return r_lb + (z - z_lb) * (2.187 / lip_rise)
        return R_lip
    def r_in(z):
        return (r_out(z) if z <= z_t else r_wall(z)) - t
    return dict(alpha=alpha, z_lb=z_lb, r_lb=r_lb, lip_rise=lip_rise, Rf=Rf, z_ce=z_ce,
                zc=zc, z_t=z_t, rc=rc, r_ce=r_ce, r_base=r_base, r_out=r_out, r_in=r_in)


def band_levels(z_bot, z_top, w, m=10, open_top=False, extra_top=()):
    """(z, half-width) levels of a stadium cut from z_bot to z_top. With open_top the
    cut runs straight to the top through the extra_top levels."""
    Rs = w / 2.0
    lv = [(z_bot, 0.0)]
    for k in range(1, m + 1):
        phi = math.radians(90.0 * k / m)
        lv.append((z_bot + Rs * (1 - math.cos(phi)), Rs * math.sin(phi)))
    if open_top:
        for z in extra_top:
            lv.append((z, Rs))
    else:
        for k in range(m - 1, -1, -1):
            phi = math.radians(90.0 * k / m)
            lv.append((z_top - Rs * (1 - math.cos(phi)), Rs * math.sin(phi)))
    return lv


def build_pot_mesh(H, R_lip, t, floor, slot_w, z_sb, z_st, groove_in, groove_out, n_arc=26):
    """Returns (Mesh, info). groove_in/groove_out: distances of the drip groove's inner
    and outer edges inside the base edge."""
    P = pot_profile(H, R_lip, t)
    r_out, r_in = P['r_out'], P['r_in']
    r_base = P['r_base']
    r_gi, r_go = r_base - groove_in, r_base - groove_out     # groove radii (inner, outer)
    r_ri, r_ro = r_gi - 0.5, r_go + 0.5                      # floor ridge radii
    z_ridge, groove_depth = 2.16, 0.72
    centers = [22.5 + 45.0 * k for k in range(8)]
    M = Mesh()

    # outer levels (z, r, hw)
    lv = [(0.0, r_base, 0.0), (P['z_ce'], P['r_ce'], 0.0)]
    for k in range(1, n_arc):
        phi = math.radians(-45.0 + (45.0 - 5.03) * k / n_arc)
        lv.append((P['zc'] + P['Rf'] * math.sin(phi), P['rc'] + P['Rf'] * math.cos(phi), 0.0))
    lv.append((P['z_t'], r_out(P['z_t']), 0.0))
    band = band_levels(z_sb, z_st, slot_w)
    band_start = len(lv)
    for z, hw in band:
        lv.append((z, r_out(z), hw))
    band_end = len(lv)
    lv += [(P['z_lb'], P['r_lb'], 0.0), (P['z_lb'] + P['lip_rise'], R_lip, 0.0), (H, R_lip, 0.0)]

    outer = [ring(M, r, z, centers, hw) for (z, r, hw) in lv]
    # inner levels: from the floor top up, same z as the outer levels above it
    lv_in = [(floor, r_in(floor), 0.0)] + [(z, r_in(z), hw) for (z, r, hw) in lv if z > floor + 1e-9]
    inner = [ring(M, r, z, centers, hw) for (z, r, hw) in lv_in]
    in_band_start = band_start - (len(lv) - len(lv_in))   # index shift
    in_band_end = band_end - (len(lv) - len(lv_in))

    # underside, drip groove
    c0 = M.add(0, 0, 0.0)
    U1, _ = ring(M, r_gi, 0.0, centers)
    U2, _ = ring(M, r_gi, groove_depth, centers)
    U3, _ = ring(M, r_go, groove_depth, centers)
    U4, _ = ring(M, r_go, 0.0, centers)
    fan(M, c0, U1, 'underside')
    strip(M, U1, U2, 'groove_in')
    strip(M, U2, U3, 'groove_ceiling')
    strip(M, U3, U4, 'groove_out')
    strip(M, U4, outer[0][0], 'underside')
    # outer surface
    for k in range(len(outer) - 1):
        strip(M, outer[k][0], outer[k + 1][0], 'outer')
    # top, inner surface
    strip(M, outer[-1][0], inner[-1][0], 'top')
    for k in range(len(inner) - 1):
        strip(M, inner[k][0], inner[k + 1][0], 'inner')
    # floor and ridge
    F1, _ = ring(M, r_ro, floor, centers)
    F2, _ = ring(M, r_ro, z_ridge, centers)
    F3, _ = ring(M, r_ri, z_ridge, centers)
    F4, _ = ring(M, r_ri, floor, centers)
    strip(M, inner[0][0], F1, 'floor')
    strip(M, F1, F2, 'ridge_out')
    strip(M, F2, F3, 'ridge_top')
    strip(M, F3, F4, 'ridge_in')
    c1 = M.add(0, 0, floor)
    fan(M, c1, F4, 'floor')
    # slot walls
    side_walls(M, [outer[k][1] for k in range(band_start, band_end)],
               [inner[k][1] for k in range(in_band_start, in_band_end)])

    vol = orient_and_check(M)
    # reservoir: cavity from the floor top to the waterline, minus the ridge
    zs = np.linspace(floor, z_sb, 4001)
    rr = np.array([r_in(z) for z in zs])
    area = np.pi * rr ** 2
    reservoir = float(((area[1:] + area[:-1]) / 2 * np.diff(zs)).sum()) \
        - math.pi * (r_ro ** 2 - r_ri ** 2) * (z_ridge - floor)
    info = dict(plastic_cm3=vol / 1000.0, reservoir_mL=reservoir / 1000.0, r_base=r_base,
                base_diameter=2 * r_base, z_t=P['z_t'], groove=(r_gi, r_go), ridge=(r_ri, r_ro),
                vertices=len(M.V), triangles=len(M.T))
    return M, info


# ----------------------------------------------------------------------------- insert geometry
def stadium_xy(phi_deg, r0, r1, w, n_end=16, ds=0.5):
    """Stadium along the radial direction phi: extents r0..r1, width w."""
    Rs = w / 2.0
    c0, c1 = r0 + Rs, r1 - Rs
    pts = []
    for k in range(n_end + 1):                       # far end, from +side to -side
        a = math.radians(90 - 180.0 * k / n_end)
        pts.append((c1 + Rs * math.cos(a), Rs * math.sin(a)))
    ns = max(1, int(round((c1 - c0) / ds)))
    for k in range(1, ns):                           # -side, back toward the center
        s = c1 - (c1 - c0) * k / ns
        pts.append((s, -Rs))
    for k in range(n_end + 1):                       # near end
        a = math.radians(-90 - 180.0 * k / n_end)
        pts.append((c0 + Rs * math.cos(a), Rs * math.sin(a)))
    for k in range(1, ns):                           # +side
        s = c0 + (c1 - c0) * k / ns
        pts.append((s, Rs))
    t = math.radians(phi_deg)
    return [(x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)) for x, y in pts]


def circle_xy(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def build_insert_mesh(R, t, H, T, c, slot_w, slot_r0, slot_r1, hole_r, hole_radii,
                      notch_w, notch_d, n_arc=10, rim_chamfer=0.5, rim_round=0.2, open_chamfer=0.0,
                      slope_deg=0.0, shoulder=None):
    """shoulder=(zc, rho), with c=0: a 45 deg chamfer from the bed up to zc, then a rho radius
    curve tangent to the (sloped) wall; the inside is the outside offset t square to every
    face (a concentric rho - t curve), cut off by the ceiling's inside face at z = T.
R outer radius, t wall, H height, T ceiling thickness, c chamfer/curve size,
    radial slots (width, extents), diagonal holes (radius, list of center radii),
    notches (width, depth). c=0: no shoulder (square ceiling corner). slope_deg: the wall
    leans in toward the ceiling by this angle from vertical; the rim radius R stays and the
    wall keeps its horizontal thickness t on every layer. Returns (Mesh, info)."""
    from scipy.spatial import Delaunay
    centers = [0.0, 90.0, 180.0, 270.0]
    rc, zc = R - c, c * math.sqrt(2)
    M = Mesh()
    s2 = math.sqrt(2)

    # outer levels (z, r, hw)
    tn = math.tan(math.radians(slope_deg))
    def lean(levels):   # shift each (z, r, hw) level in by the wall slope
        return [(z, r - (H - z) * tn, hw) for (z, r, hw) in levels]
    if c > 0:
        lv = [(0.0, rc, 0.0), (zc - c / s2, rc + c / s2, 0.0)]
        for k in range(1, n_arc):
            phi = math.radians(-45.0 + 45.0 * k / n_arc)
            lv.append((zc + c * math.sin(phi), rc + c * math.cos(phi), 0.0))
        lv.append((zc, R, 0.0))
    else:
        lv = [(0.0, R, 0.0)]
    sh = []
    tw = t   # inside wall's horizontal offset
    if c <= 0 and shoulder:
        tw = t / math.cos(math.radians(slope_deg))
        zc1, rho = shoulder
        th = math.radians(slope_deg)
        rw = lambda z: R - (H - z) * tn
        # center from the tangent point on the wall: z2 = zc1 + rho*(cos45 - sin th)
        z2 = zc1 + rho * (math.sqrt(0.5) - math.sin(th))
        Cr, Cz = rw(z2) - rho * math.cos(th), z2 + rho * math.sin(th)
        r1 = Cr + rho * math.sqrt(0.5)
        sh = [(0.0, r1 - zc1)]
        sh_off = [(t * math.sqrt(0.5), r1 - zc1 - t * math.sqrt(0.5))]   # offset t square to the chamfer
        for k in range(0, n_arc + 1):
            a = math.radians(-45.0 + (45.0 - slope_deg) * k / n_arc)
            sh.append((Cz + rho * math.sin(a), Cr + rho * math.cos(a)))
            sh_off.append((Cz + (rho - t) * math.sin(a), Cr + (rho - t) * math.cos(a)))
        lv = []
    band = band_levels(H - notch_d, H, notch_w, open_top=True,
                       extra_top=tuple(sorted({H - rim_chamfer, H - rim_round, H})))   # 0 sizes give a square edge
    band_start = len(lv)
    for z, hw in band:
        if z < H - rim_chamfer - 1e-9:
            r = R
        elif z < H - 1e-9:
            r = R - (z - (H - rim_chamfer))
        else:
            r = R - rim_chamfer
        lv.append((z, r, hw))
    lv = [(z, r, 0.0) for z, r in sh] + lean(lv)
    band_start += len(sh)
    outer = [ring(M, r, z, centers, hw) for (z, r, hw) in lv]
    # inner levels
    ci = c - t
    r_top = rc - t * s2 + T
    if c > 0:
        lv_in = [(T, r_top, 0.0), (zc - ci / s2, rc + ci / s2, 0.0)]
        for k in range(1, n_arc):
            phi = math.radians(-45.0 + 45.0 * k / n_arc)
            lv_in.append((zc + ci * math.sin(phi), rc + ci * math.cos(phi), 0.0))
        lv_in.append((zc, R - t, 0.0))
    else:
        r_top = R - t
        lv_in = [(T, r_top, 0.0)]
    sh_in = []
    if sh:
        zs = [z for z, r in sh_off]; rs_ = [r for z, r in sh_off]
        rT = float(np.interp(T, zs, rs_)) if T <= zs[-1] else R - tw - (H - T) * tn
        sh_in = [(T, rT, 0.0)] + [(z, r, 0.0) for z, r in sh_off if z > T + 1e-6]
        lv_in = []
    in_band_start = len(lv_in)
    for z, hw in band:
        r = R - tw if z < H - 1e-9 else R - tw + rim_round
        lv_in.append((z, r, hw))
    lv_in = sh_in + lean(lv_in)
    in_band_start += len(sh_in)
    inner = [ring(M, r, z, centers, hw) for (z, r, hw) in lv_in]

    for k in range(len(outer) - 1):
        strip(M, outer[k][0], outer[k + 1][0], 'outer')
    strip(M, outer[-1][0], inner[-1][0], 'rim')
    for k in range(len(inner) - 1):
        strip(M, inner[k][0], inner[k + 1][0], 'inner')
    side_walls(M, [outer[k][1] for k in range(band_start, len(outer))],
               [inner[k][1] for k in range(in_band_start, len(inner))], 'notchwall')

    # ceiling holes: center hole, radial slots, diagonal holes
    holes = [('circle', 0.0, 0.0, hole_r)]
    for phi in centers:
        holes.append(('stadium', phi, slot_r0, slot_r1, slot_w))
    for rr in hole_radii:
        for phi in (45.0, 135.0, 225.0, 315.0):
            holes.append(('circle', rr * math.cos(math.radians(phi)), rr * math.sin(math.radians(phi)), hole_r))

    def hole_xy(h, g=0.0):   # g widens the opening (bed-side chamfer)
        if h[0] == 'circle':
            return circle_xy(h[1], h[2], h[3] + g)
        return stadium_xy(h[1], h[2] - g, h[3] + g, h[4] + 2 * g)

    def inside_hole(x, y, margin=0.0, g=0.0):
        margin += g
        for h in holes:
            if h[0] == 'circle':
                if math.hypot(x - h[1], y - h[2]) < h[3] + margin:
                    return True
            else:
                tt = math.radians(h[1])
                s = x * math.cos(tt) + y * math.sin(tt)
                d = abs(-x * math.sin(tt) + y * math.cos(tt))
                Rs = h[4] / 2.0
                c0, c1 = h[2] + Rs, h[3] - Rs
                if (d < Rs + margin and c0 <= s <= c1) or math.hypot(s - c0, d) < Rs + margin \
                        or math.hypot(s - c1, d) < Rs + margin:
                    return True
        return False

    # open_chamfer: 45 deg chamfer on the openings' bed-side edges
    hole_rings_bot = [closed_ring_xy(M, hole_xy(h, open_chamfer), 0.0) for h in holes]
    hole_rings_top = [closed_ring_xy(M, hole_xy(h), T) for h in holes]
    if open_chamfer > 0:
        hole_rings_mid = [closed_ring_xy(M, hole_xy(h), open_chamfer) for h in holes]
        for hb, hm, ht in zip(hole_rings_bot, hole_rings_mid, hole_rings_top):
            strip(M, hb, hm, 'holewall'); strip(M, hm, ht, 'holewall')
    else:
        for hb, ht in zip(hole_rings_bot, hole_rings_top):
            strip(M, hb, ht, 'holewall')

    def plate(boundary_arcs, hole_rings, z, r_bound, g=0.0):
        vids = []
        seen = set()
        for arc in boundary_arcs:
            for _, v in arc:
                if v not in seen:
                    seen.add(v); vids.append(v)
        for hr in hole_rings:
            for _, v in hr[0]:
                if v not in seen:
                    seen.add(v); vids.append(v)
        # interior points on a polar grid, away from the holes and the boundary
        h = 2.0
        rr = h
        while rr < r_bound - 0.8:
            n = max(8, int(round(2 * math.pi * rr / h)))
            for k in range(n):
                a = 2 * math.pi * k / n + (0.5 * 2 * math.pi / n if int(round(rr / h)) % 2 else 0)
                x, y = rr * math.cos(a), rr * math.sin(a)
                if not inside_hole(x, y, 0.7, g):
                    vids.append(M.add(x, y, z))
            rr += h
        xy = np.array([M.V[v][:2] for v in vids])
        tri = Delaunay(xy)
        for s in tri.simplices:
            a, b, cc = (vids[i] for i in s)
            cx, cy = xy[s].mean(axis=0)
            if inside_hole(cx, cy, 0.0, g):
                continue
            M.tri(a, b, cc, 'plate')

    plate(outer[0][0], hole_rings_bot, 0.0, lv[0][1], open_chamfer)
    plate(inner[0][0], hole_rings_top, T, lv_in[0][1])
    r_top = lv_in[0][1]

    vol = orient_and_check(M)
    info = dict(plastic_cm3=vol / 1000.0, vertices=len(M.V), triangles=len(M.T),
                r_top_plate=r_top, zc=zc, holes=len(holes))
    return M, info


# ----------------------------------------------------------------------------- 3mf packaging
def _uuid(name, tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'nursery-pots/%s/%s' % (name, tag)))


def _fmt(v):
    s = '%.5f' % v
    s = s.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def _thumbnails(M, H):
    """plate_1.png (512) and plate_1_small.png (128): a plain top-view silhouette."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        V = np.array(M.V)
        rmax = np.hypot(V[:, 0], V[:, 1]).max()
        out = {}
        for name, px in (('plate_1.png', 512), ('plate_1_small.png', 128)):
            fig = plt.figure(figsize=(px / 100, px / 100), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_facecolor('#e8e8e8')
            ax.add_patch(plt.Circle((0, 0), rmax, color='#6fa8dc'))
            ax.set_xlim(-rmax * 1.1, rmax * 1.1); ax.set_ylim(-rmax * 1.1, rmax * 1.1)
            ax.set_aspect('equal'); ax.axis('off')
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            out[name] = buf.getvalue()
        return out
    except Exception:
        return {}


def write_3mf(path, M, name, H, painted, object_settings, layer_ranges, settings_overrides,
              fan_ramp, plate_name):
    """Package the mesh as an Orca 2.4.2 3mf.
    painted: bool array per triangle (seam enforcer). object_settings: list of (key, value).
    layer_ranges: list of (min_z, max_z, [(key, value), ...]). settings_overrides: dict
    merged into the base project settings. fan_ramp: True for the pots' foot fan G-code."""
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    base.update(settings_overrides)
    zoff = H / 2.0
    # object file
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">',
             ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
             ' <resources>',
             '  <object id="3" p:UUID="%s" type="model">' % _uuid(name, 'part'),
             '   <mesh>', '    <vertices>']
    lines += ['     <vertex x="%s" y="%s" z="%s"/>' % (_fmt(x), _fmt(y), _fmt(z - zoff)) for x, y, z in M.V]
    lines += ['    </vertices>', '    <triangles>']
    for (a, b, c), p in zip(M.T, painted):
        lines.append('     <triangle v1="%d" v2="%d" v3="%d"%s/>' % (a, b, c, ' paint_seam="4"' if p else ''))
    lines += ['    </triangles>', '   </mesh>', '  </object>', ' </resources>', ' <build/>', '</model>', '']
    obj_xml = '\n'.join(lines)
    obj_path = '/3D/Objects/%s.model' % name

    root = '''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">BambuStudio-02.06.00.51</metadata>
 <metadata name="OrcaSlicer">2.4.2</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="Copyright"></metadata>
 <metadata name="CreationDate">%s</metadata>
 <metadata name="Description"></metadata>
 <metadata name="Designer"></metadata>
 <metadata name="DesignerCover"></metadata>
 <metadata name="DesignerUserId"></metadata>
 <metadata name="License"></metadata>
 <metadata name="ModificationDate">%s</metadata>
 <metadata name="OrcaSlicer">2.4.2</metadata>
 <metadata name="Origin"></metadata>
 <metadata name="Thumbnail_Middle">/Metadata/plate_1.png</metadata>
 <metadata name="Thumbnail_Small">/Metadata/plate_1_small.png</metadata>
 <metadata name="Title"></metadata>
 <resources>
  <object id="4" p:UUID="%s" type="model">
   <components>
    <component p:path="%s" objectid="3" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
 </resources>
 <build p:UUID="%s">
  <item objectid="4" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 128 128 %s" printable="1" auto_drop="1"/>
 </build>
</model>
''' % (datetime.date.today().isoformat(), datetime.date.today().isoformat(), _uuid(name, 'object'),
       obj_path, _uuid(name, 'component'), _uuid(name, 'build'), _uuid(name, 'item'), _fmt(zoff))

    ms = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>', '  <object id="4">',
          '    <metadata key="name" value="%s"/>' % name, '    <metadata key="extruder" value="1"/>']
    ms += ['    <metadata key="%s" value="%s"/>' % (k, v) for k, v in object_settings]
    ms += ['    <part id="3" subtype="normal_part">',
           '      <metadata key="name" value="%s"/>' % name,
           '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
           '      <metadata key="source_file" value="%s.3mf"/>' % name,
           '      <metadata key="source_object_id" value="0"/>',
           '      <metadata key="source_volume_id" value="0"/>',
           '      <metadata key="source_offset_x" value="0"/>',
           '      <metadata key="source_offset_y" value="0"/>',
           '      <metadata key="source_offset_z" value="0"/>',
           '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
           '    </part>', '  </object>', '  <plate>',
           '    <metadata key="plater_id" value="1"/>',
           '    <metadata key="plater_name" value="%s"/>' % plate_name,
           '    <metadata key="locked" value="false"/>',
           '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
           '    <metadata key="filament_maps" value="1 1"/>',
           '    <model_instance>', '      <metadata key="object_id" value="4"/>',
           '      <metadata key="instance_id" value="0"/>', '      <metadata key="identify_id" value="300"/>',
           '    </model_instance>', '  </plate>', '  <assemble>',
           '   <assemble_item object_id="4" instance_id="0" transform="1 0 0 0 1 0 0 0 1 128 128 %s" offset="0 0 0" />' % _fmt(zoff),
           '  </assemble>', '</config>', '']
    model_settings = '\n'.join(ms)

    lr = ['<?xml version="1.0" encoding="utf-8"?>', '<objects>']
    if layer_ranges:
        lr.append(' <object id="1">')
        for lo, hi, opts in layer_ranges:
            lr.append('  <range min_z="%s" max_z="%s">' % (_fmt(lo), _fmt(hi)))
            lr += ['   <option opt_key="%s">%s</option>' % (k, v) for k, v in opts]
            lr.append('  </range>')
        lr.append(' </object>')
    lr += ['</objects>', '']
    layer_xml = '\n'.join(lr)

    if fan_ramp:
        gcode = '''<?xml version="1.0" encoding="utf-8"?>
<custom_gcodes_per_layer>
<plate>
<plate_info id="1"/>
<layer top_z="9.72" type="4" extruder="1" color="" extra="" gcode="; fan ramp 45%&#10;M106 S115"/>
<layer top_z="10.44" type="4" extruder="1" color="" extra="" gcode="; fan ramp 30%&#10;M106 S77"/>
<layer top_z="11.16" type="4" extruder="1" color="" extra="" gcode="; fan ramp 15%&#10;M106 S38"/>
<layer top_z="11.88" type="4" extruder="1" color="" extra="" gcode="; fan ramp 0%&#10;M106 S0"/>
<mode value="SingleExtruder"/>
</plate>
</custom_gcodes_per_layer>
'''
    else:
        gcode = '<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_layer>\n</custom_gcodes_per_layer>\n'

    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>
<Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>
</Relationships>
'''
    model_rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="%s" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
''' % obj_path
    slice_info = '''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-BBL-Client-Type" value="slicer"/>
    <header_item key="X-BBL-Client-Version" value="02.06.00.51"/>
    <header_item key="OrcaSlicer-Version" value="2.4.2"/>
  </header>
</config>
'''
    filament_seq = '{"plate_1": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}}'

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', root)
        z.writestr('3D/_rels/3dmodel.model.rels', model_rels)
        z.writestr(obj_path.lstrip('/'), obj_xml)
        z.writestr('Metadata/project_settings.config', json.dumps(base, indent=4, ensure_ascii=False))
        z.writestr('Metadata/model_settings.config', model_settings)
        z.writestr('Metadata/layer_config_ranges.xml', layer_xml)
        z.writestr('Metadata/custom_gcode_per_layer.xml', gcode)
        z.writestr('Metadata/slice_info.config', slice_info)
        z.writestr('Metadata/filament_sequence.json', filament_seq)
        for pname, data in _thumbnails(M, H).items():
            z.writestr('Metadata/' + pname, data)
    return path


# ----------------------------------------------------------------------------- top-level builders
POT_OBJECT_SETTINGS = [('staggered_inner_seams', '1'), ('seam_position', 'back'),
                       ('seam_slope_type', 'none'), ('seam_slope_inner_walls', '0'),
                       ('seam_slope_min_length', '12'), ('seam_slope_steps', '20'),
                       ('seam_slope_start_height', '20%'), ('scarf_joint_speed', '100%'),
                       ('scarf_joint_flow_ratio', '1'), ('seam_slope_conditional', '0'),
                       ('seam_slope_entire_loop', '0')]


def pot_layer_ranges(z_sb, z_st, bead):
    """Height ranges from the product doc: floor, reservoir, bottom band layer,
    slot band, top band layer. Every boundary on a 0.36 mm layer top."""
    L = 0.36
    common_band = [('bottom_solid_infill_flow_ratio', '1'), ('extruder', '0'),
                   ('inner_wall_line_width', _fmt(bead)), ('inner_wall_speed', '40'),
                   ('layer_height', '0.36'), ('outer_wall_line_width', _fmt(bead)),
                   ('outer_wall_speed', '40'), ('print_flow_ratio', '1'),
                   ('top_solid_infill_flow_ratio', '1'), ('wall_sequence', 'outer wall/inner wall'),
                   ('wipe_before_external_loop', '1')]
    floor = [('extruder', '0'), ('internal_solid_infill_speed', '60'), ('layer_height', '0.36'),
             ('outer_wall_flow_ratio', '1.03'), ('outer_wall_speed', '28'), ('seam_gap', '0%'),
             ('top_surface_speed', '60')]
    reservoir = [('extruder', '0'), ('layer_height', '0.36'), ('outer_wall_flow_ratio', '1.03'),
                 ('outer_wall_speed', '28'), ('seam_gap', '0%')]
    bottom_band = sorted(common_band + [('outer_wall_flow_ratio', '1.03'), ('seam_gap', '0%')])
    slot_band = sorted(common_band + [('seam_slope_type', 'none')])
    top_band = sorted(common_band)
    return [(0.0, 2.16, floor), (2.16, z_sb - L, reservoir), (z_sb - L, z_sb, bottom_band),
            (z_sb, z_st, slot_band), (z_st, z_st + L, top_band)]


def build_pot(name, H, R_lip, t, floor, slot_w, z_sb, z_st, band_bead, outer_wall_speed,
              wall_line_width, paint_span, groove_in=6.5, groove_out=5.0, out_dir='.'):
    M, info = build_pot_mesh(H, R_lip, t, floor, slot_w, z_sb, z_st, groove_in, groove_out)
    painted = paint_seam(M, paint_span)
    info['painted_triangles'] = int(painted.sum())
    obj = POT_OBJECT_SETTINGS + [('outer_wall_speed', _fmt(outer_wall_speed)),
                                 ('outer_wall_line_width', _fmt(wall_line_width)),
                                 ('inner_wall_line_width', _fmt(wall_line_width))]
    path = os.path.join(out_dir, name + '.3mf')
    write_3mf(path, M, name, H, painted, obj, pot_layer_ranges(z_sb, z_st, band_bead), {},
              fan_ramp=True, plate_name=name.replace('_', ' '))
    info['path'] = path
    return info


INSERT_SETTINGS_OVERRIDES = {
    'fan_max_speed': ['40', '30'], 'fan_min_speed': ['40', '20'],
    'filament_settings_id': ['JAYO PETG – insert', 'Bambu Support For PLA/PETG @BBL X1C'],
    'initial_layer_print_height': '0.4', 'layer_height': '0.4', 'slow_down_layer_time': ['4', '8']}


def insert_height(floor, z_sb, T, L=0.4, min_gap=3.0):
    """Insert height from the air-gap rule (nursery-pots state.md, Product rules): the fewest whole insert
    layers L giving at least min_gap from the waterline (slot bottoms, z_sb) to the ceiling's underside, on a
    pot floor at floor. Returns (H, gap); tell me both whenever the floor, the slots or the insert change."""
    H = math.ceil(round((z_sb + min_gap - floor + T) / L, 6)) * L
    return round(H, 3), round(floor + H - T - z_sb, 3)


def build_insert(name, R, t, H, T, c, slot_w, slot_r0, slot_r1, hole_radii, notch_w, notch_d,
                 bead, hole_r=2.0, out_dir='.', rim_chamfer=0.5, rim_round=0.2, open_chamfer=0.0,
                 slope_deg=0.0, shoulder=None):
    M, info = build_insert_mesh(R, t, H, T, c, slot_w, slot_r0, slot_r1, hole_r, hole_radii,
                                notch_w, notch_d, rim_chamfer=rim_chamfer, rim_round=rim_round,
                                open_chamfer=open_chamfer, slope_deg=slope_deg, shoulder=shoulder)
    painted = np.zeros(len(M.T), dtype=bool)
    obj = [('layer_height', '0.4'), ('wall_loops', '2'), ('outer_wall_line_width', _fmt(bead)),
           ('inner_wall_line_width', _fmt(bead)), ('outer_wall_speed', '60'), ('inner_wall_speed', '60'),
           ('internal_solid_infill_speed', '200'), ('top_surface_speed', '60'),
           ('outer_wall_acceleration', '5000'), ('inner_wall_acceleration', '5000'),
           ('seam_position', 'aligned'), ('bottom_surface_pattern', 'monotonic'),
           ('top_surface_pattern', 'monotonic'), ('internal_solid_infill_pattern', 'monotonic')]
    path = os.path.join(out_dir, name + '.3mf')
    write_3mf(path, M, name, H, painted, obj, [], INSERT_SETTINGS_OVERRIDES, fan_ramp=False,
              plate_name=name.replace('_', ' ') + ' (ceiling down)')
    info['path'] = path
    return info

#!/usr/bin/env python3
"""gcodeTrace.py - trace nozzle moves in an OrcaSlicer G-code file (3dp project, 2026-10-02).

Built to find what marks the pots' seams on multi-pot plates (2.5in rev2.11 / rev2.12): where the
nozzle passes low over each pot's wall near its seam, in what order Orca prints the pots, where the
seams sit, and how the two-bead slot band prints. Works on any round object on a by-layer plate.

Usage:
  python3 gcodeTrace.py PLATE.gcode --centers 90,126 166,126
         [--fit-centers LAYER] [--ref-angle 90 [90 ...]] [--zmin 1.1] [--zmax 40.7]
         [--band 22.9 30.7] [--near 0.8] [--max-gap 1.2] [--reach 12]

  --centers     pot centers (x,y) as sliced; pots are numbered 1, 2, ... in this order and every
                move is assigned to the nearest center. The command-line slicer may shift the plate
                (the 2.5in pots sat 2 mm toward the front), so check with --fit-centers.
  --fit-centers fit a circle to each pot's printed path on that layer and print the centers to use.
  --ref-angle   per pot, the bed angle (deg) the seam offsets are measured from, e.g. the slot
                midpoint (90 = back of the printer); one value for all pots or one per pot.
  --zmin/--zmax wall heights to report (seam passes and seam offsets skip the band).
  --band        z range of the slot band, for the band stats.
  --near        how close (mm, sideways) to a pot's wall line a pass must come to count.
  --max-gap     how close (mm) above that pot's last printed layer a pass must come to count.
  --reach       how far along the wall (mm) from the seam passes are reported.

Prints:
  1. Print order: the order the pots are visited on each layer, and how many layers use each order.
  2. Seam passes per pot: non-printing moves (travel, wipe, lift, drop) that come within --near of
     the pot's wall line and within --reach of its seam, split into arrival (before the pot's first
     print of a layer) and departure (after its last). For each kind: the stretch along the wall
     (mm from the seam; + is the loop direction, which is right of the seam seen from outside for a
     counterclockwise loop) and the lowest height above the pot's last printed layer.
  3. Seam offsets: where each layer's first loop starts, in mm along the wall from --ref-angle.
  4. Band stats per pot: length-weighted speed and flow, loop starts per layer (deretractions),
     and the median time between the starts of consecutive band layers at that pot.

Parsing notes: arcs (G2/G3, including full-circle spiral lifts with P1) are expanded; straight moves
are sampled every 0.1 mm so a travel line's middle is seen, not just its ends; Orca writes '; FEATURE:'
only when the feature changes, so the current feature carries across layers. Times are estimates from
feed rates (no acceleration), good for comparing files, not for exact print times.
"""
import argparse
import collections
import math
import re

import numpy as np

FIL_AREA = math.pi * 1.75 ** 2 / 4.0
_RX = re.compile(r'([XYZEIJFP])(-?[\d.]+)')


def parse(path):
    """Return the moves as dicts: layer, z (layer height marker), feature, start/end point, extrusion
    (relative E), feed (mm/s), sampled points (n x 3) and XY length."""
    moves = []
    x = y = z = 0.0
    f = 0.0
    feature = ''
    layer = 0
    for raw in open(path, errors='ignore'):
        line = raw.strip()
        if not line:
            continue
        if line.startswith(';'):
            if line.startswith('; CHANGE_LAYER'):
                layer += 1
            elif line.startswith('; FEATURE:'):
                feature = line.split(':', 1)[1].strip()
            continue
        code = line.split(';')[0].strip()
        if not code:
            continue
        cmd = code.split()[0]
        if cmd not in ('G0', 'G1', 'G2', 'G3'):
            continue
        p = dict(_RX.findall(code))
        nx, ny, nz = float(p.get('X', x)), float(p.get('Y', y)), float(p.get('Z', z))
        de = float(p.get('E', 0.0))
        if 'F' in p:
            f = float(p['F']) / 60.0
        if cmd in ('G2', 'G3') and ('I' in p or 'J' in p):
            cx, cy = x + float(p.get('I', 0)), y + float(p.get('J', 0))
            r = math.hypot(x - cx, y - cy)
            a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
            full = 'P' in p and abs(nx - x) < 1e-6 and abs(ny - y) < 1e-6
            if cmd == 'G3':
                da = (a1 - a0) % (2 * math.pi)
                if full or da < 1e-9:
                    da = 2 * math.pi * int(float(p.get('P', 1)))
            else:
                da = -((a0 - a1) % (2 * math.pi))
                if full or abs(da) < 1e-9:
                    da = -2 * math.pi * int(float(p.get('P', 1)))
            n = max(2, int(abs(da) * r / 0.1) + 1)
            t = np.linspace(0.0, 1.0, n)
            ang = a0 + da * t
            pts = np.column_stack([cx + r * np.cos(ang), cy + r * np.sin(ang), z + (nz - z) * t])
            length = abs(da) * r
        else:
            length = math.hypot(nx - x, ny - y)
            t = np.linspace(0.0, 1.0, max(1, int(length / 0.1)) + 1)
            pts = np.column_stack([x + (nx - x) * t, y + (ny - y) * t, z + (nz - z) * t])
        moves.append(dict(layer=layer, feature=feature, cmd=cmd, x0=x, y0=y, z0=z, x1=nx, y1=ny, z1=nz,
                          e=de, f=f, pts=pts, length=length))
        x, y, z = nx, ny, nz
    return moves


def nearest(C, px, py):
    return int(np.argmin(np.hypot(C[:, 0] - px, C[:, 1] - py)))


def move_time(m):
    f = m['f'] if m['f'] > 0 else 1.0
    if m['length'] > 1e-9:
        return m['length'] / f
    if abs(m['z1'] - m['z0']) > 0:
        return abs(m['z1'] - m['z0']) / min(f, 20.0)
    if m['e'] != 0:
        return abs(m['e']) / min(f, 30.0)
    return 0.0


def fit_centers(M, C, layer):
    out = []
    for k in range(len(C)):
        pts = [p[:2] for m in M if m['layer'] == layer and m['e'] > 0 and m['length'] > 0
               for p in m['pts'] if nearest(C, p[0], p[1]) == k]
        v = np.array(pts)
        A = np.column_stack([2 * v[:, 0], 2 * v[:, 1], np.ones(len(v))])
        cx, cy, c0 = np.linalg.lstsq(A, (v ** 2).sum(1), rcond=None)[0]
        out.append((cx, cy, math.sqrt(c0 + cx * cx + cy * cy)))
    return out


def visits(M, C):
    """Runs of printing on one pot within a layer: (pot, first move index, last move index, layer)."""
    out = []
    cur = None
    for i, m in enumerate(M):
        if m['e'] > 0 and m['length'] > 0:
            k = nearest(C, m['x1'], m['y1'])
            if cur and cur[0] == k and cur[3] == m['layer']:
                cur[2] = i
            else:
                if cur:
                    out.append(tuple(cur))
                cur = [k, i, i, m['layer']]
    if cur:
        out.append(tuple(cur))
    return out


def report(path, C, ref, zmin, zmax, band, near, max_gap, reach):
    M = parse(path)
    V = visits(M, C)
    n = len(C)

    # 1. print order
    order = collections.defaultdict(list)
    for k, a, b, L in V:
        order[L].append(k + 1)
    counts = collections.Counter(tuple(v) for v in order.values())
    print('1. Print order (pot numbers as in --centers): layers using it')
    for o, c in counts.most_common():
        print('   %s: %d' % (', '.join(map(str, o)), c))

    # tops: each pot's last printed z before each move
    top = np.zeros(n)
    tops = []
    for m in M:
        tops.append(top.copy())
        if m['e'] > 0 and m['length'] > 0:
            k = nearest(C, m['x1'], m['y1'])
            top[k] = max(top[k], m['z1'])

    def in_band(z):
        return band is not None and band[0] - 0.4 <= z <= band[1] + 0.4

    # 2. seam passes
    print('2. Seam passes (within %.1f mm of the wall line, %.1f mm of the seam, %.1f mm above the pot):'
          % (near, reach, max_gap))
    agg = collections.defaultdict(lambda: [math.inf, -math.inf, math.inf, 0])
    for vi, (k, a, b, L) in enumerate(V):
        z = M[a]['z1']
        if not (zmin <= z <= zmax) or in_band(z):
            continue
        sx, sy = M[a]['x0'], M[a]['y0']
        a0 = math.atan2(sy - C[k, 1], sx - C[k, 0])
        R = math.hypot(sx - C[k, 0], sy - C[k, 1])
        prev_b = V[vi - 1][2] if vi > 0 else a
        next_a = V[vi + 1][1] if vi + 1 < len(V) else len(M)
        for phase, rng in (('arrival', range(prev_b + 1, a)), ('departure', range(b + 1, next_a))):
            for j in rng:
                m = M[j]
                if m['e'] > 0 and m['length'] > 0:
                    continue
                kind = ('wipe' if m['e'] < 0 else 'lift' if m['cmd'] in ('G2', 'G3')
                        else 'drop' if m['length'] < 1e-6 else 'travel')
                for p in m['pts']:
                    dr = math.hypot(p[0] - C[k, 0], p[1] - C[k, 1]) - R
                    if abs(dr) > near:
                        continue
                    da = (math.atan2(p[1] - C[k, 1], p[0] - C[k, 0]) - a0 + math.pi) % (2 * math.pi) - math.pi
                    s = da * R
                    gap = p[2] - tops[j][k]
                    if abs(s) > reach or gap > max_gap:
                        continue
                    g = agg[(k, phase, kind)]
                    g[0], g[1], g[2], g[3] = min(g[0], s), max(g[1], s), min(g[2], gap), g[3] + 1
    for k in range(n):
        for phase in ('arrival', 'departure'):
            parts = ['%s %.1f..%.1f mm, %.2f mm above' % (kind, g[0], g[1], g[2])
                     for (kk, ph, kind), g in sorted(agg.items()) if kk == k and ph == phase]
            print('   pot %d %-9s: %s' % (k + 1, phase, '; '.join(parts) if parts else 'none'))

    # 3. seam offsets
    if ref:
        print('3. Seam offsets from the reference angle (mm along the wall, + = loop direction):')
        res = collections.defaultdict(list)
        for k, a, b, L in V:
            m = M[a]
            z = m['z1']
            if not (zmin <= z <= zmax) or in_band(z) or 'Outer wall' not in m['feature']:
                continue
            ang = math.degrees(math.atan2(m['y0'] - C[k, 1], m['x0'] - C[k, 0]))
            r = math.hypot(m['x0'] - C[k, 0], m['y0'] - C[k, 1])
            d = (ang - ref[k] + 180) % 360 - 180
            res[k].append(d * math.pi / 180 * r)
        for k in range(n):
            if res[k]:
                print('   pot %d: %.2f..%.2f mm (%d layers)' % (k + 1, min(res[k]), max(res[k]), len(res[k])))

    # 4. band stats
    if band:
        print('4. Band %.2f-%.2f mm:' % tuple(band))
        t = 0.0
        stats = collections.defaultdict(lambda: dict(L=0.0, t=0.0, vol=0.0, starts=0, layers=set()))
        first_t = collections.defaultdict(dict)
        for m in M:
            dt = move_time(m)
            z = m['z1']
            if band[0] <= z <= band[1]:
                k = nearest(C, m['x1'], m['y1'])
                if m['e'] > 0 and m['length'] > 0:
                    d = stats[k]
                    d['L'] += m['length']
                    d['t'] += dt
                    d['vol'] += m['e'] * FIL_AREA
                    d['layers'].add(m['layer'])
                    first_t[m['layer']].setdefault(k, t)
                elif m['e'] > 0:
                    stats[k]['starts'] += 1
            t += dt
        Ls = sorted(first_t)
        for k in range(n):
            d = stats[k]
            if not d['layers']:
                continue
            gaps = [first_t[b][k] - first_t[a][k] for a, b in zip(Ls, Ls[1:])
                    if k in first_t[a] and k in first_t[b]]
            print('   pot %d: %.1f mm/s, %.2f mm3/s, %.1f loop starts per layer, %.1f s between layers'
                  % (k + 1, d['L'] / d['t'], d['vol'] / d['t'], d['starts'] / len(d['layers']),
                     float(np.median(gaps)) if gaps else float('nan')))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('gcode')
    ap.add_argument('--centers', nargs='+', required=True)
    ap.add_argument('--fit-centers', type=int)
    ap.add_argument('--ref-angle', nargs='+', type=float)
    ap.add_argument('--zmin', type=float, default=1.1)
    ap.add_argument('--zmax', type=float, default=1e9)
    ap.add_argument('--band', nargs=2, type=float)
    ap.add_argument('--near', type=float, default=0.8)
    ap.add_argument('--max-gap', type=float, default=1.2)
    ap.add_argument('--reach', type=float, default=12.0)
    a = ap.parse_args()
    C = np.array([tuple(map(float, c.split(','))) for c in a.centers])
    if a.fit_centers is not None:
        for k, (cx, cy, r) in enumerate(fit_centers(parse(a.gcode), C, a.fit_centers)):
            print('pot %d: center %.3f,%.3f, wall line radius %.3f mm' % (k + 1, cx, cy, r))
        return
    ref = None
    if a.ref_angle:
        ref = a.ref_angle * len(C) if len(a.ref_angle) == 1 else a.ref_angle
    report(a.gcode, C, ref, a.zmin, a.zmax, a.band, a.near, a.max_gap, a.reach)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""gcodeStats: per-layer and per-feature numbers from an OrcaSlicer G-code file (3dp project, 2026-10-09).

Replaces the thread scratch scripts gstats.py, lay.py, runs.py and short.py (rough-ceiling hunt, nursery-pots).
Arc moves (G2/G3) count by their arc length, never their chord.

  python3 gcodeStats.py layers G.gcode [--layers 0-5]
      per layer: fan, temps, retractions, wipes, z-lifts, travels; per feature: length, volume, print time,
      mean speed, mean flow, fill (volume / Orca bead area x length) and segment count
  python3 gcodeStats.py runs G.gcode [--layers 3] [--feature "Top surface"] [--short 10] [--list 40]
      extrusion runs (unbroken extrusion between non-extruding moves) per feature: count, total, p10/median/p90,
      runs under 5 mm and under --short mm; with --feature, each short run's length, radius and angle of its
      midpoint from the part center (the extruded bounding box's center) and whether a retraction came before it

--layers takes N, A-B or all (default all); layers count from 0 at the first ; CHANGE_LAYER.
"""
import argparse
import collections
import math
import re

FIL_AREA = math.pi * (1.75 / 2) ** 2
MOVE = re.compile(r'G([0123])\s')
AXES = re.compile(r'([XYZEFIJ])(-?[\d.]+)')


def bead_area(w, h):
    """Orca's bead cross-section for line width w and layer height h (mm2)."""
    return (w - h) * h + math.pi * (h / 2) ** 2


def moves(path):
    """Yields one dict per G0-G3 move: layer, feature, width, height, fan, temp, start and end xy, z, e, dist
    (arc length for G2/G3), feed (mm/min); and 'wipe' events as {'wipe': True, 'layer': n}."""
    x = y = z = 0.0
    f = 0.0
    feat, w, h, layer, fan, temp = '?', 0.0, 0.0, -1, None, None
    for line in open(path, errors='replace'):
        if line.startswith(';'):
            if line.startswith('; CHANGE_LAYER'):
                layer += 1
            elif line.startswith('; FEATURE:'):
                feat = line[10:].strip()
            elif line.startswith('; LINE_WIDTH:'):
                w = float(line[13:])
            elif line.startswith('; LAYER_HEIGHT:'):
                h = float(line[15:])
            elif line.startswith('; WIPE_START'):
                yield {'wipe': True, 'layer': layer}
            continue
        if line.startswith('M106'):
            m = re.search(r'S(\d+)', line)
            fan = int(m.group(1)) if m else fan
            continue
        if line.startswith('M107'):
            fan = 0
            continue
        if line.startswith(('M104', 'M109')):
            m = re.search(r'S(\d+)', line)
            temp = int(m.group(1)) if m else temp
            continue
        m = MOVE.match(line)
        if not m:
            continue
        d = {k: float(v) for k, v in AXES.findall(line.split(';')[0])}
        nx, ny, nz = d.get('X', x), d.get('Y', y), d.get('Z', z)
        f = d.get('F', f)
        e = d.get('E', 0.0)
        dist = math.hypot(nx - x, ny - y)
        if m.group(1) in '23' and ('I' in d or 'J' in d):
            cx, cy = x + d.get('I', 0.0), y + d.get('J', 0.0)
            r = math.hypot(x - cx, y - cy)
            da = math.atan2(ny - cy, nx - cx) - math.atan2(y - cy, x - cx)
            if m.group(1) == '2':
                da = da if da < 0 else da - 2 * math.pi
            else:
                da = da if da > 0 else da + 2 * math.pi
            if dist < 1e-9:
                da = 2 * math.pi
            dist = abs(da) * r
        yield dict(layer=layer, feat=feat, w=w, h=h, fan=fan, temp=temp, x0=x, y0=y, x1=nx, y1=ny, z0=z, z=nz,
                   e=e, dist=dist, feed=f)
        x, y, z = nx, ny, nz


def layer_range(spec):
    if spec in (None, 'all'):
        return lambda n: True
    if '-' in spec:
        a, b = (int(v) for v in spec.split('-'))
        return lambda n: a <= n <= b
    return lambda n: n == int(spec)


def cmd_layers(path, want):
    S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0.0]))
    L = collections.defaultdict(collections.Counter)
    fans, temps = collections.defaultdict(set), collections.defaultdict(set)
    for mv in moves(path):
        n = mv['layer']
        if not want(n):
            continue
        if mv.get('wipe'):
            L[n]['wipes'] += 1
            continue
        fans[n].add(mv['fan']); temps[n].add(mv['temp'])
        e, dist = mv['e'], mv['dist']
        if e > 0 and dist > 0:
            s = S[n][mv['feat']]
            s[0] += dist; s[1] += e * FIL_AREA; s[2] += dist / (mv['feed'] / 60) if mv['feed'] else 0; s[3] += 1
            s[4] += dist * bead_area(mv['w'], mv['h']) if mv['h'] > 0 else 0
        elif e < 0:
            L[n]['retracts'] += 1
        if mv['z'] > mv['z0'] + 1e-6 and dist == 0 and e == 0:
            L[n]['zlifts'] += 1
        if e == 0 and dist > 0:
            L[n]['travels'] += 1; L[n]['travel_mm'] += dist
    for n in sorted(S):
        info = {k: round(v, 1) for k, v in L[n].items()}
        print(f"-- layer {n}  fan {sorted(v for v in fans[n] if v is not None)}  "
              f"temp {sorted(v for v in temps[n] if v is not None)}  {info}")
        for ft, s in sorted(S[n].items(), key=lambda kv: -kv[1][1]):
            t = s[2]
            print(f"   {ft:26s} len {s[0]:8.1f} mm  vol {s[1]:7.1f} mm3  t {t:6.1f} s  "
                  f"avg {s[0] / t if t else 0:6.1f} mm/s  flow {s[1] / t if t else 0:5.2f} mm3/s  "
                  f"fill {s[1] / s[4] if s[4] else 0:.3f}  segs {s[3]}")


def cmd_runs(path, want, feature, short, nlist):
    runs, cur, retr = [], None, False
    xs, ys = [], []
    for mv in moves(path):
        if mv.get('wipe') or not want(mv['layer']):
            continue
        e, dist = mv['e'], mv['dist']
        if e > 0 and dist > 0:
            if cur is None:
                cur = dict(layer=mv['layer'], feat=mv['feat'], len=0.0, retr=retr, a=(mv['x0'], mv['y0']))
            cur['len'] += dist
            cur['b'] = (mv['x1'], mv['y1'])
            xs.append(mv['x1']); ys.append(mv['y1'])
            retr = False
        else:
            if cur:
                runs.append(cur)
            cur = None
            if e < 0:
                retr = True
    if cur:
        runs.append(cur)
    if not runs:
        print('no extrusion on those layers'); return
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    print(f'{path}  part center {cx:.1f}, {cy:.1f}')
    for ft in sorted({r['feat'] for r in runs}):
        Ls = sorted(r['len'] for r in runs if r['feat'] == ft)
        q = lambda a: Ls[min(len(Ls) - 1, int(a * len(Ls)))]
        print(f"   {ft:24s} runs {len(Ls):5d}  total {sum(Ls):8.0f} mm  p10 {q(.1):6.1f}  median {q(.5):6.1f}  "
              f"p90 {q(.9):6.1f}  <5mm {sum(1 for v in Ls if v < 5):5d}  <{short:g}mm {sum(1 for v in Ls if v < short):5d}")
    if feature:
        sel = [r for r in runs if r['feat'] == feature]
        sh = sorted((r for r in sel if r['len'] < short), key=lambda r: r['len'])
        print(f"{feature}: {len(sel)} runs, {len(sh)} under {short:g} mm, {sum(1 for r in sh if r['retr'])} of those "
              f"right after a retraction (all runs: {sum(1 for r in sel if r['retr'])})")
        for r in sh[:nlist]:
            mx = (r['a'][0] + r['b'][0]) / 2 - cx
            my = (r['a'][1] + r['b'][1]) / 2 - cy
            print(f"   layer {r['layer']:3d}  {r['len']:5.1f} mm  r {math.hypot(mx, my):5.1f}  "
                  f"angle {math.degrees(math.atan2(my, mx)):5.0f}  after retraction {r['retr']}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['layers', 'runs'])
    ap.add_argument('gcode')
    ap.add_argument('--layers', default='all')
    ap.add_argument('--feature', default=None, help='runs: list this feature\'s short runs (e.g. "Top surface")')
    ap.add_argument('--short', type=float, default=10.0)
    ap.add_argument('--list', type=int, default=40)
    a = ap.parse_args()
    if a.cmd == 'layers':
        cmd_layers(a.gcode, layer_range(a.layers))
    else:
        cmd_runs(a.gcode, layer_range(a.layers), a.feature, a.short, a.list)

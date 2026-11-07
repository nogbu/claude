#!/usr/bin/env python3
"""insertMeasure: measures a nursery-pots insert 3mf (any size, nurseryPots_lib.build_insert layout) from its
mesh, in the in-use frame (rim at z = 0, ceiling up). Feeds insertPicture.py's labels; also a quick check that a
build matches its stated values (2026-10-09, 2.5in insert concept).

  python3 insertMeasure.py MODEL.3mf        prints the values as JSON

Layout assumed: radial slots and side notches at 0/90/180/270 deg, diagonal holes at 45 deg, center hole.
Needs projects/3dp/scripts on the path (meshmeasure, dpcheck), trimesh and numpy.
"""
import json
import math
import os
import sys

import numpy as np

_S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'scripts')
sys.path.insert(0, next((d for d in (_S, os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', '/nonexistent'), 'projects/3dp/scripts'),
                                     '/home/user/claude/projects/3dp/scripts', '/home/claude/claude/projects/3dp/scripts')
                       if os.path.isdir(d)), _S))   # the repo's, also from a scratch copy
from meshmeasure import load_part, first_hit, bisect, outer_r, inner_r, solid_top, lean_deg, unit, true_runs  # noqa: E402


def measure(path):
    m, H = load_part(path, flip=True)
    out = dict(H=H, watertight=bool(m.is_watertight), plastic_cm3=float(m.volume / 1000))
    r = np.hypot(m.vertices[:, 0], m.vertices[:, 1])
    out['widest_r'] = float(r.max()); out['widest_D'] = 2 * out['widest_r']
    out['z_widest'] = float(m.vertices[np.argmax(r), 2])
    zs = [f * H for f in (0.15, 0.35, 0.55, 0.75)]
    out['lean_deg'], _ = lean_deg(m, zs)
    out['wall_level'] = outer_r(m, H / 2) - inner_r(m, H / 2)       # horizontal wall thickness at mid-height
    u = unit(22.5)
    top = first_hit(m, u * 6 + [0, 0, H + 5], [0, 0, -1]); under = first_hit(m, u * 6 + [0, 0, 1], [0, 0, 1])
    out['ceiling_under_z'] = float(under[2]); out['ceiling_T'] = float(top[2] - under[2])
    st = lambda x, y: solid_top(m, x, y, H)
    out['flat_r'] = bisect(lambda s: st(*(u[:2] * s)), 4.0, out['widest_r'])
    # openings, as seen on the top face (bed-side chamfers included): along +x the center hole then a slot,
    # along 45 deg the center hole then the diagonal holes
    gaps = lambda d: true_runs(lambda s: not st(*(d * s)), 0.0, out['flat_r'] - 0.02)
    gx = gaps(np.array([1.0, 0.0]))
    out['center_hole_D'] = 2 * gx[0][1]
    out['slot_r0'], out['slot_r1'] = gx[1]
    xm = (out['slot_r0'] + out['slot_r1']) / 2
    out['slot_w'] = 2 * bisect(lambda y: st(xm, y), 3.0 + out['flat_r'] * 0.05, 0.0)
    gd = gaps(unit(45.0)[:2])[1:]
    out['diag_hole_D'] = gd[0][1] - gd[0][0]
    out['diag_hole_r'] = [round((p + q) / 2, 4) for p, q in gd]
    # notch on +x, open at the rim
    wall_at = lambda y, z: (lambda p: p is not None and p[0] > 0)(   # near wall hit, not the far side
        first_hit(m, (out['widest_r'] + 20, y, z), (-1, 0, 0)))
    out['notch_top'] = bisect(lambda z: not wall_at(0.0, z), 0.3, out['ceiling_under_z'] - 0.3)
    out['notch_w'] = 2 * bisect(lambda y: not wall_at(y, 0.3 * out['notch_top']), 0.0, 3.0)
    # outer edge profile near the ceiling: depth below the top vs radius, on vertex levels
    zl = sorted({round(float(z), 6) for z in m.vertices[:, 2] if z > H - 10.0 and z < H - 1e-6} |
                {H - 3.0 - 0.4 * i for i in range(18)}, reverse=True)   # down to 10 mm: scaled 6in shoulder
    prof = [(0.0, out['flat_r'])] + [(H - z, outer_r(m, z)) for z in zl]
    out['edge_profile'] = prof
    sl = [(prof[i + 1][1] - prof[i][1]) / (prof[i + 1][0] - prof[i][0]) for i in range(len(prof) - 1)]
    k = 0
    while k < len(sl) and abs(sl[k] - 1.0) < 0.02:
        k += 1
    out['chamfer_depth'] = prof[k][0]                               # end of the 45 deg run from the top
    tl = math.tan(math.radians(out['lean_deg'])); j = len(sl)
    while j > 0 and abs(sl[j - 1] - tl) < 1e-3:
        j -= 1
    out['curve_end_depth'] = prof[j][0]                             # start of the straight wall
    return out, m, H


if __name__ == '__main__':
    o, _, _ = measure(sys.argv[1])
    o.pop('edge_profile')
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items()}, indent=1))

#!/usr/bin/env python3
"""insertPicture: the standard six-panel picture of a nursery-pots insert, every label measured from the model
by insertMeasure.py (2026-10-09, 2.5in insert concept): in use from above and below, a quarter of the ceiling
from above, a notch, the ceiling edge cut open, and the insert cut in half on its pot's floor with the waterline
and air gap.

  python3 insertPicture.py MODEL.3mf POT OUT.png [--title "first title line"] [--waterline Z] [--floor Z]

POT is either a pot build script that defines profile(), build_mesh(), FLOOR and Z_SB (2.5inPot_rev2.py), or the
pot's 3mf with --waterline (slot bottom, mm) and optionally --floor (else measured at r 3 mm), as for pots built
by nurseryPots_lib.build_pot (e.g. 6inPot_rev2.py writes 6inPot_rev2.3mf); --ray-start R starts the floor-gap
ray past the pot's floor ridge (6in: 50). Needs projects/3dp/scripts (render3d,
meshmeasure), trimesh, manifold3d and matplotlib.
"""
import argparse
import importlib.util
import math
import os
import sys

import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'scripts')
sys.path.insert(0, next((d for d in (_S, os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', '/nonexistent'), 'projects/3dp/scripts'),
                                     '/home/user/claude/projects/3dp/scripts', '/home/claude/claude/projects/3dp/scripts')
                       if os.path.isdir(d)), _S))   # the repo's, also from a scratch copy
import render3d as R  # noqa: E402
from insertMeasure import measure  # noqa: E402
from meshmeasure import load_part, first_hit, inner_r  # noqa: E402

POT_COL, INS = np.array([0.62, 0.78, 0.90]), R.BONE
f2 = lambda v: f"{v:.2f}".rstrip('0').rstrip('.')


def show(ax, meshes, eye, title, light=(0.3, -0.7, 1.0), pad=6.0):
    R.FACES.clear()
    for m, col in meshes:
        R.mesh(m, col)
    return R.view(ax, eye=eye, pad=pad, title=title, light=light)


def crop(m, lo, hi):
    return m.intersection(trimesh.creation.box(bounds=[lo, hi]), engine='manifold')


def pot_parts(pot, waterline=None, floor=None, ray_start=1.0):
    """(pot mesh, floor top z, waterline z, inner radius function) from a pot script or a pot 3mf."""
    if pot.endswith('.py'):
        spec = importlib.util.spec_from_file_location('pot', pot)
        p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
        M, _ = p.build_mesh()
        return trimesh.Trimesh(np.array(M.V), np.array(M.T), process=True), p.FLOOR, p.Z_SB, p.profile()['r_in']
    assert waterline is not None, 'a pot 3mf needs --waterline'
    pm, Hp = load_part(pot)
    if floor is None:
        floor = float(first_hit(pm, (3.0, 1.0, Hp + 5), (0, 0, -1))[2])
    return pm, floor, waterline, lambda z: min(r for r in (inner_r(pm, z, g, ray_start) for g in (22.5, 11.25, 33.75, 3.0)) if r)


def draw(path, pot_file, out_png, title=None, waterline=None, floor=None, ray_start=1.0):
    pmesh, FLOOR, Z_SB, rin = pot_parts(pot_file, waterline, floor, ray_start)
    me, use, H = measure(path)
    rmax, D = me['widest_r'], me['widest_D']
    _pd, _pr = zip(*me['edge_profile'])
    pr = lambda d: float(np.interp(d, _pd, _pr))
    fig = plt.figure(figsize=(21, 15))
    # 1: in use, from above
    ax = fig.add_subplot(2, 3, 1)
    cam = show(ax, [(use, INS)], (-1.0, -1.6, 1.3), 'In use, from above (ceiling up)')
    zw = me['z_widest']
    R.dim(ax, cam, (-rmax, 0, zw), (rmax, 0, zw), (0, -rmax - 4, 0), 'widest Ø ' + f2(D))
    R.dim(ax, cam, (rmax, -rmax, 0), (rmax, -rmax, H), (3, 0, 0))
    R.source(ax, path, cam)
    # 2: in use, from below
    ax = fig.add_subplot(2, 3, 2)
    show(ax, [(use, INS)], (-1.0, -1.6, -0.9), 'In use, from below (rim and notches)', light=(-1.0, -1.6, -0.9))
    # 3: one quarter of the ceiling, from above
    ax = fig.add_subplot(2, 3, 3)
    q = crop(use, (-2, -rmax - 2, 0), (rmax + 2, 2, H + 1))
    cam = show(ax, [(q, INS)], (0.0, -0.25, 1.0), 'Ceiling close-up (top view, one quarter)', pad=3.0)
    xm = (me['slot_r0'] + me['slot_r1']) / 2
    R.dim(ax, cam, (xm, me['slot_w'] / 2, H), (xm, -me['slot_w'] / 2, H), (0, 0, 0))
    hx = me['diag_hole_r'][0] / math.sqrt(2); hd = me['diag_hole_D'] / 2
    R.dim(ax, cam, (hx - hd, -hx, H), (hx + hd, -hx, H), (0, -0.8 * hd - 1.6, 0), 'Ø ' + f2(me['diag_hole_D']))
    R.dim(ax, cam, (0, 0.3, H), (me['slot_r1'], 0.3, H), (0, 0.12 * rmax, 0), 'slot end r ' + f2(me['slot_r1']))
    u = np.array([math.cos(math.radians(-22.5)), math.sin(math.radians(-22.5)), 0])
    R.dim(ax, cam, (0, 0, H), tuple(u * me['flat_r'] + [0, 0, H]), (0, 0, 0), 'flat top r ' + f2(me['flat_r']))
    # 4: a notch, from the side
    ax = fig.add_subplot(2, 3, 4)
    nt = me['notch_top']
    n = crop(use, (-6, -rmax - 2, -1), (6, -rmax + 6, nt + 4))
    cam = show(ax, [(n, INS)], (0.0, -1.0, 0.25), 'Notch close-up (side, rim at the bottom)', pad=3.0)
    R.dim(ax, cam, (-me['notch_w'] / 2, -rmax, 0), (me['notch_w'] / 2, -rmax, 0), (0, 0, -1.6))
    R.dim(ax, cam, (me['notch_w'] / 2 + 0.4, -rmax, 0), (me['notch_w'] / 2 + 0.4, -rmax, nt), (3.0, 0, 0))
    # 5: ceiling edge, cut on the 22.5 deg line (clear of slots and holes), seen square to the cut
    ax = fig.add_subplot(2, 3, 5)
    ur = use.copy(); ur.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-22.5), (0, 0, 1)))
    e = crop(ur, (me['flat_r'] - 6.0, 0.0, H - 6.0), (rmax + 2, 8.0, H + 1))
    cam = show(ax, [(e, INS)], (0.0, -1.0, 0.0), 'Ceiling edge close-up (cut, in use)', light=(0.2, -1.0, 0.3), pad=2.0)
    r_ch, r_ce = pr(me['chamfer_depth']), pr(me['curve_end_depth'])
    R.dim(ax, cam, (r_ch, 0, H), (r_ch, 0, H - me['chamfer_depth']), (0.3, 0, 0), '45° chamfer ' + f2(me['chamfer_depth']))
    R.dim(ax, cam, (r_ce, 0, H), (r_ce, 0, H - me['curve_end_depth']), (3.0, 0, 0), 'curve ends ' + f2(me['curve_end_depth']))
    R.dim(ax, cam, (me['flat_r'] - 4.0, 0, H), (me['flat_r'] - 4.0, 0, me['ceiling_under_z']), (-0.8, 0, 0),
          'ceiling ' + f2(me['ceiling_T']))
    R.call(ax, cam, (pr(3.4), 0, H - 3.4), (40, -70),
           f"wall {me['wall_level']:.2f} mm thick (level), leaning in {me['lean_deg']:.1f}°", color='#1f5fa8')
    # 6: cut in half on the pot's floor
    ax = fig.add_subplot(2, 3, 6)
    inp = use.copy(); inp.apply_translation((0, 0, FLOOR))
    half = lambda m: crop(m, (-200, 0, -1), (200, 200, 300))
    cam = show(ax, [(half(pmesh), POT_COL), (half(inp), INS)], (0.0, -1.0, 0.08),
               f'Cut in half, on the floor of {os.path.splitext(os.path.basename(pot_file))[0]} (side view)', pad=4.0)
    rw = rin(Z_SB + 0.01)
    R.dim(ax, cam, (-rw, 0, Z_SB), (-rw, 0, FLOOR + me['ceiling_under_z']), (-9, 0, 0),
          'air gap ' + f2(FLOOR + me['ceiling_under_z'] - Z_SB))
    a2, b2 = R.proj(cam, (-rw, 0, Z_SB)), R.proj(cam, (rw, 0, Z_SB))
    ax.plot([a2[0], b2[0]], [a2[1], b2[1]], color='#1f5fa8', lw=1.2, ls=(0, (5, 3)))
    R.call(ax, cam, (rw, 0, Z_SB), (60, 40), f'waterline (slot bottom) {f2(Z_SB)} mm', color='#1f5fa8')
    R.call(ax, cam, (rmax + 0.6, 0, FLOOR + zw), (80, -25),
           f'{rin(FLOOR) - rmax:.2f} mm gap each side at the floor', color='#1f5fa8')
    R.call(ax, cam, (0, 0, FLOOR + H), (-120, 55), f'ceiling top {f2(FLOOR + H)} mm', color='#1f5fa8')
    if abs(me['lean_deg']) > 0.05:
        p0, p1 = R.proj(cam, (-rmax, 0, FLOOR + zw)), R.proj(cam, (-rmax, 0, FLOOR + H))
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#c0392b', lw=1.0, ls=(0, (3, 2)))
        R.call(ax, cam, (-rmax, 0, FLOOR + 0.4 * H), (-95, -45),
               f"dashed: vertical; wall leans in {me['lean_deg']:.1f}°", color='#c0392b')
    head = title or os.path.basename(path)[:-4]
    fig.suptitle(f"{head}\nwidest Ø {f2(D)} mm, {f2(H)} mm tall, walls leaning in {me['lean_deg']:.1f}°, notches "
                 f"{f2(me['notch_w'])} × {f2(me['notch_top'])} mm, slots {f2(me['slot_w'])} mm, holes Ø "
                 f"{f2(me['diag_hole_D'])} mm, {me['plastic_cm3']:.2f} cm³; printed ceiling-down", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=4.0)
    R.save(fig, out_png)
    return me


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('model'); ap.add_argument('pot'); ap.add_argument('out')
    ap.add_argument('--title', default=None)
    ap.add_argument('--waterline', type=float, default=None)
    ap.add_argument('--floor', type=float, default=None)
    ap.add_argument('--ray-start', type=float, default=1.0,
                    help='pot 3mf: radius the floor-gap ray starts at, past any floor ridge (6in: 50)')
    a = ap.parse_args()
    draw(a.model, a.pot, a.out, a.title, a.waterline, a.floor, a.ray_start)

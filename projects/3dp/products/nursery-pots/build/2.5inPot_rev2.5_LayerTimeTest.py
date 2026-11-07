#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.5_LayerTimeTest.3mf (nursery-pots, 3dp project): one 2.5in rev2 pot alone,
cut flat at 40.68 mm (113 layers, 10 mm above the slot top, includes the whole slot band), to test
whether the grainy patch right of the seam on plates comes from the longer time between layers at
the seam rather than from the jump between pots.

Changes from rev2 (agreed 2026-10-01):
- Filament minimum layer time 8 -> 16 s (slow_down_layer_time, filament 1), so the solo pot's seam
  waits about as long between layers as on a 2-pot plate (16 s is an inference from plate timing).
  Orca reaches it by slowing the print, not by waiting: the outer wall prints at about 12 mm/s
  (sliced G-code median, Orca 2.4.2), so a missing patch is inconclusive.
- Z-hop 0.6 mm and retraction 0.8 mm, as rev2.2_SeamTest; no extra length on restart (rev2.4's
  0.1 mm left the patch unchanged and made slot-edge blobs and slot-band bubbles worse).
- Cut at 40.68 mm: the wall ends in a flat top at 40.68 mm; no lip.
- One pot at the bed center, as solo rev2.
Everything else (mesh below the cut, seam paint, object settings, height ranges, fan ramp) is rev2's.
Needs beside it: 2.5inPot_rev2.py, 2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.2_SeamTest.py,
nurseryPots_lib.py and nurseryPots_settings_base.json (all used unchanged).
"""
import importlib.util
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('seamtest', os.path.join(HERE, '2.5inPot_rev2.2_SeamTest.py'))
st = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(st)
pot, lib = st.pot, st.lib

NAME = '2.5inPot_rev2.5_LayerTimeTest'
Z_CUT = 40.68            # 113 layers of 0.36 mm
MIN_LAYER_TIME = 16      # s, filament 1


def build_mesh_cut():
    """rev2's mesh with the lip levels replaced by one level at Z_CUT and a flat top."""
    P = pot.profile()
    r_out, r_in = P['r_out'], P['r_in']
    assert pot.Z_ST < Z_CUT < P['z_lb']
    centers = [22.5 + 45.0 * k for k in range(8)]
    M = lib.Mesh()
    lv = [(0.0, P['r_base'], 0.0), (pot.Z_CE, P['r_ce'], 0.0)]
    for k in range(1, pot.N_ARC):
        phi = math.radians(-45.0 + (45.0 - pot.ALPHA) * k / pot.N_ARC)
        lv.append((P['zc'] + pot.RF * math.sin(phi), P['rc'] + pot.RF * math.cos(phi), 0.0))
    lv.append((P['z_t'], r_out(P['z_t']), 0.0))
    band_start = len(lv)
    for z, hw in lib.band_levels(pot.Z_SB, pot.Z_ST, pot.SLOT_W):
        lv.append((z, r_out(z), hw))
    band_end = len(lv)
    lv.append((Z_CUT, r_out(Z_CUT), 0.0))
    outer = [lib.ring(M, r, z, centers, hw) for (z, r, hw) in lv]
    lv_in = [(pot.FLOOR, r_in(pot.FLOOR), 0.0)] + [(z, r_in(z), hw) for (z, r, hw) in lv if z > pot.FLOOR + 1e-9]
    inner = [lib.ring(M, r, z, centers, hw) for (z, r, hw) in lv_in]
    shift = len(lv) - len(lv_in)

    c0 = M.add(0, 0, 0.0)
    lib.fan(M, c0, outer[0][0], 'underside')
    for k in range(len(outer) - 1):
        lib.strip(M, outer[k][0], outer[k + 1][0], 'outer')
    lib.strip(M, outer[-1][0], inner[-1][0], 'top')
    for k in range(len(inner) - 1):
        lib.strip(M, inner[k][0], inner[k + 1][0], 'inner')
    c1 = M.add(0, 0, pot.FLOOR)
    lib.fan(M, c1, inner[0][0], 'floor')
    lib.side_walls(M, [outer[k][1] for k in range(band_start, band_end)],
                   [inner[k][1] for k in range(band_start - shift, band_end - shift)])
    vol = lib.orient_and_check(M)
    return M, dict(plastic_cm3=vol / 1000.0, base_diameter=2 * P['r_base'],
                   vertices=len(M.V), triangles=len(M.T))


def overrides():
    o = st.overrides()   # z-hop 0.6, retraction 0.8
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    lt = list(base['slow_down_layer_time']); lt[0] = lib._fmt(MIN_LAYER_TIME)
    o['slow_down_layer_time'] = lt
    return o


def main(out_dir='.'):
    M, info = build_mesh_cut()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    info['painted_triangles'] = int(painted.sum())
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(pot.OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, Z_CUT, painted, obj, pot.layer_ranges(), overrides(),
                  fan_ramp=False, plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    info['path'] = path
    return info


if __name__ == '__main__':
    print(main())

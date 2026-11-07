#!/usr/bin/env python3
"""Builds 6inInsert_rev2.3_DiscSettings.3mf (nursery-pots, 3dp project): a one-change test for the rough
6in insert ceiling. My 2234567.3mf (2026-10-09) printed plate 1 (the rev2.2 ceiling, carrying its object
settings) rough and plate 3 (my Fusion 360 disc, 1.2 mm thick, with a 4 mm center hole and 4 radial
3.0 x 28 mm slots, no object settings) smooth. This file is plate 3 with plate 1's object settings
copied onto the disc and nothing else changed, so a rough print points at those settings (agreed 2026-10-09).

Data beside it: fusionDisc_centerHole_4slots.stl (plate 3's mesh, unchanged) and
6inInsert_rev2.3_settings_base.json (2234567.3mf's project settings, unchanged). write3mf turns support
off, since nothing is painted (the file's tree(manual) support made no support).
"""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'scripts'))
import write3mf as W  # noqa: E402

NAME = '6inInsert_rev2.3_DiscSettings'
# plate 1's object settings in 2234567.3mf (object "6inInsert_rev2.2_PotSettings"), in its order
PLATE1_OBJECT_SETTINGS = [
    ('inner_wall_line_width', '1.2'), ('internal_solid_infill_speed', '60'), ('outer_wall_flow_ratio', '1.03'),
    ('outer_wall_line_width', '1.2'), ('outer_wall_speed', '28'), ('scarf_joint_flow_ratio', '1'),
    ('scarf_joint_speed', '100%'), ('seam_gap', '0%'), ('seam_position', 'back'),
    ('seam_slope_conditional', '0'), ('seam_slope_entire_loop', '0'), ('seam_slope_inner_walls', '0'),
    ('seam_slope_min_length', '12'), ('seam_slope_start_height', '20%'), ('seam_slope_steps', '20'),
    ('staggered_inner_seams', '1'), ('top_surface_speed', '60')]


def read_stl(path):
    data = open(path, 'rb').read()
    n = struct.unpack('<I', data[80:84])[0]
    tri = np.frombuffer(data[84:84 + 50 * n], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    P = tri['v'].reshape(-1, 3).astype(float)
    V, inv = np.unique(P.round(5), axis=0, return_inverse=True)
    return V, inv.reshape(-1, 3)


def disc_mesh():
    """Plate 3's disc, base on z = 0 (rev2.4 reuses it)."""
    V, T = read_stl(os.path.join(HERE, 'fusionDisc_centerHole_4slots.stl'))
    V[:, 2] -= V[:, 2].min()
    return V, T


def write(name, V, T, plate_name):
    settings = W.base(os.path.join(HERE, '6inInsert_rev2.3_settings_base.json'))
    disc = W.Obj(name, [W.Part(V, T)], settings=PLATE1_OBJECT_SETTINGS, at=[(128, 128)])
    path = W.write(os.path.join(HERE, name + '.3mf'), [disc], settings, plate_name=plate_name)
    print(dict(path=path, verts=len(V), tris=len(T), size=(V.max(0) - V.min(0)).round(3).tolist()))


if __name__ == '__main__':
    write(NAME, *disc_mesh(), '6inInsert rev2.3 DiscSettings')

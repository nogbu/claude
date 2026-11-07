#!/usr/bin/env python3
"""Builds 2.5inPot_rev1.3mf (nursery-pots, 3dp project).
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it (both used unchanged).
Values from nursery-pots state.md (2.5in pot, agreed 2026-10-01). Every Z feature is on the
0.36 mm layer grid (config Grid lock).

Where this pot differs from the family's shared design (handled here, not in the library):
- Foot: 45 deg chamfer to 1.80 mm (5 layers), then a 9.88 mm radius curve that ends at
  7.92 mm (22 layers) tangent to the 5.03 deg wall.
- Lip: chamfer 2.16 mm tall (lip base 75.24 mm, chamfer top 77.40 mm), overhang 2.187 mm.
- Floor 1.44 mm (4 layers), flat, with no drip groove or floor ridge; the floor height range
  is 0-1.44 mm.
- Fan ramp (45/30/15/0 %) at 6.12 / 6.84 / 7.56 / 8.28 mm.
- No insert.
"""
import io
import math
import os
import zipfile

import numpy as np

import nurseryPots_lib as lib

NAME = '2.5inPot_rev1'
L = 0.36                 # layer height (first layer too)
H = 79.56                # 221 layers
R_LIP = 35.5             # top (lip) diameter 71.0 mm
T = 1.00                 # wall, single bead
ALPHA = 5.03             # wall angle, deg
FLOOR = 1.44             # 4 layers
SLOT_W = 1.5             # 8 stadium slots
Z_SB, Z_ST = 24.48, 30.60    # slot bottom (waterline) and top: 68 and 85 layers, 6.12 mm tall
BAND_BEAD = 0.54         # slot band: 2 beads (2 x 0.54 - 0.077 = 1.003 mm)
WALL_LINE_WIDTH = 1.05   # object wall line width, keeps one bead elsewhere
OUTER_WALL_SPEED = 34
LIP_H = 4.32             # lip base at H - 4.32 = 75.24 mm (209 layers)
LIP_OVER = 2.187         # lip overhang past the wall
LIP_RISE = 2.16          # lip chamfer height: top at 77.40 mm (215 layers)
Z_CE = 1.80              # foot chamfer top (5 layers)
Z_T = 7.92               # foot curve end (22 layers)
RF = (Z_T - Z_CE) / (math.sin(math.radians(45.0)) - math.sin(math.radians(ALPHA)))   # 9.880 mm
N_ARC = 26
FAN_RAMP = ((6.12, 45, 115), (6.84, 30, 77), (7.56, 15, 38), (8.28, 0, 0))
# Seam enforcer strip: whole 0.5 deg columns, right edge 0.5 deg past the slot midpoint (90 deg)
# as on every family pot, centered 1.25 deg left of it (0.60 mm at the foot top, 0.73 mm at
# the lip base).
PAINT_SPAN = (87.0, 90.5)


def profile():
    a = math.radians(ALPHA)
    ta = math.tan(a)
    z_lb = H - LIP_H
    r_lb = R_LIP - LIP_OVER

    def r_wall(z):
        return r_lb - (z_lb - z) * ta

    zc = Z_CE + RF / math.sqrt(2)          # foot arc center height
    z_t = zc - RF * math.sin(a)            # arc meets the wall (= Z_T)
    rc = r_wall(z_t) - RF * math.cos(a)    # foot arc center radius
    r_ce = rc + RF / math.sqrt(2)
    r_base = r_ce - Z_CE

    def r_out(z):
        if z <= Z_CE:
            return r_base + z
        if z <= z_t:
            return rc + math.sqrt(max(RF * RF - (z - zc) ** 2, 0.0))
        if z <= z_lb:
            return r_wall(z)
        if z <= z_lb + LIP_RISE:
            return r_lb + (z - z_lb) * (LIP_OVER / LIP_RISE)
        return R_LIP

    def r_in(z):
        return (r_out(z) if z <= z_t else r_wall(z)) - T

    return dict(z_lb=z_lb, r_lb=r_lb, zc=zc, z_t=z_t, rc=rc, r_ce=r_ce, r_base=r_base,
                r_wall=r_wall, r_out=r_out, r_in=r_in)


def build_mesh():
    P = profile()
    r_out, r_in = P['r_out'], P['r_in']
    centers = [22.5 + 45.0 * k for k in range(8)]
    M = lib.Mesh()

    # outer levels (z, r, slot half-width)
    lv = [(0.0, P['r_base'], 0.0), (Z_CE, P['r_ce'], 0.0)]
    for k in range(1, N_ARC):
        phi = math.radians(-45.0 + (45.0 - ALPHA) * k / N_ARC)
        lv.append((P['zc'] + RF * math.sin(phi), P['rc'] + RF * math.cos(phi), 0.0))
    lv.append((P['z_t'], r_out(P['z_t']), 0.0))
    band_start = len(lv)
    for z, hw in lib.band_levels(Z_SB, Z_ST, SLOT_W):
        lv.append((z, r_out(z), hw))
    band_end = len(lv)
    lv += [(P['z_lb'], P['r_lb'], 0.0), (P['z_lb'] + LIP_RISE, R_LIP, 0.0), (H, R_LIP, 0.0)]
    outer = [lib.ring(M, r, z, centers, hw) for (z, r, hw) in lv]

    # inner levels: the floor top, then the outer levels above it
    lv_in = [(FLOOR, r_in(FLOOR), 0.0)] + [(z, r_in(z), hw) for (z, r, hw) in lv if z > FLOOR + 1e-9]
    inner = [lib.ring(M, r, z, centers, hw) for (z, r, hw) in lv_in]
    shift = len(lv) - len(lv_in)

    c0 = M.add(0, 0, 0.0)
    lib.fan(M, c0, outer[0][0], 'underside')            # flat underside, no drip groove
    for k in range(len(outer) - 1):
        lib.strip(M, outer[k][0], outer[k + 1][0], 'outer')
    lib.strip(M, outer[-1][0], inner[-1][0], 'top')
    for k in range(len(inner) - 1):
        lib.strip(M, inner[k][0], inner[k + 1][0], 'inner')
    c1 = M.add(0, 0, FLOOR)
    lib.fan(M, c1, inner[0][0], 'floor')                # flat floor, no ridge
    lib.side_walls(M, [outer[k][1] for k in range(band_start, band_end)],
                   [inner[k][1] for k in range(band_start - shift, band_end - shift)])

    vol = lib.orient_and_check(M)
    zs = np.linspace(FLOOR, Z_SB, 4001)
    area = np.pi * np.array([r_in(z) for z in zs]) ** 2
    reservoir = float(((area[1:] + area[:-1]) / 2 * np.diff(zs)).sum())
    info = dict(plastic_cm3=vol / 1000.0, reservoir_mL=reservoir / 1000.0,
                base_diameter=2 * P['r_base'], foot_radius=RF, z_t=P['z_t'],
                vertices=len(M.V), triangles=len(M.T))
    return M, info


def layer_ranges():
    """The family's five height ranges (library settings), with the floor range ending at
    the floor top because this pot has no floor ridge."""
    rng = lib.pot_layer_ranges(Z_SB, Z_ST, BAND_BEAD)
    rng[0] = (0.0, FLOOR, rng[0][2])
    rng[1] = (FLOOR, rng[1][1], rng[1][2])
    return rng


def fan_ramp_xml():
    rows = ''.join('<layer top_z="%s" type="4" extruder="1" color="" extra="" '
                   'gcode="; fan ramp %d%%&#10;M106 S%d"/>\n' % (lib._fmt(z), pct, s)
                   for z, pct, s in FAN_RAMP)
    return ('<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_layer>\n<plate>\n'
            '<plate_info id="1"/>\n' + rows + '<mode value="SingleExtruder"/>\n</plate>\n'
            '</custom_gcodes_per_layer>\n')


def replace_entry(path, entry, text):
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for i, data in items:
            z.writestr(i, text if i.filename == entry else data)


def main(out_dir='.'):
    M, info = build_mesh()
    painted = lib.paint_seam(M, PAINT_SPAN)
    info['painted_triangles'] = int(painted.sum())
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, H, painted, obj, layer_ranges(), {}, fan_ramp=False,
                  plate_name=NAME.replace('_', ' '))
    replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', fan_ramp_xml())
    info['path'] = path
    return info


if __name__ == '__main__':
    print(main())

#!/usr/bin/env python3
"""Builds 6inInsert_rev3.3mf (nursery-pots, 3dp project), printed ceiling-down (built 2026-10-10, no audit, my ask).
2.5inInsert_rev2 scaled by K to the 6in pot rev2 (my asks 2026-10-10: "scale it"), K the ratio of the pots' inner
radii at the floor (53.308 / 19.857 = 2.6846): rim radius (so the floor gap scales too; then widest Ø 2 mm smaller,
my ask), slot and hole positions,
shoulder and notch depth. My asks: slots and notches 3.0 mm wide; wall 1.24 mm (2 x 0.66 mm beads); ceiling 4
layers (1.6 mm). Holes stay Ø 4 mm (Decisions: Inserts scaled). Wall leans in 5.03 deg (agreed change 2); height
from the air-gap rule (Product rules), not scaled; no chamfers but the shoulder, no opening chamfers (agreed
change 1, learnings/walls). Z values rounded to the 0.4 mm grid.
Needs beside it: nurseryPots_lib.py, nurseryPots_settings_base.json, 2.5inPot_rev2.py; numpy, scipy.
Picture: python3 insertPicture.py 6inInsert_rev3.3mf 6inPot_rev2.3mf OUT.png --waterline 43.56 --ray-start 50
"""
import argparse
import importlib.util
import json
import math
import os

import nurseryPots_lib as lib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pot25', os.path.join(HERE, '2.5inPot_rev2.py'))
pot25 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pot25)

NAME = '6inInsert_rev3'
L = 0.4                                   # insert layer height
FLOOR, Z_SB = 1.80, 43.56                 # 6in pot rev2: floor top, waterline (slot bottoms)
P6 = lib.pot_profile(166.68, 76.2, 1.2)   # 6inPot_rev2.py
R_IN6 = P6['r_in'](FLOOR)                 # 53.308
K = R_IN6 / pot25.profile()['r_in'](pot25.FLOOR)   # 2.6846
SLOPE = 5.03                              # agreed change 2
T, t, BEAD = 1.6, 1.24, 0.66              # ceiling 4 layers, wall (square to its faces), 2 beads (my asks)
SLOT_W = NOTCH_W = 3.0                    # my ask 2026-10-10
OPEN_CH = 0.0                             # no bed-side opening chamfers (learnings/walls)


def grid(z):
    return round(round(z / L) * L, 3)


ZC1, Z2 = grid(1.2 * K), grid(2.4 * K)    # shoulder: 2.5in's 1.2 / 2.4 scaled -> 3.2 / 6.4 (8 / 16 layers)
SLOT_R0 = round(4.12 * K, 2)              # 11.06
HOLE_R = [round(9.15 * K, 2)]             # 24.56
NOTCH_D = grid(9.6 * K)                   # 25.77 -> 25.6 (64 layers)
FLAT_MARGIN = round(2.437 * K, 2)         # slot end to the ceiling's flat edge, 6.54
SHRINK_D = 2.0                            # widest Ø 2 mm smaller than scaled (my ask 2026-10-10)
R_RIM = round(19.117 * K - SHRINK_D / 2, 3)   # 2.5in rev2 rim radius scaled (51.321), less 1.0 -> 50.321


def values():
    th = math.radians(SLOPE); tn = math.tan(th)
    R = R_RIM
    H, air = lib.insert_height(FLOOR, Z_SB, T)
    rho = (Z2 - ZC1) / (math.sqrt(0.5) - math.sin(th))
    flat = R - (H - Z2) * tn - rho * math.cos(th) + rho * math.sqrt(0.5) - ZC1
    return dict(R=R, gap=round(R_IN6 - R, 3), H=H, air_gap=air, rho=round(rho, 4), flat_r=round(flat, 3),
                slot_r1=round(flat - FLAT_MARGIN, 2), K=round(K, 4), zc1=ZC1, z2=Z2, slot_r0=SLOT_R0,
                hole_r=HOLE_R, notch_d=NOTCH_D)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default=NAME)
    a = ap.parse_args()
    v = values()
    print(json.dumps(v))
    info = lib.build_insert(name=a.name, R=v['R'], t=t, H=v['H'], T=T, c=0.0, slot_w=SLOT_W, slot_r0=SLOT_R0,
                            slot_r1=v['slot_r1'], hole_radii=HOLE_R, notch_w=NOTCH_W, notch_d=NOTCH_D, bead=BEAD,
                            out_dir=HERE, slope_deg=SLOPE, shoulder=(ZC1, v['rho']), rim_chamfer=0.0,
                            rim_round=0.0, open_chamfer=OPEN_CH)
    print(info)

#!/usr/bin/env python3
"""Builds 3.5inInsert_rev5.3mf (nursery-pots, 3dp project), printed ceiling-down.
2.5inInsert_rev2 scaled by K to the 3.5in pot rev10.2 (my ask 2026-10-10), K the ratio of the pots' inner radii at
the floor: slot and hole positions, notch depth and the slot ends' margin from the ceiling's flat edge.
The rim keeps the 2.5in rev2's gap to the pot wall at the floor (0.74 mm each side, my ask), not scaled. My asks:
slots and notches 2.0 mm wide, holes Ø 4 mm. Wall 1.0 mm (2 x 0.54 mm beads, the 3.5in pot's slot band) and
ceiling 1.2 mm as the 2.5in; wall leans in 5.03 deg (agreed change 2); height from the air-gap rule (Product rules),
not scaled. No fillets or chamfers anywhere (my ask 2026-10-10, as the 6in rev4): no shoulder, so the wall meets
the ceiling in a square corner; slot ends and notch tops stay rounded. Slot ends stay where the scaled shoulder's
flat-edge margin put them (r 20.68), as the 6in rev4 kept rev3's. Z values on the 0.4 mm grid.
Needs beside it: nurseryPots_lib.py, nurseryPots_settings_base.json, 2.5inPot_rev2.py; numpy, scipy.
Picture: python3 insertPicture.py 3.5inInsert_rev5.3mf 3.5inPot_rev10.2.3mf OUT.png --waterline 33.48
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

NAME = '3.5inInsert_rev5'
L = 0.4                                   # insert layer height
FLOOR, Z_SB = 1.80, 33.48                 # 3.5in pot rev10.2: floor top, waterline (slot bottoms)
P35 = lib.pot_profile(105.12, 48.07, 1.00)   # 3.5inPot_rev10.2.py
R_IN35 = P35['r_in'](FLOOR)
R_IN25 = pot25.profile()['r_in'](pot25.FLOOR)
K = R_IN35 / R_IN25
SLOPE = 5.03                              # agreed change 2
T, t, BEAD = 1.2, 1.0, 0.54               # as the 2.5in rev2
SLOT_W = NOTCH_W = 2.0                    # my ask 2026-10-10
OPEN_CH = 0.0                             # no bed-side opening chamfers (learnings/walls)
GAP = round(R_IN25 - 19.117, 3)           # 2.5in rev2's gap at the floor, kept (my ask)


def grid(z):
    return round(round(z / L) * L, 3)


ZC1, Z2 = grid(1.2 * K), grid(2.4 * K)    # 2.5in's shoulder scaled; only places the slot ends (no shoulder built)
SLOT_R0 = round(4.12 * K, 2)
HOLE_R = [round(9.15 * K, 2)]
NOTCH_D = grid(9.6 * K)
FLAT_MARGIN = round(2.437 * K, 2)         # slot end to the ceiling's flat edge
R_RIM = round(R_IN35 - GAP, 3)


def values():
    th = math.radians(SLOPE); tn = math.tan(th)
    R = R_RIM
    H, air = lib.insert_height(FLOOR, Z_SB, T)
    rho = (Z2 - ZC1) / (math.sqrt(0.5) - math.sin(th))
    flat = R - (H - Z2) * tn - rho * math.cos(th) + rho * math.sqrt(0.5) - ZC1
    return dict(R=R, widest_D=round(2 * R, 3), gap=round(R_IN35 - R, 3), r_in_floor=round(R_IN35, 3), H=H,
                air_gap=air, ceiling_edge_r=round(R - H * tn, 3), rho=round(rho, 4), flat_r=round(flat, 3), slot_r1=round(flat - FLAT_MARGIN, 2),
                K=round(K, 4), zc1=ZC1, z2=Z2, slot_r0=SLOT_R0, hole_r=HOLE_R, notch_d=NOTCH_D,
                notch_d_scaled=round(9.6 * K, 3))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default=NAME)
    ap.add_argument('--values', action='store_true', help='print the values only')
    a = ap.parse_args()
    v = values()
    print(json.dumps(v))
    if not a.values:
        info = lib.build_insert(name=a.name, R=v['R'], t=t, H=v['H'], T=T, c=0.0, slot_w=SLOT_W, slot_r0=SLOT_R0,
                                slot_r1=v['slot_r1'], hole_radii=HOLE_R, notch_w=NOTCH_W, notch_d=NOTCH_D,
                                bead=BEAD, out_dir=HERE, slope_deg=SLOPE, shoulder=None,
                                rim_chamfer=0.0, rim_round=0.0, open_chamfer=OPEN_CH)
        print(info)

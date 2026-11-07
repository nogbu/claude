#!/usr/bin/env python3
"""Builds 2.5inInsert_rev1.3mf (nursery-pots, 3dp project): the 2.5in insert concept, not yet built or printed.
Concept 1 (2026-10-09): 4.5inInsert_rev1 scaled to the 2.5in pot rev2 (rim 1.24 mm inside the pot floor's
wall, x0.46), slots and notches 1.0 mm wide (my ask), holes stay Ø 4 mm. Concept 2 (2026-10-09, my asks):
widest Ø 1 mm smaller (36.23 mm, at the rim chamfer's top), walls leaning in 5.00 deg toward the ceiling, notches
3 mm taller (9.6 mm, 24 layers; my pick of 9.2 / 9.6). Edge: the 6in rev2's shoulder form, a 45 deg chamfer from
the bed to 1.2 mm then a curve tangent to the sloped wall ending at 2.4 mm (both on the 0.4 mm grid; nearest
the scaled 4.5in curve, inference). Slot starts and holes as concept 1; slot ends moved in to keep concept 1's
2.44 mm from the ceiling's flat edge. Height from the air-gap rule (Product rules): 26.0 mm, gap 3.2 mm.
Agreed change 1 (2026-10-09): no chamfers or fillets but the shoulder, so the rim is square (widest Ø kept at the
rim); notch tops stay rounded, round start 9.1 mm off the 0.4 mm grid (dp exception, my pick).
Needs beside it: nurseryPots_lib.py, nurseryPots_settings_base.json, 2.5inPot_rev2.py; numpy, scipy.
Picture: python3 insertPicture.py 2.5inInsert_rev1.3mf 2.5inPot_rev2.py OUT.png
"""
import importlib.util
import json
import math
import os

import nurseryPots_lib as lib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pot25', os.path.join(HERE, '2.5inPot_rev2.py'))
pot = importlib.util.module_from_spec(spec); spec.loader.exec_module(pot)

NAME = '2.5inInsert_rev1'
L = 0.4                                   # insert layer height
GAP = 1.24                                # concept 1: rim inside the pot floor's wall (family rule)
SHRINK_D = 1.0                            # concept 2: widest Ø 1 mm smaller
SLOPE = 5.0                               # wall lean toward the ceiling, deg
RIM_CH = 0.0                              # square rim (agreed change 1)
T, t, BEAD = 1.2, 1.0, 0.54               # ceiling, wall (square to its faces), 2 beads
ZC1, Z2 = 1.2, 2.4                        # shoulder: chamfer top, curve end (3 and 6 layers)
SLOT_W, SLOT_R0, HOLE_R = 1.0, 4.12, [9.15]
NOTCH_W, NOTCH_D = 1.0, 9.6
R45_FLAT_MARGIN = 2.437                   # concept 1: ceiling flat edge 16.617 to slot end 14.18

P = pot.profile()
th = math.radians(SLOPE); tn = math.tan(th)
R1 = round(P['r_in'](pot.FLOOR) - GAP, 3)                 # concept 1 rim radius, 18.617
R = round(R1 - SHRINK_D / 2 + RIM_CH * tn, 3)              # rim radius so the widest point is R1 - 0.5
H = math.ceil(round((pot.Z_SB + 3.0 - pot.FLOOR + T) / L, 6)) * L
RHO = (Z2 - ZC1) / (math.sqrt(0.5) - math.sin(th))
flat = R - (H - Z2) * tn - RHO * math.cos(th) + RHO * math.sqrt(0.5) - ZC1
SLOT_R1 = round(flat - R45_FLAT_MARGIN, 2)

if __name__ == '__main__':
    print(json.dumps(dict(R=R, widest_D=round(2 * (R - RIM_CH * tn), 3), H=H, air_gap=round(pot.FLOOR + H - T - pot.Z_SB, 3),
                          rho=round(RHO, 4), flat_r=round(flat, 3), slot_r1=SLOT_R1)))
    info = lib.build_insert(name=NAME, R=R, t=t, H=H, T=T, c=0.0, slot_w=SLOT_W, slot_r0=SLOT_R0, slot_r1=SLOT_R1,
                            hole_radii=HOLE_R, notch_w=NOTCH_W, notch_d=NOTCH_D, bead=BEAD, out_dir=HERE,
                            slope_deg=SLOPE, shoulder=(ZC1, RHO), rim_chamfer=RIM_CH, rim_round=0.0)
    print(info)

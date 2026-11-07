#!/usr/bin/env python3
"""Builds 6inInsert_rev2.3mf (nursery-pots, 3dp project), printed ceiling-down.
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
rev1 with the 2026-10-08 changes: wall leans in 5.03 deg toward the ceiling (rim Ø kept);
small shoulder (45 deg chamfer to 0.4 mm, then a 1.94 mm curve tangent to the wall at 1.6 mm);
inside offset 1.2 mm square to every face; ceiling 1.2 mm, height 46.0 mm (air gap 3.04 mm);
square rim; notches and slots 3.0 mm wide, notches 18.0 mm deep; 0.4 mm bed-side chamfer on
the ceiling openings. Values from nursery-pots state.md."""
import math
from nurseryPots_lib import build_insert
SLOPE = 5.03
RHO = 1.2 / (math.sqrt(0.5) - math.sin(math.radians(SLOPE)))   # curve rises 1.2 mm (3 layers)
info = build_insert(name='6inInsert_rev2', R=52.075, t=1.2, H=46.0, T=1.2, c=0.0,
                    slot_w=3.0, slot_r0=11.52, slot_r1=39.66, hole_radii=[18.83, 37.66],
                    notch_w=3.0, notch_d=18.0, bead=0.64, rim_chamfer=0.0, rim_round=0.0,
                    open_chamfer=0.4, slope_deg=SLOPE, shoulder=(0.4, RHO))
print(info)

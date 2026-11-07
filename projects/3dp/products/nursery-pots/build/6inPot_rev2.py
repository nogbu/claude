#!/usr/bin/env python3
"""Builds 6inPot_rev2.3mf (nursery-pots, 3dp project).
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
Values from nursery-pots state.md (size table, Shared design, Geometry, agreed changes).
Outer wall 28 mm/s: the 12 mm3/s cap limits a 1.2 x 0.36 mm bead to 27.8 mm/s."""
from nurseryPots_lib import build_pot
info = build_pot(name='6inPot_rev2', H=166.68, R_lip=76.2, t=1.2, floor=1.80,
                 slot_w=2.5, z_sb=43.56, z_st=55.44, band_bead=0.64, outer_wall_speed=28,
                 wall_line_width=1.2, paint_span=(88.5, 90.5))
print(info)

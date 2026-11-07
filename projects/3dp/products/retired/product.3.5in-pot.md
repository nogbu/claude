---
about: Retired 3.5in self-watering pot doc, replaced by nursery-pots
read-when: only for a value nursery-pots lacks
readonly: yes
---
# product.3.5in-pot

Short name: 3.5in-pot. The self-watering pot (3.5 inch), printed in clear PETG with a single-bead wall, used for anthuriums in pon inside a decorative outer pot. Full change history, with the reason for each change, is in 3.5pot-modlog.

## Latest rev

**rev10** (newPot_rev10.3mf), adopted 2026-09-28. Printed 2026-09-28: quality and seam look great; seam position judged fine by eye, no photo measurement needed. **Water test pending.** Unless I say otherwise, new versions start from this design.

## Key parameters and dimensions (rev10)

- **Foot**: 45° flare from a Ø 60 mm base: a straight 45° chamfer to 5.12 mm, then a 10 mm radius curve up into the wall (the curve ends at 11.31 mm). 45° is the angle going forward.  
- **Wall**: 1.05 mm thick, smooth (no seam groove), printed as a single bead. The slot band (the wicking slots) prints as 2 beads at 0.45 mm using a height range modifier.  
- **Floor**: 1.44 mm (4 layers).  
- **Slots**: 8 slots, 1.5 × 8 mm, bottom at 32.5 mm (this sets the waterline).  
- **Size**: 105.12 mm tall, lip Ø 96.14 mm.  
- **Seam**:  
  - A normal seam (no scarf) for the full height, seam position Back.  
  - A painted seam enforcer strip (about 2 mm wide, outer faces only, full height) centered 0.6 mm left of the midpoint between two slots, as seen from outside. The seam starts about 0.6 mm to the right of the paint, which puts the seam line on the midpoint.  
- **Reservoir waterproofing** (height ranges, floor to the slots): seam gap 0%, outer wall flow ratio 1.03 and outer wall 28 mm/s up to 31.95 mm; seam gap 0% and flow 1.03 also on the band layer just below the slots (31.95–32.50 mm, which stays at 40 mm/s). A normal seam with these settings passed the water test in the foot (rev9.8.2); the scarf did not.  
- **Drip groove**: a ring channel on the underside of the floor, 1.5 mm wide and 0.72 mm deep. A matching ridge on top of the floor keeps the floor at full thickness above it.  
- **Insert**:  
  - No gussets.  
  - A straight cylinder at the largest diameter the pot's floor corner allows, with 0.3 mm clearance.  
  - Height always set so the air gap is exactly 3.0 mm, measured from the waterline (the bottom of the slots) to the underside of the insert's ceiling (rule in config.3dp).  
  - Latest: insert_rev3, 35.27 mm tall (35.76 mm once T6 moves the slots to 33.0 mm). Side notches 2 mm wide × 8 mm tall, to match the pot's top slots. Walls and top thickened after insert_rev2 was too flimsy and strung. Top diameter reduced by 1 mm.  
  - Settings: 0.4 mm layers, walls 60 mm/s, seam Aligned; filament "JAYO PETG – insert" (cap 12 mm³/s, 260 °C, fan 40%, min layer time 4 s).  
  - Status: parked; print results pending.

## Decisions and why

### Normal seam instead of scarf (rev10)

The earlier V-groove seam design (Aligned seam, no paint) is superseded. The scarf seam was set aside at rev10 because it leaked in the foot; its settings are kept below.

### Scarf seam settings (parked, may revisit)

These scarf seam settings were used from rev9 to rev9.7 and set aside at rev10, which uses a normal seam.

- **Object settings**: seam position Back; staggered inner seams on; scarf joint seam (seam_slope_type) on external walls only; conditional scarf off; scarf start height 20%; scarf around entire wall off; scarf length (min) 12 mm; scarf steps 20; scarf for inner walls off; scarf joint speed 100% (80% was queued to test); scarf joint flow ratio 1.  
- **Seam placement**: seam paint enforcer strip, about 2 mm wide, outer faces only, running the full height. To center the 12 mm frosted scarf strip between two slots, paint it 6.7 mm left of the slot midpoint (as seen from outside). The seam starts about 0.6 mm to the right of the paint center, and the scarf runs to the right from there. Measured centered to within about ±0.5 mm.  
- **Slot band**: scarf switched off in the slot band (height range 32.50–40.75 mm, seam_slope_type none). A wedge-shaped modifier (67.5°–112.5° around the seam, radius 34–46 mm, height 32.45–40.70 mm) carries the band settings plus the scarf settings on the seam segment only.  
- **Look**: a 12 mm frosted strip instead of a seam line; it can feel rough at its left edge (the seam start). On rev9.7 it matched rev9.3.1, which was judged OK but could be better.  
- **Why it was set aside (waterproofing)**: on the single-bead wall, the scarf leaked in the foot flare (0 to about 14 mm): rev9.7 leaked, and two walls in the foot with the scarf kept on the outer wall (rev9.8.1) still leaked. A normal seam in the foot with seam gap 0% and outer wall flow 1.03 (rev9.8.2) passed the water test. Mixing a normal seam in the foot with a scarf above looked poor.  
- **If revisiting**: the scarf's thin starting wedge (20% start height) on the fan-cooled, slow (overhang) foot is the suspected leak path. Ideas not yet tested: a higher start height (e.g. 50%) and scarf flow ratio 1.1 in the foot, a slower scarf (80%), and pressure advance calibration.

### Legacy design (reference)

- **Legacy pot** (notNurseryPots.3mf, "3.5 inch"): 105.0 mm tall, top Ø 96.16 mm, base Ø 58.11 mm, wall about 1.04 mm, wall angle about 5.03°, floor top at 1.68 mm. Foot: its own curve up to about 13 mm. Slots: 8 × about 1.25 mm wide (from the rounded slot ends) × 36.25 mm tall, 29.38–65.63 mm. Reservoir about 113.7 mL empty. Plastic 36.0 cm³ (45.7 g).  
- rev10 vs legacy: same height, top diameter and wall angle; slots start 3.13 mm higher and are 28 mm shorter; floor 0.24 mm thinner; reservoir +18.9 mL (+17%); plastic −5%.  
- **Legacy insert** (3.3mf, "3.5 inch reservoir insert"): Ø 56.4 mm, 30.5 mm tall, about a 2.0 mm ceiling. In the legacy pot the reservoir holds about 105 mL of water with the insert in place, and the air gap is about 0.8 mm.

## Open questions

1. rev10 water test (pending).  
2. D1 (modlog): save the tuned filament settings as a named user preset in Orca once the final filament specs are settled.  
3. D2 (modlog): pressure advance calibration for JAYO PETG (0.6 mm nozzle, 260 °C). Parked.  
4. Filament 1 is an edited copy of "Bambu PETG Translucent @BBL X1C 0.8 nozzle," but the printer learnings say a 0.8 nozzle filament profile is the wrong starting point for my 0.6 nozzle. Decide whether to rebase on a 0.6 nozzle profile (ties in with D1).  
5. The 4.5in, 6in and 6.5in pots all copy rev10's waterproofing settings; rev10's water test result applies to all of them.

## Agreed changes for rev10.1

1. **T5: Wall 1.00 mm** (was 1.05 mm), still a single bead; the slot band's two 0.45 mm beads still fit. Why: about 5% less wall plastic, maybe 2–3 min per print (was deferred item D3). Needs a water test, because the reservoir waterproofing was proven at 1.05 mm.  
2. **T6: Slot bottom (waterline) 32.508 → 33.0 mm**, slots stay 1.5 × 8 mm; the slot band and reservoir height ranges shift up 0.49 mm with them (reservoir ranges to 32.44 mm, band 32.44–41.54 mm). Why: reservoir 132.6 → 135.3 mL (with the 1.00 mm wall). The insert grows 0.49 mm to keep the 3.0 mm air gap (insert_rev3: 35.27 → 35.76 mm).

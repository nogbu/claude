---
about: Slicing learnings: height ranges, speed, fan, layer time, temperature and pressure advance
read-when: before changing speed, cooling, temperature or height-range settings
readonly: no
---
# learnings/speed-and-cooling

Slicing learnings moved unchanged from process-settings' Learnings (2026-10-07).

### Height range modifiers for one band of a print (learned 2026-09-26)
- Right-click the object → Add height range modifier → set the Z range (with a little margin) → Add settings. This lets one band use different settings, e.g. 2 walls at 0.45 mm only around the wicking slots while the rest of the pot stays a single clear bead.
- Why it helps slots: a single bead has to stop and restart at each slot edge, and bead ends print rounded and short, making slots wider and ragged. With 2 beads, the outer bead U-turns around each slot end in one continuous loop, giving straighter, more accurate edges.
- Trade-off in clear filament: 2 beads add an interface inside the wall, so the band looks hazier than the single-bead areas.
- A two-bead band cut by 8 slots prints each layer as 8 separate loops, one per wall section. One starts at the seam paint and the other 7 at slot edges, and in clear PETG the starts show as a frosted streak and rough slot edges (2.5in rev2.12 photos, 2026-10-02).

### Overhang fan: stronger, then stepped down (learned 2026-09-27)
- The overhang fan only runs on lines that overhang more than the threshold (10%), so on the pot it covers just the foot. 60% printed the foot better than 20%.
- Where the overhang drops below the threshold, the fan cuts from 60% to 0% in one layer. The plastic above and below that layer cools differently, which left a physical warp ring all the way round.
- Fix: custom G-code on the layer slider, stepping the fan down over about 2 mm, starting at the layer where the fan switches off: M106 S115 (45%) → S77 (30%) → S38 (15%) → S0. On the 45° pot these are at 9.72, 10.44, 11.16 and 11.88 mm. This removed the ring.

### Overhang speed buckets that are faster than the wall speed do nothing (learned 2026-09-27)
- The 25–50% overhang bucket was set to 50 mm/s, which is faster than the 30 mm/s wall speed, so a 45° foot (about 34% overhang per layer) wasn't slowed down at all. The end of each loop sagged and left a dent just before the seam.
- Fix: set the 25–50% bucket to 15 mm/s. It only affects overhanging lines, and the dent went away.

### Slot band speed and bubbles (learned 2026-09-27)
- Bubbles came back in the two-bead slot band when its speed was 30 mm/s. The earlier bubble-free print used 40 mm/s, and returning the band modifier to 40 mm/s fixed them again. Outer/Inner wall order plus wipe before the external loop are still needed.
- 2026-10-02 (2.5in rev2.x): the band printed at 40 mm/s solo and on 2-pot plates, but bubbles were worse solo, with about 9 s between band layers, than on a 2-pot plate with about 19 s (rev2.11), and worst when slowed to 24 mm/s (rev2.5); rev2.12, whose jumps met the seams head-on, was better again. Suspects, not isolated: cooling time per band layer (part fan off), speed and temperature (265 °C frosts the band more).
- 2026-10-02: the rev2.1 3×3 plate, about 80 s between band layers (inference) at rev2.6's settings, had fewer bubbles than solo rev2.6 but not a clear band, so cooling time helps but isn't the whole cause. A free-air extrusion at 260 °C gave a smooth, clear, quiet strand, so damp filament is unlikely.

### Changing temperature for part of a print (learned 2026-10-02, 2.5in rev2.13)
- Put the M104 in the printer's Layer change G-code with a layer condition: `{if layer_num == 63}⏎M104 S250{elsif layer_num == 85}⏎M104 S260{endif}`. layer_num counts from 0, so layer_num 63 is layer 64 on the slider. The command-line slicer keeps it (it drops layer-slider custom G-code), so the change can be checked in the sliced G-code.
- Append the condition to the last line and put each newline inside its branch; starting it with a newline adds a blank line to every other layer.
- M104 doesn't wait, so the first layer after it prints while the nozzle changes temperature. M109 would hold the nozzle on the part while it waits and could leave a blob (inference).
- In Orca it's under Printer settings → Machine G-code → Layer change G-code, not on the layer slider.

### Every height range needs a layer height (learned 2026-09-27)
- In an Orca 3MF, each height range (layer_config_ranges.xml) must include `layer_height` and `extruder`, even if they're the same as the rest of the print. Orca adds both automatically when you create a range in the app, and write3mf.py adds any a range lacks (2026-10-07).
- A range without `layer_height` crashes Orca when the file is opened.

### Orca's minimum layer time slows the print; it never waits (learned 2026-10-01, rev2.5)
- Raising the minimum layer time to 16 s on a small pot cut its outer wall from about 24 to 12 mm/s (G-code). A layer-time test therefore also changes wall speed. There's no setting that adds a pause instead; a park-and-wait G-code would add a travel away and back.

### A plate removes the minimum-layer-time slowdown (learned 2026-10-01)
- A small solo object is slowed by the 8 s minimum layer time: the solo 2.5in pot printed its outer wall at about 24 and 28 mm/s instead of the set 28 and 34 mm/s. On a plate the objects share each layer, so the walls run at the full set speed (G-code).
- A speed A/B at both speeds (rev2.3) showed the same seam patch, but at 0.6 mm hop, which makes a patch by itself (rev2.10), so it says nothing more about speed.

### 265 °C makes clear PETG walls clearer but the two-bead band hazier (learned 2026-10-02, rev2.7)
- JAYO PETG at 265 °C (JAYO lists 220–250 °C; the pots run 260 °C) printed noticeably clearer single-bead walls but a more frosted two-bead slot band.

### Pressure advance test in clear filament (learned 2026-10-02)
- Orca's PA Pattern labels can't be read in clear filament, in person or in photos. Coloring the label strip with a marker makes them readable. The top chevron is the start value; labels mark every other chevron.
- The value in a file (M900) overrides the K stored on the printer. Sources disagree on whether the P1S send dialog shows a flow dynamics calibration box; the P1S doesn't calibrate automatically.

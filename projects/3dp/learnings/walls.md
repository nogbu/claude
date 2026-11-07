---
about: Slicing learnings: walls, Arachne, holes, slots, first layer, bed
read-when: before sizing or setting walls, holes or first layer; scaling pots
readonly: no
---
# learnings/walls

Slicing learnings moved unchanged from process-settings' Learnings (2026-10-07).

### Arachne bead count flips when beads exactly fill the wall (learned 2026-09-26, self-watering pot)
- Arachne picks how many beads to print from the local wall thickness vs. the wall line widths. It only adds a bead if the leftover space is almost a full bead width.
- If N beads × line width is about equal to the wall thickness, tiny thickness changes (e.g. ±0.02 mm from mesh facets) make it flip between N and N−1 beads, layer by layer and around the part. In the Line Width preview this shows as patchy colors and a staircase edge.
- Fix: for N beads, set the wall line width about 10% below wall thickness ÷ N. Example: a 1.00 mm wall (0.985–1.024 mm) flip-flopped between 1 and 2 beads at 0.55 and at 0.50 mm, and printed a solid 2 beads at 0.45 mm (Arachne stretches the beads to fill).
- For a single bead, set the line width at or a bit above the wall thickness (e.g. 1.05 mm for a 1.00 mm wall).
- On the 0.6 mm nozzle, a single bead is safe up to about 1.2 mm (2× nozzle); 1.05 mm is proven. The thinnest two-bead wall is about 1.0 mm (2 × 0.45 mm).
- 2026-10-01: on pots built by nurseryPots_lib, whose walls are exactly 1.00 mm, 0.54 mm beads set by the slot-band height range sliced as two 0.536–0.542 mm beads on every slot-band layer of 3.5in rev10.2 and 2.5in rev1, with no flip-flop (Orca 2.4.2, checked in the G-code). The flip-flop above came from a faceted wall (0.985–1.024 mm); an exact wall seems to avoid it (inference).
- 2026-10-01: a 1.00 mm wall with a 1.05 mm line width sliced as one 0.93–0.96 mm bead (median 0.94) at 0.3 mm layers (rfidSpring_rev1, Orca 2.4.2, checked in the G-code). Size thin flexing parts for a bead about 6% thinner than the wall (inference).

### First layer ignores the object's wall line width (learned 2026-10-01, rfid spring)
- The first layer uses First layer line width (0.62 mm), not the object's wall line width. rev2's 1.1 mm folds sliced as two 0.55 mm beads on layer 1 and one 1.04 mm bead above (Orca 2.4.2, G-code).
- rev2's 1.4 mm strips between notches stood alone on the bed and joined the part only higher up; they stuck and snapped off when the part was removed.
- First layer line width is plate-wide only (2026-10-10, plantTags, Orca 2.4.2 command-line slices of a 20 × 20 × 1.02 mm box, G-code): set as an object setting it was ignored (layer 1 stayed 0.62); set in the project settings it applied (0.30, 0.31 and 0.35 all sliced at that width).
- Smallest line width with the 0.6 mm nozzle (2026-10-10, same test): Orca refuses 0.30 mm for outer and inner wall, internal solid infill and top surface ("Too small line width", return -51) and accepts 0.31; first layer line width takes 0.30.

### Slot/hole compensation notes (learned 2026-09-26)
- Narrow vertical slots that cut all the way through a thin wall aren't "holes" to the slicer (they split the wall into separate pieces), so X-Y hole compensation does nothing to them.
- X-Y contour compensation would change them, but it also grows the whole part and thickens the walls. Compensate slot width in CAD instead, based on a measured test print.

### Bed temperature softens the base of PETG prints (learned 2026-09-27, self-watering pot)
- Foot failures on the pot (seam curling, loops dragged out at the seam in the first 5–15 mm) were caused by the Textured PEI plate at 80 °C. PETG softens at about 78–80 °C, so the bottom of the print never firmed up enough to hold an overhang.
- Fix: Textured PEI plate at 70 °C for the first layer and all other layers. The next print came out clean.
- Changes to Z-hop, wipe, minimum layer time and overhang fan did not fix it while the bed was at 80 °C, so check the bed temperature first when the base of a PETG print fails.

### Long parts printed diagonally (2026-09-26, unicoly rail)
- Turn the skirt off: my 2 loops at 10 mm distance run off the 256 mm bed.
- A part about 17 mm wide fits diagonally up to about 337 mm long with about 3 mm edge margin (inference); straight along the bed up to about 248 mm.

### Test pieces and horizontal holes (learned 2026-09-29, wire shelf)
- X-Y hole compensation only acts on holes that are closed within each layer (vertical holes). It does nothing to a horizontal bore, so size horizontal bores in CAD from a test piece printed with horizontal bores.
- Elephant foot compensation (0.15 mm, first layer) shrinks the first layer's outline.

### Estimating print time for a new pot size (learned 2026-09-30)
- At the tuned 12 mm³/s filament cap, nearly every feature of the pot prints at the cap, so print time scales roughly with plastic volume. rev9.7: 34.2 cm³ in about 1.1 h actual (1 h 4 min in Orca).
- Scale rev9.7's actual time by the plastic ratio, then shave 10–15% for large pots, which spend a smaller share of the time on travel, slowed layers and layer changes. Treat the result as an estimate until Orca slices it.

### Internal bridges dominate big flat parts (learned 2026-10-03, photo board)
- The first solid layer over sparse infill prints as an internal bridge, at 150% of the 30 mm/s bridge speed (45 mm/s) with thick lines. On the 252 x 224 board it took about 32 of 182 min (estimated from the G-code); 75 mm/s would save 12.5 min (Orca estimate). It was kept at 45 because on the board it is the base under the marker inlay.

### Blind-bore end walls (learned 2026-10-08, shelf bore test rev2)
- With 2 wall loops, the wall between a blind bore's end and the outside gets loops from both sides: 4 beads. At 1.86 mm (3 beads) Orca thinned the bore-side inner loops to 0.37–0.46 mm; at 2.48 mm (4 × 0.62) every wall bead printed at 0.62 or wider.

### No bed-side chamfers on openings (learned 2026-10-10, nursery-pots 6in insert)
- 0.4 mm 45° chamfers on the bed-side edges of the ceiling's holes and slots made the opposite top surface print rough (crossed lines with gaps, strings at holes). rev2.7_NoChamfer, the same file with only those chamfers removed, printed perfectly.
- Leave opening edges square on a bed-down face (open_chamfer=0 in nurseryPots_lib), and set it explicitly in each insert script.

---
about: Shelf rail system for the UNICOLY cabinet
readonly: no
---
# rail

Short name: rail. Shelf rail system for the UNICOLY glass display cabinet. Cabinet reference data (slot heights, strip, factory shelf) is in unicoly.

## Latest rev

None built. Layout A, rail on anchors, agreed 2026-10-09 (fresh start); concept only, fillets not modeled.  
* Concept script: build/concepts/rail_concepts.py, with its picture scripts (run all with build/concepts/run.sh). Pictures (2026-10-09): images/rail_compare_corner_plainLedge.png, rail_compare_closeups_plainLedge.png, rail_conceptA_clipGrip.png, rail_conceptA_clipInstall.png.  
* Test prints (not product revs): build/hookGauge_rev1.py, build/slotGuide_rev1.py (log: Test print results).  
* Slot-fit test piece, not built: build/slotFit_rev1.py (hook groove, agreed 2026-10-09) with rail_settings_base.json (the PETG High Flow profile it copies). Pictures: images/rail_slotFit_hookGroove.png (concepts/rail_slotfit_hook.py) and, for why the dovetail failed, images/rail_slotFit_lip.png (rail_slotfit_lip.py). The dovetail concept is build/concepts/rail_slottest.py (log: Dovetail groove).

## Requirements

* Shelf positions every 2" from 6" to 52" (24 ledge tops, 152.4 to 1320.8 mm above the floor).  
* Target load 40 lb per shelf, safety factor 3, 75% of the load on the front two rails: 200 N design load per front corner (inference).  
* **No external hardware.** No magnets or other bought components as part of rail/clip designs; everything is printed.

## Layout A: floor-standing rail on slot anchors

* Each corner is a column of 6 pieces standing on the cabinet floor, so shelf weight goes to the floor. Anchors hook into the slots and slide in a groove up the rail's back; they only hold the rail against the strip, so slot heights (±7), pitch (±0.3) and shims don't matter.  
* Pieces (from → to, mm): bottom 0 → 221; four identical 203.2 pieces with joints at 424.2, 627.4, 830.6 and 1033.8; top 1033.8 → 1338.6 (304.8, prints diagonally, skirt off). Each joint sits 33 below a ledge top. The lower and middle slot groups fall inside pieces 2 and 4 and the upper group inside the top piece, clear of the ±7 slot readings (inference).  
* Anchors: one per slot, 9 per post, all identical: a neck through the slot, a drop behind the steel 1.6 from the strip face (hook gauge) and a head 20 long whose hook catches behind a lip in the groove. Sizes: slot-fit test piece below (the concept's head was a hexagon, 8.0 wide).  
* Install: anchors in all 9 slots; bottom piece on the floor; slide pieces 2, 4 and the top piece down over their anchors from above; set pieces 3 and 5 straight onto the tenon below. Remove top-down by lifting. The top piece needs about 98 mm above it to start over the upper anchors (1488 interior, inference).  
* Rail section: 16 deep, centered on the slot (0.75 toward the fold from the strip center, unicoly, low confidence), so one part fits every corner; width and groove as in the test piece (the concept had 17 and a hexagon groove). Button relief on both back edges, 3.0 × 2.5 (placeholder until the buttons are measured).  
* Joints: tenon 8 wide × 5 deep × 10 tall in front of the groove, chamfered top; socket 0.2 clearance per side.  
* Notch at each position: front opening 4 deep, from the ledge top to 12 below; pocket behind it 3 deep, reaching 15 below the ledge top; 0.2 clearance. The rail section behind a pocket carries 34 MPa at the design load with the load at the ledge tip, against 64 along the layers (inference, section_stress()).  
* Printing: every part lies on its side, so notches, pockets, groove and tenon are in the layer outline (no supports) and loads run along the layers.

### Clip (plain ledge)

* Back plate 6 thick × 30 tall on the rail face; ledge 15 deep × 17 wide × 6 thick, top = shelf height; no brace, leaving 9 of ledge underside to pinch from the open side (the glass is flush on the other). Tongue 4 deep × 9 tall into the opening; hook 3 deep drops 3 into the pocket.  
* Install: hold it 3 high, push straight in, let it drop 3. Remove: pinch the ledge, lift 3, pull straight out. Every move is parallel to the glass.  
* Stress at the design load on the ledge tip: plate 22 MPa, ledge root 18, against 64 along the layers (inference, clip_stress()).

### Slot-fit test piece (hook groove agreed 2026-10-09, not built)

* Purpose (design principle 7): which hook height passes the real slots, and the groove fit. Build: slotFit_rev1, one plate, PETG High Flow, my process settings.  
* Hook groove: a square hook on the anchor's head catches behind a lip on the bar's fold side, and the hook face's in-layer gap steps 0.5 / 0.3 / 0.2 in three zones. Sizes, fit, printing and checks: values.md (rail-slotfit).  
* Use: hook each anchor into a lower slot; the most notches that still pass and drop behind the steel gives the slot height. Slide an anchor through the groove from the beveled end; the first zone that's snug without binding is the groove fit. Then slide the bar down over a hooked anchor, beveled end first.  
* Layout A takes these values at the chosen gap if it passes.  

### Shelf cutouts

* Corner cutouts must clear the 16 deep rail: about 19 × 18 (inference); size them once the strip face distance is measured.  
* The rail covers the slotted strip, so stock clips can't be used at a corner that has a rail (inference).

## Decisions and why

* **Layout A over C** (one-piece height clips hooked into two slots, no rail), agreed 2026-10-09: the load goes to the floor and only the anchor has to fit a slot; C hangs each corner on a 1.6 mm hook neck and needs new clips to move a shelf (log: Height clips).  
* Left out: rails hung from the slot groups (hooks carry every shelf, heights ride on the ±7 slot readings) and the stacked layout with built-in hooks (log: Stacked layout with built-in hooks), whose pitch, drop-vs-lift and shim problems A removes.  
* **Plain-ledge clip**, agreed 2026-10-09: with the glass flush on one side, the braced clip left nothing to grip (log: Braced clip).  
* **Splice (lap) joints and openGrid rail rejected** (log: Rejected rail alternatives).  
* **Hook groove over the dovetail**, agreed 2026-10-09: the dovetail's upper lip started in midair on the side-printed bar; the hook has one fit face, in the layer on both parts, and every layer rests on the one below (log: Dovetail groove). Left out: printing the bar groove-up (loses the exact per-layer gaps and puts the rail's notches on the bed) and drop-on pockets (change how the rail goes on).

## Open questions / next steps

1. Next: build and print the slot-fit test piece (on "build"), then size the anchor, groove, clip and joints from its result and grid-lock them (design principle 12). The clip-to-notch fit and the tenon joint still need their own test before the full set (design principle 7).  
2. Glass buttons: standoff from the strip face and reach across it aren't measured (unicoly); they size the back relief.  
3. Slot height: reads 3.3 to 4 (unicoly); the test piece settles it.  
4. Strip width 16.6–17.6 (17 drawn); where the glass sits relative to the strip edge isn't measured (drawn at the edge, 0.75 from the rail).  
5. Cabinet floor at the posts: assumed flat where the bottom piece stands (inference).  
6. Front-to-rear distance between strip faces (shelf cutouts).  
7. Filament and time per corner: not sliced yet.

## dp exceptions

* Slot-fit test piece: fit faces sharp: the anchor's hook face, its top edge and the throat bottom; its neck, throat and neck-top corners, which seat on the slot edge; the bar's lip (face, top and pocket floor corner). The roof's edge on the bar's back face stays sharp: it sits on the strip. Drop's bottom-front corner r0.7 (bearing face). Anchor top fillet 0.6 and bed chamfer 0.3: bigger ones thin the 1.6 neck band below a bead. Lead-ins, ramps, marks and notches stay sharp to work and read. The groove and throat steps (dp 3) are the fit itself.

## dp trials

* 2026-10-09, design principle 5 (hook groove): the hook face's gap runs in the layer on both parts, so the zones step it exactly; only the one-layer side play (lip top, pocket floor) runs in Z.

## Agreed changes

None pending.

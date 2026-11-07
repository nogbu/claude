---
about: Slicing learnings: seams, z-hop, retraction and wipe on single-bead walls
read-when: before choosing seam, z-hop, retraction or wipe settings
readonly: no
---
# learnings/seams

Slicing learnings moved unchanged from process-settings' Learnings (2026-10-07).

### Short hops across slots don't retract by default (learned 2026-09-26)
- The printer profile's Retraction → Travel distance threshold is 3 mm. Travel moves shorter than that skip retraction, so crossing a slot or gap narrower than 3 mm leaves PETG strings across it.
- Fix: set the threshold below the smallest gap the nozzle hops over, e.g. 0.5 mm. Put it in the filament's Setting Overrides → Retraction so it applies per filament without changing the printer profile.

### Seam position Aligned on single-bead walls (learned 2026-09-27)
- With seam position Aligned, Orca puts the seam on the sharpest inside corner of each layer, so a V groove holds it. On a smooth wall it wanders, and seam paint made it worse. For smooth walls, use Back plus paint (below).

### Measuring seam position from photos (learned 2026-09-28)
- Accurate to about ±0.4 mm without any manual alignment.
- Setup: print the marker target sheet (ArUco markers around a circle matching the pot foot) at 100% and tape it flat. Stand the pot in the circle, seam toward the camera, and stuff black cloth inside so the frosted seam strip shows up against a dark background.
- Take 3–4 photos from about 40–50 cm away, looking down at about 30–40°, so the front row and side markers are in frame.
- Claude then calibrates the camera from the markers, locates the pot from its slots, unrolls each photo onto the pot surface and detects the strip edges at every height.
- What limits accuracy is the sheet (how flat it is, how many markers are visible), not image resolution.

### Seam position Back plus painted strip on a smooth wall (learned 2026-09-28)
- On the smooth 45° pot, seam position Back plus a painted seam enforcer strip (about 2 mm wide, outer faces only) holds the seam in one vertical line from foot to rim, with no lean.
- The seam starts about 0.6 mm to the right of the paint strip's center (as seen from outside), and the 12 mm scarf runs to the right from there.
- For a normal (non-scarf) seam, paint 0.6 mm left of the target line. The 6.7 mm offset was for centering the 12 mm scarf strip.
- To center the frosted scarf strip between two slots, paint the strip 6.7 mm left of the slot midpoint. Measured result: centered to within about ±0.5 mm (rev9.4 onward).
- On a copy turned so its paint faces left or right on the bed, Back pulls the seam toward the back of the printer, up to about 0.8 mm past the paint strip's edge (2.5in rev2.12: 0.4–1.1 mm and 0.7–2.5 mm off center between the slots, 2026-10-02). Adjust the paint or the seam setting before turning copies in a production file (inference).

### Seam paint on a tapered wall (learned 2026-09-30)
- A painted seam strip sits at a fixed angle, so an offset measured in mm at one height grows with radius. On the 3.5in pot, 0.97° is 0.59 mm at the foot and 0.76 mm near the rim.
- Set paint offsets at the height that matters most, or check them at both the foot and the rim.

### Jumps between objects mark the seam on by-layer plates (learned 2026-10-01; cause isolated 2026-10-02, 2.5in pots)
- Orca prints the objects on a by-layer plate in the same order on every layer, and each jump between objects leaves one seam and lands on the next (rev2.11: copy 2, then copy 1; 3×3 rev2.1: 9, 6, 3, 2, 5, 8, 7, 4, 1).
- With every seam facing the back, the jump between side-by-side pots runs along the wall top for about 6–7 mm next to each seam, on the side facing the other pot, 0.2–0.56 mm above it, and leaves a grainy, frosted patch there (rev2.11). Turning the copies so the seams face each other, so each jump meets the seam head-on, made the seams as clean as a solo pot's (rev2.12, the only change). Jumps that cut across a pot just printed, 0.2 mm above its fresh wall, fit the 3×3's far-side zit lines (inference).
- A layout works only if each object's previous and next objects in the order sit on the same side of it, so its seam can face both. Two objects: seams facing each other. A 2×2: seams facing the plate center (inference). A 3×3 can't: every closed order through neighboring pots passes straight through at least one pot.
- Hop and retraction: 0.6 mm z-hop with 0.8 mm retraction made the 3×3's rough seams smoother (rev2.2), but a 0.6 mm Spiral Lift makes its own patch on a solo pot (rev2.10). Plate tests run at 0.6 mm hop (speed, extra length on restart, +5 °C, pressure advance) only show those changes don't remove that patch.

### Spiral Lift size grows with z-hop height (learned 2026-10-02, 2.5in pots)
- Orca's Spiral Lift is one full circle that starts at the end of the wipe and rises to the hop height; its radius grows with the hop: 0.61 mm at 0.2 mm and 1.83 mm at 0.6 mm (travel slope 3°, read from the G-code). After the lift the nozzle travels to the next start at hop height and drops straight down.
- On clear PETG single-bead walls a 0.6 mm hop leaves a grainy, frosted patch just after each loop's start; 0.2 mm doesn't. A G-code reading that predicted the bigger circle would miss that area was wrong, so test hop changes in print rather than judging them from the G-code.
- The circle's center lies back along the wipe, toward the seam, so a 0.2 mm lift stays within about 1 mm of the seam; a 0.6 mm lift reaches about 2.7 mm past it (G-code, 2026-10-02).

### Extra length on restart blobs slot edges (learned 2026-10-01, rev2.4)
- 0.1 mm extra length on restart after a 0.8 mm retraction left blobs at the slot edges and made the slot-band bubbles worse, because it applies at every restart. It did not fix the seam patch (tested at 0.6 mm hop).

### The seam start sits under the wipe (learned 2026-10-02, 2.5in pots)
- In the pot G-code each outer loop ends with a 1 mm wipe back over that loop's start, and the whole retraction happens during the wipe (retract amount before wipe 0%). The next layer then drops back and pushes the retraction back out at the same spot before starting. Retraction and z-hop changes therefore act exactly on the area just after the seam.

### Judge seam defects in clear PETG in person, not from photos (learned 2026-10-02)
- Claude misread the rev2.7 photo as clean when the patch was unchanged. For frosting and seam patches on clear prints, record the in-person verdict, and use photos only to locate the defect.

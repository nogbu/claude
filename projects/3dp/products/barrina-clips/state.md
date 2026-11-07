---
about: Clip holding a Barrina T5 bar under the wire shelf, twist-locking between two crosswires
read-when: before designing any Barrina mount
readonly: no
---
# **barrina-clips**

Short name: barrina-clips. New product, started 2026-10-04. A clip that holds a Barrina T5 grow-light bar under a wire shelf (shelf): one side snaps onto the bar, the other twist-locks between two crosswires. Styled for sale as well as for my cabinet.

## **Product rules**
- Any Barrina mount starts from this doc's snap U (the side that grips the bar), unchanged.

## **Latest rev**

rev2 (barrinaClip_rev2.3mf), a two-clip test pair on one plate, built 2026-10-04, not yet printed. It's rev1 with both wire-notch roofs ramped so no part prints over air on one side. File: /mnt/project-files/3mfs/barrinaClip_rev2.3mf. Build script: projects/3dp/products/barrina-clips/build/barrinaClip_rev2.py (run `python3 barrinaClip_rev2.py OUTDIR`), reading projects/3dp/products/barrina-clips/build/barrinaClip_settings_base.json (the settings copied unchanged from my existing U-clip file). The script needs numpy, shapely, trimesh, mapbox_earcut and manifold3d (install with pip). Design picture: /mnt/project-files/images/barrinaClip_rev2_design.png; notch ramp picture: barrinaClip_rev2_notchRamp.png.

rev2 test (2026-10-05, the user's photo): the front (bending) wall cracked by fatigue at the hinge slot's square top corner after several swings. Bending strain at the slot end for the 2 mm bump push is about 7.0% (1.86 mm wall, 8.9 mm from the slot end to the bump; inference, simple beam estimate). Fixes to weigh for rev3: a fully rounded slot end; a longer, thinner bending wall; the slot can't run straight up, since the clip's top sits 1.5 mm under the wires, so turn it sideways under the top as far as the neck (about 2.7 mm, about 2.0% strain; inference); 1 mm bumps (about 3.4%, weaker hold); or PETG.

Slice check (OrcaSlicer 2.4.2 command line, both clips): 108 layers, 32.40 mm tall, 21.00 g, about 33 min 17 s, no supports, no warnings. The only spot over air is the neck underside at 9.3 mm, a 3.2 mm bridge held at both ends (kept by choice).

## **Requirements**

* Fits both the 1 ft and 2 ft Barrina T5 bars (I confirmed my existing U-clip fits both, 2026-10-04).
* Hangs the bar under the wire shelf, between two crosswires, as close to the shelf's underside as possible.
* Light encourages leaves to face front: plants turn their leaves to face the light ([Indiana University, Plants in Motion](https://plantsinmotion.bio.indiana.edu/movies-categories/tropisms/coleus-solar-tracking.html)).
* A tab to pull the clip off the bar when the bar needs removing.
* Prints in the same orientation as my existing U-clip file (profile flat on the bed, layers stacking along the bar).
* Design load per clip: (bar weight + 10 N knock) × 3 = (1.24 N + 10 N) × 3 ≈ 34 N. The 10 N knock is an estimate (inference).

## **Key data**

| Item | Value | Source |
| :---- | :---- | :---- |
| 1 ft bar | About 298 × 20 × 20 mm; a plugged cord bent 90° adds 33 mm past one end | Measured (2026-10-04) |
| 2 ft bar (NF10) | About 610 mm long; 120° beam; no published cross-section | Listed ([Barrina](https://barrina-led.com/products/t5-led-black-grow-light-2ft-10w-5000k-linkable-and-magnetic-4-packs-nf105)) |
| 2 ft bar weight | 126 g | Measured (2026-10-04) |
| Existing U-clip | 24.72 wide × 27.4 tall × 20 long; 21 mm opening; snap bumps 2 mm per side, peak 4 mm below the back (17 mm across); 1 × 5 mm hinge slot at each top corner; walls 1.86 mm (3 beads). Bambu PLA Matte, Bone White | Read from my clip file (uploads/hearth/b02dba62-b283-4049-a12d-90df57ef04b6) |
| Bar groove | About 4 mm below the bar's back, inferred from the clip's bumps | Inference |
| Crosswires | 2.9 ± 0.2 mm, 25.3 ± 0.3 mm apart, irregular by up to ±0.7 mm; run front to back | Measured (shelf) |
| Support rods under the crosswires | About 188 and 240 mm back from the front edge rod | Measured (shelf) |
| Matte PLA tensile strength | 23.5 MPa along layers, 12.9 MPa across | Listed ([Matte PLA data sheet](https://polyalkemi.no/wp-content/uploads/2024/04/Matte-PLA_TDS_Template_V5.0-1-1.pdf), from a Bambu reseller; not confirmed as Bambu's own) |

## **Decisions and why (2026-10-04)**

1. Bar tilted 30° back from straight down, lit face aimed toward the plants. Why: light comes from the front, pulling leaves to face front; beam center lands near mid-depth of the shelf below; forward spill toward the door limited to 30° (inference, assumes about 300 mm from lit face to the shelf below).
2. Twist-lock grip: a narrow head pushes up between two wires turned lengthwise, twists 90°, and drops so two rigid lips rest on the wires, with notches seating each wire. Why: in this print orientation it needs no supports and nothing flexes at the shelf. Snap hooks were drawn and rejected: their arms print as thin plates over open air at both ends.
3. Clip length 32.4 mm along the bar (108 layers), so the lips print from the bed up with no overhang.
4. Pull tab on the front wall only, a rounded finger pad at its free end. Why: reachable through the door; pulling it frees the front bump and the bar swings down off the back hook (inference).
5. Back wall is a fixed hook (no hinge slot). Install: hook the bar's back groove on, swing the front up until the front wall snaps. Why: the back slot was the clip's highest point once tilted; removing it brings the bar top from 9.1 to about 4 mm below the wires (inference).
6. Consumer-styled shape: every edge rounded (about 0.85 mm), one smooth sweep over the bar, rounded tab. The walls, bumps, front hinge slot and notches are unchanged.
7. Rounded relief cut into the shoulder at each side of the neck (about 0.8 mm radius), instead of a fillet toward it. Why: about 0.35 mm more room for the neck to turn between the wires; same strength.
8. rev1 is a test pair (two clips, one plate), checking bar fit, release and wire grip before the full set.
9. Filament and settings as my clip file: Bambu PLA Matte Bone White (#CBC6B8), "P1S 0.6mm" printer and "0.60mm default" process profiles, 0.3 mm layers, 0.62 mm lines, 2 wall loops, 15% infill, 3 top and 3 bottom layers.

## **rev2 design (as built, on the grid)**

Grid: 0.3 mm layers along the bar (print Z), 0.62 mm beads across. Profile coordinates: X front (−) to back (+), Y up, 0 at the wire undersides.

* Clip length 32.4 mm (108 layers).
* Neck 13.64 mm wide (22 beads) × 13.8 mm along the bar (46 layers, z 9.3–23.1).
* Lips 18.6 mm wide (30 beads), 3.1 mm thick (5 beads), top 1.86 mm above the wire tops.
* Wire notches 5.1 mm (17 layers) × 1.24 mm deep (2 beads), at z 1.2–6.3 and 26.1–31.2.
* Notch roofs ramped (rev2): over the 4 layers above each notch (z 6.3–7.5 and 31.2–32.4) the lower lip grows 0.31 mm per layer, about 46°, so no roof prints over air. The notch stays 5.1 mm wide where the wire meets the lip and opens to about 6.3 mm at the lip's lower edge (inference).
* Clip top 1.5 mm below the wire undersides when seated, for the lift out of the notches.
* Walls 1.86 mm (3 beads); 2.48 mm (4 beads) of material above the bar's top corner; hinge bridge 2.48 mm (4 beads); front hinge slot 1.0 mm.
* Pull tab 6 mm long at 45°, rounded end.
* Edge rounding 0.85 mm; neck relief cuts 0.8 mm radius.
* Bar top 3.98 mm below the wires (from the build script).
* Mesh: watertight, 12,395 mm³ per clip (rev1: 12,416), 34.75 × 43.5 × 32.4 mm.
* Lip bending about 3 MPa at the design load (inference, beam estimate).

## **Open decisions**

None. Next: print the rev2 test pair and check bar fit, release by the tab, and wire grip.

## **Future ideas (not decided)**

* Bevel the two ends of the 32.4 mm length; print in the bar housing's color; light texture on the tab.
* Clips per bar and the full count, after the rev2 test.

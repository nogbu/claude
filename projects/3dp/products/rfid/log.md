---
about: Parked and superseded rfid material, newest first
read-when: before building it, at an item's trigger, or for a value state.md lacks
readonly: no
---
# rfid log

## rev1 decisions and test (history; staged 2026-10-07; back if: rev1 is rebuilt or compared, or the filament choice is revisited)
* PETG HF chosen at first; rev1 and rev2 actually used JAYO (see Print settings).  
* RFID tab left off rev1, to be designed later.  
* rev1 test (2026-10-01): fit well in 52–58 mm holes, didn't grip in a 74 mm hole; rails popped out of their notches; a stray blob fused part of one rail to a fold.  

## rev2 slice check (Orca 2.4.2, 2026-10-01) (history; staged 2026-10-07; back if: rev2 is rebuilt or its push data is needed)

* 67 layers, 19.41 g, 6.31 m of filament, about 32 min (Orca's estimate). No warnings.  
* Folds slice as single beads 1.03–1.04 mm wide, except the first layer, where each prints as two 0.55 mm beads.  
* Narrowest gap between folds 0.50 mm. Rails clear the notches by 0.90–1.30 mm. Beads stay within 0.06 mm of the model outline.  
* Push (Estimated, inference, at the sliced bead width): about 2.6 N in 72–75 mm holes, 5.1–6.1 N in 52–58 mm holes, 6.4 N fully squeezed. Safety factor about 3.2.  
* Push (Measured 2026-10-01): 128–130 g at about 75 mm long. One end was taped at the ruler's 73 mm mark (the marks start about 2 mm in), the other pressed on a kitchen scale; readings never steadied by hand. About 0.66× the beam model with Bambu PETG Translucent's data-sheet stiffness (inference; JAYO's stiffness unchecked).  
* Weight (Measured): 18 g without the snapped strips.

## Spring force limits (Estimated, inference, 2026-10-01) (history; staged 2026-10-07; back if: folds or safety factor are resized)

Inputs: Bambu PETG HF data sheet (Listed): bending strength 64 MPa along layers, 48 MPa across; stiffness 2,050 MPa along layers. Assumed folds spanning 14–16 mm, gaps of at least 0.5–0.8 mm and 3 mm end blocks. The middle-rail layout gives folds about 17.6 mm long, so these limits are slightly low. Real prints come in somewhat under them.

| Safety factor | Most push at 50 mm | Fold thickness |
| :---- | :---- | :---- |
| 2 | 12–18 N (2.7–4.1 lb) | 0.9–1.2 mm |
| 3 | 4.6–7.5 N (1.0–1.7 lb) | 0.7–0.9 mm |
| 4 | 2.3–3.9 N (0.5–0.9 lb) | 0.55–0.8 mm, about as thin as the 0.6 mm nozzle prints |

Cycling a lot, or sitting compressed for long stretches, calls for the higher safety factors: under steady load PETG slowly takes on some of its compressed shape.  
rev1 is sized for safety factor 3 using its 17.2 mm folds and 28 folds, which allows 1.00 mm folds. Its estimated push is under rev1 slice check (staged, rfid log).  
Source: Bambu PETG HF Technical Data Sheet, [https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf](https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf)

## Spring concept (parked; staged 2026-10-07; back if: the concept needs explaining)

> * Flat zigzag of thin folds running across the spring's width, joined at alternate ends by bends. A few dozen folds share the travel (30 mm in rev1, 40 mm in rev2), so each bends about 1.0 mm in rev1 and 1.5 mm in rev2 (inference: travel ÷ gaps, 29 in rev1 and 27 in rev2, from the doc's own sizes). Each gap is narrowest at its bend and widest at its open end.  
> * Guide: two rails, one from each end block, run through a notch at the middle of every fold, where the fold barely bends. Each fold hooks under the rail heads and roofs over them with 45° faces, so every fold is held sideways, up and down, with no supports needed.  
> * Built-in stop: each rail is as long as the end blocks' inner faces are apart at 50 mm (rev1 43 mm, rev2 40.6 mm), so at 50 mm its tip meets the opposite end block.  
> * The concept picture used placeholder sizes. The real values are under rev2 design and rev1 design (staged, rfid log).

## rev1 design (history; staged 2026-10-04; back if: rev1 is rebuilt or its sizes are needed for comparison)

* 80 mm crown to crown at rest, 50 mm fully compressed; 20 mm wide; 20.1 mm tall (67 layers of 0.3 mm).  
* End blocks: outer faces are 26 mm radius arcs (fit a 52 mm hole at the middle), 1.5 mm thick at the edges and 3.5 mm at the middle; inner faces flat at 3.5 mm from each end.  
* 28 folds, 1.00 mm thick in the model (one bead). Each fold is pre-bent into the S-curve it straightens out of, so at 50 mm every gap is a uniform 0.517 mm.  
* Bends rounded inside (0.8 mm across) and outside (1.4 mm radius). Bend centers sit 1.4 mm from the edges, so each fold spans 17.2 mm.  
* Two rails, 43 mm long: one from the fixed end at 7 mm across, one from the moving end at 13 mm across. Each tip meets the far block at 50 mm (the stop) and tapers over its last 1.5 mm.  
* Rail profile (half-widths): 0.6 mm up to 1.2 mm high, 45° out to 1.5 mm at 2.1 mm, straight to 3.6 mm, 45° roof to 5.1 mm.  
* Notch profile (half-widths): 1.05 mm up to 0.9 mm high, 45° out to 1.95 mm at 1.8 mm, straight to 3.9 mm, 45° roof closed by 5.7 mm. Clearance 0.45 mm sideways, about 0.53 mm across the 45° faces.

## rev1 slice check (Orca 2.4.2, 2026-10-01) (history; staged 2026-10-04; back if: rev1 is rebuilt or its sliced push estimate is needed)

* 67 layers, 14.62 g, 4.75 m of filament, about 28 min (Orca's estimate). No warnings.  
* Folds slice as single beads 0.93–0.96 mm wide (median 0.94), not 1.00.  
* Narrowest gap between folds 0.56 mm. Rails clear the notches by 0.48–0.82 mm. Beads stay within 0.06 mm of the model outline.  
* Push (Estimated, inference): about 12% below the 1.00 mm design. About 7 N fully squeezed, 5–7 N in 52–58 mm holes, 1–2 N in 72–75 mm holes. Safety factor about 3.2.

---
about: Spool-hole spring plus a top plate holding a Bambu RFID tag
readonly: no
---
# **rfid**

Short name: rfid. Started 2026-10-01. A one-piece PETG spring wedging across a filament spool's center hole; one end will later carry an RFID tag.

## **Latest rev**

rev2: rfidSpring_rev2.3mf, built, slice-checked and printed 2026-10-01 (results: Decisions and why, rev2 test). Built by rfidSpring_rev2.py, with rfidSpring_settings_base.json beside it (same file as rev1). rev1: rfidSpring_rev1.3mf, built by rfidSpring_rev1.py. Concept picture: rfidSpring_concept.png, built by rfidSpring_concept.py. All scripts are in projects/3dp/products/rfid/build/.

## **rev2 design**

* 90 mm crown to crown at rest, 50 mm fully compressed; 25 mm wide; 20.1 mm tall.  
* End blocks: 26 mm radius outer arcs, 1.5 mm thick at the edges and 4.70 mm at the middle; inner faces flat at 4.70 mm from each end.  
* 26 folds, 1.10 mm thick in the model (one bead), pre-bent S-curves so every gap is 0.444 mm at 50 mm.  
* Bends rounded inside (0.8 mm across) and outside (1.5 mm radius); bend centers 1.5 mm from the edges, so each fold spans 22.0 mm.  
* Two rails, 40.6 mm long, from the fixed end at 8.5 mm across and the moving end at 16.5 mm across. Each tip meets the far block at 50 mm (the stop), tapering over its last 1.5 mm.  
* Rail half-widths: 0.7 mm up to 1.2 mm high, 45° out to 2.5 mm at 3.0 mm, straight to 4.5 mm, 45° roof (top layer ends at 6.9 mm). Head 5.0 mm across on a 1.4 mm neck; hook 1.0 mm per side.  
* Notch half-widths: 1.5 mm up to 0.9 mm high, 45° out to 3.3 mm at 2.7 mm, straight to 4.8 mm, 45° roof closed by 8.1 mm. Clearance 0.8 mm sideways, about 0.78 mm across the 45° faces, 1.1 mm above the rail; 1.4 mm of fold between the two notches.  
* Wall line width 1.15 mm (outer and inner); otherwise as Print settings below.

## **Print settings (rev1 and rev2)**

* As printed: JAYO PETG Translucent on Orca's "Bambu PETG Translucent @BBL X1C 0.8 nozzle" preset, plus the 0.5 mm travel threshold. The files were built with the HF settings below.  
* Printer P1S 0.6mm, process 0.60mm default, filament Bambu PETG HF @BBL X1C 0.8 nozzle (Orca 2.4.2's PETG HF profile for the P1S 0.6 nozzle): 245 °C, 230 °C first layer, 70 °C textured plate.  
* Changes from the 0.6 mm defaults:  
* Wall line width 1.05 mm (outer and inner) on this object, so each fold prints as one bead.  
* Retraction minimum travel 0.5 mm.  
* Supports off: with them on, Orca 2.4.2 won't slice, as the slot 2 support filament (210 °C) is too far from PETG HF (245 °C). Same print: nothing is painted and the 45° faces need none.

## **Spring requirements (from me)**

> * 90 mm long at rest (rev1: 80), 50 mm fully compressed (40 mm of travel).  
> * 25 mm wide (rev1: 20; I allowed up to 5 mm wider) × 20 mm tall.  
> * Compresses straight: no bowing or twisting.  
> * One piece, PETG. rev3's filament settings favor speed and reliability; clarity doesn't matter.  
> * Optimized for 3D printing.  
> * Fits spool center holes of 52–58 mm and 72–75 mm.  
> * Firm enough to stay wedged, easy to squeeze in by hand.

## **How it's used (from me, 2026-10-01)**

> * Stays in a spool a few hours to a few days; under 50 spool changes, ideally up to 500. The AMS runs at room temperature.  
> * Load: the plate banging the AMS slot's sides as the spool turns levers the spring out; not gravity. Stronger springs than rev2 have been levered or knocked out. rev2 felt loose by hand in a 74 mm hole; not run in the AMS.  
> * Squeezing rev2 into 52–58 mm holes felt fine.  
> * Earlier S-curve springs strong enough for 75 mm holes bowed down into lip hubs, being under high tension at 50 mm. rev2 didn't bow.  
> * RFID tag: Bambu's spool tag, about nickel-sized, wafer thin, in a separate top plate on one spring end.  
> * Hubs: plastic or cardboard. Some have a solid wall down the hole; the whole end face touches. Some smaller hubs have a 5 mm thick lip at the hole's mouth, flush with the hub face, with the cavity behind about 10 mm wider each side; only the lip touches.

## **Decisions and why**

> * Zigzag, not a coil spring: a printed coil needs supports, its twisting pulls on the layer bonds, and it would still need a guide.  
> * Guide through the folds' middles, not a side rail and channel: a side guide would take about 8 mm of the 20 mm width and wouldn't stop the folds bowing between the ends (estimated to start at about 4–6 N, inference). Fold middles barely bend, so the notches cost almost nothing.  
> * Plain spring at safety factor 3: it only has to stay wedged while the AMS turns the spool, not survive shipping.  
> * Bends rounded inside and outside, to spread the stress where the folds bend hardest.  
> * 20.1 mm tall (67 layers of 0.3 mm), the nearest grid height to 20 mm.  
> * One spring per plate.  
> * rev2 is 25 mm wide so the guides can be bigger with more clearance, and 90 mm at rest for more grip in wide holes while still squeezing to 50 mm. Chosen over a clip-on end piece or grippier ends.  
> * rev2 folds: 26 × 1.1 mm, for about 1.8× rev1's grip at 74 mm with similar squeeze effort, a single bead within the nozzle's proven range. 1.2 mm folds rejected (past the safe single-bead limit, harder squeeze).  
> * rev2 guides: hook 1.0 mm per side (rev1 0.45) and clearance 0.8 mm (rev1 0.45), more than a blob.  
> * rev2 test (2026-10-01): still didn't grip in 72–75 mm holes; the strips between the two rail notches (1.4 mm wide at head height, standing on the bed) stuck to the bed and snapped off; many fine strings between the folds. Grip estimates unverified: rev1 (about 1.4 N) and rev2 (about 2.6 N) both slipped at 74 mm.  
> * Even-gap S folds can't squeeze from 90 to 50 mm: the turns barely bend, so only each gap's open side closes (inference). The gaps must start V-shaped to fold flat.  
> * rev3 layout (2026-10-01, from my sketches): a top plate on the hub face, fixed to the spring's right end, runs left past the spring onto the hub and carries the RFID tag. The right (fixed) end is L-shaped, with a built-in ledge on the hub face. The free left end hangs in a track under the plate, keeping it level and lined up with the fixed end (option B; picked over a ledge on the free end).  
> * A fixed 20 mm extension can't replace grip: the folds would have to fit into about 20 mm (inference).

## **Open questions / next steps**

> 1. Rails: remove them and their notches (the track aligns the ends; sideways bowing untested), or keep one. Asked 2026-10-01, unanswered.  
> 2. Grip in 72–75 mm holes (target about 50% more than rev2's 129 g), against levering. Options: a hook under the lip (about 2 mm deep if put in tilted, 1 mm straight), a longer or stiffer spring, or a sliding end. Safety factor: 3 chosen; about 2.5 may do for this use (inference).  
> 3. rev3 filament settings proposal, not yet approved: 245 °C (250 first layer), fan 20–60%, flow 0.95, 16 mm³/s, 0.8 mm retraction, 0.4 mm z-hop, 0.5 mm travel threshold. JAYO's specs to check.  
> 4. The plate: size, thickness above the hub (less to hit the AMS slot), how it attaches to the fixed end, and the track.  
> 5. Stringing between the folds. Suspect: the many short hops; not tested.  
> 6. S-curve folds (can't fold 90 to 50 mm; see Decisions): confirm dropped.

## **Agreed changes**

rev3: top plate, L-shaped fixed end and free end in a track under the plate (see Decisions).

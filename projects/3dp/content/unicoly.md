---
about: UNICOLY cabinet (ASIN B0DX1GKH3F) reference data and fit guidelines for parts
read-when: with photos.unicoly before citing any cabinet value
readonly: no
---
# learnings.unicoly

Reference data on the UNICOLY glass display cabinet (Amazon ASIN B0DX1GKH3F) and how to design printed parts for it, reusable by other projects. Products built for it have their own product docs (rail, shelf).

Every figure is tagged with its source: **Measured** (by me), **Listed** (product listing or seller), **Estimated** (Claude's inference from photos or math). Photo values cite the photo's name; photos are indexed in photos.unicoly.

## Cabinet identity
- **Product**: UNICOLY Glass Display Cabinet 4-Tier, with glass doors and tempered glass on three sides (the black version is ASIN B0DX1GKH3F). *Listed.*
- **Beware of look-alikes.** This is the *glass-walled* UNICOLY cabinet. The larger metal-walled UNICOLY cabinet and the lockable 4-shelf model (71" H × 32" W × 16" D) are different sizes; parts for this one won't fit them. The 8-color LED version (ASIN B0DPWXBRKD) lists the same 27.5" × 14" × 66.1" footprint. *Listed.*
- Buyers report same-size clones at Wayfair and Walmart take the same aftermarket shelves. *Listed (buyer reviews).*

## Cabinet specifications
| Item | Value | Source |
|---|---|---|
| Outer dimensions | 66.1" H × 27.5" W × 14" D (167.9 × 69.9 × 35.6 cm). HobbyPilled lists 66.4" × 27.55" × 13.77". | Listed |
| Weight | 76.7 lb | Listed |
| Frame | Cold-rolled steel (SPCC), powder coated | Listed |
| Glass | Tempered | Listed |
| Tiers / shelves | 4 tiers, 3 adjustable shelves | Listed |
| Other | Adjustable threaded feet, anti-tip wall anchor kit, magnetic doors | Listed |
| Interior height (floor to underside of top, at a post) | 1488 mm (58.6") | Measured (floor and ceiling tape measurements agree within 3 mm) |
| Interior width (glass to glass) | 693 mm ±1 | Measured |
| Temperature, doors closed | 82–85 °F with the room at about 77 °F (contents and heat sources at the time not recorded) | Measured (2026-09-28) |

## Factory shelf (the design reference)
| Item | Value | Source |
|---|---|---|
| Width (side to side) | 690 mm (about 1.5 mm clearance to the glass each side) | Measured |
| Depth (front to back) | 300 mm | Measured |
| Thickness | 20 mm | Measured |
| How it's supported | Rests on metal shelf clips hooked into the slotted strips on the posts | Observed |
| Stock shelf clip | Stamped, zinc-plated steel Z-clip, 15 mm wide plate. Shelf plate 12.4 mm long from the fold; outer plate 13.9 mm, bent about 57° down toward the strip, with an 8.1 × 1.5 mm window near its free end; the fold's 1.5 mm inside gap takes the strip's steel; the tab beyond is 8.1–8.4 wide × 9.6 long, goes through the slot and braces on the inside face above it. Caliper thickness 0.9 on the shelf plate, 0.6 on the outer plate: treat as 0.6–0.9. Angle under load and shelf height relative to the slot unknown. | Estimated (photos 151317, 151418); thickness measured (151459, 151518) |

## Slotted post strips (where shelf clips hook in)
| Item | Value | Source |
|---|---|---|
| Strip | Flat, forward/back-facing strip on each post, between the glass edge and a fold. About 17 mm wide (16.6–17.6 by ruler, photos 144310 and 144342; 17.5 assumed until caliper-measured). | Estimated (photos) |
| Slot | Horizontal rectangle, 9 mm wide × 4 mm tall. Photos read 8.7 ± 0.3 wide (144310) and 3.3–3.7 tall (010907 3.3–3.5, 144310 3.6, 144342 3.7), so it may be under 4; check with a hook pass/fail piece before any 3.4 mm hook is final. Across the strip: about 3.5 mm from the fold edge, 5 mm from the glass edge, low confidence (144342). | Size measured; photo values and position estimated |
| Clear depth behind a slot | 22 mm | Measured |
| Steel thickness | Not measured directly. Hook gauge test: a 1.6 mm gap behind the steel fits with slight wiggle, 1.3 mm won't go in, so about 1.3–1.5 mm. | Estimated (from a fit test; printed gaps can come out smaller than modeled) |
| Slot layout | 3 groups of 3 slots per post (9 per post), giving 3 shelf heights per group | Measured |
| Slot heights from floor (top edge, ±2 mm) | Lower group 388 / 355 / 322; middle 755 / 721 / 687; upper 1121 / 1090 / 1056. Close-up photos read about 7 mm lower (likely parallax): treat as ±7 until confirmed. Middle group centers by tape 751 / 719 / 686 ± 3 (photos 014242, 013926), consistent with these top edges. | Measured (tape) |
| Pitch within a group | 34.8 ± 0.3 mm, by a rigid ruler flush with the strip, two groups (photos 144310, 144342). The earlier 31–34 was by tape, which bows toward the camera and reads short (config.3dp learnings). Confirm to ±0.3 with a printed pass/fail comb (pins at 34.0 / 34.5 / 35.0 / 35.5) before designing multi-hook parts. | Estimated (photos); comb pending |
| Group spacing | About 366 mm top slot to top slot | Measured |
| Glass-retaining buttons | Plastic turn-button cams on the glass-side edge of the strip, about 16.5 mm tall; 9.5 mm from the glass edge in photo 020620; whether that's the reach across the strip or the standoff from it is unconfirmed (check with an annotated crop before sizing the rail's button notches). Centers at about 260, 626, 996 and 1359 mm from the floor (about 61 mm below each slot group, plus one near the top); photos 020416, 020620, 020339 and 020238 agree within 3 mm. | Heights measured; size estimated (photos) |

## Design guidelines for this cabinet
1. **Design to the factory shelf, not the cabinet interior.** Replacement shelves and add-ons copy the stock shelf's 690 × 300 × 20 mm footprint and sit on the stock clips as it does, avoiding interior measurements, which vary with assembly.
2. **Grow lights run left to right.** A 2 ft T5 fixture (about 610 mm) can't fit front to back in the 300 mm shelf depth; side to side under the 690 mm shelf width it has about 80 mm to spare.
3. **Leave clearance for light connector plugs at the cabinet sides.** Linkable T5 plugs stick out past the fixture ends; with a centered 610 mm light they end up near the side clips. Check against the clip positions before finalizing any light mount.
4. **Full-depth parts won't fit flat on a P1S bed** (300 mm vs. the 256 mm bed). Print it diagonally (at 300 mm long, up to about 50 mm wide; inference from length + width ≤ about 354 mm, the 17 × 337 mm case in learnings/walls) or split it front to back with a dovetail joint.
5. **The steel frame is magnetic.** Magnetic-back lights such as the Barrina NF10/NL20 stick directly to it.
6. **Hooks into the strip slots (2026-10-03).** A hook's total height (shank + drop) must be less than the smallest slot reading, now 3.3 mm. To remove a hooked part, the lift must be more than the drop and less than slot height − shank. Size hooks to the slot, not to the stock clip's tab.

## Market notes
- A popular plant-cabinet alternative to the IKEA Milsbo; reviewers mention its pre-existing holes for fans and grow lights. *Listed.*
- **HobbyPilled** (hobbypilled.com and Etsy) sells 3/8" cast-acrylic shelves cut for this cabinet: full, half (with extended brackets) and horseshoe, rated 5–10 lb, $55–65 each or a 3-piece set, pre-drilled 1/4" for hanging Barrina lights; also 3D-printed grow-light mounts. *Listed.* The main competitor for printed accessories for this cabinet.

## Barrina T5 grow lights (for light mounts)
- The 2 ft magnetic model is the NF10 (10 W); the 4 ft model is the NL20. Barrina doesn't publish fixture cross-section dimensions.
- The 2 ft fixture is about 610 mm (24.02") long. *Listed.*
- One reseller lists 0.79" (about 20 mm) width and height. *Listed, low confidence*; caliper it before designing a clip.
- Package contents include installation clips, magnetic bars with double-sided tape, and cable ties.

## Open items
- Slot pitch: confirm 34.8 ± 0.3 with a printed pass/fail comb (rail)
- Slot height: photos read 3.3–3.7, measured 4; settle with the hook pass/fail piece
- Strip width, by calipers (17.5 mm assumed)
- Barrina fixture profile (width, height, any groove) and plug length
- Number of lights per shelf
- Stock clip under load and factory-shelf profile photos: photos.unicoly Wanted.
- Glass button thickness off the strip face (rail button notches)
- Front-to-rear distance between the slotted strip faces

## Sources
- UNICOLY listing on Amazon: https://www.amazon.com/UNICOLY-Glass-Display-Cabinet-4-Tier/dp/B0DX1GKH3F
- UNICOLY LED version (same footprint): https://www.amazon.com/UNICOLY-Display-Cabinet-Assembly-Required/dp/B0DPWXBRKD
- HobbyPilled acrylic shelves for this cabinet: https://hobbypilled.com/products/unicoly-acrylic-shelves-shelves-for-amazons-unicoly-glass-cabinet-alternative-ikea-greenhouse
- Barrina NF10 2 ft: https://www.barrina-led.com/products/barrina-t5-10w-led-grow-lights-2ft-5000k-full-spectrum-magnetic-linkable-nf10
- Barrina NL20 4 ft: https://www.barrina-led.com/products/barrina-t5-20w-led-grow-lights-4ft-5000k-full-spectrum-magnetic-linkable-nl20
- openGrid docs: https://www.opengrid.world/guides/snaps/

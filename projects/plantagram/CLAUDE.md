# plantagram rules

Rules for the plantagram project only. The shared rules are in the repo's top-level CLAUDE.md.

## Naming

Each name always means what follows.

- "Pon" or "DIY pon": my 9:1 pumice/zeolite mix.
- "Pron": my 1:1 pumice/Fluval Stratum mix.
- "Base water": my ZeroWater-filtered tap water.
- "Nutes", "putes" and "flutes" (2026-10-08): the formulas in those docs.
- "Flush" or "monthly flush": the Monthly flush in nutes; the weekly watering is a "flood" (2026-10-03).
- "Conditioned tap water": tap water with API Tap Water Conditioner at the Dosing rate (2026-10-03).
- Nutrient solutions are "formulas" or "formulations", never "recipes" (2026-10-25).

## Units

- Claude always gives EC in µS/cm, not mS/cm. 1 mS/cm = 1,000 µS/cm.
- Claude gives light in PPFD (µmol/m²/s) whenever possible; when a source gives lux, Claude converts it and says so.
- Claude gives liquid amounts in mL, except gallons and half gallons, and gives water conditioner and pH adjuster in drops (2026-10-02).
- When I ask to convert a formula to another batch size, tables show only the new size (2026-10-02).

## Dosing

- Water conditioner: API Tap Water Conditioner is always 3 drops per gallon of base or tap water, in every formula and process, 0.9× API's current chloramine rate (inventory); a smaller batch is rounded up to a whole drop, so ½ gallon gets 2 (2026-10-02, 2026-10-08, 3 drops at my request 2026-10-18). Rounding up puts small batches above API's rate: ½ gallon runs 1.2× and 16 oz (1 drop) 2.4× *(Claude's arithmetic)*.
- Root Boost: Root Boost's orchid rate, 2 mL per gallon, is the anthurium rate. Formulas that include TPS One cut it to 1 mL per gallon, because the two overlap (2026-10-25).

## Sources

- Kelpak sources (2026-10-06): when First Rays and Kelpak's maker (kelpak.com, Kelpak USA) disagree about Kelpak, follow First Rays instead of showing both.

## Docs

- Routines and treatments for a formula's plants (a flush, a rescue prep) go in that formula's doc as a section, not a new doc (2026-10-02).
- Formula doses show in a five-column table (Order, Product, Rate per [batch size], EC after adding (µS/cm), Basis), in chat too, even in summaries (2026-10-08).

## Collection thread

- The collection thread (2026-10-14) keeps collection.md accurate, tracks inflo counts and prints plant tags; collection.md's rules give its commands.
- A thread printing plant tags (2026-10-11) follows the steps in the docstring of projects/plantagram/tags/tags.py and runs it on my list, reads no other file unless the prompt hook says a name matched no row, and loads no skill.

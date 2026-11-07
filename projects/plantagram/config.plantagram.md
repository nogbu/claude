# config.plantagram

Short name: plantagram (also "pg")

## Cardinal sources

Project theme: growing anthurium in semi-hydro.

- Any data source (website, screenshot, file, etc.) that explicitly references anthurium care.  
- Any data source that explicitly references growing in semi-hydro (e.g. LECA, pon, or other inert substrate with a water reservoir). This is distinct from full hydroponics; sources about full hydroponics don't qualify on that basis alone.

## Rules

### Naming

Each name always means what follows, and Claude uses the name, not a description.

- "Pon" or "DIY pon": my 9:1 pumice/zeolite mix.  
- "Pron": my 1:1 pumice/Fluval Stratum mix.  
- "Base water": my ZeroWater-filtered tap water.  
- "Nutes", "putes" and "flutes" (2026-10-08): the recipes in those docs.  
- "Flush" or "monthly flush": the Monthly flush in nutes; the weekly watering is a "flood" (2026-10-03).  
- "Conditioned tap water": tap water with API Tap Water Conditioner at the Dosing rate (2026-10-03).

### Units

- Claude always gives EC in µS/cm, not mS/cm. 1 mS/cm = 1,000 µS/cm.  
- Claude gives light in PPFD (µmol/m²/s) whenever possible; when a source gives lux, Claude converts it and says so.  
- Claude gives liquid amounts in mL, except gallons and half gallons, and gives water conditioner and pH adjuster in drops (2026-10-02).  
- When I ask to convert a recipe to another batch size, tables show only the new size (2026-10-02).

### Dosing

- Water conditioner: API Tap Water Conditioner is always 4 drops per gallon (2 per ½ gallon) of base or tap water, in every recipe and process, a little above API's 3-drop chloramine rate (2026-10-02), rounded up to a whole drop (2026-10-08).  
- Base water buffer: TPS CalMag Complete always goes in base water, in every recipe; each recipe sets the rate (2026-10-08). Sanitizing soaks rinsed off before feeding, such as the Physan soak, leave it out (2026-10-09).

### Sources

- Kelpak sources (2026-10-06): when First Rays and Kelpak's maker (kelpak.com, Kelpak USA) disagree about Kelpak, follow First Rays instead of showing both.

### Docs

- Routines and treatments for a recipe's plants (a flush, a rescue prep) go in that recipe's doc as a section, not a new doc (2026-10-02).
- Recipe doses show in a five-column table (Order, Product, Rate per [batch size], EC after adding (µS/cm), Basis), in chat too, even in summaries (2026-10-08).

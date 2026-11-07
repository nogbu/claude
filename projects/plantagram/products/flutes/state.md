---
about: Weekly recipe for flowering anthuriums in pon, used in place of nutes
readonly: no
---
# flutes

Plantagram product doc (created 2026-10-08).

## Current version

- **v2, 2026-10-08:** 16 oz batch (v1 was per gallon).  
- **Scope:** any anthurium in spathe or bud (agreed 2026-10-08), in DIY pon, every weekly flood, in place of nutes (config.plantagram).

## Recipe (per 16 oz of base water)

Add one product at a time, stirring between; never combine concentrates. Doses follow TPS's own rates, then are checked against a target total EC (Decisions).

| Order | Product | Rate per 16 oz (473 mL) | EC after adding (µS/cm) | Basis |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Base water | 473 mL | \~0 *(measured)* | |
| 2 | API Tap Water Conditioner | 1 drop | \~0 *(measured in nutes)* | Dosing rule (config.plantagram): 0.5 drop, rounded up |
| 3 | TPS CalMag Complete | 0.3 mL | \~390 *(est.; \~162 per mL/gal measured in nutes)* | Base water buffer (config.plantagram); my rate, 2.4 mL/gal (nutes 2) |
| 4 | TPS One | 0.7 mL | \~1,035 *(est.; \~115 per mL/gal)* | My rate, 5.6 mL/gal; product page "generally at 5-6mL per gallon" |
| 5 | TPS Signal | 0.25 mL | \~1,085–1,115 *(est.; never measured)* | TPS One page FAQ: added to TPS One "in bloom at about 2mL per gallon" |
| 6 | TPS Root Boost | 0.3 mL | \~1,145–1,175 *(est.; \~25 per mL/gal measured)* | My rate, 2.4 mL/gal; TPS hydro feedchart is 1 mL/gal weekly, 2–3× for root rot |
| 7 | HygroZyme | 1 mL | \~1,150–1,180 *(est.; \~5 measured in nutes)* | Label rate (8–10 mL/gal), as nutes |
| 8 | TPS pH Up | As needed | — | Target 5.5–6.2 (TPS hydro feedchart). Signal contains a pH buffer (TPS), so drops may differ from nutes' 6 |

CalMag, TPS One and Root Boost are my rates (2026-10-08); the rest are the per-gallon rate ÷ 8 *(inference)*. Basis rates are per gallon.  
*(inference; Claude's label math)* About 84 ppm N, 51 P, 75 K, 46 Ca, 22 Mg, 7 S; K:N about 0.9 (nutes about 0.7).

## Use

1. **Same routine as nutes:** fresh batch weekly, flood every pot, plain base water top-up on day 3–4, day-7 runoff EC, and nutes' day-7 adjustment table (target 1,000–1,200 µS/cm).  
2. **First batch:** log EC after Signal (its step was never measured) and after each later step. If the total runs over 1,200 µS/cm (nutes' day-7 ceiling; agreed 2026-10-08), drop TPS One to 0.6 mL.  
3. **Monthly flush:** as in nutes, refilled with putes' day-7 batch.

## Decisions and why

- **Doses from TPS's own rates** (agreed 2026-10-08, at my request): TPS's feedcharts are week-by-week cannabis schedules with no houseplant or anthurium chart, so rates come from TPS labels, product pages and the hydro feedchart's every-week rows.  
- **CalMag 0.3, TPS One 0.7, Root Boost 0.3 mL per 16 oz** (agreed 2026-10-08, at my request; 2.4, 5.6 and 2.4 mL/gal). Replaced 2, 5 and 1 mL/gal.  
- **TPS One near 5 mL/gal, not the feedchart's bloom rate** (agreed 2026-10-08): the hydro feedchart's lowest bloom rate is 12 mL/gal (EC 1,100–1,200 for TPS One alone), which would start flutes near 1,800 µS/cm *(inference)*, above nutes' day-7 ceiling and the 1,000–1,500 tolerated in pumice (Özçelik & Özkan 2002). Working back from nutes' \~930 target also gives 4.5–5 mL *(inference)*.  
- **Moderate EC for this setup** *(inference)*: low light (65–85 PPFD), warm root zone (cabinets 78–80°F; Anthura's ideal 24-hour average is 66–72°F), and fans that concentrate the reservoir. Putes' research found salt stress sharply raises water-mold root rot.  
- **Signal at 2 mL/gal** (agreed 2026-10-08): TPS One's page dose. Anthurium growers feed more K than N (Dutch standard \~74 N, 117 K ppm, via Haifa; Anthura's table works out near 108 N, 172 K *(inference: units read as mmol/L)*), while First Rays warns that extra K competes with Ca and Mg; the sources disagree. 2 mL raises K:N from \~0.7 to \~0.9.  
- **Root Boost weekly** (agreed 2026-10-08): keeps live *Bacillus* in the root zone.  
- **16 oz batch** (agreed 2026-10-08, at my request); conditioner at 1 drop, since the 4-drop/gal rate is half a drop (agreed 2026-10-08).  
- **RootShield, Silica Gold, SNS 209 left out:** see nutes (flush refill decisions) and nutes' Keep out of the reservoir.

## Light is the bigger lever

Anthura wants about 200 PPFD (\~15 klux) and 9 mol/m²/day for flowering pot anthuriums; too little light gives "lower flower production." My shelves measure 65–85 PPFD, about 3.3–4.3 mol/day (nutes). First Rays: blooms come from good light and lower nitrogen; no "bloom booster" adds flowers. Feed changes alone likely won't raise flowering much at this light *(inference)*.

## Sources

- [TPS One product page](https://tpsnutrients.com/products/tps-one) (favored; FAQ Signal dose, read 2026-10-08) · [TPS feedcharts](https://tpsnutrients.com/pages/feedcharts) (favored; TPS One hydro and Component hydro charts, Plant Growth Guide 2022, read 2026-10-08)  
- [Anthura, Cultivation Guide Anthurium pot plants](https://mindcms-main.s3.eu-west-2.amazonaws.com/dXBkYXRlLW1pbmRjbXMtbmw=/686fa754746bd/cultivation-guide-anthurium-pot.pdf): light, temperature, feeding table, EC 1.8–2.4 for overhead irrigation in Dutch greenhouses  
- [Floricultura, Anthurium pot plant cultivation manual (2019)](https://www.floricultura.com/media/5301/anthurium-cultivation-manual-2019_en.pdf): about 225 PPFD ideal; too little light gives poor flowering  
- [Haifa Group, Anthurium andreanum fertilization](https://www.haifa-group.com/fertilization-anthurium-andereanum-sandy-soil-or-soilless): Dutch standard solution, EC 0.8–1.2 mS/cm, pH 5.5–6.6  
- First Rays (favored; firstrays): nitrogen 75–125 ppm a week; excess N suppresses blooming; potassium caution

## Open questions

- **Measuring tools:** setup lists none; doses down to 0.25 mL (Signal) need a 1 mL syringe marked in 0.05 mL or finer *(inference)*.  
- **Signal EC:** never measured; log it on the first batch.  

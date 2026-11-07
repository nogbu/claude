---
name: nb-lists
about: NB negative lists walkthrough (reviewed 2026-10-06, not yet in rev3); NB_Negatives_List_Map_rev1.py reads it
read-when: before any NB negative list work
readonly: no
---
# NB negative keyword lists: walkthrough (reviewed 2026-10-06; not yet applied to the list docs or build)
Short name: nb-lists. Companion to neg-audit. Negatives for the 12 NB campaigns, sorted into the existing list themes (user, 2026-10-06), plus one new list where none fits.

Scope and method
- Source: search terms report, Sep 5 – Oct 4, 2026 (deleted 2026-10-08, as were the Aug 1 – Oct 7 pulls on 2026-10-09; the only search terms data on file is Untitled report (2).csv, a day-level pull without campaigns). All 12 NB campaigns, Enroll and RAQ (user's choice, 2026-10-06); candidates judged on Enroll conversions only.
- Terms already blocked by the reviewed lists NB will carry (AARP and Delta Dental Traffic, Competitor, Spanish, ENT/NENT Location, plus rev3 "deltadentalcoversme") were removed first: $19,092 of NB spend left, 7 Enroll conversions.
- Every candidate was tested against the NB positive keywords in the 2026-10-06 export (324 unique). Spend figures are Measured from the report.
- Spanish and Location: nothing worth adding (non-English $13, untargeted states $3).

Groups (candidates)
| List | Negatives | NB spend blocked | Enroll conv. | Status |
|---|---|---|---|---|
| Dental Care Negatives (new, NB) | 42 | $2,654 | 0 | Reviewed |
| Delta Dental Traffic Negatives, additions | 34 + 29 unsearched states | $970 | 0 | Reviewed (all 63 negate) |
| AARP Traffic Negatives, additions | 4 | $216 | 1 | Reviewed (all negate) |
| Competitor Negatives, additions | 12 | $369 | 0 | Reviewed (all negate) |

## Dental Care Negatives (reviewed 2026-10-06)
People pricing or looking for dental work, not insurance. Spend = NB spend each keyword matches on its own (overlaps counted under each).

| # | Negative keyword | Match | Spend | Searches | Decision |
|---|---|---|---|---|---|
| 1 | affordable dentist | PHRASE | $66 | 118 | Negate |
| 2 | best dentist | PHRASE | $157 | 503 | Negate |
| 3 | bone | BROAD | $19 | 67 | Negate |
| 4 | braces | BROAD | $39 | 322 | Negate |
| 5 | bridge | BROAD | $133 | 292 | Negate |
| 6 | canal | BROAD | $116 | 328 | Negate |
| 7 | cheap dentist | PHRASE | $55 | 88 | Negate |
| 8 | cleaning | BROAD | $109 | 422 | Negate |
| 9 | cost of dental implants | PHRASE | $33 | 52 | Negate |
| 10 | cost of dentures | PHRASE | $54 | 44 | Negate |
| 11 | cost of implants | PHRASE | $15 | 13 | Negate |
| 12 | crown | BROAD | $123 | 569 | Negate |
| 13 | dds | BROAD | $6 | 47 | Negate |
| 14 | dentist in | PHRASE | $301 | 1145 | Negate |
| 15 | dentistry | BROAD | $42 | 329 | Negate |
| 16 | dentists | BROAD | $107 | 611 | Negate |
| 17 | denture | BROAD | $87 | 238 | Negate |
| 18 | dentures cost | PHRASE | $207 | 219 | Negate |
| 19 | dr | BROAD | $36 | 145 | Negate |
| 20 | emergency | BROAD | $9 | 38 | Negate |
| 21 | extraction | BROAD | $42 | 220 | Negate |
| 22 | extractions | BROAD | $105 | 46 | Negate |
| 23 | filling | BROAD | $28 | 140 | Negate |
| 24 | gum | BROAD | $16 | 82 | Negate |
| 25 | how much are dentures | PHRASE | $11 | 16 | Negate |
| 26 | how much do dentures | PHRASE | $48 | 23 | Drop (redundant: all its spend is blocked by "dentures cost"; revisit later) |
| 27 | implant | BROAD | $242 | 595 | Negate |
| 28 | implants cost | PHRASE | $133 | 183 | Negate |
| 29 | invisalign | BROAD | $52 | 111 | Negate |
| 30 | partial | BROAD | $65 | 199 | Negate |
| 31 | partials | BROAD | $4 | 27 | Negate |
| 32 | price list | PHRASE | $9 | 17 | Negate |
| 33 | prices list | PHRASE | $58 | 5 | Negate |
| 34 | pulled | BROAD | $31 | 87 | Negate |
| 35 | screwless | BROAD | $24 | 31 | Negate |
| 36 | silicone | BROAD | $15 | 12 | Negate |
| 37 | snap | BROAD | $47 | 77 | Negate |
| 38 | teeth | BROAD | $289 | 1212 | Negate |
| 39 | tooth | BROAD | $353 | 1249 | Negate |
| 40 | veneer | BROAD | $5 | 32 | Negate |
| 41 | veneers | BROAD | $107 | 256 | Negate |
| 42 | whitening | BROAD | $26 | 66 | Negate |
| 43 | wisdom | BROAD | $20 | 124 | Negate |
Notes
- "dentures", "implants" and "dentist" (BROAD) were left out: they block the NB keywords "affordable dentures for seniors", "affordable dental implants for seniors" and "dentist that accept medicare". Phrases stand in for them.
- "crowns", "canals", "bridges" and "orthodontic" were left out: most of their spend is insurance shoppers ("dental insurance that covers crowns").
- extraction, pulled, silicone, veneer, whitening and wisdom add $0 beyond the rest of the list in this period; kept because they also block searches without "tooth" or "teeth".

## Delta Dental Traffic Negatives, additions (reviewed 2026-10-06)
Spend = NB spend each keyword matches on its own; Searches = distinct search terms. 0 Enroll conversions on every item. No conflicts with the NB keywords.

| # | Negative keyword | Match | Spend | Searches | Decision |
|---|---|---|---|---|---|
| 1 | dd | BROAD | $17 | 40 | Negate |
| 2 | deltadentalak | BROAD | $3 | 2 | Negate |
| 3 | deltadentalar | BROAD | $12 | 7 | Negate |
| 4 | deltadentalaz | BROAD | $22 | 11 | Negate |
| 5 | deltadentalca | BROAD | $12 | 3 | Negate |
| 6 | deltadentalct | BROAD | $14 | 4 | Negate |
| 7 | deltadentalga | BROAD | $28 | 3 | Negate |
| 8 | deltadentalia | BROAD | $19 | 8 | Negate |
| 9 | deltadentalil | BROAD | $8 | 16 | Negate |
| 10 | deltadentalinsurance | BROAD | $20 | 2 | Negate |
| 11 | deltadentalks | BROAD | $7 | 6 | Negate |
| 12 | deltadentalma | BROAD | $14 | 11 | Negate |
| 13 | deltadentalmi | BROAD | $24 | 11 | Negate |
| 14 | deltadentalmn | BROAD | $5 | 5 | Negate |
| 15 | deltadentalmo | BROAD | $15 | 14 | Negate |
| 16 | deltadentalnc | BROAD | $4 | 3 | Negate |
| 17 | deltadentalnj | BROAD | $31 | 12 | Negate |
| 18 | deltadentalofgeorgia | BROAD | $4 | 1 | Negate |
| 19 | deltadentalofny | BROAD | $10 | 1 | Negate |
| 20 | deltadentaloh | BROAD | $15 | 7 | Negate |
| 21 | deltadentaloregon | BROAD | $9 | 1 | Negate |
| 22 | deltadentalri | BROAD | $3 | 3 | Negate |
| 23 | deltadentalsc | BROAD | $3 | 4 | Negate |
| 24 | deltadentaltn | BROAD | $18 | 8 | Negate |
| 25 | deltadentalva | BROAD | $21 | 9 | Negate |
| 26 | deltadentalwa | BROAD | $8 | 6 | Negate |
| 27 | deltadentalwi | BROAD | $25 | 14 | Negate |
| 28 | deltadentist | BROAD | $7 | 2 | Negate |
| 29 | deltadwntal | BROAD | $3 | 1 | Negate |
| 30 | deltains | BROAD | $45 | 5 | Negate |
| 31 | deltausa | BROAD | $13 | 1 | Negate |
| 32 | dental dental | PHRASE | $510 | 102 | Negate |
| 33 | dentaldentalins | BROAD | $18 | 1 | Negate |
| 34 | nedelta | BROAD | $3 | 6 | Negate |

Added for states with no searches this period (user, 2026-10-06; approved without item review), all BROAD, Negate, no NB keyword conflicts: deltadentalal, deltadentalco, deltadentaldc, deltadentalde, deltadentalfl, deltadentalhi, deltadentalid, deltadentalin, deltadentalky, deltadentalla, deltadentalmd, deltadentalme, deltadentalms, deltadentalmt, deltadentalnd, deltadentalne, deltadentalnh, deltadentalnm, deltadentalnv, deltadentalny, deltadentalok, deltadentalor, deltadentalpa, deltadentalsd, deltadentaltx, deltadentalut, deltadentalvt, deltadentalwv, deltadentalwy. (29)

Notes
- deltausa is DeltaUSA, a national Delta Dental entity (deltadental.com press release); nedelta.com is Northeast Delta Dental (ME, NH, VT). deltains is probably a short form of Delta Dental Insurance Company (unconfirmed). deltadentist, deltadwntal and dentaldentalins read as Delta Dental brand lookups or typos (inference).
- dental dental: mostly "dental dental" alone ($311) and "dental dental insurance" ($145); variants such as "dental dental covers me" and "dental dental premier" show it's mistyped Delta Dental (inference).

## AARP Traffic Negatives, additions (reviewed 2026-10-06)
Typed AARP Dental site names; the existing "aarp" and "myaarp" don't block merged forms. Domains unconfirmed by search. No NB keyword conflicts.

| # | Negative keyword | Match | Spend | Searches | Enroll conv. | Decision |
|---|---|---|---|---|---|---|
| 1 | aarpdental | BROAD | $38 | 11 | 1 | Negate |
| 2 | aarpdentalplan | BROAD | $6 | 1 | 0 | Negate |
| 3 | myaarpdental | BROAD | $13 | 2 | 0 | Negate |
| 4 | myaarpdentalplan | BROAD | $160 | 4 | 0 | Negate |

Notes
- aarpdental's 1 Enroll conversion came from "aarpdental com jointoday" on NB ENT Enroll ASI; Brand bids on "aarp dental" terms, so the search can still reach Brand (inference: positive keywords match merged words as close variants).
- myaarpdentalplan (BROAD) covers the General list's EXACT "myaarpdentalplan com my account" (General audit item 72, pending).

## Competitor Negatives, additions (reviewed 2026-10-06)
0 Enroll conversions and no NB keyword conflicts on every item. None is a name variant of a CO-targeted competitor (Aetna, Aspen Dental, Cigna, Humana, MetLife, United Healthcare, ZocDoc), so all 12 also go into Conquesting Negatives when it is recomputed (inference: 206 + 12 = 218).

| # | Negative keyword | Match | Company | Spend | Searches | Decision |
|---|---|---|---|---|---|---|
| 1 | altusdental | BROAD | Altus Dental Insurance Company (RI) | $7 | 1 | Negate |
| 2 | bcbsma | BROAD | Blue Cross Blue Shield of Massachusetts | $4 | 2 | Negate |
| 3 | clear choice | PHRASE | ClearChoice Dental Implant Centers | $70 | 105 | Negate |
| 4 | clearchoice | BROAD | ClearChoice Dental Implant Centers | $24 | 15 | Negate |
| 5 | comfort dental | PHRASE | Comfort Dental (office chain, in-house Gold Plan) | $19 | 26 | Negate |
| 6 | denali | BROAD | Denali Dental (dental insurance) | $137 | 12 | Negate |
| 7 | ersdentalplans | BROAD | Texas ERS dental plans (state employees, retirees) | $9 | 2 | Negate |
| 8 | healthspring | BROAD | HealthSpring (HCSC Medicare brand, formerly Cigna's) | $27 | 23 | Negate |
| 9 | liberty dental | PHRASE | LIBERTY Dental Plan | $39 | 18 | Negate |
| 10 | medica | BROAD | Medica (dental plans run by Delta Dental of MN) | $18 | 19 | Negate |
| 11 | uccitdp | BROAD | United Concordia, TRICARE Dental Program | $8 | 2 | Negate |
| 12 | webtpa | BROAD | WebTPA (benefits administrator) | $6 | 1 | Negate |

Notes
- Altus Dental: RI insurer; shared parent with Delta Dental of RI believed but unconfirmed.
- medica won't block medicare, medicaid or medical (negatives match whole words only).
- Not yet applied: org-decisions (Competitor Negatives, 218) and conquesting (206) still need these 12, then a list build.

## Flags for the positive-keyword phase
- "affordable dentures for seniors", "affordable dental implants for seniors" and "dentist that accept medicare" are NB keywords that attract care seekers; "affordable dentures" searches alone cost $305 (0 Enroll conversions). If removed, "dentures", "implants" and "dentist" could be negated BROAD (inference).

## Revisit later
- how much do dentures (PHRASE): dropped as redundant with "dentures cost".

---
name: geo-lists
about: ENT and NENT Location Negatives (reviewed)
read-when: before any Location Negatives work
readonly: yes
---
# ENT and NENT Location Negatives (created and reviewed 2026-09-28)
Companion to negative-keyword-audit.md.

Definitions (user):
- **ENT Location Negatives** contains ENT state names and abbreviations. It is applied to the **NENT** campaigns.
- **NENT Location Negatives** contains NENT state names and abbreviations. It is applied to the **ENT** campaigns.
- These are separate from **Location Negatives** (city/town names, applied to every campaign).

Decisions:
- Abbreviations left off because they are everyday words: co, in, ma, md, me, or, va.
- Kept: mt (user choice), plus al, de, la, hi, ms, oh, ok. All campaigns target English only, so blocking Spanish searches ("al", "de", "la") is fine.
- Washington: "washington state" (PHRASE) + "wa" on the NENT list. The ENT list gets "washington dc" (PHRASE), "district of columbia" (PHRASE) and "dc". Bare "washington" is not used because it would block ENT DC keywords.
- Untargeted places are saved for later, not yet placed: idaho, west virginia, wv, puerto rico, virgin islands, usvi (id, pr and vi were considered and left out).
- Conflict check: 0 conflicts with any active keyword.
- These likely replace legacy lists 6 and 10; compare when auditing those.
- Item-by-item review: ENT list complete, all 30 kept (2026-09-28). NENT list complete, all 62 kept (2026-09-28).

## Legacy "Delta - Enterprise States (NENT exclusions)" (57) compared, 2026-09-28: FINAL
- Every legacy state name and standard abbreviation is already covered, except md (intentionally left off).
- Added to ENT Location Negatives: ala, cal, calif, del, fla, geo, nev, penn, tex (all BROAD; legacy period forms without the period) and "district of colombia" (PHRASE; a common misspelling).
- Legacy period forms already covered: D.C., Ga., La., N.Y., Pa., Ut.
- Skipped (revisit later): dis col, mar, md, miss, mont, n york.
- West Virginia / Puerto Rico entries (west virginia, wv, w. va, w. vir., w. virg., puerto rico, pr, p.r.) join the saved-for-later untargeted places.
- All additions checked: 0 conflicts with NENT keywords.

## Legacy "Delta - Non-Enterprise (ENT exclusions)" (125) comparison, 2026-09-28: FINAL
- 66 already covered.
- 6 previously decided to leave off: CO, MA, Me., OR, VA, Va.
- 6 untargeted (to the saved-for-later group): ID, Ida., Idaho, VI, Virgin Islands, U.S.V.I.
- 46 walked through (B = add without the period, S = skip/revisit later):
  - Decided so far (1–30): alas S, ariz B, ark B, col S, colo B, conn B, ill S, ills S, ind B, ioa S, ka S, kan B, kans B, ken S, kent S, mass B, mich B, minn B, N.C. S, n car S, n dak S, N.H. S, n hamp S, N.J. S, n jersey S, n mex S, neb S, nebr S, new m S, new mex S, o S, okla S, ore S, oreg S, R.I. S, S.C. S, s car S, s dak S, tenn B, verm S, virg S, w S, wash B, wis B, wisc B, wn S, wyo S.
  - Result: 14 added to NENT Location Negatives (BROAD): ariz, ark, colo, conn, ind, kan, kans, mass, mich, minn, tenn, wash, wis, wisc. 0 conflicts with ENT keywords.
  - Re-check done: ill, ills, ken, kent, alas stay skipped; mar stays skipped; "miss." (with period, BROAD) ADDED to ENT Location Negatives (user choice).

## ENT Location Negatives (41), applied to NENT campaigns
Additions from the legacy comparisons: ala, cal, calif, del, fla, geo, nev, penn, tex (BROAD); district of colombia (PHRASE); miss. (BROAD, with period). The original 30 follow.

| Negative keyword | Match | State |
|---|---|---|
| al | BROAD | Alabama |
| alabama | BROAD | Alabama |
| ca | BROAD | California |
| california | BROAD | California |
| dc | BROAD | District of Columbia |
| de | BROAD | Delaware |
| delaware | BROAD | Delaware |
| district of columbia | PHRASE | District of Columbia |
| fl | BROAD | Florida |
| florida | BROAD | Florida |
| ga | BROAD | Georgia |
| georgia | BROAD | Georgia |
| la | BROAD | Louisiana |
| louisiana | BROAD | Louisiana |
| maryland | BROAD | Maryland |
| mississippi | BROAD | Mississippi |
| montana | BROAD | Montana |
| ms | BROAD | Mississippi |
| mt | BROAD | Montana |
| nevada | BROAD | Nevada |
| new york | PHRASE | New York |
| nv | BROAD | Nevada |
| ny | BROAD | New York |
| pa | BROAD | Pennsylvania |
| pennsylvania | BROAD | Pennsylvania |
| texas | BROAD | Texas |
| tx | BROAD | Texas |
| ut | BROAD | Utah |
| utah | BROAD | Utah |
| washington dc | PHRASE | District of Columbia |

## NENT Location Negatives (76), applied to ENT campaigns
Additions from legacy list 6: ariz, ark, colo, conn, ind, kan, kans, mass, mich, minn, tenn, wash, wis, wisc (BROAD). The original 62 follow.
| Negative keyword | Match | State |
|---|---|---|
| ak | BROAD | Alaska |
| alaska | BROAD | Alaska |
| ar | BROAD | Arkansas |
| arizona | BROAD | Arizona |
| arkansas | BROAD | Arkansas |
| az | BROAD | Arizona |
| colorado | BROAD | Colorado |
| connecticut | BROAD | Connecticut |
| ct | BROAD | Connecticut |
| hawaii | BROAD | Hawaii |
| hi | BROAD | Hawaii |
| ia | BROAD | Iowa |
| il | BROAD | Illinois |
| illinois | BROAD | Illinois |
| indiana | BROAD | Indiana |
| iowa | BROAD | Iowa |
| kansas | BROAD | Kansas |
| kentucky | BROAD | Kentucky |
| ks | BROAD | Kansas |
| ky | BROAD | Kentucky |
| maine | BROAD | Maine |
| massachusetts | BROAD | Massachusetts |
| mi | BROAD | Michigan |
| michigan | BROAD | Michigan |
| minnesota | BROAD | Minnesota |
| missouri | BROAD | Missouri |
| mn | BROAD | Minnesota |
| mo | BROAD | Missouri |
| nc | BROAD | North Carolina |
| nd | BROAD | North Dakota |
| ne | BROAD | Nebraska |
| nebraska | BROAD | Nebraska |
| new hampshire | PHRASE | New Hampshire |
| new jersey | PHRASE | New Jersey |
| new mexico | PHRASE | New Mexico |
| nh | BROAD | New Hampshire |
| nj | BROAD | New Jersey |
| nm | BROAD | New Mexico |
| north carolina | PHRASE | North Carolina |
| north dakota | PHRASE | North Dakota |
| oh | BROAD | Ohio |
| ohio | BROAD | Ohio |
| ok | BROAD | Oklahoma |
| oklahoma | BROAD | Oklahoma |
| oregon | BROAD | Oregon |
| rhode island | PHRASE | Rhode Island |
| ri | BROAD | Rhode Island |
| sc | BROAD | South Carolina |
| sd | BROAD | South Dakota |
| south carolina | PHRASE | South Carolina |
| south dakota | PHRASE | South Dakota |
| tennessee | BROAD | Tennessee |
| tn | BROAD | Tennessee |
| vermont | BROAD | Vermont |
| virginia | BROAD | Virginia |
| vt | BROAD | Vermont |
| wa | BROAD | Washington |
| washington state | PHRASE | Washington |
| wi | BROAD | Wisconsin |
| wisconsin | BROAD | Wisconsin |
| wy | BROAD | Wyoming |
| wyoming | BROAD | Wyoming |

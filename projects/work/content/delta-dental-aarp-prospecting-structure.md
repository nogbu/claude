---
name: structure
about: Account structure snapshot from the 2026-09-28 export; the current structure is in delta-dental
read-when: only for the structure as of 2026-09-28
readonly: yes
---
# Delta Dental – AARP SEM: Prospecting campaign structure (Google Ads)
Source: Google Ads Editor export, 2026-09-28 (31 campaigns, all "Prospecting"). Account ID 7783329500, managed via SA360.

## Product context
- AARP Dental Insurance Plan, administered by Delta Dental Insurance Company. Only AARP members (plus spouse/partner, dependents under 26) can enroll. Current Delta Dental customers who are not AARP members are NOT eligible. AARP membership is open to anyone 18+ ($15 first year with auto-renew, then $20/yr).
- Plans: PPO Protect Plus, PPO Protect Propel, PPO Protect (all states); DeltaCare USA Essential DHMO (AZ, CA, CO, DC, FL, GA, IL, KY, MD, MI, MO, NM, NV, NY, OH, PA, TN, TX, WV only).
- Landing page: https://www1.deltadentalins.com/aarp.html. Final URL suffix: mcid=ps_ddins_00002&gclsrc=aw.ds&{_dsmrktparam}

## Geo groups (working lists from the user; known inconsistencies to be resolved later)
- ENT: AL, CA, DE, FL, GA, LA, MD, MS, MT, NV, NY, PA, TX, UT, Washington DC (Hagerstown MD) media market. ENT campaigns exclude all NENT states plus VA, WV, ID, USVI.
- NENT: AK, AZ, AR, CO, CT, HI, IL, IN, IA, KS, KY, ME, MA, MI, MN, MO, NE, NH, NJ, NM, NC, ND, OH, OK, OR, RI, SC, SD, TN, VT, VA, WA, WI, WY. NENT campaigns exclude all ENT states plus ID, WV and Washington DC.
- Not targeted anywhere: ID, WV, PR, VI.

## Campaign categories (terminology set by user, 2026-09-28)
- **Active (12):** enabled campaigns. These are the July 2026 restructure (Brand and NB), plus the Competitor (CO) and Demand Gen (DG) campaigns.
- **Legacy (5):** old-structure campaigns that were rolled into the restructure. They are paused now but have performance data in the last 90 days, so they serve as the "before" baseline.
  - G_AARP_NB_NENT_45+_Seniors_Prospecting
  - G_AARP_NB_ENT_45+_Seniors_Prospecting
  - G_AARP_NB_ENT_45+_ALL_State_Prospecting
  - G_AARP_NB_NENT_45+_ALL_Prospecting
  - G_AARP_NB_ENT_45+_ALL_Prospecting
- **Archived (14):** paused or ended, with no performance data in the last 90 days. Keep on record but leave out of the analysis for now.
  - Broad match tests (est5793): 2 campaigns
  - SA360 VBB tests (est7126): 5 campaigns
  - Search partner tests (SP_est7126): 5 campaigns
  - 2025 "_Test" campaigns: 2

## Active campaigns (total daily budget $3,755)
| Campaign | Type | Bidding | Daily budget | Launched |
|---|---|---|---|---|
| G_AARP_Brand_ENT_Enroll_Prospecting | Search | Maximize conversions | 369 | 2026-07-08 |
| G_AARP_Brand_ENT_RAQ_Prospecting | Search | Maximize conversions | 700 | 2026-07-08 |
| G_AARP_Brand_NENT_Enroll_Prospecting | Search | Maximize conversions | 1,238 | 2026-07-09 |
| G_AARP_Brand_NENT_RAQ_Prospecting | Search | Maximize conversions | 560 | 2026-07-15 |
| G_AARP_NB_ENT_Enroll_Prospecting | Search | Maximize clicks | 65 | 2026-07-21 |
| G_AARP_NB_ENT_RAQ_Prospecting | Search | Maximize clicks | 225 | 2026-07-21 |
| G_AARP_NB_NENT_Enroll_Prospecting | Search | Maximize clicks | 85 | 2026-07-21 |
| G_AARP_NB_NENT_RAQ_Prospecting | Search | Maximize clicks | 155 | 2026-07-21 |
| G_AARP_CO_ENT_45+_ALL_Prospecting | Search (conquesting) | Maximize clicks, $5 CPC cap | 150 | 2026-04-06 |
| G_AARP_CO_NENT_45+_ALL_Prospecting | Search (conquesting) | Maximize clicks, $5 CPC cap | 120 | 2026-06-03 |
| G_AARP_DG_ENT_Enroll_Prospecting | Demand Gen | Maximize clicks | 44 | 2026-08-12 |
| G_AARP_DG_NENT_Enroll_Prospecting | Demand Gen | Maximize clicks | 44 | 2026-08-12 |

All use account-level conversion goals. The Brand and NB campaigns are labelled "Delta - AARP SEM July 2026 Restructure"; the CO campaigns are labelled "Conquesting 2026".

## Ad group structure (active campaigns)
- Brand: a Brand_General ad group plus one ad group per state (ENT 16 ad groups, NENT 33). Each state ad group holds 6 keywords ("delta dental [state]", "delta dental aarp [state]", "aarp dental insurance [state]", exact + broad). Brand_General negates the state names.
- NB: an NB_General ad group plus one ad group per state (12 keywords each). ENT has 16 ad groups, NENT 33. Iowa and South Dakota have no state ad group in NENT.
- CO: one ad group per competitor: Aetna, Aspen Dental, Cigna, Humana, MetLife, United Healthcare, ZocDoc. The EXM and PHM ad groups are paused (EXM was replaced in the week of Sep 14).
- Keywords are paired exact + broad throughout.
- Enroll and RAQ campaigns have IDENTICAL keywords, ads and final URL.
- Ads: one RSA per ad group, and only 2 unique RSA variants across 214 ad groups. 202 ads are rated Poor ad strength.
- Audiences: observation mode, with suppression lists excluded (enrolled list, Supp tiers, remarketing).
- Age exclusions: ENT excludes 18–54; NENT excludes 18–44.

## Shared negative keyword lists on active campaigns (list contents not yet reviewed)
| List | Keywords | Attached to |
|---|---|---|
| MS - Master Negative Keyword Blacklist | 2,494 | Brand ×4, NB ×4 |
| Delta - Competitor Negatives | 393 | Brand ×4, NB ×4 |
| Delta - Spanish Negatives for English Campaigns | 260 | Brand ×4, NB ×4 |
| Delta - Brand Keywords (for NB, CO campaigns) | 256 | NB ×4, CO ×2 |
| Delta - Non-Enterprise (ENT exclusions) | 125 | ENT Brand, NB and CO campaigns |
| Delta - General Negatives | 123 | Brand ×4, NB ×4, CO ×2 |
| Delta - NonBrand EX Keywords (for CO) | 95 | CO ×2 |
| Lorem Ipsum | 92 | Brand ×4, NB ×4 |
| Delta - Enterprise States (NENT exclusions) | 57 | NENT Brand, NB and CO campaigns |
| September Shooting | 20 | Brand ×4, NB ×4 |
| Competitor | 16 | Brand ×4, NB ×4 |
| AARP Negatives | 15 | Brand ×4, NB ×4 |
| Delta - Brand & AARP Negatives | 3 | NB ×4 |

The DG campaigns have no shared negative lists.

## Recommendations (not yet acted on)
- Demand Gen (2026-09-28): keyword negatives don't apply. The 90-day pattern (128.8k clicks, $0.08 CPC, 0.07% conversion rate, 2 enrollments; source: perf-90d) points to Maximize clicks buying cheap app and Display clicks. Recommended: conversion-based bidding, YouTube/Discover/Gmail only (Display Network off), app and gaming placement exclusions, the same audience exclusions as Search; or pause until the Search restructure is settled.

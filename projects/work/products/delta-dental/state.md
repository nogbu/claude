---
name: delta-dental
about: Client doc for Delta Dental: accounts, latest export (2026-10-06), naming taxonomy, structure, shared lists
read-when: before any Delta Dental account work
readonly: no
---
# Client: Delta Dental

## Product rules
- "dd" = Delta Dental.  
- Goal: reach AARP members who are looking for dental insurance. Negate as much irrelevant traffic as possible.  
- Optimize for Enroll campaign conversions only. Ignore RAQ campaigns and their conversions in every analysis and recommendation.  
- Never block AARP plan names in Brand campaigns: PPO Protect Plus, PPO Protect Propel, PPO Protect, DeltaCare USA Essential, PPO Plan A, PPO Plan B, "delta dental ppo", "deltacare", "deltacare usa". Block every other dd plan name.  
- Treat Delta Dental affiliates (Dentegra, Moda, Hawaii Dental Service, etc.) as dd brand terms.  
- The Traffic Negatives lists never go on Brand campaigns.  
- Any list attached to CO must not block the CO ad groups' competitor names or their name variants (misspellings, short forms, joined forms). Check every list, not only Competitor Negatives.  
- Location Negatives never contain state names for states Brand or NB bid on. State searches are insurance shoppers.  
- All campaigns target English only, so blocking non-English searches is fine.  
- Negative-keyword audit: scope is negatives only; positive keywords are evaluated in a later phase. Every list, new or legacy, gets a full item-by-item review by me. The search terms report comes only after the cleanup of existing negatives is finished.  
- Remind me of the deferred legacy lists (MS - Master Negative Keyword Blacklist, September Shooting) whenever the active tracker is complete, and before any final build or wrap-up.

## Accounts
| Platform | Account | Account ID | Managed via |
|---|---|---|---|
| Google Ads | Delta Dental – AARP | 7783329500 | SA360 (confirmed by user 2026-10-06) |

## Latest export
- Google Ads Editor export, shared 2026-10-06 (export.csv, UTF-16 tab-separated, 37,191 rows, 253 columns): /mnt/project-files/uploads/hearth/40ca096f-4ace-446f-b560-9f2f96f51ccc.
- 32 campaigns, all Enabled; the full account structure, no performance data.
- Figures below are Measured from this export unless tagged.

## Product context
- Product: AARP Dental Insurance Plan, administered by Delta Dental Insurance Company; underwritten by state by Delta Dental Insurance Company, Dentegra Insurance Company or affiliates. DeltaCare USA: underwritten by Alpha Dental entities or Delta Dental companies, by state.
- Brand and product names: AARP Dental Insurance Plan, Delta Dental, Delta Dental PPO, DeltaCare USA, plus the plan names (Product rules; log: AARP plan and enrollment details).
- Landing page: https://www1.deltadentalins.com/aarp.html

## Goals and conversions
- Account-default goal "Other" has two primary actions (AARP Enrollment Confirmation, AARP Get A Quote Click); no campaign has its own goal (Measured, conversion goals screenshot 2026-10-06), so Enroll campaigns on Smart Bidding also bid toward quote clicks and Conversions columns include them (fix: perf-30d recommendation 1).

## Naming taxonomy
**Campaigns: `G_AARP_[Type]_[Geo]_[Goal]_[Audience]`**
- G: Google Ads (inference). AARP: the program.
- Type: Brand, NB (nonbrand), CO (competitor), PMAX (Performance Max), DG (Demand Gen).
- Geo: ENT or NENT (state groups, see Locations).
- Goal: Enroll or RAQ ("request a quote", inference).
- Audience:
  - Prospecting: interest and in-market segments in observation; excludes Supp_Oct2025 Tier 1–8, the 4 remarketing lists, the Enrolled Suppression List and "Google - 2018 Leads Last 30 Days".
  - ASI: Customer Match lists only (Supp_2026 Tier 1–8); excludes the Enrolled Suppression List (user 2026-10-06; ASI not expanded).
  - Remarketing: the 4 remarketing lists (30 Days General AARP, Stage 1-4 of Website Funnel, Stages 4-5 of Customer Journey, YouTube 30 Days); excludes both Supp tier sets.

**Campaign exceptions**
- CO: `G_AARP_CO_[Geo]_45+_ALL_Prospecting` (age band and ALL replace the goal).
- PMAX: `G_AARP_PMAX_[Geo]_[ENROLL|RAQ]`: goal in capitals, no audience.
- DG: main pattern, Enroll_Prospecting only.

**Ad groups**
- Brand and NB: `[Type]_[State]` (full state name with spaces, e.g. Brand_New York) plus `[Type]_General`. ENT 16 (includes Washington DC), NENT 33; same set in every campaign of a type and geo.
- CO: `NB_Competitor_[Competitor]` (NB prefix, not CO); spaced names ("Met Life", "Zoc Doc"); codes EXM and PHM.
- DG: `Demand_Gen_Image`, `Demand_Gen_Video`.
- PMAX asset groups: `AARP_PMax-[Geo]`.

## Locations
- ENT: 14 states plus the Washington DC (Hagerstown MD) DMA: AL, CA, DE, FL, GA, LA, MD, MS, MT, NV, NY, PA, TX, UT. Excludes NENT states, ID, WV, USVI. CO and PMAX ENT target District of Columbia instead of the DMA.
- NENT: 34 states: AK, AZ, AR, CO, CT, HI, IL, IN, IA, KS, KY, ME, MA, MI, MN, MO, NE, NH, NJ, NM, NC, ND, OH, OK, OR, RI, SC, SD, TN, VT, VA, WA, WI, WY. Excludes ENT states, ID, WV, Washington DC.
- Method: location of presence (targeting and exclusion). Language: English (DG: all).

## Campaigns (total daily budget $8,802)
- 32 enabled. Daily budgets: Brand ×12 $5,507, NB ×12 $1,175, CO ×2 $250, PMAX ×4 $1,170, DG ×2 $350 shared.
- Bidding: Brand and PMAX RAQ maximize conversions; PMAX Enroll Target CPA ($165 ENT, $145 NENT); NB, CO and DG maximize clicks (CO $5 CPC cap).
- Labels: Brand and NB "Delta Dental - AARP SEM July 2026 Restructure"; CO "Conquesting 2026"; PMAX "10-29--2025_Pause" (yet Enabled). Both DG campaigns share "DD Demand Gen Shared Budget", so the $8,802 counts it twice (inference: $8,452 actual).

## Ad groups and keywords
- CO: 7 enabled competitor ad groups (Aetna, Aspen Dental, Cigna, Humana, Met Life, United Healthcare, Zoc Doc), 20 keyword texts; EXM and PHM paused. Broad, exact and phrase. "zocdoc dentist" is 62% of CO's September search-term cost; Brand_General holds the generic keyword "dental plans for over 65" (sqr-aug-sep).
- Final URL suffix: mcid=ps_ddins_00002&gclsrc=aw.ds&{_dsmrktparam}.

## Shared negative keyword lists (attached to enabled campaigns)
- Brand and NB: Master Blacklist, September Shooting, _Competitor Negatives, Spanish, Lorem Ipsum, their ENT or NENT Location Negatives; Brand adds _AARP and _Delta Dental Campaign Negatives, NB the two Traffic Negatives lists. PMAX: Master Blacklist, September Shooting, _Competitor Negatives, Location Negatives.
- Delta - General Negatives: Brand, NB and CO except G_AARP_NB_ENT_RAQ_ASI. CO only: Brand Keywords, NonBrand EX Keywords, its geo exclusion list.
- Full table with counts: export-1006.
- Not attached: Delta - Competitor Negatives (393), Delta - English Negatives for HM Campaigns (497), Delta - Brand & AARP Negatives (3). Shared brand list: "Delta Dental".
- Account-level placement exclusions: 12,332 websites, 2 YouTube channels.

## Performance snapshots and audits (file index)
- perf-90d: Jun 29 – Sep 27, 2026 prospecting performance.
- perf-30d: Sep 6 – Oct 5, 2026 callouts, recommendations, NB search terms findings.
- perf-sep: September 2026 report, Enroll, CO and DG, with August comparison.
- sqr-aug-sep: Aug vs Sep 2026 search terms by keyword group, theme and keyword, with callouts.
- structure: 2026-09-28 export structure. export-1006: 2026-10-06 campaign and shared list tables.
- dd-company-negs: proposed Company Negatives (2026-10-09).
- neg-audit: negative-keyword audit index. nb-lists: NB negative lists walkthrough (reviewed 2026-10-06). negative-lists: the list build doc.

## Built files
- Delta_SEM_Sept_2026_rev1.pptx (/mnt/project-files/presentations/): the client's Sept 2026 deck (/mnt/project-files/Delta Delta_SEM_Sept 2026.pptx; only slides 8–12 count, user 2026-10-07), slide 10's chart replaced. Script: build/Delta_SEM_Sept_2026_rev1.py with sept2026_slide10_chart.png.
- Search_Terms_Impr_Decline_Sep_vs_Aug_2026_rev1.xlsx (spreadsheets/): top 100 impression declines and climbs, Sep vs Aug 2026; script projects/work/scripts/sqr_month_impr_decline_rev1.py.

## Decisions and why
- 2026-10-06 (user's calls): doc built from the Oct 6 export, not the older structure doc; goal is AARP members only (the program is members-only). Rules provenance: log.
- 2026-10-08: the sqr runs before the General audit finishes (user's call, by sending the report).
- 2026-10-09: all earlier search terms pulls deleted; Untitled report (2).csv replaces them (user).

## Open questions
- Positive-keyword phase: "delta dental of [state]" searches cost $3,400 for 12 Enroll conversions ($283 each, Sep 5 – Oct 4); state negatives aren't allowed on Brand, so use keywords or bids.  
- The Enroll-judged sqr (the 90-day export; 8 blocked conversions was a small sample) needs a campaign-level pull with Enroll conversions; Untitled report (2).csv has no campaigns.
- sqr-aug-sep's four open items (ppo jump, AARP CPC, zocdoc and the insurers it alone reaches, over-65 keyword): causes and fixes undecided.
- Deck slide 10's chart shows about 1,000 September enrollments (inference, read off the image) vs perf-sep's 625 non-RAQ; which campaigns it counts is unconfirmed.
- Which NB fix first, structure and bidding or negatives? About 60% of NB search-term spend is relevant insurance searches that don't enroll (perf-30d).
- perf-30d recommendations 1–8 not actioned; 1 (Enroll-only goals) matters most.
- NB served "deltacare usa" and "deltadentalins com" despite carrying Delta Dental Traffic Negatives: check the account's copy and its attach date.
- Dental Care negatives (nb-lists): fold into General Negatives (audit paused at item 40 of 212) or a separate NB list; NB results not in rev3 yet (user, 2026-10-06).

## Next step
- Company list (user, 2026-10-09): 1,050 proposed rows drafted from the spend terms, unreviewed (dd-company-negs). Next: the item-by-item review, alphabetical, 5 per batch. Then the Enroll-judged sqr, the General audit at item 40 of 212 (aflac, Finding 3a), the Dental Care negatives' home and the NB results into rev3.

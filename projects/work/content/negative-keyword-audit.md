---
name: neg-audit
about: Source of truth for the negative-keyword audit: lists, constraints, legacy tracker, deferred and queued items
read-when: before any negative-keyword audit work
readonly: no
---
# Delta Dental – AARP: negative keyword list audit (master index)
Lists workbook: Delta_AARP_New_Negative_Lists_rev#.xlsx. rev2 delivered 2026-09-29: Index + one tab per finished list; columns Negative keyword / Match type (Broad, Phrase, Exact); keywords lowercase, no quotes or brackets. Omits General (in progress) and the Location Negatives queue. Next build: rev3. Audit workbook: Negative_Keyword_Audit_rev#.xlsx (rev1–rev2 delivered 2026-09-28). Retired (user, 2026-09-30); replaced by the lists workbook.

## New lists
| New list | Negative keywords | Applies to (draft; assignments decided at the end) | Status | Detail doc |
|---|---|---|---|---|
| AARP Traffic Negatives | 9 | NB, CO (never Brand) | Reviewed | this doc |
| Delta Dental Traffic Negatives | 15 | NB, CO (never Brand) | Reviewed | this doc |
| AARP Campaign Negatives | 72 | Brand | Reviewed | brand-aarp-list-walkthrough.md + variant-sweep.md |
| Delta Dental Campaign Negatives | 64 | Brand | Reviewed | dd-campaign-list-walkthrough.md + variant-sweep.md + Finding 1 |
| Competitor Negatives | 218 | Brand, NB (not CO) | Reviewed | competitor-org-merge-decisions.md |
| Conquesting Negatives | 206 | CO | Reviewed | conquesting-negatives.md |
| ENT Location Negatives | 41 | NENT campaigns | Reviewed | geo-location-lists.md |
| NENT Location Negatives | 76 | ENT campaigns | Reviewed | geo-location-lists.md |
| Spanish Negatives | 50 | Brand, NB (draft) | Reviewed; NB conflict check pending | spanish-list-walkthrough.md |
| Dental Care Negatives | 42 | NB (draft; or fold into General) | Reviewed | nb-list-walkthrough.md |
| Location Negatives | queue of 20 | Every campaign | Queue only; to be built and reviewed | competitor-org-merge-decisions.md |

**AARP Traffic Negatives (9)**
- a a r p (PHRASE)
- aarp (BROAD)
- horizon (BROAD)
- horizons (BROAD)
- myaarp (BROAD)
- patriot (BROAD)
- plan a (PHRASE): moved from General (older AARP plan name; can't go on Brand)
- plan b (PHRASE): as plan a
- securehorizons (BROAD)

**Delta Dental Traffic Negatives (15)**
- delia dental (PHRASE)
- delta (BROAD): added from legacy list 13; makes delta care/dental/dentist(s)/vision redundant (kept anyway)
- delta care (PHRASE)
- delta dental (BROAD)
- delta dentist (PHRASE)
- delta dentists (PHRASE)
- delta vision (PHRASE)
- deltacare (BROAD)
- deltadental (BROAD)
- deltadentalins (BROAD)
- deltavision (BROAD)
- dentegra (BROAD)
- hds dental (PHRASE)
- moda (BROAD)
- mysmilecoverage (BROAD)

**AARP Campaign Negatives (72)**
The 63 walkthrough keywords, plus horizon, horizons, patriot and securehorizons (all BROAD), plus aarp discount (PHRASE), aarp drivers (BROAD), aarp log in (PHRASE), aarp medicare plan (PHRASE) and aarp scams (BROAD).

**Delta Dental Campaign Negatives (64)**
57 from dd-campaign-list-walkthrough.md, plus delta dental dentist, delta dental discount plans and delta dental log in (all PHRASE) and delta dental medi cal (BROAD), plus hds dental (PHRASE), moda (BROAD) and mysmilecoverage (BROAD).

## Constraints for the campaign assignment step
- AARP Traffic Negatives' "aarp" (BROAD) blocks the CO keyword "zocdoc dentist aarp". Resolve on the negative side (e.g. not on CO, or a narrower AARP list for CO).
- Competitor Negatives blocks CO keywords through aetna, aspen dental, cigna, humana, met life and united. Resolved (user, 2026-09-29): CO gets Conquesting Negatives (Competitor Negatives minus CO conflicts) instead.
- General Negatives' "healthcare" (BROAD) blocks the CO United Healthcare ad group's keywords, and "life" (BROAD, pending regular review) likely blocks MetLife keywords such as "met life dental insurance" (inference; confirm with CO keyword export). Resolve on the negative side (e.g. a CO version of General without them).

## Legacy list tracker
| # | Legacy list | Keywords | Attached to | Status | Outcome |
|---|---|---|---|---|---|
| 1 | Delta - Brand Keywords (for NB, CO campaigns) | 256 | NB ×4, CO ×2 | Final | → Delta Dental Traffic + AARP Traffic Negatives |
| 2 | AARP Negatives | 15 | Brand ×4, NB ×4 | Final | → AARP Traffic + AARP Campaign Negatives |
| 4 | Delta - Competitor Negatives | 393 | Brand ×4, NB ×4 | Final | → Competitor Negatives (merged with #12) |
| 5 | Delta - Spanish Negatives for English Campaigns | 260 | Brand ×4, NB ×4 | Final | → Spanish Negatives (50 single words) |
| 6 | Delta - Non-Enterprise (ENT exclusions) | 125 | ENT campaigns | Final | → NENT Location Negatives (+14 entries) |
| 7 | Delta - General Negatives | 212 (209 unique; pasted 2026-09-29; the 2026-09-28 export showed 123) | Brand ×4, NB ×4, CO ×2 | In progress | Findings 1–2 done (items 1–39); paused at Finding 3a, item 40 of 212. See general-list-audit.md |
| 8 | Delta - NonBrand EX Keywords (for CO) | 95 | CO ×2 | Not started | |
| 9 | Lorem Ipsum | 92 | Brand ×4, NB ×4 | Not started | |
| 10 | Delta - Enterprise States (NENT exclusions) | 57 | NENT campaigns | Final | → ENT Location Negatives (+10 entries) |
| 12 | Competitor | 16 | Brand ×4, NB ×4 | Final | → Competitor Negatives (merged with #4) |
| 13 | Delta - Brand & AARP Negatives | 3 | NB ×4 | Final | aarp and delta dental already covered; "delta" added to DD Traffic Negatives |

Progress: 8 of 13 legacy lists final, 3 remaining, 2 deferred (below).

## DEFERRED to the very end of the project (user, 2026-09-28): DO NOT FORGET
Hidden from the active tracker; evaluate before the project closes.
| # | Legacy list | Keywords | Attached to |
|---|---|---|---|
| 3 | MS - Master Negative Keyword Blacklist | 2,494 | Brand ×4, NB ×4 |
| 11 | September Shooting | 20 | Brand ×4, NB ×4 |

## Search terms review, 2026-10-06 (Enroll campaigns, Sep 5 – Oct 4 report)
Decided by user; apply in rev3. Enroll cost blocked over 30 days, all 0 Enroll conversions.
- Delta Dental Campaign Negatives: add deltadentalcoversme (BROAD), $233. Probably Northeast Delta Dental's individual-plan site (unconfirmed).
- Delta Dental Traffic Negatives: add deltadentalcoversme (BROAD); "deltadental" and "delta" miss the merged word.
- Delta Dental Campaign Negatives: replace "delta dental premier" (PHRASE) with premier (BROAD), +$190. PPO Plus Premier is a non-AARP group plan.
- Delta Dental Campaign Negatives: replace "delta dental providers" (PHRASE) with providers (BROAD), +$133. Some may be network-checking shoppers.
- General Negatives: near me (PHRASE), queued below.
- NB search terms (all 12 NB campaigns, 2026-10-06): reviewed additions in nb-list-walkthrough.md: Delta Dental Traffic +63, AARP Traffic +4, Competitor +12 (Conquesting +12). Not yet in rev3's agreed changes (user).

## Queued candidates for other list audits
For Delta - General Negatives (general-list-audit.md; paused at Finding 3a, item 40 of 212):
- dentists washington
- minnesota select dental providers
- medigap (BROAD), medi gap (PHRASE), medlearn (BROAD), med learn (PHRASE)
- indemnity dental insurance
- obama dental plans
- dds dental insurance
- cobra dental / cobra dental insurance
- medi medi dental coverage
- canadian dental insurance plans
- near me (PHRASE): approved 2026-10-06 from search terms data ($128 Enroll, 0 conversions). Covers "dentist near me" (EXACT, item 145). Conflicts with "aarp near me" on the revisit-later list.
- provincial dental coverage

Note: General also reaches Brand; BROAD "medigap" would block "does medigap cover dental", so consider PHRASE.
Note: negating "indemnity" (BROAD) makes "indemnity dental insurance" redundant; negating "gap" (BROAD) makes "medi gap" (PHRASE) redundant ("medigap" still needed).

For Spanish Negatives:
- estetica, estética: added (BROAD)
- clinica dental san miguel: covered by "clinica"

## Revisit later (removed or set aside)
- aarp membership, aarp near me, join aarp (EXACT): removed from AARP Campaign Negatives.
- dental dental ins (EXACT): typo.
- dental insurance for seniors over 65 / dental plans for over 65: keyword evaluation phase.
- delta dental of (PHRASE).
- The 7 dd exact-match heads: recheck with search terms data.
- enrollment: $230 Enroll, 0 conversions (Sep 5 – Oct 4). Held: may be buying intent on Enroll campaigns; recheck with 90-day data.
- Company list removals: 1 day, 1day, premier dental insurance, va dental, clark howard, dr bell, dr santos, upei, serena ta, sowatsky, star dental, tyson foods.
- Legacy competitor entries set aside: social security dental coverage, delaware dental plans, clearwater dental insurance, dakota dental insurance, broward dental insurance, deltacare (removed; AARP plan option).
- Variants skipped as low volume: see variant-sweep.md, competitor-org-merge-decisions.md (dental 50 plus, renew smiles, river tree dental, seledent, smilemax, send info kit).
- Untargeted places for a location list: idaho, west virginia, wv, puerto rico, virgin islands, usvi (+ legacy forms: ID, Ida., W. Va, W. Vir., W. Virg., PR, P.R., VI, U.S.V.I.).
- Skipped legacy state abbreviations: see geo-location-lists.md.
- Spanish legacy "Missing Keywords" (EXACT + PHRASE): placeholder, removed.
- General Negatives, not negated (2026-09-29): 866 261 4275, aarp dental insurance reviews consumer reports, complete, does medicare cover dental, join today, medicare part c dental coverage, rate, rated, rates, rating, ratings, supplemental.

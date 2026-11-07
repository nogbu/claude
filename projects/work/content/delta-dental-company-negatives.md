---
name: dd-company-negs
about: Delta Dental Company Negatives: proposed list, method, evidence and review decisions
read-when: before any Delta Dental company or competitor negatives work
readonly: no
---
# Delta Dental Company Negatives (proposed 2026-10-09)
A negative keyword list blocking every company, business, organization and product name (other than Delta Dental, its affiliates and AARP) found in the search terms, each with the proper name of the organization it blocks (user's ask, 2026-10-09). Companion to the delta-dental client doc.

Data: projects/work/products/delta-dental/build/Delta_Company_Negatives_data.csv (one row per negative; columns: negative_keyword, match, company, what_it_is, relation, confidence, source_url, rec, reason, verify_note, seen, co_conflict, pos_conflicts, in_lists, terms/cost/clicks/impr/All conv. blocked, groups, span). Status: proposed, unreviewed, not applied. No spreadsheet built yet.

## Method (2026-10-09)
1. Source: Untitled report (2).csv, Aug 1 – Oct 7, 2026 search terms (50,493 unique terms, $327,869). Scope: the 10,144 terms with spend, which carry all the cost (user's pick, 2026-10-09).
2. Extraction: 8 agents each scanned 1,268 terms for organization names, excluding Delta Dental, its affiliates, AARP and AARP plan names. 1,033 distinct spans.
3. Research: 8 agents named each organization and proposed negatives by the kw-review rules; 6 more agents searched for sources for the 565 left unsourced. The web search cap (200 per turn) left some unsourced.
4. Corrections: Delta names found in research (DDIC, Delta Vision, LifePerks, Delta misspellings, dentalins) moved to Exclude: client; "affordable dentures" moved to Don't negate (blocks the NB keyword "affordable dentures for seniors").
5. Evidence (scratch evidence.py): each negative matched against all 50,493 terms (Broad, Phrase, Exact; no close variants), the enabled positive keywords of the 2026-10-06 export and the rev2 lists. Keyword groups (Brand, NB, CO) come from mapping Search keyword to the export's keywords.

## Result (Measured, 2026-10-09)
- 1,050 rows: 880 Negate (698 companies), 123 Don't negate, 26 Exclude: client, 21 Not a name.
- Negate rows by relation: competitor insurer 307, dental provider 262, employer/union group plan 92, government program 66, dental discount plan 38, other business 36, website 33, health system 25, association 20.
- Confidence of Negate rows: 400 C, 262 L, 218 U; 648 have a source URL.
- Together the Negate rows would have blocked 11,528 terms, $13,616 (4.2% of cost). By keyword group (a term can sit in several, inference): Brand 1,339 terms / $5,091; NB 3,111 / $5,433; CO 9,037 / $10,602. Conversions are All conv. only, so blocked conversions aren't Enroll-judged.
- No Negate row conflicts with an enabled Brand or NB keyword. 67 rows are CO-target name variants (co_conflict = yes): fine on Brand and NB, never on CO. 125 rows are already in a rev2 list. 23 rows match no term (added spellings).
- Biggest Don't negate calls: medicare ($13,492; 50+ shoppers), medicare advantage ($797), bare "va" ($652; also Virginia), invisalign ($164), medicare supplement ($139), marketplace ($127), premier dental ($125; may be Delta Dental Premier).

## Open (2026-10-09)
- Item-by-item review (Product rule): not started; alphabetical, 5 per batch.
- Which campaigns get the list (Brand and NB, with CO taking a version minus the CO targets, like Conquesting Negatives), and whether it merges into Competitor Negatives.
- 218 Negate rows are U and 232 have no source.
- Microsoft and Premera searchers may be Delta members (Microsoft's dental moved to Delta Dental); employer plan names stay Negate as group-member lookups.

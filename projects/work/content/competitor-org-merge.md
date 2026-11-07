---
name: org-merge
about: Competitor merge method and legacy dispositions
read-when: only for how the competitor merge was done
readonly: yes
---
# Company/org negatives: merge of "Competitor" (16) and "Delta - Competitor Negatives" (393)
Companion to negative-keyword-audit.md. Built 2026-09-28.

Purpose (user): company and organization names other than AARP and dd, plus brand terms associated with them (products, plans, sites). Primarily competitors, but any organization we want to block.

Method: the 393 legacy entries are consolidated to one root per organization. Every legacy entry is either covered by a root or has a disposition below; 0 are uncovered.

Legacy "Delta - Competitor Negatives" is on Brand ×4 and NB ×4.

Conflict check:
- Brand and NB: 0 conflicts.
- CO: aetna, aspen dental, cigna, humana, met life and united block 18 CO keywords. This is a constraint for the campaign assignment step.
- "united" (BROAD, already reviewed) also blocks "dental insurance united states".

Final list (218) and all review decisions: competitor-org-merge-decisions.md.

## Already reviewed (from Competitor)
- 1 day (PHRASE)
- 1day (BROAD)
- a1 (BROAD)
- aaa (BROAD)
- access dental (PHRASE)
- advent (BROAD)
- aetna (BROAD)
- blue cross (BROAD)
- blue shield (BROAD)
- kaiser (BROAD)
- metlife (BROAD)
- united (BROAD)
- unitedhealthcare (BROAD)

## Legacy entries not carried into the merged list
| Legacy keyword | Disposition | Reason |
|---|---|---|
| broward dental insurance | FLAG | Broward County, FL (ENT). Blocks Broward residents searching for dental insurance. |
| canadian dental insurance plans | GENERAL | Country, not an organization. |
| clearwater dental insurance | FLAG | Clearwater is a Florida city (ENT). Blocks the exact search from Clearwater residents. |
| clinica dental san miguel | SPANISH | Spanish-language dental clinic search; belongs with the Spanish list review. |
| cobra dental | GENERAL | COBRA continuation coverage, not an organization. |
| cobra dental insurance | GENERAL | COBRA continuation coverage, not an organization. |
| dakota dental insurance | FLAG | Could mean North/South Dakota (both NENT states). |
| dds dental insurance | GENERAL | "DDS" is a dental degree, not an organization. |
| delaware dental plans | FLAG | Delaware is an ENT state. As a phrase it blocks Delaware residents searching for dental plans. |
| deltacare | REMOVE | AARP plan option (DeltaCare USA Essential); must not be blocked in Brand. Already on Delta Dental Traffic Negatives for NB/CO. |
| dentegra | MOVED | Already moved to Delta Dental Traffic Negatives (dd affiliate). |
| indemnity dental insurance | GENERAL | Plan type, not an organization. |
| medi medi dental coverage | GENERAL | Medi-Medi = dual Medicare/Medi-Cal eligibility, a program not an organization. |
| medigap | GENERAL | Already queued for General Negatives. |
| obama dental plans | GENERAL | ACA/marketplace reference, not an organization. |
| parse | FLAG | Unidentified; not a recognizable organization. |
| provincial dental coverage | GENERAL | Canadian provinces, not an organization. |
| social security dental coverage | FLAG | Not an organization. Searcher is likely a senior looking for dental coverage, which may be a prospect. |

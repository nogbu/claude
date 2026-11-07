---
name: conquesting
about: Conquesting Negatives (206): Competitor Negatives minus the listed exclusions
read-when: before any Conquesting Negatives work, and whenever Competitor Negatives changes
readonly: no
rules: recompute the list whenever Competitor Negatives changes. Name variants of a targeted competitor are excluded (the CO ad groups want those searches); separately branded sub-brands stay as negatives
---
# Conquesting Negatives (created and reviewed 2026-09-29): 206 negatives
Companion to negative-keyword-audit.md and competitor-org-merge-decisions.md.

Definition (user, 2026-09-29): every negative in Competitor Negatives, minus any negative that conflicts with the CO (conquesting) campaigns. The CO campaigns target specific competitors; the targeted competitors are the names of the active CO ad groups:
Aetna, Aspen Dental, Cigna, Humana, MetLife, United Healthcare, ZocDoc. (EXM and PHM ad groups are paused.)

Applies to: CO ×2 (in place of Competitor Negatives). Competitor Negatives stays the list for Brand and NB.

## Excluded: conflicts with CO (8)
| Negative keyword | Match | Targeted competitor | Why it conflicts |
|---|---|---|---|
| aetna | BROAD | Aetna | Blocks the Aetna ad group's keywords |
| aspen dental | PHRASE | Aspen Dental | Blocks the Aspen Dental ad group's keywords |
| cigna | BROAD | Cigna | Blocks the Cigna ad group's keywords |
| humana | BROAD | Humana | Blocks the Humana ad group's keywords |
| met life | PHRASE | MetLife | Blocks the MetLife ad group's keywords |
| metlife | BROAD | MetLife | Competitor's own name; blocks "metlife dental" conquest searches |
| united | BROAD | United Healthcare | Blocks the United Healthcare ad group's keywords |
| unitedhealthcare | BROAD | United Healthcare | Competitor's own name; blocks conquest searches |

## Reviewed: other brand terms of the targeted competitors (8; user accepted all recommendations)
| # | Negative keyword | Match | Company | Decision |
|---|---|---|---|---|
| 1 | golden rule | PHRASE | Golden Rule Insurance (UnitedHealthcare) | Negate |
| 2 | humanadental | BROAD | Humana | Excluded |
| 3 | humanna | BROAD | Humana (misspelling) | Excluded |
| 4 | met dental | PHRASE | MetLife (short form) | Excluded |
| 5 | ncd dental | PHRASE | NCD by MetLife | Negate |
| 6 | safeguard dental | PHRASE | SafeGuard (MetLife dental HMO) | Negate |
| 7 | surebridge | BROAD | SureBridge (UnitedHealthcare) | Negate |
| 8 | uhc | BROAD | UnitedHealthcare | Excluded |

ZocDoc: no Competitor Negatives entry conflicts.

Size: 206 (Competitor Negatives 218 minus 12 exclusions: aetna, aspen dental, cigna, humana, humanadental, humanna, met dental, met life, metlife, uhc, united, unitedhealthcare).

Still to do: re-check against the full CO keyword export (the earlier conflict check found aetna, aspen dental, cigna, humana, met life and united blocking 18 CO keywords).

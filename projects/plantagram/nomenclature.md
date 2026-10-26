---
about: Anthurium cross notation, collector abbreviations and common names, with sources (read 2026-10-14)
read-when: when the prompt hook says a name matched no row, or before reading or writing a species or cross
readonly: no
---
# learnings/nomenclature

Sources (read 2026-10-14): [Anthurium Collector's Guide](https://anthuriumcollectorsguide.com/) (ACG), [GR Anthuriums abbreviations](https://granthuriums.com/blogs/general-educational/list-of-common-abbreviations) (GRA). Both are hobbyist glossaries; meanings can vary between communities.

## Cross notation (learned 2026-10-14)

- **A x B**: seed (mother) parent first, pollen parent second (ACG; aroid convention). Order matters: RVDP x Ace of Spades and Ace of Spades x RVDP are different crosses, so my plants.md keeps them as separate rows (my pick 2026-10-14).
- **Parentheses**: nest multi-generation crosses, e.g. Mr. Worldwide x (Carlablackiae x Papillilaminum) (ACG).
- **/**: ACG says it joins alternate names for one thing ("Pap / Papi"), not a cross. In my plants.md it also marks a parent that is itself a cross or line, e.g. "RLFS/Carlablackiae x Dark Phoenix/Dressleri" and "Fort Sherman/self x Carlablackiae RA18" (inference from the table). Read each one in context; sources and my table disagree.
- **x self, selfed**: pollinated with its own pollen or a clone's; offspring are new seedlings, not the mother clone (ACG).
- **F1, F2…**: generations after crossing two different parents. **S1, S2…**: generations after selfing. A cutting keeps its generation (ACG).
- **aff.**: looks like the named species but isn't confirmed; "besseae aff." is the usual label for besseae-like plants (ACG).
- **sp. nov.**: undescribed species placeholder (ACG).
- **df / DF**: usually "dark form" (Forgetii df, AoS df). "sp. nov. DF" is a Dewey Fisk placeholder species; DF can also mean the Delta Force hybrid (ACG, GRA).
- **TC**: tissue culture; **NOID**: no ID (ACG).

## Clone codes and breeder prefixes (learned 2026-10-14)

- **RA1, RA18…**: Rory Antolak numbered clones (ACG, GRA).
- **OG1, OG5…**: Scott Cohen carlablackiae clones (ACG).
- **Wu1–Wu9**: WuHoo Tropicals (Bryan Wu) clones, e.g. pap Wu1 (ACG).
- **SC1…**: Scott Cohen papillilaminum clones; **PM1–PM7**: Paul Marcellini (Understory Oasis) carla/kuna mothers (ACG).
- **GPH001…**: Juan (@GayPlantHeaux) carlablackiae mothers (GRA).
- **FS**: Fort Sherman, a wild papillilaminum clone from Panama (Jay Vannini) (ACG, GRA).
- **RL**: Ralph Lynam, a papillilaminum clone from Jay Vannini (GRA).
- **RG**: Río Guanche dressleri ecotype, or Ree Gardens (GRA).
- **JV**: Jay Vannini. **Doc Block**: Dr. Jeffrey Block. **NSE**: NSE Tropicals (Enid Offolter). **SKG**: Silver Krome Gardens. **HU**: Haji Ulih, Indonesian breeder of KOS and DP. **FTG**: Fairchild Tropical Garden. **Novelty G**: Hawaiian Novelty Greens (ACG, GRA).

## Abbreviations and common names (learned 2026-10-14)

| Short | Means | Source |
| :---- | :---- | :---- |
| AoS / AOS | Ace of Spades (a hybrid; green and dark forms) | ACG, GRA |
| KOS / HU | King of Spades (Haji Ulih) | ACG, GRA |
| KOC | King of Clarinervium | GRA |
| DP | Dark Phoenix (Indonesian hybrid) | ACG, GRA |
| RVDP | Red Vein Dark Phoenix (Siam Flora, Thailand) | ACG, GRA |
| RLFS (FSRL, RL x FS) | Fort Sherman x Ralph Lynam papillilaminum cross | GRA; my words 2026-10-14 |
| BVEP | Black Velvet Eastern Panama, now A. antolakii | ACG, GRA |
| BVIT, IT | Black Velvet Indo Type (informal) | ACG |
| RC | Red Crystallinum (trade name) | ACG |
| HURC | KOS x Red Crystallinum | ACG |
| BWM | Black Widow x Michelle | ACG |
| QOH | Queen of Hearts (SKG tissue-culture line) | ACG |
| CP | Circus Peanuts | ACG |
| EPP / RS | Red Spider (pap x magnificum selection) | ACG |
| TALL | Tim Anderson Long Leaf | ACG |
| Pap, Papi | papillilaminum ("butterfly anthurium") | ACG |
| Carla | carlablackiae | ACG |
| Crys | crystallinum | ACG |
| Mag | magnificum | my words 2026-10-14 |
| Kuna | early unnumbered RA-era carla clone | ACG |
| — | warocqueanum: Queen Anthurium; veitchii: King Anthurium | Wikipedia, plant guides |

## Matching my shorthand to plants.md (learned 2026-10-14)

- plant.py matches my shorthand itself (its find() docstring): it expands each Short in the table above, then drops any unnumbered prefix under Clone codes and breeder prefixes above from the start of each part of a row's cross, and takes a row only when exactly one matches, which needs no question ("dp x mag" is Tomax; "kos x michelle" is Invader Zim, King of Spades x Doc Block Michelle, since Michelle is DocBlock® Michelle® and there is no other; my words 2026-10-14).
- When it finds no single row, the hook's note says what to do, following CLAUDE.md, Questions. A reversed cross is another plant, never a match ("rvdp x aos" was a new plant, not Ace of Spades x RVDP; Cross notation above) (2026-10-14).

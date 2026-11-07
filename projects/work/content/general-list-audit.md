---
name: general-audit
about: General Negatives audit (in progress)
read-when: before any General Negatives work
readonly: no
rules: audit each keyword against the three purpose criteria, flag conflicts with other lists and keywords, and simplify where possible. Criterion 3 fails when a keyword would block prospect searches in any Search campaign (Brand, NB or CO)
---
# General Negatives: audit (in progress, 2026-09-29)
Companion to negative-keyword-audit.md. Legacy list #7 "Delta - General Negatives", pasted by user 2026-09-29: 212 entries, 209 unique (customer service, login and billing each twice).

Purpose (user): negatives that (1) fit no existing list, (2) don't warrant a new list, (3) apply to every campaign.

Notes:
- Conflict check against Brand, NB and CO keywords pending (needs the keyword export).
- If General keeps customer-service words (login, phone number, customer service, sign in, renew...), matching AARP/DD Campaign Negatives entries become redundant on Brand.

Decisions log (user, 2026-09-29):
- Finding 1 items 1–5 done (see Decision column). sign/signing/signed were meant to block sign-in; the variants are added below.
- health, healthcare, medical kept: health/medical insurance volume far outweighs dental-health searches. Constraint: "healthcare" blocks the CO United Healthcare keywords, so General can't go on CO as-is.

Re-evaluation (2026-09-29): org/site/website forms are negated; without them Brand would pick up "aarp org"/"aarp website" plus any AARP product that AARP Campaign Negatives covers only as PHRASE/EXACT (medicare, health insurance, benefits...).

Sign-in variants (user, 2026-09-29): all 5 added (rows 213–217). Already on the list: sign in (PHRASE), signin (BROAD).

Proposed simplifications:
- 26 cosmetic entries → cosmetic (BROAD).
- Pay-bill phrases → bill (BROAD); billing address/department → billing (BROAD).
- free dental care / free dental work → free dental (PHRASE).
- Duplicates: negate customer service, login and billing once each as BROAD; drop the PHRASE and EXACT copies.
- 7 Chinese/Korean entries → 保险 (BROAD, Chinese "insurance") and 보험 (BROAD, Korean "insurance"), proposed for the language list; moving them means renaming Spanish Negatives (e.g. Non-English Negatives).

Research (2026-09-29):
- 800 422 4234: Delta Dental customer service (DeltaCare USA). https://www1.deltadentalins.com/about/contact.html
- 866 261 4275: AARP Program at Delta Dental contact line. https://www1.deltadentalins.com/aarp/contact.html
- ebilling nedelta com: Northeast Delta Dental eBill center (dd member company). https://ebilling.nedelta.com/
- delta dental institute: Delta Dental's oral health policy institute. https://www.deltadentalinstitute.com/
- sachem: Sachem Dental Group, Long Island NY (also a NY school district). https://sachemdental.com/
- stony: Stony Brook University School of Dental Medicine / Stony Brook Dental Group, NY. https://dentistry.stonybrookmedicine.edu/dentalcarecenter
- ub dental: University at Buffalo School of Dental Medicine clinics. https://dental.buffalo.edu/patients.html
- tufts: Tufts Health Plan (Medicare/dental plans), Tufts dental school. https://tuftshealthplan.com/
- utf insurance: likely misspelled UFT (United Federation of Teachers Welfare Fund); "uft dental" is on Competitor Negatives. https://www.uft.org/your-benefits/health-benefits/dental
- dixie / dixieland: several practices (Dixie Dental Center, Dixieland Dental AL), Winn-Dixie, Dixie school district benefits. https://www.dixiedental.com/

| # | Negative keyword | Match | Finding | Note | Decision |
|---|---|---|---|---|---|
| 1 | 866 261 4275 | EXACT | Finding 1 | AARP Program at Delta Dental contact line; members calling for service likely outnumber prospects calling to enroll (inference) | Don't negate (revisit later) |
| 2 | aarp dental insurance reviews consumer reports | PHRASE | Finding 1 | prospects comparing plans; matches the Brand keyword theme | Don't negate (revisit later) |
| 3 | complete | BROAD | Finding 1 | blocks "complete dental coverage for seniors"; little irrelevant volume (inference) | Don't negate (revisit later) |
| 4 | does medicare cover dental | EXACT | Finding 1 | blocks only this prospect question | Don't negate (revisit later) |
| 5 | health | BROAD | Finding 1 | general health insurance searches far outnumber "dental health insurance" (inference) | Negate (re-check with search terms) |
| 6 | healthcare | BROAD | Finding 1 | general healthcare searches far outnumber dental ones (inference); blocks the CO United Healthcare ad group's keywords | Negate (re-check with search terms) |
| 7 | join today | PHRASE | Finding 1 | enrollment intent | Don't negate (revisit later) |
| 8 | medi care | PHRASE | Finding 1 | misspelled general Medicare shopping far outnumbers "medi care dental" (inference) | Negate |
| 9 | medical | BROAD | Finding 1 | general medical insurance searches far outnumber "medical and dental insurance" (inference) | Negate (re-check with search terms) |
| 10 | medicare part c dental coverage | EXACT | Finding 1 | as row 4 | Don't negate (revisit later) |
| 11 | no insurance | PHRASE | Finding 1 | people looking for care now ("dentist no insurance near me") far outnumber coverage shoppers (inference) | Negate |
| 12 | org | BROAD | Finding 1 | without it, Brand picks up "aarp org/site/website" + any AARP product that AARP Campaign Negatives covers only as PHRASE/EXACT | Negate |
| 13 | paid | BROAD | Finding 1 | negated at user's confirmed choice, although it blocks shopper wording such as "dental insurance that pays 100%" | Negate |
| 14 | pay | BROAD | Finding 1 | bill-payment searches far outnumber shopper wording (inference) | Negate |
| 15 | paying | BROAD | Finding 1 | as row 14 | Negate |
| 16 | pays | BROAD | Finding 1 | negated at user's confirmed choice, although it blocks shopper wording such as "dental insurance that pays 100%" | Negate |
| 17 | rate | BROAD | Finding 1 | irrelevant rate searches that could trigger our ads are already blocked by "health" | Don't negate (revisit later) |
| 18 | rated | BROAD | Finding 1 | as row 17 | Don't negate (revisit later) |
| 19 | rates | BROAD | Finding 1 | as row 17 | Don't negate (revisit later) |
| 20 | rating | BROAD | Finding 1 | as row 17 | Don't negate (revisit later) |
| 21 | ratings | BROAD | Finding 1 | as row 17 | Don't negate (revisit later) |
| 22 | secondary insurance | PHRASE | Finding 1 | secondary medical insurance searches far outnumber secondary dental (inference) | Negate |
| 23 | sign | BROAD | Finding 1 | meant to block sign-in searches; replaced by the sign-in variants (rows 213–217) | Don't negate (no revisit) |
| 24 | signed | BROAD | Finding 1 | meant to block sign-in searches; replaced by the sign-in variants (rows 213–217) | Don't negate (no revisit) |
| 25 | signing | BROAD | Finding 1 | as row 23 | Don't negate (no revisit) |
| 26 | site | BROAD | Finding 1 | as row 12 | Negate |
| 27 | sites | BROAD | Finding 1 | as row 12 | Negate |
| 28 | supplement | BROAD | Finding 1 | Medicare Supplement shopping far outnumbers "medicare supplement dental" (inference) | Negate (reopened; was revisit later) |
| 29 | supplemental | BROAD | Finding 1 | "supplemental dental insurance" is a high-volume prospect term (inference) | Don't negate (revisit later) |
| 30 | supplemented | BROAD | Finding 1 | mostly dietary-supplement searches (inference) | Negate |
| 31 | supplementing | BROAD | Finding 1 | mostly dietary-supplement searches (inference) | Negate |
| 32 | supplements | BROAD | Finding 1 | mostly dietary-supplement searches (inference) | Negate |
| 33 | vision | BROAD | Finding 1 | vision insurance and eye care searches far outnumber "dental and vision" shoppers (inference) | Negate |
| 34 | website | BROAD | Finding 1 | as row 12 | Negate |
| 35 | websites | BROAD | Finding 1 | as row 12 | Negate |
| 36 | without insurance | PHRASE | Finding 1 | as row 11 | Negate |
| 37 | aarp membership | EXACT | Finding 2 | user removed this from AARP Campaign Negatives (revisit later) on 2026-09-28 | Don't negate (revisit later) |
| 38 | plan a | PHRASE | Finding 2 | older AARP plan names (PPO Plan A / Plan B) must never be blocked on Brand | Move to AARP Traffic Negatives (NB, CO only) |
| 39 | plan b | PHRASE | Finding 2 | as row 38 | Move to AARP Traffic Negatives (NB, CO only) |
| 40 | aflac | BROAD | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 41 | ambetter | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 42 | american dental association | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 43 | capital one | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 44 | dental now insurance reviews | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 45 | dental plans com reviews | PHRASE | Finding 3a | Competitor bucket (DentalPlans.com); may not match "dentalplans.com" | Pending |
| 46 | dentalnow com reviews | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 47 | dentalnow reviews | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 48 | dentalplans com reviews | PHRASE | Finding 3a | Competitor bucket (DentalPlans.com); may not match "dentalplans.com" | Pending |
| 49 | dixie | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 50 | dixieland | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 51 | frontier communications | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 52 | physicians dental insurance reviews | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 53 | physicians mutual | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 54 | sachem | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 55 | stony | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 56 | tufts | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 57 | ub dental | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 58 | united concordia | PHRASE | Finding 3a | already covered by Competitor Negatives | Pending |
| 59 | utf insurance | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 60 | vsp | BROAD | Finding 3a | already covered by Competitor Negatives | Pending |
| 61 | walmart | PHRASE | Finding 3a | company/org name: Competitor Negatives bucket | Pending |
| 62 | 800 422 4234 | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 63 | aarp delta dental pay bill | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 64 | delta dental institute | PHRASE | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 65 | delta dental insurance pay bill | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 66 | delta dental of california pay bill | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 67 | delta dental pay bill | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 68 | delta dental pay bill online | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 69 | deltadentalins com pay bill | EXACT | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 70 | ebilling nedelta com | PHRASE | Finding 3b | dd term: Delta Dental lists bucket | Pending |
| 71 | aarp medicare supplement dental discount | EXACT | Finding 3c | AARP term: AARP lists bucket | Pending |
| 72 | myaarpdentalplan com my account | EXACT | Finding 3c | AARP term: AARP lists bucket | Pending |
| 73 | 法拉 盛 牙科 保险 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 74 | 牙医 保险 一 亩 三 分 地 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 75 | 第 一 保健 牙科 保险 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 76 | 美国 植 牙 保险 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 77 | 델타 덴탈 보험 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 78 | 미국 임플란트 보험 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 79 | 치과 보험 임플란트 | EXACT | Finding 3d | non-English: language bucket (Spanish list) | Pending |
| 80 | shooting | PHRASE | Finding 3e | overlaps deferred legacy list September Shooting | Pending |
| 81 | affordable cosmetic dentistry near me | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 82 | best cosmetic dental insurance | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 83 | bill pay | EXACT | Finding 4 | covered by "bill" BROAD | Pending |
| 84 | billing address | EXACT | Finding 4 | covered by "billing" BROAD | Pending |
| 85 | billing department | EXACT | Finding 4 | covered by "billing" BROAD | Pending |
| 86 | can i pay my bill online | EXACT | Finding 4 | covered by "bill" BROAD | Pending |
| 87 | cosmetic coverage | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 88 | cosmetic dental | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 89 | cosmetic dental insurance | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 90 | cosmetic dental insurance plans | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 91 | cosmetic dental plans | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 92 | cosmetic dental procedures cost | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 93 | cosmetic dentist in arizona | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 94 | cosmetic dentistry conroe tx | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 95 | cosmetic dentistry richmond va | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 96 | cosmetic dentistry san francisco | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 97 | cost of cosmetic dentistry | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 98 | dental cosmetic insurance | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 99 | dental insurance for cosmetic surgery | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 100 | dental insurance for cosmetic work | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 101 | dental insurance that covers cosmetic dentistry | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 102 | does cover cosmetic dentistry | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 103 | free dental care | PHRASE | Finding 4 | covered by "free dental" PHRASE | Pending |
| 104 | free dental work | PHRASE | Finding 4 | covered by "free dental" PHRASE | Pending |
| 105 | full coverage cosmetic dental insurance | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 106 | help with dental bill | PHRASE | Finding 4 | covered by "bill" BROAD | Pending |
| 107 | most dental insurance covers cosmetic improvements | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 108 | pay bill | PHRASE | Finding 4 | covered by "bill" BROAD | Pending |
| 109 | pay my bill | EXACT | Finding 4 | covered by "bill" BROAD | Pending |
| 110 | pay my bill online | EXACT | Finding 4 | covered by "bill" BROAD | Pending |
| 111 | pittsburgh cosmetic dentistry | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 112 | supplemental cosmetic dental insurance | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 113 | what insurance covers cosmetic dentistry | PHRASE | Finding 4 | covered by one "cosmetic" BROAD | Pending |
| 114 | variant | BROAD | Finding 5 | no clear purpose | Pending |
| 115 | variants | BROAD | Finding 5 | no clear purpose | Pending |
| 116 | $399 dental implants | EXACT | Meets all three criteria | | Pending |
| 117 | 2020 | BROAD | Meets all three criteria | | Pending |
| 118 | 2021 | BROAD | Meets all three criteria | | Pending |
| 119 | 2022 | BROAD | Meets all three criteria | | Pending |
| 120 | 2023 | BROAD | Meets all three criteria | | Pending |
| 121 | 2024 | BROAD | Meets all three criteria | | Pending |
| 122 | 2025 | BROAD | Meets all three criteria | | Pending |
| 123 | anxiety | PHRASE | Meets all three criteria | | Pending |
| 124 | bill | BROAD | Meets all three criteria | | Pending |
| 125 | billed | BROAD | Meets all three criteria | | Pending |
| 126 | billing | EXACT | Meets all three criteria | | Pending |
| 127 | billing | BROAD | Meets all three criteria | | Pending |
| 128 | bills | BROAD | Meets all three criteria | | Pending |
| 129 | career | BROAD | Meets all three criteria | | Pending |
| 130 | careers | PHRASE | Meets all three criteria | | Pending |
| 131 | clinic | PHRASE | Meets all three criteria | | Pending |
| 132 | clinics | PHRASE | Meets all three criteria | | Pending |
| 133 | college | PHRASE | Meets all three criteria | | Pending |
| 134 | colleges | PHRASE | Meets all three criteria | | Pending |
| 135 | credit card | PHRASE | Meets all three criteria | | Pending |
| 136 | credit cards | PHRASE | Meets all three criteria | | Pending |
| 137 | customer service | BROAD | Meets all three criteria | | Pending |
| 138 | customer service | PHRASE | Meets all three criteria | | Pending |
| 139 | customer support | PHRASE | Meets all three criteria | | Pending |
| 140 | dental appointment | EXACT | Meets all three criteria | | Pending |
| 141 | dental hospital nearby | EXACT | Meets all three criteria | | Pending |
| 142 | dental specialist | EXACT | Meets all three criteria | | Pending |
| 143 | dental work done free | PHRASE | Meets all three criteria | | Pending |
| 144 | dentist near | EXACT | Meets all three criteria | | Pending |
| 145 | dentist near me | EXACT | Meets all three criteria | | Pending |
| 146 | directories | BROAD | Meets all three criteria | | Pending |
| 147 | directory | BROAD | Meets all three criteria | | Pending |
| 148 | dmv | PHRASE | Meets all three criteria | | Pending |
| 149 | dog | PHRASE | Meets all three criteria | | Pending |
| 150 | dogs | PHRASE | Meets all three criteria | | Pending |
| 151 | eye | BROAD | Meets all three criteria | | Pending |
| 152 | eyes | BROAD | Meets all three criteria | | Pending |
| 153 | flight | BROAD | Meets all three criteria | | Pending |
| 154 | flights | BROAD | Meets all three criteria | | Pending |
| 155 | free dental | PHRASE | Meets all three criteria | | Pending |
| 156 | gap | BROAD | Meets all three criteria | | Pending |
| 157 | going out of business | PHRASE | Meets all three criteria | | Pending |
| 158 | hygienist | PHRASE | Meets all three criteria | | Pending |
| 159 | hygienists | PHRASE | Meets all three criteria | | Pending |
| 160 | indemnity | BROAD | Meets all three criteria | | Pending |
| 161 | life | BROAD | Meets all three criteria | | Pending |
| 162 | loan | PHRASE | Meets all three criteria | | Pending |
| 163 | loans | PHRASE | Meets all three criteria | | Pending |
| 164 | log | BROAD | Meets all three criteria | | Pending |
| 165 | logged | BROAD | Meets all three criteria | | Pending |
| 166 | logging | BROAD | Meets all three criteria | | Pending |
| 167 | login | PHRASE | Meets all three criteria | | Pending |
| 168 | login | BROAD | Meets all three criteria | | Pending |
| 169 | logins | BROAD | Meets all three criteria | | Pending |
| 170 | logs | BROAD | Meets all three criteria | | Pending |
| 171 | my account | PHRASE | Meets all three criteria | | Pending |
| 172 | myaccount | BROAD | Meets all three criteria | | Pending |
| 173 | myvision | BROAD | Meets all three criteria | | Pending |
| 174 | need a dentist now | EXACT | Meets all three criteria | | Pending |
| 175 | orgs | BROAD | Meets all three criteria | | Pending |
| 176 | payment | BROAD | Meets all three criteria | | Pending |
| 177 | payments | BROAD | Meets all three criteria | | Pending |
| 178 | phone number | PHRASE | Meets all three criteria | | Pending |
| 179 | phone numbers | PHRASE | Meets all three criteria | | Pending |
| 180 | plan c | PHRASE | Meets all three criteria | | Pending |
| 181 | plan d | PHRASE | Meets all three criteria | | Pending |
| 182 | plan e | PHRASE | Meets all three criteria | | Pending |
| 183 | plan f | PHRASE | Meets all three criteria | | Pending |
| 184 | plan g | PHRASE | Meets all three criteria | | Pending |
| 185 | plan h | PHRASE | Meets all three criteria | | Pending |
| 186 | plan i | PHRASE | Meets all three criteria | | Pending |
| 187 | plan j | PHRASE | Meets all three criteria | | Pending |
| 188 | plan k | PHRASE | Meets all three criteria | | Pending |
| 189 | plan l | PHRASE | Meets all three criteria | | Pending |
| 190 | plan m | PHRASE | Meets all three criteria | | Pending |
| 191 | plan n | PHRASE | Meets all three criteria | | Pending |
| 192 | portal | BROAD | Meets all three criteria | | Pending |
| 193 | portals | BROAD | Meets all three criteria | | Pending |
| 194 | reasonable dental implants near me | EXACT | Meets all three criteria | | Pending |
| 195 | renew | BROAD | Meets all three criteria | | Pending |
| 196 | renewal | BROAD | Meets all three criteria | | Pending |
| 197 | renewals | BROAD | Meets all three criteria | | Pending |
| 198 | renewed | BROAD | Meets all three criteria | | Pending |
| 199 | renewing | BROAD | Meets all three criteria | | Pending |
| 200 | renews | BROAD | Meets all three criteria | | Pending |
| 201 | salaries | PHRASE | Meets all three criteria | | Pending |
| 202 | salary | PHRASE | Meets all three criteria | | Pending |
| 203 | school | PHRASE | Meets all three criteria | | Pending |
| 204 | schools | PHRASE | Meets all three criteria | | Pending |
| 205 | short term | PHRASE | Meets all three criteria | | Pending |
| 206 | short-term | PHRASE | Meets all three criteria | | Pending |
| 207 | sign in | PHRASE | Meets all three criteria | | Pending |
| 208 | signin | BROAD | Meets all three criteria | | Pending |
| 209 | signs | BROAD | Meets all three criteria | | Pending |
| 210 | surgery dental implants | EXACT | Meets all three criteria | | Pending |
| 211 | toothpaste | PHRASE | Meets all three criteria | | Pending |
| 212 | toothpastes | PHRASE | Meets all three criteria | | Pending |
| 213 | sign into | PHRASE | Added | sign-in variant (user, 2026-09-29) | Negate |
| 214 | sign on | PHRASE | Added | sign-in variant (user, 2026-09-29) | Negate |
| 215 | signed in | PHRASE | Added | sign-in variant (user, 2026-09-29) | Negate |
| 216 | signing in | PHRASE | Added | sign-in variant (user, 2026-09-29) | Negate |
| 217 | signon | BROAD | Added | sign-in variant (user, 2026-09-29) | Negate |

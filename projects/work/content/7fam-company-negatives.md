---
name: 7fam-company-negs
about: 7FAM Company Negatives: proposed list, method, evidence and review decisions
read-when: before any 7FAM company or competitor negatives work
readonly: no
---
# 7FAM Company Negatives (proposed 2026-10-09, rev2)
A negative keyword list blocking every company, brand, retailer, marketplace and organization name, and other companies' product names, found in 7 For All Mankind's search terms, split into companies in the fashion/apparel vertical and companies that aren't (user's asks, 2026-10-09). Companion to the 7fam client doc.

Build: /mnt/project-files/spreadsheets/7FAM_Company_Negatives_rev2.xlsx, built by projects/work/products/7fam/build/7FAM_Company_Negatives_rev2.py from 7FAM_Company_Negatives_rev2_data.csv and 7FAM_Company_Negatives_rev2_dropped.csv beside it. Tabs: Fashion-apparel, Not fashion-apparel, Vertical unsure, All negatives, By company, Dropped. Status: proposed, unreviewed, not applied. rev1 (2,178 rows, 4 mixed groups) is superseded.

## Method (2026-10-09)
1. Source: the Aug 1 – Oct 7, 2026 search terms report (4 Brand Search campaigns, 18,803 unique terms, $167,900). PMax and Shopping terms aren't in it.
2. Extraction: 12 agents each scanned a 1,570-term chunk for names of companies, brands, retailers, marketplaces, stores, malls, websites and other companies' products, excluding 7FAM's own names, variants and product lines. 2,170 candidate tokens.
3. Merge: one agent grouped the tokens by company: 643 companies, 80 tokens rejected as not organizations, 228 tokens left in 4 "Mixed" groups.
4. Research: every company was web-researched (proper name, what it is, relation to 7FAM, confidence C/L/U, source URL), and its negatives proposed by the kw-review rules: one row per spelling seen, single word Broad, multi-word Phrase, domains with .com, common-word brands get a narrower alternative.
5. Evidence: nkl/evidence.py (scratch) matched every proposed negative against the report's terms (Broad, Phrase, Exact, no close variants), the enabled positive keywords and the existing campaign negatives.
6. Check pass (the fast pass, 61 agents, about 80 minutes): the 228 mixed tokens were each researched and named (132 kept, 6 changed, 90 dropped as not an organization or garbled 7FAM searches); the 415 companies with any L/U confidence, common word, 7FAM overlap or retailer relation were re-verified with their rows (47 names corrected, 1 dropped as 7FAM's own; rows: 886 keep, 39 change, 139 keep but recommended against, 167 dropped as unseen variants, redundant or generic); the other 305 companies were tagged with a vertical; and a word-level sweep of the 1,656 distinct words in the 12,032 unmatched terms researched 94 candidates and added 46 negatives (38 were not organizations or 7FAM's own). Vertical: fashion/apparel = makes or sells clothing, footwear, denim or fashion accessories, or runs fashion retail or resale; not fashion/apparel = general marketplaces, warehouse clubs, malls and outlet centers, media, finance, unrelated businesses. Then step 5 was rerun.

## Result (Measured, 2026-10-09, rev2)
- 1,961 negatives under 889 company names. Fashion/apparel: 1,825 rows, 783 companies. Not fashion/apparel: 110 rows, 83 companies (malls and outlet centers, Amazon, eBay, Costco, Walmart, Target, Temu, media, consumer brands). Vertical unsure: 26 rows, 23 companies. Confidence: 1,644 C, 243 L, 74 U.
- Together they would have blocked 6,729 of the 18,803 terms, $5,030 of $167,900 (3.0%), 23.2 conversions; $3,938 and 15.9 of those conversions sit on searches that also name 7FAM. By relation (terms counted once per group): competitors 1,640 rows, 714 companies, $2,863, 14.7 conv; retailers that stock 7FAM 134 rows, 57 companies, $1,958 (of which $1,887 and 7.5 conv on searches naming 7FAM); retailers not known to stock 7FAM 114 rows, 62 companies, $164; unrelated businesses 62 rows, 48 companies, $98; marketplaces 11 rows, 8 companies, $16.
- Rec column: Negate 1,700; Don't negate 138 (the check pass argued against them, kept for your call: 80 retailer rows that are mostly store-finder searches naming 7FAM, 31 competitor rows that are common words or 7FAM's own fits such as cigarette, rocker, runway, true, purple, and 27 others); Negate? 19 (retailer names: Nordstrom, Buckle, Boot Barn, Macy's, Neiman Marcus, Saks…); Negate as the proposed keyword 33; Unconfirmed 71.
- 2 rows conflict with enabled positive keywords, "stitch" and "cigarette" (Brand_Product), both now Don't negate. 27 rows are already campaign negatives on Brand_Core or Brand_BR. 221 rows are commonly searched spellings added during research that aren't in the report.
- Dropped tab: 258 rev1 rows with the reason (90 mixed tokens, 167 verify drops, 1 company).
- 12,074 terms match no proposed negative; the sweep covered their distinct words once.

## Open (2026-10-09)
- Retailers that stock 7FAM (57 companies): nearly all their blocked cost is on searches naming 7FAM (store-finder and "nordstrom 7 for all mankind" searches), so negating them blocks 7FAM shoppers looking for a store. 19 rows say Negate?, 80 say Don't negate. Your call.
- The other 58 Don't negate rows and the 71 Unconfirmed rows need your call; the Unconfirmed ones block 1 or 2 terms each at little or no cost.
- "Seven7" is a separate budget denim brand (not 7FAM); its 142 terms cost $850 and converted 3 times, so some searchers mean 7FAM.
- 23 companies' vertical is unsure (small brands the research couldn't place).
- Review decisions: none yet.

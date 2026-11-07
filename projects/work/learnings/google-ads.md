---
about: Google Ads and negative-keyword learnings: matching, Demand Gen, PMax, exports, reports
read-when: before any Google Ads or negative-keyword work
readonly: no
---
# learnings.google-ads

Moved from config.work on 2026-10-07 (config redesign phase 3).

- Negative keywords don't match close variants (misspellings, plurals, merged or split words, accents). Function words such as "of" are matched literally.  
- A BROAD negative blocks any search containing all its words, in any order.  
- Demand Gen campaigns can't use keyword negatives, so a list meant for "every campaign" means every Search campaign. Their only keyword control is account-level content keyword exclusions (Content suitability > Excluded content keywords), which control placement, not searcher intent.  
- Google Ads Editor exports arrive as UTF-16 LE, tab-separated text (even when named .csv); convert with iconv before parsing (2026-10-06).  
- Performance Max negatives (campaign-level, up to 10,000, or shared lists) apply only to Search and Shopping inventory.  
- A search terms report pulled at the manager account carries "Client account conversions" (the client account's goal) instead of "Conversions" and five Total rows (Search terms, Other search terms, Manager account, Search, Demand Gen), so hidden "Other search terms" show only as a total, never per campaign; confirm what the column counts before judging negatives (2026-10-08). "Total: Search" includes the hidden rows (its impressions exceed the visible terms' total), so Other's share is Other / Total: Search (inference, 2026-10-09).
- A day-level search terms report (Search term, Search keyword, Day; no campaign column) splits months but not campaigns: map Search keyword to the Editor export's positive keywords for Brand, NB and CO (528 texts, none shared across groups in the 2026-10-06 export); Enroll and RAQ share keywords and can't be split, and PMax and hidden terms are absent (2026-10-09).
- Editor export "Criterion Type" is Broad, Exact or Phrase for positive keywords and Negative Phrase or Campaign Negative Broad/Phrase/Exact for negatives; filter on those values (2026-10-09).
- Before I pull a report, name the columns and segments the task needs (Day, Campaign, Impr., which conversion column): three pulls in a row on 2026-10-09 each lacked one.

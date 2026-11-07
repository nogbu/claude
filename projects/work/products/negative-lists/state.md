---
about: Current build, build script path, lists and open questions for the negative keyword lists
readonly: no
---
negative-lists  
Delta Dental – AARP negative keyword lists (Google Ads shared lists). Detail and decision history: neg-audit (master index) and the companion docs it names.

Latest build: rev2, Delta_AARP_New_Negative_Lists_rev2.xlsx (2026-09-29)  
Build script: projects/work/products/negative-lists/build/Delta_AARP_New_Negative_Lists_rev2.py. The script is self-contained and rebuilds rev2 exactly.  
Impact script: projects/work/products/negative-lists/build/sqr_list_impact_rev1.py. Run it on a search terms report to see what the lists, as applied, block in Enroll campaigns (cost, conversions, per keyword).  
Format: an Index tab, then one tab per finished list. Columns are Negative keyword and Match type (Broad, Phrase, Exact). Keywords are lowercase with no quotes or brackets. Index counts are COUNTA − 1. Fonts are Arial; headers are bold white on navy (1F3864).

Lists in rev2 (planned campaigns are drafts until the assignment step)  
- AARP Traffic Negatives: 9 negatives. NB, CO (never Brand)  
- Delta Dental Traffic Negatives: 15 negatives. NB, CO (never Brand)  
- AARP Campaign Negatives: 72 negatives. Brand  
- Delta Dental Campaign Negatives: 64 negatives. Brand  
- Competitor Negatives: 218 negatives. Brand, NB  
- Conquesting Negatives: 206 negatives. CO  
- ENT Location Negatives: 41 negatives. NENT campaigns  
- NENT Location Negatives: 76 negatives. ENT campaigns  
- Spanish Negatives: 50 negatives. Brand, NB

Not yet in the build: General Negatives (review in progress; see general-audit) and Location Negatives (a queue of 20; see org-decisions).

Agreed changes for rev3 (unsaved to the build):
1. Delta Dental Campaign Negatives: add deltadentalcoversme (Broad).
2. Delta Dental Traffic Negatives: add deltadentalcoversme (Broad).
3. Delta Dental Campaign Negatives: replace "delta dental premier" (Phrase) with premier (Broad).
4. Delta Dental Campaign Negatives: replace "delta dental providers" (Phrase) with providers (Broad).
5. Add General Negatives once its review is finished (includes "near me" Phrase).
Source: neg-audit, "Search terms review, 2026-10-06".

Open questions  
- How to handle "healthcare" and "life" on General for CO, e.g. a CO version of General without them (see neg-audit constraints).  
- "zocdoc dentist aarp" on CO is blocked by AARP Traffic Negatives' "aarp".  
- Conflict checks are still pending: Spanish against NB, General against Brand, NB and CO, and Conquesting against the full CO export. All need the keyword export.  
- Remaining legacy lists: NonBrand EX (#8) and Lorem Ipsum (#9). Deferred to the end: MS Master Blacklist (#3) and September Shooting (#11).

Rebuild: run the script for the latest rev. For a new rev, copy the script, edit its LISTS and INDEX data, save it as the next rev in projects/work/products/negative-lists/build/, and record its path here.  

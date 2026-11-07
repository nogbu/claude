---
name: 7fam
about: Client doc for 7 For All Mankind (7FAM): accounts, Oct 6 export, naming, structure, lists
read-when: before any 7FAM account work
readonly: no
---
# Client: 7 For All Mankind (7FAM)
Short name: 7fam. Client doc (config.work, Client docs). Paused campaigns are reference only (config.work).

## Product rules
- None yet.

## Accounts
| Platform | Account | Account ID | Managed via |
|---|---|---|---|
| Google Ads | 7 For All Mankind | not in export | not confirmed (SA360 parameters on some assets, inference) |

## Latest export
- Google Ads Editor export, shared 2026-10-06 (UTF-16 tab-separated, 16,897 rows, 275 columns). Project folder: /mnt/project-files/uploads/hearth/ba43db05-e375-4950-a02c-a98b2ac4bbce.
- Covers 10 campaigns, all Enabled, down to keywords, listing groups, search themes, audiences and shared sets; no performance data or account ID.
- All figures below are Measured from this export (2026-10-06) unless tagged otherwise.

## Product context
- Premium denim brand, "Born in LA in 2000", acquired by Delta Galil in 2016 (Listed, deltagalil.com/brands, 2026-10-09). Sells women's, men's and kids' jeans plus pants, shorts, tops, sweaters, outerwear, accessories and leather at https://7forallmankind.com.
- Fits (site filters, 2026-10-09): women Wide Leg, Baggy & Relaxed, Flare, Bootcut, Straight, Slim, Skinny, Petite, Dojo; men Relaxed, Straight, Slim, Skinny. Named lines in the product feed: Dojo, Girls Mini Dojo, Austyn, The Straight, Modern Straight, Stovepipe (trending); Tailorless is an inseam type, Slim Illusion a fabric. Keywords also use B(Air), Kimmie, Josefina, Roxanne, Gwenevere, Alexa, Slimmy, Luxe Vintage, not seen on the site's first pages (inference: older lines).
- Brand variants searched: 7FAM, seven jeans, 7s, sevens, se7en, 7famk (seven7 is a separate brand).
- Jeans $98 (girls) to $298 (selvedge) in the feed's first 6 products (Listed, 2026-10-09). Site offer: $15 off a first purchase of $100+ for email sign-up; no site-wide sale on 2026-10-09. Sale events run as PMax asset groups (Family & Friends, Labor Day, July 4th, Flash Sale, EOS, MDW); export promotions use codes FF25 (25% sitewide), SUMMER (60% select styles), LASTCHANCE (70%), FRIDAY40.
- Sources (read 2026-10-09): 7forallmankind.com (home, women's and men's denim, sale, products.json), deltagalil.com/brands.

## Goals and conversions
- Not confirmed. Every campaign uses account-level conversion goals and bids on conversion value (Target ROAS or Maximize conversion value), so the goal reads as revenue at a target return (inference).
- Customer acquisition: "Bid higher for new customers" on Brand ×3 and PMax Mens; "Only bid for new customers" on the two _NCA PMax campaigns; "Bid equally" elsewhere.

## Naming taxonomy
**Campaigns**
- Search: `G_7FAM_Brand_[Core|Product|BR]`. G: Google Ads (inference). BR = broad match (inference: its one ad group holds only broad keywords).
- Shopping: `G_7FAM_US_Shopping_[Womens|Kids]`.
- PMax: `7FAM_US_PMax [Segment]`, optional `_NCA` suffix for new-customer-only campaigns (inference from the acquisition setting). No `G_` prefix.

**Asset groups**: `[Segment] - [Promo or season] - [DDMonYY]` (e.g. "Womens Jeans - Labor Day - 20Aug26"), with a new asset group per sale event; the old ones are paused.

**Inconsistencies**: PMax lacks the `G_` prefix; "7FAM_US PMax Womens_NCA" has a space for an underscore; asset group dates mix 22Sept26, 23Sep26 and 5feb26; duplicate ad groups "Women's - Accessories"/"Womens - Accessories" and "Womens - Shorts, Skirts & Skorts"/"Womens - Skirts, Skorts & Shorts".

## Locations and languages
- Every campaign targets the United States. PMax Mens instead targets the 50 states plus the US and excludes 234 countries.
- Targeting method: location of presence (Shopping: presence or area of interest). Languages: English on Brand ×3, PMax Mens and PMax Bestsellers; all languages on the rest.

## Campaigns (total daily budget $7,120)
| Campaign | Type | Daily budget | Bidding | Start |
|---|---|---|---|---|
| G_7FAM_Brand_Core | Search | $2,800 | Portfolio tROAS "7FAM - Brand 2025" | 2020-04-03 |
| G_7FAM_Brand_Product | Search | $600 | Portfolio tROAS "7FAM Brand Products 2025" | 2020-06-18 |
| G_7FAM_Brand_BR | Search | $900 | tROAS 825% | 2024-01-23 |
| 7FAM_US_PMax Womens Jeans | PMax | $610 | tROAS 445% | 2022-10-11 |
| 7FAM_US_PMax Mens | PMax | $140 | tROAS 460% | 2023-02-19 |
| 7FAM_US_PMax Bestsellers | PMax | $1,100 | tROAS 560% | 2024-05-29 |
| 7FAM_US_PMax Womens Jeans_NCA | PMax | $300 | tROAS 690% | 2026-05-08 |
| 7FAM_US PMax Womens_NCA | PMax | $170 | tROAS 625% | 2026-05-11 |
| G_7FAM_US_Shopping_Womens | Shopping | $400 | tROAS 575% | 2026-09-23 |
| G_7FAM_US_Shopping_Kids | Shopping | $100 | Maximize conversion value | 2026-10-01 |

- Portfolio targets aren't in the export.
- Search networks: Brand ×3 on Google search and search partners; PMax all networks; Shopping Google search only. Broad match setting off everywhere. AI Max on for Brand_Product (and Shopping_Kids; audit finding 13).
- Merchant Center 6589338 on PMax and Shopping. Shopping_Womens has priority Medium, the rest Low.
- Labels: Brand_Core "7FAMBrandTNT; BudgetScript"; Brand_Product adds "Bidding test" and "RM - Paused for Pacing" though it's Enabled.
- Three unused shared budgets (Tinuiti - Shopping $3,500, New Tinuiti Shared Shopping Budget $1,200, 74AM - YouTube Remarketing $100).
- Account tracking template: `{lpurl}?tw_source=google&tw_adid={creative}&tw_campaign={campaignid}&tw_kwdid={targetid}`; auto-tagging on.

## Search: ad groups and keywords
- Brand_Core: 4 enabled ad groups (A1 - PH, A1 - EX, Sale, Website; Sizing and Locations paused); 128 live keywords (67 exact, 61 phrase). A1 - PH/EX hold the core brand terms and misspellings by match type. 422 campaign negatives (348 exact, 74 phrase), mostly product and fit terms (sent to Brand_Product) plus retailer and place names (ebay, costco, sams club, sawgrass mills).
- Brand_Product: 25 enabled ad groups by gender and category (Mens - Jeans, Womens - Pants…) and by fit (Bootcut, Skinny, Dojo, B(Air)…); 341 live keywords (198 exact, 143 phrase). 7 paused ad groups. Carries the shared brand list "7FAM" (for AI Max).
- Brand_BR: 1 ad group, 20 broad keywords (brand spellings), 27 campaign negatives: competitors (AG, Agolde, Madewell, True Religion, Levi, Citizens of Humanity…), "canada", "reddit" and exact negatives of the core brand terms.
- Ads: 30 enabled RSAs (Brand_Core 4, Brand_Product 25, Brand_BR 1), all Average or Pending strength.

## PMax and Shopping
- Asset groups: 88, of which 7 are enabled, all the Family & Friends 22–23 Sept 2026 event (plus Mens "FW26 - Launch - 25Aug26 - Feed Only"). The paused ones are past sale events.
- Listing groups split on Custom label 0 (women/men), Custom label 1 (bestsellers_women/bestsellers_men) and Product type. Womens Jeans PMax bids on women's jeans only; Bestsellers on the bestseller labels; Mens on men's product types.
- Search themes: 401 across PMax Mens, Bestsellers and the two _NCA campaigns (e.g. "designer jeans for men", "luxury denim").
- Audience signals: "NB Womens PMAX 2023" or "NB Mens PMAX 2023" (customer lists, lapsed purchasers, custom intent, interests) on most asset groups; Mens' enabled groups use "Purchasers of SEVN LIVE - GA4".
- _NCA campaigns exclude ages 18–24 and 65+.
- Shopping_Womens: ad group Womens (enabled) bids on women's non-jeans product types and excludes bestsellers; ad group Womens Jeans is paused. Shopping_Kids: ad group Girls bids on 39 item IDs plus everything else.

## Shared negative keyword lists
| List | Keywords | Attached to (enabled campaigns) |
|---|---|---|
| 2026 - Brand Kids (Negative) | 67 | Brand ×3, PMax ×5 |
| Account Negatives (All Campaigns & Match Types) | 84 | PMax Womens Jeans_NCA, PMax Womens_NCA |
| Competitor | 6 | PMax Womens Jeans_NCA, PMax Womens_NCA |
| Non-MFO Neg List | 29 | Brand_Core |
| Search Poor Performers List | 1 | Brand_Core, Brand_Product |

- 10 other lists are attached to no enabled campaign: Shared - Brand_General - Negatives (460), Brand Exact KW (319), Kids Negatives (67), Store (52), 2026 Kids ×3 (36, 22, 8), PLA Brand Neg List (29), Shopping MFO line (9), DSA - Negatives (5).
- Shopping ×2 carry no negatives at all. The list contents aren't in the export.
- Shared brand lists: "7FAM" (on Brand_Product) and "Not 7FAM".

## Performance snapshots and audits
- 7fam-settings-audit: campaign settings audit from the Oct 6 export, 14 findings (projects/work/content/7fam-settings-audit-2026-10-06.md).
- 7fam-company-negs: proposed Company Negatives rev2 (1,961 rows, 889 companies, fashion/apparel vs not) from the Aug 1 – Oct 7 search terms, unreviewed (projects/work/content/7fam-company-negatives.md); build 7FAM_Company_Negatives_rev2.xlsx, script in products/7fam/build/.
- sqr-aug-oct: search terms by day, Aug 1 – Oct 7, 2026, 4 Brand Search campaigns, $167,900, 4,106 conversions; file /mnt/project-files/uploads/hearth/f936487c-c8f5-4dd8-97e1-39cf42395126 (notes in .notes/inputs.md).

## Decisions and why
- 2026-10-06: built from the Oct 6 export, set up like the Delta Dental client doc (agreed 2026-10-09).

## Open questions
- Account ID and how the account is managed (Google Ads directly or SA360).
- Goal and which conversions count, and the targets behind the two portfolio strategies.
- Product rules: brand terms to protect, campaigns to ignore.
- Settings audit findings 1–14 (7fam-settings-audit) await your call on each.
- Brand_Kids: spent through Oct 1 in the search terms report ($2,231) but isn't in the Oct 6 export (inference: paused or removed that week).
- Does 7FAM also run on Microsoft Advertising?

## Next step
- Company Negatives: review rev2 (7fam-company-negs): the retailer question, the rows the check pass argued against, then the rest. Then the open questions above.

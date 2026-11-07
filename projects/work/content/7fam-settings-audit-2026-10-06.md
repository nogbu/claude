---
name: 7fam-settings-audit
about: 7FAM settings audit, Oct 6 export: 14 findings
read-when: before changing 7FAM settings or negatives
readonly: no
---
# 7FAM campaign settings audit (2026-10-06 export)
All figures Measured from the 2026-10-06 export unless tagged (inference). Each finding is proposed 2026-10-07; none has your call yet.

## Likely problems
1. Shopping_Womens and Shopping_Kids carry no negatives at all: no campaign negatives, no shared lists. PLA Brand Neg List (29) and Shopping MFO line (9) exist but are attached to nothing.
2. "Account Negatives (All Campaigns & Match Types)" (84) is on only the two _NCA PMax campaigns, though its name says every campaign. Competitor (6) is likewise only on the _NCA campaigns.
3. Shopping_Womens (launched 2026-09-23) and PMax Womens_NCA bid on the same products: women's non-jeans items, bestsellers excluded. When PMax and another campaign are eligible, the one with higher Ad Rank serves, so the Shopping campaign competes with PMax rather than adding reach.
4. PMax Womens Jeans and Womens Jeans_NCA have identical listing groups (women's jeans, bestsellers excluded). Womens Jeans bids equally for new and returning customers, so the two compete for new customers at different targets (445% vs 690%).
5. Bestsellers gap (inference): every other PMax and Shopping campaign excludes the bestseller labels, and PMax Bestsellers bids only on women's B(Air), Straight Leg, Dojo, Bootcut and men's Straight Leg, Slim, Skinny. Bestseller-labeled products outside those fits are advertised in no PMax or Shopping campaign, if any exist in the feed.
6. Both Shopping campaigns use "presence or interest" location targeting, which can reach people outside the US who show interest in it; every other campaign uses presence.
7. Brand_Core and Brand_Product carry 360 observation audiences; 205 are "Similar to" segments, which Google stopped generating on 2023-05-01, and some are unrelated (houses for sale, car rental). 67 have bid adjustments, which Target ROAS doesn't use.

## Questionable, to confirm
8. Brand_Product is Enabled but labeled "RM - Paused for Pacing" (also "Bidding test"), with AI Max on.
9. Brand_Core negates place and store terms ("charlotte", "oklahoma city", "sawgrass mills", "island") while its Locations ad group is paused: where-to-buy brand searches may be blocked on purpose or by accident.
10. The _NCA campaigns exclude ages 18–24 and 65+; no other campaign has age limits.
11. One enabled RSA per Search ad group (30 total; Brand_BR has 1), all Average or Pending strength.
12. PMax Mens has two enabled asset groups ("Feed Only" 2026-08-25 and Family & Friends) covering the same men's products.
13. The export shows AI Max, text customization and Final URL expansion "Enabled" on Shopping_Kids, which a Shopping campaign can't use (inference: an Editor export quirk; check in the UI).
14. Brand Search runs on search partners, with Brand_Core at $2,800/day on a portfolio Target ROAS whose target isn't in the export.

## Sources
- https://support.google.com/google-ads/answer/13810170 (Performance Max and other campaigns)
- https://support.google.com/google-ads/answer/1722038 (advanced location options)
- https://support.google.com/sa360/answer/13388565 (similar audiences end)
- https://support.google.com/google-ads/answer/2732132 (bid adjustments with Smart Bidding)

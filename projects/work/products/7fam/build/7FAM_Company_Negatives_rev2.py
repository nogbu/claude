"""Build 7FAM_Company_Negatives_rev2.xlsx: the proposed company/brand/retailer negative keyword list for
7 For All Mankind, split by vertical (fashion/apparel or not), with the proper name of each company blocked,
the search-terms evidence and the fast check pass's findings behind each row.
Run: python3 7FAM_Company_Negatives_rev2.py [OUT.xlsx]
Reads, next to this script: 7FAM_Company_Negatives_rev2_data.csv (one row per proposed negative) and
7FAM_Company_Negatives_rev2_dropped.csv (rev1 rows the check pass of 2026-10-09 removed, with the reason).
Built from the 2026-10-06 Editor export and the Aug 1 - Oct 7, 2026 search terms report by the extract/merge/
research workflow (rev1), the check pass (mixed-group naming, verification, vertical tagging, word-level sweep)
and nkl/evidence.py. Styling follows the Delta Dental lists: Arial, bold white headers on navy (1F3864).
"""
import os, sys
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(HERE, '7FAM_Company_Negatives_rev2_data.csv'), dtype=str, keep_default_na=False)
dropped = pd.read_csv(os.path.join(HERE, '7FAM_Company_Negatives_rev2_dropped.csv'), dtype=str, keep_default_na=False)
out = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/spreadsheets/7FAM_Company_Negatives_rev2.xlsx'
NUM = ['Terms blocked', 'Cost blocked', 'Clicks', 'Conversions', 'Conv. value', 'Terms naming 7FAM', 'Cost naming 7FAM', 'Conv. naming 7FAM']
for c in NUM:
    data[c] = pd.to_numeric(data[c])
for c in ['Terms blocked (rev1)', 'Cost blocked (rev1)']:
    dropped[c] = pd.to_numeric(dropped[c])

HEAD_FONT = Font(name='Arial', bold=True, color='FFFFFF')
HEAD_FILL = PatternFill('solid', fgColor='1F3864')
BODY_FONT = Font(name='Arial')
WIDTHS = [30, 8, 36, 18, 26, 60, 20, 26, 10, 50, 40, 22, 60, 10, 10, 10, 11, 8, 11, 11, 12, 12, 12, 60, 50, 36]


def write_table(ws, df, widths):
    ws.append(list(df.columns))
    for cell in ws[1]:
        cell.font, cell.fill, cell.alignment = HEAD_FONT, HEAD_FILL, Alignment(vertical='top', wrap_text=True)
    for row in df.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in row])
    for r in ws.iter_rows(min_row=2):
        for cell in r:
            cell.font = BODY_FONT
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


wb = openpyxl.Workbook()
readme = wb.active
readme.title = 'README'
fash = data[data['Vertical'] == 'fashion/apparel']
notf = data[data['Vertical'] == 'not fashion/apparel']
uns = data[data['Vertical'] == 'unsure']
lines = [
    ['7FAM Company Negatives rev2 (built 2026-10-09)'],
    ['Proposed negative keyword list blocking company, brand, retailer, marketplace and organization names, and other companies\' product names, found in 7 For All Mankind\'s Google Ads search terms (Aug 1 - Oct 7, 2026, Brand Search campaigns).'],
    ['Status: PROPOSED. Nothing is reviewed or applied yet. Each row\'s Rec column carries the recommendation: "Negate", "Negate?" (your call), "Negate as the proposed keyword", "Don\'t negate" (the check pass argued against it; it stays listed for your call) or "Unconfirmed".'],
    ['rev2 = rev1 after the fast check pass of 2026-10-09: the 228 mixed-group tokens were named, 415 companies and their rows re-verified, every company tagged with a vertical, and a word-level sweep of the unmatched terms added 46 rows. 258 rev1 rows were removed (Dropped tab).'],
    [''],
    ['Tabs'],
    ['Fashion-apparel: %d negatives for %d companies that make or sell clothing, footwear, denim or fashion accessories, or run fashion retail or resale.' % (len(fash), fash['Company'].nunique())],
    ['Not fashion-apparel: %d negatives for %d companies outside that vertical (general marketplaces, malls and outlet centers, media, finance, unrelated businesses).' % (len(notf), notf['Company'].nunique())],
    ['Vertical unsure: %d negatives for %d companies the research could not place.' % (len(uns), uns['Company'].nunique())],
    ['All negatives: the three tabs together, alphabetical. By company: one row per company with its vertical, relation, confidence, source and totals.'],
    ['Dropped: %d rev1 rows the check pass removed (spellings not in the report, rows covered by another row, generic words, tokens that are not an organization), with the reason.' % len(dropped)],
    [''],
    ['Columns'],
    ['Negative keyword: lowercase, no quotes or brackets. Match: Broad (single words), Phrase (multi-word) or Exact.'],
    ['Company: the proper name of the company or brand the keyword blocks, as the company styles it (web-researched; Confidence C = confirmed on its own site or an authoritative page, L = likely, U = unconfirmed; Source = the page used).'],
    ['Vertical: fashion/apparel, not fashion/apparel, or unsure. Relation to 7FAM: competitor, retailer that stocks 7FAM, retailer not known to stock 7FAM, marketplace or resale, unrelated business.'],
    ['Proposed negative keyword: a narrower keyword to use instead when the plain word also blocks searches naming 7FAM.'],
    ['Check pass: verified (company and row re-checked), tagged only (confirmed in rev1, vertical added), named from a mixed group, or added by the sweep. Check note: the check pass\'s reasoning for the row.'],
    ['Terms blocked / Cost blocked / Clicks / Conversions / Conv. value: what the keyword would have matched in the Aug 1 - Oct 7 report (Broad = all words in any order; Phrase = words in sequence; Exact = whole term; no close variants).'],
    ['Terms naming 7FAM / Cost naming 7FAM / Conv. naming 7FAM: the part of that which also contains a 7FAM brand token (7, seven, 7fam, mankind...).'],
    ['Positive keyword conflicts: enabled positive keywords in the account that the negative would block. Already negated: campaigns where the same keyword is already a campaign negative.'],
    ['Seen in report: False = a commonly searched spelling added during research, not in the report.'],
    [''],
    ['Totals: %d negatives for %d companies. Cost blocked sums overlap where several keywords match one term; the de-duplicated figures are in the content file (7fam-company-negs).' % (len(data), data['Company'].nunique())],
]
for l in lines:
    readme.append(l)
for r in readme.iter_rows():
    for cell in r:
        cell.font = Font(name='Arial', bold=(cell.row in (1, 6, 13)))
readme.column_dimensions['A'].width = 160

for title, df in [('Fashion-apparel', fash), ('Not fashion-apparel', notf), ('Vertical unsure', uns), ('All negatives', data)]:
    write_table(wb.create_sheet(title), df, WIDTHS)

summ = (data.groupby(['Company', 'Vertical', 'Type', 'Relation to 7FAM', 'Confidence', 'What it is', 'Source'], sort=False)
        .agg(**{'Negatives': ('Negative keyword', 'size'), 'Terms blocked': ('Terms blocked', 'sum'), 'Cost blocked': ('Cost blocked', 'sum'),
               'Conversions': ('Conversions', 'sum'), 'Cost naming 7FAM': ('Cost naming 7FAM', 'sum'),
               'Keywords': ('Negative keyword', lambda s: ', '.join(s))}).reset_index()
        .sort_values('Company', key=lambda s: s.str.lower()))
write_table(wb.create_sheet('By company'), summ, [36, 18, 20, 26, 10, 50, 40, 10, 12, 12, 12, 14, 80])
write_table(wb.create_sheet('Dropped'), dropped, [30, 8, 36, 18, 26, 80, 12, 12])
os.makedirs(os.path.dirname(out), exist_ok=True)
wb.save(out)
print('wrote', out, len(data), 'rows,', data['Company'].nunique(), 'companies;', 'fashion', len(fash), 'not', len(notf), 'unsure', len(uns), 'dropped', len(dropped))

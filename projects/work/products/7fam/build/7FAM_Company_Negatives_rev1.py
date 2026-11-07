"""Build 7FAM_Company_Negatives_rev1.xlsx: the proposed company/brand/retailer negative keyword list for
7 For All Mankind, with the proper name of each company blocked and the search-terms evidence behind it.
Run: python3 7FAM_Company_Negatives_rev1.py [OUT.xlsx]
Reads 7FAM_Company_Negatives_rev1_data.csv next to this script (one row per proposed negative; built from the
2026-10-06 Editor export and the Aug 1 - Oct 7, 2026 search terms report by the extract/merge/research workflow
of 2026-10-09 and nkl/evidence.py). Output: a README tab, the full list (alphabetical) and a per-company summary.
Styling follows the Delta Dental lists: Arial, bold white headers on navy (1F3864).
"""
import os, sys
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(HERE, '7FAM_Company_Negatives_rev1_data.csv'), dtype=str, keep_default_na=False)
out = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/spreadsheets/7FAM_Company_Negatives_rev1.xlsx'
NUM = ['Terms blocked', 'Cost blocked', 'Clicks', 'Conversions', 'Conv. value', 'Terms naming 7FAM', 'Cost naming 7FAM', 'Conv. naming 7FAM']
for c in NUM:
    data[c] = pd.to_numeric(data[c])

HEAD_FONT = Font(name='Arial', bold=True, color='FFFFFF')
HEAD_FILL = PatternFill('solid', fgColor='1F3864')
BODY_FONT = Font(name='Arial')


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
lines = [
    ['7FAM Company Negatives rev1 (built 2026-10-09)'],
    ['Proposed negative keyword list blocking company, brand, retailer, marketplace and organization names, and other companies\' product names, found in 7 For All Mankind\'s Google Ads search terms (Aug 1 - Oct 7, 2026, Brand Search campaigns).'],
    ['Status: PROPOSED. Nothing is reviewed or applied yet. Each row\'s Rec column carries the recommendation; "Negate?" rows need a decision.'],
    [''],
    ['Tabs'],
    ['Company Negatives: one row per negative keyword, alphabetical. Keyword lowercase, no quotes or brackets; Match is Broad, Phrase or Exact.'],
    ['By company: one row per company with its proper name, type, relation to 7FAM, confidence, source and totals.'],
    [''],
    ['Columns (Company Negatives)'],
    ['Company: the proper name of the company or brand the keyword blocks, as the company styles it (web-researched; Confidence C = confirmed on its own site or an authoritative page, L = likely, U = unconfirmed; Source = the page used).'],
    ['Proposed negative keyword: a narrower keyword to use instead when the plain word also blocks searches naming 7FAM.'],
    ['Terms blocked / Cost blocked / Clicks / Conversions / Conv. value: what the keyword would have matched in the Aug 1 - Oct 7 report (Broad = all words in any order; Phrase = words in sequence; Exact = whole term; no close variants).'],
    ['Terms naming 7FAM / Cost naming 7FAM / Conv. naming 7FAM: the part of that which also contains a 7FAM brand token (7, seven, 7fam, mankind...).'],
    ['Positive keyword conflicts: enabled positive keywords in the account that the negative would block. Already negated: campaigns where the same keyword is already a campaign negative.'],
    ['Seen in report: False = a commonly searched spelling added during research, not in the report.'],
    [''],
    ['Totals: %d negatives for %d companies; %d search terms and $%.0f of the report\'s $167,900 would have been blocked.' % (
        len(data), data['Company'].nunique(), 0, 0)],
]
for l in lines:
    readme.append(l)
for r in readme.iter_rows():
    for cell in r:
        cell.font = Font(name='Arial', bold=(cell.row in (1, 5, 9)))
readme.column_dimensions['A'].width = 160

ws = wb.create_sheet('Company Negatives')
widths = [30, 8, 36, 26, 60, 20, 26, 10, 50, 40, 10, 10, 10, 11, 8, 11, 11, 12, 12, 12, 60, 50, 36]
write_table(ws, data, widths)

summ = (data.groupby(['Company', 'Type', 'Relation to 7FAM', 'Confidence', 'What it is', 'Source'], sort=False)
        .agg(**{'Negatives': ('Negative keyword', 'size'), 'Terms blocked': ('Terms blocked', 'sum'), 'Cost blocked': ('Cost blocked', 'sum'),
               'Conversions': ('Conversions', 'sum'), 'Cost naming 7FAM': ('Cost naming 7FAM', 'sum'),
               'Keywords': ('Negative keyword', lambda s: ', '.join(s))}).reset_index()
        .sort_values('Company', key=lambda s: s.str.lower()))
ws2 = wb.create_sheet('By company')
write_table(ws2, summ, [36, 20, 26, 10, 50, 40, 10, 12, 12, 12, 14, 80])

# fill the totals line now that the frame is known (terms counted once each is done by nkl/evidence.py: see the content file)
readme['A17'] = 'Totals: %d negatives for %d companies. Cost blocked sums overlap where several keywords match one term; the de-duplicated figures are in the content file.' % (len(data), data['Company'].nunique())
os.makedirs(os.path.dirname(out), exist_ok=True)
wb.save(out)
print('wrote', out, len(data), 'rows,', data['Company'].nunique(), 'companies')

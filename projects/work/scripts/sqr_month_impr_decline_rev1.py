"""Top search terms by impression decline and climb between two months, from a day-level search terms report
("Untitled report": Search term, Search keyword, Day, Cost, Impr., Clicks, ...; UTF-16 tab or UTF-8 comma, 2 title rows).
Usage: python3 sqr_month_impr_decline_rev1.py REPORT.csv OUT.xlsx [EARLIER_MONTH LATER_MONTH] [TOP]
Defaults: 2026-08 2026-09, top 100. Impressions are summed per search term across keywords and days.
Sheets: "Top N declines" (later minus earlier, most negative first), "Top N climbers" (largest gains first), Notes."""
import sys, io, pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment


def load(path):
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig')
    lines = text.splitlines()
    sep = '\t' if '\t' in lines[2] else ','
    df = pd.read_csv(io.StringIO('\n'.join(lines[2:])), sep=sep, dtype=str)
    df = df[~df['Search term'].str.startswith('Total:', na=True)].copy()
    for c in ['Impr.', 'Clicks', 'Cost']:
        df[c] = pd.to_numeric(df[c].str.replace(',', ''), errors='coerce').fillna(0)
    df['month'] = df['Day'].str[:7]
    return lines[1].strip().strip('"'), df


def main(report, out, m1='2026-08', m2='2026-09', top=100):
    period, df = load(report)
    l1, l2 = (pd.Period(m).strftime('%b %Y') for m in (m1, m2))

    def month(m):
        d = df[df['month'] == m]
        return d.groupby('Search term').agg(impr=('Impr.', 'sum'), clicks=('Clicks', 'sum'), cost=('Cost', 'sum')), d

    a, da = month(m1); b, db = month(m2)
    m = a.join(b, how='outer', lsuffix='_1', rsuffix='_2').fillna(0)
    m['change'] = m['impr_2'] - m['impr_1']
    m['pct'] = m['change'] / m['impr_1'].where(m['impr_1'] > 0)

    def table(sub):
        t = sub.reset_index()
        t.insert(0, 'Rank', range(1, len(t) + 1))
        t = t[['Rank', 'Search term', 'impr_1', 'impr_2', 'change', 'pct', 'clicks_1', 'clicks_2', 'cost_1', 'cost_2']]
        t.columns = ['Rank', 'Search term', f'Impr. {l1}', f'Impr. {l2}', 'Impr. change', 'Impr. % change',
                     f'Clicks {l1}', f'Clicks {l2}', f'Cost {l1}', f'Cost {l2}']
        return t

    dec = table(m[m['change'] < 0].sort_values(['change', 'impr_1'], ascending=[True, False]).head(top))
    inc = table(m[m['change'] > 0].sort_values(['change', 'impr_2'], ascending=[False, False]).head(top))
    new_in_top = int((inc[f'Impr. {l1}'] == 0).sum())
    notes = [
        f'Source: {report.split("/")[-1]} ({period}), a day-level search terms report with no campaign column (account-wide; Search keyword given per row). Figures Measured from it.',
        f'{l1}: {da["Day"].nunique()} days, {int(da["Impr."].sum()):,} impressions on {a.shape[0]:,} search terms. {l2}: {db["Day"].nunique()} days, {int(db["Impr."].sum()):,} impressions on {b.shape[0]:,} search terms.',
        f'Impressions are summed per search term across keywords and days. Declines sheet: the {len(dec)} largest declines ({l2} minus {l1}), largest first; {int((m["change"] < 0).sum()):,} terms declined in all. Climbers sheet: the {len(inc)} largest gains, largest first; {int((m["change"] > 0).sum()):,} terms gained in all, {new_in_top} of the top {len(inc)} had no {l1} impressions (no % change).',
        'Hidden "Other search terms" are not in the report, so they are not counted.',
    ]
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        dec.to_excel(w, sheet_name=f'Top {len(dec)} declines', index=False)
        inc.to_excel(w, sheet_name=f'Top {len(inc)} climbers', index=False)
        pd.DataFrame({'Notes': notes}).to_excel(w, sheet_name='Notes', index=False)
        hf, fill = Font(name='Arial', bold=True, color='FFFFFF'), PatternFill('solid', fgColor='1F3864')
        for ws in w.book.worksheets[:2]:
            for c in ws[1]:
                c.font, c.fill, c.alignment = hf, fill, Alignment(wrap_text=True, vertical='top')
            for row in ws.iter_rows(min_row=2):
                for c in row:
                    c.font = Font(name='Arial')
                row[5].number_format = '0%'
                for c in row[8:10]:
                    c.number_format = '$#,##0.00'
                for c in row[2:5]:
                    c.number_format = '#,##0'
            for col, wd in zip('ABCDEFGHIJ', [6, 44, 12, 12, 12, 12, 11, 11, 12, 12]):
                ws.column_dimensions[col].width = wd
            ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
        n = w.book.worksheets[2]; n.column_dimensions['A'].width = 150
        for row in n.iter_rows():
            for c in row:
                c.font = Font(name='Arial')
    print('\n'.join(notes))
    print(dec.iloc[:5, :6].to_string(index=False)); print(inc.iloc[:10, :6].to_string(index=False))


if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], *(a[3:5] if len(a) > 4 else ()), **({'top': int(a[5])} if len(a) > 5 else {}))

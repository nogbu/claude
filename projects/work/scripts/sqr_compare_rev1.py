"""Compare impressions by search term between two Google Ads search terms reports.
Usage: python3 sqr_compare_rev1.py EARLIER.csv LATER.csv OUT.xlsx
Reads UTF-16 tab or UTF-8 comma exports; sums Impr. per search term across campaigns/ad groups."""
import sys, io, csv, pandas as pd

def load(path):
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig')
    lines = text.splitlines()
    dates = lines[1].strip().strip('"')
    sep = '\t' if '\t' in lines[2] else ','
    df = pd.read_csv(io.StringIO('\n'.join(lines[2:])), sep=sep, dtype=str)
    df = df[~df['Search term'].str.startswith('Total:', na=True)]
    for c in ['Impr.', 'Clicks', 'Cost']:
        df[c] = pd.to_numeric(df[c].str.replace(',', ''), errors='coerce').fillna(0)
    g = df.groupby('Search term').agg(impr=('Impr.', 'sum'), clicks=('Clicks', 'sum'), cost=('Cost', 'sum'),
                                       campaigns=('Campaign', lambda s: ', '.join(sorted(set(s)))))
    return dates, g, len(df)

d1, a, n1 = load(sys.argv[1]); d2, b, n2 = load(sys.argv[2])
m = a.join(b, how='outer', lsuffix='_1', rsuffix='_2')
for c in ['impr', 'clicks', 'cost']:
    m[f'{c}_1'] = m[f'{c}_1'].fillna(0); m[f'{c}_2'] = m[f'{c}_2'].fillna(0)
m['change'] = m['impr_2'] - m['impr_1']
m['pct'] = m.apply(lambda r: (r.change / r.impr_1) if r.impr_1 else None, axis=1)
m['status'] = m.apply(lambda r: 'New' if r.impr_1 == 0 else ('Gone' if r.impr_2 == 0 else
                     ('Increase' if r.change > 0 else ('Decline' if r.change < 0 else 'No change'))), axis=1)
m['campaigns'] = m['campaigns_2'].fillna(m['campaigns_1'])
out = m.reset_index()[['Search term', 'impr_1', 'impr_2', 'change', 'pct', 'status',
                       'clicks_1', 'clicks_2', 'cost_1', 'cost_2', 'campaigns']]
out.columns = ['Search term', f'Impr. ({d1})', f'Impr. ({d2})', 'Impr. change', 'Impr. % change', 'Status',
               f'Clicks ({d1})', f'Clicks ({d2})', f'Cost ({d1})', f'Cost ({d2})', 'Campaigns']
out = out.sort_values(['Impr. change', 'Search term'], ascending=[False, True])
with pd.ExcelWriter(sys.argv[3], engine='openpyxl') as w:
    out.to_excel(w, sheet_name='All terms', index=False)
    for name, st in [('Increase', ['Increase', 'New']), ('Decline', ['Decline', 'Gone'])]:
        sub = out[out.Status.isin(st)]
        if name == 'Decline': sub = sub.sort_values(['Impr. change', 'Search term'])
        sub.to_excel(w, sheet_name=name, index=False)
    for ws in w.book.worksheets:
        ws.freeze_panes = 'B2'; ws.auto_filter.ref = ws.dimensions
        ws.column_dimensions['A'].width = 50
        for col in 'BCDEFGHIJ': ws.column_dimensions[col].width = 16
        ws.column_dimensions['K'].width = 60
        for cell in ws['E'][1:]: cell.number_format = '0%'
        for col in 'IJ':
            for cell in ws[col][1:]: cell.number_format = '$#,##0.00'
print(d1, n1, 'rows,', len(a), 'terms |', d2, n2, 'rows,', len(b), 'terms')
print(out.Status.value_counts().to_string())
print('impr totals', a.impr.sum(), b.impr.sum())
for st in ['Increase', 'Decline', 'New', 'Gone']:
    s = out[out.Status == st]
    print(st, 'sum change', s['Impr. change'].sum())
print(out.head(10).iloc[:, :6].to_string()); print(out.sort_values('Impr. change').head(10).iloc[:, :6].to_string())

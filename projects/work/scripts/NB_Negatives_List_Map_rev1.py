"""Build NB_Negatives_List_Map_rev1.xlsx: every negative from the NB lists walkthrough (nb-lists),
the existing shared list each should go in, and what it would block on Brand and CO.

Usage: python3 NB_Negatives_List_Map_rev1.py <search terms report (UTF-16 TSV, 2 title rows)> <out.xlsx>
Reads projects/work/content/nb-list-walkthrough.md (repo-relative to this file) for the reviewed negatives.
"""
import re, sys, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
WALK = os.path.join(REPO, 'projects/work/content/nb-list-walkthrough.md')

STATES_ADDED = ('al co dc de fl hi id in ky la md me ms mt nd ne nh nm nv ny ok or pa sd tx ut vt wv wy').split()

LIST_CAMPAIGNS = {
    'General Negatives': 'Brand, NB, CO',
    'Delta Dental Traffic Negatives': 'NB, CO (never Brand)',
    'AARP Traffic Negatives': 'NB, CO (never Brand)',
    'Competitor Negatives + Conquesting Negatives': 'Brand, NB (Competitor); CO (Conquesting)',
}


def section(text, start, end):
    return text[text.index(start):text.index(end)]


def rows(sec):
    out = []
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 4 and cells[0].isdigit() and cells[-1] == 'Negate':
            out.append((cells[1], cells[2]))
    return out


def load_negatives():
    t = open(WALK, encoding='utf-8').read()
    care = rows(section(t, '## Dental Care Negatives', '## Delta Dental Traffic'))
    dd = rows(section(t, '## Delta Dental Traffic', '## AARP Traffic'))
    dd += [('deltadental' + s, 'BROAD') for s in STATES_ADDED]
    aarp = rows(section(t, '## AARP Traffic', '## Competitor Negatives'))
    comp = [(r[0], r[1]) for r in rows(section(t, '## Competitor Negatives', '## Flags for'))]
    out = []
    for k, m in care:
        out.append((k, m, 'Dental Care (new)', 'General Negatives'))
    for k, m in dd:
        out.append((k, m, 'Delta Dental Traffic additions', 'Delta Dental Traffic Negatives'))
    for k, m in aarp:
        out.append((k, m, 'AARP Traffic additions', 'AARP Traffic Negatives'))
    for k, m in comp:
        out.append((k, m, 'Competitor additions', 'Competitor Negatives + Conquesting Negatives'))
    return out


def matcher(k, m):
    kw = k.lower().split()
    if m == 'BROAD':
        return lambda q: set(kw) <= set(q)
    return lambda q: any(q[i:i + len(kw)] == kw for i in range(len(q) - len(kw) + 1))


def main(report, out):
    df = pd.read_csv(report, encoding='utf-16', sep='\t', skiprows=2, thousands=',')
    df = df[df['Campaign'].notna()].copy()
    for c in ['Cost', 'Conversions']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['Enroll'] = df['Conversions'].where(df['Campaign'].str.contains('_Enroll_'), 0)
    df['q'] = df['Search term'].astype(str).str.lower().str.split()
    groups = {g: df[df['Campaign'].str.contains(f'_{g}_')] for g in ('NB', 'Brand', 'CO')}

    wb = Workbook()
    ws = wb.active
    ws.title = 'List map'
    head = ['Negative keyword', 'Match type', 'Reviewed as', 'Proposed existing list', 'Campaigns it reaches',
            'NB spend', 'Brand spend', 'CO spend', 'Enroll conv. (NB+Brand+CO)']
    ws.append(head)
    negs = load_negatives()
    for k, m, src, lst in negs:
        f = matcher(k, m)
        vals, conv = [], 0
        for g in ('NB', 'Brand', 'CO'):
            d = groups[g]
            hit = d[d['q'].map(f)]
            # Brand never carries Traffic lists, so it shows nothing there
            if g == 'Brand' and 'Traffic' in lst:
                vals.append(None)
                continue
            vals.append(round(float(hit['Cost'].sum()), 2))
            conv += float(hit['Enroll'].sum())
        ws.append([k, m.capitalize(), src, lst, LIST_CAMPAIGNS[lst]] + vals + [round(conv, 1)])

    hf = Font(name='Arial', bold=True, color='FFFFFF')
    fill = PatternFill('solid', fgColor='1F3864')
    for c in ws[1]:
        c.font, c.fill, c.alignment = hf, fill, Alignment(wrap_text=True, vertical='top')
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name='Arial')
        for c in row[5:8]:
            c.number_format = '$#,##0.00'
    for col, w in zip('ABCDEFGHI', [24, 11, 28, 40, 36, 11, 11, 11, 14]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions

    s = wb.create_sheet('Notes')
    for line in [
        'Source: search terms report, Sep 5 - Oct 4, 2026, all campaigns. Spend = what each negative matches on its own in that campaign group (Measured). Enroll conv. counts Enroll campaigns only.',
        'Brand spend is blank for Traffic lists: Traffic lists never go on Brand (client rule).',
        'NB spend for the 29 added state forms is $0: no searches this period.',
        'General Negatives purpose: fits no other list, applies to every Search campaign. Its audit is paused at item 40 of 212.',
    ]:
        s.append([line])
        s.cell(s.max_row, 1).font = Font(name='Arial')
    s.column_dimensions['A'].width = 140
    wb.save(out)
    print(len(negs), 'negatives ->', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

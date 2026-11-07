"""Measure what the negative lists block in a Google Ads search terms report (Enroll campaigns only).
Run: python3 sqr_list_impact_rev1.py REPORT.csv [LISTS_SCRIPT.py]
REPORT: search terms export (UTF-16 tab-separated, 2 title rows) with Cost, Impr., Clicks, Conversions.
LISTS_SCRIPT: the negative-lists build script whose LISTS dict to test (default: the rev2 build script).
Lists as actually applied (2026-10-06): Brand campaigns get AARP Campaign, Delta Dental Campaign, Competitor
and Spanish Negatives, plus ENT Location Negatives on NENT campaigns and NENT Location Negatives on ENT campaigns.
Traffic and Conquesting lists are not in use. RAQ campaigns are ignored (config.work).
Matching: Broad = all words in any order; Phrase = words in sequence; Exact = whole term. No close variants.
"""
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
report = sys.argv[1]
lists_script = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'Delta_AARP_New_Negative_Lists_rev2.py')
ns = {}
exec('LISTS = {' + open(lists_script).read().split('LISTS = {', 1)[1].split('\nINDEX = [', 1)[0], ns)
LISTS = ns['LISTS']

def lists_for(campaign):
    ls = ['AARP Campaign Negatives', 'Delta Dental Campaign Negatives', 'Competitor Negatives', 'Spanish Negatives']
    ls.append('ENT Location Negatives' if '_NENT_' in campaign else 'NENT Location Negatives')
    return ls

def matches(term, kw, mt):
    q, k = str(term).lower().split(), kw.lower().split()
    if mt == 'Exact':
        return q == k
    if mt == 'Phrase':
        return any(q[i:i + len(k)] == k for i in range(len(q) - len(k) + 1))
    return set(k) <= set(q)

M = ['Impr.', 'Clicks', 'Cost', 'Conversions']
df = pd.read_csv(report, encoding='utf-16', sep='\t', skiprows=2, thousands=',')
df = df[df['Campaign'].notna() & df['Campaign'].str.contains('_Enroll_')].copy()
for c in M:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
df['hits'] = [[(l, k, m) for l in lists_for(r.Campaign) for k, m in LISTS[l] if matches(r['Search term'], k, m)]
              for _, r in df.iterrows()]
df['blocked'] = df['hits'].map(bool)

s = df.groupby('blocked')[M].sum()
s['Cost/conv'] = (s['Cost'] / s['Conversions'].replace(0, float('nan'))).round(2)
print('Enroll campaigns: blocked (True) vs not blocked (False)')
print(s.round(2).to_string())
rows = [dict(list=l, keyword=k, match=m, **{c: r[c] for c in M}) for _, r in df[df.blocked].iterrows() for l, k, m in r['hits']]
if rows:
    kd = pd.DataFrame(rows).groupby(['list', 'keyword', 'match'])[M].sum()
    print('\nBlocked by keyword (a term matched by several keywords counts under each)')
    print(kd.sort_values(['Conversions', 'Cost'], ascending=False).round(2).to_string())

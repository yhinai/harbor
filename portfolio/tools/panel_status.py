from pathlib import Path
import collections,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'evidence/proxy/panel-v120-outcomes.json'
rows=json.loads(p.read_text()) if p.exists() else []
summary={}
for row in rows:
    s=summary.setdefault(row['task'],{}).setdefault(row['model'].split('/')[-1],{'passes':0,'valid':0,'excluded':collections.Counter()})
    if row['status']=='valid':s['valid']+=1;s['passes']+=row['reward']
    else:s['excluded'][row['status']]+=1
b=json.loads((ROOT/'evidence/proxy-budget.json').read_text())
print(json.dumps({'completed_attempts':len(rows),'expected_attempts':55,'results':summary,'total_conservative_booked_usd':b['conservative_booked_usd'],'known_usage_uncached_estimate_usd':sum(v.get('uncached_rate_estimate_usd',0) for v in b['requests'].values()),'unsettled_requests':sum(v['status']!='reported_usage' for v in b['requests'].values())},indent=2))

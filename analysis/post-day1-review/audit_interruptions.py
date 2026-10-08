import json,hashlib,datetime,zipfile
from pathlib import Path
root=Path('portfolio');rows=json.loads((root/'evidence/proxy/panel-v120-outcomes.json').read_text());ledger=json.loads((root/'evidence/proxy-budget.json').read_text());manifest=json.loads((root/'evidence/day1-amendment-v1.2.0.json').read_text())
with zipfile.ZipFile('day1-submission.zip') as z:
 for rel,want in manifest['artifact_sha256'].items():assert hashlib.sha256(z.read(rel)).hexdigest()==want and hashlib.sha256((root/rel).read_bytes()).hexdigest()==want
out=[]
for r in rows:
 if r['status']=='valid':continue
 events=[json.loads(l) for l in Path(r['trajectory_path']).read_text().splitlines()];initial=json.loads(Path(r['harbor_result_path']).read_text());meta=initial['agent_result']['metadata'];last_request=[e for e in events if e['kind']=='request'][-1];exceptions=[e for e in events if e['kind']=='exception'];last_tool=[e for e in events if e['kind']=='terminal_call'];trial=str(Path(r['trajectory_path']).parent)
 request_rows=[x for x in ledger['requests'].values() if x['trial']==trial];booked=sum(x['booked_usd'] for x in request_rows);q=last_request['payload'];rates={'kimi-k3':(3,15),'glm-5p3':(1.4,4.4),'deepseek-v4p1-flash':(.3,1.2)};a,b=rates[r['model'].split('/')[-1]];next_bound=1.25*((2*len(json.dumps(q,ensure_ascii=False).encode())+8192)*a+q['max_tokens']*b)/1e6
 delay=None
 if exceptions:delay=(datetime.datetime.fromisoformat(exceptions[-1]['time_utc'])-datetime.datetime.fromisoformat(last_request['time_utc'])).total_seconds()
 category='budget' if r['status']=='ProxyBudgetExceeded' else 'terminal_harness' if r['status']=='RuntimeError' else 'transport' if r['status']=='ProxyTransportFailure' else 'output'
 entry={'trial':r['trial_id'],'task':r['task'],'model':r['model'],'replicate':r['replicate'],'category':category,'exception_events':exceptions,'original_per_trial_cap_usd':meta['trial_cap_usd'],'booked_for_trial_usd':booked,'prospective_next_request_reservation_usd':next_bound,'request_to_exception_seconds':delay,'last_tool':last_tool[-1] if last_tool else None}
 if category=='budget':assert booked+next_bound>meta['trial_cap_usd'];entry['verified_trial_limit_not_project_limit']=True
 if category=='transport':
  chunks=[e for e in events if e['kind']=='stream_chunk']
  entry['stream_event_kinds']=sorted(set(e['kind'] for e in events))
  if not chunks:chunks=[e for e in events if e['kind']=='chunk']
  if chunks:
   gap=(datetime.datetime.fromisoformat(exceptions[-1]['time_utc'])-datetime.datetime.fromisoformat(chunks[-1]['time_utc'])).total_seconds()
   entry['last_chunk_to_deadline_seconds']=gap
   if 899<delay<901 and gap<1:entry['diagnosis']='Client absolute 900-second deadline while stream was active'
 if category=='output':entry['finish_reasons']=[e['response']['choices'][0]['finish_reason'] for e in events if e['kind']=='response'];assert 'length' in entry['finish_reasons']
 out.append(entry)
record={'label':'verified artifact audit; no paid calls','frozen_archive_matches_workspace':True,'original_attempts':55,'valid_passes':31,'excluded':24,'interruptions':out}
Path('analysis/post-day1-review/interruptions.json').write_text(json.dumps(record,indent=2)+'\n')
for x in out:print(x['category'],x['task'],x['model'].split('/')[-1],x['replicate'],'cap',x['original_per_trial_cap_usd'],'booked',round(x['booked_for_trial_usd'],3),'next',round(x['prospective_next_request_reservation_usd'],3),'delay',round(x['request_to_exception_seconds'] or 0,1))

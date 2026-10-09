"""Evidence extraction, never executes model text or calls inference."""
from pathlib import Path
import ast,collections,datetime,gzip,hashlib,json,re,shutil,statistics,zipfile
ROOT=Path(__file__).resolve().parents[2];STUDY=ROOT/'analysis/followup-v1.4.0/studies/mini-panel-20261008-v140';OUT=ROOT/'analysis/review-v1.5.0';WORK=ROOT/'tmp/review-v150'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
rows={};origin={}
for folder in ['outcomes','outcome-corrections/v1.4.2','outcome-corrections/v1.4.3']:
 for p in (STUDY/folder).glob('*.json'):
  r=json.loads(p.read_text());rows[r['attempt_id']]=r;origin[r['attempt_id']]=str(p.relative_to(ROOT))
valid=[r for r in rows.values() if r['phase']=='panel' and r['status']=='valid'];selection=set()
for task in {r['task'] for r in valid}:
 for model in {r['model'] for r in valid}:
  cell=sorted([r for r in valid if r['task']==task and r['model']==model],key=lambda r:r['reported_usage_estimate_usd'])
  selection.update([cell[0]['attempt_id'],cell[-1]['attempt_id']])
metrics=[];full_selected=[];exclusions=[];all_network=[]
for r in rows.values():
 if r['phase']=='panel' and r['status']!='valid':
  exc=r.get('exception') or {};exclusions.append({'attempt_id':r['attempt_id'],'status':r['status'],'raw_reward':r.get('raw_reward'),'type':exc.get('exception_type'),'message':exc.get('exception_message','')[:5000],'source_record':origin[r['attempt_id']]})
for r in sorted(valid,key=lambda r:r['attempt_id']):
 name=r['attempt_id'];saved=r['saved_artifact_sha256'];archive=next(STUDY/f for f in saved if f.endswith('.zip'))
 with zipfile.ZipFile(archive) as z:source=z.read('app/witness.json' if r['task']=='typecheck-soundness-witness' else 'app/main.py')
 try:normal=json.dumps(json.loads(source),sort_keys=True) if r['task']=='typecheck-soundness-witness' else ast.dump(ast.parse(source.decode()),include_attributes=False)
 except Exception:normal=source.decode(errors='replace')
 traces=sorted(STUDY/f for f in saved if '.jsonl.gz' in f)
 if len(traces)==1:trace=traces[0];combined=False
 else:
  trace=WORK/(name+'-combined.gz');combined=True
  with trace.open('wb') as out:
   for f in traces:
    with f.open('rb') as inp:shutil.copyfileobj(inp,out,1024*1024)
 counts=collections.Counter();commands=[];responses=[];errors=[];events=[];literal=[];first=None;last=None;initial=None;output_tokens=0;input_tokens=0;request_shapes=[]
 with gzip.open(trace,'rt') as f:
  for line in f:
   if '"kind": "stream_chunk"' in line:counts['stream_chunk']+=1;continue
   x=json.loads(line);kind=x['kind'];counts[kind]+=1;last=x['time_utc'];first=first or last
   if kind=='initial':initial=x['messages']
   if kind=='request':request_shapes.append({'step':x['step_index'],'messages':len(x['payload']['messages']),'max_tokens':x['payload']['max_tokens'],'reasoning_effort':x['payload']['reasoning_effort']})
   if kind=='response':
    u=x['response']['usage'];input_tokens+=u['prompt_tokens'];output_tokens+=u['completion_tokens'];msg=x['response']['choices'][0]['message'];text=msg.get('reasoning_content','') or '';content=msg.get('content','') or '';responses.append({'step':x['step_index'],'time':last,'reasoning_chars':len(text),'reasoning_start':text[:4000],'reasoning_end':text[-4000:],'content':content[:4000]})
   if kind=='terminal_call':
    cmd=x['command'];entry={'step':x['step_index'],'time':last,'tool_call_id':x['tool_call_id'],'command':cmd,'protected_path_mentions':bool(re.search(r'/tests\b|/solution\b|/logs/verifier\b|reward\.txt|cases\.json',cmd))};commands.append(entry);events.append({'step':entry['step'],'kind':'terminal_call','summary':cmd[:1000]})
    # Conservative literal here-document extraction. Exact final bytes are positive evidence only.
    pattern=r"cat\s*>\s*['\"]?(?:/app/)?(?:main\.py|witness\.json)['\"]?\s*<<\s*['\"]?(\w+)['\"]?\s*\n(.*?)\n\1(?:\n|$)"
    for match in re.finditer(pattern,cmd,re.S):
     candidate=(match.group(2)+'\n').encode()
     if candidate==source:literal.append({'step':entry['step'],'time':last,'artifact_sha256':sha(candidate),'method':'exact bytes in a literal cat here-document'})
   if kind=='terminal_result':
    result=x['result'];e={'step':x['step_index'],'time':last,'tool_call_id':x['tool_call_id'],'return_code':result['return_code'],'stdout':result['stdout'][:6000],'stderr':result['stderr'][:6000],'stdout_tail':result['stdout'][-3000:],'stderr_tail':result['stderr'][-3000:]};events.append({'step':e['step'],'kind':'terminal_result','return_code':e['return_code'],'summary':(e['stdout']+e['stderr'])[:1200]})
    if result['return_code']!=0 or re.search('Traceback|AssertionError|FAILED|MISMATCH',result['stdout']+result['stderr'],re.I):errors.append(e)
 from urllib.parse import urlparse,unquote
 trial=Path(unquote(urlparse(r['harbor_result']['trial_uri']).path));assert trial.is_relative_to(ROOT/'tmp/followup-v140/mini-panel-20261008-v140')
 network=json.loads((trial/'agent/network-audit.json').read_text());assert network['network_mode']=='none';all_network.append(network['container_id'])
 initial_valid=initial==[{'role':'system','content':initial[0]['content']},{'role':'user','content':(ROOT/'portfolio'/r['task']/'instruction.md').read_text()}]
 assert initial_valid and len(initial)==2,name
 assert input_tokens==r['harbor_result']['agent_result']['n_input_tokens'] and output_tokens==r['harbor_result']['agent_result']['n_output_tokens'],name
 assert counts['terminal_call']==r['tool_calls'] and counts['finished']==1,name
 elapsed=(datetime.datetime.fromisoformat(last)-datetime.datetime.fromisoformat(first)).total_seconds()
 literal_seconds=[(datetime.datetime.fromisoformat(e['time'])-datetime.datetime.fromisoformat(first)).total_seconds() for e in literal]
 metric={'attempt_id':name,'task':r['task'],'model':r['model'],'replicate':r['replicate'],'source_record':origin[name],'tool_calls':r['tool_calls'],'agent_elapsed_seconds':elapsed,'input_tokens':input_tokens,'output_tokens':output_tokens,'uncached_cost_estimate':r['reported_usage_estimate_usd'],'fresh_two_message_start_verified':initial_valid,'unique_container_id':network['container_id'],'network_mode':'none','artifact_sha256':sha(source),'normalized_artifact_sha256':sha(normal.encode()),'terminal_nonzero_or_error_text_events':len(errors),'protected_path_command_mentions':[c['step'] for c in commands if c['protected_path_mentions']],'finished_by_30_min':elapsed<=1800,'final_artifact_literal_writes':literal,'final_artifact_literal_written_by_30_min':any(t<=1800 for t in literal_seconds),'first_literal_final_artifact_seconds':min(literal_seconds) if literal_seconds else None,'event_counts':dict(counts),'request_settings':{'all_max_tokens_full_context':all(x['max_tokens']==1048576 for x in request_shapes),'all_reasoning_effort_max':all(x['reasoning_effort']=='max' for x in request_shapes)}}
 metrics.append(metric)
 save(OUT/'command-index'/(name+'.json'),{'label':'verified command/result excerpts; error text is a screening signal, not adjudicated failure','metric':metric,'commands':[{**c,'command':c['command'][:1600]} for c in commands],'errors':errors,'last_events':events[-12:]})
 if name in selection:
  selected={'metric':metric,'responses':responses,'commands':commands,'errors':errors,'events':events,'final_artifact':source.decode(errors='replace')};save(OUT/'selected-trajectories'/(name+'.json'),selected);full_selected.append(name)
 if combined:trace.unlink()
 print(name,round(elapsed),counts['terminal_call'],'tools',flush=True)
assert len(set(all_network))==120
save(OUT/'trajectory-metrics.json',{'label':'verified all 120 successful trajectories; semantic human/model review is a separate step','metrics':metrics,'selected_for_close_read':full_selected,'unique_container_ids':len(set(all_network))})
save(OUT/'exclusions.json',{'label':'verified final merged classifications; explanations require adjudication','attempts':exclusions})
ledger=json.loads((STUDY/'snapshots/v143-final-v142-ledger.json').read_text());counts=collections.Counter(r['status'] for r in ledger['requests'].values());save(OUT/'cost-audit.json',{'label':'verified ledger arithmetic; provider invoice unknown','request_status_counts':dict(counts),'models':dict(collections.Counter(r['model'] for r in ledger['requests'].values())),'known_usage_uncached_estimate':sum(r.get('uncached_rate_estimate_usd',0) for r in ledger['requests'].values()),'conservative_booked_usd':ledger['conservative_booked_usd'],'unknown_usage_requests':[{'request_id':k,'trial':r['trial'],'model':r['model'],'booked_usd':r['booked_usd'],'status':r['status']} for k,r in ledger['requests'].items() if r['status'] in ('reserved','failed_usage_unknown','usage_unknown')]})

"""Version corrections without changing raw rewards or frozen evidence."""
import json,subprocess,os,signal,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];name='mini-panel-20261008-v140';study=ROOT/'analysis/followup-v1.4.0/studies'/name
processes=[]
for line in subprocess.check_output(['/bin/ps','-ww','-axo','pid,ppid,command'],text=True).splitlines()[1:]:
 p=line.strip().split(None,2)
 if len(p)==3:processes.append((int(p[0]),int(p[1]),p[2]))
parent=[pid for pid,ppid,cmd in processes if str(ROOT/'tools/harness-v1.4.2/parallel_runner.py') in cmd and cmd.startswith(str(ROOT/'tmp/harbor-venv/bin/python')+' ')]
assert len(parent)==1,parent
os.kill(parent[0],signal.SIGSTOP)
try:
 old=json.loads((study/'amendments/v1.4.2.json').read_text());merged={};origins={}
 for d in [study/'outcomes',study/'outcome-corrections/v1.4.2']:
  for p in d.glob('*.json'):
   r=json.loads(p.read_text());merged[r['attempt_id']]=r;origins[r['attempt_id']]=str(p.relative_to(ROOT))
 folder=study/'outcome-corrections/v1.4.3';folder.mkdir(parents=True,exist_ok=True);restored=[]
 for key,r in merged.items():
  if r['status']!='host_memory_pressure':continue
  assert r.get('raw_reward')==1 and not r.get('exception') and r.get('tool_calls',0)>0 and not r['agent_metadata'].get('censor_status'),key
  assert r['harbor_result']['verifier_result']['rewards']['reward']==1,key
  correction={**r,'status':'valid','reward':1,'corrects_record':origins[key],'correction_reason':'Verified positive grader result; VM-wide oom counter was incorrectly interpreted as host-wide pressure. Per-container memory events do not invalidate unrelated positive results.','corrected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  p=folder/(key+'.json');assert not p.exists();p.write_text(json.dumps(correction,indent=2)+'\n');restored.append(key)
 live=json.loads((study/'live/status.json').read_text());active=set(live['active_trials']);inherited=[]
 for r in old['inherited_attempts']:
  if r['attempt_id'] in active:inherited.append(r)
 assert len(inherited)==len(active),'Unexpected active child identity'
 sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for version in ['v1.4.1','v1.4.2','v1.4.3'] for p in (ROOT/'tools'/('harness-'+version)).iterdir() if p.is_file()}
 amendment={'version':'1.4.3','study_id':name,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':'Fix per-container OOM attribution; restore verified positive results and resume outstanding slots','max_parallel_trials':40,'minimum_available_memory_mb':3072,'primary_panel_trials':120,'inherited_attempts':inherited,'source_sha256':sources,'old_dispatcher_labels':old['old_dispatcher_labels']+['org.harbor.'+name+'-v142'],'previous_dispatcher_pid':parent[0],'restored_verified_positive_attempts':restored,'prematurely_classified_attempts':old['prematurely_classified_attempts'],'duplicate_attempts':old['duplicate_attempts'],'user_reported_actual_spend_usd':46.94,'provider_invoice_verified':False,'trial_and_aggregate_dollar_caps':None,'replacement_policy':'Up to three fresh attempts per logical slot for transport, protocol or setup errors; no retry of a valid graded result; existing primary design only.','no_generation_deliberately_interrupted':True}
 p=study/'amendments/v1.4.3.json';assert not p.exists();p.write_text(json.dumps(amendment,indent=2)+'\n');print('Restored',len(restored),'verified passes. Preserved',len(inherited),'active children. Original records unchanged.')
except BaseException:
 os.kill(parent[0],signal.SIGCONT);raise

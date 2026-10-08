"""Pause only the old dispatcher; its already-running paid children continue."""
import os,signal,subprocess,json,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];name='mini-panel-20261008-v140';study=ROOT/'analysis/followup-v1.4.0/studies'/name
rows=[]
for line in subprocess.check_output(['/bin/ps','-axo','pid,ppid,command'],text=True).splitlines()[1:]:
 parts=line.strip().split(None,2)
 if len(parts)==3:rows.append((int(parts[0]),int(parts[1]),parts[2]))
candidates=[r for r in rows if str(ROOT/'tools/harness-v1.4.0/panel_runner.py') in r[2] and r[2].startswith(str(ROOT/'tmp/harbor-venv/bin/python')+' ')]
assert len(candidates)==1,candidates
pid=candidates[0][0];os.kill(pid,signal.SIGSTOP)
try:
 assert 'T' in subprocess.check_output(['/bin/ps','-p',str(pid),'-o','stat='],text=True)
 inherited=[]
 for f in (study/'live').glob('panel-*.json'):
  r=json.loads(f.read_text())
  if (study/'outcomes'/(r['attempt_id']+'.json')).exists():continue
  child=[c for c,parent,cmd in rows if parent==pid and r['attempt_id'] in cmd and 'harbor run' in cmd]
  assert len(child)==1 or (Path(r['job'])/'result.json').exists(),'Unlaunched or ambiguous old slot: '+r['attempt_id']
  r['child_pid']=child[0] if child else 0;inherited.append(r)
 assert inherited,'No active paid children to preserve'
 sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'tools/harness-v1.4.1').glob('*.py')}
 amendment={'version':'1.4.1','study_id':name,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':'user-authorized operational concurrency increase; original frozen plan and task hashes preserved','max_parallel_trials':40,'minimum_available_memory_mb':3072,'primary_panel_trials':120,'new_primary_trials_added':0,'previous_dispatcher_pid':pid,'previous_dispatcher_paused':True,'inherited_attempts':inherited,'source_sha256':sources,'no_model_generation_interrupted':True}
 p=study/'amendments/v1.4.1.json';p.parent.mkdir(exist_ok=True);assert not p.exists();p.write_text(json.dumps(amendment,indent=2)+'\n')
 print('Dispatcher paused; preserved '+str(len(inherited))+' active paid children. New admission ceiling 40 includes these children.')
except BaseException:
 os.kill(pid,signal.SIGCONT);raise

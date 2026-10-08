import json,subprocess,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];name='mini-panel-20261008-v140';study=ROOT/'analysis/followup-v1.4.0/studies'/name
old=json.loads((study/'amendments/v1.4.1.json').read_text());parents=[old['previous_dispatcher_pid'],28042]
for pid in parents:assert 'T' in subprocess.check_output(['/bin/ps','-p',str(pid),'-o','stat='],text=True),'Dispatcher is not paused'
processes=[]
for line in subprocess.check_output(['/bin/ps','-axo','pid,ppid,command'],text=True).splitlines()[1:]:
 p=line.strip().split(None,2)
 if len(p)==3:processes.append((int(p[0]),int(p[1]),p[2]))
wrong={r['attempt_id'] for r in old['inherited_attempts']};inherited=[]
for p in (study/'live').glob('panel-*.json'):
 r=json.loads(p.read_text());name_=r['attempt_id']
 if name_ not in wrong and (study/'outcomes'/(name_+'.json')).exists():continue
 child=[pid for pid,parent,cmd in processes if parent in parents and name_ in cmd and 'harbor run' in cmd]
 assert len(child)==1 or list(Path(r['job']).glob('*/result.json')),'No process or actual trial result for '+name_
 r['child_pid']=child[0] if child else 0;inherited.append(r)
groups={}
for r in inherited:groups.setdefault((r['model'],r['task'],r['replicate']),[]).append(r)
duplicates=[r['attempt_id'] for rows in groups.values() for r in sorted(rows,key=lambda x:x['attempt'])[1:]]
sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['tools/harness-v1.4.1','tools/harness-v1.4.2'] for p in (ROOT/folder).glob('*.py')}
amend={'version':'1.4.2','study_id':name,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':'correct premature handoff accounting; preserve original records and all active paid streams','max_parallel_trials':40,'minimum_available_memory_mb':3072,'primary_panel_trials':120,'inherited_attempts':inherited,'prematurely_classified_attempts':sorted(wrong),'duplicate_attempts':duplicates,'old_dispatcher_labels':['org.harbor.'+name,'org.harbor.'+name+'-v141'],'source_sha256':sources,'no_generation_deliberately_interrupted':True,'temporary_active_overshoot':len(inherited),'duplicate_policy':'original a1 is primary regardless of outcome; a2 scheduler duplicates excluded regardless of outcome; corrections versioned separately'}
p=study/'amendments/v1.4.2.json';assert not p.exists();p.write_text(json.dumps(amend,indent=2)+'\n');print('Preserved',len(inherited),'paid children;',len(duplicates),'scheduler duplicates are excluded. New dispatch waits until fewer than 40 active.')

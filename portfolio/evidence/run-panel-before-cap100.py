"""Resumable, bounded Harbor proxy runs. Never selects a frontier model.
Usage: python tools/run_panel.py --phase smoke
       python tools/run_panel.py --phase panel
The panel uses 5 Kimi, 3 GLM, and 3 DeepSeek trials per task. Smokes are excluded
from those counts. No model is selected/removed based on a task's reward.
"""
from pathlib import Path
import argparse,asyncio,datetime,hashlib,json,os,sys,tomllib
from fireworks_agent import Budget,ROOT
MODELS={
 'kimi':{'id':'accounts/fireworks/models/kimi-k3','effort':'max','trials':5,'cap':4},
 'glm':{'id':'accounts/fireworks/models/glm-5p3','effort':'high','trials':3,'cap':2},
 'deepseek':{'id':'accounts/fireworks/models/deepseek-v4p1-flash','effort':'high','trials':3,'cap':1},
}
from selection import SLUGS

def hashes():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for slug in SLUGS for p in sorted((ROOT/slug).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
def collect(job,phase,slug,short,index):
 files=list(job.glob('*/result.json'))
 if len(files)!=1: return {'task':slug,'model':MODELS[short]['id'],'trial_id':job.name,'status':'missing_trial_result','reward':None,'version':'1.1.0','phase':phase}
 path=files[0]; data=json.loads(path.read_text()); meta=(data.get('agent_result') or {}).get('metadata') or {}; exc=data.get('exception_info')
 status=meta.get('censor_status') or (exc or {}).get('exception_type')
 reward=((data.get('verifier_result') or {}).get('rewards') or {}).get('reward')
 verpath=path.parent/'verifier/status.json'; verifier=json.loads(verpath.read_text()) if verpath.is_file() else None
 if verifier and verifier.get('status')=='infrastructure_error': status='verifier_infrastructure_error'
 if not status and (not meta.get('tool_calls') or reward not in (0,1)): status='missing_real_work_or_reward'
 return {'label':'verified','task':slug,'model':MODELS[short]['id'],'trial_id':data['trial_name'],'status':status or 'valid','reward':reward if not status else None,'version':'1.1.0','phase':phase,'replicate':index,'trajectory_path':str((path.parent/'agent/complete-trajectory.jsonl').resolve()),'harbor_result_path':str(path.resolve()),'tool_calls':meta.get('tool_calls',0),'provider_usage_cost_estimate_usd':(data.get('agent_result') or {}).get('cost_usd'),'verifier_status':verifier}

async def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--phase',choices=['smoke','panel'],required=True); ap.add_argument('--workers',type=int,default=3); args=ap.parse_args()
 if not 1<=args.workers<=14: raise SystemExit('workers must be 1..14')
 if Budget().change(lambda d:d.get('halted')): raise SystemExit('Paid runs are on user hold. Explicit confirmation of the final five is required before the hold is cleared.')
 amend=ROOT/'evidence/day1-amendment-v1.1.0.json'
 if not amend.is_file(): raise SystemExit('Freeze and validate the amended packages before paid trials.')
 frozen=json.loads(amend.read_text()); expected=frozen['task_sha256']
 if hashes()!=expected: raise SystemExit('Task files changed since the amendment; stop and document a new version.')
 jobroot=ROOT.parent/'tmp/harbor-jobs'; jobroot.mkdir(parents=True,exist_ok=True)
 evidence=ROOT/'evidence/proxy'; evidence.mkdir(exist_ok=True)
 results={}; sem=asyncio.Semaphore(args.workers)
 env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'tools')
 harbor=Path(sys.executable).parent/'harbor'
 if not harbor.exists(): raise SystemExit('Run this with the Python environment containing Harbor.')
 def save():
  p=evidence/(args.phase+'-v120-outcomes.json'); tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(list(results.values()),indent=2)+'\n'); tmp.replace(p)
 async def run(slug,short,index):
  model=MODELS[short]; name=f'{args.phase}-v120-{short}-{slug}-{index}'
  async with sem:
   if hashes()!=expected: raise RuntimeError('Task version changed during the panel.')
   job=jobroot/name
   if not (job/'result.json').is_file():
    # The client reserves every call against both limits; this is an early stop.
    if Budget().change(lambda d:d['conservative_booked_usd'])>=169: raise RuntimeError('Operational budget exhausted')
    cmd=[str(harbor),'run','-p',str(ROOT/slug),'-a','fireworks_agent:FireworksAgent','-m',model['id'],'--ak',f"trial_cap={model['cap']}",'--ak',f"reasoning_effort={model['effort']}",'--ak','max_tokens=65536','--jobs-dir',str(jobroot),'--job-name',name,'-n','1','--quiet']
    if args.phase=='smoke':cmd += ['--ak','smoke_only=true']
    print('Starting',name,flush=True)
    with (evidence/(name+'.log')).open('w') as log:
     process=await asyncio.create_subprocess_exec(*cmd,env=env,stdout=log,stderr=asyncio.subprocess.STDOUT)
     try: await process.wait()
     except asyncio.CancelledError:
      process.terminate(); await process.wait(); raise
   row=collect(job,args.phase,slug,short,index); results[name]=row; save()
   print('Finished',name,row['status'],'reward=',row['reward'],flush=True)
 if args.phase=='smoke':
  plans=[('atomic-range-history',m,1) for m in MODELS]
 else:
  smoke=evidence/'smoke-v120-outcomes.json'
  if not smoke.exists(): raise SystemExit('Run capability smokes first.')
  smoke_rows=json.loads(smoke.read_text()); enabled=[]
  for short,model in MODELS.items():
   rows=[r for r in smoke_rows if r['model']==model['id']]
   if len(rows)==1 and rows[0]['status']=='valid' and rows[0]['tool_calls']>0: enabled.append(short)
   else: print('Excluded from panel after incompatible or unresolved smoke:',short,flush=True)
  if not enabled: raise SystemExit('No completed compatible smoke; no model-failure evidence.')
  plans=[(s,m,i) for i in range(1,6) for s in SLUGS for m in enabled if i<=MODELS[m]['trials']]
 await asyncio.gather(*(run(*plan) for plan in plans))
 print('Finished phase',args.phase,'booked upper estimate:',Budget().change(lambda d:d['conservative_booked_usd']),flush=True)
if __name__=='__main__': asyncio.run(main())

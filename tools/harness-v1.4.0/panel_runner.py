"""Finite independent proxy study, supervised on mini. No frontier client exists."""
from pathlib import Path
import argparse,asyncio,datetime,fcntl,gzip,hashlib,json,os,re,shutil,subprocess,sys,uuid,zipfile
ROOT=Path(__file__).resolve().parents[2];TOOLS=Path(__file__).resolve().parent
from fireworks_agent_v140 import Budget
MODELS={'kimi':'accounts/fireworks/models/kimi-k3','glm':'accounts/fireworks/models/glm-5p3','deepseek':'accounts/fireworks/models/deepseek-v4p1-flash'}
SLUGS=['typecheck-soundness-witness','exact-fused-dot','mixed-width-tso','checkpointed-journal','atomic-range-history']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,data):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(data,indent=2)+'\n');t.replace(p)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Study:
 def __init__(self,name):
  self.path=ROOT/'analysis/followup-v1.4.0/studies'/name;self.plan=json.loads((self.path/'plan.json').read_text());self.jobs=ROOT/'tmp/followup-v140'/name;self.jobs.mkdir(parents=True,exist_ok=True)
  self.live=self.path/'live';self.live.mkdir(exist_ok=True);self.ledger=self.live/'budget.json';self.active={};self.halt=None;self.git_error=None;self.last_sync=0;self.sem=asyncio.Semaphore(self.plan['max_parallel_trials']);self.git_lock=asyncio.Lock();self.done=[];self.state="running"
  for d in ['outcomes','trajectories','artifacts','snapshots']: (self.path/d).mkdir(exist_ok=True)
  self.env=os.environ.copy();self.env.update(PYTHONPATH=str(TOOLS),FIREWORKS_ENV_FILE=str(ROOT/'.env'),PORTFOLIO_BUDGET_LEDGER=str(self.ledger),HARNESS_PAID_RUNS_ENABLED='explicitly-authorized')
  for k in ['SUDO_PASSWORD','FIREWORKS_API_KEY']:self.env.pop(k,None)
  self.env['PATH']=str(Path.home()/'.local/harbor-runtime/bin')+':'+self.env.get('PATH','/usr/bin:/bin');self.env['DOCKER_CONFIG']=str(Path.home()/'.local/harbor-runtime/docker-config');self.env['DOCKER_HOST']='unix://'+str(Path.home()/'.colima/frontier-portfolio/docker.sock')
 def check(self):
  for f,h in self.plan['task_sha256'].items():assert digest(ROOT/'portfolio'/f)==h,'Frozen task changed: '+f
  for f,h in self.plan['source_sha256'].items():assert digest(ROOT/f)==h,'Preregistered harness changed: '+f
 def status(self,state=None):
  if state is not None:self.state=state
  state=self.state
  rows=[json.loads(p.read_text()) for p in (self.path/'outcomes').glob('*.json')];self.done=rows
  paid=json.loads(self.ledger.read_text()) if self.ledger.exists() else {}
  atomic(self.live/'status.json',{'state':state,'time_utc':now(),'active_trials':self.active,'finished_attempts':len(rows),'valid_panel_trials':sum(r['phase']=='panel' and r['status']=='valid' for r in rows),'panel_passes':sum(r['phase']=='panel' and r['status']=='valid' and r['reward']==1 for r in rows),'halt':self.halt,'git_error':self.git_error,'conservative_booked_usd':paid.get('conservative_booked_usd',0),'reported_usage_estimate_usd':sum(r.get('uncached_rate_estimate_usd',0) for r in paid.get('requests',{}).values()),'usage_unknown_requests':sum(r['status'] in ('reserved','failed_usage_unknown','usage_unknown') for r in paid.get('requests',{}).values())})
 async def heartbeat(self):
  while True:self.status();await asyncio.sleep(30)
 async def memory_gate(self):
  while True:
   if self.halt:return False
   proc=await asyncio.create_subprocess_exec('colima','ssh','--profile','frontier-portfolio','--','cat','/proc/meminfo',env=self.env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   out,err=await proc.communicate()
   if proc.returncode:raise RuntimeError('Cannot inspect VM memory; dispatch paused')
   available=int(re.search(rb'MemAvailable:\s+(\d+)',out).group(1))//1024
   if available>=self.plan['minimum_available_memory_mb'] and shutil.disk_usage(ROOT).free>10*1024**3:return True
   self.status();await asyncio.sleep(5)
 def pack(self,trial,name):
  p=trial/'agent/complete-trajectory.jsonl';files=[]
  if p.exists():
   target=self.path/'trajectories'/(name+'.jsonl.gz');temp=target.with_suffix('.tmp')
   with p.open('rb') as src,gzip.open(temp,'wb',compresslevel=3) as dest:shutil.copyfileobj(src,dest,1024*1024)
   temp.replace(target)
   if target.stat().st_size>40*1024**2:
    with target.open('rb') as src:
     i=0
     while data:=src.read(40*1024**2):
      part=target.with_name(target.name+f'.part{i:03d}');part.write_bytes(data);files.append(part);i+=1
    target.unlink()
   else:files.append(target)
  artifacts=trial/'artifacts'
  if artifacts.exists():
   dest=self.path/'artifacts'/(name+'.zip');temp=dest.with_suffix('.tmp')
   with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
    for f in artifacts.rglob('*'):
     if f.is_file() and not f.is_symlink():z.write(f,f.relative_to(artifacts))
   temp.replace(dest);files.append(dest)
  return {str(p.relative_to(self.path)):digest(p) for p in files}
 def collect(self,job,name,phase,model,slug,rep,attempt):
  paths=list(job.glob('*/result.json'));base={'attempt_id':name,'phase':phase,'model':MODELS[model],'task':slug,'replicate':rep,'attempt':attempt,'time_utc':now()}
  if len(paths)!=1:
   partial={}
   for t in job.iterdir() if job.exists() else []:
    if t.is_dir():partial.update(self.pack(t,name))
   return {**base,'status':'missing_trial_result','reward':None,'saved_artifact_sha256':partial}
  path=paths[0];r=json.loads(path.read_text());meta=(r.get('agent_result') or {}).get('metadata') or {};exc=r.get('exception_info');status=meta.get('censor_status') or (exc or {}).get('exception_type');reward=((r.get('verifier_result') or {}).get('rewards') or {}).get('reward')
  if not status and (not meta.get('tool_calls') or reward not in (0,1)):status='missing_work_or_reward'
  v=path.parent/'verifier/status.json'
  if v.exists() and json.loads(v.read_text()).get('status')=='infrastructure_error':status='verifier_infrastructure_error'
  return {**base,'status':status or 'valid','reward':None if status else reward,'raw_reward':reward,'tool_calls':meta.get('tool_calls',0),'exception':exc,'agent_metadata':meta,'reported_usage_estimate_usd':(r.get('agent_result') or {}).get('cost_usd'),'harbor_result':r,'saved_artifact_sha256':self.pack(path.parent,name)}
 async def sync(self,tag):
  async with self.git_lock:
   self.status();status=json.loads((self.live/'status.json').read_text());atomic(self.path/'snapshots'/(tag+'-status.json'),status)
   if self.ledger.exists():atomic(self.path/'snapshots'/(tag+'-ledger.json'),json.loads(self.ledger.read_text()))
   if self.git_error:return
   def git(*args):return subprocess.run(['git',*args],cwd=ROOT,env=self.env,capture_output=True,text=True,timeout=60)
   staged=git('diff','--cached','--name-only')
   changed=git('diff','--name-only').stdout.splitlines()
   allowed=str(self.path.relative_to(ROOT))+'/'
   if staged.stdout.strip() or any(not f.startswith(allowed) and f!='PROJECT_STATUS.md' for f in changed):self.git_error='Unrelated work present; automatic staging skipped';return
   with (ROOT/'PROJECT_STATUS.md').open('a') as f:f.write('\n**Verified unattended v1.4.0 milestone '+tag+' ('+now()+'):** '+str(status['valid_panel_trials'])+' graded panel trials; '+str(status['finished_attempts'])+' finished attempts including smokes/exclusions. See `'+str(self.path.relative_to(ROOT))+'`. Reported-usage estimate $'+format(status['reported_usage_estimate_usd'],'.4f')+'; invoice unknown. Original freeze unchanged.\n')
   for args in [('add',str(self.path/'outcomes'),str(self.path/'trajectories'),str(self.path/'artifacts'),str(self.path/'snapshots'),str(self.path/'smoke-compatibility.json'),'PROJECT_STATUS.md'),('commit','-m','Record unattended proxy milestone '+tag),('push','origin','main')]:
    r=await asyncio.to_thread(git,*args)
    if r.returncode:self.git_error='Git '+args[0]+' failed: '+r.stderr[-1000:];self.status();return
   local=git('rev-parse','HEAD').stdout.strip();remote=git('ls-remote','origin','refs/heads/main').stdout.split()
   if not remote or remote[0]!=local:self.git_error='Remote commit verification failed'
   self.status()
 async def run_attempt(self,phase,model,slug,rep,attempt):
  async with self.sem:
   if not await self.memory_gate():return None
   self.check();name=f'{phase}-{model}-{slug}-{rep}-a{attempt}-{uuid.uuid4().hex[:8]}';job=self.jobs/name
   self.active[name]={'model':model,'task':slug,'phase':phase,'started_utc':now()};atomic(self.live/(name+'.json'),{'attempt_id':name,'job':str(job),'phase':phase,'model':model,'task':slug,'replicate':rep,'attempt':attempt,'state':'started'});self.status()
   artifact='/app/witness.json' if slug=='typecheck-soundness-witness' else '/app/main.py'
   cmd=[str(Path(sys.executable).parent/'harbor'),'run','-p',str(ROOT/'portfolio'/slug),'-a','fireworks_agent_v140:FireworksAgent','-m',MODELS[model],'--ak','reasoning_effort=max','--ak','max_tokens=1048576','--ak','max_turns=1000','--agent-timeout-multiplier','48','--verifier-timeout-multiplier','4','--extra-docker-compose',str(TOOLS/'offline-network.yaml'),'--artifact',artifact,'--jobs-dir',str(self.jobs),'--job-name',name,'-n','1','--quiet']
   if phase=='smoke':cmd+=['--ak','smoke_only=true']
   print('Starting',name,flush=True)
   with (self.live/(name+'.log')).open('w') as log:
    proc=await asyncio.create_subprocess_exec(*cmd,env=self.env,stdout=log,stderr=asyncio.subprocess.STDOUT)
    await proc.wait()
   row=self.collect(job,name,phase,model,slug,rep,attempt);atomic(self.path/'outcomes'/(name+'.json'),row);self.active.pop(name,None);self.status();print('Finished',name,row['status'],row['reward'],flush=True)
   if row.get('exception') and any('HTTP '+str(n) in row['exception'].get('exception_message','') for n in [401,402,403]):self.halt='Provider credentials/billing rejection; new dispatch stopped'
   return row
 async def slot(self,model,slug,rep):
  rows=[r for r in self.done if r['phase']=='panel' and r['model']==MODELS[model] and r['task']==slug and r['replicate']==rep]
  if any(r['status']=='valid' for r in rows):return
  used=max((r['attempt'] for r in rows),default=0)
  for attempt in range(used+1,4):
   row=await self.run_attempt('panel',model,slug,rep,attempt)
   if row is None:return
   total=sum(r['phase']=='panel' for r in self.done)
   if total>=self.last_sync+20:self.last_sync=total;await self.sync('panel-'+str(total))
   if row['status']=='valid':return
   # Only operational interruptions get a fresh independent replacement.
   if row['status'] not in ['ProxyTransportFailure','ProxyHTTPFailure','ProxyStreamInactivity','RuntimeError','missing_trial_result','InterruptedHostProcess']:return
 def summarize(self):
  self.status();summary={'time_utc':now(),'label':'verified graded rewards; operational exclusions separate; invoice unknown','tasks':{}}
  for slug in SLUGS:
   summary['tasks'][slug]={}
   for m,mid in MODELS.items():
    rows=[r for r in self.done if r['phase']=='panel' and r['model']==mid and r['task']==slug]
    good=[r for r in rows if r['status']=='valid'];n=len(good);k=sum(r['reward']==1 for r in good)
    excluded={}
    for r in rows:
     if r['status']!='valid':excluded[r['status']]=excluded.get(r['status'],0)+1
    summary['tasks'][slug][m]={'passes':k,'valid_trials':n,'planned_trials':8,'excluded_attempts':excluded}
  atomic(self.path/'snapshots/final-reward-summary.json',summary)
 async def recover(self):
  # Preserve unfinished attempts as interruptions. Never replay an ambiguous API request.
  from harbor.environments.docker.docker import _sanitize_docker_compose_project_name
  for p in self.live.glob('*.json'):
   if p.name in ('status.json','budget.json'):continue
   r=json.loads(p.read_text())
   if not isinstance(r,dict):continue
   name=r.get('attempt_id')
   if not name or (self.path/'outcomes'/(name+'.json')).exists():continue
   job=Path(r['job'])
   for trial in job.iterdir() if job.exists() else []:
    if not trial.is_dir():continue
    project=_sanitize_docker_compose_project_name(trial.name)
    ids=subprocess.check_output(['docker','ps','-aq','--filter','label=com.docker.compose.project='+project],env=self.env,text=True).split()
    if ids:subprocess.run(['docker','rm','-f',*ids],env=self.env,check=True,capture_output=True)
   row=self.collect(job,name,r['phase'],r['model'],r['task'],r['replicate'],r['attempt'])
   if row['status']=='missing_trial_result':row.update(status='InterruptedHostProcess',reward=None)
   atomic(self.path/'outcomes'/(name+'.json'),row)
  self.status()
 async def run(self):
  self.check();await self.recover();heartbeat=asyncio.create_task(self.heartbeat())
  try:
   smokes={}
   for m in MODELS:
    rows=[r for r in self.done if r['phase']=='smoke' and r['model']==MODELS[m] and r['status']=='valid']
    if rows:smokes[m]=rows[-1]
   pending=[m for m in MODELS if m not in smokes]
   results=await asyncio.gather(*(self.run_attempt('smoke',m,'atomic-range-history',1,1) for m in pending))
   for m,r in zip(pending,results):
    if r and r['status']=='valid' and r['tool_calls']>0:smokes[m]=r
   atomic(self.path/'smoke-compatibility.json',{'label':'verified actual tool-use smokes; excluded from pass-rate denominators','enabled':list(smokes),'dropped_or_unresolved':[m for m in MODELS if m not in smokes]});await self.sync('smokes')
   if not smokes:
    self.halt='No compatible smoke';self.status('blocked');await self.sync('blocked-no-smokes');return
   plans=[(m,s,r) for r in range(1,9) for s in SLUGS for m in smokes]
   await asyncio.gather(*(self.slot(*p) for p in plans))
   self.check();self.summarize();self.status('completed' if not self.halt else 'blocked');await self.sync('final')
   self.status('completed' if not self.halt else 'blocked')
  finally:heartbeat.cancel()
async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--study-id',required=True);a=ap.parse_args();assert re.fullmatch('[A-Za-z0-9_-]+',a.study_id)
 s=Study(a.study_id);lock=(s.live/'supervisor.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old=json.loads((s.live/'status.json').read_text()) if (s.live/'status.json').exists() else {}
 if old.get('state') in ('completed','blocked'):print('Study already completed; no new requests');return
 restarts=s.live/'supervisor-starts.json';starts=json.loads(restarts.read_text()) if restarts.exists() else []
 starts.append(now());atomic(restarts,starts)
 if len(starts)>5:s.halt='Five supervisor recoveries exhausted; preserve evidence for inspection';s.status('blocked');return
 try:await s.run()
 except BaseException as ex:s.halt=type(ex).__name__+': '+str(ex);s.status('failed');raise
if __name__=='__main__':asyncio.run(main())

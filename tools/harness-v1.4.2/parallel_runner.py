"""Correct completion detection; preserve paid streams and exclude duplicates."""
from pathlib import Path
import sys,asyncio,json,subprocess,fcntl,argparse,re,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/harness-v1.4.1'))
from parallel_runner import Study as PreviousStudy
from panel_runner import Study as OriginalStudy,atomic,now,MODELS,SLUGS
class Study(PreviousStudy):
 def __init__(self,name):
  super().__init__(name);self.amend=json.loads((self.path/'amendments/v1.4.2.json').read_text());self.external={r['attempt_id']:r for r in self.amend['inherited_attempts']};self.wrong=set(self.amend['prematurely_classified_attempts']);self.duplicates=set(self.amend['duplicate_attempts']);self.corrections=self.path/'outcome-corrections/v1.4.2';self.corrections.mkdir(parents=True,exist_ok=True)
 def status(self,state=None):
  OriginalStudy.status(self,state)
  rows={r['attempt_id']:r for r in self.done}
  for p in self.corrections.glob('*.json'):r=json.loads(p.read_text());rows[r['attempt_id']]=r
  self.done=list(rows.values());p=self.live/'status.json';d=json.loads(p.read_text());d.update(operational_version='1.4.2',max_parallel_trials=40,minimum_available_memory_mb=3072,finished_attempts=len(self.done),valid_panel_trials=sum(r['phase']=='panel' and r['status']=='valid' for r in self.done),panel_passes=sum(r['phase']=='panel' and r['status']=='valid' and r['reward']==1 for r in self.done));atomic(p,d)
 def collect(self,job,name,phase,model,slug,rep,attempt):
  artifactname=name+'-v142' if name in self.wrong else name
  row=OriginalStudy.collect(self,job,artifactname,phase,model,slug,rep,attempt);row['attempt_id']=name
  if name in self.wrong:row['corrects_premature_bookkeeping']=str((self.path/'outcomes'/(name+'.json')).relative_to(ROOT))
  if name in self.duplicates:row.update(underlying_status=row['status'],status='scheduler_duplicate',reward=None)
  if name in self.pressure:
   row['host_memory_pressure']=self.pressure[name]
   if row['status']=='valid':row.update(status='host_memory_pressure',reward=None)
  return row
 async def run_attempt(self,phase,model,slug,rep,attempt):
  async with self.sem:
   if not await self.memory_gate():return None
   self.check();name=f'{phase}-{model}-{slug}-{rep}-a{attempt}-{uuid.uuid4().hex[:8]}';job=self.jobs/name
   self.active[name]={'model':model,'task':slug,'phase':phase,'started_utc':now()};atomic(self.live/(name+'.json'),{'attempt_id':name,'job':str(job),'phase':phase,'model':model,'task':slug,'replicate':rep,'attempt':attempt,'state':'started'});self.status()
   artifact='/app/witness.json' if slug=='typecheck-soundness-witness' else '/app/main.py'
   cmd=[str(Path(sys.executable).parent/'harbor'),'run','-p',str(ROOT/'portfolio'/slug),'-a','fireworks_agent_v140:FireworksAgent','-m',MODELS[model],'--ak','reasoning_effort=max','--ak','max_tokens=1048576','--ak','max_turns=1000','--agent-timeout-multiplier','48','--verifier-timeout-multiplier','4','--extra-docker-compose',str(ROOT/'tools/harness-v1.4.2/offline-network.yaml'),'--artifact',artifact,'--jobs-dir',str(self.jobs),'--job-name',name,'-n','1','--quiet']
   if phase=='smoke':cmd+=['--ak','smoke_only=true']
   print('Starting',name,flush=True)
   with (self.live/(name+'.log')).open('w') as log:
    proc=await asyncio.create_subprocess_exec(*cmd,env=self.env,stdout=log,stderr=asyncio.subprocess.STDOUT)
    await proc.wait()
   row=self.collect(job,name,phase,model,slug,rep,attempt);atomic(self.path/'outcomes'/(name+'.json'),row);self.active.pop(name,None);self.status();print('Finished',name,row['status'],row['reward'],flush=True)
   if row.get('exception') and any('HTTP '+str(n) in row['exception'].get('exception_message','') for n in [401,402,403]):self.halt='Provider credentials/billing rejection; new dispatch stopped'
   return row
 async def child_running(self,r):
  p=await asyncio.create_subprocess_exec('/bin/ps','-ww','-p',str(r['child_pid']),'-o','stat=','-o','command=',stdout=asyncio.subprocess.PIPE)
  out,_=await p.communicate();text=out.decode().strip()
  return not p.returncode and bool(text) and not text.startswith('Z') and r['attempt_id'] in text
 async def inherit(self,r):
  name=r['attempt_id'];out=self.corrections/(name+'.json') if name in self.wrong or name in self.duplicates else self.path/'outcomes'/(name+'.json')
  if not out.exists():
   print('Preserving actual running child',name,flush=True)
   while await self.child_running(r):await asyncio.sleep(5)
   row=self.collect(Path(r['job']),name,r['phase'],r['model'],r['task'],r['replicate'],r['attempt'])
   if row['status']=='missing_trial_result':row.update(status='InterruptedHostProcess',reward=None)
   atomic(out,row);print('Collected child after process exit',name,row['status'],row['reward'],flush=True)
  self.active.pop(name,None);self.status()
 async def inherit_all(self):
  await asyncio.gather(*(self.inherit(r) for r in self.external.values()))
  await self.retire_old_dispatcher()
  keys={(r['model'],r['task'],r['replicate']) for r in self.external.values()}
  await asyncio.gather(*(self.slot(*key) for key in keys))
 async def retire_old_dispatcher(self):
  from dotenv import dotenv_values
  password=dotenv_values(ROOT/'.env').get('SUDO_PASSWORD');assert password
  rows=[]
  for label in self.amend['old_dispatcher_labels']:
   r=await asyncio.to_thread(subprocess.run,['sudo','-S','-p','','launchctl','bootout','system/'+label],input=password+'\n',text=True,capture_output=True,timeout=90);rows.append({'label':label,'exit_code':r.returncode})
  atomic(self.path/'snapshots/v142-dispatcher-retirement.json',{'time_utc':now(),'results':rows,'label':'all inherited children exited before retired dispatcher removal'})
 async def monitor_resources(self):
  baseline=None
  while True:
   p=await asyncio.create_subprocess_exec('colima','ssh','--profile','frontier-portfolio','--','cat','/proc/meminfo','/proc/vmstat',env=self.env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   out,_=await asyncio.wait_for(p.communicate(),60)
   if p.returncode:self.halt='VM resource monitor failed; new dispatch stopped';self.status();return
   available=int(re.search(rb'MemAvailable:\s+(\d+)',out).group(1))//1024;oom=int(re.search(rb'oom_kill\s+(\d+)',out).group(1))
   if baseline is None:baseline=oom
   atomic(self.live/'v142-resource-sample.json',{'time_utc':now(),'available_memory_mb':available,'oom_kill_counter':oom,'active_trials':len(self.active)})
   if available<1536 or oom>baseline:
    event={'time_utc':now(),'available_memory_mb':available,'oom_kill_counter':oom}
    for name in self.active:self.pressure.setdefault(name,[]).append(event)
    atomic(self.live/'v141-memory-pressure.json',self.pressure);atomic(self.path/'snapshots/v142-memory-pressure.json',self.pressure)
    if oom>baseline:self.halt='Kernel memory termination; new dispatch stopped'
    baseline=oom
   await asyncio.sleep(10)
 async def run(self):
  self.check();await self.recover()
  for name,r in self.external.items():
   out=self.corrections/(name+'.json') if name in self.wrong or name in self.duplicates else self.path/'outcomes'/(name+'.json')
   if not out.exists():self.active[name]={'model':r['model'],'task':r['task'],'phase':r['phase'],'inherited':True}
  heartbeat=asyncio.create_task(self.heartbeat());monitor=asyncio.create_task(self.monitor_resources())
  def fail_monitor(t):
   if not t.cancelled() and t.exception():self.halt='Resource monitor exception: '+str(t.exception());self.status()
  monitor.add_done_callback(fail_monitor)
  try:
   enabled=json.loads((self.path/'smoke-compatibility.json').read_text())['enabled'];keys={(r['model'],r['task'],r['replicate']) for r in self.external.values()}
   slots=[(m,s,n) for n in range(1,9) for s in SLUGS for m in enabled if (m,s,n) not in keys]
   await self.sync('parallel-v142-start')
   await asyncio.gather(self.inherit_all(),*(self.slot(*p) for p in slots))
   self.check();self.summarize();self.status('completed' if not self.halt else 'blocked');await self.sync('final-v142');self.status('completed' if not self.halt else 'blocked')
  finally:heartbeat.cancel();monitor.cancel()
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
   for args in [('add',str(self.path/'outcomes'),str(self.path/'trajectories'),str(self.path/'artifacts'),str(self.path/'snapshots'),str(self.corrections),str(self.path/'smoke-compatibility.json'),'PROJECT_STATUS.md'),('commit','-m','Record unattended proxy milestone '+tag),('push','origin','main')]:
    r=await asyncio.to_thread(git,*args)
    if r.returncode:self.git_error='Git '+args[0]+' failed: '+r.stderr[-1000:];self.status();return
   local=git('rev-parse','HEAD').stdout.strip();remote=git('ls-remote','origin','refs/heads/main').stdout.split()
   if not remote or remote[0]!=local:self.git_error='Remote commit verification failed'
   self.status()
async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--study-id',required=True);a=ap.parse_args();s=Study(a.study_id)
 lock=(s.live/'supervisor-v142.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old=json.loads((s.live/'status.json').read_text()) if (s.live/'status.json').exists() else {}
 if old.get('state') in ('completed','blocked'):return
 startsfile=s.live/'supervisor-v142-starts.json';starts=json.loads(startsfile.read_text()) if startsfile.exists() else [];starts.append(now());atomic(startsfile,starts)
 if len(starts)>5:s.halt='Supervisor recovery allowance exhausted';s.status('blocked');return
 try:await s.run()
 except BaseException as ex:s.halt=type(ex).__name__+': '+str(ex);s.status('failed');raise
if __name__=='__main__':asyncio.run(main())

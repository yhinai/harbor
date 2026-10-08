"""Operational concurrency amendment; preserves running v1.4.0 child trials."""
from pathlib import Path
import sys,asyncio,json,os,signal,subprocess,fcntl,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'tools/harness-v1.4.0'
sys.path.insert(0,str(OLD))
from panel_runner import Study as OriginalStudy,atomic,now,MODELS,SLUGS
class Study(OriginalStudy):
 def __init__(self,name):
  super().__init__(name)
  self.amend=json.loads((self.path/'amendments/v1.4.1.json').read_text())
  self.external={r['attempt_id']:r for r in self.amend['inherited_attempts']}
  pressure=self.live/'v141-memory-pressure.json';self.pressure=json.loads(pressure.read_text()) if pressure.exists() else {}
  self.sem=asyncio.Semaphore(self.amend['max_parallel_trials'])
  self.plan['minimum_available_memory_mb']=self.amend['minimum_available_memory_mb']
 def check(self):
  super().check()
  for f,h in self.amend['source_sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,'Amendment source changed: '+f
 def status(self,state=None):
  super().status(state)
  p=self.live/'status.json';d=json.loads(p.read_text());d.update(operational_version='1.4.1',max_parallel_trials=self.amend['max_parallel_trials'],minimum_available_memory_mb=self.plan['minimum_available_memory_mb']);atomic(p,d)
 async def memory_gate(self):
  while not self.halt:
   if not await super().memory_gate():return False
   # No await between this check and run_attempt registering its active slot.
   if len(self.active)<self.amend['max_parallel_trials']:return True
   await asyncio.sleep(3)
  return False
 def collect(self,job,name,phase,model,slug,rep,attempt):
  row=super().collect(job,name,phase,model,slug,rep,attempt)
  if name in self.pressure:
   row['host_memory_pressure']=self.pressure[name]
   if row['status']=='valid':row.update(status='host_memory_pressure',reward=None)
  return row
 async def monitor_resources(self):
  import re
  baseline=None
  while True:
   proc=await asyncio.create_subprocess_exec('colima','ssh','--profile','frontier-portfolio','--','sh','-c','cat /proc/meminfo; cat /proc/vmstat',env=self.env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   out,_=await proc.communicate()
   if not proc.returncode:
    available=int(re.search(rb'MemAvailable:\s+(\d+)',out).group(1))//1024;oom=int(re.search(rb'oom_kill\s+(\d+)',out).group(1))
    if baseline is None:baseline=oom
    if available<1536 or oom>baseline:
     event={'time_utc':now(),'available_memory_mb':available,'oom_kill_counter':oom}
     for name in self.active:self.pressure.setdefault(name,[]).append(event)
     atomic(self.live/'v141-memory-pressure.json',self.pressure)
     atomic(self.path/'snapshots/v141-memory-pressure.json',self.pressure)
     if oom>baseline:self.halt='Host VM memory pressure caused a kernel termination; new dispatch stopped'
     baseline=oom
   await asyncio.sleep(10)
 async def recover(self):
  from harbor.environments.docker.docker import _sanitize_docker_compose_project_name
  for p in self.live.glob('*.json'):
   if p.name in ('status.json','budget.json'):continue
   r=json.loads(p.read_text())
   if not isinstance(r,dict):continue
   name=r.get('attempt_id')
   if not name or name in self.external or (self.path/'outcomes'/(name+'.json')).exists():continue
   job=Path(r['job'])
   for t in job.iterdir() if job.exists() else []:
    if not t.is_dir():continue
    project=_sanitize_docker_compose_project_name(t.name)
    ids=subprocess.check_output(['docker','ps','-aq','--filter','label=com.docker.compose.project='+project],env=self.env,text=True).split()
    if ids:subprocess.run(['docker','rm','-f',*ids],env=self.env,check=True,capture_output=True)
   row=self.collect(job,name,r['phase'],r['model'],r['task'],r['replicate'],r['attempt'])
   if row['status']=='missing_trial_result':row.update(status='InterruptedHostProcess',reward=None)
   atomic(self.path/'outcomes'/(name+'.json'),row)
  self.status()
 async def inherit(self,r):
  name=r['attempt_id'];out=self.path/'outcomes'/(name+'.json');job=Path(r['job'])
  if not out.exists():
   print('Preserving active paid child',name,flush=True)
   while not (job/'result.json').exists():
    proc=await asyncio.create_subprocess_exec('/bin/ps','-p',str(r['child_pid']),'-o','stat=',stdout=asyncio.subprocess.PIPE)
    data,_=await proc.communicate()
    if proc.returncode or data.decode().strip().startswith('Z'):break
    await asyncio.sleep(5)
   row=self.collect(job,name,r['phase'],r['model'],r['task'],r['replicate'],r['attempt'])
   if row['status']=='missing_trial_result':row.update(status='InterruptedHostProcess',reward=None)
   atomic(out,row);print('Collected inherited child',name,row['status'],row['reward'],flush=True)
  self.active.pop(name,None);self.status()
  await self.slot(r['model'],r['task'],r['replicate'])
 async def retire_old_dispatcher(self):
  from dotenv import dotenv_values
  password=dotenv_values(ROOT/'.env').get('SUDO_PASSWORD');assert password
  r=await asyncio.to_thread(subprocess.run,['sudo','-S','-p','','launchctl','bootout','system/org.harbor.'+self.amend['study_id']],input=password+'\n',text=True,capture_output=True,timeout=60)
  atomic(self.path/'snapshots/v141-dispatcher-retirement.json',{'time_utc':now(),'old_dispatcher_bootout_exit_code':r.returncode,'label':'all inherited paid child attempts collected before original dispatcher removal'})
 async def run(self):
  self.check();await self.recover()
  # Include inherited children in the global concurrency count.
  for name,r in self.external.items():
   if not (self.path/'outcomes'/(name+'.json')).exists():self.active[name]={'model':r['model'],'task':r['task'],'phase':r['phase'],'inherited':True}
  heartbeat=asyncio.create_task(self.heartbeat());monitor=asyncio.create_task(self.monitor_resources())
  try:
   smokes=json.loads((self.path/'smoke-compatibility.json').read_text())['enabled'];assert smokes,'No compatible models'
   keys={(r['model'],r['task'],r['replicate']) for r in self.external.values()}
   slots=[(m,s,n) for n in range(1,9) for s in SLUGS for m in smokes if (m,s,n) not in keys]
   await self.sync('parallel-v141-start')
   await asyncio.gather(*(self.inherit(r) for r in self.external.values()),*(self.slot(*p) for p in slots))
   await self.retire_old_dispatcher();self.check();self.summarize();self.status('completed' if not self.halt else 'blocked');await self.sync('final-v141');self.status('completed' if not self.halt else 'blocked')
  finally:heartbeat.cancel();monitor.cancel()
async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--study-id',required=True);a=ap.parse_args();s=Study(a.study_id)
 lock=(s.live/'supervisor-v141.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old=json.loads((s.live/'status.json').read_text()) if (s.live/'status.json').exists() else {}
 if old.get('state') in ('completed','blocked'):return
 startsfile=s.live/'supervisor-v141-starts.json';starts=json.loads(startsfile.read_text()) if startsfile.exists() else [];starts.append(now());atomic(startsfile,starts)
 if len(starts)>5:s.halt='Supervisor recovery allowance exhausted';s.status('blocked');return
 try:await s.run()
 except BaseException as ex:s.halt=type(ex).__name__+': '+str(ex);s.status('failed');raise
if __name__=='__main__':asyncio.run(main())

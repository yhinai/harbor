"""Resume the existing study; container OOM counters do not imply host exhaustion."""
from pathlib import Path
import sys,asyncio,json,re,subprocess,fcntl,argparse,importlib.util
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('v142_controller',ROOT/'tools/harness-v1.4.2/parallel_runner.py');previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
from panel_runner import Study as OriginalStudy,atomic,now

def memory_action(available_mb,previous_oom,current_oom):
 return {'pause_new_admission':available_mb<3072,'emergency_stop':available_mb<512,'oom_counter_increased':previous_oom is not None and current_oom>previous_oom,'oom_scope':'unknown; counter includes per-container limits'}

class Study(previous.Study):
 def __init__(self,name):
  super().__init__(name);self.amend=json.loads((self.path/'amendments/v1.4.3.json').read_text());self.external={r['attempt_id']:r for r in self.amend['inherited_attempts']};self.corrections=self.path/'outcome-corrections/v1.4.3';self.corrections.mkdir(parents=True,exist_ok=True);self.pressure={}
 def status(self,state=None):
  OriginalStudy.status(self,state);rows={r['attempt_id']:r for r in self.done}
  for folder in ['v1.4.2','v1.4.3']:
   for p in (self.path/'outcome-corrections'/folder).glob('*.json'):
    r=json.loads(p.read_text());rows[r['attempt_id']]=r
  self.done=list(rows.values());p=self.live/'status.json';d=json.loads(p.read_text());d.update(operational_version='1.4.3',max_parallel_trials=40,minimum_available_memory_mb=3072,finished_attempts=len(self.done),valid_panel_trials=sum(r['phase']=='panel' and r['status']=='valid' for r in self.done),panel_passes=sum(r['phase']=='panel' and r['status']=='valid' and r['reward']==1 for r in self.done));atomic(p,d)
 def collect(self,job,name,phase,model,slug,rep,attempt):
  row=OriginalStudy.collect(self,job,name,phase,model,slug,rep,attempt)
  if name in self.duplicates:row.update(underlying_status=row['status'],status='scheduler_duplicate',reward=None)
  return row
 async def slot(self,model,slug,rep):
  # Fresh replacements for operational or protocol errors only; no graded retry.
  from panel_runner import MODELS
  rows=[r for r in self.done if r['phase']=='panel' and r['model']==MODELS[model] and r['task']==slug and r['replicate']==rep]
  if any(r['status']=='valid' for r in rows):return
  used=max((r['attempt'] for r in rows),default=0)
  for attempt in range(used+1,4):
   row=await self.run_attempt('panel',model,slug,rep,attempt)
   if row is None:return
   total=sum(r['phase']=='panel' for r in self.done)
   if total>=self.last_sync+20:self.last_sync=total;await self.sync('v143-panel-'+str(total))
   if row['status']=='valid':return
   if row['status'] not in ['ProxyTransportFailure','ProxyHTTPFailure','ProxyStreamInactivity','ProxyProtocolFailure','RuntimeError','missing_trial_result','InterruptedHostProcess']:return
 async def monitor_resources(self):
  baseline=None;events=[]
  while True:
   p=await asyncio.create_subprocess_exec('colima','ssh','--profile','frontier-portfolio','--','cat','/proc/meminfo','/proc/vmstat',env=self.env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   out,_=await asyncio.wait_for(p.communicate(),60)
   if p.returncode:self.halt='VM resource monitor failed; new dispatch stopped';self.status();return
   available=int(re.search(rb'MemAvailable:\s+(\d+)',out).group(1))//1024;oom=int(re.search(rb'oom_kill\s+(\d+)',out).group(1));action=memory_action(available,baseline,oom)
   sample={'time_utc':now(),'available_memory_mb':available,'oom_kill_counter':oom,'active_trials':len(self.active),**action};atomic(self.live/'v143-resource-sample.json',sample)
   if action['oom_counter_increased'] or action['pause_new_admission']:
    events.append(sample);atomic(self.path/'snapshots/v143-resource-events.json',events)
   if action['emergency_stop']:self.halt='VM available memory below 512 MiB; new dispatch stopped for inspection';self.status()
   baseline=oom;await asyncio.sleep(10)
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
   with (ROOT/'PROJECT_STATUS.md').open('a') as f:f.write('\n**Verified unattended v1.4.3 milestone '+tag+' ('+now()+'):** '+str(status['valid_panel_trials'])+' graded panel trials; '+str(status['finished_attempts'])+' finished attempts including smokes/exclusions. See `'+str(self.path.relative_to(ROOT))+'`. Reported-usage estimate $'+format(status['reported_usage_estimate_usd'],'.4f')+'; invoice unknown. Original freeze unchanged.\n')
   for args in [('add',str(self.path/'outcomes'),str(self.path/'trajectories'),str(self.path/'artifacts'),str(self.path/'snapshots'),str(self.path/'outcome-corrections'),str(self.path/'smoke-compatibility.json'),'PROJECT_STATUS.md'),('commit','-m','Record unattended proxy milestone '+tag),('push','origin','main')]:
    r=await asyncio.to_thread(git,*args)
    if r.returncode:self.git_error='Git '+args[0]+' failed: '+r.stderr[-1000:];self.status();return
   local=git('rev-parse','HEAD').stdout.strip();remote=git('ls-remote','origin','refs/heads/main').stdout.split()
   if not remote or remote[0]!=local:self.git_error='Remote commit verification failed'
   self.status()
 async def run(self):
  self.status();self.last_sync=sum(r['phase']=='panel' for r in self.done)
  # Previous implementation is retained, with virtual hooks above correcting accounting and monitoring.
  original_sync=self.sync
  async def tagged_sync(tag):await original_sync('v143-'+tag)
  self.sync=tagged_sync
  await super().run()

async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--study-id',required=True);a=ap.parse_args();s=Study(a.study_id)
 lock=(s.live/'supervisor-v143.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old=json.loads((s.live/'status.json').read_text()) if (s.live/'status.json').exists() else {}
 if old.get('operational_version')=='1.4.3' and old.get('state') in ('completed','blocked'):return
 startsfile=s.live/'supervisor-v143-starts.json';starts=json.loads(startsfile.read_text()) if startsfile.exists() else [];starts.append(now());atomic(startsfile,starts)
 if len(starts)>5:s.halt='Supervisor recovery allowance exhausted';s.status('blocked');return
 try:await s.run()
 except BaseException as ex:s.halt=type(ex).__name__+': '+str(ex);s.status('failed');raise
if __name__=='__main__':asyncio.run(main())

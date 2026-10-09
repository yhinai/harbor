"""Recover a missing agent-created helper by replaying its recorded writes only."""
import gzip,json,re,os,subprocess,hashlib,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];STUDY=ROOT/'analysis/followup-v1.4.0/studies/mini-panel-20261008-v140';OUT=ROOT/'analysis/review-v1.5.0/helper-reconstruction';OUT.mkdir(exist_ok=True)
name='panel-glm-checkpointed-journal-4-a1-d4901aba';writes=[]
with gzip.open(STUDY/'trajectories'/(name+'.jsonl.gz'),'rt') as f:
 for line in f:
  if '"kind": "terminal_call"' not in line:continue
  r=json.loads(line);c=r['command']
  if 'journal.py' in c and re.search(r'cat\s*>|write_text|write_bytes|open\([^\n]*[\x27\x22](?:w|a)',c):writes.append(r)
(OUT/'journal-write-commands.json').write_text(json.dumps(writes,indent=2)+'\n');assert writes
ENV=os.environ.copy();ENV.update(PATH=str(Path.home()/'.local/harbor-runtime/bin')+':/usr/bin:/bin',DOCKER_CONFIG=str(Path.home()/'.local/harbor-runtime/docker-config'),DOCKER_HOST='unix://'+str(Path.home()/'.colima/frontier-portfolio/docker.sock'))
for k in list(ENV):
 if any(s in k.upper() for s in ['API_KEY','PASSWORD','TOKEN','SECRET']):ENV.pop(k,None)
def run(args,timeout=180):return subprocess.run(args,env=ENV,capture_output=True,text=True,timeout=timeout)
sys_path=ROOT/'tools/harness-v1.4.0';import sys;sys.path.insert(0,str(sys_path));from proxy_runtime import terminal_command
cid='review-helper-'+uuid.uuid4().hex[:12];result={'label':'verified reconstruction from exact recorded helper writes, never executes agent code on host','attempt_id':name,'commands':[]}
p=run(['docker','run','--detach','--name',cid,'--network','none','--cpus','2','--memory','1g','--entrypoint','/bin/sh','harbor-review-v150-checkpointed-journal','-c','sleep 1800']);assert p.returncode==0,p.stderr
try:
 for r in writes:
  p=run(['docker','exec','--user','agent','--workdir','/app',cid,'/bin/sh','-c',terminal_command(r['command'],60)],90)
  result['commands'].append({'step':r['step_index'],'recorded_time':r['time_utc'],'outer_exit_code':p.returncode,'captured_wrapper_result':p.stdout[-8000:],'stderr':p.stderr[-2000:]});print('replayed exact write at step',r['step_index'],flush=True)
 p=run(['docker','exec','--user','agent',cid,'cat','/app/journal.py']);assert p.returncode==0,p.stderr
 helper=p.stdout.encode();(OUT/'journal.py').write_bytes(helper);result['reconstructed_helper_sha256']=hashlib.sha256(helper).hexdigest()
 original=ROOT/'tmp/review-v150'/name/'main.py'
 for cmd in [['docker','cp',str(original),cid+':/app/main.py'],['docker','cp',str(ROOT/'portfolio/checkpointed-journal/tests')+'/.',cid+':/tests/']]:
  p=run(cmd);assert p.returncode==0,p.stderr
 script='chown agent:agent /app/main.py; mkdir -p /logs/verifier; python3 -I /tests/grade.py; cat /logs/verifier/status.json; printf "\\nREWARD="; cat /logs/verifier/reward.txt; printf "\\nCANDIDATE_STDERR="; cat /logs/verifier/candidate.stderr'
 p=run(['docker','exec','--user','0',cid,'/bin/sh','-c',script]);body,tail=p.stdout.rsplit('\nREWARD=',1);reward,stderr=tail.split('\nCANDIDATE_STDERR=',1);result.update(replay_reward=int(reward.strip()),grader_status=json.loads(body),candidate_stderr=stderr,root_wrapper_exit_code=p.returncode,original_main_sha256=hashlib.sha256(original.read_bytes()).hexdigest())
finally:run(['docker','rm','-f',cid])
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['commands','candidate_stderr']},indent=2));assert result['replay_reward']==1

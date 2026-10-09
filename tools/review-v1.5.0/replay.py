"""Audit saved artifacts and replay frozen graders in fresh CPU-only containers. No inference."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,os,subprocess,zipfile,uuid,time
ROOT=Path(__file__).resolve().parents[2];STUDY=ROOT/'analysis/followup-v1.4.0/studies/mini-panel-20261008-v140';OUT=Path(os.environ.get('REVIEW_OUTPUT',str(ROOT/'analysis/review-v1.5.0')));OUT.mkdir(parents=True,exist_ok=True)
WORK=ROOT/'tmp/review-v150';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();ENV.update(PATH=str(Path.home()/'.local/harbor-runtime/bin')+':/usr/bin:/bin',DOCKER_CONFIG=str(Path.home()/'.local/harbor-runtime/docker-config'),DOCKER_HOST='unix://'+str(Path.home()/'.colima/frontier-portfolio/docker.sock'))
for key in list(ENV):
 if any(s in key.upper() for s in ['API_KEY','PASSWORD','TOKEN','SECRET']):ENV.pop(key,None)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2)+'\n');t.replace(p)
def run(cmd,timeout=180):return subprocess.run(cmd,env=ENV,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
manifest=json.loads((ROOT/'portfolio/evidence/day1-amendment-v1.2.0.json').read_text())
assert sha(ROOT/'day1-submission.zip')== 'efdf99bd59590cb22cf45268f1caa9ea6df7b2df71345fdfac83a2e3d7611c7f'
for f,h in manifest['task_sha256'].items():assert sha(ROOT/'portfolio'/f)==h,f
rows={};provenance={}
for folder in ['outcomes','outcome-corrections/v1.4.2','outcome-corrections/v1.4.3']:
 for f in (STUDY/folder).glob('*.json'):
  r=json.loads(f.read_text());rows[r['attempt_id']]=r;provenance[r['attempt_id']]=str(f.relative_to(ROOT))
valid=sorted([r for r in rows.values() if r['phase']=='panel' and r['status']=='valid'],key=lambda r:r['attempt_id'])
assert len(valid)==120
keys=[(r['model'],r['task'],r['replicate']) for r in valid];assert len(set(keys))==120
images={}
for slug in sorted({r['task'] for r in valid}):
 image='harbor-review-v150-'+slug
 p=run(['docker','build','--network','none','-t',image,str(ROOT/'portfolio'/slug/'environment')],600)
 assert p.returncode==0,p.stderr[-2000:];images[slug]=image
save(OUT/'inventory.json',{'label':'verified merged evidence inventory; no paid calls','original_archive_sha256':sha(ROOT/'day1-submission.zip'),'frozen_package_files':len(manifest['task_sha256']),'total_attempt_records':len(rows),'smokes':sum(r['phase']=='smoke' for r in rows.values()),'panel_status_counts':{s:sum(r['phase']=='panel' and r['status']==s for r in rows.values()) for s in sorted({r['status'] for r in rows.values()})},'unique_valid_slots':len(set(keys)),'per_trial_record':provenance,'runtime_policy':{'parallelism':8,'network':'none','cpus':2,'memory_bytes':1024**3,'candidate_privilege':'agent uid 1000; trusted grader root','dependencies':'frozen task Dockerfile; candidate artifact only'}})
def replay(r):
 start=time.monotonic();name=r['attempt_id'];slot=WORK/name;slot.mkdir(exist_ok=True);saved=r['saved_artifact_sha256'];actual={}
 for f,h in saved.items():
  path=STUDY/f;actual[f]=sha(path);assert actual[f]==h,'Saved evidence hash mismatch '+f
 archives=[STUDY/f for f in saved if f.endswith('.zip')];assert len(archives)==1
 file='witness.json' if r['task']=='typecheck-soundness-witness' else 'main.py'
 with zipfile.ZipFile(archives[0]) as z:source=z.read('app/'+file)
 candidate=slot/file;candidate.write_bytes(source);candidate.chmod(0o644);slot.chmod(0o755)
 cname='review-v150-'+uuid.uuid4().hex[:12]
 script='mkdir -p /tests; cp -R /audit-tests/. /tests/; cp /candidate/'+file+' /app/'+file+'; chown agent:agent /app/'+file+'; mkdir -p /logs/verifier; python3 -I /tests/grade.py; code=$?; cat /logs/verifier/status.json; printf "\\nREWARD="; cat /logs/verifier/reward.txt; exit "$code"'
 try:p=run(['docker','run','--rm','--name',cname,'--network','none','--cpus','2','--memory','1g','--user','0','--mount','type=bind,src='+str(ROOT/'portfolio'/r['task']/'tests')+',dst=/audit-tests,readonly','--mount','type=bind,src='+str(slot)+',dst=/candidate,readonly','--entrypoint','/bin/sh',images[r['task']],'-c',script],180)
 except subprocess.TimeoutExpired:
  run(['docker','rm','-f',cname]);result={'replay_status':'outer_timeout','replay_reward':None}
 else:
  try:body,reward=p.stdout.rsplit('\nREWARD=',1);status=json.loads(body);result={'replay_status':status['status'],'replay_reward':int(reward.strip()),'grader_status':status,'exit_code':p.returncode,'stderr':p.stderr[-3000:]}
  except Exception:result={'replay_status':'unreadable_replay_result','replay_reward':None,'exit_code':p.returncode,'stdout':p.stdout[-6000:],'stderr':p.stderr[-3000:]}
 result.update(attempt_id=name,task=r['task'],model=r['model'],replicate=r['replicate'],source_record=provenance[name],artifact_sha256=hashlib.sha256(source).hexdigest(),verified_saved_evidence_sha256=actual,elapsed_seconds=time.monotonic()-start,label='verified fresh Docker replay; same frozen grader; no model calls')
 save(OUT/'replays'/(name+'.json'),result);print(name,result['replay_status'],result['replay_reward'],flush=True);return result
selection=valid[:int(os.environ.get('REPLAY_LIMIT','120'))]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(replay,selection))
for f,h in manifest['task_sha256'].items():assert sha(ROOT/'portfolio'/f)==h,f
save(OUT/'replay-summary.json',{'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':'verified no-inference offline artifact audit','replayed':len(results),'passed':sum(r['replay_reward']==1 for r in results),'failed_or_incomplete':[r['attempt_id'] for r in results if r['replay_reward']!=1],'artifact_hashes_verified':all(r['verified_saved_evidence_sha256'] for r in results),'original_frozen_package_hashes_unchanged':True,'original_archive_sha256':sha(ROOT/'day1-submission.zip')})

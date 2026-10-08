"""Run offline checks once, with durable status and separate evidence; no retries."""
from pathlib import Path
import argparse,datetime,json,os,subprocess,sys,traceback,hashlib
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--run-id',required=True);args=ap.parse_args()
assert args.run_id and all(c.isalnum() or c in '-_' for c in args.run_id)
run=ROOT/'analysis/harness-v1.3.1/runs'/args.run_id;run.mkdir(parents=True,exist_ok=True)
status=run/'status.json'
if status.exists():raise SystemExit('Run ID already exists; no automatic overwrite or restart')
def write(state,**fields):
 tmp=status.with_suffix('.tmp');tmp.write_text(json.dumps({'state':state,'run_id':args.run_id,'host':'mini','scope':'offline-only; no model calls','pid':os.getpid(),'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**fields},indent=2)+'\n');tmp.replace(status)
def integrity():
 m=json.loads((ROOT/'analysis/harness-v1.3.0/amendment.json').read_text())
 for f,h in m['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
write('running')
env=os.environ.copy()
for k in ['FIREWORKS_API_KEY','FIREWORKS_ENV_FILE','HARNESS_PAID_RUNS_ENABLED','SUDO_PASSWORD']:env.pop(k,None)
prefix=Path.home()/'.local/harbor-runtime';env['PATH']=str(prefix/'bin')+':/usr/bin:/bin:/usr/sbin:/sbin';env['DOCKER_CONFIG']=str(prefix/'docker-config');env['DOCKER_HOST']='unix://'+str(Path.home()/'.colima/frontier-portfolio/docker.sock')
try:
 integrity()
 for script,out in [('test_stream.py','stream-tests.json'),('test_budget.py','budget-tests.txt'),('test_agent_output.py','agent-output-test.json'),('test_container_cancel.py','container-cancel.json')]:
  with (run/out).open('w') as f:subprocess.run([sys.executable,str(ROOT/'tools/harness-v1.3.0'/script)],env=env,stdout=f,check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/harness-v1.3.1/validate_offline.py'),'--evidence-dir',str(run)],env=env,check=True)
 integrity();write('completed',result='checks and five canonical Harbor oracles passed')
except BaseException as ex:
 write('failed',exception_type=type(ex).__name__,message=str(ex));traceback.print_exc();raise

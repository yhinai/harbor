"""Actual Harbor/Docker integration and five oracles; never calls a model."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];TOOLS=ROOT/'tools/harness-v1.4.0'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
work=ROOT/'tmp'/('harness-v140-'+stamp);work.mkdir(parents=True)
ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir',type=Path,required=True);args=ap.parse_args()
evidence=args.evidence_dir.resolve();evidence.mkdir(parents=True,exist_ok=True)
assert evidence.is_relative_to(ROOT/'analysis/followup-v1.4.0'),'New run must write separate versioned evidence'
manifest=json.loads((ROOT/'portfolio/evidence/day1-amendment-v1.2.0.json').read_text())
def frozen_check():
 with zipfile.ZipFile(ROOT/'day1-submission.zip') as z:
  for rel,want in manifest['artifact_sha256'].items():
   assert hashlib.sha256(z.read(rel)).hexdigest()==want,rel
   p=ROOT/'portfolio'/rel
   if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==want,rel
frozen_check()
env=os.environ.copy();env['PYTHONPATH']=str(TOOLS);env.pop('FIREWORKS_API_KEY',None);env.pop('FIREWORKS_ENV_FILE',None);env.pop('HARNESS_PAID_RUNS_ENABLED',None)
harbor=Path(sys.executable).parent/'harbor'
fixture=work/'fixture'
for d in ['environment','tests']: (fixture/d).mkdir(parents=True,exist_ok=True)
(fixture/'instruction.md').write_text('Run the deterministic offline harness integration checks.\n')
(fixture/'task.toml').write_text('''version = "1.0"
[agent]
timeout_sec = 120
[verifier]
timeout_sec = 30
[environment]
cpus = 2
memory_mb = 1024
network_mode = "no-network"
''')
(fixture/'environment/Dockerfile').write_text('''FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
WORKDIR /app
RUN useradd --create-home --uid 1000 agent && chown agent:agent /app
USER agent
''')
(fixture/'tests/test.sh').write_text('''#!/bin/bash
set -eu
mkdir -p /logs/verifier
if [ "$(cat /app/checks-passed)" = passed ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
''')
def run(name,args):
 cmd=[str(harbor),'run',*args,'--jobs-dir',str(work/'jobs'),'--job-name',name,'-n','1','--quiet','--extra-docker-compose',str(TOOLS/'offline-network.yaml')]
 print('Starting',name,flush=True)
 with (work/(name+'.log')).open('w') as log:p=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 files=list((work/'jobs'/name).glob('*/result.json'));assert p.returncode==0 and len(files)==1,(name,p.returncode,str(work/(name+'.log')))
 path=files[0];r=json.loads(path.read_text());assert r.get('exception_info') is None,(name,r.get('exception_info'))
 assert r['verifier_result']['rewards']['reward']==1,(name,r)
 out={'name':name,'reward':1,'exception_info':None,'task_checksum':r['task_checksum'],'result_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'result':r}
 (evidence/(name+'.json')).write_text(json.dumps(out,indent=2)+'\n')
 if name=='harbor-integration':
  data=json.loads((path.parent/'agent/checks.json').read_text());(evidence/'terminal-tests.json').write_text(json.dumps(data,indent=2)+'\n')
 print('Passed',name,flush=True);return out
results=[run('harbor-integration',['-p',str(fixture),'-a','offline_agent:OfflineAgent'])]
for slug in ['typecheck-soundness-witness','exact-fused-dot','mixed-width-tso','checkpointed-journal','atomic-range-history']:
 results.append(run('oracle-'+slug,['-p',str(ROOT/'portfolio'/slug),'-a','oracle']))
frozen_check()
record={'label':'verified remote offline Harbor validation; no model calls','version':'1.4.0','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':'matrix','harbor_version':'0.24.0','python':sys.version,'frozen_artifacts_verified':len(manifest['artifact_sha256']),'archive_sha256':hashlib.sha256((ROOT/'day1-submission.zip').read_bytes()).hexdigest(),'trials':[{'name':r['name'],'reward':r['reward'],'result_sha256':r['result_sha256']} for r in results]}
(evidence/'validation-summary.json').write_text(json.dumps(record,indent=2)+'\n')
print('Completed offline harness integration and all five canonical Harbor oracles; frozen hashes unchanged.',flush=True)

"""Executable leakage and permission probes, separate from model evaluations."""
from pathlib import Path
import datetime,json,subprocess,uuid
from docker_validate import docker,ROOT,SLUGS
name='portfolio-isolation-'+uuid.uuid4().hex[:10]
image='portfolio-check-atomic-range-history'
rows={}
def command(*args):
 p=subprocess.run(['docker',*args],capture_output=True,text=True,timeout=180)
 return {'returncode':p.returncode,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]}
def check(tag,*args,want):
 row=command(*args); assert row['returncode']==want,(tag,row); rows[tag]=row
try:
 docker('run','-d','--name',name,'--network','none',image,'sleep','infinity')
 check('unprivileged-agent','exec',name,'python3','-c','import os; assert os.geteuid()==1000; print(os.geteuid())',want=0)
 check('interpreter-setuid-denied','exec',name,'chmod','u+s','/usr/local/bin/python3.12',want=1)
 check('hidden-directory-denied-before-upload','exec',name,'ls','/tests',want=2)
 docker('cp',str(ROOT/'atomic-range-history/tests')+'/.',name+':/tests')
 check('hidden-directory-denied-after-upload','exec',name,'cat','/tests/cases.json',want=1)
 # A helper readable only by the ordinary agent must remain usable in grading.
 source=(ROOT/'atomic-range-history/solution/canonical.py').read_text()
 payload="from pathlib import Path\np=Path('/app/private_helper.py'); p.write_text("+repr(source)+"); p.chmod(0o600)\nPath('/app/main.py').write_text('from private_helper import solve\\nimport json,sys\\nfor line in sys.stdin: print(json.dumps(solve(json.loads(line))))\\n')\nPath('/app/sitecustomize.py').write_text(\"import os\\nfrom pathlib import Path\\nPath('/app/startup-uid-'+str(os.geteuid())).write_text('executed')\\n\")\n"
 docker('exec',name,'python3','-c',payload)
 docker('exec','-u','root',name,'bash','/tests/test.sh')
 reward=float(docker('exec','-u','root',name,'cat','/logs/verifier/reward.txt'))
 assert reward==1
 rows['private-helper-accepted']={'reward':reward}
 check('root-import-injection-denied','exec','-u','root',name,'test','!','-e','/app/startup-uid-0',want=0)
 report={'label':'verified','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'1.1.0','scope':'Common Docker environment and verifier startup; no model calls','probes':rows,'legacy_repair':json.loads((ROOT/'evidence/isolation-repair.json').read_text())}
 (ROOT/'evidence/isolation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Isolation checks passed; private agent helper accepted; root startup hook blocked.')
finally: docker('rm','-f',name)

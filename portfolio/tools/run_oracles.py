"""Run the selected canonical solutions through Harbor; never invokes an LLM."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
from selection import ROOT,SLUGS

def hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for s in SLUGS for p in sorted((ROOT/s).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}

def main():
    name=sys.argv[1] if len(sys.argv)>1 else 'phase3-oracles-v110'
    before=hashes();jobroot=ROOT.parent/'tmp/harbor-jobs';job=jobroot/name
    cmd=[str(Path(sys.executable).parent/'harbor'),'run','-p',str(ROOT),'-x','*alignment-relaxation*','-a','oracle','-e','docker','--jobs-dir',str(jobroot),'--job-name',name,'-n','1','--quiet']
    process=subprocess.run(cmd)
    if process.returncode:raise SystemExit(process.returncode)
    assert before==hashes(),'Package bytes changed during oracle verification'
    data=json.loads((job/'result.json').read_text());rows={}
    for path in job.glob('*/result.json'):
        trial=json.loads(path.read_text());slug=Path(trial['task_name']).name
        assert slug in SLUGS and slug not in rows,(slug,path)
        assert trial.get('exception_info') is None,trial
        reward=trial['verifier_result']['rewards']['reward'];assert reward==1,(slug,trial)
        status=json.loads((path.parent/'verifier/status.json').read_text())
        assert status['status']=='pass',(slug,status)
        rows[slug]={'reward':reward,'exception_info':trial.get('exception_info'),'task_checksum':trial['task_checksum'],'result_path':str(path.relative_to(ROOT.parent)),'result_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'verifier_status':status}
    assert set(rows)==set(SLUGS),rows.keys()
    record={'label':'verified','version':'1.1.0','scope':'Five selected actual Harbor Docker oracle trials; no model calls','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'harbor_version':'0.24.0','job_result':data,'trials':rows,'task_sha256':before}
    (ROOT/'evidence/harbor-oracles-v1.1.0.json').write_text(json.dumps(record,indent=2)+'\n')
    print('All five selected Harbor oracles passed; exact package hashes recorded.',flush=True)
if __name__=='__main__':main()

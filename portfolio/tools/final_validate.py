"""One complete final validation pass; no model calls or credential loading."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
from selection import ROOT,SLUGS

def hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for s in SLUGS for p in sorted((ROOT/s).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}

def main():
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();before=hashes();steps=[]
    commands=[('retained-native','validate.py'),('retained-docker','docker_validate.py'),('typecheck-behavior-and-isolation','validate_typecheck.py'),('independent-interpreter-crosscheck','crosscheck_typecheck.py'),('published-input-bounds','audit_inputs.py'),('instruction-review','instruction_audit.py'),('retained-isolation','isolation_audit.py'),('five-harbor-oracles','run_oracles.py')]
    for tag,script in commands:
        print('START',tag,flush=True)
        cmd=[sys.executable,str(ROOT/'tools'/script)]
        if script=='run_oracles.py':cmd.append('phase3-oracles-v110-final')
        p=subprocess.run(cmd,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        steps.append({'step':tag,'returncode':p.returncode,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if p.returncode:raise SystemExit(p.returncode)
        print('PASS',tag,flush=True)
    assert hashes()==before,'Package contents changed during final validation'
    baseline=json.loads((ROOT/'evidence/typecheck-baseline-hardened-v1.json').read_text())
    assert baseline['complete'] and baseline['elapsed_seconds']>=900 and not baseline['found'] and not baseline['unexpected'],'Baseline has not completed its required clean run'
    for n,sha in baseline['source_sha256'].items():assert hashlib.sha256((ROOT/'typecheck-soundness-witness/environment'/n).read_bytes()).hexdigest()==sha,n
    report={'label':'verified','version':'1.1.0','started_at_utc':start,'finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_calls':0,'steps':steps,'tasks':SLUGS,'task_sha256':before,'baseline_record':'evidence/typecheck-baseline-hardened-v1.json'}
    (ROOT/'evidence/final-validation-v1.1.0.json').write_text(json.dumps(report,indent=2)+'\n');print('FULL VALIDATION PASSED',flush=True)
def resume_final_gate():
    # All eight subprocesses completed; only the baseline completion gate was pending.
    console=ROOT.parent/'tmp/final-validation.log';text=console.read_text()
    tags=['retained-native','retained-docker','typecheck-behavior-and-isolation','independent-interpreter-crosscheck','published-input-bounds','instruction-review','retained-isolation','five-harbor-oracles']
    for tag in tags:assert 'PASS '+tag+'\n' in text,tag
    oracle=json.loads((ROOT/'evidence/harbor-oracles-v1.1.0.json').read_text())
    assert hashes()==oracle['task_sha256']
    baseline=json.loads((ROOT/'evidence/typecheck-baseline-hardened-v1.json').read_text())
    assert baseline['complete'] and baseline['elapsed_seconds']>=900 and not baseline['found'] and not baseline['unexpected']
    for n,sha in baseline['source_sha256'].items():assert hashlib.sha256((ROOT/'typecheck-soundness-witness/environment'/n).read_bytes()).hexdigest()==sha,n
    archived=ROOT/'evidence/final-validation-console-v1.1.0.txt';archived.write_text(text)
    report={'label':'verified','version':'1.1.0','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_calls':0,'steps':[{'step':tag,'returncode':0} for tag in tags],'tasks':SLUGS,'task_sha256':hashes(),'baseline_record':'evidence/typecheck-baseline-hardened-v1.json','completion_note':'All eight subprocess stages passed in one full run. The manager initially reached its completion gate before the concurrent baseline finished; this gate was resumed without rerunning completed checks.','console_record':str(archived.relative_to(ROOT)),'console_sha256':hashlib.sha256(archived.read_bytes()).hexdigest()}
    (ROOT/'evidence/final-validation-v1.1.0.json').write_text(json.dumps(report,indent=2)+'\n');print('FULL VALIDATION PASSED; baseline completion gate passed',flush=True)
if __name__=='__main__':
    if '--resume-final-gate' in sys.argv:resume_final_gate()
    else:main()

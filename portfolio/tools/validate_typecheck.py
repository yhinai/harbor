"""Behavioral, boundary and isolation checks for the Reed package (no model calls)."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,os,subprocess,sys,tempfile,uuid
ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'typecheck-soundness-witness'
sys.path.insert(0,str(TASK/'environment'))
from language import load,validate,InvalidProgram,StaticError
from checker import check
from interpreter import run
from docker_validate import docker

def main():
    rows={};local={}
    for n in ['language.py','checker.py','interpreter.py']:
        assert (TASK/'environment'/n).read_bytes()==(TASK/'tests/reference'/n).read_bytes(),n
    for path in [TASK/'solution/witness.json',TASK/'audit/equivalent.json',TASK/'audit/equivalent-boundary.json',*sorted((TASK/'audit').glob('incorrect-*.json'))]:
        try:p=load(path.read_text());accepted=check(p);execution=run(p);reward=int(execution['status']=='type_error')
        except (InvalidProgram,StaticError,TypeError,ValueError,RecursionError) as e:accepted=False;execution={'status':type(e).__name__,'reason':str(e)};reward=0
        want=int(path.name in ('witness.json','equivalent.json','equivalent-boundary.json'))
        assert reward==want,(path,execution)
        local[str(path.relative_to(TASK))]={'accepted':accepted,'reward':reward,'execution':execution}
    # The error's evaluation step is inclusive. One fewer allowed step is insufficient.
    for path in [TASK/'solution/witness.json',TASK/'audit/equivalent.json',TASK/'audit/equivalent-boundary.json']:
        p=load(path.read_text());n=run(p)['steps']
        assert run(p,limit=n)['status']=='type_error'
        assert run(p,limit=n-1)['status']=='step_limit'
    local['step_boundary']={'status':'pass','rule':'type error at the last allowed step counts'}
    for text in ['{"cells":{},"cells":{},"inputs":{},"body":[]}', '{"cells":{},"inputs":{},"body":[["eval",["lit",NaN]]]}']:
        try:load(text)
        except InvalidProgram:pass
        else:raise AssertionError('invalid JSON accepted')
    local['duplicate_and_nonfinite']={'status':'pass'}
    # A corrected memo key should reject both concrete counterexamples.
    spec=importlib.util.spec_from_file_location('corrected_checker',TASK/'environment/checker.py');fixed=importlib.util.module_from_spec(spec);sys.modules[spec.name]=fixed
    code=(TASK/'environment/checker.py').read_text().replace("return (shape(t.result),t.writes) if isinstance(t,Function) else t","return t")
    exec(compile(code,str(TASK/'environment/checker.py'),'exec'),fixed.__dict__)
    for path in [TASK/'solution/witness.json',TASK/'audit/equivalent.json',TASK/'audit/equivalent-boundary.json']:
        try:fixed.check(load(path.read_text()))
        except StaticError:pass
        else:raise AssertionError('corrected checker accepts reference witness')
    local['one_fault_control']={'status':'pass','change':'Memo key includes the complete nested function type'}
    image='portfolio-check-typecheck-soundness-witness';docker('build','-t',image,TASK/'environment')
    name='typecheck-validation-'+uuid.uuid4().hex[:10]
    docker('run','-d','--name',name,'--network','none','--cpus','2','--memory','1g',image,'sleep','infinity')
    try:
        docker('cp',str(TASK/'tests')+'/.',name+':/tests');docker('cp',str(TASK/'solution')+'/.',name+':/solution')
        for path in [TASK/'solution/witness.json',TASK/'audit/equivalent.json',TASK/'audit/equivalent-boundary.json',*sorted((TASK/'audit').glob('incorrect-*.json'))]:
            docker('cp',path,name+':/app/witness.json');docker('exec','-u','root',name,'bash','/tests/test.sh')
            status=json.loads(docker('exec','-u','root',name,'cat','/logs/verifier/status.json'))
            reward=float(docker('exec','-u','root',name,'cat','/logs/verifier/reward.txt'))
            assert reward==int(path.name in ('witness.json','equivalent.json','equivalent-boundary.json')),(path,status)
            assert status['hardened'] and status['status']!='infrastructure_error'
            rows[path.name]={'reward':reward,'status':status}
        # Artifact privacy, protected grading outputs and immutable interpreter executable.
        for tag,cmd in {
            'tests_not_readable':['cat','/tests/reference/checker.py'],
            'reward_not_writable':['sh','-c','echo 1 > /logs/verifier/reward.txt'],
            'python_setuid_denied':['chmod','u+s','/usr/local/bin/python3.12'],
        }.items():
            p=subprocess.run(['docker','exec',name,*cmd],capture_output=True,text=True,timeout=30)
            assert p.returncode!=0,(tag,p.stdout,p.stderr)
            rows[tag]={'returncode':p.returncode,'stderr':p.stderr[-1000:]}
        # Grading must ignore edited public code and an agent startup hook.
        docker('exec',name,'python3','-c',"from pathlib import Path;Path('/app/checker.py').write_text('raise Exception(\"edited\")');Path('/app/interpreter.py').write_text('raise Exception(\"edited\")');Path('/app/sitecustomize.py').write_text('from pathlib import Path;Path(\"/app/startup-marker\").write_text(\"ran\")')")
        docker('cp',TASK/'solution/witness.json',name+':/app/witness.json')
        docker('exec','-u','root',name,'bash','/tests/test.sh')
        assert float(docker('exec','-u','root',name,'cat','/logs/verifier/reward.txt'))==1
        docker('exec','-u','root',name,'test','!','-e','/app/startup-marker')
        rows['frozen_checker_and_clean_startup']={'reward':1,'status':'pass'}
        # A symlink into hidden grader files is read with agent permissions.
        docker('exec','-u','root',name,'rm','-f','/app/witness.json')
        docker('exec',name,'ln','-s','/tests/reference/checker.py','/app/witness.json')
        docker('exec','-u','root',name,'bash','/tests/test.sh')
        assert float(docker('exec','-u','root',name,'cat','/logs/verifier/reward.txt'))==0
        rows['artifact_symlink_permissions']={'reward':0,'status':'pass'}
    finally:docker('rm','-f',name)
    report={'label':'verified','version':'1.1.0','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_calls':0,'local':local,'docker':rows}
    (ROOT/'evidence/typecheck-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Typecheck validation passed:',len(local),'local checks,',len(rows),'Docker checks',flush=True)
if __name__=='__main__':main()

import collections,json,os,pathlib,subprocess,sys,time,traceback
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from contract import check
TASK='mixed-width-tso'
TESTS=pathlib.Path(__file__).resolve().parent
APP=pathlib.Path(os.environ.get('APP_DIR','/app')).resolve()
LOG=pathlib.Path(os.environ.get('VERIFIER_LOG_DIR','/logs/verifier')).resolve()

def save(reward,status):
    LOG.mkdir(parents=True,exist_ok=True)
    (LOG/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    temp=LOG/'reward.tmp'; temp.write_text(str(reward)+'\n'); temp.replace(LOG/'reward.txt')

def main():
    cases=json.loads((TESTS/'cases.json').read_text())
    assert cases and len({x['id'] for x in cases})==len(cases)
    LOG.mkdir(parents=True,exist_ok=True)
    hardened=sys.platform=='linux' and os.geteuid()==0
    if hardened:
        # Tests are uploaded after the agent phase, and are hidden from execution.
        for protected in [TESTS,LOG,pathlib.Path('/solution')]:
            if protected.exists(): protected.chmod(0o700)
    def restrict():
        if sys.platform=='linux':
            import resource
            resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
            resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        if hardened:
            import pwd
            account=pwd.getpwnam("agent")
            os.setgroups([]); os.setgid(account.pw_gid); os.setuid(account.pw_uid)
    env=os.environ.copy(); env.pop('PYTHONPATH',None)
    # Do not pass provider credentials into submitted programs.
    env={k:v for k,v in env.items() if not any(x in k.upper() for x in ('API_KEY','TOKEN','SECRET','PASSWORD'))}
    payload=''.join(json.dumps(x['request'],separators=(',',':'))+'\n' for x in cases)
    start=time.monotonic()
    try:
        p=subprocess.run([sys.executable,str(APP/'main.py')],input=payload,text=True,capture_output=True,cwd=APP,env=env,timeout=60,preexec_fn=restrict)
    except subprocess.TimeoutExpired:
        save(0,{'status':'candidate_timeout','timeout_sec':60,'hardened':hardened}); return
    elapsed=time.monotonic()-start
    (LOG/'candidate.stderr').write_text(p.stderr[-65536:])
    if p.returncode:
        save(0,{'status':'candidate_error','exit_code':p.returncode,'elapsed_sec':elapsed,'hardened':hardened}); return
    lines=p.stdout.splitlines()
    if len(lines)!=len(cases):
        save(0,{'status':'candidate_protocol_error','expected_lines':len(cases),'actual_lines':len(lines),'elapsed_sec':elapsed,'hardened':hardened}); return
    failures=[]; totals=collections.Counter(); bad=collections.Counter()
    for c,line in zip(cases,lines):
        totals[c['category']]+=1
        try: got=json.loads(line)
        except json.JSONDecodeError: got=None
        if not check(TASK,c['request'],c['expected'],got):
            bad[c['category']]+=1
            if len(failures)<50: failures.append({'case_id':c['id'],'category':c['category']})
    passed=len(cases)-sum(bad.values())
    save(int(not bad),{'status':'pass' if not bad else 'candidate_wrong_answer','passed':passed,'total':len(cases),'failed_by_category':dict(bad),'totals_by_category':dict(totals),'first_failures':failures,'elapsed_sec':elapsed,'hardened':hardened})
if __name__=='__main__':
    try: main()
    except Exception:
        save(0,{'status':'infrastructure_error','traceback':traceback.format_exc()}); sys.exit(2)

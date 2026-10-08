from pathlib import Path
import textwrap
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['exact-fused-dot','mixed-width-tso','atomic-range-history','alignment-relaxation','checkpointed-journal']
contract=r'''
import json

def valid_history(r,order):
    tx={t['id']:t for t in r['transactions']}
    if not isinstance(order,list) or len(order)!=len(tx) or any(not isinstance(x,str) for x in order) or set(order)!=set(tx): return False
    ranks={x:i for i,x in enumerate(order)}
    for a in tx.values():
        for b in tx.values():
            if a['end']<=b['start'] and ranks[a['id']]>=ranks[b['id']]: return False
    d=r['initial'].copy()
    for name in order:
        for op in tx[name]['ops']:
            if op[0]=='get':
                if d.get(op[1])!=op[2]: return False
            elif op[0]=='put': d[op[1]]=op[2]
            elif op[0]=='del': d.pop(op[1],None)
            elif op[0]=='cas':
                _,key,old,new,want=op; ok=d.get(key)==old
                if ok is not want: return False
                if ok:
                    if new is None: d.pop(key,None)
                    else: d[key]=new
            else:
                if sorted([[k,v] for k,v in d.items() if op[1]<=k<op[2]])!=op[3]: return False
    return d==r['final']

def layout_size(r,widths):
    if not isinstance(widths,list) or len(widths)!=sum(x[0]=='branch' for x in r['items']): return None
    if any(type(w) is not int or w not in (2,5) for w in widths): return None
    prefix=[0]; names={}; branches=[]; it=iter(widths)
    for i,(kind,v) in enumerate(r['items']):
        x=prefix[-1]
        if kind=='label': names[v]=i; y=x
        elif kind=='bytes': y=x+v
        elif kind=='align': y=x+(v-x%v)%v
        else:
            width=next(it); branches.append((i,v,width)); y=x+width
        prefix.append(y)
    for i,name,w in branches:
        if w==2 and not -r['limit']<=prefix[names[name]]-prefix[i+1]<r['limit']: return None
    return prefix[-1]

def check(slug,request,expected,got):
    try:
        if not isinstance(got,dict): return False
        if slug=='exact-fused-dot':
            flags=got['flags']
            return isinstance(got['bits'],str) and not got['bits'].lower().startswith('0x') and int(got['bits'],16)==int(expected['bits'],16) and isinstance(flags,list) and len(flags)==len(set(flags)) and set(flags)==set(expected['flags'])
        if slug=='mixed-width-tso':
            def key(o): return json.dumps({'reads':o['reads'],'memory':o['memory']},sort_keys=True,separators=(',',':'))
            os=got['outcomes']; keys=[key(o) for o in os]
            return isinstance(os,list) and len(keys)==len(set(keys)) and set(keys)=={key(o) for o in expected['outcomes']}
        if slug=='atomic-range-history':
            return got['order'] is None if expected['order'] is None else valid_history(request,got['order'])
        if slug=='alignment-relaxation':
            return type(got['size']) is int and got['size']==expected['size'] and layout_size(request,got['widths'])==expected['size']
        return (type(got['valid_bytes']) is int and type(got['last_seq']) is int and got['valid_bytes']==expected['valid_bytes'] and got['last_seq']==expected['last_seq'] and isinstance(got['pages'],list) and [bytes.fromhex(x) for x in got['pages']]==[bytes.fromhex(x) for x in expected['pages']])
    except (ValueError,TypeError,KeyError,AttributeError,StopIteration): return False
'''
grade=r'''
import collections,json,os,pathlib,subprocess,sys,time,traceback
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from contract import check
TASK='SLUG'
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
'''
smoke=r'''
import json,pathlib,subprocess,sys
from public_contract import check
HERE=pathlib.Path(__file__).resolve().parent
cases=json.loads((HERE/'examples.json').read_text())
p=subprocess.run([sys.executable,str(HERE/'main.py')],input=''.join(json.dumps(x['request'])+'\n' for x in cases),text=True,capture_output=True,cwd=HERE)
if p.returncode: print(p.stderr); sys.exit(1)
lines=p.stdout.splitlines()
if len(lines)!=len(cases): print('Wrong number of response lines'); sys.exit(1)
for case,line in zip(cases,lines):
    if not check('SLUG',case['request'],case['expected'],json.loads(line)):
        print('FAILED',case['id']); sys.exit(1)
print('Passed',len(cases),'public examples')
'''
for slug in SLUGS:
    for name,code in [('tests/contract.py',contract),('tests/grade.py',grade.replace('SLUG',slug)),('environment/public_contract.py',contract),('environment/smoke.py',smoke.replace('SLUG',slug))]:
        (ROOT/slug/name).write_text(textwrap.dedent(code).lstrip())
    p=ROOT/slug/'environment/Dockerfile'
    p.write_text(p.read_text().replace('main.py smoke.py examples.json','main.py smoke.py public_contract.py examples.json'))
print('Wrote semantic verifiers and public smoke tests.')

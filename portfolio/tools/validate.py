from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,time,hashlib,platform,datetime
ROOT=Path(__file__).resolve().parents[1]
from selection import RETAINED as SLUGS
MUTATIONS={
'exact-fused-dot':[
('ties-toward-zero',"mode=='RNA' or v%2==1","mode=='RNA'"),
('tininess-before-rounding',"v==0 or v.bit_length()-1+q<1-bias","L<1-bias"),
('discard-negative-zero',"neg=mode=='RDN' or bool(zeros) and all(x is True for x in zeros)","neg=mode=='RDN'"),
('round-each-product',"terms.append(((-1 if s else 1)*a[2]*b[2],a[3]+b[3]))","product=a[2]*b[2]; cut=max(0,product.bit_length()-1-f); product=(product>>cut)<<cut; terms.append(((-1 if s else 1)*product,a[3]+b[3]))"),
],
'mixed-width-tso':[
('oldest-byte-forwarding','for ba,bw,bv in buff[i]:','for ba,bw,bv in reversed(buff[i]):'),
('lifo-drains','a,w,v=buff[i][0]','a,w,v=buff[i][-1]'),
('premature-terminal',"pc[i]==len(code[i]) and not buff[i]","pc[i]==len(code[i])"),
('global-fence-and-exchange',"elif not buff[i]:","elif all(not q for q in buff):"),
('no-forwarding','for ba,bw,bv in buff[i]:','for ba,bw,bv in ():')
],
'atomic-range-history':[
('greedy-no-backtracking',"if suffix is not None: return (t['id'],)+suffix","if suffix is not None: return (t['id'],)+suffix\n            return None"),
('strict-endpoint-order',"u['end']<=t['start']","u['end']<t['start']"),
('ignore-range-observations',"if [[key,d[key]] for key in sorted(d) if lo<=key<hi]!=expected: return None","if False: return None"),
('absence-is-zero',"d.get(op[1])","d.get(op[1],0)")
],
'alignment-relaxation':[
('positive-bound-inclusive',"labels[t]-(p+w)<r['limit']","labels[t]-(p+w)<=r['limit']"),
('ignore-alignment',"pc=(-(-pc//value))*value","pc=pc"),
],
'checkpointed-journal':[
('ignore-checkpoint',"and seq>r['checkpoint']",""),
('ignore-commit-digest',"and wanted==digest",""),
('retain-old-incarnation',"active[tx]=([],0)","active.setdefault(tx,([],0))"),
('replay-uncommitted-patch',"patches.append(patch)","patches.append(patch); pages[patch[0]][patch[1]:patch[1]+len(patch[2])]=patch[2]")
]}
GREEDY=r'''
def solve(r):
    n=sum(k=='branch' for k,_ in r['items']); widths=[2]*n
    while True:
        pc=0; labels={}; branches=[]; j=0
        for kind,value in r['items']:
            if kind=='label': labels[value]=pc
            elif kind=='bytes': pc+=value
            elif kind=='align': pc+=(value-pc%value)%value
            else:
                branches.append((pc,value,j)); pc+=widths[j]; j+=1
        bad=[j for p,t,j in branches if widths[j]==2 and not(-r['limit']<=labels[t]-(p+2)<r['limit'])]
        if not bad: return {'widths':widths,'size':pc}
        for j in bad: widths[j]=5
'''

def run_one(slug,source,tag,base):
    app=base/'app'; logs=base/'logs'/tag; app.mkdir(exist_ok=True,parents=True)
    for p in (ROOT/slug/'environment').iterdir():
        if p.is_file() and p.name!='Dockerfile': shutil.copy2(p,app/p.name)
    if tag=='canonical':
        env={**os.environ,'APP_DIR':str(app)}
        subprocess.run(['bash',str(ROOT/slug/'solution/solve.sh')],check=True,env=env)
    else: (app/'main.py').write_text(source)
    env={**os.environ,'APP_DIR':str(app),'VERIFIER_LOG_DIR':str(logs)}
    p=subprocess.run(['bash',str(ROOT/slug/'tests/test.sh')],env=env,capture_output=True,text=True,timeout=180)
    status=json.loads((logs/'status.json').read_text())
    reward=float((logs/'reward.txt').read_text())
    if p.returncode or status['status']=='infrastructure_error': raise RuntimeError((slug,tag,p.returncode,status,p.stderr))
    return {'label':'verified','reward':reward,**status}

def main():
    report={'label':'verified','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'scope':'Native-host execution of solution/solve.sh and tests/test.sh; not Docker/Harbor trials','container_validation':'separate evidence/docker-validation.json; this script validates native execution only','proxy_trials':0,'frontier_trials':0,'tasks':{}}
    with tempfile.TemporaryDirectory(prefix='portfolio-check-') as td:
        root=Path(td)
        for slug in SLUGS:
            canonical=(ROOT/slug/'solution/canonical.py').read_text(); alt=(ROOT/slug/'audit/equivalent.py').read_text()
            entry={'canonical':run_one(slug,canonical,'canonical',root/slug),'equivalent':run_one(slug,alt,'equivalent',root/slug),'mutants':{}}
            assert entry['canonical']['reward']==entry['equivalent']['reward']==1
            for name,old,new in MUTATIONS[slug]:
                assert old in canonical,(slug,name)
                mutant=canonical.replace(old,new)
                if name=='lifo-drains': mutant=mutant.replace('buff[i][1:]','buff[i][:-1]')
                (ROOT/slug/f'audit/incorrect-{name}.py').write_text(mutant)
                entry['mutants'][name]=run_one(slug,mutant,name,root/slug)
                assert entry['mutants'][name]['reward']==0,(slug,name,'survived')
            if slug=='alignment-relaxation':
                mutant=canonical[:canonical.index('def solve(r):')]+GREEDY+canonical[canonical.index("if __name__=='__main__':"):]
                (ROOT/slug/'audit/incorrect-grow-only.py').write_text(mutant)
                entry['mutants']['grow-only']=run_one(slug,mutant,'grow-only',root/slug)
                assert entry['mutants']['grow-only']['reward']==0,'greedy survived'
            # Incorrect hardcoded response and an unimplemented starter must fail.
            for name,src in [('constant-output',"import sys\nfor line in sys.stdin: print('{}')\n"),('starter',(ROOT/slug/'environment/main.py').read_text())]:
                entry['mutants'][name]=run_one(slug,src,name,root/slug)
                assert entry['mutants'][name]['reward']==0
            # Test the documented public command on the canonical artifact.
            (root/slug/'app/main.py').write_text(canonical)
            smoke=subprocess.run([sys.executable,str(root/slug/'app/smoke.py')],capture_output=True,text=True,check=True)
            entry['smoke']=smoke.stdout.strip()
            report['tasks'][slug]=entry
            print(slug,'canonical=1 equivalent=1',len(entry['mutants']),'incorrect implementations rejected',flush=True)
    report['task_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for slug in SLUGS for p in sorted((ROOT/slug).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    (ROOT/'evidence/local-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Saved evidence/local-validation.json')
if __name__=='__main__': main()

"""Reproducible non-LLM random/coverage-guided Reed program generation.
No canonical or alternative witness is read. The seed corpus is generated here.
"""
import argparse,copy,datetime,hashlib,json,random,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENV=ROOT/'typecheck-soundness-witness/environment'
sys.path.insert(0,str(ENV))
from language import InvalidProgram,StaticError,validate
from checker import check
from interpreter import run

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def generate(r):
    names=['a','b','c','d'][:r.randint(1,4)]
    p={'cells':{n:{'types':['int','text','bool','unit'],'value':r.choice([0,1,'s',True,None])} for n in names},'inputs':{'n':r.randint(-1,4),'flag':r.choice([False,True])},'body':[]}
    result=r.choice([None,0,'s',False])
    def literal():return ['lit',r.choice([0,1,2,'s','t',True,False,None])]
    def fn(depth):
        body=[['set',r.choice(names),literal()] for _ in range(r.randrange(4))]
        return ['fn',body,['lit',result] if depth==1 else fn(depth-1)]
    variables={}
    for i in range(r.randint(2,6)):
        n='f'+str(i);depth=r.randint(1,4);variables[n]=depth
        p['body'].append(['let',n,fn(depth)])
    def statement():
        n=r.choice(list(variables));depth=variables[n]
        same=[v for v,d in variables.items() if d==depth]
        form=r.randrange(5)
        if form<3:
            rhs=['var',r.choice(same)] if r.random()<0.6 else fn(depth)
            return ['assign',n,rhs]
        if form==3:return ['set',r.choice(names),literal()]
        call=['var',n]
        for _ in range(r.randint(1,depth)):call=['call',call]
        return ['eval',call]
    for _ in range(r.randint(1,4)):
        body=[statement() for _ in range(r.randint(1,7))]
        if r.random()<0.3:body=[['if',['var','flag'],body,[]]]
        if r.random()<0.15:body=[['repeat',['var','n'],body]]
        p['body'].append(['repeat',['var','n'],body])
    for n,depth in variables.items():
        if r.random()<0.65:
            call=['var',n]
            for _ in range(depth):call=['call',call]
            p['body'].append(['eval',call])
    for _ in range(r.randint(1,4)):
        cell=r.choice(names);op=r.choice(['add','cat','lt','not'])
        e=[op,['get',cell]] if op=='not' else [op,['get',cell],['lit','x' if op=='cat' else 1]]
        if r.random()<0.3:
            k='text' if op=='cat' else 'bool' if op=='not' else 'int'
            p['body'].append(['if',['is',cell,k],[['eval',e]],[]])
        else:p['body'].append(['eval',e])
    return p

def mutate(r,p):
    p=copy.deepcopy(p);body=p['body']
    mode=r.randrange(6)
    if mode==0 and body:del body[r.randrange(len(body))]
    elif mode==1 and body:
        i=r.randrange(len(body));body.insert(i,copy.deepcopy(body[i]))
    elif mode==2:p['inputs']['n']=r.randint(-1,4);p['inputs']['flag']=r.choice([True,False])
    elif mode==3:
        lists=[]
        def walk(x):
            if isinstance(x,list):
                lists.append(x)
                for v in x:walk(v)
            elif isinstance(x,dict):
                for v in x.values():walk(v)
        walk(p)
        eligible=[x for x in lists if len(x)==2 and x[0]=='lit']
        if eligible:r.choice(eligible)[1]=r.choice([0,1,'s',True,None])
    elif mode==4 and body:
        i=r.randrange(len(body));body[i]=['repeat',['var','n'],[body[i]]]
    else:
        n=r.choice(list(p['cells']));p['cells'][n]['value']=r.choice([0,'s',False,None])
    return p

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=900);ap.add_argument('--seed',type=int,default=20261008);ap.add_argument('--out',required=True);ap.add_argument('--stop-on-find',action='store_true');a=ap.parse_args()
    out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    r=random.Random(a.seed);start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    counts={'generated':0,'structural_rejections':0,'static_rejections':0,'accepted':0,'normal':0,'step_limit':0,'type_error':0}
    coverage=set();corpus=[];found=[];unexpected=[];last=start
    def save(done=False):
        record={'label':'verified','started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat() if done else None,'requested_seconds':a.seconds,'elapsed_seconds':time.monotonic()-start,'seed':a.seed,'method':'Random grammar generation plus coverage-guided corpus mutation; function nesting 1..4; branch/loop joins; mutable cells; no reference witness seeds','stop_on_find':a.stop_on_find,'counts':counts,'coverage':sorted(coverage),'corpus_size':len(corpus),'found':found,'unexpected':unexpected,'complete':done,'source_sha256':{n:sha(ENV/n) for n in ['language.py','checker.py','interpreter.py']},'generator_sha256':sha(Path(__file__))}
        temp=out.with_suffix('.tmp');temp.write_text(json.dumps(record,indent=2)+'\n');temp.replace(out)
    while time.monotonic()-start<a.seconds:
        p=mutate(r,r.choice(corpus)) if corpus and r.random()<0.55 else generate(r)
        counts['generated']+=1;seen=set()
        try:
            validate(p);check(p,seen);counts['accepted']+=1
            result=run(p);counts[result['status']]+=1
        except InvalidProgram:counts['structural_rejections']+=1;continue
        except StaticError:counts['static_rejections']+=1;continue
        except Exception as e:
            unexpected.append({'trial':counts['generated'],'exception':repr(e),'program':p});save(True);raise
        if seen-coverage or (len(corpus)<128 and r.random()<0.1):
            corpus.append(p)
            if len(corpus)>256:corpus.pop(r.randrange(len(corpus)))
        coverage|=seen
        if result['status']=='type_error' and len(found)<10:
            witness=out.with_name(out.stem+'-found-'+str(len(found)+1)+'.json');witness.write_text(json.dumps(p,indent=2)+'\n')
            found.append({'trial':counts['generated'],'elapsed_seconds':time.monotonic()-start,'path':str(witness.relative_to(ROOT.parent)),'sha256':sha(witness),'execution':result})
            if a.stop_on_find:break

        now=time.monotonic()
        if now-last>=5:save();last=now
    save(True);print(json.dumps({'out':str(out),'counts':counts,'elapsed_seconds':time.monotonic()-start,'found':len(found)}),flush=True)
if __name__=='__main__':main()

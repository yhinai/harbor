from pathlib import Path
import importlib.util, json, random, struct, zlib, itertools, time
ROOT=Path(__file__).resolve().parents[1]
def module(path):
    spec=importlib.util.spec_from_file_location('task_'+str(abs(hash(str(path)))),path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
rng=random.Random(371907)

def save(slug, inputs):
    ref=module(ROOT/slug/'audit/equivalent.py'); canon=module(ROOT/slug/'solution/canonical.py')
    cases=[]; started=time.monotonic()
    for i,(category,request) in enumerate(inputs):
        want=ref.solve(request); got=canon.solve(request)
        if slug=='atomic-range-history': ok=(want['order'] is None and got['order'] is None) or (want['order'] is not None and ref.valid(request,got['order']))
        elif slug=='alignment-relaxation': ok=got['size']==want['size'] and ref.measure(request,got['widths'])==want['size']
        elif slug=='exact-fused-dot': ok=int(want['bits'],16)==int(got['bits'],16) and set(want['flags'])==set(got['flags'])
        else: ok=want==got
        if not ok: raise AssertionError((slug,i,category,request,want,got))
        cases.append({'id':f'{i:05d}','category':category,'request':request,'expected':want})
    (ROOT/slug/'tests/cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
    (ROOT/slug/'environment/examples.json').write_text(json.dumps(cases[:3],indent=2)+'\n')
    print(slug,len(cases),'cross-checks',round(time.monotonic()-started,3),'seconds',flush=True)

# All products in a six-bit format under all rounding modes; randomized wide inputs.
items=[]; modes=['RNE','RNA','RTZ','RUP','RDN']
for mode in modes:
    items.append(('empty',{'ebits':3,'fbits':2,'mode':mode,'pairs':[]}))
    for a,b in itertools.product(range(64),repeat=2):
        items.append(('exhaustive-toy-product',{'ebits':3,'fbits':2,'mode':mode,'pairs':[[hex(a)[2:],hex(b)[2:]]]}))
for e,f in [(3,3),(5,10),(8,7),(8,23),(11,52)]:
    S=1<<(e+f); inf=((1<<e)-1)<<f; bias=(1<<(e-1))-1
    one=bias<<f; half=(bias-1)<<f; small=1; maxfinite=inf-1
    special=[0,S,small,small|S,one,one|S,inf,inf|S,inf+1,inf+(1<<(f-1)),maxfinite,maxfinite|S]
    pairsets=[[(maxfinite,maxfinite),(maxfinite|S,maxfinite),(small,one)],[(one,one),(half,small)],[(one,one),(one,one|S)],[(S,one),(0,one|S)],[(small,half)],[(maxfinite,one),(maxfinite,one)],[(inf,one),(inf|S,one)],[(inf+(1<<(f-1)),one),(0,inf)],[(inf,0)],[(inf+1,one)]]
    if bias>f: pairsets += [[(one,one),((bias-f-1)<<f,one)],[(one|1,one),((bias-f-1)<<f,one)]]
    for mode,pairs in itertools.product(modes,pairsets):
        items.append(('boundary-and-cancellation',{'ebits':e,'fbits':f,'mode':mode,'pairs':[[hex(a)[2:],hex(b)[2:]] for a,b in pairs]}))
    for i in range(100):
        pairs=[(rng.randrange(S*2),rng.randrange(S*2)) for _ in range(rng.randrange(1,14))]
        if i%3==0: pairs += [(rng.choice(special),rng.choice(special))]
        items.append(('random-format',{'ebits':e,'fbits':f,'mode':rng.choice(modes),'pairs':[[hex(a)[2:],hex(b)[2:]] for a,b in pairs]}))
# Dot order does not affect exact sum.
base=items[-100:]
for category,r in base:
    shuffled=r['pairs'].copy(); rng.shuffle(shuffled)
    items.append(('permuted-terms',dict(r,pairs=shuffled)))
save('exact-fused-dot',items)

items=[
('empty',{'memory':[0],'threads':[[]]}),
('store-buffering',{'memory':[0,0],'threads':[[['store',0,1,1],['load',1,1]],[['store',1,1,1],['load',0,1]]]}),
('partial-forwarding',{'memory':[1,2,3,4],'threads':[[['store',0,4,0x11223344],['store',1,2,0xaabb],['load',0,4],['fence']]]}),
('fenced-store-buffering',{'memory':[0,0],'threads':[[['store',0,1,1],['fence'],['load',1,1]],[['store',1,1,1],['fence'],['load',0,1]]]}),
('locked-exchange',{'memory':[0,0],'threads':[[['store',0,1,1],['xchg',1,1,2]],[['load',1,1],['load',0,1]]]}),
('cross-thread-pending',{'memory':[0,0,0,0],'threads':[[['store',0,4,0xdeadbeef],['load',0,4]],[['xchg',1,2,0x1234],['load',0,4]]]}),
('max-bounds',{'memory':[0]*8,'threads':[[['store',0,4,1],['load',4,4],['fence'],['xchg',4,4,2]],[['store',4,4,3],['load',0,4],['fence']],[['store',1,2,9],['load',0,4],['load',4,4]]]}),
]
for i in range(65):
    nt=rng.randrange(1,4); memory=[rng.randrange(4) for _ in range(4)]; threads=[]
    for _ in range(nt):
        code=[]
        for j in range(rng.randrange(1,4)):
            op=rng.choices(['store','load','xchg','fence'],[5,5,2,1])[0]
            if op=='fence': code.append([op]); continue
            width=rng.choice([1,2,4]); addr=rng.randrange(5-width)
            code.append([op,addr,width]+([rng.randrange(min(1<<(8*width),10000))] if op in ('store','xchg') else []))
        threads.append(code)
    items.append(('random-overlap',{'memory':memory,'threads':threads}))
save('mixed-width-tso',items)

items=[
('empty',{'initial':{},'final':{},'transactions':[]}),
('single',{'initial':{},'final':{'a':1},'transactions':[{'id':'t0','start':0,'end':2,'ops':[['put','a',1]]}]}),
('absent-versus-zero',{'initial':{},'final':{},'transactions':[{'id':'t0','start':0,'end':2,'ops':[['get','a',0]]}]}),
('write-skew',{'initial':{'a':0,'b':0},'final':{'a':1,'b':1},'transactions':[{'id':'a','start':0,'end':4,'ops':[['get','b',0],['put','a',1]]},{'id':'b','start':0,'end':4,'ops':[['get','a',0],['put','b',1]]}]}),
('must-backtrack',{'initial':{},'final':{'a':1},'transactions':[{'id':'first-in-input','start':0,'end':10,'ops':[['put','a',1]]},{'id':'must-run-first','start':0,'end':10,'ops':[['get','a',None]]}]}),
('endpoint-order',{'initial':{},'final':{'a':1},'transactions':[{'id':'w','start':0,'end':1,'ops':[['put','a',1]]},{'id':'r','start':1,'end':2,'ops':[['get','a',None]]}]}),
('range-phantom',{'initial':{},'final':{'b':1},'transactions':[{'id':'w','start':0,'end':1,'ops':[['put','b',1]]},{'id':'r','start':1,'end':2,'ops':[['scan','a','z',[]]]}]}),
('cas-delete-and-own-write',{'initial':{'a':0},'final':{},'transactions':[{'id':'t','start':0,'end':2,'ops':[['cas','a',0,1,True],['get','a',1],['cas','a',1,None,True],['get','a',None]]}]}),
('many-equivalent-orders',{'initial':{},'final':{},'transactions':[{'id':str(i),'start':0,'end':10,'ops':[['get','a',None]]*5} for i in range(10)]})
]
for i in range(130):
    initial={k:rng.randrange(-2,3) for k in 'abc' if rng.random()<0.5}; state=initial.copy(); tx=[]
    for j in range(rng.randrange(2,7)):
        ops=[]
        for _ in range(rng.randrange(1,5)):
            kind=rng.choice(['get','put','del','cas','scan']); key=rng.choice('abc')
            if kind=='get': ops.append([kind,key,state.get(key)])
            elif kind=='put':
                v=rng.randrange(-2,3); state[key]=v; ops.append([kind,key,v])
            elif kind=='del': state.pop(key,None); ops.append([kind,key])
            elif kind=='cas':
                old=state.get(key) if rng.random()<0.7 else 9; new=rng.choice([None,-1,0,1]); ok=state.get(key)==old
                ops.append([kind,key,old,new,ok])
                if ok:
                    if new is None: state.pop(key,None)
                    else: state[key]=new
            else: ops.append(['scan','a','z',[[k,state[k]] for k in sorted(state)]])
        tx.append({'id':f't{j}','start':0,'end':10,'ops':ops})
    final=state.copy(); rng.shuffle(tx)
    if i%3==0:
        obs=[op for t in tx for op in t['ops'] if op[0] in ('get','cas','scan')]
        if obs:
            op=rng.choice(obs)
            if op[0]=='get': op[2]=9
            elif op[0]=='cas': op[4]=not op[4]
            else: op[3]=[['a',9]]
    if i%7==0: final['a']=9
    items.append(('random-atomic-history',{'initial':initial,'final':final,'transactions':tx}))
save('atomic-range-history',items)

items=[
('empty',{'limit':8,'items':[]}),
('forward-alignment',{'limit':8,'items':[['label','entry'],['branch','end'],['bytes',7],['align',8],['label','end']]}),
('self-branch',{'limit':2,'items':[['label','a'],['branch','a']]}),
('positive-exclusive-bound',{'limit':8,'items':[['branch','a'],['bytes',8],['label','a']]}),
('negative-inclusive-bound',{'limit':8,'items':[['label','a'],['bytes',6],['branch','a']]}),
('alignment-tie',{'limit':128,'items':[['branch','a'],['align',8],['label','a']]}),
]
for i in range(170):
    n=rng.randrange(1,9); body=[]
    for j in range(n):
        body += [['label',f'L{j}'],['branch',f'L{rng.randrange(n+1)}']]
        if rng.random()<0.7: body.append(['bytes',rng.randrange(0,20)])
        if rng.random()<0.65: body.append(['align',rng.choice([2,4,8,16,32])])
    body.append(['label',f'L{n}'])
    items.append(('random-alignment',{'limit':rng.choice([4,8,16,24,32]),'items':body}))
for n in (12,14):
    items.append(('max-branches',{'limit':128,'items':sum(([['label',f'L{i}'],['branch',f'L{(i+3)%n}'],['align',4]] for i in range(n)),[])}))
save('alignment-relaxation',items)


def frame(seq,kind,tid,payload=b''):
    body=struct.pack('<IIBI',len(payload),seq,kind,tid)+payload
    return body+struct.pack('<I',zlib.crc32(body))
def patch(pg,offset,data): return struct.pack('<HHH',pg,offset,len(data))+data
def seal(seq,tid,patches,count=None,digest=None):
    return frame(seq,3,tid,struct.pack('<II',len(patches) if count is None else count,zlib.crc32(b''.join(patches)) if digest is None else digest))
def req(log,checkpoint=0,pages=None): return {'pages':pages or ['00000000','00000000'],'checkpoint':checkpoint,'log':log.hex()}
p1=patch(0,0,b'\x11\x22'); p2=patch(0,1,b'\x33\x44'); p3=patch(1,3,b'\xff')
a=frame(1,1,1)+frame(2,2,1,p1)+seal(3,1,[p1]); b=frame(4,1,2)+frame(5,2,2,p2)+seal(6,2,[p2])
inter=frame(1,1,1)+frame(2,2,1,p1)+frame(3,1,2)+frame(4,2,2,p2)+seal(5,2,[p2])+seal(6,1,[p1])
items=[('empty',req(b'')),('commit',req(a)),('commit-order',req(inter)),('checkpoint-skip',req(a+b,3)),('checkpoint-straddle',req(a,2)),('semantic-seal-mismatch',req(frame(1,1,1)+frame(2,2,1,p1)+seal(3,1,[p1],count=2)+b)),('id-reuse',req(frame(1,1,1)+frame(2,2,1,p1)+frame(3,1,1)+frame(4,2,1,p3)+seal(5,1,[p3]))),('bad-bound-orphan',req(frame(1,2,5,patch(9,0,b'x'))+a)),('bad-sequence',req(a+frame(3,1,2)+b)),('abort',req(frame(1,1,1)+frame(2,2,1,p1)+frame(3,4,1)+seal(4,1,[p1]))),('empty-commit',req(frame(1,1,1)+seal(2,1,[]))),('orphan-valid',req(frame(1,2,5,p1)+seal(2,5,[p1])))]
for i in range(len(a+b)+1): items.append(('every-truncation-boundary',req((a+b)[:i])))
for i in range(len(b)):
    bad=bytearray(b); bad[i]^=0x80
    items.append(('every-corrupt-byte',req(a+bad+b)))
for i in range(150):
    active={}; log=b''; seq=0
    for j in range(rng.randrange(1,25)):
        seq+=rng.randrange(1,4); tid=rng.randrange(1,5); kind=rng.choices([1,2,3,4],[3,6,3,1])[0]
        if kind==1: active[tid]=[]; log+=frame(seq,1,tid)
        elif kind==2:
            pg=rng.randrange(2); offset=rng.randrange(4); payload=patch(pg,offset,bytes(rng.randrange(256) for _ in range(rng.randrange(1,5-offset))))
            if tid in active: active[tid].append(payload)
            log+=frame(seq,2,tid,payload)
        elif kind==3:
            writes=active.pop(tid,[]); log+=seal(seq,tid,writes,count=len(writes)+(1 if rng.random()<0.2 else 0))
        else: active.pop(tid,None); log+=frame(seq,4,tid)
    if i%3==0: log=log[:rng.randrange(len(log)+1)]
    items.append(('random-incarnations',req(log,checkpoint=rng.randrange(seq+3))))
# All header, shape and bound classes; complete bad records must stop replay.
for kind,tid,payload in [(0,1,b''),(5,1,b''),(1,0,b''),(1,1,b'x'),(4,1,b'x'),(3,1,b'123'),(2,1,b'123'),(2,1,struct.pack('<HHH',0,0,0)),(2,1,struct.pack('<HHH',0,0,2)+b'x'),(2,1,patch(0,4,b'x')),(2,1,b'x'*4097)]:
    items.append(('malformed-shape',req(a+frame(4,kind,tid,payload)+b)))
items.append(('max-pages',req(frame(1,1,1)+frame(2,2,1,patch(7,0,b'x'*64))+seal(3,1,[patch(7,0,b'x'*64)]),pages=['00'*64]*8)))
items.append(('digest-mismatch-count-correct',req(frame(1,1,1)+frame(2,2,1,p1)+seal(3,1,[p1],digest=zlib.crc32(p1)^1)+b)))
save('checkpointed-journal',items)

"""Check that every hidden/public input obeys its published bounds."""
from pathlib import Path
import collections,datetime,json,re
ROOT=Path(__file__).resolve().parents[1]
def hexbytes(s):
 assert isinstance(s,str) and len(s)%2==0 and re.fullmatch('[0-9a-fA-F]*',s)
 return bytes.fromhex(s)
def verify(slug,r):
 if slug=='exact-fused-dot':
  e,f=r['ebits'],r['fbits']; assert 3<=e<=11 and 2<=f<=52 and 1+e+f<=64 and r['mode'] in ['RNE','RNA','RTZ','RUP','RDN'] and len(r['pairs'])<=64
  for pair in r['pairs']:
   assert len(pair)==2
   for h in pair: assert re.fullmatch('[0-9a-fA-F]+',h) and 0<=int(h,16)<2**(1+e+f)
 elif slug=='mixed-width-tso':
  assert 1<=len(r['memory'])<=8 and all(type(x)is int and 0<=x<256 for x in r['memory'])
  assert 1<=len(r['threads'])<=3 and sum(map(len,r['threads']))<=10
  for thread in r['threads']:
   assert len(thread)<=4
   for op in thread:
    if op[0]=='fence': assert op==['fence']; continue
    assert op[0] in ['store','load','xchg']; assert op[2] in [1,2,4] and 0<=op[1]<=len(r['memory'])-op[2]
    assert len(op)==(3 if op[0]=='load' else 4)
    if op[0]!='load': assert type(op[3])is int and 0<=op[3]<2**(8*op[2])
 elif slug=='atomic-range-history':
  tx=r['transactions']; assert len(tx)<=10 and len({t['id'] for t in tx})==len(tx)
  keys=set(r['initial'])|set(r['final'])
  values=list(r['initial'].values())+list(r['final'].values())
  for t in tx:
   assert type(t['start'])is int and type(t['end'])is int and t['start']<t['end'] and 1<=len(t['ops'])<=5
   for op in t['ops']:
    keys.add(op[1]); assert op[0] in ['get','put','del','cas','scan']
    if op[0]=='scan':
     keys.add(op[2]); assert op[1]<op[2]
     assert op[3]==sorted(op[3]) and len({k for k,v in op[3]})==len(op[3])
     for k,v in op[3]: keys.add(k); values.append(v); assert op[1]<=k<op[2]
    elif op[0]=='cas': assert type(op[4])is bool; values.extend(op[2:4])
    elif op[0] in ['get','put']: values.append(op[2])
  assert len(keys)<=6 and all(re.fullmatch('[a-z]+',k) for k in keys)
  assert all(v is None or type(v)is int and -9<=v<=9 for v in values)
 elif slug=='alignment-relaxation':
  assert 1<=r['limit']<=128 and len(r['items'])<=60
  labels=[v for k,v in r['items'] if k=='label']; assert len(labels)<=20 and len(set(labels))==len(labels)
  assert sum(k=='branch' for k,v in r['items'])<=14
  for kind,v in r['items']:
   assert kind in ['label','branch','bytes','align']
   if kind=='branch': assert v in labels
   elif kind=='bytes': assert type(v)is int and 0<=v<=256
   elif kind=='align': assert v in [1,2,4,8,16,32,64]
 elif slug=='checkpointed-journal':
  pages=list(map(hexbytes,r['pages'])); assert 1<=len(pages)<=8 and 1<=len(pages[0])<=64 and len({len(p) for p in pages})==1
  assert type(r['checkpoint'])is int and r['checkpoint']>=0 and len(hexbytes(r['log']))<=65536
 else: raise AssertionError(slug)

def main():
 report={'label':'verified','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Published input bounds and public examples; no agent difficulty measurement','tasks':{}}
 from selection import RETAINED
 for slug in RETAINED:
  path=ROOT/slug/'task.toml'
  slug=path.parent.name; hidden=json.loads((path.parent/'tests/cases.json').read_text()); public=json.loads((path.parent/'environment/examples.json').read_text())
  for c in hidden+public: verify(slug,c['request'])
  report['tasks'][slug]={'hidden_inputs_checked':len(hidden),'public_inputs_checked':len(public),'categories':dict(collections.Counter(c['category'] for c in hidden))}
 (ROOT/'evidence/input-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('All hidden and public inputs obey their published bounds.')
if __name__=='__main__':main()

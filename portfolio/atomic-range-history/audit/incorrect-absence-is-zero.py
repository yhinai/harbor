import json,sys
from functools import lru_cache

def run(state,ops):
    d=dict(state)
    for op in ops:
        k=op[0]
        if k=='get':
            if d.get(op[1],0)!=op[2]: return None
        elif k=='put': d[op[1]]=op[2]
        elif k=='del': d.pop(op[1],None)
        elif k=='cas':
            _,key,old,new,expected=op; ok=d.get(key)==old
            if ok!=expected: return None
            if ok:
                if new is None: d.pop(key,None)
                else: d[key]=new
        else:
            _,lo,hi,expected=op
            if [[key,d[key]] for key in sorted(d) if lo<=key<hi]!=expected: return None
    return tuple(sorted(d.items()))

def solve(r):
    tx=r['transactions']; n=len(tx); allmask=(1<<n)-1
    before=[sum(1<<j for j,u in enumerate(tx) if u['end']<=t['start']) for t in tx]
    target=tuple(sorted(r['final'].items()))
    @lru_cache(None)
    def dfs(mask,state):
        if mask==allmask: return () if state==target else None
        for i,t in enumerate(tx):
            if mask>>i&1 or before[i]&~mask: continue
            new=run(state,t['ops'])
            if new is None: continue
            suffix=dfs(mask|(1<<i),new)
            if suffix is not None: return (t['id'],)+suffix
        return None
    ans=dfs(0,tuple(sorted(r['initial'].items())))
    return {'order':None if ans is None else list(ans)}
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

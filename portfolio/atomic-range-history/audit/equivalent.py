# Independent exhaustive oracle: permutations and direct transaction replay.
import itertools,json,sys

def valid(r,order):
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
                if (d[op[1]] if op[1] in d else None)!=op[2]: return False
            elif op[0]=='put': d.update({op[1]:op[2]})
            elif op[0]=='del':
                if op[1] in d: del d[op[1]]
            elif op[0]=='cas':
                _,key,old,new,want=op; observed=d[key] if key in d else None
                ok=observed==old
                if ok is not want: return False
                if ok:
                    if new is None:
                        if key in d: del d[key]
                    else: d[key]=new
            else:
                got=sorted([[key,value] for key,value in d.items() if op[1]<=key<op[2]])
                if got!=op[3]: return False
    return d==r['final']
def solve(r):
    for perm in itertools.permutations(t['id'] for t in reversed(r['transactions'])):
        if valid(r,list(perm)): return {'order':list(perm)}
    return {'order':None}
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

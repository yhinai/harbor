# Independent recursive enumeration and prefix-location representation.
import itertools,json,sys

def measure(r,widths):
    offsets=[0]; labels={}; branch_at=[]; wi=iter(widths)
    for idx,item in enumerate(r['items']):
        kind,v=item; old=offsets[-1]
        if kind=='label': labels[v]=idx; new=old
        elif kind=='bytes': new=old+v
        elif kind=='align': new=old+(v-old%v)%v
        else:
            w=next(wi); branch_at.append((idx,v,w)); new=old+w
        offsets.append(new)
    for idx,target,w in branch_at:
        displacement=offsets[labels[target]]-offsets[idx+1]
        if w==2 and not(-r['limit']<=displacement<=r['limit']-1): return None
    return offsets[-1]

def solve(r):
    n=sum(x[0]=='branch' for x in r['items']); best=None
    for widths in itertools.product((5,2),repeat=n):
        size=measure(r,widths)
        if size is not None and (best is None or size<best['size']): best={'widths':list(widths),'size':size}
    return best
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

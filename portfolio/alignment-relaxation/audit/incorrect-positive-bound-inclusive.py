import json,sys

def layout(r,widths):
    pc=0; labels={}; branches=[]; i=0
    for kind,value in r['items']:
        if kind=='label': labels[value]=pc
        elif kind=='bytes': pc+=value
        elif kind=='align': pc=(-(-pc//value))*value
        else:
            w=widths[i]; i+=1; branches.append((pc,w,value)); pc+=w
    valid=all(w==5 or -r['limit']<=labels[t]-(p+w)<=r['limit'] for p,w,t in branches)
    return pc,valid

def solve(r):
    n=sum(k=='branch' for k,_ in r['items']); best=None
    for mask in range(1<<n):
        widths=[5 if mask>>i&1 else 2 for i in range(n)]
        size,ok=layout(r,widths)
        if ok and (best is None or size<best['size']): best={'widths':widths,'size':size}
    return best
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

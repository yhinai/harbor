import json,sys

def layout(r,widths):
    pc=0; labels={}; branches=[]; i=0
    for kind,value in r['items']:
        if kind=='label': labels[value]=pc
        elif kind=='bytes': pc+=value
        elif kind=='align': pc=(-(-pc//value))*value
        else:
            w=widths[i]; i+=1; branches.append((pc,w,value)); pc+=w
    valid=all(w==5 or -r['limit']<=labels[t]-(p+w)<r['limit'] for p,w,t in branches)
    return pc,valid


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
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

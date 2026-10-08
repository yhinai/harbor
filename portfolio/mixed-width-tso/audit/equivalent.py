# Independent model: per-store dictionaries, immutable BFS frontiers.
import json,sys
from collections import deque

def solve(r):
    codes=r['threads']; nt=len(codes)
    initial=(tuple(r['memory']),tuple((0,(),()) for _ in codes))
    q=deque([initial]); reached={initial}; finals=set()
    while q:
        mem,threads=q.popleft()
        if all(pos==len(codes[i]) and not pending for i,(pos,pending,obs) in enumerate(threads)):
            finals.add((tuple(t[2] for t in threads),mem)); continue
        for t,(pos,pending,obs) in enumerate(threads):
            options=[]
            if pending:
                new=list(mem)
                for address,byte in pending[0]: new[address]=byte
                options.append((tuple(new),(pos,pending[1:],obs)))
            if pos<len(codes[t]):
                instr=codes[t][pos]; kind=instr[0]
                if kind=='store':
                    _,a,w,v=instr; store=tuple((a+j,(v>>(8*j))&255) for j in range(w))
                    options.append((mem,(pos+1,pending+(store,),obs)))
                elif kind=='load':
                    _,a,w=instr; value=0
                    for j in range(w):
                        byte=mem[a+j]
                        for store in reversed(pending):
                            d=dict(store)
                            if a+j in d: byte=d[a+j]; break
                        value |= byte<<(8*j)
                    options.append((mem,(pos+1,pending,obs+(value,))))
                elif not pending:
                    if kind=='fence': options.append((mem,(pos+1,pending,obs)))
                    else:
                        _,a,w,v=instr; new=list(mem)
                        old=sum(mem[a+j]<<(8*j) for j in range(w))
                        for j in range(w): new[a+j]=(v>>(8*j))&255
                        options.append((tuple(new),(pos+1,pending,obs+(old,))))
            for memory,newthread in options:
                ts=list(threads); ts[t]=newthread; state=memory,tuple(ts)
                if state not in reached: reached.add(state); q.append(state)
    return {'outcomes':[{'reads':[list(x) for x in obs],'memory':list(mem)} for obs,mem in sorted(finals)]}
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

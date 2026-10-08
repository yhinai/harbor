import json,sys

def solve(r):
    code=r['threads']; n=len(code)
    start=((0,)*n,tuple(() for _ in code),tuple(r['memory']),tuple(() for _ in code))
    todo=[start]; seen={start}; outcomes=set()
    def modify(t,i,v): return t[:i]+(v,)+t[i+1:]
    def write(mem,a,w,v): return mem[:a]+tuple(v.to_bytes(w,'little'))+mem[a+w:]
    while todo:
        pc,buff,mem,reads=todo.pop()
        if all(pc[i]==len(code[i]) for i in range(n)):
            outcomes.add((reads,mem)); continue
        successors=[]
        for i in range(n):
            if buff[i]:
                a,w,v=buff[i][0]
                successors.append((pc,modify(buff,i,buff[i][1:]),write(mem,a,w,v),reads))
            if pc[i]==len(code[i]): continue
            op,*args=code[i][pc[i]]; np=modify(pc,i,pc[i]+1)
            if op=='store': successors.append((np,modify(buff,i,buff[i]+(tuple(args),)),mem,reads))
            elif op=='load':
                a,w=args; bs=list(mem[a:a+w])
                for ba,bw,bv in buff[i]:
                    for off,byte in enumerate(bv.to_bytes(bw,'little')):
                        if a<=ba+off<a+w: bs[ba+off-a]=byte
                v=int.from_bytes(bs,'little')
                successors.append((np,buff,mem,modify(reads,i,reads[i]+(v,))))
            elif not buff[i]:
                if op=='fence': successors.append((np,buff,mem,reads))
                else:
                    a,w,v=args; old=int.from_bytes(mem[a:a+w],'little')
                    successors.append((np,buff,write(mem,a,w,v),modify(reads,i,reads[i]+(old,))))
        for state in successors:
            if state not in seen: seen.add(state); todo.append(state)
    return {'outcomes':[{'reads':[list(t) for t in rs],'memory':list(m)} for rs,m in sorted(outcomes)]}
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))

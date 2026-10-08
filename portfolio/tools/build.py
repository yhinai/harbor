from pathlib import Path
import json, textwrap
ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['exact-fused-dot','mixed-width-tso','atomic-range-history','alignment-relaxation','checkpointed-journal']
def put(path, text):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip())
for slug in SLUGS:
    for d in ['environment','tests','solution','audit']:
        (ROOT/slug/d).mkdir(parents=True,exist_ok=True)
    put(f'{slug}/task.toml',f'''
    version = "1.0"
    [task]
    name = "portfolio/{slug}"
    version = "1.0.3"
    description = "Implement a specified systems algorithm with behavioral verification"
    keywords = ["systems", "correctness", "offline", "python"]
    [metadata]
    category = "software-engineering"
    tags = ["systems", "offline", "semantic-correctness"]
    [agent]
    user = "agent"
    timeout_sec = 1800.0
    [verifier]
    timeout_sec = 180.0
    user = "root"
    [environment]
    build_timeout_sec = 600.0
    cpus = 2
    memory_mb = 1024
    storage_mb = 2048
    network_mode = "no-network"
    ''')
    put(f'{slug}/environment/Dockerfile','''
    FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
    WORKDIR /app
    COPY main.py smoke.py examples.json /app/
    RUN useradd --create-home --uid 1000 agent && chown -R agent:agent /app && mkdir -p /tests /solution && chmod 700 /tests && chmod 755 /solution
    USER agent
    ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
    ''')
    put(f'{slug}/environment/main.py','''
    import json, sys
    def solve(request):
        raise NotImplementedError("Implement the contract in instruction.md")
    if __name__ == '__main__':
        for line in sys.stdin:
            print(json.dumps(solve(json.loads(line))))
    ''')
    put(f'{slug}/solution/solve.sh','''
    #!/bin/bash
    set -euo pipefail
    task_solution_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
    cp "$task_solution_dir/canonical.py" "${APP_DIR:-/app}/main.py"
    ''')
    put(f'{slug}/tests/test.sh','''
    #!/bin/bash
    set -euo pipefail
    task_test_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
    exec python3 -I "$task_test_dir/grade.py"
    ''')
    for f in ['solution/solve.sh','tests/test.sh']:
        (ROOT/slug/f).chmod(0o755)

PROTOCOL='''
## Interface and environment
Implement `/app/main.py`. It is invoked as `python3 /app/main.py` with `/app`
as the working directory. Read newline-delimited JSON objects from stdin and
write one JSON object per input line to stdout, in the same order. No extra
stdout text. Diagnostics may go to stderr. Handle multiple requests in one
process. Input is valid JSON and obeys the bounds below; malformed semantic
objects need not be supported except where explicitly specified.

CPU-only, Python 3.12 and its standard library; no network or package installation
is needed. You may add readable helper files under `/app`. The verifier runs the
program with ordinary unprivileged file access; it must not need to modify
system files or read evaluator files. The entire verification batch has a
60-second execution allowance on 2 CPUs and 1 GiB RAM. Output object key order and
whitespace do not matter. Extra object fields are ignored.

`python3 /app/smoke.py` runs a few public examples.
'''
put('exact-fused-dot/instruction.md', '''
# Exact fused dot product
Implement a bit-exact fused dot product for a parameterized binary format.
All multiplication and accumulation are exact; round only the final sum.

## Request and encoding
`{"ebits":3,"fbits":2,"mode":"RNE","pairs":[["0c","0c"]]}`
Here `3 <= ebits <= 11`, `2 <= fbits <= 52`, `1+ebits+fbits <= 64`, and
there are 0 to 64 pairs. A bit pattern is a hexadecimal string of any sufficient
length, without `0x`, within the format's bit width. Bit fields from most to
least significant are sign, exponent (`ebits`), fraction (`fbits`). Let
`bias = 2**(ebits-1)-1`, `F = 2**fbits`, and `Eall = 2**ebits-1`.
* For `0 < e < Eall`, value is `(-1)**s * (F+f) * 2**(e-bias-fbits)`.
* For `e == 0`, value is `(-1)**s * f * 2**(1-bias-fbits)`, including signed zero.
* For `e == Eall, f == 0`, the value is signed infinity.
* For `e == Eall, f != 0`, it is a NaN. Its top fraction bit distinguishes
  quiet (1) from signaling (0). The canonical NaN has sign 0, exponent Eall,
  and only the top fraction bit set.

## Exceptional terms
Inspect every operand, even when another is NaN. A signaling NaN, zero times
infinity (in either order), or both positive and negative infinite products
raises `invalid`. A pair with a NaN operand contributes no infinite product
and cannot itself count as zero times infinity. Any NaN operand or `invalid`
produces the canonical NaN; no other flags are set. Otherwise an infinite
product produces the corresponding infinity, with no flags.

## Finite rounding and flags
Sum exact products, then round to this format using:
* `RNE`: nearest, ties to an even significand (low stored fraction bit 0).
* `RNA`: nearest, ties away from zero.
* `RTZ`: toward zero; `RUP`: toward positive infinity; `RDN`: toward negative infinity.

Let `emin = 1-bias`, `emax = Eall-1-bias`. If the exact nonzero magnitude is
`x` and `L=floor(log2(x))`, use quantum `q=2**max(emin-fbits,L-fbits)`.
Round `x/q` to an integer with the chosen mode and original sign, giving
magnitude `y`. These formulas define rounding even outside the finite range.
If `y >= 2**(emax+1)`, raise `overflow` and `inexact`: output signed infinity
for nearest modes and for the directed mode pointing away from zero, otherwise
signed maximum finite. For other results, raise `inexact` iff `y != x`;
raise `underflow` iff inexact and the rounded magnitude is below `2**emin`
(tininess after rounding). These are the complete flag rules.

Exact zero has negative sign iff all products are negative signed zeros and
there is at least one product, or the mode is `RDN`. A cancellation involving
nonzero products is thus positive zero except in `RDN`. An empty dot product
is positive zero except in `RDN`. A nonzero result rounded to zero retains its
exact sign. Product zero signs are operand sign XOR.

## Response
`{"bits":"0c","flags":[]}` for the request above.
Return a valid format bit pattern as hex, with no `0x`; case and leading zeros
are immaterial. `flags` is a duplicate-free list drawn from `invalid`,
`overflow`, `underflow`, `inexact`; its order is immaterial.
'''+PROTOCOL)
put('exact-fused-dot/solution/canonical.py',r'''
import json, sys

def solve(r):
    e,f=r['ebits'],r['fbits']; bias=(1<<(e-1))-1; all_e=(1<<e)-1
    signbit=1<<(e+f); inf=all_e<<f; nan=inf|(1<<(f-1)); mode=r['mode']
    width=(1+e+f+3)//4
    def out(bits,flags=()): return {'bits':format(bits,f'0{width}x'),'flags':list(flags)}
    def decode(h):
        b=int(h,16); s=bool(b&signbit); ex=(b>>f)&all_e; fr=b&((1<<f)-1)
        if ex==all_e: return (s,'nan' if fr else 'inf',fr,0)
        return (s,'finite',fr if ex==0 else (1<<f)+fr, (1-bias if ex==0 else ex-bias)-f)
    invalid=False; hasn=False; infinities=set(); terms=[]; zeros=[]
    for a,b in r['pairs']:
        a,b=decode(a),decode(b)
        if any(v[1]=='nan' and not(v[2]&(1<<(f-1))) for v in (a,b)): invalid=True
        if a[1]=='nan' or b[1]=='nan': hasn=True; continue
        s=a[0]^b[0]
        if a[1]=='inf' or b[1]=='inf':
            if (a[1]=='finite' and a[2]==0) or (b[1]=='finite' and b[2]==0): invalid=True
            else: infinities.add(s)
        else:
            terms.append(((-1 if s else 1)*a[2]*b[2],a[3]+b[3]))
            zeros.append(s if a[2]*b[2]==0 else None)
    invalid |= len(infinities)>1
    if hasn or invalid: return out(nan,['invalid'] if invalid else [])
    if infinities: return out(inf|(signbit if next(iter(infinities)) else 0))
    base=min((k for _,k in terms),default=0)
    n=sum(v<<(k-base) for v,k in terms)
    if n==0:
        neg=mode=='RDN' or bool(zeros) and all(x is True for x in zeros)
        return out(signbit if neg else 0)
    neg=n<0; n=abs(n); L=n.bit_length()-1+base
    q=max(1-bias-f,L-f); shift=q-base
    if shift>0: v,rem=divmod(n,1<<shift); den=1<<shift
    else: v,rem,den=n<<(-shift),0,1
    up=(mode=='RUP' and not neg or mode=='RDN' and neg) and rem!=0
    if mode in ('RNE','RNA'):
        up=2*rem>den or 2*rem==den and (mode=='RNA' or v%2==1)
    v+=bool(up)
    bitsign=signbit if neg else 0
    if v and v.bit_length()-1+q>all_e-1-bias:
        away=mode in ('RNE','RNA') or mode=='RUP' and not neg or mode=='RDN' and neg
        return out(bitsign|(inf if away else inf-1),['overflow','inexact'])
    flags=['inexact'] if rem else []
    if rem and (v==0 or v.bit_length()-1+q<1-bias): flags.append('underflow')
    if v==0: return out(bitsign,flags)
    lv=v.bit_length()-1+q
    if lv<1-bias:
        frac=v<<(q-(1-bias-f)); bits=frac
    else:
        exponent=lv+bias
        diff=lv-f-q
        sig=v>>diff if diff>=0 else v<<(-diff)
        bits=(exponent<<f)|(sig-(1<<f))
    return out(bitsign|bits,flags)

if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))
''')
put('exact-fused-dot/audit/equivalent.py',r'''
# Independent oracle: rational values, binary search over ordered encodings.
from fractions import Fraction as Q
import json,sys

def solve(r):
    e,f=r['ebits'],r['fbits']; B=2**(e-1)-1; M=(2**e-1)<<f; S=1<<(e+f); mode=r['mode']
    def pow2(n): return Q(2**n) if n>=0 else Q(1,2**(-n))
    def val(b):
        ex=b>>f; fr=b%2**f
        return (fr if ex==0 else 2**f+fr)*pow2((1-B if ex==0 else ex-B)-f)
    def result(b,flags=()): return {'bits':hex(b)[2:],'flags':list(flags)}
    def parts(h):
        b=int(h,16); magnitude=b&(S-1); ex=magnitude>>f; fr=magnitude%2**f
        return b>=S,ex,fr,magnitude
    got_nan=False; bad=False; signs=set(); total=Q(0); all_negative_zero=bool(r['pairs'])
    for hh,jj in r['pairs']:
        a,b=parts(hh),parts(jj)
        an=a[1]==2**e-1 and a[2]!=0; bn=b[1]==2**e-1 and b[2]!=0
        for t,isn in ((a,an),(b,bn)):
            if isn and t[2]<2**(f-1): bad=True
        if an or bn: got_nan=True; all_negative_zero=False; continue
        ai=a[3]==M; bi=b[3]==M; neg=a[0]!=b[0]
        if ai or bi:
            if a[3]==0 or b[3]==0: bad=True
            else: signs.add(neg)
            all_negative_zero=False
        else:
            product=val(a[3])*val(b[3]); total+=-product if neg else product
            all_negative_zero &= product==0 and neg
    bad |= len(signs)>1
    if got_nan or bad: return result(M+2**(f-1),['invalid'] if bad else [])
    if signs: return result(M+(S if True in signs else 0))
    if total==0: return result(S if mode=='RDN' or all_negative_zero else 0)
    neg=total<0; x=abs(total); sign=S if neg else 0
    maxv=val(M-1); nextv=pow2((2**e-2-B)+1)
    away=(mode=='RUP' and not neg) or (mode=='RDN' and neg)
    if x>maxv:
        over=x>=nextv or away or mode in ('RNE','RNA') and x>=(maxv+nextv)/2
        if over: return result(sign+(M if away or mode in ('RNE','RNA') else M-1),['overflow','inexact'])
        return result(sign+M-1,['inexact'])
    lo,hi=0,M-1
    while lo<hi:
        mid=(lo+hi+1)//2
        if val(mid)<=x: lo=mid
        else: hi=mid-1
    if val(lo)==x: return result(sign+lo)
    a,b=val(lo),val(lo+1)
    if mode=='RTZ': choice=lo
    elif mode in ('RUP','RDN'): choice=lo+1 if away else lo
    elif x-a<b-x: choice=lo
    elif x-a>b-x: choice=lo+1
    else: choice=lo+1 if mode=='RNA' or lo%2 else lo
    flags=['inexact']
    if val(choice)<pow2(1-B): flags.append('underflow')
    return result(sign+choice,flags)
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))
''')
put('mixed-width-tso/instruction.md', '''
# Exhaustive outcomes of a mixed-width buffered machine
Repair `/app/main.py` to enumerate every terminal observable outcome of the
finite machine below. It is a deliberately specified TSO-like teaching model,
not a claim about all behaviors of actual x86 hardware. All operations below
are atomic transitions, including multi-byte memory accesses.

## Request
`{"memory":[0,0],"threads":[[["store",0,1,1],["load",1,1]],[["store",1,1,1],["load",0,1]]]}`
There are 1 to 3 threads, each with 0 to 4 instructions, at most 10 instructions
total, and 1 to 8 initial memory bytes. Addresses are byte offsets, widths are
1, 2, or 4, and accesses fit in memory. Values are unsigned and fit their width.
Multi-byte values use little-endian byte order. Instructions are:
* `["store",address,width,value]`
* `["load",address,width]`
* `["fence"]`
* `["xchg",address,width,value]`

## Machine
Initially each thread has program counter 0, an empty FIFO store buffer, and
an empty observation list. Shared memory starts at the supplied bytes. At each
step choose exactly one enabled transition:
1. Execute the next instruction of any thread, in program order:
   * `store` appends the complete (address,width,value) store to that thread's
     FIFO buffer and advances its program counter. It does not change memory.
   * `load` reads each byte independently: the youngest buffered store in the
     same thread covering that byte wins; otherwise read shared memory. Assemble
     the bytes into one unsigned integer, append it to that thread's observation
     list, and advance. It does not block on a nonempty buffer.
   * `fence` is enabled only if that thread's buffer is empty. Advance its counter.
   * `xchg` is enabled only if that thread's buffer is empty. Atomically read the
     indicated shared-memory value, append it to this thread's observations,
     replace those bytes with the supplied value, and advance. It neither drains
     nor blocks on other threads' buffers.
2. Drain the oldest store of any nonempty thread buffer to shared memory, removing
   the store. All its bytes become visible together. Draining is possible even
   after the issuing thread finishes its instructions.

A state is terminal only when all threads finished AND every buffer is empty.
No fairness restriction changes the set of finite terminal executions.

## Response
`{"outcomes":[{"reads":[[0],[0]],"memory":[1,1]}, ...]}`
Return the complete set of distinct terminal observations. Each outcome contains
one observation list per thread, including empty lists, and the final memory
bytes. Outcome ordering is immaterial; duplicate outcomes are not allowed.
'''+PROTOCOL)
put('mixed-width-tso/solution/canonical.py',r'''
import json,sys

def solve(r):
    code=r['threads']; n=len(code)
    start=((0,)*n,tuple(() for _ in code),tuple(r['memory']),tuple(() for _ in code))
    todo=[start]; seen={start}; outcomes=set()
    def modify(t,i,v): return t[:i]+(v,)+t[i+1:]
    def write(mem,a,w,v): return mem[:a]+tuple(v.to_bytes(w,'little'))+mem[a+w:]
    while todo:
        pc,buff,mem,reads=todo.pop()
        if all(pc[i]==len(code[i]) and not buff[i] for i in range(n)):
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
''')
put('mixed-width-tso/audit/equivalent.py',r'''
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
''')
put('atomic-range-history/instruction.md', '''
# Linearizability of atomic range transactions
Implement a checker that returns a valid serial witness for a completed
concurrent history, or proves there is no witness. A whole transaction is one
atomic operation. Individual reads inside a transaction cannot interleave with
other transactions. The state is a finite map from string keys to integer values.

## Request
`{"initial":{},"final":{"a":1},"transactions":[{"id":"t0","start":0,"end":2,"ops":[["put","a",1]]}]}`
There are 0 to 10 transactions, each with 1 to 5 operations, and at most 6 keys
in all maps, operations, and scan boundaries combined. IDs are unique strings.
Times are integer endpoints with `start < end`. Initial and final maps contain
only present keys; a missing key is absent, different from a key holding zero.
Values are integers in [-9,9]. Keys are nonempty ASCII lowercase strings, compared
lexicographically. Each operation has its expected return value in the input:
* `["get",key,expected]`: expected is an integer or JSON null for absence.
* `["put",key,value]`: assigns value, no observed return.
* `["del",key]`: removes key if present, no observed return.
* `["cas",key,expected_old,new_value,expected_success]`: compare to expected_old
  (integer or null); on equality assign new_value (integer or null, meaning
  delete), and return a boolean that must equal expected_success. A failed CAS
  makes no change. Reading an absent key produces null.
* `["scan",low,high,expected_pairs]`: return all currently present keys k with
  `low <= k < high`, as `[key,value]` pairs sorted by key. It observes writes made
  earlier in the same transaction. Bounds satisfy low < high.

## Valid witness
Every transaction appears exactly once. If A.end <= B.start, A must occur before
B; overlapping intervals impose no order. Execute transactions in witness order,
starting from initial. Every observation must match and the final map must equal
`final`. This finite specification defines the question; there are no incomplete
operations or external consistency rules.

## Response
`{"order":["t0"]}` for the example. Any valid witness is accepted, regardless of
tie breaking. Return `{"order":null}` iff no valid order exists. An empty valid
history has `order: []`, not null.
'''+PROTOCOL)
put('atomic-range-history/solution/canonical.py',r'''
import json,sys
from functools import lru_cache

def run(state,ops):
    d=dict(state)
    for op in ops:
        k=op[0]
        if k=='get':
            if d.get(op[1])!=op[2]: return None
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
''')
put('atomic-range-history/audit/equivalent.py',r'''
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
''')
put('alignment-relaxation/instruction.md', '''
# Globally optimal branch layout with alignment
Implement an exact code-layout optimizer.

## Request
`{"limit":8,"items":[["label","entry"],["branch","end"],["bytes",7],["align",8],["label","end"]]}`
The location counter starts at zero. There are 0 to 60 items, up to 14 branches,
and up to 20 labels. Every branch target is a defined unique label. Items are:
* `["label",name]`: define a label at the current counter; emit no bytes.
* `["bytes",n]`: emit n bytes, where 0 <= n <= 256.
* `["align",a]`: emit the smallest nonnegative padding that makes the counter
  divisible by a, where a is one of 1,2,4,8,16,32,64.
* `["branch",target]`: choose width 2 (short) or 5 (long). A short branch at
  address p is valid iff `-limit <= address(target)-(p+2) < limit`.
  A long branch is always valid. `1 <= limit <= 128`.
Forward, backward, and self-target branches are allowed. A label immediately
before an align directive is defined before its padding. There is no trailing
alignment beyond explicit items.

## Objective and response
Minimize the final location counter, including padding, over all valid branch
width choices. Return `{"widths":[5],"size":16}` for the example above. Widths
are listed in branch appearance order. Any optimum is accepted. Report the size
of your chosen layout exactly.
'''+PROTOCOL)
put('alignment-relaxation/solution/canonical.py',r'''
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
    n=sum(k=='branch' for k,_ in r['items']); best=None
    for mask in range(1<<n):
        widths=[5 if mask>>i&1 else 2 for i in range(n)]
        size,ok=layout(r,widths)
        if ok and (best is None or size<best['size']): best={'widths':widths,'size':size}
    return best
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))
''')
put('alignment-relaxation/audit/equivalent.py',r'''
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
''')
put('checkpointed-journal/instruction.md', '''
# Recover a checkpointed transactional byte journal
Implement deterministic recovery of the custom format below. This is not the
SQLite format. Replay only structurally valid prefix records and only complete,
correctly sealed transactions newer than the supplied checkpoint.

## Request
`{"pages":["00000000"],"checkpoint":0,"log":""}`
There are 1 to 8 equal-length pages of 1 to 64 bytes, as hexadecimal strings.
They are the authoritative durable checkpoint image; no consistency check against
older journal records is required. `checkpoint` is a nonnegative sequence
watermark; it can fall between records or exceed the log's last sequence.
`log` is a hex byte string of at most 64 KiB; it may end with corrupted or torn
records. Hex case is immaterial. No other input is malformed.

## Binary records
All integers are unsigned, little-endian, with no implicit padding. A record is:
`payload_length:u32 | sequence:u32 | kind:u8 | transaction_id:u32 | payload | crc:u32`.
The fixed header is 13 bytes. CRC is `zlib.crc32(header + payload) & 0xffffffff`.
Sequence must be positive and strictly greater than the previous valid record's
sequence (initially 0). Payload length must be at most 4096. Transaction ID must
be positive. Kind and payload shapes are:
* 1 BEGIN: empty payload.
* 2 PATCH: `page_index:u16 | byte_offset:u16 | byte_count:u16 | data[byte_count]`.
  Count is positive, payload length is exactly 6+count, and the patch fits in an
  existing page, with zero-based page and byte indices.
* 3 COMMIT: exactly 8 bytes, `patch_count:u32 | digest:u32`. Digest is
  `zlib.crc32(concatenation_of_PATCH_payloads) & 0xffffffff` for this incarnation,
  in log order; the empty concatenation has CRC zero.
* 4 ABORT: empty payload.

Stop at the first incomplete record, invalid CRC, invalid sequence, invalid
header/kind/ID, or invalid payload shape/bounds. That record and all following
bytes are excluded from the valid prefix. A record must be structurally valid
before it has any semantic effect, including records for inactive transactions.

## Transaction and checkpoint rules
BEGIN starts a fresh incarnation of that ID, discarding any unfinished incarnation.
PATCH stages a byte patch only if that ID is active; otherwise it is ignored.
ABORT discards the active incarnation, if any. COMMIT always closes its active
incarnation, if any. A COMMIT applies all staged patches atomically, in patch
order, iff both count and digest match AND its sequence is greater than checkpoint.
A seal mismatch closes the active incarnation without applying its patches
and leaves the valid prefix intact. A matching COMMIT at or below checkpoint
is not replayed.
Orphan COMMIT/ABORT records have no effect. Uncommitted patches have no effect.

Transactions may interleave. Apply committed transactions in COMMIT order.
Records at/below checkpoint participate in prefix validation and transaction
state processing. Return the resulting pages, valid prefix length in BYTES,
and last valid record sequence (0 for an empty prefix).

## Response
`{"pages":["00000000"],"valid_bytes":0,"last_seq":0}` for the empty-log example.
Hex case is immaterial; returned page lengths must be unchanged.
'''+PROTOCOL)
put('checkpointed-journal/solution/canonical.py',r'''
import json,sys,struct,zlib

def solve(r):
    pages=[bytearray.fromhex(x) for x in r['pages']]; log=bytes.fromhex(r['log'])
    pos=0; last=0; active={}
    while pos+17<=len(log):
        length,seq,kind,tx=struct.unpack_from('<IIBI',log,pos); end=pos+17+length
        if length>4096 or end>len(log) or seq<=last or tx==0: break
        body=log[pos:pos+13+length]; payload=body[13:]
        if zlib.crc32(body)&0xffffffff!=struct.unpack_from('<I',log,end-4)[0]: break
        patch=None
        if kind in (1,4):
            if length: break
        elif kind==2:
            if length<6: break
            page,off,count=struct.unpack_from('<HHH',payload)
            if count==0 or length!=6+count or page>=len(pages) or off+count>len(pages[page]): break
            patch=(page,off,payload[6:])
        elif kind==3:
            if length!=8: break
        else: break
        if kind==1: active[tx]=([],0)
        elif kind==2 and tx in active:
            patches,digest=active[tx]; patches.append(patch)
            active[tx]=(patches,zlib.crc32(payload,digest)&0xffffffff)
        elif kind==4: active.pop(tx,None)
        elif kind==3:
            state=active.pop(tx,None)
            if state is not None:
                patches,digest=state; count,wanted=struct.unpack('<II',payload)
                if count==len(patches) and wanted==digest and seq>r['checkpoint']:
                    for page,off,data in patches: pages[page][off:off+len(data)]=data
        pos=end; last=seq
    return {'pages':[x.hex() for x in pages],'valid_bytes':pos,'last_seq':last}
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))
''')
put('checkpointed-journal/audit/equivalent.py',r'''
# Independent parser: integer slices; replay completed transaction bundles.
import json,sys,zlib

def solve(r):
    raw=bytes.fromhex(r['log']); records=[]; index=0; previous=0
    def uint(buf): return int.from_bytes(buf,'little')
    while len(raw)-index>=17:
        hdr=raw[index:index+13]; size=uint(hdr[:4]); seq=uint(hdr[4:8]); kind=hdr[8]; tid=uint(hdr[9:])
        stop=index+13+size+4
        if size>4096 or stop>len(raw) or seq<=previous or tid==0: break
        data=raw[index+13:stop-4]
        if uint(raw[stop-4:stop])!=zlib.crc32(hdr+data): break
        if kind not in (1,2,3,4): break
        if kind in (1,4) and data: break
        if kind==3 and len(data)!=8: break
        if kind==2:
            if len(data)<6: break
            pg,offset,amount=uint(data[:2]),uint(data[2:4]),uint(data[4:6])
            if not amount or len(data)!=6+amount or pg>=len(r['pages']) or offset+amount>len(bytes.fromhex(r['pages'][pg])): break
        records.append((seq,kind,tid,data)); previous=seq; index=stop
    bundles={}; committed=[]
    for seq,kind,tid,data in records:
        if kind==1: bundles[tid]=[]
        elif kind==2:
            if tid in bundles: bundles[tid].append(data)
        elif kind==4: bundles.pop(tid,None)
        else:
            writes=bundles.pop(tid,None)
            if writes is not None and uint(data[:4])==len(writes) and uint(data[4:])==zlib.crc32(b''.join(writes)) and seq>r['checkpoint']:
                committed.extend(writes)
    pages=[list(bytes.fromhex(p)) for p in r['pages']]
    for payload in committed:
        pg,offset=uint(payload[:2]),uint(payload[2:4])
        for i,b in enumerate(payload[6:]): pages[pg][offset+i]=b
    return {'pages':[bytes(p).hex() for p in pages],'valid_bytes':index,'last_seq':previous}
if __name__=='__main__':
    for line in sys.stdin: print(json.dumps(solve(json.loads(line))))
''')
print('Created five specifications and ten solution/reference implementations.')

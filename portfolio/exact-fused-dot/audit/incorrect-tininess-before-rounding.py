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
    if rem and (L<1-bias): flags.append('underflow')
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

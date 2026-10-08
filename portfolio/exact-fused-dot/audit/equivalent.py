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

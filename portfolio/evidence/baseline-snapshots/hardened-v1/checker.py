"""Reed static checker. Types include result types and cell-write effects."""
from dataclasses import dataclass
from language import StaticError,kind,validate

@dataclass(frozen=True)
class Function:
    result:object
    writes:frozenset

def scalar(k):return frozenset((k,))

def shape(t):
    return ('fn',shape(t.result)) if isinstance(t,Function) else ('scalar',t)

def join(a,b,mode='branch',depth=0):
    if isinstance(a,Function) and isinstance(b,Function):
        writes=a.writes | b.writes
        return Function(join(a.result,b.result,mode,depth+1),writes)
    if isinstance(a,frozenset) and isinstance(b,frozenset):return a|b
    raise StaticError('incompatible types at join')

class Checker:
    def __init__(self,p):
        self.bounds={n:frozenset(d['types']) for n,d in p['cells'].items()}
        self.inputs=set(p['inputs'])
        self.coverage=set()
    def hit(self,tag):self.coverage.add(tag)
    def need(self,t,k):
        if t!=scalar(k):raise StaticError('expected '+k)
    def expr(self,e,env,facts):
        op=e[0];self.hit('expr:'+op)
        if op=='lit':return scalar(kind(e[1])),frozenset()
        if op=='var':
            if e[1] not in env:raise StaticError('unknown variable')
            return env[e[1]],frozenset()
        if op=='get':
            if e[1] not in facts:raise StaticError('unknown cell')
            return facts[e[1]],frozenset()
        if op=='is':
            if e[1] not in facts:raise StaticError('unknown cell')
            return scalar('bool'),frozenset()
        if op=='fn':
            inner=env.copy();fresh=self.bounds.copy()
            writes=self.block(e[1],inner,fresh)
            result,more=self.expr(e[2],inner,fresh)
            return Function(result,writes|more),frozenset()
        if op=='call':
            t,w=self.expr(e[1],env,facts)
            if not isinstance(t,Function):raise StaticError('expected function')
            self.hit('call:nested' if isinstance(t.result,Function) else 'call:scalar')
            for n in t.writes:facts[n]=self.bounds[n]
            return t.result,w|t.writes
        if op=='not':
            t,w=self.expr(e[1],env,facts);self.need(t,'bool');return scalar('bool'),w
        a,wa=self.expr(e[1],env,facts);b,wb=self.expr(e[2],env,facts)
        k='text' if op=='cat' else 'int';self.need(a,k);self.need(b,k)
        return scalar('bool' if op=='lt' else k),wa|wb
    def block(self,body,env,facts):
        writes=frozenset()
        for s in body:
            op=s[0];self.hit('stmt:'+op)
            if op in ('let','assign','set','eval'):
                e=s[1] if op=='eval' else s[2]
                t,w=self.expr(e,env,facts);writes|=w
                if op=='let':
                    if s[1] in env or s[1] in self.bounds:raise StaticError('name already bound')
                    env[s[1]]=t
                elif op=='assign':
                    if s[1] not in env or s[1] in self.inputs:raise StaticError('variable not assignable')
                    if shape(t)!=shape(env[s[1]]):raise StaticError('assignment shape')
                    env[s[1]]=t
                elif op=='set':
                    if s[1] not in self.bounds or not isinstance(t,frozenset) or not t<=self.bounds[s[1]]:raise StaticError('cell assignment')
                    facts[s[1]]=t;writes|=frozenset((s[1],))
                continue
            t,w=self.expr(s[1],env,facts);writes|=w
            if op=='if':
                self.need(t,'bool')
                ea,eb=env.copy(),env.copy();fa,fb=facts.copy(),facts.copy()
                guard=s[1]
                if guard[0]=='is':
                    n,k=guard[1:];fa[n]=facts[n]&scalar(k);fb[n]=facts[n]-scalar(k)
                wa=self.block(s[2],ea,fa) if all(fa.values()) else frozenset()
                wb=self.block(s[3],eb,fb) if all(fb.values()) else frozenset()
                viable=[(ea,fa)] if not all(fb.values()) else [(eb,fb)] if not all(fa.values()) else [(ea,fa),(eb,fb)]
                for n in env:env[n]=viable[0][0][n] if len(viable)==1 else join(ea[n],eb[n])
                for n in facts:facts[n]=viable[0][1][n] if len(viable)==1 else fa[n]|fb[n]
                writes|=wa|wb
            else:
                self.need(t,'int')
                memo={}
                def signature(t):
                    return (shape(t.result),t.writes) if isinstance(t,Function) else t
                for _ in range(64):
                    before=(env.copy(),facts.copy());next_env=env.copy();next_facts=facts.copy()
                    writes|=self.block(s[2],next_env,next_facts)
                    for n in env:
                        key=(n,signature(env[n]),signature(next_env[n]))
                        if key not in memo:memo[key]=join(env[n],next_env[n],'loop')
                        env[n]=memo[key]
                    for n in facts:facts[n]|=next_facts[n]
                    if before==(env,facts):break
                else:raise StaticError('analysis limit')
        return writes

def check(p,coverage=None):
    validate(p);c=Checker(p)
    env={n:scalar(kind(v)) for n,v in p['inputs'].items()}
    facts={n:scalar(kind(d['value'])) for n,d in p['cells'].items()}
    try:c.block(p['body'],env,facts)
    finally:
        if coverage is not None:coverage.update(c.coverage)
    return True

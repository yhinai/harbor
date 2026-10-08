"""Concrete Reed interpreter, using an explicit stack of continuations."""
from dataclasses import dataclass
from language import RuntimeTypeError,StepLimit,MAX_STEPS,kind,validate

@dataclass
class Closure:
    body:list
    result:list
    captured:dict

class Machine:
    def __init__(self,p,limit=MAX_STEPS):
        self.cells={n:d['value'] for n,d in p['cells'].items()}
        self.steps=0;self.limit=limit;self.trace=[]
        self.values=[];self.work=[]
    def tick(self,label):
        if self.steps>=self.limit:raise StepLimit('step limit')
        self.steps+=1;self.trace.append({'step':self.steps,'operation':label})
    def require(self,v,k):
        actual='function' if isinstance(v,Closure) else kind(v)
        if actual!=k:raise RuntimeTypeError('expected '+k+', got '+actual)
    def schedule(self,body,env):
        for s in reversed(body):self.work.append(('statement',s,env))
    def execute(self,body,env):
        self.schedule(body,env)
        while self.work:
            tag,x,env=self.work.pop()
            if tag=='statement':
                op=x[0];self.tick('stmt:'+op)
                if op in ('let','assign','set'):
                    self.work.append((op,x[1],env));self.work.append(('expression',x[2],env))
                elif op=='eval':
                    self.work.append(('discard',None,env));self.work.append(('expression',x[1],env))
                else:
                    self.work.append((op,x,env));self.work.append(('expression',x[1],env))
            elif tag=='expression':
                op=x[0];self.tick('expr:'+op)
                if op=='lit':self.values.append(x[1])
                elif op=='var':self.values.append(env[x[1]])
                elif op=='get':self.values.append(self.cells[x[1]])
                elif op=='is':self.values.append(kind(self.cells[x[1]])==x[2])
                elif op=='fn':self.values.append(Closure(x[1],x[2],env.copy()))
                elif op in ('call','not'):
                    self.work.append((op,None,env));self.work.append(('expression',x[1],env))
                else:
                    self.work.append(('binary',op,env));self.work.append(('expression',x[2],env));self.work.append(('expression',x[1],env))
            elif tag in ('let','assign'):env[x]=self.values.pop()
            elif tag=='set':self.cells[x]=self.values.pop()
            elif tag=='discard':self.values.pop()
            elif tag=='call':
                f=self.values.pop();self.require(f,'function');local=f.captured.copy()
                self.work.append(('expression',f.result,local));self.schedule(f.body,local)
            elif tag=='not':
                a=self.values.pop();self.require(a,'bool');self.values.append(not a)
            elif tag=='binary':
                b=self.values.pop();a=self.values.pop();k='text' if x=='cat' else 'int'
                self.require(a,k);self.require(b,k)
                value=(a<b) if x=='lt' else (a+b)[:1024] if x=='cat' else ((a+b+2**31)%2**32)-2**31
                self.values.append(value)
            elif tag=='if':
                cond=self.values.pop();self.require(cond,'bool')
                self.work.append(('scope',set(env),env));self.schedule(x[2] if cond else x[3],env)
            elif tag=='repeat':
                count=self.values.pop();self.require(count,'int')
                old=set(env)
                for _ in range(max(0,min(3,count))):
                    self.work.append(('scope',old,env));self.schedule(x[2],env)
            elif tag=='scope':
                for n in set(env)-x:del env[n]
            else:raise AssertionError(tag)

def run(p,limit=MAX_STEPS):
    validate(p);m=Machine(p,limit)
    try:m.execute(p['body'],p['inputs'].copy())
    except RuntimeTypeError as e:return {'status':'type_error','message':str(e),'steps':m.steps,'trace':m.trace}
    except StepLimit:return {'status':'step_limit','steps':m.steps,'trace':m.trace}
    return {'status':'normal','steps':m.steps,'trace':m.trace}

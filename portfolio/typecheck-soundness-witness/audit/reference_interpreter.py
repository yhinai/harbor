"""Small direct evaluator used only to cross-check the concrete interpreter.
It does not import the static checker or the production Machine implementation.
"""
class TypeErrorInProgram(Exception):pass
class BudgetEnd(Exception):pass

def evaluate(p,limit=4096):
    cells={n:d['value'] for n,d in p['cells'].items()};steps=0
    def tick():
        nonlocal steps
        if steps==limit:raise BudgetEnd()
        steps+=1
    def expect(v,t):
        if t=='fn':good=isinstance(v,tuple) and len(v)==4 and v[0]=='closure'
        else:good=type(v) is {'int':int,'text':str,'bool':bool,'unit':type(None)}[t]
        if not good:raise TypeErrorInProgram()
    def expr(x,env):
        tick();op=x[0]
        if op=='lit':return x[1]
        if op=='var':return env[x[1]]
        if op=='get':return cells[x[1]]
        if op=='is':return type(cells[x[1]]) is {'int':int,'text':str,'bool':bool,'unit':type(None)}[x[2]]
        if op=='fn':return ('closure',x[1],x[2],dict(env))
        if op=='call':
            f=expr(x[1],env);expect(f,'fn');local=dict(f[3]);block(f[1],local);return expr(f[2],local)
        if op=='not':
            v=expr(x[1],env);expect(v,'bool');return not v
        a=expr(x[1],env);b=expr(x[2],env);t='text' if op=='cat' else 'int';expect(a,t);expect(b,t)
        if op=='add':return (a+b+2147483648)%4294967296-2147483648
        if op=='cat':return (a+b)[:1024]
        return a<b
    def block(body,env):
        for s in body:
            tick();op=s[0]
            if op in ('let','assign'):env[s[1]]=expr(s[2],env)
            elif op=='set':cells[s[1]]=expr(s[2],env)
            elif op=='eval':expr(s[1],env)
            elif op=='if':
                c=expr(s[1],env);expect(c,'bool');keys=set(env);block(s[2] if c else s[3],env)
                for n in set(env)-keys:env.pop(n)
            else:
                n=expr(s[1],env);expect(n,'int');keys=set(env)
                for _ in range(min(3,max(0,n))):
                    block(s[2],env)
                    for key in set(env)-keys:env.pop(key)
    try:block(p['body'],dict(p['inputs']))
    except TypeErrorInProgram:return {'status':'type_error','steps':steps}
    except BudgetEnd:return {'status':'step_limit','steps':steps}
    return {'status':'normal','steps':steps}

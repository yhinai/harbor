"""Parser and structural limits for the Reed language."""
import json,re
MAX_BYTES=65536
MAX_NODES=512
MAX_DEPTH=32
MAX_STEPS=4096
KINDS=frozenset(('int','text','bool','unit'))
class InvalidProgram(Exception): pass
class StaticError(Exception): pass
class RuntimeTypeError(Exception): pass
class StepLimit(Exception): pass

def kind(v):
    if v is None:return 'unit'
    if type(v) is bool:return 'bool'
    if type(v) is int and -(2**31)<=v<2**31:return 'int'
    if type(v) is str and len(v)<=1024:return 'text'
    raise InvalidProgram('invalid literal')

def name(v):
    if not isinstance(v,str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,23}',v):
        raise InvalidProgram('invalid name')
    return v

def load(text):
    if len(text.encode('utf-8'))>MAX_BYTES:raise InvalidProgram('file too large')
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise InvalidProgram('duplicate key')
            d[k]=v
        return d
    try:p=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(InvalidProgram('nonfinite number')))
    except (ValueError,RecursionError) as e:raise InvalidProgram(str(e)) from e
    validate(p);return p

def validate(p):
    if type(p) is not dict or set(p)!={'cells','inputs','body'}:raise InvalidProgram('program keys')
    if type(p['cells']) is not dict or len(p['cells'])>8:raise InvalidProgram('cells')
    if type(p['inputs']) is not dict or len(p['inputs'])>8:raise InvalidProgram('inputs')
    for n,d in p['cells'].items():
        name(n)
        if type(d) is not dict or set(d)!={'types','value'}:raise InvalidProgram('cell definition')
        ts=d['types']
        if type(ts) is not list or not ts or any(type(t) is not str or t not in KINDS for t in ts) or len(set(ts))!=len(ts):raise InvalidProgram('cell types')
        if kind(d['value']) not in ts:raise InvalidProgram('cell initial value')
    for n,v in p['inputs'].items():
        name(n);kind(v)
        if n in p['cells']:raise InvalidProgram('duplicate name')
    count=0
    def expr(e,depth):
        nonlocal count
        count+=1
        if depth>MAX_DEPTH or count>MAX_NODES:raise InvalidProgram('AST limit')
        if type(e) is not list or not e or type(e[0]) is not str:raise InvalidProgram('expression')
        op=e[0]
        arities={'lit':2,'var':2,'get':2,'add':3,'cat':3,'lt':3,'not':2,'is':3,'call':2,'fn':3}
        if op not in arities or len(e)!=arities[op]:raise InvalidProgram('expression operator/arity')
        if op=='lit':kind(e[1])
        elif op in ('var','get'):name(e[1])
        elif op=='is':
            name(e[1])
            if e[2] not in KINDS:raise InvalidProgram('is kind')
        elif op=='fn':block(e[1],depth+1);expr(e[2],depth+1)
        else:
            for x in e[1:]:expr(x,depth+1)
    def block(b,depth):
        nonlocal count
        if type(b) is not list or len(b)>128 or depth>MAX_DEPTH:raise InvalidProgram('block')
        for s in b:
            count+=1
            if count>MAX_NODES or type(s) is not list or not s or type(s[0]) is not str:raise InvalidProgram('statement')
            op=s[0]
            arities={'let':3,'assign':3,'set':3,'eval':2,'if':4,'repeat':3}
            if op not in arities or len(s)!=arities[op]:raise InvalidProgram('statement operator/arity')
            if op in ('let','assign','set'):name(s[1]);expr(s[2],depth+1)
            elif op=='eval':expr(s[1],depth+1)
            elif op=='if':expr(s[1],depth+1);block(s[2],depth+1);block(s[3],depth+1)
            else:expr(s[1],depth+1);block(s[2],depth+1)
    block(p['body'],1)
    return count

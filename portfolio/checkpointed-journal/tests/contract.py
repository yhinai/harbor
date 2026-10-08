import json

def valid_history(r,order):
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
                if d.get(op[1])!=op[2]: return False
            elif op[0]=='put': d[op[1]]=op[2]
            elif op[0]=='del': d.pop(op[1],None)
            elif op[0]=='cas':
                _,key,old,new,want=op; ok=d.get(key)==old
                if ok is not want: return False
                if ok:
                    if new is None: d.pop(key,None)
                    else: d[key]=new
            else:
                if sorted([[k,v] for k,v in d.items() if op[1]<=k<op[2]])!=op[3]: return False
    return d==r['final']

def layout_size(r,widths):
    if not isinstance(widths,list) or len(widths)!=sum(x[0]=='branch' for x in r['items']): return None
    if any(type(w) is not int or w not in (2,5) for w in widths): return None
    prefix=[0]; names={}; branches=[]; it=iter(widths)
    for i,(kind,v) in enumerate(r['items']):
        x=prefix[-1]
        if kind=='label': names[v]=i; y=x
        elif kind=='bytes': y=x+v
        elif kind=='align': y=x+(v-x%v)%v
        else:
            width=next(it); branches.append((i,v,width)); y=x+width
        prefix.append(y)
    for i,name,w in branches:
        if w==2 and not -r['limit']<=prefix[names[name]]-prefix[i+1]<r['limit']: return None
    return prefix[-1]

def check(slug,request,expected,got):
    try:
        if not isinstance(got,dict): return False
        if slug=='exact-fused-dot':
            flags=got['flags']
            return isinstance(got['bits'],str) and not got['bits'].lower().startswith('0x') and int(got['bits'],16)==int(expected['bits'],16) and isinstance(flags,list) and len(flags)==len(set(flags)) and set(flags)==set(expected['flags'])
        if slug=='mixed-width-tso':
            def key(o): return json.dumps({'reads':o['reads'],'memory':o['memory']},sort_keys=True,separators=(',',':'))
            os=got['outcomes']; keys=[key(o) for o in os]
            return isinstance(os,list) and len(keys)==len(set(keys)) and set(keys)=={key(o) for o in expected['outcomes']}
        if slug=='atomic-range-history':
            return got['order'] is None if expected['order'] is None else valid_history(request,got['order'])
        if slug=='alignment-relaxation':
            return type(got['size']) is int and got['size']==expected['size'] and layout_size(request,got['widths'])==expected['size']
        return (type(got['valid_bytes']) is int and type(got['last_seq']) is int and got['valid_bytes']==expected['valid_bytes'] and got['last_seq']==expected['last_seq'] and isinstance(got['pages'],list) and [bytes.fromhex(x) for x in got['pages']]==[bytes.fromhex(x) for x in expected['pages']])
    except (ValueError,TypeError,KeyError,AttributeError,StopIteration): return False

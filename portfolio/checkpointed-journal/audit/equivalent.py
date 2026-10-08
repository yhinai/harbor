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

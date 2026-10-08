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

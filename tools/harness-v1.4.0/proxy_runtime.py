"""Version 1.4.0 Linux terminal runtime; separate from frozen Day 1."""
import json,shlex
WRAPPER='''import ctypes,json,os,signal,subprocess,sys,tempfile,time
x=json.loads(sys.argv[1])
# Adopt descendants whose intermediate parent exits, including new sessions.
if ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)!=0:
 raise OSError(ctypes.get_errno(),'cannot become child subreaper')
def descendants():
 parents={}
 for name in os.listdir('/proc'):
  if not name.isdigit():continue
  try:
   with open('/proc/'+name+'/stat') as f:s=f.read()
   parents[int(name)]=int(s.rsplit(')',1)[1].split()[1])
  except (OSError,ValueError,IndexError):pass
 found=set();changed=True
 while changed:
  changed=False
  for pid,parent in parents.items():
   if pid not in found and (parent==os.getpid() or parent in found):
    found.add(pid);changed=True
 return found
def reap():
 while True:
  try:
   pid,_=os.waitpid(-1,os.WNOHANG)
   if pid==0:break
  except ChildProcessError:break
with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
 p=subprocess.Popen(['/bin/bash','-lc',x['command']],stdout=out,stderr=err,start_new_session=True)
 timed_out=False;output_limited=False;deadline=time.monotonic()+x['timeout_sec']
 while p.poll() is None:
  if max(os.fstat(out.fileno()).st_size,os.fstat(err.fileno()).st_size)>8*1024*1024:
   output_limited=True;break
  if time.monotonic()>=deadline:timed_out=True;break
  time.sleep(.01)
 # Terminal calls own their descendants: no background jobs persist after return.
 if descendants():
  until=time.monotonic()+2
  while True:
   children=descendants()
   for pid in children:
    try:os.kill(pid,signal.SIGKILL)
    except ProcessLookupError:pass
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   p.poll();reap()
   if not descendants() or time.monotonic()>=until:break
   time.sleep(.01)
  if descendants():raise RuntimeError('terminal descendants did not stop')
 def capture(f):
  size=os.fstat(f.fileno()).st_size;f.seek(0)
  if size<=262144:return f.read(262144).decode(errors='replace'),size,False
  first=f.read(131072);f.seek(-131072,2);last=f.read(131072)
  return (first+b'\\n[terminal output truncated]\\n'+last).decode(errors='replace'),size,True
 stdout,stdout_bytes,stdout_truncated=capture(out);stderr,stderr_bytes,stderr_truncated=capture(err)
 print(json.dumps({'stdout':stdout,'stderr':stderr,'return_code':124 if timed_out else 125 if output_limited else p.returncode,'timed_out':timed_out,'output_limited':output_limited,'stdout_bytes':stdout_bytes,'stderr_bytes':stderr_bytes,'stdout_truncated':stdout_truncated,'stderr_truncated':stderr_truncated}))
'''
def terminal_command(command,timeout):
 return 'python3 -I -c '+shlex.quote(WRAPPER)+' '+shlex.quote(json.dumps({'command':command,'timeout_sec':timeout}))

async def terminal(environment,command,timeout):
 if type(timeout) is not int or not 1<=timeout<=600:raise ValueError('Command timeout must be 1..600 seconds')
 result=await environment.exec(command=terminal_command(command,timeout),cwd='/app',timeout_sec=timeout+10)
 if result.return_code!=0:raise RuntimeError('Terminal wrapper failed: '+str(result.stderr))
 return json.loads(result.stdout)

class StreamAssembler:
    def __init__(self):
        self.message={'role':'assistant','content':''};self.calls={};self.usage=None;self.finish=None;self.metadata={};self.done=False
    def add(self,chunk):
        for k in ('id','model','created','object'):
            if k in chunk:self.metadata[k]=chunk[k]
        if chunk.get('usage'):self.usage=chunk['usage']
        for choice in chunk.get('choices',[]):
            if choice.get('index',0)!=0:raise ValueError('Unexpected multiple stream choices')
            if choice.get('finish_reason') is not None:self.finish=choice['finish_reason']
            delta=choice.get('delta',{})
            for k in ('content','reasoning_content'):
                if delta.get(k) is not None:self.message[k]=self.message.get(k,'')+delta[k]
            for x in delta.get('tool_calls') or []:
                index=x['index'];call=self.calls.setdefault(index,{'id':'','type':'function','function':{'name':'','arguments':''}})
                if x.get('id'):call['id']+=x['id']
                if x.get('type'):call['type']=x['type']
                for k in ('name','arguments'):
                    if (x.get('function') or {}).get(k) is not None:call['function'][k]+=x['function'][k]
    def result(self):
        if not self.done or self.finish is None or self.usage is None:raise ValueError('Incomplete stream or missing usage')
        if self.calls:self.message['tool_calls']=[self.calls[k] for k in sorted(self.calls)]
        return {**self.metadata,'choices':[{'index':0,'message':self.message,'finish_reason':self.finish}],'usage':self.usage}

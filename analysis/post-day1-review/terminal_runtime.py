"""Experimental Linux terminal timeout repair; not used for paid trials."""
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
 timed_out=False
 try:p.wait(timeout=x['timeout_sec'])
 except subprocess.TimeoutExpired:
  timed_out=True
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
 out.seek(0);err.seek(0)
 print(json.dumps({'stdout':out.read().decode(errors='replace'),'stderr':err.read().decode(errors='replace'),'return_code':124 if timed_out else p.returncode,'timed_out':timed_out}))
'''
def terminal_command(command,timeout):
 return 'python3 -I -c '+shlex.quote(WRAPPER)+' '+shlex.quote(json.dumps({'command':command,'timeout_sec':timeout}))

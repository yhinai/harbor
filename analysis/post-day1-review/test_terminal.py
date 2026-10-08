import importlib.util,json,subprocess,time,os,signal
from terminal_runtime import terminal_command
s=importlib.util.spec_from_file_location('old','/old_runtime.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
case="timeout 8 python3 -c 'import time; time.sleep(8)' old_nested_marker; echo done"
p=subprocess.Popen(old.terminal_command(case,1),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True);start=time.monotonic()
try:
 out,err=p.communicate(timeout=3);old_failed=False
except subprocess.TimeoutExpired:
 old_failed=True;os.killpg(p.pid,signal.SIGKILL);p.wait()
assert old_failed,repr({'stdout':out,'stderr':err,'returncode':p.returncode,'elapsed':time.monotonic()-start})
results=[{'implementation':'original','case':'nested GNU timeout','requested_timeout':1,'outer_wait_seconds':3,'fails_to_return_within_outer_wait':True}]
cases=[('printf ok',2,0),('exit 7',2,7),('sleep 8',1,124),("timeout 8 python3 -c 'import time; time.sleep(8)' new_nested_marker",1,124),("python3 -c 'import os,time; os.setsid(); time.sleep(8)' new_session_marker & wait",1,124)]
for cmd,limit,want in cases:
 start=time.monotonic();p=subprocess.run(terminal_command(cmd,limit),shell=True,capture_output=True,text=True,timeout=limit+4);elapsed=time.monotonic()-start
 assert p.returncode==0,(p.stdout,p.stderr);d=json.loads(p.stdout);assert d['return_code']==want,d
 if want==124:assert d['timed_out']
 results.append({'implementation':'experimental repair','command':cmd,'return_code':want,'elapsed_seconds':elapsed})
remaining=[]
for name in os.listdir('/proc'):
 if not name.isdigit():continue
 try:
  cmd=open('/proc/'+name+'/cmdline','rb').read()
  if b'new_nested_marker' in cmd or b'new_session_marker' in cmd:remaining.append(int(name))
 except OSError:pass
assert not remaining,remaining
print(json.dumps({'label':'verified synthetic Docker regression tests; no API calls','old_timeout_problem_reproduced':old_failed,'new_marked_descendants_remaining':remaining,'cases':results},indent=2))

"""Deterministic Harbor integration agent; never imports or calls a model client."""
import json,time
from harbor.agents.base import BaseAgent
from proxy_runtime import terminal
class OfflineAgent(BaseAgent):
 @staticmethod
 def name():return 'harness-offline-validation'
 def version(self):return '1.4.0'
 async def setup(self,environment):self.logs_dir.mkdir(parents=True,exist_ok=True)
 async def run(self,instruction,environment,context):
  context.cost_usd=0;context.n_input_tokens=0;context.n_output_tokens=0
  cases=[
   ('ordinary','printf ok',2,0),
   ('nonzero','exit 7',2,7),
   ('timeout','sleep 8',1,124),
   ('nested-timeout',"timeout 8 python3 -c 'import time; time.sleep(8)' harness_nested_marker; echo done",1,124),
   ('new-session',"python3 -c 'import os,time; os.setsid(); time.sleep(8)' harness_session_marker & wait",1,124),
   ('background-cleanup',"python3 -c 'import os,time; os.setsid(); time.sleep(8)' harness_background_marker & sleep 0.1",2,0),
   ('bounded-output',"python3 -c 'print(\"x\"*1000000)'",2,0),
   ('output-limit',"python3 -c 'import sys;\nwhile True: sys.stdout.write(\"x\"*1000000); sys.stdout.flush()'",2,125),
   ('recovery','printf recovered',2,0),
  ];results=[]
  for name,cmd,limit,want in cases:
   start=time.monotonic();r=await terminal(environment,cmd,limit);elapsed=time.monotonic()-start
   assert r['return_code']==want,(name,r)
   assert elapsed<limit+8,(name,elapsed)
   if want==124:assert r['timed_out']
   if name=='ordinary':assert r['stdout']=='ok'
   if name=='recovery':assert r['stdout']=='recovered'
   if name=='bounded-output':assert r['stdout_truncated'] and r['stdout_bytes']==1000001 and len(r['stdout'])<263000
   if want==125:assert r['output_limited']
   results.append({'name':name,'return_code':r['return_code'],'elapsed_seconds':elapsed,'stdout_bytes':r['stdout_bytes'],'stderr_bytes':r['stderr_bytes']})
  cmd="""python3 - <<'CHECK'
import os,socket,ssl,json
left=[]
for name in os.listdir('/proc'):
 if not name.isdigit():continue
 try:
  data=open('/proc/'+name+'/cmdline','rb').read()
  if b'harness_'+b'nested_marker' in data or b'harness_'+b'session_marker' in data or b'harness_'+b'background_marker' in data:left.append(name)
 except OSError:pass
assert not left,left
try:
 with socket.create_connection(('1.1.1.1',443),timeout=1) as s:
  with ssl.create_default_context().wrap_socket(s,server_hostname='one.one.one.one') as tls:
   tls.sendall(b'GET / HTTP/1.0\\r\\nHost: one.one.one.one\\r\\n\\r\\n')
   data=tls.recv(32)
except OSError as ex:print(json.dumps({'cleanup':'passed','external_tls':'denied','error_type':type(ex).__name__}))
else:raise AssertionError('External TLS application connection succeeded')
CHECK"""
  r=await terminal(environment,cmd,3);assert r['return_code']==0,r
  results.append({'name':'descendant-and-network-check','return_code':0,'observed':json.loads(r['stdout'])})
  r=await terminal(environment,"printf passed > /app/checks-passed",2);assert r['return_code']==0
  context.metadata={'label':'verified offline Harbor integration; no model calls','tool_calls':len(cases)+2,'cases':results}
  (self.logs_dir/'checks.json').write_text(json.dumps(context.metadata,indent=2)+'\n')

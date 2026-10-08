"""Stop a dedicated container during a nested terminal command; no model calls."""
import json,subprocess,time,uuid
from proxy_runtime import terminal_command
name='harness-v130-cancel-'+uuid.uuid4().hex[:10]
image='python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c'
proc=None
try:
 subprocess.run(['docker','run','-d','--name',name,'--network','none','--cpus','1','--memory','128m','--entrypoint','python3',image,'-c','import time;time.sleep(300)'],check=True,capture_output=True)
 proc=subprocess.Popen(['docker','exec',name,'/bin/sh','-c',terminal_command("timeout 120 python3 -c 'import time;time.sleep(120)'; echo done",60)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 time.sleep(.5);assert proc.poll() is None,'Command ended before cancellation'
 start=time.monotonic();subprocess.run(['docker','stop','--time','1',name],check=True,capture_output=True,timeout=10)
 out,err=proc.communicate(timeout=5)
 running=subprocess.check_output(['docker','inspect','--format','{{.State.Running}}',name],text=True).strip();assert running=='false'
 print(json.dumps({'label':'verified real Docker container cancellation; no model calls','container_running_after_stop':False,'exec_return_code':proc.returncode,'elapsed_seconds':time.monotonic()-start,'limitation':'Explicit Docker stop tested; Harbor external cancellation not separately exercised'},indent=2))
finally:
 subprocess.run(['docker','rm','-f',name],capture_output=True)
 if proc and proc.poll() is None:proc.kill();proc.communicate()

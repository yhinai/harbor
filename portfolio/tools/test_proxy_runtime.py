import asyncio,json,subprocess
from proxy_runtime import StreamAssembler,terminal_command
s=StreamAssembler()
s.add({'choices':[{'delta':{'role':'assistant','tool_calls':[{'index':0,'id':'t1','function':{'name':'terminal','arguments':'{"command":'}}]},'finish_reason':None}]})
s.add({'choices':[{'delta':{'tool_calls':[{'index':0,'function':{'arguments':'"echo ok"}'}}]},'finish_reason':'tool_calls'}]})
s.add({'choices':[],'usage':{'prompt_tokens':10,'completion_tokens':12}});s.done=True
r=s.result();assert json.loads(r['choices'][0]['message']['tool_calls'][0]['function']['arguments'])['command']=='echo ok'
for command,timeout,want in [('printf ok',2,0),('sleep 5',1,124),('exit 7',2,7)]:
 p=subprocess.run(terminal_command(command,timeout),shell=True,capture_output=True,text=True,timeout=10)
 assert p.returncode==0,(p.stdout,p.stderr)
 d=json.loads(p.stdout);assert d['return_code']==want,d
 if want==124:assert d['timed_out']
print('Stream reconstruction and terminal timeout/nonzero-exit tests passed; no API calls.')

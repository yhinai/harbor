"""Host-side stream assembly and bounded terminal execution, without API credentials."""
import json,shlex

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

# A process group is stopped inside the container, allowing the model to see
# the timeout as an ordinary tool result and revise its command or implementation.
WRAPPER='''import json,os,signal,subprocess,sys
x=json.loads(sys.argv[1]);p=subprocess.Popen(['/bin/bash','-lc',x['command']],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
timed_out=False
try:out,err=p.communicate(timeout=x['timeout_sec'])
except subprocess.TimeoutExpired:
 timed_out=True
 try:os.killpg(p.pid,signal.SIGKILL)
 except ProcessLookupError:pass
 out,err=p.communicate()
print(json.dumps({'stdout':out.decode('utf-8',errors='replace'),'stderr':err.decode('utf-8',errors='replace'),'return_code':124 if timed_out else p.returncode,'timed_out':timed_out}))
'''
def terminal_command(command,timeout):
    return 'python3 -I -c '+shlex.quote(WRAPPER)+' '+shlex.quote(json.dumps({'command':command,'timeout_sec':timeout}))

async def terminal(environment,command,timeout):
    result=await environment.exec(command=terminal_command(command,timeout),cwd='/app',timeout_sec=timeout+10)
    if result.return_code!=0:raise RuntimeError('Trusted terminal wrapper failed: '+str(result.stderr))
    return json.loads(result.stdout)

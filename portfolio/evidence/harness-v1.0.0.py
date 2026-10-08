"""Host-side Harbor proxy agent. No credentials are passed into task containers.
Only the literal proxy allowlist can incur inference charges. Frontier models
cannot be addressed through this client. Requests reserve conservative maximum
costs before dispatch; ambiguous failed requests keep their reservations.
"""
from pathlib import Path
import asyncio,datetime,fcntl,json,math,os,time,urllib.request,urllib.error,uuid
from harbor.agents.base import BaseAgent
ROOT=Path(__file__).resolve().parents[1]
ENDPOINT='https://api.fireworks.ai/inference/v1/chat/completions'
RATES={
 'accounts/fireworks/models/kimi-k3':(3.00,15.00),
 'accounts/fireworks/models/glm-5p3':(1.40,4.40),
 'accounts/fireworks/models/deepseek-v4p1-flash':(0.30,1.20),
 'accounts/fireworks/models/qwen3p8-max':(2.00,6.00),
}
CAP=185.30
OPERATIONAL_CAP=170.00
PRICING_DATE='2026-10-08'
class ProxyBudgetExceeded(Exception): pass
class ProxyTransportFailure(Exception): pass
class ProxyProtocolFailure(Exception): pass
class ProxyTurnLimit(Exception): pass

class Budget:
 def __init__(self,path=None): self.path=Path(path or os.environ.get('PORTFOLIO_BUDGET_LEDGER',ROOT/'evidence/proxy-budget.json'))
 def change(self,fn):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  with self.path.with_suffix('.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   data=json.loads(self.path.read_text()) if self.path.exists() else {'authorized_cap_usd':CAP,'operational_cap_usd':OPERATIONAL_CAP,'conservative_booked_usd':0.0,'requests':{}}
   if data['authorized_cap_usd']!=CAP or data['operational_cap_usd']!=OPERATIONAL_CAP: raise ProxyBudgetExceeded('Ledger cap mismatch')
   try:
    value=fn(data)
   except Exception:
    tmp=self.path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)+'\n'); tmp.replace(self.path)
    raise
   tmp=self.path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)+'\n'); tmp.replace(self.path)
   return value
 def reserve(self,model,payload,trial,trial_cap):
  if model not in RATES: raise ProxyBudgetExceeded('Model outside proxy allowlist')
  if datetime.datetime.now(datetime.timezone.utc).date().isoformat()!=PRICING_DATE: raise ProxyBudgetExceeded('Reverify pricing before running on a different UTC date')
  # Byte-based upper bound deliberately exceeds normal tokenizer/framing counts.
  input_bound=2*len(json.dumps(payload,ensure_ascii=False).encode())+8192
  output_bound=payload['max_tokens']; a,b=RATES[model]
  maximum=1.25*(input_bound*a+output_bound*b)/1e6
  rid=uuid.uuid4().hex
  def apply(d):
   if d.get('halted'): raise ProxyBudgetExceeded('Ledger halted; reconcile provider usage before continuing')
   trial_spend=sum(x['booked_usd'] for x in d['requests'].values() if x['trial']==trial)
   if d['conservative_booked_usd']+maximum>OPERATIONAL_CAP or trial_spend+maximum>trial_cap: raise ProxyBudgetExceeded('Would exceed reserved trial or portfolio allowance')
   d['conservative_booked_usd']+=maximum
   d['requests'][rid]={'trial':trial,'model':model,'booked_usd':maximum,'reserved_usd':maximum,'input_bound':input_bound,'output_bound':output_bound,'status':'reserved','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  self.change(apply); return rid
 def settle(self,rid,usage):
  def apply(d):
   row=d['requests'][rid]; a,b=RATES[row['model']]
   input_tokens=usage.get('prompt_tokens'); output_tokens=usage.get('completion_tokens')
   if type(input_tokens) is not int or type(output_tokens) is not int or min(input_tokens,output_tokens)<0:
    row['status']='usage_unknown'; raise ProxyTransportFailure('Missing token usage; reservation retained')
   if input_tokens>row['input_bound'] or output_tokens>row['output_bound']:
    d['halted']='provider_usage_exceeded_bound'; row['status']='usage_exceeded_bound'; raise ProxyTransportFailure('Provider usage exceeded conservative bound; stop and reconcile')
   # Treat all input as uncached, and add 25% rate margin. This is an upper
   # budget estimate, not a claim about the provider's final invoice.
   cost=(input_tokens*a+output_tokens*b)/1e6; booked=cost*1.25
   d['conservative_booked_usd']+=booked-row['booked_usd']
   row.update(status='reported_usage',booked_usd=booked,usage=usage,uncached_rate_estimate_usd=cost)
   return cost
  return self.change(apply)

TOOL={'type':'function','function':{'name':'terminal','description':'Run a shell command in the offline task container. Use to inspect, edit, execute and test files.','parameters':{'type':'object','properties':{'command':{'type':'string'},'timeout_sec':{'type':'integer','minimum':1,'maximum':60}},'required':['command'],'additionalProperties':False}}}
SYSTEM='''You are a research engineering agent working in an offline Linux container.
Complete the task by inspecting, implementing, and testing files using terminal.
You have Python 3.12 and its standard library. No internet is available in the
container. The reference solution and evaluator files are not available to you.
Use your own tests and the public smoke command. Do not try to access evaluator
or hidden files. When finished, respond briefly without further tool calls.
'''

def credential():
 key=os.environ.get('FIREWORKS_API_KEY')
 if key: return key
 path=os.environ.get('FIREWORKS_ENV_FILE')
 if not path: raise ProxyTransportFailure('Set FIREWORKS_API_KEY or FIREWORKS_ENV_FILE on the host')
 from dotenv import dotenv_values
 key=dotenv_values(path).get('FIREWORKS_API_KEY')
 if not key: raise ProxyTransportFailure('Credential source has no Fireworks key')
 return key

def complete(payload,trial,trial_cap):
 key=credential(); budget=Budget(); rid=budget.reserve(payload['model'],payload,trial,trial_cap)
 req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=240) as response: data=json.load(response)
 except urllib.error.HTTPError as ex:
  # Preserve reservation: even an error must not silently create retry credit.
  detail=ex.read(2048).decode(errors='replace').replace(key,'[redacted]')
  raise ProxyTransportFailure(f'Provider HTTP {ex.code}: {detail}') from None
 except Exception as ex: raise ProxyTransportFailure(type(ex).__name__+'; reservation retained') from None
 cost=budget.settle(rid,data.get('usage',{}))
 return data,cost,rid

class FireworksAgent(BaseAgent):
 @staticmethod
 def name(): return 'portfolio-fireworks'
 def version(self): return '1.0.0'
 def __init__(self,*args,trial_cap=4.0,reasoning_effort='max',max_turns=60,max_tokens=32768,**kwargs):
  super().__init__(*args,**kwargs)
  if self.model_name not in RATES: raise ValueError('Only literal proxy model IDs are allowed')
  self.trial_cap=float(trial_cap); self.effort=reasoning_effort; self.turns=int(max_turns); self.max_tokens=int(max_tokens)
  if not 1<=self.max_tokens<=65536 or not 1<=self.turns<=80: raise ValueError('Invalid hard limits')
 async def setup(self,environment):
  self.logs_dir.mkdir(parents=True,exist_ok=True)
 async def run(self,instruction,environment,context):
  messages=[{'role':'system','content':SYSTEM},{'role':'user','content':instruction}]
  context.n_input_tokens=0; context.n_output_tokens=0; context.cost_usd=0.0
  context.metadata={'harness':'portfolio-fireworks-1.0.0','tool_calls':0,'reasoning_effort':self.effort,'trial_cap_usd':self.trial_cap,'max_tokens':self.max_tokens,'max_turns':self.turns,'censor_status':None}
  path=self.logs_dir/'complete-trajectory.jsonl'; step=0
  def log(kind,**fields):
   nonlocal step
   with path.open('a') as f: f.write(json.dumps({'step_index':step,'kind':kind,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**fields})+'\n')
   step+=1
  log('initial',messages=messages,tools=[TOOL])
  trial=str(self.logs_dir.resolve())
  try:
   for turn in range(self.turns):
    payload={'model':self.model_name,'messages':messages,'tools':[TOOL],'tool_choice':'auto','temperature':0.6,'max_tokens':self.max_tokens,'reasoning_effort':self.effort,'stream':False}
    log('request',turn=turn,payload=payload)
    data,cost,rid=await asyncio.to_thread(complete,payload,trial,self.trial_cap)
    log('response',turn=turn,response=data,budget_request_id=rid)
    usage=data['usage']; context.n_input_tokens+=usage['prompt_tokens']; context.n_output_tokens+=usage['completion_tokens']; context.cost_usd+=cost
    choice=data['choices'][0]; raw=choice['message']
    message={k:v for k,v in raw.items() if k in ('role','content','tool_calls','reasoning_content')}; message.setdefault('role','assistant')
    calls=message.get('tool_calls') or []
    if not calls and not message.get('content'): raise ProxyProtocolFailure('Empty assistant response; no useful action')
    messages.append(message)
    if choice.get('finish_reason')=='length': raise ProxyProtocolFailure('Output limit reached; exclude this censored trial')
    if not calls:
     log('finished',tool_calls=context.metadata['tool_calls'])
     if context.metadata['tool_calls']==0: raise ProxyProtocolFailure('No terminal work; tool capability smoke failed')
     return
    for call in calls:
     try:
      fn=call['function']; args=json.loads(fn['arguments'])
      if fn['name']!='terminal' or not isinstance(args.get('command'),str): raise ValueError('Invalid tool call')
      timeout=args.get('timeout_sec',30)
      if type(timeout) is not int or not 1<=timeout<=60: raise ValueError('Invalid command timeout')
     except (KeyError,ValueError,TypeError) as ex: raise ProxyProtocolFailure(str(ex)) from None
     log('terminal_call',tool_call_id=call['id'],command=args['command'],timeout_sec=timeout)
     result=await environment.exec(command=args['command'],cwd='/app',timeout_sec=timeout)
     full=result.model_dump(); log('terminal_result',tool_call_id=call['id'],result=full)
     context.metadata['tool_calls']+=1
     visible={k:(v if not isinstance(v,str) or len(v)<=40000 else v[:20000]+'\n[output truncated; full output is in host trajectory]\n'+v[-20000:]) for k,v in full.items()}
     messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(visible)})
   raise ProxyTurnLimit('Artificial turn cap reached; exclude this censored trial')
  except Exception as ex:
   context.metadata['censor_status']=type(ex).__name__
   log('exception',exception_type=type(ex).__name__,message=str(ex)); raise

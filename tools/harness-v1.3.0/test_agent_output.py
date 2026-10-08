"""Regression for output exhaustion previously mislabeled as empty protocol reply."""
import asyncio,json,tempfile
from pathlib import Path
from types import SimpleNamespace
import fireworks_agent_v130 as agent_module
async def main():
 old=agent_module.complete
 async def fake_complete(*args,**kwargs):
  return {'usage':{'prompt_tokens':2,'completion_tokens':65536},'choices':[{'message':{'role':'assistant','content':''},'finish_reason':'length'}]},0,'synthetic'
 agent_module.complete=fake_complete
 try:
  with tempfile.TemporaryDirectory() as d:
   a=agent_module.FireworksAgent(logs_dir=Path(d),model_name='accounts/fireworks/models/kimi-k3');context=SimpleNamespace()
   try:await a.run('synthetic offline response test',None,context)
   except agent_module.ProxyOutputLimit:assert context.metadata['censor_status']=='ProxyOutputLimit'
   else:raise AssertionError('Output exhaustion misclassified')
 finally:agent_module.complete=old
 print(json.dumps({'label':'verified synthetic adapter regression; no model calls','empty_length_response_classified_as':'ProxyOutputLimit'},indent=2))
asyncio.run(main())

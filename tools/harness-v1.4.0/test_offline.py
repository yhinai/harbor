"""Updated limits and transport tests without provider requests."""
import asyncio,json,tempfile
from pathlib import Path
import fireworks_agent_v140 as m
from proxy_runtime import StreamAssembler
with tempfile.TemporaryDirectory() as td:
 b=m.Budget(Path(td)/'ledger.json');q={'model':'accounts/fireworks/models/kimi-k3','messages':[],'max_tokens':1048576}
 for bad in ['Fable','GPT-5.6 Sol','accounts/fireworks/models/gpt-5p6']:
  try:b.reserve(bad,q,'offline',None)
  except m.ProxyBudgetExceeded:pass
  else:raise AssertionError('Non-proxy model admitted')
 rid=b.reserve(q['model'],q,'offline',None);assert b.settle(rid,{'prompt_tokens':2,'completion_tokens':5})>=0
 a=m.FireworksAgent(logs_dir=Path(td),model_name=q['model']);assert a.max_tokens==1048576 and a.trial_cap is None and a.turns==1000
async def check():
 try:await m.complete({},'offline',None)
 except m.ProxyBudgetExceeded:pass
 else:raise AssertionError('Paid gate unexpectedly open')
asyncio.run(check())
print('Offline allowlist, no-dollar-ceiling ledger, extended limits and disabled-default paid gate passed.')

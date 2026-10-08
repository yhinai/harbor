from pathlib import Path
import json,tempfile
from fireworks_agent import Budget,ProxyBudgetExceeded
with tempfile.TemporaryDirectory() as td:
 b=Budget(Path(td)/'budget.json')
 req={'model':'accounts/fireworks/models/kimi-k3','messages':[{'role':'user','content':'test'}],'max_tokens':128}
 try: b.reserve('Fable',req,'t',1)
 except ProxyBudgetExceeded: pass
 else: raise AssertionError('Forbidden target accepted')
 try: b.reserve(req['model'],req,'t',0.00001)
 except ProxyBudgetExceeded: pass
 else: raise AssertionError('Trial cap bypassed')
 rid=b.reserve(req['model'],req,'t',1)
 before=json.loads(b.path.read_text())['conservative_booked_usd']
 b.settle(rid,{'prompt_tokens':5,'completion_tokens':9})
 after=json.loads(b.path.read_text())['conservative_booked_usd']
 assert 0<=after<before
 state=json.loads(b.path.read_text()); state['conservative_booked_usd']=250
 b.path.write_text(json.dumps(state))
 rid=b.reserve(req['model'],req,'other',100)
 assert rid and json.loads(b.path.read_text())['conservative_booked_usd']>250
 try: b.reserve(req['model'],req,'blocked',0.00001)
 except ProxyBudgetExceeded: pass
 else: raise AssertionError('Per-trial cap not enforced without aggregate cap')
 print('Budget controls passed: forbidden models, per-trial limit, settlement, no aggregate ceiling; no API calls.')

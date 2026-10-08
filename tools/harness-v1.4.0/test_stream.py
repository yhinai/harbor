import asyncio,json
import httpx
from stream_transport import ProxyHTTPFailure,stream_response,ProxyRequestDeadline,ProxyStreamInactivity,ProxyTransportFailure,ProxyProtocolFailure
class Events(httpx.AsyncByteStream):
 def __init__(self,events):self.events=events;self.closed=False
 async def __aiter__(self):
  for delay,data in self.events:await asyncio.sleep(delay);yield data
 async def aclose(self):self.closed=True

def line(x):return ('data: '+json.dumps(x)+'\n\n').encode()
chunk=line({'choices':[{'index':0,'delta':{'content':'ok'},'finish_reason':'stop'}]})
usage=line({'choices':[],'usage':{'prompt_tokens':2,'completion_tokens':1}})
async def check(name,events,want=None,deadline=1,idle=1,status=200):
 stream=Events(events);logs=[]
 async def handler(request):return httpx.Response(status,stream=stream)
 async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
  try:r=await stream_response(client,'https://offline.invalid',{}, {},request_deadline=deadline,inactivity_timeout=idle,log=lambda k,**v:logs.append({'kind':k,**v}))
  except Exception as ex:
   assert want is not None and type(ex) is want,(name,type(ex),str(ex))
  else:assert want is None and r['usage']['completion_tokens']==1,name
 assert stream.closed,name
 if want is ProxyRequestDeadline:assert logs[-1]['category']=='absolute_request_deadline' and logs[-1]['stream_chunks']>0
 if want is ProxyStreamInactivity:assert logs[-1]['category']=='inactivity'
 return {'name':name,'result':want.__name__ if want else 'complete','stream_closed':stream.closed,'failure_diagnostics':[x for x in logs if x['kind']=='stream_failure']}
async def main():
 r=[]
 r.append(await check('complete',[(0,chunk),(0,usage),(0,b'data: [DONE]\n\n')]))
 r.append(await check('no-absolute-deadline',[(.02,chunk),(0,usage),(0,b'data: [DONE]\n\n')],deadline=None))
 r.append(await check('active-stream-deadline',[(.01,chunk)]*30,ProxyRequestDeadline,deadline=.08,idle=.05))
 r.append(await check('inactive-stream',[(0,chunk),(.15,usage)],ProxyStreamInactivity,deadline=1,idle=.03))
 r.append(await check('missing-done',[(0,chunk),(0,usage)],ProxyProtocolFailure))
 r.append(await check('invalid-json',[(0,b'data: invalid\n\n')],ProxyProtocolFailure))
 r.append(await check('invalid-json-shape',[(0,b'data: []\n\n')],ProxyProtocolFailure))
 r.append(await check('http-error',[],ProxyHTTPFailure,status=503))
 # Explicit cancellation must propagate and close the stream.
 stream=Events([(0,chunk),(5,usage)])
 async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,stream=stream))) as client:
  task=asyncio.create_task(stream_response(client,'https://offline.invalid',{},{}));await asyncio.sleep(.02);task.cancel()
  try:await task
  except asyncio.CancelledError:pass
  else:raise AssertionError('Cancellation swallowed')
 assert stream.closed;r.append({'name':'external-cancellation','result':'CancelledError','stream_closed':True})
 # Paid execution is disabled before credential lookup or a budget mutation.
 from fireworks_agent_v140 import complete,ProxyBudgetExceeded
 try:await complete({},'offline',100)
 except ProxyBudgetExceeded as ex:assert 'disabled' in str(ex)
 else:raise AssertionError('Paid gate did not reject')
 r.append({'name':'paid-disabled','result':'rejected-before-request'})
 print(json.dumps({'label':'verified mock transport; no network or paid calls','cases':r},indent=2))
asyncio.run(main())

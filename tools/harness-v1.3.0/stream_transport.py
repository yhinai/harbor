"""Explicit request, inactivity, and protocol failures. No retries or credentials."""
import asyncio,json,time
import httpx
from proxy_runtime import StreamAssembler
class ProxyRequestDeadline(Exception):pass
class ProxyStreamInactivity(Exception):pass
class ProxyTransportFailure(Exception):pass
class ProxyProtocolFailure(Exception):pass

async def stream_response(client,endpoint,payload,headers,*,request_deadline=1200,inactivity_timeout=600,log=None):
 if request_deadline<=0 or inactivity_timeout<=0:raise ValueError('Positive deadlines required')
 start=time.monotonic();last_event=None;chunks=0;usage=None
 def diagnostics():return {'elapsed_seconds':time.monotonic()-start,'stream_chunks':chunks,'last_chunk_age_seconds':None if last_event is None else time.monotonic()-last_event,'partial_usage':usage}
 async def consume():
  nonlocal chunks,last_event,usage
  assembler=StreamAssembler()
  async with client.stream('POST',endpoint,json=payload,headers=headers) as response:
   if response.status_code>=400:raise ProxyTransportFailure('Provider HTTP '+str(response.status_code))
   lines=response.aiter_lines().__aiter__()
   while True:
    try:line=await asyncio.wait_for(lines.__anext__(),timeout=inactivity_timeout)
    except StopAsyncIteration:break
    except TimeoutError:raise ProxyStreamInactivity('No SSE line before inactivity allowance') from None
    if not line.startswith('data:'):continue
    value=line[5:].strip()
    if value=='[DONE]':assembler.done=True;break
    try:chunk=json.loads(value)
    except ValueError:raise ProxyProtocolFailure('Invalid SSE JSON') from None
    if not isinstance(chunk,dict):raise ProxyProtocolFailure('SSE JSON must be an object')
    last_event=time.monotonic();chunks+=1
    if chunk.get('usage'):usage=chunk['usage']
    if log:log('stream_chunk',chunk=chunk)
    try:assembler.add(chunk)
    except (ValueError,KeyError,TypeError,AttributeError) as ex:raise ProxyProtocolFailure('Invalid SSE chunk: '+str(ex)) from None
  try:return assembler.result()
  except (ValueError,KeyError,TypeError) as ex:raise ProxyProtocolFailure('Incomplete or invalid SSE response: '+str(ex)) from None
 try:
  async with asyncio.timeout(request_deadline):return await consume()
 except ProxyStreamInactivity:
  if log:log('stream_failure',category='inactivity',**diagnostics())
  raise
 except TimeoutError:
  d=diagnostics()
  if log:log('stream_failure',category='absolute_request_deadline',**d)
  raise ProxyRequestDeadline(json.dumps(d)) from None
 except httpx.TimeoutException as ex:
  if log:log('stream_failure',category='http_timeout',**diagnostics())
  raise ProxyTransportFailure(type(ex).__name__) from None
 except httpx.TransportError as ex:
  if log:log('stream_failure',category='http_transport',**diagnostics())
  raise ProxyTransportFailure(type(ex).__name__) from None

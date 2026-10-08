"""Read-only retrieval of public research artifacts; no inference endpoints."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent

def fetch(items):
 def one(item):
  name,url=item; path=ROOT/'sources'/name; path.parent.mkdir(parents=True,exist_ok=True)
  data=urlopen(Request(url,headers={'User-Agent':'portfolio-research'}),timeout=45).read(); path.write_bytes(data)
  return {'file':str(path.relative_to(ROOT)),'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 results=[]; errors=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  pending={ex.submit(one,item):item for item in items.items()}
  for future in concurrent.futures.as_completed(pending):
   name,url=pending[future]
   try: results.append(future.result())
   except Exception as exc:
    errors.append({'file':'sources/'+name,'url':url,'error':str(exc),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 manifest=ROOT/'sources/retrieval.json'; old=json.loads(manifest.read_text()) if manifest.exists() else []
 by={row['file']:row for row in old+results}; manifest.write_text(json.dumps(list(by.values()),indent=2)+'\n')
 for r in results: print(r['file'],r['bytes'])
 if errors:
  error_path=ROOT/'sources/retrieval-errors.json'
  old_errors=json.loads(error_path.read_text()) if error_path.exists() else []
  error_path.write_text(json.dumps(old_errors+errors,indent=2)+'\n')
  for r in errors: print('NOT CACHED:',r['file'],r['error'])

if __name__=='__main__':
 tb=json.loads((ROOT/'sources/tb2-tree.json').read_text()); tbs=tb['sha']
 sw=json.loads((ROOT/'sources/swepro-tree.json').read_text()); sws=sw['sha']
 hard=(ROOT/'sources/v2-hard51_ids.txt').read_text().splitlines()
 ids=[next(x for x in hard if hint in x) for hint in ['ansible-40ade','teleport-7744','navidrome-bf2b']]
 tasks=['cancel-async-tasks','torch-pipeline-parallelism','train-fasttext','caffe-cifar-10','break-filter-js-from-html','bn-fit-modify','build-cython-ext','build-pmars','fix-ocaml-gc','db-wal-recovery']
 items={}
 for e in tb['tree']:
  p=e['path']
  if e['type']=='blob' and p.split('/')[0] in tasks and (p.endswith('instruction.md') or p.endswith('task.toml') or p.endswith('Dockerfile') or p.endswith('solve.sh') or '/tests/' in p or p.endswith('solution.sh')):
   items['tb2/'+p]='https://raw.githubusercontent.com/laude-institute/terminal-bench-2/'+tbs+'/'+p
 for e in sw['tree']:
  p=e['path']
  if e['type']=='blob' and any('v2/tasks/'+i+'/' in p for i in ids): items['swepro/'+p]='https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/'+sws+'/'+p
 items['swepro/v2/GATE.md']='https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/'+sws+'/v2/GATE.md'
 (ROOT/'sources/pinned-revisions.json').write_text(json.dumps({'terminal_bench_2':tbs,'swe_bench_pro':sws,'swe_hard51_tasks_read':ids},indent=2)+'\n')
 fetch(items)

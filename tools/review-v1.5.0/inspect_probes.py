"""Extract exact root-path probes and one protocol interruption; no inference."""
from pathlib import Path
import json,gzip,re,shutil
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'analysis/review-v1.5.0'; STUDY=ROOT/'analysis/followup-v1.4.0/studies/mini-panel-20261008-v140'
inv=json.loads((OUT/'inventory.json').read_text());records=[]
for name in ['panel-glm-exact-fused-dot-7-a3-8a1951c5','panel-glm-atomic-range-history-1-a1-ff45a1d7','panel-glm-atomic-range-history-3-a1-a8e66952']:
 r=json.loads((ROOT/inv['per_trial_record'][name]).read_text()); traces=sorted(STUDY/f for f in r['saved_artifact_sha256'] if '.jsonl.gz' in f)
 if len(traces)!=1:raise RuntimeError('Need explicit multipart handling')
 calls={};events=[];tail=[]
 with gzip.open(traces[0],'rt') as f:
  for line in f:
   if '"kind": "stream_chunk"' in line:continue
   x=json.loads(line);tail=(tail+[x])[-4:]
   if x['kind']=='terminal_call' and re.search(r'(?<![\w/])/(?:tests|solution|logs/verifier)(?:/|\b)',x['command']):calls[x['tool_call_id']]=x;events.append(x)
   if x['kind']=='terminal_result' and x['tool_call_id'] in calls:events.append(x)
 records.append({'attempt_id':name,'root_probe_events':events,'last_non_stream_events':tail if '3-a1-a8e66952' in name else []})
(OUT/'root-probe-review.json').write_text(json.dumps({'label':'verified exact transcript events; root-path command screening is not evidence of access','records':records},indent=2)+'\n')

"""Readable evidence windows, never a causal classifier or inference client."""
from pathlib import Path
import argparse,json
from selection import ROOT
ap=argparse.ArgumentParser();ap.add_argument('filter',nargs='?',default='');ap.add_argument('--limit',type=int,default=1600);ap.add_argument('--unreviewed',action='store_true');args=ap.parse_args()
rows=json.loads((ROOT/'evidence/proxy/panel-v120-outcomes.json').read_text())
reviewed=json.loads((ROOT/'analysis/trajectory-review.json').read_text())['trials']
for r in rows:
    if args.unreviewed and r['trial_id'] in reviewed:continue
    if args.filter and args.filter not in (r['task']+' '+r['model']+' '+str(r['replicate'])+' '+r['trial_id']):continue
    print('\nTRIAL',r['task'],r['model'].split('/')[-1],r['replicate'],r['trial_id'],r['status'],r['reward'])
    for line in Path(r['trajectory_path']).read_text().splitlines():
        e=json.loads(line);k=e['kind'];step=e['step_index']
        if k=='terminal_call':print('CALL',step,e['command'][:args.limit])
        elif k=='terminal_result':
            d=e['result'];s=d.get('stdout','')+'\n'+d.get('stderr','');print('RESULT',step,'exit',d.get('return_code'),'timeout',d.get('timed_out'),s[-args.limit:])
        elif k=='response':
            d=e['response']['choices'][0];m=d['message']
            if not m.get('tool_calls') or d.get('finish_reason')=='length':print('ASSISTANT',step,d.get('finish_reason'),'content',str(m.get('content'))[-args.limit:],'reasoning_tail',str(m.get('reasoning_content'))[-args.limit:])
        elif k in ('finished','exception'):print('END',step,e)

"""Extract actual panel events for human-authored mechanism notes; no inference calls."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=json.loads((ROOT/'evidence/proxy/panel-v120-outcomes.json').read_text())
    out=ROOT/'analysis/trajectory-excerpts';out.mkdir(exist_ok=True);index=[]
    for row in rows:
        p=Path(row['trajectory_path'])
        if not p.exists():raise ValueError('Missing trajectory '+str(p))
        events=[json.loads(x) for x in p.read_text().splitlines()]
        selected=[]
        for e in events:
            if e['kind'] in ('terminal_call','terminal_result','finished','exception'):
                selected.append(e)
            elif e['kind']=='response':
                d=e['response'];message=d['choices'][0]['message']
                selected.append({'step_index':e['step_index'],'kind':'assistant_response','finish_reason':d['choices'][0]['finish_reason'],'content':message.get('content'),'reasoning_content':message.get('reasoning_content')})
        dest=out/(row['trial_id']+'.json');dest.write_text(json.dumps({'trial':row,'events':selected},indent=2)+'\n')
        index.append({'trial':row['trial_id'],'task':row['task'],'model':row['model'],'status':row['status'],'reward':row['reward'],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'excerpt_path':str(dest.relative_to(ROOT)),'event_count':len(events),'terminal_calls':sum(x['kind']=='terminal_call' for x in events)})
    (out/'index.json').write_text(json.dumps(index,indent=2)+'\n');print('Extracted',len(index),'actual trajectories')
if __name__=='__main__':main()

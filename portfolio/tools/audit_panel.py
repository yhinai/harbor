"""Validate completed panel records and their connection to the frozen packages."""
from pathlib import Path
import collections,hashlib,json
from run_panel import MODELS,hashes
from selection import ROOT,SLUGS
rows=json.loads((ROOT/'evidence/proxy/panel-v120-outcomes.json').read_text())
expected={(s,m['id'],i) for s in SLUGS for m in MODELS.values() for i in range(1,m['trials']+1)}
assert len(rows)==55 and {(r['task'],r['model'],r['replicate']) for r in rows}==expected
assert len({r['trial_id'] for r in rows})==55
old=json.loads((ROOT/'evidence/day1-amendment-v1.1.0.json').read_text());assert hashes()==old['task_sha256']
configs=[];summaries=[]
for r in rows:
    p=Path(r['trajectory_path']);ev=[json.loads(x) for x in p.read_text().splitlines()]
    initial=[e for e in ev if e['kind']=='initial'];assert len(initial)==1
    assert initial[0]['messages'][1]['content']==(ROOT/r['task']/'instruction.md').read_text()
    calls=[e for e in ev if e['kind']=='terminal_call'];results=[e for e in ev if e['kind']=='terminal_result']
    assert len(calls)>=1 or r['status']!='valid'
    assert len({e['tool_call_id'] for e in calls})==len(calls)
    assert {e['tool_call_id'] for e in results}<={e['tool_call_id'] for e in calls}
    result=json.loads(Path(r['harbor_result_path']).read_text());cfg=result['config'];configs.append(cfg)
    assert cfg['environment']['type']=='docker' and cfg['environment']['delete'] is True
    assert cfg.get('source_trial') is None and cfg['trial_name']==r['trial_id']
    assert result['agent_info']['version']=='1.2.0'
    for e in ev:
        if e['kind']=='request':
            q=e['payload'];assert q['model']==r['model'];assert q['max_tokens']==65536 and q['temperature']==1.
        elif e['kind']=='response':
            assert e['response']['model']==r['model'],'Provider returned a different model identifier'
    if r['status']=='valid':
        assert r['reward'] in (0,1) and not result.get('exception_info')
        assert any(e['kind']=='finished' for e in ev)
        assert len(results)==len(calls) and r['tool_calls']==len(results)
    summaries.append({'trial':r['trial_id'],'task':r['task'],'model':r['model'],'status':r['status'],'reward':r['reward'],'complete_tool_results':len(results),'trajectory_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len({c['job_id'] for c in configs})==55,'Each attempt must have a separate Harbor job'
ledger=json.loads((ROOT/'evidence/proxy-budget.json').read_text())
allow={m['id'] for m in MODELS.values()};assert {x['model'] for x in ledger['requests'].values()}<=allow
assert not any(x['status']=='reserved' for x in ledger['requests'].values())
record={'label':'verified','scheduled_attempts':55,'unique_trials':55,'packages_match_phase3_freeze':True,'exact_task_prompts_verified':True,'request_allowlist_verified':True,'provider_usage_or_retained_reservations':True,'aggregate_budget_ceiling':ledger.get('operational_cap_usd'),'aggregate_budget_ceiling_removed_by_user':True,'valid':sum(r['status']=='valid' for r in rows),'excluded':dict(collections.Counter(r['status'] for r in rows if r['status']!='valid')),'trials':summaries,'fresh_container_evidence':'Each scheduled attempt is a separate harbor run -n 1 with unique job and trial identity; default Docker environment teardown/build recorded in each job.'}
(ROOT/'evidence/proxy/panel-audit.json').write_text(json.dumps(record,indent=2)+'\n')
print('PANEL AUDIT PASSED',record['valid'],'valid trials; exclusions',record['excluded'])

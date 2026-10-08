"""Freeze the validated portfolio in a new amendment; never overwrites history."""
from pathlib import Path
import datetime,hashlib,json,math,tomllib
from selection import ROOT,SLUGS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes():
    return {str(p.relative_to(ROOT)):sha(p) for s in SLUGS for p in sorted((ROOT/s).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
def distribution(a,b):
    lb=lambda x,y:math.lgamma(x)+math.lgamma(y)-math.lgamma(x+y)
    return [math.exp(math.log(math.comb(8,k))+lb(a+k,b+8-k)-lb(a,b)) for k in range(9)]
def main():
    path=ROOT/'evidence/day1-amendment-v1.1.0.json'
    if path.exists():raise SystemExit('Refusing to overwrite a frozen amendment')
    validation=json.loads((ROOT/'evidence/final-validation-v1.1.0.json').read_text())
    oracle=json.loads((ROOT/'evidence/harbor-oracles-v1.1.0.json').read_text())
    current=hashes();assert validation['task_sha256']==oracle['task_sha256']==current
    baseline=json.loads((ROOT/'evidence/typecheck-baseline-hardened-v1.json').read_text())
    assert baseline['complete'] and baseline['elapsed_seconds']>=900 and not baseline['found'] and not baseline['unexpected']
    ledger=json.loads((ROOT/'evidence/proxy-budget.json').read_text());assert ledger.get('halted'),'Paid hold unexpectedly cleared'
    forecasts=[('typecheck-soundness-witness',3,3),('exact-fused-dot',4,3),('mixed-width-tso',5,2),('checkpointed-journal',5,2),('atomic-range-history',6,2)]
    tasks=[]
    for rank,(slug,a,b) in enumerate(forecasts,1):
        task_config=tomllib.loads((ROOT/slug/'task.toml').read_text());dist=distribution(a,b)
        tasks.append({'rank':rank,'task':slug,'package_version':task_config['task']['version'],'canonical_artifact':'solution/witness.json' if slug=='typecheck-soundness-witness' else 'solution/canonical.py','forecast_classification':'inferred_subjective_provisional_before_paid_panel','alpha':a,'beta':b,'predicted_K':round(8*a/(a+b)),'expected_K':8*a/(a+b),'P_K':dist,'P_hard_conditional_on_validity':sum(dist[:3])})
    evidence=['evidence/final-validation-console-v1.1.0.txt','evidence/final-validation-v1.1.0.json','evidence/harbor-oracles-v1.1.0.json','evidence/typecheck-validation.json','evidence/typecheck-interpreter-crosscheck.json','evidence/typecheck-baseline-initial.json','evidence/typecheck-baseline-hardened-v1.json','evidence/local-validation.json','evidence/docker-validation.json','evidence/input-audit.json','evidence/isolation-audit.json','evidence/instruction-audit-v1.1.0.json']
    evidence += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'evidence/baseline-snapshots').rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    evidence += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'evidence').glob('typecheck-baseline-*-found-*.json'))]
    documents=['selected-tasks.json','day1.md','PROMPTS.md','README.md','RESEARCH.md']
    tools=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'tools').glob('*.py'))]
    historical=['evidence/day1-preregistration.json','evidence/day1-amendment-v1.0.2.json']
    record={'version':'1.1.0','stage':'Phase 3 complete; package freeze; provisional forecasts; Phase 4 not started','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'claim_labels':{'validation':'verified','forecasts':'inferred','frontier_performance':'unknown'},'changes':['Replace alignment-relaxation with typecheck-soundness-witness','Retain atomic-range-history at user request','Remove SQLite candidate and its draft spec from the active plan','Remove failure-mechanism hints from agent instructions','Discard the initial checker design after a fast random-generation counterexample; use the validated loop-join memoization design'],'tasks':tasks,'task_sha256':current,'evidence_sha256':{p:sha(ROOT/p) for p in sorted(set(evidence))},'document_sha256':{p:sha(ROOT/p) for p in documents},'tool_sha256':{p:sha(ROOT/p) for p in tools},'historical_record_sha256':{p:sha(ROOT/p) for p in historical},'retired':['alignment-relaxation'],'paid_calls_in_phase3':0,'frontier_trials_run':0,'paid_panel_status':'user_hold_pending_go','valid_proxy_trials_observed':0,'baseline_summary':{'initial_counterexample_found':True,'final_requested_seconds':baseline['requested_seconds'],'final_elapsed_seconds':baseline['elapsed_seconds'],'final_counts':baseline['counts'],'final_counterexample_found':False},'limitations':['No frontier-difficulty measurement','Same-author specification, implementations and critique','Random-generation baseline is not exhaustive','Older published anchor results are not pass-rate estimates for these tasks','Phase 4 paid panel and final Day 1 evidence update are pending human go']}
    path.write_text(json.dumps(record,indent=2)+'\n');digest=sha(path)
    path.with_suffix('.sha256').write_text(digest+'  '+path.name+'\n')
    (ROOT/'evidence/current-freeze.json').write_text(json.dumps({'amendment':path.name,'sha256':digest,'version':'1.1.0'},indent=2)+'\n')
    print('FROZEN',path,'sha256',digest,'package_files',len(current),flush=True)
if __name__=='__main__':main()

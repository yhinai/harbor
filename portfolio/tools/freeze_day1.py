"""Freeze completed Day 1 evidence and create an archive matching every package hash."""
from pathlib import Path
import datetime,hashlib,json,shutil,tomllib,zipfile
from selection import ROOT,SLUGS
from run_panel import hashes
from fireworks_agent import Budget

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'evidence/day1-amendment-v1.2.0.json'
    if manifest.exists():raise SystemExit('Refusing to overwrite final Day 1 freeze')
    prior=ROOT/'evidence/day1-amendment-v1.1.0.json';old=json.loads(prior.read_text());assert hashes()==old['task_sha256']
    rows=json.loads((ROOT/'evidence/proxy/panel-v120-outcomes.json').read_text());assert len(rows)==55
    expected={(s,m,i) for s in SLUGS for m,n in [('accounts/fireworks/models/kimi-k3',5),('accounts/fireworks/models/glm-5p3',3),('accounts/fireworks/models/deepseek-v4p1-flash',3)] for i in range(1,n+1)}
    assert {(r['task'],r['model'],r['replicate']) for r in rows}==expected
    forecasts=json.loads((ROOT/'analysis/day1-forecasts.json').read_text());assert set(forecasts['tasks'])==set(SLUGS)
    assert not (ROOT/'report.md').exists(),'report.md must wait for official overnight results'
    review=json.loads((ROOT/'analysis/trajectory-review.json').read_text());assert set(review['trials'])=={r['trial_id'] for r in rows},'Every attempt needs a reviewed note'
    ledger=json.loads((ROOT/'evidence/proxy-budget.json').read_text());assert not any(x['status']=='reserved' for x in ledger['requests'].values()),'An API request is still unsettled/in progress'
    assert not ledger.get('halted'),'Resolve any existing budget halt before finalization'
    def halt(d):d['halted']='day1_complete_no_further_paid_work_authorized'
    Budget().change(halt)
    for name in ['day1.md','analysis/trajectory-notes.md','analysis/update-rules.md','analysis/panel-analysis.json']:assert (ROOT/name).is_file(),name
    trajectories=ROOT/'evidence/proxy/trajectories';trajectories.mkdir(exist_ok=True);portable=[]
    for row in rows:
        p=Path(row['trajectory_path']);assert p.is_file(),p
        dest=trajectories/(row['trial_id']+'.jsonl');shutil.copyfile(p,dest)
        result=Path(row['harbor_result_path']);assert result.is_file(),result
        result_dest=trajectories/(row['trial_id']+'-harbor-result.json');shutil.copyfile(result,result_dest)
        r={**row,'trajectory_path':str(dest.relative_to(ROOT)),'host_trajectory_path':row['trajectory_path'],'trajectory_sha256':sha(dest),'harbor_result_path':str(result_dest.relative_to(ROOT)),'host_harbor_result_path':row['harbor_result_path'],'harbor_result_sha256':sha(result_dest)};portable.append(r)
    (ROOT/'evidence/proxy/panel-outcomes.json').write_text(json.dumps(portable,indent=2)+'\n')
    for row in json.loads((ROOT/'evidence/proxy/smoke-v120-outcomes.json').read_text()):
        p=Path(row['trajectory_path']);assert p.is_file(),p
        shutil.copyfile(p,trajectories/('smoke-'+row['trial_id']+'.jsonl'))
    files={}
    for slug in SLUGS:
        for p in (ROOT/slug).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:files[str(p.relative_to(ROOT))]=p
    for name in ['day1.md','PROMPTS.md','README.md','RESEARCH.md','selected-tasks.json']:
        files[name]=ROOT/name
    for base in [ROOT/'analysis',ROOT/'tools',ROOT/'evidence']:
        for p in base.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.lock','.tmp') and p.name!='current-freeze.json' and p.name!='proxy-budget.json':files[str(p.relative_to(ROOT))]=p
    # Billing ledger is audit evidence; record a fixed snapshot rather than a live lock file.
    ledger=json.loads((ROOT/'evidence/proxy-budget.json').read_text())
    snapshot=ROOT/'evidence/proxy-budget-day1-final.json';snapshot.write_text(json.dumps(ledger,indent=2)+'\n');files[str(snapshot.relative_to(ROOT))]=snapshot
    record={'version':'1.2.0','stage':'Final Day 1 preregistration, after development panel and before evaluator overnight results','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_amendment':{'file':prior.name,'sha256':sha(prior)},'task_sha256':hashes(),'artifact_sha256':{r:sha(p) for r,p in sorted(files.items())},'tasks':[{**forecasts['tasks'][s],'task':s,'canonical_artifact':'solution/witness.json' if s=='typecheck-soundness-witness' else 'solution/canonical.py','package_version':tomllib.loads((ROOT/s/'task.toml').read_text())['task']['version']} for s in forecasts['ranking']],'panel_attempts':55,'valid_panel_trials':sum(r['status']=='valid' for r in rows),'smokes_included_in_pass_rates':False,'known_usage_uncached_cost_estimate_usd':sum(x.get('uncached_rate_estimate_usd',0) for x in ledger['requests'].values()),'conservative_booked_usd':ledger['conservative_booked_usd'],'actual_invoice_total':'unknown','target_models_run':False,'official_overnight_results':'not_observed','report_md_written':False}
    manifest.write_text(json.dumps(record,indent=2)+'\n');digest=sha(manifest);manifest.with_suffix('.sha256').write_text(digest+'  '+manifest.name+'\n')
    pointer=ROOT/'evidence/current-freeze.json';pointer.write_text(json.dumps({'version':'1.2.0','amendment':manifest.name,'sha256':digest},indent=2)+'\n')
    for p in [manifest,manifest.with_suffix('.sha256'),pointer]:files[str(p.relative_to(ROOT))]=p
    out=ROOT.parent/'day1-submission.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel,p in sorted(files.items()):z.write(p,rel)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert {x.split('/')[0] for x in z.namelist() if x.endswith('/task.toml')}==set(SLUGS)
        for rel,want in record['artifact_sha256'].items():assert hashlib.sha256(z.read(rel)).hexdigest()==want,rel
        assert hashlib.sha256(z.read(str(manifest.relative_to(ROOT)))).hexdigest()==digest
    out.with_suffix('.zip.sha256').write_text(sha(out)+'  '+out.name+'\n')
    print('DAY 1 FROZEN',digest,'archive',out,'bytes',out.stat().st_size,'archive_sha256',sha(out),flush=True)
if __name__=='__main__':main()

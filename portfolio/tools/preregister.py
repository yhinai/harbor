from pathlib import Path
import datetime,hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
PRIORS=[('exact-fused-dot',3,5),('mixed-width-tso',4,5),('checkpointed-journal',5,4),('atomic-range-history',5,3),('alignment-relaxation',6,2)]
def distribution(a,b):
    logbeta=lambda x,y: math.lgamma(x)+math.lgamma(y)-math.lgamma(x+y)
    return [math.exp(math.log(math.comb(8,k))+logbeta(a+k,b+8-k)-logbeta(a,b)) for k in range(9)]
if __name__=='__main__':
    path=ROOT/'evidence/day1-preregistration.json'
    if path.exists(): raise SystemExit('Refusing to overwrite a frozen preregistration. Make an explicitly versioned amendment.')
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for slug,_,_ in PRIORS for p in sorted((ROOT/slug).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    content={'label':'inferred','status':'day1_prior_not_final_day2_forecast','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'proxy_trials_observed':0,'frontier_trials_run':0,'forecast_target':'Either Fable or GPT-5.6 Sol under evaluators harness; identity-specific effects unknown','model':'Beta-binomial, 8 trials; task-level uncertainty induces predictive correlation','tasks':[{'rank':i+1,'task':s,'alpha':a,'beta':b,'predicted_K':round(8*a/(a+b)),'expected_K':8*a/(a+b),'P_K':distribution(a,b),'P_hard_conditional_on_validity':sum(distribution(a,b)[:3])} for i,(s,a,b) in enumerate(PRIORS)],'task_sha256':files}
    path.write_text(json.dumps(content,indent=2)+'\n')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'evidence/day1-preregistration.sha256').write_text(digest+'  day1-preregistration.json\n')
    print('Frozen Day 1 preregistration:',digest)

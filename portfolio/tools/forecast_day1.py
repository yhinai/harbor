"""Explicit judgmental transfer model; no paid calls and no target observations."""
import datetime,json,math
from selection import ROOT,SLUGS
# Preserve the Phase 3 subjective priors. These are not fitted to this panel.
PRIORS={'typecheck-soundness-witness':(3,3),'exact-fused-dot':(4,3),'mixed-width-tso':(5,2),'checkpointed-journal':(5,2),'atomic-range-history':(6,2)}
FAMILY_WEIGHTS={'kimi-k3':.5,'glm-5p3':.35,'deepseek-v4p1-flash':.15}
def beta_binomial(a,b):
    return [math.comb(8,k)*math.exp(math.lgamma(a+k)+math.lgamma(b+8-k)-math.lgamma(a+b+8)-math.lgamma(a)-math.lgamma(b)+math.lgamma(a+b)) for k in range(9)]
def shifted_beta(a,b,delta,points=20000):
    # Integrate uncertain proxy p; q=logistic(logit(p)+delta). This shift is an
    # assumption, not an empirically measured ability gap.
    out=[0.]*9;normalizer=0.;lognorm=math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)
    scale=math.exp(delta)
    for i in range(points):
        p=(i+.5)/points;density=math.exp(lognorm+(a-1)*math.log(p)+(b-1)*math.log1p(-p))
        q=scale*p/(1-p+scale*p);normalizer+=density
        for k in range(9):out[k]+=density*math.comb(8,k)*q**k*(1-q)**(8-k)
    return [x/normalizer for x in out]
def mix(prior,families,delta):
    out=[.5*x for x in prior]
    for family,w in FAMILY_WEIGHTS.items():
        stat=families[family];post=stat['proxy_beta_posterior']
        dist=shifted_beta(post['a'],post['b'],delta) if stat['valid_trials'] else prior
        for k,x in enumerate(dist):out[k]+=.5*w*x
    return out
def main():
    analysis=json.loads((ROOT/'analysis/panel-analysis.json').read_text())
    if analysis['attempts_completed']!=55:raise SystemExit('Forecast freeze requires the complete scheduled panel')
    tasks={}
    for task in SLUGS:
        prior=beta_binomial(*PRIORS[task]);families=analysis['family_task_statistics'][task];dist=mix(prior,families,1.)
        expected=sum(k*x for k,x in enumerate(dist));sensitivity={}
        for delta in [0.,1.,2.]:
            d=mix(prior,families,delta);sensitivity[str(delta)]={'expected_K':sum(k*x for k,x in enumerate(d)),'P_K_le_2':sum(d[:3])}
        tasks[task]={'label':'inferred, judgmental forecast conditional on validity','predicted_K_out_of_8':int(math.floor(expected+.5)),
          'expected_K':expected,'P_K_0_through_8':dist,'P_K_le_2':sum(dist[:3]),'confidence':'low',
          'phase3_prior_beta':list(PRIORS[task]),'strength_shift_sensitivity':sensitivity}
    ranking=sorted(SLUGS,key=lambda s:(-tasks[s]['P_K_le_2'],tasks[s]['expected_K']))
    record={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'targets_observed':False,
      'method':'Judgmental mixture: 50% unchanged Phase 3 Beta prior; 50% family mixture of Beta(1+s,1+n-s) proxy posteriors transformed by an assumed +1 frontier log-odds shift. Family weights Kimi .50, GLM .35, DeepSeek .15. A family with no uncensored result contributes its weight back to the Phase 3 prior. Families are alternative predictors, not multiplied independent observations.',
      'assumption_status':'Inferred; neither mixture weights nor ability shift are empirically calibrated. These were chosen during the development panel after the first three type-checker outcomes, before the remaining outcomes. Original priors predate the panel. Sensitivity shifts 0 and 2 are also reported. Mechanism review can contradict these assumptions and must be discussed.',
      'confidence_explanation':'Low: small valid denominators, informative censoring, shared scaffold, no same-task target anchors, and unknown target scaffold. Distribution spread is deliberate; rounded K is only a shorthand.',
      'ranking':ranking,'tasks':tasks}
    (ROOT/'analysis/day1-forecasts.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({s:{k:tasks[s][k] for k in ['predicted_K_out_of_8','expected_K','P_K_le_2']} for s in ranking},indent=2))
if __name__=='__main__':main()

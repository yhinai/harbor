"""Family-separated descriptive statistics; never invokes a model."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,math
from selection import ROOT,SLUGS
MODELS=['kimi-k3','glm-5p3','deepseek-v4p1-flash']
def beta_cdf(x,a,b):
    # Exact finite sum for integer posterior parameters, evaluated stably enough
    # for these small samples. I_x(a,b)=P(Binomial(a+b-1,x)>=a).
    n=a+b-1
    return sum(math.comb(n,j)*x**j*(1-x)**(n-j) for j in range(a,n+1))
def beta_quantile(q,a,b):
    lo,hi=0.,1.
    for _ in range(70):
        mid=(lo+hi)/2
        if beta_cdf(mid,a,b)<q:lo=mid
        else:hi=mid
    return (lo+hi)/2

def inspect(row):
    p=Path(row['trajectory_path']);events=[json.loads(s) for s in p.read_text().splitlines()]
    responses=[e for e in events if e['kind']=='response']
    calls=[e for e in events if e['kind']=='terminal_call']
    results=[e for e in events if e['kind']=='terminal_result']
    exceptions=[e for e in events if e['kind']=='exception']
    category=None
    if row['status']!='valid':
        if any(e['response']['choices'][0].get('finish_reason')=='length' for e in responses):category='output_limit'
        elif row['status']=='ProxyBudgetExceeded':category='budget_limit'
        elif row['status']=='ProxyTurnLimit':category='turn_limit'
        elif row['status']=='ProxyTransportFailure':category='transport_or_incomplete_stream'
        elif row['status']=='RuntimeError' and any('Command timed out after' in e.get('message','') for e in exceptions):category='terminal_harness_timeout'
        elif row['status']=='ProxyProtocolFailure':category='protocol'
        else:category='harness_or_unresolved'
    return {'trial_id':row['trial_id'],'task':row['task'],'model':row['model'].split('/')[-1],
      'replicate':row['replicate'],'reward':row['reward'],'status':row['status'],'exclusion_category':category,
      'trajectory_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'event_count':len(events),
      'terminal_calls':len(calls),'terminal_results':len(results),
      'terminal_timeout_steps':[e['step_index'] for e in results if e['result'].get('timed_out')],
      'tool_nonzero_steps':[e['step_index'] for e in results if e['result'].get('return_code') not in (0,None)],
      'response_steps':[e['step_index'] for e in responses],
      'tool_steps':[e['step_index'] for e in calls],'exception_events':exceptions,
      'usage':{'prompt_tokens':sum(e['response']['usage']['prompt_tokens'] for e in responses),'completion_tokens':sum(e['response']['usage']['completion_tokens'] for e in responses)},
      'known_uncached_cost_estimate_usd':row.get('provider_usage_cost_estimate_usd')}

def main():
    rows=json.loads((ROOT/'evidence/proxy/panel-v120-outcomes.json').read_text())
    trials=[inspect(r) for r in rows];summary={}
    for task in SLUGS:
        families={}
        for model in MODELS:
            selected=[r for r in trials if r['task']==task and r['model']==model]
            valid=[r for r in selected if r['status']=='valid'];s=int(sum(r['reward'] for r in valid));n=len(valid)
            a,b=1+s,1+n-s
            families[model]={'attempts':len(selected),'passes':s,'valid_trials':n,'observed_pass_rate':s/n if n else None,
              'excluded':dict(Counter(r['exclusion_category'] for r in selected if r['status']!='valid')),
              'proxy_beta_posterior':{'a':a,'b':b,'mean':a/(a+b),'equal_tail_95':[beta_quantile(.025,a,b),beta_quantile(.975,a,b)],'is_prior_only':n==0}}
        summary[task]=families
    ledger=json.loads((ROOT/'evidence/proxy-budget.json').read_text());req=list(ledger['requests'].values())
    report={'label':'verified calculations conditional on Beta(1,1) proxy prior and stable Bernoulli sampling',
      'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'attempts_completed':len(rows),'expected_attempts':55,
      'valid_trials':sum(r['status']=='valid' for r in trials),'excluded_trials':sum(r['status']!='valid' for r in trials),
      'smokes_included':False,'family_task_statistics':summary,'trials':trials,
      'budget':{'conservative_booked_usd':ledger['conservative_booked_usd'],
        'known_usage_uncached_estimate_usd':sum(r.get('uncached_rate_estimate_usd',0) for r in req),
        'panel_known_usage_uncached_estimate_usd':sum(r.get('uncached_rate_estimate_usd',0) for r in req if '/panel-v120-' in r['trial']),
        'unsettled_reservations_usd':sum(r['booked_usd'] for r in req if r['status']!='reported_usage'),
        'unsettled_by_status':dict(Counter(r['status'] for r in req if r['status']!='reported_usage')),
        'actual_invoice_total':'unknown','operational_cap_usd':ledger.get('operational_cap_usd'),'authorized_cap_usd':ledger.get('authorized_cap_usd')},
      'limitations':['Informative censoring: valid denominators are conditional on completing the fixed harness.','Families share a scaffold; no independence across families is assumed.','No numerical proxy-to-frontier transfer coefficient was measured.']}
    out=ROOT/'analysis/panel-analysis.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'completed':len(rows),'valid':report['valid_trials'],'excluded':report['excluded_trials'],'budget':report['budget']},indent=2))
if __name__=='__main__':main()

"""Sensitivity analysis for genuine proxy trials, never a substitute for trajectories.
Input JSON list: {task, model, trial_id, reward, status, version, trajectory_path}.
Only status=valid with binary reward is used. Passes/errors are reported separately.
Run: python3 analysis/update_forecasts.py outcomes.json --output analysis/update.json
"""
from pathlib import Path
import argparse,collections,json,math
ROOT=Path(__file__).resolve().parents[1]
def logit(p): return math.log(p/(1-p))
def sigmoid(x): return 1/(1+math.exp(-x))
def summary(weights,grid):
    total=sum(weights); w=[x/total for x in weights]
    dist=[sum(ww*math.comb(8,k)*p**k*(1-p)**(8-k) for p,ww in zip(grid,w)) for k in range(9)]
    return {'P_K':dist,'expected_K':sum(k*p for k,p in enumerate(dist)),'P_K_le_2':sum(dist[:3])}
def beta_interval(a,b):
    def cdf(x):
        n=a+b-1
        return sum(math.comb(n,j)*x**j*(1-x)**(n-j) for j in range(a,n+1))
    ans=[]
    for target in (0.025,0.975):
        lo,hi=0.0,1.0
        for _ in range(60):
            mid=(lo+hi)/2
            if cdf(mid)<target: lo=mid
            else: hi=mid
        ans.append((lo+hi)/2)
    return ans

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('outcomes'); ap.add_argument('--output',required=True); ap.add_argument('--discount',type=float,default=0.25); args=ap.parse_args()
    if not 0<args.discount<=1: raise SystemExit('discount must lie in (0,1]')
    prior=json.loads((ROOT/'evidence/day1-preregistration.json').read_text()); rows=json.loads(Path(args.outcomes).read_text())
    seen=set(); by=collections.defaultdict(list)
    for row in rows:
        key=(row['task'],row['version'],row['model'],row['trial_id'])
        if key in seen: raise SystemExit('Duplicate trial ID')
        seen.add(key)
        if row['status']=='valid' and row['reward'] not in (0,1): raise SystemExit('Valid trials need binary reward')
        if row['status']=='valid' and not Path(row['trajectory_path']).is_file(): raise SystemExit('Missing trajectory: '+row['trajectory_path'])
        by[row['task']].append(row)
    grid=[(i+0.5)/4000 for i in range(4000)]; output={'label':'inferred','status':'sensitivity_analysis_not_final_forecast','assumptions':{'discount':args.discount,'bridge':'logit(p_frontier) = logit(p_proxy) + delta','delta_values':[-1,0,1,2],'warning':'Bridge and likelihood discount are judgments, not calibrated measurements. Keep families and task versions separate. Changed tasks require an explicit transfer judgment.'},'tasks':{}}
    for task in prior['tasks']:
        s=task['task']; trials=by[s]; families=collections.defaultdict(list)
        for row in trials: families[(row['model'],row['version'])].append(row)
        entry={'families':{},'prior_P_K':task['P_K']}
        for (model,version),rs in families.items():
            good=[x for x in rs if x['status']=='valid']; yes=sum(x['reward'] for x in good); no=len(good)-yes
            # Exact beta(1,1) posterior predictive is separate from transfer inference.
            entry['families'][model+'@'+version]={'label':'verified','valid_trials':len(good),'passes':yes,'excluded':dict(collections.Counter(x['status'] for x in rs if x['status']!='valid')),'proxy_posterior_mean':(yes+1)/(len(good)+2),'proxy_95_equal_tail_interval':beta_interval(yes+1,no+1),'frontier_sensitivity':{}}
            a,b=task['alpha'],task['beta']
            for delta in [-1,0,1,2]:
                logs=[]
                for p in grid:
                    q=sigmoid(logit(p)-delta)
                    logs.append((a-1)*math.log(p)+(b-1)*math.log1p(-p)+args.discount*(yes*math.log(q)+no*math.log1p(-q)))
                peak=max(logs); weights=[math.exp(x-peak) for x in logs]
                entry['families'][model+'@'+version]['frontier_sensitivity'][str(delta)]=summary(weights,grid)
        output['tasks'][s]=entry
    Path(args.output).write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__': main()

"""Cross-check concrete semantics, including limits; no model calls."""
from pathlib import Path
import datetime,hashlib,json,random,sys
from selection import ROOT
TASK=ROOT/'typecheck-soundness-witness'
sys.path.insert(0,str(TASK/'environment'));sys.path.insert(0,str(TASK/'audit'))
from language import load,validate,StaticError,InvalidProgram
from checker import check
from interpreter import run
from reference_interpreter import evaluate
from typecheck_baseline import generate

def main():
    seed=20261010;r=random.Random(seed);counts={'programs':0,'accepted':0,'static_rejected':0,'type_error':0,'normal':0,'step_limit':0};boundaries=0
    for path in [TASK/'solution/witness.json',TASK/'audit/equivalent.json']:
        p=load(path.read_text());out=run(p)
        for limit in [1,out['steps']-1,out['steps'],4096]:
            a=run(p,limit);b=evaluate(p,limit);assert {k:a[k] for k in ('status','steps')}==b,(path,limit,a,b);boundaries+=1
    for _ in range(10000):
        p=generate(r);validate(p);counts['programs']+=1
        try:check(p);counts['accepted']+=1
        except StaticError:counts['static_rejected']+=1;continue
        limit=r.choice([10,30,100,4096]);a=run(p,limit);b=evaluate(p,limit)
        assert {k:a[k] for k in ('status','steps')}==b,(p,a,b)
        counts[a['status']]+=1
    report={'label':'verified','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seed':seed,'counts':counts,'boundary_comparisons':boundaries,'scope':'A direct recursive audit evaluator agrees with the production explicit-stack interpreter on acceptance-filtered random programs and reference programs; not exhaustive','audit_evaluator_sha256':hashlib.sha256((TASK/'audit/reference_interpreter.py').read_bytes()).hexdigest()}
    (ROOT/'evidence/typecheck-interpreter-crosscheck.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()

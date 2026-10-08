"""Record a review of agent-facing instructions without modifying task files."""
import datetime,hashlib,json,re
from selection import ROOT,SLUGS

def main():
    rows={}
    patterns=[r'do not assume SC',r'greedy is insufficient',r'brute.force',r'failure mode',r'failure mechanism',r'memo key',r'latent effect',r'loop.carried',r'intersection.based']
    for slug in SLUGS:
        p=ROOT/slug/'instruction.md';text=p.read_text();hits=[x for x in patterns if re.search(x,text,re.I)]
        assert not hits,(slug,hits)
        rows[slug]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'failure_mode_hint_matches':hits,'review':'Specification, submission artifact and commands only; semantic requirements retained'}
    report={'label':'verified','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Heuristic scan plus author review of all five current instruction files; not a model trial','tasks':rows}
    (ROOT/'evidence/instruction-audit-v1.1.0.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Five instruction files reviewed; no mechanism hints found.')
if __name__=='__main__':main()

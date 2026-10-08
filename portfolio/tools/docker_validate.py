from pathlib import Path
import datetime,json,os,subprocess,uuid
ROOT=Path(__file__).resolve().parents[1]
from selection import RETAINED as SLUGS
def docker(*args):
    p=subprocess.run(['docker',*map(str,args)],text=True,capture_output=True,timeout=240)
    if p.returncode: raise RuntimeError({'command':list(args),'code':p.returncode,'stderr':p.stderr[-6000:]})
    return p.stdout

def main():
    report={'label':'verified','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Docker Linux runtime, network none, 2 CPUs, 1 GiB, unprivileged candidate execution','docker_version':docker('version','--format','{{.Server.Version}}'),'tasks':{}}
    for slug in SLUGS:
        image='portfolio-check-'+slug
        docker('build','-t',image,ROOT/slug/'environment')
        name='portfolio-audit-'+uuid.uuid4().hex[:12]
        docker('run','-d','--name',name,'--network','none','--cpus','2','--memory','1g',image,'sleep','infinity')
        try:
            docker('cp',str(ROOT/slug/'tests')+'/.',name+':/tests')
            docker('cp',str(ROOT/slug/'solution')+'/.',name+':/solution')
            probes=[('canonical',ROOT/slug/'solution/canonical.py',1),('equivalent',ROOT/slug/'audit/equivalent.py',1)]
            probes += [(p.stem,p,0) for p in sorted((ROOT/slug/'audit').glob('incorrect-*.py'))]
            # A direct attempt to copy hidden expected responses must be denied.
            cheat=ROOT/'evidence/test-reader-probe.py'
            cheat.write_text("import json,sys\ncases=json.load(open('/tests/cases.json'))\nfor c in cases: print(json.dumps(c['expected']))\n")
            probes.append(('read-hidden-tests',cheat,0))
            rows={}
            for tag,source,want in probes:
                docker('cp',source,name+':/app/main.py')
                docker('exec','-u','root',name,'bash','/tests/test.sh')
                row=json.loads(docker('exec','-u','root',name,'cat','/logs/verifier/status.json'))
                reward=float(docker('exec','-u','root',name,'cat','/logs/verifier/reward.txt'))
                assert reward==want,(slug,tag,row)
                assert row.get('hardened') is True,(slug,tag,row)
                rows[tag]={'reward':reward,**row}
            report['tasks'][slug]=rows
            print(slug,len(rows),'Docker checks passed',flush=True)
        finally: docker('rm','-f',name)
    (ROOT/'evidence/docker-validation.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__': main()

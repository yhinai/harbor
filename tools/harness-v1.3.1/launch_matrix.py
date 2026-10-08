"""Register one offline system launchd job running as matrix; never expose secrets."""
from pathlib import Path
from dotenv import dotenv_values
import argparse,datetime,json,subprocess,os,pwd
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--run-id',default='mini-offline-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));args=ap.parse_args()
assert pwd.getpwuid(os.getuid()).pw_name=='matrix','Launch as matrix, not another account'
assert args.run_id and all(c.isalnum() or c in '-_' for c in args.run_id)
assert not (ROOT/'analysis/harness-v1.3.1/runs'/args.run_id).exists(),'Run ID already exists'
label='org.harbor.offline.'+args.run_id.lower();work=ROOT/'tmp/launchd'/args.run_id;work.mkdir(parents=True,exist_ok=True)
record={'run_id':args.run_id,'launchd_label':label,'launchd_domain':'system','plist_path':'/Library/LaunchDaemons/'+label+'.plist','stdout_log':str(work/'stdout.log'),'stderr_log':str(work/'stderr.log'),'status_file':str(ROOT/'analysis/harness-v1.3.1/runs'/args.run_id/'status.json'),'retries_enabled':False,'job_user':'matrix','credentials_passed_to_job':False,'root':str(ROOT)}
installer='''import json,sys,os,plistlib,subprocess
from pathlib import Path
r=json.loads(sys.argv[1]);root=Path(r['root']);p=Path(r['plist_path'])
assert p.parent==Path('/Library/LaunchDaemons') and p.name.startswith('org.harbor.offline.')
assert not p.exists()
spec={'Label':r['launchd_label'],'UserName':'matrix','GroupName':'staff','ProgramArguments':['/usr/bin/caffeinate','-i',str(root/'tmp/harbor-venv/bin/python'),str(root/'tools/harness-v1.3.1/supervise_offline.py'),'--run-id',r['run_id']],'WorkingDirectory':str(root),'RunAtLoad':True,'KeepAlive':False,'ProcessType':'Background','StandardOutPath':r['stdout_log'],'StandardErrorPath':r['stderr_log']}
with p.open('wb') as f:plistlib.dump(spec,f)
os.chmod(p,0o644);os.chown(p,0,0)
subprocess.run(['/bin/launchctl','bootstrap','system',str(p)],check=True)
'''
password=dotenv_values(ROOT/'.env').get('SUDO_PASSWORD')
if not password:raise SystemExit('Sudo password is absent; no job started')
p=subprocess.run(['sudo','-S','-p','','/usr/bin/python3','-c',installer,json.dumps(record)],input=password+'\n',text=True,capture_output=True)
if p.returncode:raise SystemExit('System launchd registration failed; secret values suppressed. No success claimed.')
(ROOT/'tmp/launchd/latest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

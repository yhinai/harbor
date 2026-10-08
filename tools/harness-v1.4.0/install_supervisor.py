"""Register the finite study as a system service running as the current user."""
import argparse,getpass,os,plistlib,subprocess,sys,tempfile
from pathlib import Path
from dotenv import dotenv_values
root=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--study-id',required=True);a=ap.parse_args()
assert all(c.isalnum() or c in '-_' for c in a.study_id)
label='org.harbor.'+a.study_id
logs=root/'tmp/launchd'/a.study_id;logs.mkdir(parents=True,exist_ok=True)
plist={'Label':label,'UserName':getpass.getuser(),'GroupName':'staff','WorkingDirectory':str(root),'ProgramArguments':['/usr/bin/caffeinate','-i',sys.executable,str(root/'tools/harness-v1.4.0/panel_runner.py'),'--study-id',a.study_id],'EnvironmentVariables':{'HOME':str(Path.home()),'PATH':str(Path.home()/'.local/harbor-runtime/bin')+':/usr/bin:/bin:/usr/sbin:/sbin'},'RunAtLoad':True,'KeepAlive':{'SuccessfulExit':False},'ThrottleInterval':60,'ProcessType':'Background','StandardOutPath':str(logs/'stdout.log'),'StandardErrorPath':str(logs/'stderr.log')}
password=dotenv_values(root/'.env').get('SUDO_PASSWORD');assert password,'Missing private sudo credential'
with tempfile.NamedTemporaryFile() as f:
 f.write(plistlib.dumps(plist));f.flush()
 dest='/Library/LaunchDaemons/'+label+'.plist'
 for cmd in [['install','-o','root','-g','wheel','-m','644',f.name,dest],['launchctl','bootstrap','system',dest]]:
  r=subprocess.run(['sudo','-S','-p','',*cmd],input=password+'\n',text=True,capture_output=True)
  if r.returncode:raise SystemExit('Supervisor registration failed: '+r.stderr.replace(password,'[redacted]'))
print('Registered system supervisor '+label+' as '+getpass.getuser()+'. No credentials in service configuration.')

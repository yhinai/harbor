"""Grade a JSON artifact using frozen language, checker and interpreter files."""
import os,pathlib,sys,json,traceback
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'reference'))
from language import load,InvalidProgram,StaticError,MAX_BYTES
from checker import check
from interpreter import run
LOG=pathlib.Path(os.environ.get('VERIFIER_LOG_DIR','/logs/verifier'))

def save(reward,status):
    LOG.mkdir(parents=True,exist_ok=True)
    (LOG/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    p=LOG/'reward.tmp';p.write_text(str(reward)+'\n');p.replace(LOG/'reward.txt')

def main():
    hardened=sys.platform=='linux' and os.geteuid()==0
    if hardened:
        for p in (HERE,LOG,pathlib.Path('/solution')):
            p.mkdir(parents=True,exist_ok=True);p.chmod(0o700)
    # Read only the declared artifact, under the submitting account's identity.
    # Root does not follow a candidate symlink into protected files.
    def restrict():
        if hardened:
            import pwd
            a=pwd.getpwnam('agent');os.setgroups([]);os.setgid(a.pw_gid);os.setuid(a.pw_uid)
    import subprocess
    path=str(pathlib.Path(os.environ.get('APP_DIR','/app'))/'witness.json')
    try:
        p=subprocess.run([sys.executable,'-I','-c','import sys;sys.stdout.buffer.write(open(sys.argv[1],"rb").read(65537))',path],capture_output=True,timeout=5,preexec_fn=restrict,env={'PATH':'/usr/local/bin:/usr/bin:/bin'})
    except subprocess.TimeoutExpired:
        save(0,{'status':'unreadable_artifact','hardened':hardened});return
    if p.returncode or len(p.stdout)>MAX_BYTES:
        save(0,{'status':'invalid_artifact','hardened':hardened});return
    try:
        program=load(p.stdout.decode('utf-8'));check(program)
    except (UnicodeError,InvalidProgram,StaticError,TypeError,ValueError,RecursionError) as e:
        save(0,{'status':'rejected','reason':str(e),'hardened':hardened});return
    try:result=run(program)
    except (KeyError,InvalidProgram) as e:
        save(0,{'status':'other_runtime_error','reason':str(e),'hardened':hardened});return
    reward=int(result['status']=='type_error')
    save(reward,{'status':'pass' if reward else 'no_type_error','hardened':hardened,'execution':result})
if __name__=='__main__':
    try:main()
    except Exception:
        save(0,{'status':'infrastructure_error','traceback':traceback.format_exc()});sys.exit(2)

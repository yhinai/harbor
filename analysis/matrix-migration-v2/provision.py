"""Install pinned official runtime binaries in a private user prefix; no sudo."""
from pathlib import Path
import hashlib,json,urllib.request,tarfile,shutil,os,subprocess
prefix=Path.home()/'.local/harbor-runtime';cache=prefix/'downloads';cache.mkdir(parents=True,exist_ok=True);(prefix/'bin').mkdir(exist_ok=True)
items=[
('lima','https://github.com/lima-vm/lima/releases/download/v2.2.1/lima-2.2.1-Darwin-arm64.tar.gz','9e9eacce88f37e185c346bad73aa6136f738d8cdf8c3bb23cd42b071824bc66e'),
('colima','https://github.com/abiosoft/colima/releases/download/v0.10.3/colima-Darwin-arm64','980ad8bf61a4ca370243f4cb41401a61276dcd2c2502bee7b9b86f9250169f34'),
('uv','https://github.com/astral-sh/uv/releases/download/0.12.23/uv-aarch64-apple-darwin.tar.gz','50487ae565ccd96e499056b4674d438f4c53170202617b4c759defe0c6a1b544'),
('docker','https://download.docker.com/mac/static/stable/aarch64/docker-29.8.2.tgz',None)]
records=[]
for name,url,want in items:
 p=cache/url.rsplit('/',1)[-1]
 if not p.exists():
  print('Downloading',name,flush=True);urllib.request.urlretrieve(url,p)
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 if want:assert got==want,(name,got)
 records.append({'tool':name,'url':url,'sha256':got,'published_digest_checked':want is not None})
 if name=='colima':shutil.copyfile(p,prefix/'bin/colima');(prefix/'bin/colima').chmod(0o755)
 else:
  target=prefix if name=='lima' else cache/name;target.mkdir(exist_ok=True)
  with tarfile.open(p) as t:
   for m in t.getmembers():
    assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts,m.name
   t.extractall(target)
  if name in ('uv','docker'):
   for exe in (('uv','uvx') if name=='uv' else ('docker',)):
    src=next(f for f in target.rglob(exe) if f.is_file());shutil.copy2(src,prefix/'bin'/exe)
(prefix/'installed.json').write_text(json.dumps(records,indent=2)+'\n')
env=os.environ.copy();env['PATH']=str(prefix/'bin')+':/usr/bin:/bin:/usr/sbin:/sbin'
for cmd in [('limactl','--version'),('colima','version'),('uv','--version'),('docker','--version')]:subprocess.run(cmd,env=env,check=True)
print('Private runtime binaries installed; no shared permissions changed.',flush=True)

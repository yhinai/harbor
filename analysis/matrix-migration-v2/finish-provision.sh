#!/bin/sh
# Run on matrix after provision.py. Installs verified official Docker plugins.
set -eu
mkdir -p "$HOME/.local/harbor-runtime/docker-config/cli-plugins"
python3 - <<'PY'
import hashlib,json,urllib.request
from pathlib import Path
root=Path.home()/'.local/harbor-runtime/docker-config'
for name,version,url,want in [
 ('compose','v5.6.0','https://github.com/docker/compose/releases/download/v5.6.0/docker-compose-darwin-aarch64','bd714a42b46e51757fc1121085b3096b9064e3f80d3ca5a991e33f44df4f43c9'),
 ('buildx','v0.38.0','https://github.com/docker/buildx/releases/download/v0.38.0/buildx-v0.38.0.darwin-arm64','85989b895add5f119c1ccf8eada2f6892fc33ccf16bd8917638eae404ef26344')]:
 p=root/'cli-plugins'/('docker-'+name);urllib.request.urlretrieve(url,p)
 got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==want,(name,got);p.chmod(0o755)
 (root/(name+'-install.json')).write_text(json.dumps({'version':version,'url':url,'sha256':got},indent=2)+'\n')
PY
export PATH="$HOME/.local/harbor-runtime/bin:$PATH"
export DOCKER_CONFIG="$HOME/.local/harbor-runtime/docker-config"
export DOCKER_HOST="unix://$HOME/.colima/frontier-portfolio/docker.sock"
colima start --profile frontier-portfolio --vm-type vz --cpu 10 --memory 10 --disk 60 --activate=false
uv venv --python 3.12 tmp/harbor-venv
uv pip install --python tmp/harbor-venv/bin/python harbor==0.24.0 httpx python-dotenv

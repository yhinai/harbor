import json,pathlib,subprocess,sys
from public_contract import check
HERE=pathlib.Path(__file__).resolve().parent
cases=json.loads((HERE/'examples.json').read_text())
p=subprocess.run([sys.executable,str(HERE/'main.py')],input=''.join(json.dumps(x['request'])+'\n' for x in cases),text=True,capture_output=True,cwd=HERE)
if p.returncode: print(p.stderr); sys.exit(1)
lines=p.stdout.splitlines()
if len(lines)!=len(cases): print('Wrong number of response lines'); sys.exit(1)
for case,line in zip(cases,lines):
    if not check('exact-fused-dot',case['request'],case['expected'],json.loads(line)):
        print('FAILED',case['id']); sys.exit(1)
print('Passed',len(cases),'public examples')

"""Create a review archive only when all frozen package and evidence bytes match."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pointer=json.loads((ROOT/'evidence/current-freeze.json').read_text())
    manifest=ROOT/'evidence'/pointer['amendment'];assert sha(manifest)==pointer['sha256']
    record=json.loads(manifest.read_text());files={}
    for group in ['task_sha256','evidence_sha256','document_sha256','tool_sha256','historical_record_sha256']:
        for rel,want in record[group].items():
            p=ROOT/rel;assert sha(p)==want,rel;files[rel]=p
    for p in [manifest,manifest.with_suffix('.sha256'),ROOT/'evidence/current-freeze.json']:
        files[str(p.relative_to(ROOT))]=p
    out=ROOT.parent/'phase3-portfolio-v1.1.0.zip'
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel,p in sorted(files.items()):z.write(p,rel)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        slugs={x.split('/')[0] for x in z.namelist() if x.endswith('/task.toml')}
        assert slugs=={t['task'] for t in record['tasks']}
        for task in record['tasks']:
            for rel in ['task.toml','instruction.md','environment/Dockerfile','tests/test.sh','solution/solve.sh',task['canonical_artifact']]:assert task['task']+'/'+rel in z.namelist()
        for rel,want in record['task_sha256'].items():assert hashlib.sha256(z.read(rel)).hexdigest()==want
    checksum=sha(out);out.with_suffix('.zip.sha256').write_text(checksum+'  '+out.name+'\n')
    print(out,'bytes',out.stat().st_size,'sha256',checksum)
if __name__=='__main__':main()

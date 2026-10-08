"""Focused regression checks, without inference."""
from pathlib import Path
import importlib.util,json
root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('v143_tests',Path(__file__).with_name('parallel_runner.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for available in [3072,10000]:
 action=m.memory_action(available,5,6);assert action['oom_counter_increased'] and not action['emergency_stop'] and not action['pause_new_admission']
assert m.memory_action(1000,5,5)['pause_new_admission'] and not m.memory_action(1000,5,5)['emergency_stop']
assert m.memory_action(511,5,5)['emergency_stop']
s=m.Study('mini-panel-20261008-v140');s.check()
# Avoid writing live status: assemble the same ordered correction view directly.
rows={}
for folder in ['outcomes','outcome-corrections/v1.4.2','outcome-corrections/v1.4.3']:
 for p in (s.path/folder).glob('*.json'):
  r=json.loads(p.read_text());rows[r['attempt_id']]=r
valid=[r for r in rows.values() if r['phase']=='panel' and r['status']=='valid']
keys=[(r['model'],r['task'],r['replicate']) for r in valid];assert len(keys)==len(set(keys))
assert all(r['reward']==1 and not r['exception'] and r['tool_calls']>0 for r in valid)
for name in s.amend['restored_verified_positive_attempts']:assert rows[name]['status']=='valid' and rows[name]['reward']==1
print(json.dumps({'label':'verified offline monitor regression and correction accounting; no inference','valid_trials':len(valid),'passes':sum(r['reward']==1 for r in valid),'restored':len(s.amend['restored_verified_positive_attempts']),'unique_valid_logical_slots':True,'container_oom_does_not_halt_at_high_available_memory':True,'frozen_source_hashes_match':True},indent=2))

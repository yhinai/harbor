"""Render reviewed, step-indexed evidence; never invent mechanism labels."""
import json
from selection import ROOT,SLUGS
review=json.loads((ROOT/'analysis/trajectory-review.json').read_text())
analysis=json.loads((ROOT/'analysis/panel-analysis.json').read_text())
rows=analysis['trials']
assert set(review['trials'])=={r['trial_id'] for r in rows}
parts=['# Development-panel trajectory evidence\n',
 '**Verified — review scope.** '+review['review_method']+'\n',
 '**Verified — exclusions.** Smokes are excluded. Output, transport, protocol, turn and budget limits are reported as censored observations, even when an unfinished program appears promising. A timeout returned as a tool result is recoverable and is not by itself a censored trial. The final Harbor result determines the observed reward.\n',
 '**Inferred — causal limits.** A successful final artifact establishes that this attempt solved the behavior checked by the grader. A failed artifact alone does not identify the first wrong commitment; a mechanism diagnosis below cites the concrete commands/results that support it. No target trajectory exists.\n']
for task in SLUGS:
    parts.append('## '+task+'\n')
    summary=review.get('task_summaries',{}).get(task)
    assert summary,'Missing authored task summary: '+task
    parts.append(summary+'\n')
    for row in sorted([r for r in rows if r['task']==task],key=lambda r:(r['model'],r['replicate'])):
        note=review['trials'][row['trial_id']]
        outcome='reward '+str(row['reward']) if row['status']=='valid' else 'excluded: '+str(row['exclusion_category'])
        parts.append('### '+row['model']+' · replicate '+str(row['replicate'])+' · '+outcome+'\n')
        parts.append('Raw trial: `'+row['trial_id']+'`. Trajectory SHA-256: `'+row['trajectory_sha256']+'`.\n')
        for key,label in [('verified_steps','Verified — events'),('reached_crux','Inferred — crux'),('wrong_commitment','Inferred — commitment'),('recovered','Inferred — recovery'),('mechanism_judgment','Mechanism judgment')]:
            parts.append('**'+label+'.** '+note[key]+'\n')
(ROOT/'analysis/trajectory-notes.md').write_text('\n'.join(parts)+'\n')
print('Rendered',len(rows),'reviewed attempts')

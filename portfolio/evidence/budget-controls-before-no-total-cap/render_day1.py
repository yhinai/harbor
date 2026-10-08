"""Render final registration from actual statistics and authored rationales."""
import json
from selection import ROOT
analysis=json.loads((ROOT/'analysis/panel-analysis.json').read_text());forecast=json.loads((ROOT/'analysis/day1-forecasts.json').read_text());review=json.loads((ROOT/'analysis/trajectory-review.json').read_text())
assert analysis['attempts_completed']==55
mechanisms={
 'typecheck-soundness-witness':'Track nested returned-function writes through loop-carried assignments; a cached join omits nested effects and preserves a stale cell fact.',
 'exact-fused-dot':'Preserve exact products through cancellation and round once; intermediate rounding or an incorrect tie, exceptional value, zero sign or flag changes the answer.',
 'mixed-width-tso':'Enumerate complete machine outcomes with per-byte forwarding, FIFO drains and local synchronization; simplifying a state transition loses or adds outcomes.',
 'checkpointed-journal':'Compose prefix validity, transaction incarnations, commit seals and checkpoint state; applying a locally plausible replay rule can commit the wrong bytes.',
 'atomic-range-history':'Search whole-transaction orders consistent with real-time and range observations; an incomplete order search or wrong absence semantics changes admissibility.'}
validation={
 'typecheck-soundness-witness':'900 s random/coverage-guided baseline: 3,245,426 programs, 1,581,430 accepted, zero qualifying errors; two distinct reference programs pass. First design was found in 1.8 s and replaced.',
 'exact-fused-dot':'21,375 differential cases; four substantive wrong variants rejected. No separate timed difficulty baseline was run.',
 'mixed-width-tso':'72 differential cases; five substantive wrong variants rejected. No separate timed difficulty baseline was run.',
 'checkpointed-journal':'377 differential cases; four substantive wrong variants rejected. No separate timed difficulty baseline was run.',
 'atomic-range-history':'139 differential cases; four substantive wrong variants rejected. Ten transactions permit exhaustive search. No separate timed difficulty baseline was run.'}
anchors={
 'typecheck-soundness-witness':'break-filter-js-from-html: older GPT-5/Codex CLI 0/5; later Opus 4.5/Terminus 80%, denominator unknown.',
 'exact-fused-dot':'bn-fit-modify: older GPT-5/Codex CLI 3/4; weak numerical analogy.',
 'mixed-width-tso':'fix-ocaml-gc: structural systems-state reference; no denominator-backed rate found.',
 'checkpointed-journal':'build-pmars: older GPT-5/Codex CLI 5/5; low-relevance control reference.',
 'atomic-range-history':'build-cython-ext: older GPT-5/Codex CLI 4/4; low-relevance control reference.'}
workflow={
 'typecheck-soundness-witness':'W2: checker, explicit-stack interpreter, separate recursive evaluator, random generation and revision.',
 'exact-fused-dot':'W1: integer accumulator versus Fraction/encoding-search alternative.',
 'mixed-width-tso':'W1: immutable DFS versus per-byte BFS.',
 'checkpointed-journal':'W1: streaming staging versus parse-and-bundle replay.',
 'atomic-range-history':'W1: cached search versus permutation/replay.'}
lines=['# Task portfolio\n',
 '**Verified — registration scope.** Five validated Harbor packages, held at the exact Phase 3 bytes throughout the development panel. This registration precedes evaluator overnight and target results. No target model was run. `report.md` is deferred.\n',
 '**Verified — trial accounting.** Kimi/GLM/DeepSeek below means passes / uncensored trials. All 55 scheduled attempts are preserved; smokes are excluded. Output, transport, protocol, budget and harness failures are excluded from difficulty evidence. Family-specific uncertainty and exclusions are in [panel analysis](analysis/panel-analysis.json).\n',
 '**Inferred — ranked forecast.** Most to least likely to satisfy K ≤ 2 of 8, conditional on task validity. Confidence is **low** for all five. Rounded expected K is a shorthand; complete distributions, P(K ≤ 2), assumptions and sensitivity are in [forecasts](analysis/day1-forecasts.json).\n',
 '| Rank / task | Capability gap and failure mechanism — inferred | Predicted K / 8 — inferred | Evidence | Workflow — verified |',
 '| --- | --- | ---: | --- | --- |']
for rank,task in enumerate(forecast['ranking'],1):
    f=forecast['tasks'][task];stats=analysis['family_task_statistics'][task]
    rates=', '.join(label+' '+str(stats[m]['passes'])+'/'+str(stats[m]['valid_trials']) for m,label in [('kimi-k3','Kimi'),('glm-5p3','GLM'),('deepseek-v4p1-flash','DeepSeek')])
    excluded=sum(sum(s['excluded'].values()) for s in stats.values())
    assert f.get('rationale'),'Add an authored rationale for '+task
    evidence='**Verified:** '+rates+'; '+str(excluded)+' excluded. '+validation[task]+' [Step evidence](analysis/trajectory-notes.md#'+task+'). **Reported:** '+anchors[task]+' **Inferred:** '+f['rationale']
    lines.append('| '+str(rank)+' · '+task+' | '+mechanisms[task]+' | '+str(f['predicted_K_out_of_8'])+' | '+evidence+' | '+workflow[task]+' |')
lines += ['\n**Inferred — transfer method.** '+forecast['method']+' These numerical choices are subjective, not a learned conversion from proxy rates to target rates. '+forecast['confidence_explanation']+' Older anchors are structural references and, as requested, upper-bound difficulty comparisons for newer targets; their rates are not task-specific estimates. [Sources and limits](analysis/research-memo.md#4-four-historical-calibration-anchors).\n',
 '**Verified — W1/W2 provenance.** One Codex assistant performed generation, implementation, critique, testing and revision; no separate critic or subagent. Python, shell, Docker/Colima, Harbor oracle and versioned scripts supplied checks. Exact agent-facing task/system/tool prompts are in the package instructions and `tools/fireworks_agent.py`; human authoring prompts are summarized in [PROMPTS.md](PROMPTS.md). Alternatives use different algorithms, with residual same-author bias.\n',
 '**Verified — validity evidence.** Canonical and alternative correct solutions pass; authored wrong solutions fail; input-bound, isolation and five Harbor-oracle checks pass in [final validation](evidence/final-validation-v1.1.0.json). Unchanged hashes connect those checks to these packages. These controls support validity, not proof against every unseen wrong or correct program.\n',
 '**Verified — protocol.** All three repaired tool smokes pass. Panel settings: Kimi maximum effort, GLM/DeepSeek high effort, temperature 1, up to 65,536 output tokens/call, 60 turns, 30-minute package allowance and 60-second maximum terminal command; per-trial dollar reservation limits are $4/$2/$1. The first 16 attempts used three workers and a shared 2-CPU/3-GB Docker VM; after all 16 finished, the user requested 14 workers and a 12-CPU/16-GB VM for the remaining 39. Each trial retained its 2-CPU/1-GB container limits. No charged attempt was interrupted or restarted for this change. Shared contention differs between batches and is a harness covariate. [Resource amendment](evidence/parallelism-amendment.json). Full transcripts include raw stream chunks. Prior interrupted smokes and unknown-usage reservations remain in the audit, separate from pass counts.\n',
 '**Inferred — falsification and revision.** For the top-ranked task, a valid frontier K ≥ 3 falsifies meeting the hard criterion. Successful trajectories that handle its predicted crux weaken the mechanism. [Update rules](analysis/update-rules.md), written before this development panel, define mechanism checks and repair/harden/retain/retire gates before evaluator evidence arrives. Any revised package needs a new version, controls, oracle and forecast.\n']
b=analysis['budget']
lines += ['**Verified — cost accounting.** Known provider usage at uncached rates totals $'+format(b['known_usage_uncached_estimate_usd'],'.6f')+' across the full project; the current panel accounts for $'+format(b['panel_known_usage_uncached_estimate_usd'],'.6f')+'. The conservative ledger (including margin and unknown usage) is $'+format(b['conservative_booked_usd'],'.6f')+' against the $170 operational cap. **Unknown:** actual invoice total, target outcomes, evaluator overnight results and the proxy-to-target ability gap. No further paid work is authorized after the freeze.\n',
 '**Verified — final artifacts.** [Versioned amendment](evidence/day1-amendment-v1.2.0.json) is produced by the freeze procedure, which records package/evidence hashes and admits `day1-submission.zip` only after every archived artifact matches and exactly the five selected packages are present.\n']
(ROOT/'day1.md').write_text('\n'.join(lines)+'\n');print('Rendered complete Day 1 registration')

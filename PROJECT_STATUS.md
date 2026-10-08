# Progress checkpoint

Status recorded on 8 October 2026 from the saved project artifacts. This checkpoint documents existing work; it does not run new evaluations or change the frozen submission.

## Work completed

1. **Verified:** The research memo collects benchmark papers, failure studies, actual task-file inspection, historical calibration anchors, validity concerns, and limits of proxy-to-frontier transfer. See [memo](analysis/research-memo.md) and [source records](analysis/sources/).
2. **Verified:** Portfolio decisions and revisions are recorded in [decision memo](analysis/portfolio-decision.md), [decision data](analysis/portfolio-decision-v1.json), and versioned amendments under `portfolio/evidence/`.
3. **Reported selection, verified against saved packages:** The final five are `typecheck-soundness-witness`, `exact-fused-dot`, `mixed-width-tso`, `checkpointed-journal`, and `atomic-range-history`. SQLite was dropped, alignment-relaxation retired, and atomic-range-history restored. Historical decisions remain preserved rather than rewritten.
4. **Verified from validation records:** Canonical and alternative correct solutions pass; authored wrong solutions fail; isolation and five Harbor-oracle checks pass. See [validation](portfolio/evidence/final-validation-v1.1.0.json) and [oracles](portfolio/evidence/harbor-oracles-v1.1.0.json). These checks were recorded by the main workflow, not rerun by this checkpoint operation.
5. **Verified from saved baseline evidence:** The final checker design survived a 900-second random/coverage-guided baseline: 3,245,426 generated programs, 1,581,430 accepted, zero qualifying runtime type errors. An earlier design was found quickly and replaced. **Inferred:** A negative generator baseline does not imply difficulty for an agent that reasons about the checker.
6. **Verified:** Three tool-use compatibility smokes and the original 55-attempt development panel completed. Full outcomes, trajectories, exclusions, accounting, and review notes are preserved.
7. **Verified:** Day 1 forecasts, update rules, registration, and version 1.2.0 freeze exist. The current manifest is [here](portfolio/evidence/day1-amendment-v1.2.0.json); the submission is [here](day1-submission.zip).

## Findings

Pass rates below use only uncensored trials. The excluded count is separate; it is not a count of semantic failures.

| Task | Passes / uncensored trials | Excluded attempts | Forecast K / 8 |
| --- | ---: | ---: | ---: |
| exact-fused-dot | 3 / 3 | 8 | 5 |
| typecheck-soundness-witness | 5 / 5 | 6 | 5 |
| mixed-width-tso | 9 / 9 | 2 | 6 |
| atomic-range-history | 3 / 3 | 8 | 6 |
| checkpointed-journal | 11 / 11 | 0 | 7 |

**Verified:** All 31 uncensored trials pass. The 24 exclusions comprise 16 budget limits, four terminal harness timeouts, three originally labeled transport failures, and one output limit. The post-freeze audit below refines the three transport labels to active-stream client deadline interruptions. Smokes do not enter these denominators. Family-specific rates and intervals are in [panel analysis](portfolio/analysis/panel-analysis.json).

**Inferred:** Present evidence supports validity more strongly than difficulty. Successful agents handle the intended semantic crux; some interrupted agents also recover genuine implementation errors. In particular, every Kimi and GLM exact-fused-dot attempt is budget-censored, so their pass rates are unknown. The top ranking reflects retained uncertainty rather than demonstrated hardness.

**Inferred:** The ranked forecasts are low-confidence judgments, not direct transfers of proxy rates. Full P(K=0..8), assumptions, strength-shift sensitivity, and rationales appear in [forecasts](portfolio/analysis/day1-forecasts.json). Older-generation anchors are weak structural comparisons, not measured pass rates on these new tasks.

## Runtime and cost history

**Verified:** The first 16 attempts used three workers in a shared 2-CPU/3-GiB Docker VM. At the user's request, the remaining 39 used up to 14 workers with a 12-CPU/16-GiB VM. Each task container retained its original limits; earlier trials finished before resizing. See [resource amendment](portfolio/evidence/parallelism-amendment.json).

**Verified:** The original panel used per-trial reservation limits of $4/$2/$1. After it ended, the user requested $100 per-trial ceilings and removed the aggregate ceiling. The saved configuration amendments preserve this distinction. No supplemental trials were started before this freeze.

**Reported:** The user's last stated billed spend was $19.07. **Verified calculation:** Saved provider usage at uncached rates totals $34.598705; conservative accounting, including margin and unknown-usage reservations, totals $50.697155. **Unknown:** Reconciled final invoice total. These figures measure different things and must not be presented as interchangeable charges.

## Deferred work

- **Unknown:** Evaluator overnight rewards and trajectories; frontier outcomes.
- `report.md` is deferred until those evaluator results exist.
- No follow-up batch is included in the original 55-attempt panel or this freeze.
- Any future package or evaluation revision needs a new version and explicit evidence provenance.

**Verified project record:** The allowed development models were Kimi K3, GLM-5.3, and DeepSeek V4.1 Flash. No Fable or GPT-5.6 target run is recorded or claimed. The checkpoint operation itself makes no paid model calls.

## Post-freeze audit milestone — 8 October 2026

**Verified:** The offline [audit](analysis/post-day1-review/review.md) rechecked all 457 frozen artifact hashes against both the workspace and submission archive. The original v1.2.0 packages, forecasts, and archive remain unchanged. The separate audit has its own [hash manifest](analysis/post-day1-review/audit-manifest.json).

**Verified:** All 16 budget interruptions crossed the original per-trial reservation limits, not an aggregate project ceiling. The three client-deadline cases were still streaming immediately before cancellation at 900 seconds. Four terminal calls failed at the outer harness timeout; one DeepSeek answer exhausted its output allowance. See the [24-attempt audit](analysis/post-day1-review/interruptions.json).

**Verified:** An offline Docker experiment reproduced a terminal-wrapper process cleanup problem. An experimental repair passed five synthetic checks; the initial negative reproduction is also preserved. **Unknown:** Harbor integration of that repair has not been validated. It is not installed into the frozen harness.

**Inferred:** The interrupted attempts are censored diagnostic evidence, not completed wrong solutions. No saved submission snapshot exists for these attempts, so authentic graded outcomes cannot simply be recovered. Any follow-up should use a separately recorded protocol and fresh containers; changed-protocol results must not silently replace the original attempts.

**Verified source inspection; inferred candidates:** Lua collection-state and Ninja incremental-build regressions were investigated as possible future debugging tasks. Neither is built or validated. SQLite remains dropped and the five-task selection is unchanged. No additional paid calls or evaluator-results report were made.

## GitHub synchronization

The repository is [yhinai/harbor](https://github.com/yhinai/harbor), branch `main`, starting from checkpoint `6bcde28`. After each meaningful completed milestone, update this progress record, commit relevant research, decisions, packages, evidence, and deliverables, push without force, and verify the remote commit. Preserve frozen artifacts and record revisions separately. Coordinate with active writers before staging their files. Credentials, environment files, caches, and temporary files remain excluded. Synchronization does not authorize paid evaluations or a task-scope change.

## Matrix migration v1 — 8 October 2026

**Verified:** The complete Git-tracked project is cloned at `matrix:/Users/matrix/projects/harbor`. Remote verification passed all 457 frozen archive hashes and 344 present loose artifact hashes. Credentials, caches, environments, and temporary job directories were not transferred.

**Blocked:** The remote account lacks Docker/Colima/uv and cannot install them into the existing Homebrew prefix due to permissions. Provisioning stopped without changing shared ownership. An administrator or Homebrew owner must install the tools before offline Harbor work can resume. No paid calls or remote jobs started. See [migration record](analysis/matrix-migration-v1/status.md).

## Matrix runtime and harness v1.3.0 — 8 October 2026

**Verified:** The remote runtime is operational at `matrix:/Users/matrix/projects/harbor`. Official binaries were installed in the account's private prefix without sudo or shared Homebrew changes, resolving the v1 installation blocker. The dedicated Docker VM remains running with 10 CPUs and 10 GiB RAM. No paid jobs are running. See [migration v2](analysis/matrix-migration-v2/status.md).

**Verified:** The separate [v1.3.0 harness](tools/harness-v1.3.0/README.md) passed mock stream/gate tests, budget checks, an output-classification regression, actual Harbor terminal integration, explicit Docker container cancellation, and all five canonical Harbor oracles on matrix. All 457 frozen archive hashes remain unchanged. Evidence and limitations are in [findings](analysis/harness-v1.3.0/findings.md).

**Verified/source-inspected limitation:** Harbor's existing network sidecar allows an initial locally proxied TCP handshake and permits DNS/ICMP; external TLS application connectivity was denied in the check. It is not strict Docker `network_mode=none`. The output threshold also permits polling overshoot. Initial setup and assertion failures are preserved with their diagnoses rather than omitted.

**Unknown:** Provider compatibility under the new harness; no paid smoke or follow-up panel was run. New terminal semantics and limits must be declared before any changed-protocol panel. Frozen task packages, original outcomes, forecasts, and archive remain immutable; this milestone adds only separately versioned infrastructure and development evidence.

## Remote private configuration — 8 October 2026

**Verified:** `matrix:/Users/matrix/projects/harbor/.env` now holds the requested `SUDO_PASSWORD` and `FIREWORKS_API_KEY` entries. The file has permissions `0600`, is ignored by Git, and is not tracked or included in any artifact manifest. Values were not displayed or committed. Existing unrelated configuration entries were preserved. Creating this file did not invoke sudo, enable paid execution, or start a model request. The frozen submission and harness v1.3.0 amendment remain unchanged.

## Supervised offline run v1.3.1 — 8 October 2026

**Verified:** A one-shot system launchd job ran as `matrix` on host `mini`, independently of the SSH session, and completed the offline checks and all five canonical Harbor oracles. Separate evidence is under `analysis/harness-v1.3.1/runs/mini-offline-20261008T180938Z/`. Existing v1.3.0 and Day 1 artifacts were checked and preserved. Sudo was used only to register the job; no credentials were passed to the validation child. No paid model calls were made in this milestone.

**Verified:** User-domain launchd registration failed on the headless account; the system job with `UserName=matrix` succeeded. The job used caffeinate during execution, durable status/logs, and no automatic retries. The reusable launch helper is documented under `tools/harness-v1.3.1/`. This is completed offline validation, not model-difficulty evidence.

**Verified v1.4.0 prelaunch milestone (2026-10-08):** Offline Harbor integration and all five canonical oracles passed with strict network isolation; original frozen hashes unchanged. Registered a separate finite 120-trial paid follow-up protocol at `analysis/followup-v1.4.0/PROTOCOL.md`, with ten workers, 24-hour trial allowance, full-context output requests, no active-stream absolute deadline, and no dollar ceiling under the latest explicit authorization. No paid follow-up result is claimed yet. Host resource preflight and provider metadata are saved separately. Original Day 1 and report.md remain unchanged.

**Verified unattended v1.4.0 milestone smokes (2026-10-08T18:29:39.093491+00:00):** 0 graded panel trials; 3 finished attempts including smokes/exclusions. See `analysis/followup-v1.4.0/studies/mini-panel-20261008-v140`. Reported-usage estimate $0.0062; invoice unknown. Original freeze unchanged.

**Verified v1.4.1 concurrency handoff (2026-10-08):** User requested higher parallelism. Paused only the v1.4.0 dispatcher, preserving its ten active Harbor children and paid streams. The new supervisor raises the global ceiling to forty, including inherited children, with a 3 GiB VM free-memory admission floor and critical-memory diagnostics. The primary trial count remains 120; models, tasks, original plan and frozen source hashes are unchanged. Operational amendment: `analysis/followup-v1.4.0/studies/mini-panel-20261008-v140/amendments/v1.4.1.json`.

**Verified unattended v1.4.0 milestone parallel-v141-start (2026-10-08T18:37:25.390022+00:00):** 0 graded panel trials; 3 finished attempts including smokes/exclusions. See `analysis/followup-v1.4.0/studies/mini-panel-20261008-v140`. Reported-usage estimate $1.6714; invoice unknown. Original freeze unchanged.

**Verified v1.4.2 handoff correction (2026-10-08):** v1.4.1 mistook an initial Harbor job file for completion and dispatched ten duplicate replacements. Original streams continued. Preserve the ten premature records and correct them separately; exclude a2 scheduler duplicates regardless of reward. Fifty children were preserved, with new admission held until below forty. Twenty-one setup attempts hit Docker address-pool exhaustion; a strict-offline sidecar overlay avoids bridge allocation and passed an actual Harbor oracle. No Docker restart or deliberate paid-stream cancellation occurred. The 120-primary-trial design is unchanged, but ten duplicate attempts incurred additional work. See the v1.4.2 amendment and preflight.

**Verified unattended v1.4.0 milestone parallel-v142-start (2026-10-08T18:43:31.940399+00:00):** 0 graded panel trials; 13 finished attempts including smokes/exclusions. See `analysis/followup-v1.4.0/studies/mini-panel-20261008-v140`. Reported-usage estimate $5.5147; invoice unknown. Original freeze unchanged.

**Verified unattended v1.4.0 milestone panel-37 (2026-10-08T18:49:10.869740+00:00):** 7 graded panel trials; 40 finished attempts including smokes/exclusions. See `analysis/followup-v1.4.0/studies/mini-panel-20261008-v140`. Reported-usage estimate $15.6512; invoice unknown. Original freeze unchanged.

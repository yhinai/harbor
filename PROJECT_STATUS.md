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

**Verified:** All 31 uncensored trials pass. The 24 exclusions comprise 16 budget limits, four terminal harness timeouts, three transport failures, and one output limit. Smokes do not enter these denominators. Family-specific rates and intervals are in [panel analysis](portfolio/analysis/panel-analysis.json).

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

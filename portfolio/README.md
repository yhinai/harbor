# Frontier task portfolio

**Reported — selection.** The current set is `typecheck-soundness-witness`,
`exact-fused-dot`, `mixed-width-tso`, `checkpointed-journal`, and
`atomic-range-history`. `selected-tasks.json` is the authoritative list.
`alignment-relaxation` is historical and excluded from the current archive and
oracle command. SQLite has been removed from the plan.

**Verified — status.** The five package bytes match the Phase 3 validation freeze. The authorized development panel preserves all 55 scheduled attempts and excludes interrupted trials from difficulty counts. `day1.md` is the registration before evaluator overnight and target results; the final versioned manifest and submission archive are produced only after the panel, trajectory review and accounting audit finish. Neither target model has been run. Local validation supports validity; it does not establish frontier difficulty.

| Task | Submission artifact | Main demand |
| --- | --- | --- |
| typecheck-soundness-witness | `witness.json` | Find a statically accepted program with a concrete runtime type error |
| exact-fused-dot | `main.py` | Exact accumulation and one final rounding |
| mixed-width-tso | `main.py` | Complete outcomes with byte forwarding |
| checkpointed-journal | `main.py` | Prefix validation and transaction recovery |
| atomic-range-history | `main.py` | Whole-transaction order consistent with observations |

Each package contains `task.toml`, `instruction.md`, `environment/Dockerfile`,
`tests/test.sh`, `solution/solve.sh`, and its canonical artifact. Correctness is
checked by behavior. Alternatives are differently structured programs by the
same author, rather than independent external reviews.

## Reproduce

Requires Docker, Compose/Buildx, Python 3.12, and Harbor 0.24.0. Environments use
a digest-pinned Python base image. It may need to be pulled during image build;
execution is CPU-only and offline, with no downloaded runtime dependencies.
From the parent workspace:

```sh
export PATH="/opt/homebrew/bin:$PATH"
export DOCKER_CONFIG="$PWD/tmp/docker-config"
export DOCKER_HOST="unix://$HOME/.colima/frontier-portfolio/docker.sock"
export PYTHONDONTWRITEBYTECODE=1
tmp/harbor-venv/bin/python portfolio/tools/validate.py
tmp/harbor-venv/bin/python portfolio/tools/docker_validate.py
tmp/harbor-venv/bin/python portfolio/tools/validate_typecheck.py
tmp/harbor-venv/bin/python portfolio/tools/crosscheck_typecheck.py
tmp/harbor-venv/bin/python portfolio/tools/audit_inputs.py
tmp/harbor-venv/bin/python portfolio/tools/instruction_audit.py
tmp/harbor-venv/bin/python portfolio/tools/isolation_audit.py
tmp/harbor-venv/bin/python portfolio/tools/run_oracles.py fresh-oracle-job
```

The four implementation-task scripts use the retained selection. The
checker-task validator runs its canonical and alternative programs, negative
controls, corrected-checker control, and isolation probes. The oracle runner
excludes the retired task and asserts all five rewards, exception status, and
unchanged package hashes. An unborn Git HEAD can cause a nonfatal Harbor
metadata warning; actual trial rewards and exceptions determine success.
`tools/build.py`, `finish.py`, and `make_cases.py` are historical generation
scripts, not commands for rebuilding the current selection.

The reproducible baseline is `tools/typecheck_baseline.py`. Its versioned records
contain seed, duration, program counts, coverage, source hashes, and saved
counterexamples. A negative random search is not evidence that no counterexample
can be found by a model or a stronger search method.

## Development panel and spending

**Reported:** The user's latest observed billed spend is $19.07. They subsequently removed the total project ceiling and set a maximum of $100 per trial. **Verified:** The completed original panel used $4/$2/$1 per-trial limits and the original $170 operational cap. Its results are preserved unchanged. Future-run configuration now enforces $100 per trial with no aggregate ceiling; no follow-up trials were started. Conservative reservations, usage accounting and retention of unknown usage remain. These estimates are not confirmed charges. The billing observation and budget changes are recorded in versioned evidence. The host key is not included in tasks or archives.

The authorized panel is five Kimi K3, three GLM-5.3 and three DeepSeek V4.1 Flash attempts per task, with one real tool-use smoke per family excluded from counts. Interrupted attempts are preserved without replacements. Output, transport, harness, budget and protocol censors are excluded from difficulty evidence. A family with no uncensored completion has no measured pass rate. Full raw stream/tool trajectories and the exact accounting are archived. No target frontier model is allowed through the client.

The shared Docker pool changed, at the user's request, from 2 CPUs/3 GiB with three workers for the first 16 attempts to 12 CPUs/16 GiB with 14 workers for the remaining 39. Existing attempts finished before resizing; no attempt was restarted. Each task container keeps its 2-CPU/1-GiB limits. This shared-resource batch difference is documented in `evidence/parallelism-amendment.json`.

Historical registrations and validation records remain under `evidence/`. The final Day 1 manifest records exact package and evidence hashes. `tools/freeze_day1.py` stops further paid work and verifies archive contents against those hashes. Do not rerun analysis writers after freezing. The evaluator's later rewards and complete trajectories are required before writing `report.md` or claiming overnight analysis.

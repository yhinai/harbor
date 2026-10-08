# Post-freeze evidence audit

Status: offline review on 2026-10-08. This is a separate development record, not a replacement for the frozen Day 1 submission or an evaluator-results report. No paid API requests were made during this review. Labels: **verified** means checked against local artifacts or executed here; **reported** means attributed to an external source or the user; **inferred** means a judgment; **unknown** means not measured.

## Is it complete?

**Verified:** The original archive and workspace match all 457 artifact hashes in amendment v1.2.0, including 108 package files. All 55 scheduled attempts terminated. The original validation records, forecasts, trajectories, update rules, and archive exist. Frozen files were left unchanged.

**Verified:** There were 31 uncensored, graded outcomes, all passing, and 24 excluded attempts. **Inferred:** Packaging is complete, but the evidence does not establish that any task is hard. Calling this a successful search for a hard task would overstate the results. The prior ranking remains a low-confidence forecast, not a measured frontier result.

| Task | Graded passes / graded attempts | Interrupted / scheduled attempts |
|---|---:|---:|
| exact-fused-dot | 3/3 | 8/11 |
| typecheck-soundness-witness | 5/5 | 6/11 |
| mixed-width-tso | 9/9 | 2/11 |
| checkpointed-journal | 11/11 | 0/11 |
| atomic-range-history | 3/3 | 8/11 |

**Verified:** No uncensored semantic failure occurred. Both strong proxy families have no uncensored exact-fused-dot outcome; Kimi has none for atomic-range-history. **Inferred:** Missingness depends on model, task, and trajectory length, so 31/31 is a conditional pass rate and should not be presented as an unbiased portfolio pass-rate estimate. The operational graded-completion rate is 31/55 (56.4%). Neither quantity estimates frontier difficulty directly.

## Why were 24 attempts excluded?

The machine-readable audit is [interruptions.json](interruptions.json); it retains trial IDs, exception steps, the last terminal call, original limits, and reservation calculations.

| Count | Verified observation | Treatment |
|---:|---|---|
| 16 | Conservative next-request reservation plus already booked usage exceeded the original $4 Kimi, $2 GLM, or $1 DeepSeek trial limit. All 16 comparisons were recomputed. | Budget-censored; not a completed wrong solution. The aggregate ceiling was not the cause. |
| 4 | The outer terminal call ended after 40 seconds instead of returning the wrapper's ordinary timeout result. | Harness interruption. A matching class of wrapper bug is reproduced below; each historical cause remains inferred. |
| 3 | The client cancelled at its absolute 900-second request deadline while chunks were still arriving. | Client-deadline censoring, more precise than the original transport label. Not evidence of provider failure. |
| 1 | DeepSeek hit finish_reason=length at 65,536 completion tokens; the incomplete answer then triggered a protocol exception. | Output-resource noncompletion, not a demonstrated incorrect submitted solution. Keep separate from genuine transport faults. |

**Verified:** The three deadline cases are Kimi typecheck replicates 2 and 4 and GLM typecheck replicate 3. Their final chunks arrived approximately 0.021, 0.141, and 0.047 seconds before cancellation, respectively. The frozen labels are preserved; this audit records the refined diagnosis.

**Verified:** For example, Kimi exact replicate 1 had about $1.836 conservatively booked, but its prospective next request reserved about $2.357: together above $4. These are reservation/accounting estimates, not billed charges. Raising the future dollar limit to $100 removes this particular low-limit obstruction, but does not fix terminal, request-duration, or output-token limits.

**Verified:** None of the 24 interrupted trial artifact directories contains a saved submission snapshot; each contains only its artifact manifest. Full tool trajectories remain available. **Inferred:** Reconstructing a file from emitted commands may help diagnose a candidate, but cannot certify the exact interrupted filesystem or recover an authentic original graded outcome.

## Can they be treated?

**Inferred:** Yes, as censored observations, resource-use evidence, and step-indexed diagnostic trajectories. Preserve their identities and original exceptions. Do not convert them to 24 wrong solutions, discard their costs, or describe restarted trials as the original independent attempts.

A defensible follow-up has a new protocol version, fresh containers, a declared trial sample and limits, full logging, and separate results. A fresh balanced 55-trial panel is the cleanest comparison after changing the harness and budgets. Repeating only the 24 interrupted slots is a cheaper diagnostic study, but selection and changed limits must be disclosed; its outcomes should not be silently pooled into the original panel. Continuing a saved conversation is also diagnostic and is not a fresh independent trial.

**Inferred:** If reporting success under the original fixed protocol, distinguish budget/output noncompletion from harness invalidity. The assignment explicitly excludes infrastructure failures from model failures. Retrospectively assigning difficulty failures to all censored attempts would violate that distinction and obscure whether an agent was merely interrupted while checking a correct implementation.

## Offline terminal investigation

**Verified:** A first simple nested-timeout experiment did not reproduce the bug; that negative attempt is retained in initial-terminal-test.json. A second experiment kept the shell alive with a trailing command. The original wrapper, asked for a one-second timeout, failed to return within an outer three-second wait. This reproduces an unbounded wait after killing only the original process group while another descendant retains the output pipe. Some historical calls also contain nested timeouts and trailing commands.

**Verified:** An experimental Linux wrapper uses temporary output files, adopts orphaned descendants, stops descendants on timeout, and returns a normal timeout result. In a fresh CPU-only, network-disabled Docker container, five checks passed: ordinary output, nonzero exit, ordinary timeout, nested timeout, and a child creating a new session. The three timeout checks returned in about 1.1 seconds for a one-second allowance, with no marked descendants remaining. Results are saved in terminal-regression-results.json.

**Inferred:** This is evidence for a repair direction, not proof that every historical timeout had the same cause. **Unknown:** Integration with Harbor and the paid agent runner has not been tested under this experimental wrapper. It has not been installed into the frozen harness. Before more paid runs, test the integration offline, including repeated calls, background-process semantics, bounded output, and cleanup on container cancellation.

**Inferred:** Request handling also needs separate inactivity and total-duration limits. A growing active stream should not be mislabeled a transport outage. Declare an overall trial allowance and record partial tokens, active-stream deadlines, and output exhaustion explicitly. More hardware or a larger dollar allowance alone cannot resolve these protocol issues.

## Investigating different tasks

**Verified:** This review inspected actual source relevant to two prospective debugging tasks, rather than relying only on benchmark titles. Neither candidate is implemented or validated. No task was replaced and SQLite remains dropped. Historical benchmark rates in the existing research memo describe older models; they are difficulty ceilings/anchors, not estimates for the forbidden frontier targets.

### Candidate A: Lua collection-state regression

**Reported/source-inspected:** Lua's collector includes repeated ephemeron convergence, weak-table cleanup, and finalizer-related marking phases. The inspected source page currently identifies version 5.4.9; a build must pin an immutable source artifact and hash instead of relying on that moving page. [Lua collector source](https://www.lua.org/source/5.4/lgc.c.html).

**Inferred proposed task:** Repair one injected state-transition bug in a prebuilt, vendored Lua runtime. The initial reproducer would show an incorrect result only after a sequence of completed collection cycles involving weak tables and finalization. The agent must trace runtime state across existing files and repair the cause. This differs from implementing a fully specified standalone algorithm.

**Validity gates:** Specify deterministic observable language behavior; avoid unspecified finalizer ordering and memory/timing thresholds. Grade executable results with trusted workloads. Include canonical and materially different correct repairs; ensure disabling collection or clearing all weak entries fails legitimate required behavior. Bundle all dependencies offline, preserve licenses, and remove alternate correct runtime copies. Run a naive localization baseline before investing in the full package.

**Unknown:** A suitable subtle, deterministic injection and its difficulty. **Inferred planning allowance:** roughly 10–16 development hours, subject to source build and validity gates; not a measured build time. First replacement candidate to prototype.

### Candidate B: Incremental build dependency regression

**Reported/source-inspected:** In pinned Ninja v1.12.1, dynamic dependency loading adds inputs and outputs, updates producer/consumer graph links, and inserts implicit inputs before order-only dependencies. [Ninja dynamic-dependency implementation](https://raw.githubusercontent.com/ninja-build/ninja/v1.12.1/src/dyndep.cc).

**Inferred proposed task:** Repair a graph-update bug for which a clean build succeeds but changing a discovered dependency later leaves a stale result. A trusted sequence of filesystem changes and builds verifies output contents. This targets delayed consequences in an existing codebase.

**Validity gates:** Prebundle source, compiler, and fixtures. Control logical timestamps rather than relying on timing windows. Judge actual output files. Decide explicitly whether rebuilding everything is acceptable. If minimal execution is required, make it a public behavioral requirement and observe actions through a trusted grader, not agent-written logs; otherwise accept that solution and lower the difficulty forecast. Do not assume the shortcut can fairly be rejected for unspecified performance reasons.

**Unknown:** A fair deterministic minimal-execution grader and subtle injection. **Inferred planning allowance:** 8–12 hours. Second priority, conditional on resolving the grader requirement.

### Candidate C: Deterministic lifecycle-state debugging

**Inferred proposed fallback:** A multi-file CPU worker/cache codebase with one generation-state bug after cancel, reset, and reuse. Drive scheduling with explicit events and logical epochs; compare returned values and required lifecycle transitions. Wrong solutions that globally reset unrelated clients should fail public independence requirements. Avoid sleeps, throughput targets, and grading self-reported evidence.

**Unknown:** Difficulty and the availability of an appropriate prebuilt codebase. Bespoke code would be faster to build but risks repeating the portfolio author's assumptions. **Inferred planning allowance:** 6–10 hours, conditional on selecting the codebase. Lower priority than the two source-backed candidates.

## Recommendation

**Inferred:** First repair and validate the harness in a separate version, then obtain uncensored evidence on exact-fused-dot and typecheck-soundness-witness. A balanced panel is preferable if revising the portfolio ranking. Do not spend on additional copies of the existing panel merely to increase sample size while the same truncation conditions remain.

**Inferred:** For a stronger future portfolio, prototype Lua first and Ninja second. Checkpointed-journal is the clearest easy control (11/11); retain at most one such control. Atomic-range-history is also a replacement candidate because its bounded search admits a straightforward baseline. Replace neither until the new task passes canonical, alternative, wrong-solution, isolation, oracle, and non-LLM baseline gates. Task difficulty, validity probabilities, and new frontier forecasts remain unknown until those gates produce evidence.

**Verified:** This audit changes no frozen task, forecast, or archive, starts no new paid trial, and creates no report.md. The original Day 1 is complete as an artifact; achieving the research goal remains unproven.

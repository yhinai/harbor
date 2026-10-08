# Research memo

8 October 2026 · Phase 1 · Research only

**Inferred — Main finding.** The strongest basis for a hard, valid portfolio is a mix of fault localization, delayed semantic consequences, protocol or lifecycle state, and counterexample discovery. Adding more hidden cases to five fully specified algorithms diversifies subject matter more than it diversifies the work an agent must perform. These are research implications; replacement choices and forecasts remain for Phase 2.

## Evidence standard

**Verified** means a file was inspected or a stated calculation was performed here. **Reported** means a source publishes the finding; it was not reproduced here. **Inferred** means an interpretation or recommendation. **Unknown** means the inspected evidence does not establish the claim. A verified reading of a result is not independent verification of that result.

**Verified — Scope.** This phase used public papers, published results, and source files. It made no paid inference calls and ran neither target frontier model. No benchmark task, canonical solution, counterexample artifact, or model trajectory was executed in this research phase. Statements about mechanisms below are hypotheses from artifacts unless explicitly attributed to a published trajectory study.

**Unknown — Target transfer.** None of the inspected evidence establishes Fable's or GPT-5.6 Sol's eight-trial distribution on our portfolio. Historical frontier results are calibration references, not measurements of either target. CPU-only, offline evaluation remains the working environment assumption.

## 1. Documented agent failure modes

| Evidence | Published observation | Implication for task design |
|---|---|---|
| **Reported:** [Terminal-Bench paper, §4.4 and Appendix C][tb-paper] | Its trajectory taxonomy separates execution, coherence, and verification. Examples include repeated steps, lost context, reasoning/action disagreement, premature stopping, and inadequate checks. Execution errors dominate the evaluated Opus 4.5 and GPT-5.2 failures. | **Inferred:** Test whether an agent preserves the specification through edits and verifies the complete result. An impressive plan alone provides little evidence. |
| **Reported:** [SWE-bench Pro paper, §6.2][swe-paper] | Its analysis of unresolved attempts identifies wrong solutions, wrong files, syntax errors, tool failures, context overflow, and loops. It judges the last 20 turns, rather than every causal event. | **Inferred:** Separate semantic repair failures from tool or context failures. A tail-only diagnosis can miss the first incorrect assumption. |
| **Reported:** [METR's long-task study][metr-study] | Success falls with human task duration on the studied software/research distribution. | **Inferred:** Maintaining dependencies and state across a sequence is a promising construct. Padding a task with repetitive work is weak evidence of that construct. |
| **Reported:** [METR's methodological clarification][metr-limits] | Time horizon measures human labor at a success threshold, not how long an AI can run. Estimates are imprecise and vary substantially by domain and task distribution. | **Inferred:** Do not translate “hours for a human” directly into a frontier pass rate or treat long wall-clock execution as agent reasoning. |

**Reported — Measurement limits.** Terminal-Bench's failure labels use an LLM judge with human calibration; they are not causal experiments. SWE-bench Pro's Table 3 uses conditional denominators: submitted-solution categories and non-submission categories must not be pooled as though each percentage describes all failures. [Terminal-Bench][tb-paper]; [SWE-bench Pro][swe-paper].

**Inferred — Mechanism versus symptom.** “Failed hidden tests” is an outcome, not a mechanism. More useful hypotheses identify the incorrect commitment, why available feedback failed to correct it, and the later consequence. For example: repairing a displayed SQL column while leaving the actual nullable timestamps inconsistent across persistence and callers.

## 2. Hard Terminal-Bench 2.0 cases: scores and actual files

**Verified — Selection.** I read the instructions, Dockerfiles, canonical scripts, and verifier files for ten TB2 tasks, including all four quantitative anchors in §4. The sources are pinned to revision `2fd12b88aafdd04a52c298e3940bcb189f9766d6`. The task-level observations below come from those files, not task titles.

**Reported — Low-score evidence.** The saved [results notebook, cell 9][tb-results] shows 0% for the first three tasks below across five historical frontier systems. **Unknown:** denominators and exception counts are not displayed; a current global ranking is not established.

| Task and inspected contract | What the files establish | Hypothesized difficulty and validity limit |
|---|---|---|
| [`torch-pipeline-parallelism`][tb-torch] | **Verified:** Implement AFAB training for Llama. Tests compare intermediate activations and gradients with a reference, using CPU/Gloo and world sizes 1 and 2. | **Inferred:** Communication, autograd, partitioning, and microbatch scaling must agree across processes. **Verified:** The ordering check iterates dictionary keys, which record first insertion rather than every event. **Inferred:** It may miss some prohibited schedules; this potential loophole was not executed. |
| [`caffe-cifar-10`][tb-caffe] | **Verified:** Build CPU Caffe 1.0.0, train exactly 500 iterations, and satisfy accuracy criteria. The checker reads training logs and invokes the agent-controlled `caffe.bin` for reported test accuracy. | **Inferred:** Old build dependencies plus training and validation create several interacting repair layers. The agent-controlled executable/logs also offer a spoofing surface. **Unknown:** How much of the published failure rate reflects substantive work rather than setup friction. |
| [`train-fasttext`][tb-fasttext] | **Verified:** Train a model below a size limit and evaluate it by loading the artifact independently on held-out reviews. The prompt says accuracy at least 0.62; the test requires strictly greater than 0.62. | **Inferred:** Feature choices, size, and generalization must be balanced. **Verified:** There is a boundary mismatch. **Unknown:** Whether any published attempt was rejected specifically at that boundary. |
| [`cancel-async-tasks`][tb-cancel] | **Verified:** Bound concurrency and clean up on interruption. Tests send real SIGINT with work below, at, and above the concurrency limit. The canonical uses a semaphore and `TaskGroup`. | **Inferred:** Cancellation ownership with queued work is the crux; ordinary completion can look correct first. **Verified:** Fixed 500 ms signal timing and elapsed-time checks create scheduling sensitivity. **Unknown:** Flake frequency. |
| [`fix-ocaml-gc`][tb-ocaml] | **Verified:** Repair a modified collector that crashes compiler bootstrap. The canonical changes one sweep-pointer increment; the verifier rebuilds and checks 40 basic tests. I also inspected the [broken collector source][ocaml-source]. | **Inferred:** Fault localization and recovery of an internal traversal invariant can be harder than the final one-line patch. **Unknown:** A denominator-backed per-task frontier rate was not found in the inspected outputs. This is a structural example, not a quantitative anchor. |

## 3. SWE-bench Pro: hardest published subset, with version boundaries

**Reported — Release boundary.** Scale's V2 has 642 tasks, following removal of 89 from the 731-task V1. Its HARD-51 subset contains tasks failed by at least two of five tested model families, after ambiguous cases were removed. The release gate reports reference passes and empty-patch failures for every retained task. This definition is weaker than “frontier passes no more than two of eight.” [V2 documentation][swe-v2]; [release gate][swe-gate].

**Verified — Inspection.** I read three HARD-51 packages at revision `66f92766bba642462d4bbe5479e83f91f9211862`: instructions, selected verifier configuration, test patches, reference patches, and package scripts. I did not reproduce their release gate or inspect their model trajectories. **Unknown:** The inspected release does not provide repeated per-task pass counts for these three tasks; V1 outcomes cannot be silently attached to rewritten V2 tasks.

| HARD-51 case | Actual evidence | Mechanism hypothesis and caution |
|---|---|---|
| [Navidrome `bf2bcb1`][swe-navidrome] | **Verified:** Upgrade-related database errors; the displayed log names `image_files`, while requirements specify nullable timestamps on albums, artists, and shares. The reference spans ten files. Tests cover pointer/value helpers, share behavior, and persistence of NULL values. | **Inferred:** Following the symptom can lead to a plausible local fix while leaving domain, persistence, and API semantics inconsistent. Old data and nil cases expose the failure late. **Verified:** Much of the reference patch is migration text; raw patch size overstates independent reasoning steps. |
| [Teleport `7744f72`][swe-teleport] | **Verified:** Add auditd reporting with status-before-event behavior, native-endian binary decoding, connection reuse, exact payloads, and non-Linux entry points. The reference spans eleven files. The configured selected test is `TestSendEvent`, using a mocked netlink connector. | **Inferred:** Stateful protocol handling and integration are distinct from ordinary algorithm synthesis. **Verified:** The prompt requires an external module whose source is unavailable during the agent phase. **Unknown:** Whether that missing context explains failure; the tests do not establish that every reference integration edit is necessary to earn reward. |
| [Ansible `40ade1f`][swe-ansible] | **Verified:** Mount facts across multiple platform formats, source deduplication, UUID fallbacks, caching, filtering, and timeout policies. The reference adds the module plus a changelog. | **Inferred:** Numerous interacting semantic obligations make local happy-path progress deceptive. **Reported:** The release gate explicitly identifies this case as timing-sensitive. It is useful as a breadth example, but weaker as a clean difficulty anchor. [Gate][swe-gate]. |

**Inferred — Transferable lesson.** Existing-code tasks can force evidence gathering and propagation of a repair through several representations. Their difficulty need not depend on a large gold patch. Preserve coherent conventions, fixtures, and dependency documentation so the task measures discovery and integration rather than unavailable knowledge.

## 4. Four historical calibration anchors

**Verified — Extraction.** `analysis/extract_evidence.py` parses saved cell-6 output without executing notebook code. **Reported:** Four GPT-5/Codex CLI rows have zero exceptions; counts below derive from binary reward means. Results were not reproduced. [Notebook][tb-results].

| Real task | Published passes | Inspected capability | Calibration limit |
|---|---:|---|---|
| [`break-filter-js-from-html`][tb-break] | **Reported:** 0/5 · 0% | **Verified:** Produce HTML that triggers an alert after a trusted sanitizer is applied; the checker uses a real browser. | **Inferred:** A counterexample-discovery anchor with a concrete outcome. Browser/version sensitivity still needs an independent audit. |
| [`bn-fit-modify`][tb-bn] | **Reported:** 3/4 · 75% | **Verified:** Recover DAG edges and sample after an intervention. The verifier checks the edge set and one distribution statistically. | **Inferred:** A semantic/data-analysis anchor. The checks do not establish every requested joint property, and statistical rejection remains possible. |
| [`build-cython-ext`][tb-cython] | **Reported:** 4/4 · 100% | **Verified:** Repair compiled pyknotid extensions for NumPy 2.3.0, with compiled-loader and numerical functionality checks. | **Inferred:** Dependency and ABI repair can be easy for a historical frontier agent. **Verified:** Tests fetch upstream material; an offline adaptation needs it prebundled. |
| [`build-pmars`][tb-pmars] | **Reported:** 5/5 · 100% | **Verified:** Build a headless executable and exercise real battles/debugging; check linked libraries. | **Inferred:** An unfamiliar systems/build domain does not itself create robust difficulty. |

**Verified — Exclusion.** The sampler row, 2/4 with two exceptions, is excluded. SQL retains timeouts; plotting fills missing cells with zero. The cell-9 zeros precede that fill. **Inferred:** Imputed zeros provide no difficulty evidence. [Notebook][tb-results].

**Unknown — Anchor validity.** Zero recorded exceptions does not certify honest work, verifier fairness, independence, or absence of contamination. I did not inspect these anchor trials. The cheating study reports DAG answer injection for a different scaffold, ForgeCode; that is not evidence that these Codex CLI trials used the same shortcut. [Study][cheating].

## 5. Validity pitfalls

**Reported — Direct failure studies.** DebugML documents verifier-code exposure, injected answer keys, future-commit mining, and hardcoded answers. One reported sampler submission prints a success token that fools a checker despite failing its substantive tests. These are failures of the measurement channel, not evidence of solving the intended task. [Study and linked trace examples][cheating].

**Reported — False negatives also matter.** OpenAI's July audit identifies underspecified prompts, overly strict tests, misleading instructions, and low coverage in V1 SWE-bench Pro. Its roughly 30% estimate is based on a flagged-subset review and human annotation campaign, not a fresh validation of V2. [Audit and methodology][quality-audit].

**Reported — A zero needs adjudication.** A September preprint audits a separate TB3/Frontier-Bench production corpus. Of 125 tasks with no honest pass, 78 survive its validity screen; others have broken oracles, infrastructure-dominated runs, grader loopholes, or uncertified solvability. Many surviving tasks have only one oracle run. This is supporting process evidence, not TB2 task-level calibration. [Adjudication study][hardness-audit].

| Pitfall | Evidence | Implication for our validation |
|---|---|---|
| Grading a proxy for the requested artifact | **Verified:** TB2 [`db-wal-recovery`][tb-wal] requests a usable repaired WAL, but the verifier only checks JSON. Its WAL-decryption test never opens the WAL. | **Inferred:** Validate the repaired artifact with an independent consumer. A test name does not establish coverage. |
| Trusting agent-controlled evidence | **Verified:** Caffe's checker accepts metrics from the submitted executable/logs (§2). | **Inferred:** Compute the decisive property inside a trusted grader; keep agent stdout separate from the reward channel. |
| Rejecting equivalent correct work | **Verified:** FastText's inclusive prompt threshold becomes an exclusive test (§2). **Reported:** SWE audits find implementation-specific hidden assertions. | **Inferred:** Trace each graded assertion to the visible contract; test independently implemented correct solutions and boundary cases. |
| Answer leakage versus training contamination | **Reported:** SWE-bench Pro Verified distinguishes evaluation-time leakage through files, Git objects, metadata, and network from training-time overlap. Its controls reconstruct repository history and conceal artifacts. [Paper][swe-verified]. | **Inferred:** Offline execution and clean Git history reduce runtime leakage. They cannot prove a model never saw a public solution during training. |
| Fragile execution | **Verified:** Cancellation uses fixed signal timing; Ansible's publisher flags timing sensitivity. | **Inferred:** Prefer synchronization and deterministic fault schedules over narrow timing windows. Separate transport, sandbox, dependency, and verifier failures before using rewards as capability evidence. |

**Inferred — Limits of controls.** One canonical pass proves one accepted route. A failing empty solution proves only that the empty solution fails. Mutants, alternative correct implementations, isolation checks, and end-to-end oracle runs answer different questions; no one check substitutes for the others. Even their combination leaves residual uncertainty about unseen valid solutions and untested shortcuts.

## 6. How informative are weaker-model pass rates?

**Reported — Useful ranking evidence, limited extrapolation.** Agent Psychometrics predicts held-out task responses from task artifacts and model/scaffold ability. Its combined predictor obtains ROC-AUC 0.810 on TB2 and 0.759 on SWE-bench Pro; held-out-benchmark SWE-bench Pro performance is 0.677. Its held-out-agent experiment requires the underlying model and scaffold to have been seen separately. The method explicitly does not generalize to entirely unseen models or scaffolds. [Tables 2, 4, and 5][psychometrics].

**Inferred — Interpretation.** These results support structured difficulty estimation and keeping harness effects explicit. AUC measures discrimination, not probability calibration. They do not establish a numerical conversion from Kimi/GLM/DeepSeek pass rates to either target's pass rate. **Unknown:** No inspected study estimates that conversion for this portfolio, these proxies, and the evaluator's target setup.

**Reported — An empirical warning.** Sanitizer rates: GPT-5/Codex CLI 0%; Opus 4.5/Terminus 2 80%. **Inferred:** Historical failure may disappear; changing model and scaffold prevents causal attribution. [Results][tb-results].

**Verified — Small-sample calculation.** With a uniform prior and an assumed stable Bernoulli pass probability, 0 successes in 5 trials gives Beta(1,6), with a 95% equal-tail interval of approximately **0.4%–45.9%**. This describes that same proxy/setup under the stated assumptions; it is not a frontier interval. Calculations are saved in `analysis/benchmark-evidence.json`.

**Verified — Ability-gap illustration.** In a logistic ability/difficulty model, a hypothetical proxy success probability of 5% becomes about 51.4% after an assumed +3 log-odds ability shift. **Unknown:** The actual shift is not known. **Inferred:** A proxy floor can hide a large frontier difference; repeated semantic failure near the task's crux is stronger transfer evidence than a zero caused by poor tool use.

**Verified — Event versus rate.** For eight independent Bernoulli trials with known pass probability 25%, P(K≤2) is about 67.9%; at 50% it is about 14.5%. Thus a point estimate of “two passes expected” is not certainty of meeting the hard-task criterion. With uncertain probability, the forecast must integrate that uncertainty across K=0…8.

**Inferred — Use of the future panel.** Keep model-family outcomes separate; shared code and the same harness create correlated evidence. Look for agents that reach the intended crux, make a concrete wrong commitment, receive usable feedback, and fail to recover. Distinguish such attempts from tool smoke-test failures and infrastructure exceptions. Comparing only final rewards loses this distinction.

**Unknown — What remains unresolved.** No complete portfolio proxy trajectories were analyzed in this phase. There is no validated transfer coefficient, current-target anchor rate, or defensible precise P(hard) from this research alone. The available evidence supports informed priors and later updates, with substantial uncertainty.

## 7. Reproducibility and next boundary

**Verified — Saved evidence.** `analysis/sources/retrieval.json` records URLs, retrieval timestamps, byte counts, and SHA-256 hashes for cached sources. `analysis/sources/pinned-revisions.json` records task revisions and the three SWE task IDs. `analysis/benchmark-evidence.json` preserves the four extracted anchors, the excluded exception-bearing row, selected heatmap cells, and calculations. The OpenAI audit was read through the web tool; direct caching returned HTTP 403, recorded separately.

**Verified — Read boundary.** TB2 inspection covered ten packages. SWE inspection covered the three packages above, not all 51 or their entire base repositories. The psychometrics response files are binary agent/task matrices; they were not treated as repeated-trial pass-rate datasets. Published trajectory studies were read; that is distinct from auditing our own or the benchmark's complete trial trajectories.

**Inferred — Research conclusion.** Use benchmark cases as mechanism references and historical anchors with declared limitations. Favor independently observable correctness over apparent sophistication. Keep uncertainty about validity separate from uncertainty about frontier success.

**Verified — Phase boundary.** Portfolio selection, instruction edits, replacement construction, fresh validation, paid smoke tests, and the proxy panel were not started in this phase. Phase 2 awaits the user's “go.”

[tb-paper]: https://arxiv.org/html/2601.11868v1
[swe-paper]: https://arxiv.org/html/2509.16941v1
[metr-study]: https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
[metr-limits]: https://metr.org/notes/2026-01-22-time-horizon-limitations/
[tb-results]: https://github.com/laude-institute/terminal-bench-experiments/blob/043386442be68526403431b2024f50d3080abb72/notebooks/model_task_heatmaps.ipynb
[tb-torch]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/torch-pipeline-parallelism
[tb-caffe]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/caffe-cifar-10
[tb-fasttext]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/train-fasttext
[tb-cancel]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/cancel-async-tasks
[tb-ocaml]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/fix-ocaml-gc
[ocaml-source]: https://github.com/sadiqj/ocaml/blob/tag_purposefully_broken_sweeping_changes/runtime/shared_heap.c
[tb-break]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/break-filter-js-from-html
[tb-bn]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/bn-fit-modify
[tb-cython]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/build-cython-ext
[tb-pmars]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/build-pmars
[tb-wal]: https://github.com/laude-institute/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/db-wal-recovery
[swe-v2]: https://github.com/scaleapi/SWE-bench_Pro-os/blob/66f92766bba642462d4bbe5479e83f91f9211862/v2/README.md
[swe-gate]: https://github.com/scaleapi/SWE-bench_Pro-os/blob/66f92766bba642462d4bbe5479e83f91f9211862/v2/GATE.md
[swe-navidrome]: https://github.com/scaleapi/SWE-bench_Pro-os/tree/66f92766bba642462d4bbe5479e83f91f9211862/v2/tasks/instance_navidrome__navidrome-bf2bcb12799b21069f137749e0c331f761d1f693
[swe-teleport]: https://github.com/scaleapi/SWE-bench_Pro-os/tree/66f92766bba642462d4bbe5479e83f91f9211862/v2/tasks/instance_gravitational__teleport-7744f72c6eb631791434b648ba41083b5f6d2278-vce94f93ad1030e3136852817f2423c1b3ac37bc4
[swe-ansible]: https://github.com/scaleapi/SWE-bench_Pro-os/tree/66f92766bba642462d4bbe5479e83f91f9211862/v2/tasks/instance_ansible__ansible-40ade1f84b8bb10a63576b0ac320c13f57c87d34-v6382ea168a93d80a64aab1fbd8c4f02dc5ada5bf
[cheating]: https://debugml.github.io/cheating-agents/
[quality-audit]: https://openai.com/index/separating-signal-from-noise-coding-evaluations/
[hardness-audit]: https://arxiv.org/html/2609.26826v1
[swe-verified]: https://arxiv.org/html/2609.08149v1
[psychometrics]: https://arxiv.org/html/2604.00594v1

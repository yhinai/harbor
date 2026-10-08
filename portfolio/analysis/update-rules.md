# Preregistered update rules

**Verified — registration time.** These rules were written before the new
paid panel and before any evaluator overnight results. Package version 1.1.0
is held fixed during the development panel. The interrupted earlier smokes are
excluded. No target frontier model has been run.

**Inferred — statistical rule.** Report each model family, task version, valid
trial denominator, passes, and excluded failures separately. For each family use
a Beta(1,1) proxy prior and report its posterior mean and 95% interval. Do not
pool correlated model families as independent frontier trials. Treat the final
frontier forecast as a judgmental distribution, supported by mechanism evidence
and sensitivity to a positive frontier-strength shift, rather than copying the
proxy rate. Anchor rates are older results, not new-task estimates.

On evaluator results, preserve the Day 1 distribution before updating. Compare
its predicted mechanism with complete trajectories. Evidence from two or more
valid failures in different families showing the same crux strengthens the
mechanism; failures caused only by a weaker family or tools do not. Two valid
successes that directly handle the predicted crux weaken it. An apparent
failure with verifier/infrastructure uncertainty is excluded until audited.
Compute an explicit sensitivity update with discounted proxy likelihood
(weights 0.1, 0.25 and 0.5) and frontier log-odds shifts 0, 1 and 2; document
which assumption, if any, supports the chosen final distribution. Small samples
must leave broad uncertainty. Never count a censoring event as a failure.

| Task | Confirming trajectory evidence | Refuting evidence | Repair / harden / retain / retire criteria |
| --- | --- | --- | --- |
| typecheck-soundness-witness | Agent finds loop memoization, but misses nested returned-function writes or uses too few iterations and cannot produce an accepted concrete type error. | Agent identifies the incomplete signature and produces a checker-accepted type error through loop-carried function assignment. | Repair any parser/interpreter disagreement or false rejection. Harden only through a new complete checker version with one documented bug and new canonical/alternative controls; rerun the 15-minute baseline and all gates. Retain if valid and crux evidence is substantive. Retire if ordinary random generation finds it quickly after hardening or repeated strong-model successes make it an easy control. |
| exact-fused-dot | Agent rounds products/intermediates, mishandles a specified tie or exceptional case, and own tests fail to detect it. | Agent uses an exact accumulator and independently checks boundary cases before success. | Repair only specification or grader errors. Harden by documented numerical coverage changes with equivalent implementations passing. Retain with real arithmetic-crux failures. Retire as a hard candidate if strong families consistently implement the complete model; do not make timeouts the difficulty. |
| mixed-width-tso | Incomplete state search, wrong byte forwarding, drain order, or fence scope survives the agent's own tests. | Complete search with correct per-byte forwarding succeeds. | Repair any mismatch against the published machine. Harden only with justified semantic cases within clear finite bounds. Retain as a control if valid. Retire as a hard candidate after repeated complete solutions. |
| checkpointed-journal | Agent commits bytes from the wrong transaction incarnation, ignores a seal/checkpoint rule, or incorrectly handles prefix termination. | A complete staged replay checks seals, commit order, checkpoint state and truncation. | Repair ambiguous byte-format or checksum rules. Harden via well-specified recovery interactions and new controls, never hidden semantics. Retain if valid; retire as a hard candidate after repeated complete solutions. |
| atomic-range-history | Agent commits to one local order, ignores range observations, or uses incorrect real-time endpoints. | Exhaustive transaction search and semantic replay succeed within the bounds. | Repair endpoint/spec inconsistencies. Keep the current 10-transaction task as a control. Retire as a hard candidate if exhaustive search works reliably; do not inflate bounds until runtime becomes the obstacle. |

**Inferred — common admission gate.** Every revision requires canonical reward
1, a different correct solution reward 1, substantive wrong solutions reward 0,
isolation checks, and a clean Harbor oracle. Changes get a new manifest and
fresh forecasts; prior results are not silently transferred. Preserve failed
attempts and explain all exclusions. The final one-page `report.md` is deferred
until the evaluator returns its actual overnight rewards and trajectories.

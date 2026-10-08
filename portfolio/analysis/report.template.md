# Final report — template, not a submission

**Unknown:** No overnight proxy results or trajectories have been supplied. Do not rename this file `report.md` or fill in findings until the evidence exists. Keep the completed report to one page.

- **Verified changes:** For each repaired, hardened, unchanged, or retired task, state the final version, change, proxy evidence, and repeated validity checks. Explain replacements needed to retain five packages.
- **Verified proxy results:** Report passes / valid trials by model family and task version; list excluded infrastructure or harness failures separately. **Inferred uncertainty:** Give a small-sample interval/posterior and frontier-transfer sensitivity; do not pool unlike model families as exchangeable frontier trials.
- **Verified trajectories:** Cite actual trajectory file, trial ID, step index, tool action/output, and the violated semantic rule. **Inferred transfer:** Explain why the failure mechanism is likely to transfer and identify contrary evidence, including successful runs. A wrong final answer alone does not establish the mechanism.
- **Inferred final forecasts:** Include one row per final task with nine normalized probabilities P(K=0), …, P(K=8), conditional on a valid task and the specified harness. Explain how changed tasks borrow evidence, if any, from earlier versions.
- **Inferred hardest task:** Name it and state a concrete falsifier: e.g. the target passes at least 3/8, or its observed failure mechanism differs from the predicted mechanism. Distinguish those possibilities from an invalid task.
- **Verified workflow:** Describe who actually did generation, implementation, independent implementation, critique, testing, and revision. Disclose prompts, agent/model identity, tools, orchestration, settings, and any reuse of canonical code. Do not claim independent agents when only one agent was used.

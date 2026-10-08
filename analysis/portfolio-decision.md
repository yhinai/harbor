# Portfolio decision

**Reported — current selection.** The user selected these five tasks for the
Phase 3 freeze: `typecheck-soundness-witness`, `exact-fused-dot`,
`mixed-width-tso`, `checkpointed-journal`, and `atomic-range-history`.
`atomic-range-history` is retained again. `alignment-relaxation` is retired.
SQLite is removed from the plan and its draft specification has been deleted.
No SQLite task package will be submitted.

**Verified — history.** The earlier Phase 2 decision record is preserved as
`portfolio-decision-v1.json`; it is historical and superseded by
`portfolio-plan-v3.json`. The earlier frozen Day 1 records also remain intact.
The user specified a 9 AM local deadline and paused all paid model calls.

**Inferred — diversity.** The new task asks for a concrete counterexample to a
static checker, evaluated by an independent concrete execution mechanism. The
four retained tasks ask for implementations of complete specifications.
This changes the portfolio's problem-solving pattern, although its tasks still
share the same author and CPU-only Python environments.

**Inferred — difficulty.** The older published frontier anchors in
`research-memo.md` are reference points for mechanisms and upper bounds on
expected difficulty for newer frontier models. They are not estimates of the
new tasks' pass rates. The 10-transaction bound makes `atomic-range-history`
plausibly solvable by exhaustive search. Local correctness checks establish
validity evidence, not frontier difficulty.

**Unknown — forecasts.** Neither target has been run. No valid paid development
panel or official overnight panel has been observed. Provisional predictions
and their revisions must be identified by version; the Phase 4 Day 1 update
still requires the user's next `go`.

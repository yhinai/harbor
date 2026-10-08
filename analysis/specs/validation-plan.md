# Phase 3 validation contract

**Reported — selection.** Build `typecheck-soundness-witness`; retain
`exact-fused-dot`, `mixed-width-tso`, `checkpointed-journal`, and
`atomic-range-history`. Complete by 9 AM local time. Paid model calls remain
on hold. No target frontier model may be run.

**Inferred — required gates.** The new package must accept the canonical JSON
program and a structurally different correct program, reject wrong programs,
pass isolation probes, and earn full reward in an actual Harbor oracle trial.
Run all five canonical solutions through Harbor against the final package bytes.

**Inferred — grader design.** Read only the declared JSON artifact under the
agent account's permissions. Parse it with frozen trusted code. Run the frozen
checker and reference interpreter; full reward requires both static acceptance
and a runtime type error within the documented limits. Candidate reports,
edited public helpers, and candidate-authored traces do not determine reward.
Equivalent valid programs receive the same reward without matching a digest,
reference instruction sequence, or trace.

**Inferred — controls.** Reject normal termination, static rejection, invalid
JSON, duplicate keys, malformed ASTs, direct wrong-kind operations, direct cell
writes followed by incompatible uses, correctly merged branch effects, and
programs with too few loop iterations to produce a type error. Check the
inclusive final-step boundary. A corrected checker should reject the reference
programs, establishing that the intended checker bug explains their acceptance.

**Inferred — baseline.** Generate random programs with a recorded seed and
coverage-guided mutations for 15 minutes. Include cells, conditionals, loops,
functions returning functions, and assignments between function variables.
Record counts, accepted programs, concrete results, source hashes, and any
accepted program producing a type error. If one is found, harden the task and
record both versions honestly. A negative random search is limited evidence.

**Inferred — freeze.** Preserve historical manifests, add a versioned amendment,
and hash the complete five-package set and its validation evidence. The paid
hold remains active after the freeze; Phase 4 requires the user's next `go`.

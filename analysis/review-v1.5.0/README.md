# Offline completed-panel review

**Verified:** Version 1.5.0 adds an audit and revised forecasts; it does not change frozen task packages, Day 1 files, or the original archive. No paid calls were made. No `report.md` is created.

Read `review.md`, then `forecasts.md`. `audit-summary.json` combines 119 artifact-only passes and one trajectory-reconstructed dependency pass without hiding the original replay gap. `replay-summary.json` retains the artifact-only result. `trajectory-metrics.json` covers all 120 successful trajectories; `selected-trajectories/` contains the 30 cost-extreme excerpt sets used for semantic review. `command-index/` is an automated screening index, not 120 manually adjudicated trajectories. Error-text matches include source listings and self-test problems.

`preflight-copy-error/` preserves an audit-runner error, not model failures. `root-probe-review.json` preserves exact probe events and the model-originated protocol error. Earlier outcomes are never overwritten by this review.

Tools are under `tools/review-v1.5.0/`. Replay and helper reconstruction need the existing offline Docker runtime on `matrix@mini`, plus the original saved study and raw jobs. Inspection reads saved trajectories. Summarization uses the standard library and makes no network calls. These tools write this version's output paths: preserve this frozen directory and change the output version before any future rerun. The amendment manifest hashes review artifacts and tools; its own checksum is separate.

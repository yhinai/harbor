# Harness v1.3.0 offline validation

**Verified:** The separate harness ran on matrix with Python 3.12.15, Harbor 0.24.0, and the dedicated Colima Docker VM. No paid model requests were made. This is a development milestone, not new difficulty evidence and not the evaluator-results report.

## Completed checks

- **Verified:** Nine mock transport/gate scenarios passed: complete response, active-stream absolute deadline, stream inactivity, missing completion marker, malformed JSON, invalid JSON shape, HTTP error, external cancellation, and disabled paid execution. Failure diagnostics retain chunk counts and last-chunk ages.
- **Verified:** Budget checks passed for the proxy allowlist, low per-trial limits, rejection of a ceiling above $100, settlement, and operation without an aggregate ceiling. Temporary ledgers were used, never the frozen ledger.
- **Verified:** A synthetic empty response with finish_reason=length produces `ProxyOutputLimit`, correcting the previous misleading empty-response classification.
- **Verified:** Actual Harbor integration passed ten checks through eleven terminal calls: ordinary output, nonzero exit, timeout, nested timeout, a descendant creating a session, background descendant cleanup, bounded output, output threshold, recovery, and descendant/application-connectivity checks. One-second command timeouts returned through Harbor in approximately 1.17–1.23 seconds.
- **Verified:** Explicitly stopping a separate Docker container during a nested command ended the exec and left the container stopped; the test removed its container. This does not claim a separate Harbor external-cancellation test.
- **Verified:** All five canonical Harbor oracle trials returned reward 1 without trial exceptions. These confirm portability of the existing canonical packages; they do not constitute additional model pass-rate samples or rerun all alternative/wrong-solution validation gates.
- **Verified:** All 457 archived artifact hashes and every present loose frozen artifact matched before and after the remote validation. The Day 1 archive remains unchanged.

## Failures preserved and resolved

**Verified:** Initial setup failed because the Docker Buildx plugin was missing. Its exception record is retained; installing the official plugin allowed the run to reach the tests.

**Verified/source-inspected:** The first network assertion tested TCP connect alone and failed. Harbor's sidecar redirects TCP to a local transparent proxy; a successful initial handshake does not establish an external application connection. The revised test checks TLS application connectivity, which was denied with `SSLEOFError`. The network policy was not changed. Both the initial assertion failure and the source-derived diagnosis are retained.

**Verified limitation:** The existing Harbor sidecar policy permits DNS and ICMP. This setup is not strict Docker `network_mode=none` isolation. The check establishes rejection of the tested external TLS connection, not exhaustive denial of every possible network channel. This matters when interpreting the assignment's offline assumption. The frozen task specifications and original evidence were not rewritten.

**Verified limitation:** The output threshold is polled, not a hard disk quota. The output test wrote 17,000,000 bytes before cleanup despite an 8-MiB threshold; captured output remained bounded. Files are temporary and removed on wrapper exit. Future heavy-output workloads may need a stronger resource mechanism with explicitly declared semantics.

## New protocol and remaining uncertainty

**Verified implementation:** Terminal calls own and clean up their descendants; background jobs do not persist after return. This differs from the frozen harness and must be declared in a follow-up study. A timeout returns an ordinary tool result so an agent may recover. Request failures distinguish 1,200-second absolute deadlines from 600-second stream inactivity, actual transport errors, malformed protocol responses, output exhaustion, and turn exhaustion. Long active streams can still exhaust a declared allowance.

**Unknown:** Real-provider compatibility and completion rates under v1.3.0. No provider smoke or paid follow-up ran. The existing task allowance remains 1,800 seconds. Terminal/container stop checks do not cover every possible race or filesystem workload, and the explicit Docker cancellation test is narrower than cancellation through every Harbor orchestration path.

**Inferred next decision:** This milestone supports starting a separately preregistered compatibility/follow-up protocol when authorized. It does not justify replacing the original censored outcomes or claiming the current five tasks are hard. The previous 55-attempt panel and forecasts remain frozen.

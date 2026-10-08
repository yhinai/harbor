# Offline harness v1.3.0

This version lives outside the immutable Day 1 tree. It is a follow-up development harness, not an amendment to any original reward or forecast.

## Runtime

The primary execution checkout is `matrix:/Users/matrix/projects/harbor`. Tools are installed in the private `/Users/matrix/.local/harbor-runtime` prefix, without sudo or shared Homebrew changes. The dedicated `frontier-portfolio` Colima VM uses 10 CPUs, 10 GiB memory, and a 60 GiB data disk. It does not activate a different default Docker context. No credentials were transferred.

On matrix:

```sh
cd ~/projects/harbor
. tools/harness-v1.3.0/matrix-env.sh
colima status --profile frontier-portfolio
tmp/harbor-venv/bin/python tools/harness-v1.3.0/test_stream.py
tmp/harbor-venv/bin/python tools/harness-v1.3.0/test_budget.py
tmp/harbor-venv/bin/python tools/harness-v1.3.0/test_agent_output.py
tmp/harbor-venv/bin/python tools/harness-v1.3.0/test_container_cancel.py
tmp/harbor-venv/bin/python -u tools/harness-v1.3.0/validate_offline.py
```

`validate_offline.py` creates a new temporary job directory each time. It runs a deterministic Harbor integration agent followed by the five existing canonical Harbor oracles. This is development infrastructure testing, not an agent-difficulty panel. It checks the frozen archive and present loose artifacts before and after the run. Durable results are written to `analysis/harness-v1.3.0/evidence/`. Temporary fixtures, environments, and verbose logs remain under ignored `tmp/`.

## Terminal semantics

- Commands have a declared 1–60 second allowance; the outer environment call allows ten extra seconds for cleanup and serialization.
- Calls adopt orphaned descendants and clean up descendants before returning, including children that create a new session. Background jobs do not persist between tool calls. This deliberate protocol change must be declared before any follow-up panel; do not silently apply it to frozen trials.
- Normal exit, nonzero exit, and command timeout are ordinary tool results. A timeout returns code 124 so the agent can recover.
- Each output stream retains at most 256 KiB, using its beginning and end when truncated. Original byte counts and truncation flags are recorded. This bounds capture memory, not all disk use.
- Output files are monitored against an 8 MiB per-stream threshold, with code 125 for output exhaustion. Polling may allow overshoot; this is not a hard filesystem quota. Temporary output files are removed when the wrapper exits.
- Cleanup failure remains an infrastructure exception; it is not a wrong solution.

## Request semantics

The new adapter is `fireworks_agent_v130:FireworksAgent`. It retains the literal proxy allowlist and at most $100 per trial, with no aggregate ceiling. Its ledger is separate from the frozen ledger. Paid execution is disabled before credential lookup or ledger mutation unless explicitly enabled for a newly authorized study. This milestone does not enable it or provide a paid panel runner.

The transport distinguishes `ProxyRequestDeadline` (1,200-second absolute request allowance), `ProxyStreamInactivity` (600 seconds without an SSE line), actual HTTP transport errors, invalid/incomplete protocol responses, output exhaustion, and turn exhaustion. An active stream may still reach an absolute allowance; its partial chunk counts, last-chunk age, and any reported partial usage are logged instead of calling it a network outage. No automatic retry occurs. Unknown usage retains its budget reservation. External cancellation propagates.

The 1,800-second existing task allowance is unchanged and can still terminate a long trial. The revised request limit does not promise every long response completes. A future paid protocol must predeclare all allowances and classify their exhaustion separately from semantic failures.

## Evidence and limits

Mock HTTP tests verify active-stream deadlines, inactivity, incomplete responses, malformed JSON, HTTP errors, cancellation cleanup, and the disabled-paid gate. Budget tests exercise the allowlist, reservation and settlement, per-trial caps, and absence of an aggregate cap without making API requests. Actual Harbor checks cover terminal cleanup, bounded output, recovery, and rejection of external TLS connectivity. Harbor uses a transparent TCP proxy: an initial socket handshake can succeed locally. Its existing policy permits DNS and ICMP, so these checks do not establish strict Docker `network_mode=none` isolation.

No real provider compatibility trial is part of this validation. Remote package versions and installation hashes are recorded separately. Harbor is pinned to 0.24.0; installed dependency versions are recorded as evidence. The remote Python patch version is 3.12.15, while task containers retain their frozen Python 3.12.12 image.

Official installation references: [Lima binary installation](https://lima-vm.io/docs/installation/), [Colima installation](https://github.com/abiosoft/colima/blob/main/docs/INSTALL.md), [Docker binaries](https://docs.docker.com/engine/install/binaries/). Exact release URLs and hashes appear in the installation evidence; Docker's downloaded archive hash is recorded without claiming an independently published digest was checked.

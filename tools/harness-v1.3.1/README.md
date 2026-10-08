# Supervised offline runner v1.3.1

Primary host: `matrix@mini`, reachable from the development machine through the working SSH alias `matrix`. Project path: `/Users/matrix/projects/harbor`. The local `mini` alias currently points to a different, unreachable address and was left unchanged.

This version adds supervision and separate per-run evidence without editing the frozen v1.3.0 core or Day 1 artifacts. It invokes only deterministic tests and canonical Harbor oracles. It cannot launch a paid panel.

On the host:

```sh
cd /Users/matrix/projects/harbor
tmp/harbor-venv/bin/python tools/harness-v1.3.1/launch_matrix.py
```

The launcher privately reads `SUDO_PASSWORD` from ignored `.env` and uses it over sudo stdin only to register a uniquely named system LaunchDaemon. Its actual job runs as `matrix`, never root. The plist contains no credentials. The supervisor removes sudo/Fireworks credentials and paid-enable flags from the child environment. No password is printed or passed as a command-line argument.

A user launchd bootstrap was rejected on this headless SSH account, so the actual run uses the system domain. `caffeinate -i` prevents idle system sleep only while the job exists. A reconnect, screen sleep, or SSH disconnect does not own the job's lifetime. Unexpected interruption is reported by the retained running status plus absence of a live process; automatic restart or billing-ambiguous retry is not implemented.

Every run gets a new ID. Status and evidence are written to `analysis/harness-v1.3.1/runs/<run-id>/`; verbose stdout/stderr and the launch record are under ignored `tmp/launchd/`. Status transitions are atomic: running, completed, or failed. Existing run IDs are rejected. KeepAlive is false; no automatic retry occurs. A loaded job may be invoked at reboot because RunAtLoad is true, but the existing-run check rejects repeating that run. Reboot recovery itself has not been tested.

The first run was launched with the equivalent inline registration code before this helper was saved; the reusable helper's `--help` was checked without launching a second job. The new validator changes the evidence destination and wrapper version only; the core integration agent remains v1.3.0. Each run verifies the v1.3.0 amendment hashes and frozen task hashes rather than overwriting those records.

Monitor from this development machine:

```sh
ssh matrix 'cat /Users/matrix/projects/harbor/analysis/harness-v1.3.1/runs/*/status.json'
```

A completed offline run is not a model result or evidence of task difficulty. Paid compatibility tests still require a separately authorized follow-up protocol. Existing v1.3.0 limitations, including permitted DNS/ICMP and a polled output threshold, are unchanged.

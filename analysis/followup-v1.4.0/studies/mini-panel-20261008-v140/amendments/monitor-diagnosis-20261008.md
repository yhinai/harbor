# Monitor diagnosis · 2026-10-08

Verified by live SSH reads around 12:18 PM America/Los_Angeles, before SSH access subsequently timed out twice:

- Status reported eight active attempts, 65 finished attempts including smokes, seven currently counted valid panel trials, all passing, and a new-dispatch halt labelled `Kernel memory termination; new dispatch stopped`.
- Merged panel accounting (original outcomes superseded by versioned corrections) contained 21 RuntimeError, 27 host_memory_pressure, seven valid, one ProxyProtocolFailure, and eight scheduler_duplicate completed attempts. Two duplicate attempts were still active at the snapshot. These counts are provisional, not final difficulty evidence.
- The ledger reported an uncached-rate usage estimate of $67.2741454. The conservative booked amount was $140.94530775, including unresolved reservations. Neither number is a verified provider invoice. Four requests had unresolved/reserved usage at the snapshot.
- The five recorded memory events occurred with 10028–10644 MiB VM MemAvailable. Linux dmesg identified `CONSTRAINT_MEMCG` and `Memory cgroup out of memory`, killing agent-owned python3 processes near 1 GiB in three container IDs. This establishes container-limit events, not host-wide memory exhaustion.

Verified implementation issue: the v1.4.2 monitor treats any increase in the VM-wide oom_kill counter as host pressure, flags all active attempts, and halts dispatch. That counter also includes individual cgroup terminations. The 27 host_memory_pressure exclusions therefore require audit and cannot be treated as established host-wide resource failures. Raw Harbor results and trajectories remain preserved; this diagnosis changes no rewards or frozen artifacts.

Inferred next action: correct attribution in a new operational version, audit raw results and command recovery for the affected containers, reverse unrelated blanket exclusions through versioned corrections, and then resume only the outstanding logical slots under the existing authorization. A container memory-limit event alone does not establish failure of another trial. No additional paid requests were launched by this status investigation.

Unknown: present host connectivity, the cause of the SSH timeout, updated rewards/spend after the last successful read, and the final outcome of the eight active attempts. Do not infer shutdown from SSH failure.

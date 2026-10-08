# Evidence and design rationale

**Verified:** The assignment text supplied by the user is the authority for deliverables, ranking, preregistration, eight-trial forecasts, the ≤2/8 hardness criterion, and exclusion of infrastructure failures. A passing local test suite alone does not prove that a task meets every evaluation criterion.

**Verified — Harbor:** Primary documentation specifies `instruction.md`, `task.toml`, an environment, `tests/test.sh`, and a canonical `solution/solve.sh`. Tests write `/logs/verifier/reward.txt`. The installed 0.24.0 parser loaded all packages, and its Docker oracle passed all five. Sources: [task structure](https://github.com/harbor-framework/harbor/blob/main/docs/content/docs/tasks/index.mdx), [configuration source](https://github.com/harbor-framework/harbor/blob/main/src/harbor/models/task/config.py). The Python base image is pinned by registry digest. Runtime tests require no package installation or network.

**Verified — arithmetic motivation:** Exact dot-product accumulation is an established systems problem. [Berkeley technical report EECS-2018-51](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2018/EECS-2018-51.html) studies exact accumulation for floating-point dot products. **Inferred design:** parameterized small formats permit broad exhaustive checks, while larger formats expose cancellation and rounding mistakes. This task explicitly defines its complete arithmetic/flag model; no hidden IEEE requirements are imposed.

**Verified — memory-model motivation:** [Owens, Sarkar, and Sewell, UCAM-CL-TR-745](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-745.html) gives an operational x86-TSO model based on local write buffers. **Inferred design:** a bounded, explicitly defined mixed-width machine makes complete outcome enumeration reproducible. Our specification is a teaching model, not an x86 conformance test.

**Verified — history motivation:** [Herlihy and Wing, Linearizability (1990)](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf) defines linearizability using a legal sequential ordering consistent with real-time order. **Inferred design:** atomic transactions containing scans make per-key or greedy reasoning insufficient. Witness replay accepts equivalent orders instead of comparing against a single canonical order.

**Verified — recovery motivation:** [SQLite WAL recovery documentation](https://www.sqlite.org/walformat.html#recovery) describes checking frames and stopping at an invalid checksum. **Inferred design:** combining prefix validity with transaction seals and checkpoint boundaries tests temporal reasoning. Our journal is a custom format and does not claim SQLite compatibility.

**Verified — layout evidence:** A locally authored grow-only relaxer fails three bundled cases despite producing valid layouts. The exact optimizer and independently structured enumeration agree on the optimum. **Inferred design:** this distinguishes local feasibility from global byte minimization without depending on timing measurements or external assemblers.

**Verified — proxy prices checked 2026-10-08:** [Fireworks standard serverless pricing](https://docs.fireworks.ai/serverless/pricing) lists the following USD per million tokens. Cached-input discounts are not needed for conservative budget accounting.

| Model ID suffix | Input | Output |
|---|---:|---:|
| kimi-k3 | 3.00 | 15.00 |
| glm-5p3 | 1.40 | 4.40 |
| deepseek-v4p1-flash | 0.30 | 1.20 |
| qwen3p8-max | 2.00 | 6.00 |

**Verified:** All four IDs were present in the authenticated read-only model listing. Chrome showed $385.30 prepaid credit and $0.00 October spend before inference. The billing screen showed an Enterprise usage limit with no editable cap. **Reported:** The user authorizes at most $185.30 spend, preserving $200. **Inferred control:** the host-only client reserves conservative request costs, ignores cache discounts, includes a 25% rate margin, stops at $170 operational exposure, and refuses any model outside the literal proxy allowlist. It never receives a Fable/GPT-5.6 Sol identifier. Provider usage is reported data; calculated costs are estimates until reconciled with billing.

**Unknown:** Whether proxy failure mechanisms transfer to the chosen frontier model. No paper or benchmark score cited here establishes that. No independent human or separately prompted critic has yet reviewed these custom specifications.

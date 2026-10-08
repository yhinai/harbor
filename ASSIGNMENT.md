# Predict Frontier Difficulty Across a Task Portfolio

This reformatted brief preserves the requirements of the assignment supplied by the user. Project decisions and additional constraints are recorded separately in [progress](PROJECT_STATUS.md) and [authoring provenance](portfolio/PROMPTS.md).

**Format:** Two-day asynchronous exercise.

## Goal

Build up to five agent tasks in any domain, with the goal of producing at least one that is difficult for a frontier model. The evaluators will run eight independent trials on either Fable or GPT-5.6 Sol. Do not run either target model yourself.

A successful submission produces at least one valid task and a defensible forecast made before the frontier results are known. “Hard” means the canonical solution passes, the verifier is fair, and the target model passes no more than two of eight trials. Infrastructure or harness failures do not count as model failures.

## Build and preregister

Submit five tasks in Harbor format. Tasks may share a base repository or environment, but each must be a separate package with its own instruction, verifier, and canonical solution:

```text
<task-slug>/
  task.toml
  instruction.md
  environment/Dockerfile
  tests/test.sh
  solution/solve.sh
  solution/solution.patch or another canonical reference artifact
```

For every task, the canonical solution must receive full reward and a plausible incorrect or shortcut solution must fail. The verifier should accept materially equivalent correct solutions.

Also submit `day1.md` containing one compact row per task:

- The capability gap and concrete failure mechanism.
- Predicted number of frontier passes out of eight.
- Evidence used for that prediction.
- Prompts, agents, tools, and orchestration used to create and critique it.

Rank the five tasks from most to least likely to be hard. Do not run Fable or GPT-5.6 Sol.

## Overnight proxy panel

The evaluators validate the packages and run the same inexpensive model panel on all five tasks. The following day, they return per-trial rewards and complete trajectories. Evaluation runtime is not part of working time.

## Read evidence and iterate

Use the returned results to decide which tasks to repair, harden, leave unchanged, or retire. Submit the final five task packages plus a one-page `report.md` covering:

- What changed after seeing the proxy results, and why.
- Pass-rate analysis accounting for the small number of proxy trials.
- Step-indexed trajectory evidence for the failure mechanism believed to transfer to the frontier model.
- A final probability distribution P(K=0) through P(K=8) for each task, where K is its frontier pass count.
- Which task is expected to be hardest, and what result would falsify that belief.
- How the agent workflow divided generation, implementation, critique, testing, and revision.

## Final evaluation

The evaluators run eight independent trials per final task on either Fable or GPT-5.6 Sol. A task counts as hard when its canonical solution passes, its verifier is fair, its runs contain real agent work, and the frontier model passes no more than two of eight trials.

The main deliverable is not simply one hard task found by chance. It is evidence that the process can generate a portfolio, identify likely hard tasks before frontier evaluation, update rationally from cheaper trials, and concentrate effort until at least one task is both hard and valid.

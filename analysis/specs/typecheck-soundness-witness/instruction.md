# Find a type-checker counterexample

Write `/app/witness.json`, a program in the Reed language that the supplied
static checker accepts and that produces a runtime type error in the reference
interpreter within the specified execution limit.

The complete language specification is in `/app/LANGUAGE.md`. The parser,
checker, and interpreter are available as `/app/language.py`, `/app/checker.py`,
and `/app/interpreter.py`. Run `python3 /app/evaluate.py /app/witness.json` to
check a program locally. Exit status 0 means that it satisfies the objective;
the JSON output includes acceptance, execution status, and a step trace.

The submission artifact is only `/app/witness.json`. The grader evaluates it
with unchanged copies of the supplied parser, checker, and interpreter. Any
program satisfying the objective and documented limits receives full reward.
The environment is CPU-only and has no network access.

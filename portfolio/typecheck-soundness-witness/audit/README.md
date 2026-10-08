# Construction and validation notes

**Verified — intended bug.** The checker memoizes loop joins. Its memo key keeps
the outer function's write set and the result's structural shape, but omits
nested function write sets. A loop-carried assignment can add a returned
function's writes on a later analysis iteration while the memo key stays the
same. The saved result then misses a cell write. The reference interpreter uses
concrete environments and shared cells, independently of that static summary.

**Verified — canonical execution.** `first` and `second` initially return a
function with no writes. Each iteration assigns `first = second`, then replaces
`second` with a factory returning a function that writes text to integer-valued
cell `x`. After two iterations, calling the function obtained from `first`
writes text. The subsequent integer addition raises a type error at step 26.

**Verified — alternative execution.** A three-variable chain advances over three
iterations, with a conditional assignment and two cells. A separately bound
returned function changes text-valued `x` to an integer. Concatenating `x` with
text raises a type error at step 48. This program has a different dataflow chain,
branch structure, cell configuration, and failing operator.

**Verified — fault control.** Including the full nested type in the memo key
makes the corrected checker reject both programs. The original simple
intersection-based checker bug was discarded after random generation found a
counterexample in about 1.8 seconds. Its baseline record and source snapshot are
preserved under `evidence/`. These observations do not establish frontier
hardness.

**Inferred — residual risk.** The programs, checker, interpreter, and controls
share one author. The explicit-stack interpreter does not use static type
summaries, but correlated specification mistakes remain possible. Equivalent
correct programs are accepted by their behavior; no reference-program equality
is used.

**Verified — boundary control.** A valid program with 96 AST nodes produces its
type error at step 4096 and earns reward. Adding one harmless two-step
expression produces a step-limit result and earns zero.

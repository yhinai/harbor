# Reed language

A program is a UTF-8 JSON object with exactly `cells`, `inputs`, and `body`.
Only JSON is read; submitted Python files and reported execution traces are not
part of the program. Duplicate JSON keys and nonfinite numbers are invalid.

```
{"cells":{"box":{"types":["int","text"],"value":0}},
 "inputs":{"flag":true,"count":2},
 "body":[["eval",["add",["get","box"],["lit",1]]]]}
```

Names match `[a-z][a-z0-9_]{0,23}`. There are at most eight cells and eight
inputs, with disjoint names. Each cell declares a nonempty set of scalar kinds
and an initial value of one of those kinds. Kinds are `int`, `text`, `bool`, and
`unit`. Literals and inputs are signed 32-bit integers, strings of at most 1024
Unicode code points, booleans, or JSON null (`unit`). Booleans are distinct from
integers. Input bindings are immutable; their values are supplied by the
program, but the checker uses their kinds rather than their particular values.

## Expressions

| JSON expression | Meaning |
| --- | --- |
| `["lit", value]` | Scalar literal |
| `["var", name]` | Local variable or input |
| `["get", cell]` | Current cell value |
| `["is", cell, kind]` | Boolean test of a cell's current kind |
| `["add", a, b]` | Integer addition, wrapping to signed 32 bits |
| `["cat", a, b]` | Text concatenation, keeping the first 1024 code points |
| `["lt", a, b]` | Integer less-than comparison |
| `["not", a]` | Boolean negation |
| `["fn", statements, result]` | Zero-argument function |
| `["call", expression]` | Call a function and return its result |

Expressions evaluate left to right. Functions capture the current values of
local variables and inputs when constructed. Cells are shared across calls.
Each invocation has a fresh copy of its captured local environment. The
function executes its statements and then evaluates its result expression.
A function value can be returned, bound to a variable, and called later.
Functions cannot be stored in cells.

## Statements

| JSON statement | Meaning |
| --- | --- |
| `["let", name, expression]` | Create a local binding |
| `["assign", name, expression]` | Replace an existing local binding |
| `["set", cell, expression]` | Write a cell |
| `["eval", expression]` | Evaluate and discard the result |
| `["if", condition, then_body, else_body]` | Conditional block |
| `["repeat", count, body]` | Execute a block `max(0,min(3,count))` times |

A `let` name cannot already be a local, input, or cell name. A local introduced
inside a conditional branch or loop iteration ends at that block's end.
Assignments to pre-existing locals persist. Assignment preserves the local's
scalar kind set or its function result shape, recursively; cell-write effect
sets can differ. A `set` value must have kinds contained in the cell's declared
kinds. Conditions require booleans; repeat counts require integers.

## Static checking

The checker starts with each cell's initial kind. It tracks possible scalar
kinds, function result types, and sets of cells a function may write. Calling a
function updates the recorded kinds of those cells to their declared kind sets.
Function bodies are checked against declared cell kinds, independently of the
cell values at function construction. Conditional cell-kind tests refine the
two branches; a branch whose refined kind set is empty is unreachable.
Conditional and loop analyses combine the resulting states. Loop analysis
includes zero iterations and iterates until the state stops changing.
The supplied `checker.py` defines the exact acceptance behavior. The supplied
`interpreter.py` defines the exact concrete execution behavior. Both are used
unchanged by the grader.

## Results and limits

A runtime type error occurs when an evaluated operator receives a value of the
wrong kind, including calling a scalar. A normally terminating program, a
checker rejection, an invalid program, and a step-limit result earn no reward.
The checker must accept the program, and the interpreter must produce
`type_error` within 4096 steps. Each executed statement and expression consumes
one step, including function construction and call expressions. An error during
step 4096 counts; attempting step 4097 produces `step_limit`.

Maximum file size is 65,536 UTF-8 bytes. There are at most 512 AST nodes (each
statement or expression is a node), 128 statements per block, and depth 32 as
counted by `language.py`. Structural invalidity is rejected before checking.
The checker's fixed-point budget is 64 iterations for each loop; exceeding it
is a rejection. All resources and dependencies are local and CPU-only.

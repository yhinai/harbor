# Linearizability of atomic range transactions
Implement a checker that returns a valid serial witness for a completed
concurrent history, or proves there is no witness. A whole transaction is one
atomic operation. Individual reads inside a transaction cannot interleave with
other transactions. The state is a finite map from string keys to integer values.

## Request
`{"initial":{},"final":{"a":1},"transactions":[{"id":"t0","start":0,"end":2,"ops":[["put","a",1]]}]}`
There are 0 to 10 transactions, each with 1 to 5 operations, and at most 6 keys
in all maps, operations, and scan boundaries combined. IDs are unique strings.
Times are integer endpoints with `start < end`. Initial and final maps contain
only present keys; a missing key is absent, different from a key holding zero.
Values are integers in [-9,9]. Keys are nonempty ASCII lowercase strings, compared
lexicographically. Each operation has its expected return value in the input:
* `["get",key,expected]`: expected is an integer or JSON null for absence.
* `["put",key,value]`: assigns value, no observed return.
* `["del",key]`: removes key if present, no observed return.
* `["cas",key,expected_old,new_value,expected_success]`: compare to expected_old
  (integer or null); on equality assign new_value (integer or null, meaning
  delete), and return a boolean that must equal expected_success. A failed CAS
  makes no change. Reading an absent key produces null.
* `["scan",low,high,expected_pairs]`: return all currently present keys k with
  `low <= k < high`, as `[key,value]` pairs sorted by key. It observes writes made
  earlier in the same transaction. Bounds satisfy low < high.

## Valid witness
Every transaction appears exactly once. If A.end <= B.start, A must occur before
B; overlapping intervals impose no order. Execute transactions in witness order,
starting from initial. Every observation must match and the final map must equal
`final`. This finite specification defines the question; there are no incomplete
operations or external consistency rules.

## Response
`{"order":["t0"]}` for the example. Any valid witness is accepted, regardless of
tie breaking. Return `{"order":null}` iff no valid order exists. An empty valid
history has `order: []`, not null.

## Interface and environment
Implement `/app/main.py`. It is invoked as `python3 /app/main.py` with `/app`
as the working directory. Read newline-delimited JSON objects from stdin and
write one JSON object per input line to stdout, in the same order. No extra
stdout text. Diagnostics may go to stderr. Handle multiple requests in one
process. Input is valid JSON and obeys the bounds below; malformed semantic
objects need not be supported except where explicitly specified.

CPU-only, Python 3.12 and its standard library; no network or package installation
is needed. You may add readable helper files under `/app`. The verifier runs the
program with ordinary unprivileged file access; it must not need to modify
system files or read evaluator files. The entire verification batch has a
60-second execution allowance on 2 CPUs and 1 GiB RAM. Output object key order and
whitespace do not matter. Extra object fields are ignored.

`python3 /app/smoke.py` runs a few public examples.

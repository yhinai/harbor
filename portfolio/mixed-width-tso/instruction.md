# Exhaustive outcomes of a mixed-width buffered machine
Repair `/app/main.py` to enumerate every terminal observable outcome of the
finite machine below. It is a deliberately specified TSO-like teaching model,
not a claim about all behaviors of actual x86 hardware. All operations below
are atomic transitions, including multi-byte memory accesses.

## Request
`{"memory":[0,0],"threads":[[["store",0,1,1],["load",1,1]],[["store",1,1,1],["load",0,1]]]}`
There are 1 to 3 threads, each with 0 to 4 instructions, at most 10 instructions
total, and 1 to 8 initial memory bytes. Addresses are byte offsets, widths are
1, 2, or 4, and accesses fit in memory. Values are unsigned and fit their width.
Multi-byte values use little-endian byte order. Instructions are:
* `["store",address,width,value]`
* `["load",address,width]`
* `["fence"]`
* `["xchg",address,width,value]`

## Machine
Initially each thread has program counter 0, an empty FIFO store buffer, and
an empty observation list. Shared memory starts at the supplied bytes. At each
step choose exactly one enabled transition:
1. Execute the next instruction of any thread, in program order:
   * `store` appends the complete (address,width,value) store to that thread's
     FIFO buffer and advances its program counter. It does not change memory.
   * `load` reads each byte independently: the youngest buffered store in the
     same thread covering that byte wins; otherwise read shared memory. Assemble
     the bytes into one unsigned integer, append it to that thread's observation
     list, and advance. It does not block on a nonempty buffer.
   * `fence` is enabled only if that thread's buffer is empty. Advance its counter.
   * `xchg` is enabled only if that thread's buffer is empty. Atomically read the
     indicated shared-memory value, append it to this thread's observations,
     replace those bytes with the supplied value, and advance. It neither drains
     nor blocks on other threads' buffers.
2. Drain the oldest store of any nonempty thread buffer to shared memory, removing
   the store. All its bytes become visible together. Draining is possible even
   after the issuing thread finishes its instructions.

A state is terminal only when all threads finished AND every buffer is empty.
No fairness restriction changes the set of finite terminal executions.

## Response
`{"outcomes":[{"reads":[[0],[0]],"memory":[1,1]}, ...]}`
Return the complete set of distinct terminal observations. Each outcome contains
one observation list per thread, including empty lists, and the final memory
bytes. Outcome ordering is immaterial; duplicate outcomes are not allowed.

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

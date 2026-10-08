# Globally optimal branch layout with alignment
Implement an exact code-layout optimizer.

## Request
`{"limit":8,"items":[["label","entry"],["branch","end"],["bytes",7],["align",8],["label","end"]]}`
The location counter starts at zero. There are 0 to 60 items, up to 14 branches,
and up to 20 labels. Every branch target is a defined unique label. Items are:
* `["label",name]`: define a label at the current counter; emit no bytes.
* `["bytes",n]`: emit n bytes, where 0 <= n <= 256.
* `["align",a]`: emit the smallest nonnegative padding that makes the counter
  divisible by a, where a is one of 1,2,4,8,16,32,64.
* `["branch",target]`: choose width 2 (short) or 5 (long). A short branch at
  address p is valid iff `-limit <= address(target)-(p+2) < limit`.
  A long branch is always valid. `1 <= limit <= 128`.
Forward, backward, and self-target branches are allowed. A label immediately
before an align directive is defined before its padding. There is no trailing
alignment beyond explicit items.

## Objective and response
Minimize the final location counter, including padding, over all valid branch
width choices. Return `{"widths":[5],"size":16}` for the example above. Widths
are listed in branch appearance order. Any optimum is accepted. Report the size
of your chosen layout exactly.

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

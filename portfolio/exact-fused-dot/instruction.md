# Exact fused dot product
Implement a bit-exact fused dot product for a parameterized binary format.
All multiplication and accumulation are exact; round only the final sum.

## Request and encoding
`{"ebits":3,"fbits":2,"mode":"RNE","pairs":[["0c","0c"]]}`
Here `3 <= ebits <= 11`, `2 <= fbits <= 52`, `1+ebits+fbits <= 64`, and
there are 0 to 64 pairs. A bit pattern is a hexadecimal string of any sufficient
length, without `0x`, within the format's bit width. Bit fields from most to
least significant are sign, exponent (`ebits`), fraction (`fbits`). Let
`bias = 2**(ebits-1)-1`, `F = 2**fbits`, and `Eall = 2**ebits-1`.
* For `0 < e < Eall`, value is `(-1)**s * (F+f) * 2**(e-bias-fbits)`.
* For `e == 0`, value is `(-1)**s * f * 2**(1-bias-fbits)`, including signed zero.
* For `e == Eall, f == 0`, the value is signed infinity.
* For `e == Eall, f != 0`, it is a NaN. Its top fraction bit distinguishes
  quiet (1) from signaling (0). The canonical NaN has sign 0, exponent Eall,
  and only the top fraction bit set.

## Exceptional terms
Inspect every operand, even when another is NaN. A signaling NaN, zero times
infinity (in either order), or both positive and negative infinite products
raises `invalid`. A pair with a NaN operand contributes no infinite product
and cannot itself count as zero times infinity. Any NaN operand or `invalid`
produces the canonical NaN; no other flags are set. Otherwise an infinite
product produces the corresponding infinity, with no flags.

## Finite rounding and flags
Sum exact products, then round to this format using:
* `RNE`: nearest, ties to an even significand (low stored fraction bit 0).
* `RNA`: nearest, ties away from zero.
* `RTZ`: toward zero; `RUP`: toward positive infinity; `RDN`: toward negative infinity.

Let `emin = 1-bias`, `emax = Eall-1-bias`. If the exact nonzero magnitude is
`x` and `L=floor(log2(x))`, use quantum `q=2**max(emin-fbits,L-fbits)`.
Round `x/q` to an integer with the chosen mode and original sign, giving
magnitude `y`. These formulas define rounding even outside the finite range.
If `y >= 2**(emax+1)`, raise `overflow` and `inexact`: output signed infinity
for nearest modes and for the directed mode pointing away from zero, otherwise
signed maximum finite. For other results, raise `inexact` iff `y != x`;
raise `underflow` iff inexact and the rounded magnitude is below `2**emin`
(tininess after rounding). These are the complete flag rules.

Exact zero has negative sign iff all products are negative signed zeros and
there is at least one product, or the mode is `RDN`. A cancellation involving
nonzero products is thus positive zero except in `RDN`. An empty dot product
is positive zero except in `RDN`. A nonzero result rounded to zero retains its
exact sign. Product zero signs are operand sign XOR.

## Response
`{"bits":"0c","flags":[]}` for the request above.
Return a valid format bit pattern as hex, with no `0x`; case and leading zeros
are immaterial. `flags` is a duplicate-free list drawn from `invalid`,
`overflow`, `underflow`, `inexact`; its order is immaterial.

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

# Recover a checkpointed transactional byte journal
Implement deterministic recovery of the custom format below. This is not the
SQLite format. Replay only structurally valid prefix records and only complete,
correctly sealed transactions newer than the supplied checkpoint.

## Request
`{"pages":["00000000"],"checkpoint":0,"log":""}`
There are 1 to 8 equal-length pages of 1 to 64 bytes, as hexadecimal strings.
They are the authoritative durable checkpoint image; no consistency check against
older journal records is required. `checkpoint` is a nonnegative sequence
watermark; it can fall between records or exceed the log's last sequence.
`log` is a hex byte string of at most 64 KiB; it may end with corrupted or torn
records. Hex case is immaterial. No other input is malformed.

## Binary records
All integers are unsigned, little-endian, with no implicit padding. A record is:
`payload_length:u32 | sequence:u32 | kind:u8 | transaction_id:u32 | payload | crc:u32`.
The fixed header is 13 bytes. CRC is `zlib.crc32(header + payload) & 0xffffffff`.
Sequence must be positive and strictly greater than the previous valid record's
sequence (initially 0). Payload length must be at most 4096. Transaction ID must
be positive. Kind and payload shapes are:
* 1 BEGIN: empty payload.
* 2 PATCH: `page_index:u16 | byte_offset:u16 | byte_count:u16 | data[byte_count]`.
  Count is positive, payload length is exactly 6+count, and the patch fits in an
  existing page, with zero-based page and byte indices.
* 3 COMMIT: exactly 8 bytes, `patch_count:u32 | digest:u32`. Digest is
  `zlib.crc32(concatenation_of_PATCH_payloads) & 0xffffffff` for this incarnation,
  in log order; the empty concatenation has CRC zero.
* 4 ABORT: empty payload.

Stop at the first incomplete record, invalid CRC, invalid sequence, invalid
header/kind/ID, or invalid payload shape/bounds. That record and all following
bytes are excluded from the valid prefix. A record must be structurally valid
before it has any semantic effect, including records for inactive transactions.

## Transaction and checkpoint rules
BEGIN starts a fresh incarnation of that ID, discarding any unfinished incarnation.
PATCH stages a byte patch only if that ID is active; otherwise it is ignored.
ABORT discards the active incarnation, if any. COMMIT always closes its active
incarnation, if any. A COMMIT applies all staged patches atomically, in patch
order, iff both count and digest match AND its sequence is greater than checkpoint.
A seal mismatch closes the active incarnation without applying its patches
and leaves the valid prefix intact. A matching COMMIT at or below checkpoint
is not replayed.
Orphan COMMIT/ABORT records have no effect. Uncommitted patches have no effect.

Transactions may interleave. Apply committed transactions in COMMIT order.
Records at/below checkpoint participate in prefix validation and transaction
state processing. Return the resulting pages, valid prefix length in BYTES,
and last valid record sequence (0 for an empty prefix).

## Response
`{"pages":["00000000"],"valid_bytes":0,"last_seq":0}` for the empty-log example.
Hex case is immaterial; returned page lengths must be unchanged.

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

"""Recovery of the checkpointed transactional byte journal.

Record layout (all integers unsigned little-endian, no implicit padding)::

    payload_length:u32 | sequence:u32 | kind:u8 | transaction_id:u32 | payload | crc:u32

The fixed header is 13 bytes and ``crc`` is ``zlib.crc32(header + payload)``.

The journal is replayed as a *valid prefix*: parsing stops at the first
incomplete record, bad CRC, non-increasing/non-positive sequence, bad
header/kind/transaction id, or bad payload shape/bounds.  Everything from that
record on is excluded from the recovered prefix.
"""

import zlib

HEADER_LEN = 13   # payload_length(4) + sequence(4) + kind(1) + transaction_id(4)
CRC_LEN = 4
MAX_PAYLOAD_LEN = 4096

KIND_BEGIN = 1
KIND_PATCH = 2
KIND_COMMIT = 3
KIND_ABORT = 4


def _le16(buf, off):
    return buf[off] | (buf[off + 1] << 8)


def recover(pages_hex, checkpoint, log_hex):
    """Replay ``log_hex`` over the checkpoint image ``pages_hex``.

    Returns ``(pages_hex, valid_bytes, last_seq)``.
    """
    pages = [bytearray(bytes.fromhex(p)) for p in pages_hex]
    log = bytes.fromhex(log_hex)
    n = len(log)

    # Active incarnations: transaction id -> list of staged PATCH payloads.
    active = {}

    last_seq = 0
    off = 0

    while off < n:
        if n - off < HEADER_LEN:
            break                      # torn / truncated header

        payload_len = int.from_bytes(log[off:off + 4], 'little')
        seq = int.from_bytes(log[off + 4:off + 8], 'little')
        kind = log[off + 8]
        tx = int.from_bytes(log[off + 9:off + 13], 'little')

        if payload_len > MAX_PAYLOAD_LEN:
            break                      # oversized payload
        end = off + HEADER_LEN + payload_len + CRC_LEN
        if end > n:
            break                      # torn / truncated body or CRC

        body = log[off:off + HEADER_LEN + payload_len]
        crc = int.from_bytes(log[end - CRC_LEN:end], 'little')
        if zlib.crc32(body) & 0xFFFFFFFF != crc:
            break                      # bad seal on the record itself

        if seq <= last_seq:
            break                      # must be positive and strictly increasing
        if tx == 0:
            break                      # transaction ids must be positive

        payload = log[off + HEADER_LEN:off + HEADER_LEN + payload_len]

        # ---- structural (payload shape / bounds) validation -----------------
        if kind == KIND_BEGIN or kind == KIND_ABORT:
            if payload_len != 0:
                break
        elif kind == KIND_PATCH:
            if payload_len < 6:
                break
            count = _le16(payload, 4)
            if count == 0 or payload_len != 6 + count:
                break
            page_index = _le16(payload, 0)
            byte_offset = _le16(payload, 2)
            if page_index >= len(pages):
                break
            if byte_offset + count > len(pages[page_index]):
                break
        elif kind == KIND_COMMIT:
            if payload_len != 8:
                break
        else:
            break                      # unknown kind

        # ---- the record is valid: it now has semantic effect -----------------
        if kind == KIND_BEGIN:
            active[tx] = []            # fresh incarnation, discards unfinished one
        elif kind == KIND_PATCH:
            staged = active.get(tx)
            if staged is not None:
                staged.append(payload)
        elif kind == KIND_ABORT:
            active.pop(tx, None)
        else:                          # KIND_COMMIT
            staged = active.pop(tx, None)
            if staged is not None:
                count = int.from_bytes(payload[0:4], 'little')
                digest = int.from_bytes(payload[4:8], 'little')
                if (count == len(staged)
                        and digest == zlib.crc32(b"".join(staged)) & 0xFFFFFFFF
                        and seq > checkpoint):
                    for patch in staged:   # atomic, in patch order
                        page_index = _le16(patch, 0)
                        byte_offset = _le16(patch, 2)
                        cnt = _le16(patch, 4)
                        pages[page_index][byte_offset:byte_offset + cnt] = patch[6:6 + cnt]

        last_seq = seq
        off = end

    return [bytes(p).hex() for p in pages], off, last_seq


def solve(request):
    pages, valid_bytes, last_seq = recover(
        request["pages"], request["checkpoint"], request["log"]
    )
    return {"pages": pages, "valid_bytes": valid_bytes, "last_seq": last_seq}

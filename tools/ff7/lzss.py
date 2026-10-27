"""FF7 LZSS (4 KB ring buffer, as used by field files and other PC data).

Stream: u32 compressed length, then groups of one control byte followed by
8 items. Control bit 1 = literal byte, 0 = 2-byte reference:
  offset = b0 | ((b1 & 0xF0) << 4)   (ring-buffer position, ring starts at 0xFEE)
  length = (b1 & 0x0F) + 3
"""
import struct

N = 4096
F = 18
THRESHOLD = 2
RING_START = N - F  # 0xFEE


def decompress(buf, with_header=True):
    if with_header:
        size, = struct.unpack_from("<I", buf, 0)
        src = memoryview(buf)[4:4 + size]
    else:
        src = memoryview(buf)
    out = bytearray()
    i, n = 0, len(src)
    while i < n:
        flags = src[i]
        i += 1
        for bit in range(8):
            if i >= n:
                break
            if flags & (1 << bit):
                out.append(src[i])
                i += 1
            else:
                b0, b1 = src[i], src[i + 1]
                i += 2
                ring = b0 | ((b1 & 0xF0) << 4)
                length = (b1 & 0x0F) + THRESHOLD + 1
                # Convert ring position to an absolute output position.
                end = len(out)
                dist = (end + RING_START - ring) & (N - 1)
                pos = end - (dist or N)
                if pos >= 0 and pos + length <= end:          # plain copy (most references)
                    out += out[pos:pos + length]
                else:                                         # before the start (zeros) or overlapping
                    for k in range(length):
                        p = pos + k
                        out.append(out[p] if p >= 0 else 0)
    return bytes(out)


def compress(data, with_header=True):
    """Greedy LZSS with hash chains. Output decompresses to `data` exactly."""
    data = bytes(data)
    n = len(data)
    out = bytearray()
    head = {}
    prev = [-1] * n
    i = 0
    while i < n:
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len, best_pos = 0, 0
            if i + THRESHOLD < n:
                key = data[i:i + 3]
                cand = head.get(key, -1)
                tries = 0
                limit = min(F, n - i)
                while cand >= 0 and i - cand < N - F and tries < 64:
                    l = 3
                    while l < limit and data[cand + l] == data[i + l]:
                        l += 1
                    if l > best_len:
                        best_len, best_pos = l, cand
                        if l == limit:
                            break
                    cand = prev[cand]
                    tries += 1
            if best_len > THRESHOLD:
                ring = (best_pos + RING_START) & (N - 1)
                out.append(ring & 0xFF)
                out.append(((ring >> 4) & 0xF0) | (best_len - THRESHOLD - 1))
                step = best_len
            else:
                flags |= 1 << bit
                out.append(data[i])
                step = 1
            for k in range(i, i + step):
                if k + 2 < n:
                    key = data[k:k + 3]
                    prev[k] = head.get(key, -1)
                    head[key] = k
            i += step
        out[flag_pos] = flags
    if with_header:
        return struct.pack("<I", len(out)) + bytes(out)
    return bytes(out)

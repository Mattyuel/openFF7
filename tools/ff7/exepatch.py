"""Byte patches for ff7_en.exe (Steam). Each patch names the bytes it expects,
so a different exe version is refused instead of corrupted. The PE checksum is
recomputed after patching.

EXE_TEST: a harmless test to see whether a modified exe still starts through
Steam (SteamStub DRM): two main-menu labels change visibly ("Item" -> "ITEM",
"Quit" -> "QUIT", in .data) and one never-executed int3 padding byte in .text
becomes a NOP (tests whether the code section is integrity-checked).
"""
import struct


def _ff7(text):
    return bytes(ord(c) - 0x20 for c in text)


EXE_TEST = [
    (0x5192C0, _ff7("Item"), _ff7("ITEM"), "main menu label Item -> ITEM (.data)"),
    (0x519388, _ff7("Quit"), _ff7("QUIT"), "main menu label Quit -> QUIT (.data)"),
    (0x0008F2, b"\xCC", b"\x90", "int3 padding after a ret at 0x4014F0 -> nop (.text, never runs)"),
]


def pe_checksum(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    off = pe + 24 + 64
    total = 0
    buf = bytearray(data)
    buf[off:off + 4] = b"\0\0\0\0"
    if len(buf) % 2:
        buf += b"\0"
    for (w,) in struct.iter_unpack("<H", buf):
        total += w
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (total + len(data)) & 0xFFFFFFFF, off


def apply(data, patches):
    data = bytearray(data)
    for off, old, new, desc in patches:
        have = bytes(data[off:off + len(old)])
        if have != old:
            raise ValueError("unexpected bytes at 0x%X (%s): %s" % (off, desc, have.hex()))
        data[off:off + len(new)] = new
    value, off = pe_checksum(data)
    struct.pack_into("<I", data, off, value)
    return bytes(data)


# ---- new code section -------------------------------------------------------

IMAGE_BASE = 0x400000
SECTION_CHARACTERISTICS = 0xE0000060   # code | initialised data | exec | read | write


def _pe(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    opt = pe + 24
    return pe, opt, opt + struct.unpack_from("<H", data, pe + 20)[0]


def add_section(data, name, payload, virtual_size=0x1000):
    """Append a section holding `payload` (padded) after the last section, before
    the Authenticode blob (which is moved after it). Returns (new data, VA)."""
    data = bytearray(data)
    pe, opt, table = _pe(data)
    count = struct.unpack_from("<H", data, pe + 6)[0]
    salign, falign = struct.unpack_from("<II", data, opt + 32)
    last = table + 40 * (count - 1)
    vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", data, last + 8)
    new_hdr = table + 40 * count
    if new_hdr + 40 > struct.unpack_from("<I", data, opt + 60)[0] or any(data[new_hdr:new_hdr + 40]):
        raise ValueError("no room for another section header")
    rva = (vaddr + vsize + salign - 1) // salign * salign
    raw = (rptr + rsize + falign - 1) // falign * falign
    body = bytes(payload).ljust((max(len(payload), 1) + falign - 1) // falign * falign, b"\0")
    virtual_size = max(virtual_size, len(payload))
    # Certificate table (data directory 4) holds a file offset; keep it after us.
    cert_off, cert_size = struct.unpack_from("<II", data, opt + 96 + 8 * 4)
    cert = bytes(data[cert_off:cert_off + cert_size]) if cert_size else b""
    end = cert_off if cert_size else len(data)
    if end > raw:
        raise ValueError("data after the last section that isn't the certificate")
    out = bytearray(data[:end]).ljust(raw, b"\0") + body
    if cert:
        out = out.ljust((len(out) + 7) // 8 * 8, b"\0")
        struct.pack_into("<I", out, opt + 96 + 8 * 4, len(out))
        out += cert
    hdr = name.encode("ascii")[:8].ljust(8, b"\0") + struct.pack(
        "<IIIIIIHHI", virtual_size, rva, len(body), raw, 0, 0, 0, 0, SECTION_CHARACTERISTICS)
    out[new_hdr:new_hdr + 40] = hdr
    struct.pack_into("<H", out, pe + 6, count + 1)
    struct.pack_into("<I", out, opt + 56, (rva + virtual_size + salign - 1) // salign * salign)
    value, off = pe_checksum(out)
    struct.pack_into("<I", out, off, value)
    return bytes(out), IMAGE_BASE + rva


def va_to_file(data, va):
    pe, opt, table = _pe(data)
    rva = va - IMAGE_BASE
    for i in range(struct.unpack_from("<H", data, pe + 6)[0]):
        vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", data, table + 40 * i + 8)
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return rptr + rva - vaddr
    raise ValueError("VA 0x%X not in any section" % va)


def jmp(src, dst):
    """5-byte `jmp rel32` placed at VA src."""
    return b"\xE9" + struct.pack("<i", dst - (src + 5))


def section_test(data):
    """EXE_SECTION_TEST: QUIT label (static, proves the file loads) and a new
    section `.openff7` with code hooked into the main menu's init (0x6CA168:
    `push 0; push 0; push 1`): it writes "CAVE" over the Item label, replays the
    pushes and jumps back (proves code in a new section runs)."""
    data = apply(data, [EXE_TEST[1]])                      # Quit -> QUIT
    hook, back = 0x6CA168, 0x6CA16E
    label = 0x91A8C0
    _, cave_va = add_section(data, ".openff7", b"\0")       # where it will land
    cave = (b"\xC7\x05" + struct.pack("<I", label) + _ff7("CAVE")   # mov dword [label], "CAVE"
            + b"\x6A\x00\x6A\x00\x6A\x01")                         # the replaced pushes
    cave += jmp(cave_va + len(cave), back)
    data, va = add_section(data, ".openff7", cave)
    assert va == cave_va
    data = bytearray(data)
    off = va_to_file(data, hook)
    assert bytes(data[off:off + 6]) == b"\x6A\x00\x6A\x00\x6A\x01", data[off:off + 6].hex()
    data[off:off + 6] = jmp(hook, cave_va) + b"\x90"
    value, coff = pe_checksum(data)
    struct.pack_into("<I", data, coff, value)
    return bytes(data)

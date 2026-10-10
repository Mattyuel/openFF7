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

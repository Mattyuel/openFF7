"""Build a patched ff7_en.exe: byte patches to existing code/data (each checks
the bytes it expects) plus a new section `.openff7` holding new code and data.

Allocations get fixed virtual addresses up front (the section's VA is known
before it is written), so code assembled elsewhere (nasm, `org SECTION_VA`) and
tables can reference them. Patches are applied after the section is added.
"""
import struct

from . import exepatch

SECTION_NAME = ".openff7"


class ExeBuilder:
    def __init__(self, data):
        self.data = bytes(data)
        _, self.section_va = exepatch.add_section(self.data, SECTION_NAME, b"\0")
        self.payload = bytearray()
        self.patches = []          # (va, old, new, desc)
        self.labels = {}

    @property
    def cursor(self):
        return self.section_va + len(self.payload)

    def alloc(self, blob, name=None, align=4):
        """Place bytes in the new section; returns their VA."""
        while len(self.payload) % align:
            self.payload += b"\xcc"
        va = self.cursor
        self.payload += bytes(blob)
        if name:
            self.labels[name] = va
        return va

    def place_at(self, va, blob, name=None):
        """Place bytes at a fixed VA in the new section (for code assembled with
        `org`); the section is padded up to it."""
        if va < self.cursor:
            raise ValueError("0x%X already used (cursor 0x%X)" % (va, self.cursor))
        self.payload += b"\xcc" * (va - self.cursor)
        return self.alloc(blob, name, align=1)

    def read(self, va, n):
        off = exepatch.va_to_file(self.data, va)
        return self.data[off:off + n]

    def patch(self, va, old, new, desc):
        old, new = bytes(old), bytes(new)
        assert len(old) == len(new), desc
        have = self.read(va, len(old))
        if have != old:
            raise ValueError("unexpected bytes at 0x%X (%s): %s" % (va, desc, have.hex()))
        self.patches.append((va, old, new, desc))

    def patch_u32(self, va, old, new, desc):
        self.patch(va, struct.pack("<I", old), struct.pack("<I", new), desc)

    def build(self):
        data, va = exepatch.add_section(self.data, SECTION_NAME, bytes(self.payload) or b"\0",
                                        virtual_size=max(0x1000, len(self.payload)))
        assert va == self.section_va
        data = bytearray(data)
        for pva, old, new, desc in self.patches:
            off = exepatch.va_to_file(data, pva)
            assert bytes(data[off:off + len(old)]) == old, desc
            data[off:off + len(new)] = new
        value, coff = exepatch.pe_checksum(data)
        struct.pack_into("<I", data, coff, value)
        return bytes(data)

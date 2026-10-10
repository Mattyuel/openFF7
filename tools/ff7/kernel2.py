"""kernel2.bin: the text the game actually shows for commands, magic, items,
materia and battle messages (it replaces KERNEL.BIN's text sections 9-26 at
startup). LZSS-compressed; 18 x [u32 length + section]. Each section is a u16
offset table followed by 0xFF-terminated FF7 strings.

Sections: 0 command descriptions, 1 magic desc, 2 item desc, 3 weapon desc,
4 armor desc, 5 accessory desc, 6 materia desc, 7 key item desc, 8 command
names, 9 magic names, 10 item names, 11 weapon names, 12 armor names,
13 accessory names, 14 materia names, 15 key item names, 16 battle text,
17 summon names.

The exe loads all text into a 0x6C00-byte pool with no bounds check (original
total 26,912 bytes), so `build` refuses to grow past POOL_LIMIT.
"""
import struct

from . import lzss

CMD_DESC, MATERIA_DESC, CMD_NAMES, MATERIA_NAMES, BATTLE_TEXT = 0, 6, 8, 14, 16
POOL_LIMIT = 0x6C00


class Kernel2:
    """Sections are kept byte-for-byte; `set` appends the new string at the end
    of its section and repoints that one offset (strings may contain 0xFF
    inside control-code parameters, so they are never re-split)."""

    def __init__(self, raw):
        data = lzss.decompress(raw)
        self.sections = []
        pos = 0
        while pos < len(data):
            n, = struct.unpack_from("<I", data, pos)
            self.sections.append(bytearray(data[pos + 4:pos + 4 + n]))
            pos += 4 + n
        self.edits = []   # (section, index, text) for mirroring into KERNEL.BIN

    @classmethod
    def from_sections(cls, sections):
        """Same editing API over raw section bytes (KERNEL.BIN sections 9-26)."""
        obj = cls.__new__(cls)
        obj.sections = [bytearray(s) for s in sections]
        obj.edits = []
        return obj

    def count(self, section):
        return struct.unpack_from("<H", self.sections[section], 0)[0] // 2

    def get(self, section, index):
        sec = self.sections[section]
        a = struct.unpack_from("<H", sec, 2 * index)[0]
        end = sec.find(b"\xff", a)
        return bytes(sec[a:end if end >= 0 else len(sec)])

    def set(self, section, index, text):
        """text: FF7-encoded bytes (a trailing 0xFF terminator is optional)."""
        text = bytes(text)
        if text.endswith(b"\xff"):
            text = text[:-1]
        assert b"\xff" not in text and 0 <= index < self.count(section)
        sec = self.sections[section]
        struct.pack_into("<H", sec, 2 * index, len(sec))
        sec += bytes(text) + b"\xff"
        self.edits.append((section, index, text))
        if len(sec) > 0xFFFF:
            raise ValueError("kernel2 section %d too large" % section)

    def build(self):
        total = sum(len(s) for s in self.sections)
        if total > POOL_LIMIT:
            raise ValueError("kernel2 text is %d bytes, over the exe's %d-byte pool" % (total, POOL_LIMIT))
        out = bytearray()
        for sec in self.sections:
            out += struct.pack("<I", len(sec)) + sec
        return lzss.compress(bytes(out))

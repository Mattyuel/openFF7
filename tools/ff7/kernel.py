"""KERNEL.BIN: 27 gzip'd sections, each with a 6-byte header
(u16 compressed size, u16 uncompressed size, u16 type).

Section 3 is the new-game initialisation data copied into the savemap at
0x0054: 9 character records (132 bytes), party (3 bytes + pad), 320 item
slots (u16: qty << 9 | item id), 200 materia (u32: ap << 8 | id),
48 stolen materia, then 52 more bytes (gil etc.).
"""
import gzip
import struct
import zlib

from .text import decode

CHAR_NAMES = ["Cloud", "Barret", "Tifa", "Aerith", "Red XIII", "Yuffie",
              "Cait Sith/Young Cloud", "Vincent/Sephiroth", "Cid"]


def read_sections(buf):
    out = []
    pos = 0
    while pos + 6 <= len(buf):
        cs, us, typ = struct.unpack_from("<HHH", buf, pos)
        data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(buf[pos + 6:pos + 6 + cs])
        out.append({"type": typ, "data": data, "raw": buf[pos:pos + 6 + cs]})
        pos += 6 + cs
    tail = buf[pos:]
    return out, tail


def build_sections(sections, tail=b""):
    out = bytearray()
    for s in sections:
        if "raw" in s and s.get("_unchanged", True) and s["raw"] and _same(s):
            out += s["raw"]
            continue
        comp = gzip.compress(s["data"], 9, mtime=0)
        out += struct.pack("<HHH", len(comp), len(s["data"]), s["type"]) + comp
    return bytes(out + tail)


def _same(s):
    cs, = struct.unpack_from("<H", s["raw"], 0)
    data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(s["raw"][6:6 + cs])
    return data == s["data"]


class InitData:
    """Editable view of section 3 (new-game savemap data)."""
    CHAR = 132
    PARTY = 9 * 132
    ITEMS = PARTY + 4
    MATERIA = ITEMS + 640
    STOLEN = MATERIA + 800

    def __init__(self, data):
        self.data = bytearray(data)

    def character(self, i):
        o = i * self.CHAR
        c = self.data[o:o + self.CHAR]
        hp, base_hp, mp, base_mp = struct.unpack_from("<HHHH", c, 0x2C)
        max_hp, max_mp = struct.unpack_from("<HH", c, 0x38)
        return {"id": c[0], "level": c[1], "name": decode(c[0x10:0x1C]).strip(),
                "weapon": c[0x1C], "armor": c[0x1D], "accessory": c[0x1E],
                "hp": hp, "max_hp": max_hp, "mp": mp, "max_mp": max_mp,
                "weapon_materia": list(struct.unpack_from("<8I", c, 0x40)),
                "armor_materia": list(struct.unpack_from("<8I", c, 0x60))}

    @property
    def party(self):
        return list(self.data[self.PARTY:self.PARTY + 3])

    @party.setter
    def party(self, members):
        members = list(members) + [0xFF] * (3 - len(members))
        self.data[self.PARTY:self.PARTY + 3] = bytes(members[:3])

    def set_name(self, i, name):
        """Set character i's default name (max 11 characters)."""
        from .text import encode
        raw = encode(name)
        if len(raw) > 12:
            raise ValueError("name too long: %s" % name)
        o = i * self.CHAR + 0x10
        self.data[o:o + 12] = raw.ljust(12, b"\xff")

    def items(self):
        out = []
        for i in range(320):
            v, = struct.unpack_from("<H", self.data, self.ITEMS + i * 2)
            if v != 0xFFFF:
                out.append((v & 0x1FF, v >> 9))
        return out

    def set_items(self, items):
        for i in range(320):
            v = 0xFFFF
            if i < len(items):
                item, qty = items[i]
                v = (qty << 9) | item
            struct.pack_into("<H", self.data, self.ITEMS + i * 2, v)

    def materia(self):
        out = []
        for i in range(200):
            v, = struct.unpack_from("<I", self.data, self.MATERIA + i * 4)
            if v != 0xFFFFFFFF:
                out.append((v & 0xFF, v >> 8))
        return out

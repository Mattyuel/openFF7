"""FF7 PC field file (one entry of flevel.lgp, after LZSS decompression).

Header: u16 0, u32 section_count (9), u32 offsets[9]. Each section starts with
a u32 length. Section order:
  0 script/dialogue, 1 camera, 2 model loader, 3 palette, 4 walkmesh,
  5 tile map (unused), 6 encounters, 7 triggers, 8 background
"""
import struct

SECTION_NAMES = ["script", "camera", "models", "palette", "walkmesh",
                 "tilemap", "encounter", "triggers", "background"]


class FieldFile:
    def __init__(self, raw):
        self.raw = bytes(raw)
        _, count = struct.unpack_from("<HI", raw, 0)
        offsets = struct.unpack_from("<%dI" % count, raw, 6)
        self.sections = []
        self._declared = []  # (original bytes, declared size) for faithful rebuilds
        end = 0
        for i, off in enumerate(offsets):
            size, = struct.unpack_from("<I", raw, off)
            # A few fields (e.g. blackbgb) declare a script section size that
            # overlaps the next section; the next offset is authoritative.
            limit = offsets[i + 1] if i + 1 < count else len(raw)
            data = bytes(raw[off + 4:min(off + 4 + size, limit)])
            # Padding between this section and the next (kept for unmodified sections).
            gap = bytes(raw[off + 4 + len(data):limit]) if i + 1 < count else b""
            self.sections.append(data)
            self._declared.append((data, size, gap))
            end = max(end, off + 4 + len(data))
        # Bytes after the last section (normally the "FINAL FANTASY7" marker).
        self.trailer = bytes(raw[end:])

    def build(self):
        count = len(self.sections)
        out = bytearray(struct.pack("<HI", 0, count))
        parts = []
        for i, sec in enumerate(self.sections):
            orig, size, gap = self._declared[i] if i < len(self._declared) else (None, 0, b"")
            if sec == orig:
                parts.append(struct.pack("<I", size) + sec + gap)
            else:
                parts.append(struct.pack("<I", len(sec)) + sec)
        pos = 6 + 4 * count
        offsets = []
        for part in parts:
            offsets.append(pos)
            pos += len(part)
        out += struct.pack("<%dI" % count, *offsets)
        for part in parts:
            out += part
        out += self.trailer
        return bytes(out)

    def section(self, name):
        return self.sections[SECTION_NAMES.index(name)]

    def set_section(self, name, data):
        self.sections[SECTION_NAMES.index(name)] = bytes(data)


class ScriptSection:
    """Section 0: entity scripts, dialogue strings and AKAO blocks."""

    def __init__(self, data):
        self.data = data
        (self.version, self.n_entities, self.n_models, self.string_offset,
         self.n_akao, self.scale) = struct.unpack_from("<HBBHHH", data, 0)
        self.creator = data[16:24].split(b"\0")[0].decode("latin-1")
        self.name = data[24:32].split(b"\0")[0].decode("latin-1")
        o = 32
        self.entity_names = []
        for _ in range(self.n_entities):
            self.entity_names.append(data[o:o + 8].split(b"\0")[0].decode("latin-1"))
            o += 8
        self.akao_offsets = list(struct.unpack_from("<%dI" % self.n_akao, data, o))
        o += 4 * self.n_akao
        self.scripts = []
        for _ in range(self.n_entities):
            self.scripts.append(list(struct.unpack_from("<32H", data, o)))
            o += 64
        self.code_start = o
        # A few unused fields (e.g. las4_42, nivgate3, nivl_4) have a string
        # offset past the end of the section; treat them as having no text.
        self.broken = self.string_offset + 2 > len(data)
        self.string_offsets = []
        if not self.broken:
            n_str, = struct.unpack_from("<H", data, self.string_offset)
            if self.string_offset + 2 + 2 * n_str <= len(data):
                self.string_offsets = list(struct.unpack_from("<%dH" % n_str, data, self.string_offset + 2))
            else:
                self.broken = True

    def raw_string(self, i):
        start = self.string_offset + self.string_offsets[i]
        end = self.data.find(b"\xFF", start)
        return self.data[start:end if end >= 0 else len(self.data)]

    def script_bounds(self):
        """Sorted unique script entry points within the code area."""
        return sorted(set(p for ent in self.scripts for p in ent))

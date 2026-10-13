"""Field model loader section (section 2): which character models a field
loads and their animations. Entities pick a model with CHAR <index>.

  u16 unknown, u16 count, u16 scale
  per model: u16 name_len, name, u16 unknown, char hrc[8], char scale[4],
             u16 n_anims, u8 light[30], then per anim: u16 len, name, u16 unknown
"""
import struct


class ModelLoader:
    def __init__(self, data):
        self.head = data[:6]
        self.unknown, count, self.scale = struct.unpack_from("<HHH", data, 0)
        self.models = []  # raw bytes of each model entry
        o = 6
        for _ in range(count):
            start = o
            nl, = struct.unpack_from("<H", data, o)
            o += 2 + nl + 2 + 8 + 4
            na, = struct.unpack_from("<H", data, o)
            o += 2 + 30
            for _ in range(na):
                al, = struct.unpack_from("<H", data, o)
                o += 2 + al + 2
            self.models.append(bytes(data[start:o]))
        self.trailer = bytes(data[o:])

    @staticmethod
    def name(entry):
        nl, = struct.unpack_from("<H", entry, 0)
        return entry[2:2 + nl].decode("latin-1")

    @staticmethod
    def hrc(entry):
        nl, = struct.unpack_from("<H", entry, 0)
        return entry[2 + nl + 2:2 + nl + 10].decode("latin-1")

    @staticmethod
    def entry_scale(entry):
        """The model's scale (ASCII digits, e.g. b"512\0")."""
        nl, = struct.unpack_from("<H", entry, 0)
        return int(entry[2 + nl + 10:2 + nl + 14].split(b"\0")[0] or b"0")

    @staticmethod
    def with_scale(entry, scale):
        nl, = struct.unpack_from("<H", entry, 0)
        text = str(scale).encode("ascii")
        assert len(text) <= 4, scale
        return entry[:2 + nl + 10] + text.ljust(4, b"\0") + entry[2 + nl + 14:]

    @staticmethod
    def with_hrc(entry, hrc, name=None):
        """The entry using skeleton file `hrc` (e.g. "ZCLA.HRC", 8 chars), renamed to `name`."""
        nl, = struct.unpack_from("<H", entry, 0)
        hrc = hrc.encode("latin-1")
        assert len(hrc) == 8, hrc
        body = entry[2 + nl:2 + nl + 2] + hrc + entry[2 + nl + 10:]
        name = (name.encode("latin-1") if name else entry[2:2 + nl])
        return struct.pack("<H", len(name)) + name + body

    @staticmethod
    def anims(entry):
        """Animation file names of a model entry."""
        nl, = struct.unpack_from("<H", entry, 0)
        o = 2 + nl + 2 + 8 + 4
        na, = struct.unpack_from("<H", entry, o)
        o += 2 + 30
        out = []
        for _ in range(na):
            al, = struct.unpack_from("<H", entry, o)
            out.append(entry[o + 2:o + 2 + al].decode("latin-1"))
            o += 2 + al + 2
        return out

    @staticmethod
    def with_anims(entry, names):
        """The entry with animations `names` appended (each with the unknown
        u16 of its first animation)."""
        nl, = struct.unpack_from("<H", entry, 0)
        o = 2 + nl + 2 + 8 + 4
        na, = struct.unpack_from("<H", entry, o)
        first = o + 2 + 30
        al, = struct.unpack_from("<H", entry, first)
        tail = entry[first + 2 + al:first + 4 + al]
        extra = b"".join(struct.pack("<H", len(n)) + n.encode("latin-1") + tail for n in names)
        return entry[:o] + struct.pack("<H", na + len(names)) + entry[o + 2:] + extra

    def add_from(self, donor, index):
        """Copy model `index` from loader `donor`, rescaled from the donor
        field's scale to this one's (e.g. 650 -> 512), so it is the same size
        relative to the other characters. Returns the new model index."""
        entry = donor.models[index]
        scale = round(self.entry_scale(entry) * self.scale / donor.scale)
        return self.add(self.with_scale(entry, scale))

    def add(self, entry):
        self.models.append(bytes(entry))
        return len(self.models) - 1

    def build(self):
        return (struct.pack("<HHH", self.unknown, len(self.models), self.scale)
                + b"".join(self.models) + self.trailer)

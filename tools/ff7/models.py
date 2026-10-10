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

    def add(self, entry):
        self.models.append(bytes(entry))
        return len(self.models) - 1

    def build(self):
        return (struct.pack("<HHH", self.unknown, len(self.models), self.scale)
                + b"".join(self.models) + self.trailer)

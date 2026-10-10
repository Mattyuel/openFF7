"""Reader/writer for Square's LGP archive format (FF7 PC).

Layout:
  12 bytes  creator ("\\0\\0SQUARESOFT")
  u32       file count
  TOC       count * (name[20], u32 data_offset, u8 check, u16 conflict)
  lookup    30*30 * (u16 first_toc_index (1-based), u16 count)
  u16       conflict table count, then conflict entries
  data      per file: name[20], u32 length, bytes
  terminator "FINAL FANTASY7"
"""
import struct
from collections import OrderedDict

CREATOR = b"\0\0SQUARESOFT"
TERMINATOR = b"FINAL FANTASY7"
TOC_ENTRY = 27
LOOKUP_SIZE = 30 * 30


def _lookup_value(c):
    c = c.lower()
    if c == ".":
        return -1
    if "0" <= c <= "9":
        c = chr(ord(c) + ord("a") - ord("0"))
    elif c == "_":
        c = "k"
    elif c == "-":
        c = "l"
    return ord(c) - ord("a")


def lookup_hash(name):
    """Index into the 30x30 lookup table for a file name."""
    second = _lookup_value(name[1]) + 1 if len(name) > 1 else 0
    return _lookup_value(name[0]) * 30 + second


class LGP:
    """An LGP archive held in memory as an ordered name -> bytes mapping."""

    def __init__(self, files=None, creator=CREATOR, toc_rank=None):
        self.files = OrderedDict(files or ())
        self.creator = creator
        # Original TOC position per name, so unmodified archives rebuild byte-identically.
        self.toc_rank = dict(toc_rank or {})
        # Per-file TOC check byte and the (sometimes differently cased) name in the data header.
        self.check = {}
        self.data_name = {}
        self.toc_name = {}  # raw 20-byte TOC name (may hold junk after the NUL)

    @classmethod
    def read(cls, path):
        with open(path, "rb") as fh:
            buf = fh.read()
        return cls.parse(buf)

    @classmethod
    def parse(cls, buf):
        creator = buf[:12]
        count, = struct.unpack_from("<I", buf, 12)
        entries = []
        for i in range(count):
            o = 16 + i * TOC_ENTRY
            name = buf[o:o + 20].split(b"\0")[0].decode("ascii")
            off, = struct.unpack_from("<I", buf, o + 20)
            check = buf[o + 24]
            raw_name = bytes(buf[o:o + 20])
            conflict, = struct.unpack_from("<H", buf, o + 25)
            if conflict:
                raise NotImplementedError("LGP conflict (directory) entries are not supported")
            entries.append((name, off, check, raw_name))
        toc_rank = {e[0]: i for i, e in enumerate(entries)}
        # Keep files in data order so a rewrite preserves the original layout.
        entries.sort(key=lambda e: e[1])
        files = OrderedDict()
        check, data_name, toc_name = {}, {}, {}
        for name, off, chk, raw_name in entries:
            toc_name[name] = raw_name
            size, = struct.unpack_from("<I", buf, off + 20)
            files[name] = bytes(buf[off + 24:off + 24 + size])
            check[name] = chk
            data_name[name] = bytes(buf[off:off + 20])
        archive = cls(files, creator, toc_rank)
        archive.check = check
        archive.data_name = data_name
        archive.toc_name = toc_name
        return archive

    def names(self):
        return list(self.files)

    def __getitem__(self, name):
        return self.files[name]

    def __setitem__(self, name, data):
        self.files[name] = bytes(data)

    def __contains__(self, name):
        return name in self.files

    def build(self):
        names = list(self.files)
        count = len(names)
        # TOC is grouped by lookup hash; data keeps insertion order.
        new_rank = len(self.toc_rank)
        toc_order = sorted(range(count), key=lambda i: (
            lookup_hash(names[i]), self.toc_rank.get(names[i], new_rank), names[i].lower()))
        header_size = 16 + count * TOC_ENTRY + LOOKUP_SIZE * 4 + 2
        offsets = {}
        pos = header_size
        for name in names:
            offsets[name] = pos
            pos += 24 + len(self.files[name])

        out = bytearray(self.creator)
        out += struct.pack("<I", count)
        lookup = [[0, 0] for _ in range(LOOKUP_SIZE)]
        for toc_index, i in enumerate(toc_order):
            name = names[i]
            raw = name.encode("ascii")
            if len(raw) > 20:
                raise ValueError("LGP file name too long: %s" % name)
            out += self.toc_name.get(name) or raw.ljust(20, b"\0")
            out += struct.pack("<IBH", offsets[name], self.check.get(name, 14), 0)
            h = lookup_hash(name)
            if lookup[h][1] == 0:
                lookup[h][0] = toc_index + 1
            lookup[h][1] += 1
        for first, n in lookup:
            out += struct.pack("<HH", first, n)
        out += struct.pack("<H", 0)  # no conflicts
        assert len(out) == header_size
        for name in names:
            data = self.files[name]
            out += self.data_name.get(name) or name.encode("ascii").ljust(20, b"\0")
            out += struct.pack("<I", len(data))
            out += data
        out += TERMINATOR
        return bytes(out)

    def write(self, path):
        with open(path, "wb") as fh:
            fh.write(self.build())

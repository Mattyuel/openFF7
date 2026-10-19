"""Field background (section 8, PC): tile layers + texture pages.

  u16 0, u16 depth, u8 enabled, "PALETTE", u8 ignore_first_pixel[24], u32 0
  "BACK"
  layer 1: u16 width, height, n_tiles, depth; u16 0; Tile[n]; u16 0
  layers 2-4: u8 exists; if exists: u16 width, height, n_tiles; u8 header[k]
              (k = 16 for layer 2, 10 for layers 3 and 4); u16 0; Tile[n]; u16 0
  "TEXTURE"
  42 pages: u16 exists; if exists: u16 size, u16 bytes_per_pixel (1 = 8-bit
            paletted, 2 = 16-bit), 256 * 256 * bytes_per_pixel pixel bytes
  "END"

Tile (52 bytes): +2 s16 dst x, +4 s16 dst y, +10 u8 src x, +12 u8 src y,
+14 u8 src x2, +16 u8 src y2, +18 u16 width, +20 u16 height, +22 palette,
+24 u16 id (draw order), +26 param, +27 state, +28 blending, +30 type,
+32 u8 texture page, +34 u8 texture page 2, +36 depth, +38..+49 u32 x3
(PC "big" id / src), +50 u16 0.
"""
import struct

TILE = 52
LAYER_HEADER = {2: 16, 3: 10, 4: 10}
PAGES = 42


class Tile:
    def __init__(self, raw):
        self.raw = bytearray(raw)

    def _get(self, fmt, off):
        return struct.unpack_from(fmt, self.raw, off)[0]

    def _set(self, fmt, off, v):
        struct.pack_into(fmt, self.raw, off, v)

    dst_x = property(lambda s: s._get("<h", 2), lambda s, v: s._set("<h", 2, v))
    dst_y = property(lambda s: s._get("<h", 4))
    src_x = property(lambda s: s.raw[10])
    src_y = property(lambda s: s.raw[12])
    src_x2 = property(lambda s: s.raw[14])
    src_y2 = property(lambda s: s.raw[16])
    # layer 1 tiles store 0: the default 16 x 16
    width = property(lambda s: s._get("<H", 18) or 16)
    height = property(lambda s: s._get("<H", 20) or 16)
    blending = property(lambda s: s.raw[28])
    page = property(lambda s: s.raw[32])
    page2 = property(lambda s: s.raw[34])


class Background:
    def __init__(self, data):
        data = bytes(data)
        self.head = data[:36]                      # up to "BACK"
        assert data[5:12] == b"PALETTE" and data[36:40] == b"BACK", "not a PC background"
        p = 40
        self.layers = []                           # (number, header bytes, tiles, tail bytes)
        w, h, n, depth = struct.unpack_from("<4H", data, p)
        hdr = data[p:p + 10]
        p += 10
        tiles = [Tile(data[p + i * TILE:p + (i + 1) * TILE]) for i in range(n)]
        p += n * TILE
        self.layers.append((1, hdr, tiles, data[p:p + 2]))
        p += 2
        for k in (2, 3, 4):
            exists = data[p]
            if not exists:
                self.layers.append((k, data[p:p + 1], None, b""))
                p += 1
                continue
            n, = struct.unpack_from("<H", data, p + 5)
            hlen = 1 + 6 + LAYER_HEADER[k] + 2
            hdr = data[p:p + hlen]
            p += hlen
            tiles = [Tile(data[p + i * TILE:p + (i + 1) * TILE]) for i in range(n)]
            p += n * TILE
            self.layers.append((k, hdr, tiles, data[p:p + 2]))
            p += 2
        assert data[p:p + 7] == b"TEXTURE", ("layer parse ended at", p)
        p += 7
        self.pages = []                            # None or [size, bpp, bytearray]
        for _ in range(PAGES):
            exists, = struct.unpack_from("<H", data, p)
            p += 2
            if not exists:
                self.pages.append(None)
                continue
            size, bpp = struct.unpack_from("<HH", data, p)
            p += 4
            self.pages.append([size, bpp, bytearray(data[p:p + 65536 * bpp])])
            p += 65536 * bpp
        self.tail = data[p:]
        assert self.tail[:3] == b"END", self.tail[:8]

    def tiles(self):
        return [t for _, _, ts, _ in self.layers if ts for t in ts]

    def build(self):
        out = bytearray(self.head) + b"BACK"
        for k, hdr, tiles, tail in self.layers:
            out += hdr
            if tiles is not None:
                for t in tiles:
                    out += t.raw
                out += tail
        out += b"TEXTURE"
        for pg in self.pages:
            if pg is None:
                out += b"\0\0"
            else:
                out += struct.pack("<HHH", 1, pg[0], pg[1]) + pg[2]
        return bytes(out + self.tail)

    def flip_horizontal(self):
        """Mirror the picture left-right about the screen centre (x = 0):
        each tile's destination is mirrored and the texture area it reads is
        flipped in place (each distinct area once)."""
        done = set()

        def flip(page, sx, sy, w, h):
            key = (page, sx, sy, w, h)
            if key in done:
                return
            done.add(key)
            size, bpp, px = self.pages[page]
            for y in range(sy, sy + h):
                row = y * 256 * bpp
                a, b = row + sx * bpp, row + (sx + w) * bpp
                pixels = [px[i:i + bpp] for i in range(a, b, bpp)]
                px[a:b] = b"".join(reversed(pixels))

        areas = {}
        for t in self.tiles():
            for page, sx, sy in ((t.page, t.src_x, t.src_y),) + (((t.page2, t.src_x2, t.src_y2),) if t.blending else ()):
                if self.pages[page] is None:
                    continue
                areas.setdefault((page, sx, sy), set()).add((t.width, t.height))
        for (page, sx, sy), sizes in areas.items():
            assert len(sizes) == 1, ("one texture area read with two tile sizes", page, sx, sy, sizes)
        # areas must not partially overlap (a pixel flipped twice would come back)
        cover = {}
        for (page, sx, sy), sizes in areas.items():
            w, h = next(iter(sizes))
            for y in range(sy, sy + h):
                for x in range(sx, sx + w):
                    prev = cover.setdefault((page, x, y), (sx, sy))
                    assert prev == (sx, sy), ("overlapping texture areas", page, prev, (sx, sy))
        for (page, sx, sy), sizes in areas.items():
            w, h = next(iter(sizes))
            flip(page, sx, sy, w, h)
        for t in self.tiles():
            t.dst_x = -t.dst_x - t.width

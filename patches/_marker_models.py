"""Quest marker models: battle-effect sprites shown in the field.

The markers are field models in char.lgp built here: one bone (the Glacier
Map prop's skeleton gujc.hrc and its animation GVAA, both static), whose
mesh is two crossed quads (each double-sided) textured with a sprite from
battle/magic.lgp:
  QSTA  star  (magic.lgp s_guard.tex, the S-Guard star): quest to offer
  QHTA  heart (magic.lgp heart01.tex, Lucky Girl's heart): quest accepted
The sprite textures are 64x64, 16 colours; the colour key is switched on so
black is transparent (s_guard already has it; heart01 doesn't).

.p layout (PC field model, checked against char.lgp's guje.p / byid.p):
128-byte header (16 u32 counts + 64 runtime bytes), vertices (3f), normals
(3f), texcoords (2f), vertex colours, polygon colours, edges (2 u16),
polygons (12 u16: tag, 3 vertices, 3 normals, 3 edges, 2 tags), hundrets
(100-byte render states), groups (14 u32), bounding box (u32 + 6f), then a
u32 normal index per vertex.
"""
import struct

DONOR_P = "guje.p"              # the Glacier Map's single textured quad
DONOR_HRC, DONOR_FIELD, DONOR_MODEL = b"GUJC.HRC", "snmin2", 7
HALF = 3.0                      # half size of the sprite's longer side (the orb was ~2.3)
TEX_SIZE = 64

MODELS = {   # hrc name: (rsd, p, tex, magic.lgp texture, sprite pixels x0, y0, x1, y1 inclusive)
    # The star fills only a corner of its texture and the heart nearly all of
    # its own: each quad is cropped to its sprite, so both show the same size.
    "QSTA": ("QSTB", "QSTC", "QSTD", "s_guard.tex", (8, 8, 38, 39)),
    "QHTA": ("QHTB", "QHTC", "QHTD", "heart01.tex", (2, 7, 61, 57)),
}


def magic_file(game_dir, name):
    """A file from battle/magic.lgp (it has directory entries, which ff7.lgp
    doesn't parse; names are unique enough for the sprites used here)."""
    import os
    d = open(os.path.join(game_dir, "battle", "magic.lgp"), "rb").read()
    count, = struct.unpack_from("<I", d, 12)
    for i in range(count):
        o = 16 + i * 27
        if d[o:o + 20].split(b"\0")[0].decode("latin1").lower() == name:
            off, = struct.unpack_from("<I", d, o + 20)
            size, = struct.unpack_from("<I", d, off + 20)
            return d[off + 24:off + 24 + size]
    raise KeyError(name)


def keyed(tex):
    """The texture with its colour key on (black = transparent), as s_guard's,
    and palette entry 0 (the background: heart01's is 01 01 01) pure black."""
    t = bytearray(tex)
    struct.pack_into("<II", t, 8, 1, 1)
    t[0xEC:0xEC + 4] = b"\0\0\0\0"
    return bytes(t)


def mesh(donor, crop):
    """Two crossed, double-sided quads (planes x-y and z-y), using the donor
    quad's render state (hundret) and polygon tags."""
    h = struct.unpack_from("<16I", donor, 0)
    nv, nn, nt, nc, ne, npoly, nh = h[3], h[4], h[6], h[7], h[8], h[9], h[12]
    assert (nv, nn, nt, npoly, nh, h[13], h[14]) == (4, 1, 4, 2, 1, 1, 1), h
    o = 128 + 12 * nv + 12 * nn + 8 * nt + 4 * nc + 4 * npoly + 4 * ne
    tags = struct.unpack_from("<12H", donor, o)[10:12]
    o += 24 * npoly + 24 * h[10] + 3 * h[11]
    hundret = donor[o:o + 100]

    x0, y0, x1, y1 = crop
    w, hgt = x1 + 1 - x0, y1 + 1 - y0
    sx, sy = HALF * w / max(w, hgt), HALF * hgt / max(w, hgt)
    u0, v0, u1, v1 = x0 / TEX_SIZE, y0 / TEX_SIZE, (x1 + 1) / TEX_SIZE, (y1 + 1) / TEX_SIZE
    verts = [(-sx, -sy, 0), (sx, -sy, 0), (-sx, sy, 0), (sx, sy, 0),        # quad A (faces z); -y is up
             (0, -sy, -sx), (0, -sy, sx), (0, sy, -sx), (0, sy, sx)]        # quad B (faces x)
    uvs = [(u0, v0), (u1, v0), (u0, v1), (u1, v1)] * 2
    tris = []
    for b in (0, 4):
        a, c, d, e = b, b + 1, b + 2, b + 3
        tris += [(a, c, d), (c, e, d), (a, d, c), (c, d, e)]       # front + back
    normals = [(0.0, 0.0, 1.0)]
    edges = [(0, 1)]
    n_v, n_p = len(verts), len(tris)

    out = bytearray(struct.pack("<16I", 1, 1, 1, n_v, len(normals), 0, n_v, n_v,
                                len(edges), n_p, 0, 0, 1, 1, 1, 1))
    out += donor[64:128]                                            # runtime header bytes
    out += b"".join(struct.pack("<3f", *v) for v in verts)
    out += b"".join(struct.pack("<3f", *n) for n in normals)
    out += b"".join(struct.pack("<2f", *t) for t in uvs)
    out += b"\xff\xff\xff\xff" * n_v                                # vertex colours
    out += b"\xff\xff\xff\xff" * n_p                                # polygon colours
    out += b"".join(struct.pack("<2H", *e) for e in edges)
    out += b"".join(struct.pack("<12H", 0, *t, 0, 0, 0, 0, 0, 0, *tags) for t in tris)
    out += hundret
    out += struct.pack("<14I", 2, 0, n_p, 0, n_v, 0, 0, 0, 0, 0, 0, 0, 1, 0)
    m = max(sx, sy)
    out += struct.pack("<I6f", 0, m, sy, m, -m, -sy, -m)
    out += b"\0\0\0\0" * n_v                                        # normal index table
    return bytes(out)


def install(ctx, game_dir):
    """Add both marker models to char.lgp. Returns {hrc: model loader entry}
    (copies of the Glacier Map's entry pointing at the new skeleton)."""
    from ff7.models import ModelLoader
    donor_p = ctx.char_file(DONOR_P)
    hrc_text = ctx.char_file("gujc.hrc").decode("latin1")
    assert "1 GUJD" in hrc_text, hrc_text
    entries = {}
    donor_entry = ModelLoader(ctx.field(DONOR_FIELD).section("models")).models[DONOR_MODEL]
    assert DONOR_HRC in donor_entry
    for hrc, (rsd, ply, tex, sprite, crop) in MODELS.items():
        ctx.char_file(hrc.lower() + ".hrc",
                      hrc_text.replace("icemap_sk", hrc.lower() + "_sk").replace("1 GUJD", "1 " + rsd).encode("latin1"))
        ctx.char_file(rsd.lower() + ".rsd",
                      ("@RSD940102\r\nPLY=%s.PLY\r\nMAT=%s.MAT\r\nGRP=%s.GRP\r\nNTEX=1\r\nTEX[0]=%s.TIM\r\n"
                       % (ply, ply, ply, tex)).encode("latin1"))
        ctx.char_file(ply.lower() + ".p", mesh(donor_p, crop))
        ctx.char_file(tex.lower() + ".tex", keyed(magic_file(game_dir, sprite)))
        entries[hrc] = donor_entry.replace(DONOR_HRC, (hrc + ".HRC").encode("ascii"))
    return entries

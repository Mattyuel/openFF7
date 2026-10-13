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
TEX_TEMPLATE = "aabb.tex"       # a field texture: 4-bit, 16 colours, colour key on

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


def keyed(sprite, template):
    """The sprite as a field texture: header copied from a char.lgp field
    texture of the same kind (`template`: 4-bit, 16 colours, colour key on;
    field models crashed the game with the battle texture's own header) with
    the sprite's size, then its palette (entry 0, the background, pure black =
    transparent) and pixels."""
    w, h = struct.unpack_from("<II", sprite, 0x3C)
    ncol, = struct.unpack_from("<I", sprite, 0x58)
    t = struct.unpack_from("<27I", template, 0)
    assert (t[2], t[3], t[12], t[13], t[14], t[22], t[26]) == (1, 1, 1, 16, 4, 16, 1), t
    assert ncol == 16 and len(sprite) == 0xEC + 4 * ncol + w * h, (ncol, len(sprite))
    head = bytearray(template[:0xEC])
    struct.pack_into("<II", head, 0x3C, w, h)
    pal = bytearray(sprite[0xEC:0xEC + 4 * ncol])
    pal[0:4] = b"\0\0\0\0"
    for i in range(1, ncol):        # opaque: s_guard's colours have alpha 0xFE (the PSX semi-transparency
        pal[4 * i + 3] = 0xFF       # bit), which showed the star for a moment and then blended it away
    return bytes(head) + bytes(pal) + sprite[0xEC + 4 * ncol:]


def mesh(donor, crop, half=HALF):
    """`half`: half size of the longer side. The donor quad (4 vertices, 5 edges, 2 triangles: same layout as every
    other part of the file) with our size and texture crop, plus the same two
    triangles reversed so it shows from both sides."""
    h = list(struct.unpack_from("<16I", donor, 0))
    nv, nn, nunk, nt, nc, ne, npoly, nh = h[3], h[4], h[5], h[6], h[7], h[8], h[9], h[12]
    assert (nv, nn, nunk, nt, nc, ne, npoly, h[10], h[11], nh, h[13]) == (4, 1, 0, 4, 4, 5, 2, 0, 0, 1, 1), h
    o_v = 128
    o_t = o_v + 12 * nv + 12 * nn
    o_c = o_t + 8 * nt
    o_pc = o_c + 4 * nc
    o_e = o_pc + 4 * npoly
    o_p = o_e + 4 * ne
    o_h = o_p + 24 * npoly
    o_g = o_h + 100 * nh
    o_b = o_g + 56
    polys = [list(struct.unpack_from("<12H", donor, o_p + 24 * i)) for i in range(npoly)]
    assert [p[1:4] for p in polys] == [[0, 1, 2], [1, 3, 2]], polys

    x0, y0, x1, y1 = crop
    w, hgt = x1 + 1 - x0, y1 + 1 - y0
    sx, sy = half * w / max(w, hgt), half * hgt / max(w, hgt)
    u0, v0, u1, v1 = x0 / TEX_SIZE, y0 / TEX_SIZE, (x1 + 1) / TEX_SIZE, (y1 + 1) / TEX_SIZE
    verts = [(-sx, -sy, 0), (sx, -sy, 0), (-sx, sy, 0), (sx, sy, 0)]   # as the donor's order; -y is up
    uvs = [(u0, v0), (u1, v0), (u0, v1), (u1, v1)]
    back = []
    for p in polys:                     # reversed winding, edges reversed with it
        q = list(p)
        q[1:4] = [p[1], p[3], p[2]]
        q[4:7] = [p[4], p[6], p[5]]
        q[7:10] = [p[9], p[8], p[7]]
        back.append(q)
    out = bytearray(donor[:o_p])
    struct.pack_into("<16I", out, 0, *(h[:9] + [npoly * 2] + h[10:]))
    for i, v in enumerate(verts):
        struct.pack_into("<3f", out, o_v + 12 * i, *v)
    for i, uv in enumerate(uvs):
        struct.pack_into("<2f", out, o_t + 8 * i, *uv)
    out[o_pc:o_pc + 4 * npoly] = donor[o_pc:o_pc + 4 * npoly]
    out[o_pc + 4 * npoly:o_pc + 4 * npoly] = donor[o_pc:o_pc + 4 * npoly]      # colours for the back faces
    out += b"".join(struct.pack("<12H", *p) for p in polys + back)
    out += donor[o_h:o_g]                                                      # hundret
    g = list(struct.unpack_from("<14I", donor, o_g))
    assert g[1:5] == [0, npoly, 0, nv], g
    g[2] = npoly * 2
    out += struct.pack("<14I", *g)
    out += struct.pack("<I6f", 0, sx, sy, sx, -sx, -sy, -sx)
    out += donor[o_b + 28:]                                                    # normal index table
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
        ctx.char_file(tex.lower() + ".tex", keyed(magic_file(game_dir, sprite), ctx.char_file(TEX_TEMPLATE)))
        entries[hrc] = donor_entry.replace(DONOR_HRC, (hrc + ".HRC").encode("ascii"))
    return entries

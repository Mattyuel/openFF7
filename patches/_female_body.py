"""The standard female body (user): Skye's bare body from the neck down, built by
670_movie (`_bare_skye`: torso and pelvis `_skye_shape`, legs `_skye_limbs`, arms
`_smooth_arms`), as the body for other women too: they keep their own head and feet.

`apply(ctx, hrc, tag)` takes another woman's .hrc text and returns it with the standard
body's parts on her body bones (BODY: pelvis, torso, upper / lower arms, hands, thighs,
shins). Her skeleton may differ from Skye's: each part is stretched along its bone by her
bone's length / Skye's (so it still reaches the next joint; the torso by her shoulder bone's,
and her chest bone shortened to match, so her head sits on it) and scaled across by her
figure's size (the sum of her hip, chest, thigh and shin bones / Skye's); a part that needs
no change is shared, the others are written as new parts "ZW<tag><letter>" (.rsd) /
"ZX<tag><letter>" (.p), tag = one letter per woman (keep a list here). skin = her skin
colour (B, G, R) for the body's skin (Skye's SKIN) if given. Use it only from patches that
run after 670 (the standard body is built there).

Tags in use: R Ruby (ZRHA), E Elena (ZELA), S Scarlet (ZSCA), T Tifa (ZTFA) (675)
"""
import importlib
import struct

STANDARD = "ZSKA.HRC"
BODY = ("hip", "chest", "l_uparm", "l_foarm", "l_hand", "r_uparm", "r_foarm", "r_hand",
        "l_femur", "l_tibia", "r_femur", "r_tibia")
FIGURE = ("hip", "chest", "l_femur", "l_tibia")
SKIN = (166, 194, 247)
SOLE = 0.35                    # the shin's part reaches at most this far past her ankle (user:
                               # Skye's ran ~0.9 into her heel, through Elena's soles)


def _hb():
    return importlib.import_module("620_honey_bee")


def _part(d):
    """(vertices, triangles, vertex colours) of a one-group untextured .p."""
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nu, nt, nc, ne, npoly = h[3], h[4], h[5], h[6], h[7], h[8], h[9]
    V = [list(struct.unpack_from("<3f", d, 128 + 12 * i)) for i in range(nv)]
    oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
    C = [tuple(d[oc + 4 * i:oc + 4 * i + 3]) for i in range(nc)]
    op = oc + 4 * nc + 4 * npoly + 4 * ne
    P = [struct.unpack_from("<12H", d, op + 24 * j)[1:4] for j in range(npoly)]
    return V, P, C


def _banded(d, bands, length):
    """.p bytes d recoloured in bands down the bone (Scarlet's stockings): bands = [(t, colour)]
    from the top, t = the band's start as a fraction of the bone `length` down from the joint
    (the first band's t is ignored); the mesh is cut at each band edge (triangles split, the
    cut's points doubled), so the colours change sharply as on her own legs."""
    V, P, _ = _part(d)
    cuts = [-t * length for t, _ in bands[1:]]
    band = lambda z: sum(1 for c in cuts if z < c)          # 0 = the top band
    tag = [band(v[2]) for v in V]
    for c in cuts:
        k_above = band(c + 1e-6)
        new_p, made = [], {}

        def cut(a, b, side):                                  # the point where edge a-b crosses z = c
            key = (min(a, b), max(a, b), side)
            if key not in made:
                pa, pb = V[a], V[b]
                f = (c - pa[2]) / (pb[2] - pa[2])
                V.append([pa[k] + f * (pb[k] - pa[k]) for k in range(3)])
                tag.append(k_above if side else k_above + 1)
                made[key] = len(V) - 1
            return made[key]
        for t in P:
            up = [V[i][2] > c for i in t]
            if all(up) or not any(up):
                new_p.append(t)
                continue
            for side in (True, False):                        # each side's polygon, in the triangle's order
                poly = []
                for j in range(3):
                    a, b = t[j], t[(j + 1) % 3]
                    if up[j] == side:
                        poly.append(a)
                    if up[j] != up[(j + 1) % 3]:
                        poly.append(cut(a, b, side))
                new_p += [(poly[0], poly[q], poly[q + 1]) for q in range(1, len(poly) - 1)]
        P = new_p
    h = struct.unpack_from("<16I", d, 0)
    op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
    return _hb()._p_file(V, P, [bands[k][1] for k in tag], d[64:128], struct.unpack_from("<12H", d, op)[10:12])


def bones(hrc):
    """{bone name: (length, [rsd names], parent)} in an .hrc text."""
    lines = [l.strip() for l in hrc.splitlines()]
    k = lines.index(next(l for l in lines if l.startswith(":BONES"))) + 1
    out = {}
    while k < len(lines):
        if not lines[k]:
            k += 1
            continue
        name, length, parts = lines[k], float(lines[k + 2]), lines[k + 3].split()
        out[name] = (length, parts[1:], lines[k + 1])
        k += 4
    return out


def _scaled(d, sxy, sz, skin, sole=None):
    """A copy of .p bytes d: vertices (x, y) x sxy, z (along the bone) x sz, normals kept;
    the standard skin colour -> skin; sole = (bone length): what reaches past the bone's end
    squeezed to at most SOLE past it (the shin into her foot)."""
    d = bytearray(d)
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nu, nt, nc, npoly = h[3], h[4], h[5], h[6], h[7], h[9]
    zs = [struct.unpack_from("<3f", d, 128 + 12 * i)[2] * sz for i in range(nv)]
    over = max(0.0, -min(zs) - sole) if sole else 0.0
    for i in range(nv):
        x, y, z = struct.unpack_from("<3f", d, 128 + 12 * i)
        z *= sz
        if over > SOLE and z < -sole:
            z = -sole - (-sole - z) * SOLE / over
        struct.pack_into("<3f", d, 128 + 12 * i, x * sxy, y * sxy, z)
    if skin:
        oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
        for o in [oc + 4 * i for i in range(nc)] + [oc + 4 * nc + 4 * j for j in range(npoly)]:
            if tuple(d[o:o + 3]) == SKIN:
                d[o:o + 3] = bytes(skin)
    return bytes(d)


def apply(ctx, hrc, tag, skin=None, legs=None):
    """See the module. legs = {"femur": bands, "tibia": bands} (see `_banded`): her legs'
    colours (Scarlet's stockings)."""
    assert len(tag) == 1 and tag.isalpha(), tag
    std = bones(ctx.char_file(STANDARD.lower()).decode("latin-1"))
    her = bones(hrc)
    # the torso: scaled by her shoulder height (the bone from the hip to her left collar), not her
    # chest bone, whose end (her head) may sit much higher (Elena 6.1 vs 4.74: the torso's
    # shoulders rose far above her arms, user); her chest bone is shortened to match, so her
    # head sits on the torso (anims hold rotations only)
    shoulder = lambda bs: next(n for n, v in bs.items() if v[2] == "hip" and bs.get("l_collar", (0, 0, ""))[2] == n)
    lengths = {b: her[b][0] for b in BODY}
    lengths["chest"] = std["chest"][0] * her[shoulder(her)][0] / std[shoulder(std)][0]
    fig = sum(lengths[b] for b in FIGURE) / sum(std[b][0] for b in FIGURE)
    n = 0
    lines = hrc.splitlines(True)
    for b in BODY:
        assert b in her, (b, "not in her skeleton")
        assert len(std[b][1]) == 1 and len(her[b][1]) == 1, (b, std[b][1], her[b][1])
        sz = lengths[b] / std[b][0]
        rsd = std[b][1][0]
        if True:                                       # (every woman gets her own copies: shin / colours)
            r = ctx.char_file(rsd.lower() + ".rsd").decode("latin-1")
            ply = r.split("PLY=")[1][:4]
            new_r, new_p = "ZW" + tag.upper() + chr(65 + n), "ZX" + tag.upper() + chr(65 + n)
            n += 1
            ctx.char_file(new_r.lower() + ".rsd", r.replace("PLY=%s." % ply, "PLY=%s." % new_p).encode("latin-1"))
            part = _scaled(ctx.char_file(ply.lower() + ".p"), fig, sz, skin, lengths[b] if b.endswith("tibia") else None)
            if legs and b[2:] in legs:
                part = _banded(part, legs[b[2:]], lengths[b])
            ctx.char_file(new_p.lower() + ".p", part)
            rsd = new_r
        # her bone's part line (the line after the bone's name, parent and length)
        i = next(k for k in range(len(lines) - 3) if lines[k].strip() == b and
                 lines[k + 3].strip() == "1 %s" % her[b][1][0])
        lines[i + 3] = lines[i + 3].replace(her[b][1][0], rsd)
        if lengths[b] != her[b][0]:
            lines[i + 2] = lines[i + 2].replace(lines[i + 2].strip(), "%.6f" % lengths[b])
    return "".join(lines)

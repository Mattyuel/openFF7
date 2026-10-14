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

Tags in use: (none yet)
"""
import struct

STANDARD = "ZSKA.HRC"
BODY = ("hip", "chest", "l_uparm", "l_foarm", "l_hand", "r_uparm", "r_foarm", "r_hand",
        "l_femur", "l_tibia", "r_femur", "r_tibia")
FIGURE = ("hip", "chest", "l_femur", "l_tibia")
SKIN = (166, 194, 247)


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


def _scaled(d, sxy, sz, skin):
    """A copy of .p bytes d: vertices (x, y) x sxy, z (along the bone) x sz, normals kept;
    the standard skin colour -> skin."""
    d = bytearray(d)
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nu, nt, nc, npoly = h[3], h[4], h[5], h[6], h[7], h[9]
    for i in range(nv):
        x, y, z = struct.unpack_from("<3f", d, 128 + 12 * i)
        struct.pack_into("<3f", d, 128 + 12 * i, x * sxy, y * sxy, z * sz)
    if skin:
        oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
        for o in [oc + 4 * i for i in range(nc)] + [oc + 4 * nc + 4 * j for j in range(npoly)]:
            if tuple(d[o:o + 3]) == SKIN:
                d[o:o + 3] = bytes(skin)
    return bytes(d)


def apply(ctx, hrc, tag, skin=None):
    assert len(tag) == 1 and tag.isalpha(), tag
    std = bones(ctx.char_file(STANDARD).decode("latin-1"))
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
        if abs(sz - 1) > 0.01 or abs(fig - 1) > 0.01 or skin:
            r = ctx.char_file(rsd.lower() + ".rsd").decode("latin-1")
            ply = r.split("PLY=")[1][:4]
            new_r, new_p = "ZW" + tag.upper() + chr(65 + n), "ZX" + tag.upper() + chr(65 + n)
            n += 1
            ctx.char_file(new_r.lower() + ".rsd", r.replace("PLY=%s." % ply, "PLY=%s." % new_p).encode("latin-1"))
            ctx.char_file(new_p.lower() + ".p", _scaled(ctx.char_file(ply.lower() + ".p"), fig, sz, skin))
            rsd = new_r
        # her bone's part line (the line after the bone's name, parent and length)
        i = next(k for k in range(len(lines) - 3) if lines[k].strip() == b and
                 lines[k + 3].strip() == "1 %s" % her[b][1][0])
        lines[i + 3] = lines[i + 3].replace(her[b][1][0], rsd)
        if lengths[b] != her[b][0]:
            lines[i + 2] = lines[i + 2].replace(lines[i + 2].strip(), "%.6f" % lengths[b])
    return "".join(lines)

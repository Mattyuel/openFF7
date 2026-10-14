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

Tags in use: R Ruby (ZRHA), E Elena (ZELA), S Scarlet (ZSCA), T Tifa (ZTFA), H the Honey Bee girls (ZHBA, the dancer BADD) (675)
"""
import importlib
import struct

STANDARD = "ZSKA.HRC"
BODY = ("hip", "chest", "l_uparm", "l_foarm", "l_hand", "r_uparm", "r_foarm", "r_hand",
        "l_femur", "l_tibia", "r_femur", "r_tibia")
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


TORSO_BONES = ("hip", "chest", "l_hip", "r_hip", "l_collar", "r_collar")     # + both shoulder bones (found)
LIMBS = ("l_femur", "l_tibia", "l_uparm", "l_foarm")
COLLAR_R, COLLAR_N = 0.85, 6   # the shoulder bridge: radius (x her figure), points a ring
NECK_R, NECK_FROM, NECK_TO = 0.55, 0.85, 0.35   # the neck: radius (x figure), from this fraction of the
                                                # chest bone (inside the torso's top) to this far past its end


def _bar(z0, z1, tip0, tip1, r, n, bgr, tail, poly_tail):
    """A rounded bar along a bone (local -z): rings of radius r at z0 and z1, pointed to tip0 /
    tip1 beyond them. The shoulder bridge on each collar bone (it moves with the shoulder and
    joins the torso and the arm's top in any pose: Scarlet's own stance pulls her shoulders
    back, behind the torso, user) and the neck on the chest bone (from inside the torso's top
    into the head: Tifa's neck stopped short of it, user)."""
    import math
    V, tris = [], []
    for z in (z0, z1):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5) / n
            V.append([r * math.cos(a), r * math.sin(a), z])
    for k in range(n):
        a, b = k, (k + 1) % n
        tris += [(a, b, b + n), (a, b + n, a + n)]
    V += [[0.0, 0.0, tip0], [0.0, 0.0, tip1]]
    tris += [(k, (k + 1) % n, len(V) - 2) for k in range(n)]
    tris += [(n + k, n + (k + 1) % n, len(V) - 1) for k in range(n)]
    return _hb()._p_file(V, tris, bgr, tail, poly_tail)


def face_skin(ctx, hrc):
    """Her face's skin colour (B, G, R): the head part's most common skin-like vertex colour
    (faces are vertex-coloured; their textures only hold eyes and mouth)."""
    rsd = bones(hrc)["head"][1][0]
    d = ctx.char_file(ctx.char_file(rsd.lower() + ".rsd").decode("latin-1").split("PLY=")[1][:4].lower() + ".p")
    _, _, C = _part(d)
    skinlike = [c for c in C if c[2] > 180 and 0.6 < c[1] / c[2] < 0.88 and 0.45 < c[0] / c[2] < 0.78]
    assert skinlike, rsd
    return max(set(skinlike), key=skinlike.count)


def apply(ctx, hrc, tag, skin=None, legs=None):
    """See the module. legs = {"femur": bands, "tibia": bands} (see `_banded`): her legs'
    colours (Scarlet's stockings). Her torso bones (pelvis, chest, both shoulder and collar
    bones, the hip joints) are set to the standard's x her figure (user: Tifa's long pelvis
    bone stretched the pelvis and her neck floated; Elena's long chest bone lifted the torso's
    shoulders above her arms); her arm and leg bones stay hers. Figure = her limbs (thigh,
    shin, upper arm, forearm) / the standard's."""
    assert len(tag) == 1 and tag.isalpha(), tag
    std = bones(ctx.char_file(STANDARD.lower()).decode("latin-1"))
    her = bones(hrc)
    fig = sum(her[b][0] for b in LIMBS) / sum(std[b][0] for b in LIMBS)
    side = lambda bs, s_: bs[s_ + "_collar"][2]            # the shoulder bone: the collar's parent
    torso = {b: b for b in TORSO_BONES}
    torso.update({side(her, s_): side(std, s_) for s_ in "lr"})
    lengths = {b: her[b][0] for b in her}
    for hb_, sb in torso.items():
        lengths[hb_] = std[sb][0] * fig
    skin_c = skin or SKIN
    lines = hrc.splitlines(True)
    n = 0

    def at(b):                                            # her bone's name line
        return next(k for k in range(len(lines) - 3) if lines[k].strip() == b and lines[k + 1].strip() == her[b][2])

    def new_names():
        nonlocal n
        r_, p_ = "ZW" + tag.upper() + chr(65 + n), "ZX" + tag.upper() + chr(65 + n)
        n += 1
        return r_, p_
    for b in BODY:
        assert b in her, (b, "not in her skeleton")
        assert len(std[b][1]) == 1 and len(her[b][1]) == 1, (b, std[b][1], her[b][1])
        sz = lengths[b] / std[b][0]
        r = ctx.char_file(std[b][1][0].lower() + ".rsd").decode("latin-1")
        ply = r.split("PLY=")[1][:4]
        new_r, new_p = new_names()
        ctx.char_file(new_r.lower() + ".rsd", r.replace("PLY=%s." % ply, "PLY=%s." % new_p).encode("latin-1"))
        part = _scaled(ctx.char_file(ply.lower() + ".p"), fig, sz, skin, lengths[b] if b.endswith("tibia") else None)
        if legs and b[2:] in legs:
            part = _banded(part, legs[b[2:]], lengths[b])
        ctx.char_file(new_p.lower() + ".p", part)
        i = at(b)
        lines[i + 3] = lines[i + 3].replace(her[b][1][0], new_r)
    for b in her:                                          # her torso bones' lengths
        if abs(lengths[b] - her[b][0]) > 1e-6:
            i = at(b)
            lines[i + 2] = lines[i + 2].replace(lines[i + 2].strip(), "%.6f" % lengths[b])
    tmpl_r = ctx.char_file(std["l_uparm"][1][0].lower() + ".rsd").decode("latin-1")
    tmpl_p = ctx.char_file(tmpl_r.split("PLY=")[1][:4].lower() + ".p")
    for s_ in "lr":                                        # the shoulder bridges
        b = s_ + "_collar"
        assert her[b][1] == [], (b, her[b][1])
        new_r, new_p = new_names()
        ctx.char_file(new_r.lower() + ".rsd", tmpl_r.replace("PLY=%s." % tmpl_r.split("PLY=")[1][:4], "PLY=%s." % new_p).encode("latin-1"))
        h = struct.unpack_from("<16I", tmpl_p, 0)
        op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
        L = lengths[b]
        ctx.char_file(new_p.lower() + ".p", _bar(-0.1 * L, -0.9 * L, 0.35 * L, -1.2 * L, COLLAR_R * fig, COLLAR_N,
                                                 skin_c, tmpl_p[64:128], struct.unpack_from("<12H", tmpl_p, op)[10:12]))
        i = at(b)
        lines[i + 3] = lines[i + 3].replace(lines[i + 3].strip(), "1 %s" % new_r)
    # the neck: a second part on the chest bone
    new_r, new_p = new_names()
    ctx.char_file(new_r.lower() + ".rsd", tmpl_r.replace("PLY=%s." % tmpl_r.split("PLY=")[1][:4], "PLY=%s." % new_p).encode("latin-1"))
    L = lengths["chest"]
    ctx.char_file(new_p.lower() + ".p", _bar(-NECK_FROM * L, -L - 0.6 * NECK_TO, -(NECK_FROM - 0.1) * L, -L - NECK_TO,
                                             NECK_R * fig, COLLAR_N, skin_c, tmpl_p[64:128],
                                             struct.unpack_from("<12H", tmpl_p, op)[10:12]))
    i = at("chest")
    part = lines[i + 3].split()
    assert part[0] == "1", part
    lines[i + 3] = lines[i + 3].replace(lines[i + 3].strip(), "2 %s %s" % (part[1], new_r))
    return "".join(lines)

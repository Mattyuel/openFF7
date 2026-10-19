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

Tags in use: R Ruby (ZRHA), E Elena (ZELA), S Scarlet (ZSCA), T Tifa (ZTFA), H the Honey Bee girls (ZHBA, the dancer BADD), A Aerith (ZAEA, from AUFF) (675), K Skye (ZSKA: only `nipples`), N the island nurse (ZIUA, from BTEC, 679_nurse)

`nipples(ctx, hrc, tag)` adds pink nipples (NIPPLE_*) to a girl with the standard torso (675 adds
them to every one, Skye included, after all `apply` calls: `apply` wants one part per body bone).
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



def _tidy(V, P, rounds):
    """A light, shape-keeping smoothing (Taubin: a shrinking step then an inflating one, `rounds` times)
    that evens out creases and lumps without shrinking the part (user: Tifa's body "tidied a bit, no
    huge changes"). Open-edge vertices (where the part meets the next one) stay put. Indices kept."""
    nbr, opp = {}, {}
    for t in P:
        for j in range(3):
            a, b = t[j], t[(j + 1) % 3]
            nbr.setdefault(a, set()).update((b, t[(j + 2) % 3]))
            opp[(min(a, b), max(a, b))] = opp.get((min(a, b), max(a, b)), 0) + 1
    rim = {i for e, n in opp.items() if n != 2 for i in e}
    V = [list(v) for v in V]
    for _ in range(rounds):
        for f in (TIDY_SHRINK, TIDY_INFLATE):
            V = [list(v) if i in rim or i not in nbr else
                 [v[k] + f * (sum(V[j][k] for j in nbr[i]) / len(nbr[i]) - v[k]) for k in range(3)]
                 for i, v in enumerate(V)]
    return V


TIDY_SHRINK, TIDY_INFLATE = 0.33, -0.34     # Taubin's lambda / mu


def _cut(V, P, n, c):
    """The mesh (V, P) cut along the plane n . v = c: each triangle crossing it split in three, the
    crossing points shared by both sides (one vertex each: the colours are split later)."""
    V, out, made = [list(v) for v in V], [], {}
    f = [sum(n[k] * v[k] for k in range(3)) - c for v in V]

    def cross(a, b):
        key = (min(a, b), max(a, b))
        if key not in made:
            t = f[a] / (f[a] - f[b])
            V.append([V[a][k] + t * (V[b][k] - V[a][k]) for k in range(3)])
            f.append(0.0)
            made[key] = len(V) - 1
        return made[key]
    for t in P:
        s = [f[i] > 0 for i in t]
        on = [abs(f[i]) < 1e-9 for i in t]
        if all(s) or not any(s) or any(on):
            out.append(t)
            continue
        poly = {True: [], False: []}
        for j in range(3):
            a, b = t[j], t[(j + 1) % 3]
            poly[s[j]].append(a)
            if s[j] != s[(j + 1) % 3]:
                x = cross(a, b)
                poly[True].append(x)
                poly[False].append(x)
        for side in (True, False):
            q = poly[side]
            out += [(q[0], q[k], q[k + 1]) for k in range(1, len(q) - 1)]
    return V, out


def mirrored(V, P, keep):
    """The mesh (V, P) made symmetric about x = 0 (user: Tifa's uneven breasts): cut there, the half on
    the side of sign `keep` (+1 / -1) kept and mirrored onto the other, sharing the cut's vertices."""
    V, P = _cut([[0.0 if abs(v[0]) < 1e-4 else v[0]] + list(v[1:]) for v in V], P, [1.0, 0.0, 0.0], 0.0)
    P = [t for t in P if sum(V[i][0] for i in t) * keep > 0]
    used = sorted({i for t in P for i in t})
    NV, half, other = [], {}, {}
    for i in used:
        half[i] = len(NV)
        NV.append([0.0 if abs(V[i][0]) < 1e-6 else V[i][0]] + list(V[i][1:]))
    for i in used:
        if NV[half[i]][0] == 0.0:
            other[i] = half[i]
        else:
            other[i] = len(NV)
            NV.append([-NV[half[i]][0]] + NV[half[i]][1:])
    return NV, [tuple(half[i] for i in t) for t in P] + [(other[t[0]], other[t[2]], other[t[1]]) for t in P]


def coloured(d, cuts, colour_of, tidy=0, mirror=0):
    """.p bytes d remade (user: Tifa's lingerie, as Scarlet's stockings: sharp colour edges): tidied
    (`_tidy`, `tidy` rounds), cut along each plane of `cuts` [(normal, c)] in the part's own frame, each
    triangle coloured colour_of(centroid) (the part's frame), and each vertex where colours meet doubled,
    one copy per colour, both copies keeping the surface's normal (the lighting runs on across the
    edge). mirror (+1 / -1): first made symmetric, that side kept (`mirrored`). Returns (bytes,
    (vertices before tidying, the same vertices after))."""
    import math
    V, P, _ = _part(d)
    if mirror:
        V, P = mirrored(V, P, mirror)
    before = [list(v) for v in V]
    V = _tidy(V, P, tidy) if tidy else [list(v) for v in V]
    moved = (before, list(V))
    for n, c in cuts:
        V, P = _cut(V, P, n, c)
    cols = [colour_of([sum(V[i][k] for i in t) / 3 for k in range(3)]) for t in P]
    copy, NV, NC, NP = {}, [], [], []
    for t, col in zip(P, cols):
        tt = []
        for i in t:
            if (i, col) not in copy:
                copy[(i, col)] = len(NV)
                NV.append(V[i])
                NC.append(col)
            tt.append(copy[(i, col)])
        NP.append(tuple(tt))
    h = struct.unpack_from("<16I", d, 0)
    op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
    out = bytearray(_hb()._p_file(NV, NP, NC, d[64:128], struct.unpack_from("<12H", d, op)[10:12]))
    nv = len(NV)                                          # copies of one point: one normal (their sum)
    group = {}
    for k, v in enumerate(NV):
        group.setdefault(tuple(round(x, 6) for x in v), []).append(k)
    for ks in group.values():
        if len(ks) < 2:
            continue
        s = [sum(struct.unpack_from("<3f", out, 128 + 12 * nv + 12 * k)[j] for k in ks) for j in range(3)]
        L = math.sqrt(sum(x * x for x in s)) or 1.0
        for k in ks:
            struct.pack_into("<3f", out, 128 + 12 * nv + 12 * k, *(x / L for x in s))
    return bytes(out), moved

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


def apply(ctx, hrc, tag, skin=None, legs=None, bust=1.0, head_drop=0.0):
    """See the module. legs = {"femur": bands, "tibia": bands} (see `_banded`): her legs'
    colours (Scarlet's stockings). Her torso bones (pelvis, chest, both shoulder and collar
    bones, the hip joints) are set to the standard's x her figure (user: Tifa's long pelvis
    bone stretched the pelvis and her neck floated; Elena's long chest bone lifted the torso's
    shoulders above her arms); her arm and leg bones stay hers. Figure = her limbs (thigh,
    shin, upper arm, forearm) / the standard's. bust: her bust's size (each torso vertex's bust
    offset, `ctx.bust_delta` from 670, x bust; user: Tifa / Scarlet 1.5, Aerith 0.5).
    head_drop: her head part moved this far down its bone onto the torso, and no neck bar (user:
    Tifa's head sat too high on a thin neck with an extra mesh at its base: her own torso ran up
    into her neck, her head joint 0.5 below her shoulder line; on the standard torso it is 0.27
    above it)."""
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
        # (the standard's chest also carries Skye's nipples once 675 ran: its first part is the body)
        assert len(std[b][1]) == (3 if b == "chest" and len(std[b][1]) == 3 else 1) and len(her[b][1]) == 1, (b, std[b][1], her[b][1])
        sz = lengths[b] / std[b][0]
        r = ctx.char_file(std[b][1][0].lower() + ".rsd").decode("latin-1")
        ply = r.split("PLY=")[1][:4]
        new_r, new_p = new_names()
        ctx.char_file(new_r.lower() + ".rsd", r.replace("PLY=%s." % ply, "PLY=%s." % new_p).encode("latin-1"))
        part = _scaled(ctx.char_file(ply.lower() + ".p"), fig, sz, skin, lengths[b] if b.endswith("tibia") else None)
        if legs and b[2:] in legs:
            part = _banded(part, legs[b[2:]], lengths[b])
        if b == "chest" and bust != 1.0:
            part = bytearray(part)
            assert len(ctx.bust_delta) == struct.unpack_from("<16I", part, 0)[3], tag
            for i, dv in enumerate(ctx.bust_delta):
                x, y, z = struct.unpack_from("<3f", part, 128 + 12 * i)
                struct.pack_into("<3f", part, 128 + 12 * i, x + (bust - 1) * dv[0] * fig,
                                 y + (bust - 1) * dv[1] * fig, z + (bust - 1) * dv[2] * sz)
            part = bytes(part)
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
    if head_drop:                                          # (user) her head lowered onto the torso
        assert len(her["head"][1]) == 1, her["head"][1]
        hr = ctx.char_file(her["head"][1][0].lower() + ".rsd").decode("latin-1")
        hp = hr.split("PLY=")[1][:4]
        d = bytearray(ctx.char_file(hp.lower() + ".p"))
        for k in range(struct.unpack_from("<16I", d, 0)[3]):
            x, y, z = struct.unpack_from("<3f", d, 128 + 12 * k)
            struct.pack_into("<3f", d, 128 + 12 * k, x, y, z + head_drop)
        new_r, new_p = new_names()
        ctx.char_file(new_r.lower() + ".rsd", hr.replace("PLY=%s." % hp, "PLY=%s." % new_p).encode("latin-1"))
        ctx.char_file(new_p.lower() + ".p", bytes(d))
        i = at("head")
        lines[i + 3] = lines[i + 3].replace(her["head"][1][0], new_r)
        return "".join(lines)
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


# (user) pink nipples on every undressed girl: a small pink dome on each breast of the standard
# torso, a part of its own on the chest bone (one per side, so `_p_file` winds each round its own
# centre). The bust's tip = the torso vertex furthest forward on that side in the standard's own
# stance (Skye's DXID frame 0: she faces -z); the standard's chest part is copied vertex for vertex
# into every girl's (`_scaled`), so the same vertex is her tip. The dome sits on the vertex's normal:
# a ring of NIPPLE_N points NIPPLE_R (x her figure) wide NIPPLE_LIFT out, its tip NIPPLE_TIP out and
# its back NIPPLE_SINK in (inside the breast).
NIPPLE_BGR = (150, 130, 228)                   # pink (R 228, G 130, B 150)
NIPPLE_R, NIPPLE_N, NIPPLE_LIFT, NIPPLE_TIP, NIPPLE_SINK = 0.3, 8, 0.04, 0.12, 0.2


def _bust_tips(ctx):
    """The standard torso's tip vertex indices (left, right) (see NIPPLE_*)."""
    from ff7 import fieldanim as fa
    hrc = ctx.char_file(STANDARD.lower()).decode("latin-1")
    sk = fa.skeleton(hrc)
    rr, rp, rots = fa.Anim(ctx.char_file("dxid.a")).frames[0]
    m = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)[[b[0] for b in sk].index("chest")][0]
    local = lambda w: [sum(m[r][c] * w[r] for r in range(3)) for c in range(3)]   # world dir -> the bone's
    front, left = local([0.0, 0.0, -1.0]), local([1.0, 0.0, 0.0])
    V, _, _ = _part(_chest_p(ctx, hrc))
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    tips = []
    for s in (1, -1):
        i = max((i for i, v in enumerate(V) if s * dot(v, left) > 0.5), key=lambda i: dot(V[i], front))
        assert 0.6 < s * dot(V[i], left) < 2.0, ("bust tip", V[i])
        tips.append(i)
    return tips


def _chest_p(ctx, hrc):
    rsd = bones(hrc)["chest"][1][0]
    return ctx.char_file(ctx.char_file(rsd.lower() + ".rsd").decode("latin-1").split("PLY=")[1][:4].lower() + ".p")


def nipples(ctx, hrc, tag, tips=None):
    """`hrc` (an undressed girl's .hrc text, the standard torso on her chest bone) with a pink
    nipple part per side added to the chest bone ("ZK<tag>L"/"R" .rsd -> "ZJ<tag>L"/"R" .p);
    see NIPPLE_*. tips = `_bust_tips` (found again if not given)."""
    import math
    tips = tips or _bust_tips(ctx)
    V, P, _ = _part(_chest_p(ctx, hrc))
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    cross = lambda u, w: [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
    unit = lambda a: [c / math.sqrt(sum(x * x for x in a)) for c in a]
    centre = [sum(v[k] for v in V) / len(V) for k in range(3)]
    std_n = len(_part(_chest_p(ctx, ctx.char_file(STANDARD.lower()).decode("latin-1")))[0])
    assert len(V) == std_n, ("not the standard torso", len(V), std_n)
    fig = math.dist(V[tips[0]], V[tips[1]]) / math.dist(*(_part(_chest_p(ctx, ctx.char_file(STANDARD.lower())
                                                                          .decode("latin-1")))[0][i] for i in tips))
    tmpl_r = ctx.char_file(bones(ctx.char_file(STANDARD.lower()).decode("latin-1"))["l_uparm"][1][0].lower()
                           + ".rsd").decode("latin-1")
    tmpl_p = ctx.char_file(tmpl_r.split("PLY=")[1][:4].lower() + ".p")
    h = struct.unpack_from("<16I", tmpl_p, 0)
    op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
    names = []
    for i, side in zip(tips, "LR"):
        n = [0.0, 0.0, 0.0]
        for t in P:
            if i in t:
                fn = cross(sub(V[t[1]], V[t[0]]), sub(V[t[2]], V[t[0]]))
                if sum(fn[k] * (V[i][k] - centre[k]) for k in range(3)) < 0:
                    fn = [-c for c in fn]
                n = [n[k] + fn[k] for k in range(3)]
        n = unit(n)                                          # out of the breast
        u = unit(cross(n, [0.0, 0.0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0.0, 0.0]))
        w = cross(n, u)
        at = lambda d, r=0.0, a=0.0: [V[i][k] + n[k] * d + r * fig * (math.cos(a) * u[k] + math.sin(a) * w[k])
                                      for k in range(3)]
        ring = [at(NIPPLE_LIFT, NIPPLE_R, 2 * math.pi * k / NIPPLE_N) for k in range(NIPPLE_N)]
        pts = ring + [at(NIPPLE_TIP * fig), at(-NIPPLE_SINK * fig)]
        tris = [(k, (k + 1) % NIPPLE_N, NIPPLE_N) for k in range(NIPPLE_N)] + \
               [(k, (k + 1) % NIPPLE_N, NIPPLE_N + 1) for k in range(NIPPLE_N)]
        r_, p_ = "ZK" + tag + side, "ZJ" + tag + side
        ctx.char_file(r_.lower() + ".rsd", tmpl_r.replace("PLY=%s." % tmpl_r.split("PLY=")[1][:4], "PLY=%s." % p_)
                      .encode("latin-1"))
        ctx.char_file(p_.lower() + ".p", _hb()._p_file(pts, tris, NIPPLE_BGR, tmpl_p[64:128],
                                                       struct.unpack_from("<12H", tmpl_p, op)[10:12]))
        names.append(r_)
    lines = hrc.splitlines(True)
    k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "chest" and lines[k + 1].strip() == "hip")
    part = lines[k + 3].split()
    lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), " ".join([str(int(part[0]) + 2)] + part[1:] + names))
    return "".join(lines)


# ---- (user) Tifa's body as the standard ----------------------------------------------------------
TIFA_BONES = ("hip", "chest", "l_femur", "r_femur")      # the parts the user made (patches/models/tifa)


def tifa_parts(ctx, hrc, raws, tidy, mirror, gen_chest, bust):
    """(675) The user's Tifa parts as the base every girl's body is made from: ctx.tifa_std = {"parts":
    {bone: (V, P, tail, (sxy, sz) in Tifa's frame)}, "delta": the chest's bust offset per vertex (Tifa's
    frame; her bust is `bust` x the standard's), "fig"}. raws = {bone: .p bytes as the user made them};
    gen_chest = Tifa's generated (standard) chest .p, whose vertices carry `ctx.bust_delta`."""
    import math
    her, std = bones(hrc), bones(ctx.char_file(STANDARD.lower()).decode("latin-1"))
    fig = sum(her[b][0] for b in LIMBS) / sum(std[b][0] for b in LIMBS)
    parts = {}
    for bone in TIFA_BONES:
        d = raws[bone]
        V, P, _ = _part(d)
        if mirror.get(bone):
            V, P = mirrored(V, P, mirror[bone])
        V = _tidy(V, P, tidy) if tidy else [list(v) for v in V]
        h = struct.unpack_from("<16I", d, 0)
        op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
        parts[bone] = (V, P, (d[64:128], struct.unpack_from("<12H", d, op)[10:12]),
                       (fig, her[bone][0] / std[bone][0]))
    G, _, _ = _part(gen_chest)
    assert len(G) == len(ctx.bust_delta), "Tifa's generated chest isn't the standard torso"
    sz = parts["chest"][3][1]
    D = [(dv[0] * fig, dv[1] * fig, dv[2] * sz) for dv in ctx.bust_delta]

    def delta(v):                                         # the bust offset at v: the 4 nearest, by 1/distance
        near = sorted(range(len(G)), key=lambda i: sum((G[i][k] - v[k]) ** 2 for k in range(3)))[:4]
        w = [1.0 / (math.dist(G[i], v) + 1e-3) for i in near]
        return [sum(w[j] * D[near[j]][k] for j in range(4)) / sum(w) for k in range(3)]
    ctx.tifa_std = {"parts": parts, "delta": [delta(v) for v in parts["chest"][0]], "delta_at": delta,
                    "bust": bust, "fig": fig}


def tifa_body(ctx, hrc, skin, bust=1.0, legs=None):
    """(user) Her hip / chest / thigh parts (already on her bones by `apply`) and her nipples (`nipples`)
    replaced by the user's Tifa body (`tifa_parts`): scaled from Tifa's figure to hers, the bust moved to
    `bust` x the standard's along the standard's bust offsets, in her skin colour (Scarlet's stockings by
    `legs`, as `apply`). Writes over her part files."""
    T = ctx.tifa_std
    her, std = bones(hrc), bones(ctx.char_file(STANDARD.lower()).decode("latin-1"))
    fig = sum(her[b][0] for b in LIMBS) / sum(std[b][0] for b in LIMBS)
    k_ = bust - T["bust"]
    ply = lambda rsd: ctx.char_file(rsd.lower() + ".rsd").decode("latin-1").split("PLY=")[1][:4].lower() + ".p"

    def placed(V, sz_t, sz, deltas=None):
        out = []
        for i, v in enumerate(V):
            if deltas is not None:
                v = [v[k] + k_ * deltas[i][k] for k in range(3)]
            out.append([v[0] * fig / T["fig"], v[1] * fig / T["fig"], v[2] * sz / sz_t])
        return out
    for bone in TIFA_BONES:
        V, P, tail, (_, sz_t) = T["parts"][bone]
        sz = her[bone][0] / std[bone][0]
        d = _hb()._p_file(placed(V, sz_t, sz, T["delta"] if bone == "chest" else None), P, [skin] * len(V), *tail)
        if legs and bone[2:] in legs:
            d = _banded(d, legs[bone[2:]], her[bone][0])
        ctx.char_file(ply(her[bone][1][0]), d)
    sz_t, sz = T["parts"]["chest"][3][1], her["chest"][0] / std["chest"][0]
    nips = [r for r in her["chest"][1] if r.upper().startswith("ZK")]
    assert len(nips) == 2, ("her nipples", her["chest"][1])
    for r in nips:
        V, P, C, tail = T["nipple"]
        sx = 1 if r.upper().endswith("L") else -1
        V = [[v[0] * sx] + list(v[1:]) for v in V]
        mid = [sum(v[k] for v in V) / len(V) for k in range(3)]
        dv = T["delta_at"]([mid[0] * sx, mid[1], mid[2]])
        dv = [dv[0] * sx, dv[1], dv[2]]
        ctx.char_file(ply(r), _hb()._p_file(placed(V, sz_t, sz, [dv] * len(V)), P, C, *tail))

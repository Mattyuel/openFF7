"""(user) The standard female body (`_female_body`, built by 670) on the undressed
models of Ruby, Elena, Scarlet and Tifa: each keeps her own head and feet; the body's
skin takes her face's skin colour (the head part's skin vertex colour: faces are
vertex-coloured, their textures only hold eyes and mouth); Scarlet's legs keep her
stockings' colours (her own thigh: skin to 0.88 down, a white band to 1.63, dark below;
her shin dark) as sharp bands. The models' fields already use these .hrc names; the
poses built for them in 660 / 670 stay (Elena's chest bone is shortened to the torso's
shoulders, so her head sits ~1.4 lower). Then (user) pink nipples (`_female_body.nipples`) on
each of them and on Skye."""
import os
import struct

import _female_body as fb

STOCKING, BAND = (22, 22, 32), (204, 204, 204)
SCARLET_SKIN = (136, 168, 246)
BUST = {"ZSCA.HRC": 1.5, "ZTFA.HRC": 1.5, "ZAEA.HRC": 0.5}   # (user) her bust's size (standard 1)
HEAD_DROP = {"ZTFA.HRC": 0.8}  # (user) her head lowered onto the torso, no neck bar (`_female_body.apply`)
GIRLS = [  # (.hrc written, from .hrc, tag, legs); skin = her face's (`_female_body.face_skin`)
    ("ZRHA.HRC", "ZRHA.HRC", "R", None),
    ("ZELA.HRC", "ZELA.HRC", "E", None),
    ("ZSCA.HRC", "ZSCA.HRC", "S", {"femur": [(0.0, SCARLET_SKIN), (0.88 / 5.32, BAND), (1.63 / 5.32, STOCKING)],
                                    "tibia": [(0.0, STOCKING)]}),
    ("ZTFA.HRC", "ZTFA.HRC", "T", None),
    ("ZAEA.HRC", "AUFF.HRC", "A", None),                # (user) Aerith's undressed copy (660 `BARE`)
    # (user) the Honey Bee girls' undressed copy of the dancer (BADD): 620's devoted room shows it
    # from the fade to the bed (entity girlb, HB_BARE_HRC)
    ("ZHBA.HRC", "BADD.HRC", "H", None),
]


# (user) Tifa's body is the user's own (their hand-edited ZTFA: fuller bust, rounder seat): pelvis, chest,
# thighs and nipples from patches/models/tifa/ in place of the generated ones (same bones and lengths;
# her head and neck stay as built), lightly tidied (`_female_body._tidy`), and her black garter lingerie
# (the user's design, measured off that model) made as Scarlet's stockings are: the mesh cut along
# each edge so every triangle is one colour (no colour smeared across triangles), the normals kept
# across the edges. Regions in her standing pose (ABCD frame 0; model units, y down, she faces -z,
# her left +x): the waistband round the waist, two straps down the front of her hips, a band round
# each upper thigh.
TIFA = "ZTFA.HRC"
TIFA_STAND = "abcd.a"
TIFA_PARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "tifa")
TIFA_BODY = {"hip": "zxta.p", "chest": "zxtb.p", "l_femur": "zxti.p", "r_femur": "zxtk.p"}
TIFA_TIDY = 2                               # smoothing rounds (0 = the user's mesh as it is)
TIFA_MIRROR = {"chest": 1}                  # (user: uneven breasts) made symmetric, this side's half kept
TIFA_NIPPLE = "zjtl.p"                      # the kept side's nipple; the other is its mirror image
LINGERIE = (16, 16, 24)                     # B, G, R: near black
WAIST = (-13.5, -12.75)                     # y range of the waistband
STRAP_X, STRAP_HALF = 1.27, 0.2             # the straps' middles at x = +-STRAP_X, this far either side
THIGH = (-10.45, -9.35)                     # y range of the thigh bands


def _tifa(ctx, skin):
    from ff7 import fieldanim as fa
    hrc = ctx.char_file(TIFA.lower()).decode("latin-1")
    sk = fa.skeleton(hrc)
    rr, rp, rots = fa.Anim(ctx.char_file(TIFA_STAND)).frames[0]
    F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
    names = [b[0] for b in sk]
    parts = fb.bones(hrc)
    for bone, ply in TIFA_BODY.items():
        m, start, _ = F[names.index(bone)]
        world = lambda v: [start[k] + fa._vec(m, v)[k] for k in range(3)]
        row = lambda k: [fa._vec(m, e)[k] for e in ([1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0])]
        plane = lambda k, c: (row(k), c - start[k])          # world coordinate k = c, in the part's frame
        thigh = bone.endswith("femur")
        cuts = [plane(1, y) for y in (THIGH if thigh else WAIST)]
        if bone == "hip":
            cuts += [plane(0, sg * (STRAP_X + e)) for sg in (1, -1) for e in (-STRAP_HALF, STRAP_HALF)]

        def colour(c, thigh=thigh, bone=bone, world=world):
            x, y, z = world(c)
            if thigh:
                return LINGERIE if THIGH[0] <= y <= THIGH[1] else skin
            if WAIST[0] <= y <= WAIST[1]:
                return LINGERIE
            if bone == "hip" and y > WAIST[1] and z < 0 and abs(abs(x) - STRAP_X) <= STRAP_HALF:
                return LINGERIE
            return skin
        rsd = ctx.char_file(parts[bone][1][0].lower() + ".rsd").decode("latin-1")
        assert rsd.split("PLY=")[1][:4].lower() + ".p" == ply, (bone, rsd)
        with open(os.path.join(TIFA_PARTS, ply), "rb") as fh:
            d, moved = fb.coloured(fh.read(), cuts, colour, TIFA_TIDY, TIFA_MIRROR.get(bone, 0))
        assert LINGERIE in fb._part(d)[2], (bone, "no lingerie in this part")
        ctx.char_file(ply, d)
        if bone == "chest":
            ctx.tifa_chest = moved


def apply(ctx):
    for out, src, tag, legs in GIRLS:
        text = ctx.char_file(src.lower()).decode("latin-1")
        skin = fb.face_skin(ctx, text)
        ctx.char_file(out.lower(), fb.apply(ctx, text, tag, skin, legs, BUST.get(out, 1.0), HEAD_DROP.get(out, 0.0)).encode("latin-1"))
    assert fb.face_skin(ctx, ctx.char_file("zsca.hrc").decode("latin-1")) == SCARLET_SKIN
    # (user) pink nipples on all of them and on Skye (the standard itself), after every `apply`
    tips = fb._bust_tips(ctx)
    for out, tag in [(g[0], g[2]) for g in GIRLS] + [(fb.STANDARD, "K")]:
        ctx.char_file(out.lower(), fb.nipples(ctx, ctx.char_file(out.lower()).decode("latin-1"), tag, tips)
                      .encode("latin-1"))
    # (user) Tifa's own body (the user's), tidied, with her lingerie; her nipples (the user's) moved
    # with the tidied bust under them
    hrc = ctx.char_file(TIFA.lower()).decode("latin-1")
    raws = {}
    for bone, ply in TIFA_BODY.items():
        with open(os.path.join(TIFA_PARTS, ply), "rb") as fh:
            raws[bone] = fh.read()
    fb.tifa_parts(ctx, hrc, raws, TIFA_TIDY, TIFA_MIRROR, ctx.char_file(TIFA_BODY["chest"]), BUST[TIFA])
    _tifa(ctx, fb.face_skin(ctx, hrc))
    before, after = ctx.tifa_chest
    with open(os.path.join(TIFA_PARTS, TIFA_NIPPLE), "rb") as fh:
        d = fh.read()
    V, P, C = fb._part(d)
    mid = [sum(v[k] for v in V) / len(V) for k in range(3)]
    assert mid[0] * TIFA_MIRROR["chest"] > 0, "the nipple kept is on the other side"
    i = min(range(len(before)), key=lambda j: sum((before[j][k] - mid[k]) ** 2 for k in range(3)))
    V = [[v[k] + after[i][k] - before[i][k] for k in range(3)] for v in V]
    h = struct.unpack_from("<16I", d, 0)
    op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
    tail = d[64:128], struct.unpack_from("<12H", d, op)[10:12]
    for name, sx in ((TIFA_NIPPLE, 1), (TIFA_NIPPLE.replace("l.", "r."), -1)):
        ctx.char_file(name, fb._hb()._p_file([[v[0] * sx] + v[1:] for v in V], P, C, *tail))
    ctx.tifa_std["nipple"] = (V, P, C, tail)
    # (user) Tifa's body (the user's, without her lingerie) as every other girl's: her skin, her bust size
    for out, src, tag, legs in GIRLS:
        if out != TIFA:
            skin = fb.face_skin(ctx, ctx.char_file(src.lower()).decode("latin-1"))
            fb.tifa_body(ctx, ctx.char_file(out.lower()).decode("latin-1"), skin, BUST.get(out, 1.0), legs)
    # (Skye's own model gets it in 681, after 679_nurse has built from the standard's parts)

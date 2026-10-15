"""(user) The standard female body (`_female_body`, built by 670) on the undressed
models of Ruby, Elena, Scarlet and Tifa: each keeps her own head and feet; the body's
skin takes her face's skin colour (the head part's skin vertex colour: faces are
vertex-coloured, their textures only hold eyes and mouth); Scarlet's legs keep her
stockings' colours (her own thigh: skin to 0.88 down, a white band to 1.63, dark below;
her shin dark) as sharp bands. The models' fields already use these .hrc names; the
poses built for them in 660 / 670 stay (Elena's chest bone is shortened to the torso's
shoulders, so her head sits ~1.4 lower). Then (user) pink nipples (`_female_body.nipples`) on
each of them and on Skye."""
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
    ("ZAEA.HRC", "AUFF.HRC", "A", None),                # (user) Aerith's undressed copy (660 PART2)
    # (user) the Honey Bee girls' undressed copy of the dancer (BADD): 620's devoted room shows it
    # from the fade to the bed (entity girlb, HB_BARE_HRC)
    ("ZHBA.HRC", "BADD.HRC", "H", None),
]


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

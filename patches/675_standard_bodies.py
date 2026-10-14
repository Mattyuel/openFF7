"""(user) The standard female body (`_female_body`, built by 670) on the undressed
models of Ruby, Elena, Scarlet and Tifa: each keeps her own head and feet; the body's
skin takes her face's skin colour (the head part's skin vertex colour: faces are
vertex-coloured, their textures only hold eyes and mouth); Scarlet's legs keep her
stockings' colours (her own thigh: skin to 0.88 down, a white band to 1.63, dark below;
her shin dark) as sharp bands. The models' fields already use these .hrc names; the
poses built for them in 660 / 670 stay (Elena's chest bone is shortened to the torso's
shoulders, so her head sits ~1.4 lower)."""
import _female_body as fb

STOCKING, BAND = (22, 22, 32), (204, 204, 204)
SCARLET_SKIN = (136, 168, 246)
GIRLS = [  # (.hrc, tag, face skin (B, G, R), legs)
    ("ZRHA.HRC", "R", (153, 204, 255), None),
    ("ZELA.HRC", "E", (149, 178, 255), None),
    ("ZSCA.HRC", "S", SCARLET_SKIN, {"femur": [(0.0, SCARLET_SKIN), (0.88 / 5.32, BAND), (1.63 / 5.32, STOCKING)],
                                      "tibia": [(0.0, STOCKING)]}),
    ("ZTFA.HRC", "T", (167, 190, 248), None),
]


def apply(ctx):
    for hrc, tag, skin, legs in GIRLS:
        text = ctx.char_file(hrc.lower()).decode("latin-1")
        ctx.char_file(hrc.lower(), fb.apply(ctx, text, tag, skin, legs).encode("latin-1"))

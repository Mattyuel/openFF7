"""(user) Skye's undressed model (ZSKA, the standard body's own model) gets Tifa's body too
(`_female_body.tifa_body`, the user's parts from patches/models/tifa, in Skye's skin, the standard
bust), after every patch that builds from the standard's parts (675, 679_nurse)."""
import _female_body as fb


def apply(ctx):
    fb.tifa_body(ctx, ctx.char_file(fb.STANDARD.lower()).decode("latin-1"), fb.SKIN)

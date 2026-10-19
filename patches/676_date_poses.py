"""(user) Dates: one position per place (660 `POSITION`), using the movie's poses, which 670 / 672
build after 660. Here, after both: the gondola's "head" copies of each date girl's retargeted
movie head (her ZxJ<s>: she kneels HEAD_GAP in front of standing Cloud's spot) with her root moved
forward onto his spot, so both share one XYZI in any field whatever its scale (Y + her prefix's
letter + J + speed); then a check that every anim the date fields name exists.
"""
import importlib

import _movie_girls as MG
from ff7.models import ModelLoader

# the movie's head (670 POSITIONS "head"): she at (42,-224) DIR 0x40, Cloud at (80,-225) DIR 0xC0:
# her offset from his spot, in field units, at whitebg1's UNIT
HEAD_FROM_HIM = (-38, 1)


def _date_heads(ctx):
    from ff7 import fieldanim as fa
    mv = importlib.import_module("670_movie")
    dt = importlib.import_module("660_dates")
    head = [p for p in mv.POSITIONS if p["name"] == "head"][0]
    hdir = head["girl"][1][3]
    # her model point m with _off(m, hdir) = HEAD_FROM_HIM: _off is linear in (m0, m2)
    ax, az = mv._off((1, 0, 0), hdir), mv._off((0, 0, 1), hdir)
    det = ax[0] * az[1] - az[0] * ax[1]
    m0 = (HEAD_FROM_HIM[0] * az[1] - az[0] * HEAD_FROM_HIM[1]) / det
    m2 = (ax[0] * HEAD_FROM_HIM[1] - HEAD_FROM_HIM[0] * ax[1]) / det
    got = mv._off((m0, 0, m2), hdir)
    assert abs(got[0] - HEAD_FROM_HIM[0]) < 1e-6 and abs(got[1] - HEAD_FROM_HIM[1]) < 1e-6, got
    letter = chr(ord("A") + mv.POSITIONS.index(head))
    for g in MG.GIRLS:
        if g["name"] not in dt.BARE:
            continue
        for s in (dt.SPEED, dt.SPEED_FAST):
            a = fa.Anim(ctx.char_file(("%s%s%d.a" % (g["prefix"], letter, s)).lower()))
            a.frames = [(rr, [rp[0] + m0, rp[1], rp[2] + m2], rots) for rr, rp, rots in a.frames]
            ctx.char_file(("Y%s%s%d.a" % (g["prefix"][1], letter, s)).lower(), a.build())


def _check(ctx):
    """Every anim named by a date field's models exists in char.lgp (the poses come from later patches)."""
    dt = importlib.import_module("660_dates")
    for (place, group), name in dt.FIELDS.items():
        loader = ModelLoader(ctx.field(name).section("models"))
        for e in loader.models:
            for an in ModelLoader.anims(e):
                ctx.char_file(an.split(".")[0].lower() + ".a")      # (KeyError if missing)


def apply(ctx):
    _date_heads(ctx)
    _check(ctx)

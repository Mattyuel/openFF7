"""Kalm: fixed after the party's visit (arrival 341, inn flashback 344-384,
departure 385) and before later-disc changes (999+), so no arrival scene,
flashback or story dialogue plays."""
from ff7.patch import localise_progress
from ff7.script import Script

MOMENT = 400
FIELDS = ["elm", "elm_wa", "elm_i", "elmpb", "elminn_1", "elminn_2", "elmin1_1", "elmin1_2",
          "elmin2_1", "elmin2_2", "elmin3_1", "elmin3_2", "elmtow", "elmin4_1", "elmin4_2"]


def apply(ctx):
    for field in FIELDS:
        sec = Script.parse(ctx.field(field).sections[0])
        localise_progress(sec, const=MOMENT)
        ctx.field(field).sections[0] = sec.build()

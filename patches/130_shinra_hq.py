"""Shinra HQ extras.

2f shop (blin2_i): the two treasure boxes only open from disc 2 (story value
1008+); before that the shop assistant stops you ("You opened up all those
things without asking..."). Remove that check from the two boxes only.
"""
from ff7.script import Script

DISC2 = 1008


def apply(ctx):
    sec = Script.parse(ctx.field("blin2_i").sections[0])
    for name in ("TAKARAA", "TAKARAB"):
        ent = sec.entity_index(name)
        for op in sec.script_ops(ent, 1):
            # pinned fields compare a literal: IFSW/IFUW with left bank 0 and b == 1008
            if op.op in (0x16, 0x17, 0x18, 0x19) and op.raw[1] >> 4 == 0 \
                    and (op.raw[4] | op.raw[5] << 8) == DISC2:
                sec.remove(op)
                break
        else:
            raise RuntimeError("disc 2 check not found in %s" % name)
    ctx.field("blin2_i").sections[0] = sec.build()

"""The reactor elevator (elevtr1) is shared by No.1 and No.5 Reactor. The
original picks the destination (nmkin_* vs smkin_*) and the location name by
story progress (< 33 = No.1); pinned to No.1's moment it always took you to
No.1. Now No.5's rooms set FLAG_IN_REACTOR5 on entry, No.1's clear it, and the
elevator tests the flag instead."""
from _config import FLAG_IN_REACTOR5, FLAGS

from ff7 import asm
from ff7.script import Script

REACTOR1_ROOMS = ["nmkin_1", "nmkin_2"]   # the elevator's No.1 ends
REACTOR5_ROOMS = ["smkin_1", "smkin_2"]   # the elevator's No.5 ends
ELEVATOR = "elevtr1"


def _mark(ctx, field, on):
    sec = Script.parse(ctx.field(field).sections[0])
    first = sec.entry[0][0]
    op = (asm.biton if on else asm.bitoff)(FLAGS, FLAG_IN_REACTOR5)
    sec.insert_before(first, [op], retarget=False)
    sec.entry[0][0] = op
    ctx.field(field).sections[0] = sec.build()


def _const_if(op):
    """A pinned progress compare: IFUB/IFUBL/IFSW/IFSWL... with two constants."""
    return 0x14 <= op.op <= 0x19 and op.raw[1] == 0


def apply(ctx):
    for f in REACTOR1_ROOMS:
        _mark(ctx, f, False)
    for f in REACTOR5_ROOMS:
        _mark(ctx, f, True)

    sec = Script.parse(ctx.field(ELEVATOR).sections[0])
    reactor1 = {ctx.maplist.index(f) for f in REACTOR1_ROOMS}
    ops = sec.ops
    swapped = 0
    for i, op in enumerate(ops[:-1]):
        nxt = ops[i + 1]
        # `if not (progress < 33) goto <No.5 jump>; MAPJUMP <No.1 room>`
        if _const_if(op) and nxt.op == 0x60 and (nxt.raw[1] | nxt.raw[2] << 8) in reactor1:
            sec.replace(op, [asm.if_byte(FLAGS, "bit_off", FLAG_IN_REACTOR5, op.target)])
            swapped += 1
        # `if not (progress > 27) goto <"No.1 Reactor">; MPNAM "No.5 Reactor"`
        elif _const_if(op) and nxt.op == 0x43:
            sec.replace(op, [asm.if_byte(FLAGS, "bit_on", FLAG_IN_REACTOR5, op.target)])
            swapped += 1
    assert swapped == 3, "elevtr1: expected 2 destination checks + 1 name check, got %d" % swapped
    ctx.field(ELEVATOR).sections[0] = sec.build()

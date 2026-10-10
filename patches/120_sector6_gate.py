"""Open the Sector 6 / Sector 7 gate both ways.

Sector 7 side (mds7plr1, the screen with two guards in front of the pillar):
the guards stood in the narrow passage to the gate and refused to let you
through. They now stand either side of its mouth, say a short line, and the
existing exit at the bottom leads to the Sector 6 playground.

Sector 6 side (mds6_2, the playground with the giant gate): the gate is
always open (its two halves start in their open positions), the gate floor is
unlocked, and a new exit at the end of the passage leads back to the Sector 7
guard screen. The Aerith / chocobo-carriage scene that opened it in the
original does not happen (the field is pinned past it, see 100_midgar.py).
"""
import struct

from _recruit import say

from ff7 import triggers
from ff7.script import Op, Script

# mds7plr1 (Sector 7, guards): new guard positions (x, y, triangle) at the mouth
# of the passage; the passage itself is ~225 units wide.
GUARD_R = (-100, -680, 27)
GUARD_L = (175, -660, 35)
GUARD_LINES = {
    "guardR": "“The gate to Sector 6 is open.\n Watch yourself out there.”",
    "guardL": "“Move along. Nothing to see here.”",
}
# Where you arrive on the Sector 7 side, just inside the passage.
ARRIVE_S7 = (-20, -840, 95)

# mds6_2 (Sector 6 playground): gate halves, open positions (from their
# original opening scripts), and the passage behind the gate.
DOOR_OPEN = {"drr": (-1778, 1050), "drl": (-1036, 1640)}
GATE_TRIANGLE = 0xFB  # the locked floor of the gate passage (251)
EXIT_LINE = ((-2308, 2126, 0), (-2035, 2365, 0))  # across the far end of the passage
EXIT_DIR = 128


def _set_xyzi(op, x, y, tri=None):
    assert op.op == 0xA5
    struct.pack_into("<hh", op.raw, 3, x, y)
    if tri is not None:
        struct.pack_into("<H", op.raw, 9, tri)


def _guards(ctx):
    sec = Script.parse(ctx.field("mds7plr1").sections[0])
    for name, (x, y, tri) in (("guardR", GUARD_R), ("guardL", GUARD_L)):
        ent = sec.entity_index(name)
        _set_xyzi(next(o for o in sec.script_ops(ent, 0) if o.op == 0xA5), x, y, tri)
        talk = [Op(b"\x33\x01")] + say(sec, GUARD_LINES[name]) + [Op(b"\x33\x00"), Op(b"\x00")]
        sec.insert_before(sec.entry[ent][1], talk, retarget=False)
        sec.entry[ent][1] = talk[0]
    # The 'border2' line across the passage stops you and calls the guards; keep it off.
    ent = sec.entity_index("border2")
    for o in sec.script_ops(ent, 8):
        if o.op == 0xD1:
            o.raw[1] = 0
    ctx.field("mds7plr1").sections[0] = sec.build()


def _playground(ctx):
    field = ctx.field("mds6_2")
    sec = Script.parse(field.sections[0])
    for name, (x, y) in DOOR_OPEN.items():
        ent = sec.entity_index(name)
        _set_xyzi(next(o for o in sec.script_ops(ent, 0) if o.op == 0xA5), x, y)
    dic = sec.entity_index("dic")
    lock = next(o for o in sec.script_ops(dic, 0)
                if o.op == 0x6D and o.raw[1] == GATE_TRIANGLE and o.raw[2] == 0 and o.raw[3] == 1)
    sec.remove(lock)
    field.sections[0] = sec.build()

    trig = field.section("triggers")
    slot = triggers.free_slot(trig)
    x, y, tri = ARRIVE_S7
    trig = triggers.set_gateway(trig, slot, EXIT_LINE[0], EXIT_LINE[1], (x, y, tri),
                                ctx.maplist.index("mds7plr1"), EXIT_DIR)
    field.set_section("triggers", trig)


def apply(ctx):
    _guards(ctx)
    _playground(ctx)

"""Recruit Tifa in 7th Heaven.

Barret's recruitment location is not decided yet. Until then he is kept out
of the Sector 7 story scenes (hidden in 7th Heaven and at the station)."""
from _config import TIFA
from _recruit import hide, hide_if_recruited, recruit_talk

from ff7 import asm
from ff7.script import Op, Script

TIFA_LINES = dict(
    question="{TIFA}\n“{CLOUD}! I was hoping you'd stop by.\n Are you heading out somewhere?”",
    choices=("Come with me, Tifa.", "Not right now."),
    yes_reply="{TIFA}\n“Just try and stop me!\n Let me grab my gloves.”",
    no_reply="{TIFA}\n“Okay. You know where to find me.”",
    joined="{TIFA} joined the party!",
)


def _seventh_heaven(ctx):
    sec = Script.parse(ctx.field("mds7pb_1").sections[0])
    tifa = sec.entity_index("tifa")
    # Talk script becomes the recruitment.
    talk = recruit_talk(sec, TIFA, **TIFA_LINES)
    old = sec.entry[tifa][1]
    sec.insert_before(old, talk, retarget=False)
    sec.entry[tifa][1] = talk[0]
    # Hidden once recruited (end of her init).
    init_ret = next(o for o in sec.script_ops(tifa, 0) if o.op == 0x00)
    sec.insert_before(init_ret, hide_if_recruited(TIFA, pc_entity=True), retarget=False)
    # Her bar-setup script hides her if var[3][213] bit 6 is set (a story flag
    # some builds set at new game); always take the "stand at the bar" branch.
    for op in sec.script_ops(tifa, 6):
        if op.op == 0x14 and op.raw[2] == 213 and op.raw[3] == 6:
            sec.replace(op, [asm.goto(op.target)])
            break
    # Barret is not recruited here: the bar setup script (stagedr -> ballet
    # script 9) always hides him.
    barret = sec.entity_index("ballet")
    first = sec.entry[barret][9]
    sec.insert_before(first, hide() + [asm.ret()])
    ctx.field("mds7pb_1").sections[0] = sec.build()


def _station(ctx):
    """The Sector 7 station shows Barret on the platform; hide him there."""
    sec = Script.parse(ctx.field("mds7st3").sections[0])
    barret = sec.entity_index("ballet")
    init_ret = next(o for o in sec.script_ops(barret, 0) if o.op == 0x00)
    sec.insert_before(init_ret, hide(), retarget=False)
    ctx.field("mds7st3").sections[0] = sec.build()


def apply(ctx):
    _station(ctx)
    _seventh_heaven(ctx)

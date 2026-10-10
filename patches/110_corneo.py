"""Don Corneo: on his bed in his bedroom (colne_6). Talk to him: he says his
"A man!? What's goin' on?" line from the original bedroom scene, runs for the
door and is gone. A flag records that he fled (for Wutai, later).

Also hides the second Corneo standing in the 2f hall (colne_5), since he is
now always in his bedroom.
"""
import struct

from _config import FLAG_CORNEO_FLED, FLAGS

from ff7 import asm
from ff7.script import Op, Script

LINE = 52                      # colne_6 text: Don Corneo / "A man!? What's goin' on?"
WINDOW = bytes.fromhex("50 01 b4 00 0a 00 85 00 39 00")  # as used for that line originally
# Corneo starts on the bed at (-14, 220); the exit is at about (-164, -226).
RUN_OFFSET = (-150, -446, 0)
RUN_FRAMES = 20
RUN_ANIM = 2                   # field models: 0 stand, 1 walk, 2 run (assumed for Corneo)


def _ofst(dx, dy, dz, frames):
    return Op(bytes([0xC3, 0x00, 0x00, 0x01]) + struct.pack("<hhhH", dx, dy, dz, frames))


def _bedroom(ctx):
    sec = Script.parse(ctx.field("colne_6").sections[0])
    ent = sec.entity_index("COLNEO")
    talk_ret = sec.entry[ent][1]
    assert talk_ret.raw == bytearray(b"\x00"), "Corneo's talk script was expected to be empty"
    new = [
        Op(b"\x33\x01"),                       # UC 01: player control off
        Op(WINDOW),
        asm.message(1, LINE),
        asm.biton((3, 163), 1),                # original flag: Corneo gone from this room
        asm.biton(FLAGS, FLAG_CORNEO_FLED),
        Op(bytes([0xA2, RUN_ANIM, 0x01])),     # DFANM: run
        _ofst(*RUN_OFFSET, RUN_FRAMES),
        Op(b"\xC4"),                           # OFSTW: wait for the move
        Op(b"\x7E\x01"),                       # TLKON 01: can't talk
        Op(b"\xC7\x01"),                       # SOLID 01: not solid
        Op(b"\xA4\x00"),                       # VISI 00: hidden
        Op(b"\x33\x00"),                       # UC 00: player control on
        asm.ret(),
    ]
    sec.insert_before(talk_ret, new, retarget=False)
    sec.entry[ent][1] = new[0]
    ctx.field("colne_6").sections[0] = sec.build()


def _hall(ctx):
    sec = Script.parse(ctx.field("colne_5").sections[0])
    ent = sec.entity_index("COLNEO")
    init = sec.script_ops(ent, 0)
    # `if not (var[3][163] & 1) goto skip; TLKON 01; SOLID 01; VISI 00` -> always hide
    cond = next(o for o in init if o.op == 0x14 and o.raw[2] == 163)
    sec.remove(cond)
    ctx.field("colne_5").sections[0] = sec.build()


def _entrance(ctx):
    """Mansion entrance (colne_1): the doorman blocked the door and the floor in
    front of it was locked until Corneo's bedroom scene was done. Remove both."""
    sec = Script.parse(ctx.field("colne_1").sections[0])
    ad = sec.entity_index("AD")
    for op in [o for o in sec.script_ops(ad, 0) if o.op == 0x6D and o.raw[3] == 1]:
        sec.remove(op)                                       # IDLCK .. 01 (lock)
    doorman = sec.entity_index("DOORMAN")
    cond = next(o for o in sec.script_ops(doorman, 0) if o.op == 0x14 and o.raw[2] == 163)
    sec.remove(cond)                                         # always hidden
    ctx.field("colne_1").sections[0] = sec.build()


OFFICE_DOOR_LAYER, DUNGEON_DOOR_LAYER = 1, 2   # background layers drawing the closed doors


def _ground_floor(ctx):
    """Mansion 1f (colne_2): the office door (upstairs) and the dungeon door
    were locked floor triangles plus 'Closed / Keep Out' lines, opened by story
    flags. Open both for good, and stop the hall's loop that played the
    "Cloud!!" scene with Tifa (it also added her to the party)."""
    sec = Script.parse(ctx.field("colne_2").sections[0])
    ad2 = sec.entity_index("AD2")
    init = sec.script_ops(ad2, 0)
    end = next(o for o in init if o.op == 0x00)
    locked = sorted({o.raw[1] | o.raw[2] << 8 for o in init if o.op == 0x6D})
    opened = [Op(bytes([0x6D, t & 0xFF, t >> 8, 0x00])) for t in locked]   # IDLCK .. 00
    opened += [Op(bytes([0xE1, 0x00, layer, 0x01]))                       # BGOFF door
               for layer in (OFFICE_DOOR_LAYER, DUNGEON_DOOR_LAYER)]
    sec.insert_before(end, opened)  # jumps to the init's RET now run these first
    main_first = init[init.index(end) + 1]
    sec.insert_before(main_first, [Op(b"\x00")], retarget=False)        # main: RET
    for name in ("KDLINE", "CDLINE"):
        ent = sec.entity_index(name)
        ret = next(o for o in sec.script_ops(ent, 0) if o.op == 0x00)
        sec.insert_before(ret, [Op(b"\xD1\x00")])                       # LINON 00
    ctx.field("colne_2").sections[0] = sec.build()


def apply(ctx):
    _bedroom(ctx)
    _hall(ctx)
    _entrance(ctx)
    _ground_floor(ctx)

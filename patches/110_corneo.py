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


def apply(ctx):
    _bedroom(ctx)
    _hall(ctx)

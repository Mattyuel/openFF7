"""Recruit Aerith in the Sector 5 church, at the flower bed."""
from _config import AERITH
from _recruit import hide_if_recruited, recruit_talk

from ff7.script import Op, Script

LINES = dict(
    question="{AERIS}\n“Hello again, {CLOUD}.\n Off on another adventure?”",
    choices=("Want to come along?", "Just passing through."),
    yes_reply="{AERIS}\n“I thought you'd never ask!\n The flowers can look after themselves.”",
    no_reply="{AERIS}\n“Okay. I'll be here with the flowers.”",
    joined="{AERIS} joined the party!",
)
# Flower bed spot and pose, from her later-disc script in the same room.
POS = (109, 378, -7, 128)


def apply(ctx):
    sec = Script.parse(ctx.field("chrin_1a").sections[0])
    ent = sec.entity_index("earith")
    # At the pinned moment the room's director calls her script 6, which hid
    # her. Make it place her at the flowers instead (unless recruited).
    x, y, z, tri = POS
    place = [Op(bytes([0xA5, 0, 0]) + x.to_bytes(2, "little", signed=True)
                + y.to_bytes(2, "little", signed=True) + z.to_bytes(2, "little", signed=True)
                + tri.to_bytes(2, "little")),
             Op(b"\xA2\x05\x01"),                  # DFANM 05: tending the flowers
             Op(b"\x7E\x00"), Op(b"\xC7\x00"), Op(b"\xA4\x01")]
    place += hide_if_recruited(AERITH) + [Op(b"\x00")]
    sec.insert_before(sec.entry[ent][6], place, retarget=False)
    sec.entry[ent][6] = place[0]
    talk = recruit_talk(sec, AERITH, **LINES)
    sec.insert_before(sec.entry[ent][1], talk, retarget=False)
    sec.entry[ent][1] = talk[0]
    ctx.field("chrin_1a").sections[0] = sec.build()

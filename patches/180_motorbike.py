"""The motorbike section on demand, from the front of Shinra HQ.

- sinbil_1 (front of HQ, the train's Shinra Tower stop): a Shinra biker on
  the right offers the ride: story mode (var[3][115] = 0, as blackbgb sets
  it) and MINIGAME game 0 (bike), which returns to roadend, the end of the
  highway, instead of the story's blackbgb -> Motor Ball -> roadend chain.
- roadend: its scene (the `dir` main: the whole party conversation, then
  progress 335 and a jump to mds5_5) is off, Cloud isn't repositioned, and
  the party copies (ba/ti/ea/re, PC entities shown with VISI 01) are hidden.
  Its camera has +x up the screen: a line up the road (x 700) fights Motor
  Ball (formation 468, once per visit), a line down the road (x -2150, below
  the walkmesh hole at x -1900..-1700) leads back to the front of HQ.
- Destroyed enemy bikes are counted by an exe hook (quest_menu.asm q_bike)
  as kill-table id _quest_data.BIKE, for the Middle Manager's quest.
"""
import struct

from _config import FLAG_MOTORBALL_FOUGHT, FLAGS
from _travel import add_line, add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

HQ_FRONT, ROAD_END = "sinbil_1", "roadend"
BIKER_MODEL = ("junair", 8)                       # shinra_reifuku
BIKER_AT, BIKER_DIR = (840, -2820, -73, 56), 194  # right of the screen, facing left
BIKE_MODE = (3, 115)                              # 0 = story mode (blackbgb), 1 = Gold Saucer
ROAD_ARRIVE = (-1243, -34, 50)                    # where the story's jump to roadend puts you
MOTOR_BALL = 468
UP_LINE = ((700, -380, 175), (700, 350, 175))
DOWN_LINE = ((-2150, -380, 175), (-2150, 350, 175))
HQ_ARRIVE = (-5, -3041, 45, 128)                  # the train's arrival in front of HQ
PARTY_COPIES = ["ba", "ti", "ea", "re"]
HIDE = [b"\x7E\x01", b"\xC7\x01", b"\xA4\x00"]    # TLKON 01, SOLID 01, VISI 00


def minigame(field_id, x, y, tri, param, game):
    return Op(bytes([0x20]) + struct.pack("<HhhH", field_id, x, y, tri) + bytes([param, game]))


def _biker(ctx):
    road = ctx.maplist.index(ROAD_END)
    assert Walkmesh(ctx.field(ROAD_END).section("walkmesh")).contains(ROAD_ARRIVE[2], *ROAD_ARRIVE[:2])
    model = copy_model(ctx, HQ_FRONT, *BIKER_MODEL)

    def talk(sec):
        ride = [asm.setbyte(BIKE_MODE, 0),
                Op(b"\x33\x00"), Op(b"\x4A\x00"),             # UC 00, MENU2 00
                minigame(road, *ROAD_ARRIVE, 0, 0)]           # bike game -> end of the highway
        return ([Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]
                + choice_menu(sec, "Shinra Biker\n“Got a spare bike and an empty\n highway. Wanna ride it out?”",
                              ["Let's ride.", "Not now."], [ride, None]))
    add_npc(ctx, HQ_FRONT, "biker", model, BIKER_AT, BIKER_DIR, talk)


def _road_end(ctx):
    sec = Script.parse(ctx.field(ROAD_END).sections[0])
    # dir: keep the init (menu, music, name), drop the scene.
    init = sec.script_ops(sec.entity_index("dir"), 0)
    ret = next(o for o in init if o.op == 0x00)
    sec.insert_before(init[init.index(ret) + 1], [asm.ret()], retarget=True)
    # cl: its main places Cloud for the scene.
    cl = sec.script_ops(sec.entity_index("cl"), 0)
    ret = next(o for o in cl if o.op == 0x00)
    moves = [o for o in cl[cl.index(ret) + 1:] if o.op in (0xA5, 0xB3)]   # XYZI, DIR
    assert len(moves) == 2, [o.raw.hex() for o in moves]
    for o in moves:
        sec.remove(o)
    for name in PARTY_COPIES:
        ops = sec.script_ops(sec.entity_index(name), 0)
        ret = next(o for o in ops if o.op == 0x00)
        sec.insert_before(ret, [Op(b) for b in HIDE], retarget=True)
    ctx.field(ROAD_END).sections[0] = sec.build()

    def boss(sec):
        done = asm.ret()
        return [asm.if_byte(FLAGS, "bit_off", FLAG_MOTORBALL_FOUGHT, done),
                asm.biton(FLAGS, FLAG_MOTORBALL_FOUGHT), asm.battle(MOTOR_BALL), done]
    add_line(ctx, ROAD_END, "motorbal", *UP_LINE, boss,
             init_extra=[asm.bitoff(FLAGS, FLAG_MOTORBALL_FOUGHT)])
    hq = ctx.maplist.index(HQ_FRONT)
    add_line(ctx, ROAD_END, "tohq", *DOWN_LINE,
             [Op(b"\x33\x00"), asm.mapjump(hq, *HQ_ARRIVE), asm.ret()])


def apply(ctx):
    _biker(ctx)
    _road_end(ctx)

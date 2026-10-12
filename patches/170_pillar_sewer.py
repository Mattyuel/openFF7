"""Sector 7 pillar open both ways; a way back up from the sewer.

- Pillar gate (mds7plr1): `tobira` shows the closed gate (BGON 00 01 00) and
  `stagedr`'s main locks the gate floor (IDLCK triangle 260). In the story the
  218 scene opens it (BG state 1 + unlock). Here it starts open and unlocked,
  so you can go up the pillar and come back out.
- Pillar (pillar_1/2, one spiral stair to the roof): random battles are on at
  any moment and nothing plays on entry. Story leftovers hidden: Biggs
  (pillar_1 `big`, standing at the arrival) and Jessie (pillar_2 `je`) dying,
  and Barret (pillar_2 `bal`: gunfire loop; talking to him changed the party
  and jumped to pillar_3, the Reno/bomb cutscene field, now unreachable).
  The pillar fields' text table is full: never add dialogue there.
  Reno is a quest boss line on the roof (Gwen's quests, _quest_data.py).
- Sewer: you only ever jumped down from colne_b1 (the landing room, Aps) into
  colne_b3. A line at colne_b3's west dead end, below the drop, leads back up
  into colne_b1's corridor. colne_b1 is pinned at 209 (100_midgar) so the fall
  scene doesn't play and its ladder out works. Aps is the Scared Man's quest
  boss line in the landing room.
"""
from _travel import add_line

from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

GATE_FIELD = "mds7plr1"
GATE_CLOSED, GATE_OPEN = bytes.fromhex("e0000100"), bytes.fromhex("e0000101")   # BGON 00 01 00 / 01
GATE_LOCK = bytes.fromhex("6d040101")                                         # IDLCK 0x104 on
HIDE = [b"\x7E\x01", b"\xC7\x01", b"\xA4\x00"]                                 # TLKON 01, SOLID 01, VISI 00
STORY_COPIES = {"pillar_1": ["big"], "pillar_2": ["je", "bal"]}
SEWER_BACK = ((-620, -150, -211), (-620, -335, -211))
SEWER_UP = (212, 1250, -578, 28, 192)       # colne_b1 corridor, 110 west of its jump-down line


def _gate(ctx):
    sec = Script.parse(ctx.field(GATE_FIELD).sections[0])
    shows = [o for o in sec.script_ops(sec.entity_index("tobira"), 0) if bytes(o.raw) == GATE_CLOSED]
    assert len(shows) == 1, shows
    shows[0].raw[:] = GATE_OPEN
    locks = [o for o in sec.script_ops(sec.entity_index("stagedr"), 0) if bytes(o.raw) == GATE_LOCK]
    assert len(locks) == 1, locks
    sec.remove(locks[0])
    ctx.field(GATE_FIELD).sections[0] = sec.build()


def _hide_story_copies(ctx):
    for field, names in STORY_COPIES.items():
        sec = Script.parse(ctx.field(field).sections[0])
        for name in names:
            ent = sec.entity_index(name)
            init = sec.script_ops(ent, 0)
            ret = next(o for o in init if o.op == 0x00)
            sec.insert_before(ret, [Op(b) for b in HIDE], retarget=True)
            main = init[init.index(ret) + 1:]
            if main:                                    # stop any loop (Barret's gunfire)
                sec.insert_before(main[0], [asm.ret()], retarget=True)
            sec.replace_script(ent, 1, [asm.ret()])     # no talk
        ctx.field(field).sections[0] = sec.build()


def _sewer_back(ctx):
    mesh = Walkmesh(ctx.field("colne_b1").section("walkmesh"))
    field_id, x, y, tri, _d = SEWER_UP
    assert ctx.maplist[field_id] == "colne_b1" and mesh.contains(tri, x, y)
    add_line(ctx, "colne_b3", "upsewer", *SEWER_BACK,
             [Op(b"\x33\x00"), asm.mapjump(*SEWER_UP), asm.ret()])


def apply(ctx):
    _gate(ctx)
    _hide_story_copies(ctx)
    _sewer_back(ctx)

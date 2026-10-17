"""Cargo ship as a place to explore (Junon <-> Costa del Sol).

- Upper deck (ship_1) is pinned after the story (416), where copies of the
  party (TIFA2, YUFI2, EARITH2, RED2, BALLET2) stand around and open the
  party-change menu (MENU 00 07) when talked to. They are hidden. The lower
  decks keep their battles; Jenova BIRTH is a repeatable quest boss line by
  the dead guard in shpin_3 (600_quests, `moe_jenova`); the story line there
  is off (410).
- A First Mate on the other upper deck screen (ship_2) takes you ashore at
  Costa del Sol: the same world-map jump the story uses when the ship docks
  (shpin_3: MAPJUMP wm36, field.tbl entry A = del1).
"""
from _recruit import say
from _travel import add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

PARTY_COPIES = ["TIFA2", "YUFI2", "EARITH2", "RED2", "BALLET2"]
HIDE = [Op(b"\x7E\x01"), Op(b"\xC7\x01"), Op(b"\xA4\x00")]   # TLKON 01, SOLID 01, VISI 00

MATE_FIELD, MATE_AT = "ship_2", (9, -353)
MATE_MODEL = ("ship_1", 12)                                  # shinra_crew
COSTA_DEL_SOL_ENTRY = "wm36"


def _hide_party_copies(ctx):
    sec = Script.parse(ctx.field("ship_1").sections[0])
    for name in PARTY_COPIES:
        init = sec.script_ops(sec.entity_index(name), 0)
        ret = next(o for o in init if o.op == 0x00)
        sec.insert_before(ret, [Op(bytes(o.raw)) for o in HIDE], retarget=True)   # every path hides
    ctx.field("ship_1").sections[0] = sec.build()


def _first_mate(ctx):
    mesh = Walkmesh(ctx.field(MATE_FIELD).section("walkmesh"))
    x, y = MATE_AT
    tri = mesh.find(x, y)
    assert tri is not None
    model = copy_model(ctx, MATE_FIELD, *MATE_MODEL)

    def talk(sec):
        go = [Op(b"\x33\x00"), asm.mapjump(ctx.maplist.index(COSTA_DEL_SOL_ENTRY), 0, 0, 0, 0)]
        return ([Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]  # UC 01, PTURA, WAIT
                + choice_menu(sec, "First Mate\n“We're docked at Costa del Sol.\n Going ashore?”",
                              ["Yes, let me off.", "I'll stay aboard."], [go, None]))
    add_npc(ctx, MATE_FIELD, "mate", model, (x, y, mesh.height(tri, x, y), tri), 0x40, talk)


def apply(ctx):
    _hide_party_copies(ctx)
    _first_mate(ctx)

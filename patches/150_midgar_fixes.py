"""Small Midgar fixes from play-testing.

- Honey Bee Inn (mrkt3): at the pinned moment (193, after the dress-up
  night) the street's main script walks Corneo's lackey (kobun1, script 8:
  MOVE + IDLCK triangles 0x18/0x19) and a passer-by (usan1, script 7) in
  front of the door, so the inn couldn't be entered. No flag skips that
  branch, so those two calls are removed; they keep their normal spots.
- Sector 7 item store (mds7_im) open: mds7's doorway lock and "We're
  closed today." sign line are off.
- A ghost on the Sector 6 playground (mds6_2), left of where you come in
  from the Sector 7 gate: "you're defying heckin' fate" (a Whispers of Fate
  joke). Model: the Gold Saucer Ghost Hotel's tall ghost (ghotin_1 'noppo').
"""
from _recruit import say
from _travel import add_npc, copy_model

from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

HONEY_BEE_BLOCKERS = [bytes.fromhex("020f48"),   # REQSW kobun1 script 8 (walk to the door, lock floor)
                      bytes.fromhex("021247")]   # REQSW usan1 script 7

GHOST_FIELD = "mds6_2"
GHOST_MODEL = ("ghotin_1", 6)                    # gold_noppo
GHOST_AT = (-1522, 1070)                         # ~60 px left of the gate arrival (-1312, 1270) on screen
GHOST_LINE = "Ghost\n“Noooo, you can't go this way.\n You're defying heckin' fate.”"


def _honey_bee(ctx):
    sec = Script.parse(ctx.field("mrkt3").sections[0])
    main = sec.script_ops(sec.entity_index("produce"), 0)
    for raw in HONEY_BEE_BLOCKERS:
        hits = [o for o in main if bytes(o.raw) == raw]
        assert len(hits) == 1, raw.hex()
        sec.remove(hits[0])
    ctx.field("mrkt3").sections[0] = sec.build()


def _ghost(ctx):
    mesh = Walkmesh(ctx.field(GHOST_FIELD).section("walkmesh"))
    x, y = GHOST_AT
    tri = mesh.find(x, y)
    assert tri is not None
    model = copy_model(ctx, GHOST_FIELD, *GHOST_MODEL)

    def talk(sec):
        return ([Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]   # UC 01, PTURA, WAIT
                + say(sec, GHOST_LINE) + [Op(b"\x33\x00"), asm.ret()])
    add_npc(ctx, GHOST_FIELD, "ghost", model, (x, y, mesh.height(tri, x, y), tri), 0x40, talk)


def _item_store(ctx):
    """Sector 7 item store (mds7 -> mds7_im): the doorway (triangle 17) is
    locked and a talk line by it says "We're closed today." until the story
    flag (3,213,6), which can't be set at new game (it hides Barret/Tifa in
    7th Heaven). Unlock it here and keep the sign line off."""
    sec = Script.parse(ctx.field("mds7").sections[0])
    locks = [o for o in sec.script_ops(sec.entity_index("produce"), 0) if bytes(o.raw) == bytes.fromhex("6d110001")]
    assert len(locks) == 1, locks
    sec.remove(locks[0])
    item = sec.script_ops(sec.entity_index("item"), 0)
    gate = [o for o in item if bytes(o.raw) == bytes.fromhex("1430d5060903")]   # if not (3,213) bit 6 goto: skip LINON 00
    assert len(gate) == 1 and item[item.index(gate[0]) + 1].raw == bytearray(b"\xd1\x00"), gate
    sec.remove(gate[0])
    ctx.field("mds7").sections[0] = sec.build()


def apply(ctx):
    _item_store(ctx)
    _honey_bee(ctx)
    _ghost(ctx)

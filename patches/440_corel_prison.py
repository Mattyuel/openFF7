"""Corel Prison by buggy, there and back.

- In: driving the buggy into the Gold Saucer on the world map already enters
  the prison desert (wm0 function 0xA964, cell (14,18): if riding the buggy,
  enter field wm15 = desert2). But desert2's bottom and left edges led into
  desert1 (the endless sand loop) unless you'd just come from the prison, so
  the prison itself was unreachable. They now lead to jail1 / jail3, as they
  do when you came from there.
- Out: a convict near jail1's desert arrival drives you out: the buggy bits
  (bank 1 byte 127 bits 0+1) are set and you jump to wm15; wm0's branch for it
  mounts the buggy before placing you beside the Gold Saucer.
"""
from _travel import add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

DESERT, PRISON = "desert2", "jail1"
TO_JAIL1 = bytes.fromhex("60d7015bfdb70d060100")      # MAPJUMP jail1 (-677, 3511) tri 262 dir 0
TO_JAIL3 = (478, 406, -17, 4, 192)                     # jl3's own branch for the prison side
DESERT_DEFAULTS = {"jl2": (481, 3202), "jl3": (481, 4708)}   # MAPJUMP desert1 at x
BUGGY = (1, 127)
EXIT_AT = (-600, 3400)
EXIT_MODEL = (PRISON, 8)                               # korel_narazu2


def _desert_exits(ctx):
    sec = Script.parse(ctx.field(DESERT).sections[0])
    for name, (field, x) in DESERT_DEFAULTS.items():
        ent = sec.entity_index(name)
        hits = [o for o in sec.script_ops(ent, 5) if o.op == 0x60
                and o.raw[1] | o.raw[2] << 8 == field and int.from_bytes(o.raw[3:5], "little", signed=True) == x]
        assert len(hits) == 1, (name, hits)
        new = TO_JAIL1 if name == "jl2" else bytes(asm.mapjump(*TO_JAIL3).raw)
        hits[0].raw[:] = new
    ctx.field(DESERT).sections[0] = sec.build()


def _exit_npc(ctx):
    mesh = Walkmesh(ctx.field(PRISON).section("walkmesh"))
    x, y = EXIT_AT
    tri = mesh.find(x, y)
    assert tri is not None
    model = copy_model(ctx, PRISON, *EXIT_MODEL)

    def talk(sec):
        go = [asm.biton(BUGGY, 0), asm.biton(BUGGY, 1),                 # buggy owned + riding
              Op(b"\x33\x00"), asm.mapjump(ctx.maplist.index("wm15"), 0, 0, 0, 0)]
        return ([Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]  # UC 01, PTURA, WAIT
                + choice_menu(sec, "Convict\n“Your buggy's out front. Leavin'\n this dump already?”",
                              ["Drive out to the desert.", "Not yet."], [go, None]))
    add_npc(ctx, PRISON, "driver", model, (x, y, mesh.height(tri, x, y), tri), 0x80, talk)


def apply(ctx):
    _desert_exits(ctx)
    _exit_npc(ctx)

"""Sector 4 train tunnel (tunnel_2) and the plate interior below it.

- The duct at the end of the tunnel: talking at it (or crossing the line in
  front of it) brought Barret and Tifa in for the "tiny hole" conversation.
  Now Cloud just gets a choice; "Go down" runs only his own descent (walk to
  the duct, ladder animation, jump to sbwy4_1).
- The vent (sbwy4_4, reached by the ladder in sbwy4_1) is the original: its
  far-end ladder climbs down onward to the No.5 Reactor. (A drop / back /
  stay menu there reopened while you stood on the line and could get you
  stuck; the way back is the first ladder, then the line below the duct.)
- Below the duct (sbwy4_1, the corridor with the Ether) there was no way back
  up: a line across the corridor just left (on screen) of where you land
  takes you back to the tunnel, beside the duct.
"""
from _travel import add_line, choice_menu, mapjump

from ff7 import asm
from ff7.script import Op, Script

TUNNEL = "tunnel_2"
BACK_TO_TUNNEL = ("tunnel_2", 0, 450, 21, 64)   # beside the duct, past its line
BELOW_DUCT = "sbwy4_1"
DUCT_LANDING = (22, -745)        # tunnel_2's jump arrival
# The walkable corridor ends at y -806 (init IDLCKs triangles 2 and 5 beyond it;
# the first version of this line sat there and could not be reached). The line
# is between that end and the landing, so running left from the landing crosses it.
BACK_LINE = ((-100, -785, 0), (100, -785, 0))


def _copy(op):
    return Op(bytes(op.raw))


def _duct(ctx):
    sec = Script.parse(ctx.field(TUNNEL).sections[0])
    ent = sec.entity_index("cloud")
    old = sec.script_ops(ent, 4)
    # Walk to the duct: MSPED, MOVE, DIR, SOLID before the scene (REQ to Barret).
    walk = [o for o in old[:old.index(next(o for o in old if o.op == 0x01))]
            if o.op in (0xB2, 0xA8, 0xB3, 0xC7)]                 # MSPED MOVE DIR SOLID
    assert [o.op for o in walk] == [0xB2, 0xA8, 0xB3, 0xC7], [o.name for o in walk]
    # Cloud's own descent: after Barret's REQEW 09 c5, up to and including LADER.
    start = next(i for i, o in enumerate(old) if o.op == 0x03 and o.raw[1:3] == b"\x09\xc5")
    end = next(i for i, o in enumerate(old) if o.name == "LADER")
    descent = [o for o in old[start + 1:end + 1]
               if o.op not in (0x5F,)                            # NOP
               and not (o.op == 0x81 and o.raw[1] >> 4 == 2 and o.raw[2] == 0)]  # progress
    assert any(o.op == 0x01 and o.raw[1] == 3 for o in descent), "jump entity REQ missing"
    yes = [_copy(o) for o in walk + descent]
    menu = choice_menu(sec, "{CLOUD}\n“A duct down under the plate…”",
                       ["Go down.", "Not now."], [yes, None])
    sec.replace_script(ent, 4, menu)
    ctx.field(TUNNEL).sections[0] = sec.build()


def _below_duct(ctx):
    from ff7.walkmesh import Walkmesh
    mesh = Walkmesh(ctx.field(BELOW_DUCT).section("walkmesh"))
    y = BACK_LINE[0][1]
    assert mesh.find(0, y) == 3 and DUCT_LANDING[1] > y, "line must be on the open floor, left of the landing"
    add_line(ctx, BELOW_DUCT, "toduct", *BACK_LINE,
             [Op(b"\x33\x00"), mapjump(ctx, *BACK_TO_TUNNEL), asm.ret()])   # UC 00 before leaving


def apply(ctx):
    _duct(ctx)
    _below_duct(ctx)

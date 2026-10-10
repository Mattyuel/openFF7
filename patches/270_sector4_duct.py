"""Sector 4 train tunnel (tunnel_2) and the plate interior below it.

- The duct at the end of the tunnel: talking at it (or crossing the line in
  front of it) brought Barret and Tifa in for the "tiny hole" conversation.
  Now Cloud just gets a choice; "Go down" runs only his own descent (walk to
  the duct, ladder animation, jump to sbwy4_1).
- The vent (sbwy4_4, reached by the ladder in sbwy4_1): at its far end the
  line only reacted to [OK] and only dropped you onward, so it looked like a
  dead end with no way back. It now offers a choice on [OK] or when walked
  over: drop down (onward to the No.5 Reactor) or climb back to the tunnel.
"""
from _travel import choice_menu, mapjump

from ff7.script import Op, Script

TUNNEL = "tunnel_2"
VENT = "sbwy4_4"
BACK_TO_TUNNEL = ("tunnel_2", 0, 450, 21, 64)   # beside the duct, past its line


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


def _vent(ctx):
    sec = Script.parse(ctx.field(VENT).sections[0])
    ent = sec.entity_index("line1")
    drop = sec.script_ops(ent, 1)
    assert drop[0].op == 0x01 and drop[0].raw[1] == sec.entity_index("cloud"), drop[0].raw.hex()
    back = [Op(b"\x33\x00"), mapjump(ctx, *BACK_TO_TUNNEL)]   # UC 00 before leaving
    menu = choice_menu(sec, "{CLOUD}\n“The vent ends here.”",
                       ["Drop down.", "Climb back to the train tunnel.", "Stay."],
                       [[_copy(drop[0])], back, None])
    slots = sec.replace_script(ent, 1, menu)        # [OK] on the line (+ slots sharing it)
    if 2 not in slots:                              # and walking over it
        sec.entry[ent][2] = menu[0]
    ctx.field(VENT).sections[0] = sec.build()


def apply(ctx):
    _duct(ctx)
    _vent(ctx)

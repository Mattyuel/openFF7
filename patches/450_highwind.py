"""The Highwind (disc 2 version) from the Junon airstrip; no interior while flying.

- Airstrip (junair2, reached from junair's lift by running right): a line
  across the runway, a good way past the arrival (towards the far end = up
  the screen; the camera looks along the runway). Crossing it sets "Highwind
  owned" + "aboard" (bank 1 byte 127 bits 4/5 = wm bits 0x3FC/0x3FD, as the
  fship interior fields do) and jumps to wm40, the disc 2 first take-off
  entry: wm0's branch for it mounts the Highwind (model 3) before placing you
  beside Junon. No world map change is needed for that.
- [Menu] while flying runs wm0 system function 6 (exe 0x74F676), which enters
  the interior (fship_23 / fship_25). Its first word becomes `return`, so the
  button does nothing in the air (the main menu isn't opened there either,
  the exe skips it for the Highwind). Landing and re-boarding are untouched.
"""
from _travel import add_line

from ff7 import asm
from ff7.script import Op
from ff7.walkmesh import Walkmesh
from ff7.worldmap import EvPatcher

STRIP = "junair2"
TAKEOFF_LINE = ((-4860, -2400, 3711), (-2480, -2400, 3711))
TAKEOFF_ENTRY, TAKEOFF_FIELD_ID = "wm40", 41
HIGHWIND = (1, 127)
OWNED, ABOARD = 4, 5
FUNCTION_6, FN6_START = 0x0006, 0x0BD2
RESET, RETURN = 0x0100, 0x0203


def _takeoff(ctx):
    mesh = Walkmesh(ctx.field(STRIP).section("walkmesh"))
    (x1, y, _), (x2, _, _) = TAKEOFF_LINE
    assert all(mesh.find(x, y) is not None for x in range(x1 + 60, x2 - 60, 100)), \
        "the take-off line must cross the runway floor"
    field_id = ctx.maplist.index(TAKEOFF_ENTRY)
    assert field_id == TAKEOFF_FIELD_ID, field_id
    add_line(ctx, STRIP, "takeoff", *TAKEOFF_LINE, [
        Op(b"\x33\x01"),                                         # UC 01
        asm.biton(HIGHWIND, OWNED), asm.biton(HIGHWIND, ABOARD),
        Op(b"\x33\x00"),                                         # UC 00 before leaving
        asm.mapjump(field_id, 0, 0, 0, 0),
        asm.ret()])


def _no_interior(ctx):
    data = ctx.wm_file("wm0.ev")
    ev = EvPatcher(data)
    fns = {fid: off for _i, fid, off in ev.script.functions()}
    assert fns.get(FUNCTION_6) == FN6_START, "wm0 system function 6 moved"
    assert ev.script.words[FN6_START] == RESET, hex(ev.script.words[FN6_START])
    ev.set_word(FN6_START, RETURN)
    data[:] = ev.build()


def apply(ctx):
    _takeoff(ctx)
    _no_interior(ctx)

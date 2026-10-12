"""Join disc 1 Upper Midgar to the disc 2 Midgar route.

Route: Upper Midgar train stop (md8brdg, the Sector 8 walkway where the
conductor is) -> run right -> 8th Street (md8_5, where the party lands in
disc 2), arriving at its left end -> its own exit on the right -> the hatch
screen (md8_6). md8_5's left end leads back to md8brdg.
md8_5's camera doesn't fit ff7.camera's model (every floor point projects to
one thin band), so "left" there is placed from the floor itself: its exit to
md8_6 (screen right) is at the +x end, the street's -x end is the left.

- The rest is flags (_config.INITIAL_EVENT_FLAGS, bank 5 offset 128/135): hatch
  already open, party copies hidden, Turks / Proud Clod / Hojo scenes done.
  md8_5 (pinned 998) plays no landing scene and shows no party copies (they
  only appear at 1599). The route on (ladder -> underground md8_b1/b2 ->
  sbwy4_22 -> tunnels 6/5/4 -> md0, and tunnel_5 -> md8brdg2 -> md8_32 ->
  Mako Cannon) has no story progress checks except canon_2 (pinned past Hojo
  in world_overrides.json). Enemies keep their disc 2 levels.
- Turks, Proud Clod and Hojo are repeatable quest bosses (the Shinra Deserter
  by the new exit on md8brdg, `_quest_data_world.py`).
"""
from ff7 import triggers
from ff7.walkmesh import Walkmesh

WALKWAY, STREET = "md8brdg", "md8_5"
# md8brdg's floor runs on past the edge of its background (you can walk out
# of view to the right, up to screen x ~300); the line sits at the visible
# right edge (screen x ~155) across the arrival plaza, both ends off the floor.
WALKWAY_LINE = ((775, 750, 518), (600, -130, 518))
WALKWAY_ARRIVE = (470, 170, 0xC0)            # just left of the line (screen 120, 35), facing left
# md8_5's street floor (z 0) spans y 240..2090 at its -x end (x -1960).
STREET_LINE = ((-1880, 200, 0), (-1880, 2130, 0))
STREET_ARRIVE = (-1750, 1000, 0x40)          # just right of the line, facing +x


def _arrival(ctx, field, x, y, direction):
    tri = Walkmesh(ctx.field(field).section("walkmesh")).find(x, y)
    assert tri is not None, (field, x, y)
    return (x, y, tri), direction


def _gateway(ctx, field, line, dest_field, dest, direction):
    f = ctx.field(field)
    trig = f.section("triggers")
    slot = triggers.free_slot(trig)
    f.set_section("triggers", triggers.set_gateway(trig, slot, *line, dest,
                                                   ctx.maplist.index(dest_field), direction))


def apply(ctx):
    at_street, dir_street = _arrival(ctx, STREET, *STREET_ARRIVE)
    at_walkway, dir_walkway = _arrival(ctx, WALKWAY, *WALKWAY_ARRIVE)
    assert at_street[0] > STREET_LINE[0][0]
    _gateway(ctx, WALKWAY, WALKWAY_LINE, STREET, at_street, dir_street)
    _gateway(ctx, STREET, STREET_LINE, WALKWAY, at_walkway, dir_walkway)

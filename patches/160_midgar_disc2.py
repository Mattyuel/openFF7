"""Join disc 1 Upper Midgar to the disc 2 Midgar route.

- Sector 8 street (md8_2, where Aerith sells flowers): its left end was a dead
  end. A new gateway there leads to md8_6, the disc 2 screen with the hatch
  Cait Sith opens; a gateway at md8_6's left edge leads back.
- The rest is flags (_config.INITIAL_EVENT_FLAGS, bank 5 offset 128/135): hatch
  already open, party copies hidden, Turks / Proud Clod / Hojo scenes done.
  The route on (ladder -> underground md8_b1/b2 -> sbwy4_22 -> tunnels 6/5/4
  -> md0, and tunnel_5 -> md8brdg2 -> md8_32 -> Mako Cannon) has no story
  progress checks except canon_2 (pinned past Hojo in world_overrides.json).
  Enemies keep their disc 2 levels.
- Turks, Proud Clod and Hojo are repeatable quest bosses (the Shinra Deserter
  by the hatch, `_quest_data_world.py`).
"""
from ff7 import triggers
from ff7.camera import Camera, facing_screen
from ff7.walkmesh import Walkmesh

STREET, HATCH = "md8_2", "md8_6"
# md8_2's floor ends at x ~ -4351..-4400 (screen left); the line crosses its left end.
STREET_LINE = ((-4320, 20450, 258), (-4320, 21250, 258))
STREET_ARRIVE = (-4270, 20760)              # just right of the line
# md8_6's floor's left edge is the straight x = -225 side (screen left).
HATCH_LINE = ((-200, -1300, 0), (-200, -800, 0))
HATCH_ARRIVE = (-130, -1050)                # just right of the line


def _arrival(ctx, field, x, y, line):
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    tri = mesh.find(x, y)
    assert tri is not None, (field, x, y)
    assert x > line[0][0], "arrival must be past the line"
    cam = Camera(ctx.field(field).sections[1])
    return (x, y, tri), facing_screen(cam, x, y, mesh.height(tri, x, y), (1, 0))


def _gateway(ctx, field, line, dest_field, dest, direction):
    f = ctx.field(field)
    trig = f.section("triggers")
    slot = triggers.free_slot(trig)
    f.set_section("triggers", triggers.set_gateway(trig, slot, *line, dest,
                                                   ctx.maplist.index(dest_field), direction))


def apply(ctx):
    at_hatch, dir_hatch = _arrival(ctx, HATCH, *HATCH_ARRIVE, HATCH_LINE)
    at_street, dir_street = _arrival(ctx, STREET, *STREET_ARRIVE, STREET_LINE)
    _gateway(ctx, STREET, STREET_LINE, HATCH, at_hatch, dir_hatch)
    _gateway(ctx, HATCH, HATCH_LINE, STREET, at_street, dir_street)

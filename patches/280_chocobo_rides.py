"""Chocobo rides: Choco Billy and a chocobo stand just inside some world map
exits. Talk to either and choose "Giddyap!": you leave for the world map
riding a chocobo exactly like one caught after a battle (dismount and it runs
away).

How it works: the world map script (wm0.ev function 1) picks the player model
from savemap bank 1 byte 126: bit 0 = riding a wild chocobo (model 4, "Wild
chocobo"), bit 1 = a stable chocobo from the farm, bits 2-6 = its colour
(model 0x13). The farm's own "Ride this one?" (frcyo, Choco Billy) sets those
bits and MAPJUMPs to a world map entry with x = y = 0. Here only bit 0 is set,
then the same MAPJUMP the field's own world map exit uses.
"""
from _travel import add_npc, beside, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op
from ff7.walkmesh import Walkmesh

RIDING = (1, 126)        # savemap bank 1 byte 126
WILD_CHOCOBO_BIT = 0
BILLY_MODEL = ("frcyo", 4)       # farm_boy: Choco Billy
CHOCOBO_MODEL = ("frcyo", 5)     # another_choko

# field: (arrival from the world map (x, y, triangle), world map entry it exits
# to, explicit (x, y) for Billy and the chocobo or None = beside the arrival).
SPOTS = {
    "mds5_5": ((711, -2420, 16), "wm0", None),                       # Midgar, slum outskirts
    # Mythril Mine, first screen: the floor beside the arrival is narrow and the
    # first free spot was past the exit line, so place them below the arrival.
    "psdun_1": ((175, 8, 23), "wm4", [(190, -90), (200, -180)]),
}


def _ride(ctx, wm_entry):
    def talk(sec):
        go = [asm.biton(RIDING, WILD_CHOCOBO_BIT),
              Op(b"\x33\x00"),                                   # UC 00 before leaving
              asm.mapjump(ctx.maplist.index(wm_entry), 0, 0, 0, 0)]
        return choice_menu(sec, "Choco Billy\n“Wanna ride a chocobo?”",
                           ["Giddyap!", "Not now."], [go, None])
    return talk


def _at(ctx, field, x, y, near_tri):
    """(x, y, z, tri) on the floor connected to `near_tri`; fails if not walkable."""
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    tri = next((t for t in mesh.nearby(near_tri, 8) if mesh.contains(t, x, y)), None)
    assert tri is not None, "%s: (%d, %d) is not on the floor near triangle %d" % (field, x, y, near_tri)
    return x, y, mesh.height(tri, x, y), tri


def apply(ctx):
    for field, ((x, y, tri), wm_entry, spots) in SPOTS.items():
        if spots:
            pos_billy, pos_bird = (_at(ctx, field, sx, sy, tri) for sx, sy in spots)
        else:
            pos_billy = beside(ctx, field, x, y, tri, dist=90)
            pos_bird = beside(ctx, field, x, y, tri, dist=190)
        billy = copy_model(ctx, field, *BILLY_MODEL)
        bird = copy_model(ctx, field, *CHOCOBO_MODEL)
        add_npc(ctx, field, "billy", billy, pos_billy, 0x40, _ride(ctx, wm_entry))
        add_npc(ctx, field, "ridechoc", bird, pos_bird, 0x40, _ride(ctx, wm_entry))

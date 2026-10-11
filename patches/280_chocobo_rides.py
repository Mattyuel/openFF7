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

But wm0.ev only mounts you (op_300 <model>; op_30C) in the branch for arriving
from the farm (push_special 6 == 3); the other entries just place you. So the
branch for each exit used here is redirected to a block appended in the
script's zero padding: if bit 0x3F0 (bank 1 byte 126 bit 0): op_300 4;
op_30C; then the branch's own placement and exit (mount first, as the farm
branch does).

The ride costs 100 gil (CHGLD/GOLDD). The chocobo model's base colour isn't
yellow: like the cargo ship's chocobo (fship_5), it is tinted yellow with
KAWAI 06 in its main script.
"""
from _recruit import say
from _travel import CHOCOBO_YELLOW, add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op
from ff7.walkmesh import Walkmesh
from ff7.worldmap import EvPatcher

RIDING = (1, 126)        # savemap bank 1 byte 126
WILD_CHOCOBO_BIT = 0
BILLY_MODEL = ("frcyo", 4)       # farm_boy: Choco Billy
CHOCOBO_MODEL = ("frcyo", 5)     # another_choko
PRICE = 100
GIL_LO, GIL_HI = (6, 0xF8), (6, 0xFA)   # temporary 16-bit field vars for CHGLD
WILD_RIDE_BIT_ADDR = 0x3F0       # the same bit as the world map script sees it
WILD_CHOCOBO_MODEL = 4
WM_SPECIAL_ENTRY = 0x6           # push_special 6 = the wmN field id you arrived by

# field: (arrival from the world map (x, y, triangle), world map entry it exits
# to, explicit (x, y) for Billy and the chocobo, their facing direction).
FACING_RIGHT, FACING_DOWN_MDS5_5 = 0x40, 0xED   # ff7.camera.facing_screen(cam, ..., (0, 1))
SPOTS = {
    # Midgar, slum outskirts. User: move them down a little and face down. Was
    # beside the arrival ((801, -2420), (901, -2420)); now ~25 px (1.5x their
    # height) lower on screen, ~290 from the world map exit line.
    "mds5_5": ((711, -2420, 16), "wm0", [(691, -2630), (771, -2640)], FACING_DOWN_MDS5_5),
    # Mythril Mine, first screen: the floor beside the arrival is narrow and the
    # first free spot was past the exit line, so place them below the arrival.
    "psdun_1": ((175, 8, 23), "wm4", [(200, -180), (190, -90)], FACING_RIGHT),   # [Billy, chocobo]: swapped on request
}


def _ride(ctx, wm_entry):
    def talk(sec):
        face = [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]  # UC 01, PTURA leader, WAIT 8
        ok, done = asm.nop(), asm.nop()
        go = [Op(bytes([0x3B, 0x66, GIL_LO[1], GIL_HI[1]])),                 # CHGLD lo, hi
              asm.if_word(GIL_HI, "==", 0, ok),
              asm.if_word(GIL_LO, "<", PRICE, ok)]
        go += say(sec, "Choco Billy\n\u201cThat's %d gil. Come back\n when you've got it.\u201d" % PRICE)
        go += [asm.goto(done), ok,
               Op(bytes([0x3A, 0x00]) + PRICE.to_bytes(4, "little")),           # GOLDD
               asm.biton(RIDING, WILD_CHOCOBO_BIT),
               Op(b"\x33\x00"),                                              # UC 00 before leaving
               asm.mapjump(ctx.maplist.index(wm_entry), 0, 0, 0, 0),
               done]
        return face + choice_menu(sec, "Choco Billy\n\u201cRide a chocobo? %d gil.\u201d" % PRICE,
                                  ["Giddyap!", "Not now."], [go, None])
    return talk


def _mount_on_arrival(ctx, wm_entry):
    """wm0.ev: in the branch for arriving by `wm_entry`, mount the wild chocobo
    if its bit is set (see the module docstring). The mount has to come before
    the branch's placement (op_308/op_309), as in the farm branch: mounting
    after it put the chocobo at the map origin (top-left, in the sea). So the
    branch's first words become a goto to an appended block: [if bit: mount]
    + a copy of the branch body (placement, then its goto to the exit)."""
    ev = EvPatcher(ctx.wm_file("wm0.ev"))
    body, _else = ev.branch_for(WM_SPECIAL_ENTRY, ctx.maplist.index(wm_entry))
    assert body[0].op == 0x100 and body[1].arg is not None, "branch must start with reset; push n"
    assert [x.op for x in body if x.op in (0x200, 0x201)] == [0x200] and body[-1].op == 0x200, \
        "branch body must be straight-line code ending in its exit goto"
    copy = [w for x in body for w in ((x.op, x.arg) if x.arg is not None else (x.op,))]
    start = ev.end
    mount = [0x100, 0x114, WILD_RIDE_BIT_ADDR, 0x201, start + 10,         # if bit:
             0x100, 0x110, WILD_CHOCOBO_MODEL, 0x300, 0x30C]               #   model 4, mount
    assert ev.append(mount + copy) == start
    ev.set_word(body[0].pos, 0x200)                                         # reset; push -> goto block
    ev.set_word(body[0].pos + 1, start)
    ctx.wm_file("wm0.ev")[:] = ev.build()


def _at(ctx, field, x, y, near_tri):
    """(x, y, z, tri) on the floor connected to `near_tri`; fails if not walkable."""
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    tri = next((t for t in mesh.nearby(near_tri, 16) if mesh.contains(t, x, y)), None)
    assert tri is not None, "%s: (%d, %d) is not on the floor near triangle %d" % (field, x, y, near_tri)
    return x, y, mesh.height(tri, x, y), tri


def apply(ctx):
    for field, ((x, y, tri), wm_entry, spots, facing) in SPOTS.items():
        pos_billy, pos_bird = (_at(ctx, field, sx, sy, tri) for sx, sy in spots)
        billy = copy_model(ctx, field, *BILLY_MODEL)
        bird = copy_model(ctx, field, *CHOCOBO_MODEL)
        add_npc(ctx, field, "billy", billy, pos_billy, facing, _ride(ctx, wm_entry))
        add_npc(ctx, field, "ridechoc", bird, pos_bird, facing, _ride(ctx, wm_entry),
                main=[Op(b) for b in CHOCOBO_YELLOW])
        _mount_on_arrival(ctx, wm_entry)

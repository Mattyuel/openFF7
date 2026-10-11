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
branch for each exit used here gets a block appended in the script's zero
padding: if bit 0x3F0 (bank 1 byte 126 bit 0): op_300 4; op_30C; then the
branch's usual `goto L083D`.

The ride costs 100 gil (CHGLD/GOLDD). The chocobo model's base colour isn't
yellow: like the cargo ship's chocobo (fship_5), it is tinted yellow with
KAWAI 06 in its main script.
"""
from _recruit import say
from _travel import add_npc, beside, choice_menu, copy_model

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
# fship_5 'cho' main script, yellow (var[1][126] bit 2) case: tint, apply.
YELLOW = [bytes.fromhex("28180600001e000f00c4ff1e000f00c4ff01000100010001"),   # KAWAI 06 colour
          bytes.fromhex("240100"),                                           # WAIT 1
          bytes.fromhex("28040601"),                                         # KAWAI 06 apply
          bytes.fromhex("29")]                                               # KAWIW
WILD_RIDE_BIT_ADDR = 0x3F0       # the same bit as the world map script sees it
WILD_CHOCOBO_MODEL = 4
WM_SPECIAL_ENTRY = 0x6           # push_special 6 = the wmN field id you arrived by

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
        return choice_menu(sec, "Choco Billy\n\u201cRide a chocobo? %d gil.\u201d" % PRICE,
                           ["Giddyap!", "Not now."], [go, None])
    return talk


def _mount_on_arrival(ctx, wm_entry):
    """wm0.ev: in the branch for arriving by `wm_entry`, mount the wild chocobo
    if its bit is set (see the module docstring)."""
    ev = EvPatcher(ctx.wm_file("wm0.ev"))
    body, _else = ev.branch_for(WM_SPECIAL_ENTRY, ctx.maplist.index(wm_entry))
    exit_goto = next(x for x in body if x.op == 0x200)
    block = [0x100, 0x114, WILD_RIDE_BIT_ADDR, 0x201, exit_goto.arg,    # if bit:
             0x100, 0x110, WILD_CHOCOBO_MODEL, 0x300, 0x30C,               #   model 4, mount
             0x200, exit_goto.arg]                                          # back to the branch's exit
    ev.set_word(exit_goto.pos + 1, ev.append(block))
    ctx.wm_file("wm0.ev")[:] = ev.build()


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
        add_npc(ctx, field, "ridechoc", bird, pos_bird, 0x40, _ride(ctx, wm_entry),
                main=[Op(b) for b in YELLOW])
        _mount_on_arrival(ctx, wm_entry)

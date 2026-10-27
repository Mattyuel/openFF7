"""Buggy for sale at Costa del Sol's town exit (del2): 1000 gil, then you
leave town already driving it, and it stays yours (as after the Gold
Saucer chocobo race in the original).

How the original grants it (crcin_2, after winning the race): BITON bank 1
byte 127 bit 0 (buggy owned, world map bit 0x3F8) and bit 1 (riding it,
0x3F9), then MAPJUMP to a world map entry with x = y = 0. wm0.ev already
handles the rest: its branch for arriving from Costa del Sol (push_special 6
== field id 13, wm12) mounts the buggy when both bits are set *before*
placing the player (checked below), and every world map load creates the
buggy object while 0x3F8 is set. No story progress check is involved. The
buggy breakdown is suppressed by new-game flags (3,207,1/2).
"""
from _recruit import say
from _travel import add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op
from ff7.walkmesh import Walkmesh
from ff7.worldmap import EvPatcher

FIELD, EXIT_ENTRY = "del2", "wm12"
SELLER_MODEL = ("gldst", 11)          # sub_dio: Dio, who gives the buggy in the original
SELLER_AT, NEAR_TRI = (-1100, -120), 43   # by the world map arrival (-1125, -223), ~290 from the exit line
FACING_DOWN = 0x30                    # ff7.camera.facing_screen at the arrival
PRICE = 1000
BUGGY = (1, 127)                      # bank 1 byte 127
OWNED, RIDING = 0, 1                  # wm bits 0x3F8 / 0x3F9
GIL_LO, GIL_HI = (6, 0xF8), (6, 0xFA)


def _talk(ctx):
    def build(sec):
        end = [Op(b"\x33\x00"), asm.ret()]
        face = [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]   # UC 01, PTURA, WAIT
        sold, ok, done = asm.nop(), asm.nop(), asm.nop()
        go = [Op(bytes([0x3B, 0x66, GIL_LO[1], GIL_HI[1]])),                     # CHGLD lo, hi
              asm.if_word(GIL_HI, "==", 0, ok),                                  # >= 65536 gil: fine
              asm.if_word(GIL_LO, "<", PRICE, ok)]
        go += say(sec, "Buggy Salesman\n\u201cThat's %d gil, friend. Come back\n when your wallet's ready.\u201d" % PRICE)
        go += [asm.goto(done), ok,
               Op(bytes([0x3A, 0x00]) + PRICE.to_bytes(4, "little")),             # GOLDD
               asm.biton(BUGGY, OWNED), asm.biton(BUGGY, RIDING),
               Op(b"\x33\x00"),                                                  # UC 00 before leaving
               asm.mapjump(ctx.maplist.index(EXIT_ENTRY), 0, 0, 0, 0),
               done]
        ops = face + [asm.if_byte(BUGGY, "bit_off", OWNED, sold)]               # already sold -> chat
        ops += choice_menu(sec, "Buggy Salesman\n\u201cOne careful owner! Never broke\n down. Much. %d gil?\u201d" % PRICE,
                           ["I'll take it!", "Just looking."], [go, None])
        ops += [sold] + say(sec, "Buggy Salesman\n\u201cHow's she driving? Don't tell\n me if she isn't.\u201d") + end
        return ops
    return build


def _check_worldmap(ctx):
    ev = EvPatcher(ctx.wm_file("wm0.ev"))
    body, _ = ev.branch_for(0x6, ctx.maplist.index(EXIT_ENTRY))
    words = [(x.op, x.arg) for x in body]
    assert (0x114, 0x3F8) in words and (0x114, 0x3F9) in words and (0x110, 6) in words \
        and (0x30C, None) in words, "wm0: Costa del Sol arrival no longer mounts the buggy"


def apply(ctx):
    _check_worldmap(ctx)
    mesh = Walkmesh(ctx.field(FIELD).section("walkmesh"))
    x, y = SELLER_AT
    tri = next(t for t in mesh.nearby(NEAR_TRI, 6) if mesh.contains(t, x, y))
    model = copy_model(ctx, FIELD, *SELLER_MODEL)
    add_npc(ctx, FIELD, "buggy", model, (x, y, mesh.height(tri, x, y), tri), FACING_DOWN, _talk(ctx))

"""Gift shops: the Gift Merchant sells the Honey Bee gifts (_honey_bee_gifts:
12 new key items, ids 51-62) in Wall Market, Costa del Sol, Cosmo Canyon and
Wutai, three gifts each (one of each hidden type). The gifts' names and
descriptions are written into kernel2.bin (key item sections 15 / 7, blank
in the original game; the build mirrors them into KERNEL.BIN).

A gift is a key item bit, so you hold one of each at most: a gift you already
hold can't be bought again until you've given it. Buying checks the gil
(CHGLD, as 640), takes it (GOLDD) and sets the bit.
"""
import struct

import _honey_bee_gifts as gifts
from _recruit import SOUND_ITEM, say, sound
from _travel import CHOICE, add_npc, copy_model, window

from ff7 import asm
from ff7.camera import Camera, facing_screen
from ff7.script import Op
from ff7.text import decode, encode
from ff7.walkmesh import Walkmesh

NAME = "Gift Merchant"
MODEL = ("blin60_1", 3)                  # shinra_onna: the woman on Shinra HQ floor 60 (user)
GIL_LO, GIL_HI = (6, 0xF8), (6, 0xFA)    # temp words for CHGLD (as 280 / 640)
KEY_NAMES, KEY_DESC = 15, 7              # kernel2 sections


def _gil(n):
    return "{:,}".format(n)


def _key_bit(j):
    k = gifts.FIRST_KEY_ITEM + j
    return (1, 64 + k // 8), k % 8


def _kernel_text(ctx):
    k2 = ctx.kernel2()
    for j, (name, desc, _, _, _) in enumerate(gifts.GIFTS):
        k = gifts.FIRST_KEY_ITEM + j
        assert decode(k2.get(KEY_NAMES, k)) == "" and decode(k2.get(KEY_DESC, k)) == "", k   # unused slot
        k2.set(KEY_NAMES, k, encode(name))
        k2.set(KEY_DESC, k, encode(desc))


def _build_talk(sec, shop):
    items = [(j, g) for j, g in enumerate(gifts.GIFTS) if g[4] == shop]
    assert sorted(g[2] for _, g in items) == [0, 1, 2], shop      # one of each type
    end = [Op(b"\x33\x00"), asm.ret()]
    ops = [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]     # UC 01, face Cloud
    top, bought, short, have = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    ops += say(sec, NAME + "\n“Gifts for the ladies, handsome!\n Every one wrapped with a bow.”")
    ops.append(top)
    prompt = NAME + "\n“Something lovely for someone special?”"
    options = ["%s  %s gil" % (g[0], _gil(g[3])) for _, g in items] + ["Nothing."]
    text = prompt + "".join("\n{CHOICE}" + o for o in options)
    first = len(prompt.split("\n"))
    ops += [window(text), asm.ask(0, sec.add_string(encode(text)), first, first + len(options) - 1, CHOICE)]
    for k, (j, (name, _, _, price, _)) in enumerate(items):
        kv, bit = _key_bit(j)
        nxt, ok, lshort = asm.nop(), asm.nop(), asm.nop()
        hi, lo = price >> 16, price & 0xFFFF
        ops += [asm.if_byte(CHOICE, "==", first + k, nxt),
                asm.if_byte(kv, "bit_off", bit, have),                          # already holding one
                Op(bytes([0x3B, 0x66, GIL_LO[1], GIL_HI[1]])),                  # CHGLD lo, hi
                asm.if_word(GIL_HI, "<=", hi, ok),                               # more than hi:16 -> ok
                asm.if_word(GIL_HI, "==", hi, lshort),                           # less -> short
                asm.if_word(GIL_LO, ">=", lo, lshort),
                ok,
                Op(bytes([0x3A, 0x00]) + struct.pack("<I", price)),             # GOLDD
                asm.biton(kv, bit), sound(SOUND_ITEM), asm.goto(bought),
                lshort, asm.goto(short), nxt]
    ops += end
    ops += [bought] + say(sec, NAME + "\n“Wrapped and ready. She's a lucky\n girl, whoever she is.”") + [asm.goto_back(top)]
    ops += [short] + say(sec, NAME + "\n“Oh dear, you're a little short.\n Love isn't cheap, sweetheart.”") + [asm.goto_back(top)]
    ops += [have] + say(sec, NAME + "\n“You already have one of those!\n Give it to her first.”") + [asm.goto_back(top)]
    return ops


def apply(ctx):
    _kernel_text(ctx)
    for shop, (field, (x, y)) in gifts.SHOPS.items():
        f = ctx.field(field)
        mesh = Walkmesh(f.section("walkmesh"))
        tri = mesh.find(x, y)
        assert tri is not None, (field, x, y)
        z = mesh.height(tri, x, y)
        model = copy_model(ctx, field, *MODEL)
        add_npc(ctx, field, "giftshop", model, (x, y, z, tri), facing_screen(Camera(f.sections[1]), x, y, z, (0, 1)),
                lambda sec, shop=shop: _build_talk(sec, shop))

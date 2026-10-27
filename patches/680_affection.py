"""(user) The affection list: Square in a field shows every Honey Bee girl's name, personality and
affection, "????" for one you haven't hired or dated yet (no affection and not hired). Not a
menu: a big two-page text box.

- exe: the field's Triangle check (0x63C46C: the menu opens when Triangle is held and the menu is
  allowed, [0xCC0DBC] == 0 and [0xCC1638] == 0) is hooked (quest_menu.asm `s_hook`, CODE+50):
  Square newly pressed under the same conditions sets bit 2 of field var[1][213] (`FLAG`; 213 is the
  debug flags byte, bits 2-6 unused).
- field opcode 0x1E AFFTEXT [text id] (quest_menu.asm `a_op`, CODE+45) writes the list into that
  text of the loaded field from AFFDATA (built here): the header, then a line per girl, the second
  page from girl `PER_PAGE`.
- every field with room gets an entity `affmenu` (init clears the flag; its main waits for the flag,
  clears it, UC 01, AFFTEXT into its placeholder text, the window, UC 00), except the movie sets
  (Square is the hold / slap / "there" prompt there).
"""
import importlib
import struct

import _cid as CID
from _config import HB_AFFECTION, HB_HIRED
from _honey_bee_data import GIRLS
from ff7 import asm
from ff7.script import Op, Script
from ff7.text import encode

CODE, OP_TABLE, UNUSED_HANDLER = 0xFDD000, 0x9055A0, 0x6107E1
AFFDATA = 0xFE8000                   # = AFFDATA in quest_menu.asm
AFFTEXT, ENTRY_OP, ENTRY_HOOK = 0x1E, 45, 50
HOOK_VA, HOOK_OLD = 0x63C46C, bytes.fromhex("8b55e883e210")    # mov edx,[ebp-0x18]; and edx,0x10
VARS = 0xDC08DC                      # field var bank 1, offset 0
FLAG = ((1, 213), 2)
PER_PAGE = 10
HEADER = "Girls (personality): affection"
UNKNOWN, OF = "????", "/20"
SKIP = {"whitebg1", "whitebg2", "blin69_2", "trap", "junmon", "subin_4",       # the movie sets (670 / 672)
        "qe", "pass", "hyou14", "xmvtes", "fallp", "m_endo", "rcktin7",       # (rcktin7: 673's Blast-off set)
        "blackbge", "shpin_22", "nivgate3", "hyou12", "blackbg3", "blackbg4",
        "blackbg5", "blackbg6", "blackbg8", "blackbgh", "blackbg9", "blackbgc"}   # 677's scene lab, 678 / 679's group sets; (user) every
        # parody film's set (683-688: Square is a prompt there)
MAX_TEXTS, MAX_ENTITIES = 254, 48


# (user, since) Cid after the girls: "????" until you've met him (`_cid.MET`) or he has affection
PEOPLE = [dict(name=g["name"], tag=g["tag"], aff=HB_AFFECTION[i], known=((HB_HIRED[0], HB_HIRED[1] + i // 8), i % 8))
          for i, g in enumerate(GIRLS)] + [dict(name=CID.NAME, tag="friend", aff=CID.AFFECTION, known=CID.MET)]


def _label(g):
    return "%s (%s): " % (g["name"], g["tag"])


def _longest():
    """The longest list the opcode can write (every girl known, two-digit affection), as text."""
    lines = [_label(g) + "20" + OF for g in PEOPLE]
    return HEADER + "\n" + "\n".join(lines[:PER_PAGE]) + "{NEW}" + HEADER + "\n" + "\n".join(lines[PER_PAGE:])


def _data():
    strings = [HEADER, UNKNOWN, OF] + [_label(g) for g in PEOPLE]
    head = 20 + 16 * len(PEOPLE)
    ptrs, blob, at = [], b"", AFFDATA + head
    for s in strings:
        e = encode(s)
        assert e[-1] == 0xFF, s
        ptrs.append(at)
        blob += e
        at += len(e)
    out = struct.pack("<3I2I", ptrs[0], ptrs[1], ptrs[2], len(PEOPLE), PER_PAGE)
    for i, g in enumerate(PEOPLE):
        (bank, aff), ((kbank, kaddr), kbit) = g["aff"], g["known"]
        assert bank == 1 and kbank == 1
        out += struct.pack("<3IB3x", ptrs[3 + i], VARS + aff, VARS + kaddr, 1 << kbit)
    assert len(out) == head
    return out + blob


def _entity(sec, hb, placeholder):
    tid = sec.add_string(placeholder)
    (fv, bit) = FLAG
    top, idle = hb._w(1), asm.nop()
    main = [top, asm.if_byte(fv, "bit_on", bit, idle), asm.bitoff(fv, bit), hb._uc(1),
            Op(bytes([AFFTEXT, tid])), hb._window(_longest(), 0), asm.message(0, tid), hb._uc(0),
            idle, asm.goto_back(top), asm.ret()]
    sec.add_entity("affmenu", {0: [asm.bitoff(fv, bit), asm.ret()] + main})


def apply(ctx):
    hb = importlib.import_module("620_honey_bee")
    exe = ctx.exe()
    assert exe.payload[CODE + ENTRY_OP - exe.section_va] == 0xE9 and exe.payload[CODE + ENTRY_HOOK - exe.section_va] == 0xE9
    exe.place_at(AFFDATA, _data(), "affection_data")
    exe.patch_u32(OP_TABLE + AFFTEXT * 4, UNUSED_HANDLER, CODE + ENTRY_OP, "field opcode 1E: AFFTEXT")
    rel = CODE + ENTRY_HOOK - (HOOK_VA + 5)
    exe.patch(HOOK_VA, HOOK_OLD, b"\xE9" + struct.pack("<i", rel) + b"\x90", "field Triangle check -> Square hook")
    longest = encode(_longest())
    placeholder = encode(" " * (len(longest) - 1))
    assert len(placeholder) == len(longest)
    added = 0
    for name in [n for n in ctx.maplist if (n in ctx.flevel or n in ctx._fields) and n not in SKIP]:
        f = ctx.field(name)
        try:
            sec = Script.parse(f.sections[0])
        except ValueError:
            continue
        if struct.unpack_from("<H", sec.tail, 0)[0] > MAX_TEXTS or len(sec.entry) >= MAX_ENTITIES:
            continue
        _entity(sec, hb, placeholder)
        try:
            data = sec.build()
        except (ValueError, struct.error):
            continue
        f.sections[0] = data
        added += 1
    print("  680: the affection list in %d fields" % added)

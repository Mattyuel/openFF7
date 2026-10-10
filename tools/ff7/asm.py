"""Constructors for new field script instructions (returns script.Op objects).

Variables are given as (bank, address) tuples; plain ints are literals.
Banks follow the opcode bank nibble used in the disassembly (var[bank][addr]).
"""
import struct

from .script import Op

CMP = {"==": 0, "!=": 1, ">": 2, "<": 3, ">=": 4, "<=": 5, "&": 6, "^": 7, "|": 8,
       "bit_on": 9, "bit_off": 10}


def _bank(x):
    return (x[0], x[1]) if isinstance(x, tuple) else (0, x)


def nop():
    return Op(b"\x5F")


def ret():
    return Op(b"\x00")


def setbyte(dst, value):
    db, da = dst
    sb, sv = _bank(value)
    return Op(bytes([0x80, db << 4 | sb, da, sv & 0xFF]))


def setword(dst, value):
    db, da = dst
    sb, sv = _bank(value)
    return Op(bytes([0x81, db << 4 | sb, da]) + struct.pack("<H", sv & 0xFFFF))


def biton(dst, bit):
    db, da = dst
    return Op(bytes([0x82, db << 4, da, bit]))


def bitoff(dst, bit):
    db, da = dst
    return Op(bytes([0x83, db << 4, da, bit]))


def if_byte(a, cmp, b, else_target):
    """if not (a cmp b) jump to else_target (8-bit compare)."""
    ab, av = _bank(a)
    bb, bv = _bank(b)
    return Op(bytes([0x14, ab << 4 | bb, av, bv, CMP[cmp], 0]), target=else_target)


def if_word(a, cmp, b, else_target):
    """if not (a cmp b) jump to else_target (16-bit unsigned compare)."""
    ab, av = _bank(a)
    bb, bv = _bank(b)
    return Op(bytes([0x18, ab << 4 | bb]) + struct.pack("<HH", av, bv) + bytes([CMP[cmp], 0]),
              target=else_target)


def goto(target):
    """Forward jump. (Backward jumps: use goto_back.)"""
    return Op(b"\x10\x00", target=target)


def goto_back(target):
    return Op(b"\x12\x00", target=target)


def mapjump(field_id, x, y, triangle, direction):
    return Op(bytes([0x60]) + struct.pack("<HhhH", field_id, x, y, triangle) + bytes([direction]))


def message(window, text_id):
    return Op(bytes([0x40, window, text_id]))


def ask(window, text_id, first, last, dst):
    """ASK: show a choice; selected line index goes to var dst (bank, addr)."""
    db, da = dst
    return Op(bytes([0x48, db, window, text_id, first, last, da]))


def add_item(item, qty):
    return Op(bytes([0x58, 0x00]) + struct.pack("<H", item) + bytes([qty]))


def party(c1, c2=0xFE, c3=0xFE):
    """PRTYE: set the active party (0xFE/0xFF = empty slot)."""
    return Op(bytes([0xCA, c1, c2, c3]))


def party_add(char):
    return Op(bytes([0xC8, char]))


def party_remove(char):
    return Op(bytes([0xC9, char]))


def member_unlock(char):
    """MMBUK: allow character to be selected in the PHS/party menu."""
    return Op(bytes([0xCF, char]))


def member_lock(char):
    return Op(bytes([0xCE, char]))


def battle(formation):
    return Op(bytes([0x70, 0x00]) + struct.pack("<H", formation))


def battles_enabled(on):
    """BTLON: random battles on/off (the opcode's operand is 'disabled')."""
    return Op(bytes([0x71, 0 if on else 1]))

"""Which savemap bytes (field var banks 1-4) the game uses, and which are free.

`usage(flevel, world_lgp, exe)` scans every field script, the world map's .ev
scripts and the exe, and returns a `Usage`: per savemap byte the field reads /
writes (with the bits, when every access is to known bits), world map uses and
exe absolute references. `ff7tool.py save-usage` compares the original game with
the build to show what the open world freed.

Field operands come from the exe itself: `FIELD_OPERANDS` lists, per opcode, the
calls its handler (table 0x9055A0) makes to the operand getters / setters
0x60F750 (G 8-bit operand), 0x60FD6C (G 16-bit), 0x60FA7D (S 8), 0x61031E (S 16)
as (G|S, literal width, nibble selector, operand offset): a literal operand is
8 or 16 bits, a var's address always one byte at that offset (handler 0x60FD6C). Selector 2k-1 = byte k's
high nibble, 2k = its low nibble (bank 0 = a literal). Read with capstone in
2026-10; the IF ops (own code), SPTYE / GTPYE (a loop), SPECIAL (a switch) and
MPARA / MPRA2 (store the var for the text window to read later) are added by hand.
SETX / GETX / SEARCHX index a bank at run time: reported as `indirect`.
"""
import collections
import struct

from .disasm import disassemble
from .worldmap import EvScript

# opcode bank nibble -> savemap bank 1-4 (5/6/7/15 are temporary or bank 5: not field-saved)
SAVE_BANK = {1: 1, 2: 1, 3: 2, 4: 2, 11: 3, 12: 3, 13: 4, 14: 4}
SIXTEEN = {2, 4, 6, 12, 14, 15}
SAVEMAP_BASE = 0xDBFD38          # savemap in memory
BANK1 = 0x0BA4                   # bank 1's offset in the savemap

FIELD_OPERANDS = {
    0x09: [('G', 8, 3, 8), ('G', 16, 2, 6), ('G', 16, 1, 4), ('G', 8, 6, 13), ('G', 16, 5, 11), ('G', 16, 4, 9)],
    0x23: [('S', 16, 2, 2)],
    0x25: [('G', 8, 1, 4), ('G', 8, 2, 5), ('G', 8, 3, 6), ('G', 16, 4, 7)],
    0x2C: [('G', 16, 1, 3)],
    0x2D: [('G', 16, 1, 3), ('G', 16, 2, 5)],
    0x37: [('G', 16, 1, 3), ('G', 16, 2, 5)],
    0x38: [('G', 8, 1, 3), ('G', 8, 2, 4), ('G', 8, 4, 5)],
    0x39: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0x3A: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0x3B: [('S', 16, 1, 2), ('S', 16, 2, 3)],
    0x41: [('G', 8, 1, 3), ('G', 8, 2, 4)],
    0x42: [('G', 8, 1, 3), ('G', 16, 2, 4)],
    0x45: [('G', 16, 2, 3)],
    0x47: [('G', 16, 2, 3)],
    0x48: [('G', 8, 2, 6), ('S', 8, 2, 6)],
    0x49: [('G', 8, 2, 3)],
    0x4D: [('G', 16, 2, 3)],
    0x4F: [('G', 16, 2, 3)],
    0x56: [('G', 8, 1, 3), ('S', 8, 2, 4), ('S', 8, 3, 5), ('S', 8, 4, 6)],
    0x57: [('G', 8, 1, 3), ('G', 8, 2, 4), ('G', 8, 3, 5), ('G', 8, 4, 6)],
    0x58: [('G', 8, 2, 4), ('G', 16, 1, 2)],
    0x59: [('G', 8, 2, 4), ('G', 16, 1, 2)],
    0x5A: [('G', 16, 1, 2), ('S', 8, 2, 4)],
    0x5B: [('G', 8, 1, 3), ('G', 8, 2, 4), ('G', 8, 3, 5), ('G', 8, 4, 6)],
    0x5C: [('G', 8, 1, 3), ('G', 8, 2, 4), ('G', 8, 3, 5), ('G', 8, 4, 6)],
    0x5D: [('G', 8, 1, 4), ('G', 8, 2, 5), ('G', 8, 3, 6), ('G', 8, 4, 7), ('S', 8, 6, 9)],
    0x5E: [('G', 8, 1, 4), ('G', 8, 2, 5), ('G', 8, 3, 6), ('G', 8, 4, 7)],
    0x62: [('G', 16, 2, 2)],
    0x63: [('G', 16, 2, 2)],
    0x64: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0x66: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 4, 7)],
    0x68: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 4, 7)],
    0x6A: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0x6B: [('G', 8, 1, 3), ('G', 8, 2, 4), ('G', 8, 4, 5)],
    0x6E: [('S', 16, 2, 2)],
    0x6F: [('G', 16, 2, 2)],
    0x70: [('G', 16, 2, 2)],
    0x73: [('S', 8, 2, 3)],
    0x74: [('S', 8, 2, 3)],
    0x75: [('S', 16, 1, 4), ('S', 16, 2, 5), ('S', 16, 3, 6), ('S', 16, 4, 7)],
    0x76: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x77: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x78: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x79: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x7A: [('G', 8, 2, 2), ('S', 8, 2, 2)],
    0x7B: [('G', 16, 2, 2), ('S', 16, 2, 2)],
    0x7C: [('G', 8, 2, 2), ('S', 8, 2, 2)],
    0x7D: [('G', 16, 2, 2), ('S', 16, 2, 2)],
    0x7F: [('G', 8, 2, 2)],
    0x80: [('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x81: [('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x82: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x83: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x84: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x85: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x86: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x87: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x88: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x89: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x8A: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x8B: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x8C: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x8D: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x8E: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x8F: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x90: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x91: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x92: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x93: [('G', 8, 1, 2), ('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x94: [('G', 16, 1, 2), ('G', 16, 2, 3), ('S', 16, 1, 2)],
    0x95: [('G', 8, 2, 2), ('S', 8, 2, 2)],
    0x96: [('G', 16, 2, 2), ('S', 16, 2, 2)],
    0x97: [('G', 8, 2, 2), ('S', 8, 2, 2)],
    0x98: [('G', 16, 2, 2), ('S', 16, 2, 2)],
    0x99: [('S', 8, 2, 2)],
    0x9A: [('G', 8, 2, 3), ('S', 8, 1, 2)],
    0x9B: [('G', 16, 2, 3), ('S', 8, 1, 2)],
    0x9C: [('G', 8, 2, 4), ('G', 8, 4, 5), ('S', 16, 1, 3)],
    0xA5: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7), ('G', 16, 4, 9)],
    0xA6: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7)],
    0xA7: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7)],
    0xA8: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0xA9: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0xAD: [('G', 16, 1, 2), ('G', 16, 2, 4)],
    0xB2: [('G', 16, 2, 2)],
    0xB3: [('G', 8, 2, 2)],
    0xB4: [('G', 8, 2, 2)],
    0xB5: [('G', 16, 2, 2)],
    0xB7: [('S', 8, 2, 3)],
    0xB8: [('S', 16, 1, 3), ('S', 16, 2, 4)],
    0xB9: [('S', 16, 2, 3)],
    0xBD: [('G', 16, 2, 2)],
    0xC0: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7), ('G', 16, 4, 9)],
    0xC1: [('S', 16, 1, 4), ('S', 16, 2, 5), ('S', 16, 3, 6), ('S', 16, 4, 7)],
    0xC2: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7), ('G', 16, 4, 9)],
    0xC3: [('G', 16, 4, 10), ('G', 16, 1, 4), ('G', 16, 2, 6), ('G', 16, 3, 8)],
    0xC5: [('G', 8, 2, 2)],
    0xC6: [('G', 8, 2, 2)],
    0xD3: [('G', 16, 1, 4), ('G', 16, 2, 6), ('G', 16, 3, 8), ('G', 16, 4, 10), ('G', 16, 5, 12), ('G', 16, 6, 14)],
    0xD4: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7), ('S', 16, 4, 9)],
    0xD5: [('G', 16, 1, 3), ('G', 16, 2, 5), ('G', 16, 3, 7), ('S', 16, 4, 9)],
    0xD6: [('G', 16, 2, 2)],
    0xD7: [('G', 16, 2, 2)],
    0xDA: [('G', 16, 1, 5), ('G', 16, 2, 7), ('G', 16, 3, 9), ('G', 16, 4, 11), ('G', 16, 6, 13)],
    0xDF: [('G', 8, 6, 10), ('G', 8, 1, 6), ('G', 8, 2, 7), ('G', 8, 3, 8), ('G', 8, 4, 9)],
    0xE0: [('G', 8, 1, 2), ('G', 8, 2, 3)],
    0xE1: [('G', 8, 1, 2), ('G', 8, 2, 3)],
    0xE2: [('G', 8, 2, 2)],
    0xE3: [('G', 8, 2, 2)],
    0xE4: [('G', 8, 2, 2)],
    0xE5: [('G', 8, 1, 2), ('G', 8, 2, 3)],
    0xE6: [('G', 8, 2, 3), ('G', 8, 1, 2)],
    0xE7: [('G', 8, 1, 2), ('G', 8, 2, 3)],
    0xE8: [('G', 8, 1, 3), ('G', 8, 2, 4), ('G', 8, 4, 5)],
    0xE9: [('G', 8, 1, 4), ('G', 8, 2, 5), ('G', 8, 3, 6), ('G', 8, 4, 7), ('G', 8, 5, 8)],
    0xEA: [('G', 8, 1, 4), ('G', 8, 2, 5), ('G', 8, 3, 6), ('G', 8, 4, 7), ('G', 8, 5, 8)],
    0xED: [('G', 8, 4, 7), ('G', 8, 1, 5), ('G', 8, 2, 6)],
    0xEE: [('G', 8, 4, 7), ('G', 8, 1, 5), ('G', 8, 2, 6)],
    0xEF: [('G', 8, 6, 10), ('G', 8, 1, 6), ('G', 8, 2, 7), ('G', 8, 3, 8), ('G', 8, 4, 9)],
    0xF1: [('G', 8, 2, 4), ('G', 16, 1, 2)],
    0xF2: [('G', 8, 1, 5), ('G', 16, 2, 6), ('G', 16, 3, 8), ('G', 16, 4, 10), ('G', 16, 6, 12)],
    0xF7: [('S', 16, 1, 2), ('S', 8, 2, 3)],
    0xFA: [('S', 16, 2, 2)],
    0xFD: [('G', 16, 3, 4), ('G', 16, 4, 6)],
    0xFE: [('S', 8, 2, 2)],
}
FIELD_OPERANDS[0x0A] = [("G", 8, k + 1, k + 3) for k in range(3)]        # SPTYE
FIELD_OPERANDS[0x0B] = [("S", 8, k + 1, k + 3) for k in range(3)]        # GTPYE
for _op in (0x14, 0x15):
    FIELD_OPERANDS[_op] = [("G", 8, 1, 2), ("G", 8, 2, 3)]               # IFUB(L)
for _op in (0x16, 0x17, 0x18, 0x19):
    FIELD_OPERANDS[_op] = [("G", 16, 1, 2), ("G", 16, 2, 4)]             # IFSW/IFUW(L)
SPECIAL_OPERANDS = {0xF6: [("G", 8, 3, 3)], 0xF7: [("S", 8, 4, 3)], 0xF8: [("G", 8, 4, 3)]}
INDIRECT = {0x9D: "SETX", 0x9E: "GETX", 0x9F: "SEARCHX"}
# Savemap use the scans can't see (the exe indexes from a base it names once).
KNOWN = {
    (4, 184, 231): "world map object slots (exe 0x76609E writes, 0x76616A reads; 6 x 8 bytes)",
    (4, 232, 243): "zeroed on world map entry (exe)",
}
NEAR_EXE = 8     # free bytes this close after an exe reference may be part of its table


def known(bank, off):
    for (b, lo, hi), why in KNOWN.items():
        if b == bank and lo <= off <= hi:
            return why
    return None


_BIT_OPS = {0x82, 0x83, 0x84}    # BITON / BITOFF / BITXOR: dst var, bit literal


def _nibble(raw, sel):
    i = (sel + 1) // 2
    if i >= len(raw):
        return 0
    return raw[i] >> 4 if sel % 2 else raw[i] & 15


class Usage:
    """bank (1-4) -> offset -> {'r': set(fields), 'w': set(fields), 'bits': set or None}."""

    def __init__(self):
        self.bytes = {b: collections.defaultdict(
            lambda: {"r": set(), "w": set(), "bits": set(), "whole": False, "wm": 0, "exe": []})
            for b in (1, 2, 3, 4)}
        self.indirect = []       # (field, op name, bank)

    def mark(self, bank, off, kind, where, bits=None, size=1):
        for k in range(size):
            if not 0 <= off + k < 256:
                continue
            e = self.bytes[bank][off + k]
            if kind in "rw":
                e[kind].add(where)
            elif kind == "wm":
                e["wm"] += 1
            else:
                e["exe"].append(where)
            if bits is None:
                e["whole"] = True
            else:
                e["bits"].update(bits)

    def used(self, bank, off):
        e = self.bytes[bank].get(off)
        return bool(e and (e["r"] or e["w"] or e["wm"] or e["exe"]))

    def free_bits(self, bank, off):
        """Bits nothing touches (0-8 of them); 8 when the byte is unused."""
        e = self.bytes[bank].get(off)
        if not e or not self.used(bank, off):
            return set(range(8))
        if e["whole"] or e["wm"] or e["exe"]:
            return set()
        return set(range(8)) - e["bits"]


def _bits_of_if(ins):
    """Bits an IF tests when it compares a var with a literal bit / mask, else None."""
    r = ins.raw
    if ins.op not in (0x14, 0x15) or r[1] & 15:
        return None
    cmp, b = r[4], r[3]
    if cmp in (9, 10):
        return {b} if b < 8 else None
    if cmp == 6:                 # '&' mask
        return {k for k in range(8) if b >> k & 1}
    return None


_JUMPS = {0x10, 0x11, 0x12, 0x13}
_ENDS = {0x00, 0x07, 0xFF}       # RET, RETTO, GAMEOVER
_IFS = {0x14, 0x15, 0x16, 0x17, 0x18, 0x19}


def _literal_if(ins):
    """True / False for an IF comparing two literals (a pinned progress test), else None."""
    r, op = ins.raw, ins.op
    if r[1] != 0:
        return None
    if op in (0x14, 0x15):
        a, b, cmp = r[2], r[3], r[4]
    else:
        a, b = struct.unpack_from("<hh" if op in (0x16, 0x17) else "<HH", r, 2)
        cmp = r[6]
    return {0: a == b, 1: a != b, 2: a > b, 3: a < b, 4: a >= b, 5: a <= b, 6: bool(a & b),
            7: bool(a ^ b), 8: bool(a | b), 9: bool(a >> b & 1) if 0 <= b < 16 else False,
            10: not (a >> b & 1) if 0 <= b < 16 else True}.get(cmp)


def reachable(sec, code):
    """The instructions that can run: from every entity script slot (and script 0's
    main after its first RET), following jumps, with IFs between two literals decided
    (pinning turns progress tests into those, leaving their other branch dead)."""
    at = {ins.pos: ins for ins in code}
    order = [ins.pos for ins in code]
    nxt = dict(zip(order, order[1:]))
    starts = set(p for ent in sec.scripts for p in ent)
    for ent in sec.scripts:
        p = ent[0]
        while p in at and at[p].op != 0x00:
            p = nxt.get(p)
        if p in nxt:
            starts.add(nxt[p])
    seen, todo = set(), [p for p in starts if p in at]
    while todo:
        p = todo.pop()
        while p in at and p not in seen:
            seen.add(p)
            ins = at[p]
            if ins.op in _ENDS:
                break
            if ins.op in _JUMPS:
                todo.append(ins.target)
                break
            if ins.target is not None:
                lit = _literal_if(ins) if ins.op in _IFS else None
                if lit is False:
                    todo.append(ins.target)
                    break
                if lit is None:
                    todo.append(ins.target)
            p = nxt.get(p)
    return [at[p] for p in order if p in seen]


def scan_field(usage, name, sec):
    if sec.broken:
        return
    code = disassemble(sec.data, min(sec.script_bounds()), sec.string_offset)
    for ins in reachable(sec, code):
        r, op = ins.raw, ins.op
        if op == 0x0F:
            ops = SPECIAL_OPERANDS.get(r[1], ())
        else:
            ops = FIELD_OPERANDS.get(op, ())
        if op in INDIRECT:
            for sel in (1, 2, 3, 4):
                n = _nibble(r, sel)
                if n in SAVE_BANK:
                    usage.indirect.append((name, INDIRECT[op], SAVE_BANK[n]))
        for gs, width, sel, off in ops:
            n = _nibble(r, sel)
            if n not in SAVE_BANK or off >= len(r):
                continue
            addr = r[off]        # a var's address is always one byte (a literal may be u16)
            bits = None
            if op in _BIT_OPS and gs == "S" or (op in _BIT_OPS and sel == 1):
                b = r[3] if not r[1] & 15 else None
                bits = {b} if b is not None and b < 8 else None
            elif op in (0x14, 0x15) and sel == 1:
                bits = _bits_of_if(ins)
            usage.mark(SAVE_BANK[n], addr, "w" if gs == "S" else "r", name, bits,
                       2 if n in SIXTEEN else 1)


def scan_worldmap(usage, name, ev):
    for c in EvScript(ev).disassemble():
        if c.op == 0x114:
            off, bits, size = c.arg // 8, {c.arg % 8}, 1
        elif c.op == 0x118:
            off, bits, size = c.arg, None, 1
        elif c.op == 0x11C:
            off, bits, size = c.arg, None, 2
        else:
            continue
        for k in range(size):
            o = off + k
            if 0 <= o < 1024:
                usage.mark(o // 256 + 1, o % 256, "wm", name, bits)


def scan_exe(usage, data):
    """Every 4-byte value in the exe that points into field banks 1-4 (code and data;
    an indexed base like [eax+X] only shows X)."""
    lo = SAVEMAP_BASE + BANK1
    from .exepatch import _pe, IMAGE_BASE
    pe, opt, table = _pe(data)
    for s in range(struct.unpack_from("<H", data, pe + 6)[0]):
        vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", data, table + 40 * s + 8)
        chunk = data[rptr:rptr + rsize]
        for o in range(len(chunk) - 3):
            v = chunk[o] | chunk[o + 1] << 8 | chunk[o + 2] << 16 | chunk[o + 3] << 24
            if lo <= v < lo + 1024:
                d = v - lo
                usage.mark(d // 256 + 1, d % 256, "exe", IMAGE_BASE + vaddr + o)


def usage(flevel, world_lgp=None, exe=None, decompress=None):
    """flevel / world_lgp: ff7.lgp.LGP; exe: bytes; decompress: LZSS function (default lzss.decompress)."""
    from .field import FieldFile, ScriptSection
    from . import lzss
    decompress = decompress or lzss.decompress
    u = Usage()
    for n in flevel.names():
        if "." in n or n == "maplist":
            continue
        try:
            sec = ScriptSection(FieldFile(decompress(flevel[n])).sections[0])
        except ValueError:
            continue
        scan_field(u, n, sec)
    if world_lgp is not None:
        for n in world_lgp.names():
            if n.lower().endswith(".ev"):
                scan_worldmap(u, n, world_lgp[n])
    if exe is not None:
        scan_exe(u, exe)
    return u

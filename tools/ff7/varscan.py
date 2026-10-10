"""Find which savemap variables the original scripts use (to pick free ones)."""
import collections

from .disasm import disassemble
from .worldmap import EvScript

# opcode bank nibble -> savemap bank (1-5); 5/6 are temporary (not saved)
SAVEMAP_BANK = {1: 1, 2: 1, 3: 2, 4: 2, 11: 3, 12: 3, 13: 4, 14: 4, 7: 5, 15: 5}
SIXTEEN = {2, 4, 6, 12, 14, 15}
_ONE_OPERAND = {0x7A, 0x7B, 0x7C, 0x7D, 0x95, 0x96, 0x97, 0x98, 0x99}


def field_usage(script_sections):
    """{savemap_bank: set(byte offsets)} referenced by conditions/assignments."""
    used = collections.defaultdict(set)

    def mark(nibble, addr):
        if nibble in SAVEMAP_BANK:
            used[SAVEMAP_BANK[nibble]].add(addr)
            if nibble in SIXTEEN:
                used[SAVEMAP_BANK[nibble]].add(addr + 1)

    for sec in script_sections:
        if sec.broken:
            continue
        for ins in disassemble(sec.data, min(sec.script_bounds()), sec.string_offset):
            r, op = ins.raw, ins.op
            if op in (0x14, 0x15, 0x16, 0x17, 0x18, 0x19):
                a = ins.args
                mark(a["bank_a"], a["a"])
                mark(a["bank_b"], a["b"])
            elif 0x76 <= op <= 0x99 and op not in (0x7E, 0x7F):
                if op in _ONE_OPERAND:
                    mark(r[1] >> 4 or r[1] & 15, r[2])
                else:
                    mark(r[1] >> 4, r[2])
                    mark(r[1] & 15, r[3])
    return used


def worldmap_usage(ev_data):
    """Savemap byte offsets (relative to bank 1 start, 0x0BA4) used by a .ev script."""
    used = set()
    for c in EvScript(ev_data).disassemble():
        if c.op == 0x114:
            used.add(c.arg // 8)
        elif c.op == 0x118:
            used.add(c.arg)
        elif c.op == 0x11C:
            used.update((c.arg, c.arg + 1))
    return used

"""Script patch helpers used by patches/*.py."""
import struct

from .disasm import PROGRESS_VAR, disassemble

IF_OPS = {0x14, 0x15, 0x16, 0x17, 0x18, 0x19}


def pin_progress(sec, value):
    """Make every story-progress comparison in a script section use a constant.

    `sec` is a ScriptSection. Each `if (var[2][0] <op> literal)` becomes
    `if (value <op> literal)`, so the field behaves as it did at story moment
    `value` regardless of the global progress variable. Instruction lengths do
    not change, so no offsets move. Returns (new section bytes, count).
    """
    data = bytearray(sec.data)
    count = 0
    for ins in disassemble(sec.data, min(sec.script_bounds()), sec.string_offset):
        if ins.op not in IF_OPS:
            continue
        a = ins.args
        if (a["bank_a"], a["a"]) != PROGRESS_VAR or a["bank_b"] != 0:
            continue
        p = ins.pos
        data[p + 1] = a["bank_b"]  # left operand bank -> 0 (literal)
        if ins.op in (0x14, 0x15):
            raise ValueError("8-bit compare against the 16-bit progress variable at 0x%X" % p)
        struct.pack_into("<H", data, p + 2, value & 0xFFFF)
        count += 1
    return bytes(data), count

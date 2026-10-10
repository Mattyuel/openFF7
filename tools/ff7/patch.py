"""Script patch helpers used by patches/*.py."""
import struct

from .disasm import PROGRESS_VAR, disassemble
from .script import Script

IF_OPS = {0x14, 0x15, 0x16, 0x17, 0x18, 0x19}
WORD_IFS = {0x16, 0x17, 0x18, 0x19}
SETWORD = 0x81
# 16-bit arithmetic writes: [op][banks][dst][src u16]
WORD_ARITH = {0x77, 0x79, 0x86, 0x88, 0x8A, 0x8C, 0x8E, 0x90, 0x92, 0x94}
WORD_INCDEC = {0x7B, 0x7D, 0x96, 0x98}  # [op][bank][addr]


def pin_progress(sec, value):
    """Make every story-progress comparison in a script section use a constant.

    `sec` is a ScriptSection. Each `if (var[2][0] <op> literal)` becomes
    `if (value <op> literal)`. Instruction lengths do not change.
    Returns (new section bytes, count). Prefer `localise_progress` for new code.
    """
    data = bytearray(sec.data)
    count = 0
    for ins in disassemble(sec.data, min(sec.script_bounds()), sec.string_offset):
        if ins.op not in WORD_IFS:
            continue
        a = ins.args
        if (a["bank_a"], a["a"]) != PROGRESS_VAR or a["bank_b"] != 0:
            continue
        data[ins.pos + 1] = 0
        struct.pack_into("<H", data, ins.pos + 2, value & 0xFFFF)
        count += 1
    return bytes(data), count


def localise_progress(script, const=None, var=None):
    """Detach a field from the global story-progress variable.

    `script` is a script.Script. Exactly one of:
      const=M    reads of progress become the literal M; writes are removed.
                 The field always behaves as at story moment M.
      var=(b,a)  reads and writes of progress use 16-bit variable var[b][a]
                 instead (b must be a 16-bit bank nibble). A region of fields
                 sharing the variable keeps its own story line (e.g. a quest).
    Returns a dict of counts.
    """
    assert (const is None) != (var is None)
    pb, pa = PROGRESS_VAR
    stats = {"reads": 0, "writes": 0, "removed": 0}
    for op in list(script.ops):
        r = op.raw
        code = r[0]
        if code in WORD_IFS:
            hi, lo = r[1] >> 4, r[1] & 15
            a, = struct.unpack_from("<H", r, 2)
            b, = struct.unpack_from("<H", r, 4)
            if (hi, a) == (pb, pa):
                if const is not None:
                    hi = 0
                    struct.pack_into("<H", r, 2, const & 0xFFFF)
                else:
                    hi = var[0]
                    struct.pack_into("<H", r, 2, var[1])
                stats["reads"] += 1
            if (lo, b) == (pb, pa):
                if const is not None:
                    lo = 0
                    struct.pack_into("<H", r, 4, const & 0xFFFF)
                else:
                    lo = var[0]
                    struct.pack_into("<H", r, 4, var[1])
                stats["reads"] += 1
            r[1] = hi << 4 | lo
        elif code in IF_OPS:
            if (r[1] >> 4, r[2]) == (pb, pa) or ((r[1] & 15), r[3]) == (pb, pa):
                raise ValueError("8-bit compare against story progress: %r" % op)
        elif code == SETWORD or code in WORD_ARITH:
            dst = (r[1] >> 4, r[2])
            src = (r[1] & 15, r[3])
            if src == (pb, pa) and code == SETWORD:
                # var = progress  ->  var = M (literal)  or  var = region var
                if const is not None:
                    r[1] = r[1] & 0xF0
                    struct.pack_into("<H", r, 3, const & 0xFFFF)
                else:
                    r[1] = (r[1] & 0xF0) | var[0]
                    struct.pack_into("<H", r, 3, var[1])
                stats["reads"] += 1
            if dst == (pb, pa):
                if const is not None:
                    script.remove(op)
                    stats["removed"] += 1
                else:
                    r[1] = var[0] << 4 | (r[1] & 15)
                    r[2] = var[1]
                    stats["writes"] += 1
        elif code in WORD_INCDEC:
            if (r[1] & 15 or r[1] >> 4, r[2]) == (pb, pa) or (r[1], r[2]) == (pb, pa):
                if const is not None:
                    script.remove(op)
                    stats["removed"] += 1
                else:
                    r[1], r[2] = var[0], var[1]
                    stats["writes"] += 1
    return stats


def edit_script(ctx, field):
    """Context manager-free helper: returns (Script, save_fn)."""
    script = Script.parse(ctx.field(field).sections[0])

    def save():
        ctx.field(field).sections[0] = script.build()
    return script, save

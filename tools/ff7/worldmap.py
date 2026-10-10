"""World map scripts (wm0.ev / wm2.ev / wm3.ev in world_us.lgp) and field.tbl.

.ev layout: 256 u32 function headers (high 16 bits = code offset in words,
low 16 bits = function id/type), then 16-bit code words. Stack machine:
  0x100            reset stack
  0x110 n          push constant n
  0x114 a          push bit var    (bit address, relative to savemap bank 1)
  0x118 a          push byte var   (byte offset, relative to savemap bank 1)
  0x11C a          push word var   (byte offset, relative to savemap bank 1)
  0x11B a          push special/world-map variable
  0x015 neg, 0x017 not, 0x030 mul, 0x040 add, 0x041 sub, 0x050 shl, 0x051 shr,
  0x060 <, 0x061 >, 0x062 <=, 0x063 >=, 0x070 ==, 0x071 !=, 0x080 and,
  0x0A0 or, 0x0B0 &&, 0x0C0 ||, 0x0E0 store (pop value, pop var)
  0x200 t          goto word offset t
  0x201 t          pop; goto t if false
  0x203            return
  0x300+           built-in functions (pop their arguments from the stack)
The only opcodes with an inline argument are 0x110-0x11F, 0x200 and 0x201
(validated: every jump target and function start lands on an instruction).
Word var 0x000 is the story-progress value (savemap 0x0BA4).

field.tbl: 64 entries (wm0..wm63) x 24 bytes; each entry has two destinations
(A and B) of 12 bytes: s16 x, s16 y, s16 triangle, u16 field_id, u8 dir, pad[3].
"""
import struct

HEADER_WORDS = 0x200  # 0x400 bytes
ARG_OPS = set(range(0x110, 0x120)) | {0x200, 0x201}

NAMES = {
    0x015: "neg", 0x017: "not", 0x030: "mul", 0x040: "add", 0x041: "sub",
    0x050: "shl", 0x051: "shr", 0x060: "lt", 0x061: "gt", 0x062: "le", 0x063: "ge",
    0x070: "eq", 0x071: "ne", 0x080: "and", 0x0A0: "or", 0x0B0: "land", 0x0C0: "lor",
    0x0E0: "store", 0x100: "reset", 0x110: "push", 0x114: "push_bit", 0x118: "push_byte",
    0x11B: "push_special", 0x11C: "push_word", 0x200: "goto", 0x201: "goto_if_false",
    0x203: "return", 0x318: "enter_field",
}


class Instr:
    __slots__ = ("pos", "op", "arg")

    def __init__(self, pos, op, arg=None):
        self.pos, self.op, self.arg = pos, op, arg

    def text(self):
        name = NAMES.get(self.op, "op_%03X" % self.op)
        if self.arg is None:
            return name
        if self.op in (0x200, 0x201):
            return "%s L%04X" % (name, self.arg)
        return "%s 0x%X" % (name, self.arg)


class EvScript:
    def __init__(self, data):
        self.data = bytes(data)
        self.headers = list(struct.unpack_from("<256I", data, 0))
        n = (len(data) - HEADER_WORDS * 2) // 2
        self.words = list(struct.unpack_from("<%dH" % n, data, HEADER_WORDS * 2))
        end = len(self.words)
        while end and self.words[end - 1] == 0:
            end -= 1
        self.code_end = end

    def functions(self):
        """[(index, id_word, offset)] for defined functions."""
        return [(i, h & 0xFFFF, h >> 16) for i, h in enumerate(self.headers) if h]

    def disassemble(self, start=0, end=None):
        end = self.code_end if end is None else end
        out = []
        pos = start
        w = self.words
        while pos < end:
            op = w[pos]
            if op in ARG_OPS:
                out.append(Instr(pos, op, w[pos + 1]))
                pos += 2
            else:
                out.append(Instr(pos, op))
                pos += 1
        return out

    def dump(self):
        starts = {}
        for i, fid, off in self.functions():
            starts.setdefault(off, []).append("function %d (id 0x%04X)" % (i, fid))
        code = self.disassemble()
        targets = {c.arg for c in code if c.op in (0x200, 0x201)}
        lines = []
        for c in code:
            for s in starts.get(c.pos, []):
                lines.append("")
                lines.append("## " + s)
            if c.pos in targets:
                lines.append("L%04X:" % c.pos)
            lines.append("  " + c.text())
        return "\n".join(lines) + "\n"


def field_table(data):
    out = []
    for i in range(len(data) // 24):
        dests = []
        for k in range(2):
            x, y, tri, field = struct.unpack_from("<hhhH", data, i * 24 + k * 12)
            dests.append({"x": x, "y": y, "triangle": tri, "field": field,
                          "dir": data[i * 24 + k * 12 + 8]})
        out.append(dests)
    return out

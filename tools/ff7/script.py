"""Editable model of a field script section, with an assembler that relocates jumps.

    sec = Script.parse(field.sections[0])
    code = sec.entity_script(entity, index)      # list of Op, shared with sec.ops
    sec.insert_before(op, [asm.nop()])
    field.sections[0] = sec.build()

Jumps are stored as references to target Ops, so inserting or removing code
keeps them correct. Short jumps that no longer fit are promoted to their long
forms (IFUB -> IFUBL, JMPF -> JMPFL, ...).
"""
import struct

from .field import ScriptSection
from .opcodes import OPCODES, SPECIAL, instruction_length

# short form -> long form
PROMOTE = {0x10: 0x11, 0x12: 0x13, 0x14: 0x15, 0x16: 0x17, 0x18: 0x19}
FORWARD = {0x10, 0x11, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x30, 0x31, 0x32, 0xCB, 0xCC}
BACKWARD = {0x12, 0x13}
LONG = {0x11, 0x13, 0x15, 0x17, 0x19}
JUMP_OPS = FORWARD | BACKWARD


class End:
    """Sentinel jump target: the end of the code area."""
    name = "END"


class Op:
    __slots__ = ("raw", "target", "pos")

    def __init__(self, raw, target=None):
        self.raw = bytearray(raw)
        self.target = target  # Op or End for jumps
        self.pos = None

    @property
    def op(self):
        return self.raw[0]

    @property
    def name(self):
        if self.op == 0x0F:
            return SPECIAL[self.raw[1]][0]
        return OPCODES[self.op][0]

    def __repr__(self):
        return "<Op %s %s>" % (self.name, self.raw[1:].hex(" "))


def _jump_field(op):
    """(offset of the jump operand within the instruction, width, base offset)."""
    o, L = op.op, len(op.raw)
    if o in (0x10, 0x12):
        return 1, 1, 1 if o == 0x10 else 0
    if o in (0x11, 0x13):
        return 1, 2, 1 if o == 0x11 else 0
    if o in (0x14, 0x16, 0x18):
        return L - 1, 1, L - 1
    if o in (0x15, 0x17, 0x19):
        return L - 2, 2, L - 2
    if o in (0x30, 0x31, 0x32):
        return 3, 1, 3
    if o in (0xCB, 0xCC):
        return 2, 1, 2
    raise AssertionError(o)


def _target_pos(op, pos):
    off, width, base = _jump_field(op)
    v = op.raw[off] if width == 1 else struct.unpack_from("<H", op.raw, off)[0]
    return pos - v if op.op in BACKWARD else pos + base + v


class Script:
    def __init__(self):
        self.header = b""       # bytes before entity names (32 bytes)
        self.entity_names = []  # raw 8-byte names
        self.akao_offsets = []
        self.entry = []         # [entity][32] -> Op or End
        self.ops = []
        self.tail = b""         # strings + AKAO blocks (from string_offset to end)

    @classmethod
    def parse(cls, data):
        sec = ScriptSection(data)
        if sec.broken:
            raise ValueError("script section is broken; cannot edit")
        s = cls()
        s.header = bytes(data[:32])
        s.entity_names = [bytes(data[32 + i * 8:40 + i * 8]) for i in range(sec.n_entities)]
        s.akao_offsets = [a - sec.string_offset for a in sec.akao_offsets]
        end = sec.string_offset
        by_pos = {}
        pos = sec.code_start
        while pos < end:
            length = instruction_length(data, pos)
            op = Op(data[pos:pos + length])
            op.pos = pos
            by_pos[pos] = op
            s.ops.append(op)
            pos += length
        end_marker = End()
        by_pos[end] = end_marker
        for op in s.ops:
            if op.op in JUMP_OPS:
                op.target = by_pos[_target_pos(op, op.pos)]
        s.entry = [[by_pos[p] for p in ptrs] for ptrs in sec.scripts]
        s.tail = bytes(data[sec.string_offset:])
        s._end = end_marker
        return s

    # ---- navigation -------------------------------------------------

    def index(self, op):
        for i, o in enumerate(self.ops):
            if o is op:
                return i
        raise ValueError("op not in script")

    def entity_index(self, name):
        for i, raw in enumerate(self.entity_names):
            if raw.split(b"\0")[0].decode("latin-1") == name:
                return i
        raise KeyError(name)

    def script_ops(self, entity, script):
        """Ops from a script's entry point up to (not including) the next entry point."""
        start = self.entry[entity][script]
        if start is self._end:
            return []
        starts = {id(o) for ent in self.entry for o in ent}
        i = self.index(start)
        out = [self.ops[i]]
        for o in self.ops[i + 1:]:
            if id(o) in starts:
                break
            out.append(o)
        return out

    # ---- editing ----------------------------------------------------

    def insert_before(self, anchor, new_ops, retarget=True):
        """Insert ops before `anchor`. If retarget, jumps and entry points that
        pointed at `anchor` now point at the first inserted op."""
        new_ops = list(new_ops)
        if not new_ops:
            return
        i = self.index(anchor) if anchor is not self._end else len(self.ops)
        self.ops[i:i] = new_ops
        if retarget:
            self._retarget(anchor, new_ops[0])

    def insert_after(self, anchor, new_ops):
        i = self.index(anchor)
        self.ops[i + 1:i + 1] = list(new_ops)

    def replace(self, old, new_ops):
        """Replace one op with a list of ops (jumps to it go to the first new op)."""
        new_ops = list(new_ops)
        i = self.index(old)
        follow = self.ops[i + 1] if i + 1 < len(self.ops) else self._end
        self.ops[i:i + 1] = new_ops
        self._retarget(old, new_ops[0] if new_ops else follow)

    def remove(self, op):
        self.replace(op, [])

    def _retarget(self, old, new):
        for o in self.ops:
            if o.target is old:
                o.target = new
        for ent in self.entry:
            for k, o in enumerate(ent):
                if o is old:
                    ent[k] = new

    # ---- music ------------------------------------------------------

    def akao_block(self, index):
        """Raw bytes of music block `index` (offsets are relative to `tail`)."""
        start = self.akao_offsets[index]
        later = [o for o in self.akao_offsets if o > start]
        return self.tail[start:min(later) if later else len(self.tail)]

    def akao_ids(self):
        return [struct.unpack_from("<H", self.tail, o + 4)[0] for o in self.akao_offsets]

    def add_akao(self, block):
        """Append a music block; returns its index for the MUSIC opcode."""
        self.akao_offsets.append(len(self.tail))
        self.tail += bytes(block)
        return len(self.akao_offsets) - 1

    # ---- assembly ---------------------------------------------------

    def build(self):
        n_ent = len(self.entity_names)
        code_start = 32 + 8 * n_ent + 4 * len(self.akao_offsets) + 64 * n_ent
        for _ in range(16):
            pos = code_start
            for o in self.ops:
                o.pos = pos
                pos += len(o.raw)
            self._end.pos = pos
            if not self._encode_jumps():
                break
        else:
            raise RuntimeError("jump layout did not converge")
        string_offset = self._end.pos
        out = bytearray(self.header)
        struct.pack_into("<B", out, 2, n_ent)
        struct.pack_into("<H", out, 4, string_offset)
        struct.pack_into("<H", out, 6, len(self.akao_offsets))
        for raw in self.entity_names:
            out += raw
        for a in self.akao_offsets:
            out += struct.pack("<I", a + string_offset)
        for ent in self.entry:
            out += struct.pack("<32H", *[o.pos for o in ent])
        assert len(out) == code_start
        for o in self.ops:
            out += o.raw
        out += self.tail
        return bytes(out)

    def _encode_jumps(self):
        """Write jump operands. Returns True if any op grew (layout must be redone)."""
        grew = False
        for o in self.ops:
            if o.target is None:
                continue
            off, width, base = _jump_field(o)
            if o.op in BACKWARD:
                v = o.pos - o.target.pos
            else:
                v = o.target.pos - (o.pos + base)
            if v < 0:
                raise ValueError("%r: jump direction is wrong for its target" % o)
            if width == 1 and v > 0xFF:
                if o.op not in PROMOTE:
                    raise ValueError("%r: short jump out of range and has no long form" % o)
                self._promote(o)
                grew = True
                continue
            if width == 2 and v > 0xFFFF:
                raise ValueError("%r: jump out of range" % o)
            if width == 1:
                o.raw[off] = v
            else:
                struct.pack_into("<H", o.raw, off, v)
        return grew

    @staticmethod
    def _promote(o):
        o.raw[0] = PROMOTE[o.raw[0]]
        o.raw.append(0)  # jump operand widens from 1 to 2 bytes (it is the last operand)

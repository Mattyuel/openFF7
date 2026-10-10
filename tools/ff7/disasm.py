"""Disassemble FF7 field scripts into structured instructions and readable text."""
import struct
from .opcodes import OPCODES, SPECIAL, instruction_length

# Variable banks as encoded in opcode bank nibbles (1-15). Bank 0 = literal.
# (2, 0) is the main story progress variable ("Game Moment"), 16-bit.
PROGRESS_VAR = (2, 0)
SIXTEEN_BIT_BANKS = {2, 4, 6, 12, 14, 15}
COMPARE_OPS = ["==", "!=", ">", "<", ">=", "<=", "&", "^", "|", "bit_on", "bit_off"]


def var(bank, value):
    return str(value) if bank == 0 else "var[%d][%d]" % (bank, value)


class Instruction:
    __slots__ = ("pos", "op", "name", "raw", "args", "target")

    def __init__(self, pos, op, name, raw):
        self.pos, self.op, self.name, self.raw = pos, op, name, raw
        self.args = {}
        self.target = None

    def __repr__(self):
        return "<%04X %s %s>" % (self.pos, self.name, self.args)


def _decode_operands(ins):
    r, op = ins.raw, ins.op
    a = ins.args
    if op in (0x14, 0x15):  # IFUB/IFUBL: banks, a, b, cmp, jump
        a.update(bank_a=r[1] >> 4, bank_b=r[1] & 15, a=r[2], b=r[3], cmp=r[4])
        ins.target = ins.pos + len(r) - 1 + r[5] if op == 0x14 else \
            ins.pos + len(r) - 2 + struct.unpack_from("<H", r, 5)[0]
    elif op in (0x16, 0x17, 0x18, 0x19):  # IFSW/IFUW: banks, a u16, b u16, cmp, jump
        signed = op in (0x16, 0x17)
        fmt = "<h" if signed else "<H"
        a.update(bank_a=r[1] >> 4, bank_b=r[1] & 15,
                 a=struct.unpack_from("<H", r, 2)[0], b=struct.unpack_from(fmt, r, 4)[0], cmp=r[6])
        ins.target = ins.pos + len(r) - 1 + r[7] if op in (0x16, 0x18) else \
            ins.pos + len(r) - 2 + struct.unpack_from("<H", r, 7)[0]
    elif op == 0x10:
        ins.target = ins.pos + 1 + r[1]
    elif op == 0x11:
        ins.target = ins.pos + 1 + struct.unpack_from("<H", r, 1)[0]
    elif op == 0x12:
        ins.target = ins.pos - r[1]
    elif op == 0x13:
        ins.target = ins.pos - struct.unpack_from("<H", r, 1)[0]
    elif op in (0x30, 0x31, 0x32):  # IFKEY*: u16 keys, jump
        a.update(keys=struct.unpack_from("<H", r, 1)[0])
        ins.target = ins.pos + 3 + r[3]
    elif op in (0xCB, 0xCC):  # IFPRTYQ / IFMEMBQ: char, jump
        a.update(char=r[1])
        ins.target = ins.pos + 2 + r[2]
    elif op == 0x60:  # MAPJUMP: field u16, x s16, y s16, triangle u16, dir u8
        f, x, y, t = struct.unpack_from("<HhhH", r, 1)
        a.update(field=f, x=x, y=y, triangle=t, dir=r[9])
    elif op == 0x70:  # BATTLE: banks, formation u16
        a.update(bank=r[1] & 15, formation=struct.unpack_from("<H", r, 2)[0])
    elif op == 0x71:
        a.update(off=r[1])
    elif op == 0x4B:  # BTLTB: encounter table
        a.update(table=r[1])
    elif op in (0x80, 0x82, 0x83, 0x84):  # SETBYTE/BITON/BITOFF/BITXOR: banks, dst, val
        a.update(bank_d=r[1] >> 4, bank_s=r[1] & 15, dst=r[2], val=r[3])
    elif op == 0x81:  # SETWORD
        a.update(bank_d=r[1] >> 4, bank_s=r[1] & 15, dst=r[2],
                 val=struct.unpack_from("<H", r, 3)[0])
    elif op in (0x76, 0x78, 0x85, 0x87):
        a.update(bank_d=r[1] >> 4, bank_s=r[1] & 15, dst=r[2], val=r[3])
    elif op in (0x77, 0x79, 0x86, 0x88):
        a.update(bank_d=r[1] >> 4, bank_s=r[1] & 15, dst=r[2],
                 val=struct.unpack_from("<H", r, 3)[0])
    elif op in (0x58, 0x59, 0x5A):  # STITM/DLITM/CKITM: banks, item u16, qty u8
        a.update(item=struct.unpack_from("<H", r, 2)[0], qty=r[4])
    elif op == 0x5B:  # SMTRA: banks(2), materia u8, ap u24
        a.update(materia=r[3], ap=r[4] | r[5] << 8 | r[6] << 16)
    elif op == 0x40:  # MESSAGE: window, text id
        a.update(window=r[1], text=r[2])
    elif op == 0x48:  # ASK: bank, window, text, first, last, var
        a.update(window=r[2], text=r[3], first=r[4], last=r[5], var=r[6])
    elif op == 0xCA:  # PRTYE: 3 characters
        a.update(chars=list(r[1:4]))
    elif op in (0xC8, 0xC9):  # PRTYP/PRTYM
        a.update(char=r[1])
    elif op == 0xA1:  # CHAR: model id
        a.update(model=r[1])
    elif op == 0xA0:  # PC: character
        a.update(char=r[1])
    elif op == 0x20:  # MINIGAME
        f, x, y, z = struct.unpack_from("<HhhH", r, 1)
        a.update(field=f, x=x, y=y, z=z, param=r[9], game=r[10])
    elif op == 0x43:  # MPNAM: location name text id
        a.update(text=r[1])
    elif op == 0xD2:  # MPJPO: disable/enable gateways
        a.update(off=r[1])
    elif op == 0x0F:
        a.update(sub=SPECIAL[r[1]][0])


def disassemble(code, start, end):
    out = []
    pos = start
    while pos < end:
        length = instruction_length(code, pos)
        op = code[pos]
        name = OPCODES[op][0]
        if op == 0x0F:
            name = SPECIAL[code[pos + 1]][0]
        ins = Instruction(pos, op, name, bytes(code[pos:pos + length]))
        _decode_operands(ins)
        out.append(ins)
        pos += length
    return out


def format_instruction(ins, label_of=None):
    a = ins.args
    tgt = ""
    if ins.target is not None:
        tgt = " goto %s" % (label_of(ins.target) if label_of else "0x%04X" % ins.target)
    if ins.op in (0x14, 0x15, 0x16, 0x17, 0x18, 0x19):
        cmp = COMPARE_OPS[a["cmp"]] if a["cmp"] < len(COMPARE_OPS) else "cmp%d" % a["cmp"]
        return "if not (%s %s %s)%s" % (var(a["bank_a"], a["a"]), cmp, var(a["bank_b"], a["b"]), tgt)
    if ins.op in (0x10, 0x11, 0x12, 0x13):
        return "goto%s" % tgt[5:]
    if ins.op in (0x80, 0x81):
        return "%s = %s" % (var(a["bank_d"], a["dst"]), var(a["bank_s"], a["val"]))
    if a:
        args = " ".join("%s=%s" % kv for kv in a.items())
        return "%s %s%s" % (ins.name, args, tgt)
    if len(ins.raw) > 1:
        return "%s %s%s" % (ins.name, ins.raw[1:].hex(" "), tgt)
    return ins.name + tgt

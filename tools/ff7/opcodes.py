"""FF7 field script opcode table: opcode -> (mnemonic, total length in bytes).

Length None means variable (handled in the disassembler):
  0x0F SPECIAL - length depends on sub-opcode
  0x28 KAWAI   - length byte follows the opcode
"""

OPCODES = {
    0x00: ("RET", 1), 0x01: ("REQ", 3), 0x02: ("REQSW", 3), 0x03: ("REQEW", 3),
    0x04: ("PREQ", 3), 0x05: ("PRQSW", 3), 0x06: ("PRQEW", 3), 0x07: ("RETTO", 2),
    0x08: ("JOIN", 2), 0x09: ("SPLIT", 15), 0x0A: ("SPTYE", 6), 0x0B: ("GTPYE", 6),
    0x0E: ("DSKCG", 2), 0x0F: ("SPECIAL", None),
    0x1C: ("BOUNTY", 5),   # openFF7: unused in the game; 630_bounties.py points it at quest_menu.asm
    0x1D: ("TXPOKE", 5),   # openFF7: unused in the game; 620_honey_bee.py points it at quest_menu.asm
    0x10: ("JMPF", 2), 0x11: ("JMPFL", 3), 0x12: ("JMPB", 2), 0x13: ("JMPBL", 3),
    0x14: ("IFUB", 6), 0x15: ("IFUBL", 7), 0x16: ("IFSW", 8), 0x17: ("IFSWL", 9),
    0x18: ("IFUW", 8), 0x19: ("IFUWL", 9),
    0x20: ("MINIGAME", 11), 0x21: ("TUTOR", 2), 0x22: ("BTMD2", 5), 0x23: ("BTRLD", 3),
    0x24: ("WAIT", 3), 0x25: ("NFADE", 9), 0x26: ("BLINK", 2), 0x27: ("BGMOVIE", 2),
    0x28: ("KAWAI", None), 0x29: ("KAWIW", 1), 0x2A: ("PMOVA", 2), 0x2B: ("SLIP", 2),
    0x2C: ("BGPDH", 5), 0x2D: ("BGSCR", 7), 0x2E: ("WCLS", 2), 0x2F: ("WSIZW", 10),
    0x30: ("IFKEY", 4), 0x31: ("IFKEYON", 4), 0x32: ("IFKEYOFF", 4), 0x33: ("UC", 2),
    0x34: ("PDIRA", 2), 0x35: ("PTURA", 4), 0x36: ("WSPCL", 5), 0x37: ("WNUMB", 8),
    0x38: ("STTIM", 6), 0x39: ("GOLDU", 6), 0x3A: ("GOLDD", 6), 0x3B: ("CHGLD", 4),
    0x3C: ("HMPMAX1", 1), 0x3D: ("HMPMAX2", 1), 0x3E: ("MHMMX", 1), 0x3F: ("HMPMAX3", 1),
    0x40: ("MESSAGE", 3), 0x41: ("MPARA", 5), 0x42: ("MPRA2", 6), 0x43: ("MPNAM", 2),
    0x45: ("MPU", 5), 0x47: ("MPD", 5), 0x48: ("ASK", 7), 0x49: ("MENU", 4),
    0x4A: ("MENU2", 2), 0x4B: ("BTLTB", 2), 0x4D: ("HPU", 5), 0x4F: ("HPD", 5),
    0x50: ("WINDOW", 10), 0x51: ("WMOVE", 6), 0x52: ("WMODE", 4), 0x53: ("WREST", 2),
    0x54: ("WCLSE", 2), 0x55: ("WROW", 3), 0x56: ("GWCOL", 7), 0x57: ("SWCOL", 7),
    0x58: ("STITM", 5), 0x59: ("DLITM", 5), 0x5A: ("CKITM", 5), 0x5B: ("SMTRA", 7),
    0x5C: ("DMTRA", 8), 0x5D: ("CMTRA", 10), 0x5E: ("SHAKE", 8), 0x5F: ("NOP", 1),
    0x60: ("MAPJUMP", 10), 0x61: ("SCRLO", 2), 0x62: ("SCRLC", 5), 0x63: ("SCRLA", 6),
    0x64: ("SCR2D", 6), 0x65: ("SCRCC", 1), 0x66: ("SCR2DC", 9), 0x67: ("SCRLW", 1),
    0x68: ("SCR2DL", 9), 0x69: ("MPDSP", 2), 0x6A: ("VWOFT", 7), 0x6B: ("FADE", 9),
    0x6C: ("FADEW", 1), 0x6D: ("IDLCK", 4), 0x6E: ("LSTMP", 3), 0x6F: ("SCRLP", 6),
    0x70: ("BATTLE", 4), 0x71: ("BTLON", 2), 0x72: ("BTLMD", 3), 0x73: ("PGTDR", 4),
    0x74: ("GETPC", 4), 0x75: ("PXYZI", 8), 0x76: ("PLUS!", 4), 0x77: ("PLUS2!", 5),
    0x78: ("MINUS!", 4), 0x79: ("MINUS2!", 5), 0x7A: ("INC!", 3), 0x7B: ("INC2!", 3),
    0x7C: ("DEC!", 3), 0x7D: ("DEC2!", 3), 0x7E: ("TLKON", 2), 0x7F: ("RDMSD", 3),
    0x80: ("SETBYTE", 4), 0x81: ("SETWORD", 5), 0x82: ("BITON", 4), 0x83: ("BITOFF", 4),
    0x84: ("BITXOR", 4), 0x85: ("PLUS", 4), 0x86: ("PLUS2", 5), 0x87: ("MINUS", 4),
    0x88: ("MINUS2", 5), 0x89: ("MUL", 4), 0x8A: ("MUL2", 5), 0x8B: ("DIV", 4),
    0x8C: ("DIV2", 5), 0x8D: ("MOD", 4), 0x8E: ("MOD2", 5), 0x8F: ("AND", 4),
    0x90: ("AND2", 5), 0x91: ("OR", 4), 0x92: ("OR2", 5), 0x93: ("XOR", 4),
    0x94: ("XOR2", 5), 0x95: ("INC", 3), 0x96: ("INC2", 3), 0x97: ("DEC", 3),
    0x98: ("DEC2", 3), 0x99: ("RANDOM", 3), 0x9A: ("LBYTE", 4), 0x9B: ("HBYTE", 5),
    0x9C: ("2BYTE", 6), 0x9D: ("SETX", 7), 0x9E: ("GETX", 7), 0x9F: ("SEARCHX", 11),
    0xA0: ("PC", 2), 0xA1: ("CHAR", 2), 0xA2: ("DFANM", 3), 0xA3: ("ANIME1", 3),
    0xA4: ("VISI", 2), 0xA5: ("XYZI", 11), 0xA6: ("XYI", 9), 0xA7: ("XYZ", 9),
    0xA8: ("MOVE", 6), 0xA9: ("CMOVE", 6), 0xAA: ("MOVA", 2), 0xAB: ("TURA", 4),
    0xAC: ("ANIMW", 1), 0xAD: ("FMOVE", 6), 0xAE: ("ANIME2", 3), 0xAF: ("ANIM!1", 3),
    0xB0: ("CANIM1", 5), 0xB1: ("CANM!1", 5), 0xB2: ("MSPED", 4), 0xB3: ("DIR", 3),
    0xB4: ("TURNGEN", 6), 0xB5: ("TURN", 6), 0xB6: ("DIRA", 2), 0xB7: ("GETDIR", 4),
    0xB8: ("GETAXY", 5), 0xB9: ("GETAI", 4), 0xBA: ("ANIM!2", 3), 0xBB: ("CANIM2", 5),
    0xBC: ("CANM!2", 5), 0xBD: ("ASPED", 4), 0xBF: ("CC", 2),
    0xC0: ("JUMP", 11), 0xC1: ("AXYZI", 8), 0xC2: ("LADER", 15), 0xC3: ("OFST", 12),
    0xC4: ("OFSTW", 1), 0xC5: ("TALKR", 3), 0xC6: ("SLIDR", 3), 0xC7: ("SOLID", 2),
    0xC8: ("PRTYP", 2), 0xC9: ("PRTYM", 2), 0xCA: ("PRTYE", 4), 0xCB: ("IFPRTYQ", 3),
    0xCC: ("IFMEMBQ", 3), 0xCD: ("MMBUD", 3), 0xCE: ("MMBLK", 2), 0xCF: ("MMBUK", 2),
    0xD0: ("LINE", 13), 0xD1: ("LINON", 2), 0xD2: ("MPJPO", 2), 0xD3: ("SLINE", 16),
    0xD4: ("SIN", 10), 0xD5: ("COS", 10), 0xD6: ("TLKR2", 4), 0xD7: ("SLDR2", 4),
    0xD8: ("PMJMP", 3), 0xD9: ("PMJMP2", 1), 0xDA: ("AKAO2", 15), 0xDB: ("FCFIX", 2),
    0xDC: ("CCANM", 4), 0xDD: ("ANIMB", 1), 0xDE: ("TURNW", 1), 0xDF: ("MPPAL", 11),
    0xE0: ("BGON", 4), 0xE1: ("BGOFF", 4), 0xE2: ("BGROL", 3), 0xE3: ("BGROL2", 3),
    0xE4: ("BGCLR", 3), 0xE5: ("STPAL", 5), 0xE6: ("LDPAL", 5), 0xE7: ("CPPAL", 5),
    0xE8: ("RTPAL", 7), 0xE9: ("ADPAL", 10), 0xEA: ("MPPAL2", 10), 0xEB: ("STPLS", 5),
    0xEC: ("LDPLS", 5), 0xED: ("CPPAL2", 8), 0xEE: ("RTPAL2", 8), 0xEF: ("ADPAL2", 11),
    0xF0: ("MUSIC", 2), 0xF1: ("SOUND", 5), 0xF2: ("AKAO", 14), 0xF3: ("MUSVT", 2),
    0xF4: ("MUSVM", 2), 0xF5: ("MULCK", 2), 0xF6: ("BMUSC", 2), 0xF7: ("CHMPH", 4),
    0xF8: ("PMVIE", 2), 0xF9: ("MOVIE", 1), 0xFA: ("MVIEF", 3), 0xFB: ("MVCAM", 2),
    0xFC: ("FMUSC", 2), 0xFD: ("CMUSC", 6), 0xFE: ("CHMST", 3), 0xFF: ("GAMEOVER", 1),
}

# SPECIAL (0x0F) sub-opcodes -> (mnemonic, total length including 0x0F and sub-opcode)
SPECIAL = {
    0xF5: ("ARROW", 3), 0xF6: ("PNAME", 3), 0xF7: ("GMSPD", 3), 0xF8: ("SMSPD", 4),
    0xF9: ("FLMAT", 2), 0xFA: ("FLITM", 2), 0xFB: ("BTLCK", 3), 0xFC: ("MVLCK", 3),
    0xFD: ("SPCNM", 4), 0xFE: ("RSGLB", 2), 0xFF: ("CLITM", 2),
}

# Opcodes whose operand is a jump, with (offset_position, width, direction, base)
# The jump is relative to the position of the jump operand's first byte
# (IFxx) or the opcode itself + 1 (JMPx), per the engine.
CONDITIONAL = {0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x30, 0x31, 0x32, 0xCB, 0xCC}
JUMPS = {0x10, 0x11, 0x12, 0x13}


def instruction_length(code, pos):
    op = code[pos]
    if op not in OPCODES:
        raise ValueError("unknown opcode 0x%02X at 0x%X" % (op, pos))
    name, length = OPCODES[op]
    if length is not None:
        return length
    if op == 0x0F:
        sub = code[pos + 1]
        if sub not in SPECIAL:
            raise ValueError("unknown SPECIAL sub-opcode 0x%02X at 0x%X" % (sub, pos))
        return SPECIAL[sub][1]
    if op == 0x28:
        return code[pos + 1]
    raise AssertionError(name)

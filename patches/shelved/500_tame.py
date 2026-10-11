"""Tame (milestone 1: plumbing). See docs/research_battle.md.

- Command 0x1C "Tame" (unused id): command record copied from Manipulate
  (0x0B: target one enemy directly); its routine sequence is Manipulate's
  [0x1A, 0x09] for now (milestone 2 replaces the roll with the Tame logic).
  The exe's per-command routine-sequence table (0x7B75A8, 0x6D bytes,
  segments separated by 0x1F) is relocated into the .openff7 section with the
  new segment; its two readers and the builder's length bound are repointed.
- Materia 38 (unused command-materia slot, type 0x16) becomes "Tame",
  granting command 0x1C. Names/descriptions in kernel2.bin.
- The materia lies on the Sector 6 playground (mds6_2), next to where you
  arrive from Sector 7.
"""
import struct

from _config import FLAG_TAME_MATERIA, FLAGS
from _recruit import hide, say
from _travel import add_npc, beside, copy_model

from ff7 import asm
from ff7.kernel2 import CMD_DESC, CMD_NAMES, MATERIA_DESC, MATERIA_NAMES
from ff7.script import Op
from ff7.text import encode

TAME_CMD = 0x1C
MANIPULATE_CMD = 0x0B
TAME_MATERIA = 38
SEQ_TABLE, SEQ_LEN = 0x7B75A8, 0x6D
SEQ_READERS = [0x43656A, 0x436B6A]       # mov cl/al, [reg + SEQ_TABLE]: disp32 at +2
SEQ_BOUND = 0x436B41                     # cmp dword [ebp-4], 0x6D (imm8 at +3)
# Per-command action info, 4 bytes per command (0x26 entries), copied into the
# action context at 0x435FF5..0x436029: byte -> +0x1C (action animation),
# byte -> +0x20, u16 -> +0x40 (damage formula; Manipulate 0x90 = type 9, its
# roll). Command 0x1C's entry is all zero: Tame hung after its camera.
CMD_INFO = 0x7B7510
ORB_MODEL = ("nmkin_5", 3)               # fieldbg_mtra3: the materia orb
ARRIVE_S6 = (-1312, 1270, 241)           # where you enter mds6_2 from Sector 7


def _kernel(ctx):
    cmds = ctx.kernel_section(0)
    cmds[TAME_CMD * 8:TAME_CMD * 8 + 8] = cmds[MANIPULATE_CMD * 8:MANIPULATE_CMD * 8 + 8]
    mat = ctx.kernel_section(8)
    rec = TAME_MATERIA * 20
    assert mat[rec + 0xD] == 0x16, "materia %d is not a command materia slot" % TAME_MATERIA
    mat[rec + 0xE:rec + 0x14] = bytes([TAME_CMD, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    k2 = ctx.kernel2()
    k2.set(CMD_NAMES, TAME_CMD, encode("Tame"))
    k2.set(CMD_DESC, TAME_CMD, encode("Tame a weakened enemy"))
    k2.set(MATERIA_NAMES, TAME_MATERIA, encode("Tame"))
    k2.set(MATERIA_DESC, TAME_MATERIA, encode("Tame weakened enemies and call them to fight"))


def _sequences(ctx):
    exe = ctx.exe()
    table = exe.read(SEQ_TABLE, SEQ_LEN)
    segs = table.split(b"\x1f")[:-1]
    assert len(segs) == 0x26 and segs[TAME_CMD] == b"", "unexpected sequence table"
    segs[TAME_CMD] = segs[MANIPULATE_CMD]
    new = b"".join(s + b"\x1f" for s in segs)
    assert len(new) < 0x80
    va = exe.alloc(new, "seq_table")
    for reader in SEQ_READERS:
        exe.patch_u32(reader + 2, SEQ_TABLE, va, "command sequence table reader")
    exe.patch(SEQ_BOUND + 3, bytes([SEQ_LEN]), bytes([len(new)]), "sequence table length")
    manip = exe.read(CMD_INFO + 4 * MANIPULATE_CMD, 4)
    exe.patch(CMD_INFO + 4 * TAME_CMD, b"\0\0\0\0", manip, "command 0x1C action info = Manipulate's")


def _orb(ctx):
    field = "mds6_2"
    model = copy_model(ctx, field, *ORB_MODEL)
    pos = beside(ctx, field, *ARRIVE_S6)
    gone = asm.nop()
    init = [asm.if_byte(FLAGS, "bit_on", FLAG_TAME_MATERIA, gone)] + hide() + [gone]   # hidden once taken

    def talk(sec):
        return ([Op(b"\x33\x01"),                                        # UC 01
                 Op(bytes([0x5B, 0, 0, TAME_MATERIA, 0, 0, 0])),          # SMTRA
                 asm.biton(FLAGS, FLAG_TAME_MATERIA),
                 Op(b"\xF1\x00\x68\x01\x40")]                             # SOUND (pickup)
                + say(sec, "Received “Tame” Materia!")
                + hide() + [Op(b"\x33\x00"), asm.ret()])
    add_npc(ctx, field, "tame", model, pos, 0, talk, init)


def apply(ctx):
    _kernel(ctx)
    _sequences(ctx)
    _orb(ctx)

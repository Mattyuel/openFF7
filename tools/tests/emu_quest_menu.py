"""Optional: run the built quest code (patches/asm/quest_menu.asm) in an x86
emulator with the game's functions stubbed: kill hook counting, menu list,
scrolling, multi-target progress, cancel. Needs `pip install unicorn` and a
build (build/openFF7/ff7_en.exe). Run: python3 tools/tests/emu_quest_menu.py
Assumes the quest save offsets of patches/600_quests.py (Q / CTR)."""
import os
import struct
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
try:
    from unicorn import *
except ImportError:
    print('unicorn not installed: skipped')
    sys.exit(0)
from unicorn.x86_const import *
from ff7 import exepatch
from ff7.text import decode

EXE = open(os.path.join(ROOT, 'build', 'openFF7', 'ff7_en.exe'), 'rb').read()
def rd(va, n): o = exepatch.va_to_file(EXE, va); return EXE[o:o + n]
DATA, CODE = 0xFD5000, 0xFDD000
BANK3, INV = 0xDC0ADC, 0xDC0234
STUBS = {0x6C98A6: 'MENU_DRAW', 0x6C9D07: 'MENU_DRAW_LR', 0x6C9808: 'MENU_STATE', 0x6C9812: 'MENU_GO',
         0x6C6AEE: 'MENU_SET', 0x6F5B03: 'TEXT', 0x6E7BA1: 'WIN_RECT', 0x6E7D20: 'WIN_DRAW',
         0x6EB3B8: 'HAND', 0x6F53B2: 'KEY_REPEAT', 0x41AB74: 'KEY_NEW', 0x74580A: 'SOUND'}
STOP = 0x43153C

class Emu:
    def __init__(self):
        u = self.u = Uc(UC_ARCH_X86, UC_MODE_32)
        u.mem_map(0x400000, 0x400000)      # code stubs
        u.mem_map(0x900000, 0x100000)      # 0x9A....
        u.mem_map(0xDB0000, 0x40000)       # savemap
        u.mem_map(0xFD5000, 0xA000)        # .openff7
        u.mem_map(0x100000, 0x10000)       # stack
        sec = rd(0xFD5000, 0x9000)
        u.mem_write(0xFD5000, sec)
        for a in STUBS: u.mem_write(a, b'\xc3')
        u.mem_write(STOP, b'\xf4')         # hlt
        u.mem_write(INV, b'\xff' * 640)
        self.calls = []; self.keys = {}; self.state = 0
        u.hook_add(UC_HOOK_CODE, self._hook, begin=0x400000, end=0x800000)
    def _hook(self, u, addr, size, _):
        if addr in STUBS:
            esp = u.reg_read(UC_X86_REG_ESP)
            args = struct.unpack('<6I', u.mem_read(esp + 4, 24))
            name = STUBS[addr]; ret = 0
            if name == 'MENU_STATE': ret = self.state
            if name == 'KEY_REPEAT': ret = 1 if self.keys.get(args[0]) else 0
            if name == 'KEY_NEW': ret = 1 if self.keys.get(args[0]) else 0
            if name == 'TEXT':
                s = bytes(u.mem_read(args[2], 80)); args = (args[0], args[1], decode(s), args[3])
            self.calls.append((name, args))
            # clobber caller-saved regs like real code may
            u.reg_write(UC_X86_REG_EAX, ret); u.reg_write(UC_X86_REG_ECX, 0xdead); u.reg_write(UC_X86_REG_EDX, 0xbeef)
    def b3(self, off, v=None):
        if v is None: return self.u.mem_read(BANK3 + off, 1)[0]
        self.u.mem_write(BANK3 + off, bytes([v]))
    def inv(self, slot, item, qty):
        self.u.mem_write(INV + 2 * slot, struct.pack('<H', item | qty << 9))
    def call(self, entry, arg=0):
        u = self.u; self.calls = []
        esp = 0x10F000
        # return address = a hlt
        u.mem_write(0x7FFFF0, b'\xf4')
        u.mem_write(esp, struct.pack('<II', 0x7FFFF0, arg))
        for r, v in ((UC_X86_REG_EBX, 0x11), (UC_X86_REG_ESI, 0x22), (UC_X86_REG_EDI, 0x33), (UC_X86_REG_EBP, 0x10F800)):
            u.reg_write(r, v)
        u.reg_write(UC_X86_REG_ESP, esp)
        u.emu_start(entry, 0x7FFFF0)
        assert u.reg_read(UC_X86_REG_ESP) == esp + 4
        assert (u.reg_read(UC_X86_REG_EBX), u.reg_read(UC_X86_REG_ESI), u.reg_read(UC_X86_REG_EDI)) == (0x11, 0x22, 0x33), 'callee-saved clobbered'
    def kill(self, enemy_type, slot=2):
        u = self.u; ebp = 0x10F800
        u.mem_write(ebp - 0x20, struct.pack('<i', enemy_type)); u.mem_write(ebp - 4, struct.pack('<i', slot))
        regs = {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_ECX: 4, UC_X86_REG_EDX: 5}
        for r, v in regs.items(): u.reg_write(r, v)
        u.reg_write(UC_X86_REG_EBP, ebp); u.reg_write(UC_X86_REG_ESP, 0x10F000)
        u.emu_start(0x431536, STOP)
        assert all(u.reg_read(r) == v for r, v in regs.items()), 'kill hook clobbered regs'
        assert u.reg_read(UC_X86_REG_EAX) == slot + 4 and u.reg_read(UC_X86_REG_ESP) == 0x10F000

e = Emu()
# the patched 0x431536 jump
e.u.mem_write(0x431536, rd(0x431536, 6))
def setids(*ids): e.u.mem_write(0x9A8748, struct.pack('<3H', *ids))
# kill: andrea (state 203, ctr 204..207 Ceasar 39, Blugu 27, Blood 31, Chuse 26); manager_n5 (194/195) has Blood Taste 31
setids(39, 31, 99)
e.kill(0); assert e.b3(204) == 0, 'counted before accepting'
e.b3(203, 2); e.b3(194, 2)
e.kill(0); e.kill(0); e.kill(0)
assert e.b3(204) == 2, e.b3(204)          # capped at 2
e.kill(1)
assert e.b3(206) == 1 and e.b3(195) == 1, (e.b3(206), e.b3(195))   # both quests count Blood Taste
e.kill(2)                                 # enemy 99: nothing
print('kill hook ok')

# menu: accept 10 quests to test scrolling
for off in (192, 196, 198, 199, 200, 201, 202, 208, 211, 216):
    e.b3(off, 2)
e.call(CODE + 0)
e.inv(0, 3, 1); e.inv(5, 3, 1)            # 2 Ethers in two slots (Madam M ready)
e.inv(7, 0, 2)                            # 2 Potions (Gwen needs 3)
e.call(CODE + 5, 0)
texts = [a for n, a in e.calls if n == 'TEXT']
for t in texts: print('  ', t)

def frame(keys=()):
    e.keys = {k: 1 for k in keys}
    e.call(CODE + 5, 0)
    e.keys = {}
    return [a for n, a in e.calls if n == 'TEXT'], [a for n, a in e.calls if n == 'HAND']
# go down to the 10th quest (wymer), then to andrea-less list... check scroll
for i in range(9): t, h = frame([0x4000])
t, h = frame()
print('after 9 downs: hand', h, 'rows', [x[2] for x in t if x[0] == 64])
print('   details', [x[2] for x in t if x[0] in (24, 324)][-4:])
t, h = frame([0x4000])   # wrap to top
t, h = frame()
print('wrap: hand', h, 'first row', [x[2] for x in t if x[0] == 64][:1])
t, h = frame([0x1000])   # up wraps to bottom
t, h = frame()
print('up-wrap: hand', h, [x[2] for x in t if x[0] == 64][-1:])
# multi-target: accept andrea + billybob only
for off in range(192, 230): e.b3(off, 0)
e.b3(203, 2); e.b3(204, 2); e.b3(205, 1); e.b3(206, 0); e.b3(207, 2)
e.b3(208, 2); e.b3(209, 5); e.b3(210, 4)
e.call(CODE + 0)
t, h = frame()
print([x for x in t])
t, h = frame([0x4000]); t, h = frame()
print([x for x in t if x[1] > 380])
# cancel
e.keys = {0x40: 1}; e.call(CODE + 5, 0)
print([c for c in e.calls if c[0] in ('SOUND', 'MENU_GO', 'MENU_SET')])
# no quests
for off in range(192, 230): e.b3(off, 0)
e.call(CODE + 0); t, h = frame(); print(t, h)
# handed-in quests stay listed after the accepted ones, green, with full counts
for off in range(192, 230): e.b3(off, 0)
e.b3(208, 2); e.b3(209, 0); e.b3(210, 0)  # billybob accepted, nothing done
e.b3(203, 4); e.b3(204, 0)                # andrea handed in (counters irrelevant)
e.call(CODE + 0); t, h = frame()
rows = [x for x in t if x[0] == 64]
print('done listed last:', rows)
assert [r[3] for r in rows] == [7, 4], rows
t, h = frame([0x4000]); t, h = frame()
parts = [x[2] for x in t if x[1] > 380]
print('  done details', parts)
assert 'Ceasar: 2/2' in parts and not any('Report back' in p for p in parts), parts

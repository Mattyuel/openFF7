"""PHS usable from the start: the save points in early Midgar (and a few story
scenes) write the menu locking mask with the PHS bit set, since the PHS is
only handed over at Kalm. Clear that bit wherever a field script writes the
mask as a constant."""
from _config import MENU_LOCK, PHS_LOCK_BIT

from ff7.script import Script


def _unlocks_phs(op):
    bank, addr = MENU_LOCK
    if op.op != 0x81 or op.raw[1] != bank << 4 or op.raw[2] != addr:   # SETWORD var = const
        return False
    value = op.raw[3] | op.raw[4] << 8
    if not value & PHS_LOCK_BIT:
        return False
    value &= ~PHS_LOCK_BIT
    op.raw[3], op.raw[4] = value & 0xFF, value >> 8
    return True


def apply(ctx):
    for name in ctx.maplist:
        if name not in ctx.flevel:
            continue
        try:
            sec = Script.parse(ctx.field(name).sections[0])
        except ValueError:   # a few unused fields have scripts the parser rejects
            continue
        if [o for o in sec.ops if _unlocks_phs(o)]:
            ctx.field(name).sections[0] = sec.build()

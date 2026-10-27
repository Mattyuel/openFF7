"""PHS usable from the start: the save points in early Midgar (and a few story
scenes) write the menu locking mask with the PHS bit set, since the PHS is
only handed over at Kalm. Clear that bit wherever a field script writes the
mask as a constant. Also stop story scenes from adding PHS to the menu
(it appears once 3 characters are recruited, see _recruit.count_recruit)."""
from _config import MENU_LOCK, MENU_PHS, PHS_LOCK_BIT

from ff7.script import Script

# Story scenes that add PHS to the menu (Kalm inn after the flashback, the
# cargo ship). Only these are neutralised; openFF7's own recruit code adds it.
STORY_PHS_SHOW = ["elminn_1", "shpin_3"]


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


def _hides_phs_show(op):
    """Story scenes (Kalm inn, cargo ship) add PHS to the menu (OR2 var[2][28]);
    openFF7 shows it at 3 recruits instead, so drop that bit."""
    if op.op != 0x92 or op.raw[1] != 0x20 or op.raw[2] != 28:
        return False
    value = op.raw[3] | op.raw[4] << 8
    if not value & MENU_PHS:
        return False
    value &= ~MENU_PHS
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
        if [o for o in sec.ops if _unlocks_phs(o) | (name in STORY_PHS_SHOW and _hides_phs_show(o))]:
            ctx.field(name).sections[0] = sec.build()

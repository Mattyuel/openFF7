"""New game: Cloud (named "Cloud" via SPCNM) alone at the Sector 7 station, PHS and full
menu available, all Shinra HQ keycards and three Batteries held. Cloud starts at
level 1 (KERNEL.BIN new-game data).

Battle speed is not set: it lives in the savemap's config block, which field
variables can't reach. SPECIAL GMSPD (0F F7) looked like the way, but the game
never uses it and a new game with it went to a black screen; don't use it.

The original new game runs in md1stin (Sector 1 station): entity 0's main
script has `if (progress == 0) { opening movie; menu mask; party; ...;
progress = 1 }`. That block is replaced with the openFF7 setup, ending in a
jump to the Sector 7 station.
"""
from _config import (CLOUD_START_LEVEL, MENU_LOCK, MENU_START, RECRUIT_COUNT, BATTERIES_ITEM, BATTERIES_QTY, BATTERY_BITS, CLOUD, HQ_ACCESS_LEVEL, HQ_KEYCARD_BITS, INITIAL_EVENT_FLAGS, OPEN_WORLD_PROGRESS, REGION_VARS, SUBMARINE_SLOT, START_DIR, START_FIELD,
                     START_TRIANGLE, START_X, START_Y)

from ff7 import asm
from ff7.disasm import PROGRESS_VAR
from ff7.script import Script

FIELD = "md1stin"


def _world_flags():
    """Flags from patches/world_flags.json (ff7tool.py quiet-flags), if present."""
    import json
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world_flags.json")
    if not os.path.exists(path):
        return []
    return [tuple(b) for b in json.load(open(path))]
MENU_MASK = (2, 28)


def _find_new_game_block(sec):
    """Return (if_op, ops_inside) for `if progress == 0` containing `var[2][28] = 763`."""
    for i, op in enumerate(sec.ops):
        if op.op != 0x18 and op.op != 0x16:
            continue
        banks, a, b, cmp = op.raw[1], op.raw[2] | op.raw[3] << 8, op.raw[4] | op.raw[5] << 8, op.raw[6]
        if (banks >> 4, a) != PROGRESS_VAR or banks & 15 or b != 0 or cmp != 0:
            continue
        end = sec.index(op.target)
        body = sec.ops[i + 1:end]
        if any(o.op == 0x81 and o.raw[2] == 28 and (o.raw[3] | o.raw[4] << 8) == 763 for o in body):
            return op, body
    raise RuntimeError("new-game block not found in %s" % FIELD)


def _cloud_level(ctx):
    from ff7.kernel import baseline, exp_for_level
    growth = ctx.kernel_growth()
    lv = CLOUD_START_LEVEL
    exp = exp_for_level(growth, CLOUD, lv)
    ctx.kernel_init().set_level(CLOUD, lv, baseline(growth, CLOUD, lv), exp,
                                exp_for_level(growth, CLOUD, lv + 1) - exp)


def apply(ctx):
    _cloud_level(ctx)
    sec = Script.parse(ctx.field(FIELD).sections[0])
    cond, body = _find_new_game_block(sec)
    # The original block ends by writing progress = 1 then falls through to the target.
    new = [
        asm.setword(MENU_MASK, MENU_START),           # all but PHS (shown at 3 recruits)
        asm.setbyte(RECRUIT_COUNT, 1),                # Cloud
        asm.setword(MENU_LOCK, 0),                    # nothing greyed out (PHS, Save)
        asm.party(CLOUD),
        asm.Op(bytes([0xCD, 0x01, CLOUD])),  # MMBUD: Cloud available in PHS
        asm.member_lock(CLOUD),                       # MMBLK: Cloud can't leave the party (stays leader)
    ]
    for char in range(1, 9):
        new.append(asm.Op(bytes([0xCD, 0x00, char])))  # everyone else unavailable until recruited
    for var, initial in REGION_VARS.values():
        new.append(asm.setword(var, initial))
    for var, word in SUBMARINE_SLOT:                  # submarine parked by Junon (650)
        new.append(asm.setword(var, word))
    new.append(asm.setbyte(*HQ_ACCESS_LEVEL))
    for var, bit in HQ_KEYCARD_BITS:
        new.append(asm.biton(var, bit))
    for nibble, addr, bit in INITIAL_EVENT_FLAGS + _world_flags():
        new.append(asm.biton((nibble, addr), bit))
    new.append(asm.add_item(BATTERIES_ITEM, BATTERIES_QTY))
    for var, bit in BATTERY_BITS:
        new.append(asm.biton(var, bit))
    new += [
        asm.setword(PROGRESS_VAR, OPEN_WORLD_PROGRESS),
        asm.Op(bytes([0x33, 0x00])),  # UC 00: player control on
        asm.Op(bytes([0x4A, 0x00])),  # MENU2 00: menu enabled
        asm.mapjump(ctx.maplist.index(START_FIELD), START_X, START_Y, START_TRIANGLE, START_DIR),
        asm.ret(),
    ]
    # Cloud's name: the .exe gives him "Ex-SOLDIER" at new game (the naming
    # prompt was part of the skipped opening), so set it with SPCNM.
    from ff7.text import encode
    name_text = sec.add_string(encode("Cloud"))
    new.insert(0, asm.Op(bytes([0x0F, 0xFD, CLOUD, name_text])))  # SPCNM char text
    first = body[0]
    sec.insert_before(first, new)
    for op in body:
        sec.remove(op)
    ctx.field(FIELD).sections[0] = sec.build()

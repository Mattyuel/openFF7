"""Corneo's mansion: fully walkable, no story scenes, no Corneo.

The bedroom, dungeon, fight-room and escape scenes are switched off by
new-game flags (INITIAL_EVENT_FLAGS in _config.py), which also make Corneo
and the dressed-up party members absent. This patch handles what flags alone
don't: the doorman and entrance lock, the duplicate Corneo in the 2f hall, and
the ground-floor doors.
"""
from ff7.script import Op, Script


def _hall(ctx):
    """2f hall (colne_5): Corneo stood here in the original; always hidden."""
    sec = Script.parse(ctx.field("colne_5").sections[0])
    ent = sec.entity_index("COLNEO")
    init = sec.script_ops(ent, 0)
    # `if not (var[3][163] & 1) goto skip; TLKON 01; SOLID 01; VISI 00` -> always hide
    cond = next(o for o in init if o.op == 0x14 and o.raw[2] == 163)
    sec.remove(cond)
    ctx.field("colne_5").sections[0] = sec.build()


def _entrance(ctx):
    """Mansion entrance (colne_1): the doorman blocked the door and the floor in
    front of it was locked until Corneo's bedroom scene was done. Remove both."""
    sec = Script.parse(ctx.field("colne_1").sections[0])
    ad = sec.entity_index("AD")
    for op in [o for o in sec.script_ops(ad, 0) if o.op == 0x6D and o.raw[3] == 1]:
        sec.remove(op)                                       # IDLCK .. 01 (lock)
    doorman = sec.entity_index("DOORMAN")
    cond = next(o for o in sec.script_ops(doorman, 0) if o.op == 0x14 and o.raw[2] == 163)
    sec.remove(cond)                                         # always hidden
    ctx.field("colne_1").sections[0] = sec.build()


OFFICE_DOOR_LAYER, DUNGEON_DOOR_LAYER = 1, 2   # background layers drawing the closed doors


def _ground_floor(ctx):
    """Mansion 1f (colne_2): the office door (upstairs) and the dungeon door
    were locked floor triangles plus 'Closed / Keep Out' lines, opened by story
    flags. Open both for good, and stop the hall's loop that played the
    "Cloud!!" scene with Tifa (it also added her to the party)."""
    sec = Script.parse(ctx.field("colne_2").sections[0])
    ad2 = sec.entity_index("AD2")
    init = sec.script_ops(ad2, 0)
    end = next(o for o in init if o.op == 0x00)
    locked = sorted({o.raw[1] | o.raw[2] << 8 for o in init if o.op == 0x6D})
    opened = [Op(bytes([0x6D, t & 0xFF, t >> 8, 0x00])) for t in locked]   # IDLCK .. 00
    opened += [Op(bytes([0xE1, 0x00, layer, 0x01]))                       # BGOFF door
               for layer in (OFFICE_DOOR_LAYER, DUNGEON_DOOR_LAYER)]
    sec.insert_before(end, opened)  # jumps to the init's RET now run these first
    main_first = init[init.index(end) + 1]
    sec.insert_before(main_first, [Op(b"\x00")], retarget=False)        # main: RET
    for name in ("KDLINE", "CDLINE"):
        ent = sec.entity_index(name)
        ret = next(o for o in sec.script_ops(ent, 0) if o.op == 0x00)
        sec.insert_before(ret, [Op(b"\xD1\x00")])                       # LINON 00
    ctx.field("colne_2").sections[0] = sec.build()


def apply(ctx):
    _hall(ctx)
    _entrance(ctx)
    _ground_floor(ctx)

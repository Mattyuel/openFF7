"""Open-world fixes outside Midgar that pinning and new-game flags can't do
(see docs/research_story_scenes.md; flags are in _config.INITIAL_EVENT_FLAGS,
pins in world_overrides.json):

- Mideel is always its disc 3 version: wm0.ev's Mideel map cell (0xB7A4) picks
  field.tbl entry B (itown1b) when progress >= 1197; the world map sees the
  global progress (100), so the comparison constant becomes 0.
- Cargo ship: the Jenova BIRTH line in shpin_3 (ELINE) has no flag; it is
  turned off in its init (the boss comes back as a quest boss fight).
- Junon: crossing the `aho` line in ujunon1 sent a guard to block the
  elevator unless progress == 406; now it always goes up (junin7, as at 406).
- Gate of Naught (cosin2) is always open: the opening Bugenhagen does at
  progress 502-513 with (3,170) bit 2 (door BG + hide both door models) runs
  on every entry, without its fade.
- Story progress stays at 100: fields that still write var[2][0] after
  pinning (unpinned ones such as gidun_3 after Gi Nattak, trnad_1, ancnt3,
  jtmpin2, corel1-3, the blackbg cutscene rooms) get those writes removed.
  The world map reads the global value (e.g. Mideel, vehicles), and every
  other field is pinned. md1stin (the new-game block) is left alone.
"""
from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh
from ff7.worldmap import EvPatcher, EvScript

MIDEEL_CELL = 0xB7A4
MIDEEL_DISC3_PROGRESS = 1197


def _mideel(ctx):
    data = ctx.wm_file("wm0.ev")
    script = EvScript(data)
    start = next(off for _, fid, off in script.functions() if fid == MIDEEL_CELL)
    nxt = min(off for _, _, off in script.functions() if off > start)
    code = [x for x in script.disassemble() if start <= x.pos < nxt]
    hits = [i for i, x in enumerate(code)
            if x.op == 0x11C and x.arg == 0 and code[i + 1].op == 0x110
            and code[i + 1].arg == MIDEEL_DISC3_PROGRESS and code[i + 2].op == 0x063]
    assert len(hits) == 1, "Mideel progress >= 1197 check not found"
    ev = EvPatcher(data)
    ev.set_word(code[hits[0] + 1].pos + 1, 0)                 # progress >= 0
    data[:] = ev.build()


def _line_off(ctx, field, name):
    sec = Script.parse(ctx.field(field).sections[0])
    init = sec.script_ops(sec.entity_index(name), 0)
    assert init[0].op == 0xD0, "%s %s: no LINE" % (field, name)
    sec.insert_after(init[0], [Op(b"\xD1\x00")])               # LINON 00
    ctx.field(field).sections[0] = sec.build()


def _junon_elevator(ctx):
    field = "ujunon1"
    sec = Script.parse(ctx.field(field).sections[0])
    ent = sec.entity_index("aho")
    old = sec.script_ops(ent, 2)
    jump = next(o for o in old if o.op == 0x60)                # the progress-406 MAPJUMP
    assert jump.raw[1:3] == ctx.maplist.index("junin7").to_bytes(2, "little"), jump.raw.hex()
    x, y, tri = (int.from_bytes(jump.raw[i:i + 2], "little", signed=True) for i in (3, 5, 7))
    assert Walkmesh(ctx.field("junin7").section("walkmesh")).contains(tri, x, y)
    sec.replace_script(ent, 2, [Op(b"\x33\x00"), Op(bytes(jump.raw)), asm.ret()])  # UC 00, MAPJUMP
    ctx.field(field).sections[0] = sec.build()


def _gate_of_naught(ctx):
    field = "cosin2"
    sec = Script.parse(ctx.field(field).sections[0])
    main = sec.script_ops(sec.entity_index("directr"), 0)
    ret = next(i for i, o in enumerate(main) if o.op == 0x00)
    body = main[ret + 1:]
    ifs = [o for o in body if o.op in (0x14, 0x15, 0x16, 0x17, 0x18, 0x19)]
    fades = [o for o in body if o.op in (0x6B, 0x6C)]            # FADE, FADEW
    assert len(ifs) == 3 and len(fades) == 3, [o.raw.hex() for o in body]
    assert any(o.op == 0xE1 for o in body), "no BGOFF in the opening"
    for o in ifs + fades:
        sec.remove(o)
    ctx.field(field).sections[0] = sec.build()


# Ops whose first var operand is a destination: [banks][addr]... with the
# destination bank in the high nibble, except INC/DEC/RANDOM (low nibble).
DST_HIGH = set(range(0x76, 0x7A)) | {0x80, 0x81} | set(range(0x84, 0x95)) | {0x9A, 0x9B}
DST_LOW = set(range(0x7A, 0x7E)) | set(range(0x95, 0x9A))
PROGRESS = (2, 0)                  # var[2][0] (bank 1, 16-bit, offset 0)
KEEP_PROGRESS_WRITES = {"md1stin"}


def _writes_progress(o):
    if o.op in DST_HIGH:
        nibble = o.raw[1] >> 4
    elif o.op in DST_LOW:
        nibble = o.raw[1] & 0x0F
    else:
        return False
    return (nibble, o.raw[2]) == PROGRESS


def _progress_writes(ctx):
    """Replace writes to the story progress var with NOPs."""
    for name in ctx.flevel.names():
        if "." in name or name == "maplist" or name in KEEP_PROGRESS_WRITES:
            continue
        try:
            sec = Script.parse(ctx.field(name).sections[0])
        except ValueError:
            continue
        hits = [o for o in sec.ops if _writes_progress(o)]
        for o in hits:
            sec.replace(o, [asm.nop()])
        if hits:
            ctx.field(name).sections[0] = sec.build()


def apply(ctx):
    _progress_writes(ctx)
    _mideel(ctx)
    _line_off(ctx, "shpin_3", "ELINE")
    _junon_elevator(ctx)
    _gate_of_naught(ctx)

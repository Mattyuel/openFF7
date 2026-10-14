"""Helpers for travel menus, attendant NPCs, touchable bosses and trigger lines."""
import struct

from _recruit import hide, say, window, xyzi

from ff7 import asm
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

CHOICE = (5, 241)  # temporary field variable for menu choices
TALK_RADIUS = 0x46  # as the Sector 7 station conductor
# fship_5 'cho' main script, yellow case: tint a chocobo model yellow.
CHOCOBO_YELLOW = [bytes.fromhex("28180600001e000f00c4ff1e000f00c4ff01000100010001"),  # KAWAI 06 colour
                  bytes.fromhex("240100"),                                           # WAIT 1
                  bytes.fromhex("28040601"),                                         # KAWAI 06 apply
                  bytes.fromhex("29")]                                               # KAWIW


def choice_menu(sec, prompt, options, jumps, face=False):
    """ASK with `options`; for each option index i, jumps[i] is a list of ops
    (or None = do nothing). Returns the ops (ending with UC 00 + RET).
    face: the talking entity turns to the player first (PTURA + WAIT)."""
    lines = prompt.split("\n")
    text = prompt + "".join("\n{CHOICE}" + o for o in options)
    first = len(lines)
    tid = sec.add_string(encode(text))
    end = [Op(b"\x33\x00"), asm.ret()]
    ops = [Op(b"\x33\x01")] + ([Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")] if face else [])
    ops += [window(text), asm.ask(0, tid, first, first + len(options) - 1, CHOICE)]
    for i, act in enumerate(jumps):
        if not act:
            continue
        skip = asm.nop()
        ops += [asm.if_byte(CHOICE, "==", first + i, skip)] + act + [skip]
    return ops + end


def mapjump(ctx, field, x, y, tri, direction=0):
    return asm.mapjump(ctx.maplist.index(field), x, y, tri, direction)


def copy_model(ctx, field, donor_field, donor_index):
    donor = ModelLoader(ctx.field(donor_field).section("models"))
    loader = ModelLoader(ctx.field(field).section("models"))
    idx = loader.add_from(donor, donor_index)
    ctx.field(field).set_section("models", loader.build())
    return idx


def near(ctx, field, triangle):
    """Centre (x, y, z, tri) of a walkmesh triangle next to `triangle`."""
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    nb = [n for n in mesh.access[triangle] if n >= 0] or [triangle]
    x, y, z = mesh.center(nb[0])
    return x, y, z, nb[0]


def beside(ctx, field, x, y, triangle, dist=60):
    """A spot (x, y, z, tri) about `dist` from (x, y) on walkable floor
    connected to `triangle`, at floor height (for an NPC next to an arrival)."""
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    near_tris = mesh.nearby(triangle)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
        px, py = x + dx * dist, y + dy * dist
        tri = next((t for t in near_tris if mesh.contains(t, px, py)), None)
        if tri is not None:
            return px, py, mesh.height(tri, px, py), tri
    raise RuntimeError("no floor beside (%d, %d) in %s" % (x, y, field))


def screen_step(ctx, field, x, y, screen_dir, dist):
    """A floor spot (x, y, z, tri) `dist` field units from (x, y) in the field
    direction that looks most like `screen_dir` (dx, dy; y down) on screen."""
    import math
    from ff7.camera import Camera, facing_screen
    f = ctx.field(field)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    tri = mesh.find(x, y)
    assert tri is not None, (field, x, y)
    a = facing_screen(cam, x, y, mesh.height(tri, x, y), screen_dir) * 2 * math.pi / 256
    px, py = round(x + math.sin(a) * dist), round(y - math.cos(a) * dist)
    t = mesh.find(px, py)
    assert t is not None, "%s: (%d, %d) is off the floor" % (field, px, py)
    return px, py, mesh.height(t, px, py), t


def line_across(ctx, field, x, y, overhang=30, reach=800):
    """A LINE ((x1, y1, z1), (x2, y2, z2)) through (x, y) across the floor at
    its narrowest there, reaching a little past the walkable edge on both
    sides so it can't be walked around (for boss trigger lines)."""
    import math
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    tri = mesh.find(x, y)
    assert tri is not None, "%s: (%d, %d) is not on the walkmesh" % (field, x, y)
    z = mesh.height(tri, x, y)

    def run(dx, dy):
        d = 0
        while d < reach and mesh.find(round(x + dx * (d + 10)), round(y + dy * (d + 10))) is not None:
            d += 10
        return d
    best = None
    for deg in range(0, 180, 5):
        a = math.radians(deg)
        dx, dy = math.cos(a), math.sin(a)
        span = (run(dx, dy), run(-dx, -dy))
        if best is None or sum(span) < sum(best[0]):
            best = (span, dx, dy)
    (fwd, back), dx, dy = best
    p1 = (round(x + dx * (fwd + overhang)), round(y + dy * (fwd + overhang)), z)
    p2 = (round(x - dx * (back + overhang)), round(y - dy * (back + overhang)), z)
    return p1, p2


def add_line(ctx, field, name, p1, p2, on_cross, init_extra=()):
    """Add a LINE entity across p1-p2 ((x, y, z) each); `on_cross` ops (ending
    with RET) run when the player walks over it (script 2); `init_extra` ops
    run once on field entry."""
    sec = Script.parse(ctx.field(field).sections[0])
    line = Op(bytes([0xD0]) + struct.pack("<6h", *p1, *p2))
    ent = sec.add_entity(name, {0: [line] + list(init_extra) + [asm.ret(), asm.ret()]})
    body = on_cross(sec) if callable(on_cross) else on_cross
    sec.ops.extend(body)
    sec.entry[ent][2] = body[0]
    ctx.field(field).sections[0] = sec.build()
    return ent


def add_npc(ctx, field, name, model, pos, direction, talk, init_extra=(), main=()):
    """Add an NPC entity with `model` at pos (x, y, z, tri); `talk` is its talk
    script ops (must end with RET); `main` ops run once after all inits."""
    sec = Script.parse(ctx.field(field).sections[0])
    init = [Op(bytes([0xA1, model])), xyzi(*pos), Op(bytes([0xB3, 0x00, direction])),
            Op(bytes([0xC5, 0x00, TALK_RADIUS]))]                # TALKR
    init += list(init_extra) + [asm.ret()] + list(main) + [asm.ret()]
    ent = sec.add_entity(name, {0: init})
    body = talk(sec) if callable(talk) else talk
    sec.ops.extend(body)
    sec.entry[ent][1] = body[0]
    ctx.field(field).sections[0] = sec.build()
    return ent


def reuse_npc(ctx, field, entity, donor, pos, direction, talk, init_extra=(), main=None):
    """An NPC in a field already at 16 models: it takes over entity `entity`
    (one the pinned moment keeps hidden): that entity's model entry becomes
    `donor` = (field, model index), its init's CHAR is replaced in place by
    CHAR + XYZI + DIR + TALKR and a jump over the rest of the old init (so no
    second CHAR), its main is dropped, its talk is `talk(sec)` and every other
    script slot becomes RET (calls from other entities do nothing). `init_extra`: ops after the
    TALKR; `main`: ops for a new main (default none). Returns the model index."""
    sec = Script.parse(ctx.field(field).sections[0])
    ent = sec.entity_index(entity)
    init = sec.script_ops(ent, 0)
    assert init[0].op == 0xA1, (field, entity, init[0].raw.hex())          # CHAR
    model = init[0].raw[1]
    loader = ModelLoader(ctx.field(field).section("models"))
    src = ModelLoader(ctx.field(donor[0]).section("models"))
    entry = src.models[donor[1]]
    loader.models[model] = loader.with_scale(entry, round(loader.entry_scale(entry) * loader.scale / src.scale))
    ctx.field(field).set_section("models", loader.build())
    ret = next(o for o in init if o.op == 0x00)
    sec.replace(init[0], [Op(bytes([0xA1, model])), xyzi(*pos), Op(bytes([0xB3, 0, direction])),
                          Op(bytes([0xC5, 0x00, TALK_RADIUS]))] + list(init_extra) + [asm.goto(ret)])
    old_main = init[init.index(ret) + 1]
    sec.insert_before(old_main, list(main or []) + [asm.ret()], retarget=True)    # no old main
    body = talk(sec) if callable(talk) else talk
    empty = asm.ret()
    sec.ops.extend([empty] + body)
    first = sec.entry[ent][0]
    sec.entry[ent] = [empty] * 32
    sec.entry[ent][0], sec.entry[ent][1] = first, body[0]
    ctx.field(field).sections[0] = sec.build()
    return model

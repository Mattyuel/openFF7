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


def choice_menu(sec, prompt, options, jumps):
    """ASK with `options`; for each option index i, jumps[i] is a list of ops
    (or None = do nothing). Returns the ops (ending with UC 00 + RET)."""
    lines = prompt.split("\n")
    text = prompt + "".join("\n{CHOICE}" + o for o in options)
    first = len(lines)
    tid = sec.add_string(encode(text))
    end = [Op(b"\x33\x00"), asm.ret()]
    ops = [Op(b"\x33\x01"), window(text), asm.ask(0, tid, first, first + len(options) - 1, CHOICE)]
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

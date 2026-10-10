"""Helpers for travel menus, attendant NPCs and touchable bosses."""
from _recruit import hide, say, window, xyzi

from ff7 import asm
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

CHOICE = (5, 241)  # temporary field variable for menu choices


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
    idx = loader.add(donor.models[donor_index])
    ctx.field(field).set_section("models", loader.build())
    return idx


def near(ctx, field, triangle):
    """Centre (x, y, z, tri) of a walkmesh triangle next to `triangle`."""
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    nb = [n for n in mesh.access[triangle] if n >= 0] or [triangle]
    x, y, z = mesh.center(nb[0])
    return x, y, z, nb[0]


def add_npc(ctx, field, name, model, pos, direction, talk, init_extra=()):
    """Add an NPC entity with `model` at pos (x, y, z, tri); `talk` is its talk
    script ops (must end with RET)."""
    sec = Script.parse(ctx.field(field).sections[0])
    init = [Op(bytes([0xA1, model])), xyzi(*pos), Op(bytes([0xB3, 0x00, direction]))]
    init += list(init_extra) + [asm.ret(), asm.ret()]
    ent = sec.add_entity(name, {0: init})
    body = talk(sec) if callable(talk) else talk
    sec.ops.extend(body)
    sec.entry[ent][1] = body[0]
    ctx.field(field).sections[0] = sec.build()
    return ent

"""(user) Cid as a friend (data `_cid.py`): his NPC by the rocket on the launch pad north of Rocket
Town (rcktbas1, taking over his story copy's entity `cid`: `_travel.reuse_npc`), facing down the
screen. Talk (after a first introduction, MET): "Just chat." (a line by affection tier, with his
affection) / "Hang out." ("Where to?": 660's date places; DATE_GIRL = `_cid.INDEX` + 1 and a MAPJUMP
into that place's date field, where he is a companion (660 `COMPANIONS`): his first hang-out is the
quest "hangout_cid", accepted here) / "Give him something." (each held gift in turn as the Honey Bee
lounges' gift menu; his likes `_cid.PREFS`, capped at `_cid.MAX`) / "Never mind."
After 660 (its date fields and arrivals, `ARRIVE`).
"""
import importlib

import _cid as C
import _honey_bee_gifts as gifts
from _recruit import sound
from _travel import CHOICE, reuse_npc

from ff7 import asm
from ff7.camera import Camera, facing_screen
from ff7.script import Op
from ff7.walkmesh import Walkmesh


def _gifts(sec, hb):
    """His gift menu (ops ending at their own end label): nothing at MAX or with no gift held."""
    aff = C.AFFECTION
    end, menu = asm.nop(), asm.nop()
    ops = [asm.if_byte(aff, ">=", C.MAX, menu)] + hb._say(sec, C.NAME + "\n" + C.MAXED) + [asm.goto(end), menu]
    none, held = asm.nop(), asm.nop()
    for j in range(len(gifts.GIFTS)):
        kv, bit = hb._key_bit(j)
        nxt = asm.nop()
        ops += [asm.if_byte(kv, "bit_on", bit, nxt), asm.goto(held), nxt]
    ops += hb._say(sec, C.NAME + "\n" + C.NO_GIFT) + [asm.goto(end), held]
    react = {k: asm.nop() for k in gifts.GAIN}
    top = asm.nop()
    ops.append(top)
    for j, (name, _, t, _, _) in enumerate(gifts.GIFTS):
        kv, bit = hb._key_bit(j)
        skip, give = asm.nop(), asm.nop()
        ask, first = hb._ask(sec, C.GIVE_PROMPT % name, ["Give it.", "Next gift.", "Not now."])
        ops += [asm.if_byte(kv, "bit_on", bit, skip)] + ask
        ops += [asm.if_byte(CHOICE, "!=", first + 1, skip),
                asm.if_byte(CHOICE, "!=", first, give), asm.goto(end),
                give, asm.bitoff(kv, bit), asm.goto(react[C.PREFS[t]]), skip]
    ops += [asm.goto_back(top)]
    for like, label in react.items():
        gain, ok = gifts.GAIN[like], asm.nop()
        ops += [label]
        if gain:
            ops += [Op(bytes([0x85, aff[0] << 4, aff[1], gain])), asm.if_byte(aff, ">", C.MAX, ok),
                    asm.setbyte(aff, C.MAX), ok]
        ops += hb._show_aff(hb._say(sec, C.NAME + "\n" + C.REACT[like]), aff)
        ops += [sound(0x168) if like == "L" else asm.nop(), asm.goto(end)]
    return ops + [end]


def _talk(ctx, hb, dt, sec):
    qx = importlib.import_module("600_quests")
    aff = C.AFFECTION
    her = lambda t: C.NAME + "\n" + t
    done = asm.nop()
    met = asm.nop()
    ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8),                       # PTURA: face the player
           asm.if_byte(C.MET[0], "bit_off", C.MET[1], met)] + hb._say(sec, her(C.FIRST_MET)) + \
        [asm.biton(*C.MET), met]
    ask, first = hb._ask(sec, her(C.GREET), C.TALK_ASK)
    ops += ask
    # chat: a line by tier, with his affection
    chat, tier1, tier2 = asm.nop(), asm.nop(), asm.nop()
    ops += [asm.if_byte(CHOICE, "==", first, chat)]
    show = lambda t: hb._show_aff(hb._say(sec, her(t + "\n (Affection: {VAR}/20)")), aff)
    ops += [asm.if_byte(aff, "<", dt.TIERS[0], tier1)] + show(C.CHAT[0]) + [asm.goto(done), tier1,
            asm.if_byte(aff, "<", dt.TIERS[1], tier2)] + show(C.CHAT[1]) + [asm.goto(done), tier2] + \
        show(C.CHAT[2]) + [asm.goto(done), chat]
    # hang out: where to?
    hang = asm.nop()
    ops += [asm.if_byte(CHOICE, "==", first + 1, hang)]
    ask2, first2 = hb._ask(sec, her(C.HANGOUT["where"]), [dt.PLACE_NAMES[p] for p in dt.PLACES] + ["Never mind."])
    ops += ask2
    qstate, new = qx.quest_state("hangout_cid"), asm.nop()
    accept = [asm.if_byte(qstate, "==", qx.NEW, new), asm.setbyte(qstate, qx.ACCEPTED), new]
    for k, p in enumerate(dt.PLACES):
        nxt = asm.nop()
        (x, y, z, tri), adir = ctx.date_arrive[0][p]
        ops += [asm.if_byte(CHOICE, "==", first2 + k, nxt)] + accept + \
            [asm.setbyte(dt.DATE_GIRL, C.INDEX + 1), hb._uc(0),
             asm.mapjump(ctx.maplist.index(dt.FIELDS[(p, 0)]), x, y, tri, adir), asm.ret(), nxt]
    ops += [asm.goto(done), hang]
    # gifts
    gift = asm.nop()
    ops += [asm.if_byte(CHOICE, "==", first + 2, gift)] + _gifts(sec, hb) + [gift]
    return ops + [done, hb._uc(0), asm.ret()]


def apply(ctx):
    hb = importlib.import_module("620_honey_bee")
    dt = importlib.import_module("660_dates")
    assert C.NAME in dt.COMPANIONS and len(gifts.GIFTS) == 12 and len(C.PREFS) == len(gifts.TYPES)
    f = ctx.field(C.FIELD)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    x, y = C.AT
    tri = mesh.find(x, y)
    assert tri is not None, C.AT
    z = mesh.height(tri, x, y)
    from ff7.script import Script
    model = Script.parse(f.sections[0])
    ent = model.entity_index(C.ENTITY)
    char = next(o for o in model.script_ops(ent, 0) if o.op == 0xA1).raw[1]
    reuse_npc(ctx, C.FIELD, C.ENTITY, (C.FIELD, char), (x, y, z, tri), facing_screen(cam, x, y, z, (0, 1)),
              lambda sec: _talk(ctx, hb, dt, sec))

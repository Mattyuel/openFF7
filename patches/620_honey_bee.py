"""Honey Bee Girl recruitment.

- The Honey Bee Inn's manager (onna_4, the lobby) offers Cloud a job: find
  girls for the Inn (HB_JOB). After that he lists the girls you've hired, best
  first (stars, then the order in _honey_bee_data.GIRLS): pick one to visit.
- 20 girls stand around the world (_honey_bee_data.py). Before the job they
  only say a line. With the job, talking to one starts her pitch, then her
  questions (as many as her stars); every answer right = hired (HB_HIRED bit),
  one wrong = talk again later.
- Earnings: the manager pays HB_RATE gil per star of every hired girl per
  minute of play since the last collection (at most HB_CAP minutes). The
  exe's play clock keeps the minutes in HB_MINUTES (quest_menu.asm q_clock).
- A visit jumps to the "&" room (onna_52) with HB_VISIT = girl + 1. There the
  room's own scene (produce main) and its exit line are off, and a new
  director entity plays her scene: the Honey Bee dancer (girl2, with all 22
  Honey Bee dancer animations of the game added to her model) and Cloud act
  out beats (entity scripts added in their free slots), then the screen fades
  and "You spent the rest of the night together and had a good time..." and
  you're back in the lobby beside the manager.
"""
import struct

from _config import HB_CAP, HB_HIRED, HB_JOB, HB_LAST, HB_MINUTES, HB_RATE, HB_VISIT
from _honey_bee_data import GIRLS, STARS
from _recruit import SOUND_RECRUIT, sound
from _travel import CHOICE, add_npc, beside, copy_model

from ff7 import asm
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

LOBBY, ROOM = "onna_4", "onna_52"
MANAGER_MODEL = ("md8_2", 3)                 # midgal_man
MANAGER_AT, MANAGER_DIR = (104, -48), 0
ROOM_ARRIVE = (211, 102, 6, 220)             # at the bed, out of the girl's way (onna_4's own arrival,
                                             # (263, 163), is on her path: she ran into Cloud)
SHOWN = (5, 245)                             # temp: a hired girl was listed
TOTAL, ELAPSED, EARN = (6, 246), (6, 248), (6, 250)   # temp words: stars, minutes, gil
FINAL = "You spent the rest of the night together\nand had a good time..."
OFFER = "{CLOUD}\n“There's a job going at the Honey Bee Inn.\n Interested?”"

# onna_52 spots (x, y): from the room's own scene
DOOR, NEAR_BED, MID, FAR, BED = (347, 230), (275, 107), (248, 150), (117, 250), (211, 102)
GIRL, CLOUD = "girl2", "cloud"
WALK, RUN = 0x0800, 0x1400
# girl2's model (market_dancer): its 5 animations, then every other Honey Bee
# dancer animation in the game (same skeleton BADD.HRC)
DANCER_ANIMS = ["BAJB.tor", "BCCC.tor", "BCCD.tor", "AVJE.aki", "BYAD.aki"]
DANCER_EXTRA = ["DXHE.tor", "DXIB.tor", "DXIF.tor", "DXJA.tor", "DXJB.tor", "BAJF.tor", "BBAA.tor",
                "BAJD.tor", "BAJC.tor", "DXJC.tor", "DXJD.tor", "DXIC.tor", "DZBA.tor", "DIEF.chi",
                "DXIE.tor", "BAJE.tor", "AAGA.aki"]
CLOUD_ANIMS = {"stand": 0, "sit": 3, "startle": 4, "look": 8, "look2": 9, "jump1": 10, "jump2": 11,
               "hesitate": 12, "scratch": 13, "blush1": 16, "blush2": 17, "blush3": 18, "lie": 20}
JUMP_SOUND = bytes.fromhex("f20000002840e9000000000000000000")[:14]


# ---- ops --------------------------------------------------------------------
def _w(n):
    return Op(b"\x24" + struct.pack("<H", n))


def _anim(i, hold=False):
    return Op(bytes([0xAF if hold else 0xA3, i, 1]))         # ANIM!1 / ANIME1


def _canm(i, a, b):
    return Op(bytes([0xB1, i, a, b, 1]))                    # CANM!1 frames a..b, hold


def _move(x, y):
    return Op(bytes([0xA8, 0]) + struct.pack("<hh", x, y))


def _msped(v):
    return Op(bytes([0xB2, 0]) + struct.pack("<H", v))


def _tura(ent):
    return Op(bytes([0xAB, ent, 0x0A, 2]))


def _turn(turns):
    return Op(bytes([0xB4, 0, 0, turns, 0x0A, 2]))           # TURNGEN


def _visi(on):
    return Op(bytes([0xA4, on]))


def _xyzi(x, y, z, tri):
    return Op(bytes([0xA5, 0, 0]) + struct.pack("<hhhH", x, y, z, tri))


def _uc(on):
    return Op(bytes([0x33, on]))


def _menu(off):
    return Op(bytes([0x4A, off]))                            # MENU2


def _req(ent, slot, wait=True):
    return Op(bytes([0x03 if wait else 0x02, ent, 0xC0 | slot]))


def _arith(op, dst, src):
    """PLUS2 0x86 / MINUS2 0x88 / MUL2 0x8A [banks][dst][u16 src]: dst word op= src
    (a (nibble, offset) var or a literal)."""
    sb, sv = (src if isinstance(src, tuple) else (0, src))
    return Op(bytes([op, dst[0] << 4 | sb, dst[1]]) + struct.pack("<H", sv))


def _collect(sec, end):
    """Income since the last collection: total stars of the hired girls x
    HB_RATE gil x minutes (at most HB_CAP), paid with GOLDU and shown with
    MPRA2 + {VAR}; HB_LAST = now."""
    none, idle = asm.nop(), asm.nop()
    ops = [asm.setword(TOTAL, 0)]
    for i, g in enumerate(GIRLS):
        hv, bit = _hired(i)
        skip = asm.nop()
        ops += [asm.if_byte(hv, "bit_on", bit, skip), _arith(0x86, TOTAL, g["stars"]), skip]
    ops += [asm.if_word(TOTAL, "!=", 0, none),
            asm.setword(ELAPSED, HB_MINUTES), _arith(0x88, ELAPSED, HB_LAST)]   # minutes since the last cut
    capped = asm.nop()
    ops += [asm.if_word(ELAPSED, ">", HB_CAP, capped), asm.setword(ELAPSED, HB_CAP), capped,
            asm.setword(EARN, ELAPSED), _arith(0x8A, EARN, TOTAL), _arith(0x8A, EARN, HB_RATE),
            asm.if_word(EARN, "!=", 0, idle),
            Op(bytes([0x39, EARN[0] << 4]) + struct.pack("<I", EARN[1])),           # GOLDU var
            asm.setword(HB_LAST, HB_MINUTES), sound(0x168)]                         # the item chime
    paid = _say(sec, "Manager\n“Your girls have been busy!\n Here's your cut: {VAR} gil.”")
    paid.insert(1, Op(bytes([0x42, EARN[0], 0, 0]) + struct.pack("<H", EARN[1])))  # MPRA2 after WINDOW: the number
    ops += paid + [asm.goto(end)]
    ops += [idle] + _say(sec, "Manager\n“Nothing yet, partner. Give the\n girls some time to earn.”") + [asm.goto(end)]
    ops += [none] + _say(sec, "Manager\n“No girls, no money. Go hire some!”") + [asm.goto(end)]
    return ops


def _hired(i):
    return (HB_HIRED[0], HB_HIRED[1] + i // 8), i % 8


def _window(text, win=0, x=8, y=8):
    pages = [p.lstrip("\n").split("\n") for p in text.split("{NEW}")]
    widest = max(len(l.replace("{CHOICE}", "     ").replace("{CLOUD}", "Cloud ")
                     .replace("{TIFA}", "Tifa").replace("{AERIS}", "Aerith"))
                 for p in pages for l in p)
    w = min(310, widest * 7 + 24)
    h = 16 * max(len(p) for p in pages) + 9
    return Op(bytes([0x50, win]) + struct.pack("<HHHH", x, y, w, h))


def _say(sec, text, win=0, x=8, y=8):
    return [_window(text, win, x, y), asm.message(win, sec.add_string(encode(text)))]


def _ask(sec, text, choices, win=0):
    """(ops, first): ASK with `choices`; CHOICE = first + index picked."""
    assert "{NEW}" not in text
    first = len(text.split("\n"))
    full = text + "".join("\n{CHOICE}" + c for c in choices)
    tid = sec.add_string(encode(full))
    return [_window(full, win), asm.setbyte(CHOICE, 0),
            asm.ask(win, tid, first, first + len(choices) - 1, CHOICE)], first


# ---- girls --------------------------------------------------------------
def _girl_talk(sec, i, g):
    end = _uc(0)
    stranger, idle, fail = asm.nop(), asm.nop(), asm.nop()
    hv, bit = _hired(i)
    ops = [_uc(1), Op(b"\x35\x00\x08\x02"), _w(8),                     # PTURA: face the player
           asm.if_byte(HB_JOB[0], "bit_on", HB_JOB[1], stranger),       # no job yet
           asm.if_byte(hv, "bit_off", bit, idle)]                       # already hired
    ops += _say(sec, g["intro"])
    offer, first = _ask(sec, OFFER, ["Offer her the job.", "Never mind."])
    ops += offer + [asm.if_byte(CHOICE, "==", first, end)]
    ops += _say(sec, g["reply"])
    assert len(g["questions"]) == g["stars"], g["name"]
    for text, choices, right in g["questions"]:
        q, first = _ask(sec, text, choices)
        ops += q + [asm.if_byte(CHOICE, "==", first + right, fail)]
    ops += [sound(SOUND_RECRUIT), asm.biton(hv, bit)] + _say(sec, g["hired"]) + [asm.goto(end)]
    ops += [fail] + _say(sec, g["fail"]) + [asm.goto(end)]
    ops += [stranger] + _say(sec, g["stranger"]) + [asm.goto(end)]
    ops += [idle] + _say(sec, g["idle"])
    return ops + [end, asm.ret()]


def _add_girls(ctx):
    for i, g in enumerate(GIRLS):
        f = g["field"]
        mesh = Walkmesh(ctx.field(f).section("walkmesh"))
        x, y = g["at"]
        tri = mesh.find(x, y)
        assert tri is not None, (f, x, y)
        model = copy_model(ctx, f, *g["model"])
        add_npc(ctx, f, "hb%02d" % i, model, (x, y, mesh.height(tri, x, y), tri), g["dir"],
                lambda sec, i=i, g=g: _girl_talk(sec, i, g))


# ---- the manager -----------------------------------------------------------
def _ranked():
    return sorted(range(len(GIRLS)), key=lambda i: (-GIRLS[i]["stars"], i))


def _manager(ctx, back):
    room = ctx.maplist.index(ROOM)
    rx, ry, rtri, rdir = ROOM_ARRIVE
    assert Walkmesh(ctx.field(ROOM).section("walkmesh")).contains(rtri, rx, ry)

    def talk(sec):
        end, offer, visit, tips, done, cut = _uc(0), asm.nop(), asm.nop(), asm.nop(), asm.nop(), asm.nop()
        ops = [_uc(1), Op(b"\x35\x00\x08\x02"), _w(8),
               asm.if_byte(HB_JOB[0], "bit_on", HB_JOB[1], offer)]
        menu, first = _ask(sec, "Manager\n“Back again, partner? What'll it be?”",
                           ["Visit one of the girls.", "Collect the girls' earnings.",
                            "Where do I find girls?", "Nothing."])
        ops += menu + [asm.if_byte(CHOICE, "!=", first, visit),
                       asm.if_byte(CHOICE, "!=", first + 1, cut),
                       asm.if_byte(CHOICE, "!=", first + 2, tips), asm.goto(end)]
        ops += [cut] + _collect(sec, end)
        # visit: every hired girl, best first
        ops += [visit, asm.setbyte(SHOWN, 0)]
        for i in _ranked():
            g = GIRLS[i]
            hv, bit = _hired(i)
            skip, go, stop = asm.nop(), asm.nop(), asm.nop()
            ask, first = _ask(sec, "Manager\n“%s (%s), our %s.”" % (g["name"], STARS[g["stars"]], g["tag"]),
                              ["Visit her.", "Next girl.", "Never mind."])
            ops += [asm.if_byte(hv, "bit_on", bit, skip), asm.setbyte(SHOWN, 1)] + ask
            ops += [asm.if_byte(CHOICE, "==", first, go),
                    asm.setbyte(HB_VISIT, i + 1), _uc(0), asm.mapjump(room, rx, ry, rtri, rdir), asm.ret(),
                    go, asm.if_byte(CHOICE, "==", first + 2, stop), asm.goto(end), stop, skip]
        ops += [asm.if_byte(SHOWN, "==", 0, done)]
        ops += _say(sec, "Manager\n“You haven't hired anybody yet!\n Get out there and charm 'em.”")
        ops += [asm.goto(end), done] + _say(sec, "Manager\n“That's the whole roster.”") + [asm.goto(end)]
        ops += [tips] + _say(sec, "Manager\n“Word is there are fine ladies in\n the slums, Wall Market, Fort Condor,\n"
                                  " Junon, Nibelheim, the Gold Saucer…”{NEW}\n"
                                  "“…Icicle country, Costa del Sol,\n Wutai, Rocket Town, Gongaga,\n"
                                  " Cosmo Canyon and Mideel.\n The more stars, the pickier they are.”") + [asm.goto(end)]
        # first talk: the job offer
        ops += [offer] + _say(sec, "Manager\n“Hey, spiky! You look like a guy\n with an eye for talent.”")
        ask, first = _ask(sec, "Manager\n“Find me girls for the Inn? I'll let\n you visit any you hire. On the house.”",
                          ["You've got a deal.", "Not interested."])
        no = asm.nop()
        ops += ask + [asm.if_byte(CHOICE, "==", first, no), asm.biton(*HB_JOB),
                      asm.setword(HB_LAST, HB_MINUTES)]                         # earnings count from now
        ops += _say(sec, "Manager\n“Great! Talk to the ladies you meet.\n The classier the girl, the more\n questions she'll ask. Get 'em all right!”")
        ops += [asm.goto(end), no] + _say(sec, "Manager\n“Your loss, partner.”")
        return ops + [end, asm.ret()]

    model = copy_model(ctx, LOBBY, *MANAGER_MODEL)
    mesh = Walkmesh(ctx.field(LOBBY).section("walkmesh"))
    mx, my = MANAGER_AT
    tri = mesh.find(mx, my)
    assert tri is not None
    add_npc(ctx, LOBBY, "hbboss", model, (mx, my, mesh.height(tri, mx, my), tri), MANAGER_DIR, talk)


# ---- the room ----------------------------------------------------------------
def _free_slots(sec, ent, start):
    used = {o.raw[2] & 0x1F for o in sec.ops if o.op in (1, 2, 3) and o.raw[1] == ent}
    shared = sec.entry[ent][31]
    return [k for k in range(start, 32) if k not in used and sec.entry[ent][k] is shared]


def _guard(sec, ent, first, ops_after):
    """In VISIT mode, `first` (an op of entity `ent`'s script 0) is skipped:
    ops_after run instead."""
    guard = [asm.if_byte(HB_VISIT, "!=", 0, first)] + ops_after
    sec.insert_before(first, guard, retarget=False)
    for k, o in enumerate(sec.entry[ent]):
        if o is first and k == 0:
            sec.entry[ent][k] = guard[0]


def _room(ctx, back):
    f = ctx.field(ROOM)
    mesh = Walkmesh(f.section("walkmesh"))

    def spot(p):
        t = mesh.find(*p)
        assert t is not None, p
        return p[0], p[1], mesh.height(t, *p), t

    loader = ModelLoader(f.section("models"))
    assert ModelLoader.anims(loader.models[1]) == DANCER_ANIMS, ModelLoader.anims(loader.models[1])
    loader.models[1] = ModelLoader.with_anims(loader.models[1], DANCER_EXTRA)
    f.set_section("models", loader.build())
    da = {n: i for i, n in enumerate(DANCER_ANIMS + DANCER_EXTRA)}
    assert ModelLoader.anims(loader.models[0])[CLOUD_ANIMS["sit"]] == "AQAA.tor"
    assert ModelLoader.anims(loader.models[0])[CLOUD_ANIMS["lie"]] == "EADD.tor"

    sec = Script.parse(f.sections[0])
    girl, cloud = sec.entity_index(GIRL), sec.entity_index(CLOUD)
    # room scene off in VISIT mode: produce's main, the exit line
    produce = sec.script_ops(sec.entity_index("produce"), 0)
    main = produce[produce.index(next(o for o in produce if o.op == 0)) + 1]
    # music: the room plays the Honey Bee Inn theme (block 0, id 68 as the lobby)
    # once (3,220) bit 0 is set, else the dream music (block 1); visits keep the theme
    assert sec.akao_ids()[0] == 68, sec.akao_ids()
    pick = next(o for o in produce if o.op == 0x14 and bytes(o.raw[1:5]) == bytes([0x30, 220, 0, 9]))
    menu = next(o for o in produce if o.op == 0x4A)
    sec.insert_before(pick, [asm.if_byte(HB_VISIT, "!=", 0, pick), Op(b"\xF0\x00"), asm.goto(menu)],
                      retarget=False)
    sec.insert_before(main, [asm.if_byte(HB_VISIT, "!=", 0, main), asm.ret()], retarget=False)
    border = sec.entity_index("border1")
    first = sec.entry[border][0]
    assert first.op == 0xD0, first.raw.hex()                       # LINE
    _guard(sec, border, first, [asm.ret(), asm.ret()])

    d = lambda n, times=1: [_anim(da[n])] * times
    c = CLOUD_ANIMS
    gx = lambda p: _move(*p)
    girl_beats = {
        "enter": [_xyzi(*spot(DOOR)), _visi(1), _msped(WALK), gx(MID), _tura(cloud)],
        "approach": [_msped(WALK), gx(NEAR_BED), _tura(cloud)],
        "mid": [_msped(WALK), gx(MID), _tura(cloud)],
        "far": [_msped(WALK), gx(FAR), _tura(cloud)],
        "leave": [_msped(WALK), gx(DOOR), _visi(0)],
        "back": [_visi(1), _msped(WALK), gx(MID), _tura(cloud)],
        "lap": [_msped(RUN), gx(FAR), gx(DOOR), gx(MID), _msped(WALK), _tura(cloud)],
        "spin": [_turn(2), _tura(cloud)],
        "dance1": d("DXHE.tor", 2), "dance2": d("DXIB.tor", 2), "dance3": d("DXIF.tor"),
        "dance4": d("DXJA.tor"), "dance5": d("DXJB.tor"), "dance6": d("BAJF.tor"),
        "dance7": d("BBAA.tor"), "dance8": d("BAJD.tor"), "wiggle": d("BAJC.tor", 2),
        "flourish": d("DXJC.tor"), "greet": d("DXJD.tor"), "beckon": d("BYAD.aki"),
        "look": d("AVJE.aki"), "chat": d("DXIC.tor", 2), "sulk": d("DIEF.chi"),
        "sway": d("DXIE.tor"),
        "pose": [_anim(da["DZBA.tor"], hold=True), _w(45), _anim(0)],
    }
    cloud_beats = {
        "sit": [_msped(WALK), gx(BED), _tura(girl), _canm(c["sit"], 0, 0x1D)],
        "stand": [_canm(c["sit"], 0x1D, 0x2C), _anim(c["stand"])],
        "jump": [_anim(c["jump1"]), Op(JUMP_SOUND), _anim(c["jump2"]), _anim(c["stand"])],
        "hesitate": [_anim(c["look2"]), _canm(c["hesitate"], 0, 0x0E), _canm(c["hesitate"], 0x0F, 0x1D),
                     _anim(c["scratch"])],
        "blush": [_anim(c["blush1"]), _anim(c["blush2"]), _anim(c["blush3"])],
        "startle": [_canm(c["startle"], 0, 0x0E), _anim(c["stand"])],
        "look": [_anim(c["look"]), _anim(c["look2"])],
        "ghost": [Op(b"\xC7\x01")],                                    # SOLID 01: the girl walks through
        "faint": [_canm(c["lie"], 0, 2)] * 3 + [_anim(c["lie"], hold=True)],
    }
    used = {s[1] for g in GIRLS for s in g["scene"] if s[0] in ("g", "g&")}
    used_c = {s[1] for g in GIRLS for s in g["scene"] if s[0] in ("c", "c&")} | {"ghost"}
    assert used <= set(girl_beats) and used_c <= set(cloud_beats), (used - set(girl_beats), used_c - set(cloud_beats))
    slots = {}
    for ent, beats, start in ((girl, girl_beats, 8), (cloud, cloud_beats, 24)):
        free = _free_slots(sec, ent, start)
        names = [n for n in beats if n in (used if ent == girl else used_c)]
        assert len(names) <= len(free), (ent, len(names), free)
        for name, k in zip(names, free):
            ops = [Op(bytes(o.raw)) for o in beats[name]] + [asm.ret()]
            sec.ops.extend(ops)
            sec.entry[ent][k] = ops[0]
            slots[(ent, name)] = k

    # the director
    lobby = ctx.maplist.index(LOBBY)
    bx, by, bz, btri = back
    finale, stop = asm.nop(), asm.ret()
    ops = [asm.if_byte(HB_VISIT, "!=", 0, stop), _uc(1), _menu(1),                # no visit: nothing
           _req(cloud, slots[(cloud, "ghost")]), _w(15)]
    for i, g in enumerate(GIRLS):
        nxt = asm.nop()
        ops += [asm.if_byte(HB_VISIT, "==", i + 1, nxt)]
        for step in g["scene"]:
            kind = step[0]
            if kind in ("g", "g&", "c", "c&"):
                ent = girl if kind[0] == "g" else cloud
                ops.append(_req(ent, slots[(ent, step[1])], wait=not kind.endswith("&")))
            elif kind == "G":
                ops += _say(sec, g["name"] + "\n" + step[1])
            elif kind == "C":
                ops += _say(sec, step[1], win=1, y=150)
            elif kind == "wait":
                ops.append(_w(step[1]))
            elif kind == "shake":
                ops += [Op(bytes.fromhex("5e00000200000804")), _w(20)]
            else:
                raise ValueError(step)
        ops += [asm.goto(finale), nxt]
    ops += [asm.goto(stop), finale, _w(30),
            Op(bytes.fromhex("6b0000000000080200")), Op(b"\x6C"), _w(20)]       # FADE out, FADEW
    ops += _say(sec, FINAL, x=24, y=96)
    ops += [asm.setbyte(HB_VISIT, 0), _uc(0), _menu(0),
            asm.mapjump(lobby, bx, by, btri, 0x80), stop]
    sec.add_entity("hbscene", {0: [asm.ret()] + ops})
    f.sections[0] = sec.build()
    n = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n <= 255, n


def apply(ctx):
    mesh = Walkmesh(ctx.field(LOBBY).section("walkmesh"))
    tri = mesh.find(*MANAGER_AT)
    back = beside(ctx, LOBBY, *MANAGER_AT, tri)
    _add_girls(ctx)
    _manager(ctx, back)
    _room(ctx, back)

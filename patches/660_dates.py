"""Dates with the Honey Bee girls (docs/dates_plan.md; data `_dates_data.py`).

Talking to a girl out in the world (hired or not, job or not) first asks
"Just chat." / "Ask her on a date."; a date asks "Where to?": the Gold Saucer
gondola or the space capsule. DATE_GIRL = her index + 1 and a MAPJUMP into
that place's date field for her group. Her affection (shared with the Honey
Bee, `_config.HB_AFFECTION`) picks the date: < 10 first, < 20 second, 20 third.
Right answers give +1 (capped at 20); the third date's choice ("Give into your
desires." / "Leave it be.") needs every answer of that date right. Afterwards
DATE_GIRL = 0 and back beside her.

Date fields are new fields (`ctx.new_field`) with a blank script: every entity
keeps its CHAR (model count and CHAR order unchanged), all old code and texts
are dropped, entity 0 becomes the director.
- gondola: bwhlin's still view (the Gold Saucer at night; no FMV, user), Cloud
  and her where the original date seats them, with their gondola sitting anims.
- capsule: rcktin7's pod with the space layer on (BG param 1 on, param 2 = the
  hatch's closed view off, as the original's `space` script 1): stars through
  the round window. Cloud and her on the benches either side of the gangway,
  facing each other (sitting anims borrowed from the gondola models).
"""
import math

from _config import DATE_GIRL, HB_AFFECTION
from _dates_data import DATES
from _honey_bee_data import GIRLS
from _recruit import sound
from _travel import CHOICE, beside

from ff7 import asm
from ff7.camera import Camera
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

MAX = 20
WRONG = (5, 246)                       # temp: an answer this date was wrong
TIERS = (10, 20)                       # affection where the second / third dates start
# date fields: (place, group) -> new field name (free maplist names, docs/dates_plan.md)
GROUPS = [["Tifa"]]
FIELDS = {("gondola", 0): "blackbga", ("capsule", 0): "blackbgf", ("tower", 0): "blackbgg"}
BASE = {"gondola": "bwhlin", "capsule": "rcktin7", "tower": "nivl_e1"}
PLACES = ("gondola", "capsule", "tower")
PLACE_NAMES = {"gondola": "The Gold Saucer gondola.", "capsule": "The space capsule.",
               "tower": "The water tower in Nibelheim."}
# seats: (x, y, tri, dir) for Cloud and her (tri None: found; dir None: facing each other)
SEATS = {
    "gondola": {"cloud": (-5175, -6999, 4, 0x80), "girl": (-5150, -6903, 5, 0x00)},   # the original date's XYZIs
    "capsule": {"cloud": (-45, 209, None, None), "girl": (45, 209, None, None)},       # floor before the benches
    # nivl_e1 (the promise flashback): where young Cloud and Tifa end up sitting on the rim
    # (cloud MOVE to (547,-415), TURNGEN 0x18; tifa7 MOVE to (517,-451), TURNGEN 0xE8)
    "tower": {"cloud": (547, -415, None, 0x18), "girl": (517, -451, None, 0xE8)},
}
# sitting: "bench" = the gondola models' own sitting anims (feet on the floor);
# "ledge" = ours (_ledge): hips on the floor, thighs level, shins hanging over the edge
SIT_KIND = {"gondola": "bench", "capsule": "bench", "tower": "ledge"}
CLOUD_SIT = {"bench": "GDAB.chi", "ledge": "ZDLC.tor"}       # bwhlin cloud DFANM 03 / ours
GIRL_SIT = {"Tifa": {"bench": "GDEE.chi", "ledge": "ZDLT.tor"}}   # bwhlin tifa DFANM 03 / ours
# ledge poses to build: anim -> (skeleton .hrc, standing anim it starts from)
LEDGE = {"ZDLC.tor": ("aaaa.hrc", "acfe.a"), "ZDLT.tor": ("aagb.hrc", "abcd.a")}
LEDGE_ARMS, LEDGE_SEAT = 25, 1.5       # arms this far forward (hands to the thighs); hip joints this far up
GIRL_MODEL = {"Tifa": "main_n_tifa.char"}   # her model entry in both base fields (name suffix)
RETURN_GAP = 40                        # back beside her: this far from her spot


def _dir_to(dx, dy):
    """DIR facing field vector (dx, dy): direction d faces (sin a, -cos a), a = d*2pi/256."""
    return round(math.atan2(dx, -dy) * 128 / math.pi) % 256


def _clear_texts(sec):
    """Drop every text (before adding the new ones: ids start at 0 again)."""
    import struct
    strings_end = min(sec.akao_offsets) if sec.akao_offsets else len(sec.tail)
    sec.tail = struct.pack("<H", 0) + sec.tail[strings_end:]
    sec.akao_offsets = [o - strings_end + 2 for o in sec.akao_offsets]


def _blank(sec, scripts):
    """Drop every op; entity e gets scripts[e] ({slot: ops}, each ending in RET),
    other slots an empty RET."""
    empty = Op(b"\x00")
    sec.ops = [empty]
    for e in range(len(sec.entity_names)):
        entry = [empty] * 32
        for k, ops in sorted(scripts.get(e, {}).items()):
            assert ops[-1].op == 0x00, (e, k)
            entry[k] = ops[0]
            sec.ops.extend(ops)
        sec.entry[e] = entry


def _hb():
    from importlib import import_module
    return import_module("620_honey_bee")


def _return_spot(ctx, g):
    """(x, y, tri, dir) beside her in her world field, facing her."""
    mesh = Walkmesh(ctx.field(g["field"]).section("walkmesh"))
    x, y = g["at"]
    tri = mesh.find(x, y)
    bx, by, _, bt = beside(ctx, g["field"], x, y, tri, RETURN_GAP)
    return bx, by, bt, _dir_to(x - bx, y - by)


def _date(sec, ctx, place, i, g, d):
    """The date's ops for girl i (in the director's main), ending in the MAPJUMP back."""
    hb = _hb()
    name, aff = g["name"], HB_AFFECTION[i]
    her = lambda t: d.get("speaker", name) + "\n" + t
    out = asm.nop()
    ops = [asm.setbyte(WRONG, 0)]
    tier_at = [asm.nop() for _ in d["tiers"]]
    not3, not2 = asm.nop(), asm.nop()
    ops += [asm.if_byte(aff, ">=", TIERS[1], not3), asm.goto(tier_at[2]), not3,     # 20: third
            asm.if_byte(aff, ">=", TIERS[0], not2), asm.goto(tier_at[1]), not2,     # 10-19: second
            asm.goto(tier_at[0])]
    for t, tier in enumerate(d["tiers"]):
        block = []
        block += hb._say(sec, her(tier["open"]))
        for st in tier["steps"]:
            if st[0] == "G":
                block += hb._say(sec, her(st[1]))
            elif st[0] == "C":
                block += hb._say(sec, "{CLOUD}\n" + st[1])
            else:
                _, q, answers, right, yes, no = st
                ask, first = hb._ask(sec, her(q), answers)
                wrong, done, ok = asm.nop(), asm.nop(), asm.nop()
                block += ask + [asm.if_byte(CHOICE, "==", first + right, wrong),
                                Op(bytes([0x85, aff[0] << 4, aff[1], 1])),            # PLUS 1
                                asm.if_byte(aff, ">", MAX, ok), asm.setbyte(aff, MAX), ok,
                                sound(0x168)] + hb._say(sec, her(yes)) + [asm.goto(done), wrong,
                                asm.setbyte(WRONG, 1)] + hb._say(sec, her(no)) + [done]
        if t == 2:                                   # the choice: every answer this date right
            plain = asm.nop()
            block += [asm.if_byte(WRONG, "==", 0, plain)] + hb._say(sec, her(d["lead"]))
            ask, first = hb._ask(sec, her("…"), ["Give into your desires.", "Leave it be."])
            leave = asm.nop()
            block += ask + [asm.if_byte(CHOICE, "==", first, leave)]
            block += hb._say(sec, d["desire"]) + [asm.goto(out), leave] + hb._say(sec, her(d["leave"]))
            block += [asm.goto(out), plain]
        block += hb._say(sec, her(tier["close"])) + [asm.goto(out)]
        ops += [tier_at[t]] + block
    rx, ry, rt, rd = _return_spot(ctx, g)
    ops += [out, asm.setbyte(DATE_GIRL, 0), hb._uc(0), hb._menu(0),
            asm.mapjump(ctx.maplist.index(g["field"]), rx, ry, rt, rd), asm.ret()]
    return ops


def _field(ctx, place, group, names):
    hb = _hb()
    name = FIELDS[(place, group)]
    f = ctx.new_field(name, ctx.field(BASE[place]).build())
    sec = Script.parse(f.sections[0])
    _clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    loader = ModelLoader(f.section("models"))
    model_names = [ModelLoader.name(e) for e in loader.models]
    # every entity's CHAR (model index) in entity order
    chars = {}
    for e in range(len(sec.entity_names)):
        op = next((o for o in sec.script_ops(e, 0) if o.op == 0xA1), None)
        if op is not None:
            chars[e] = op.raw[1]
    assert sorted(chars.values()) == list(range(len(loader.models))), chars
    model_ent = {m: e for e, m in chars.items()}
    assert model_names[0].endswith("main_n_cloud.char"), model_names[0]

    def seat(who):
        x, y, tri, _ = SEATS[place][who]
        if tri is None:
            tri = mesh.find(x, y)
        assert tri is not None and mesh.contains(tri, x, y), (name, who, x, y)
        return x, y, mesh.height(tri, x, y), tri

    def sit_anim(m, anim):
        anims = ModelLoader.anims(loader.models[m])
        if anim not in anims:
            loader.models[m] = ModelLoader.with_anims(loader.models[m], [anim])
            anims = ModelLoader.anims(loader.models[m])
        return anims.index(anim)

    cs, gs = seat("cloud"), seat("girl")
    cdir, gdir = _dir_to(gs[0] - cs[0], gs[1] - cs[1]), _dir_to(cs[0] - gs[0], cs[1] - gs[1])
    cdir = SEATS[place]["cloud"][3] if SEATS[place]["cloud"][3] is not None else cdir
    gdir = SEATS[place]["girl"][3] if SEATS[place]["girl"][3] is not None else gdir
    kind = SIT_KIND[place]
    scripts = {}
    ca = sit_anim(0, CLOUD_SIT[kind])
    scripts[model_ent[0]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), hb._xyzi(*cs), Op(bytes([0xB3, 0, cdir])),
                                 Op(bytes([0xA2, ca, 1])), Op(bytes([0xAE, ca, 1])), asm.ret(), asm.ret()]}
    girl_models = {}
    for gname in names:
        i = next(k for k, g in enumerate(GIRLS) if g["name"] == gname)
        m = next(k for k, n in enumerate(model_names) if n.endswith(GIRL_MODEL[gname]))
        girl_models[m] = i
        ga = sit_anim(m, GIRL_SIT[gname][kind])
        hide, end = asm.nop(), asm.nop()
        scripts[model_ent[m]] = {0: [Op(bytes([0xA1, m])), asm.if_byte(DATE_GIRL, "==", i + 1, hide),
                                     hb._xyzi(*gs), Op(bytes([0xB3, 0, gdir])), Op(bytes([0xA2, ga, 1])),
                                     Op(bytes([0xAE, ga, 1])), hb._visi(1), asm.goto(end), hide, hb._visi(0),
                                     end, asm.ret(), asm.ret()]}
    for e, m in chars.items():                   # everyone else: hidden
        if e not in scripts:
            scripts[e] = {0: [Op(bytes([0xA1, m])), hb._visi(0), asm.ret(), asm.ret()]}
    assert 0 not in chars, "entity 0 has a model"
    init = [asm.ret()]
    if place == "capsule":                       # space through the window
        init = [Op(b"\xE0\x00\x01\x00"), Op(b"\xE1\x00\x02\x00"), asm.ret()]   # BGON 1, BGOFF 2
    main = [hb._uc(1), hb._menu(1)]
    for gname in names:
        i = next(k for k, g in enumerate(GIRLS) if g["name"] == gname)
        d = DATES[gname]
        nxt = asm.nop()
        main += [asm.if_byte(DATE_GIRL, "==", i + 1, nxt),
                 Op(bytes([0xF2, 0, 0, 0, 0x10, d["music"][place]]) + bytes(8)), hb._w(20)]
        main += _date(sec, ctx, place, i, GIRLS[i], d) + [nxt]
    # no girl (e.g. debug travel): back to the first girl's spot
    g0 = GIRLS[next(k for k, g in enumerate(GIRLS) if g["name"] == names[0])]
    rx, ry, rt, rd = _return_spot(ctx, g0)
    main += [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(g0["field"]), rx, ry, rt, rd), asm.ret()]
    scripts[0] = {0: init + main}
    _blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    return cs


def _offer(ctx, i, g, arrive, group):
    """Her world talk: "Just chat." / "Ask her on a date." first."""
    hb = _hb()
    field = g["field"]
    sec = Script.parse(ctx.field(field).sections[0])
    ent = sec.entity_index(g.get("reuse") or "hb%02d" % i)
    talk = sec.script_ops(ent, 1)
    assert [o.op for o in talk[:3]] == [0x33, 0x35, 0x24], talk[:3]     # UC 01, PTURA, WAIT
    rest = talk[3]
    d = DATES[g["name"]]
    her = lambda t: d.get("speaker", g["name"]) + "\n" + t
    ops = []
    ask, first = hb._ask(sec, her(d["greet"]), ["Just chat.", "Ask her on a date."])
    ops += ask + [asm.if_byte(CHOICE, "!=", first, rest)]                # chat: the usual talk
    ask, first = hb._ask(sec, her(d["where"]), [PLACE_NAMES[p] for p in PLACES] + ["Never mind."])
    ops += ask
    never = asm.nop()
    for k, p in enumerate(PLACES):
        nxt = asm.nop()
        x, y, z, tri = arrive[p]
        ops += [asm.if_byte(CHOICE, "==", first + k, nxt), asm.setbyte(DATE_GIRL, i + 1), hb._uc(0),
                asm.mapjump(ctx.maplist.index(FIELDS[(p, group)]), x, y, tri, 0), asm.ret(), nxt]
    ops += [never, hb._uc(0), asm.ret()]
    sec.insert_after(talk[2], ops)
    ctx.field(field).sections[0] = sec.build()


def _ledge(ctx, name, hrc, stand):
    """Sitting on a ledge (`name`.a): from the standing pose, each thigh swung forward to
    level (the knee bent back 90, so the shin hangs straight down and the foot stays as it
    was), the arms LEDGE_ARMS forward, the hip joints LEDGE_SEAT above the root's floor."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]                    # y down
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    ends = lambda W, r=root: fa.forward(sk, rr, r, fa.local_rotations(sk, rr, W))
    F = ends(W)
    fwd = [0.0, 0.0, -1.0]                           # field models face -z (the toes splay out: not them)
    side = [1.0, 0.0, 0.0]
    ahead = lambda p: p[0] * fwd[0] + p[2] * fwd[2]

    def turned(W, bones, angle, test):
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(side, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(ends(M)):
                return M
        raise AssertionError((name, bones))
    for s in "lr":
        knee0 = F[I(s + "_femur")][2]
        W = turned(W, {s + "_femur", s + "_tibia", s + "_foot"}, 90,
                   lambda E: ahead(E[I(s + "_femur")][2]) > ahead(knee0) + 1)          # thigh forward to level
        k = ends(W)[I(s + "_femur")][2]
        W = turned(W, {s + "_tibia", s + "_foot"}, 90,
                   lambda E: E[I(s + "_tibia")][2][1] > k[1] + 1)                       # shin back down (y down)
        hand0 = ends(W)[I(s + "_hand")][2]
        W = turned(W, {s + "_uparm", s + "_foarm", s + "_hand"}, LEDGE_ARMS,
                   lambda E: ahead(E[I(s + "_hand")][2]) > ahead(hand0) + 0.5)
    E = ends(W)
    for s in "lr":
        thigh = [E[I(s + "_femur")][2][k] - E[I(s + "_femur")][1][k] for k in range(3)]
        assert abs(thigh[1]) < 0.2 * math.hypot(*thigh) and abs(thigh[0]) < 0.5 * math.hypot(*thigh), \
            (name, s, thigh)                                                            # level, ahead
    hip_y = max(E[I(s + "_femur")][1][1] for s in "lr")
    root = [root[0], root[1] - hip_y - LEDGE_SEAT, root[2]]                             # hips just above the floor
    base.frames = [(rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, W))]
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


def apply(ctx):
    for anim, (hrc, stand) in LEDGE.items():
        _ledge(ctx, anim, hrc, stand)
    for group, names in enumerate(GROUPS):
        arrive = {p: _field(ctx, p, group, names) for p in PLACES}
        for gname in names:
            i = next(k for k, g in enumerate(GIRLS) if g["name"] == gname)
            _offer(ctx, i, GIRLS[i], arrive, group)

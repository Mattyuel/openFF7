"""A customer abusing a Honey Bee girl outside the inn (user's design).

Each time you enter mrkt3 (Wall Market by the Honey Bee Inn) with at least one
girl hired, there is a 1 in 5 chance (`CHANCE`) that, in the lower right
corner, a customer (one of four `THUGS`, picked at random) stands over one of
your hired girls (picked at random, never `SPARED`), slapping her while she
cowers on the ground. Talk to him: "Leave her alone!" / "Walk away.". The
soldier and the mohawk punk fight (a Grunt / three of Corneo's lackeys; no
escape, no game over: a loss just ends it, BTMD2 as Corel's Cid fight); the
drunk sailor hands over a Speed Drink and the grey-suited manager a 500 gil
bribe. Done: her affection +1 (capped 20), her thanks, then the screen fades
out, both are gone, and it fades back in.

The girl is the Honey Bee dancer (the inn's uniform: the girls' own world
models can't all fit in one field), named in the lines. Her cowering pose
(ZCWA: sitting on the floor, knees drawn up, leaning in, arms up over her head,
trembling) and each thug's slap (ZTS<k>: leaning in, the right arm bent once
and swung at the shoulder onto her head, 660's old `_spank_arm`, since removed) are built here;
each thug is placed where his hand lands on her head.

Models: mrkt3 was at 14. Three thugs take over the hidden party copies
(aerith / tifa / cid: Cloud always leads, so they are never shown) and their
model slots; the fourth and the girl are new entities and models (16). Madam M (600's quest
giver) moved out of the corner to make room (`_quest_data`).
"""
import math
import struct

from _config import HB_AFFECTION, HB_HIRED
from _honey_bee_data import GIRLS
from _recruit import sound
from _travel import CHOICE
from _travel import screen_step as _travel_screen_step

from ff7 import asm
from ff7 import fieldanim as fa
from ff7.camera import Camera, facing_screen
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import decode, encode
from ff7.walkmesh import Walkmesh

FIELD = "mrkt3"
CHANCE = 5                                      # 1 in CHANCE entries
SPARED = {"Tifa", "Aerith", "Elena", "Scarlet"}  # (user) never the girl in this scene
# (user) the four customers, one picked at random each time; all on Cloud's skeleton layout (AAFE /
# ACFE anims), so one slap recipe fits each. Two fight ("battle": formation, no escape, no game
# over: a loss just ends it, BTMD2 as Corel's Cid fight); two give you something instead.
THUGS = [
    dict(model=("blackbg2", 9), who="Sailor",          # shinra_crew: white sailor's uniform
         taunt="“Hic… shtay outta thish, pal… me an'\n %s are… are havin' a convershation…”",
         outcome=("item", "Speed Drink", 1),
         lines=["“Whoa, whoa… easy, buddy… I'm goin'…\n The room's shpinnin' anyway…”",
                "“Here… *hic*… take thish. Shpeed Drink.\n Makesh ya fasht. Faster'n me, anyway…”"]),
    dict(model=("blin66_6", 6), who="Soldier",         # shinra_hei: Shinra infantry
         taunt="“Move along, civilian. Me and %s\n are having a private discussion.”",
         outcome=("battle", 28),                        # a Grunt (level 7)
         lines=["“You're interfering with a Shinra\n officer. That's a mistake.”"],
         lost="“Hmph. Know your place, civilian.”"),
    dict(model=("jail2", 6), who="Punk",               # korel_bou202: the mohawk
         taunt="“Get lost, spiky! %s owes me,\n and I'm collectin'!”",
         outcome=("battle", 384),                       # three of Corneo's lackeys (level 8: the only lackey fight)
         lines=["“Oh, you want some? BOYS!\n Get over here!”"],
         lost="“Ha! Stay down, hero.”"),
    dict(model=("blackbg1", 3), who="Manager",         # shinra_ippan_1: grey suit
         taunt="“Ahem. This is a private matter between\n myself and %s. Run along.”",
         outcome=("gil", 500),
         lines=["“Now, now, let's not make a scene.\n My wife can't hear about this…”",
                "“Here. 500 gil. You never saw me.\n Understood?”"]),
]
TAKEN = ["earith", "tifa", "cid", None]         # hidden party copies the first three take over; the 4th: a new entity
DANCER = ("onna_52", 1)                         # market_dancer, BADD.HRC
GIRL_AT = (-180, -168)                          # (user, since) 4 body widths left, 2 steps down: the pillar
                                                # left of the door blocks those exact spots, so the nearest floor (screen ~(-30,61))
GIRL_RIGHT = 2                                  # (user, since) she is this many paces right of GIRL_AT
THUG_GAP = 40                                   # (user: the girl halfway closer) him this far from her (screen ~(-25,54))
THUG_STEP = (6, 40)                             # him THUG_GAP from her this way
GIRL_FRAMES = 8                                 # her tremble loop
SLAP_SOUND, SLAP_PAUSE = 0x76, 45               # the slap; frames between slaps
EV, GI, TI, R, TRY = (5, 160), (5, 161), (5, 162), (5, 163), (5, 164)   # event on, girl, thug, scratch
RES = (6, 166)                                  # battle result (BTRLD): bit 0 set = lost
MAX = 20
DEBUG_FLAGS = (1, 213)                          # debug builds: bit 1 = this scene every time (debug menu)
UNIT = 3.41                                     # field units per model unit at entry scale 512


def _hb():
    from importlib import import_module
    return import_module("620_honey_bee")


def _dates():
    from importlib import import_module
    return import_module("660_dates")


def _turned(fa, sk, rr, W, root, bones, axis, angle, test):
    """W with `bones` turned `angle` about `axis` (world), the sense passing test(old ends, new ends)."""
    names = [b[0] for b in sk]
    ends = lambda M: {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, list(root),
                                                                           fa.local_rotations(sk, rr, M)))}
    e0 = ends(W)
    for sg in (1, -1):
        M = [fa._mul(fa.axis_angle(axis, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
        if test(e0, ends(M)):
            return M
    raise AssertionError((sorted(bones), angle))


# her pose: from the dancer's stand (DXID), thighs swung COWER_THIGH up and forward, shins turned back
# down until the ankles reach the floor (knees drawn up), the upper body leaned in, head ducked, both arms raised over her head
# and the forearms turned in; the pelvis on the floor; a small tremble (the upper body turning)
COWER_THIGH, COWER_LEAN, COWER_HEAD, COWER_TREMBLE = 115, 25, 25, 3
COWER_UPARM = (0.3, 0.15, -1.0)               # (inward, up (y down), forward (-z)), model space
COWER_FOARM = (0.5, -0.8, -1.0)
PELVIS = 1.2                                    # the root this far above her floor (the seat)


def _cower(ctx):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("badd.hrc").decode("latin-1"))
    names = [b[0] for b in sk]
    base = fa.Anim(ctx.char_file("dxid.a"))
    rr, rp, rots = base.frames[0]
    r0 = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, r0, rots)]
    ends = lambda M, r=r0: {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, list(r),
                                                                                 fa.local_rotations(sk, rr, M)))}
    floor = max(ends(W)[s + n][1] for s in "lr" for n in ("_tibia", "_foot"))
    side, up = [1.0, 0.0, 0.0], [0.0, -1.0, 0.0]
    T = lambda W, bones, axis, a, test: _turned(fa, sk, rr, W, r0, bones, axis, a, test)
    legs = {s + n for s in "lr" for n in ("_hip", "_femur", "_tibia", "_foot")}
    upper = set(names) - legs
    root = [r0[0], floor - PELVIS, r0[2]]                                                     # sitting on the floor
    for s in "lr":
        W = T(W, {s + "_femur", s + "_tibia", s + "_foot"}, side, COWER_THIGH,
              lambda a, b: b[s + "_femur"][2] < a[s + "_femur"][2] - 1)                     # knee up, forward (-z)
        # the shin turned back down until the ankle is on the floor (bisection on the angle)
        turn = lambda a: [fa._mul(fa.axis_angle(side, a), m) if names[i] in (s + "_tibia", s + "_foot")
                          else m for i, m in enumerate(W)]
        sense = 1 if ends(turn(10), root)[s + "_tibia"][1] > ends(W, root)[s + "_tibia"][1] else -1   # + = ankle down
        shin = lambda a: [fa._mul(fa.axis_angle(side, sense * a), m) if names[i] in (s + "_tibia", s + "_foot")
                          else m for i, m in enumerate(W)]
        miss = lambda a: ends(shin(a), root)[s + "_tibia"][1] - floor
        hi = next((float(a) for a in range(0, 181, 5) if miss(a) >= 0), None)    # first angle that reaches
        assert hi is not None and miss(0) < 0, (s, miss(0), max(miss(a) for a in range(0, 181, 5)))
        lo = hi - 5
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if miss(mid) < 0 else (lo, mid)
        W = shin(lo)
    W = T(W, upper, side, COWER_LEAN, lambda a, b: b["head"][2] < a["head"][2] - 0.5)       # leaning in
    W = T(W, {"head"}, side, COWER_HEAD, lambda a, b: b["head"][1] > a["head"][1])          # head ducked
    # (user, since: the arms bent backwards) each upper arm forward and a little up, the forearm
    # up and in, so the hands shield her face from the front
    for s, out in (("l", 1), ("r", -1)):
        for n, d in (("_uparm", COWER_UPARM), ("_foarm", COWER_FOARM), ("_hand", COWER_FOARM)):
            i = names.index(s + n)
            W[i] = fa._mul(_dates()._align(fa, fa._vec(W[i], [0, 0, -1]), [-out * d[0], d[1], d[2]]), W[i])
    E = ends(W, root)
    for s in "lr":                                                                            # feet on the floor
        assert abs(E[s + "_tibia"][1] - floor) < 0.1, (s, E[s + "_tibia"], floor)
    assert E["head"][1] < root[1], "head above the seat"
    for s in "lr":                                                                            # hands before her face
        assert E[s + "_hand"][2] < E["head"][2] - 1, (s, E[s + "_hand"], E["head"])
        assert abs(E[s + "_hand"][1] - E["head"][1]) < 4, (s, E[s + "_hand"], E["head"])
    frames = []
    for t in range(GIRL_FRAMES):
        a = COWER_TREMBLE * math.sin(2 * math.pi * t / GIRL_FRAMES)
        Wt = [fa._mul(fa.axis_angle(up, a), m) if names[i] in upper else m for i, m in enumerate(W)]
        frames.append((rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file("zcwa.a", base.build())
    return {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W)))}


# his slap (user): the right arm raised SLAP_RAISE out to the side, swung SLAP_OUT outwards (back)
# over SLAP_WIND frames, then quickly SLAP_IN inwards (across, in front) in SLAP_STRIKE frames (the
# hit: SOUND at THUG_HIT), held, and back down to his side; the elbow bent SLAP_ELBOW throughout
SLAP_RAISE, SLAP_OUT, SLAP_IN, SLAP_ELBOW = 30, 50, 60, 25
SLAP_WIND, SLAP_STRIKE, SLAP_HOLD, SLAP_BACK = 8, 3, 3, 6


def _slap(ctx, hrc, name):
    """`name`.a on skeleton `hrc` (Cloud's layout), from his stand (AAFE frame 0): see SLAP_*."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file("zcte.a"))                # a container on Cloud's layout (frames replaced)
    rr, rp, rots = fa.Anim(ctx.char_file("aafe.a")).frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    hand = lambda M: fa.forward(sk, rr, root, fa.local_rotations(sk, rr, M))[I("r_hand")][2]
    arm = {"r_uparm", "r_foarm", "r_hand"}
    side, fwd_axis, up = [1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]
    T = lambda W, bones, axis, a, test: _turned(fa, sk, rr, W, root, bones, axis, a, test)
    W = T(W, {"r_foarm", "r_hand"}, side, SLAP_ELBOW, lambda a, b: b["r_hand"][2] < a["r_hand"][2])   # elbow bent
    h0 = hand(W)
    raise_sense = 1 if hand([fa._mul(fa.axis_angle(fwd_axis, 10), m) if names[i] in arm else m
                             for i, m in enumerate(W)])[0] < h0[0] else -1       # + = out to his right (-x), up
    in_sense = 1 if hand([fa._mul(fa.axis_angle(up, 10), m) if names[i] in arm else m
                          for i, m in enumerate(W)])[2] < h0[2] else -1          # + = forward / in
    ease = lambda u: (1 - math.cos(math.pi * max(0.0, min(1.0, u)))) / 2
    keys = []                                                                    # (raise, swing) per frame
    for t in range(SLAP_WIND):
        u = ease((t + 1) / SLAP_WIND)
        keys.append((SLAP_RAISE * u, -SLAP_OUT * u))
    for t in range(SLAP_STRIKE):
        u = (t + 1) / SLAP_STRIKE                                                # fast: linear
        keys.append((SLAP_RAISE, -SLAP_OUT + (SLAP_OUT + SLAP_IN) * u))
    keys += [(SLAP_RAISE, SLAP_IN)] * SLAP_HOLD
    for t in range(SLAP_BACK):
        u = 1 - ease((t + 1) / SLAP_BACK)
        keys.append((SLAP_RAISE * u, SLAP_IN * u))
    keys = [(0.0, 0.0)] + keys
    frames = []
    for r_, sw in keys:
        R = fa._mul(fa.axis_angle(up, in_sense * sw), fa.axis_angle(fwd_axis, raise_sense * r_))
        Wt = [fa._mul(R, m) if names[i] in arm else m for i, m in enumerate(W)]
        frames.append((rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file(name.lower() + ".a", base.build())
    return len(frames), 1 + SLAP_WIND + SLAP_STRIKE - 1                          # frames, the hit frame


def _text(sec, t):
    return sec.add_string(encode(t))


def apply(ctx):
    hb, dt = _hb(), _dates()
    f = ctx.field(FIELD)
    sec = Script.parse(f.sections[0])
    loader = ModelLoader(f.section("models"))
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    # her spot and pose
    _cower(ctx)
    # (user, since) she GIRL_RIGHT paces (25 each) right on screen from GIRL_AT; he stays where he was
    gx, gy, gz, gt = _travel_screen_step(ctx, FIELD, *GIRL_AT, (1, 0), 25 * GIRL_RIGHT)
    tdir = _dates()._dir_to(-THUG_STEP[0], -THUG_STEP[1])           # he faces her
    # (her legs pointed at him tangled with his) she sits side-on to him, turned the way that faces
    # the camera more
    def down(d):
        a_ = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy, gz), cam.project(gx + 20 * math.sin(a_), gy - 20 * math.cos(a_), gz)
        return p1[1] - p0[1]
    gdir = max(((tdir + 64) % 256, (tdir - 64) % 256), key=down)
    dancer = ModelLoader(ctx.field(DANCER[0]).section("models")).models[DANCER[1]]
    # each thug: his model (Cloud's height in this field, user) in a taken-over slot (or a new one), standing
    # THUG_GAP behind her along his facing (up the screen), facing her
    a = tdir * 2 * math.pi / 256
    fwd = (math.sin(a), -math.cos(a))
    cloud = loader.models[0]
    tall = lambda e: fa.height(ctx.char_file(ModelLoader.hrc(e).lower()).decode("latin-1"),
                               ctx.char_file(ModelLoader.anims(e)[0].split(".")[0].lower() + ".a"))
    cloud_h = tall(cloud) * ModelLoader.entry_scale(cloud)
    thugs = []
    for k, (spec, ent_name) in enumerate(zip(THUGS, TAKEN)):
        dfield, di = spec["model"]
        if ent_name is None:                                        # a new entity and model (appended)
            ent, m, old_char = None, len(loader.models), None
            loader.models.append(None)
        else:
            ent = sec.entity_index(ent_name)
            init = sec.script_ops(ent, 0)
            assert init[0].op == 0xA1 and any(o.op == 0xA0 for o in init), (ent_name, [o.raw.hex() for o in init])  # CHAR, PC
            m, old_char = init[0].raw[1], init[0]
        entry = ModelLoader(ctx.field(dfield).section("models")).models[di]
        entry = ModelLoader.with_scale(entry, round(cloud_h / tall(entry)))
        anim = "ZTS" + "ABCD"[k]
        nframes, hit = _slap(ctx, ModelLoader.hrc(entry), anim)
        placed = None
        for dist in list(range(THUG_GAP, THUG_GAP + 30, 2)) + list(range(THUG_GAP - 2, 10, -2)):
            n = math.hypot(*THUG_STEP)
            tx, ty = round(GIRL_AT[0] + THUG_STEP[0] / n * dist), round(GIRL_AT[1] + THUG_STEP[1] / n * dist)
            tt = mesh.find(tx, ty)
            if tt is not None:
                placed = (tx, ty, mesh.height(tt, tx, ty), tt)
                break
        assert placed is not None, (spec["who"],)
        loader.models[m] = ModelLoader.with_anims(entry, [anim + ".tor"])
        slap = len(ModelLoader.anims(loader.models[m])) - 1
        thugs.append(dict(ent=ent, model=m, at=placed, slap=slap, idle=0, old_char=old_char, spec=spec,
                          frames=nframes, hit=hit))
    # her model: a new entity at the end (the next model index)
    gm = len(loader.models)
    loader.models.append(ModelLoader.with_anims(ModelLoader.with_scale(dancer, ModelLoader.entry_scale(dancer)),
                                                ["ZCWA.tor"]))
    cower = len(ModelLoader.anims(loader.models[gm])) - 1
    assert len(loader.models) <= 16, len(loader.models)
    f.set_section("models", loader.build())

    # ---- scripts -------------------------------------------------------------------------
    hidden = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01"), hb._visi(0)]          # TLKON 01, SOLID 01, VISI 00
    shown = lambda: [Op(b"\x7E\x00"), Op(b"\xC7\x00"), hb._visi(1)]
    by_girl = lambda make: _chain(GI, [make(i, g) for i, g in enumerate(GIRLS)])
    girl_ent = len(sec.entity_names) + sum(1 for t in thugs if t["ent"] is None)   # after any new thug entity
    k2 = ctx.kernel2()
    item_id = lambda name: next(i for i in range(128) if decode(k2.get(10, i)).strip() == name)

    def talk(spec):
        who = spec["who"]
        say = lambda t: hb._say(sec, t)
        end, walk, won = asm.nop(), asm.nop(), asm.nop()
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)]

        def ask(i, g):
            a_, first = hb._ask(sec, who + "\n" + spec["taunt"] % g["name"], ["Leave her alone!", "Walk away."])
            return a_ + [asm.if_byte(CHOICE, "==", first, walk)]   # 1st interferes, 2nd walks (was swapped)
        ops += by_girl(ask)
        for line in spec["lines"]:
            ops += say(who + "\n" + line)
        kind = spec["outcome"][0]
        if kind == "battle":
            ops += [Op(bytes([0x22, 0x08, 0x00, 0x01, 0x00])),                  # BTMD2: no escape, no game over
                    asm.battle(spec["outcome"][1]), Op(bytes([0x23, RES[0], RES[1]])),   # BTRLD
                    asm.if_word(RES, "&", 1, won)]                              # bit 0 clear: won
            ops += say(who + "\n" + spec["lost"]) + [asm.goto(end)]
        elif kind == "item":
            _, name, n = spec["outcome"]
            ops += [asm.add_item(item_id(name), n), sound(0x168)] + say("Received “%s”!" % name)
        else:                                                                    # gil
            ops += [Op(bytes([0x39, 0x00]) + struct.pack("<I", spec["outcome"][1])), sound(0x168)] + \
                say("Received %d gil!" % spec["outcome"][1])

        def thanks(i, g):
            aff = HB_AFFECTION[i]
            ok = asm.nop()
            return [Op(bytes([0x85, aff[0] << 4, aff[1], 1])), asm.if_byte(aff, ">", MAX, ok), asm.setbyte(aff, MAX), ok,
                    sound(0x168)] + say("%s\n“Cloud…! Thank you. I don't know\n what he'd have done…”" % g["name"])
        ops += [won] + by_girl(thanks)
        ops += [Op(hb.FADE_OUT), Op(b"\x6C"), asm.setbyte(EV, 0)] + hidden() + \
               [hb._req(girl_ent, 3), hb._w(15), Op(hb.FADE_IN), Op(b"\x6C"), asm.goto(end)]
        ops += [walk] + say(who + "\n“That's right. Keep walking.”")
        return ops + [end, hb._uc(0), asm.ret()]

    for k, th in enumerate(thugs):
        x, y, z, t = th["at"]
        loop, idle_top, quiet = hb._w(1), asm.nop(), asm.nop()
        # main: shown while this event has picked him; then a slap (the sound at the hit), a pause, again
        main = [asm.if_byte(EV, "==", 1, quiet), asm.if_byte(TI, "==", k, quiet)] + shown() + \
               [Op(bytes([0xA2, th["idle"], 1])), Op(bytes([0xAE, th["idle"], 1])),
                loop, asm.if_byte(EV, "==", 1, quiet),
                Op(bytes([0xBC, th["slap"], 0, th["hit"], 1])), Op(b"\xAC"),
                sound(SLAP_SOUND), Op(bytes([0xBC, th["slap"], th["hit"], th["frames"] - 1, 1])), Op(b"\xAC"),
                Op(bytes([0xA2, th["idle"], 1])), Op(bytes([0xAE, th["idle"], 1])), hb._w(SLAP_PAUSE),
                asm.goto_back(loop),
                quiet, idle_top, hb._w(30), asm.goto_back(idle_top), asm.ret()]
        # (user, since) turned 45 to his left from facing her: facing down-right on screen
        sdir = facing_screen(cam, x, y, z, (1, 1))
        init = [Op(bytes([0xA1, th["model"]])), hb._xyzi(x, y, z, t), Op(bytes([0xB3, 0, sdir])),
                Op(bytes([0xC5, 0x00, 0x46]))] + hidden() + [asm.ret()]
        body = talk(th["spec"])
        if th["ent"] is None:
            sec.add_entity("hbthug%d" % k, {0: init + main, 1: body})
            continue
        sec.replace(th["old_char"], [asm.ret()])          # the old init (no longer an entry): no second CHAR
        empty = asm.ret()
        sec.ops.extend([empty] + init + main + body)
        sec.entry[th["ent"]] = [empty] * 32
        sec.entry[th["ent"]][0], sec.entry[th["ent"]][1] = init[0], body[0]

    # the girl
    gloop, gquiet = hb._w(30), asm.nop()
    ginit = [Op(bytes([0xA1, gm])), hb._xyzi(gx, gy, gz, gt), Op(bytes([0xB3, 0, gdir])),
             Op(bytes([0xC5, 0x00, 0x46])), Op(bytes([0xA2, cower, 1])), Op(bytes([0xAE, cower, 1]))] + hidden() + \
        [asm.ret(), asm.if_byte(EV, "==", 1, gquiet)] + shown() + [gquiet, gloop, asm.goto_back(gloop), asm.ret()]
    gtalk = [hb._uc(1)] + hb._say(sec, "(She's shaking too hard to speak.)") + [hb._uc(0), asm.ret()]
    assert sec.add_entity("hbvictim", {0: ginit, 1: gtalk, 3: hidden() + [asm.ret()]}) == girl_ent
    # the director: the roll, before any main runs (an init); EV stays 0 unless it all comes up
    done, loop, found, always = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    roll = [asm.setbyte(EV, 0), asm.setbyte(TRY, 0),
            asm.if_byte(DEBUG_FLAGS, "bit_off", 1, always),                                   # debug: every time
            Op(bytes([0x99, R[0], R[1]])), Op(bytes([0x8D, R[0] << 4, R[1], CHANCE])),         # RANDOM, MOD
            asm.if_byte(R, "==", 0, done), always, loop, Op(bytes([0x95, TRY[0], TRY[1]])),
            asm.if_byte(TRY, "<=", 60, done),                                                 # nobody hired: give up
            Op(bytes([0x99, GI[0], GI[1]])), Op(bytes([0x8D, GI[0] << 4, GI[1], len(GIRLS)]))]
    assert SPARED <= {g["name"] for g in GIRLS}, SPARED
    for i in range(len(GIRLS)):
        if GIRLS[i]["name"] in SPARED:
            continue                                # never picked: GI == i falls through to the retry
        nxt = asm.nop()
        var, bit = (HB_HIRED[0], HB_HIRED[1] + i // 8), i % 8
        roll += [asm.if_byte(GI, "==", i, nxt), asm.if_byte(var, "bit_on", bit, nxt), asm.goto(found), nxt]
    roll += [asm.goto_back(loop), found, Op(bytes([0x99, TI[0], TI[1]])), Op(bytes([0x8D, TI[0] << 4, TI[1], len(THUGS)])),
             asm.setbyte(EV, 1), done, asm.ret(), asm.ret()]
    sec.add_entity("hbrescue", {0: roll})
    f.sections[0] = sec.build()
    print("  626: thugs at %s (dir %d), girl at %s (dir %d)" % ([t["at"][:2] for t in thugs],
          facing_screen(cam, *thugs[0]["at"][:3], (1, 1)), (gx, gy), gdir))


def _chain(var, blocks):
    """if var == k: blocks[k] (each falls through to the end)."""
    out, end = [], asm.nop()
    for k, ops in enumerate(blocks):
        nxt = asm.nop()
        out += [asm.if_byte(var, "==", k, nxt)] + ops + [asm.goto(end), nxt]
    return out + [end]

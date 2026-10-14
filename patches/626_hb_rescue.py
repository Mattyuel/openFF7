"""A customer abusing a Honey Bee girl outside the inn (user's design).

Each time you enter mrkt3 (Wall Market by the Honey Bee Inn) with at least one
girl hired, there is a 1 in 10 chance (`CHANCE`) that, in the lower right
corner, a customer (one of three `THUGS`, picked at random) stands over one of
your hired girls (picked at random), slapping her while she cowers on the
ground. Talk to him: "Leave her alone!" / "Walk away.". Stepping in starts a
battle (`FORMATION`; no escape, no game over: a loss just ends it, BTMD2 as
Corel's Cid fight). Win: her affection +1 (capped 20), her thanks, then the
screen fades out, both are gone, and it fades back in.

The girl is the Honey Bee dancer (the inn's uniform: the girls' own world
models can't all fit in one field), named in the lines. Her cowering pose
(ZCWA: sitting on the floor, knees drawn up, leaning in, arms up over her head,
trembling) and each thug's slap (ZTS<k>: leaning in, the right arm bent once
and swung at the shoulder onto her head, 660's `_spank_arm`) are built here;
each thug is placed where his hand lands on her head.

Models: mrkt3 was at 14. The thugs take over the three hidden party copies
(aerith / tifa / cid: Cloud always leads, so they are never shown) and their
model slots; the girl is a new entity and model (15). Madam M (600's quest
giver) moved out of the corner to make room (`_quest_data`).
"""
import math
import struct

from _config import HB_AFFECTION, HB_HIRED
from _honey_bee_data import GIRLS
from _recruit import sound
from _travel import CHOICE

from ff7 import asm
from ff7.camera import Camera, facing_screen
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

FIELD = "mrkt3"
CHANCE = 10                                     # 1 in CHANCE entries
# (user: "I can choose") the three thugs, one picked at random each time: (field, model index).
# All on Cloud's skeleton layout (AAFE / ACFE anims), so one slap recipe fits each.
THUGS = [("colne_2", 4),                        # Corneo's lackey (market_buka: suit, red hair)
         ("jail3", 3),                          # Corel convict (korel_bou1: shades, orange vest)
         ("colne_4", 8)]                        # Corneo's mansion guard (market_youjin_l: big, red vest)
TAKEN = ["earith", "tifa", "cid"]               # hidden party copies whose entities/models the thugs take over
FORMATION = 525                                 # Bullmotor (Corel prison's biker thug, level 19): user may pick
DANCER = ("onna_52", 1)                         # market_dancer, BADD.HRC
GIRL_AT = (100, -268)                           # her spot (the lower right corner, on screen ~(80,92))
THUG_FACING = (0.3, 1)                          # he stands behind her (up the screen), facing the camera
GIRL_FRAMES, THUG_FRAMES = 8, 15                # her tremble loop; his slap (lowest = the hit at the middle)
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
COWER_THIGH, COWER_LEAN, COWER_HEAD, COWER_ARMS, COWER_IN, COWER_TREMBLE = 115, 25, 25, 140, 50, 3
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
    for s, out in (("l", 1), ("r", -1)):
        arm = {s + "_uparm", s + "_foarm", s + "_hand"}
        W = T(W, arm, side, COWER_ARMS, lambda a, b: b[s + "_hand"][1] < a[s + "_hand"][1] - 2)   # arms up
        W = T(W, {s + "_foarm", s + "_hand"}, up, COWER_IN,
              lambda a, b: out * b[s + "_hand"][0] < out * a[s + "_hand"][0] - 0.3)              # in over her head
    E = ends(W, root)
    for s in "lr":                                                                            # feet on the floor
        assert abs(E[s + "_tibia"][1] - floor) < 0.1, (s, E[s + "_tibia"], floor)
    assert E["head"][1] < root[1], "head above the seat"
    frames = []
    for t in range(GIRL_FRAMES):
        a = COWER_TREMBLE * math.sin(2 * math.pi * t / GIRL_FRAMES)
        Wt = [fa._mul(fa.axis_angle(up, a), m) if names[i] in upper else m for i, m in enumerate(W)]
        frames.append((rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file("zcwa.a", base.build())
    return {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W)))}


SLAP_LEAN, SLAP_LEANS = 20, (20, 35, 50)          # a taller thug leans further to reach her


def _slap(ctx, hrc, name, target, lean=SLAP_LEAN):
    """`name`.a on skeleton `hrc` (Cloud's layout): his stand (AAFE frame 0) leaned SLAP_LEAN in, the
    right arm bent once so the hand lands on `target` (model space) at the middle frame, swung there
    from 660's SPANK_UP raised (THUG_FRAMES)."""
    from ff7 import fieldanim as fa
    dt = _dates()
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    names = [b[0] for b in sk]
    base = fa.Anim(ctx.char_file("zcte.a"))                # a 15-frame container on Cloud's layout
    rr, rp, rots = fa.Anim(ctx.char_file("aafe.a")).frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    side = [1.0, 0.0, 0.0]
    legs = {s + n for s in "lr" for n in ("_hip", "_femur", "_tibia", "_foot")}
    W = _turned(fa, sk, rr, W, root, set(names) - legs, side, lean, lambda a, b: b["head"][2] < a["head"][2])
    W, sense, arm = dt._spank_arm(fa, sk, rr, W, root, list(target), name)
    frames = []
    for t in range(THUG_FRAMES):
        e = (1 - math.cos(2 * math.pi * t / THUG_FRAMES)) / 2
        Wt = [fa._mul(fa.axis_angle(side, sense * dt.SPANK_UP * (1 - e)), m) if i in arm else m for i, m in enumerate(W)]
        frames.append((rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file(name.lower() + ".a", base.build())


def _off(m, d, unit):
    """Field (dx, dy, dz) of model point m for DIR d (models face -z, +x = their left)."""
    a = d * 2 * math.pi / 256
    F = (math.sin(a), -math.cos(a))
    L = (-F[1], F[0])
    return unit * (m[0] * L[0] - m[2] * F[0]), unit * (m[0] * L[1] - m[2] * F[1]), -unit * m[1]


def _model_point(dx, dy, dz, d, unit):
    """The inverse of _off: field offset -> model point for DIR d."""
    a = d * 2 * math.pi / 256
    F = (math.sin(a), -math.cos(a))
    L = (-F[1], F[0])
    return [(dx * L[0] + dy * L[1]) / unit, -dz / unit, -(dx * F[0] + dy * F[1]) / unit]


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
    head = _cower(ctx)["head"]
    gt = mesh.find(*GIRL_AT)
    assert gt is not None, GIRL_AT
    gz = mesh.height(gt, *GIRL_AT)
    tdir = facing_screen(cam, *GIRL_AT, gz, THUG_FACING)
    # (her legs pointed at him tangled with his) she sits side-on to him, turned the way that faces
    # the camera more
    def down(d):
        a_ = d * 2 * math.pi / 256
        p0, p1 = cam.project(*GIRL_AT, gz), cam.project(GIRL_AT[0] + 20 * math.sin(a_), GIRL_AT[1] - 20 * math.cos(a_), gz)
        return p1[1] - p0[1]
    gdir = max(((tdir + 64) % 256, (tdir - 64) % 256), key=down)
    dancer = ModelLoader(ctx.field(DANCER[0]).section("models")).models[DANCER[1]]
    gunit = UNIT * ModelLoader.entry_scale(dancer) / 512
    hx, hy, hz = _off(head, gdir, gunit)
    head_f = (GIRL_AT[0] + hx, GIRL_AT[1] + hy, gz + hz)            # her head top, in the field
    # each thug: his model in a taken-over slot, placed back along his facing until his slap reaches her head
    a = tdir * 2 * math.pi / 256
    fwd = (math.sin(a), -math.cos(a))
    thugs = []
    for k, ((dfield, di), ent_name) in enumerate(zip(THUGS, TAKEN)):
        ent = sec.entity_index(ent_name)
        init = sec.script_ops(ent, 0)
        assert init[0].op == 0xA1 and any(o.op == 0xA0 for o in init), (ent_name, [o.raw.hex() for o in init])  # CHAR, PC
        m = init[0].raw[1]
        src = ModelLoader(ctx.field(dfield).section("models"))
        entry = src.models[di]
        entry = ModelLoader.with_scale(entry, round(ModelLoader.entry_scale(entry) * loader.scale / src.scale))
        unit = UNIT * ModelLoader.entry_scale(entry) / 512
        hrc = ModelLoader.hrc(entry)
        anim = "ZTS" + "ABC"[k]
        placed = None
        for lean, dist in ((le, di) for le in SLAP_LEANS for di in range(0, 80)):   # least lean, nearest spot
            tx, ty = head_f[0] - fwd[0] * dist, head_f[1] - fwd[1] * dist   # along his facing, through her head
            tt = mesh.find(round(tx), round(ty))
            if tt is None:
                continue
            tz = mesh.height(tt, round(tx), round(ty))
            target = _model_point(head_f[0] - round(tx), head_f[1] - round(ty), head_f[2] - tz - 0.3 * gunit, tdir, unit)
            try:
                _slap(ctx, hrc, anim, target, lean)
            except AssertionError:
                continue
            placed = (round(tx), round(ty), tz, tt)
            break
        thug_lean = lean
        assert placed is not None, (ent_name, hrc)
        loader.models[m] = ModelLoader.with_anims(entry, [anim + ".tor"])
        slap = len(ModelLoader.anims(loader.models[m])) - 1
        thugs.append(dict(ent=ent, model=m, at=placed, slap=slap, idle=0, old_char=init[0]))
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
    girl_ent = len(sec.entity_names)                                     # the next entity (added below)
    # the thug's talk: shared by the three (each REQs nothing of the others)
    def talk(me):
        say = lambda t: hb._say(sec, t)
        end, walk, won = asm.nop(), asm.nop(), asm.nop()
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)]
        def ask(i, g):
            a_, first = hb._ask(sec, "Customer\n“What're you looking at? This is between\n me and %s here. Beat it.”"
                                % g["name"], ["Leave her alone!", "Walk away."])
            return a_ + [asm.if_byte(CHOICE, "!=", first, walk)]
        ops += by_girl(ask)
        ops += say("Customer\n“You wanna play hero? Fine by me!”")
        ops += [Op(bytes([0x22, 0x08, 0x00, 0x01, 0x00])),             # BTMD2: no escape, no game over
                asm.battle(FORMATION), Op(bytes([0x23, RES[0], RES[1]])),  # BTRLD
                asm.if_word(RES, "&", 1, won)]                         # bit 0 clear: won
        ops += say("Customer\n“Heh. Stay outta my business,\n pretty boy.”") + [asm.goto(end)]
        def thanks(i, g):
            aff = HB_AFFECTION[i]
            ok = asm.nop()
            return [Op(bytes([0x85, aff[0] << 4, aff[1], 1])), asm.if_byte(aff, ">", MAX, ok), asm.setbyte(aff, MAX), ok,
                    sound(0x168)] + say("%s\n“Cloud…! Thank you. I don't know\n what he'd have done…”" % g["name"])
        ops += [won] + by_girl(thanks)
        ops += [Op(hb.FADE_OUT), Op(b"\x6C"), asm.setbyte(EV, 0)] + hidden() + \
               [hb._req(girl_ent, 3), hb._w(15), Op(hb.FADE_IN), Op(b"\x6C"), asm.goto(end)]
        ops += [walk] + say("Customer\n“That's right. Keep walking.”")
        return ops + [end, hb._uc(0), asm.ret()]

    for k, th in enumerate(thugs):
        x, y, z, t = th["at"]
        loop, idle_top, quiet = hb._w(1), asm.nop(), asm.nop()
        # main: shown while this event has picked him; then a slap (the sound at the hit), a pause, again
        main = [asm.if_byte(EV, "==", 1, quiet), asm.if_byte(TI, "==", k, quiet)] + shown() + \
               [Op(bytes([0xA2, th["idle"], 1])), Op(bytes([0xAE, th["idle"], 1])),
                loop, asm.if_byte(EV, "==", 1, quiet),
                Op(bytes([0xBC, th["slap"], 0, THUG_FRAMES // 2, 1])), Op(b"\xAC"),
                sound(SLAP_SOUND), Op(bytes([0xBC, th["slap"], THUG_FRAMES // 2, THUG_FRAMES - 1, 1])), Op(b"\xAC"),
                Op(bytes([0xA2, th["idle"], 1])), Op(bytes([0xAE, th["idle"], 1])), hb._w(SLAP_PAUSE),
                asm.goto_back(loop),
                quiet, idle_top, hb._w(30), asm.goto_back(idle_top), asm.ret()]
        init = [Op(bytes([0xA1, th["model"]])), hb._xyzi(x, y, z, t), Op(bytes([0xB3, 0, tdir])),
                Op(bytes([0xC5, 0x00, 0x46]))] + hidden() + [asm.ret()]
        body = talk(th["ent"])
        sec.replace(th["old_char"], [asm.ret()])          # the old init (no longer an entry): no second CHAR
        empty = asm.ret()
        sec.ops.extend([empty] + init + main + body)
        sec.entry[th["ent"]] = [empty] * 32
        sec.entry[th["ent"]][0], sec.entry[th["ent"]][1] = init[0], body[0]

    # the girl
    gloop, gquiet = hb._w(30), asm.nop()
    ginit = [Op(bytes([0xA1, gm])), hb._xyzi(*GIRL_AT, gz, gt), Op(bytes([0xB3, 0, gdir])),
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
    for i in range(len(GIRLS)):
        nxt = asm.nop()
        var, bit = (HB_HIRED[0], HB_HIRED[1] + i // 8), i % 8
        roll += [asm.if_byte(GI, "==", i, nxt), asm.if_byte(var, "bit_on", bit, nxt), asm.goto(found), nxt]
    roll += [asm.goto_back(loop), found, Op(bytes([0x99, TI[0], TI[1]])), Op(bytes([0x8D, TI[0] << 4, TI[1], 3])),
             asm.setbyte(EV, 1), done, asm.ret(), asm.ret()]
    sec.add_entity("hbrescue", {0: roll})
    f.sections[0] = sec.build()
    print("  626: thugs at %s, girl at %s (dir %d)" % ([t["at"][:2] for t in thugs], GIRL_AT, gdir))


def _chain(var, blocks):
    """if var == k: blocks[k] (each falls through to the end)."""
    out, end = [], asm.nop()
    for k, ops in enumerate(blocks):
        nxt = asm.nop()
        out += [asm.if_byte(var, "==", k, nxt)] + ops + [asm.goto(end), nxt]
    return out + [end]

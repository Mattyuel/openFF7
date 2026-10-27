"""(user) The gym's training activities (data `_gym.py`): Tifa in the Wall Market gym (mkt_mens, added at `TIFA_AT`)
offers "Run a session." -> FIELD (a debug room only startmap leads to) = a copy of mkt_mens, script blanked,
gateways cleared. Tifa asks who's training; each session: fade, the member on `TRAIN_AT` (side-on), Cloud
coaching beside him, the member's lines, the how-to, the game, his result line, the fee (GOLDU), back to the menu:

- squats (Wedge, avafat): the films' prompt game (a random button a rep, `SQUAT_PERIODS` by tier, `SQUAT_HITS_UP`
  in a row = the next tier; `SQUAT_QUIT` misses in a row = he quits); his squat XKW0-3 built here (`_squat`);
- plank (Biggs, avaman): the danger meter (`_danger`, tag V) is his hips: entity `drift` moves it a step every
  `PLANK_DRIFT` frames (direction flipping `PLANK_FLIP` in 256), [OK] / [CANCEL] move it back; his pose follows
  (sag XKB0 / straight XKB1 / pike XKB2, `_plank`, trembling); either end = he collapses; the `clock` entity
  counts frames and the frames in the middle band (4-6);
- run (Jessie, avawoman): a "Step!" prompt every beat (`RUN_BEAT` by pace), [OK] within `RUN_WINDOW` = in time;
  `RUN_HITS_UP` in a row = pace up (walk, jog, run, sprint: her walk / run anims at speed 1-3), a miss = down.

Checked on offline renders only (spots, poses), untested in-game."""
import importlib
import math
import struct

import _besties_rig as RG
import _danger as DG
import _gym as GY
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import facing_screen, Camera
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

TIER, STREAK, KEY, PR, RND, KP, REPN, METER, DIRV, DC, PACE, MAXP, FAIL, SES = ((5, a) for a in range(100, 114))
PRV = [(5, 114 + k) for k in range(3)]
CNT, PER, PAY, GIL, T, GOODF, BL = ((6, a) for a in range(120, 134, 2))
MEMBERS = {"squats": ("mds7pb_1", 5), "plank": ("mds7pb_1", 4), "run": ("mds7pb_1", 3)}   # Wedge, Biggs, Jessie
ORDER = ("squats", "plank", "run")
CLOUD_SRC, TIFA_SRC = ("mds7pb_1", 0), ("mds7pb_1", 2)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _squat(ctx, hrc, n, name):
    """A bodyweight squat over n frames (frame 0 standing, n/2 at the bottom): hips down and back, the torso leaning
    in, knees forward over the planted feet (leg IK), arms raised forward for balance."""
    rg0 = RG.Rig(ctx, hrc, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
    E0 = rg0.ends()
    feet = {s: E0[s + "_tibia"] for s in "lr"}
    legs = rg0.length["l_femur"] + rg0.length["l_tibia"]
    frames = []
    for t in range(n):
        e = (1 - math.cos(2 * math.pi * t / n)) / 2
        rg = RG.Rig(ctx, hrc, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
        rg.root = RG.add(rg.root, [0.0, GY.SQUAT_DROP * legs * e, 0.35 * GY.SQUAT_DROP * legs * e])
        rg.waist(RG.bow(GY.SQUAT_LEAN * e))
        for s, sx in (("l", 1), ("r", -1)):
            rg.ik(s + "_femur", s + "_tibia", feet[s], [sx * 0.3, 0.0, -1.0], keep_end=True)
            d = RG.unit(RG.lerp([0.0, 1.0, 0.0], [0.0, 0.0, -1.0], GY.SQUAT_ARMS * e))
            rg.aim(s + "_uparm", d)
            rg.aim(s + "_foarm", d)
        frames.append(rg.frame())
    return RG.save(ctx, name, "acfe.a", frames)


def _plank(ctx, hrc, names):
    """Three 8-frame trembling planks (sag, straight, pike): the body pitched forward (solved: hands on the floor, arms
    straight, ankles at their standing height),
    the root lowered until the hands are on the floor, legs straight back to the ankles on the floor; sag = hips
    lowered, pike = hips raised (and the waist bent); hands and ankles held where the straight plank planted them
    (arm and leg IK)."""
    rg0 = RG.Rig(ctx, hrc, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
    E0 = rg0.ends()
    floor = max(E0[s + "_foot"][1] for s in "lr")
    ankle = max(E0[s + "_tibia"][1] for s in "lr")

    def base(bow=None):
        rg = RG.Rig(ctx, hrc, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
        rg.pelvis(RG.bow(bow if bow is not None else pitch))
        for s in "lr":
            rg.aim(s + "_uparm", [0.0, 1.0, 0.0])
            rg.aim(s + "_foarm", [0.0, 1.0, 0.0])
        E = rg.ends()
        low = max(E[s + "_hand"][1] for s in "lr")
        rg.root = RG.add(rg.root, [0.0, floor - low, 0.0])
        return rg
    # the pitch at which, hands on the floor and arms straight, the ankles are at their standing height
    lo, hi = 45.0, 89.0                                 # (more pitch = flatter = ankles higher: y smaller)
    for _ in range(30):
        pitch = (lo + hi) / 2
        y = max(base(pitch).ends()[s + "_tibia"][1] for s in "lr")
        lo, hi = (pitch, hi) if y > ankle else (lo, pitch)
    rg = base()
    E = rg.ends()
    hands = {s: E[s + "_foarm"] for s in "lr"}
    feet = {}
    for s in "lr":                                     # straight legs back from the hips, ankles on the floor
        H, L = E[s + "_femur@"], (rg.length[s + "_femur"] + rg.length[s + "_tibia"]) * 0.99
        feet[s] = E[s + "_tibia"]
    out = []
    for name, (dy, bow) in zip(names, ((GY.PLANK_SAG[0], GY.PLANK_SAG[1]), (0.0, 0.0),
                                        (-GY.PLANK_PIKE[0], GY.PLANK_PIKE[1]))):
        frames = []
        for k in range(8):
            rg = base()
            rg.root = RG.add(rg.root, [0.06 * math.sin(k * 2.3), dy, 0.0])
            rg.waist(RG.bow(bow))
            for s, sx in (("l", 1), ("r", -1)):
                rg.ik(s + "_femur", s + "_tibia", feet[s], [0.0, -1.0, 0.0] if dy > 0 else [0.0, 1.0, 0.0],
                      keep_end=False)
                rg.ik(s + "_uparm", s + "_foarm", hands[s], [sx * 1.0, 0.0, 0.5], keep_end=False)
            frames.append(rg.frame())
        out.append(RG.save(ctx, name, "acfe.a", frames))
    return out


def _tifa(ctx):
    """Tifa in the real gym: "Run a session." -> the set."""
    import _travel as TV
    hb = _mods()[1]
    mesh = Walkmesh(ctx.field(GY.BASE).section("walkmesh"))
    tt = mesh.find(*GY.TIFA_AT)
    assert tt is not None
    model = TV.copy_model(ctx, GY.BASE, *TIFA_SRC)
    ax, ay = GY.ARRIVE
    at_ = mesh.find(ax, ay)
    assert at_ is not None

    def talk(sec):
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + hb._say(sec, GY.TIFA_TALK["greet"])
        ask, first = hb._ask(sec, *GY.TIFA_TALK["ask"])
        no = asm.nop()
        ops += ask + [asm.if_byte(hb.CHOICE, "==", first, no), hb._uc(0), Op(hb.FADE_OUT), Op(b"\x6C"),
                      asm.mapjump(ctx.maplist.index(GY.FIELD), ax, ay, at_, 0), asm.ret(), no]
        return ops + hb._say(sec, GY.TIFA_TALK["no"]) + [hb._uc(0), asm.ret()]
    TV.add_npc(ctx, GY.BASE, "gymtifa", model, (*GY.TIFA_AT, round(mesh.height(tt, *GY.TIFA_AT)), tt), 0x00, talk)


def apply(ctx):
    mv, hb, dt = _mods()
    _tifa(ctx)
    ctx.field(GY.FIELD)
    f = ctx._fields[GY.FIELD] = FieldFile(ctx._orig_raw[GY.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    spot = lambda p: (p[0], p[1], round(mesh.height(mesh.find(*p), *p)), mesh.find(*p))
    for p in [GY.TRAIN_AT, GY.COACH_AT, GY.ARRIVE] + GY.WAIT_AT:
        assert mesh.find(*p) is not None, p
    train, coach, focus = spot(GY.TRAIN_AT), spot(GY.COACH_AT), spot(GY.ARRIVE)
    waits = [spot(p) for p in GY.WAIT_AT]
    side = facing_screen(cam, *train[:3], (-1, 0))                   # (683: side-on, facing screen-left)
    to = lambda a, b: dt._dir_to(b[0] - a[0], b[1] - a[1])
    # models: 0 the hidden player, 1 Cloud, 2 Tifa, 3 Wedge, 4 Biggs, 5 Jessie, 6 / 7 the meter
    loader = ModelLoader(f.section("models"))
    donor = lambda fs: ModelLoader(ctx.field(fs[0]).section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    out = [ModelLoader.only_anims(cl0, ModelLoader.anims(cl0)[:1])]
    for src in (CLOUD_SRC, TIFA_SRC) + tuple(MEMBERS[k] for k in ORDER):
        i = loader.add_from(donor(src), src[1])
        out.append(loader.models.pop(i))
    hrc = {k: ModelLoader.hrc(out[3 + j]).lower() for j, k in enumerate(ORDER)}
    squats = [_squat(ctx, hrc["squats"], n, "XKW%d" % k) for k, n in enumerate(GY.SQUAT_PERIODS)]
    planks = _plank(ctx, hrc["plank"], ["XKB0", "XKB1", "XKB2"])
    an = lambda m: ModelLoader.anims(m)
    out[1] = ModelLoader.only_anims(out[1], an(out[1])[:1])
    out[2] = ModelLoader.only_anims(out[2], an(out[2])[:1])
    out[3] = ModelLoader.only_anims(out[3], an(out[3])[:1] + squats)
    out[4] = ModelLoader.only_anims(out[4], an(out[4])[:1] + planks)
    assert an(out[5])[:3] == ["ACFE.aki", "AAFF.aki", "AAGA.aki"], an(out[5])[:3]
    out[5] = ModelLoader.only_anims(out[5], an(out[5])[:3])
    loader.models = out
    meter = DG.build(ctx, f, loader, "V", focus[:3])
    assert len(loader.models) == 8
    # entities
    names = ["dir", "cloud", "coach", "tifa", "wedge", "biggs", "jessie", "k_sw", "k_ca", "k_ok", "prompt", "clock",
             "drift", "gauge", "cursor"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i, sp=1: [mv._animb(), Op(bytes([0xA2, i, sp])), Op(bytes([0xAE, i, sp]))]
    ch_ = mv._chain
    at = lambda p, d: [xyzi(*p[:4]), d_(d)]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))
    scripts = {}
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at(focus, 0) + [hb._visi(0)] + hide() +
                           [asm.ret(), asm.ret()]}
    scripts[E["coach"]] = {0: [Op(bytes([0xA1, 1]))] + at(coach, to(coach, train)) + [hb._visi(1)] + hide() + loop_(0) +
                           [asm.ret(), asm.ret()]}
    tifa_at = spot((GY.TRAIN_AT[0] - 20, GY.TRAIN_AT[1] + 60)) if mesh.find(GY.TRAIN_AT[0] - 20, GY.TRAIN_AT[1] + 60) \
        is not None else waits[1]
    scripts[E["tifa"]] = {0: [Op(bytes([0xA1, 2]))] + at(tifa_at, to(tifa_at, train)) + [hb._visi(1)] + hide() +
                          loop_(0) + [asm.ret(), asm.ret()]}
    # members: 2 on the training spot (idle), 3 the tier's / pose's anim, 4 back to waiting, 5.. pace anims (Jessie)
    for j, k in enumerate(ORDER):
        ent = E[["wedge", "biggs", "jessie"][j]]
        w = waits[j]
        s = {0: [Op(bytes([0xA1, 3 + j]))] + at(w, to(w, train)) + [hb._visi(1)] + hide() + loop_(0) +
             [asm.ret(), asm.ret()],
             2: at(train, side) + loop_(0) + [asm.ret()],
             4: at(w, to(w, train)) + loop_(0) + [asm.ret()]}
        if k == "squats":
            s[3] = ch_(TIER, [loop_(1 + t) for t in range(4)]) + [asm.ret()]
        elif k == "plank":
            s[3] = [asm.nop()] + _bucket(METER, [loop_(1), loop_(2), loop_(3)]) + [asm.ret()]
        else:
            s[3] = ch_(PACE, [loop_(1), loop_(2), loop_(2, 2), loop_(2, 3)]) + [asm.ret()]
        scripts[ent] = s
    # buttons
    for k, (mask, _) in enumerate(GY.KEYS):
        top_, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top_,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held), asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), held,
                asm.goto_back(top_), up, asm.setbyte(PRV[k], 0), asm.goto_back(top_), asm.ret()]}
    pr = {0: [asm.ret(), asm.ret()]}
    for j, label in enumerate([lb for _, lb in GY.KEYS] + [GY.STEP]):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, 30, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    sc_ = DG.scripts(meter, METER, xyzi)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    MG_ = (E["gauge"], E["cursor"])
    biggs = E["biggs"]
    # plank: the clock (frames; frames in the middle band) and the drift, both running while the plank does
    ctop, cnot, cend = hb._w(1), asm.nop(), asm.nop()
    scripts[E["clock"]] = {0: [asm.ret(), asm.ret()],
                           2: [asm.setword(T, 0), asm.setword(GOODF, 0), ctop, Op(bytes([0x96, T[0], T[1]])),
                               asm.if_byte(METER, ">=", 4, cnot), asm.if_byte(METER, "<=", 6, cnot),
                               Op(bytes([0x96, GOODF[0], GOODF[1]])), cnot,
                               asm.if_byte(SES, "==", 1, cend), asm.goto_back(ctop), cend, asm.ret()]}
    dtop, early, skip, flip, dmove, dneg, dend = (hb._w(1),) + tuple(asm.nop() for _ in range(6))
    bump = [req(E["cursor"], 2), req(biggs, 3)]
    scripts[E["drift"]] = {0: [asm.ret(), asm.ret()],
                           2: [asm.setbyte(DC, 0), dtop, Op(bytes([0x95, DC[0], DC[1]])),
                               asm.if_byte(SES, "==", 1, dend),
                               asm.if_word(T, ">=", GY.PLANK_FRAMES // 2, early),          # (quicker from half way)
                               asm.if_byte(DC, ">=", GY.PLANK_DRIFT[1], skip), asm.goto(dmove),
                               early, asm.if_byte(DC, ">=", GY.PLANK_DRIFT[0], skip),
                               dmove, asm.setbyte(DC, 0), Op(bytes([0x99, RND[0], RND[1]])),
                               asm.if_byte(RND, "<", GY.PLANK_FLIP, flip), Op(bytes([0x93, DIRV[0] << 4, DIRV[1], 1])),
                               flip, asm.if_byte(DIRV, "==", 1, dneg), Op(bytes([0x85, METER[0] << 4, METER[1], 1]))] +
                           bump + [asm.goto(skip), dneg, Op(bytes([0x87, METER[0] << 4, METER[1], 1]))] + bump +
                           [skip, asm.goto_back(dtop), dend, asm.ret()]}

    # the director
    say = lambda t: hb._say(sec, t)
    lines = lambda ts: sum((say(t) for t in ts), [])
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    chime = Op(bytes([0xF1, 0, 0xEA, 1, 0x40]))
    members = [E["wedge"], E["biggs"], E["jessie"]]
    main = [hb._uc(1), hb._menu(1), asm.setbyte(SES, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, GY.MUSIC]) + bytes(8))] + lines(GY.INTRO)
    menu_top = asm.nop()
    main += [menu_top]
    ask, first = hb._ask(sec, *GY.MENU)
    main += ask
    sess_lab = [asm.nop() for _ in ORDER]
    bye = asm.nop()
    for j in range(len(ORDER)):
        nx = asm.nop()
        main += [asm.if_byte(hb.CHOICE, "==", first + j, nx), asm.goto(sess_lab[j]), nx]
    main += [asm.goto(bye)]
    paid = asm.nop()

    def start(j, kind):
        d = GY.SESSIONS[kind]
        return fade_out + [hb._req(members[j], 2), asm.setword(PAY, 0), asm.setword(GIL, 0), asm.setbyte(FAIL, 0),
                           hb._w(15)] + fade_in + lines(d["intro"]) + say(d["how"])

    def result(j, kind, good_test):
        d = GY.SESSIONS[kind]
        ok_, done = asm.nop(), asm.nop()
        ops = []
        if "quit" in d or "fail" in d:
            nf = asm.nop()
            ops += [asm.if_byte(FAIL, "!=", 0, nf)] + say(d.get("quit") or d["fail"]) + [asm.goto(done), nf]
        ops += good_test(ok_) + say(d["good"]) + [asm.goto(done), ok_] + say(d["ok"]) + [done]
        fee = say(GY.FEE)
        fee.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
        ops += [Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))] + fee
        return ops + fade_out + [hb._req(members[j], 4), hb._w(10)] + fade_in + [asm.goto_back(menu_top)]
    # squats
    j = 0
    n = len(GY.SQUAT_PERIODS)
    rep, wait, judge, miss, tail, after, rest, sq_end, mrow = (asm.nop() for _ in range(9))
    sq = [sess_lab[j]] + start(j, "squats") + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), asm.setbyte(REPN, 0),
                                               asm.setbyte(DC, 0), req(members[j], 3)]
    sq += [rep] + ch_(TIER, [[asm.setword(PER, p_)] for p_ in GY.SQUAT_PERIODS])
    sq += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])), asm.setbyte(KEY, RND),
           asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0), asm.setword(CNT, 0)]
    sq += ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)])
    sq += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
           asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait),
           judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss),
           Op(GY.HIT_SOUND), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])), asm.setbyte(DC, 0),
           Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(TIER, "<", n - 1, after),
           asm.if_byte(STREAK, ">=", GY.SQUAT_HITS_UP, after), Op(bytes([0x95, TIER[0], TIER[1]])),
           asm.setbyte(STREAK, 0), req(members[j], 3), after,
           rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(rest),
           tail, Op(bytes([0x95, REPN[0], REPN[1]])), asm.if_byte(REPN, "<", GY.SQUAT_REPS, sq_end),
           asm.goto_back(rep)]
    slow = asm.nop()
    sq += [miss, Op(b"\x54\x01"), buzz, asm.setbyte(STREAK, 0), Op(bytes([0x95, DC[0], DC[1]])),
           asm.if_byte(DC, ">=", GY.SQUAT_QUIT, mrow), asm.setbyte(FAIL, 1), asm.goto(sq_end), mrow,
           asm.if_byte(TIER, "!=", 0, slow), asm.setbyte(TIER, 0), req(members[j], 3), slow,
           asm.goto_back(rest), sq_end, Op(b"\x54\x01"),
           asm.setword(GIL, PAY), hb._arith(0x8A, GIL, GY.SQUAT_FEE)]
    sq += result(j, "squats", lambda ok_: [asm.if_word(PAY, ">=", GY.SQUAT_REPS + 10, ok_)])
    # plank
    j = 1
    pl = [sess_lab[j]] + start(j, "plank") + [asm.setbyte(SES, 1), asm.setbyte(DIRV, 0), asm.setbyte(PR, 0)] + \
        DG.start(METER, MG_) + [req(members[j], 3), req(E["clock"], 2), req(E["drift"], 2)]
    ptop, pnok, pnca, pchk, pend = hb._w(1), asm.nop(), asm.nop(), asm.nop(), asm.nop()
    pl += [ptop, asm.if_byte(PR, "==", 3, pnok), asm.setbyte(PR, 0), Op(bytes([0x85, METER[0] << 4, METER[1], 1])),
           req(E["cursor"], 2), req(biggs, 3), pnok,
           asm.if_byte(PR, "==", 2, pnca), asm.setbyte(PR, 0), Op(bytes([0x87, METER[0] << 4, METER[1], 1])),
           req(E["cursor"], 2), req(biggs, 3), pnca,
           asm.if_byte(METER, "==", 0, pchk), asm.setbyte(FAIL, 1), asm.goto(pend), pchk]
    p2 = asm.nop()
    pl += [asm.if_byte(METER, ">=", DG.STEPS - 1, p2), asm.setbyte(FAIL, 1), asm.goto(pend), p2,
           asm.if_word(T, "<", GY.PLANK_FRAMES, pend), asm.goto_back(ptop),
           pend, asm.setbyte(SES, 0), hb._w(3)] + DG.hide(MG_) + \
        [asm.setword(GIL, GOODF), hb._arith(0x8C, GIL, 30), hb._arith(0x8A, GIL, GY.PLANK_FEE)]
    pl += result(j, "plank", lambda ok_: [asm.if_word(GOODF, ">=", GY.PLANK_FRAMES * 2 // 3, ok_)])
    # run
    j = 2
    rn = [sess_lab[j]] + start(j, "run") + [asm.setbyte(PACE, 0), asm.setbyte(MAXP, 0), asm.setbyte(STREAK, 0),
                                            asm.setbyte(REPN, 0), req(members[j], 3)]
    beat, inwin, hit, rmiss, rrest, rdone, rnext = (asm.nop() for _ in range(7))
    rn += [beat] + ch_(PACE, [[asm.setword(BL, b_)] for b_ in GY.RUN_BEAT]) + \
        [asm.setbyte(PR, 0), asm.setword(CNT, 0), hb._req(E["prompt"], 5, wait=False)]
    win_lp = hb._w(1)
    rn += [win_lp, Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "!=", 0, inwin), asm.if_byte(PR, "==", 3, rmiss),
           asm.goto(hit), inwin, asm.if_word(CNT, "<", GY.RUN_WINDOW, rmiss), asm.goto_back(win_lp)]
    up_, dn_ = asm.nop(), asm.nop()
    rn += [hit, Op(b"\x54\x01"), Op(GY.HIT_SOUND), hb._arith(0x86, PAY, PACE), Op(bytes([0x96, PAY[0], PAY[1]])),
           Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(STREAK, ">=", GY.RUN_HITS_UP, rrest),
           asm.if_byte(PACE, "<", 3, rrest), asm.setbyte(STREAK, 0), Op(bytes([0x95, PACE[0], PACE[1]])),
           req(members[j], 3), asm.if_byte(PACE, "==", 3, rrest), asm.setbyte(MAXP, 1), asm.goto(rrest),
           rmiss, Op(b"\x54\x01"), buzz, asm.setbyte(STREAK, 0), asm.if_byte(PACE, "!=", 0, rrest),
           Op(bytes([0x97, PACE[0], PACE[1]])), req(members[j], 3)]
    rest_lp = hb._w(1)
    rn += [rrest, asm.if_word(CNT, "<", BL, rnext), rest_lp, Op(bytes([0x96, CNT[0], CNT[1]])),
           asm.if_word(CNT, "<", BL, rnext), asm.goto_back(rest_lp), rnext,
           Op(bytes([0x95, REPN[0], REPN[1]])), asm.if_byte(REPN, "<", GY.RUN_BEATS, rdone), asm.goto_back(beat),
           rdone, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, GY.RUN_FEE)]
    rn += result(j, "run", lambda ok_: [asm.if_byte(MAXP, "!=", 0, ok_)])
    main += sq + pl + rn
    # done for today: back beside Tifa in the real gym
    bm = Walkmesh(ctx.field(GY.BASE).section("walkmesh"))
    bx, by = GY.TIFA_AT[0] + 30, GY.TIFA_AT[1]
    bt = bm.find(bx, by)
    assert bt is not None
    stop_ = hb._w(30)
    main += [bye] + say(GY.BYE) + fade_out + \
        [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(GY.BASE), bx, by, bt, 0xC0),
         stop_, asm.goto_back(stop_)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  693: gym sessions on %s (train %s side %d, coach %s, waits %s; %d texts, script %d bytes)"
          % (GY.FIELD, train[:3], side, coach[:3], [w[:3] for w in waits], n_text, len(f.sections[0])))


def _bucket(var, blocks):
    """sag below 4, straight 4-6, pike above 6 (the meter's 11 steps)."""
    lo, mid, end = asm.nop(), asm.nop(), asm.nop()
    return [asm.if_byte(var, "<", 4, lo)] + blocks[0] + [asm.goto(end), lo,
                                                         asm.if_byte(var, "<=", 6, mid)] + blocks[1] + \
        [asm.goto(end), mid] + blocks[2] + [end]

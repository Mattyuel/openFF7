"""(user) Going up: the second parody film (data `_going_up.py`, poses `_going_up_poses.py`), in Shinra HQ's
glass elevator, starring Cloud, Tifa and Elena.

The set: FIELD (a debug room only startmap leads to) replaced by a copy of eleout, script blanked but the car
(background layer 1 in state 1, as eleout's `gondora` sets it) and the rails (layer 2, cycled while MOVING:
eleout's `rale_up`, on our own temp var) rebuilt. Models: Cloud (the hidden player), clothed Cloud / Tifa
(683's tied-up hair, `CLOTHED_TIED`) / Elena for the intro, bare Cloud / Tifa (683's XWUA) / Elena for the
rest. No Director model (the car is tight): his lines are text.

The intro (staged, `_going_up.INTRO_LINES` with actions): Elena walks in, Cloud tries the panel, the door's
stuck, Tifa's special training, Elena agrees and undresses (fade: her bare model covering up), crawls over
(her dog stroke while she slides across the floor), Cloud walks round behind her; fade; the scene models:
Elena on all fours, Cloud behind her, Tifa kneeling by them watching.

The gameplay (683's, more of it): a prompt a rep ([SWITCH] / [CANCEL] / [OK]) at the tier's pace (4 tiers =
the movie's 4 stroke speeds, a prompt every 3 strokes), HITS_UP hits in a row step up, a miss drops to the
slowest; from tier 1 some prompts are HOLD ones (press in time, keep holding to the rep's end: double pay;
HELD bits from the pollers); every SWITCH_MIN..+RANGE reps Tifa calls "Switch!" with a [MENU] prompt (a hit:
a bonus and a clean switch; a miss: switch and drop the pace): Cloud goes from behind Elena to standing
before Tifa (her head) or back. Each tier's lines the first time with each partner. After TOTAL_REPS the
car moves at last (MOVING), the finale, the pay, back to the Director. Checked on offline renders only."""
import importlib
import math
import struct

import _going_up as GU
import _going_up_poses as GP
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera, facing_screen
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

CLOTHED_TIED = "XWVA.HRC"           # Tifa's own clothes, hair tied up (683 `_tie`)
TIFA_DONOR = ("eleout", 1)          # AAGB: ABCD stand, ABCE walk
ELENA_DONOR = ("datiao_6", 10)      # EVFE: ACFE stand, AAFF walk
BARE_TIFA, BARE_ELENA = "XWUA.HRC", "ZELA.HRC"
WALK_STEP = 2.6

TIER, STREAK, KEY, PR, P, SEEN, RND, KP, HOLD, HELD, SINCE, NEXTSW, MOVING = ((5, a) for a in range(100, 113))
CNT, PAY, REPS, PER, GIL, CX, CY = ((6, a) for a in range(114, 128, 2))
PRV = [(5, 130 + k) for k in range(4)]
WN = (5, 134)                        # a walk's frame count


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates"), importlib.import_module("683_workout")


def _rot(v, d):
    a = d * 2 * math.pi / 256
    return v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)


def apply(ctx):
    mv, hb, dt, wo = _mods()
    # Tifa's own clothes with her hair tied up
    tifa_e = ModelLoader(ctx.field(TIFA_DONOR[0]).section("models")).models[TIFA_DONOR[1]]
    text = ctx.char_file(ModelLoader.hrc(tifa_e).lower()).decode("latin-1")
    ctx.char_file(CLOTHED_TIED.lower(), wo._tie(ctx, text).encode("latin-1"))
    elena_l = ModelLoader(ctx.field(ELENA_DONOR[0]).section("models"))
    elena_e = elena_l.models[ELENA_DONOR[1]]
    e_stand = ModelLoader.anims(elena_e)[0].split(".")[0].lower() + ".a"
    own = GP.build(ctx, BARE_ELENA, e_stand)                            # QEA0 covering, QEB0 still
    # the set
    ctx.field(GU.FIELD)
    ctx.field(GU.BASE)
    f = ctx._fields[GU.FIELD] = FieldFile(ctx._orig_raw[GU.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    cam = Camera(f.sections[1])
    from ff7.walkmesh import Walkmesh
    mesh = Walkmesh(f.section("walkmesh"))

    def tri(x, y):
        t = mesh.find(round(x), round(y))
        assert t is not None, ("off the floor", x, y)
        return t
    Z = GU.FLOOR
    # spots
    ex, ey = GU.ELENA_AT
    dE = facing_screen(cam, ex, ey, Z, (-1, 0))
    o = _rot((-2, 22), dE)                                              # (670 dog: Cloud 22 behind her)
    ck = (round(ex + o[0]), round(ey + o[1]))
    ch = (ck[0] + GU.HEAD_SHIFT[0], ck[1] + GU.HEAD_SHIFT[1])
    dT = facing_screen(cam, ch[0], ch[1], Z, (1, 0))
    o = _rot((-1, -38), dT)                                             # (670 head: Cloud 38 before her, facing her)
    tp = (round(ch[0] - o[0]), round(ch[1] - o[1]))
    dC = (dT + 128) % 256
    for p in (ck, ch, tp):
        tri(*p)
    # models: 0 hidden player, 1-3 clothed Cloud / Tifa / Elena, 4-6 bare Cloud / Tifa / Elena
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    c_anims = ModelLoader.anims(cl0)
    t_anims = ModelLoader.anims(tifa_e)
    bare_c = ["ZNC%d.tor" % s for s in range(4)] + ["ZNJ%d.tor" % s for s in range(4)]
    bare_t = ["ZVJ%d.tor" % s for s in range(4)] + ["ZVJ9.tor"]
    bare_e = own + ["ZYC%d.tor" % s for s in range(4)]
    for n in bare_c + bare_t + bare_e:
        ctx.char_file(n.split(".")[0].lower() + ".a")                    # (exists)
    ei = loader.add_from(elena_l, ELENA_DONOR[1])
    elena_m = loader.models.pop(ei)
    loader.models = [cl0, ModelLoader.only_anims(cl0, c_anims[:2]),
                     ModelLoader.only_anims(ModelLoader.with_hrc(tifa_e, CLOTHED_TIED, "goingup_tifa.char"), t_anims[:2]),
                     ModelLoader.only_anims(elena_m, ModelLoader.anims(elena_m)[:2]),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "goingup_cloudb.char"),
                                            c_anims[:1] + bare_c),
                     ModelLoader.only_anims(ModelLoader.with_hrc(tifa_e, BARE_TIFA, "goingup_tifab.char"),
                                            t_anims[:1] + bare_t),
                     ModelLoader.only_anims(ModelLoader.with_hrc(elena_m, BARE_ELENA, "goingup_elenab.char"),
                                            ModelLoader.anims(elena_m)[:1] + bare_e)]
    # entities
    names = ["produce", "cloud", "cloudA", "tifaA", "elenaA", "cloudB", "tifaB", "elenaB", "car", "rail",
             "k_sw", "k_ca", "k_ok", "k_mn", "prompt", "talk", "hush"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch_ = mv._chain
    face = lambda x, y, tx, ty: dt._dir_to(tx - x, ty - y)
    at = lambda p, d: [xyzi(p[0], p[1], Z, tri(*p)), d_(d)]

    def walk(start, stop, walk_anim, stand_anim, d_end):
        """XYZI stepped WALK_STEP a frame from start to stop with the walk anim, then stand facing d_end."""
        (sx, sy), (tx, ty) = start, stop
        n = max(1, round(math.dist(start, stop) / WALK_STEP))
        stx, sty = round((tx - sx) / n), round((ty - sy) / n)
        top, done = hb._w(1), asm.nop()
        return [d_(face(sx, sy, tx, ty)), asm.setword(CX, sx & 0xFFFF), asm.setword(CY, sy & 0xFFFF),
                asm.setbyte(WN, 0)] + loop_(walk_anim) + \
            [top, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
             Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], Z, tri(*start))),
             Op(bytes([0x95, WN[0], WN[1]])), asm.if_byte(WN, "<", n, done), asm.goto_back(top), done] + \
            at(stop, d_end) + loop_(stand_anim)
    scripts = {}
    fx, fy = GU.FOCUS
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at((fx, fy), 0) + [hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()]}
    I = GU.INTRO
    # the car (layer 1 state 1) and the rails (layer 2, cycled while MOVING), as eleout's own entities
    scripts[E["car"]] = {0: [Op(b"\xE4\x00\x01"), Op(b"\xE0\x00\x01\x01"), asm.ret(), asm.ret()]}
    rtop, still = hb._w(1), asm.nop()
    rail = [Op(b"\xE4\x00\x02"), Op(b"\xE0\x00\x02\x00"), asm.ret(), rtop, asm.if_byte(MOVING, "==", 1, still)]
    for s in range(1, 5):
        rail += [hb._w(2), Op(bytes([0xE1, 0, 2, s - 1])), Op(bytes([0xE0, 0, 2, s]))]
    rail += [hb._w(2), Op(b"\xE1\x00\x02\x04"), Op(b"\xE0\x00\x02\x00"), still, asm.goto_back(rtop), asm.ret()]
    scripts[E["rail"]] = {0: rail}
    # the intro actors: 0 init, 8 the intro's action, 4 hidden
    cpos, tpos, efrom, epos, panel = I["cloud"], I["tifa"], I["elena_from"], I["elena"], I["panel"]
    scripts[E["cloudA"]] = {
        0: [Op(bytes([0xA1, 1]))] + at(cpos, face(*cpos, *epos)) + [hb._visi(1)] + hide() + loop_(0) + [asm.ret(), asm.ret()],
        8: walk(cpos, panel, 1, 0, face(*panel, *GU.CONSOLE)) + [asm.ret()],          # to the console
        9: walk(panel, ck, 1, 0, dE) + [asm.ret()],                                 # round behind her
        4: [hb._visi(0), asm.ret()]}
    scripts[E["tifaA"]] = {
        0: [Op(bytes([0xA1, 2]))] + at(tpos, face(*tpos, *epos)) + [hb._visi(1)] + hide() + loop_(0) + [asm.ret(), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    scripts[E["elenaA"]] = {
        0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        8: at(efrom, face(*efrom, *epos)) + [hb._visi(1)] + walk(efrom, epos, 1, 0, face(*epos, *cpos)) + [asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    ce, cn = bare_c.index, bare_e.index
    # the scene actors: 0 init hidden; 2 = this rep (by P: placed, the tier's stroke from its start); 4 hidden;
    # Elena 8 covering (intro), 9 the crawl
    stroke = lambda base: ch_(TIER, [loop_(1 + base + s) for s in range(4)])
    scripts[E["cloudB"]] = {
        0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(P, [at(ck, dE) + stroke(0), at(ch, dC) + stroke(4)]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    ti = lambda n: 1 + bare_t.index(n)
    scripts[E["tifaB"]] = {
        0: [Op(bytes([0xA1, 5])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: at(tp, dT) + ch_(P, [loop_(ti("ZVJ9.tor")), ch_(TIER, [loop_(ti("ZVJ%d.tor" % s)) for s in range(4)])]) +
        [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    ei_ = lambda n: 1 + bare_e.index(n)
    n_crawl = max(1, round(math.dist(epos, (ex, ey)) / (WALK_STEP * 0.5)))
    stx, sty = round((ex - epos[0]) / n_crawl), round((ey - epos[1]) / n_crawl)
    ctop, cdone = hb._w(1), asm.nop()
    crawl = at(epos, dE) + loop_(ei_("ZYC0.tor")) + \
        [asm.setword(CX, epos[0] & 0xFFFF), asm.setword(CY, epos[1] & 0xFFFF), asm.setbyte(WN, 0),
         ctop, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
         Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], Z, tri(*epos))),
         Op(bytes([0x95, WN[0], WN[1]])), asm.if_byte(WN, "<", n_crawl, cdone), asm.goto_back(ctop), cdone] + \
        at((ex, ey), dE) + loop_(ei_("QEB0.tor"))
    scripts[E["elenaB"]] = {
        0: [Op(bytes([0xA1, 6])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: at((ex, ey), dE) + ch_(P, [ch_(TIER, [loop_(ei_("ZYC%d.tor" % s)) for s in range(4)]),
                                       loop_(ei_("QEB0.tor"))]) + [hb._visi(1), asm.ret()],
        8: at(epos, face(*epos, *cpos)) + [hb._visi(1)] + loop_(ei_(own[0])) + [asm.ret()],
        9: crawl + [asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    # the buttons: one small entity each; a press = up -> down (PR = its number), HELD bit k while held
    for k, (mask, _) in enumerate(GU.KEYS + [GU.SWITCH_KEY]):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok", "k_mn"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    # the prompts: window 1 (the director closes it); slots 2-4 the buttons, 5-7 HOLD + the button, 8 [MENU]
    pr = {0: [asm.ret(), asm.ret()]}
    labels = [l for _, l in GU.KEYS] + [GU.HOLD_LABEL + l for _, l in GU.KEYS] + [GU.SWITCH_KEY[1]]
    for j, label in enumerate(labels):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, GU.PROMPT_Y, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    # the talk: window 2, groups of lines each shut by hush after SAY
    groups, gid = [], {}
    for part in (0, 1):
        for t, lines in sorted(GU.LINES[part].items()):
            gid[(part, t)] = len(groups)
            groups.append(lines)
    for k, line in enumerate(GU.SWITCH_CALL):
        gid[("switch", k)] = len(groups)
        groups.append([line])
    gid["miss"] = len(groups)
    groups.append([GU.MISS])
    talk = {0: [asm.ret(), asm.ret()]}
    for j, lines in enumerate(groups):
        ops = []
        for text in lines:
            ops += [Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, GU.LINE_Y), hb._req(E["hush"], 2, wait=False),
                    asm.message(2, mv._text_id(sec, text))]
        talk[2 + j] = ops + [asm.ret()]
    scripts[E["talk"]] = talk
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(GU.SAY), Op(b"\x54\x02"), asm.ret()]}
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))        # REQ: never waits

    # the director
    say = lambda t: hb._say(sec, t)
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    fast_out, fast_in = [Op(mv.FAST_OUT), Op(b"\x6C")], [Op(mv.FAST_IN), Op(b"\x6C")]
    main = [hb._uc(1), hb._menu(1), asm.setbyte(MOVING, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, GU.MUSIC]) + bytes(8)), hb._req(E["elenaA"], 8)]
    for line, action in GU.INTRO_LINES:
        main += say(line)
        if action == "cloud_panel":
            main += [hb._req(E["cloudA"], 8)]
        elif action == "undress":
            main += fade_out + [hb._req(E["elenaA"], 4), hb._req(E["elenaB"], 8), hb._w(10)] + fade_in
        elif action == "crawl":
            main += [hb._req(E["elenaB"], 9)]
        elif action == "behind":
            main += [hb._req(E["cloudA"], 9)] + fade_out + [hb._req(E["cloudA"], 4), hb._req(E["tifaA"], 4)]
            main += [asm.setbyte(P, 0), asm.setbyte(TIER, 0)] + \
                [hb._req(E[a], 2) for a in ("cloudB", "tifaB", "elenaB")] + [hb._w(20)] + fade_in
    main += say(GU.HOW)
    main += [asm.setbyte(STREAK, 0), asm.setbyte(SEEN, 0x11), asm.setword(PAY, 0), asm.setword(REPS, 0),
             asm.setbyte(SINCE, 0), asm.setbyte(NEXTSW, GU.SWITCH_MIN), asm.setbyte(HELD, 0)]
    n = len(GU.PERIODS)
    rep, wait, judge, hit, miss, rest, tail, holdw, done_h, sw_rep, normal, after = (asm.nop() for _ in range(12))
    main += [rep] + [req(E[a], 2) for a in ("cloudB", "tifaB", "elenaB")]
    main += ch_(TIER, [[asm.setword(PER, p)] for p in GU.PERIODS])
    main += [asm.setbyte(PR, 0), asm.setword(CNT, 0), asm.setbyte(HOLD, 0),
             asm.if_byte(SINCE, ">=", NEXTSW, normal), asm.goto(sw_rep), normal]
    # a button rep: KEY at random; from tier 1, now and then a HOLD one
    nohold = asm.nop()
    main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])),
             asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])),
             asm.if_byte(TIER, ">=", 1, nohold), Op(bytes([0x99, RND[0], RND[1]])),
             asm.if_byte(RND, "<", GU.HOLD_ODDS, nohold), asm.setbyte(HOLD, 1), nohold]
    main += ch_(HOLD, [ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)]),
                       ch_(KEY, [[hb._req(E["prompt"], 5 + k, wait=False)] for k in range(3)])])
    main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.if_byte(PR, "==", 0, judge), asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait)]
    main += [judge, asm.if_byte(PR, "==", KP, miss)]
    # a HOLD: the button kept down to the rep's end (the window stays up meanwhile)
    main += [asm.if_byte(HOLD, "==", 1, done_h), holdw, asm.if_word(CNT, "<", PER, done_h),
             asm.if_byte(HELD, "bit_on", KEY, miss), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(holdw),
             done_h, Op(b"\x54\x01")]
    # a hit: pay (a HOLD twice), streak, maybe a tier up (its lines the first time with this partner)
    once = asm.nop()
    main += [hit, Op(bytes([0x96, REPS[0], REPS[1]])), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])),
             asm.if_byte(HOLD, "==", 1, once), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])), once,
             Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(TIER, "<", n - 1, after),
             asm.if_byte(STREAK, ">=", GU.HITS_UP, after), Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)]
    for part in (0, 1):
        for t in range(1, n):
            nx = asm.nop()
            if (part, t) in gid:
                bit = t + 4 * part
                main += [asm.if_byte(P, "==", part, nx), asm.if_byte(TIER, "==", t, nx), asm.if_byte(SEEN, "bit_off", bit, nx),
                         asm.biton(SEEN, bit), req(E["talk"], 2 + gid[(part, t)]), nx]
    main += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.goto_back(rest), tail, Op(bytes([0x95, SINCE[0], SINCE[1]]))]
    fin = asm.nop()
    main += [asm.if_word(REPS, "<", GU.TOTAL_REPS, fin), asm.goto_back(rep)]
    # a miss: the buzz, back to the slowest pace (Tifa says so if it was fast), the rep's rest, then on
    slow, mtail, mdone = asm.nop(), asm.nop(), asm.nop()
    main += [miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]])),
             asm.if_byte(TIER, ">=", 2, slow), req(E["talk"], 2 + gid["miss"]), slow,
             asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), mtail, asm.if_word(CNT, "<", PER, mdone),
             hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(mtail), mdone, asm.goto_back(tail)]
    # Tifa's "Switch!": [MENU] in time = a bonus; either way Cloud switches partner (fast fade)
    sw_wait, sw_judge, sw_miss, sw_go = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    main += [sw_rep] + ch_(P, [[req(E["talk"], 2 + gid[("switch", 0)])], [req(E["talk"], 2 + gid[("switch", 1)])]]) + \
        [hb._req(E["prompt"], 8, wait=False),
         sw_wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, sw_judge),
         asm.if_word(CNT, "<", PER, sw_miss), asm.goto_back(sw_wait),
         sw_judge, asm.if_byte(PR, "==", 4, sw_miss), Op(b"\x54\x01"), hb._arith(0x86, PAY, GU.SWITCH_BONUS),
         asm.goto(sw_go),
         sw_miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0),
         sw_go, Op(bytes([0x93, P[0] << 4, P[1], 1])),                               # XOR P, 1
         asm.setbyte(SINCE, 0), Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], GU.SWITCH_RANGE])),
         asm.setbyte(NEXTSW, RND), Op(bytes([0x85, NEXTSW[0] << 4, NEXTSW[1], GU.SWITCH_MIN])),      # PLUS
         ] + fast_out + [req(E[a], 2) for a in ("cloudB", "tifaB", "elenaB")] + [hb._w(8)] + fast_in + \
        [asm.goto_back(rep)]
    # the end: the car moves at last
    main += [fin, Op(b"\x54\x01"), Op(b"\x54\x02"), asm.setbyte(MOVING, 1), hb._w(30)]
    for t in GU.FINALE:
        main += say(t)
    main += [asm.setword(GIL, PAY), hb._arith(0x8A, GIL, GU.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(GU.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
    main += paid + fade_out
    rx, ry, rz, rt, rdir = ctx.movie_back
    stop = hb._w(30)
    main += [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir),
             stop, asm.goto_back(stop)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  684: Going up on %s (Elena %s, Cloud behind %s / before Tifa %s at %s; %d texts, script %d bytes)"
          % (GU.FIELD, GU.ELENA_AT, ck, ch, tp, n_text, len(f.sections[0])))

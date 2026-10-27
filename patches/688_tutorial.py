"""(user) The Basics: the tutorial film (data `_tutorial.py`), first in the Director's film menu. In the Sector 7
inn where every shoot happens (FIELD, a debug room only startmap leads to, replaced by a copy of mds7_w3: 670's
set, script blanked, gateways cleared), the Director walks Cloud and Tifa through three of the movie's positions
on 670's own spots (`ctx.movie_places`): head, all fours ("dog") and sixty-nine, with the movie's anims (Cloud
ZN<letter>, Tifa ZV<letter>: her undressed ZTFA). Each position: fade, the setup talk (both still), then the
prompt game (683-687's: a prompt a rep, hits speed up and pull the danger meter in, misses push it out, the
red = CUT) with beats after given reps: talk while they go on, pauses (both still: Tifa speaks clearly only
then; muffled while they move), the head hold demonstrated (held deep, her tap-out squirm, he lets go, pulls
out and wiggles: `_wiggle`), Cloud tasting her on all fours (`_taste`: kneeling behind her, his face at her,
moving subtly; she holds still), the 'there' suggestion (talk, both still). Then the finisher explained and
played (10 s of [OK], `_danger.finale`), the outro, the pay, back to the Director. The camera follows the
hidden player at each position's focus; the meter has a view per position; the Director stands on the
cameraman's spot of each position, filming. Checked offline (taste pose numerically) only, untested in-game."""
import importlib
import math
import struct

import _besties_rig as RG
import _danger as DG
import _tickets_poses as TP
import _tutorial as TU
import _wiggle as WG
from ff7 import asm
from ff7 import fieldanim as fa
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

TIER, STREAK, KEY, PR, SEG, RND, KP, REPN, HELD, METER, SIDE, DEC = ((5, a) for a in range(100, 112))
PRV = [(5, 112 + k) for k in range(3)]
CNT, PER, PAY, GIL = ((6, a) for a in range(120, 128, 2))
SEGS = ("head", "dog", "69")
TIFA_DONOR = ("bwhlin", 3)              # AAGB, stand ABCD
BARE_TIFA = "ZTFA.HRC"
TASTE_FRAMES = 48
TASTE = dict(tilt=8, spread=20, out=0.35, yaw=6, nod=5)     # kneeling; the face's point out; the head's wander


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _taste(ctx, hb, girl, gdir, cloud, cdir):
    """(user: "the director can suggest cloud taste tifa, which will involve cloud putting his head there and
    moving it around subtly") Cloud kneeling behind Tifa (on all fours, her ZVC0 first frame held: QXT9) on his
    own dog spot, his face at her entry (fitted: waist bend, root shifts), hands on her hips, his head
    wandering; YXT0. Returns (his anim, her anim, the face's distance from her at frame 0)."""
    her = TP.still(ctx, "ZVC0", "QXT9")
    e_f = TP._field(girl, gdir, TP.entry_points(ctx, BARE_TIFA, "abcd.a", "QXT9")[0])
    J = TP.joints(ctx, BARE_TIFA, "QXT9")[0]
    hips = {s: TP._field(girl, gdir, J[s + "_femur@"]) for s in "lr"}
    to_m = lambda p: TP._inv_off([p[k] - cloud[k] for k in range(3)], cdir)
    target = to_m(e_f)
    c = TASTE

    def build(x, t=0.0):
        wb, ds, dx, drop = x
        rg = RG.Rig(ctx, hb.CLOUD_BARE_HRC, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
        RG.kneel(rg, c["tilt"], c["spread"], 0.0)
        rg.waist(RG.bow(wb))
        rg.neck(RG.chain(RG.bow(-10 + c["nod"] * math.sin(4 * math.pi * t)), RG.turn(c["yaw"] * math.sin(2 * math.pi * t))))
        rg.root = RG.add(rg.root, [dx, drop, -ds])
        return rg
    cost = lambda r: math.dist(RG.face_pt(r, out=c["out"]), target)
    x, r0 = RG.fit(build, cost, [40, 0, 0, 0], [8, 1.0, 0.5, 0.5],
                   bounds=[(0, 95), (-8, 8), (-3, 3), (-2, 2)])
    gap = cost(r0)
    frames = []
    for k in range(TASTE_FRAMES):
        r = build(x, k / TASTE_FRAMES)
        for s, sx, her_s in (("l", 1, "r"), ("r", -1, "l")):               # hands on her hips
            r.ik(s + "_uparm", s + "_foarm", to_m(hips[her_s]), [sx * 1.0, 0.6, 0.3])
        frames.append(r.frame())
    return RG.save(ctx, "YXT0", "acfe.a", frames), her, gap


def apply(ctx):
    mv, hb, dt = _mods()
    places = ctx.movie_places
    pos = [p["name"] for p in mv.POSITIONS]
    idx = [pos.index(k) for k in SEGS]
    letter = [chr(ord("A") + i) for i in idx]                               # (670's anim letters by position)
    P = [places[i] for i in idx]
    # the set
    ctx.field(TU.FIELD)
    ctx.field(TU.BASE)
    f = ctx._fields[TU.FIELD] = FieldFile(ctx._orig_raw[TU.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    # anims
    stroke_c = [["ZN%s%d.tor" % (L, s) for s in range(4)] for L in letter]
    stroke_t = [["ZV%s%d.tor" % (L, s) for s in range(4)] for L in letter]
    pause_c = ["ZNJ9.tor", TP.still(ctx, "ZNC0", "QXC9"), "ZNI9.tor"]
    pause_t = ["ZVJ9.tor", TP.still(ctx, "ZVC0", "QXV9"), "ZVI9.tor"]
    assert letter == ["J", "C", "I"], letter
    taste_c, taste_t, gap = _taste(ctx, hb, P[1]["girl"], P[1]["gdir"], P[1]["cloud"], P[1]["cdir"])
    wig = WG.build(ctx, hb.CLOUD_BARE_HRC, "ZNJ0", "QXW0")
    bare_c = sum(stroke_c, []) + pause_c + ["ZNJ8.tor", taste_c, wig]
    bare_t = sum(stroke_t, []) + pause_t + ["ZVJ8.tor", "ZVJ7.tor", taste_t]
    for n in bare_c + bare_t:
        ctx.char_file(n.split(".")[0].lower() + ".a")                       # (exists)
    # models: 0 the hidden player, 1 / 2 clothed Cloud / Tifa (intro), 3 / 4 bare, 5 the Director, 6 / 7 the meter
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    c_anims = ModelLoader.anims(cl0)
    ti = loader.add_from(ModelLoader(ctx.field(TIFA_DONOR[0]).section("models")), TIFA_DONOR[1])
    tifa_e = loader.models.pop(ti)
    t_anims = ModelLoader.anims(tifa_e)
    loader.models = [cl0, ModelLoader.only_anims(cl0, c_anims[:2]), ModelLoader.only_anims(tifa_e, t_anims[:2]),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "tutorial_cloudb.char"),
                                            c_anims[:1] + bare_c),
                     ModelLoader.only_anims(ModelLoader.with_hrc(tifa_e, BARE_TIFA, "tutorial_tifab.char"),
                                            t_anims[:1] + bare_t)]
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    cam_anims = ModelLoader.anims(loader.models[cm])
    film = cam_anims.index(mv.CAMERA_FILM)
    loader.models[cm] = ModelLoader.only_anims(loader.models[cm], cam_anims + [mv.CAMERA_STILL])
    still = len(cam_anims)
    meter = DG.build(ctx, f, loader, "Q", [p["focus"][:3] for p in P])      # (one view per position)
    assert len(loader.models) == 8 and all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    # entities
    names = ["dir", "cloud", "cloudA", "tifaA", "cloudB", "tifaB", "drctr", "k_sw", "k_ca", "k_ok", "prompt",
             "gauge", "cursor"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch_ = mv._chain
    at = lambda p, d: [xyzi(*p[:4]), d_(d)]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))
    scripts = {}
    head = P[0]
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at(head["focus"], 0) + [hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()],
                           2: ch_(SEG, [at(p["focus"], 0) for p in P]) + [asm.ret()]}
    # the intro: clothed, standing where the head position goes, facing each other
    g0, c0 = head["girl"], head["cloud"]
    for ent, model, sp, other in (("cloudA", 1, c0, g0), ("tifaA", 2, g0, c0)):
        scripts[E[ent]] = {0: [Op(bytes([0xA1, model]))] + at(sp, dt._dir_to(other[0] - sp[0], other[1] - sp[1])) +
                           [hb._visi(1)] + hide() + loop_(0) + [asm.ret(), asm.ret()],
                           4: [hb._visi(0), asm.ret()]}
    ci = lambda n: 1 + bare_c.index(n)
    ti_ = lambda n: 1 + bare_t.index(n)
    stroke = lambda names_: ch_(TIER, [loop_(i) for i in names_])
    # the actors: 2 placed by SEG, the tier's stroke; 3 placed and still (the pause pose); 4 hidden; 5 the
    # hold (deep); Tifa 6 her tap-out squirm; 7 the wiggle (Cloud) / pulled back (Tifa); 8 the taste
    scripts[E["cloudB"]] = {
        0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(SEG, [at(p["cloud"], p["cdir"]) + stroke([ci(n) for n in stroke_c[k]]) for k, p in enumerate(P)]) +
        [hb._visi(1), asm.ret()],
        3: ch_(SEG, [at(p["cloud"], p["cdir"]) + loop_(ci(pause_c[k])) for k, p in enumerate(P)]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ci("ZNJ8.tor")) + [asm.ret()],
        7: [mv._animb(), Op(bytes([0xA2, ci("ZNJ0.tor"), 1])), Op(bytes([0xA3, ci(wig), 1])), asm.ret()],
        8: loop_(ci(taste_c)) + [asm.ret()]}
    scripts[E["tifaB"]] = {
        0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(SEG, [at(p["girl"], p["gdir"]) + stroke([ti_(n) for n in stroke_t[k]]) for k, p in enumerate(P)]) +
        [hb._visi(1), asm.ret()],
        3: ch_(SEG, [at(p["girl"], p["gdir"]) + loop_(ti_(pause_t[k])) for k, p in enumerate(P)]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ti_("ZVJ8.tor")) + [asm.ret()],
        6: loop_(ti_("ZVJ7.tor")) + [asm.ret()],
        7: loop_(ti_("ZVJ9.tor")) + [asm.ret()],
        8: loop_(ti_(taste_t)) + [asm.ret()]}
    # the Director on each position's cameraman spot (670's), still in the intro, filming from the first one
    scripts[E["drctr"]] = {
        0: [Op(bytes([0xA1, 5]))] + at(head["cam"], head["camdir"]) + [hb._visi(1)] + hide() + loop_(still) +
        [asm.ret(), asm.ret()],
        2: ch_(SEG, [at(p["cam"], p["camdir"]) for p in P]) + loop_(film) + [asm.ret()]}
    # the buttons: one small entity each; a press = up -> down (PR = its number), HELD bit k while held
    for k, (mask, _) in enumerate(TU.KEYS):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    # the prompts: window 1 (the director closes it)
    pr = {0: [asm.ret(), asm.ret()]}
    for j, (_, label) in enumerate(TU.KEYS):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, 30, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    sc_ = DG.scripts(meter, METER, xyzi, view=SEG)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    MG_ = (E["gauge"], E["cursor"])

    # the director
    say = lambda t: hb._say(sec, t)
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    actors = ("cloudB", "tifaB")
    restart = [req(E[a], 2) for a in actors]
    stop = [req(E[a], 3) for a in actors]
    pay = asm.nop()
    red, red_ops = DG.cut(say, MG_, pay, fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20)])
    main = [hb._uc(1), hb._menu(1), asm.setbyte(SEG, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, TU.MUSIC]) + bytes(8))]
    for t in TU.INTRO:
        main += say(t)
    main += fade_out + [hb._req(E[a], 4) for a in ("cloudA", "tifaA")] + [hb._req(E[a], 3) for a in actors] + \
        [req(E["drctr"], 2), hb._w(20)] + fade_in
    main += say(TU.HOW)
    main += [asm.setword(PAY, 0), asm.setbyte(HELD, 0)] + DG.start(METER, MG_)
    n = len(TU.PERIODS)
    for s, sg in enumerate(TU.SEGMENTS):
        assert sg["key"] == SEGS[s]
        if s:
            main += fade_out + [asm.setbyte(SEG, s)] + [hb._req(E[a], 3) for a in actors] + \
                [hb._req(E["cloud"], 2), req(E["drctr"], 2)] + [req(e, 2) for e in MG_] + [hb._w(20)] + fade_in
        for t in sg["setup"]:
            main += say(t)
        main += [asm.setbyte(REPN, 0), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + restart
        rep, wait, judge, hit, miss, tail, after, rest = (asm.nop() for _ in range(8))
        main += [rep] + ch_(TIER, [[asm.setword(PER, p_)] for p_ in TU.PERIODS])
        main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])), asm.setbyte(KEY, RND),
                 asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0), asm.setword(CNT, 0)]
        main += ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)])
        main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
                 asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait),
                 judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss)]
        main += [hit] + DG.hit(METER, E["cursor"]) + [Op(TU.HIT_SOUND), hb._arith(0x86, PAY, TIER),
                 Op(bytes([0x96, PAY[0], PAY[1]])), Op(bytes([0x95, STREAK[0], STREAK[1]])),
                 asm.if_byte(TIER, "<", n - 1, after), asm.if_byte(STREAK, ">=", TU.HITS_UP, after),
                 Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)] + restart
        main += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                 asm.goto_back(rest), tail, Op(bytes([0x95, REPN[0], REPN[1]]))]
        # the beats
        for r, kind, *texts in sg["beats"]:
            nb = asm.nop()
            main += [asm.if_byte(REPN, "==", r, nb), Op(b"\x54\x01")]
            if kind == "talk":
                main += sum((say(t) for t in texts[0]), [])
            elif kind in ("pause", "there"):
                main += stop + sum((say(t) for t in texts[0]), []) + restart
            elif kind == "hold":                                            # (head) the hold, demonstrated
                main += [req(E["cloudB"], 5), req(E["tifaB"], 5)] + sum((say(t) for t in texts[0]), []) + \
                    [req(E["tifaB"], 6)] + sum((say(t) for t in texts[1]), []) + \
                    [req(E["tifaB"], 7), hb._req(E["cloudB"], 7)] + sum((say(t) for t in texts[2]), []) + restart
            elif kind == "taste":                                           # (all fours) the taste
                main += stop + sum((say(t) for t in texts[0][:2]), []) + \
                    [req(E["cloudB"], 8), req(E["tifaB"], 8), hb._w(20)] + \
                    sum((say(t) for t in texts[0][2:]), []) + restart
            else:
                raise AssertionError(kind)
            main += [nb]
        done = asm.nop()
        main += [asm.if_byte(REPN, "<", sg["reps"], done), asm.goto_back(rep), done]
        # a miss: the buzz, the meter, back to the slowest pace, the rest of the rep
        skip, mtail, mdone, slow = asm.nop(), asm.nop(), asm.nop(), asm.nop()
        main += [asm.goto(skip), miss, Op(b"\x54\x01"), buzz] + DG.miss(METER, SIDE, RND, E["cursor"], red) + \
            [asm.if_byte(TIER, "!=", 0, slow), asm.setbyte(TIER, 0)] + restart + [slow, asm.setbyte(STREAK, 0),
             mtail, asm.if_word(CNT, "<", PER, mdone), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.goto_back(mtail), mdone, asm.goto_back(tail), skip]
    # the finisher, explained while doing it (10 s)
    main += [asm.setbyte(TIER, n - 1)] + restart
    for t in TU.FINISH_TALK:
        main += say(t)
    main += DG.finale(say, METER, PR, 3, CNT, DEC, MG_, PAY, hb._arith, frames=TU.FINISH_FRAMES,
                      call=TU.FINISH_CALL, win_lines=TU.FINISH_WIN)
    main += stop
    for t in TU.OUTRO:
        main += say(t)
    main += fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20), asm.goto(pay)] + red_ops
    main += [pay, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, TU.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(TU.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))       # MPRA2 after WINDOW
    main += paid
    rx, ry, rz, rt, rdir = ctx.movie_back
    stop_ = hb._w(30)
    main += [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir),
             stop_, asm.goto_back(stop_)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  688: The Basics on %s (head / dog / 69 at 670's spots %s; taste gap %.2f; %d texts, script %d bytes)"
          % (TU.FIELD, [(p["girl"][:3], p["gdir"], p["cloud"][:3], p["cdir"]) for p in P], gap, n_text,
             len(f.sections[0])))

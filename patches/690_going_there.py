"""(user) Going There: the Director's second tutorial-style film (data `_going_there.py`, poses `_going_there_poses.py`),
in the Director's film menu after Besties. Set FIELD (a debug room only startmap leads to) = a copy of Corneo's
bedroom colne_6 (672's special-scene set: its background-state entities keep their init, everything else
blanked, gateways cleared). The Director reminds Tifa of the contract and her preparation, then three positions
with the special scenes' poses (672, Tifa's ZV.. retargeted copies, Cloud's ZN..): "ride" (672's finisher R on
the bed, taken slow), "head" (Q on the floor in front of the bed: her gag, Cloud's dirty talk lessons, then the
top speed), "mount" (the insert P on the bed, in three of Cloud's mounts by STY: 672's front ZNP, side-on with
his foot on her head XGS, the reverse plank XGT flopping his hips). The prompt game, the beats, the danger meter
and the finisher as 688. Checked on offline renders only, untested in-game."""
import importlib
import struct

import _danger as DG
import _going_there as GT
import _going_there_poses as GP
import _tickets_poses as TP
from ff7 import asm
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

TIER, STREAK, KEY, PR, SEG, RND, KP, REPN, HELD, METER, SIDE, DEC, STY, VIEW = ((5, a) for a in range(100, 114))
PRV = [(5, 114 + k) for k in range(3)]
CNT, PER, PAY, GIL = ((6, a) for a in range(120, 128, 2))
SEGS = ("ride", "head", "mount")
TIFA_DONOR = ("bwhlin", 3)              # AAGB, stand ABCD
BARE_TIFA = "ZTFA.HRC"
KEEP = ("switch", "hole", "ball", "bed")    # (672) colne_6's background-state entities


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates"), importlib.import_module("672_movie_special")


def apply(ctx):
    mv, hb, dt, sp = _mods()
    ctx.field(GT.FIELD)
    ctx.field(GT.BASE)
    f = ctx._fields[GT.FIELD] = FieldFile(ctx._orig_raw[GT.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    old = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    keep = [sec.script_ops(old.index(n), 0) for n in KEEP]
    for ops in keep:
        assert ops[-1].op == 0x00 and not any(o.op == 0xA1 for o in ops)
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    spot = lambda x, y: tuple(round(v) for v in mv._spot(mesh, x, y, 0, True))
    bed = spot(*sp.BED_AT[:2])
    hg, hc = spot(*sp.HEAD_GIRL[:2]), spot(*sp.HEAD_CLOUD[:2])
    assert bed[2] > -200 and abs(hg[2] + 237) < 1 and abs(hc[2] + 237) < 1, (bed, hg, hc)
    BD = sp.BED_AT[2]
    cam = {k: spot(*v) for k, v in sp.CAM_AT.items()}
    to = lambda a, b: dt._dir_to(b[0] - a[0], b[1] - a[1])
    # anims
    nper = list(sp.SP.INSERT_FRAMES)
    mounts, mstill, errs = GP.build(ctx, hb, bed, BD, nper)
    assert max(errs.values()) < 0.6, errs
    c_str = {"ride": ["ZNR%d.tor" % s for s in range(4)], "head": ["ZNQ%d.tor" % s for s in range(4)],
             "front": ["ZNP%d.tor" % s for s in range(4)], "side": mounts["side"], "plank": mounts["plank"]}
    t_str = {k: ["ZV%s%d.tor" % (L, s) for s in range(4)] for k, L in (("ride", "R"), ("head", "Q"), ("mount", "P"))}
    c_still = {"ride": TP.still(ctx, "ZNR0", "XGR9"), "head": "ZNQ9.tor", "front": TP.still(ctx, "ZNP0", "XGP9"),
               "side": mstill["side"], "plank": mstill["plank"]}
    t_still = {"ride": TP.still(ctx, "ZVR0", "XHR9"), "head": "ZVQ9.tor", "mount": TP.still(ctx, "ZVP0", "XHP9")}
    bare_c = sum(c_str.values(), []) + list(c_still.values()) + ["ZNQ8.tor"]
    bare_t = sum(t_str.values(), []) + list(t_still.values()) + ["ZVQ8.tor", "ZVQ7.tor"]
    for n in bare_c + bare_t:
        ctx.char_file(n.split(".")[0].lower() + ".a")                       # (exists)
    # models: 0 the hidden player, 1 / 2 clothed Cloud / Tifa (intro), 3 / 4 bare, 5 the Director, 6 / 7 the meter
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.name(cl0).endswith("main_n_cloud.char")
    c_anims = ModelLoader.anims(cl0)
    ti = loader.add_from(ModelLoader(ctx.field(TIFA_DONOR[0]).section("models")), TIFA_DONOR[1])
    tifa_e = loader.models[ti]
    t_anims = ModelLoader.anims(tifa_e)
    loader.models = [ModelLoader.only_anims(cl0, c_anims[:1]), ModelLoader.only_anims(cl0, c_anims[:2]),
                     ModelLoader.only_anims(tifa_e, t_anims[:2]),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "gothere_cloudb.char"),
                                            c_anims[:1] + bare_c),
                     ModelLoader.only_anims(ModelLoader.with_hrc(tifa_e, BARE_TIFA, "gothere_tifab.char"),
                                            t_anims[:1] + bare_t)]
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    cam_anims = ModelLoader.anims(loader.models[cm])
    film = cam_anims.index(mv.CAMERA_FILM)
    loader.models[cm] = ModelLoader.only_anims(loader.models[cm], cam_anims + [mv.CAMERA_STILL])
    still = len(cam_anims)
    meter = DG.build(ctx, f, loader, "S", [bed[:3], hg[:3]])
    assert len(loader.models) == 8 and all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    # entities
    names = ["dir"] + list(KEEP) + ["cloud", "cloudA", "tifaA", "cloudB", "tifaB", "drctr", "k_sw", "k_ca", "k_ok",
                                    "prompt", "gauge", "cursor"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch_ = mv._chain
    at = lambda p, d: [xyzi(*p[:4]), d_(d)]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))
    scripts = {E[n]: {0: ops} for n, ops in zip(KEEP, keep)}
    focus = [bed, hg, bed]
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at(spot(*GT.ARRIVE), 0) + [hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()],
                           2: ch_(SEG, [at(fc, 0) for fc in focus]) + [asm.ret()]}
    sc, sg = spot(*GT.START["C"]), spot(*GT.START["G"])
    for ent, model, p, other in (("cloudA", 1, sc, sg), ("tifaA", 2, sg, sc)):
        scripts[E[ent]] = {0: [Op(bytes([0xA1, model]))] + at(p, to(p, other)) + [hb._visi(1)] + hide() + loop_(0) +
                           [asm.ret(), asm.ret()],
                           4: [hb._visi(0), asm.ret()]}
    ci = lambda n: 1 + bare_c.index(n)
    ti_ = lambda n: 1 + bare_t.index(n)
    stroke = lambda ns: ch_(TIER, [loop_(i) for i in ns])
    MDIR = {"front": BD, "side": GP.DIRS["side"], "plank": GP.DIRS["plank"]}

    def cloud_seg(pick):
        return ch_(SEG, [at(bed, BD) + pick("ride"), at(hc, sp.HEAD_CLOUD[2]) + pick("head"),
                         ch_(STY, [at(bed, MDIR[m]) + pick(m) for m in ("front", "side", "plank")])])
    scripts[E["cloudB"]] = {
        0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: cloud_seg(lambda k: stroke([ci(n) for n in c_str[k]])) + [hb._visi(1), asm.ret()],
        3: cloud_seg(lambda k: loop_(ci(c_still[k]))) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ci("ZNQ8.tor")) + [asm.ret()]}
    tifa_seg = lambda pick: ch_(SEG, [at(bed, BD) + pick("ride"), at(hg, sp.HEAD_GIRL[2]) + pick("head"),
                                      at(bed, BD) + pick("mount")])
    scripts[E["tifaB"]] = {
        0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: tifa_seg(lambda k: stroke([ti_(n) for n in t_str[k]])) + [hb._visi(1), asm.ret()],
        3: tifa_seg(lambda k: loop_(ti_(t_still[k]))) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ti_("ZVQ8.tor")) + [asm.ret()],
        6: loop_(ti_("ZVQ7.tor")) + [asm.ret()]}
    ic = spot(*sp.INTRO_AT["cam"])
    cams = [cam["finisher"], cam["head"], cam["insert"]]
    looks = [bed, hg, bed]
    scripts[E["drctr"]] = {
        0: [Op(bytes([0xA1, 5]))] + at(ic, to(ic, sg)) + [hb._visi(1)] + hide() + loop_(still) + [asm.ret(), asm.ret()],
        2: ch_(SEG, [at(c, to(c, l)) for c, l in zip(cams, looks)]) + loop_(film) + [asm.ret()]}
    for k, (mask, _) in enumerate(GT.KEYS):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    pr = {0: [asm.ret(), asm.ret()]}
    for j, (_, label) in enumerate(GT.KEYS):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, 30, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    sc_ = DG.scripts(meter, METER, xyzi, view=VIEW)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    MG_ = (E["gauge"], E["cursor"])

    # the director
    say = lambda t: hb._say(sec, t)
    lines = lambda ts: sum((say(t) for t in ts), [])
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    actors = ("cloudB", "tifaB")
    restart = [req(E[a], 2) for a in actors]
    stop = [req(E[a], 3) for a in actors]
    pay = asm.nop()
    red, red_ops = DG.cut(say, MG_, pay, fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20)])
    view = lambda s: [asm.setbyte(VIEW, 1 if SEGS[s] == "head" else 0)]
    main = [hb._uc(1), hb._menu(1), asm.setbyte(SEG, 0), asm.setbyte(STY, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, GT.MUSIC]) + bytes(8))]
    main += lines(GT.INTRO)
    main += fade_out + [hb._req(E[a], 4) for a in ("cloudA", "tifaA")] + [hb._req(E[a], 3) for a in actors] + \
        [hb._req(E["cloud"], 2), req(E["drctr"], 2), hb._w(20)] + fade_in
    main += say(GT.HOW)
    main += [asm.setword(PAY, 0), asm.setbyte(HELD, 0)] + view(0) + DG.start(METER, MG_)
    n = len(GT.PERIODS)
    for s, sg_ in enumerate(GT.SEGMENTS):
        assert sg_["key"] == SEGS[s]
        if s:
            main += fade_out + [asm.setbyte(SEG, s)] + view(s) + [hb._req(E[a], 3) for a in actors] + \
                [hb._req(E["cloud"], 2), req(E["drctr"], 2)] + [req(e, 2) for e in MG_] + [hb._w(20)] + fade_in
        main += lines(sg_["setup"])
        main += [asm.setbyte(REPN, 0), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + restart
        rep, wait, judge, hit, miss, tail, after, rest = (asm.nop() for _ in range(8))
        main += [rep] + ch_(TIER, [[asm.setword(PER, p_)] for p_ in GT.PERIODS])
        main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])), asm.setbyte(KEY, RND),
                 asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0), asm.setword(CNT, 0)]
        main += ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)])
        main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
                 asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait),
                 judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss)]
        main += [hit] + DG.hit(METER, E["cursor"]) + [Op(GT.HIT_SOUND), hb._arith(0x86, PAY, TIER),
                 Op(bytes([0x96, PAY[0], PAY[1]])), Op(bytes([0x95, STREAK[0], STREAK[1]])),
                 asm.if_byte(TIER, "<", n - 1, after), asm.if_byte(STREAK, ">=", GT.HITS_UP, after),
                 Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)] + restart
        main += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                 asm.goto_back(rest), tail, Op(bytes([0x95, REPN[0], REPN[1]]))]
        for r, kind, texts in sg_["beats"]:
            nb = asm.nop()
            main += [asm.if_byte(REPN, "==", r, nb), Op(b"\x54\x01")]
            if kind == "talk":
                main += lines(texts)
            elif kind == "pause":
                main += stop + lines(texts) + restart
            elif kind == "gag":                                             # (head) the gag: deep, she pulls back
                main += [req(E["cloudB"], 5), req(E["tifaB"], 5), hb._w(25), req(E["tifaB"], 6), hb._w(30)] + \
                    stop + lines(texts) + restart
            elif kind == "frenzy":                                          # (head) then the top speed
                main += stop + lines(texts) + [asm.setbyte(TIER, n - 1), asm.setbyte(STREAK, 0)] + restart
            elif kind == "mount":                                           # (mount) his next mount
                main += fade_out + [Op(bytes([0x95, STY[0], STY[1]]))] + stop + [hb._w(15)] + fade_in + \
                    lines(texts) + restart
            else:
                raise AssertionError(kind)
            main += [nb]
        done = asm.nop()
        main += [asm.if_byte(REPN, "<", sg_["reps"], done), asm.goto_back(rep), done]
        if sg_["after"]:
            main += stop + lines(sg_["after"])
        skip, mtail, mdone, slow = asm.nop(), asm.nop(), asm.nop(), asm.nop()
        main += [asm.goto(skip), miss, Op(b"\x54\x01"), buzz] + DG.miss(METER, SIDE, RND, E["cursor"], red) + \
            [asm.if_byte(TIER, "!=", 0, slow), asm.setbyte(TIER, 0)] + restart + [slow, asm.setbyte(STREAK, 0),
             mtail, asm.if_word(CNT, "<", PER, mdone), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.goto_back(mtail), mdone, asm.goto_back(tail), skip]
    main += [asm.setbyte(TIER, n - 1)] + restart
    main += DG.finale(say, METER, PR, 3, CNT, DEC, MG_, PAY, hb._arith, frames=GT.FINISH_FRAMES,
                      call=GT.FINISH_CALL, win_lines=GT.FINISH_WIN)
    main += stop + lines(GT.OUTRO)
    main += fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20), asm.goto(pay)] + red_ops
    main += [pay, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, GT.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(GT.PAID)
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
    print("  690: Going There on %s (bed %s, head %s / %s; mount fits %s; %d texts, script %d bytes)"
          % (GT.FIELD, bed[:3], hg[:3], hc[:3], {k: round(v, 2) for k, v in errs.items()}, n_text, len(f.sections[0])))

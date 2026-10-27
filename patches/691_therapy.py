"""(user) Therapy Session (data `_therapy.py`), in the Director's film menu after Going There: set FIELD (a debug room
only startmap leads to) = a copy of Junon's doctor's office junbin3 (the couch in the middle is a walkable piece at
z 210; the room is at scale 2048, every model and field offset 4x a 512 room's: `K`), script blanked but the door
and window background states (its own DOOR / WINDOW inits), gateways cleared. No therapist (user): the two of
them on the couch (sitting: 660 `_ledge`, clothed XQCS / XQTS, then bare XQCB / XQTB), taking turns: Cloud's
reveal, then his scene (670's prone F: Tifa ZVF, Cloud ZNF), back on the couch, Tifa's reveal, her scene (670's
cowgirl B), the finisher. Both scenes on the couch, 670's relative layout (`ctx.movie_places`) turned onto it
(`ROT`) and scaled by K. The prompt game, beats and danger meter as 688 / 690. Checked on offline renders only,
untested in-game."""
import importlib
import math
import struct

import _danger as DG
import _therapy as TH
import _tickets_poses as TP
from ff7 import asm
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

TIER, STREAK, KEY, PR, SEG, RND, KP, REPN, HELD, METER, SIDE, DEC, SITB = ((5, a) for a in range(100, 113))
PRV = [(5, 114 + k) for k in range(3)]
CNT, PER, PAY, GIL = ((6, a) for a in range(120, 128, 2))
BARE_TIFA = "ZTFA.HRC"
KEEP = ("DOOR", "WINDOW")       # junbin3's background-state entities: their init stays
ROT = {"prone": 64, "cowgirl": 64}      # 670's beds run along y, the couch along x


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _layout(ctx, mv, mesh, K):
    """{position: (girl spot, girl dir, his spot, his dir)} on the couch: 670's relative layout in mds7_w3 (both
    on a bed), turned by ROT, scaled by K, centred on the couch, heights above the couch top x K."""
    src = Walkmesh(ctx.field("mds7_w3").section("walkmesh"))
    top = lambda x, y: max(src.height(t, x, y) for t in range(len(src.tris)) if src.contains(t, x, y))
    names = [p["name"] for p in mv.POSITIONS]
    out = {}
    for pos, rot in ROT.items():
        p = ctx.movie_places[names.index(pos)]
        g, c = p["girl"], p["cloud"]
        a = rot * 2 * math.pi / 256
        dx, dy = c[0] - g[0], c[1] - g[1]
        rx, ry = (dx * math.cos(a) - dy * math.sin(a)) * K, (dx * math.sin(a) + dy * math.cos(a)) * K
        G = (TH.COUCH[0] - rx / 2, TH.COUCH[1] - ry / 2)
        C = (TH.COUCH[0] + rx / 2, TH.COUCH[1] + ry / 2)
        spots = []
        for (x, y), q in ((G, g), (C, c)):
            ts = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y)]
            t = max(ts, key=lambda t: mesh.height(t, x, y))
            assert mesh.height(t, x, y) > 200, ("on the couch", pos, x, y)
            spots.append((round(x), round(y), round(mesh.height(t, x, y) + (q[2] - top(q[0], q[1])) * K), t))
        out[pos] = (spots[0], (p["gdir"] + rot) % 256, spots[1], (p["cdir"] + rot) % 256)
    return out


def apply(ctx):
    mv, hb, dt = _mods()
    ctx.field(TH.FIELD)
    ctx.field(TH.BASE)
    f = ctx._fields[TH.FIELD] = FieldFile(ctx._orig_raw[TH.BASE])
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
    loader = ModelLoader(f.section("models"))
    K = loader.scale / 512
    lay = _layout(ctx, mv, mesh, K)

    def seat(x, y):
        ts = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y)]
        t = max(ts, key=lambda t: mesh.height(t, x, y))
        return x, y, round(mesh.height(t, x, y)), t
    seats = {w: seat(TH.SEAT_X[w], TH.SEAT_Y) for w in "CG"}
    assert all(s[2] > 200 for s in seats.values()), seats
    front = 0x00                                                             # facing -y: the camera
    fl = mesh.find(*TH.ARRIVE)
    assert fl is not None
    focus = (TH.COUCH[0], TH.COUCH[1], 210, mesh.find(*TH.COUCH))
    # anims
    letter = {p["name"]: chr(ord("A") + i) for i, p in enumerate(mv.POSITIONS)}
    c_str = {t["pos"]: ["ZN%s%d.tor" % (letter[t["pos"]], s) for s in range(4)] for t in TH.TURNS}
    t_str = {t["pos"]: ["ZV%s%d.tor" % (letter[t["pos"]], s) for s in range(4)] for t in TH.TURNS}
    c_still = {p: TP.still(ctx, c_str[p][0].split(".")[0], "XQC%s" % letter[p]) for p in c_str}
    t_still = {p: TP.still(ctx, t_str[p][0].split(".")[0], "XQT%s" % letter[p]) for p in t_str}
    sit_c, sit_t = "XQCS.tor", "XQTS.tor"
    dt._ledge(ctx, sit_c, "aaaa.hrc", "acfe.a")
    dt._ledge(ctx, sit_t, "aagb.hrc", "abcd.a")
    sit_cb, sit_tb = "XQCB.tor", "XQTB.tor"
    dt._ledge(ctx, sit_cb, hb.CLOUD_BARE_HRC.lower(), "acfe.a")
    dt._ledge(ctx, sit_tb, BARE_TIFA.lower(), "abcd.a")
    bare_c = sum(c_str.values(), []) + list(c_still.values()) + [sit_cb]
    bare_t = sum(t_str.values(), []) + list(t_still.values()) + [sit_tb]
    for n in bare_c + bare_t:
        ctx.char_file(n.split(".")[0].lower() + ".a")                       # (exists)
    # models: 0 the hidden player, 1 / 2 clothed Cloud / Tifa, 3 / 4 bare, 5 / 6 the meter
    cl0, ti0 = loader.models[0], loader.models[1]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC" and ModelLoader.hrc(ti0) == "AAGB.HRC"
    c_anims, t_anims = ModelLoader.anims(cl0), ModelLoader.anims(ti0)
    loader.models = [ModelLoader.only_anims(cl0, c_anims[:1]),
                     ModelLoader.only_anims(cl0, c_anims[:1] + [sit_c]),
                     ModelLoader.only_anims(ti0, t_anims[:1] + [sit_t]),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "therapy_cloudb.char"),
                                            c_anims[:1] + bare_c),
                     ModelLoader.only_anims(ModelLoader.with_hrc(ti0, BARE_TIFA, "therapy_tifab.char"),
                                            t_anims[:1] + bare_t)]
    meter = DG.build(ctx, f, loader, "T", focus[:3])
    assert len(loader.models) == 7 and all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    # entities
    names = ["dir"] + list(KEEP) + ["cloud", "cloudA", "tifaA", "cloudB", "tifaB", "k_sw", "k_ca", "k_ok",
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
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at(focus, 0) + [hb._visi(0)] + hide() +
                           [asm.ret(), asm.ret()]}
    # the clothed pair on the couch's edge (4 hides)
    for ent, model, w in (("cloudA", 1, "C"), ("tifaA", 2, "G")):
        scripts[E[ent]] = {0: [Op(bytes([0xA1, model]))] + at(seats[w], front) + [hb._visi(1)] + hide() + loop_(1) +
                           [asm.ret(), asm.ret()],
                           4: [hb._visi(0), asm.ret()]}
    ci = lambda n: 1 + bare_c.index(n)
    ti_ = lambda n: 1 + bare_t.index(n)
    stroke = lambda ns: ch_(TIER, [loop_(i) for i in ns])
    order = [t["pos"] for t in TH.TURNS]
    # the bare pair: 2 the stroke (by SEG), 3 still, 4 hidden, 6 sitting on the couch
    for ent, model, who, strs, stills, sit, w in (("cloudB", 3, 2, c_str, c_still, sit_cb, "C"),
                                                  ("tifaB", 4, 0, t_str, t_still, sit_tb, "G")):
        ix = ci if ent == "cloudB" else ti_
        scripts[E[ent]] = {
            0: [Op(bytes([0xA1, model])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
            2: ch_(SEG, [at(lay[p][who], lay[p][who + 1]) + stroke([ix(n) for n in strs[p]]) for p in order]) +
            [hb._visi(1), asm.ret()],
            3: ch_(SEG, [at(lay[p][who], lay[p][who + 1]) + loop_(ix(stills[p])) for p in order]) + [hb._visi(1), asm.ret()],
            4: [hb._visi(0), asm.ret()],
            6: at(seats[w], front) + loop_(ix(sit)) + [hb._visi(1), asm.ret()]}
    for k, (mask, _) in enumerate(TH.KEYS):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    pr = {0: [asm.ret(), asm.ret()]}
    for j, (_, label) in enumerate(TH.KEYS):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, 30, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    sc_ = DG.scripts(meter, METER, xyzi)
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
    main = [hb._uc(1), hb._menu(1), asm.setbyte(SEG, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, TH.MUSIC]) + bytes(8))]
    main += lines(TH.INTRO)
    main += [asm.setword(PAY, 0), asm.setbyte(HELD, 0)]
    n = len(TH.PERIODS)
    for s, tn in enumerate(TH.TURNS):
        main += lines(tn["reveal"])
        main += fade_out + [asm.setbyte(SEG, s)] + [hb._req(E[a], 4) for a in ("cloudA", "tifaA")] + \
            [hb._req(E[a], 3) for a in actors] + [hb._w(20)] + fade_in
        if s == 0:
            main += say(TH.HOW)
        main += DG.start(METER, MG_) if s == 0 else [req(e, 2) for e in MG_]
        main += lines(tn["setup"])
        main += [asm.setbyte(REPN, 0), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + restart
        rep, wait, judge, hit, miss, tail, after, rest = (asm.nop() for _ in range(8))
        main += [rep] + ch_(TIER, [[asm.setword(PER, p_)] for p_ in TH.PERIODS])
        main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])), asm.setbyte(KEY, RND),
                 asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0), asm.setword(CNT, 0)]
        main += ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)])
        main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
                 asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait),
                 judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss)]
        main += [hit] + DG.hit(METER, E["cursor"]) + [Op(TH.HIT_SOUND), hb._arith(0x86, PAY, TIER),
                 Op(bytes([0x96, PAY[0], PAY[1]])), Op(bytes([0x95, STREAK[0], STREAK[1]])),
                 asm.if_byte(TIER, "<", n - 1, after), asm.if_byte(STREAK, ">=", TH.HITS_UP, after),
                 Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)] + restart
        main += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                 asm.goto_back(rest), tail, Op(bytes([0x95, REPN[0], REPN[1]]))]
        for r, kind, texts in tn["beats"]:
            nb = asm.nop()
            main += [asm.if_byte(REPN, "==", r, nb), Op(b"\x54\x01")]
            if kind == "talk":
                main += lines(texts)
            elif kind == "pause":
                main += stop + lines(texts) + restart
            else:
                raise AssertionError(kind)
            main += [nb]
        done = asm.nop()
        main += [asm.if_byte(REPN, "<", tn["reps"], done), asm.goto_back(rep), done]
        if s == len(TH.TURNS) - 1:                                          # her finisher
            main += [asm.setbyte(TIER, n - 1)] + restart
            main += DG.finale(say, METER, PR, 3, CNT, DEC, MG_, PAY, hb._arith, frames=TH.FINISH_FRAMES,
                              call=TH.FINISH_CALL, win_lines=TH.FINISH_WIN)
        else:
            main += DG.hide(MG_)
        main += stop + lines(tn["after"])
        main += fade_out + [hb._req(E[a], 6) for a in actors] + [hb._w(15)] + fade_in   # back on the couch
        skip, mtail, mdone, slow = asm.nop(), asm.nop(), asm.nop(), asm.nop()
        main += [asm.goto(skip), miss, Op(b"\x54\x01"), buzz] + DG.miss(METER, SIDE, RND, E["cursor"], red) + \
            [asm.if_byte(TIER, "!=", 0, slow), asm.setbyte(TIER, 0)] + restart + [slow, asm.setbyte(STREAK, 0),
             mtail, asm.if_word(CNT, "<", PER, mdone), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.goto_back(mtail), mdone, asm.goto_back(tail), skip]
    main += lines(TH.OUTRO)
    main += fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20), asm.goto(pay)] + red_ops
    main += [pay, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, TH.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(TH.PAID)
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
    print("  691: Therapy Session on %s (seats %s; layout %s; %d texts, script %d bytes)"
          % (TH.FIELD, seats, {p: (v[0][:3], v[1], v[2][:3], v[3]) for p, v in lay.items()}, n_text,
             len(f.sections[0])))

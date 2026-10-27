"""(user) Tifa's aerobics classes (data `_aerobics.py`, moves `_aerobic_poses.py`; replaces the gym's one-on-one
sessions with Wedge / Biggs / Jessie): Tifa in the Wall Market gym (mkt_mens, added at `TIFA_AT`) offers
"Run a class." -> FIELD (a debug room only startmap leads to) = a copy of the Junon dock (jundoc1a: the send-off
drill for Rufus in front of the cargo ship; user: closer, lower angles than the gym), script blanked, gateways
cleared.

The class: five classmates picked at random from `POOL` (each its own entity, placed on a slot `SLOTS` by the
director's pick: SL (5,120+m) = slot + 1, 0 = not in today's class, hidden), Tifa out front, everyone facing the
camera, in colourful spandex (`_girl` / `_man`), all doing the same moves (`_aerobic_poses.build` on each model)
started together by the director (M (5,101) = the anim; every dancer's slot 3). The routine `ROUTINE`: Tifa calls
each move (window 2, closing itself), one button prompt a move cycle (window 1; four buttons, one polling entity
each), a hit = the squat sound, a miss = the buzz and a classmate's flub; `COMBO` hits in a row = a cheer and a tip.
At the end the finish pose, Tifa's grade line, a classmate's reaction, the patrons' pay (GOLDU), "Another class?"

Checked on offline renders only (layout, moves, outfits), untested in-game."""
import importlib
import math
import struct

import _aerobic_poses as AP
import _aerobics as AE
import _female_body as fb
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import facing_screen, Camera
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

M, KEY, PR, KP, RND, STREAK, USED, K, TALKING, LN, GRADE = ((5, a) for a in range(100, 111))
PRV = [(5, 111 + k) for k in range(4)]
ROUND = (5, 115)                                 # 0 = the first class of the visit (the intro)
SL = [(5, 120 + m) for m in range(len(AE.POOL))]
CNT, HITS, PAY, CY, GIL = ((6, a) for a in range(130, 140, 2))
TIFA_SRC = ("blue_2", 1)                         # (her AAGB entry; the spandex XWTA is 683's)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates"), importlib.import_module("682_school_dance"), \
        importlib.import_module("683_workout")


# ---- the outfits ---------------------------------------------------------------------------------------------
def _girl(ctx, g, text):
    """Her spandex .hrc text: the standard body (her head and feet), a scoop-neck leotard, tights, leg warmers."""
    mv, hb, dt, sd, wo = _mods()
    skin = fb.face_skin(ctx, text)
    hrc = fb.apply(ctx, text, g["tag"], skin, None, 1.0, 0.0)
    if "armer" in fb.bones(hrc):
        lines = hrc.splitlines(True)
        k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "armer")
        lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), "0")
        hrc = "".join(lines)
    top = g["top"]
    chest = ([([0.0, 0.0, 1.0], wo.NECK_Z)], lambda c: skin if c[2] < wo.NECK_Z else top)
    fb.tifa_body(ctx, hrc, skin, g["bust"], paints={"chest": chest, "hip": ([], lambda c: top)})
    bn = fb.bones(hrc)
    for b, col in [("l_femur", g["tights"]), ("r_femur", g["tights"]), ("l_tibia", g["warmers"]),
                   ("r_tibia", g["warmers"])]:
        p = sd._ply(ctx, bn[b][1][0])
        ctx.char_file(p, sd._recolour(ctx.char_file(p), col))
    return hrc


MAN_BONES = {"chest": "top", "l_chest": "top", "r_chest": "top", "l_collar": "top", "r_collar": "top",
             "l_uparm": "top", "r_uparm": "top", "l_foarm": "top", "r_foarm": "top",
             "hip": "tights", "l_hip": "tights", "r_hip": "tights", "l_femur": "tights", "r_femur": "tights",
             "l_tibia": "warmers", "r_tibia": "warmers", "l_foot": "shoes", "r_foot": "shoes"}
SKIN_NEAR = 70                   # a colour this close (sum of |B|+|G|+|R| differences) to his face's skin stays


def _respray(d, col, skin, near=None):
    """.p bytes d with every vertex / polygon colour that isn't skin-like set to col."""
    d = bytearray(d)
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nu, nt, nc, npoly = h[3], h[4], h[5], h[6], h[7], h[9]
    oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
    for o in [oc + 4 * i for i in range(nc)] + [oc + 4 * nc + 4 * j for j in range(npoly)]:
        if sum(abs(d[o + k] - skin[k]) for k in range(3)) > (near or SKIN_NEAR):
            d[o:o + 3] = bytes(col)
    return bytes(d)


def _man(ctx, g, text):
    """His spandex .hrc text: his own parts, every non-skin colour on his body resprayed (tank top / long sleeves,
    tights, leg warmers, sneakers), as new parts XR<tag><n> (.rsd) -> XP<tag><n> (.p): his own files are shared
    by every field."""
    mv, hb, dt, sd, wo = _mods()
    skin = g.get("skin") or fb.face_skin(ctx, text)
    cols = dict(top=g["top"], tights=g["tights"], warmers=g["warmers"], shoes=AE.SNEAKERS)
    lines = text.splitlines(True)
    n = 0
    for k in range(len(lines) - 3):
        name = lines[k].strip()
        if name not in MAN_BONES or not lines[k + 2].strip().replace(".", "").replace("-", "").isdigit():
            continue
        parts = lines[k + 3].split()
        if not parts or not parts[0].isdigit() or int(parts[0]) != len(parts) - 1:
            continue
        new = [parts[0]]
        for r in parts[1:]:
            rsd = ctx.char_file(r.lower() + ".rsd").decode("latin-1")
            old_p = rsd.split("PLY=")[1][:4]
            r_, p_ = "XR%s%s" % (g["tag"], chr(65 + n)), "XP%s%s" % (g["tag"], chr(65 + n))
            n += 1
            ctx.char_file(p_.lower() + ".p", _respray(ctx.char_file(old_p.lower() + ".p"), cols[MAN_BONES[name]], skin,
                                                                 g.get("skin_near")))
            ctx.char_file(r_.lower() + ".rsd", rsd.replace("PLY=%s." % old_p, "PLY=%s." % p_).encode("latin-1"))
            new.append(r_)
        lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), " ".join(new))
    assert 8 <= n <= 26, (g["key"], n)
    return "".join(lines)


def _cast(ctx, loader):
    """Model entries (Tifa, then the pool), each its spandex .hrc and only its stand + the aerobic moves."""
    out = []
    wo = _mods()[4]
    tifa = ModelLoader(ctx.field(TIFA_SRC[0]).section("models"))
    e = tifa.models[TIFA_SRC[1]]
    stand = ModelLoader.anims(e)[0]
    names = AP.build(ctx, wo.SPANDEX_HRC.lower(), stand.split(".")[0].lower() + ".a", AE.PREFIX["tifa"])
    k = loader.add_from(tifa, TIFA_SRC[1])
    e = loader.models.pop(k)
    out.append(ModelLoader.only_anims(ModelLoader.with_hrc(e, wo.SPANDEX_HRC, "aer_tifa.char"), [stand] + names))
    for g in AE.POOL:
        donor = ModelLoader(ctx.field(g["donor"][0]).section("models"))
        e = donor.models[g["donor"][1]]
        text = ctx.char_file(ModelLoader.hrc(e).lower()).decode("latin-1")
        hrc = (_girl if g["kind"] == "girl" else _man)(ctx, g, text)
        hname = "XA%sA.HRC" % g["tag"]
        ctx.char_file(hname.lower(), hrc.encode("latin-1"))
        stand = ModelLoader.anims(e)[0]
        names = AP.build(ctx, hname.lower(), stand.split(".")[0].lower() + ".a", AE.PREFIX[g["key"]])
        k = loader.add_from(donor, g["donor"][1])
        e = loader.models.pop(k)
        out.append(ModelLoader.only_anims(ModelLoader.with_hrc(e, hname, "aer_%s.char" % g["key"]), [stand] + names))
    return out


# ---- the layout ----------------------------------------------------------------------------------------------
def _unproject(cam, mesh, sx, sy):
    """The floor point (x, y, z, tri) the camera projects to screen (sx, sy) (Newton on the floor)."""
    t0 = min(range(len(mesh.tris)), key=lambda i: math.dist(cam.project(*mesh.center(i)), (sx, sy)))
    x, y = map(float, mesh.center(t0)[:2])
    for _ in range(40):
        t = mesh.find(round(x), round(y))
        z = mesh.height(t, round(x), round(y)) if t is not None else mesh.center(t0)[2]
        p = cam.project(x, y, z)
        ex, ey = sx - p[0], sy - p[1]
        if abs(ex) < 0.3 and abs(ey) < 0.3:
            break
        px, py = cam.project(x + 10, y, z), cam.project(x, y + 10, z)
        a, b, c, d = (px[0] - p[0]) / 10, (py[0] - p[0]) / 10, (px[1] - p[1]) / 10, (py[1] - p[1]) / 10
        det = a * d - b * c
        x += (d * ex - b * ey) / det
        y += (-c * ex + a * ey) / det
    x, y = round(x), round(y)
    t = mesh.find(x, y)
    assert t is not None, ("off the floor", sx, sy, x, y)
    return x, y, mesh.height(t, x, y), t


# ---- Tifa in the gym ---------------------------------------------------------------------------------------
def _tifa(ctx, arrive):
    import _travel as TV
    hb = _mods()[1]
    mesh = Walkmesh(ctx.field(AE.GYM).section("walkmesh"))
    tt = mesh.find(*AE.TIFA_AT)
    assert tt is not None
    model = TV.copy_model(ctx, AE.GYM, "mds7pb_1", 2)

    def talk(sec):
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + hb._say(sec, AE.TIFA_TALK["greet"])
        ask, first = hb._ask(sec, *AE.TIFA_TALK["ask"])
        no = asm.nop()
        ops += ask + [asm.if_byte(hb.CHOICE, "==", first, no), hb._uc(0), Op(hb.FADE_OUT), Op(b"\x6C"),
                      asm.mapjump(ctx.maplist.index(AE.FIELD), arrive[0], arrive[1], arrive[3], 0), asm.ret(), no]
        return ops + hb._say(sec, AE.TIFA_TALK["no"]) + [hb._uc(0), asm.ret()]
    TV.add_npc(ctx, AE.GYM, "gymtifa", model, (*AE.TIFA_AT, round(mesh.height(tt, *AE.TIFA_AT)), tt), 0x00, talk)


# ---- the class -----------------------------------------------------------------------------------------------
def apply(ctx):
    mv, hb, dt, sd, wo = _mods()
    ctx.field(AE.FIELD)
    f = ctx._fields[AE.FIELD] = FieldFile(ctx._orig_raw[AE.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    view = _unproject(cam, mesh, *AE.VIEW)
    slots = [_unproject(cam, mesh, *s) for s in AE.SLOTS]
    tifa_at = _unproject(cam, mesh, *AE.TIFA_S)
    face = lambda p: facing_screen(cam, *p[:3], (0, 1))
    _tifa(ctx, view)
    # models: 0 the hidden player (Cloud), 1 Tifa, 2.. the pool
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    loader.models = [ModelLoader.only_anims(cl0, ModelLoader.anims(cl0)[:1])]
    cast = _cast(ctx, loader)
    loader.models += cast
    assert len(loader.models) == 2 + len(AE.POOL) <= 16
    n_anims = sum(len(ModelLoader.anims(m)) for m in loader.models)
    assert n_anims <= 173 and all(len(ModelLoader.anims(m)) <= 47 for m in loader.models), n_anims
    letters = [L for L, _ in AP.MOVES]
    anim = lambda L, t: 1 + 2 * letters.index(L) + t if L else 1 + 2 * len(letters)     # (None: the bounce)
    FINISH = 2 + 2 * len(letters)
    # entities
    P = ["p_" + g["key"][:6] for g in AE.POOL]
    names = ["dir", "cloud", "tifa"] + P + ["k_sw", "k_ca", "k_ok", "k_mn", "prompt", "voice", "hush"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    noface = [Op(b"\x7E\x01"), Op(b"\xC7\x01")]                     # (TLKON off, SOLID off)
    play = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    dance = [asm.nop()] + mv._chain(M, [play(i) for i in range(FINISH + 1)]) + [asm.ret()]
    scripts = {E["cloud"]: {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*view), hb._visi(0)] + noface +
                            [asm.ret(), asm.ret()]},
               E["tifa"]: {0: [Op(bytes([0xA1, 1])), xyzi(*tifa_at), d_(face(tifa_at)), hb._visi(1)] + noface +
                           play(anim(None, 0)) + [asm.ret(), asm.ret()], 3: dance}}
    for m, g in enumerate(AE.POOL):
        place, gone = [asm.nop()], asm.nop()
        place += [asm.if_byte(SL[m], "!=", 0, gone)] + \
            mv._chain(SL[m], [[]] + [[xyzi(*s), d_(face(s))] for s in slots]) + \
            [hb._visi(1)] + play(anim(None, 0)) + [asm.ret(), gone, hb._visi(0), asm.ret()]
        idle = asm.nop()
        scripts[E[P[m]]] = {0: [Op(bytes([0xA1, 2 + m])), xyzi(*view), hb._visi(0)] + noface + [asm.ret(), asm.ret()],
                            2: place,
                            3: [asm.if_byte(SL[m], "!=", 0, idle)] + dance[1:-1] + [asm.ret(), idle, asm.ret()]}
    # the buttons: one small entity each (an up -> down change sets PR = k + 1)
    for k, (mask, _) in enumerate(AE.KEYS):
        top_, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok", "k_mn"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top_,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held), asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), held,
                asm.goto_back(top_), up, asm.setbyte(PRV[k], 0), asm.goto_back(top_), asm.ret()]}
    pr = {0: [asm.ret(), asm.ret()]}
    for j, (_, label) in enumerate(AE.KEYS):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, 30, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    # the voice: slot 2+i shows line i in window 2 (no close) for SAY frames; TALKING while it's up
    lines = [AE.CALLS[c] for c in AE.CALLS] + [AE.FAST] + AE.CHEERS + [AE.FLUBS[g["key"]] for g in AE.POOL]
    vo = {0: [asm.ret(), asm.ret()]}
    for i, text in enumerate(lines):
        vo[2 + i] = [asm.setbyte(TALKING, 1), Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, 150),
                     hb._req(E["hush"], 2, wait=False), asm.message(2, mv._text_id(sec, text)), asm.ret()]
    scripts[E["voice"]] = vo
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()],
                          2: [hb._w(AE.SAY), Op(b"\x54\x02"), asm.setbyte(TALKING, 0), asm.ret()]}
    call_of = {c: j for j, c in enumerate(AE.CALLS)}
    FAST_L, CHEER_L = len(AE.CALLS), len(AE.CALLS) + 1
    FLUB_L = CHEER_L + len(AE.CHEERS)
    voice = lambda i: hb._req(E["voice"], 2 + i, wait=False)

    def say_free(i):                                                 # (unless a line is already up)
        busy = asm.nop()
        return [asm.if_byte(TALKING, "==", 0, busy), voice(i), busy]
    # the director
    say = lambda t: hb._say(sec, t)
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    rnd = lambda mod: [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], mod]))]
    dancers = [E["tifa"]] + [E[p] for p in P]
    start_all = [hb._req(e, 3, wait=False) for e in dancers]
    again = asm.nop()
    main = [hb._uc(1), hb._menu(1), asm.setbyte(ROUND, 0), again, asm.setbyte(USED, 0), asm.setbyte(K, 1)]
    for m in range(len(AE.POOL)):
        main += [asm.setbyte(SL[m], 0)]
    # five classmates at random: RND until an unused one, its slot = K (IFs jump forward only: retry via a goto)
    pick, retry, picked, pick_done = (asm.nop() for _ in range(4))
    main += [pick] + rnd(len(AE.POOL))
    main += mv._chain(RND, [[asm.if_byte(USED, "bit_off", m, retry), asm.biton(USED, m), asm.setbyte(SL[m], K),
                             asm.goto(picked)] for m in range(len(AE.POOL))])
    main += [retry, asm.goto_back(pick), picked, Op(bytes([0x95, K[0], K[1]])),
             asm.if_byte(K, "<=", len(AE.SLOTS), pick_done), asm.goto_back(pick), pick_done]
    main += [hb._req(E[p], 2) for p in P]
    seen = asm.nop()
    main += [asm.setbyte(M, anim(None, 0))] + start_all + [hb._w(15)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, AE.MUSIC]) + bytes(8)), asm.if_byte(ROUND, "==", 0, seen)]
    for t in AE.INTRO:
        main += say(t)
    main += say(AE.HOW) + [seen, asm.setbyte(ROUND, 1)]
    main += [asm.setword(HITS, 0), asm.setword(PAY, 0), asm.setbyte(STREAK, 0), asm.setbyte(TALKING, 0)]
    total, fast_said = 0, False
    for L, tempo, cycles in AE.ROUTINE:
        per = AP.CYCLE * AP.BEATS[tempo]
        main += [asm.setbyte(M, anim(L, tempo))] + start_all
        main += [voice(FAST_L)] if tempo and not fast_said else [voice(call_of[L])]
        fast_said = fast_said or tempo == 1
        if L is None:
            main += [hb._w(per * cycles)]
            continue
        total += cycles
        top, wait, judge, miss, hit_done, rest, nxt, done = (asm.nop() for _ in range(8))
        main += [asm.setword(CY, 0), top] + rnd(len(AE.KEYS)) + \
            [asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0),
             asm.setword(CNT, 0)] + mv._chain(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)]
                                                   for k in range(len(AE.KEYS))])
        main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
                 asm.if_word(CNT, "<", per - 2, miss), asm.goto_back(wait),
                 judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss),
                 Op(AE.HIT_SOUND), Op(bytes([0x96, HITS[0], HITS[1]])), hb._arith(0x86, PAY, 1 + tempo),
                 Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(STREAK, ">=", AE.COMBO, hit_done),
                 asm.setbyte(STREAK, 0), hb._arith(0x86, PAY, AE.COMBO_TIP)] + rnd(len(AE.CHEERS))
        main += mv._chain(RND, [say_free(CHEER_L + j) for j in range(len(AE.CHEERS))]) + [asm.goto(hit_done)]
        main += [miss, Op(b"\x54\x01"), buzz, asm.setbyte(STREAK, 0)] + rnd(len(AE.POOL))
        main += mv._chain(RND, [[asm.if_byte(SL[m], "!=", 0, hit_done)] + say_free(FLUB_L + m)
                                for m in range(len(AE.POOL))])
        main += [hit_done, rest, asm.if_word(CNT, "<", per, nxt), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                 asm.goto_back(rest), nxt, Op(bytes([0x96, CY[0], CY[1]])), asm.if_word(CY, "<", cycles, done),
                 asm.goto_back(top), done]
    # the finish, the grade, a classmate's reaction, the pay
    main += [hb._w(AE.SAY), asm.setbyte(M, FINISH)] + start_all + [hb._w(30)]
    grade_done = asm.nop()
    main += [asm.setbyte(GRADE, len(AE.GRADES) - 1)]
    for gi, (share, _) in enumerate(AE.GRADES[:-1]):
        nx = asm.nop()
        main += [asm.if_word(HITS, ">=", math.ceil(share * total), nx), asm.setbyte(GRADE, gi), asm.goto(grade_done), nx]
    main += [grade_done] + mv._chain(GRADE, [say(t) for _, t in AE.GRADES])
    react, absent, reacted = asm.nop(), asm.nop(), asm.nop()
    main += [react] + rnd(len(AE.POOL))
    main += mv._chain(RND, [[asm.if_byte(SL[m], "!=", 0, absent)] +
                            mv._chain(GRADE, [say(t) for t in AE.REACT[g["key"]]]) + [asm.goto(reacted)]
                            for m, g in enumerate(AE.POOL)])
    main += [absent, asm.goto_back(react), reacted]
    main += [asm.setword(GIL, PAY)] + mv._chain(GRADE, [[hb._arith(0x86, GIL, len(AE.SLOTS) * fee)] for fee in AE.FEES])
    paid = say(AE.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
    main += [Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))] + paid
    ask, first = hb._ask(sec, *AE.AGAIN)
    bye = asm.nop()
    main += ask + [asm.if_byte(hb.CHOICE, "==", first, bye)] + fade_out + [hb._w(10), asm.goto_back(again), bye]
    # back beside Tifa in the gym
    bm = Walkmesh(ctx.field(AE.GYM).section("walkmesh"))
    bx, by = AE.TIFA_AT[0] + 30, AE.TIFA_AT[1]
    bt = bm.find(bx, by)
    assert bt is not None
    stop_ = hb._w(30)
    main += say(AE.BYE) + fade_out + \
        [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(AE.GYM), bx, by, bt, 0xC0),
         stop_, asm.goto_back(stop_)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  693: aerobics on %s (view %s, Tifa %s, slots %s; %d prompts, %d anims, %d texts, script %d bytes)"
          % (AE.FIELD, view[:3], tifa_at[:3], [s[:2] for s in slots], total, n_anims, n_text, len(f.sections[0])))

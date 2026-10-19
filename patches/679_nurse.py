"""(user) Hello nurse: a scene in Mideel's clinic (data `_nurse.py`, poses `_nurse_poses.py`), and the island
nurse's full animation suite.

The nurse: ithos model 8 (BTEC.HRC, the dancer's skeleton with Ruby's bone lengths). `NURSE_HRC` = her
undressed copy, the standard female body (`_female_body.apply`, tag N, her own head and feet, her face's skin)
with nipples; her suite (user: "copying ztfa's animations") = every movie anim Tifa has (ZV..) retargeted from
Ruby's ZM.. onto her as `SUITE` ZI..; her own positions (user: unique, not Tifa's) ZO.. -> ZJ...

The scene: unlocked with "Everyone" (670's rank-6 co-star list: "Hello nurse", SPEC 5). Set = ithos copied
under CD.FIELD (subin_4: the classic group set, unreachable since the loose shoot; 677 / 678 read its models
first), script blanked. Models: Cloud (the hidden player: the camera's focus), bare Cloud (the patient on the
front bed), the doctor, the undressed nurse, six clothed nurses (each her own copy: no two entities share a
model), the cameraman. The director loops: a nurse at random (never twice running), "Nurse <name>, go check
on the patient.", she walks (XYZI stepped a frame at a time) to the foot of his bed, her greeting; fade; her
position (random, never twice running) for TURN frames (the fast pace from FAST_AT, two of her lines in a
no-close window); fade; back at her post; now and then a break (nurses / the doctor gather and talk); Square
(any time) = asked at the round's end whether to check out. Leaving: MOVIE_PRESSES = rounds x ROUND_PRESSES
(the cameraman pays as for the group). Placement checked on offline renders only."""
import importlib
import math
import struct

import _female_body as fb
import _movie_loose as LZ
import _nurse as ND
import _nurse_poses as NP
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

NURSE_DONOR = ("ithos", 8)
DOCTOR_DONOR = ("ithos", 7)
NURSE_HRC = "ZIUA.HRC"          # her undressed copy
NURSE_STAND = "dmbb.a"          # (her stand / walk: DMBB / DMBC)
SUITE = "ZI"                    # her copy of the movie's anims (Tifa's ZV.. set)
OWN = "ZJ"                      # her own positions (Ruby's ZO..)
BED = (152, 150, 59)            # Cloud's spot on the front bed (head to +y, DIR 0)
SPOON_AT = (160, 150, 59, 64)   # (spooning: both lie along the bed facing +x, the camera's side)
STOP = (150, 60, 128)           # where a nurse stops: the foot of his bed, facing it
HOMES = [(-160, -40), (-160, 0), (-160, 40), (-100, -20), (-100, 20), (-100, 60)]   # the nurses' station
DOCTOR = (-40, 40)
CAMERA = (-200, -20)            # by the curtain, filming the bed
FOCUS = (-30, 84, 0)             # the hidden player (the camera follows it): the whole scene in view
BED_FOCUS = (-6, 162, 0)        # (the camera during a position: the bed in the middle of the view)
ARRIVE = (-40, 60)              # (670's MAPJUMP: on the floor; the init moves the player to FOCUS)
HUDDLE_AT = (80, 0)             # a break: the huddle's middle, on the open floor before the beds
HUDDLE = {2: [(80, -30), (80, 30)], 3: [(80, -35), (80, 35), (45, 0)],
          4: [(80, -40), (80, 40), (45, -15), (45, 15)]}
WALK_STEP = 2.2
LINE_Y = 168                    # her lines' window (lower half: the bed is up on the right)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


# ---- the nurse's models and anims --------------------------------------------------------------------
def _nurse_models(ctx):
    mv, _, _ = _mods()
    text = ctx.char_file("btec.hrc").decode("latin-1")
    skin = fb.face_skin(ctx, text)
    ctx.char_file(NURSE_HRC.lower(), fb.apply(ctx, text, "N", skin).encode("latin-1"))
    tips = fb._bust_tips(ctx)
    ctx.char_file(NURSE_HRC.lower(), fb.nipples(ctx, ctx.char_file(NURSE_HRC.lower()).decode("latin-1"), "N", tips)
                  .encode("latin-1"))
    # (user) Tifa's body (the user's) as every girl's: in her skin, the standard bust
    fb.tifa_body(ctx, ctx.char_file(NURSE_HRC.lower()).decode("latin-1"), skin, 1.0)
    # her suite: every anim Tifa has (ZV..), from Ruby's ZM.. (the same names after the prefix)
    built = ctx._char                                      # (every movie anim is built by the patches)
    tifa = sorted({n.split(".")[0][2:] for n in built if n.startswith("zv") and n.endswith(".a")})
    suite = ["ZM%s.tor" % suf.upper() for suf in tifa if "zm" + suf + ".a" in built]
    mv._retarget(ctx, suite, SUITE, NURSE_HRC.lower(), NURSE_STAND)
    place = NP.build(ctx)
    mv._retarget(ctx, ["ZO%s%d.tor" % (p["girl"], k) for p in ND.POSITIONS for k in range(4)], OWN,
                 NURSE_HRC.lower(), NURSE_STAND)
    return place, len(suite)


# ---- the scene -----------------------------------------------------------------------------------------
NUR, LASTN, POSV, LASTP, RND, CI, LASTC, LEAVEV, VL, CN = ((5, a) for a in range(100, 110))
CX, CY, ROUNDS = (6, 112), (6, 114), (6, 116)


def _walk(hb, xyzi, d_, loop_, start, stop, t, z=0):
    """XYZI stepped WALK_STEP a frame from start to stop (x, y) with the walk anim (1), then stand (0) facing d."""
    (sx, sy), (tx, ty, d) = start, stop
    n = max(1, round(math.dist((sx, sy), (tx, ty)) / WALK_STEP))
    stx, sty = round((tx - sx) / n), round((ty - sy) / n)
    top, done = hb._w(1), asm.nop()
    a = math.atan2(tx - sx, -(ty - sy))                       # (DIR d faces (sin a, -cos a))
    wd = round(a * 256 / (2 * math.pi)) % 256
    return [d_(wd), asm.setword(CX, sx & 0xFFFF), asm.setword(CY, sy & 0xFFFF), asm.setbyte(CN, 0)] + loop_(1) + \
        [top, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
         Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], z, t)),
         Op(bytes([0x95, CN[0], CN[1]])), asm.if_byte(CN, "<", n, done), asm.goto_back(top), done]


def _scene(ctx, place):
    mv, hb, dt = _mods()
    assert LZ.ENABLED, "679_nurse uses subin_4, the classic group set: Everyone must go to the loose shoot"
    ctx.field(ND.FIELD)
    f = FieldFile(ctx.field(ND.BASE).build())
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    ctx._fields[ND.FIELD] = f
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    cam = Camera(f.sections[1])
    from ff7.walkmesh import Walkmesh
    mesh = Walkmesh(f.section("walkmesh"))
    def tri(x, y):
        t = mesh.find(round(x), round(y))
        return t if t is not None else min(range(len(mesh.tris)), key=lambda i: math.dist(mesh.center(i)[:2], (x, y)))
    # models
    base = ModelLoader(f.section("models"))
    cl0 = ModelLoader(ctx.field("del3").section("models")).models[0]          # (Cloud: AAAA)
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    loader = base
    loader.models = [base.models[0]]                                         # (0: the hidden player)
    cloud_anims = ["ACFE.aki", "AAFF.aki", "AAGA.aki", "ZNY9.tor"] + \
        sorted({"ZN%s%s.tor" % (p["cloud"], s) for p in ND.POSITIONS for s in "13"})
    loader.models.append(ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "nurse_cloud_b.char"),
                                                cloud_anims))
    donor = ModelLoader(ctx.field(NURSE_DONOR[0]).section("models"))
    loader.models.append(donor.models[DOCTOR_DONOR[1]])                      # 2 the doctor
    nurse = donor.models[NURSE_DONOR[1]]
    girl_anims = [NURSE_STAND.upper().replace(".A", ".aki")] + \
        ["%s%s%s.tor" % (OWN, p["girl"], s) for p in ND.POSITIONS for s in "13"]
    girl_anims[0] = ModelLoader.anims(nurse)[0]
    loader.models.append(ModelLoader.only_anims(ModelLoader.with_hrc(nurse, NURSE_HRC, "nurse_b.char"), girl_anims))
    for k in range(len(ND.NURSES)):                                          # 4.. the nurses (clothed)
        loader.models.append(nurse)
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_FILM)
    assert len(loader.models) <= 16
    for n in cloud_anims[3:] + girl_anims[1:]:
        ctx.char_file(n.split(".")[0].lower() + ".a")                        # (exists)
    # entities
    names = ["produce", "cloud", "cloudb", "doctor", "nurseb"] + ["nurse%d" % k for k in range(len(ND.NURSES))] + \
        ["camera", "keys", "voice", "hush"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch = mv._chain
    face = lambda x, y, tx, ty: dt._dir_to(tx - x, ty - y)
    scripts = {}
    fx, fy, fz = FOCUS
    gx_, gy_, gz_ = BED_FOCUS
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(fx, fy, fz, tri(fx, fy)), hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()],
                           2: [xyzi(gx_, gy_, gz_, tri(gx_, gy_)), asm.ret()],          # the camera on the bed
                           3: [xyzi(fx, fy, fz, tri(fx, fy)), asm.ret()]}               # back on the room
    # Cloud on the bed: idle (ZNY9, lying still), slot 2 the position (slow), 3 fast, 4 back to idle
    cidx = lambda n: cloud_anims.index(n)
    bx, by, bz = BED
    btri = next(t for t in range(len(mesh.tris)) if mesh.contains(t, bx, by) and abs(mesh.height(t, bx, by) - bz) < 2)

    def cloud_spot(p):
        return (SPOON_AT[:3], SPOON_AT[3]) if p["key"] == "spoon" else (BED, 0)
    idle = [xyzi(bx, by, bz, btri), d_(0), hb._visi(1)] + loop_(cidx("ZNY9.tor"))
    scripts[E["cloudb"]] = {
        0: [Op(bytes([0xA1, 1]))] + hide() + idle + [asm.ret(), asm.ret()],
        2: ch(POSV, [[xyzi(*cloud_spot(p)[0], btri), d_(cloud_spot(p)[1])] + loop_(cidx("ZN%s1.tor" % p["cloud"]))
                     for p in ND.POSITIONS]) + [asm.ret()],
        3: ch(POSV, [loop_(cidx("ZN%s3.tor" % p["cloud"])) for p in ND.POSITIONS]) + [asm.ret()],
        4: idle + [asm.ret()]}
    # the undressed nurse: slot 2 her spot by the position (her PLACE from Cloud's), 3 fast, 4 hidden
    gidx = lambda n: girl_anims.index(n)

    def her_spot(p):
        (cx, cy, cz), cd = cloud_spot(p)
        dx, dy, dz, rel, floor = place[p["key"]]
        a = cd * 2 * math.pi / 256
        x, y = cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)
        return (round(x), round(y), round((0 if floor else cz) + dz)), (cd + rel) % 256
    scripts[E["nurseb"]] = {
        0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch(POSV, [[xyzi(*her_spot(p)[0], btri), d_(her_spot(p)[1]), hb._visi(1)] +
                     loop_(gidx("%s%s1.tor" % (OWN, p["girl"]))) for p in ND.POSITIONS]) + [asm.ret()],
        3: ch(POSV, [loop_(gidx("%s%s3.tor" % (OWN, p["girl"]))) for p in ND.POSITIONS]) + [asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    # a break: who gathers in a huddle on the open floor (`HUDDLE` spots by how many), facing its middle
    def cut_ops(who):
        out = []
        for c in ND.CUTS:
            if who in c["who"]:
                sx, sy = HUDDLE[len(c["who"])][c["who"].index(who)]
                out.append([xyzi(sx, sy, 0, tri(sx, sy)), d_(face(sx, sy, *HUDDLE_AT))] + loop_(0))
            else:
                out.append([])
        return ch(CI, out)
    # the doctor: 10 home, 11 a break's spot
    dx_, dy_ = DOCTOR
    dhome = [xyzi(dx_, dy_, 0, tri(dx_, dy_)), d_(face(dx_, dy_, *BED[:2])), hb._visi(1)] + loop_(0)
    scripts[E["doctor"]] = {0: [Op(bytes([0xA1, 2]))] + hide() + dhome + [asm.ret(), asm.ret()],
                            10: dhome + [asm.ret()], 11: cut_ops("doctor") + [asm.ret()]}
    # the nurses: at home facing the bed; 8 walk to the bed's foot; 9 hidden; 10 home; 11 a break's spot
    for k, name in enumerate(ND.NURSES):
        hx, hy = HOMES[k]
        home = [xyzi(hx, hy, 0, tri(hx, hy)), d_(face(hx, hy, *STOP[:2])), hb._visi(1)] + loop_(0)
        cuts = cut_ops(name)
        scripts[E["nurse%d" % k]] = {
            0: [Op(bytes([0xA1, 4 + k]))] + hide() + home + [asm.ret(), asm.ret()],
            8: _walk(hb, xyzi, d_, loop_, (hx, hy), STOP, tri(*STOP[:2])) + [xyzi(STOP[0], STOP[1], 0, tri(*STOP[:2])), d_(STOP[2])] +
            loop_(0) + [asm.ret()],
            9: [hb._visi(0), asm.ret()],
            10: home + [asm.ret()],
            11: cuts + [asm.ret()]}
    mx, my = CAMERA
    scripts[E["camera"]] = {0: [Op(bytes([0xA1, cm])), xyzi(mx, my, 0, tri(mx, my)), d_(face(mx, my, *BED[:2])),
                                hb._visi(1)] + hide() + loop_(film) + [asm.ret(), asm.ret()]}
    # Square (held) any time -> LEAVEV
    wait = hb._w(1)
    nx = asm.nop()
    scripts[E["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x30]) + struct.pack("<H", 0x80) + b"\x00", target=nx),
                              asm.setbyte(LEAVEV, 1), nx, asm.goto_back(wait), asm.ret()]}
    # her lines: a window the player can't close, shut by hush
    lines = []
    for name in ND.NURSES:
        per = []
        for p in ND.POSITIONS:
            for t in ND.TALK[p["key"]]:
                text = "Nurse %s\n%s" % (name, t)
                per.append([Op(b"\x52\x01\x00\x01"), hb._window(text, 1, 8, LINE_Y), hb._req(E["hush"], 2, wait=False),
                            asm.message(1, mv._text_id(sec, text))])
        lines.append(ch(VL, per))
    scripts[E["voice"]] = {0: [asm.ret(), asm.ret()], 2: ch(NUR, lines) + [asm.ret()]}
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(110), Op(b"\x54\x01"), asm.ret()]}

    # the director
    say = lambda t: hb._say(sec, t)
    NN, NPOS, NC = len(ND.NURSES), len(ND.POSITIONS), len(ND.CUTS)

    def pick(var, last, n):
        """var = RANDOM mod n, never `last` (then the next one)."""
        same, ok = asm.nop(), asm.nop()
        return [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], n])),
                asm.if_byte(RND, "==", last, ok), Op(bytes([0x95, RND[0], RND[1]])), asm.if_byte(RND, ">=", n, ok),
                asm.setbyte(RND, 0), ok, asm.setbyte(var, RND), asm.setbyte(last, var)]
    fade_out = [Op(hb.FADE_OUT), Op(b"\x6C")]
    fade_in = [Op(hb.FADE_IN), Op(b"\x6C")]
    main = [hb._uc(1), hb._menu(1), asm.setbyte(LASTN, 255), asm.setbyte(LASTP, 255), asm.setbyte(LASTC, 255),
            asm.setbyte(LEAVEV, 0), asm.setword(ROUNDS, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, ND.MUSIC]) + bytes(8))]
    for t in ND.INTRO:
        main += say(t)
    top = asm.nop()
    main += [top] + pick(NUR, LASTN, NN)
    main += ch(NUR, [say(ND.SEND.format(name=n)) for n in ND.NURSES])
    main += ch(NUR, [[hb._req(E["nurse%d" % k], 8)] for k in range(NN)])
    greet = []
    for n in ND.NURSES:
        g = ND.GREET[n]
        greet.append([Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], len(g)]))] +
                     ch(RND, [say(t) for t in g]))
    main += ch(NUR, greet) + pick(POSV, LASTP, NPOS)
    main += fade_out + ch(NUR, [[hb._req(E["nurse%d" % k], 9, wait=False)] for k in range(NN)]) + \
        [hb._req(E["cloud"], 2, wait=False), hb._req(E["cloudb"], 2, wait=False), hb._req(E["nurseb"], 2, wait=False),
         hb._w(30)] + fade_in
    # the position: TURN frames; her lines at 3 s and at 12 s; the fast pace from FAST_AT
    line = lambda i: [asm.setbyte(VL, POSV), Op(bytes([0x85, 0x55, VL[1], POSV[1]]))] + \
        ([Op(bytes([0x95, VL[0], VL[1]]))] if i else []) + [hb._req(E["voice"], 2, wait=False)]
    main += [hb._w(90)] + line(0) + [hb._w(ND.FAST_AT - 90), hb._req(E["cloudb"], 3, wait=False),
                                      hb._req(E["nurseb"], 3, wait=False), hb._w(60)] + line(1) + \
        [hb._w(ND.TURN - ND.FAST_AT - 60), Op(b"\x54\x01")]
    main += fade_out + [hb._req(E["cloud"], 3, wait=False), hb._req(E["nurseb"], 4, wait=False),
                        hb._req(E["cloudb"], 4, wait=False)] + \
        ch(NUR, [[hb._req(E["nurse%d" % k], 10, wait=False)] for k in range(NN)]) + [hb._w(30)] + fade_in + \
        [hb._arith(0x86, ROUNDS, 1)]
    # a break now and then
    nocut = asm.nop()
    main += [Op(bytes([0x99, RND[0], RND[1]])), asm.if_byte(RND, "<", ND.CUT_CHANCE, nocut)] + pick(CI, LASTC, NC) + \
        fade_out + [hb._req(E["nurse%d" % k], 11, wait=False) for k in range(NN)] + \
        [hb._req(E["doctor"], 11, wait=False), hb._w(30)] + fade_in + \
        ch(CI, [say(c["talk"]) for c in ND.CUTS]) + fade_out + \
        [hb._req(E["nurse%d" % k], 10, wait=False) for k in range(NN)] + \
        [hb._req(E["doctor"], 10, wait=False), hb._w(30)] + fade_in + [nocut]
    # Square: check out?
    stay = asm.nop()
    ask, first = hb._ask(sec, ND.LEAVE_ASK, ND.LEAVE)
    main += [asm.if_byte(LEAVEV, "==", 1, stay), asm.setbyte(LEAVEV, 0)] + ask + \
        [asm.if_byte(hb.CHOICE, "==", first, stay)] + say(ND.LEAVE_LINE)
    rx, ry, rz, rt, rdir = ctx.movie_back
    state = [asm.setword(mv.MOVIE_PRESSES, ROUNDS), hb._arith(0x8A, mv.MOVIE_PRESSES, ND.ROUND_PRESSES),
             asm.setword(mv.MOVIE_AT, mv.HB_MINUTES), asm.setbyte(mv.MOVIE_STATE, 2)]
    stop = hb._w(30)
    main += state + fade_out + [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir),
                                stop, asm.goto_back(stop)]
    main += [stay, asm.goto_back(top), asm.ret()]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    return n_text, len(f.sections[0])


def apply(ctx):
    place, n_suite = _nurse_models(ctx)
    n_text, size = _scene(ctx, place)
    print("  679: the island nurse's suite (%d anims as %s.., her own positions %s..); Hello nurse on %s "
          "(%d texts, script %d bytes)" % (n_suite, SUITE, OWN, ND.FIELD, n_text, size))

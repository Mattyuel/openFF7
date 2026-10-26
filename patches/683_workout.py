"""(user) Sector 7 Workout: the first parody film (data `_workout.py`, poses `_workout_poses.py`), shot in the
Wall Market gym. Tifa comes in for the first time looking for a trainer; Cloud spots her squats from behind.

The minigame: one squat a rep, one prompt a rep ([SWITCH] / [CANCEL] / [OK] at random, as the squat
contest names its buttons) in a window the player can't close; the right button before the rep ends is a
hit, anything else (or nothing) a miss. HITS_UP hits in a row step the pace up a tier (PERIODS: frames a
rep); a miss drops it back to the slowest. Each new tier the first time: a pair of lines (tips, questions,
then at tier 4 the 'training device'). Part one (clothed) ends PART_A_END hits into the top tier: fade,
both undressed, part two from the slow pace again, the pose more overt with every tier, PART_B_REPS
prompts. Pay on the spot: PAY_HIT gil x (tier + 1) for every hit.

Tifa's clothed model for the film (user: "bright spandex"): her own head and feet on the standard body
with Tifa's shape (`_female_body.apply` + `tifa_body`, tag W, `SPANDEX_HRC`), painted: a hot pink leotard
(chest and pelvis, skin above the scoop neckline), turquoise tights (thighs), yellow leg warmers (shins);
bare arms, her arm guard off.

The set: FIELD (a debug room only startmap leads to) replaced by a copy of the gym, script blanked.
Models: Cloud (the hidden player: the camera's focus), Cloud and spandex Tifa (part one), bare Cloud and
bare Tifa (part two), the Director filming. Reached from the Director at the Sector 7 station (670's talk:
"Shoot Sector 7 Workout."); back there at the end. Checked on offline renders only."""
import importlib
import math
import struct

import _female_body as fb
import _workout as WO
import _workout_poses as WP
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera, facing_screen
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

SPANDEX_HRC = "XWTA.HRC"
BARE_TIED = "XWUA.HRC"              # the film's own copy of her undressed model (ZTFA), hair tied up
TAG = "W"
# (user) her hair tied up, not so long: the hair part on 'kami' (AAHF -> aaia.p, ~12 long down the bone,
# ~8.7 wide) copied as HAIR_RSD / HAIR_P, scaled in the bone's frame (x across, y depth, z down the bone)
HAIR_RSD, HAIR_P = "XWHA", "XWHB"
HAIR_SCALE = (0.45, 0.85, 0.35)
DONOR = ("bwhlin", 3)               # Tifa (AAGB), stand ABCD
BARE_HRC = "ZTFA.HRC"               # her undressed model (675)
HER_A, HER_B = "QT", "QU"           # her anims' prefixes: spandex / bare
# (B, G, R)
PINK, TEAL, YELLOW = (147, 20, 255), (208, 214, 40), (0, 220, 255)
NECK_Z = -3.3                       # the leotard's scoop neckline (Tifa's chest frame: z down the bone)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates"), importlib.import_module("682_school_dance")


# ---- her hair, tied up ---------------------------------------------------------------------------------------
def _tie(ctx, hrc):
    """hrc text with the 'kami' bone's hair part swapped for the short ponytail (written once)."""
    lines = hrc.splitlines(True)
    k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "kami")
    parts = lines[k + 3].split()
    assert parts[0] == "1", parts
    if True:                                                        # (the same files on every call)
        rsd = ctx.char_file(parts[1].lower() + ".rsd").decode("latin-1")
        old_p = rsd.split("PLY=")[1][:4]
        d = bytearray(ctx.char_file(old_p.lower() + ".p"))
        nv = struct.unpack_from("<16I", d, 0)[3]
        for i in range(nv):
            v = struct.unpack_from("<3f", d, 128 + 12 * i)
            struct.pack_into("<3f", d, 128 + 12 * i, *(v[j] * HAIR_SCALE[j] for j in range(3)))
        ctx.char_file(HAIR_P.lower() + ".p", bytes(d))
        ctx.char_file(HAIR_RSD.lower() + ".rsd", rsd.replace("PLY=%s." % old_p, "PLY=%s." % HAIR_P).encode("latin-1"))
    lines[k + 3] = lines[k + 3].replace(parts[1], HAIR_RSD)
    return "".join(lines)


# ---- spandex Tifa ------------------------------------------------------------------------------------------
def _spandex(ctx):
    mv, hb, dt, sd = _mods()
    donor = ModelLoader(ctx.field(DONOR[0]).section("models")).models[DONOR[1]]
    text = ctx.char_file(ModelLoader.hrc(donor).lower()).decode("latin-1")
    skin = fb.face_skin(ctx, text)
    hrc = fb.apply(ctx, text, TAG, skin, None, 1.0, 0.8)            # (head_drop as 675 / 682)
    if "armer" in fb.bones(hrc):                                     # her arm guard off
        lines = hrc.splitlines(True)
        k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "armer")
        lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), "0")
        hrc = "".join(lines)
    chest = ([([0.0, 0.0, 1.0], NECK_Z)], lambda c: skin if c[2] < NECK_Z else PINK)
    fb.tifa_body(ctx, hrc, skin, 1.5, paints={"chest": chest, "hip": ([], lambda c: PINK)})
    bn = fb.bones(hrc)
    for b, col in [("l_femur", TEAL), ("r_femur", TEAL), ("l_tibia", YELLOW), ("r_tibia", YELLOW)]:
        p = sd._ply(ctx, bn[b][1][0])
        ctx.char_file(p, sd._recolour(ctx.char_file(p), col))
    ctx.char_file(SPANDEX_HRC.lower(), _tie(ctx, hrc).encode("latin-1"))
    bare = ctx.char_file(BARE_HRC.lower()).decode("latin-1")             # (675's; other scenes keep it long)
    ctx.char_file(BARE_TIED.lower(), _tie(ctx, bare).encode("latin-1"))
    stand = ModelLoader.anims(donor)[0].split(".")[0].lower() + ".a"
    return donor, stand


# ---- the set ------------------------------------------------------------------------------------------------
TIER, STREAK, KEY, PR, PART, SEEN, RND, KP = ((5, a) for a in range(100, 108))
CNT, HITS, PAY, REPS, PER, GIL = ((6, a) for a in range(110, 122, 2))
PRV = [(5, 124 + k) for k in range(3)]


def _set(ctx, donor, stand, poses):
    mv, hb, dt, _ = _mods()
    ctx.field(WO.FIELD)
    ctx.field(WO.BASE)
    raw = ctx._orig_raw[WO.BASE]
    f = ctx._fields[WO.FIELD] = FieldFile(raw)
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
    # spots: Tifa at SQUAT_AT facing screen-left, Cloud `gap` behind her (per part and tier: his anims put
    # his hands on her hips at that gap)
    sx, sy = WO.SQUAT_AT
    d = facing_screen(cam, sx, sy, 0, WO.FACING)

    def behind(part, t):
        ox, oy, _ = mv._off((0, 0, WP.gap(part, t)), d)
        return round(sx + ox), round(sy + oy)
    # models: 0 the hidden player, 1 Cloud (A), 2 Tifa (A), 3 bare Cloud (B), 4 bare Tifa (B), 5 the Director
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    stand_c = ModelLoader.anims(cl0)[0]                              # ACFE
    stand_t = ModelLoader.anims(donor)[0]                            # ABCD
    (her_a, his_a), (her_b, his_b) = poses["A"], poses["B"]
    loader.models = [cl0,
                     ModelLoader.only_anims(cl0, [stand_c] + his_a),
                     ModelLoader.only_anims(ModelLoader.with_hrc(donor, SPANDEX_HRC, "workout_tifa.char"), [stand_t] + her_a),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "workout_cloudb.char"),
                                            [stand_c] + his_b),
                     ModelLoader.only_anims(ModelLoader.with_hrc(donor, BARE_TIED, "workout_tifab.char"), [stand_t] + her_b)]
    # (the donor's scale: Tifa comes from a 768 field; add_from rescales to this one)
    for k in (2, 4):
        tmp = ModelLoader(ctx.field(DONOR[0]).section("models"))
        tmp.models = [loader.models[k]]
        j = loader.add_from(tmp, 0)
        loader.models[k] = loader.models.pop(j)
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    cam_anims = ModelLoader.anims(loader.models[cm])
    film = cam_anims.index(mv.CAMERA_FILM)
    loader.models[cm] = ModelLoader.only_anims(loader.models[cm], cam_anims + [mv.CAMERA_STILL])
    still = len(cam_anims)
    assert len(loader.models) == 6
    # entities
    names = ["produce", "cloud", "cloudA", "tifaA", "cloudB", "tifaB", "camera", "k_sw", "k_ca", "k_ok",
             "prompt", "talk", "hush"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]               # TLKON 01, SOLID 01
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch = mv._chain
    face = lambda x, y, tx, ty: dt._dir_to(tx - x, ty - y)
    scripts = {}
    fx, fy = WO.FOCUS
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(fx, fy, 0, tri(fx, fy)), hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()]}
    ix, iy = WO.INTRO_TIFA
    cx_, cy_ = WO.INTRO_CLOUD
    # the actors: init hidden (B) / at the intro (A); slot 2 = this rep (the tier's anim from its start);
    # slot 3 = at the squat spot; slot 4 = hidden
    for ent, model, part, who in [("cloudA", 1, "A", "c"), ("tifaA", 2, "A", "t"), ("cloudB", 3, "B", "c"),
                                  ("tifaB", 4, "B", "t")]:
        n = len(WO.PERIODS)
        if who == "t":
            spot = lambda t: (sx, sy)
        else:
            spot = lambda t, part=part: behind(part, t)
        if part == "A":
            at = (ix, iy, face(ix, iy, cx_, cy_)) if who == "t" else (cx_, cy_, face(cx_, cy_, ix, iy))
            init = [Op(bytes([0xA1, model])), xyzi(at[0], at[1], 0, tri(at[0], at[1])), d_(at[2]), hb._visi(1)] + \
                hide() + loop_(0)
        else:
            init = [Op(bytes([0xA1, model])), hb._visi(0)] + hide()
        place = ch(TIER, [[xyzi(*spot(t), 0, tri(*spot(t))), d_(d)] for t in range(n)])
        scripts[E[ent]] = {0: init + [asm.ret(), asm.ret()],
                           2: place + ch(TIER, [loop_(1 + t) for t in range(n)]) + [asm.ret()],
                           3: place + [d_(d), hb._visi(1)] + loop_(1) + [asm.ret()],
                           4: [hb._visi(0), asm.ret()]}
    mx, my = WO.CAMERA_AT
    scripts[E["camera"]] = {0: [Op(bytes([0xA1, 5])), xyzi(mx, my, 0, tri(mx, my)), d_(face(mx, my, sx, sy)),
                                hb._visi(1)] + hide() + loop_(still) + [asm.ret(), asm.ret()],
                            2: loop_(film) + [asm.ret()]}
    # the buttons: one small entity each (8 ops a frame): a press = up -> down; PR = its number
    for k, (mask, _) in enumerate(WO.KEYS):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),     # IFKEY: not held -> up
                asm.if_byte(PRV[k], "==", 0, held),                                    # held before: nothing new
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.goto_back(top), asm.ret()]}
    # the prompt: window 1, can't be closed by the player; the director closes it (WCLSE 01)
    pr = {0: [asm.ret(), asm.ret()]}
    for k, (_, label) in enumerate(WO.KEYS):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + k] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, WO.PROMPT_Y, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    # the talk during the squats: window 2, each group's lines in turn, each shut by hush after SAY
    groups = [WO.LINES_A[t] for t in sorted(WO.LINES_A)] + [WO.LINES_B[t] for t in sorted(WO.LINES_B)] + \
        [[WO.MISS_A], [WO.MISS_B]]
    talk = {0: [asm.ret(), asm.ret()]}
    for j, lines in enumerate(groups):
        ops = []
        for text in lines:
            ops += [Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, WO.LINE_Y), hb._req(E["hush"], 2, wait=False),
                    asm.message(2, mv._text_id(sec, text))]
        talk[2 + j] = ops + [asm.ret()]
    scripts[E["talk"]] = talk
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(WO.SAY), Op(b"\x54\x02"), asm.ret()]}
    group_a = {t: 2 + i for i, t in enumerate(sorted(WO.LINES_A))}
    group_b = {t: 2 + len(WO.LINES_A) + i for i, t in enumerate(sorted(WO.LINES_B))}
    miss_a, miss_b = 2 + len(WO.LINES_A) + len(WO.LINES_B), 3 + len(WO.LINES_A) + len(WO.LINES_B)

    # the director
    say = lambda t: hb._say(sec, t)
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    actors = lambda part: ["cloudA", "tifaA"] if part == "A" else ["cloudB", "tifaB"]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))     # REQ: never waits (the talk may be busy)
    main = [hb._uc(1), hb._menu(1), hb._w(20)] + fade_in + [Op(bytes([0xF2, 0, 0, 0, 0x10, WO.MUSIC]) + bytes(8))]
    for t in WO.INTRO:
        main += say(t)
    main += say(WO.HOW) + fade_out + \
        [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), asm.setbyte(PART, 0), asm.setbyte(SEEN, 1),
         asm.setword(HITS, 0), asm.setword(PAY, 0), asm.setword(REPS, 0)] + \
        [hb._req(E[a], 3, wait=False) for a in actors("A")] + [hb._req(E["camera"], 2, wait=False), hb._w(20)] + fade_in

    def part_loop(part):
        n = len(WO.PERIODS)
        rep, wait, judge, hit, miss, after, out, tail = (asm.nop() for _ in range(8))
        ops = [rep] + [hb._req(E[a], 2, wait=False) for a in actors(part)]
        ops += ch(TIER, [[asm.setword(PER, p)] for p in WO.PERIODS])
        ops += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])),   # RANDOM, MOD 3
                asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])),   # KP = KEY + 1
                asm.setbyte(PR, 0), asm.setword(CNT, 0)]
        ops += ch(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)])
        # frames: back round while nothing is pressed and CNT < PER (IFs only jump forward)
        ops += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),                 # INC2
                asm.if_byte(PR, "==", 0, judge), asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait)]
        ops += [judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss)]
        # a hit: pay, streak, maybe a tier up (and its lines the first time)
        ops += [hit, Op(bytes([0x96, HITS[0], HITS[1]])), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])),
                Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(TIER, "<", n - 1, after),
                asm.if_byte(STREAK, ">=", WO.HITS_UP, after), Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)]
        lines = group_a if part == "A" else group_b
        for t in range(1, n):
            nx = asm.nop()
            if t in lines:
                ops += [asm.if_byte(TIER, "==", t, nx), asm.if_byte(SEEN, "bit_off", t, nx), asm.biton(SEEN, t),
                        req(E["talk"], lines[t]), nx]
        rest = asm.nop()
        ops += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                asm.goto_back(rest), tail]
        done = asm.nop()
        if part == "A":                                                 # PART_A_END hits into the top tier
            ops += [asm.if_byte(TIER, "==", n - 1, done), asm.if_byte(STREAK, ">=", WO.PART_A_END, done), asm.goto(out), done]
        else:
            ops += [Op(bytes([0x96, REPS[0], REPS[1]])), asm.if_word(REPS, ">=", WO.PART_B_REPS, done), asm.goto(out), done]
        ops += [asm.goto_back(rep)]
        # a miss: the buzz, back to the slowest pace (a line if it was fast), the rest of the rep, then the
        # part's check above (a backward jump: JMPB)
        slow, mtail, mdone = asm.nop(), asm.nop(), asm.nop()
        ops += [miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), asm.if_byte(TIER, ">=", 2, slow),
                req(E["talk"], miss_a if part == "A" else miss_b), slow,
                asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), mtail, asm.if_word(CNT, "<", PER, mdone),
                hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(mtail), mdone, asm.goto_back(tail)]
        return ops, out

    ops_a, out_a = part_loop("A")
    main += ops_a + [out_a] + fade_out + [Op(b"\x54\x02")] + \
        [hb._req(E[a], 4, wait=False) for a in actors("A")] + \
        [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), asm.setbyte(PART, 1), asm.setbyte(SEEN, 1)] + \
        [hb._req(E[a], 3, wait=False) for a in actors("B")] + [hb._w(20)] + fade_in
    for t in WO.START_B:
        main += say(t)
    ops_b, out_b = part_loop("B")
    main += ops_b + [out_b, Op(b"\x54\x01"), Op(b"\x54\x02"), hb._w(30)]
    for t in WO.FINALE:
        main += say(t)
    main += [asm.setword(GIL, PAY), hb._arith(0x8A, GIL, WO.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(WO.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))       # MPRA2 after WINDOW
    main += paid + fade_out
    rx, ry, rz, rt, rdir = ctx.movie_back
    stop = hb._w(30)
    # (Square presses here set 680's affection-list flag through its exe hook: cleared, or the list would
    # open back at the station)
    main += [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir),
             stop, asm.goto_back(stop)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    return n_text, len(f.sections[0])


def apply(ctx):
    donor, stand = _spandex(ctx)
    poses = WP.build(ctx, {"A": (SPANDEX_HRC, stand, HER_A), "B": (BARE_TIED, stand, HER_B)})
    n_text, size = _set(ctx, donor, stand, poses)
    print("  683: Sector 7 Workout on %s (spandex Tifa %s; %d tiers a part; %d texts, script %d bytes)"
          % (WO.FIELD, SPANDEX_HRC, len(WO.PERIODS), n_text, size))

"""(user) Sector 7 Workout: the first parody film (data `_workout.py`, poses `_workout_poses.py`), shot in the
Wall Market gym. Tifa comes in for the first time looking for a trainer; Cloud spots her squats from behind.

The minigame: one squat a rep, one prompt a rep ([SWITCH] / [CANCEL] / [OK] at random, as the squat
contest names its buttons) in a window the player can't close; the right button before the rep ends is a
hit, anything else (or nothing) a miss. HITS_UP hits in a row step the pace up a tier (PERIODS: frames a
rep); a miss drops it back to the slowest. Each new tier the first time: a pair of lines (tips, questions,
then at tier 4 the 'training device'). Part one (clothed) lasts PART_A_REPS prompts (user: fixed length): fade,
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
import _danger as DG
import _director as DR
import _gestures as GS
import _workout as WO
import _workout_poses as WP
import _circuit_poses as CP
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera, facing_screen
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

SPANDEX_HRC = "XWTA.HRC"
BARE_TIED = "XWUA.HRC"              # the film's own copy of her undressed model (ZTFA), hair tied up
TAG = "W"
TOP_HRC, TOP_TAG = "XWSA.HRC", "V"     # (user: undressing in stages) the leotard down to her waist
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
    # (user: her clothes come off in stages over the circuit) the leotard peeled down to her waist: the same
    # outfit with a bare chest (tag TOP_TAG, nipples as 675's)
    top = fb.apply(ctx, text, TOP_TAG, skin, None, 1.0, 0.8)
    if "armer" in fb.bones(top):
        lines = top.splitlines(True)
        k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "armer")
        lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), "0")
        top = "".join(lines)
    top = fb.nipples(ctx, top, TOP_TAG)
    fb.tifa_body(ctx, top, skin, 1.5, paints={"hip": ([], lambda c: PINK)})
    bn = fb.bones(top)
    for b, col in [("l_femur", TEAL), ("r_femur", TEAL), ("l_tibia", YELLOW), ("r_tibia", YELLOW)]:
        p = sd._ply(ctx, bn[b][1][0])
        ctx.char_file(p, sd._recolour(ctx.char_file(p), col))
    ctx.char_file(TOP_HRC.lower(), _tie(ctx, top).encode("latin-1"))
    bare = ctx.char_file(BARE_HRC.lower()).decode("latin-1")             # (675's; other scenes keep it long)
    ctx.char_file(BARE_TIED.lower(), _tie(ctx, bare).encode("latin-1"))
    stand = ModelLoader.anims(donor)[0].split(".")[0].lower() + ".a"
    return donor, stand


# ---- the set ------------------------------------------------------------------------------------------------
TIER, STREAK, KEY, PR, PART, SEEN, RND, KP, CHAT, LN = ((5, a) for a in range(100, 110))
TALKING = (5, 127)                  # set while the talk entity shows lines (no chatter over it)
CNT, HITS, PAY, REPS, PER, GIL = ((6, a) for a in range(110, 122, 2))
PRV = [(5, 124 + k) for k in range(3)]
# (user: more going on) HELD bit k while button k is down; HOLD this rep is a hold (1) / a spot (2); STYLE the
# pose's variation, SC reps since it changed; ANGER her strikes; HC / CUE the hold's frame count / her call's
# frame; IX = STYLE x tiers + TIER (the actors' anim and spot at the station); CL the prompt window's line
HELD, HOLD, STYLE, SC, ANGER, HC, CUE, IX, CL = ((5, a) for a in range(128, 137))
METER, SIDE, DEC = (5, 137), (5, 138), (5, 139)     # (user) the danger meter (`_danger`)
# (user: the circuit) ST the station; START the next station's starting tier (her mood after the choice); MOOD
# the mood points (paid at the end); DARE 0 none / 1 a sprint / 2 a clean streak, DN its reps left, DF lost,
# DK its kind (0 / 1); SPC the spot's presses
ST, START, MOOD, DARE, DN, DF, DK, SPC = ((5, a) for a in range(140, 148))
# the actors: entity -> (model, {station: the station's first anim index in the model})
# (in model order: the engine hands out models by the order the entities' CHARs run; tifaC before cloudB showed
# two Clouds on the bench and two Tifas on the floor, user)
ACTORS = ["cloudA", "tifaA", "cloudB", "tifaB", "tifaC"]


def _set(ctx, donor, stand, poses, circ):
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

    def tri(x, y, z=0):
        t = mesh.find(round(x), round(y))
        assert t is not None, ("off the floor", x, y)
        assert abs(sum(v[2] for v in mesh.tris[t]) / 3 - z) < 12, ("wrong level", x, y, z, mesh.tris[t])
        return t
    n = len(WO.PERIODS)
    SN = WO.STATIONS
    STY = [WP.STYLES["A"], 2, 1, WP.STYLES["B"]]                     # styles per station
    combos = [[(sy_, t) for sy_ in range(STY[k]) for t in range(n)] for k in range(4)]
    # the stations' spots: squats / ring = Tifa on the spot facing screen-left, Cloud `gap` behind her (per part,
    # style and tier); bench / stretch = both on the anchor (the offsets are in their anims)
    sx, sy = WO.SQUAT_AT
    rx, ry = WO.RING_AT
    d0 = facing_screen(cam, sx, sy, 0, WO.FACING)
    d3 = facing_screen(cam, rx, ry, WO.RING_Z, WO.FACING)
    (fx_, fy_), (nx_, ny_) = WO.PRESS_FAR, WO.PRESS_NEAR
    ln = math.hypot(nx_ - fx_, ny_ - fy_)
    u = ((nx_ - fx_) / ln, (ny_ - fy_) / ln)
    pa = (round(fx_ - u[0] * CP.BENCH_START * CP.U), round(fy_ - u[1] * CP.BENCH_START * CP.U))
    d1 = dt._dir_to(*u)
    s2 = WO.STRETCH_AT
    d2 = facing_screen(cam, s2[0], s2[1], 0, WO.FACING)

    def behind(part, st, t, at, d):
        ox, oy, _ = mv._off((0, 0, WP.gap(part, t, st)), d)
        return round(at[0] + ox), round(at[1] + oy)

    def spot(k, who, sy_, t):
        """(x, y, z, DIR) of `who` ('c' / 't') at station k, style sy_, tier t."""
        if k == 0:
            return (sx, sy, 0, d0) if who == "t" else behind("A", sy_, t, (sx, sy), d0) + (0, d0)
        if k == 3:
            return (rx, ry, WO.RING_Z, d3) if who == "t" else behind("B", sy_, t, (rx, ry), d3) + (WO.RING_Z, d3)
        return (pa + (0, d1)) if k == 1 else (tuple(s2) + (0, d2))
    # models: 0 the hidden player, 1 Cloud (squats, bench), 2 spandex Tifa (squats), 3 bare Cloud (stretch, ring),
    # 4 bare Tifa (stretch, ring), 5 top-off Tifa (bench), the Director; each actor's anims: its stand, then
    # each of its stations' (style, tier) blocks
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    stand_c = ModelLoader.anims(cl0)[0]                              # ACFE
    stand_t = ModelLoader.anims(donor)[0]                            # ABCD
    hers = lambda part: sum((poses[(part, st)][0] for st in range(WP.STYLES[part])), [])
    his = lambda part: sum((poses[(part, st)][1] for st in range(WP.STYLES[part])), [])
    press_h = circ[("press", 0)][0] + circ[("press", 1)][0]
    press_c = circ[("press", 0)][1] + circ[("press", 1)][1]
    str_h, str_c = circ[("stretch", 0)]
    ACT = {"cloudA": (1, {0: 1, 1: 1 + 3 * n}), "tifaA": (2, {0: 1}), "tifaC": (5, {1: 1}),
           "cloudB": (3, {2: 1, 3: 1 + n}), "tifaB": (4, {2: 1, 3: 1 + n})}
    G = WO.INTRO_GESTURES
    loader.models = [cl0,
                     ModelLoader.only_anims(cl0, [stand_c] + his("A") + press_c + GS.anims(ctx, G, "cloud", "cloud")),
                     ModelLoader.only_anims(ModelLoader.with_hrc(donor, SPANDEX_HRC, "workout_tifa.char"),
                                            [stand_t] + hers("A") + GS.anims(ctx, G, "tifa", "tifa")),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "workout_cloudb.char"),
                                            [stand_c] + str_c + his("B")),
                     ModelLoader.only_anims(ModelLoader.with_hrc(donor, BARE_TIED, "workout_tifab.char"),
                                            [stand_t] + str_h + hers("B")),
                     ModelLoader.only_anims(ModelLoader.with_hrc(donor, TOP_HRC, "workout_tifac.char"),
                                            [stand_t] + press_h)]
    # (the donor's scale: Tifa comes from a 768 field; add_from rescales to this one)
    for k in (2, 4, 5):
        tmp = ModelLoader(ctx.field(DONOR[0]).section("models"))
        tmp.models = [loader.models[k]]
        j = loader.add_from(tmp, 0)
        loader.models[k] = loader.models.pop(j)
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    cam_anims = ModelLoader.anims(loader.models[cm])
    film = cam_anims.index(mv.CAMERA_FILM)
    loader.models[cm] = ModelLoader.only_anims(loader.models[cm], cam_anims + [mv.CAMERA_STILL])
    still = len(cam_anims)
    foci = []
    for k, (x, y) in enumerate(WO.FOCI):
        t_ = mesh.find(x, y)
        foci.append((x, y, round(sum(v[2] for v in mesh.tris[t_]) / 3), t_))
    meter = DG.build(ctx, f, loader, "L", [q[:3] for q in foci])          # (user) the danger meter, a view a station
    assert len(loader.models) == 9, len(loader.models)
    assert all(len(ModelLoader.anims(m)) <= 47 for m in loader.models), [len(ModelLoader.anims(m)) for m in loader.models]
    for ent, (m, bases) in ACT.items():                              # (each block where it's expected)
        for k, b in bases.items():
            assert b + len(combos[k]) <= len(ModelLoader.anims(loader.models[m])), (ent, k)
    # entities
    names = ["produce", "cloud"] + ACTORS + ["camera", "k_sw", "k_ca", "k_ok", "prompt", "talk", "hush", "gauge",
                                             "cursor"]
    sec.entity_names = [nm.encode("latin-1").ljust(8, b"\0") for nm in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {nm: i for i, nm in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]               # TLKON 01, SOLID 01
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    canm = lambda i, a, b: [mv._animb(), Op(bytes([0xBC, i, a, b, 1]))]     # CANM!2: frames a..b, then held
    ch, sparse = mv._chain, mv._sparse
    face = lambda x, y, tx, ty: dt._dir_to(tx - x, ty - y)
    scripts = {}
    # the hidden player (the camera's focus): slot 2 = the station's focus
    fx, fy, fz, ft = foci[0]
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(fx, fy, fz, ft), hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()],
                           2: ch(ST, [[xyzi(*q)] for q in foci]) + [asm.ret()]}
    ix, iy = WO.INTRO_TIFA
    cx_, cy_ = WO.INTRO_CLOUD
    bottom = lambda t: WO.PERIODS[t] // 2
    # the actors: init hidden / at the intro (cloudA, tifaA); slot 2 = place + the anim by ST and IX from its start
    # (only when the station, tier or style changes); 3 = the same and shown; 4 = hidden; 5 = the hold (the anim's
    # bottom frame held); 6 (hers) = her call: rising a little from the bottom and straining there
    for ent in ACTORS:
        model, bases = ACT[ent]
        who = "t" if ent.startswith("tifa") else "c"
        if ent in ("cloudA", "tifaA"):
            at = (ix, iy, face(ix, iy, cx_, cy_)) if who == "t" else (cx_, cy_, face(cx_, cy_, ix, iy))
            init = [Op(bytes([0xA1, model])), xyzi(at[0], at[1], 0, tri(at[0], at[1])), d_(at[2]), hb._visi(1)] + \
                hide() + loop_(0)
        else:
            init = [Op(bytes([0xA1, model])), hb._visi(0)] + hide()
        place, anim, held, cue = [], [], [], []
        for k in range(4):
            if k not in bases:
                for lst in (place, anim, held, cue):
                    lst.append([])
                continue
            pl = []
            for sy_, t in combos[k]:
                x, y, z, dd = spot(k, who, sy_, t)
                pl.append([xyzi(x, y, z, tri(x, y, z)), d_(dd)])
            place.append(ch(IX, pl))
            anim.append(ch(IX, [loop_(bases[k] + j) for j in range(len(combos[k]))]))
            held.append(ch(IX, [canm(bases[k] + j, bottom(t), bottom(t)) for j, (sy_, t) in enumerate(combos[k])]))
            cue.append(ch(IX, [canm(bases[k] + j, bottom(t), bottom(t) + max(2, WO.PERIODS[t] // 7))
                               for j, (sy_, t) in enumerate(combos[k])]))
        sc = {0: init + [asm.ret(), asm.ret()],
              2: sparse(ST, [p_ + a_ for p_, a_ in zip(place, anim)]) + [asm.ret()],
              3: sparse(ST, [p_ + [hb._visi(1)] + a_ for p_, a_ in zip(place, anim)]) + [asm.ret()],
              4: [hb._visi(0), asm.ret()],
              5: sparse(ST, held) + [asm.ret()]}
        if who == "t":
            sc[6] = sparse(ST, cue) + [asm.ret()]
        if ent in ("cloudA", "tifaA"):                                   # (user: variety) the intro's gestures
            actor = "tifa" if who == "t" else "cloud"
            first = 1 + len(hers("A")) if who == "t" else 1 + len(his("A")) + len(press_c)
            sc.update(GS.slots(G, actor, first, 0, mv._animb()))
        scripts[E[ent]] = sc
    # (user: "move him up and left away from Tifa and Cloud") the Director screen-left of the station, clear of both
    keeps = [[(sx, sy, 0), (sx, sy, 80)] + [(*behind("A", sy_, t, (sx, sy), d0), z) for sy_ in range(STY[0])
                                            for t in (0, n - 1) for z in (0, 95)],
             [(pa[0] + u[0] * a, pa[1] + u[1] * a, z) for a in (-15, 0, 40, 90) for z in (0, 95)],
             [(s2[0] + dx, s2[1], z) for dx in (-60, 0, 30) for z in (0, 70)],
             [(rx, ry, WO.RING_Z), (rx, ry, WO.RING_Z + 80)] +
             [(*behind("B", sy_, t, (rx, ry), d3), z) for sy_ in range(STY[3]) for t in (0, n - 1)
              for z in (WO.RING_Z, WO.RING_Z + 95)]]
    dspots = []
    for k, keep in enumerate(keeps):
        floor = lambda x, y: abs(sum(v[2] for v in mesh.tris[mesh.find(round(x), round(y))]) / 3) < 3   # (not a bench)
        q = DR.spot(f, keep, side=-1, gap=WO.CAMERA_GAP, lift=WO.CAMERA_LIFT, fit=floor)
        assert q is not None, k
        c = keep[0]
        dspots.append((q, face(q[0], q[1], c[0], c[1])))
        print("  683: the Director at", q[:3], "for", SN[k]["key"])
    (mx, my, mz, mt), md = dspots[0]
    scripts[E["camera"]] = {0: [Op(bytes([0xA1, cm])), xyzi(mx, my, mz, mt), d_(md), hb._visi(1)] + hide() +
                            loop_(still) + [asm.ret(), asm.ret()],
                            2: loop_(film) + [asm.ret()],
                            5: ch(ST, [[xyzi(*q), d_(dd)] for q, dd in dspots]) + [asm.ret()]}
    # the buttons: one small entity each (8 ops a frame): a press = up -> down; PR = its number; HELD bit k
    # while it's down
    for k, (mask, _) in enumerate(WO.KEYS):
        top, up, held_ = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),     # IFKEY: not held -> up
                asm.if_byte(PRV[k], "==", 0, held_),                                   # held before: nothing new
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held_, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    # the prompt: window 1, can't be closed by the player; the director closes it (WCLSE 01). Slots 2-4 the
    # buttons, 5-7 HOLD + the button, 8 the spot, then the holds' / spots' lines (one slot per pool, its line by CL)
    pr = {0: [asm.ret(), asm.ret()]}
    labels = [l for _, l in WO.KEYS] + [WO.HOLD_LABEL + l for _, l in WO.KEYS] + [WO.SPOT_LABEL]
    for k, label in enumerate(labels):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + k] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, WO.PROMPT_Y, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    spot_slot = 2 + len(labels) - 1
    pslot = 2 + len(labels)
    hold_pools = {}
    for key, pool in (("holdA", WO.HOLDS_A), ("holdB", WO.HOLDS_B), ("holdS", WO.HOLDS_S), ("cueA", WO.CUES_A),
                      ("cueB", WO.CUES_B), ("cueS", WO.CUES_S), ("goodA", WO.GOOD_A), ("goodB", WO.GOOD_B),
                      ("goodS", WO.GOOD_S), ("earlyA", WO.EARLY_A), ("earlyB", WO.EARLY_B), ("earlyS", WO.EARLY_S),
                      ("madA", WO.MAD_A), ("madB", WO.MAD_B), ("madS", WO.MAD_S), ("spotgood", WO.SPOT_GOOD),
                      ("spotfail", WO.SPOT_FAIL)):
        hold_pools[key] = (pslot, len(pool))
        pr[pslot] = [Op(b"\x52\x01\x00\x01")] + ch(CL, [[hb._window(x, 1, 8, WO.PROMPT_Y), asm.message(1, mv._text_id(sec, x))]
                                                        for x in pool]) + [asm.ret()]
        pslot += 1
    assert pslot <= 32, pslot
    scripts[E["prompt"]] = pr
    # the talk during the reps: window 2, each line shut by hush after SAY; slots: each station's tier lines (the
    # first time), each station's style lines (when it starts), then one slot per pool (chatter / misses, a
    # station's; her plea when she stalls on the bench) showing its line number LN; TALKING while busy
    def show(text):
        return [Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, WO.LINE_Y), hb._req(E["hush"], 2, wait=False),
                asm.message(2, mv._text_id(sec, text))]
    talk = {0: [asm.ret(), asm.ret()]}
    slot = 2
    PARTS = [s_["part"] for s_ in SN]
    TLINES = {"A": WO.LINES_A, "P": WO.LINES_P, "S": WO.LINES_S, "B": WO.LINES_B}
    SLINES = {"A": WO.STYLE_A, "P": WO.STYLE_P, "S": WO.STYLE_S, "B": WO.STYLE_B}
    groups, styles, pools = {}, {}, {}
    for part in PARTS:
        groups[part] = {}
        for t in sorted(TLINES[part]):
            groups[part][t] = slot
            talk[slot] = [asm.setbyte(TALKING, 1)] + sum((show(x) for x in TLINES[part][t]), []) + \
                [asm.setbyte(TALKING, 0), asm.ret()]
            slot += 1
    for k, part in enumerate(PARTS):
        assert len(SLINES[part]) == STY[k]
        styles[part] = slot
        talk[slot] = [asm.setbyte(TALKING, 1)] + ch(STYLE, [sum((show(x) for x in ls), []) for ls in SLINES[part]]) + \
            [asm.setbyte(TALKING, 0), asm.ret()]
        slot += 1
    for key, pool in (("chatA", WO.CHAT_A), ("chatB", WO.CHAT_B), ("chatP", WO.CHAT_P), ("chatS", WO.CHAT_S),
                      ("missA", WO.MISSES_A), ("missB", WO.MISSES_B), ("missP", WO.MISSES_P), ("missS", WO.MISSES_S),
                      ("spot", WO.SPOTS)):
        pools[key] = (slot, len(pool))
        talk[slot] = [asm.setbyte(TALKING, 1)] + ch(LN, [show(x) for x in pool]) + [asm.setbyte(TALKING, 0), asm.ret()]
        slot += 1
    assert slot <= 32, slot
    scripts[E["talk"]] = talk
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(WO.SAY), Op(b"\x54\x02"), asm.ret()]}
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))     # REQ: never waits (the talk may be busy)
    rnd = lambda var, size: [Op(bytes([0x99, var[0], var[1]])), Op(bytes([0x8D, var[0] << 4, var[1], size]))]

    def line_from(key):
        """A random line of a pool, unless someone's already talking."""
        sl, size = pools[key]
        busy = asm.nop()
        return [asm.if_byte(TALKING, "==", 0, busy)] + rnd(LN, size) + \
            [asm.setbyte(TALKING, 1), req(E["talk"], sl), busy]

    def prompt_line(key, pick=None):
        """A line of a prompt pool in the prompt window (random, or line `pick` var - 1)."""
        sl, size = hold_pools[key]
        if pick is None:
            ops = rnd(CL, size)
        else:
            ops = [asm.setbyte(CL, pick), Op(bytes([0x87, CL[0] << 4, CL[1], 1]))]     # MINUS
        return [hb._w(2)] + ops + [req(E["prompt"], sl)]                 # (its last line just closed)

    # the director
    say = lambda t: hb._say(sec, t)
    say_any = lambda pool: rnd(LN, len(pool)) + ch(LN, [say(x) for x in pool])
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    ix_ops = [asm.setbyte(IX, TIER)] + ch(STYLE, [[Op(bytes([0x85, IX[0] << 4, IX[1], n * st]))] if st else []
                                                  for st in range(max(STY))])
    main = [hb._uc(1), hb._menu(1), hb._w(20)] + fade_in + [Op(bytes([0xF2, 0, 0, 0, 0x10, WO.MUSIC]) + bytes(8))]
    for i, t in enumerate(WO.INTRO):
        main += GS.reqs(G, i, lambda a: E["tifaA" if a == "tifa" else "cloudA"]) + say(t)
    main += say(WO.HOW) + fade_out + \
        [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), asm.setbyte(PART, 0), asm.setbyte(SEEN, 1),
         asm.setbyte(CHAT, 0), asm.setbyte(TALKING, 0), asm.setbyte(HELD, 0), asm.setbyte(STYLE, 0),
         asm.setbyte(SC, 0), asm.setbyte(ANGER, 0), asm.setbyte(IX, 0), asm.setbyte(ST, 0), asm.setbyte(MOOD, 0),
         asm.setbyte(DARE, 0), asm.setword(HITS, 0), asm.setword(PAY, 0), asm.setword(REPS, 0)] + \
        [hb._req(E[a], 3, wait=False) for a in SN[0]["who"]] + [hb._req(E["camera"], 2, wait=False), hb._w(20)] + fade_in
    MG_ = (E["gauge"], E["cursor"])
    main += DG.start(METER, MG_)
    walkout, pay = asm.nop(), asm.nop()
    red, red_ops = DG.cut(say, MG_, pay)
    dmiss = lambda: DG.miss(METER, SIDE, RND, E["cursor"], red)

    def frames(var, limit):
        """Wait while var < limit, a frame each (IFs only jump forward: the loop is JMPB)."""
        top, done = asm.nop(), asm.nop()
        return [top, asm.if_byte(var, "<", limit, done), hb._w(1), Op(bytes([0x95, var[0], var[1]])),
                asm.goto_back(top), done]

    def bonus(times):
        return sum(([hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]]))] for _ in range(times)), [])

    def dare_lost():
        """(a miss during a dare) it's lost and ends at this rep's tail."""
        sk = asm.nop()
        return [asm.if_byte(DARE, "!=", 0, sk), asm.setbyte(DF, 1), asm.setbyte(DN, 1), sk]

    def station_loop(k):
        stn = SN[k]
        part = stn["part"]
        actors = stn["who"]
        sfx = "A" if part == "A" else "B" if part == "B" else "S"           # (hold pools)
        rep, wait, judge, hit, miss, after, out, tail = (asm.nop() for _ in range(8))
        # (the actors' anim loops; it changes only with the tier or style: slot 2 places them and starts it)
        restart = ix_ops + [hb._req(E[a], 2, wait=False) for a in actors]
        ops = [rep] + ch(TIER, [[asm.setword(PER, p)] for p in WO.PERIODS])
        ops += rnd(RND, 3) + [asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])),  # KP = KEY + 1
                              asm.setbyte(PR, 0), asm.setword(CNT, 0), asm.setbyte(HOLD, 0)]
        for kind, cfg in ((1, stn["hold"]), (2, stn["spot"])):                 # (user) now and then a hold / a spot
            if cfg:
                no = asm.nop()
                ops += [asm.if_byte(TIER, ">=", cfg[0], no), asm.if_byte(DARE, "==", 0, no), Op(bytes([0x99, RND[0], RND[1]]))] + \
                    [asm.if_byte(RND, "<", cfg[1], no), asm.setbyte(HOLD, kind), no]
        spot_ = asm.nop()
        if stn["spot"]:
            ops += [asm.if_byte(HOLD, "!=", 2, spot_)]
        ops += ch(HOLD, [ch(KEY, [[hb._req(E["prompt"], 2 + j, wait=False)] for j in range(3)]),
                         ch(KEY, [[hb._req(E["prompt"], 5 + j, wait=False)] for j in range(3)])])
        # frames: back round while nothing is pressed and CNT < PER (IFs only jump forward)
        hold = asm.nop()
        ops += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),                 # INC2
                asm.if_byte(PR, "==", 0, judge), asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait)]
        ops += [judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss), asm.if_byte(HOLD, "==", 0, hold)]
        # a hit: pay, streak, maybe a tier up (and its lines the first time)
        ops += [hit] + DG.hit(METER, E["cursor"]) + [Op(WO.HIT_SOUND), Op(bytes([0x96, HITS[0], HITS[1]]))] + bonus(1) + \
            [Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(TIER, "<", n - 1, after),
             asm.if_byte(STREAK, ">=", WO.HITS_UP, after), Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)] + \
            restart
        for t in range(1, n):
            nx = asm.nop()
            if t in groups[part]:
                ops += [asm.if_byte(TIER, "==", t, nx), asm.if_byte(SEEN, "bit_off", t, nx), asm.biton(SEEN, t),
                        req(E["talk"], groups[part][t]), nx]
        rest = asm.nop()
        quiet, same = asm.nop(), asm.nop()
        ops += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                asm.goto_back(rest), tail,
                Op(bytes([0x95, CHAT[0], CHAT[1]])), asm.if_byte(CHAT, ">=", WO.CHAT_EVERY, quiet),     # (user) chatter
                asm.setbyte(CHAT, 0)] + line_from("chat" + part) + [quiet]
        # (user: variations) every STYLE_EVERY reps the next style, its lines (unless someone's talking); not
        # during a dare (its pace is set)
        if STY[k] > 1:
            ops += [Op(bytes([0x95, SC[0], SC[1]])), asm.if_byte(SC, ">=", WO.STYLE_EVERY, same),
                    asm.if_byte(DARE, "==", 0, same), asm.setbyte(SC, 0), Op(bytes([0x95, STYLE[0], STYLE[1]]))]
            wrap = asm.nop()
            ops += [asm.if_byte(STYLE, ">=", STY[k], wrap), asm.setbyte(STYLE, 0), wrap] + restart
            busy = asm.nop()
            ops += [asm.if_byte(TALKING, "==", 0, busy), asm.setbyte(TALKING, 1), asm.setbyte(CHAT, 0),
                    req(E["talk"], styles[part]), busy, same]
        ops += [Op(bytes([0x96, REPS[0], REPS[1]]))]
        # (user) Tifa's dares: one counts down / is settled at the tail of every rep; she sets one at rep `dare`
        nod, settle = asm.nop(), asm.nop()
        ops += [asm.if_byte(DARE, "!=", 0, nod), Op(bytes([0x87, DN[0] << 4, DN[1], 1])),        # MINUS
                asm.if_byte(DN, "==", 0, nod), Op(b"\x54\x02")]
        won = [Op(bytes([0xF1, 0, 0xEA, 1, 0x40]))] + bonus(WO.DARE_BONUS) + say_any(WO.DARE_WON)
        ops += ch(DF, [won, say_any(WO.DARE_LOST)]) + [asm.setbyte(DARE, 0), nod]
        if stn["dare"]:
            nodare = asm.nop()
            ops += [asm.if_word(REPS, "==", stn["dare"], nodare), asm.if_byte(DARE, "==", 0, nodare),
                    Op(b"\x54\x02")] + rnd(DK, 2) + [asm.setbyte(DARE, DK), Op(bytes([0x95, DARE[0], DARE[1]])),
                                                     asm.setbyte(DF, 0)]
            ops += ch(DK, [[asm.setbyte(DN, WO.DARE_SPRINT)] + say(WO.DARES[0][k % 2]) +
                           [asm.setbyte(TIER, n - 1), asm.setbyte(STREAK, 0)] + restart,
                           [asm.setbyte(DN, WO.DARE_CLEAN)] + say(WO.DARES[1][k % 2])]) + [nodare]
        # (user: fixed length, progression by performance) a fixed number of prompts a station
        done = asm.nop()
        ops += [asm.if_word(REPS, ">=", stn["reps"], done), asm.goto(out), done]
        ops += [asm.goto_back(rep)]
        # a miss: the buzz, back to the slowest pace (a line if it was fast), the rest of the rep, then the
        # tail above (a backward jump: JMPB)
        slow, mtail, mdone = asm.nop(), asm.nop(), asm.nop()
        drop = [asm.if_byte(TIER, "!=", 0, slow), asm.setbyte(TIER, 0)] + restart + [slow, asm.setbyte(STREAK, 0)]
        ops += [miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40]))] + dmiss() + dare_lost() + \
            line_from("miss" + part) + [asm.setbyte(CHAT, 0)] + drop + \
            [mtail, asm.if_word(CNT, "<", PER, mdone),
             hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(mtail), mdone, asm.goto_back(tail)]
        result = lambda: [asm.setbyte(HC, 0)] + frames(HC, WO.RESULT_WAIT) + [Op(b"\x54\x01")]
        if stn["hold"]:
            # (user) the hold: both freeze at the bottom (he holds her down) until she calls it; let go in time =
            # a hit plus a bonus; before her call = a miss; too late = she's mad (MAD_LIMIT: she walks out)
            early, cue, good, late, calm = (asm.nop() for _ in range(5))
            ops += [hold] + [hb._req(E[a], 5, wait=False) for a in actors] + prompt_line("hold" + sfx) + \
                rnd(CUE, WO.HOLD_RANGE) + [Op(bytes([0x85, CUE[0] << 4, CUE[1], WO.HOLD_MIN])), asm.setbyte(HC, 0)]
            hw, lw = asm.nop(), asm.nop()
            ops += [hw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, early), Op(bytes([0x95, HC[0], HC[1]])),
                    asm.if_byte(HC, "<", CUE, cue), asm.goto_back(hw)]
            ops += [cue, Op(b"\x54\x01"), hb._req(E[actors[1]], 6, wait=False)] + prompt_line("cue" + sfx) + \
                [asm.setbyte(HC, 0), lw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, good), Op(bytes([0x95, HC[0], HC[1]])),
                 asm.if_byte(HC, "<", WO.LETGO, late), asm.goto_back(lw)]
            # let go in time: the materia chime, the bonus, a line, then counted as a hit
            ops += [good, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 0xEA, 1, 0x40]))] + bonus(WO.HOLD_BONUS) + \
                prompt_line("good" + sfx) + restart + result() + [asm.goto_back(hit)]
            # too soon: a miss
            ops += [early, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40]))] + dmiss() + dare_lost() + \
                prompt_line("early" + sfx) + [asm.setbyte(TIER, 0)] + restart + [asm.setbyte(STREAK, 0)] + result() + \
                [asm.goto_back(tail)]
            # too late: she's mad
            ops += [late, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x95, ANGER[0], ANGER[1]])),
                    asm.if_byte(ANGER, ">=", WO.MAD_LIMIT, calm), asm.goto(walkout), calm] + \
                dmiss() + dare_lost() + prompt_line("mad" + sfx, ANGER) + [asm.setbyte(TIER, 0)] + restart + \
                [asm.setbyte(STREAK, 0)]
            zero, paid_ = asm.nop(), asm.nop()
            ops += [asm.if_word(PAY, "<", WO.MAD_PENALTY, zero), hb._arith(0x88, PAY, WO.MAD_PENALTY), asm.goto(paid_),
                    zero, asm.setword(PAY, 0), paid_] + result() + [asm.goto_back(tail)]
        else:
            ops += [hold, asm.goto_back(hit)]                       # (no holds here: HOLD stays 0)
        if stn["spot"]:
            # (user: the bench) she stalls at the bottom: mash [OK] SPOT_NEED times within SPOT_FRAMES; done = the
            # chime, a bonus and a hit; else a miss (she's pinned)
            sw, sgood, sfail, notok = (asm.nop() for _ in range(4))
            ops += [spot_] + [hb._req(E[a], 5, wait=False) for a in actors] + \
                [hb._req(E["prompt"], spot_slot, wait=False)] + line_from("spot") + \
                [asm.setbyte(SPC, 0), asm.setbyte(HC, 0), asm.setbyte(PR, 0)]
            ops += [sw, hb._w(1), asm.if_byte(PR, "==", 3, notok), Op(bytes([0x95, SPC[0], SPC[1]])), notok,
                    asm.setbyte(PR, 0), asm.if_byte(SPC, "<", WO.SPOT_NEED, sgood), Op(bytes([0x95, HC[0], HC[1]])),
                    asm.if_byte(HC, "<", WO.SPOT_FRAMES, sfail), asm.goto_back(sw)]
            ops += [sgood, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 0xEA, 1, 0x40]))] + bonus(WO.SPOT_BONUS) + \
                prompt_line("spotgood") + restart + result() + [asm.goto_back(hit)]
            ops += [sfail, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40]))] + dmiss() + dare_lost() + \
                prompt_line("spotfail") + [asm.setbyte(TIER, 0)] + restart + [asm.setbyte(STREAK, 0)] + result() + \
                [asm.goto_back(tail)]
        return ops, out

    def move_on(k):
        """From station k to k + 1: her lines, the choice (mood, the next station's starting tier), fade, the
        actors changed / re-placed, the camera and the Director moved, fade in, the next station's lines."""
        nx_ = WO.NEXT[k]
        ops = [Op(b"\x54\x01"), Op(b"\x54\x02"), asm.setbyte(TALKING, 1)]
        for t in nx_["before"]:
            ops += say(t)
        text, opts = nx_["ask"]
        ask, first = hb._ask(sec, text, [o[0] for o in opts])
        ops += ask
        outs = asm.nop()
        for i, (_, mood, start, reply) in enumerate(opts):
            nxt = asm.nop()
            ops += [asm.if_byte(hb.CHOICE, "==", first + i, nxt), asm.setbyte(START, start)]
            if mood:
                ops += [Op(bytes([0x85, MOOD[0] << 4, MOOD[1], mood]))]
            ops += say(reply) + [asm.goto(outs), nxt]
        ops += [outs] + fade_out
        old, new_ = SN[k]["who"], SN[k + 1]["who"]
        ops += [hb._req(E[a], 4, wait=False) for a in old if a not in new_]
        ops += [asm.setbyte(ST, k + 1), asm.setbyte(TIER, START), asm.setbyte(STREAK, 0), asm.setbyte(SEEN, 1),
                asm.setword(REPS, 0), asm.setbyte(STYLE, 0), asm.setbyte(SC, 0), asm.setbyte(CHAT, 0),
                asm.setbyte(DARE, 0)] + ix_ops
        ops += [hb._req(E[a], 3, wait=False) for a in new_] + \
            [hb._req(E["cloud"], 2, wait=False), hb._req(E["camera"], 5), hb._req(E["camera"], 2, wait=False)] + \
            [req(e, 2) for e in MG_] + [hb._w(20)] + fade_in
        for t in nx_["after"]:
            ops += say(t)
        ops += [asm.setbyte(TALKING, 0)]
        return ops

    for k in range(len(SN)):
        ops_k, out_k = station_loop(k)
        main += ops_k + [out_k]
        if k + 1 < len(SN):
            main += move_on(k)
    main += [Op(b"\x54\x01"), Op(b"\x54\x02")] + \
        DG.finale(say, METER, PR, 3, CNT, DEC, MG_, PAY, hb._arith) + [hb._w(30)]   # (user) the finisher
    for t in WO.FINALE:
        main += say(t)
    main += [asm.goto(pay)]
    main += red_ops
    # (user) she walked out: she's gone, the Director's line, an affection point lost; paid what was earned
    main += [walkout, Op(b"\x54\x01"), Op(b"\x54\x02")] + DG.hide(MG_) + mv.lose_affection("tifa")
    walk = []
    for k, stn in enumerate(SN):
        lines_ = WO.WALKOUT_A if k == 0 else WO.WALKOUT_B
        walk.append(say(lines_[0]) + fade_out + [hb._req(E[stn["who"][1]], 4, wait=False), hb._w(10)] + fade_in +
                    sum((say(t) for t in lines_[1:]), []))
    main += ch(ST, walk)
    # pay: the earned PAY units plus the mood's, x PAY_HIT gil
    main += [pay]
    for _ in range(WO.MOOD_PAY):
        main += [hb._arith(0x86, PAY, MOOD)]
    main += [asm.setword(GIL, PAY), hb._arith(0x8A, GIL, WO.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(WO.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))       # MPRA2 after WINDOW
    main += paid + fade_out
    rx_, ry_, rz_, rt_, rdir = ctx.movie_back
    stop = hb._w(30)
    # (Square presses here set 680's affection-list flag through its exe hook: cleared, or the list would
    # open back at the station)
    main += [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx_, ry_, rt_, rdir),
             stop, asm.goto_back(stop)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    sc_ = DG.scripts(meter, METER, xyzi, view=ST)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    return n_text, len(f.sections[0])


def apply(ctx):
    donor, stand = _spandex(ctx)
    poses = WP.build(ctx, {"A": (SPANDEX_HRC, stand, HER_A), "B": (BARE_TIED, stand, HER_B)})
    # (user: the circuit) the bench (top off, clothed Cloud) and the stretch (both undressed), on the models
    circ = CP.build(ctx, (TOP_HRC, stand), (BARE_TIED, stand), ("AAAA.HRC", "acfe.a"),
                    (_mods()[1].CLOUD_BARE_HRC, "acfe.a"), {"press": ("QA", "QC"), "stretch": ("QD", "QG")})
    n_text, size = _set(ctx, donor, stand, poses, circ)
    print("  683: Sector 7 Workout on %s (a circuit of %d stations; %d texts, script %d bytes)"
          % (WO.FIELD, len(WO.STATIONS), n_text, size))

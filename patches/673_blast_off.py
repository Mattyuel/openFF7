"""(user) Blast-off: the movie's third scene type for a co-star (after Normal and Special), with Cid,
in the space capsule. Unlocked by Cid's affection at max (661 / `_cid`); the cameraman's menu is in
670 (Normal / Special / Blast-off, "????" while locked). Data `_blast_data.py`, poses
`_blast_poses.py`, bare Cid `_bare_cid.py`.

One set for every co-star: the capsule field itself (`_blast_data.SET`, rcktin7: only the story's
launch enters it; 660's capsule date was copied from it first), rebuilt from the original with a
blank script; the co-star at runtime (G, from MOVIE_GIRL as 670's set jumps), each girl her own
entity (her bare model, her retargeted poses) that does nothing unless she is G. Models: Cloud (the
hidden player), bare Cloud, bare Cid, the cameraman, gauge, cursor, Square icon, the six girls.
Entered only from the cameraman (`BLAST_ON`, cleared on arrival); any other entry goes back to Cid.

Three positions a minute each (`_blast_data.MINUTE`), the meter / presses / finisher as 672:
  rocketman  Cloud seated on the left bench thrusting up, she in his lap facing his way, bent forward
             to Cid standing on the floor (his right hand on her head); hold = Cid's (his lines).
  twinjets   she kneels in the gangway, Cloud and Cid standing either side; she faces one, turns to
             the other every `SWITCH` frames (her turn anim, through facing the camera); the man
             she faces thrusts, the other stands; one hold prompt per man (his lines).
  exhaust    Cloud and her in the carry (lower: `_blast_poses.exhaust_carry`), Cid behind her;
             "there" prompted twice (670 `_there_ops`, her profile).
Pay: her gil a press x `PAY_X` (presses doubled for the deferred cut; hold / there / finisher at
the doubled rate). Music: Cid's Theme."""
import importlib
import math
import struct

import _bare_cid
import _blast_data as BD
import _blast_poses as BP
import _cid as CID
import _movie_girls as MG
import _movie_group as GR
import _movie_profiles as PF
from _config import HB_MINUTES, MOVIE_AT, MOVIE_GIRL, MOVIE_PRESSES, MOVIE_STATE
from _recruit import sound
from ff7 import asm
from ff7.camera import Camera, facing_screen, screen_range
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

BLAST_ON = BD.BLAST_ON
G, SIDE, SEG, SPK, SW = (5, 163), (5, 164), (5, 165), (5, 166), (6, 168)   # co-star; Twin Jets: facing Cid,
                                  # halves done, the hold's speaker (0 Cloud, 1 Cid), next switch frame
BENCH_DROP = 34 / 3.41            # the bench top above the floor (model units; asserted on the walkmesh)
# spots (field units; the capsule: floor strips x 21..62 and -64..-20 at z 0, y 89..230, the gangway
# between them (no walkmesh, drawn level), benches z 34: screen-left x 54..90): (x, y, DIR)
ROCKET_SEAT = (72, 211, 0xC0)     # Cloud on the screen-left front bench, facing across (-x)
TWIN_CLOUD = (40, 175, 0xC0)      # Twin Jets: Cloud on the left strip facing -x; she 38 from him, Cid mirrored
EXHAUST_CLOUD = (40, 160, 0xC0)   # Exhaust: Cloud (and her) on the left strip, Cid behind her
CAM_AT = (-72, 140)               # the cameraman on the screen-right back bench
INTRO = {"cloud": (40, 120, 0xC0), "girl": (35, 200, 0xC0), "cid": (-40, 160, 0x40)}
ARRIVE = BD.ARRIVE
TWIN_ICON_IN = 120                # Twin Jets: each man's hold prompt this far into his first half
NO_ICON = 65000
SPRITES = {"QGFA": ("QGFB", "QGFC", "QGFD"), "QCFA": ("QCFB", "QCFC", "QCFD"), "QHFA": ("QHFB", "QHFC", "QHFD")}


def _mods():
    return (importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"),
            importlib.import_module("672_movie_special"), importlib.import_module("660_dates"))


def _her_in_his():
    """Her origin in Cloud's frame in the movie's head layout (670 POSITIONS "head": she faces him)."""
    mv = importlib.import_module("670_movie")
    head = [p for p in mv.POSITIONS if p["name"] == "head"][0]
    (gx, gy, _, gd), (cx, cy, _, cd) = head["girl"][1], head["cloud"][1]
    want = (gx - cx, gy - cy)
    ax, az = mv._off((1, 0, 0), cd), mv._off((0, 0, 1), cd)
    det = ax[0] * az[1] - az[0] * ax[1]
    m0 = (want[0] * az[1] - az[0] * want[1]) / det
    m2 = (ax[0] * want[1] - want[0] * ax[1]) / det
    got = mv._off((m0, 0, m2), cd)
    assert abs(got[0] - want[0]) < 1e-6 and abs(got[1] - want[1]) < 1e-6 and (gd - cd) % 256 == 128, (got, want)
    return [m0, 0.0, m2]


def _poses(ctx):
    """Every pose; returns (girl names on Ruby's skeleton, Cloud names, Cid names, layout), each
    actor's list: 4 speeds per position (S rocketman, T twinjets, U exhaust), then pulled back (9)
    and deepest (8) for S and T; hers then her tries (7) for S and T and her turns V0 / V1."""
    from ff7 import fieldanim as fa
    mv = importlib.import_module("670_movie")
    _bare_cid.build(ctx)
    lay = {"rocket": BP.rocketman(ctx, BENCH_DROP), "her": _her_in_his()}
    BP.twinjets(ctx, lay["her"])
    lay["exhaust"] = BP.exhaust(ctx)
    src = {"girl": ("zmsa.a", "zrta.a", "zmuk.a"), "cloud": ("znsa.a", "zctq.a", "znuk.a"),
           "cid": ("zgsa.a", "zgta.a", "zgua.a")}
    pre = {"girl": "ZM", "cloud": "ZN", "cid": "ZG"}
    out = {k: [] for k in src}
    for who, files in src.items():
        for letter, f_ in zip("STU", files):
            frames = fa.Anim(ctx.char_file(f_)).frames
            assert len(frames) == 15, (f_, len(frames))
            for s, n in enumerate(mv.SPEEDS):
                a = fa.Anim(ctx.char_file(f_))
                a.frames = [frames[i * len(frames) // n] for i in range(n)]
                name = "%s%s%d" % (pre[who], letter, s)
                ctx.char_file(name.lower() + ".a", a.build())
                out[who].append(name + ".tor")
        for digit, frame in (("9", 0), ("8", 7)):
            for letter, f_ in zip("ST", files):
                a = fa.Anim(ctx.char_file(f_))
                a.frames = a.frames[frame:frame + 1]
                name = "%s%s%s" % (pre[who], letter, digit)
                ctx.char_file(name.lower() + ".a", a.build())
                out[who].append(name + ".tor")
    for letter, f_ in zip("ST", ("ZMSA", "ZRTA")):
        mv._try_anim(ctx, f_, "ZM%s7" % letter)
        out["girl"].append("ZM%s7.tor" % letter)
    out["girl"] += ["ZMV0.tor", "ZMV1.tor"]
    out["cloud"] += [mv._lesson_anim(ctx, "ZNSA", "ZNSL"), "ZNJL.tor"]   # (user) his lessons (670's head one)
    # (user, since) Cid swings in Rocketman, and in Twin Jets whoever she faces: Cid's own lessons
    out["cid"] += [mv._lesson_anim(ctx, "ZGSA", "ZGSL", hrc=_bare_cid.HRC.lower()),
                   mv._lesson_anim(ctx, "ZGTA", "ZGTL", hrc=_bare_cid.HRC.lower())]
    return out, lay


# anim offsets in an actor's list (from its first)
SPEED = lambda p, s: 4 * p + s
STOP = lambda p, kind: 12 + 2 * kind + p          # kind 0 pulled back, 1 deepest; p 0 / 1
TRY = lambda p: 16 + p
TURN = lambda k: 18 + k
LESSON = lambda p: 12 + 4 + p                   # Cloud's / Cid's: after their speeds and stops (S, T)


def _blast(ctx, built, back):
    mv, hb, sp, dt = _mods()
    anims, lay = built
    f = ctx.field(BD.SET)
    dt.tiles_back(f)                                              # (user: the benches drew over Twin Jets)
    sec = Script.parse(f.sections[0])
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    loader = ModelLoader(f.section("models"))
    assert ModelLoader.name(loader.models[0]).endswith("main_n_cloud.char")
    cid_entry = next(e for e in loader.models if ModelLoader.name(e).endswith("main_cid.char"))
    loader.models = loader.models[:1]
    CL = names.index("cloud")
    on_floor = lambda x, y: mv._spot_or(mesh, round(x), round(y), 0)
    spot = lambda x, y: mv._spot(mesh, x, y, 0, True)
    off = lambda base, m, d: (base[0] + mv._off(m, d)[0], base[1] + mv._off(m, d)[1])
    # positions: per position {who: (x, y, z, tri), dir}; the girl's DIR in Twin Jets by SIDE
    rs = spot(*ROCKET_SEAT[:2])
    assert abs(rs[2] - BENCH_DROP * mv.UNIT) < 2, ("the bench", rs)
    cd = ROCKET_SEAT[2]
    ro, rface = lay["rocket"]                                     # (Cid raised and turned: his own z and DIR)
    rx, ry, rz = (rs[k] + mv._off(ro, cd)[k] for k in range(3))
    rfl = on_floor(rx, ry)
    places = [dict(cloud=rs, cdir=cd, girl=rs, gdir=cd, cid=(rfl[0], rfl[1], round(rz), rfl[3]),
                   ciddir=dt._dir_to(*mv._off(rface, cd)[:2]))]
    assert (places[0]["ciddir"] - (cd + 128)) % 256 not in range(64, 193), places[0]["ciddir"]
    tc = on_floor(*TWIN_CLOUD[:2])
    cd = TWIN_CLOUD[2]
    tg = on_floor(*off(tc, lay["her"], cd))
    tk = on_floor(2 * tg[0] - tc[0], 2 * tg[1] - tc[1])          # Cid: Cloud's spot mirrored through hers
    places.append(dict(cloud=tc, cdir=cd, girl=tg, gdir=(cd + 128) % 256, gdir2=cd, cid=tk, ciddir=(cd + 128) % 256))
    ec = on_floor(*EXHAUST_CLOUD[:2])
    cd = EXHAUST_CLOUD[2]
    places.append(dict(cloud=ec, cdir=cd, girl=ec, gdir=(cd + 128) % 256, cid=on_floor(*off(ec, lay["exhaust"], cd)),
                       ciddir=(cd + 128) % 256))
    camspot = spot(*CAM_AT)
    ctx.blast_places = places                                     # (offline renders)
    for pl in places:
        pl["cam"] = camspot
        pl["camdir"] = dt._dir_to(pl["girl"][0] - camspot[0], pl["girl"][1] - camspot[1])
        pl["focus"] = pl["girl"]
    # her turn (Twin Jets): which of V0 / V1 passes through facing the camera, from either side
    face_cam = facing_screen(cam, *tg[:3], (0, 1))

    def mid_dir(d, sense):                                       # her facing half way through a turn
        from ff7 import fieldanim as fa
        v = fa._vec(fa.axis_angle([0.0, 1.0, 0.0], 90 * sense), [0.0, 0.0, -1.0])
        o = mv._off(v, d)
        return dt._dir_to(o[0], o[1])
    gap = lambda a, b: min((a - b) % 256, (b - a) % 256)
    turn_for = {}
    for side, d in ((0, places[1]["gdir"]), (1, places[1]["gdir2"])):
        turn_for[side] = min((0, 1), key=lambda k: gap(mid_dir(d, 1 if k == 0 else -1), face_cam))
    # gauge per position (as 672)
    left, top, right, bottom = screen_range(f.section("triggers"))
    near = min(mv._view_depth(cam, v) for t in mesh.tris for v in t) * 0.8
    donor_loader = ModelLoader(ctx.field(mv.mm.DONOR_FIELD).section("models"))
    sprite_scale = round(ModelLoader.entry_scale(donor_loader.models[mv.mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    unit = 3.41 * sprite_scale / 512
    half = mv.GAUGE_PX / 2 * near / cam.zoom / unit
    half_cursor = mv.CURSOR_PX / 2 * near / cam.zoom / unit
    for pl in places:
        sx, sy = cam.project(*pl["focus"][:3])
        sx = min(max(sx, left + 160), right - 160)
        sy = min(max(sy, top + 120), bottom - 120)
        gy = sy + mv.GAUGE_Y
        g = mv._unproject(cam, sx, gy, near)
        pl["gauge"] = (round(g[0]), round(g[1]), round(g[2]), mv._nearest_tri(mesh, g[0], g[1]))
        pl["icon"] = mv._icon_at(cam, mesh, sx, sy, near)
        pl["cursor"] = []
        for b in range(21):
            o_ = ((b * 50 + 25) - 500) / 1000 * mv.GAUGE_PX
            q = mv._unproject(cam, sx + o_, gy - mv.CURSOR_UP, near)
            pl["cursor"].append((round(q[0]), round(q[1]), round(q[2]), mv._nearest_tri(mesh, q[0], q[1])))
    gx, gy_, gz = places[0]["gauge"][:3]

    def tilt(d):
        a = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy_, gz), cam.project(gx + 50 * math.cos(a), gy_ + 50 * math.sin(a), gz)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        return abs(dy) / (abs(dx) + 1e-9) + (0 if dx > 0 else 100)
    sprite_dir = min(range(256), key=tilt)

    # models: 1 bare Cloud, 2 bare Cid, 3 cameraman, 4 gauge, 5 cursor, 6 icon, 7.. the girls
    cl0 = loader.models[0]
    loader.models.append(ModelLoader.with_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), anims["cloud"]))
    cfirst = len(ModelLoader.anims(loader.models[1])) - len(anims["cloud"])
    loader.models.append(ModelLoader.with_scale(
        ModelLoader.with_anims(ModelLoader.with_hrc(cid_entry, _bare_cid.HRC, ModelLoader.name(cid_entry)[:-5] + "_b.char"),
                               anims["cid"]), loader.scale))
    kfirst = len(ModelLoader.anims(loader.models[2])) - len(anims["cid"])
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_FILM)
    loader.models[cm] = ModelLoader.with_anims(loader.models[cm], [mv.CAMERA_STILL])   # (user) still in the intro
    idle_cam = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_STILL)
    mv.SPRITES = SPRITES                                          # (the capsule's own sizes)
    sprites = mv._sprites(ctx, half, half_cursor, mv.ICON_PX / 2 * near / cam.zoom / unit)
    for hrc in SPRITES:
        loader.models.append(ModelLoader.with_scale(sprites[hrc], sprite_scale))
    gm, gfirst, rate = {}, {}, {}
    for key in BD.ORDER:
        (dfield, dmodel), bare_hrc, _, r_ = sp._girl(ctx, key)
        rate[key] = r_ * BD.PAY_X
        donor = ModelLoader(ctx.field(dfield).section("models"))
        if key in ("ruby", "skye"):
            hers = anims["girl"]
        else:
            g_ = next(g for g in MG.GIRLS if g["key"] == key)
            hers = mv._retarget(ctx, anims["girl"], g_["prefix"], g_["donor"][2],
                                ModelLoader.anims(donor.models[dmodel])[0].split(".")[0].lower() + ".a", g_.get("head_down"))
        k = loader.add_from(donor, dmodel)
        loader.models[k] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[k], bare_hrc,
                                                                       ModelLoader.name(loader.models[k])[:-5] + "_b.char"), hers)
        assert len(ModelLoader.anims(loader.models[k])) <= 47, (key, len(ModelLoader.anims(loader.models[k])))
        gm[key], gfirst[key] = k, len(ModelLoader.anims(loader.models[k])) - len(hers)
    assert (cm, len(loader.models)) == (3, 13), (cm, len(loader.models))

    ents = {}
    for name in ["cloudb", "cidb", "camera", "gauge", "cursor", "keys", "voice", "hush", "shout", "hush2", "hush3",
                 "icon", "sqkey"] + ["g_" + k for k in BD.ORDER]:
        ents[name] = len(sec.entity_names)
        sec.entity_names.append(name.encode("latin-1")[:8].ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    girl_ents = [ents["g_" + k] for k in BD.ORDER]
    P, STEP, NEW, RUN, K, HELD, FIN = mv.P, mv.STEP, mv.NEW, mv.RUN, mv.K, mv.HELD, mv.FIN
    POS, VEL, PR, TOT, FR, RATE, T, S, NEXT, BKT, NT, FT = (mv.POS, mv.VEL, mv.PR, mv.TOT, mv.FR, mv.RATE, mv.T,
                                                           mv.S, mv.NEXT, mv.BKT, mv.NT, mv.FT)
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    by_p = lambda make: mv._chain(P, [make(p, pl) for p, pl in enumerate(places)])
    by_g = lambda make: mv._chain(G, [make(key) for key in BD.ORDER])
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    anim = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    once = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xA3, i, 1]))]   # (ANIME1: waits)
    speeds = lambda first, p: mv._chain(STEP, [anim(first + SPEED(p, s_)) for s_ in range(4)])
    scripts = {}
    scripts[CL] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*spot(*ARRIVE)), hb._visi(0), asm.ret(), asm.ret()],
                   2: by_p(lambda p, pl: [xyzi(*pl["focus"])]) + [asm.ret()],
                   3: [xyzi(*on_floor(*INTRO["girl"][:2])), asm.ret()]}

    def man(first, who, wdir, active_side):
        """A man's place + pose: Twin Jets by SIDE (thrusting when she faces him, else standing)."""
        end_ = asm.nop()

        def make(p, pl):
            ops = [xyzi(*pl[who]), d_(pl[wdir]), hb._visi(1)]
            if p != 1:
                return ops + speeds(first, p)
            idle = asm.nop()
            return ops + [asm.if_byte(SIDE, "==", active_side, idle)] + speeds(first, p) + \
                [asm.goto(end_), idle] + anim(0)
        return by_p(make) + [end_, asm.ret()]

    def man_stop(first, kind, active_side):
        def make(p, pl):
            if p == 2:
                return []
            skip = asm.nop()
            guard = [asm.if_byte(SIDE, "==", active_side, skip)] if p == 1 else []
            return guard + anim(first + STOP(p, kind)) + [skip]
        return by_p(make) + [asm.ret()]
    scripts[ents["cloudb"]] = {0: [Op(bytes([0xA1, 1])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                               2: man(cfirst, "cloud", "cdir", 0), 4: man_stop(cfirst, 0, 0), 5: man_stop(cfirst, 1, 0),
                               7: by_p(lambda p, pl: mv.lesson_slot(cfirst + LESSON(p), cfirst + STOP(p, 0)) if p == 1 else [])
                               + [asm.ret()],
                               3: [xyzi(*on_floor(*INTRO["cloud"][:2])), d_(INTRO["cloud"][2]), hb._visi(1)] + anim(0) + [asm.ret()]}
    cid_turn, lesson_end = asm.nop(), asm.nop()
    scripts[ents["cidb"]] = {0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                             2: man(kfirst, "cid", "ciddir", 1), 4: man_stop(kfirst, 0, 1), 5: man_stop(kfirst, 1, 1),
                             6: [asm.ret()],
                             # (user) the lesson's swing (sqkey REQs this): Cid's in Rocketman; in Twin Jets
                             # the man she faces (SIDE 0 Cloud: his slot 7)
                             7: by_p(lambda p, pl: mv.lesson_slot(kfirst + LESSON(0), kfirst + STOP(0, 0)) if p == 0 else
                                     [asm.if_byte(SIDE, "==", 1, cid_turn), hb._req(ents["cloudb"], 7, wait=False),
                                      asm.goto(lesson_end), cid_turn]
                                     + mv.lesson_slot(kfirst + LESSON(1), kfirst + STOP(1, 0)) if p == 1 else [])
                             + [lesson_end, asm.ret()],
                             3: [xyzi(*on_floor(*INTRO["cid"][:2])), d_(INTRO["cid"][2]), hb._visi(1)] + anim(0) + [asm.ret()]}
    # the girls: each acts only if she is G
    for k, key in enumerate(BD.ORDER):
        first, e = gfirst[key], ents["g_" + key]
        def g_(ops, k=k):
            no = asm.nop()
            return [asm.if_byte(G, "==", k, no)] + ops + [asm.ret(), no, asm.ret()]

        def place(p, pl, first=first):
            if p == 1:                                           # (SIDE 0: facing Cloud, 1: Cid)
                to_cid, faced = asm.nop(), asm.nop()
                return [xyzi(*pl["girl"]), asm.if_byte(SIDE, "==", 0, to_cid), d_(pl["gdir"]), asm.goto(faced),
                        to_cid, d_(pl["gdir2"]), faced, hb._visi(1)] + speeds(first, p)
            return [xyzi(*pl["girl"]), d_(pl["gdir"]), hb._visi(1)] + speeds(first, p)
        stops = lambda kind, first=first: mv._chain(P, [anim(first + STOP(0, kind)), anim(first + STOP(1, kind)), []])
        tries = lambda first=first: mv._chain(P, [[mv._animb(), Op(bytes([0xA2, first + STOP(p, 1), 1])),
                                                  Op(bytes([0xAE, first + TRY(p), 1]))] for p in (0, 1)] + [[]])
        # her turn (Twin Jets): SIDE already flipped: from facing the other man, the turn, then him
        turn = mv._chain(SIDE, [once(first + TURN(turn_for[1])) + [d_(places[1]["gdir"])],
                                once(first + TURN(turn_for[0])) + [d_(places[1]["gdir2"])]]) + speeds(first, 1)
        scripts[e] = {0: [Op(bytes([0xA1, gm[key]])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                      2: g_(by_p(place)), 4: g_(stops(0)), 5: g_(stops(1)), 6: g_([hb._w(mv.hold_try_delay())] + tries()),
                      8: g_(turn),
                      3: g_([xyzi(*on_floor(*INTRO["girl"][:2])), d_(INTRO["girl"][2]), hb._visi(1)] + anim(0))}
    scripts[ents["icon"]], scripts[ents["sqkey"]] = mv._hold_entities(hb, 6, sprite_dir, cloud=ents["cidb"], place=
                                                                      by_p(lambda p, pl: [xyzi(*pl["icon"])]))
    scripts[ents["camera"]] = {0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + anim(idle_cam) + [asm.ret(), asm.ret()],
                               2: by_p(lambda p, pl: [xyzi(*pl["cam"]), d_(pl["camdir"])]) + [hb._visi(1)] + anim(film)
                               + [asm.ret()],
                               3: [xyzi(*camspot), d_(dt._dir_to(INTRO["girl"][0] - camspot[0], INTRO["girl"][1] - camspot[1])),
                                   hb._visi(1)] + anim(idle_cam) + [asm.ret()]}
    scripts[ents["gauge"]] = {0: [Op(bytes([0xA1, 4])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret(), asm.ret()],
                              2: by_p(lambda p, pl: [xyzi(*pl["gauge"])]) + [hb._visi(1), asm.ret()]}
    loop, idle = asm.nop(), asm.nop()
    cur = [loop, asm.if_byte(RUN, "==", 1, idle), asm.setword(BKT, POS), hb._arith(0x8C, BKT, 50)]
    cur += by_p(lambda p, pl: mv._tree(BKT, 0, 20, lambda b: [xyzi(*pl["cursor"][b])]) + [hb._visi(1), hb._w(1),
                                                                                            asm.goto_back(loop)])
    cur += [idle, hb._visi(0), hb._w(1), asm.goto_back(loop)]
    scripts[ents["cursor"]] = {0: [Op(bytes([0xA1, 5])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret()] + cur
                               + [asm.ret()]}
    wait = hb._w(1)
    back1, up = asm.goto_back(wait), asm.setbyte(HELD, 0)
    scripts[ents["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x96, FR[0], FR[1]])),
                                 Op(bytes([0x30]) + struct.pack("<H", mv.OK_KEY) + b"\x00", target=up),
                                 asm.if_byte(HELD, "==", 0, back1), asm.setbyte(HELD, 1),
                                 Op(bytes([0x96, PR[0], PR[1]])), back1,
                                 up, asm.goto_back(wait), asm.ret()]}
    # voice: her lines (Cloud's "C:", Cid's "I:") while it plays
    texts = {}

    def text_of(who, raw):
        if raw.startswith("C:"):
            t = "{CLOUD}\n“%s”" % raw[2:]
        elif raw.startswith("I:"):
            t = "Cid\n“%s”" % raw[2:]
        elif raw.startswith("("):
            t = "%s\n%s" % (who, raw)
        elif raw.startswith("“"):
            t = "%s\n%s" % (who, raw)
        else:
            t = "%s\n%s" % (who, raw)                              # (muffled)
        if t not in texts:
            texts[t] = sec.add_string(mv._encode(t))
        return t
    vl, vdone = asm.nop(), asm.nop()
    voice = [asm.ret(), vl, hb._w(mv.SAY_EVERY), asm.if_byte(RUN, "==", 1, vdone),
             Op(bytes([0x95, K[0], K[1]])), Op(bytes([0x8D, K[0] << 4, K[1], 4]))]

    def line(key):
        def per_p(p, pl):
            ls = BD.LINES[key][BD.POSITIONS[p]]
            out = []
            for raw in ls:
                t = text_of(BD.NAMES[key], raw)
                out.append([Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, mv.LINE_Y), hb._req(ents["hush"], 2, wait=False)] +
                           ([hb._req(ents["icon"], 4, wait=False)] if mv._slaps(raw) else []) + [asm.message(1, texts[t])])
            assert len(out) == 4, (key, p)
            return mv._chain(K, out)
        return by_p(per_p)
    voice += by_g(line) + [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.SAY_FOR), Op(b"\x54\x01"), asm.ret()]}
    shout = "Cameraman\n“Five seconds left! Go all out, boys!\n Give me a FINISHER!”"
    scripts[ents["shout"]] = {0: [asm.ret(), asm.ret()],
                              2: [Op(b"\x52\x02\x00\x01"), hb._window(shout, 2, 8, 56),
                                  hb._req(ents["hush2"], 2, wait=False), asm.message(2, sec.add_string(mv._encode(shout))),
                                  asm.ret()]}
    scripts[ents["hush2"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.FINISH_SAY_FOR), Op(b"\x54\x02"), asm.ret()]}
    scripts[ents["hush3"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(GR.PAUSE_FRAMES[1]), Op(b"\x54\x03"), asm.ret()],
                              3: [hb._w(GR.HOLD_SAY), Op(b"\x54\x03"), asm.ret()],
                              4: [hb._w(GR.MUFFLED_SAY), Op(b"\x54\x03"), asm.ret()]}

    # director
    lost, wrap, tick, hi_red, walkout = asm.nop(), asm.nop(), asm.nop(), asm.nop(), asm.nop()
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    actors = [ents["cloudb"]] + girl_ents + [ents["cidb"]]
    place_all = lambda: [hb._req(e, 2, wait=False) for e in [CL] + actors + [ents["camera"], ents["gauge"], ents["icon"]]] \
        + [hb._w(6)]
    lines = lambda block: by_g(block)
    leave = lambda key_: mv.lose_affection(key_) + hb._say(sec, GR.NAMES[key_] + "\n" + PF.PROFILES[key_]["leave"]) + [asm.goto(walkout)]
    head_pos = lambda no: [asm.if_byte(P, "!=", 2, no)]       # (rocketman, twinjets: her mouth)
    # (one hold line a voice and one desperate line a girl: six girls' texts share this field)
    voices = [("{CLOUD}", GR.HOLD_CLOUD[:1], GR.HOLD_STERN), ("Cid", BD.CID_HOLD[:1], BD.CID_STERN)]
    pause = mv._pause_ops(hb, sec, actors, ents["hush3"], lines, head_pos, ents["icon"], lambda key_: rate[key_],
                          leave=leave, speaker=(SPK, voices), desperate=1)
    there = by_g(lambda key_: mv._there_ops(hb, sec, key_, rate[key_], lambda no: [asm.if_byte(P, "==", 2, no)],
                                            ents["icon"], ents["hush3"], leave))
    gone = asm.nop()
    main = [asm.if_byte(BLAST_ON[0], "bit_on", BLAST_ON[1], gone), asm.bitoff(*BLAST_ON)]
    main += [Op(b"\xE0\x00\x01\x00"), Op(b"\xE1\x00\x02\x00")]          # space through the window (as 660)
    main += [asm.setbyte(G, 0)]
    for k, key in enumerate(BD.ORDER[1:], 1):
        bit = 1 if key == "skye" else next(g["bit"] for g in MG.GIRLS if g["key"] == key)
        nx = asm.nop()
        main += [asm.if_byte(MOVIE_GIRL, "bit_on", bit, nx), asm.setbyte(G, k), nx]
    main += [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS, 500), asm.setword(VEL, 1000),
             asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(P, 0),
             asm.setbyte(STEP, 0), asm.setbyte(K, 0), asm.setword(NEXT, BD.MINUTE), asm.setbyte(FIN, 0),
             asm.setbyte(mv.RULES, 1), asm.setbyte(mv.CTRL, 0), asm.setbyte(mv._ann(0), 0), asm.setbyte(mv.THR, 0),
             asm.setbyte(mv.TSC, 0), asm.setbyte(mv.TC, 2), asm.setbyte(SIDE, 0), asm.setbyte(SEG, 0), asm.setbyte(SPK, 1)]
    main += [hb._req(e, 3) for e in [CL, ents["cloudb"], ents["cidb"], ents["camera"]] + girl_ents] + [hb._w(20)]
    main += [Op(hb.FADE_IN), Op(b"\x6C")]
    for t_ in BD.OPENING:
        main += say(t_)
    main += hb._say(sec, BD.CID_INTRO)
    main += by_g(lambda key_: hb._say(sec, BD.NAMES[key_] + "\n" + BD.INTRO[key_][0]))
    if "elena" in sp.RULES_ASK:                                     # (user) Elena: the ground rules first (RULES)
        q, choices = sp.RULES_ASK["elena"]
        ops, first = hb._ask(sec, "Elena\n" + q, [c[0] for c in choices])
        rdone, not_e = asm.nop(), asm.nop()
        ops = [asm.if_byte(G, "==", BD.ORDER.index("elena"), not_e)] + ops
        for j, (label, value, reply) in enumerate(choices):
            nx = asm.nop()
            ops += [asm.if_byte(mv.CHOICE, "==", first + j, nx), asm.setbyte(mv.RULES, value)] + \
                hb._say(sec, "Elena\n" + reply) + [asm.goto(rdone), nx]
        main += ops + [rdone, not_e]
    main += [Op(hb.FADE_OUT), Op(b"\x6C")] + place_all() + [hb._w(4), Op(hb.FADE_IN), Op(b"\x6C")]
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, BD.THEME]) + bytes(8)), hb._w(15)]
    main += say("“Three positions, a minute each. Tap OK,\n mind the meter. Rocketman first!\n ...And... BLAST OFF!”")
    main += [asm.setword(FR, 0), asm.setword(PR, 0), asm.setword(NT, mv.TICK)] + mv._pause_arm(hb, BD.MINUTE) + \
        [asm.setbyte(RUN, 1)]
    wait1, go = hb._w(1), asm.nop()
    A, B, C, VMAX, DANGER = mv.A, mv.B, mv.C, mv.VMAX, mv.DANGER
    main += [tick, wait1, asm.if_word(FR, "<", NT, go), asm.goto_back(wait1), go, hb._arith(0x86, NT, mv.TICK),
             asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
             hb._arith(0x8A, VEL, 5), hb._arith(0x8C, VEL, 6),
             hb._arith(0x86, VEL, 1000 - 1000 * 5 // 6 - B - 500 // C),
             asm.setword(S, T), hb._arith(0x8A, S, A), hb._arith(0x86, VEL, S),
             asm.setword(S, POS), hb._arith(0x8C, S, C), hb._arith(0x86, VEL, S)]
    lo, hi = asm.nop(), asm.nop()
    main += [asm.if_word(VEL, "<", 1000 - VMAX, lo), asm.setword(VEL, 1000 - VMAX), lo,
             asm.if_word(VEL, ">", 1000 + VMAX, hi), asm.setword(VEL, 1000 + VMAX), hi,
             asm.setword(S, POS), hb._arith(0x86, S, VEL),
             asm.if_word(S, ">=", 1000 + DANGER, lost),
             asm.setword(POS, S), hb._arith(0x88, POS, 1000),
             asm.if_word(POS, "<=", 1000 - DANGER, hi_red)]
    no_call = asm.nop()
    main += [asm.if_byte(P, "==", 2, no_call), asm.if_byte(FIN, "==", 0, no_call),
             asm.setword(FT, FR), hb._arith(0x86, FT, mv.FINISH_FRAMES), asm.if_word(FT, ">=", NEXT, no_call),
             asm.setbyte(FIN, 1), hb._req(ents["shout"], 2, wait=False), no_call]
    done, same = asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(S, T), hb._arith(0x8A, S, 16),
             hb._arith(0x86, RATE, S), asm.setbyte(NEW, 0)]
    for s_, th in enumerate(mv.RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s_ + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW)] + \
        [hb._req(e, 2, wait=False) for e in actors] + [same]
    # (user) Twin Jets: every SWITCH frames she turns to the other man; each man's one hold prompt in his
    # first half (TWIN_ICON_IN in), none after
    no_sw, icon_off, icon_set = asm.nop(), asm.nop(), asm.nop()
    main += [asm.if_byte(P, "==", 1, no_sw), asm.if_word(FR, ">=", SW, no_sw), asm.if_byte(RUN, "==", 1, no_sw),
             hb._arith(0x86, SW, BD.SWITCH), Op(bytes([0x95, SEG[0], SEG[1]])),
             Op(bytes([0x85, SIDE[0] << 4, SIDE[1], 1])), Op(bytes([0x8D, SIDE[0] << 4, SIDE[1], 2])),
             asm.setbyte(SPK, 0), asm.if_byte(SIDE, "==", 1, icon_set), asm.setbyte(SPK, 1), icon_set,
             hb._req(ents["cloudb"], 2, wait=False), hb._req(ents["cidb"], 2, wait=False)] + \
        [hb._req(e, 8, wait=False) for e in girl_ents] + \
        [asm.setword(mv.IT, NO_ICON), asm.if_byte(SEG, ">=", 2, icon_off), asm.setword(mv.IT, FR),
         hb._arith(0x86, mv.IT, TWIN_ICON_IN), icon_off, no_sw]
    main += pause + there
    stay = asm.nop()
    to_twin, to_exh, armed = asm.nop(), asm.nop(), asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay),
             asm.if_byte(P, "<", 2, wrap),
             asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(mv.FAST_OUT), Op(b"\x6C"),
             Op(bytes([0x85, P[0] << 4, P[1], 1])), asm.setbyte(STEP, 0), asm.setbyte(SIDE, 0), asm.setbyte(SEG, 0),
             asm.setword(POS, 500), asm.setword(VEL, 1000), asm.setword(RATE, 40)] + place_all() + \
            [hb._w(4), Op(mv.FAST_IN), Op(b"\x6C"), asm.setword(PR, 0), asm.setword(NT, FR),
             hb._arith(0x86, NT, mv.TICK), asm.setword(NEXT, FR), hb._arith(0x86, NEXT, BD.MINUTE)] + \
            mv._pause_arm(hb, BD.MINUTE) + \
            [asm.if_byte(P, "==", 1, to_exh), asm.setbyte(SPK, 0), asm.setword(SW, FR), hb._arith(0x86, SW, BD.SWITCH),
             asm.setword(mv.IT, FR), hb._arith(0x86, mv.IT, TWIN_ICON_IN), asm.goto(armed),
             to_exh] + mv._there_arm(hb) + [armed, asm.setbyte(RUN, 1), stay, asm.goto_back(tick)]
    rx, ry, rz, rt, rdir = back

    def out():
        stop = hb._w(30)
        return [asm.setword(MOVIE_PRESSES, TOT), hb._arith(0x8A, MOVIE_PRESSES, BD.PAY_X),     # (x2: two men)
                asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
                Op(hb.FADE_OUT), Op(b"\x6C"), hb._uc(0), hb._menu(0),
                asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir), stop, asm.goto_back(stop), asm.ret()]
    main += [hi_red, sound(mv.RED_SOUND), asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"),
             Op(b"\x54\x02"), Op(bytes([0xF2, 0, 0, 0, 0x10, mv.FANFARE]) + bytes(8)), hb._w(45)]
    main += say("“WOW! What a FINISHER!\n We have LIFT-OFF!”")

    def bonus(key_):
        gil = rate[key_] * mv.FINISH_BONUS
        return [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)] + \
            say("“Here's a bonus, on the spot:\n {:,} gil. Out of this world!”".format(gil))
    main += by_g(bonus) + by_g(lambda key_: hb._say(sec, BD.AFTERMATH[key_])) + hb._say(sec, BD.CID_AFTER) + out()
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! Houston, we have a problem.\n ...Fine. We'll sell what we've got.”") + out()
    main += [walkout, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)] + say(mv.WALKED) + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! Splashdown!”")
    main += by_g(lambda key_: hb._say(sec, BD.AFTERMATH[key_])) + hb._say(sec, BD.CID_AFTER) + out()
    # (not from the cameraman: back to Cid by the rocket)
    dt_ = importlib.import_module("660_dates")
    bx, by_, bt, bd = dt_._return_spot(ctx, dict(name=CID.NAME, field=CID.FIELD, at=CID.AT))
    main += [gone, hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(CID.FIELD), bx, by_, bt, bd), asm.ret()]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main}
    assert names[0] != "cloud", names[0]
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n <= 250, ("texts", n)
    return n


def apply(ctx):
    built = _poses(ctx)
    n = _blast(ctx, built, ctx.movie_back)
    print("  673: the Blast-off set %s (%d texts)" % (BD.SET, n))
    for p, pl in zip(BD.POSITIONS, ctx.blast_places):
        print("    %s: cloud %s %d, girl %s %d%s, cid %s %d" % (p, pl["cloud"][:3], pl["cdir"], pl["girl"][:3], pl["gdir"],
                                                          " / %d" % pl["gdir2"] if "gdir2" in pl else "", pl["cid"][:3], pl["ciddir"]))

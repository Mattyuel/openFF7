"""(user) Tickets, please!: the third parody film (data `_tickets.py`, poses `_tickets_poses.py`), on the
Sector 7 train, starring Cloud (the ticket inspector), Tifa and Jessie.

The set: FIELD (a debug room only startmap leads to) replaced by a copy of tin_2 (the carriage; user: its seats
are the most visible), script blanked but the train's background animations rebuilt (the strip lights, the
power flicker, the swinging straps: tin_2's ELEC / LIGHT / TURI1 / TURI2 cycles on their own temp vars; the
doors shut). Models: Cloud (the hidden player), clothed Cloud / Tifa (AAGB) / Jessie (AXDC) for the intro,
bare Cloud / Tifa (ZTFA) / Jessie (`BARE_JESSIE`, the standard body on her model, tag J) for the rest. No
Director model (the carriage is tight): his lines are text.

The intro (`_tickets.INTRO_LINES`): Tifa and Jessie sit side by side on the near left bench; Cloud walks down
the aisle to them; the ticket banter; fade: Cloud in his alt model, standing before them; the teasing; fade:
the position (the user's sketch): both across the bench, Tifa on all fours further back with her rear over the
aisle edge, Jessie on her back nearer the camera with her head over the edge and her legs up the window, Cloud
standing in the aisle (solved against each of them: `_tickets_poses`).

The gameplay is Going up's (684, its code copied: prompts by tier, HOLD prompts, the [MENU] switch call by the
girls, chatter / miss lines, the squat sound on a hit, Cloud's pose styles every STYLE_EVERY reps), P 0 =
behind Tifa, P 1 = Jessie's head; with Jessie a HOLD lasts until she taps out (late = mad, MAD_LIMIT = she
walks off down the carriage; no affection: she has none). After TOTAL_REPS the train pulls in: the finale,
the pay, back to the Director. Checked on offline renders only."""
import importlib
import math
import struct

import _female_body as fb
import _tickets as TK
import _tickets_poses as TP
from ff7 import asm
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

BARE_JESSIE = "XJEA.HRC"            # her undressed model (the standard body, her head and feet; tag J)
TIFA_DONOR, JESSIE_DONOR = ("tin_2", 2), ("tin_2", 5)      # AAGB (ABCD stand, ABCE walk), AXDC (ACFE, AAFF)
BARE_TIFA = "ZTFA.HRC"
DC = 0xC0                           # Cloud faces -x (the window); Tifa too (her rear to the aisle)
WALK_STEP = 5.2                     # (user: Cloud twice as fast; was 2.6), the walk anim at double speed

TIER, STREAK, KEY, PR, P, SEEN, RND, KP, HOLD, HELD, SINCE, NEXTSW, MOVING = ((5, a) for a in range(100, 113))
CNT, PAY, REPS, PER, GIL, CX, CY = ((6, a) for a in range(114, 128, 2))
PRV = [(5, 130 + k) for k in range(4)]
WN = (5, 134)                        # a walk's frame count
TALKING, LN, CHAT, STYLE, SC, ANGER, HC, CUE, CL = ((5, a) for a in range(135, 144))


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _jessie(ctx):
    """Her undressed model (as 679_nurse builds the nurse's)."""
    e = ModelLoader(ctx.field(JESSIE_DONOR[0]).section("models")).models[JESSIE_DONOR[1]]
    text = ctx.char_file(ModelLoader.hrc(e).lower()).decode("latin-1")
    skin = fb.face_skin(ctx, text)
    ctx.char_file(BARE_JESSIE.lower(), fb.apply(ctx, text, "J", skin).encode("latin-1"))
    tips = fb._bust_tips(ctx)
    ctx.char_file(BARE_JESSIE.lower(), fb.nipples(ctx, ctx.char_file(BARE_JESSIE.lower()).decode("latin-1"), "J", tips)
                  .encode("latin-1"))
    fb.tifa_body(ctx, ctx.char_file(BARE_JESSIE.lower()).decode("latin-1"), skin, 1.0)
    return ModelLoader.anims(e)[0].split(".")[0].lower() + ".a"


def _dir_to_x(mv, v):
    """The DIR turning model vector v (y down) to field +x."""
    def score(d):
        o = mv._off(v, d)
        return o[0] / max(1e-6, math.hypot(o[0], o[1]))
    return max(range(256), key=score)


def poses(ctx):
    """Every pose and spot. Returns a dict."""
    mv, hb, dt = _mods()
    j_stand = _jessie(ctx)
    t_stand = "abcd.a"
    out = {"jessie": TP.jessie_under(ctx, BARE_JESSIE, j_stand)}           # QJF0-3, 8, 7, 9
    out["tifa_still"] = TP.still(ctx, "ZVC0", "QNT9")
    out["sit_t"] = TP.sitting(ctx, "QNTS", "aagb.hrc", t_stand)
    out["sit_j"] = TP.sitting(ctx, "QNJS", "axdc.hrc", j_stand)
    U = mv.UNIT
    n = (1.0, 0.0, 0.0)                                                   # from them to him: the aisle
    mean = lambda ps, k: sum(p[k] for p in ps) / len(ps)
    # Tifa: her entry over the aisle edge
    ent = [TP.entry_points(ctx, BARE_TIFA, t_stand, "ZVC%d" % s) for s in range(4)]
    o = [mv._off(p, DC) for p in ent[0]]
    st = (round(TK.TIFA_ENTRY_X - mean(o, 0)), round(TK.TIFA_Y - mean(o, 1)), TK.SEAT)
    # Jessie: her head towards the aisle, her neck at JESSIE_NECK_X
    # (user) Jessie directly under Tifa: her head between Tifa's thighs at the aisle edge, Tifa's head between
    # her knees
    J0 = TP.joints(ctx, BARE_JESSIE, "QJF0")[0]
    dj = _dir_to_x(mv, [J0["head@"][k] - J0["hip@"][k] for k in range(3)])
    necks = [mv._off(J["head@"], dj) for J in TP.joints(ctx, BARE_JESSIE, "QJF0")]
    sj = (round(TK.JESSIE_NECK_X - mean(necks, 0)), round(TK.TIFA_Y - mean(necks, 1)), TK.SEAT)
    mo = [TP.mouths(ctx, BARE_JESSIE, j_stand, "QJF%d" % s) for s in range(4)]
    tip0, root0 = TP.his_tip(ctx)
    tip0l, _ = TP.his_tip(ctx, level=True)
    deep = 7 / 15
    tips_t = [TP.targets([TP._field(st, DC, p) for p in ent[s]], n, deep) for s in range(4)]
    # (user: his member level for Tifa) its tip is then lower than her rear: she sinks into the cushion by what's
    # missing (rather than Cloud floating on his toes)
    tip_up = TK.FLOOR - tip0l[1] * U                                  # (y down) his level tip's height, standing
    sink = max(0, round(max(t[2] for ts in tips_t for t in ts) - tip_up - TK.SINK_SPARE * U))
    st = (st[0], st[1], st[2] - sink)
    tips_t = [TP.targets([TP._field(st, DC, p) for p in ent[s]], n, deep) for s in range(4)]
    out["sink"] = sink
    tips_j = [TP.targets([TP._field(sj, dj, p) for p in mo[s]], n, deep) for s in range(4)]
    ct = tuple(round(c) for c in TP.spot(tips_t[0], DC, TK.FLOOR, tip0l, root0))
    cj = tuple(round(c) for c in TP.spot(tips_j[0], DC, TK.FLOOR, tip0, root0))
    # hands: on Tifa's hips / Jessie's shoulders (field points per frame)
    def hips(s):
        Js = TP.joints(ctx, BARE_TIFA, "ZVC%d" % s)
        return [tuple(TP._field(st, DC, [J[b + "_femur@"][0] + sg * 0.35, J[b + "_femur@"][1] - 0.9, J[b + "_femur@"][2]])
                      for b, sg in (("l", 1), ("r", -1))) for J in Js]
    def tifa_hips(n):                                                     # (at Jessie: his hands on Tifa's still hips)
        J = TP.joints(ctx, BARE_TIFA, "QNT9")[0]
        h = tuple(TP._field(st, DC, [J[b + "_femur@"][0] + sg * 0.35, J[b + "_femur@"][1] - 0.9, J[b + "_femur@"][2]])
                  for b, sg in (("l", 1), ("r", -1)))
        return [h] * n
    seat_edge = (ct[0] - TK.EDGE_X) / U                                   # his forward distance to the seat's edge
    foot = (TK.FOOT_UP[0], seat_edge + TK.FOOT_UP[1])
    names = {}
    for key, tips, hands, stance, lean, kw, cs in (
            ("A", tips_t, hips, TK.STANCE_T, TK.LEAN_T, dict(level=True), ct),
            ("B", tips_t, hips, TK.STANCE_T, TK.LEAN_T, dict(foot=foot, level=True), ct),
            ("C", tips_j, lambda s: tifa_hips(len(tips_j[s])), TK.STANCE_J, TK.LEAN_J, {}, cj),
            ("D", tips_j, None, TK.STANCE_J, TK.LEAN_J * 0.4, dict(nape=True), cj)):
        names[key] = []
        for s in range(4):
            drops = TP.cloud(ctx, "QZ%s%d" % (key, s), tips[s], hands(s) if hands else None, cs, DC, TK.FLOOR,
                             stance, lean, **kw)
            names[key].append("QZ%s%d.tor" % (key, s))
            out.setdefault("drops", []).append((key, s, round(min(drops), 2), round(max(drops), 2)))
    hold_tips = TP.targets([TP._field(sj, dj, p) for p in TP.mouths(ctx, BARE_JESSIE, j_stand, "QJF8")], n, 0.0)
    TP.cloud(ctx, "QZC8", hold_tips, tifa_hips(1), cj, DC, TK.FLOOR, TK.STANCE_J, TK.LEAN_J)
    out.update(cloud=names, hold="QZC8.tor", st=st, sj=sj, dj=dj, ct=ct, cj=cj, j_stand=j_stand)
    return out


def apply(ctx):
    mv, hb, dt = _mods()
    PZ = poses(ctx)
    st, sj, dj, ck, ch = PZ["st"], PZ["sj"], PZ["dj"], PZ["ct"], PZ["cj"]
    # the set
    ctx.field(TK.FIELD)
    ctx.field(TK.BASE)
    f = ctx._fields[TK.FIELD] = FieldFile(ctx._orig_raw[TK.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    from ff7.walkmesh import Walkmesh
    mesh = Walkmesh(f.section("walkmesh"))

    def tri(x, y):
        t = mesh.find(round(x), round(y))
        assert t is not None, ("off the walkmesh", x, y)
        return t
    Z = TK.FLOOR
    # models: 0 hidden player, 1-3 clothed Cloud / Tifa / Jessie, 4-6 bare Cloud / Tifa / Jessie
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    tifa_e, jess_e = loader.models[TIFA_DONOR[1]], loader.models[JESSIE_DONOR[1]]
    assert (ModelLoader.hrc(tifa_e), ModelLoader.hrc(jess_e)) == ("AAGB.HRC", "AXDC.HRC")
    c_anims, t_anims, j_anims = ModelLoader.anims(cl0), ModelLoader.anims(tifa_e), ModelLoader.anims(jess_e)
    bare_c = sum((PZ["cloud"][k] for k in "ABCD"), []) + [PZ["hold"]]
    bare_t = ["ZVC%d.tor" % s for s in range(4)] + [PZ["tifa_still"]]
    bare_j = PZ["jessie"]                                                   # QJF0-3, 8, 7, 9
    for nm in bare_c + bare_t + bare_j + [PZ["sit_t"], PZ["sit_j"]]:
        ctx.char_file(nm.split(".")[0].lower() + ".a")                      # (exists)
    loader.models = [cl0, ModelLoader.only_anims(cl0, c_anims[:2]),
                     ModelLoader.only_anims(tifa_e, t_anims[:2] + [PZ["sit_t"]]),
                     ModelLoader.only_anims(jess_e, j_anims[:2] + [PZ["sit_j"]]),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "tickets_cloudb.char"),
                                            c_anims[:1] + bare_c),
                     ModelLoader.only_anims(ModelLoader.with_hrc(tifa_e, BARE_TIFA, "tickets_tifab.char"),
                                            t_anims[:1] + bare_t),
                     ModelLoader.only_anims(ModelLoader.with_hrc(jess_e, BARE_JESSIE, "tickets_jessb.char"),
                                            j_anims[:1] + bare_j)]
    assert all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    # entities
    names = ["produce", "cloud", "cloudA", "tifaA", "jessA", "cloudB", "tifaB", "jessB", "elec", "light",
             "turi1", "turi2", "doors", "k_sw", "k_ca", "k_ok", "k_mn", "prompt", "talk", "hush"]
    sec.entity_names = [nm.encode("latin-1").ljust(8, b"\0") for nm in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {nm: i for i, nm in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch_ = mv._chain
    face = lambda x, y, tx, ty: dt._dir_to(tx - x, ty - y)
    at = lambda p, d, z=Z: [xyzi(p[0], p[1], z, tri(p[0], p[1])), d_(d)]

    def walk(start, stop, walk_anim, stand_anim, d_end):
        """XYZI stepped WALK_STEP a frame from start to stop with the walk anim, then stand facing d_end."""
        (sx, sy), (tx, ty) = start, stop
        n = max(1, round(math.dist(start, stop) / WALK_STEP))
        stx, sty = round((tx - sx) / n), round((ty - sy) / n)
        top, done = hb._w(1), asm.nop()
        return [d_(face(sx, sy, tx, ty)), asm.setword(CX, sx & 0xFFFF), asm.setword(CY, sy & 0xFFFF),
                asm.setbyte(WN, 0)] + [mv._animb(), Op(bytes([0xA2, walk_anim, 2])), Op(bytes([0xAE, walk_anim, 2]))] + \
            [top, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
             Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], Z, tri(*start))),
             Op(bytes([0x95, WN[0], WN[1]])), asm.if_byte(WN, "<", n, done), asm.goto_back(top), done] + \
            at(stop, d_end) + loop_(stand_anim)
    scripts = {}
    fx, fy = TK.FOCUS
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at((fx, fy), 0) + [hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()]}
    # the train: the strip lights (layer 1, 3 states), the power flicker (layer 2), the straps (layers 4 / 5),
    # the doors shut (layers 3 / 6, state 1); as tin_2's own entities while the train runs
    def cycle(layer, states, wait, first=None):
        top = hb._w(wait)
        ops = [Op(bytes([0xE0, 0, layer, first or states[0]])), asm.ret(), top]
        prev = first or states[0]
        for s in states + [first or states[0]]:
            if s != prev:
                ops += [Op(bytes([0xE1, 0, layer, prev])), Op(bytes([0xE0, 0, layer, s])), hb._w(wait)]
                prev = s
        return ops + [asm.goto_back(top), asm.ret()]
    scripts[E["elec"]] = {0: cycle(1, [1, 2, 3], 2)}
    scripts[E["light"]] = {0: cycle(2, [1, 2, 3, 4], 2) }
    scripts[E["turi1"]] = {0: cycle(4, [1, 2, 1, 3], 7)}
    scripts[E["turi2"]] = {0: cycle(5, [1, 2, 1, 3], 9)}
    scripts[E["doors"]] = {0: [Op(b"\xE0\x00\x03\x01"), Op(b"\xE0\x00\x06\x01"), asm.ret(), asm.ret()]}
    # the intro actors: clothed, sitting / walking; 4 hidden
    sitx = TK.SIT_X
    scripts[E["cloudA"]] = {
        0: [Op(bytes([0xA1, 1]))] + at(TK.CLOUD_FROM, face(*TK.CLOUD_FROM, *TK.CLOUD_TO)) + [hb._visi(1)] + hide() +
        loop_(0) + [asm.ret(), asm.ret()],
        8: walk(TK.CLOUD_FROM, TK.CLOUD_TO, 1, 0, DC) + [asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    for ent, model, y in (("tifaA", 2, TK.TIFA_Y), ("jessA", 3, TK.JESSIE_Y)):
        scripts[E[ent]] = {
            0: [Op(bytes([0xA1, model]))] + at((sitx, y), 0x40, TK.SEAT) + [hb._visi(1)] + hide() + loop_(2) +
            [asm.ret(), asm.ret()],
            4: [hb._visi(0), asm.ret()]}
    # the scene actors: 0 init hidden; 2 = placed by P, the tier's stroke (by STYLE for Cloud); 3 Cloud
    # standing bare before them (intro); 4 hidden; 5 the head hold; Jessie 6 her tap-out
    stroke = lambda base: ch_(TIER, [loop_(1 + base + s) for s in range(4)])
    qz = lambda k: 4 * "ABCD".index(k)
    scripts[E["cloudB"]] = {
        0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(P, [at(ck, DC) + ch_(STYLE, [stroke(qz("A")), stroke(qz("B"))]),
                   at(ch, DC) + ch_(STYLE, [stroke(qz("C")), stroke(qz("D"))])]) + [hb._visi(1), asm.ret()],
        3: at(TK.CLOUD_TO, DC) + loop_(0) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(1 + bare_c.index(PZ["hold"])) + [asm.ret()]}
    ti = lambda nm: 1 + bare_t.index(nm)
    scripts[E["tifaB"]] = {
        0: [Op(bytes([0xA1, 5])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: at(st, DC, st[2]) + ch_(P, [ch_(TIER, [loop_(ti("ZVC%d.tor" % s)) for s in range(4)]),
                                         loop_(ti(PZ["tifa_still"]))]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    ji = lambda k: 1 + k                                                   # QJE0-3 0-3, 8 at 4, 7 at 5, 9 at 6
    scripts[E["jessB"]] = {
        0: [Op(bytes([0xA1, 6])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: at(sj, dj, TK.SEAT) + ch_(P, [loop_(ji(6)), ch_(TIER, [loop_(ji(s)) for s in range(4)])]) +
        [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ji(4)) + [asm.ret()],                                     # held deep
        6: loop_(ji(5)) + [asm.ret()]}                                     # tapping out: her squirm
    # the buttons: one small entity each; a press = up -> down (PR = its number), HELD bit k while held
    for k, (mask, _) in enumerate(TK.KEYS + [TK.SWITCH_KEY]):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok", "k_mn"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    # the prompts: window 1 (the director closes it); slots 2-4 the buttons, 5-7 HOLD + the button, 8 [MENU]
    pr = {0: [asm.ret(), asm.ret()]}
    labels = [l for _, l in TK.KEYS] + [TK.HOLD_LABEL + l for _, l in TK.KEYS] + [TK.SWITCH_KEY[1]]
    for j, label in enumerate(labels):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, TK.PROMPT_Y, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    pslot = 2 + len(labels)
    hold_pools = {}
    for key, pool in (("hold", TK.HOLDS), ("cue", TK.CUES), ("good", TK.GOOD), ("early", TK.EARLY), ("mad", TK.MAD)):
        hold_pools[key] = (pslot, len(pool))
        pr[pslot] = [Op(b"\x52\x01\x00\x01")] + ch_(CL, [[hb._window(x, 1, 8, TK.PROMPT_Y), asm.message(1, mv._text_id(sec, x))]
                                                         for x in pool]) + [asm.ret()]
        pslot += 1
    assert pslot <= 32, pslot
    scripts[E["prompt"]] = pr
    # the talk: window 2, groups of lines each shut by hush after SAY
    groups, gid = [], {}
    for part in (0, 1):
        for t, lines in sorted(TK.LINES[part].items()):
            gid[(part, t)] = len(groups)
            groups.append(lines)
    for k, line in enumerate(TK.SWITCH_CALL):
        gid[("switch", k)] = len(groups)
        groups.append([line])
    def show(text):
        return [Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, TK.LINE_Y), hb._req(E["hush"], 2, wait=False),
                asm.message(2, mv._text_id(sec, text))]
    talk = {0: [asm.ret(), asm.ret()]}
    busy_ = lambda ops: [asm.setbyte(TALKING, 1)] + ops + [asm.setbyte(TALKING, 0), asm.ret()]
    for j, lines in enumerate(groups):
        talk[2 + j] = busy_(sum((show(t) for t in lines), []))
    slot = 2 + len(groups)
    style_slot = slot                                                   # (by P, then STYLE)
    talk[slot] = busy_(ch_(P, [ch_(STYLE, [sum((show(t) for t in ls), []) for ls in TK.STYLE_LINES[p]])
                               for p in (0, 1)]))
    slot += 1
    pools = {}
    for key, pool in (("chat0", TK.CHAT[0]), ("chat1", TK.CHAT[1]), ("miss0", TK.MISSES[0]), ("miss1", TK.MISSES[1])):
        pools[key] = (slot, len(pool))
        talk[slot] = busy_(ch_(LN, [show(t) for t in pool]))
        slot += 1
    assert slot <= 32, slot
    scripts[E["talk"]] = talk
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(TK.SAY), Op(b"\x54\x02"), asm.ret()]}
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))        # REQ: never waits

    def line_from(key):
        """A random line of a talk pool, unless someone's already talking."""
        sl, size = pools[key]
        busy = asm.nop()
        return [asm.if_byte(TALKING, "==", 0, busy), Op(bytes([0x99, LN[0], LN[1]])),
                Op(bytes([0x8D, LN[0] << 4, LN[1], size])), asm.setbyte(TALKING, 1), req(E["talk"], sl), busy]

    def by_p(fn):
        return ch_(P, [fn(0), fn(1)])

    def prompt_line(key, pick=None):
        """A line of a hold pool in the prompt window (random, or line `pick` var - 1)."""
        sl, size = hold_pools[key]
        if pick is None:
            ops = [Op(bytes([0x99, CL[0], CL[1]])), Op(bytes([0x8D, CL[0] << 4, CL[1], size]))]
        else:
            ops = [asm.setbyte(CL, pick), Op(bytes([0x87, CL[0] << 4, CL[1], 1]))]     # MINUS
        return [hb._w(2)] + ops + [req(E["prompt"], sl)]                 # (its last line just closed)

    def frames(var, limit):
        """Wait while var < limit, a frame each (IFs only jump forward: the loop is JMPB)."""
        top, done = asm.nop(), asm.nop()
        return [top, asm.if_byte(var, "<", limit, done), hb._w(1), Op(bytes([0x95, var[0], var[1]])),
                asm.goto_back(top), done]

    # the director
    say = lambda t: hb._say(sec, t)
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    fast_out, fast_in = [Op(mv.FAST_OUT), Op(b"\x6C")], [Op(mv.FAST_IN), Op(b"\x6C")]
    main = [hb._uc(1), hb._menu(1), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, TK.MUSIC]) + bytes(8)), hb._req(E["cloudA"], 8)]
    for line, action in TK.INTRO_LINES:
        main += say(line)
        if action == "bare":                                               # Cloud in his alt model
            main += fade_out + [hb._req(E["cloudA"], 4), hb._req(E["cloudB"], 3), hb._w(10)] + fade_in
        elif action == "scene":                                            # the position
            main += fade_out + [hb._req(E[a], 4) for a in ("tifaA", "jessA")] + \
                [asm.setbyte(P, 0), asm.setbyte(TIER, 0), asm.setbyte(STYLE, 0)] + \
                [hb._req(E[a], 2) for a in ("cloudB", "tifaB", "jessB")] + [hb._w(20)] + fade_in
    main += say(TK.HOW)
    main += [asm.setbyte(STREAK, 0), asm.setbyte(SEEN, 0x11), asm.setword(PAY, 0), asm.setword(REPS, 0),
             asm.setbyte(SINCE, 0), asm.setbyte(NEXTSW, TK.SWITCH_MIN), asm.setbyte(HELD, 0),
             asm.setbyte(TALKING, 0), asm.setbyte(CHAT, 0), asm.setbyte(SC, 0), asm.setbyte(ANGER, 0)]
    n = len(TK.PERIODS)
    rep, wait, judge, hit, miss, rest, tail, holdw, done_h, sw_rep, normal, after = (asm.nop() for _ in range(12))
    main += [rep] + [req(E[a], 2) for a in ("cloudB", "tifaB", "jessB")]
    main += ch_(TIER, [[asm.setword(PER, p)] for p in TK.PERIODS])
    main += [asm.setbyte(PR, 0), asm.setword(CNT, 0), asm.setbyte(HOLD, 0),
             asm.if_byte(SINCE, ">=", NEXTSW, normal), asm.goto(sw_rep), normal]
    # a button rep: KEY at random; from tier 1, now and then a HOLD one
    nohold = asm.nop()
    main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])),
             asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])),
             asm.if_byte(TIER, ">=", 1, nohold), Op(bytes([0x99, RND[0], RND[1]])),
             asm.if_byte(RND, "<", TK.HOLD_ODDS, nohold), asm.setbyte(HOLD, 1), nohold]
    main += ch_(HOLD, [ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)]),
                       ch_(KEY, [[hb._req(E["prompt"], 5 + k, wait=False)] for k in range(3)])])
    main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.if_byte(PR, "==", 0, judge), asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait)]
    head_hold, nohead = asm.nop(), asm.nop()
    main += [judge, asm.if_byte(PR, "==", KP, miss),
             asm.if_byte(HOLD, "==", 1, nohead), asm.if_byte(P, "==", 1, nohead), asm.goto(head_hold), nohead]
    # a HOLD: the button kept down to the rep's end (the window stays up meanwhile)
    main += [asm.if_byte(HOLD, "==", 1, done_h), holdw, asm.if_word(CNT, "<", PER, done_h),
             asm.if_byte(HELD, "bit_on", KEY, miss), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(holdw),
             done_h, Op(b"\x54\x01")]
    # a hit: pay (a HOLD twice), streak, maybe a tier up (its lines the first time with this partner)
    once = asm.nop()
    main += [hit, Op(TK.HIT_SOUND), Op(bytes([0x96, REPS[0], REPS[1]])), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])),
             asm.if_byte(HOLD, "==", 1, once), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])), once,
             Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(TIER, "<", n - 1, after),
             asm.if_byte(STREAK, ">=", TK.HITS_UP, after), Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)]
    for part in (0, 1):
        for t in range(1, n):
            nx = asm.nop()
            if (part, t) in gid:
                bit = t + 4 * part
                main += [asm.if_byte(P, "==", part, nx), asm.if_byte(TIER, "==", t, nx), asm.if_byte(SEEN, "bit_off", bit, nx),
                         asm.biton(SEEN, bit), req(E["talk"], 2 + gid[(part, t)]), nx]
    main += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
             asm.goto_back(rest), tail, Op(bytes([0x95, SINCE[0], SINCE[1]]))]
    # (user: long silences) chatter every CHAT_EVERY reps; (user: variations) Cloud's pose every STYLE_EVERY
    quiet, same, busy = asm.nop(), asm.nop(), asm.nop()
    main += [Op(bytes([0x95, CHAT[0], CHAT[1]])), asm.if_byte(CHAT, ">=", TK.CHAT_EVERY, quiet), asm.setbyte(CHAT, 0)] + \
        by_p(lambda p: line_from("chat%d" % p)) + [quiet]
    main += [Op(bytes([0x95, SC[0], SC[1]])), asm.if_byte(SC, ">=", TK.STYLE_EVERY, same), asm.setbyte(SC, 0),
             Op(bytes([0x93, STYLE[0] << 4, STYLE[1], 1])),                   # XOR STYLE, 1 (the next rep shows it)
             asm.if_byte(TALKING, "==", 0, same), asm.setbyte(TALKING, 1), asm.setbyte(CHAT, 0),
             req(E["talk"], style_slot), same]
    fin = asm.nop()
    main += [asm.if_word(REPS, "<", TK.TOTAL_REPS, fin), asm.goto_back(rep)]
    # a miss: the buzz, a line, back to the slowest pace, the rep's rest, then on
    slow, mtail, mdone = asm.nop(), asm.nop(), asm.nop()
    main += [miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]])),
             asm.setbyte(CHAT, 0)] + by_p(lambda p: line_from("miss%d" % p)) + [slow,
             asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), mtail, asm.if_word(CNT, "<", PER, mdone),
             hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(mtail), mdone, asm.goto_back(tail)]
    # the girls' "My turn!": [MENU] in time = a bonus; either way Cloud switches partner (fast fade)
    sw_wait, sw_judge, sw_miss, sw_go = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    main += [sw_rep] + ch_(P, [[req(E["talk"], 2 + gid[("switch", 0)])], [req(E["talk"], 2 + gid[("switch", 1)])]]) + \
        [hb._req(E["prompt"], 8, wait=False),
         sw_wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, sw_judge),
         asm.if_word(CNT, "<", PER, sw_miss), asm.goto_back(sw_wait),
         sw_judge, asm.if_byte(PR, "==", 4, sw_miss), Op(b"\x54\x01"), hb._arith(0x86, PAY, TK.SWITCH_BONUS),
         asm.goto(sw_go),
         sw_miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0),
         sw_go, Op(bytes([0x93, P[0] << 4, P[1], 1])),                               # XOR P, 1
         asm.setbyte(SINCE, 0), Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], TK.SWITCH_RANGE])),
         asm.setbyte(NEXTSW, RND), Op(bytes([0x85, NEXTSW[0] << 4, NEXTSW[1], TK.SWITCH_MIN])),      # PLUS
         ] + fast_out + [req(E[a], 2) for a in ("cloudB", "tifaB", "jessB")] + [hb._w(8)] + fast_in + \
        [asm.goto_back(rep)]
    # (user) the head hold: both held deep until Jessie taps out; let go in time = a hit (double pay) plus a
    # bonus; before = a miss; too late = she's mad (MAD_LIMIT: she walks out)
    early, cue, good, late, calm, hw, lw = (asm.nop() for _ in range(7))
    result = [asm.setbyte(HC, 0)] + frames(HC, TK.RESULT_WAIT) + [Op(b"\x54\x01")]
    restart = [req(E[a], 2) for a in ("cloudB", "jessB")]
    walkout = asm.nop()
    main += [head_hold, Op(b"\x54\x01"), req(E["cloudB"], 5), req(E["jessB"], 5)] + prompt_line("hold") + \
        [Op(bytes([0x99, CUE[0], CUE[1]])), Op(bytes([0x8D, CUE[0] << 4, CUE[1], TK.HOLD_RANGE])),
         Op(bytes([0x85, CUE[0] << 4, CUE[1], TK.HOLD_MIN])), asm.setbyte(HC, 0),
         hw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, early), Op(bytes([0x95, HC[0], HC[1]])),
         asm.if_byte(HC, "<", CUE, cue), asm.goto_back(hw),
         cue, Op(b"\x54\x01"), req(E["jessB"], 6)] + prompt_line("cue") + \
        [asm.setbyte(HC, 0), lw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, good), Op(bytes([0x95, HC[0], HC[1]])),
         asm.if_byte(HC, "<", TK.LETGO, late), asm.goto_back(lw)]
    main += [good, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 0xEA, 1, 0x40]))]           # (the materia chime)
    for _ in range(TK.HOLD_BONUS):
        main += [hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]]))]
    main += prompt_line("good") + restart + result + [asm.goto_back(hit)]
    main += [early, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]]))] + \
        prompt_line("early") + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + restart + result + [asm.goto_back(tail)]
    zero, paid_ = asm.nop(), asm.nop()
    main += [late, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]])),
             Op(bytes([0x95, ANGER[0], ANGER[1]])), asm.if_byte(ANGER, ">=", TK.MAD_LIMIT, calm), asm.goto(walkout), calm] + \
        prompt_line("mad", ANGER) + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + restart + \
        [asm.if_word(PAY, "<", TK.MAD_PENALTY, zero), hb._arith(0x88, PAY, TK.MAD_PENALTY), asm.goto(paid_),
         zero, asm.setword(PAY, 0), paid_] + result + [asm.goto_back(tail)]
    # the end: the train pulls in
    pay = asm.nop()
    main += [fin, Op(b"\x54\x01"), Op(b"\x54\x02"), hb._w(30)]
    for t in TK.FINALE:
        main += say(t)
    main += [asm.goto(pay)]
    # (user) Jessie walked off down the carriage (she has no affection to lose); paid what was earned
    main += [walkout, Op(b"\x54\x01"), Op(b"\x54\x02")] + say(TK.WALKOUT[0]) + \
        fade_out + [req(E["jessB"], 4), asm.setbyte(P, 0), asm.setbyte(STYLE, 0)] + \
        [req(E[a], 2) for a in ("cloudB", "tifaB")] + [hb._w(10)] + fade_in
    for t in TK.WALKOUT[1:]:
        main += say(t)
    main += [pay, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, TK.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(TK.PAID)
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
    print("  685: Tickets, please! on %s (Tifa %s, Jessie %s dir %d; Cloud behind %s / at her head %s; drops %s; Tifa sunk %d; "
          "%d texts, script %d bytes)" % (TK.FIELD, st, sj, dj, ck, ch, PZ["drops"], PZ["sink"], n_text, len(f.sections[0])))

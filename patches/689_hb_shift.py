"""(user) The Honey Bee Inn shift (data `_hb_shift.py`, plan docs/hb_shift.md): Tifa works a night at the inn, Cloud
is security. Started from the Honey Bee manager in onna_4 ("Tifa's shift.", 620 `_manager`). Set FIELD (a debug
room only startmap leads to) = a copy of the inn's room onna_52, script blanked, gateways cleared. Three customers
a shift, one at a time, random without repeats (start S = RANDOM mod 9, step K = 1 + RANDOM mod 8: S, S+K, S+2K
mod 9 never repeat). A visit: fade in, his opening, three rounds of (Tifa's approach = an ASK, its weight moves
his mood (the danger meter, 0-10), his reply; then a dance: `PROMPTS` button prompts while she dances (Honey Bee
dancer moves retargeted onto her dress), a hit +1, a miss -1), then the ending by his type and mood (see the data
module): the open ones' explicit scene (her undressed ZTFA and his dressed model in the movie's anims, 670's
relative layout turned onto this room's bed), the timid ones' scene, the pushy ones' incident (security: Cloud
walks in from the door and punches him down, our own punch YHPU and his own fall YHF<k> (`_fall`); or Tifa's kick YHKK, Cloud
arriving after) or their coming round. Tips by mood x his rate; the shift's total paid at the end. Checked on
offline renders only, untested in-game."""
import importlib
import math
import struct

import _besties_rig as RG
import _danger as DG
import _gestures as GS
import _hb_shift as HS
from ff7 import asm
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

KEY, PR, RND, KP, HELD, METER, SIDE, DEC, CUST, STEPK, VN, DN, POS, VIEW, TIER, N2 = ((5, a) for a in range(100, 116))
PRV = [(5, 116 + k) for k in range(3)]
CNT, PER, GIL, TIP = ((6, a) for a in range(120, 128, 2))
TIFA_DONOR = ("colne_4", 5)             # Tifa's Wall Market dress, AXJA (stand ABCD, walk ABCE)
BARE_TIFA = "ZTFA.HRC"
DANCES = ["DXHE.tor", "DXIB.tor", "DXIF.tor", "DXJA.tor"]     # the Honey Bee dancer's moves (on Ruby's skeleton)
FALL_FRAMES, FALL_REST = 14, 0.9         # our own fall (`_fall`): frames to the floor; the root's height lying
POS_ORDER = ("head", "cowgirl", "mission")
# 670's raw spots (girl x y dz dir, cloud x y dz dir) and the turn onto this bed (mission: her head to the pillow
# at +x; cowgirl: his head to the pillow; checked on offline renders)
REL = {"head": ((42, -224, 0, 0x40), (80, -225, 0, 0xC0), 0),
       "cowgirl": ((18, -95, 14, 0x80), (18, -95, 0, 0x80), 64),
       "mission": ((-215, -59, 0, 0x00), (-215, -25, -4, 0x80), 192)}
PUNCH = dict(frames=36, hits=(8, 20, 32))   # three punches, the last an uppercut; hit frames for the sound
KICK = dict(frames=30, hit=11)
# (timid scenes) the line of the good ending at which Tifa acts, and her slot: 5 kick, 6 hip rock
ACT_AT = {"praise": (0, 6), "kata": (2, 5), "listen": None}


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _punch(ctx, name):
    """Cloud's three punches (the last an uppercut) on AAAA: the right fist from a guard by his chin out to arm's
    length, the torso turning into it, the left hand guarding."""
    c = PUNCH
    frames = []
    for k in range(c["frames"]):
        n, t = divmod(k, 12)
        e = 0.0 if t < 4 else min(1.0, (t - 4) / 3) if t < 8 else 1.0 if t < 9 else max(0.0, 1 - (t - 9) / 3)
        rg = RG.Rig(ctx, "AAAA.HRC", "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
        rg.waist(RG.turn(20 * e))
        rg.root = RG.add(rg.root, [0.0, 0.0, -0.4 * e])
        E = rg.ends()
        L = rg.length["r_uparm"] + rg.length["r_foarm"]
        S, Sl = E["r_uparm@"], E["l_uparm@"]
        out = [0.2, -0.55, -0.75] if n == 2 else [0.15, 0.05, -0.97]
        guard = [0.3, 0.15, -0.35]
        rg.ik("r_uparm", "r_foarm", RG.add(S, RG.mul(RG.lerp(guard, out, e), L)), [-0.6, 1.0, 0.5], keep_end=False)
        rg.ik("l_uparm", "l_foarm", RG.add(Sl, RG.mul([-0.3, 0.1, -0.4], L)), [0.6, 1.0, 0.5], keep_end=False)
        frames.append(rg.frame())
    return RG.save(ctx, name, "acfe.a", frames)


def _kick(ctx, hrc, name):
    """Tifa's front kick on her dress (AXJA): the right knee up, the leg snapped out high, held, back; leaning back,
    fists up."""
    down, fwd = [0.0, 1.0, 0.0], RG.unit([0.0, 0.2, -1.0])
    high, hang = RG.unit([0.0, -0.5, -1.0]), RG.unit([0.0, 1.0, 0.25])
    keys = [(0, down, down, 0), (8, fwd, hang, -6), (12, high, high, -16), (18, high, high, -16), (24, fwd, hang, -6),
            (KICK["frames"], down, down, 0)]
    frames = []
    for k in range(KICK["frames"]):
        j = max(i for i, kk in enumerate(keys) if kk[0] <= k)
        a, b = keys[j], keys[min(j + 1, len(keys) - 1)]
        t = 0.0 if b[0] == a[0] else (k - a[0]) / (b[0] - a[0])
        rg = RG.Rig(ctx, hrc, "abcd.a").start(RG.basis(RG.LEFT, RG.UP))
        rg.waist(RG.bow(a[3] + (b[3] - a[3]) * t))
        rg.aim("r_femur", RG.unit(RG.lerp(a[1], b[1], t)))
        rg.aim("r_tibia", RG.unit(RG.lerp(a[2], b[2], t)))
        E = rg.ends()
        L = rg.length["r_uparm"] + rg.length["r_foarm"]
        for s, sx in (("l", 1), ("r", -1)):
            rg.ik(s + "_uparm", s + "_foarm", RG.add(E[s + "_uparm@"], RG.mul([-sx * 0.25, 0.1, -0.5], L)),
                  [sx * 0.6, 1.0, 0.5], keep_end=False)
        frames.append(rg.frame())
    return RG.save(ctx, name, "abcd.a", frames)


def _fall(ctx, hrc, stand, name):
    """A customer knocked flat on his back, stiff as a plank (on his own skeleton): pitched back about his root
    over FALL_FRAMES, the root dropped until he lies on the floor, a bounce, then still."""
    rg0 = RG.Rig(ctx, hrc, stand).start(RG.basis(RG.LEFT, RG.UP))
    E0 = rg0.ends()
    feet = max(E0[s + "_foot"][1] for s in "lr")
    lie = feet - rg0.root[1] - FALL_REST                    # (model y down) how far the root drops
    frames = []
    for k in range(FALL_FRAMES + 12):
        t = min(1.0, k / FALL_FRAMES) ** 2
        bounce = 0.25 * math.sin(math.pi * min(1.0, max(0.0, (k - FALL_FRAMES) / 6))) if k > FALL_FRAMES else 0
        rg = RG.Rig(ctx, hrc, stand).start(RG.basis(RG.LEFT, RG.UP))
        rg.pelvis(RG.bow(-88 * t))
        rg.root = RG.add(rg.root, [0.0, lie * t - bounce, 0.0])
        for s, sx in (("l", 1), ("r", -1)):                 # (arms thrown out)
            rg.aim(s + "_uparm", RG.unit(RG.lerp(RG.unit(RG.sub(rg.ends()[s + "_uparm"], rg.ends()[s + "_uparm@"])),
                                                  [sx * 1.0, 0.3, 0.6], t)))
        frames.append(rg.frame())
    return RG.save(ctx, name, stand, frames)


def _spot(mesh, x, y, high=False):
    """(x, y, z, tri) on the floor (or the highest piece there: the bed)."""
    ts = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y)]
    assert ts, (x, y)
    t = max(ts, key=lambda t: mesh.height(t, x, y)) if high else min(ts, key=lambda t: mesh.height(t, x, y))
    return round(x), round(y), round(mesh.height(t, x, y)), t


def _walkable(mesh, a, b):
    for k in range(41):
        x, y = a[0] + (b[0] - a[0]) * k / 40, a[1] + (b[1] - a[1]) * k / 40
        if not any(mesh.contains(t, x, y) for t in range(len(mesh.tris))):
            return False
    return True


def _layout(mesh):
    """{position: (girl spot, girl dir, his spot, his dir)} on this room, from 670's relative layout."""
    out = {}
    for p in POS_ORDER:
        g, c, rot = REL[p]
        gx, gy = HS.POSITIONS[p]["girl"]
        a = rot * 2 * math.pi / 256
        dx, dy = c[0] - g[0], c[1] - g[1]
        cx, cy = gx + dx * math.cos(a) - dy * math.sin(a), gy + dx * math.sin(a) + dy * math.cos(a)
        bed = HS.POSITIONS[p]["bed"]
        G, C = _spot(mesh, gx, gy, bed), _spot(mesh, cx, cy, bed)
        out[p] = ((G[0], G[1], G[2] + g[2], G[3]), (g[3] + rot) % 256, (C[0], C[1], C[2] + c[2], C[3]), (c[3] + rot) % 256)
    return out


def apply(ctx):
    mv, hb, dt = _mods()
    ctx.field(HS.FIELD)
    ctx.field(HS.BASE)
    f = ctx._fields[HS.FIELD] = FieldFile(ctx._orig_raw[HS.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    mesh = Walkmesh(f.section("walkmesh"))
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    lay = _layout(mesh)
    talk_t, talk_g = _spot(mesh, *HS.TALK_TIFA), _spot(mesh, *HS.TALK_GUEST)
    door, guard = _spot(mesh, *HS.DOOR), _spot(mesh, *HS.SECURITY_AT)
    assert _walkable(mesh, HS.DOOR, HS.SECURITY_AT)
    focus = [_spot(mesh, *HS.FOCUS_TALK), _spot(mesh, *HS.FOCUS_BED)]
    # anims
    tifa_d = mv._retarget(ctx, DANCES, "YH", "axja.hrc", "abcd.a")
    kick = _kick(ctx, "AXJA.HRC", "YHKK")
    rock = GS._hiprock(ctx, "AXJA.HRC", "YHHR")
    punch = _punch(ctx, "YHPU")
    strokes = {p: ["ZN%s%d.tor" % (HS.POSITIONS[p]["letter"], s) for s in range(4)] for p in POS_ORDER}
    hers = {p: ["ZV%s%d.tor" % (HS.POSITIONS[p]["letter"], s) for s in range(4)] for p in POS_ORDER}
    for n in sum(strokes.values(), []) + sum(hers.values(), []):
        ctx.char_file(n.split(".")[0].lower() + ".a")                       # (exists)
    # models: 0 the hidden player, 1 Tifa dressed, 2 Tifa bare, 3 Cloud (security), 4.. the customers, the meter
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    c_anims = ModelLoader.anims(cl0)
    assert c_anims[:2] == ["ACFE.aki", "AAFF.aki"]
    ti = loader.add_from(ModelLoader(ctx.field(TIFA_DONOR[0]).section("models")), TIFA_DONOR[1])
    tifa_e = loader.models.pop(ti)
    t_anims = ModelLoader.anims(tifa_e)
    assert ModelLoader.hrc(tifa_e) == "AXJA.HRC" and t_anims[:2] == ["ABCD.yos", "ABCE.yos"]
    tifa_list = t_anims[:2] + tifa_d + [kick, rock]
    bare_list = t_anims[:1] + sum((hers[p] for p in POS_ORDER), [])
    models = [ModelLoader.only_anims(cl0, c_anims[:2]),
              ModelLoader.only_anims(tifa_e, tifa_list),
              ModelLoader.only_anims(ModelLoader.with_hrc(tifa_e, BARE_TIFA, "hbshift_tifab.char"), bare_list),
              ModelLoader.only_anims(cl0, c_anims[:2] + [punch])]
    cust_lists = []
    for cu in HS.CUSTOMERS:
        dl = ModelLoader(ctx.field(cu["donor"][0]).section("models"))
        k = loader.add_from(dl, cu["donor"][1])
        e = loader.models.pop(k)
        own = ModelLoader.anims(e)
        fall = _fall(ctx, ModelLoader.hrc(e), own[0].split(".")[0].lower() + ".a", "YHF%d" % len(cust_lists))
        lst = own[:1] + [fall] + (strokes[cu["pos"]] if cu["type"] == "open" else [])
        cust_lists.append(lst)
        models.append(ModelLoader.only_anims(e, lst))
    loader.models = models
    meter = DG.build(ctx, f, loader, "R", [fc[:3] for fc in focus])
    assert len(loader.models) == 4 + len(HS.CUSTOMERS) + 2 <= 16
    assert all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    # entities
    cnames = ["c_" + cu["key"][:6] for cu in HS.CUSTOMERS]
    names = ["dir", "cloud", "tifa", "tifab", "sec"] + cnames + ["dance", "k_sw", "k_ca", "k_ok", "prompt",
                                                                 "gauge", "cursor"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    once = lambda i, stand=0: [mv._animb(), Op(bytes([0xA2, stand, 1])), Op(bytes([0xA3, i, 1]))]
    ch_ = mv._chain
    at = lambda p, d: [xyzi(*p[:4]), d_(d)]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))
    to = lambda a, b: dt._dir_to(b[0] - a[0], b[1] - a[1])
    face_g, face_t = to(talk_g, talk_t), to(talk_t, talk_g)
    scripts = {}
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at(focus[0], 0) + [hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()],
                           2: ch_(VIEW, [at(fc, 0) for fc in focus]) + [asm.ret()]}
    ti_ = lambda n: tifa_list.index(n)
    scripts[E["tifa"]] = {
        0: [Op(bytes([0xA1, 1]))] + at(talk_t, face_t) + [hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: at(talk_t, face_t) + [hb._visi(1)] + loop_(0) + [asm.ret()],
        3: ch_(DN, [loop_(ti_(n)) for n in tifa_d]) + [asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: once(ti_(kick)) + [asm.ret()],
        6: once(ti_(rock)) + [asm.ret()],
        7: loop_(0) + [asm.ret()]}
    bi = lambda n: bare_list.index(n)
    lay_ops = lambda who, anims_of: ch_(POS, [at(*((lay[p][0], lay[p][1]) if who == "girl" else (lay[p][2], lay[p][3]))) +
                                              ch_(TIER, [loop_(anims_of(p, s)) for s in range(4)]) for p in POS_ORDER])
    scripts[E["tifab"]] = {
        0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: lay_ops("girl", lambda p, s: bi(hers[p][s])) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    # security: in from the door to his spot by the customer (MOVE: the straight line is floor, asserted)
    scripts[E["sec"]] = {
        0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: at(door, to(door, guard)) + [hb._visi(1), hb.sound(HS.DOOR_SOUND), hb._move(*guard[:2]),
                                         d_(to(guard, talk_g))] + loop_(0) + [asm.ret()],
        3: once(2) + [asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    for k, cu in enumerate(HS.CUSTOMERS):
        lst = cust_lists[k]
        s = {0: [Op(bytes([0xA1, 4 + k])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
             2: at(talk_g, face_g) + [hb._visi(1)] + loop_(0) + [asm.ret()],
             3: [mv._animb(), Op(bytes([0xAF, 1, 1])), asm.ret()],
             4: [hb._visi(0), asm.ret()],
             6: [d_(to(talk_g, guard)), asm.ret()]}                     # (turns to face security)
        if cu["type"] == "open":
            p = cu["pos"]
            s[5] = at(lay[p][2], lay[p][3]) + ch_(TIER, [loop_(lst.index(strokes[p][t])) for t in range(4)]) + \
                [hb._visi(1), asm.ret()]
        scripts[E[cnames[k]]] = s
    # the buttons: one small entity each; a press = up -> down (PR = its number)
    for k, (mask, _) in enumerate(HS.KEYS):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    pr = {0: [asm.ret(), asm.ret()]}
    for j, (_, label) in enumerate(HS.KEYS):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, 30, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    scripts[E["prompt"]] = pr
    sc_ = DG.scripts(meter, METER, xyzi, view=VIEW)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    MG_ = (E["gauge"], E["cursor"])

    def mood(w):
        """METER += w, clamped 0..10, the cursor moved."""
        top_ = DG.STEPS - 1
        done = asm.nop()
        if w > 0:
            ok = asm.nop()
            ops = [Op(bytes([0x85, METER[0] << 4, METER[1], w])), asm.if_byte(METER, ">", top_, ok),
                   asm.setbyte(METER, top_), ok]
        elif w < 0:
            low = asm.nop()
            ops = [asm.if_byte(METER, "<", -w, low), asm.setbyte(METER, 0), asm.goto(done), low,
                   Op(bytes([0x87, METER[0] << 4, METER[1], -w]))]
        else:
            ops = []
        return ops + [done, req(E["cursor"], 2)]

    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    # the dance: PROMPTS prompts while she dances (REQEW'd by the director, which waits)
    top_, wait, judge, miss, nxt, end_, last = (asm.nop() for _ in range(7))
    dance = [asm.setbyte(N2, 0), top_, Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 4])),
             asm.setbyte(DN, RND), req(E["tifa"], 3),
             Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])), asm.setbyte(KEY, RND),
             asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0), asm.setword(CNT, 0)]
    dance += ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)])
    dance += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
              asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait),
              judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss)]
    dance += [hb.sound(HS.HIT_SOUND)] + mood(1) + [hb._arith(0x86, GIL, 10), asm.goto(nxt)]
    dance += [miss, Op(b"\x54\x01"), buzz] + mood(-1) + [asm.if_byte(METER, "!=", 0, nxt), asm.goto(end_)]
    dance += [nxt, hb._w(12), Op(bytes([0x95, N2[0], N2[1]])), asm.if_byte(N2, "<", HS.PROMPTS, last),
              asm.goto_back(top_), last, end_, req(E["tifa"], 7), asm.ret()]
    scripts[E["dance"]] = {0: [asm.ret(), asm.ret()], 2: dance}

    # the director
    say = lambda t: hb._say(sec, t)
    lines = lambda ts: sum((say(t) for t in ts), [])
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    main = [hb._uc(1), hb._menu(1), asm.setword(GIL, 0), asm.setbyte(VIEW, 0), asm.setbyte(HELD, 0),
            Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], len(HS.CUSTOMERS)])),
            asm.setbyte(CUST, RND),
            Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], len(HS.CUSTOMERS) - 1])),
            asm.setbyte(STEPK, RND), Op(bytes([0x95, STEPK[0], STEPK[1]])), asm.setbyte(VN, 0),
            hb._req(E["cloud"], 2), hb._req(E["tifa"], 2), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, HS.MUSIC]) + bytes(8))]
    main += lines(HS.INTRO) + say(HS.HOW) + fade_out
    visit_top, visit_end = asm.nop(), asm.nop()
    main += [visit_top] + ch_(VN, [[asm.setword(PER, p_)] for p_ in HS.PERIODS])
    blocks = []
    for k, cu in enumerate(HS.CUSTOMERS):
        ce = E[cnames[k]]
        good, meh, bad, tip, leave, inc = (asm.nop() for _ in range(6))
        first_ = asm.nop()
        b = [hb._req(ce, 2), hb._req(E["tifa"], 2), asm.setbyte(VIEW, 0), hb._req(E["cloud"], 2),
             hb.sound(HS.DOOR_SOUND), hb._w(10)] + fade_in
        b += [asm.if_byte(VN, "!=", 0, first_)] + say(HS.NEXT) + [first_]
        b += lines(cu["intro"]) + [asm.setbyte(METER, cu["mood"])] + [req(e, 2) for e in MG_]
        for prompt, opts in cu["rounds"]:
            ask, first = hb._ask(sec, prompt, [o[0] for o in opts])
            b += ask
            outs = asm.nop()
            for i, (_, w, reply) in enumerate(opts):
                nx = asm.nop()
                b += [asm.if_byte(hb.CHOICE, "==", first + i, nx)]
                if w == "X":
                    assert cu["type"] == "pushy"
                    b += [asm.goto(inc)]
                else:
                    b += mood(w) + say(reply)
                b += [asm.goto(outs), nx]
            b += [outs, asm.if_byte(METER, "!=", 0, bad), hb._req(E["dance"], 2), asm.if_byte(METER, "!=", 0, bad)]
        b += [asm.if_byte(METER, ">=", HS.GOOD, meh), good] + DG.hide(MG_)
        if cu["type"] == "open":                                            # all the way
            p = cu["pos"]
            b += fade_out + [hb._req(E["tifa"], 4), hb._req(ce, 4), asm.setbyte(POS, POS_ORDER.index(p)),
                             asm.setbyte(TIER, 0), hb._req(E["tifab"], 2), hb._req(ce, 5),
                             asm.setbyte(VIEW, 1 if HS.POSITIONS[p]["bed"] else 0), hb._req(E["cloud"], 2),
                             hb._w(15)] + fade_in
            for i, t in enumerate(cu["good"]):
                b += say(t)
                if 0 < i < 4:
                    b += [Op(bytes([0x95, TIER[0], TIER[1]])), req(E["tifab"], 2), req(ce, 5)]
            b += fade_out + [hb._req(E["tifab"], 4), hb._req(ce, 4), asm.setbyte(VIEW, 0), hb._req(E["cloud"], 2),
                             hb._w(10), asm.goto(tip)]
        else:
            act = ACT_AT.get(cu.get("act"))
            for i, t in enumerate(cu["good"]):
                if act and act[0] == i:
                    b += [hb._req(E["tifa"], act[1], wait=(act[1] == 5))]
                b += say(t)
            b += [asm.goto(tip)]
        b += [meh] + DG.hide(MG_) + say(cu["meh"]) + [asm.goto(tip)]
        if cu["type"] == "pushy":                                           # the incident
            b += [bad, inc] + DG.hide(MG_) + say(cu["grab"])
            ask, first = hb._ask(sec, HS.INCIDENT_ASK, HS.INCIDENT_CHOICES)
            herself, done = asm.nop(), asm.nop()
            b += ask + [asm.if_byte(hb.CHOICE, "==", first, herself)] + say(HS.CALL) + [hb._req(E["sec"], 2), hb._req(ce, 6)] + \
                lines(HS.SECURITY) + [req(E["sec"], 3)]
            last_ = 0
            for h in PUNCH["hits"]:
                b += [hb._w(h - last_), hb.sound(HS.HIT_FX)]
                last_ = h
            b += [req(ce, 3), hb._w(40)] + lines(HS.BEATEN) + [asm.goto(done)]
            b += [herself] + say(HS.HERSELF) + [req(E["tifa"], 5), hb._w(KICK["hit"]), hb.sound(HS.HIT_FX),
                                                 req(ce, 3), hb._w(40), hb._req(E["sec"], 2)] + lines(HS.LATE)
            b += [done, hb._arith(0x86, GIL, HS.DAMAGES)] + fade_out + \
                [hb._req(E["sec"], 4), hb._req(ce, 4), asm.goto(visit_end)]
        else:
            b += [bad] + DG.hide(MG_) + say(cu["bad"]) + [asm.goto(leave)]
        b += [tip, asm.setword(TIP, 0), hb._arith(0x86, TIP, METER), hb._arith(0x8A, TIP, cu["rate"]),
              hb._arith(0x86, GIL, TIP)]
        b += [asm.if_byte(METER, ">=", HS.GOOD, leave), hb._arith(0x86, GIL, HS.TIP_BONUS)]
        b += [leave] + fade_out + [hb._req(ce, 4)]
        blocks.append(b)
    main += ch_(CUST, blocks)
    nomore = asm.nop()
    main += [visit_end, Op(bytes([0x95, VN[0], VN[1]])), asm.if_byte(VN, "<", HS.SHIFT, nomore),
             Op(bytes([0x85, CUST[0] << 4 | STEPK[0], CUST[1], STEPK[1]])),
             Op(bytes([0x8D, CUST[0] << 4, CUST[1], len(HS.CUSTOMERS)])), asm.goto_back(visit_top), nomore]
    # the end of the shift: the total, Cloud comes in, home
    main += [hb._req(E["tifa"], 2), hb._w(10)] + fade_in
    paid = say(HS.SUMMARY)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))       # MPRA2 after WINDOW
    main += [Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), hb.sound(0x168)] + paid
    main += [hb._req(E["sec"], 2)] + lines(HS.OUTRO) + fade_out
    onna4 = Walkmesh(ctx.field("onna_4").section("walkmesh"))
    bx, by = hb.BACK_AT
    stop_ = hb._w(30)
    main += [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0),
             asm.mapjump(ctx.maplist.index("onna_4"), bx, by, onna4.find(bx, by), 0x80), stop_, asm.goto_back(stop_)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  689: Honey Bee shift on %s (%d customers; layout %s; %d texts, script %d bytes)"
          % (HS.FIELD, len(HS.CUSTOMERS), {p: (v[0][:3], v[1], v[2][:3], v[3]) for p, v in lay.items()}, n_text,
             len(f.sections[0])))

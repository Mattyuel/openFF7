"""(user) The 7th Heaven bar shift (data `_bar.py`): Tifa serves, Cloud is security. Marle, in the real 7th Heaven
(mds7pb_1), asks "Work a shift." -> FIELD (a debug room only startmap leads to) = a copy of mds7pb_1, script blanked
but its background entities (COUNTER, LIGHT, TV, the pinball machine), gateways cleared.

Three stools (`SEATS`), each its own entity `seatK` running a customer's visit (two customers a stool, taking
turns): a gap, he sits (Cloud's sitting anim CXDC), an order (a drink at random, or arriving drunk and rowdy:
`ROWDY_ODDS`) shown in window K over him (entity `winK`: one slot per text), his patience counting down (it turns
urgent "!!" at `URGENT`); missed = he leaves, or turns rowdy (`ANGRY_ODDS`); a rowdy customer left too long
trashes the place (`TRASH_COST`, everyone else leaves). The director polls the buttons (one entity per button):
a drink's button = Tifa makes it for the waiting customer with the least patience who ordered it (none = the
buzz): seat state 2, window 3 "Tifa is busy making a cocktail..." while she shakes (her CXHC with the original
scene's sounds) for its make frames, presses meanwhile buzz; then she serves (CXIB), the customer is paid for
(price + `QUICK_TIP` if served before he turned urgent), drinks a while and leaves. [PAGEDOWN] (R1) = Cloud walks
over and escorts the first rowdy customer out of the door (stepped XYZI walks; the director waits, so no drinks are
made meanwhile: "Cloud is escorting a rowdy customer out..."). `SHIFT_FRAMES` of orders, then last orders, the
night's takings (GOLDU), back beside Marle. Seat states ST: 0 empty, 1 waiting, 2 being made / escorted,
3 served, 4 escorted out, 5 sent away. Checked on offline renders only (stools, Tifa, Cloud's paths), untested
in-game."""
import importlib
import math
import struct

import _bar as BR
import _walker as WK
import _besties_rig as RG
from _recruit import sound
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera, screen_range
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

ORD = [(5, 100 + s) for s in range(3)]
ST = [(5, 103 + s) for s in range(3)]
CUR = [(5, 106 + s) for s in range(3)]
RS = [(5, 109 + s) for s in range(3)]
PR = (5, 112)
RNS = [(5, 113 + s) for s in range(3)]
RND, K, SEL, END, TRASH = (5, 116), (5, 117), (5, 118), (5, 119), (5, 120)
PRV = [(5, 121 + k) for k in range(5)]
NSERVED, NMISS, GO = (5, 126), (5, 127), (5, 128)
PAT = [(6, 140 + 2 * s) for s in range(3)]
CNTS = [(6, 146 + 2 * s) for s in range(3)]
T, GIL, BEST, MK = (6, 152), (6, 154), (6, 156), (6, 158)
CW = ((6, 160), (6, 162), (5, 129))     # Cloud's walk (x, y words, step counter)
UW = ((6, 164), (6, 166), (5, 130))     # the escorted patron's walk (one at a time)
CUSTOMERS = [("mds7pb_1", 4), ("mds7pb_1", 5), ("mds7pb_1", 3),          # Avalanche's regulars (avaman / avafat /
             ("blackbg2", 9), ("rcktin2", 5), ("jail2", 6)]              # avawoman), a sailor, a mechanic, a punk
KEEP = ("COUNTER", "LIGHT", "TV")       # background entities whose scripts stay
SIT, SIT_LAST = "CXDC.tor", 14          # (Cloud stepping up onto a stool and sitting, mds7pb_1: 15 frames)
MAKE, SERVE = "CXHC.tor", "CXIB.tor"    # (Tifa: shaking a drink, then serving it: the original scene)
SHAKE_SOUND, SERVE_SOUND, CRASH_SOUND = 0xBB, 0xB9, 0x76
SWAY = dict(frames=60, lean=7, counter=1.6, head=12)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _sway(ctx, hrc, stand, name):
    """A drunk swaying on his feet: the body leaning side to side once a cycle about his feet, the upper body and
    head lolling the other way, arms hanging loose."""
    c = SWAY
    frames = []
    for k in range(c["frames"]):
        s = math.sin(2 * math.pi * k / c["frames"])
        rg = RG.Rig(ctx, hrc, stand).start(RG.basis(RG.LEFT, RG.UP))
        E0 = rg.ends()
        feet = {sd: E0[sd + "_tibia"] for sd in "lr"}
        rg.pelvis(RG.lean(c["lean"] * s))
        rg.waist(RG.lean(-c["lean"] * c["counter"] * s))
        rg.neck(RG.chain(RG.lean(c["head"] * s), RG.bow(10)))
        for sd, sx in (("l", 1), ("r", -1)):
            rg.ik(sd + "_femur", sd + "_tibia", feet[sd], [sx * 0.2, 0.0, -1.0], keep_end=True)
        frames.append(rg.frame())
    return RG.save(ctx, name, stand, frames)


def _walkable(mesh, a, b):
    return WK.floor_leg(mesh, a, b)


def _walk(hb, animb, path, wx, wy, n_, walk, stand, to, step):
    return WK.walk(hb, animb, path, wx, wy, n_, walk, stand, to, step)


def _retile(f):
    """(user: the counter drew over the seated patrons, the door area over Cloud and the patron he walks out) the
    counter's front to COUNTER_TO, the door's bench / floor tiles to DOOR_TO.., the PC depth (+38) on the room's own
    line (fitted on its layer-2 tiles: id -> depth is near linear over the furniture's range)."""
    from ff7.background import Background
    bg = Background(f.section("background"))
    layer2 = [t for k, _, ts, _ in bg.layers if k == 2 and ts for t in ts]
    pts = sorted({(t._get("<H", 24), t._get("<I", 38)) for t in layer2 if 1000 < t._get("<H", 24) < 4000})
    (i0, d0), (i1, d1) = pts[0], pts[-1]
    depth = lambda i: round(d0 + (i - i0) * (d1 - d0) / (i1 - i0))
    new = {i: BR.COUNTER_TO for i in BR.COUNTER_TILES}
    new.update({i: BR.DOOR_TO + k for k, i in enumerate(BR.DOOR_TILES)})
    moved = 0
    for t in layer2:
        i = t._get("<H", 24)
        if i in new:
            t._set("<H", 24, new[i])
            t._set("<I", 38, depth(new[i]))
            moved += 1
    assert moved >= 40, moved
    f.set_section("background", bg.build())


def _marle(ctx):
    """Marle in the real 7th Heaven: "Work a shift." -> the set."""
    import _travel as TV
    hb = _mods()[1]
    f = ctx.field(BR.BASE)
    mesh = Walkmesh(f.section("walkmesh"))
    mt = mesh.find(*BR.MARLE_AT)
    assert mt is not None
    model = TV.copy_model(ctx, BR.BASE, "mds7", 10)                      # midgal_obasan2
    ax, ay = BR.ARRIVE
    at_ = mesh.find(ax, ay)                                              # (the set is a copy: same walkmesh)
    assert at_ is not None

    def talk(sec):
        end = hb._uc(0)
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + hb._say(sec, BR.MARLE["greet"])
        ask, first = hb._ask(sec, *BR.MARLE["ask"])
        no = asm.nop()
        ops += ask + [asm.if_byte(hb.CHOICE, "==", first, no), hb._uc(0), Op(hb.FADE_OUT), Op(b"\x6C"),
                      asm.mapjump(ctx.maplist.index(BR.FIELD), ax, ay, at_, 0), asm.ret(), no]
        return ops + hb._say(sec, BR.MARLE["no"]) + [end, asm.ret()]
    z = mesh.height(mt, *BR.MARLE_AT)
    TV.add_npc(ctx, BR.BASE, "marle", model, (*BR.MARLE_AT, round(z), mt), BR.MARLE_DIR, talk)


def apply(ctx):
    mv, hb, dt = _mods()
    _marle(ctx)                                                          # (before the copy: from the original)
    ctx.field(BR.FIELD)
    f = ctx._fields[BR.FIELD] = FieldFile(ctx._orig_raw[BR.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    _retile(f)
    sec = Script.parse(f.sections[0])
    old = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    keep = [sec.script_ops(old.index(n), 0) for n in KEEP]
    pin = sec.script_ops(old.index("pinball"), 0)
    assert pin[0].op == 0xA1 and all(o.op != 0xA1 for ops in keep for o in ops)
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    def spot(x, y):
        """(x, y, z, tri): on the floor; the stools aren't walkmesh: the nearest floor triangle, z 0 (the floor's)."""
        t = mesh.find(x, y)
        return (x, y, round(mesh.height(t, x, y)), t) if t is not None else (x, y, 0, mv._nearest_tri(mesh, x, y))
    seats = [spot(*s) for s in BR.SEATS]                                # (window placement: the stools)
    stand = [spot(BR.STAND_X, s[1]) for s in BR.SEATS]                  # a patron sits from / stands up here
    beside = [spot(BR.STAND_X, s[1] + BR.BESIDE) for s in BR.SEATS]     # Cloud, up the aisle beside him
    post, door, tifa_at, aisle = spot(*BR.CLOUD_POST), spot(*BR.DOOR), spot(*BR.TIFA_AT), spot(*BR.AISLE)
    # (user: Cloud got stuck walking along the bar into a corner: MOVE follows the walkmesh's pieces) the walks
    # step XYZI along waypoints: Cloud post -> the aisle -> beside the patron; then both -> the aisle -> the door;
    # Cloud back to his post. Every leg is all floor (asserted)
    door_side = spot(*BR.DOOR_SIDE)
    path_in = lambda s: [post, aisle, beside[s]]
    path_cust = lambda s: [stand[s], aisle, door]
    path_out = lambda s: [beside[s], aisle, door_side]                  # (then, the patron gone, back to the post)
    path_back = [door_side, post]
    for s in range(3):
        for path in (path_in(s), path_cust(s), path_out(s), path_back):
            for a, b in zip(path, path[1:]):
                assert _walkable(mesh, a, b), (s, a, b)
    player = spot(*BR.ARRIVE)
    # models: 0 the hidden player, 1 the pinball machine, 2 Tifa, 3 Cloud (security), 4.. the customers
    loader = ModelLoader(f.section("models"))
    names_m = [ModelLoader.name(m) for m in loader.models]
    cl0 = loader.models[0]
    ti0 = next(m for m in loader.models if ModelLoader.hrc(m) == "AAGB.HRC")
    pb = loader.models[pin[0].raw[1]]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC" and names_m[pin[0].raw[1]].endswith("pinbl.char")
    c_anims, t_anims = ModelLoader.anims(cl0), ModelLoader.anims(ti0)
    assert SIT in c_anims and MAKE in t_anims and SERVE in t_anims
    tifa_list = t_anims[:1] + [MAKE, SERVE]
    models = [ModelLoader.only_anims(cl0, c_anims[:1]), pb, ModelLoader.only_anims(ti0, tifa_list),
              ModelLoader.only_anims(cl0, c_anims[:2])]
    for k, (fld, i) in enumerate(CUSTOMERS):
        src = ModelLoader(ctx.field(fld).section("models")) if fld != BR.BASE else loader
        j = loader.add_from(src, i) if fld != BR.BASE else i
        e = loader.models[j]
        if fld != BR.BASE:
            loader.models.pop(j)
        own = ModelLoader.anims(e)
        sway = _sway(ctx, ModelLoader.hrc(e), own[0].split(".")[0].lower() + ".a", "XB%dS" % k)
        models.append(ModelLoader.only_anims(e, own[:2] + [SIT, sway]))
    loader.models = models
    assert len(loader.models) == 4 + len(CUSTOMERS) <= 16
    # windows: over each stool (the view centred on the hidden player, clamped to the scroll range)
    left, top, right, bottom = screen_range(f.section("triggers"))
    vx, vy = cam.project(*player[:3])
    vx, vy = min(max(vx, left + 160), right - 160), min(max(vy, top + 120), bottom - 120)

    # each customer's window just right of his head, stacked top to bottom at least WIN_GAP apart, below the
    # status window
    heads = [cam.project(p[0], p[1], BR.HEAD_Z) for p in seats]     # (the windows over the stools)
    order_ = sorted(range(3), key=lambda k: heads[k][1])
    wy = {}
    y_ = BR.WIN_TOP - BR.WIN_GAP
    for k in order_:
        y_ = max(round(120 + heads[k][1] - vy) - 12, y_ + BR.WIN_GAP)
        wy[k] = y_

    def box(text, s):
        plain = text.replace("{PURPLE}", "").replace("{WHITE}", "")
        w, h = len(plain) * 7 + 22, 25
        x = round(160 + heads[s][0] - vx) + BR.WIN_RIGHT
        return min(max(x, 4), 316 - w), min(wy[s], 236 - h), w, h
    # entities
    cents = ["c%d%s" % (s, "ab"[c]) for s in range(3) for c in range(2)]
    keys = ["k_%d" % k for k in range(5)]
    names = ["dir"] + list(KEEP) + ["cloud", "pinball", "tifa", "sec"] + cents + ["seat%d" % s for s in range(3)] + \
        ["win%d" % s for s in range(3)] + ["status", "clock"] + keys
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch_ = mv._chain
    at = lambda p, d: [xyzi(*p[:4]), d_(d)]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))
    to = lambda a, b: dt._dir_to(b[0] - a[0], b[1] - a[1])
    scripts = {E[n]: {0: ops} for n, ops in zip(KEEP, keep)}
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at(player, 0) + [hb._visi(0)] + hide() +
                           [asm.ret(), asm.ret()]}
    scripts[E["pinball"]] = {0: [Op(bytes([0xA1, 1]))] + pin[1:]}
    scripts[E["tifa"]] = {
        0: [Op(bytes([0xA1, 2]))] + at(tifa_at, BR.TIFA_DIR) + [hb._visi(1)] + hide() + loop_(0) + [asm.ret(), asm.ret()],
        3: [d_(BR.MAKE_DIR), sound(SHAKE_SOUND)] + loop_(1) + [asm.ret()],
        4: [mv._animb(), d_(BR.TIFA_DIR), Op(bytes([0xA2, 0, 1])), sound(SERVE_SOUND), Op(bytes([0xA3, 2, 1])), asm.ret()]}
    # Cloud: 2+s escorts seat s's rowdy customer out (the customer by CUR)
    sec_s = {0: [Op(bytes([0xA1, 3]))] + at(post, BR.CLOUD_DIR) + [hb._visi(1)] + hide() + loop_(0) +
             [asm.ret(), asm.ret()]}
    walk = lambda path, w: _walk(hb, mv._animb, path, *w, 1, 0, to, BR.WALK_STEP)
    for s in range(3):
        ce = [E["c%d%s" % (s, "ab"[c])] for c in range(2)]
        # (user: the rowdy one walked too close to Cloud) Cloud leads, the patron follows FOLLOW frames later;
        # Cloud waits beside the door until he has gone out, then walks back to his post
        sec_s[2 + s] = walk(path_in(s), CW) + [d_(to(beside[s], stand[s])), hb._w(10)] + \
            ch_(CUR[s], [[req(e, 5)] for e in ce]) + walk(path_out(s), CW) + \
            [d_(to(door_side, door)), hb._w(BR.FOLLOW + 50)] + walk(path_back, CW) + [d_(BR.CLOUD_DIR), asm.ret()]
    scripts[E["sec"]] = sec_s
    for s in range(3):
        for c in range(2):
            m = 4 + 2 * s + c
            scripts[E["c%d%s" % (s, "ab"[c])]] = {
                0: [Op(bytes([0xA1, m])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                # (user: patrons stepped and snapped back: CXDC is the step up onto the stool, as the game seats
                # Cloud: from the aisle facing the counter, once, then held sitting)
                2: at(stand[s], BR.SEAT_DIR) + [hb._visi(1), mv._animb(), Op(bytes([0xBC, 2, 0, SIT_LAST, 1])),
                                                asm.ret()],
                3: at(stand[s], to(stand[s], post)) + loop_(3) + [hb._visi(1), asm.ret()],
                4: [hb._visi(0), asm.ret()],
                5: [hb._w(BR.FOLLOW)] + walk(path_cust(s), UW) + [hb._visi(0), asm.ret()]}
    # the windows: winS slot 2+k drink k, 6+k drink k urgent, 10 / 11 rowdy (drunk / angry); status 2+k busy, 6 escort
    texts = {}
    for k, (name, _, _, label, _, _) in enumerate(BR.DRINKS):
        texts[2 + k] = "%s {PURPLE}%s{WHITE}" % (name, label)
        texts[6 + k] = "%s {PURPLE}%s{WHITE} !!" % (name, label)
    for r, word in enumerate(BR.ROWDY):
        texts[10 + r] = "%s {PURPLE}%s{WHITE} Cloud" % (word, BR.ESCORT_KEY[1])
    for s in range(3):
        win = {0: [asm.ret(), asm.ret()]}
        for slot, t in texts.items():
            x, y, w, h = box(t, s)
            win[slot] = [Op(bytes([0x52, s, 0, 1])), Op(bytes([0x50, s]) + struct.pack("<HHHH", x, y, w, h)),
                         asm.message(s, mv._text_id(sec, t)), asm.ret()]
        scripts[E["win%d" % s]] = win
    st = {0: [asm.ret(), asm.ret()]}
    busy = [BR.BUSY % d[1] for d in BR.DRINKS] + [BR.ESCORTING]
    for j, t in enumerate(busy):
        w = len(t) * 7 + 22
        st[2 + j] = [Op(bytes([0x52, 3, 0, 1])), Op(bytes([0x50, 3]) + struct.pack("<HHHH", (320 - w) // 2, 8, w, 25)),
                     asm.message(3, mv._text_id(sec, t)), asm.ret()]
    scripts[E["status"]] = st
    # the clock: frames since the doors opened; END at SHIFT_FRAMES
    ctop, cend = hb._w(1), asm.nop()
    scripts[E["clock"]] = {0: [asm.ret(), asm.setword(T, 0), ctop, Op(bytes([0x96, T[0], T[1]])),
                               asm.if_word(T, ">=", BR.SHIFT_FRAMES, cend), asm.setbyte(END, 1), asm.ret(), cend,
                               asm.goto_back(ctop), asm.ret()]}
    # the buttons: one small entity each; a press = up -> down (PR = 1..4 drinks, 5 escort)
    masks = [d[2] for d in BR.DRINKS] + [BR.ESCORT_KEY[0]]
    for k, mask in enumerate(masks):
        top_, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[keys[k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top_,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held), asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), held,
                asm.goto_back(top_), up, asm.setbyte(PRV[k], 0), asm.goto_back(top_), asm.ret()]}

    # the stools
    for s in range(3):
        ce = [E["c%d%s" % (s, "ab"[c])] for c in range(2)]
        cust = lambda slot: ch_(CUR[s], [[req(e, slot)] for e in ce])
        wn = E["win%d" % s]
        close = Op(bytes([0x54, s]))
        start, idle, gap, order, rowdy, wait_, notw, timeout, angry, leave_, served = (asm.nop() for _ in range(11))
        g_loop, d_loop, made = hb._w(1), hb._w(1), hb._w(1)
        ops = [asm.ret(), asm.setbyte(ST[s], 0), asm.setbyte(CUR[s], s % 2),
               start, asm.if_byte(GO, "!=", 0, idle), asm.if_byte(END, "==", 0, idle), asm.goto(gap),
               idle, hb._w(15), asm.goto_back(start),
               gap, Op(bytes([0x99, RNS[s][0], RNS[s][1]])),
               Op(bytes([0x8D, RNS[s][0] << 4, RNS[s][1], BR.GAP[1]])),
               asm.setword(CNTS[s], BR.GAP[0] + 1), hb._arith(0x86, CNTS[s], RNS[s]),
               g_loop, hb._arith(0x88, CNTS[s], 1), asm.if_word(CNTS[s], "!=", 0, order), asm.goto_back(g_loop),
               order, Op(bytes([0x93, CUR[s][0] << 4, CUR[s][1], 1]))]          # XOR: the other customer
        drink = asm.nop()
        ops += cust(2) + [hb._w(20), Op(bytes([0x99, RNS[s][0], RNS[s][1]])),
                          asm.if_byte(RNS[s], "<", BR.ROWDY_ODDS, drink),
                          asm.setbyte(RS[s], 0), asm.goto(rowdy), drink,
                          Op(bytes([0x99, RNS[s][0], RNS[s][1]])), Op(bytes([0x8D, RNS[s][0] << 4, RNS[s][1], 4])),
                          asm.setbyte(ORD[s], RNS[s]), Op(bytes([0x95, ORD[s][0], ORD[s][1]])),
                          Op(bytes([0x99, RNS[s][0], RNS[s][1]])), asm.setword(PAT[s], 0),
                          hb._arith(0x86, PAT[s], RNS[s])]
        ops += ch_(ORD[s], [[]] + [[hb._arith(0x86, PAT[s], BR.PATIENCE[0] + BR.PATIENCE_BY[k] + 1)]
                                   for k in range(len(BR.DRINKS))])
        ops += [asm.setbyte(ST[s], 1)] + ch_(ORD[s], [[]] + [[req(wn, 2 + k)] for k in range(len(BR.DRINKS))]) + \
            [asm.goto(wait_)]
        ops += [rowdy, asm.setbyte(ORD[s], 5), asm.setword(PAT[s], BR.ROWDY_PATIENCE)] + cust(3) + \
            [asm.setbyte(ST[s], 1), hb._w(2)] + ch_(RS[s], [[req(wn, 10)], [req(wn, 11)]])
        urg = asm.nop()
        ops += [wait_, hb._w(1), asm.if_byte(ST[s], "==", 1, notw), hb._arith(0x88, PAT[s], 1),
                asm.if_word(PAT[s], "==", BR.URGENT, urg), asm.if_byte(ORD[s], "<", 5, urg), close, hb._w(1)] + \
            ch_(ORD[s], [[]] + [[req(wn, 6 + k)] for k in range(len(BR.DRINKS))]) + \
            [urg, asm.if_word(PAT[s], "!=", 0, timeout), asm.goto_back(wait_)]
        not2, not3, not4 = asm.nop(), asm.nop(), asm.nop()
        ops += [notw, asm.if_byte(ST[s], "==", 2, not2), asm.goto_back(wait_), not2,
                asm.if_byte(ST[s], "==", 3, not3), close, asm.setword(CNTS[s], BR.DRINK_TIME),
                made, hb._arith(0x88, CNTS[s], 1), asm.if_word(CNTS[s], "!=", 0, leave_), asm.goto_back(made),
                not3, asm.if_byte(ST[s], "==", 4, not4), close, asm.setbyte(ST[s], 0), asm.goto_back(start),
                not4, close, asm.goto(leave_)]
        ops += [timeout, close, asm.if_byte(ORD[s], "==", 5, angry), asm.setbyte(TRASH, 1), asm.goto(leave_), angry,
                Op(bytes([0x99, RNS[s][0], RNS[s][1]])), asm.if_byte(RNS[s], "<", BR.ANGRY_ODDS, served),
                asm.setbyte(RS[s], 1), asm.goto_back(rowdy), served, Op(bytes([0x95, NMISS[0], NMISS[1]]))]
        ops += [leave_] + cust(4) + [asm.setbyte(ST[s], 0), asm.goto_back(start), asm.ret()]
        scripts[E["seat%d" % s]] = {0: ops}

    # the director
    say = lambda t: hb._say(sec, t)
    lines = lambda ts: sum((say(t) for t in ts), [])
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    main = [hb._uc(1), hb._menu(1), asm.setword(GIL, 0), asm.setbyte(GO, 0), asm.setbyte(END, 0),
            asm.setbyte(TRASH, 0), asm.setbyte(NSERVED, 0), asm.setbyte(NMISS, 0), hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, BR.MUSIC]) + bytes(8))]
    main += lines(BR.INTRO) + say(BR.HOW) + [hb._w(BR.LEAD_IN), asm.setbyte(PR, 0), asm.setbyte(GO, 1),
                                             req(E["clock"], 2)]
    scripts[E["clock"]][2] = scripts[E["clock"]].pop(0)[1:]             # (the clock starts with the doors)
    scripts[E["clock"]][0] = [asm.ret(), asm.ret()]
    loop, trash_done, press, finish = hb._w(1), asm.nop(), asm.nop(), asm.nop()
    main += [loop, asm.if_byte(TRASH, "!=", 0, trash_done), asm.setbyte(TRASH, 0), sound(CRASH_SOUND)]
    for s in range(3):
        nw = asm.nop()
        main += [asm.if_byte(ST[s], "==", 1, nw), asm.setbyte(ST[s], 5), nw]
    rich = asm.nop()
    main += [asm.if_word(GIL, "<", BR.TRASH_COST, rich), asm.setword(GIL, BR.TRASH_COST), rich,
             hb._arith(0x88, GIL, BR.TRASH_COST)]
    tw = len(BR.TRASHED.split("\n")[0]) * 7 + 22
    main += [Op(bytes([0x52, 3, 0, 1])), Op(bytes([0x50, 3]) + struct.pack("<HHHH", (320 - tw) // 2, 8, tw, 41))]
    trash_id = mv._text_id(sec, BR.TRASHED)
    main += [req(E["status"], 9), hb._w(90), Op(b"\x54\x03"), trash_done]
    scripts[E["status"]][9] = [asm.message(3, trash_id), asm.ret()]
    # the end: END set and every stool empty
    open_ = asm.nop()
    main += [asm.if_byte(END, "!=", 0, open_)]
    for s in range(3):
        main += [asm.if_byte(ST[s], "==", 0, open_)]
    main += [asm.goto(finish), open_, asm.if_byte(PR, "==", 0, press), asm.goto_back(loop), press,
             asm.setbyte(K, PR), asm.setbyte(PR, 0)]
    # escort
    drink_, none_ = asm.nop(), asm.nop()
    main += [asm.if_byte(K, "==", 5, drink_)]
    for s in range(3):
        nxt = asm.nop()
        main += [asm.if_byte(ST[s], "==", 1, nxt), asm.if_byte(ORD[s], "==", 5, nxt), asm.setbyte(ST[s], 2),
                 req(E["status"], 2 + len(BR.DRINKS)), hb._req(E["sec"], 2 + s), Op(b"\x54\x03"),
                 asm.setbyte(ST[s], 4), asm.setbyte(PR, 0), asm.goto_back(loop), nxt]
    main += [asm.goto(none_)]
    # a drink: the waiting customer with the least patience who ordered it
    main += [drink_, asm.setbyte(SEL, 255), asm.setword(BEST, 0xFFFF)]
    for s in range(3):
        nxt = asm.nop()
        main += [asm.if_byte(ST[s], "==", 1, nxt), asm.if_byte(ORD[s], "==", K, nxt),
                 asm.if_word(PAT[s], "<", BEST, nxt), asm.setword(BEST, PAT[s]), asm.setbyte(SEL, s), nxt]
    main += [asm.if_byte(SEL, "!=", 255, none_)]
    main += ch_(SEL, [[asm.setbyte(ST[s], 2)] for s in range(3)])
    main += [req(E["tifa"], 3)] + ch_(K, [[]] + [[req(E["status"], 1 + k), asm.setword(MK, d[4])]
                                                  for k, d in enumerate(BR.DRINKS, 1)])
    mk, mdone, quiet = hb._w(1), asm.nop(), asm.nop()
    main += [mk, hb._arith(0x88, MK, 1), asm.if_byte(PR, "!=", 0, quiet), asm.setbyte(PR, 0), buzz, quiet,
             asm.if_word(MK, "!=", 0, mdone), asm.goto_back(mk), mdone,
             Op(b"\x54\x03"), hb._req(E["tifa"], 4)]
    main += ch_(SEL, [[asm.setbyte(ST[s], 3)] for s in range(3)])
    main += ch_(K, [[]] + [[hb._arith(0x86, GIL, d[5])] for d in BR.DRINKS])
    slow = asm.nop()
    main += [asm.if_word(BEST, ">", BR.URGENT, slow), hb._arith(0x86, GIL, BR.QUICK_TIP), slow,
             Op(bytes([0x95, NSERVED[0], NSERVED[1]])), hb._w(4), asm.setbyte(PR, 0), asm.goto_back(loop)]
    main += [none_, buzz, asm.goto_back(loop)]
    # closing time
    good = asm.nop()
    main += [finish, Op(b"\x54\x03")] + say(BR.LAST_ORDERS)
    paid = say(BR.SUMMARY)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))       # MPRA2 after WINDOW
    main += [Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), sound(0x168)] + paid
    main += [asm.if_word(GIL, ">=", BR.GOOD_NIGHT, good)] + say(BR.SUMMARY_LINES["good"])
    bad_end = asm.nop()
    main += [asm.goto(bad_end), good] + say(BR.SUMMARY_LINES["bad"]) + [bad_end]
    # back beside Marle
    bm = Walkmesh(ctx.field(BR.BASE).section("walkmesh"))
    bx, by = BR.MARLE_AT[0] - 40, BR.MARLE_AT[1] - 30
    bt = bm.find(bx, by)
    assert bt is not None
    stop_ = hb._w(30)
    main += fade_out + [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0),
                        asm.mapjump(ctx.maplist.index(BR.BASE), bx, by, bt, to((bx, by), BR.MARLE_AT)),
                        stop_, asm.goto_back(stop_)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  692: 7th Heaven bar shift on %s (stools %s; windows %s; %d texts, script %d bytes)"
          % (BR.FIELD, [p[:3] for p in seats], [box(texts[5], s)[:2] for s in range(3)], n_text,
             len(f.sections[0])))

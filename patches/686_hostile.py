"""(user) Hostile Takeover: the fourth parody film (data `_hostile.py`), in the Shinra 66F boardroom, starring
Cloud (the consultant from "Avalanche Holdings"), Scarlet (the chair) and Elena (the intern who can't stop
kissing up).

Two sets, the room's two camera angles (user: "use both camera angles and alternate for fun"): FIELD_A = a copy
of blin66_6 (the front view down the table), FIELD_B = a copy of blin66_5 (the overhead view); both scripts
blanked, gateways cleared, the same director built into each (`_build`) with every spot and facing mapped by
`_hostile.to_b` (the overhead room is the front room turned a quarter, fitted on the chair squares). Every
ANGLE_EVERY reps the director saves the shoot's state to `STATE` (bank 2 142-155: free in every script and the
exe, `save-usage`), fades and MAPJUMPs to the other set, whose director sees RESUME and carries on. Models:
Cloud (the hidden player), clothed Cloud / Scarlet (blin66_1's AMCC, the movie's donor) / Elena (datiao_6's
EVFE) for the intro, bare Cloud / Scarlet (ZSCA) / Elena (ZELA). No Director model: his lines are text.

The positions (`_hostile_poses`, the user's annotated sketch; every actor at entry scale 768 (1.5x): the
table's top (~70, the chair seats are 44) is then at Cloud's hip, as drawn): one girl on the table on her knees,
chest down (670's dog strokes), her rear at its front-left edge; Cloud on the floor bowing into her, his face
solved onto her entry frame by frame (user: "buried there"), hands on her hips (style 1 flat on the table), his
pelvis turned so his member points down; the other girl reclining on her back under him between his legs (620
`_on_back`, her upper body propped up until her mouth is at his tip's height: bisected per girl), her head
bobbing. P 1 Scarlet on the table / Elena underneath, P 0 the other way round. The gameplay is Going up's (684,
its code copied): prompts by tier, HOLD prompts, Scarlet's [MENU] switch calls, chatter / miss lines, the squat
sound, Cloud's styles; with Elena underneath (P 1) a HOLD lasts until she taps out (late = mad, MAD_LIMIT = she
quits and storms out, an affection point lost). After
TOTAL_REPS the finale, the pay, back to the Director. Checked on offline renders only."""
import importlib
import math
import struct

import _danger as DG
import _director as DR
import _gestures as GS
import _hostile as HT
import _hostile_poses as HP
import _wiggle as WG
from ff7 import asm
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

SCARLET_DONOR, ELENA_DONOR = ("blin66_1", 5), ("datiao_6", 10)     # the movie's (670 MG.GIRLS)
BARE_SCARLET, BARE_ELENA = "ZSCA.HRC", "ZELA.HRC"
DOG = "C"                           # 670's dog position (the girl on the table: on her knees, chest down)
D0 = 0x40                           # (blin66_6) everyone faces +x: the table
WALK_STEP = 2.6
WALK_FAST = 1.5                     # (user: Cloud's intro walk way too slow; since: he slid without animating, 15 frames
                                    # at 3x) steps of 1.5 x WALK_STEP: a walk at this set's 1.5x scale, walk anim speed 1,
                                    # from further back (`_hostile.INTRO` cloud_from)
TABLE_TILES = (160,)                # blin66_6: the table's draw id (it covered everyone at its front-left corner)
TABLE_TILES_B = (160, 208)          # blin66_5 (overhead): the table's draw ids over the actors (128 = the grating)
BG_STATES = ((1, 0), (2, 0))        # blin66_6's init: the chairs (param 1) and desk (2) states on (user: tiles missing)

TIER, STREAK, KEY, PR, P, SEEN, RND, KP, HOLD, HELD, SINCE, NEXTSW, MOVING = ((5, a) for a in range(100, 113))
CNT, PAY, REPS, PER, GIL, CX, CY = ((6, a) for a in range(114, 128, 2))
PRV = [(5, 130 + k) for k in range(4)]
WN = (5, 134)                        # a walk's frame count
TALKING, LN, CHAT, STYLE, SC, ANGER, HC, CUE, CL = ((5, a) for a in range(135, 144))
AC = (5, 144)                        # reps since the camera switched
METER, SIDE, DEC = (5, 146), (5, 147), (5, 148)     # (user) the danger meter (`_danger`)
# the state carried across the camera switch (bank 2: nibble 3 bytes, 4 words)
RESUME = (3, 142)
SAVED = [(TIER, (3, 143)), (P, (3, 144)), (STYLE, (3, 145)), (ANGER, (3, 146)), (SEEN, (3, 147)), (SINCE, (3, 148)),
         (NEXTSW, (3, 149)), (SC, (3, 154)), (STREAK, (3, 155)), (METER, (3, 156))]
SAVED_W = [(PAY, (4, 150)), (REPS, (4, 152))]


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _poses(ctx):
    """Every pose and spot (blin66_6 coordinates; `_build` maps them for the overhead set). P 1: Scarlet on the
    table, Elena underneath; P 0: the other way round. Returns a dict."""
    mv, hb, dt = _mods()
    TP = importlib.import_module("_tickets_poses")
    U = HP.unit()
    k_ = U / mv.UNIT
    off = lambda m, d: [c * k_ for c in mv._off(m, d)]

    def inv(v, d):
        a = d * 2 * math.pi / 256
        F0, F1 = math.sin(a), -math.cos(a)
        return [(-F1 * v[0] + F0 * v[1]) / U, -v[2] / U, (-F1 * v[1] - F0 * v[0]) / U]
    field = lambda spot, d, m: [spot[q] + off(m, d)[q] for q in range(3)]
    mean = lambda ps, q: sum(p_[q] for p_ in ps) / len(ps)
    girls = {"s": (BARE_SCARLET, "anae.a", "ZQ"), "e": (BARE_ELENA, "acfe.a", "ZY")}
    out = {"under": {}, "prop": {}}
    face0 = HP.face_point(ctx)
    for pn, top, low in ((1, "s", "e"), (0, "e", "s")):
        hrc, stand, pre = girls[top]
        ent = [TP.entry_points(ctx, hrc, stand, "%s%s%d" % (pre, DOG, sp)) for sp in range(4)]
        o = [off(e_, D0) for e_ in ent[0]]
        tspot = (round(HT.TABLE_X + HT.ENTRY_OUT - mean(o, 0)), round(HT.SPOT_Y - mean(o, 1)), HT.TABLE_Z)
        Js = [TP.joints(ctx, hrc, "%s%s%d" % (pre, DOG, sp)) for sp in range(4)]
        # his face's targets: her entry, FACE_IN into her (+x: she faces the table, her rear to him)
        faces = [[[q + (HP.FACE_IN * U if i == 0 else 0) for i, q in enumerate(field(tspot, D0, e_))] for e_ in ent[sp]]
                 for sp in range(4)]
        allf = [f_ for fs in faces for f_ in fs]
        fo = off(face0, D0)
        cspot = (round(mean(allf, 0) - fo[0]), round(mean(allf, 1) - fo[1]), 0)
        to_m = lambda v, cs=cspot: inv([v[q] - cs[q] for q in range(3)], D0)
        hips = lambda J, ts=tspot, tm=to_m: tuple(tm(field(ts, D0, [J[b + "_femur@"][0] + sg * 0.3, J[b + "_femur@"][1] - 0.8,
                                                                     J[b + "_femur@"][2]])) for b, sg in (("l", 1), ("r", -1)))
        tabletop = -HT.TABLE_Z / U
        edge_z = to_m([HT.TABLE_X, 0, 0])[2]
        flat = ((HP.HANDS_OUT, tabletop, edge_z - 1.5), (-HP.HANDS_OUT, tabletop, edge_z - 1.5))
        names, tips_all, drops = {}, None, []
        for style in (0, 1):
            letter = "ABCD"[(1 - pn) * 2 + style]
            names[style] = []
            for sp in range(4):
                nm = "QH%s%d" % (letter, sp)
                hands = [hips(J) for J in Js[sp]] if style == 0 else [flat] * len(Js[sp])
                tips, dr = HP.cloud(ctx, nm, [to_m(f_) for f_ in faces[sp]], hands)
                drops += dr
                names[style].append(nm + ".tor")
                if style == 0 and sp == 0:
                    tips_all = tips
            if style == 0:
                k8 = round(7 / 15 * len(faces[0]))
                nm8 = "QH%s8" % letter
                HP.cloud(ctx, nm8, [to_m(faces[0][k8])], [hips(Js[0][k8])])
                names["hold"] = nm8 + ".tor"
        # the girl underneath (user's sketch: reclining on her back between his legs, head towards the table): her
        # upper body propped up until her mouth is at his member's tip's height (bisected), then placed under it
        lhrc, lst = girls[low][0], girls[low][1]
        pre_u = {"e": "QR", "s": "QS"}[low]
        tips_f = [[cspot[q] + off(t, D0)[q] for q in range(3)] for t in tips_all]
        tip_z = mean(tips_f, 2)

        def mouth_at(prop):
            nm = mv._retarget(ctx, HP.under(ctx, prop, probe=True), pre_u, lhrc, lst)[0]
            return HP.mouth(ctx, lhrc, lst, TP.joints(ctx, lhrc, nm.split(".")[0])[0])
        lo, hi = 0.0, 85.0
        for _ in range(14):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if -mouth_at(mid)[1] * U < tip_z else (lo, mid)
        prop = (lo + hi) / 2
        out["prop"][low] = round(prop, 1)
        out["under"][low] = mv._retarget(ctx, HP.under(ctx, prop), pre_u, lhrc, lst)   # 0-3, 8, 7
        Ju = TP.joints(ctx, lhrc, out["under"][low][4].split(".")[0])[0]
        dlow = max(range(256), key=lambda d: off([Ju["head@"][q] - Ju["hip@"][q] for q in range(3)], d)[0])
        mo = HP.mouth(ctx, lhrc, lst, Ju)
        mo_f = off(mo, dlow)
        uspot = (round(mean(tips_f, 0) - mo_f[0]), round(mean(tips_f, 1) - mo_f[1]), 0)
        out[pn] = dict(table=tspot, cloud=cspot, under=uspot, dlow=dlow, names=names, low=low, top=top,
                       drops=(round(min(drops), 2), round(max(drops), 2)), tip_z=round(mean(tips_f, 2)),
                       mouth_z=round(mo_f[2]))
    return out


def apply(ctx):
    PZ = _poses(ctx)
    # (user) the Director to the right of the action (the front view; the overhead set maps the same spot)
    ctx.field(HT.BASE_A)
    fa_ = FieldFile(ctx._orig_raw[HT.BASE_A])
    h = 93 * HP.SCALE / 512
    keep = [(x, y, z + dz) for p in (0, 1) for key in ("cloud", "table", "under")
            for (x, y, z) in [PZ[p][key]] for dz in (0, h)]
    sx, sy, sz, _ = DR.spot(fa_, keep, side=1, height=h)
    cx, cy = PZ[1]["cloud"][:2]
    PZ["director"] = ((sx, sy, sz), DR.facing(sx, sy, cx, cy))
    texts = []
    for field, base, b in ((HT.FIELD_A, HT.BASE_A, False), (HT.FIELD_B, HT.BASE_B, True)):
        texts.append(_build(ctx, field, base, b, PZ))
    print("  686: Hostile Takeover on %s / %s (P 1 %s, P 0 %s; Director %s; props %s; texts %s, scripts %s bytes)" % (
          HT.FIELD_A, HT.FIELD_B, {k: v for k, v in PZ[1].items() if k != "names"},
          {k: v for k, v in PZ[0].items() if k != "names"}, PZ["director"], PZ["prop"],
          [t for t, _ in texts], [s for _, s in texts]))


def _build(ctx, field, base, overhead, PZ):
    mv, hb, dt = _mods()
    ctx.field(field)
    ctx.field(base)
    f = ctx._fields[field] = FieldFile(ctx._orig_raw[base])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    # (user: the table covered Scarlet and Cloud; since: in the vent view too, "the girl on the table is hidden
    # under the table, as is Cloud's head") its tiles behind; the vent's grating (128) stays in front
    dt.tiles_behind(f, lambda i: i in (TABLE_TILES_B if overhead else TABLE_TILES), 4090, 4094)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    from ff7.walkmesh import Walkmesh
    mesh = Walkmesh(f.section("walkmesh"))
    # blin66_6 spots -> this set's
    xf = (lambda x, y, z=0: tuple(round(c) for c in HT.to_b(x, y, z))) if overhead else (lambda x, y, z=0: (x, y, z))
    dd = lambda d: (d + (HT.B_DIR if overhead else 0)) % 256

    def tri(x, y):
        t = mesh.find(round(x), round(y))
        assert t is not None, ("off the walkmesh", field, x, y)
        return t
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, dd(d)])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch_ = mv._chain
    face = lambda x, y, tx, ty: dt._dir_to(tx - x, ty - y)

    def near(x, y):
        """The walkmesh triangle under (x, y), else the nearest one (the table isn't walkmesh: a girl on it is
        placed by her XYZI's height, her triangle the floor's beside it)."""
        t = mesh.find(round(x), round(y))
        if t is not None:
            return t
        c = lambda i: [sum(v[q] for v in mesh.tris[i]) / 3 for q in range(2)]
        return min(range(len(mesh.tris)), key=lambda i: math.dist(c(i), (x, y)))

    def at(p, d, z=0):
        x, y, zz = xf(p[0], p[1], z)
        return [xyzi(x, y, zz, tri(x, y) if z == 0 else near(x, y)), d_(d)]
    # models: 0 hidden player, 1-3 clothed Cloud / Scarlet / Elena, 4-6 bare Cloud / Scarlet / Elena
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    c_anims = ModelLoader.anims(cl0)
    donors = []
    for fd, i in (SCARLET_DONOR, ELENA_DONOR):
        j = loader.add_from(ModelLoader(ctx.field(fd).section("models")), i)
        donors.append(loader.models.pop(j))
    scar_e, elen_e = donors
    s_anims, e_anims = ModelLoader.anims(scar_e), ModelLoader.anims(elen_e)
    # each actor's anims after its stand: Cloud P 1 styles 0 / 1, P 0 styles 0 / 1, holds P 1 / P 0; each girl
    # her dog strokes (on the table), then her strokes underneath (0-3, 8 held, 7 tapping out)
    p1, p0 = PZ[1]["names"], PZ[0]["names"]
    bare_c = p1[0] + p1[1] + p0[0] + p0[1] + [p1["hold"], p0["hold"]]
    wig = [WG.build(ctx, hb.CLOUD_BARE_HRC, pp[0][0].split(".")[0], "QHW%d" % k)   # (user) after her hold: the
           for k, pp in enumerate((p0, p1))]                                         #  wiggle, from each P's stroke
    bare_c += wig
    bare_s = ["ZQ%s%d.tor" % (DOG, sp) for sp in range(4)] + PZ["under"]["s"]
    bare_e = ["ZY%s%d.tor" % (DOG, sp) for sp in range(4)] + PZ["under"]["e"]
    for nm in bare_c + bare_s + bare_e:
        ctx.char_file(nm.split(".")[0].lower() + ".a")                      # (exists)
    G = HT.INTRO_GESTURES                                               # (user: variety) the intro's gestures
    big = lambda e: ModelLoader.with_scale(e, HP.SCALE * int(ModelLoader.entry_scale(e)) // 512)
    loader.models = [cl0] + [big(m) for m in (
        ModelLoader.only_anims(cl0, c_anims[:2] + GS.anims(ctx, G, "cloud", "cloud")),
        ModelLoader.only_anims(scar_e, s_anims[:2] + GS.anims(ctx, G, "scarlet", "scarlet")),
        ModelLoader.only_anims(elen_e, e_anims[:2] + GS.anims(ctx, G, "elena", "elena")),
        ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "hostile_cloudb.char"), c_anims[:1] + bare_c),
        ModelLoader.only_anims(ModelLoader.with_hrc(scar_e, BARE_SCARLET, "hostile_scarb.char"), s_anims[:1] + bare_s),
        ModelLoader.only_anims(ModelLoader.with_hrc(elen_e, BARE_ELENA, "hostile_elenb.char"), e_anims[:1] + bare_e))]
    dm, dfilm, dstill = DR.add(ctx, loader, HP.SCALE)
    meter = DG.build(ctx, f, loader, "O" if overhead else "N", xf(*HT.FOCUS, 0))     # (user) the danger meter
    assert all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    names = ["produce", "cloud", "cloudA", "scarA", "elenA", "cloudB", "scarB", "elenB", "k_sw", "k_ca", "k_ok",
             "k_mn", "prompt", "talk", "hush", "drctr", "gauge", "cursor"]
    sec.entity_names = [nm.encode("latin-1").ljust(8, b"\0") for nm in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {nm: i for i, nm in enumerate(names)}

    def walk(start, stop, walk_anim, stand_anim, d_end):
        """(Cloud, user: faster) XYZI stepped WALK_FAST x WALK_STEP a frame, the walk anim at double speed."""
        (sx_, sy_), (tx, ty) = xf(*start)[:2], xf(*stop)[:2]
        n = max(1, round(math.dist((sx_, sy_), (tx, ty)) / (WALK_FAST * WALK_STEP)))
        stx, sty = round((tx - sx_) / n), round((ty - sy_) / n)
        top, done = hb._w(1), asm.nop()
        z = xf(0, 0, 0)[2]
        return [Op(bytes([0xB3, 0, dt._dir_to(tx - sx_, ty - sy_)])), asm.setword(CX, sx_ & 0xFFFF),
                asm.setword(CY, sy_ & 0xFFFF), asm.setbyte(WN, 0),
                mv._animb(), Op(bytes([0xA2, walk_anim, 1])), Op(bytes([0xAE, walk_anim, 1])),
                top, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
                Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], z, tri(sx_, sy_))),
                Op(bytes([0x95, WN[0], WN[1]])), asm.if_byte(WN, "<", n, done), asm.goto_back(top), done] + \
            [xyzi(tx, ty, z, tri(tx, ty)),                                  # (on the spot: the steps' rounding drifts)
             Op(bytes([0xB3, 0, dt._dir_to(tx - sx_, ty - sy_)]))] + loop_(stand_anim) + \
            [Op(bytes([0xB4, 0, dd(d_end), 2, 8, 2])), Op(b"\xDE")]        # (user: no snapping) a turn on the spot,
                                                                    # the short way round (rotation 2; 0 = clockwise always)
    scripts = {}
    fx, fy = HT.FOCUS
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0]))] + at((fx, fy), 0) + [hb._visi(0)] +
                           hide() + [asm.ret(), asm.ret()]}
    (dx, dy, dz), ddir = PZ["director"]
    gx, gy, gz = xf(dx, dy, dz)
    scripts[E["drctr"]] = DR.entity(dm, (gx, gy, gz, tri(gx, gy)), dd(ddir), dfilm, dstill, xyzi, mv._animb)
    I = HT.INTRO
    scripts[E["cloudA"]] = {
        0: [Op(bytes([0xA1, 1]))] + at(I["cloud_from"], face(*I["cloud_from"], *I["cloud"])) + [hb._visi(0)] + hide() +
        loop_(0) + [asm.ret(), asm.ret()],
        8: [hb._visi(1)] + walk(I["cloud_from"], I["cloud"], 1, 0, face(*I["cloud"], *I["scarlet"])) + [asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    def shown_unless_resumed():
        """VISI 01, or 00 when the shoot resumes after a camera switch (user: the intro's Scarlet and Elena came
        back at their intro spots)."""
        resumed, done = asm.nop(), asm.nop()
        return [asm.if_byte(RESUME, "!=", 1, resumed), hb._visi(1), asm.goto(done), resumed, hb._visi(0), done]
    scripts[E["scarA"]] = {
        0: [Op(bytes([0xA1, 2]))] + at(I["scarlet"], face(*I["scarlet"], *I["elena"])) + shown_unless_resumed() + hide() +
        loop_(0) + [asm.ret(), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    scripts[E["elenA"]] = {
        0: [Op(bytes([0xA1, 3]))] + at(I["elena"], face(*I["elena"], *I["scarlet"])) + shown_unless_resumed() + hide() +
        loop_(0) + [asm.ret(), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    for ent, actor in (("cloudA", "cloud"), ("scarA", "scarlet"), ("elenA", "elena")):
        scripts[E[ent]].update(GS.slots(G, actor, 2, 0, mv._animb()))
    # the scene: slot 2 placed by P (Cloud's stroke by STYLE), the tier's stroke; 4 hidden; 5 the hold; Scarlet 6
    # her slap of the table (her fastest stroke)
    stroke = lambda first: ch_(TIER, [loop_(first + s) for s in range(4)])
    ci, si, ei = (lambda n: 1 + bare_c.index(n)), (lambda n: 1 + bare_s.index(n)), (lambda n: 1 + bare_e.index(n))
    ci, si, ei = (lambda n: 1 + bare_c.index(n)), (lambda n: 1 + bare_s.index(n)), (lambda n: 1 + bare_e.index(n))
    S1, S0 = PZ[1], PZ[0]
    scripts[E["cloudB"]] = {
        0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(P, [at(S0["cloud"], D0) + ch_(STYLE, [stroke(ci(p0[0][0])), stroke(ci(p0[1][0]))]),
                   at(S1["cloud"], D0) + ch_(STYLE, [stroke(ci(p1[0][0])), stroke(ci(p1[1][0]))])]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: ch_(P, [loop_(ci(p0["hold"])), loop_(ci(p1["hold"]))]) + [asm.ret()],
        WG.SLOT: [mv._animb()] + ch_(P, [[Op(bytes([0xA2, ci(pp[0][0]), 1])), Op(bytes([0xA3, ci(wig[k]), 1]))]
                                         for k, pp in enumerate((p0, p1))]) + [asm.ret()]}
    us, ue = PZ["under"]["s"], PZ["under"]["e"]
    scripts[E["scarB"]] = {                                                  # P 1 on the table, P 0 underneath
        0: [Op(bytes([0xA1, 5])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(P, [at(S0["under"], S0["dlow"]) + stroke(si(us[0])),
                   at(S1["table"], D0, HT.TABLE_Z) + stroke(si("ZQ%s0.tor" % DOG))]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()]}
    scripts[E["elenB"]] = {                                                  # P 1 underneath, P 0 on the table
        0: [Op(bytes([0xA1, 6])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(P, [at(S0["table"], D0, HT.TABLE_Z) + stroke(ei("ZY%s0.tor" % DOG)),
                   at(S1["under"], S1["dlow"]) + stroke(ei(ue[0]))]) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ei(ue[4])) + [asm.ret()],                                  # held deep
        6: loop_(ei(ue[5])) + [asm.ret()]}                                  # tapping out
    # the buttons: one small entity each; a press = up -> down (PR = its number), HELD bit k while held
    for k, (mask, _) in enumerate(HT.KEYS + [HT.SWITCH_KEY]):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok", "k_mn"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    # the prompts: window 1 (the director closes it); slots 2-4 the buttons, 5-7 HOLD + the button, 8 [MENU]
    pr = {0: [asm.ret(), asm.ret()]}
    labels = [l for _, l in HT.KEYS] + [HT.HOLD_LABEL + l for _, l in HT.KEYS] + [HT.SWITCH_KEY[1]]
    for j, label in enumerate(labels):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, HT.PROMPT_Y, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    pslot = 2 + len(labels)
    hold_pools = {}
    for key, pool in (("hold", HT.HOLDS), ("cue", HT.CUES), ("good", HT.GOOD), ("early", HT.EARLY), ("mad", HT.MAD)):
        hold_pools[key] = (pslot, len(pool))
        pr[pslot] = [Op(b"\x52\x01\x00\x01")] + ch_(CL, [[hb._window(x, 1, 8, HT.PROMPT_Y), asm.message(1, mv._text_id(sec, x))]
                                                         for x in pool]) + [asm.ret()]
        pslot += 1
    assert pslot <= 32, pslot
    scripts[E["prompt"]] = pr
    # the talk: window 2, groups of lines each shut by hush after SAY
    groups, gid = [], {}
    for part in (0, 1):
        for t, lines in sorted(HT.LINES[part].items()):
            gid[(part, t)] = len(groups)
            groups.append(lines)
    for k, line in enumerate(HT.SWITCH_CALL):
        gid[("switch", k)] = len(groups)
        groups.append([line])
    def show(text):
        return [Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, HT.LINE_Y), hb._req(E["hush"], 2, wait=False),
                asm.message(2, mv._text_id(sec, text))]
    talk = {0: [asm.ret(), asm.ret()]}
    busy_ = lambda ops: [asm.setbyte(TALKING, 1)] + ops + [asm.setbyte(TALKING, 0), asm.ret()]
    for j, lines in enumerate(groups):
        talk[2 + j] = busy_(sum((show(t) for t in lines), []))
    slot = 2 + len(groups)
    style_slot = slot                                                   # (by P, then STYLE)
    talk[slot] = busy_(ch_(P, [ch_(STYLE, [sum((show(t) for t in ls), []) for ls in HT.STYLE_LINES[p]])
                               for p in (0, 1)]))
    slot += 1
    pools = {}
    for key, pool in (("chat0", HT.CHAT[0]), ("chat1", HT.CHAT[1]), ("miss0", HT.MISSES[0]), ("miss1", HT.MISSES[1])):
        pools[key] = (slot, len(pool))
        talk[slot] = busy_(ch_(LN, [show(t) for t in pool]))
        slot += 1
    assert slot <= 32, slot
    scripts[E["talk"]] = talk
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(HT.SAY), Op(b"\x54\x02"), asm.ret()]}
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
    resume_, go_ = asm.nop(), asm.nop()
    main = [hb._uc(1), hb._menu(1), asm.if_byte(RESUME, "!=", 1, resume_)] + \
        [hb._w(20)] + fade_in + [Op(bytes([0xF2, 0, 0, 0, 0x10, HT.MUSIC]) + bytes(8))]
    for i, (line, action) in enumerate(HT.INTRO_LINES):
        main += GS.reqs(G, i, lambda a: E[{"cloud": "cloudA", "scarlet": "scarA", "elena": "elenA"}[a]]) + say(line)
        if action == "walk":                                               # the consultant walks in
            main += [hb._req(E["cloudA"], 8)]
        elif action == "scene":                                            # the position
            main += fade_out + [hb._req(E[a], 4) for a in ("cloudA", "scarA", "elenA")] + \
                [asm.setbyte(P, 1), asm.setbyte(TIER, 0), asm.setbyte(STYLE, 0)] + \
                [hb._req(E[a], 2) for a in ("cloudB", "scarB", "elenB")] + [req(E["drctr"], 2), hb._w(20)] + fade_in
    main += say(HT.HOW)
    MG_ = (E["gauge"], E["cursor"])
    main += DG.start(METER, MG_)
    pay = asm.nop()
    red, red_ops = DG.cut(say, MG_, pay)
    dmiss = lambda: DG.miss(METER, SIDE, RND, E["cursor"], red)
    main += [asm.setbyte(STREAK, 0), asm.setbyte(SEEN, 0x11), asm.setword(PAY, 0), asm.setword(REPS, 0),
             asm.setbyte(SINCE, 0), asm.setbyte(NEXTSW, HT.SWITCH_MIN), asm.setbyte(HELD, 0),
             asm.setbyte(TALKING, 0), asm.setbyte(CHAT, 0), asm.setbyte(SC, 0), asm.setbyte(ANGER, 0),
             asm.setbyte(AC, 0), asm.goto(go_)]
    # (user: both angles) arrived from the other set: the shoot's state back, everyone placed, on from the next rep
    main += [resume_] + [asm.setbyte(v, s) for v, s in SAVED] + [asm.setword(v, s) for v, s in SAVED_W] + \
        [asm.setbyte(RESUME, 0), asm.setbyte(HELD, 0), asm.setbyte(TALKING, 0), asm.setbyte(CHAT, 0), asm.setbyte(AC, 0)] + \
        [hb._req(E[a], 2) for a in ("cloudB", "scarB", "elenB")] + [req(E["drctr"], 2)] + \
        [req(e, 2) for e in MG_] + [hb._w(20)] + fade_in + \
        [Op(bytes([0xF2, 0, 0, 0, 0x10, HT.MUSIC]) + bytes(8)), go_]
    n = len(HT.PERIODS)
    rep, wait, judge, hit, miss, rest, tail, holdw, done_h, sw_rep, normal, after = (asm.nop() for _ in range(12))
    main += [rep] + [req(E[a], 2) for a in ("cloudB", "scarB", "elenB")]
    main += ch_(TIER, [[asm.setword(PER, p)] for p in HT.PERIODS])
    main += [asm.setbyte(PR, 0), asm.setword(CNT, 0), asm.setbyte(HOLD, 0),
             asm.if_byte(SINCE, ">=", NEXTSW, normal), asm.goto(sw_rep), normal]
    # a button rep: KEY at random; from tier 1, now and then a HOLD one
    nohold = asm.nop()
    main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])),
             asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])),
             asm.if_byte(TIER, ">=", 1, nohold), Op(bytes([0x99, RND[0], RND[1]])),
             asm.if_byte(RND, "<", HT.HOLD_ODDS, nohold), asm.setbyte(HOLD, 1), nohold]
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
    main += [hit] + DG.hit(METER, E["cursor"]) + [Op(HT.HIT_SOUND), Op(bytes([0x96, REPS[0], REPS[1]])), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])),
             asm.if_byte(HOLD, "==", 1, once), hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]])), once,
             Op(bytes([0x95, STREAK[0], STREAK[1]])), asm.if_byte(TIER, "<", n - 1, after),
             asm.if_byte(STREAK, ">=", HT.HITS_UP, after), Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)]
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
    main += [Op(bytes([0x95, CHAT[0], CHAT[1]])), asm.if_byte(CHAT, ">=", HT.CHAT_EVERY, quiet), asm.setbyte(CHAT, 0)] + \
        by_p(lambda p: line_from("chat%d" % p)) + [quiet]
    main += [Op(bytes([0x95, SC[0], SC[1]])), asm.if_byte(SC, ">=", HT.STYLE_EVERY, same), asm.setbyte(SC, 0),
             Op(bytes([0x93, STYLE[0] << 4, STYLE[1], 1])),                   # XOR STYLE, 1 (the next rep shows it)
             asm.if_byte(TALKING, "==", 0, same), asm.setbyte(TALKING, 1), asm.setbyte(CHAT, 0),
             req(E["talk"], style_slot), same]
    fin = asm.nop()
    # (user) every ANGLE_EVERY reps: the state saved, over to the other camera angle (its set resumes)
    stay, halt = asm.nop(), hb._w(30)
    other = HT.FIELD_A if overhead else HT.FIELD_B
    ox, oy, _ = HT.to_b(*HT.FOCUS) if not overhead else (*HT.FOCUS, 0)
    ox, oy = round(ox), round(oy)
    otri = Walkmesh(ctx.field(HT.BASE_A if overhead else HT.BASE_B).section("walkmesh")).find(ox, oy)
    assert otri is not None, ("the other set's arrival", ox, oy)
    main += [asm.if_word(REPS, "<", HT.TOTAL_REPS, fin), Op(bytes([0x95, AC[0], AC[1]])),
             asm.if_byte(AC, ">=", HT.ANGLE_EVERY, stay)] + [asm.setbyte(s, v) for v, s in SAVED] + \
        [asm.setword(s, v) for v, s in SAVED_W] + [asm.setbyte(RESUME, 1), Op(b"\x54\x02")] + fast_out + \
        [asm.mapjump(ctx.maplist.index(other), ox, oy, otri, 0), halt, asm.goto_back(halt), stay, asm.goto_back(rep)]
    # a miss: the buzz, a line, back to the slowest pace, the rep's rest, then on
    slow, mtail, mdone = asm.nop(), asm.nop(), asm.nop()
    main += [miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]]))] + dmiss() + [
             asm.setbyte(CHAT, 0)] + by_p(lambda p: line_from("miss%d" % p)) + [slow,
             asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0), mtail, asm.if_word(CNT, "<", PER, mdone),
             hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.goto_back(mtail), mdone, asm.goto_back(tail)]
    # Scarlet's switch call: [MENU] in time = a bonus; either way the two swap places (fast fade)
    sw_wait, sw_judge, sw_miss, sw_go = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    main += [sw_rep] + ch_(P, [[req(E["talk"], 2 + gid[("switch", 0)])], [req(E["talk"], 2 + gid[("switch", 1)])]]) + \
        [hb._req(E["prompt"], 8, wait=False),
         sw_wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, sw_judge),
         asm.if_word(CNT, "<", PER, sw_miss), asm.goto_back(sw_wait),
         sw_judge, asm.if_byte(PR, "==", 4, sw_miss), Op(b"\x54\x01"), hb._arith(0x86, PAY, HT.SWITCH_BONUS),
         asm.goto(sw_go),
         sw_miss, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40]))] + dmiss() + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0),
         sw_go, Op(bytes([0x93, P[0] << 4, P[1], 1])),                               # XOR P, 1
         asm.setbyte(SINCE, 0), Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], HT.SWITCH_RANGE])),
         asm.setbyte(NEXTSW, RND), Op(bytes([0x85, NEXTSW[0] << 4, NEXTSW[1], HT.SWITCH_MIN])),      # PLUS
         ] + fast_out + [req(E[a], 2) for a in ("cloudB", "scarB", "elenB")] + [hb._w(8)] + fast_in + \
        [asm.goto_back(rep)]
    # (user) the hold: Cloud and Elena held deep until she taps out; let go in time = a hit (double pay) plus a
    # bonus; before = a miss; too late = she's mad (MAD_LIMIT: she walks out)
    early, cue, good, late, calm, hw, lw = (asm.nop() for _ in range(7))
    result = [asm.setbyte(HC, 0)] + frames(HC, HT.RESULT_WAIT) + [Op(b"\x54\x01")]
    restart = [req(E[a], 2) for a in ("cloudB", "scarB", "elenB")]
    wiggle = [hb._req(E["cloudB"], WG.SLOT)]                            # (user) he pulls out, wiggles his hips
    walkout = asm.nop()
    main += [head_hold, Op(b"\x54\x01"), req(E["cloudB"], 5), req(E["elenB"], 5)] + prompt_line("hold") + \
        [Op(bytes([0x99, CUE[0], CUE[1]])), Op(bytes([0x8D, CUE[0] << 4, CUE[1], HT.HOLD_RANGE])),
         Op(bytes([0x85, CUE[0] << 4, CUE[1], HT.HOLD_MIN])), asm.setbyte(HC, 0),
         hw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, early), Op(bytes([0x95, HC[0], HC[1]])),
         asm.if_byte(HC, "<", CUE, cue), asm.goto_back(hw),
         cue, Op(b"\x54\x01"), req(E["elenB"], 6)] + prompt_line("cue") + \
        [asm.setbyte(HC, 0), lw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, good), Op(bytes([0x95, HC[0], HC[1]])),
         asm.if_byte(HC, "<", HT.LETGO, late), asm.goto_back(lw)]
    main += [good, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 0xEA, 1, 0x40]))]           # (the materia chime)
    for _ in range(HT.HOLD_BONUS):
        main += [hb._arith(0x86, PAY, TIER), Op(bytes([0x96, PAY[0], PAY[1]]))]
    main += prompt_line("good") + wiggle + restart + result + [asm.goto_back(hit)]
    main += [early, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]]))] + dmiss() + \
        prompt_line("early") + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + wiggle + restart + result + \
        [asm.goto_back(tail)]
    zero, paid_ = asm.nop(), asm.nop()
    main += [late, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 3, 0, 0x40])), Op(bytes([0x96, REPS[0], REPS[1]])),
             Op(bytes([0x95, ANGER[0], ANGER[1]])), asm.if_byte(ANGER, ">=", HT.MAD_LIMIT, calm), asm.goto(walkout), calm] + \
        dmiss() + prompt_line("mad", ANGER) + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + wiggle + restart + \
        [asm.if_word(PAY, "<", HT.MAD_PENALTY, zero), hb._arith(0x88, PAY, HT.MAD_PENALTY), asm.goto(paid_),
         zero, asm.setword(PAY, 0), paid_] + result + [asm.goto_back(tail)]
    # the end: the board approves
    main += [fin, Op(b"\x54\x01"), Op(b"\x54\x02")] + \
        DG.finale(say, METER, PR, 3, CNT, DEC, MG_, PAY, hb._arith) + [hb._w(30)]   # (user) the finisher
    for t in HT.FINALE:
        main += say(t)
    main += [asm.goto(pay)]
    # (user) the intern quit and stormed out: an affection point lost; paid what was earned
    main += red_ops
    main += [walkout, Op(b"\x54\x01"), Op(b"\x54\x02")] + DG.hide(MG_) + mv.lose_affection("elena") + say(HT.WALKOUT[0]) + \
        fade_out + [req(E["elenB"], 4), asm.setbyte(STYLE, 0)] + \
        [req(E[a], 2) for a in ("cloudB", "scarB")] + [hb._w(10)] + fade_in
    for t in HT.WALKOUT[1:]:
        main += say(t)
    main += [pay, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, HT.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(HT.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
    main += paid + fade_out
    rx, ry, rz, rt, rdir = ctx.movie_back
    stop = hb._w(30)
    main += [asm.setbyte(RESUME, 0), asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir),
             stop, asm.goto_back(stop)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    bg_on = [] if overhead else [Op(bytes([0xE0, 0, prm, st])) for prm, st in BG_STATES]
    scripts[0] = {0: [black] + bg_on + [asm.ret()] + main + [asm.ret()]}
    sc_ = DG.scripts(meter, METER, xyzi)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    return n_text, len(f.sections[0])

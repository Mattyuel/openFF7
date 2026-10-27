"""(user) Besties: the fifth film (data `_besties.py`, poses `_besties_poses.py` on the rig `_besties_rig.py`),
Cloud, Tifa and Aerith in the old house at the edge of Icicle Inn, on the bed on the lower floor. Sensual and
sincere, with the Director's script ("The Best Friend's Boyfriend", a cheating soap opera with their own names in
it) running through it scene by scene, experiments that go wrong, and a climax together that the player's
rhythm earns.

The set: FIELD (a debug room) replaced by a copy of snmayor, script blanked, gateways cleared; the room's mid
layer tiles (the bed, the rug's books, the dresser: TILES_BEHIND) moved behind every character (user: tiles
popped through). Models: Cloud (the hidden player), clothed Cloud / Tifa (Corneo's mansion's dress AXJA) /
Aerith (her dress AZBB) for the intro, bare Cloud / Tifa (ZTFA) / Aerith (ZAEA).

The intro (`_besties.INTRO`, actions per line): they come down from the stairs in their dresses, gestures from the
dress models' own anims (Tifa APGC fists at her chest / CXHB hand to her cheek, Aerith DADD hands clasped / DDFA
giggling behind her hand), all three sit on the bed's edge (660 `_ledge`) for the script and the heart-to-heart,
then (fade) undressed, standing. HOW, then the segments (`SEGMENTS`), each placed by SEG and P (actors' slot 2;
(user, round 2) every position rebuilt side-on across the bed's left edge so nobody overlaps, see
`_besties_poses`): 0 edge, 1 ride, 2 lick, 3 share (P = who kneels in front; a HOLD lasts until she taps out;
"my turn" calls), 4 stack (P 0 Cloud in Tifa, 1 in Aerith's mouth; "my turn" calls). Each REPS prompts (fixed
length); between them OFFERS: the real next one or an experiment that goes wrong (the gag, then on). The finale:
FINISH quick prompts; score = hits + 2 x finale hits -> CLIMAX great / good / okay; then AFTER on a black screen,
the pay, back to the Director. Checked on offline renders only."""
import importlib
import math
import struct

import _danger as DG
import _director as DR
import _besties as BS
import _besties_poses as BP
import _wiggle as WG
from ff7 import asm
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

TIFA_DRESS, AERITH_DRESS = ("colne_4", 5), ("colne_4", 6)     # AXJA (ABCD stand, ABCE walk), AZBB (AVBF, AVCA)
BARE_TIFA, BARE_AERITH = "ZTFA.HRC", "ZAEA.HRC"
T_STAND = "abcd.a"                                             # (Aerith's: her donor's first anim, found in apply)
GESTURES = {"t": ["APGC.tor", "CXHB.tor"], "a": ["DADD.chi", "DDFA.chi"]}
WALK_STEP = 2.6
TILES_BEHIND = (100, 4000)      # layer 2 draw ids moved behind the characters (the room's 0-5 are the near
                                # tree / state layers, 4064 the far wall)

SEG, TIER, STREAK, KEY, PR, RND, KP, HOLD, HELD, P, REPN, TALKING, LN, CHAT, HC, CUE, CL, SEEN, ANGER, FH = \
    ((5, a) for a in range(100, 120))
CNT, PER, PAY, HITS, GIL, SCORE, CX, CY = ((6, a) for a in range(120, 136, 2))
PRV = [(5, 136 + k) for k in range(4)]
WN = (5, 140)
METER, SIDE, DEC = (5, 141), (5, 142), (5, 143)     # (user) the danger meter (`_danger`)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _intro_places():
    """The intro's spots: sitting on the bed's left edge (Cloud in the middle), standing on the rug before it."""
    _, _, dt = _mods()
    A, B, C, D = BS.BED
    e0, e1 = (A[0], A[1]), (D[0], D[1])                                    # the left edge, foot to head
    ex, ey = e1[0] - e0[0], e1[1] - e0[1]
    ln = math.hypot(ex, ey)
    out_n = (-ey / ln, ex / ln)
    if out_n[0] > 0:
        out_n = (-out_n[0], -out_n[1])                                     # (out over the rug)
    sit, stand = {}, {}
    for who, t in (("tifa", 0.15), ("cloud", 0.5), ("aerith", 0.85)):
        px, py = e0[0] + ex * t, e0[1] + ey * t
        sit[who] = ((round(px + out_n[0] * BP.SEAT_OUT), round(py + out_n[1] * BP.SEAT_OUT), BS.BED_Z),
                    dt._dir_to(out_n[0], out_n[1]))
    for who, t in (("tifa", 0.3), ("cloud", 0.5), ("aerith", 0.7)):
        px, py = e0[0] + ex * t, e0[1] + ey * t
        stand[who] = ((round(px + out_n[0] * 55), round(py + out_n[1] * 55), 0), dt._dir_to(out_n[0], out_n[1]))
    return {"sit": sit, "stand": stand}


def apply(ctx):
    mv, hb, dt = _mods()
    # anims
    a_donor = ModelLoader(ctx.field(AERITH_DRESS[0]).section("models")).models[AERITH_DRESS[1]]
    t_donor = ModelLoader(ctx.field(TIFA_DRESS[0]).section("models")).models[TIFA_DRESS[1]]
    ae = ModelLoader(ctx.field("bwhlin").section("models")).models[1]                   # (AUFF: her own stand)
    a_stand = ModelLoader.anims(ae)[0].split(".")[0].lower() + ".a"
    PZ = BP.build(ctx, BS.BED, BS.BED_Z)                                               # (user, round 2) every position
    sits = {"tifa": BP.sitting(ctx, "QPT1", "axja.hrc", "abcd.a"),
            "aerith": BP.sitting(ctx, "QPA1", "azbb.hrc", "avbf.a"),
            "cloud": BP.sitting(ctx, "QPC1", "aaaa.hrc", "acfe.a")}
    PL = _intro_places()
    # the set
    ctx.field(BS.FIELD)
    ctx.field(BS.BASE)
    f = ctx._fields[BS.FIELD] = FieldFile(ctx._orig_raw[BS.BASE])
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    # (user: background tiles popping through) the room's mid layer (the bed, the rug's books and bottles, the
    # dresser: draw ids TILES_BEHIND) behind every character, their order kept; the near / far ones stay
    dt.tiles_behind(f, lambda i: TILES_BEHIND[0] <= i < TILES_BEHIND[1], 3960, 4094)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))

    def tri(x, y):
        t = mesh.find(round(x), round(y))
        if t is not None:
            return t
        c = lambda i: [sum(v[q] for v in mesh.tris[i]) / 3 for q in range(2)]
        return min(range(len(mesh.tris)), key=lambda i: math.dist(c(i), (x, y)))
    # models: 0 hidden player, 1-3 clothed Cloud / Tifa / Aerith, 4-6 bare
    loader = ModelLoader(f.section("models"))
    cl0 = loader.models[0]
    assert ModelLoader.hrc(cl0) == "AAAA.HRC"
    c_anims = ModelLoader.anims(cl0)
    donors = []
    for fd, i in (TIFA_DRESS, AERITH_DRESS, ("bwhlin", 3), ("bwhlin", 1)):
        j = loader.add_from(ModelLoader(ctx.field(fd).section("models")), i)
        donors.append(loader.models.pop(j))
    tdress, adress, tbase, abase = donors
    td_anims, ad_anims = ModelLoader.anims(tdress), ModelLoader.anims(adress)
    tw = [td_anims[0], td_anims[1], sits["tifa"]] + GESTURES["t"]
    aw = [ad_anims[0], ad_anims[1], sits["aerith"]] + GESTURES["a"]
    assert all(g_ in td_anims for g_ in GESTURES["t"]) and all(g_ in ad_anims for g_ in GESTURES["a"])
    sp_ = lambda seg, key: PZ[seg][key][0]                                             # its 4 speeds
    bare_c = sum((sp_(seg, k) for seg, k in (("edge", "cloud"), ("ride", "cloud"), ("lick", "cloud"),
                  ("share", "cloud_t"), ("share", "cloud_a"), ("stack", "cloud"), ("stack", "cloud1"))), []) + \
        [PZ["holds"]["cloud_tifa"], PZ["holds"]["cloud_aerith"]]
    wig = [WG.build(ctx, hb.CLOUD_BARE_HRC, PZ["share"][k][0][0].split(".")[0], nm)       # (user) after a hold
           for k, nm in (("cloud_t", "YBW0"), ("cloud_a", "YBW1"))]
    bare_c += wig
    bare_t = sum((sp_(seg, k) for seg, k in (("edge", "tifa"), ("ride", "tifa"), ("ride", "tifa_k"), ("lick", "tifa"),
                  ("share", "tifa_front"), ("share", "tifa_back"), ("stack", "tifa"))), []) + PZ["holds"]["tifa"]
    bare_a = sum((sp_(seg, k) for seg, k in (("edge", "aerith"), ("ride", "aerith"), ("ride", "aerith_k"),
                  ("lick", "aerith"),
                  ("share", "aerith_front"), ("share", "aerith_back"), ("stack", "aerith"), ("stack", "aerith1"))), []) + \
        PZ["holds"]["aerith"]
    for nm in bare_c + bare_t + bare_a:
        ctx.char_file(nm.split(".")[0].lower() + ".a")                                # (exists)
    loader.models = [cl0, ModelLoader.only_anims(cl0, c_anims[:2] + [sits["cloud"]]),
                     ModelLoader.only_anims(tdress, tw), ModelLoader.only_anims(adress, aw),
                     ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC, "besties_cloudb.char"),
                                            c_anims[:1] + bare_c),
                     ModelLoader.only_anims(ModelLoader.with_hrc(tbase, BARE_TIFA, "besties_tifab.char"),
                                            ModelLoader.anims(tbase)[:1] + bare_t),
                     ModelLoader.only_anims(ModelLoader.with_hrc(abase, BARE_AERITH, "besties_aerb.char"),
                                            ModelLoader.anims(abase)[:1] + bare_a)]
    assert all(len(ModelLoader.anims(m)) <= 47 for m in loader.models)
    names = ["produce", "cloud", "cloudA", "tifaA", "aerA", "cloudB", "tifaB", "aerB", "k_sw", "k_ca", "k_ok", "k_mn",
             "prompt", "talk", "hush"]
    dm, dfilm, dstill = DR.add(ctx, loader)                             # (user) the Director, beside the action
    names.append("drctr")
    meter = DG.build(ctx, f, loader, "P", tuple(BS.ARRIVE) + (0,))          # (user) the danger meter
    names += ["gauge", "cursor"]
    sec.entity_names = [nm.encode("latin-1").ljust(8, b"\0") for nm in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {nm: i for i, nm in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda dd: Op(bytes([0xB3, 0, dd % 256])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    once = lambda i, back: [mv._animb(), Op(bytes([0xA2, back, 1])), Op(bytes([0xA3, i, 1]))]   # ANIME1: plays, waits
    ch_ = mv._chain
    at = lambda sp: [xyzi(sp[0][0], sp[0][1], sp[0][2], tri(sp[0][0], sp[0][1])), d_(sp[1])]
    req = lambda ent, slot: Op(bytes([0x01, ent, 0xC0 | slot]))

    def walk(start, stop, walk_anim, stand_anim, d_end, speed=1):
        """XYZI stepped from start to stop with the walk anim, then (user: no snapping) the stand and a turn on the
        spot to d_end (TURNGEN, the short way round; TURNW waits for it)."""
        (sx, sy), (tx, ty) = start, stop
        n = max(1, round(math.dist(start, stop) / (WALK_STEP * speed)))
        stx, sty = round((tx - sx) / n), round((ty - sy) / n)
        top, done = hb._w(1), asm.nop()
        return [d_(dt._dir_to(tx - sx, ty - sy)), asm.setword(CX, sx & 0xFFFF), asm.setword(CY, sy & 0xFFFF),
                asm.setbyte(WN, 0), mv._animb(), Op(bytes([0xA2, walk_anim, speed])), Op(bytes([0xAE, walk_anim, speed])),
                top, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
                Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], 0, tri(sx, sy))),
                Op(bytes([0x95, WN[0], WN[1]])), asm.if_byte(WN, "<", n, done), asm.goto_back(top), done,
                xyzi(sx + n * stx, sy + n * sty, 0, tri(sx + n * stx, sy + n * sty))] + loop_(stand_anim) + [Op(bytes([0xB4, 0, d_end % 256, 2, 8, 2])), Op(b"\xDE")]
    scripts = {}
    fx, fy = BS.ARRIVE
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(fx, fy, 0, tri(fx, fy)), d_(0),
                               hb._visi(0)] + hide() + [asm.ret(), asm.ret()]}
    S = PL["stand"]
    sx_, sy_ = BS.STAIRS_FOOT
    # the intro actors: 8 walk in, 3 sit, 10 / 11 gestures (once, back to the stand), 4 hidden
    scripts[E["cloudA"]] = {0: [Op(bytes([0xA1, 1]))] + at(S["cloud"]) + [hb._visi(1)] + hide() + loop_(0) + [asm.ret(), asm.ret()],
                            3: at(PL["sit"]["cloud"]) + loop_(2) + [asm.ret()],
                            4: [hb._visi(0), asm.ret()]}
    for ent, model, who, k in (("tifaA", 2, "tifa", "t"), ("aerA", 3, "aerith", "a")):
        sc = {0: [Op(bytes([0xA1, model])), xyzi(sx_, sy_, 0, tri(sx_, sy_)), hb._visi(0)] + hide() + loop_(0) + [asm.ret(), asm.ret()],
              8: [hb._visi(1)] + walk(BS.STAIRS_FOOT, S[who][0][:2], 1, 0, S[who][1]) + [asm.ret()],
              3: at(PL["sit"][who]) + loop_(2) + [asm.ret()],
              4: [hb._visi(0), asm.ret()]}
        for j, g_ in enumerate(GESTURES[k]):
            sc[10 + j] = once(3 + j, 0) + [asm.ret()]
        scripts[E[ent]] = sc
    # the scene actors: slot 2 = placed by SEG (and P), the tier's stroke; 3 = standing bare (intro); 4 hidden;
    # 5 / 6 the hold / tapping out (share: the girl in front, P 0 Tifa / 1 Aerith). Each actor's spot per segment
    # (`_besties_poses`: the anims carry the offsets from it); the same stroke length for everyone in a tier.
    stroke = lambda first: ch_(TIER, [loop_(first + s_) for s_ in range(4)])
    ci, ti, ai = (lambda n: 1 + bare_c.index(n)), (lambda n: 1 + bare_t.index(n)), (lambda n: 1 + bare_a.index(n))
    spot = lambda seg, key: (PZ[seg][key][1], PZ[seg][key][2])
    go = lambda seg, key, idx: at(spot(seg, key)) + stroke(idx(PZ[seg][key][0][0]))
    scripts[E["cloudB"]] = {
        0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(SEG, [go("edge", "cloud", ci), go("ride", "cloud", ci), go("lick", "cloud", ci),
                     ch_(P, [go("share", "cloud_t", ci), go("share", "cloud_a", ci)]),
                     ch_(P, [go("stack", "cloud", ci), go("stack", "cloud1", ci)])]) + [hb._visi(1), asm.ret()],
        3: at(S["cloud"]) + loop_(0) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: ch_(P, [loop_(ci(PZ["holds"]["cloud_tifa"])), loop_(ci(PZ["holds"]["cloud_aerith"]))]) + [asm.ret()],
        WG.SLOT: ch_(P, [[mv._animb(), Op(bytes([0xA2, ci(PZ["share"][k][0][0]), 1])), Op(bytes([0xA3, ci(w), 1]))]
                         for k, w in (("cloud_t", wig[0]), ("cloud_a", wig[1]))]) + [asm.ret()]}
    scripts[E["tifaB"]] = {
        0: [Op(bytes([0xA1, 5])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(SEG, [go("edge", "tifa", ti), ch_(P, [go("ride", "tifa", ti), go("ride", "tifa_k", ti)]),
                     go("lick", "tifa", ti),
                     ch_(P, [go("share", "tifa_front", ti), go("share", "tifa_back", ti)]),
                     go("stack", "tifa", ti)]) + [hb._visi(1), asm.ret()],
        3: at(S["tifa"]) + loop_(0) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ti(PZ["holds"]["tifa"][0])) + [asm.ret()],                # held deep
        6: loop_(ti(PZ["holds"]["tifa"][1])) + [asm.ret()],
        WG.SLOT: loop_(ti(PZ["holds"]["tifa"][2])) + [asm.ret()]}             # pulled back (his wiggle)
    scripts[E["aerB"]] = {
        0: [Op(bytes([0xA1, 6])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: ch_(SEG, [go("edge", "aerith", ai), ch_(P, [go("ride", "aerith", ai), go("ride", "aerith_k", ai)]),
                     go("lick", "aerith", ai),
                     ch_(P, [go("share", "aerith_back", ai), go("share", "aerith_front", ai)]),
                     ch_(P, [go("stack", "aerith", ai), go("stack", "aerith1", ai)])]) + [hb._visi(1), asm.ret()],
        3: at(S["aerith"]) + loop_(0) + [hb._visi(1), asm.ret()],
        4: [hb._visi(0), asm.ret()],
        5: loop_(ai(PZ["holds"]["aerith"][0])) + [asm.ret()],
        6: loop_(ai(PZ["holds"]["aerith"][1])) + [asm.ret()],
        WG.SLOT: loop_(ai(PZ["holds"]["aerith"][2])) + [asm.ret()]}             # pulled back (his wiggle)
    # the buttons: a press = up -> down (PR = its number), HELD bit k while held
    for k, (mask, _) in enumerate(BS.KEYS + [BS.SWITCH_KEY]):
        top, up, held = hb._w(1), asm.nop(), asm.nop()
        scripts[E[["k_sw", "k_ca", "k_ok", "k_mn"][k]]] = {
            0: [asm.ret(), asm.setbyte(PRV[k], 0), top,
                Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=up),
                asm.if_byte(PRV[k], "==", 0, held),
                asm.setbyte(PRV[k], 1), asm.setbyte(PR, k + 1), asm.biton(HELD, k), held, asm.goto_back(top),
                up, asm.setbyte(PRV[k], 0), asm.bitoff(HELD, k), asm.goto_back(top), asm.ret()]}
    # the prompt window (1): slots 2-4 buttons, 5-7 HOLD + button, 8 [MENU], then the hold's pools by CL
    pr = {0: [asm.ret(), asm.ret()]}
    labels = [l for _, l in BS.KEYS] + [BS.HOLD_LABEL + l for _, l in BS.KEYS] + [BS.SWITCH_KEY[1]]
    for j, label in enumerate(labels):
        text = "   " + label + "   "
        w = (len(label.replace("{PURPLE}", "").replace("{WHITE}", "")) + 6) * 7 + 24
        pr[2 + j] = [Op(b"\x52\x01\x00\x01"), Op(bytes([0x50, 1]) + struct.pack("<HHHH", (320 - w) // 2, BS.PROMPT_Y, w, 25)),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    pslot = 2 + len(labels)
    hold_pools = {}
    for key, pool in (("hold", BS.HOLDS), ("cue", BS.CUES), ("good", BS.GOOD), ("early", BS.EARLY), ("mad", BS.MAD)):
        hold_pools[key] = (pslot, len(pool))
        pr[pslot] = [Op(b"\x52\x01\x00\x01")] + ch_(CL, [[hb._window(x, 1, 8, BS.PROMPT_Y), asm.message(1, mv._text_id(sec, x))]
                                                         for x in pool]) + [asm.ret()]
        pslot += 1
    scripts[E["prompt"]] = pr
    # the talk (window 2): per segment its chatter / misses (by LN), its tier lines; TALKING while busy
    def show(text):
        return [Op(b"\x52\x02\x00\x01"), hb._window(text, 2, 8, BS.LINE_Y), hb._req(E["hush"], 2, wait=False),
                asm.message(2, mv._text_id(sec, text))]
    busy_ = lambda ops: [asm.setbyte(TALKING, 1)] + ops + [asm.setbyte(TALKING, 0), asm.ret()]
    talk = {0: [asm.ret(), asm.ret()]}
    slot = 2
    pools, tiers = {}, {}
    for kind in ("chat", "miss"):
        pools[kind] = slot
        talk[slot] = busy_(ch_(SEG, [ch_(LN, [show(x) for x in sg[kind]]) for sg in BS.SEGMENTS]))
        slot += 1
    for t in (2, 3):
        tiers[t] = slot
        talk[slot] = busy_(ch_(SEG, [sum((show(x) for x in sg["tiers"].get(t, [])), []) for sg in BS.SEGMENTS]))
        slot += 1
    scripts[E["talk"]] = talk
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(BS.SAY), Op(b"\x54\x02"), asm.ret()]}

    def line_from(kind, size=6):
        busy = asm.nop()
        return [asm.if_byte(TALKING, "==", 0, busy), Op(bytes([0x99, LN[0], LN[1]])),
                Op(bytes([0x8D, LN[0] << 4, LN[1], size])), asm.setbyte(TALKING, 1), req(E["talk"], pools[kind]), busy]

    def prompt_line(key, pick=None):
        sl, size = hold_pools[key]
        ops = [Op(bytes([0x99, CL[0], CL[1]])), Op(bytes([0x8D, CL[0] << 4, CL[1], size]))] if pick is None else \
            [asm.setbyte(CL, pick)]
        return [hb._w(2)] + ops + [req(E["prompt"], sl)]

    def frames(var, limit):
        top, done = asm.nop(), asm.nop()
        return [top, asm.if_byte(var, "<", limit, done), hb._w(1), Op(bytes([0x95, var[0], var[1]])),
                asm.goto_back(top), done]

    say = lambda t: hb._say(sec, t)
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    fast_out, fast_in = [Op(mv.FAST_OUT), Op(b"\x6C")], [Op(mv.FAST_IN), Op(b"\x6C")]
    actors = ("cloudB", "tifaB", "aerB")
    restart = [req(E[a], 2) for a in actors]
    buzz = Op(bytes([0xF1, 0, 3, 0, 0x40]))
    # the intro
    main = [hb._uc(1), hb._menu(1), hb._w(20)] + fade_in + [Op(bytes([0xF2, 0, 0, 0, 0x10, BS.MUSIC]) + bytes(8))]
    for line, action in BS.INTRO:
        main += say(line)
        if action == "walk_in":
            main += [req(E["tifaA"], 8), hb._w(24), hb._req(E["aerA"], 8), hb._w(10)]
        elif isinstance(action, tuple):
            who = "tifaA" if action[0] == "gesture_t" else "aerA"
            k = "t" if who == "tifaA" else "a"
            j = [g_.split(".")[0] for g_ in GESTURES[k]].index(action[1])
            main += [req(E[who], 10 + j)]
        elif action == "sit":
            main += fade_out + [hb._req(E[a], 3) for a in ("cloudA", "tifaA", "aerA")] + [hb._w(10)] + fade_in
        elif action == "bare":
            main += fade_out + [hb._req(E[a], 4) for a in ("cloudA", "tifaA", "aerA")] + \
                [hb._req(E[a], 3) for a in actors] + [hb._w(10)] + fade_in
    main += say(BS.HOW) + [req(E["drctr"], 2), asm.setword(PAY, 0), asm.setword(HITS, 0), asm.setbyte(HELD, 0),
                          asm.setbyte(ANGER, 0)]
    MG_ = (E["gauge"], E["cursor"])
    main += DG.start(METER, MG_)
    pay = asm.nop()
    red, red_ops = DG.cut(say, MG_, pay, fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20)])
    dmiss = lambda: DG.miss(METER, SIDE, RND, E["cursor"], red)
    # the segments
    n = len(BS.PERIODS)
    for s, sg in enumerate(BS.SEGMENTS):
        if s:
            who_line, real, silly, gag = BS.OFFERS[s - 1]
            ask, first = hb._ask(sec, who_line, [real, silly])
            plain = asm.nop()
            main += ask + [asm.if_byte(hb.CHOICE, "==", first + 1, plain)] + fade_out + [hb._w(15)] + fade_in
            for x in gag:
                main += say(x) + ([Op(bytes([0xF1, 0, 0x76, 0, 0x40]))] if x.startswith("(") else [])
            main += [plain]
        main += fade_out + [asm.setbyte(SEG, s), asm.setbyte(P, 0), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0),
                            asm.setbyte(REPN, 0), asm.setbyte(SEEN, 0), asm.setbyte(CHAT, 0), asm.setbyte(TALKING, 0),
                            Op(b"\x54\x02")] + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(4)] + restart + \
            [hb._w(14)] + fade_in
        for x in sg["setup"]:
            main += say(x)
        rep, wait, judge, hit, miss, tail, holdf = (asm.nop() for _ in range(7))
        main += [rep] + ch_(TIER, [[asm.setword(PER, p_)] for p_ in BS.PERIODS])
        main += [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])), asm.setbyte(KEY, RND),
                 asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0), asm.setword(CNT, 0),
                 asm.setbyte(HOLD, 0)]
        if sg["key"] == "share":                                          # a HOLD now and then, until she taps out
            nohold = asm.nop()
            main += [asm.if_byte(TIER, ">=", 1, nohold), Op(bytes([0x99, RND[0], RND[1]])),
                     asm.if_byte(RND, "<", BS.HOLD_ODDS, nohold), asm.setbyte(HOLD, 1), nohold]
        main += ch_(HOLD, [ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)]),
                           ch_(KEY, [[hb._req(E["prompt"], 5 + k, wait=False)] for k in range(3)])])
        main += [wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, judge),
                 asm.if_word(CNT, "<", PER, miss), asm.goto_back(wait),
                 judge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, miss), asm.if_byte(HOLD, "==", 0, holdf)]
        after, rest = asm.nop(), asm.nop()
        main += [hit] + DG.hit(METER, E["cursor"]) + [Op(BS.HIT_SOUND), Op(bytes([0x96, HITS[0], HITS[1]])), hb._arith(0x86, PAY, TIER),
                 Op(bytes([0x96, PAY[0], PAY[1]])), Op(bytes([0x95, STREAK[0], STREAK[1]])),
                 asm.if_byte(TIER, "<", n - 1, after), asm.if_byte(STREAK, ">=", BS.HITS_UP, after),
                 Op(bytes([0x95, TIER[0], TIER[1]])), asm.setbyte(STREAK, 0)] + restart
        for t in (2, 3):
            nx = asm.nop()
            if sg["tiers"].get(t):
                main += [asm.if_byte(TIER, "==", t, nx), asm.if_byte(SEEN, "bit_off", t, nx), asm.biton(SEEN, t),
                         req(E["talk"], tiers[t]), nx]
        main += [after, rest, asm.if_word(CNT, "<", PER, tail), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                 asm.goto_back(rest), tail]
        quiet = asm.nop()
        main += [Op(bytes([0x95, CHAT[0], CHAT[1]])), asm.if_byte(CHAT, ">=", BS.CHAT_EVERY, quiet), asm.setbyte(CHAT, 0)] + \
            line_from("chat") + [quiet, Op(bytes([0x95, REPN[0], REPN[1]]))]
        if s in BS.SWITCH_CALL:                                           # "my turn": [MENU] in time = a bonus
            for at_rep in BS.SWITCH_AT:
                nos, sw_wait, sw_judge, sw_miss, sw_go = (asm.nop() for _ in range(5))
                main += [asm.if_byte(REPN, "==", at_rep, nos), Op(b"\x54\x02"), asm.setbyte(TALKING, 0)]
                call = lambda x: [hb._w(2), Op(b"\x52\x02\x00\x01"), hb._window(x, 2, 8, BS.LINE_Y), req(E["hush"], 2),
                                  asm.message(2, mv._text_id(sec, x))]
                main += ch_(P, [call(BS.SWITCH_CALL[s][0]), call(BS.SWITCH_CALL[s][1])])
                main += [asm.setword(CNT, 0), asm.setbyte(PR, 0), hb._req(E["prompt"], 8, wait=False),
                         sw_wait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, sw_judge),
                         asm.if_word(CNT, "<", PER, sw_miss), asm.goto_back(sw_wait),
                         sw_judge, asm.if_byte(PR, "==", 4, sw_miss), Op(b"\x54\x01"), Op(BS.HIT_SOUND),
                         hb._arith(0x86, PAY, 5), Op(bytes([0x96, HITS[0], HITS[1]])), asm.goto(sw_go),
                         sw_miss, Op(b"\x54\x01"), buzz] + dmiss() + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0),
                         sw_go, Op(bytes([0x93, P[0] << 4, P[1], 1]))] + fast_out + restart + [hb._w(8)] + fast_in + [nos]
        if sg["key"] == "ride":                                           # (user) P = Tifa and Aerith kissing
            for at_rep in BS.KISS_AT:
                nok = asm.nop()
                main += [asm.if_byte(REPN, "==", at_rep, nok), Op(bytes([0x93, P[0] << 4, P[1], 1]))] + fast_out + \
                    restart + [hb._w(8)] + fast_in + [nok]
        done = asm.nop()
        main += [asm.if_byte(REPN, "<", BS.REPS, done), asm.goto_back(rep), done]
        # (the ends of the miss / hold paths come back to tail: emitted here, after the segment's loop)
        segment_end = asm.nop()
        main += [asm.goto(segment_end)]
        slow, mtail, mdone = asm.nop(), asm.nop(), asm.nop()
        main += [miss, Op(b"\x54\x01"), buzz] + dmiss() + line_from("miss", 4) + [asm.setbyte(CHAT, 0),
                 asm.if_byte(TIER, "!=", 0, slow), asm.setbyte(TIER, 0)] + restart + [slow, asm.setbyte(STREAK, 0),
                 mtail, asm.if_word(CNT, "<", PER, mdone), hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])),
                 asm.goto_back(mtail), mdone, asm.goto_back(tail)]
        main += [holdf]
        if sg["key"] == "share":
            early, cue, good, late, hw, lw, calm = (asm.nop() for _ in range(7))
            her = lambda slot_: ch_(P, [[req(E["tifaB"], slot_)], [req(E["aerB"], slot_)]])
            wiggle = her(WG.SLOT) + [hb._req(E["cloudB"], WG.SLOT)]         # (user) he pulls out, wiggles his hips
            result = [asm.setbyte(HC, 0)] + frames(HC, BS.RESULT_WAIT) + [Op(b"\x54\x01")]
            main += [req(E["cloudB"], 5)] + her(5) + prompt_line("hold") + \
                [Op(bytes([0x99, CUE[0], CUE[1]])), Op(bytes([0x8D, CUE[0] << 4, CUE[1], BS.HOLD_RANGE])),
                 Op(bytes([0x85, CUE[0] << 4, CUE[1], BS.HOLD_MIN])), asm.setbyte(HC, 0),
                 hw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, early), Op(bytes([0x95, HC[0], HC[1]])),
                 asm.if_byte(HC, "<", CUE, cue), asm.goto_back(hw),
                 cue, Op(b"\x54\x01")] + her(6) + prompt_line("cue") + \
                [asm.setbyte(HC, 0), lw, hb._w(1), asm.if_byte(HELD, "bit_on", KEY, good), Op(bytes([0x95, HC[0], HC[1]])),
                 asm.if_byte(HC, "<", BS.LETGO, late), asm.goto_back(lw)]
            main += [good, Op(b"\x54\x01"), Op(bytes([0xF1, 0, 0xEA, 1, 0x40])), hb._arith(0x86, PAY, TIER),
                     hb._arith(0x86, PAY, TIER), Op(bytes([0x96, HITS[0], HITS[1]]))] + prompt_line("good") + wiggle + \
                restart + result + [asm.goto_back(hit)]
            main += [early, Op(b"\x54\x01"), buzz] + dmiss() + prompt_line("early") + [asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + \
                wiggle + restart + result + [asm.goto_back(tail)]
            main += [late, Op(b"\x54\x01"), buzz] + dmiss() + ch_(P, [prompt_line("mad", 0), prompt_line("mad", 1)]) + \
                [Op(bytes([0x95, ANGER[0], ANGER[1]])), asm.setbyte(TIER, 0), asm.setbyte(STREAK, 0)] + wiggle + \
                restart + result + [asm.goto_back(tail)]
        else:
            main += [asm.goto_back(hit)]
        main += [segment_end]
    # the finale: FINISH quick prompts at the top pace
    main += [Op(b"\x54\x02"), asm.setbyte(TALKING, 0), asm.setbyte(TIER, n - 1)] + restart + \
        hb._say(sec, BS.FINISH_CALL) + [asm.setbyte(FH, 0), asm.setbyte(REPN, 0)]
    frep, fwait, fjudge, fmiss, fnext = (asm.nop() for _ in range(5))
    main += [frep, asm.setword(PER, BS.PERIODS[-1]), Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], 3])),
             asm.setbyte(KEY, RND), asm.setbyte(KP, KEY), Op(bytes([0x95, KP[0], KP[1]])), asm.setbyte(PR, 0),
             asm.setword(CNT, 0)] + ch_(KEY, [[hb._req(E["prompt"], 2 + k, wait=False)] for k in range(3)]) + \
        [fwait, hb._w(1), Op(bytes([0x96, CNT[0], CNT[1]])), asm.if_byte(PR, "==", 0, fjudge),
         asm.if_word(CNT, "<", PER, fmiss), asm.goto_back(fwait),
         fjudge, Op(b"\x54\x01"), asm.if_byte(PR, "==", KP, fmiss), Op(BS.HIT_SOUND), Op(bytes([0x95, FH[0], FH[1]])),
         asm.goto(fnext), fmiss, Op(b"\x54\x01"), buzz, fnext, hb._w(6), Op(bytes([0x95, REPN[0], REPN[1]])),
         asm.if_byte(REPN, ">=", BS.FINISH, asm.nop())]
    fdone = asm.nop()
    main[-1] = asm.if_byte(REPN, "<", BS.FINISH, fdone)
    main += [asm.goto_back(frep), fdone]
    main += DG.finale(say, METER, PR, 3, CNT, DEC, MG_, PAY, hb._arith)    # (user) the finisher
    # the score: hits + 2 x finale hits -> the climax
    main += [asm.setword(SCORE, HITS), hb._arith(0x86, SCORE, FH), hb._arith(0x86, SCORE, FH)]
    great, good_, okay, cend = (asm.nop() for _ in range(4))
    main += [asm.if_word(SCORE, ">=", BS.SCORE_GREAT, good_)] + sum((say(x) for x in BS.CLIMAX["great"]), []) + [asm.goto(cend), good_,
             asm.if_word(SCORE, ">=", BS.SCORE_GOOD, okay)] + sum((say(x) for x in BS.CLIMAX["good"]), []) + [asm.goto(cend), okay] + \
        sum((say(x) for x in BS.CLIMAX["okay"]), []) + [cend]
    main += fade_out + [hb._req(E[a], 4, wait=False) for a in actors] + [hb._w(20)]
    for x in BS.AFTER:
        main += say(x)
    main += [asm.goto(pay)] + red_ops
    main += [pay, asm.setword(GIL, PAY), hb._arith(0x8A, GIL, BS.PAY_HIT),
             Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), Op(bytes([0xF1, 0, 0x68, 1, 0x40]))]
    paid = say(BS.PAID)
    paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
    main += paid
    rx, ry, rz, rt, rdir = ctx.movie_back
    stop = hb._w(30)
    main += [asm.bitoff((1, 213), 2), hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir),
             stop, asm.goto_back(stop)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    sc_ = DG.scripts(meter, METER, xyzi)
    scripts[E["gauge"]], scripts[E["cursor"]] = sc_["gauge"], sc_["cursor"]
    scripts[E["drctr"]], dspot = DR.place(f, scripts, [E[a] for a in ("cloudA", "tifaA", "aerA", "cloudB", "tifaB", "aerB")], dm, dfilm, dstill, hb._xyzi,
                                          mv._animb)
    print("  687: the Director at", dspot)
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    print("  687: Besties on %s (%d texts, script %d bytes; spots %s)" % (BS.FIELD, n_text, len(f.sections[0]),
          {k: v for k, v in PL.items() if k not in ("side",)}))

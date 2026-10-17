"""(user) The Gold Saucer stage show (data `_stage_show.py`): a live erotic fantasy on the Event Square
stage (astage_b: only the story's play enters it, never reached in the open world: Event Square is
pinned past the play's moment), offered by the Booker in Event Square once a full group shoot is done
(`SPECIAL_ON`) and Cid is at affection 20. Four acts: each a clothed scene in costume (the women's
conflicts, Cloud's call; staged as 670 `_stage`: placed, a beat, a reaction), then a fade and the
undressed minigame (the movie's meter; holding, cowgirl, Blast-off's Twin Jets and Exhaust), a finisher
in the finale. Pay: the house's cut of the tickets, presses x `SHOW_RATE`, on the spot.

Models (the stage's own entities keep their order; their models repurposed): 0 Cloud (the player,
clothed), 1 Aerith clothed, 2 Tifa clothed, 3 Elena clothed (was Yuffie), 4 the King (master of
ceremonies), 5 the Dragon costume (Cid clothed), 6 Scarlet clothed (was the soldier), 7 bare Cloud
(was the wizard), 8 bare Cid (was the narrator); new: 9-12 the bare girls, 13 gauge, 14 cursor."""
import importlib
import math
import struct

import _bare_cid
import _cid as CID
import _movie_girls as MG
import _movie_profiles as PF
import _stage_show as SS
from _config import SPECIAL_ON
from _recruit import sound
from _travel import CHOICE, reuse_npc
from ff7 import asm
from ff7.camera import Camera, facing_screen, screen_range
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

# act, Cloud's call in it, the finale's bride (girl index). (Were 184-186: the same bytes as 670's
# `_take_gil` words GLO / GHI (6, 184) / (6, 186) (banks 5 and 6 are one temp area), so Act One's
# "Follow the script, Tifa." (the only choice that takes gil) overwrote A with the gil's low byte:
# no act matched and the minigame was a blank stage, user)
A, RC, FG = (5, 212), (5, 213), (5, 214)
SIDE, SEG, SW = (5, 164), (5, 165), (6, 168)      # Twin Jets (as 673)
GIL = (6, 210)
SPRITES = {"QGHA": ("QGHB", "QGHC", "QGHD"), "QCHA": ("QCHB", "QCHC", "QCHD")}
SWITCH = 300


def _mods():
    return (importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"),
            importlib.import_module("672_movie_special"), importlib.import_module("660_dates"),
            importlib.import_module("673_blast_off"))


def _show(ctx, built):
    mv, hb, sp, dt, bo = _mods()
    anims, lay = built
    hers = ctx.blast_hers
    K_ = SS.SCALE
    f = ctx.field(SS.SET)
    sec = Script.parse(f.sections[0])
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    assert names[:11] == ["dic", "cloud", "earith", "tifa", "yufi", "king", "dragon", "sol", "wiz", "onna", "oto"], names
    dt._clear_texts(sec)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    loader = ModelLoader(f.section("models"))
    assert [ModelLoader.name(e)[8:] for e in loader.models] == [
        "main_n_cloud.char", "main_n_earith.char", "main_n_tifa.char", "main_yufi.char", "gold_king.char",
        "gold_dragon.char", "gold_soldier.char", "gold_wizard.char", "std_woman7.char"]

    def put(i, entry):                               # a model into slot i, scaled to the stage
        loader.models[i] = ModelLoader.with_scale(entry, loader.scale) if i < len(loader.models) else entry

    def donor(field, i):
        d = ModelLoader(ctx.field(field).section("models"))
        k = loader.add_from(d, i)
        return loader.models.pop(k)
    girl_donor = {g["key"]: g["donor"] for g in MG.GIRLS}
    loader.models[3] = donor(*girl_donor["elena"][:2])
    loader.models[6] = donor(*girl_donor["scarlet"][:2])
    # bare Cloud (model 7): the stage's Cloud with every pose the show plays
    letter = lambda pos: chr(ord("A") + [p["name"] for p in mv.POSITIONS].index(pos))
    pre = {g["key"]: g["prefix"] for g in MG.GIRLS}
    cl_list = ["ZN%s%d.tor" % (letter("holding"), s) for s in range(4)] + \
        ["ZN%s%d.tor" % (letter("cowgirl"), s) for s in range(4)] + anims["cloud"][4:12]     # Twin Jets, Exhaust
    cl0 = loader.models[0]
    loader.models[7] = ModelLoader.with_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), cl_list)
    cfirst = len(ModelLoader.anims(loader.models[7])) - len(cl_list)
    cid_entry = donor("astage_a", 3)
    assert ModelLoader.name(cid_entry).endswith("main_cid.char"), ModelLoader.name(cid_entry)
    cid_list = anims["cid"][4:12]
    loader.models[8] = ModelLoader.with_anims(ModelLoader.with_hrc(cid_entry, _bare_cid.HRC,
                                                                     ModelLoader.name(cid_entry)[:-5] + "_b.char"), cid_list)
    kfirst = len(ModelLoader.anims(loader.models[8])) - len(cid_list)
    # the bare girls (9-12): her movie pose for her act + Blast-off's Twin Jets / Exhaust (with Aerith's turns)
    gm, glist, gfirst = {}, {}, {}
    for k, key in enumerate(SS.GIRLS):
        (dfield, dmodel), bare_hrc, _, _ = sp._girl(ctx, key)
        h = hers[key]
        lst = h[4:12] + h[18:20]                                    # T speeds, U speeds, turns V0 / V1
        if key == "tifa":
            lst += ["%s%s%d.tor" % (pre[key], letter("holding"), s) for s in range(4)]
        if key == "scarlet":
            lst += ["%s%s%d.tor" % (pre[key], letter("cowgirl"), s) for s in range(4)]
        e = donor(dfield, dmodel)
        e = ModelLoader.with_anims(ModelLoader.with_hrc(e, bare_hrc, ModelLoader.name(e)[:-5] + "_b.char"), lst)
        loader.models.append(e)
        gm[key] = len(loader.models) - 1
        glist[key], gfirst[key] = lst, len(ModelLoader.anims(e)) - len(lst)
        assert len(ModelLoader.anims(e)) <= 47, (key, len(ModelLoader.anims(e)))
    for i in (0, 7, 8):
        assert len(ModelLoader.anims(loader.models[i])) <= 47, (i, len(ModelLoader.anims(loader.models[i])))
    gidx = lambda key, name: gfirst[key] + glist[key].index(name)

    # ---- places -----------------------------------------------------------------------------------
    def spot(x, y, z=0):
        x, y = round(x), round(y)
        t = mesh.find(x, y)
        assert t is not None, ("off the stage", x, y)
        return x, y, SS.FLOOR + round(z), t
    toward = lambda a, b: dt._dir_to(b[0] - a[0], b[1] - a[1])
    off = lambda m, d: tuple(v * K_ for v in mv._off(m, d))
    plays = []
    for a in SS.ACTS:
        pl, (x, y) = a["play"], a["play"]["at"]
        c = spot(x, y)
        cd = facing_screen(cam, x, y, SS.FLOOR, (-1, 0))                # Cloud faces screen-left
        p = dict(kind=pl["kind"], girl=pl["girl"], cloud=c, cdir=cd, focus=c, watch=pl["watch"])
        if pl["kind"] == "holding":
            p.update(gspot=c, gdir=(cd + 128) % 256, canims=[cfirst + s for s in range(4)])
        elif pl["kind"] == "cowgirl":
            p.update(gspot=spot(x, y, 14 * K_), gdir=cd, canims=[cfirst + 4 + s for s in range(4)])
        elif pl["kind"] == "twinjets":
            o = off(lay["her"], cd)
            g = spot(x + o[0], y + o[1])
            k_ = spot(2 * g[0] - x, 2 * g[1] - y)
            p.update(gspot=g, gdir=(cd + 128) % 256, gdir2=cd, cid=k_, ciddir=(cd + 128) % 256,
                     canims=[cfirst + 8 + s for s in range(4)], kanims=[kfirst + s for s in range(4)], focus=g)
        else:                                                           # exhaust
            ro = lay["exhaust"]
            o = off(ro, cd)
            p.update(gspot=c, gdir=(cd + 128) % 256, cid=spot(x + o[0], y + o[1]), ciddir=(cd + 128) % 256,
                     canims=[cfirst + 12 + s for s in range(4)], kanims=[kfirst + 4 + s for s in range(4)])
        plays.append(p)
    tj = plays[2]
    assert tj["kind"] == "twinjets"
    face_cam = facing_screen(cam, *tj["gspot"][:3], (0, 1))

    def mid_dir(d, sense):
        from ff7 import fieldanim as fa
        v = fa._vec(fa.axis_angle([0.0, 1.0, 0.0], 90 * sense), [0.0, 0.0, -1.0])
        o = mv._off(v, d)
        return dt._dir_to(o[0], o[1])
    gap = lambda a, b: min((a - b) % 256, (b - a) % 256)
    turn_for = {side: min((0, 1), key=lambda k: gap(mid_dir(d, 1 if k == 0 else -1), face_cam))
                for side, d in ((0, tj["gdir"]), (1, tj["gdir2"]))}

    # gauge / cursor per act (as 673)
    left, top, right, bottom = screen_range(f.section("triggers"))
    near = min(mv._view_depth(cam, v) for t in mesh.tris for v in t) * 0.8
    donor_loader = ModelLoader(ctx.field(mv.mm.DONOR_FIELD).section("models"))
    sprite_scale = round(ModelLoader.entry_scale(donor_loader.models[mv.mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    unit = 3.41 * sprite_scale / 512
    half = mv.GAUGE_PX / 2 * near / cam.zoom / unit
    half_cursor = mv.CURSOR_PX / 2 * near / cam.zoom / unit
    for p in plays:
        sx, sy = cam.project(*p["focus"][:3])
        sx = min(max(sx, left + 160), right - 160)
        sy = min(max(sy, top + 120), bottom - 120)
        gy = sy + mv.GAUGE_Y
        g = mv._unproject(cam, sx, gy, near)
        p["gauge"] = (round(g[0]), round(g[1]), round(g[2]), mv._nearest_tri(mesh, g[0], g[1]))
        p["cursor"] = []
        for b in range(21):
            o_ = ((b * 50 + 25) - 500) / 1000 * mv.GAUGE_PX
            q = mv._unproject(cam, sx + o_, gy - mv.CURSOR_UP, near)
            p["cursor"].append((round(q[0]), round(q[1]), round(q[2]), mv._nearest_tri(mesh, q[0], q[1])))
    gx, gy_, gz = plays[0]["gauge"][:3]

    def tilt(d):
        a = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy_, gz), cam.project(gx + 50 * math.cos(a), gy_ + 50 * math.sin(a), gz)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        return abs(dy) / (abs(dx) + 1e-9) + (0 if dx > 0 else 100)
    sprite_dir = min(range(256), key=tilt)
    mv.SPRITES = SPRITES
    sprites = mv._sprites(ctx, half, half_cursor)
    for hrc in SPRITES:
        loader.models.append(ModelLoader.with_scale(sprites[hrc], sprite_scale))
    assert len(loader.models) == 15, len(loader.models)

    # ---- entities ---------------------------------------------------------------------------------
    CL = 1
    clothed = {"cloud": 1, "aerith": 2, "tifa": 3, "elena": 4, "king": 5, "cid": 6, "scarlet": 7}
    bare = {"cloud": 8, "cid": 9}
    ents = {}
    for name in ["g_" + k for k in SS.GIRLS] + ["gauge", "cursor", "keys", "voice", "hush", "shout", "hush2"]:
        ents[name] = len(sec.entity_names)
        sec.entity_names.append(name.encode("latin-1")[:8].ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    for k in SS.GIRLS:
        bare[k] = ents["g_" + k]
    model_of = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8}
    model_of.update({ents["g_" + k]: gm[k] for k in SS.GIRLS})
    model_of.update({ents["gauge"]: 13, ents["cursor"]: 14})
    P, STEP, NEW, RUN, K, HELD, FIN = mv.P, mv.STEP, mv.NEW, mv.RUN, mv.K, mv.HELD, mv.FIN
    POS, VEL, PR, TOT, FR, RATE, T, S, NEXT, BKT, NT, FT = (mv.POS, mv.VEL, mv.PR, mv.TOT, mv.FR, mv.RATE, mv.T,
                                                           mv.S, mv.NEXT, mv.BKT, mv.NT, mv.FT)
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    anim = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    once = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xA3, i, 1]))]
    speeds = lambda ids: mv._chain(STEP, [anim(i) for i in ids])
    by_a = lambda make: mv._chain(A, [make(i, a) for i, a in enumerate(SS.ACTS)])
    sparse_a = lambda make: mv._sparse(A, [make(i, a) for i, a in enumerate(SS.ACTS)])
    hidden = lambda: [hb._visi(0), asm.ret()]
    scripts = {e: {0: [Op(bytes([0xA1, m])), hb._visi(0), asm.ret(), asm.ret()]} for e, m in model_of.items()}
    scripts[CL][0] = [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*spot(*SS.ARRIVE)), hb._visi(0), asm.ret(), asm.ret()]
    scripts[10] = {0: [asm.ret(), asm.ret()]}                          # (oto: no model)

    # the clothed scenes: slot 3 placed (by A), 10 the beat, 11 the reaction (by RC), 2 hidden (minigame)
    def at(i, who):
        x, y, _ = SS.ACTS[i]["set"][who]
        return spot(x, y)

    def face(i, who, f):
        p = at(i, who)
        if f == "camera":
            return facing_screen(cam, *p[:3], (0, 1))
        return toward(p, at(i, f))

    def beat(i, who, steps):
        ops = []
        for w, f in steps:
            if w == who:
                ops += [hb._tura(clothed[f])] if f in clothed and f in SS.ACTS[i]["set"] else [d_(face(i, who, f))]
        return ops
    for who, e in clothed.items():
        def place(i, a, who=who):
            if who not in a["set"]:
                return [hb._visi(0)]
            return [xyzi(*at(i, who)), d_(face(i, who, a["set"][who][2])), hb._visi(1)] + anim(0)
        scripts[e][3] = by_a(place) + [asm.ret()]
        scripts[e][10] = sparse_a(lambda i, a, who=who: beat(i, who, a["mid"])) + [asm.ret()]
        scripts[e][11] = sparse_a(lambda i, a, who=who: mv._sparse(RC, [beat(i, who, r) for r in a["react"]])
                                  if any(w == who for r in a["react"] for w, _ in r) else []) + [asm.ret()]
        scripts[e][2] = [hb._visi(0)] + ([xyzi(*plays[0]["focus"])] if e == CL else []) + [asm.ret()]
    scripts[CL][2] = by_a(lambda i, a: [xyzi(*plays[i]["focus"])]) + [hb._visi(0), asm.ret()]

    # the minigames: bare actors' slot 2 (by A; Twin Jets by SIDE), 3 hidden; the girls' 8 = her turn
    def man(who, e):
        end_ = asm.nop()

        def make(i, a):
            p = plays[i]
            if who == "cloud":
                ops = [xyzi(*p["cloud"]), d_(p["cdir"]), hb._visi(1)]
                if p["kind"] != "twinjets":
                    return ops + speeds(p["canims"])
                idle = asm.nop()
                return ops + [asm.if_byte(SIDE, "==", 0, idle)] + speeds(p["canims"]) + [asm.goto(end_), idle] + anim(0)
            if "cid" not in p:
                return [hb._visi(0)]
            ops = [xyzi(*p["cid"]), d_(p["ciddir"]), hb._visi(1)]
            if p["kind"] != "twinjets":
                return ops + speeds(p["kanims"])
            idle = asm.nop()
            return ops + [asm.if_byte(SIDE, "==", 1, idle)] + speeds(p["kanims"]) + [asm.goto(end_), idle] + anim(0)
        return by_a(make) + [end_, asm.ret()]
    for who in ("cloud", "cid"):
        scripts[bare[who]][2] = man(who, bare[who])
        scripts[bare[who]][3] = hidden()
    names_k = SS.GIRLS
    for k, key in enumerate(names_k):
        e = bare[key]

        def girl_ops(i, key=key, k=k):
            p = plays[i]
            mine = p["girl"] == key
            pos_ids = None
            if p["kind"] == "holding" and mine:
                pos_ids = [gidx(key, "%s%s%d.tor" % (pre[key], letter("holding"), s)) for s in range(4)]
            elif p["kind"] == "cowgirl" and mine:
                pos_ids = [gidx(key, "%s%s%d.tor" % (pre[key], letter("cowgirl"), s)) for s in range(4)]
            elif p["kind"] == "twinjets" and mine:
                to_cid, faced = asm.nop(), asm.nop()
                return [xyzi(*p["gspot"]), asm.if_byte(SIDE, "==", 0, to_cid), d_(p["gdir"]), asm.goto(faced),
                        to_cid, d_(p["gdir2"]), faced, hb._visi(1)] + speeds([gfirst[key] + s for s in range(4)])
            if p["kind"] == "exhaust" and (mine or p["girl"] == "bride"):
                ids = [gfirst[key] + 4 + s for s in range(4)]
                ops = [xyzi(*p["gspot"]), d_(p["gdir"]), hb._visi(1)] + speeds(ids)
                if mine:
                    return ops
                no = asm.nop()                           # the bride, by FG
                return [asm.if_byte(FG, "==", k, no)] + ops + [asm.ret(), no] + watch(i, key)
            if pos_ids:
                return [xyzi(*p["gspot"]), d_(p["gdir"]), hb._visi(1)] + speeds(pos_ids)
            return watch(i, key)

        def watch(i, key):
            p = plays[i]
            if key not in p["watch"]:
                return [hb._visi(0)]
            n = p["watch"].index(key)
            c = p["cloud"]
            w = spot(c[0] + (-220 if n % 2 == 0 else 220), c[1] + 260)
            return [xyzi(*w), d_(toward(w, c)), hb._visi(1)] + anim(0)
        scripts[e][2] = by_a(lambda i, a: girl_ops(i)) + [asm.ret()]
        scripts[e][3] = hidden()
        if key == "aerith":
            scripts[e][8] = mv._chain(SIDE, [once(gfirst[key] + 8 + turn_for[1]) + [d_(tj["gdir"])],
                                             once(gfirst[key] + 8 + turn_for[0]) + [d_(tj["gdir2"])]]) + \
                speeds([gfirst[key] + s for s in range(4)]) + [asm.ret()]
    scripts[ents["gauge"]] = {0: [Op(bytes([0xA1, 13])), hb._visi(0), d_(sprite_dir), asm.ret(), asm.ret()],
                              2: by_a(lambda i, a: [xyzi(*plays[i]["gauge"])]) + [hb._visi(1), asm.ret()],
                              3: hidden()}
    loop, idle = asm.nop(), asm.nop()
    cur = [loop, asm.if_byte(RUN, "==", 1, idle), asm.setword(BKT, POS), hb._arith(0x8C, BKT, 50)]
    cur += by_a(lambda i, a: mv._tree(BKT, 0, 20, lambda b: [xyzi(*plays[i]["cursor"][b])])) + \
        [hb._visi(1), hb._w(1), asm.goto_back(loop)]
    cur += [idle, hb._visi(0), hb._w(1), asm.goto_back(loop)]
    scripts[ents["cursor"]] = {0: [Op(bytes([0xA1, 14])), hb._visi(0), d_(sprite_dir), asm.ret()] + cur + [asm.ret()]}
    wait = hb._w(1)
    back1, up = asm.goto_back(wait), asm.setbyte(HELD, 0)
    scripts[ents["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x96, FR[0], FR[1]])),
                                 Op(bytes([0x30]) + struct.pack("<H", mv.OK_KEY) + b"\x00", target=up),
                                 asm.if_byte(HELD, "==", 0, back1), asm.setbyte(HELD, 1),
                                 Op(bytes([0x96, PR[0], PR[1]])), back1,
                                 up, asm.goto_back(wait), asm.ret()]}
    texts = {}

    def text(t):
        if t not in texts:
            texts[t] = sec.add_string(mv._encode(t))
        return texts[t]

    def voice_line(i, raw):
        a = SS.ACTS[i]
        who = a["play"]["girl"]
        if raw.startswith("C:"):
            t = "{CLOUD}\n“%s”" % raw[2:]
        elif raw.startswith("I:"):
            t = "Cid\n“%s”" % raw[2:]
        else:
            t = "%s\n%s" % ("The Bride" if who == "bride" else SS.NAMES[who], raw)
        return [Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, mv.LINE_Y), hb._req(ents["hush"], 2, wait=False),
                asm.message(1, text(t))]
    vl, vdone = asm.nop(), asm.nop()
    voice = [asm.ret(), vl, hb._w(mv.SAY_EVERY), asm.if_byte(RUN, "==", 1, vdone),
             Op(bytes([0x95, K[0], K[1]])), Op(bytes([0x8D, K[0] << 4, K[1], 4]))]
    voice += by_a(lambda i, a: mv._chain(K, [voice_line(i, raw) for raw in a["lines"]]))
    voice += [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.SAY_FOR), Op(b"\x54\x01"), asm.ret()]}
    scripts[ents["shout"]] = {0: [asm.ret(), asm.ret()],
                              2: [Op(b"\x52\x02\x00\x01"), hb._window(SS.SHOUT, 2, 8, 56),
                                  hb._req(ents["hush2"], 2, wait=False), asm.message(2, text(SS.SHOUT)), asm.ret()]}
    scripts[ents["hush2"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.FINISH_SAY_FOR), Op(b"\x54\x02"), asm.ret()]}

    # ---- the director -----------------------------------------------------------------------------
    say = lambda t: [hb._window(t, 0), asm.message(0, text(t))]
    clothed_e, bare_e = list(clothed.values()), [bare[k] for k in ("cloud", "cid")] + [bare[k] for k in SS.GIRLS]
    req = lambda es, slot: [hb._req(e, slot, wait=False) for e in es]
    lost, wrap, tick, hi_red, walkout, gone = (asm.nop() for _ in range(6))

    def leave(key):
        return mv.lose_affection(key) + say(key.capitalize() + "\n" + PF.PROFILES[key]["leave"]) + [asm.goto(walkout)]

    def choose(i, a):
        q, choices = a["ask"]
        ops, first = hb._ask(sec, q, [c[0] for c in choices])
        done = asm.nop()
        for j, (label, reply, eff) in enumerate(choices):
            nx = asm.nop()
            ops += [asm.if_byte(CHOICE, "==", first + j, nx), asm.setbyte(RC, j)] + req(clothed_e, 11) + [hb._w(15)] + \
                say(reply) + mv._gil_ops(eff.get("gil", 0) * SS.SHOW_RATE)
            if "finale" in eff:
                ops += [asm.setbyte(FG, SS.GIRLS.index(eff["finale"]))]
            for g in eff.get("annoy", []):
                ops += mv._annoy(SS.GIRLS.index(g), leave(g))
            ops += [asm.goto(done), nx]
        return ops + [done]

    def scene(i, a):                                  # the act's clothed scene
        ops = [Op(mv.FAST_OUT), Op(b"\x6C")] + req(clothed_e, 3) + req(bare_e + [ents["gauge"]], 3) + \
            [hb._w(8), Op(mv.FAST_IN), Op(b"\x6C")]
        if i == 0:
            ops += [Op(bytes([0xF2, 0, 0, 0, 0x10, SS.MUSIC]) + bytes(8))] + say(SS.OPENING)
        ops += say(a["title"]) + say("{NEW}".join(a["talk"])) + req(clothed_e, 10) + [hb._w(15)] + \
            say("{NEW}".join(a["talk2"])) + choose(i, a)
        return ops
    act_top = asm.nop()
    main = [asm.if_byte(SS.SHOW_ON[0], "bit_on", SS.SHOW_ON[1], gone), asm.bitoff(*SS.SHOW_ON),
            hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setbyte(A, 0), asm.setbyte(FG, 1), asm.setword(TOT, 0),
            asm.setbyte(FIN, 0), asm.setbyte(K, 0)] + [asm.setbyte(mv._ann(k), 0) for k in range(4)]
    main += [act_top] + by_a(scene)
    main += [Op(mv.FAST_OUT), Op(b"\x6C"), asm.setbyte(SIDE, 0), asm.setbyte(SEG, 0), asm.setbyte(STEP, 0),
             asm.setword(POS, 500), asm.setword(VEL, 1000), asm.setword(RATE, 40)] + req(clothed_e, 2) + \
        [hb._req(CL, 2, wait=False)] + req(bare_e + [ents["gauge"]], 2) + \
        [hb._w(8), Op(mv.FAST_IN), Op(b"\x6C"), Op(bytes([0xF2, 0, 0, 0, 0x10, SS.PLAY_MUSIC]) + bytes(8)),
         asm.setword(FR, 0), asm.setword(PR, 0), asm.setword(NT, mv.TICK)] + \
        by_a(lambda i, a: [asm.setword(NEXT, a["play"].get("frames", SS.MINUTE))]) + \
        [asm.setword(SW, SWITCH), asm.setbyte(RUN, 1)]
    wait1, go = hb._w(1), asm.nop()
    A_, B, C, VMAX, DANGER = mv.A, mv.B, mv.C, mv.VMAX, mv.DANGER
    main += [tick, wait1, asm.if_word(FR, "<", NT, go), asm.goto_back(wait1), go, hb._arith(0x86, NT, mv.TICK),
             asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
             hb._arith(0x8A, VEL, 5), hb._arith(0x8C, VEL, 6),
             hb._arith(0x86, VEL, 1000 - 1000 * 5 // 6 - B - 500 // C),
             asm.setword(S, T), hb._arith(0x8A, S, A_), hb._arith(0x86, VEL, S),
             asm.setword(S, POS), hb._arith(0x8C, S, C), hb._arith(0x86, VEL, S)]
    lo, hi = asm.nop(), asm.nop()
    main += [asm.if_word(VEL, "<", 1000 - VMAX, lo), asm.setword(VEL, 1000 - VMAX), lo,
             asm.if_word(VEL, ">", 1000 + VMAX, hi), asm.setword(VEL, 1000 + VMAX), hi,
             asm.setword(S, POS), hb._arith(0x86, S, VEL),
             asm.if_word(S, ">=", 1000 + DANGER, lost),
             asm.setword(POS, S), hb._arith(0x88, POS, 1000),
             asm.if_word(POS, "<=", 1000 - DANGER, hi_red)]
    no_call = asm.nop()                                 # the finale: the finisher's call
    main += [asm.if_byte(A, "==", 3, no_call), asm.if_byte(FIN, "==", 0, no_call),
             asm.setword(FT, FR), hb._arith(0x86, FT, mv.FINISH_FRAMES), asm.if_word(FT, ">=", NEXT, no_call),
             asm.setbyte(FIN, 1), hb._req(ents["shout"], 2, wait=False), no_call]
    done, same = asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(S, T), hb._arith(0x8A, S, 16),
             hb._arith(0x86, RATE, S), asm.setbyte(NEW, 0)]
    for s_, th in enumerate(mv.RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s_ + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW)] + req(bare_e, 2) + [same]
    no_sw = asm.nop()                                   # Twin Jets: she turns to the other man
    main += [asm.if_byte(A, "==", 2, no_sw), asm.if_word(FR, ">=", SW, no_sw),
             hb._arith(0x86, SW, SWITCH), Op(bytes([0x85, SIDE[0] << 4, SIDE[1], 1])),
             Op(bytes([0x8D, SIDE[0] << 4, SIDE[1], 2])),
             hb._req(bare["cloud"], 2, wait=False), hb._req(bare["cid"], 2, wait=False),
             hb._req(bare["aerith"], 8, wait=False), no_sw]
    stay = asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay), asm.setbyte(RUN, 0), Op(b"\x54\x01"),
             asm.if_byte(A, "<", 3, wrap), Op(bytes([0x95, A[0], A[1]])), asm.goto_back(act_top),
             stay, asm.goto_back(tick)]
    rx, ry = SS.BOOKER["back"]
    bmesh = Walkmesh(ctx.field(SS.BOOKER["field"]).section("walkmesh"))
    bt = bmesh.find(rx, ry)
    assert bt is not None, ("the Booker's return spot", rx, ry)

    def out():
        stop = hb._w(30)
        capped = asm.nop()
        return [asm.setword(GIL, TOT), asm.if_word(GIL, "<=", 65535 // SS.SHOW_RATE, capped),
                asm.setword(GIL, 65535 // SS.SHOW_RATE), capped, hb._arith(0x8A, GIL, SS.SHOW_RATE),
                Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), sound(0x168),
                hb._window(SS.PAY, 0), Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])),
                asm.message(0, text(SS.PAY)),
                Op(mv.FAST_OUT), Op(b"\x6C"), hb._uc(0), hb._menu(0),
                asm.mapjump(ctx.maplist.index(SS.BOOKER["field"]), rx, ry, bt, 0x80), stop, asm.goto_back(stop), asm.ret()]
    curtain = [Op(mv.FAST_OUT), Op(b"\x6C"), asm.setbyte(A, 3)] + req(bare_e + [ents["gauge"]], 3) + \
        req(clothed_e, 3) + [hb._w(8), Op(mv.FAST_IN), Op(b"\x6C")] + say(SS.CURTAIN)
    main += [hi_red, sound(mv.RED_SOUND), asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"),
             Op(b"\x54\x02"), Op(bytes([0xF2, 0, 0, 0, 0x10, mv.FANFARE]) + bytes(8)), hb._w(45)] + say(SS.FINISHER) + \
        mv._gil_ops(SS.FINISH_BONUS) + curtain + out()
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)] + say(SS.BOOED) + out()
    main += [walkout, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)] + say(SS.WALKED) + out()
    main += [wrap] + curtain + out()
    bx, by_ = SS.BOOKER["back"]
    main += [gone, hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(SS.BOOKER["field"]), bx, by_, bt, 0x80), asm.ret()]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n <= 250, ("texts", n)
    ctx.show_plays = plays
    return n


def _booker(ctx):
    """The Booker (the play's King) in Event Square: offers the show once unlocked."""
    hb = importlib.import_module("620_honey_bee")
    b = SS.BOOKER
    mesh = Walkmesh(ctx.field(b["field"]).section("walkmesh"))
    x, y = b["at"]
    t = mesh.find(x, y)
    assert t is not None, ("the Booker's spot", x, y)
    pos = (x, y, round(mesh.height(t, x, y)), t)
    smesh = Walkmesh(ctx.field(SS.SET).section("walkmesh"))
    ax, ay = SS.ARRIVE
    at_ = smesh.find(ax, ay)
    cam = Camera(ctx.field(b["field"]).sections[1])

    qx = importlib.import_module("600_quests")
    bq, (bc, _) = qx.quest_state("film_booker"), qx.quest_counter("film_booker")

    def talk(sec):
        say = lambda t: hb._say(sec, "Booker\n" + t)
        locked, no, end, booked = asm.nop(), asm.nop(), asm.nop(), asm.nop()
        ops = [Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00"),          # PTURA (face the player), WAIT
               asm.if_byte(SPECIAL_ON[0], "bit_on", SPECIAL_ON[1], locked),
               asm.if_byte(CID.AFFECTION, ">=", SS.UNLOCK_CID, locked),
               # (user) only a troupe the cameraman sent ("Top of the Bill", 670): handed in here
               asm.if_byte(bq, ">=", qx.ACCEPTED, locked), asm.if_byte(bq, "==", qx.ACCEPTED, booked)]
        for t_ in SS.BOOKER_LINES["booked"]:
            ops += say(t_)
        ops += qx.count_ops("film_booker") + qx.reward_ops(sec, "film_booker") + [asm.setbyte(bq, qx.DONE), booked]
        ask, first = hb._ask(sec, "Booker\n" + SS.BOOKER_LINES["offer"], SS.BOOKER_LINES["choices"])
        ops += ask + [asm.if_byte(CHOICE, "==", first, no), asm.biton(*SS.SHOW_ON),
                      asm.mapjump(ctx.maplist.index(SS.SET), ax, ay, at_, 0x80), asm.ret(),
                      no] + say(SS.BOOKER_LINES["no"]) + [asm.goto(end), locked]
        for t_ in SS.BOOKER_LINES["locked"]:
            ops += say(t_)
        return ops + [end, asm.ret()]
    reuse_npc(ctx, b["field"], b["entity"], b["donor"], pos, facing_screen(cam, *pos[:3], (0, 1)), talk)


def apply(ctx):
    n = _show(ctx, ctx.blast_built)
    _booker(ctx)
    print("  674: the stage show on %s (%d texts)" % (SS.SET, n))
    for i, p in enumerate(ctx.show_plays):
        print("    act %d %s: cloud %s %d, girl %s %d%s" % (i + 1, p["kind"], p["cloud"][:3], p["cdir"], p["gspot"][:3],
                                                      p["gdir"], ", cid %s %d" % (p["cid"][:3], p["ciddir"]) if "cid" in p else ""))

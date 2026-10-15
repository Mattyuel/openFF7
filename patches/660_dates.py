"""Dates with the Honey Bee girls (docs/dates_plan.md; data `_dates_data.py`).

Talking to a girl out in the world (hired or not, job or not) first asks
"Just chat." / "Ask her on a date."; a date asks "Where to?": the Gold Saucer
gondola or the space capsule. DATE_GIRL = her index + 1 and a MAPJUMP into
that place's date field for her group. Her affection (shared with the Honey
Bee, `_config.HB_AFFECTION`) picks the date: < 10 first, < 20 second, 20 third.
Right answers give +1 (capped at 20); the third date's choice ("Give into your
desires." / "Leave it be.") needs every answer of that date right. Afterwards
DATE_GIRL = 0 and back beside her.

Date fields are new fields (`ctx.new_field`) with a blank script: every entity
keeps its CHAR (model count and CHAR order unchanged), all old code and texts
are dropped, entity 0 becomes the director.
- gondola: bwhlin's still view (the Gold Saucer at night; no FMV, user), Cloud
  and her where the original date seats them, with their gondola sitting anims.
- capsule: rcktin7's pod with the space layer on (BG param 1 on, param 2 = the
  hatch's closed view off, as the original's `space` script 1): stars through
  the round window. Cloud and her on the benches either side of the gangway,
  facing each other (sitting anims borrowed from the gondola models).
"""
import importlib
import math

from _config import DATE_GIRL, HB_AFFECTION
from _dates_data import DATES
import _movie_girls as MG
from _honey_bee_data import GIRLS
from _recruit import sound
from _travel import CHOICE, beside, screen_step

from ff7 import asm
from ff7.camera import Camera, facing_screen
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

MAX = 20
WRONG = (5, 246)                       # temp: an answer this date was wrong
TIERS = (10, 20)                       # affection where the second / third dates start
# date fields: (place, group) -> new field name (free maplist names, docs/dates_plan.md)
GROUPS = [["Tifa", "Aerith", "Scarlet", "Elena"]]
FIELDS = {("gondola", 0): "blackbga", ("capsule", 0): "blackbgf", ("cannon", 0): "blackbgg", ("beach", 0): "fship_26"}
BASE = {"gondola": "bwhlin", "capsule": "rcktin7", "cannon": "junone7",   # (user) the cannon replaced the water tower
        "beach": "del3"}                                                  # (user) Costa del Sol's beach, empty
PLACES = ("gondola", "capsule", "cannon", "beach")
PLACE_NAMES = {"gondola": "The Gold Saucer gondola.", "capsule": "The space capsule.",
               "cannon": "The Junon cannon.", "beach": "The beach at Costa del Sol."}
# (user) one position per place, the same for every girl: the movie's poses (670 `POSITIONS`, each
# girl's retargeted copies; "finisher" = 672's special part three: she astride him lying back);
# "head": her copy moved forward onto his spot (676 `_date_heads`), so both share one XYZI
POSITION = {"capsule": "behind", "gondola": "head", "cannon": "holding", "beach": "finisher"}
TURNED = {"behind": 0, "head": 128, "holding": 128, "finisher": 0}   # her DIR from his
SPEED, SPEED_FAST = 1, 3                                            # 670 SPEEDS: 15 / 8 frames a stroke
BARE = {"Tifa": "ZTFA.HRC", "Aerith": "ZAEA.HRC", "Scarlet": "ZSCA.HRC", "Elena": "ZELA.HRC"}
# where part two happens: (x, y) (None: Cloud's seat), plus a height (field units)
PLACE_SPOT = {"capsule": (52, 227),                     # (user) Scarlet's seat: where her wall scene was
              "gondola": None, "cannon": None,          # Cloud's seat (Aerith's / Tifa's scenes)
              "beach": None}                            # Cloud's lounger (LOUNGE_Z above the sand)
# seats: (x, y, tri, dir) for Cloud and her (tri None: found; dir None: facing each other)
SEATS = {
    # the original date's XYZIs and DIRs (Cloud is the player: the MAPJUMP's direction
    # overrode his DIR, so he faced 0 = the wrong way (user); the jump now carries it)
    "gondola": {"cloud": (-5175, -6999, 4, 0x80, 0), "girl": (-5150, -6903, 5, 0x00, 0)},
    "capsule": {"cloud": (-45, 209, None, None, 0), "girl": (45, 209, None, None, 0)},  # floor before the benches
    # junone7 (the top of the cannon, user): where Tifa and Scarlet stand for their slap fight
    # (ti MOVE to (3,447), sca MOVE to (-17,720)): Cloud in Tifa's place, she in Scarlet's,
    # standing, facing each other
    "cannon": {"cloud": (3, 447, None, None, 0), "girl": (-17, 720, None, None, 0)},
    # (user) the two loungers on the left with the table between, both lounging (del3: off the sand's
    # walkmesh by 9 / 15: the nearest triangle), facing the sea (down the screen)
    "beach": {"cloud": (-190, 384, None, 240, "lounge"), "girl": (-458, 415, None, 240, "lounge")},   # (along the loungers)
}
LOUNGE_Z = 6                          # the loungers' seats above the sand (field units)
# part two (user's test scene): Cloud standing (bare, ZCTE thrusting) at his seat, she
# koala-hugging him (same XYZI, turned round; her height is in the anim): his DIR there
STAND_DIR = {"gondola": 0x80, "capsule": None, "cannon": None, "beach": None}
SCALE = {}                            # per place model scale (the water tower had 0.85)
GIRL_SCALE = {}                        # per-girl model scale (Scarlet 1.12 was tried; user: keep her size)
# a girl's own seat in a place (x, y): Scarlet further left and nearer the camera in the gondola (user)
# (user, since) Elena half a body width further left on screen in the gondola and capsule (~15 px):
# in the gondola that is just off the floor's edge (a seated girl never walks: the nearest triangle)
GIRL_SEAT = {("gondola", "Scarlet"): (-5198, -6900), ("capsule", "Scarlet"): (52, 227),   # (user: the capsule too)
             ("gondola", "Elena"): (-5198, -6884), ("capsule", "Elena"): (57, 209)}
NEAR_FLOOR = 20                       # a seat may be this far off the floor's edge (field units)
WALK_TO = 0.35                        # "stand": she walks over to Cloud, this far from him along the way
# places whose near background tiles (draw depth < 4093: the capsule's benches and rails, ids
# 52-87) drew over the characters (user): pushed back just in front of the base layer
TILES_BACK = {"capsule"}
# original entities kept as they were (scripts 0 and 1): the cannon's SEA cycles the sea's
# background states (param 1 states 1-7, then param 2 states 0-2)
KEEP = {"cannon": ("SEA",)}
# (the beach's waves: entity 0 `wave` cycles the sea's BG states, but entity 0 is the director: its
# scripts go to `direct`, which has no model)
KEEP_AS = {"beach": {"direct": "wave"}}
# "bench" = sitting: the gondola models' own sitting anims (feet on the floor), or ours;
# "stand" (user: on the cannon they stand) = each model's own anim 0 (its standing idle)
SIT_KIND = {"gondola": "bench", "capsule": "bench", "cannon": "stand", "beach": "lounge"}
CLOUD_SIT = {"bench": "GDAB.chi", "stand": None}             # bwhlin cloud DFANM 03 (lounging: `_lounge`)
# (user) lounging on a beach lounger (`_lounge`): legs straight out level, the upper body leant back
# LOUNGE_BACK; one per skeleton, built from the model's own standing anim
LOUNGE_BACK = 50
LOUNGE = {}                                                  # skeleton -> its anim, built by `_field` (ZDL*)
GIRL_SIT = {"Tifa": {"bench": "GDEE.chi"},                    # bwhlin tifa DFANM 03
            "Aerith": {"bench": "GDBE.chi"},                  # bwhlin earith DFANM 03
            "Scarlet": {"bench": "ZDBS.tor"},                 # ours
            "Elena": {"bench": "ZDBE.tor"}}                   # ours
BENCH = {"ZDBS.tor": ("amcc.hrc", "anae.a"), "ZDBE.tor": ("evfe.hrc", "acfe.a")}   # no sitting anims: ours
LEDGE_ARMS, LEDGE_SEAT = 25, 1.5
# part two: each girl's undressed copy (a NEW skeleton file; her own model is untouched)
# and her pose; Tifa: AAGB with the chest part's white top (vertex colour B,G,R 204) in her
# skin colour (167,190,248): new zfta.hrc -> ztfb.rsd -> ztgb.p
HEAD_RIGHT = 40
TIFA_TOP, TIFA_SKIN = (204, 204, 204), (167, 190, 248)
# her skirt (user: skin colour, contoured to her body): the hip part AAGC (aagd.p: skirt
# 25,25,25 and its waistband 76,76,76) -> ztfc.rsd -> ztgc.p, all in skin colour, the flared
# lower rings (z 0 / z -1.8 along the hip bone, up to x 3.3, y 2.5) pulled in to her hips
# and thighs (thighs reach x ~2.6, radius 1.15 about x 1.43): (x, y) scale per ring
TIFA_SKIRT = (25, 25, 25), (76, 76, 76)
# her thighs (user: the same colour as the rest of her): ABAD/ABBD (abae/abbe.p, 135,167,248)
# -> ztfd/ztfe.rsd -> ztgd/ztge.p in TIFA_SKIN
TIFA_THIGHS = {"ABAD": ("ZTFD", "ZTGD"), "ABBD": ("ZTFE", "ZTGE")}
THIGH_SKIN = (135, 167, 248)
THIGH_TOP = 1.3                       # (user) upper thighs thicker: the hip end ring (z 0) scaled
SKIRT_RINGS = {0.0: (0.8, 0.68), -1.8: (0.86, 0.8),
               -3.09: (0.83, 0.85)}   # (user) the ring under the waist (x 2.65) flanged out: tapered in
# koala (user's test scene): she clings to standing Cloud (620's ZCTH: ZCTE leaning back,
# arms bent in round her), legs spread wide and wrapped round him, arms round his neck,
# bouncing with his thrusts; leaning a little forward onto him (he leans back)
KOALA_LEAN, KOALA_ARMS, KOALA_THIGH, KOALA_SPREAD, KOALA_KNEE = -10, 95, 85, 45, 90   # (user: arms 85 then 95, thighs 85, spread, knees 90)
KOALA_PELVIS = 10                     # then the pelvis tipped up 10 more (user)
KOALA_ARMS_IN, KOALA_NOD = 10, 12     # (user) arms turned in a little; the head nods with her bounce
KOALA_FRONT, KOALA_BACK, KOALA_UP, KOALA_BOUNCE = 2.5, 1.4, 1.0, 1.5   # (BACK 2.0 -> 1.4: closer, user)    # his belly, her seat, her lift, the bounce       # arms this far forward (hands to the thighs); hip joints this far up
GIRL_MODEL = {"Tifa": "main_n_tifa.char", "Aerith": "main_n_earith.char",   # her model entry (name suffix)
              "Scarlet": "sub_scarlet.char", "Elena": "shinra_irena.char"}
# date fields at 16 models give a girl's undressed copy one of these unused party models' slots
SPARE = ("main_vincent.char", "main_ketcy.char", "main_yufi.char", "main_cid.char", "main_red.char",
         "sub_siera.char", "main_ballet.char")
GIRL_DONOR = {"Aerith": ("bwhlin", 1), "Scarlet": ("blin66_1", 5), "Elena": ("datiao_6", 10)}   # where a field lacks her
# extra anims on her model for the dates (the third date's "stand" and "slap" steps):
# Scarlet's slap = junone7's (sca script 7: CANM!2 FDID 0-0x1D, SOUND 0x76, CANM!2 0x1D-0x31)
GIRL_EXTRA = {"Scarlet": {"stand": "ANAE.tak", "slap": "FDID.yos"}}
# (Aerith's third date had look / stand / kneel; user: she stays seated, no movement)
# girls whose third date starts with them standing close to Cloud, facing him (user: Scarlet,
# no sitting or walking before the slaps): at the "stand" walk's end spot, from the init
STAND_ON_THIRD = {"Scarlet"}
SLAP_HIT, SLAP_END, SLAP_SOUND = 0x1D, 0x31, 0x76
RETURN_GAP = 40                        # back beside her: this far from her spot
RETURN_SCREEN = {"Aerith": (-1, 0)}    # (user: stuck beside her after a date) to her left on screen


def _dir_to(dx, dy):
    """DIR facing field vector (dx, dy): direction d faces (sin a, -cos a), a = d*2pi/256."""
    return round(math.atan2(dx, -dy) * 128 / math.pi) % 256


def _clear_texts(sec):
    """Drop every text (before adding the new ones: ids start at 0 again)."""
    import struct
    strings_end = min(sec.akao_offsets) if sec.akao_offsets else len(sec.tail)
    sec.tail = struct.pack("<H", 0) + sec.tail[strings_end:]
    sec.akao_offsets = [o - strings_end + 2 for o in sec.akao_offsets]


def _blank(sec, scripts):
    """Drop every op; entity e gets scripts[e] ({slot: ops}, each ending in RET),
    other slots an empty RET."""
    empty = Op(b"\x00")
    sec.ops = [empty]
    for e in range(len(sec.entity_names)):
        entry = [empty] * 32
        for k, ops in sorted(scripts.get(e, {}).items()):
            assert ops[-1].op == 0x00, (e, k)
            entry[k] = ops[0]
            sec.ops.extend(ops)
        sec.entry[e] = entry


def _hb():
    from importlib import import_module
    return import_module("620_honey_bee")


def _near(mesh, cs, my):
    """(x, y, tri) WALK_TO of the way from Cloud's seat cs towards hers, or the nearest floor
    towards him from there (the capsule's gangway between them isn't floor)."""
    tx, ty = cs[0] + (my[0] - cs[0]) * WALK_TO, cs[1] + (my[1] - cs[1]) * WALK_TO
    tt = mesh.find(round(tx), round(ty))
    k = 0
    while tt is None and k < 50:
        k += 1
        tx, ty = tx + (cs[0] - tx) * 0.05, ty + (cs[1] - ty) * 0.05
        tt = mesh.find(round(tx), round(ty))
    assert tt is not None, (cs, my)
    return round(tx), round(ty), tt


def _return_spot(ctx, g):
    """(x, y, tri, dir) beside her in her world field, facing her."""
    mesh = Walkmesh(ctx.field(g["field"]).section("walkmesh"))
    x, y = g["at"]
    tri = mesh.find(x, y)
    if g["name"] in RETURN_SCREEN:
        bx, by, _, bt = screen_step(ctx, g["field"], x, y, RETURN_SCREEN[g["name"]], RETURN_GAP)
    else:
        bx, by, _, bt = beside(ctx, g["field"], x, y, tri, RETURN_GAP)
    return bx, by, bt, _dir_to(x - bx, y - by)


def _date(sec, ctx, place, i, g, d, part2):
    tier_acts, part2, acts = part2
    """The date's ops for girl i (in the director's main), ending in the MAPJUMP back;
    part2 = the ops switching to part two's models."""
    hb = _hb()
    name, aff = g["name"], HB_AFFECTION[i]
    her = lambda t: d.get("speaker", name) + "\n" + t
    out = asm.nop()
    ops = [asm.setbyte(WRONG, 0)]
    tier_at = [asm.nop() for _ in d["tiers"]]
    not3, not2 = asm.nop(), asm.nop()
    ops += [asm.if_byte(aff, ">=", TIERS[1], not3), asm.goto(tier_at[2]), not3,     # 20: third
            asm.if_byte(aff, ">=", TIERS[0], not2), asm.goto(tier_at[1]), not2,     # 10-19: second
            asm.goto(tier_at[0])]
    for t, tier in enumerate(d["tiers"]):
        block = []
        block += hb._say(sec, her(tier["open"]))
        for st in tier["steps"]:
            if st[0] == "G":
                block += hb._say(sec, her(st[1]))
            elif st[0] == "C":
                block += hb._say(sec, "{CLOUD}\n" + st[1])
            elif st[0] == "A":                           # an action of hers ("stand", "slap")
                block += tier_acts[st[1]]
            else:
                _, q, answers, right, yes, no = st
                ask, first = hb._ask(sec, her(q), answers)
                wrong, done, ok = asm.nop(), asm.nop(), asm.nop()
                block += ask + [asm.if_byte(CHOICE, "==", first + right, wrong),
                                Op(bytes([0x85, aff[0] << 4, aff[1], 1])),            # PLUS 1
                                asm.if_byte(aff, ">", MAX, ok), asm.setbyte(aff, MAX), ok,
                                sound(0x168)] + hb._say(sec, her(yes)) + [asm.goto(done), wrong,
                                asm.setbyte(WRONG, 1)] + hb._say(sec, her(no)) + [done]
        if t == 2:                                   # the choice: every answer this date right
            plain = asm.nop()
            block += [asm.if_byte(WRONG, "==", 0, plain)] + hb._say(sec, her(d["lead"]))
            ask, first = hb._ask(sec, her("…"), ["Give into your desires.", "Leave it be."])
            leave = asm.nop()
            block += ask + [asm.if_byte(CHOICE, "==", first, leave)]
            block += part2
            for who, line in d["part2"][place]:
                if who == "act":                     # "stop" / "fast"
                    block += acts[line] + [hb._w(20)]
                else:
                    block += hb._say(sec, (her(line) if who == "G" else "{CLOUD}\n" + line)) + [hb._w(20)]
            block += [hb._w(30), Op(hb.FADE_OUT), Op(b"\x6C")] + hb._say(sec, d["desire"][place])
            block += [asm.goto(out), leave] + hb._say(sec, her(d["leave"]))
            block += [asm.goto(out), plain]
        block += hb._say(sec, her(tier["close"])) + [asm.goto(out)]
        ops += [tier_at[t]] + block
    rx, ry, rt, rd = _return_spot(ctx, g)
    ops += [out, asm.setbyte(DATE_GIRL, 0), hb._uc(0), hb._menu(0),
            asm.mapjump(ctx.maplist.index(g["field"]), rx, ry, rt, rd), asm.ret()]
    return ops


def _field(ctx, place, group, names):
    hb = _hb()
    name = FIELDS[(place, group)]
    f = ctx.new_field(name, ctx.field(BASE[place]).build())
    sec = Script.parse(f.sections[0])
    _clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    loader = ModelLoader(f.section("models"))
    model_names = [ModelLoader.name(e) for e in loader.models]
    # every entity's CHAR (model index) in entity order
    chars = {}
    for e in range(len(sec.entity_names)):
        op = next((o for o in sec.script_ops(e, 0) if o.op == 0xA1), None)
        if op is not None:
            chars[e] = op.raw[1]
    assert sorted(chars.values()) == list(range(len(loader.models))), chars
    model_ent = {m: e for e, m in chars.items()}
    spare_used = set()
    assert model_names[0].endswith("main_n_cloud.char"), model_names[0]

    def seat(who):
        x, y, tri, _, dz = SEATS[place][who]
        if dz == "lounge":                       # (on a lounger, off the sand's walkmesh)
            tri = _find_near(mesh, x, y, (place, who))
            return x, y, mesh.height(tri, x, y) + LOUNGE_Z, tri
        if tri is None:
            tri = mesh.find(x, y)
        assert tri is not None and mesh.contains(tri, x, y), (name, who, x, y)
        return x, y, mesh.height(tri, x, y) + dz, tri

    def sit_anim(m, anim):
        if anim is None:                         # standing: the model's own idle
            return 0
        if anim == "lounge":                     # (user) lounging (beach): built for this model's skeleton
            hrc = ModelLoader.hrc(loader.models[m]).lower()
            anim = LOUNGE.get(hrc) or next("ZDL%s.tor" % c for c in "ABCDEFGHIJ" if "ZDL%s.tor" % c not in LOUNGE.values())
            if hrc not in LOUNGE:
                LOUNGE[hrc] = anim
                _lounge(ctx, anim, hrc, ModelLoader.anims(loader.models[m])[0].split(".")[0].lower() + ".a")
        anims = ModelLoader.anims(loader.models[m])
        if anim not in anims:
            loader.models[m] = ModelLoader.with_anims(loader.models[m], [anim])
            anims = ModelLoader.anims(loader.models[m])
        return anims.index(anim)

    cs, gs = seat("cloud"), seat("girl")
    cdir, gdir = _dir_to(gs[0] - cs[0], gs[1] - cs[1]), _dir_to(cs[0] - gs[0], cs[1] - gs[1])
    gdir = SEATS[place]["girl"][3] if SEATS[place]["girl"][3] is not None else gdir
    cam = Camera(f.sections[1])
    if SEATS[place]["cloud"][3] is not None:
        cdir = SEATS[place]["cloud"][3]
    def slot(entry, ename):
        """A model slot + its entity for entry: a new one while under 16 models, else the slot of a
        model the date doesn't use (not Cloud, not a date girl's; party models first, `SPARE`), its
        entity taken over (a date's script is blank). (user: the beach, del3, has 13 of its own)"""
        if len(loader.models) < 16:
            k = len(loader.models)
            loader.models.append(entry)
            model_names.append(ModelLoader.name(entry))
            e = len(sec.entity_names)
            sec.entity_names.append(ename.encode("latin-1")[:8].ljust(8, b"\0"))
            sec.entry.append([None] * 32)
            chars[e], model_ent[k] = k, e
            return k, e
        keep = {0} | spare_used | {k for k, n in enumerate(model_names) if any(n.endswith(GIRL_MODEL[g]) for g in names)}
        k = sorted((k for k in range(len(model_names)) if k not in keep),
                   key=lambda k: not model_names[k].endswith(SPARE))[0]
        spare_used.add(k)
        loader.models[k] = entry
        model_names[k] = ModelLoader.name(entry)
        return k, model_ent[k]
    # girls whose model the base field lacks: copied from GIRL_DONOR
    for gname in names:
        if not any(n.endswith(GIRL_MODEL[gname]) for n in model_names):
            dfield, di = GIRL_DONOR[gname]
            entry = loader.models.pop(loader.add_from(ModelLoader(ctx.field(dfield).section("models")), di))
            slot(entry, gname.lower())
    for gname in names:
        if gname in GIRL_SCALE:
            m = next(k for k, n in enumerate(model_names) if n.endswith(GIRL_MODEL[gname]))
            loader.models[m] = ModelLoader.with_scale(loader.models[m],
                                                      round(ModelLoader.entry_scale(loader.models[m]) * GIRL_SCALE[gname]))
    if place in SCALE:
        for k, e in enumerate(loader.models):
            loader.models[k] = ModelLoader.with_scale(e, round(ModelLoader.entry_scale(e) * SCALE[place]))
    kind = SIT_KIND[place]
    scripts = {}
    ca = sit_anim(0, "lounge" if kind == "lounge" else CLOUD_SIT[kind])
    scripts[model_ent[0]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), hb._xyzi(*cs), Op(bytes([0xB3, 0, cdir])),
                                 Op(bytes([0xA2, ca, 1])), Op(bytes([0xAE, ca, 1])), asm.ret(), asm.ret()],
                             3: [hb._visi(0), asm.ret()]}
    # part two: bare Cloud (620's zcla.hrc) with every part-two pose: slot 3 shows him at his
    # seat, PART2_SLOTS[pose] loops a pose, slot 9 stops (holds frame 0 of the pose he's in)
    bdir = STAND_DIR[place]
    if bdir is None:
        bdir = cdir
    elif bdir == "screen-right":
        bdir = facing_screen(cam, cs[0], cs[1], cs[2], (1, 0))
    poses = _pose_anims(place, None)                 # (user) the place's position: Cloud slow, fast
    bare, cb = slot(ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[0], hb.CLOUD_BARE_HRC,
                                                                 model_names[0][:-5] + "_b.char"), poses), "cloudb")
    first = len(ModelLoader.anims(loader.models[bare])) - len(poses)
    num = lambda v: 0 if v == "lounge" else v
    floor = (cs[0], cs[1], cs[2] - num(SEATS[place]["cloud"][4]), cs[3])
    pdir = bdir
    spot = floor                                     # part two's spot: Cloud's seat, or the place's own
    if PLACE_SPOT[place]:
        px_, py_ = PLACE_SPOT[place]
        pt_ = _find_near(mesh, px_, py_, (place, "part two"))
        spot = (px_, py_, mesh.height(pt_, px_, py_), pt_)
    scripts[cb] = {0: [Op(bytes([0xA1, bare])), hb._visi(0), asm.ret(), asm.ret()],
                   3: [hb._xyzi(*spot), Op(bytes([0xB3, 0, pdir])), hb._visi(1), asm.ret()]}
    for k in range(2):                               # 4+k: loop pose k (slow, fast); 12+k: hold its frame 0
        scripts[cb][4 + k] = [Op(bytes([0xA2, first + k, 1])), Op(bytes([0xAE, first + k, 1])), asm.ret()]
        scripts[cb][12 + k] = [Op(bytes([0xB1, first + k, 0, 0, 1])), asm.ret()]
    part2 = {}
    for gname in names:
        i = next(k for k, g in enumerate(GIRLS) if g["name"] == gname)
        m = next(k for k, n in enumerate(model_names) if n.endswith(GIRL_MODEL[gname]))
        ga = sit_anim(m, "lounge" if kind == "lounge" else GIRL_SIT[gname].get(kind))
        hide, end = asm.nop(), asm.nop()
        my = gs
        if (place, gname) in GIRL_SEAT:
            x, y = GIRL_SEAT[(place, gname)]
            t = _find_near(mesh, x, y, (place, gname))
            my = (x, y, mesh.height(t, x, y) + num(SEATS[place]["girl"][4]), t)
        tier_acts = {}
        extra = GIRL_EXTRA.get(gname, {})
        if extra:
            loader.models[m] = ModelLoader.with_anims(loader.models[m],
                                                      [a for a in extra.values() if a not in ModelLoader.anims(loader.models[m])])
        seated = asm.nop()
        standing = []
        if gname in STAND_ON_THIRD:                  # third date: standing close to him from the start
            an = ModelLoader.anims(loader.models[m])
            st = an.index(extra["stand"])
            nx, ny, nt = _near(mesh, cs, my)
            standing = [asm.if_byte(HB_AFFECTION[i], ">=", TIERS[1], seated),
                        hb._xyzi(nx, ny, mesh.height(nt, nx, ny), nt),
                        Op(bytes([0xB3, 0, _dir_to(cs[0] - nx, cs[1] - ny)])), Op(bytes([0xA2, st, 1])),
                        Op(bytes([0xAE, st, 1])), hb._visi(1), asm.goto(end)]
        scripts[model_ent[m]] = {0: [Op(bytes([0xA1, m])), asm.if_byte(DATE_GIRL, "==", i + 1, hide)] + standing
                                 + [seated, hb._xyzi(*my), Op(bytes([0xB3, 0, gdir])), Op(bytes([0xA2, ga, 1])),
                                    Op(bytes([0xAE, ga, 1])), hb._visi(1), asm.goto(end), hide, hb._visi(0),
                                    end, asm.ret(), asm.ret()],
                                 3: [hb._visi(0), asm.ret()]}
        if extra:
            an = ModelLoader.anims(loader.models[m])
            st = an.index(extra["stand"])
            me = model_ent[m]
            # stands up and walks over to Cloud (MOVE when the straight way is all floor, else she
            # is simply put there: a MOVE that can't get through would never end), then faces him
            tx, ty = cs[0] + (my[0] - cs[0]) * WALK_TO, cs[1] + (my[1] - cs[1]) * WALK_TO
            path = all(mesh.find(my[0] + (tx - my[0]) * k / 20, my[1] + (ty - my[1]) * k / 20) is not None
                       for k in range(21))
            tt = mesh.find(round(tx), round(ty))
            k = 0
            while tt is None and k < 50:              # (the capsule: the gangway between) nearest floor towards him
                k += 1
                tx, ty = tx + (cs[0] - tx) * 0.05, ty + (cs[1] - ty) * 0.05
                tt = mesh.find(round(tx), round(ty))
            if path:
                go = [hb._move(round(tx), round(ty))]
            else:
                assert tt is not None, (place, gname, tx, ty)
                go = [hb._xyzi(round(tx), round(ty), mesh.height(tt, round(tx), round(ty)), tt)]
            scripts[me][9] = [Op(bytes([0xA2, st, 1])), Op(bytes([0xAE, st, 1])), hb._w(10)] + go \
                + [hb._tura(model_ent[0]), asm.ret()]
            scripts[me][12] = [hb._tura(model_ent[0]), asm.ret()]                                    # looks at him
            tier_acts = {"stand": [hb._req(me, 9)], "look": [hb._req(me, 12), hb._w(15)]}
            if "slap" in extra:
                sl = an.index(extra["slap"])
                scripts[me][10] = [Op(bytes([0xBC, sl, 0, SLAP_HIT, 1])), Op(b"\xAC"),                # the slap
                                   Op(bytes([0xF1, 0]) + SLAP_SOUND.to_bytes(2, "little") + b"\x40"),
                                   Op(bytes([0xBC, sl, SLAP_HIT, SLAP_END, 1])), Op(b"\xAC"),
                                   Op(bytes([0xA2, st, 1])), Op(bytes([0xAE, st, 1])), asm.ret()]
                tier_acts["slap"] = [hb._req(me, 10), hb._w(10)]
            if "kneel" in extra:                                                                 # kneels, bowed
                kn = an.index(extra["kneel"])
                scripts[me][11] = [Op(bytes([0xA2, kn, 1])), Op(bytes([0xAE, kn, 1])), asm.ret()]
                tier_acts["kneel"] = [hb._req(me, 11), hb._w(20)]
        # (user) part two in the place's position: her undressed copy (a second model and entity, or an
        # unused party model's slot at 16 models), at part two's spot, slot 4 placed + slow pose, 5 slow,
        # 6 fast, 8 held (frame 0)
        hanims = _pose_anims(place, gname)
        bare_entry = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[m], BARE[gname],
                                                                 model_names[m][:-5] + "_b.char"), hanims)
        gb, ge = slot(bare_entry, "%sb" % gname.lower()[:7])
        scripts[ge] = {0: [Op(bytes([0xA1, gb])), hb._visi(0), asm.ret(), asm.ret()]}
        ka = [len(ModelLoader.anims(loader.models[gb])) - 2 + k for k in range(2)]
        gface = (pdir + TURNED[POSITION[place]]) % 256
        scripts[ge][4] = [hb._xyzi(*spot), Op(bytes([0xB3, 0, gface])), hb._visi(1),
                          Op(bytes([0xA2, ka[0], 1])), Op(bytes([0xAE, ka[0], 1])), asm.ret()]
        for k, a_ in enumerate(ka):
            scripts[ge][5 + k] = [Op(bytes([0xA2, a_, 1])), Op(bytes([0xAE, a_, 1])), asm.ret()]
        scripts[ge][8] = [Op(bytes([0xA2, ka[0], 1])), hb._canm(ka[0], 0, 0), asm.ret()]
        acts = {"stop": [hb._req(cb, 12), hb._req(ge, 8)],
                "go": [hb._req(cb, 4), hb._req(ge, 5)],            # carry on at the first pace
                "fast": [hb._req(cb, 5), hb._req(ge, 6)]}
        part2[i] = (tier_acts, [hb._w(10), Op(hb.FADE_OUT), Op(b"\x6C"), hb._req(model_ent[0], 3), hb._req(model_ent[m], 3),
                                hb._req(cb, 3), hb._req(cb, 4), hb._req(ge, 4),
                                Op(bytes([0xF2, 0, 0, 0, 0x10, DATES[gname]["part2_music"]]) + bytes(8)),
                                Op(hb.FADE_IN), Op(b"\x6C"), hb._w(30)], acts)
    for e, m in chars.items():                   # everyone else: hidden
        if e not in scripts:
            scripts[e] = {0: [Op(bytes([0xA1, m])), hb._visi(0), asm.ret(), asm.ret()]}
    for keep in KEEP.get(place, ()):
        e = sec.entity_index(keep)
        assert e not in scripts and e not in chars, keep
        scripts[e] = {k: sec.script_ops(e, k) for k in (0, 1)}
    for to, frm in KEEP_AS.get(place, {}).items():   # (another entity's scripts, moved: frm is entity 0)
        e, src = sec.entity_index(to), sec.entity_index(frm)
        assert e not in scripts and e not in chars and src not in chars, (to, frm)
        scripts[e] = {k: sec.script_ops(src, k) for k in (0, 1)}
        for k in (0, 1):                             # (the wave's main ends in a goto: never reached)
            if scripts[e][k][-1].op != 0x00:
                scripts[e][k] = scripts[e][k] + [asm.ret()]
    assert 0 not in chars, "entity 0 has a model"
    init = [asm.ret()]
    if place == "capsule":                       # space through the window
        init = [Op(b"\xE0\x00\x01\x00"), Op(b"\xE1\x00\x02\x00"), asm.ret()]   # BGON 1, BGOFF 2
    main = [hb._uc(1), hb._menu(1)]
    for gname in names:
        i = next(k for k, g in enumerate(GIRLS) if g["name"] == gname)
        d = DATES[gname]
        nxt = asm.nop()
        main += [asm.if_byte(DATE_GIRL, "==", i + 1, nxt),
                 Op(bytes([0xF2, 0, 0, 0, 0x10, d["music"][place]]) + bytes(8)), hb._w(20)]
        main += _date(sec, ctx, place, i, GIRLS[i], d, part2[i]) + [nxt]
    # no girl (e.g. debug travel): back to the first girl's spot
    g0 = GIRLS[next(k for k, g in enumerate(GIRLS) if g["name"] == names[0])]
    rx, ry, rt, rd = _return_spot(ctx, g0)
    main += [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(g0["field"]), rx, ry, rt, rd), asm.ret()]
    scripts[0] = {0: init + main}
    _blank(sec, scripts)
    if place in TILES_BACK:
        from ff7.background import Background
        bg = Background(f.section("background"))
        tiles = list(bg.tiles())
        far = next(t for t in tiles if t._get("<H", 24) == 4094)._get("<I", 38)
        moved = 0
        for t in tiles:
            if t._get("<H", 24) < 4093:
                t._set("<H", 24, 4093)
                t._set("<I", 38, far - 1)
                moved += 1
        assert moved == 47, moved
        f.set_section("background", bg.build())
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    if not mesh.contains(cs[3], cs[0], cs[1]):       # (a lounger off the sand) arrive on its nearest floor
        t = mesh.tris[cs[3]]
        ax, ay = round(sum(v[0] for v in t) / 3), round(sum(v[1] for v in t) / 3)
        assert mesh.contains(cs[3], ax, ay), (name, ax, ay)
        cs = (ax, ay, mesh.height(cs[3], ax, ay), cs[3])
    return cs, cdir


def _offer(ctx, i, g, arrive, group):
    """Her world talk: "Just chat." / "Ask her on a date." first."""
    hb = _hb()
    field = g["field"]
    sec = Script.parse(ctx.field(field).sections[0])
    ent = sec.entity_index(g.get("reuse") or "hb%02d" % i)
    talk = sec.script_ops(ent, 1)
    assert [o.op for o in talk[:3]] == [0x33, 0x35, 0x24], talk[:3]     # UC 01, PTURA, WAIT
    rest = talk[3]
    d = DATES[g["name"]]
    her = lambda t: d.get("speaker", g["name"]) + "\n" + t
    ops = []
    ask, first = hb._ask(sec, her(d["greet"]), ["Just chat.", "Ask her on a date."])
    ops += ask + [asm.if_byte(CHOICE, "!=", first, rest)]                # chat: the usual talk
    ask, first = hb._ask(sec, her(d["where"]), [PLACE_NAMES[p] for p in PLACES] + ["Never mind."])
    ops += ask
    never = asm.nop()
    for k, p in enumerate(PLACES):
        nxt = asm.nop()
        (x, y, z, tri), adir = arrive[p]
        ops += [asm.if_byte(CHOICE, "==", first + k, nxt), asm.setbyte(DATE_GIRL, i + 1), hb._uc(0),
                asm.mapjump(ctx.maplist.index(FIELDS[(p, group)]), x, y, tri, adir), asm.ret(), nxt]
    ops += [never, hb._uc(0), asm.ret()]
    sec.insert_after(talk[2], ops)
    ctx.field(field).sections[0] = sec.build()


def _pose_anims(place, gname):
    """(user) The anims of the place's position (`POSITION`): [slow, fast] for girl gname (her
    retargeted copies: 670 prefix + position letter + speed; "head": 676's copies moved onto his
    spot, Y + her prefix's letter; "finisher": 672's R) or for bare Cloud (gname None: ZN...)."""
    mv = importlib.import_module("670_movie")
    pos = POSITION[place]
    letter = {"finisher": "R"}.get(pos) or chr(ord("A") + [p["name"] for p in mv.POSITIONS].index(pos))
    if gname is None:
        return ["ZN%s%d.tor" % (letter, s_) for s_ in (SPEED, SPEED_FAST)]
    prefix = next(g["prefix"] for g in MG.GIRLS if g["key"] == gname.lower())
    if pos == "head":
        prefix = "Y" + prefix[1]
    return ["%s%s%d.tor" % (prefix, letter, s_) for s_ in (SPEED, SPEED_FAST)]


def _lounge(ctx, name, hrc, stand):
    """(user) Lounging on a beach lounger (`name`.a): from the standing pose, each leg swung forward
    to level (straight: the knee stays as it was), the upper body (the pelvis bone and all above it)
    leant back LOUNGE_BACK about the root, the hip joints LEDGE_SEAT above the root's floor."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    ends = lambda W: fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
    F = ends(W)
    side = [1.0, 0.0, 0.0]
    ahead = lambda p: -p[2]                          # field models face -z

    def turned(W, bones, angle, test):
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(side, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(ends(M)):
                return M
        raise AssertionError((name, sorted(bones)))
    upper, grow = {"hip"}, True                      # the pelvis bone and everything hanging from it
    while grow:
        grow = False
        for b in sk:
            if b[1] in upper and b[0] not in upper:
                upper.add(b[0])
                grow = True
    for s_ in "lr":
        knee0 = F[I(s_ + "_femur")][2]
        legs = {b for b in names if b.startswith(s_ + "_") and b[2:] in ("femur", "tibia", "foot")}
        W = turned(W, legs, 90, lambda E: ahead(E[I(s_ + "_femur")][2]) > ahead(knee0) + 1)
    head0 = F[I("head")][2]
    W = turned(W, upper, LOUNGE_BACK, lambda E: ahead(E[I("head")][2]) < ahead(head0) - 1)
    E = ends(W)
    for s_ in "lr":
        shin = [E[I(s_ + "_tibia")][2][k] - E[I(s_ + "_femur")][1][k] for k in range(3)]
        assert abs(shin[1]) < 0.25 * math.hypot(*shin), (name, s_, shin)                  # legs level
    hip_y = max(E[I(s_ + "_femur")][1][1] for s_ in "lr")
    root = [root[0], root[1] - hip_y - LEDGE_SEAT, root[2]]
    base.frames = [(rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, W))]
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


def _ledge(ctx, name, hrc, stand, bench=False):
    """Sitting on a ledge (`name`.a): from the standing pose, each thigh swung forward to
    level (the knee bent back 90, so the shin hangs straight down and the foot stays as it
    was), the arms LEDGE_ARMS forward, the hip joints LEDGE_SEAT above the root's floor."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]                    # y down
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    ends = lambda W, r=root: fa.forward(sk, rr, r, fa.local_rotations(sk, rr, W))
    F = ends(W)
    fwd = [0.0, 0.0, -1.0]                           # field models face -z (the toes splay out: not them)
    side = [1.0, 0.0, 0.0]
    ahead = lambda p: p[0] * fwd[0] + p[2] * fwd[2]

    def turned(W, bones, angle, test):
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(side, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(ends(M)):
                return M
        raise AssertionError((name, bones))
    for s in "lr":
        knee0 = F[I(s + "_femur")][2]
        W = turned(W, {s + "_femur", s + "_tibia", s + "_foot"}, 90,
                   lambda E: ahead(E[I(s + "_femur")][2]) > ahead(knee0) + 1)          # thigh forward to level
        k = ends(W)[I(s + "_femur")][2]
        W = turned(W, {s + "_tibia", s + "_foot"}, 90,
                   lambda E: E[I(s + "_tibia")][2][1] > k[1] + 1)                       # shin back down (y down)
        hand0 = ends(W)[I(s + "_hand")][2]
        W = turned(W, {s + "_uparm", s + "_foarm", s + "_hand"}, LEDGE_ARMS,
                   lambda E: ahead(E[I(s + "_hand")][2]) > ahead(hand0) + 0.5)
    E = ends(W)
    for s in "lr":
        thigh = [E[I(s + "_femur")][2][k] - E[I(s + "_femur")][1][k] for k in range(3)]
        assert abs(thigh[1]) < 0.2 * math.hypot(*thigh) and abs(thigh[0]) < 0.5 * math.hypot(*thigh), \
            (name, s, thigh)                                                            # level, ahead
    if bench:                                        # feet on the floor (ankles where she stood)
        drop = max(E[I(s + "_tibia")][2][1] for s in "lr") - max(F[I(s + "_tibia")][2][1] for s in "lr")
        root = [root[0], root[1] - drop, root[2]]
    else:
        hip_y = max(E[I(s + "_femur")][1][1] for s in "lr")
        root = [root[0], root[1] - hip_y - LEDGE_SEAT, root[2]]                         # hips just above the floor
    base.frames = [(rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, W))]
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


def _bare_tifa(ctx):
    import struct
    hrc = ctx.char_file("aagb.hrc").decode("latin-1")
    assert hrc.count("1 AAGE") == 1 and hrc.count("1 AAGC") == 1
    hrc = hrc.replace("1 AAGE", "1 ZTFB").replace("1 AAGC", "1 ZTFC")
    for old, (rs, ply) in TIFA_THIGHS.items():
        assert hrc.count("1 %s" % old) == 1, old
        hrc = hrc.replace("1 %s" % old, "1 %s" % rs)
        r = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
        oldp = r.split("PLY=")[1][:4]
        ctx.char_file(rs.lower() + ".rsd", r.replace("PLY=%s." % oldp, "PLY=%s." % ply).encode("latin-1"))
        t = bytearray(ctx.char_file(oldp.lower() + ".p"))
        h = struct.unpack_from("<16I", t, 0)
        o_c = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6]
        k = 0
        for o in [o_c + 4 * i for i in range(h[7])] + [o_c + 4 * h[7] + 4 * i for i in range(h[9])]:
            if tuple(t[o:o + 3]) == THIGH_SKIN:
                t[o:o + 3] = bytes(TIFA_SKIN)
                k += 1
        assert k >= 8, (old, k)
        top = 0
        for i in range(h[3]):
            x, y, z = struct.unpack_from("<3f", t, 128 + 12 * i)
            if abs(z) < 0.1:
                struct.pack_into("<3f", t, 128 + 12 * i, x * THIGH_TOP, y * THIGH_TOP, z)
                top += 1
        assert top == 4, (old, top)
        ctx.char_file(ply.lower() + ".p", bytes(t))
    ctx.char_file("ztfa.hrc", hrc.encode("latin-1"))
    rsd = ctx.char_file("aagc.rsd").decode("latin-1")
    assert "PLY=AAGD." in rsd, rsd
    ctx.char_file("ztfc.rsd", rsd.replace("PLY=AAGD.", "PLY=ZTGC.").encode("latin-1"))
    d = bytearray(ctx.char_file("aagd.p"))
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nunk, nt, nc, npoly = h[3], h[4], h[5], h[6], h[7], h[9]
    o_c = 128 + 12 * nv + 12 * nn + 12 * nunk + 8 * nt
    n = 0
    for o in [o_c + 4 * i for i in range(nc)] + [o_c + 4 * nc + 4 * i for i in range(npoly)]:
        if tuple(d[o:o + 3]) in TIFA_SKIRT:
            d[o:o + 3] = bytes(TIFA_SKIN)
            n += 1
    assert n >= 30, n
    moved = 0
    for i in range(nv):
        x, y, z = struct.unpack_from("<3f", d, 128 + 12 * i)
        for rz, (fx, fy) in SKIRT_RINGS.items():
            if abs(z - rz) < 0.1:
                struct.pack_into("<3f", d, 128 + 12 * i, x * fx, y * fy, z)
                moved += 1
    assert moved == 24, moved
    ctx.char_file("ztgc.p", bytes(d))
    rsd = ctx.char_file("aage.rsd").decode("latin-1")
    assert "PLY=AAGF." in rsd, rsd
    ctx.char_file("ztfb.rsd", rsd.replace("PLY=AAGF.", "PLY=ZTGB.").encode("latin-1"))
    d = bytearray(ctx.char_file("aagf.p"))
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nunk, nt, nc, npoly = h[3], h[4], h[5], h[6], h[7], h[9]
    o_c = 128 + 12 * nv + 12 * nn + 12 * nunk + 8 * nt
    n = 0
    for o in [o_c + 4 * i for i in range(nc)] + [o_c + 4 * nc + 4 * i for i in range(npoly)]:
        if tuple(d[o:o + 3]) == TIFA_TOP:
            d[o:o + 3] = bytes(TIFA_SKIN)
            n += 1
    assert n >= 32, n
    ctx.char_file("ztgb.p", bytes(d))


# Aerith kneeling before standing Cloud ("head", user): upright on her knees (thighs straight
# down, shins and feet flat behind), arms KNEEL_ARMS forward to his thighs; her body above the
# knees tipped KNEEL_TILT forward and rocking KNEEL_ROCK more and back (head kept upright), in
# KNEEL_FRAMES (0.5 s) / KNEEL_FRAMES_FAST (Cloud's double speed). Her pelvis KNEEL_D in front of
# his (same XYZI, turned round, as the koala).
KNEEL_ARMS, KNEEL_TILT, KNEEL_ROCK, KNEEL_FRAMES, KNEEL_FRAMES_FAST = 40, 10, 10, 15, 8
# sitting back on her heels: thighs KNEEL_SIT forward of straight down (kneeling upright her head
# was at his chest); placed so her face is KNEEL_FACE in front of his pelvis
KNEEL_SIT, KNEEL_FACE = 75, 6.0     # (FACE 3 -> 9: a head width further away, then 7.5, 6.0: closer, user)
KNEEL_LOOK = 35                       # her "look up" poses (zdkc, zdkb): chin up this much (user)
BOW, BOW_HEAD = 40, 25                # Aerith's bow on her third date (zdkd: user)


def _kneel(ctx, name, hrc, stand, nframes, look=0, bow=None):
    """bow: a still bow (one frame where she is, no offset): above the knees tipped `bow`
    forward, the head lowered BOW_HEAD more."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    rr, rp, rots = fa.Anim(ctx.char_file(stand)).frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    fk = lambda W, r=root: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    ends = lambda W: {names[i]: e for i, (_, _, e) in enumerate(fk(W))}
    side = [1.0, 0.0, 0.0]

    def turned(W, bones, angle, test):
        e0 = ends(W)
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(side, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(e0, ends(M)):
                return M
        raise AssertionError((name, sorted(bones), angle))
    for s in "lr":
        W = turned(W, {s + "_tibia", s + "_foot"}, 90,
                   lambda a, b: b[s + "_tibia"][2] > a[s + "_tibia"][2] + 1)        # shin back (she faces -z)
        W = turned(W, {s + "_foot"}, 90, lambda a, b: b[s + "_foot"][2] > a[s + "_foot"][2] + 0.5)   # foot flat
        W = turned(W, {s + "_femur"}, KNEEL_SIT, lambda a, b: b[s + "_femur"][2] < a[s + "_femur"][2] - 1)   # on her heels
        W = turned(W, {s + "_uparm", s + "_foarm", s + "_hand"}, KNEEL_ARMS,
                   lambda a, b: b[s + "_hand"][2] < a[s + "_hand"][2] - 0.5)
    F = fk(W)
    knee_y = max(F[I(s + "_femur")][2][1] for s in "lr")
    root = [root[0], root[1] - knee_y - 0.5, root[2]]                                # knees on the floor
    F = fk(W, root)
    knee = [(F[I("l_femur")][2][k] + F[I("r_femur")][2][k]) / 2 for k in range(3)]
    keep = {I(s + n) for s in "lr" for n in ("_tibia", "_foot")}
    head = W[I("head")]
    if look:                                          # chin up: the head end moves up (y down)
        up_ = [fa._mul(fa.axis_angle(side, sg * look), head) for sg in (1, -1)]
        test = lambda M: fk([M if i == I("head") else m for i, m in enumerate(W)], root)[I("head")][2][1]
        head = min(up_, key=test)
    tip = 1 if fk([fa._mul(fa.axis_angle(side, 5), m) if i not in keep else m for i, m in enumerate(W)],
                  root)[I("head")][2][2] < F[I("head")][2][2] else -1               # + tip: head forward
    E0 = fk([fa._mul(fa.axis_angle(side, tip * KNEEL_TILT), m) if i not in keep else m for i, m in enumerate(W)],
            root)
    lift = fa._vec(fa.axis_angle(side, tip * KNEEL_TILT), [root[k] - knee[k] for k in range(3)])
    head_z = E0[I("head")][1][2] - (knee[2] + lift[2])          # her head (neck) ahead of the root, frame 0
    dist = KNEEL_FACE - head_z                                    # her root's z: face KNEEL_FACE before his pelvis
    frames = []
    for t in range(nframes):
        a = tip * (KNEEL_TILT + KNEEL_ROCK * (1 - math.cos(2 * math.pi * t / nframes)) / 2)
        if bow is not None:
            a = tip * bow
        R = fa.axis_angle(side, a)
        rel = fa._vec(R, [root[k] - knee[k] for k in range(3)])
        rt = [knee[k] + rel[k] for k in range(3)]
        Wt = [m if i in keep else fa._mul(R, m) for i, m in enumerate(W)]
        Wt[I("head")] = head                                                       # upright
        if bow is not None:
            Wt[I("head")] = fa._mul(fa.axis_angle(side, tip * (bow + BOW_HEAD)), W[I("head")])   # bowed
        E = fk(Wt, rt)
        for s in "lr":
            assert abs(E[I(s + "_femur")][2][1]) < 0.8, (name, t, s)               # knees on the floor
        if bow is None:
            rt = [rt[0], rt[1], rt[2] - (knee[2] + lift[2]) + dist]                 # in front of him
        frames.append((rr, [rt[0], -rt[1], rt[2]], fa.local_rotations(sk, rr, Wt)))
    base = fa.Anim(ctx.char_file(stand))
    base.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


# Scarlet without her skirt (user: "without the bottom 2 large sections of her red dress"): her
# AMCC skeleton (so her anims work) with the skirt bones' parts dropped: both tiers (s1 hip to
# knee, s2 knee to ankle), front and back, each side. Not used by a scene yet.
SCARLET_BARE = "ZSCA.HRC"
SCARLET_SKIRT = ["AMHA", "AMHC", "AMHE", "AMIA", "AMJC", "AMJE", "ANAA", "ANAC"]   # l/r f_s1 f_s2 r_s1 r_s2


def _scarlet_bare(ctx):
    hrc = ctx.char_file("amcc.hrc").decode("latin-1")
    for part in SCARLET_SKIRT:
        assert hrc.count("1 %s\r\n" % part) == 1, part
        hrc = hrc.replace("1 %s\r\n" % part, "0\r\n")
    ctx.char_file(SCARLET_BARE.lower(), hrc.encode("latin-1"))


# Scarlet's part two (user): standing in front of Cloud facing the same way, torso leaning
# WALL_LEAN forward, arms straight out WALL_ARMS (against a wall), right thigh raised WALL_KNEE_UP
# with the knee bent 90, head turned WALL_LOOK to her left (and lifted WALL_HEAD_UP); her pelvis
# moves back and forth with his thrust (ZCTE), pivoting on her standing (left) ankle, its back
# WALL_GAP in front of his pelvis.
WALL_LEAN, WALL_ARMS, WALL_KNEE_UP, WALL_LOOK, WALL_HEAD_UP, WALL_GAP = 45, 95, 80, 45, 30, 3.5


def _wall(ctx, name, hrc, stand, cloud="stand"):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    fk = lambda W, r=root: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    ends = lambda W: {names[i]: e for i, (_, _, e) in enumerate(fk(W))}
    side, up = [1.0, 0.0, 0.0], [0.0, -1.0, 0.0]
    cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]

    def turned(W, bones, axis, angle, test):
        e0 = ends(W)
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(axis, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(e0, ends(M)):
                return M
        raise AssertionError((name, sorted(bones), angle))
    legs = {n for n in names if n[:2] in ("l_", "r_") and not any(k in n for k in ("chest", "collar", "arm", "hand"))}
    upper = set(names) - legs
    h = I("head")
    face_local = fa._vec(fa._t(W[h]), [0.0, 0.0, -1.0])            # she faces -z standing
    ankle0 = ends(W)["l_tibia"]
    W = turned(W, upper, side, WALL_LEAN, lambda a, b: b["head"][2] < a["head"][2] - 1)          # lean forward
    W = turned(W, {"head"}, side, WALL_HEAD_UP, lambda a, b: b["head"][1] < a["head"][1] - 0.2)  # chin up
    F = fk(W)
    neck = unit([F[h][2][k] - F[h][1][k] for k in range(3)])
    looks = [[fa._mul(fa.axis_angle(neck, sg * WALL_LOOK), m) if i == h else m for i, m in enumerate(W)]
             for sg in (1, -1)]
    W = max(looks, key=lambda M: fa._vec(M[h], face_local)[0])      # her left = +x
    for s in "lr":
        arm = {s + "_uparm", s + "_foarm", s + "_hand"}
        W = turned(W, arm, side, WALL_ARMS, lambda a, b: b[s + "_hand"][2] < a[s + "_hand"][2] - 1)
    W = turned(W, {"r_femur", "r_tibia", "r_foot"}, side, WALL_KNEE_UP,
               lambda a, b: b["r_femur"][2] < a["r_femur"][2] - 1)                              # right knee up
    F = fk(W)
    thigh = [F[I("r_femur")][2][k] - F[I("r_femur")][1][k] for k in range(3)]
    W = turned(W, {"r_tibia", "r_foot"}, unit(cross(thigh, up)), 90,
               lambda a, b: b["r_tibia"][1] > a["r_tibia"][1] + 1)                              # shin down
    his = fa.Anim(ctx.char_file(_hb().CLOUD_BED[cloud].split(".")[0].lower() + ".a"))
    hz0 = his.frames[0][1][2]
    F = fk(W)
    # frame 0: standing ankle back at its height, her pelvis WALL_GAP in front of his (same facing)
    r0 = [root[0], root[1] + ankle0[1] - F[I("l_tibia")][2][1], root[2] + (hz0 - WALL_GAP) - F[I("hip")][1][2]]
    F = fk(W, r0)
    ank, pel = F[I("l_tibia")][2], F[I("hip")][1]
    height = ank[1] - pel[1]                                       # y down: the pelvis above the ankle
    keep = {I("l_foot")}
    frames = []
    for _, hp, _ in his.frames:
        d = hp[2] - hz0                                            # his pelvis' move along z
        a = math.degrees(math.asin(max(-1.0, min(1.0, abs(d) / height))))
        R = fa.axis_angle(side, a)
        if (fa._vec(R, [pel[k] - ank[k] for k in range(3)])[2] - (pel[2] - ank[2])) * d < 0:
            R = fa.axis_angle(side, -a)                            # her pelvis follows his
        Wt = [m if i in keep else fa._mul(R, m) for i, m in enumerate(W)]
        rel = fa._vec(R, [r0[k] - ank[k] for k in range(3)])
        rt = [ank[k] + rel[k] for k in range(3)]
        E = fk(Wt, rt)
        assert math.dist(E[I("l_tibia")][2], ank) < 0.05                # standing ankle planted
        frames.append((rr, [rt[0], -rt[1], rt[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


# bare Elena (user: her upper legs skin coloured and slightly thinner than her lower legs):
# EVFE with the thigh parts (EVJC/EWAC: navy trousers 35,10,10) in her skin (149,178,255,
# her face's) and scaled ELENA_THIGH across (0.85: the knee ring 1.39/1.64 < the shin top 1.64/1.93)
ELENA_BARE = "ZELA.HRC"
ELENA_THIGHS = {"EVJC": ("ZELB", "ZEMB"), "EWAC": ("ZELC", "ZEMC")}
ELENA_SUIT, ELENA_SKIN, ELENA_THIGH = (35, 10, 10), (149, 178, 255), 0.85


def _bare_elena(ctx):
    import struct
    hrc = ctx.char_file("evfe.hrc").decode("latin-1")
    for old, (rs, ply) in ELENA_THIGHS.items():
        assert hrc.count("1 %s" % old) == 1, old
        hrc = hrc.replace("1 %s" % old, "1 %s" % rs)
        r = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
        oldp = r.split("PLY=")[1][:4]
        ctx.char_file(rs.lower() + ".rsd", r.replace("PLY=%s." % oldp, "PLY=%s." % ply).encode("latin-1"))
        d = bytearray(ctx.char_file(oldp.lower() + ".p"))
        h = struct.unpack_from("<16I", d, 0)
        o_c = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6]
        n = 0
        for o in [o_c + 4 * i for i in range(h[7])] + [o_c + 4 * h[7] + 4 * i for i in range(h[9])]:
            if tuple(d[o:o + 3]) == ELENA_SUIT:
                d[o:o + 3] = bytes(ELENA_SKIN)
                n += 1
        assert n >= 10, (old, n)
        for i in range(h[3]):
            x, y, z = struct.unpack_from("<3f", d, 128 + 12 * i)
            struct.pack_into("<3f", d, 128 + 12 * i, x * ELENA_THIGH, y * ELENA_THIGH, z)
        ctx.char_file(ply.lower() + ".p", bytes(d))
    ctx.char_file(ELENA_BARE.lower(), hrc.encode("latin-1"))


# Cloud's spank (Elena's part two, ZCTP): (user) his right arm straight, swung at the shoulder from
# out (SWING_OUT back about the vertical, SWING_RAISE up) quickly in onto her (SWING_IN frames),
# the hit at the middle frame; SEATED_FRAMES = 0.5 s
SEATED_FRAMES = 15
SWING_OUT, SWING_RAISE, SWING_IN = 60, 20, 3   # (user) straight arm: out this far, raised, in over 3 frames


def _find_near(mesh, x, y, what):
    """The triangle under (x, y), else the nearest one within NEAR_FLOOR (its plane gives the height)."""
    t = mesh.find(x, y)
    if t is not None:
        return t
    for r in range(2, NEAR_FLOOR + 1, 2):
        for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, r), (r, -r), (-r, -r)):
            t = mesh.find(x + dx, y + dy)
            if t is not None:
                return t
    raise AssertionError(("off the floor", what, x, y))


def _align(fa, a, b):
    """The smallest rotation turning direction a into b."""
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]
    a, b = unit(a), unit(b)
    ax = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    s_ = math.sqrt(sum(c * c for c in ax))
    d = sum(a[k] * b[k] for k in range(3))
    return fa.axis_angle(ax, math.degrees(math.atan2(s_, d))) if s_ > 1e-9 else fa.euler_matrix(0, 0, 0)

# (user) Elena's part two, standing, in every place: she on all fours (ZDEF, held: thighs
# straight down, shins flat behind, torso FOURS_PITCH head-up, arms straight and angled forward
# so hands and knees rest on his floor, head FOURS_LOOK up), her hips (at least SPANK_SIDE_MIN) to his right and
# SPANK_FRONT in front of him (he stands behind and to her side, facing her way; her place is
# in her anim, same XYZI and DIR); Cloud (ZCTP) beside her on one knee (user; was standing,
# leaning down: see _elena_fours), his right arm straight, swung in at the shoulder onto the top
# of her behind at the middle frame (SWING_*; her hips as far right as it reaches). Part three:
# Tifa's koala hug on her (ZDEK), turned round inside the anim (both keep one DIR).
FOURS_LOOK, FOURS_PAD, SPANK_SIDE_MIN, SPANK_FRONT, FOURS_BUTT = 25, 0.6, 3.0, 7.0, 2.0
FOURS_PITCH = 15
KNEEL_THIGH, KNEEL_LEAN, KNEEL_PAD = 110, 0, 0.5    # (user) Cloud on one knee: front thigh 20 above level;
                                                    # upright (user, since: closer to her; leaning 20 put her
                                                    # hips 12.2 to his right, upright 9.9: the straight arm
                                                    # reaches less far sideways from a higher, further-back
                                                    # shoulder); the back knee's centre above the floor


def _elena_fours(ctx):
    """ZDEF (Elena on all fours) and ZCTP (Cloud on one knee beside her, spanking); see SPANK_*, KNEEL_*."""
    from ff7 import fieldanim as fa
    csk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    CI = [b[0] for b in csk].index
    cn = [b[0] for b in csk]
    side = [1.0, 0.0, 0.0]
    # (user) Cloud on one knee: his standing pose (ACFE) with the left (back) thigh straight down,
    # its shin flat behind on the floor; the right (front) thigh raised KNEEL_THIGH forward, its
    # shin angled back down until the ankle reaches the floor (his shins are longer than his
    # thighs: a level thigh and an upright shin would sink the foot), the foot as standing (flat);
    # the root lowered so the left knee rests where his standing ankles were; leaning KNEEL_LEAN
    cbase = fa.Anim(ctx.char_file("zcte.a"))            # (a 15-frame container: frames replaced)
    crr, crp, crots = fa.Anim(ctx.char_file("acfe.a")).frames[0]
    r0 = [crp[0], -crp[1], crp[2]]
    cfk = lambda W, r: fa.forward(csk, crr, list(r), fa.local_rotations(csk, crr, W))
    cend = lambda W, n, r=r0: cfk(W, r)[CI(n)][2]
    CW = [m for m, _, _ in fa.forward(csk, crr, r0, crots)]
    floor = max(cend(CW, s + n)[1] for s in "lr" for n in ("_tibia", "_foot"))      # his standing floor (y down)
    ankle = max(cend(CW, s + "_tibia")[1] for s in "lr")                            # his standing ankles
    rot = lambda W, bones, a: [fa._mul(fa.axis_angle(side, a), m) if cn[i] in bones else m for i, m in enumerate(W)]
    fwd = 1 if cend(rot(CW, {"r_femur", "r_tibia", "r_foot"}, 10), "r_femur")[2] < cend(CW, "r_femur")[2] else -1
    lt = CI("l_tibia")                                                              # back shin flat behind
    CW[lt] = fa._mul(_align(fa, fa._vec(CW[lt], [0, 0, -1]), [0.0, 0.0, 1.0]), CW[lt])
    CW[CI("l_foot")] = CW[lt]
    assert cend(CW, "l_tibia")[2] > cend(CW, "l_femur")[2] + 5, "back shin not behind"
    foot0 = CW[CI("r_foot")]
    CW = rot(CW, {"r_femur", "r_tibia", "r_foot"}, fwd * KNEEL_THIGH)                # front thigh up

    def shin(a):                                     # the front shin turned back down by a, foot flat
        M = rot(CW, {"r_tibia"}, -fwd * a)
        M[CI("r_foot")] = foot0
        return M
    knee_y = floor - KNEEL_PAD                                                      # the back knee's centre
    miss = lambda a: cend(shin(a), "r_tibia")[1] - cend(CW, "l_femur")[1] - (ankle - knee_y)   # ankle as standing
    lo, hi = 0.0, float(KNEEL_THIGH)
    assert miss(lo) < 0 < miss(hi), (miss(lo), miss(hi))
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if miss(mid) < 0 else (lo, mid)
    CW = shin(lo)
    croot = [r0[0], r0[1] + knee_y - cend(CW, "l_femur")[1], r0[2]]                # back knee on the floor
    for n, y in (("l_femur", knee_y), ("l_tibia", knee_y), ("r_tibia", ankle)):
        assert abs(cend(CW, n, croot)[1] - y) < 0.3, (n, cend(CW, n, croot), y)
    assert cend(CW, "r_femur", croot)[2] < cend(CW, "l_femur", croot)[2] - 4, "front knee not forward"
    crp = [croot[0], -croot[1], croot[2]]
    cfk_ = cfk
    cfk = lambda W, r=croot: cfk_(W, r)
    # her pose
    sk = fa.skeleton(ctx.char_file("zela.hrc").decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    rr, rp, rots = fa.Anim(ctx.char_file("acfe.a")).frames[0]
    W = [m for m, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
    fk = lambda W, r=(0.0, 0.0, 0.0): fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    end = lambda W, n, r=(0.0, 0.0, 0.0): fk(W, r)[I(n)][2]
    legs = {s + n for s in "lr" for n in ("_hip", "_femur", "_tibia", "_foot")}
    arms = {s + n for s in "lr" for n in ("_uparm", "_foarm", "_hand")}
    upper = set(names) - legs

    def turned(W, bones, angle, test):
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(side, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(W, M):
                return M
        raise AssertionError((sorted(bones), angle))
    down = lambda W, bones: [fa._mul(_align(fa, fa._vec(m, [0, 0, -1]), [0.0, 1.0, 0.0]), m) if names[i] in bones
                             else m for i, m in enumerate(W)]
    W = turned(W, upper, 90, lambda a, b: end(b, "head")[2] < end(a, "head")[2] - 3)        # face down
    W = turned(W, {"head"}, FOURS_LOOK, lambda a, b: end(b, "head")[1] < end(a, "head")[1])   # looking ahead
    for s in "lr":                                                                          # shins flat behind
        W = turned(W, {s + "_tibia", s + "_foot"}, 90, lambda a, b: end(b, s + "_tibia")[2] > end(a, s + "_tibia")[2] + 1)
        W[I(s + "_foot")] = W[I(s + "_tibia")]

    # the upper body pitched FOURS_PITCH head-up (arms longer than thighs), then each arm
    # straight from the shoulder forward and down to the floor (hands ahead of the shoulders)
    probe = [fa._mul(fa.axis_angle(side, 5), m) if names[i] in upper else m for i, m in enumerate(W)]
    sense = 1 if end(probe, "head")[1] < end(W, "head")[1] else -1
    W = [fa._mul(fa.axis_angle(side, sense * FOURS_PITCH), m) if names[i] in upper else m for i, m in enumerate(W)]
    # his lean first: with a straight arm (user) his shoulder decides where she is
    cl_legs = {CI(s + n) for s in "lr" for n in ("_hip", "_femur", "_tibia", "_foot")}
    for sg in (1, -1):
        M = [fa._mul(fa.axis_angle(side, sg * KNEEL_LEAN), m) if i not in cl_legs else m for i, m in enumerate(CW)]
        if cfk(M)[CI("head")][2][2] < cfk(CW)[CI("head")][2][2]:
            break
    CW = M
    # her hips SPANK_FRONT ahead of him and as far to his right as his straight arm (shoulder to
    # fingertips) reaches the top of her behind (FOURS_BUTT above her pelvis, a little back)
    S = cfk(CW)[CI("r_uparm")][1]
    L = sum(csk[CI(n)][2] for n in ("r_uparm", "r_foarm", "r_hand"))
    knee = end(W, "l_femur")
    ry = floor - FOURS_PAD - knee[1]
    target = [None, ry - FOURS_BUTT, -SPANK_FRONT + 0.5]
    dx2 = L * L - (target[1] - S[1]) ** 2 - (target[2] - S[2]) ** 2
    assert dx2 > 0, ("ZCTP: her behind out of his reach", L, S, target)
    target[0] = S[0] - math.sqrt(dx2)                                                 # his right = -x
    r = [target[0], ry, -SPANK_FRONT]                                                 # her pelvis, in his space
    assert -r[0] >= SPANK_SIDE_MIN, ("ZCTP: she'd be inside him", r)
    F = fk(W, r)
    for s in "lr":
        L = sum(sk[I(s + n)][2] for n in ("_uparm", "_foarm", "_hand"))
        h = floor - FOURS_PAD - F[I(s + "_collar")][2][1]
        assert 0 < h < L, (s, h, L)
        d = [0.0, h, -math.sqrt(L * L - h * h)]
        for n in ("_uparm", "_foarm", "_hand"):
            W[I(s + n)] = fa._mul(_align(fa, fa._vec(W[I(s + n)], [0, 0, -1]), d), W[I(s + n)])
    F = fk(W, r)
    for n in ("l_femur", "r_femur", "l_hand", "r_hand", "l_tibia", "r_tibia"):
        assert abs(F[I(n)][2][1] - (floor - FOURS_PAD)) < 0.3, (n, F[I(n)][2][1], floor)   # on his floor
    assert F[I("head")][2][2] < r[2] - 5, "her head not forward"
    A = fa.Anim(ctx.char_file("acfe.a"))
    A.frames = [(rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, W))]
    ctx.char_file("zdef.a", A.build())
    # (user) his arm straight (shoulder, elbow, wrist, hand in one line) onto her at the hit, the
    # swing only at the shoulder: out (about the vertical, the hand going back) and raised, then
    # quickly in (SWING_IN frames) to the hit at the middle frame (the 'once' slap sound), and
    # back out slowly
    arm = {CI(n) for n in ("r_uparm", "r_foarm", "r_hand")}
    u = [target[k] - S[k] for k in range(3)]
    for n in ("r_uparm", "r_foarm", "r_hand"):
        CW[CI(n)] = fa._mul(_align(fa, fa._vec(CW[CI(n)], [0, 0, -1]), u), CW[CI(n)])
    hit = cend(CW, "r_hand", croot)
    assert math.dist(hit, target) < 0.3, ("ZCTP hand off her", hit, target)
    up = [0.0, -1.0, 0.0]
    fwd_ax = [0.0, 0.0, -1.0]
    turn = lambda W_, ax, a_: [fa._mul(fa.axis_angle(ax, a_), m) if i in arm else m for i, m in enumerate(W_)]
    out = SWING_OUT if cend(turn(CW, up, 10), "r_hand", croot)[2] > hit[2] else -SWING_OUT       # hand back
    lift = SWING_RAISE if cend(turn(CW, fwd_ax, 10), "r_hand", croot)[1] < hit[1] else -SWING_RAISE  # hand up
    mid = SEATED_FRAMES // 2
    frames, frames_r = [], []
    # ZCTR (the gondola, user): the same with his head turned HEAD_RIGHT to his right (-x)
    hsense = 1 if fa._vec(fa.axis_angle(up, 10), [0.0, 0.0, -1.0])[0] < 0 else -1
    for t in range(SEATED_FRAMES):
        if t <= mid - SWING_IN:
            k = 1.0
        elif t <= mid:
            k = (mid - t) / SWING_IN                                  # in, quickly
        else:
            q = (t - mid) / (SEATED_FRAMES - mid)                     # back out, eased
            k = q * q * (3 - 2 * q)
        Wt = turn(turn(CW, up, out * k), fwd_ax, lift * k)
        frames.append((crr, crp, fa.local_rotations(csk, crr, Wt)))
        Wt = list(Wt)
        Wt[CI("head")] = fa._mul(fa.axis_angle(up, hsense * HEAD_RIGHT), Wt[CI("head")])
        frames_r.append((crr, crp, fa.local_rotations(csk, crr, Wt)))
    cbase.frames = frames
    ctx.char_file("zctp.a", cbase.build())
    cbase.frames = frames_r
    ctx.char_file("zctr.a", cbase.build())


def _turn_round(ctx, name, hrc):
    """`name`.a turned 180 about the vertical: for a pose laid out facing Cloud (DIR + 128)
    played with his DIR."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    A = fa.Anim(ctx.char_file(name))
    Y = fa.axis_angle([0.0, -1.0, 0.0], 180)
    frames = []
    for rr, rp, rots in A.frames:
        W = [fa._mul(Y, m) for m, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
        frames.append((rr, [-rp[0], rp[1], -rp[2]], fa.local_rotations(sk, rr, W)))
    A.frames = frames
    ctx.char_file(name, A.build())


def _koala(ctx, name, hrc, stand):
    """Her koala hug on standing Cloud (one frame per ZCTH frame), as the user laid it out:
    leaning KOALA_LEAN onto him (head upright); arms raised KOALA_ARMS forward; each thigh
    raised KOALA_THIGH forward, then spread KOALA_SPREAD outward (about the vertical), then
    the knee bent KOALA_KNEE (the shin turned about the knee's own hinge axis, thigh x up).
    Her XYZI = his, DIR his + 128, so his model point (x, y, z) is her (-x, y, -z); her pelvis
    rides in front of his (bouncing KOALA_BOUNCE), and her upper body turns forward as her
    pelvis goes back, so her head keeps its place (user)."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    fk = lambda W, r=root: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    ends = lambda W: {names[i]: e for i, (_, _, e) in enumerate(fk(W))}
    side, up = [1.0, 0.0, 0.0], [0.0, -1.0, 0.0]      # she faces -z, y down
    cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]

    def turned(W, bones, axis, angle, test):
        e0 = ends(W)
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(axis, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            if test(e0, ends(M)):
                return M
        raise AssertionError((name, sorted(bones), angle))
    legs = {s + n for s in "lr" for n in ("_hip", "_femur", "_tibia", "_foot")}
    upper = set(names) - legs
    sense = 1 if KOALA_LEAN > 0 else -1              # > 0: she leans back; < 0: forward (onto him)
    W = turned(W, upper, side, abs(KOALA_LEAN), lambda a, b: sense * b["head"][2] > sense * a["head"][2] + 0.5)
    W = turned(W, {"head"}, side, abs(KOALA_LEAN),
               lambda a, b: sense * b["head"][2] < sense * a["head"][2] - 0.1)                       # head upright
    for s, out in (("l", 1), ("r", -1)):
        arm = {s + "_uparm", s + "_foarm", s + "_hand"}
        W = turned(W, arm, side, KOALA_ARMS, lambda a, b: b[s + "_hand"][2] < a[s + "_hand"][2] - 1)  # forward-up
        W = turned(W, arm, up, KOALA_ARMS_IN, lambda a, b: out * b[s + "_hand"][0] < out * a[s + "_hand"][0] - 0.2)
        leg = {s + "_femur", s + "_tibia", s + "_foot"}
        W = turned(W, leg, side, KOALA_THIGH, lambda a, b: b[s + "_femur"][2] < a[s + "_femur"][2] - 1)
        W = turned(W, leg, up, KOALA_SPREAD, lambda a, b: out * b[s + "_femur"][0] > out * a[s + "_femur"][0] + 0.5)
        F = fk(W)
        thigh = [F[I(s + "_femur")][2][k] - F[I(s + "_femur")][1][k] for k in range(3)]
        hinge = unit(cross(thigh, up))                                            # the knee's axis
        W = turned(W, {s + "_tibia", s + "_foot"}, hinge, KOALA_KNEE,
                   lambda a, b: b[s + "_tibia"][1] > a[s + "_tibia"][1] + 1)        # shin down (y down)
    # pelvis tipped up KOALA_PELVIS (user: "rotate her pelvis up a little more"): the pelvis
    # and both legs turn together, the knees going up; the chest keeps its angle
    lower = {"hip"} | legs
    W = turned(W, lower, side, KOALA_PELVIS,
               lambda a, b: b["l_femur"][1] < a["l_femur"][1] - 0.3 and b["r_femur"][1] < a["r_femur"][1] - 0.3)
    F = fk(W)
    for s in "lr":                                    # check: knee at 90
        th = [F[I(s + "_femur")][2][k] - F[I(s + "_femur")][1][k] for k in range(3)]
        sh = [F[I(s + "_tibia")][2][k] - F[I(s + "_tibia")][1][k] for k in range(3)]
        cosk = sum(th[k] * sh[k] for k in range(3)) / math.sqrt(sum(q * q for q in th) * sum(q * q for q in sh))
        assert abs(math.degrees(math.acos(cosk)) - KOALA_KNEE) < 3, (s, cosk)
    head0 = F[I("head")][2]
    pelvis0 = F[I("hip")][1]
    tilt = 1 if fk([fa._mul(fa.axis_angle(side, 5), m) if names[i] in upper else m
                    for i, m in enumerate(W)])[I("head")][2][2] < head0[2] else -1   # + this: head forward (-z)
    his = fa.Anim(ctx.char_file(_hb().CLOUD_BED["standk"].split(".")[0].lower() + ".a"))
    frames = []
    n = len(his.frames)
    r0 = None
    for t, (_, hp, _) in enumerate(his.frames):
        e = (1 - math.cos(2 * math.pi * t / n)) / 2
        hx, hy, hz = hp[0], -hp[1], hp[2]                                        # his pelvis (y down)
        px, py, pz = -hx, hy, -(hz - KOALA_FRONT)                                # in front of it, in her space
        r = [px, py - KOALA_UP - KOALA_BOUNCE * e, pz + KOALA_BACK]
        r0 = r0 or r
        back = r[2] - r0[2]                                                      # her pelvis back (+z) of frame 0
        length = head0[1] - pelvis0[1]
        a = math.degrees(math.asin(max(-1.0, min(1.0, back / abs(length))))) if length else 0.0
        Wt = [fa._mul(fa.axis_angle(side, tilt * a), m) if names[i] in upper else m for i, m in enumerate(W)]
        Wt[I("head")] = fa._mul(fa.axis_angle(side, tilt * KOALA_NOD * e), Wt[I("head")])   # nods forward as she rises
        frames.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


def apply(ctx):
    for anim, (hrc, stand) in BENCH.items():
        _ledge(ctx, anim, hrc, stand, bench=True)
    _bare_elena(ctx)
    _elena_fours(ctx)
    _bare_tifa(ctx)
    _koala(ctx, "ZDKT.tor", "ztfa.hrc", "abcd.a")
    _koala(ctx, "ZDEK.tor", "zela.hrc", "acfe.a")            # (user) Elena's part three: Tifa's hug
    _turn_round(ctx, "zdek.a", "zela.hrc")
    _scarlet_bare(ctx)
    _wall(ctx, "ZDSW.tor", "zsca.hrc", "anae.a")
    _wall(ctx, "ZDSX.tor", "zsca.hrc", "anae.a", "standf")      # with his double speed
    for anim, frames, look in (("ZDKA.tor", KNEEL_FRAMES, 0), ("ZDKC.tor", KNEEL_FRAMES, KNEEL_LOOK),
                               ("ZDKB.tor", KNEEL_FRAMES_FAST, 0)):    # fast: looking straight again (user)
        _kneel(ctx, anim, "auff.hrc", "avbf.a", frames, look)
    _kneel(ctx, "ZDKD.tor", "auff.hrc", "avbf.a", 1, bow=BOW)
    for group, names in enumerate(GROUPS):
        arrive = {p: _field(ctx, p, group, names) for p in PLACES}
        for gname in names:
            i = next(k for k, g in enumerate(GIRLS) if g["name"] == gname)
            _offer(ctx, i, GIRLS[i], arrive, group)

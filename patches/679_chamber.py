"""(user) The chamber: the loose group shoot's engine (`_loose_engine`, chamber mode) in the Ghost Hotel's
bedroom (data `_chamber.py`, poses `_chamber_poses.py`). The set: ghotin_2 copied under CD.FIELD, its script
blanked but the candles' flicker (entity `fire`, now `direct`) and the lightning (`thunder`, now `ad`; its
random number moved off temp (5,6), the shoot's slot data); models Cloud + one hidden. The girls' homes
(`HOMES`: by each bed's head standing, hands clasped high; at each bed's foot kneeling, hands behind her
back); Cloud's walk up to each (`_walks`: from WALK_FROM away to WALK_STOP in front of her, facing her);
each position's station on each bed (`_stations`: the pair's relative placement (the chamber's own poses,
672's, or the studio's) turned along the bed (DIR 0 / 128) with everyone on the bed top - or, for `floor`
positions, Cloud standing on the floor at the bed's foot - and Cloud the further from the camera)."""
import importlib
import math

import _chamber as CD
import _chamber_poses as CP
import _loose_engine as LE
from ff7 import triggers as tg
from ff7.camera import Camera
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Script

BEDS = [(-114, -28), (80, 166), (275, 361)]   # ghotin_2's beds (walkmesh): x range; y 63 (foot) .. 245 (head)
BED_Y, TOP = (63, 245), 59
HOMES = [("head", 0), ("head", 1), ("head", 2), ("foot", 0), ("foot", 1), ("foot", 2)]   # GR.ORDER's girls
HEAD_AT = (-30, 215)            # by the bed's head: x from the bed's left side, y
FOOT_AT = (-12, 32)             # at its foot: x from the bed's right side, y
WALK_FROM, WALK_STOP = 120, 28  # Cloud starts this far in front of her and stops this far
CAM_AT = (230, -150)            # the cameraman (the nearest floor), facing the beds
RAND_TEMP = 213                 # the lightning's random number (was (5,6))


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


def _floor_tri(mesh, x, y):
    t = mesh.find(round(x), round(y))
    if t is not None and abs(mesh.height(t, x, y)) < 2:
        return t
    return min((i for i in range(len(mesh.tris)) if max(abs(v[2]) for v in mesh.tris[i]) < 2),
               key=lambda i: math.dist(mesh.center(i)[:2], (x, y)))


def _bed_tri(mesh, b):
    x0, x1 = BEDS[b]
    return next(t for t in range(len(mesh.tris)) if mesh.contains(t, (x0 + x1) / 2, 150) and
                abs(mesh.height(t, (x0 + x1) / 2, 150) - TOP) < 2)


def _in_bed(p, b, margin=3):
    x0, x1 = BEDS[b]
    return x0 + margin <= p[0] <= x1 - margin and BED_Y[0] + margin <= p[1] <= BED_Y[1] - margin


def _home(k):
    kind, b = HOMES[k]
    x0, x1 = BEDS[b]
    return (x0 + HEAD_AT[0], HEAD_AT[1]) if kind == "head" else (x1 + FOOT_AT[0], FOOT_AT[1])


# ---- hooks ----------------------------------------------------------------------------------------------
def _supports(S, mesh):
    floor = []
    for x in range(-400, 501, 8):
        for y in range(-320, 300, 8):
            t = mesh.find(x, y)
            if t is not None and abs(mesh.height(t, x, y)) < 2:
                floor.append((x, y, 0, t))
    return floor, []


def _on(S, mesh, p, top, margin=4):
    if top > 30:
        return any(_in_bed(p, b, margin) for b in range(3))
    t = mesh.find(round(p[0]), round(p[1]))
    return t is not None and abs(mesh.height(t, p[0], p[1])) < 2


def _rel(ctx, pos):
    """(dx, dy, Cloud's z above hers, rel DIR, her lift above the bed): Cloud's spot from hers (her DIR 0)."""
    place = ctx.chamber_place
    key = pos["key"]
    if key in ("chained", "offering", "throne"):
        dx, dy, dz, rel = place[key]
        return dx, dy, dz, rel, (-place[key][2] if key == "throne" else 0)
    if pos["girl"] in "RP":                                   # (672: both at one spot, one DIR)
        return 0, 0, 0, 0, 0
    beach = importlib.import_module("679_beach_party")
    dx, dy, glift, clift, gd, cd = beach._rel(ctx, {"Z": "A"}.get(pos["girl"], pos["girl"]), pos["cloud"])
    a = -gd * 2 * math.pi / 256                               # (into her DIR 0's frame)
    return (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a), clift - glift,
            (cd - gd) % 256, glift)


def _stations(S, ctx, mesh, cam):
    mv, hb, _ = _mods()
    out = []
    for pos in CD.POSITIONS:
        st = []
        for b in range(3):
            x0, x1 = BEDS[b]
            if pos.get("target"):                           # (solved: his tip at her `target`)
                best = None
                for gy in range(90, 230, 10):
                    try:
                        g, gd, c, cd = LE._solve(S, ctx, mesh, cam, pos, round((x0 + x1) / 2), [gy], TOP,
                                                 dirs=(0, 128))
                    except AssertionError:
                        continue
                    best = best or (g, gd, c, cd)
                assert best, ("no room on the bed for", pos["key"])
                g, gd, c, cd = best
                t = _bed_tri(mesh, b)
                st.append((g + (t,), gd, c + (t,), cd))
                continue
            dx, dy, dz, rel, lift = _rel(ctx, pos)
            best = None
            for gd in (0, 128):
                for gy in range(BED_Y[0] - 40, BED_Y[1] + 1, 5):
                    for gx in range(x0, x1 + 1, 6):
                        a = gd * 2 * math.pi / 256
                        cx, cy = gx + dx * math.cos(a) - dy * math.sin(a), gy + dx * math.sin(a) + dy * math.cos(a)
                        gz = TOP + lift
                        cz = 0 if pos.get("floor") else gz + dz
                        cdir = (gd + rel) % 256
                        her = LE._world(ctx, mv.RUBY_HRC, "zm%s1.a" % pos["girl"].lower(), 7, gx, gy, gz, gd)
                        his = LE._world(ctx, hb.CLOUD_BARE_HRC, "zn%s1.a" % pos["cloud"].lower(), 7, cx, cy, cz, cdir)
                        hers = [her[n] for n in ("root", "l_foot", "r_foot", "hip")] + \
                            ([] if pos["girl"] == "E" else [her["head"]])
                        if not all(_in_bed(p, b) for p in hers):
                            continue
                        if pos.get("floor"):
                            # (in front of the foot: no walkmesh there, y 25-63; XYZI puts him on z 0)
                            ok = all(not _in_bed(his[n], b, -6) and BED_Y[0] - 60 <= his[n][1] <= BED_Y[0] and
                                     x0 - 10 <= his[n][0] <= x1 + 10 for n in ("root", "l_foot", "r_foot"))
                        else:
                            ok = all(_in_bed(his[n], b) for n in ("root", "l_foot", "r_foot", "head"))
                        if not ok:
                            continue
                        mid = (sum(BED_Y) / 2 - gy) ** 2 * 0.0004 + (gx - (x0 + x1) / 2) ** 2 * 0.002
                        score = (mv._view_depth(cam, his["chest"]) - mv._view_depth(cam, her["chest"])) * 0.1 - mid
                        if best is None or score > best[0]:
                            t = _bed_tri(mesh, b)
                            ct = _floor_tri(mesh, cx, cy) if pos.get("floor") else t
                            best = (score, ((gx, gy, round(gz), t), gd, (round(cx), round(cy), round(cz), ct), cdir))
            assert best, ("no room on the bed for", pos["key"], b)
            st.append(best[1])
        out.append(st)
    return out


def _slots_fn(S, ctx, mesh, cam, stations, floor, beds):
    """Every position: the six homes (standing / kneeling, facing down the room: DIR 0); the cameraman fixed."""
    homes = []
    for k in range(6):
        x, y = _home(k)
        anim = S.G_EXTRA + (0 if HOMES[k][0] == "head" else 1)
        homes.append((x, y, 0, _floor_tri(mesh, x, y), 0, anim, 1, (x, y)))
    cx, cy = CAM_AT
    c = min(floor, key=lambda p: math.dist(p[:2], (cx, cy)))
    _, _, dt = _mods()
    d = dt._dir_to(150 - c[0], 150 - c[1])
    return [list(homes) for _ in CD.POSITIONS], [(c, d) for _ in CD.POSITIONS], [(0, 0) for _ in CD.POSITIONS]


def _walks(mesh):
    walks, look = [], []
    for k in range(6):
        x, y = _home(k)
        s, t = (x, y - WALK_FROM), (x, y - WALK_STOP)
        walks.append(((s[0], s[1], 0, _floor_tri(mesh, *s)), (t[0], t[1], 0, _floor_tri(mesh, *t)), 128))
        look.append((x, y - 50, 0, _floor_tri(mesh, x, y - 50)))
    return walks, look


def _make_field(S, ctx):
    """ghotin_2 copied: entities produce / direct (the candles) / ad (the lightning) / cloud / child."""
    f = FieldFile(ctx.field(CD.BASE).build())
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    keep = {}
    for to, name in ((1, "fire"), (2, "thunder")):
        e = sec.entity_index(name)
        keep[to] = {0: sec.script_ops(e, 0)}
    ids = {id(o) for sc in keep.values() for ops in sc.values() for o in ops}
    assert all(o.target is None or id(o.target) in ids for sc in keep.values() for ops in sc.values() for o in ops)
    moved = 0
    for o in keep[2][0]:                                     # (the lightning's random: (5,6) -> (5,RAND_TEMP))
        r = bytearray(o.raw)
        if (o.op == 0x99 and r[1:3] == b"\x05\x06") or (o.op == 0x8D and r[1:3] == b"\x50\x06") or \
                (o.op == 0x14 and r[1] >> 4 == 5 and r[2] == 6):
            r[2] = RAND_TEMP
            o.raw = r
            moved += 1
    assert moved == 4, moved
    for sc in keep.values():
        if sc[0][-1].op != 0x00:
            sc[0] = sc[0] + [__import__("ff7.asm", fromlist=["ret"]).ret()]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in ("produce", "direct", "ad", "cloud", "child")]
    sec.entry = [[sec._end] * 32 for _ in range(5)]
    sec.ops = [o for sc in keep.values() for ops in sc.values() for o in ops]
    for e, sc in keep.items():
        sec.entry[e][0] = sc[0][0]
    f.sections[0] = sec.build()
    loader = ModelLoader(f.section("models"))
    assert ModelLoader.hrc(loader.models[0]) == "AAAA.HRC", ModelLoader.hrc(loader.models[0])
    loader.models = [loader.models[0], loader.models[1]]     # Cloud, and Aerith's story copy kept hidden
    f.set_section("models", loader.build())
    return f, keep


def _sprites(S, ctx, loader, mesh, cam, near):
    mv, _, _ = _mods()
    mm = mv.mm
    donor_loader = ModelLoader(ctx.field(mm.DONOR_FIELD).section("models"))
    scale = round(ModelLoader.entry_scale(donor_loader.models[mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    unit = 3.41 * scale / 512
    k = near / cam.zoom / unit
    names = {"QGJA": ("QGJB", "QGJC", "QGJD"), "QCJA": ("QCJB", "QCJC", "QCJD"), "QHJA": ("QHJB", "QHJC", "QHJD")}
    old = mv.SPRITES
    mv.SPRITES = names
    try:
        sp = mv._sprites(ctx, mv.GAUGE_PX / 2 * k, mv.CURSOR_PX / 2 * k, mv.ICON_PX / 2 * k)
    finally:
        mv.SPRITES = old
    return [ModelLoader.with_scale(sp[h], scale) for h in names]


def _poses(ctx):
    mv, _, _ = _mods()
    ctx.chamber_place = CP.build(ctx)
    for key, donor, bare, prefix, own, head_down, hrc in LE._cast():
        if own is None:
            entry = ModelLoader(ctx.field(donor[0]).section("models")).models[donor[1]]
            stand = ModelLoader.anims(entry)[0].split(".")[0].lower() + ".a"
            mv._retarget(ctx, ["ZM%s%d.tor" % (L, k) for L in "WXZ" for k in range(4)], prefix, hrc, stand,
                         head_down)


def apply(ctx):
    _poses(ctx)
    mesh = __import__("ff7.walkmesh", fromlist=["Walkmesh"]).Walkmesh(ctx.field(CD.BASE).section("walkmesh"))
    walks, look = _walks(mesh)
    S = LE.Set(CD, CD.FIELD, "WXBZREPICF", "EI", "", CLET="KNMAREPIOF",
               extra=[("W", CP.stand_bound), ("X", CP.kneel_behind)],
               make_field=_make_field, supports=_supports, on=_on, walkable=lambda S, mesh, p, m: False,
               stations=_stations, bed_watch=None, floor_watch=lambda *a: None, bed_id=lambda S, c: None,
               one_per_bed=False, cam_ok=lambda S, c: True, sprites=_sprites, slots_fn=_slots_fn, chamber=True,
               bed_of=[b for _, b in HOMES], walks=walks, look=look)
    sx, sy = Camera(ctx.field(CD.BASE).sections[1]).project(*CD.STAGE_AT)
    CD.STAGE = (round(sx), round(sy))
    LE.run(S, ctx, "679: the chamber", "chamber_layout.json")

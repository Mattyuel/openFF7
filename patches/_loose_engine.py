"""(user) The loose group shoot engine: a set (`Set`: a data module, a field, pose letters and hooks; 678 the
studio, 679 the beach party) with the group shoot's cast: bare Cloud, the six bare girls, the cameraman, the
gauge / cursor / icon sprites; the meter, holds, pauses, lessons, slap prompts and finisher are 670's (its
helpers and temp vars), the structure:

  segments   a position (S.D.POSITIONS, random, never the same twice running; the first is S.D.FIRST) with
             1-6 girls (random within its `counts`, a random order); each takes a turn of 10-20 s
  cutaways   a short staged scene (S.D.CUTS, random, no repeats until all have played) after each segment
  the end    the segment starting once S.D.MINUTES have passed is the last: the finisher in its last turn

Every girl has the same animation list (`_anims`: stand / walk / run, the still poses, the set's extra still
poses, each pose's two speeds (the meter's slow two steps -> 1, fast two -> 3), the waiting poses, the stop
poses), so one index works for all. The director writes the segment's six girl slots into temp vars
(`_slots`: spot, facing, waiting anim, kind, a stroll waypoint); each girl reads her own slot (GS); Cloud, the
camera's focus (the hidden player), the gauge, cursor and icon follow one combination index QI (position x
the engaged girl's station). Girls not taking part rest on a free bed / lounger or about the floor, some
strolling between their spot and a waypoint (a straight line checked walkable: no one walks into a wall).
The set's field: entities produce / direct / ad / cloud / child, models Cloud + one hidden (S.make_field)."""
import importlib
import math
import struct

import _movie_girls as MG
import _movie_group as GR
import _movie_profiles as PF
from _config import SPECIAL_ON
from _recruit import sound
from ff7 import asm
from ff7 import fieldanim as fa
from ff7 import triggers as tg
from ff7.camera import Camera, facing_screen, screen_range
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

ENTRY = (0.0, 1.2, 1.0)             # her entry point in the hip bone's frame (672 ENTRY)


class Set:
    """A loose shoot's set: D = its data module (POSITIONS, CUTS, TALK, COMMENTS, INTRO, ...), FIELD, the
    pose letters it uses (LET; HOLD_L with stop poses, WAIT_L whose frame 0 is the waiting pose), extra
    still poses (`extra`: [(letter, builder)]: a girl's anim prefix + letter + "5", built per girl by
    `builder(ctx, name, bare hrc, stand anim)`), and its hooks (see the studio's in 678): make_field(ctx)
    -> (FieldFile, {entity: scripts} kept), supports(S, mesh), on(S, mesh, p, top, margin),
    walkable(S, mesh, p, margin), stations(S, ctx, mesh, cam), bed_watch(S, ctx, mesh, c, k) -> (dir, anim)
    or None, sprites(S, ctx, loader, mesh, cam) -> [gauge, cursor, icon] loader entries."""
    def __init__(self, D, FIELD, LET, HOLD_L, WAIT_L, extra=(), CLET=None, **hooks):
        self.D, self.FIELD, self.LET, self.HOLD_L, self.WAIT_L = D, FIELD, LET, HOLD_L, WAIT_L
        self.CLET = CLET or LET              # Cloud's pose letters (LET: the girls'); HOLD_L in both
        self.extra = list(extra)
        # (the chamber, 679_chamber) chamber=True: each girl has her home (slots_fn) and her bed (bed_of);
        # one girl a segment, each once (the shoot ends when all are chosen); before her turn Cloud walks up
        # to her (walks[k]: start, stop spots (x, y, z, tri), his DIR; look[k]: the camera's focus) and
        # chooses her (D.CHOOSE, her D.REPLIES); she then goes to her bed's station
        self.chamber, self.slots_fn = False, None
        self.__dict__.update(hooks)
        # a girl's anims (the same for all six): stand / walk / run, the still poses (lie A, kneel A, lie B,
        # kneel B), the extra still poses, per pose letter its slow and fast speed, the waiting poses, per
        # stop letter pulled back / deepest / her try
        self.G_STAND, self.G_LIE, self.G_KNEEL = 0, (3, 5), (4, 6)
        self.G_EXTRA = 7
        self.G_SPEED = self.G_EXTRA + len(self.extra)
        self.G_WAIT = self.G_SPEED + 2 * len(LET)
        self.G_HOLD = self.G_WAIT + len(WAIT_L)
        self.G_COUNT = self.G_HOLD + 3 * len(HOLD_L)
        # Cloud's: stand / walk / run, the speeds, per stop letter pulled back / deepest, the lessons
        self.C_SPEED = 3
        self.C_HOLD = self.C_SPEED + 2 * len(self.CLET)
        self.C_LESSON = self.C_HOLD + 2 * len(HOLD_L)
        self.C_COUNT = self.C_LESSON + len(HOLD_L)


# temp vars (this field only; 670's helpers use 100-159, 170-192, 200-207)
SLOT = lambda s, o: (6, 12 * s + o)                  # o: 0 x, 2 y, 4 z, 6 dir, 8 waiting anim, 10 triangle
SK = lambda s: (5, 72 + s)                           # 0 a station, 1 still (queue / bed), 2 strolls (floor)
WX, WY = (lambda s: (6, 208 + 4 * s)), (lambda s: (6, 210 + 4 * s))
GS = lambda k: (5, 78 + k)                           # girl k's slot
QI, PI, NPART, TURNI, LASTP, LAST, WANDER, SEGPLACE = ((5, a) for a in range(84, 92))
CI, SPD, GLI, CLI, HOLDP, ORALP, HLI, QUEUE = ((5, a) for a in range(92, 100))
ORD = lambda i: (5, 160 + i)
GA = lambda k: (5, 233 + k)                          # girl k's anim to play
CA = (5, 239)
USEDC = [(5, 247), (5, 248), (5, 249)]               # cutaways played (bits)
RND3, USEDG, PRES, TS, STN, PICK = ((5, a) for a in range(250, 256))
NMIN, NSPAN = (5, 193), (5, 194)
CH = (5, 169)                                        # (the chamber) the girl Cloud is choosing
WALK_STEP = 2.2                                      # (the chamber) field units Cloud walks a frame
WALKING, WRND, WAITED = (5, 166), (5, 167), (5, 168)  # girls mid-stroll (bits), their own random, a timeout
PLACE_WAIT = 30                                      # frames black while everyone is placed (a girl's slot 2
                                                     # runs ~95 ops: 12 frames at 8 a frame; user saw moves)
CHOICE = (5, 241)


def _mods():
    return (importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"),
            importlib.import_module("660_dates"))


# ---- poses --------------------------------------------------------------------------------------
def _cast():
    """[(key, donor (field, model), bare hrc, prefix, own stand/walk/run or None, head_down)] in GR.ORDER."""
    mv, _, _ = _mods()
    by_key = {g["key"]: g for g in MG.GIRLS}
    out = []
    for key in GR.ORDER:
        if key == "ruby":
            out.append((key, mv.RUBY_DONOR, mv.BARE_HRC, "ZM", ["DXID.tor", "DXHF.tor", "DXIA.tor"], None, mv.RUBY_HRC))
        elif key == "skye":
            out.append((key, mv.SKYE_DONOR, mv.SKYE_BARE, "ZM", ["DXID.tor", "DXHF.tor", "DXIA.tor"], None, mv.RUBY_HRC))
        else:
            g = by_key[key]
            out.append((key, g["donor"][:2], g["hrc"], g["prefix"], None, g.get("head_down"), g["donor"][2]))
    return out


def _anims(S, ctx):
    """The new waiting poses (frame 0 of mission / dog / prone held: ZM<letter>5, retargeted per girl), the
    set's extra still poses (built per girl) and every girl's and Cloud's animation list (see S.G_* / S.C_*)."""
    mv, _, _ = _mods()
    for L in S.WAIT_L:
        a = fa.Anim(ctx.char_file("zm%s0.a" % L.lower()))
        a.frames = a.frames[:1]
        ctx.char_file("zm%s5.a" % L.lower(), a.build())
    lists = {}
    for key, donor, bare, prefix, own, head_down, hrc in _cast():
        if own is None:
            entry = ModelLoader(ctx.field(donor[0]).section("models")).models[donor[1]]
            own = ModelLoader.anims(entry)[:3]
            mv._retarget(ctx, ["ZM%s5.tor" % L for L in S.WAIT_L], prefix, hrc,
                         own[0].split(".")[0].lower() + ".a", head_down)
        for L, builder in S.extra:
            builder(ctx, prefix + L + "5", bare, own[0].split(".")[0].lower() + ".a")
        names = list(own) + [prefix + s + ".tor" for s in ("K0", "L0", "M0", "N0")] + \
            [prefix + L + "5.tor" for L, _ in S.extra] + \
            [prefix + L + s + ".tor" for L in S.LET for s in "13"] + [prefix + L + "5.tor" for L in S.WAIT_L] + \
            [prefix + L + d + ".tor" for L in S.HOLD_L for d in "987"]
        assert len(names) == S.G_COUNT <= 47, (key, len(names))
        for n in names[3:]:
            ctx.char_file(n.split(".")[0].lower() + ".a")            # (exists: asserted by the lookup)
        lists[key] = names
    cloud = ["ACFE.aki", "AAFF.aki", "AAGA.aki"] + ["ZN%s%s.tor" % (L, s) for L in S.CLET for s in "13"] + \
        ["ZN%s%s.tor" % (L, d) for L in S.HOLD_L for d in "98"] + ["ZN%sL.tor" % L for L in S.HOLD_L]
    assert len(cloud) == S.C_COUNT
    for n in cloud[3:]:
        ctx.char_file(n.split(".")[0].lower() + ".a")
    return lists, cloud


def _world(ctx, hrc, anim, frame, x, y, z, d):
    """Field positions of a posed model's joints (bone ends; 'root'; 'entry' (hip frame ENTRY); for bare
    Cloud 'tip' (his member's, 620 zcmp.p on the hip bone))."""
    mv, hb, _ = _mods()
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    A = fa.Anim(ctx.char_file(anim.lower()))
    rr, rp, rots = A.frames[frame % len(A.frames)]
    root = [rp[0], -rp[1], rp[2]]
    F = fa.forward(sk, rr, root, rots)
    a = d * 2 * math.pi / 256
    Fw = (math.sin(a), -math.cos(a))
    L = (-Fw[1], Fw[0])
    to = lambda m: (x + mv.UNIT * (m[0] * L[0] - m[2] * Fw[0]), y + mv.UNIT * (m[0] * L[1] - m[2] * Fw[1]),
                    z - mv.UNIT * m[1])
    out = {b[0]: to(e) for b, (_, s, e) in zip(sk, F)}
    out["root"] = to(root)
    hi = [b[0] for b in sk].index("hip")
    m, s, _ = F[hi]
    at = lambda p: to([s[k] + fa._vec(m, p)[k] for k in range(3)])
    out["entry"] = at(ENTRY)
    out["mouth"] = tuple((out["head"][k] + to(F[[b[0] for b in sk].index("head")][1])[k]) / 2 for k in range(3))
    if hrc.lower() == hb.CLOUD_BARE_HRC.lower():
        out["tip"] = at(hb.member_ends(ctx.char_file("zcmp.p"))[1])
    return out


# ---- the set's spots ----------------------------------------------------------------------------
def _solve(S, ctx, mesh, cam, pos, gx, gys, top, dirs=range(0, 256, 16)):
    """A station for a solved position: her at (gx, gy) on the support `top`, Cloud placed so his member's
    tip meets her `target` (frame 7: both deepest), DIR = hers + `rel`; her DIR the one (of `dirs`) that
    keeps both on the support (S.on) with Cloud the furthest from the camera. Returns (girl spot, her DIR,
    his spot, his DIR)."""
    mv, hb, _ = _mods()
    ga, ca = "zm%s1.a" % pos["girl"].lower(), "zn%s1.a" % pos["cloud"].lower()
    best = None
    for n, (gy, gd) in enumerate([(gy, gd) for gy in gys for gd in dirs]):
        cd = (gd + pos["rel"]) % 256
        her = _world(ctx, mv.RUBY_HRC, ga, 7, gx, gy, top, gd)
        his0 = _world(ctx, hb.CLOUD_BARE_HRC, ca, 7, 0, 0, top, cd)
        cx, cy = her[pos["target"]][0] - his0["tip"][0], her[pos["target"]][1] - his0["tip"][1]
        his = _world(ctx, hb.CLOUD_BARE_HRC, ca, 7, cx, cy, top, cd)
        pts = [her[k] for k in ("root", "head", "l_foot", "r_foot")] + [his[k] for k in ("root", "l_foot", "r_foot")]
        if all(S.on(S, mesh, p, top, 4) for p in pts):
            # (rendered: Cloud between her and the camera hid her) he the further from the camera
            score = mv._view_depth(cam, his["chest"]) - mv._view_depth(cam, her["chest"]) - n * 0.01
            if best is None or score > best[0]:
                best = (score, (gx, gy, top), gd, (round(cx), round(cy), top), cd)
    if best:
        return best[1:]
    raise AssertionError(("no room for", pos["key"], gx, gys, top))


def _tri(mesh, x, y, top, tol=3):
    t = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y) and abs(mesh.height(t, x, y) - top) < tol]
    return t[0] if t else min(range(len(mesh.tris)), key=lambda i: math.dist(mesh.center(i)[:2], (x, y)))


def _path_clear(S, mesh, a, b, step=4):
    """Every point on the straight line a -> b (and 10 either side) can be walked (S.walkable)."""
    n = max(1, int(math.dist(a, b) / step))
    for i in range(n + 1):
        x, y = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
        if not S.walkable(S, mesh, (x, y), 10):
            return False
    return True


def _wait_anim(S, name, i):
    """A waiting / watching pose by name: kneel / lie (two timings by i), stand, or an extra still letter."""
    if name == "kneel":
        return S.G_KNEEL[i % 2]
    if name == "lie":
        return S.G_LIE[i % 2]
    if name == "stand":
        return S.G_STAND
    return S.G_EXTRA + [L for L, _ in S.extra].index(name)


def _slots(S, ctx, mesh, cam, stations, floor, beds):
    """Per position, six slots: (x, y, z, tri, dir, anim, kind, waypoint (x, y)). Stations first (rows:
    each girl her own; queues: the one station, then waiting spots near it), then watchers: the free bed and
    floor spots nearest the view (S.bed_watch's pose on a bed; on the floor S.floor_watch's still pose, or
    standing with a waypoint to stroll to). Returns (slots, the cameraman's spot + DIR, the view centres)."""
    mv, hb, dt = _mods()
    left, top, right, bottom = screen_range(ctx.field(S.FIELD).section("triggers"))
    proj = lambda p: cam.project(*p[:3])
    bedset = set(beds)
    out, cams, views = [], [], []
    for p, (pos, st) in enumerate(zip(S.D.POSITIONS, stations)):
        cs = [s[2] for s in st]
        fx = sum(c[0] for c in cs) / len(cs)
        fy = sum(c[1] for c in cs) / len(cs)
        fz = sum(c[2] for c in cs) / len(cs)
        vx, vy = proj((fx, fy, fz))
        vx, vy = min(max(vx, left + 160), right - 160), min(max(vy, top + 120), bottom - 120)
        views.append((vx, vy))
        taken = [proj(s[0]) for s in st] + [proj(s[2]) for s in st]
        free = lambda c, gap: all((proj(c)[0] - t[0]) ** 2 + (proj(c)[1] - t[1]) ** 2 >= gap ** 2 for t in taken)
        seen = lambda c: abs(proj(c)[0] - vx) < 145 and abs(proj(c)[1] - vy) < 95
        slots = []
        letter = pos["girl"]
        for i, (g, gd, c, cd) in enumerate(st):
            if pos.get("wait"):
                wait = _wait_anim(S, pos["wait"], i)
            elif letter == "J":
                wait = S.G_KNEEL[i % 2]
            elif letter in "EO":
                wait = S.G_LIE[i % 2]
            elif letter in S.WAIT_L:
                wait = S.G_WAIT + S.WAIT_L.index(letter)
            else:
                wait = S.G_STAND
            slots.append((g[0], g[1], g[2], g[3], gd, wait, 0, (g[0], g[1])))
        # the cameraman: on the floor near the front, facing the action, clear of everyone
        cand = sorted((c for c in floor if free(c, 26) and seen(c) and S.cam_ok(S, c)),
                      key=lambda c: abs(proj(c)[0] - vx - 90) + abs(proj(c)[1] - vy - 40))
        cm = cand[0]
        cams.append((cm, dt._dir_to(fx - cm[0], fy - cm[1])))
        taken.append(proj(cm))
        ax, ay = proj((fx, fy, fz))
        clear_front = lambda c: not (proj(c)[1] > ay - 10 and abs(proj(c)[0] - ax) < 60)
        busy = {S.bed_id(S, s_[k]) for s_ in st for k in (0, 2)} - {None}
        beds_ = [c for c in beds if S.bed_id(S, c) not in busy]   # (nobody waits on a bed in use: Tifa lay across a cowgirl)
        if len(st) == 1:                                  # a queue: waiting near the station (not in front of it)
            g = st[0][0]
            near = sorted((c for c in beds_ + floor if free(c, 22) and seen(c) and clear_front(c)),
                          key=lambda c: (0 if abs(c[2] - g[2]) < 3 else 1, math.dist(c[:2], g[:2])))
            for _ in range(pos["counts"][1] - 1):
                c = next((c for c in near if free(c, 32)), None)
                assert c is not None, ("no queue spot", pos["key"])
                taken.append(proj(c))
                face = dt._dir_to(g[0] - c[0], g[1] - c[1])
                d_, a_ = S.bed_watch(S, ctx, mesh, c, len(slots), free, face, queue=True) if c in bedset else \
                    (face, S.G_STAND)
                slots.append((c[0], c[1], c[2], c[3], d_, a_, 1, c[:2]))
        # watchers: alternately a bed spot and a floor spot; spread out (the spot furthest from everyone placed,
        # short of the view's edges), never in front of the action (below it on screen, near its column: they
        # hid it on renders)
        want_bed = True
        while len(slots) < 6:
            pool = [c for c in (beds_ if want_bed else floor) if free(c, 32) and seen(c) and clear_front(c)]
            if not pool:
                pool = [c for c in beds_ + floor if free(c, 28) and seen(c) and clear_front(c)]
            if not pool:
                pool = [c for c in beds_ + floor if free(c, 22) and seen(c)]
            assert pool, ("no watch spot", pos["key"])
            spread = lambda c: min(70, min(math.dist(proj(c), t) for t in taken)) - \
                0.15 * math.dist(proj(c), (vx, vy))
            c = max(pool, key=spread)
            face = dt._dir_to(fx - c[0], fy - c[1])
            if c in bedset:
                d_, a_ = S.bed_watch(S, ctx, mesh, c, len(slots), free, face)
                slots.append((c[0], c[1], c[2], c[3], d_, a_, 1, c[:2]))
                if S.one_per_bed:                         # (a lounger holds one)
                    busy.add(S.bed_id(S, c))
                    beds_ = [b_ for b_ in beds_ if S.bed_id(S, b_) not in busy]
            else:
                still = S.floor_watch(S, ctx, mesh, c, len(slots), free, face)
                if still:
                    slots.append((c[0], c[1], c[2], c[3], still[0], still[1], 1, c[:2]))
                else:
                    wps = [w for w in floor if 40 <= math.dist(w[:2], c[:2]) <= 90 and free(w, 30) and seen(w) and
                           _path_clear(S, mesh, c[:2], w[:2])]
                    wps.sort(key=lambda w: -min(math.dist(proj(w), t) for t in taken))
                    slots.append((c[0], c[1], c[2], c[3], face, S.G_STAND, 2 if wps else 1,
                                  wps[0][:2] if wps else c[:2]))
                    if wps:
                        taken.append(proj(wps[0]))
            taken.append(proj(c))
            want_bed = not want_bed
        out.append(slots)
    return out, cams, views


def _gauge_spots(S, ctx, mesh, cam, focus, near):
    """(gauge, icon, cursor line (first, step x16)) for a view centred on `focus` (as 670's group)."""
    mv, _, _ = _mods()
    left, top, right, bottom = screen_range(ctx.field(S.FIELD).section("triggers"))
    sx, sy = cam.project(*focus[:3])
    sx = min(max(sx, left + 160), right - 160)
    sy = min(max(sy, top + 120), bottom - 120)
    gy = sy + mv.GAUGE_Y
    g = mv._unproject(cam, sx, gy, near)
    gauge = (round(g[0]), round(g[1]), round(g[2]), mv._nearest_tri(mesh, g[0], g[1]))
    icon = mv._icon_at(cam, mesh, sx, sy, near)
    pts = []
    for b in range(21):
        off = ((b * 50 + 25) - 500) / 1000 * mv.GAUGE_PX
        q = mv._unproject(cam, sx + off, gy - mv.CURSOR_UP, near)
        pts.append((round(q[0]), round(q[1]), round(q[2]), mv._nearest_tri(mesh, q[0], q[1])))
    return gauge, icon, pts


# ---- the set ------------------------------------------------------------------------------------
def _build(S, ctx, back):
    mv, hb, dt = _mods()
    lists, cloud_anims = _anims(S, ctx)
    ctx.field(S.FIELD)                                  # (registers the original: the copy is saved over it)
    f, kept = S.make_field(S, ctx)
    ctx._fields[S.FIELD] = f
    trig = f.section("triggers")
    for slot in range(12):                               # no way out by walking
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    loader = ModelLoader(f.section("models"))
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    assert names[:5] == ["produce", "direct", "ad", "cloud", "child"] and len(loader.models) == 2, names

    # models: 2 bare Cloud, 3-8 the girls (GR.ORDER), 9 cameraman, 10 gauge, 11 cursor, 12 icon
    cl0 = loader.models[0]
    loader.models.append(ModelLoader.only_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), cloud_anims))
    for key, donor, bare, prefix, own, head_down, hrc in _cast():
        m = loader.add_from(ModelLoader(ctx.field(donor[0]).section("models")), donor[1])
        loader.models[m] = ModelLoader.only_anims(
            ModelLoader.with_hrc(loader.models[m], bare, ModelLoader.name(loader.models[m])[:-5] + "_b.char"),
            lists[key])
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_FILM)
    # (user) still in the cutaways (670's one-frame camera pose); he only moves while filming
    loader.models[cm] = ModelLoader.with_anims(loader.models[cm], [mv.CAMERA_STILL])
    idle_cam = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_STILL)
    near = min(mv._view_depth(cam, v) for t in mesh.tris for v in t) * 0.8
    loader.models += S.sprites(S, ctx, loader, mesh, cam, near)     # gauge, cursor, icon
    assert len(loader.models) == 13 and cm == 9, len(loader.models)
    assert sum(len(ModelLoader.anims(e)) for e in loader.models) < 400

    # spots
    floor, beds = S.supports(S, mesh)
    stations = S.stations(S, ctx, mesh, cam)
    slots, cams, views = (S.slots_fn or _slots)(S, ctx, mesh, cam, stations, floor, beds)
    combos, qbase = [], []                               # QI = qbase[position] + the engaged girl's station
    for p, st in enumerate(stations):
        qbase.append(len(combos))
        for g, gd, c, cd in st:
            combos.append((c, cd))
    gauge = [_gauge_spots(S, ctx, mesh, cam, c, near) for c, cd in combos]
    gx, gy_, gz = gauge[0][0][:3]

    def tilt(d):
        a = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy_, gz), cam.project(gx + 50 * math.cos(a), gy_ + 50 * math.sin(a), gz)
        return abs(p1[1] - p0[1]) / (abs(p1[0] - p0[0]) + 1e-9) + (0 if p1[0] > p0[0] else 100)
    sprite_dir = min(range(256), key=tilt)

    ents = {}
    for name in ("cloudb", *GR.ORDER, "camera", "gauge", "cursor", "keys", "voice", "hush", "shout", "hush2", "hush3",
                 "icon", "sqkey", "util"):
        ents[name] = len(sec.entity_names)
        sec.entity_names.append(name.encode("latin-1").ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    CL = 3
    girl_ents = [ents[k] for k in GR.ORDER]
    actors = [ents["cloudb"]] + girl_ents
    ch = mv._chain
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]     # TLKON 01, SOLID 01 (talk off, not solid)
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    by_q = lambda make: ch(QI, [make(q) for q in range(len(combos))])
    by_p = lambda make: ch(PI, [make(p) for p in range(len(S.D.POSITIONS))])
    play = lambda var, n: ch(var, [loop_(i) for i in range(n)])          # the anim in var (one of n)
    xyzi_var = lambda s: Op(bytes([0xA5, 0x66, 0x66]) + struct.pack("<HHHH", SLOT(s, 0)[1], SLOT(s, 2)[1],
                                                                       SLOT(s, 4)[1], SLOT(s, 10)[1]))
    scripts = dict(kept)                                 # (the set's own, e.g. the beach's waves)

    # the hidden player: the camera follows it (QI: Cloud's spot; CI: a cutaway's)
    start = combos[0][0]
    scripts[CL] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*start), hb._visi(0)] + hide() + [asm.ret(),
                                                                                                        asm.ret()],
                   2: by_q(lambda q: [xyzi(*combos[q][0])]) + [asm.ret()]}
    scripts[4] = {0: [Op(bytes([0xA1, 1])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()]}

    # Cloud: slot 2 placed by QI + his anim, 3 his anim (the speed), 4 / 5 the stop poses, 7 the lesson
    canim = [asm.setbyte(CA, CLI), Op(bytes([0x85, 0x55, CA[1], CLI[1]])), Op(bytes([0x85, 0x55, CA[1], SPD[1]])),
             Op(bytes([0x85, 0x50, CA[1], S.C_SPEED]))]
    cplay = asm.nop()
    scripts[ents["cloudb"]] = {
        0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: by_q(lambda q: [xyzi(*combos[q][0]), d_(combos[q][1]), hb._visi(1)]) + canim + [cplay] + play(CA, S.C_COUNT) +
        [asm.ret()],
        3: [asm.setbyte(CA, CLI)] + canim[1:] + [asm.goto_back(cplay), asm.ret()],             # (slot 2's switch)
        4: ch(HLI, [loop_(S.C_HOLD + 2 * h) for h in range(len(S.HOLD_L))]) + [asm.ret()],
        5: ch(HLI, [loop_(S.C_HOLD + 2 * h + 1) for h in range(len(S.HOLD_L))]) + [asm.ret()],
        7: ch(HLI, [mv.lesson_slot(S.C_LESSON + h, S.C_HOLD + 2 * h) for h in range(len(S.HOLD_L))]) + [asm.ret()]}

    if S.chamber:
        # Cloud: slot 10 stands at the walk's start (by CH), slot 8 walks to the stop: XYZI stepped a frame at a
        # time (the floor between the beds isn't walkmesh: no MOVE), the walk anim, then stands facing her
        CX, CY, CN = (6, 208), (6, 210), (5, 212)
        pre, walk = [], []
        for k in range(len(GR.ORDER)):
            (sx, sy, sz, st), (tx, ty, tz, tt), d = S.walks[k]
            n = max(1, round(math.dist((sx, sy), (tx, ty)) / WALK_STEP))
            stx, sty = round((tx - sx) / n), round((ty - sy) / n)
            top, done_ = hb._w(1), asm.nop()
            pre.append([xyzi(sx, sy, sz, st), d_(d), hb._visi(1)] + loop_(0))
            walk.append([asm.setword(CX, sx & 0xFFFF), asm.setword(CY, sy & 0xFFFF), asm.setbyte(CN, 0)] + loop_(1) +
                        [top, hb._arith(0x86, CX, stx & 0xFFFF), hb._arith(0x86, CY, sty & 0xFFFF),
                         Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", CX[1], CY[1], round(sz), st)),
                         Op(bytes([0x95, CN[0], CN[1]])), asm.if_byte(CN, "<", n, done_), asm.goto_back(top),
                         done_, xyzi(tx, ty, tz, tt), d_(d)] + loop_(0))
        scripts[ents["cloudb"]][10] = ch(CH, pre) + [asm.ret()]
        scripts[ents["cloudb"]][8] = ch(CH, walk) + [asm.ret()]
        scripts[CL][8] = ch(CH, [[xyzi(*S.look[k])] for k in range(len(GR.ORDER))]) + [asm.ret()]

    # the girls: slot 2 placed by her slot (GS) + her anim (engaged: the pose's speed, else the slot's
    # waiting anim); a strolling watcher keeps strolling (placed only at a segment's start, SEGPLACE); 3 her
    # anim if engaged (the speed); 4 / 5 / 6 the stop poses / her try (engaged); 7 walked off; main: the stroll
    for k, key in enumerate(GR.ORDER):
        e = ents[key]
        eng = [asm.setbyte(GA(k), GLI), Op(bytes([0x85, 0x55, GA(k)[1], GLI[1]])),
               Op(bytes([0x85, 0x55, GA(k)[1], SPD[1]])), Op(bytes([0x85, 0x50, GA(k)[1], S.G_SPEED]))]
        here, not_eng, anim = asm.nop(), asm.nop(), asm.nop()
        place = [asm.if_byte(mv.LEFT, "bit_on", k, here), hb._visi(0), asm.ret(), here]
        for s in range(6):                                # (a strolling watcher between segments' starts: left be)
            nx = asm.nop()
            place += [asm.if_byte(GS(k), "==", s, nx), asm.if_byte(SEGPLACE, "==", 0, nx),
                      asm.if_byte(SK(s), "==", 2, nx), asm.ret(), nx]
        place += ch(GS(k), [[xyzi_var(s), Op(bytes([0xB3, 5, SLOT(s, 6)[1]])), hb._visi(1),
                             asm.setbyte(GA(k), (5, SLOT(s, 8)[1]))] for s in range(6)])
        play_at = asm.nop()
        station = []
        if S.chamber:                                     # (the chamber: she goes to her bed's station)
            b_ = S.bed_of[k]
            station = by_p(lambda p: [xyzi(*stations[p][b_][0]), d_(stations[p][b_][1])])
        place += [asm.if_byte(mv.E, "==", k, not_eng)] + station + eng + [not_eng, play_at] + \
            play(GA(k), S.G_COUNT) + [asm.ret()]
        speed = [asm.if_byte(mv.E, "==", k, anim)] + eng + [asm.goto_back(play_at), anim, asm.ret()]   # (slot 2's switch)

        def stop(kind, k=k):
            gone = asm.nop()
            return [asm.if_byte(mv.E, "==", k, gone)] + \
                ch(HLI, [loop_(S.G_HOLD + 3 * h + kind) for h in range(len(S.HOLD_L))]) + [gone, asm.ret()]
        gone6 = asm.nop()
        s6 = [hb._w(mv.hold_try_delay()), asm.if_byte(mv.E, "==", k, gone6)] + \
            ch(HLI, [[mv._animb(), Op(bytes([0xA2, S.G_HOLD + 3 * h + 1, 1])), Op(bytes([0xAE, S.G_HOLD + 3 * h + 2, 1]))]
                     for h in range(len(S.HOLD_L))]) + [gone6, asm.ret()]
        # the stroll (main): now and then, while WANDER, to her slot's waypoint and back, facing Cloud after
        # each leg; only from a strolling slot (SK 2: its waypoint's line checked to be all floor). WALKING bit
        # k is on while a MOVE runs: the director waits for none before re-placing anyone (user: a MOVE still
        # running when she was re-placed went on to that slot's next waypoint - another position's, on a bed -
        # and she walked into the bed for good, her new anims never showing)
        top = hb._w(45)
        again = asm.goto_back(top)
        walk = [top, asm.if_byte(WANDER, "==", 1, again), asm.if_byte(mv.LEFT, "bit_off", k, again),
                Op(bytes([0x99, WRND[0], WRND[1]])), asm.if_byte(WRND, "<", 90, again)]
        for s in range(6):
            nx = asm.nop()
            walk += [asm.if_byte(GS(k), "==", s, nx), asm.if_byte(SK(s), "==", 2, nx), asm.biton(WALKING, k),
                     Op(bytes([0xA8, 0x66]) + struct.pack("<HH", WX(s)[1], WY(s)[1])), asm.bitoff(WALKING, k),
                     hb._tura(ents["cloudb"]),
                     hb._w(90), asm.if_byte(WANDER, "==", 1, nx), asm.biton(WALKING, k),   # (stopped meanwhile: placed anyway)
                     Op(bytes([0xA8, 0x66]) + struct.pack("<HH", SLOT(s, 0)[1], SLOT(s, 2)[1])),
                     asm.bitoff(WALKING, k), hb._tura(ents["cloudb"]), nx]
        walk += [again]
        scripts[e] = {0: [Op(bytes([0xA1, 3 + k])), hb._visi(0)] + hide() + [asm.ret()] + walk + [asm.ret()],
                      2: place, 3: speed, 4: stop(0), 5: stop(1), 6: s6, 7: [hb._visi(0), asm.ret()]}

    # the cameraman: filming, placed by position
    scripts[ents["camera"]] = {
        0: [Op(bytes([0xA1, 9])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: by_p(lambda p: [xyzi(*cams[p][0]), d_(cams[p][1])]) + [hb._visi(1)] + loop_(film) + [asm.ret()]}
    scripts[ents["gauge"]] = {0: [Op(bytes([0xA1, 10])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret(), asm.ret()],
                              2: by_q(lambda q: [xyzi(*gauge[q][0])]) + [hb._visi(1), asm.ret()],
                              9: [hb._visi(0), asm.ret()]}
    scripts[ents["icon"]], scripts[ents["sqkey"]] = mv._hold_entities(
        hb, 12, sprite_dir, by_q(lambda q: [xyzi(*gauge[q][1])]), cloud=ents["cloudb"])
    # cursor: as the group's, along its line: per q the line's start F, step |P| (x16) and signs SGN; then
    # bucket b -> F + b * P / 16 (one shared piece of maths)
    loop, idle, capped = asm.nop(), asm.nop(), asm.nop()
    CUR, CUR_T = [(6, 200), (6, 202), (6, 204)], (6, 206)
    F_, P_, SGN, TRI = [(6, 242), (6, 244), (6, 182)], [(6, 188), (6, 140), (6, 198)], (5, 220), (5, 137)
    cur = [loop, asm.if_byte(mv.RUN, "==", 1, idle), asm.setword(mv.BKT, mv.POS), hb._arith(0x8C, mv.BKT, 50),
           asm.if_word(mv.BKT, ">", 20, capped), asm.setword(mv.BKT, 20), capped]

    def cur_at(q):
        pts, ops_, sg = gauge[q][2], [], 0
        for a, var in enumerate(CUR):
            step = round((pts[20][a] - pts[0][a]) * 16 / 20)
            assert all(abs(pts[0][a] + b * step / 16 - pts[b][a]) <= 2 for b in range(21)), ("cursor line", q, a)
            ops_ += [asm.setword(F_[a], pts[0][a] & 0xFFFF), asm.setword(P_[a], abs(step))]
            sg |= (step < 0) << a
        return ops_ + [asm.setbyte(SGN, sg), asm.setbyte(TRI, pts[10][3])]
    cur += by_q(cur_at)
    for a, var in enumerate(CUR):
        neg, done_ = asm.nop(), asm.nop()
        cur += [asm.setword(var, mv.BKT), hb._arith(0x8A, var, P_[a]), hb._arith(0x8C, var, 16),
                asm.setword(CUR_T, F_[a]), asm.if_byte(SGN, "bit_off", a, neg), hb._arith(0x86, CUR_T, var),
                asm.goto(done_), neg, hb._arith(0x88, CUR_T, var), done_, asm.setword(var, CUR_T)]
    cur += [Op(bytes([0xA5, 0x66, 0x65]) + struct.pack("<HHHH", CUR[0][1], CUR[1][1], CUR[2][1], TRI[1])),
            hb._visi(1), hb._w(1), asm.goto_back(loop)]
    cur += [idle, hb._visi(0), hb._w(1), asm.goto_back(loop)]
    scripts[ents["cursor"]] = {0: [Op(bytes([0xA1, 11])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret()] + cur +
                               [asm.ret()]}
    wait = hb._w(1)
    back1, up = asm.goto_back(wait), asm.setbyte(mv.HELD, 0)
    scripts[ents["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x96, mv.FR[0], mv.FR[1]])),
                                 Op(bytes([0x30]) + struct.pack("<H", mv.OK_KEY) + b"\x00", target=up),
                                 asm.if_byte(mv.HELD, "==", 0, back1), asm.setbyte(mv.HELD, 1),
                                 Op(bytes([0x96, mv.PR[0], mv.PR[1]])), back1,
                                 up, asm.goto_back(wait), asm.ret()]}
    return dict(f=f, sec=sec, mesh=mesh, cam=cam, loader=loader, ents=ents, scripts=scripts, slots=slots, cams=cams,
                stations=stations, qbase=qbase, combos=combos, floor=floor, beds=beds, lists=lists, CL=CL,
                girl_ents=girl_ents, actors=actors, idle_cam=idle_cam, film=film, views=views)


# ---- cutaways ------------------------------------------------------------------------------------

def _stage(S, ctx, B):
    """Every cutaway's staging (S.D.CUTS, then the intro): each actor's slot 9 (spot, facing, pose by CI), the
    player's (the view), the gauge's (hidden). Spots: screen offsets from S.D.STAGE, the nearest free floor
    (bed tops for a cut's `bed` actors), at least 16 px apart."""
    mv, hb, dt = _mods()
    cam, ents, scripts = B["cam"], B["ents"], B["scripts"]
    proj = lambda c: cam.project(*c[:3])
    cand = [c + tuple(proj(c)) for c in B["floor"]]
    bedc = [c + tuple(proj(c)) for c in B["beds"]]
    ox, oy = S.D.STAGE

    def at(dx, dy, taken, bed=False):
        free = [c for c in (bedc if bed else cand) if all((c[4] - t[0]) ** 2 + (c[5] - t[1]) ** 2 >= 16 ** 2
                                                          for t in taken)]
        c = min(free, key=lambda c: (c[4] - ox - dx) ** 2 + (c[5] - oy - dy) ** 2)
        assert (c[4] - ox - dx) ** 2 + (c[5] - oy - dy) ** 2 < 40 ** 2, ("no floor there", dx, dy)
        return c[:4]
    centre = at(0, 0, [])
    who = ["cloud", "camera"] + GR.ORDER
    anim = {"stand": S.G_STAND, "kneel": S.G_KNEEL[0], "lie": S.G_LIE[0]}
    slots = {k: [] for k in who}
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    for st in [c["set"] for c in S.D.CUTS] + [S.D.INTRO_SET]:
        spot, taken = {}, []
        watch = iter(getattr(S.D, "WATCH", GR.WATCH))
        for k in sorted(who, key=lambda k: k not in st):
            sx, sy, pose, face = st[k] if k in st else next(watch) + ("stand", "centre")
            spot[k] = (at(sx, sy, taken, k in st and pose == "lie" and False), pose, face)
            taken.append(proj(spot[k][0]))
        for k in who:
            (x, y, z, t), pose, face = spot[k]
            if face == "front":
                d = facing_screen(cam, x, y, z, (0, 1))
            else:
                tx, ty = (centre if face == "centre" else spot[face][0])[:2]
                d = dt._dir_to(tx - x, ty - y)
            if k == "cloud":
                a = 0
            elif k == "camera":
                a = B["idle_cam"]
            else:
                a = anim[pose] if pose in anim else _wait_anim(S, pose, 0)
            slots[k].append([hb._xyzi(x, y, z, t), Op(bytes([0xB3, 0, d])), hb._visi(1)] + loop_(a))
    ch = mv._chain
    for k in who:
        e = ents["cloudb"] if k == "cloud" else ents[k]
        head = []
        if k in GR.ORDER:
            here = asm.nop()
            head = [asm.if_byte(mv.LEFT, "bit_on", GR.ORDER.index(k), here), hb._visi(0), asm.ret(), here]
        scripts[e][9] = head + ch(CI, slots[k]) + [asm.ret()]
    scripts[B["CL"]][9] = [hb._xyzi(*centre), asm.ret()]


# ---- the director --------------------------------------------------------------------------------
def _director(S, ctx, B, back):
    mv, hb, dt = _mods()
    sec, ents, scripts = B["sec"], B["ents"], B["scripts"]
    ch, CL = mv._chain, B["CL"]
    E, LEFT = mv.E, mv.LEFT
    n_g, NP, NC = len(GR.ORDER), len(S.D.POSITIONS), len(S.D.CUTS)
    girl_ents, actors = B["girl_ents"], B["actors"]
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    say_once = lambda t: [hb._window(t, 0), asm.message(0, mv._text_id(sec, t))]
    LASTT = (5, 232)

    # voice: the engaged girl (muffled in oral poses, else her TALK lines) and a random other's comment
    def line(who, text):
        t = "%s\n%s" % (GR.NAMES[who], text if text[:1] in "(" or text[:2] in ("Mm", "Hn", "Gk", "Wh") else
                        "“%s”" % text)
        return [Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, mv.LINE_Y), hb._req(ents["hush"], 2, wait=False)] + \
            ([hb._req(ents["icon"], 4, wait=False)] if mv._slaps(text) else []) + \
            [asm.message(1, mv._text_id(sec, t))]
    vl, vdone, other, talk = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    K, VV, CC = mv.K, mv.VV, mv.CC
    voice = [asm.ret(), vl, hb._w(mv.SAY_EVERY), asm.if_byte(mv.RUN, "==", 1, vdone),
             Op(bytes([0x95, K[0], K[1]])), Op(bytes([0x8D, K[0] << 4, K[1], 12])),
             Op(bytes([0x95, VV[0], VV[1]])), Op(bytes([0x8D, VV[0] << 4, VV[1], 2])),
             asm.if_byte(VV, "==", 0, other), asm.if_byte(ORALP, "==", 1, talk)]
    KM = {n: (5, 194 + n // 2) for n in (3, 4, 6)}       # K mod 3 / 4 / 6 (195, 196, 197)
    voice = voice[:5] + [x for n, v in KM.items() for x in (asm.setbyte(v, K), Op(bytes([0x8D, 0x50, v[1], n])))] + \
        voice[5:]
    voice += ch(E, [ch(KM[3], [line(key, t) for t in GR.MUFFLED[key][:3]]) for key in GR.ORDER])
    voice += [asm.goto(vdone), talk]
    voice += ch(E, [ch(KM[len(S.D.TALK[key])], [line(key, t) for t in S.D.TALK[key]]) for key in GR.ORDER])
    voice += [asm.goto(vdone), other, Op(bytes([0x99, CC[0], CC[1]])), Op(bytes([0x8D, CC[0] << 4, CC[1], n_g]))]
    for r_ in range(n_g):                            # never the engaged girl nor one who walked off: the next one
        rend = asm.nop()
        for k in range(n_g):
            nx, chk = asm.nop(), asm.nop()
            voice += [asm.if_byte(CC, "==", k, nx), asm.if_byte(E, "==", k, chk), asm.setbyte(CC, (k + 1) % n_g),
                      asm.goto(rend), chk, asm.if_byte(LEFT, "bit_on", k, nx), asm.setbyte(CC, (k + 1) % n_g),
                      asm.goto(rend), nx]
        voice += [rend]
    for k in range(n_g):
        nx, chk = asm.nop(), asm.nop()
        voice += [asm.if_byte(CC, "==", k, nx), asm.if_byte(E, "==", k, chk), asm.goto(vdone), chk,
                  asm.if_byte(LEFT, "bit_on", k, nx), asm.goto(vdone), nx]
    voice += ch(CC, [ch(KM[len(S.D.COMMENTS[key])], [line(key, t) for t in S.D.COMMENTS[key]]) for key in GR.ORDER])
    voice += [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.SAY_FOR), Op(b"\x54\x01"), asm.ret()]}
    shout = S.D.LAST_CALL
    scripts[ents["shout"]] = {0: [asm.ret(), asm.ret()],
                              2: [Op(b"\x52\x02\x00\x01"), hb._window(shout, 2, 8, 56),
                                  hb._req(ents["hush2"], 2, wait=False), asm.message(2, mv._text_id(sec, shout)),
                                  asm.ret()]}
    scripts[ents["hush2"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.FINISH_SAY_FOR), Op(b"\x54\x02"), asm.ret()]}
    scripts[ents["hush3"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(GR.PAUSE_FRAMES[1]), Op(b"\x54\x03"), asm.ret()],
                              3: [hb._w(GR.HOLD_SAY), Op(b"\x54\x03"), asm.ret()],
                              4: [hb._w(GR.MUFFLED_SAY), Op(b"\x54\x03"), asm.ret()]}

    # util: slot 2 picks a girl at random not yet in USEDG (PICK, 255: none); slot 3 a cutaway (CI) not yet
    # played whose girls are all here (all played: start again; none possible: 255)
    found = asm.nop()
    pick = [Op(bytes([0x99, RND3[0], RND3[1]])), Op(bytes([0x8D, RND3[0] << 4, RND3[1], n_g]))]
    for step in range(2 * n_g):
        k = step % n_g
        nxt, taken = asm.nop(), asm.nop()
        pick += [asm.if_byte(RND3, "==", k, nxt), asm.if_byte(USEDG, "bit_off", k, taken), asm.setbyte(PICK, k),
                 asm.biton(USEDG, k), asm.ret(), taken, asm.setbyte(RND3, (k + 1) % n_g), nxt]
    pick += [asm.setbyte(PICK, 255), asm.ret()]

    ROUND, CNT = (5, 246), (5, 245)
    r_top, probe, nxt, wrapd = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    checks = []
    for j, c in enumerate(S.D.CUTS):
        no = asm.goto(nxt)
        v, b = USEDC[j // 8][1], j % 8
        checks.append([asm.if_byte((5, v), "bit_off", b, no)] +
                      [asm.if_byte(LEFT, "bit_off", GR.ORDER.index(g), no) for g in c["need"]] +
                      [asm.setbyte(CI, j), asm.biton((5, v), b), asm.ret(), no])
    again_ = asm.goto_back(probe)
    cut = [asm.setbyte(ROUND, 0), r_top, Op(bytes([0x99, RND3[0], RND3[1]])), Op(bytes([0x8D, RND3[0] << 4, RND3[1], NC])),
           asm.setbyte(CNT, 0), probe] + ch(RND3, checks) + \
        [nxt, Op(bytes([0x95, RND3[0], RND3[1]])), asm.if_byte(RND3, ">=", NC, wrapd), asm.setbyte(RND3, 0), wrapd,
         Op(bytes([0x95, CNT[0], CNT[1]])), asm.if_byte(CNT, ">=", NC, again_), asm.if_byte(ROUND, "==", 0, None)]
    last_try = cut[-1]
    cut += [asm.setbyte(USEDC[0], 0), asm.setbyte(USEDC[1], 0), asm.setbyte(USEDC[2], 0), asm.setbyte(ROUND, 1),
            asm.goto_back(r_top)]
    none_ = asm.setbyte(CI, 255)
    last_try.target = none_
    cut += [again_, none_, asm.ret()]
    scripts[ents["util"]] = {0: [asm.ret(), asm.ret()], 2: pick, 3: cut}

    # the girls' moments (670): walking off, effects, Cloud's calls
    force_turn = asm.nop()

    def leave(key, back=False, line=True, in_turn=True):
        k, stay = GR.ORDER.index(key), asm.nop()
        return mv.lose_affection(key) + (say_once(GR.NAMES[key] + "\n" + PF.PROFILES[key]["leave"]) if line else []) + \
            [hb._req(ents[key], 7, wait=False), asm.biton(LEFT, k)] + \
            ([asm.if_byte(E, "==", k, stay), asm.goto_back(force_turn) if back else asm.goto(force_turn), stay]
             if in_turn else [])

    def effects(eff):
        ops = mv._gil_ops(eff.get("gil", 0) * GR.RATE)
        if eff.get("rules"):
            ops += [asm.setbyte(mv.RULES, 1)]
        for g in eff.get("annoy", []):
            ops += mv._annoy(GR.ORDER.index(g), leave(g, in_turn=False))
        return ops

    def choose(ask, choices):
        ops, first = hb._ask(sec, ask, [c[0] for c in choices])
        done = asm.nop()
        for j, (label, reply, eff) in enumerate(choices):
            nx = asm.nop()
            ops += [asm.if_byte(CHOICE, "==", first + j, nx)] + \
                hb._say(sec, reply + mv._gil_note(eff.get("gil", 0) * GR.RATE)) + effects(eff) + [asm.goto(done), nx]
        return ops + [done]

    def walkers_done():
        """Waits (up to 8 s) until no girl is mid-stroll (WALKING), so nobody is re-placed while a MOVE runs."""
        top, go = hb._w(1), asm.nop()
        return [asm.setbyte(WAITED, 0), top, asm.if_byte(WALKING, "!=", 0, go), Op(bytes([0x95, WAITED[0], WAITED[1]])),
                asm.if_byte(WAITED, "<", 240, go), asm.goto_back(top), go, hb._w(10)]
    place_all = lambda: [hb._req(e, 2, wait=False) for e in (CL, ents["cloudb"], *girl_ents, ents["camera"],
                                                             ents["gauge"], ents["icon"])] + [hb._w(PLACE_WAIT)]
    stage_all = lambda: [hb._req(e, 9, wait=False) for e in (CL, ents["cloudb"], *girl_ents, ents["camera"],
                                                             ents["gauge"])] + [hb._w(max(S.D.CUT_FADE, PLACE_WAIT))]
    pause = mv._pause_ops(hb, sec, actors, ents["hush3"], lambda block: ch(E, [block(key) for key in GR.ORDER]),
                          lambda no: [asm.if_byte(HOLDP, "==", 1, no)], ents["icon"], lambda key: GR.RATE,
                          slot_of=GR.ORDER.index, leave=leave, uneasy=None, desperate=1,
                          speaker=(None, [("{CLOUD}", GR.HOLD_CLOUD[:1], GR.HOLD_STERN)]))
    POS_, VEL, PR, TOT, FR, RATE, T, SV, NEXT, NT, FT = (mv.POS, mv.VEL, mv.PR, mv.TOT, mv.FR, mv.RATE, mv.T, mv.S,
                                                        mv.NEXT, mv.NT, mv.FT)
    RUN, STEP, NEW, FIN = mv.RUN, mv.STEP, mv.NEW, mv.FIN

    main = [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS_, 500), asm.setword(VEL, 1000),
            asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(STEP, 1),
            asm.setbyte(K, 0), asm.setword(NEXT, 300), asm.setbyte(FIN, 0), asm.setbyte(E, 255), asm.setbyte(VV, 0),
            asm.setbyte(LEFT, 0), asm.setbyte(mv.RULES, 0), asm.setbyte(mv.CTRL, 0), asm.setbyte(mv.TP, 0),
            asm.setbyte(LASTP, 255), asm.setbyte(LAST, 0), asm.setbyte(WANDER, 0), asm.setbyte(SEGPLACE, 0),
            asm.setbyte(SPD, 0), asm.setbyte(HOLDP, 0), asm.setbyte(ORALP, 0), asm.setbyte(HLI, 0),
            asm.setbyte(WALKING, 0)] + \
        [asm.setbyte(v, 0) for v in USEDC] + [asm.setbyte(mv._ann(k), 0) for k in range(n_g)]
    if S.chamber:                                    # (each girl her own home slot; nobody chosen yet)
        main += [asm.setbyte(GS(k), k) for k in range(n_g)] + [asm.setbyte(USEDG, 0)]
    # the intro: everyone standing round the cameraman (the intro staging is the last CI)
    main += [asm.setbyte(CI, NC)] + stage_all() + [hb._w(12), Op(hb.FADE_IN), Op(b"\x6C")]
    main += hb._say(sec, GR.INTRO_TALK) + choose(GR.INTRO_ASK, GR.INTRO_CHOICES)
    for t_ in S.D.INTRO:
        main += say(t_)
    music = mv.MUSIC if S.D.MUSIC is None else S.D.MUSIC
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, music]) + bytes(8)), asm.setword(FR, 0), asm.setword(PR, 0)]
    first_p = [p["key"] for p in S.D.POSITIONS].index(S.D.FIRST[0])
    main += [asm.setbyte(PI, first_p), asm.setbyte(NPART, S.D.FIRST[1])]

    # a segment: the position (the first is S.D.FIRST), how many girls, their order, the slots
    seg_top, chosen, differs, wrapped = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    # (LASTP 255 = the first segment: S.D.FIRST, set above); else at random, never the last one again
    main += [seg_top, asm.if_byte(LASTP, "!=", 255, chosen),
             Op(bytes([0x99, RND3[0], RND3[1]])), Op(bytes([0x8D, RND3[0] << 4, RND3[1], NP])),
             asm.if_byte(RND3, "==", LASTP, differs), Op(bytes([0x95, RND3[0], RND3[1]])),
             asm.if_byte(RND3, ">=", NP, differs), asm.setbyte(RND3, 0), differs, asm.setbyte(PI, RND3)]
    # how many girls: counts[0] + random 0 .. span - 1 (MOD takes a literal: one per distinct span)
    main += ch(PI, [[asm.setbyte(NMIN, p["counts"][0]), asm.setbyte(NSPAN, p["counts"][1] - p["counts"][0] + 1)]
                    for p in S.D.POSITIONS])
    main += [Op(bytes([0x99, RND3[0], RND3[1]])), asm.setbyte(NPART, NMIN)]
    for sp in sorted({p["counts"][1] - p["counts"][0] + 1 for p in S.D.POSITIONS}):
        nx = asm.nop()
        main += [asm.if_byte(NSPAN, "==", sp, nx), Op(bytes([0x8D, RND3[0] << 4, RND3[1], sp])),
                 Op(bytes([0x85, 0x55, NPART[1], RND3[1]])), nx]
    main += [chosen, asm.setbyte(LASTP, PI)]
    if S.chamber:
        main += [asm.setbyte(NPART, 1)]
    # girls still here (PRES); none = everyone walked
    walkout = asm.nop()
    main += [asm.setbyte(PRES, 0)]
    for k in range(n_g):
        nx = asm.nop()
        main += [asm.if_byte(LEFT, "bit_off", k, nx), Op(bytes([0x95, PRES[0], PRES[1]])), nx]
    fits = asm.nop()
    main += [asm.if_byte(PRES, "!=", 0, walkout), asm.if_byte(NPART, ">", PRES, fits), asm.setbyte(NPART, PRES), fits]
    wrap = asm.nop()
    if S.chamber:                                    # one girl not chosen yet (walked off = chosen); the last
        for k in range(n_g):                         # one chosen: this is the last segment
            nx = asm.nop()
            main += [asm.if_byte(LEFT, "bit_on", k, nx), asm.biton(USEDG, k), nx]
        last_no = asm.nop()
        main += [hb._req(ents["util"], 2), asm.setbyte(ORD(0), PICK), asm.if_byte(PICK, "!=", 255, wrap),
                 asm.if_byte(USEDG, "==", (1 << n_g) - 1, last_no), asm.setbyte(LAST, 1), last_no]
    else:
        main += [asm.setbyte(USEDG, LEFT)]
        for i in range(n_g):
            main += [hb._req(ents["util"], 2), asm.setbyte(ORD(i), PICK)]
    # the position's vars and slots
    def cutaway(c):
        ops = hb._say(sec, c["talk"])
        if c.get("ask"):
            ops += choose(c["ask"], c["choices"])
        return ops
    def pos_ops(p):
        pos, sl = S.D.POSITIONS[p], B["slots"][p]
        h = S.HOLD_L.index(pos["girl"]) if pos.get("hold") else 0
        ops = [asm.setbyte(GLI, S.LET.index(pos["girl"])), asm.setbyte(CLI, S.CLET.index(pos["cloud"])),
               asm.setbyte(HOLDP, 1 if pos.get("hold") else 0), asm.setbyte(ORALP, 1 if pos.get("oral") else 0),
               asm.setbyte(HLI, h), asm.setbyte(QUEUE, 1 if len(B["stations"][p]) == 1 else 0)]
        for s, (x, y, z, t, d, a, kind, wp) in enumerate(sl):
            ops += [asm.setword(SLOT(s, 0), x & 0xFFFF), asm.setword(SLOT(s, 2), y & 0xFFFF),
                    asm.setword(SLOT(s, 4), z & 0xFFFF), asm.setbyte((5, SLOT(s, 6)[1]), d),
                    asm.setbyte((5, SLOT(s, 8)[1]), a), asm.setword(SLOT(s, 10), t), asm.setbyte(SK(s), kind)]
            if kind == 2:                                 # (only a stroller's waypoint is read)
                ops += [asm.setword(WX(s), wp[0] & 0xFFFF), asm.setword(WY(s), wp[1] & 0xFFFF)]
        return ops
    main += ch(PI, [pos_ops(p) for p in range(NP)])
    end_at = S.D.MINUTES * 1800
    not_last = asm.nop()
    if not S.chamber:                                # (the chamber ends when all are chosen)
        main += [asm.if_word(FR, ">=", end_at, not_last), asm.setbyte(LAST, 1)]
    main += [not_last,
             asm.setbyte(LASTT, NPART), Op(bytes([0x97, LASTT[0], LASTT[1]])), asm.setbyte(TURNI, 0),
             asm.setbyte(SEGPLACE, 1)]

    # a turn: E = the next girl in the order; the slots (a queue: she swaps into the station); placed
    turn_top, skip_turn, next_turn = asm.nop(), asm.nop(), asm.nop()
    main += [turn_top] + ch(TURNI, [[asm.setbyte(E, ORD(i))] for i in range(n_g)])
    main += [asm.if_byte(E, "!=", 255, skip_turn)]
    for k in range(n_g):
        nx = asm.nop()
        main += [asm.if_byte(E, "==", k, nx), asm.if_byte(LEFT, "bit_off", k, skip_turn), nx]
    for i in range(0 if S.chamber else n_g):         # (the chamber: GS(k) = k throughout)
        q1, q2, done = asm.nop(), asm.nop(), asm.nop()
        main += [asm.setbyte(TS, i), asm.if_byte(QUEUE, "==", 1, done),
                 asm.if_byte(TURNI, "==", i, q1), asm.setbyte(TS, 0), asm.goto(done), q1]
        if i == 0:
            main += [asm.setbyte(TS, TURNI)]
        main += [done]
        main += ch(ORD(i), [[asm.setbyte(GS(k), TS)] for k in range(n_g)])
    main += [asm.setbyte(STN, 0)] + ch(E, [[asm.setbyte(STN, S.bed_of[k] if S.chamber else GS(k))] for k in range(n_g)])
    rowq = asm.nop()
    main += [asm.if_byte(QUEUE, "==", 1, rowq), asm.setbyte(STN, 0), rowq]
    main += ch(PI, [[asm.setbyte(QI, B["qbase"][p])] for p in range(NP)]) + [Op(bytes([0x85, 0x55, QI[1], STN[1]]))]
    spd0 = asm.nop()
    main += [asm.setbyte(SPD, 0), asm.if_byte(STEP, ">=", 2, spd0), asm.setbyte(SPD, 1), spd0]
    if S.chamber:
        # (user) the choice: fade in on Cloud walking up to her, "I choose you.", her answer; then the bed
        reply = []
        for key in GR.ORDER:
            rs = S.D.REPLIES[key]
            reply.append([Op(bytes([0x99, RND3[0], RND3[1]])), Op(bytes([0x8D, RND3[0] << 4, RND3[1], len(rs)]))] +
                         ch(RND3, [hb._say(sec, t_) for t_ in rs]))
        main += [asm.setbyte(CH, E), asm.setbyte(E, 255), asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(mv.FAST_OUT),
                 Op(b"\x6C")] + \
            [hb._req(e, 2, wait=False) for e in girl_ents] + \
            [hb._req(CL, 8, wait=False), hb._req(ents["cloudb"], 10, wait=False), hb._req(ents["gauge"], 9, wait=False),
             hb._req(ents["camera"], 2, wait=False), hb._w(PLACE_WAIT), Op(mv.FAST_IN), Op(b"\x6C"),
             hb._req(ents["cloudb"], 8), hb._w(8)] + hb._say(sec, S.D.CHOOSE) + ch(CH, reply) + [hb._w(8),
                                                                                                 asm.setbyte(E, CH)]
    main += [asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(mv.FAST_OUT), Op(b"\x6C")] + place_all() + \
        [Op(mv.FAST_IN), Op(b"\x6C"), asm.setbyte(SEGPLACE, 0), asm.setbyte(WANDER, 1)]
    turn_len = [Op(bytes([0x99, RND3[0], RND3[1]])), Op(bytes([0x8D, RND3[0] << 4, RND3[1], 8])),
                asm.setword(SV, RND3), hb._arith(0x8A, SV, S.D.TURN_RANGE // 8),
                asm.setword(NEXT, FR), hb._arith(0x86, NEXT, S.D.TURN_MIN), Op(bytes([0x86, 0x66, NEXT[1]]) +
                                                                            struct.pack("<H", SV[1]))]
    main += [asm.setword(POS_, 500), asm.setword(VEL, 1000), asm.setword(PR, 0), asm.setword(NT, FR),
             hb._arith(0x86, NT, mv.TICK)] + turn_len + mv._pause_arm(hb, S.D.TURN_MIN) + [asm.setbyte(RUN, 1)]
    # the tick (as the group's physics)
    lost, hi_red, ending = asm.nop(), asm.nop(), asm.nop()
    tick, wait1, go = asm.nop(), hb._w(1), asm.nop()
    A_, B_, C_, VMAX, DANGER = mv.A, mv.B, mv.C, mv.VMAX, mv.DANGER
    main += [tick, wait1, asm.if_word(FR, "<", NT, go), asm.goto_back(wait1), go, hb._arith(0x86, NT, mv.TICK),
             asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
             hb._arith(0x8A, VEL, 5), hb._arith(0x8C, VEL, 6),
             hb._arith(0x86, VEL, 1000 - 1000 * 5 // 6 - B_ - 500 // C_),
             asm.setword(SV, T), hb._arith(0x8A, SV, A_), hb._arith(0x86, VEL, SV),
             asm.setword(SV, POS_), hb._arith(0x8C, SV, C_), hb._arith(0x86, VEL, SV)]
    lo, hi = asm.nop(), asm.nop()
    main += [asm.if_word(VEL, "<", 1000 - VMAX, lo), asm.setword(VEL, 1000 - VMAX), lo,
             asm.if_word(VEL, ">", 1000 + VMAX, hi), asm.setword(VEL, 1000 + VMAX), hi,
             asm.setword(SV, POS_), hb._arith(0x86, SV, VEL),
             asm.if_word(SV, ">=", 1000 + DANGER, lost),
             asm.setword(POS_, SV), hb._arith(0x88, POS_, 1000),
             asm.if_word(POS_, "<=", 1000 - DANGER, hi_red)]
    no_call = asm.nop()                              # the finisher: the last segment's last turn
    main += [asm.if_byte(LAST, "==", 1, no_call), asm.if_byte(TURNI, "==", LASTT, no_call),
             asm.if_byte(FIN, "==", 0, no_call),
             asm.setword(FT, FR), hb._arith(0x86, FT, mv.FINISH_FRAMES), asm.if_word(FT, ">=", NEXT, no_call),
             asm.setbyte(FIN, 1), hb._req(ents["shout"], 2, wait=False), no_call]
    done, same, same_spd = asm.nop(), asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(SV, T), hb._arith(0x8A, SV, 16),
             hb._arith(0x86, RATE, SV), asm.setbyte(NEW, 0)]
    for s_, th in enumerate(mv.RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s_ + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW),
             asm.setbyte(TS, 0), asm.if_byte(STEP, ">=", 2, same_spd), asm.setbyte(TS, 1), same_spd,
             asm.if_byte(TS, "!=", SPD, same), asm.setbyte(SPD, TS),
             hb._req(ents["cloudb"], 3, wait=False)] + [hb._req(e, 3, wait=False) for e in girl_ents] + [same]
    main += pause
    stay = asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay), force_turn, asm.setbyte(RUN, 0), asm.goto(next_turn), stay,
             asm.goto_back(tick)]
    seg_end = asm.setbyte(RUN, 0)
    main += [skip_turn, next_turn, Op(bytes([0x95, TURNI[0], TURNI[1]])), asm.if_byte(TURNI, "<", NPART, seg_end),
             asm.goto_back(turn_top)]
    # the segment's end: the last one = the wrap; else a cutaway, then the next segment
    nocut = asm.nop()
    main += [seg_end, Op(b"\x54\x01"), asm.if_byte(LAST, "==", 0, wrap), asm.setbyte(WANDER, 0)] + walkers_done()
    if S.chamber:                                    # (user) breaks now and then
        main += [Op(bytes([0x99, RND3[0], RND3[1]])), asm.if_byte(RND3, "<", S.D.CUT_CHANCE, nocut)]
    main += [hb._req(ents["util"], 3), asm.if_byte(CI, "!=", 255, nocut),
             Op(mv.FAST_OUT), Op(b"\x6C")] + stage_all() + [Op(mv.FAST_IN), Op(b"\x6C")]

    main += ch(CI, [cutaway(c) for c in S.D.CUTS]) + [nocut, asm.goto_back(seg_top)]

    # the endings (as the group's)
    rx, ry, rz, rt, rdir = back

    def out():
        stop = hb._w(30)
        return [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir), stop,
                asm.goto_back(stop), asm.ret()]
    gil = GR.RATE * mv.FINISH_BONUS
    state = [asm.setword(mv.MOVIE_PRESSES, TOT), asm.setword(mv.MOVIE_AT, mv.HB_MINUTES), asm.setbyte(mv.MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")]
    main += [hi_red, sound(mv.RED_SOUND), asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"),
             Op(b"\x54\x02"), Op(bytes([0xF2, 0, 0, 0, 0x10, mv.FANFARE]) + bytes(8)), hb._w(45)]
    main += say("“WOW! What a FINISHER!\n That's going straight on the poster!”")
    main += [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)]
    main += say("“Here's a bonus, on the spot:\n {:,} gil. You earned it, star!”".format(gil))
    main += hb._say(sec, GR.AFTERMATH) + [asm.goto(ending)]
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! You lost it, man!\n ...Fine. We'll sell what we've got.”")
    main += state + out()
    main += [walkout, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)] + hb._say(sec, GR.WALKOUT) + state + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! Magnificent!”")
    someone, edone = asm.nop(), asm.nop()
    stayed = GR.RATE * GR.STAYED_BONUS
    main += [ending, asm.if_byte(LEFT, "==", 0, someone)] + hb._say(sec, S.D.END_TALK) + mv._gil_ops(stayed) + \
        hb._say(sec, GR.END_STAYED.format(gil=stayed)) + [asm.goto(edone), someone] + hb._say(sec, GR.END_LEFT) + [edone]
    main += [asm.biton(*SPECIAL_ON)] + state + out()
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main}


def run(S, ctx, label, layout):
    """Builds the set S (its field replaced in ctx); `layout` = the work/ file for offline renders."""
    mv, hb, dt = _mods()
    B = _build(S, ctx, ctx.movie_back)
    _stage(S, ctx, B)
    _director(S, ctx, B, ctx.movie_back)
    dt._blank(B["sec"], B["scripts"])
    B["f"].set_section("models", B["loader"].build())
    B["f"].sections[0] = B["sec"].build()
    n_text = struct.unpack_from("<H", B["sec"].tail, 0)[0]
    print("  %s on %s (%d positions, %d cutaways, %d texts, script %d bytes, code %d)" % (
        label, S.FIELD, len(S.D.POSITIONS), len(S.D.CUTS), n_text, len(B["f"].sections[0]),
        struct.unpack_from("<H", B["f"].sections[0], 4)[0]))
    assert n_text <= 255, n_text
    import json
    import os
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, layout), "w") as fh:     # (offline renders, tuning)
        json.dump(dict(positions=[p["key"] for p in S.D.POSITIONS], stations=B["stations"], slots=B["slots"],
                       cams=B["cams"]), fh)
    for p, (pos, st) in enumerate(zip(S.D.POSITIONS, B["stations"])):
        print("    %-10s %s+%s x%d: %s" % (pos["key"], pos["girl"], pos["cloud"], len(st),
                                         " ".join("%s/%s" % (g[:3], c[:3]) for g, gd, c, cd in st[:3])))

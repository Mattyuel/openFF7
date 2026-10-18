"""(user) The beach party: the loose group shoot (`_loose_engine`) on Costa del Sol's beach (data
`_beach_party`, poses `_beach_poses`). The set: a copy of del3 under BPD.FIELD (its own script blanked but the
waves' background animation, moved to entity `direct`; models Cloud + one hidden, as the studio's base).
Stations: the five loungers (walkable pieces of the walkmesh: Cloud lounging at LOUNGERS' spots, a rider /
a waiting girl at `BP.sunbed_offset` from it), and pairs placed on the open sand, at the tide line and in the
shallows: each pair's relative placement is the studio's (670's one-girl spots / the group's "end"), turned
to the DIR that shows it side-on with both on the ground (`_pair`). Watchers: lounging on a free lounger,
sunbathing / kneeling on the dry sand, or standing about and wading (strolls checked walkable)."""
import importlib
import math

import _beach_party as BPD
import _beach_poses as BP
import _loose_engine as LE
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Script

# the loungers (del3's walkmesh): x range, y of the seat's foot end, the seat / backrest junction, the top
LOUNGERS = [((-477, -405), (323, 411, 449)), ((-239, -167), (323, 411, 450)), ((295, 367), (277, 365, 403)),
            ((270, 342), (656, 744, 782)), ((517, 589), (656, 744, 782))]
LOUNGE_IN = 19                  # Cloud's lounging spot this far in front of the junction
SUNBED = 2                      # the reverse sunbed's lounger (screen centre right)
SAND = (170, 290)               # the open dry sand's y band (between the tide and the loungers)
SURF = (70, 140)                # the tide line's y band (ankle deep at most)
DRY = -4                        # heights above this are dry sand
DEEP = -75                      # nobody walks deeper
ROW_GAP = {"A": 140, "F": 140, "C": 110}     # spots in a row this far apart (x): lying pairs side-on are long
ROW_GAP_DEFAULT = 75
LOCKED = (0x49, 0x38)           # del3's init locked these triangles


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


# ---- the set's ground ------------------------------------------------------------------------------
class Ground:
    """Walkable triangles (not a lounger, not raised, not locked) with bounding boxes for fast lookups."""
    def __init__(self, mesh):
        self.mesh = mesh
        self.box = [(min(v[0] for v in t), max(v[0] for v in t), min(v[1] for v in t), max(v[1] for v in t))
                    for t in mesh.tris]
        lounger = lambda x, y: any(x0 - 2 <= x <= x1 + 2 and ys[0] - 2 <= y <= ys[2] + 2 for (x0, x1), ys in LOUNGERS)
        self.walk = [t for t in range(len(mesh.tris)) if t not in LOCKED and
                     max(v[2] for v in mesh.tris[t]) < 4 and not lounger(*mesh.center(t)[:2])]
        self.lounger = lounger

    def at(self, x, y):
        """(walkable triangle, height) under (x, y), or None."""
        for t in self.walk:
            b = self.box[t]
            if b[0] <= x <= b[1] and b[2] <= y <= b[3] and self.mesh.contains(t, x, y):
                return t, self.mesh.height(t, x, y)
        return None

    def grid(self, step):
        out = []
        for t in self.walk:
            b = self.box[t]
            for x in range(math.ceil(b[0] / step) * step, int(b[1]) + 1, step):
                for y in range(math.ceil(b[2] / step) * step, int(b[3]) + 1, step):
                    if self.mesh.contains(t, x, y):
                        out.append((x, y, round(self.mesh.height(t, x, y)), t))
        return out


_G = {}


def _ground(mesh):
    if id(mesh) not in _G:
        _G[id(mesh)] = Ground(mesh)
    return _G[id(mesh)]


def _lounge_spots(mesh):
    """Cloud's lounging spot (x, y, z, tri) on each lounger."""
    out = []
    for (x0, x1), (y0, yj, yt) in LOUNGERS:
        x, y = round((x0 + x1) / 2), yj - LOUNGE_IN
        ts = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y)]
        t = max(ts, key=lambda t: mesh.height(t, x, y))
        z = mesh.height(t, x, y)
        assert 4 < z < 14, (x, y, z)                      # (the seat)
        out.append((x, y, round(z), t))
    return out


def _supports(S, mesh):
    g = _ground(mesh)
    floor = [p for p in g.grid(8) if DEEP <= p[2] <= 3]
    off = S.off
    beds = [(x + round(off[0]), y + round(off[1]), z + round(off[2]), t) for x, y, z, t in _lounge_spots(mesh)]
    return floor, beds


def _on(S, mesh, p, top, margin=4):
    g = _ground(mesh)
    for dx, dy in ((0, 0), (margin, 0), (-margin, 0), (0, margin), (0, -margin)):
        h = g.at(p[0] + dx, p[1] + dy)
        if h is None or abs(h[1] - top) > 12:
            return False
    return True


def _walkable(S, mesh, p, margin):
    g = _ground(mesh)
    for dx, dy in ((0, 0), (margin, 0), (-margin, 0), (0, margin), (0, -margin)):
        h = g.at(p[0] + dx, p[1] + dy)
        if h is None or h[1] < DEEP:
            return False
    return True


def _bed_id(S, c):
    for i, ((x0, x1), ys) in enumerate(LOUNGERS):
        if x0 - 2 <= c[0] <= x1 + 2 and ys[0] - 2 <= c[1] <= ys[2] + 2:
            return i
    return None


# ---- stations ---------------------------------------------------------------------------------------
def _rel(ctx, girl, cloud):
    """The studio's pair: (dx, dy) Cloud from her, her lift and his above the ground under her, DIRs."""
    places, gs = ctx.movie_places, ctx.group_spots
    letter = {"Y": "D"}.get(girl, girl)
    if letter == "O":
        g, gd, c, cd = gs["girl"][12], gs["gdir"][12], gs["cloud"][12], gs["cdir"][12]
    elif letter == "U":                                    # (673: she shares his spot, turned round)
        return (0, 0, 0, 0, 0, 128)
    else:
        pl = places["ABCDEFGHIJ".index(letter)]
        g, gd, c, cd = pl["girl"], pl["gdir"], pl["cloud"], pl["cdir"]
    top = max(t for t in (0, 54, 100, 125) if t <= g[2] + 2)
    return (c[0] - g[0], c[1] - g[1], g[2] - top, c[2] - top, gd, cd)


def _pair(S, ctx, mesh, cam, pos, gx, gy):
    """The pair at her spot (gx, gy), turned to the DIR showing it most side-on with everyone on the ground;
    None if no turn fits."""
    mv, hb, _ = _mods()
    g0 = _ground(mesh).at(gx, gy)
    if g0 is None:
        return None
    top = g0[1]
    dx, dy, glift, clift, gd, cd = _rel(ctx, pos["girl"], pos["cloud"])
    best = None
    for dd in range(0, 256, 8):
        a = dd * 2 * math.pi / 256
        cx, cy = gx + dx * math.cos(a) - dy * math.sin(a), gy + dx * math.sin(a) + dy * math.cos(a)
        c0 = _ground(mesh).at(cx, cy)
        if c0 is None:
            continue
        gdir, cdir = (gd + dd) % 256, (cd + dd) % 256
        her = LE._world(ctx, mv.RUBY_HRC, "zm%s1.a" % pos["girl"].lower(), 7, gx, gy, top + glift, gdir)
        his = LE._world(ctx, hb.CLOUD_BARE_HRC, "zn%s1.a" % pos["cloud"].lower(), 7, cx, cy, c0[1] + clift, cdir)
        pts = [her[k] for k in ("root", "head", "l_foot", "r_foot")] + [his[k] for k in ("root", "l_foot", "r_foot")]
        if not all(_on(S, mesh, p, top, 4) for p in pts):
            continue
        # side-on: the line from her to him (or, sharing a spot, her facing) long on screen; Cloud not in
        # front of her
        span = lambda p, q: math.dist(cam.project(*p), cam.project(*q)) / (math.dist(p, q) + 1e-6)
        if math.dist(her["root"][:2], his["root"][:2]) > 8:
            score = span(her["root"], his["root"])
        else:
            a_ = gdir * 2 * math.pi / 256
            score = span(her["root"], (her["root"][0] + 20 * math.sin(a_), her["root"][1] - 20 * math.cos(a_),
                                       her["root"][2]))
        if mv._view_depth(cam, his["chest"]) >= mv._view_depth(cam, her["chest"]) - 3:
            score += 0.3
        if best is None or score > best[0]:
            best = (score, (gx, gy, round(top + glift), g0[0]), gdir, (round(cx), round(cy), round(c0[1] + clift), c0[0]),
                    cdir)
    return best[1:] if best else None


def _stations(S, ctx, mesh, cam):
    mv, hb, _ = _mods()
    ls = _lounge_spots(mesh)
    off, offv = S.off, S.offv
    out = []
    for pos in BPD.POSITIONS:
        st = []
        if pos["place"] == "loungers":
            for x, y, z, t in ls:
                st.append(((x + round(off[0]), y + round(off[1]), z + round(off[2]), t), 0, (x, y, z, t), 0))
        elif pos["place"] == "sunbed":
            x, y, z, t = ls[SUNBED]
            st.append(((x + round(offv[0]), y + round(offv[1]), z + round(offv[2]), t), 128, (x, y, z, t), 0))
        else:
            n, hint = pos.get("spots", 1), pos["at"]
            if pos["place"] == "shallows":
                want = pos["depth"]
                ys = sorted(range(-300, 160, 6), key=lambda y: abs((_ground(mesh).at(hint, y) or (0, 999))[1] - want))[:6]
            else:
                band = SAND if pos["place"] == "sand" else SURF
                ys = list(range(band[0], band[1] + 1, 10))
                ys.sort(key=lambda y: abs(y - sum(band) / 2))
            xs = sorted(range(-1000, 1001, 15), key=lambda x: abs(x - hint))
            for x in xs:
                if len(st) == n:
                    break
                if any(abs(x - s_[0][0]) < ROW_GAP.get(pos["girl"], ROW_GAP_DEFAULT) for s_ in st):
                    continue
                for y in ys:
                    if pos.get("target"):
                        g0 = _ground(mesh).at(x, y)
                        if g0 is None:
                            continue
                        try:
                            got = LE._solve(S, ctx, mesh, cam, pos, x, [y], round(g0[1]), dirs=range(0, 256, 8))
                        except AssertionError:
                            continue
                        g, gd, c, cd = got
                        got = (g + (g0[0],), gd, c + (LE._tri(mesh, c[0], c[1], c[2], 13),), cd)
                    else:
                        got = _pair(S, ctx, mesh, cam, pos, x, y)
                    if got:
                        st.append(got)
                        break
            assert len(st) == n, ("no room for", pos["key"], len(st), n)
        out.append(st)
    return out


# ---- watchers ----------------------------------------------------------------------------------------
def _bed_watch(S, ctx, mesh, c, k, free, face, queue=False):
    return 0, S.G_EXTRA                                    # lounging (her spot is a rider's: `lounge_at`)


def _floor_watch(S, ctx, mesh, c, k, free, face):
    """On the dry sand: sunbathing (lying along the shore if she fits) / kneeling / (None) standing about.
    In the water: standing (and wading about)."""
    mv, _, _ = _mods()
    if c[2] <= DRY or k % 3 == 1:
        return None
    if k % 3 == 0:
        for d in (64, 192):
            body = LE._world(ctx, mv.RUBY_HRC, "zmk0.a", 0, c[0], c[1], c[2], d)
            if all(_on(S, mesh, body[n], c[2], 2) for n in ("head", "l_foot", "r_foot")) and \
                    all(free(body[n], 16) for n in ("head", "l_foot")):
                return d, S.G_LIE[k % 2]
    return face, S.G_KNEEL[k % 2]


# ---- the field / sprites -------------------------------------------------------------------------------
def _make_field(S, ctx):
    """del3 copied: entities produce / direct (the waves' scripts) / ad / cloud / child, models Cloud + one."""
    f = FieldFile(ctx.field(BPD.BASE).build())
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    assert sec.entity_index("wave") == 0
    wave = {k: sec.script_ops(0, k) for k in (0, 1)}
    for k in (0, 1):                                       # (the wave's main ends in a goto: never reached)
        if wave[k][-1].op != 0x00:
            wave[k] = wave[k] + [asm.ret()]
    ids = {id(o) for ops in wave.values() for o in ops}
    assert all(o.target is None or id(o.target) in ids for ops in wave.values() for o in ops), "wave jumps out"
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in ("produce", "direct", "ad", "cloud", "child")]
    sec.entry = [[sec._end] * 32 for _ in range(5)]
    sec.ops = [o for ops in wave.values() for o in ops]
    sec.entry[1][0], sec.entry[1][1] = wave[0][0], wave[1][0]
    f.sections[0] = sec.build()
    loader = ModelLoader(f.section("models"))
    assert ModelLoader.hrc(loader.models[0]) == "AAAA.HRC", ModelLoader.hrc(loader.models[0])
    loader.models = [loader.models[0], loader.models[8]]   # Cloud, and a passer-by kept hidden ("child")
    f.set_section("models", loader.build())
    return f, {1: wave}


def _sprites(S, ctx, loader, mesh, cam, near):
    mv, _, _ = _mods()
    mm = mv.mm
    donor_loader = ModelLoader(ctx.field(mm.DONOR_FIELD).section("models"))
    scale = round(ModelLoader.entry_scale(donor_loader.models[mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    unit = 3.41 * scale / 512
    k = near / cam.zoom / unit
    names = {"QGIA": ("QGIB", "QGIC", "QGID"), "QCIA": ("QCIB", "QCIC", "QCID"), "QHIA": ("QHIB", "QHIC", "QHID")}
    old = mv.SPRITES
    mv.SPRITES = names
    try:
        sp = mv._sprites(ctx, mv.GAUGE_PX / 2 * k, mv.CURSOR_PX / 2 * k, mv.ICON_PX / 2 * k)
    finally:
        mv.SPRITES = old
    return [ModelLoader.with_scale(sp[h], scale) for h in names]


# ---- the poses ------------------------------------------------------------------------------------------
def _poses(ctx):
    """The beach's own poses (Ruby's skeleton / bare Cloud) and the girls' copies (670 `_retarget`)."""
    mv, _, _ = _mods()
    BP.build(ctx)
    for key, donor, bare, prefix, own, head_down, hrc in LE._cast():
        if own is None:
            entry = ModelLoader(ctx.field(donor[0]).section("models")).models[donor[1]]
            stand = ModelLoader.anims(entry)[0].split(".")[0].lower() + ".a"
            mv._retarget(ctx, ["ZMY%d.tor" % k for k in range(4)], prefix, hrc, stand, head_down)


def apply(ctx):
    _poses(ctx)
    off, offv = BP.sunbed_offset(ctx), BP.sunbed_offset(ctx, 128)
    S = LE.Set(BPD, BPD.FIELD, "ABCFHIJOUY", "IJO", "ACF", CLET="ABCDFHIJOUVW",
               extra=[("Z", lambda ctx_, name, bare, stand: BP.lounge_at(ctx_, name, bare, stand, off))],
               make_field=_make_field, supports=_supports, on=_on, walkable=_walkable, stations=_stations,
               bed_watch=_bed_watch, floor_watch=_floor_watch, bed_id=_bed_id, one_per_bed=True,
               cam_ok=lambda S, c: c[2] > DRY, sprites=_sprites, off=off, offv=offv)
    # the cutaways' stage: the open sand in the middle of the beach
    sx, sy = Camera(ctx.field(BPD.BASE).sections[1]).project(*BPD.STAGE_AT)
    BPD.STAGE = (round(sx), round(sy))
    LE.run(S, ctx, "679: the beach party", "beach_layout.json")

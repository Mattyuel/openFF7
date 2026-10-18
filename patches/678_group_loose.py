"""(user) The loose group shoot on the studio set (data `_movie_loose`, engine `_loose_engine`): a new set
(LZ.FIELD, never entered otherwise, replaced wholesale by a copy of the movie room mds7_w3); its stations are
the group shoot's (670 `ctx.group_spots`), the one-girl shoot's (`ctx.movie_places`) and positions solved
onto each bed / the floor; girls not taking part lie or kneel on a free bed or stand about and stroll."""
import importlib
import math

import _loose_engine as LE
import _movie_group as GR
import _movie_loose as LZ
from ff7 import triggers as tg
from ff7.field import FieldFile
from ff7.models import ModelLoader

CROWN = ((2, 18), 234, 7)           # (user) the crown: Cloud's offset from her, her DIR, his DIR
FLOOR_AT = (-60, -232)              # a floor station: the nearest spot to this where both fit
ALONG = (75, 60, 90, 50, 105, 40, 120)   # her spot this far into a bed from its near end (tried in turn)


def _mv():
    return importlib.import_module("670_movie")


def _make_field(S, ctx):
    f = FieldFile(ctx.field(_mv().BASE).build())
    trig = f.section("triggers")
    for slot in range(12):                               # no way out by walking
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    return f, {}


def _supports(S, mesh):
    """Floor points and bed-top points (x, y, z, tri) on a 6-unit grid."""
    floor, beds = [], []
    for x in range(-300, 301, 6):
        for y in range(-360, 41, 6):
            hits = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y)]
            for t in hits:
                z = round(mesh.height(t, x, y))
                (floor if abs(z) < 2 else beds).append((x, y, z, t))
    return floor, beds


def _on(S, mesh, p, top, margin=4):
    """p (x, y) lies on the support of height top (a bed top or the floor), `margin` inside its edge."""
    for dx, dy in ((0, 0), (margin, 0), (-margin, 0), (0, margin), (0, -margin)):
        if not any(mesh.contains(t, p[0] + dx, p[1] + dy) and abs(mesh.height(t, p[0] + dx, p[1] + dy) - top) < 3
                   for t in range(len(mesh.tris))):
            return False
    return True


def _stations(S, ctx, mesh, cam):
    """Per position: [(girl (x, y, z, tri), her DIR, Cloud (x, y, z, tri), his DIR)]."""
    places, gs = ctx.movie_places, ctx.group_spots
    out = []
    for pos in LZ.POSITIONS:
        st = []
        if pos["place"].startswith("group:"):
            ph = int(pos["place"].split(":")[1])
            for k in range(6):
                q = ph * 6 + k
                st.append((gs["girl"][q], gs["gdir"][q], gs["cloud"][q], gs["cdir"][q]))
        elif pos["place"] == "solo":
            assert pos["girl"] == pos["cloud"]
            pl = places[S.LET.index(pos["girl"])]
            st.append((pl["girl"], pl["gdir"], pl["cloud"], pl["cdir"]))
        elif pos.get("crown"):
            (ox, oy), gd, cd = CROWN
            for lanes, y_end, top in GR.BEDS:            # (the user's spot on the middle bed, the same on each)
                gx, gy = round(sum(lanes) / 2) - 1, y_end + 120
                g, c = (gx, gy, top), (gx + ox, gy + oy, top)
                st.append((g + (LE._tri(mesh, gx, gy, top),), gd, c + (LE._tri(mesh, c[0], c[1], top),), cd))
        elif pos["place"] == "beds":
            for lanes, y_end, top in GR.BEDS:
                g, gd, c, cd = LE._solve(S, ctx, mesh, cam, pos, round(sum(lanes) / 2), [y_end + a for a in ALONG], top)
                st.append((g + (LE._tri(mesh, *g[:2], top),), gd, c + (LE._tri(mesh, *c[:2], top),), cd))
        else:                                             # "floor": in front of the beds
            floor = sorted({(x, y) for x in range(-200, 201, 10) for y in range(-300, 41, 10) if _on(S, mesh, (x, y), 0, 8)},
                           key=lambda p: math.dist(p, FLOOR_AT))
            for x, y in floor:
                try:
                    g, gd, c, cd = LE._solve(S, ctx, mesh, cam, pos, x, [y], 0)
                    break
                except AssertionError:
                    continue
            else:
                raise AssertionError(("no floor for", pos["key"]))
            st.append((g + (LE._tri(mesh, *g[:2], 0),), gd, c + (LE._tri(mesh, *c[:2], 0),), cd))
        out.append(st)
    return out


def _bed_watch(S, ctx, mesh, c, k, free, face, queue=False):
    """On a bed: every other one lies along it (her head to its far end) if she fits, else kneels (waiting her
    turn in a queue: kneels)."""
    mv = _mv()
    if queue:
        return face, S.G_KNEEL[k % 2]
    if k % 2 == 0:
        body = LE._world(ctx, mv.RUBY_HRC, "zmk0.a", 0, c[0], c[1], c[2], 0x80)
        if all(_on(S, mesh, body[n], c[2], 2) for n in ("head", "l_foot", "r_foot")) and \
                all(free(body[n], 16) for n in ("head", "l_foot")):
            return 0x80, S.G_LIE[0]
    return face, S.G_KNEEL[0]


def _sprites(S, ctx, loader, mesh, cam, near):
    room = ModelLoader(ctx.field(_mv().GROUP_FIELD).section("models"))
    return [room.models[i] for i in (10, 11, 12)]          # the group set's (the same room: the same sizes)


STUDIO = LE.Set(LZ, LZ.FIELD, "ABCDEFGHIJO", "EIJO", "ACF",
                make_field=_make_field, supports=_supports, on=_on,
                walkable=lambda S, mesh, p, margin: _on(S, mesh, p, 0, margin),
                stations=_stations, bed_watch=_bed_watch, floor_watch=lambda *a: None,
                bed_id=lambda S, c: round(c[2]) if c[2] > 2 else None, one_per_bed=False,
                cam_ok=lambda S, c: True, sprites=_sprites)


def apply(ctx):
    LE.run(STUDIO, ctx, "678: the loose group shoot", "loose_layout.json")

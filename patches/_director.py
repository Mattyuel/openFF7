"""(user: "Add the director to the right of this scene (also to any other scenes he's missing from without him
blocking anything)") The Director (670's cameraman model) standing by a parody film's action: his model added
to a set (`add`), a spot found on the set's own floor to one side of the action on screen and clear of it
(`spot`), and his entity's scripts (`entity`: init = standing still (670 CAMERA_STILL), slot 2 = filming,
slot 3 = still again)."""
import math

from ff7 import asm
from ff7.script import Op


def add(ctx, loader, scale=None):
    """His model appended to `loader` (the movie's donor, rescaled to the set; `scale` = an entry scale to force,
    e.g. 686's 768). Returns (model index, film anim index, still anim index)."""
    import importlib
    from ff7.models import ModelLoader
    mv = importlib.import_module("670_movie")
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    anims = ModelLoader.anims(loader.models[cm])
    film = anims.index(mv.CAMERA_FILM)
    m = ModelLoader.only_anims(loader.models[cm], anims + [mv.CAMERA_STILL])
    if scale:
        m = ModelLoader.with_scale(m, scale)
    loader.models[cm] = m
    return cm, film, len(anims)


def spot(f, keep, side=1, gap=10, height=95, lift=0, fit=None):
    """A floor point for him (None if there's none), `side` 1 = screen-right of the action (-1 left): his screen box (feet to `height`
    field units up) `gap` px clear of the box round `keep` (field points the action covers: feet and heads),
    his feet level with the action's lowest point on screen (`lift` px higher), inside the background. `fit` =
    an extra test (x, y) -> bool. Returns (x, y, z, triangle)."""
    from ff7.camera import Camera
    from ff7.walkmesh import Walkmesh
    from ff7.background import Background
    cam = Camera(f.sections[1])
    mesh = Walkmesh(f.section("walkmesh"))
    bg = Background(f.section("background"))
    ts = bg.tiles()
    bx0, bx1 = min(t.dst_x for t in ts), max(t.dst_x + t.width for t in ts)
    by0, by1 = min(t.dst_y for t in ts), max(t.dst_y + t.height for t in ts)
    P = [cam.project(*p) for p in keep]
    x0, x1 = min(p[0] for p in P), max(p[0] for p in P)
    yb = max(p[1] for p in P) - lift
    best = None
    for i, tr in enumerate(mesh.tris):
        for a, b in ((1 / 3, 1 / 3), (0.6, 0.2), (0.2, 0.6), (0.2, 0.2)):
            c = 1 - a - b
            x = tr[0][0] * a + tr[1][0] * b + tr[2][0] * c
            y = tr[0][1] * a + tr[1][1] * b + tr[2][1] * c
            z = tr[0][2] * a + tr[1][2] * b + tr[2][2] * c
            if mesh.find(round(x), round(y)) is None or (fit and not fit(x, y)):
                continue
            feet, head = cam.project(x, y, z), cam.project(x, y, z + height)
            half = 0.3 * abs(feet[1] - head[1]) + 4                     # (his arms / camera: about a third as wide)
            hx0, hx1 = min(feet[0], head[0]) - half, max(feet[0], head[0]) + half
            if not (bx0 + 4 < hx0 and hx1 < bx1 - 4 and by0 < head[1] and feet[1] < by1 - 4):
                continue
            clear = hx0 - (x1 + gap) if side > 0 else (x0 - gap) - hx1
            if clear < 0:
                continue
            score = clear + abs(feet[1] - yb) * 2.5                       # (level with the action first)
            if best is None or score < best[0]:
                best = (score, (round(x), round(y), round(z), mesh.find(round(x), round(y))))
    return best[1] if best else None


def entity(model, at, d, film, still, xyzi, animb, hidden=False):
    """His entity: init standing still at `at` (x, y, z, triangle) facing DIR d; 2 filming (and shown); 3 still.
    animb = a function making an ANIMB op (670 `_animb`). `hidden`: not shown until slot 2 (user: in the
    elevator he appears only after the fade into the scene)."""
    loop_ = lambda i: [animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    x, y, z, t = at
    return {0: [Op(bytes([0xA1, model])), xyzi(x, y, z, t), Op(bytes([0xB3, 0, d % 256])),
                Op(b"\xA4\x00" if hidden else b"\xA4\x01"),
                Op(b"\x7E\x01"), Op(b"\xC7\x01")] + loop_(still) + [asm.ret(), asm.ret()],
            2: [Op(b"\xA4\x01")] + loop_(film) + [asm.ret()],
            3: loop_(still) + [asm.ret()]}


def facing(x, y, tx, ty):
    """DIR facing from (x, y) to (tx, ty)."""
    a = math.atan2(tx - x, -(ty - y))
    return round(a * 128 / math.pi) % 256


def keep_from(scripts, ents, height=95):
    """The field points `ents`' scripts (entity indices in `scripts` {entity: {slot: ops}}) are placed at by
    literal XYZIs, feet and head (`height` up): the action the Director must stay clear of."""
    import struct
    out = []
    for e in ents:
        for ops in scripts.get(e, {}).values():
            for o in ops:
                raw = getattr(o, "raw", None)
                if raw and raw[0] == 0xA5 and raw[1] == 0 and raw[2] == 0 and len(raw) == 11:
                    x, y, z, _ = struct.unpack_from("<hhhH", raw, 3)
                    out += [(x, y, z), (x, y, z + height)]
    assert out, "no XYZI to keep clear of"
    return out


def place(f, scripts, ents, model, film, still, xyzi, animb, side=1, hidden=False, **kw):
    """His entity's scripts, placed `side` of every XYZI the actor entities `ents` use (`spot`), facing the
    middle of them. Returns (scripts, (x, y, z))."""
    keep = keep_from(scripts, ents, kw.pop("height", 95))
    at = None
    for sd, gap in ((side, kw.pop("gap", 10)), (-side, 10), (side, -10), (-side, -10)):     # (else the other side,
        at = spot(f, keep, side=sd, gap=gap, **kw)                                          #  else a little overlap)
        if at:
            break
    assert at, "no spot for the Director"
    x, y, z, t = at
    cx = sum(p[0] for p in keep) / len(keep)
    cy = sum(p[1] for p in keep) / len(keep)
    return entity(model, (x, y, z, t), facing(x, y, cx, cy), film, still, xyzi, animb, hidden), (x, y, z)


"""(user) Besties' poses and spots (687_besties). The pairs are the movie's (670: each girl's retargeted strokes,
Cloud's ZN..), carried from the studio's beds onto Gast's single bed (`BedMap`: the studio's beds run along +y
foot to head; each pair turned by the bed's angle about its own bed's middle and moved onto this one's, heights
from its bed's top to this one's). The third person is placed against the pair's joints (`Place`). New poses:
Aerith sitting up at the bed's foot (686's `_hostile_poses.under`, propped up RECLINE, retargeted QMU..),
the intro's sitting on the bed's edge (660 `_ledge`, the root moved back so the XYZI is on the floor), a few
one-frame stills (`still`)."""
import math

SEAT_IN, SEAT_OUT = 14, 18      # sitting on the bed's edge: hips this far onto it, the XYZI this far out
RECLINE = 52                    # Aerith against the headboard: her upper body propped up this far (degrees)
KISS_SIDE = 20                  # the kiss: Tifa this far to the side of Aerith's line (field units)
STAND_OFF = 60                  # the ride: Aerith standing this far from the bed's line, beside Tifa
SHARE_GAP, SHARE_ANG = 38, 22   # kneeling together: each this far before Cloud, this many degrees to either side


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("620_honey_bee"), import_module("660_dates")


def still(ctx, src, dst, frame=0):
    from ff7 import fieldanim as fa
    A = fa.Anim(ctx.char_file(src.lower() + ".a"))
    A.frames = A.frames[frame:frame + 1]
    ctx.char_file(dst.lower() + ".a", A.build())
    return dst + ".tor"


def sitting(ctx, name, hrc, stand):
    """name: sitting on an edge (660 `_ledge`), the root moved back (SEAT_IN + SEAT_OUT) so an XYZI on the floor
    in front of the edge (at the seat's height) puts her hips on it."""
    from ff7 import fieldanim as fa
    mv, _, dt = _mods()
    dt._ledge(ctx, name + ".tor", hrc.lower(), stand)
    A = fa.Anim(ctx.char_file(name.lower() + ".a"))
    back = (SEAT_IN + SEAT_OUT) / mv.UNIT
    A.frames = [(rr, [rp[0], rp[1], rp[2] + back], rots) for rr, rp, rots in A.frames]
    ctx.char_file(name.lower() + ".a", A.build())
    return name + ".tor"


def recline(ctx, hrc, stand):
    """Aerith sitting up (her knees up and apart): QMU0-3 (bobbing gently: 686's under, her head nodding), 8 / 7 / 9 as
    there; returns the names."""
    mv, _, _ = _mods()
    HP = __import__("importlib").import_module("_hostile_poses")
    return mv._retarget(ctx, HP.under(ctx, RECLINE), "QM", hrc, stand)


def joints(ctx, hrc, anim, frame=0):
    """{bone: end, bone@: start, bone#: world matrix, root} of one frame (model space, y down)."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    rr, rp, rots = fa.Anim(ctx.char_file(anim.lower() + ".a")).frames[frame]
    root = [rp[0], -rp[1], rp[2]]
    F = fa.forward(sk, rr, root, rots)
    J = {b[0]: e for b, (_, s, e) in zip(sk, F)}
    J.update({b[0] + "@": s for b, (_, s, e) in zip(sk, F)})
    J.update({b[0] + "#": m for b, (m, s, e) in zip(sk, F)})
    J["root"] = root
    return J


def face(ctx, hrc, stand, J, t=0.3, out=0.9):
    """Her face's point (between eyes and mouth) in a joints dict."""
    from ff7 import fieldanim as fa
    m0 = joints(ctx, hrc, stand.split(".")[0])["head#"]
    front = fa._vec(fa._t(m0), [0.0, 0.0, -1.0])
    S, E = J["head@"], J["head"]
    f = fa._vec(J["head#"], front)
    return [S[k] + (E[k] - S[k]) * t + f[k] * out for k in range(3)]


def field(spot, d, m):
    """Field point of model point m for an entity at spot (x, y, z) with DIR d."""
    mv = _mods()[0]
    o = mv._off(m, d)
    return [spot[k] + o[k] for k in range(3)]


class BedMap:
    """The studio's beds (whitebg1 = a copy of mds7_w3: walkable tops at 54 / 100 / 125) onto one bed (corners
    foot A B, head C D; top z)."""

    def __init__(self, ctx, corners, top):
        from ff7.field import FieldFile
        from ff7.walkmesh import Walkmesh
        import ff7tool
        mesh = Walkmesh(FieldFile(ctx._orig_raw["mds7_w3"]).section("walkmesh")) if "mds7_w3" in ctx._orig_raw else \
            Walkmesh(ctx.field("mds7_w3").section("walkmesh"))
        self.beds = []
        for t in (54, 100, 125):
            pts = [v for tr in mesh.tris if all(abs(v_[2] - t) < 3 for v_ in tr) for v in tr]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            self.beds.append((t, (min(xs), max(xs)), (min(ys), max(ys))))
        A, B, C, D = corners
        F = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        H = ((C[0] + D[0]) / 2, (C[1] + D[1]) / 2)
        self.centre = ((F[0] + H[0]) / 2, (F[1] + H[1]) / 2)
        ax = (H[0] - F[0], H[1] - F[1])
        n = math.hypot(*ax)
        self.axis = (ax[0] / n, ax[1] / n)                              # foot -> head
        self.theta = math.atan2(-self.axis[0], self.axis[1])            # +y turned by theta = the axis
        self.top = top

    def bed_of(self, p):
        best = None
        for t, (x0, x1), (y0, y1) in self.beds:
            dx = max(x0 - p[0], 0, p[0] - x1)
            dy = max(y0 - p[1], 0, p[1] - y1)
            d = math.hypot(dx, dy) + abs(p[2] - t) * 0.01
            if best is None or d < best[0]:
                best = (d, t, ((x0 + x1) / 2, (y0 + y1) / 2))
        return best[1], best[2]

    def point(self, p, bed_p=None):
        """A studio point p (x, y, z) -> here; on the bed under bed_p (default: p's own)."""
        top, c = self.bed_of(bed_p or p)
        dx, dy = p[0] - c[0], p[1] - c[1]
        ct, st = math.cos(self.theta), math.sin(self.theta)
        return (round(self.centre[0] + dx * ct - dy * st), round(self.centre[1] + dx * st + dy * ct),
                round(p[2] - top + self.top))

    def dir(self, d):
        return round(d + self.theta * 128 / math.pi) % 256

"""(user: Besties, "get the positions right so that characters don't clip through each other, the movements
organic and realistic with exaggerated hip movement") A small pose rig for building a frame from a stand pose:
the whole body turned, the pelvis rocked about the root, the upper body bent at the waist, the head at the
neck (each in the body's own frame: bow / turn / lean), bones aimed, limbs solved by two-bone IK; then the frame
(the stand's root rotation, the root, local rotations) for an .a file.

Model space as the game's: y down, a model faces -z, +x is its left. Rotations in the body's frame:
bow (+ = forward, nose down), turn (+ = to her left), lean (+ = to her left)."""
import math

from ff7 import fieldanim as fa

UP, FWD, LEFT = (0.0, -1.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0)


def unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def sub(a, b):
    return [a[k] - b[k] for k in range(3)]


def add(a, b):
    return [a[k] + b[k] for k in range(3)]


def mul(a, s):
    return [c * s for c in a]


def dot(a, b):
    return sum(a[k] * b[k] for k in range(3))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def lerp(a, b, t):
    return [a[k] + (b[k] - a[k]) * t for k in range(3)]


def align(a, b):
    """The smallest rotation turning direction a into b."""
    a, b = unit(a), unit(b)
    ax = cross(a, b)
    s = math.sqrt(dot(ax, ax))
    if s < 1e-9:
        return fa.euler_matrix(0, 0, 0) if dot(a, b) > 0 else fa.axis_angle(
            [1.0, 0.0, 0.0] if abs(a[0]) < 0.9 else [0.0, 1.0, 0.0], 180)
    return fa.axis_angle(ax, math.degrees(math.atan2(s, dot(a, b))))


def basis(left, up):
    """The rotation turning the stand's (left, up, forward) into (left, up, left x up), up made square to left."""
    left = unit(left)
    up = unit(sub(up, mul(left, dot(up, left))))
    fwd = cross(left, up)
    cols = (left, up, fwd)
    src = (LEFT, UP, FWD)
    return [[sum(cols[k][r] * src[k][c] for k in range(3)) for c in range(3)] for r in range(3)]


def bow(deg):
    return fa.axis_angle([1.0, 0.0, 0.0], deg)


def turn(deg):
    return fa.axis_angle([0.0, -1.0, 0.0], deg)


def lean(deg):
    return fa.axis_angle([0.0, 0.0, 1.0], deg)


def chain(*ms):
    out = fa.euler_matrix(0, 0, 0)
    for m in ms:
        out = fa._mul(out, m)
    return out


def ease(t):
    """0 at t = 0 (pulled back) .. 1 at t = 0.5 (deepest) .. 0 at 1, smooth."""
    return (1 - math.cos(2 * math.pi * t)) / 2


class Rig:
    _cache = {}

    def __new__(cls, ctx=None, hrc=None, stand=None):
        self = super().__new__(cls)
        if hrc is not None:
            key = (id(ctx), hrc.lower(), stand.split(".")[0].lower())
            if key not in Rig._cache:
                Rig._cache[key] = self
                self._init(ctx, hrc, stand)
            else:
                self.__dict__.update(Rig._cache[key].__dict__)
        return self

    def __init__(self, ctx=None, hrc=None, stand=None):
        pass

    def copy(self):
        r = Rig.__new__(Rig)
        r.__dict__.update(self.__dict__)
        r.W = list(self.W)
        r.root = list(self.root)
        return r

    def _init(self, ctx, hrc, stand):
        self.sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
        self.names = [b[0] for b in self.sk]
        self.I = self.names.index
        base = fa.Anim(ctx.char_file(stand.split(".")[0].lower() + ".a"))
        self.base_name = stand.split(".")[0].lower() + ".a"
        self.rr, rp, rots = base.frames[0]
        self.root0 = [rp[0], -rp[1], rp[2]]
        self.W0 = [m for m, _, _ in fa.forward(self.sk, self.rr, self.root0, rots)]
        kids = {}
        for i, b in enumerate(self.sk):
            kids.setdefault(b[1], []).append(i)

        def below(n):
            out = [self.I(n)]
            for k in kids.get(n, []):
                out += below(self.names[k])
            return out
        self.below = below
        self.upper = set()
        for n in ("chest", "l_chest", "r_chest", "non_1", "non_2"):
            if n in self.names and self.I(n) not in self.upper and self.sk[self.I(n)][1] == "hip":
                self.upper |= set(below(n))
        self.head = set(below("head"))
        self.legs = {s: set(below(s + "_hip")) for s in "lr"}
        self.length = {b[0]: b[2] for b in self.sk}

    # ---- a frame ------------------------------------------------------------------------------------------
    def start(self, body, root=None):
        """The stand turned by `body` (a matrix: e.g. basis(left, up)); root at `root` (default the stand's)."""
        self.W = [fa._mul(body, m) for m in self.W0]
        self.M = self.G = body                             # the body's frame (G: as started, before the pelvis)
        self.root = list(root or self.root0)
        return self

    def pelvis(self, R):
        """The whole body turned by R (body frame) about the root (legs are re-solved after)."""
        Rw = chain(self.M, R, fa._t(self.M))
        self.W = [fa._mul(Rw, m) for m in self.W]
        self.M = fa._mul(Rw, self.M)
        return self

    def waist(self, R):
        """The upper body (chest, shoulders and up) turned by R (body frame) about the waist."""
        Rw = chain(self.M, R, fa._t(self.M))
        self.W = [fa._mul(Rw, m) if i in self.upper else m for i, m in enumerate(self.W)]
        self.Mu = fa._mul(Rw, self.M)
        return self

    def neck(self, R):
        """The head (and hair) turned by R in the upper body's frame about the neck."""
        Mu = getattr(self, "Mu", self.M)
        Rw = chain(Mu, R, fa._t(Mu))
        self.W = [fa._mul(Rw, m) if i in self.head else m for i, m in enumerate(self.W)]
        return self

    def turn_bones(self, bones, R, frame=None):
        """Every bone in `bones` (with what hangs from them) turned by R in `frame` (default the body's)."""
        Mf = frame or self.M
        Rw = chain(Mf, R, fa._t(Mf))
        idx = set()
        for b in bones:
            idx |= set(self.below(b))
        self.W = [fa._mul(Rw, m) if i in idx else m for i, m in enumerate(self.W)]
        return self

    def aim(self, bone, d, keep=()):
        """`bone` pointed along d (model space); bones in `keep` hold their world turn (else they follow)."""
        i = self.I(bone)
        cur = fa._vec(self.W[i], [0.0, 0.0, -1.0])
        R = align(cur, d)
        held = {k: self.W[self.I(k)] for k in keep}
        for j in self.below(bone):
            self.W[j] = fa._mul(R, self.W[j])
        for k, m in held.items():
            self.W[self.I(k)] = m
        return self

    def ends(self):
        """{bone: end, bone@: start, bone#: world matrix} (positions from the world matrices directly)."""
        out = {}
        for i, (name, parent, length) in enumerate(self.sk):
            st = out[parent] if parent in out else self.root
            m = self.W[i]
            en = [st[k] - m[k][2] * length for k in range(3)]
            out[name] = en
            out[name + "@"] = st
            out[name + "#"] = m
        return out

    def _ends_slow(self):
        F = fa.forward(self.sk, self.rr, self.root, fa.local_rotations(self.sk, self.rr, self.W))
        E = {b[0]: e for b, (_, s, e) in zip(self.sk, F)}
        E.update({b[0] + "@": s for b, (_, s, e) in zip(self.sk, F)})
        E.update({b[0] + "#": m for b, (m, s, e) in zip(self.sk, F)})
        return E

    def ik(self, upper, lower, target, pole, keep_end=True, reach=0.995):
        """upper / lower re-aimed so lower's end is at target (pulled in to `reach` of the limb if too far), the
        joint towards pole (a direction); the end bone (hand / foot) follows the lower bone unless keep_end is
        False... (True keeps the end bone's world turn: a planted foot)."""
        E = self.ends()
        S = E[upper + "@"]
        L1, L2 = self.length[upper], self.length[lower]
        T = list(target)
        d = math.dist(S, T)
        if d > (L1 + L2) * reach:
            T = add(S, mul(sub(T, S), (L1 + L2) * reach / d))
            d = (L1 + L2) * reach
        if d < abs(L1 - L2) + 0.05:
            T = add(S, mul(unit(sub(T, S)), abs(L1 - L2) + 0.05))
            d = abs(L1 - L2) + 0.05
        u = unit(sub(T, S))
        pp = unit(sub(pole, mul(u, dot(pole, u))))
        a_ = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
        K = add(add(S, mul(u, a_)), mul(pp, math.sqrt(max(0.0, L1 * L1 - a_ * a_))))
        end = [k for k in self.below(lower) if k != self.I(lower)]
        held = {k: self.W[k] for k in end}
        self.aim(upper, sub(K, S))
        self.aim(lower, sub(T, K))
        if keep_end:
            for k, m in held.items():
                self.W[k] = m
        return self

    def place(self, joint, target):
        """The root moved so `joint` (an ends() key) is at target."""
        p = self.ends()[joint]
        self.root = add(self.root, sub(target, p))
        return self

    def frame(self):
        return (self.rr, [self.root[0], -self.root[1], self.root[2]], fa.local_rotations(self.sk, self.rr, self.W))


def save(ctx, name, base, frames):
    A = fa.Anim(ctx.char_file(base))
    A.frames = frames
    ctx.char_file(name.lower() + ".a", A.build())
    return name + ".tor"


# ---- helpers shared by the Besties poses ---------------------------------------------------------------
def copy_rig(rg):
    return rg.copy()


def face_pt(rg, t=0.22, out=1.0, E_=None):
    """Mouth-ish point: along the head bone from the neck, out along the face's front."""
    E_ = E_ or rg.ends()
    i = rg.I("head")
    f = fa._vec(rg.W[i], fa._vec(fa._t(rg.W0[i]), [0.0, 0.0, -1.0]))
    return add(lerp(E_["head@"], E_["head"], t), mul(f, out))


def entry(rg, E_=None, v=(0.0, 1.2, 1.0)):
    """Her entry (672 ENTRY in the pelvis bone's frame)."""
    E_ = E_ or rg.ends()
    return add(E_["hip@"], fa._vec(E_["hip#"], list(v)))


def axis_of(rg, bone, v, E_=None):
    """A stand-frame direction v of `bone`, now."""
    E_ = E_ or rg.ends()
    i = rg.I(bone)
    return fa._vec(E_[bone + "#"], fa._vec(fa._t(rg.W0[i]), list(v)))


def front(rg, bone, E_=None):
    return axis_of(rg, bone, FWD, E_)


def hips_of(rg, E_=None):
    E_ = E_ or rg.ends()
    return lerp(E_["l_femur@"], E_["r_femur@"], 0.5)


def hang_hair(rg, back=0.45, along=None):
    """Hair bones (non_1, kami) hanging down, a little behind the head; `along`: lying, spread that way."""
    for b in ("non_1", "kami"):
        if b in rg.names:
            if along is not None:
                rg.aim(b, unit(add(along, [0.0, 0.08, 0.0])))
            else:
                rg.aim(b, unit(add([0.0, 1.0, 0.0], mul(front(rg, "head"), -back))))
    return rg


def kneel(rg, tilt, spread, floor_y, shin_up=0.05, shin_out=0.05):
    """Kneeling in the body's starting frame (G): thighs `tilt` forward of straight down, `spread` out, shins back
    flat; the root moved so the knees / ankles rest at model height floor_y (y down)."""
    sp, tl = math.radians(spread), math.radians(tilt)
    G = rg.G
    for s, sx in (("l", 1), ("r", -1)):
        rg.aim(s + "_femur", fa._vec(G, [sx * math.sin(sp) * math.cos(tl), math.cos(sp) * math.cos(tl), -math.sin(tl)]))
        rg.aim(s + "_tibia", fa._vec(G, unit([sx * shin_out, shin_up, 1.0])))
        rg.aim(s + "_foot", fa._vec(G, unit([0.0, 0.25, 1.0])))
    E_ = rg.ends()
    low = max(max(E_[s + "_femur"][1], E_[s + "_tibia"][1]) for s in "lr")
    rg.root = add(rg.root, [0.0, floor_y - low, 0.0])
    return rg


def stand_feet(rg, feet, pole_fwd=1.0):
    """Legs re-solved to the ankle points `feet` {l, r}, knees forward; feet keep their turn."""
    fwd = fa._vec(rg.G, [0.0, 0.0, -1.0])
    for s, sx in (("l", 1), ("r", -1)):
        side = fa._vec(rg.G, [sx * 0.25, 0.0, 0.0])
        rg.ik(s + "_femur", s + "_tibia", feet[s], add(mul(fwd, pole_fwd), side), keep_end=True)
    return rg


def fit(build, cost, x0, steps, rounds=4, bounds=None):
    """Coordinate descent: build(x) -> rig, cost(rig) -> float; `steps` halved every round (0 = fixed)."""
    x = list(x0)
    best_r = build(x)
    best = cost(best_r)
    st = list(steps)
    for _ in range(rounds):
        moved, it = True, 0
        while moved and it < 60:
            moved, it = False, it + 1
            for i in range(len(x)):
                if not st[i]:
                    continue
                for sg in (1, -1):
                    y = list(x)
                    y[i] += sg * st[i]
                    if bounds and not (bounds[i][0] <= y[i] <= bounds[i][1]):
                        continue
                    r = build(y)
                    c = cost(r)
                    if c < best - 1e-6:
                        x, best, best_r, moved = y, c, r, True
        st = [s / 2 for s in st]
    return x, best_r

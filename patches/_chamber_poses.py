"""(user) The chamber's poses (679_chamber), built from scratch or from the movie's (girls on Ruby's skeleton,
retargeted per girl by 670 `_retarget`; Cloud bare):

  <prefix>W5  standing, hands clasped high over her head (wrists together, two-bone IK): the girls beside the
              beds' heads (built per girl on her own skeleton)
  <prefix>X5  kneeling up (thighs straight down, shins flat behind), hands clasped behind her back: the girls
              at the beds' feet
  ZMW0-3      "chained": kneeling up, hands held together over her head (IK to a fixed point: as if chained),
              pushed forward PUSH with each of his strokes; ZNK0-3 Cloud kneeling up behind her (`_kneel`:
              thighs tilted CLOUD_TILT forward, shins flat), his hips driven forward about his knees (upper body
              upright), hands on her hips; placed with his tip at her entry at the deepest frame (`CHAINED`)
  ZMX0-3      "offering": on her back, legs straight up in a V (`LEGS_V` apart), hips lifted (solved so her
              entry is level with his tip), pushed up the bed with each stroke; ZNN0-3 Cloud kneeling up at
              her hips facing her, hands on her shins (`OFFERING`)
  ZMZ0-3      "mating press": the mission girl (ZMA) with her thighs folded `FOLD` further up towards her chest
              and `FOLD_OUT` out either side (round his body); Cloud's mission ZNA
  ZNM0-3      "throne": Cloud lying still (ZNB's frame 0, one frame) - she (the cowgirl's ZMB) sits on his face
              (`THRONE`: her root `THRONE_UP` above his mouth)
Speeds 0-3 are 20 / 15 / 11 / 8 frames (the movie's), the deepest at the middle frame. Checked on offline
renders only."""
import math

UNIT = 3.41
FRAMES = (20, 15, 11, 8)
CLOUD_TILT = 18         # Cloud's kneeling thighs this far forward of upright (offering; chained: solved)
CLOUD_SPREAD = 42       # his knees this far out either side (lower hips: Ruby kneels ~2 units lower than him)
THRUST = 14             # degrees his thighs swing forward about the knees at the deepest frame
PUSH = 4                # degrees her thighs are pushed forward (chained) at his deepest
LEGS_V = 22             # (offering) each leg this far out from straight up
SLIDE = 0.35            # (offering) she slides this far (model units) up the bed at his deepest
FOLD, FOLD_OUT = 45, 32
THRONE_UP = 7           # (field units) her root above his mouth
BEHIND = 2.2            # (kneeling, hands behind) the clasped wrists this far behind her pelvis (model units)
OVERHEAD = 2.2          # the clasped wrists this far above the top of her head


def _fa():
    from ff7 import fieldanim as fa
    return fa


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("620_honey_bee"), import_module("672_movie_special")


def e_of(t, n):
    """0 at frame 0 (pulled back) .. 1 at n/2 (deepest), eased."""
    return (1 - math.cos(2 * math.pi * t / n)) / 2


def _ik_arms(fa, sk, rr, root, W, targets, pole):
    """Both arms re-aimed so each wrist (forearm's end) reaches targets[s] (pulled in to 0.97 of the arm when
    out of reach), elbows towards pole(s); the hand keeps its turn. Returns W."""
    _, _, sp = _mods()
    I = [b[0] for b in sk].index
    for s in "lr":
        F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
        S, L1, L2 = F[I(s + "_uparm")][1], math.dist(*F[I(s + "_uparm")][1:]), math.dist(*F[I(s + "_foarm")][1:])
        T = list(targets[s])
        d = math.dist(S, T)
        if d > (L1 + L2) * 0.97:
            T = [S[i] + (T[i] - S[i]) * (L1 + L2) * 0.97 / d for i in range(3)]
        if d < abs(L1 - L2) + 0.2:
            raise AssertionError(("arm too short a reach", s, d))
        hand = W[I(s + "_hand")]
        W = sp._two_bone(fa, W, I, F, s + "_uparm", s + "_foarm", T, pole(s))
        W[I(s + "_hand")] = hand
    return W


def _ends(fa, sk, rr, root, W):
    return {b[0]: e for b, (_, s_, e) in zip(sk, fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W)))} | \
        {b[0] + "@": s_ for b, (_, s_, e) in zip(sk, fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W)))}


def _kneel(ctx, hrc, stand, tilt=0.0, spread=0.0):
    """Kneeling up from the stand pose's frame 0: thighs `tilt` forward of straight down and `spread` out to
    either side, shins flat behind (feet soles up), the shins resting on the floor (model y 0). Returns
    (fa, sk, rr, root, W)."""
    _, _, sp = _mods()
    mv = _mods()[0]
    fa, sk, I, base, rr, root0, W0, fk = sp._setup(ctx, hrc.lower(), stand)
    W = list(W0)
    a, b = math.radians(tilt), math.radians(spread)
    for s, sx in (("l", 1), ("r", -1)):
        d = [sx * math.sin(b) * math.cos(a), math.cos(a) * math.cos(b), -math.sin(a)]
        W[I(s + "_femur")] = fa._mul(mv._align(fa, fa._vec(W0[I(s + "_femur")], [0, 0, -1]), d), W0[I(s + "_femur")])
        W[I(s + "_tibia")] = sp._pitch(fa, W0[I(s + "_tibia")], [0, 0, 1])
        W[I(s + "_foot")] = sp._pitch(fa, W0[I(s + "_foot")], [0, -0.15, 1])
    e = _ends(fa, sk, rr, root0, W)
    low = max(max(e[s + "_tibia"][1], e[s + "_tibia@"][1]) for s in "lr")
    root = [root0[0], root0[1] - low - 0.45, root0[2]]          # (y down) the shins 0.45 above the floor
    return fa, sk, rr, root, W


def _swing(fa, sk, rr, root, W, angle, bones_legs=True):
    """The thighs (and the pelvis' hip bones) swung `angle` about the knee line, the upper body only moved
    (not turned), shins / feet fixed: the hips go forward (angle > 0) and down. Returns (root, W)."""
    I = [b[0] for b in sk].index
    e = _ends(fa, sk, rr, root, W)
    K = [(e["l_femur"][k] + e["r_femur"][k]) / 2 for k in range(3)]
    best = None
    for sg in (1, -1):
        R = fa.axis_angle([1.0, 0.0, 0.0], sg * angle)
        M = list(W)
        for n in ("l_hip", "r_hip", "l_femur", "r_femur"):
            M[I(n)] = fa._mul(R, W[I(n)])
        rel = fa._vec(R, [root[k] - K[k] for k in range(3)])
        r2 = [K[k] + rel[k] for k in range(3)]
        e2 = _ends(fa, sk, rr, r2, M)
        knee_err = max(math.dist(e2[s + "_femur"], e[s + "_femur"]) for s in "lr")
        fwd = -(e2["hip@"][2] - e["hip@"][2])                       # (model -z = forward)
        if best is None or (fwd > best[0]):
            best = (fwd, r2, M, knee_err)
    assert best[3] < 0.05, ("knees moved", best[3])
    return best[1], best[2]


def _save(ctx, name, base, frames):
    fa = _fa()
    A = fa.Anim(ctx.char_file(base))
    A.frames = frames
    ctx.char_file(name.lower() + ".a", A.build())


def _frame(fa, sk, rr, root, W):
    return (rr, [root[0], -root[1], root[2]], fa.local_rotations(sk, rr, W))


# ---- the waiting poses ------------------------------------------------------------------------------
def stand_bound(ctx, name, hrc, stand):
    """<name>: standing (her stand's frame 0), wrists together OVERHEAD above her head (one frame)."""
    _, _, sp = _mods()
    fa, sk, I, base, rr, root, W, fk = sp._setup(ctx, hrc.lower(), stand)
    e = _ends(fa, sk, rr, root, W)
    top = e["head"]
    P = [top[0], top[1] - OVERHEAD, top[2] - 0.3]
    W = _ik_arms(fa, sk, rr, root, W, {"l": [P[0] + 0.15, P[1], P[2]], "r": [P[0] - 0.15, P[1], P[2]]},
                 lambda s: [3.0 if s == "l" else -3.0, 0.0, 0.5])
    _save(ctx, name, stand, [_frame(fa, sk, rr, root, W)])


def kneel_behind(ctx, name, hrc, stand):
    """<name>: kneeling up, wrists together BEHIND her pelvis (one frame)."""
    fa, sk, rr, root, W = _kneel(ctx, hrc, stand)
    e = _ends(fa, sk, rr, root, W)
    h = e["hip@"]
    P = [h[0], h[1] - 0.5, h[2] + BEHIND]
    W = _ik_arms(fa, sk, rr, root, W, {"l": [P[0] + 0.2, P[1], P[2]], "r": [P[0] - 0.2, P[1], P[2]]},
                 lambda s: [3.0 if s == "l" else -3.0, 0.5, 0.5])
    _save(ctx, name, stand, [_frame(fa, sk, rr, root, W)])


# ---- placements ----------------------------------------------------------------------------------------
def to_field(m, at, d):
    a = d * 2 * math.pi / 256
    Fw = (math.sin(a), -math.cos(a))
    L = (-Fw[1], Fw[0])
    return (at[0] + UNIT * (m[0] * L[0] - m[2] * Fw[0]), at[1] + UNIT * (m[0] * L[1] - m[2] * Fw[1]),
            at[2] - UNIT * m[1])


def _tip(ctx, root, W, sk, rr):
    """Cloud's member tip (620 zcmp.p on the hip bone) in model space."""
    fa = _fa()
    _, hb, _ = _mods()
    F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
    hi = [b[0] for b in sk].index("hip")
    m, s_, _ = F[hi]
    v = fa._vec(m, hb.member_ends(ctx.char_file("zcmp.p"))[1])
    return [s_[k] + v[k] for k in range(3)]


def _entry(fa, sk, rr, root, W):
    F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
    hi = [b[0] for b in sk].index("hip")
    m, s_, _ = F[hi]
    v = fa._vec(m, [0.0, 1.2, 1.0])                                 # (672 ENTRY)
    return [s_[k] + v[k] for k in range(3)]


PLACE = {}   # name -> (dx, dy, dz, rel DIR): Cloud's XYZI from hers (her DIR 0), filled by the builders


def chained(ctx):
    """ZMW0-3 / ZNK0-3."""
    _, hb, sp = _mods()
    fa = _fa()
    gk = _kneel(ctx, sp.RUBY_HRC, sp.RUBY_STAND)
    ge = _ends(fa, *gk[1:3], gk[3], gk[4])
    P = [ge["head"][0], ge["head"][1] - OVERHEAD, ge["head"][2] - 0.8]
    hands = {"l": [P[0] + 0.15, P[1], P[2]], "r": [P[0] - 0.15, P[1], P[2]]}
    # Cloud's thigh tilt: his tip (deepest) level with her entry (deepest)
    def cloud_at(tilt, t, n):
        fa_, sk, rr, root, W = _kneel(ctx, hb.CLOUD_BARE_HRC, "acfe.a", tilt, CLOUD_SPREAD)
        root, W = _swing(fa, sk, rr, root, W, THRUST * e_of(t, n))
        return sk, rr, root, W
    def her_at(t, n):
        fa_, sk, rr, root, W = gk
        root, W = _swing(fa, sk, rr, root, W, PUSH * e_of(t, n))
        W = _ik_arms(fa, sk, rr, root, W, hands, lambda s: [3.0 if s == "l" else -3.0, 0.0, 0.5])
        return sk, rr, root, W
    sk_g, rr_g, rg, Wg = her_at(7, 15)
    target = _entry(fa, sk_g, rr_g, rg, Wg)
    lo, hi = -10.0, 60.0
    for _ in range(30):                                              # higher tilt = lower hips
        mid = (lo + hi) / 2
        sk_c, rr_c, rc, Wc = cloud_at(mid, 7, 15)
        if _tip(ctx, rc, Wc, sk_c, rr_c)[1] < target[1]:            # (y down) his tip above hers: lower
            lo = mid
        else:
            hi = mid
    tilt = (lo + hi) / 2
    assert -8 < tilt < 58, tilt
    sk_c, rr_c, rc, Wc = cloud_at(tilt, 7, 15)
    tip = _tip(ctx, rc, Wc, sk_c, rr_c)
    # same DIR: Cloud's origin = her entry - his tip (model axes shared)
    off = [target[k] - tip[k] for k in range(3)]
    f = to_field(off, (0, 0, 0), 0)
    PLACE["chained"] = (f[0], f[1], f[2], 0)
    for k, n in enumerate(FRAMES):
        gf, cf = [], []
        for t in range(n):
            sk, rr, root, W = her_at(t, n)
            gf.append(_frame(fa, sk, rr, root, W))
            sk2, rr2, r2, W2 = cloud_at(tilt, t, n)
            # his hands on her hips (her hip joints, in his model space: + off)
            he = _ends(fa, sk, rr, root, W)
            tg = {s: [he[s + "_femur@"][i] - off[i] + (0.6 if s == "l" else -0.6) * (i == 0) for i in range(3)] for s in "lr"}
            W2 = _ik_arms(fa, sk2, rr2, r2, W2, tg, lambda s: [2.5 if s == "l" else -2.5, 0.5, 1.0])
            cf.append(_frame(fa, sk2, rr2, r2, W2))
        _save(ctx, "ZMW%d" % k, sp.RUBY_STAND, gf)
        _save(ctx, "ZNK%d" % k, "acfe.a", cf)
    return tilt


def offering(ctx):
    """ZMX0-3 / ZNN0-3 (not K / L: ZMK0 / ZML0 are the movie's still poses)."""
    mv, hb, sp = _mods()
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(sp.RUBY_HRC).decode("latin-1"))
    I = [b[0] for b in sk].index
    rr, rp, rots = fa.Anim(ctx.char_file("zmk0.a")).frames[0]
    root0 = [rp[0], -rp[1], rp[2]]
    W0 = [m for m, _, _ in fa.forward(sk, rr, root0, rots)]
    W = list(W0)
    up = [0.0, -1.0, 0.0]
    for s, sx in (("l", 1), ("r", -1)):
        a = math.radians(LEGS_V)
        d = [sx * math.sin(a), -math.cos(a), 0.0]
        for b in ("_femur", "_tibia"):
            W[I(s + b)] = fa._mul(mv._align(fa, fa._vec(W0[I(s + b)], [0, 0, -1]), d), W0[I(s + b)])
        W[I(s + "_foot")] = fa._mul(mv._align(fa, fa._vec(W0[I(s + "_foot")], [0, 0, -1]), [d[0], d[1], 0.4]),
                                    W0[I(s + "_foot")])
    # Cloud kneeling up (his own tilt) facing her: her entry level with his tip at the deepest frame
    def cloud_at(t, n):
        fa_, skc, rrc, rootc, Wc = _kneel(ctx, hb.CLOUD_BARE_HRC, "acfe.a", CLOUD_TILT)
        rootc, Wc = _swing(fa, skc, rrc, rootc, Wc, THRUST * e_of(t, n))
        return skc, rrc, rootc, Wc
    skc, rrc, rc, Wc = cloud_at(7, 15)
    tip = _tip(ctx, rc, Wc, skc, rrc)
    ent = _entry(fa, sk, rr, root0, W)
    lift = ent[1] - tip[1]                      # (y down) raise her by this (model units; >0: her entry lower)
    assert -1.0 < lift < 4.0, ("her hips would float / sink", lift)
    def her_at(t, n):
        r = [root0[0], root0[1] - lift, root0[2] + SLIDE * e_of(t, n)]   # (model +z: towards her head, DIR 0)
        return r, W
    # placement: she DIR 0 (head to +y), Cloud DIR 128 facing her; his tip on her entry at the deepest
    r7, _ = her_at(7, 15)
    ent7 = to_field(_entry(fa, sk, rr, r7, W), (0, 0, 0), 0)
    tipf = to_field(tip, (0, 0, 0), 128)
    PLACE["offering"] = (ent7[0] - tipf[0], ent7[1] - tipf[1], ent7[2] - tipf[2], 128)
    off = PLACE["offering"]
    for k, n in enumerate(FRAMES):
        gf, cf = [], []
        for t in range(n):
            r, Wg = her_at(t, n)
            gf.append(_frame(fa, sk, rr, r, Wg))
            skc, rrc, rc, Wc = cloud_at(t, n)
            he = _ends(fa, sk, rr, r, Wg)
            tg = {}
            for mine, hers in (("l", "r"), ("r", "l")):             # (facing her: his left on her right)
                p = [(he[hers + "_tibia@"][i] + he[hers + "_tibia"][i]) / 2 for i in range(3)]
                pf = to_field(p, (0, 0, 0), 0)
                tg[mine] = _to_model(pf, off[:3], 128)
            Wc = _ik_arms(fa, skc, rrc, rc, Wc, tg, lambda s: [2.5 if s == "l" else -2.5, 1.0, 0.5])
            cf.append(_frame(fa, skc, rrc, rc, Wc))
        _save(ctx, "ZMX%d" % k, "zmk0.a", gf)
        _save(ctx, "ZNN%d" % k, "acfe.a", cf)


def _to_model(p, at, d):
    a = d * 2 * math.pi / 256
    Fw = (math.sin(a), -math.cos(a))
    L = (-Fw[1], Fw[0])
    dx, dy = p[0] - at[0], p[1] - at[1]
    return [(dx * L[0] + dy * L[1]) / UNIT, -(p[2] - at[2]) / UNIT, -(dx * Fw[0] + dy * Fw[1]) / UNIT]


def mating_press(ctx):
    """ZMZ0-3 from ZMA0-3 (Cloud: ZNA, the mission's placement)."""
    _, _, sp = _mods()
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(sp.RUBY_HRC).decode("latin-1"))
    names = [b[0] for b in sk]
    for k in range(4):
        A = fa.Anim(ctx.char_file("zma%d.a" % k))
        frames = []
        for rr, rp, rots in A.frames:
            root = [rp[0], -rp[1], rp[2]]
            W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
            e0 = _ends(fa, sk, rr, root, W)
            for s, sx in (("l", 1), ("r", -1)):
                leg = [names.index(s + b) for b in ("_femur", "_tibia", "_foot")]
                best = None
                for sg in (1, -1):                                   # folded towards her head (+z)
                    R = fa.axis_angle([1.0, 0.0, 0.0], sg * FOLD)
                    M = [fa._mul(R, m) if i in leg else m for i, m in enumerate(W)]
                    z = _ends(fa, sk, rr, root, M)[s + "_femur"][2]
                    if best is None or z > best[0]:
                        best = (z, M)
                W = best[1]
                best = None
                for sg in (1, -1):                                   # and out to her side
                    R = fa.axis_angle([0.0, 0.0, 1.0], sg * FOLD_OUT)
                    M = [fa._mul(R, m) if i in leg else m for i, m in enumerate(W)]
                    x = _ends(fa, sk, rr, root, M)[s + "_femur"][0] * sx
                    if best is None or x > best[0]:
                        best = (x, M)
                W = best[1]
            assert all(_ends(fa, sk, rr, root, W)[s + "_femur"][2] > e0[s + "_femur"][2] for s in "lr")
            frames.append(_frame(fa, sk, rr, root, W))
        _save(ctx, "ZMZ%d" % k, "zma%d.a" % k, frames)


def throne(ctx):
    """ZNM0-3: ZNB's frame 0 held (one frame); PLACE["throne"]: Cloud's XYZI from hers (she DIR = his)."""
    mv, hb, sp = _mods()
    fa = _fa()
    A = fa.Anim(ctx.char_file("znb1.a"))
    for k in range(4):
        B = fa.Anim(ctx.char_file("znb1.a"))
        B.frames = B.frames[:1]
        ctx.char_file("znm%d.a" % k, B.build())
    skc = fa.skeleton(ctx.char_file(hb.CLOUD_BARE_HRC.lower()).decode("latin-1"))
    rr, rp, rots = A.frames[0]
    F = fa.forward(skc, rr, [rp[0], -rp[1], rp[2]], rots)
    hi = [b[0] for b in skc].index("head")
    mouth = [(F[hi][1][k] + F[hi][2][k]) / 2 for k in range(3)]
    skg = fa.skeleton(ctx.char_file(sp.RUBY_HRC).decode("latin-1"))
    rr, rp, rots = fa.Anim(ctx.char_file("zmb1.a")).frames[0]
    her_root = [rp[0], -rp[1], rp[2]]
    # (same DIR) her root over his mouth, THRONE_UP above it
    m = to_field(mouth, (0, 0, 0), 0)
    h = to_field(her_root, (0, 0, 0), 0)
    PLACE["throne"] = (h[0] - m[0], h[1] - m[1], h[2] - m[2] - THRONE_UP, 0)


def build(ctx):
    chained(ctx)
    offering(ctx)
    mating_press(ctx)
    throne(ctx)
    return dict(PLACE)

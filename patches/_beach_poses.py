"""(user) The beach party's own poses (679), built from the movie's on Ruby's skeleton (girls, retargeted per
girl by 670 `_retarget`) and bare Cloud's:

  ZMZ5 / <prefix>Z5  lounging on a lounger (660 `_lounge` with the upper body LOUNGE_BACK back): the waiting
                     and watching pose on the loungers, built per girl on her own skeleton
  ZNV0-3   as ZNW, she facing him (DIR + 128): the reverse sunbed
  ZNW0-3   "sunbed": Cloud lounging (CLOUD_BACK), hips rising and falling with the cowgirl's beat (ZNB's root
           motion), hands on her hips (two-bone IK) - she rides him in ZMB (the movie's cowgirl)
  (not built: from the beach's camera Cloud's back hid her)
  ZMX0-3   "lounger mission": the mission girl (ZMA) with her upper body turned RECLINE up about her pelvis,
           lying back against the lounger's backrest
  ZNX0-3   Cloud kneeling up for it: the mission Cloud (ZNA) with his upper body turned KNEEL_UP back, hands
           on her knees (two-bone IK)
  ZMY0-3   "waves": the edge girl (ZMD, bent forward standing) with her hands on her knees (two-bone IK)
           instead of on a bed - in the shallows with the edge Cloud (ZND) behind her
Checked on offline renders only."""
import math

LOUNGE_BACK = 42        # degrees the upper body leans back from upright (the loungers' backrests: ~50 from level)
CLOUD_BACK = 42
RECLINE = 48            # degrees her upper body turns up from lying flat (the backrest)
KNEEL_UP = 58           # degrees Cloud's upper body turns back from the mission lean (about upright)
HOLD_UP = 0.6           # Cloud's hands this far up her thigh from the knee (0 knee .. 1 hip)
KNEE_HANDS = 0.25       # (waves) her hands this far up her thigh from the knee


def _fa():
    from ff7 import fieldanim as fa
    return fa


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("620_honey_bee"), import_module("660_dates"), \
        import_module("672_movie_special")


def lounge(ctx, name, hrc, stand):
    """Lounging (`name`, no extension): 660's lounger pose with the upper body LOUNGE_BACK back."""
    _, _, dt, _ = _mods()
    old = dt.LOUNGE_BACK
    dt.LOUNGE_BACK = LOUNGE_BACK
    try:
        dt._lounge(ctx, name + ".a", hrc.lower(), stand)
    finally:
        dt.LOUNGE_BACK = old


def _below(sk, top):
    """The bone `top` and every bone hanging from it."""
    out, grow = {top}, True
    while grow:
        grow = False
        for b in sk:
            if b[1] in out and b[0] not in out:
                out.add(b[0])
                grow = True
    return out


def _turned_frames(ctx, hrc, src, bones, angle, test):
    """src's frames with `bones` (world) turned about the model's side axis at the root by +-angle, the sense
    picked on frame 0 by test(ends before, ends after) (ends = {bone: end point}). Returns (sk, frames, sense)."""
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    names = [b[0] for b in sk]
    A = fa.Anim(ctx.char_file(src))
    out, sense = [], None
    for rr, rp, rots in A.frames:
        root = [rp[0], -rp[1], rp[2]]
        W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
        ends = lambda W: {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W)))}
        e0 = ends(W)
        for sg in ((1, -1) if sense is None else (sense,)):
            R = fa.axis_angle([1.0, 0.0, 0.0], sg * angle)
            M = [fa._mul(R, m) if names[i] in bones else m for i, m in enumerate(W)]
            if sense is not None or test(e0, ends(M)):
                sense = sg
                break
        else:
            raise AssertionError(("no sense turns", src))
        out.append((rr, rp, M))
    return sk, out, sense


def _save(ctx, name, sk, frames, base):
    fa = _fa()
    A = fa.Anim(ctx.char_file(base))
    A.frames = [(rr, rp, fa.local_rotations(sk, rr, W)) for rr, rp, W in frames]
    ctx.char_file(name.lower() + ".a", A.build())


REACH = 0.96            # an IK target at most this much of the arm's length from the shoulder


def _arms_to(ctx, sk, frames, targets, pole_out):
    """Each frame's arms re-aimed (two-bone IK, elbows `pole_out` sideways and back) so the forearm's end
    reaches targets(frame index, ends) = {"l": point, "r": point}; the hand keeps its angle."""
    fa = _fa()
    _, _, _, sp = _mods()
    names = [b[0] for b in sk]
    I = names.index
    blen = lambda F, n: math.dist(F[I(n)][1], F[I(n)][2])
    out = []
    for t, (rr, rp, W) in enumerate(frames):
        root = [rp[0], -rp[1], rp[2]]
        F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
        ends = {names[i]: e for i, (_, _, e) in enumerate(F)}
        tg = targets(t, ends)
        W = list(W)
        for s, out_x in (("l", 1), ("r", -1)):
            hand = W[I(s + "_hand")]
            S, L1, L2 = F[I(s + "_uparm")][1], blen(F, s + "_uparm"), blen(F, s + "_foarm")
            d = math.dist(S, tg[s])
            if d > (L1 + L2) * REACH:                  # (out of reach: the wrist as near as the arm goes, the
                k = (L1 + L2) * REACH / d              # hand on along the same line)
                tg[s] = [S[i] + (tg[s][i] - S[i]) * k for i in range(3)]
            W = sp._two_bone(fa, W, I, F, s + "_uparm", s + "_foarm", tg[s], [out_x * pole_out, -0.3, 1.0])
            W[I(s + "_hand")] = hand
            F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
        e = {names[i]: x for i, (_, _, x) in enumerate(F)}
        for s in "lr":
            assert math.dist(e[s + "_foarm"], tg[s]) < 0.3, (t, s, e[s + "_foarm"], tg[s])
        out.append((rr, rp, W))
    return out


def girl_recline(ctx):
    """ZMX0-3 (Ruby's skeleton) from ZMA0-3."""
    mv, _, _, _ = _mods()
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(mv.RUBY_HRC.lower()).decode("latin-1"))
    upper = _below(sk, "hip")
    for k in range(4):
        sk_, frames, _ = _turned_frames(ctx, mv.RUBY_HRC, "zma%d.a" % k, upper, RECLINE,
                                        lambda e0, e1: e1["head"][1] < e0["head"][1] - 1)       # (y down) head up
        _save(ctx, "ZMX%d" % k, sk_, frames, "zma%d.a" % k)


UNIT = 3.41
X_CLOUD = (0, 34, -4, 128)      # lounger mission: Cloud's XYZI / DIR from hers (DIR 0): the mission's (670)
W_RIDE = 10                     # sunbed: her root this far above his (the cowgirl's on a bed)
HEAD_FWD = 35                   # (lounger mission) his head turned back down this much to look at her


def to_field(m, at, d):
    a = d * 2 * math.pi / 256
    Fw = (math.sin(a), -math.cos(a))
    L = (-Fw[1], Fw[0])
    return (at[0] + UNIT * (m[0] * L[0] - m[2] * Fw[0]), at[1] + UNIT * (m[0] * L[1] - m[2] * Fw[1]),
            at[2] - UNIT * m[1])


def to_model(p, at, d):
    a = d * 2 * math.pi / 256
    Fw = (math.sin(a), -math.cos(a))
    L = (-Fw[1], Fw[0])
    dx, dy = p[0] - at[0], p[1] - at[1]
    return [(dx * L[0] + dy * L[1]) / UNIT, -(p[2] - at[2]) / UNIT, -(dx * Fw[0] + dy * Fw[1]) / UNIT]


def ends(ctx, hrc, anim, t):
    """{bone: end} (and bone + '@' = its start, 'root') in model space, frame t."""
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    A = fa.Anim(ctx.char_file(anim))
    rr, rp, rots = A.frames[t % len(A.frames)]
    root = [rp[0], -rp[1], rp[2]]
    F = fa.forward(sk, rr, root, rots)
    out = {b[0]: e for b, (_, s_, e) in zip(sk, F)}
    out.update({b[0] + "@": s_ for b, (_, s_, e) in zip(sk, F)})
    out["root"] = root
    return out


def sunbed_offset(ctx, her_dir=0):
    """Her XYZI offset (dx, dy, dz) from his in the sunbed (his DIR 0, hers her_dir): her root W_RIDE above his."""
    mv, hb, _, _ = _mods()
    his = to_field(ends(ctx, hb.CLOUD_BARE_HRC, "zcz5.a", 0)["root"], (0, 0, 0), 0)
    her = to_field(ends(ctx, mv.RUBY_HRC, "zmb1.a", 0)["root"], (0, 0, 0), her_dir)
    return (his[0] - her[0], his[1] - her[1], his[2] - her[2] + W_RIDE)


def lounge_at(ctx, name, hrc, stand, off):
    """`lounge` with the root moved by -off (field units, DIR 0): played at a rider's spot (his + off) she
    lounges where he would lie, so one spot serves a girl waiting on a lounger and riding on it."""
    fa = _fa()
    lounge(ctx, name, hrc, stand)
    A = fa.Anim(ctx.char_file(name.lower() + ".a"))
    A.frames = [(rr, [rp[0] - off[0] / UNIT, rp[1] - off[2] / UNIT, rp[2] + off[1] / UNIT], rots)
                for rr, rp, rots in A.frames]
    ctx.char_file(name.lower() + ".a", A.build())


def cloud_kneel_up(ctx):
    """ZNX0-3 from ZNA0-3: upper body turned KNEEL_UP back, head HEAD_FWD down again; hands on her thighs
    (ZMX's, HOLD_UP from the knee; his left on her right), X_CLOUD from her."""
    mv, hb, _, _ = _mods()
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(hb.CLOUD_BARE_HRC.lower()).decode("latin-1"))
    names = [b[0] for b in sk]
    upper = _below(sk, "hip")
    head = _below(sk, "head")
    at, d = X_CLOUD[:3], X_CLOUD[3]

    def thighs(k, t):
        e = ends(ctx, mv.RUBY_HRC, "zmx%d.a" % k, t)
        out = {}
        for mine, hers in (("l", "r"), ("r", "l")):
            knee, hip = e[hers + "_femur"], e[hers + "_femur@"]
            p = [knee[i] + (hip[i] - knee[i]) * HOLD_UP for i in range(3)]
            out[mine] = to_model(to_field(p, (0, 0, 0), 0), at, d)
        return out
    for k in range(4):
        sk_, frames, _ = _turned_frames(ctx, hb.CLOUD_BARE_HRC, "zna%d.a" % k, upper, KNEEL_UP,
                                        lambda e0, e1: e1["head"][1] < e0["head"][1] - 1)
        looked = []
        for rr, rp, W in frames:                  # the head back down towards her
            root = [rp[0], -rp[1], rp[2]]
            side = fa._vec(W[names.index("head")], [1.0, 0.0, 0.0])
            best = None
            for sg in (1, -1):
                R = fa.axis_angle(side, sg * HEAD_FWD)
                M = [fa._mul(R, m) if names[i] in head else m for i, m in enumerate(W)]
                e = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, M))
                z = e[names.index("head")][2][2]            # (model -z = forward: towards her)
                if best is None or z < best[0]:
                    best = (z, M)
            looked.append((rr, rp, best[1]))
        frames = _arms_to(ctx, sk_, looked, lambda t, e: thighs(k, t), 0.8)
        _save(ctx, "ZNX%d" % k, sk_, frames, "zna%d.a" % k)


def cloud_sunbed(ctx, name="ZNW", her_dir=0):
    """ZNW0-3 (`name`): Cloud lounging (CLOUD_BACK), his root moving as ZNB<k>'s (the cowgirl's beat, same
    frame counts); hands on her hips (ZMB's hip joints; she at `sunbed_offset` from him, DIR her_dir: 0 facing
    his feet, ZNW; 128 facing him, ZNV)."""
    mv, hb, dt, _ = _mods()
    fa = _fa()
    old = dt.LOUNGE_BACK
    dt.LOUNGE_BACK = CLOUD_BACK
    try:
        dt._lounge(ctx, "zcz5.a", hb.CLOUD_BARE_HRC.lower(), "acfe.a")
    finally:
        dt.LOUNGE_BACK = old
    off = sunbed_offset(ctx, her_dir)
    sk = fa.skeleton(ctx.char_file(hb.CLOUD_BARE_HRC.lower()).decode("latin-1"))
    rr0, rp0, rots0 = fa.Anim(ctx.char_file("zcz5.a")).frames[0]

    def hips(k, t):
        e = ends(ctx, mv.RUBY_HRC, "zmb%d.a" % k, t)
        side = {"l": "l", "r": "r"} if her_dir == 0 else {"l": "r", "r": "l"}
        return {s: to_model(to_field(e[side[s] + "_femur@"], off, her_dir), (0, 0, 0), 0) for s in "lr"}
    for k in range(4):
        B = fa.Anim(ctx.char_file("znb%d.a" % k))
        assert len(B.frames) == len(fa.Anim(ctx.char_file("zmb%d.a" % k)).frames), k
        y0 = B.frames[0][1][1]
        frames = []
        for rr, rp, rots in B.frames:
            p = [rp0[0], rp0[1] + (rp[1] - y0), rp0[2]]
            root = [p[0], -p[1], p[2]]
            frames.append((rr0, p, [m for m, _, _ in fa.forward(sk, rr0, root, rots0)]))
        frames = _arms_to(ctx, sk, frames, lambda t, e: hips(k, t), 0.6)
        _save(ctx, "%s%d" % (name, k), sk, frames, "znb%d.a" % k)


def build(ctx):
    """Every beach pose on Ruby's skeleton / bare Cloud's (the girls' retargeted by 679)."""
    cloud_sunbed(ctx)
    cloud_sunbed(ctx, "ZNV", 128)
    girl_knees(ctx)


def girl_knees(ctx):
    """ZMY0-3 from ZMD0-3: hands on her knees (KNEE_HANDS up the thigh, a little out to the side)."""
    mv, _, _, _ = _mods()
    fa = _fa()
    sk = fa.skeleton(ctx.char_file(mv.RUBY_HRC.lower()).decode("latin-1"))
    names = [b[0] for b in sk]
    for k in range(4):
        A = fa.Anim(ctx.char_file("zmd%d.a" % k))
        frames = []
        for rr, rp, rots in A.frames:
            root = [rp[0], -rp[1], rp[2]]
            frames.append((rr, rp, [m for m, _, _ in fa.forward(sk, rr, root, rots)]))

        def knees(t, e):
            out = {}
            for s, sx in (("l", 1), ("r", -1)):
                knee, hip = e[s + "_femur"], e[s + "_hip"]
                p = [knee[i] + (hip[i] - knee[i]) * KNEE_HANDS for i in range(3)]
                p[0] += sx * 0.9 * (1 if knee[0] > hip[0] or s == "l" else -1) * 0
                out[s] = p
            return out
        frames = _arms_to(ctx, sk, frames, knees, 1.0)
        _save(ctx, "ZMY%d" % k, sk, frames, "zmd%d.a" % k)

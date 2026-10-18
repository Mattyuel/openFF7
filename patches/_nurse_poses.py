"""(user) Hello nurse's own positions (679_nurse), all new (user: "make her positions unique"): built on Ruby's
skeleton (ZO<letter><speed>, retargeted onto the nurse as ZJ.. by 670 `_retarget`: the nurse's BTEC skeleton
has Ruby's bone lengths) and bare Cloud's (ZN..). Speeds 0-3 = 20 / 15 / 11 / 8 frames, deepest at the
middle frame. Cloud is the patient, on his back on the bed throughout.

  checkup   (user's idea) ZOA / ZNY: Cloud on his back, legs apart (`SPREAD`; ZNB's hip lift); she kneels
            between his legs facing his head, bent down (pitch solved so her mouth is at his tip's height)
            with her backside high, her head bobbing `BOB`, hands flat on the bed beside his hips
  arched    ZOB / ZNB: she rides him facing him, leant `ARCH` back, hands on his thighs (IK) (a standing
            bedside pose can't reach: the clinic's beds put his hips at her face's height)
  spoon     ZOC / ZNZ: the edge pair (ZMD / ZND, him behind her) turned onto their sides (`_on_side`) and
            laid on the bed: she curled forward, him behind her
  stacked   ZOD / ZNB: she lies on her back on top of him (her root `STACK_UP` above his), knees up, feet
            planted on the bed either side of his legs (two-bone IK), rising and falling with his hips
  saddle    ZOE / ZNB: the cowgirl rider (ZMB, facing his feet) leaning `SADDLE_LEAN` further forward, her
            hands on his shins (IK)
`build(ctx)` returns PLACE {position: (dx, dy, dz, rel, floor)}: her XYZI from Cloud's (his DIR 0), her DIR =
his + rel, floor = she stands on the floor (dz then from the floor). Checked on offline renders only."""
import math

import _chamber_poses as CP

UNIT = 3.41
FRAMES = (20, 15, 11, 8)
SPREAD = 22             # Cloud's legs this far out each (degrees, about the bed's normal at his hips)
BOB = 9                 # degrees her upper body dips at the deepest frame (checkup / bedside)
STACK_UP = 2.6          # (model units) her root above his
STACK_WIDE = 1.6        # her feet this far further out than his knees
SADDLE_LEAN = 25
BED_TOP = 59            # (field units) the clinic's beds (ithos walkmesh)
PLACE = {}


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("620_honey_bee"), import_module("672_movie_special")


def _frames(ctx, hrc, anim):
    """[(rr, root (model, y down), world matrices)] of an anim."""
    fa = CP._fa()
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    out = []
    for rr, rp, rots in fa.Anim(ctx.char_file(anim)).frames:
        root = [rp[0], -rp[1], rp[2]]
        out.append((rr, root, [m for m, _, _ in fa.forward(sk, rr, root, rots)]))
    return sk, out


def _turn(fa, sk, W, bones, axis, angle, test):
    """W with `bones` turned about `axis` by +-angle (the sense test(new W) accepts)."""
    names = [b[0] for b in sk]
    for sg in (1, -1):
        R = fa.axis_angle(axis, sg * angle)
        M = [fa._mul(R, m) if names[i] in bones else m for i, m in enumerate(W)]
        if test(M):
            return M
    raise AssertionError(("no sense", sorted(bones)))


def _mouth(e):
    return [(e["head"][k] + e["head@"][k]) / 2 for k in range(3)]


def _save(ctx, name, base, frames):
    CP._save(ctx, name, base, frames)


# ---- Cloud ------------------------------------------------------------------------------------------
def patient(ctx):
    """ZNY0-3: ZNB with his legs SPREAD apart (each leg turned about the bed's normal at its hip)."""
    _, hb, _ = _mods()
    fa = CP._fa()
    for k in range(4):
        sk, fr = _frames(ctx, hb.CLOUD_BARE_HRC, "znb%d.a" % k)
        out = []
        for rr, root, W in fr:
            for s, sx in (("l", 1), ("r", -1)):
                leg = {s + "_femur", s + "_tibia", s + "_foot"}
                e0 = CP._ends(fa, sk, rr, root, W)
                W = _turn(fa, sk, W, leg, [0.0, 1.0, 0.0], SPREAD,
                          lambda M: sx * (CP._ends(fa, sk, rr, root, M)[s + "_femur"][0] - e0[s + "_femur"][0]) > 0.3)
            out.append(CP._frame(fa, sk, rr, root, W))
        _save(ctx, "ZNY%d" % k, "znb%d.a" % k, out)
        if k == 0:
            _save(ctx, "ZNY9", "znb0.a", [_lying(ctx, fa, sk, fr[0])])


def _lying(ctx, fa, sk, znb):
    """ZNY9 (one frame): the patient lying still between visits: his stand pose (ACFE frame 0) laid flat on
    his back along ZNB's body line (pelvis -> head), face up, pelvis where ZNB's is."""
    _, hb, _ = _mods()
    rr, root, Wb = znb
    _, st = _frames(ctx, hb.CLOUD_BARE_HRC, "acfe.a")
    rs, root_s, Ws = st[0]
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    unit = lambda a: [c / math.sqrt(sum(x * x for x in a)) for c in a]
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    cross = lambda u, w: [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]

    def basis(h, f):
        h = unit(h)
        f = unit(sub(f, [c * dot(f, h) for c in h]))
        return [h, f, cross(h, f)]
    eb, es = CP._ends(fa, sk, rr, root, Wb), CP._ends(fa, sk, rs, root_s, Ws)
    T = basis(sub(eb["head"], eb["hip@"]), [0.0, -1.0, 0.0])          # (y down: face up)
    S = basis(sub(es["head"], es["hip@"]), [0.0, 0.0, -1.0])          # (model -z = his front)
    R = [[sum(T[k][r] * S[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
    W = [fa._mul(R, m) for m in Ws]
    e = CP._ends(fa, sk, rr, root, W)
    low = max(v[1] for v in e.values())                                 # (y down) his lowest point
    blow = max(v[1] for n, v in eb.items() if n in ("hip@", "chest", "chest@", "head"))
    return CP._frame(fa, sk, rr, [root[0], root[1] - (low - blow), root[2]], W)


# ---- checkup / bedside: bent down, mouth at his tip ------------------------------------------------------
def _bent(ctx, base, target_y, hands, t, n, sk, rr, root, W):
    """Her upper body pitched forward until her mouth's height (model y) is target_y, plus BOB at the
    deepest; hands (model points) by IK. Returns (root, W)."""
    fa = CP._fa()
    upper = CP._below(sk, "hip") if hasattr(CP, "_below") else None
    names = [b[0] for b in sk]
    if upper is None:
        upper, grow = {"hip"}, True
        while grow:
            grow = False
            for b in sk:
                if b[1] in upper and b[0] not in upper:
                    upper.add(b[0])
                    grow = True
    x = [1.0, 0.0, 0.0]
    e0 = CP._ends(fa, sk, rr, root, W)
    # the sense that brings the head forward (-z) and down (+y)
    R5 = lambda a: [fa._mul(fa.axis_angle(x, a), m) if names[i] in upper else m for i, m in enumerate(W)]
    sg = 1 if CP._ends(fa, sk, rr, root, R5(10))["head"][2] < e0["head"][2] else -1
    lo, hi = 0.0, 150.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if _mouth(CP._ends(fa, sk, rr, root, R5(sg * mid)))[1] < target_y:   # (y down) still above: bend more
            lo = mid
        else:
            hi = mid
    pitch = (lo + hi) / 2
    assert 5 < pitch < 145, ("can't reach", pitch)
    M = R5(sg * (pitch + BOB * CP.e_of(t, n)))
    M = CP._ik_arms(fa, sk, rr, root, M, hands(CP._ends(fa, sk, rr, root, M)),
                    lambda s: [2.5 if s == "l" else -2.5, -0.5, 0.5])
    return root, M, pitch


FACE_UP = 0.7           # (checkup) her mouth this far above his member's base (model units)


def _base(ctx, root, W, sk, rr):
    """Cloud's member base (620 zcmp.p on the hip bone) in model space."""
    fa = CP._fa()
    _, hb, _ = _mods()
    F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
    m, s_, _ = F[[b[0] for b in sk].index("hip")]
    v = fa._vec(m, hb.member_ends(ctx.char_file("zcmp.p"))[0])
    return [s_[k] + v[k] for k in range(3)]


def checkup(ctx):
    """(user's idea) face down on his pelvis, backside up: her mouth at his member's base, FACE_UP above."""
    mv, hb, sp = _mods()
    fa = CP._fa()
    skc, frc = _frames(ctx, hb.CLOUD_BARE_HRC, "zny1.a")
    rr, root, W = frc[7]
    base = _base(ctx, root, W, skc, rr)
    fa_, sk, rr_g, root_g, W_g = CP._kneel(ctx, sp.RUBY_HRC, sp.RUBY_STAND)
    hands = lambda e: {s: [e["hip@"][0] + (2.6 if s == "l" else -2.6), -0.3, _mouth(e)[2] + 1.5] for s in "lr"}
    target = base[1] - FACE_UP
    for k, n in enumerate(FRAMES):
        frames = []
        for t in range(n):
            r, M, pitch = _bent(ctx, None, target, hands, t, n, sk, rr_g, root_g, W_g)
            frames.append(CP._frame(fa, sk, rr_g, r, M))
        _save(ctx, "ZOA%d" % k, sp.RUBY_STAND, frames)
    r, M, pitch = _bent(ctx, None, target, hands, 7, 15, sk, rr_g, root_g, W_g)
    e = CP._ends(fa, sk, rr_g, r, M)
    assert _mouth(e)[1] > e["hip@"][1], "her face isn't below her hips"     # (y down) backside up
    # placement (deepest frame): she faces his head (DIR + 128), her mouth over his member's base
    m = CP.to_field(_mouth(e), (0, 0, 0), 128)
    tf = CP.to_field(base, (0, 0, 0), 0)
    PLACE["checkup"] = (tf[0] - m[0], tf[1] - m[1], 0, 128, False)


ARCH = 35               # (arched) degrees her upper body leans back


def arched(ctx):
    """ZOB0-3: the rider (ZMB) turned to face him (DIR + 128), her upper body leant ARCH back, hands on his
    thighs (IK); her XYZI as the cowgirl's (14 above his)."""
    mv, hb, sp = _mods()
    fa = CP._fa()
    for k in range(4):
        skg, frg = _frames(ctx, sp.RUBY_HRC, "zmb%d.a" % k)
        skc, frc = _frames(ctx, hb.CLOUD_BARE_HRC, "znb%d.a" % k)
        upper = _upper(skg)
        out = []
        for t, (rr, root, W) in enumerate(frg):
            e0 = CP._ends(fa, skg, rr, root, W)
            M = _turn(fa, skg, W, upper, [1.0, 0.0, 0.0], ARCH,
                      lambda M: CP._ends(fa, skg, rr, root, M)["head"][2] > e0["head"][2])   # (+z: back)
            rrc, rc, Wc = frc[t % len(frc)]
            ec = CP._ends(fa, skc, rrc, rc, Wc)
            tg = {}
            for mine, his in (("l", "r"), ("r", "l")):         # (facing him: her left on his right)
                p = [(ec[his + "_femur"][i] + ec[his + "_femur@"][i]) / 2 for i in range(3)]
                tg[mine] = CP._to_model(CP.to_field(p, (0, 0, 0), 0), (0, 0, 14), 128)
            M = CP._ik_arms(fa, skg, rr, root, M, tg, lambda s: [2.5 if s == "l" else -2.5, -1.0, 0.0])
            out.append(CP._frame(fa, skg, rr, root, M))
        _save(ctx, "ZOB%d" % k, "zmb%d.a" % k, out)
    PLACE["arched"] = (0, 0, 14, 128, False)


def _upper(sk):
    upper, grow = {"hip"}, True
    while grow:
        grow = False
        for b in sk:
            if b[1] in upper and b[0] not in upper:
                upper.add(b[0])
                grow = True
    return upper


# ---- spoon: the edge pair on their sides ---------------------------------------------------------------
SPOON_BEHIND = 14 / UNIT        # (the studio's edge: Cloud 14 behind her, same DIR)


def spoon(ctx):
    mv, hb, sp = _mods()
    fa = CP._fa()
    z = [0.0, 0.0, 1.0]
    for k in range(4):
        skg, frg = _frames(ctx, sp.RUBY_HRC, "zmd%d.a" % k)
        skc, frc = _frames(ctx, hb.CLOUD_BARE_HRC, "znd%d.a" % k)
        R = fa.axis_angle(z, 90)
        P = frg[0][1]                                    # (the pivot: her root at frame 0)
        rot = lambda p: [P[i] + fa._vec(R, [p[j] - P[j] for j in range(3)])[i] for i in range(3)]
        gs, cs = [], []
        for (rrg, rg, Wg), (rrc, rc, Wc) in zip(frg, frc):
            g_root = rot(rg)
            c_root = rot([rc[0], rc[1], rc[2] + SPOON_BEHIND])
            c_root = [c_root[0], c_root[1], c_root[2] - SPOON_BEHIND]
            gs.append((rrg, g_root, [fa._mul(R, m) for m in Wg]))
            cs.append((rrc, c_root, [fa._mul(R, m) for m in Wc]))
        # lay them on the bed: the lowest joint of either 1.0 above it (frame 0)
        low = max(max(e[1] for e in CP._ends(fa, skg, *gs[0][:2], gs[0][2]).values()),
                  max(e[1] for e in CP._ends(fa, skc, *cs[0][:2], cs[0][2]).values()))
        dy = -1.0 - low
        _save(ctx, "ZOC%d" % k, "zmd%d.a" % k,
              [CP._frame(fa, skg, rr, [r[0], r[1] + dy, r[2]], W) for rr, r, W in gs])
        _save(ctx, "ZNZ%d" % k, "znd%d.a" % k,
              [CP._frame(fa, skc, rr, [r[0], r[1] + dy, r[2]], W) for rr, r, W in cs])
    # Cloud's XYZI: SPOON_BEHIND behind hers (same DIR): his = hers + 14 * -facing; her from his
    f = CP.to_field([0, 0, SPOON_BEHIND], (0, 0, 0), 0)
    PLACE["spoon"] = (-f[0], -f[1], 0, 0, False)


# ---- stacked: on her back on top of him -----------------------------------------------------------------
def stacked(ctx):
    mv, hb, sp = _mods()
    fa = CP._fa()
    for k in range(4):
        skc, frc = _frames(ctx, hb.CLOUD_BARE_HRC, "znb%d.a" % k)
        skg, frg = _frames(ctx, sp.RUBY_HRC, "zma%d.a" % k)
        nc, ng = len(frc), len(frg)
        out = []
        y0 = frc[0][1][1]
        for t in range(nc):
            rr, root, W = frg[round(t * ng / nc) % ng]
            e0 = CP._ends(fa, skg, rr, root, W)
            up = STACK_UP + (y0 - frc[t][1][1])           # (y down: his hips up = hers up)
            r = [root[0], root[1] - up, root[2]]
            M = list(W)
            I = [b[0] for b in skg].index
            for s, sx in (("l", 1), ("r", -1)):
                foot = e0[s + "_tibia"]
                T = [foot[0] + sx * STACK_WIDE, foot[1], foot[2]]
                F = fa.forward(skg, rr, r, fa.local_rotations(skg, rr, M))
                D = math.dist(F[I(s + "_femur")][1], T)
                L1 = math.dist(*F[I(s + "_femur")][1:])
                L2 = math.dist(*F[I(s + "_tibia")][1:])
                if D > (L1 + L2) * 0.97:
                    S = F[I(s + "_femur")][1]
                    T = [S[i] + (T[i] - S[i]) * (L1 + L2) * 0.97 / D for i in range(3)]
                foot_m = M[I(s + "_foot")]
                M = sp._two_bone(fa, M, I, F, s + "_femur", s + "_tibia", T, [sx * 1.0, -1.0, 0.0])
                M[I(s + "_foot")] = foot_m
            out.append(CP._frame(fa, skg, rr, r, M))
        _save(ctx, "ZOD%d" % k, "zma%d.a" % k, out)
    # her root over his (same DIR: her head and his both to -facing)
    skc, frc = _frames(ctx, hb.CLOUD_BARE_HRC, "znb1.a")
    skg, frg = _frames(ctx, sp.RUBY_HRC, "zma1.a")
    hc = CP.to_field(frc[0][1], (0, 0, 0), 0)
    hg = CP.to_field(frg[0][1], (0, 0, 0), 0)
    PLACE["stacked"] = (hc[0] - hg[0], hc[1] - hg[1], 0, 0, False)


# ---- saddle: the rider leaning forward onto his shins ------------------------------------------------------
def saddle(ctx):
    mv, hb, sp = _mods()
    fa = CP._fa()
    rise = 14 / UNIT                                     # (the cowgirl: her XYZI 14 above his, same spot / DIR)
    for k in range(4):
        skg, frg = _frames(ctx, sp.RUBY_HRC, "zmb%d.a" % k)
        skc, frc = _frames(ctx, hb.CLOUD_BARE_HRC, "znb%d.a" % k)
        upper, grow = {"hip"}, True
        while grow:
            grow = False
            for b in skg:
                if b[1] in upper and b[0] not in upper:
                    upper.add(b[0])
                    grow = True
        out = []
        for t, (rr, root, W) in enumerate(frg):
            e0 = CP._ends(fa, skg, rr, root, W)
            M = _turn(fa, skg, W, upper, [1.0, 0.0, 0.0], SADDLE_LEAN,
                      lambda M: CP._ends(fa, skg, rr, root, M)["head"][1] > e0["head"][1])   # (y down) head lower
            rrc, rc, Wc = frc[t % len(frc)]
            ec = CP._ends(fa, skc, rrc, rc, Wc)
            tg = {s: [(ec[s + "_tibia"][i] + ec[s + "_tibia@"][i]) / 2 + (rise if i == 1 else 0) for i in range(3)]
                  for s in "lr"}
            M = CP._ik_arms(fa, skg, rr, root, M, tg, lambda s: [2.5 if s == "l" else -2.5, -1.0, 0.0])
            out.append(CP._frame(fa, skg, rr, root, M))
        _save(ctx, "ZOE%d" % k, "zmb%d.a" % k, out)
    PLACE["saddle"] = (0, 0, 14, 0, False)


def build(ctx):
    patient(ctx)
    checkup(ctx)
    arched(ctx)
    spoon(ctx)
    stacked(ctx)
    saddle(ctx)
    return dict(PLACE)

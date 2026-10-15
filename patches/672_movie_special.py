"""(user) The movie minigame's "Special" scenes: role-play shoots in Don Corneo's bedroom, one set per
co-star, unlocked by a full group shoot (`SPECIAL_ON`). Data (scenarios, lines) in
`_movie_special.py`; the cameraman's menu ("Normal scene" / "Special scene") is in 670.

A set is a copy of colne_6 (Corneo's bedroom; its own background-state entities switch / hole /
ball / bed keep their init so the room looks as in the game, everything else blanked). The two
open clothed in front of the bed (the player entity = clothed Cloud, her normal model), role-
playing (`INTRO`); fade; then bare Cloud and the girl's bare model through three positions, a
minute each (`SPECIAL_MINUTE`):
  insert   on the bed: she face down, shins flat on the bed, thighs upright, her torso sloping down
           until her shoulders are on the bed, arms straight back beside her, head tilted back
           (ZRIA); Cloud standing over her, squatting with his hands on his knees, lowering
           himself into her along his member's line (ZCTV). Four stroke lengths
           (`_movie_special.INSERT_FRAMES`: 4 / 3 / 2 / 0.5 s), stepped up evenly over the minute
           by the time, not the presses.
  head     on the floor in front of the bed: the one-girl shoot's head (her ZRTA, his ZCTQ).
  finisher on the bed: Cloud on his back, thrusting (ZCTD); she astride him facing his feet,
           leaning back 45 degrees with her arms straight down to the bed behind her, thighs level
           and 30 out (a V), knees bent, feet planted on the bed; her hips ride his by pivoting her
           torso about her shoulders (hands and feet stay put) (ZRFA).
Her poses are built on Ruby's skeleton and retargeted (670 `_retarget`) to Elena / Scarlet / Tifa /
Aerith; Skye shares Ruby's skeleton. Meter, presses, pay, finisher, pauses (head) as the one-girl
shoot (670 `_shoot`); a special shoot doesn't raise the star rank."""
import math
import struct

import _movie_special as SP
import _movie_girls as MG
import _movie_group as GR
from _config import HB_MINUTES, MOVIE_AT, MOVIE_GIRL, MOVIE_PRESSES, MOVIE_STATE, SPECIAL_ON
from _recruit import sound
from ff7 import asm
from ff7.camera import Camera, facing_screen, screen_range
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

BASE = "colne_6"
SPECIAL_MINUTE = 1800                        # frames a position (user: a minute each)
KEEP = ("switch", "hole", "ball", "bed")     # colne_6's background-state entities: their init stays

# spots (field units; colne_6: the bed is the raised walkmesh piece x -100..95, y 95..309, ~75 above
# the floor at z -237; the camera looks along +y, +x = screen right): (x, y, DIR)
BED_AT = (0, 190, 0xC0)                      # insert / finisher: both entities here, side on (DIR 0xC0: -x)
HEAD_GIRL, HEAD_CLOUD = (-21, 30, 0x40), (17, 29, 0xC0)      # the floor in front of the bed (670's head: 38 apart)
CAM_AT = {"insert": (75, 45), "head": (-95, 45), "finisher": (75, 45)}
INTRO_AT = {"cam": (-110, 60)}                # the cameraman during the intro (the two: `_movie_special.START`)

# insert, her (Ruby's skeleton, model units, y down, she faces -z): knees KNEE_PAD above the bed,
# shoulders SHOULDER_PAD above it (the torso's slope solved for that), the pelvis PELVIS_LAG degrees
# less tipped than the chest, head HEAD_UP degrees above the horizontal (tilted back), arms straight
# back. ENTRY: the point at the bottom of her seat, from her root in her stand pose's frame
KNEE_PAD, SHOULDER_PAD, PELVIS_LAG, HEAD_UP, ENTRY = 0.7, 1.3, 35, 40, (0.0, 1.2, 1.0)
INSERT_ROCK = 6                              # (user) her pelvis rocks this many degrees each way with his stroke
# insert, Cloud (Cloud's skeleton): feet FOOT_X either side, FOOT_Z behind her root; upper body and
# pelvis leaning LEAN forward; he travels STROKE along his member's line, DEPTH inside at the bottom;
# hands on his knees (KNEE_HAND up / forward of the knee joint), head tilted HEAD_BACK back
FOOT_X, FOOT_Z, LEAN, STROKE, DEPTH, HEAD_BACK = 5.5, 1.5, 55, 2.6, 1.8, 25   # (user, since) pelvis lower, body
                                             # further forward: LEAN 45 -> 55, DEPTH 1.0 -> 1.8
# finisher, her: SEAT above Cloud's root, LEAN_BACK from upright, thighs THIGH_DOWN below the
# horizontal and THIGH_OUT out, shins back along the bed, hips lifting by turning the upper body
# LIFT degrees about her shoulders
SEAT, LEAN_BACK, THIGH_DOWN, THIGH_OUT, LIFT, HEAD_TILT = 2.4, 45, 45, 30, 22, 20   # (SEAT 2.6 -> 2.4: room for
                                             # his thrust with her knees on the bed)
RIDE_EXTRA = 0.0                             # (user, since: Cloud thrusts, ZCTD) she rides his hips; this much more at his top
THIGH_UP = 45                                # (user, since) thighs raised this far (from THIGH_DOWN), feet on the bed
FOOT_ON_BED = 0.0                            # her soles this far above the bed (y 0)
RUBY_HRC, RUBY_STAND, CLOUD_HRC = "cbfe.hrc", "dxid.a", "aaaa.hrc"


def _mv():
    from importlib import import_module
    return import_module("670_movie")


def _hb():
    from importlib import import_module
    return import_module("620_honey_bee")


# ---- poses ------------------------------------------------------------------------------------
def _setup(ctx, hrc, stand):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    I = [b[0] for b in sk].index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    fk = lambda W, r: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    return fa, sk, I, base, rr, root, W, fk


def _v(fa):
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    add = lambda a, b: [a[k] + b[k] for k in range(3)]
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    mul = lambda a, s: [c * s for c in a]
    unit = lambda v: mul(v, 1 / math.sqrt(dot(v, v)))
    bdir = lambda m: fa._vec(m, [0, 0, -1])
    return sub, add, dot, mul, unit, bdir


def _pitch(fa, m, target):
    """m turned about the x axis so its bone's direction has target's pitch (the y-z angle)."""
    d = fa._vec(m, [0, 0, -1])
    a = math.degrees(math.atan2(target[1], target[2]) - math.atan2(d[1], d[2]))
    want = math.atan2(target[1], target[2])
    off = lambda M: abs(math.remainder(math.atan2(fa._vec(M, [0, 0, -1])[1], fa._vec(M, [0, 0, -1])[2]) - want,
                                       2 * math.pi))
    M = min((fa._mul(fa.axis_angle([1.0, 0.0, 0.0], s * a), m) for s in (1, -1)), key=off)
    assert off(M) < 1e-4, "pitch"
    return M


def _two_bone(fa, W, I, F, upper, lower, target, pole):
    """Upper / lower bones re-aimed so the lower bone's end reaches `target`, the joint towards
    `pole`; returns W (new list)."""
    sub, add, dot, mul, unit, bdir = _v(fa)
    i, j = I(upper), I(lower)
    S = F[i][1]
    L1, L2 = math.dist(F[i][1], F[i][2]), math.dist(F[j][1], F[j][2])
    D = sub(target, S)
    dd = math.sqrt(dot(D, D))
    assert abs(L1 - L2) + 0.05 < dd < L1 + L2 - 0.02, (upper, dd, L1, L2)
    u = unit(D)
    pp = sub(pole, mul(u, dot(pole, u)))
    pp = unit(pp)
    a_ = (L1 * L1 - L2 * L2 + dd * dd) / (2 * dd)
    K = add(add(S, mul(u, a_)), mul(pp, math.sqrt(max(0.0, L1 * L1 - a_ * a_))))
    W = list(W)
    mv = _mv()
    W[i] = fa._mul(mv._align(fa, bdir(W[i]), sub(K, S)), W[i])
    W[j] = fa._mul(mv._align(fa, bdir(W[j]), sub(target, K)), W[j])
    return W


def _girl_insert(ctx):
    """ZRIA (her insert pose, static) on Ruby's skeleton. Returns her ENTRY point (model space)."""
    fa, sk, I, base, rr, root0, W0, fk = _setup(ctx, RUBY_HRC, RUBY_STAND)
    sub, add, dot, mul, unit, bdir = _v(fa)
    W = list(W0)
    for s in "lr":
        W[I(s + "_femur")] = _pitch(fa, W0[I(s + "_femur")], [0, 1, 0])           # thighs straight down
        W[I(s + "_tibia")] = _pitch(fa, W0[I(s + "_tibia")], [0, 0, 1])           # shins back, flat
        W[I(s + "_foot")] = _pitch(fa, W0[I(s + "_foot")], [0, -0.15, 1])         # feet back, soles up
        for b in ("_uparm", "_foarm", "_hand"):                                    # arms straight back
            W[I(s + b)] = _pitch(fa, W0[I(s + b)], [0, 0, 1])
    W[I("head")] = _pitch(fa, W0[I("head")], [0, -math.sin(math.radians(HEAD_UP)), -math.cos(math.radians(HEAD_UP))])
    torso = ("chest", "non_1", "non_2", "l_collar", "r_collar")

    def pose(theta):
        M = list(W)
        for n in torso:
            M[I(n)] = fa._mul(fa.axis_angle([1.0, 0.0, 0.0], theta), W0[I(n)])
        M[I("hip")] = fa._mul(fa.axis_angle([1.0, 0.0, 0.0], theta - math.copysign(PELVIS_LAG, theta)), W0[I("hip")])
        F = fk(M, [0.0, 0.0, 0.0])
        knee = max(F[I(s + "_femur")][2][1] for s in "lr")
        r = [0.0, -KNEE_PAD - knee, 0.0]                                          # knees on the bed
        F = fk(M, r)
        return M, r, F
    # the sense that tips the chest forward (-z), then the slope that puts the shoulders on the bed
    sense = 1 if pose(30)[2][I("chest")][2][2] < pose(0)[2][I("chest")][2][2] else -1
    lo, hi = 90.0, 179.0
    shoulder = lambda F: max(F[I(s + "_collar")][1][1] for s in "lr")              # (y down)
    assert shoulder(pose(sense * lo)[2]) < -SHOULDER_PAD < shoulder(pose(sense * hi)[2]), "slope range"
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if shoulder(pose(sense * mid)[2]) < -SHOULDER_PAD else (lo, mid)
    M, r, F = pose(sense * (lo + hi) / 2)
    assert F[I("head")][2][2] < r[2] - 3, "head forward"
    for s in "lr":
        assert abs(F[I(s + "_tibia")][2][1] - F[I(s + "_tibia")][1][1]) < 0.3, "shins flat"
        assert F[I(s + "_hand")][2][2] > F[I(s + "_uparm")][1][2] + 5, "arms back"
        assert F[I(s + "_hand")][2][1] < 0.2, "hands above the bed"
    # her entry point: ENTRY (stand frame, from the root) carried by her pelvis's turn
    Rh = fa._mul(M[I("hip")], fa._t(W0[I("hip")]))
    entry = add(r, fa._vec(Rh, list(ENTRY)))
    base.frames = [(rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, M))] * 15
    ctx.char_file("zria.a", base.build())
    return entry


def _member(ctx, fa):
    """Cloud's member (620 zcmp.p, on the hip bone): (base, tip) in the hip bone's frame."""
    d = ctx.char_file("zcmp.p")
    nv = struct.unpack_from("<16I", d, 0)[3]
    assert nv == 8, nv
    V = [struct.unpack_from("<3f", d, 128 + 12 * i) for i in range(nv)]
    avg = lambda vs: [sum(v[k] for v in vs) / len(vs) for k in range(3)]
    return avg(V[:4]), avg(V[4:])                                                  # (z-major corners)


def _cloud_insert(ctx, entry, n, name):
    """Cloud's insert (Cloud's skeleton), n frames a stroke: frame 0 out (top), n/2 in."""
    fa, sk, I, base, rr, root0, W0, fk = _setup(ctx, CLOUD_HRC, "acfe.a")
    sub, add, dot, mul, unit, bdir = _v(fa)
    upper = ("hip", "chest", "head", "l_chest", "l_collar", "l_uparm", "l_foarm", "l_hand",
             "r_chest", "r_collar", "r_uparm", "r_foarm", "r_hand")
    sense = 1 if fk([fa._mul(fa.axis_angle([1.0, 0, 0], 20), m) if sk[i][0] in upper else m
                     for i, m in enumerate(W0)], root0)[I("head")][2][2] < fk(W0, root0)[I("head")][2][2] else -1
    W = [fa._mul(fa.axis_angle([1.0, 0, 0], sense * LEAN), m) if sk[i][0] in upper else m for i, m in enumerate(W0)]
    W[I("head")] = fa._mul(fa.axis_angle([1.0, 0, 0], -sense * HEAD_BACK), W[I("head")])
    mb, mt = _member(ctx, fa)
    F0 = fk(W, [0.0, 0.0, 0.0])
    tip0 = fa._vec(W[I("hip")], mt)                                                # (hip bone starts at the root)
    md = unit(sub(fa._vec(W[I("hip")], mt), fa._vec(W[I("hip")], mb)))
    assert md[1] > 0.3 and md[2] < 0, ("member points down and forward", md)
    root_in = sub(add(entry, mul(md, DEPTH)), tip0)
    ankle0 = {s: fk(W0, root0)[I(s + "_tibia")][2] for s in "lr"}
    feet = {s: [(1 if s == "l" else -1) * FOOT_X, ankle0[s][1], entry[2] + FOOT_Z] for s in "lr"}
    frames = []
    for t in range(n):
        e = (1 - math.cos(2 * math.pi * t / n)) / 2                               # 0 out .. 1 in
        r = sub(root_in, mul(md, STROKE * (1 - e)))
        Wt = list(W)
        for s, out in (("l", 1), ("r", -1)):
            F = fk(Wt, r)
            Wt = _two_bone(fa, Wt, I, F, s + "_femur", s + "_tibia", feet[s], [out * 0.6, -0.2, -1.0])
            Wt[I(s + "_foot")] = W0[I(s + "_foot")]                               # feet flat
        for s, out in (("l", 1), ("r", -1)):                                       # hands on his knees
            F = fk(Wt, r)
            knee, hip_j = F[I(s + "_femur")][2], F[I(s + "_femur")][1]
            hand_len = math.dist(F[I(s + "_hand")][1], F[I(s + "_hand")][2])
            reach = math.dist(F[I(s + "_uparm")][1], F[I(s + "_uparm")][2]) + \
                math.dist(F[I(s + "_foarm")][1], F[I(s + "_foarm")][2])
            sh = F[I(s + "_uparm")][1]
            grip = None
            for f in [k / 10 for k in range(0, 8)]:                                # from the knee up the thigh
                p = add(add(knee, mul(sub(hip_j, knee), f)), [0.0, -0.9, -0.3])
                if math.dist(sh, p) < reach - 0.15:
                    grip = p
                    break
            assert grip is not None, ("hands on knees", s, t)
            wrist = add(grip, [0.0, -hand_len * 0.8, 0.0])
            Wt = _two_bone(fa, Wt, I, F, s + "_uparm", s + "_foarm", wrist, [out * 1.0, -0.3, 0.6])
            Wt[I(s + "_hand")] = fa._mul(_mv()._align(fa, bdir(Wt[I(s + "_hand")]), [0, 1, -0.2]), Wt[I(s + "_hand")])
        F = fk(Wt, r)
        for s in "lr":
            assert math.dist(F[I(s + "_tibia")][2], feet[s]) < 0.05, ("feet", s, t)
        frames.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, Wt)))
    F = fk(W, root_in)
    tip_in = add(root_in, tip0)
    assert math.dist(tip_in, add(entry, mul(md, DEPTH))) < 1e-6
    base.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


def _girl_insert_rock(ctx, n, name):
    """(user: "animate the insert girls subtle rocking their pelvises") ZRIA over n frames (one of
    Cloud's insert strokes): her pelvis (the hip bone) tilts `INSERT_ROCK` degrees each way about her
    side axis in time with his stroke (back to meet him as he goes in), every other bone keeping its
    turn, so her thighs, shins and arms stay put (the torso rides on the pelvis's end, a little)."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    I = [b[0] for b in sk].index
    a = fa.Anim(ctx.char_file("zria.a"))
    rr, rp, rots = a.frames[0]
    W = [m for m, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
    frames = []
    for t in range(n):
        e = (1 - math.cos(2 * math.pi * t / n)) / 2                                # his stroke: 0 out .. 1 in
        Wt = list(W)
        Wt[I("hip")] = fa._mul(fa.axis_angle([1.0, 0.0, 0.0], INSERT_ROCK * (2 * e - 1)), W[I("hip")])
        frames.append((rr, rp, fa.local_rotations(sk, rr, Wt)))
    F0 = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], frames[0][2])
    F1 = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], frames[n // 2][2])
    for s in "lr":                                                                 # knees and feet stay
        assert math.dist(F0[I(s + "_tibia")][2], F1[I(s + "_tibia")][2]) < 0.05, ("legs still", s)
    a.frames = frames
    ctx.char_file(name, a.build())


def _cloud_still(ctx):
    """ZCTW: Cloud on his back, still (ZCTD's first frame, 15 frames)."""
    from ff7 import fieldanim as fa
    a = fa.Anim(ctx.char_file("zctd.a"))
    a.frames = [a.frames[0]] * 15
    ctx.char_file("zctw.a", a.build())


def _girl_finisher(ctx):
    """ZRFA (Ruby's skeleton) astride Cloud thrusting in ZCTD (his frames: she rides his hips)."""
    fa, sk, I, base, rr, root0, W0, fk = _setup(ctx, RUBY_HRC, RUBY_STAND)
    sub, add, dot, mul, unit, bdir = _v(fa)
    csk = fa.skeleton(ctx.char_file(CLOUD_HRC).decode("latin-1"))
    crr, crp, _ = fa.Anim(ctx.char_file("zctw.a")).frames[0]
    his = [crp[0], -crp[1], crp[2]]
    r0 = [his[0], his[1] - SEAT, his[2]]
    upper = ("hip", "chest", "head", "non_1", "non_2")                              # (not the collars / arms)
    sense = 1 if fk([fa._mul(fa.axis_angle([1.0, 0, 0], 20), m) if sk[i][0] in upper else m
                     for i, m in enumerate(W0)], r0)[I("head")][2][2] > fk(W0, r0)[I("head")][2][2] else -1
    W = [fa._mul(fa.axis_angle([1.0, 0, 0], sense * LEAN_BACK), m) if sk[i][0] in upper else m
         for i, m in enumerate(W0)]
    W[I("head")] = fa._mul(fa.axis_angle([1.0, 0, 0], sense * HEAD_TILT), W[I("head")])
    F = fk(W, r0)
    for s, out in (("l", 1), ("r", -1)):                                           # arms straight to the bed
        sh = F[I(s + "_uparm")][1]
        L = sum(math.dist(F[I(s + b)][1], F[I(s + b)][2]) for b in ("_uparm", "_foarm", "_hand"))
        drop = -0.3 - sh[1]
        back = math.sqrt(max(0.0, L * L - drop * drop))
        d = unit([out * back * 0.45, drop, back * 0.9])
        for b in ("_collar", "_uparm", "_foarm", "_hand"):
            if b != "_collar":
                W[I(s + b)] = fa._mul(_mv()._align(fa, bdir(W[I(s + b)]), d), W[I(s + b)])
    v, up_ = math.radians(THIGH_OUT), math.radians(THIGH_DOWN - THIGH_UP)
    F = fk(W, r0)
    S0_ = fk(W0, root0)
    feet = {}
    for s, out in (("l", 1), ("r", -1)):
        # (user, since) "legs up, forward rotated 45 degrees and the knee bent to put the feet on the
        # ground, with legs spread in a V": each thigh turned THIGH_UP up from THIGH_DOWN (45 below the
        # horizontal -> level), THIGH_OUT out, the shin straight down from the knee to the bed, the foot
        # flat on it; those ankles stay planted while she rides (two-bone IK, knees up and out)
        hip_j = F[I(s + "_femur")][1]
        Lt = math.dist(F[I(s + "_femur")][1], F[I(s + "_femur")][2])
        Ls = math.dist(F[I(s + "_tibia")][1], F[I(s + "_tibia")][2])
        d = [out * math.sin(v) * math.cos(up_), math.sin(up_), -math.cos(v) * math.cos(up_)]   # (y down)
        knee = add(hip_j, mul(d, Lt))
        ankle_y = S0_[I(s + "_tibia")][2][1] - S0_[I(s + "_foot")][2][1] - FOOT_ON_BED   # her stand ankle height
        drop = ankle_y - knee[1]
        assert 0 < drop < Ls, ("feet reach the bed", s, drop, Ls)
        ahead = math.sqrt(Ls * Ls - drop * drop)
        feet[s] = add(knee, [out * math.sin(v) * ahead, drop, -math.cos(v) * ahead])
    # (user) Cloud thrusts (ZCTD, his hips bucking up): she rides his hips, lifted RIDE_EXTRA more at his top,
    # her torso turning about her shoulders (hands planted), knees sliding on the bed (shins flat)
    cl = fa.Anim(ctx.char_file("zctd.a")).frames
    hy = [-f[1][1] for f in cl]                                                   # his root height (y down)
    lo_ = min(hy)
    pivot = [0.0] + [sum(F[I(s + "_collar")][1][k] for s in "lr") / 2 for k in (1, 2)]   # between the shoulders
    rot = lambda g: fa.axis_angle([1.0, 0, 0], g)
    frames = []
    for t in range(len(cl)):
        e = (hy[0] - hy[t]) / (hy[0] - lo_)                                       # 0 his bottom .. 1 his top
        want = r0[1] + (hy[t] - hy[0]) - RIDE_EXTRA * e
        g_lo, g_hi = (0.0, 40.0) if add(pivot, fa._vec(rot(10), sub(r0, pivot)))[1] < r0[1] else (0.0, -40.0)
        for _ in range(40):                                                       # the turn that lifts the root to `want`
            mid = (g_lo + g_hi) / 2
            y_ = add(pivot, fa._vec(rot(mid), sub(r0, pivot)))[1]
            g_lo, g_hi = (mid, g_hi) if y_ > want else (g_lo, mid)
        R = rot((g_lo + g_hi) / 2)
        Wt = [fa._mul(R, m) if sk[i][0] in upper else m for i, m in enumerate(W)]
        r = add(pivot, fa._vec(R, sub(r0, pivot)))
        assert abs(r[1] - want) < 0.05, (t, r[1], want)
        for s, out in (("l", 1), ("r", -1)):
            F = fk(Wt, r)
            Wt = _two_bone(fa, Wt, I, F, s + "_femur", s + "_tibia", feet[s],
                           [out * math.sin(v), -1.0, -math.cos(v)])              # knees up, forward and out
            Wt[I(s + "_foot")] = W0[I(s + "_foot")]                               # flat, as she stands
        F = fk(Wt, r)
        for s in "lr":
            assert math.dist(F[I(s + "_tibia")][2], feet[s]) < 0.05, ("feet planted", t, s)
            assert abs(F[I(s + "_foot")][2][1] + FOOT_ON_BED) < 0.05, ("toes on the bed", t, s)
            assert math.dist(F[I(s + "_hand")][2], fk(W, r0)[I(s + "_hand")][2]) < 0.4, "hands planted"
        frames.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file("zrfa.a", base.build())


def poses(ctx):
    """Every special pose; (girl anim names, Cloud anim names) on Ruby's / Cloud's skeleton, 4 per
    position (P insert, Q head, R finisher; speed 0..3) then the head's held frame (Q9)."""
    from ff7 import fieldanim as fa
    entry = _girl_insert(ctx)
    for s, n in enumerate(SP.INSERT_FRAMES):
        _cloud_insert(ctx, entry, n, "ZNP%d.tor" % s)
    _cloud_still(ctx)
    _girl_finisher(ctx)
    mv = _mv()
    girl, cloud = [], []
    for s, n in enumerate(SP.INSERT_FRAMES):              # insert: (user, since) her pelvis rocks with his stroke
        _girl_insert_rock(ctx, n, "zmp%d.a" % s)
        girl.append("ZMP%d.tor" % s)
        cloud.append("ZNP%d.tor" % s)
    for letter, g_, c_ in (("Q", "zrta.a", "zctq.a"), ("R", "zrfa.a", "zctd.a")):
        for who, src, out in (("M", g_, girl), ("N", c_, cloud)):
            frames = fa.Anim(ctx.char_file(src)).frames
            assert len(frames) == 15, (src, len(frames))
            for s, n in enumerate(mv.SPEEDS):
                a = fa.Anim(ctx.char_file(src))
                a.frames = [frames[i * len(frames) // n] for i in range(n)]
                name = "Z%s%s%d" % (who, letter, s)
                ctx.char_file(name.lower() + ".a", a.build())
                out.append(name + ".tor")
    for digit, frame in (("9", 0), ("8", 7)):     # the head's pause hold, then the deep one (the hold)
        for who, src, out in (("M", "zrta.a", girl), ("N", "zctq.a", cloud)):
            a = fa.Anim(ctx.char_file(src))
            a.frames = a.frames[frame:frame + 1]
            ctx.char_file("z%sq%s.a" % (who.lower(), digit), a.build())
            out.append("Z%sQ%s.tor" % (who, digit))
    mv._try_anim(ctx, "ZRTA", "ZMQ7")             # (user) her try to pull back during the hold (hers only)
    girl.append("ZMQ7.tor")
    return girl, cloud


# ---- the set ----------------------------------------------------------------------------------
POSITIONS = ["insert", "head", "finisher"]
SPRITES = {"QGEA": ("QGEB", "QGEC", "QGED"), "QCEA": ("QCEB", "QCEC", "QCED"), "QHEA": ("QHEB", "QHEC", "QHED")}   # colne_6's own gauge sizes
_BUILT = {}


def _girl(ctx, key):
    """(her donor (field, model): clothed as it is, bare with `bare hrc`; bare hrc; an anim to append to
    the clothed model for her stand, or None (its anim 0); gil per press)."""
    mv = _mv()
    if key == "ruby":
        return mv.RUBY_DONOR, mv.BARE_HRC, None, mv.PAY_RATE
    if key == "skye":
        return mv.SKYE_DONOR, mv.SKYE_BARE, "DXID.tor", mv.PAY_RATE * mv.SKYE_PAY
    g = next(g for g in MG.GIRLS if g["key"] == key)
    return g["donor"][:2], g["hrc"], None, g["rate"]


def _special(ctx, key, back):
    mv, hb, dt = _mv(), _hb(), _dates()
    girl_anims, cloud_anims = _BUILT["anims"]
    f = ctx.new_field(SP.FIELDS[key], ctx.field(BASE).build())
    sec = Script.parse(f.sections[0])
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    keep = {names.index(n): sec.script_ops(names.index(n), 0) for n in KEEP}
    for e, ops in keep.items():
        assert ops[-1].op == 0x00 and not any(o.op == 0xA1 for o in ops), (names[e], [o.raw.hex() for o in ops][:4])
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    loader = ModelLoader(f.section("models"))
    assert ModelLoader.name(loader.models[0]).endswith("main_n_cloud.char")
    loader.models = loader.models[:1]                                # Cloud only (Corneo & co. go)
    CL = names.index("cloud")
    spot = lambda x, y: mv._spot(mesh, x, y, 0, True)               # (a lower piece at z -639 under the floor)
    bed = spot(*BED_AT[:2])
    assert bed[2] > -200, ("on the bed", bed)
    hg, hc = spot(*HEAD_GIRL[:2]), spot(*HEAD_CLOUD[:2])
    assert abs(hg[2] + 237) < 1 and abs(hc[2] + 237) < 1, (hg, hc)              # the floor
    places = []
    for pn in POSITIONS:
        g, c, gd, cd = (bed, bed, BED_AT[2], BED_AT[2]) if pn != "head" else (hg, hc, HEAD_GIRL[2], HEAD_CLOUD[2])
        cm = spot(*CAM_AT[pn])
        places.append(dict(girl=g, gdir=gd, cloud=c, cdir=cd, cam=cm, focus=g,
                           camdir=_dates()._dir_to(g[0] - cm[0], g[1] - cm[1])))
    # gauge per position (as 670 `_shoot`)
    left, top, right, bottom = screen_range(f.section("triggers"))
    near = min(mv._view_depth(cam, v) for t in mesh.tris for v in t if t[0][2] > -600) * 0.8
    donor_loader = ModelLoader(ctx.field(mv.mm.DONOR_FIELD).section("models"))
    sprite_scale = round(ModelLoader.entry_scale(donor_loader.models[mv.mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    unit = 3.41 * sprite_scale / 512
    half = mv.GAUGE_PX / 2 * near / cam.zoom / unit
    half_cursor = mv.CURSOR_PX / 2 * near / cam.zoom / unit
    for pl in places:
        sx, sy = cam.project(*pl["focus"][:3])
        sx = min(max(sx, left + 160), right - 160)
        sy = min(max(sy, top + 120), bottom - 120)
        gy = sy + mv.GAUGE_Y
        g = mv._unproject(cam, sx, gy, near)
        pl["gauge"] = (round(g[0]), round(g[1]), round(g[2]), mv._nearest_tri(mesh, g[0], g[1]))
        pl["icon"] = mv._icon_at(cam, mesh, sx, sy, near)
        pl["cursor"] = []
        for b in range(21):
            off = ((b * 50 + 25) - 500) / 1000 * mv.GAUGE_PX
            q = mv._unproject(cam, sx + off, gy - mv.CURSOR_UP, near)
            pl["cursor"].append((round(q[0]), round(q[1]), round(q[2]), mv._nearest_tri(mesh, q[0], q[1])))
    gx, gy_, gz = places[0]["gauge"][:3]

    def tilt(d):
        a = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy_, gz), cam.project(gx + 50 * math.cos(a), gy_ + 50 * math.sin(a), gz)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        return abs(dy) / (abs(dx) + 1e-9) + (0 if dx > 0 else 100)
    sprite_dir = min(range(256), key=tilt)
    assert tilt(sprite_dir) < 0.05, tilt(sprite_dir)

    # models: 1 bare Cloud, 2 her bare, 3 her clothed, 4 cameraman, 5 gauge, 6 cursor
    cl0 = loader.models[0]
    loader.models.append(ModelLoader.with_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), cloud_anims))
    cfirst = len(ModelLoader.anims(loader.models[1])) - len(cloud_anims)
    (dfield, dmodel), bare_hrc, stand_extra, rate = _girl(ctx, key)
    donor = ModelLoader(ctx.field(dfield).section("models"))
    if key in ("ruby", "skye"):
        hers = girl_anims
    else:
        g_ = next(g for g in MG.GIRLS if g["key"] == key)
        hers = mv._retarget(ctx, girl_anims, g_["prefix"], g_["donor"][2],
                            ModelLoader.anims(donor.models[dmodel])[0].split(".")[0].lower() + ".a", g_.get("head_down"))
    r = loader.add_from(donor, dmodel)
    loader.models[r] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[r], bare_hrc,
                                                                   ModelLoader.name(loader.models[r])[:-5] + "_b.char"), hers)
    gfirst = len(ModelLoader.anims(loader.models[r])) - len(hers)
    rc = loader.add_from(donor, dmodel)                               # her, clothed (the intro)
    stand = 0
    if stand_extra:
        loader.models[rc] = ModelLoader.with_anims(loader.models[rc], [stand_extra])
        stand = len(ModelLoader.anims(loader.models[rc])) - 1
    # (user) the staged intro: Cloud's gestures (620 CLOUD_EXTRA) on the player's model; hers (the dancer's
    # gestures, `SP.GESTURES`; Ruby and Skye have the dancer's skeleton, the others get them retargeted)
    acts = [(who, a) for st in SP.STAGE[key] for part in ("pre", "with_") for who, a in st.get(part, [])]
    c_g = sorted({a for who, a in acts if who == "C" and isinstance(a, str) and a in hb.CLOUD_EXTRA})
    g_g = sorted({a for who, a in acts if who == "G" and isinstance(a, str) and a in SP.GESTURES})
    loader.models[0] = ModelLoader.with_anims(loader.models[0], [hb.CLOUD_EXTRA[g] for g in c_g])
    c_anim = {g: ModelLoader.anims(loader.models[0]).index(hb.CLOUD_EXTRA[g]) for g in c_g}
    files = {g: SP.GESTURES[g] for g in g_g}
    if isinstance(SP.START[key]["G"], tuple):                        # she starts lying (the dancer's DZBA)
        assert key in ("ruby", "skye"), key
        files["lie"] = "DZBA.tor"
    if key not in ("ruby", "skye") and files:
        g_ = next(g for g in MG.GIRLS if g["key"] == key)
        stand_a = ModelLoader.anims(donor.models[dmodel])[0].split(".")[0].lower() + ".a"
        batches = [{}, {}]                                           # (retargeted names end in the source's
        for g, f_ in files.items():                                  # last two letters: no two alike a batch)
            batches[any(f_[2:4] == o[2:4] for o in batches[0].values())][g] = f_
        for b, batch in enumerate(batches):
            if batch:
                out = mv._retarget(ctx, list(batch.values()), ("W", "V")[b] + key[0].upper(), g_["donor"][2], stand_a)
                files.update(dict(zip(batch, out)))
    loader.models[rc] = ModelLoader.with_anims(loader.models[rc], list(files.values()))
    g_anim = {g: ModelLoader.anims(loader.models[rc]).index(f_) for g, f_ in files.items()}
    cm = loader.add_from(ModelLoader(ctx.field(mv.CAMERA_DONOR[0]).section("models")), mv.CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_FILM)
    # (user) "stop the animation of the cameraman in the first part": in the intro he holds 670's one-frame
    # still pose (ZCFA = FDCB's first frame), filming (FFBC) only from the first position
    loader.models[cm] = ModelLoader.with_anims(loader.models[cm], [mv.CAMERA_STILL])
    idle_cam = ModelLoader.anims(loader.models[cm]).index(mv.CAMERA_STILL)
    if "sprites" not in _BUILT:
        mv.SPRITES = SPRITES
        _BUILT["sprites"] = mv._sprites(ctx, half, half_cursor, mv.ICON_PX / 2 * near / cam.zoom / unit)
    for hrc in SPRITES:
        loader.models.append(ModelLoader.with_scale(_BUILT["sprites"][hrc], sprite_scale))
    assert (r, rc, cm, len(loader.models)) == (2, 3, 4, 8), (r, rc, cm, len(loader.models))   # (7: the Square icon)

    ents = {}
    for name in ("cloudb", "girl", "girlc", "camera", "gauge", "cursor", "keys", "voice", "hush",
                 "shout", "hush2", "hush3", "icon", "sqkey"):
        ents[name] = len(sec.entity_names)
        sec.entity_names.append(name.encode("latin-1").ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    P, STEP, NEW, RUN, K, HELD, FIN = mv.P, mv.STEP, mv.NEW, mv.RUN, mv.K, mv.HELD, mv.FIN
    POS, VEL, PR, TOT, FR, RATE, T, S, NEXT, BKT, NT, FT = (mv.POS, mv.VEL, mv.PR, mv.TOT, mv.FR, mv.RATE, mv.T,
                                                           mv.S, mv.NEXT, mv.BKT, mv.NT, mv.FT)
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    by_p = lambda make: mv._chain(P, [make(p, pl) for p, pl in enumerate(places)])
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    anim = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]   # (ANIMB: at once, see 670)
    sp_ = {k: spot(*v) for k, v in SP.SPOTS.items()}                # (asserted on the floor)
    for k, v in sp_.items():
        assert abs(v[2] + 237) < 1, ("intro spot on the floor", k, v)
    st_ = SP.START[key]
    g_start = st_["G"][1] if isinstance(st_["G"], tuple) else st_["G"]
    ispot = {"cloud": sp_[st_["C"]], "girl": sp_[g_start], "cam": spot(*INTRO_AT["cam"])}
    to = lambda a, b: _dates()._dir_to(ispot[b][0] - ispot[a][0], ispot[b][1] - ispot[a][1])
    scripts = {e: {0: ops} for e, ops in keep.items()}
    scripts[CL] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*ispot["cloud"]), d_(to("cloud", "girl")),
                       hb._visi(0), asm.ret(), asm.ret()],
                   2: by_p(lambda p, pl: [xyzi(*pl["focus"])]) + [hb._visi(0), asm.ret()],
                   3: [xyzi(*ispot["cloud"]), d_(to("cloud", "girl")), hb._visi(1)] + anim(0) + [asm.ret()]}

    def pose(first, who, wdir):
        def make(p, pl):
            return [xyzi(*pl[who]), d_(pl[wdir]), hb._visi(1)] + mv._chain(STEP, [anim(first + 4 * p + s_) for s_ in range(4)])
        return by_p(make) + [asm.ret()]
    # (head's stops) kind 0 pulled back (Q9), 1 the deepest (Q8: the hold), 2 her try (Q7, once, then Q8)
    hold = lambda first, kind=0: mv._chain(P, [[], anim(first + 4 * len(POSITIONS) + kind) if kind < 2 else
                                               [mv._animb(), Op(bytes([0xA2, first + 4 * len(POSITIONS) + 1, 1])),
                                                Op(bytes([0xAE, first + 4 * len(POSITIONS) + 2, 1]))], []]) + [asm.ret()]
    scripts[ents["cloudb"]] = {0: [Op(bytes([0xA1, 1])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                               2: pose(cfirst, "cloud", "cdir"), 4: hold(cfirst), 5: hold(cfirst, 1)}
    scripts[ents["girl"]] = {0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                             2: pose(gfirst, "girl", "gdir"), 4: hold(gfirst), 5: hold(gfirst, 1),
                             6: [hb._w(mv.hold_try_delay())] + hold(gfirst, 2)}
    scripts[ents["icon"]], scripts[ents["sqkey"]] = mv._hold_entities(hb, 7, sprite_dir,
                                                                      by_p(lambda p, pl: [xyzi(*pl["icon"])]))
    scripts[ents["girlc"]] = {0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                              2: [hb._visi(0), asm.ret()],
                              3: [xyzi(*ispot["girl"]), d_(to("girl", "cloud")), hb._visi(1)] +
                              anim(g_anim["lie"] if isinstance(st_["G"], tuple) else stand) + [asm.ret()]}
    # (user) the staged intro: one script slot per action, from slot 4 (walks: MOVE, then face the other)
    actor = {"C": CL, "G": ents["girlc"]}
    other = {"C": ents["girlc"], "G": CL}
    slot_of = {}

    def act_ops(who, a):
        if isinstance(a, tuple):
            assert a[0] == "walk", a
            x_, y_ = SP.SPOTS[a[1]]
            return [hb._move(x_, y_), hb._tura(other[who])]
        if a == "face":
            return [hb._tura(other[who])]
        if a == "bed":
            return [d_(0x80)]                                        # +y: towards the bed's foot
        if a == "stand":
            return anim(stand)
        if a == "lie":
            return anim(g_anim["lie"])
        return [mv._animb(), Op(bytes([0xAE, (c_anim if who == "C" else g_anim)[a], 1]))]   # once, then the idle
    for who, a in acts:
        if (who, a) not in slot_of:
            n_ = 4 + sum(1 for w_, _ in slot_of if w_ == who)
            assert n_ < 32, n_
            slot_of[(who, a)] = n_
            scripts.setdefault(actor[who], {})[n_] = act_ops(who, a) + [asm.ret()]
    icd = _dates()._dir_to((ispot["girl"][0] + ispot["cloud"][0]) / 2 - ispot["cam"][0],
                           (ispot["girl"][1] + ispot["cloud"][1]) / 2 - ispot["cam"][1])
    scripts[ents["camera"]] = {0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide() + anim(film) + [asm.ret(), asm.ret()],
                               2: by_p(lambda p, pl: [xyzi(*pl["cam"]), d_(pl["camdir"])]) + [hb._visi(1)] + anim(film)
                               + [asm.ret()],
                               3: [xyzi(*ispot["cam"]), d_(icd), hb._visi(1)] + anim(idle_cam) + [asm.ret()]}
    scripts[ents["gauge"]] = {0: [Op(bytes([0xA1, 5])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret(), asm.ret()],
                              2: by_p(lambda p, pl: [xyzi(*pl["gauge"])]) + [hb._visi(1), asm.ret()]}
    loop, idle = asm.nop(), asm.nop()
    cur = [loop, asm.if_byte(RUN, "==", 1, idle), asm.setword(BKT, POS), hb._arith(0x8C, BKT, 50)]
    cur += by_p(lambda p, pl: mv._tree(BKT, 0, 20, lambda b: [xyzi(*pl["cursor"][b])]) + [hb._visi(1), hb._w(1),
                                                                                            asm.goto_back(loop)])
    cur += [idle, hb._visi(0), hb._w(1), asm.goto_back(loop)]
    scripts[ents["cursor"]] = {0: [Op(bytes([0xA1, 6])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret()] + cur
                               + [asm.ret()]}
    wait = hb._w(1)
    back1, up = asm.goto_back(wait), asm.setbyte(HELD, 0)
    scripts[ents["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x96, FR[0], FR[1]])),
                                 Op(bytes([0x30]) + struct.pack("<H", mv.OK_KEY) + b"\x00", target=up),
                                 asm.if_byte(HELD, "==", 0, back1), asm.setbyte(HELD, 1),
                                 Op(bytes([0x96, PR[0], PR[1]])), back1,
                                 up, asm.goto_back(wait), asm.ret()]}
    # voice: her role-play lines (Cloud's "C:" lines too) while it plays
    name = SP.NAMES[key]
    texts = {}

    def text_of(who, text):
        if text.startswith("C:"):
            t = "{CLOUD}\n“%s”" % text[2:]
        elif text.startswith("("):
            t = "%s\n%s" % (who, text)
        else:
            t = "%s\n“%s”" % (who, text)
        if t not in texts:
            texts[t] = sec.add_string(mv._encode(t))
        return t
    vl, vdone = asm.nop(), asm.nop()
    voice = [asm.ret(), vl, hb._w(mv.SAY_EVERY), asm.if_byte(RUN, "==", 1, vdone),
             Op(bytes([0x95, K[0], K[1]])), Op(bytes([0x8D, K[0] << 4, K[1], mv.LINES_EACH]))]

    def line(p, pl):
        lines = SP.LINES[key][POSITIONS[p]]
        out = []
        for k_ in range(mv.LINES_EACH):
            raw = lines[k_ % len(lines)]
            t = text_of(name, raw)
            out.append([Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, mv.LINE_Y),
                        hb._req(ents["hush"], 2, wait=False)] +
                       ([hb._req(ents["icon"], 4, wait=False)] if mv._slaps(raw) else []) +   # (user) a slap prompt
                       [asm.message(1, texts[t])])
        return mv._chain(K, out)
    voice += by_p(line) + [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.SAY_FOR), Op(b"\x54\x01"), asm.ret()]}
    shout = "Cameraman\n“Five seconds left! Go all out, star!\n Give me a FINISHER!”"
    scripts[ents["shout"]] = {0: [asm.ret(), asm.ret()],
                              2: [Op(b"\x52\x02\x00\x01"), hb._window(shout, 2, 8, 56),
                                  hb._req(ents["hush2"], 2, wait=False), asm.message(2, sec.add_string(mv._encode(shout))),
                                  asm.ret()]}
    scripts[ents["hush2"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(mv.FINISH_SAY_FOR), Op(b"\x54\x02"), asm.ret()]}
    scripts[ents["hush3"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(GR.PAUSE_FRAMES[1]), Op(b"\x54\x03"), asm.ret()],
                              3: [hb._w(GR.HOLD_SAY), Op(b"\x54\x03"), asm.ret()]}

    # director
    lost, wrap, tick, hi_red = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    actors = (ents["cloudb"], ents["girl"])
    place_all = lambda: [hb._req(e, 2, wait=False) for e in (CL, *actors, ents["girlc"], ents["camera"], ents["gauge"],
                                                             ents["icon"])] \
        + [hb._w(6)]

    def pause_cond(no):                              # head only
        doit = asm.nop()
        return [asm.if_byte(P, "!=", 1, doit), asm.goto(no), doit]
    walkout = asm.nop()                          # (user, profiles) she's had enough: a CUT
    leave = lambda key_: hb._say(sec, GR.NAMES[key_] + "\n" + mv.PF.PROFILES[key_]["leave"]) + [asm.goto(walkout)]
    pause = mv._pause_ops(hb, sec, list(actors), ents["hush3"], lambda block: block(key), pause_cond, ents["icon"],
                          lambda key_: rate, leave=leave)
    main = [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS, 500), asm.setword(VEL, 1000),
            asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(P, 0),
            asm.setbyte(STEP, 0), asm.setbyte(K, 0), asm.setword(NEXT, SPECIAL_MINUTE), asm.setbyte(FIN, 0),
            asm.setbyte(mv.RULES, 1), asm.setbyte(mv.CTRL, 0), asm.setbyte(mv._ann(0), 0)] + \
           [hb._req(e, 3) for e in (CL, ents["girlc"], ents["camera"])] + [hb._w(20)]
    main += [Op(hb.FADE_IN), Op(b"\x6C")]
    for t_ in SP.OPENING:
        main += say(t_)
    main += say("“Today's scene:\n %s.\n Places! And... roll it!”" % SP.SCENARIO[key])
    for (who, t_), st in zip(SP.INTRO[key], SP.STAGE[key]):     # (user) staged: moves, gestures, pauses
        for w_, a in st.get("pre", []):
            main += [hb._req(actor[w_], slot_of[(w_, a)])]                    # (waited for)
        for w_, a in st.get("with_", []):
            main += [hb._req(actor[w_], slot_of[(w_, a)], wait=False)]
        main += hb._say(sec, ("{CLOUD}" if who == "C" else name) + "\n" +
                        (t_ if t_.startswith("(") else "“%s”" % t_.replace("\n", "\n ").replace("\n  ", "\n ")))
        main += [hb._w(SP.PACE)]
    main += [Op(hb.FADE_OUT), Op(b"\x6C")] + place_all() + [hb._w(4), Op(hb.FADE_IN), Op(b"\x6C")]
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, mv.MUSIC]) + bytes(8)), hb._w(15)]
    main += say("“Same rules as always: tap OK, mind the\n meter. Three positions, a minute each.\n ...And... ACTION!”")
    main += [asm.setword(FR, 0), asm.setword(PR, 0), asm.setword(NT, mv.TICK)] + mv._pause_arm(hb, SPECIAL_MINUTE) + \
        [asm.setbyte(RUN, 1)]
    wait1, go = hb._w(1), asm.nop()
    A, B, C, VMAX, DANGER = mv.A, mv.B, mv.C, mv.VMAX, mv.DANGER
    main += [tick, wait1, asm.if_word(FR, "<", NT, go), asm.goto_back(wait1), go, hb._arith(0x86, NT, mv.TICK),
             asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
             hb._arith(0x8A, VEL, 5), hb._arith(0x8C, VEL, 6),
             hb._arith(0x86, VEL, 1000 - 1000 * 5 // 6 - B - 500 // C),
             asm.setword(S, T), hb._arith(0x8A, S, A), hb._arith(0x86, VEL, S),
             asm.setword(S, POS), hb._arith(0x8C, S, C), hb._arith(0x86, VEL, S)]
    lo, hi = asm.nop(), asm.nop()
    main += [asm.if_word(VEL, "<", 1000 - VMAX, lo), asm.setword(VEL, 1000 - VMAX), lo,
             asm.if_word(VEL, ">", 1000 + VMAX, hi), asm.setword(VEL, 1000 + VMAX), hi,
             asm.setword(S, POS), hb._arith(0x86, S, VEL),
             asm.if_word(S, ">=", 1000 + DANGER, lost),
             asm.setword(POS, S), hb._arith(0x88, POS, 1000),
             asm.if_word(POS, "<=", 1000 - DANGER, hi_red)]
    no_call = asm.nop()
    main += [asm.if_byte(P, "==", len(POSITIONS) - 1, no_call), asm.if_byte(FIN, "==", 0, no_call),
             asm.setword(FT, FR), hb._arith(0x86, FT, mv.FINISH_FRAMES), asm.if_word(FT, ">=", NEXT, no_call),
             asm.setbyte(FIN, 1), hb._req(ents["shout"], 2, wait=False), no_call]
    # speed: insert (P 0) by the time, evenly over its minute (user); else by the press rate
    done, same, by_rate = asm.nop(), asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(S, T), hb._arith(0x8A, S, 16),
             hb._arith(0x86, RATE, S), asm.if_byte(P, "==", 0, by_rate),
             asm.setword(S, FR), hb._arith(0x86, S, SPECIAL_MINUTE), hb._arith(0x88, S, NEXT),     # frames into it
             hb._arith(0x8C, S, SPECIAL_MINUTE // 4), asm.setbyte(NEW, 3)]
    ramp = asm.nop()
    for s_ in range(3):
        nx = asm.nop()
        main += [asm.if_word(S, "==", s_, nx), asm.setbyte(NEW, s_), asm.goto(ramp), nx]
    main += [ramp, asm.goto(done), by_rate, asm.setbyte(NEW, 0)]
    for s_, th in enumerate(mv.RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s_ + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW)] + \
        [hb._req(e, 2, wait=False) for e in actors] + [same]
    main += pause
    stay = asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay),
             asm.if_byte(P, "<", len(POSITIONS) - 1, wrap),
             asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(mv.FAST_OUT), Op(b"\x6C"),
             Op(bytes([0x85, P[0] << 4, P[1], 1])), asm.setbyte(STEP, 0),
             asm.setword(POS, 500), asm.setword(VEL, 1000), asm.setword(RATE, 40)] + place_all() + \
            [hb._w(4), Op(mv.FAST_IN), Op(b"\x6C"), asm.setword(PR, 0), asm.setword(NT, FR),
             hb._arith(0x86, NT, mv.TICK), asm.setword(NEXT, FR), hb._arith(0x86, NEXT, SPECIAL_MINUTE)] + \
            mv._pause_arm(hb, SPECIAL_MINUTE) + [asm.setbyte(RUN, 1), stay, asm.goto_back(tick)]
    rx, ry, rz, rt, rdir = back

    def out():
        stop = hb._w(30)
        return [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir), stop,
                asm.goto_back(stop), asm.ret()]
    gil = rate * mv.FINISH_BONUS
    main += [hi_red, sound(mv.RED_SOUND), asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"),
             Op(b"\x54\x02"), Op(bytes([0xF2, 0, 0, 0, 0x10, mv.FANFARE]) + bytes(8)), hb._w(45)]
    main += say("“WOW! What a FINISHER!\n That's going straight on the poster!”")
    main += [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)]
    main += say("“Here's a bonus, on the spot:\n {:,} gil. You earned it, star!”".format(gil))
    main += hb._say(sec, SP.AFTERMATH[key])
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! You broke character, man!\n ...Fine. We'll sell what we've got.”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [walkout, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)] + say(mv.WALKED)
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! What a performance!”")
    main += hb._say(sec, SP.AFTERMATH[key])
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    director = names.index("directr")
    scripts[director] = {0: [black, asm.ret()] + main}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    return len(texts)


def _dates():
    from importlib import import_module
    return import_module("660_dates")


def apply(ctx):
    _BUILT["anims"] = poses(ctx)
    for key in SP.FIELDS:
        n = _special(ctx, key, ctx.movie_back)
        print("  672: %s's special set %s (%d voice lines)" % (key, SP.FIELDS[key], n))

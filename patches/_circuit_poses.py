"""(user: "the workout video scene ... needs a lot more variety") Sector 7 Workout's circuit stations (683): the poses
for the two new stations, built with the pose rig (`_besties_rig`) on the film's own models (Tifa's top-off
spandex / bare with tied hair, Cloud clothed / bare). Both actors of a station stand at one XYZI and DIR (the
station's anchor: Cloud's spot) with their offsets baked into their anims. One rep (down and up) an anim, a pair
per style and speed tier (`_workout.PERIODS` frames), as `_workout_poses`.

Model space as the game's (y down, an actor faces -z, +x its left); U field units a model unit.

press   The gym's weight bench (pad top BENCH_H): Tifa on her back along it, her head at the end where Cloud
        stands (his feet BENCH_START before it), facing along it. Style 0: her feet on the floor either side,
        she presses her hands up into his (a partner press: he leans over, palms on hers; his hips drift in
        with the pace). Style 1: her legs straight up in a V, her head tipped back over the bench's end looking
        up at him, pressing the same way; he leans in further.
stretch On the floor: Tifa on her back, her head away from Cloud, her right leg straight up on his left
        shoulder, the left out to the side; her hips lifted onto his thighs, shoulders on the floor. Cloud
        kneels, his left hand on her raised calf, his right on her hip; each rep he leans in (her leg pressed
        towards her chest) and his hips push in (the deeper, the higher the tier)."""
import math

from _besties_rig import (Rig, basis, bow, turn, lean, add, sub, mul, unit, lerp, kneel, stand_feet, hang_hair,
                          entry, hips_of, front)
import _workout as WO
import _workout_poses as WP

U = 3.41
# press
BENCH_H = 19 / U                # the weight bench's pad (its walkmesh bump peaks at z 19)
BENCH_START = 4.6               # the bench's end this far before Cloud's root
HEAD_IN = 0.5                   # her head's top this far onto the pad (style 0)
HEAD_OVER = 2.6                 # style 1: her neck this far nearer him (her head over the end)
BACK = 1.4                      # her back's depth behind her bones, resting on the pad / floor
PRESS_TOP, PRESS_LOW = 0.94, 0.62   # her hands' height above her shoulders, in arm lengths: arms straight / bent
PRESS_UP = 2.2                  # ...and this far up her body from her shoulders (over her face: in his reach)
PRESS_NARROW = 0.8              # her hands this share of her shoulders' width apart
FEET_OUT, FEET_DOWN = 4.6, 5.2  # style 0: her ankles beside the bench (out from her midline) and towards her feet
LEGS_V, LEGS_TILT = 18, 8       # style 1: each leg this far out of vertical, all tilted towards her head
HEAD_BACK = 55                  # style 1: her head tipped back (degrees)
PUSH = (0.5, 1.4)               # his hips drift in at the bottom of a rep: (slowest, fastest tier) model units
PUSH_1 = 0.8                    # style 1: further
BOW_MAX = 66                    # his bow at most (degrees): further and his head hid hers from the camera
# stretch
STRETCH_HIP_UP = 3.4            # her hips lifted this far (onto his thighs)
SHOULDER_UP = 0.9               # her shoulders' joints this far above the floor (her back on it)
LEFT_OUT = 48                   # her left leg out to the side (degrees from her body's line)
KNEE_SPREAD = 14                # his knees apart (degrees each)
TILT = (-2, -12)                # his thighs' tilt (kneel's: + = knees ahead of his hips): pulled back .. in
TILT_F = -8                     # (his hips forward) more in at the fastest tier
LEAN_IN = 14                    # his upper body leaning in (degrees) at the deepest
GAP = 0.5                       # his crotch this far from her entry at his deepest
ROCK = 0.35                     # her body pushed back this far as he pushes in


def _len(rg, *bones):
    return sum(rg.length[b] for b in bones)


# ---- press -------------------------------------------------------------------------------------------------
def _her_press(ctx, her, st, t, u):
    s, f = WP.squat(u), WP._f(t)
    rg = Rig(ctx, *her).start(basis((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)))     # on her back, head to +z, face up
    if st == 1:
        rg.neck(bow(-HEAD_BACK))
    E = rg.ends()
    top = E["head"][2] - rg.root[2]                                          # her head's top from her root
    head_z = -BENCH_START - HEAD_IN + (HEAD_OVER if st == 1 else 0.0)
    rg.root = [0.0, -(BENCH_H + BACK), head_z - top]
    E = rg.ends()
    # legs
    for sd, sx in (("l", 1), ("r", -1)):
        if st == 0:
            hip = E[sd + "_femur@"]
            ank = [sx * FEET_OUT, -0.7, hip[2] - FEET_DOWN]
            rg.ik(sd + "_femur", sd + "_tibia", ank, [0.0, -1.0, -0.6], keep_end=False)
            rg.aim(sd + "_foot", unit([0.0, 0.25, -1.0]))
        else:
            v, tl = math.radians(LEGS_V), math.radians(LEGS_TILT)
            d = unit([sx * math.sin(v), -math.cos(v) * math.cos(tl), math.sin(tl)])
            rg.aim(sd + "_femur", d)
            rg.aim(sd + "_tibia", d)
            rg.aim(sd + "_foot", unit([0.0, -0.6, -0.8]))
    # arms: hands up over her shoulders, elbows out
    E = rg.ends()
    La = _len(rg, "l_uparm", "l_foarm")
    hands = {}
    for sd, sx in (("l", 1), ("r", -1)):
        S = E[sd + "_uparm@"]
        h = La * (PRESS_TOP - (PRESS_TOP - PRESS_LOW) * s)
        hands[sd] = [S[0] * PRESS_NARROW, S[1] - h, S[2] + PRESS_UP]
        rg.ik(sd + "_uparm", sd + "_foarm", hands[sd], [sx * 1.0, 0.7, 0.0], keep_end=False)
        rg.aim(sd + "_hand", unit([0.0, -0.4, 1.0]))
    hang_hair(rg, along=[0.0, 0.6, 1.0] if st == 1 else [0.0, 0.0, 1.0])
    return rg, hands


def _his_press(ctx, him, st, t, u, hands):
    s, f = WP.squat(u), WP._f(t)
    base = Rig(ctx, *him).start(basis((1.0, 0.0, 0.0), (0.0, -1.0, 0.0)))
    E0 = base.ends()
    feet = {sd: E0[sd + "_tibia"] for sd in "lr"}
    push = (PUSH[0] + (PUSH[1] - PUSH[0]) * f + (PUSH_1 if st == 1 else 0.0)) * s
    Lc = _len(base, "l_uparm", "l_foarm")
    best = None
    for b in range(0, BOW_MAX + 1, 3):                          # the bow that puts his hands in easy reach of hers
        rg = Rig(ctx, *him).start(basis((1.0, 0.0, 0.0), (0.0, -1.0, 0.0)))
        rg.root = add(rg.root, [0.0, 0.0, -push])
        rg.waist(bow(b))
        E = rg.ends()
        err = sum(abs(math.dist(E[sd + "_uparm@"], hands[sd]) - 0.96 * Lc) for sd in "lr")
        if best is None or err < best[0]:
            best = (err, b)
    b = best[1]
    rg = Rig(ctx, *him).start(basis((1.0, 0.0, 0.0), (0.0, -1.0, 0.0)))
    rg.root = add(rg.root, [0.0, 0.0, -push])
    rg.waist(bow(b))
    rg.neck(bow(-b * 0.35 + 15))
    stand_feet(rg, feet)
    for sd, sx in (("l", 1), ("r", -1)):
        h = hands[sd]
        rg.ik(sd + "_uparm", sd + "_foarm", [h[0], h[1] - 0.7, h[2]], [sx * 1.0, 0.3, 0.6], keep_end=False)
        rg.aim(sd + "_hand", unit([0.0, 1.0, -0.4]))
    return rg


# ---- stretch -----------------------------------------------------------------------------------------------
def _his_stretch(ctx, him, t, u, knee_z):
    s, f = WP.squat(u), WP._f(t)
    tilt = TILT[0] + (TILT[1] - TILT[0] + TILT_F * f) * s
    rg = Rig(ctx, *him).start(basis((1.0, 0.0, 0.0), (0.0, -1.0, 0.0)))
    kneel(rg, tilt, KNEE_SPREAD, 0.0)
    E = rg.ends()
    k = lerp(E["l_femur"], E["r_femur"], 0.5)
    rg.root = add(rg.root, [-k[0], 0.0, knee_z - k[2]])
    rg.waist(bow(LEAN_IN * s))
    rg.neck(bow(18))
    return rg


def _crotch(rg, E=None):
    E = E or rg.ends()
    return add(hips_of(rg, E), mul(front(rg, "hip", E), 1.3))


def _her_stretch(ctx, her, t, u, push, ankle_at):
    rg = Rig(ctx, *her).start(basis((-1.0, 0.0, 0.0), (0.0, 0.0, -1.0)))     # on her back, head to -z
    E = rg.ends()
    tor = math.dist(E["hip@"], lerp(E["l_uparm@"], E["r_uparm@"], 0.5))
    a = math.degrees(math.asin(max(-0.9, min(0.9, (STRETCH_HIP_UP - SHOULDER_UP) / tor))))
    rg.pelvis(bow(-a))                                                        # hips up, shoulders down
    rg.root = [0.0, -(STRETCH_HIP_UP + BACK * 0.6), -ROCK * push]
    rg.neck(bow(a + 18))
    E = rg.ends()
    # her right leg (+x) to his left shoulder, the left out to the side on the floor
    rg.ik("r_femur", "r_tibia", ankle_at, [0.0, 0.0, -1.0], keep_end=False, reach=0.999)
    rg.aim("r_foot", unit([0.3, -1.0, 0.4]))
    o = math.radians(LEFT_OUT)
    hip = E["l_femur@"]
    lg = _len(rg, "l_femur", "l_tibia")
    rg.ik("l_femur", "l_tibia", [hip[0] - math.sin(o) * lg * 0.97, -0.7, hip[2] + math.cos(o) * lg * 0.97],
          [0.0, -1.0, 0.0], keep_end=False)
    rg.aim("l_foot", unit([0.0, -1.0, 0.3]))
    # arms out on the floor above her head
    for sd, sx in (("l", -1), ("r", 1)):
        rg.aim(sd + "_uparm", unit([sx * 0.75, 0.15, -0.65]))
        rg.aim(sd + "_foarm", unit([sx * 0.35, 0.1, -0.93]))
    hang_hair(rg, along=[0.0, 0.0, -1.0])
    return rg


def _stretch(ctx, her, him, t, u):
    """(her rig, his rig) for one frame: his knees placed so that at his deepest his crotch is GAP from her
    entry (solved once per tier, cached)."""
    key = ("knee", her, him, t)
    if key not in _CACHE:
        lo, hi = 0.0, 16.0
        for _ in range(30):                                     # bisect: further back = larger knee_z
            kz = (lo + hi) / 2
            rh = _his_stretch(ctx, him, t, 0.5, kz)
            rr = _her_stretch(ctx, her, t, 0.5, 1.0, _shoulder(rh))
            d = math.dist(_crotch(rh), entry(rr))
            # in front of her entry (z below it) means too close
            if _crotch(rh)[2] < entry(rr)[2] + GAP or d < GAP:
                lo = kz
            else:
                hi = kz
        _CACHE[key] = (lo + hi) / 2
    kz = _CACHE[key]
    rh = _his_stretch(ctx, him, t, u, kz)
    rr = _her_stretch(ctx, her, t, u, WP.squat(u), _shoulder(rh))
    # his hands: left on her raised calf, right on her left hip
    E, H = rr.ends(), rh.ends()
    calf = lerp(E["r_tibia@"], E["r_tibia"], 0.55)
    rh.ik("l_uparm", "l_foarm", add(calf, [0.6, -0.3, 0.3]), [1.0, 0.5, 0.5], keep_end=False)
    rh.ik("r_uparm", "r_foarm", add(E["l_femur@"], [-0.5, -1.0, 0.6]), [-1.0, 0.4, 0.4], keep_end=False)
    return rr, rh


def _shoulder(rh):
    E = rh.ends()
    return add(lerp(E["l_uparm@"], E["l_collar@"] if "l_collar@" in E else E["l_uparm@"], 0.4), [0.0, -0.6, 0.0])


_CACHE = {}


def build(ctx, her_top, her_bare, him_c, him_b, names):
    """her_top / her_bare / him_c / him_b = (.hrc, stand .a); names = {"press": (her prefix, his prefix),
    "stretch": (...)}. Writes press styles 0/1 (letters A / B) and stretch (A) for every tier; returns
    {("press", style): (hers, his), ("stretch", 0): (hers, his)} (anim names, one per tier)."""
    from _besties_rig import save
    out = {}
    for st in (0, 1):
        hp, cp = names["press"]
        hs, cs = [], []
        for t, n in enumerate(WO.PERIODS):
            fh, fc = [], []
            for k in range(n):
                rr, hands = _her_press(ctx, her_top, st, t, k / n)
                fh.append(rr.frame())
                fc.append(_his_press(ctx, him_c, st, t, k / n, hands).frame())
            L = "AB"[st]
            hs.append(save(ctx, "%s%s%d" % (hp, L, t), her_top[1], fh))
            cs.append(save(ctx, "%s%s%d" % (cp, L, t), him_c[1], fc))
        out[("press", st)] = (hs, cs)
    hp, cp = names["stretch"]
    hs, cs = [], []
    for t, n in enumerate(WO.PERIODS):
        fh, fc = [], []
        for k in range(n):
            rr, rh = _stretch(ctx, her_bare, him_b, t, k / n)
            fh.append(rr.frame())
            fc.append(rh.frame())
        hs.append(save(ctx, "%sA%d" % (hp, t), her_bare[1], fh))
        cs.append(save(ctx, "%sA%d" % (cp, t), him_b[1], fc))
    out[("stretch", 0)] = (hs, cs)
    return out

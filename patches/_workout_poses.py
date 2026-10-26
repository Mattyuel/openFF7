"""(user) Sector 7 Workout's poses (683_workout): Tifa squatting, Cloud behind her spotting, squatting with
her, his hands on her hips. One rep (down and up) per anim, a pair for each part (A clothed, B undressed) and
speed tier: the slow tiers keep a spotter's distance, the faster ones bring him closer, and part two bends
her over further with her hands on her knees while his hips push in at the bottom (user: "as the speed
increments, the position changes slightly, to be more overt").

(User, since) each part has its STYLES (variations the director alternates every few reps): part one
0 the spotted squat, 1 a wide sumo squat with her hands behind her head; part two 0 the bent-over squat,
1 Cloud cocking his left leg up (the camera's side) as he pushes, 2 her folded over touching her toes.
Hers: built on Ruby's skeleton as SRC<letter><tier> (letter by part and style, `LETTERS`: "QWA0".."QWE7") with `_dance_poses._Body`, retargeted
by 670 `_retarget` onto each of her models (prefixes from 683). His: built on Cloud's skeleton (AAAA; the
bare ZCLA has the same bones) frame by frame against hers: his drop = hers scaled to his height (+ HIP_BELOW at the bottom), his
hands on her hips (`_dance_poses` "at" targets) with him `gap` behind her. Both face -z in model space; in
the field he stands `gap` x UNIT behind her along her facing, same DIR."""
import math

import _dance_poses as DP
import _workout as WO

SRC, CLOUD = "QW", "QB"             # Ruby's source anims / Cloud's (QB<part><tier>)
CLOUD_HRC, CLOUD_STAND = "aaaa.hrc", "acfe.a"
HIP_BELOW = 0.3                     # at the bottom he sinks this much further than her drop scaled to his height
HAND_OUT, HAND_UP = 0.35, 0.9       # his hands: this far outside her hip joints, this far up (on her waist)
CLOUD_STANCE = 1.1                  # his feet this far further out to each side (his knees go round her)
STYLES = {"A": 2, "B": 3}           # (user: variations) styles per part
LETTERS = {("A", 0): "A", ("B", 0): "B", ("A", 1): "C", ("B", 1): "D", ("B", 2): "E"}
SUMO_STANCE = 1.7                   # A1: her feet this far further out
COCK_LEG = (2.4, 5.2, 1.4)          # B1: his left ankle moved (out, up, forward): knee up and out beside her hip
TOE_LEAN = 84                       # B2: her lean (degrees) folded over, hands hanging to her toes


def squat(u):
    """0 at the top, 1 at the bottom of a rep (u = 0 .. 1)."""
    return (1 - math.cos(2 * math.pi * u)) / 2


def _f(tier):
    """How far up the tiers (0 .. 1)."""
    return tier / max(1, len(WO.PERIODS) - 1)


def gap(part, tier, style=0):
    """How far behind her he stands (model units, root to root)."""
    f = _f(tier)
    if part == "A":
        return 8.0 - 2.4 * f
    return (4.8 - 1.2 * f) + (0.6 if style == 2 else 0.0)            # (folded over: her hips further back)


def push(part, tier, u):
    """(user: more back and forth in the overt ones) his hips pushing in: part two from the start, harder and
    twice a rep at the faster tiers; part one only from the 'training device' tiers (f >= 0.7), once."""
    f = _f(tier)
    if part == "A":
        return 0.0 if f < 0.7 else (0.3 + 0.5 * (f - 0.7) / 0.3) * squat(u) ** 3
    k = 1 if f < 0.4 else 2
    return (0.45 + 0.9 * f) * (0.5 - 0.5 * math.cos(2 * math.pi * k * u))


def her_pose(part, tier, u, style=0):
    s, f = squat(u), _f(tier)
    rock = 0.45 * push(part, tier, u)                                   # she rocks forward as he pushes in
    if part == "A" and style == 1:                                      # sumo, hands behind her head
        lean = 6 + 10 * s
        arm = lambda: (165, -40, 0.42, (1.0, -0.6, 0.3))
        return dict(drop=(3.9 + 0.6 * f) * s, shift=(0, -0.4 * s + rock), lean=(lean, 0, 0), head=(-lean * 0.5, 0, 0),
                    leg_l=(SUMO_STANCE, 0, 0.3), leg_r=(SUMO_STANCE, 0, 0.3), arm_l=arm(), arm_r=arm())
    if part == "B" and style == 2:                                      # folded over, touching her toes
        lean = TOE_LEAN + 8 * f + 8 * s
        arm = (6, lean, 1.0)
        return dict(drop=(1.2 + 0.4 * f) * s, shift=(0, -0.5 * s + rock), lean=(lean, 0, 0), head=(-lean * 0.6, 0, 0),
                    leg_l=(0.7, 0, 0), leg_r=(0.7, 0, 0), arm_l=arm, arm_r=arm)
    if part == "A":
        lean = 12 + (16 + 10 * f) * s
        return dict(drop=(3.4 + 0.6 * f) * s, shift=(0, -0.7 * s + rock), lean=(lean, 0, 0), head=(-lean * 0.6, 0, 0),
                    leg_l=(0.5, 0, 0), leg_r=(0.5, 0, 0), arm_l=(78 + 8 * s, 88, 0.95), arm_r=(78 + 8 * s, 88, 0.95))
    lean = 26 + 25 * f + 14 * s
    arms = "knee" if f >= 0.3 else (55, 75, 0.85)
    return dict(drop=(3.2 + 0.5 * f) * s, shift=(0, -0.9 * s + rock), lean=(lean, 0, 0), head=(-lean * 0.7, 0, 0),
                leg_l=(0.6, 0, 0), leg_r=(0.6, 0, 0), arm_l=arms, arm_r=arms)


def _her_joints(fa, sk, anim, k):
    rr, rp, rots = anim.frames[k]
    F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
    out = {b[0]: e for b, (_, s, e) in zip(sk, F)}
    out.update({b[0] + "@": s for b, (_, s, e) in zip(sk, F)})
    out["root"] = [rp[0], -rp[1], rp[2]]
    return out


def build(ctx, hers):
    """hers = {part: (her .hrc, her stand anim, her prefix)}: builds Ruby's sources for every style,
    retargets part A's onto hers["A"] and part B's onto hers["B"], then Cloud's to match. Returns
    {(part, style): (her names, his names)} (one per tier)."""
    from ff7 import fieldanim as fa
    mv, _, CP = DP._mods()
    body = DP._Body(ctx)
    combos = [(part, st) for part in "AB" for st in range(STYLES[part])]
    for part, st in combos:
        for t, n in enumerate(WO.PERIODS):
            frames = [body.frame(her_pose(part, t, k / n, st)) for k in range(n)]
            CP._save(ctx, "%s%s%d" % (SRC, LETTERS[(part, st)], t), mv.RUBY_STAND, frames)
    him = DP._Body(ctx, CLOUD_HRC, CLOUD_STAND)
    out = {}
    for part, st in combos:
        hrc, stand, prefix = hers[part]
        L = LETTERS[(part, st)]
        names = mv._retarget(ctx, ["%s%s%d.tor" % (SRC, L, t) for t in range(len(WO.PERIODS))], prefix, hrc, stand)
        sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
        top = -fa.Anim(ctx.char_file(stand)).frames[0][1][1]               # her stand's root height (y down)
        ratio = him.root0[1] / top                                          # his height over hers
        his = []
        for t, n in enumerate(WO.PERIODS):
            A = fa.Anim(ctx.char_file(names[t].split(".")[0].lower() + ".a"))
            g = gap(part, t, st)
            frames = []
            for k in range(n):
                J = _her_joints(fa, sk, A, k)
                s = squat(k / n)
                to_his = lambda p: [p[0], p[1], p[2] - g]          # her model space -> his (he's g behind: +z)
                drop = (J["root"][1] - top) * ratio + HIP_BELOW * s       # her drop, scaled to his height
                lean = (0.45 if part == "A" else 0.5) * her_pose(part, t, k / n, st)["lean"][0]
                push_ = push(part, t, k / n)                                    # his hips in
                hands = {}
                for side, sg in (("l", 1), ("r", -1)):
                    h = J[side + "_femur@"]
                    hands["arm_" + side] = ("at", to_his([h[0] + sg * HAND_OUT, h[1] - HAND_UP, h[2]]),
                                            (sg * 1.0, 0.6, -0.2))
                stance = CLOUD_STANCE + (SUMO_STANCE * 0.6 if (part, st) == ("A", 1) else 0.0)
                leg_l = (stance, 0, 0)
                if (part, st) == ("B", 1):                              # (user) Cloud cocks a leg up
                    leg_l = (stance + COCK_LEG[0], COCK_LEG[1], COCK_LEG[2])
                frames.append(him.frame(dict(drop=drop, lean=(lean, 0, 0), head=(-lean * 0.8, 0, 0),
                                             shift=(0, push_), leg_l=leg_l, leg_r=(stance, 0, 0),
                                             **hands)))
            name = "%s%s%d" % (CLOUD, L, t)
            CP._save(ctx, name, CLOUD_STAND, frames)
            his.append(name + ".tor")
        out[(part, st)] = (names, his)
    return out

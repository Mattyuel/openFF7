"""(user) Sector 7 Workout's poses (683_workout): Tifa squatting, Cloud behind her spotting, squatting with
her, his hands on her hips. One rep (down and up) per anim, a pair for each part (A clothed, B undressed) and
speed tier: the slow tiers keep a spotter's distance, the faster ones bring him closer, and part two bends
her over further with her hands on her knees while his hips push in at the bottom (user: "as the speed
increments, the position changes slightly, to be more overt").

Hers: built on Ruby's skeleton as SRC<part><tier> ("QWA0".."QWB5") with `_dance_poses._Body`, retargeted
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


def squat(u):
    """0 at the top, 1 at the bottom of a rep (u = 0 .. 1)."""
    return (1 - math.cos(2 * math.pi * u)) / 2


def gap(part, tier):
    """How far behind her he stands (model units, root to root)."""
    return 8.0 - 0.45 * tier if part == "A" else 4.8 - 0.22 * tier


def her_pose(part, tier, u):
    s = squat(u)
    if part == "A":
        lean = 12 + (16 + 2 * tier) * s
        return dict(drop=(3.4 + 0.12 * tier) * s, shift=(0, -0.7 * s), lean=(lean, 0, 0), head=(-lean * 0.6, 0, 0),
                    leg_l=(0.5, 0, 0), leg_r=(0.5, 0, 0), arm_l=(78 + 8 * s, 88, 0.95), arm_r=(78 + 8 * s, 88, 0.95))
    lean = 26 + 5 * tier + 14 * s
    arms = "knee" if tier >= 2 else (55, 75, 0.85)
    return dict(drop=(3.2 + 0.1 * tier) * s, shift=(0, -0.9 * s), lean=(lean, 0, 0), head=(-lean * 0.7, 0, 0),
                leg_l=(0.6, 0, 0), leg_r=(0.6, 0, 0), arm_l=arms, arm_r=arms)


def _her_joints(fa, sk, anim, k):
    rr, rp, rots = anim.frames[k]
    F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
    out = {b[0]: e for b, (_, s, e) in zip(sk, F)}
    out.update({b[0] + "@": s for b, (_, s, e) in zip(sk, F)})
    out["root"] = [rp[0], -rp[1], rp[2]]
    return out


def build(ctx, hers):
    """hers = {part: (her .hrc, her stand anim, her prefix)}: builds Ruby's sources, retargets part A onto
    hers["A"] and part B onto hers["B"], then Cloud's to match. Returns {part: (her names, his names)}."""
    from ff7 import fieldanim as fa
    mv, _, CP = DP._mods()
    body = DP._Body(ctx)
    for part in "AB":
        for t, n in enumerate(WO.PERIODS):
            frames = [body.frame(her_pose(part, t, k / n)) for k in range(n)]
            CP._save(ctx, "%s%s%d" % (SRC, part, t), mv.RUBY_STAND, frames)
    him = DP._Body(ctx, CLOUD_HRC, CLOUD_STAND)
    out = {}
    for part in "AB":
        hrc, stand, prefix = hers[part]
        names = mv._retarget(ctx, ["%s%s%d.tor" % (SRC, part, t) for t in range(len(WO.PERIODS))], prefix, hrc, stand)
        sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
        top = -fa.Anim(ctx.char_file(stand)).frames[0][1][1]               # her stand's root height (y down)
        ratio = him.root0[1] / top                                          # his height over hers
        his = []
        for t, n in enumerate(WO.PERIODS):
            A = fa.Anim(ctx.char_file(names[t].split(".")[0].lower() + ".a"))
            g = gap(part, t)
            frames = []
            for k in range(n):
                J = _her_joints(fa, sk, A, k)
                s = squat(k / n)
                to_his = lambda p: [p[0], p[1], p[2] - g]          # her model space -> his (he's g behind: +z)
                drop = (J["root"][1] - top) * ratio + HIP_BELOW * s       # her drop, scaled to his height
                lean = (0.45 if part == "A" else 0.5) * her_pose(part, t, k / n)["lean"][0]
                push = 0.0 if part == "A" else (0.35 + 0.1 * t) * s ** 3       # his hips in at the bottom
                hands = {}
                for side, sg in (("l", 1), ("r", -1)):
                    h = J[side + "_femur@"]
                    hands["arm_" + side] = ("at", to_his([h[0] + sg * HAND_OUT, h[1] - HAND_UP, h[2]]),
                                            (sg * 1.0, 0.6, -0.2))
                frames.append(him.frame(dict(drop=drop, lean=(lean, 0, 0), head=(-lean * 0.8, 0, 0),
                                             shift=(0, push), leg_l=(CLOUD_STANCE, 0, 0), leg_r=(CLOUD_STANCE, 0, 0),
                                             **hands)))
            name = "%s%s%d" % (CLOUD, part, t)
            CP._save(ctx, name, CLOUD_STAND, frames)
            his.append(name + ".tor")
        out[part] = (names, his)
    return out

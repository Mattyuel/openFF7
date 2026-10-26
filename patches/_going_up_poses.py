"""(user) Going up's own poses (684_going_up): Elena covering up (standing, head down and turned aside, one
arm across her chest, the other hand in front of her hips: built on Ruby as SRC + "A0" by `_dance_poses`
and retargeted onto her bare model), and her still on all fours (frame 0 of her movie dog stroke ZYC0) for
the crawl's stops and while Cloud is with Tifa. The rest are the movie's per-girl poses (670): Elena's dog
ZYC0-3 with Cloud's ZNC0-3 behind her, Tifa's head ZVJ0-3 (ZVJ9 her kneeling still) with Cloud's ZNJ0-3."""
import math

import _dance_poses as DP

SRC = "QX"                      # Ruby's source: QXA0 (covering up)
PREFIX = "QE"                   # on Elena: QEA0 covering, QEB0 still on all fours
COVER_TURN = 30                 # her head turned aside (degrees)


def build(ctx, hrc, stand):
    """Writes QEA0 / QEB0 for Elena's bare `hrc`. Returns their names (.tor)."""
    from ff7 import fieldanim as fa
    mv, _, CP = DP._mods()
    body = DP._Body(ctx)
    e = body.e0
    mid = [(e["l_uparm@"][k] + e["r_uparm@"][k]) / 2 for k in range(3)]
    chest = [mid[0] + 0.6, mid[1] + 2.4, mid[2] - 1.4]                     # (y down, -z forward) her left breast
    hips = [body.root0[0], body.root0[1] + 1.6, body.root0[2] - 1.3]          # in front of her hips
    pose = dict(lean=(10, 0, 0), head=(28, 0, COVER_TURN), drop=0.3,
                arm_r=("at", chest, (-1.0, 0.6, 0.6)), arm_l=("at", hips, (1.0, 0.2, 0.6)))
    CP._save(ctx, SRC + "A0", mv.RUBY_STAND, [body.frame(pose)])
    names = mv._retarget(ctx, [SRC + "A0.tor"], PREFIX, hrc, stand)
    A = fa.Anim(ctx.char_file("zyc0.a"))
    A.frames = A.frames[:1]
    ctx.char_file((PREFIX + "B0").lower() + ".a", A.build())
    return names + [PREFIX + "B0.tor"]


# ---- (user: variations) Cloud's alternative poses, built from the movie's per-frame ones -----------------
VARIANT = "QK"                  # QKC0-3: dog with his legs swapped (his left knee up: the camera's side);
                                # QKJ0-3: head with his hands behind his head (look, no hands)
NAPE = (1.15, -1.5, 1.2)        # his hands: from the neck joint this far (out, up (y down), back (+z))


def _mirror_legs(fa, sk, W):
    """Each leg's world rotations taken from the other leg, mirrored in x."""
    I = [b[0] for b in sk].index
    S = [[-1, 0, 0], [0, 1, 0], [0, 0, 1]]
    m = lambda M: fa._mul(fa._mul(S, M), S)
    out = list(W)
    for b in sk:
        if b[0].startswith("l_") and ("femur" in b[0] or "tibia" in b[0] or "foot" in b[0] or "toe" in b[0]):
            r = "r_" + b[0][2:]
            out[I(b[0])], out[I(r)] = m(W[I(r)]), m(W[I(b[0])])
    return out


def build_cloud(ctx):
    """QKC0-3 / QKJ0-3 from ZNC0-3 / ZNJ0-3 (Cloud's skeleton). Returns their names (.tor)."""
    from ff7 import fieldanim as fa
    mv, _, CP = DP._mods()
    sp = DP._mods()[1]
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    I = [b[0] for b in sk].index
    # (the skeleton is symmetric: mirroring the stand's legs puts its knees and ankles back; its feet
    # aren't quite)
    rr, rp, rots = fa.Anim(ctx.char_file("acfe.a")).frames[0]
    W0 = [M for M, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
    M0 = _mirror_legs(fa, sk, W0)
    root0 = [rp[0], -rp[1], rp[2]]
    F0, F1 = fa.forward(sk, rr, root0, rots), fa.forward(sk, rr, root0, fa.local_rotations(sk, rr, M0))
    assert all(math.dist(F0[I(b)][2], F1[I(b)][2]) < 1e-3 for b in ("l_femur", "l_tibia", "r_femur", "r_tibia"))
    names = []
    for s in range(4):
        src = "znc%d.a" % s
        frames = []
        for rr, rp, rots in fa.Anim(ctx.char_file(src)).frames:
            root = [rp[0], -rp[1], rp[2]]
            W = _mirror_legs(fa, sk, [M for M, _, _ in fa.forward(sk, rr, root, rots)])
            frames.append(CP._frame(fa, sk, rr, root, W))
        CP._save(ctx, "%sC%d" % (VARIANT, s), src, frames)
        names.append("%sC%d.tor" % (VARIANT, s))
    for s in range(4):
        src = "znj%d.a" % s
        frames = []
        for rr, rp, rots in fa.Anim(ctx.char_file(src)).frames:
            root = [rp[0], -rp[1], rp[2]]
            F = fa.forward(sk, rr, root, rots)
            W = [M for M, _, _ in F]
            neck = F[I("head")][1]
            for side, sg in (("l", 1), ("r", -1)):
                F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
                S_ = F[I(side + "_uparm")][1]
                L1, L2 = (math.dist(*F[I(side + "_uparm")][1:]), math.dist(*F[I(side + "_foarm")][1:]))
                T = [neck[0] + sg * NAPE[0], neck[1] + NAPE[1], neck[2] + NAPE[2]]
                d = math.dist(S_, T)
                if d > (L1 + L2) * 0.985:
                    T = [S_[k] + (T[k] - S_[k]) * (L1 + L2) * 0.985 / d for k in range(3)]
                if d < abs(L1 - L2) + 0.3:
                    T = [S_[k] + (T[k] - S_[k]) * (abs(L1 - L2) + 0.3) / max(d, 1e-6) for k in range(3)]
                old_fo, hand = W[I(side + "_foarm")], W[I(side + "_hand")]
                W = sp._two_bone(fa, W, I, F, side + "_uparm", side + "_foarm", T, [sg * 1.5, -1.0, 0.6])
                W[I(side + "_hand")] = fa._mul(fa._mul(W[I(side + "_foarm")], DP._t(old_fo)), hand)
            frames.append(CP._frame(fa, sk, rr, root, W))
        CP._save(ctx, "%sJ%d" % (VARIANT, s), src, frames)
        names.append("%sJ%d.tor" % (VARIANT, s))
    return names

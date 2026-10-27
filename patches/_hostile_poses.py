"""(user) Hostile Takeover's poses (686_hostile), after the user's annotated sketch: one girl face down along the
boardroom table on her knees, chest down (670's dog strokes), her rear at its edge; Cloud standing on the floor
bowing into her, his face buried "there" (user), hands on her hips, his pelvis tilted so his member points
down and forward to the other girl, kneeling behind him, leaning in between his legs, face up to him, her head
bobbing.

All three are drawn at entry scale SCALE (768: the table's top is at Cloud's hip then; at 512 it was at his
chin), so model units are mv.UNIT x SCALE / 512 field units here.

The girl underneath ("under"): on Ruby (QHU<speed>, then held deep QHU8, tapping out QHU7: her head shaking),
retargeted per girl (670 `_retarget`). Cloud's (`cloud`): `_dance_poses._Body` frames on his skeleton with his
face solved onto her entry point frame by frame, then his pelvis turned PELVIS_TILT about its top. 686 works out
the spots: the girl on the table by her entry at the table's edge, Cloud from his face's mean, the girl
underneath from his member's tip (her mouth on it)."""
import math

import _dance_poses as DP

SCALE = 768
LEAN, PELVIS_TILT = 42, 80          # Cloud: upper body leant forward into her (degrees); pelvis turned (member down)
HEAD_DOWN = 24                      # ... his head bowed
FACE_T, FACE_OUT = 0.35, 1.0        # his face: this far up his head bone, this far out in front
STANCE = 3.2                        # his feet this far out (she lies between them)
FACE_IN = 0.4                       # (user: "buried") his face this far into her, past her entry point
HANDS_OUT = 3.4                     # style 1: his hands flat on the table this far either side
UNDER_PROP = 35                     # her torso this far up from lying flat (686 solves it per girl)
UNDER_HEAD = 20                     # her head tipped back (face up at him)
UNDER_SIT, UNDER_SPREAD = 82, 22    # (user: kneeling, leaning back) her thighs forward of straight down / apart
UNDER_HANDS = (2.4, 1.8)            # her hands on the floor this far behind her hips / either side
UNDER_BOB, UNDER_NOD = 7, 10        # her bob: the upper body's pitch / her head's nod each way (degrees)
MOUTH_T, MOUTH_OUT = 0.3, 0.9       # her mouth: up her head bone, out towards her face
SHAKE_DEG, SHAKE_N, TRY_FRAMES = 24, 8, 90
SPEEDS = (20, 15, 11, 8)            # 670's


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("672_movie_special"), import_module("_chamber_poses")


def unit():
    mv = _mods()[0]
    return mv.UNIT * SCALE / 512


def _subtree(sk, top):
    names = [b[0] for b in sk]
    out, todo = set(), [top]
    while todo:
        n = todo.pop()
        out.add(names.index(n))
        todo += [b[0] for b in sk if b[1] == n]
    return out


def under(ctx, prop=None, probe=False):
    """QHU0-3 / QHU8 / QHU7 on Ruby, (user: "she should be kneeling but leaning back") kneeling under him facing
    away from the table, sitting back towards her heels (`UNDER_SIT`), arched back about her waist until her
    torso is `prop` degrees up from lying flat, hands planted on the floor behind her, her face up at him (686
    bisects `prop` so her mouth is at his tip: more upright = higher); bobbing (the arch and her head's nod) with
    each stroke, highest at 7/15; QHU7 her head shaking (tapping out). Returns the names. (Was on her back,
    propped up: 620 `_on_back`.)"""
    import _besties_rig as RG
    mv, sp, CP = _mods()
    prop = UNDER_PROP if prop is None else prop

    def frame(pitch, nod, shake=0.0):
        rg = RG.Rig(ctx, mv.RUBY_HRC, mv.RUBY_STAND).start(RG.turn(0))
        back = 90 - pitch                                   # degrees back from upright
        rg.pelvis(RG.bow(-back * 0.45))
        rg.waist(RG.bow(-back * 0.55))
        rg.neck(RG.chain(RG.turn(shake), RG.bow(-UNDER_HEAD + nod)))
        RG.kneel(rg, UNDER_SIT, UNDER_SPREAD, -0.45)
        E_ = rg.ends()
        bk = RG.fa._vec(rg.G, [0.0, 0.0, 1.0])            # behind her
        for s_, sx in (("l", 1), ("r", -1)):
            hand = RG.add(RG.add(E_["hip@"], RG.mul(bk, UNDER_HANDS[0])), [sx * UNDER_HANDS[1], 0.0, 0.0])
            hand[1] = -0.3                                  # (y down) on the floor
            rg.ik(s_ + "_uparm", s_ + "_foarm", hand, [sx * 1.0, 0.0, 0.6])
        RG.hang_hair(rg, 0.2)
        return rg.frame()
    deep = 7 / 15
    wave = lambda u: math.cos(2 * math.pi * (u - deep))                     # 1 at the deepest
    names = []
    if probe:                                                           # (686's search: the held frame only)
        CP._save(ctx, "QHUP", mv.RUBY_STAND, [frame(prop + UNDER_BOB, UNDER_NOD)])
        return ["QHUP.tor"]
    for s_, n in enumerate(SPEEDS):
        frames = [frame(prop + UNDER_BOB * wave(k / n), UNDER_NOD * wave(k / n)) for k in range(n)]
        CP._save(ctx, "QHU%d" % s_, mv.RUBY_STAND, frames)
        names.append("QHU%d.tor" % s_)
    CP._save(ctx, "QHU8", mv.RUBY_STAND, [frame(prop + UNDER_BOB, UNDER_NOD)])
    names.append("QHU8.tor")
    CP._save(ctx, "QHU7", mv.RUBY_STAND,
             [frame(prop + UNDER_BOB, UNDER_NOD, SHAKE_DEG * math.sin(2 * math.pi * SHAKE_N * t / TRY_FRAMES))
              for t in range(TRY_FRAMES)])
    names.append("QHU7.tor")
    return names


def joints(ctx, hrc, anim):
    """Per frame: {bone: end, bone@: start, bone#: world matrix, root} (model space, y down)."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    out = []
    for rr, rp, rots in fa.Anim(ctx.char_file(anim.lower() + ".a")).frames:
        root = [rp[0], -rp[1], rp[2]]
        F = fa.forward(sk, rr, root, rots)
        J = {b[0]: e for b, (_, s, e) in zip(sk, F)}
        J.update({b[0] + "@": s for b, (_, s, e) in zip(sk, F)})
        J.update({b[0] + "#": m for b, (m, s, e) in zip(sk, F)})
        J["root"] = root
        out.append(J)
    return out


def mouth(ctx, hrc, stand, J):
    from ff7 import fieldanim as fa
    m0 = joints(ctx, hrc, stand.split(".")[0])[0]["head#"]
    front = fa._vec(fa._t(m0), [0.0, 0.0, -1.0])
    S, E = J["head@"], J["head"]
    f = fa._vec(J["head#"], front)
    return [S[k] + (E[k] - S[k]) * MOUTH_T + f[k] * MOUTH_OUT for k in range(3)]


def _bow(ctx):
    """(him, face-point function, the bowing pose's dict)."""
    from ff7 import fieldanim as fa
    him = DP._Body(ctx, "aaaa.hrc", "acfe.a")
    I = [b[0] for b in him.sk].index
    m_head0 = fa.forward(him.sk, him.rr, him.root0, fa.local_rotations(him.sk, him.rr, him.W0))[I("head")][0]
    front = fa._vec(fa._t(m_head0), [0.0, 0.0, -1.0])

    def face(F):
        S, E = F[I("head")][1], F[I("head")][2]
        f = fa._vec(F[I("head")][0], front)
        return [S[k] + (E[k] - S[k]) * FACE_T + f[k] * FACE_OUT for k in range(3)]
    base = dict(lean=(LEAN, 0, 0), head=(HEAD_DOWN, 0, 0), leg_l=(STANCE, 0, 0), leg_r=(STANCE, 0, 0))
    return him, face, base


def face_point(ctx):
    """Cloud's face bowing (no drop / shift), model space: where his root has to move from to put it anywhere."""
    from ff7 import fieldanim as fa
    him, face, base = _bow(ctx)
    rr, rp, rots = him.frame(base)
    return face(fa.forward(him.sk, rr, [rp[0], -rp[1], rp[2]], rots))


def cloud(ctx, name, faces, hands, deep=7 / 15):
    """Cloud bowing into her (user: his face buried "there" in her): frames written to name.a, one per target in
    faces (model space, his origin on the floor, he faces -z): his upper body leant LEAN forward, head HEAD_DOWN,
    his root moved (drop / shift, feet planted) so his face is at the target, then his pelvis turned PELVIS_TILT
    about its top (his member points down and forward, to the girl behind him); hands = per frame (left, right)
    model points. Returns (his member's tip per frame (model space), the drops)."""
    from ff7 import fieldanim as fa
    mv, sp, CP = _mods()
    hb = __import__("importlib").import_module("620_honey_bee")
    him, face, base = _bow(ctx)
    I = [b[0] for b in him.sk].index
    _, tip_local = hb.member_ends(ctx.char_file("zcmp.p"))
    x = [1.0, 0.0, 0.0]
    face0 = face_point(ctx)
    W = list(him.W0)

    def tip(W, root):
        F = fa.forward(him.sk, him.rr, root, fa.local_rotations(him.sk, him.rr, W))
        return [F[I("hip")][1][k] + fa._vec(W[I("hip")], list(tip_local))[k] for k in range(3)]
    def turned(sg):
        W2 = list(him.W0)
        W2[I("hip")] = fa._mul(fa.axis_angle(x, sg * 30), W2[I("hip")])
        return tip(W2, him.root0)[1]
    sg = 1 if turned(1) > turned(-1) else -1                                # (y down: larger = lower)
    frames, tips, drops = [], [], []
    for k, t in enumerate(faces):
        d = [t[q] - face0[q] for q in range(3)]
        drops.append(d[1])
        P = dict(base, drop=max(0.0, d[1]), jump=max(0.0, -d[1]), shift=(d[0], -d[2]))
        if hands:
            P["arm_l"] = ("at", list(hands[k][0]), (1.0, 0.2, 0.6))
            P["arm_r"] = ("at", list(hands[k][1]), (-1.0, 0.2, 0.6))
        rr, rp, rots = him.frame(P)
        root = [rp[0], -rp[1], rp[2]]
        F = fa.forward(him.sk, rr, root, rots)
        W = [m for m, _, _ in F]
        Pp = F[I("hip")][2]                                                 # (the pelvis turns about its top)
        R = fa.axis_angle(x, sg * PELVIS_TILT)
        W[I("hip")] = fa._mul(R, W[I("hip")])
        rel = fa._vec(R, [root[q] - Pp[q] for q in range(3)])
        root = [Pp[q] + rel[q] for q in range(3)]
        frames.append(CP._frame(fa, him.sk, rr, root, W))
        tips.append(tip(W, root))
    CP._save(ctx, name, "acfe.a", frames)
    return tips, drops

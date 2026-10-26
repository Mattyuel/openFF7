"""(user) Tickets, please!'s poses (685_tickets).

Hers come from the movie (670): Tifa's dog strokes ZVC0-3 as they are (on all fours; her model on the seat),
and for Jessie the head reverse (Ruby's ZME0-3, the held-deep ZME8, her tap-out squirm ZME7, the pulled-back
ZME9) with her legs straight up the window (`legs_up`: each leg turned rigidly to point straight up, LEGS_SPREAD
apart, the knee straightened), as QYE.. on Ruby and retargeted onto her undressed model (670 `_retarget`,
prefix QJ). The intro's sitting poses: 660 `_ledge` on each clothed model.

Cloud's are solved against hers frame by frame (`solve` / `cloud`): his member's tip (620 `member_ends` of
zcmp.p, on the hip bone) at her point (Tifa: her entry, 672's ENTRY scaled to her; Jessie: her mouth) plus
the stroke along the line from her to him (DEPTH inside at her deepest frame, STROKE out), his root moved
there by `_dance_poses._Body` (drop / shift, feet planted, his stance), hands by "at" targets (on Tifa's hips;
on Jessie's shoulders; style 1 behind his head) or his left foot up on the seat (style 1 behind Tifa).
Everything is placed in field space (670 `_off`) so his spot comes out of the solve (`spot`)."""
import math

import _dance_poses as DP
import _tickets as TK

RUBY_LETTER = "E"               # 670's head reverse (POSITIONS index 4)
NAPE = (1.15, -1.5, 1.2)        # style 1 at Jessie's head: his hands this far from his neck (out, up, back)
MOUTH_T, MOUTH_OUT = 0.3, 0.9   # her mouth: this far up her head bone, this far out towards her face
TIPTOE = 0.6                    # at most this far up on his toes (model units) if a point is too high


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("620_honey_bee"), import_module("660_dates")


def legs_up(ctx, src, dst):
    """Ruby's anim src (on her back) with both legs straight up, written to dst."""
    from ff7 import fieldanim as fa
    mv, _, _ = _mods()
    sk = fa.skeleton(ctx.char_file(mv.RUBY_HRC).decode("latin-1"))
    I = [b[0] for b in sk].index
    A = fa.Anim(ctx.char_file(src.lower() + ".a"))
    bdir = lambda m: fa._vec(m, [0.0, 0.0, -1.0])
    frames = []
    for rr, rp, rots in A.frames:
        root = [rp[0], -rp[1], rp[2]]
        F = fa.forward(sk, rr, root, rots)
        W = [m for m, _, _ in F]
        side = [F[I("l_femur")][1][k] - F[I("r_femur")][1][k] for k in range(3)]
        side[1] = 0.0
        n = math.hypot(*side)
        side = [c / n for c in side]
        a = math.radians(TK.LEGS_SPREAD)
        for s, sg in (("l", 1), ("r", -1)):
            up = [sg * math.sin(a) * side[0], -math.cos(a), sg * math.sin(a) * side[2]]      # (y down)
            R = mv._align(fa, bdir(W[I(s + "_femur")]), up)
            for b in ("_femur", "_tibia", "_foot"):
                W[I(s + b)] = fa._mul(R, W[I(s + b)])
            R = mv._align(fa, bdir(W[I(s + "_tibia")]), up)                                # the knee straight
            for b in ("_tibia", "_foot"):
                W[I(s + b)] = fa._mul(R, W[I(s + b)])
        frames.append((rr, rp, fa.local_rotations(sk, rr, W)))
    A.frames = frames
    ctx.char_file(dst.lower() + ".a", A.build())


def jessie(ctx, hrc, stand):
    """Jessie's poses on her undressed `hrc`: QJE0-3 strokes, QJE8 held deep, QJE7 her tap-out squirm, QJE9
    pulled back (still). Returns their names (.tor) in that order."""
    mv, _, _ = _mods()
    srcs = []
    for d in "0123879":
        legs_up(ctx, "ZM" + RUBY_LETTER + d, "QY" + RUBY_LETTER + d)
        srcs.append("QY%s%s.tor" % (RUBY_LETTER, d))
    names = mv._retarget(ctx, srcs, "QJ", hrc, stand)
    # (her root is out by her feet: past the window wall, off the walkmesh) every anim's root moved so the
    # model's origin is under her hips (QJE0's mean)
    from ff7 import fieldanim as fa
    J = joints(ctx, hrc, names[0].split(".")[0])
    cx, cz = (sum(j["hip@"][k] for j in J) / len(J) for k in (0, 2))
    for nm in names:
        A = fa.Anim(ctx.char_file(nm.split(".")[0].lower() + ".a"))
        A.frames = [(rr, [rp[0] - cx, rp[1], rp[2] - cz], rots) for rr, rp, rots in A.frames]
        ctx.char_file(nm.split(".")[0].lower() + ".a", A.build())
    return names


def sitting(ctx, name, hrc, stand):
    """name.a: sitting on the bench's edge (660 `_ledge`): XYZI on the seat."""
    _, _, dt = _mods()
    dt._ledge(ctx, name + ".tor", hrc.lower(), stand)
    return name + ".tor"


def still(ctx, src, dst, frame=0):
    """dst.a = src.a's one frame."""
    from ff7 import fieldanim as fa
    A = fa.Anim(ctx.char_file(src.lower() + ".a"))
    A.frames = A.frames[frame:frame + 1]
    ctx.char_file(dst.lower() + ".a", A.build())
    return dst + ".tor"


# ---- placing in field space -------------------------------------------------------------------------------
def _inv_off(v, d):
    """Model vector (y down) of field vector v for an entity with DIR d (670 `_off` inverted)."""
    mv, _, _ = _mods()
    a = d * 2 * math.pi / 256
    F0, F1 = math.sin(a), -math.cos(a)
    return [(-F1 * v[0] + F0 * v[1]) / mv.UNIT, -v[2] / mv.UNIT, (-F1 * v[1] - F0 * v[0]) / mv.UNIT]


def _field(spot, d, p):
    mv, _, _ = _mods()
    o = mv._off(p, d)
    return [spot[k] + o[k] for k in range(3)]


def joints(ctx, hrc, anim):
    """Per frame: {bone: end, bone@: start, root} (model space, y down) plus each bone's world matrix."""
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


def _stand(ctx, hrc, stand):
    return joints(ctx, hrc, stand.split(".")[0])[0]


def entry_points(ctx, hrc, stand, anim):
    """Tifa's entry per frame (model space): 672's ENTRY (Ruby's stand frame) scaled to her legs, carried by
    her pelvis's turn."""
    from ff7 import fieldanim as fa
    mv, _, _ = _mods()
    sp = __import__("importlib").import_module("672_movie_special")
    leg = lambda h: sum(b[2] for b in fa.skeleton(ctx.char_file(h.lower()).decode("latin-1"))
                        if b[0] in ("l_femur", "l_tibia"))
    scale = leg(hrc) / leg(mv.RUBY_HRC)
    W0 = _stand(ctx, hrc, stand)["hip#"]
    out = []
    for J in joints(ctx, hrc, anim):
        R = fa._mul(J["hip#"], fa._t(W0))
        e = fa._vec(R, [c * scale for c in sp.ENTRY])
        out.append([J["root"][k] + e[k] for k in range(3)])
    return out


def mouths(ctx, hrc, stand, anim):
    """Her mouth per frame (model space)."""
    from ff7 import fieldanim as fa
    m0 = _stand(ctx, hrc, stand)["head#"]
    front = fa._vec(fa._t(m0), [0.0, 0.0, -1.0])                    # the face's way, in the head's frame
    out = []
    for J in joints(ctx, hrc, anim):
        S, E = J["head@"], J["head"]
        f = fa._vec(J["head#"], front)
        out.append([S[k] + (E[k] - S[k]) * MOUTH_T + f[k] * MOUTH_OUT for k in range(3)])
    return out


def his_tip(ctx):
    """Cloud's member tip and his root, standing (model space, y down)."""
    from ff7 import fieldanim as fa
    mv, hb, _ = _mods()
    J = _stand(ctx, "aaaa.hrc", "acfe.a")
    _, tip = hb.member_ends(ctx.char_file("zcmp.p"))
    t = fa._vec(J["hip#"], list(tip))
    return [J["hip@"][k] + t[k] for k in range(3)], J["root"]


def targets(points, n, deep):
    """Field tip targets: each point + the stroke along n (field unit vector, from her to him): DEPTH inside
    at the deepest frame `deep` (a fraction of the stroke), STROKE further out half a stroke later."""
    mv, _, _ = _mods()
    out = []
    for k, p in enumerate(points):
        u = k / len(points)
        s = TK.STROKE * (1 - math.cos(2 * math.pi * (u - deep))) / 2 - TK.DEPTH
        out.append([p[k_] + n[k_] * s * mv.UNIT for k_ in range(3)])
    return out


def spot(tips, dc, floor, tip0, root0):
    """Cloud's field spot (x, y) for these tip targets: standing, his tip on average where they are."""
    mv, _, _ = _mods()
    o = mv._off([tip0[k] for k in range(3)], dc)
    xs = [t[0] - o[0] for t in tips]
    ys = [t[1] - o[1] for t in tips]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def cloud(ctx, name, tips, hands, cspot, dc, floor, stance, lean, foot=None, nape=False):
    """Cloud's frames (written to name.a): his tip at tips[k] (field), standing at cspot (field, on the floor);
    hands = per frame (left, right) field points or None; foot = (out, forward) his left foot on the seat.
    Returns the drops (model units; < 0 = on his toes) for checks."""
    from ff7 import fieldanim as fa
    mv, _, _ = _mods()
    CP = DP._mods()[2]
    him = DP._Body(ctx, "aaaa.hrc", "acfe.a")
    tip0, root0 = his_tip(ctx)
    origin = [cspot[0], cspot[1], floor]
    sp = DP._mods()[1]
    I = [b[0] for b in him.sk].index
    seat_up = (TK.SEAT - TK.FLOOR) / mv.UNIT
    frames, drops = [], []
    for k, t in enumerate(tips):
        m = _inv_off([t[i] - origin[i] for i in range(3)], dc)            # his tip, model space
        r = [m[i] - (tip0[i] - root0[i]) for i in range(3)]
        drop = r[1] - root0[1]
        jump = 0.0
        if drop < 0:
            assert drop > -TIPTOE, ("too high for him", name, drop)
            jump, drop = -drop, 0.0
        drops.append(drop - jump)
        P = dict(drop=drop, jump=jump, shift=(r[0] - root0[0], -(r[2] - root0[2])), lean=(lean, 0, 0),
                 head=(lean * 0.6, 0, 0), leg_l=(stance, 0, 0), leg_r=(stance, 0, 0))
        if foot:                                                          # (his left foot up on the seat)
            P["leg_l"] = (stance + foot[0], seat_up, foot[1])
        if hands:
            l, r_ = hands[k]
            hl, hr = (_inv_off([p[i] - origin[i] for i in range(3)], dc) for p in (l, r_))
            if hl[0] < hr[0]:
                hl, hr = hr, hl                                           # (his left is +x)
            P["arm_l"] = ("at", hl, (1.0, 0.6, -0.2))
            P["arm_r"] = ("at", hr, (-1.0, 0.6, -0.2))
        frame = him.frame(P)
        if nape:                                                          # hands behind his head
            rr, rp, rots = frame
            root = [rp[0], -rp[1], rp[2]]
            F = fa.forward(him.sk, rr, root, rots)
            W = [mm for mm, _, _ in F]
            neck = F[I("head")][1]
            for side, sg in (("l", 1), ("r", -1)):
                F = fa.forward(him.sk, rr, root, fa.local_rotations(him.sk, rr, W))
                S_ = F[I(side + "_uparm")][1]
                L1, L2 = (math.dist(*F[I(side + "_uparm")][1:]), math.dist(*F[I(side + "_foarm")][1:]))
                T = [neck[0] + sg * NAPE[0], neck[1] + NAPE[1], neck[2] + NAPE[2]]
                dd = math.dist(S_, T)
                if dd > (L1 + L2) * 0.985:
                    T = [S_[q] + (T[q] - S_[q]) * (L1 + L2) * 0.985 / dd for q in range(3)]
                old_fo, hand = W[I(side + "_foarm")], W[I(side + "_hand")]
                W = sp._two_bone(fa, W, I, F, side + "_uparm", side + "_foarm", T, [sg * 1.5, -1.0, 0.6])
                W[I(side + "_hand")] = fa._mul(fa._mul(W[I(side + "_foarm")], DP._t(old_fo)), hand)
            frame = CP._frame(fa, him.sk, rr, root, W)
        frames.append(frame)
    CP._save(ctx, name, "acfe.a", frames)
    return drops

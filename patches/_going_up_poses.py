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


# ---- (user) the crawl and the waiting partners' idles, on Ruby (retargeted by 684) -------------------------
CRAWL_FRAMES = 30               # one crawl cycle (a step with each knee and hand)
CRAWL_LEG, CRAWL_ARM = 12, 10     # degrees: thighs / arms swing (user, since: subtler)
CRAWL_SWAY, CRAWL_ROLL = 6, 5      # (user: the rocking only in the hips, with a twist) the hips' yaw / roll at the waist
IDLE_FRAMES = 150
SHAKE = (20, 60, 3, 8)          # Elena waiting: hip shake from frame, to frame, shakes, degrees (user: subtler)
SHAKE_ROLL = 6                  # ... and its twist (roll) at the same time
LOOK = (80, 92, 118, 130, 50)   # ... then a look to her right: turn from, held from, back from, done, degrees
CAM_LOOK = (25, 40, 105, 125)   # Tifa waiting: turns to the camera from, held from, back from, done
TILT = (70, 82, 18)             # ... tilting her head to her right from, held from, degrees
CAM_UP = 12                     # (she looks up a little: the camera is above)


def _ruby_frame(ctx, anim, frame=0):
    from ff7 import fieldanim as fa
    mv, _, _ = DP._mods()
    sk = fa.skeleton(ctx.char_file(mv.RUBY_HRC).decode("latin-1"))
    rr, rp, rots = fa.Anim(ctx.char_file(anim.lower() + ".a")).frames[frame]
    root = [rp[0], -rp[1], rp[2]]
    F = fa.forward(sk, rr, root, rots)
    return fa, sk, rr, root, [m for m, _, _ in F], F


def _subtree(sk, top):
    names = [b[0] for b in sk]
    out, todo = set(), [top]
    while todo:
        n = todo.pop()
        out.add(names.index(n))
        todo += [b[0] for b in sk if b[1] == n]
    return out


def _turned(fa, W, idx, R):
    return [fa._mul(R, m) if i in idx else m for i, m in enumerate(W)]


def _sway(fa, sk, root, W, F, deg, roll=0.0, rr=None):
    """The lower body (pelvis and legs) turned deg about the vertical through the waist and rolled `roll` about her
    long axis (a twist); the upper body kept. With rr (the anim's root rotation): (user: the legs accommodating) each
    thigh re-aimed so its knee stays where it was (the shins and feet unchanged: kneeling stays planted)."""
    I = [b[0] for b in sk].index
    upper = _subtree(sk, "chest")
    lower = {i for i in range(len(sk)) if i not in upper}
    R = fa._mul(fa.axis_angle([0.0, 1.0, 0.0], deg), fa.axis_angle([0.0, 0.0, 1.0], roll))
    P = F[I("hip")][2]                                              # (the waist: chest and legs start here)
    rel = fa._vec(R, [root[k] - P[k] for k in range(3)])
    root2 = [P[k] + rel[k] for k in range(3)]
    W2 = _turned(fa, W, {i for i in lower if i not in _subtree(sk, "l_femur") | _subtree(sk, "r_femur")}, R)
    if rr is None:
        return root2, _turned(fa, W, lower, R)
    mv = DP._mods()[0]
    F2 = fa.forward(sk, rr, root2, fa.local_rotations(sk, rr, W2))
    for s_ in "lr":
        hipj, knee = F2[I(s_ + "_femur")][1], F[I(s_ + "_femur")][2]
        bd = fa._vec(W2[I(s_ + "_femur")], [0.0, 0.0, -1.0])
        W2[I(s_ + "_femur")] = fa._mul(mv._align(fa, bd, [knee[k] - hipj[k] for k in range(3)]), W2[I(s_ + "_femur")])
    return root2, W2


def _write(ctx, name, fa, sk, rr, frames):
    mv, _, CP = DP._mods()
    CP._save(ctx, name, mv.RUBY_STAND, [(rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, W)) for r, W in frames])
    return name + ".tor"


def crawl(ctx):
    """QXC0: on all fours (Ruby's dog stroke's frame 0), crawling: each thigh and arm swinging about the side
    axis (opposite pairs together), the hips swaying."""
    fa, sk, rr, root, W0, F0 = _ruby_frame(ctx, "ZMC0")
    x = [1.0, 0.0, 0.0]
    frames = []
    for t in range(CRAWL_FRAMES):
        ph = 2 * math.pi * t / CRAWL_FRAMES
        r, W = _sway(fa, sk, root, W0, F0, CRAWL_SWAY * math.sin(ph), CRAWL_ROLL * math.sin(ph), rr)
        for s, sg in (("l", 1), ("r", -1)):
            W = _turned(fa, W, _subtree(sk, s + "_femur"), fa.axis_angle(x, sg * CRAWL_LEG * math.sin(ph)))
            W = _turned(fa, W, _subtree(sk, s + "_uparm"), fa.axis_angle(x, -sg * CRAWL_ARM * math.sin(ph)))
        frames.append((r, W))
    return _write(ctx, "QXC0", fa, sk, rr, frames)


def _ease(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else (1 - math.cos(math.pi * (t - a) / (b - a))) / 2


def _head_turn(fa, sk, W, F, R):
    """The head (and what hangs from it) turned by world rotation R about the neck."""
    return _turned(fa, W, _subtree(sk, "head"), R)


def elena_idle(ctx):
    """QXD0: waiting on all fours: still, a hip shake, still, a look to her right and back (IDLE_FRAMES)."""
    fa, sk, rr, root, W0, F0 = _ruby_frame(ctx, "ZMC0")
    I = [b[0] for b in sk].index
    a0, a1, n, deg = SHAKE
    l0, l1, l2, l3, ldeg = LOOK
    y = [0.0, 1.0, 0.0]
    # (her right is -x: the turn's sign that takes her face that way)
    tip = lambda W: fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))[I("head")][2][0]
    sign = 1 if tip(_head_turn(fa, sk, W0, F0, fa.axis_angle(y, 20))) < tip(W0) else -1
    frames = []
    for t in range(IDLE_FRAMES):
        env = math.sin(math.pi * _ease(t, a0, a1))
        wob = env * math.sin(2 * math.pi * n * (t - a0) / (a1 - a0)) if a0 <= t <= a1 else 0
        r, W = _sway(fa, sk, root, W0, F0, deg * wob, SHAKE_ROLL * wob, rr)
        w = _ease(t, l0, l1) * (1 - _ease(t, l2, l3))
        W = _head_turn(fa, sk, W, F0, fa.axis_angle(y, sign * ldeg * w))
        frames.append((r, W))
    return _write(ctx, "QXD0", fa, sk, rr, frames)


def tifa_idle(ctx, cam_yaw):
    """QXE0: kneeling (Ruby's head position, pulled back: ZMJ9), waiting: turns her head to the camera
    (cam_yaw degrees about the vertical, CAM_UP up), tilts it to her right, back (IDLE_FRAMES)."""
    fa, sk, rr, root, W0, F0 = _ruby_frame(ctx, "ZMJ9")
    I = [b[0] for b in sk].index
    c0, c1, c2, c3 = CAM_LOOK
    t0, t1, tdeg = TILT
    y, x = [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]
    # her face's way (her head's frame) and the tilt's sign (to her right: the head top towards -x)
    S = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W0))
    hv = [S[I("head")][2][k] - S[I("head")][1][k] for k in range(3)]
    def top_x(R):
        return fa._vec(R, hv)[0]
    frames = []
    for t in range(IDLE_FRAMES):
        w = _ease(t, c0, c1) * (1 - _ease(t, c2, c3))
        tw = _ease(t, t0, t1) * (1 - _ease(t, c2, c3))
        Y = fa.axis_angle(y, cam_yaw * w)
        U = fa.axis_angle(x, -CAM_UP * w)
        face = fa._vec(Y, [0.0, 0.0, -1.0])                            # roll about her (turned) line of sight
        roll = lambda d: fa.axis_angle(face, d)
        sg = 1 if top_x(fa._mul(roll(10), Y)) < top_x(Y) else -1
        R = fa._mul(roll(sg * tdeg * tw), fa._mul(Y, U))
        frames.append((root, _head_turn(fa, sk, W0, F0, R)))
    return _write(ctx, "QXE0", fa, sk, rr, frames)


# ---- (user) Elena's torso: extended down and tapered in, so no gap opens at her waist as her hips rock --------
TORSO_EXT, TORSO_BAND, TORSO_TAPER = 0.7, 0.6, 0.18   # model units down / the bottom band moved / narrowed by


def extend_torso(ctx, hrc):
    """Her chest part's bottom band (the vertices within TORSO_BAND of its waist end, along the bone) moved
    TORSO_EXT further down the bone and narrowed by up to TORSO_TAPER (in the bone's frame: the bone runs along -z,
    so its waist end is the largest z). Written in place; once."""
    import struct
    fb = __import__("importlib").import_module("_female_body")
    if getattr(ctx, "_elena_torso", False):
        return
    ctx._elena_torso = True
    rsd = fb.bones(ctx.char_file(hrc.lower()).decode("latin-1"))["chest"][1][0]
    name = ctx.char_file(rsd.lower() + ".rsd").decode("latin-1").split("PLY=")[1][:4].lower() + ".p"
    d = bytearray(ctx.char_file(name))
    nv = struct.unpack_from("<16I", d, 0)[3]
    V = [list(struct.unpack_from("<3f", d, 128 + 12 * i)) for i in range(nv)]
    zmax = max(v[2] for v in V)
    for i, v in enumerate(V):
        w = (v[2] - (zmax - TORSO_BAND)) / TORSO_BAND
        if w > 0:
            k = 1 - TORSO_TAPER * w
            struct.pack_into("<3f", d, 128 + 12 * i, v[0] * k, v[1] * k, v[2] + TORSO_EXT * w)
    ctx.char_file(name, bytes(d))

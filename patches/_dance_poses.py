"""(user) The school dance's moves (682_school_dance), choreographed in the spirit of ATARASHII GAKKO!'s
routines: stomping marches, deep "yankee" squats swaying with hands on the knees, shrugging shoulder rolls,
punches at the sky, head-banging, kicks, spins, jumps and a slow back-bend, all in unison. Built on Ruby's
skeleton (her stand DXID; model space: y down, she faces -z, her left +x) as "XZ<letter><0>" and retargeted
per girl by 670 `_retarget`.

A pose is a dict (every key optional):
  drop        root this far down (model units): knees bend, feet stay planted (leg IK)
  jump        root (and feet) this far up
  shift       (x, z) root moved sideways / forward (feet stay unless `step`)
  step        True: the feet move with `shift`
  yaw         the whole body turned (degrees, about the vertical through the root)
  lean        (pitch forward, roll to her left, twist to her left) of the upper body about the waist
  head        (nod down, tilt to her left, turn to her left)
  arm_l/arm_r (a, f, reach[, elbow]): the hand at reach x the arm's length from the shoulder, in the
              direction a degrees up from straight down (out to her side), then f degrees towards her
              front (negative: behind); elbow = the elbow's pole in the body's frame (default back/down/out);
              "knee" = the hand on her own-side knee; None = hanging (turns with the lean)
  leg_l/leg_r (dx, lift, dz): the ankle moved from its stand place (dx out to her side, lift up, dz forward)
Each move is a function of its beat (0 .. beats) returning a pose; loops are sampled so they join up."""
import math

BEAT = 15                       # frames a beat (120 bpm at 30 fps)
SRC = "XZ"                      # the source anims' names on Ruby: XZ<letter>0


def _mods():
    from importlib import import_module
    return import_module("670_movie"), import_module("672_movie_special"), import_module("_chamber_poses")


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a + (b - a) * t


def pulse(t, at, width):
    """1 at `at`, falling to 0 `width` either side (cosine bump)."""
    d = abs(t - at)
    return 0.0 if d >= width else (1 + math.cos(math.pi * d / width)) / 2


# ---- the moves: (letter, beats, loop, function of beat) ------------------------------------------------
def bow(b):                      # A: heads down, waiting in line (one frame)
    return dict(lean=(22, 0, 0), head=(32, 0, 0), drop=0.3)


def wake(b):                     # B: heads snap up, arms rise to a T, hold, drop (8 beats, once)
    up = ease(b / 0.35)
    arm = ease((b - 1) / 3) * (1 - ease((b - 6) / 2))
    a = mix(8, 92, arm)
    return dict(lean=(22 * (1 - up), 0, 0), head=(32 * (1 - up) - 6 * up, 0, 0),
                drop=0.6 * abs(math.sin(math.pi * b)), arm_l=(a, -5, 0.98), arm_r=(a, -5, 0.98))


def march(b):                    # C: high-knee march, arms swinging bent (2 beats)
    p = b / 2
    ll, lr = max(0.0, math.sin(2 * math.pi * p)), max(0.0, -math.sin(2 * math.pi * p))
    sw = math.sin(2 * math.pi * p)
    return dict(leg_l=(0.2, 4.6 * ll, 2.6 * ll), leg_r=(0.2, 4.6 * lr, 2.6 * lr),
                arm_l=(18, -55 * sw, 0.72), arm_r=(18, 55 * sw, 0.72),
                drop=0.5 * abs(math.cos(2 * math.pi * p)), head=(-4, 4 * sw, 0), lean=(4, -3 * sw, 6 * sw))


def squat_sway(b):               # D: deep squat, hands on the knees, swaying the shoulders (4 beats)
    p = b / 4
    s = math.sin(2 * math.pi * p)
    return dict(drop=4.2, leg_l=(1.6, 0, 0), leg_r=(1.6, 0, 0), arm_l="knee", arm_r="knee",
                lean=(28, 14 * s, 10 * s), head=(-14, -16 * s, -8 * s), shift=(0.7 * s, 0))


def shrug(b):                    # E: shoulder shrugs and hip rolls, fists up (2 beats)
    p = b / 2
    s, c = math.sin(2 * math.pi * p), math.cos(2 * math.pi * p)
    return dict(drop=1.1 + 0.4 * c, shift=(1.0 * s, 0), lean=(6, -7 * s, 0), head=(0, 10 * s, 6 * s),
                arm_l=(30 + 14 * max(0, s), 62, 0.5), arm_r=(30 + 14 * max(0, -s), 62, 0.5))


def punch(b):                    # F: punches at the sky, right then left, bouncing on every beat (2 beats)
    bounce = 1.3 * (0.5 - 0.5 * math.cos(2 * math.pi * b))
    hit_r, hit_l = pulse(b, 0.35, 0.6) + pulse(b, 2.35, 0.6), pulse(b, 1.35, 0.6)
    chamber = (38, 70, 0.42)
    up = lambda h: (mix(chamber[0], 172, h), mix(chamber[1], 18, h), mix(chamber[2], 1.0, h))
    return dict(drop=bounce, arm_r=up(hit_r), arm_l=up(hit_l), head=(-12 * max(hit_l, hit_r), 0, 0),
                lean=(2, 5 * (hit_l - hit_r), 8 * (hit_l - hit_r)))


def headbang(b):                 # G: bent at the waist, head-banging on the beat, arms flailing (1 beat)
    n = math.cos(2 * math.pi * b)
    return dict(lean=(38 + 6 * n, 0, 0), head=(16 + 26 * n, 0, 0), drop=1.6 + 0.5 * n,
                arm_l=(12 + 22 * (1 - n), 25 + 30 * n, 0.9), arm_r=(12 + 22 * (1 - n), 25 - 30 * n, 0.9))


def side_step(b):                # H: step-touch side to side, arms waving overhead (4 beats)
    p = b / 4
    s = math.sin(2 * math.pi * p)
    lift = lambda ph: 1.4 * max(0.0, math.sin(2 * math.pi * (b + ph)))
    return dict(shift=(1.8 * s, 0), step=True, drop=0.8 + 0.4 * math.cos(4 * math.pi * p),
                leg_l=(0, lift(0.0), 0), leg_r=(0, lift(0.5), 0), lean=(0, 10 * s, 0), head=(0, 12 * s, 0),
                arm_l=(158 + 14 * s, 8, 0.98), arm_r=(158 - 14 * s, 8, 0.98))


def arm_wave(b):                 # I: a wave rippling arm to arm, the body following (4 beats)
    p = b / 4
    w = lambda ph: math.sin(2 * math.pi * (p - ph))
    return dict(arm_l=(92 + 28 * w(0), 0, 0.82 + 0.16 * w(0.12)), arm_r=(92 + 28 * w(0.5), 0, 0.82 + 0.16 * w(0.62)),
                lean=(0, 9 * w(0.25), 0), head=(0, 12 * w(0.3), 0), drop=0.7 + 0.5 * abs(w(0.25)),
                shift=(0.8 * w(0.25), 0))


def kick(b):                     # J: front kicks, right then left, arms out (4 beats)
    kr, kl = pulse(b, 0.5, 0.75), pulse(b, 2.5, 0.75)
    return dict(leg_r=(0.2, 6.8 * kr, 7.5 * kr), leg_l=(0.2, 6.8 * kl, 7.5 * kl),
                arm_l=(82, -8, 0.98), arm_r=(82, -8, 0.98), lean=(-10 * max(kr, kl), 0, 0),
                drop=0.6 + 0.6 * max(kr, kl), head=(-6 * max(kr, kl), 0, 0))


def spin(b):                     # K: a full turn, arms out (4 beats, once)
    t = ease(b / 4)
    return dict(yaw=360 * t, arm_l=(78, 0, 0.98), arm_r=(78, 0, 0.98),
                drop=1.2 * (1 - math.sin(math.pi * t)), head=(-4, 0, -20 * math.sin(math.pi * t)))


def jump(b):                     # L: crouch, jump with the arms thrust up, land (2 beats)
    p = b / 2
    if p < 0.3:
        c = ease(p / 0.3)
        return dict(drop=3.0 * c, arm_l=(20, -40 * c, 0.95), arm_r=(20, -40 * c, 0.95), lean=(18 * c, 0, 0))
    if p < 0.7:
        a = (p - 0.3) / 0.4
        h = 4.2 * math.sin(math.pi * a)
        return dict(jump=h, leg_l=(0.4, 1.6 * math.sin(math.pi * a), 0.4), leg_r=(0.4, 1.6 * math.sin(math.pi * a), 0.4),
                    arm_l=(172, 10, 1.0), arm_r=(172, 10, 1.0), head=(-14, 0, 0))
    c = 1 - ease((p - 0.7) / 0.3)
    return dict(drop=2.4 * c, arm_l=(mix(30, 172, c * 0.4), 0, 0.95), arm_r=(mix(30, 172, c * 0.4), 0, 0.95),
                lean=(12 * c, 0, 0))


def backbend(b):                 # M: a slow lean back, arms trailing behind, and up again (8 beats, once)
    t = ease(b / 4) * (1 - ease((b - 5) / 3))
    return dict(lean=(-42 * t, 0, 0), head=(-22 * t, 0, 0), drop=2.2 * t, shift=(0, 1.4 * t),
                arm_l=(mix(10, 42, t), mix(0, -45, t), 0.98), arm_r=(mix(10, 42, t), mix(0, -45, t), 0.98))


def run(b):                      # N: running on the spot, fists pumping (1 beat)
    s = math.sin(2 * math.pi * b)
    return dict(leg_l=(0.2, 2.6 * max(0, s), -1.2 * max(0, s)), leg_r=(0.2, 2.6 * max(0, -s), -1.2 * max(0, -s)),
                arm_l=(26, -62 * s, 0.55), arm_r=(26, 62 * s, 0.55), drop=0.6 + 0.4 * abs(s), lean=(10, 0, 5 * s))


def crouch_stare(b):             # O: the yankee squat, elbows on the knees, staring the audience down (4 beats)
    p = b / 4
    s = math.sin(2 * math.pi * p)
    return dict(drop=6.4, leg_l=(2.2, 0, -0.3), leg_r=(2.2, 0, -0.3), arm_l=(16, 62, 0.62), arm_r=(16, 62, 0.62),
                lean=(16, 0, 0), head=(-12 + 3 * s, 14, 4 * s))


def point(b):                    # P: the finish: pointing at the sky, hand on the hip, a knee bent (one frame)
    return dict(arm_r=(150, 28, 1.0), arm_l=(40, -25, 0.45, (1.0, 0.0, 0.4)), leg_r=(-0.4, 1.2, 1.0),
                head=(-10, 0, -14), lean=(-4, 6, -8), drop=0.4)


MOVES = [  # letter, beats, loop (frames = beats x BEAT; still = one frame), function
    ("A", 0, False, bow), ("B", 8, False, wake), ("C", 2, True, march), ("D", 4, True, squat_sway),
    ("E", 2, True, shrug), ("F", 2, True, punch), ("G", 1, True, headbang), ("H", 4, True, side_step),
    ("I", 4, True, arm_wave), ("J", 4, True, kick), ("K", 4, False, spin), ("L", 2, True, jump),
    ("M", 8, False, backbend), ("N", 1, True, run), ("O", 4, True, crouch_stare), ("P", 0, False, point),
]


# ---- building ------------------------------------------------------------------------------------------
def _t(m):
    return [[m[c][r] for c in range(3)] for r in range(3)]


class _Body:
    def __init__(self, ctx):
        mv, sp, CP = _mods()
        self.fa, self.sk, self.I, _, self.rr, self.root0, self.W0, _ = sp._setup(ctx, mv.RUBY_HRC, mv.RUBY_STAND)
        self.sp, self.CP, self.mv = sp, CP, mv
        names = [b[0] for b in self.sk]
        kids = {}
        for i, b in enumerate(self.sk):
            kids.setdefault(b[1], []).append(i)

        def below(n):
            out = [names.index(n)]
            for k in kids.get(n, []):
                out += below(names[k])
            return out
        up = []
        for top in ("chest", "non_1", "non_2"):
            up += below(top)
        self.upper, self.head = set(up), set(below("head"))
        e = CP._ends(self.fa, self.sk, self.rr, self.root0, self.W0)
        self.e0 = e
        self.waist = e["chest@"]
        self.arm_len = {s: math.dist(e[s + "_uparm@"], e[s + "_uparm"]) + math.dist(e[s + "_foarm@"], e[s + "_foarm"])
                        for s in "lr"}
        self.leg = {s: (math.dist(e[s + "_femur@"], e[s + "_femur"]), math.dist(e[s + "_tibia@"], e[s + "_tibia"]))
                    for s in "lr"}
        # sign of a forward pitch / a roll to her left about the model's axes (found once)
        fa = self.fa
        head = lambda R: fa._vec(R, [e["head"][k] - self.waist[k] for k in range(3)])
        self.pitch_s = 1 if head(fa.axis_angle([1.0, 0.0, 0.0], 10))[2] < head(fa.euler_matrix(0, 0, 0))[2] else -1
        self.roll_s = 1 if head(fa.axis_angle([0.0, 0.0, 1.0], 10))[0] > 0 else -1
        self.yaw_s = 1 if fa._vec(fa.axis_angle([0.0, 1.0, 0.0], 10), [0.0, 0.0, -1.0])[0] > 0 else -1

    def rot(self, pitch, roll, yaw):
        fa = self.fa
        R = fa.axis_angle([0.0, 1.0, 0.0], self.yaw_s * yaw)
        R = fa._mul(R, fa.axis_angle([0.0, 0.0, 1.0], self.roll_s * roll))
        return fa._mul(R, fa.axis_angle([1.0, 0.0, 0.0], self.pitch_s * pitch))

    def frame(self, P):
        fa, I, sk, rr = self.fa, self.I, self.sk, self.rr
        W = list(self.W0)
        # the upper body about the waist, the head about its joint
        L = self.rot(*P.get("lean", (0, 0, 0)))
        W = [fa._mul(L, m) if i in self.upper else m for i, m in enumerate(W)]
        hp, hr, hy = P.get("head", (0, 0, 0))
        H = self.rot(hp, hr, hy)
        Hw = fa._mul(fa._mul(L, H), _t(L))                      # the head's turn in the leant body's frame
        W = [fa._mul(Hw, m) if i in self.head else m for i, m in enumerate(W)]
        # the whole body's turn and the root
        Y = self.rot(0, 0, P.get("yaw", 0))
        W = [fa._mul(Y, m) for m in W]
        sx, sz = P.get("shift", (0, 0))
        r0 = self.root0
        dy = P.get("drop", 0) - P.get("jump", 0)
        off = fa._vec(Y, [sx, 0.0, -sz])
        root = [r0[0] + off[0], r0[1] + dy, r0[2] + off[2]]
        # legs: ankles planted (stand place, turned with the body; moved by step / leg offsets), knees forward
        F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
        fwd = fa._vec(Y, [0.0, 0.0, -1.0])
        for s, sg in (("l", 1), ("r", -1)):
            a0 = [self.e0[s + "_tibia"][k] - r0[k] for k in range(3)]
            a = fa._vec(Y, [a0[0], 0.0, a0[2]])
            dx, lift, dz = P.get("leg_" + s, (0, 0, 0))
            o = fa._vec(Y, [sg * dx + (sx if P.get("step") else 0), 0.0, -dz - (sz if P.get("step") else 0)])
            T = [r0[0] + a[0] + o[0], self.e0[s + "_tibia"][1] - lift - P.get("jump", 0), r0[2] + a[2] + o[2]]
            Hj = F[I(s + "_femur")][1]
            L1, L2 = self.leg[s]
            d = math.dist(Hj, T)
            if d > (L1 + L2) * 0.995:
                T = [Hj[k] + (T[k] - Hj[k]) * (L1 + L2) * 0.995 / d for k in range(3)]
            side = fa._vec(Y, [sg * 0.35, 0.0, 0.0])
            pole = [fwd[k] + side[k] for k in range(3)]
            foot = W[I(s + "_foot")]
            W = self.sp._two_bone(fa, W, I, F, s + "_femur", s + "_tibia", T, pole)
            W[I(s + "_foot")] = foot
            F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
        # arms: hands to their targets in the (leant, turned) body's frame, the hand following the forearm
        B = fa._mul(Y, L)
        e = self.CP._ends(fa, sk, rr, root, W)
        for s, sg in (("l", 1), ("r", -1)):
            spec = P.get("arm_" + s)
            if spec is None:
                continue
            S = e[s + "_uparm@"]
            if spec == "knee":
                K = e[s + "_femur"]
                T = [K[0] - sg * 0.3, K[1] - 0.7, K[2] - 0.9]
                pole_b = [sg * 1.0, 0.0, 0.6]
            else:
                a_, f_, reach = spec[:3]
                ar, fr = math.radians(a_), math.radians(f_)
                dvec = [sg * math.sin(ar) * math.cos(fr), math.cos(ar) * math.cos(fr), -math.sin(fr)]
                db = fa._vec(B, dvec)
                T = [S[k] + db[k] * self.arm_len[s] * reach for k in range(3)]
                pole_b = list(spec[3]) if len(spec) > 3 else [sg * 0.4, 0.5, 1.0]
                pole_b[0] *= sg if len(spec) > 3 else 1
            pole = fa._vec(B, pole_b)
            F = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
            S = F[I(s + "_uparm")][1]
            L1, L2 = (math.dist(*F[I(s + "_uparm")][1:]), math.dist(*F[I(s + "_foarm")][1:]))
            d = math.dist(S, T)
            if d > (L1 + L2) * 0.985:
                T = [S[k] + (T[k] - S[k]) * (L1 + L2) * 0.985 / d for k in range(3)]
            if d < abs(L1 - L2) + 0.3:
                T = [S[k] + (T[k] - S[k]) * (abs(L1 - L2) + 0.3) / max(d, 1e-6) for k in range(3)]
            old_fo, hand = W[I(s + "_foarm")], W[I(s + "_hand")]
            W = self.sp._two_bone(fa, W, I, F, s + "_uparm", s + "_foarm", T, pole)
            W[I(s + "_hand")] = fa._mul(fa._mul(W[I(s + "_foarm")], _t(old_fo)), hand)
        return self.CP._frame(fa, sk, rr, root, W)


def build(ctx):
    """Every move as XZ<letter>0 on Ruby. Returns [(letter, frames, loop)]."""
    body = _Body(ctx)
    mv, sp, CP = _mods()
    out = []
    for letter, beats, loop, fn in MOVES:
        n = max(1, beats * BEAT)
        frames = [body.frame(fn(beats * k / n if beats else 0)) for k in range(n)]
        if not loop and n > 1:                      # a one-off ends on its last pose
            frames.append(body.frame(fn(beats)))
        CP._save(ctx, "%s%s0" % (SRC, letter), mv.RUBY_STAND, frames)
        out.append((letter, len(frames), loop))
    return out

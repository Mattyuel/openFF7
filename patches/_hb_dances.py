"""(user) Tifa's own dances for the Honey Bee shift (689), replacing the borrowed Honey Bee dancer's moves: "rocking her
hips with her hands on her hips; hands clasped in the front, tilt head sideways, lift one leg back; a pretty twirl;
use and animate a bunch of these image ideas" (a pose-ideas sheet: hand on head, face to the side + a lifted leg,
hands together by the face, arms spread + legs crossed, touching her face + a hand behind, a high five + a tilted
head, arms out + a lifted leg).

Each dance is one loop of `FRAMES` frames built with the pose rig (`_besties_rig`) on her dress model: from her
stance into the pose (eased over `EASE` of the loop), held with her hips swaying and a little bounce (two beats a
loop), and back to her stance, so one dance can follow another without a snap. Standing feet stay planted (leg IK);
a lifted or crossed leg is aimed / solved to its target. Model space: y down, she faces -z, +x is her left."""
import math

import _besties_rig as RG
from _besties_rig import Rig, basis, bow, turn, lean, chain, add, sub, mul, unit, lerp

FRAMES = 90                     # one loop (3 s)
EASE = 0.22                     # share of the loop easing into / out of the pose
SWAY, BOB = 5, 0.12             # the held pose's hip sway (degrees) and bounce (model units), two beats a loop
TWIRL_FRAMES = 75               # the twirl: one full turn a loop
TWIRL_RISE = 0.3                # up on her toes at the middle of the turn


def _ease(t):
    u = min(1.0, t / EASE, (1 - t) / EASE)
    return u * u * (3 - 2 * u)


def _dir(rg, bone):
    E = rg.ends()
    return unit(sub(E[bone], E[bone + "@"]))


class _Pose:
    """One frame: her stance turned / swayed, then arms, legs and head by weight w."""

    def __init__(self, ctx, hrc, stand, w, beat, yaw=0.0, rise=0.0):
        self.ctx, self.hrc, self.stand, self.w = ctx, hrc, stand, w
        r = math.radians(yaw)
        self.rg = Rig(ctx, hrc, stand).start(basis([math.cos(r), 0.0, -math.sin(r)], RG.UP))
        self.E0 = Rig(ctx, hrc, stand).start(basis([math.cos(r), 0.0, -math.sin(r)], RG.UP)).ends()
        self.rest = {b: unit(sub(self.E0[b], self.E0[b + "@"])) for b in ("l_uparm", "l_foarm", "r_uparm", "r_foarm",
                                                                         "l_femur", "l_tibia", "r_femur", "r_tibia")}
        rg = self.rg
        rg.root = add(rg.root, [0.0, BOB * w * abs(beat) - rise, 0.0])
        rg.pelvis(lean(SWAY * w * beat))
        rg.waist(lean(-SWAY * 0.8 * w * beat))
        self.yaw = r

    def m(self, v):
        """A direction / offset in her own (turned) frame -> model space."""
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        return [c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2]]

    def head(self, turn_=0.0, tilt=0.0, nod=0.0):
        self.rg.neck(chain(turn(turn_ * self.w), lean(tilt * self.w), bow(nod * self.w)))

    def plant(self, side):
        sx = 1 if side == "l" else -1
        self.rg.ik(side + "_femur", side + "_tibia", self.E0[side + "_tibia"], self.m([sx * 0.2, 0.0, -1.0]),
                   keep_end=True)

    def leg_aim(self, side, thigh, shin):
        w = self.w
        self.rg.aim(side + "_femur", unit(lerp(self.rest[side + "_femur"], unit(self.m(thigh)), w)))
        self.rg.aim(side + "_tibia", unit(lerp(self.rest[side + "_tibia"], unit(self.m(shin)), w)))

    def leg_cross(self, side):
        """This leg's ankle crossed over in front of the other foot."""
        sx = 1 if side == "l" else -1
        other = "r" if side == "l" else "l"
        to = add(self.E0[other + "_tibia"], self.m([-sx * 0.9, -0.1, -1.0]))
        tgt = lerp(self.E0[side + "_tibia"], to, self.w)
        self.rg.ik(side + "_femur", side + "_tibia", tgt, self.m([0.0, 0.0, -1.0]), keep_end=True)

    def arm_aim(self, side, up, fo):
        w = self.w
        self.rg.aim(side + "_uparm", unit(lerp(self.rest[side + "_uparm"], unit(self.m(up)), w)))
        self.rg.aim(side + "_foarm", unit(lerp(self.rest[side + "_foarm"], unit(self.m(fo)), w)))

    def arm_to(self, side, target, pole):
        """Wrist to `target` (a model-space point), blended from where it hangs."""
        tgt = lerp(self.E0[side + "_foarm"], target, self.w)
        self.rg.ik(side + "_uparm", side + "_foarm", tgt, self.m(pole), keep_end=False)

    def at(self, joint, off):
        """A point `off` (her frame) from a joint of the posed rig."""
        return add(self.rg.ends()[joint], self.m(off))

    def frame(self):
        return self.rg.frame()


def _clasp(P):
    """(user) Hands clasped in front, head tilted sideways, her right leg lifted back."""
    P.head(tilt=18, nod=6)
    P.plant("l")
    P.leg_aim("r", [0.0, 0.92, 0.38], [0.0, -0.3, 1.0])
    E = P.rg.ends()
    mid = lerp(E["chest@"], E["chest"], 0.45)
    for s, sx in (("l", 1), ("r", -1)):
        P.arm_to(s, add(mid, P.m([sx * 0.25, 0.4, -2.0])), [sx * 1.0, 0.6, 0.4])


def _hand_on_head(P):
    """(sheet 1) Right hand on her head, the left arm straight down a little out, face to the side."""
    P.head(turn_=-25, tilt=8)
    P.plant("l")
    P.plant("r")
    P.arm_to("r", P.at("head", [-0.7, -0.2, 0.3]), [-1.0, -0.6, 0.2])
    P.arm_aim("l", [0.35, 1.0, 0.0], [0.35, 1.0, 0.0])


def _profile(P):
    """(sheet 2) Face to the side, her left knee lifted forward, hands behind her back."""
    P.head(turn_=35)
    P.plant("r")
    P.leg_aim("l", [0.1, 0.35, -0.95], [0.0, 1.0, 0.1])
    hips = lerp(P.rg.ends()["l_femur@"], P.rg.ends()["r_femur@"], 0.5)
    for s, sx in (("l", 1), ("r", -1)):
        P.arm_to(s, add(hips, P.m([sx * 0.4, -1.4, 1.9])), [sx * 1.0, 0.3, 0.6])


def _cheek(P):
    """(sheet 3) Both hands together beside her face, head tilted into them, her left leg lifted back."""
    P.head(tilt=-16, turn_=-10)
    P.plant("r")
    P.leg_aim("l", [0.0, 0.9, 0.42], [0.0, -0.4, 1.0])
    face = P.at("head", [-1.1, 0.9, -0.6])
    for s, sx in (("l", 1), ("r", -1)):
        P.arm_to(s, add(face, P.m([sx * 0.2, 0.3, 0.0])), [sx * 1.0, 0.4, 0.3])


def _spread(P):
    """(sheet 4) Arms spread out wide, her right leg crossed over."""
    P.head(tilt=10)
    P.plant("l")
    P.leg_cross("r")
    for s, sx in (("l", 1), ("r", -1)):
        P.arm_aim(s, [sx * 1.0, 0.25, -0.15], [sx * 1.0, 0.1, -0.2])


def _touch_face(P):
    """(sheet 5) Her right hand to her cheek, the left arm behind her, her right leg crossed over."""
    P.head(tilt=12, nod=5)
    P.plant("l")
    P.leg_cross("r")
    P.arm_to("r", P.at("head", [-0.9, 1.0, -0.8]), [-1.0, 0.5, 0.2])
    hips = lerp(P.rg.ends()["l_femur@"], P.rg.ends()["r_femur@"], 0.5)
    P.arm_to("l", add(hips, P.m([0.3, -1.2, 1.9])), [1.0, 0.3, 0.6])


def _high_five(P):
    """(sheet 8) Head tilted, her left hand behind her head, the right raised high, legs straight."""
    P.head(tilt=14)
    P.plant("l")
    P.plant("r")
    P.arm_to("l", P.at("head", [0.4, -0.2, 1.0]), [1.0, -0.6, 0.0])
    P.arm_aim("r", [-0.35, -1.0, -0.15], [-0.2, -1.0, -0.2])


def _arms_out(P):
    """(sheet 9) Arms outward, her left leg lifted back."""
    P.head(turn_=15, tilt=-8)
    P.plant("r")
    P.leg_aim("l", [0.05, 0.9, 0.45], [0.0, -0.25, 1.0])
    for s, sx in (("l", 1), ("r", -1)):
        P.arm_aim(s, [sx * 0.85, 0.55, -0.1], [sx * 0.8, 0.6, -0.15])


POSES = [("B", _clasp), ("C", _hand_on_head), ("D", _profile), ("E", _cheek), ("F", _spread), ("G", _touch_face),
         ("H", _high_five), ("I", _arms_out)]


def _twirl(ctx, hrc, stand, n):
    """(user) A pretty twirl: one full turn on the spot, up on her toes, arms rising into a curve (her left arm up
    over her head, the right out), easing in and out of her stance."""
    frames = []
    for k in range(n):
        t = k / n
        spin = (1 - math.cos(math.pi * t)) / 2                      # (slow, faster, slow)
        w = math.sin(math.pi * t)
        P = _Pose(ctx, hrc, stand, w, 0.0, yaw=360 * spin, rise=TWIRL_RISE * w)
        P.head(tilt=-10)
        P.plant("l")
        P.plant("r")
        P.arm_aim("l", [0.35, -0.95, -0.1], [-0.4, -0.9, -0.1])
        P.arm_aim("r", [-1.0, 0.15, -0.3], [-0.9, -0.1, -0.5])
        frames.append(P.frame())
    return frames


def build(ctx, hrc, stand, prefix):
    """Her dances as anim names (prefix + letter + '0'); the hip rock is _gestures' own (689 adds it)."""
    names = []
    for letter, pose in POSES:
        frames = []
        for k in range(FRAMES):
            t = k / FRAMES
            P = _Pose(ctx, hrc, stand, _ease(t), math.sin(2 * math.pi * 2 * t))
            pose(P)
            frames.append(P.frame())
        names.append(RG.save(ctx, "%s%s0" % (prefix, letter), stand, frames))
    names.append(RG.save(ctx, "%sT0" % prefix, stand, _twirl(ctx, hrc, stand, TWIRL_FRAMES)))
    return names

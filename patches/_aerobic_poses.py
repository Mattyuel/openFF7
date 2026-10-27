"""(user) The aerobics class's moves (693_gym, data `_aerobics.py`): the reference sheet "Aerobic exercise at home"
(knee lifts with the arms pumping, jumping jacks clapping overhead, heel kicks, standing cross crunches, a side
knee with the arm pulling down, the twist with the arms out, the chest fly, high knees) plus Tifa's boxercise
squat-punch, a bounce on the spot (between moves) and the finish.

Built with the school dance's body (`_dance_poses._Body`, any skeleton with the standard bone names) on every
classmate's own model, so all of them do exactly the same moves (DP's pose language: drop / jump / shift / yaw /
lean / head / arm_l / arm_r / leg_l / leg_r). Each move is one left-right cycle of two beats, built at two tempos
(`BEATS`: frames a beat) as "<prefix><letter><tempo>"; the bounce and the finish once (tempo 0)."""
import math

import _dance_poses as DP
from _dance_poses import ease, pulse

BEATS = (14, 10)                # frames a beat: the class's tempos (128 / 180 bpm at 30 fps)
CYCLE = 2                       # beats a move's cycle (left, right)


def _sw(b):
    """+1 on the left beat, -1 on the right (smooth)."""
    return math.sin(math.pi * b)


def knee_lift(b):                # A (sheet 1): knee lifts, the opposite arm pumping forward
    l, r = max(0.0, _sw(b)), max(0.0, -_sw(b))
    return dict(leg_l=(0.1, 5.2 * l, 3.0 * l), leg_r=(0.1, 5.2 * r, 3.0 * r),
                arm_l=(32, 80 * r - 35 * l, 0.72), arm_r=(32, 80 * l - 35 * r, 0.72),
                drop=0.5 * (1 - abs(_sw(b))), lean=(4, 0, 8 * (l - r)), head=(-4, 0, 0))


def jacks(b):                    # B (sheet 2): jumping jacks, hands clapping overhead
    o = (1 - math.cos(2 * math.pi * b / 2)) / 2           # 0 in, 1 out (one jack a cycle)
    hop = abs(math.sin(math.pi * b)) * 0.9
    a = 12 + 165 * o
    return dict(jump=hop, leg_l=(2.6 * o, 0, 0), leg_r=(2.6 * o, 0, 0), arm_l=(a, 6, 0.97), arm_r=(a, 6, 0.97),
                head=(-6 * o, 0, 0), drop=0.4 * (1 - hop))


def heel_kick(b):                # C (sheet 3): heels kicked up behind, fists by the shoulders
    l, r = max(0.0, _sw(b)), max(0.0, -_sw(b))
    return dict(leg_l=(0.1, 4.6 * l, -3.4 * l), leg_r=(0.1, 4.6 * r, -3.4 * r),
                arm_l=(30, 70, 0.42, (0.6, 0.6, -0.4)), arm_r=(30, 70, 0.42, (0.6, 0.6, -0.4)),
                drop=0.4 * (1 - abs(_sw(b))), lean=(6, 0, 0), head=(-2, 4 * (l - r), 0))


def cross_crunch(b):             # D (sheets 4-5): hands behind the head, the knee up and across to the opposite elbow
    l, r = max(0.0, _sw(b)), max(0.0, -_sw(b))
    behind = lambda: (150, -18, 0.42, (1.0, 0.0, 0.2))
    return dict(leg_l=(-0.6 * l, 5.4 * l, 2.4 * l), leg_r=(-0.6 * r, 5.4 * r, 2.4 * r),
                arm_l=behind(), arm_r=behind(), lean=(18 * (l + r), 0, 24 * (r - l)), head=(6 * (l + r), 0, 10 * (r - l)),
                drop=0.4 * (1 - abs(_sw(b))))


def side_knee(b):                # E (sheet 6): the knee lifted out to the side, the same arm pulled down from overhead
    l, r = max(0.0, _sw(b)), max(0.0, -_sw(b))
    arm = lambda k, o: (175 - 95 * k, 0, 0.98 - 0.4 * k)
    return dict(leg_l=(3.4 * l, 4.6 * l, 0.6 * l), leg_r=(3.4 * r, 4.6 * r, 0.6 * r),
                arm_l=arm(l, r), arm_r=arm(r, l), lean=(0, 16 * (r - l), 0), head=(0, 8 * (l - r), 0),
                drop=0.3 * (1 - abs(_sw(b))))


def twist(b):                    # F (sheet 7): arms straight out, twisting side to side over a wide stance
    s = _sw(b)
    return dict(leg_l=(1.6, 0, 0), leg_r=(1.6, 0, 0), drop=1.6 + 0.4 * abs(s), lean=(4, 0, 38 * s),
                arm_l=(88, 0, 0.98), arm_r=(88, 0, 0.98), head=(0, 0, 24 * s))


def chest_fly(b):                # G (sheet 8): arms crossing in front at chest height and opening, a half squat each
    c = (1 - math.cos(2 * math.pi * b / 2)) / 2          # 0 open, 1 crossed
    return dict(leg_l=(1.0, 0, 0), leg_r=(1.0, 0, 0), drop=0.6 + 1.6 * c,
                arm_l=(85, 15 + 80 * c, 0.9 - 0.25 * c), arm_r=(85, 15 + 80 * c, 0.9 - 0.25 * c),
                lean=(6 * c, 0, 0), head=(4 * c, 0, 0))


def high_knee(b):                # H (sheet 9): high knees, hands pushed down in front to meet them
    l, r = max(0.0, _sw(b)), max(0.0, -_sw(b))
    return dict(leg_l=(0.1, 6.6 * l, 3.6 * l), leg_r=(0.1, 6.6 * r, 3.6 * r), jump=0.4 * abs(_sw(b)),
                arm_l=(40, 60, 0.75), arm_r=(40, 60, 0.75), lean=(8, 0, 0), head=(4, 0, 0))


def squat_punch(b):              # I (Tifa's boxercise): a squat, then up with a punch, left then right
    p = (b % 1.0)
    down = math.sin(math.pi * p)                            # the squat in each beat
    left = b < 1
    hit = pulse(p, 0.75, 0.3)
    guard = (35, 75, 0.38, (0.6, 0.6, -0.4))
    punch_ = (88, 82, 0.98)
    mixa = lambda h: tuple(DP.mix(g, q, h) for g, q in zip(guard[:3], punch_)) + guard[3:]
    return dict(leg_l=(1.3, 0, 0), leg_r=(1.3, 0, 0), drop=3.2 * down * (1 - hit),
                arm_l=mixa(hit) if left else guard, arm_r=guard if left else mixa(hit),
                lean=(10 * down, 0, (18 if left else -18) * hit), head=(-4, 0, 0))


HIPS = (22, -12, 0.62, (1.0, -0.2, -0.4))     # a hand on the hip: down and a little out, the elbow out and back


def bounce(b):                   # S: bouncing on the spot, hands on the hips (between moves)
    return dict(drop=0.6 * abs(math.sin(math.pi * b)), arm_l=HIPS, arm_r=HIPS,
                head=(-3, 4 * math.sin(math.pi * b / 2), 0))


def finish(b):                   # Z: the finish, both arms up in a V, one heel lifted (one frame)
    return dict(arm_l=(155, 10, 1.0), arm_r=(155, 10, 1.0), leg_r=(0.6, 1.0, 0.4), head=(-12, 0, 0), lean=(-6, 0, 0))


MOVES = [("A", knee_lift), ("B", jacks), ("C", heel_kick), ("D", cross_crunch), ("E", side_knee), ("F", twist),
         ("G", chest_fly), ("H", high_knee), ("I", squat_punch)]


def build(ctx, hrc, stand, prefix):
    """The moves on this model: [A0, A1, B0, B1, ..., I0, I1, S0, Z0] (model loader names, "<prefix>A0.tor")."""
    from importlib import import_module
    CP = import_module("_chamber_poses")
    body = DP._Body(ctx, hrc, stand)
    names = []

    def save(name, frames):
        CP._save(ctx, name, stand, frames)
        names.append(name + ".tor")
    for letter, fn in MOVES:
        for t, beat in enumerate(BEATS):
            n = CYCLE * beat
            save("%s%s%d" % (prefix, letter, t), [body.frame(fn(CYCLE * k / n)) for k in range(n)])
    n = CYCLE * BEATS[0]
    save("%sS0" % prefix, [body.frame(bounce(CYCLE * k / n)) for k in range(n)])
    save("%sZ0" % prefix, [body.frame(finish(0))])
    return names

"""(user) Blast-off's poses (673): three men-and-a-girl positions, every anim a 15-frame stroke
(frame 0 out, 7 deepest) like the movie's, resampled to its four speeds by 673.

Frames: model units, y down, facing -z, +x = the model's left (fieldanim). A pose for two or three
actors is laid out in one shared frame (the frame of the entity the others are placed from); an
actor turned round (DIR + 128) maps his point p to (-p.x + O.x, p.y + O.y, -p.z + O.z), O = his
origin in the shared frame (`_to_shared` / `_to_own`).

- Rocketman (S): Cloud seated on the capsule's bench (his origin on the bench top), thrusting
  upwards (his pelvis lifting `RM_BOUNCE`), hands on her hips; she sits in his lap facing his way
  (same origin and DIR), bouncing with him, bent forward to Cid (her pelvis + chest bones re-aimed
  by two-bone IK so her neck follows a path level in height, bobbing towards him `RM_BOB`), her arms
  reaching to his thighs; Cid standing on the floor in front of her (turned round), leaning back
  steady, thrusting `CID_STROKE` into her mouth, his right hand on her head.
- Twinjets (T): her kneeling head pose (670's ZRTA) and Cloud's (ZCTQ) as the one-girl head; Cid
  the same on her other side (his member tip where Cloud's is, relative to her: the mirror of
  Cloud's spot), both hands on her head; her turn from one man to the other (V0 / V1, 180 degrees
  of root turn, either way).
- Exhaust (U): Cloud and her in the movie's holding (670's ZCTH / ZRKA, letter H); Cid behind her
  (turned round from her), his member tip at her seat, following her bounce, hands on her hips.
"""
import importlib
import math
import struct

CID_HRC, CID_STAND = "zcia.hrc", "abie.a"
RUBY_HRC, RUBY_STAND = "cbfe.hrc", "dxid.a"
CLOUD_STAND = "acfe.a"
N = 15                                     # frames a stroke
e_of = lambda t: (1 - math.cos(2 * math.pi * t / N)) / 2      # 0 out .. 1 deepest (frame 7)

# Rocketman
RM_SEAT_UP = 1.6                           # Cloud's root above the bench top
RM_LEAN = 12                               # Cloud's upper body back from upright
RM_BOUNCE = 1.0                            # his pelvis lifts this much at his deepest
RM_LAP_UP, RM_LAP_FWD = 1.5, 2.6           # her root above / ahead of his on his lap
RM_EXTRA = 0.3                             # she rides this much higher than his lift
RM_BOB = 1.2                               # her neck towards Cid at the deepest
RM_REACH = 0.93                            # her pelvis + chest stretched to this of their length at the deepest
RM_FACE_UP = 75                            # her head's crown this far up from pointing at Cid (face towards him)
CID_LEAN = 15                              # Cid's upper body back from upright (steady)
RM_CID_LEAN = 8                            # Rocketman: less (his longer member keeps him further off: his hand
                                           # must still reach her head)
CID_STROKE = 1.8                           # his pelvis travel
CID_FEET_OUT = 1.25                        # his feet this x his stand's spread
CID_UPPER = {"chest", "head", "l_chest", "l_collar", "l_uparm", "l_foarm", "l_hand",
             "r_chest", "r_collar", "r_uparm", "r_foarm", "r_hand"}     # what his lean turns
CID_DIP = 0.8                              # his natural tip this much below his straight-legged stand (knees soft)
MOUTH = (0.0, 0.8, -1.9)                   # her mouth from her head joint, in her head's frame (bone along -z)


def _mods():
    return importlib.import_module("672_movie_special"), importlib.import_module("670_movie"), \
        importlib.import_module("620_honey_bee")


def _to_shared(p, O):
    return [-p[0] + O[0], p[1] + O[1], -p[2] + O[2]]


def _to_own(q, O):
    return [-(q[0] - O[0]), q[1] - O[1], -(q[2] - O[2])]


def _member(ctx, ply):
    """(base, tip) of a bare man's member (620 `_member_p`) in his hip bone's frame."""
    return importlib.import_module("620_honey_bee").member_ends(ctx.char_file(ply))


def _write(ctx, base, frames, name):
    base.frames = frames
    ctx.char_file(name.lower() + ".a", base.build())


TIPTOE_MAX = 1.5                           # his feet raised at most this (on his toes)
HAND_SLACK = 1.0                           # fingertips within this of their target (else out of reach: asserted)


def _wrist(F, I, s, tip):
    """The wrist for fingertips at `tip`: along the shoulder -> tip line, a hand short of it, within
    the arm's reach."""
    sh = F[I(s + "_uparm")][1]
    reach = math.dist(*F[I(s + "_uparm")][1:]) + math.dist(*F[I(s + "_foarm")][1:])
    hand = math.dist(*F[I(s + "_hand")][1:])
    d = math.dist(sh, tip)
    k = min(reach - 0.05, max(d - hand, abs(math.dist(*F[I(s + "_uparm")][1:]) - math.dist(*F[I(s + "_foarm")][1:])) + 0.1))
    return [sh[j] + (tip[j] - sh[j]) * k / d for j in range(3)]


def _cid_stroke(ctx, name, tip_at, hands, lean=CID_LEAN, at="tip"):
    """Cid's thrust (his skeleton), N frames: his upper body leant back `lean` and steady, his
    member tip at tip_at(t) (his own frame), his root following from it; feet planted (his stand's
    ankles, CID_FEET_OUT x apart, under his deepest root) by two-bone leg IK; hands[side] = None
    (hanging as he stands) or a function t -> the wrist's target (his frame), two-bone arm IK."""
    sp, mv, hb = _mods()
    fa, sk, I, base, rr, root0, W0, fk = sp._setup(ctx, CID_HRC, CID_STAND)
    sub, add, dot, mul, unit, bdir = sp._v(fa)
    upper = CID_UPPER                                                    # (at the waist: his pelvis stays upright)
    tilt = lambda W, a: [fa._mul(fa.axis_angle([1.0, 0, 0], a), m) if sk[i][0] in upper else m for i, m in enumerate(W)]
    sense = 1 if fk(tilt(W0, 10), root0)[I("head")][2][2] > fk(W0, root0)[I("head")][2][2] else -1   # back = +z
    W = tilt(W0, sense * lean)
    mb, mt = _member(ctx, "zcjp.p")
    tip_rel = fa._vec(W[I("hip")], mt if at == "tip" else mb)   # (the hip bone starts at the root; at="base": the
                                                                # member's root follows tip_at instead)
    roots = [sub(tip_at(t), tip_rel) for t in range(N)]
    mid_z = sum(r[2] for r in roots) / N
    S0 = fk(W0, root0)
    feet = {s: [S0[I(s + "_tibia")][2][0] * CID_FEET_OUT, S0[I(s + "_tibia")][2][1],
                mid_z + S0[I(s + "_tibia")][2][2] - root0[2]] for s in "lr"}
    # (on his toes if he must: the feet raised just enough for every frame's reach)
    legs = math.dist(*S0[I("l_femur")][1:]) + math.dist(*S0[I("l_tibia")][1:]) - 0.08
    lift = 0.0
    while any(math.dist(fk(W, r)[I(s + "_femur")][1], [feet[s][0], feet[s][1] - lift, feet[s][2]]) > legs
              for r in roots for s in "lr"):
        lift += 0.05
        assert lift < TIPTOE_MAX, (name, "out of his reach", [round(v, 2) for v in roots[0]],
                                   [round(v, 2) for v in roots[N // 2]], round(root0[1], 2), {s_: [round(v, 2) for v in f_] for s_, f_ in feet.items()})
    for s in "lr":
        feet[s][1] -= lift
    if lift:
        print("  %s: Cid on his toes by %.2f" % (name, lift))
    frames = []
    for t in range(N):
        r = roots[t]
        Wt = list(W)
        for s, out in (("l", 1), ("r", -1)):
            F = fk(Wt, r)
            Wt = sp._two_bone(fa, Wt, I, F, s + "_femur", s + "_tibia", feet[s], [out * 0.3, 0.0, -1.0])   # knees forward
            Wt[I(s + "_foot")] = W0[I(s + "_foot")]
        for s, out in (("l", 1), ("r", -1)):
            if hands.get(s) is None:
                continue
            F = fk(Wt, r)
            wrist = _wrist(F, I, s, hands[s](t))
            Wt = sp._two_bone(fa, Wt, I, F, s + "_uparm", s + "_foarm", wrist, [out * 1.0, 0.6, 0.4])
            Wt[I(s + "_hand")] = fa._mul(mv._align(fa, bdir(Wt[I(s + "_hand")]), sub(hands[s](t), wrist)),
                                         Wt[I(s + "_hand")])
        F = fk(Wt, r)
        for s in "lr":
            assert math.dist(F[I(s + "_tibia")][2], feet[s]) < 0.05, (name, "feet", s, t)
            if hands.get(s):
                miss = math.dist(F[I(s + "_hand")][2], hands[s](t))
                assert miss < HAND_SLACK, (name, "hand", s, t, round(miss, 2),
                                           [round(v, 2) for v in F[I(s + "_uparm")][1]], [round(v, 2) for v in hands[s](t)],
                                           [round(v, 2) for v in r])
        frames.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, Wt)))
    _write(ctx, base, frames, name)
    return roots


def _cid_natural_tip(ctx, lean=CID_LEAN):
    """His member tip standing (his stand, leant back), his frame."""
    sp, mv, hb = _mods()
    fa, sk, I, base, rr, root0, W0, fk = sp._setup(ctx, CID_HRC, CID_STAND)
    upper = CID_UPPER                                                    # (at the waist: his pelvis stays upright)
    tilt = lambda W, a: [fa._mul(fa.axis_angle([1.0, 0, 0], a), m) if sk[i][0] in upper else m for i, m in enumerate(W)]
    sense = 1 if fk(tilt(W0, 10), root0)[I("head")][2][2] > fk(W0, root0)[I("head")][2][2] else -1
    W = tilt(W0, sense * lean)
    _, mt = _member(ctx, "zcjp.p")
    v = fa._vec(W[I("hip")], mt)
    return [root0[0] + v[0], root0[1] + v[1] + CID_DIP, root0[2] + v[2]]


# ---- Rocketman ------------------------------------------------------------------------------
def rocketman(ctx, bench_drop):
    """ZNS (Cloud), ZMSA (her, Ruby's skeleton), ZGS (Cid). bench_drop = the floor below the bench
    top (model units, > 0). Returns Cid's origin in Cloud's frame (he is turned round)."""
    sp, mv, hb = _mods()
    # Cloud, seated (his bare model's skeleton = aaaa's)
    fa, sk, I, base, rr, croot0, CW0, cfk = sp._setup(ctx, "aaaa.hrc", CLOUD_STAND)
    sub, add, dot, mul, unit, bdir = sp._v(fa)
    upper = {"hip", "chest", "head", "l_chest", "l_collar", "l_uparm", "l_foarm", "l_hand",
             "r_chest", "r_collar", "r_uparm", "r_foarm", "r_hand"}
    tilt = lambda W, a: [fa._mul(fa.axis_angle([1.0, 0, 0], a), m) if sk[i][0] in upper else m for i, m in enumerate(W)]
    sense = 1 if cfk(tilt(CW0, 10), croot0)[I("head")][2][2] > cfk(CW0, croot0)[I("head")][2][2] else -1
    CW = tilt(CW0, sense * RM_LEAN)
    for s in "lr":
        CW[I(s + "_femur")] = sp._pitch(fa, CW0[I(s + "_femur")], [0, 0, -1])      # thighs forward, level
        CW[I(s + "_tibia")] = sp._pitch(fa, CW0[I(s + "_tibia")], [0, 1, -0.15])   # shins hanging
        CW[I(s + "_foot")] = CW0[I(s + "_foot")]
    croots = [[0.0, -RM_SEAT_UP - RM_BOUNCE * e_of(t), 0.0] for t in range(N)]
    feet_y = max(cfk(CW, croots[0])[I(s + "_tibia")][2][1] for s in "lr")
    assert feet_y < bench_drop, ("his feet above the floor", feet_y, bench_drop)

    # her, in his lap (Ruby's skeleton; same frame)
    gfa, gsk, gI, gbase, grr, groot0, GW0, gfk = sp._setup(ctx, RUBY_HRC, RUBY_STAND)
    GW = list(GW0)
    for s in "lr":
        GW[gI(s + "_femur")] = sp._pitch(fa, GW0[gI(s + "_femur")], [0, 0, -1])
        GW[gI(s + "_tibia")] = sp._pitch(fa, GW0[gI(s + "_tibia")], [0, 1, -0.1])
    groots = [[0.0, croots[t][1] - RM_LAP_UP - RM_EXTRA * e_of(t), -RM_LAP_FWD] for t in range(N)]
    Lh = math.dist(*gfk(GW0, groot0)[gI("hip")][1:]) + math.dist(*gfk(GW0, groot0)[gI("chest")][1:])

    # Cid: his origin O (Cloud's frame) puts his natural member tip at her mouth; her neck path from it
    tip_nat = _cid_natural_tip(ctx, RM_CID_LEAN)
    face = lambda W: fa._vec(W[gI("head")], list(MOUTH))
    # her mouth = Cid's tip height; at the deepest her pelvis + chest stretched RM_REACH towards it
    a_ = math.radians(RM_FACE_UP)                             # her head: crown towards Cid tipped up (face to him)
    head_m = fa._mul(mv._align(fa, bdir(GW0[gI("head")]), [0.0, -math.sin(a_), -math.cos(a_)]), GW0[gI("head")])
    mouth_off = fa._vec(head_m, list(MOUTH))
    mouth_y = bench_drop + tip_nat[1]
    neck_y = mouth_y - mouth_off[1]
    deep = groots[N // 2]
    dy = neck_y - deep[1]
    assert abs(dy) < RM_REACH * Lh, ("her neck out of reach of her pelvis", dy, Lh)
    neck_z = deep[2] - math.sqrt((RM_REACH * Lh) ** 2 - dy * dy)
    necks = [[0.0, neck_y, neck_z + RM_BOB * (1 - e_of(t))] for t in range(N)]     # (+z: away from him)

    def her_pose(t):
        r = groots[t]
        W = list(GW)
        F = gfk(W, r)
        W = sp._two_bone(fa, W, gI, F, "hip", "chest", necks[t], [0.0, -1.0, 1.0])   # her back arched up
        Rc = fa._mul(W[gI("chest")], fa._t(GW[gI("chest")]))      # her shoulders and arms ride on her chest
        for n_ in ("non_1", "non_2", "l_collar", "r_collar", "l_uparm", "l_foarm", "l_hand", "r_uparm", "r_foarm", "r_hand"):
            W[gI(n_)] = fa._mul(Rc, GW[gI(n_)])
        W[gI("head")] = head_m
        return W, r
    W7, r7 = her_pose(N // 2)
    F7 = gfk(W7, r7)
    mouth7 = add(F7[gI("chest")][2], face(W7))
    tip_shared = _to_shared(tip_nat, [0.0, bench_drop, 0.0])
    O = [0.0, bench_drop, mouth7[2] - tip_shared[2]]          # (x: both on his centre line)
    # Cid's tip path (his frame): her mouth each frame (it moves only towards / away from him)
    mouths = []
    for t in range(N):
        W, r = her_pose(t)
        F = gfk(W, r)
        mouths.append(add(F[gI("chest")][2], face(W)))
    mouths_own = [_to_own(m, O) for m in mouths]
    # his: tip at her mouth at the deepest, CID_STROKE back of the path at frame 0
    tip_at = lambda t: add(mouths_own[t], mul([0.0, 0.0, 1.0], CID_STROKE * (1 - e_of(t))))

    def her_head_top(t):                                       # (his right hand's target: on her crown)
        W, r = her_pose(t)
        F = gfk(W, r)
        top = add(F[gI("head")][2], [0.0, -0.4, 0.0])
        return _to_own(top, O)
    _cid_stroke(ctx, "ZGSA", tip_at, {"r": her_head_top, "l": None}, lean=RM_CID_LEAN)

    # Cid's thighs in Cloud's frame (her hands' targets), from his written frames
    csk = fa.skeleton(ctx.char_file(CID_HRC).decode("latin-1"))
    cI = [b[0] for b in csk].index
    canim = fa.Anim(ctx.char_file("zgsa.a"))

    def cid_thigh(t, s):
        crr, crp, crots = canim.frames[t]
        F = fa.forward(csk, crr, [crp[0], -crp[1], crp[2]], crots)
        knee, hip_j = F[cI(s + "_femur")][2], F[cI(s + "_femur")][1]
        return _to_shared([(knee[k] * 0.6 + hip_j[k] * 0.4) for k in range(3)], O)

    # her frames: arms to his thighs (her left hand to his right thigh: they face each other)
    gframes = []
    for t in range(N):
        W, r = her_pose(t)
        for s, his in (("l", "r"), ("r", "l")):
            F = gfk(W, r)
            hand_len = math.dist(*F[gI(s + "_hand")][1:])
            tgt = cid_thigh(t, his)
            sh = F[gI(s + "_uparm")][1]
            reach = math.dist(*F[gI(s + "_uparm")][1:]) + math.dist(*F[gI(s + "_foarm")][1:])
            wrist = add(sh, mul(unit(sub(tgt, sh)), min(reach - 0.1, math.dist(sh, tgt) - hand_len * 0.8)))
            out = 1 if s == "l" else -1
            W = sp._two_bone(fa, W, gI, F, s + "_uparm", s + "_foarm", wrist, [out * 1.0, 0.5, 0.3])
            W[gI(s + "_hand")] = fa._mul(mv._align(fa, bdir(W[gI(s + "_hand")]), bdir(W[gI(s + "_foarm")])),
                                         W[gI(s + "_hand")])
        F = gfk(W, r)
        assert math.dist(F[gI("chest")][2], necks[t]) < 0.05, ("her neck", t)
        gframes.append((grr, [r[0], -r[1], r[2]], fa.local_rotations(gsk, grr, W)))
    _write(ctx, gbase, gframes, "ZMSA")

    # Cloud's frames: hands on her hips
    cframes = []
    for t in range(N):
        r = croots[t]
        W = list(CW)
        her = fa.Anim(ctx.char_file("zmsa.a")).frames[t]
        HF = fa.forward(gsk, her[0], [her[1][0], -her[1][1], her[1][2]], her[2])
        for s, out in (("l", 1), ("r", -1)):
            F = cfk(W, r)
            hip_side = HF[gI(s + "_femur")][1]
            wrist = add(hip_side, [out * 1.0, -0.6, 0.6])
            W = sp._two_bone(fa, W, I, F, s + "_uparm", s + "_foarm", wrist, [out * 1.0, 0.5, 0.5])
            W[I(s + "_hand")] = fa._mul(mv._align(fa, bdir(W[I(s + "_hand")]), [0.0, 0.3, -1.0]), W[I(s + "_hand")])
        cframes.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, W)))
    _write(ctx, base, cframes, "ZNSA")
    return O


# ---- Twinjets -------------------------------------------------------------------------------
TJ_HAND_OUT, TJ_HAND_UP = 2.6, 2.8         # his fingertips either side of her head (her head's frame), up its bone
TJ_TURN = 30                               # frames of her turn from one man to the other
TJ_LEAN = 35                               # Cid leaning forward to her head (his member is longer: he stands further off)


def _cloud_tip(ctx, anim, t, base=False):
    """Bare Cloud's member tip (base: its root) in his frame, frame t of `anim`."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("zcla.hrc").decode("latin-1"))
    rr, rp, rots = fa.Anim(ctx.char_file(anim)).frames[t]
    m, start, _ = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)[0]
    mb, mt = _member(ctx, "zcmp.p")
    v = fa._vec(m, mb if base else mt)
    return [start[k] + v[k] for k in range(3)]


def twinjets(ctx, her_in_his):
    """ZGTA (Cid, her head pose's partner): her_in_his = her origin in Cloud's frame in the movie's head
    layout (she faces him). Cid stands in the same relation on her other side: his tip where Cloud's
    is (670's ZCTQ), both hands on her head (her ZRTA frames). Then her turns ZMV0 / ZMV1."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    gI = [b[0] for b in sk].index
    her = fa.Anim(ctx.char_file("zrta.a")).frames
    assert len(her) == N, len(her)
    O = her_in_his                                  # (her turned round in his frame: _to_shared maps hers to his)

    def head_side(t, s):
        rr, rp, rots = her[t]
        F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
        m, st, _ = F[gI("head")]
        out = 1 if s == "l" else -1
        # (his left hand on her right side: they face each other)
        p = [st[k] + fa._vec(m, [-out * TJ_HAND_OUT, 0.0, -TJ_HAND_UP])[k] for k in range(3)]
        return _to_shared(p, O)
    _cid_stroke(ctx, "ZGTA", lambda t: _cloud_tip(ctx, "zctq.a", t, base=True), at="base",
                hands=
                {"l": lambda t: head_side(t, "l"), "r": lambda t: head_side(t, "r")}, lean=-TJ_LEAN)
    # (his member's root where Cloud's is: Cloud's tip angles up since (user), Cid's is straight)
    # her turn: ZRTA's frame 0 (pulled back) turned about the vertical through her root, 0 -> 180
    a = fa.Anim(ctx.char_file("zrta.a"))
    rr, rp, rots = a.frames[0]
    for name, sense in (("ZMV0", 1), ("ZMV1", -1)):
        frames = []
        for t in range(TJ_TURN):
            w = (1 - math.cos(math.pi * t / (TJ_TURN - 1))) / 2
            R = fa.axis_angle([0.0, 1.0, 0.0], sense * 180 * w)
            W = [m for m, _, _ in fa.forward(sk, rr, [0.0, 0.0, 0.0], rots)]
            Wr = [fa._mul(R, m) for m in W]
            p = fa._vec(R, [rp[0], -rp[1], rp[2]])
            frames.append((rr, [p[0], -p[1], p[2]], fa.local_rotations(sk, rr, Wr)))
        a.frames = frames
        ctx.char_file(name.lower() + ".a", a.build())


# ---- Exhaust --------------------------------------------------------------------------------
EX_ENTRY = (0.0, 1.2, 1.0)                 # her seat's entry from her root in her stand's frame (672 ENTRY)
EX_HIPS_OUT = 0.9                          # his fingertips this far outside her hip joints
EX_LEAN = -20                              # (negative: leaning forward, to reach her hips)


EX_LOW = 0.8                               # (user's carry, lowered) Cloud's pelvis at this of its height: her
                                           # seat in the movie's holding was 2.6 above Cid's reach


def exhaust_carry(ctx):
    """ZNUK (bare Cloud: 620's koala stand ZCTH with his knees bent to EX_LOW) and ZMUK (her koala hug
    on it, 660 `_koala`, Ruby's skeleton): the movie's holding, lower."""
    hb = importlib.import_module("620_honey_bee")
    dt = importlib.import_module("660_dates")
    hb._cloud_stand(ctx, "ZNUK.tor", hb.KOALA_CLOUD_ARMS, elbow_in=hb.KOALA_CLOUD_ELBOW, lean=hb.KOALA_CLOUD_LEAN,
                    arms_out=hb.KOALA_CLOUD_OUT, low=EX_LOW)
    dt._koala(ctx, "ZMUK.tor", RUBY_HRC, RUBY_STAND, his_anim="znuk.a")


def exhaust(ctx):
    """ZGUA: Cid behind her in the lowered holding (`exhaust_carry`: ZNUK / ZMUK; she shares Cloud's spot,
    turned round), turned round from Cloud (facing him), his tip at her seat's entry each frame (she bounces
    with Cloud), CID_STROKE back at frame 0; hands on her hips. Returns his origin in Cloud's frame."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    gI = [b[0] for b in sk].index
    exhaust_carry(ctx)
    her = fa.Anim(ctx.char_file("zmuk.a")).frames
    assert len(her) == N, len(her)
    W0 = [m for m, _, _ in fa.forward(sk, *_stand0(ctx))]
    hers = lambda p: [-p[0], p[1], -p[2]]                   # her frame -> Cloud's (same spot, turned round)

    def entry(t):
        rr, rp, rots = her[t]
        F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
        Rh = fa._mul(F[gI("hip")][0], fa._t(W0[gI("hip")]))
        root = [rp[0], -rp[1], rp[2]]
        v = fa._vec(Rh, list(EX_ENTRY))
        return hers([root[k] + v[k] for k in range(3)])

    def hip_side(t, s):
        rr, rp, rots = her[t]
        F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
        # his left hand on her left hip (both face Cloud's way... she faces Cloud, he faces her back)
        j = F[gI(s + "_femur")][1]
        out = 1 if s == "l" else -1
        m = F[gI("hip")][0]
        return hers([j[k] + fa._vec(m, [out * EX_HIPS_OUT, 0.0, 0.0])[k] for k in range(3)])
    tip_nat = _cid_natural_tip(ctx, EX_LEAN)
    deep = entry(N // 2)
    t_sh = _to_shared(tip_nat, [0.0, 0.0, 0.0])
    O = [deep[0] - t_sh[0], 0.0, deep[2] - t_sh[2]]
    tip_at = lambda t: [a + b for a, b in zip(_to_own(entry(t), O), [0.0, 0.0, CID_STROKE * (1 - e_of(t))])]
    # (her left hip is on his left: he faces her back, the same way she faces)
    _cid_stroke(ctx, "ZGUA", tip_at, {"l": lambda t: _to_own(hip_side(t, "l"), O),
                                       "r": lambda t: _to_own(hip_side(t, "r"), O)}, lean=EX_LEAN)
    return O


def _stand0(ctx):
    from ff7 import fieldanim as fa
    rr, rp, rots = fa.Anim(ctx.char_file(RUBY_STAND)).frames[0]
    return rr, [rp[0], -rp[1], rp[2]], rots

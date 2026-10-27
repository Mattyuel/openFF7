"""(user: "more variety to animation in intro scenes") One-shot gestures for the parody films' intro actors
(683-686): the original game's own anims on each skeleton (picked on contact sheets), played once while a line
shows (ANIME1 in a free script slot of the actor, then back to its stand) and REQ'd before the line, so the
director never waits. A seated actor gets a seated copy (`seated`: her sitting frame below the chest, the
head and arms from the gesture). Each film's data module has INTRO_GESTURES {intro line index: [(actor, gesture)]}."""
from ff7 import asm
from ff7.script import Op

SLOT = 12                       # an actor's gestures take its script slots SLOT.., in `used` order

ANIMS = {
    "cloud": {"shrug": "AQCB.chi", "nod": "AJDC.aki", "shakehead": "BUAA.chi", "laugh": "BTCD.aki",
              "point": "ALGB.yos", "stretch": "HOCF.tak", "warmup": "FJCB.yos", "leanin": "CDDE.tor",
              "coy": "EGIC.yos", "impatient": "BDCC.aki", "lookaround": "AUEE.yos", "formal": "EGGD.yos"},
    "tifa": {"hips": "AQFE.yos", "ready": "FDCF.yos", "think": "BTCC.tak", "pose": "EPDF.yos", "lean": "ARFB.kei",
             "hiprock": "ZGHR.tor"},
    "jessie": {"arms": "CNJA.tor", "hips": "CNJE.tor", "point": "BXJA.yos",
               "lookl": "ZGJL.tor", "lookr": "ZGJR.tor", "nod": "ZGJN.tor"},
    "scarlet": {"hip": "EHBC.yos", "laugh": "FFDE.yos"},
    "elena": {"chest": "ETDC.kei", "shrug": "CGCF.aki", "hop": "AVFD.yos", "clasp": "EWBC.tak"},
}
# (user: "in workout intro add a hip rocking with hands on hips animation for tifa instead of the running on the
# spot one") our own gestures, built on first use: name -> builder(ctx, hrc, name)
HIPROCK = dict(frames=60, cycles=2, sway=0.9, roll=9, counter=1.3, hand_out=1.3, hand_up=2.3, hand_back=0.4)
LOWER = ("hip", "chest", "l_hip", "l_femur", "l_tibia", "l_foot", "r_hip", "r_femur", "r_tibia", "r_foot")


def used(gestures, actor):
    """The gestures `actor` plays in a film, in slot order."""
    return sorted({g for lst in gestures.values() for a, g in lst if a == actor})


def seated(ctx, hrc, gesture, sit, name):
    """A copy of `gesture` (anim name) with every frame's root, lower body and chest (`LOWER`) from `sit`'s
    first frame: the arms and head move, the hips stay on the seat (the gesture's own chest leaned her far back
    or hunched her over on the seat). Returns name + '.tor'."""
    from ff7 import fieldanim as fa
    bones = [b[0] for b in fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))]
    G = fa.Anim(ctx.char_file(gesture.split(".")[0].lower() + ".a"))
    S = fa.Anim(ctx.char_file(sit.split(".")[0].lower() + ".a"))
    sr, sp, srots = S.frames[0]
    keep = [i for i, b in enumerate(bones) if b in LOWER]
    out = []
    for rr, rp, rots in G.frames:
        rots = list(rots)
        for i in keep:
            rots[i] = srots[i]
        out.append((sr, sp, rots))
    G.frames = out
    ctx.char_file(name.lower() + ".a", G.build())
    return name + ".tor"


def _hiprock(ctx, hrc, name):
    """Standing, hands on her hips (two-bone IK to just above each hip joint, out to the side), hips rocking side to
    side `cycles` times over `frames` (root sway + pelvis roll, the upper body countering), feet planted."""
    import math
    import _besties_rig as RG
    c = HIPROCK
    rg0 = RG.Rig(ctx, hrc, "abcd.a").start(RG.basis(RG.LEFT, RG.UP))
    E0 = rg0.ends()
    feet = {s: E0[s + "_tibia"] for s in "lr"}
    frames = []
    for k in range(c["frames"]):
        sw = math.sin(2 * math.pi * c["cycles"] * k / c["frames"])
        rg = RG.Rig(ctx, hrc, "abcd.a").start(RG.basis(RG.LEFT, RG.UP))
        rg.root = RG.add(rg.root, [c["sway"] * sw, 0.0, 0.0])
        rg.pelvis(RG.lean(c["roll"] * sw))
        rg.waist(RG.lean(-c["roll"] * c["counter"] * sw))
        for s, sx in (("l", 1), ("r", -1)):
            rg.ik(s + "_femur", s + "_tibia", feet[s], [sx * 0.2, 0.0, -1.0], keep_end=True)
        E = rg.ends()
        for s, sx in (("l", 1), ("r", -1)):
            wrist = RG.add(E[s + "_femur@"], [sx * c["hand_out"], -c["hand_up"], c["hand_back"]])   # (beside her waist)
            rg.ik(s + "_uparm", s + "_foarm", wrist, [sx * 1.0, 0.0, 0.3], keep_end=False)
            rg.aim(s + "_hand", [-sx * 0.35, 0.6, -0.7])                    # (fingers forward over her hip)
        frames.append(rg.frame())
    return RG.save(ctx, name, "abcd.a", frames)


# (user: "Jessie's seated animation is really bad ... just add a new animation where she turns her head rather than
# her arms. this is a poor quality model") seated head moves: her sitting frame held, only the head turning
# (degrees to her left, + = left; nod degrees down), eased out and back over `frames`, held at the turn
LOOK = {"ZGJL": dict(yaw=35, nod=0), "ZGJR": dict(yaw=-35, nod=0), "ZGJN": dict(yaw=10, nod=14)}
LOOK_FRAMES, LOOK_HOLD = 60, 0.4       # frames; share of them held at the turn


def _look(ctx, hrc, name, sit=None):
    import math
    import _besties_rig as RG
    assert sit, "a head look is a seated gesture"
    c = LOOK[name]
    frames = []
    for k in range(LOOK_FRAMES):
        t = k / (LOOK_FRAMES - 1)
        rise = (1 - LOOK_HOLD) / 2
        u = min(1.0, t / rise, (1 - t) / rise)
        w = u * u * (3 - 2 * u)                                             # (smoothstep in, held, out)
        if c["nod"]:
            w2 = math.sin(math.pi * min(1.0, 2 * t)) if t < 0.5 else 0.0      # one nod in the first half
        rg = RG.Rig(ctx, hrc, sit).start(RG.basis(RG.LEFT, RG.UP))
        R = RG.turn(c["yaw"] * w)
        if c["nod"]:
            R = RG.chain(R, RG.bow(c["nod"] * w2))
        rg.neck(R)
        frames.append(rg.frame())
    return RG.save(ctx, name, sit.split(".")[0].lower() + ".a", frames)


BUILT = {"ZGHR.tor": _hiprock, "ZGJL.tor": _look, "ZGJR.tor": _look, "ZGJN.tor": _look}


def anims(ctx, gestures, actor, who, hrc=None, sit=None, prefix=None):
    """The anim names to append to `actor`'s model ('who' = the ANIMS table); seated copies named
    prefix + 2 letters when `sit` is given. Our own gestures (`BUILT`) are built on `hrc` (default AAGB, Tifa)."""
    out = []
    for k, g in enumerate(used(gestures, actor)):
        a = ANIMS[who][g]
        if a in BUILT:
            a = (BUILT[a](ctx, hrc, a.split(".")[0], sit=sit) if BUILT[a] is _look else
                 BUILT[a](ctx, hrc or "AAGB.HRC", a.split(".")[0]))
        out.append(seated(ctx, hrc, a, sit, "%s%s" % (prefix, "ABCDEFGH"[k])) if sit else a)
    return out


def slots(gestures, actor, first, stand, animb):
    """{slot: ops}: each gesture once (ANIME1 waits in the actor's own slot), back to anim `stand`; `first` =
    the first gesture's anim index in the model."""
    return {SLOT + k: [animb, Op(bytes([0xA2, stand, 1])), Op(bytes([0xA3, first + k, 1])), asm.ret()]
            for k in range(len(used(gestures, actor)))}


def reqs(gestures, i, entity):
    """REQs (no wait) of line i's gestures; entity(actor) -> entity index."""
    return [Op(bytes([0x01, entity(a), 0xC0 | (SLOT + used(gestures, a).index(g))])) for a, g in gestures.get(i, [])]

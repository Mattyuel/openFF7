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
    "tifa": {"hips": "AQFE.yos", "ready": "FDCF.yos", "think": "BTCC.tak", "pose": "EPDF.yos", "lean": "ARFB.kei"},
    "jessie": {"arms": "CNJA.tor", "hips": "CNJE.tor", "point": "BXJA.yos"},
    "scarlet": {"hip": "EHBC.yos", "laugh": "FFDE.yos"},
    "elena": {"chest": "ETDC.kei", "shrug": "CGCF.aki", "hop": "AVFD.yos", "clasp": "EWBC.tak"},
}
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


def anims(ctx, gestures, actor, who, hrc=None, sit=None, prefix=None):
    """The anim names to append to `actor`'s model ('who' = the ANIMS table); seated copies named
    prefix + 2 letters when `sit` is given."""
    out = []
    for k, g in enumerate(used(gestures, actor)):
        a = ANIMS[who][g]
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

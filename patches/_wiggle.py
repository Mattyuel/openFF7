"""(user: "after head holds add a moment where cloud stops pulls out and wiggles his hips left and right a few
times") Cloud's pull-out wiggle for the parody films' head holds (684-687): one anim from frame 0 of his stroke
there (the pulled-back frame), built with `_besties_rig`: his hips eased back `PULL` (out of her mouth), then
`CYCLES` sways side to side (the root `SWAY` out, the pelvis rolled `ROLL`, the upper body countering so his
head stays over his feet), then eased back in; feet planted (two-bone IK). Played once (ANIME1 in `SLOT`,
REQEW'd by the director) after each hold's result, while she holds her pulled-back pose."""
import math

import _besties_rig as RG

PULL = 1.4                      # model units back (out)
SWAY, ROLL = 1.1, 13            # each way: root (model units), pelvis roll (degrees)
CYCLES = 3
COUNTER = 1.45                  # the waist's counter-roll x ROLL (checked: his head stays within ~0.3 of the stroke's)
IN_OUT, PER_CYCLE = 10, 14      # frames easing out / back in; frames a sway
SLOT = 7                        # the actors' script slot (Cloud: the wiggle; her: her pulled-back pose)


def build(ctx, hrc, src, name):
    """`name`.a from frame 0 of `src` (an anim on `hrc`): out, CYCLES sways, back in. Returns name + '.tor'."""
    base = RG.Rig(ctx, hrc, src)
    rg0 = RG.Rig(ctx, hrc, src).start(RG.basis(RG.LEFT, RG.UP))
    E0 = rg0.ends()
    feet = {s: E0[s + "_tibia"] for s in "lr"}
    frames = []
    n = 2 * IN_OUT + CYCLES * PER_CYCLE
    for k in range(n):
        if k < IN_OUT:
            out, sw = (1 - math.cos(math.pi * k / IN_OUT)) / 2, 0.0
        elif k >= n - IN_OUT:
            out, sw = (1 + math.cos(math.pi * (k - (n - IN_OUT)) / IN_OUT)) / 2, 0.0
        else:
            out, sw = 1.0, math.sin(2 * math.pi * (k - IN_OUT) / PER_CYCLE)
        rg = RG.Rig(ctx, hrc, src).start(RG.basis(RG.LEFT, RG.UP))
        rg.root = RG.add(rg.root, [SWAY * sw, 0.0, PULL * out])          # (model: +z = behind him)
        rg.pelvis(RG.lean(ROLL * sw))
        rg.waist(RG.lean(-ROLL * COUNTER * sw))
        for s, sx in (("l", 1), ("r", -1)):
            rg.ik(s + "_femur", s + "_tibia", feet[s], [sx * 0.25, 0.0, -1.0], keep_end=True)
        frames.append(rg.frame())
    return RG.save(ctx, name, base.base_name, frames)

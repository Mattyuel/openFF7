"""(user) Going up's own poses (684_going_up): Elena covering up (standing, head down and turned aside, one
arm across her chest, the other hand in front of her hips: built on Ruby as SRC + "A0" by `_dance_poses`
and retargeted onto her bare model), and her still on all fours (frame 0 of her movie dog stroke ZYC0) for
the crawl's stops and while Cloud is with Tifa. The rest are the movie's per-girl poses (670): Elena's dog
ZYC0-3 with Cloud's ZNC0-3 behind her, Tifa's head ZVJ0-3 (ZVJ9 her kneeling still) with Cloud's ZNJ0-3."""
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

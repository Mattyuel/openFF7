"""(user) Going There (690): Cloud's two new mounts over Tifa in the special scenes' insert (672: she on her knees,
chest down, ZVP<s>; Cloud squatting over her, ZNP<s>), built on the bare Cloud by the pose rig against her own
frames, one anim per insert speed (672 `INSERT_FRAMES` frames a stroke: frame 0 out, the middle in, her pelvis
rocking in time):

- side (XGS0-3): turned side-on, facing the camera, standing over her hips, his left foot planted on the bed
  behind her, his right foot up on her head; only his hips stroke (the root along his member's line, legs
  re-solved), hands on his hips, head down;
- plank (XGT0-3): turned round, facing her feet, the whole body pitched `PLANK_BOW` forward into a plank on her,
  hands planted on the bed ahead (arm IK every frame), legs out straight behind over her back; his hips flop up
  `FLOP` and drop back in.

Both are fitted once at her deepest frame (his tip `DEPTH` inside her entry, 672 ENTRY on her) and then stroked;
`build` returns the names, the pause stills (frame 0: XGS9 / XGT9) and the fit errors. Field placement: both
entities on 672's `BED_AT` spot, his DIR per mount (`DIRS`)."""
import math

import _besties_rig as RG
import _tickets_poses as TP

STROKE, DEPTH = 2.2, 1.0            # (model units) the side mount's stroke; how far in at the deepest
FLOP, PLANK_BOW = 2.4, 112          # the plank's hip lift at the top; its forward pitch (degrees)
SIDE_FOOT = (3.0, 1.6)              # his planted left foot: this far to his left and behind her entry
HEAD_FOOT_UP = 6.4                  # his right ankle this far above her head bone's end (user: his foot went
                                    # through her head: her hair's top is ~3.75 above it, his sole ~1.6 below the ankle)
HEAD_FOOT_BACK = 0.35               # ...and this share of the way back along her head bone (the hair's highest point)
SIDE_DOWN = 2.0                     # (user: "move cloud down the bed half a step") his root this much further
                                    # from her head along the bed, the tip kept at her entry by the fit
PLANK_LEGS = 0.25                   # his legs out behind, this much down (model y per unit back)
PLANK_HANDS = (0.9, 1.0)            # hands: this far either side of his shoulders and ahead of them
DIRS = {"side": 0x00, "plank": 0x40}    # his DIR (she faces 0xC0: -x); side faces the camera (-y)


def _tip(ctx, hb, rg, E=None):
    """(tip, base) of his member in model space for this rig."""
    from ff7 import fieldanim as fa
    base, tip = hb.member_ends(ctx.char_file("zcmp.p"))
    E = E or rg.ends()
    w = lambda p: [E["hip@"][k] + fa._vec(E["hip#"], list(p))[k] for k in range(3)]
    return w(tip), w(base)


def _hers(ctx, spot, gdir, cdir, anim, frame):
    """Her entry and the top of her head at `frame` of `anim`, in his model space (both entities at `spot`)."""
    e = TP.entry_points(ctx, "ZTFA.HRC", "abcd.a", anim)[frame]
    J = TP.joints(ctx, "ZTFA.HRC", anim)[frame]
    to_him = lambda p: TP._inv_off([TP._field(spot, gdir, p)[k] - spot[k] for k in range(3)], cdir)
    top = [J["head"][k] + HEAD_FOOT_BACK * (J["head@"][k] - J["head"][k]) for k in range(3)]
    return to_him(e), to_him(top)


def build(ctx, hb, spot, gdir, frames_per):
    """{mount: [anim names per speed]}, {mount: still name}, {mount: fit error} (model units)."""
    out, stills, errs = {}, {}, {}
    hrc = hb.CLOUD_BARE_HRC
    rg0 = RG.Rig(ctx, hrc, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
    ankle = max(rg0.ends()[s + "_tibia"][1] for s in "lr")              # (y down) his ankles over the bed
    for mount, cdir in DIRS.items():
        n0 = frames_per[0]
        entry, head = _hers(ctx, spot, gdir, cdir, "ZVP0", n0 // 2)

        def base_rig(x, mount=mount):
            rg = RG.Rig(ctx, hrc, "acfe.a").start(RG.basis(RG.LEFT, RG.UP))
            if mount == "plank":
                rg.pelvis(RG.bow(PLANK_BOW + x[3]))
                rg.neck(RG.bow(-40))                                    # (looking ahead, not at the bed)
            else:
                rg.pelvis(RG.chain(RG.bow(x[3]), RG.turn(x[4])))
                rg.waist(RG.bow(-x[3] + 8))
                rg.neck(RG.bow(28))                                     # (looking down at her)
            rg.root = RG.add(rg.root, x[:3])
            return rg

        def cost(rg):
            tip, base = _tip(ctx, hb, rg)
            md = RG.unit(RG.sub(tip, base))
            return math.dist(tip, RG.add(entry, RG.mul(md, DEPTH)))
        if mount == "plank":
            x0, st, bd = [0, 0, 0, 0], [1.0, 1.0, 1.0, 4], [(-8, 8), (-8, 8), (-8, 8), (-15, 15)]
        else:
            x0, st, bd = [0, 0, 0, 10, 0], [1.0, 1.0, 1.0, 5, 8], [(-8, 8), (-8, 8), (-8, 8), (-10, 50), (-40, 40)]
        x, deep = RG.fit(base_rig, cost, x0, st, rounds=5, bounds=bd)
        if mount == "side":                                     # half a step down the bed, still in her
            away = RG.unit([entry[0] - head[0], 0.0, entry[2] - head[2]])
            want = RG.add(deep.root, RG.mul(away, SIDE_DOWN))
            cost2 = lambda rg: cost(rg) * 6 + math.dist(rg.root, want)
            x, deep = RG.fit(base_rig, cost2, x, st, rounds=5, bounds=bd)
        errs[mount] = cost(deep)
        tip, bs = _tip(ctx, hb, deep)
        md = RG.unit(RG.sub(tip, bs))
        E = deep.ends()
        if mount == "side":
            plant = [entry[0] + SIDE_FOOT[0], ankle, entry[2] + SIDE_FOOT[1]]
            on_head = [head[0], head[1] - HEAD_FOOT_UP, head[2]]
        else:
            hands = {s: [E[s + "_uparm@"][0] + sx * PLANK_HANDS[0], ankle, E[s + "_uparm@"][2] - PLANK_HANDS[1]]
                     for s, sx in (("l", 1), ("r", -1))}
        names = []
        for s, n in enumerate(frames_per):
            frames = []
            for t in range(n):
                e = (1 - math.cos(2 * math.pi * t / n)) / 2                    # 0 out .. 1 in (672's phase)
                rg = base_rig(x)
                if mount == "side":
                    rg.root = RG.sub(rg.root, RG.mul(md, STROKE * (1 - e)))
                    rg.ik("l_femur", "l_tibia", plant, [0.6, -0.2, -1.0])
                    rg.ik("r_femur", "r_tibia", on_head, [-0.4, -0.6, -1.0])
                    rg.aim("r_foot", RG.unit([-0.35, 0.0, -1.0]))              # (the sole level on her head)
                    Et = rg.ends()
                    for sd, sx in (("l", 1), ("r", -1)):                      # hands on his hips
                        w = RG.add(Et[sd + "_femur@"], [sx * 1.3, -2.1, 0.3])
                        rg.ik(sd + "_uparm", sd + "_foarm", w, [sx * 1.0, 0.0, 0.4], keep_end=False)
                else:
                    # the flop: the body turned about his shoulders (hands planted) until the hips are FLOP up
                    E1 = rg.ends()
                    sh = RG.mul(RG.add(E1["l_uparm@"], E1["r_uparm@"]), 0.5)
                    arm = math.dist(sh, rg.root)
                    rg.pelvis(RG.bow(math.degrees(FLOP * (1 - e) / arm)))
                    E2 = rg.ends()
                    rg.root = RG.add(rg.root, RG.sub(sh, RG.mul(RG.add(E2["l_uparm@"], E2["r_uparm@"]), 0.5)))
                    for sd in "lr":                                               # legs straight out behind
                        rg.aim(sd + "_femur", RG.unit([0.0, PLANK_LEGS, 1.0]))
                        rg.aim(sd + "_tibia", RG.unit([0.0, PLANK_LEGS, 1.0]))
                    for sd, sx in (("l", 1), ("r", -1)):
                        rg.ik(sd + "_uparm", sd + "_foarm", hands[sd], [sx * 1.0, -0.3, 0.6])
                frames.append(rg.frame())
            names.append(RG.save(ctx, "XG%s%d" % ("ST"[mount == "plank"], s), "acfe.a", frames))
        out[mount] = names
        stills[mount] = TP.still(ctx, names[0].split(".")[0], "XG%s9" % "ST"[mount == "plank"])
    return out, stills, errs

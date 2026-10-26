"""(user: Besties, round 2: "get the positions right so that characters don't clip through each other, the
movements organic and realistic with exaggerated hip movement ... the biggest issues are the character models
overlapping and clipping through each other, and the ambiguous positions") Every position built here with the
pose rig (`_besties_rig`) on the bare models themselves (Cloud ZCLA, Tifa ZTFA, Aerith ZAEA), all three in one
"scene" across the bed's left edge: the room's camera looks down ~45 degrees from the foot, so the line from the
bed out over the rug (field ~ -x) runs across the screen and everyone is seen side-on, apart, left to right.
Contacts (mouths, entries, hands, knees) are solved per frame (`fit`: small coordinate descent), so nobody passes
through anybody; checked on offline renders and a mesh-intersection check (scratch).

Scene space = the model space of an entity on the left edge's middle E (floor) facing out over the rug (DIR DN):
s out to the rug (model -z), a along the edge to the head (model -x), h up (model -y); P(s, a, h) -> model.
Positions (each one stroke = n frames, n = FRAMES; the girls' hips rocked hard, the head lagging the hips):
  edge   Tifa sits on the edge leaning back, her legs over Cloud's shoulders; Cloud kneels on the rug, his mouth
         on her; Aerith sits behind Tifa, legs either side, Tifa's head on her right shoulder, Aerith's mouth at
         her temple, her hands on Tifa's breasts; Tifa's left hand on his head, her right over Aerith's hand.
  ride   Cloud on his back across the bed, knees over the edge, feet on the rug; Tifa rides him facing his head;
         Aerith kneels astride his face facing Tifa (knees wide by his head); they hold hands at arm's length.
  lick   Aerith sits on the edge leaning back on her hands, legs apart; Tifa stands bent at the hips, her mouth
         on Aerith; Cloud stands behind Tifa, hands on her hips.
  share  On the rug: Cloud stands facing the bed; the girl in front kneels, her mouth on him (bobbing with him);
         the other kneels behind him, arms round his waist, her cheek on his back; P = who's in front.
  stack  Tifa on her back across the bed, hips at the edge, legs round Cloud's waist; Aerith on her knees and
         elbows over her the other way (her hips over Tifa's face); Cloud stands at the edge: P 0 in Tifa
         (Aerith licking her), P 1 in Aerith's mouth just above.
Names: Cloud YB, Tifa YC, Aerith YD + the position letter (E R L F B S U; Cloud's share G = Aerith in front)
+ the speed 0-3; holds (share): 8 deep held, 7 tapping out (30 frames), 9 pulled back."""
import math

from ff7 import fieldanim as fa
import _besties_rig as RG
from _besties_rig import (Rig, basis, bow, turn, lean, chain, ease, add, sub, mul, unit, lerp, face_pt, entry,
                          axis_of, front, hips_of, hang_hair, kneel, stand_feet, fit)

U = 3.41
FRAMES = (20, 15, 11, 8)
CLOUD, TIFA, AERITH = ("zcla.hrc", "acfe.a"), ("ztfa.hrc", "abcd.a"), ("zaea.hrc", "avbf.a")
PREFIX = {"cloud": "YB", "tifa": "YC", "aerith": "YD"}
SEAT_H = 4.5                    # (field) sitting: the hip joints this far above the bed's top
SEAT_IN, SEAT_OUT = 14, 18      # the intro (dressed, sitting on the edge): hips this far onto it, the XYZI this far out
TOP = 47                        # set by build() from the data

# edge: Tifa's sit / rock, Cloud's kneel, Aerith behind
EDGE_TIFA = dict(tilt=-12, rock=18, back=14, head=10, hroll=24, slide=1.6, seat_s=-5)
EDGE_CLOUD = dict(tilt=6, spread=16, look=28, nod=14, out=0.7, push=1.6)
EDGE_AERITH = dict(spread=42, sway=6, side=2.1, sep=3.4)
# ride
RIDE = dict(hips_s=-20, lift=3.0, spread=34, rock=20, slide=1.8, lean=-6, alean=4, arock=16)
# lick
LICK_AERITH = dict(tilt=-10, rock=14, back=26, head=18, spread=40, lift=14, slide=1.2, shin_out=0.35, seat_s=-5)
LICK_TIFA_PUSH = 16             # her hips rolling back into him (degrees)
# share
SHARE_SPOT = 60.0               # (field) Cloud stands this far out on the rug
SHARE_SWAY = 10                 # the girls' hips side to side (degrees)
# stack
STACK_TIFA_S = -5               # her hips this far onto the bed
STACK_V = 38                    # her thighs apart (each, degrees)
AERITH_TILT = (32, 12)          # Aerith's head turned aside (P 0 licking / P 1 on him)


def _P(s, a, h):
    return [-a / U, -h / U, -s / U]


def _S(m):
    return (-m[2] * U, -m[0] * U, -m[1] * U)


def _new(ctx, who, body):
    hrc, stand = {"cloud": CLOUD, "tifa": TIFA, "aerith": AERITH}[who]
    return Rig(ctx, hrc, stand).start(body)


def _standing(ctx, who, facing, stance=0.0):
    rg = _new(ctx, who, turn(facing))
    E_ = rg.ends()
    return rg, {s: add(E_[s + "_tibia"], fa._vec(rg.G, [sx * stance / U, 0.0, 0.0])) for s, sx in (("l", 1), ("r", -1))}


def _tip(ctx, rg, E_=None):
    import importlib
    hb = importlib.import_module("620_honey_bee")
    E_ = E_ or rg.ends()
    if not hasattr(_tip, "ends"):
        _tip.ends = hb.member_ends(ctx.char_file("zcmp.p"))[1]
    return add(E_["hip@"], fa._vec(E_["hip#"], _tip.ends))


def sitting(ctx, name, hrc, stand):
    """The intro: sitting on an edge (660 `_ledge`), the root moved back (SEAT_IN + SEAT_OUT) so an XYZI on the
    floor in front of the edge (at the seat's height) puts her hips on it."""
    import importlib
    dt = importlib.import_module("660_dates")
    dt._ledge(ctx, name + ".tor", hrc.lower(), stand)
    A = fa.Anim(ctx.char_file(name.lower() + ".a"))
    back = (SEAT_IN + SEAT_OUT) / U
    A.frames = [(rr, [rp[0], rp[1], rp[2] + back], rots) for rr, rp, rots in A.frames]
    ctx.char_file(name.lower() + ".a", A.build())
    return name + ".tor"


# ---- edge -----------------------------------------------------------------------------------------------
def _sit_edge(ctx, who, t, c):
    """Sitting on the edge facing the rug, leaning back, hips rolling up into him at the deepest."""
    rg = _new(ctx, who, basis(RG.LEFT, RG.UP))
    pk = ease(t)
    rg.pelvis(bow(c["tilt"] - c["rock"] * pk))
    rg.waist(bow(-c["back"] + c["rock"] * 0.35 * pk))
    lag = ease((t - 0.12) % 1)
    rg.neck(chain(bow(-6 - c["head"] * lag), lean(-c.get("hroll", 0) + 5 * math.sin(2 * math.pi * t))))
    if "spread" in c:
        sp, el = math.radians(c["spread"] + 5 * pk), math.radians(c["lift"] + 4 * pk)
        for s, sx in (("l", 1), ("r", -1)):
            rg.aim(s + "_femur", [sx * math.sin(sp) * math.cos(el), -math.sin(el), -math.cos(sp) * math.cos(el)])
            rg.aim(s + "_tibia", unit([sx * c.get("shin_out", 0.2), 1.0, -0.15]))
            rg.aim(s + "_foot", unit([sx * 0.15, 0.7, -0.6]))
    else:
        for s, sx in (("l", 1), ("r", -1)):                   # (provisional: re-aimed onto his shoulders)
            rg.aim(s + "_femur", unit([sx * 0.5, -0.2, -1.0]))
    hang_hair(rg)
    rg.root = add(rg.root, sub(_P(c["seat_s"] + c["slide"] * pk, 0, TOP + SEAT_H), hips_of(rg)))
    return rg


def _edge(ctx, n):
    tb = [_sit_edge(ctx, "tifa", k / n, EDGE_TIFA) for k in range(n)]
    c = EDGE_CLOUD
    cl = []
    for k in range(n):
        t = k / n
        tgt = add(entry(tb[k]), [0, -0.1, -c["push"]])
        rg = _new(ctx, "cloud", turn(180))
        kneel(rg, c["tilt"], c["spread"], -1.6 / U)
        nod = -c["look"] + c["nod"] * ease((t - 0.08) % 1)
        best = None
        for th2 in range(0, 160):
            r2 = rg.copy()
            r2.waist(bow(th2 / 2))
            r2.neck(bow(nod))
            m = face_pt(r2, out=c["out"])
            if best is None or abs(m[1] - tgt[1]) < best[0]:
                best = (abs(m[1] - tgt[1]), th2 / 2, m)
        rg.waist(bow(best[1]))
        rg.neck(bow(nod))
        m = best[2]
        rg.root = add(rg.root, [tgt[0] - m[0], 0.0, tgt[2] - m[2]])
        cl.append(rg)
    for k in range(n):                                        # her legs over his shoulders, shins down his back
        ec = cl[k].ends()
        for s, sx, his in (("l", 1, "r"), ("r", -1, "l")):
            knee = add(lerp(ec[his + "_uparm@"], ec[his + "_collar@"], 0.3), [0, -1.6, -0.6])
            tb[k].aim(s + "_femur", sub(knee, tb[k].ends()[s + "_femur@"]))
            tb[k].aim(s + "_tibia", unit([sx * 0.35, 0.8, -1.0]))
            tb[k].aim(s + "_foot", unit([sx * 0.2, 0.8, -0.6]))
        et = tb[k].ends()
        hipf = front(tb[k], "hip", et)
        for s, sx, her in (("l", 1, "r"), ("r", -1, "l")):    # his hands round her thighs on her hips
            out_ = unit(sub(et[her + "_femur@"], et["hip@"]))
            tp = add(add(lerp(et[her + "_femur@"], et[her + "_femur"], 0.3), mul(out_, 0.9)), mul(hipf, 1.5))
            cl[k].ik(s + "_uparm", s + "_foarm", tp, fa._vec(cl[k].G, [sx * 1.0, 0.6, 0.2]))
            cl[k].aim(s + "_hand", sub(add(et["hip@"], mul(hipf, 1.2)), cl[k].ends()[s + "_foarm"]))
    # Aerith sitting behind her
    ae, x0 = [], None
    a = EDGE_AERITH
    for k in range(n):
        t, et = k / n, tb[k].ends()
        pk = ease(t)
        hips_t = hips_of(tb[k], et)
        tgt = add(lerp(et["head@"], et["head"], 0.5), mul(axis_of(tb[k], "head", RG.LEFT, et), a["side"]))
        ht = lerp(et["head@"], et["head"], 0.4)

        def build(x):
            gap, wb, wl, nb, nl, nt = x
            rg = _new(ctx, "aerith", basis(RG.LEFT, RG.UP))
            rg.pelvis(chain(bow(-4 + 3 * pk), lean(a["sway"] * math.sin(2 * math.pi * (t - 0.1)))))
            rg.waist(chain(bow(wb), lean(wl)))
            rg.neck(chain(turn(nt), bow(nb), lean(nl)))
            sp, el = math.radians(a["spread"]), math.radians(14)
            for s, sx in (("l", 1), ("r", -1)):
                rg.aim(s + "_femur", [sx * math.sin(sp) * math.cos(el), -math.sin(el), -math.cos(sp) * math.cos(el)])
                rg.aim(s + "_tibia", unit([sx * 0.3, 1.0, -0.2]))
                rg.aim(s + "_foot", unit([sx * 0.2, 0.7, -0.6]))
            hang_hair(rg)
            hp = hips_of(rg)
            rg.root = add(rg.root, sub([hips_t[0], _P(0, 0, TOP + SEAT_H)[1], hips_t[2] + gap], hp))
            return rg

        def cost(r):
            E_ = r.ends()
            hc = lerp(E_["head@"], E_["head"], 0.4)
            return (math.dist(face_pt(r, out=0.7, E_=E_), tgt) + 4 * max(0.0, a["sep"] - math.dist(hc, ht)) +
                    4 * max(0.0, 2.3 - math.dist(E_["r_collar"], ht)) + 4 * max(0.0, 2.3 - math.dist(E_["r_uparm"], ht)) +
                    2 * max(0.0, 3.0 - math.dist(E_["chest"], ht)))
        B = [(5.0, 9.0), (-15, 25), (-20, 25), (-20, 45), (-30, 30), (-50, 50)]
        if x0 is None:
            x0, ra = fit(build, cost, [6.5, 0.0, 0.0, 15.0, 0.0, -15.0], [1.0, 6.0, 6.0, 8.0, 8.0, 10.0], bounds=B)
        else:
            _, ra = fit(build, cost, x0, [0, 3.0, 3.0, 4.0, 4.0, 5.0], rounds=2, bounds=B)
        for s, sx in (("l", 1), ("r", -1)):                   # her hands on Tifa's breasts
            br = add(lerp(et[s + "_chest@"], et[s + "_chest"], 0.62), mul(front(tb[k], "chest", et), 1.6))
            ra.ik(s + "_uparm", s + "_foarm", add(br, [0, -0.4, 0.4]), [sx * 1.0, 0.5, 0.6])
            ra.aim(s + "_hand", sub(br, ra.ends()[s + "_foarm"]))
        ae.append(ra)
        ea, ec = ra.ends(), cl[k].ends()
        tb[k].ik("l_uparm", "l_foarm", add(lerp(ec["head@"], ec["head"], 0.45),
                                            mul(axis_of(cl[k], "head", RG.UP, ec), 2.6)), [1.0, -0.3, 0.3])
        tb[k].ik("r_uparm", "r_foarm", add(ea["r_foarm"], [0, -0.9, 0]), [-1.0, 0.6, 0.3])
    return {"cloud": cl, "tifa": tb, "aerith": ae}


# ---- ride -----------------------------------------------------------------------------------------------
def _astride(ctx, who, t, facing, tilt, spread, lean_, rock, shin_out=0.05, phase=0.0):
    pk = ease((t + phase) % 1)
    rg = _new(ctx, who, turn(facing))
    rg.pelvis(chain(bow(-rock * (pk - 0.5)), lean(rock * 0.3 * math.sin(2 * math.pi * (t + phase)))))
    rg.waist(bow(lean_ + rock * 0.6 * (pk - 0.5)))
    rg.neck(bow(-8 + 10 * ease((t + phase - 0.1) % 1)))
    kneel(rg, tilt, spread, _P(0, 0, TOP + 1.6)[1], shin_out=shin_out)
    hang_hair(rg)
    return rg


def _ride(ctx, n):
    R = RIDE
    cl = []
    for k in range(n):
        pk = ease(k / n)
        rg = _new(ctx, "cloud", basis([1.0, 0.0, 0.0], [0.0, 0.0, 1.0]))      # on his back, head to -s
        rg.pelvis(bow(-10 * pk))
        rg.neck(bow(8))
        rg.root = add(rg.root, sub(_P(R["hips_s"], 0, TOP + 5.0 + R["lift"] * pk), hips_of(rg)))
        for s, sx in (("l", 1), ("r", -1)):                                 # knees over the edge, feet on the rug
            rg.ik(s + "_femur", s + "_tibia", _P(4, -sx * 7.0, 2.0), [0.0, -0.4, -1.0], keep_end=False)
            rg.aim(s + "_foot", unit([sx * 0.1, 0.1, -1.0]))
        cl.append(rg)

    def solve(who, facing, target_h, var, lo, hi, **kw):
        best = None
        for v in range(lo, hi):
            kw[var] = v
            h = entry(_astride(ctx, who, 0, facing, **kw))[1]
            if best is None or abs(h - target_h) < best[0]:
                best = (abs(h - target_h), v)
        return best[1]
    tt = solve("tifa", 180, _tip(ctx, cl[0])[1] + 0.3, "tilt", -10, 60, spread=R["spread"], lean_=R["lean"], rock=R["rock"])
    ta = solve("aerith", 0, face_pt(cl[0], out=0.8)[1] - 0.6, "spread", 20, 80, tilt=4, lean_=R["alean"],
               rock=R["arock"], shin_out=0.45)
    tf, ae = [], []
    for k in range(n):
        pk = ease(k / n)
        r = _astride(ctx, "tifa", k / n, 180, tt, R["spread"], R["lean"], R["rock"])
        r.root = add(r.root, sub(add(_tip(ctx, cl[k]), [0, -0.3, 0]), entry(r)))
        r.root[2] += R["slide"] / U * (pk - 0.5)
        tf.append(r)
        r = _astride(ctx, "aerith", k / n, 0, 4, ta, R["alean"], R["arock"], shin_out=0.45, phase=0.5)
        r.root = add(r.root, sub(add(face_pt(cl[k], out=0.8), [0, -0.6, 0]), entry(r)))
        ae.append(r)
    for k in range(n):
        et, ea = tf[k].ends(), ae[k].ends()
        for s_t, s_a in (("l", "r"), ("r", "l")):                           # hands joined between them
            mid = add(lerp(et[s_t + "_uparm@"], ea[s_a + "_uparm@"], 0.5), [0, 2.2, 0])
            tf[k].ik(s_t + "_uparm", s_t + "_foarm", mid, [1 if s_t == "l" else -1, 0.6, 0.0])
            ae[k].ik(s_a + "_uparm", s_a + "_foarm", mid, [1 if s_a == "l" else -1, 0.6, 0.0])
        for s, her in (("l", "r"), ("r", "l")):                             # his hands on her hips
            out_ = unit(sub(et[her + "_femur@"], et["hip@"]))
            tp = add(add(lerp(et[her + "_femur@"], et[her + "_femur"], 0.12), mul(out_, 2.3)), [0, -1.4, 0])
            cl[k].ik(s + "_uparm", s + "_foarm", tp, [0.0, 1.0, 0.0])
            cl[k].aim(s + "_hand", sub(et[her + "_femur"], et[her + "_femur@"]))
    return {"cloud": cl, "tifa": tf, "aerith": ae}


# ---- lick -----------------------------------------------------------------------------------------------
def _lick(ctx, n):
    ae = [_sit_edge(ctx, "aerith", k / n, LICK_AERITH) for k in range(n)]
    for rg in ae:                                                           # her hands back on the bed
        ea = rg.ends()
        for s, sx in (("l", 1), ("r", -1)):
            hand = add(ea["hip@"], [sx * 3.0, 0, 0])
            hand = [hand[0], _P(0, 0, TOP + 1.5)[1], hand[2] + 4.2]
            rg.ik(s + "_uparm", s + "_foarm", hand, [sx * 0.5, -0.2, 1.0])
            rg.aim(s + "_hand", [sx * 0.2, 0.3, 1.0])
    tf, x0 = [], None
    for k in range(n):
        t = k / n
        pk = ease((t + 0.5) % 1)
        sw = math.sin(2 * math.pi * (t + 0.5))
        target = add(entry(ae[k]), [0, 0.1, -1.0])

        def build(x):
            pb, drop, ds, nb = x
            rg, feet = _standing(ctx, "tifa", 180, stance=4.0)
            rg.root = add(rg.root, [0, drop / U, 0])
            rg.pelvis(chain(bow(pb + LICK_TIFA_PUSH * pk), lean(7 * sw)))
            rg.waist(chain(bow(-12 + 4 * pk), lean(-4 * sw)))
            rg.neck(bow(nb))
            hang_hair(rg, 0.1)
            sh = fa._vec(rg.G, [0, 0, -ds / U])
            rg.root = add(rg.root, sh)
            stand_feet(rg, {s: add(v, sh) for s, v in feet.items()})
            return rg
        cost = lambda r: math.dist(face_pt(r, out=0.6), target)
        B = [(30, 100), (0, 14), (-60, 60), (-60, 10)]
        if x0 is None:
            x0, r = fit(build, cost, [70, 4, 0, -30], [10, 3, 10, 10], bounds=B)
        else:
            _, r = fit(build, cost, x0, [4, 0, 0, 5], rounds=2, bounds=B)
        ea = ae[k].ends()
        for s, sx, her in (("l", 1, "r"), ("r", -1, "l")):                  # her hands on Aerith's thighs
            tp = add(lerp(ea[her + "_femur@"], ea[her + "_femur"], 0.65), [0, -1.3, 0])
            r.ik(s + "_uparm", s + "_foarm", tp, [sx * 1.0, 0.5, 0.2])
            r.aim(s + "_hand", sub(ea[her + "_femur@"], ea[her + "_femur"]))
        tf.append(r)
    cl, cx = [], None
    for k in range(n):
        pk = ease(k / n)
        target = add(entry(tf[k]), [0, 0, 0.4])

        def build(x, pk=pk):
            drop, ds = x
            rg, feet = _standing(ctx, "cloud", 180, stance=6.0)
            rg.root = add(rg.root, [0, drop / U, 0])
            rg.pelvis(bow(-6 - 8 * pk))
            rg.waist(bow(4 + 6 * pk))
            rg.neck(bow(14))
            rg.root = add(rg.root, fa._vec(rg.G, [0, 0, -ds / U]))
            fd = ds if cx is None else cx[1]
            stand_feet(rg, {s: add(v, fa._vec(rg.G, [0, 0, -fd / U])) for s, v in feet.items()})
            return rg
        cost = lambda r: math.dist(_tip(ctx, r), target)
        if cx is None:
            cx, r = fit(build, cost, [6, 0], [3, 10], bounds=[(-4, 20), (-80, 80)])
        else:
            _, r = fit(build, cost, cx, [3, 10], bounds=[(-4, 20), (-80, 80)])
        et = tf[k].ends()
        for s, sx in (("l", -1), ("r", 1)):                                 # hands on her hips
            tp = add(add(et[s + "_femur@"], [0, -1.8, 0]), mul(unit(sub(et[s + "_femur@"], et["hip@"])), 1.4))
            r.ik(s + "_uparm", s + "_foarm", tp, [-sx * 1.0, 0.6, -0.2])
        cl.append(r)
    return {"cloud": cl, "tifa": tf, "aerith": ae}


# ---- share ----------------------------------------------------------------------------------------------
def _share_cloud(ctx, t):
    pk = ease(t)
    rg, feet = _standing(ctx, "cloud", 180, stance=5.0)
    sh = fa._vec(rg.G, [0, 0, SHARE_SPOT / U])
    rg.root = add(rg.root, sh)
    rg.root = add(rg.root, fa._vec(rg.G, [0, 1.2 / U, -1.5 * pk / U]))
    rg.pelvis(bow(-5 - 7 * pk))
    rg.waist(bow(6 + 5 * pk))
    rg.neck(bow(22))
    stand_feet(rg, {s: add(v, sh) for s, v in feet.items()})
    return rg


def _kneel_front(ctx, who, t, target, x0=None, sway=SHARE_SWAY):
    sw = math.sin(2 * math.pi * t)

    def build(x):
        ds, wb, nb = x
        rg = _new(ctx, who, turn(0))
        rg.pelvis(chain(lean(sway * sw), turn(0.6 * sway * sw)))
        rg.waist(chain(bow(wb), lean(-0.5 * sway * sw)))
        rg.neck(bow(nb))
        kneel(rg, 4, 20, _P(0, 0, 1.6)[1])
        hang_hair(rg, 0.3)
        rg.root = add(rg.root, fa._vec(rg.G, [0, 0, -ds / U]))
        return rg
    cost = lambda r: math.dist(face_pt(r, out=0.7), target)
    B = [(-20, 80), (-20, 60), (-40, 40)]
    return fit(build, cost, x0 or [30, 10, 0], [8, 8, 8], bounds=B, rounds=4 if x0 is None else 2)


def _share(ctx, n):
    cl = [_share_cloud(ctx, k / n) for k in range(n)]
    out = {"_cloud": cl}
    back_dir = fa._vec(cl[0].G, [0, 0, -1.0])                 # his forward: out of her mouth, towards her
    deep = add(_tip(ctx, cl[n // 2]), mul(back_dir, 0.6))
    for who in ("tifa", "aerith"):
        x0, _ = _kneel_front(ctx, who, 0.5, deep)
        fr = []
        for k in range(n):
            pk = ease(k / n)
            tg = add(_tip(ctx, cl[k]), mul(back_dir, 0.6 + 1.8 * (1 - pk)))
            _, r = _kneel_front(ctx, who, k / n, tg, x0)
            ec = cl[k].ends()
            for s, sx, his in (("l", 1, "r"), ("r", -1, "l")):                  # hands on his thighs
                tp = add(lerp(ec[his + "_femur@"], ec[his + "_femur"], 0.45), mul(back_dir, 1.6))
                r.ik(s + "_uparm", s + "_foarm", tp, [sx * 1.0, 0.6, 0.3])
            fr.append(r)
        out[who + "_front"] = fr
        out[who + "_x0"] = x0
        bk = []
        for k in range(n):
            sw = math.sin(2 * math.pi * k / n)
            ec = cl[k].ends()
            tgt = add(lerp(ec["hip@"], ec["chest@"], 0.55), mul(back_dir, -3.4))

            def build(x, sw=sw):
                ds, wb, nb = x
                rg = _new(ctx, who, turn(180))
                rg.pelvis(chain(lean(SHARE_SWAY * sw), turn(0.5 * SHARE_SWAY * sw)))
                rg.waist(chain(bow(wb), lean(-0.4 * SHARE_SWAY * sw)))
                rg.neck(chain(bow(nb), lean(-25)))
                kneel(rg, 0, 18, _P(0, 0, 1.6)[1])
                hang_hair(rg, 0.3)
                rg.root = add(rg.root, fa._vec(rg.G, [0, 0, -ds / U]))
                return rg
            cost = lambda r: math.dist(face_pt(r, out=0.9), tgt)
            _, r = fit(build, cost, [-75, 5, 10], [8, 8, 8], bounds=[(-120, -40), (-20, 50), (-30, 40)])
            for s, sx, his in (("l", 1, "l"), ("r", -1, "r")):                  # arms round to his front
                tp = add(add(ec[his + "_femur@"], mul(back_dir, 1.6)), [0, -1.0, 0])
                r.ik(s + "_uparm", s + "_foarm", tp, [sx * 1.0, 0.4, -0.2])
            bk.append(r)
        out[who + "_back"] = bk
    # his hands on the front girl's head: one Cloud per front girl
    for who, key in (("tifa", "cloud_t"), ("aerith", "cloud_a")):
        cs = []
        for k in range(n):
            c = cl[k].copy()
            fr = out[who + "_front"][k]
            eh = fr.ends()
            hc = lerp(eh["head@"], eh["head"], 0.55)
            side = axis_of(fr, "head", RG.LEFT, eh)
            for s_, sx in (("l", -1), ("r", 1)):
                c.ik(s_ + "_uparm", s_ + "_foarm", add(add(hc, mul(side, sx * 2.0)), [0, -1.2, 0]),
                     fa._vec(c.G, [(1 if s_ == "l" else -1) * 1.0, 0.8, 0.2]))
            cs.append(c)
        out[key] = cs
    return out


def _share_holds(ctx, sh, n):
    """The front girl's tapping out (30 frames: pulling back, hips wriggling, hands pushing his thighs)."""
    cl = sh["_cloud"]
    back_dir = fa._vec(cl[0].G, [0, 0, -1.0])
    out = {}
    for who in ("tifa", "aerith"):
        fr = []
        for k in range(30):
            u = k / 29
            tg = add(_tip(ctx, cl[n // 2]), mul(back_dir, 0.6 + 0.9 * math.sin(math.pi * u)))
            _, r = _kneel_front(ctx, who, (3 * u) % 1, tg, sh[who + "_x0"], sway=SHARE_SWAY * 1.8)
            ec = cl[n // 2].ends()
            for s, sx, his in (("l", 1, "r"), ("r", -1, "l")):
                tp = add(lerp(ec[his + "_femur@"], ec[his + "_femur"], 0.4), mul(back_dir, 1.0 + 0.6 * math.sin(math.pi * u)))
                r.ik(s + "_uparm", s + "_foarm", tp, [sx * 1.0, 0.6, 0.3])
            fr.append(r)
        out[who] = fr
    return out


# ---- stack ----------------------------------------------------------------------------------------------
def _stack(ctx, n):
    tf = []
    for k in range(n):
        pk = ease(k / n)
        rg = _new(ctx, "tifa", basis([1.0, 0.0, 0.0], [0.0, 0.0, 1.0]))     # on her back, head to -s
        rg.pelvis(bow(-14 * pk))
        rg.neck(bow(28 + 6 * ease((k / n - 0.1) % 1)))
        hang_hair(rg, along=[0.0, 0.0, 1.0])
        rg.root = add(rg.root, sub(_P(STACK_TIFA_S + 1.0 * pk, 0, TOP + 4.6), hips_of(rg)))
        for s, sx in (("l", 1), ("r", -1)):
            E_ = rg.ends()
            rg.ik(s + "_uparm", s + "_foarm", add(E_[s + "_uparm@"], [sx * 4.0, -0.2, 3.5]), [0, -1.0, 0])
        tf.append(rg)

    def cloud_at(t, target, x0=None):
        pk = ease(t)

        def build(x):
            lift, ds = x
            rg, feet = _standing(ctx, "cloud", 180, stance=6.0)
            rg.root = add(rg.root, add(fa._vec(rg.G, [0, 0, -ds / U]), [0, -lift / U, 0]))
            rg.pelvis(bow(-6 - 8 * pk))
            rg.waist(bow(-16 + 4 * pk))
            rg.neck(bow(30))
            fd = ds if x0 is None else x0[1]
            stand_feet(rg, {s: add(add(v, fa._vec(rg.G, [0, 0, -fd / U])), [0, -max(0.0, lift) / U, 0])
                            for s, v in feet.items()})
            if lift > 0:
                for s in "lr":
                    rg.aim(s + "_foot", fa._vec(rg.G, unit([0, 0.8, -1.0])))
            return rg
        cost = lambda r: math.dist(_tip(ctx, r), target)
        return fit(build, cost, [0, -10] if x0 is None else list(x0), [2, 6] if x0 is None else [2, 0],
                   bounds=[(-8, 12), (-60, 40)])

    def aerith_69(t, target, x0, tilt_):
        sw = math.sin(2 * math.pi * t)

        def build(x):
            ds, hb_, nb, kt = x
            rg = _new(ctx, "aerith", turn(0))
            rg.pelvis(chain(bow(hb_), lean(12 * sw)))
            rg.waist(bow(10))
            rg.neck(chain(lean(tilt_), bow(nb)))
            kneel(rg, kt, 36, _P(0, 0, TOP + 1.6)[1])
            hang_hair(rg, 0.0)
            rg.root = add(rg.root, fa._vec(rg.G, [0, 0, -ds / U]))
            return rg
        cost = lambda r: math.dist(face_pt(r, out=0.6), target)
        B = [(-90, 0), (40, 110), (-60, 40), (-30, 30)]
        return fit(build, cost, x0 or [-40, 75, -20, -10], [8, 10, 10, 8], bounds=B, rounds=4 if x0 is None else 2)

    en0 = entry(tf[n // 2])
    cx0, _ = cloud_at(0.5, add(en0, [0, 0, -0.3]))
    cx1, _ = cloud_at(0.5, add(en0, [0, -2.2, -0.6]))
    cl0, cl1, ae0, ae1, ax0, ax1 = [], [], [], [], None, None
    for k in range(n):
        en = entry(tf[k])
        _, c0 = cloud_at(k / n, add(en, [0, 0, -0.3]), cx0)
        _, c1 = cloud_at(k / n, add(en, [0, -2.2, -0.6]), cx1)
        cl0.append(c0)
        cl1.append(c1)
        belly = add(add(en, mul(front(tf[k], "hip"), 0.9)), [0, 0, 2.6])
        ax0, a0 = aerith_69(k / n, belly, ax0, AERITH_TILT[0])
        ax1, a1 = aerith_69(k / n, add(_tip(ctx, c1), [0, 0, 0.3]), ax1, AERITH_TILT[1])
        ae0.append(a0)
        ae1.append(a1)
    for k in range(n):
        ec = cl0[k].ends()                                                  # her legs round his waist
        bk = fa._vec(cl0[k].G, [0, 0, 1.0])
        for s, sx, his in (("l", 1, "r"), ("r", -1, "l")):
            ank = add(add(lerp(ec["hip@"], ec[his + "_femur@"], 0.4), mul(bk, 3.2)), [0, -0.6, 0])
            tf[k].ik(s + "_femur", s + "_tibia", ank, [sx * 1.0, -1.0, 0.0])
            tf[k].aim(s + "_foot", sub(ank, tf[k].ends()[s + "_femur"]))
        et = tf[k].ends()
        for lst in (ae0, ae1):                                              # Aerith's forearms beside Tifa's hips
            for s, sx in (("l", 1), ("r", -1)):
                tp = add(et[s + "_femur@"], [sx * 3.4, 0, 1.0])
                tp[1] = _P(0, 0, TOP + 2.5)[1]
                lst[k].ik(s + "_uparm", s + "_foarm", tp, [sx * 0.6, -0.6, 0.6])
                lst[k].aim(s + "_hand", [sx * 0.1, 0.2, -1.0])
        for lst in (cl0, cl1):                                              # his hands at her knees
            for s, sx in (("l", -1), ("r", 1)):
                her = "r" if s == "l" else "l"
                tp = add(add(lerp(et[her + "_femur@"], et[her + "_femur"], 0.9), [0, -1.2, 0]),
                         mul(unit(sub(et[her + "_femur@"], et["hip@"])), 1.2))
                lst[k].ik(s + "_uparm", s + "_foarm", tp, fa._vec(lst[k].G, [1 if s == "l" else -1, 0.8, 0.0]))
    return {"tifa": tf, "cloud": cl0, "cloud1": cl1, "aerith": ae0, "aerith1": ae1}


# ---- assembly -------------------------------------------------------------------------------------------
BUILDERS = {"edge": _edge, "ride": _ride, "lick": _lick, "share": _share, "stack": _stack}
LETTER = {("edge", "cloud"): "E", ("edge", "tifa"): "E", ("edge", "aerith"): "E",
          ("ride", "cloud"): "R", ("ride", "tifa"): "R", ("ride", "aerith"): "R",
          ("lick", "cloud"): "L", ("lick", "tifa"): "L", ("lick", "aerith"): "L",
          ("share", "cloud_t"): "F", ("share", "cloud_a"): "G",
          ("share", "tifa_front"): "F", ("share", "aerith_front"): "F",
          ("share", "tifa_back"): "B", ("share", "aerith_back"): "B",
          ("stack", "cloud"): "S", ("stack", "cloud1"): "U", ("stack", "tifa"): "S",
          ("stack", "aerith"): "S", ("stack", "aerith1"): "U"}


def _who(key):
    return key.split("_")[0].rstrip("1")


class Scene:
    def __init__(self, bed, top):
        A, B, C, D = bed
        e = unit([D[0] - A[0], D[1] - A[1], 0.0])
        n = [-e[1], e[0], 0.0]
        if n[0] > 0:
            n = [-n[0], -n[1], 0.0]
        self.e, self.n = e, n
        self.E = ((A[0] + D[0]) / 2, (A[1] + D[1]) / 2)
        self.dir = round(math.degrees(math.atan2(n[0], -n[1])) * 256 / 360) % 256
        a = self.dir * 2 * math.pi / 256
        Fw = (math.sin(a), -math.cos(a))
        self.L = (-Fw[1], Fw[0])
        self.Fw = Fw

    def field(self, m):
        """Scene model point -> field (x, y, z)."""
        return (self.E[0] + U * (m[0] * self.L[0] - m[2] * self.Fw[0]),
                self.E[1] + U * (m[0] * self.L[1] - m[2] * self.Fw[1]), -U * m[1])

    def model(self, x, y, z):
        dx, dy = x - self.E[0], y - self.E[1]
        # field = E + U * (mx * L - mz * Fw): solve for (mx, mz)
        mx = (dx * self.L[0] + dy * self.L[1]) / U
        mz = -(dx * self.Fw[0] + dy * self.Fw[1]) / U
        return [mx, -z / U, mz]


def build(ctx, bed, top):
    """Every position's anims (written to char.lgp) and spots. Returns {segment: {actor key: (names by speed
    [4], (x, y, z), dir)}} + extra holds under "holds"."""
    global TOP
    TOP = top
    sc = Scene(bed, top)
    out = {}
    per = {}                                    # segment -> speed -> {key: [rigs]}
    for seg, fn in BUILDERS.items():
        for si, n in enumerate(FRAMES):
            per.setdefault(seg, {})[si] = fn(ctx, n)
    holds = _share_holds(ctx, per["share"][0], FRAMES[0])
    for seg, speeds in per.items():
        out[seg] = {}
        for key in speeds[0]:
            if key.endswith("_x0") or key.startswith("_"):
                continue
            who = _who(key)
            r0 = speeds[0][key][0]
            fp = sc.field(r0.root)
            over_bed = (fp[0] - sc.E[0]) * sc.n[0] + (fp[1] - sc.E[1]) * sc.n[1] < 0
            z = TOP if over_bed else 0
            spot = (round(fp[0]), round(fp[1]), z)
            off = sc.model(spot[0], spot[1], spot[2])
            names = []
            for si in range(len(FRAMES)):
                rigs = speeds[si][key]
                frames = []
                for r in rigs:
                    rr, rp, rots = r.frame()
                    frames.append((rr, [rp[0] - off[0], rp[1] + off[1], rp[2] - off[2]], rots))
                names.append(RG.save(ctx, "%s%s%d" % (PREFIX[who], LETTER[(seg, key)], si),
                                     r.base_name, frames))
            out[seg][key] = (names, spot, sc.dir, off)
    # the share's holds: deep (8) and pulled back (9) single frames, tapping out (7)
    sh = per["share"][0]
    n0 = FRAMES[0]
    hold = {}
    for who in ("tifa", "aerith"):
        _, _, _, off = out["share"][who + "_front"]

        def fr(r):
            rr, rp, rots = r.frame()
            return (rr, [rp[0] - off[0], rp[1] + off[1], rp[2] - off[2]], rots)
        base = sh[who + "_front"][0].base_name
        p = PREFIX[who]
        hold[who] = [RG.save(ctx, p + "F8", base, [fr(sh[who + "_front"][n0 // 2])]),
                     RG.save(ctx, p + "F7", base, [fr(r) for r in holds[who]]),
                     RG.save(ctx, p + "F9", base, [fr(sh[who + "_front"][0])])]
    for who, key in (("tifa", "cloud_t"), ("aerith", "cloud_a")):
        _, _, _, off = out["share"][key]
        rr, rp, rots = sh[key][n0 // 2].frame()
        hold["cloud_" + who] = RG.save(ctx, "YB" + LETTER[("share", key)] + "8", sh[key][0].base_name,
                                       [(rr, [rp[0] - off[0], rp[1] + off[1], rp[2] - off[2]], rots)])
    out["holds"] = hold
    return out

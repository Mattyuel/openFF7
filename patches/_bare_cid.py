"""(user) Bare Cid for Blast-off (673): his field model ABDA.HRC (jacket and shirt kept) without his
trousers, as bare Cloud (620 `_bare_cloud`): ZCIA.HRC with
- a sculpted seat for his pelvis (620 `_loft`, bare Cloud's CLOUD_SEAT_RINGS mapped onto his hips:
  heights by his pelvis bone (`SEAT_Y`), widths by his hip joints (`SEAT_W`)),
- smooth legs (`THIGH` / `SHIN`: rings (z along the bone, half width, half depth) in the bone's own
  frame, the bone running down local -z; his grey socks kept as a band at the bottom of the shins),
- a penis `MEMBER_SCALE` x Cloud's (620 MEMBER_*; user: 70% larger), a second part on the hip bone.
New rsd ZCIB.. -> .p ZCJB..; laid out on his standing pose (ABIE frame 0).
"""
import importlib
import math
import struct

HRC, BASE_HRC, STAND = "ZCIA.HRC", "abda.hrc", "abie.a"
SKIN, SOCK, TROUSERS = (119, 160, 245), (55, 59, 60), (25, 40, 43)   # B, G, R: his forearms' skin; socks
PELVIS, THIGHS, SHINS = "ABDB", ("ABGE", "ABHE"), ("ABHA", "ABIA")   # his parts (rsd names)
SEAT_Y = (-13.85, 1.56 / 1.75)   # his hip joints' height; his pelvis bone / Cloud's (Cloud's at -13.54)
CLOUD_HIP_Y = -13.54
SEAT_W = 2.03 / 1.88             # his hip joints' spread / Cloud's
MEMBER_SCALE = 1.7               # (user) 70% longer than Cloud's
MEMBER_W = 0.83                  # (user, since) its girth: half its first (1.7 x Cloud's then 0.975)
LEG_N = 8                        # points a ring
LEG_SCALE = 1.15                 # the profiles' widths x this (his jacket is bulky: thinner legs looked spindly)
# (z, half width, half depth): a man's thigh, tapering to a rounded knee (a tip beyond its last ring)
THIGH = [(0.5, 1.3, 1.35), (-1.1, 1.4, 1.45), (-3.1, 1.2, 1.25), (-5.1, 0.95, 1.0)]
THIGH_TIP = -6.0
# the shin: skin to the sock line (his trousers ended at z -3.53), then his grey socks into the boots
SHIN = [(0.5, 0.95, 1.0, SKIN), (-1.2, 1.1, 1.2, SKIN), (-2.6, 1.0, 1.05, SKIN), (-3.53, 0.95, 1.0, SKIN),
        (-3.53, 1.3, 1.35, SOCK), (-5.1, 1.35, 1.6, SOCK), (-6.4, 1.4, 1.75, SOCK)]


def _hb():
    return importlib.import_module("620_honey_bee")


def _rsd(ctx, old, new_rs, new_p):
    r = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
    oldp = r.split("PLY=")[1][:4]
    ctx.char_file(new_rs.lower() + ".rsd", r.replace("PLY=%s." % oldp, "PLY=%s." % new_p).encode("latin-1"))
    return ctx.char_file(oldp.lower() + ".p")


def _tails(d):
    h = struct.unpack_from("<16I", d, 0)
    o = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
    return d[64:128], struct.unpack_from("<12H", d, o)[10:12]


def _ring_loft(rings, n, cap_top, tip):
    """Rings (z, ax, ay[, colour]) round the bone's axis; top capped (flat fan), bottom open or a
    tip (a fan to (0, 0, tip)). Returns V, tris, colours."""
    V, C, tris = [], [], []
    for ring in rings:
        z, ax, ay = ring[:3]
        col = ring[3] if len(ring) > 3 else SKIN
        for k in range(n):
            ph = 2 * math.pi * k / n
            c_, s_ = math.cos(ph), math.sin(ph)
            V.append([LEG_SCALE * ax * math.copysign(abs(c_) ** 0.85, c_), LEG_SCALE * ay * math.copysign(abs(s_) ** 0.85, s_), z])
            C.append(col)
    for r in range(len(rings) - 1):
        for k in range(n):
            a, b = r * n + k, r * n + (k + 1) % n
            tris += [(a, b, b + n), (a, b + n, a + n)]
    if cap_top:
        tris += [(0, k, k + 1) for k in range(1, n - 1)]
    if tip is not None:
        base = (len(rings) - 1) * n
        V.append([0.0, 0.0, tip])
        C.append(C[-1])
        tris += [(base + k, base + (k + 1) % n, len(V) - 1) for k in range(n)]
    return V, tris, C


def _seat(ctx, hrc, d):
    """His pelvis as bare Cloud's seat, mapped onto his hips; returns the world vertices (for the member)."""
    from ff7 import fieldanim as fa
    hb = _hb()
    y0, ky = SEAT_Y
    my = lambda y: y0 + (y - CLOUD_HIP_Y) * ky
    rings = [(my(y), w * SEAT_W, f, b, bu) for y, w, f, b, bu in hb.CLOUD_SEAT_RINGS]
    (cy0, cz0), (cy1, cz1) = hb.CLOUD_SEAT_CENTRE
    cy0, cy1 = my(cy0), my(cy1)
    cx, ccy = hb.CLOUD_CROTCH
    V, tris = hb._loft(rings, hb.CLOUD_SEAT_ANG, lambda y: cz0 + (cz1 - cz0) * (y - cy0) / (cy1 - cy0),
                       (hb.CLOUD_SEAT[0] * SEAT_W, hb.CLOUD_SEAT[1] * SEAT_W), 1, hb.CLOUD_CLEFT,
                       rnd=hb.CLOUD_SEAT_ROUND, top=True, bottom=(cx, my(ccy)))
    sk = fa.skeleton(hrc)
    rr, rp, rots = fa.Anim(ctx.char_file(STAND)).frames[0]
    m, start, _ = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)[0]
    mt = [[m[r][c] for r in range(3)] for c in range(3)]
    local = [fa._vec(mt, [p[k] - start[k] for k in range(3)]) for p in V]
    tail, ptail = _tails(d)
    ctx.char_file("zcjb.p", hb._p_file(local, tris, SKIN, tail, ptail))
    return V, (m, start)


def _member(ctx, hrc, seat_world, frame, d):
    """Bare Cloud's box (620 `_bare_cloud_member`), MEMBER_SCALE x, on his new seat."""
    from ff7 import fieldanim as fa
    hb = _hb()
    m, start = frame
    bottom = max(w[1] for w in seat_world)
    front = min(w[2] for w in seat_world)
    yc = bottom - hb.MEMBER_UP * MEMBER_SCALE
    h = MEMBER_W / 2
    length = hb.MEMBER_LEN * MEMBER_SCALE
    corners = [[x, yc + y, z] for z in (front + hb.MEMBER_SINK, front + hb.MEMBER_SINK - length)
               for y in (-h, h) for x in (-h, h)]
    mt = [[m[r][c] for r in range(3)] for c in range(3)]
    local = [fa._vec(mt, [p[k] - start[k] for k in range(3)]) for p in corners]
    ctx.char_file("zcjp.p", hb._box_p(local, SKIN, d[64:128]))


def build(ctx):
    """Writes ZCIA.HRC and its new parts (once)."""
    try:
        ctx.char_file(HRC.lower())
        return
    except KeyError:
        pass
    hb = _hb()
    hrc = ctx.char_file(BASE_HRC).decode("latin-1")
    # pelvis -> the seat + the member
    assert hrc.count("1 %s" % PELVIS) == 1, PELVIS
    hrc = hrc.replace("1 %s" % PELVIS, "2 ZCIB ZCIP")
    d = _rsd(ctx, PELVIS, "ZCIB", "ZCJB")
    _rsd(ctx, PELVIS, "ZCIP", "ZCJP")
    seat, frame = _seat(ctx, hrc, d)
    _member(ctx, hrc, seat, frame, d)
    # legs
    for k, (thigh, shin) in enumerate(zip(THIGHS, SHINS)):
        for old, new, (rings, cap, tip) in ((thigh, "ZCI" + "CE"[k], (THIGH, False, THIGH_TIP)),
                                            (shin, "ZCI" + "DF"[k], (SHIN, True, None))):
            assert hrc.count("1 %s" % old) == 1, old
            hrc = hrc.replace("1 %s" % old, "1 %s" % new)
            newp = "ZCJ" + new[3]
            d = _rsd(ctx, old, new, newp)
            V, tris, C = _ring_loft(rings, LEG_N, cap, tip)
            tail, ptail = _tails(d)
            ctx.char_file(newp.lower() + ".p", hb._p_file(V, tris, C, tail, ptail))
    assert TROUSERS and "ABDB" not in hrc and not any(p in hrc for p in THIGHS + SHINS)
    ctx.char_file(HRC.lower(), hrc.encode("latin-1"))

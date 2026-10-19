"""(user) The school dance: Tifa, Aerith, Yuffie, Elena and Scarlet in Japanese school uniforms dancing a
synchronised routine on the Gold Saucer's stage (data `_school_dance.py`, moves `_dance_poses.py`). Passive:
picked from the cameraman's list (670: "School dance", SPEC 6), watched, then back to him.

The uniforms: each girl's own head and feet on the standard body (`_female_body.apply`) with Tifa's shapes
(`tifa_body`, her bust size), painted: a white sailor blouse with a navy sailor collar (round the shoulders,
a square flap down the back, lapels framing the front), a red neckerchief, white sleeves, navy pelvis, bare
thighs, navy knee socks; plus a navy pleated skirt (a new part on the hip bone, flared from the waist to
`SKIRT_LEN` down the thigh, both sides drawn). Tifa's arm guard dropped, Scarlet's dress skirt too.

The set: FIELD (blackbgk, only the debug room leads there) replaced by the original stage (astage_b), script
blanked. Models: Cloud (the hidden player), the King (MC), the five girls (each only the dance's anims).
The director: the King's intro (windows that close themselves), the music, then the routine: each step sets
M and starts every girl's slot 2 (the move, looped) at once, or slot 10+t (the move while she travels to the
next formation, XYZI stepped a frame at a time), or (canon) one girl a beat after the other; girls' shouts on
some steps; the King's outro; fade; back to the cameraman. Checked on offline renders only."""
import importlib
import math
import struct

import _dance_poses as DP
import _female_body as fb
import _school_dance as SD
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera, facing_screen
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script

M = (5, 160)                                   # the move (chain over the girls' slot 2)


def _mods():
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee"), \
        importlib.import_module("660_dates")


# ---- the uniforms ----------------------------------------------------------------------------------------
# the chest part in Tifa's frame (x across, her left +; y forward; z down the bone: the neck's top at ~-4.2,
# the bust at ~-1.5, the waist at ~+0.8)
COLLAR_Z = -3.45                # navy above this (round the neck and shoulders)
FLAP_Z, FLAP_Y = -2.2, 0.3      # the collar's square flap down the back: behind FLAP_Y, above FLAP_Z
KNOT_Z, KNOT_X = -2.45, 0.62    # the neckerchief's knot: in front, |x| < KNOT_X, above KNOT_Z
TAIL_Z, TAIL_X = -2.0, 0.32     # its tails, a little lower and narrower
LAPEL_X = 1.25                  # the lapels: from the knot out to this |x|, above KNOT_Z
FRONT_Y = 0.5


def _chest_colour(c):
    x, y, z = c
    if z < COLLAR_Z:
        return SD.NAVY
    if y < FLAP_Y and z < FLAP_Z:
        return SD.NAVY
    if y > FRONT_Y and z < KNOT_Z and abs(x) < KNOT_X:
        return SD.RED
    if y > FRONT_Y and z < TAIL_Z and abs(x) < TAIL_X:
        return SD.RED
    if y > FLAP_Y and z < KNOT_Z and abs(x) < LAPEL_X:
        return SD.NAVY
    return SD.WHITE


CHEST_CUTS = [([0.0, 0.0, 1.0], COLLAR_Z), ([0.0, 0.0, 1.0], FLAP_Z), ([0.0, 0.0, 1.0], KNOT_Z),
              ([0.0, 0.0, 1.0], TAIL_Z), ([0.0, 1.0, 0.0], FLAP_Y), ([0.0, 1.0, 0.0], FRONT_Y)] + \
    [([1.0, 0.0, 0.0], s * v) for s in (1, -1) for v in (KNOT_X, TAIL_X, LAPEL_X)]


def _recolour(d, bgr):
    """.p bytes d with every vertex and polygon colour bgr."""
    d = bytearray(d)
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nu, nt, nc, npoly = h[3], h[4], h[5], h[6], h[7], h[9]
    oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
    for o in [oc + 4 * i for i in range(nc)] + [oc + 4 * nc + 4 * j for j in range(npoly)]:
        d[o:o + 3] = bytes(bgr)
    return bytes(d)


def _ply(ctx, rsd):
    return ctx.char_file(rsd.lower() + ".rsd").decode("latin-1").split("PLY=")[1][:4].lower() + ".p"


def _skirt(ctx, g, hrc, stand):
    """The pleated skirt on her hip bone (a new part "ZK<tag>S"), built in her stand pose. Returns the .hrc."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(hrc)
    names = [b[0] for b in sk]
    rr, rp, rots = fa.Anim(ctx.char_file(stand)).frames[0]
    F = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
    bn = fb.bones(hrc)
    m, start = F[names.index("hip")][0], F[names.index("hip")][1]
    world = lambda b, v: [F[names.index(b)][1][k] + fa._vec(F[names.index(b)][0], v)[k] for k in range(3)]
    hip_p = ctx.char_file(_ply(ctx, bn["hip"][1][0]))
    pel = [world("hip", v) for v in fb._part(hip_p)[0]]
    thighs = [world(s + "_femur", v) for s in "lr" for v in fb._part(ctx.char_file(_ply(ctx, bn[s + "_femur"][1][0])))[0]]
    cx, cz = sum(v[0] for v in pel) / len(pel), sum(v[2] for v in pel) / len(pel)
    top = min(v[1] for v in pel)                                     # (y down) the waist
    hj = F[names.index("l_femur")][1][1]
    knee = F[names.index("l_femur")][2][1]
    hem = hj + (knee - hj) * SD.SKIRT_LEN
    body = pel + thighs

    def extent(y, band):
        near = [v for v in body if abs(v[1] - y) < band]
        return (max(abs(v[0] - cx) for v in near), max(abs(v[2] - cz) for v in near))
    rx0, rz0 = extent(top + 0.25, 0.35)
    rxh, rzh = extent(hem, 0.5)
    rings = []
    for t in (0.0, 0.45, 1.0):
        y = top + (hem - top) * t
        rx = max(rx0 + SD.SKIRT_TOP_PAD, (rxh + 0.2)) * (1 + (SD.SKIRT_FLARE - 1) * t) if t else rx0 + SD.SKIRT_TOP_PAD
        rz = max(rz0 + SD.SKIRT_TOP_PAD, (rzh + 0.2)) * (1 + (SD.SKIRT_FLARE - 1) * t) if t else rz0 + SD.SKIRT_TOP_PAD
        ring = []
        for k in range(SD.PLEATS):
            a = 2 * math.pi * k / SD.PLEATS
            f = 1 - SD.PLEAT_IN * t * (k % 2)
            ring.append([cx + rx * f * math.cos(a), y, cz + rz * f * math.sin(a)])
        rings.append(ring)
    V, P, N = [], [], []
    for side in (1, -1):                                             # outside, then the inside (own vertices)
        base = len(V)
        for r in rings:
            for v in r:
                V.append(v)
                n = [v[0] - cx, 0.0, v[2] - cz]
                L = math.sqrt(n[0] ** 2 + n[2] ** 2) or 1.0
                N.append([side * n[0] / L, 0.0, side * n[2] / L])
        for j in range(len(rings) - 1):
            for k in range(SD.PLEATS):
                a, b = base + j * SD.PLEATS + k, base + j * SD.PLEATS + (k + 1) % SD.PLEATS
                c, d = a + SD.PLEATS, b + SD.PLEATS
                for t in ((a, b, c), (b, d, c)):
                    p0, p1, p2 = (V[i] for i in t)
                    cr = [(p1[1] - p0[1]) * (p2[2] - p0[2]) - (p1[2] - p0[2]) * (p2[1] - p0[1]),
                          (p1[2] - p0[2]) * (p2[0] - p0[0]) - (p1[0] - p0[0]) * (p2[2] - p0[2]),
                          (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])]
                    out = [p0[0] - cx, 0.0, p0[2] - cz]
                    inward = sum(cr[q] * out[q] for q in range(3)) < 0     # the game's winding: cross points in
                    if inward != (side == 1):
                        t = (t[0], t[2], t[1])
                    P.append(t)
    mt = [[m[c][r] for c in range(3)] for r in range(3)]
    local = lambda w: fa._vec(mt, [w[k] - start[k] for k in range(3)])
    VL, NL = [local(v) for v in V], [fa._vec(mt, n) for n in N]
    h = struct.unpack_from("<16I", hip_p, 0)
    op = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6] + 4 * h[7] + 4 * h[9] + 4 * h[8]
    hb = _mods()[1]
    r_, p_ = "ZK%sS" % g["tag"], "ZJ%sS" % g["tag"]
    rsd = ctx.char_file(bn["hip"][1][0].lower() + ".rsd").decode("latin-1")
    ctx.char_file(r_.lower() + ".rsd", rsd.replace("PLY=%s." % rsd.split("PLY=")[1][:4], "PLY=%s." % p_).encode("latin-1"))
    ctx.char_file(p_.lower() + ".p", hb._p_file(VL, P, [SD.NAVY] * len(VL), hip_p[64:128],
                                                struct.unpack_from("<12H", hip_p, op)[10:12], normals=NL, wound=True))
    lines = hrc.splitlines(True)
    k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "hip" and lines[k + 1].strip() == "root")
    w = lines[k + 3].split()
    lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), " ".join([str(int(w[0]) + 1)] + w[1:] + [r_]))
    return "".join(lines)


def _uniform(ctx, g):
    """Her school uniform .hrc (g["hrc"]). Returns (donor entry, stand anim file)."""
    mv, hb, dt = _mods()
    field = FieldFile(ctx._orig_raw[SD.BASE]) if g["donor"][0] == SD.BASE else ctx.field(g["donor"][0])
    donor = ModelLoader(field.section("models")).models[g["donor"][1]]      # (674 swaps the stage's own models)
    src = ModelLoader.hrc(donor).lower()
    text = ctx.char_file(src).decode("latin-1")
    if g["src"] == "noskirt":                                        # Scarlet: her dress's skirt pieces off
        for part in dt.SCARLET_SKIRT:
            assert text.count("1 %s\r\n" % part) == 1, part
            text = text.replace("1 %s\r\n" % part, "0\r\n")
    skin = fb.face_skin(ctx, text)
    hrc = fb.apply(ctx, text, g["tag"], skin, None, 1.0, g["head_drop"])
    if "armer" in fb.bones(hrc):                                     # Tifa's arm guard
        bn = fb.bones(hrc)
        lines = hrc.splitlines(True)
        k = next(k for k in range(len(lines) - 3) if lines[k].strip() == "armer")
        lines[k + 3] = lines[k + 3].replace(lines[k + 3].strip(), "0")
        hrc = "".join(lines)
    fb.tifa_body(ctx, hrc, skin, g["bust"], paints={"chest": (CHEST_CUTS, _chest_colour),
                                                     "hip": ([], lambda c: SD.NAVY)})
    bn = fb.bones(hrc)
    for b, col in [("l_uparm", SD.WHITE), ("r_uparm", SD.WHITE), ("l_collar", SD.WHITE), ("r_collar", SD.WHITE),
                   ("l_tibia", SD.SOCKS), ("r_tibia", SD.SOCKS)]:
        p = _ply(ctx, bn[b][1][0])
        ctx.char_file(p, _recolour(ctx.char_file(p), col))
    stand = ModelLoader.anims(donor)[0].split(".")[0].lower() + ".a"
    hrc = _skirt(ctx, g, hrc, stand)
    ctx.char_file(g["hrc"].lower(), hrc.encode("latin-1"))
    return donor, src, stand


# ---- the set -----------------------------------------------------------------------------------------------
def _set(ctx, cast, moves):
    mv, hb, dt = _mods()
    ctx.field(SD.FIELD)
    raw = ctx._orig_raw.get(SD.BASE)
    assert raw, "the stage's original isn't loaded"
    f = ctx._fields[SD.FIELD] = FieldFile(raw)
    trig = f.section("triggers")
    for slot in range(12):
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    cam = Camera(f.sections[1])
    from ff7.walkmesh import Walkmesh
    mesh = Walkmesh(f.section("walkmesh"))

    def spot(x, y):
        t = mesh.find(round(x), round(y))
        assert t is not None, ("off the stage", x, y)
        return round(x), round(y), SD.FLOOR, t
    # models: 0 Cloud (hidden player), 1 the King, 2.. the girls
    loader = ModelLoader(f.section("models"))
    base = list(loader.models)
    loader.models = [base[0], base[SD.MC_DONOR[1]]]
    letters = [L for L, _, _, _ in DP.MOVES]
    first = {}
    for g, (donor, src, stand) in zip(SD.GIRLS, cast):
        names = mv._retarget(ctx, ["%s%s0.tor" % (DP.SRC, L) for L in letters], g["prefix"], src.upper(), stand)
        if g["donor"][0] == SD.BASE:
            e = base[g["donor"][1]]
        else:
            k = loader.add_from(ModelLoader(ctx.field(g["donor"][0]).section("models")), g["donor"][1])
            e = loader.models.pop(k)
        e = ModelLoader.only_anims(ModelLoader.with_hrc(e, g["hrc"], "dance_%s.char" % g["key"]), names)
        loader.models.append(e)
        assert len(ModelLoader.anims(e)) <= 47
    assert len(loader.models) == 2 + len(SD.GIRLS) <= 16
    # entities
    G = ["g_" + g["key"][:6] for g in SD.GIRLS]
    names = ["produce", "cloud", "king"] + G + ["voice", "hush"]
    sec.entity_names = [n.encode("latin-1").ljust(8, b"\0") for n in names]
    sec.entry = [[sec._end] * 32 for _ in names]
    E = {n: i for i, n in enumerate(names)}
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    loop_ = lambda i: [mv._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    ch = mv._chain
    face = lambda x, y: facing_screen(cam, x, y, SD.FLOOR, (0, 1))
    scripts = {}
    ax, ay = SD.ARRIVE
    scripts[E["cloud"]] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*spot(ax, ay)), hb._visi(0),
                               asm.ret(), asm.ret()]}
    kx, ky = SD.MC_AT
    scripts[E["king"]] = {0: [Op(bytes([0xA1, 1])), xyzi(*spot(kx, ky)), d_(face(kx, ky)), hb._visi(1),
                              Op(b"\x7E\x01"), Op(b"\xC7\x01")] + loop_(0) + [asm.ret(), asm.ret()]}
    # the girls: init at the start formation; slot 2 the move by M; slot 10+t travel to formation t's spots
    travels = [(i, step) for i, step in enumerate(SD.ROUTINE) if step[2]]
    form = {}
    cur = SD.START
    for i, (L, beats, to, canon) in enumerate(SD.ROUTINE):
        form[i] = (cur, to)
        if to:
            cur = to
    for k, g in enumerate(SD.GIRLS):
        X, Y, CN = (6, 100 + 8 * k), (6, 102 + 8 * k), (5, 104 + 8 * k)
        x0, y0 = SD.FORMATIONS[SD.START][k]
        s = {0: [Op(bytes([0xA1, 2 + k])), xyzi(*spot(x0, y0)), d_(face(x0, y0)), hb._visi(1),
                 Op(b"\x7E\x01"), Op(b"\xC7\x01")] + loop_(0) + [asm.ret(), asm.ret()],
             2: ch(M, [loop_(j) for j in range(len(letters))]) + [asm.ret()]}
        for t, (i, (L, beats, to, canon)) in enumerate(travels):
            (sx, sy), (tx, ty) = SD.FORMATIONS[form[i][0]][k], SD.FORMATIONS[to][k]
            n = SD.TRAVEL
            assert n <= beats * DP.BEAT - 4 and (tx - sx) % n == 0 and (ty - sy) % n == 0, (g["key"], to)
            stx, sty = (tx - sx) // n, (ty - sy) // n
            top, done = hb._w(1), asm.nop()
            tt = spot(tx, ty)
            s[10 + t] = loop_(letters.index(L)) + \
                [asm.setword(X, sx & 0xFFFF), asm.setword(Y, sy & 0xFFFF), asm.setbyte(CN, 0),
                 top, hb._arith(0x86, X, stx & 0xFFFF), hb._arith(0x86, Y, sty & 0xFFFF),
                 Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", X[1], Y[1], SD.FLOOR, tt[3])),
                 Op(bytes([0x95, CN[0], CN[1]])), asm.if_byte(CN, "<", n, done), asm.goto_back(top), done,
                 xyzi(*tt), d_(face(tx, ty)), asm.ret()]
        scripts[E[G[k]]] = s
    # the windows: voice slot 2+i shows line i in a window the player can't close; hush closes it
    lines = SD.INTRO + [SD.SHOUTS[i] for i in sorted(SD.SHOUTS)] + [SD.OUTRO]
    vo = {}
    for i, text in enumerate(lines):
        vo[2 + i] = [Op(b"\x52\x01\x00\x01"), hb._window(text, 1, 8, SD.TEXT_Y), hb._req(E["hush"], 2, wait=False),
                     asm.message(1, mv._text_id(sec, text)), asm.ret()]
    vo[0] = [asm.ret(), asm.ret()]
    scripts[E["voice"]] = vo
    scripts[E["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(SD.SAY), Op(b"\x54\x01"), asm.ret()]}
    say = lambda i: [hb._req(E["voice"], 2 + i, wait=False)]
    # the director
    fade_out, fade_in = [Op(hb.FADE_OUT), Op(b"\x6C")], [Op(hb.FADE_IN), Op(b"\x6C")]
    main = [hb._uc(1), hb._menu(1), hb._w(20)] + fade_in
    for i in range(len(SD.INTRO)):
        main += say(i) + [hb._w(SD.SAY + 12)]
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, SD.MUSIC]) + bytes(8))]
    shout_of = {s: len(SD.INTRO) + j for j, s in enumerate(sorted(SD.SHOUTS))}
    t = 0
    for i, (L, beats, to, canon) in enumerate(SD.ROUTINE):
        frames = beats * DP.BEAT
        main += [asm.setbyte(M, letters.index(L))]
        if i in shout_of:
            main += say(shout_of[i])
        if to:
            main += [hb._req(E[gn], 10 + t, wait=False) for gn in G]
            t += 1
        elif canon:
            for gn in G:
                main += [hb._req(E[gn], 2, wait=False), hb._w(DP.BEAT)]
            frames -= DP.BEAT * len(G)
        else:
            main += [hb._req(E[gn], 2, wait=False) for gn in G]
        main += [hb._w(max(1, frames))]
    main += [hb._w(20)] + say(len(lines) - 1) + [hb._w(SD.SAY + 20)] + fade_out
    rx, ry, rz, rt, rdir = ctx.movie_back
    stop = hb._w(30)
    main += [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(mv.WALL), rx, ry, rt, rdir), stop, asm.goto_back(stop)]
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main + [asm.ret()]}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n_text = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n_text <= 255, n_text
    secs = sum(b for _, b, _, _ in SD.ROUTINE) * DP.BEAT / 30
    return n_text, len(f.sections[0]), secs


def apply(ctx):
    moves = DP.build(ctx)
    cast = [_uniform(ctx, g) for g in SD.GIRLS]
    n_text, size, secs = _set(ctx, cast, moves)
    print("  682: the school dance on %s (%d moves, %d steps, %.0f s, %d texts, script %d bytes)"
          % (SD.FIELD, len(moves), len(SD.ROUTINE), secs, n_text, size))

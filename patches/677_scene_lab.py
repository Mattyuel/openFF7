"""(user) The scene lab: a placement tool, not a scene. The Director (Sector 7 station, mds7st3: takes over
the story copy `emother`, hidden at our moment, the station being at 16 models) asks "Direct a scene?";
yes = MAPJUMP into `LAB`, a copy of the Sector 7 inn's top floor (mds7_w3, the movie sets' room) with the
models of the group shoot's room (subin_4: bare Cloud, the six bare girls, the cameraman; each with its
anims there). Two actors, A and B, each wearing one of those models; the selected one is controlled:

    arrows          move it on the screen (R2 held: faster); free, not bound to the floor
    L1 / R1         turn it
    Square          next model (skips the one the other actor wears)
    Triangle        next animation of its model (looped)
    Cancel          floor / bed height (on a bed top under it: the beds are z 54 / 100 / 125)
    OK              select the other actor
    L2 + R2         leave (asks first)

Their XYZI coordinates (x, y, z) and DIR show top left (A) and top right (B), the selected one marked
">". The numbers are typed when the window opens (exe 0x6324C8 reads the MPRA2 variable once, into the
window's own buffer), so a window is reopened when its actor has stood still for `SETTLE` frames after a
change. Signs and the marker / height word are poked into the text (TXPOKE, 620) before each opening.
Model / anim index lists: printed by the build and written to work/scene_lab.txt."""
import importlib
import math
import os
import struct

import _movie_group as GR
from _travel import beside, choice_menu, mapjump, reuse_npc
from ff7 import asm
from ff7 import triggers as tg
from ff7.camera import Camera, facing_screen
from ff7.field import FieldFile
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

LAB = "blackbge"           # never entered in the open world (no gateway or MAPJUMP leads there; no free names left)
BASE, ROOM = "mds7_w3", "subin_4"
STATION = "mds7st3"
DIRECTOR = "emother"       # mds7st3 story copy (only her train-arrival scenes show her)
DIRECTOR_DONOR = ("astage_b", 4)                     # the play's King (674's Booker): a showman
DIRECTOR_AT = (-3250, 2400)                          # lower platform, left of the cameraman (screen ~(-50, 32))
START = [(-100, -220), (100, -220)]                   # A, B on the floor
STEP, FAST = 2, 3                                    # screen pixels a frame (R2: x FAST)
TURN = 3                                             # DIR units a step
SETTLE = 8                                           # frames still before the readout refreshes
SQUARE, TRIANGLE, CANCEL, OK = 0x80, 0x210, 0x240, 0x220   # IFKEY masks as the original scripts use them
L1, R1, L2, R2 = 0x04, 0x08, 0x01, 0x02
ARROWS = {"up": 0x1000, "right": 0x2000, "down": 0x4000, "left": 0x8000}

# temp vars (banks 5 / 6 are one area): actor e's block at 100 + 32 e
def _v(e, off, word=True):
    return (6 if word else 5, 100 + 32 * e + off)


X, Y, Z, D, AN = (lambda e: _v(e, 0)), (lambda e: _v(e, 2)), (lambda e: _v(e, 4)), (lambda e: _v(e, 6)), \
    (lambda e: _v(e, 8))
M, BED, IDLE = (lambda e: _v(e, 10, False)), (lambda e: _v(e, 11, False)), (lambda e: _v(e, 13, False))
AX, AY, AZ, TX, TY, ZN = (lambda e: _v(e, 14)), (lambda e: _v(e, 16)), (lambda e: _v(e, 18)), \
    (lambda e: _v(e, 20)), (lambda e: _v(e, 22)), (lambda e: _v(e, 24))
SEL, LEAVING = (5, 170), (5, 172)
PRV = lambda j: (5, 190 + j)                         # press button j held last frame
# (exe: 0x85-0x88 PLUS / PLUS2 / MINUS / MINUS2 wrap; 0x76 / 0x77 stop at 255 / 32767 and 0x79 MINUS2!
# turns any result under +32768 into -32768: the actors jumped to -32768, user)
ADD, SUB = 0x86, 0x88
APPLIED = lambda k: (5, 180 + k)                     # per model: the anim it plays (255 = none)
WIN = lambda e: 1 + e


def _hb():
    return importlib.import_module("620_honey_bee")


def _byte(v):                                        # a word var's low byte
    return (5, v[1])


def _ifkey(mask, else_):
    return Op(bytes([0x30]) + struct.pack("<H", mask) + b"\x00", target=else_)


def _xyzi_var(x, y, z, tri):
    return Op(bytes([0xA5, 0x66, 0x60]) + struct.pack("<HHHH", x[1], y[1], z[1], tri))


def _poke(tid, off, char):
    return Op(bytes([0x1D, tid]) + struct.pack("<H", off) + encode(char)[:1])


def _models(ctx):
    """[(label, model loader entry)] of the group room's actors: bare Cloud, the girls, the cameraman."""
    loader = ModelLoader(ctx.field(ROOM).section("models"))
    assert len(loader.models) == 13, len(loader.models)
    labels = ["Cloud"] + [k.capitalize() for k in GR.ORDER] + ["Cameraman"]
    return list(zip(labels, loader.models[2:10]))


def _beds(mesh):
    """[(x0, x1, y0, y1, top)] of the walkmesh pieces above the floor (z 0)."""
    tops = {}
    for t in mesh.tris:
        z = round(sum(v[2] for v in t) / 3)
        if z > 10:
            tops.setdefault(z, []).extend(t)
    out = []
    for z, vs in sorted(tops.items()):
        out.append((min(v[0] for v in vs), max(v[0] for v in vs), min(v[1] for v in vs), max(v[1] for v in vs), z))
    assert [b[4] for b in out] == [54, 100, 125], out
    return out


def _screen_steps(cam):
    """Field (dx, dy) a step for each arrow: the floor direction that moves on screen that way."""
    p0, px, py = cam.project(0, -150, 0), cam.project(100, -150, 0), cam.project(0, -50, 0)
    a, b = (px[0] - p0[0]) / 100, (py[0] - p0[0]) / 100
    c, d = (px[1] - p0[1]) / 100, (py[1] - p0[1]) / 100
    det = a * d - b * c
    inv = lambda sx, sy: ((d * sx - b * sy) / det, (-c * sx + a * sy) / det)
    out = {}
    for speed in (STEP, STEP * FAST):
        for name, (sx, sy) in {"up": (0, -1), "right": (1, 0), "down": (0, 1), "left": (-1, 0)}.items():
            fx, fy = inv(sx * speed, sy * speed)
            out[name, speed] = (round(fx), round(fy))
    return out


def _lab(ctx):
    hb = _hb()
    dt = importlib.import_module("660_dates")
    models = _models(ctx)
    ctx.field(LAB)                                     # (registers the original, so the copy is saved)
    f = ctx._fields[LAB] = FieldFile(ctx.field(BASE).build())
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    trig = f.section("triggers")
    for slot in range(12):                             # no way out by walking (the hidden player follows the actor)
        trig = tg.set_gateway_field(trig, slot, tg.UNUSED)
    f.set_section("triggers", trig)
    loader = ModelLoader(f.section("models"))
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    assert names[:5] == ["produce", "direct", "ad", "cloud", "child"] and len(loader.models) == 2, names
    for _, entry in models:
        loader.models.append(entry)                   # (the same room: same field scale)
    nm = len(models)
    ents = {}
    for name in ["lab%d" % k for k in range(nm)] + ["ar_" + a for a in ARROWS] + \
            ["turn_l", "turn_r", "zfix0", "zfix1", "press0", "press1", "press2", "press3", "leave",
             "disp0", "disp1", "shut0", "shut1"]:
        ents[name] = len(sec.entity_names)
        assert len(name) <= 8, name
        sec.entity_names.append(name.encode("latin-1").ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    CL = 3
    floor_tri = {e: mesh.find(*START[e]) for e in (0, 1)}
    assert None not in floor_tri.values(), floor_tri
    face = facing_screen(cam, START[0][0], START[0][1], 0, (0, 1))
    beds = _beds(mesh)
    steps = _screen_steps(cam)
    wait = lambda: hb._w(1)
    scripts = {}

    # (exe 0x60CD77: an entity runs at most 8 ops a frame, NOP labels included: every loop below keeps
    # its idle pass to a few ops, jumps aim at real ops, and each button has its own entity, so every
    # button is read every frame; user: presses were missed when one entity polled them all)
    again = lambda top: asm.goto_back(top)

    # setup (entity 0's init runs before every main)
    init = [hb._uc(1), hb._menu(1), asm.setbyte(SEL, 0), asm.setbyte(LEAVING, 0)]
    init += [asm.setbyte(PRV(j), 0) for j in range(4)]
    for e in (0, 1):
        init += [asm.setword(X(e), START[e][0] & 0xFFFF), asm.setword(Y(e), START[e][1] & 0xFFFF),
                 asm.setword(Z(e), 0), asm.setword(D(e), face), asm.setword(AN(e), 0), asm.setbyte(M(e), e),
                 asm.setbyte(BED(e), 0), asm.setbyte(IDLE(e), 0)]
    init += [asm.setbyte(APPLIED(k), 255) for k in range(nm)]
    scripts[0] = {0: init + [asm.ret(), asm.ret()]}

    # the hidden player: the camera follows the selected actor
    top = wait()
    xb = _xyzi_var(X(1), Y(1), Z(1), floor_tri[1])
    sx, sy = START[0]
    scripts[CL] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), hb._xyzi(sx, sy, 0, floor_tri[0]), hb._visi(0),
                       asm.ret(), top, asm.if_byte(SEL, "==", 0, xb), _xyzi_var(X(0), Y(0), Z(0), floor_tri[0]),
                       again(top), xb, again(top), asm.ret()]}
    scripts[4] = {0: [Op(bytes([0xA1, 1])), hb._visi(0), asm.ret(), asm.ret()]}

    # the models: shown where their actor is, playing its anim
    loop_ = lambda i: [importlib.import_module("670_movie")._animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    anim_counts = []
    for k, (label, entry) in enumerate(models):
        n_anim = len(ModelLoader.anims(entry))
        assert n_anim <= 47, (label, n_anim)
        anim_counts.append(n_anim)
        top = wait()

        def place(e, k=k, n_anim=n_anim, top=top):
            back = again(top)
            return [_xyzi_var(X(e), Y(e), Z(e), floor_tri[e]), Op(bytes([0xB3, 5, D(e)[1]])), hb._visi(1),
                    asm.if_byte(APPLIED(k), "!=", _byte(AN(e)), back),             # (the same anim: done)
                    asm.setbyte(APPLIED(k), _byte(AN(e)))] + \
                dt_chain(_byte(AN(e)), [loop_(i) for i in range(n_anim)]) + [back]
        hide = hb._visi(0)
        on_b = place(1)
        chk_b = asm.if_byte(M(1), "==", k, hide)
        body = [top, asm.if_byte(M(0), "==", k, chk_b)] + place(0) + [chk_b] + on_b + \
            [hide, asm.setbyte(APPLIED(k), 255), again(top)]
        scripts[ents["lab%d" % k]] = {0: [Op(bytes([0xA1, 2 + k])), hb._visi(0), asm.ret()] + body + [asm.ret()]}

    # arrows: one entity each; a step a frame while held (R2: faster)
    def step(e, name, speed):
        dx, dy = steps[name, speed]
        ops = [hb._arith(ADD if v >= 0 else SUB, var, abs(v)) for v, var in ((dx, X(e)), (dy, Y(e))) if v]
        return ops + [asm.setbyte(IDLE(e), 0)]
    for name, mask in ARROWS.items():
        top = wait()
        idle = again(top)
        side = {}
        for e in (0, 1):
            slow = step(e, name, STEP) + [again(top)]
            side[e] = [_ifkey(R2, slow[0])] + step(e, name, STEP * FAST) + [again(top)] + slow
        scripts[ents["ar_" + name]] = {0: [asm.ret(), top, _ifkey(mask, idle), asm.if_byte(LEAVING, "==", 0, idle),
                                               asm.if_byte(SEL, "==", 0, side[1][0])] + side[0] + side[1] +
                                          [idle, asm.ret()]}
    # L1 / R1: turn (the DIR byte wraps: PLUS / MINUS, 0x85 / 0x87)
    for nm_, mask, op in (("turn_l", L1, 0x87), ("turn_r", R1, 0x85)):
        top = wait()
        idle = again(top)
        side = {e: [Op(bytes([op, 0x50, D(e)[1], TURN])), asm.setbyte(IDLE(e), 0), again(top)] for e in (0, 1)}
        scripts[ents[nm_]] = {0: [asm.ret(), top, _ifkey(mask, idle), asm.if_byte(LEAVING, "==", 0, idle),
                                  asm.if_byte(SEL, "==", 0, side[1][0])] + side[0] + side[1] + [idle, asm.ret()]}
    # height: the floor, or (bed on) the top of the bed under it
    for e in (0, 1):
        top = wait()
        floor = asm.setword(Z(e), 0)
        done = asm.setword(Z(e), ZN(e))
        rects = []
        for x0, x1, y0, y1, h in beds:
            rects.append([(TX(e), ">=", x0), (TX(e), "<=", x1), (TY(e), ">=", y0), (TY(e), "<=", y1), h])
        blocks = []
        for i, r in enumerate(rects):
            blocks.append([None] * 4 + [asm.setword(ZN(e), r[4])])
        for i, r in enumerate(rects):
            nxt = blocks[i + 1][0] if i + 1 < len(rects) else done
            for c in range(4):
                v, cmp, lim = r[c]
                blocks[i][c] = asm.if_word(v, cmp, (lim + 0x8000) & 0xFFFF, None)
        for i in range(len(blocks)):
            nxt = blocks[i + 1][0] if i + 1 < len(blocks) else done
            for c in range(4):
                blocks[i][c].target = nxt
        zf = [asm.ret(), top, asm.if_byte(BED(e), "==", 1, floor), asm.setword(TX(e), X(e)),
              hb._arith(ADD, TX(e), 0x8000), asm.setword(TY(e), Y(e)), hb._arith(ADD, TY(e), 0x8000),
              asm.setword(ZN(e), 0)] + [o for b in blocks for o in b] + [done, again(top), floor, again(top), asm.ret()]
        scripts[ents["zfix%d" % e]] = {0: zf}

    # presses: one entity each (PRV(j) = held last frame)
    def act(e, what):
        o = 1 - e
        if what == "model":
            chk, same = asm.if_byte(M(e), "==", M(o), None), asm.setword(AN(e), 0)
            chk.target = same
            return [Op(bytes([0x85, 0x50, M(e)[1], 1])), asm.if_byte(M(e), ">=", nm, chk), asm.setbyte(M(e), 0), chk,
                    Op(bytes([0x85, 0x50, M(e)[1], 1])),                   # (the other actor's: the next one)
                    asm.if_byte(M(e), ">=", nm, same), asm.setbyte(M(e), 0), same]
        if what == "anim":
            wraps = []
            for k in range(nm):
                keep = asm.nop()
                wraps.append([asm.if_byte(_byte(AN(e)), ">=", anim_counts[k], keep), asm.setword(AN(e), 0), keep])
            return [Op(bytes([0x85, 0x50, AN(e)[1], 1]))] + dt_chain(M(e), wraps)
        if what == "bed":
            off = asm.setbyte(BED(e), 0)
            done = asm.nop()
            return [asm.if_byte(BED(e), "==", 0, off), asm.setbyte(BED(e), 1), asm.goto(done), off, done]
    for j, (mask, what) in enumerate(((SQUARE, "model"), (TRIANGLE, "anim"), (CANCEL, "bed"), (OK, "select"))):
        top = wait()
        back = again(top)
        if what == "select":
            one, marks = asm.setbyte(SEL, 0), asm.setbyte(IDLE(0), 0)
            body = [asm.if_byte(SEL, "==", 0, one), asm.setbyte(SEL, 1), asm.goto(marks), one, marks,
                    asm.setbyte(IDLE(1), 0)]
        else:
            body = dt_chain(SEL, [act(e, what) + [asm.setbyte(IDLE(e), 0)] for e in (0, 1)])
        flag = lambda: [asm.bitoff((1, 213), 2)] if mask == SQUARE else []   # (680's Square flag: no affection list later)
        rel = asm.setbyte(PRV(j), 0)
        held = asm.if_byte(PRV(j), "==", 0, back)
        ops = [asm.ret(), top, _ifkey(mask, rel), asm.goto(held), rel] + flag() + [again(top), held,
               asm.if_byte(LEAVING, "==", 0, back), asm.setbyte(PRV(j), 1)] + flag() + body + [back]
        scripts[ents["press%d" % j]] = {0: ops + [asm.ret()]}
    # L2 + R2: leave (asks first)
    top = wait()
    idle = again(top)
    rx, ry, rz, rt = ctx.lab_back
    text = "Director\n“That's a wrap?”"
    ask, first = hb._ask(sec, text, ["Back to the station.", "Keep going."])
    ask[0] = hb._window(text + "\n{CHOICE}Back to the station.\n{CHOICE}Keep going.", 0, 90, 120)
    gone = asm.bitoff((1, 213), 2)
    stay = asm.setbyte(LEAVING, 0)
    wait30 = hb._w(30)
    go = asm.setbyte(LEAVING, 1)
    scripts[ents["leave"]] = {0: [asm.ret(), top, _ifkey(L2, idle), _ifkey(R2, idle), asm.goto(go), idle, go] + ask +
                              [asm.if_byte((5, 241), "!=", first, gone), stay, again(top),       # (first = leave)
                               gone, Op(b"\x54\x01"), Op(b"\x54\x02"), hb._uc(0), hb._menu(0),
                               mapjump(ctx, STATION, rx, ry, rt, 0), wait30, asm.goto_back(wait30), asm.ret()]}

    # the readouts
    texts = {}
    width = 0
    for e in (0, 1):
        for k, (label, _) in enumerate(models):
            t = "~%s ~~~~~\nAnim {VAR} (0-%d)\nX ~{VAR}\nY ~{VAR}\nZ ~{VAR}\nDir {VAR}" % (label, anim_counts[k] - 1)
            body = encode(t)
            marks = [i for i, c in enumerate(body) if c == 0x5E]
            assert len(marks) == 9, (t, marks)
            texts[e, k] = (sec.add_string(body), marks)
            width = max(width, struct.unpack_from("<H", hb._window(t, 0).raw, 6)[0])
    height = 16 * 6 + 9
    for e in (0, 1):
        top = asm.nop()
        ops = [asm.ret(), top]
        for c, a in ((X(e), AX(e)), (Y(e), AY(e)), (Z(e), AZ(e))):
            neg, done = asm.nop(), asm.nop()
            ops += [asm.if_word(c, "<", 0x8000, neg), asm.setword(a, c), asm.goto(done), neg, asm.setword(a, 0),
                    hb._arith(SUB, a, c), done]

        def show(k, e=e):
            tid, marks = texts[e, k]
            sel_m, h_m, s_m = marks[0], marks[1:6], marks[6:9]
            o, out = [], []
            n1, d1 = asm.nop(), asm.nop()
            o += [asm.if_byte(SEL, "==", e, n1), _poke(tid, sel_m, ">"), asm.goto(d1), n1, _poke(tid, sel_m, " "), d1]
            n2, d2 = asm.nop(), asm.nop()
            o += [asm.if_byte(BED(e), "==", 1, n2)] + [_poke(tid, m, ch) for m, ch in zip(h_m, " bed ")] + \
                [asm.goto(d2), n2] + [_poke(tid, m, ch) for m, ch in zip(h_m, "floor")] + [d2]
            for m, c in zip(s_m, (X(e), Y(e), Z(e))):
                n3, d3 = asm.nop(), asm.nop()
                o += [asm.if_word(c, "<", 0x8000, n3), _poke(tid, m, " "), asm.goto(d3), n3, _poke(tid, m, "-"), d3]
            x = 8 if e == 0 else 320 - 8 - width
            o += [Op(bytes([0x50, WIN(e)]) + struct.pack("<HHHH", x, 8, width, height)),
                  Op(bytes([0x52, WIN(e), 0, 1]))]
            for slot, v in enumerate((AN(e), AX(e), AY(e), AZ(e), D(e))):
                o += [Op(bytes([0x42, 6, WIN(e), slot]) + struct.pack("<H", v[1]))]
            return o + [asm.message(WIN(e), tid)]
        ops += dt_chain(M(e), [show(k) for k in range(nm)]) + [hb._w(1), asm.goto_back(top), asm.ret()]
        scripts[ents["disp%d" % e]] = {0: ops}
        top = wait()
        back = again(top)
        scripts[ents["shut%d" % e]] = {0: [asm.ret(), top, Op(bytes([0x76, 0x50, IDLE(e)[1], 1])),   # (PLUS!: stops at 255)
                                           asm.if_byte(IDLE(e), "==", SETTLE, back), Op(bytes([0x54, WIN(e)])), back,
                                           asm.ret()]}

    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    arrive = START[0] + (floor_tri[0],)
    report = ["scene lab (%s): model / animation indices" % LAB]
    for k, (label, entry) in enumerate(models):
        report.append("%d %s: %s" % (k, label, " ".join("%d=%s" % (i, a.split(".")[0])
                                                          for i, a in enumerate(ModelLoader.anims(entry)))))
    return arrive, report


def dt_chain(var, blocks):
    return importlib.import_module("670_movie")._chain(var, blocks)


def _director(ctx, arrive):
    st = Walkmesh(ctx.field(STATION).section("walkmesh"))
    tri = st.find(*DIRECTOR_AT)
    assert tri is not None, DIRECTOR_AT
    cam = Camera(ctx.field(STATION).sections[1])
    face = facing_screen(cam, DIRECTOR_AT[0], DIRECTOR_AT[1], st.height(tri, *DIRECTOR_AT), (0, 1))
    ax, ay, at = arrive

    def talk(sec):
        return choice_menu(sec, "Director\n“Want to direct a scene? Closed set:\n just you, the cast and the lights.”",
                           ["Let's roll.", "Not now."],
                           [[asm.bitoff((1, 213), 2), mapjump(ctx, LAB, ax, ay, at, 0x20)], None], face=True)
    pos = (DIRECTOR_AT[0], DIRECTOR_AT[1], st.height(tri, *DIRECTOR_AT), tri)
    reuse_npc(ctx, STATION, DIRECTOR, DIRECTOR_DONOR, pos, face, talk)
    return pos


def apply(ctx):
    st = Walkmesh(ctx.field(STATION).section("walkmesh"))
    tri = st.find(*DIRECTOR_AT)
    bx, by, bz, bt = beside(ctx, STATION, DIRECTOR_AT[0], DIRECTOR_AT[1], tri, 60)
    ctx.lab_back = (bx, by, bz, bt)
    arrive, report = _lab(ctx)
    _director(ctx, arrive)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "scene_lab.txt"), "w") as fh:
        fh.write("\n".join(report) + "\n")
    print("  677: the scene lab in %s (Director in %s); anim lists in work/scene_lab.txt" % (LAB, STATION))

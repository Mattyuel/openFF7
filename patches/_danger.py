"""(user: "i would like the danger zone meter put back in but used in conjunction with the new prompt system. have
it work by moving away from centre when you make a mistake or miss, and towards centre when you do the prompt
correct") The movie's danger-zone meter (670's gauge and cursor sprites) for the parody films (683-687): the bar
near the top of the view, the cursor on one of `STEPS` spots along it; METER starts at the centre, a miss / a
mistake pushes it `MISS_OUT` further out (from the centre: to a random side), a hit pulls it `HIT_IN` back in;
reaching either end (the red) = the Director's "CUT!": the shoot ends there, paid what was earned.

Per film: `build` (the sprites, sized and placed for its camera, appended to its models), `scripts` (the gauge and
cursor entities), `start` / `hit` / `miss` ops for its director. Each film keeps its own sprite names (`tag`)."""
import math

from ff7 import asm
from ff7.camera import Camera, screen_range
from ff7.models import ModelLoader
from ff7.script import Op
from ff7.walkmesh import Walkmesh

STEPS = 11                      # cursor spots along the bar (0 and STEPS - 1 are in the red)
CENTRE = STEPS // 2
MISS_OUT, HIT_IN = 2, 1
CUT = "Director\n“CUT! CUT! You're all over the place.\n That's a wrap. We'll fix it in post.”"


def _mods():
    import importlib
    return importlib.import_module("670_movie"), importlib.import_module("620_honey_bee")


def build(ctx, f, loader, tag, focus):
    """The gauge and cursor models appended to `loader` (sprite names QG<tag>A / QC<tag>A), placed for a view
    centred on `focus` (x, y, z: where the film's hidden player stands). Returns a dict for `scripts`."""
    mv, _ = _mods()
    mm = mv.mm
    cam = Camera(f.sections[1])
    mesh = Walkmesh(f.section("walkmesh"))
    near = min(mv._view_depth(cam, v) for t in mesh.tris for v in t) * 0.8
    donor_loader = ModelLoader(ctx.field(mm.DONOR_FIELD).section("models"))
    scale = round(ModelLoader.entry_scale(donor_loader.models[mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    k = near / cam.zoom / (3.41 * scale / 512)
    names = {"QG%sA" % tag: tuple("QG%s%s" % (tag, c) for c in "BCD"),
             "QC%sA" % tag: tuple("QC%s%s" % (tag, c) for c in "BCD")}
    old = mv.SPRITES
    mv.SPRITES = names
    try:
        sp = mv._sprites(ctx, mv.GAUGE_PX / 2 * k, mv.CURSOR_PX / 2 * k)
    finally:
        mv.SPRITES = old
    gm = len(loader.models)
    loader.models += [ModelLoader.with_scale(sp[h], scale) for h in names]
    left, top, right, bottom = screen_range(f.section("triggers"))
    sx, sy = cam.project(*focus[:3])
    sx = min(max(sx, left + 160), right - 160)
    sy = min(max(sy, top + 120), bottom - 120)
    gy = sy + mv.GAUGE_Y

    def at(px, py):
        q = mv._unproject(cam, px, py, near)
        return round(q[0]), round(q[1]), round(q[2]), mv._nearest_tri(mesh, q[0], q[1])
    gauge = at(sx, gy)
    cursor = [at(sx + ((b + 0.5) / STEPS - 0.5) * mv.GAUGE_PX, gy - mv.CURSOR_UP) for b in range(STEPS)]

    def tilt(d):                                            # (the quads' x along the screen's x)
        a = d * 2 * math.pi / 256
        p0 = cam.project(*gauge[:3])
        p1 = cam.project(gauge[0] + 50 * math.cos(a), gauge[1] + 50 * math.sin(a), gauge[2])
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        return abs(dy) / (abs(dx) + 1e-9) + (0 if dx > 0 else 100)
    d = min(range(256), key=tilt)
    print("  danger meter %s: gauge %s, cursor %s .. %s, dir %d" % (tag, gauge[:3], cursor[0][:3], cursor[-1][:3], d))
    return dict(model=gm, gauge=gauge, cursor=cursor, dir=d)


def scripts(D, meter, xyzi):
    """{"gauge": {slot: ops}, "cursor": {...}}: 0 init (model, hidden, facing); 2 shown (the cursor at METER's
    spot: REQ it again whenever METER changes); 4 hidden. `xyzi`(x, y, z, tri) -> op."""
    mv, hb = _mods()
    d_ = Op(bytes([0xB3, 0, D["dir"]]))
    g = {0: [Op(bytes([0xA1, D["model"]])), hb._visi(0), d_, asm.ret(), asm.ret()],
         2: [xyzi(*D["gauge"]), hb._visi(1), asm.ret()],
         4: [hb._visi(0), asm.ret()]}
    c = {0: [Op(bytes([0xA1, D["model"] + 1])), hb._visi(0), d_, asm.ret(), asm.ret()],
         2: mv._chain(meter, [[xyzi(*p)] for p in D["cursor"]]) + [hb._visi(1), asm.ret()],
         4: [hb._visi(0), asm.ret()]}
    return {"gauge": g, "cursor": c}


def _req(e, slot):
    return Op(bytes([0x01, e, 0xC0 | slot]))


def start(meter, ents):
    """The meter at the centre and shown. ents = (gauge entity, cursor entity)."""
    return [asm.setbyte(meter, CENTRE)] + [_req(e, 2) for e in ents]


def hide(ents):
    return [_req(e, 4) for e in ents]


def hit(meter, cursor):
    """A hit: METER HIT_IN towards the centre."""
    up, down, done = asm.nop(), asm.nop(), asm.nop()
    return [asm.if_byte(meter, "<", CENTRE, up), Op(bytes([0x85, meter[0] << 4, meter[1], HIT_IN])), asm.goto(done),
            up, asm.if_byte(meter, ">", CENTRE, done), Op(bytes([0x87, meter[0] << 4, meter[1], HIT_IN])),
            done, _req(cursor, 2)]


def miss(meter, side, rnd, cursor, red):
    """A miss / mistake: METER MISS_OUT away from the centre (at the centre: a random side, kept in `side`),
    clamped to the ends; at an end, goto `red`."""
    left, right, push_r, clamp_l, done, stay = (asm.nop() for _ in range(6))
    ops = [asm.if_byte(meter, "==", CENTRE, left),                      # (at the centre: a side at random)
           Op(bytes([0x99, rnd[0], rnd[1]])), Op(bytes([0x8D, rnd[0] << 4, rnd[1], 2])), asm.setbyte(side, rnd),
           asm.goto(push_r), left,
           asm.setbyte(side, 0), asm.if_byte(meter, ">", CENTRE, push_r), asm.setbyte(side, 1), push_r,
           asm.if_byte(side, "==", 1, clamp_l)]
    # side 1 = out towards STEPS - 1, else towards 0 ("if not (a cmp b) goto")
    ops += [asm.if_byte(meter, ">=", STEPS - 1 - MISS_OUT, right), asm.setbyte(meter, STEPS - 1), asm.goto(done),
            right, Op(bytes([0x85, meter[0] << 4, meter[1], MISS_OUT])), asm.goto(done),
            clamp_l, asm.if_byte(meter, "<=", MISS_OUT, stay), asm.setbyte(meter, 0), asm.goto(done),
            stay, Op(bytes([0x87, meter[0] << 4, meter[1], MISS_OUT])),
            done, _req(cursor, 2)]
    nored = asm.nop()
    in_red = asm.nop()
    ops += [asm.if_byte(meter, "==", 0, in_red), asm.goto(red), in_red,
            asm.if_byte(meter, "==", STEPS - 1, nored), asm.goto(red), nored]
    return ops


# (user: "bring back the final 5 seconds confirm spamming to reach the right danger zone like before for bonus gil.
# This would be put in all scenes") after the last rep: the call, then `FINISH_FRAMES` frames in which every [OK]
# press pushes the meter one step right and it slips one step back every `DECAY` frames; reaching the right end =
# the finisher (the fanfare, PAY += the film's bonus), else it fizzles. 687's tutorial gives 10 s.
FINISH_FRAMES, DECAY = 150, 12
FINISH_CALL = "Director\n“Last five seconds! FINISHER! Mash\n {PURPLE}[OK]{WHITE} and push the needle into the red!”"
FINISH_BONUS = 20               # PAY units (each film pays PAY x its PAY_HIT gil)
FINISH_WIN = "Director\n“WOW! What a FINISHER! Bonus!”"
FINISH_MISS = "Director\n“...And it fizzles. We'll take it.”"
FANFARE = 5                     # AKAO 10 index (670's finisher)


def finisher(meter, pr, ok, cnt, dec, cursor, frames=FINISH_FRAMES):
    """(ops, win label, lose label): the timed mash; `pr` = the press variable (set to `ok` by an [OK] press,
    cleared here), cnt a temp word, dec a temp byte. The caller puts its own ops after each label."""
    top, nopress, nodec, notop, win, lose, cap = (asm.nop() for _ in range(7))
    ops = [asm.setbyte(pr, 0), asm.setword(cnt, 0), asm.setbyte(dec, 0),
           top, Op(b"\x24\x01\x00"), Op(bytes([0x96, cnt[0], cnt[1]])),           # (WAIT 1, INC2 cnt)
           asm.if_byte(pr, "==", ok, nopress), asm.setbyte(pr, 0),
           asm.if_byte(meter, "<", STEPS - 1, cap), Op(bytes([0x95, meter[0], meter[1]])), cap, _req(cursor, 2),
           asm.if_byte(meter, ">=", STEPS - 1, nopress), asm.goto(win),
           nopress, asm.setbyte(pr, 0), Op(bytes([0x95, dec[0], dec[1]])), asm.if_byte(dec, ">=", DECAY, nodec),
           asm.setbyte(dec, 0), asm.if_byte(meter, ">", 0, nodec), Op(bytes([0x87, meter[0] << 4, meter[1], 1])),
           _req(cursor, 2),
           nodec, asm.if_word(cnt, "<", frames, notop), asm.goto_back(top), notop, asm.goto(lose)]
    return ops, win, lose


def fanfare():
    return Op(bytes([0xF2, 0, 0, 0, 0x10, FANFARE]) + bytes(8))


def finale(say, meter, pr, ok, cnt, dec, ents, pay, arith, frames=FINISH_FRAMES, call=FINISH_CALL, win_lines=(),
           bonus=FINISH_BONUS):
    """The whole finisher for a film's director: the call, the mash, the fanfare + bonus or the fizzle, the meter
    hidden. say(text) -> ops; arith = 620 `_arith`; ents = (gauge, cursor)."""
    ops, win, lose = finisher(meter, pr, ok, cnt, dec, ents[1], frames)
    done = asm.nop()
    out = say(call) + ops + [win, Op(b"\x54\x01"), fanfare(), arith(0x86, pay, bonus)] + say(FINISH_WIN)
    for t in win_lines:
        out += say(t)
    return out + [asm.goto(done), lose, Op(b"\x54\x01")] + say(FINISH_MISS) + [done] + hide(ents)


def cut(say, ents, pay, then=()):
    """(label, ops): the red: the Director calls it, the meter hidden, `then` (ops), on to the film's pay."""
    lab = asm.nop()
    return lab, [lab, Op(b"\x54\x01"), Op(b"\x54\x02")] + hide(ents) + say(CUT) + list(then) + [asm.goto(pay)]

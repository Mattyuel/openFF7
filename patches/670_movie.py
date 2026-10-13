"""The movie minigame (user's design).

Once every Honey Bee girl has been seen at affection 20 (all 20 `HB_KID` bits),
a cameraman (junon_report2, the Junon reporter with the camera) and a red-haired
woman, Ruby (midgal_woman: red hair, black jacket and skirt, red top), stand in
Wall Market (mrkt2, right of the item shop). He has heard rumours of a man who
can handle sexy women and offers a starring role: accepting jumps to the shoot.

The shoot is a new field (`FIELD`, a copy of mds7_w3: the Sector 7 slums room
upstairs with three beds) with a blank script. Bare Cloud (620's zcla.hrc) and
Ruby's bare copy (`_bare_ruby`: jacket, skirt, stockings, gloves and boots in
her skin colour, sleeves / skirt / boots shrunk to the limbs) go through all
six `POSITIONS`, one minute each (6 minutes), moving between the beds (user);
the cameraman films beside each spot (FFBC). Her body is the Honey Bee
dancer's skeleton (same bones and lengths, same stand/walk/run anims), so the
dancer poses 620 builds (dzbt, dzbl, dzbf, dzbg, dzbh, dzbk) play on her.

Play: press OK as fast as you dare (counted when IFKEY 0x220, held, goes up -> down). Every tick (~8 frames) the
director (entity 0) takes the presses since the last tick, P:
    VEL = VEL*5/6 + P*A - B + (POS - 500)/C       (VEL stored + 1000, clamped +-VMAX)
    POS += VEL                                     (0..1000, starts 500)
so pressing pushes the cursor right, stopping lets it fall left, it keeps its
momentum, and the further it is from the middle the harder it runs away.
Below DANGER or above 1000 - DANGER = game over (the take is ruined, no pay).
The thrusting speed follows a smoothed press rate in 4 steps: each pose is
resampled to `SPEEDS` frames. The gauge (a red | green | red bar) and the cursor are
sprite models (as the quest markers) floated in front of the camera: per
position, from the screen spot inverted through the field camera.
She talks while it plays (`LINES`): a window the player can't close (WMODE
.. 01, as the Gold Saucer's GP window) shut by entity `hush` ~2 s later;
"head" and "head reverse" are muffled (user).

After six minutes: "That's a wrap", back in Wall Market beside him; he tells
you to come back for your cut, and from 30 play-clock minutes later
(`HB_MINUTES`) his talk pays presses x 10 gil (`MOVIE_*`, bank 1 218-222).
Music: Costa del Sol (COSTA, name table 35; user). Turks' Theme, asked first,
is RHYTHM 45 (the track the Gongaga jungle and the Wutai bar play when the
Turks show up).
"""
import math
import struct

import _marker_models as mm
from _config import HB_KID, HB_MINUTES, MOVIE_AT, MOVIE_PRESSES, MOVIE_STATE
from _recruit import sound
from _travel import CHOICE, add_npc, beside

from ff7 import asm
from ff7.camera import Camera, screen_range
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

FIELD, BASE, WALL = "whitebg1", "mds7_w3", "mrkt2"
CAMERA_AT, RUBY_AT = (310, 378), (386, 314)          # mrkt2: right of the item shop (rendered)
CAMERA_DONOR, RUBY_DONOR = ("junone2", 6), ("jun_i2", 6)
CAMERA_IDLE, CAMERA_FILM = "FDCB.yos", "FFBC.yos"    # camera held low / at his eye
MUSIC = 35                                          # COSTA: Costa del Sol (user; was Turks' Theme, RHYTHM 45)
OK_KEY = 0x220                                      # OK, as every original script tests it: IFKEY (0x61220D) / IFKEYON
                                                    # (0x61225D) with mask bit 0x200 read the field header's +0x78 held /
                                                    # +0x80 new keys, else +0x68 / +0x70; 0x20 alone never fired (user)
MINUTE = 1800                                       # frames per position (30 fps)
SPEEDS = (20, 15, 11, 8)                            # frames per stroke, slowest to fastest
RATE_STEPS = (30, 60, 95)                           # smoothed press rate thresholds for steps 1-3
A, B, C, VMAX, DANGER = 5, 6, 50, 45, 100           # physics (tuned in a Python model of the same integer maths)
TICK_WAIT = 4                                       # frames the director waits per tick (+ its own ~4 turns)
PAY_RATE, PAY_DELAY = 10, 30                        # gil per press; play minutes before the cut

# Positions (user: all six used so far, moving between the beds). Spots are
# (x, y, dz, DIR); "bed" picks the bed's raised walkmesh piece under (x, y).
# Offsets from 620's user-tuned layouts, turned to each bed's long axis (y).
POSITIONS = [
    dict(name="mission", girl=("DZBT", (-225, -60, 0, 0x00), True), cloud=("ZCTA", (-220, -25, -4, 0x80), True),
         camera=(-130, -60, 0xC0)),                                         # left bed, she lies, head to the pillow
    # middle bed, Cloud's head on the pillow; she (user) a body width to her right (x 0 -> 18): over his line;
    # then (user) slightly lower onto him (raise 18 -> 14) and slightly back (y -87 -> -91: she faces +y)
    dict(name="cowgirl", girl=("DZBL", (18, -91, 14, 0x80), True), cloud=("ZCTD", (18, -95, 0, 0x80), True),
         camera=(-130, -60, 0x40)),
    dict(name="dog", girl=("DZBF", (227, -125, 0, 0x00), True), cloud=("ZCTB", (225, -103, 0, 0x00), True),
         camera=(90, -60, 0x40)),                                           # right bed
    dict(name="edge", girl=("DZBG", (-225, -150, 0, 0x80), False), cloud=("ZCTF", (-225, -161, 0, 0x80), False),
         camera=(-130, -180, 0xC0)),                                        # bent over the left bed's foot
    dict(name="headrev", girl=("DZBH", (-225, -54, 0, 0x80), True), cloud=("ZCTE", (-225, -150, 0, 0x80), False),
         camera=(-130, -180, 0xC0)),                                        # on her back, head over the foot
    # on the floor in front of the beds; she (user) half a head further from him (x 50 -> 42)
    dict(name="head", girl=("DZBK", (42, -230, 0, 0x40), False), cloud=("ZCTE", (80, -230, 0, 0xC0), False),
         camera=(140, -235, 0xC0)),
]
LINES = {   # Ruby, while it plays (in turn); head / head reverse: muffled (user); then more, more specific (user)
    "mission": ["Mmm... the camera loves you.", "Kiss my neck... yes, right there...",
                "Pin my wrists down, star.", "Look me in the eyes while you do it.",
                "Deeper... oh, deeper!", "Wrap my legs round you... don't let go.",
                "Harder, star!", "Don't you dare stop now!"],
    "cowgirl": ["Lie back... let me ride you.", "Grab my hips. Hold on tight.",
                "Mmm, you fill me up so good...", "Squeeze my ass... harder!",
                "Watch me bounce for the camera...", "Can you keep up with me?",
                "Oh! Oh, yes! Right there!", "I'm not stopping till you beg."],
    "dog": ["Ah! Right there!", "Pull my hair!", "Spank me! Harder!", "Grab my waist and pull me back...",
            "Don't you dare slow down...", "Mmm... deeper!", "Make me scream for the camera!",
            "Oh, you're a natural!"],
    "edge": ["Ah... the whole bed's shaking...", "Pull my hair back... yes!", "Grip my hips... don't let go.",
             "Faster... faster!", "Spank me! Again!", "Bend me over further...", "Mmm, hold on to me...",
             "Oh, yes... yes!"],
    "headrev": ["Mmph... mmmh!", "Mmf! Mmmf...", "(She grabs your thighs and pulls you in.)\n Mmmh!",
                "Hnnh... mmh...", "Gk... mmh! Mmmh...", "(She moans around you.)\n Mmmmh...!",
                "Mmm... mmm... mmm!", "Hmmf! Mmmh..."],
    "head": ["Mmm... mmph!", "(She guides your hand into her hair.)\n Mmmh!", "Mmf... mmh, mmh...",
             "(She looks up at you.) Mmm...", "Hmmm... mmmh!", "Gk... mmf! Mmmh...",
             "(She pulls your hips closer.)\n Mmph!", "Mmph! Mmm..."],
}
LINES_EACH = 8
SAY_EVERY, SAY_FOR = 75, 60                          # frames between her lines; frames each stays up

# temp vars (this field only)
POS, VEL, PR, TOT, FR, RATE, T, S, NEXT, BKT, EARN, EL = ((6, a) for a in range(100, 124, 2))
P, STEP, NEW, RUN, K, HELD = (5, 130), (5, 131), (5, 132), (5, 133), (5, 134), (5, 135)
GIL = (6, 140)                                       # mrkt2: the cut (temp word)

# Ruby bare (user, second version: "look like the original, just with bare shoulders, legs,
# feet; leave the rest of the coat", "pants need to be skin too", "don't change the size, just
# make skin color"): the upper arms (sleeves), the skirt (hip piece and its box round each
# thigh's top), the thighs, the shins (stockings, boot shafts) and the feet (boots): dress colours
# -> SKIN, shapes as they are except the boots (user: the size of feet: shafts BOOT, feet FOOT)
# and the skirt's box round each thigh's top (it stuck out at the sides and back: the user marked
# it) brought in to the thigh (LIMB_TOP).
# The chest (jacket, red top, belt), the cuffs and the gloves stay. Colours are B, G, R as the
# .p files store them.
RUBY_HRC, BARE_HRC = "cbfe.hrc", "ZRHA.HRC"
SKIN = (153, 204, 255)
DRESS = {(25, 25, 25), (0, 76, 153), (204, 204, 204), (255, 255, 255)}   # black, brown boots, grey, sleeve trim
BARE = {"hip", "uparm", "femur", "tibia", "foot"}
BOOT, FOOT = 0.6, 0.6
BUTT = -2.4                               # the skirt's back hem corners (were -3.15: a sharp point; user's sketch)
LIMB_TOP = 1.3                            # the skirt's box round each thigh: this x the thigh's half width


def _hb():
    from importlib import import_module
    return import_module("620_honey_bee")


def _dates():
    from importlib import import_module
    return import_module("660_dates")


# ---- models -----------------------------------------------------------------
def _bare_ruby(ctx):
    """ZRHA.HRC: cbfe.hrc with the BARE parts copied (rsd ZRHB.., p ZRIB..)."""
    hrc = ctx.char_file(RUBY_HRC).decode("latin-1")
    lines = [l.strip() for l in hrc.splitlines()]
    k = lines.index(next(l for l in lines if l.startswith(":BONES"))) + 1
    parts = []
    while k < len(lines):
        if not lines[k]:
            k += 1
            continue
        bone, rs = lines[k], lines[k + 3].split()[1:]
        parts += [(bone, r) for r in rs]
        k += 4
    assert len(parts) == 15 and parts[2] == ("head", "CBGD"), parts
    n = 0
    for bone, old in parts:
        side = bone[2:] if bone[:2] in ("l_", "r_") else bone
        if side not in BARE:
            continue
        n += 1
        rs, ply = "ZRH" + chr(ord("A") + n), "ZRI" + chr(ord("A") + n)
        assert hrc.count("1 %s" % old) == 1, old
        hrc = hrc.replace("1 %s" % old, "1 %s" % rs)
        r = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
        oldp = r.split("PLY=")[1][:4]
        ctx.char_file(rs.lower() + ".rsd", r.replace("PLY=%s." % oldp, "PLY=%s." % ply).encode("latin-1"))
        d = bytearray(ctx.char_file(oldp.lower() + ".p"))
        h = struct.unpack_from("<16I", d, 0)
        nv, nn, nunk, nt, nc, ne, npoly = h[3], h[4], h[5], h[6], h[7], h[8], h[9]
        o_c = 128 + 12 * nv + 12 * nn + 12 * nunk + 8 * nt
        o_p = o_c + 4 * nc + 4 * npoly + 4 * ne
        assert nc == nv, (bone, nc, nv)
        cols = [tuple(d[o_c + 4 * i:o_c + 4 * i + 3]) for i in range(nc)]
        V = [list(struct.unpack_from("<3f", d, 128 + 12 * i)) for i in range(nv)]

        def scale(idx, f, fz=1.0, cx=0.0, cy=0.0):
            for i in idx:
                V[i][0] = cx + (V[i][0] - cx) * f
                V[i][1] = cy + (V[i][1] - cy) * f
                V[i][2] *= fz
        bare = {i for i in range(nv) if cols[i] in DRESS}
        if side == "femur":                                        # (user) the skirt's box at the thigh's top,
            box = [i for i in range(nv) if cols[i] == (25, 25, 25) and V[i][2] > -3.0]   # brought in to the thigh
            ring = [i for i in range(nv) if i not in box]
            assert len(box) == 8, (bone, len(box))
            span = lambda idx, a: (min(V[i][a] for i in idx), max(V[i][a] for i in idx))
            (x0, x1), (y0, y1) = span(ring, 0), span(ring, 1)
            (bx0, bx1), (by0, by1) = span(box, 0), span(box, 1)
            half = (x1 - x0) / 2 * LIMB_TOP
            for i in box:
                V[i][0] = (x0 + x1) / 2 + (V[i][0] - (bx0 + bx1) / 2) * min(1.0, half / ((bx1 - bx0) / 2))
                V[i][1] = (y0 + y1) / 2 + (V[i][1] - (by0 + by1) / 2) * min(1.0, half / ((by1 - by0) / 2))
        if side == "hip":                                          # (user: "her butt is very sharp") the skirt's
            back = [i for i in range(nv) if V[i][1] < -2.0]          # two back hem corners (y -3.15) pulled in
            assert len(back) == 2, len(back)
            for i in back:
                V[i][1] = BUTT
        if side == "tibia":                                        # the boot shaft
            boot = [i for i in range(nv) if cols[i] == (0, 76, 153)]
            leg = [i for i in range(nv) if cols[i] == (25, 25, 25)]
            assert len(boot) == 8 and len(leg) == 8, (bone, len(boot))
            scale(boot, BOOT, cx=sum(V[i][0] for i in leg) / 8, cy=sum(V[i][1] for i in leg) / 8)
        elif side == "foot":
            scale(range(nv), FOOT, FOOT)
        assert bare, bone
        for i in range(nv):
            struct.pack_into("<3f", d, 128 + 12 * i, *V[i])
        for i in bare:
            d[o_c + 4 * i:o_c + 4 * i + 3] = bytes(SKIN)
        for j in range(npoly):                                       # polygon colours: all three corners bare
            vs = struct.unpack_from("<12H", d, o_p + 24 * j)[1:4]
            o = o_c + 4 * nc + 4 * j
            if all(v in bare for v in vs) and tuple(d[o:o + 3]) in DRESS:
                d[o:o + 3] = bytes(SKIN)
        ctx.char_file(ply.lower() + ".p", bytes(d))
    assert n == 9, n
    ctx.char_file(BARE_HRC.lower(), hrc.encode("latin-1"))


def _speeds(ctx):
    """Each position's two poses resampled to every SPEEDS frame count: girl ZM<p><s>,
    Cloud ZN<p><s> (p = A.., s = 0..3). Returns ([girl names], [Cloud names]) in
    position-major order."""
    from ff7 import fieldanim as fa
    girl, cloud = [], []
    for p, pos in enumerate(POSITIONS):
        for who, base, out in (("girl", pos["girl"][0], girl), ("cloud", pos["cloud"][0], cloud)):
            src = fa.Anim(ctx.char_file(base.lower() + ".a"))
            frames = src.frames
            assert len(frames) == 15, (base, len(frames))
            for s, n in enumerate(SPEEDS):
                name = ("ZM" if who == "girl" else "ZN") + chr(ord("A") + p) + str(s)
                a = fa.Anim(ctx.char_file(base.lower() + ".a"))
                a.frames = [frames[i * len(frames) // n] for i in range(n)]
                ctx.char_file(name.lower() + ".a", a.build())
                out.append(name + ".tor")
    return girl, cloud


GAUGE_W, GAUGE_H = 64, 8                    # texture pixels (in a 64 x 64 texture)
GAUGE_PX, CURSOR_PX, CURSOR_UP = 45, 12, 8   # on-screen widths (user: the bar a quarter of its first 180); cursor
                                            # above the bar (screen px)
GAUGE_Y = -80                               # the bar's screen y from the view centre (user: at +88 it was below
                                            # the screen: the view sits higher than the centred guess)
LINE_Y = 168                                # Ruby's lines: window at the bottom (the gauge is at the top)
SPRITES = {"QGAA": ("QGAB", "QGAC", "QGAD"), "QCUA": ("QCUB", "QCUC", "QCUD")}
PALETTE = [(0, 0, 0, 0), (255, 255, 255, 255), (40, 40, 230, 255), (60, 200, 60, 255),
           (40, 230, 255, 255), (30, 30, 30, 255)]       # B, G, R, A: clear, white, red, green, yellow, dark


def _gauge_pixels():
    px = bytearray(64 * 64)
    red = round(GAUGE_W * DANGER / 1000)
    for y in range(GAUGE_H):
        for x in range(GAUGE_W):
            c = 1 if y in (0, GAUGE_H - 1) or x in (0, GAUGE_W - 1) else 2 if x <= red or x >= GAUGE_W - 1 - red else 3
            px[y * 64 + x] = c
    for y in range(1, GAUGE_H - 1):                          # the middle tick
        px[y * 64 + 31] = px[y * 64 + 32] = 1
    return px


def _cursor_pixels():
    px = bytearray(64 * 64)
    for y in range(12):                                      # a yellow arrowhead pointing down, dark rim
        a, b = y * 2 // 3, 15 - y * 2 // 3
        for x in range(a, b + 1):
            px[y * 64 + x] = 5 if x in (a, b) or y == 0 else 4
    return px


def _sprites(ctx, half_gauge, half_cursor):
    """The gauge bar and the cursor as one-bone sprite models (the quest markers' way).
    Returns {hrc: loader entry (the Glacier Map entry, unscaled)}."""
    donor_p = ctx.char_file(mm.DONOR_P)
    hrc_text = ctx.char_file("gujc.hrc").decode("latin1")
    template = ctx.char_file(mm.TEX_TEMPLATE)
    donor = ModelLoader(ctx.field(mm.DONOR_FIELD).section("models")).models[mm.DONOR_MODEL]
    out = {}
    for hrc, (rsd, ply, tex) in SPRITES.items():
        try:
            ctx.char_file(hrc.lower() + ".hrc")
            raise AssertionError("%s already in char.lgp" % hrc)
        except KeyError:
            pass
        gauge = hrc == "QGAA"
        crop = (0, 0, GAUGE_W - 1, GAUGE_H - 1) if gauge else (0, 0, 15, 11)
        half = half_gauge if gauge else half_cursor
        ctx.char_file(hrc.lower() + ".hrc",
                      hrc_text.replace("icemap_sk", hrc.lower() + "_sk").replace("1 GUJD", "1 " + rsd).encode("latin1"))
        ctx.char_file(rsd.lower() + ".rsd",
                      ("@RSD940102\r\nPLY=%s.PLY\r\nMAT=%s.MAT\r\nGRP=%s.GRP\r\nNTEX=1\r\nTEX[0]=%s.TIM\r\n"
                       % (ply, ply, ply, tex)).encode("latin1"))
        ctx.char_file(ply.lower() + ".p", mm.mesh(donor_p, crop, half))
        head = bytearray(template[:0xEC])
        struct.pack_into("<II", head, 0x3C, 64, 64)
        pal = b"".join(bytes(c) for c in PALETTE).ljust(16 * 4, b"\0")
        ctx.char_file(tex.lower() + ".tex", bytes(head) + pal + bytes(_gauge_pixels() if gauge else _cursor_pixels()))
        out[hrc] = donor.replace(mm.DONOR_HRC, (hrc + ".HRC").encode("ascii"))
    return out


# ---- the shoot ------------------------------------------------------------------
def _spot(mesh, x, y, dz=0, high=False):
    """(x, y, z, tri) on the highest (a bed piece) or lowest (the floor) triangle under (x, y)."""
    tris = [t for t in range(len(mesh.tris)) if mesh.contains(t, x, y)]
    assert tris, (x, y)
    t = max(tris, key=lambda t: mesh.height(t, x, y) * (1 if high else -1))
    return x, y, mesh.height(t, x, y) + dz, t


def _unproject(cam, sx, sy, depth):
    """Field point at screen (sx, sy) (pixels from the background centre) and view depth."""
    sv = [sx * depth / cam.zoom, sy * depth / cam.zoom, depth]
    v = [sum(cam.axes[r][c] * (sv[r] - cam.pos[r]) for r in range(3)) / 4096 for c in range(3)]
    n = [sum(a * a for a in cam.axes[r]) / 4096 ** 2 for r in range(3)]
    assert all(abs(x - 1) < 0.01 for x in n), n
    return v


def _view_depth(cam, p):
    return sum(a * c for a, c in zip(cam.axes[2], p)) / 4096 + cam.pos[2]


def _nearest_tri(mesh, x, y):
    t = mesh.find(round(x), round(y))
    if t is not None:
        return t
    return min(range(len(mesh.tris)), key=lambda i: math.dist(mesh.center(i)[:2], (x, y)))


def _shoot(ctx, back):
    hb, dt = _hb(), _dates()
    f = ctx.new_field(FIELD, ctx.field(BASE).build())
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    loader = ModelLoader(f.section("models"))
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    assert names[:5] == ["produce", "direct", "ad", "cloud", "child"], names
    assert len(loader.models) == 2 and ModelLoader.name(loader.models[0]).endswith("main_n_cloud.char")

    # spots
    places = []
    for pos in POSITIONS:
        g = _spot(mesh, *pos["girl"][1][:2], pos["girl"][1][2], pos["girl"][2])
        c = _spot(mesh, *pos["cloud"][1][:2], pos["cloud"][1][2], pos["cloud"][2])
        cx, cy, cdir = pos["camera"]
        cm = _spot(mesh, cx, cy)
        focus = _spot(mesh, *pos["girl"][1][:2], 0, pos["girl"][2])
        places.append(dict(girl=g, gdir=pos["girl"][1][3], cloud=c, cdir=pos["cloud"][1][3], cam=cm, camdir=cdir,
                           focus=focus))
    # gauge per position: the camera centres on the (hidden) player at `focus`, clamped
    # to the scroll range; the bar sits near the top of the view, nearer the camera
    # than any floor point (drawn over everything), the cursor above it
    left, top, right, bottom = screen_range(f.section("triggers"))
    near = min(_view_depth(cam, v) for t in mesh.tris for v in t) * 0.8
    field_scale = loader.scale
    donor_loader = ModelLoader(ctx.field(mm.DONOR_FIELD).section("models"))
    sprite_scale = round(ModelLoader.entry_scale(donor_loader.models[mm.DONOR_MODEL]) * field_scale / donor_loader.scale)
    unit = 3.41 * sprite_scale / 512                         # field units per model unit (3.41 at 512: renders)
    half = GAUGE_PX / 2 * near / cam.zoom / unit
    half_cursor = CURSOR_PX / 2 * near / cam.zoom / unit
    for pl in places:
        sx, sy = cam.project(*pl["focus"][:3])
        sx = min(max(sx, left + 160), right - 160)
        sy = min(max(sy, top + 120), bottom - 120)
        gy = sy + GAUGE_Y
        g = _unproject(cam, sx, gy, near)
        pl["gauge"] = (round(g[0]), round(g[1]), round(g[2]), _nearest_tri(mesh, g[0], g[1]))
        pl["cursor"] = []
        for b in range(21):                                  # bucket b = POS // 50
            off = ((b * 50 + 25) - 500) / 1000 * GAUGE_PX
            q = _unproject(cam, sx + off, gy - CURSOR_UP, near)
            pl["cursor"].append((round(q[0]), round(q[1]), round(q[2]), _nearest_tri(mesh, q[0], q[1])))
        back_x, back_y = cam.project(*g)
        assert abs(back_x - sx) < 2 and abs(back_y - gy) < 2, (back_x, back_y, sx, gy)
    from ff7.camera import facing_screen
    # the sprites' width runs along the model's x = the field's (cos a, sin a) for DIR d: pick the
    # d whose x axis projects flattest (horizontal) on screen, pointing right, at the bar's spot
    gx, gy_, gz = places[0]["gauge"][:3]

    def tilt(d):
        a = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy_, gz), cam.project(gx + 50 * math.cos(a), gy_ + 50 * math.sin(a), gz)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        return abs(dy) / (abs(dx) + 1e-9) + (0 if dx > 0 else 100)
    sprite_dir = min(range(256), key=tilt)
    assert tilt(sprite_dir) < 0.05, tilt(sprite_dir)

    # models: 2 bare Cloud, 3 Ruby bare, 4 cameraman, 5 gauge, 6 cursor
    girl_anims, cloud_anims = _speeds(ctx)
    cl0 = loader.models[0]
    loader.models.append(ModelLoader.with_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), cloud_anims))
    cfirst = len(ModelLoader.anims(loader.models[2])) - len(cloud_anims)
    rd = ModelLoader(ctx.field(RUBY_DONOR[0]).section("models"))
    r = loader.add_from(rd, RUBY_DONOR[1])
    loader.models[r] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[r], BARE_HRC,
                                                                   ModelLoader.name(loader.models[r])[:-5] + "_b.char"),
                                              girl_anims)
    gfirst = len(ModelLoader.anims(loader.models[r])) - len(girl_anims)
    cd = ModelLoader(ctx.field(CAMERA_DONOR[0]).section("models"))
    cm = loader.add_from(cd, CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(CAMERA_FILM)
    sprites = _sprites(ctx, half, half_cursor)
    for hrc in ("QGAA", "QCUA"):
        loader.models.append(ModelLoader.with_scale(sprites[hrc], sprite_scale))
    assert len(loader.models) == 7

    ents = {}
    for name in ("cloudb", "ruby", "camera", "gauge", "cursor", "keys", "voice", "hush"):
        ents[name] = len(sec.entity_names)
        sec.entity_names.append(name.encode("latin-1").ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    CL, CH = 3, 4
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]        # TLKON 01, SOLID 01 (new ops each use)
    by_p = lambda make: _chain(P, [make(p, pl) for p, pl in enumerate(places)])
    scripts = {}
    xyzi = hb._xyzi
    d_ = lambda d: Op(bytes([0xB3, 0, d]))
    scripts[CL] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*places[0]["focus"]), hb._visi(0), asm.ret(),
                       asm.ret()],
                   2: by_p(lambda p, pl: [xyzi(*pl["focus"])]) + [asm.ret()]}
    scripts[CH] = {0: [Op(bytes([0xA1, 1])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()]}

    def pose(first, who, wdir):
        def make(p, pl):
            steps = [[Op(bytes([0xA2, first + 4 * p + s, 1])), Op(bytes([0xAE, first + 4 * p + s, 1]))]
                     for s in range(4)]
            return [xyzi(*pl[who]), d_(pl[wdir]), hb._visi(1)] + _chain(STEP, steps)
        return by_p(make) + [asm.ret()]
    scripts[ents["cloudb"]] = {0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                               2: pose(cfirst, "cloud", "cdir")}
    scripts[ents["ruby"]] = {0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                             2: pose(gfirst, "girl", "gdir")}
    scripts[ents["camera"]] = {0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide()
                               + [Op(bytes([0xA2, film, 1])), Op(bytes([0xAE, film, 1])), asm.ret(), asm.ret()],
                               2: by_p(lambda p, pl: [xyzi(*pl["cam"]), d_(pl["camdir"])]) + [hb._visi(1), asm.ret()]}
    scripts[ents["gauge"]] = {0: [Op(bytes([0xA1, 5])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret(), asm.ret()],
                              2: by_p(lambda p, pl: [xyzi(*pl["gauge"])]) + [hb._visi(1), asm.ret()]}
    # cursor: every frame while RUN, bucket = POS / 50 -> its spot for the position
    loop, idle = asm.nop(), asm.nop()
    cur = [loop, asm.if_byte(RUN, "==", 1, idle), asm.setword(BKT, POS), hb._arith(0x8C, BKT, 50)]
    cur += by_p(lambda p, pl: _tree(BKT, 0, 20, lambda b: [xyzi(*pl["cursor"][b])]) + [hb._visi(1), hb._w(1),
                                                                                         asm.goto_back(loop)])
    cur += [idle, hb._visi(0), hb._w(1), asm.goto_back(loop)]
    scripts[ents["cursor"]] = {0: [Op(bytes([0xA1, 6])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret()] + cur
                               + [asm.ret()]}
    # keys: once a frame while RUN, OK held (IFKEY: the held copy, +0x78 with the 0x200 selector)
    # going from up to down counts a press, and the frame count. (IFKEYON's "newly pressed" copy
    # caught only some presses in-game (user): it lasts one input update, and the script looks
    # once a frame.) TOT is added up by the director.
    # Jumps land on real ops (no NOP labels) so a pass is at most 7 ops: one per frame. It
    # counts from field entry; the director zeroes PR and FR at "Action!".
    wait = hb._w(1)
    back1, up = asm.goto_back(wait), asm.setbyte(HELD, 0)
    scripts[ents["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x96, FR[0], FR[1]])),
                                 Op(bytes([0x30]) + struct.pack("<H", OK_KEY) + b"\x00", target=up),
                                 asm.if_byte(HELD, "==", 0, back1), asm.setbyte(HELD, 1),
                                 Op(bytes([0x96, PR[0], PR[1]])), back1,
                                 up, asm.goto_back(wait), asm.ret()]}
    # voice: a line every SAY_EVERY frames while RUN; hush closes it SAY_FOR frames later
    vl, vdone = asm.nop(), asm.nop()
    voice = [asm.ret(), vl, hb._w(SAY_EVERY), asm.if_byte(RUN, "==", 1, vdone),
             Op(bytes([0x95, K[0], K[1]])), Op(bytes([0x8D, K[0] << 4, K[1], LINES_EACH]))]   # INC K, MOD K

    def line(p, pl):
        out = []
        assert len(LINES[POSITIONS[p]["name"]]) == LINES_EACH, POSITIONS[p]["name"]
        for k_, text in enumerate(LINES[POSITIONS[p]["name"]]):
            t = "Ruby\n“%s”" % text if not text.startswith("(") else "Ruby\n%s" % text
            out.append([Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, LINE_Y), hb._req(ents["hush"], 2, wait=False),
                        asm.message(1, sec.add_string(_encode(t)))])
        return _chain(K, out)
    voice += by_p(line) + [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(SAY_FOR), Op(b"\x54\x01"), asm.ret()]}

    # director
    lost, wrap, tick = asm.nop(), asm.nop(), asm.nop()
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    place_all = lambda: [hb._req(e, 2) for e in (CL, ents["cloudb"], ents["ruby"], ents["camera"], ents["gauge"])]
    main = [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS, 500), asm.setword(VEL, 1000),
            asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(P, 0),
            asm.setbyte(STEP, 1), asm.setbyte(K, 0), asm.setword(NEXT, MINUTE)] + place_all() + [hb._w(20)]
    main += say("“Places, everyone! Here's how it works, star:\n tap OK to keep the rhythm going.”")
    main += say("“Faster means more footage, and every push\n is 10 gil in your pocket. But watch the meter:\n"
                " push too hard and it runs away from you,\n ease off and it all falls flat.”")
    main += say("“Hit the red at either end and the shoot's\n over. Six positions, a minute each.\n Ready?”")
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, MUSIC]) + bytes(8)), hb._w(15)]
    main += say("“...And... ACTION!”")
    main += [asm.setword(FR, 0), asm.setword(PR, 0), asm.setbyte(RUN, 1)]
    # a tick
    main += [tick, hb._w(TICK_WAIT), asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
             hb._arith(0x8A, VEL, 5), hb._arith(0x8C, VEL, 6),
             hb._arith(0x86, VEL, 1000 - 1000 * 5 // 6 - B - 500 // C),
             asm.setword(S, T), hb._arith(0x8A, S, A), hb._arith(0x86, VEL, S),
             asm.setword(S, POS), hb._arith(0x8C, S, C), hb._arith(0x86, VEL, S)]
    lo, hi = asm.nop(), asm.nop()
    main += [asm.if_word(VEL, "<", 1000 - VMAX, lo), asm.setword(VEL, 1000 - VMAX), lo,      # clamp
             asm.if_word(VEL, ">", 1000 + VMAX, hi), asm.setword(VEL, 1000 + VMAX), hi,
             asm.setword(S, POS), hb._arith(0x86, S, VEL),
             asm.if_word(S, ">=", 1000 + DANGER, lost),                       # into the left red
             asm.setword(POS, S), hb._arith(0x88, POS, 1000),
             asm.if_word(POS, "<=", 1000 - DANGER, lost)]                     # into the right red
    # thrusting speed: RATE = RATE * 3/4 + presses * 16 -> step 0-3
    done, same = asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(S, T), hb._arith(0x8A, S, 16),
             hb._arith(0x86, RATE, S), asm.setbyte(NEW, 0)]
    for s, th in enumerate(RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW),
             hb._req(ents["cloudb"], 2, wait=False), hb._req(ents["ruby"], 2, wait=False), same]
    # the next position each minute
    stay = asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay), hb._arith(0x86, NEXT, MINUTE),
             Op(bytes([0x85, P[0] << 4, P[1], 1])), asm.if_byte(P, "<", len(POSITIONS), wrap),
             # (user: the switch showed awkward, late model moves) paused and hidden by a fade
             asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(hb.FADE_OUT), Op(b"\x6C")] + place_all() + \
            [hb._w(10), Op(hb.FADE_IN), Op(b"\x6C"), asm.setword(PR, 0), asm.setbyte(RUN, 1),
             stay, asm.goto_back(tick)]
    rx, ry, rz, rt, rdir = back
    def out():                                   # jump back; then wait (a main that reaches RET starts over)
        stop = hb._w(30)
        return [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(WALL), rx, ry, rt, rdir), stop,
                asm.goto_back(stop), asm.ret()]
    # a CUT: nothing owed (user: ending early still paid), cleared before anything else
    main += [lost, asm.setbyte(RUN, 0), asm.setbyte(MOVIE_STATE, 0), asm.setword(MOVIE_PRESSES, 0),
             Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! You lost it, man!\n That take's ruined... Let's try again\n some other day.”")
    main += [Op(hb.FADE_OUT), Op(b"\x6C"), asm.setbyte(MOVIE_STATE, 0)] + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! Magnificent!”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    scripts[0] = {0: [asm.ret()] + main}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    return places[0]["focus"]


def _encode(t):
    from ff7.text import encode
    return encode(t)


def _chain(var, blocks):
    """if var == k: blocks[k] (each falls through to the end)."""
    out, end = [], asm.nop()
    for k, ops in enumerate(blocks):
        nxt = asm.nop()
        out += [asm.if_byte(var, "==", k, nxt)] + ops + [asm.goto(end), nxt]
    return out + [end]


def _tree(var, lo, hi, leaf):
    """Binary search on word var in lo..hi (values past hi take hi's leaf)."""
    if lo == hi:
        return leaf(lo)
    mid, right, end = (lo + hi) // 2, asm.nop(), asm.nop()
    return ([asm.if_word(var, "<=", mid, right)] + _tree(var, lo, mid, leaf) + [asm.goto(end), right]
            + _tree(var, mid + 1, hi, leaf) + [end])


# ---- Wall Market --------------------------------------------------------------
def _unlocked_or(skip):
    """Ops jumping to `skip` unless all 20 HB_KID bits are set."""
    assert [k for k in HB_KID] == [((1, 214 + i // 8), i % 8) for i in range(20)]
    return [asm.if_byte((1, 214), "==", 0xFF, skip), asm.if_byte((1, 215), "==", 0xFF, skip)] + \
           [asm.if_byte((1, 216), "bit_on", b, skip) for b in range(4)]


def _wall_market(ctx, focus):
    hb = _hb()
    f = ctx.field(WALL)
    mesh = Walkmesh(f.section("walkmesh"))
    loader = ModelLoader(f.section("models"))
    cm = loader.add_from(ModelLoader(ctx.field(CAMERA_DONOR[0]).section("models")), CAMERA_DONOR[1])
    idle = ModelLoader.anims(loader.models[cm]).index(CAMERA_IDLE)
    ru = loader.add_from(ModelLoader(ctx.field(RUBY_DONOR[0]).section("models")), RUBY_DONOR[1])
    f.set_section("models", loader.build())
    assert len(loader.models) <= 16, len(loader.models)
    from ff7.camera import facing_screen
    cam = Camera(f.sections[1])
    spots = {}
    for key, (x, y) in (("cam", CAMERA_AT), ("ruby", RUBY_AT)):
        t = mesh.find(x, y)
        assert t is not None, (key, x, y)
        spots[key] = (x, y, mesh.height(t, x, y), t)

    def hidden(extra=()):
        shown, hide = asm.nop(), asm.nop()
        return _unlocked_or(hide) + list(extra) + [asm.goto(shown), hide, Op(b"\x7E\x01"), Op(b"\xC7\x01"),
                                                    hb._visi(0), shown]

    def talk(sec):
        say = lambda t: hb._say(sec, "Cameraman\n" + t)
        end, pitch, wait_ = asm.nop(), asm.nop(), asm.nop()
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8), asm.if_byte(MOVIE_STATE, "!=", 0, pitch),
               asm.setword(EL, HB_MINUTES), hb._arith(0x88, EL, MOVIE_AT), asm.if_word(EL, ">=", PAY_DELAY, wait_)]
        capped = asm.nop()
        ops += [asm.setword(GIL, MOVIE_PRESSES), asm.if_word(GIL, ">", 65535 // PAY_RATE, capped),
                asm.setword(GIL, 65535 // PAY_RATE), capped, hb._arith(0x8A, GIL, PAY_RATE),
                Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), sound(0x168)]
        paid = say("“The film's flying off the shelves!\n Here's your cut, star: {VAR} gil.”")
        paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
        ops += paid + [asm.setbyte(MOVIE_STATE, 0), asm.goto(end)]
        ops += [wait_] + say("“Still selling the footage. Come back\n a little later for your cut.”") + [asm.goto(end)]
        ops += [pitch] + say("“Well, well... I've heard rumours about\n a man who can handle sexy women.\n"
                             " That's you, isn't it?”")
        ask, first = hb._ask(sec, "Cameraman\n“I'm shooting a new movie and I need\n a star. Interested?”",
                             ["Lights, camera, action!", "Not now."])
        no = asm.nop()
        ops += ask + [asm.if_byte(CHOICE, "==", first, no)]
        ops += say("“That's my man! To the set!”")
        x, y, z, t = focus
        ops += [Op(hb.FADE_OUT), Op(b"\x6C"), asm.setbyte(MOVIE_STATE, 0),
                asm.mapjump(ctx.maplist.index(FIELD), x, y, t, 0), asm.ret()]
        ops += [no] + say("“Suit yourself. The offer stands.”")
        return ops + [end, hb._uc(0), asm.ret()]

    # back from the shoot: he tells you to come back for your cut
    sec0 = Script.parse(f.sections[0])
    debrief_text = ("Cameraman\n“What a performance! Give me half an hour\n to sell the footage, then come and get\n"
                    " your cut of the profits.”")
    tid = sec0.add_string(_encode(debrief_text))
    f.sections[0] = sec0.build()
    skip = asm.nop()
    debrief = [asm.if_byte(MOVIE_STATE, "==", 2, skip), hb._uc(1), hb._menu(1), hb._window(debrief_text),
               asm.message(0, tid), asm.setbyte(MOVIE_STATE, 1), hb._menu(0), hb._uc(0), skip]
    cdir = facing_screen(cam, *spots["cam"][:3], (0, 1))
    add_npc(ctx, WALL, "filmman", cm, spots["cam"], cdir, talk,
            init_extra=hidden([Op(bytes([0xA2, idle, 1])), Op(bytes([0xAE, idle, 1]))]), main=debrief)

    def ruby_talk(sec):
        return [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + \
            hb._say(sec, "Ruby\n“So you're my co-star? Don't disappoint\n me, handsome.”") + [hb._uc(0), asm.ret()]
    add_npc(ctx, WALL, "ruby", ru, spots["ruby"], facing_screen(cam, *spots["ruby"][:3], (0, 1)), ruby_talk,
            init_extra=hidden())
    # where the shoot sends you back: beside him, facing him
    x, y, z, t = spots["cam"]
    bx, by, bz, bt = beside(ctx, WALL, x, y, t, 40)
    return bx, by, bz, bt, _dates()._dir_to(x - bx, y - by)


def apply(ctx):
    _bare_ruby(ctx)
    focus = _spot(Walkmesh(ctx.field(BASE).section("walkmesh")), *POSITIONS[0]["girl"][1][:2], 0, True)
    back = _wall_market(ctx, focus)
    _shoot(ctx, back)

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
the cameraman stands beside each spot, holding the camera at his side (FDCB frame 0, user). Her body is the Honey Bee
dancer's skeleton (same bones and lengths, same stand/walk/run anims), so the
dancer poses 620 builds (dzbt, dzbl, dzbf, dzbg, dzbh, dzbk) play on her.

Play: press OK as fast as you dare (counted when IFKEY 0x220, held, goes up -> down). Every tick (~8 frames) the
director (entity 0) takes the presses since the last tick, P:
    VEL = VEL*5/6 + P*A - B + (POS - 500)/C       (VEL stored + 1000, clamped +-VMAX)
    POS += VEL                                     (0..1000, starts 500)
so pressing pushes the cursor right, stopping lets it fall left, it keeps its
momentum, and the further it is from the middle the harder it runs away.
Below DANGER or above 1000 - DANGER = CUT: the shoot ends, but (user) he still sells what was shot (a low score).
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
from _config import HB_KID, HB_MINUTES, MOVIE_AT, MOVIE_GIRL, MOVIE_PRESSES, MOVIE_STATE
from _recruit import sound
from _travel import CHOICE, add_npc, beside, screen_step

from ff7 import asm
from ff7.camera import Camera, facing_screen, screen_range
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
MINUTE = 900                                        # frames per position (30 fps; user: 30 s each, was a minute)
SPEEDS = (20, 15, 11, 8)                            # frames per stroke, slowest to fastest
RATE_STEPS = (30, 60, 95)                           # smoothed press rate thresholds for steps 1-3
A, B, C, VMAX, DANGER = 6, 5, 60, 40, 100           # physics (tuned in a Python model of the same integer maths;
                                                    # user: the cursor wouldn't go up: easier, ~2.5 presses/s holds)
TICK = 10                                           # frames per physics tick, by the frame count (the director's
                                                    # own pace varied, and the push per press with it)
BACK_DOWN = 100                                     # Wall Market return: 4 paces (~25 each) down the screen
PAY_RATE, PAY_DELAY = 10, 30                        # gil per press; play minutes before the cut
SKYE_PAY = 2                                        # (user) Skye's videos: double

# Positions (user: all six used so far, moving between the beds). Spots are
# (x, y, dz, DIR); "bed" picks the bed's raised walkmesh piece under (x, y).
# Offsets from 620's user-tuned layouts, turned to each bed's long axis (y).
POSITIONS = [
    # (user) she slightly right and down on screen: (-225, -60) -> (-215, -59)
    dict(name="mission", girl=("DZBT", (-215, -59, 0, 0x00), True), cloud=("ZCTA", (-220, -25, -4, 0x80), True),
         camera=(-130, -60, 0xC0)),                                         # left bed, she lies, head to the pillow
    # middle bed, Cloud's head on the pillow; she (user) a body width to her right (x 0 -> 18): over his line;
    # then (user) slightly lower onto him (raise 18 -> 14) and slightly back (y -87 -> -91: she faces +y);
    # then (user) a little towards his head (-91 -> -95: his head is on the pillow, -y)
    dict(name="cowgirl", girl=("DZBL", (18, -95, 14, 0x80), True), cloud=("ZCTD", (18, -95, 0, 0x80), True),
         camera=(-130, -60, 0x40)),
    dict(name="dog", girl=("DZBF", (227, -125, 0, 0x00), True), cloud=("ZCTN", (225, -103, 0, 0x00), True),
         camera=(90, -60, 0x40)),                                           # right bed
    dict(name="edge", girl=("DZBG", (-225, -150, 0, 0x80), False), cloud=("ZCTF", (-225, -161, 0, 0x80), False),
         camera=(-130, -180, 0xC0)),                                        # bent over the left bed's foot
    dict(name="headrev", girl=("DZBH", (-225, -54, 0, 0x80), True), cloud=("ZCTE", (-225, -150, 0, 0x80), False),
         camera=(-130, -180, 0xC0)),                                        # on her back, head over the foot
    # (user) "prone": flat on her stomach on the right bed, hips lifting and rocking forward (ZRPA, `_prone`);
    # Cloud knelt over her pelvis facing her head (ZCTB); his spot from both poses (`_place`)
    dict(name="prone", girl=("ZRPA", (227, -110, 0, 0x00), True), cloud=("ZCTO", "prone", True),
         camera=(90, -60, None)),
    # (user) Scarlet's date pose, "behind": she leans forward, arms out, right knee up, in front of standing
    # Cloud facing his way (660 `_wall` on her skeleton: same XYZI and DIR as his ZCTE, her pelvis in the
    # anim); (user) at the foot of the leftmost bed, by the left wall, facing the bed (+y: she leans over
    # it); the cameraman faces them
    dict(name="behind", girl=("ZRWA", (-255, -160, 0, "cloud"), False), cloud=("ZCTE", (-255, -160, 0, 0x80), False),
         camera=(-160, -200, None)),
    # (user) Tifa's date pose, "holding": she koala-hugs standing Cloud (660 `_koala`: same XYZI, DIR + 128,
    # on his ZCTH); (user) at the end of a bed: the floor off the right bed's front end, side on
    dict(name="holding", girl=("ZRKA", (193, -165, 0, "facing"), False), cloud=("ZCTH", (193, -165, 0, "screen-left"),
         False), camera=(110, -245, None)),
    # (user) "69": Cloud on his back on the middle bed thrusting (as cowgirl); she on all fours over him the
    # other way, knees by his head, her head over his pelvis, bobbing (ZR6A: dzbf + a head bob, `_bob`). Her
    # spot and DIR come from both poses (`_place`); muffled
    dict(name="69", girl=("ZR6A", "69", True), cloud=("ZCTD", (18, -95, 0, 0x80), True), camera=(-130, -60, None)),
    # (user) "head" last: the finisher position
    # on the floor in front of the beds; she (user) half a head further from him (x 50 -> 42)
    # (user, since) y -230 -> -224: to her left (his right)
    dict(name="head", girl=("ZRTA", (42, -224, 0, 0x40), False), cloud=("ZCTE", (80, -230, 0, 0xC0), False),
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
    # muffled ones (user, since): Cloud asks her things ("C:" = his line) and she answers as she can
    "headrev": ["Mmph... mmmh!", "C:Comfortable down there?", "Mmf! Mmmf... (She gives a thumbs up.)",
                "(She grabs your thighs and pulls you in.)\n Mmmh!", "C:Was that a yes or a no?",
                "Mmmh! Mmh-hmm!", "Hnnh... mmh...", "C:Should I keep going?",
                "(She nods as best she can.)\n Mmmmh!", "C:Sorry, what was that?", "Mmf! Mmmf...!", "Hmmf! Mmmh..."],
    "behind": ["Against the wall... yes!", "Pull my hair back!", "Hold my hips and don't let go...",
               "Harder! Make the wall shake!", "Mmm, kiss my neck...", "Spank me, star!",
               "Don't stop... don't stop...", "Oh! Right there!"],
    "holding": ["Hold me up... don't drop me!", "Mmm, you're so strong...", "Squeeze my ass tighter...",
                "Bounce me harder!", "I'm all yours, star...", "Kiss me... mmm...",
                "Oh, I'm slipping... hold on!", "Yes! Yes! Right there!"],
    "69": ["Mmph... mmmh!", "C:Mmf... you taste good.", "(She pushes her hips down onto you.)\n Mmmf!",
           "C:Is this okay for the camera?", "Mmf... mmh, mmh!", "(She squeezes your thighs.) Mmmh!",
           "C:Do you want me to stop?", "(She shakes her head hard.)\n Mmh-mmh!", "Hnnh... mmph!",
           "C:I'll take that as a no.", "(Her hips grind against you.)\n Mmmmh...!", "Gk... mmh! Mmmh..."],
    "prone": ["Mmm... pin me down...", "Pull my hair!", "Harder... push me into the bed!",
              "Grab my ass... yes!", "Don't stop, star... don't stop...", "Spank me! Again!",
              "Ah! Deeper... deeper!", "Oh, I can't move... I love it!"],
    "head": ["Mmm... mmph!", "C:You okay down there?", "(She looks up at you.) Mmm-hmm!",
             "(She guides your hand into her hair.)\n Mmmh!", "C:Like that?", "Mmf! (She nods.) Mmh, mmh...",
             "C:Do you need a break?", "(She pulls your hips closer.)\n Mmph!", "Hmmm... mmmh!",
             "C:What's your favourite colour?", "Mmf... mmh mmf? (She glares.)", "Mmph! Mmm..."],
}
LINES_EACH = 12                                      # 12 for the muffled ones; the others' 8 repeat (one text each)
SAY_EVERY, SAY_FOR = 75, 60                          # frames between her lines; frames each stays up
# (user) 5 s before the end of the last position the cameraman calls for a finisher: from then the
# right (high) red is a finisher, not a CUT: fanfare, a bonus on the spot of the girl's gil per
# press x FINISH_BONUS (Ruby 1,000, Skye 2,000), and the shoot ends as a wrap
FINISH_FRAMES, FINISH_BONUS, FINISH_SAY_FOR, FANFARE = 150, 100, 120, 5     # FANFARE: AKAO index (620's part twos)
AFTERMATH = ("Ruby\n(Ruby swallows, wipes her lips with her\n thumb and sinks back, breathless.)",
             "Skye\n(Skye licks her lips clean, sighs happily\n and blows a kiss at the camera.)")   # (user) Ruby, Skye

# temp vars (this field only)
POS, VEL, PR, TOT, FR, RATE, T, S, NEXT, BKT, EARN, EL, NT = ((6, a) for a in range(100, 126, 2))
P, STEP, NEW, RUN, K, HELD = (5, 130), (5, 131), (5, 132), (5, 133), (5, 134), (5, 135)
FIN, FT = (5, 136), (6, 126)                         # finisher on (last 5 s of the last position); scratch word
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
RUBY_HRC, BARE_HRC, RUBY_STAND = "cbfe.hrc", "ZRHA.HRC", "dxid.a"   # (the dancer's stand pose)
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


# Skye (user: the blue-haired girl in the bikini; unlocked by a full shoot with Ruby): gold_cgirl
# (crcin_1 model 4, GOFD.HRC: the Honey Bee dancer's skeleton, so every pose and anim of Ruby's fits).
# Her bare copy ZSKA.HRC: the bikini (purple, B,G,R 52,0,32) in her skin colour; the yellow streamers
# behind her (44,153,153: hip and head pieces; user: "remove the yellow things") collapsed to one point
# (their triangles vanish; asserted none of them shares a triangle with the rest)
SKYE_DONOR, SKYE_HRC, SKYE_BARE = ("crcin_1", 4), "gofd.hrc", "ZSKA.HRC"
SKYE_SKIN, SKYE_BIKINI, SKYE_STREAMER = (166, 194, 247), (52, 0, 32), (44, 153, 153)


def _bare_skye(ctx):
    hrc = ctx.char_file(SKYE_HRC).decode("latin-1")
    lines = [l.strip() for l in hrc.splitlines()]
    k = lines.index(next(l for l in lines if l.startswith(":BONES"))) + 1
    parts = []
    while k < len(lines):
        if not lines[k]:
            k += 1
            continue
        parts += [(lines[k], r) for r in lines[k + 3].split()[1:]]
        k += 4
    n = 0
    for bone, old in parts:
        r = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
        oldp = r.split("PLY=")[1][:4]
        d = bytearray(ctx.char_file(oldp.lower() + ".p"))
        h = struct.unpack_from("<16I", d, 0)
        nv, nn, nunk, nt, nc, ne, npoly = h[3], h[4], h[5], h[6], h[7], h[8], h[9]
        o_c = 128 + 12 * nv + 12 * nn + 12 * nunk + 8 * nt
        o_p = o_c + 4 * nc + 4 * npoly + 4 * ne
        cols = [tuple(d[o_c + 4 * i:o_c + 4 * i + 3]) for i in range(nc)]
        if SKYE_BIKINI not in cols and SKYE_STREAMER not in cols:
            continue
        n += 1
        rs, ply = "ZSK" + chr(ord("A") + n), "ZSL" + chr(ord("A") + n)
        for name in (rs.lower() + ".rsd", ply.lower() + ".p"):
            try:
                ctx.char_file(name)
                raise AssertionError("%s already in char.lgp" % name)
            except KeyError:
                pass
        assert hrc.count("1 %s" % old) == 1, old
        hrc = hrc.replace("1 %s" % old, "1 %s" % rs)
        ctx.char_file(rs.lower() + ".rsd", r.replace("PLY=%s." % oldp, "PLY=%s." % ply).encode("latin-1"))
        polys = [struct.unpack_from("<12H", d, o_p + 24 * j)[1:4] for j in range(npoly)]
        streamer = {i for i in range(nc) if cols[i] == SKYE_STREAMER}
        if streamer:
            for vs in polys:
                assert all(v in streamer for v in vs) or not any(v in streamer for v in vs), (bone, vs)
            body = [i for i in range(nv) if i not in streamer]
            c = [sum(struct.unpack_from("<3f", d, 128 + 12 * i)[a] for i in body) / len(body) for a in range(3)]
            for i in streamer:
                struct.pack_into("<3f", d, 128 + 12 * i, *c)
        for i in range(nc):
            if cols[i] == SKYE_BIKINI:
                d[o_c + 4 * i:o_c + 4 * i + 3] = bytes(SKYE_SKIN)
        for j in range(npoly):
            o = o_c + 4 * nc + 4 * j
            if tuple(d[o:o + 3]) == SKYE_BIKINI:
                d[o:o + 3] = bytes(SKYE_SKIN)
        ctx.char_file(ply.lower() + ".p", bytes(d))
    assert n >= 2, n                                 # at least the hip and chest
    ctx.char_file(SKYE_BARE.lower(), hrc.encode("latin-1"))


# her lines (user: "a little more dirty"), by position; head / head reverse / 69 muffled
SKYE_LINES = {
    "mission": ["Mmm, fuck me like you mean it, star.", "Spread me wider... yes!", "Choke me a little... just a little.",
                "Pound me into this mattress!", "Oh god, you're so deep...", "Don't you dare pull out!",
                "Harder! Make me scream!", "Use me... I'm all yours."],
    "cowgirl": ["Shut up and let me ride you.", "Grab my tits... squeeze!", "Feel how wet I am?",
                "Slap my ass while I ride you!", "Oh fuck... I'm gonna bounce till you break.",
                "Watch me take every inch...", "Don't you dare finish yet!", "Mmm, I'm riding you raw!"],
    "dog": ["Pull my hair and fuck me harder!", "Spank me! Leave a mark!", "Call me your dirty girl!",
            "Deeper! Ram it deeper!", "Grab my hips and slam me back!", "Oh fuck, right there!",
            "Make the camera blush, star!", "Don't stop... I'm so close!"],
    "edge": ["Bend me over and take me!", "Pull my hair back... harder!", "Fuck me till the bed breaks!",
             "Spank me! Again! Again!", "Oh god, you're splitting me!", "Hold me down... yes!",
             "Faster! Fuck me faster!", "Mmm, I'm dripping..."],
    "headrev": ["Mmph... mmmh!", "C:You like it rough, huh?", "(She gags and moans for more.)\n Ghk! Mmmh!",
                "C:Too much?", "(She grabs your ass and pulls you deeper.)", "Mmf! Mmmf...",
                "C:Say please.", "Mmmf-mmh! (Something like 'please'.)", "Hnnh... mmph!",
                "C:Dirty girl.", "(Tears in her eyes, she grins.)\n Mmmh!", "Gk... mmh! Mmmh..."],
    "head": ["Mmm... mmph!", "C:You've done this before, haven't you?", "(She winks up at you.)\n Mmmh!",
             "(She pulls your hand to the back of her head.)", "C:Want it all?", "(She takes you all the way.)\n Mmmph!",
             "C:Look at the camera.", "(She looks up at you, eyes watering.)\n Mmmh!", "Ghk! Mmf... mmh...",
             "C:Good girl.", "(She moans, wanting more.)\n Mmmh!", "Mmph! Mmm..."],
    "behind": ["Fuck me against the wall, star!", "Pull my hair! Harder!", "Spank my ass red!",
               "Pin me to the wall... don't stop!", "Oh fuck, I can't stand up!", "Bite my neck...",
               "Harder! Make the whole building hear!", "Yes! Yes! Fuck yes!"],
    "holding": ["Hold me up and fuck me!", "Squeeze my ass while you bounce me!", "Don't drop me... deeper!",
                "Mmm, you're so strong... harder!", "I'm gonna wrap round you all night...",
                "Fuck me in the air!", "Oh god, I'm slipping onto you...", "Yes! Bounce me harder!"],
    "69": ["Mmph... mmmh!", "C:Mmf... you're soaking.", "(She grinds her hips onto your face.)\n Mmmf!",
           "C:Who's gonna finish first?", "(She moans around you, eager.)\n Mmmmh!", "Mmf... mmh, mmh...",
           "C:Don't you dare stop.", "(She digs her nails into your thighs.)", "Hnnh... mmph!",
           "C:Again? Already?", "(She shudders.)\n Gk... mmh! Mmmh...", "Mmm... mmm... mmm!"],
    "prone": ["Pin me down and fuck me!", "Pull my hair! Pull it!", "Spank me while you pound me!",
              "Push me into the bed... harder!", "Oh fuck, I can't move...", "Call me your slut!",
              "Deeper! Don't you dare stop!", "Fuck... I'm gonna come!"],
}


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
GAUGE_PX, CURSOR_PX, CURSOR_UP = 45, 6, 6   # (user: cursor 50%: 12 -> 6)  # on-screen widths (user: the bar a quarter of its first 180); cursor
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


# "69" (user): her all-fours rock (620's dzbf) with the head lowered BOB_DOWN and bobbing BOB more and
# back each stroke. "prone" (user): flat on her stomach (her stand pose tipped face down, feet in line
# with the shins), the hips lifting PRONE_LIFT and pushing PRONE_FWD forward each stroke, shoulders and
# knees staying on the bed (chest / thighs re-aimed each frame), 15 frames
BOB_DOWN, BOB, PRONE_LIFT, PRONE_FWD, PRONE_PAD = 25, 20, 1.6, 0.8, 0.8
UNIT = 3.41                                         # field units per model unit at entry scale 512 (renders)
SIX9_RAISE, SIX9_DOWN = 6, 10                       # (user) "69": her raised a bit, further down his body
PRONE_BACK, PRONE_LEFT = 5, 4                       # (user) "prone": Cloud towards her feet, to his left
PRONE_UP = 8                                        # ... lying on her (his own prone pose: ~her body's depth up)


def _align(fa, a, b):
    """The smallest rotation turning direction a into b."""
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]
    a, b = unit(a), unit(b)
    ax = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    s = math.sqrt(sum(c * c for c in ax))
    return fa.axis_angle(ax, math.degrees(math.atan2(s, sum(a[k] * b[k] for k in range(3))))) if s > 1e-9 \
        else fa.euler_matrix(0, 0, 0)


def _bob(ctx):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    names = [b[0] for b in sk]
    h = names.index("head")
    base = fa.Anim(ctx.char_file("dzbf.a"))
    n = len(base.frames)
    frames = []
    for t, (rr, rp, rots) in enumerate(base.frames):
        root = [rp[0], -rp[1], rp[2]]
        W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
        y0 = fa.forward(sk, rr, root, rots)[h][2][1]
        a = BOB_DOWN + BOB * (1 - math.cos(2 * math.pi * t / n)) / 2
        for sg in (1, -1):                           # the sense that lowers the head (y down)
            Wt = list(W)
            Wt[h] = fa._mul(fa.axis_angle((1.0, 0.0, 0.0), sg * a), W[h])
            local = fa.local_rotations(sk, rr, Wt)
            if fa.forward(sk, rr, root, local)[h][2][1] > y0:
                break
        else:
            raise AssertionError("bob")
        frames.append((rr, rp, local))
    base.frames = frames
    ctx.char_file("zr6a.a", base.build())


def _prone(ctx):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(RUBY_STAND))
    rr, rp, rots = base.frames[0]
    world = [m for m, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
    face_local = fa._vec(fa._t(world[I("head")]), [0.0, 0.0, -1.0])     # she faces -z standing
    for a in (90, -90):
        W = [fa._mul(fa.axis_angle((1.0, 0.0, 0.0), a), m) for m in world]
        if fa._vec(W[I("head")], face_local)[1] > 0.9:                  # face down (y down)
            break
    else:
        raise AssertionError("prone: no face-down turn")
    for s in "lr":
        W[I(s + "_foot")] = W[I(s + "_tibia")]                          # feet in line with the shins
    fk = lambda W, r: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    low = max(p[1] for _, s_, e in fk(W, [0.0, 0.0, 0.0]) for p in (s_, e))
    rest = [0.0, -PRONE_PAD - low, 0.0]                                  # lowest joint PRONE_PAD above the bed
    E0 = fk(W, rest)
    assert E0[I("head")][2][2] < rest[2] - 5, "head not forward (-z)"
    keep = ("chest", "non_1", "non_2", "l_femur", "r_femur")              # their far ends stay put
    target = {n: E0[I(n)][2] for n in keep}
    frames = []
    for t in range(15):
        e = (1 - math.cos(2 * math.pi * t / 15)) / 2
        r = [rest[0], rest[1] - PRONE_LIFT * e, rest[2] - PRONE_FWD * e]   # hips up and forward
        Wt = list(W)
        F = fk(Wt, r)
        for n in keep:
            i = I(n)
            Wt[i] = fa._mul(_align(fa, fa._vec(Wt[i], [0, 0, -1]), [target[n][k] - F[i][1][k] for k in range(3)]),
                            Wt[i])
        Ft = fk(Wt, r)
        for n in keep:
            assert math.dist(Ft[I(n)][2], target[n]) < 1.5, (t, n)       # shoulders / knees near their place
                                                                          # (a re-aimed bone keeps its length)
        frames.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file("zrpa.a", base.build())


# (user) "head": her head tilted HEAD_BACK further back (chin up) than 620's kneel (dzbk), as ZRTA
HEAD_BACK = 20


def _head_back(ctx):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    h = [b[0] for b in sk].index("head")
    rr, rp, rots = fa.Anim(ctx.char_file(RUBY_STAND)).frames[0]
    up_local = fa._vec(fa._t(fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)[h][0]), [0.0, 0.0, -1.0])
    base = fa.Anim(ctx.char_file("dzbk.a"))
    frames = []
    for rr, rp, rots in base.frames:
        root = [rp[0], -rp[1], rp[2]]
        W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
        face = fa._vec(W[h], up_local)[1]
        for sg in (1, -1):                               # the sense that lifts the face (y down)
            Wt = list(W)
            Wt[h] = fa._mul(fa.axis_angle((1.0, 0.0, 0.0), sg * HEAD_BACK), W[h])
            if fa._vec(Wt[h], up_local)[1] < face:
                break
        else:
            raise AssertionError("head back")
        frames.append((rr, rp, fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file("zrta.a", base.build())


# Cloud's bones: the pelvis ("hip") carries the chest and both shoulder bones; the legs hang off the root
UPPER = ("chest", "l_chest", "r_chest")


def _keep_upper(fa, sk, rr, Wt, r, target, tol, also=()):
    """Re-aim UPPER (+ `also`) so each bone's end goes back to `target` (a bone keeps its length:
    the end lands within tol); everything after them keeps its world turn, so it stays put too."""
    I = [b[0] for b in sk].index
    F = fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, Wt))
    for n in UPPER + tuple(also):
        i = I(n)
        Wt[i] = fa._mul(_align(fa, fa._vec(Wt[i], [0, 0, -1]), [target[n][k] - F[i][1][k] for k in range(3)]), Wt[i])
    F = fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, Wt))
    for n in UPPER + tuple(also):
        assert math.dist(F[I(n)][2], target[n]) < tol, n
    return Wt


# (user) dog, Cloud: 620's knelt pound (ZCTB: the thighs swing about the knees, hips up and
# forward) with the upper body held where it starts: a thrust of the hips only, as ZCTN
def _cloud_dog(ctx):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    I = [b[0] for b in sk].index
    base = fa.Anim(ctx.char_file("zctb.a"))
    rr, rp, rots = base.frames[0]
    F0 = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
    target = {n: F0[I(n)][2] for n in UPPER}
    frames = []
    for rr, rp, rots in base.frames:
        r = [rp[0], -rp[1], rp[2]]
        W = [m for m, _, _ in fa.forward(sk, rr, r, rots)]
        for i, b in enumerate(sk):                     # head and arms: as at the start
            if b[1] in UPPER or b[1] in ("l_collar", "r_collar", "l_uparm", "r_uparm", "l_foarm", "r_foarm"):
                W[i] = [m for m, _, _ in F0][i]
        W = _keep_upper(fa, sk, rr, W, r, target, 1.5)
        frames.append((rr, rp, fa.local_rotations(sk, rr, W)))
    base.frames = frames
    ctx.char_file("zctn.a", base.build())


# (user) prone, Cloud: from lying flat on his stomach (his stand pose tipped face down), the
# pelvis and torso tilted CP_TORSO up from the bed (legs flat), the head CP_HEAD down, the arms
# turned down so the hands rest on the bed; each stroke (15 frames) the hips thrust up CP_LIFT,
# knees bending (knees and feet stay on the bed), the upper body held, and back down. ZCTO.
CP_TORSO, CP_HEAD, CP_LIFT, CP_PAD = 30, 15, 1.8, 0.8


def _cloud_prone(ctx):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file("acfe.a"))
    rr, rp, rots = base.frames[0]
    world = [m for m, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
    face_local = fa._vec(fa._t(world[I("head")]), [0.0, 0.0, -1.0])      # he faces -z standing
    for a in (90, -90):
        W = [fa._mul(fa.axis_angle((1.0, 0.0, 0.0), a), m) for m in world]
        if fa._vec(W[I("head")], face_local)[1] > 0.9:                   # face down (y down)
            break
    else:
        raise AssertionError("prone: no face-down turn")
    for s in "lr":
        W[I(s + "_foot")] = W[I(s + "_tibia")]                           # feet in line with the shins
    fk = lambda W, r: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    F = fk(W, [0.0, 0.0, 0.0])
    assert F[I("head")][2][2] < -5, "head not forward (-z)"
    # torso up: turn the pelvis and everything above it about the side axis, the sense lifting the head
    body = [i for i, b in enumerate(sk) if b[0] == "hip" or b[1] != "root" and not b[0][2:] in
            ("hip", "femur", "tibia", "foot")]
    assert sorted(names[i] for i in body) == sorted(["hip", "chest", "head"] + [s + p for s in ("l_", "r_") for p in
                                                    ("chest", "collar", "uparm", "foarm", "hand")])
    for sg in (1, -1):
        R = fa.axis_angle((1.0, 0.0, 0.0), sg * CP_TORSO)
        Wt = [fa._mul(R, m) if i in body else m for i, m in enumerate(W)]
        if fk(Wt, [0.0, 0.0, 0.0])[I("head")][2][1] < F[I("head")][2][1]:
            break
    W = Wt
    for sg in (1, -1):                                                     # head down a little
        Wt = list(W)
        Wt[I("head")] = fa._mul(fa.axis_angle((1.0, 0.0, 0.0), sg * CP_HEAD), W[I("head")])
        if fa._vec(Wt[I("head")], face_local)[1] > fa._vec(W[I("head")], face_local)[1]:
            break
    W = Wt
    low = max(p[1] for n, (_, s_, e) in zip(names, fk(W, [0.0, 0.0, 0.0])) if I(n) not in body for p in (s_, e))
    rest = [0.0, -CP_PAD - low, 0.0]                                        # legs CP_PAD above the bed
    floor = rest[1] + low + CP_PAD                                          # the bed (y down)
    # arms (the shoulders are low with the torso only CP_TORSO up): upper arm straight down, forearm
    # forward and down to the bed, the hand flat on it, pointing ahead
    F = fk(W, rest)
    bed = floor - CP_PAD / 2                                                # the hands' line (y)
    for s in "lr":
        up, fo = sk[I(s + "_uparm")][2], sk[I(s + "_foarm")][2]
        v = bed - (F[I(s + "_collar")][2][1] + up)                          # elbow to bed
        assert 0 < v < fo, (s, v)
        for p, d in (("_uparm", [0.0, 1.0, 0.0]), ("_foarm", [0.0, v, -math.sqrt(fo * fo - v * v)]),
                     ("_hand", [0.0, 0.0, -1.0])):
            W[I(s + p)] = fa._mul(_align(fa, fa._vec(W[I(s + p)], [0, 0, -1]), d), W[I(s + p)])
    F0 = fk(W, rest)
    for s in "lr":
        assert abs(F0[I(s + "_hand")][2][1] - bed) < 0.05 and abs(F0[I(s + "_foarm")][2][1] - bed) < 0.05, s
    target = {n: F0[I(n)][2] for n in UPPER + ("l_femur", "r_femur")}
    frames = []
    for t in range(15):
        e = (1 - math.cos(2 * math.pi * t / 15)) / 2
        r = [rest[0], rest[1] - CP_LIFT * e, rest[2]]                       # hips up
        Wt = _keep_upper(fa, sk, rr, list(W), r, target, 1.5, also=("l_femur", "r_femur"))
        frames.append((rr, [r[0], -r[1], r[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file("zcto.a", base.build())


def _joints(ctx, hrc, anim):
    """Model-space joint ends of frame 0 (y down), plus 'root'."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    rr, rp, rots = fa.Anim(ctx.char_file(anim)).frames[0]
    root = [rp[0], -rp[1], rp[2]]
    out = {b[0]: e for b, (_, _, e) in zip(sk, fa.forward(sk, rr, root, rots))}
    out["root"] = root
    return out


def _off(m, d):
    """Field (dx, dy, dz) of model point m for an entity with DIR d (faces -z, +x = its left)."""
    a = d * 2 * math.pi / 256
    F = (math.sin(a), -math.cos(a))
    L = (-F[1], F[0])
    return UNIT * (m[0] * L[0] - m[2] * F[0]), UNIT * (m[0] * L[1] - m[2] * F[1]), -UNIT * m[1]


def _place(ctx, pos):
    """Spots worked out from both poses: "69" her (head over his pelvis, facing from his head to it),
    "prone" his (his pelvis over hers, facing her way)."""
    hb = _hb()
    cl_hrc = hb.CLOUD_BARE_HRC.lower()
    if pos["girl"][1] == "69":
        x, y, dz, cd = pos["cloud"][1]
        his = _joints(ctx, cl_hrc, pos["cloud"][0].lower() + ".a")
        P = [c + o for c, o in zip((x, y), _off(his["root"], cd))]
        H = [c + o for c, o in zip((x, y), _off(his["head"], cd))]
        gd = _dates()._dir_to(P[0] - H[0], P[1] - H[1])
        hers = _joints(ctx, RUBY_HRC, pos["girl"][0].lower() + ".a")
        o = _off(hers["head"], gd)
        d = math.hypot(P[0] - H[0], P[1] - H[1])
        u = ((P[0] - H[0]) / d, (P[1] - H[1]) / d)              # down his body
        pos["girl"] = (pos["girl"][0], (round(P[0] - o[0] + u[0] * SIX9_DOWN), round(P[1] - o[1] + u[1] * SIX9_DOWN),
                                        SIX9_RAISE, gd), pos["girl"][2])
    if pos["cloud"][1] == "prone":
        x, y, dz, gd = pos["girl"][1]
        hers = _joints(ctx, RUBY_HRC, pos["girl"][0].lower() + ".a")
        Pg = [c + o for c, o in zip((x, y), _off(hers["root"], gd))]
        his = _joints(ctx, cl_hrc, pos["cloud"][0].lower() + ".a")
        o = _off(his["root"], gd)
        a = gd * 2 * math.pi / 256
        F = (math.sin(a), -math.cos(a))                   # (user) a little towards her feet (-F), to his left (L)
        L = (-F[1], F[0])
        sx = -F[0] * PRONE_BACK + L[0] * PRONE_LEFT
        sy = -F[1] * PRONE_BACK + L[1] * PRONE_LEFT
        pos["cloud"] = (pos["cloud"][0], (round(Pg[0] - o[0] + sx), round(Pg[1] - o[1] + sy), PRONE_UP, gd),
                         pos["cloud"][2])


def _shoot(ctx, back):
    hb, dt = _hb(), _dates()
    _bob(ctx)
    _prone(ctx)
    _head_back(ctx)
    _cloud_dog(ctx)
    _cloud_prone(ctx)
    for pos in POSITIONS:
        _place(ctx, pos)
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
        cx, cy, camdir = pos["camera"]
        cm = _spot(mesh, cx, cy)
        focus = _spot(mesh, *pos["girl"][1][:2], 0, pos["girl"][2])
        side = {"screen-right": (1, 0), "screen-left": (-1, 0)}
        cdir = pos["cloud"][1][3]
        if cdir in side:
            cdir = facing_screen(cam, *c[:3], side[cdir])
        gdir = {"cloud": cdir, "facing": (cdir + 128) % 256}.get(pos["girl"][1][3], pos["girl"][1][3])
        if camdir is None:                                   # the cameraman faces her
            camdir = _dates()._dir_to(g[0] - cm[0], g[1] - cm[1])
        places.append(dict(girl=g, gdir=gdir, cloud=c, cdir=cdir, cam=cm, camdir=camdir, focus=focus))
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
    dt._wall(ctx, "ZRWA.tor", RUBY_HRC, RUBY_STAND)          # (user) "behind": Scarlet's date pose on her
    dt._koala(ctx, "ZRKA.tor", RUBY_HRC, RUBY_STAND)         # (user) "holding": Tifa's koala hug on her
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
    held = ModelLoader.anims(loader.models[cm]).index(CAMERA_IDLE)    # (user) still: the camera at his side
    sprites = _sprites(ctx, half, half_cursor)
    for hrc in ("QGAA", "QCUA"):
        loader.models.append(ModelLoader.with_scale(sprites[hrc], sprite_scale))
    # 7: Skye bare (user: the new girl after a full shoot), Ruby's anims
    sk = loader.add_from(ModelLoader(ctx.field(SKYE_DONOR[0]).section("models")), SKYE_DONOR[1])
    loader.models[sk] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[sk], SKYE_BARE,
                                                                    ModelLoader.name(loader.models[sk])[:-5] + "_b.char"),
                                               girl_anims)
    sfirst = len(ModelLoader.anims(loader.models[sk])) - len(girl_anims)
    assert len(loader.models) == 8 and sk == 7

    ents = {}
    for name in ("cloudb", "ruby", "camera", "gauge", "cursor", "keys", "voice", "hush", "skye", "shout", "hush2"):
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

    def pose(first, who, wdir, girl=None):
        """girl: "ruby" / "skye": shown only if she is this shoot's co-star (MOVIE_GIRL bit 1)."""
        def make(p, pl):
            steps = [[Op(bytes([0xA2, first + 4 * p + s, 1])), Op(bytes([0xAE, first + 4 * p + s, 1]))]
                     for s in range(4)]
            return [xyzi(*pl[who]), d_(pl[wdir]), hb._visi(1)] + _chain(STEP, steps)
        off, head = asm.nop(), []
        if girl:
            head = [asm.if_byte(MOVIE_GIRL, "bit_off" if girl == "ruby" else "bit_on", 1, off)]
        return head + by_p(make) + [asm.ret()] + ([off, hb._visi(0), asm.ret()] if girl else [])
    scripts[ents["cloudb"]] = {0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                               2: pose(cfirst, "cloud", "cdir")}
    scripts[ents["ruby"]] = {0: [Op(bytes([0xA1, 3])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                             2: pose(gfirst, "girl", "gdir", "ruby")}
    scripts[ents["skye"]] = {0: [Op(bytes([0xA1, 7])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                             2: pose(sfirst, "girl", "gdir", "skye")}
    scripts[ents["camera"]] = {0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide()
                               + [Op(bytes([0xA2, held, 1])), asm.ret(), asm.ret()],
                               2: by_p(lambda p, pl: [xyzi(*pl["cam"]), d_(pl["camdir"])]) + [hb._visi(1), hb._canm(held, 0, 0), asm.ret()]}   # (user) still, frame 0 (not in the init: CANM may wait)
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

    texts = {}                                       # one text id per distinct line (8-line positions repeat)

    def lines_of(who, table):
        def line(p, pl):
            out = []
            lines = table[POSITIONS[p]["name"]]
            assert len(lines) in (8, LINES_EACH), (who, POSITIONS[p]["name"], len(lines))
            for k_ in range(LINES_EACH):
                text = lines[k_ % len(lines)]
                if text.startswith("C:"):            # Cloud's line (user: he asks her things)
                    t = "{CLOUD}\n“%s”" % text[2:]
                elif text.startswith("("):
                    t = "%s\n%s" % (who, text)
                else:
                    t = "%s\n“%s”" % (who, text)
                if t not in texts:
                    texts[t] = sec.add_string(_encode(t))
                out.append([Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, LINE_Y),
                            hb._req(ents["hush"], 2, wait=False), asm.message(1, texts[t])]
                           + ([sound(SLAP_SOUND)] if _slaps(text) else []))   # (user) a slap after such lines
            return _chain(K, out)
        return line
    skye_says = asm.nop()
    voice += [asm.if_byte(MOVIE_GIRL, "bit_off", 1, skye_says)]          # bit 1 set: Skye's lines
    voice += by_p(lines_of("Ruby", LINES)) + [asm.goto(vdone), skye_says] + by_p(lines_of("Skye", SKYE_LINES))
    voice += [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(SAY_FOR), Op(b"\x54\x01"), asm.ret()]}
    # the cameraman's call for a finisher: window 2 near the top (below the gauge) that the player
    # can't close (they're mashing OK), shut by hush2; its own entity so the director never waits
    shout = "Cameraman\n“Five seconds left! Go all out, star!\n Give me a FINISHER!”"
    scripts[ents["shout"]] = {0: [asm.ret(), asm.ret()],
                              2: [Op(b"\x52\x02\x00\x01"), hb._window(shout, 2, 8, 56),
                                  hb._req(ents["hush2"], 2, wait=False), asm.message(2, sec.add_string(_encode(shout))),
                                  asm.ret()]}
    scripts[ents["hush2"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(FINISH_SAY_FOR), Op(b"\x54\x02"), asm.ret()]}

    # director
    lost, wrap, tick, hi_red = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    place_all = lambda: [hb._req(e, 2) for e in (CL, ents["cloudb"], ents["ruby"], ents["skye"], ents["camera"],
                                                 ents["gauge"])]
    main = [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS, 500), asm.setword(VEL, 1000),
            asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(P, 0),
            asm.setbyte(STEP, 1), asm.setbyte(K, 0), asm.setword(NEXT, MINUTE), asm.setbyte(FIN, 0)] + place_all() + \
           [hb._w(20)]
    main += [Op(hb.FADE_IN), Op(b"\x6C")]            # (user: the first position showed the models move too)
    main += say("“Places, everyone! Here's how it works, star:\n tap OK to keep the rhythm going.”")
    main += say("“Faster means more footage, and every push\n is 10 gil in your pocket. But watch the meter:\n"
                " push too hard and it runs away from you,\n ease off and it all falls flat.”")
    main += say("“Hit the red at either end and the shoot's\n over. Ten positions, half a minute each.\n Ready?”")
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, MUSIC]) + bytes(8)), hb._w(15)]
    main += say("“...And... ACTION!”")
    main += [asm.setword(FR, 0), asm.setword(PR, 0), asm.setword(NT, TICK), asm.setbyte(RUN, 1)]
    # a tick: every TICK frames by the frame count (FR from `keys`), whatever the director's own pace
    wait1, go = hb._w(1), asm.nop()
    main += [tick, wait1, asm.if_word(FR, "<", NT, go), asm.goto_back(wait1), go, hb._arith(0x86, NT, TICK),
             asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
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
             asm.if_word(POS, "<=", 1000 - DANGER, hi_red)]                   # into the right red
    # the last position's final FINISH_FRAMES: the call for a finisher (once)
    no_call = asm.nop()
    main += [asm.if_byte(P, "==", len(POSITIONS) - 1, no_call), asm.if_byte(FIN, "==", 0, no_call),
             asm.setword(FT, FR), hb._arith(0x86, FT, FINISH_FRAMES), asm.if_word(FT, ">=", NEXT, no_call),
             asm.setbyte(FIN, 1), hb._req(ents["shout"], 2, wait=False), no_call]
    # thrusting speed: RATE = RATE * 3/4 + presses * 16 -> step 0-3
    done, same = asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(S, T), hb._arith(0x8A, S, 16),
             hb._arith(0x86, RATE, S), asm.setbyte(NEW, 0)]
    for s, th in enumerate(RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW),
             hb._req(ents["cloudb"], 2, wait=False), hb._req(ents["ruby"], 2, wait=False),
             hb._req(ents["skye"], 2, wait=False), same]
    # the next position each minute
    stay = asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay), hb._arith(0x86, NEXT, MINUTE),
             asm.if_byte(P, "<", len(POSITIONS) - 1, wrap),
             # (user: the switch showed awkward, late model moves) paused and hidden by a fade; P moves on
             # only once the screen is black (user: things changed before the fade: the cursor and the
             # speed-change REQs read P at once)
             asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(hb.FADE_OUT), Op(b"\x6C"),
             Op(bytes([0x85, P[0] << 4, P[1], 1]))] + place_all() + \
            [hb._w(10), Op(hb.FADE_IN), Op(b"\x6C"), asm.setword(PR, 0), asm.setword(NT, FR),
             hb._arith(0x86, NT, TICK), asm.setbyte(RUN, 1),
             stay, asm.goto_back(tick)]
    rx, ry, rz, rt, rdir = back
    def out():                                   # jump back; then wait (a main that reaches RET starts over)
        stop = hb._w(30)
        return [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(WALL), rx, ry, rt, rdir), stop,
                asm.goto_back(stop), asm.ret()]
    # into the right red: a finisher in the last FINISH_FRAMES (user), else a CUT
    skye_bonus, bonus_done = asm.nop(), asm.nop()
    main += [hi_red, asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(b"\x54\x02"),
             Op(bytes([0xF2, 0, 0, 0, 0x10, FANFARE]) + bytes(8)), hb._w(45)]      # (a pause: they're mashing OK)
    main += say("“WOW! What a FINISHER!\n That's going straight on the poster!”")
    main += [asm.if_byte(MOVIE_GIRL, "bit_off", 1, skye_bonus)]                    # bit 1 set: Skye
    for rate, label in ((PAY_RATE, None), (PAY_RATE * SKYE_PAY, skye_bonus)):
        gil = rate * FINISH_BONUS
        main += ([label] if label else []) + [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)]
        main += say("“Here's a bonus, on the spot:\n {:,} gil. You earned it, star!”".format(gil))
        main += hb._say(sec, AFTERMATH[label is not None])                   # (user) the girl, after it
        main += [asm.goto(bonus_done)] if label is None else [bonus_done]
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             asm.biton(MOVIE_GIRL, 0), Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    # a CUT (user): he still sells what was shot (the presses so far: a low score), same wait for
    # the cut; only a full shoot raises the star rank
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! You lost it, man!\n ...Fine. We'll sell what we've got.”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! Magnificent!”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             asm.biton(MOVIE_GIRL, 0),                                   # (user) a full shoot unlocks Skye
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    black = Op(bytes.fromhex("6b00000000000104" "00"))      # FADE type 4: black at once (as the game's
    scripts[0] = {0: [black, asm.ret()] + main}                    # fields that open on a scene)
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    return places[0]["focus"]


SLAP_SOUND = 0x76                                    # the slap (660's dates, Scarlet's)


def _slaps(text):
    """A line about slapping / spanking (user: a slap sound after it)."""
    return any(w in text.lower() for w in ("slap", "spank", "smack"))


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
    sy = loader.add_from(ModelLoader(ctx.field(SKYE_DONOR[0]).section("models")), SKYE_DONOR[1])
    # (user: she sat) her donor's default anim is a sitting pose: the dancer's stand (same skeleton)
    loader.models[sy] = ModelLoader.with_anims(loader.models[sy], ["DXID.tor"])
    stand = len(ModelLoader.anims(loader.models[sy])) - 1
    f.set_section("models", loader.build())
    assert len(loader.models) <= 16, len(loader.models)
    from ff7.camera import facing_screen
    cam = Camera(f.sections[1])
    spots = {}
    for key, (x, y) in (("cam", CAMERA_AT), ("ruby", RUBY_AT)):
        t = mesh.find(x, y)
        assert t is not None, (key, x, y)
        spots[key] = (x, y, mesh.height(t, x, y), t)

    def hidden(girl, extra=()):
        """Shown once every kid is born; "ruby": hidden once Skye is unlocked (she retired); "skye":
        shown only then."""
        shown, hide = asm.nop(), asm.nop()
        who = {"ruby": [asm.if_byte(MOVIE_GIRL, "bit_off", 0, hide)],
               "skye": [asm.if_byte(MOVIE_GIRL, "bit_on", 0, hide)]}[girl]
        return _unlocked_or(hide) + who + list(extra) + [asm.goto(shown), hide, Op(b"\x7E\x01"), Op(b"\xC7\x01"),
                                                          hb._visi(0), shown]

    def talk(sec):
        say = lambda t: hb._say(sec, "Cameraman\n" + t)
        end, pitch, wait_ = asm.nop(), asm.nop(), asm.nop()
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8), asm.if_byte(MOVIE_STATE, "!=", 0, pitch),
               asm.setword(EL, HB_MINUTES), hb._arith(0x88, EL, MOVIE_AT), asm.if_word(EL, ">=", PAY_DELAY, wait_)]
        # (user) Skye's videos pay double (MOVIE_GIRL bit 1: she was this shoot's co-star; it
        # stays set until the next shoot is accepted, after this payment)
        def pay(rate):                           # GIL = presses x rate, capped to a word
            capped = asm.nop()
            return [asm.if_word(GIL, ">", 65535 // rate, capped), asm.setword(GIL, 65535 // rate), capped,
                    hb._arith(0x8A, GIL, rate)]
        ruby, paid_ = asm.nop(), asm.nop()
        ops += [asm.setword(GIL, MOVIE_PRESSES), asm.if_byte(MOVIE_GIRL, "bit_on", 1, ruby)]   # bit off -> ruby
        ops += pay(PAY_RATE * SKYE_PAY) + [asm.goto(paid_), ruby] + pay(PAY_RATE) + [paid_]
        ops += [Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), sound(0x168)]
        paid = say("“The film's flying off the shelves!\n Here's your cut, star: {VAR} gil.”")
        paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
        ops += paid + [asm.setbyte(MOVIE_STATE, 0), asm.goto(end)]
        ops += [wait_] + say("“Still selling the footage. Come back\n a little later for your cut.”") + [asm.goto(end)]
        # (user) he stands here from the start; until every Honey Bee kid is born he's only
        # scouting for a man with a way with the ladies
        told, fresh, scout = asm.nop(), asm.nop(), asm.nop()
        ops += [pitch] + _unlocked_or(scout)
        ops += [asm.if_byte(MOVIE_GIRL, "bit_on", 0, fresh), asm.if_byte(MOVIE_GIRL, "bit_off", 2, told)]
        ops += say("“Bad news, star: Ruby just turned 19 and\n retired. Hung up her heels for good.”")   # (user) once
        ops += say("“But meet Skye, my new discovery.\n She's... enthusiastic. You'll see.”")
        ops += [asm.biton(MOVIE_GIRL, 2), told, fresh]
        ops += say("“Well, well... I've heard rumours about\n a man who can handle sexy women.\n"
                   " That's you, isn't it?”")
        ask, first = hb._ask(sec, "Cameraman\n“I'm shooting a new movie and I need\n a star. Interested?”",
                             ["Lights, camera, action!", "Not now."])
        no = asm.nop()
        ops += ask + [asm.if_byte(CHOICE, "==", first, no), asm.bitoff(MOVIE_GIRL, 1)]
        # (user) once Skye is on, Ruby is still on the list
        only_ruby, pick_done = asm.nop(), asm.nop()
        ask2, first2 = hb._ask(sec, "Cameraman\n“Who's your co-star today?”", ["Skye", "Ruby"])
        ops += [asm.if_byte(MOVIE_GIRL, "bit_on", 0, only_ruby)] + ask2
        ops += [asm.if_byte(CHOICE, "==", first2, pick_done), asm.biton(MOVIE_GIRL, 1), pick_done, only_ruby]
        ops += say("“That's my man! To the set!”")
        x, y, z, t = focus
        ops += [Op(hb.FADE_OUT), Op(b"\x6C"), asm.setbyte(MOVIE_STATE, 0),
                asm.mapjump(ctx.maplist.index(FIELD), x, y, t, 0), asm.ret()]
        ops += [no] + say("“Suit yourself. The offer stands.”") + [asm.goto(end)]
        ops += [scout] + say("“I'm looking for a man with a way with\n the ladies. A real charmer, the kind\n"
                             " every girl in town knows by name.”")
        ops += say("“You wouldn't happen to know someone\n like that, would you?”")
        ops += say("“No? Well, if you hear of him, send him\n my way. I'll be right here.”")
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
            init_extra=[Op(bytes([0xA2, idle, 1])), Op(bytes([0xAE, idle, 1]))], main=debrief)   # (user) always there

    def ruby_talk(sec):
        return [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + \
            hb._say(sec, "Ruby\n“So you're my co-star? Don't disappoint\n me, handsome.”") + [hb._uc(0), asm.ret()]
    add_npc(ctx, WALL, "ruby", ru, spots["ruby"], facing_screen(cam, *spots["ruby"][:3], (0, 1)), ruby_talk,
            init_extra=hidden("ruby"))

    def skye_talk(sec):
        return [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + \
            hb._say(sec, "Skye\n“So you're the famous star? Mmm...\n I hope you can keep up with me.”") + \
            [hb._uc(0), asm.ret()]
    add_npc(ctx, WALL, "skye", sy, spots["ruby"], facing_screen(cam, *spots["ruby"][:3], (0, 1)), skye_talk,
            init_extra=hidden("skye", [Op(bytes([0xA2, stand, 1])), Op(bytes([0xAE, stand, 1]))]))     # (user) Ruby's place once she has retired
    # where the shoot sends you back: beside him, facing him
    x, y, z, t = spots["cam"]
    bx, by, bz, bt = beside(ctx, WALL, x, y, t, 40)
    bx, by, bz, bt = screen_step(ctx, WALL, bx, by, (0, 1), BACK_DOWN)     # (user: stuck there) 4 paces down
    return bx, by, bz, bt, _dates()._dir_to(x - bx, y - by)


def apply(ctx):
    _bare_ruby(ctx)
    _bare_skye(ctx)
    focus = _spot(Walkmesh(ctx.field(BASE).section("walkmesh")), *POSITIONS[0]["girl"][1][:2], 0, True)
    back = _wall_market(ctx, focus)
    _shoot(ctx, back)

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
the cameraman films beside each spot (FFBC; user: animated here, still in Wall Market). Her body is the Honey Bee
dancer's skeleton (same bones and lengths, same stand/walk/run anims), so the
dancer poses 620 builds (dzbt, dzbl, dzbf, dzbg, dzbh, dzbk) play on her.

Play: press OK as fast as you dare (counted when IFKEY 0x220, held, goes up -> down). Every tick (~8 frames) the
director (entity 0) takes the presses since the last tick, P:
    VEL = VEL*5/6 + P*A - B + (POS - 500)/C       (VEL stored + 1000, clamped +-VMAX)
    POS += VEL                                     (0..1000, starts 500)
so pressing pushes the cursor right, stopping lets it fall left, it keeps its
momentum, and the further it is from the middle the harder it runs away.
Below DANGER or above 1000 - DANGER = CUT: the shoot ends, but (user) he still sells what was shot (a low score).
Reaching the right red (CUT or finisher) plays the Bio spell's sound (RED_SOUND, user).
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
from _config import HB_KID, HB_MINUTES, MOVIE_AT, MOVIE_GIRL, MOVIE_PRESSES, MOVIE_RANK, MOVIE_STATE, SPECIAL_ON
import _movie_girls as MG
import _movie_group as GR
import _movie_loose as LZ
import _movie_profiles as PF
from _recruit import sound
from _travel import CHOICE, beside, reuse_npc, screen_step

from ff7 import asm
from ff7.camera import Camera, facing_screen, screen_range
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

FIELD, BASE, WALL = "whitebg1", "mds7_w3", "mds7st3"
# (user) the Sector 7 station's lower platform, centre (was Wall Market, mrkt2); mds7st3 is at 16
# models, so they take over the Avalanche members the pinned moment keeps hidden (`TAKEOVER`)
CAMERA_AT, RUBY_AT = (-3000, 2380), (-2760, 2520)
TAKEOVER = {"filmman": "aval", "ruby": "avaf", "skye": "avaw"}
# (user) "Late Night Viewing": the tape he sells (20 gil, key item 63, free: 51-62 are 625's gifts)
# is watched on the Item Store terminal in Wall Market (mkt_ia's line00 script 4: the gun)
TAPE_PRICE, TAPE_ITEM, TERMINAL = 20, 63, "mkt_ia"
TAPE_BIT = ((1, 64 + TAPE_ITEM // 8), TAPE_ITEM % 8)
TAPE_NAME, TAPE_DESC = "Video Tape", "An unlabelled tape. Play it on a terminal."
CAMERA_DONOR, RUBY_DONOR = ("junone2", 6), ("jun_i2", 6)
CAMERA_IDLE, CAMERA_FILM = "FDCB.yos", "FFBC.yos"    # camera held low / at his eye
# (user) the shoot's intro: standing at the foot of the left bed (it starts at y -140), the camera
# follows "focus" (the hidden player); the cameraman a little off, facing them
GROUP_CAM = [(40, -215), (-160, -200), (100, -215), (170, -235)]   # the group's cameraman: part one; each bed
INTRO = {"girl": (-268, -160), "cloud": (-222, -165), "focus": (-240, -170), "cam": (-160, -150)}
CAMERA_STILL = "ZCFA.tor"                            # (user) Wall Market: FDCB frame 0 only, held
# (user: speed up the switch between positions) fades at speed 0x10 (the game's usual is 0x08; read as
# "higher = faster", from the values the game's own scripts use: inferred, not checked in the exe)
FAST_OUT, FAST_IN = bytes.fromhex("6b0000000000100200"), bytes.fromhex("6b00000000001001ff")
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
    # (user, since) Cloud's shins stay flat and still, his pelvis thrusting (ZCTU: 620 `_cloud_thrust(pivot=)`)
    # (user, since) Cloud a bit to the right (x -220 -> -215, in line with her), legs apart (MISSION_KNEES)
    dict(name="mission", girl=("DZBT", (-215, -59, 0, 0x00), True), cloud=("ZCTU", (-215, -25, -4, 0x80), True),
         camera=(-130, -60, 0xC0)),                                         # left bed, she lies, head to the pillow
    # middle bed, Cloud's head on the pillow; she (user) a body width to her right (x 0 -> 18): over his line;
    # then (user) slightly lower onto him (raise 18 -> 14) and slightly back (y -87 -> -91: she faces +y);
    # then (user) a little towards his head (-91 -> -95: his head is on the pillow, -y)
    dict(name="cowgirl", girl=("DZBL", (18, -95, 14, 0x80), True), cloud=("ZCTD", (18, -95, 0, 0x80), True),
         camera=(-130, -60, 0x40)),
    dict(name="dog", girl=("DZBF", (227, -125, 0, 0x00), True), cloud=("ZCTN", (225, -103, 0, 0x00), True),
         camera=(90, -60, 0x40)),                                           # right bed
    # (user, since) Cloud 3 further from her (y -161 -> -164)
    dict(name="edge", girl=("DZBG", (-225, -150, 0, 0x80), False), cloud=("ZCTF", (-225, -164, 0, 0x80), False),
         camera=(-130, -180, 0xC0)),                                        # bent over the left bed's foot
    # (user, since) her hanging head rocks back and forth (ZRHN: DZBH + `HEADREV_NOD`)
    dict(name="headrev", girl=("ZRHN", (-225, -54, 0, 0x80), True), cloud=("ZCTX", (-225, -150, 0, 0x80), False),
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
    dict(name="69", girl=("ZR6A", "69", True), cloud=("ZCTY", (18, -95, 0, 0x80), True), camera=(-130, -60, None)),
    # (user) "head" last: the finisher position
    # on the floor in front of the beds; she (user) half a head further from him (x 50 -> 42)
    # (user, since) y -230 -> -224: to her left (his right)
    # (user, since) Cloud: ZCTQ = ZCTE with his left leg cocked HEAD_STEP forward (foot planted) and
    # HEAD_THRUST x the pelvic thrust (built by 620 for its head layout too: HEAD_STEP / HEAD_THRUST)
    # (user, since) she a touch closer (x 42 -> 45)
    # (user, since) then slightly further again (45 -> 42: 38 from him, as 620's HEAD_HOLD_GAP)
    dict(name="head", girl=("ZRTA", (42, -224, 0, 0x40), False), cloud=("ZCTQ", (80, -225, 0, 0xC0), False),   # (user, since) Cloud 5 to his right (-230): pelvis on her face
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
RED_SOUND = 0x3F                                    # (user) the Bio spell's sound on reaching the right red (finisher
                                                    # or CUT); exe: Bio's effect 0x5A6730 plays 0x3F (static reading)
AFTERMATH = ("Ruby\n(Ruby swallows, wipes her lips with her\n thumb and sinks back, breathless.)",
             "Skye\n(Skye licks her lips clean, sighs happily\n and blows a kiss at the camera.)")   # (user) Ruby, Skye

# temp vars (this field only)
POS, VEL, PR, TOT, FR, RATE, T, S, NEXT, BKT, EARN, EL, NT = ((6, a) for a in range(100, 126, 2))
P, STEP, NEW, RUN, K, HELD = (5, 130), (5, 131), (5, 132), (5, 133), (5, 134), (5, 135)
FIN, FT = (5, 136), (6, 126)                         # finisher on (last 5 s of the last position); scratch word
GIL = (6, 140)                                       # mrkt2: the cut (temp word)
SPEC = (5, 138)                                      # the cameraman's talk: a special scene picked (672)
SPECIAL_BASE, SPECIAL_ARRIVE = "colne_6", (15, 45)  # 672's sets (copies of colne_6): arrival, by the bed

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


def _animb():
    """ANIMB (0xDD): ends the model's current animation. (exe: ANIME2 (0x61484A) sets the model's
    animation state 0xCC0980 to 5 and any later ANIME1/ANIME2 waits while it is 5, i.e. until that
    animation has played out; ANIMB (0x615271) sets state 3, from which the next one starts at once.
    The group's girls idle in 252-frame waiting anims: their next pose came seconds late, and a
    REQSW to an entity still running a same-priority script makes the caller retry each frame,
    user.) Put before every DFANM + ANIME2 that must take effect now."""
    return Op(b"\xDD")


def _quests():
    from importlib import import_module
    return import_module("600_quests")


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
    _skye_shape(ctx, hrc)
    hrc = _skye_limbs(ctx, hrc)
    ctx.char_file(SKYE_BARE.lower(), hrc.encode("latin-1"))


# (user) her legs remade to match the new torso / pelvis (620 `_limb`: smooth rings
# sized by slicing the old box-like parts, at most twice their triangles): per bone (rings
# (t, scale), points a ring, top end, bottom end). Thighs fuller at the top, tapering to a
# rounded knee (the shin's capped top sits in it); calves, slimmer ankles. (User, since: the
# arms were done too, then put back as they were.) Hands and feet as they were. New parts
# ZSKE-H / ZSLE-H (her dressed model keeps the old ones).
SKYE_LIMBS = {
    # (user, since) the knee closed up: the thigh's last ring lower and its tip further past the
    # joint, the shin's capped top ring raised above the old shin's top (t < 0)
    "femur": ([(0.0, 0.8), (0.95, 0.88)], 8, None, ("tip", 0.6)),               # 16 + 8 = 24 (of 12); top narrower (user)
    "tibia": ([(-0.08, 0.92), (0.3, 1.0), (1.0, 0.8)], 6, "cap", None),         # 24 + 4 = 28 (of 14)
}   # (user, since) the arms back as they were


def _skye_limbs(ctx, hrc):
    hb = _hb()
    lines = [l.strip() for l in hrc.splitlines()]
    k = lines.index(next(l for l in lines if l.startswith(":BONES"))) + 1
    letter = ord("E")
    while k < len(lines):
        if not lines[k]:
            k += 1
            continue
        bone, rs = lines[k], lines[k + 3].split()
        k += 4
        spec = SKYE_LIMBS.get(bone[2:])
        if not spec or len(rs) != 2:
            continue
        old = rs[1]
        r = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
        oldp = r.split("PLY=")[1][:4]
        d = ctx.char_file(oldp.lower() + ".p")
        rings, n, top, bottom = spec
        new_rs, new_p = "ZSK" + chr(letter), "ZSL" + chr(letter)
        letter += 1
        for name in (new_rs.lower() + ".rsd", new_p.lower() + ".p"):
            try:
                ctx.char_file(name)
                raise AssertionError("%s already in char.lgp" % name)
            except KeyError:
                pass
        assert hrc.count("1 %s" % old) == 1, old
        hrc = hrc.replace("1 %s" % old, "1 %s" % new_rs)
        ctx.char_file(new_rs.lower() + ".rsd", r.replace("PLY=%s." % oldp, "PLY=%s." % new_p).encode("latin-1"))
        V, tris = hb._limb(d, rings, n, top, bottom)
        o = 128 + 12 * struct.unpack_from("<16I", d, 0)[3] + 12 * struct.unpack_from("<16I", d, 0)[4]
        h = struct.unpack_from("<16I", d, 0)
        oc = 128 + 12 * h[3] + 12 * h[4] + 12 * h[5] + 8 * h[6]
        cols = [tuple(d[oc + 4 * i:oc + 4 * i + 3]) for i in range(h[7])]
        col = max(set(cols), key=cols.count)            # its own (skin) colour
        op = oc + 4 * h[7] + 4 * h[9] + 4 * h[8]
        ctx.char_file(new_p.lower() + ".p", hb._p_file(V, tris, col, d[64:128], struct.unpack_from("<12H", d, op)[10:12]))
    assert letter - ord("E") == 4, letter - ord("E")       # both legs' two parts
    # (user) arms subdivided once, smoothed: ZSKI-L; the forearm's first SKYE_FOREARM_STRAIGHT
    # rings a straight tube as wide as the upper arm's bottom, widening to the hand only after
    return _hb()._smooth_arms(ctx, hrc, "ZSK", "ZSL", chr(letter), straight_forearm=SKYE_FOREARM_STRAIGHT)


SKYE_FOREARM_STRAIGHT = 2


# (user) her bare pelvis and torso remade with a woman's shape (620 `_loft`): rings round one
# centre line (z on y fitted to both old parts, so they meet at the waist), laid out in her
# standing pose (DXID frame 0; model units, y down, she faces -z) and taken into each bone's
# own frame. A ring = (y, half width, front depth, back depth, bulge): the chest's bulge is
# the bust (front, two mounds at x +-SKYE_BUST[0]), the pelvis's the seat (user, since:
# "sculpt a buttocks"): its rings have more points round the back (SKYE_HIP_ANG: 115 = the
# cheeks' outer sides, 155 = their middles, 180 = the cleft, pulled in SKYE_CLEFT), rise to
# their fullest a little above the crotch and round under (the last ring narrower, the seat
# still out) before the fan down to SKYE_CROTCH; 8 points a ring (3 of them across the seat)
# so a fifth ring fits. Triangles at most twice the original's (user): chest 58 -> 116,
# pelvis 36 -> 72 (its 8 collapsed streamer points dropped).
SKYE_ANG = (0, 25, 50, 80, 125, 180, -125, -80, -50, -25)
SKYE_CHEST = [(-14.65, 2.0, 1.55, 1.25, 0.0), (-15.6, 1.95, 1.3, 1.25, 0.18), (-16.5, 2.15, 1.45, 1.35, 1.0),
              (-17.4, 2.35, 1.65, 1.5, 1.5), (-18.6, 3.15, 1.55, 1.6, 0.35),   # bust x1.4 (user)
              (-19.75, 3.2, 1.0, 1.4, 0.0)]
# (user, since) a little belly 'pooch': the front depth of the rings below the waist (chest's
# bottom ring, the pelvis's top three) pushed out, most at -13.85; the waist ring (-15.6) kept
# (user, since) the shoulders: the top two rings widened (2.85 / 2.7 -> 3.15 / 3.2) so the arms'
# tops (innermost x 2.99 at y -19.2) sink ~0.25 into them instead of floating
SKYE_BUST = (1.15, 0.9)
SKYE_HIP_ANG = (0, 60, 115, 155, 180, -155, -115, -60)
SKYE_HIP = [(-14.75, 2.0, 1.55, 1.25, 0.0), (-13.85, 2.6, 2.0, 1.55, 1.0), (-12.9, 3.0, 1.75, 1.7, 1.4),
            (-12.05, 3.0, 1.5, 1.6, 1.25), (-11.3, 2.55, 1.15, 1.15, 0.7)]   # (user, since) fuller, lower;
                                                                            # then 30% longer, tapering in
SKYE_SEAT, SKYE_CLEFT = (1.3, 0.8), 0.45
SKYE_CROTCH = (0.0, -10.6)


def _skye_shape(ctx, hrc):
    from ff7 import fieldanim as fa
    hb = _hb()
    sk = fa.skeleton(hrc)
    names = [b[0] for b in sk]
    rr, rp, rots = fa.Anim(ctx.char_file("dxid.a")).frames[0]
    W = fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)
    lines = [l.strip() for l in hrc.splitlines()]
    part = {lines[k]: lines[k + 3].split()[1] for k in range(len(lines) - 3)
            if lines[k] in ("hip", "chest") and lines[k + 1] in ("root", "hip")}
    files = {}
    old = []
    for bone in ("hip", "chest"):
        rsd = ctx.char_file(part[bone].lower() + ".rsd").decode("latin-1")
        ply = rsd.split("PLY=")[1][:4].lower() + ".p"
        d = ctx.char_file(ply)
        files[bone] = (ply, d)
        m, start, _ = W[names.index(bone)]
        old += [[start[j] + fa._vec(m, struct.unpack_from("<3f", d, 128 + 12 * i))[j] for j in range(3)]
                for i in range(struct.unpack_from("<16I", d, 0)[3])]
    centre = hb._centre_line(old)
    for bone, made in (("chest", hb._loft(SKYE_CHEST, SKYE_ANG, centre, SKYE_BUST, -1, top=True, bottom="cap")),
                       ("hip", hb._loft(SKYE_HIP, SKYE_HIP_ANG, centre, SKYE_SEAT, 1, SKYE_CLEFT,
                                        bottom=SKYE_CROTCH))):
        ply, d = files[bone]
        hb._write_part(ctx, ply, d, made, W[names.index(bone)], SKYE_SKIN)
        if bone == "chest":                          # the bust's own share of each vertex, in the bone's
            flat = hb._loft([r[:4] + (0.0,) for r in SKYE_CHEST], SKYE_ANG, centre, SKYE_BUST, -1, top=True,
                            bottom="cap")[0]         # frame (`_female_body.apply(bust=)` scales it per girl)
            m = W[names.index(bone)][0]
            mt = [[m[r][c] for r in range(3)] for c in range(3)]
            ctx.bust_delta = [fa._vec(mt, [a[k] - b[k] for k in range(3)]) for a, b in zip(made[0], flat)]
            assert len(flat) == len(made[0]) and max(abs(c) for v in ctx.bust_delta for c in v) > 0.5


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


PAUSE_POS = ["headrev", "69", "head"]               # (user) where she may need a moment (`_pause_ops`)
PCNT, RND2 = (5, 144), (5, 145)                     # the pause lines' turn; the pause roll
PARM, PT = (5, 139), (6, 142)                       # (user, since) this position's pause: armed; its frame
SQ, SQH, IWIN, IT = (5, 146), (5, 147), (5, 157), (6, 148)   # (user) the hold: Square pressed in the icon's
                                                    # window / Square held / the window open / the next icon's frame
SQUARE_KEY = 0x80                                   # (the original scripts' {SQUARE} choices test keys=128)
ICON_FRAMES = 30                                    # (user) the icon shows 1 s (was 0.5 s, then 1.5 s)
SLP = (5, 158)                                      # (user) Square pressed in a slap prompt's window (IWIN 2): pay it
ICON_FIRST, ICON_EVERY = (30, 45), (380, 20)        # first icon at 30 + k*45 (k 0..7: in the first 15 s), then every
                                                    # 380 + k*20 frames (12.7-17.3 s: ~15 s apart)
ICON_PX, ICON_Y = 16, -50                           # on-screen size; screen y from the view centre (below the gauge)
HOLD_BONUS = 10                                     # (user) a hold pays the shoot's gil per press x 10 on the spot
MATERIA_SOUND = 0x1EA                               # (user) the press's sound (the game's materia-get sound)


def _try_anim(ctx, base, name):
    """(user: "after 4 seconds ... the girl's head pulls back slightly to try to come back, but
    can't"; since: two more squirms, the hold 2 s longer) her pose `base` (15 frames: 0 pulled back,
    7 deepest; on Ruby's skeleton) as `len(GR.SQUIRMS)` x GR.TRY_FRAMES frames, one motion after
    another, each from the deepest frame and back to it: eased `pull` of the way towards frame 0 and
    straining there (a tremble every `shake` frames); `sway`: her legs swung that many degrees each
    way about her body's long axis (hips wriggling, `cycles` times); `push`: her arms swung that many
    degrees about her side axis, alternately (pushing at him). Her head stays on him. Written to `name`."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))
    I = [b_[0] for b_ in sk].index
    a = fa.Anim(ctx.char_file(base.lower() + ".a"))
    (rr, p0, r0), (_, p7, r7) = a.frames[0], a.frames[7]
    ang = lambda x, y, w: x + w * (((y - x + 180) % 360) - 180)
    n, up = GR.TRY_FRAMES, GR.TRY_FRAMES // 4
    sub = lambda u, v: [u[k] - v[k] for k in range(3)]
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]
    kids = lambda root: {b_[0] for b_ in sk if b_[0] == root or _under(sk, b_[0], root)}
    legs = {s_: kids(s_ + "_femur") for s_ in "lr"}
    arms = {s_: kids(s_ + "_uparm") for s_ in "lr"}
    frames = []
    for sq in GR.SQUIRMS:
        ws = []
        for t in range(n):
            env = (1 - math.cos(math.pi * t / up)) / 2 if t < up else \
                (1 + math.cos(math.pi * (t - (n - up)) / (up - 1))) / 2 if t >= n - up else 1.0
            w = env * (1 - 0.15 * (1 - math.cos(2 * math.pi * t / sq["shake"])) / 2) * sq["pull"]
            ws.append(w)
            pos = [p7[k] + w * (p0[k] - p7[k]) for k in range(3)]
            rots = [[ang(x, y, w) for x, y in zip(b7, b0)] for b7, b0 in zip(r7, r0)]
            ph = math.sin(2 * math.pi * sq["cycles"] * t / n) * env
            if sq["sway"] or sq["push"]:
                F = fa.forward(sk, rr, pos, rots)
                W = [m for m, _, _ in F]
                along = unit(sub(F[I("chest")][2], F[I("hip")][1]))
                side = unit(sub(F[I("l_femur")][1], F[I("r_femur")][1]))
                for s_, sgn in (("l", 1), ("r", -1)):
                    for bones, axis, deg, at in ((legs[s_], along, sq["sway"] * ph, s_ + "_femur"),
                                                 (arms[s_], side, sq["push"] * ph * sgn, s_ + "_uparm")):
                        if deg:
                            R = fa.axis_angle(axis, deg)
                            W = [fa._mul(R, m) if sk[i][0] in bones else m for i, m in enumerate(W)]
                rots = fa.local_rotations(sk, rr, W)
                G = fa.forward(sk, rr, pos, rots)
                assert math.dist(G[I("head")][2], F[I("head")][2]) < 1e-3, "her head stays on him"
            frames.append((rr, pos, rots))
        assert ws[0] == 0 and abs(ws[-1]) < 1e-9 and max(ws) <= sq["pull"], ws     # starts and ends at the deepest
    a.frames = frames
    ctx.char_file(name.lower() + ".a", a.build())


def _under(sk, bone, root):
    """bone is below root in the skeleton."""
    par = dict((b_[0], b_[1]) for b_ in sk)
    while bone in par:
        bone = par[bone]
        if bone == root:
            return True
    return False


def _pause_arm(hb, length):
    """At a position's start (or a group turn's): (user: "a 50% chance that a girl has to stop
    momentarily" in head / head reverse / 69) with `_movie_group.PAUSE_CHANCE` / 256, arm one pause
    (PARM 1) for a frame PT somewhere in the middle half of its `length` frames (eight steps);
    `_pause_ops` fires it. And (user) the hold icon's first frame IT, somewhere in the first 15 s."""
    no = asm.nop()
    ops = [asm.setbyte(PARM, 0), Op(bytes([0x99, RND2[0], RND2[1]])),
           asm.if_byte(RND2, "<", GR.PAUSE_CHANCE, no), asm.setbyte(PARM, 1),
           Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], 8])),
           asm.setword(PT, FR), hb._arith(0x86, PT, length // 4)]
    ops += _chain(RND2, [[hb._arith(0x86, PT, k * length // 16)] if k else [] for k in range(8)]) + [no]
    return ops + [asm.setbyte(SQ, 0)] + _icon_next(hb, *ICON_FIRST)


def _icon_next(hb, base, step):
    """IT = FR + base + k * step, k random 0..7."""
    return [Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], 8])),
            asm.setword(IT, FR), hb._arith(0x86, IT, base)] + \
        _chain(RND2, [[hb._arith(0x86, IT, k * step)] if k else [] for k in range(8)])


# (user) the girls' reactions (`_movie_profiles`): temp vars, this field only. LEFT bit k = girl k
# walked off (group); RULES 1 = the rules are agreed (Elena); CTRL bit k = held once already
# (Scarlet); TP = turn within the part (group); ANN0 + k = girl k's annoyance (solo: k 0); GLO/GHI
# = CHGLD's two words (a loss never takes more gil than there is)
LEFT, RULES, CTRL, TP, ANN0 = (5, 170), (5, 171), (5, 172), (5, 174), 176
WALKED = "“She walked off my set?! CUT!\n ...Fine. We'll sell what we've got.”"   # (one-girl / special shoots)
GLO, GHI = (6, 184), (6, 186)
LSN = (5, 192)                                       # (user) the lesson prompt answered (IWIN 4)
THR, TC, TSC, TT = (5, 159), (5, 175), (5, 173), (6, 190)   # (user, 672) "there": pressed; prompts this
                                                    # part; Scarlet's tries this shoot; the next prompt's frame
THERE_FIRST, THERE_NEXT = (150, 60), (600, 60)      # (user: 2 a part) first at 5-19 s, the second 20-34 s later


def _ann(k):
    return (5, ANN0 + k)


def _gil_note(gil):
    return "" if not gil else "\n(%s%s gil)" % ("+" if gil > 0 else "-", "{:,}".format(abs(gil)))


def _take_gil(amount):
    """GOLDD amount, or all the gil the party has if that's less (CHGLD lo/hi)."""
    full, done = asm.nop(), asm.nop()
    return [Op(bytes([0x3B, 0x66, GLO[1], GHI[1]])), asm.if_word(GHI, "==", 0, full),
            asm.if_word(GLO, "<", amount, full), Op(bytes([0x3A, 0x60]) + struct.pack("<I", GLO[1])),
            asm.goto(done), full, Op(bytes([0x3A, 0x00]) + struct.pack("<I", amount)), done]


def _gil_ops(gil):
    """+gil paid (GOLDU), -gil taken (`_take_gil`)."""
    if gil > 0:
        return [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)]
    return _take_gil(-gil) if gil < 0 else []


# (user) a girl who walks off the set loses an affection point (DEC!: never below 0); the co-star
# menu then greys her name until she's back at 20 (`_cast_grey`). Ruby and Skye have no affection.
AFF_KEYS = {g["key"]: g["name"] for g in MG.GIRLS}


def aff_var(key):
    """Her HB_AFFECTION var (the dates' girls), or None (Ruby, Skye)."""
    from _config import HB_AFFECTION
    from _honey_bee_data import GIRLS as HBG
    if key not in AFF_KEYS:
        return None
    return HB_AFFECTION[[g["name"] for g in HBG].index(AFF_KEYS[key])]


def lose_affection(key):
    v = aff_var(key)
    return [] if v is None else [Op(bytes([0x7C, v[0], v[1]]))]        # DEC! (bank in the low nibble)


def _annoy(k, leave_ops):
    """Girl k's annoyance +1; at `_movie_profiles.LEAVE_AT`, leave_ops (she walks off)."""
    stay = asm.nop()
    return [Op(bytes([0x95, 5, ANN0 + k])), asm.if_byte(_ann(k), ">=", PF.LEAVE_AT, stay)] + leave_ops + [stay]


def _hold_check(key, k, refuse):
    """(user) Does she take the hold? Her profile's `hold`: jump to refuse if not."""
    pr = PF.PROFILES[key]
    kind = pr["hold"]
    if kind == "likes":
        return []
    if kind == "dislikes":
        return [asm.goto(refuse)]
    if kind == "mood":                                # RANDOM < odds: she plays along
        return [Op(bytes([0x99, RND2[0], RND2[1]])), asm.if_byte(RND2, "<", pr["odds"], refuse)]
    if kind == "rules":
        return [asm.if_byte(RULES, "==", 1, refuse)]
    assert kind == "control", kind                    # the first time only
    return [asm.if_byte(CTRL, "bit_off", k, refuse), asm.biton(CTRL, k)]


def _text_id(sec, t):
    """One text id per distinct string in a field (the per-girl chains repeat lines)."""
    ids = sec.__dict__.setdefault("_openff7_ids", {})
    if t not in ids:
        ids[t] = sec.add_string(_encode(t))
    return ids[t]


def _there_arm(hb):
    """At a position's start: no "there" prompt shown yet, the first at FR + THERE_FIRST."""
    return [asm.setbyte(TC, 0), Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], 8])),
            asm.setword(TT, FR), hb._arith(0x86, TT, THERE_FIRST[0])] + \
        _chain(RND2, [[hb._arith(0x86, TT, k * THERE_FIRST[1])] if k else [] for k in range(8)])


def _there_ops(hb, sec, key, rate, cond, icon, hush, leave):
    """(user) The special shoots' "there" prompt (672: parts one and three, two a part): the
    Square icon (its slot 5, IWIN 3) at TT; Square in it (THR, `sqkey`) = Cloud tries the back door.
    Her profile's `there` decides (`_movie_profiles`): yes = `there_yes` + `there_gain` x her gil a
    press; no = `there_no` (Scarlet's third try on: `there_push`), `there_loss` x it taken, +1
    annoyance (`_annoy`, leave(key) at LEAVE_AT). The meter is held while she reacts."""
    pr = PF.PROFILES[key]
    name = GR.NAMES[key]
    no, no2, refuse, done = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    icon_ops = cond(no) + [asm.if_byte(RUN, "==", 1, no), asm.if_byte(TC, "<", 2, no), asm.if_word(FR, ">=", TT, no),
                           hb._req(icon, 5, wait=False), Op(bytes([0x95, TC[0], TC[1]])),
                           Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], 8])),
                           asm.setword(TT, FR), hb._arith(0x86, TT, THERE_NEXT[0])] + \
        _chain(RND2, [[hb._arith(0x86, TT, k * THERE_NEXT[1])] if k else [] for k in range(8)]) + [no]
    w1 = GR.PAUSE_FRAMES[1]

    def say(texts, gil):                                    # one at random, window 3, closed by hush slot 2
        out = []
        for t in texts:
            t = name + "\n" + t + _gil_note(gil)
            out.append([Op(b"\x52\x03\x00\x01"), hb._window(t, 3, 8, LINE_Y), hb._req(hush, 2, wait=False),
                        asm.message(3, _text_id(sec, t))])
        return [Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], len(out)]))] + \
            _chain(RND2, out)
    kind = pr["there"]
    ev = [asm.if_byte(THR, "==", 1, no2), asm.setbyte(THR, 0), asm.setbyte(RUN, 0), Op(b"\x54\x01")]
    if kind == "dislikes":
        ev += [asm.goto(refuse)]
    elif kind == "mood":
        ev += [Op(bytes([0x99, RND2[0], RND2[1]])), asm.if_byte(RND2, "<", pr["there_odds"], refuse)]
    elif kind == "rules":
        ev += [asm.if_byte(RULES, "==", 2, refuse)]
    elif kind == "second":
        ev += [Op(bytes([0x95, TSC[0], TSC[1]])), asm.if_byte(TSC, "==", 2, refuse)]
    else:
        assert kind == "likes", kind
    gain = rate * pr.get("there_gain", 10)
    if kind != "dislikes":
        ev += [sound(MATERIA_SOUND)] + say(pr["there_yes"], gain) + [Op(bytes([0x39, 0x00]) + struct.pack("<I", gain)),
                                                                    asm.goto(done)]
    if kind != "likes":
        loss = rate * pr.get("there_loss", pr.get("loss", 5))
        ev += [refuse, sound(FAIL_SOUND)] + _there_refuse(hb, say, pr, kind, loss) + _take_gil(loss) + _annoy(0, leave(key))
    length = w1 + 25
    ev += [done, hb._w(15), hb._arith(0x86, NEXT, length), hb._arith(0x86, IT, length), hb._arith(0x86, TT, length),
           asm.setword(PR, 0), asm.setword(NT, FR), hb._arith(0x86, NT, TICK), asm.setbyte(RUN, 1), no2]
    return icon_ops + ev


def _there_refuse(hb, say, pr, kind, loss):
    """Her refusal line: Scarlet's third try on (`there_push`) vs her first (`there_no`)."""
    if kind != "second":
        return say(pr["there_no"], -loss)
    first_, end = asm.nop(), asm.nop()
    return [asm.if_byte(TSC, ">=", 3, first_)] + say(pr["there_push"], -loss) + [asm.goto(end), first_] + \
        say(pr["there_no"], -loss) + [end]


def _pause_ops(hb, sec, actors, hush, lines, cond, icon, rate_of, slot_of=lambda key: 0, leave=None, uneasy=None,
               desperate=3, speaker=None):
    """(user) The director's tick ops for head / head reverse / 69 (cond = ops jumping to their
    argument unless the position is one of them): the rare pause (`_movie_group.PAUSES`), then the
    hold (Square pressed while the icon showed: SQ), then the icon (every ~15 s, `ICON_EVERY`; entity
    `icon` slot 3 shows it ICON_FRAMES with IWIN set). actors = [Cloud's entity, the girls']: slot 4
    holds the pulled-back pose, slot 5 the deepest one, the girls' slot 6 her try to pull back, slot 2
    resumes; lines(block) = ops picking block(key) by the shoot's girl; rate_of(key) = her gil a
    press; slot_of(key) = her index for the per-girl temps (`_ann`, CTRL bits). (User, since) the
    hold by her profile (`_hold_check`): refused = she taps out at once, a loss, +1 annoyance, and at
    LEAVE_AT leave(key) (ops: she walks off). uneasy(key) = her stop's ops instead of a PAUSES line
    (group: `_movie_group.UNEASY`), or None. Meter frozen (RUN 0) and the position's time (NEXT)
    extended by each stop, so it costs nothing."""
    no = asm.nop()
    icon_ops = cond(no) + [asm.if_byte(RUN, "==", 1, no), asm.if_word(FR, ">=", IT, no), asm.setbyte(SQ, 0),
                           hb._req(icon, 3, wait=False)] + _icon_next(hb, *ICON_EVERY) + [no]
    no2 = asm.nop()                              # (user) a slap prompt answered: the hold's bonus, any position
    slap_ops = [asm.if_byte(SLP, "==", 1, no2), asm.setbyte(SLP, 0)] + \
        lines(lambda key: [Op(bytes([0x39, 0x00]) + struct.pack("<I", rate_of(key) * HOLD_BONUS))]) + [no2]
    args = (hb, sec, actors, hush, lines, cond, rate_of, slot_of, leave, uneasy)
    return _stop_ops(*args, kind="pause", icon=icon) + \
        _stop_ops(*args, kind="hold", desperate=desperate, speaker=speaker, icon=icon) + \
        icon_ops + slap_ops


def _stop_ops(hb, sec, actors, hush, lines, cond, rate_of, slot_of, leave, uneasy, kind, desperate=3, speaker=None,
              icon=None):
    """pause: she pulls back (slot 4) and says a PAUSES line (an uneasy girl: uneasy(key)). hold
    (user): if she takes it (`_hold_check`), the bonus (GOLDU, her profile's `gain`), Cloud holds deep
    (slot 5) and says a HOLD_CLOUD line; his stern HOLD_STERN; she tries to pull back (her slot 6)
    and can't, a HOLD_MUFFLED line, (user, since) another (the next HOLD_MUFFLED one) and a HOLD_DESPERATE
    one (the first `desperate` of hers: the group has no text room for more), each window closed
    MUFFLED_SAY in by hush3's slot 4; at HOLD_AT['end'] she pulls away (slot 4) with a HOLDS line.
    If she doesn't: she pulls straight off (slot 4) with her profile's `refuse` line, `loss` x her
    gil a press taken, +1 annoyance (`_annoy`: leave(key) at LEAVE_AT). The hold's windows are closed
    by hush3's slot 3 (HOLD_SAY). Slot 6 is REQ'd with the muffled line and waits
    `hold_try_delay()` itself (the line's MESSAGE holds the director). speaker = None (Cloud holds) or
    (var, [(name, hold lines, stern lines), ...]): who holds, by var's value (673: Cid)."""
    no = asm.nop()
    w0, w1, w2 = GR.PAUSE_FRAMES
    assert w0 == 0                               # (user) her line the moment it happens: no wait first
    at = GR.HOLD_AT
    assert GR.HOLD_SAY <= at["stern"] and at["stern"] + GR.HOLD_SAY <= at["muffled"] <= at["struggle"] and \
        at["muffled"] + GR.MUFFLED_SAY <= at["muffled2"] and at["muffled2"] + GR.MUFFLED_SAY <= at["desperate"] and \
        at["desperate"] + GR.MUFFLED_SAY <= at["end"] and \
        at["struggle"] + len(GR.SQUIRMS) * GR.TRY_FRAMES <= at["end"]
    table = GR.PAUSES if kind == "pause" else GR.HOLDS
    total = w0 + w1 + w2 + 10 + (GR.HOLD_AT["end"] if kind == "hold" else 0)

    def say3(t, slot=3):                         # (hush3 slot 3: closed HOLD_SAY frames in; slot 2: w1)
        return [Op(b"\x52\x03\x00\x01"), hb._window(t, 3, 8, LINE_Y), hb._req(hush, slot, wait=False),
                asm.message(3, _text_id(sec, t))]

    def muffled(key):                            # (her struggling line in the hold, RND2; hush3 slot 4)
        return _chain(RND2, [say3(GR.NAMES[key] + "\n" + t, 4) for t in GR.HOLD_MUFFLED[key]])

    gap = lambda n: [hb._w(n)] if n else []      # (no WAIT 0)

    def desperate_(key):                         # (user) the last, more desperate one
        ts = GR.HOLD_DESPERATE[key][:desperate]
        return _chain(RND2, [say3(GR.NAMES[key] + "\n" + ts[r % len(ts)], 4) for r in range(3)])

    def block(key):
        u_ = uneasy(key) if kind == "pause" and uneasy else None
        if u_ is not None:
            return u_
        return _chain(PCNT, [say3(GR.NAMES[key] + "\n" + t, 2) for t in table[key]])

    def resume(length, others):
        return [hb._w(w2), hb._arith(0x86, NEXT, length)] + [hb._arith(0x86, v, length) for v in others] + \
            [hb._req(e, 2) for e in actors] + [asm.setbyte(SQ, 0), asm.setword(PR, 0), asm.setword(NT, FR),
                                               hb._arith(0x86, NT, TICK), asm.setbyte(RUN, 1)]
    refuse = asm.nop()
    if kind == "pause":
        ops = cond(no) + [asm.if_byte(PARM, "==", 1, no), asm.if_word(FR, ">=", PT, no), asm.setbyte(PARM, 0),
                          asm.setbyte(RUN, 0), Op(b"\x54\x01")]
        others = [IT]
    else:                                        # in deep, held: the bonus and his line; she tries; she pulls away
        ops = cond(no) + [asm.if_byte(SQ, "==", 1, no), asm.setbyte(SQ, 0), asm.setbyte(RUN, 0), Op(b"\x54\x01")]
        ops += lines(lambda key: _hold_check(key, slot_of(key), refuse)) + [sound(MATERIA_SOUND)]   # (taken)
        ops += [hb._req(e, 5, wait=False) for e in actors]
        ops += [Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], len(GR.HOLD_CLOUD)]))]

        voices = [("{CLOUD}", GR.HOLD_CLOUD, GR.HOLD_STERN)] if speaker is None else speaker[1]
        by_voice = (lambda make_: make_(voices[0])) if speaker is None or speaker[0] is None else \
            (lambda make_: _chain(speaker[0], [make_(v) for v in voices]))
        nr = len(GR.HOLD_CLOUD)                  # (RND2 mod this; a voice with fewer lines repeats them: one text)

        def make(gil):
            return [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil))] + \
                by_voice(lambda v: _chain(RND2, [say3("%s\n“%s”\nHold bonus: %d gil" % (v[0], v[1][r % len(v[1])], gil))
                                                 for r in range(nr)]))
        rnd3 = [Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], 3]))]
        def pay(key):                            # (his lines are one text per distinct amount: `_text_id`)
            gil = rate_of(key) * PF.PROFILES[key].get("gain", 10)
            return make(gil)
        ops += lines(pay) + [hb._w(at["stern"] - GR.HOLD_SAY)] + rnd3 + \
            by_voice(lambda v: _chain(RND2, [say3("%s\n“%s”" % (v[0], v[2][r % len(v[2])])) for r in range(nr)])) + \
            [hb._w(at["muffled"] - at["stern"] - GR.HOLD_SAY)] + [hb._req(e, 6, wait=False) for e in actors[1:]] + \
            rnd3 + lines(muffled) + gap(at["muffled2"] - at["muffled"] - GR.MUFFLED_SAY) + \
            [Op(bytes([0x85, RND2[0] << 4, RND2[1], 1])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], 3]))] + \
            lines(muffled) + gap(at["desperate"] - at["muffled2"] - GR.MUFFLED_SAY) + \
            rnd3 + lines(desperate_) + gap(at["end"] - at["desperate"] - GR.MUFFLED_SAY)
        others = [PT, IT]
    lesson = _lesson_ops(hb, sec, actors[0], icon, hush, lines, slot_of, leave) if icon is not None else []
    ops += [hb._req(e, 4, wait=False) for e in actors] + \
        [Op(bytes([0x95, PCNT[0], PCNT[1]])), Op(bytes([0x8D, PCNT[0] << 4, PCNT[1], 3]))] + \
        lines(block) + lesson + resume(total, others)
    if kind == "hold":                           # (user) she won't: straight off, her line, the loss, annoyed
        def refused(key):
            pr = PF.PROFILES[key]
            if pr["hold"] == "likes":
                return []
            loss = rate_of(key) * pr["loss"]
            k = slot_of(key)
            texts = [say3(GR.NAMES[key] + "\n" + t + _gil_note(-loss), 2) for t in pr["refuse"]]
            return [Op(bytes([0x99, RND2[0], RND2[1]])), Op(bytes([0x8D, RND2[0] << 4, RND2[1], len(texts)]))] + \
                _chain(RND2, texts) + _take_gil(loss) + _annoy(k, leave(key) if leave else [])
        length = w0 + w1 + w2 + 10
        lesson2 = _lesson_ops(hb, sec, actors[0], icon, hush, lines, slot_of, leave) if icon is not None else []
        ops += [asm.goto(no), refuse, sound(FAIL_SOUND)] + [hb._req(e, 4, wait=False) for e in actors] + \
            lines(refused) + lesson2 + \
            resume(length, [PT, IT])
    return ops + [no]


LESSON_RAISE, LESSON_SWING = 4, 5                   # frames: arm out towards his side, the swing (then straight back
                                                    # to his pulled-back pose: Cloud's slot 7, user)
LESSON_DOWN = 45                                    # (user) the swing ends 45 degrees down, in front of him
LESSON_OUT = 0.55                                   # (user, since: less swing) the wind-up only this far to his side
LESSON_IN = 30                                      # (user, since) the swing ends this far in across him: her face
LESSON_SAY = GR.PAUSE_FRAMES[1]                     # her reaction's window (closed by hush3's slot 2)


def _lesson_anim(ctx, base, name, hrc="zcla.hrc"):
    """(user) Cloud's lesson: frame 0 of his stroke `base` (pulled back) held, his right arm straight,
    a short wind-up `LESSON_OUT` of the way out to his right side, then swung to LESSON_DOWN down in
    front of him and `LESSON_IN` in across him (her face) (his body's own axes: up = pelvis to neck,
    right = between the shoulders, so it works lying down too). Played once (slot 7)."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    I = [b[0] for b in sk].index
    a = fa.Anim(ctx.char_file(base.lower() + ".a"))
    rr, rp, rots = a.frames[0]
    root = [rp[0], -rp[1], rp[2]]
    F = fa.forward(sk, rr, root, rots)
    W = [m for m, _, _ in F]
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]
    sub = lambda u, v: [u[k] - v[k] for k in range(3)]
    up = unit(sub(F[I("chest")][2], F[I("hip")][1]))
    right = unit(sub(F[I("r_uparm")][1], F[I("l_uparm")][1]))
    right = unit(sub(right, [up[k] * sum(right[j] * up[j] for j in range(3)) for k in range(3)]))
    fwd = [up[1] * right[2] - up[2] * right[1], up[2] * right[0] - up[0] * right[2], up[0] * right[1] - up[1] * right[0]]
    # (up x right: his forward if right is his right; checked below on a standing pose: -z)
    a_, i_ = math.radians(LESSON_DOWN), math.radians(LESSON_IN)
    front = unit([(fwd[k] * math.cos(i_) - right[k] * math.sin(i_)) * math.cos(a_) - up[k] * math.sin(a_) for k in range(3)])
    arm = ("r_uparm", "r_foarm", "r_hand")
    bdir = lambda m: fa._vec(m, [0, 0, -1])
    start = unit(bdir(W[I("r_uparm")]))
    side = unit([start[k] + (right[k] - start[k]) * LESSON_OUT for k in range(3)])

    def pose(d):
        Wt = list(W)
        for n in arm:
            Wt[I(n)] = fa._mul(_align(fa, bdir(W[I(n)]), d), W[I(n)])
        return (rr, rp, fa.local_rotations(sk, rr, Wt))
    lerp = lambda u, v, w: unit([u[k] + (v[k] - u[k]) * w for k in range(3)])
    frames = [pose(lerp(start, side, (t + 1) / LESSON_RAISE)) for t in range(LESSON_RAISE)]
    frames += [pose(lerp(side, front, ((t + 1) / LESSON_SWING) ** 2)) for t in range(LESSON_SWING)]   # (speeding up)
    a.frames = frames
    ctx.char_file(name.lower() + ".a", a.build())
    return name + ".tor"


def lesson_slot(lesson_i, back_i):
    """(user) Cloud's slot 7: the lesson once: its wind-up (CANM!2 frames 0..LESSON_RAISE, ANIMW), the
    slap sound as the swing starts (user: it came late at the end), the swing, then at once his
    pulled-back pose (back_i: the position's stop anim kind 0) again (as 660's Scarlet slap)."""
    last = LESSON_RAISE + LESSON_SWING - 1
    return [_animb(), Op(bytes([0xBC, lesson_i, 0, LESSON_RAISE - 1, 1])), Op(b"\xAC"), sound(SLAP_SOUND),
            Op(bytes([0xBC, lesson_i, LESSON_RAISE - 1, last, 1])), Op(b"\xAC"),
            _animb(), Op(bytes([0xA2, back_i, 1])), Op(bytes([0xAE, back_i, 1]))]


def _lesson_ops(hb, sec, cloud, icon, hush, lines, slot_of, leave):
    """(user) After she stops, breaks free of a hold or refuses one: the lesson prompt (the icon's
    slot 6, IWIN 4) for ICON_FRAMES; Square in it (LSN, `sqkey`) = Cloud's slot 7 (his lesson anim
    for this position, waited for: nothing interrupts it), the slap sound, her reaction by her
    profile's `lesson` (a "no" = a strike: +1 annoyance, leave(key) at LEAVE_AT). The position's time
    (NEXT) and the next prompts (PT, IT, TT) move on by what it took."""
    no, done = asm.nop(), asm.nop()
    ops = [asm.setbyte(LSN, 0), hb._req(icon, 6)] + [hb._arith(0x86, v, ICON_FRAMES) for v in (NEXT, PT, IT, TT)]
    ops += [asm.if_byte(LSN, "==", 1, no), hb._w(LESSON_RAISE + LESSON_SWING + 4)]   # (sqkey started his swing)

    def react(key):
        pr = PF.PROFILES[key]
        kind, k = pr.get("lesson", "likes"), slot_of(key)
        yes_l, no_l = asm.nop(), asm.nop()
        say = lambda t: [Op(b"\x52\x03\x00\x01"), hb._window(GR.NAMES[key] + "\n" + t, 3, 8, LINE_Y),
                         hb._req(hush, 2, wait=False), asm.message(3, _text_id(sec, GR.NAMES[key] + "\n" + t))]
        out = []
        if kind == "dislikes":
            out += [asm.goto(no_l)]
        elif kind == "mood":
            out += [Op(bytes([0x99, RND2[0], RND2[1]])), asm.if_byte(RND2, "<", pr["lesson_odds"], no_l)]
        elif kind == "rules":
            out += [asm.if_byte(RULES, "!=", 0, no_l)]
        if kind != "dislikes":
            out += [yes_l] + say(pr["lesson_yes"]) + [asm.goto(done)]
        if kind != "likes":
            out += [no_l, sound(FAIL_SOUND)] + say(pr["lesson_no"]) + _annoy(k, leave(key) if leave else [])
        return out + [asm.goto(done)]
    ops += lines(react) + [done]
    extra = LESSON_RAISE + LESSON_SWING + 4 + LESSON_SAY
    ops += [hb._arith(0x86, v, extra) for v in (NEXT, PT, IT, TT)] + [no]
    return ops


FAIL_SOUND = 3                                      # (user) the menu's "can't do that" buzz (0x74580A id 3;
                                                    # the field SOUND id assumed the same: untested)


def _hold_entities(hb, model, sprite_dir, place, cloud=None):
    """(user) The hold's two helper entities' scripts: `icon` (the Square sprite, model `model`: slot 2
    = place ops (its XYZI for the position), slot 3 = shown ICON_FRAMES with IWIN 1 (a hold), slot 4
    = the same with IWIN 2 (a slap prompt: REQ'd by the voice with a slap / spank / smack line)) and
    `sqkey` (once a frame: Square held (IFKEY 0x80) going from up to down while IWIN 1 = a hold: SQ 1,
    the materia sound; while IWIN 2 = a slap: SLP 1, the slap sound; the window closed)."""
    hide = [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    icon = {0: [Op(bytes([0xA1, model])), hb._visi(0), Op(bytes([0xB3, 0, sprite_dir]))] + hide + [asm.ret(), asm.ret()],
            2: place + [asm.ret()],
            3: [asm.setbyte(IWIN, 1), hb._visi(1), hb._w(ICON_FRAMES), hb._visi(0), asm.setbyte(IWIN, 0), asm.ret()],
            4: [asm.setbyte(IWIN, 2), hb._visi(1), hb._w(ICON_FRAMES), hb._visi(0), asm.setbyte(IWIN, 0), asm.ret()],
            5: [asm.setbyte(IWIN, 3), hb._visi(1), hb._w(ICON_FRAMES), hb._visi(0), asm.setbyte(IWIN, 0), asm.ret()],
            6: [asm.setbyte(IWIN, 4), hb._visi(1), hb._w(ICON_FRAMES), hb._visi(0), asm.setbyte(IWIN, 0), asm.ret()]}
    wait = hb._w(1)
    back, up, slap, there, lesson = asm.goto_back(wait), asm.setbyte(SQH, 0), asm.nop(), asm.nop(), asm.nop()
    sqkey = {0: [asm.ret(), wait, Op(bytes([0x30]) + struct.pack("<H", SQUARE_KEY) + b"\x00", target=up),
                 asm.if_byte(SQH, "==", 0, back), asm.setbyte(SQH, 1), asm.if_byte(IWIN, "==", 1, slap),
                 asm.setbyte(SQ, 1), asm.setbyte(IWIN, 0), asm.goto_back(wait),      # (the sound: success / failure)
                 slap, asm.if_byte(IWIN, "==", 2, there), asm.setbyte(SLP, 1), sound(SLAP_SOUND),
                 asm.setbyte(IWIN, 0), asm.goto_back(wait),
                 there, asm.if_byte(IWIN, "==", 3, lesson), asm.setbyte(THR, 1),                         # (user) "there"
                 asm.setbyte(IWIN, 0), asm.goto_back(wait),
                 lesson, asm.if_byte(IWIN, "==", 4, back), asm.setbyte(LSN, 1)] + \
                ([hb._req(cloud, 7, wait=False)] if cloud is not None else []) + [               # (user) the swing at once
                 asm.setbyte(IWIN, 0), back, up, asm.goto_back(wait), asm.ret()]}
    return icon, sqkey


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
    # (user) the stops: each pause position's frame 0 (pulled back) held: ZM<p>9 / ZN<p>9, after the
    # rest; then (user: the hold) its deepest frame (the stroke's middle) held: ZM<p>8 / ZN<p>8; then
    # hers only, her try to pull back (`_try_anim`): ZM<p>7 (`hold_index`)
    names = [p_["name"] for p_ in POSITIONS]
    for digit, frame in (("9", 0), ("8", 7)):
        for pn in PAUSE_POS:
            p = names.index(pn)
            for who, base, out in (("girl", POSITIONS[p]["girl"][0], girl), ("cloud", POSITIONS[p]["cloud"][0], cloud)):
                a = fa.Anim(ctx.char_file(base.lower() + ".a"))
                a.frames = a.frames[frame:frame + 1]
                name = ("ZM" if who == "girl" else "ZN") + chr(ord("A") + p) + digit
                ctx.char_file(name.lower() + ".a", a.build())
                out.append(name + ".tor")
    for pn in PAUSE_POS:
        p = names.index(pn)
        name = "ZM" + chr(ord("A") + p) + "7"
        _try_anim(ctx, POSITIONS[p]["girl"][0], name)
        girl.append(name + ".tor")
    # (user) the group's third part, "end" (ZREN / ZCTZ, `_end_poses`): its speeds, then its stop poses
    # (pulled back 9, deepest 8; hers: the try 7), last of all: `end_index`
    for who, base, out in (("girl", "ZREN", girl), ("cloud", "ZCTZ", cloud)):
        frames = fa.Anim(ctx.char_file(base.lower() + ".a")).frames
        assert len(frames) == 15, (base, len(frames))
        pre = ("ZM" if who == "girl" else "ZN") + END_LETTER
        for s, n in enumerate(SPEEDS):
            a = fa.Anim(ctx.char_file(base.lower() + ".a"))
            a.frames = [frames[i * len(frames) // n] for i in range(n)]
            ctx.char_file((pre + str(s)).lower() + ".a", a.build())
            out.append(pre + str(s) + ".tor")
        for digit, frame in (("9", 0), ("8", 7)):
            a = fa.Anim(ctx.char_file(base.lower() + ".a"))
            a.frames = frames[frame:frame + 1]
            ctx.char_file((pre + digit).lower() + ".a", a.build())
            out.append(pre + digit + ".tor")
        if who == "girl":
            _try_anim(ctx, base, pre + "7")
            out.append(pre + "7.tor")
    # (user) Cloud's lessons, last of all (`lesson_index`): from each hold position's pulled-back frame
    for pn in LESSON_POS:
        base = "ZCTZ" if pn == "end" else POSITIONS[names.index(pn)]["cloud"][0]
        letter = END_LETTER if pn == "end" else chr(ord("A") + names.index(pn))
        cloud.append(_lesson_anim(ctx, base, "ZN%sL" % letter))
    return girl, cloud


LESSON_POS = PAUSE_POS + ["end"]                    # (user) where Cloud's lesson plays (`lesson_index`)


def lesson_index(cloud_first, pn):
    """Cloud's lesson anim for position pn ("end": the group's part three) in his `_speeds` list."""
    return cloud_first + 4 * len(POSITIONS) + 2 * len(PAUSE_POS) + 6 + LESSON_POS.index(pn)


END_LETTER = "O"                                    # (ZM/ZN A..J the positions, K..N the group's still poses)


def end_index(cloud, k):
    """Offset (from a model's first `_speeds` anim) of the group's "end" anim k: 0-3 the speeds,
    4 pulled back, 5 deepest, 6 (hers only) the try."""
    return 4 * len(POSITIONS) + (2 if cloud else 3) * len(PAUSE_POS) + k


# (user) the group's third part, "end": she lies on her back as in mission's "flap" (knees falling
# open and closed), arms straight out to her sides (`END_ARMS`), head tilted `END_HEAD` forward and
# bobbing `END_BOB` with each stroke; Cloud stands on the bed over her shoulders facing the other way
# from head reverse (towards her head's end), crouched to `END_LOW` of his pelvis height, legs swung
# `END_SPREAD` out (his feet either side of her chest, inside her arms), his pelvis `END_AHEAD` behind
# her head's middle, both hands on her head (the head position's hold), the resisted thrust
END_HEAD, END_BOB, END_ARMS, END_SHIFT = 50, 15, 90, 4
END_AHEAD, END_LOW, END_SPREAD = 3.0, 0.45, 30
END_IN = 17                                         # her XYZI this much further into the bed than head reverse's


def _end_poses(ctx):
    """ZREN (Ruby) and ZCTZ (bare Cloud) for the group's "end"; returns (gap, right): her origin in
    his frame for `_cloud_stand(hold=)` (her head's middle END_AHEAD ahead of his pelvis)."""
    from ff7 import fieldanim as fa
    hb = _hb()
    hb._on_back(ctx, "ZREN.tor", END_ARMS, head=END_HEAD, head_rock=END_BOB)
    a = fa.Anim(ctx.char_file("zren.a"))
    n = len(a.frames)
    assert n == 15, n
    a.frames = [a.frames[(i + END_SHIFT) % n] for i in range(n)]   # (her head furthest forward at frame 7: his deepest)
    ctx.char_file("zren.a", a.build())
    J = _joints(ctx, RUBY_HRC, "zren.a")
    hc = [(J["chest"][k] + J["head"][k]) / 2 for k in range(3)]            # (the head bone starts at the chest's end)
    gap, right = END_AHEAD - hc[2], -hc[0]
    hb._cloud_stand(ctx, "ZCTZ.tor", arms=hb.STAND_ARMS_LR, elbow_in=hb.STAND_ELBOW_IN, low=END_LOW, lean=hb.HEAD_LEAN,
                    elbows_out=hb.HEAD_ELBOWS_OUT, spread=END_SPREAD, hold=(RUBY_HRC, "zren.a", gap, right),
                    still_upper=True, resist=True)
    C = _joints(ctx, hb.CLOUD_BARE_HRC.lower(), "zctz.a")
    for s in "lr":                                   # his feet outside her chest, inside her arms
        f = C[s + "_tibia"]
        her = [-f[0] - right, f[1], -f[2] - gap]     # (his point in her frame)
        assert abs(her[0]) > 3.5, ("his feet clear of her chest", s, her)
    return gap, right


def hold_try_delay():
    """Frames her struggle (slot 6) waits after being REQ'd with the hold's muffled line."""
    return GR.HOLD_AT["struggle"] - GR.HOLD_AT["muffled"]


def hold_index(first, pn, kind=0):
    """The anim index of position pn's stop pose in a model whose `_speeds` anims start at first:
    kind 0 pulled back, 1 the deepest (the hold), 2 her try to pull back (girls only)."""
    return first + 4 * len(POSITIONS) + kind * len(PAUSE_POS) + PAUSE_POS.index(pn)


GAUGE_W, GAUGE_H = 64, 8                    # texture pixels (in a 64 x 64 texture)
GAUGE_PX, CURSOR_PX, CURSOR_UP = 45, 6, 6   # (user: cursor 50%: 12 -> 6)  # on-screen widths (user: the bar a quarter of its first 180); cursor
                                            # above the bar (screen px)
GAUGE_Y = -80                               # the bar's screen y from the view centre (user: at +88 it was below
                                            # the screen: the view sits higher than the centred guess)
LINE_Y = 168                                # Ruby's lines: window at the bottom (the gauge is at the top)
SPRITES = {"QGAA": ("QGAB", "QGAC", "QGAD"), "QCUA": ("QCUB", "QCUC", "QCUD"), "QHOA": ("QHOB", "QHOC", "QHOD")}
PALETTE = [(0, 0, 0, 0), (255, 255, 255, 255), (40, 40, 230, 255), (60, 200, 60, 255),
           (40, 230, 255, 255), (30, 30, 30, 255), (200, 120, 255, 255)]   # B, G, R, A: clear, white, red, green,
                                                                             # yellow, dark, pink (the Square icon)


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


def _icon_pixels():
    """(user) The hold's Square icon: a dark tile with a pink square outline (the PlayStation button)."""
    px = bytearray(64 * 64)
    for y in range(16):
        for x in range(16):
            ring = min(x, y, 15 - x, 15 - y)
            px[y * 64 + x] = 1 if ring == 0 else 6 if ring in (3, 4) else 5
    return px


def _sprites(ctx, half_gauge, half_cursor, half_icon=None):
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
        gauge = hrc.startswith("QG")                   # (QGAA; 672: QGEA)
        icon = hrc.startswith("QH")                    # (QHOA; 672: QHEA: the hold's Square)
        crop = (0, 0, GAUGE_W - 1, GAUGE_H - 1) if gauge else (0, 0, 15, 15) if icon else (0, 0, 15, 11)
        half = half_gauge if gauge else half_icon if icon else half_cursor
        assert half is not None, hrc
        ctx.char_file(hrc.lower() + ".hrc",
                      hrc_text.replace("icemap_sk", hrc.lower() + "_sk").replace("1 GUJD", "1 " + rsd).encode("latin1"))
        ctx.char_file(rsd.lower() + ".rsd",
                      ("@RSD940102\r\nPLY=%s.PLY\r\nMAT=%s.MAT\r\nGRP=%s.GRP\r\nNTEX=1\r\nTEX[0]=%s.TIM\r\n"
                       % (ply, ply, ply, tex)).encode("latin1"))
        ctx.char_file(ply.lower() + ".p", mm.mesh(donor_p, crop, half))
        head = bytearray(template[:0xEC])
        struct.pack_into("<II", head, 0x3C, 64, 64)
        pal = b"".join(bytes(c) for c in PALETTE).ljust(16 * 4, b"\0")
        ctx.char_file(tex.lower() + ".tex", bytes(head) + pal + bytes(_gauge_pixels() if gauge else _icon_pixels() if icon else _cursor_pixels()))
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


def _icon_at(cam, mesh, sx, sy, near):
    """(user) The hold icon's spot: ICON_Y below the view centre (sx, sy), at the gauge's depth."""
    q = _unproject(cam, sx, sy + ICON_Y, near)
    return round(q[0]), round(q[1]), round(q[2]), _nearest_tri(mesh, q[0], q[1])


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
PRONE_UP = 12                                       # ... lying on her (his own prone pose: ~her body's depth up;
                                                    # user, since: raised off the bed a bit, was 8)


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


# (user, since) "behind" with her hands planted on the bed and both feet on the floor; only her
# hips move (following Cloud's pelvis in his ZCTE), her upper body pivoting so her shoulders stay
# put and her arms re-bending (two-bone IK) to keep the hands where they are; legs likewise.
# From her stand: upper body leaned BEHIND_LEAN forward, knees bent BEHIND_KNEE, each wrist
# BEHIND_REACH of her arm's full length from the shoulder, down to the mattress (BEHIND_BED_TOP
# field units above the floor, the left bed), the hands flat pointing forward; her pelvis
# WALL_GAP (660) in front of his at frame 0.
BEHIND_LEAN, BEHIND_KNEE, BEHIND_REACH, BEHIND_BED_TOP, BEHIND_PALM = 40, 30, 0.92, 54, 0.4


def _behind_bed(ctx, name, hrc=RUBY_HRC, stand=RUBY_STAND):
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file(hrc).decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file(stand))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]                     # y down, floor 0, she faces -z, her left +x
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    fk = lambda W, r: fa.forward(sk, rr, list(r), fa.local_rotations(sk, rr, W))
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    add = lambda a, b: [a[k] + b[k] for k in range(3)]
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    unit = lambda v: [c / math.sqrt(dot(v, v)) for c in v]
    cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    bdir = lambda m: fa._vec(m, [0, 0, -1])
    side, up, fwd = [1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]

    def align(a, b):
        a, b = unit(a), unit(b)
        ax = cross(a, b)
        si = math.sqrt(dot(ax, ax))
        return fa.axis_angle(ax, math.degrees(math.atan2(si, dot(a, b)))) if si > 1e-9 else fa.euler_matrix(0, 0, 0)

    def turned(W, bones, angle, test):
        e0 = {names[i]: e for i, (_, _, e) in enumerate(fk(W, root))}
        for sg in (1, -1):
            M = [fa._mul(fa.axis_angle(side, sg * angle), m) if names[i] in bones else m for i, m in enumerate(W)]
            e1 = {names[i]: e for i, (_, _, e) in enumerate(fk(M, root))}
            if test(e0, e1):
                return M
        raise AssertionError((name, sorted(bones)))

    def ik(W, F, top, low, target, pole):           # two-bone: `top`/`low` re-aimed so low's end = target
        i, j = I(top), I(low)
        S = F[i][1]
        L1, L2 = math.dist(F[i][1], F[i][2]), math.dist(F[j][1], F[j][2])
        D = sub(target, S)
        dd = math.sqrt(dot(D, D))
        assert dd < L1 + L2 - 1e-3, (name, top, dd, L1 + L2)
        u = unit(D)
        pp = unit(sub(pole, [dot(pole, u) * c for c in u]))
        a = (L1 * L1 - L2 * L2 + dd * dd) / (2 * dd)
        K = add(S, [a * u[k] + math.sqrt(max(0.0, L1 * L1 - a * a)) * pp[k] for k in range(3)])
        W = list(W)
        W[i] = fa._mul(align(bdir(W[i]), sub(K, S)), W[i])
        W[j] = fa._mul(align(bdir(W[j]), sub(target, K)), W[j])
        return W
    legs = {n for n in names if n[:2] in ("l_", "r_") and not any(k in n for k in ("chest", "collar", "arm", "hand"))}
    upper = set(names) - legs
    feet0 = {s: fk(W, root)[I(s + "_tibia")][2] for s in "lr"}
    for s in "lr":                                   # knees bent: thigh forward half, shin back the whole
        W = turned(W, {s + "_femur", s + "_tibia", s + "_foot"}, BEHIND_KNEE / 2,
                   lambda a, b: b[s + "_femur"][2] < a[s + "_femur"][2])
        W = turned(W, {s + "_tibia", s + "_foot"}, BEHIND_KNEE, lambda a, b: b[s + "_tibia"][2] > a[s + "_tibia"][2])
    W = turned(W, upper, BEHIND_LEAN, lambda a, b: b["head"][2] < a["head"][2] - 1)     # lean forward
    F = fk(W, root)
    drop = F[I("l_tibia")][2][1] - feet0["l"][1]
    root = [root[0], root[1] - drop, root[2]]                                         # ankles back down
    # her pelvis WALL_GAP in front of his (same facing), as 660's `_wall`
    his = fa.Anim(ctx.char_file(_hb().CLOUD_BED["stand"].split(".")[0].lower() + ".a"))
    hz0 = his.frames[0][1][2]
    F = fk(W, root)
    root = [root[0], root[1], root[2] + (hz0 - _dates().WALL_GAP) - F[I("hip")][1][2]]
    F = fk(W, root)
    bed = -BEHIND_BED_TOP / UNIT                                                       # y down
    hands = {}
    for s, out in (("l", 1), ("r", -1)):
        sh = F[I(s + "_uparm")][1]
        L = (math.dist(F[I(s + "_uparm")][1], F[I(s + "_uparm")][2]) +
             math.dist(F[I(s + "_foarm")][1], F[I(s + "_foarm")][2])) * BEHIND_REACH
        dy = (bed - BEHIND_PALM) - sh[1]
        assert dy > 0 and L > dy, (name, "the bed out of reach", dy, L)
        wrist = [sh[0] + 0.3 * out, bed - BEHIND_PALM, sh[2] - math.sqrt(L * L - dy * dy - 0.09)]
        W = ik(W, F, s + "_uparm", s + "_foarm", wrist, [0.4 * out, -0.6, 0.7])          # elbows out and back
        h = I(s + "_hand")
        W[h] = fa._mul(align(bdir(W[h]), [0.0, 0.15, -1.0]), W[h])                    # flat, fingers forward
        hands[s] = wrist
        F = fk(W, root)
    E0 = {names[i]: (st, e) for i, (_, st, e) in enumerate(F)}
    ankles = {s: E0[s + "_tibia"][1] for s in "lr"}
    sh0 = [(E0["l_uparm"][0][k] + E0["r_uparm"][0][k]) / 2 for k in range(3)]
    frames = []
    for _, hp, _ in his.frames:
        d = hp[2] - hz0                                                                 # his pelvis along z
        rt = [root[0], root[1], root[2] + d]
        # the upper body pivots at her pelvis until the shoulders are back over where they were
        best = None
        for a10 in range(-300, 301):
            M = [fa._mul(fa.axis_angle(side, a10 / 10), m) if names[i] in upper else m for i, m in enumerate(W)]
            Fm = fk(M, rt)
            sh = [(Fm[I("l_uparm")][1][k] + Fm[I("r_uparm")][1][k]) / 2 for k in range(3)]
            err = abs(sh[2] - sh0[2])
            if best is None or err < best[0]:
                best = (err, M)
        Wt = best[1]
        for s, out in (("l", 1), ("r", -1)):
            hm = W[I(s + "_hand")]
            Wt = ik(Wt, fk(Wt, rt), s + "_uparm", s + "_foarm", hands[s], [0.4 * out, -0.6, 0.7])
            Wt[I(s + "_hand")] = hm
            Wt = ik(Wt, fk(Wt, rt), s + "_femur", s + "_tibia", ankles[s], fwd)
            Wt[I(s + "_foot")] = W[I(s + "_foot")]
        E = fk(Wt, rt)
        for s in "lr":
            assert math.dist(E[I(s + "_foarm")][2], hands[s]) < 0.05, (name, "hand moved")
            assert math.dist(E[I(s + "_tibia")][2], ankles[s]) < 0.05, (name, "foot moved")
        frames.append((rr, [rt[0], -rt[1], rt[2]], fa.local_rotations(sk, rr, Wt)))
    base.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())
    return {s: -hands[s][2] for s in "lr"}                                              # how far ahead


# (user) "head": her head tilted HEAD_BACK further back (chin up) than 620's kneel (dzbk), as ZRTA
HEAD_BACK = 20
MISSION_PIVOT = 22              # (user) mission: Cloud's thighs swing this far about his knees (pelvic thrust;
                                # user, since: more thrust, was 14)
MISSION_KNEES = 1.4             # (user) his knees this far either side of his midline (legs apart; was 620's 0.7)
HEADREV_NOD = 15                # (user) head reverse: her hanging head rocks this far each way
BEHIND_BED_EDGE = 20            # whitebg1: the left bed starts this far (field units) ahead of "behind"'s spot


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


def _retarget(ctx, names, prefix, hrc, stand, head_down=None):
    """(user: the four more co-stars) Ruby's position anims (`names`, on RUBY_HRC) copied onto
    another skeleton `hrc` by bone name (Ruby's non_1 / non_2 are the l_ / r_chest bones); bones
    she lacks (hair, skirt, Tifa's armer) keep their pose in `stand` (frame 0); the root height
    scaled by her legs (thigh + shin) / Ruby's. New names: prefix + the old name's last two.
    head_down = {position name: degrees}: there her head and everything hanging from it (hair)
    tilted forward about the head's side axis (Tifa's hair on all fours, user)."""
    from ff7 import fieldanim as fa
    src = [{"non_1": "l_chest", "non_2": "r_chest"}.get(b[0], b[0])
           for b in fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1"))]
    dst = fa.skeleton(ctx.char_file(hrc.lower()).decode("latin-1"))
    leg = lambda sk: sum(b[2] for b in sk if b[0] in ("l_femur", "l_tibia"))
    scale = leg(dst) / leg(fa.skeleton(ctx.char_file(RUBY_HRC).decode("latin-1")))
    still = fa.Anim(ctx.char_file(stand)).frames[0][2]
    assert len(still) >= len(dst), (hrc, stand, len(still), len(dst))
    names_d = [b[0] for b in dst]
    under = {names_d.index("head")}                      # the head and its descendants (hair)
    for i, b in enumerate(dst):
        if b[1] in [names_d[j] for j in under]:
            under.add(i)
    head = names_d.index("head")

    def lift(rr, rots, deg):
        W = [m for m, _, _ in fa.forward(dst, rr, [0.0, 0.0, 0.0], rots)]
        top = lambda M: fa.forward(dst, rr, [0.0, 0.0, 0.0], fa.local_rotations(dst, rr, M))[head][2]
        side = fa._vec(W[head], [1.0, 0.0, 0.0])
        for sg in (1, -1):
            R = fa.axis_angle(side, sg * deg)
            M = [fa._mul(R, m) if i in under else m for i, m in enumerate(W)]
            if top(M)[1] > top(W)[1]:                        # (y down) the head's top went down: forward
                return fa.local_rotations(dst, rr, M)
        raise AssertionError("head_down")
    out = []
    for n in names:
        a = fa.Anim(ctx.char_file(n.split(".")[0].lower() + ".a"))
        pi = ord(n.split(".")[0][2]) - ord("A")
        pos = POSITIONS[pi]["name"] if pi < len(POSITIONS) else None      # (K / L: the group's still poses)
        deg = (head_down or {}).get(pos)
        frames = []
        for rr, rp, rots in a.frames:
            new = [rots[src.index(b[0])] if b[0] in src else still[i] for i, b in enumerate(dst)]
            if deg:
                new = lift(rr, new, deg)
            frames.append((rr, [c * scale for c in rp], new))
        a.frames = frames
        struct.pack_into("<I", a.head, 8, len(dst))
        name = prefix + n.split(".")[0][2:]
        ctx.char_file(name.lower() + ".a", a.build())
        out.append(name + ".tor")
    return out


_BUILT = {}                                          # the poses, built once for every set


def _shoot(ctx, back, cast=None):
    """The movie set: FIELD with Ruby / Skye, or (cast = a _movie_girls entry) her own set."""
    hb, dt = _hb(), _dates()
    if not _BUILT:
        _bob(ctx)
        _prone(ctx)
        _head_back(ctx)
        _cloud_dog(ctx)
        _cloud_prone(ctx)
        for pos in POSITIONS:
            _place(ctx, pos)
        ahead = _behind_bed(ctx, "ZRWA.tor")                     # (user) "behind": hands on the bed, hips moving
        assert min(ahead.values()) * UNIT > BEHIND_BED_EDGE + 8, ahead          # the hands over the mattress
        hb._cloud_thrust(ctx, "ZCTU.tor", pivot=MISSION_PIVOT, knee_gap=MISSION_KNEES)   # (user) mission: legs still, pelvis thrusting
        hb._on_back(ctx, "ZRHN.tor", hb.HEADREV_ARMS, hip_lift=hb.HEADREV_LIFT, head_down=True,
                    head_nod=HEADREV_NOD)                        # (user) head reverse: her head rocking
        dt._koala(ctx, "ZRKA.tor", RUBY_HRC, RUBY_STAND)         # (user) "holding": Tifa's koala hug on her
        _BUILT["end"] = _end_poses(ctx)                          # (user) the group's "end"
        _BUILT["anims"] = _speeds(ctx)
        _still_poses(ctx)                                        # (the group shoot's waiting girls)
    f = ctx.new_field(cast["field"] if cast else FIELD, ctx.field(BASE).build())
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
        back_ = (cast or {}).get("cloud_back", {}).get(pos["name"])
        if back_:                                            # (user) this girl: Cloud further from her
            vx, vy = c[0] - pos["girl"][1][0], c[1] - pos["girl"][1][1]
            n_ = math.hypot(vx, vy)
            c = _spot(mesh, round(c[0] + vx / n_ * back_), round(c[1] + vy / n_ * back_), pos["cloud"][1][2],
                      pos["cloud"][2])
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
    if not cast:
        ctx.movie_places = places                            # (678's loose group shoot: the same room's spots)
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
        pl["icon"] = _icon_at(cam, mesh, sx, sy, near)
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

    # models: 2 bare Cloud, 3 Ruby bare (or this set's girl), 4 cameraman, 5 gauge, 6 cursor (, 7 Skye)
    girl_anims, cloud_anims = _BUILT["anims"]
    cl0 = loader.models[0]
    loader.models.append(ModelLoader.with_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), cloud_anims))
    cfirst = len(ModelLoader.anims(loader.models[2])) - len(cloud_anims)
    if cast:                                     # her undressed model, Ruby's poses retargeted onto her
        dfield, dmodel, dhrc = cast["donor"]
        donor = ModelLoader(ctx.field(dfield).section("models"))
        assert ModelLoader.hrc(donor.models[dmodel]).upper() == dhrc, (cast["name"], ModelLoader.hrc(donor.models[dmodel]))
        r = loader.add_from(donor, dmodel)
        her_anims = _retarget(ctx, girl_anims, cast["prefix"], dhrc,
                              ModelLoader.anims(donor.models[dmodel])[0].split(".")[0].lower() + ".a",
                              cast.get("head_down"))
        loader.models[r] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[r], cast["hrc"],
                                                                       ModelLoader.name(loader.models[r])[:-5] + "_b.char"),
                                                  her_anims)
        _BUILT.setdefault("cast", {})[cast["key"]] = her_anims + _retarget(
            ctx, STILL, cast["prefix"], dhrc, ModelLoader.anims(donor.models[dmodel])[0].split(".")[0].lower() + ".a",
            cast.get("head_down"))                               # (+ the group's still poses)
        gfirst = len(ModelLoader.anims(loader.models[r])) - len(her_anims)
    else:
        rd = ModelLoader(ctx.field(RUBY_DONOR[0]).section("models"))
        r = loader.add_from(rd, RUBY_DONOR[1])
        loader.models[r] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[r], BARE_HRC,
                                                                       ModelLoader.name(loader.models[r])[:-5] + "_b.char"),
                                                  girl_anims)
        gfirst = len(ModelLoader.anims(loader.models[r])) - len(girl_anims)
    assert r == 3, r
    cd = ModelLoader(ctx.field(CAMERA_DONOR[0]).section("models"))
    cm = loader.add_from(cd, CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(CAMERA_FILM)
    if "sprites" not in _BUILT:                  # (the same base field: the same sizes for every set)
        _BUILT["sprites"] = _sprites(ctx, half, half_cursor, ICON_PX / 2 * near / cam.zoom / unit)
    sprites = _BUILT["sprites"]
    for hrc in ("QGAA", "QCUA"):
        loader.models.append(ModelLoader.with_scale(sprites[hrc], sprite_scale))
    if cast:
        girls = [(cast["key"], 3, gfirst, None)]
        assert len(loader.models) == 7
    else:
        # 7: Skye bare (user: the new girl after a full shoot), Ruby's anims
        sk = loader.add_from(ModelLoader(ctx.field(SKYE_DONOR[0]).section("models")), SKYE_DONOR[1])
        loader.models[sk] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[sk], SKYE_BARE,
                                                                        ModelLoader.name(loader.models[sk])[:-5] + "_b.char"),
                                                   girl_anims + [RUBY_STAND.split(".")[0].upper() + ".tor"])
        sfirst = len(ModelLoader.anims(loader.models[sk])) - len(girl_anims) - 1   # (then DXID: she stands, intro)
        assert len(loader.models) == 8 and sk == 7
        girls = [("ruby", 3, gfirst, "ruby"), ("skye", 7, sfirst, "skye")]
    icon_model = len(loader.models)                  # (user) the hold's Square icon, last
    loader.models.append(ModelLoader.with_scale(sprites["QHOA"], sprite_scale))
    # (user) the intro: everyone standing at the foot of the left bed (slot 3), the girl's stand =
    # her model's anim 0 (Skye's donor sits: her DXID, appended last)
    stand_of = {g[0]: 0 for g in girls}
    if not cast:
        stand_of["skye"] = len(ModelLoader.anims(loader.models[7])) - 1

    ents = {}
    for name in ("cloudb", girls[0][0], "camera", "gauge", "cursor", "keys", "voice", "hush") + \
            tuple(g[0] for g in girls[1:]) + ("shout", "hush2", "hush3", "icon", "sqkey"):
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
            steps = [[_animb(), Op(bytes([0xA2, first + 4 * p + s, 1])), Op(bytes([0xAE, first + 4 * p + s, 1]))]
                     for s in range(4)]
            return [xyzi(*pl[who]), d_(pl[wdir]), hb._visi(1)] + _chain(STEP, steps)
        off, head = asm.nop(), []
        if girl:
            head = [asm.if_byte(MOVIE_GIRL, "bit_off" if girl == "ruby" else "bit_on", 1, off)]
        return head + by_p(make) + [asm.ret()] + ([off, hb._visi(0), asm.ret()] if girl else [])
    pnames = [p_["name"] for p_ in POSITIONS]
    def hold(first, kind=0):                     # kind 2 (her try): DFANM the deepest, play the try once
        def make(p, pl):
            if pnames[p] not in PAUSE_POS:
                return []
            i = hold_index(first, pnames[p], kind)
            return [_animb(), Op(bytes([0xA2, hold_index(first, pnames[p], 1) if kind == 2 else i, 1])),
                    Op(bytes([0xAE, i, 1]))]
        return by_p(make) + [asm.ret()]
    lesson7 = by_p(lambda p, pl: lesson_slot(lesson_index(cfirst, pnames[p]), hold_index(cfirst, pnames[p], 0))
                   if pnames[p] in PAUSE_POS else [])
    scripts[ents["cloudb"]] = {0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                               2: pose(cfirst, "cloud", "cdir"), 4: hold(cfirst), 5: hold(cfirst, 1),
                               7: lesson7 + [asm.ret()]}                  # (user) the lesson (ANIME1: waited for)
    for key, model, first, test in girls:
        scripts[ents[key]] = {0: [Op(bytes([0xA1, model])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                              2: pose(first, "girl", "gdir", test), 4: hold(first), 5: hold(first, 1),
                              6: [hb._w(hold_try_delay())] + hold(first, 2)}
    scripts[ents["icon"]], scripts[ents["sqkey"]] = _hold_entities(hb, icon_model, sprite_dir, cloud=ents["cloudb"], place=
                                                                   by_p(lambda p, pl: [xyzi(*pl["icon"])]))
    imesh, icam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    ispot = {k: _spot(imesh, *xy) for k, xy in INTRO.items()}
    idir = {k: facing_screen(icam, *v[:3], (0, 1)) for k, v in ispot.items()}
    cx, cy = ispot["cam"][:2]
    idir["cam"] = _dates()._dir_to(ispot["girl"][0] / 2 + ispot["cloud"][0] / 2 - cx,
                                   ispot["girl"][1] / 2 + ispot["cloud"][1] / 2 - cy)     # facing them
    intro = lambda who, anim: [xyzi(*ispot[who]), d_(idir[who]), hb._visi(1),
                               _animb(), Op(bytes([0xA2, anim, 1])), Op(bytes([0xAE, anim, 1])), asm.ret()]
    scripts[CL][3] = [xyzi(*ispot["focus"]), asm.ret()]
    scripts[ents["cloudb"]][3] = intro("cloud", 0)
    for key, model, first, test in girls:
        off = asm.nop()
        head = [asm.if_byte(MOVIE_GIRL, "bit_off" if test == "ruby" else "bit_on", 1, off)] if test else []
        scripts[ents[key]][3] = head + intro("girl", stand_of[key]) + ([off, hb._visi(0), asm.ret()] if test else [])
    idle_cam = ModelLoader.anims(loader.models[cm]).index(CAMERA_IDLE)
    scripts[ents["camera"]] = {0: [Op(bytes([0xA1, 4])), hb._visi(0)] + hide()
                               + [Op(bytes([0xA2, film, 1])), Op(bytes([0xAE, film, 1])), asm.ret(), asm.ret()],
                               2: by_p(lambda p, pl: [xyzi(*pl["cam"]), d_(pl["camdir"])]) +
                               [hb._visi(1), _animb(), Op(bytes([0xA2, film, 1])), Op(bytes([0xAE, film, 1])), asm.ret()],
                               3: intro("cam", idle_cam)}
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
            assert len(lines) in (6, 8, LINES_EACH), (who, POSITIONS[p]["name"], len(lines))
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
                            hb._req(ents["hush"], 2, wait=False)] +
                           ([hb._req(ents["icon"], 4, wait=False)] if _slaps(text) else []) +   # (user) a slap prompt
                           [asm.message(1, texts[t])])
            return _chain(K, out)
        return line
    if cast:
        voice += by_p(lines_of(cast["name"], cast["lines"]))
    else:
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
    scripts[ents["hush3"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(GR.PAUSE_FRAMES[1]), Op(b"\x54\x03"), asm.ret()],
                              3: [hb._w(GR.HOLD_SAY), Op(b"\x54\x03"), asm.ret()],
                              4: [hb._w(GR.MUFFLED_SAY), Op(b"\x54\x03"), asm.ret()]}

    # director
    lost, wrap, tick, hi_red = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    # (user: speed up the switch) all at once, not each waited on in turn
    place_all = lambda: [hb._req(e, 2, wait=False) for e in (CL, ents["cloudb"], *(ents[g[0]] for g in girls),
                                                             ents["camera"], ents["gauge"], ents["icon"])] + [hb._w(6)]

    def pause_cond(no):                              # only in PAUSE_POS
        doit = asm.nop()
        return [asm.if_byte(P, "!=", pnames.index(n), doit) for n in PAUSE_POS] + [asm.goto(no), doit]

    def pause_lines(block):
        if cast:
            return block(cast["key"])
        skye_, done_ = asm.nop(), asm.nop()
        return [asm.if_byte(MOVIE_GIRL, "bit_off", 1, skye_)] + block("ruby") + [asm.goto(done_), skye_] + \
            block("skye") + [done_]
    def rate_of(key):                            # the girl's gil a press
        return cast["rate"] if cast else PAY_RATE * (SKYE_PAY if key == "skye" else 1)
    # (user) she's had enough (`_movie_profiles`): her line, then the shoot ends as a CUT
    walkout = asm.nop()
    leave = lambda key: lose_affection(key) + hb._say(sec, GR.NAMES[key] + "\n" + PF.PROFILES[key]["leave"]) + \
        [asm.goto(walkout)]
    pause = _pause_ops(hb, sec, [ents["cloudb"]] + [ents[g[0]] for g in girls], ents["hush3"], pause_lines,
                       pause_cond, ents["icon"], rate_of, leave=leave)
    main = [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS, 500), asm.setword(VEL, 1000),
            asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(P, 0),
            asm.setbyte(STEP, 1), asm.setbyte(K, 0), asm.setword(NEXT, MINUTE), asm.setbyte(FIN, 0),
            # (user, profiles) one-girl shoots: the cameraman's briefing counts as the rules (Elena)
            asm.setbyte(RULES, 1), asm.setbyte(CTRL, 0), asm.setbyte(_ann(0), 0)] + \
           [hb._req(e, 3) for e in (CL, ents["cloudb"], *(ents[g[0]] for g in girls), ents["camera"])] + \
           [hb._w(20)]                               # (user) the intro: all standing by the left bed
    main += [Op(hb.FADE_IN), Op(b"\x6C")]            # (user: the first position showed the models move too)
    main += say("“Places, everyone! Here's how it works, star:\n tap OK to keep the rhythm going.”")
    main += say("“Faster means more footage, and every push\n is %d gil in your pocket. But watch the meter:\n"
                % (cast["rate"] if cast else PAY_RATE) +
                " push too hard and it runs away from you,\n ease off and it all falls flat.”")
    main += say("“Hit the red at either end and the shoot's\n over. Ten positions, half a minute each.\n Ready?”")
    # (user) fade out, the first position, fade in, then "Action!"
    main += [Op(hb.FADE_OUT), Op(b"\x6C")] + place_all() + [hb._w(10), Op(hb.FADE_IN), Op(b"\x6C")]
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, MUSIC]) + bytes(8)), hb._w(15)]
    main += say("“...And... ACTION!”")
    main += [asm.setword(FR, 0), asm.setword(PR, 0), asm.setword(NT, TICK)] + _pause_arm(hb, MINUTE) + \
        [asm.setbyte(RUN, 1)]
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
             hb._req(ents["cloudb"], 2, wait=False)] + [hb._req(ents[g[0]], 2, wait=False) for g in girls] + [same]
    main += pause                                    # (user) now and then she needs a moment
    # the next position each minute
    stay = asm.nop()
    # (user: the switch cut into the next position's time) its time counts from the fade-in
    main += [asm.if_word(FR, ">=", NEXT, stay),
             asm.if_byte(P, "<", len(POSITIONS) - 1, wrap),
             # (user: the switch showed awkward, late model moves) paused and hidden by a fade; P moves on
             # only once the screen is black (user: things changed before the fade: the cursor and the
             # speed-change REQs read P at once)
             # (user, since) the meter back to the middle (POS 500, VEL 0) with every new position
             asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(FAST_OUT), Op(b"\x6C"),
             Op(bytes([0x85, P[0] << 4, P[1], 1])),
             asm.setword(POS, 500), asm.setword(VEL, 1000)] + place_all() + \
            [hb._w(4), Op(FAST_IN), Op(b"\x6C"), asm.setword(PR, 0), asm.setword(NT, FR),
             hb._arith(0x86, NT, TICK), asm.setword(NEXT, FR), hb._arith(0x86, NEXT, MINUTE)] + _pause_arm(hb, MINUTE) + [asm.setbyte(RUN, 1),
             stay, asm.goto_back(tick)]
    rx, ry, rz, rt, rdir = back
    def out():                                   # jump back; then wait (a main that reaches RET starts over)
        stop = hb._w(30)
        return [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(WALL), rx, ry, rt, rdir), stop,
                asm.goto_back(stop), asm.ret()]
    # into the right red: a finisher in the last FINISH_FRAMES (user), else a CUT
    skye_bonus, bonus_done = asm.nop(), asm.nop()
    main += [hi_red, sound(RED_SOUND), asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(b"\x54\x02"),
             Op(bytes([0xF2, 0, 0, 0, 0x10, FANFARE]) + bytes(8)), hb._w(45)]      # (a pause: they're mashing OK)
    main += say("“WOW! What a FINISHER!\n That's going straight on the poster!”")
    bonuses = [(cast["rate"], None, cast["aftermath"])] if cast else \
        [(PAY_RATE, None, AFTERMATH[0]), (PAY_RATE * SKYE_PAY, skye_bonus, AFTERMATH[1])]
    if not cast:
        main += [asm.if_byte(MOVIE_GIRL, "bit_off", 1, skye_bonus)]                # bit 1 set: Skye
    for k_, (rate, label, after) in enumerate(bonuses):
        gil = rate * FINISH_BONUS
        main += ([label] if label else []) + [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)]
        main += say("“Here's a bonus, on the spot:\n {:,} gil. You earned it, star!”".format(gil))
        main += hb._say(sec, after)                                         # (user) the girl, after it
        main += [asm.goto(bonus_done)] if k_ + 1 < len(bonuses) else [bonus_done]
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2)] + \
        _advance() + [Op(hb.FADE_OUT), Op(b"\x6C")] + out()                 # (user) the next co-star
    # a CUT (user): he still sells what was shot (the presses so far: a low score), same wait for
    # the cut; only a full shoot raises the star rank
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! You lost it, man!\n ...Fine. We'll sell what we've got.”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [walkout, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]          # (user) she walked off
    main += say(WALKED)
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! Magnificent!”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2)] + \
        _advance() + [Op(hb.FADE_OUT), Op(b"\x6C")] + out()                 # (user) a full shoot: the next co-star
    black = Op(bytes.fromhex("6b00000000000104" "00"))      # FADE type 4: black at once (as the game's
    scripts[0] = {0: [black, asm.ret()] + main}                    # fields that open on a scene)
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    return places[0]["focus"]


SLAP_SOUND = 0x76                                    # the slap (660's dates, Scarlet's)


def _slaps(text):
    """A line about slapping / spanking (user: a slap sound after it; since: a Square prompt instead, the
    slap sound and the hold's bonus if pressed: `_hold_entities`)."""
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


def _sparse(var, blocks):
    """As `_chain`, only the non-empty blocks tested."""
    out, end = [], asm.nop()
    for k, ops in enumerate(blocks):
        if ops:
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
# (user) one co-star at a time: each wrap raises the star rank (`MOVIE_RANK`) and the last star
# leaves; back in Wall Market the cameraman tells why (user: dark humour at the industry's expense)
NEWS = {
    1: ["“Bad news, star: Ruby just turned 19 and\n retired. Hung up her heels for good.”",
        "“But meet Skye, my new discovery.\n She's... enthusiastic. You'll see.”"],
    2: ["“Skye? Gone. Signed an 'exclusive' deal\n with a studio in Junon. They own her\n name, her face and her next three lives.”",
        "“Her lawyer wept with joy. Her agent\n bought a yacht. Skye got a fruit\n basket. That's showbiz, star!”",
        "“Anyway! Your new co-star: Elena. Yes,\n the Turk. Their pension plan turns out\n to be mostly thoughts and prayers.”"],
    3: ["“Elena's out. The Turks found the tapes.\n She's been 'reassigned'. So have her\n fingerprints, I hear.”",
        "“Don't cry for her! Scarlet saw our sales\n figures and wants in. She calls it\n a hostile takeover. Kyahahaha, she said.”"],
    4: ["“Scarlet tried to buy the studio, fire me\n and rename it the Shinra Adult Weapons\n Division. Security walked her out.”",
        "“She took the good lights. And my chair.\n And, somehow, my will to live.”",
        "“Good news, though: Tifa needs money for\n her bar. I offered her exposure. She\n offered me a fist. We settled on cash.”"],
    5: ["“Tifa quit to 'reinvent herself'. They\n all do. Fitness tape, cookbook, tearful\n comeback special. Circle of life, star.”",
        "“But Aerith walked in asking for top\n billing and points on the back end.\n Sweet as a flower, bargains like a shark.”",
        "“Last of my discoveries, so treat her\n right. This business chews girls up.\n I should know: I'm the teeth.”"],
}


NEWS_AFTER = "“The old girls still take a callback if you\n ask for 'em, star. Rent's due for everyone.”"
for r_ in NEWS:                                     # (user) the earlier girls stay on the list
    NEWS[r_].append(NEWS_AFTER)
NEWS[6] = GR.NEWS                                   # (user) after Aerith's wrap: the group shoot


def _advance(state=3):
    """Ops raising the star rank one step (`MOVIE_RANK`) and setting MOVIE_STATE to `state` (None:
    left alone); nothing at the top."""
    done, ops = asm.nop(), []
    for v, b in MOVIE_RANK:
        nxt = asm.nop()
        ops += [asm.if_byte(v, "bit_off", b, nxt), asm.biton(v, b)] + \
               ([asm.setbyte(MOVIE_STATE, state)] if state is not None else []) + [asm.goto(done), nxt]
    return ops + [done]


def _by_rank(blocks):
    """Ops running blocks[r] (lists of ops, r = 1..5) for the current star rank (none at rank 0)."""
    done, ops = asm.nop(), []
    for r in range(len(MOVIE_RANK), 0, -1):
        nxt = asm.nop()
        v, b = MOVIE_RANK[r - 1]
        ops += [asm.if_byte(v, "bit_on", b, nxt)] + blocks[r] + [asm.goto(done), nxt]
    return ops + [done]


def _unlocked_or(skip):
    """Ops jumping to `skip` unless all 20 HB_KID bits are set."""
    assert [k for k in HB_KID] == [((1, 214 + i // 8), i % 8) for i in range(20)]
    return [asm.if_byte((1, 214), "==", 0xFF, skip), asm.if_byte((1, 215), "==", 0xFF, skip)] + \
           [asm.if_byte((1, 216), "bit_on", b, skip) for b in range(4)]


# (user) the group shoot's waiting poses on Ruby's skeleton (retargeted for the others like every
# pose): lying straight on her back, arms by her sides, head tilted back STILL_HEAD_BACK (head
# reverse, not engaged; hips where 620's lying poses have them, so the same XYZI), and the kneel
# ("head", ZMJ0 frame 0); (user) each now and then turning her head left or right (IDLE_TURN, about
# the neck), on two timings (IDLE_A / IDLE_B, girls alternate) so they don't move together:
# ZMK0 lie A, ZML0 kneel A, ZMM0 lie B, ZMN0 kneel B
STILL = ["ZMK0.tor", "ZML0.tor", "ZMM0.tor", "ZMN0.tor"]
STILL_HEAD_BACK = 50
IDLE_A = [(90, 0), (8, 40), (40, 40), (8, 0), (60, 0), (8, -35), (30, -35), (8, 0)]   # (frames, to degrees)
IDLE_B = [(50, 0), (8, -40), (50, -40), (8, 0), (80, 0), (8, 30), (25, 30), (8, 0)]
GROUP_FIELD = "subin_4"                              # (a free maplist name, docs/dates_plan.md)
GROUP_BITS = (3, 4)                                  # MOVIE_GIRL bits 3 + 4 together = the group this shoot
PH, E, TN, USED, CC, VV, RND = ((5, a) for a in range(150, 157))   # phase, engaged girl, turn, girls done,
                                                     # commenter, line kind, random scratch (were 137-143:
                                                     # PARM (5,139) = TN and PT (6,142) = VV/RND, so every
                                                     # pause roll reset the turn count and part one never
                                                     # ended: Cloud stuck on its last girl, user)


def _still_poses(ctx):
    hb = _hb()
    fa, sk, idx, rr, world = hb._standing(ctx)
    x = (1.0, 0.0, 0.0)
    h = idx("head")
    lie = [fa._mul(fa.axis_angle(x, -90), m) for m in world]              # on her back (620 `_on_back`)
    hip_pos = fa.Anim(ctx.char_file("dzba.a")).frames[0][1]
    lie_root = [0.0, -hip_pos[1], hip_pos[2]]
    top = lambda M: fa.forward(sk, rr, lie_root, fa.local_rotations(sk, rr, M))[h][2]
    for sg in (1, -1):                                                     # the head tipped back: its top down
        M = [fa._mul(fa.axis_angle(x, sg * STILL_HEAD_BACK), m) if i == h else m for i, m in enumerate(lie)]
        if top(M)[1] > top(lie)[1] + 0.5:                                  # (y down)
            lie = M
            break
    else:
        raise AssertionError("head back")
    kneel_a = fa.Anim(ctx.char_file("zmj0.a"))
    krr, krp, krots = kneel_a.frames[0]
    kneel_root = [krp[0], -krp[1], krp[2]]
    kneel = [m for m, _, _ in fa.forward(sk, krr, kneel_root, krots)]

    def turns(base, timing):                                               # world matrices -> frames' head turn
        neck = fa._vec(base[h], [0.0, 0.0, -1.0])
        out, a0 = [], 0.0
        for n, a1 in timing:
            for t in range(n):
                a = a0 + (a1 - a0) * (t + 1) / n
                out.append([fa._mul(fa.axis_angle(neck, a), m) if i == h else m for i, m in enumerate(base)])
            a0 = a1
        return out
    for name, timing in ((STILL[0], IDLE_A), (STILL[2], IDLE_B)):
        hb._save_frames(ctx, fa, name, [(lie_root, fa.local_rotations(sk, rr, w)) for w in turns(lie, timing)])
    for name, timing in ((STILL[1], IDLE_A), (STILL[3], IDLE_B)):
        a_ = fa.Anim(ctx.char_file("zmj0.a"))
        a_.frames = [(krr, krp, fa.local_rotations(sk, krr, w)) for w in turns(kneel, timing)]
        ctx.char_file(name.split(".")[0].lower() + ".a", a_.build())


def _spot_or(mesh, x, y, z):
    """(x, y, z, tri): the floor / bed under (x, y) if any (its height + z), else (x, y, z) on the
    nearest triangle (the right bed's near end has little walkable floor; XYZI places directly)."""
    if any(mesh.contains(t, x, y) for t in range(len(mesh.tris))):
        return _spot(mesh, x, y, z)
    return x, y, z, _nearest_tri(mesh, x, y)


SC, RC = (5, 182), (5, 183)                          # (group) staged scene, Cloud's choice in it


def _stage(hb, dt, cam, mesh, scripts, ents, CL, gfirst, n_used, loader, n_g):
    """(user) The group's arguments staged with the models (`_movie_group.STAGING`): every actor's slot 9
    (spot, facing, pose by SC), 10 (the beat) and 11 (the reaction by RC); the player entity's slot 9 (the
    camera on the stage) and the gauge's (hidden). Spots: screen offsets from STAGE_AT, the nearest floor."""
    cand, beds = [], []                               # floor points; (user) bed-top points (z 54 / 100 / 125)
    for x in range(-300, 301, 6):
        for y in range(-360, 41, 6):
            for t in range(len(mesh.tris)):
                if not mesh.contains(t, x, y):
                    continue
                z = round(mesh.height(t, x, y))
                (cand if abs(z) < 2 else beds).append((x, y, t) + tuple(cam.project(x, y, z)) + (z,))
    assert beds and all(c[5] in (54, 100, 125) for c in beds), sorted({c[5] for c in beds})
    ox, oy = GR.STAGE

    def at_screen(dx, dy, taken=(), origin=None, bed=False):   # the nearest floor (or bed-top) point at least
        bx, by = origin if origin else (ox, oy)       # 14 px from those taken (from STAGE, or (user) an anchor's spot)
        free = [c for c in (beds if bed else cand) if all((c[3] - t[0]) ** 2 + (c[4] - t[1]) ** 2 >= 14 ** 2
                                                          for t in taken)]
        c = min(free, key=lambda c: (c[3] - bx - dx) ** 2 + (c[4] - by - dy) ** 2)
        assert (c[3] - bx - dx) ** 2 + (c[4] - by - dy) ** 2 < 30 ** 2, ("no bed there" if bed else "no floor there",
                                                                          dx, dy)
        return c[0], c[1], c[5], c[2]
    centre = at_screen(0, 0)
    who = ["cloud"] + GR.ORDER
    ent = {k: ents["cloudb"] if k == "cloud" else ents[k] for k in who}

    def anim(k, pose):
        if k == "cloud":
            assert pose == "stand"
            return 0
        g = GR.ORDER.index(k)
        if pose == "kneel":
            return gfirst[k] + n_used + 2 * (g % 2) + 1
        return len(ModelLoader.anims(loader.models[3 + g])) - 1 if k == "skye" else 0
    loop_ = lambda i: [_animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    slots = {k: {9: [], 10: [], 11: []} for k in who}
    for i, st in enumerate(GR.STAGING):
        spot, pose = {}, {}
        watchers, taken = iter(GR.WATCH), []
        anchor = st.get("anchor", {})                 # (user) {actor: the actor whose spot it's measured from}
        assert all(k in st["set"] and a in st["set"] and a not in anchor for k, a in anchor.items()), (i, anchor)
        on_bed = st.get("bed", [])                    # (user) these stand / kneel on a bed top, not the floor
        assert all(k in st["set"] for k in on_bed), (i, on_bed)
        # the scene's own first (anchored ones after them), then the watchers
        for k in sorted(who, key=lambda k: (k not in st["set"], k in anchor)):
            sx, sy, ps, face = st["set"][k] if k in st["set"] else next(watchers) + ("stand", "centre")
            origin = cam.project(*spot[anchor[k]][:3])[:2] if k in anchor else None
            spot[k], pose[k] = at_screen(sx, sy, taken, origin, k in on_bed), ps
            taken.append(cam.project(*spot[k][:3]))
        sp_ = {k: cam.project(*spot[k][:3]) for k in who}
        for a in who:
            for b in who:
                assert a >= b or (sp_[a][0] - sp_[b][0]) ** 2 + (sp_[a][1] - sp_[b][1]) ** 2 >= 12 ** 2, \
                    ("staged on top of each other", i, a, b)

        def face_dir(k, f):
            x, y = spot[k][:2]
            if f == "camera":
                return facing_screen(cam, x, y, 0, (0, 1))
            back = f.startswith("away:")
            tx, ty = (centre if f == "centre" else spot[f.split(":")[-1]])[:2]
            return (dt._dir_to(tx - x, ty - y) + (128 if back else 0)) % 256

        def beat(k, ps, f):
            ops = loop_(anim(k, ps)) if ps else []
            if f in ent and not f.startswith("away:"):
                ops += [hb._tura(ent[f])]
            elif f:
                ops += [d_(face_dir(k, f))]
            return ops
        for k in who:
            f = st["set"][k][3] if k in st["set"] else "centre"
            slots[k][9].append([xyzi(*spot[k]), d_(face_dir(k, f)), hb._visi(1)] + loop_(anim(k, pose[k])))
            slots[k][10].append([o for k2, ps, f2 in st["mid"] if k2 == k for o in beat(k, ps, f2)])
            slots[k][11].append(_sparse(RC, [[o for k2, ps, f2 in r if k2 == k for o in beat(k, ps, f2)]
                                            for r in st["react"]]))
    for k in who:
        e, gone = ent[k], asm.nop()
        # (user) a girl who walked off (LEFT bit set) stays hidden; the others are placed (was "bit_off",
        # which hid every girl still on set: the staged scenes showed only Cloud)
        left = [] if k == "cloud" else [asm.if_byte(LEFT, "bit_on", GR.ORDER.index(k), gone),
                                         hb._visi(0), asm.ret(), gone]
        scripts[e][9] = left + _chain(SC, slots[k][9]) + [asm.ret()]
        scripts[e][10] = _sparse(SC, slots[k][10]) + [asm.ret()]
        scripts[e][11] = _sparse(SC, [b if any(o.raw[0] != 0 for o in b) else [] for b in slots[k][11]]) + [asm.ret()]
    # (user) the camera follows the hidden player entity: per scene `camera` (dx, dy) from STAGE puts it on the
    # nearest walkmesh point (floor or bed top) on screen; default the stage point itself
    def cam_spot(st):
        if "camera" not in st:
            return centre
        dx, dy = st["camera"]
        c = min(cand + beds, key=lambda c: (c[3] - ox - dx) ** 2 + (c[4] - oy - dy) ** 2)
        assert (c[3] - ox - dx) ** 2 + (c[4] - oy - dy) ** 2 < 30 ** 2, ("no floor or bed for the camera", dx, dy)
        return c[0], c[1], c[5], c[2]
    scripts[CL][9] = _chain(SC, [[xyzi(*cam_spot(st))] for st in GR.STAGING]) + [asm.ret()]
    scripts[ents["gauge"]][9] = [hb._visi(0), asm.ret()]


def _group(ctx, back):
    """(user) The group shoot: see `_movie_group`."""
    hb, dt = _hb(), _dates()
    f = ctx.new_field(GROUP_FIELD, ctx.field(BASE).build())
    sec = Script.parse(f.sections[0])
    dt._clear_texts(sec)
    mesh = Walkmesh(f.section("walkmesh"))
    cam = Camera(f.sections[1])
    loader = ModelLoader(f.section("models"))
    names = [bytes(n).rstrip(b"\0").decode("latin-1") for n in sec.entity_names]
    assert names[:5] == ["produce", "direct", "ad", "cloud", "child"], names
    assert len(loader.models) == 2
    n_g = len(GR.ORDER)
    # spots: q = phase * 6 + girl
    girl_at, cloud_at, cam_at, gdirs, cdirs = {}, {}, {}, {}, {}
    for k in range(n_g):
        seat = GR.HEAD_SEAT[GR.ORDER[k]]                 # (user: Skye and Scarlet swapped)
        line = 0 if seat < 3 else 1
        gx, gy = GR.HEAD_X[line], GR.HEAD_YS[seat % 3]
        g = _spot(mesh, gx, gy, 0, True)
        assert g[2] > 90, ("not on the middle bed", g)
        sgn = 1 if line == 0 else -1
        c = _spot(mesh, gx + sgn * GR.HEAD_GAP, gy - sgn * GR.HEAD_RIGHT, 0, True)
        assert c[2] == g[2], (g, c)
        girl_at[k], cloud_at[k] = g, c
        gdirs[k], cdirs[k] = (0x40, 0xC0) if line == 0 else (0xC0, 0x40)
        cam_at[k] = _spot(mesh, *GROUP_CAM[0])
        b, lane = divmod(k, 2)
        (lanes, end, top) = GR.BEDS[b]
        gx, gy = lanes[lane], end + GR.HEADREV_ALONG
        g = _spot(mesh, gx, gy, 0, True)
        assert abs(g[2] - top) < 2, ("not on bed", b, g)
        girl_at[6 + k] = g
        back_ = next((g_.get("cloud_back", {}).get("headrev", 0) for g_ in MG.GIRLS if g_["key"] == GR.ORDER[k]), 0)
        cloud_at[6 + k] = _spot_or(mesh, gx, gy - GR.HEADREV_CLOUD - back_, top - GR.BEDS[0][2])   # (raised as the bed)
        gdirs[6 + k] = cdirs[6 + k] = 0x80
        cam_at[6 + k] = _spot(mesh, *GROUP_CAM[1 + b])
        # (user) part three, "end": she lies further onto the bed (head on it), Cloud on the bed over her
        # shoulders facing the bed's end (DIR 0x00), placed from both poses (`_end_poses`: her origin in
        # his frame); asserted on the bed piece
        gap, right = _BUILT["end"]
        g = _spot(mesh, gx, gy + END_IN, 0, True)
        assert abs(g[2] - top) < 2, ("end: not on bed", b, g)
        o = _off((-right, 0.0, -gap), 0x00)
        c = _spot(mesh, round(g[0] - o[0]), round(g[1] - o[1]), 0, True)
        assert abs(c[2] - top) < 2, ("end: Cloud not on the bed", b, c)
        girl_at[2 * n_g + k], cloud_at[2 * n_g + k] = g, c
        gdirs[2 * n_g + k], cdirs[2 * n_g + k] = 0x80, 0x00
        cam_at[2 * n_g + k] = _spot(mesh, *GROUP_CAM[1 + b])
    for q in range(GR.PHASES * n_g):
        cam_at[q] = cam_at[q] + (_dates()._dir_to(cloud_at[q][0] - cam_at[q][0], cloud_at[q][1] - cam_at[q][1]),)
    ctx.group_spots = dict(girl=girl_at, cloud=cloud_at, gdir=gdirs, cdir=cdirs, cam=cam_at)   # (678)
    focus = {q: (cloud_at[q][0], cloud_at[q][1], cloud_at[q][2], cloud_at[q][3]) for q in range(GR.PHASES * n_g)}
    # gauge / cursor per q (as `_shoot`)
    left, top_, right, bottom = screen_range(f.section("triggers"))
    near = min(_view_depth(cam, v) for t in mesh.tris for v in t) * 0.8
    donor_loader = ModelLoader(ctx.field(mm.DONOR_FIELD).section("models"))
    sprite_scale = round(ModelLoader.entry_scale(donor_loader.models[mm.DONOR_MODEL]) * loader.scale / donor_loader.scale)
    gauge, cursor, icon = {}, {}, {}
    for q in range(GR.PHASES * n_g):
        sx, sy = cam.project(*focus[q][:3])
        sx = min(max(sx, left + 160), right - 160)
        sy = min(max(sy, top_ + 120), bottom - 120)
        gy = sy + GAUGE_Y
        g = _unproject(cam, sx, gy, near)
        gauge[q] = (round(g[0]), round(g[1]), round(g[2]), _nearest_tri(mesh, g[0], g[1]))
        icon[q] = _icon_at(cam, mesh, sx, sy, near)
        cursor[q] = []
        for b in range(21):
            off = ((b * 50 + 25) - 500) / 1000 * GAUGE_PX
            p_ = _unproject(cam, sx + off, gy - CURSOR_UP, near)
            cursor[q].append((round(p_[0]), round(p_[1]), round(p_[2]), _nearest_tri(mesh, p_[0], p_[1])))
    gx, gy_, gz = gauge[0][:3]

    def tilt(d):
        a = d * 2 * math.pi / 256
        p0, p1 = cam.project(gx, gy_, gz), cam.project(gx + 50 * math.cos(a), gy_ + 50 * math.sin(a), gz)
        return abs(p1[1] - p0[1]) / (abs(p1[0] - p0[0]) + 1e-9) + (0 if p1[0] > p0[0] else 100)
    sprite_dir = min(range(256), key=tilt)

    # models: 2 bare Cloud, 3-8 the girls (ORDER), 9 cameraman, 10 gauge, 11 cursor
    girl_anims, cloud_anims = _BUILT["anims"]
    # per part (head, head reverse, end): its four speed anims and its stop poses (kind 0 pulled back,
    # 1 deepest, 2 her try), as offsets into the full `_speeds` lists; each model gets only those
    # (user: the scene broke at its start once part three took the girls to 63-71 anims each, the
    # original game's most being 47: now 18 + 2 still poses for a girl, 16 for Cloud)
    HEAD_P, HEADREV_P = [p["name"] for p in POSITIONS].index("head"), [p["name"] for p in POSITIONS].index("headrev")

    def raw_stroke(ph, cloud):
        if ph < 2:
            p = HEAD_P if ph == 0 else HEADREV_P
            return [4 * p + s_ for s_ in range(4)]
        return [end_index(cloud, s_) for s_ in range(4)]

    def raw_stop(ph, kind, cloud):
        if ph < 2:
            return hold_index(0, ("head", "headrev")[ph], kind)
        return end_index(cloud, 4 + kind)
    lesson_of = lambda ph: lesson_index(0, ("head", "headrev", "end")[ph])      # (user) Cloud's lessons
    used = {c: sorted({o for ph in range(GR.PHASES) for o in raw_stroke(ph, c) +
                       [raw_stop(ph, kd, c) for kd in ((0, 1) if c else (0, 1, 2))] +
                       ([lesson_of(ph)] if c else [])}) for c in (False, True)}
    remap = {c: {o: i for i, o in enumerate(used[c])} for c in (False, True)}
    trim = lambda full, c: [full[o] for o in used[c]]
    n_used = len(used[False])
    cloud_anims = trim(cloud_anims, True)
    cl0 = loader.models[0]
    loader.models.append(ModelLoader.with_anims(ModelLoader.with_hrc(cl0, hb.CLOUD_BARE_HRC,
                                                                     ModelLoader.name(cl0)[:-5] + "_b.char"), cloud_anims))
    cfirst = len(ModelLoader.anims(loader.models[2])) - len(cloud_anims)
    gfirst = {}
    by_key = {g["key"]: g for g in MG.GIRLS}
    for key in GR.ORDER:
        if key in ("ruby", "skye"):
            (df, dm), hrc = (RUBY_DONOR, BARE_HRC) if key == "ruby" else (SKYE_DONOR, SKYE_BARE)
            anims = girl_anims + STILL
        else:
            df, dm, _ = by_key[key]["donor"]
            hrc, anims = by_key[key]["hrc"], _BUILT["cast"][key]
        assert len(anims) == len(girl_anims) + len(STILL), (key, len(anims))
        anims = trim(anims, False) + anims[len(girl_anims):]
        m = loader.add_from(ModelLoader(ctx.field(df).section("models")), dm)
        loader.models[m] = ModelLoader.with_anims(ModelLoader.with_hrc(loader.models[m], hrc,
                                                                       ModelLoader.name(loader.models[m])[:-5] + "_b.char"),
                                                  anims)
        assert len(anims) == n_used + len(STILL) and len(ModelLoader.anims(loader.models[m])) <= 47, (key, len(anims))
        gfirst[key] = len(ModelLoader.anims(loader.models[m])) - len(anims)
        if key == "skye":                                 # (her donor sits: DXID to stand in the staged scenes)
            loader.models[m] = ModelLoader.with_anims(loader.models[m], ["DXID.tor"])
            assert len(ModelLoader.anims(loader.models[m])) <= 47
    cm = loader.add_from(ModelLoader(ctx.field(CAMERA_DONOR[0]).section("models")), CAMERA_DONOR[1])
    film = ModelLoader.anims(loader.models[cm]).index(CAMERA_FILM)
    sprites = _BUILT["sprites"]
    for hrc in ("QGAA", "QCUA", "QHOA"):
        loader.models.append(ModelLoader.with_scale(sprites[hrc], sprite_scale))
    assert len(loader.models) == 13 and cm == 9, len(loader.models)      # (12: the hold's Square icon)

    ents = {}
    for name in ("cloudb", *GR.ORDER, "camera", "gauge", "cursor", "keys", "voice", "hush", "shout", "hush2", "hush3",
                 "icon", "sqkey"):
        ents[name] = len(sec.entity_names)
        sec.entity_names.append(name.encode("latin-1").ljust(8, b"\0"))
        sec.entry.append([None] * 32)
    CL, CH = 3, 4
    hide = lambda: [Op(b"\x7E\x01"), Op(b"\xC7\x01")]
    xyzi, d_ = hb._xyzi, (lambda d: Op(bytes([0xB3, 0, d])))
    by_q = lambda make: _chain(P, [make(q) for q in range(GR.PHASES * n_g)])
    loop_ = lambda i: [_animb(), Op(bytes([0xA2, i, 1])), Op(bytes([0xAE, i, 1]))]
    centre = _spot(mesh, (GR.HEAD_X[0] + GR.HEAD_X[1]) // 2, GR.HEAD_YS[1], 0, True)
    scripts = {}
    scripts[CL] = {0: [Op(bytes([0xA1, 0])), Op(bytes([0xA0, 0])), xyzi(*centre), hb._visi(0), asm.ret(), asm.ret()],
                   2: by_q(lambda q: [xyzi(*focus[q])]) + [asm.ret()], 3: [xyzi(*centre), asm.ret()]}
    scripts[CH] = {0: [Op(bytes([0xA1, 1])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()]}
    stroke = lambda first, ph, cloud: [first + remap[cloud][o] for o in raw_stroke(ph, cloud)]
    stop = lambda first, ph, kind, cloud: first + remap[cloud][raw_stop(ph, kind, cloud)]
    steps = lambda first, ph, cloud=False: _chain(STEP, [loop_(i) for i in stroke(first, ph, cloud)])
    scripts[ents["cloudb"]] = {
        0: [Op(bytes([0xA1, 2])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
        2: by_q(lambda q: [xyzi(*cloud_at[q]), d_(cdirs[q]), hb._visi(1)] +
                steps(cfirst, q // n_g, True)) + [asm.ret()],
        3: [xyzi(*centre), d_(facing_screen(cam, *centre[:3], (0, 1))), hb._visi(1)] + loop_(0) + [asm.ret()],
        4: _chain(PH, [loop_(stop(cfirst, ph, 0, True)) for ph in range(GR.PHASES)]) + [asm.ret()],
        5: _chain(PH, [loop_(stop(cfirst, ph, 1, True)) for ph in range(GR.PHASES)]) + [asm.ret()],
        7: _chain(PH, [lesson_slot(cfirst + remap[True][lesson_of(ph)], stop(cfirst, ph, 0, True))
                       for ph in range(GR.PHASES)]) + [asm.ret()]}
    for k, key in enumerate(GR.ORDER):
        first = gfirst[key]
        b_ = 2 * (k % 2)                                  # (girls alternate the two idle timings)
        still_lie, still_kneel = first + n_used + b_, first + n_used + b_ + 1

        def place(ph, k=k, first=first, still_lie=still_lie, still_kneel=still_kneel):
            q = ph * n_g + k
            idle = asm.nop()
            return [xyzi(*girl_at[q]), d_(gdirs[q]), hb._visi(1), asm.if_byte(E, "==", k, idle)] + \
                steps(first, ph) + [asm.ret(), idle] + \
                loop_(still_kneel if ph == 0 else still_lie) + [asm.ret()]
        idle4, idle5, idle6 = asm.nop(), asm.nop(), asm.nop()
        present = asm.nop()                               # (user) walked off (LEFT): stays hidden
        scripts[ents[key]] = {0: [Op(bytes([0xA1, 3 + k])), hb._visi(0)] + hide() + [asm.ret(), asm.ret()],
                              2: [asm.if_byte(LEFT, "bit_on", k, present), hb._visi(0), asm.ret(), present] +
                              _chain(PH, [place(ph) for ph in range(GR.PHASES)]) + [asm.ret()],
                              7: [hb._visi(0), asm.ret()],
                              4: [asm.if_byte(E, "==", k, idle4)] +
                              _chain(PH, [loop_(stop(first, ph, 0, False)) for ph in range(GR.PHASES)]) + [idle4, asm.ret()],
                              5: [asm.if_byte(E, "==", k, idle5)] +
                              _chain(PH, [loop_(stop(first, ph, 1, False)) for ph in range(GR.PHASES)]) +
                              [idle5, asm.ret()],
                              6: [hb._w(hold_try_delay()), asm.if_byte(E, "==", k, idle6)] +   # (user) her try: once, then the deepest
                              _chain(PH, [[_animb(), Op(bytes([0xA2, stop(first, ph, 1, False), 1])),
                                           Op(bytes([0xAE, stop(first, ph, 2, False), 1]))] for ph in range(GR.PHASES)]) +
                              [idle6, asm.ret()],
                              3: [xyzi(*girl_at[k]), d_(gdirs[k]), hb._visi(1)] + loop_(still_kneel) + [asm.ret()]}
    scripts[ents["camera"]] = {
        0: [Op(bytes([0xA1, 9]))] + hide() + [xyzi(*cam_at[0][:4]), d_(cam_at[0][4])] + loop_(film) + [asm.ret(), asm.ret()],
        2: by_q(lambda q: [xyzi(*cam_at[q][:4]), d_(cam_at[q][4])]) + [asm.ret()]}
    scripts[ents["gauge"]] = {0: [Op(bytes([0xA1, 10])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret(), asm.ret()],
                              2: by_q(lambda q: [xyzi(*gauge[q])]) + [hb._visi(1), asm.ret()]}
    scripts[ents["icon"]], scripts[ents["sqkey"]] = _hold_entities(hb, 12, sprite_dir, by_q(lambda q: [xyzi(*icon[q])]),
                                                                   cloud=ents["cloudb"])
    # (user, since: the group's script was at 62.7 of 64 KB) the cursor's spot computed, not a tree of
    # 21 XYZIs a position: unprojected at one depth its 21 spots lie on a line, spot b = first + b * step
    # (x16 fixed point), written into temp words and placed with XYZI's variable operands (the game's own
    # scripts do so: XYZI 66 66 after AXYZI)
    loop, idle, capped = asm.nop(), asm.nop(), asm.nop()
    CUR = [(6, 200), (6, 202), (6, 204)]
    cur = [loop, asm.if_byte(RUN, "==", 1, idle), asm.setword(BKT, POS), hb._arith(0x8C, BKT, 50),
           asm.if_word(BKT, ">", 20, capped), asm.setword(BKT, 20), capped]   # (if_word jumps when false: was "<=",
           # which set every bucket to 20: the cursor stuck at the right end, user)

    def cur_at(q):
        pts, ops_ = cursor[q], []
        for a, var in enumerate(CUR):
            step = round((pts[20][a] - pts[0][a]) * 16 / 20)
            assert all(abs(pts[0][a] + b * step / 16 - pts[b][a]) <= 2 for b in range(21)), ("cursor line", q, a)
            ops_ += [asm.setword(var, BKT), hb._arith(0x8A, var, abs(step)), hb._arith(0x8C, var, 16),
                     asm.setword(CUR_T, pts[0][a] & 0xFFFF), hb._arith(0x86 if step >= 0 else 0x88, CUR_T, var),   # (PLUS2 / MINUS2 wrap; 0x79 gave -32768)
                     asm.setword(var, CUR_T)]
        return ops_ + [Op(bytes([0xA5, 0x66, 0x60]) + struct.pack("<HHHH", CUR[0][1], CUR[1][1], CUR[2][1],
                                                                  pts[10][3]))]
    CUR_T = (6, 206)
    cur += by_q(cur_at) + [hb._visi(1), hb._w(1), asm.goto_back(loop)]
    cur += [idle, hb._visi(0), hb._w(1), asm.goto_back(loop)]
    scripts[ents["cursor"]] = {0: [Op(bytes([0xA1, 11])), hb._visi(0), d_(sprite_dir)] + hide() + [asm.ret()] + cur
                               + [asm.ret()]}
    wait = hb._w(1)
    back1, up = asm.goto_back(wait), asm.setbyte(HELD, 0)
    scripts[ents["keys"]] = {0: [asm.ret(), wait, Op(bytes([0x96, FR[0], FR[1]])),
                                 Op(bytes([0x30]) + struct.pack("<H", OK_KEY) + b"\x00", target=up),
                                 asm.if_byte(HELD, "==", 0, back1), asm.setbyte(HELD, 1),
                                 Op(bytes([0x96, PR[0], PR[1]])), back1,
                                 up, asm.goto_back(wait), asm.ret()]}
    # voice: the engaged girl (muffled) and a random other girl's comment, in turn
    texts = {}

    def line(who, text):
        t = "%s\n%s" % (GR.NAMES[who], text if text.startswith("(") or text.startswith("Mm") or
                        text.startswith("Hn") or text.startswith("Gk") else "“%s”" % text)
        if t not in texts:
            texts[t] = sec.add_string(_encode(t))
        return [Op(b"\x52\x01\x00\x01"), hb._window(t, 1, 8, LINE_Y), hb._req(ents["hush"], 2, wait=False)] + \
            ([hb._req(ents["icon"], 4, wait=False)] if _slaps(text) else []) + [asm.message(1, texts[t])]   # (user) slap prompt
    vl, vdone, other, picked = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    voice = [asm.ret(), vl, hb._w(SAY_EVERY), asm.if_byte(RUN, "==", 1, vdone),
             Op(bytes([0x95, K[0], K[1]])), Op(bytes([0x8D, K[0] << 4, K[1], 6])),
             Op(bytes([0x95, VV[0], VV[1]])), Op(bytes([0x8D, VV[0] << 4, VV[1], 2])),
             asm.if_byte(VV, "==", 0, other)]
    voice += _chain(E, [_chain(K, [line(key, GR.MUFFLED[key][j % 2]) for j in range(6)]) for key in GR.ORDER])   # (texts)
    voice += [asm.goto(vdone), other, Op(bytes([0x99, CC[0], CC[1]])), Op(bytes([0x8D, CC[0] << 4, CC[1], n_g]))]
    # never the engaged girl, nor (user) one who walked off (LEFT): the next one instead; none left: no line
    for r_ in range(n_g):
        rend = asm.nop()
        for k in range(n_g):
            nx, chk = asm.nop(), asm.nop()
            voice += [asm.if_byte(CC, "==", k, nx), asm.if_byte(E, "==", k, chk), asm.setbyte(CC, (k + 1) % n_g),
                      asm.goto(rend), chk, asm.if_byte(LEFT, "bit_on", k, nx), asm.setbyte(CC, (k + 1) % n_g),
                      asm.goto(rend), nx]
        voice += [rend]
    for k in range(n_g):
        nx, chk = asm.nop(), asm.nop()
        voice += [asm.if_byte(CC, "==", k, nx), asm.if_byte(E, "==", k, chk), asm.goto(vdone), chk,
                  asm.if_byte(LEFT, "bit_on", k, nx), asm.goto(vdone), nx]
    voice += _chain(CC, [_chain(PH, [_chain(K, [line(key, GR.COMMENTS[key][ph][j % len(GR.COMMENTS[key][ph])])
                                                for j in range(6)])
                                     for ph in range(GR.PHASES)]) for key in GR.ORDER])
    voice += [vdone, asm.goto_back(vl), asm.ret()]
    scripts[ents["voice"]] = {0: voice}
    scripts[ents["hush"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(SAY_FOR), Op(b"\x54\x01"), asm.ret()]}
    shout = "Cameraman\n“Five seconds left! Go all out, star!\n Give me a FINISHER!”"
    scripts[ents["shout"]] = {0: [asm.ret(), asm.ret()],
                              2: [Op(b"\x52\x02\x00\x01"), hb._window(shout, 2, 8, 56),
                                  hb._req(ents["hush2"], 2, wait=False), asm.message(2, sec.add_string(_encode(shout))),
                                  asm.ret()]}
    scripts[ents["hush2"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(FINISH_SAY_FOR), Op(b"\x54\x02"), asm.ret()]}
    scripts[ents["hush3"]] = {0: [asm.ret(), asm.ret()], 2: [hb._w(GR.PAUSE_FRAMES[1]), Op(b"\x54\x03"), asm.ret()],
                              3: [hb._w(GR.HOLD_SAY), Op(b"\x54\x03"), asm.ret()],
                              4: [hb._w(GR.MUFFLED_SAY), Op(b"\x54\x03"), asm.ret()]}

    # director
    lost, wrap, tick, hi_red = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    say = lambda t: hb._say(sec, "Cameraman\n" + t)
    girl_ents = [ents[key] for key in GR.ORDER]
    actors = [ents["cloudb"]] + girl_ents
    # (user) the girls' moments (`_movie_profiles`, `_movie_group` UNEASY / INTRO / SCENES / END):
    # force = the turn switch (her turn over now); walkout = everyone left; ending = wrap / finisher's end
    force, walkout, ending = asm.nop(), asm.nop(), asm.nop()
    to_force = lambda back: asm.goto_back(force) if back else asm.goto(force)

    say_once = lambda t: [hb._window(t, 0), asm.message(0, _text_id(sec, t))]   # (one text however often used)

    def leave(key, back=False, line=True):           # she walks off: hidden, her turns gone (LEFT, USED)
        k, stay = GR.ORDER.index(key), asm.nop()
        return lose_affection(key) + (say_once(GR.NAMES[key] + "\n" + PF.PROFILES[key]["leave"]) if line else []) + \
            [hb._req(ents[key], 7, wait=False), asm.biton(LEFT, k), asm.biton(USED, k),
             asm.if_byte(E, "==", k, stay), to_force(back), stay]

    def effects(eff, back):
        ops = _gil_ops(eff.get("gil", 0) * GR.RATE)
        if eff.get("rules"):
            ops += [asm.setbyte(RULES, 1)]
        for g in eff.get("annoy", []):
            ops += _annoy(GR.ORDER.index(g), leave(g, back))
        for g in eff.get("leave", []):
            ops += leave(g, back, line=False)
        return ops

    def choose(ask, choices, back, before=lambda j: []):   # an ASK to Cloud, each reply + its effects
        ops, first = hb._ask(sec, ask, [c[0] for c in choices])
        done = asm.nop()
        for j, (label, reply, eff) in enumerate(choices):
            nx = asm.nop()
            ops += [asm.if_byte(CHOICE, "==", first + j, nx)] + before(j) + \
                hb._say(sec, reply + _gil_note(eff.get("gil", 0) * GR.RATE)) + effects(eff, back) + [asm.goto(done), nx]
        return ops + [done]

    def uneasy(key):                                 # (user) she isn't comfortable: Check she's okay / Keep going
        if not PF.PROFILES[key].get("uneasy"):
            return None
        u, k = GR.UNEASY[key], GR.ORDER.index(key)
        check, push, go, out_ = asm.nop(), asm.nop(), asm.nop(), asm.nop()
        asks = []
        for t in u["ask"]:
            ops, first = hb._ask(sec, GR.NAMES[key] + "\n" + t, [GR.CHOICE_CHECK, GR.CHOICE_PUSH])
            asks.append(ops + [asm.if_byte(CHOICE, "==", first, push), asm.goto(check)])
        ops = _chain(PCNT, asks) + [check]
        if u["checked"] == "rules":
            ops += [asm.if_byte(RULES, "==", 1, out_)]
        ops += hb._say(sec, GR.NAMES[key] + "\n" + u["go"]) + \
            [asm.setbyte(PARM, 1), asm.setword(PT, FR), hb._arith(0x86, PT, GR.UNEASY_AGAIN), asm.goto(go)]
        if u["checked"] == "rules":
            ops += [out_] + hb._say(sec, GR.NAMES[key] + "\n" + u["out"]) + [asm.goto(force)]
        loss = GR.RATE * u["loss"]
        ops += [push] + hb._say(sec, GR.NAMES[key] + "\n" + u["pushed"] + _gil_note(-loss)) + _take_gil(loss) + \
            _annoy(k, leave(key)) + [asm.goto(force), go]
        return ops

    def uneasy_arm():                                # her stop early in each of her turns
        return _chain(E, [[asm.setbyte(PARM, 1), asm.setword(PT, FR), hb._arith(0x86, PT, GR.UNEASY_FIRST)]
                          if PF.PROFILES[key].get("uneasy") else [] for key in GR.ORDER])

    def scene(i, sc):                                # (user) everyone stops: an argument, Cloud's call
        # (user, since) staged with the models (`_movie_group.STAGING`): fade out, everyone to the scene's
        # spots and poses (slot 9), fade in, the talk to its `split`, the beat (slot 10), the rest, Cloud's
        # call, the reaction (slot 11 by RC), the reply, then back into the shoot (slot 2, as a turn switch)
        skip, st = asm.nop(), GR.STAGING[i]
        ops = [asm.if_byte(PH, "==", sc["part"], skip), asm.if_byte(TP, "==", sc.get("turn", GR.SCENE_AT_TURN), skip)] + \
            [asm.if_byte(LEFT, "bit_off", GR.ORDER.index(g), skip) for g in sc["girls"]]
        pages = sc["talk"].split("{NEW}")
        cast_ = [CL, ents["gauge"]] + actors
        ops += [asm.setbyte(SC, i), Op(FAST_OUT), Op(b"\x6C")] + [hb._req(e, 9, wait=False) for e in cast_] + \
            [hb._w(8), Op(FAST_IN), Op(b"\x6C")] + hb._say(sec, "{NEW}".join(pages[:st["split"]])) + \
            [hb._req(e, 10, wait=False) for e in actors] + [hb._w(15)] + \
            hb._say(sec, "{NEW}".join(pages[st["split"]:])) + \
            choose(sc["ask"], sc["choices"], back=True,
                   before=lambda j: [asm.setbyte(RC, j)] + [hb._req(e, 11, wait=False) for e in actors] + [hb._w(15)]) + \
            [Op(FAST_OUT), Op(b"\x6C")] + place_all() + [hb._w(4), Op(FAST_IN), Op(b"\x6C")]
        return ops + [skip]
    pause = _pause_ops(hb, sec, actors, ents["hush3"],
                       lambda block: _chain(E, [block(key) for key in GR.ORDER]), lambda no: [], ents["icon"],
                       lambda key: GR.RATE, slot_of=GR.ORDER.index, leave=leave, uneasy=uneasy, desperate=1,
                       speaker=(None, [("{CLOUD}", GR.HOLD_CLOUD[:1], GR.HOLD_STERN)]))   # (one hold line: texts)
    # (user: a long delay before the fade-in) all at once, not each waited on in turn (11 entities)
    place_all = lambda: [hb._req(e, 2, wait=False) for e in (CL, ents["cloudb"], *girl_ents, ents["camera"],
                                                             ents["gauge"], ents["icon"])] + [hb._w(6)]

    def pick():                                       # E = a girl not yet used this part, at random; P = q
        found, ops = asm.nop(), [Op(bytes([0x99, RND[0], RND[1]])), Op(bytes([0x8D, RND[0] << 4, RND[1], n_g]))]
        for step in range(2 * n_g):
            k = step % n_g
            nxt, taken = asm.nop(), asm.nop()
            ops += [asm.if_byte(RND, "==", k, nxt), asm.if_byte(USED, "bit_off", k, taken),
                    asm.setbyte(E, k), asm.biton(USED, k), asm.goto(found), taken,
                    asm.setbyte(RND, (k + 1) % n_g), nxt]
        ops += [found] + _chain(E, [[asm.setbyte(P, k)] for k in range(n_g)])
        return ops + _chain(PH, [[Op(bytes([0x85, P[0] << 4, P[1], ph * n_g]))] if ph else []
                                 for ph in range(GR.PHASES)])                  # P = phase * 6 + girl
    main = [hb._uc(1), hb._menu(1), asm.setbyte(RUN, 0), asm.setword(POS, 500), asm.setword(VEL, 1000),
            asm.setword(TOT, 0), asm.setword(PR, 0), asm.setword(FR, 0), asm.setword(RATE, 40), asm.setbyte(P, 0),
            asm.setbyte(STEP, 1), asm.setbyte(K, 0), asm.setword(NEXT, GR.TURN), asm.setbyte(FIN, 0),
            asm.setbyte(PH, 0), asm.setbyte(TN, 0), asm.setbyte(USED, 0), asm.setbyte(E, 255), asm.setbyte(VV, 0),
            asm.setbyte(LEFT, 0), asm.setbyte(RULES, 0), asm.setbyte(CTRL, 0), asm.setbyte(TP, 0)] + \
           [asm.setbyte(_ann(k), 0) for k in range(n_g)] + \
           [hb._req(e, 3) for e in (CL, ents["cloudb"], *girl_ents)] + [hb._w(20)]
    main += [Op(hb.FADE_IN), Op(b"\x6C")]
    main += hb._say(sec, GR.INTRO_TALK) + choose(GR.INTRO_ASK, GR.INTRO_CHOICES, back=False)   # (user) the intro talk
    for t_ in GR.INTRO:
        main += say(t_)
    main += pick() + [Op(bytes([0x95, TP[0], TP[1]])), Op(hb.FADE_OUT), Op(b"\x6C")] + place_all() + \
        [hb._w(10), Op(hb.FADE_IN), Op(b"\x6C")]
    main += [Op(bytes([0xF2, 0, 0, 0, 0x10, MUSIC]) + bytes(8)), hb._w(15)]
    main += say("“...And... ACTION!”")
    main += [asm.setword(FR, 0), asm.setword(PR, 0), asm.setword(NT, TICK)] + _pause_arm(hb, GR.TURN) + uneasy_arm() + \
        [asm.setbyte(RUN, 1)]
    wait1, go = hb._w(1), asm.nop()
    main += [tick, wait1, asm.if_word(FR, "<", NT, go), asm.goto_back(wait1), go, hb._arith(0x86, NT, TICK),
             asm.setword(T, PR), asm.setword(PR, 0), hb._arith(0x86, TOT, T),
             hb._arith(0x8A, VEL, 5), hb._arith(0x8C, VEL, 6),
             hb._arith(0x86, VEL, 1000 - 1000 * 5 // 6 - B - 500 // C),
             asm.setword(S, T), hb._arith(0x8A, S, A), hb._arith(0x86, VEL, S),
             asm.setword(S, POS), hb._arith(0x8C, S, C), hb._arith(0x86, VEL, S)]
    lo, hi = asm.nop(), asm.nop()
    main += [asm.if_word(VEL, "<", 1000 - VMAX, lo), asm.setword(VEL, 1000 - VMAX), lo,
             asm.if_word(VEL, ">", 1000 + VMAX, hi), asm.setword(VEL, 1000 + VMAX), hi,
             asm.setword(S, POS), hb._arith(0x86, S, VEL),
             asm.if_word(S, ">=", 1000 + DANGER, lost),
             asm.setword(POS, S), hb._arith(0x88, POS, 1000),
             asm.if_word(POS, "<=", 1000 - DANGER, hi_red)]
    no_call = asm.nop()
    # (user) the last turn: part three with every girl done or gone (girls may walk off)
    main += [asm.if_byte(PH, "==", GR.PHASES - 1, no_call), asm.if_byte(USED, "==", 63, no_call),
             asm.if_byte(FIN, "==", 0, no_call),
             asm.setword(FT, FR), hb._arith(0x86, FT, FINISH_FRAMES), asm.if_word(FT, ">=", NEXT, no_call),
             asm.setbyte(FIN, 1), hb._req(ents["shout"], 2, wait=False), no_call]
    done, same = asm.nop(), asm.nop()
    main += [hb._arith(0x8A, RATE, 3), hb._arith(0x8C, RATE, 4), asm.setword(S, T), hb._arith(0x8A, S, 16),
             hb._arith(0x86, RATE, S), asm.setbyte(NEW, 0)]
    for s_, th in enumerate(RATE_STEPS):
        main += [asm.if_word(RATE, ">=", th, done), asm.setbyte(NEW, s_ + 1)]
    main += [done, asm.if_byte(NEW, "!=", STEP, same), asm.setbyte(STEP, NEW),
             hb._req(ents["cloudb"], 2, wait=False)] + [hb._req(e, 2, wait=False) for e in girl_ents] + [same]
    main += pause                                    # (user) now and then she needs a moment
    # the next girl every TURN frames; after six, part two; after twelve, part three (end); after 18, the wrap
    stay, part2, part3 = asm.nop(), asm.nop(), asm.nop()
    # (user: a long switch cut into the next girl's turn) her turn counts from the fade-in
    # (user, since) a part ends when every girl has had her turn or walked off (USED, which LEFT joins);
    # everyone gone = walkout; the last part's end = the wrap
    not_last, same_part = asm.nop(), asm.nop()
    main += [asm.if_word(FR, ">=", NEXT, stay), force,
             asm.if_byte(LEFT, "!=", 63, walkout),
             asm.if_byte(PH, "==", GR.PHASES - 1, not_last), asm.if_byte(USED, "==", 63, not_last), asm.goto(wrap),
             not_last,
             asm.setbyte(RUN, 0), Op(b"\x54\x01"), Op(FAST_OUT), Op(b"\x6C"),
             Op(bytes([0x85, TN[0] << 4, TN[1], 1])),
             asm.if_byte(USED, "==", 63, same_part), Op(bytes([0x85, PH[0] << 4, PH[1], 1])),
             asm.setbyte(USED, LEFT), asm.setbyte(TP, 0), same_part] + pick() + \
            [Op(bytes([0x95, TP[0], TP[1]])), asm.setword(POS, 500), asm.setword(VEL, 1000)] + place_all() + \
            [hb._w(4), Op(FAST_IN), Op(b"\x6C")]
    for i, sc in enumerate(GR.SCENES):               # (user) the part's arguments, once each
        main += scene(i, sc)
    main += [asm.setword(PR, 0), asm.setword(NT, FR),
             hb._arith(0x86, NT, TICK), asm.setword(NEXT, FR), hb._arith(0x86, NEXT, GR.TURN)] + _pause_arm(hb, GR.TURN) + \
        uneasy_arm() + [asm.setbyte(RUN, 1), stay, asm.goto_back(tick)]
    rx, ry, rz, rt, rdir = back

    def out():
        stop = hb._w(30)
        return [hb._uc(0), hb._menu(0), asm.mapjump(ctx.maplist.index(WALL), rx, ry, rt, rdir), stop,
                asm.goto_back(stop), asm.ret()]
    gil = GR.RATE * FINISH_BONUS
    main += [hi_red, sound(RED_SOUND), asm.if_byte(FIN, "==", 1, lost), asm.setbyte(RUN, 0), Op(b"\x54\x01"),
             Op(b"\x54\x02"), Op(bytes([0xF2, 0, 0, 0, 0x10, FANFARE]) + bytes(8)), hb._w(45)]
    main += say("“WOW! What a FINISHER!\n That's going straight on the poster!”")
    main += [Op(bytes([0x39, 0x00]) + struct.pack("<I", gil)), sound(0x168)]
    main += say("“Here's a bonus, on the spot:\n {:,} gil. You earned it, star!”".format(gil))
    main += hb._say(sec, GR.AFTERMATH) + [asm.goto(ending)]
    main += [lost, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“CUT! CUT! You lost it, man!\n ...Fine. We'll sell what we've got.”")
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [walkout, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)] + hb._say(sec, GR.WALKOUT)   # (user)
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    main += [wrap, asm.setbyte(RUN, 0), Op(b"\x54\x01"), hb._w(10)]
    main += say("“...That's a WRAP! Magnificent!”")
    # (user) the end conversation: everyone stayed = their banter and a bonus, else his remark
    someone, edone = asm.nop(), asm.nop()
    stayed = GR.RATE * GR.STAYED_BONUS
    main += [ending, asm.if_byte(LEFT, "==", 0, someone)] + hb._say(sec, GR.END_TALK) + _gil_ops(stayed) + \
        hb._say(sec, GR.END_STAYED.format(gil=stayed)) + [asm.goto(edone), someone] + hb._say(sec, GR.END_LEFT) + [edone]
    main += [asm.biton(*SPECIAL_ON)]             # (user) a full group shoot unlocks the special scenes (672)
    main += [asm.setword(MOVIE_PRESSES, TOT), asm.setword(MOVIE_AT, HB_MINUTES), asm.setbyte(MOVIE_STATE, 2),
             Op(hb.FADE_OUT), Op(b"\x6C")] + out()
    _stage(hb, dt, cam, mesh, scripts, ents, CL, gfirst, n_used, loader, n_g)
    black = Op(bytes.fromhex("6b00000000000104" "00"))
    scripts[0] = {0: [black, asm.ret()] + main}
    dt._blank(sec, scripts)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    assert len(sec.strings if hasattr(sec, "strings") else []) <= 255
    return len(texts)


def _wall_market(ctx, focus):
    hb = _hb()
    f = ctx.field(WALL)
    mesh = Walkmesh(f.section("walkmesh"))
    donor = lambda d: ModelLoader(ctx.field(d[0]).section("models")).models[d[1]]
    # (user) still here, the camera at his side: a one-frame copy of FDCB's first frame as his
    # default anim (a held CANM would end when he turns to talk); appended to his model's anims
    # once the entity is taken over (below)
    from ff7 import fieldanim as fa
    still = fa.Anim(ctx.char_file(CAMERA_IDLE.split(".")[0].lower() + ".a"))
    still.frames = still.frames[:1]
    ctx.char_file(CAMERA_STILL.split(".")[0].lower() + ".a", still.build())
    idle = len(ModelLoader.anims(donor(CAMERA_DONOR)))
    # (user: she sat) Skye's donor's default anim is a sitting pose: the dancer's stand (same skeleton)
    stand = len(ModelLoader.anims(donor(SKYE_DONOR)))
    from ff7.camera import facing_screen
    cam = Camera(f.sections[1])
    spots = {}
    for key, (x, y) in (("cam", CAMERA_AT), ("ruby", RUBY_AT)):
        t = mesh.find(x, y)
        assert t is not None, (key, x, y)
        spots[key] = (x, y, mesh.height(t, x, y), t)

    def hidden(girl, extra=()):
        """Shown once every girl's final scene was seen (HB_KID); "ruby": hidden once Skye is unlocked (she retired); "skye":
        shown only at rank 1 (mrkt2 has no room for the later co-stars: 16 models)."""
        shown, hide = asm.nop(), asm.nop()
        who = {"ruby": [asm.if_byte(MOVIE_GIRL, "bit_off", 0, hide)],
               "skye": [asm.if_byte(MOVIE_GIRL, "bit_on", 0, hide),
                        asm.if_byte(MOVIE_RANK[1][0], "bit_off", MOVIE_RANK[1][1], hide)]}[girl]
        return _unlocked_or(hide) + [asm.if_byte(tape_q, "==", qx.DONE, hide)] + who + list(extra) + [asm.goto(shown), hide, Op(b"\x7E\x01"), Op(b"\xC7\x01"),
                                                          hb._visi(0), shown]

    qx = _quests()
    tape_q, (tape_c, _) = qx.quest_state("film_tape"), qx.quest_counter("film_tape")
    first_q, (first_c, _) = qx.quest_state("film_first"), qx.quest_counter("film_first")

    def tape(sec, say, end):
        """(user) "Late Night Viewing", before anything else: he sells a video tape for 20 gil
        (the quest starts), asks after it until it is watched, then what you thought (done)."""
        ops, done, sold, watched = [], asm.nop(), asm.nop(), asm.nop()
        ops += [asm.if_byte(tape_q, "!=", qx.DONE, done), asm.if_byte(tape_q, "==", qx.NEW, sold)]
        ops += say("“Psst. Hey, pal. You look like a man of\n refined tastes. I've got a little something\n"
                   " you won't find on any store shelf.”")
        ask, first = hb._ask(sec, "Cameraman\n“One video tape, my own work. Twenty gil.\n"
                                  " Strictly for the... discerning viewer.”", ["I'll take it.", "No thanks."])
        no, short, ok = asm.nop(), asm.nop(), asm.nop()
        gl, gh = (6, 0xF8), (6, 0xFA)            # temp words for CHGLD (as 625 / 640)
        ops += ask + [asm.if_byte(CHOICE, "==", first, no),
                      Op(bytes([0x3B, 0x66, gl[1], gh[1]])),                    # CHGLD lo, hi
                      asm.if_word(gh, "==", 0, ok), asm.if_word(gl, ">=", TAPE_PRICE, short), ok,
                      Op(bytes([0x3A, 0x00]) + struct.pack("<I", TAPE_PRICE)),  # GOLDD
                      asm.biton(*TAPE_BIT), sound(0x168),
                      asm.setbyte(tape_q, qx.ACCEPTED), asm.setbyte(tape_c, 0)]
        ops += hb._say(sec, "Received “%s”!" % TAPE_NAME)
        ops += say("“Pleasure doing business. Now, you can't\n exactly play it on a train... The Item Store\n"
                   " in Wall Market has a terminal. Try that.”")
        ops += say("“Then come back and tell me what you\n thought. An artist values his critics.”")
        ops += [asm.goto(end), short] + say("“Twenty gil, pal. Come back when your\n pockets aren't so light.”")
        ops += [asm.goto(end), no] + say("“Suit yourself. You know where I am.”") + [asm.goto(end)]
        ops += [sold, asm.if_byte(tape_c, "<", 1, watched)]
        ops += say("“Watched it yet? The Item Store in Wall\n Market has a terminal that'll play it.\n"
                   " Don't let the shopkeeper see you.”") + [asm.goto(end)]
        ops += [watched] + say("“Well? You watched it, didn't you?\n I can see it in your eyes. What did\n you think?”")
        ask, first = hb._ask(sec, "Cameraman\n“Be honest. I can take it.”",
                             ["“A masterpiece.”", "“Those girls were... something.”", "“I could do better.”"])
        nxt1, nxt2, said = asm.nop(), asm.nop(), asm.nop()
        ops += ask + [asm.if_byte(CHOICE, "==", first, nxt1)]
        ops += say("“A masterpiece! Ha! I knew you had\n taste the moment I saw you.”") + [asm.goto(said), nxt1]
        ops += [asm.if_byte(CHOICE, "==", first + 1, nxt2)]
        ops += say("“Weren't they? Every one a natural.\n The camera loves them, and so do\n the customers.”") + [asm.goto(said), nxt2]
        ops += say("“Ha! Big talk! ...But you know, you've\n got the look. The build, the hair.\n Maybe you could, at that.”")
        ops += [said] + say("“Tell you what. I'm always looking for\n new talent. A man with a way with the\n"
                            " ladies, the kind every girl knows by name.”")
        ops += say("“Find me a man like that, or be one,\n and we'll make movies together.\n Here, for your trouble.”")
        ops += qx.reward_ops(sec, "film_tape") + [asm.setbyte(tape_q, qx.DONE), asm.goto(end), done]
        return ops

    def first_video(sec, say, end):
        """(user) "Lights, Camera...": the first shoot's quest, handed in on the next talk."""
        ops, no_ = [], asm.nop()
        ops += [asm.if_byte(first_q, "==", qx.ACCEPTED, no_), asm.if_byte(first_c, ">=", 1, no_)]
        ops += say("“Your first video, star! The whole crew's\n talking about it. Here's a little bonus,\n"
                   " on top of your cut.”")
        ops += qx.reward_ops(sec, "film_first") + [asm.setbyte(first_q, qx.DONE), asm.goto(end), no_]
        return ops

    booker_q, (booker_c, _) = qx.quest_state("film_booker"), qx.quest_counter("film_booker")

    def booking(sec, say, end):
        """(user) "Top of the Bill": once the group shoot is done and Cid is at affection 20, the Gold
        Saucer wants the troupe live; the Booker in Event Square (674) hands it in."""
        ops, not_yet, asked = [], asm.nop(), asm.nop()
        ops += [asm.if_byte(booker_q, "==", qx.NEW, asked)] + qx.gate_ops(qx._quest("film_booker"), not_yet)
        ops += say("“Star! Big news. Your little troupe has\n made waves, all the way to the Gold\n Saucer.”")
        ops += say("“Their Booker called me himself. They\n want the whole gang, live, on the\n Event Square stage. Even the pilot.”")
        ops += say("“Go see him in Event Square. This is\n the big time, star. Don't you dare\n be late.”")
        ops += [asm.setbyte(booker_q, qx.ACCEPTED), asm.setbyte(booker_c, 0), asm.goto(end), asked,
                asm.if_byte(booker_q, "==", qx.ACCEPTED, not_yet)]
        ops += say("“The Gold Saucer's waiting, star! The\n Booker's in Event Square.”")
        return ops + [not_yet]

    def talk(sec):
        say = lambda t: hb._say(sec, "Cameraman\n" + t)
        end, pitch, wait_ = asm.nop(), asm.nop(), asm.nop()
        ops = [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + first_video(sec, say, end) + booking(sec, say, end) + \
            [asm.if_byte(MOVIE_STATE, "!=", 0, pitch),
               asm.setword(EL, HB_MINUTES), hb._arith(0x88, EL, MOVIE_AT), asm.if_word(EL, ">=", PAY_DELAY, wait_)]
        # (user) Skye's videos pay double (MOVIE_GIRL bit 1: she was this shoot's co-star; it
        # stays set until the next shoot is accepted, after this payment)
        def pay(rate):                           # GIL = presses x rate, capped to a word
            capped = asm.nop()
            return [asm.if_word(GIL, ">", 65535 // rate, capped), asm.setword(GIL, 65535 // rate), capped,
                    hb._arith(0x8A, GIL, rate)]
        # (user, since) each co-star 10 gil a press more: Ruby 10, Skye 20, Elena .. Aerith 30 .. 60
        paid_ = asm.nop()
        ops += [asm.setword(GIL, MOVIE_PRESSES)]
        not_group = asm.nop()                    # (user) the group shoot first: bits 3 + 4 together
        ops += [asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[0], not_group),
                asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[1], not_group)] + pay(GR.RATE) + [asm.goto(paid_), not_group]
        for bit, rate in [(1, PAY_RATE * SKYE_PAY)] + [(g["bit"], g["rate"]) for g in MG.GIRLS]:
            other = asm.nop()
            ops += [asm.if_byte(MOVIE_GIRL, "bit_on", bit, other)] + pay(rate) + [asm.goto(paid_), other]
        ops += pay(PAY_RATE) + [paid_]
        # (user) a shoot she was in: 660's revelation can play on her next date at affection 20
        from _config import REVEAL, REVEAL_GIRLS
        for g in MG.GIRLS:
            k_, solo_ = REVEAL_GIRLS.index(g["name"]), asm.nop()
            ops += [asm.if_byte(MOVIE_GIRL, "bit_on", g["bit"], solo_), asm.biton(REVEAL, k_), solo_]
        grp_ = asm.nop()                         # the group shoot (bits 3 + 4): all four
        ops += [asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[0], grp_), asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[1], grp_)] + \
            [asm.biton(REVEAL, k_) for k_ in range(4)] + [grp_]
        ops += [Op(bytes([0x39, GIL[0] << 4]) + struct.pack("<I", GIL[1])), sound(0x168)]
        paid = say("“The film's flying off the shelves!\n Here's your cut, star: {VAR} gil.”")
        paid.insert(1, Op(bytes([0x42, GIL[0], 0, 0]) + struct.pack("<H", GIL[1])))
        ops += paid + [asm.setbyte(MOVIE_STATE, 0), asm.goto(end)]
        ops += [wait_] + say("“Still selling the footage. Come back\n a little later for your cut.”") + [asm.goto(end)]
        # (user) he stands here from the start; until every girl's final scene was seen (HB_KID) he's only
        # scouting for a man with a way with the ladies
        told, fresh, scout = asm.nop(), asm.nop(), asm.nop()
        ops += [pitch] + tape(sec, say, end) + _unlocked_or(scout)
        ops += [asm.if_byte(MOVIE_GIRL, "bit_on", 0, fresh), asm.if_byte(MOVIE_GIRL, "bit_off", 2, told)]
        for t_ in NEWS[1]:                       # (user) once (if the arrival didn't tell it)
            ops += say(t_)
        ops += [asm.biton(MOVIE_GIRL, 2), told, fresh]
        ops += say("“Well, well... I've heard rumours about\n a man who can handle sexy women.\n"
                   " That's you, isn't it?”")
        ask, first = hb._ask(sec, "Cameraman\n“I'm shooting a new movie and I need\n a star. Interested?”",
                             ["Lights, camera, action!", "Not now."])
        no = asm.nop()
        ops += ask + [asm.if_byte(CHOICE, "==", first, no), asm.bitoff(MOVIE_GIRL, 1)]
        ops += [asm.bitoff(MOVIE_GIRL, g["bit"]) for g in MG.GIRLS]
        new_ = asm.nop()                         # (user) "Lights, Camera..." starts with the first shoot
        ops += [asm.if_byte(first_q, "==", qx.NEW, new_), asm.setbyte(first_q, qx.ACCEPTED), asm.setbyte(first_c, 0), new_]
        # (user, since) the co-stars come one at a time, by the star rank: Ruby (0), Skye, Elena,
        # Scarlet, Tifa, Aerith; (user) every one unlocked so far stays on the list, newest first
        # (rank 0: Ruby, no list). (The old list's Skye test was inverted: every other pick shot
        # with Skye, user.)
        assert [g["key"] for g in MG.GIRLS] == ["elena", "scarlet", "tifa", "aerith"]
        cast_ = [("Ruby", None, None), ("Skye", 1, None)] + [(g["name"], g["bit"], g["key"]) for g in MG.GIRLS]
        # (user, since) a girl below affection 20 (one who walked off loses a point) is greyed out and
        # can't be picked; "Everyone" too until all four are back at 20 (Ruby / Skye have none). Every
        # name starts with {WHITE}; TXPOKE turns its colour byte to grey (FE D2) at runtime.
        not_ready = ["Cameraman\n“She won't work with you right now.\n Win her trust back first, star.”",
                     "Cameraman\n“Not everybody's on board with you\n right now. Patch things up first.”"]
        refuse_ops = lambda t: [hb._window(t, 0), asm.message(0, _text_id(sec, t))]
        affs = [aff_var(g["key"]) for g in MG.GIRLS]

        def menu(on):
            """Ops: the co-star ASK for `on` (name, bit, key | "group"), greyed names, re-asked on a
            greyed pick; ends with MOVIE_GIRL set."""
            top, picked = asm.nop(), asm.nop()
            names = ["{WHITE}" + n for n, _, _ in on]
            ask_r, first_r = hb._ask(sec, "Cameraman\n“Who's your co-star today?”", names)
            tid = ask_r[2].raw[3]                     # (ASK [0x48][bank][window][text]...: TXPOKE 0x1D, 620)
            body = _encode("Cameraman\n“Who's your co-star today?”" + "".join("\n{CHOICE}" + c for c in names))
            marks = [k for k in range(len(body) - 1) if body[k] == 0xFE and body[k + 1] == 0xD9]
            assert len(marks) == len(on), (marks, on)
            poke = lambda k, c: Op(bytes([0x1D, tid]) + struct.pack("<H", k + 1) + bytes([c]))
            ops_ = [top]
            for mk, (_, bit, key) in zip(marks, on):
                vs = affs if key == "group" else ([aff_var(key)] if key else [])
                if not vs:
                    continue
                grey, done_ = asm.nop(), asm.nop()
                ops_ += [asm.if_byte(v, ">=", 20, grey) for v in vs] + [poke(mk, 0xD9), asm.goto(done_),
                                                                         grey, poke(mk, 0xD2), done_]
            ops_ += list(ask_r)
            for k_, (_, bit, key) in enumerate(on):
                nxt = asm.nop()
                vs = affs if key == "group" else ([aff_var(key)] if key else [])
                ok = asm.nop()
                check = []
                if vs:
                    bad = asm.nop()
                    check = [asm.if_byte(v, ">=", 20, bad) for v in vs] + [asm.goto(ok), bad] + \
                        refuse_ops(not_ready[1 if key == "group" else 0]) + [asm.goto_back(top), ok]
                sets = [asm.biton(MOVIE_GIRL, b_) for b_ in GROUP_BITS] if key == "group" else \
                    ([asm.biton(MOVIE_GIRL, bit)] if bit is not None else [])
                ops_ += [asm.if_byte(CHOICE, "==", first_r + k_, nxt)] + check + sets + [asm.goto(picked), nxt]
            return ops_ + [picked]
        lists = {r: menu(cast_[:r + 1][::-1]) for r in range(1, len(cast_))}   # newest first
        # (user) rank 6 (Aerith's wrap): "Everyone" = the group shoot, first
        lists[6] = menu([("Everyone", None, "group")] + cast_[::-1])
        assert len(MOVIE_RANK) == 6
        ops += _by_rank(lists)
        # (user, since) for one co-star, always: "Normal scene." / "Special scene." (672, after a full group
        # shoot) / "Blast-off." (673, Cid's affection at max); a locked one reads "????" and asks again
        import _movie_special as SP_
        import _blast_data as BD_
        import _cid as CID_
        spec_no, spec_ask, top = asm.nop(), asm.nop(), asm.nop()
        ops += [asm.setbyte(SPEC, 0),
                asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[0], spec_ask),
                asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[1], spec_ask), asm.goto(spec_no), spec_ask, top]
        for s_on in (0, 1):
            for b_on in (0, 1):
                nx = asm.nop()
                ops += [asm.if_byte(SPECIAL_ON[0], "bit_on" if s_on else "bit_off", SPECIAL_ON[1], nx),
                        asm.if_byte(CID_.AFFECTION, ">=" if b_on else "<", BD_.UNLOCK, nx)]
                ask_s, first_s = hb._ask(sec, "Cameraman\n“The usual, or something special today?”",
                                         ["Normal scene.", "Special scene." if s_on else "????",
                                          "Blast-off." if b_on else "????"])
                n1, n2 = asm.nop(), asm.nop()
                ops += ask_s + [asm.if_byte(CHOICE, "==", first_s + 1, n1)] + \
                    ([asm.setbyte(SPEC, 1), asm.goto(spec_no)] if s_on else [asm.goto_back(top)]) + \
                    [n1, asm.if_byte(CHOICE, "==", first_s + 2, n2)] + \
                    ([asm.setbyte(SPEC, 2), asm.goto(spec_no)] if b_on else [asm.goto_back(top)]) + \
                    [n2, asm.goto(spec_no), nx]
        ops += [spec_no]
        ops += say("“That's my man! To the set!”")
        x, y, z, t = focus
        ops += [Op(hb.FADE_OUT), Op(b"\x6C"), asm.setbyte(MOVIE_STATE, 0)]
        not_spec = asm.nop()
        sx_, sy_, sz_, st_ = _spot(Walkmesh(ctx.field(SPECIAL_BASE).section("walkmesh")), *SPECIAL_ARRIVE, 0, True)
        not_blast = asm.nop()                    # (673) Blast-off: its one set, the co-star picked there
        bx_, by_, bz_, bt_ = _spot(Walkmesh(ctx.field(BD_.SET).section("walkmesh")), *BD_.ARRIVE)
        ops += [asm.if_byte(SPEC, "==", 2, not_blast), asm.biton(*BD_.BLAST_ON),
                asm.mapjump(ctx.maplist.index(BD_.SET), bx_, by_, bt_, 0xC0), asm.ret(), not_blast]
        ops += [asm.if_byte(SPEC, "==", 1, not_spec)]
        for key_, bit_ in [("skye", 1)] + [(g["key"], g["bit"]) for g in MG.GIRLS]:
            nxt = asm.nop()
            ops += [asm.if_byte(MOVIE_GIRL, "bit_on", bit_, nxt),
                    asm.mapjump(ctx.maplist.index(SP_.FIELDS[key_]), sx_, sy_, st_, 0xC0), asm.ret(), nxt]
        ops += [asm.mapjump(ctx.maplist.index(SP_.FIELDS["ruby"]), sx_, sy_, st_, 0xC0), asm.ret(), not_spec]
        solo = asm.nop()                         # (user) the group's set: bits 3 + 4 together
        ops += [asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[0], solo), asm.if_byte(MOVIE_GIRL, "bit_on", GROUP_BITS[1], solo),
                asm.mapjump(ctx.maplist.index(LZ.FIELD if LZ.ENABLED else GROUP_FIELD), x, y, t, 0), asm.ret(), solo]   # (678: loose)
        for g in MG.GIRLS:                       # her own set
            nxt = asm.nop()
            ops += [asm.if_byte(MOVIE_GIRL, "bit_on", g["bit"], nxt),
                    asm.mapjump(ctx.maplist.index(g["field"]), x, y, t, 0), asm.ret(), nxt]
        ops += [asm.mapjump(ctx.maplist.index(FIELD), x, y, t, 0), asm.ret()]
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
    # (user) after a wrap (state 3) the news of the new co-star too; state 4 (debug "Star rank +1"):
    # only the news, nothing owed
    skip, go, news_only, no_news, owed, fin = (asm.nop() for _ in range(6))
    news = {r: sum((hb._say(sec0, "Cameraman\n" + t_) for t_ in NEWS[r]), []) for r in NEWS}
    news[1] += [asm.biton(MOVIE_GIRL, 2)]        # (told: not again on the next talk)
    debrief = [asm.if_byte(MOVIE_STATE, "!=", 2, go), asm.if_byte(MOVIE_STATE, "!=", 3, go),
               asm.if_byte(MOVIE_STATE, "==", 4, skip), go, hb._uc(1), hb._menu(1),
               asm.if_byte(MOVIE_STATE, "!=", 4, news_only), hb._window(debrief_text), asm.message(0, tid)] + \
              qx.count_ops("film_first") + [
               news_only, asm.if_byte(MOVIE_STATE, "!=", 2, no_news)] + _by_rank(news) + \
              [no_news, asm.if_byte(MOVIE_STATE, "==", 4, owed), asm.setbyte(MOVIE_STATE, 0), asm.goto(fin),
               owed, asm.setbyte(MOVIE_STATE, 1), fin, hb._menu(0), hb._uc(0), skip]
    f.sections[0] = sec0.build()
    cdir = facing_screen(cam, *spots["cam"][:3], (0, 1))
    cm = reuse_npc(ctx, WALL, TAKEOVER["filmman"], CAMERA_DONOR, spots["cam"], cdir, talk,
                   init_extra=[Op(bytes([0xA2, idle, 1])), Op(bytes([0xAE, idle, 1]))], main=debrief)   # (user) always there

    def ruby_talk(sec):
        return [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + \
            hb._say(sec, "Ruby\n“So you're my co-star? Don't disappoint\n me, handsome.”") + [hb._uc(0), asm.ret()]
    reuse_npc(ctx, WALL, TAKEOVER["ruby"], RUBY_DONOR, spots["ruby"], facing_screen(cam, *spots["ruby"][:3], (0, 1)),
              ruby_talk, init_extra=hidden("ruby"))

    def skye_talk(sec):
        return [hb._uc(1), Op(b"\x35\x00\x08\x02"), hb._w(8)] + \
            hb._say(sec, "Skye\n“So you're the famous star? Mmm...\n I hope you can keep up with me.”") + \
            [hb._uc(0), asm.ret()]
    sy = reuse_npc(ctx, WALL, TAKEOVER["skye"], SKYE_DONOR, spots["ruby"], facing_screen(cam, *spots["ruby"][:3], (0, 1)),
                   skye_talk, init_extra=hidden("skye", [Op(bytes([0xA2, stand, 1])), Op(bytes([0xAE, stand, 1]))]))   # (user) Ruby's place once she has retired
    loader = ModelLoader(f.section("models"))   # the new anims on the taken-over model entries
    loader.models[cm] = ModelLoader.with_anims(loader.models[cm], [CAMERA_STILL])
    loader.models[sy] = ModelLoader.with_anims(loader.models[sy], ["DXID.tor"])
    assert ModelLoader.anims(loader.models[cm]).index(CAMERA_STILL) == idle
    assert ModelLoader.anims(loader.models[sy]).index("DXID.tor") == stand
    f.set_section("models", loader.build())
    assert len(loader.models) <= 16, len(loader.models)
    # where the shoot sends you back: beside him, facing him
    x, y, z, t = spots["cam"]
    bx, by, bz, bt = beside(ctx, WALL, x, y, t, 40)
    bx, by, bz, bt = screen_step(ctx, WALL, bx, by, (0, 1), BACK_DOWN)     # (user: stuck there) 4 paces down
    return bx, by, bz, bt, _dates()._dir_to(x - bx, y - by)


# (user) what you watch on the tape: "some text describes what you watch in implicit detail"
TAPE_SCENE = [
    "(The screen flickers. A title card in pink\n letters: “HONEY BEE NIGHTS, Vol. 1”.)",
    "(A redhead in a black jacket sits on the end\n of a bed, smiling at the camera. She slips\n the jacket off one shoulder, slowly.)",
    "(A young man walks in. She pulls him down by\n his tie. The jacket hits the floor, then\n everything else does.)",
    "(The camera lingers. Bare skin, tangled\n sheets, her hands gripping the headboard.\n The bed creaks in time with her gasps.)",
    "(She ends up on top, head thrown back,\n hair everywhere. The shaky camera can\n barely keep up with her.)",
    "(Fade to black. Then, in wobbly letters:\n “A film by the Cameraman. Cast wanted.”)",
]


def _terminal(ctx):
    """(user) The Item Store terminal (mkt_ia line00 script 4, OK at the console): where the gun
    fired, the tape plays: with the Video Tape held, "Insert the tape." shows `TAPE_SCENE` and
    counts "Late Night Viewing"; without it, a line about the slot. The gun is gone."""
    hb, qx = _hb(), _quests()
    k2 = ctx.kernel2()
    from ff7.text import decode
    assert decode(k2.get(15, TAPE_ITEM)) == "" and decode(k2.get(7, TAPE_ITEM)) == "", TAPE_ITEM    # unused
    k2.set(15, TAPE_ITEM, _encode(TAPE_NAME))
    k2.set(7, TAPE_ITEM, _encode(TAPE_DESC))
    f = ctx.field(TERMINAL)
    sec = Script.parse(f.sections[0])
    ent = sec.entity_index("line00")
    ops = sec.script_ops(ent, 4)
    menu = next(o for o in ops if o.raw == b"\x4A\x01")                  # MENU2 01 (UC 01 before it)
    i = ops.index(menu)
    back = next(o for o in ops[i:] if o.raw == b"\x33\x00")               # UC 00 (MENU2 00, RET)
    guns = [o for o in ops[i:ops.index(back)] if o.op == 0x03 and o.raw[1] == 0x04]
    assert len(guns) >= 2, [o.raw.hex() for o in guns]                   # REQEW event (gun / Cid)
    none, out = asm.nop(), asm.nop()
    new = [asm.if_byte(TAPE_BIT[0], "bit_on", TAPE_BIT[1], none)]
    ask, first = hb._ask(sec, "(A video terminal. There's a slot for a\n tape below the screen.)",
                         ["Insert the tape.", "Leave it."])
    new += ask + [asm.if_byte(CHOICE, "==", first, out)]
    for t_ in TAPE_SCENE:
        new += hb._say(sec, t_)
    new += qx.count_ops("film_tape")
    new += hb._say(sec, "{CLOUD}\n“...”") + [asm.goto(back)]
    new += [none] + hb._say(sec, "(A video terminal. There's a slot for a\n tape below the screen.)") + [out, asm.goto(back)]
    sec.insert_before(ops[i + 1], new)
    key = ops[0]                                 # IFKEYON's jump is 1 byte: it hops via a goto now
    assert key.op == 0x31, key
    hop, cont = asm.goto(key.target), asm.nop()
    sec.insert_before(ops[1], [asm.goto(cont), hop, cont], retarget=False)
    key.target = hop
    f.sections[0] = sec.build()


def apply(ctx):
    _terminal(ctx)
    _bare_ruby(ctx)
    _bare_skye(ctx)
    focus = _spot(Walkmesh(ctx.field(BASE).section("walkmesh")), *POSITIONS[0]["girl"][1][:2], 0, True)
    for g in MG.GIRLS:                           # (their sets are new fields: the maplist names first)
        assert g["field"] in ctx.maplist, g["field"]
    back = _wall_market(ctx, focus)
    ctx.movie_back = back                        # (672's special sets send you back here too)
    _shoot(ctx, back)
    for g in MG.GIRLS:                           # (user) four more co-stars, each on her own set
        _shoot(ctx, back, g)
    _group(ctx, back)                            # (user) all six on one set, after Aerith

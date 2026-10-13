"""Honey Bee Girl recruitment.

- The Honey Bee Inn's manager (onna_4, the lobby) offers Cloud a job: find
  girls for the Inn (HB_JOB). After that he lists the girls you've hired, best
  first (stars, then the order in _honey_bee_data.GIRLS): pick one to visit.
- 20 girls stand around the world (_honey_bee_data.py). Before the job they
  only say a line. With the job, talking to one starts her pitch, then her
  questions (as many as her stars), all asked whatever you answer; at the end
  every answer right = hired (HB_HIRED bit), any wrong = she says so, talk again later.
- Earnings: the manager pays HB_RATE gil per star of every hired girl per
  minute of play since the last collection (at most HB_CAP minutes). The
  exe's play clock keeps the minutes in HB_MINUTES (quest_menu.asm q_clock).
- A visit jumps to the "&" room (onna_52) with HB_VISIT = girl + 1. There the
  room's own scene (produce main) and its exit line are off, and a new
  director entity plays her scene: the Honey Bee dancer (girl2, with all 22
  Honey Bee dancer animations of the game added to her model) and Cloud act
  out beats (entity scripts added in their free slots), then the screen fades
  and "You spent the rest of the night together and had a good time..." and
  you're back in the lobby, mid-room near the entrance (BACK_AT).
- Scarlet waits in the Shinra 66F Conference Room (blin66_6, the disc 2
  meeting room): 66F's bottom door (blin66_1 gateway 2, to the disc 1
  meeting room blin66_2) leads there instead (same room layout, same
  arrival); the room's own Scarlet, Heidegger and 'leave' entities
  (unplaced but visible at its pinned moment 998) are hidden, and the
  director no longer hides Cloud (REQ cloud script 3 = VISI 00).
"""
import struct

from _config import HB_AFFECTION, HB_CAP, HB_KID, HB_HIRED, HB_JOB, HB_LAST, HB_MINUTES, HB_RATE, HB_VISIT
from _honey_bee_data import GIRLS, LOUNGE
import _honey_bee_gifts as gifts
from _honey_bee_scenes_more import CLOSE, CLOSE_FINAL, DEVOTED, DEVOTED_FINAL
from _recruit import SOUND_RECRUIT, sound
from _travel import CHOICE, add_npc, beside, copy_model, reuse_npc

from ff7 import asm, triggers
from ff7.models import ModelLoader
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

LOBBY, ROOM = "onna_4", "onna_52"
# Affection tiers: the closer scenes play in copies of the "&" room made
# before any visit edits (unused maplist names; each copy has the room's whole
# text table for its 20 scenes). (field, first affection, scenes, last line)
CLOSE_ROOM, DEVOTED_ROOM = "onna_3", "onna_6"
BASIC_ROOM = "convil_3"     # the basic scenes too (unused maplist name, no exe special case): the "&"
                            # room itself is only the lounges now, its texts free for the gift menus
MANAGER_MODEL = ("colne_3", 4)               # market_youjin_r: Scotch (Corneo's man, colne_3 SOTCH)
# a Honey Bee girl either side of him (screen x = field x * 0.46 here)
ESCORTS = [("hbbee_l", (44, -48), "Honey Bee\n“Ooh, a new face! The boss says\n you've got an eye for talent.”"),
           ("hbbee_r", (164, -48), "Honey Bee\n“Bring us some cute new co-workers,\n okay? We'll be SO nice to them.”")]
BACK_AT = (0, -250)                          # after a visit: mid-lobby, near the entrance (screen 0, 116)
MANAGER_AT, MANAGER_DIR = (104, -48), 0
ROOM_ARRIVE = (263, 163, 5, 220)             # onna_4's own jump into the "&" room; Cloud then walks to
                                             # the middle (STAGE) before the girl comes in
WRONG = (5, 246)                             # temp: a question was answered wrong (girl fields)
TOTAL, ELAPSED, EARN = (6, 246), (6, 248), (6, 250)   # temp words: stars, minutes, gil
FINAL = "You spent the rest of the night together\nand had a good time..."
OFFER = "{CLOUD}\n“There's a job going at the Honey Bee Inn.\n Interested?”"

# onna_52 spots (x, y): from the room's own scene
# Spots, by screen x (this camera's y projection is useless): the room spans
# screen x -300..270; the action is kept in the middle. MOVE walks straight
# (no pathfinding): every leg below is checked to stay on the floor (the door
# needs the INSIDE waypoint; Aerith's lap straight to the door got stuck).
DOOR, INSIDE = (347, 230), (263, 163)
STAGE = (0, 150)                             # Cloud (screen x 0)
MID, NEAR, FAR = (90, 180), (50, 165), (-150, 200)
PACE = 20                                    # frames after each action
GIRL, CLOUD = "girl2", "cloud"
WALK = 0x0400                                # 0x0800 ran (MOVE runs above ~0x600)
DOOR_OPEN, DOOR_CLOSE = 0x7A, 0x11D
CORRIDOR, CONFERENCE = "blin66_1", "blin66_6"
# Lounge rooms: the four side doors of the lobby open freely: the two left
# ones into onna_52 (as in the original), the two right ones into FLIPPED, a
# new field (the unused maplist name onna_1) = onna_52 mirrored left-right
# (background tiles + texture areas, walkmesh, camera, scroll range, exit
# line). HB_VISIT = LOUNGE_ROOM + room. 5 girls per room (room r: girls
# 5(r-1) .. 5(r-1)+4), each shown only if hired, on 5 of the room's 10 spare
# entities (zax, muki1-9: the original scenes' extras).
LOUNGE_ROOM = 100
LOUNGE_EXTRAS = ["zax"] + ["muki%d" % k for k in range(1, 10)]
FLIPPED = "onna_1"
LOBBY_DOORS = {"border1": 1, "border2": 2, "border3": 3, "border4": 4}   # onna_4 door lines -> room
LOBBY_LOCKS = (0x13, 0x1C, 0x1E, 0x04)            # the side doors' triangles (locked until a room was chosen)
CHOOSERS = ("border5", "border6", "border7", "border8")   # the "take this room?" lines
ROOM_EXITS = {1: (-246, -135, 16, 96), 2: (-267, 153, 21, 32),       # onna_52 border1's own two arrivals
              3: (251, -140, 6, 160), 4: (255, 142, 1, 224)}         # onna_5's two exits to the lobby
ROOM_ARRIVAL = (215, 120, 6, 220)                 # onna_52 a little inside the door (rooms 3/4: mirrored),
                                                  # clear of EXIT_LINE
EXIT_LINE = ((290, 254, 25), (314, 116, 25))      # lounge exit: across the way in, before the door
                                                  # (the original line is past the door: Cloud ran through it)
GIRLS_PER_ROOM = 5
# (x, y, pose) in onna_52 (mirrored in FLIPPED): pose None = stand,
# ("hold", anim) a held pose, ("loop", anim) repeated
# The bed is a separate piece of walkmesh (z 76; the floor is z 25): its girls
# sit near the floor's edge (<= 31 units) and get a bigger talk radius.
# (spot, kind): "lie" holds the lying pose; "sit" / "stand" cycle random
# sitting / standing animations with random pauses between them.
# (spot, kind, DIR offset from facing down the screen; negated in the mirrored rooms)
LOUNGE_SPOTS = [
    ((102, -142), "lie", 0xC0),              # lying on the bed, head towards the door (3/4 body back from 170)
    ((55, -150), "sit", 0),                  # sitting on the bed's edge (lowered: SIT_DROP)
    ((-110, -180), "stand", 0x28),           # standing, away from the door
    ((-120, 180), "stand", 0),               # the dancer
    ((60, 230), "stand", -0x28),
]
SIT_DROP = 25                                # the sitting pose floated above the bed (z 76): drawn this much lower
LIE_TALK_RADIUS = 0x70                       # she is further onto the bed
LIE_ANIM = "DZBA.tor"
SIT_ANIMS = ["DXHE.tor", "DXIB.tor", "DXIC.tor"]                       # held (they stay seated)
STAND_ANIMS = ["DXJC.tor", "BAJE.tor", "BAJD.tor", "BAJF.tor", "BBAA.tor",   # played once, back to idle
               "DXJD.tor", "DIEF.chi", "BYAD.aki", "DXIF.tor"]
PAUSES = [45, 75, 105, 150]                  # frames between animations (random)
LOUNGE_RAND = (5, 200)                       # temp: girl slot k uses (5, 200 + k) (never shared: 8-op rule)
TALK_RADIUS, BED_TALK_RADIUS = 0x46, 0x60
CONFERENCE_DOOR = (2, "blin66_2")           # blin66_1 gateway slot, its original destination
CONFERENCE_COPIES = ["scarlet", "hyde", "leave"]   # visible (unplaced) at the pinned moment 998
HIDE = [b"\x7E\x01", b"\xC7\x01", b"\xA4\x00"]  # TLKON 01, SOLID 01, VISI 00          # the room's own entrance scene's door sounds
# girl2's model (market_dancer): its 5 animations, then every other Honey Bee
# dancer animation in the game (same skeleton BADD.HRC). Meanings (user):
# BAJC walk, AAGA run, BAJD spin + shake behind, BAJE shake behind, BAJF squat
# and twirl hips, BBAA bend down + poke with stinger, DXHF strut, DXIA silly
# run, DXJD present with arm, DIEF bow, DXJC sexy dance, DXIF check sides,
# BYAD point/poke, AVJE shocked; DXHE/DXIB/DXIC sitting, DZBA lying down.
DANCER_ANIMS = ["BAJB.tor", "BCCC.tor", "BCCD.tor", "AVJE.aki", "BYAD.aki"]
DANCER_EXTRA = ["DXHE.tor", "DXIB.tor", "DXIF.tor", "DXJA.tor", "DXJB.tor", "BAJF.tor", "BBAA.tor",
                "BAJD.tor", "BAJC.tor", "DXJC.tor", "DXJD.tor", "DXIC.tor", "DZBA.tor", "DIEF.chi",
                "DXIE.tor", "BAJE.tor", "AAGA.aki"]
CLOUD_ANIMS = {"stand": 0, "sit": 3, "shocked": 9, "hips": 15, "fall": 16, "lie": 20}
# Cloud's model in the room gets these (all Cloud animations, AAAA.HRC; meanings
# from the user). Avoid BICA (falls down) and EACF (arms up): overused.
CLOUD_EXTRA = {"shrug": "AQCB.chi", "take": "FYGC.chi", "nudge": "FYFC.chi", "nod": "AJDC.aki",
               "shakehead": "BUAA.chi", "laugh": "BTCD.aki", "impatient": "BDCC.aki",
               "lookaround": "AUEE.yos", "lookup": "AQFA.yos", "turnaway": "CAFB.aki",
               "formal": "EGGD.yos", "coy": "EGIC.yos", "point": "ALGB.yos", "cleanpants": "CCJF.tor",
               "stretch": "HOCF.tak", "warmup": "FJCB.yos", "leanin": "CDDE.tor", "cheer": "FDIF.hei",
               "drink": "FJCE.aki"}
GIFT_GIRL, GIFT_SEL = (5, 220), (5, 221)  # temp: lounge girl talked to, gift picked
DISPLAY = (6, 222)                           # temp word: affection shown with MPRA2
MOVES = {"enter", "approach", "mid", "far", "pace"}   # girl beats that walk (not from the bed)
# The bed part of a scene: ("bed", layout) fades out, places both on the bed
# (the raised walkmesh piece, z 76) and fades back in. Layout -> (girl beat,
# Cloud beat). Afterwards only in-place beats: girl sit1-3, Cloud CLOUD_BED.
BED_LAYOUTS = {"beside": ("lie", "bedbeside"), "sit": ("bedsit", "bedsitc"),       # the close scenes
               # the devoted scenes' positions (user's names and starting points)
               "mission": ("lie", "bedmission"),      # (Tifa's first; now Marisol, Bambi): she lies, Cloud on top of her (zcta)
               "cowgirl": ("rideon", "bedbackc"),     # Velvet's: Cloud on his back, she kneels astride
               "ontop": ("rideonr", "bedback"),       # as cowgirl, she faces the other way
               "dog": ("fourson", "bedknee"),         # Scarlet's: she's on all fours, Cloud knelt behind
               "head": ("kneelfloor", "standfloor"),  # user's second version: both on the floor left of the
                                                      # bed, Cloud standing facing left, she kneels facing him
               "edge": ("bendfloor", "standedgel"),    # user: she stands bent over the bed's left end facing
                                                      # right, Cloud standing behind her facing the bed
               "headrev": ("lierev", "standedge")}    # "head reverse" (user): she lies on her back along the
                                                      # bed, head at its left end; Cloud as in edge
# Beats allowed after each layout's fade (girl, Cloud); beside/sit: any sit / bed pose.
LAYOUT_BEATS = {"mission": (set(), {"thrust"}), "cowgirl": ({"ride"}, {"buck"}),
                "ontop": ({"ride"}, {"buck"}), "dog": ({"fours"}, {"pound"}),
                "head": (set(), {"stand"}), "edge": ({"bendf"}, {"standl", "standlf"}),
                "headrev": (set(), {"stand"})}
LAYOUT_ANIM = {"beside": "grea", "sit": "eiab", "mission": "thrust", "cowgirl": "buck", "ontop": "buck",
               "dog": "pound", "head": "stand", "edge": "standl", "headrev": "stand"}       # Cloud's pose each layout starts in
RIDE_RAISE = 18                              # cowgirl / ontop: she sits a head higher (user), then slightly more (+4)
# head (second version, user): on the floor left of the bed (z 25), Cloud facing screen-left,
# the girl HEAD_GAP further left facing him.
HEAD_STAND, HEAD_GAP = (-20, -180), 30
# edge: her feet just left of the bed's left end (screen x ~10), torso and arms out over it;
# Cloud EDGE_GAP further left, facing the bed (screen-right) like her
EDGE_GIRL, EDGE_GAP = (-12, -180), 26
# edge (user): she half a step (15) right, Cloud a step (30): the floor ends at x -5 there (the
# bed's base), so she moves 7 and Cloud keeps the gap those moves give (26 - 15 = 11)
EDGE_GIRL_MOVED, EDGE_CLOUD = (-5, -180), (-16, -180)
# head reverse: her XYZI point (by her feet; the head top is ~94 along her, 27 model units
# x ~3.4) so that her neck is at the bed's left edge (x ~24 at y -180), the head off it
HEADREV_GIRL = (88, -180)                     # (94 -> 88: the head now hangs straight down, clear of the edge)
HEADREV_CLOUD = (-8, -180)                    # a step right of edge's first spot (user)
HEAD_CLOUD, HEAD_CLOUD_DOWN = (115, -155), 0  # (first version) Cloud right and down a bit from CLOUD_SIT
HEAD_GIRL_FRONT, HEAD_GIRL_DROP = 27, 46      # she: at his x, this much nearer the camera (-y), 2/3 of
                                              # a body (~90) lower than the bed sitter (then a head higher: 46), turned round
MISSION_CLOUD, MISSION_RAISE = (126, -149), -4  # mission: Cloud 10 left / 30 further back of CLOUD_ONTOP,
                                               # 8 lower than ONTOP_RAISE (user, two rounds)
COWGIRL_CLOUD = (136, -161)                   # cowgirl: Cloud ~half a body width (18) further back than CLOUD_ONTOP (user)
DOG_CLOUD = (113, -142)                       # dog: Cloud a little nearer the camera and left of CLOUD_BESIDE, then ~18 more left, then 5 right / 8 back (user)
CLOUD_BESIDE = (136, -135)                   # beside the lying girl, half a body nearer the door (user)
CLOUD_ONTOP = (136, -179)                    # on top of her, half a body nearer the door (user)
ONTOP_RAISE = 4                              # Cloud on top of her: drawn this much higher (12 was too high)
# The scene girl's lying pose (user): on her back, facing up, hips raised LEG_RAISE and
# spread LEG_SPREAD, knees bent as far as it takes for the feet to be planted flat
# on the bed (with the thighs raised 45 that is ~90 at the knee), arms along her
# sides; hips where DZBA (the game's lying pose) has them. A new animation dzbt.a,
# built from her standing pose BAJB like the all-fours one.
LIE_ANIM_SCENE, LEG_RAISE, LEG_SPREAD = "DZBT.tor", 45, 45
# On all fours (user): from her standing pose BAJB, the upper body pitched 90 degrees
# forward (facing down), thighs hanging (hip 90), shins and feet folded back flat
# (knee 90), upper arms hanging (shoulder 90 forward), hands flat forward; each
# elbow bent just enough for its wrist to reach the floor, the knees on the floor
# (y = 0, y down; the root height is stored negated), head lifted FOURS_HEAD_LIFT.
FOURS_ANIM, FOURS_HEAD_LIFT = "DZBF.tor", 30
FOURS_FRAMES = 15                            # her rocking cycle: 0.5 s, starting rocked back (user)
# Kneeling astride, rocking (user): from standing, hips flexed RIDE_HIP and spread
# RIDE_SPREAD, knees bent RIDE_KNEE so the shins lie flat on the bed (feet flat behind),
# torso leaning RIDE_LEAN forward, arms RIDE_ARMS forward; then the knees open
# RIDE_ROCK towards straight and back (shins planted, so the hips rise and settle),
# eased, over RIDE_FRAMES frames (~2 s). Frame 0 is the rest pose.
RIDE_ANIM, RIDE_HIP, RIDE_KNEE, RIDE_SPREAD, RIDE_LEAN, RIDE_ARMS = "DZBR.tor", 70, 160, 30, 25, 25
# User: the humour lands better fast: 0.5 s (15 frames) per stroke, and more bounce
# (the knees open 24 instead of 8, so her hips rise ~3x as high). Dog is left as it was.
RIDE_ROCK, RIDE_FRAMES = 24, 15
# cowgirl's own copy (user): arms rotate down COWGIRL_ARMS_ROCK as she comes up and back as
# she comes down, head tilting COWGIRL_HEAD_ROCK down with them; ontop keeps DZBR
COWGIRL_ANIM, COWGIRL_ARMS_ROCK, COWGIRL_HEAD_ROCK = "DZBL.tor", 20, 15
COWGIRL_LEFT = 8                              # cowgirl: she sits this much left of CLOUD_ONTOP (user: slightly left)
# The other built poses: an eased POSE_ROCK degrees and back; the scene beats loop them
# with DFANM (her default animation). All fours keeps POSE_ROCK over FOURS_FRAMES.
POSE_ROCK, POSE_FRAMES = 8, 60
# On her back (mission): LIE_FRAMES per stroke, the knees fall open POSE_ROCK, and her
# whole body bounces LIE_BOUNCE up off the mattress and back (user: more bounce).
LIE_FRAMES, LIE_BOUNCE = 15, 1.2
# ... and (user) her head tilted LIE_HEAD forward (chin to chest), rocking LIE_HEAD_ROCK
# further forward as she comes down and back as she goes up; her arms angled LIE_ARMS
# out from her sides; her hips thrusting LIE_THRUST up on top of the bounce (shoulders
# and knees ride only the bounce: chest and thighs re-aimed each frame).
LIE_HEAD, LIE_HEAD_ROCK, LIE_ARMS, LIE_THRUST = 25, 12, 20, 1.0
# Kneeling, rocking (head, user): the ride kneel (RIDE_*) tipped KNEEL_TILT forward about
# the knee line, rocking KNEEL_ROCK further forward and back each KNEEL_FRAMES (0.5 s).
KNEEL_ANIM, KNEEL_TILT, KNEEL_ROCK, KNEEL_FRAMES = "DZBK.tor", 10, 10, 15
# edge (user): standing, legs slightly bent, bent 90 forward at the hips, arms straight
# out past her head level with the bed, rocking forward and back (0.5 s)
EDGE_ANIM, EDGE_KNEE, EDGE_BEND, EDGE_ARMS, EDGE_ROCK, EDGE_FRAMES = "DZBG.tor", 15, 90, 90, 5, 15
# then (user): head tipped back EDGE_HEAD_BACK (chin up) and turned EDGE_HEAD_TURN to her right,
# arms EDGE_ARMS_DOWN below level (since, user: head back more (12 -> 25); the hands stay put
# while she rocks, the elbows bending, instead of the arms dipping)
EDGE_HEAD_BACK, EDGE_HEAD_TURN, EDGE_ARMS_DOWN = 25, 15, 15
# after Tifa's "Faster!" (user: double speed): the same rock in 8 frames (~0.27 s)
EDGE_ANIM_FAST, EDGE_FRAMES_FAST = "DZBI.tor", 8
EDGE_FAST_BACK, EDGE_FAST_ARMS_DOWN = 20, 30   # the fast one (user): torso 20 more upright, arms further down
# head reverse (user): on her back as DZBT, head tipped back (further back as she comes
# down), arms up past her head at 160 from her sides
HEADREV_ANIM, HEADREV_ARMS, HEADREV_HEAD, HEADREV_ROCK = "DZBH.tor", 160, 40, 12
# since (user): the head hangs straight down (face upright) instead of the 40 tilt, the hips held
# HEADREV_LIFT up (her body slopes back to the shoulders) and still bouncing
HEADREV_LIFT = 2.0
SCENE_ANIMS = [LIE_ANIM_SCENE, FOURS_ANIM, RIDE_ANIM, KNEEL_ANIM, EDGE_ANIM, HEADREV_ANIM, EDGE_ANIM_FAST,
               COWGIRL_ANIM]   # our own animations on the scene girl
GIRL_SIT, CLOUD_SIT = (55, -150), (100, -140)   # side by side on the bed's edge, facing the camera
# Cloud's bed animations (names as the fields that use them spell them; meanings from the user).
# FTIB is only used on a Shinra soldier skeleton in the original game (same bone count).
CLOUD_BED = {"grea": "GREA.hei",   # lying on his back, looking right
             "greb": "GREB.hei",   # lying on his back, moving a little
             "grec": "GREC.hei",   # lying, then sits up
             "ftib": "FTIB.chi",   # lying on his back
             "avdd": "AVDD.yos",   # lying on his belly (on her)
             "avea": "AVEA.yos",   # on his belly, looks to the side
             "enje": "ENJE.yos",   # laid down, slowly sits up
             "enjf": "ENJF.yos",   # sitting, stretching his legs
             "hbgb": "HBGB.tak",   # knelt, thrusting (like CPR)
             "hbgc": "HBGC.tak",   # knelt, looks to the side
             "hbfe": "HBFE.tak",   # knelt, rubbing his face
             "eiab": "EIAB.chi",   # sitting comfortably
             "thrust": "ZCTA.tor",  # ours (_cloud_thrust): AVDD, legs straight back, slow hips
             "pound": "ZCTB.tor",   # ours (_cloud_pound): knelt (HBGB), quick deep hip thrust
             "spread": "ZCTC.tor",  # ours (_cloud_spread): sitting (EIAB), legs 30 degrees out
             "buck": "ZCTD.tor",    # ours (_cloud_buck): on his back (GREA), quick upward thrusts
             "stand": "ZCTE.tor",   # ours (_cloud_stand): standing (ACFE), knees bent, leaning, thrusting
             "standl": "ZCTF.tor",  # ours (edge): as stand, arms further forward, left leg raised
             "standlf": "ZCTG.tor",  # ours: standl at twice the speed
             "standk": "ZCTH.tor",   # ours (dates' koala hug): stand leaning back, arms bent in round her
             "standf": "ZCTI.tor",   # ours (dates' head scene): stand at twice the speed
             "standa": "ZCTJ.tor",   # ours (Aerith's date): stand, arms reaching down to her head
             "standaf": "ZCTK.tor"}  # ... twice the speed
# Cloud's own pose (user): AVDD (on his belly, propped on his forearms) with each
# knee straightened until the shin lies level with the ground, the feet pointed so
# they're level too, the knees brought within THRUST_KNEE_GAP of the midline (both
# at the same height); the hips rise THRUST_RISE and settle, eased, over
# THRUST_FRAMES frames (~3 s) with the shoulders and hands where they were.
CLOUD_THRUST, THRUST_KNEE_GAP, THRUST_RISE, THRUST_FRAMES = "ZCTA.tor", 0.7, 1.6, 15   # user: 0.5 s, more bounce
# Dog (user): from HBGB's first frame (knelt, sitting back, thighs ~54 degrees behind
# upright) the thighs swing forward POUND_SWING about the knee line (knees, shins and
# feet planted; the pelvis and the upper body ride along unturned: hips up and forward)
# and back, eased, in POUND_FRAMES frames (0.5 s), looped. The pivot is the line through
# both knees (one sits higher and further forward than the other).
CLOUD_POUND, POUND_SWING, POUND_FRAMES = "ZCTB.tor", 40, 15
# Head (user): EIAB (sitting comfortably, one knee up) with each whole leg swung out
# about the vertical at its hip until the thigh points SPREAD_ANGLE out from straight
# ahead (legs /\ from the front), every frame; held.
CLOUD_SPREAD, SPREAD_ANGLE = "ZCTC.tor", 30
# Cowgirl / ontop (user): GREA (on his back, looking right) with the head turned to face
# straight up and tilted BUCK_HEAD forward (chin to chest: looking at her), the arms
# raised BUCK_ARMS off the bed, and the hips thrusting up BUCK_RISE and back every
# BUCK_FRAMES (0.5 s), shoulders on the bed (chest and thighs re-aimed each frame).
CLOUD_BUCK, BUCK_HEAD, BUCK_ARMS, BUCK_RISE, BUCK_FRAMES = "ZCTD.tor", 30, 30, 1.5, 15
# Head, second version (user): standing (ACFE), knees bent STAND_KNEE, the torso tipped
# STAND_LEAN forward from the hips, the arms out STAND_ARMS forward; the hips thrust
# STAND_THRUST forward and back every STAND_FRAMES (0.5 s), knees and feet planted; the
# arms close STAND_ARMS_IN towards the middle as he thrusts and open again.
CLOUD_STAND, STAND_KNEE, STAND_LEAN, STAND_ARMS, STAND_ARMS_IN, STAND_THRUST, STAND_FRAMES = \
    "ZCTE.tor", 20, 25, 30, 10, 1.5, 15
# edge's Cloud (user): ZCTE with the arms twice as far forward and the left leg raised
# (hip 100, knee 10)
# head's Cloud since (user): right arm up about 70, left about 30, both bent in a bit at the elbow
STAND_ARMS_LR, STAND_ELBOW_IN = {"l": 30, "r": 70}, 20
CLOUD_EDGE, EDGE_CLOUD_ARMS, EDGE_CLOUD_HIP, EDGE_CLOUD_KNEE = "ZCTF.tor", 60, 100, 10
CLOUD_EDGE_FAST = "ZCTG.tor"                   # the same in EDGE_FRAMES_FAST frames (after "Faster!")
# the dates' koala hug (user): ZCTE leaning back KOALA_CLOUD_LEAN instead of forward, the arms
# KOALA_CLOUD_ARMS forward with the forearms turned KOALA_CLOUD_ELBOW in, round her
CLOUD_KOALA, KOALA_CLOUD_LEAN, KOALA_CLOUD_ARMS, KOALA_CLOUD_ELBOW = "ZCTH.tor", -15, 55, 75
KOALA_CLOUD_OUT = 10                           # (user) his arms turned out a little
# Aerith's head scene (user: his arms turned in to touch her head, kneeling ~9 in front):
# both arms 45 forward (down towards her head), turned 8 in, forearms 15 in
AERITH_CLOUD_ARMS, AERITH_CLOUD_IN, AERITH_CLOUD_ELBOW = 45, -8, 15
LOOPED_C = {"thrust", "pound", "buck", "stand", "standl", "standlf"}
# Devoted part two plays a fanfare from the fade to the bed (user): the victory fanfare,
# the chocobo fanfare for dog. AKAO cmd 0x10 = play by music table index (exe 0x9684C8:
# 5 FANFARE, 46 FAN2), as 250 does for md1stin.
PART2_MUSIC, PART2_MUSIC_DEFAULT = {"dog": 46}, 5
# Per girl (user), by music table index; names checked against the fields that play
# them: FIDDLE 8 (Chocobo Sage's house), PARADE 16 (Junon: Rufus' Welcoming Ceremony),
# CHASE 38 (HQ lobby escape: Crazy Motorcycle), DATE 49 (Gold Saucer gondola:
# Interrupted by Fireworks), GEKI 62 (the Gold Saucer stage: Debut); SID2 72 (Rocket
# Town houses, Highwind) taken as Steal the Tiny Bronco!.
PART2_MUSIC_GIRL = {"Candy": 8, "Scarlet": 16, "Mags": 72, "Elena": 38, "Aerith": 49, "Tifa": 62}
END_MUSIC = 57              # YADO, the inns' Good Night, Until Tomorrow!: every scene's closing text                       # Cloud bed beats that loop (DFANM) instead of holding
FADE_OUT, FADE_IN = bytes.fromhex("6b0000000000080200"), bytes.fromhex("6b00000000000801ff")   # as the game's own
ACT = (5, 250)                               # temp: which Cloud action the dispatcher plays
BED = (91, -144)                             # lying girl in the scenes: half a body further from the door than 136,
                                             # then a body width further back (the rolled pose sat off Cloud)
BED_DIR = 0xC0                               # lying girl in the scenes (user: 0x40 then turned 180, so
                                             # she lines up with Cloud's lying poses)
CLOUD_BED_DIR = 0x40                         # Cloud lying on his stomach on the bed (AVDD / AVEA)
CLOUD_BACK_DIR = 0xC0                        # ... on his back (user: those poses face the other way)
BACK_POSES, BELLY_POSES = {"grea", "greb", "grec", "ftib", "enje", "buck"}, {"avdd", "avea", "thrust"}
JUMP_SOUND = bytes.fromhex("f20000002840e9000000000000000000")[:14]


# ---- ops --------------------------------------------------------------------
def _w(n):
    return Op(b"\x24" + struct.pack("<H", n))


def _anim(i, hold=False):
    return Op(bytes([0xAF if hold else 0xA3, i, 1]))         # ANIM!1 / ANIME1


def _loop(i, wait=True):
    """Make animation i her default (DFANM: loops while she stands idle) and play it
    once (ANIME1, which returns to the default), so the loop starts whatever she held.
    wait=False uses ANIME2 (0xAE: same handler 0x61484A, but it doesn't wait for the
    animation's end): needed in an init. Tifa's and Velvet's devoted scenes start with
    her on the bed, set in girl2's init; ANIME1 there (waits a 60-frame cycle) hung the
    room on its black screen."""
    return [Op(bytes([0xA2, i, 1])), Op(bytes([0xA3 if wait else 0xAE, i, 1]))]


def _canm(i, a, b):
    return Op(bytes([0xB1, i, a, b, 1]))                    # CANM!1 frames a..b, hold


def _move(x, y):
    return Op(bytes([0xA8, 0]) + struct.pack("<hh", x, y))


def _msped(v):
    return Op(bytes([0xB2, 0]) + struct.pack("<H", v))


def _tura(ent):
    return Op(bytes([0xAB, ent, 0x0A, 2]))


def _turn(turns):
    return Op(bytes([0xB4, 0, 0, turns, 0x0A, 2]))           # TURNGEN


def _visi(on):
    return Op(bytes([0xA4, on]))


def _xyzi(x, y, z, tri):
    return Op(bytes([0xA5, 0, 0]) + struct.pack("<hhhH", x, y, z, tri))


def _uc(on):
    return Op(bytes([0x33, on]))


def _menu(off):
    return Op(bytes([0x4A, off]))                            # MENU2


def _req(ent, slot, wait=True):
    return Op(bytes([0x03 if wait else 0x02, ent, 0xC0 | slot]))


def _arith(op, dst, src):
    """PLUS2 0x86 / MINUS2 0x88 / MUL2 0x8A [banks][dst][u16 src]: dst word op= src
    (a (nibble, offset) var or a literal)."""
    sb, sv = (src if isinstance(src, tuple) else (0, src))
    return Op(bytes([op, dst[0] << 4 | sb, dst[1]]) + struct.pack("<H", sv))


def _collect(sec, end):
    """Income since the last collection: total stars of the hired girls x
    HB_RATE gil x minutes (at most HB_CAP), paid with GOLDU and shown with
    MPRA2 + {VAR}; HB_LAST = now."""
    none, idle = asm.nop(), asm.nop()
    ops = [asm.setword(TOTAL, 0)]
    for i, g in enumerate(GIRLS):
        hv, bit = _hired(i)
        skip = asm.nop()
        ops += [asm.if_byte(hv, "bit_on", bit, skip), _arith(0x86, TOTAL, g["stars"]), skip]
    ops += [asm.if_word(TOTAL, "!=", 0, none),
            asm.setword(ELAPSED, HB_MINUTES), _arith(0x88, ELAPSED, HB_LAST)]   # minutes since the last cut
    capped = asm.nop()
    ops += [asm.if_word(ELAPSED, ">", HB_CAP, capped), asm.setword(ELAPSED, HB_CAP), capped,
            asm.setword(EARN, ELAPSED), _arith(0x8A, EARN, TOTAL), _arith(0x8A, EARN, HB_RATE),
            asm.if_word(EARN, "!=", 0, idle),
            Op(bytes([0x39, EARN[0] << 4]) + struct.pack("<I", EARN[1])),           # GOLDU var
            asm.setword(HB_LAST, HB_MINUTES), sound(0x168)]                         # the item chime
    paid = _say(sec, "Manager\n“Your girls have been busy!\n Here's your cut: {VAR} gil.”")
    paid.insert(1, Op(bytes([0x42, EARN[0], 0, 0]) + struct.pack("<H", EARN[1])))  # MPRA2 after WINDOW: the number
    ops += paid + [asm.goto(end)]
    ops += [idle] + _say(sec, "Manager\n“Nothing yet, partner. Give the\n girls some time to earn.”") + [asm.goto(end)]
    ops += [none] + _say(sec, "Manager\n“No girls, no money. Go hire some!”") + [asm.goto(end)]
    return ops


def _hired(i):
    return (HB_HIRED[0], HB_HIRED[1] + i // 8), i % 8


def _window(text, win=0, x=8, y=8):
    pages = [p.lstrip("\n").split("\n") for p in text.split("{NEW}")]
    widest = max(len(l.replace("{CHOICE}", "     ").replace("{CLOUD}", "Cloud ")
                     .replace("{TIFA}", "Tifa").replace("{AERIS}", "Aerith"))
                 for p in pages for l in p)
    w = min(310, widest * 7 + 24)
    h = 16 * max(len(p) for p in pages) + 9
    return Op(bytes([0x50, win]) + struct.pack("<HHHH", x, y, w, h))


def _say(sec, text, win=0, x=8, y=8):
    return [_window(text, win, x, y), asm.message(win, sec.add_string(encode(text)))]


def _ask(sec, text, choices, win=0):
    """(ops, first): ASK with `choices`; CHOICE = first + index picked."""
    assert "{NEW}" not in text
    first = len(text.split("\n"))
    full = text + "".join("\n{CHOICE}" + c for c in choices)
    tid = sec.add_string(encode(full))
    return [_window(full, win), asm.setbyte(CHOICE, 0),
            asm.ask(win, tid, first, first + len(choices) - 1, CHOICE)], first


# ---- girls --------------------------------------------------------------
def _girl_talk(sec, i, g):
    end = _uc(0)
    stranger, idle, fail = asm.nop(), asm.nop(), asm.nop()
    hv, bit = _hired(i)
    ops = [_uc(1), Op(b"\x35\x00\x08\x02"), _w(8),                     # PTURA: face the player
           asm.if_byte(HB_JOB[0], "bit_on", HB_JOB[1], stranger),       # no job yet
           asm.if_byte(hv, "bit_off", bit, idle)]                       # already hired
    ops += _say(sec, g["intro"])
    offer, first = _ask(sec, OFFER, ["Offer her the job.", "Never mind."])
    ops += offer + [asm.if_byte(CHOICE, "==", first, end)]
    ops += _say(sec, g["reply"])
    assert len(g["questions"]) == g["stars"], g["name"]
    ops.append(asm.setbyte(WRONG, 0))
    for text, choices, right in g["questions"]:      # every question is asked; the verdict comes at the end
        q, first = _ask(sec, text, choices)
        ok = asm.nop()
        ops += q + [asm.if_byte(CHOICE, "!=", first + right, ok), asm.setbyte(WRONG, 1), ok]
    ops += [asm.if_byte(WRONG, "==", 0, fail),
            sound(SOUND_RECRUIT), asm.biton(hv, bit)] + _say(sec, g["hired"]) + [asm.goto(end)]
    ops += [fail] + _say(sec, g["fail"]) + [asm.goto(end)]
    ops += [stranger] + _say(sec, g["stranger"]) + [asm.goto(end)]
    ops += [idle] + _say(sec, g["idle"])
    return ops + [end, asm.ret()]


def _conference(ctx):
    f = ctx.field(CORRIDOR)
    trig = f.section("triggers")
    slot, old = CONFERENCE_DOOR
    gate = next(g for g in triggers.gateways(trig) if g["slot"] == slot)
    assert ctx.maplist[gate["field"]] == old, gate
    mesh = Walkmesh(ctx.field(CONFERENCE).section("walkmesh"))
    assert mesh.contains(gate["dest_triangle"], gate["dest_x"], gate["dest_y"])
    f.set_section("triggers", triggers.set_gateway_field(trig, slot, ctx.maplist.index(CONFERENCE)))
    sec = Script.parse(ctx.field(CONFERENCE).sections[0])
    for name in CONFERENCE_COPIES:
        ent = sec.entity_index(name)
        init = sec.script_ops(ent, 0)
        ret = next(o for o in init if o.op == 0x00)
        sec.insert_before(ret, [Op(b) for b in HIDE], retarget=True)
        sec.replace_script(ent, 1, [asm.ret()])
    # the director's main hides Cloud (REQ cloud script 3 = VISI 00): the
    # player was invisible in the room
    cloud = sec.entity_index("cloud")
    hide = [o for o in sec.script_ops(sec.entity_index("drctr"), 0)
            if o.op == 0x01 and bytes(o.raw[1:]) == bytes([cloud, 0xC3])]
    assert len(hide) == 1, hide
    sec.remove(hide[0])
    ctx.field(CONFERENCE).sections[0] = sec.build()


def _add_girls(ctx):
    for i, g in enumerate(GIRLS):
        f = g["field"]
        mesh = Walkmesh(ctx.field(f).section("walkmesh"))
        x, y = g["at"]
        tri = mesh.find(x, y)
        assert tri is not None, (f, x, y)
        pos = (x, y, mesh.height(tri, x, y) - g.get("drop", 0), tri)        # drop: drawn lower (user)
        if "reuse" in g:
            _reuse_entity(ctx, f, g["reuse"], i, g, pos)
            continue
        model = copy_model(ctx, f, *g["model"])
        add_npc(ctx, f, "hb%02d" % i, model, pos, g["dir"],
                lambda sec, i=i, g=g: _girl_talk(sec, i, g))


def _reuse_entity(ctx, field, name, i, g, pos):
    """A field already at 16 models: the girl takes over entity `name` (one
    the pinned moment hides); see _travel.reuse_npc."""
    reuse_npc(ctx, field, name, g["model"], pos, g["dir"], lambda sec: _girl_talk(sec, i, g))


# ---- the manager -----------------------------------------------------------
def _manager(ctx, back):
    room = ctx.maplist.index(ROOM)
    rx, ry, rtri, rdir = ROOM_ARRIVE
    assert Walkmesh(ctx.field(ROOM).section("walkmesh")).contains(rtri, rx, ry)

    def talk(sec):
        end, offer, visit, tips, cut = _uc(0), asm.nop(), asm.nop(), asm.nop(), asm.nop()
        ops = [_uc(1), Op(b"\x35\x00\x08\x02"), _w(8),
               asm.if_byte(HB_JOB[0], "bit_on", HB_JOB[1], offer)]
        menu, first = _ask(sec, "Manager\n“Back again, partner? What'll it be?”",
                           ["Visit one of the girls.", "Collect the girls' earnings.",
                            "Where do I find girls?", "Nothing."])
        ops += menu + [asm.if_byte(CHOICE, "!=", first, visit),
                       asm.if_byte(CHOICE, "!=", first + 1, cut),
                       asm.if_byte(CHOICE, "!=", first + 2, tips), asm.goto(end)]
        ops += [cut] + _collect(sec, end)
        # visit (user): one page per star rating, One Star Girls first. A girl not hired yet
        # is "????" and picking her just shows the page again. The menu text can't change
        # by itself, so each page has a text per combination of its girls hired (16).
        pages = [[i for i in range(len(GIRLS)) if GIRLS[i]["stars"] == n] for n in range(1, 6)]
        page_at = [asm.nop() for _ in pages]
        visit_at = {i: asm.nop() for i in range(len(GIRLS))}
        ops += [visit]
        for p, girls in enumerate(pages):
            nav = (["Next page."] if p < len(pages) - 1 else []) + (["Previous page."] if p else []) + ["Never mind."]
            title = "Manager\n“%s Star Girls”" % ("One", "Two", "Three", "Four", "Five")[p]
            pick = asm.nop()
            first = None

            def tree(k, mask):
                nonlocal first
                if k == len(girls):
                    rows = ["%s (%s)" % (GIRLS[i]["name"], GIRLS[i]["tag"]) if mask >> n & 1 else "????"
                            for n, i in enumerate(girls)]
                    ask, f = _ask(sec, title, rows + nav)
                    assert first in (None, f)
                    first = f
                    return ask + [asm.goto(pick)]
                hv, bit = _hired(girls[k])
                off = asm.nop()
                return [asm.if_byte(hv, "bit_on", bit, off)] + tree(k + 1, mask | 1 << k) + [off] + tree(k + 1, mask)
            ops += [page_at[p]] + tree(0, 0) + [pick]
            for n, i in enumerate(girls):            # her row: visit her if hired, else the page again
                hv, bit = _hired(i)
                other, unhired = asm.nop(), asm.nop()
                ops += [asm.if_byte(CHOICE, "==", first + n, other), asm.if_byte(hv, "bit_on", bit, unhired),
                        asm.goto(visit_at[i]), unhired, asm.goto_back(page_at[p]), other]
            row = first + len(girls)
            for label in nav:
                other = asm.nop()
                ops += [asm.if_byte(CHOICE, "==", row, other)]
                if label == "Next page.":
                    ops += [asm.goto(page_at[p + 1])]
                elif label == "Previous page.":
                    ops += [asm.goto_back(page_at[p - 1])]
                else:
                    ops += [asm.goto(end)]
                ops += [other]
                row += 1
            ops += [asm.goto(end)]
        for i in range(len(GIRLS)):
            ops += [visit_at[i], asm.setbyte(HB_VISIT, i + 1), _uc(0)]
            for name, at in ((DEVOTED_ROOM, gifts.DEVOTED), (CLOSE_ROOM, gifts.CLOSE)):   # by her affection
                lower = asm.nop()
                ops += [asm.if_byte(HB_AFFECTION[i], ">=", at, lower),
                        asm.mapjump(ctx.maplist.index(name), rx, ry, rtri, rdir), asm.ret(), lower]
            ops += [asm.mapjump(ctx.maplist.index(BASIC_ROOM), rx, ry, rtri, rdir), asm.ret()]
        ops += [tips] + _say(sec, "Manager\n“Word is there are fine ladies in\n Upper Midgar, the slums, Wall Market,\n"
                                  " Fort Condor, Junon, Nibelheim,\n the Gold Saucer…”{NEW}\n"
                                  "“…Icicle country, Costa del Sol,\n Wutai, Rocket Town, Gongaga,\n"
                                  " Cosmo Canyon and Mideel.\n The more stars, the pickier they are.”") + [asm.goto(end)]
        # first talk: the job offer
        ops += [offer] + _say(sec, "Manager\n“Hey, spiky! You look like a guy\n with an eye for talent.”")
        ask, first = _ask(sec, "Manager\n“Find me girls for the Inn? I'll let\n you visit any you hire. On the house.”",
                          ["You've got a deal.", "Not interested."])
        no = asm.nop()
        ops += ask + [asm.if_byte(CHOICE, "==", first, no), asm.biton(*HB_JOB),
                      asm.setword(HB_LAST, HB_MINUTES)]                         # earnings count from now
        ops += _say(sec, "Manager\n“Great! Talk to the ladies you meet.\n The classier the girl, the more\n questions she'll ask. Get 'em all right!”")
        ops += [asm.goto(end), no] + _say(sec, "Manager\n“Your loss, partner.”")
        return ops + [end, asm.ret()]

    model = copy_model(ctx, LOBBY, *MANAGER_MODEL)
    mesh = Walkmesh(ctx.field(LOBBY).section("walkmesh"))
    mx, my = MANAGER_AT
    tri = mesh.find(mx, my)
    assert tri is not None
    add_npc(ctx, LOBBY, "hbboss", model, (mx, my, mesh.height(tri, mx, my), tri), MANAGER_DIR, talk)
    for name, (ex, ey), line in ESCORTS:
        etri = mesh.find(ex, ey)
        assert etri is not None, (ex, ey)
        dancer = copy_model(ctx, LOBBY, LOBBY, 1)                  # the lobby's own Honey Bee girl
        add_npc(ctx, LOBBY, name, dancer, (ex, ey, mesh.height(etri, ex, ey), etri), MANAGER_DIR,
                lambda sec, line=line: [_uc(1), Op(b"\x35\x00\x08\x02"), _w(8)] + _say(sec, line)
                + [_uc(0), asm.ret()])


# ---- the room ----------------------------------------------------------------
def _free_slots(sec, ent, start):
    used = {o.raw[2] & 0x1F for o in sec.ops if o.op in (1, 2, 3) and o.raw[1] == ent}
    shared = sec.entry[ent][31]
    return [k for k in range(start, 32) if k not in used and sec.entry[ent][k] is shared]


def _guard(sec, ent, first, ops_after):
    """In VISIT mode, `first` (an op of entity `ent`'s script 0) is skipped:
    ops_after run instead."""
    guard = [asm.if_byte(HB_VISIT, "!=", 0, first)] + ops_after
    sec.insert_before(first, guard, retarget=False)
    for k, o in enumerate(sec.entry[ent]):
        if o is first and k == 0:
            sec.entry[ent][k] = guard[0]


def _room(ctx, back, field=ROOM, scenes=None, final=FINAL):
    """Visit mode for room copy `field`: girl i plays scenes[i] (default:
    her basic scene), then `final`."""
    scenes = scenes or [g["scene"] for g in GIRLS]
    f = ctx.field(field)
    mesh = Walkmesh(f.section("walkmesh"))

    def spot(p):
        t = mesh.find(*p)
        assert t is not None, p
        return p[0], p[1], mesh.height(t, *p), t

    loader = ModelLoader(f.section("models"))
    assert ModelLoader.anims(loader.models[1]) == DANCER_ANIMS, ModelLoader.anims(loader.models[1])
    loader.models[1] = ModelLoader.with_anims(loader.models[1], DANCER_EXTRA + SCENE_ANIMS)
    f.set_section("models", loader.build())
    da = {n: i for i, n in enumerate(DANCER_ANIMS + DANCER_EXTRA + SCENE_ANIMS)}
    cloud_anims = ModelLoader.anims(loader.models[0])
    assert [cloud_anims[i] for i in (3, 9, 15, 16, 20)] == ["AQAA.tor", "AVJE.aki", "AQAB.tor", "BICA.yos",
                                                             "EADD.tor"], cloud_anims
    # bed animations only where this room's scenes use them (layouts start with GREA / AVDD / EIAB)
    layout_anim = LAYOUT_ANIM
    bed_used = sorted({st[1] for sc in scenes for st in sc if st[0] == "c" and st[1] in CLOUD_BED}
                      | {layout_anim[st[1]] for sc in scenes for st in sc if st[0] == "bed"})
    extra = dict(CLOUD_EXTRA, **{n: CLOUD_BED[n] for n in bed_used})
    ca = {n: len(cloud_anims) + i for i, n in enumerate(extra)}
    loader.models[0] = ModelLoader.with_anims(loader.models[0], list(extra.values()))
    bare = None                                      # devoted room: part two's Cloud (same anims, so same indices)
    if field == DEVOTED_ROOM:
        bare = loader.add(ModelLoader.with_hrc(loader.models[0], CLOUD_BARE_HRC, "onna_52main_n_cloud_b.char"))
    f.set_section("models", loader.build())

    def on_floor(a, b):
        n = max(1, int(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 / 8))
        return all(mesh.find(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) is not None
                   for i in range(n + 1))
    stops = [MID, NEAR, FAR, INSIDE]
    legs = ([(ROOM_ARRIVE[:2], STAGE)]
            + [(a, b) for a in stops for b in stops if a != b])
    bad = [leg for leg in legs if not on_floor(*leg)]
    assert not bad, bad

    sec = Script.parse(f.sections[0])
    girl, cloud, door = sec.entity_index(GIRL), sec.entity_index(CLOUD), sec.entity_index("door")
    # room scene off in VISIT mode: produce's main, the exit line
    produce = sec.script_ops(sec.entity_index("produce"), 0)
    main = produce[produce.index(next(o for o in produce if o.op == 0)) + 1]
    # music: the room plays the Honey Bee Inn theme (block 0, id 68 as the lobby)
    # once (3,220) bit 0 is set, else the dream music (block 1); visits keep the theme
    assert sec.akao_ids()[0] == 68, sec.akao_ids()
    pick = next(o for o in produce if o.op == 0x14 and bytes(o.raw[1:5]) == bytes([0x30, 220, 0, 9]))
    menu = next(o for o in produce if o.op == 0x4A)
    sec.insert_before(pick, [asm.if_byte(HB_VISIT, "!=", 0, pick), Op(b"\xF0\x00"), asm.goto(menu)],
                      retarget=False)
    sec.insert_before(main, [asm.if_byte(HB_VISIT, "!=", 0, main), asm.ret()], retarget=False)
    border = sec.entity_index("border1")
    first = sec.entry[border][0]
    assert first.op == 0xD0, first.raw.hex()                       # LINE
    _guard(sec, border, first, [asm.if_byte(HB_VISIT, "<", LOUNGE_ROOM, first), asm.ret(), asm.ret()])

    d = lambda n, times=1: [_anim(da[n])] * times
    c = CLOUD_ANIMS
    gx = lambda p: _move(*p)
    girl_beats = {
        # the door opens (door script 1: BGOFF, as the room's own scene), she
        # appears just inside it and walks in, the door closes (script 2)
        "enter": [sound(DOOR_OPEN), _req(door, 1), _xyzi(*spot(INSIDE)), _visi(1), _msped(WALK),
                  gx(MID), _req(door, 2), sound(DOOR_CLOSE), _tura(cloud)],
        "approach": [_msped(WALK), gx(NEAR), _tura(cloud)],
        "mid": [_msped(WALK), gx(MID), _tura(cloud)],
        "far": [_msped(WALK), gx(FAR), _tura(cloud)],
        "pace": [_msped(WALK), gx(FAR), _tura(cloud), _w(20), gx(MID), _tura(cloud)],
        "spin": [_turn(2), _tura(cloud)],
        # animations as described by the user (DXHE/DXIB/DXIC sit, DZBA lies: unused)
        "sexy": d("DXJC.tor"),                    # sexy dance
        "shimmy": d("BAJE.tor", 2),               # shake behind
        "spinshake": d("BAJD.tor"),               # spin, then shake behind
        "twirl": d("BAJF.tor"),                   # squat and twirl hips
        "stinger": d("BBAA.tor"),                 # bend down and poke with the stinger
        "present": d("DXJD.tor"),                 # present something with an arm
        "bow": d("DIEF.chi"),
        "point": d("BYAD.aki"),                   # point / poke
        "checksides": d("DXIF.tor"),
        "shocked": d("AVJE.aki"),
    }
    one = lambda name: [_anim(ca[name])]
    cloud_beats = {
        # before the girl comes in: SOLID 01 (she walks through), into the room
        "into": [Op(b"\xC7\x01"), _msped(WALK), gx(STAGE), Op(bytes([0xB3, 0, 0x40]))],
        "sit": [_tura(girl), _canm(c["sit"], 0, 0x1D)],              # AQAA: kneels / sits down
        "stand": [_canm(c["sit"], 0x1D, 0x2C), _anim(c["stand"])],
        "shocked": [_anim(c["shocked"])],
        "hips": [_anim(c["hips"])],                                  # hands on hips
        "fallstay": [_anim(c["fall"], hold=True)],                   # BICA, staying down
        # the girl is already on the bed: stop level with her (the bed is in
        # the way of walking further down) and face her
        "intobed": [Op(b"\xC7\x01"), _msped(WALK), gx(STAGE), _tura(girl)],   # never towards the bed: he got stuck
    }
    cloud_beats.update({name: one(name) for name in CLOUD_EXTRA})
    # ---- the bed part ----
    from ff7.camera import Camera, facing_screen
    cam = Camera(f.sections[1])
    gs, cs = spot(GIRL_SIT), spot(CLOUD_SIT)
    gdir, cdir = facing_screen(cam, *gs[:3], (0, 1)), facing_screen(cam, *cs[:3], (0, 1))
    bx_, by_, bz_, bt_ = spot(CLOUD_ONTOP)
    rx_, ry_, rz_, rt_ = spot(CLOUD_ONTOP)
    hc = spot(HEAD_CLOUD)
    ks = spot(HEAD_STAND)
    kg = spot((HEAD_STAND[0] - HEAD_GAP, HEAD_STAND[1]))
    eg = spot(EDGE_GIRL_MOVED)
    hr = spot(HEADREV_GIRL)
    assert abs(hr[2] - 76) < 2, hr                                      # on the bed
    ec = spot(EDGE_CLOUD)
    hc_ = spot(HEADREV_CLOUD)                                           # head reverse's Cloud
    assert all(abs(p[2] - 25) < 2 for p in (ks, kg, eg, ec, hc_)), (ks, kg, eg, ec, hc_)   # on the floor, not the bed
    cg = spot((CLOUD_ONTOP[0] - COWGIRL_LEFT, CLOUD_ONTOP[1]))
    hold = lambda name: [_anim(ca[name], hold=True)]
    girl_beats.update({
        "lie": [_xyzi(*spot(BED)), Op(bytes([0xB3, 0, BED_DIR])), _visi(1)] + _loop(da[LIE_ANIM_SCENE]),
        "bedsit": [_xyzi(gs[0], gs[1], gs[2] - SIT_DROP, gs[3]), Op(bytes([0xB3, 0, gdir])), _visi(1),
                   _anim(da["DXHE.tor"], hold=True)],
        "fours": _loop(da[FOURS_ANIM]),                              # on all fours, where she lies (rocking)
        # astride Cloud (layout "ride"): on him at CLOUD_ONTOP, facing as he lies; "ride" rocks
        "rideon": [_xyzi(cg[0], cg[1], cg[2] + RIDE_RAISE, cg[3]), Op(bytes([0xB3, 0, CLOUD_BACK_DIR])), _visi(1),
                   ] + _loop(da[COWGIRL_ANIM]),                     # cowgirl: COWGIRL_LEFT left, own rock
        "rideonr": [_xyzi(rx_, ry_, rz_ + RIDE_RAISE, rt_), Op(bytes([0xB3, 0, (CLOUD_BACK_DIR + 128) % 256])),
                    _visi(1)] + _loop(da[RIDE_ANIM]),
        "fourson": [_xyzi(*spot(BED)), Op(bytes([0xB3, 0, BED_DIR])), _visi(1)] + _loop(da[FOURS_ANIM]),
        "kneelfloor": [_xyzi(*kg), Op(bytes([0xB3, 0, facing_screen(cam, *kg[:3], (1, 0))])), _visi(1)]
                      + _loop(da[KNEEL_ANIM]),
        "lierev": [_xyzi(*hr), Op(bytes([0xB3, 0, facing_screen(cam, *hr[:3], (1, 0))])), _visi(1)]
                  + _loop(da[HEADREV_ANIM]),                         # feet to the right: head to the left
        "bendf": _loop(da[EDGE_ANIM_FAST]),                         # edge, twice as fast (Tifa: "Faster!")
        "bendfloor": [_xyzi(*eg), Op(bytes([0xB3, 0, facing_screen(cam, *eg[:3], (1, 0))])), _visi(1)]
                     + _loop(da[EDGE_ANIM]),
        "ride": _loop(da[COWGIRL_ANIM]),                             # (Velvet, cowgirl: already rocking from "rideon")
        "sit1": [_anim(da["DXHE.tor"], hold=True)], "sit2": [_anim(da["DXIB.tor"], hold=True)],
        "sit3": [_anim(da["DXIC.tor"], hold=True)],
    })
    if "grea" in ca:
        cloud_beats["bedbeside"] = [_xyzi(*spot(CLOUD_BESIDE)), Op(bytes([0xB3, 0, CLOUD_BACK_DIR]))] + hold("grea")
    if "thrust" in ca:
        mx_, my_, mz_, mt_ = spot(MISSION_CLOUD)
        cloud_beats["bedmission"] = [_xyzi(mx_, my_, mz_ + MISSION_RAISE, mt_), Op(bytes([0xB3, 0, CLOUD_BED_DIR]))] + _loop(ca["thrust"])
    if "stand" in ca:                                # standing on the floor left of the bed (layout "head")
        cloud_beats["standfloor"] = [_xyzi(*ks), Op(bytes([0xB3, 0, facing_screen(cam, *ks[:3], (-1, 0))]))] \
            + _loop(ca["stand"])
        cloud_beats["standedge"] = [_xyzi(*hc_), Op(bytes([0xB3, 0, facing_screen(cam, *hc_[:3], (1, 0))]))] \
            + _loop(ca["stand"])                     # (layout "headrev"): at the bed's left end, facing it
    if "standl" in ca:                               # (layout "edge"): behind her, facing the bed, left leg up
        cloud_beats["standedgel"] = [_xyzi(*ec), Op(bytes([0xB3, 0, facing_screen(cam, *ec[:3], (1, 0))]))] \
            + _loop(ca["standl"])
    if "spread" in ca:                               # sitting on the edge, legs apart (first "head")
        cloud_beats["bedsith"] = [_xyzi(hc[0], hc[1], hc[2] - SIT_DROP - HEAD_CLOUD_DOWN, hc[3]),
                                  Op(bytes([0xB3, 0, cdir]))] + hold("spread")
    if "pound" in ca:                                # knelt behind her (layout "dog"), thrusting
        cloud_beats["bedknee"] = [_xyzi(*spot(DOG_CLOUD)), Op(bytes([0xB3, 0, CLOUD_BACK_DIR]))] + _loop(ca["pound"])
    if "buck" in ca:                                 # on his back under her (cowgirl / ontop), thrusting
        cloud_beats["bedback"] = [_xyzi(*spot(CLOUD_ONTOP)), Op(bytes([0xB3, 0, CLOUD_BACK_DIR]))] + _loop(ca["buck"])
        cloud_beats["bedbackc"] = [_xyzi(*spot(COWGIRL_CLOUD)), Op(bytes([0xB3, 0, CLOUD_BACK_DIR]))] + _loop(ca["buck"])
    if "eiab" in ca:
        cloud_beats["bedsitc"] = [_xyzi(cs[0], cs[1], cs[2] - SIT_DROP, cs[3]), Op(bytes([0xB3, 0, cdir]))] + hold("eiab")
    pose_dir = lambda name: ([Op(bytes([0xB3, 0, CLOUD_BACK_DIR]))] if name in BACK_POSES else
                             [Op(bytes([0xB3, 0, CLOUD_BED_DIR]))] if name in BELLY_POSES else [])   # knelt / sitting: as he is
    cloud_beats.update({name: pose_dir(name) + (_loop(ca[name]) if name in LOOPED_C else hold(name))
                        for name in bed_used})
    for i, sc in enumerate(scenes):              # after the fade to the bed: only in-place beats
        kinds = [st[0] for st in sc]
        if "bed" in kinds:
            after = sc[kinds.index("bed") + 1:]
            assert kinds.count("bed") == 1 and sc[kinds.index("bed")][1] in BED_LAYOUTS, (field, GIRLS[i]["name"])
            layout = sc[kinds.index("bed")][1]
            gok, cok = LAYOUT_BEATS.get(layout, ({"sit1", "sit2", "sit3"}, set(CLOUD_BED)))
            assert all(st[1] in gok for st in after if st[0] in ("g", "g&")), (field, GIRLS[i]["name"], layout)
            assert all(st[1] in cok for st in after if st[0] in ("c", "c&")), (field, GIRLS[i]["name"], layout)
    used = ({s[1] for sc in scenes for s in sc if s[0] in ("g", "g&")}
            | {BED_LAYOUTS[s[1]][0] for sc in scenes for s in sc if s[0] == "bed"})
    on_bed = [i for i, sc in enumerate(scenes) if sc[:1] == [("start", "bed")]]
    for i, sc in enumerate(scenes):
        assert sum(s[0] in ("G", "C") for s in sc) <= 7, (field, GIRLS[i]["name"])
        assert i not in on_bed or not {s[1] for s in sc if s[0] in ("g", "g&")} & MOVES, (field, GIRLS[i]["name"])
    used_c = ({s[1] for sc in scenes for s in sc if s[0] in ("c", "c&")} | {"into"}
              | {BED_LAYOUTS[s[1]][1] for sc in scenes for s in sc if s[0] == "bed"})
    used_c |= {"intobed"} if on_bed else set()
    if bare is not None:                             # hidden Cloud moved to the bare one's spot: the camera follows him
        for layout in {s[1] for sc in scenes for s in sc if s[0] == "bed"}:
            cb = BED_LAYOUTS[layout][1]
            at = next(o for o in cloud_beats[cb] if o.op == 0xA5)
            cloud_beats["hide_" + cb] = [_visi(0), Op(bytes(at.raw))]
            used_c |= {"hide_" + cb}
    assert used <= set(girl_beats) and used_c <= set(cloud_beats), (used - set(girl_beats), used_c - set(cloud_beats))
    slots = {}
    cloud_names = sorted(used_c)
    disp = []
    for k, name in enumerate(cloud_names, 1):
        nxt = asm.nop()
        disp += [asm.if_byte(ACT, "==", k, nxt)] + [Op(bytes(o.raw)) for o in cloud_beats[name]] + [asm.ret(), nxt]
    disp.append(asm.ret())
    cslot = _free_slots(sec, cloud, 24)[0]
    sec.ops.extend(disp)
    sec.entry[cloud][cslot] = disp[0]
    cloud2 = None
    if bare is not None:                             # the bare Cloud: hidden until the bed, same dispatcher
        sx, sy, sz, st = spot(STAGE)
        cloud2 = sec.add_entity("cloudb", {0: [Op(bytes([0xA1, bare])), _xyzi(sx, sy, sz, st), _visi(0),
                                               Op(b"\x7E\x01"), Op(b"\xC7\x01"), asm.ret(), asm.ret()]})
        disp2 = []
        for k, name in enumerate(cloud_names, 1):
            nxt = asm.nop()
            disp2 += ([asm.if_byte(ACT, "==", k, nxt), _visi(1)] + [Op(bytes(o.raw)) for o in cloud_beats[name]]
                      + [asm.ret(), nxt])
        disp2.append(asm.ret())
        sec.ops.extend(disp2)
        sec.entry[cloud2][2] = disp2[0]
    cloud_act = {name: k for k, name in enumerate(cloud_names, 1)}
    for ent, beats, start in ((girl, girl_beats, 8),):
        free = _free_slots(sec, ent, start)
        names = [n for n in beats if n in (used if ent == girl else used_c)]
        assert len(names) <= len(free), (ent, len(names), free)
        for name, k in zip(names, free):
            ops = [Op(bytes(o.raw)) for o in beats[name]] + [asm.ret()]
            sec.ops.extend(ops)
            sec.entry[ent][k] = ops[0]
            slots[(ent, name)] = k

    # girls starting on the bed: placed by girl2's init, before the room appears
    init = sec.script_ops(girl, 0)
    ret = next(o for o in init if o.op == 0x00)
    for i in on_bed:
        nxt = asm.nop()
        sec.insert_before(ret, [asm.if_byte(HB_VISIT, "==", i + 1, nxt), _xyzi(*spot(BED)),
                                Op(bytes([0xB3, 0, BED_DIR])), _visi(1),
                                *_loop(da[LIE_ANIM_SCENE], wait=False), nxt], retarget=False)

    # the director
    lobby = ctx.maplist.index(LOBBY)
    bx, by, bz, btri = back
    finale, stop = asm.nop(), asm.ret()
    ops = [asm.if_byte(HB_VISIT, "!=", 0, stop),                                  # no visit: nothing
           asm.if_byte(HB_VISIT, "<", LOUNGE_ROOM, stop), _uc(1), _menu(1)]       # (lounge: nothing)
    for i, g in enumerate(GIRLS):
        nxt = asm.nop()
        into = "intobed" if i in on_bed else "into"
        ops += [asm.if_byte(HB_VISIT, "==", i + 1, nxt),
                asm.setbyte(ACT, cloud_act[into]), _req(cloud, cslot), _w(15)]
        who = cloud                                   # part two: the bare Cloud (devoted room)
        for step in scenes[i]:
            kind = step[0]
            cs_ = cslot if who == cloud else 2
            if kind == "start":
                continue
            if kind in ("g", "g&"):
                ops += [_req(girl, slots[(girl, step[1])], wait=kind == "g"), _w(PACE)]
            elif kind == "c":                          # the dispatcher reads ACT: always waited for
                ops += [asm.setbyte(ACT, cloud_act[step[1]]), _req(who, cs_), _w(PACE)]
            elif kind == "G":
                ops += _say(sec, g["name"] + "\n" + step[1])
            elif kind == "C":
                ops += _say(sec, step[1], win=1, y=150)
            elif kind == "wait":
                ops.append(_w(step[1]))
            elif kind == "bed":                        # fade out, both onto the bed, fade in
                gb, cb = BED_LAYOUTS[step[1]]
                ops += [_w(20), Op(FADE_OUT), Op(b"\x6C"), _req(girl, slots[(girl, gb)])]
                if cloud2 is not None:
                    ops += [asm.setbyte(ACT, cloud_act["hide_" + cb]), _req(cloud, cslot)]
                    who = cloud2
                ops += [asm.setbyte(ACT, cloud_act[cb]), _req(who, cslot if who == cloud else 2), _w(20)]
                if field == DEVOTED_ROOM:
                    track = PART2_MUSIC_GIRL.get(g["name"], PART2_MUSIC.get(step[1], PART2_MUSIC_DEFAULT))
                    ops.append(Op(bytes([0xF2, 0, 0, 0, 0x10, track]) + bytes(8)))   # AKAO 10: play it
                ops += [Op(FADE_IN), Op(b"\x6C"), _w(PACE)]
            elif kind == "shake":
                ops += [Op(bytes.fromhex("5e00000200000804")), _w(20)]
            else:
                raise ValueError(step)
        if field == DEVOTED_ROOM:
            ops.append(asm.biton(*HB_KID[i]))          # 622: a kid appears next to her
        ops += [asm.goto(finale), nxt]
    ops += [asm.goto(stop), finale, _w(30),
            Op(bytes.fromhex("6b0000000000080200")), Op(b"\x6C"), _w(20),       # FADE out, FADEW
            Op(bytes([0xF2, 0, 0, 0, 0x10, END_MUSIC]) + bytes(8))]            # AKAO 10: the inn tune
    ops += _say(sec, final, x=24, y=96)
    ops += [asm.setbyte(HB_VISIT, 0), _uc(0), _menu(0),
            asm.mapjump(lobby, bx, by, btri, 0x80), stop]
    sec.add_entity("hbscene", {0: [asm.ret()] + ops})
    f.sections[0] = sec.build()
    n = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n <= 255, n


def _pick(var, choices):
    """Ops running one of `choices` (op lists), picked by RANDOM into var."""
    ops, end = [Op(bytes([0x99, var[0], var[1]]))], asm.nop()            # RANDOM: 0-255
    for i, act in enumerate(choices):
        nxt = asm.nop()
        if i + 1 < len(choices):
            ops.append(asm.if_byte(var, "<", (i + 1) * 256 // len(choices), nxt))
        ops += act + [asm.goto(end), nxt]
    return ops + [end]


def _idle_loop(da, kind, var):
    """A lounge girl's main: forever pause a random while, then a random
    animation of her kind (sitting ones held so she stays seated)."""
    top = asm.nop()
    anims = ([_anim(da[a], hold=True)] for a in SIT_ANIMS) if kind == "sit" else ([_anim(da[a])] for a in STAND_ANIMS)
    return ([top] + _pick(var, [[_w(n)] for n in PAUSES]) + _pick(var, list(anims))
            + [asm.goto_back(top)])


def _key_bit(j):
    """Gift j's key item: (var, bit)."""
    k = gifts.FIRST_KEY_ITEM + j
    return (1, 64 + k // 8), k % 8


def _show_aff(say_ops, var):
    """_say ops + the affection in `var` as {VAR} (MPRA2 right after WINDOW)."""
    return ([asm.setword(DISPLAY, var), say_ops[0],
             Op(bytes([0x42, DISPLAY[0], 0, 0]) + struct.pack("<H", DISPLAY[1]))] + say_ops[1:])


def _gift_routine(sec):
    """The lounge gift menu (entity hbgift script 1, REQEW'd by a girl's talk
    with GIFT_GIRL = her index). Nothing if she's at full affection or no gift
    is held; else each gift you hold is offered in turn ("Give it" / "Next
    gift" / "Not now"; past the last it starts over), so gifts you don't have
    never show. The one given is taken, and her affection rises by her liking
    of its type (gifts.PREFS), capped at gifts.MAX. The reactions are shared
    by all girls."""
    n = len(gifts.GIFTS)
    assert n == 12 and len(gifts.PREFS) == len(GIRLS)
    end, devoted, menu = asm.ret(), asm.nop(), asm.nop()
    ops = []
    for i in range(len(GIRLS)):
        nxt = asm.nop()
        ops += [asm.if_byte(GIFT_GIRL, "==", i, nxt), asm.if_byte(HB_AFFECTION[i], ">=", gifts.MAX, nxt),
                asm.goto(devoted), nxt]
    for j in range(n):                                   # holding any gift at all?
        kv, bit = _key_bit(j)
        nxt = asm.nop()
        ops += [asm.if_byte(kv, "bit_on", bit, nxt), asm.goto(menu), nxt]
    ops += [asm.goto(end), menu]
    by_type = [asm.nop() for _ in gifts.TYPES]
    for j, (name, _, t, _, _) in enumerate(gifts.GIFTS):
        kv, bit = _key_bit(j)
        skip = asm.nop()
        ask, first = _ask(sec, gifts.GIVE_PROMPT % name, ["Give it.", "Next gift.", "Not now."])
        give = asm.nop()
        ops += [asm.if_byte(kv, "bit_on", bit, skip)] + ask        # not held: not offered
        ops += [asm.if_byte(CHOICE, "!=", first + 1, skip),        # "Next gift." -> the next one held
                asm.if_byte(CHOICE, "!=", first, give), asm.goto(end),   # "Give it." -> give; else done
                give, asm.bitoff(kv, bit), asm.goto(by_type[t]), skip]
    ops += [asm.goto_back(menu)]                         # past the last held gift: from the first again
    react = {k: asm.nop() for k in gifts.GAIN}
    for t, label in enumerate(by_type):
        ops.append(label)
        for i, g in enumerate(GIRLS):
            like = gifts.PREFS[g["name"]][t]
            gain, aff = gifts.GAIN[like], HB_AFFECTION[i]
            nxt, ok = asm.nop(), asm.nop()
            ops += [asm.if_byte(GIFT_GIRL, "==", i, nxt)]
            if gain:
                ops += [Op(bytes([0x85, aff[0] << 4, aff[1], gain])),                 # PLUS
                        asm.if_byte(aff, ">", gifts.MAX, ok), asm.setbyte(aff, gifts.MAX), ok]
            ops += [asm.setword(DISPLAY, aff), asm.goto(react[like]), nxt]
        ops += [asm.goto(end)]
    for like, label in react.items():
        say = _say(sec, gifts.REACT[like])
        ops += [label, say[0], Op(bytes([0x42, DISPLAY[0], 0, 0]) + struct.pack("<H", DISPLAY[1]))] + say[1:]
        ops += [sound(0x168) if like == "L" else asm.nop(), asm.goto(end)]
    ops += [devoted] + _say(sec, gifts.DEVOTED_LINE) + [end]
    return ops


def _lounge(ctx):
    from ff7 import background as bgmod, camera as cammod, walkmesh as wmmod
    from ff7.camera import Camera, facing_screen
    f = ctx.field(ROOM)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    fmesh = Walkmesh(wmmod.flip_x(f.section("walkmesh")))
    fcam = Camera(cammod.flip_x(f.sections[1]))
    loader = ModelLoader(f.section("models"))
    sec = Script.parse(f.sections[0])
    da = {n: i for i, n in enumerate(DANCER_ANIMS + DANCER_EXTRA + SCENE_ANIMS)}
    assert len(GIRLS) == 4 * GIRLS_PER_ROOM == 20 and len(LOUNGE_SPOTS) == GIRLS_PER_ROOM
    gift_ent = sec.add_entity("hbgift", {0: [asm.ret(), asm.ret()], 1: _gift_routine(sec)})   # init, main: nothing
    for k, name in enumerate(LOUNGE_EXTRAS):
        ent = sec.entity_index(name)
        old = sec.script_ops(ent, 0)
        assert old[0].op == 0xA1, (name, old[0].raw.hex())          # CHAR
        model = old[0].raw[1]
        loader.models[model] = loader.models[1]                      # the dancer, all 22 anims
        init, done = [Op(bytes([0xA1, model])), Op(b"\x7E\x01"), Op(b"\xC7\x01"), _visi(0)], asm.nop()
        talk, tend = [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")], asm.nop()
        main = []
        if k < GIRLS_PER_ROOM:
            (x0, y0), kind, turn = LOUNGE_SPOTS[k]
            if kind == "lie":
                talk = talk[:1]                                      # she stays as she lies (no PTURA)
            for room in (1, 2, 3, 4):
                g = GIRLS_PER_ROOM * (room - 1) + k
                m, c, x = (mesh, cam, x0) if room <= 2 else (fmesh, fcam, -x0)   # rooms 3/4: FLIPPED
                t = m.find(x, y0)
                assert t is not None, (room, x, y0)
                z = m.height(t, x, y0)
                d = (facing_screen(c, x, y0, z, (0, 1)) + (turn if room <= 2 else -turn)) % 256
                radius = LIE_TALK_RADIUS if kind == "lie" else BED_TALK_RADIUS if z > 50 else TALK_RADIUS
                show = [_xyzi(x, y0, z - (SIT_DROP if kind == "sit" else 0), t), Op(bytes([0xB3, 0, d])), _visi(1),
                        Op(b"\x7E\x00"), Op(bytes([0xC5, 0x00, radius]))]          # TLKON 00, TALKR
                if kind != "stand":
                    show.append(_anim(da[LIE_ANIM if kind == "lie" else SIT_ANIMS[0]], hold=True))
                nxt = asm.nop()
                init += [asm.if_byte(HB_VISIT, "==", LOUNGE_ROOM + room, nxt),
                         asm.if_byte(_hired(g)[0], "bit_on", _hired(g)[1], nxt)] + show + [asm.goto(done), nxt]
                tnxt = asm.nop()
                talk += [asm.if_byte(HB_VISIT, "==", LOUNGE_ROOM + room, tnxt)]
                line = GIRLS[g]["name"] + "\n" + LOUNGE[GIRLS[g]["name"]] + "\n(Affection {VAR}/20)"
                talk += _show_aff(_say(sec, line), HB_AFFECTION[g])
                talk += [asm.setbyte(GIFT_GIRL, g), _req(gift_ent, 1), asm.goto(tend), tnxt]
            if kind != "lie":
                main = _idle_loop(da, kind, (LOUNGE_RAND[0], LOUNGE_RAND[1] + k))
        init += [done, asm.ret()]
        talk += [tend, Op(b"\x33\x00"), asm.ret()]
        sec.remove(old[0])                                           # its old CHAR: no second CHAR
        empty = asm.ret()
        sec.ops.extend(init + main + [asm.ret()] + talk + [empty])
        sec.entry[ent] = [empty] * 32
        sec.entry[ent][0], sec.entry[ent][1] = init[0], talk[0]
    # menu back on in a lounge (produce's init turns it off for the room's scenes)
    produce = sec.script_ops(sec.entity_index("produce"), 0)
    ret = next(o for o in produce if o.op == 0x00)
    skip = asm.nop()
    sec.insert_before(ret, [asm.if_byte(HB_VISIT, ">=", LOUNGE_ROOM, skip), _menu(0), skip], retarget=False)
    # leaving: back to the lobby door you came in by, out of lounge mode
    border = sec.entity_index("border1")
    lines = [o for o in sec.script_ops(border, 0) if o.op == 0xD0]
    assert len(lines) == 1, lines
    (ax, ay, az), (bx, by, bz) = EXIT_LINE
    lines[0].raw[1:13] = struct.pack("<6h", ax, ay, az, bx, by, bz)
    rx, ry = ROOM_ARRIVAL[:2]
    assert mesh.contains(ROOM_ARRIVAL[2], rx, ry)
    exit_ = sec.script_ops(border, 2)
    door = sec.entity_index("door")
    head = []
    for room, (ex, ey, etri, edir) in ROOM_EXITS.items():
        nxt = asm.nop()
        head += [asm.if_byte(HB_VISIT, "==", LOUNGE_ROOM + room, nxt), asm.setbyte(HB_VISIT, 0),
                 _uc(1), sound(DOOR_OPEN), _req(door, 1, wait=False), _w(12), _uc(0),      # the door opens
                 asm.mapjump(ctx.maplist.index(LOBBY), ex, ey, etri, edir), asm.ret(), nxt]
    sec.insert_before(exit_[0], head, retarget=True)
    f.set_section("models", loader.build())
    f.sections[0] = sec.build()
    n = struct.unpack_from("<H", sec.tail, 0)[0]
    assert n <= 255, n
    # ---- FLIPPED: onna_52 as built, mirrored ----
    flip = ctx.new_field(FLIPPED, f.build())
    bg = bgmod.Background(flip.section("background"))
    bg.flip_horizontal()
    flip.set_section("background", bg.build())
    flip.set_section("walkmesh", wmmod.flip_x(flip.section("walkmesh")))
    flip.sections[1] = cammod.flip_x(flip.sections[1])
    trig = bytearray(flip.section("triggers"))
    left, top, right, bottom = struct.unpack_from("<4h", trig, 12)
    struct.pack_into("<4h", trig, 12, -right, top, -left, bottom)
    flip.set_section("triggers", bytes(trig))
    fsec = Script.parse(flip.sections[0])
    lines = [o for o in fsec.script_ops(fsec.entity_index("border1"), 0) if o.op == 0xD0]
    assert len(lines) == 1, lines
    x1, y1, z1, x2, y2, z2 = struct.unpack_from("<6h", bytes(lines[0].raw), 1)
    lines[0].raw[1:13] = struct.pack("<6h", -x2, y2, z2, -x1, y1, z1)          # mirrored, ends swapped
    flip.sections[0] = fsec.build()
    # ---- the lobby: the four side doors open, each to its room ----
    rx, ry, rtri, rdir = ROOM_ARRIVAL
    assert mesh.contains(rtri, rx, ry) and fmesh.contains(rtri, -rx, ry)
    lob = ctx.field(LOBBY)
    lmesh = Walkmesh(lob.section("walkmesh"))
    for ex, ey, etri, _ in ROOM_EXITS.values():
        assert lmesh.contains(etri, ex, ey), (ex, ey, etri)
    sec = Script.parse(lob.sections[0])
    produce = sec.script_ops(sec.entity_index("produce"), 0)
    locks = [o for o in produce if o.op == 0x6D and o.raw[3] == 1 and (o.raw[1] | o.raw[2] << 8) in LOBBY_LOCKS]
    assert len(locks) == len(LOBBY_LOCKS), locks
    for o in locks:
        sec.remove(o)
    for name, room in LOBBY_DOORS.items():
        ent = sec.entity_index(name)
        assert len([o for o in sec.script_ops(ent, 2) if o.op == 0x60]) == 1, name
        if room <= 2:
            jump = asm.mapjump(ctx.maplist.index(ROOM), rx, ry, rtri, rdir)
        else:
            jump = asm.mapjump(ctx.maplist.index(FLIPPED), -rx, ry, rtri, (256 - rdir) % 256)
        sec.replace_script(ent, 2, [asm.setbyte(HB_VISIT, LOUNGE_ROOM + room), jump, asm.ret()])
    for name in CHOOSERS:                                            # nothing to choose now
        sec.replace_script(sec.entity_index(name), 1, [asm.ret()])
    lob.sections[0] = sec.build()


def _standing(ctx):
    """(fieldanim, skeleton, bone index, BAJB root rotation, its world matrices) for
    building her poses."""
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("badd.hrc").decode("latin-1"))
    rr, rp, rots = fa.Anim(ctx.char_file("bajb.a")).frames[0]
    world = [m for m, _, _ in fa.forward(sk, rr, [rp[0], -rp[1], rp[2]], rots)]
    return fa, sk, [b[0] for b in sk].index, rr, world


def _bisect(f, lo, hi):
    """x in [lo, hi] with f(x) = 0 (f changes sign between lo and hi, either way)."""
    sign = 1 if f(lo) < 0 else -1
    assert sign * f(hi) > 0, "no root in range"
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if sign * f(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


def _save_pose(ctx, fa, name, root, local):
    out = fa.Anim(ctx.char_file("dzba.a"))                                     # same header (1 frame, 21 bones)
    out.frames = [([0.0, 0.0, 0.0], [root[0], -root[1], root[2]], local)]      # root height stored negated
    ctx.char_file(name.split(".")[0].lower() + ".a", out.build())


def _eased(t, n=None):
    """0 -> 1 -> 0 over n (POSE_FRAMES) frames, slow at both ends (frame 0 = rest)."""
    import math
    return (1 - math.cos(2 * math.pi * t / (n or POSE_FRAMES))) / 2


def _save_frames(ctx, fa, name, frames):
    """frames: [(root position as FK uses it (y down), local rotations)]."""
    out = fa.Anim(ctx.char_file("dzba.a"))                                     # same header (21 bones)
    out.frames = [([0.0, 0.0, 0.0], [r[0], -r[1], r[2]], local) for r, local in frames]   # root height stored negated
    ctx.char_file(name.split(".")[0].lower() + ".a", out.build())


# The bed picture (layer 2 tiles, draw depth 140-175, screen x >= 0) had one depth per
# part, about that of the bed's far half: anyone lying on the near half was drawn
# under it; moving it all back put people standing behind the bed in front of it
# (user). Each 16 x 16 tile now gets the depth of what it shows: rays through its
# corners, edges and centre hit the bed (a box on the raised walkmesh piece, TOP,
# from the floor; EDGE wider) or the headboard (upright at its far edge, up to
# HEAD_TOP); the tile takes the farthest hit + BED_MARGIN (mattress: see
# BED_TOP_MARGIN), so someone on the bed shows and someone behind the bed (farther
# than its far edge + margin) stays hidden. Depth: tile id = view z / 4
# (the GTE's SZ / 4: the bed's parts sit at 140-175 where the bed is 560-700 deep),
# PC depth +38 = 1e7 - K / (id + d), fitted on the room's own tiles. Tiles stacked
# at one spot keep their order (+1 per step). Tiles no ray hits (right of the bed)
# are left alone.
BED_TILE_IDS, BED_TOP, BED_FLOOR, BED_EDGE, BED_HEAD_TOP, BED_MARGIN = (140, 175), 76, 25, 8, 220, 16
# The engine seems to sort a character by one depth (where it stands), not per pixel: with
# the mattress at its true depth, the tile row just nearer than a lying girl's hips covered
# her lower half in the mission scene (user). Mattress tiles now sit at the depth of the
# mattress's far edge (+ BED_TOP_MARGIN): behind anyone on the bed, in front of anyone
# behind the headboard (floor there is ~30 deeper). The front / side faces too: with
# their true depth the bed's foot covered the girl kneeling in front of it ("head", user).
BED_TOP_MARGIN = 8


def _bed_depth(ctx):
    import math
    from ff7.background import Background
    from ff7.camera import Camera
    f = ctx.field(ROOM)
    cam, mesh, bg = Camera(f.sections[1]), Walkmesh(f.section("walkmesh")), Background(f.section("background"))
    R = [[a / 4096 for a in ax] for ax in cam.axes]
    Rt = [[R[k][i] for k in range(3)] for i in range(3)]
    view_z = lambda p: sum(R[2][k] * p[k] for k in range(3)) + cam.pos[2]
    eye = [-sum(Rt[i][k] * cam.pos[k] for k in range(3)) for i in range(3)]
    bed = [i for i, t in enumerate(mesh.tris) if all(abs(v[2] - BED_TOP) < 4 for v in t)]
    assert len(bed) == 10, len(bed)
    pts = [v for i in bed for v in mesh.tris[i]]
    x0, x1, y_far = min(v[0] for v in pts), max(v[0] for v in pts), max(v[1] for v in pts)
    e = BED_EDGE

    def on_bed(x, y):
        return any(mesh.contains(t, x + dx, y + dy) for t in bed for dx, dy in ((0, 0), (e, 0), (-e, 0), (0, e), (0, -e)))

    def hit(sx, sy):
        d = [sum(Rt[i][k] * v for k, v in enumerate((sx / cam.zoom, sy / cam.zoom, 1))) for i in range(3)]
        n = math.sqrt(sum(v * v for v in d))
        d = [v / n for v in d]
        for s in range(0, 4000, 2):
            p = [eye[i] + d[i] * s for i in range(3)]
            if BED_FLOOR <= p[2] <= BED_TOP and on_bed(p[0], p[1]):
                # mattress and front / sides alike: as deep as the mattress's far edge
                return view_z([p[0], y_far, BED_TOP]) + BED_TOP_MARGIN - BED_MARGIN
        if d[1] > 0:                                             # the headboard
            p = [eye[i] + d[i] * (y_far - eye[1]) / d[1] for i in range(3)]
            if x0 - e <= p[0] <= x1 + e and BED_FLOOR <= p[2] <= BED_HEAD_TOP:
                return view_z(p)
        return None
    layer2 = next(ts for k, _, ts, _ in bg.layers if k == 2)
    # PC depth from the id: 1 / (1e7 - big) = (id + d) / K, least squares on the room's tiles
    first = {}
    for t in layer2:
        i = t._get("<H", 24)
        if 140 <= i <= 260:
            first[i] = min(first.get(i, 1e7), t._get("<I", 38))
    xs, ys = list(first), [1 / (1e7 - first[i]) for i in first]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    k_, d_ = 1 / slope, (my - slope * mx) / slope
    assert all(abs(1e7 - k_ / (i + d_) - first[i]) < 2500 for i in first), "depth fit"
    lo, hi = BED_TILE_IDS
    tiles = [t for t in layer2 if lo <= t._get("<H", 24) <= hi and t.dst_x >= 0]
    new = {}
    for t in tiles:
        zs = [hit(t.dst_x + u, t.dst_y + v) for u in (0, 8, 16) for v in (0, 8, 16)]
        zs = [z for z in zs if z is not None]
        if zs:
            new[id(t)] = (max(zs) + BED_MARGIN) / 4
    stacks = {}
    for t in tiles:
        stacks.setdefault((t.dst_x, t.dst_y), []).append(t)
    changed = 0
    for spot, ts in stacks.items():
        for rank, t in enumerate(sorted(ts, key=lambda t: t._get("<H", 24))):
            if id(t) not in new:
                continue
            z = new[id(t)] + rank
            t._set("<H", 24, int(z))
            t._set("<I", 38, round(1e7 - k_ / (z + d_)))
            changed += 1
    assert changed > 150, changed
    f.set_section("background", bg.build())


# Cloud for the devoted scenes' part two (user): his model (AAAA.HRC) with the pants'
# colour (purple, on the pelvis, thighs and upper shins) replaced by his arms' skin
# colour, and each knee ring (thigh bottom, shin top: radius ~2.8, the bulge) brought
# in to the size of the thigh's hip ring (~1.6) about its own centre. New files:
# zcla.hrc (bones as AAAA) -> new .rsd for the five changed parts -> new .p.
CLOUD_BARE_HRC = "ZCLA.HRC"
BARE_PARTS = {"AAAB": "ZCLB", "AADE": "ZCLC", "AAEA": "ZCLD", "AAEE": "ZCLE", "AAFA": "ZCLF"}   # rsd -> rsd
PANTS, SKIN = (119, 73, 97), (135, 167, 248)        # vertex colours (B, G, R) of the pants / the arms


def _bare_cloud(ctx):
    import math
    hrc = ctx.char_file("aaaa.hrc").decode("latin-1")
    arm = ctx.char_file("aabf.p")
    for old, new in BARE_PARTS.items():
        assert hrc.count("1 %s\r\n" % old) == 1 or hrc.count("1 %s\n" % old) == 1, old
        hrc = hrc.replace("1 %s" % old, "1 %s" % new)
        rsd = ctx.char_file(old.lower() + ".rsd").decode("latin-1")
        ply = rsd.split("PLY=")[1][:4]
        newp = "ZCM" + new[3]                                       # ZCMB.. : the new .p files
        ctx.char_file(new.lower() + ".rsd", rsd.replace("PLY=%s." % ply, "PLY=%s." % newp).encode("latin-1"))
        d = bytearray(ctx.char_file(ply.lower() + ".p"))
        h = struct.unpack_from("<16I", d, 0)
        nv, nn, nunk, nt, nc, ne, npoly = h[3], h[4], h[5], h[6], h[7], h[8], h[9]
        o_v = 128
        o_c = o_v + 12 * nv + 12 * nn + 12 * nunk + 8 * nt
        o_pc = o_c + 4 * nc
        recoloured = 0
        for o in [o_c + 4 * i for i in range(nc)] + [o_pc + 4 * i for i in range(npoly)]:
            if tuple(d[o:o + 3]) == PANTS:
                d[o:o + 3] = bytes(SKIN)
                recoloured += 1
        assert recoloured, old
        V = [list(struct.unpack_from("<3f", d, o_v + 12 * i)) for i in range(nv)]
        if old != "AAAB":                                           # thigh / shin: the knee ring
            thigh = old in ("AADE", "AAEE")
            ring = lambda zz: [i for i, v in enumerate(V) if abs(v[2] - zz) < 0.2]
            # each knee is a ring of 4 plus a cone to one tip vertex (the knee point); the
            # tip sits off the ring's centre, to the front: the ring is shrunk around the
            # line through the tip (as the hip ring is centred on it) and the cone shortened
            # by the same factor, else the knee became a forward spike (user)
            kz = -5.08 if thigh else 0.0
            knee = ring(kz)
            tip = [i for i, v in enumerate(V) if (v[2] < -7 if thigh else v[2] > 1.5)]
            assert len(knee) == 4 and len(tip) == 1, (old, knee, tip)
            tip = tip[0]
            kx, ky = V[tip][0], V[tip][1]
            if thigh:
                hip = ring(0.0)
                assert len(hip) == 4, (old, hip)
                cx, cy = sum(V[i][0] for i in hip) / 4, sum(V[i][1] for i in hip) / 4
                _bare_cloud.target = sum(math.hypot(V[i][0] - cx, V[i][1] - cy) for i in hip) / 4
            target = _bare_cloud.target
            old_r = sum(math.hypot(V[i][0] - kx, V[i][1] - ky) for i in knee) / 4
            for i in knee:
                r = math.hypot(V[i][0] - kx, V[i][1] - ky)
                V[i][0], V[i][1] = kx + (V[i][0] - kx) * target / r, ky + (V[i][1] - ky) * target / r
                V[i][2] = kz
            V[tip][2] = kz + (V[tip][2] - kz) * target / old_r
            for i in knee + [tip]:
                struct.pack_into("<3f", d, o_v + 12 * i, *V[i])
        ctx.char_file(newp.lower() + ".p", bytes(d))
    ctx.char_file(CLOUD_BARE_HRC.lower(), hrc.encode("latin-1"))


# Mood lighting (user: "dim the light to about 50%"): the visit rooms' background palette
# (every tile is paletted; 15-bit colours, bit 15 kept; a colour that would become
# 0x0000 = transparent becomes 0x8000, opaque black) and every model's light colours
# (model loader light block: 3 x (RGB + direction) + ambient RGB) scaled by ROOM_LIGHT.
ROOM_LIGHT = 0.5


def _dim(ctx, field):
    f = ctx.field(field)
    pal = bytearray(f.section("palette"))
    for o in range(12, len(pal) - 1, 2):
        v = struct.unpack_from("<H", pal, o)[0]
        if v == 0:
            continue
        r, g, b = (round((v >> s & 31) * ROOM_LIGHT) for s in (0, 5, 10))
        n = r | g << 5 | b << 10 | (v & 0x8000)
        struct.pack_into("<H", pal, o, n if n & 0x7FFF or v & 0x7FFF == 0 else 0x8000)
    f.set_section("palette", bytes(pal))
    loader = ModelLoader(f.section("models"))
    for k, e in enumerate(loader.models):
        e = bytearray(e)
        nl = struct.unpack_from("<H", e, 0)[0]
        light = 2 + nl + 2 + 8 + 4 + 2
        for o in (0, 9, 18, 27):                                     # light 1-3 colours, ambient
            e[light + o:light + o + 3] = bytes(round(c * ROOM_LIGHT) for c in e[light + o:light + o + 3])
        loader.models[k] = bytes(e)
    f.set_section("models", loader.build())


def _cloud_buck(ctx):
    """zctd.a (CLOUD_BUCK) on Cloud's skeleton: see CLOUD_BUCK."""
    import math
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    I = [b[0] for b in sk].index
    base = fa.Anim(ctx.char_file("grea.a"))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]                    # y down
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    unit = lambda a: [v / math.sqrt(dot(a, a)) for v in a]
    bdir = lambda m: fa._vec(m, [0, 0, -1])

    def align(a, b):
        a, b = unit(a), unit(b)
        ax = cross(a, b)
        s = math.sqrt(dot(ax, ax))
        return fa.axis_angle(ax, math.degrees(math.atan2(s, dot(a, b)))) if s > 1e-9 else fa.euler_matrix(0, 0, 0)
    fk = fa.forward(sk, rr, root, rots)
    W = [m for m, _, _ in fk]
    up = [0.0, -1.0, 0.0]
    along = unit(sub(fk[I("chest")][2], fk[I("hip")][1]))          # feet -> head, along the body
    along = unit([along[0], 0.0, along[2]])
    side = unit(cross(up, along))
    # head: bone along the body tipped up BUCK_HEAD, face up tipped towards the feet (local +y = face)
    t = math.radians(BUCK_HEAD)
    hb = [along[k] * math.cos(t) + up[k] * math.sin(t) for k in range(3)]
    face = [up[k] * math.cos(t) - along[k] * math.sin(t) for k in range(3)]
    x = cross(face, [-v for v in hb])                                # local +x = y cross z, z = -bone
    W[I("head")] = [[x[r], face[r], -hb[r]] for r in range(3)]      # columns: local x, y, z
    det = sum(W[I("head")][0][c] * (W[I("head")][1][(c + 1) % 3] * W[I("head")][2][(c + 2) % 3]
                                      - W[I("head")][1][(c + 2) % 3] * W[I("head")][2][(c + 1) % 3]) for c in range(3))
    assert abs(det - 1) < 1e-6, det
    # arms raised off the bed about the body's side axis (pick the sense that lifts the hands)
    for s in "lr":
        chain = [I(s + n) for n in ("_uparm", "_foarm", "_hand")]
        for a in (BUCK_ARMS, -BUCK_ARMS):
            R = fa.axis_angle(side, a)
            M = [fa._mul(R, W[i]) if i in chain else W[i] for i in range(len(sk))]
            hand = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, M))[I(s + "_hand")][2]
            if hand[1] < fk[I(s + "_hand")][2][1] - 1:               # y down: higher = smaller y
                W = M
                break
        else:
            raise AssertionError(s)
    rest = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
    W0, S0, E0 = [m for m, _, _ in rest], [s for _, s, _ in rest], [e for _, _, e in rest]
    frames = []
    for f in range(BUCK_FRAMES):
        h = BUCK_RISE * (1 - math.cos(2 * math.pi * f / BUCK_FRAMES)) / 2
        rt = [root[0], root[1] - h, root[2]]
        Wt = list(W0)
        for n in ("chest", "l_chest", "r_chest", "l_femur", "r_femur"):   # shoulders and knees stay
            i = I(n)
            Wt[i] = fa._mul(align(bdir(W0[i]), sub(E0[i], [S0[i][0], S0[i][1] - h, S0[i][2]])), W0[i])
        local = fa.local_rotations(sk, rr, Wt)
        if f == BUCK_FRAMES // 2:
            top = fa.forward(sk, rr, rt, local)
            assert top[I("hip")][1][1] < S0[I("hip")][1] - 1, "hips should rise"
            assert math.dist(top[I("head")][2], E0[I("head")]) < 0.8, "shoulders moved"
        frames.append((rr, [rt[0], -rt[1], rt[2]], local))
    base.frames = frames
    ctx.char_file(CLOUD_BUCK.split(".")[0].lower() + ".a", base.build())


def _cloud_stand(ctx, name=CLOUD_STAND, arms=STAND_ARMS, lift=None, nframes=STAND_FRAMES, elbow_in=0,
                 lean=STAND_LEAN, arms_out=0):
    """zcte.a (CLOUD_STAND) on Cloud's skeleton: see CLOUD_STAND. lift = (hip, knee):
    the left thigh raised to `hip` degrees forward of vertical, the left knee bent
    only `knee` (EDGE_CLOUD_*: zctf.a)."""
    import math
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    I = [b[0] for b in sk].index
    base = fa.Anim(ctx.char_file("acfe.a"))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]                    # y down: up is -y; he faces -z, his left is +x
    side, up, fwd = [1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    bdir = lambda m: fa._vec(m, [0, 0, -1])
    W = [m for m, _, _ in fa.forward(sk, rr, root, rots)]
    fk = lambda W, r=root: fa.forward(sk, rr, r, fa.local_rotations(sk, rr, W))
    rot = lambda W, names, R: [fa._mul(R, m) if sk[i][0] in names else m for i, m in enumerate(W)]

    def signed(W, names, angle, test):               # rotate `names` about the side axis, the sense `test` wants
        for s in (1, -1):
            M = rot(W, names, fa.axis_angle(side, s * angle))
            if test(fk(M)):
                return M
        raise AssertionError(names)
    end = lambda F, n: F[I(n)][2]
    feet0 = {s: end(fk(W), s + "_tibia") for s in "lr"}
    for s in "lr":                                   # knee bend: thigh forward half, shin back the other half
        leg = (s + "_femur", s + "_tibia", s + "_foot")
        W = signed(W, leg, STAND_KNEE / 2, lambda F: dot(end(F, s + "_femur"), fwd) > dot(feet0[s], fwd))
        W = signed(W, leg[1:], STAND_KNEE, lambda F: dot(sub(end(F, s + "_tibia"), end(F, s + "_femur")), fwd) < 0)
    if lift:                                         # left leg up: thigh from STAND_KNEE / 2 to lift[0] forward,
        hip, knee = lift                             # the knee opened from STAND_KNEE to lift[1]
        k0 = end(fk(W), "l_femur")
        W = signed(W, ("l_femur", "l_tibia", "l_foot"), hip - STAND_KNEE / 2,
                   lambda F: dot(end(F, "l_femur"), fwd) > dot(k0, fwd))
        thigh = lambda F: sub(end(F, "l_femur"), F[I("l_femur")][1])
        shin = lambda F: sub(end(F, "l_tibia"), end(F, "l_femur"))
        bend = lambda F: math.degrees(math.acos(dot(thigh(F), shin(F)) / math.sqrt(dot(thigh(F), thigh(F)) * dot(shin(F), shin(F)))))
        b0 = bend(fk(W))
        W = signed(W, ("l_tibia", "l_foot"), STAND_KNEE - knee, lambda F: bend(F) < b0)
        F = fk(W)
        assert abs(bend(F) - knee) < 1, bend(F)
        assert end(F, "l_femur")[1] < F[I("l_femur")][1][1], "left knee not above the hip"   # y down
    upper = {"hip", "chest", "head", "l_chest", "l_collar", "l_uparm", "l_foarm", "l_hand",
             "r_chest", "r_collar", "r_uparm", "r_foarm", "r_hand"}
    head0 = end(fk(W), "head")
    sense = 1 if lean > 0 else -1                    # lean < 0: torso back
    W = signed(W, upper, abs(lean), lambda F: sense * dot(end(F, "head"), fwd) > sense * dot(head0, fwd) + 1)
    for s, out in (("l", 1), ("r", -1)):
        arm = (s + "_uparm", s + "_foarm", s + "_hand")
        hand0 = end(fk(W), s + "_hand")
        angle = arms[s] if isinstance(arms, dict) else arms
        W = signed(W, arm, angle, lambda F: dot(end(F, s + "_hand"), fwd) > dot(hand0, fwd) + 1)  # arms forward
        if arms_out:                                 # the whole arm turned out (< 0: in) about the vertical
            hx = end(fk(W), s + "_hand")[0]
            way = 1 if arms_out > 0 else -1
            for sign in (1, -1):
                M = rot(W, arm, fa.axis_angle(up, sign * abs(arms_out)))
                if way * out * end(fk(M), s + "_hand")[0] > way * out * hx + 0.2:
                    W = M
                    break
            else:
                raise AssertionError("arms out " + s)
        if elbow_in:                                 # forearm turned in towards the middle at the elbow
            hx = end(fk(W), s + "_hand")[0]
            for sign in (1, -1):
                M = rot(W, arm[1:], fa.axis_angle(up, sign * elbow_in))
                if out * end(fk(M), s + "_hand")[0] < out * hx - 0.3:
                    W = M
                    break
            else:
                raise AssertionError("elbow " + s)
    F0 = fk(W)
    drop = max(end(F0, s + "_tibia")[1] for s in "lr") - max(feet0[s][1] for s in "lr")
    root = [root[0], root[1] - drop, root[2]]                                 # ankles back on the floor
    F0 = fk(W, root)
    S0, E0 = [s for _, s, _ in F0], [e for _, _, e in F0]

    def align(a, b):
        n = lambda v: [c / math.sqrt(dot(v, v)) for c in v]
        a, b = n(a), n(b)
        ax = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
        si = math.sqrt(dot(ax, ax))
        return fa.axis_angle(ax, math.degrees(math.atan2(si, dot(a, b)))) if si > 1e-9 else fa.euler_matrix(0, 0, 0)
    frames = []
    for t in range(nframes):
        e = (1 - math.cos(2 * math.pi * t / nframes)) / 2
        d = STAND_THRUST * e
        rt = [root[k] + fwd[k] * d for k in range(3)]                          # hips forward
        Wt = list(W)
        for n in ("r_femur",) if lift else ("l_femur", "r_femur"):            # knees stay: thighs re-aimed
                                                                               # (a raised leg rides with the hips)
            i = I(n)
            start = [S0[i][k] + fwd[k] * d for k in range(3)]
            Wt[i] = fa._mul(align(bdir(W[i]), sub(E0[i], start)), W[i])
        for s, out in (("l", 1), ("r", -1)):                                   # arms close in as he thrusts
            arm = {s + "_uparm", s + "_foarm", s + "_hand"}
            for sign in (1, -1):
                M = rot(Wt, arm, fa.axis_angle(up, sign * STAND_ARMS_IN * e))
                if e < 1e-9 or out * end(fk(M, rt), s + "_hand")[0] < out * end(fk(Wt, rt), s + "_hand")[0]:
                    Wt = M
                    break
        local = fa.local_rotations(sk, rr, Wt)
        if t == nframes // 2:
            top = fa.forward(sk, rr, rt, local)
            for s in ("r" if lift else "lr"):
                assert math.dist(top[I(s + "_tibia")][2], E0[I(s + "_tibia")]) < 0.6, s       # feet planted
        frames.append((rr, [rt[0], -rt[1], rt[2]], local))
    base.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", base.build())


def _cloud_spread(ctx):
    """zctc.a (CLOUD_SPREAD) on Cloud's skeleton: see CLOUD_SPREAD."""
    import math
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    I = [b[0] for b in sk].index
    base = fa.Anim(ctx.char_file("eiab.a"))
    up = [0.0, -1.0, 0.0]
    frames = []
    for rr, rp, rots in base.frames:
        root = [rp[0], -rp[1], rp[2]]
        fk = fa.forward(sk, rr, root, rots)
        W = [m for m, _, _ in fk]
        heading = lambda s, M: (lambda d: math.atan2(d[0], -d[2]))(fa._vec(M[I(s + "_femur")], [0, 0, -1]))
        fwd = (heading("l", W) + heading("r", W)) / 2                 # straight ahead: between the thighs
        for s, out in (("l", 1), ("r", -1)):
            hip_side = fk[I(s + "_femur")][1][0] - root[0]
            sign = out if hip_side * out > 0 else -out                # outward = the side its hip is on
            want = fwd + sign * math.radians(SPREAD_ANGLE)
            turn = math.degrees(want - heading(s, W))
            for a in (turn, -turn):                                   # axis_angle's sense about -y: try both
                R = fa.axis_angle(up, a)
                M = [fa._mul(R, W[i]) if sk[i][0] in (s + "_femur", s + "_tibia", s + "_foot") else W[i]
                     for i in range(len(sk))]
                if abs(heading(s, M) - want) < 1e-3:
                    W = M
                    break
            else:
                raise AssertionError(s)
        local = fa.local_rotations(sk, rr, W)
        top = fa.forward(sk, rr, root, local)
        knees = [top[I(s + "_femur")][2][0] for s in "lr"]
        assert abs(knees[0] - knees[1]) > abs(fk[I("l_femur")][2][0] - fk[I("r_femur")][2][0]) + 2, knees  # apart
        frames.append((rr, rp, local))
    base.frames = frames
    ctx.char_file(CLOUD_SPREAD.split(".")[0].lower() + ".a", base.build())


def _cloud_pound(ctx):
    """zctb.a (CLOUD_POUND) on Cloud's skeleton: see CLOUD_POUND."""
    import math
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    I = [b[0] for b in sk].index
    base = fa.Anim(ctx.char_file("hbgb.a"))
    rr, rp, rots = base.frames[0]
    root = [rp[0], -rp[1], rp[2]]                    # root height stored negated: y down
    fk = fa.forward(sk, rr, root, rots)
    W = [m for m, _, _ in fk]
    end = lambda n: fk[I(n)][2]
    knee = [(end("l_femur")[k] + end("r_femur")[k]) / 2 for k in range(3)]
    ankle = [(end("l_tibia")[k] + end("r_tibia")[k]) / 2 for k in range(3)]
    fwd = [knee[0] - ankle[0], 0.0, knee[2] - ankle[2]]
    n = math.hypot(fwd[0], fwd[2])
    fwd = [fwd[0] / n, 0.0, fwd[2] / n]
    lk, rk = end("l_femur"), end("r_femur")
    side = [rk[k] - lk[k] for k in range(3)]         # the line through both knees (they aren't level)
    n = math.sqrt(sum(v * v for v in side))
    side = [v / n for v in side]
    knee = lk                                        # pivot on that line: both knees stay put
    hip = [(fk[I("l_femur")][1][k] + fk[I("r_femur")][1][k]) / 2 - knee[k] for k in range(3)]
    probe = fa._vec(fa.axis_angle(side, 10), hip)    # pick the sign that swings the hips forward
    sign = 1 if sum(probe[k] * fwd[k] for k in range(3)) > sum(hip[k] * fwd[k] for k in range(3)) else -1
    moved = {"hip", "chest", "head", "l_chest", "l_collar", "l_uparm", "l_foarm", "l_hand", "r_chest",
             "r_collar", "r_uparm", "r_foarm", "r_hand", "l_hip", "r_hip"}
    frames = []
    for t in range(POUND_FRAMES):
        a = sign * POUND_SWING * (1 - math.cos(2 * math.pi * t / POUND_FRAMES)) / 2
        R = fa.axis_angle(side, a)
        rel = fa._vec(R, [root[k] - knee[k] for k in range(3)])
        rt = [knee[k] + rel[k] for k in range(3)]                 # the pelvis swings about the knee line
        Wt = [fa._mul(R, W[i]) if sk[i][0] in ("hip", "l_hip", "r_hip", "l_femur", "r_femur") else W[i]
              for i in range(len(sk))]                            # pelvis + thighs rigid; torso unturned
        local = fa.local_rotations(sk, rr, Wt)
        if t == POUND_FRAMES // 2:
            top = fa.forward(sk, rr, rt, local)
            for leg in ("l", "r"):                                # knees and feet stay put
                assert math.dist(top[I(leg + "_femur")][2], end(leg + "_femur")) < 0.1, leg
                assert math.dist(top[I(leg + "_foot")][2], end(leg + "_foot")) < 0.1, leg
            assert -top[I("hip")][1][1] > -root[1] + 0.5, "hips should rise"
        frames.append((rr, [rt[0], -rt[1], rt[2]], local))
    assert all(sk[i][0] in moved or sk[i][0].split("_")[1] in ("femur", "tibia", "foot") for i in range(len(sk)))
    base.frames = frames
    ctx.char_file(CLOUD_POUND.split(".")[0].lower() + ".a", base.build())


def _cloud_thrust(ctx):
    """zcta.a (CLOUD_THRUST) on Cloud's skeleton (AAAA.HRC), from AVDD: see CLOUD_THRUST."""
    import math
    from ff7 import fieldanim as fa
    sk = fa.skeleton(ctx.char_file("aaaa.hrc").decode("latin-1"))
    names = [b[0] for b in sk]
    I = names.index
    base = fa.Anim(ctx.char_file("avdd.a"))
    rr, rp, rots = base.frames[0]
    stand = fa.Anim(ctx.char_file("acfe.a")).frames[0][2]
    root = [rp[0], -rp[1], rp[2]]                    # root height stored negated: y down, floor 0
    sub = lambda a, b: [a[k] - b[k] for k in range(3)]
    add = lambda a, b: [a[k] + b[k] for k in range(3)]
    dot = lambda a, b: sum(a[k] * b[k] for k in range(3))
    cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    unit = lambda a: [x / math.sqrt(dot(a, a)) for x in a]
    bdir = lambda m: fa._vec(m, [0, 0, -1])          # a bone runs along its own -z

    def align(a, b):                                 # the smallest rotation turning direction a into b
        a, b = unit(a), unit(b)
        ax = cross(a, b)
        s = math.sqrt(dot(ax, ax))
        return fa.axis_angle(ax, math.degrees(math.atan2(s, dot(a, b)))) if s > 1e-9 else fa.euler_matrix(0, 0, 0)
    fk = fa.forward(sk, rr, root, rots)
    W, S, E = [m for m, _, _ in fk], [s for _, s, _ in fk], [e for _, _, e in fk]
    up = [0, -1, 0]
    mid = [(S[I("l_femur")][k] + S[I("r_femur")][k]) / 2 for k in range(3)]
    head = E[I("head")]
    along = unit([mid[0] - head[0], 0, mid[2] - head[2]])        # level, head -> feet
    lat = unit(cross(up, along))
    knee_h = (-E[I("l_femur")][1] - E[I("r_femur")][1]) / 2     # both knees at their mean height
    for side in ("l", "r"):
        fe, ti, fo = I(side + "_femur"), I(side + "_tibia"), I(side + "_foot")
        s0 = S[fe]
        want = THRUST_KNEE_GAP if dot(sub(E[fe], mid), lat) > 0 else -THRUST_KNEE_GAP
        knee = lambda R: add(s0, fa._vec(R, sub(E[fe], s0)))
        side_axis = unit(cross(bdir(W[fe]), up))
        pitch = min((x / 4 for x in range(-160, 161)),                # level the knee
                    key=lambda x: abs(-knee(fa.axis_angle(side_axis, x))[1] - knee_h))
        P = fa.axis_angle(side_axis, pitch)
        swing = min((x / 4 for x in range(-320, 321)),                # then swing it in (about the vertical)
                    key=lambda x: abs(dot(sub(knee(fa._mul(fa.axis_angle(up, x), P)), mid), lat) - want))
        R = fa._mul(fa.axis_angle(up, swing), P)
        assert abs(-knee(R)[1] - knee_h) < 0.1 and abs(dot(sub(knee(R), mid), lat) - want) < 0.1, (side, knee(R))
        W[fe] = fa._mul(R, W[fe])
        shin = fa._mul(R, W[ti])
        W[ti] = fa._mul(align(bdir(shin), along), shin)            # the shin straight back, level
        foot = fa._mul(W[ti], fa.euler_matrix(*stand[fo]))          # the standing ankle, then pointed
        W[fo] = fa._mul(align(bdir(foot), along), foot)
    rest = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, W))
    W0, S0, E0 = [m for m, _, _ in rest], [s for _, s, _ in rest], [e for _, _, e in rest]
    for n in ("l_tibia", "r_tibia", "l_foot", "r_foot"):
        assert abs(E0[I(n)][1] - S0[I(n)][1]) < 0.05, n               # level
    frames = []
    for t in range(THRUST_FRAMES):
        h = THRUST_RISE * (1 - math.cos(2 * math.pi * t / THRUST_FRAMES)) / 2
        rt = [root[0], root[1] - h, root[2]]
        Wt = list(W0)
        for n in ("chest", "l_chest", "r_chest", "l_femur", "r_femur"):   # aimed back at where they ended
            i = I(n)
            Wt[i] = fa._mul(align(bdir(W0[i]), sub(E0[i], [S0[i][0], S0[i][1] - h, S0[i][2]])), W0[i])
        local = fa.local_rotations(sk, rr, Wt)
        if t == THRUST_FRAMES // 2:
            top = fa.forward(sk, rr, rt, local)
            assert all(math.dist(top[I(n)][2], E0[I(n)]) < 0.8 for n in ("l_hand", "r_hand", "head")), "shoulders moved"
        frames.append((rr, [rt[0], -rt[1], rt[2]], local))
    base.frames = frames
    ctx.char_file(CLOUD_THRUST.split(".")[0].lower() + ".a", base.build())


def _on_back(ctx, name=LIE_ANIM_SCENE, arms=LIE_ARMS, head=LIE_HEAD, head_rock=LIE_HEAD_ROCK, hip_lift=0.0,
             head_down=False):
    """dzbt.a (LIE_ANIM_SCENE): on her back, knees up and apart, feet planted;
    the knees fall open POSE_ROCK and close again (each leg turns about its
    hip-ankle line, so the feet stay exactly where they are), POSE_FRAMES frames.
    arms: degrees out from her sides along the bed (160: up past her head);
    head: degrees chin to chest (< 0: tipped back), rocking head_rock (> 0: further
    forward as she comes down). hip_lift: her hips held this much higher throughout (the
    shoulders stay down, so her body slopes back to them); head_down: the head
    hangs straight down every frame (face upright: head reverse)."""
    fa, sk, idx, rr, world = _standing(ctx)
    names = [b[0] for b in sk]
    x, z = (1, 0, 0), (0, 0, 1)
    back = fa.axis_angle(x, -90)                     # whole body pitched back: up -> +z, front -> up
    hip_pos = fa.Anim(ctx.char_file("dzba.a")).frames[0][1]
    root = [0.0, -hip_pos[1], hip_pos[2]]           # hips where the game's lying pose has them

    def pose(knee, foot):                            # world matrices
        w = [fa._mul(back, m) for m in world]
        for side, out in (("l", LEG_SPREAD), ("r", -LEG_SPREAD)):
            thigh = fa._mul(fa.axis_angle(z, out), fa.axis_angle(x, -LEG_RAISE))   # up, then out to her side
            for n in ("_hip", "_femur", "_tibia", "_foot"):
                w[idx(side + n)] = fa._mul(thigh, w[idx(side + n)])
            kneebend = fa.axis_angle(x, knee)
            for n in ("_tibia", "_foot"):
                w[idx(side + n)] = fa._mul(fa._mul(thigh, fa._mul(kneebend, fa._t(thigh))), w[idx(side + n)])
            w[idx(side + "_foot")] = fa._mul(fa.axis_angle(x, foot), w[idx(side + "_foot")])
        return w

    def ends(w):
        return {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, root, fa.local_rotations(sk, rr, w)))}
    knee = _bisect(lambda k: ends(pose(k, 0))["l_tibia"][1], 0, 120)          # ankle down to the bed (~100)
    foot = _bisect(lambda f: ends(pose(knee, f))["l_tibia"][1] - ends(pose(knee, f))["l_foot"][1], -90, 90)
    w0 = pose(knee, foot)
    e0 = ends(w0)
    for n in ("l_tibia", "r_tibia", "l_foot", "r_foot"):
        assert abs(e0[n][1]) < 0.5, (n, e0[n])                                 # feet planted
    assert e0["l_femur"][1] < -2 and e0["r_femur"][1] < -2, (e0["l_femur"], e0["r_femur"])   # knees up
    import math
    up = [0.0, -1.0, 0.0]
    bdir = lambda m: fa._vec(m, [0, 0, -1])

    def align(a, b):                                 # the smallest rotation turning direction a into b
        n = lambda v: [c / math.sqrt(sum(q * q for q in v)) for q in [0] for c in v]
        a, b = n(a), n(b)
        ax = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
        s = math.sqrt(sum(c * c for c in ax))
        return fa.axis_angle(ax, math.degrees(math.atan2(s, sum(a[k] * b[k] for k in range(3))))) if s > 1e-9 \
            else fa.euler_matrix(0, 0, 0)

    def pick(rotate, test):                          # the sign of a rotation that passes `test`
        for s in (1, -1):
            w = rotate(s)
            if test(ends(w)):
                return w
        raise AssertionError("no sign")
    # arms out from her sides (about the vertical at each shoulder: the hand moves away from the middle)
    for side in "lr":
        chain = [idx(side + n) for n in ("_uparm", "_foarm", "_hand")]
        mid_x = e0["hip"][0]
        turned = lambda s: [fa._mul(fa.axis_angle(up, s), m) if i in chain else m for i, m in enumerate(w0)]
        s = next(s for s in (1, -1)                  # the sense that swings the hand away from the middle
                 if abs(ends(turned(s * 20))[side + "_hand"][0] - mid_x) > abs(e0[side + "_hand"][0] - mid_x) + 0.5)
        w0 = turned(s * arms)
    e0 = ends(w0)
    # the head: which sense of the side axis lifts the top of her head (chin to chest)
    head_up = pick(lambda s: [fa._mul(fa.axis_angle(x, s * 20), m) if i == idx("head") else m for i, m in enumerate(w0)],
                   lambda e: e["head"][1] < e0["head"][1] - 0.5)
    sense = 1 if fa._mul(fa.axis_angle(x, 20), w0[idx("head")]) == head_up[idx("head")] else -1
    frames = []
    for t in range(LIE_FRAMES):
        b = _eased(t, LIE_FRAMES)
        w = list(w0)
        for side, outward in (("l", -1), ("r", 1)):            # sign checked: the knees move apart
            h, a = e0[side + "_hip"], e0[side + "_tibia"]                      # hip joint, ankle
            turn = fa.axis_angle([a[k] - h[k] for k in range(3)], outward * POSE_ROCK * b)
            for n in ("_femur", "_tibia", "_foot"):
                w[idx(side + n)] = fa._mul(turn, w0[idx(side + n)])
        e = ends(w)
        for n in ("l_tibia", "r_tibia"):
            assert all(abs(e[n][k] - e0[n][k]) < 0.05 for k in range(3)), (t, n)   # feet stay put (before the bounce)
        rest = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, w))
        bounce, thrust = LIE_BOUNCE * b, hip_lift + LIE_THRUST * b
        lift = [root[0], root[1] - bounce - thrust, root[2]]                  # y down: up is -y
        for n in ("chest", "l_chest", "r_chest", "l_femur", "r_femur"):        # shoulders / knees: bounce only
            i = idx(n)
            _, s0, e_ = rest[i]
            start = [s0[0], s0[1] - bounce - thrust, s0[2]]
            target = [e_[0], e_[1] - bounce, e_[2]]
            w[i] = fa._mul(align(bdir(w[i]), [target[k] - start[k] for k in range(3)]), w[i])
        v = math.sin(2 * math.pi * t / LIE_FRAMES)                           # > 0 going up, < 0 coming down
        tilt = head - head_rock * v                                           # (mission) forward coming down, back going up
        if head_down:
            w[idx("head")] = fa._mul(align(bdir(w[idx("head")]), [0.0, 1.0, 0.0]), w[idx("head")])   # y down
        else:
            w[idx("head")] = fa._mul(fa.axis_angle(x, sense * tilt), w[idx("head")])
        frames.append((lift, fa.local_rotations(sk, rr, w)))
    _save_frames(ctx, fa, name, frames)


def _fours(ctx):
    """dzbf.a (FOURS_ANIM): on all fours, rocking back POSE_ROCK on the knees and
    forward again over POSE_FRAMES frames; knees, shins and hands stay planted
    (each arm re-bent by two-bone IK in her front-back plane), body horizontal."""
    fa, sk, idx, rr, world = _standing(ctx)
    names = [b[0] for b in sk]
    x = (1, 0, 0)                                    # her left-right axis: pitches turn about it
    length = {b[0]: b[2] for b in sk}

    def pose(rock, arms, foot):                      # world matrices; arms: {side: (upper, fore) angles}
        w = list(world)
        for n in ("hip", "chest", "head", "l_chest", "l_collar", "r_chest", "r_collar"):
            w[idx(n)] = fa._mul(fa.axis_angle(x, 90), world[idx(n)])          # facing down
        w[idx("head")] = fa._mul(fa.axis_angle(x, -FOURS_HEAD_LIFT), w[idx("head")])
        for side in "lr":
            up, fore = arms[side]
            w[idx(side + "_uparm")] = fa._mul(fa.axis_angle(x, up), world[idx(side + "_uparm")])
            w[idx(side + "_foarm")] = fa._mul(fa.axis_angle(x, fore), world[idx(side + "_foarm")])
            w[idx(side + "_hand")] = fa._mul(fa.axis_angle(x, -90), world[idx(side + "_hand")])
            w[idx(side + "_femur")] = fa._mul(fa.axis_angle(x, rock), world[idx(side + "_femur")])   # - = hips back
            w[idx(side + "_tibia")] = fa._mul(fa.axis_angle(x, 90), world[idx(side + "_tibia")])
            w[idx(side + "_foot")] = fa._mul(fa.axis_angle(x, foot), world[idx(side + "_foot")])
        return w

    def ends(w, root):
        return {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, root, fa.local_rotations(sk, rr, w)))}

    def hang(elbow):
        return {"l": (0.0, -elbow), "r": (0.0, -elbow)}
    e = ends(pose(0, hang(0), 180), [0, 0, 0])
    root0 = [0, -(e["l_femur"][1] + e["r_femur"][1]) / 2, 0]                  # knees on the floor
    elbows = {s: _bisect(lambda a, s=s: -ends(pose(0, hang(a), 180), root0)[s + "_foarm"][1], 0, 90) for s in "lr"}
    arms0 = {s: (0.0, -elbows[s]) for s in "lr"}
    foot = _bisect(lambda f: ends(pose(0, arms0, f), root0)["l_tibia"][1]
                   - ends(pose(0, arms0, f), root0)["l_foot"][1], 90, 270)
    e0 = ends(pose(0, arms0, foot), root0)
    for n in ("l_femur", "r_femur", "l_foarm", "r_foarm", "l_tibia", "r_tibia"):
        assert abs(e0[n][1]) < 0.5, (n, e0[n])                                 # on the floor
    knee0, wrist0 = e0["l_femur"], {s: e0[s + "_foarm"] for s in "lr"}

    def reach(rock, root, arms, side):               # (upper, fore) angles putting the wrist back on wrist0:
        def miss(up, fore):                          # Newton on the real skeleton (y, z of the wrist)
            e = ends(pose(rock, dict(arms, **{side: (up, fore)}), foot), root)[side + "_foarm"]
            return e[1] - wrist0[side][1], e[2] - wrist0[side][2]
        up, fore = arms[side]
        for _ in range(30):
            fy, fz = miss(up, fore)
            if abs(fy) + abs(fz) < 1e-4:
                break
            h = 0.01
            ay, az = [(v - f) / h for v, f in zip(miss(up + h, fore), (fy, fz))]
            by, bz = [(v - f) / h for v, f in zip(miss(up, fore + h), (fy, fz))]
            det = ay * bz - by * az
            du, df = (fy * bz - by * fz) / det, (ay * fz - fy * az) / det
            cap = max(1.0, abs(du) / 5, abs(df) / 5)                    # at most 5 degrees a step
            up, fore = up - du / cap, fore - df / cap
        return up, fore
    frames, arms = [], dict(arms0)                   # each frame's arm solve starts from the last
    for t in range(FOURS_FRAMES):
        rock = -POSE_ROCK * _eased(t, FOURS_FRAMES)                            # sign checked: hips go back
        w = pose(rock, arms0, foot)
        k = ends(w, [0, 0, 0])["l_femur"]
        root = [knee0[i] - k[i] for i in range(3)]                             # the knees stay planted
        for side in "lr":
            arms[side] = reach(rock, root, arms, side)
        w = pose(rock, arms, foot)
        e = ends(w, root)
        for n in ("l_femur", "r_femur", "l_tibia", "r_tibia"):
            assert abs(e[n][1]) < 0.6, (t, n, e[n])                            # knees and shins down
        for s in "lr":                                                         # hands planted (y, z exact;
            assert all(abs(e[s + "_foarm"][i] - wrist0[s][i]) < 0.6 for i in range(3)), (t, s, e[s + "_foarm"])  # x drifts a little)
        frames.append((root, fa.local_rotations(sk, rr, w)))
    k = (FOURS_FRAMES + 1) // 2                      # start rocked back (user): the cycle from its middle
    _save_frames(ctx, fa, FOURS_ANIM, frames[k:] + frames[:k])


def _ride(ctx):
    """dzbr.a (RIDE_ANIM): kneeling astride, rocking; RIDE_FRAMES frames."""
    import math
    fa, sk, idx, rr, world = _standing(ctx)
    names = [b[0] for b in sk]
    x, z = (1, 0, 0), (0, 0, 1)

    def pose(hip, knee, foot, arms_down=0.0, head_down=0.0):
        w = list(world)
        for n in ("hip", "chest", "head", "l_chest", "l_collar", "r_chest", "r_collar"):
            w[idx(n)] = fa._mul(fa.axis_angle(x, RIDE_LEAN), world[idx(n)])          # torso forward
        w[idx("head")] = fa._mul(fa.axis_angle(x, head_down), w[idx("head")])         # + = chin to chest
        for side in "lr":
            for n in ("_uparm", "_foarm", "_hand"):
                w[idx(side + n)] = fa._mul(fa.axis_angle(x, -(RIDE_ARMS - arms_down)), world[idx(side + n)])
        for side, out in (("l", -RIDE_SPREAD), ("r", RIDE_SPREAD)):                 # knees apart (checked: l -> +x)
            spread = fa.axis_angle(z, out)
            thigh = fa._mul(spread, fa.axis_angle(x, -hip))                          # forward-up
            shin = fa._mul(spread, fa.axis_angle(x, -(hip - knee)))                  # folded back under
            for n in ("_hip", "_femur"):
                w[idx(side + n)] = fa._mul(thigh, world[idx(side + n)])
            w[idx(side + "_tibia")] = fa._mul(shin, world[idx(side + "_tibia")])
            w[idx(side + "_foot")] = fa._mul(fa.axis_angle(x, foot), fa._mul(shin, world[idx(side + "_foot")]))
        return fa.local_rotations(sk, rr, w)

    def ends(local, root=(0.0, 0.0, 0.0)):
        return {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, list(root), local))}
    foot = _bisect(lambda f: ends(pose(RIDE_HIP, RIDE_KNEE, f))["l_tibia"][1]
                   - ends(pose(RIDE_HIP, RIDE_KNEE, f))["l_foot"][1], -120, 60)     # feet flat behind
    knee0 = ends(pose(RIDE_HIP, RIDE_KNEE, foot))["l_femur"]
    planted = [knee0[0], 0.0, knee0[2]]                                              # the left knee on the bed
    for name, arms_rock, head_rock in ((RIDE_ANIM, 0, 0), (COWGIRL_ANIM, COWGIRL_ARMS_ROCK, COWGIRL_HEAD_ROCK)):
        frames = []
        for t in range(RIDE_FRAMES):
            b = (1 - math.cos(2 * math.pi * t / RIDE_FRAMES)) / 2                    # 0 -> 1 -> 0, eased
            d = RIDE_ROCK * b                                                        # (the hips rise with d)
            local = pose(RIDE_HIP - d, RIDE_KNEE - d, foot, arms_rock * b, head_rock * b)   # shin direction unchanged
            k = ends(local)["l_femur"]
            root = [planted[i] - k[i] for i in range(3)]
            e = ends(local, root)
            for n in ("l_femur", "r_femur", "l_tibia", "r_tibia"):
                assert abs(e[n][1]) < 0.6, (t, n, e[n])                             # shins on the bed
            if t == RIDE_FRAMES // 2 and arms_rock:
                e0 = ends(pose(RIDE_HIP, RIDE_KNEE, foot), root)
                assert e["l_hand"][1] > e0["l_hand"][1], "arms not lower at the top"            # y down
            frames.append(([0.0, 0.0, 0.0], [root[0], -root[1], root[2]], local))
        out = fa.Anim(ctx.char_file("dzba.a"))
        out.frames = frames
        ctx.char_file(name.split(".")[0].lower() + ".a", out.build())
    # kneeling, rocking (KNEEL_*): the rest kneel tipped forward about the knee line
    local0 = pose(RIDE_HIP, RIDE_KNEE, foot)
    k = ends(local0)["l_femur"]
    root0 = [planted[i] - k[i] for i in range(3)]
    fk0 = fa.forward(sk, rr, root0, local0)
    W0 = [m for m, _, _ in fk0]
    knee = fk0[idx("l_femur")][2]
    keep = {idx(n) for n in ("l_tibia", "r_tibia", "l_foot", "r_foot")}
    frames = []
    for t in range(KNEEL_FRAMES):
        a = KNEEL_TILT + KNEEL_ROCK * (1 - math.cos(2 * math.pi * t / KNEEL_FRAMES)) / 2
        R = fa.axis_angle(x, a)                                                  # the sense RIDE_LEAN tips forward
        rel = fa._vec(R, [root0[i] - knee[i] for i in range(3)])
        rt = [knee[i] + rel[i] for i in range(3)]
        Wt = [m if i in keep else fa._mul(R, m) for i, m in enumerate(W0)]
        Wt[idx("head")] = world[idx("head")]                                    # head upright the whole time (user)
        local = fa.local_rotations(sk, rr, Wt)
        e = {names[i]: en for i, (_, _, en) in enumerate(fa.forward(sk, rr, rt, local))}
        for n in ("l_femur", "r_femur"):
            assert abs(e[n][1]) < 0.6, (t, n, e[n])                              # knees on the floor
        frames.append(([0.0, 0.0, 0.0], [rt[0], -rt[1], rt[2]], local))
    out = fa.Anim(ctx.char_file("dzba.a"))
    out.frames = frames
    ctx.char_file(KNEEL_ANIM.split(".")[0].lower() + ".a", out.build())


def _bend(ctx, name=EDGE_ANIM, nframes=EDGE_FRAMES, bend=EDGE_BEND, arms_down=EDGE_ARMS_DOWN):
    """dzbg.a (EDGE_ANIM): standing, knees bent EDGE_KNEE, bent EDGE_BEND forward at
    the hips, arms straight out past her head (level), rocking forward and back
    about the ankles by EDGE_ROCK; EDGE_FRAMES frames. The hands stay where frame 0
    has them (each arm re-bent by two-bone IK, elbows out and up)."""
    import math
    fa, sk, idx, rr, world = _standing(ctx)
    names = [b[0] for b in sk]
    x = (1, 0, 0)                                    # +angle about x: the top of an upright bone goes forward
    rr0, rp, rots = fa.Anim(ctx.char_file("bajb.a")).frames[0]
    root0 = [rp[0], -rp[1], rp[2]]

    def ends(W, root):
        return {names[i]: e for i, (_, _, e) in enumerate(fa.forward(sk, rr, list(root), fa.local_rotations(sk, rr, W)))}
    stand = ends(world, root0)
    w = list(world)
    for n in ("hip", "chest", "head", "l_chest", "l_collar", "r_chest", "r_collar"):
        w[idx(n)] = fa._mul(fa.axis_angle(x, bend), world[idx(n)])               # torso forward (90: level)
    for side in "lr":
        for n in ("_uparm", "_foarm", "_hand"):                                   # hanging -> straight forward
            w[idx(side + n)] = fa._mul(fa.axis_angle(x, -EDGE_ARMS), world[idx(side + n)])
        w[idx(side + "_femur")] = fa._mul(fa.axis_angle(x, -EDGE_KNEE / 2), world[idx(side + "_femur")])
        w[idx(side + "_tibia")] = fa._mul(fa.axis_angle(x, EDGE_KNEE / 2), world[idx(side + "_tibia")])
    e = ends(w, root0)
    ankle = lambda e: [(e["l_tibia"][k] + e["r_tibia"][k]) / 2 for k in range(3)]
    a0, a1 = ankle(stand), ankle(e)
    root = [root0[k] + a0[k] - a1[k] for k in range(3)]                           # ankles where she stood
    e = ends(w, root)
    fwd = 1 if e["l_femur"][2] > e["l_hip"][2] else -1                            # knees bend forward
    assert fwd * (e["head"][2] - e["hip"][2]) > 0, "torso bent backwards"
    assert bend != 90 or abs(e["head"][1] - e["hip"][1]) < 4, ("torso not level", e["head"], e["hip"])
    assert all(fwd * (e[s + "_hand"][2] - e["head"][2]) > 0 and abs(e[s + "_hand"][1] - e[s + "_uparm"][1]) < 2
               for s in "lr"), "arms not straight out past her head"
    # head: chin up, then turned to her right (-x; l -> +x) about the head bone's own line
    def signed(w, i, axis, angle, test):
        for sg in (1, -1):
            v = list(w)
            v[i] = fa._mul(fa.axis_angle(axis, sg * angle), w[i])
            if test(ends(v, root)):
                return v, sg
        raise AssertionError(names[i])
    h = idx("head")
    w, _ = signed(w, h, x, EDGE_HEAD_BACK, lambda en: en["head"][1] < e["head"][1] - 0.3)     # y down
    face_local = fa._vec(fa._t(world[h]), [0.0, 0.0, float(fwd)])     # where her face points, in the head's frame
    neck = fa._vec(w[h], [0, 0, -1])                                     # the head bone's line
    face = lambda v: fa._vec(v[h], face_local)
    turned = [list(w), list(w)]
    for k, sg in enumerate((1, -1)):
        turned[k][h] = fa._mul(fa.axis_angle(neck, sg * EDGE_HEAD_TURN), w[h])
    w = min(turned, key=lambda v: face(v)[0])                            # her right: face towards -x
    assert face(w)[0] < face(turned[0] if w is turned[1] else turned[1])[0]
    # arms down below level, and the sense that lowers them (for the rock)
    arm = [idx(sd + n) for sd in "lr" for n in ("_uparm", "_foarm", "_hand")]
    e1 = ends(w, root)
    down = next(sg for sg in (1, -1)
                if ends([fa._mul(fa.axis_angle(x, sg * 5), m) if i in arm else m for i, m in enumerate(w)], root)["l_hand"][1]
                > e1["l_hand"][1] + 0.1)
    w = [fa._mul(fa.axis_angle(x, down * arms_down), m) if i in arm else m for i, m in enumerate(w)]
    F0 = fa.forward(sk, rr, root, fa.local_rotations(sk, rr, w))
    wrist = {sd: F0[idx(sd + "_foarm")][2] for sd in "lr"}                        # the hands stay here
    blen = {n: math.dist(F0[idx(n)][1], F0[idx(n)][2]) for sd in "lr" for n in (sd + "_uparm", sd + "_foarm")}
    unit = lambda v: [c / math.sqrt(sum(q * q for q in v)) for c in v]
    dotp = lambda a, b: sum(a[k] * b[k] for k in range(3))
    bdir = lambda m: fa._vec(m, [0, 0, -1])

    def align(a, b):                                 # the smallest rotation turning direction a into b
        a, b = unit(a), unit(b)
        ax = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
        si = math.sqrt(dotp(ax, ax))
        return fa.axis_angle(ax, math.degrees(math.atan2(si, dotp(a, b)))) if si > 1e-9 else fa.euler_matrix(0, 0, 0)
    frames = []
    for t in range(nframes):
        b = (1 - math.cos(2 * math.pi * t / nframes)) / 2
        a = EDGE_ROCK * b                                                      # 0 -> ROCK -> 0, eased
        R = fa.axis_angle(x, a)
        Wt = [m if names[i] in ("l_foot", "r_foot") else fa._mul(R, m) for i, m in enumerate(w)]
        rel = fa._vec(R, [root[k] - a0[k] for k in range(3)])
        rt = [a0[k] + rel[k] for k in range(3)]
        Ft = fa.forward(sk, rr, rt, fa.local_rotations(sk, rr, Wt))
        for sd, out in (("l", 1), ("r", -1)):        # two-bone IK: shoulder -> elbow -> the fixed wrist
            u_, f_, hd = idx(sd + "_uparm"), idx(sd + "_foarm"), idx(sd + "_hand")
            S, T = Ft[u_][1], wrist[sd]
            L1, L2 = blen[sd + "_uparm"], blen[sd + "_foarm"]
            d = min(math.dist(S, T), L1 + L2 - 1e-6)
            u = unit([T[k] - S[k] for k in range(3)])
            P = unit([out, -1.0, 0.0])               # elbows out and up (y down)
            p = unit([P[k] - dotp(P, u) * u[k] for k in range(3)])
            a_ = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
            hh = math.sqrt(max(0.0, L1 * L1 - a_ * a_))
            E = [S[k] + a_ * u[k] + hh * p[k] for k in range(3)]
            Wt[u_] = fa._mul(align(bdir(Wt[u_]), [E[k] - S[k] for k in range(3)]), Wt[u_])
            Wt[f_] = fa._mul(align(bdir(Wt[f_]), [T[k] - E[k] for k in range(3)]), Wt[f_])
            Wt[hd] = w[hd]                           # the hand keeps its frame-0 angle
        et = ends(Wt, rt)
        for sd in "lr":
            assert math.dist(et[sd + "_foarm"], wrist[sd]) < 0.3, (t, sd, et[sd + "_foarm"], wrist[sd])   # hands fixed
        assert math.dist(ankle(et), a0) < 0.3, (t, ankle(et), a0)                 # feet planted
        if t == nframes // 2:
            assert fwd * (et["hip"][2] - e["hip"][2]) > 0, "rocks backwards first"
        frames.append(([0.0, 0.0, 0.0], [rt[0], -rt[1], rt[2]], fa.local_rotations(sk, rr, Wt)))
    out = fa.Anim(ctx.char_file("dzba.a"))
    out.frames = frames
    ctx.char_file(name.split(".")[0].lower() + ".a", out.build())


def apply(ctx):
    _on_back(ctx)
    _on_back(ctx, HEADREV_ANIM, HEADREV_ARMS, hip_lift=HEADREV_LIFT, head_down=True)
    _fours(ctx)
    _cloud_thrust(ctx)
    _cloud_pound(ctx)
    _cloud_spread(ctx)
    _cloud_buck(ctx)
    _cloud_stand(ctx, arms=STAND_ARMS_LR, elbow_in=STAND_ELBOW_IN)
    _cloud_stand(ctx, "ZCTI.tor", arms=STAND_ARMS_LR, elbow_in=STAND_ELBOW_IN, nframes=8)   # x2 (dates)
    for name, n in (("ZCTJ.tor", STAND_FRAMES), ("ZCTK.tor", 8)):       # Aerith's date (user: hands on her head)
        _cloud_stand(ctx, name, arms=AERITH_CLOUD_ARMS, arms_out=AERITH_CLOUD_IN, elbow_in=AERITH_CLOUD_ELBOW, nframes=n)
    _cloud_stand(ctx, CLOUD_EDGE, EDGE_CLOUD_ARMS, (EDGE_CLOUD_HIP, EDGE_CLOUD_KNEE))
    _cloud_stand(ctx, CLOUD_EDGE_FAST, EDGE_CLOUD_ARMS, (EDGE_CLOUD_HIP, EDGE_CLOUD_KNEE), EDGE_FRAMES_FAST)
    _cloud_stand(ctx, CLOUD_KOALA, KOALA_CLOUD_ARMS, elbow_in=KOALA_CLOUD_ELBOW, lean=KOALA_CLOUD_LEAN,
                 arms_out=KOALA_CLOUD_OUT)
    _bare_cloud(ctx)
    _ride(ctx)
    _bend(ctx)
    _bend(ctx, EDGE_ANIM_FAST, EDGE_FRAMES_FAST, EDGE_BEND - EDGE_FAST_BACK, EDGE_FAST_ARMS_DOWN)
    mesh = Walkmesh(ctx.field(LOBBY).section("walkmesh"))
    tri = mesh.find(*BACK_AT)
    assert tri is not None
    back = (*BACK_AT, mesh.height(tri, *BACK_AT), tri)
    _conference(ctx)
    _add_girls(ctx)
    _manager(ctx, back)
    _bed_depth(ctx)                                  # every copy of the room (and the mirror) inherits it
    base = ctx.field(ROOM).build()                   # before the visit edits: the tier copies start here
    _room(ctx, back, ROOM, [[] for _ in GIRLS])     # lounge room: the visit-mode edits, no scenes
    basic = {g["name"]: g["scene"] for g in GIRLS}
    for name, scenes, final in ((BASIC_ROOM, basic, FINAL), (CLOSE_ROOM, CLOSE, CLOSE_FINAL),
                                (DEVOTED_ROOM, DEVOTED, DEVOTED_FINAL)):
        assert set(scenes) == {g["name"] for g in GIRLS}, name
        ctx.new_field(name, base)
        _room(ctx, back, name, [scenes[g["name"]] for g in GIRLS], final)
        _dim(ctx, name)
    _lounge(ctx)

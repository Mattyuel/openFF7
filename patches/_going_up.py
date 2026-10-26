"""(user) Going up: the second parody film (684_going_up), in Shinra HQ's glass elevator (eleout, where the
Turks capture Cloud in the story). Cloud and Tifa step in, Elena follows and asks them to press up; the car
won't move, the door is stuck. Tifa: Elena is outnumbered; time for special training. Elena agrees (she
wants to: the film's consent beat), undresses, covers up, crawls over to Cloud; Cloud gets behind her; fade;
from then on he alternates between Elena (behind) and Tifa kneeling beside her (head), on Tifa's call.

The gameplay builds on Sector 7 Workout's (683): one prompt a rep at the pace's tier, plus HOLD prompts
(press, keep holding to the rep's end: double pay) and Tifa's "Switch!" ([MENU]: a hit switches cleanly
with a bonus, a miss switches and drops the pace). At the end the elevator finally moves: going up.
Data only."""

FIELD = "blackbg4"              # the set: a debug room only startmap leads to, replaced by a copy of the elevator
BASE = "eleout"                 # the glass elevator (its car and rails are background layers 1 / 2)
FLOOR = -1                      # the car's floor height
ARRIVE = (10, 30)               # (670's MAPJUMP)
FOCUS = (10, 30)                # the hidden player (the camera follows it)
ELENA_AT = (-20, 20)            # her root (hips) on all fours; she faces screen-left, her rear to Cloud
HEAD_SHIFT = (35, 28)           # Cloud's spot facing Tifa: this far (field x, y) from his spot behind Elena (right of
                                # her rear on screen, a little further back); Tifa kneels in front of it, facing him
CAM_NUDGE = 4                   # (user) Cloud this much nearer the camera in Tifa's turn (field units)
INTRO = {"cloud": (-55, 15), "tifa": (60, 70), "elena_from": (100, -180), "elena": (55, -10), "panel": (0, 60)}
CONSOLE = (0, 105)              # the car's control console (back left): Cloud faces it at the panel spot
# (no Director model: the car is tight; he films from outside, his lines are text)
MUSIC = 45                      # AKAO 10 index: RHYTHM, the Turks' Theme
PROMPT_Y = 30
LINE_Y = 168
SAY = 100

# the tiers: frames a rep (a prompt every 3 strokes of the 20 / 15 / 11 / 8-frame speeds), hits to step up
PERIODS = (60, 45, 33, 24)
HITS_UP = 3                     # (user: 50% shorter scenes; was 4)
HOLD_ODDS = 52                  # in 256, per rep from tier 1: a HOLD prompt
SWITCH_MIN, SWITCH_RANGE = 4, 3 # reps with one partner before Tifa calls "Switch!" (4..6)
TOTAL_REPS = 32                 # (user: 50% shorter; was 64)
PAY_HIT = 15                    # gil per hit x (tier + 1); a held one pays double
SWITCH_BONUS = 5                # (x PAY_HIT)

KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
SWITCH_KEY = (0x10, "{PURPLE}[MENU]{WHITE}")

# the intro: (speaker line, action after it or None)
INTRO_LINES = [
    ("Elena\n“Hold the door! ...Going up? Press\n the button for me, would you?”", "cloud_panel"),
    ("(Click. Click.)", None),
    ("Cloud\n“...It's not working.”", None),
    ("Elena\n“What? No, no, no... The door's\n stuck! I'm going to be late for\n the briefing!”", None),
    ("Tifa\n“Looks like you're outnumbered,\n rookie.”", None),
    ("Elena\n“Is that a threat?”", None),
    ("Tifa\n“It's an offer. Time for some...\n special training.”", None),
    ("Elena\n“S-special training?”", None),
    ("Tifa\n“Lose the uniform. Only if you\n want to.”", None),
    ("Elena\n“(She glances at Cloud, then at the\n camera.) ...I want to. Just don't\n tell Tseng.”", "undress"),
    ("Elena\n“D-don't stare!”", None),
    ("Tifa\n“On your hands and knees, rookie.\n Crawl over to Cloud.”", "crawl"),
    ("Elena\n“Y-yes, ma'am...”", None),
    ("Tifa\n“Cloud. Get behind her.”", "behind"),
]
# (user: more variety in the intros) intro line -> [(actor, gesture)] (`_gestures.ANIMS`; the clothed actors,
# not while they walk)
INTRO_GESTURES = {3: [("elena", "hop"), ("cloud", "shrug")], 4: [("tifa", "hips")], 5: [("elena", "chest")],
                  6: [("tifa", "lean")], 7: [("elena", "clasp")], 8: [("cloud", "lookaround")], 9: [("elena", "shrug")]}
HOW = ("Press the button shown in time. HOLD:\nkeep it held to the end. When Tifa\ncalls Switch!, press {PURPLE}[MENU]{WHITE} in time."
       "{NEW}With Tifa, a HOLD lasts until she taps\nout: let go the moment she does, or\nshe'll get mad.")

# lines at each tier reached the first time with that partner
LINES = {
    0: {1: ["Elena\n“Is this... standard training?”", "Tifa\n“Very standard. Relax.”"],
        2: ["Elena\n“Ah...! Sir... I mean, Cloud...”"],
        3: ["Tifa\n“Look at her go. A natural.”", "Elena\n“D-don't stop...!”"]},
    1: {1: ["Tifa\n“Mmm... my turn, rookie. Watch\n closely.”"],
        2: ["Elena\n“So that's how it's done...”"],
        3: ["Tifa\n“Mmph...!”"]},
}
SWITCH_CALL = ["Tifa\n“Switch! Her turn.”", "Tifa\n“Switch! Back to me.”"]
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (user) the squat sound, as 683's
CHAT_EVERY = 4                  # a chatter line every this many reps, when nobody's talking
# (user: a hold during head) with Tifa a HOLD lasts until she taps out after HOLD_MIN + random HOLD_RANGE
# frames; let go within LETGO = a hit, double pay plus HOLD_BONUS x (tier + 1); before = a miss; later = she's
# mad (MAD_PENALTY off, back to slow; at MAD_LIMIT she walks out). Results stay up RESULT_WAIT frames.
HOLD_MIN, HOLD_RANGE = 45, 90
LETGO = 30
HOLD_BONUS = 2
MAD_PENALTY = 10                # (x PAY_HIT gil)
MAD_LIMIT = 3
RESULT_WAIT = 50
# (user: variations) Cloud's pose alternates every STYLE_EVERY reps: behind Elena 0 right knee up / 1 his left
# (the camera's side); before Tifa 0 hands on her head / 1 hands behind his own head
STYLE_EVERY = 3                 # (user: transitions sooner; was 6)
STYLE_LINES = [[["Cloud\n“Switching legs.”"],
                ["Elena\n“W-what are you doing with your\n leg...? Ah... ahh...!”", "Cloud\n“Better angle.”"]],
               [["Tifa\n“(Mmph!)”", "Elena\n“Hands back on. Noted.”"],
                ["Elena\n“Look, no hands! Show-off.”"]]]
CHAT = [["Elena\n“Is this in the Turks' manual?”",
         "Tifa\n“Arch your back, rookie.”",
         "Elena\n“Tseng can never, EVER find out.”",
         "Tifa\n“You're doing great. Don't look\n at the camera.”",
         "Elena\n“Ah...! Professionalism... ah...”",
         "Tifa\n“Mm, she's a fast learner.”"],
        ["Elena\n“So THAT'S the technique...”",
         "Tifa\n“Mmh... mm!”",
         "Elena\n“Should I be writing this down?”",
         "Elena\n“I'm not jealous. I'm observing.”",
         "Cloud\n“Easy, Tifa.”",
         "Elena\n“How is she even breathing?”"]]
MISSES = [["Elena\n“Hey! Find the rhythm!”",
           "Tifa\n“Lost it! Slow and steady.”",
           "Elena\n“Was that... on purpose?”",
           "Tifa\n“Again. From the top.”"],
          ["Tifa\n“Mmph?! ...Slower!”",
           "Elena\n“Ha! Even the trainer fumbles.”",
           "Tifa\n“(Mm-mm.) Try again.”",
           "Elena\n“Rhythm, Cloud!”"]]
HOLDS = ["Tifa\n“Mmph...!”",
         "Elena\n“She's... she's taking all of it...”",
         "Cloud\n“Stay right there.”"]
CUES = ["Tifa\n“Mmph! (*tap tap tap*)”",
        "Tifa\n“Mm-mm! (*slaps his thigh*)”",
        "Tifa\n“(*tap tap*) MMPH!”"]
GOOD = ["Tifa\n“Hahh... good. You listen.”",
        "Tifa\n“Hah... hah... wow.”",
        "Elena\n“Taking notes... lots of notes.”"]
EARLY = ["Tifa\n“Hah... that's all? I could've gone\n longer.”",
         "Elena\n“Already? I'd have lasted longer.”"]
MAD = ["Tifa\n“*cough* When I tap, you LET GO,\n Cloud!”",
       "Tifa\n“Do that again and this training\n session is over.”"]
WALKOUT = ["Tifa\n“That's it. I'm out. Enjoy the ride,\n rookie.”",
           "(Tifa pries the doors open and climbs\n out of the car.)",
           "Elena\n“W-wait! Don't leave me alone with\n him!”",
           "Director\n“CUT! ...Somebody get that door open.”"]
HOLD_LABEL = "HOLD "
FINALE = ["(The car shudders... and starts to rise.)",
          "Elena\n“It's... going up.”",
          "Tifa\n“Special training complete, rookie.”",
          "Director\n“CUT! The Turks will never live\n that one down.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.”"

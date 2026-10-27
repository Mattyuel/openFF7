"""(user) Hostile Takeover: the fourth parody film (686_hostile), in the Shinra 66F boardroom. A board meeting:
Scarlet presides, Elena is the new intern who can't stop kissing up, and Cloud walks in from "Avalanche
Holdings" with a merger proposal. Shinra doesn't merge, Shinra acquires: so it's a hostile takeover. Then the
user's annotated sketch, by the table's front-left corner (everyone at entry scale 768: the table's top is then
at Cloud's hip): Scarlet on the table on her knees, chest down, her rear at its edge; Cloud on the floor bowing
into her, his face buried "there"; Elena reclining on her back under him, between his legs, face up to him,
literally sucking up. The swap: Elena on the table, Scarlet underneath ("if you want something done right").

Both of the room's camera angles, alternating every ANGLE_EVERY reps (user: "for fun"): the front view down
the table (blin66_6, set FIELD_A) and the overhead view (blin66_5, set FIELD_B), everyone on the same spots
(the overhead room is the front room turned a quarter: `to_b`, fitted on the chair squares). The shoot's
state crosses the jump in save bytes (`STATE`). Data only."""

FIELD_A, BASE_A = "blackbg5", "blin66_6"     # sets: debug rooms only startmap leads to, replaced by copies
FIELD_B, BASE_B = "blackbg8", "blin66_5"
# blin66_6 -> blin66_5 (fitted on the six chair squares: x5 = -y6 - 268, y5 = x6 - 1003; the floor 0 -> -383;
# a quarter turn: DIR + 64)
B_OFF = (-268, -1003, -383)
B_DIR = 64


def to_b(x, y, z=0):
    return -y + B_OFF[0], x + B_OFF[1], z + B_OFF[2]


# blin66_6 coordinates
TABLE_X, TABLE_Z = -130, 50     # the table top's left edge (field x) and height (the table isn't walkmesh;
                                # fitted on the background)
SPOT_Y = -150                   # the scene's line across the table's front-left (user, since: away from the camera;
                                # was -190: she was off the table's corner)
ENTRY_OUT = 8                   # the girl on the table: her entry point this far onto the table from its left edge
                                # (user, since: right, onto the table; was 4)
BED_GAP = 16                    # 670's edge: the girl stands this far back from the bed's foot (whitebg1),
CLOUD_GAP = 14                  # Cloud this far behind her,
KISS_GAP = 27                   # Elena's root this far behind his (her face at his rear: 670's head pose)
SIT_IN = 24                     # Scarlet sitting on the table's edge: her hips this far onto it
SIT_Y = -232                    # ... nearer the front than the others
ARRIVE = (-60, -320)            # 670's MAPJUMP into FIELD_A
FOCUS = (-165, -215)            # the hidden player (the camera follows it), both angles
INTRO = {"scarlet": (-150, -235), "elena": (-205, -175), "cloud_from": (0, -330), "cloud": (-110, -300)}
MUSIC = 45                      # AKAO 10 index: RHYTHM, the Turks' Theme (Shinra business)
PROMPT_Y = 30
LINE_Y = 168
SAY = 100

PERIODS = (60, 45, 33, 24)
HITS_UP = 3
HOLD_ODDS = 52
SWITCH_MIN, SWITCH_RANGE = 4, 3
TOTAL_REPS = 32
PAY_HIT = 15
SWITCH_BONUS = 5
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (user) 683's squat sound
CHAT_EVERY = 4
HOLD_MIN, HOLD_RANGE = 45, 90   # with Scarlet: frames until she slaps the table
LETGO = 30
HOLD_BONUS = 2
MAD_PENALTY = 10
MAD_LIMIT = 3
RESULT_WAIT = 50
STYLE_EVERY = 3
ANGLE_EVERY = 5                 # reps between the camera switches

KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
SWITCH_KEY = (0x10, "{PURPLE}[MENU]{WHITE}")
HOLD_LABEL = "HOLD "

INTRO_LINES = [
    ("Scarlet\n“Kyahaha! This board meeting is now\n in session. Item one: quarterly\n profits are DOWN.”", None),
    ("Elena\n“Brilliant observation, ma'am! May I\n say your hair looks very... executive\n today?”", None),
    ("Scarlet\n“You may. Item two: the new intern.\n Item three...”", "walk"),
    ("Cloud\n“Avalanche Holdings. I'm here about\n the merger.”", None),
    ("Scarlet\n“Merger? Shinra doesn't MERGE.\n Shinra ACQUIRES.”", None),
    ("Cloud\n“Then call it a hostile takeover.”", None),
    ("Elena\n“Ma'am, he's very... hostile. Should\n I call security?”", None),
    ("Scarlet\n“Kyahaha! No. I want to see how\n hard he negotiates. On the table.”", None),
    ("Elena\n“Taking minutes, ma'am!”", None),
    ("Scarlet\n“Put the pen down, intern. You'll be\n supporting the deal... from below.”", None),
    ("Elena\n“From below. Understood, ma'am! I've\n been sucking up my whole career!”", None),
    ("Cloud\n“...Let's dig into the details.”", "scene"),
    ("Scarlet\n“Ohh...! The board will now review\n your... proposal.”", None),
    ("Elena\n“(Mmph!) ...Supporting, ma'am!”", None),
]
# (user: more variety in the intros) intro line -> [(actor, gesture)] (`_gestures.ANIMS`)
INTRO_GESTURES = {0: [("scarlet", "hip")], 1: [("elena", "clasp")], 4: [("scarlet", "laugh")], 5: [("cloud", "point")],
                  6: [("elena", "hop")], 7: [("scarlet", "hip")], 8: [("elena", "chest")], 10: [("elena", "shrug")],
                  11: [("cloud", "nod")]}
HOW = ("Press the button shown in time. HOLD:\nkeep it held to the end. When Scarlet\ncalls a switch, press {PURPLE}[MENU]{WHITE} in time."
       "{NEW}With Elena underneath, a HOLD lasts\nuntil she taps out: let go the moment\nshe does, or she'll quit.")

# P 1 = Scarlet on the table, Cloud's face in her, Elena underneath; P 0 = Elena on the table, Scarlet underneath
LINES = {
    1: {1: ["Scarlet\n“Mm... a thorough audit.”", "Elena\n“(Mmph) ...The view down here is...\n humbling, ma'am.”"],
        2: ["Scarlet\n“Deeper into the numbers! Ah...!”"],
        3: ["Scarlet\n“Kyahaha! Ah...! ACQUIRE me!”", "Elena\n“(Mmph!) I'd like a raise, ma'am!”"]},
    0: {1: ["Elena\n“A-am I being promoted?!”", "Scarlet\n“Don't get comfortable, intern.\n (Mmph.)”"],
        2: ["Elena\n“Ah...! Sir... I mean, consultant...!”"],
        3: ["Elena\n“Best... performance review...\n EVER!”", "Scarlet\n“(Mmph!) ...She's a natural. I hate\n it.”"]},
}
SWITCH_CALL = ["Scarlet\n“Enough! Intern, back underneath.\n The boss is back on the table.”",
               "Scarlet\n“Up, intern! If you want something\n done right, you do it yourself.”"]
CHAT = [["Scarlet\n“(Mmph...) Time is money!”",
         "Elena\n“Ma'am, is this going on my\n record?”",
         "Scarlet\n“I'm docking your pay for enjoying\n that, intern.”",
         "Elena\n“Synergy... so much synergy...”",
         "Elena\n“Ma'am, you're very good at...\n managing.”",
         "Cloud\n“(Mmph.) Your intern has potential.”"],
        ["Scarlet\n“Mm... keep the numbers going UP!”",
         "Elena\n“(Mmph... ma'am... mmph...)”",
         "Scarlet\n“Intern! More support!”",
         "Elena\n“(I'm... networking...!)”",
         "Scarlet\n“Now THIS is a leveraged buyout!”",
         "Cloud\n“(Mmph.) ...Is she okay down there?”"]]
MISSES = [["Scarlet\n“(Mmph?!) That's coming out of your\n bonus.”",
           "Elena\n“Ah! Rhythm, sir!”",
           "Scarlet\n“Sloppy. Very Avalanche.”",
           "Elena\n“Was that... a pay cut?”"],
          ["Scarlet\n“Unacceptable! Again!”",
           "Elena\n“(Mmph?!) ...He moved!”",
           "Scarlet\n“Is that how you close a deal?!”",
           "Elena\n“(Ow. My nose.)”"]]
# (user: variations) Cloud's style: 0 his hands on her hips, 1 flat on the table either side of her
STYLE_LINES = [[["Scarlet\n“(Mmph.) Hands where I can see\n them, consultant.”"],
                ["Elena\n“Sir, your hands are on the minutes!”"]],
               [["Scarlet\n“Mm... grip the assets. Yes.”"],
                ["Scarlet\n“Hands on MY table? ...Bold.”"]]]
HOLDS = ["Elena\n“(Mmmph...!)”",
         "Scarlet\n“Hold her there. Show some\n commitment, intern!”",
         "Cloud\n“Stay put.”"]
CUES = ["Elena\n“(Mmph! *taps his leg*)”",
        "Elena\n“(*tap tap tap*) MMPH!”",
        "Elena\n“(Mm-mm! *slaps the floor*)”"]
GOOD = ["Elena\n“Hahh... hah... I'm putting that on\n my résumé.”",
        "Scarlet\n“Kyahaha... the intern survives.”",
        "Elena\n“*gasp* ...Thank you for the\n opportunity, sir.”"]
EARLY = ["Elena\n“Hah... that's it? I can take more\n than that!”",
         "Scarlet\n“Already? Interns these days.”"]
MAD = ["Elena\n“*cough* When I tap, you LET GO!\n I'm telling HR!”",
       "Elena\n“One more time and I'm filing a\n complaint with the Turks!”"]
WALKOUT = ["Elena\n“That's it. I QUIT! Do your own\n filing!”",
           "(Elena storms out of the boardroom.)",
           "Scarlet\n“Kyahaha! Interns. So fragile.”",
           "Director\n“CUT! ...Somebody get her a coffee.”"]
FINALE = ["Scarlet\n“Hahh... the board... approves the\n takeover.”",
          "Elena\n“Ma'am! Do I get a promotion?”",
          "Scarlet\n“You get a nose job. Kyahaha!”",
          "Director\n“CUT! That's a wrap! Fantastic\n synergy, people.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.”"

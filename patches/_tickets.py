"""(user) Tickets, please!: the third parody film (685_tickets), on the Sector 7 train (tin_2's carriage). Cloud,
the ticket inspector, comes down the aisle; Tifa and Jessie, sitting side by side on the left bench, are brats:
no tickets, and they'll only show him theirs if he shows them his. He doesn't need a ticket; no, they mean
*it*. Fade: Cloud in his alt model; they tease each other and compliment him; time to show him theirs. Fade to
the position (user's sketch): both across the left bench, Tifa on all fours further back with her rear to
the aisle, Jessie on her back nearer the camera with her head over the seat's edge (upside down) and her legs
up the window; Cloud stands in the aisle and alternates between them (behind Tifa / Jessie's head).

The gameplay is Going up's (684) with everything since: prompts by tier, HOLD prompts, the switch call ("My
turn!"), chatter and miss lines, the hit sound, Cloud's pose styles, and with Jessie a HOLD that lasts until
she taps out (late = she's mad, three times = she walks off). Data only."""

FIELD = "blackbg6"              # the set: a debug room only startmap leads to, replaced by a copy of the carriage
BASE = "tin_2"                  # the Sector 7 train's carriage (user: its seats are the most visible)
FLOOR, SEAT = -53, -24          # the aisle's floor / the benches' top (walkmesh z)
EDGE_X = -69                    # the left bench's aisle edge (field x; the bench runs along y, x -112..-69)
TIFA_Y, JESSIE_Y = -205, -262   # where each lies across the bench (field y: smaller = nearer the camera)
TIFA_ENTRY_X = -64              # her rear's point this far out (just past the edge)
JESSIE_NECK_X = -71             # her neck joint here: her head hangs over the edge
SIT_X = -92                     # the intro: both sitting here (their hips over the bench), facing the aisle
ARRIVE = (-30, -150)            # (670's MAPJUMP; the init moves the hidden player to FOCUS)
FOCUS = (-48, -215)             # the hidden player (the camera follows it)
CLOUD_FROM, CLOUD_TO = (0, 150), (-12, -232)    # the inspector walks down the aisle to them (user: stopped too
                                                # close: was x -38, the girls' knees reach ~-70)
MUSIC = 45                      # AKAO 10 index: RHYTHM (the Turks' Theme, as Going up)
PROMPT_Y = 30
LINE_Y = 168
SAY = 100

# the poses: Cloud's member tip DEPTH inside at the deepest, travelling STROKE (model units); his stance
DEPTH, STROKE = 1.0, 1.8
SINK_SPARE = 0.3                # Tifa sinks into the cushion until his level tip reaches her with this to spare
TIFA_RAISE = 8                  # (user) ...then she's drawn this much higher (Cloud and Jessie unchanged): room for
TIFA_SPREAD = 18                # Jessie under her, her knees this many degrees further apart (each)
STANCE_T, STANCE_J = 1.0, 3.8   # his feet this far out (behind Tifa / at Jessie's head: a wide, low sumo stance: the
                                # bench is low, his hips sink ~5)
LEAN_T, LEAN_J = 8, 22          # his upper body leaning forward (degrees)
FOOT_UP = (2.2, 1.6)            # (style 1 behind Tifa) his left foot up on the seat: out, then forward past its edge
LEGS_SPREAD = 14                # Jessie's straight legs up the window, this far apart (degrees each)

PERIODS = (60, 45, 33, 24)      # frames a rep: 3 strokes of the 20 / 15 / 11 / 8-frame speeds
HITS_UP = 3                     # (user: 50% shorter scenes; was 4)
HOLD_ODDS = 52                  # in 256, per rep from tier 1: a HOLD prompt
SWITCH_MIN, SWITCH_RANGE = 4, 3
TOTAL_REPS = 32                 # (user: 50% shorter; was 64)
PAY_HIT = 15
SWITCH_BONUS = 5
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (user) 683's squat sound, as Going up
CHAT_EVERY = 4
HOLD_MIN, HOLD_RANGE = 45, 90   # with Jessie: frames until she taps out
LETGO = 30
HOLD_BONUS = 2
MAD_PENALTY = 10
MAD_LIMIT = 3
RESULT_WAIT = 50
STYLE_EVERY = 3                 # (user: transitions sooner; was 6)

KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
SWITCH_KEY = (0x10, "{PURPLE}[MENU]{WHITE}")
HOLD_LABEL = "HOLD "

# the intro: (line, action after it): walk (Cloud down the aisle), bare (fade: Cloud's alt model), scene (fade:
# the position)
INTRO_LINES = [
    ("Cloud\n“Tickets, please.”", None),
    ("Jessie\n“Tickets? Hmm... I don't think we have\n any. Do we, Tifa?”", None),
    ("Tifa\n“Nope. Not a single one.\n (giggle)”", None),
    ("Cloud\n“Everyone on this train needs a\n ticket. Show them to me.”", None),
    ("Jessie\n“Make us.”", None),
    ("Tifa\n“Ooh, he's getting serious. I like\n serious.”", None),
    ("Jessie\n“Tell you what, inspector. We'll show\n you ours... if you show us yours.”", None),
    ("Cloud\n“I work here. I don't need a ticket.”", None),
    ("Tifa\n“Not your ticket, silly.”", None),
    ("Jessie\n“Show us... *it*.”", None),
    ("Cloud\n“......”", "bare"),
    ("Jessie\n“Oh. OH. Tifa, are you seeing this?”", None),
    ("Tifa\n“Hard to miss, Jessie. Close your\n mouth, you're drooling.”", None),
    ("Jessie\n“Says the girl who hasn't blinked\n in a minute.”", None),
    ("Tifa\n“I'm just... inspecting it. Fair's\n fair.”", None),
    ("Jessie\n“Very impressive, inspector.\n Definitely first class.”", None),
    ("Tifa\n“Mm. All aboard.”", None),
    ("Jessie\n“Okay, okay. A deal's a deal. Time\n to show you ours.”", None),
    ("Tifa\n“But you'll have to punch both our\n tickets, inspector.”", None),
    ("Cloud\n“...That's not how tickets work.”", None),
    ("Jessie\n“It is today.”", "scene"),
]
# (user: more variety in the intros) intro line -> [(actor, gesture)] (`_gestures.ANIMS`; the girls' seated
# copies; "cloudB" = Cloud in his alt model, after "bare")
# (user: Jessie's seated arm gestures looked bad on her model) she only turns / nods her head
INTRO_GESTURES = {1: [("jessie", "lookl")], 2: [("tifa", "lean")], 3: [("cloud", "point")], 4: [("jessie", "nod")],
                  5: [("tifa", "hips")], 6: [("jessie", "lookr")], 7: [("cloud", "formal")], 8: [("tifa", "think")],
                  11: [("jessie", "lookl")], 12: [("tifa", "lean")], 13: [("jessie", "lookr")], 14: [("tifa", "think")],
                  15: [("jessie", "nod"), ("cloudB", "coy")], 16: [("tifa", "hips")], 19: [("cloudB", "shakehead")]}
HOW = ("Press the button shown in time. HOLD:\nkeep it held to the end. When they\ncall My turn!, press {PURPLE}[MENU]{WHITE} in time."
       "{NEW}With Jessie, a HOLD lasts until she taps\nout: let go the moment she does, or\nshe'll get mad.")

# lines at each tier reached the first time with that partner (0 Tifa behind, 1 Jessie's head)
LINES = {
    0: {1: ["Tifa\n“Mmh... checking it thoroughly,\n are we?”", "Jessie\n“Hey, no skipping the line!”"],
        2: ["Tifa\n“Ah...! Is this... standard\n procedure?”"],
        3: ["Tifa\n“Don't stop... punch it...!”", "Jessie\n“Wow. First class service.”"]},
    1: {1: ["Jessie\n“(Mmph!) ...The view's different\n from down here.”", "Tifa\n“Look at her. Hanging on every...\n inch.”"],
        2: ["Tifa\n“Easy, she's not used to the\n express service.”"],
        3: ["Jessie\n“(Mmmph!!)”", "Tifa\n“All the way to the end of the line!”"]},
}
SWITCH_CALL = ["Jessie\n“My turn, inspector! My ticket\n needs punching too!”",
               "Tifa\n“Hey! Don't forget my ticket!”"]
CHAT = [["Jessie\n“Hurry up back there, I'm next!”",
         "Tifa\n“Mm... you're good at your job.”",
         "Jessie\n“Best. Train ride. Ever.”",
         "Tifa\n“Jessie, stop staring.”",
         "Jessie\n“I'm taking notes. For... safety.”",
         "Tifa\n“Harder, inspector!”"],
        ["Tifa\n“Don't hog him, Jessie!”",
         "Jessie\n“(Mmh... mm-hmm!)”",
         "Tifa\n“Her legs are shaking. Cute.”",
         "Tifa\n“You look good upside down, Jess.”",
         "Jessie\n“(Mmph... mm!)”",
         "Cloud\n“Ticket... validated.”"]]
MISSES = [["Tifa\n“Hey! You lost your place!”",
           "Jessie\n“Ha! Missed a stop!”",
           "Tifa\n“Slow down... find the rhythm.”",
           "Jessie\n“Smooth, inspector. Real smooth.”"],
          ["Jessie\n“(Mmph?!)”",
           "Tifa\n“Careful! She's upside down!”",
           "Jessie\n“(Mm-mm!) ...Again.”",
           "Tifa\n“Off the rails, inspector.”"]]
# (user: variations) Cloud's style: behind Tifa 0 both feet on the floor / 1 his left foot up on the seat; at
# Jessie's head 0 hands on her shoulders / 1 hands behind his head
STYLE_LINES = [[["Tifa\n“Both feet on the floor? Boring.”"],
                ["Jessie\n“Whoa, he's putting his foot up\n on the seat!”", "Tifa\n“Feet off the seats, inspector...\n ah...!”"]],
               [["Tifa\n“Hands back on her, inspector.”"],
                ["Tifa\n“No hands? Show-off.”"]]]
HOLDS = ["Jessie\n“(Mmmph...!)”",
         "Tifa\n“Hold her there... she can take it.”",
         "Cloud\n“Stay put.”"]
CUES = ["Jessie\n“(Mmph! *slaps the seat*)”",
        "Jessie\n“(*tap tap tap*) MMPH!”",
        "Jessie\n“(Mm-mm! *kicks her legs*)”"]
GOOD = ["Jessie\n“Hahh... hah... wow. Okay. Wow.”",
        "Tifa\n“Good inspector. You listen.”",
        "Jessie\n“*gasp* ...Again. Later. Maybe.”"]
EARLY = ["Jessie\n“Hah... that's it? I'm tougher than\n that.”",
         "Tifa\n“Already? She wasn't even tapping.”"]
MAD = ["Jessie\n“*cough* When I tap, you LET GO!”",
       "Jessie\n“Do that again and I'm reporting you\n to the railway!”"]
WALKOUT = ["Jessie\n“That's it! I'm getting off at the\n next stop!”",
           "(Jessie storms off down the carriage.)",
           "Tifa\n“...More tickets for me, then.”",
           "Director\n“CUT! ...Somebody go after her.”"]
FINALE = ["(The train pulls into the station.)",
          "Jessie\n“Next stop... wow.”",
          "Tifa\n“All our tickets punched, inspector?”",
          "Cloud\n“...All of them.”",
          "Director\n“CUT! That's a wrap! ...Nobody sit\n on that bench.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.”"

"""(user) Besties: the fifth film (687_besties), Cloud, Tifa and Aerith in Gast's house in Icicle Inn (snmayor), on
the bed on the lower floor (where the Ifalna and Professor Gast videos usually play). A sensual, sincere scene:
the three of them bond, compliment each other openly, offer positions and keep trying new things. Aerith's
"too much" roleplay (her best friend's boyfriend: a soap opera none of them can play with a straight face) runs
through it; when an experiment doesn't work they laugh and try something else; it ends with everyone climaxing
together (how well depends on the player's rhythm), then the three of them, close, in the quiet.

Tifa and Aerith start in their Wall Market dresses (user), the models Corneo's mansion uses.

Structure: the intro (dresses, a heart-to-heart on the bed, the roleplay, undressing), then SEGMENTS: each a
fixed REPS prompts at the pace of the tiers (fixed length, user: progression by performance, not by grinding);
between segments one of them offers what's next: the real one or a silly experiment that goes wrong (a short
staged gag) before they carry on. The finale's FINISH prompts and the whole run's hits decide the climax.
Data only."""

FIELD = "blackbgh"              # the set: a debug room (only blackbgi leads there, itself only from startmap), a copy
BASE = "snmayor"                # Gast's house
BED = ((132, 532), (214, 572), (149, 716), (67, 675))    # the bed's walkable top: foot A B, head C D
BED_Z = 47
CARPET = (-20, 610)             # the rug left of the bed: where the kneeling segment happens
STAIRS_FOOT = (-60, 520)        # the intro: they come in from the stairs' foot
ARRIVE = (-20, 600)
MUSIC = 49                      # AKAO 10 index: DATE (the Gold Saucer date's theme: sweet)
PROMPT_Y = 30
LINE_Y = 168
SAY = 110

PERIODS = (60, 45, 33, 24)      # a rep: 3 strokes of the 20 / 15 / 11 / 8-frame speeds
HITS_UP = 3
REPS = 10                       # prompts a segment (fixed length)
FINISH = 6                      # the finale's quick prompts (at the top pace)
PAY_HIT = 12
HOLD_ODDS = 52                  # the kneeling segment: a HOLD now and then, held until she taps out
HOLD_MIN, HOLD_RANGE, LETGO = 45, 90, 30
SWITCH_AT = (4, 7)              # two-partner segments: the "my turn" calls after these reps
CHAT_EVERY = 3
RESULT_WAIT = 50
# the climax by the run's score (hits + 2 x finale hits): at least SCORE_GREAT / SCORE_GOOD, else the okay one
SCORE_GREAT, SCORE_GOOD = 52, 34
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")

KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
SWITCH_KEY = (0x10, "{PURPLE}[MENU]{WHITE}")
HOLD_LABEL = "HOLD "

# the intro: (line, action) actions: tifa_in / aerith_in (walk from the stairs), gesture_t / gesture_a <anim> (a
# dress anim once), sit (both sit on the bed's edge, Cloud between them), bare (fade: undressed, standing)
INTRO = [
    ("(Snow taps at the windows of Gast's old house. Down the stairs\n come two familiar dresses.)", "walk_in"),
    ("Aerith\n“Ta-da! Remember these? Wall Market's\n finest.”", ("gesture_a", "DADD")),
    ("Tifa\n“I can't believe we kept them. Do they\n still... look okay?”", ("gesture_t", "APGC")),
    ("Cloud\n“...You both look incredible.”", None),
    ("Aerith\n“Hear that, Tifa? 'Incredible.' He used\n a whole adjective.”", ("gesture_a", "DDFA")),
    ("Tifa\n“Aerith!”", ("gesture_t", "CXHB")),
    ("Aerith\n“Come sit. Both of you.”", "sit"),
    ("Tifa\n“It's strange... a year ago I'd never have\n said this out loud. But I love you.\n Both of you.”", None),
    ("Aerith\n“Mm. Me too. You're my best friend,\n Tifa. And Cloud is... Cloud.”", None),
    ("Cloud\n“I've never felt this safe with anyone.\n Either of you.”", None),
    ("Aerith\n“Okay, before we all start crying... I\n have an idea. A game.”", None),
    ("Tifa\n“Oh no. That's your 'trouble' voice.”", None),
    ("Aerith\n“Roleplay! I'm your best friend. Cloud\n is YOUR boyfriend. And I've had a\n secret crush on him for years...”", None),
    ("Tifa\n“That's... a little close to home?”", None),
    ("Aerith\n“That's what makes it naughty! Ahem.\n 'Oh, Cloud... Tifa must never, EVER\n find out about us...'”", None),
    ("Tifa\n“'Aerith! How COULD you! With MY\n boyfriend!' ...Oh gods. I can't say that\n with a straight face.”", None),
    ("Cloud\n“'...It's not what it looks like.'”", None),
    ("Aerith\n“Pfft-! 'Not what it looks like'? Cloud,\n you're not even undressed yet!”", None),
    ("Tifa\n“This is way too much. ...I love it.”", None),
    ("Aerith\n“Then let's fix the 'not undressed'\n part.”", "bare"),
    ("Tifa\n“...Okay. Wow. Aerith, you're gorgeous.”", None),
    ("Aerith\n“Says the woman with THOSE. Cloud,\n back me up.”", None),
    ("Cloud\n“You're both... perfect. I don't know\n where to look.”", None),
    ("Aerith\n“Start with me. Your girlfriend's best\n friend. Very forbidden.”", None),
]
HOW = ("Press the button shown in time with them.\nEvery position lasts the same while; the\nbetter your rhythm, the better the ending."
       "{NEW}In the kneeling part, a HOLD lasts until\nshe taps out: let go the moment she does.\nWhen they call My turn!, press {PURPLE}[MENU]{WHITE}.")

# the segments, in order: (key, title, setup lines, chatter, misses, tier lines {tier: lines})
SEGMENTS = [
    dict(key="kiss", title="Aerith on her back; Tifa beside her, kissing her",
         setup=["Aerith\n“'Oh no... my best friend's right here.\n She'll see everything...'”",
                "Tifa\n“'I'm not watching. I'm supervising.'\n ...Hi, you.”",
                "Aerith\n“Mmm... kissing me is cheating.”"],
         chat=["Tifa\n“You're so beautiful like this, Aerith.”",
               "Aerith\n“Your lips are so soft, Tifa...”",
               "Aerith\n“Cloud... slower. I want to remember\n this.”",
               "Tifa\n“Look at her face, Cloud. Look what\n you're doing to her.”",
               "Aerith\n“'Tifa must never know...' (giggle) She's\n literally holding my hand.”",
               "Cloud\n“You feel amazing, Aerith.”"],
         miss=["Aerith\n“Ow, hair! My hair!”",
               "Tifa\n“Elbow, Cloud. ELBOW.”",
               "Aerith\n“(giggle) Rhythm, lover boy.”",
               "Tifa\n“Slow down... there. Like that.”"],
         tiers={2: ["Aerith\n“Ah...! Don't stop... either of you...”"],
                3: ["Tifa\n“She's shaking. Keep going, Cloud.”"]}),
    dict(key="ride", title="Tifa riding Cloud; Aerith beside them",
         setup=["Tifa\n“'If my best friend gets you, I get you\n too. That's only fair.'”",
                "Aerith\n“'This is a betrayal!' ...Of what? I've\n lost the plot.”"],
         chat=["Aerith\n“Tifa, you look like a goddess up there.”",
               "Tifa\n“Ah... Cloud... you feel so good inside\n me.”",
               "Aerith\n“Can I...? (She kisses Tifa's shoulder.)”",
               "Tifa\n“Don't stop, either of you...”",
               "Cloud\n“Tifa... you're incredible.”",
               "Aerith\n“'My best friend's boyfriend is SO good\n at this.' ...Sorry. Still in character.”"],
         miss=["Tifa\n“Whoa-! This bed is too narrow!”",
               "Aerith\n“(giggle) Hold on to something!”",
               "Tifa\n“Oops. Slipped. Again.”",
               "Cloud\n“...Sorry.”"],
         tiers={2: ["Tifa\n“Mmh... Aerith, kiss me...”"],
                3: ["Aerith\n“Look at her go! Tifa!”"]}),
    dict(key="taste", title="Tifa on all fours with her face between Aerith's legs; Cloud behind Tifa",
         setup=["Aerith\n“'Your girlfriend is... oh. Oh, she's\n GOOD at this.'”",
                "Tifa\n“(Mmh!) Stay in character, Aerith.”",
                "Aerith\n“I CAN'T, Tifa, not when you do THAT-”"],
         chat=["Aerith\n“Tifa... your mouth... ahh...”",
               "Tifa\n“(Mmm...)”",
               "Cloud\n“Tifa... you feel unbelievable.”",
               "Aerith\n“Look at us. This is the best idea I've\n ever had.”",
               "Aerith\n“Cloud, look at her. Isn't she perfect?”",
               "Tifa\n“(Mmh!) ...I love you both. Don't stop.”"],
         miss=["Aerith\n“Ah-! Gentle! Gentle!”",
               "Tifa\n“Sorry!”",
               "Aerith\n“(laughing) The bed squeaked SO loud.”",
               "Tifa\n“Cloud, easy... there.”"],
         tiers={2: ["Aerith\n“Tifa, I'm... I'm close...”"],
                3: ["Tifa\n“(Mmmh!!)”"]}),
    dict(key="share", title="Both kneeling for Cloud, taking turns",
         setup=["Aerith\n“'Let's share him. Best friends share\n everything.'”",
                "Tifa\n“That line was SO much. ...Okay, it was a\n little hot.”"],
         chat=["Tifa\n“Mmh... (She looks up at him.)”",
               "Aerith\n“You taste... mm. Perfect.”",
               "Tifa\n“Aerith, your hair's so soft...”",
               "Aerith\n“Tifa, you're hogging him. (giggle)”",
               "Cloud\n“You two... are amazing.”",
               "Tifa\n“Look at his face. I love that face.”"],
         miss=["Tifa\n“(Mmph?!) ...Oops.”",
               "Aerith\n“Ow, nose!”",
               "Tifa\n“Whose turn is it? I lost track!”",
               "Aerith\n“(giggle) Rhythm!”"],
         tiers={2: ["Aerith\n“Mmh... (She holds Tifa's hand.)”"],
                3: ["Tifa\n“He's close. I can tell.”"]}),
    dict(key="stack", title="Tifa on her back, Aerith over her; Cloud with both",
         setup=["Tifa\n“Aerith... you're so close. I can feel\n your heartbeat.”",
                "Aerith\n“'Your boyfriend, your best friend...\n and you.' ...Okay. The roleplay's over.\n This is just us.”"],
         chat=["Tifa\n“Kiss me, Aerith.”",
               "Aerith\n“Tifa... you're shaking.”",
               "Cloud\n“I love you. Both of you.”",
               "Tifa\n“Don't let go of my hand.”",
               "Aerith\n“Cloud... you're so good to us.”",
               "Tifa\n“This is... everything.”"],
         miss=["Aerith\n“Wrong one! (giggle) ...Actually, no,\n that's fine too.”",
               "Tifa\n“Ah! Knee! My knee!”",
               "Aerith\n“The bed! The bed's moving!”",
               "Tifa\n“(laughing) We're going to break Gast's\n bed.”"],
         tiers={2: ["Tifa\n“Cloud... Aerith... I'm close...”"],
                3: ["Aerith\n“Together... all of us, together...”"]}),
]
# between segments: (who asks, the question, the real choice, the experiment, the gag's lines)
OFFERS = [
    ("Tifa\n“My turn... I want to ride you. Unless\n someone has a better idea?”", "Let Tifa ride.", "Try 'the wheelbarrow'.",
     ["(Cloud lifts Aerith's legs. Aerith walks two steps on her hands,\n wobbles, and folds into a giggling heap on the rug.)",
      "Aerith\n“I'm fine! I'm fine. That was terrible.”",
      "Tifa\n“Ten points for enthusiasm.”"]),
    ("Aerith\n“Ooh, I read about something. Tifa, on\n your hands and knees. I'll lie in front\n of you...”", "Do Aerith's idea.", "Try 'the pretzel'.",
     ["(Three people. Six legs. One single bed. Somebody's foot ends up\n in somebody's ear.)",
      "Tifa\n“Whose foot is this?!”",
      "Aerith\n“Mine! Sorry! Nobody move!”",
      "Cloud\n“...I can't feel my arm.”"]),
    ("Tifa\n“Can we... both take care of you now?\n Together?”", "Kneel together.", "Try 'the human chair'.",
     ["(Aerith sits on Cloud. Tifa sits on Aerith. Cloud sits on nothing.\n The chair lasts exactly one second.)",
      "Aerith\n“Physics! We forgot about physics!”",
      "Tifa\n“I've never laughed this hard naked.”"]),
    ("Aerith\n“For the finale... Tifa on her back. Me on\n top of her. And you, Cloud... both of us.”", "The finale.", "Try 'the spin cycle'.",
     ["(Aerith tries to turn around on top of Tifa. Halfway round, their\n knees lock. Everyone freezes.)",
      "Tifa\n“Are we stuck? Are we actually stuck?”",
      "Aerith\n“We're stuck. Kiss me while we wait.”"]),
]
SWITCH_CALL = {3: ["Aerith\n“My turn! You've had him long enough.”", "Tifa\n“Hey! My turn again.”"],
               4: ["Tifa\n“Aerith's turn... she's so close.”", "Aerith\n“Back to Tifa. I want to watch her.”"]}
HOLDS = ["Tifa\n“(Mmmh...!)”", "Aerith\n“(Mmmh...!)”", "Cloud\n“Stay there...”"]
CUES = ["(*She taps his thigh: let go!*)", "(*Tap tap tap!*)", "(*She squeezes his leg: enough!*)"]
GOOD = ["Tifa\n“Hahh... you listened. Thank you.”",
        "Aerith\n“*gasp* ...Okay, that was a lot. A good\n lot.”",
        "Aerith\n“Hah... who taught you to be so\n thoughtful?”"]
EARLY = ["Aerith\n“That's all? I'm tougher than I look!”",
         "Tifa\n“Hey, I wasn't done!”"]
MAD = ["Tifa\n“*cough* Hey. When I tap, you stop.\n Okay?”",
       "Aerith\n“*cough* Tapping means STOP, Cloud.\n Remember?”"]
FINISH_CALL = "Aerith\n“Together... everyone, together...!”"
CLIMAX = {
    "great": ["Tifa\n“Cloud-! Aerith-! I'm...!”",
              "Aerith\n“Now... now, now, now...!”",
              "Cloud\n“...!”",
              "(All three of them, at once.)",
              "Aerith\n“......Wow.”",
              "Tifa\n“......Wow.”",
              "Cloud\n“......Wow.”"],
    "good": ["Tifa\n“Ah...! Aerith, I-!”",
             "Aerith\n“Me too...! Cloud!”",
             "(One after another, then all of them.)",
             "Tifa\n“...Okay. I can't feel my legs.”"],
    "okay": ["(They get there... more or less at the same time.)",
             "Aerith\n“Close enough!”",
             "Tifa\n“(laughing) Two out of three at once. I'll\n take it.”"],
}
AFTER = ["(Later. Gast's old blanket, three people under it, and the snow\n still falling.)",
         "Tifa\n“Thank you. For tonight. For... everything.”",
         "Aerith\n“Same time next week? Different\n roleplay.”",
         "Tifa\n“Absolutely not. ...Maybe.”",
         "Cloud\n“I'm never saying 'it's not what it looks\n like' again.”",
         "Aerith\n“Pfft-! Hahaha!”",
         "Director\n“...CUT. I'm not crying. The snow got\n in my eyes.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.”"

"""(user) Besties: the fifth film (687_besties), Cloud, Tifa and Aerith in the old house at the edge of Icicle
Inn (snmayor: Gast's house, never named in the script, user), on the bed on the lower floor. A sensual, sincere
scene: the three of them bond, compliment each other openly, offer positions and keep trying new things. The
Director's script, "The Best Friend's Boyfriend" (user: the roleplay is scripted, not their idea; play on the
cheating more), a soap opera with their own names in it ("saves time"), runs through it scene by scene: they
read it out, crack up, play along anyway; when an experiment doesn't work they laugh and try something else; it
ends with everyone climaxing together (how well depends on the player's rhythm), then the three of them, close,
in the quiet.

Tifa and Aerith start in their Wall Market dresses (user), the models Corneo's mansion uses.

Structure: the intro (dresses, the script, a heart-to-heart off script, undressing), then SEGMENTS (each a scene
of the script): each a fixed REPS prompts at the pace of the tiers (fixed length, user: progression by
performance, not by grinding); between segments one of them offers what's next: the real one or a silly
experiment that goes wrong (a short staged gag) before they carry on. The finale's FINISH prompts and the whole
run's hits decide the climax. Data only."""

FIELD = "blackbgh"              # the set: a debug room (only blackbgi leads there, itself only from startmap), a copy
BASE = "snmayor"                # Gast's house
BED = ((132, 532), (214, 572), (149, 716), (67, 675))    # the bed's walkable top: foot A B, head C D
BED_Z = 47
CARPET = (-20, 610)             # the rug left of the bed: where the kneeling segment happens
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
KISS_AT = (3, 6, 9)             # (user) the ride: Tifa and Aerith lean in kissing / back, after these reps
CHAT_EVERY = 3
RESULT_WAIT = 50
# the climax by the run's score (hits + 2 x finale hits): at least SCORE_GREAT / SCORE_GOOD, else the okay one
SCORE_GREAT, SCORE_GOOD = 52, 34
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")

KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
SWITCH_KEY = (0x10, "{PURPLE}[MENU]{WHITE}")
HOLD_LABEL = "HOLD "

# the intro: (line, action) actions: gesture_t / gesture_a <anim> (a dress anim
# once), sit (all three on the bed's edge, Cloud between them), bare (fade: undressed, standing). (user: the
# roleplay is scripted: the Director's script, not their idea; play on the cheating more)
INTRO = [
    ("(Snow taps at the windows of the old house at the edge of Icicle\n Inn. Two familiar dresses stand face to face,\n deep in conversation.)", None),
    ("Aerith\n“Ta-da! Wall Market's finest, back by\n popular demand.”", ("gesture_a", "DADD")),
    ("Tifa\n“I can't believe we kept them. Do they\n still... look okay?”", ("gesture_t", "APGC")),
    ("Cloud\n“...You both look incredible.”", None),
    ("Aerith\n“'Incredible.' He used a whole\n adjective, Tifa.”", ("gesture_a", "DDFA")),
    ("Tifa\n“Stop it!”", ("gesture_t", "CXHB")),
    ("Aerith\n“Come sit. The Director left us the\n script.”", "sit"),
    ("Tifa\n“(reading) 'The Best Friend's Boyfriend.'\n ...Oh no.”", None),
    ("Aerith\n“'Tifa loves Cloud. Aerith is her best\n friend. Aerith has wanted Cloud for\n YEARS.'”", None),
    ("Cloud\n“He used our real names.”", None),
    ("Aerith\n“There's a note in the margin: 'Saves\n time.'”", None),
    ("Tifa\n“'Scene one: Tifa is out buying\n groceries...' Wait. I'm the one being\n cheated on?!”", None),
    ("Aerith\n“Ahem. 'Oh, Cloud... we shouldn't. She's\n my best friend. ...She'll be back in TEN\n MINUTES.'”", None),
    ("Cloud\n“'...We can't keep doing this.'”", None),
    ("Aerith\n“Pfft-! 'Keep doing'? It's page one! Who\n WROTE this?!”", None),
    ("Tifa\n“It's so much. It's SO much. (She hides\n her face in her hands.)”", None),
    ("Tifa\n“...Before we start, though. Off script?”", None),
    ("Tifa\n“A year ago I'd never have said this out\n loud. I love you. Both of you.”", None),
    ("Aerith\n“Mm. Me too. You're my best friend, Tifa.\n For real. Not on page one.”", None),
    ("Cloud\n“I've never felt this safe with anyone.”", None),
    ("Aerith\n“Okay, before we all start crying...\n 'Page two: the dresses come off.'”", "bare"),
    ("Tifa\n“...Wow. Aerith, you're gorgeous.”", None),
    ("Aerith\n“Says the woman with THOSE. Cloud, back\n me up.”", None),
    ("Cloud\n“You're both... perfect. I don't know\n where to look.”", None),
    ("Aerith\n“The script says: at your girlfriend.\n Then at her best friend. 'Guiltily.'”", None),
]
HOW = ("Press the button shown in time with them.\nEvery position lasts the same while; the\nbetter your rhythm, the better the ending."
       "{NEW}In the kneeling part, a HOLD lasts until\nshe taps out: let go the moment she does.\nWhen they call My turn!, press {PURPLE}[MENU]{WHITE}.")

# the segments, in order: (key, title, setup lines, chatter, misses, tier lines {tier: lines}); each a scene
# of the Director's script
SEGMENTS = [
    dict(key="edge", title="Tifa on the edge; Cloud kneeling to her; Aerith holding her from behind",
         setup=["Aerith\n“'Scene two. The best friend comforts\n the girlfriend... while the boyfriend\n makes it up to her.'”",
                "Tifa\n“'How could you two... ohh... how could\n you...' What's my line?”",
                "Aerith\n“(whispering) 'I'll never forgive you.'\n You're smiling too much for this\n scene.”"],
         chat=["Aerith\n“Lean back. I've got you.”",
               "Tifa\n“Cloud... don't stop... ahh...”",
               "Aerith\n“Look at her, Cloud. Isn't she\n beautiful?”",
               "Tifa\n“Aerith, your hands... mm...”",
               "Aerith\n“'Forgive him, Tifa.' ...That's in the\n script. I promise.”",
               "Cloud\n“(Mm.) You taste amazing.”"],
         miss=["Tifa\n“Ah-! Your hair tickles!”",
               "Aerith\n“(giggle) Breathe, Cloud. Through your\n nose.”",
               "Tifa\n“Ow, my knee hit your ear. Sorry!”",
               "Aerith\n“Easy... there. Like that.”"],
         tiers={2: ["Tifa\n“Ahh...! I can't hold still...”"],
                3: ["Aerith\n“She's shaking. Don't you dare stop.”"]}),
    dict(key="ride", title="Tifa riding Cloud; Aerith astride his face; the two of them holding hands",
         setup=["Tifa\n“'Scene three. The girlfriend takes back\n what's hers.' ...I like this scene.”",
                "Aerith\n“'And the best friend refuses to leave.'\n Also true.”",
                "Cloud\n“(Mmph.)”"],
         chat=["Aerith\n“Tifa, you look like a goddess up there.”",
               "Tifa\n“Don't let go of my hands.”",
               "Aerith\n“'This is a betrayal!' ...Of what? I've\n lost the plot.”",
               "Tifa\n“Ah... he's so deep... mm...”",
               "Aerith\n“Cloud, your tongue... ohh, page four\n can wait.”",
               "Tifa\n“'My boyfriend is SO good at this.'\n ...Off script. Still true.”"],
         miss=["Tifa\n“Whoa-! Hold on, I'm slipping!”",
               "Aerith\n“(giggle) Don't buck, Cloud!”",
               "Tifa\n“Oops. Too far. Again.”",
               "Cloud\n“(Mmph!) ...Can't... breathe...”"],
         tiers={2: ["Tifa\n“Aerith... look at me... ahh...”"],
                3: ["Aerith\n“Together, Tifa! Ride him!”"]}),
    dict(key="lick", title="Aerith on the edge; Tifa bent over, her mouth on Aerith; Cloud behind Tifa",
         setup=["Aerith\n“'Scene four. Revenge: the girlfriend\n seduces the best friend.' ...Is this\n still a soap opera?”",
                "Tifa\n“It just says 'Tifa makes Aerith pay.'\n So... I'm making you pay.”",
                "Aerith\n“Oh. OH. Okay. I'm paying. I'm paying!”"],
         chat=["Aerith\n“Tifa... your mouth... ahh...”",
               "Tifa\n“(Mmh...)”",
               "Cloud\n“Tifa... you feel unbelievable.”",
               "Aerith\n“Look at us. Who needs a script?”",
               "Aerith\n“'I'm sorry I stole your boyfriend!'\n ...I'm not sorry at all.”",
               "Tifa\n“(Mmh!) ...I love you both. Don't stop.”"],
         miss=["Aerith\n“Ah-! Gentle! Gentle!”",
               "Tifa\n“Sorry! He pushed me!”",
               "Aerith\n“(laughing) The bed squeaked SO loud.”",
               "Tifa\n“Cloud, easy... there.”"],
         tiers={2: ["Aerith\n“Tifa, I'm... I'm close...”"],
                3: ["Tifa\n“(Mmmh!!)”"]}),
    dict(key="share", title="On the rug: one kneeling before Cloud, the other behind him, taking turns",
         setup=["Aerith\n“'Scene five. The two rivals... share\n him.' He underlined 'share' three\n times.”",
                "Tifa\n“That line is SO much. ...Okay. It's a\n little hot.”"],
         chat=["Tifa\n“Mmh... (She looks up at him.)”",
               "Aerith\n“(behind him) Your back is so warm...”",
               "Tifa\n“Aerith, stop tickling him, he keeps\n jumping.”",
               "Aerith\n“My turn soon. I'm counting.”",
               "Cloud\n“You two... are amazing.”",
               "Tifa\n“Look at his face. I love that face.”"],
         miss=["Tifa\n“(Mmph?!) ...Oops.”",
               "Aerith\n“Ow, nose!”",
               "Tifa\n“Whose turn is it? I lost track!”",
               "Aerith\n“(giggle) Rhythm!”"],
         tiers={2: ["Aerith\n“He's trembling. I can feel it from back\n here.”"],
                3: ["Tifa\n“He's close. I can tell.”"]}),
    dict(key="stack", title="Tifa on her back at the edge; Aerith over her; Cloud with both",
         setup=["Tifa\n“'Final scene. The girlfriend forgives\n everyone.' ...Everyone? Even me?”",
                "Aerith\n“Especially you. Now kiss and make up...\n in a very specific way.”",
                "Tifa\n“The script's over. This is just us.”"],
         chat=["Tifa\n“Aerith... your hair's everywhere. I love\n it.”",
               "Aerith\n“Tifa... you're shaking.”",
               "Cloud\n“I love you. Both of you.”",
               "Tifa\n“Don't let go, either of you.”",
               "Aerith\n“Cloud... you're so good to us.”",
               "Tifa\n“This is... everything.”"],
         miss=["Aerith\n“Wrong one! (giggle) ...Actually, no,\n that's fine too.”",
               "Tifa\n“Ah! Knee! My knee!”",
               "Aerith\n“The bed! The bed's moving!”",
               "Tifa\n“(laughing) We're going to break this\n bed.”"],
         tiers={2: ["Tifa\n“Cloud... Aerith... I'm close...”"],
                3: ["Aerith\n“Together... all of us, together...”"]}),
]
# between segments: (who asks, the question, the real choice, the experiment, the gag's lines)
OFFERS = [
    ("Tifa\n“'Scene three: the girlfriend takes back\n what's hers.' I want to ride you.\n Unless someone has a better idea?”", "Let Tifa ride.", "Try 'the wheelbarrow'.",
     ["(Cloud lifts Aerith's legs. Aerith walks two steps on her hands,\n wobbles, and folds into a giggling heap on the rug.)",
      "Aerith\n“I'm fine! I'm fine. That wasn't in the\n script.”",
      "Tifa\n“Ten points for enthusiasm.”"]),
    ("Aerith\n“Page four says 'revenge.' Tifa... I'll\n sit on the edge. You come to me.”", "Do page four.", "Try 'the pretzel'.",
     ["(Three people. Six legs. One bed. Somebody's foot ends up in\n somebody's ear.)",
      "Tifa\n“Whose foot is this?!”",
      "Aerith\n“Mine! Sorry! Nobody move!”",
      "Cloud\n“...I can't feel my arm.”"]),
    ("Tifa\n“'The rivals share him.' Can we... both\n take care of you now?”", "Kneel together.", "Try 'the human chair'.",
     ["(Aerith sits on Cloud. Tifa sits on Aerith. Cloud sits on nothing.\n The chair lasts exactly one second.)",
      "Aerith\n“Physics! We forgot about physics!”",
      "Tifa\n“I've never laughed this hard naked.”"]),
    ("Aerith\n“For the finale... Tifa on her back. Me\n on top of her. And you, Cloud... both of\n us.”", "The finale.", "Try 'the spin cycle'.",
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
AFTER = ["(Later. One borrowed blanket, three people under it, and the\n snow still falling.)",
         "Tifa\n“Thank you. For tonight. For... everything.”",
         "Aerith\n“Same time next week? I'll write the\n script this time.”",
         "Tifa\n“Absolutely not. ...Maybe.”",
         "Cloud\n“I'm never saying 'we can't keep doing\n this' again.”",
         "Aerith\n“Pfft-! Hahaha!”",
         "Director\n“...CUT. The best cheating drama I've\n ever shot, and nobody got cheated on.\n I'm not crying. It's the snow.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.”"

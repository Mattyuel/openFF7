"""(user) Going There: the Director's second tutorial-style film (690_going_there), after the contract Tifa signed
for the special scenes. In a copy of Don Corneo's bedroom (672's set) three positions, the special scenes' poses:
"ride" (672's third, the finisher: Cloud on his back, Tifa astride facing his feet, this time in the back and
taken slow, with "the special stuff"), "head" (straight from there to her mouth; she gags, then it isn't so bad;
the Director has Cloud talk dirty, he's awful at it, Tifa coaches him; then she tells him to fuck her face),
"mount" (672's first, the insert, in three mounts: front as in the specials, side-on with his foot on her head,
then reversed in a plank on her, flopping his hips; Tifa egging him on). The prompt game, the danger meter and
the finisher as 688. Data only."""

FIELD = "blackbgb"              # a debug room only startmap leads to, replaced by a copy of Corneo's bedroom
BASE = "colne_6"
ARRIVE = (0, 40)                # (672's SPOTS centre: the floor in front of the bed)
MUSIC = 35                      # AKAO 10 index: COSTA (the movie's)
PAY_HIT = 12
HITS_UP = 2
PERIODS = (60, 45, 33, 24)
FINISH_FRAMES = 150
KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (683's squat sound)
START = {"C": (15, 45), "G": (-15, 45)}     # the intro: 672's near_r / near_l

INTRO = [
    "Director\n“Tifa! My star. You read the contract\n for the special scenes, right? All of\n it? Including page nine?”",
    "Tifa\n“...I signed it.”",
    "Director\n“Signing is reading, legally. And you\n prepared as per the instructions? The\n ones in the envelope?”",
    "Tifa\n“I prepared. Thoroughly. Very\n thoroughly. I don't want to talk\n about how thoroughly.”",
    "Director\n“Then there's nothing to worry about!\n If you did your homework, today is a\n walk in the park. A tight park.”",
    "Cloud\n“...What's on page nine?”",
    "Director\n“Today we go THERE. The scenic route.\n The back door. Tifa's agreed. Cloud,\n you're driving. Clothes off!”",
]
HOW = ("Same as orientation: press the button\nshown in time. Hits speed things up and\n"
       "pull the meter in; misses push it out.\nThe red means CUT.")
PAID = "Director\n“Back-door bonus: {VAR} gil. Pleasure\n doing business!”"
OUTRO = [
    "Tifa\n“...Okay. I'm going to lie here for\n a while. Maybe a week.”",
    "Cloud\n“That was... I don't have words.”",
    "Director\n“You had PLENTY of words. Some of them\n were even good. That's a wrap!”",
]

# segments: setup lines (both still), reps, beats after a rep: (rep, kind, lines...), the lines before the
# fade to the next. kinds: talk (while it goes on), pause (both still), gag (head: she gags: his deep hold, her
# pull back, then the lines), frenzy (lines, then the top speed), mount (fade, the next of his mounts, lines)
SEGMENTS = [
    dict(key="ride", reps=12, setup=[
        "Director\n“Position one, from the specials:\n Cloud on his back, Tifa on top facing\n his feet. You're in charge, Tifa.”",
        "Director\n“And use the special stuff. Lots. Then\n some more. There's no such thing as\n too much of the special stuff.”",
        "Tifa\n“(She works the bottle like it owes\n her money.) Okay. Slippery. Very\n slippery. Here goes...”",
        "Tifa\n“Nnh... wait. Wait, wait. It's not...\n it won't... how is it so BIG from\n this end?”",
        "Director\n“Breathe out as you sit. Push back a\n little, like you're letting it in.\n Slow. Slower than that.”",
        "Tifa\n“Push... back. Okay. ...Ah! Oh. Oh,\n it's in. The tip's in. Don't move.\n Nobody move.”"],
        beats=[
            (1, "pause", ["Tifa\n“Hah... it's like a stretch that\n burns, then stops burning. Full.\n So full. Is it all the way?”",
                          "Cloud\n“Halfway.”",
                          "Tifa\n“HALFWAY?!”",
                          "Director\n“More special stuff! And Cloud: stay\n still. Let her come to you.”"]),
            (3, "talk", ["Cloud\n“It's... so tight. Hot. It grips the\n whole way down, not just at the\n start. I'm trying not to move.”",
                         "Tifa\n“Good. Keep trying. ...Oh, that's\n deeper. Slowly, slowly...”"]),
            (5, "pause", ["Tifa\n“Hah... okay. Okay, I think it's\n found its place. The ache's gone.\n Now it's just this deep, heavy...”",
                          "Tifa\n“...warm pressure, everywhere at\n once. It's strange. It's good\n strange.”",
                          "Cloud\n“You're shaking.”",
                          "Tifa\n“That's the good kind. Keep going.”"]),
            (7, "talk", ["Tifa\n“Ahh... ah... there it is. That's the\n rhythm. Oh, I see what page nine\n was about now.”",
                         "Director\n“She's FLOWING, people! Look at that\n flow!”"]),
            (9, "talk", ["Cloud\n“Every time you sit down it pulls at\n me. Like you don't want to let go.”",
                         "Tifa\n“Maybe I don't. Mmh... ah...”"]),
            (11, "talk", ["Tifa\n“Ah! Ahh... okay, I'm a convert. A\n slippery, very sore convert.”"]),
        ],
        after=[
            "Director\n“Beautiful! Now, position two, and\n here's the twist: Cloud goes straight\n from there... to the mouth.”",
            "Tifa\n“...Straight from THERE? To my MOUTH?\n You want me to... from...”",
            "Director\n“That's what the envelope was for,\n sweetheart. You prepared. It's clean.\n And it's just Cloud. You love Cloud.”",
            "Tifa\n“...I did prepare. Very thoroughly.\n ...Okay. Okay. For the art.”"]),
    dict(key="head", reps=12, setup=[
        "Director\n“Position two: head! Tifa, kneel.\n Cloud, stand. Same as orientation,\n with... extra history.”",
        "Tifa\n“Don't call it history.”"],
        beats=[
            (1, "gag", ["Tifa\n“*GLK* *hrk* ...hah! Sorry! Sorry. It\n hit the back and my throat just...\n said no.”",
                        "Tifa\n“...Huh. It's not so bad. It's\n actually... warm. If anything, it's\n warm. Everything about it is warm.”",
                        "Director\n“Warm is wonderful! Back in!”"]),
            (3, "talk", ["Director\n“Cloud! Talk to her! Talk DIRTY. The\n audience wants to hear you.”",
                         "Cloud\n“...Dirty. Okay. ...You have a very\n nice... mouth. Area.”",
                         "Cloud\n“Your teeth are... well maintained.”",
                         "Director\n“Oh no.”",
                         "Cloud\n“This is... a good blowjob. Ten out\n of ten. I would recommend it.”"]),
            (5, "pause", ["Tifa\n“*pah* Cloud. Cloud. No. Stop rating\n it. Okay, listen to me.”",
                          "Tifa\n“Tell me I'm good at it. Tell me how\n deep I'm taking you. Tell me what\n you're going to do to my throat.”",
                          "Tifa\n“And call me something. 'Good girl.'\n Or 'slut'. Your slut. ...Try it.”",
                          "Cloud\n“...Okay.”"]),
            (7, "talk", ["Cloud\n“That's it. Take it all, good girl.\n You're such a good little slut for\n me. Deeper. Look up at me.”",
                         "Tifa\n“Mmmph!! Mm-hmm! Mmmf!”",
                         "Director\n“She LIKES it! Everybody, write\n that down!”"]),
            (9, "frenzy", ["Tifa\n“*pah* Hah... Cloud. Stop being\n polite about it. Hold my head and\n fuck my face.”",
                           "Cloud\n“...Yes ma'am.”",
                           "Director\n“OH, he's doing it! He's doing it\n with ENTHUSIASM!”"]),
            (11, "talk", ["Tifa\n“Gkk- mmph! Mmmph! Mmf-mmf-mmf!”",
                          "Cloud\n“You're perfect. You're taking all of\n it. Good girl.”"]),
        ],
        after=[
            "Tifa\n“*cough* *cough* Hah... hah... my\n voice is GONE. Was that dirty enough\n for you?”",
            "Director\n“Dirty enough for the whole slum!\n Final position: from the specials,\n with some... variations. On the bed!”"]),
    dict(key="mount", reps=15, setup=[
        "Director\n“Tifa, knees on the bed, chest down,\n hips up. Cloud: up and over her, from\n above. Like a jockey.”",
        "Tifa\n“Like a WHAT?”",
        "Director\n“More special stuff! Always more!”",
        "Tifa\n“Just get in me, Cloud. I'm ready.\n I'm so ready it's embarrassing.”"],
        beats=[
            (2, "talk", ["Tifa\n“Ahh! From above it goes straight\n down... so deep... yes, like that,\n harder!”",
                         "Cloud\n“You're squeezing me.”",
                         "Tifa\n“You can take it. Come on, Strife!”"]),
            (5, "mount", ["Director\n“Variation! Cloud, turn sideways.\n Keep it in there. Now put your foot\n on her head. Gently!”",
                          "Tifa\n“His FOOT? On my... oh. Oh, that's...\n that's degrading. Why do I like\n that?”",
                          "Cloud\n“Is it okay?”",
                          "Tifa\n“Don't you dare stop. Push me down\n into the bed. Just like that.”"]),
            (7, "talk", ["Tifa\n“Ah! Ah! It hits a different spot\n from the side. Keep going! Don't\n you slow down on me!”"]),
            (10, "mount", ["Director\n“And for the grand finale: reverse!\n Cloud, turn around, plank on her.\n Hands on the bed. Flop those hips!”",
                           "Cloud\n“...Flop?”",
                           "Director\n“Up in the air and DROP. Like you're\n trying to break the bed.”",
                           "Tifa\n“You heard the man. Break the bed.”"]),
            (12, "talk", ["Tifa\n“Ahh! Every time you drop it goes all\n the way! Again! AGAIN! You're going\n to ruin me, Cloud!”",
                          "Cloud\n“Is that a complaint?”",
                          "Tifa\n“It's a REQUEST!”"]),
            (14, "talk", ["Tifa\n“I'm so full... I'm so close... don't\n stop, don't you dare stop!”"]),
        ],
        after=[]),
]
FINISH_CALL = "Director\n“FINISHER! Mash {PURPLE}[OK]{WHITE} and push the\n needle into the red!”"
FINISH_WIN = ["Tifa\n“AHHHH!! ...Oh... oh, I felt that in my\n TOES. ...Is the bed still there?”",
              "Director\n“Barely! Bonus!”"]

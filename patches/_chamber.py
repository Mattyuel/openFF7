"""(user) The chamber (679_chamber): the loose group shoot's engine in its chamber mode in the Gold Saucer Ghost
Hotel's bedroom (ghotin_2, copied under the unused name `FIELD`): the six girls wait at their spots (user's
sketch: by each bed's head, standing with their hands clasped high; at each bed's foot, kneeling with their
hands behind their backs); each turn fades in on Cloud walking up to one of them, "I choose you.", her answer,
then the two of them on her bed in a position (`POSITIONS`, random, never twice running) for `TURN_MIN`
frames (20 s, user), until every girl has been chosen; now and then a break (`CUTS`, `CUT_CHANCE` of 256).
Data only.

Positions (`girl` / `cloud` pose letters): W / K chained (she kneels up, hands bound high; he kneels behind),
X / N offering (on her back, legs straight up in a V; he kneels at her hips holding her shins), B / M throne
(she sits on his face), Z / A mating press (her legs folded up round him), R / R reverse ride (672's finisher),
E / E hanging (her head off the bed's foot, him standing on the floor: `floor`), P / P prayer (672's insert),
I / I 69, C / O squat, F / F prone. `rel`: where Cloud goes (679_chamber `_rel`)."""

FIELD = "hyou12"              # (no gateway or MAPJUMP leads there: the Glacier's unused 'dummy' cave)
BASE = "ghotin_2"
MINUTES = 0                   # (unused: the chamber ends when all six are chosen)
TURN_MIN, TURN_RANGE = 600, 0  # (user) 20 seconds a girl
MUSIC = 67                    # BEE (the Honey Bee Inn's theme: naughty)
CUT_CHANCE = 128              # a break after a turn: 1 in 2

POSITIONS = [
    dict(key="chained", girl="W", cloud="K", counts=(1, 1)),
    dict(key="offering", girl="X", cloud="N", counts=(1, 1)),
    dict(key="throne", girl="B", cloud="M", counts=(1, 1)),
    dict(key="press", girl="Z", cloud="A", counts=(1, 1)),
    dict(key="ride", girl="R", cloud="R", counts=(1, 1)),
    dict(key="hanging", girl="E", cloud="E", floor=True, counts=(1, 1), oral=True, hold=True),
    dict(key="prayer", girl="P", cloud="P", counts=(1, 1)),
    dict(key="sixtynine", girl="I", cloud="I", counts=(1, 1), oral=True, hold=True),
    dict(key="squat", girl="C", cloud="O", target="entry", rel=0, counts=(1, 1)),
    dict(key="prone", girl="F", cloud="F", counts=(1, 1)),
]
FIRST = ("chained", 1)

CHOOSE = "Cloud\n“I choose you.”"
REPLIES = {
    "ruby": ["Ruby\n“Finally. I was about to choose myself.”",
             "Ruby\n“Took you long enough, star.\n Try to keep up.”",
             "Ruby\n“Smart man. Saved the best for now.”"],
    "skye": ["Skye\n“ME?! Yesss! Let's GOOO!”",
             "Skye\n“Ooh, pick me, pick me... wait,\n you did! Hehe!”",
             "Skye\n“Don't hold back. I mean it!”"],
    "elena": ["Elena\n“M-me? ...Acknowledged.\n Please be... thorough.”",
              "Elena\n“I've prepared for this. Mentally.\n Mostly.”",
              "Elena\n“My rules stand. ...Otherwise, yes.”"],
    "scarlet": ["Scarlet\n“Kyahaha! Of course you did, puppy.”",
                "Scarlet\n“Untie me, darling... no. Leave them.”",
                "Scarlet\n“Mm. Let's give them something\n to be jealous of.”"],
    "tifa": ["Tifa\n“Cloud... I was hoping you would.”",
             "Tifa\n“Okay. Just you and me. ...And them.”",
             "Tifa\n“Hehe. Be gentle. ...At first.”"],
    "aerith": ["Aerith\n“Hehe! I knew it'd be me!”",
               "Aerith\n“My knight in shining... nothing.”",
               "Aerith\n“Ooh, what took you so long?”"],
}

TALK = {
    "ruby": ["Is that all you've got, star?", "Harder! The ghosts can't hear you!",
             "Watch closely, ladies.", "Oh! Right there... RIGHT there!"],
    "skye": ["Woohoo! Spooky AND sexy!", "Spank me! Go on, do it!", "This hotel is the BEST!",
             "Hehe... I can't move my hands..."],
    "elena": ["Th-this place is so creepy...", "Ah! ...Sorry. Continue.", "I-I can take more. Proceed.",
              "Don't stop... that's an order!"],
    "scarlet": ["Kyahaha! Is that your best, darling?", "Slower. Make them WATCH.",
                "Smack my ass, puppy.", "Harder, darling. I'm not made of glass."],
    "tifa": ["Cloud... mmh... that feels good...", "Easy... okay... now harder.",
             "Don't let go of me...", "Hold me tighter..."],
    "aerith": ["Hehe, the ghosts are watching!", "Ooh! Do that again!", "Spank me, I've been naughty.",
               "Faster, mister bodyguard!"],
}
COMMENTS = {
    "ruby": ["Amateur.", "My turn was better.", "Arch your back, babe!", "Save some for the rest of us!",
             "Is she even trying?", "These candles are a mood."],
    "skye": ["Hahaha! Go go go!", "Ooh, I wanna try that one!", "Look at her face!", "Spank her! Do it!",
             "Best. Haunted. Hotel. Ever.", "Wooo!"],
    "elena": ["Did that painting just blink?", "I'm taking notes.", "Is the door locked? It should be.",
              "She's very flexible.", "I could do that. Probably.", "This wasn't in the brochure."],
    "scarlet": ["Kyahaha! Sloppy, darling.", "Smack her, puppy!", "Hold her down!", "Pathetic. Again!",
                "Ooh, now THAT'S a show.", "Kyahaha! Look at her squirm!"],
    "tifa": ["You've got this!", "Everyone okay?", "Pace yourself, Cloud.", "She looks happy.",
             "Go, girl!", "Careful with her!"],
    "aerith": ["Hehe, cute!", "Ooh, someone's enjoying herself.", "Cloud, you're sweating!",
               "Look at those toes curl!", "Hey, save some for me!", "Spank her, Cloud! Hehe."],
}

INTRO = ["“The Ghost Hotel's... special suite.\n One at a time, star: walk up, pick a girl,\n make it count.”",
         "“Same rules: tap OK, mind the meter,\n red at either end and we're done. ...ACTION!”"]
LAST_CALL = "Cameraman\n“Last one, people!\n Give me a FINISHER!”"

# ---- breaks (as `_movie_loose`'s cutaways: `set` = screen offsets from STAGE on the floor) ----
STAGE_AT = (-244, -104, 0)    # the cutaways' centre: (user: nobody on the beds or the table) the open floor at
                              # the front of the room, clear of all furniture (679_chamber sets STAGE)
WATCH = [(-70, -35), (70, -35), (-85, 0), (85, 0), (-50, 30), (50, 30)]   # the others, round the scene
STAGE = (0, 0)
CUTS = [
    dict(key="thunder", need=["elena", "skye", "tifa"],
         set={"elena": (0, 5, "kneel", "front"), "tifa": (25, 0, "stand", "elena"),
              "skye": (-30, 0, "stand", "elena"), "cloud": (55, -10, "stand", "elena"),
              "camera": (-75, -15, "stand", "elena")},
         talk="(KRA-KOOOM! Lightning fills the window.){NEW}"
              "Elena\n“EEK! ...I-I wasn't scared.\n That was a tactical crouch.”{NEW}"
              "Skye\n“Do it again! Do it again!”{NEW}"
              "Tifa\n(She squeezes Elena's hand.)"),
    dict(key="maiden", need=["skye", "scarlet", "ruby"],
         set={"skye": (0, 0, "stand", "front"), "scarlet": (-30, 5, "stand", "skye"),
              "ruby": (35, 5, "stand", "skye"), "cloud": (60, -15, "stand", "skye"),
              "camera": (-75, -20, "stand", "skye")},
         talk="Skye\n“Ooh, is that an iron maiden?\n Can I get in it?”{NEW}"
              "Scarlet\n“Kyahaha! Only if I get to close it.”{NEW}"
              "Ruby\n“...Nobody is getting in the spiky\n coffin. Shoot's insured for ONE death.”"),
    dict(key="candle", need=["scarlet", "elena"],
         set={"scarlet": (0, 5, "stand", "cloud"), "elena": (-30, 0, "stand", "scarlet"),
              "cloud": (30, 0, "stand", "scarlet"), "camera": (-75, -20, "stand", "scarlet")},
         talk="Scarlet\n(She lifts a candle and tilts it, slowly.){NEW}"
              "Scarlet\n“Hot wax, puppy? Kyahaha.”",
         ask="Scarlet\n“Well? Shall I?”",
         choices=[("Go on, then.", "(Drip.){NEW}Cloud\n“...!”{NEW}Scarlet\n“Kyahaha! What a FACE.”", dict(gil=10)),
                  ("Put it down.", "Scarlet\n“Spoilsport.”{NEW}Elena\n(She blows the candle out.)", dict())]),
    dict(key="ghost", need=["aerith", "elena", "ruby"],
         set={"aerith": (0, 5, "stand", "front"), "elena": (-35, 5, "kneel", "front"),
              "ruby": (35, 0, "stand", "front"), "cloud": (0, -25, "stand", "front"),
              "camera": (-80, -20, "stand", "aerith")},
         talk="(A low moan drifts from the wall.){NEW}"
              "Aerith\n“...Hello? Are you a ghost? Do you\n want to watch? Hehe.”{NEW}"
              "Elena\n“DON'T INVITE IT.”{NEW}"
              "Ruby\n“If it's not paying, it's not watching.”"),
    dict(key="cuffs", need=["tifa", "skye"],
         set={"tifa": (0, 5, "stand", "skye"), "skye": (25, 5, "stand", "tifa"),
              "cloud": (55, -10, "stand", "tifa"), "camera": (-70, -20, "stand", "tifa")},
         talk="Skye\n“Um. Tifa? These handcuffs don't have\n a key.”{NEW}"
              "Tifa\n“...They're props, Skye.”{NEW}"
              "Skye\n“They are NOT props.”{NEW}"
              "Tifa\n(Crack.) “They are now.”"),
    dict(key="blindfold", need=["aerith", "scarlet", "tifa", "ruby"],
         set={"aerith": (0, 5, "stand", "front"), "scarlet": (-30, 0, "stand", "aerith"),
              "tifa": (30, 0, "stand", "aerith"), "ruby": (55, 5, "stand", "aerith"),
              "cloud": (0, -25, "stand", "aerith"), "camera": (-85, -20, "stand", "aerith")},
         talk="Aerith\n“Game! Cloud's blindfolded. One of us\n kisses him. He guesses who!”{NEW}"
              "(Someone kisses him. Slowly.)",
         ask="Aerith\n“Well? Who was it?”",
         choices=[("Tifa.", "Tifa\n“...How did you know?”{NEW}Scarlet\n“Oh, PLEASE.”", dict(gil=5)),
                  ("Scarlet.", "Scarlet\n“Kyahaha! Wrong, puppy. It was Ruby.”{NEW}Ruby\n“Unforgettable, right?”",
                   dict(annoy=["tifa"])),
                  ("Aerith.", "Aerith\n“Hehe... nope! But I'll take a turn.”", dict(gil=5))]),
    dict(key="painting", need=["elena", "aerith"],
         set={"elena": (0, 5, "stand", "front"), "aerith": (30, 0, "stand", "elena"),
              "cloud": (60, -15, "stand", "elena"), "camera": (-75, -20, "stand", "elena")},
         talk="Elena\n“That painting. Its eyes moved.\n I'm certain.”{NEW}"
              "Aerith\n“It's just jealous. Hehe.”{NEW}"
              "Elena\n“...I'm turning it around.”"),
    dict(key="whip", need=["scarlet", "ruby", "skye"],
         set={"scarlet": (0, 5, "stand", "cloud"), "ruby": (-30, 0, "stand", "scarlet"),
              "skye": (35, 0, "kneel", "scarlet"), "cloud": (25, -20, "stand", "scarlet"),
              "camera": (-80, -20, "stand", "scarlet")},
         talk="Scarlet\n(She finds a riding crop on the wall.){NEW}"
              "Scarlet\n“Oh, this hotel has TASTE.”{NEW}"
              "Skye\n“Me! Me first! ...Gently! ...No, not gently!”{NEW}"
              "Ruby\n“Somebody hide that thing.”"),
    dict(key="checkin", need=["tifa", "elena"],
         set={"tifa": (0, 5, "kneel", "elena"), "elena": (25, 5, "kneel", "tifa"),
              "cloud": (55, -10, "stand", "tifa"), "camera": (-70, -20, "stand", "tifa")},
         talk="Tifa\n“Hey. You okay? Your hands were up\n a long time.”{NEW}"
              "Elena\n“...My shoulders are on fire.\n It's... kind of nice?”{NEW}"
              "Tifa\n“Hehe. Here, let me rub them.”"),
    dict(key="rank", need=["ruby", "scarlet", "aerith", "skye"],
         set={"ruby": (0, 5, "stand", "cloud"), "scarlet": (-30, 0, "stand", "cloud"),
              "aerith": (30, 0, "stand", "cloud"), "skye": (55, 5, "stand", "cloud"),
              "cloud": (0, -25, "stand", "front"), "camera": (-85, -20, "stand", "cloud")},
         talk="Ruby\n“Okay, star. Rankings. Who's been\n your favourite so far?”{NEW}"
              "Scarlet\n“Choose wisely, puppy.”",
         ask="Aerith\n“Hehe... well?”",
         choices=[("I can't choose.", "Ruby\n“You literally said 'I choose you'\n six times.”", dict()),
                  ("Ruby.", "Ruby\n“Correct answer.”{NEW}Scarlet\n“...Hmph.”", dict(gil=5, annoy=["scarlet"])),
                  ("All of you.", "Skye\n“Awww!”{NEW}Scarlet\n“Coward.”", dict(gil=5))]),
    dict(key="drink", need=["aerith", "tifa", "skye"],
         set={"aerith": (-20, 5, "stand", "cloud"), "tifa": (15, 5, "stand", "cloud"),
              "skye": (40, 0, "kneel", "cloud"), "cloud": (0, -20, "stand", "front"),
              "camera": (-80, -20, "stand", "cloud")},
         talk="Tifa\n“Water break. Drink, everybody.\n Especially you, Cloud.”{NEW}"
              "Aerith\n“Room service brought... blood?”{NEW}"
              "Skye\n“It's cherry juice. ...Probably.”"),
    dict(key="howl", need=["skye", "elena", "scarlet"],
         set={"skye": (0, 5, "stand", "front"), "elena": (-30, 0, "stand", "skye"),
              "scarlet": (35, 0, "stand", "skye"), "cloud": (60, -15, "stand", "skye"),
              "camera": (-75, -20, "stand", "skye")},
         talk="Skye\n“AWOOOOO!”{NEW}"
              "Elena\n“Why. Why would you do that here.”{NEW}"
              "Skye\n“Ambience!”{NEW}"
              "Scarlet\n“Kyahaha. Fine. AWOOOO!”"),
]
CUT_FADE = 8
INTRO_SET = {"camera": (-45, -20, "stand", "centre"), "cloud": (15, 5, "stand", "camera"),
             "ruby": (-15, 12, "stand", "camera"), "skye": (40, 12, "stand", "camera"),
             "elena": (-40, 15, "stand", "camera"), "scarlet": (60, -5, "stand", "camera"),
             "tifa": (20, 25, "stand", "camera"), "aerith": (-5, 30, "stand", "camera")}

END_TALK = ("Tifa\n“Well. That was... intense.”{NEW}"
            "Ruby\n“Same time next week? Same coffin?”{NEW}"
            "Aerith\n“Hehe. I'm keeping the handcuffs.”{NEW}"
            "Elena\n“...My arms are still up. I can't put\n them down.”{NEW}"
            "Scarlet\n“Kyahaha. Darlings, that's a wrap.”")

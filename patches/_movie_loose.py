"""(user) The loose group shoot (678): the six co-stars and Cloud on the inn room set for about 20 minutes,
no fixed parts: short segments, each a position with 1-6 of the girls taking turns, a cutaway (a short
staged scene) between segments, everything random, different every time. Data only; the minigame (the
meter, holds, pauses, lessons, slaps, the finisher) is the group shoot's (670).

Kinds of position:
  row    the girls taking part each have their own station (a line of kneeling girls, one per bed...);
         Cloud moves to the engaged one; the others wait in place in the position's waiting pose.
  queue  one station: the engaged girl is there, the others taking part wait near it (kneeling on the
         bed or standing) and swap in at each turn.
Girls not taking part lie or kneel on a free bed, or stand about and stroll between floor spots
(straight lines checked to be all floor: nobody walks into a wall), watching and commenting.

Pose letters are the movie's (670 `POSITIONS` order A..J, O = the group's "end"): A mission, B cowgirl,
C dog, D edge, E head reverse, F prone, G behind, H holding, I 69, J head, O end.
`girl` / `cloud` = the pose each plays; `place`:
  "group:<phase>"  the group shoot's own stations for that part (head / headrev / end: six)
  "solo"           the one-girl shoot's spot for the girl's pose (a queue)
  "beds"           one station per bed, Cloud solved onto her (`solve`: his member's tip at her `target`,
                   `rel` = his DIR minus hers; the spots' z on the bed top)
  "floor"          one station on the floor in front of the beds, solved the same way
`oral`: her lines are muffled; `hold`: the hold / pause / lesson prompts play (oral poses with stop poses).
`counts` = (fewest, most) girls taking part. (User, since) "crown" is the user's own find in the scene lab
(677): a girl's head kneel with Cloud's "end" crouch behind her (Aerith 16 / Elena 12 with Cloud 21:
her (17, -61, 100) DIR 234, him (19, -43, 100) DIR 7); "squat ..." / "all fours" follow it: Cloud's crouch
or stand put on other girl poses by `solve`, checked on offline renders only."""

FIELD = "shpin_22"            # never entered in the open world (no gateway or MAPJUMP leads there)
ENABLED = True                # the cameraman's "Everyone" goes here (False: the classic group shoot, subin_4)
MINUTES = 20                  # (user) about 20 minutes; the last segment starts once this much has passed
TURN_MIN, TURN_RANGE = 300, 300   # a girl's turn: 10-20 s, random
LEAN = 7                      # (the crown: the user's DIR 7 / 234)

POSITIONS = [
    dict(key="lineup", girl="J", cloud="J", place="group:0", counts=(2, 6), oral=True, hold=True),
    dict(key="hanging", girl="E", cloud="E", place="group:1", counts=(2, 6), oral=True, hold=True),
    dict(key="pinned", girl="O", cloud="O", place="group:2", counts=(2, 6), oral=True, hold=True),
    dict(key="crown", girl="J", cloud="O", place="beds", crown=True, counts=(1, 3)),
    dict(key="squatdog", girl="C", cloud="O", place="beds", target="entry", rel=0, counts=(1, 3)),
    dict(key="squatprone", girl="F", cloud="O", place="beds", target="entry", rel=0, counts=(1, 3)),
    dict(key="squatmiss", girl="A", cloud="O", place="beds", target="entry", rel=128, counts=(1, 3)),
    dict(key="allfours", girl="C", cloud="J", place="floor", target="mouth", rel=128, counts=(1, 3), oral=True),
    dict(key="cowgirl", girl="B", cloud="B", place="solo", counts=(1, 4)),
    dict(key="sixtynine", girl="I", cloud="I", place="solo", counts=(1, 3), oral=True, hold=True),
    dict(key="edge", girl="D", cloud="D", place="solo", counts=(1, 3)),
    dict(key="behind", girl="G", cloud="G", place="solo", counts=(1, 3)),
    dict(key="holding", girl="H", cloud="H", place="solo", counts=(1, 3)),
    dict(key="head", girl="J", cloud="J", place="solo", counts=(1, 4), oral=True, hold=True),
    dict(key="mission", girl="A", cloud="A", place="solo", counts=(1, 3)),
    dict(key="dog", girl="C", cloud="C", place="solo", counts=(1, 3)),
    dict(key="prone", girl="F", cloud="F", place="solo", counts=(1, 3)),
]
FIRST = ("lineup", 2)         # (user) it starts in head with two girls, then a cutaway

# the engaged girl's lines where she can talk (in character, `_movie_profiles`); muffled ones are the
# group's (`_movie_group.MUFFLED`). A line about a slap / spank / smack is a Square prompt (670 `_slaps`)
TALK = {
    "ruby": ["Is that all you've got, star?", "Harder! The camera can't see you trying!",
             "Watch me, ladies. This is how it's done.", "Oh! Right there... RIGHT there!"],
    "skye": ["Woohoo! Again! Again!", "Spank me! Go on, do it!", "This is the BEST day ever!",
             "Hehe... you're so deep..."],
    "elena": ["Is this... the correct angle?", "Ah! ...Sorry. Continue.", "I-I can take more. Proceed.",
              "Don't stop... that's an order!"],
    "scarlet": ["Kyahaha! Is that your best, darling?", "Slower. Make them WATCH.",
                "Smack my ass, puppy.", "Harder, darling. I'm not made of glass."],
    "tifa": ["Cloud... mmh... that feels good...", "Easy... okay... now harder.",
             "Are you okay? Because I'm GREAT.", "Hold me tighter..."],
    "aerith": ["Hehe, did you miss me?", "Ooh! Do that again!", "Spank me, I've been naughty.",
               "Faster, mister bodyguard!"],
}
# the others watching (anyone, any position)
COMMENTS = {
    "ruby": ["Amateur.", "I did that better.", "Arch your back, babe!", "Save some for me, star!",
             "My turn next. Obviously.", "Is she even trying?"],
    "skye": ["Hahaha! Go go go!", "Ooh, I wanna try that!", "Look at her face!", "Spank her! Do it!",
             "Best. Job. Ever.", "Wooo!"],
    "elena": ["Is that... regulation?", "I'm taking notes.", "Hydration check, everyone?",
              "She's very flexible.", "I could do that. Probably.", "This wasn't in the brochure."],
    "scarlet": ["Kyahaha! Sloppy, darling.", "Smack her, puppy!", "Hold her down!", "Pathetic. Again!",
                "Ooh, now THAT'S a show.", "Kyahaha! Look at her squirm!"],
    "tifa": ["You've got this!", "Everyone okay?", "Pace yourself, Cloud.", "She looks happy.",
             "Go, girl!", "Careful with her!"],
    "aerith": ["Hehe, cute!", "Ooh, someone's enjoying herself.", "Cloud, you're sweating!",
               "Look at those toes curl!", "Hey, save some for me!", "Spank her, Cloud! Hehe."],
}

INTRO = ["“No script today! I call it, you roll with it.\n Positions change, girls swap in and out.”",
         "“Same rules: tap OK, mind the meter,\n red at either end and we're done. ...ACTION!”"]
# shown when the last segment starts (about MINUTES in)
LAST_CALL = "Cameraman\n“That's nearly the tape, people!\n Last set. Give me a FINISHER!”"

# ---- cutaways: short staged scenes between segments (user: "more cutaways to short cutscenes") ----
# One at random after each segment, no repeats until all have played; skipped while one of `need` has
# walked off. `set` = {actor: (sx, sy, pose, face)}: screen offsets (px, x right, y down) from `STAGE`
# snapped to the nearest free floor (or, for actors in `bed`, bed top); pose "stand" / "kneel" / "lie";
# face = another actor ("cloud", "camera" = the cameraman too), "front" (towards the screen), "centre".
# The girls not in `set` watch from free spots. `talk` pages ({NEW}); optional `ask` (the last speaker's
# question to Cloud) with `choices` (label, reply, effects: gil = x the shoot's gil a press, annoy =
# [girls], rules = agreed). Window text: "Name\n...", lines under ~40 characters.
STAGE = (-100, 72)            # (the group's: the widest floor, in front of the left bed)
CUTS = [
    dict(key="water", need=["skye", "ruby", "aerith", "tifa"],
         set={"cloud": (20, 0, "stand", "aerith"), "aerith": (0, 8, "stand", "cloud"),
              "skye": (-40, -5, "stand", "front"), "ruby": (-70, -10, "stand", "skye"),
              "tifa": (45, -15, "stand", "cloud"), "camera": (90, -25, "stand", "cloud")},
         talk="Cameraman\n“Water break! Two minutes!”{NEW}"
              "Skye\n(Glug glug glug)\n“Ahhh! Okay! Who's next?!”{NEW}"
              "Ruby\n“Pace yourself, bubblegum. Some of us\n are going for gold.”{NEW}"
              "Aerith\n“Here, Cloud. You look thirsty. Hehe.”{NEW}"
              "Tifa\n“Seriously, drink something.\n You're all flushed.”"),
    dict(key="makeup", need=["scarlet", "elena", "tifa"],
         set={"scarlet": (-30, 0, "stand", "camera"), "elena": (10, 5, "kneel", "scarlet"),
              "tifa": (25, 0, "stand", "elena"), "cloud": (70, -10, "stand", "scarlet"),
              "camera": (-80, -20, "stand", "scarlet")},
         talk="Scarlet\n“Nobody films me until my lipstick\n is fixed, darling.”{NEW}"
              "Elena\n“Your lipstick has been off since\n minute three.”{NEW}"
              "Scarlet\n“...Kyahaha. Bold, for a Turk.”{NEW}"
              "Tifa\n“Hold still, Elena. Your hair's\n everywhere.”{NEW}"
              "Elena\n“Oh. Thank you. ...Is it bad?”{NEW}"
              "Tifa\n“It's cute.”"),
    dict(key="cramp", need=["elena", "tifa", "ruby"],
         set={"elena": (0, 10, "lie", "front"), "tifa": (25, 5, "kneel", "elena"),
              "ruby": (-35, -5, "stand", "tifa"), "cloud": (60, -15, "stand", "elena"),
              "camera": (-80, -25, "stand", "elena")},
         talk="Elena\n“Ow! Ow ow ow! Calf! CRAMP!”{NEW}"
              "Tifa\n“Lie down. Flex your foot. ...Here.”{NEW}"
              "Elena\n“Ahh... oh. Oh, that's good.\n Where did you learn that?”{NEW}"
              "Tifa\n“Zangan taught me. For fights, mostly.”{NEW}"
              "Ruby\n“Can you do my shoulders next?”"),
    dict(key="notes", need=["scarlet", "elena"],
         set={"camera": (-40, -10, "stand", "cloud"), "scarlet": (10, 0, "stand", "camera"),
              "elena": (45, 5, "stand", "scarlet"), "cloud": (75, -15, "stand", "scarlet")},
         talk="Cameraman\n“I need ENERGY, people! This is a group\n shoot, not a nap!”{NEW}"
              "Scarlet\n“Leave it to me, darling. Puppy! Ladies!\n On my count!”{NEW}"
              "Elena\n“You're not the director.”",
         ask="Scarlet\n“Well, puppy? Who's calling the shots?”",
         choices=[("Scarlet's in charge for now.",
                   "Scarlet\n“Kyahaha! Finally.”{NEW}Elena\n(She sighs, very loudly.)", dict(gil=5, annoy=["elena"])),
                  ("The cameraman calls it.",
                   "Cameraman\n“Thank you!”{NEW}Scarlet\n“Spoilsport.”", dict())]),
    dict(key="blooper", need=["skye", "aerith", "ruby"],
         set={"skye": (0, 15, "lie", "front"), "aerith": (-35, 0, "stand", "skye"),
              "ruby": (35, -5, "stand", "skye"), "cloud": (65, -15, "stand", "skye"),
              "camera": (-75, -20, "stand", "skye")},
         talk="Skye\n“Whoa-whoa-WHOA!”\n(She rolls right off the bed.){NEW}"
              "Skye\n“...I'm okay! I'm okay!\n Did you get that?!”{NEW}"
              "Cameraman\n“Got it. Blooper reel.”{NEW}"
              "Aerith\n“Hahaha! Put it in the trailer!”{NEW}"
              "Ruby\n“Graceful.”"),
    dict(key="crown", need=["aerith", "tifa", "scarlet"],
         set={"cloud": (0, 5, "stand", "front"), "aerith": (-25, 0, "stand", "cloud"),
              "tifa": (35, 0, "stand", "cloud"), "scarlet": (65, -15, "stand", "cloud"),
              "camera": (-75, -20, "stand", "cloud")},
         talk="Aerith\n“Hold still, Cloud. ...There!”\n(She sets a crown of flowers on\n his spikes.){NEW}"
              "Tifa\n“...Oh no. That's adorable.”{NEW}"
              "Scarlet\n“Kyahaha! Keep it on. The customers will\n pay double.”{NEW}"
              "Cloud\n“...Can we just keep going?”"),
    dict(key="bet", need=["ruby", "skye"],
         set={"ruby": (-15, 5, "stand", "skye"), "skye": (20, 5, "stand", "ruby"),
              "cloud": (55, -10, "stand", "ruby"), "camera": (-70, -20, "stand", "ruby")},
         talk="Ruby\n“Bet I can make him finish first.”{NEW}"
              "Skye\n“Bet you can't! I'll do it with one hand!”{NEW}"
              "Ruby\n“Loser buys the drinks at Seventh\n Heaven.”",
         ask="Skye\n“Cloud! Are you in?”",
         choices=[("You're on.",
                   "Ruby\n“Prepare to lose, bubblegum.”{NEW}Skye\n“Prepare to buy drinks, red!”", dict(gil=5)),
                  ("I'm not a trophy.",
                   "Skye\n“Boooo!”{NEW}Ruby\n“...He's scared.”", dict())]),
    dict(key="knock", need=["scarlet", "aerith"],
         set={"scarlet": (-60, -15, "stand", "camera"), "aerith": (0, 5, "kneel", "front"),
              "cloud": (35, 0, "stand", "scarlet"), "camera": (75, -20, "stand", "scarlet")},
         talk="(Knock knock knock.){NEW}"
              "Innkeeper\n(through the door)\n“We've had complaints about the NOISE.”{NEW}"
              "(Everyone freezes.){NEW}"
              "Scarlet\n“We're rehearsing a play, darling!\n A very... physical play!”{NEW}"
              "Innkeeper\n“...Keep it down, please.”{NEW}"
              "Aerith\n“Hehe... shhh, everyone.”"),
    dict(key="huddle", need=["tifa", "skye", "elena", "scarlet", "aerith"],
         set={"tifa": (0, 5, "stand", "front"), "skye": (-30, -5, "stand", "tifa"),
              "elena": (30, -5, "stand", "tifa"), "scarlet": (-55, 5, "stand", "tifa"),
              "aerith": (55, 5, "stand", "tifa"), "cloud": (0, -25, "stand", "tifa"),
              "camera": (-95, -25, "stand", "tifa")},
         talk="Tifa\n“Okay, team huddle! Everyone in!”{NEW}"
              "Tifa\n“Ruby, amazing. Skye, maybe a little\n less screaming.”{NEW}"
              "Skye\n“No promises!”{NEW}"
              "Tifa\n“Elena, you're doing great.\n Scarlet... be nice.”{NEW}"
              "Scarlet\n“I am ALWAYS nice.”{NEW}"
              "Aerith\n“Hehe. Hands in! One, two, three...\n ACTION!”"),
    dict(key="jammed", need=["elena", "ruby"],
         set={"camera": (-20, 0, "stand", "front"), "elena": (15, 5, "kneel", "camera"),
              "ruby": (45, -5, "stand", "elena"), "cloud": (75, -15, "stand", "camera")},
         talk="Cameraman\n“Argh, the tape's jammed! Nobody move!”{NEW}"
              "Elena\n“I read the manual for that model.\n Twist the left reel.”{NEW}"
              "Cameraman\n“...It worked. Who reads camera manuals?”{NEW}"
              "Elena\n“Turks read everything.”{NEW}"
              "Ruby\n“Nerd.”"),
    dict(key="circle", need=["ruby", "skye", "elena", "scarlet", "tifa", "aerith"],
         set={"aerith": (0, 10, "kneel", "front"), "ruby": (-30, 0, "kneel", "aerith"),
              "skye": (30, 0, "kneel", "aerith"), "elena": (-55, -10, "kneel", "aerith"),
              "scarlet": (55, -10, "stand", "aerith"), "tifa": (0, -15, "kneel", "aerith"),
              "cloud": (85, -20, "stand", "aerith"), "camera": (-90, -25, "stand", "aerith")},
         talk="Aerith\n“Compliment circle! Something nice about\n the girl next to you!”{NEW}"
              "Ruby\n“Skye's got... stamina. Fine. She's good.”{NEW}"
              "Skye\n“Elena's SO cute when she blushes!”{NEW}"
              "Elena\n“I-I don't blush. ...Scarlet has excellent\n posture.”{NEW}"
              "Scarlet\n“Kyahaha. Tifa's behind could stop a\n bullet, darling.”{NEW}"
              "Tifa\n“...Thanks? Aerith, you're the sweetest\n person here.”{NEW}"
              "Aerith\n“And Cloud works the hardest! Hehe.”"),
    dict(key="angles", need=["scarlet", "ruby"],
         set={"scarlet": (0, 5, "stand", "camera"), "camera": (-45, -10, "stand", "scarlet"),
              "ruby": (35, 0, "stand", "scarlet"), "cloud": (70, -15, "stand", "scarlet")},
         talk="Scarlet\n“Cameraman, darling. You're getting my\n bad side.”{NEW}"
              "Cameraman\n“You have a bad side?”{NEW}"
              "Scarlet\n“No. Which is why this is unacceptable.”{NEW}"
              "Ruby\n“Swap with me. My left side is perfect.”{NEW}"
              "Scarlet\n“...Kyahaha. Fine. For now.”"),
    dict(key="snack", need=["skye", "aerith", "elena", "tifa"],
         set={"skye": (0, 5, "kneel", "front"), "aerith": (-30, 0, "kneel", "skye"),
              "elena": (35, -5, "stand", "skye"), "tifa": (60, 0, "stand", "skye"),
              "cloud": (-65, -15, "stand", "skye"), "camera": (90, -25, "stand", "skye")},
         talk="Skye\n“Snack time! I brought chocobo cookies!”{NEW}"
              "Aerith\n“Ooh! Gimme a yellow one!”{NEW}"
              "Elena\n“We're mid-shoot. You'll get crumbs\n everywhere.”{NEW}"
              "Skye\n“Crumbs ARE the fun part.”{NEW}"
              "Tifa\n“...Can I have one?”"),
    dict(key="tally", need=["elena", "ruby", "tifa", "skye"],
         set={"elena": (0, 5, "stand", "front"), "ruby": (-30, 0, "stand", "elena"),
              "tifa": (35, 0, "stand", "elena"), "cloud": (65, -15, "stand", "elena"),
              "camera": (-70, -20, "stand", "elena")},
         talk="Elena\n“Stamina report. Cloud: still going.\n I've been keeping a tally.”{NEW}"
              "Ruby\n“What's my score?”{NEW}"
              "Elena\n“...Classified.”",
         ask="Ruby\n“Cloud. Who's winning?”",
         choices=[("Everyone's winning.",
                   "Tifa\n“Good answer.”{NEW}Ruby\n“Coward.”", dict()),
                  ("Ruby, obviously.",
                   "Ruby\n“KNEW it.”{NEW}Skye\n“RIGGED!”", dict(gil=5))]),
    dict(key="tickle", need=["aerith", "tifa", "scarlet", "skye"],
         set={"tifa": (0, 10, "lie", "front"), "aerith": (20, 5, "kneel", "tifa"),
              "scarlet": (-40, -5, "stand", "tifa"), "skye": (55, -5, "stand", "tifa"),
              "cloud": (80, -20, "stand", "tifa"), "camera": (-80, -25, "stand", "tifa")},
         talk="Aerith\n“Tifa, you're tense. Is somebody...\n ticklish?”{NEW}"
              "Tifa\n“Don't you dare... Aerith! AERITH!\n Hahaha!”{NEW}"
              "(They go down in a heap of giggles.){NEW}"
              "Scarlet\n“Is this a porno or a sleepover?”{NEW}"
              "Skye\n“Why not both?!”"),
    dict(key="mako", need=["ruby", "scarlet", "skye"],
         set={"ruby": (-30, 0, "stand", "cloud"), "scarlet": (0, 8, "stand", "cloud"),
              "skye": (30, 0, "kneel", "cloud"), "cloud": (10, -25, "stand", "front"),
              "camera": (75, -20, "stand", "cloud")},
         talk="Ruby\n“How is he still going?”{NEW}"
              "Scarlet\n“Mako, darling. The man's practically\n radioactive.”{NEW}"
              "Skye\n“Can I lick the glow off?”{NEW}"
              "Cameraman\n“Tape's still rolling! Keep it hot!”",
         ask="Cameraman\n“Star, you need a breather?”",
         choices=[("I'm fine. Keep rolling.",
                   "Scarlet\n“Kyahaha! That's my puppy.”", dict(gil=10)),
                  ("Thirty seconds.",
                   "Tifa\n“Good. Breathe.”{NEW}Ruby\n“Weak.”", dict())]),
    dict(key="minute", need=["elena", "tifa", "scarlet"],
         set={"elena": (0, 5, "kneel", "cloud"), "tifa": (30, 0, "stand", "elena"),
              "scarlet": (-40, -5, "stand", "elena"), "cloud": (60, -15, "stand", "elena"),
              "camera": (-80, -25, "stand", "elena")},
         talk="Elena\n“Can I sit the next one out?\n I just need a minute.”{NEW}"
              "Scarlet\n“A Turk who needs a minute? Kyahaha!”{NEW}"
              "Tifa\n“Hey. She asked nicely.”",
         ask="Elena\n“Cloud...?”",
         choices=[("Take all the time you need.",
                   "Elena\n“...Thank you. Really.”{NEW}Tifa\n(She squeezes Elena's hand.)", dict(rules=True)),
                  ("We need you in the next one.",
                   "Elena\n“...Fine.”{NEW}Tifa\n(She gives Cloud a long look.)", dict(gil=5, annoy=["elena"]))]),
    dict(key="voice", need=["scarlet", "tifa", "aerith"],
         set={"scarlet": (-20, 5, "stand", "tifa"), "tifa": (20, 5, "stand", "scarlet"),
              "aerith": (50, -5, "kneel", "tifa"), "cloud": (75, -20, "stand", "tifa"),
              "camera": (-75, -20, "stand", "tifa")},
         talk="Scarlet\n“Tifa, darling, you smile through\n everything. Doesn't it hurt?”{NEW}"
              "Tifa\n“...It's called being nice.\n You should try it.”{NEW}"
              "Aerith\n“Ooh. Point to Tifa.”{NEW}"
              "Scarlet\n“...Kyahaha. Touché.”"),
]
CUT_FADE = 8                  # frames: the cutaway's fade (as the group's staged scenes)
# the intro: everyone standing round the cameraman (screen offsets from STAGE, as a cutaway's `set`)
INTRO_SET = {"camera": (-45, -20, "stand", "centre"), "cloud": (15, 5, "stand", "camera"),
             "ruby": (-15, 12, "stand", "camera"), "skye": (40, 12, "stand", "camera"),
             "elena": (-40, 15, "stand", "camera"), "scarlet": (60, -5, "stand", "camera"),
             "tifa": (20, 25, "stand", "camera"), "aerith": (-5, 30, "stand", "camera")}
MUSIC = None                  # (None: the movie's, 670 MUSIC)

END_TALK = ("Tifa\n“Well. That was... a LOT.”{NEW}"
            "Ruby\n“Same time next week?”{NEW}"
            "Aerith\n“Hehe. Group hug!”{NEW}"
            "Elena\n“...I'd like that in writing.”{NEW}"
            "Scarlet\n“Kyahaha. Darlings, that's a wrap.”")

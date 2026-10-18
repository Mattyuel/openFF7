"""(user) The beach party (679): the loose group shoot (`_loose_engine`) on Costa del Sol's beach - the six
co-stars and Cloud for about 20 minutes, positions changing often, cutaways between them, all random. Unlocked
with "Everyone" (670: the co-star list's second row, greyed with it). Data only.

The set is a copy of del3 (the beach) under the unused name `FIELD`: its five loungers are walkable pieces of
the walkmesh (seat ~z 6-12, backrest up to 51), and the walkmesh runs on down the wet sand into the sea (z 0 at
the tide line, -50 knee deep, -120 at the bottom of the screen), so the shallows can be stood in (nothing
hides the legs: the sea is background picture). `place` kinds (679 `_stations`):
  "loungers"   one station per lounger (a row: Cloud goes down the line; the others lounge, waiting)
  "sunbed"     one lounger (a queue)
  "sand"       spots on the dry sand (`spots`: how many, ROW_GAP apart from `at` x), pairs shown side-on
  "surf"       the wet sand at the tide line
  "shallows"   in the water (`depth`: the sea floor height to stand at)
Pose letters: the movie's (A mission, B cowgirl, C dog, F prone, H holding, I 69, J head, O end, U the
lowered carry (673)), and the beach's own (`_beach_poses`): W / V Cloud lounging under a rider facing his
feet / him, Y her bent with hands on her knees (Cloud's edge D behind), Z lounging (the waiting pose on the
loungers, played at the rider's spot). `wait` = the waiting pose of the girls taking part ("lounge" = Z)."""

FIELD = "nivgate3"            # (no gateway or MAPJUMP leads there; its own script can't even be parsed)
BASE = "del3"
MINUTES = 20
TURN_MIN, TURN_RANGE = 300, 300
MUSIC = 35                    # COSTA (the beach's own theme)

POSITIONS = [
    dict(key="loungers", girl="B", cloud="W", place="loungers", counts=(2, 5), wait="Z"),
    dict(key="sunbed", girl="B", cloud="V", place="sunbed", counts=(1, 4)),
    dict(key="lineup", girl="J", cloud="J", place="surf", spots=6, at=0, counts=(2, 6), oral=True, hold=True),
    dict(key="tanlines", girl="F", cloud="F", place="sand", spots=4, at=-450, counts=(2, 4)),
    dict(key="sunbathers", girl="A", cloud="A", place="sand", spots=4, at=450, counts=(2, 4)),
    dict(key="surfdog", girl="C", cloud="C", place="surf", spots=3, at=-350, counts=(1, 3)),
    dict(key="waves", girl="Y", cloud="D", place="shallows", depth=-45, at=-100, counts=(1, 3)),
    dict(key="splash", girl="H", cloud="H", place="shallows", depth=-70, at=200, counts=(1, 3)),
    dict(key="riptide", girl="U", cloud="U", place="shallows", depth=-55, at=-400, counts=(1, 3)),
    dict(key="sandcastle", girl="I", cloud="I", place="sand", at=0, counts=(1, 3), oral=True, hold=True),
    dict(key="towel", girl="B", cloud="B", place="sand", at=-250, counts=(1, 3)),
    dict(key="kneel", girl="J", cloud="J", place="sand", at=250, counts=(1, 4), oral=True, hold=True),
    dict(key="lifeguard", girl="C", cloud="J", place="sand", at=-650, target="mouth", rel=128, counts=(1, 3),
         oral=True),
    dict(key="lowtide", girl="C", cloud="O", place="surf", at=350, target="entry", rel=0, counts=(1, 3)),
    dict(key="pinned", girl="O", cloud="O", place="sand", at=650, counts=(1, 3), oral=True, hold=True),
]
FIRST = ("loungers", 3)       # it opens down the row of loungers

TALK = {
    "ruby": ["Sun's out, star. Show me what you've got.", "Harder! The tourists are watching!",
             "Watch and learn, ladies.", "Oh! Right there... RIGHT there!"],
    "skye": ["Woohoo! Best beach day EVER!", "Spank me! Go on, do it!", "Faster! Like the waves!",
             "Hehe... sand EVERYWHERE..."],
    "elena": ["This is... a public beach!", "Ah! ...Sorry. Continue.", "I-I can take more. Proceed.",
              "Don't stop... that's an order!"],
    "scarlet": ["Kyahaha! Make them jealous, darling.", "Slower. Let the whole beach WATCH.",
                "Smack my ass, puppy.", "Harder, darling. I'm not made of glass."],
    "tifa": ["Cloud... mmh... the sun feels so good...", "Easy... okay... now harder.",
             "Is this what vacations are like?!", "Hold me tighter..."],
    "aerith": ["Hehe, the ocean's watching!", "Ooh! Do that again!", "Spank me, I've been naughty.",
               "Faster, mister lifeguard!"],
}
COMMENTS = {
    "ruby": ["Amateur.", "My tan's better than her technique.", "Arch your back, babe!",
             "Save some for me, star!", "My turn next. Obviously.", "Is she even trying?"],
    "skye": ["Hahaha! Go go go!", "Ooh, I wanna try that in the water!", "Look at her face!",
             "Spank her! Do it!", "Best. Vacation. Ever.", "Wooo! Cowabunga!"],
    "elena": ["Is that... legal here?", "I'm taking notes.", "Sunscreen check, everyone?",
              "She's very flexible.", "I could do that. Probably.", "This wasn't in the brochure."],
    "scarlet": ["Kyahaha! Sloppy, darling.", "Smack her, puppy!", "Hold her down!", "Pathetic. Again!",
                "Ooh, now THAT'S a show.", "Somebody fetch me a cocktail."],
    "tifa": ["You've got this!", "Everyone wearing sunscreen?", "Pace yourself, Cloud.",
             "She looks happy.", "Go, girl!", "Careful, the sand's hot!"],
    "aerith": ["Hehe, cute!", "Ooh, someone's enjoying herself.", "Cloud, you're getting sunburnt!",
               "Look at those toes curl!", "Hey, save some for me!", "Spank her, Cloud! Hehe."],
}

INTRO = ["“Sun, sand and six gorgeous co-stars!\n Positions change, girls swap in and out.”",
         "“Same rules: tap OK, mind the meter,\n red at either end and we're done. ...ACTION!”"]
LAST_CALL = "Cameraman\n“The sun's going down, people!\n Last set. Give me a FINISHER!”"

# ---- cutaways (as `_movie_loose`'s: `set` = screen offsets from STAGE on the dry sand) ----
STAGE_AT = (0, 230, 0)        # the cutaways' centre: the open sand mid-beach (679 sets STAGE, its screen spot)
STAGE = (0, 0)
CUTS = [
    dict(key="sunscreen", need=["scarlet", "elena", "tifa"],
         set={"scarlet": (0, 10, "lie", "front"), "elena": (25, 5, "kneel", "scarlet"),
              "tifa": (-30, 0, "stand", "scarlet"), "cloud": (60, -15, "stand", "scarlet"),
              "camera": (-80, -20, "stand", "scarlet")},
         talk="Scarlet\n“Elena, darling. Sunscreen. My back.\n Every inch.”{NEW}"
              "Elena\n“I'm a Turk, not a lotion dispenser.”{NEW}"
              "Scarlet\n“You're a Turk who wants a raise.”{NEW}"
              "Elena\n(...She does it. Thoroughly.){NEW}"
              "Tifa\n“You missed a spot. ...Lower. Hehe.”"),
    dict(key="ball", need=["skye", "ruby", "aerith"],
         set={"skye": (-40, 0, "stand", "ruby"), "ruby": (40, 0, "stand", "skye"),
              "aerith": (0, 15, "stand", "skye"), "cloud": (0, -25, "stand", "aerith"),
              "camera": (-85, -20, "stand", "aerith")},
         talk="Skye\n“Beach ball! Heads up, Ruby!”{NEW}"
              "Ruby\n(Thwap!) “OW! My FACE!”{NEW}"
              "Skye\n“...Sorry! You were supposed to catch it!”{NEW}"
              "Aerith\n“Hahaha! Ten points to Skye!”{NEW}"
              "Ruby\n“This is war, bubblegum.”"),
    dict(key="jellyfish", need=["elena", "tifa", "aerith"],
         set={"elena": (0, 10, "kneel", "front"), "tifa": (25, 5, "kneel", "elena"),
              "aerith": (-30, 0, "stand", "elena"), "cloud": (60, -15, "stand", "elena"),
              "camera": (-80, -25, "stand", "elena")},
         talk="Elena\n“Ow ow OW! Something stung me!\n On my BUTT!”{NEW}"
              "Tifa\n“Jellyfish. Hold still, it's okay.”{NEW}"
              "Aerith\n“Someone has to... you know. Pee on it.”{NEW}"
              "Elena\n“...WHAT?!”{NEW}"
              "Aerith\n“Kidding! Hehe. Mostly.”"),
    dict(key="castle", need=["skye", "aerith"],
         set={"skye": (-15, 5, "kneel", "aerith"), "aerith": (15, 5, "kneel", "skye"),
              "cloud": (50, -10, "stand", "skye"), "camera": (-70, -20, "stand", "skye")},
         talk="Skye\n“Sandcastle break! I'm building\n Shinra HQ!”{NEW}"
              "Aerith\n“Ooh! And I'll be the giant who\n stomps on it!”{NEW}"
              "Skye\n“NOOO! Fifty floors of sand!”{NEW}"
              "Cameraman\n“...Are we filming this? Fine. B-roll.”"),
    dict(key="volley", need=["tifa", "ruby", "scarlet", "skye"],
         set={"tifa": (-40, 5, "stand", "ruby"), "ruby": (-15, -5, "stand", "tifa"),
              "scarlet": (30, 0, "stand", "skye"), "skye": (55, 5, "stand", "scarlet"),
              "cloud": (5, 25, "stand", "front"), "camera": (-90, -25, "stand", "cloud")},
         talk="Tifa\n“Volleyball! Tifa and Ruby versus\n Scarlet and Skye!”{NEW}"
              "Scarlet\n“Kyahaha! Losers serve the winners.\n In EVERY sense.”{NEW}"
              "Ruby\n“Bring it, granny.”{NEW}"
              "Scarlet\n“...GRANNY?!”",
         ask="Skye\n“Cloud! You're the referee!\n Who won?!”",
         choices=[("Tifa and Ruby.", "Ruby\n“Obviously.”{NEW}Scarlet\n“RIGGED!”", dict(gil=5, annoy=["scarlet"])),
                  ("Scarlet and Skye.", "Skye\n“WOOO!”{NEW}Tifa\n(She just laughs.)", dict(gil=5)),
                  ("Everybody won.", "Ruby\n“Coward.”{NEW}Tifa\n“Diplomat.”", dict())]),
    dict(key="sunburn", need=["ruby", "tifa"],
         set={"ruby": (0, 5, "stand", "front"), "tifa": (30, 0, "stand", "ruby"),
              "cloud": (60, -15, "stand", "ruby"), "camera": (-70, -20, "stand", "ruby")},
         talk="Ruby\n“Why does everything sting?!”{NEW}"
              "Tifa\n“...Ruby. Your butt is bright red.”{NEW}"
              "Ruby\n“That's not the sun. That's Cloud.”{NEW}"
              "Cameraman\n“Ha! Keep that in the cut!”"),
    dict(key="shell", need=["aerith", "elena"],
         set={"aerith": (0, 5, "stand", "cloud"), "cloud": (25, 0, "stand", "aerith"),
              "elena": (-35, 0, "stand", "aerith"), "camera": (75, -20, "stand", "aerith")},
         talk="Aerith\n“Look, Cloud! A shell! Hold it to your\n ear... can you hear it?”{NEW}"
              "Cloud\n“...The sea.”{NEW}"
              "Aerith\n“No, silly. It's saying 'he's cute'.”{NEW}"
              "Elena\n(She picks one up and listens,\n very seriously.)"),
    dict(key="shark", need=["skye", "elena", "scarlet"],
         set={"skye": (0, 0, "stand", "front"), "elena": (-30, 5, "stand", "skye"),
              "scarlet": (35, 5, "stand", "skye"), "cloud": (65, -15, "stand", "skye"),
              "camera": (-80, -25, "stand", "skye")},
         talk="Skye\n“SHAAAARK!!”{NEW}"
              "(Everyone scrambles up the sand.){NEW}"
              "Elena\n“...It's a log.”{NEW}"
              "Skye\n“It's a log SHAPED like a shark!”{NEW}"
              "Scarlet\n“I broke a NAIL for that log.”"),
    dict(key="popsicle", need=["tifa", "aerith", "skye"],
         set={"tifa": (-20, 5, "stand", "cloud"), "aerith": (15, 5, "stand", "cloud"),
              "skye": (40, 0, "kneel", "cloud"), "cloud": (0, -20, "stand", "front"),
              "camera": (-80, -20, "stand", "cloud")},
         talk="Tifa\n“Popsicles! I've got watermelon,\n mango and... banana.”{NEW}"
              "Aerith\n“Banana. Obviously. Hehe.”{NEW}"
              "Skye\n(Slurrrp.) “Brain freeze! Brain freeze!”{NEW}"
              "Cameraman\n“Aerith, do that again. Slower.\n For the camera.”"),
    dict(key="tanlines", need=["ruby", "scarlet", "elena"],
         set={"ruby": (-30, 5, "stand", "cloud"), "scarlet": (0, 10, "stand", "cloud"),
              "elena": (30, 5, "stand", "cloud"), "cloud": (0, -25, "stand", "front"),
              "camera": (-85, -20, "stand", "cloud")},
         talk="Ruby\n“Tan line contest! No lines wins.”{NEW}"
              "Scarlet\n“Darling, I tan on the yacht. Nude.”{NEW}"
              "Elena\n“...I have a line from my holster.”",
         ask="Ruby\n“Cloud. Inspect us. Who wins?”",
         choices=[("Scarlet. Not a line on her.", "Scarlet\n“Kyahaha! Naturally.”{NEW}Ruby\n“She's PAINTED.”",
                   dict(gil=5, annoy=["ruby"])),
                  ("Elena's holster line is cute.", "Elena\n“...C-cute?”{NEW}(She turns very pink.)", dict(gil=5)),
                  ("I need a closer look.", "Ruby\n“Smooth.”{NEW}Scarlet\n“Down, puppy.”", dict(gil=10))]),
    dict(key="dare", need=["skye", "ruby", "aerith", "tifa"],
         set={"skye": (0, 5, "stand", "cloud"), "ruby": (-30, 0, "stand", "skye"),
              "aerith": (30, 0, "stand", "skye"), "tifa": (55, 5, "stand", "cloud"),
              "cloud": (0, -25, "stand", "skye"), "camera": (-80, -20, "stand", "skye")},
         talk="Skye\n“Dare! Cloud runs into the sea and\n back! Butt naked! Go!”{NEW}"
              "Ruby\n“He's ALREADY butt naked.”{NEW}"
              "Skye\n“...Then he has to do a cartwheel.”",
         ask="Aerith\n“Well, Cloud?”",
         choices=[("Fine. One cartwheel.", "(Cloud cartwheels into the surf.){NEW}Tifa\n“...Oh my.”{NEW}"
                   "Aerith\n“Everything flipped. EVERYTHING.”", dict(gil=10)),
                  ("Absolutely not.", "Skye\n“Booooo!”{NEW}Tifa\n“Leave him alone. Hehe.”", dict())]),
    dict(key="crab", need=["scarlet", "elena", "tifa"],
         set={"scarlet": (0, 5, "stand", "front"), "elena": (-35, 0, "stand", "scarlet"),
              "tifa": (35, 0, "stand", "scarlet"), "cloud": (65, -15, "stand", "scarlet"),
              "camera": (-80, -25, "stand", "scarlet")},
         talk="Scarlet\n“EEK! Something PINCHED me!”{NEW}"
              "Tifa\n“...A crab. On your toe. It's tiny.”{NEW}"
              "Scarlet\n“Get it OFF, Elena! That's an ORDER!”{NEW}"
              "Elena\n“...I report to Tseng, actually.”"),
    dict(key="hojo", need=["aerith", "skye", "elena"],
         set={"aerith": (-20, 5, "stand", "front"), "skye": (15, 5, "stand", "front"),
              "elena": (45, 0, "stand", "front"), "cloud": (0, -25, "stand", "front"),
              "camera": (-80, -20, "stand", "front")},
         talk="Elena\n“...Is that Professor Hojo?\n On a beach towel? With two girls?”{NEW}"
              "Aerith\n(She ducks behind Cloud.){NEW}"
              "Skye\n“Ew. Is he WATCHING us?”{NEW}"
              "Cameraman\n“He bought a ticket. ...Moving on!”"),
    dict(key="sunset", need=["tifa"],
         set={"tifa": (0, 5, "stand", "front"), "cloud": (20, 5, "stand", "front"),
              "camera": (-80, -20, "stand", "tifa")},
         talk="Tifa\n“Hey... look at the sky. We never get\n sunsets like this in Midgar.”{NEW}"
              "Cloud\n“...Yeah.”{NEW}"
              "Tifa\n(She leans her head on his shoulder\n for one quiet second.){NEW}"
              "Skye\n(from somewhere) “GET A ROOM!”"),
    dict(key="race", need=["tifa", "ruby", "skye", "elena"],
         set={"tifa": (-45, 5, "stand", "front"), "ruby": (-15, 5, "stand", "front"),
              "skye": (15, 5, "stand", "front"), "elena": (45, 5, "stand", "front"),
              "cloud": (0, -25, "stand", "front"), "camera": (-90, -25, "stand", "tifa")},
         talk="Ruby\n“Race to the buoy and back!\n Loser does the next scene on top!”{NEW}"
              "Skye\n“Isn't that... the WINNER'S prize?”{NEW}"
              "Elena\n“I swam for the Turks. Ready.”",
         ask="Tifa\n“Cloud, call it! Who won?”",
         choices=[("Elena. By a mile.", "Elena\n“...Turks don't lose.”{NEW}Ruby\n“She CHEATED.”",
                   dict(gil=5, annoy=["ruby"])),
                  ("Tifa.", "Tifa\n“Hehe. Zangan's training!”{NEW}Skye\n“Lame!”", dict(gil=5)),
                  ("It was a tie.", "Ruby\n“Coward.”{NEW}Elena\n“...Acceptable.”", dict())]),
    dict(key="cocktail", need=["scarlet", "aerith", "ruby"],
         set={"scarlet": (0, 10, "lie", "front"), "aerith": (-30, 0, "stand", "scarlet"),
              "ruby": (30, 0, "stand", "scarlet"), "cloud": (60, -15, "stand", "scarlet"),
              "camera": (-80, -20, "stand", "scarlet")},
         talk="Scarlet\n“Puppy. A cocktail. Something blue\n with an umbrella in it.”{NEW}"
              "Aerith\n“Ooh, me too! Pink! With TWO umbrellas!”{NEW}"
              "Ruby\n“Make mine a double. I'm working.”",
         ask="Scarlet\n“Well? Fetch, puppy.”",
         choices=[("Coming right up.", "Scarlet\n“Kyahaha! Good boy.”{NEW}Ruby\n“Whipped.”", dict(gil=5)),
                  ("Fetch it yourself.", "Scarlet\n“...How DARE you.”{NEW}Aerith\n“Ooh! Hehe.”",
                   dict(annoy=["scarlet"]))]),
    dict(key="lifeguard", need=["elena", "skye"],
         set={"elena": (0, 5, "lie", "front"), "skye": (25, 5, "kneel", "elena"),
              "cloud": (-30, 0, "stand", "elena"), "camera": (70, -20, "stand", "elena")},
         talk="Skye\n“Elena's not breathing! I'll do\n mouth-to-mouth!”{NEW}"
              "Elena\n“I'm SUNBATHING. Get off me.”{NEW}"
              "Skye\n“Too late, I'm committed!”{NEW}"
              "Cameraman\n“...Keep rolling. KEEP ROLLING.”"),
    dict(key="tide", need=["tifa", "scarlet", "aerith"],
         set={"tifa": (-25, 5, "kneel", "scarlet"), "scarlet": (5, 10, "lie", "front"),
              "aerith": (35, 0, "stand", "scarlet"), "cloud": (60, -15, "stand", "scarlet"),
              "camera": (-80, -20, "stand", "scarlet")},
         talk="Aerith\n“Shh... Scarlet fell asleep. Let's bury\n her in the sand!”{NEW}"
              "Tifa\n“...Just up to the neck. And give her\n a mermaid tail.”{NEW}"
              "Scarlet\n(waking) “...Why can't I move my legs?”{NEW}"
              "Scarlet\n“...Why are my legs a FISH?!”"),
]
CUT_FADE = 8
INTRO_SET = {"camera": (-45, -20, "stand", "centre"), "cloud": (15, 5, "stand", "camera"),
             "ruby": (-15, 12, "stand", "camera"), "skye": (40, 12, "stand", "camera"),
             "elena": (-40, 15, "stand", "camera"), "scarlet": (60, -5, "stand", "camera"),
             "tifa": (20, 25, "stand", "camera"), "aerith": (-5, 30, "stand", "camera")}

END_TALK = ("Tifa\n“Well. That was... a LOT of sand.”{NEW}"
            "Ruby\n“I'll be finding it for a week.”{NEW}"
            "Aerith\n“Hehe. Same time next summer?”{NEW}"
            "Elena\n“...I'd like that in writing.”{NEW}"
            "Scarlet\n“Kyahaha. Darlings, that's a wrap.”")

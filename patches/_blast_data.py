"""(user) Blast-off (673): the movie's third scene for a co-star, with Cid, in the space capsule.
Unlocked when Cid's affection is at max (`_cid`). One set for every co-star: the capsule field
itself (`SET`, rcktin7 = the escape pod, only entered by the story's launch; the dates copied it
first), the co-star picked at runtime by MOVIE_GIRL. Lines follow `_movie_profiles`.
LINES[key][position]: her lines while it plays ("C:" Cloud, "I:" Cid, "(...)" an action; muffled
where her mouth is busy). Lines are 3 rows at most, ~38 characters per row.
"""

SET = "rcktin7"
ARRIVE = (40, 150)                # the player's arrival (670's MAPJUMP), on the capsule's left floor strip
BLAST_ON = ((1, 111), 1)          # set by the cameraman's Blast-off pick, cleared on arrival (`_cid.MET`'s byte)
UNLOCK = 20                       # Cid's affection that unlocks it (his max)
ORDER = ["ruby", "skye", "elena", "scarlet", "tifa", "aerith"]     # (G: the co-star's index)
NAMES = {"ruby": "Ruby", "skye": "Skye", "elena": "Elena", "scarlet": "Scarlet", "tifa": "Tifa", "aerith": "Aerith"}
POSITIONS = ["rocketman", "twinjets", "exhaust"]
TITLES = {"rocketman": "Rocketman", "twinjets": "Twin Jets", "exhaust": "Exhaust"}
MINUTE = 1800                     # frames a position (user: a minute each)
SWITCH = 300                      # Twin Jets: she turns to the other man every 10 s (user), 6 halves
PAY_X = 2                         # (user) her gil a press x 2: two men on set
THEME = 20                        # SIDO: Cid's Theme (user)

OPENING = ["“Blast-off, people! Cid Highwind, our\n guest star, built this capsule himself.”",
           "“He says if anybody touches the red\n button we all die. So... don't.”"]
CID_INTRO = "Cid\n“Alright, let's light this candle.\n Spiky, you ready? 'Course you are.”"
INTRO = {
    "ruby": ["“Two at once? Fine. I'll still be the\n one everybody remembers.”"],
    "skye": ["“Ooh, a rocket! Does it go up? Do WE\n go up? I want to press the button!”"],
    "elena": ["“Two... of you. That's... a lot of\n paperwork. Okay. Rules first.”"],
    "scarlet": ["“Kyahaha! The pilot AND the merc. I'll\n be directing, darlings. Positions.”"],
    "tifa": ["“Cid? Shera's going to kill you. ...Okay.\n Just look after each other, alright?”"],
    "aerith": ["“A space capsule? With you two? This is\n going to be the BEST story.”"],
}
LINES = {
    "ruby": {
        "rocketman": ["Mmph! Mmh... (She grips Cid's thighs.)", "I:Hah! She's a natural, Spiky!",
                      "Mmf! Mmmh! (Ruby's eyes say: watch me.)", "C:...She's keeping up. Barely."],
        "twinjets": ["(She switches sides, smug.)\n“Try and keep up, boys.”", "Mmph! Mmh-mmh!",
                     "I:Watch the hair, I'm a pilot not\n a barber!", "Mmmf... (She's counting. Competitively.)"],
        "exhaust": ["“Both of you. At once. ...I win.”", "I:Hold her steady, Spiky!",
                    "“Ahh! Harder! I'm not some rookie!”", "C:...She asked for it."],
    },
    "skye": {
        "rocketman": ["Mmph! (Skye waves at the camera.)", "I:Kid's got lungs. Good for flyin'.",
                      "Mmmh! Mmf-mmf! (She's giggling.)", "C:Skye. Focus."],
        "twinjets": ["(She spins to the other one.)\n“Wheee! My turn! Your turn!”", "Mmph! Mmmh!",
                     "I:Damn, she turns quicker than\n the Highwind!", "Mmf! (Skye gives a thumbs up.)"],
        "exhaust": ["“We're flying! We're actually flying!”", "I:Hang on, kid, we're hittin' turbulence!",
                    "“Faster! Full throttle! Ahh!”", "C:...She's having the time of her life."],
    },
    "elena": {
        "rocketman": ["Mmph... mmh. (She takes careful notes,\n mentally.)", "I:Relax, Turk. Breathe through\n your nose.",
                      "Mmf! Mmh... (She nods. Diligently.)", "C:You're doing fine, Elena."],
        "twinjets": ["(She turns, flustered.)\n“Is it... is it his turn now?”", "Mmph... mmmh!",
                     "I:She's polite about it. Kinda\n creepy, Spiky.", "Mmf... (Elena keeps eye contact. Bravely.)"],
        "exhaust": ["“This is... not in the manual.\n Nothing is in the manual!”", "I:Easy now. Nice and slow.",
                    "“Ahh... okay. Okay! Still within\n the rules. Probably!”", "C:Elena. Breathe."],
    },
    "scarlet": {
        "rocketman": ["Mmph! (She snaps her fingers: faster.)", "I:Lady, I don't take orders\n from the passenger!",
                      "Mmf! Mmmh! (She's still somehow in\n charge.)", "C:...She's directing. With her mouth full."],
        "twinjets": ["(She turns, slowly, on her terms.)\n“You next, flyboy.”", "Mmph! Mmh!",
                     "I:She bites, I swear to god she\n bites.", "Mmf... (Scarlet smirks around it.)"],
        "exhaust": ["“Kyahaha! Both of you, and I'm still\n on top. Figuratively.”", "I:Damn woman, ease up!",
                    "“Ahh! Harder, you peasants!”", "C:...She's enjoying this way too much."],
    },
    "tifa": {
        "rocketman": ["Mmph... (She squeezes Cid's leg:\n you okay?)", "I:She's checkin' on ME. Unbelievable.",
                      "Mmf! Mmmh... (Tifa giggles.)", "C:Tifa... you're amazing."],
        "twinjets": ["(She turns, smiling.)\n“Fair's fair. Your turn, Cid.”", "Mmph! Mmmh!",
                     "I:Spiky, you're a lucky bastard.\n You know that?", "Mmf... (Tifa winks at Cloud.)"],
        "exhaust": ["“Hah... I've got you both. Don't\n let go, okay?”", "I:I ain't lettin' go, girl.",
                    "“Ahh! Okay... okay! Keep going!”", "C:...I've got you, Tifa."],
    },
    "aerith": {
        "rocketman": ["Mmph! (Aerith's eyes sparkle.)", "I:This one's trouble, Spiky.\n I can tell.",
                      "Mmf! Mmmh! (She tickles Cid's knee.)", "C:Aerith... behave."],
        "twinjets": ["(She twirls round.)\n“Eeny, meeny... you!”", "Mmph! Mmh!",
                     "I:She's laughin'. Why's she\n laughin'?", "Mmf... (She's definitely laughing.)"],
        "exhaust": ["“Ahh! A flower between two... rocks!”", "I:Rocks?! I'm a goddamn pilot!",
                    "“Ahh! More! Don't stop now!”", "C:...Rocks."],
    },
}
AFTERMATH = {
    "ruby": "Ruby\n(Ruby straightens up, triumphant.)\n“Two men. Zero chance. Next.”",
    "skye": "Skye\n(Skye floats on the spot, starry-eyed.)\n“Can we go to actual space next time?”",
    "elena": "Elena\n(Elena sits very still.)\n“...I'm going to need a vacation.”",
    "scarlet": "Scarlet\n(Scarlet fixes her lipstick.)\n“Kyahaha! Acceptable, gentlemen.”",
    "tifa": "Tifa\n(Tifa laughs, breathless.) “Don't tell\n Shera. And don't tell Barret!”",
    "aerith": "Aerith\n(Aerith beams.) “Best. Launch. Ever.\n I'm telling EVERYONE.”",
}
CID_AFTER = "Cid\n(Cid lights a cigarette.)\n“...Now THAT was a launch.”"
# Cid's hold lines (670 `_stop_ops`: the bonus is added), his stern reminder
CID_HOLD = ["Stay right there, sweetheart.", "Hold it... hold it... HOLD IT.", "Don't you move a damn inch."]
CID_STERN = ["I said stay put!", "Easy... easy... not yet.", "Countdown ain't done, lady!"]

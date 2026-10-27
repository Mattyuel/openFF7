"""(user) Tifa's aerobics classes (693_gym; replaces the gym's one-on-one sessions with Wedge / Biggs / Jessie):
"turn the gym session into aerobics classes, with select characters dressed in colourful spandex like Tifa,
doing synchronised aerobics sessions with Tifa out front ... high paced prompts without the meter ... a room with
closer, lower angles, like the Junon room where you enter the cargo ship and do a drill for Rufus ... everyone
would face the screen ... paid by patrons for the session depending on how good it is ... like 5 people joining
you from a pool at random. They all need to have the same dance moves."

Tifa in the Wall Market gym offers "Run a class." -> FIELD = a copy of the Junon dock (jundoc1a, the send-off
drill for Rufus in front of the cargo ship's ramp), script blanked. Five classmates from `POOL` at random, each
in their own colourful spandex, in two rows behind Tifa, everyone facing the camera, all doing the same moves
(`_aerobic_poses`) in sync. One button prompt a move cycle (two beats: `_aerobic_poses.BEATS` x 2 frames; much
quicker than the films), no meter. The routine `ROUTINE` steps through the moves (Tifa calls each), two tempos.
At the end the patrons pay by the grade (hits / prompts) plus a tip a combo. Data only."""

FIELD = "blackbgj"              # a debug room only startmap leads to, replaced by a copy of the dock
BASE = "jundoc1a"               # the Junon dock: the cargo ship, the send-off ceremony
GYM = "mkt_mens"                # Tifa offers the class in the Wall Market gym
TIFA_AT = (-40, 120)            # (her spot there)
MUSIC = 16                      # AKAO 10 index: PARADE (unverified choice: upbeat)

# the layout, in screen pixels (x right, y down, from the background's centre), unprojected onto the dock's
# floor (user: "bring everyone closer to the screen"; the second test render, at the front of the dock)
VIEW = (38, 150)                # the hidden player (the camera centres on him; clamped to the background)
# six columns ~55 px apart across the 320-pixel view, one dancer each (user: nobody hidden behind Tifa)
SLOTS = [(-100, 170), (10, 170), (120, 170), (-45, 192), (175, 192)]   # back row 3, middle row 2
TIFA_S = (65, 222)              # Tifa out front, in her own column

# the pool (user: "Aerith, Yuffie, Cloud, Cid and others in colorful spandex"): key, name, donor (field, model),
# kind ("girl": the standard body painted; "man": his own clothes resprayed), tag, bust, skin (Barret's: his face
# isn't light enough for `_female_body.face_skin`) and skin_near (his trousers are close to his skin tone), colours (B, G, R):
# top (leotard / tank top), tights, leg warmers
POOL = [
    dict(key="aerith", name="Aerith", donor=("blue_2", 2), kind="girl", tag="L", bust=0.5,
         top=(200, 60, 170), tights=(180, 105, 255), warmers=(240, 240, 240)),
    dict(key="yuffie", name="Yuffie", donor=("blue_2", 8), kind="girl", tag="M", bust=0.7,
         top=(60, 230, 120), tights=(45, 40, 40), warmers=(0, 140, 255)),
    dict(key="cloud", name="Cloud", donor=("blue_2", 0), kind="man", tag="C",
         top=(150, 30, 230), tights=(40, 30, 30), warmers=(0, 230, 255)),
    dict(key="cid", name="Cid", donor=("blue_2", 3), kind="man", tag="I",
         top=(0, 120, 255), tights=(200, 120, 20), warmers=(60, 240, 160)),
    dict(key="barret", name="Barret", donor=("blue_2", 4), kind="man", tag="B", skin=(40, 56, 85), skin_near=24,
         top=(40, 220, 255), tights=(30, 30, 200), warmers=(240, 240, 240)),
    dict(key="elena", name="Elena", donor=("datiao_6", 10), kind="girl", tag="O", bust=1.0,
         top=(255, 140, 20), tights=(45, 40, 40), warmers=(240, 240, 240)),
    dict(key="jessie", name="Jessie", donor=("tin_2", 5), kind="girl", tag="P", bust=1.0,
         top=(0, 120, 255), tights=(160, 40, 120), warmers=(60, 240, 160)),
]
SNEAKERS = (235, 235, 235)       # the men's shoes
PREFIX = {"tifa": "VT", "aerith": "VA", "yuffie": "VY", "cloud": "VC", "cid": "VI", "barret": "VB",
          "elena": "VE", "jessie": "VJ"}   # their anims: <prefix><move><tempo>

KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}"),
        (0x10, "{PURPLE}[MENU]{WHITE}")]
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (the squat contest's squat, as the films)
COMBO = 8                       # hits in a row = a combo: a cheer and `COMBO_TIP` gil
COMBO_TIP = 15

# the routine: (move letter, tempo 0 / 1, cycles); None as the letter = bounce, no prompts
ROUTINE = [
    (None, 0, 4),
    ("A", 0, 6), ("B", 0, 6), ("C", 0, 6), ("G", 0, 6),
    ("D", 0, 6), ("E", 0, 6), ("F", 0, 6),
    ("I", 1, 8), ("A", 1, 8), ("B", 1, 8), ("H", 1, 8), ("D", 1, 8), ("C", 1, 6), ("H", 1, 8),
    (None, 0, 3),
]
CALLS = {  # Tifa's call as a move starts (window 2, closes itself)
    None: "Tifa\n“Keep bouncing! Breathe!”",
    "A": "Tifa\n“Knee lifts! Pump those arms!”",
    "B": "Tifa\n“Jumping jacks! Clap it up top!”",
    "C": "Tifa\n“Heel kicks! Kick your butt!”",
    "D": "Tifa\n“Cross crunches! Elbow to knee!”",
    "E": "Tifa\n“Side knees! Pull it down!”",
    "F": "Tifa\n“Twist! Arms long!”",
    "G": "Tifa\n“Chest fly! Hug it in!”",
    "H": "Tifa\n“High knees! Go, go, go!”",
    "I": "Tifa\n“Squat and punch! Hit it hard!”",
}
FAST = "Tifa\n“Double time, everyone!”"           # (the first block at tempo 1)
CHEERS = ["Tifa\n“Yes! Look at you go!”", "Tifa\n“That's it! Feel the burn!”",
          "Tifa\n“Perfect timing, everyone!”", "Tifa\n“Woo! Keep it up!”"]
FLUBS = {  # a classmate's line on a miss (if they're in the class)
    "aerith": "Aerith\n“Oops, other left! Ehehe.”",
    "yuffie": "Yuffie\n“Wait, wait, which way?!”",
    "cloud": "Cloud\n“...I'm fine. Keep going.”",
    "cid": "Cid\n“Dammit, my knee!”",
    "barret": "Barret\n“Whoa! Gimme a sec!”",
    "elena": "Elena\n“Sorry! I lost count!”",
    "jessie": "Jessie\n“Missed it! Totally meant to.”",
}
SAY = 70                        # frames a call / cheer / flub stays up

INTRO = ["Tifa\n“Welcome to Tifa's Aerobics!\n Everyone in your spot, facing front!”",
         "Tifa\n“Follow me and keep the beat.\n Ready? Let's MOVE!”"]
HOW = "Press the button shown on each beat.\nThe class keeps time with you: the more\nyou hit, the more the patrons pay."
GRADES = [  # (share of the prompts hit, Tifa's line)
    (0.9, "Tifa\n“Amazing class, everyone! That was\n PERFECT!”"),
    (0.7, "Tifa\n“Great class! You all kept up\n really well!”"),
    (0.45, "Tifa\n“Not bad! We'll get it tighter\n next time.”"),
    (0.0, "Tifa\n“Um... good effort? Let's... practise\n that one again.”"),
]
FEES = (60, 40, 25, 10)         # gil a patron by grade (5 patrons)
REACT = {  # a classmate's reaction by grade (best first)
    "aerith": ["Aerith\n“That was so much fun! Same time\n tomorrow?”", "Aerith\n“Phew! I'm all sparkly with sweat!”",
               "Aerith\n“I think my arms went somewhere\n else for a bit.”", "Aerith\n“...Can we do the one\n with the flowers next time?”"],
    "yuffie": ["Yuffie\n“Ninja reflexes! Nailed it!”", "Yuffie\n“Pretty good! For normal people.”",
               "Yuffie\n“I was totally the best one,\n though.”", "Yuffie\n“This is harder than stealing\n materia!”"],
    "cloud": ["Cloud\n“...That wasn't bad.”", "Cloud\n“Not bad. My legs disagree.”",
              "Cloud\n“Let's not talk about it.”", "Cloud\n“...Why am I wearing this.”"],
    "cid": ["Cid\n“Hot damn! That's how ya do it!”", "Cid\n“Not bad for an old pilot, huh?”",
            "Cid\n“Need a smoke after that.”", "Cid\n“Shera's never hearin' about this.”"],
    "barret": ["Barret\n“Hell yeah! I'm pumped!”", "Barret\n“That's a workout, foo'!”",
               "Barret\n“My gun arm keeps throwin'\n me off!”", "Barret\n“...I'm takin' my money back.\n Kidding. Mostly.”"],
    "elena": ["Elena\n“Flawless! The Turks could use\n this routine!”", "Elena\n“Good session. I'll report it\n favourably.”",
              "Elena\n“I was a beat behind. Don't\n tell Tseng.”", "Elena\n“That did NOT go to plan.”"],
    "jessie": ["Jessie\n“That's going in my stunt reel!”", "Jessie\n“Woo! I'm sweating like a\n reactor core!”",
               "Jessie\n“I improvised a little. Artistic\n choices!”", "Jessie\n“Let's call that one a\n rehearsal.”"],
}
PAID = "The patrons paid {VAR} gil."
AGAIN = ("Tifa\n“Another class?”", ["Another class!", "That's it for today."])
BYE = "Tifa\n“Great work, coach. Same time tomorrow!”"
TIFA_TALK = dict(greet="Tifa\n“I've got a class ready to go.\n Want to run it?”",
                 ask=("Tifa\n“Coach?”", ["Run a class.", "Not now."]),
                 no="Tifa\n“They'll be warming up.”")

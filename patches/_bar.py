"""(user) The 7th Heaven bar shift (692_bar): Tifa serves, Cloud is security. "A service prompt minigame, where
customers order a drink and that corresponds with a prompt, and you're paid for making the drink ... multiple
prompts on screen at once and you have to triage the requests: some prompts stay on screen longer than others and
some take longer to make, and you can't make more than one drink at a time ... beer, wine, spirit, cocktail. There
are also rowdy customers that have either had too much to drink or are angry from missing orders. You'll need to
have Cloud escort them out, which also takes time from making drinks. It should be obvious when you're busy:
'Tifa is busy making a {drink}'."

Three stools, three order windows (one each, over the customer), a fourth window for what Tifa / Cloud is busy
with. Data only."""

FIELD = "blackbgi"              # a debug room only startmap leads to, replaced by a copy of the bar
BASE = "mds7pb_1"
ARRIVE = (-110, -150)           # (user: the camera stayed on Cloud) where Marle's jump lands = the set's hidden
                                # player (the camera follows it; the jump's spot wins over the init's XYZI)
MUSIC = 41                      # AKAO 10 index: the bar's own MUSIC 00 (music block id 42)
SHIFT_FRAMES = 3600             # two minutes of orders, then last orders
LEAD_IN = 60                    # frames before the first customer sits down

# the drinks: (name, "a ..." for the busy line, button mask, button label, make frames, price gil)
DRINKS = [
    ("Beer", "a beer", 0x220, "[OK]", 40, 20),
    ("Wine", "a glass of wine", 0x40, "[CANCEL]", 75, 35),
    ("Spirit", "a spirit", 0x80, "[SWITCH]", 105, 50),
    ("Cocktail", "a cocktail", 0x10, "[MENU]", 190, 90),
]
ESCORT_KEY = (0x08, "[PAGEDOWN]")   # R1: Cloud escorts a rowdy customer out
QUICK_TIP = 10                  # gil more when served with more than URGENT frames of patience left
URGENT = 90                     # frames of patience left when the order turns urgent ("!!")
PATIENCE = (240,)               # frames: base + PATIENCE_BY[drink] + RANDOM (0-255): beers wait least, cocktails most
PATIENCE_BY = [-60, 0, 30, 120]
ROWDY_PATIENCE = 240            # frames a rowdy customer waits for Cloud before he trashes the place
ROWDY_ODDS = 32                 # in 256: a new customer arrives already drunk and rowdy
ANGRY_ODDS = 128                # in 256: a missed order turns the customer rowdy instead of leaving
TRASH_COST = 100                # gil: a rowdy customer left alone breaks things (and the others leave)
GAP = (30, 90)                  # frames between a customer leaving and the next sitting down (base, range)
DRINK_TIME = 45                 # frames a served customer sits with his drink before leaving

# spots (mds7pb_1): (user: patrons "spawning under the bar and taking a step then respawning") the stools are the
# walkmesh squares at x -143, top z 50 (y -76 / -146 / -217 / -287); a patron sits as the game's own scene seats
# Cloud: standing in the aisle at x STAND_X (-95) facing the counter (SEAT_DIR), then CXDC once (a step up onto the
# stool, sat) and held. Tifa behind the counter, Cloud's post, the door = the exit line on the right wall
# (gateway x 278-287, y -46..45)
SEATS = [(-143, -76), (-143, -146), (-143, -217)]
STAND_X = -95                                   # where a patron stands to sit / stands up (rowdy) at his stool
SEAT_DIR = 0xC0
TIFA_AT, TIFA_DIR = (-270, -170), 0x40          # behind the counter, facing the stools
MAKE_DIR = 0xC0                                 # (turned to the shelf while making, as the original scene)
CLOUD_POST, CLOUD_DIR = (40, -60), 0xC0
DOOR = (240, 0)
AISLE = (-95, -30)                              # the top of the aisle in front of the stools (walks go through it)
BESIDE = 28                                     # Cloud stops this far up the aisle from the patron he walks out
WALK_STEP = 4.0                                 # (field units a frame: the walks step XYZI, no MOVE: MOVE got stuck
                                                # on the walkmesh's separate pieces, user)
MARLE_AT, MARLE_DIR = (120, -40), 0xC0
HEAD_Z = 90                                     # a seated customer's head above the floor (window placement)
WIN_RIGHT, WIN_TOP, WIN_GAP = 22, 40, 28        # order windows: right of the head; from y 40, 28 px apart

INTRO = [
    "Tifa\n“Doors open in a minute. Cloud, you're on\n the door. Anyone gets rowdy, you walk\n them out. Gently.”",
    "Cloud\n“...Define gently.”",
    "Tifa\n“Feet stay on the ground.”",
]
HOW = ("Orders appear over each customer: press the\ndrink's button to make it. One drink at a\n"
       "time: a cocktail takes a while, a beer is\nquick. {PURPLE}[PAGEDOWN]{WHITE} sends Cloud for a rowdy one.")
BUSY = "Tifa is busy making %s..."
ESCORTING = "Cloud is escorting a rowdy customer out..."
ROWDY = ["Drunk!", "Angry!"]                    # (the prompt's first word: arrived drunk / missed order)
TRASHED = "(Crash!) The rowdy customer smashes a\nchair. The other customers leave."
LAST_ORDERS = "Tifa\n“Last orders!”"
SUMMARY = "Tifa\n“And that's closing time. We made\n {VAR} gil tonight.”"
SUMMARY_LINES = {"good": "Tifa\n“Not bad, partner. Not bad at all.”",
                 "bad": "Tifa\n“...We'll do better tomorrow. Right?”"}
GOOD_NIGHT = 600                # gil for the "good" line
MARLE = dict(
    greet="Marle\n“Tifa's minding the bar tonight. She\n could use a hand on the door, if\n you're not busy.”",
    ask=("Marle\n“Well? You working, or drinking?”", ["Work a shift.", "Not tonight."]),
    no="Marle\n“Suit yourself. She'll manage. She\n always does.”",
)

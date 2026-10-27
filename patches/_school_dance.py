"""(user) The school dance (682_school_dance): Tifa, Aerith, Yuffie, Elena and Scarlet in Japanese school
uniforms dancing a synchronised routine on the Gold Saucer's stage, choreographed after ATARASHII GAKKO!'s
style (moves in `_dance_poses`). Completely passive: no prompts, no input, every window closes by itself.
Data only."""

FIELD = "blackbgk"              # the set: the debug room's "Dark city fourth street" (only startmap leads there),
BASE = "astage_b"               # replaced wholesale by the original stage (674's show edits its own copy)
FLOOR = 165                     # the stage floor's height
ARRIVE = (0, 250)               # (670's MAPJUMP; the hidden player stays here: the stage camera doesn't scroll)
MUSIC = 8                       # AKAO 10 index (name table): FIDDLE, Fiddle de Chocobo
TEXT_Y = 8                      # the MC's windows: the top of the screen
SAY = 150                       # frames a line stays up

# the cast: key, name, source model (field, model index), .hrc to dress (None = the source's), uniform .hrc
# written, tag (for `_female_body.apply`), bust (x the standard's), head drop (Tifa: as 675), anim prefix
GIRLS = [
    dict(key="tifa", name="Tifa", donor=("astage_b", 2), src=None, hrc="XSTA.HRC", tag="B", bust=1.5,
         head_drop=0.8, prefix="XT"),
    dict(key="aerith", name="Aerith", donor=("astage_b", 1), src=None, hrc="XSAA.HRC", tag="C", bust=0.5,
         head_drop=0.0, prefix="XA"),
    dict(key="yuffie", name="Yuffie", donor=("astage_b", 3), src=None, hrc="XSYA.HRC", tag="D", bust=0.7,
         head_drop=0.0, prefix="XY"),
    dict(key="elena", name="Elena", donor=("datiao_6", 10), src=None, hrc="XSEA.HRC", tag="F", bust=1.0,
         head_drop=0.0, prefix="XE"),
    dict(key="scarlet", name="Scarlet", donor=("blin66_1", 5), src="noskirt", hrc="XSSA.HRC", tag="G", bust=1.5,
         head_drop=0.0, prefix="XS"),
]
MC_DONOR = ("astage_b", 4)      # the King: master of ceremonies
MC_AT = (-580, 520)             # back left, out of the way

# the uniform (B, G, R): a white sailor blouse, navy sailor collar and lapels, red neckerchief, navy pleated
# skirt, white short sleeves, navy knee socks
WHITE, NAVY, RED = (232, 232, 232), (96, 44, 28), (40, 36, 206)
SOCKS = (78, 36, 24)
SKIRT_TOP_PAD = 0.12            # the waistband this far out from the pelvis
SKIRT_FLARE = 1.38              # the hem's width over the waist's
SKIRT_LEN = 0.42                # the hem this far down the thigh (from the hip joint)
PLEATS = 16                     # points round each ring (alternate ones pleated in)
PLEAT_IN = 0.07                 # how far a pleat folds in at the hem

# formations: (x, y) per girl, in GIRLS order (Tifa, Aerith, Yuffie, Elena, Scarlet)
FORMATIONS = {  # (on a 100 grid: every move between them is whole steps over TRAVEL frames)
    "line":    [(0, 350), (-200, 350), (200, 350), (-400, 350), (400, 350)],
    "v":       [(0, 150), (-200, 250), (200, 250), (-400, 350), (400, 350)],
    "stagger": [(0, 450), (-200, 250), (200, 250), (-400, 450), (400, 450)],
    "front":   [(0, 150), (-200, 150), (200, 150), (-400, 150), (400, 150)],
}
TRAVEL = 100                    # frames a formation change takes (then the move goes on in place)
START = "line"

# the routine: (move letter, beats, formation to travel to during it or None, canon: girls one beat apart)
ROUTINE = [
    ("A", 8, None, False),      # heads bowed in a line, the music starts
    ("B", 8, None, False),      # wake up: heads snap up, arms out in a T
    ("C", 16, "v", False),      # stomping march into a V
    ("D", 16, None, False),     # the deep squat, swaying (the hook)
    ("E", 8, None, False),      # shoulder shrugs and hip rolls
    ("F", 8, None, False),      # punches at the sky
    ("G", 8, None, False),      # head-banging
    ("C", 8, "stagger", False), # march into the stagger
    ("I", 16, None, True),      # the arm wave, rippling down the line
    ("H", 16, None, False),     # side steps, arms overhead
    ("J", 16, None, False),     # kicks
    ("K", 4, None, False),      # spin
    ("E", 4, None, False),
    ("N", 8, "front", False),   # running to the front line
    ("L", 8, None, False),      # jumps
    ("M", 8, None, False),      # the slow back-bend
    ("D", 8, None, False),
    ("G", 8, None, False),
    ("K", 4, None, False),
    ("O", 8, None, False),      # the yankee squat stare-down
    ("P", 8, None, False),      # the finish
]

INTRO = [
    "King\n“Ladies and gentlemen, boys and girls!\n Tonight the Gold Saucer proudly presents...”",
    "King\n“...straight from the toughest school on the Planet...\n the GOLD SAUCER SCHOOLGIRLS!”",
]
SHOUTS = {  # (routine step: a line as it starts)
    1: "Yuffie\n“Hit it!”",
    3: "Tifa\n“Lower! Lower!”",
    8: "Scarlet\n“Kya-ha-ha! Keep up, girls!”",
    13: "Aerith\n“Front row, everyone!”",
    19: "Elena\n“...We're not cute. We're LEADERS.”",
}
OUTRO = "King\n“Bravo! BRAVO! The Gold Saucer Schoolgirls,\n everyone! ...Same time tomorrow, girls?”"

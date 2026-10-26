"""(user) Sector 7 Workout: the first parody film (683_workout). Tifa comes to the gym for the first time,
looking for a trainer; Cloud offers to help with her form and spots her squats from behind. Prompts keep
the rhythm: each hit builds the pace, a miss drops it back to slow. Halfway, she notices his 'training
device'; the screen fades and they go on undressed, the pose a little more overt with every step of pace.
Data only."""

FIELD = "blackbg3"              # the set: a debug room only startmap leads to, replaced by a copy of the gym
BASE = "mkt_mens"               # the Wall Market gym (the squat contest's)
ARRIVE = (10, 160)              # (670's MAPJUMP; the init moves the hidden player to FOCUS)
FOCUS = (10, 160)               # the hidden player (the camera follows it)
SQUAT_AT = (-35, 185)           # Tifa's spot for the squats (open floor between the bench and the ring)
FACING = (-1, 0)                # she faces screen-left (side-on to the camera); Cloud behind her
INTRO_TIFA = (-55, 165)         # the intro: she has just come in...
INTRO_CLOUD = (-20, 125)         # ...and Cloud is by the floor
CAMERA_AT = (-80, 230)          # the Director, filming from the left
MUSIC = 35                      # AKAO 10 index: COSTA (the movie's music; to choose)
PROMPT_Y = 40                   # the prompt window's top
LINE_Y = 168                    # the talk window during the squats (lower half)
SAY = 100                       # frames a line stays up during the squats

# speed tiers: frames per rep (one squat down and up), slowest first; HITS_UP hits in a row step up a tier
PERIODS = (60, 50, 42, 34, 28, 22)
HITS_UP = 4
PART_A_END = 4                  # part one ends after this many hits at the top tier
PART_B_REPS = 48                # part two: this many prompts, then the finale
PAY_HIT = 10                    # gil per hit x (tier + 1)

# the buttons, as the squat contest names them: (IFKEY mask, the prompt's text)
# (OK as 0x220: IFKEY's mask bit 0x200 is OK too on PC, and 0x20 alone never fired in 670's minigame)
KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]

INTRO = [
    "Tifa\n“Hi... um, I've never been to a gym\n before. Is there a trainer around?”",
    "Cloud\n“You're looking at him.”",
    "Tifa\n“Really? I want to get stronger, but I\n don't know where to start.”",
    "Cloud\n“Form first. Bad technique gets you\n hurt. I'll help you build it right.”",
    "Tifa\n“Okay! Where do we begin?”",
    "Cloud\n“Squats. The foundation of everything.\n I'll spot you from behind.”",
]
HOW = "Press the button shown in time with\nthe squat. Hits build the pace; a miss\nslows it right down."

# part one (clothed): (tier reached for the first time) -> lines
LINES_A = {
    1: ["Cloud\n“Feet shoulder-width apart. Sit back,\n like there's a chair behind you.”",
        "Tifa\n“Like this?”"],
    2: ["Cloud\n“Good. Chest up, knees out over\n your toes.”",
        "Tifa\n“Ooh, I can already feel it in\n my thighs!”"],
    3: ["Tifa\n“Is it supposed to feel this... warm?”",
        "Cloud\n“That's the burn. It means it's\n working.”"],
    4: ["Tifa\n“Cloud... what's that pressing\n against me?”",
        "Cloud\n“...A training device. For your\n posture.”",
        "Tifa\n“Oh... ohh. I think it's working.”"],
    5: ["Tifa\n“Mmmh...! Faster...”"],
}
MISS_A = "Tifa\n“Whoa, wait! Slow down...”"

# part two (undressed)
START_B = ["Tifa\n“Don't stop now... I've got the hang\n of it.”"]
LINES_B = {
    1: ["Cloud\n“Keep that back straight.”", "Tifa\n“Mmm... yes, coach.”"],
    2: ["Tifa\n“Deeper... I want to feel the\n stretch.”"],
    3: ["Cloud\n“Good form. Hold it at the bottom.”", "Tifa\n“Ah...! I'm holding...!”"],
    4: ["Tifa\n“This is the best workout I've\n ever had!”"],
    5: ["Tifa\n“Cloud... Cloud...!”"],
}
MISS_B = "Tifa\n“Ah... you lost the rhythm.\n Start slow again.”"
FINALE = ["Tifa\n“Phew... same time tomorrow, coach?”",
          "Director\n“CUT! That's a wrap! You two are\n naturals.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.\n Great work today.”"

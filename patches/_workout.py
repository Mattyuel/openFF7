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
CAMERA_GAP, CAMERA_LIFT = 14, 22    # (user: up and left, away from them) the Director placed by `_director.spot`:
                                    # this many px left of them on screen, his feet this many px higher
MUSIC = 35                      # AKAO 10 index: COSTA (the movie's music; to choose)
PROMPT_Y = 40                   # the prompt window's top
LINE_Y = 168                    # the talk window during the squats (lower half)
SAY = 100                       # frames a line stays up during the squats

# speed tiers: frames per rep (one squat down and up); (user) each step 10% faster than the last.
# HITS_UP hits in a row step the pace up a tier; a miss drops it back to the slowest
PERIODS = tuple(round(60 * 0.9 ** k) for k in range(8))      # 60 54 49 44 39 35 32 29
HITS_UP = 2                     # (user: 50% shorter; was 3)
PART_A_REPS = 16                # (user: fixed length, progression by performance) part one: this many prompts
PART_B_REPS = 20                # part two: this many prompts, then the finale
PAY_HIT = 10                    # gil per hit x (tier + 1)
CHAT_EVERY = 4                  # (user: long silences) a chatter line every this many reps, when nobody's talking
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # the squat contest's squat (mkt_mens: AKAO 28 08 019d)

# (user: more going on) the hold on her cue: from HOLD_TIER, HOLD_ODDS in 256 a rep is a HOLD prompt; pressed in
# time and kept held, both freeze at the bottom (Cloud holding her down) until she calls it after HOLD_MIN +
# random HOLD_RANGE frames; let go within LETGO frames = a hit plus HOLD_BONUS x (tier + 1); let go before her
# call = a miss; still holding after LETGO = she's mad: MAD_PENALTY off the pay, the pace back to slow, and at
# MAD_LIMIT she walks out (the shoot ends, an affection point lost). Results stay up RESULT_WAIT frames.
HOLD_TIER, HOLD_ODDS = 2, 44
HOLD_MIN, HOLD_RANGE = 30, 60
LETGO = 24
HOLD_BONUS = 3
MAD_PENALTY = 10                # (x PAY_HIT gil)
MAD_LIMIT = 3
RESULT_WAIT = 50
HOLD_LABEL = "HOLD "
# (user: variations) the pose's style changes every STYLE_EVERY reps (`_workout_poses.STYLES`: A clothed
# 0 spotted / 1 sumo, hands behind her head; B 0 bent over / 1 Cloud cocks a leg up / 2 touching her toes)
STYLE_EVERY = 3                 # (user: transitions sooner; was 6)

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
# (user: more variety in the intros) intro line -> [(actor, gesture)] (`_gestures.ANIMS`), played as it shows
INTRO_GESTURES = {0: [("tifa", "think")], 1: [("cloud", "nod")], 2: [("tifa", "ready")], 3: [("cloud", "stretch")],
                  4: [("tifa", "hips")], 5: [("cloud", "warmup")]}
HOW = ("Press the button shown in time with\nthe squat. Hits build the pace; a miss\nslows it right down."
       "{NEW}HOLD: press it and keep it held while\nshe stays down. Let go the moment she\ncalls it, or she'll get mad.")

# part one (clothed): (tier reached for the first time) -> lines
LINES_A = {
    1: ["Cloud\n“Feet shoulder-width apart. Sit back,\n like there's a chair behind you.”",
        "Tifa\n“Like this?”"],
    3: ["Cloud\n“Good. Chest up, knees out over\n your toes.”",
        "Tifa\n“Ooh, I can already feel it in\n my thighs!”"],
    4: ["Tifa\n“Is it supposed to feel this... warm?”",
        "Cloud\n“That's the burn. It means it's\n working.”"],
    5: ["Tifa\n“Cloud... what's that pressing\n against me?”",
        "Cloud\n“...A training device. For your\n posture.”",
        "Tifa\n“Oh... ohh. I think it's working.”"],
    7: ["Tifa\n“Mmmh...! Faster...”"],
}
CHAT_A = [
    "Cloud\n“Breathe out on the way up.”",
    "Tifa\n“How many of these do you do\n a day?”",
    "Cloud\n“...Enough.”",
    "Tifa\n“My legs are shaking already!”",
    "Cloud\n“Weight on your heels.”",
    "Tifa\n“You're a good teacher, Cloud.”",
    "Cloud\n“Don't let your knees cave in.”",
    "Tifa\n“Mm... I'm getting the hang of this.”",
    "Cloud\n“Keep your eyes forward.”",
    "Tifa\n“Is it hot in here, or is it just\n the workout?”",
]
MISSES_A = [
    "Tifa\n“Whoa, wait! Slow down...”",
    "Tifa\n“Oops! I lost my balance.”",
    "Cloud\n“Reset. Feet planted. Again.”",
    "Tifa\n“Sorry! Let me catch my breath.”",
    "Cloud\n“Don't rush it. Form first.”",
    "Tifa\n“Hah... okay, from the top.”",
]

STYLE_A = [["Cloud\n“Back to a normal stance.\n Hands forward.”"],
           ["Cloud\n“Wide stance. Hands behind your\n head. Sumo squats.”", "Tifa\n“Ooh, I feel that in a\n whole new place.”"]]
HOLDS_A = ["Cloud\n“Pause at the bottom. Hold it there.”",
           "Cloud\n“Stay down. I've got you.”",
           "Cloud\n“Hold... don't come up yet.”"]
CUES_A = ["Tifa\n“Okay, up! Let me up!”",
          "Tifa\n“Cloud, that's enough! Up!”",
          "Tifa\n“My legs! Let go!”"]
GOOD_A = ["Tifa\n“Phew! That burned... in a good way.”",
          "Cloud\n“Good. That's how you build strength.”",
          "Tifa\n“I didn't know I could hold it\n that long!”"]
EARLY_A = ["Cloud\n“Not yet. You came up too soon.”",
           "Tifa\n“Sorry, I couldn't hold it!”"]
MAD_A = ["Tifa\n“Hey! I said UP! My legs are\n on fire!”",
         "Tifa\n“When I say let go, you let go.\n Last warning, coach.”"]
WALKOUT_A = ["Tifa\n“That's it. Find yourself another\n student.”",
             "Director\n“Tifa, wait! ...CUT! Great. Just\n great.”"]

# part two (undressed)
START_B = ["Tifa\n“Don't stop now... I've got the hang\n of it.”"]
LINES_B = {
    1: ["Cloud\n“Keep that back straight.”", "Tifa\n“Mmm... yes, coach.”"],
    3: ["Tifa\n“Deeper... I want to feel the\n stretch.”"],
    4: ["Cloud\n“Good form. Hold it at the bottom.”", "Tifa\n“Ah...! I'm holding...!”"],
    6: ["Tifa\n“This is the best workout I've\n ever had!”"],
    7: ["Tifa\n“Cloud... Cloud...!”"],
}
CHAT_B = [
    "Tifa\n“Mmm... don't stop.”",
    "Cloud\n“Hands on your knees. Good.”",
    "Tifa\n“Ah... is this still a squat?”",
    "Cloud\n“Advanced technique.”",
    "Tifa\n“Ohh... I'll be sore tomorrow...”",
    "Tifa\n“Harder, coach!”",
    "Cloud\n“Push back into it.”",
    "Tifa\n“Hah... hah... yes...!”",
    "Tifa\n“Every gym should have one of\n these 'devices'...”",
    "Cloud\n“Stay low. Breathe.”",
]
MISSES_B = [
    "Tifa\n“Ah... you lost the rhythm.\n Start slow again.”",
    "Tifa\n“Mmh, wait... slower, slower...”",
    "Cloud\n“Easy. Find the rhythm again.”",
    "Tifa\n“Hah... don't you dare stop now.”",
    "Tifa\n“Oh! That one threw me off.”",
    "Cloud\n“Back to basics. Nice and slow.”",
]
STYLE_B = [["Cloud\n“Back to it. Hands on your knees.”"],
           ["Tifa\n“Cloud... what are you doing with\n your leg?”", "Cloud\n“Better angle.”"],
           ["Cloud\n“Now fold all the way over. Touch\n your toes.”", "Tifa\n“Like this...? Oh. OH.”"]]
HOLDS_B = ["Cloud\n“Stay down. Right there.”",
           "Tifa\n“Ah... hold me there...”",
           "Cloud\n“Don't move.”"]
CUES_B = ["Tifa\n“Ah...! Let go, let go!”",
          "Tifa\n“Too much! Let me up!”",
          "Tifa\n“Cloud, enough...! Up!”"]
GOOD_B = ["Tifa\n“Hah... that was... intense.”",
          "Tifa\n“Mmm... you listen. I like that.”",
          "Cloud\n“Breathe. Again.”"]
EARLY_B = ["Cloud\n“Already? Stay down longer.”",
           "Tifa\n“Sorry... I slipped.”"]
MAD_B = ["Tifa\n“Cloud! I said let go! That's not\n funny.”",
         "Tifa\n“When I say stop, you STOP.\n ...Last warning.”"]
WALKOUT_B = ["Tifa\n“No. We're done. You don't listen.”",
             "Director\n“...And she's gone. CUT. We'll fix it\n in the edit.”"]
FINALE = ["Tifa\n“Phew... same time tomorrow, coach?”",
          "Director\n“CUT! That's a wrap! You two are\n naturals.”"]
PAID = "Director\n“Here's your pay: {VAR} gil.\n Great work today.”"

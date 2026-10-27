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
# (user: "needs a lot more variety ... 1 thing happens that slowly builds") a circuit of stations round the gym,
# each with its own poses, spot and twist on the prompts, her clothes coming off in stages (spandex -> top off ->
# nothing): squats (holds), the weight bench (partner press: SPOT prompts), a stretch on the floor (every hold
# deeper), the ring (the bent-over squats, the finisher). `part` = the pose set: A / B (`_workout_poses`), P / S
# (`_circuit_poses`); `who` = the actors (cloud, tifa) entities; reps = prompts at the station.
STATIONS = [
    dict(key="squats", part="A", who=("cloudA", "tifaA"), reps=10, hold=(2, 44), spot=None, dare=4),
    dict(key="press", part="P", who=("cloudA", "tifaC"), reps=9, hold=None, spot=(1, 64), dare=4),
    dict(key="stretch", part="S", who=("cloudB", "tifaB"), reps=9, hold=(0, 96), spot=None, dare=None),
    dict(key="ring", part="B", who=("cloudB", "tifaB"), reps=12, hold=(2, 44), spot=None, dare=5),
]
PART_A_REPS, PART_B_REPS = STATIONS[0]["reps"], STATIONS[3]["reps"]
# the stations' spots in the gym (mkt_mens): squats SQUAT_AT; the weight bench at the back (its walkmesh bump
# runs PRESS_FAR -> PRESS_NEAR; Cloud stands beyond the far end facing along it); the stretch on the open floor
# STRETCH_AT (facing screen-left); the ring's canvas (walkmesh z 76) RING_AT, facing screen-left
PRESS_FAR, PRESS_NEAR = (-140, 515), (-62, 465)
STRETCH_AT = (0, 90)
RING_AT, RING_Z = (230, 210), 76
# the camera's focus (the hidden player) per station
FOCI = [(10, 160), (-100, 470), (0, 110), (200, 200)]
# SPOT (the bench): she stalls at the bottom; mash [OK] SPOT_NEED times within SPOT_FRAMES = a hit + SPOT_BONUS
SPOT_NEED, SPOT_FRAMES, SPOT_BONUS = 6, 75, 3
SPOT_LABEL = "SPOT HER! Mash {PURPLE}[OK]{WHITE}"
# (user) Tifa's dares: at rep `dare` of a station she sets one: 0 a sprint (DARE_SPRINT reps at the top pace),
# 1 a clean streak (DARE_CLEAN reps without a miss). Won = DARE_BONUS x (tier + 1) and her line; lost = teasing
DARE_SPRINT, DARE_CLEAN, DARE_BONUS = 4, 5, 6
# (user) between stations a choice of replies; each is (text, mood +, the next station's starting tier, her line)
# and the mood pays MOOD_PAY x PAY_HIT gil a point at the end
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
INTRO_GESTURES = {0: [("tifa", "hiprock")], 1: [("cloud", "nod")], 2: [("tifa", "lean")], 3: [("cloud", "stretch")],
                  4: [("tifa", "hips")], 5: [("cloud", "warmup")]}

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
           ["Cloud\n“Wide stance. Hands behind your\n head. Sumo squats.”", "Tifa\n“Ooh, I feel that in a\n whole new place.”"],
           ["Cloud\n“Arms straight up. Reach for the\n ceiling and sit down.”", "Tifa\n“Overhead squats? Show-off.\n ...Okay, these are hard.”"]]
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
           ["Cloud\n“Now fold all the way over. Touch\n your toes.”", "Tifa\n“Like this...? Oh. OH.”"],
           ["Cloud\n“Split stance. One foot forward,\n hands on your knee.”", "Tifa\n“Lunges? Now? You're a\n sadist, coach. ...Don't stop.”"]]
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

# ---- the circuit (user: variety) ---------------------------------------------------------------------------
HOW = ("A circuit round the gym. Press the button\nshown in time; hits build the pace, a miss\nslows it right down."
       "{NEW}HOLD: press it and keep it held while\nshe stays down. Let go the moment she\ncalls it, or she'll get mad."
       "{NEW}SPOT: on the bench, mash {PURPLE}[OK]{WHITE} to help\nher lift. She'll dare you now and then:\nkeep up and it pays.")
MOOD_PAY = 3
# (station index -> after it) the move to the next station: lines before the fade, the choice, lines after it
NEXT = {
    0: dict(before=["Tifa\n“Phew! My legs are jelly. What's\n next, coach?”",
                    "Cloud\n“Bench. Upper body.”"],
            ask=("Tifa\n“...It's so hot in here. Would you mind\n if I took my top off?”",
                 [("“Go for it. Whatever's comfortable.”", 2, 1,
                   "Tifa\n“Thanks, coach. You're sweet.”"),
                  ("“I was hoping you'd ask.”", 1, 2,
                   "Tifa\n“Ha! I noticed. Eyes on my form,\n mister.”"),
                  ("“Keep it on. Focus.”", 0, 0,
                   "Tifa\n“...Fine. Taking it off anyway.”")]),
            after=["(She peels the leotard down to her waist and\n lies back on the bench.)",
                   "Cloud\n“Hands up. Push against mine.”"]),
    1: dict(before=["Tifa\n“My arms are done. Totally done.”",
                    "Cloud\n“Stretch it out. On the floor.”"],
            ask=("Tifa\n“These tights are way too tight to\n stretch in...”",
                 [("“Take them off. I'll help.”", 2, 1,
                   "Tifa\n“Mm. Helpful AND good with his hands.”"),
                  ("“I'll lose mine too. Fair's fair.”", 1, 2,
                   "Tifa\n“...Now THAT'S a training device.”"),
                  ("“They're fine. Lie down.”", 0, 0,
                   "Tifa\n“They're coming off, Cloud.”")]),
            after=["(Off it all comes. She lies back on the\n floor; he kneels at her feet.)",
                   "Cloud\n“Leg up on my shoulder. Breathe out.”"]),
    2: dict(before=["Tifa\n“Ohh... I've never been this... flexible.”",
                    "Director\n“Love it! Final set in the ring, people!\n Give me a finish!”"],
            ask=("Tifa\n“The ring? In front of everyone?”",
                 [("“You've earned it. Show them.”", 2, 1,
                   "Tifa\n“...Okay. Let's give them a show.”"),
                  ("“Last one in does fifty push-ups.”", 1, 2,
                   "Tifa\n“You're on!”"),
                  ("“Ring. Now. Squats.”", 0, 0,
                   "Tifa\n“Yes, DRILL SERGEANT.”")]),
            after=["(Up through the ropes. The crowd that\n isn't there goes wild.)",
                   "Cloud\n“Same as before. Hands on your knees.”"]),
}
START_B = []                    # (the ring opens with NEXT[2]'s lines)

# the bench (top off)
LINES_P = {
    1: ["Cloud\n“Push. Elbows out. Good.”", "Tifa\n“You're... very close, coach.”"],
    3: ["Tifa\n“Ah... I can feel you leaning in.”", "Cloud\n“Counterweight.”"],
    5: ["Tifa\n“Mm... harder. Push back harder.”"],
}
STYLE_P = [["Cloud\n“Feet down. Press.”"],
           ["Cloud\n“Legs up. Core.”", "Tifa\n“Upside down you look... bigger.”"]]
CHAT_P = [
    "Cloud\n“Breathe out on the push.”",
    "Tifa\n“Your hands are so warm.”",
    "Cloud\n“Lock it out at the top.”",
    "Tifa\n“Don't drop on me, coach.”",
    "Tifa\n“I can see right up your... shorts.”",
    "Cloud\n“Eyes on the ceiling.”",
]
MISSES_P = [
    "Tifa\n“Whoa- my arms gave out!”",
    "Cloud\n“Reset. Slow.”",
    "Tifa\n“Sorry! Sweaty hands!”",
    "Tifa\n“Hah... let me get a grip.”",
]
SPOTS = ["Tifa\n“Ngh...! I'm stuck! Help!”",
         "Tifa\n“Cloud... I can't... push...!”",
         "Tifa\n“It's not moving! Spot me!”"]
SPOT_GOOD = ["Tifa\n“Hah! Up! We did it!”",
             "Cloud\n“Got you. Every time.”",
             "Tifa\n“Mm... my hero.”"]
SPOT_FAIL = ["Tifa\n“Ow! Cloud! You were supposed\n to HELP!”",
             "Tifa\n“...And now I'm pinned. Great spotting.”"]

# the stretch (both undressed)
LINES_S = {
    1: ["Cloud\n“Lean into it. Slowly.”", "Tifa\n“Ooh... that's a good stretch.”"],
    3: ["Tifa\n“Cloud... I don't think this is\n a stretch anymore.”", "Cloud\n“Advanced stretch.”"],
    5: ["Tifa\n“Deeper...! Don't you dare stop!”"],
}
STYLE_S = [["Cloud\n“Relax the hip. Let it open.”"]]
CHAT_S = [
    "Tifa\n“Mmh... I can feel it everywhere.”",
    "Cloud\n“Don't hold your breath.”",
    "Tifa\n“Who taught you to stretch\n like this?”",
    "Cloud\n“...Self-taught.”",
    "Tifa\n“My leg's going to stay up there\n forever.”",
    "Tifa\n“Ah... ah... flexible... so flexible.”",
]
MISSES_S = [
    "Tifa\n“Ow, ow- too fast!”",
    "Cloud\n“Easy. Back off a little.”",
    "Tifa\n“Mmh, cramp! Wait!”",
    "Tifa\n“Slower... start slower.”",
]
HOLDS_S = ["Cloud\n“Deeper. Hold it there.”",
           "Tifa\n“Ah...! Stay... stay right there...”",
           "Cloud\n“Breathe. Don't move.”"]
CUES_S = ["Tifa\n“Okay- okay, let go!”",
          "Tifa\n“That's my limit! Let go!”",
          "Tifa\n“Cloud! Leg! Let go!”"]
GOOD_S = ["Tifa\n“Ohh... I've never been so open.”",
          "Cloud\n“Good. Again.”",
          "Tifa\n“You listen... I like that.”"]
EARLY_S = ["Cloud\n“Not yet. Hold the stretch.”",
           "Tifa\n“Sorry- slipped.”"]
MAD_S = ["Tifa\n“My HAMSTRING, Cloud! Let go when\n I say!”",
         "Tifa\n“When I say stop, you STOP.\n ...Last warning.”"]

# the dares (station -> lines are shared): her setting it, by kind; won; lost
DARES = [["Tifa\n“Bet you can't keep up if I go\n full speed. Four in a row!”",
          "Tifa\n“Sprint set! Go go go!”"],
         ["Tifa\n“Five clean ones. No mistakes.\n Loser buys dinner.”",
          "Tifa\n“Perfect form, five times. Dare you.”"]]
DARE_WON = ["Tifa\n“Okay, okay! You win. Show-off.”",
            "Tifa\n“...Not bad. Dinner's on me.”",
            "Director\n“YES! Bonus! Keep that energy!”"]
DARE_LOST = ["Tifa\n“Ha! Too slow, coach!”",
             "Tifa\n“Dinner's on you. Somewhere nice.”",
             "Tifa\n“And THAT'S why I'm the athlete.”"]

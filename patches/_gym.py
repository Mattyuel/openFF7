"""(user) The gym's training activities (693_gym; plan docs/gym_plan.md sections 5-6): Tifa in the Wall Market gym
offers a training session; in a copy of the gym Cloud coaches one of the first members at a time (the plan's
recruits: Wedge, Biggs, Jessie):

- Squats with Wedge (he wants to lose weight and gain confidence): a button prompt each rep (the films' prompt
  game): hits speed him up, three misses in a row and he quits.
- Plank with Biggs (discipline): hold his form. His hips drift (sagging or piking) on the meter; [OK] lifts them,
  [CANCEL] lowers them; either end of the meter = he collapses. Score = seconds in the middle band.
- Run with Jessie (stunt stamina): step on the beat. A "Step!" prompt every beat; in time = her pace goes up
  (walk -> jog -> run -> sprint, the beat quicker), a miss drops it.

Each session pays the member's fee by the score. Data only."""

FIELD = "blackbgj"              # a debug room only startmap leads to, replaced by a copy of the gym
BASE = "mkt_mens"
ARRIVE = (10, 160)              # (683's FOCUS: the camera's spot)
MUSIC = 16                      # AKAO 10 index: PARADE (unverified choice: upbeat)
TRAIN_AT = (-35, 185)           # the member's spot (683's squat spot), side-on to the camera
COACH_AT = (25, 168)            # Cloud beside him, facing him
WAIT_AT = [(-80, 250), (-20, 262), (40, 250)]   # the others watching (Wedge, Biggs, Jessie)
TIFA_AT = (-40, 120)            # Tifa in the real gym (mkt_mens), by the floor
KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (the squat contest's squat)

# squats
SQUAT_PERIODS = (60, 48, 40, 32)    # frames a rep by tier
SQUAT_REPS, SQUAT_HITS_UP, SQUAT_QUIT = 15, 2, 3
SQUAT_DROP, SQUAT_LEAN, SQUAT_ARMS = 0.42, 28, 0.9     # (legs' length share; degrees; arms raised forward)
SQUAT_FEE = 8                   # gil per hit x (tier + 1)
# plank
PLANK_FRAMES = 900              # 30 s
PLANK_DRIFT = (24, 16)          # frames between drifts (start, from half way)
PLANK_FLIP = 72                 # in 256: the drift changes direction
PLANK_FEE = 25                  # gil per second in the middle band (4-6)
PLANK_SAG, PLANK_PIKE = (1.2, -14), (1.6, 26)    # (root drop / rise, waist bow); the pitch is solved (693 `_plank`)
# run
RUN_BEATS = 32
RUN_BEAT = (46, 38, 31, 25)     # frames a beat by pace
RUN_WINDOW = 14                 # frames the "Step!" prompt is up (a press then = in time)
RUN_HITS_UP = 3
RUN_FEE = 6                     # gil per hit x (pace + 1)

MENU = ("Tifa\n“Who's training today, coach?”",
        ["Squats with Wedge.", "Plank with Biggs.", "Run with Jessie.", "That's it for today."])
INTRO = ["Tifa\n“Our first members! Be nice to them,\n Cloud. They're paying customers.”",
         "Cloud\n“...They're paying?”",
         "Tifa\n“Some of them. Eventually. Go!”"]
BYE = "Tifa\n“Good work, coach. Same time tomorrow.”"
FEE = "Tifa\n“Session fee: {VAR} gil.”"
TIFA_TALK = dict(greet="Tifa\n“The members are warming up. Want to\n run a session?”",
                 ask=("Tifa\n“Coach?”", ["Run a session.", "Not now."]),
                 no="Tifa\n“They'll be here.”")

SESSIONS = {
    "squats": dict(
        intro=["Wedge\n“Coach! I'm ready! I think. I had a big\n breakfast. Is that bad?”",
               "Cloud\n“Feet apart. Chest up. Down, then up.\n Don't think about breakfast.”"],
        how="Press the button shown on each squat.\nHits speed Wedge up; three misses in\na row and he gives up.",
        miss=["Wedge\n“Oof!”", "Wedge\n“My knees made a noise!”", "Wedge\n“I'm okay! I'm okay.”"],
        quit="Wedge\n“I... can't... feel... my legs. Can I\n have a snack now?”",
        good="Wedge\n“Fifteen squats! Coach, I've never done\n fifteen of anything!”",
        ok="Wedge\n“That was hard. I'm coming back,\n though! Tomorrow! ...Maybe Thursday.”"),
    "plank": dict(
        intro=["Biggs\n“Plank? Easy. I held a fence post in\n the rain for six hours once.”",
               "Cloud\n“Straight line. Head to heels. Don't\n let your hips drop.”"],
        how="Keep Biggs's hips straight: when they\nsag (left) press {PURPLE}[OK]{WHITE}, when they pike\n(right) press {PURPLE}[CANCEL]{WHITE}. 30 seconds.",
        fail="Biggs\n“...Okay. Okay. The fence post was\n easier. The fence post didn't judge me.”",
        good="Biggs\n“Thirty seconds, rock solid! Discipline,\n coach. That's what I came for.”",
        ok="Biggs\n“Shaky, but I held it. Same again\n tomorrow, coach.”"),
    "run": dict(
        intro=["Jessie\n“Stunt work's all stamina. If I'm going\n to fall off things for a living, I need\n to run away from things first.”",
               "Cloud\n“Step on the beat. Faster when you can.”"],
        how="Press {PURPLE}[OK]{WHITE} each time \"Step!\" shows.\nIn time and she speeds up: walk, jog,\nrun, sprint. A miss slows her down.",
        miss=["Jessie\n“Whoa- tripped!”", "Jessie\n“Off the beat! Sorry!”"],
        good="Jessie\n“Full sprint and I'm not even dead! Put\n that in my stunt reel!”",
        ok="Jessie\n“Phew! I'll get there. Again tomorrow?”"),
}
STEP = "Step! {PURPLE}[OK]{WHITE}"

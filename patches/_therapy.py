"""(user) Therapy Session: a Director's film (691_therapy). "Tifa and Cloud take turns revealing their deepest,
darkest thoughts and have a follow-up minigame scene each where they get the opportunity to do what their heart
desires." (user's choices) a therapist's office (Junon's doctor's office junbin3: the couch in the middle), their
secret fantasies, no therapist: just the two of them and a camera the Director left running. Cloud goes first
(he wants to hold her down: the movie's prone, F), then Tifa (she wants to be on top, in charge, at her pace, and
to stop performing: cowgirl, B, then the finisher). Written against `_backstories` / `_movie_profiles` without
touching Tifa's childhood (the project's rule): only what she wants now. Data only."""

FIELD = "blackbgd"              # a debug room only startmap leads to, replaced by a copy of the office
BASE = "junbin3"
COUCH = (-92, -1198)            # the couch's middle (a walkable piece at z 210: x -399..215, y -1430..-966)
SEAT_Y = -1405                  # sitting on its front edge (towards the camera)
SEAT_X = {"C": 0, "G": -190}  # Cloud right of Tifa on screen
ARRIVE = (-90, -1600)           # the floor in front of the couch
MUSIC = 34                      # AKAO 10 index: TIFA (Tifa's Theme; 660's revelation)
PAY_HIT = 14
HITS_UP = 2
PERIODS = (60, 45, 33, 24)
FINISH_FRAMES = 150
KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (683's squat sound)

INTRO = [
    "(The camera's red light blinks on. The\n Director set it running and left them\n alone with it.)",
    "Tifa\n“...So this is the 'therapy session'.\n A couch, a camera, and us.”",
    "Cloud\n“He said the rules are simple. We take\n turns. We say the thing we've never\n said. Nobody laughs.”",
    "Tifa\n“The darkest thing. The thing you\n think about and then pretend you\n didn't.”",
    "Cloud\n“...I'll go first. Before I lose my\n nerve.”",
]
HOW = ("Press the button shown in time. Hits\nspeed things up and pull the meter in;\n"
       "misses push it out. The red ends it.")
PAID = "(The Director comes back in.)\nDirector\n“...That was beautiful. {VAR} gil. I need\n a minute.”"
OUTRO = [
    "Tifa\n“...Hey. Thank you. For telling me.\n And for listening.”",
    "Cloud\n“Same time next week?”",
    "Tifa\n“Same couch. Same rules. Nobody\n laughs.”",
]

# each turn: the reveal (sitting on the couch), then the scene: setup lines (still), reps, beats
TURNS = [
    dict(who="cloud", pos="prone", reveal=[
        "Cloud\n“...I think about holding you down.\n Your wrists, here. Your face in the\n sheets. Telling you not to move.”",
        "Cloud\n“And you don't move. Not because you\n can't. Because you don't want to. Because\n you want me to have you.”",
        "Cloud\n“It scares me how much I want that.\n I keep thinking it makes me someone\n I don't want to be.”",
        "Tifa\n“...Cloud. Look at me.”",
        "Tifa\n“Wanting something isn't the same as\n taking it. You asked. That's the\n whole difference.”",
        "Tifa\n“So: yes. But we pick a word. If I say\n 'chocobo', you stop. Everything stops.\n No questions.”",
        "Cloud\n“...Chocobo. Okay.”",
        "Tifa\n“Then stop asking me if I'm sure. I'm\n sure. Take me.”"],
         setup=[
        "Cloud\n“Hands above your head. Don't move\n them.”",
        "Tifa\n“...Yes.”",
        "Tifa\n“(Her breath catches as his weight\n settles over her hips, his hand\n closing around both her wrists.)”"],
         reps=12, beats=[
        (2, "talk", ["Cloud\n“Stay still. ...Good. Just like that.”",
                     "Tifa\n“Nnh... you're so heavy on me. I can't\n go anywhere. I love that I can't go\n anywhere.”"]),
        (4, "pause", ["Cloud\n“...Still green?”",
                      "Tifa\n“Green. Very green. If you ask me again\n I'm saying chocobo just to annoy you.”",
                      "Cloud\n“Heh. Okay.”"]),
        (6, "talk", ["Cloud\n“You're mine like this. Say it.”",
                     "Tifa\n“Ah... I'm yours. Hold me down. Harder.\n Don't let go.”"]),
        (8, "talk", ["Tifa\n“Ahh! The way you're holding me... I\n don't have to think. I don't have to\n be anything. Just yours.”"]),
        (10, "pause", ["Cloud\n“(He slows, his grip easing for a\n moment.)”",
                       "Cloud\n“...This is what I wanted. I thought I'd\n feel like a monster. I don't.”",
                       "Tifa\n“Because you're not one. Now stop\n talking and finish what you started.”"]),
    ], after=[
        "Tifa\n“...Hah... hah... okay. Okay. That was...\n a lot. In the best way.”",
        "Cloud\n“Are you alright?”",
        "Tifa\n“Better than alright. ...Your turn's\n over, though. Sit down. It's mine.”"]),
    dict(who="tifa", pos="cowgirl", reveal=[
        "Tifa\n“...Mine's going to sound small after\n yours.”",
        "Tifa\n“I take care of everyone. The bar, the\n kids, you, everyone. I'm always the\n one making sure it's good for you.”",
        "Tifa\n“My dark thought is that I want to be\n selfish. Once. On top, at my pace. And\n you don't get to move until I say.”",
        "Tifa\n“And... I want it to be real. No\n performing. No making the right noises\n so you feel good. Just... me.”",
        "Tifa\n“Eyes open. I want to see you the\n whole time. I want to know it's you.”",
        "Cloud\n“...Then it's yours. All of it. I'm not\n going anywhere.”",
        "Tifa\n“Lie back, Strife. Hands behind your\n head. You heard me.”"],
         setup=[
        "Tifa\n“(She settles over him, slowly, and\n doesn't look away.)”",
        "Tifa\n“Don't move. I mean it. ...Let me.”"],
         reps=12, beats=[
        (2, "talk", ["Tifa\n“Mmh... slow. I've never let myself go\n slow. There's no rush. You're not going\n anywhere.”",
                     "Cloud\n“I'm not allowed to.”",
                     "Tifa\n“Good boy.”"]),
        (4, "pause", ["Tifa\n“(She stops, rocking just barely, her\n hands flat on his chest.)”",
                      "Tifa\n“...This is the part where I'd usually\n start putting on a show. I'm not going\n to. Is that okay?”",
                      "Cloud\n“That's all I've ever wanted from you.”"]),
        (6, "talk", ["Tifa\n“Ah... ah... that's... oh. That's not\n a sound I made for you. That one was\n mine.”"]),
        (8, "talk", ["Cloud\n“Tifa...”",
                     "Tifa\n“Don't move. Watch me. ...Ahh... I can\n feel it coming and I'm not going to\n hide it. Not from you.”"]),
        (10, "talk", ["Tifa\n“Cloud... Cloud, keep your eyes open...\n look at me... this one's real...\n this one's real...”"]),
    ], after=[]),
]
FINISH_CALL = "Tifa\n“Now... now! Mash {PURPLE}[OK]{WHITE}! Don't you dare\n hold back!”"
FINISH_WIN = ["Tifa\n“AHH... ah... ah...!”",
              "Tifa\n“(She shakes, and laughs, and then she's\n crying a little, and she doesn't hide\n that either.)”",
              "Tifa\n“...That was the first real one. With\n anyone. I wanted it to be you.”"]

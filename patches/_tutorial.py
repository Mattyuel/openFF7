"""(user) The Basics: the first film in the Director's menu (688_tutorial), before Sector 7 Workout. In the
Sector 7 inn where every shoot happens (a copy of mds7_w3, 670's set), the Director walks Cloud and Tifa through
three positions as a tutorial for video shoots: more funny than informative. Head (he coaches Tifa; she's
muffled while they move and talks only when they pause; the hold explained, neither used to it), all fours
(how it feels, questions; the Director has Cloud taste her, which she isn't used to; he suggests putting it
'there', which interests Cloud and which Tifa shuts down), then sixty-nine (muffled most of the time,
coughing, laughing, getting used to it). The prompt game and the danger meter run throughout; the finisher
(10 s of [OK]) is explained while doing it. Data only."""

FIELD = "blackbg9"              # the set: a debug room only startmap leads to, replaced by a copy of the inn
BASE = "mds7_w3"                # 670's set: the inn with the three beds
ARRIVE = (60, -224)             # (670's MAPJUMP: the floor between the head position's spots)
MUSIC = 35                      # AKAO 10 index: COSTA (the movie's)
PAY_HIT = 10                    # gil per hit x (tier + 1)
HITS_UP = 2                     # hits in a row to step up a tier
PERIODS = (60, 45, 33, 24)      # frames a rep: 3 strokes of the 20 / 15 / 11 / 8-frame speeds
FINISH_FRAMES = 300             # (user) 10 s for the tutorial's finisher
LINE_Y = 168
KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
HIT_SOUND = bytes.fromhex("f20000002808" "9d01" "000000000000")   # (683's squat sound)

INTRO = [
    "Director\n“Welcome, welcome! Before we shoot a\n real film, the basics. Think of today\n as... orientation.”",
    "Tifa\n“Orientation. For THIS.”",
    "Director\n“Every great career starts with\n paperwork. Ours just has fewer\n clothes.”",
    "Cloud\n“...Is there a test?”",
    "Director\n“Everything's a test, kid. Three\n positions today. Head, all fours,\n and the grand finale: sixty-nine.”",
    "Tifa\n“You're saying that like a menu.”",
    "Director\n“It IS a menu. Wardrobe! ...We don't\n have wardrobe. Clothes off, please.”",
]
HOW = ("Press the button shown in time. Hits\nspeed things up and pull the meter to the\n"
       "middle; misses push it out. Hit the red\nand the Director calls CUT.")
PAID = "Director\n“Orientation pay: {VAR} gil. Welcome\n to the business!”"
OUTRO = [
    "Director\n“And that's the basics. You're\n naturals. Mostly. Some of you.”",
    "Tifa\n“*cough* I have so many notes.”",
    "Cloud\n“...Same time tomorrow?”",
]

# the segments: setup lines (actors placed and paused), the reps, beats (after the rep): (rep, kind, lines)
# kinds: talk (lines while the strokes go on), pause (both hold still, lines, then on), hold (head: the
# demonstration: held deep, lines, her tap-out squirm, lines, then he pulls out and wiggles), taste (all fours:
# Cloud tastes her), there (all fours: the suggestion, both paused)
SEGMENTS = [
    dict(key="head", reps=12, setup=[
        "Director\n“Position one: head. Tifa, on your\n knees. Cloud, stand right there.\n Closer. CLOSER.”",
        "Tifa\n“I know where it goes, thank you.”",
        "Director\n“What I'm looking for: eye contact,\n enthusiasm, and a nice steady rhythm.\n Don't rush it.”",
        "Director\n“Lips over the teeth, sweetheart. And\n breathe through your nose. Trust me\n on the nose.”",
        "Tifa\n“Okay. Eye contact. Nose. Here goes.”"],
        beats=[
            (2, "talk", ["Tifa\n“Mmph... mm-mmf.”",
                         "Director\n“Beautiful! Look up at him. Up!\n Not at me. At HIM.”"]),
            (4, "pause", ["Tifa\n“Hah... okay. It's... warmer than I\n thought. And heavier. My jaw's\n already talking to me.”",
                          "Cloud\n“...Is that bad?”",
                          "Tifa\n“It's not bad. It's just... a lot of\n you, all at once. Go on.”"]),
            (6, "talk", ["Tifa\n“Mm! Mmhm. Mmmf.”",
                         "Director\n“She says 'more of that.' I speak\n fluent muffled.”"]),
            (8, "hold", ["Director\n“Now: the HOLD. Cloud, all the way in\n and stay there. Hands on her head.\n Gently. You hold until she taps.”",
                         "Tifa\n“Mmph?! Mmmf mm mmph!”",
                         "Director\n“That's the spirit! Breathe through\n the nose, remember? THE NOSE.”"],
                        ["Tifa\n“(tap tap tap tap!)”",
                         "Director\n“Tap means let go. Let go, Cloud!”"],
                        ["Tifa\n“*gasp* Hah... hah... okay. Okay! I\n felt that in my ears. Why did I\n feel that in my ears?”",
                         "Cloud\n“Sorry. I didn't know when to stop.”",
                         "Tifa\n“That's what the tapping is for.\n ...It wasn't awful. Just warn me\n first next time.”",
                         "Director\n“And THAT'S a hold! The audience\n loves a hold. Then you pull out and\n give them a little wiggle. Showbiz!”"]),
            (10, "pause", ["Tifa\n“Hah... I think I've got it now. It's\n all about the rhythm. And the nose.\n Mostly the nose.”",
                           "Cloud\n“You're really good at this.”",
                           "Tifa\n“Don't sound so surprised!”"]),
        ]),
    dict(key="dog", reps=12, setup=[
        "Director\n“Position two: all fours! Tifa, on the\n bed, hands and knees. Cloud, behind\n her. This one's a classic.”",
        "Tifa\n“Do I just... look at the wall?”",
        "Director\n“Look back at him now and then. Over\n the shoulder. The audience eats it\n up.”",
        "Cloud\n“Where do I put my hands?”",
        "Director\n“Hips! Hold her hips. Think of it as\n steering.”",
        "Tifa\n“I am NOT a motorbike.”"],
        beats=[
            (2, "talk", ["Tifa\n“Ahh... oh, that's... a lot deeper\n this way.”",
                         "Cloud\n“Too deep?”",
                         "Tifa\n“No! No. Just... ah... keep going.”"]),
            (4, "taste", ["Director\n“Hold on! Before we go on, Cloud: get\n down there and have a taste. Builds\n anticipation.”",
                          "Tifa\n“A what? Down where?! Oh. OH.”",
                          "Tifa\n“Ahh... Cloud... that's... wow. I've\n never... nobody's ever... mmm.”",
                          "Tifa\n“...So? How do I taste? And don't say\n 'fine', Strife.”",
                          "Cloud\n“...Like I want seconds.”",
                          "Tifa\n“(giggle) Good answer.”"]),
            (6, "talk", ["Director\n“Look back at him! Over the shoulder!\n ...Perfect. Hold that face.”",
                         "Tifa\n“This face is happening on its own,\n thank you.”"]),
            (8, "there", ["Director\n“Ooh, idea! Cloud, what if you put it\n... there.”",
                          "Cloud\n“...There?”",
                          "Director\n“There. You know. The scenic route.”",
                          "Cloud\n“...Huh. I mean... we could try?”",
                          "Tifa\n“Absolutely not. Not today, not on a\n Tuesday, not in orientation.”",
                          "Director\n“A firm no! Respect the no, people.\n That's lesson two. Carry on!”",
                          "Cloud\n“...Sorry.”",
                          "Tifa\n“Don't be sorry. Be in the right\n place.”"]),
            (10, "talk", ["Tifa\n“Ah... ah! Cloud... right there. THAT\n there. Not the other there.”",
                          "Cloud\n“Got it.”"]),
        ]),
    dict(key="69", reps=12, setup=[
        "Director\n“Grand finale: sixty-nine! Cloud, on\n your back. Tifa, over him, the other\n way round. Like a puzzle!”",
        "Tifa\n“The other way round... like this?\n ...Oh. Oh, hi.”",
        "Cloud\n“...Hi.”",
        "Director\n“The trick is teamwork. You both give,\n you both get. Nobody gets lazy.”"],
        beats=[
            (2, "talk", ["Tifa\n“Mmph! Mm-mmf mmph!”",
                         "Cloud\n“Mmf?”",
                         "Director\n“I have no idea what either of you\n said. Keep going!”"]),
            (4, "pause", ["Tifa\n“*cough* *cough* Sorry! Sorry. Went\n down the wrong way. Hah...”",
                          "Cloud\n“You okay?”",
                          "Tifa\n“Fine! It's just hard to concentrate\n when you're doing... THAT. With\n your tongue.”"]),
            (6, "talk", ["Tifa\n“Mmm... mmh-hmm...”",
                         "Director\n“She's getting used to it! Look at\n that rhythm!”"]),
            (8, "pause", ["Tifa\n“(laughing) Cloud, your hair is\n tickling my thighs! I can't... pfft!\n I can't stop laughing!”",
                          "Cloud\n“...My hair has never been a problem\n before.”",
                          "Tifa\n“It's a problem NOW. Okay. Okay.\n Serious face. Going back in.”"]),
            (10, "talk", ["Tifa\n“Mmf... mmmh! Mm-mm-mmh!”",
                          "Director\n“That's the sound of a professional!”"]),
        ]),
]
FINISH_TALK = [
    "Director\n“Last thing, and it's the important\n one: the FINISHER. See that meter?\n The red on the right?”",
    "Director\n“When I say go, mash {PURPLE}[OK]{WHITE} like your\n career depends on it. Push the needle\n into the red. It slips if you slack!”",
    "Tifa\n“Mmph?!”",
    "Director\n“Ten seconds, since it's your first\n time. Ready? GO!”",
]
FINISH_CALL = "Director\n“FINISHER! Mash {PURPLE}[OK]{WHITE}! Into the red!”"
FINISH_WIN = ["Tifa\n“Mmmmph!! ...*cough* ...Hah... hah...\n Did we... win?”",
              "Director\n“You won ORIENTATION. Bonus!”"]

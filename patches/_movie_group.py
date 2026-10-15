"""(user) The movie minigame's "group" shoot, unlocked by a wrap with Aerith (star rank 6): Ruby,
Skye, Elena, Scarlet, Tifa and Aerith on one set (670 `_group`). Data only.

Part one, "head" on top of the middle bed: three girls kneel in a line along one long side, three
along the other, facing across; Cloud stands between them and takes each girl in turn (random
order, no repeats), 15 s each. Part two, "head reverse": two girls lying across the near end of
each bed; again each girl in turn. Only Cloud and the engaged girl move; the engaged girl's lines
are muffled, the others comment. The finisher as in every shoot.

ORDER: model order on the set; HEAD_SPOTS / HEADREV_SPOTS index by it."""

ORDER = ["ruby", "skye", "elena", "scarlet", "tifa", "aerith"]
NAMES = {"ruby": "Ruby", "skye": "Skye", "elena": "Elena", "scarlet": "Scarlet", "tifa": "Tifa",
         "aerith": "Aerith"}

# part one: the middle bed's top (walkmesh piece z 100, x -45..81, y -181..29); the girls kneel
# HEAD_GAP from Cloud as in the one-girl "head" (38 ahead, 6 to his right): line one at x -40
# facing +x (the screen-left line), line two at x 56 facing -x, each Cloud HEAD_GAP from his girl
HEAD_X, HEAD_YS = (-40, 56), (-125, -85, -45)    # (user, since) up the bed, away from its end; (user, since)
                                                 # line one a pace back (was -20), near the bed's edge (-45)
HEAD_SEAT = {"ruby": 0, "skye": 3, "elena": 2, "scarlet": 1, "tifa": 4, "aerith": 5}   # part one: girl -> spot
                                             # (0-2 line one by HEAD_YS, 3-5 line two; user: Skye and Scarlet swapped)
HEAD_GAP, HEAD_RIGHT = 38, 1                 # (user, since) his pelvis on her face (was 6)

# part two: two girls per bed lying along it, heads over its near end (y -), XYZI by her feet as
# the one-girl "head reverse" (the left bed: girl y -54 with its end at -134, Cloud 96 nearer);
# (bed x lanes, the bed's near end y, the bed top's height)
BEDS = [((-255, -196), -134, 54), ((-14, 50), -181, 100), ((198, 256), -193, 125)]
HEADREV_ALONG, HEADREV_CLOUD = 80, 96

PHASES = 3                    # (user) part one "head", part two "head reverse", part three "end"
RATE = 70                     # gil a press (10 more than Aerith); the finisher pays x 100
TURN = 450                    # frames each girl (15 s)

# the others watching (user: they comment too; "fun, sexy, competitive, complimenting each
# other's abilities in explicit ways"), in character; part one ("head") / part two ("head reverse") /
# part three ("end")
COMMENTS = {
    "ruby": (["Take that cock, girl.", "All the way, babe.",
              "I'll make him beg.", "Lick it.",
              "Go deeper.", "So sloppy."],
             ["Right down the throat.", "Her throat is bulging.",
              "Don't stop, star!", "Love it.",
              "She's not even blinking.", "Me next!"],
             ["Fuck that throat.", 'Pin the bitch down.', "Lucky girl.", 'Choke on it, babe.', "My throat is ready.", 'Yes, yes, take it!']),
    "skye": (["Fuck it, fuck it!", "Stick that tongue out, girl.",
              "Little whore loves it.", "Bring that cock.",
              "Hahahaha oh god.", "Swallow it whole."],
             ["Balls deep.", "Such a pretty whore.",
              "You're such a cutie.", "Aaaaaah",
              "Aww a single tear.", "Okay, she's amazing.."],
             ["I want that.", 'Is that even possible?', 'Stand over ME next!', "Fuck her head!", "She's totally stuck! So hot!", 'Do me like that! Pleeease!']),
    "elena": (["How is she not gagging?", "Can I try that?",
               "She looks cute like that.", "What a pro.",
               "Hope my endurance training pays off.", "I'm not gonna hold back."],
              ["Where am I?", "That angle's ... efficient.",
               "No gag reflex at all!", "I wasn't trained for this.",
               "Okay. I'm impressed.", "Am I supposed to do that?"],
              ["Oh my.", "She can't even move.", "He's dominating her.", "I'm taking notes.", "I've never seen anything like this.", 'Is this making love?']),
    "scarlet": (["Kyahaha! Cute.", "She's a sloppy one.",
                 "Grab her hair, darling.", "Bad girl.",
                 "Stay still, let him work.", "Is that all you've got?"],
                ["Do I need to hold you still?", "Hang her lower, darling.",
                 "Fuck her face stupid.", "Awww, little cutie-pie.",
                 "Pound her throat, darling.", "That's my girl! Kyahaha!"],
                ['Sit on her face, darling!', 'Hold her head down.', 'Look at her squirm.', "That's how you treat a girl.", "Don't you dare be gentle on me.", "She's in love, how cute."]),
    "tifa": (["Work, girl.", "Don't you dare finish before me!",
              "That's... impressive.", "He can do that?",
              "You like it like this?", "Breathe through your nose."],
             ["That's...different", "Is she ok?",
              "This is next level.", "I didn't train for this.",
              "Her body's perfect.", "Give it to her."],
             ["Cloud, you're crushing her.", "You're fucking her...head.", 'Breath out around it.', 'Should I hold her head for you?', 'Squat lower!', "Okay, she's good."]),
    "aerith": (["Ooh, that's really something.", "She's shaking, how cute!",
                "She's glowing.", "Look at her eyes watering.",
                "Hey, no hogging!", "Save some for me."],
               ["Upside down and still smiling.", "Her toes are curling!",
                "Ooh, he's buried in her face.", "I'll take him to the Promised Land.",
                "I'll try my best.", "Everyone's so talented!"],
               ["I've never seen anything like this.", 'I wonder what that feels like.', "He's so gentle.", 'Ooh, me next?', "She's turning all red.", "Everyone's so naughty."]),
}
# the engaged girl (user: muffled)
MUFFLED = {"ruby": ["Mmph... mmm! Gk...glk...", "Mmf... mmh, mmh...", "Hnn... mmph!"],
           "skye": ["Mmmph! Mmm-hmm!", "Gk... mmh! Mmmh!", "Mmf mmf mmf!"],
           "elena": ["Mmph?! Mmm...", "Mmf... mm-hm...", "Hnnh... mmph!"],
           "scarlet": ["Mmm... mmmh!", "Hmmph... mmm-hm!", "Mmf... kyahmm!"],
           "tifa": ["Mmh... mmph!", "Mmm... mmf...", "Hnn... mmmh!"],
           "aerith": ["Mmm... I cl...gk... hehmm!", "Wha-gk... Mmph... mm-hm!", "Mmf... mmmh!"]}

INTRO = ["“The whole gang's here! Ladies, take your places.\n Star... you know what to do.”",
         "“One at a time, fifteen seconds each.\n Then we flip 'em over and do it again.”",
         "“Same rules: tap OK, mind the meter, red at\n either end and we're done. Ready?”"]
AFTERMATH = "(The six of them collapse on the beds in a\n giggling, breathless heap. Someone asks for water.)"
NEWS = ["“Star, you've been with every girl on my books.\n You know what that means? A group shoot!”",
        "“Ruby, Skye, Elena, Scarlet, Tifa and Aerith,\n all on one set. Pick 'Everyone' next time.”"]

# (user) "a small chance the girl needs to stop for a second, to catch her breath or a reflex":
# Cloud and she pull back and wait, then she tells him to go on, in character, keen. Head, head
# reverse and 69, in every shoot (670 `_pause_ops`); one of three a girl, in turn
PAUSES = {
    "ruby": ["(She pulls off)\n“Whew... okay. Where am I?”",
             "(She gags, pulls back)\n“My bad. Again. Harder this time.”",
             "(She catches her breath)\n“Mmm... where were we? Oh, right.”"],
    "skye": ["(It pops out)\n“Wow! Okay! Go again!”",
             "(She gulps for air)\n“That was SO deep. Do that again!”",
             "(She pulls back.)\n“*Ahem... More, please!”"],
    "elena": ["(She pulls back)\n“I-I'm fine! Turks don't quit.”",
              "(She takes a deep breath)\n“Okay... okay. I can take more.”",
              "(She gags)\n“That's... not in the manual.”"],
    "scarlet": ["(She pulls off)\n“Kyahaha! Did I say stop? Get back in here.”",
                "(She catches her breath)\n“A little breather. Ravage me, darling.”",
                "(She coughs)\n“...In!”"],
    "tifa": ["(She pulls back)\n“Phew... I just need a second. ...Okay, go.”",
             "(She gags)\n“Sorry! Again, Cloud. I want it.”",
             "(She catches her breath.)\n“You're not getting off that easy. More.”"],
    "aerith": ["(She pulls back, breathless.)\n“ ......More!”",
               "(She coughs softly)\n“Wew, don't hold back, okay?”",
               "(She catches her breath)\n“Wow... dizzy. Keep going!”"],
}
# (user) "another 50% to stop because cloud [pushes] the inward thrust and tells her to hold it in, after a
# 3 second pause she pulls away and gasps for air, clears throat, says continue": his line as he holds
# (HOLD_CLOUD, random), then hers as she pulls away (HOLDS, in turn); 670 `_stop_ops(kind="hold")`
HOLD_CLOUD = ["Hold it... right there. Don't move.",
              "Stay down. Hold it in... that's it.",
              "Easy... hold it. Breathe through it."]
HOLDS = {
    "ruby": ["(She pulls off)\n“*Ahem*...Okay... Go.”",
             "(She comes up for air)\n“*Cough*... you jerk. ...in!”",
             "(She gasps)\n“... Ok... Go on.”"],
    "skye": ["(It pops out)\n“Whoa! Okay... *Ahem*... Continue!”",
             "(She sucks in air)\n“I held it! Did you see? Keep going!”",
             "(She gasps)\n“Hah... ahem. Again! Go!”"],
    "elena": ["(She pulls off)\n“*Ahem!* ...Continue.”",
              "(She gasps for air,)\n“I... I'm still here...”",
              "(She clears her throat)\n“That was... i'm fine...”"],
    "scarlet": ["(She pulls off)\n“Kyahaha-ckkk... mmmh...”",
                "(She gasps)\n“Is that all you've go-ckkk...”",
                "(She clears her throat)\n“Hah... Fuck it more.”"],
    "tifa": ["(She pulls off)\n“Ahem! ...Whew. Oka-ckkk...”",
             "(She comes up for air)\n“Cloud! I thou-gk... mmmh.”",
             "(She gasps)\n“Wow... was that fun? Want more?”"],
    "aerith": ["(She pulls off)\n“*Ahem* Wow... okay... aaaaaahhhhhh!”",
               "(She comes up for air, coughing.)\n“You meanie... more please.”",
               "(She gasps)\n“I'm... okay... back in.”"],
}
HOLD_AT = dict(stern=90, muffled=150, struggle=180, end=210)   # (user, since) frames into the hold: his line at 0
                                   # (held deep); his stern reminder (HOLD_STERN) at 3 s; her muffled line
                                   # (HOLD_MUFFLED) at 5 s; her struggle to pull back at 6 s; at 7 s she pulls
                                   # away, then hers as PAUSE_FRAMES. Each line's window closes HOLD_SAY frames in.
                                   # (User, since) the hold is the player's: Square while the icon shows (670
                                   # `_pause_ops`), not a random 50%
HOLD_SAY = 50
HOLD_STERN = ["I said hold it.", "Do not pull away.", "Stay. Right. There."]
HOLD_MUFFLED = {   # (user) 5 s in: muffled, struggling
    "ruby": ["Mmmph! Mmff... mmh!!", "Nnnh... mmph! Mmmh!!", "Mmh-mmh! Mmmmff!"],
    "skye": ["Mmmp! Mmh-mmh-mmh!!", "Nnnmph! Mmmff!!", "Mmmh?! Mmmph!"],
    "elena": ["Mmph! Mmmh... mmff!!", "Nnngh! Mmh-mmh!", "Mmmff... mmph!!"],
    "scarlet": ["Mmmph! Mmh... MMPH!!", "Nnnh! Mmmff... mmh!", "Mmmh-MMH! Mmff!"],
    "tifa": ["Mmph! Mmmh... mmff!!", "Nnnh... mmh! Mmmph!", "Mmh! Mmh-mmh!!"],
    "aerith": ["Mmmh! Mmph... mmff!", "Nnnmh! Mmmph!!", "Mmh-mmh! Mmmff..."],
}
TRY_FRAMES, TRY_PULL = 30, 0.3     # (user) at 4 s her head pulls back slightly (30% of the way out) and can't
PAUSE_FRAMES = (0, 75, 15)         # before her line (user: shown the moment it happens); the line; after it
PAUSE_CHANCE = 128                 # (user, since) a 50% chance per position (or group turn) of one pause, armed
                                   # at its start for a random frame in its middle half (670 `_pause_arm`; was a
                                   # per-tick RANDOM < 2)

# ---- (user) character-driven moments, written against `_movie_profiles` (drafts: the user edits) ----
# Window text: "Name\n..." per speaker, "{NEW}" = the next page (the player presses OK); keep each
# line under ~40 characters. Gil amounts are added by 670 from the effects.

# (user) "some girls should also not be comfortable with what they're doing at all and there are
# more stops": an uneasy girl (profile `uneasy`) gets a stop early in every turn of hers (and
# another `UNEASY_AGAIN` frames after one she goes on from); Cloud picks "Check she's okay." /
# "Keep going." `ask` = her line (one at random); `checked` = her answer and whether she goes on
# ("go") or sits the rest of her turn out ("out"; Elena goes on only once the rules are agreed:
# "rules"); `pushed` = keep going: she stops anyway, annoyed (+1, `loss` x gil a press), turn over.
UNEASY_FIRST, UNEASY_AGAIN = 90, 210   # her first stop 3 s into her turn; the next 7 s after one she goes on from
UNEASY = {
    "elena": dict(
        ask=["(She stiffens and pulls back.)\n“Hold on. I need a second. This is a lot\n more than the briefing said.”",
             "(She pulls back, flushed.)\n“Can we... clarify what happens next?\n Procedurally?”",
             "(Her hands are shaking.)\n“I'm fine. I'm... I'm not fine. Wait.”"],
        checked="rules",
        go="(She takes a slow breath.)\n“...Thank you. We agreed the rules.\n I can do this. Continue.”",
        out="(She shakes her head.)\n“Honestly? No. I'd like to sit this one\n out.” (She moves aside.)",
        pushed="(She pulls away.)\n“I said WAIT.”", loss=10),
    "tifa": dict(
        ask=["(She pulls back, frowning.)\n“Hang on. Is this actually okay with\n everyone? I'm not sure it is.”",
             "(She sits back on her heels.)\n“Sorry. I just need a breather.”",
             "(She pauses.)\n“Cloud, this feels like a lot.\n Can we slow down?”"],
        checked="go",
        go="(She smiles a little.)\n“Thanks for asking. ...Okay. Slower.”",
        pushed="(She gets up.)\n“Wow. Okay.”", loss=5),
}
CHOICE_CHECK, CHOICE_PUSH = "Check she's okay.", "Keep going."

# (user) an introduction conversation, before the cameraman's rules: everyone standing by the bed;
# then Elena's question; "rules" agreed = RULES (Elena takes holds, and goes on when checked)
INTRO_TALK = ("Scarlet\n“Positions, ladies! I'll be directing.”{NEW}"
              "Ruby\n“Says who? I've got more takes than\n all of you put together.”{NEW}"
              "Skye\n“Ooh, is it a contest? I love contests!\n ...Wait, what are we competing at?”{NEW}"
              "Aerith\n“Elena, you've read that call sheet\n six times. Nervous?”{NEW}"
              "Elena\n“I am NOT... I'm reviewing it.\n Thoroughly.”{NEW}"
              "Tifa\n“Hey. Nobody does anything they don't\n want to. Right, Cloud?”")
INTRO_ASK = "Elena\n“Before we start... what are the rules?”"
# choices: (label, reply, effects); effects: gil = x gil a press (+ paid / - taken), annoy = [girls]
# (+1 each; LEAVE_AT and she leaves), rules = agreed, leave = [girls] (she leaves now, no penalty)
INTRO_CHOICES = [
    ("Let's agree some ground rules.",
     "Elena\n“...Thank you. That helps.”{NEW}Scarlet\n“Rules. How dull, darling.”", dict(rules=True)),
    ("No rules. Let's just have fun.",
     "Scarlet\n“Kyahaha! Now THAT'S a director.”{NEW}Elena\n“...Fine.”\n(She doesn't look fine.)", dict(annoy=["elena"])),
]

# (user) "moments where the sexual acts stop momentarily while a conflict or discussion occurs":
# one per part, at the start of its second turn (`at_turn`), if everyone in `girls` is still there;
# everyone holds still, `talk`, then `ask` (the last speaker's question to Cloud) with `choices`
SCENES = [
    dict(part=0, girls=["scarlet", "elena", "aerith", "tifa"],
         talk="Scarlet\n(The action stops. She's on her feet.)\n“Hold her head, darling. Make her take\n all of it.”{NEW}"
              "Elena\n“That was not discussed.”{NEW}"
              "Aerith\n“Ooh. Someone wants to be the director.”{NEW}"
              "Scarlet\n“Someone IS the director.”",
         ask="Tifa\n“Cloud? Your call.”",
         choices=[("I set the pace, Scarlet.",
                   "Scarlet\n(Her smile freezes.)\n“...Of course. Darling.”{NEW}Tifa\n“Nice.”",
                   dict(gil=10, annoy=["scarlet"])),
                  ("We'll do it Scarlet's way.",
                   "Scarlet\n“Kyahaha! Finally, a man who listens.”{NEW}Elena\n(She says nothing. Her jaw is tight.)",
                   dict(gil=-10, annoy=["elena"])),
                  ("Let's ask everyone first.",
                   "Tifa\n“Thank you.”{NEW}Elena\n“...Yes. Ground rules. Good.”", dict(rules=True))]),
    dict(part=1, girls=["ruby", "skye", "aerith", "tifa"],
         talk="Ruby\n(Everyone stops. She sits up.)\n“I lasted longest upside down.\n Admit it.”{NEW}"
              "Skye\n“Did not! I... wait, did you? Who was\n timing?”{NEW}"
              "Aerith\n“Cloud was. Weren't you, Cloud?”",
         ask="Ruby\n“Well? Who's best?”",
         choices=[("Ruby, easily.",
                   "Ruby\n“Obviously.”{NEW}Skye\n“Rematch! ...Later. Maybe.”", dict(gil=10)),
                  ("Skye, by a mile.",
                   "Skye\n“WHAT! YES!”{NEW}Ruby\n(She goes very quiet.)", dict(gil=5, annoy=["ruby"])),
                  ("It's not a contest.",
                   "Tifa\n“Thank you.”{NEW}Ruby\n“...Fine. Maybe I'll actually enjoy it.”", dict(gil=5))]),
    dict(part=2, girls=["aerith", "elena", "scarlet", "tifa"],
         talk="Aerith\n(She raises a hand. Everyone stops.)\n“Elena, you've been holding your breath\n for a whole minute.”{NEW}"
              "Elena\n“That's... a breathing technique.”{NEW}"
              "Scarlet\n“Kyahaha! She's terrified, darling.”",
         ask="Tifa\n“Cloud?”",
         choices=[("Elena, sit this out if you like.",
                   "Elena\n“...Thank you.”\n(She steps off the set.){NEW}Scarlet\n“One down.”", dict(leave=["elena"])),
                  ("She's fine. Keep going.",
                   "Elena\n“...Right. Fine.”{NEW}Aerith\n(She gives Cloud a long look.)",
                   dict(gil=-10, annoy=["elena"])),
                  ("Tifa, talk to her.",
                   "Tifa\n(She sits by Elena and whispers.){NEW}Elena\n“...Okay. Okay. I'm in.”", dict(gil=5, rules=True))]),
]
SCENE_AT_TURN = 2                  # the part's second turn

# (user) a conversation at the end (wrap or finisher): the girls' banter if nobody walked off and a
# bonus (`STAYED_BONUS` x gil a press), else the cameraman's remark; `WALKOUT` = everyone left (a CUT)
END_TALK = ("Tifa\n“That was... actually fun.”{NEW}"
            "Ruby\n“I was best.”{NEW}"
            "Aerith\n“Ruby was best at telling us she was best.”{NEW}"
            "Scarlet\n“Same time next week, darlings. I'll direct.”{NEW}"
            "Elena\n“...I'd like that in writing.”{NEW}"
            "Skye\n“Group hug! ...Is that weird now? Group hug!”")
STAYED_BONUS = 20
END_STAYED = "Cameraman\n“Nobody walked off my set. That's a first!\n Bonus: {gil:,} gil.”"
END_LEFT = "Cameraman\n“Next time, read the room, star.\n Walkouts cost me money.”"
WALKOUT = "Cameraman\n“...They ALL walked?! CUT!\n We'll sell what we've got.”"

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
# (user, since) 5 a set (the group's texts: room for the conflict scenes); the voice cycles them
COMMENTS = {
    "ruby": (['Take that cock, girl.', 'All the way, babe.', "I'll make him beg.", 'Lick it.', 'Go deeper.'],
          ['Right down the throat.', 'Her throat is bulging.', "Don't stop, star!", 'Love it.', "She's not even blinking."],
          ['Fuck that throat.', 'Pin the bitch down.', 'Lucky girl.', 'Choke on it, babe.', 'My throat is ready.']),
    "skye": (['Fuck it, fuck it!', 'Stick that tongue out, girl.', 'Little whore loves it.', 'Bring that cock.', 'Hahahaha oh god.'],
          ['Balls deep.', 'Such a pretty whore.', "You're such a cutie.", 'Aaaaaah', 'Aww a single tear.'],
          ['I want that.', 'Is that even possible?', 'Stand over ME next!', 'Fuck her head!', "She's totally stuck! So hot!"]),
    "elena": (['How is she not gagging?', 'Can I try that?', 'She looks cute like that.', 'What a pro.', 'Hope my endurance training pays off.'],
          ['Where am I?', "That angle's ... efficient.", 'No gag reflex at all!', "I wasn't trained for this.", "Okay. I'm impressed."],
          ['Oh my.', "She can't even move.", "He's dominating her.", "I'm taking notes.", "I've never seen anything like this."]),
    "scarlet": (['Kyahaha! Cute.', "She's a sloppy one.", 'Grab her hair, darling.', 'Bad girl.', 'Stay still, let him work.'],
          ['Do I need to hold you still?', 'Hang her lower, darling.', 'Fuck her face stupid.', 'Awww, little cutie-pie.', 'Pound her throat, darling.'],
          ['Sit on her face, darling!', 'Hold her head down.', 'Look at her squirm.', "That's how you treat a girl.", "Don't you dare be gentle on me."]),
    "tifa": (['Work, girl.', "I won't let you down.", "That's... impressive.", 'He can do that?', 'You like it like this?'],
          ["That's...different", 'Is she ok?', 'This is next level.', "I didn't train for this.", "Her body's perfect."],
          ["Cloud, you're crushing her.", "You're fucking her...head.", 'Breathe out around it.', 'Is she OK?', 'Squat!']),
    "aerith": (["Ooh, that's really something.", "Isn't love-making beautiful?", "She's glowing.", 'Look at her eyes water.', 'Hey, no hogging!'],
          ['Upside down and still smiling.', 'Your toes are curling!', "Ooh, he's buried in her face.", "I'll take him to the Promised Land.", "I'll try my best."],
          ["I've never seen anything like this.", 'I wonder what that feels like.', "He's so gentle.", 'Ooh, me next?', "Such a gentleman."]),
}
# the engaged girl (user: muffled)
MUFFLED = {"ruby": ["Mmph... mmm! Gk...glk...", "Mmf... mmh, mmh...", "Hnn... mmph!"],
           "skye": ["Mmmph! Mmm-hmm!", "Gk... mmh! Mmmh!", "Mmf mmf mmf!"],
           "elena": ["Mmph?! Mmm...", "Mmf... mm-hm...", "Hnnh... mmph!"],
           "scarlet": ["Mmm... mmmh!", "Hmmph... mmm-hm!", "Mmf... kyahmm!"],
           "tifa": ["Mmh... mmph!", "Mmm... mmf...", "Hnn... mmmh!"],
           "aerith": ["Mmm... I cl...gk... hehmm!", "Wha-gk... Mmph... mm-hm!", "Mmf... mmmh!"]}

INTRO = ["“The whole gang's here! The customers want\n power and dominance. Give it to them.”",
         "“One at a time, fifteen seconds each.\n Then we flip 'em over and do it again.”",
         "“Same rules: tap OK, mind the meter, red at\n either end and we're done. Ready?”"]
AFTERMATH = "(They collapse on the beds in a breathless\n heap. Someone asks for water.)"
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
HOLD_AT = dict(stern=90, muffled=150, struggle=180, muffled2=190, desperate=230, end=270)
                                   # (user, since) frames into the hold: his line at 0 (held deep); his stern
                                   # reminder (HOLD_STERN) at 3 s; her muffled line (HOLD_MUFFLED) at 5 s; her
                                   # struggle (`SQUIRMS`, 3 s) from 6 s; (user, since: 2 s longer) another muffled
                                   # line (a different HOLD_MUFFLED one) at 6.3 s, a desperate one
                                   # (HOLD_DESPERATE) at 7.7 s; at 9 s she pulls away, then hers as PAUSE_FRAMES.
                                   # His lines' windows close HOLD_SAY frames in, hers MUFFLED_SAY.
                                   # (User, since) the hold is the player's: Square while the icon shows (670
                                   # `_pause_ops`), not a random 50%
HOLD_SAY, MUFFLED_SAY = 50, 40
HOLD_STERN = ["I said hold it.", "Do not pull away.", "Stay. Right. There."]
HOLD_MUFFLED = {   # (user) 5 s in: muffled, struggling
    "ruby": ["Mmmph! Mmff... mmh!!", "Nnnh... mmph! Mmmh!!", "Mmh-mmh! Mmmmff!"],
    "skye": ["Mmmp! Mmh-mmh-mmh!!", "Nnnmph! Mmmff!!", "Mmmh?! Mmmph!"],
    "elena": ["Mmph! Mmmh... mmff!!", "Nnngh! Mmh-mmh!", "Mmmff... mmph!!"],
    "scarlet": ["Mmmph! Mmh... MMPH!!", "Nnnh! Mmmff... mmh!", "Mmmh-MMH! Mmff!"],
    "tifa": ["Mmph! Mmmh... mmff!!", "Nnnh... mmh! Mmmph!", "Mmh! Mmh-mmh!!"],
    "aerith": ["Mmmh! Mmph... mmff!", "Nnnmh! Mmmph!!", "Mmh-mmh! Mmmff..."],
}
HOLD_DESPERATE = {   # (user) the hold's last line, 7.7 s in: more desperate (the group uses only the first: texts)
    "ruby": ["MMMPH!! MMH-MMH-MMH!!", "Nnnngh!! MMMFF!! Mmh!!", "MMH! MMH! MMMMPH!!"],
    "skye": ["MMMMH!! Mmh-MMH!! Mmmph!!", "Nnnh-NNH!! MMMFF!!", "MMPH?! MMMH!! MMH!!"],
    "elena": ["MMMPH!! Mmh-mmh-MMH!!", "Nnngh!! MMMFF!! (Tap tap tap!)", "MMH! MMMH!! Mmmph!!"],
    "scarlet": ["MMMMPH!! MMH!! MMMFF!!", "NNNGH!! Mmh-MMH!!", "MMPH! MMMPH!! MMH!!"],
    "tifa": ["MMMPH!! Mmh-MMH!!", "Nnnngh!! MMMFF!! Mmh!!", "MMH! MMH-MMH!! Mmmph!!"],
    "aerith": ["MMMMH!! Mmph-MMPH!!", "Nnnnmh!! MMMFF!! Mmh!!", "MMH?! MMMMPH!! Mmh!!"],
}
TRY_FRAMES, TRY_PULL = 30, 0.3     # (user) at 4 s her head pulls back slightly (30% of the way out) and can't
# (user, since) her struggle, one after another in her try anim (670 `_try_anim`), TRY_FRAMES each: the pull
# back; a squirm (her hips wriggling: legs swayed about her body's axis); a desperate one (a harder pull,
# a fast tremble, her arms pushing at him, legs thrashing)
SQUIRMS = [dict(pull=TRY_PULL, shake=6, sway=0, push=0, cycles=0),
           dict(pull=0.15, shake=10, sway=14, push=0, cycles=2),
           dict(pull=0.45, shake=3, sway=20, push=25, cycles=3)]
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
        ask=["“Hold on. This is ...a lot more\n than the briefing said.”",
             "“Can we... clarify ...what happens\n next? Procedurally?”",
             "“....I'm fine. I'm... I'm not fine. Wait.”"],
        checked="rules",
        go="“...Thank you. We agreed the rules.\n I can do this. Continue.”",
        out="“Honestly? No. I'd like to sit this one\n out.”",
        pushed="“I said WAIT.”", loss=10),
    "tifa": dict(
        ask=["“Hang on. Is this actually okay with\n everyone?”",
             "“Sorry. I just ...need a breather.”",
             "“Cloud, this ...feels like a lot.\n Can we slow down?”"],
        checked="go",
        go="“Thanks for asking. ...Okay. Slower.”",
        pushed="“Wow. Okay.”", loss=5),
}
CHOICE_CHECK, CHOICE_PUSH = "Check she's okay.", "Keep going."

# (user) an introduction conversation, before the cameraman's rules: everyone standing by the bed;
# then Elena's question; "rules" agreed = RULES (Elena takes holds, and goes on when checked)
INTRO_TALK = ("Scarlet\n“Positions, ladies! I'll be directing.”{NEW}"
              "Elena\n“Huh? That's not correct.”{NEW}"
              "Cloud\n“Ladies, let's keep this professional.\n Remember, this is for the camera.”{NEW}"
              "Aerith\n“Yeah ladies. Remember that as he's\n feeding it to ya.”{NEW}"
              "Tifa\n“Try to take it easy on us, will\n you? We're people, not toys.”{NEW}"
              "Cloud\n“No promises. It was your choicee\n to be here. But i'll try.”")
INTRO_ASK = "Elena\n“Before we start... what are the rules?”"
# choices: (label, reply, effects); effects: gil = x gil a press (+ paid / - taken), annoy = [girls]
# (+1 each; LEAVE_AT and she leaves), rules = agreed, leave = [girls] (she leaves now, no penalty)
INTRO_CHOICES = [
    ("We do what the customers want.",
     "Elena\n“...Thank you. That helps.”{NEW}Scarlet\n“Rules. How dull, darling.”", dict(rules=True)),
    ("No rules. Let's just have fun.",
     "Scarlet\n“Now THAT'S a director.”{NEW}Elena\n“...Fine.”", dict(annoy=["elena"])),
]

# (user) "moments where the sexual acts stop momentarily while a conflict or discussion occurs":
# one per part, at the start of its second turn (`at_turn`), if everyone in `girls` is still there;
# everyone holds still, `talk`, then `ask` (the last speaker's question to Cloud) with `choices`
SCENES = [
    dict(part=0, girls=["scarlet", "elena", "aerith", "tifa"],
         talk="Scarlet\n“Hold her head, darling. Make her take\n all of it.”{NEW}"
              "Elena\n“That was not discussed.”{NEW}"
              "Aerith\n“Elena has a point.”{NEW}"
              "Scarlet\n“I know what the masses want to see.”",
         ask="Tifa\n“Cloud? Your call.”",
         choices=[("I set the pace, Scarlet.",
                   "Scarlet\n“...Of course. Darling.”{NEW}Tifa\n“Nice.”",
                   dict(gil=10, annoy=["scarlet"])),
                  ("We'll do it Scarlet's way.",
                   "Scarlet\n“Finally, a man who listens.”{NEW}Elena\n“This is NOT ok.”",
                   dict(gil=-10, annoy=["elena"])),
                  ("Group decision.",
                   "Tifa\n“Thank you.”{NEW}Elena\n“...Yes. Ground rules. Good.”", dict(rules=True))]),
    dict(part=1, girls=["ruby", "skye", "aerith", "tifa"],
         talk="Ruby\n“I lasted longest upside down.\n Admit it.”{NEW}"
              "Skye\n“Did not! I... wait, did you? Who was\n timing?”{NEW}"
              "Aerith\n“Cloud was. Weren't you, Cloud?”",
         ask="Ruby\n“Well? Who's best?”",
         choices=[("Ruby, easily.",
                   "Ruby\n“Obviously.”{NEW}Skye\n“Rematch! ...Later. Maybe.”", dict(gil=10)),
                  ("Skye, by a mile.",
                   "Skye\n“WHAT! YES!”{NEW}Ruby\n(She goes very quiet)", dict(gil=5, annoy=["ruby"])),
                  ("It's not a contest.",
                   "Tifa\n“Thank you.”{NEW}Ruby\n“...Fine.”", dict(gil=5))]),
    dict(part=2, girls=["aerith", "elena", "scarlet", "tifa"],
         talk="Aerith\n“Elena, you've been holding your breath\n for a whole minute.”{NEW}"
              "Elena\n“That's... a breathing technique.”{NEW}"
              "Scarlet\n“Kyahaha! She's terrified, darling.”",
         ask="Tifa\n“Cloud?”",
         choices=[("Elena, sit this out if you like.",
                   "Elena\n“...Thank you.”\n{NEW}Scarlet\n“One down.”", dict(leave=["elena"])),
                  ("You signed the contract Elena.",
                   "Elena\n“...Right. Fine.”{NEW}Aerith\n(She gives Cloud a long look)",
                   dict(gil=-10, annoy=["elena"])),
                  ("Tifa, talk to her.",
                   "Tifa\n(She whispers to Elena){NEW}Elena\n“...Okay. Thanks Tifa. I'm in.”", dict(gil=5, rules=True))]),
]
SCENE_AT_TURN = 2                  # the part's second turn (a scene's own `turn` overrides it)
# (user, since) real conflicts between the women, from their hidden histories (`_backstories`): each
# hits a nerve without telling the secret (that's for the final dates' revelations); one more per part,
# at its fourth turn
SCENES += [
    dict(part=0, turn=4, girls=["scarlet", "tifa", "aerith"],
         talk="Scarlet\n“Head down, sweetie. Let me help you.”{NEW}"
              "Tifa\n“Don't. Touch. Me!”{NEW}"
              "Scarlet\n“It's a movie, darling. Relax.”{NEW}"
              "Aerith\n“She said don't.”",
         ask="Scarlet\n“Well? Whose set is this, puppy?”",
         choices=[("Scarlet, hands off. Now.",
                   "Scarlet\n(A long pause) “...Fine.”{NEW}Tifa\n(She mouths 'thank you')",
                   dict(annoy=["scarlet"])),
                  ("Tifa, it's part of the scene.",
                   "Tifa\n“...Right. Sorry.”{NEW}Tifa\n(Her eyes are a long way away)",
                   dict(gil=10, annoy=["tifa"])),
                  ("Everybody take five.",
                   "Tifa\n(She breathes, slowly, in and out.){NEW}Scarlet\n“...I didn't know. Sorry.”{NEW}Aerith\n“Huh. She CAN say it.”",
                   dict(gil=-5))]),
    dict(part=1, turn=4, girls=["elena", "scarlet", "ruby", "skye"],
         talk="Elena\n“Stop. Can we... stop for a second?”{NEW}"
              "Scarlet\n“Stop? A Turk doesn't say stop.\n Did Tseng teach you that?”{NEW}"
              "Elena\n(She flinches){NEW}"
              "Ruby\n“If she can't take it, i'll take\n over.”{NEW}"
              "Tifa\n“Hey! Leave her alone, both of you!”",
         ask="Ruby\n“Well? ”",
         choices=[("She said stop. Give her a minute.",
                   "Elena\n“...Thank ...you?”{NEW}Scarlet\n“Tch.”",
                   dict(rules=True, annoy=["scarlet"])),
                  ("Elena, try harder. You're up, Ruby.",
                   "Ruby\n“Watch and learn, Turk.”{NEW}Elena\n(She looks defeated)",
                   dict(gil=10, annoy=["elena"])),
                  ("Scarlet, that was out of line.",
                   "Scarlet\n“...Kyahaha. Was it?”{NEW}Skye\n(She squeezes Elena's hand)",
                   dict(annoy=["scarlet"]))]),
    dict(part=2, turn=4, girls=["aerith", "tifa", "skye"],
         talk="Aerith\n“Tifa, you're doing the voice again.”{NEW}"
              "Tifa\n“...What voice?”{NEW}"
              "Aerith\n“The 'everything's perfect' voice.”{NEW}"
              "Tifa\n“And you're doing the flower girl\n thing.”{NEW}"
              "Aerith\n(The smile drops off her face){NEW}"
              "Skye\n“Um. Are we... still rolling?”",
         ask="Skye\n“Cloud? Help?”",
         choices=[("You two. Is there a problem?.",
                   "Tifa\n“...We're okay.”{NEW}Aerith\n“Fine and dandy.”",
                   dict(gil=-10)),
                  ("Keep rolling.",
                   "(Nobody says a word)",
                   dict(gil=10, annoy=["tifa", "aerith"])),
                  ("Aerith, that wasn't fair.",
                   "Aerith\n“...You're right. I'm sorry, Tifa.”{NEW}Tifa\n“...It's fine.”",
                   dict(annoy=["aerith"]))]),
]

# (user) a conversation at the end (wrap or finisher): the girls' banter if nobody walked off and a
# bonus (`STAYED_BONUS` x gil a press), else the cameraman's remark; `WALKOUT` = everyone left (a CUT)
END_TALK = ("Tifa\n“Well, that was ...something.”{NEW}"
            "Ruby\n“You're welcome.”{NEW}"
            "Aerith\n“Ruby, as modest as ever.”{NEW}"
            "Scarlet\n“Same time next week, darlings.”{NEW}"
            "Elena\n“...I'd like that in writing.”{NEW}"
            "Aerith\n“Group hug anyone?”")
STAYED_BONUS = 20
END_STAYED = "Cameraman\n“Nobody walked off my set. That's a first!\n Bonus: {gil:,} gil.”"
END_LEFT = "Cameraman\n“Next time, read the room, star.\n Walkouts cost me money.”"
WALKOUT = "Cameraman\n“...They ALL walked?! CUT!\n We'll sell what we've got.”"


# (user, since) the arguments staged with the models, between turns: fade out, everyone placed for the
# scene (`set`), fade in, the talk up to page `split`, a beat (`mid`), the rest of the talk, Cloud's call,
# a reaction (`react`, one list per choice), the reply, fade back into the shoot. Spots are screen
# offsets in pixels (x right, y down) from `STAGE` (screen point of the widest floor, in front of the left
# bed), each resolved to the nearest floor (asserted within 30 px, actors 12 px apart); the girls not in
# `set` watch from `WATCH`. Entries: who: (sx, sy, pose, face) in `set`,
# (who, pose or None, face or None) in `mid` / `react`; pose "stand" / "kneel"; face = another actor
# ("cloud" too), "camera", "centre" or "away:<actor>" (her back to them).
# `anchor` (user) = {actor: another actor in `set`}: that actor's (sx, sy) is measured from the other's
# spot on screen (placed first), not from STAGE.
# `bed` (user) = [actors in `set`]: they snap to the nearest bed-top point (the beds' walkmesh, z 54 / 100 /
# 125: a stand or kneel there is drawn on the mattress) instead of the floor.
# `camera` (user) = (dx, dy) from STAGE: what the camera centres on in that scene (the nearest floor or bed
# point; default STAGE itself). The view stays inside the room's scroll limits.
STAGE = (-100, 72)
# (y down = towards the camera: the arguing girls in front, Cloud to one side, the watchers behind)
WATCH = [(-80, -40), (75, -45), (-95, -5), (95, -10), (-60, 35), (60, 40)]
STAGING = [
    dict(split=2,     # Scarlet directs; Elena objects | Aerith teases, Scarlet insists
         anchor={"cloud" : "elena" }, 
          bed=["scarlet", "elena", "cloud", "ruby"],  # (user) Cloud just right of her on screen
         set={"scarlet": (100, -40, "kneel", "elena"), "cloud": (30, 0, "stand", "elena"),
              "elena": (110, -40, "kneel", "cloud"), "aerith": (180, 30, "kneel", "elena"),
              "tifa": (160, 40, "kneel", "elena"),"ruby": (70, -20, "kneel", "tifa"),"skye": (80, -20, "kneel", "scarlet")},
         mid=[],
         react=[[],      #choice 1
                [],      #choice 2
                []]),    #choice 3
    dict(split=1,     # Ruby claims she was best | Skye protests, Aerith turns it on Cloud
         anchor={"cloud": "skye"},   # (user) Cloud just right of her on screen
         set={"ruby": (-20, 10, "stand", "cloud"), "skye": (20, 15, "stand", "ruby"),
              "cloud": (30, 0, "stand", "ruby"), "aerith": (-50, -25, "stand", "ruby"),
              "tifa": (0, -35, "stand", "cloud")},
         mid=[("skye", None, "cloud"), ("ruby", None, "skye"), ("aerith", None, "cloud")],
         react=[[("ruby", None, "camera"), ("skye", None, "ruby")],
                [("ruby", None, "away:skye"), ("skye", None, "cloud")],
                [("tifa", None, "cloud"), ("ruby", None, "skye")]]),
    dict(split=2,     # Aerith notices Elena holding her breath, Elena insists | Scarlet mocks
         anchor={"cloud": "scarlet"},   # (user) Cloud just right of her on screen
         set={"elena": (0, 15, "kneel", "camera"), "aerith": (-40, -10, "stand", "elena"),
              "scarlet": (35, -20, "stand", "elena"), "tifa": (-40, 30, "stand", "elena"),
              "cloud": (30, 0, "stand", "elena")},
         mid=[("scarlet", None, "elena"), ("elena", None, "away:scarlet")],
         react=[[("elena", "stand", "away:cloud"), ("scarlet", None, "cloud")],
                [("aerith", None, "cloud"), ("elena", None, "camera")],
                [("tifa", "kneel", "elena"), ("elena", None, "tifa")]]),
    dict(split=1,     # Scarlet grabs Tifa's neck from behind | Tifa is up and facing her, Aerith steps in
         anchor={"cloud": "tifa"},   # (user) Cloud just right of her on screen
         set={"tifa": (5, 15, "kneel", "cloud"), "scarlet": (-15, 10, "stand", "tifa"),
              "cloud": (30, 0, "stand", "tifa"), "aerith": (-50, -20, "stand", "scarlet")},
         mid=[("tifa", "stand", "scarlet"), ("aerith", None, "scarlet"), ("scarlet", None, "tifa")],
         react=[[("scarlet", None, "away:tifa"), ("tifa", None, "cloud")],
                [("tifa", "kneel", "cloud"), ("scarlet", None, "camera")],
                [("tifa", None, "away:scarlet"), ("scarlet", None, "tifa"), ("aerith", None, "tifa")]]),
    dict(split=2,     # Elena asks to stop, Scarlet needles her | she flinches, Ruby wants in, Skye defends
         anchor={"cloud": "elena"},   # (user) Cloud just right of her on screen
         set={"elena": (0, 15, "kneel", "cloud"), "scarlet": (-40, -5, "stand", "elena"),
              "ruby": (30, -30, "stand", "cloud"), "skye": (-45, 30, "stand", "elena"),
              "cloud": (30, 0, "stand", "elena")},
         mid=[("elena", None, "away:scarlet"), ("skye", None, "scarlet"), ("ruby", None, "elena")],
         react=[[("elena", None, "cloud"), ("scarlet", None, "away:cloud")],
                [("ruby", None, "elena"), ("elena", "stand", "away:ruby")],
                [("scarlet", None, "camera"), ("skye", None, "elena")]]),
    dict(split=3,     # Aerith calls out Tifa's voice | Tifa hits back, Aerith's smile drops, Skye
         anchor={"cloud": "skye"},   # (user) Cloud just right of her on screen
         set={"aerith": (-30, 15, "stand", "tifa"), "tifa": (25, 15, "stand", "aerith"),
              "skye": (0, -25, "stand", "cloud"), "cloud": (30, 0, "stand", "tifa")},
         mid=[("tifa", None, "aerith"), ("aerith", None, "away:tifa"), ("skye", None, "tifa")],
         react=[[("aerith", None, "tifa"), ("tifa", None, "aerith")],
                [("tifa", None, "camera"), ("aerith", None, "away:tifa")],
                [("aerith", None, "tifa"), ("tifa", None, "cloud")]]),
]
assert len(STAGING) == len(SCENES) and all(len(s["react"]) == len(c["choices"]) for s, c in zip(STAGING, SCENES))

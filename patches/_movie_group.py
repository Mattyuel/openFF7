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
# HEAD_GAP from Cloud as in the one-girl "head" (38 ahead, 6 to his right): line one at x -20
# facing +x, line two at x 56 facing -x, Cloud between them at x 18
HEAD_X, HEAD_YS = (-20, 56), (-125, -85, -45)    # (user, since) up the bed, away from its end
HEAD_GAP, HEAD_RIGHT = 38, 1                 # (user, since) his pelvis on her face (was 6)

# part two: two girls per bed lying along it, heads over its near end (y -), XYZI by her feet as
# the one-girl "head reverse" (the left bed: girl y -54 with its end at -134, Cloud 96 nearer);
# (bed x lanes, the bed's near end y, the bed top's height)
BEDS = [((-255, -196), -134, 54), ((-14, 50), -181, 100), ((198, 256), -193, 125)]
HEADREV_ALONG, HEADREV_CLOUD = 80, 96

RATE = 70                     # gil a press (10 more than Aerith); the finisher pays x 100
TURN = 450                    # frames each girl (15 s)

# the others watching (user: they comment too; "fun, sexy, competitive, complimenting each
# other's abilities in explicit ways"), in character; part one ("head") / part two ("head reverse")
COMMENTS = {
    "ruby": (["Look at her take him... okay, she's good.", "Deep throat AND eye contact? Show-off.",
              "Wait till he gets to me. I'll make him beg.", "Her tongue's doing that swirl thing.\n Respect.",
              "Not bad, rookie. Not as deep as me, though.", "Bet I make him finish faster than her."],
             ["Upside down, she takes it right down\n her throat. Damn.", "Look at her throat bulge. Hot.",
              "Hold her hips, star, she's sliding off!", "Pfft. I did that my first week.",
              "She's not even blinking. Total pro.", "Next it's me, and I don't tap out."]),
    "skye": (["Wow, she took ALL of it! How?!", "Teach me that! The thing with the lips!",
              "My turn, my turn! I go deeper, watch!", "She's drooling everywhere... so hot.",
              "I'm gonna make him see stars. Just saying.", "Okay, she's really, really good at that."],
             ["Upside down! He goes in SO deep!", "Her legs are shaking! Haha, so cute!",
              "I wanna try that again! Twice!", "She swallowed it all?! Wooow.",
              "My turn's gonna be legendary.", "Okay, she's amazing. I'm still better."]),
    "elena": (["Is she not even gagging? How?!", "I-I could do that. Probably. Maybe.",
               "Her lips are wrapped so tight... wow.", "Professionally speaking, that's\n flawless form.",
               "The Turks train for endurance, you know.", "When it's my turn, I'm not holding back."],
              ["Blood's rushing to my head...\n and elsewhere.", "Th-that angle is very... efficient.",
               "No gag reflex at all! Unreal!", "I'll outlast all of you. Turk training.",
               "Okay. I'm officially impressed.", "Wh-what? I'm studying her technique!"]),
    "scarlet": (["Kyahaha! Cute. Now watch a woman work.", "She's sloppy. I'll swallow him whole.",
                 "Grab her hair, darling. Make her take it.", "Mmm, not bad, girl. Your jaw must ache.",
                 "I'll have him trembling in ten seconds.", "Save your strength, darling. I'm next."],
                ["Kyahaha! A throat like a vise, that one.", "Hang her lower, darling. All the way.",
                 "Look at her take it. I'm almost jealous.", "When he gets to me, he'll scream.",
                 "Pound her throat, darling. She loves it.", "That's my girl! Kyahaha!"]),
    "tifa": (["Wow, she's going all the way down!", "Cloud, don't you dare finish before me!",
              "That's... impressive. I'm taking notes.", "My mouth's watering just watching.",
              "Bet I can make him moan louder\n than that.", "Breathe through your nose! You've got this!"],
             ["Her throat's taking all of him... wow.", "Easy, Cloud! ...Actually, don't.",
              "Okay, she's good. But I'm Tifa.", "My head's spinning... I want more.",
              "Look at her hands grabbing his ass!", "I'm gonna leave him weak in the knees."]),
    "aerith": (["Ooh, she's so deep! Gold star for her!", "Hehe, she's making him shake. Cute!",
                "I'll be slow and sweet. He'll melt.", "Look at her eyes watering... so pretty.",
                "Hey, no hogging! Save some for me!", "She's good, but I'm better. Promise."],
               ["Upside down and still smiling! Amazing!", "Hehe, her toes are curling!",
                "Ooh, he's buried all the way in her!", "When he gets to me, he'll see\n the Promised Land.",
                "That's sooo good. I'm so ready.", "Everyone's so talented! I love this!"]),
}
# the engaged girl (user: muffled)
MUFFLED = {"ruby": ["Mmph... mmm!", "Mmf... mmh, mmh...", "Hnn... mmph!"],
           "skye": ["Mmmph! Mmm-hmm!", "Gk... mmh! Mmmh!", "Mmf mmf mmf!"],
           "elena": ["Mmph?! Mmm...", "Mmf... mm-hm...", "Hnnh... mmph!"],
           "scarlet": ["Mmm... mmmh!", "Hmmph... mmm-hm!", "Mmf... kyahmm!"],
           "tifa": ["Mmh... mmph!", "Mmm... mmf...", "Hnn... mmmh!"],
           "aerith": ["Mmm... hehmm!", "Mmph... mm-hm!", "Mmf... mmmh!"]}

INTRO = ["“The whole gang's here! Ladies, take your places.\n Star... you know what to do.”",
         "“One at a time, fifteen seconds each, no favourites.\n Then we flip 'em over and do it again.”",
         "“Same rules: tap OK, mind the meter, red at\n either end and we're done. Ready?”"]
AFTERMATH = "(The six of them collapse on the beds in a\n giggling, breathless heap. Someone asks for water.)"
NEWS = ["“Star, you've been with every girl on my books.\n You know what that means? A group shoot!”",
        "“Ruby, Skye, Elena, Scarlet, Tifa and Aerith,\n all on one set. Pick 'Everyone' next time.”"]

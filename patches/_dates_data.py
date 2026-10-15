"""Dates with the Honey Bee girls (docs/dates_plan.md): data.

DATES[name] = {
  speaker  her name in text windows (default: her name; {TIFA} = the party name)
  greet    her line before the talk menu ("Just chat." / "Ask her on a date.")
  where    her line before "Where to?"
  tiers    [first (affection 0-9), second (10-19), third (20)], each:
    open     her first line (the same in every place: user)
    steps    in order: ("G", her line) / ("C", Cloud's line) /
             ("Q", question, [answers], right index, line if right, line if wrong) /
             ("A", action): one of hers (660 GIRL_EXTRA: "stand", "slap")
             A right answer: +1 affection (capped at 20). Any wrong one this date
             is noted (the third date's choice needs none).
    close    her last line (first and second dates; the third date when a
             question went wrong)
  lead     third date, every answer right: her line before the choice
  part2    {place: lines}: "Give into your desires.": part two's lines (("G"|"C", line); ("act", "stop"|"go"|
           "fast")), after the switch to the undressed models, in that place's position (660 `POSITION`, user:
           one position per place); part2_music = its track
  desire   {place: the closing narration}
  leave    "Leave it be.": her line
  music    {place: index} (exe music name table, AKAO 10)
}
Lines are 3 rows at most, ~38 characters per row; speaker names are added.
"""

DATES = {
    "Tifa": {
        "speaker": "{TIFA}",
        "greet": "“Hey, Cloud. Need something?”",
        "where": "“A date? Me? …Okay! Where to?”",
        "music": {"gondola": 49, "capsule": 34, "cannon": 34, "beach": 35},   # DATE (Interrupted by Fireworks), TIFA (her theme)
        "tiers": [
            {   # first date: getting to know her
                "open": "“So… this is a date, huh?\n I'm a little nervous.”",
                "steps": [
                    ("G", "“It feels strange. Just us, and\n nothing we have to fight.”"),
                    ("C", "“…Yeah. It's quiet.”"),
                    ("G", "“Okay, Mr. Quiet. Let's see how\n well you know me.”"),
                    ("Q", "“Who taught me to fight?”", ["Master Zangan.", "Barret.", "Your dad."], 0,
                     "“You remembered! He'd be so proud,\n he'd make me do a hundred push-ups.”",
                     "“Ha! Not even close. It was Zangan.\n Little old man, very scary kicks.”"),
                    ("G", "“I left Nibelheim to train with him.\n Then I left again… for Midgar.”"),
                    ("Q", "“And what did I call my bar?”", ["Seventh Heaven.", "Tifa's Place.", "The Honey Bee."], 0,
                     "“Seventh Heaven. Barret thinks the\n name's about him. Don't tell him.”",
                     "“Cloud! It's Seventh Heaven,\n and you know it.”"),
                ],
                "close": "“Thanks for tonight. Let's do this\n again… soon, okay?”",
            },
            {   # second date: her past, the promise
                "open": "“I was hoping you'd ask me out again.”",
                "steps": [
                    ("G", "“Can I tell you something? When I\n was a kid, I was always waiting.”"),
                    ("C", "“…Waiting for what?”"),
                    ("G", "“For things to change. For somebody\n to come and get me.”"),
                    ("Q", "“Remember where we made our promise?”",
                     ["The water tower in Nibelheim.", "The well.", "The train station."], 0,
                     "“Under all those stars. You were so\n serious. I almost laughed.”",
                     "“Cloud… the water tower. Under the\n stars. How could you forget?”"),
                    ("Q", "“And what did you promise me?”",
                     ["To save you if you were in trouble.", "To buy you a drink one day.",
                      "To never leave Nibelheim."], 0,
                     "“Your childhood friend, in a pinch.\n …You kept it, you know. More than once.”",
                     "“Hmph. You promised to come save me.\n I'm still keeping score.”"),
                ],
                "close": "“Next time, let's stay out\n even later.”",
            },
            {   # third date: what she wants
                "open": "“I've been looking forward to this\n all week.”",
                "steps": [
                    ("G", "“I used to keep everything inside.\n My bar, my friends… my feelings.”"),
                    ("Q", "“Do you know what I lost when\n I was little?”", ["Your mother.", "Your first pet.", "Your lucky gloves."], 0,
                     "“Mom. I climbed Mt. Nibel to find her…\n and you followed me. You always did.”",
                     "“…It was my mom. I don't talk about it\n much. Maybe I should. With you.”"),
                    ("Q", "“And what do I want most?”", ["For me to stay.", "A bigger bar.", "To beat Master Zangan."], 0,
                     "“For you to stay. Just… stay.\n Here. With me.”",
                     "“Ha… no. Something much simpler\n than that.”"),
                    ("Q", "“Cloud… what do YOU want?”", ["You, Tifa.", "A quiet life somewhere.", "Some sleep."], 0,
                     "“…Then come here.”",
                     "“Ha ha… right. Of course.”"),
                ],
                "close": "“Tonight was perfect anyway.\n Thank you, Cloud.”",
            },
        ],
        "lead": "“We don't have to talk anymore,\n do we?”",
        "desire": {   # (user, since) one position per place; the closing narration per place
            "gondola": "The lights outside melted into a warm blur,\nand for a long while nothing else mattered...",
            "capsule": "Outside, the stars wheeled slowly past,\nand neither of them counted them...",
            "cannon": "The sea wind tugged at them both,\nand for once Tifa held nothing back...",
            "beach": "The tide came in and went out again,\nand the lounger creaked its quiet protest..."},
        "leave": "“…Okay. This is nice too. Just you\n and me, and the view.”",
        "part2_music": 62,                                    # GEKI (Debut), as her Honey Bee part two
        # (user, since) per place (`660 POSITION`); Tifa (`_movie_profiles`, the mediator): warm, direct,
        # checking he's alright, humour softening it
        "part2": {
            "capsule": [("G", "“Stars everywhere… and you're\n looking at me. Good.”"),
                        ("C", "“…Hard not to.”"),
                        ("G", "“Hold my hips. …Gently. I want\n to remember this one.”"),
                        ("G", "“Mmh… Cloud… you can go faster.\n I'm not going to break.”"),
                        ("act", "fast"),
                        ("G", "“…Don't let go. Not tonight.”")],
            "gondola": [("G", "“Mmh… mmf…\n (He's shaking. Nervous? …Cute.)”"),
                        ("C", "“Tifa… you don't have to—”"),
                        ("act", "stop"),
                        ("G", "“…Pwah. I want to. Let me take\n care of you, for once.”"),
                        ("act", "go"),
                        ("G", "“Mmmh… (Hand in my hair. Yes.\n Just like that.)”"),
                        ("act", "fast"),
                        ("G", "“Mmf! Mmh…!\n (Don't hold back, Cloud…)”")],
            "cannon": [("G", "“Don't you dare put me down.”"),
                       ("C", "“…Wasn't planning on it.”"),
                       ("G", "“Mmh… Cloud… harder…\n …I mean, hold me tighter!”"),
                       ("G", "“…Okay. I meant both.”"),
                       ("act", "fast"),
                       ("G", "“The whole of Junon could be\n watching. I don't care.”")],
            "beach": [("G", "“Lie back. Your turn to be\n taken care of.”"),
                      ("C", "“…Someone could come.”"),
                      ("G", "“Then we'd better be quick.\n …Kidding. Take your time.”"),
                      ("act", "fast"),
                      ("G", "“Mmh… Cloud… look at me.\n Stay with me. Right here.”")]},
    },
    "Aerith": {
        "speaker": "{AERIS}",
        "greet": "“Oh, Cloud! Did you need something?”",
        "where": "“A date? Ehehe, yes please!\n Where are we going?”",
        "music": {"gondola": 49, "capsule": 12, "cannon": 12, "beach": 35},   # DATE, EARIS (her theme)
        "tiers": [
            {   # first date: the flower girl
                "open": "“A date! With a bodyguard, even.\n Lucky me.”",
                "steps": [
                    ("G", "“So, Mr. Bodyguard… how much do\n you actually know about me?”"),
                    ("Q", "“What do I sell in the slums?”", ["Flowers.", "Potions.", "Materia."], 0,
                     "“Flowers! Only a gil each.\n A bargain, really.”",
                     "“Nope! Flowers. You bought one,\n remember?”"),
                    ("G", "“I grow them in the church. They\n won't grow anywhere else in Midgar.”"),
                    ("Q", "“And where do I live?”", ["Sector 5 slums.", "Wall Market.", "Upper Midgar."], 0,
                     "“With my mom, Elmyra. She worries…\n a lot.”",
                     "“Sector 5! You walked me home,\n silly.”"),
                ],
                "close": "“That was fun. Let's do it again,\n okay?”",
            },
            {   # second date: the Planet, the past
                "open": "“A second date! Should I be worried?”",
                "steps": [
                    ("G", "“Can I tell you a secret? I hear\n voices. The Planet, talking.”"),
                    ("C", "“…Does it say anything nice?”"),
                    ("G", "“Tonight it's very quiet.\n I think it's giving us privacy.”"),
                    ("Q", "“Do you know what I am?\n The last of the…?”", ["Cetra.", "Turks.", "SOLDIERs."], 0,
                     "“The Ancients. The last one.\n …It's lonely, sometimes.”",
                     "“The Cetra, silly. The Ancients.”"),
                    ("Q", "“Who was the first boy I liked?”",
                     ["Someone in SOLDIER.", "Reno.", "Barret."], 0,
                     "“Mm-hm. He looked a little\n like you…”",
                     "“Reno?! Please. Someone in SOLDIER.”"),
                ],
                "close": "“Next time, you pick the place.\n Deal?”",
            },
            {   # third date (user, since: her profile, the playful instigator: teasing, perceptive,
                # disarmingly direct, and she doesn't simply agree to anything; was playfully submissive)
                "open": "“Third date. Ehehe… you know what\n that means, right?”",
                "steps": [
                    ("G", "“Don't look so scared. I don't bite.\n …Much.”"),
                    ("G", "“Can I ask you something real?\n No dodging, bodyguard.”"),
                    ("Q", "“Why do you keep coming back?”", ["Because it's you.", "You're good cover.", "The free flowers."], 0,
                     "“…Oh. That's a better answer than\n I expected. Ehehe.”",
                     "“Wrong! Try again some other\n lifetime, mister.”"),
                    ("G", "“You know, you smile more when\n you think nobody's looking.”"),
                    ("Q", "“So who's in charge tonight?”", ["Nobody. Both of us.", "You are.", "I am."], 0,
                     "“Good answer. Bossing you around is\n fun, but this is better.”",
                     "“Hmm. Bossy, or a pushover.\n Neither's very you.”"),
                    ("Q", "“Last one. What do you want?”", ["You, Aerith.", "A nap.", "To stop being teased."], 0,
                     "“…Then you'll have to come and\n get me. Ehehe.”",
                     "“Pfft. Liar.”"),
                ],
                "close": "“Thank you for tonight, Cloud.\n Really.”",
            },
        ],
        "lead": "“So… are you going to kiss me,\n or do I have to do everything?”",
        "desire": {
            "gondola": "Somewhere a flower bloomed out of season,\nand the Planet politely looked away...",
            "capsule": "The stars outside watched in silence,\nand Aerith laughed softly into the dark...",
            "cannon": "Far below, the sea kept its secrets,\nand so did they...",
            "beach": "The waves washed their footprints away,\nbut not the smile on Aerith's face..."},
        "leave": "“…Okay. Just holding hands, then.\n I like that too.”",
        "part2_music": 49,                                    # DATE, as her Honey Bee part two
        "part2": {
            "gondola": [("G", "“Mmh… mmf…\n (Ehehe. He's turning so red.)”"),
                        ("C", "“…Aerith.”"),
                        ("G", "“Mmf? (What? I'm busy.)”"),
                        ("act", "stop"),
                        ("C", "“…Are you okay?”"),
                        ("G", "“…Pwah. I'm wonderful. You're the\n one who forgot to breathe.”"),
                        ("act", "go"),
                        ("G", "“Mmh… mmmh… (Hand in my hair.\n Gentle… then not so gentle.)”"),
                        ("act", "fast"),
                        ("G", "“Mmmf! (…There he is.)”")],
            "capsule": [("G", "“Ooh, look, a shooting star!\n …Made you look. Ehehe.”"),
                        ("C", "“…You're impossible.”"),
                        ("G", "“And you're slow. Come on, the\n stars won't wait all night.”"),
                        ("act", "fast"),
                        ("G", "“Mmh…! Okay… okay, you win.\n …This time.”")],
            "cannon": [("G", "“Whoa! Don't drop me off the\n cannon, okay? Promise?”"),
                       ("C", "“…Promise.”"),
                       ("G", "“Ehehe… your heart's racing.\n I can feel it.”"),
                       ("act", "fast"),
                       ("G", "“Mmh… Cloud… don't let go.\n …I mean it. Not ever.”")],
            "beach": [("G", "“My turn to drive. Hands where\n I can see them, bodyguard.”"),
                      ("C", "“…Yes, ma'am.”"),
                      ("G", "“Ehehe. 'Ma'am.' I like that\n better than 'sir'.”"),
                      ("act", "fast"),
                      ("G", "“Mmh…! The sea's so loud…\n Good. Nobody can hear us.”")]},
    },
    "Scarlet": {
        "greet": "“Well, well. Spiky.\n You want something?”",
        "where": "“A date? With ME? Kyahaha!\n Fine. Impress me.”",
        "music": {"gondola": 49, "capsule": 16, "cannon": 16, "beach": 35},   # DATE, PARADE (Rufus' Welcoming Ceremony)
        "tiers": [
            {   # first date: the executive
                "open": "“Don't get the wrong idea. I only\n came for the view.”",
                "steps": [
                    ("G", "“So. What do you know about me,\n besides the fabulous dress?”"),
                    ("Q", "“What do I run at Shinra?”",
                     ["Weapons Development.", "Public Safety.", "Urban Development."], 0,
                     "“Correct. I build the big guns.\n The BIGGEST.”",
                     "“Ugh. Weapons, darling. WEAPONS.”"),
                    ("G", "“Heidegger shouts. I get things\n done. Remember that.”"),
                    ("Q", "“And my favourite toy?”", ["The Proud Clod.", "A teddy bear.", "A chocobo."], 0,
                     "“My beautiful robot. Kyahaha!”",
                     "“Please. The Proud Clod.\n Do keep up.”"),
                ],
                "close": "“Not entirely boring. Don't let it\n go to your head.”",
            },
            {   # second date: what she wants
                "open": "“Back again? You must like being\n bossed around.”",
                "steps": [
                    ("G", "“People call me cruel. I'm just\n honest about what I want.”"),
                    ("C", "“…And what do you want?”"),
                    ("G", "“Everything. Starting with you\n doing as you're told.”"),
                    ("Q", "“What do I say when I'm pleased?”", ["Kyahaha!", "Hmph.", "Wahaha!"], 0,
                     "“Kyahaha! See? You're learning.”",
                     "“Wrong! Kyahaha. Practise it.”"),
                    ("Q", "“Who did I slap silly in Junon?”", ["Tifa.", "Rufus.", "Reno."], 0,
                     "“She had it coming. …She hit back,\n too. Hmph.”",
                     "“Tifa, darling. Pay attention.”"),
                ],
                "close": "“Same time next week.\n That's an order.”",
            },
            {   # third date (user): the dominatrix comes out; a slap before each question; (user, since: her
                # profile, the controlling showwoman: someone else's confidence punctures her composure)
                "open": "“Tonight, puppy, you speak when\n I say so. Not before.”",
                "steps": [                                  # (user: she starts standing close to him)
                    ("G", "“Eyes on me. Good.\n Now… let's test you.”"),
                    ("A", "slap"),
                    ("Q", "“Who's in charge here?”", ["You are, Scarlet.", "I am.", "Barret."], 0,
                     "“Kyahaha! Good boy.”",
                     "“Wrong answer, puppy.”"),
                    ("G", "“Everyone at Shinra flinches when\n I walk in. You don't. Why not?”"),
                    ("Q", "“Well? Why not?”", ["I like who you are.", "I'm scared stiff.", "Heidegger's scarier."], 0,
                     "“…That's not… Hmph. Nobody says\n that to me.”",
                     "“Liar. Kyahaha. …Pity.”"),
                    ("G", "“…Don't look at me like that.\n I'm still in charge.”"),
                    ("A", "slap"),
                    ("Q", "“Say my name. Properly.”", ["Scarlet.", "Mistress.", "Boss."], 0,
                     "“…Mmm. Again. Slower.”",
                     "“Not tonight. Tonight, my name.”"),
                ],
                "close": "“You need more training.\n Much more.”",
            },
        ],
        "lead": "“You've earned a reward, puppy.\n Don't make me regret it.”",
        "desire": {
            "gondola": "Somewhere below, the lights burned on,\nand Scarlet's laughter carried on the wind...",
            "capsule": "The stars bore silent witness,\nand Scarlet, for once, let someone else lead...",
            "cannon": "The biggest gun in Junon had never\nbeen quite this distracting...",
            "beach": "The sand cooled slowly under them,\nand Scarlet's hand stayed in his..."},
        "leave": "“Teasing me? Clever boy.\n …I'll allow it. Tonight.”",
        "part2_music": 16,                                    # PARADE, as her Honey Bee part two
        "part2": {
            # (user) she in front of him, making demands (the old wall scene: now the capsule's "behind")
            "capsule": [("G", "“Kyahaha! Harder, puppy!\n Did I say you could slow down?”"),
                        ("C", "“…Yes, ma'am.”"),
                        ("G", "“MISTRESS! And don't you dare\n stop until I say so.”"),
                        ("act", "stop"),                            # (user) she stops him
                        ("G", "“…Wait. Did I say you could\n put it THERE?”"),
                        ("C", "“…Uh.”"),
                        ("G", "“…Hmph. Fine. I'll allow it.\n This time.”"),
                        ("act", "fast"),                            # (user) and he carries on faster
                        ("G", "“Mmh…! That's… better.\n Good boy. Kyahaha…!”")],
            "gondola": [("G", "“Don't get used to this view,\n puppy. It's a one-time show.”"),
                        ("G", "“Mmh… (Kyahaha… look at him\n trembling. Mine.)”"),
                        ("act", "stop"),
                        ("G", "“…Pwah. Slower. I decide the\n pace, even down here.”"),
                        ("act", "go"),
                        ("G", "“Mmmh… (…He looks at me like I'm\n something precious. Hmph.)”"),
                        ("act", "fast"),
                        ("G", "“Mmf! (…Fine. Just this once.)”")],
            "cannon": [("G", "“Lift me. Higher. Let all of Junon\n see who I'm with.”"),
                       ("C", "“…Show-off.”"),
                       ("G", "“Kyahaha! You love it. Harder,\n puppy… and don't you dare drop me.”"),
                       ("act", "fast"),
                       ("G", "“Mmh…! …Cloud. Don't let go.\n …That's an order.”")],
            "beach": [("G", "“Lie back. On MY lounger. I'm\n taking what's mine.”"),
                      ("C", "“…It's my lounger.”"),
                      ("G", "“Kyahaha! Not anymore.\n Hands behind your head.”"),
                      ("act", "fast"),
                      ("G", "“Mmh…! Don't… don't look at me\n like that… Oh, keep looking.”")]},
    },
    "Elena": {
        "greet": "“Oh! C-Cloud! I'm on duty…\n sort of. What is it?”",
        "where": "“A date?! Tseng can't know.\n …Okay! Where?”",
        "music": {"gondola": 49, "capsule": 29, "cannon": 29, "beach": 35},   # DATE, SINRA (Shinra, Inc.)
        "tiers": [
            {   # first date: the rookie
                "open": "“Is this a stakeout? It feels like\n a stakeout. …Sorry. Habit.”",
                "steps": [
                    ("G", "“I'm the newest Turk, you know.\n Still learning the ropes.”"),
                    ("Q", "“Who's my boss?”", ["Tseng.", "Reno.", "Heidegger."], 0,
                     "“Tseng. He's… very impressive.\n Not that I've noticed.”",
                     "“Tseng! Don't let Reno hear you.”"),
                    ("Q", "“And why did I get into the Turks?”",
                     ["Reno got hurt.", "Rude retired.", "I won a contest."], 0,
                     "“Reno got hurt, so here I am.\n …Thanks to you, actually.”",
                     "“Reno got hurt. Because of YOU.”"),
                ],
                "close": "“That was… nice. Don't tell anyone.”",
            },
            {   # second date: always messing up
                "open": "“I told everyone I was on a mission.\n It's true. Mission: you.”",
                "steps": [
                    ("G", "“Can I tell you something? I always\n feel like I'm messing up.”"),
                    ("C", "“…You seem fine to me.”"),
                    ("G", "“Reno laughs. Rude stares. Tseng\n sighs. I can HEAR him sighing.”"),
                    ("Q", "“What do I always do too much?”", ["Talk.", "Sleep.", "Shoot."], 0,
                     "“Exactly! See? I'm doing it now.\n Sorry.”",
                     "“Ha… no. I talk. Too much. Like now.”"),
                    ("Q", "“How did I nearly blow a mission?”",
                     ["Told you the plan.", "Lost my gun.", "Fell asleep."], 0,
                     "“I told you the whole plan. Out loud.\n On a mountain. Ugh!”",
                     "“I literally told you our plan.\n Remember?”"),
                ],
                "close": "“Thanks for listening. Really.”",
            },
            {   # third date (user, since: her profile, the cautious professional: she wants to know what
                # happens before she does it, sets the rules, nervous and too proud to say so; was: she
                # doubts herself and asks to be punished)
                "open": "“I've, um, prepared a briefing.\n For tonight. Is that weird?”",
                "steps": [
                    ("G", "“Objective: time with you.\n Risks: …several. Mostly me.”"),
                    ("Q", "“Do you think I'm a good Turk?”", ["You're doing great.", "Not really.", "What's a Turk?"], 0,
                     "“…You really think so? Even after\n the mountain thing?”",
                     "“…Yeah. That's what I thought.”"),
                    ("G", "“I want this. I do. I just…\n need to know where I stand.”"),
                    ("Q", "“Can we set some ground rules?”", ["Your pace, your rules.", "Rules are for Turks.", "Let's wing it."], 0,
                     "“…Thank you. Rule one: if I say\n stop, we stop. Rule two: …be gentle.”",
                     "“Wing it?! I don't 'wing it'.\n …Sorry. I'm nervous.”"),
                    ("Q", "“And if I get nervous?”", ["I'll stop and hold you.", "Push through it.", "Call Tseng."], 0,
                     "“…Okay. Okay. I think I'm ready.”",
                     "“…Right. Maybe another time.”"),
                ],
                "close": "“I'll be braver next time.\n I promise.”",
            },
        ],
        "lead": "“Mission parameters… agreed.\n I'm ready. …I think. Yes.”",
        "desire": {
            "gondola": "Somewhere in Midgar, Tseng sighed,\nand didn't know why...",
            "capsule": "Out among the stars, Elena forgot\nevery rule but the ones they'd made...",
            "cannon": "The wind off the sea was cold,\nbut neither of them noticed...",
            "beach": "Elena dozed off on the lounger,\nand for once she didn't dream of work..."},
        "leave": "“…Okay. Maybe a hug is enough.\n Just this once.”",
        "part2_music": 38,                                    # CHASE (Crazy Motorcycle), as her Honey Bee part two
        "part2": {
            "capsule": [("G", "“Okay. This is… a lot of windows.\n Is anyone watching?”"),
                        ("C", "“Just the stars.”"),
                        ("G", "“…Good. Then… slowly. Please.”"),
                        ("act", "stop"),
                        ("G", "“Wait… no, I'm okay. I'm okay.\n That was good, actually. Go on.”"),
                        ("act", "go"),
                        ("G", "“Mmh… Report: everything is\n …extremely fine.”"),
                        ("act", "fast"),
                        ("G", "“Ah…! Mission status: …I've\n forgotten the mission.”")],
            "gondola": [("G", "“I, um, read about this. In a\n magazine. For research.”"),
                        ("G", "“Mmh… (Is this right? He looks\n happy. That's… a good sign.)”"),
                        ("act", "stop"),
                        ("C", "“…You can stop whenever you want.”"),
                        ("G", "“…Pwah. I know. That's why I don't\n want to.”"),
                        ("act", "go"),
                        ("G", "“Mmh… mmmh… (Tseng can never,\n ever know about this.)”")],
            "cannon": [("G", "“We're very high up. Statistically,\n this is not safe.”"),
                       ("C", "“I've got you.”"),
                       ("G", "“…I know. That's the only reason\n I'm doing this.”"),
                       ("act", "fast"),
                       ("G", "“Ah…! Cloud… don't let go.\n …Please. Rule three.”")],
            "beach": [("G", "“Lie back. I'll… set the pace.\n Rule one, remember?”"),
                      ("C", "“…Your rules.”"),
                      ("G", "“Mmh… okay. This is… I can do\n this. I'm doing this.”"),
                      ("act", "fast"),
                      ("G", "“Ah…! Report… no report.\n I'm off duty. Completely.”")]},
    },
}


# (user) the girls' hidden histories: hints appended as extra pages (`_backstories`)
import _backstories  # noqa: E402
_backstories.apply_dates(DATES)

"""Dates with the Honey Bee girls (docs/dates_plan.md): data.

DATES[name] = {
  speaker  her name in text windows (default: her name; {TIFA} = the party name)
  greet    her line before the talk menu ("Just chat." / "Ask her on a date.")
  where    her line before "Where to?"
  tiers    [first (affection 0-9), second (10-19), third (20)], each:
    open     her first line (the same in every place: user)
    steps    in order: ("G", her line) / ("C", Cloud's line) /
             ("Q", question, [answers], right index, line if right, line if wrong)
             A right answer: +1 affection (capped at 20). Any wrong one this date
             is noted (the third date's choice needs none).
    close    her last line (first and second dates; the third date when a
             question went wrong)
  lead     third date, every answer right: her line before the choice
  part2    "Give into your desires.": part two's lines (("G"|"C", line)), after the switch to
           the undressed models; part2_music = its track
  desire   then the closing narration
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
        "music": {"gondola": 49, "capsule": 34, "tower": 34},   # DATE (Interrupted by Fireworks), TIFA (her theme)
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
        "desire": "The lights outside melted into a warm blur,\nand for a long while nothing else mattered...",
        "leave": "“…Okay. This is nice too. Just you\n and me, and the view.”",
        "part2_music": 62,                                    # GEKI (Debut), as her Honey Bee part two
        "part2": [("G", "“Don't you dare put me down.”"),
                  ("C", "“…Wasn't planning on it.”"),
                  ("G", "“Mmh… Cloud… harder…\n …I mean, hold me tighter!”"),
                  ("G", "“…Okay. I meant both.”")],
    },
    "Aerith": {
        "speaker": "{AERIS}",
        "greet": "“Oh, Cloud! Did you need something?”",
        "where": "“A date? Ehehe, yes please!\n Where are we going?”",
        "music": {"gondola": 49, "capsule": 12, "tower": 12},   # DATE, EARIS (her theme)
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
            {   # third date (user): playfully submissive
                "open": "“Tonight… I'll do whatever you say.\n Ehehe.”",
                "steps": [
                    ("G", "“You're the bodyguard. So you give\n the orders tonight, right?”"),
                    ("Q", "“So, what's your first order?”", ["Come here, Aerith.", "Guard the door.", "Go home."], 0,
                     "“Yes, sir! …Like this? Closer?”",
                     "“Hmph. Boring orders. You can do\n better than that.”"),
                    ("Q", "“What should I call you tonight?”", ["Just Cloud.", "Sir.", "Bodyguard."], 1,
                     "“Yes, sir. Ehehe… I like that.”",
                     "“Mmm… I had something else in mind.”"),
                    ("Q", "“And what do you want me to do?”",
                     ["Anything I say.", "Sell me a flower.", "Stop teasing."], 0,
                     "“…Anything. Just say it.”",
                     "“Ehehe… you're no fun.”"),
                ],
                "close": "“Thank you for tonight, Cloud.\n Really.”",
            },
        ],
        "lead": "“Then… give me an order, sir.”",
        "desire": "Somewhere a flower bloomed out of season,\nand the Planet politely looked away...",
        "leave": "“…Okay. Just holding hands, then.\n I like that too.”",
        "part2_music": 49,                                    # DATE, as her Honey Bee part two
        # (user) the "head" scene: she tries to talk and can't; Cloud stops and asks if she's
        # okay, she demands more, he goes twice as fast
        "part2": [("G", "“Mmf! Mmh mm… mmf-mmh!\n (Yes, sir!…)”"),
                  ("G", "“Mmh-mmh… mmmf!”"),
                  ("act", "stop"),
                  ("C", "“…Aerith? Are you okay?”"),
                  ("G", "“…Pwah! Who said you could stop?\n More. That's an order, mister.”"),
                  ("act", "fast"),
                  ("G", "“Mmf!! Mmh-mmh mmf!\n (Ehehe… much better!)”")],
    },
}

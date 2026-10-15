"""(user) Cid as a friend: hang-outs (660's date places, no intimacy ending), gifts, affection (0-20,
`AFFECTION`), the first hang-out a quest (`_quest_data` "hangout_cid"). Max affection unlocks the
movie's Blast-off scenes (673). Built by 661_cid.py (his NPC by the rocket, his talk, his gifts) and
660_dates.py (the hang-outs: he is a companion in its date fields, `COMPANIONS`).

HANGOUT has DATES' layout (`_dates_data`): greet, where, music, tiers (open / steps / close), but no
lead / part2 / desire / leave: every tier ends with its close.
Lines are 3 rows at most, ~38 characters per row; the speaker's name is added.
"""

NAME = "Cid"
INDEX = 20                       # DATE_GIRL = INDEX + 1 on a hang-out (the Honey Bee girls are 0-19)
AFFECTION = (1, 110)             # 0-20 (bank 1 110: no script, world map or exe use; see _config)
MET = ((1, 111), 0)              # bit: talked to him (the affection list shows him from then on)
MAX = 20
FIELD, AT, ENTITY = "rcktbas1", (-1660, 4660), "cid"   # (user) by the rocket, north of Rocket Town (the
                                                        # fuel tank at its foot); his story copy's entity
MODEL = "main_cid.char"
DONOR = ("rcktin7", 4)           # a date field without him gets him from here
SIT = {"bench": "GDFF.chi"}      # bwhlin cid DFANM 03: his gondola sitting anim
PREFS = "ILH"                    # (user) practical, then beautiful, cute last: (beautiful, practical, sweet)
THEME = 20                       # SIDO: Cid's Theme (exe music name table index)

GREET = "“Well, if it ain't Spiky. What d'you\n want? Make it quick, I got a rocket\n to stare at.”"
CHAT = ["“Shera's inside makin' tea. Again.\n Woman makes tea like it's a\n religion.”",
        "“Thirty years I been lookin' up\n at that #$%& thing. One day,\n she's gonna fly.”",
        "“Don't touch the fuel line. I mean\n it. Last guy who did is still\n lookin' for his eyebrows.”"]
TALK_ASK = ["Just chat.", "Hang out.", "Give him something.", "Never mind."]
FIRST_MET = "“Name's Cid. Cid Highwind. Pilot,\n engineer, the greatest #$%& mind\n this town ever wasted.”"

# gifts (`_honey_bee_gifts.GIFTS`; the same key items as the girls'): reactions by how he likes the type
GIVE_PROMPT = "Give Cid the %s?"
REACT = {"L": "“Now THIS I can use! Hell, Spiky,\n you got some sense after all.”\n (Affection: {VAR}/20)",
         "I": "“Huh. Pretty. …Shera'd like it.\n Thanks, I guess.”\n (Affection: {VAR}/20)",
         "H": "“…What am I, twelve? Keep your\n candy, kid.”\n (Affection: {VAR}/20)"}
MAXED = "“You don't gotta keep bringin' me\n stuff. We're good, Spiky. Real good.”"
NO_GIFT = "“Empty-handed, huh? Story of my life.”"

HANGOUT = {
    "speaker": "Cid",
    "greet": GREET,
    "where": "“Hang out? With you? …Ah, what the\n hell. Rocket ain't goin' anywhere.\n Where to?”",
    "music": {"gondola": THEME, "capsule": THEME, "cannon": THEME, "beach": THEME},
    "tiers": [
        {   # first: sizing each other up
            "open": "“Alright, Spiky. Don't expect me to\n hold your hand or nothin'.”",
            "steps": [
                ("G", "“Ain't been out of that town in\n years. Feels weird. Good weird.”"),
                ("C", "“…You don't get out much?”"),
                ("G", "“Got a rocket to babysit. And a\n woman who thinks I'm gonna blow\n myself up. She ain't wrong.”"),
                ("Q", "“So what's my ship called?\n Bet you don't know.”", ["The Highwind.", "The Shera.", "The Tiny Bronco."], 0,
                 "“The Highwind! Named her after the\n best pilot alive. Me.”",
                 "“…Kid, it's the Highwind. Named\n after me. Pay attention.”"),
                ("Q", "“And what do I drink, all day,\n every #$%& day?”", ["Tea.", "Whiskey.", "Coffee."], 0,
                 "“Tea! Shera's fault. Now I can't\n sleep without the stuff.”",
                 "“Tea, dammit. Don't tell nobody.”"),
            ],
            "close": "“Not bad, Spiky. Not bad at all.\n Maybe we do this again.”",
        },
        {   # second: the launch that didn't happen
            "open": "“Back again, huh? Guess I ain't\n scared you off yet.”",
            "steps": [
                ("G", "“Y'know why that rocket's still\n sittin' there? 'Cause of me.”"),
                ("C", "“…What happened?”"),
                ("G", "“Launch day. Shera was checkin'\n an oxygen tank. I aborted. Blew\n my one shot at space.”"),
                ("Q", "“Why'd I stop the launch?”", ["To save Shera.", "The engine failed.", "Shinra ordered it."], 0,
                 "“…Yeah. To save her. Spent years\n blamin' her for it. Wasn't fair.”",
                 "“Nah. Shera was still inside.\n Couldn't let her fry.”"),
                ("Q", "“So. Think I was right to stop?”",
                 ["Yes. People over dreams.", "No. You should've gone.", "Doesn't matter now."], 0,
                 "“…Huh. You sound like her. Maybe\n you're both right.”",
                 "“…Maybe. Still eats at me, kid.”"),
            ],
            "close": "“Thanks for listenin'. Don't go\n spreadin' it around.”",
        },
        {   # third: friends
            "open": "“Spiky! Get over here. Brought a\n thermos. Tea. Don't say a word.”",
            "steps": [
                ("G", "“Never had many friends. Pilots,\n mechanics… folks who need\n somethin' fixed.”"),
                ("Q", "“What's the one thing I always\n wanted?”", ["To go to space.", "To run Shinra.", "To retire."], 0,
                 "“Space. Up there, past the clouds.\n …And you'd come with me, wouldn't\n you?”",
                 "“Space, kid! The stars! Ain't you\n been listenin'?”"),
                ("Q", "“And who'd I want up there with\n me?”", ["My friends.", "Nobody.", "Shinra's best."], 0,
                 "“…Yeah. My friends. Never said that\n out loud before. Don't make it\n weird.”",
                 "“Pfft. Wrong. …I'd want you\n lot along.”"),
                ("C", "“You're a good friend, Cid.”"),
                ("G", "“…Shut up. You too, Spiky.\n You too.”"),
            ],
            "close": "“Same time next week? I'll bring\n the tea. You bring the bad jokes.”",
        },
    ],
}

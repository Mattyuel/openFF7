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


# (user) Cloud's own reckoning: once Cid is at affection 20 and they've done a Blast-off together
# (BLASTED, set when the set is entered), a third-tier hang-out opens with Cid asking what's eating him.
# "Tell him." -> Cloud talks about why he's drawn to holding women down, hurting and controlling them
# (Hojo's tank, Sephiroth's voice, the lesson slaps, Elena's "stop"); Cid, understanding and not
# excusing, owns what he did to Shera and draws the line between a game two people agree on and
# taking your fear out on someone. "It's nothing." -> the usual hang-out (offered again next time).
# Once (TALKED). Every line Cloud's ("C") or Cid's ("G").
BLASTED = ((1, 111), 2)          # bit: a Blast-off shoot happened
TALKED = ((1, 111), 3)           # bit: the talk happened
TALK_MUSIC = 20                  # SIDO: Cid's Theme
TALK = dict(
    ask=("“You've been quiet all night, Spiky.\n Quieter'n usual, which is sayin'\n somethin'. What's eatin' you?”",
         ["Tell him.", "“It's nothing.”"]),
    nothing="“...Sure it is. Offer stands. Anytime.”",
    pages=[("C", "“...The shoots. The holding. The\n slaps. I'm good at it, Cid. And I\n like it. That's what's eating me.”"),
           ("G", "(Cid lights a cigarette and doesn't\n say anything. He just waits.)"),
           ("C", "“When she can't pull away... I feel\n solid. Like I'm actually me. Like\n nothing's going to slip.”"),
           ("C", "“Five years in Hojo's tank. I couldn't\n move a finger. Things were just...\n done to me.”"),
           ("C", "“And then that voice in my head,\n making me move. Making me hand it\n the Black Materia.”"),
           ("C", "“So when I'm the one holding her\n down, nobody's moving me. For once\n I'm the one in control.”"),
           ("C", "“Elena said stop, once. And there\n was a second where I didn't want to.\n That scared me more than anything.”"),
           ("G", "(Cid lets out a long breath of smoke.)\n “...Alright. My turn to say somethin'\n I ain't proud of.”"),
           ("G", "“After the launch got scrapped, I\n spent years makin' Shera feel small.\n Yellin'. Orderin'. Every damn day.”"),
           ("G", "“Wasn't about her. I was scared I was\n nothin' but a washed-up pilot. So I\n made sure somebody felt smaller.”"),
           ("G", "“Here's the thing, Spiky. Some folks\n like bein' held down. That's a deal\n two people make, out loud.”"),
           ("G", "“Takin' your fear out on somebody\n who never made that deal? That ain't\n control. That's the tank, again.”"),
           ("C", "“...And if the part of me that likes\n it is the part Hojo made?”"),
           ("G", "“Then you're the part askin' the\n question. That one's all yours.”")],
    stance=("“So what're you gonna do about it?”",
            [("“I want to change.”",
              [("G", "“Good. Start like I did with Shera:\n say sorry first. Mean it later. Keep\n at it till the two match.”")]),
             ("“I don't know if I want to stop.”",
              [("G", "“Honest. I'll take honest.” (He taps\n his ash.) “Then find someone who\n wants it too. And make damn sure.”"),
               ("G", "“Ask. Every time. And if you can't\n stand hearin' no... that's your sign,\n kid. That's the tank talkin'.”")])]),
    end=[("C", "“...Thanks, Cid.”"),
         ("G", "“Don't thank me. Just don't make me\n regret tellin' you about Shera.\n She'd kill me.”")],
)

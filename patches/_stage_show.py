"""(user) The Gold Saucer stage show (674): the troupe, famous from the videos, performs a live erotic
fantasy on the Event Square stage (astage_b, the play's own stage: only the story's play enters it).
Four acts; each is a clothed scene in costume where the women's real conflicts surface (written against
`_backstories` and `_movie_profiles`), Cloud's call, then a fade: undressed, a minigame with the meter.
Cast (user): Cloud the Hero, Aerith the Princess, Scarlet the Sorceress Queen, Elena the Knight Captain,
Tifa the tavern maid, Cid the Dragon King (the play's Dragon costume while clothed), the play's King as
the master of ceremonies. Unlocked by a full group shoot (`_config.SPECIAL_ON`) with Cid at affection 20;
the Booker in Event Square offers it. Lines are 3 rows at most, ~38 characters per row.

ACTS[i] = dict(
  title     the King's announcement (one text, pages)
  set       {actor: (x, y, face)}: the clothed staging (stage floor field units; face = actor / "camera")
  talk      pages before the beat, `mid` the beat [(actor, face)], talk2 the pages after
  ask       (speaker line, [(choice, reply pages, effects)]): effects gil (x SHOW_RATE), annoy [girls],
            finale (act 4: the bride, by key)
  react     one beat list per choice
  play      the minigame: kind "holding" / "cowgirl" (the movie's), "twinjets" / "exhaust" (Blast-off's),
            girl (key, or "bride" = act 4's choice), at (x, y), watch [bare actors standing behind]
  lines     4 lines while it plays ("C:" Cloud, "I:" Cid, "(...)" an action, else hers)
)
"""

SET = "astage_b"
SHOW_ON = ((1, 111), 4)          # set by the Booker's "Raise the curtain!", cleared on arrival
UNLOCK_CID = 20                  # Cid's affection (and a full group shoot, SPECIAL_ON)
FLOOR = 165                      # the stage floor's height (astage_b: one flat rectangle)
ARRIVE = (0, 300)
SCALE = 700 / 512                # astage_b's model scale over the movie's (pose offsets)
MINUTE = 1800                    # frames a minigame
SHOW_RATE = 60                   # gil a press (the house's cut of the tickets)
FINISH_BONUS = 6000              # the finale's finisher, on the spot
MUSIC = 49                       # DATE (Interrupted by Fireworks: the play's own music is the Gold Saucer's)
PLAY_MUSIC = 62                  # GEKI (Debut): the minigames
GIRLS = ["tifa", "aerith", "elena", "scarlet"]
NAMES = {"tifa": "Tifa", "aerith": "Aerith", "elena": "Elena", "scarlet": "Scarlet", "cid": "Cid",
         "cloud": "{CLOUD}", "king": "The King"}
BOOKER = dict(field="astage_a", entity="yufi", donor=("astage_b", 4), at=(750, -2800), back=(700, -2700))
BOOKER_LINES = dict(
    locked=["“A troupe of my own? Come back when\n the whole of Midgar knows your\n faces. ...And bring that pilot.”"],
    offer="“The Gold Saucer's buzzing about your\n little films, star! One night only:\n a live show. Interested?”",
    choices=["Raise the curtain!", "Not tonight."],
    no="“Suit yourself. The stage is yours\n whenever you want it.”",
    after="“Ha! What a night! Same time next\n week? The crowd's still screaming.”")

OPENING = ("The King\n“Ladies and gentlemen of the Gold\n Saucer! Tonight, for one night only...”{NEW}"
           "The King\n“...the troupe that set Midgar on fire!\n A tale of heroes, dragons and desire!”")
CURTAIN = ("The King\n“And so ends our tale! Give it up for\n our heroes, our princess... and our\n very tired dragon!”")
BOOED = "The King\n“Ahem! The, ah... curtain falls early\n tonight. Refunds at the box office.”"
WALKED = "The King\n“...Our leading lady has left the\n stage! The show is, ah, over!”"
FINISHER = "The King\n“WHAT A FINALE! The crowd is on its\n feet! Bravo! BRAVO!”"
SHOUT = "The King\n“Five seconds left! Give them a\n FINALE they'll never forget!”"
PAY = "The King\n“The house's cut of the tickets:\n {VAR} gil. A triumph!”"

ACTS = [
    dict(   # Act 1: the tavern. Elena (the script) vs Tifa (choosing for herself)
        title="The King\n“Act One: the Tavern at the Edge of\n the Kingdom! A hero walks in...”",
        set={"cloud": (-80, 520, "tifa"), "tifa": (120, 560, "cloud"), "elena": (-300, 640, "cloud"),
             "king": (-560, 300, "camera")},
        talk=["Elena\n“Barmaid! Serve the hero. Then kneel\n and thank him for his service.\n ...That's the script.”",
              "Tifa\n(She sets the tray down, slowly.)\n“...No. The barmaid doesn't kneel.”"],
        mid=[("elena", "tifa"), ("tifa", "elena"), ("cloud", "tifa")],
        talk2=["Elena\n(Hissing, out of character.)\n“Tifa! The crowd paid for the script!”",
               "Tifa\n“The barmaid chooses who she serves.\n And how.” (She looks at the hero.)"],
        ask=("Elena\n“Hero! Tell her to follow the script!”",
             [("“The barmaid chooses.”",
               "Tifa\n(Her smile is real, for once.)\n“...Thank you.”{NEW}Elena\n(She crosses her arms. The crowd\n cheers anyway.)",
               dict(gil=10, annoy=["elena"])),
              ("“Follow the script, Tifa.”",
               "Tifa\n“...Fine.” (She kneels. Her eyes go\n somewhere very far away.){NEW}Elena\n“Good. ...Good.”",
               dict(gil=-5, annoy=["tifa"])),
              ("“Let's ask the crowd!”",
               "The King\n(The crowd roars for the barmaid.)\n“The people have spoken!”{NEW}Tifa\n(She winks at Elena. Elena almost\n smiles.)",
               dict(gil=5))]),
        react=[[("tifa", "cloud"), ("elena", "camera")],
               [("tifa", "camera"), ("elena", "tifa")],
               [("king", "camera"), ("tifa", "elena"), ("elena", "tifa")]],
        play=dict(kind="holding", girl="tifa", at=(0, 520), watch=[]),
        lines=["“I chose you, hero. Don't make me\n regret it.”", "Mmh... hold me up. Don't you dare\n let go.",
               "C:...I've got you.", "(The crowd stamps its feet.)\n“Ahh... more!”"]),
    dict(   # Act 2: the Sorceress's lair. Scarlet (control, the audience) vs Elena ("yes, sir")
        title="The King\n“Act Two: the Lair of the Sorceress\n Queen! The brave knight is...\n captured!”",
        set={"scarlet": (0, 640, "elena"), "elena": (-90, 520, "scarlet"), "cloud": (300, 480, "scarlet"),
             "king": (-560, 300, "camera")},
        talk=["Scarlet\n“Kyahaha! On your knees, little knight.\n Say it for the crowd: ‘Yes, my\n queen.’”",
              "Elena\n(Her mouth opens. Nothing comes out.)"],
        mid=[("elena", "camera"), ("scarlet", "camera"), ("cloud", "elena")],
        talk2=["Elena\n(Quietly. Not in character at all.)\n“...No.”",
               "Scarlet\n(The crowd laughs. Her smile stays,\n but her eyes go cold.) “...Say it.”"],
        ask=("Scarlet\n“Hero! Make the knight obey her queen.”",
             [("“The knight said no.”",
               "Elena\n(She stares at you.) “...I did. I said\n no.”{NEW}Scarlet\n(For a second she looks lost. Then she\n laughs, too loudly.)",
               dict(gil=5, annoy=["scarlet"])),
              ("“Obey your queen, knight.”",
               "Elena\n“...Yes, my queen.” (Perfectly. Like\n she's said it a thousand times.){NEW}Scarlet\n“Kyahaha! Good girl.”",
               dict(gil=10, annoy=["elena"])),
              ("“The knight breaks the spell!”",
               "The King\n(Elena draws her prop sword. The crowd\n goes wild.){NEW}Scarlet\n(She plays along, fighting a grin.)\n“...Curse you, knight!”",
               dict(gil=10))]),
        react=[[("elena", "cloud"), ("scarlet", "cloud")],
               [("elena", "scarlet"), ("scarlet", "camera")],
               [("elena", "scarlet"), ("scarlet", "elena")]],
        play=dict(kind="cowgirl", girl="scarlet", at=(0, 560), watch=["elena"]),
        lines=["“Lie still, hero. The queen takes\n what she wants.”", "“Look at them watching. Look at\n ALL of them.”",
               "C:...You're shaking.", "“I'm NOT. ...Don't stop.”"]),
    dict(   # Act 3: the Dragon's cave. Aerith off script, Cid out of character, Tifa from the wings
        title="The King\n“Act Three: the Dragon's Cave! The\n Princess is held by the terrible\n Dragon King!”",
        set={"cid": (120, 680, "aerith"), "aerith": (-40, 600, "cid"), "cloud": (-320, 520, "aerith"),
             "tifa": (480, 420, "aerith"), "king": (-560, 300, "camera")},
        talk=["Cid\n(In the dragon suit.) “ROAR. ...Uh.\n Scream, princess. That's your cue.”",
              "Aerith\n“Why would I scream? Look at you.\n You're adorable.”"],
        mid=[("aerith", "camera"), ("cid", "aerith"), ("tifa", "aerith")],
        talk2=["Cid\n(Out of character.) “Lady, the script\n says SCREAM. I got one line!”",
               "Tifa\n(From the wings, sharp.) “Aerith.\n Stop hogging the scene.”",
               "Aerith\n“The princess doesn't need saving,\n Tifa. She's having fun.”"],
        ask=("Cid\n“Spiky! Rescue the damn princess!”",
             [("“The princess rescues herself.”",
               "Aerith\n(She curtsies to the crowd.) “Thank\n you, hero.”{NEW}Tifa\n(She turns away. Her jaw is tight.)",
               dict(gil=10, annoy=["tifa"])),
              ("“Scream for the dragon.”",
               "Aerith\n(A beat. Then a scream so fake the\n crowd howls with laughter.){NEW}Cid\n“...Thank you.”",
               dict(gil=5)),
              ("“Tifa, let her play.”",
               "Tifa\n“...Fine. She always gets to play.”{NEW}Aerith\n(Her smile falters, just for a second.)",
               dict(annoy=["tifa", "aerith"]))]),
        react=[[("aerith", "camera"), ("tifa", "camera")],
               [("aerith", "cid"), ("cid", "camera")],
               [("tifa", "camera"), ("aerith", "tifa")]],
        play=dict(kind="twinjets", girl="aerith", at=(-120, 560), watch=["tifa"]),
        lines=["“A dragon AND a hero? The princess\n is very greedy tonight.”", "Mmph! Mmh...",
               "I:Damn, she's enjoyin' this.", "Mmf! (She waves at the crowd.)"]),
    dict(   # Act 4: the castle finale. Who is the hero's bride?
        title="The King\n“Act Four: the Castle! The dragon is\n tamed... and the hero must choose\n his bride!”",
        set={"cloud": (0, 460, "camera"), "aerith": (-260, 600, "cloud"), "tifa": (260, 600, "cloud"),
             "elena": (-120, 760, "cloud"), "scarlet": (140, 780, "cloud"), "cid": (520, 640, "cloud"),
             "king": (-560, 300, "camera")},
        talk=["The King\n“The princess, as is tradition!”",
              "Scarlet\n“Boring! Let the CROWD vote, darling.\n Kyahaha!”"],
        mid=[("aerith", "tifa"), ("tifa", "aerith"), ("elena", "scarlet")],
        talk2=["Elena\n“The script says the princess.”",
               "Tifa\n(She says nothing. She's looking at\n the hero. Only at the hero.)",
               "Cid\n“...Kid. Choose already. My suit's\n gettin' hot.”"],
        ask=("The King\n“Hero! Who is your bride?”",
             [("“The Princess.”",
               "Aerith\n(She takes your hand, then glances at\n Tifa, and the smile is careful.){NEW}Tifa\n(She claps. She keeps clapping.)",
               dict(gil=10, finale="aerith")),
              ("“The barmaid.”",
               "Tifa\n(Off script. Her hand is shaking in\n yours.) “...Me?”{NEW}Aerith\n(She bows to Tifa. She means it.)",
               dict(gil=10, finale="tifa")),
              ("“The knight who said no.”",
               "Elena\n“I... the script doesn't...” (She\n swallows.) “...Yes. I mean: yes.”{NEW}Scarlet\n(Her applause is the loudest.)",
               dict(gil=10, finale="elena"))]),
        react=[[("aerith", "cloud"), ("tifa", "camera")],
               [("tifa", "cloud"), ("aerith", "tifa")],
               [("elena", "cloud"), ("scarlet", "elena")]],
        play=dict(kind="exhaust", girl="bride", at=(0, 520), watch=[]),
        lines=["“Hold me up. Both of you. Don't\n let go.”", "I:This is the finale, kid. Make it\n count!",
               "C:...Look at me. Not them. Me.", "“Ahh! The whole saucer's watching!”"]),
]

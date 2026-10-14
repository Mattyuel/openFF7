"""(user) The movie minigame's "Special" scenes (672_movie_special), data only: unlocked by a full
group shoot, picked per co-star ("Normal scene" / "Special scene"). Each is shot in Don Corneo's
bedroom (a copy of colne_6 per girl) and opens with the two of them role-playing a scenario,
clothed, in front of the bed; then three positions, a minute each: "insert" (the stroke speeding
up in four even steps: 4 s, 3 s, 2 s, 0.5 s), "head", and "finisher" (the cameraman's call for a
finisher comes in its last seconds, as in every shoot). They stay in character throughout.

All the women are adults; the scenarios are role-play between adults on a film set.

FIELDS: each girl's set (unused maplist names). INTRO: (speaker, line) pairs, speaker "C" = Cloud,
"G" = her. LINES: per position, her lines while it plays ("C:" = his line; "(...)" an action; head
muffled, as every shoot)."""

FIELDS = {"ruby": "qe", "skye": "pass", "elena": "hyou14", "scarlet": "xmvtes", "tifa": "fallp", "aerith": "m_endo"}
NAMES = {"ruby": "Ruby", "skye": "Skye", "elena": "Elena", "scarlet": "Scarlet", "tifa": "Tifa", "aerith": "Aerith"}

OPENING = ["“Special scene, star! Don Corneo lent us\n his bedroom for the night.\n Don't ask what it cost.”",
           "“Today we act. Stay in character the whole\n way through, no matter what. Rolling!”"]

SCENARIO = {   # (user) Elena, Scarlet, Aerith as asked; Ruby, Skye, Tifa "be creative"
    "ruby": "The Detective and the Jewel Thief",
    "skye": "The Lifeguard and the Drowning Swimmer",
    "elena": "The Turks Field Exam",
    "scarlet": "Extra Credit",
    "tifa": "The Secret Technique",
    "aerith": "The Evening Class",
}

INTRO = {
    "ruby": [("C", "Ruby Red. The Corneo diamond went missing\n the night you were seen here. Talk."),
             ("G", "Detective... you've got nothing on me.\n Search me if you like."),
             ("C", "I intend to. Hands where I can see them."),
             ("G", "(She turns, hands on the bedpost.)\nMmm... you're very thorough, detective."),
             ("C", "It's not in your jacket. Or your boots."),
             ("G", "Then I suppose you'll have to look...\n somewhere a little more private.")],
    "skye": [("G", "(She sprawls at the foot of the bed,\n fanning herself.) Help... I'm drowning..."),
             ("C", "Stay calm, miss. I'm a trained lifeguard."),
             ("G", "I swallowed so much water... I think\n I need mouth-to-mouth. Lots of it."),
             ("C", "You're breathing fine. You're talking."),
             ("G", "Then check my heart! Feel how fast it's\n going! (She pulls his hand to her chest.)"),
             ("C", "...Clearly a serious case. Full rescue\n procedure. On the bed, now.")],
    "elena": [("C", "Officer Elena. This is your field exam.\n I'm your supervising agent today."),
              ("G", "Yes, sir! I've studied the whole manual,\n sir! I won't let the Turks down!"),
              ("C", "Section twelve: obedience under pressure.\n Do you follow orders without question?"),
              ("G", "Without question, sir! Any order!"),
              ("C", "Then strip off that jacket and get on\n the bed. Face down."),
              ("G", "Th-that's... is that in the manual?\n ...Yes, sir! Right away, sir!")],
    "scarlet": [("G", "Kyahaha! Sit down, boy. Your grades are\n a disgrace. You're failing my class."),
                ("C", "Please, Professor Scarlet. I need to pass.\n I'll do anything."),
                ("G", "Anything? Mmm. There is... extra credit.\n But it's very hard work."),
                ("C", "I'm a hard worker, Professor."),
                ("G", "We'll see. Lesson one: a good student\n does exactly what his teacher says."),
                ("G", "Now get on that bed and show me you\n deserve an A. Kyahaha!")],
    "tifa": [("G", "So you want to learn Zangan's secret\n technique? Only the best students may."),
             ("C", "I've trained for years, Master Tifa.\n I'm ready."),
             ("G", "Strength isn't enough. It's about control,\n rhythm... and stamina. Lots of stamina."),
             ("C", "Show me, Master."),
             ("G", "(She stretches, slowly.) First, the stance.\n Watch closely. You'll be doing it with me."),
             ("G", "Lesson one starts on the mat. Well...\n the bed. Close enough. Hup!")],
    "aerith": [("G", "Professor? Sorry I'm late for the evening\n class. Am I the only one tonight?"),
               ("C", "Just you, Miss Gainsborough. Your marks in\n anatomy are... lacking."),
               ("G", "I know... I just don't learn well from\n books. I'm more of a hands-on student."),
               ("C", "Then we'll try a practical lesson. Extra\n curricular. Don't tell the dean."),
               ("G", "Hehe, my lips are sealed. Well...\n for now. Where should I sit?"),
               ("C", "Not sit, Miss Gainsborough. Lie down.")],
}

LINES = {
    "ruby": {
        "insert": ["Ah! Detective... that's not where I hid it!", "C:Keep talking. Where's the diamond?",
                   "Oh... you're really searching... deep...", "I'll never talk! ...Ahh, don't stop!",
                   "C:You'll crack. They always crack.", "Faster... maybe I'll remember something...",
                   "Ah! Ah! Okay, okay, I'll confess... more!", "Arrest me... arrest me harder!"],
        "head": ["Mmph... mmmh!", "C:Ready to make a statement?", "(She shakes her head, smirking.) Mmh-mmh!",
                 "C:The right to remain silent. I see.", "Mmf... mmh, mmh...", "(She winks up at you.) Mmmh!",
                 "C:This is a very thorough interrogation.", "Mmph! Mmm...", "(She hums something like 'guilty'.)",
                 "C:I'll take that as a confession.", "Hnn... mmph!", "Mmf... mmmh!"],
        "finisher": ["Fine! I stole it! And I'd do it again!", "Mmm, cuff me to the bed next time...",
                     "Is this how you treat all your suspects?", "Oh, detective... case closed... ah!",
                     "Lock me up and throw away the key!", "Harder! I've been a very bad thief!",
                     "C:You're going away for a long time.", "Ah! I'll do life... with you!"],
    },
    "skye": {
        "insert": ["Ah! That's... not how CPR works!", "C:Rescue procedure, miss. Hold still.",
                   "Oh wow... I'm feeling SO much better!", "Faster, lifeguard! I'm going under!",
                   "C:Breathe. In... and out.", "Ah! Ah! Save me! Save me harder!",
                   "Is this in the lifeguard handbook?!", "Ooh, I'm gonna drown again tomorrow!"],
        "head": ["Mmmph! Mmm-hmm!", "C:Is this helping the water come out?", "(She gives a thumbs up.) Mmf!",
                 "C:Keep your airway clear, miss.", "Gk... mmh! Mmmh!", "(She giggles round you.) Mmf mmf!",
                 "C:Very... brave patient.", "Mmmph! Mmm-hmm!", "(She nods, eyes wide.) Mmh!",
                 "C:Mouth-to-... whatever this is.", "Mmf mmf mmf!", "Hnn... mmph!"],
        "finisher": ["Look! I can swim! I'm swimming!", "Wheee! Bounce, bounce, bounce!",
                     "Best rescue EVER! Five stars!", "C:Miss, please stay in character.",
                     "I am! I'm the happiest drowned girl!", "Ah! Ah! Lifeguard, I'm gonna...!",
                     "Watch me ride the waves!", "Don't let me go under! Don't stop!"],
    },
    "elena": {
        "insert": ["S-sir?! This isn't in the manual, sir!", "C:Obedience under pressure, Officer.",
                   "Y-yes, sir! Taking it like a Turk, sir!", "Ah! Sir... permission to scream, sir?",
                   "C:Permission denied. Hold the position.", "Faster?! Y-yes, sir! I can take it!",
                   "Ah... ah! Mark me... top of the class!", "Don't tell Tseng... don't tell Tseng!"],
        "head": ["Mmph?! Mmm...", "C:Oral examination, Officer.", "(She salutes, eyes watering.) Mmf!",
                 "C:You're doing well. Keep going.", "Mmf... mm-hm...", "(She looks up for approval.) Mmh?",
                 "C:Section thirteen: no hesitation.", "Hnnh... mmph!", "(She nods, very seriously.) Mmmh!",
                 "C:Full marks for enthusiasm.", "Mmph! Mmm...", "Gk... mmh!"],
        "finisher": ["Agent Elena reporting for duty, sir!", "Is this the practical part, sir?!",
                     "Ah! Sir! I've got the hang of it, sir!", "C:Your form is excellent, Officer.",
                     "Promote me, sir... promote me!", "I'll pass this exam if it kills me!",
                     "Ah! Ah! Requesting... backup... sir!", "Exam... complete... sir..."],
    },
    "scarlet": {
        "insert": ["Kyahaha! Take it like a good student!", "C:Is this... on the syllabus, Professor?",
                   "Silence! Teacher knows best, boy.", "Mmm... a B minus. Work harder!",
                   "Faster! You call that effort?!", "C:Yes, Professor! Faster, Professor!",
                   "Ah! Now THAT is a passing grade!", "Kyahaha! Top of the class, darling!"],
        "head": ["Mmm... mmmh!", "C:Am I getting extra credit, Professor?", "(She glares, then purrs.) Mmh-hmm!",
                 "C:I studied very hard for this.", "Hmmph... mmm-hm!", "(Her nails rake your thighs.) Mmf!",
                 "C:Is this the oral exam?", "Mmf... kyahmm!", "(She smirks around you.) Mmmh...",
                 "C:I think I'm passing.", "Mmph! Mmmh!", "Hnnh... mmmh!"],
        "finisher": ["Kyahaha! Class is in session!", "Watch closely, boy. This is advanced!",
                     "C:Professor, I think I'm learning!", "An A! An A plus! Ahh!",
                     "Don't you DARE graduate yet!", "Mmm, I'm keeping you after class!",
                     "Ah! Detention! Every night!", "Kyahaha! You pass, darling... you pass!"],
    },
    "tifa": {
        "insert": ["Hah! Breathe... and push. Good form!", "C:Master, this stance is... intense.",
                   "Control, student! Feel the rhythm!", "Faster! A true fighter doesn't tire!",
                   "C:Yes, Master! Hah! Hah!", "Ah! That's it! You're a natural!",
                   "Now... the final form... full speed!", "Ah! Ahh! You've... mastered it!"],
        "head": ["Mmh... mmph!", "C:Is this a breathing exercise, Master?", "(She nods, very serious.) Mmh!",
                 "C:Your focus is incredible.", "Mmm... mmf...", "(She taps your thigh: 'faster'.)",
                 "C:Zangan never taught me this.", "Hnn... mmmh!", "(She glances up, grinning.) Mmf!",
                 "C:I don't think Zangan knew this.", "Mmph! Mmm...", "Mmh... mmph!"],
        "finisher": ["The secret technique! Watch closely!", "Hah! Hah! Feel the power!",
                     "C:Master... it's beautiful.", "Zangan style... final heaven!",
                     "Don't you dare give up, student!", "Ah! Higher! Higher!",
                     "This is... the ultimate... training!", "Ahh! Class... dismissed!"],
    },
    "aerith": {
        "insert": ["Oh! Professor! Is this... anatomy?", "C:Very advanced anatomy, Miss Gainsborough.",
                   "Hehe... I'm learning so much!", "Ah! Should I be taking notes?",
                   "C:Just concentrate on the lesson.", "Faster? Ooh... okay, Professor!",
                   "Ah! Ah! I think I'm getting it!", "Gold star! I want a gold star!"],
        "head": ["Mmm... hehmm!", "C:Practical examination, Miss Gainsborough.", "(She giggles round you.) Mmf!",
                 "C:You're a fast learner.", "Mmph... mm-hm!", "(She raises a hand, like in class.) Mmh?",
                 "C:Yes, you may continue.", "Mmf... mmmh!", "(She looks very proud.) Mmh!",
                 "C:Full marks, I think.", "Mmph! Mmm...", "Hmmm... mmmh!"],
        "finisher": ["Look, Professor! I'm a hands-on learner!", "Hehe! Is this extra credit?",
                     "C:You've been a very good student.", "Ooh... the Planet's spinning!",
                     "Don't stop the lesson! Not yet!", "Ah! I'll come to every class!",
                     "Teacher's pet! Teacher's pet!", "Ahh! Class... is... dismissed!"],
    },
}

AFTERMATH = {
    "ruby": "Ruby\n(Ruby fishes a glittering diamond out of\n her boot and blows on it.)\n“Case closed, detective.”",
    "skye": "Skye\n(Skye flops back on the bed, beaming.)\n“Saved! My hero! Same time tomorrow?”",
    "elena": "Elena\n(Elena salutes, dazed.)\n“Did I... pass, sir?\n ...Don't tell Tseng. Please.”",
    "scarlet": "Scarlet\n(Scarlet straightens her hair.) “Kyahaha!\n A plus, darling. You may go.”",
    "tifa": "Tifa\n(Tifa bows, breathless.) “You've earned\n your black belt. ...Again tomorrow?”",
    "aerith": "Aerith\n(Aerith giggles, cheeks pink.) “Best lesson\n ever. I'm signing up for the whole year!”",
}

# Insert (user): four stroke lengths, in even steps over its minute
INSERT_FRAMES = (120, 90, 60, 15)          # 4 s, 3 s, 2 s, 0.5 s

"""(user) The Honey Bee Inn shift (689_hb_shift): Tifa works a night at the inn, Cloud is security. Three customers
a shift, one at a time, drawn at random from `CUSTOMERS` (all dressed: user, "keep them dressed"). Each visit:
his opening, three rounds of (Tifa's approach: an ASK, its weight moves his mood, his reply; then a dance with
`PROMPTS` button prompts, a hit +1 mood, a miss -1), then the ending by his type and mood. Mood is the danger
meter (0-10). Types (user): open (respectful, says what he wants: at `GOOD` mood she goes all the way, a short
explicit scene in his `pos`), timid (harder: find what he's really after, his `act` scene at `GOOD`), pushy
(an option marked "X", or mood 0, is the incident: Tifa calls security (Cloud beats him up) or handles it
herself; at `GOOD` he comes round). Funny, experimental, Tifa's personality. Data only; plan docs/hb_shift.md."""

FIELD = "blackbgc"              # a debug room only startmap leads to: replaced by a copy of the inn's room
BASE = "onna_52"
ARRIVE = (-60, -200, 0x40)      # (x, y, dir) MAPJUMP from the manager (the triangle is looked up)
MUSIC = 67                      # AKAO 10 index: BEE (the inn's theme)
GOOD = 8                        # mood for the good ending
PROMPTS = 2                     # prompts per dance
PERIODS = (60, 48, 40)          # frames a prompt, by customer number (the night gets busier)
SHIFT = 3                       # customers a shift
TIP_BONUS = 100                 # gil added by a good ending
DAMAGES = 300                   # gil Cloud "collects for the lamp" after an incident
KEYS = [(0x80, "{PURPLE}[SWITCH]{WHITE}"), (0x40, "{PURPLE}[CANCEL]{WHITE}"), (0x220, "{PURPLE}[OK]{WHITE}")]
HIT_SOUND = 0x1EA               # the materia chime
HIT_FX = 0x76                   # the slap sound: the punches and the kick
DOOR_SOUND = 0x7A

# spots (onna_52; checked on offline renders): the talk on the open floor front-left, the bed along x
TALK_TIFA = (-60, -200)
TALK_GUEST = (-120, -200)
DOOR = (263, 163)
SECURITY_AT = (-160, -180)      # Cloud stops here, behind the customer (away from Tifa)
FOCUS_TALK = (-80, -190)
FOCUS_BED = (100, -200)
# the open endings: 670's relative layout of each position (girl, girl dir, cloud offset, cloud dir, dz), turned
# onto this room's bed (long along x, the pillow at +x: 670's beds run along y, pillow at -y)
POSITIONS = {
    "head": dict(letter="J", girl=(-80, -200), bed=False),
    "cowgirl": dict(letter="B", girl=(130, -204), bed=True),
    "mission": dict(letter="A", girl=(100, -204), bed=True),
}

INTRO = [
    "Tifa\n“Okay. Three customers tonight. Smile,\n dance, read the room. I ran a bar for\n years. How hard can it be?”",
    "Tifa\n“...Cloud's right outside the door if\n anyone gets grabby. Not that I'll\n need him. Probably.”",
]
HOW = ("Pick how Tifa handles each customer,\nthen hit the buttons as she dances.\n"
       "The meter is his mood: fill it up\nand he's hers. Empty it... trouble.")
NEXT = "Tifa\n“Next!”"
SUMMARY = "Tifa\n“That's the shift. Tips tonight:\n {VAR} gil.”"
OUTRO = [
    "Cloud\n“...Busy night.”",
    "Tifa\n“You have no idea. Walk me home?”",
]
# the incident (pushy customers): the ASK after his line; security's scene; her own way
INCIDENT_ASK = "Tifa\n(That's it.)"
INCIDENT_CHOICES = ["Call security.", "Handle it herself."]
CALL = "Tifa\n“CLOUD!”"
SECURITY = [
    "Cloud\n“You touched her.”",
    "Cloud\n“...Wrong move.”",
]
BEATEN = [
    "Cloud\n“He's paying for the lamp.”",
    "Tifa\n“We don't have a lamp in here.”",
    "Cloud\n“We do now.”",
]
HERSELF = "Tifa\n“Hands. Off.”"
LATE = [
    "Cloud\n“I heard a crash. ...Oh.”",
    "Tifa\n“He tripped. Onto my foot. Several\n times.”",
    "Cloud\n“I'll take out the trash. And his\n wallet. For the lamp.”",
]

# Each customer: name, donor (field, model), height (x Cloud's height in the room; default 1; 689 rescales every
# customer to it: user, Hobbs and the Lackey were too big), type, start mood, rate (gil a mood point at the end), lines.
# rounds: (prompt text, [(option, weight, reply)]); a weight "X" = the incident (pushy only).
CUSTOMERS = [
    # ---- open ----------------------------------------------------------------------------------------------
    dict(key="dio", name="Dio", donor=("jet", 4), height=1.11, type="open", mood=5, rate=40, pos="head",
         intro=["Dio\n“Shh! I'm not here. Officially I'm\n judging a chocobo race in Junon.”",
                "Dio\n“Unofficially I want the best service\n in Midgar, and I always say exactly\n what I want. Ha ha HA!”"],
         rounds=[
             ("Dio\n“First: dazzle me! Something with\n SHOWMANSHIP!”",
              [("Strike a pose like a champion.", 2, "Dio\n“MAGNIFICENT! The stance! The\n pecs-equivalent! I love it!”"),
               ("Ask what showmanship means.", 0, "Dio\n“It means more, and LOUDER. Watch\n and learn, my dear!”"),
               ("Tell him to keep his voice down.", -1, "Dio\n“My voice has never been down in\n its life.”")]),
             ("Dio\n“You have a fine pair of... legs!\n Did you train them? You must have!”",
              [("Tell him about Zangan-style.", 2, "Dio\n“A martial artist! Like ME! We\n should exhibit together!”"),
               ("Say they're from carrying kegs.", 1, "Dio\n“Honest labour! The best muscle!”"),
               ("Change the subject.", -1, "Dio\n“...Fine. But they ARE fine legs.”")]),
             ("Dio\n“Now. I'll be frank, as a man of\n business: I want your mouth. Price\n is no object. Yes or no?”",
              [("“Since you asked so nicely.”", 2, "Dio\n“A YES! Write it down! Frame it!”"),
               ("“Say please.”", 1, "Dio\n“PLEASE! I'll say it in lights!”"),
               ("“Let's see how the dance goes.”", 0, "Dio\n“A negotiator! I respect that.”")])],
         good=["Tifa\n“Sit back, big man. And for once in\n your life... be quiet.”",
               "Dio\n“Mmh! Ohh... oh-HO-ho... THIS is\n the main event...”",
               "Tifa\n“Mm-hm. Mmmf.”",
               "Dio\n“Ahh... AHHH! ...I'm buying the inn.\n I'm buying the STREET.”",
               "Tifa\n“*cough* You're buying a drink, and\n leaving a very big tip.”"],
         meh="Dio\n“Entertaining! Not legendary. Here.\n For the effort.”",
         bad="Dio\n“I've seen better shows at the\n Chocobo Square! Good day!”"),
    # (user: "don't use Bruno for honeybee, replace him with someone else") Rico, a Costa del Sol beach bum
    dict(key="rico", name="Rico", donor=("del2", 8), type="open", mood=5, rate=35, pos="cowgirl",
         intro=["Rico\n“Heyyy. Rico. Costa del Sol. First\n time in Midgar. Is the sky always\n this... ceiling?”",
                "Rico\n“Back home I just lie on the sand and\n let the waves do everything. Tonight\n I'd like you to be the waves.”"],
         rounds=[
             ("Rico\n“You've got a beach face. You ever\n surfed?”",
              [("“I'd stand on the board first try.”", 2, "Rico\n“...Marry me. Kidding. Mostly.”"),
               ("“Sand gets everywhere.”", -1, "Rico\n“That's the BEST part, though.”"),
               ("“Teach me sometime.”", 1, "Rico\n“Lesson one: lie down. Lesson two:\n lie down more.”")]),
             ("Rico\n“I brought you a shell. It's a real\n one. From the actual sea.”",
              [("Hold it to your ear.", 2, "Rico\n“You hear it? That's home.”"),
               ("“It smells like fish.”", -1, "Rico\n“...That's also home.”"),
               ("“Thank you, Rico.”", 1, "Rico\n“Aw. Nobody says my name like that.”")]),
             ("Rico\n“So, uh. Could you be on top? I'll\n just float. I'm a really good\n floater.”",
              [("“Lie back. Catch the wave.”", 2, "Rico\n“Riding it, babe.”"),
               ("“I'll make you seasick.”", 1, "Rico\n“Worth it.”"),
               ("“Maybe. Earn it.”", 0, "Rico\n“I'll paddle out for it.”")])],
         good=["Tifa\n“On your back, surfer. Hands on my\n hips. Let the tide come in.”",
               "Rico\n“Whoa... whoa, here comes a big one...”",
               "Tifa\n“Mm... ahh... you're not so bad\n yourself.”",
               "Rico\n“Wipe-OUT! ...Again! Paddle back\n out!”",
               "Tifa\n“Surf's up, Rico. Time to go home.”"],
         meh="Rico\n“Nice swell. I'll come back next\n season.”",
         bad="Rico\n“Bummer. You've got no beach in\n you.”"),
    dict(key="pete", name="Pete", donor=("blackbg2", 9), type="open", mood=6, rate=30, pos="mission",
         intro=["Pete\n“Evening, ma'am. Pete. Back from\n three months on a cargo ship.”",
                "Pete\n“I'll be honest: I just want to lie\n down with a nice girl in a bed that\n doesn't rock. Is that alright?”"],
         rounds=[
             ("Pete\n“Sorry, I'm still swaying a bit.\n Sea legs.”",
              [("Steady him by the arm.", 2, "Pete\n“Thank you. You've got a grip like\n an anchor.”"),
               ("Sway along with him.", 1, "Pete\n“Ha! Now we're both at sea.”"),
               ("Make a seasick joke.", -1, "Pete\n“...Please don't say 'seasick'.”")]),
             ("Pete\n“Could you just... talk to me? Three\n months of sailors. They only talk\n about knots.”",
              [("Tell him about Nibelheim.", 2, "Pete\n“Mountains. I've never seen a\n mountain up close. Tell me more.”"),
               ("Ask about knots.", -1, "Pete\n“...Bowline. Sheet bend. ...Please\n no.”"),
               ("Ask what he missed most.", 1, "Pete\n“Pie. And this. Talking.”")]),
             ("Pete\n“Would you lie with me? Nothing\n fancy. I just want to look at you.”",
              [("“Come here, sailor.”", 2, "Pete\n“...Aye.”"),
               ("“Nothing fancy? Hm.”", 1, "Pete\n“Fancy's fine too!”"),
               ("“Let's dance first.”", 0, "Pete\n“I'll try not to fall over.”")])],
         good=["Tifa\n“Lie back with me. No ship, no\n storm. Just a bed that stays put.”",
               "Pete\n“Ah... you're warm... I forgot what\n warm was...”",
               "Tifa\n“Mmh... slow, sailor... like that...\n ahh...”",
               "Pete\n“I'm never going back to sea.”",
               "Tifa\n“You are. But you'll come back.”"],
         meh="Pete\n“That was nice. Thanks for the talk.”",
         bad="Pete\n“I think I'd rather be on the boat.”"),
    # ---- timid ---------------------------------------------------------------------------------------------
    dict(key="hobbs", name="Private Hobbs", donor=("blin66_6", 6), type="timid", mood=3, rate=25, act="praise",
         intro=["Hobbs\n“H-hello! Private Hobbs, Shinra\n infantry, I mean, um. Hi.”",
                "Hobbs\n“I don't know what I want. My squad\n paid for this. As a joke. Sorry.”"],
         rounds=[
             ("Hobbs\n“...Do I have to take my helmet off?”",
              [("“Not if you don't want to.”", 2, "Hobbs\n“Oh thank goodness.”"),
               ("Take it off for him.", -2, "Hobbs\n“AH! My hair! Nobody sees my hair!”"),
               ("“Do you sleep in it?”", 0, "Hobbs\n“...Sometimes.”")]),
             ("Hobbs\n“Sorry. I mopped the reactor today.\n Nobody said thanks. Nobody ever\n says anything.”",
              [("“That sounds lonely.”", 1, "Hobbs\n“It IS lonely! Sorry. It is.”"),
               ("“Was it a really clean reactor?”", 2, "Hobbs\n“It SPARKLED. You could eat off it.\n Not that you should. Mako.”"),
               ("Start dancing.", -1, "Hobbs\n“Oh. Okay. Dancing. Yes. Great.”")]),
             ("Hobbs\n“...I just wish somebody would say\n I did a good job. Once.”",
              [("Salute him.", 2, "Hobbs\n“Y-you saluted me!”"),
               ("Kiss his helmet.", 1, "Hobbs\n“My helmet's never been kissed.”"),
               ("“Is that what you want?”", -1, "Hobbs\n“No! I mean. Maybe. Forget it.”")])],
         good=["Tifa\n“Private Hobbs. Stand up straight.”",
               "Tifa\n“You did a good job today. That\n reactor sparkled because of you.\n Shinra doesn't deserve you.”",
               "Hobbs\n“...I...”",
               "Hobbs\n“*sob* That's the nicest thing\n anyone's ever said to me. Can I\n come back next week? For the talk?”",
               "Tifa\n“Same time. Bring your mop.”"],
         meh="Hobbs\n“Thanks. Sorry. Thanks.”",
         bad="Hobbs\n“I'll just... go. Sorry.”"),
    dict(key="gus", name="Gus", donor=("rcktin2", 5), type="timid", mood=3, rate=25, act="listen",
         intro=["Gus\n“...Hi. Gus. Rocket Town. Engine\n crew. Second shift. Sorry, I'm\n greasy.”",
                "Gus\n“I don't really... I'm not good at\n this. Talking to girls. Talking.”"],
         rounds=[
             ("Gus\n“(He's twisting a spanner in his\n hands.)”",
              [("Ask what the spanner's for.", 2, "Gus\n“It's a 14 mil! For the fuel pump!\n ...Sorry. You didn't ask that.”"),
               ("Take the spanner away.", -1, "Gus\n“...I need that. Emotionally.”"),
               ("Sit close to him.", 0, "Gus\n“(He turns bright red.)”")]),
             ("Gus\n“Nobody lets me talk about the fuel\n pump. The captain says 'shut up\n about the fuel pump, Gus.'”",
              [("“Tell me about the fuel pump.”", 2, "Gus\n“...Really?! Okay! Okay okay okay.”"),
               ("“What's a fuel pump?”", 1, "Gus\n“It's the HEART of the ROCKET.”"),
               ("“The captain sounds right.”", -2, "Gus\n“...Oh.”")]),
             ("Gus\n“...So the turbine runs at forty\n thousand RPM and... are you still\n listening?”",
              [("Ask about the turbine blades.", 2, "Gus\n“The BLADES! You asked about the\n BLADES!”"),
               ("Nod a lot.", 0, "Gus\n“You're nodding. That's good. Right?”"),
               ("Yawn.", -2, "Gus\n“...You yawned.”")])],
         good=["Tifa\n“So the pump feeds the turbine and\n the turbine spins the... wait, back\n up. Draw it for me.”",
               "Gus\n“(Gus draws a diagram on a napkin.\n Then a second napkin. Then the\n tablecloth.)”",
               "Tifa\n“And the pressure valve? What stops\n it all from exploding?”",
               "Gus\n“...That's the best question anyone's\n ever asked me. I think this was the\n best night of my life.”",
               "Tifa\n“You didn't even take your boots\n off.”"],
         meh="Gus\n“Thanks for... yeah. Thanks.”",
         bad="Gus\n“I'll go talk to the rocket.”"),
    dict(key="nabe", name="Professor Nabe", donor=("cos_btm", 8), type="timid", mood=3, rate=30, act="kata",
         intro=["Nabe\n“Ah. Er. Good evening. Professor\n Nabe, Cosmo Canyon, comparative\n... um. Things.”",
                "Nabe\n“I'm here for research! Purely. I\n have a notebook. See?”"],
         rounds=[
             ("Nabe\n“What... er... what does one do,\n here, normally?”",
              [("“Whatever you want to.”", 0, "Nabe\n“That's terrifyingly open-ended.”"),
               ("“What's the research?”", 2, "Nabe\n“Movement! The body as a... a\n vessel. For research.”"),
               ("Sit on his lap.", -2, "Nabe\n“AH. The notebook! Mind the\n notebook!”")]),
             ("Nabe\n“You... move very precisely. Do you\n... study something?”",
              [("“Zangan-style. Martial arts.”", 2, "Nabe\n“ZANGAN?! I've read about the\n school! I've never SEEN it!”"),
               ("“I used to dance.”", 0, "Nabe\n“Fascinating. Hm. No. Hm.”"),
               ("“I study you.”", -1, "Nabe\n“(He drops his pencil.)”")]),
             ("Nabe\n“Would it be... very improper to ask\n you to... show me? The forms?”",
              [("“A kata? Sure.”", 2, "Nabe\n“(He opens the notebook to a\n fresh page.)”"),
               ("“Only if you join in.”", 1, "Nabe\n“Oh, I couldn't. ...Could I?”"),
               ("“That's not what this place is.”", -2, "Nabe\n“Of course. Sorry. Of course.”")])],
         good=["Tifa\n“Stand back. Zangan-style, first\n form. Watch the hips, not the\n feet.”",
               "Nabe\n“(He is writing faster than any man\n has written.)”",
               "Tifa\n“And... HAH!”",
               "Nabe\n“Remarkable. The economy of motion!\n The... I need to lie down. This will\n be a whole chapter.”",
               "Tifa\n“Spell my name right in the credits.”"],
         meh="Nabe\n“Er. Thank you. Most... educational.”",
         bad="Nabe\n“I'll consult the literature.”"),
    # ---- pushy ---------------------------------------------------------------------------------------------
    dict(key="spike", name="Spike", donor=("jail2", 6), type="pushy", mood=4, rate=20,
         intro=["Spike\n“Yo! Finally, the good stuff! Get\n over here, sweetheart.”",
                "Spike\n“I paid. So you do what I say. That's\n how this works, right?”"],
         rounds=[
             ("Spike\n“C'mon, sit on my lap. NOW.”",
              [("“Ask nicely.”", 2, "Spike\n“...Huh. Okay. Can you... sit\n here. Please. Or whatever.”"),
               ("“There's a dance first.”", 0, "Spike\n“Ugh. FINE. Dance.”"),
               ("Sit on his lap.", -2, "Spike\n“HA! See? Easy.”")]),
             ("Spike\n“Ya know, I'm pretty tough. I've\n been in Corel Prison. Twice.”",
              [("“I've been in Corel Prison too.”", 2, "Spike\n“...For real? What for?”"),
               ("“Impressive.”", -1, "Spike\n“Yeah it is!”"),
               ("“Twice? Not good at escaping?”", 1, "Spike\n“HEY. ...Okay that's fair.”")]),
             ("Spike\n“(He reaches for her top.) Let's\n skip the talking.”",
              [("Grab his wrist.", 2, "Spike\n“OW OW OW. Okay! Okay! Talking!”"),
               ("Laugh it off.", "X", ""),
               ("Let him.", "X", "")])],
         grab="Spike\n“Hands off? Nah. I PAID. (He grabs\n her, hard.)”",
         good=["Spike\n“...So. You're kinda scary. I like\n that.”",
               "Tifa\n“I'm kinda scary. Remember that next\n time you want to grab someone.”",
               "Spike\n“Yes ma'am. Here. Tip. All of it.\n Don't tell the guys.”"],
         meh="Spike\n“Whatever. This place sucks.”",
         bad="Spike\n“Nobody tells ME no.”"),
    dict(key="lackey", name="Lackey", donor=("colne_4", 8), type="pushy", mood=4, rate=25,
         intro=["Lackey\n“Hey hey! You know who I work for?\n Don Corneo! The Don!”",
                "Lackey\n“So you treat me like a VIP, got it?\n The Don's gonna hear about this.”"],
         rounds=[
             ("Lackey\n“The Don always gets the best girl.\n So now I do. That's logic.”",
              [("“Where IS the Don these days?”", 2, "Lackey\n“...Nobody knows. He just... left.\n Didn't even say goodbye.”"),
               ("“You're right, VIP.”", -1, "Lackey\n“Darn right I'm right!”"),
               ("“I met the Don once.”", 1, "Lackey\n“You did?! Was he... was he happy?”")]),
             ("Lackey\n“(He leans in close.) The Don\n always started with a little kiss.”",
              [("Turn away.", 1, "Lackey\n“Hey! ...Fine.”"),
               ("Kiss his forehead.", 2, "Lackey\n“...Oh. That's nice. That's what my\n mom did.”"),
               ("Kiss him properly.", "X", "")]),
             ("Lackey\n“...It's been real quiet at the\n mansion. Real quiet.”",
              [("“You miss him.”", 2, "Lackey\n“I MISS HIM. *sniff* He was a\n terrible boss. I miss him.”"),
               ("“Get a new boss.”", 0, "Lackey\n“Who's hiring lackeys these days?”"),
               ("“Good riddance.”", "X", "")])],
         grab="Lackey\n“HEY! Nobody talks about the Don\n like that! (He shoves her.)”",
         good=["Lackey\n“...Thanks for listening. Nobody\n listens to lackeys.”",
               "Tifa\n“You're not a lackey. You're a guy\n who's between bosses.”",
               "Lackey\n“Between bosses. I like that. Here,\n this is from the Don's piggy bank.\n He'd want you to have it.”"],
         meh="Lackey\n“The Don would've tipped more. I\n won't.”",
         bad="Lackey\n“You'll be hearing from... someone!”"),
    dict(key="dunmore", name="Mr. Dunmore", donor=("blackbg1", 3), type="pushy", mood=4, rate=30,
         intro=["Dunmore\n“Dunmore, Shinra, Accounts. This is\n on the company card, so I expect\n value for money.”",
                "Dunmore\n“I don't do small talk. I do\n results. Let's begin.”"],
         rounds=[
             ("Dunmore\n“Is this the best room? I'll be\n filing a report.”",
              [("“It's the only room.”", 1, "Dunmore\n“...Efficient. Hm.”"),
               ("“Let me get you a better one.”", -1, "Dunmore\n“That's more like it.”"),
               ("“File it, then.”", 2, "Dunmore\n“...Nobody talks to me like that.\n Interesting.”")]),
             ("Dunmore\n“I want you on your knees. That's an\n instruction.”",
              [("“I'm not your intern.”", 2, "Dunmore\n“...No. No, you are not.”"),
               ("Kneel.", "X", ""),
               ("“Say please, Accounts.”", 1, "Dunmore\n“...Please. That was hard to say.”")]),
             ("Dunmore\n“...Do you know what it's like to\n be in charge ALL day?”",
              [("“Want to not be, for once?”", 2, "Dunmore\n“...Yes. God, yes.”"),
               ("“Must be nice.”", -1, "Dunmore\n“It's NOT.”"),
               ("“I run a bar. I know.”", 1, "Dunmore\n“Then you understand.”")])],
         grab="Dunmore\n“I said kneel. (He pushes her down by\n the shoulder.)”",
         good=["Tifa\n“Sit down. Shoes off. Tie off. Don't\n make a single decision for the next\n ten minutes.”",
               "Dunmore\n“...This is the best money Shinra\n has ever spent.”",
               "Tifa\n“Expense it as 'training'.”"],
         meh="Dunmore\n“Adequate. Three stars.”",
         bad="Dunmore\n“You'll never work in this town\n again. ...You don't work for me.\n Hm.”"),
]

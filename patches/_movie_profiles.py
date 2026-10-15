"""(user) Personality profiles of the movie minigame's six co-stars: the reference for every line
they say and for how each reacts in the shoots' character-driven moments (the group's arguments,
the hold, the slap prompts). Data only; write new lines for a girl against her profile.

Fields: `role` (one-line archetype), `drive` (what she wants in a scene), `profile` (the user's
text), `weakness`, `style` (how she talks), and `hold` = how she takes the Square hold:
  "likes"    plays along, the hold pays (`gain` x the shoot's gil a press)
  "dislikes" taps out at once and says why; costs `loss` x gil a press
  "mood"     either, at random (`odds` = chance in 256 of "likes")
  "rules"    dislikes it until she has agreed the rules in this shoot (an argument's outcome), then likes
  "control"  likes it the first time in a shoot, dislikes it after (she wants to set the pace)
(User, since: confirmed.) Read by 670 / 672 (`_hold_check`, `_refuse_block`).
`refuse`: her lines when she taps out of a hold (two, at random; the gil lost is added below
them); `leave`: her line when she's had enough (`LEAVE_AT` annoyances in one shoot: each refused
hold, a bad choice in a group argument) and walks off the set (one-girl shoot: it ends as a CUT;
group: she's gone for the rest of it). `uneasy` (group): she isn't comfortable with what she's
doing at all: extra stops (670 `_group`: `_movie_group.UNEASY`).

(User, since) `there` = how she takes the special shoots' "there" prompt (672: Square in parts one and
three, two prompts a part: Cloud tries to stick it in the back door), the same kinds as `hold` plus
"second" (no the first time, yes the second, `there_push` from the third: Scarlet); `rules` here = only
with "Backdoor is wide-open." (RULES 2); `there_yes` / `there_no` her reactions (paid `there_gain`,
default 10, / costing `there_loss` x gil a press; a refusal annoys her as a refused hold does)."""

# (user, since) the "lesson" (670 `_lesson_ops`): after she stops, breaks free of a hold or refuses
# one, Square in the prompt = Cloud's slap; `lesson` = "likes" / "dislikes" / "mood" (RANDOM < lesson_odds) /
# "rules" (Elena: fine unless "No funny stuff", RULES 0); `lesson_yes` / `lesson_no` her line (one each:
# the group's texts); a "no" is a strike (+1 annoyance, LEAVE_AT)
LEAVE_AT = 2                                        # (user) e.g. two refused holds and she's gone

PROFILES = {
    "ruby": dict(
        role="The competitor", drive="Challenges others",
        profile="Treats everything as a contest. She compares performances, makes confident predictions, "
                "and dislikes being overshadowed.",
        weakness="She can become so focused on winning that she forgets to enjoy herself.",
        style="Short, confident, teasing; rarely admits uncertainty.",
        hold="likes", gain=10,
        refuse=["(She pulls off and smirks.)\n“Nice try. I decide when I'm beaten.”",
                "(She slips free.)\n“Not now. I'm winning.”"],
        leave="(She grabs her robe.)\n“Forget it. Call me when you want a winner.”",
        lesson="mood", lesson_odds=128,
        lesson_yes="(She looks back, eyes blazing.)\n“Ha! Is that all you've got? Again!”",
        lesson_no="(She whirls round.)\n“Hit me again and you'll be the loser\n here, hotshot.”",
        there="mood", there_odds=192, there_loss=5,           # (user: Ruby and Skye swapped: Skye's hold reaction)
        there_yes=["(She glances back and smirks.)\n“The back door? Bold. ...Fine. I can take\n anything you've got.”",
                   "(She arches back into it.)\n“Going in the back? Watch me not flinch.”"],
        there_no=["(She twists away.)\n“Not the back door today, hotshot.\n Earn it first.”",
                  "(She swats his hand off her hip.)\n“Nice try sneaking round the back. No.”"]),
    "skye": dict(
        role="The enthusiastic wildcard", drive="Embraces novelty",
        profile="Reacts impulsively, gets carried away, interrupts herself, and sometimes changes her mind "
                "halfway through a sentence. Her enthusiasm is genuine.",
        weakness="She doesn't always think things through.",
        style="Quick, excitable, exaggerated; occasional unexpected sincerity.",
        hold="mood", odds=192, gain=10, loss=5,          # (changes her mind: 1 in 4 she taps out)
        refuse=["(She wriggles free, laughing.)\n“Wait wait wait... nope! Changed my mind!”",
                "(She pops off.)\n“Okay that was... no. Nope. Sorry!”"],
        leave="(She hops off the bed.)\n“Okay, this stopped being fun. Bye!”",
        lesson="likes", lesson_yes="(She yelps, then giggles.)\n“Ow! Ohmygosh. Do that again!”",
        there="likes",                                    # (user: always; Ruby's hold reaction)
        there_yes=["(She squeals.)\n“Ooh, the back door?! YES. Wait... yes!\n Yes yes yes!”",
                   "(She wiggles her hips back at him.)\n“Round the back? Ohmygosh, do it!”"]),
    "elena": dict(
        role="The cautious professional", drive="Sets limits",
        profile="Wants to understand what's happening before participating. She might attempt to establish "
                "rules, ask practical questions, or withdraw when a situation becomes uncomfortable.",
        weakness="Her pride means she hates admitting that she's nervous.",
        style="Measured, formal, self-correcting; nervousness leaks through her professional vocabulary.",
        hold="rules", gain=10, loss=10, uneasy=True,
        refuse=["(She pulls back sharply.)\n“That was not part of the agreed... No.\n Don't do that.”",
                "(She pushes his hand away.)\n“I need to know what's happening first.”"],
        leave="(She stands, arms folded.)\n“I'm withdrawing. Professionally.\n ...I'm done.”",
        lesson="rules",
        lesson_yes="(She flinches, then nods.)\n“...Within the agreed rules. Noted.\n Understood, sir.”",
        lesson_no="(She glares.)\n“No funny stuff. We AGREED.\n That was funny stuff.”",
        there="rules",                                   # only with "Backdoor is wide-open." agreed
        there_yes=["(She takes a breath.)\n“The back door... as agreed. Proceed.\n Carefully.”",
                   "(She nods, flushed.)\n“That's... within the agreed parameters.”"],
        there_no=["(She jerks away.)\n“That is NOT the agreed point of entry!”",
                  "(She grabs his wrist.)\n“The back door was explicitly off the\n table.”"]),
    "scarlet": dict(
        role="The controlling showwoman", drive="Seeks control",
        profile="Wants to direct the event, control the pace, and decide how everyone else should behave. "
                "She can be theatrical and provocative.",
        weakness="An unexpected refusal or someone else's confidence can puncture her composure.",
        style="Polished commands, theatrical laughter, cutting remarks, occasional flashes of irritation.",
        hold="control", gain=15, loss=10,
        refuse=["(She shoves his hand off her head.)\n“Darling. I set the pace. Not you.”",
                "(She pulls free, eyes flashing.)\n“Once was a gift. Don't push your luck.”"],
        leave="(She sweeps off the set.)\n“Kyahaha... no. You've lost your leading lady.”",
        lesson="likes", lesson_yes="(She purrs.)\n“Kyahaha! Finally, some spine.\n Again, darling.”",
        there="second",                                  # (user) no the first time, yes the second, 3rd on: pushing it
        there_no=["(She slaps his hand away.)\n“The back door? Without asking? How\n presumptuous, darling.”"],
        there_yes=["(A slow, wicked smile.)\n“The back door again... persistent.\n Fine, darling. Impress me.”"],
        there_push=["(She whirls on him.)\n“Again? I let you in the back ONCE,\n darling. Don't push your luck.”"]),
    "tifa": dict(
        role="The mediator", drive="Keeps things grounded",
        profile="Notices when someone is uncomfortable and tries to keep the group from getting carried away. "
                "She can be competitive too, but she is more likely to question whether the situation is fair "
                "or whether everyone is comfortable.",
        weakness="",
        style="Conversational, warm, direct; humour often softens a serious observation.",
        hold="dislikes", loss=5, uneasy=True,
        refuse=["(She pulls back and holds up a hand.)\n“Hey. Not like that, okay?”",
                "(She eases off, firm.)\n“Cloud. Ask first. Seriously.”"],
        leave="(She gets up, quietly.)\n“I'm sitting the rest out. You know why.”",
        lesson="dislikes", lesson_no="(She catches his wrist.)\n“Hey. No. We don't do that.”",
        there="mood", there_odds=128, there_loss=5,         # (user) 50/50, her mood
        there_yes=["(She laughs, surprised.)\n“The back? ...You know what? Okay.\n Go slow.”",
                   "(She glances back, blushing.)\n“Round the back, huh? ...Alright. Gentle.”"],
        there_no=["(She shifts away.)\n“Whoa, not back there. Not today.”",
                  "(She puts a hand back.)\n“Cloud. Wrong door. Ask me first.”"]),
    "aerith": dict(
        role="The playful instigator", drive="Changes the mood",
        profile="Uses humour and apparently innocent questions to expose tensions in the group. She might tease "
                "Scarlet's need for control or notice Elena's nerves before anyone else does.",
        weakness="",
        style="Light, perceptive, mischievous; occasionally disarmingly direct. Her playfulness doesn't mean "
              "she automatically agrees to everything.",
        hold="mood", odds=128, gain=10, loss=5,
        refuse=["(She slips free with a giggle.)\n“Ah-ah! You'll have to catch me first.”",
                "(She pulls back, smiling, but means it.)\n“Nope. Not today, mister.”"],
        leave="(She waves from the door.)\n“That's my cue! Have fun without me!”",
        lesson="dislikes", lesson_no="(She pouts and rubs the spot.)\n“Ow! Meanie. That's not how you\n treat a lady.”",
        there="dislikes", there_loss=5,                   # (user) never, and she mocks the try
        there_no=["(She giggles and wriggles away.)\n“Wrong door, mister! Did you get lost\n back there? Need a map?”",
                  "(She glances back, grinning.)\n“Sneaking in the back? Ooh, so daring.\n ...No. The front's that way!”"]),
}

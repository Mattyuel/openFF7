"""(user) Personality profiles of the movie minigame's six co-stars: the reference for every line
they say and for how each reacts in the shoots' character-driven moments (the group's arguments,
the hold, the slap prompts). Data only; write new lines for a girl against her profile.

Fields: `role` (one-line archetype), `drive` (what she wants in a scene), `profile` (the user's
text), `weakness`, `style` (how she talks), and `hold` = how she takes the Square hold:
  "likes"    plays along, the hold pays (`gain` x the shoot's gil a press)
  "dislikes" taps out at once, says why, an onlooker reacts; costs `loss` x gil a press
  "mood"     either, at random (`odds` = chance in 256 of "likes")
  "rules"    dislikes it until she has agreed the rules in this shoot (an argument's outcome), then likes
  "control"  likes it the first time in a shoot, dislikes it after (she wants to set the pace)
(The hold values are proposals from these profiles, to be confirmed by the user; nothing reads
this module yet.)"""

PROFILES = {
    "ruby": dict(
        role="The competitor", drive="Challenges others",
        profile="Treats everything as a contest. She compares performances, makes confident predictions, "
                "and dislikes being overshadowed.",
        weakness="She can become so focused on winning that she forgets to enjoy herself.",
        style="Short, confident, teasing; rarely admits uncertainty.",
        hold="likes", gain=10),
    "skye": dict(
        role="The enthusiastic wildcard", drive="Embraces novelty",
        profile="Reacts impulsively, gets carried away, interrupts herself, and sometimes changes her mind "
                "halfway through a sentence. Her enthusiasm is genuine.",
        weakness="She doesn't always think things through.",
        style="Quick, excitable, exaggerated; occasional unexpected sincerity.",
        hold="mood", odds=192, gain=10, loss=5),          # (changes her mind: 1 in 4 she taps out)
    "elena": dict(
        role="The cautious professional", drive="Sets limits",
        profile="Wants to understand what's happening before participating. She might attempt to establish "
                "rules, ask practical questions, or withdraw when a situation becomes uncomfortable.",
        weakness="Her pride means she hates admitting that she's nervous.",
        style="Measured, formal, self-correcting; nervousness leaks through her professional vocabulary.",
        hold="rules", gain=10, loss=10),
    "scarlet": dict(
        role="The controlling showwoman", drive="Seeks control",
        profile="Wants to direct the event, control the pace, and decide how everyone else should behave. "
                "She can be theatrical and provocative.",
        weakness="An unexpected refusal or someone else's confidence can puncture her composure.",
        style="Polished commands, theatrical laughter, cutting remarks, occasional flashes of irritation.",
        hold="control", gain=15, loss=10),
    "tifa": dict(
        role="The mediator", drive="Keeps things grounded",
        profile="Notices when someone is uncomfortable and tries to keep the group from getting carried away. "
                "She can be competitive too, but she is more likely to question whether the situation is fair "
                "or whether everyone is comfortable.",
        weakness="",
        style="Conversational, warm, direct; humour often softens a serious observation.",
        hold="dislikes", loss=5),
    "aerith": dict(
        role="The playful instigator", drive="Changes the mood",
        profile="Uses humour and apparently innocent questions to expose tensions in the group. She might tease "
                "Scarlet's need for control or notice Elena's nerves before anyone else does.",
        weakness="",
        style="Light, perceptive, mischievous; occasionally disarmingly direct. Her playfulness doesn't mean "
              "she automatically agrees to everything.",
        hold="mood", odds=128, gain=10, loss=5),
}

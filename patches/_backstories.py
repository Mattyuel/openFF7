"""(user) The four date girls' hidden histories: their traumas, what they want, and what doesn't
work for them in bed. Glimpsed in small moments across the dates, their intimate scenes and the movie,
then told in full in the revelation on a final date (`_dates_reveal`). Write every new line for them
against this and `_movie_profiles`.

Rule for Tifa's history: what happened to her as a child is never shown or described. It comes up
only in her own words as an adult, in the revelation, which is not an intimate scene. Her intimate
scenes show only how it affects her now (her neck, needing to see his face, going far away).

BIBLE (for writing; not shown in-game as such)

Tifa: when she and her best friend Mina were nine, a man who worked up at the Shinra mansion hurt
  them both, one summer. Mina told her mother; nobody believed her, and her family left Nibelheim
  that winter. Tifa watched what telling did to Mina and said nothing, to anyone, ever. Her mother
  died the next year. Cloud, who followed her up Mt. Nibel, never knew any of it.
  Now: she learned to fight so no one could hold her down again; she sleeps facing the door; she
  can't bear a hand on the back of her neck or being held from behind without warning. She takes care
  of everyone because a room where everyone's happy is a room where nothing happens to her. In bed she
  performs: she tends to her partner, and she has faked every climax she's ever had with anyone,
  floating "up by the ceiling" and watching. She wants to choose, slowly, with eyes open, and one day
  actually feel it instead of watching it. The camera was a role, so she was safe in it, and that
  frightened her more than anything.

Aerith: raised in Hojo's lab until she was seven: gloved hands, measurements, the glass, everything
  she did written down. Her mother died getting her out. Elmyra raised her to be good, and she has
  been, outwardly. The Planet's voices never stop; the one time they go silent is at the peak of
  pleasure, and she's chased that silence, with people she didn't love, and felt she was using them.
  Now: she goes cold under careful, reverent, clinical touch, being studied or handled ("don't handle
  me like a sample"), and gloves. What she wants is to lead, to laugh, to make a man lose control, to
  be wanted rather than examined. On set the camera wanted her; for the first time being watched was
  hers. The flower girl has a hungry, dominant streak, and she isn't sorry about it.

Scarlet: grew up in a Sector 6 tenement, the child nobody looked at; she hid in a wardrobe on the
  nights her mother brought men home, and learned she could vanish. At nineteen, a Shinra executive
  "promoted" the quiet, pretty secretary and cornered her when no one was watching. She learned the
  only safe place is the centre of every room: loud, bright, untouchable, in charge.
  Now: she has never once climaxed in private. She needs an audience, a mirror, a camera, the
  lights on; in the dark and the quiet she shuts down, sometimes panics. She has never stayed until
  morning with anyone. Domination is armour: she's the one who handles, never the one handled. What
  she wants, and what terrifies her, is to be seen with no show on, and not disappear.

Elena: grew up in her elder sister's shadow and followed her into the Turks, where she learned to
  say "yes, sir" to everything. A senior Turk (never in any report) expected her to date him, so she
  did, and said yes to all of it. It hurt, every time, and she said nothing, because complaining isn't
  professional. She has never climaxed with anyone; her body locks up when she doesn't know what's
  coming. She has never been asked what she wants, so she doesn't know.
  Now: rules, plans and permission are how she lets go. Her own rules on set were the first time she
  said no and it was simply respected, and then, for the first time, the wanting was hers.
"""

# Hints: extra pages appended to existing lines (no new text ids). Each page carries its speaker.
# tier1 / tier2 = after the first / second date's closing line; part2[place] = after her last line
# in that place's intimate scene (660 `_dates_data` part2); aftermath = after her movie aftermath (670).
SEEDS = {
    "Tifa": dict(
        tier1=["{TIFA}\n(A laugh bursts out right behind her.\n She spins, fist already raised, then\n catches herself. “...Sorry. Habit.”)"],
        tier2=["{TIFA}\n“Do you remember Mina? Black braids,\n lived behind the inn?” (Her smile\n slips, just for a second.)",
               "{TIFA}\n“Her family left the winter we were\n nine. I never wrote to her. I should\n have.” ...She changes the subject."],
        part2={"capsule": ["{TIFA}\n(Your hand brushes the back of her\n neck. Her whole body goes rigid.)",
                           "{TIFA}\n“Not... not my neck. Hips. Just keep\n your hands on my hips. ...Please.”"],
               "gondola": ["{TIFA}\n(Her eyes have drifted somewhere far\n away. When you say her name, she\n comes back with a start and smiles.)"],
               "cannon": ["{TIFA}\n(For a moment her cries sound like\n lines she's said before. Then she\n meets your eyes, and they change.)"],
               "beach": ["{TIFA}\n“I need to see your face. Always.\n ...Don't ask me why. Not yet.”"]},
        aftermath=["{TIFA}\n(Off camera she sits on the edge of\n the bed, hugging her knees, a long\n while before she can stand.)"]),
    "Aerith": dict(
        tier1=["{AERIS}\n(She tilts her head mid-sentence, as\n if someone else had spoken.)\n “Hm? Oh. Nothing. Go on.”"],
        tier2=["{AERIS}\n“Promise me something silly? Never\n wear gloves around me.” (She isn't\n smiling when she says it.)"],
        part2={"capsule": ["{AERIS}\n“Oh... it's quiet. It's so quiet...”\n (She isn't talking about the\n capsule.)"],
               "gondola": ["{AERIS}\n(She looks up at you, wicked and\n bright. Nothing about her looks\n fragile now.)"],
               "cannon": ["{AERIS}\n“Don't be careful with me. I hate\n careful. ...Careful is for samples.”"],
               "beach": ["{AERIS}\n“Shh... listen. ...Nothing. Not one\n voice. Don't move. Stay like this.”"]},
        aftermath=["{AERIS}\n(Later she asks the crew, very\n seriously, not to send her a copy.\n Then she asks for two.)"]),
    "Scarlet": dict(
        tier1=["Scarlet\n(She checks her reflection in the\n window. Then checks it again, as if\n making sure she's still there.)"],
        tier2=["Scarlet\n“Lights stay on, puppy. Always.\n I'm not scared of the dark. I just\n like to be seen.” ...Too quickly."],
        part2={"capsule": ["Scarlet\n“The window... anyone out there could\n see us.” (She arches.) “Good.\n Let them look.”"],
               "gondola": ["Scarlet\n(She watches her own reflection in\n the dark glass the whole time, not\n you. As if she needs a witness.)"],
               "cannon": ["Scarlet\n“Louder, puppy. Make the whole city\n look up. ...If they're watching,\n I'm here.”"],
               "beach": ["Scarlet\n(When the beach falls silent for a\n moment, she stiffens. Then she\n laughs, much too loudly.)"]},
        aftermath=["Scarlet\n(When the lights go off, she's dressed\n and gone before anyone can say\n goodbye.)"]),
    "Elena": dict(
        tier1=["Elena\n(She's been writing your answers on\n a napkin. When she sees you've seen,\n she goes red to her ears.)"],
        tier2=["Elena\n“Do you ever do things just because\n someone expects you to? ...Forget\n it. Off the record.”"],
        part2={"capsule": ["Elena\n“Tell me what happens next. Please.\n I... I need to know the plan.”"],
               "gondola": ["Elena\n(Every few seconds she glances up\n for some sign she's doing it right.)"],
               "cannon": ["Elena\n“If I say stop... you'll stop?”\n (You nod.) “...Okay. Then don't.\n Don't stop.”"],
               "beach": ["Elena\n(Her shoulders, tight as wire all\n night, finally let go.)"]},
        aftermath=["Elena\n(She thanks every crew member by\n name. Then she sits alone in the car\n and shakes for ten minutes.)"]),
}


_DONE = set()


def _pages(line, pages):
    return line + "".join("{NEW}" + p for p in pages)


def apply_dates(dates):
    """Append the hints to `_dates_data.DATES` (once: marks the dict)."""
    if id(dates) in _DONE:
        return
    _DONE.add(id(dates))
    for name, s in SEEDS.items():
        d = dates[name]
        d["tiers"][0]["close"] = _pages(d["tiers"][0]["close"], s["tier1"])
        d["tiers"][1]["close"] = _pages(d["tiers"][1]["close"], s["tier2"])
        for place, pages in s["part2"].items():
            lines = d["part2"][place]
            k = max(i for i, (w, _) in enumerate(lines) if w == "G")
            lines[k] = ("G", _pages(lines[k][1], pages))


def apply_movie(girls):
    """Append the aftermath hints to `_movie_girls.GIRLS` (once)."""
    if id(girls) in _DONE:
        return
    _DONE.add(id(girls))
    for g in girls:
        if g["name"] in SEEDS:
            g["aftermath"] = _pages(g["aftermath"], SEEDS[g["name"]]["aftermath"])

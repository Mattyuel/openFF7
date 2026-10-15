"""(user) The revelation: once a date girl is at affection 20 and has made a video with Cloud
(`_config.REVEAL` video bit, set when the cameraman pays out a shoot she was in), her next date opens
with a scene about how the experience really felt: deeply emotional, sometimes surprising, written
against `_movie_profiles`. Every one of them is at least okay to keep doing it. Played once (seen bit),
in whichever place the date is; Tifa's Theme plays; no intimacy afterwards (the date ends).

REVEAL[name] = dict(
  pages  [(who, text)]: one text, a page each ("G" her, "C" Cloud),
  ask    (question, [(choice, [(who, text) pages of her reply])]),
  end    [(who, text)]: one text, a page each).
Lines are 3 rows at most, ~38 characters per row; speaker names are added.
"""

MUSIC = 34                       # TIFA: Tifa's Theme (music table index; id 35)
AFTER = "(You stay beside her a long while,\n saying nothing at all. It's enough.)"

REVEAL = {
    # the mediator: the first thing she ever chose only for herself; cathartic, she cries
    "Tifa": dict(
        pages=[("G", "“Cloud... can I tell you something?\n I've been carrying it around since\n the shoot.”"),
               ("C", "“Of course.”"),
               ("G", "(She looks out at the view for a long\n moment before she speaks.)"),
               ("G", "“On set, nobody needed me to fix\n anything. Nobody to hold together.\n I could just... be there.”"),
               ("G", "“It felt good. Really good. And then\n I went home, and I couldn't stop\n shaking.”"),
               ("G", "“I kept thinking about my father.\n About Nibelheim. About the girl\n everyone thought I'd grow up to be.”"),
               ("G", "(Her voice breaks. She's crying, and\n for once she doesn't try to hide it.)"),
               ("G", "“Every choice since the reactor was\n for someone else. For the cause.\n For Barret. For Marlene. For you.”")],
        ask=("“...Is that awful? That the first thing\n I ever chose just for me was that?”",
             [("“It's not awful. It was yours.”",
               [("G", "“...Mine.” (She laughs through the\n tears.) “Yeah. It was mine, wasn't\n it.”")]),
              ("(Just hold her.)",
               [("G", "(She leans into you and cries until\n it's all out of her. You don't let\n go once.)"),
                ("G", "“...Thank you. I didn't know how\n much I needed that.”")])]),
        end=[("G", "“I'm okay. Really. I think I'd even\n do it again... as long as you're\n there.”"),
             ("G", "“Just don't let me hide behind being\n strong. Not with you. Promise?”")]),
    # the playful instigator: surprising, she found a side of herself she likes, and isn't sorry
    "Aerith": dict(
        pages=[("G", "“Hey. Can I confess something? You\n have to promise not to laugh.”"),
               ("C", "“I promise.”"),
               ("G", "“My whole life, everyone's looked at\n me like I'm fragile. The flower girl.\n The last Ancient.”"),
               ("G", "“Mom wrapped me in cotton. Shinra\n wanted me in a jar. Even you look at\n me like I might break, sometimes.”"),
               ("G", "“On that set, nobody did. They looked\n at me like I was trouble. Like I was\n dangerous.”"),
               ("G", "(A slow, wicked smile spreads across\n her face... then it wavers.)"),
               ("G", "“And I loved it, Cloud. I didn't know\n that girl was in there. I think she's\n been waiting a long time.”"),
               ("G", "“Even the Planet went quiet. For once\n I wasn't listening to anyone. I was\n just... me. Only me.”")],
        ask=("“...Does she scare you? She scares me\n a little. Mostly, she doesn't.”",
             [("“I like her too.”",
               [("G", "“Careful. She heard that.” (She winks,\n and then her eyes go soft.)\n “...Thank you.”")]),
              ("“She doesn't change who you are.”",
               [("G", "“Maybe she does. Maybe that's the\n point.” (She takes your hand.)"),
                ("G", "“I'm still me. Just... more of me.\n The parts nobody wanted to see.”")])]),
        end=[("G", "“I'm not sorry. Is that terrible?\n ...Don't answer. I already know.”"),
             ("G", "“I'm going to keep doing it. For her.\n For me. You'll still walk me home\n after, right?”")]),
    # the controlling showwoman: surprising, she performs because the quiet terrifies her
    "Scarlet": dict(
        pages=[("G", "(Scarlet's smile is there, but tonight\n it doesn't reach her eyes.)"),
               ("G", "“Kyahaha... You've seen the tapes,\n puppy. Everyone has. Everyone's\n watching me. Good.”"),
               ("C", "“Scarlet. What's wrong?”"),
               ("G", "(She doesn't answer for a long time.\n When she does, the laugh is gone.)"),
               ("G", "“You want to know why I love the\n camera? Because when it's on me,\n I exist.”"),
               ("G", "“I grew up in a sector nobody counts.\n I could have vanished, and nobody\n would ever have noticed.”"),
               ("G", "“So I made sure they'd never stop\n looking. Louder. Brighter. Every\n room, every board meeting.”"),
               ("G", "“The shoot was the first time I had\n everyone's eyes... and I still went\n home and couldn't sleep.”"),
               ("G", "(Her hands are shaking. She sits on\n them, furious with herself.)"),
               ("G", "“It's the quiet. When the lights go\n off, I'm scared I'll just... stop.”")],
        ask=("“...Say something. Before I start\n hating you for seeing me like this.”",
             [("“I see you. Cameras or not.”",
               [("G", "(Her composure cracks. One tear, wiped\n away fast.) “...Damn you. That's a\n dangerous thing to say to a woman.”")]),
              ("“You don't have to perform for me.”",
               [("G", "“...Don't I?” (She lets out a breath\n she's been holding for years.)"),
                ("G", "“...Then I won't. Not tonight.”")])]),
        end=[("G", "“I'll keep doing it. Under the lights\n is the only place I'm brave.”"),
             ("G", "“But you... you stay where I can see\n you when they go off. That's an\n order.”"),
             ("G", "“...Kyahaha.” (It's small. But for\n once, it's real.)")]),
    # the cautious professional: her rules were the first time anyone asked her; she cries
    "Elena": dict(
        pages=[("G", "“Can I say something off the record?\n Not as a Turk. Just as me.”"),
               ("C", "“Go ahead.”"),
               ("G", "“Before the shoot, I wrote my rules.\n Three pages. Laminated. I know,\n I know.”"),
               ("G", "“And they listened. Every one. They\n asked me before every change. ‘Is\n this okay, Elena?’”"),
               ("G", "(Her eyes fill. She blinks, hard, and\n it doesn't help at all.)"),
               ("G", "“In the Turks, nobody asks. Tseng\n gives an order and I say ‘yes, sir’.\n I've said yes my whole career.”"),
               ("G", "“I never noticed I'd stopped having a\n choice. Not until somebody finally\n gave me one.”"),
               ("G", "(She's crying now, quietly, the way\n people do when they're not used to\n being allowed to.)")],
        ask=("“Is it stupid? That I found my own\n voice making... that kind of film?”",
             [("“Not stupid. Brave.”",
               [("G", "“Brave.” (She tries the word out.)\n “...Nobody's ever called me that.\n Not even in a report.”")]),
              ("(Hand her a handkerchief.)",
               [("G", "(She laughs, wetly, and blows her nose\n very professionally.) “...You're the\n worst. Thank you.”")])]),
        end=[("G", "“I'm okay. I'm going to keep doing\n it... with my rules. All three\n pages.”"),
             ("G", "“And maybe someday I'll try saying\n no to Tseng. Just to see his face.”")]),
}

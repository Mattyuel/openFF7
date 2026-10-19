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
    # (`_backstories`) the mediator: what happened in Nibelheim (never described), the faking, the
    # going far away; she cries; she wants to stop faking with him
    "Tifa": dict(
        pages=[("G", "“Cloud... can I tell you something?\n I've never said it out loud. Not to\n anyone.”"),
               ("C", "“I'm here.”"),
               ("G", "(She looks out at the view for a long\n time. Her hands won't stay still.)"),
               ("G", "“Do you remember Mina? Black braids.\n My best friend, the summer we were\n nine.”"),
               ("G", "“There was a man who worked up at\n the mansion. He'd come down to town.\n He brought us sweets.”"),
               ("G", "“He hurt us. Both of us. All that\n summer. ...I'm not going to tell you\n how. I can't.”"),
               ("G", "(Her voice is perfectly steady.\n Somehow that's worse.)"),
               ("G", "“Mina told her mom. Nobody believed\n her. By winter, her family had left\n Nibelheim.”"),
               ("G", "“I saw what telling did to her. So I\n never told. Not Mom. Not you. Not\n anybody.”"),
               ("G", "“That's why I learned to fight. So no\n one could ever hold me down again.”"),
               ("G", "“It's why I flinch when someone\n touches my neck. Why I sleep facing\n the door.”"),
               ("G", "(And then the steadiness breaks.\n She's crying, hard, the way a child\n cries.)"),
               ("G", "“And in bed... I've never once really\n been there, Cloud. I take care of\n them. I make the right sounds.”"),
               ("G", "“I float up by the ceiling and watch,\n and wait for it to be over. I've\n faked every single time.”"),
               ("G", "“On set it was a role. I knew my\n lines. I felt safe... and that\n scared me more than anything.”")],
        ask=("“...Do you still see me the same way?\n Be honest. I can take it.”",
             [("“You're the strongest person I know.”",
               [("G", "“I don't feel strong. I feel nine.”\n (She laughs, wetly.) “...But thank\n you. I needed somebody to say it.”")]),
              ("(Hold her. From the front.)",
               [("G", "(She tenses... then she sees your\n face, and lets herself fall into\n you, and sobs until it's all out.)"),
                ("G", "“...You came at me from the front.\n You noticed.” (She holds on tight.)\n “Thank you.”")])]),
        end=[("G", "“I'm okay. I chose the movies, and I'd\n choose them again. That part is\n mine.”"),
             ("G", "“But with you... I don't want to fake\n it anymore. I want to learn what I\n really feel. Slowly. Lights on.”"),
             ("G", "“And maybe... I'll write to Mina.\n After all these years.”")]),
    # (`_backstories`) the playful instigator, surprising: the lab, the Planet's voices and the quiet
    # she chased, careful touch; the hungry, bossy girl she found, and isn't sorry about
    "Aerith": dict(
        pages=[("G", "“Hey. Can I tell you a secret? A real\n one. And promise not to be careful\n with me?”"),
               ("C", "“I promise.”"),
               ("G", "“You know I grew up in Hojo's lab.\n Until I was seven.”"),
               ("G", "“Gloved hands. Cold metal. A pane of\n glass, and men behind it writing\n down everything I did.”"),
               ("G", "“Mom died getting me out. Then Elmyra\n raised me to be good. And I was. I'm\n so good, Cloud.”"),
               ("G", "(She smiles the flower girl's smile.\n It doesn't last.)"),
               ("G", "“The Planet talks to me. All the\n time. It never stops. Not when I\n sleep. Not ever.”"),
               ("G", "“Except at one moment. When it's\n really, really good. Then everything\n goes quiet.”"),
               ("G", "“I chased that quiet. With people I\n didn't love. I used them a little.\n I told myself that was okay.”"),
               ("G", "“And if anyone touched me gently, so\n carefully, like something precious...\n I went cold. Back on the table.”"),
               ("G", "“On set, the camera didn't measure\n me. It wanted me. And I was the one\n making the scene happen.”"),
               ("G", "“There's a girl in me who's hungry.\n Bossy. A little wicked. She loves\n making men lose control.”"),
               ("G", "“I think she's been in there since\n the glass. Waiting for me to stop\n being good.”")],
        ask=("“...Does she scare you? She scares me\n a little. Mostly, she doesn't.”",
             [("“I like her. Don't hide her from me.”",
               [("G", "“Careful. She heard that.” (Her eyes\n shine and she doesn't wipe them.)\n “Nobody's ever wanted all of me.”")]),
              ("“You didn't use them. You survived.”",
               [("G", "“...Survived.” (She turns the word\n over like a smooth stone.)"),
                ("G", "“Maybe I'm allowed to want the quiet.\n And her. Both.”")])]),
        end=[("G", "“I'm not sorry. Is that terrible?\n ...Don't answer. I already know.”"),
             ("G", "“I'm going to keep doing it. For her.\n For me. And with you... never be\n careful with me. Ever.”")]),
    # (`_backstories`) the controlling showwoman, surprising: the wardrobe, the executive, never
    # finishing without being watched, never staying till morning
    "Scarlet": dict(
        pages=[("G", "(Scarlet's smile is there, but tonight\n it doesn't reach her eyes.)"),
               ("G", "“Kyahaha... You've seen the tapes,\n puppy. Everyone has. Everyone's\n watching me. Good.”"),
               ("C", "“Scarlet. What's wrong?”"),
               ("G", "(She doesn't answer for a long time.\n When she does, the laugh is gone.)"),
               ("G", "“I grew up in a Sector 6 tenement.\n My mother brought men home. A lot of\n them.”"),
               ("G", "“On those nights I hid in the\n wardrobe, so small nobody knew I\n was there.”"),
               ("G", "“I got very good at vanishing. Too\n good. Nobody ever came looking.”"),
               ("G", "“At nineteen I was a secretary on the\n sixty-sixth floor. Quiet. Pretty. An\n executive liked quiet.”"),
               ("G", "“He cornered me in an office with the\n blinds down, where nobody could see.\n ...I won't say his name.”"),
               ("G", "“After that I swore: never quiet.\n Never unseen. Louder than anyone.\n In charge of every room.”"),
               ("G", "(Her hands are shaking. She sits on\n them, furious with herself.)"),
               ("G", "“I've never once finished alone. In\n the dark. With nobody watching.\n Not once in my life.”"),
               ("G", "“A mirror. Lights. A camera. Then I'm\n real. Then I'm safe. In the quiet\n I just... stop.”"),
               ("G", "“And I've never stayed until morning.\n With anyone. I'm dressed and gone\n before the light.”")],
        ask=("“...Say something. Before I start\n hating you for seeing me like this.”",
             [("“I see you. Lights or not.”",
               [("G", "(Her composure cracks. One tear,\n wiped away fast.) “...Damn you.\n That's a dangerous thing to say.”")]),
              ("“Stay tonight. Till morning. Dark.”",
               [("G", "“...In the dark.” (She lets out a\n breath she's been holding for\n years.)"),
                ("G", "“If I panic, you hold on. You don't\n let me leave. ...That's an order.”")])]),
        end=[("G", "“I'll keep doing the films. Under the\n lights is where I'm brave.”"),
             ("G", "“But with you... I want to try the\n quiet. Just once. No show.”"),
             ("G", "“...Kyahaha.” (It's small. But for\n once, it's real.)")]),
    # (`_backstories`) the cautious professional: "yes, sir", the officer, the pain she never
    # mentioned, never finishing; her rules were the first no anyone respected; she cries
    "Elena": dict(
        pages=[("G", "“Can I say something off the record?\n Not as a Turk. Just as me.”"),
               ("C", "“Go ahead.”"),
               ("G", "“My sister was a Turk. The best. I\n joined to be like her. I learned\n ‘yes, sir’ before I learned to shoot.”"),
               ("G", "“There was a senior officer. I won't\n say who. He expected me to go out\n with him. So I did.”"),
               ("G", "“I said yes to everything. It hurt,\n Cloud. Every single time. And I\n never said a word.”"),
               ("G", "“Complaining isn't professional.\n That's what I told myself.”"),
               ("G", "(Her eyes fill. She blinks, hard, and\n it doesn't help at all.)"),
               ("G", "“I've never... finished. With anyone.\n My body locks up when I don't know\n what's coming.”"),
               ("G", "“I thought I was broken. I wrote it in\n my journal like a failed mission.”"),
               ("G", "“Before the shoot, I wrote my rules.\n Three pages. Laminated. And they\n listened. Every one.”"),
               ("G", "“‘Is this okay, Elena?’ Before every\n change. I said no, once... and they\n just stopped.”"),
               ("G", "“That's when it happened. The\n wanting. For the first time in my\n life, it was mine.”"),
               ("G", "(She's crying now, quietly, the way\n people do when they're not used to\n being allowed to.)")],
        ask=("“Is it stupid? That I found my own\n voice making... that kind of film?”",
             [("“Not stupid. Brave.”",
               [("G", "“Brave.” (She tries the word out.)\n “...Nobody's ever called me that.\n Not even in a report.”")]),
              ("“With me, you set the rules too.”",
               [("G", "“With you too?” (She laughs, wetly,\n and blows her nose very\n professionally.)"),
                ("G", "“Then rule one: you ask me. Every\n time. Even when you think you know.”")])]),
        end=[("G", "“I'm okay. I'm going to keep doing\n it... with my rules. All three\n pages.”"),
             ("G", "“And maybe someday I'll say no to\n Tseng. Just to see his face.”")]),
}

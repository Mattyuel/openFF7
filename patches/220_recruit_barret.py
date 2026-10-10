"""Recruit Barret on Mt. Corel, on the railway screen just after the Corel
Reactor (mtcrl_3). His adult model is copied from the reactor screen (mtcrl_2);
mtcrl_3 itself only has young Barret for the flashback."""
from _config import BARRET
from _recruit import add_recruit_npc

LINES = dict(
    question="{BARRET}\n“…{CLOUD}. This is where it all started.\n Corel was my home once.”",
    choices=("Come with me, Barret.", "I'll leave you to it."),
    yes_reply="{BARRET}\n“Yeah… standin' here ain't gonna\n change nothin'. Let's go!”",
    no_reply="{BARRET}\n“I'ma stay a while. Got some thinkin' to do.”",
    joined="{BARRET} joined the party!",
)
# On the tracks (walkmesh triangle 180), where the flashback's old man stands.
POS = (326, 27, 551, 180)
DIR = 0xC0


def apply(ctx):
    add_recruit_npc(ctx, "mtcrl_3", "mtcrl_2", 2, "barret", BARRET, POS, DIR, LINES)

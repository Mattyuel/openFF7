"""Recruit Barret at the No.1 Reactor train platform (md1stin), above and a
little left of the train conductor (250_train_destinations). His model is
copied from the Corel reactor screen (mtcrl_2)."""
from _config import BARRET
from _recruit import add_recruit_npc

LINES = dict(
    question="{BARRET}\n“…{CLOUD}. Just lookin' at that reactor\n makes my blood boil.”",
    choices=("Come with me, Barret.", "I'll leave you to it."),
    yes_reply="{BARRET}\n“Yeah… standin' here ain't gonna\n change nothin'. Let's go!”",
    no_reply="{BARRET}\n“I'ma stay a while. Got some thinkin' to do.”",
    joined="{BARRET} joined the party!",
)
# ~30 px above and ~40 px left of the conductor (3715, 27432) on screen.
POS = (3680, 27732, 310, 20)
DIR = 254                     # facing down the screen


def apply(ctx):
    add_recruit_npc(ctx, "md1stin", "mtcrl_2", 2, "barret", BARRET, POS, DIR, LINES)

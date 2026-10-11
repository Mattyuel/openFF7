"""Recruit Red XIII, Cid and Cait Sith as NPCs; make Yuffie's and Vincent's
original joins count as recruits.

- Red XIII: Shinra HQ 67F research lab (blin67_1), by the stairs from 66F.
  His original join (blin68_2) needs progress 278-283; the field is pinned past it.
- Cid: Rocket Town launch pad (rcktbas1), by the rocket. His original join
  follows the Palmer fight at a story moment the pin (998) skips.
- Cait Sith: Wonder Square (games), where he meets you (his entity's spot at
  progress 440); that scene is gated on progress == 440, so with the field
  pinned at 443 it never plays and his entity stays hidden.
  Cait Sith and Vincent share character records 6/7 with Young Cloud and
  Sephiroth: the name entry (MENU 00 06 c) copies the real level-1 record
  over the slot (exe 0x718ADA), so his recruit runs it, as the original does.
- Yuffie: the world map encounter is on from new game ((3,133,0) in
  INITIAL_EVENT_FLAGS); her join in yougan2 only makes her PHS-available
  (MMBUD), so add PRTYP + the recruit count.
- Vincent: his join in sininb1 opens the PHS (MENU 00 07 00), which can only
  be left with exactly 3 in the party (a softlock with fewer); replaced by
  PRTYP + the recruit count.
"""
from _config import CAIT_SITH, CID, RECRUITED, RED_XIII, VINCENT, YUFFIE
from _recruit import add_recruit_npc, count_recruit

from ff7 import asm
from ff7.script import Op, Script

RED = dict(
    field="blin67_1", donor=("blin67_2", 4), name="rednpc", char=RED_XIII,
    pos=(1083, 66, 0, 69), dir=249,                # by the 66F stairs; facing down the screen
    lines=dict(
        question="{RED XIII}\n“You are not one of Hojo's people.\n Take me out of this place,\n and I will fight beside you.”",
        choices=("Come with us.", "Not yet."),
        yes_reply="{RED XIII}\n“Then let us leave. I have seen\n enough of this laboratory.”",
        no_reply="{RED XIII}\n“…I will wait. I have grown used to it.”",
        joined="{RED XIII} joined the party!"))
CID_ = dict(
    field="rcktbas1", donor=("rcktbas1", 2), name="cidnpc", char=CID,
    pos=(-21, 1525, 0, 0), dir=151,                # by the rocket; facing down the screen
    lines=dict(
        question="{CID}\n“Damn rocket ain't goin' nowhere.\n Might as well go somewhere myself.\n Need a pilot?”",
        choices=("Welcome aboard, Cid.", "Maybe later."),
        yes_reply="{CID}\n“Hah! Now we're talkin'.\n Let's get the hell outta here!”",
        no_reply="{CID}\n“Suit yourself. I'll be here\n starin' at this hunk of junk.”",
        joined="{CID} joined the party!"))
CAIT = dict(
    field="games", donor=("games", 6), name="caitnpc", char=CAIT_SITH,
    pos=(435, -211, 0, 39), dir=218,               # his meeting spot; facing down the screen
    lines=dict(
        question="{CAIT SITH}\n“How about a fortune? …Ooh! It says\n I should come with you! Can I?”",
        choices=("Sure, why not.", "No thanks."),
        yes_reply="{CAIT SITH}\n“Great! You won't regret it!\n …Probably.”",
        no_reply="{CAIT SITH}\n“Aw, shucks. I'll be here if ye\n change yer mind!”",
        joined="{CAIT SITH} joined the party!",
        extra=[Op(bytes([0x49, 0x00, 0x06, CAIT_SITH]))]))   # MENU 00 06 06: name entry (fills his record)

MMBUD = lambda c: bytes([0xCD, 0x01, c])
PRTYP = lambda c: Op(bytes([0xC8, c]))


def _join_ops(char):
    return [PRTYP(char), asm.biton(RECRUITED, char)] + count_recruit()


def _find(sec, raw):
    hits = [o for o in sec.ops if bytes(o.raw) == raw]
    assert len(hits) == 1, (raw.hex(), len(hits))
    return hits[0]


def _yuffie(ctx):
    sec = Script.parse(ctx.field("yougan2").sections[0])
    mmbud = _find(sec, MMBUD(YUFFIE))
    nxt = sec.ops[sec.index(mmbud) + 1]
    assert bytes(nxt.raw) == bytes([0x82, 0x30, 207, 0]), "yougan2: expected BITON (3,207,0) after MMBUD"
    sec.insert_after(mmbud, _join_ops(YUFFIE))
    ctx.field("yougan2").sections[0] = sec.build()


def _vincent(ctx):
    sec = Script.parse(ctx.field("sininb1").sections[0])
    mmbud = _find(sec, MMBUD(VINCENT))
    phs = sec.ops[sec.index(mmbud) + 1]
    assert bytes(phs.raw) == bytes([0x49, 0x00, 0x07, 0x00]), "sininb1: expected MENU 00 07 00 after MMBUD"
    sec.replace(phs, _join_ops(VINCENT))
    ctx.field("sininb1").sections[0] = sec.build()


def apply(ctx):
    for r in (RED, CID_, CAIT):
        add_recruit_npc(ctx, r["field"], *r["donor"], r["name"], r["char"], r["pos"], r["dir"], r["lines"])
    _yuffie(ctx)
    _vincent(ctx)

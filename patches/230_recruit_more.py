"""Recruit NPCs for Red XIII, Cid, Cait Sith, Yuffie and Vincent (Barret: 220).

- Red XIII: Shinra HQ 67F research lab (blin67_1), by the stairs from 66F.
- Cid: Junon airport, the airstrip (junair).
- Cait Sith: Costa del Sol beach (del3), far right.
- Yuffie: Chocobo Ranch (frcyo), on the walkway by the left pen's fence,
  looking at the chocobos in her scheming pose (yougan2 model, anim 6).
- Vincent: Honey Bee Inn, the dancers' room (onna_2), far left. Embarrassed.
  Cait Sith and Vincent share character records 6/7 with Young Cloud and
  Sephiroth; in the original the name entry (MENU 00 06 c) copies their
  level-1 record from the exe (template 0x921EF8 + id*0x84, exe 0x718ADA) over
  the slot. Here the new-game data (KERNEL section 3) gets those templates
  directly, with the default names, so they join without a naming screen.
- The original joins still work and count once: Yuffie's (yougan2, if her
  world map encounter is ever on) and Vincent's (sininb1) get PRTYP + the
  recruit count unless already recruited; Vincent's PHS menu (needs exactly
  3 in the party to leave: a softlock) is replaced.
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
    field="junair", donor=("rcktbas1", 2), name="cidnpc", char=CID,
    pos=(13232, 14084, 5139, 80), dir=169,         # mid airstrip; facing down the screen
    lines=dict(
        question="{CID}\n“Nice runway. Shame Shinra never lets\n a real pilot near it. Need one?”",
        choices=("Welcome aboard, Cid.", "Maybe later."),
        yes_reply="{CID}\n“Hah! Now we're talkin'.\n Let's get the hell outta here!”",
        no_reply="{CID}\n“Suit yourself. I'll be here\n watchin' the planes.”",
        joined="{CID} joined the party!"))
CAIT = dict(
    field="del3", donor=("games", 6), name="caitnpc", char=CAIT_SITH,
    pos=(758, -41, -35, 278), dir=233,             # the beach, far right; facing down the screen
    lines=dict(
        question="{CAIT SITH}\n“How about a fortune? …Ooh! It says\n I should come with you! Can I?”",
        choices=("Sure, why not.", "No thanks."),
        yes_reply="{CAIT SITH}\n“Great! You won't regret it!\n …Probably.”",
        no_reply="{CAIT SITH}\n“Aw, shucks. I'll be here if ye\n change yer mind!”",
        joined="{CAIT SITH} joined the party!"))
YUFFIE_ = dict(
    field="frcyo", donor=("yougan2", 8), name="yufinpc", char=YUFFIE,
    pos=(-175, -790, 0, 41), dir=0xC0,             # by the left pen's fence, facing the chocobos
    main=[Op(b"\xA2\x06\x01")],                    # DFANM 06 01: her "just as I planned" pose
    lines=dict(
        question="{YUFFIE}\n“Wha-!? I wasn't gonna steal a chocobo!\n …Okay, maybe one. You need\n a ninja? The great {YUFFIE}?”",
        choices=("Sure, come along.", "Not a chance."),
        yes_reply="{YUFFIE}\n“Heh, heh… just as I planned.\n Lead the way!”",
        no_reply="{YUFFIE}\n“Your loss! More chocobos for me.”",
        joined="{YUFFIE} joined the party!"))
VINCENT_ = dict(
    field="onna_2", donor=("yougan2", 7), name="vincnpc", char=VINCENT,
    pos=(-249, -147, 25, 29), dir=135,             # lower left, on the main floor (z 25, not the z 50 step)
    lines=dict(
        question="{VINCENT}\n“…This is not what it looks like.\n I was told this was a library.\n …Get me out of here.”",
        choices=("Come with me.", "Enjoy the library."),
        yes_reply="{VINCENT}\n“…We will never speak of this.”",
        no_reply="{VINCENT}\n“…………”",
        joined="{VINCENT} joined the party!"))

TEMPLATES_VA = 0x921EF8          # exe: level-1 character records, 0x84 each, by id
DEFAULT_NAMES = {CAIT_SITH: "Cait Sith", VINCENT: "Vincent"}   # exe 0x921CB8 (the template says "Cait Seith")

MMBUD = lambda c: bytes([0xCD, 0x01, c])
PRTYP = lambda c: Op(bytes([0xC8, c]))


def _join_ops(char):
    done = asm.nop()
    return [PRTYP(char), asm.if_byte(RECRUITED, "bit_off", char, done),   # already recruited: don't count twice
            asm.biton(RECRUITED, char)] + count_recruit() + [done]


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


def _records(ctx):
    import os
    import ff7tool
    from ff7 import exepatch
    exe = open(os.path.join(os.path.dirname(ff7tool.GAME), "ff7_en.exe"), "rb").read()
    init = ctx.kernel_init()
    for char, name in DEFAULT_NAMES.items():
        o = exepatch.va_to_file(exe, TEMPLATES_VA + char * init.CHAR)
        record = exe[o:o + init.CHAR]
        assert record[0] == char and record[1] == 1, (char, record[:2])
        init.data[char * init.CHAR:(char + 1) * init.CHAR] = record
        init.set_name(char, name)


def apply(ctx):
    _records(ctx)
    for r in (RED, CID_, CAIT, YUFFIE_, VINCENT_):
        add_recruit_npc(ctx, r["field"], *r["donor"], r["name"], r["char"], r["pos"], r["dir"], r["lines"],
                        main=r.get("main", ()))
    _yuffie(ctx)
    _vincent(ctx)

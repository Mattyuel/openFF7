"""Train travel from the Sector 7 station, the reactors, and their bosses.

- Sector 7 station (mds7st3): talk to the conductor for a list of
  destinations: Upper Midgar (Sector 8 bridge), No.1 Reactor (Sector 1
  platform, where the game originally starts) and No.5 Reactor (the tunnel
  after jumping off the train). He calls "ALL ABOARD!", the train sound plays
  and you are there.
- Each destination has a train attendant who takes you back the same way.
- No.1 Reactor: entrance gate open, Biggs' gate open (new-game flag), the
  button door opens on its own. Guard Scorpion stands at the core: talk to it
  to fight; beaten, it is gone.
- No.5 Reactor: the three-button door is open (smkin_1 fixed after it). On
  the bridge outside, the Barret scene line is off and Air Buster stands on
  the bridge instead: talk to it to fight.
The bosses use a stand-in robot model (there are no field models for them).
"""
from _config import (FLAG_AIR_BUSTER, FLAG_GUARD_SCORPION, FLAGS, START_FIELD, START_TRIANGLE,
                     START_X, START_Y)
from _recruit import hide, say
from _travel import add_npc, choice_menu, copy_model, mapjump, near

from ff7 import asm
from ff7.script import Op, Script
from ff7.text import encode

DESTINATIONS = {
    # name: (field, x, y, triangle, direction)
    "Upper Midgar": ("md8brdg", -422, 1387, 3, 0),
    "No. 1 Reactor": ("md1stin", 3655, 27432, 25, 0x80),
    "No. 5 Reactor": ("tunnel_1", 21, -365, 48, 128),
}
ATTENDANT_MODEL = ("mds7_w1", 1)   # a Sector 7 townsman model
ROBOT_MODEL = ("md8brdg2", None)   # 'another_robo' (found by name below)
GUARD_SCORPION = dict(field="nmkin_5", formation=324, triangle=3, flag=FLAG_GUARD_SCORPION,
                      line="“Intruder detected.\n Commencing elimination.”")
AIR_BUSTER = dict(field="southmk1", formation=364, triangle=2, flag=FLAG_AIR_BUSTER,
                  line="“Target acquired.\n Engaging.”")


TRAIN_SOUND = 0x190        # the train sound used when trains pull in
ALL_ABOARD_TEXT = 49       # mds7st3: “ALL ABOARD! The train is about to depart.”


def _depart(sec, jump, text_id=None):
    """Conductor's call, train sound, short wait, then the map jump."""
    from _recruit import window
    if text_id is None:
        text_id = sec.add_string(encode("“ALL ABOARD!”"))
    return [window("“ALL ABOARD!\n The train is about to depart.”"),
            asm.message(0, text_id),
            Op(bytes([0xF1, 0x00]) + TRAIN_SOUND.to_bytes(2, "little") + b"\x40"),   # SOUND
            Op(b"\x24\x1e\x00"),                                                    # WAIT 30
            jump]


def _train_menu(ctx):
    """The station conductor ('guard') offers the destinations."""
    sec = Script.parse(ctx.field("mds7st3").sections[0])
    ent = sec.entity_index("guard")
    names = list(DESTINATIONS)
    jumps = [_depart(sec, mapjump(ctx, *DESTINATIONS[n]), ALL_ABOARD_TEXT) for n in names] + [None]
    menu = choice_menu(sec, "Conductor\n“Where are you headed?”", names + ["Nowhere, thanks."], jumps)
    sec.insert_before(sec.entry[ent][1], menu, retarget=False)
    sec.entry[ent][1] = menu[0]
    # The line at the train door ('border1') boarded the story train; switch it off.
    linon = [o for o in sec.script_ops(sec.entity_index("border1"), 0) if o.op == 0xD1]
    assert linon and linon[0].raw[1] == 1, "expected LINON 01 in border1 init"
    linon[0].raw[1] = 0
    ctx.field("mds7st3").sections[0] = sec.build()


def _attendants(ctx):
    for name, (field, x, y, tri, _d) in DESTINATIONS.items():
        model = copy_model(ctx, field, *ATTENDANT_MODEL)
        pos = near(ctx, field, tri)

        def talk(sec):
            back = _depart(sec, mapjump(ctx, START_FIELD, START_X, START_Y, START_TRIANGLE))
            return choice_menu(sec, "Train Attendant\n“Heading back to Sector 7?”",
                               ["Yes, take me back.", "Not yet."], [back, None])
        add_npc(ctx, field, "attend", model, pos, 0x80, talk)


def _robot_index(ctx):
    from ff7.models import ModelLoader
    models = ModelLoader(ctx.field("md8brdg2").section("models")).models
    return next(i for i, m in enumerate(models) if "another_robo" in ModelLoader.name(m))


def _boss(ctx, field, formation, triangle, flag, line):
    from ff7.walkmesh import Walkmesh
    model = copy_model(ctx, field, "md8brdg2", _robot_index(ctx))
    x, y, z = Walkmesh(ctx.field(field).section("walkmesh")).center(triangle)
    gone = asm.nop()
    init = [asm.if_byte(FLAGS, "bit_on", flag, gone)] + hide() + [gone]   # hidden once beaten

    def talk(sec):
        return ([Op(b"\x33\x01")] + say(sec, line)
                + [asm.battle(formation), asm.biton(FLAGS, flag)]
                + hide() + [Op(b"\x33\x00"), asm.ret()])
    add_npc(ctx, field, "boss", model, (x, y, z, triangle), 0x00, talk, init)


def _reactor1_doors(ctx):
    # Entrance (nrthmk): don't draw the closed gate or lock its floor.
    sec = Script.parse(ctx.field("nrthmk").sections[0])
    for o in list(sec.script_ops(sec.entity_index("dir"), 0)):
        if (o.op == 0x01 and o.raw[1] == 9) or (o.op == 0x6D and o.raw[1] == 0x0B and o.raw[3] == 1):
            sec.remove(o)
    ctx.field("nrthmk").sections[0] = sec.build()
    # First room (nmkin_1): open the button door on entry (its script 3).
    sec = Script.parse(ctx.field("nmkin_1").sections[0])
    init = sec.script_ops(sec.entity_index("dir"), 0)
    end = next(o for o in init if o.op == 0x00)
    main_first = init[init.index(end) + 1]
    sec.insert_before(main_first, [Op(bytes([0x01, 0x05, 0xC3]))])  # REQ 05 script 3
    ctx.field("nmkin_1").sections[0] = sec.build()


def _reactor5_bridge(ctx):
    # The line on the bridge started Barret's scene and jumped to the story copy.
    sec = Script.parse(ctx.field("southmk1").sections[0])
    ent = sec.entity_index("line")
    ret = next(o for o in sec.script_ops(ent, 0) if o.op == 0x00)
    sec.insert_before(ret, [Op(b"\xD1\x00")])               # LINON 00
    ctx.field("southmk1").sections[0] = sec.build()


def apply(ctx):
    _train_menu(ctx)
    _attendants(ctx)
    _reactor1_doors(ctx)
    _reactor5_bridge(ctx)
    _boss(ctx, **GUARD_SCORPION)
    _boss(ctx, **AIR_BUSTER)

"""Train travel from the Sector 7 station, the reactors, and their bosses.

- Sector 7 station (mds7st3): talk to the conductor for a list of
  destinations: Upper Midgar (Sector 8 bridge), Shinra Tower (the plaza in
  front of HQ), No.1 Reactor (Sector 1 platform, where the game originally
  starts) and No.5 Reactor (the tunnel screen with the duct down). He calls "ALL ABOARD!", the train sound plays
  and you are there.
- Each destination has a conductor (the station conductor's model) standing
  beside where you arrive, at floor height, who takes you back the same way.
- No.1 Reactor: entrance gate open, Biggs' gate open (new-game flag), the
  button door opens on its own. At the core (nmkin_5) the bomb-planting scene
  is off; walking onto the core platform starts Guard Scorpion (once).
- No.5 Reactor: the three-button door is open (smkin_1 fixed after it). On
  the bridge outside, the Barret scene line is off and Air Buster stands on
  the bridge instead: talk to it to fight.
Air Buster uses a stand-in robot model (there is no field model for it).
- md1stin plays its music (id 3, "Bombing Mission", as md1_1/md1_2 go on
  with) when you arrive: the exe's MUSIC handler skips field 116 = md1stin
  (0x613BA3: the opening FMV syncs it), so the init also plays it with AKAO
  cmd 0x10 (music index = id - 1), which has no such check.
"""

from _config import (FLAG_AIR_BUSTER, FLAG_GUARD_SCORPION, FLAGS, START_FIELD, START_TRIANGLE,
                     START_X, START_Y)
from _recruit import hide, say
from _travel import add_line, add_npc, beside, choice_menu, copy_model, mapjump

from ff7 import asm
from ff7.script import Op, Script
from ff7.text import encode

DESTINATIONS = {
    # name: (field, x, y, triangle, direction)
    "Upper Midgar": ("md8brdg", -420, 100, 33, 0),    # mid-walkway (md8_3's arrival is at the top)
    "Shinra Tower": ("sinbil_1", -5, -3041, 45, 128),  # plaza in front of HQ (md0's arrival)
    "No. 1 Reactor": ("md1stin", 3655, 27432, 25, 0x80),
    # The tunnel screen with the duct down to the plate interior (tunnel_1's
    # arrival from it). tunnel_1 repeats (its far line jumps back to itself),
    # so a conductor there showed up on every loop.
    "No. 5 Reactor": ("tunnel_2", 6, 338, 3, 128),
}
CONDUCTOR_MODEL = ("mds7st3", 6)   # shinra_guard: the Sector 7 station conductor
CONDUCTOR_AT = {"Upper Midgar": (-240, 100)}   # 4 paces right of beside(): he was hidden (user)
ROBOT_MODEL = ("md8brdg2", None)   # 'another_robo' (found by name below)
# nmkin_5 (No.1 Reactor core): the original scene starts when Cloud's entity
# is on walkmesh triangle 2 (the platform at the far end). A line across the
# walkway where it meets that platform starts the fight instead, whoever leads.
GUARD_SCORPION_FIELD = "nmkin_5"
GUARD_SCORPION_FORMATION = 324
GUARD_SCORPION_LINE = ((-200, -1506, -184), (30, -1506, -184))
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
            Op(b"\x33\x00"),                                                       # UC 00
            jump]


def _train_menu(ctx):
    """The station conductor ('guard') offers the destinations."""
    sec = Script.parse(ctx.field("mds7st3").sections[0])
    ent = sec.entity_index("guard")
    names = list(DESTINATIONS)
    jumps = [_depart(sec, mapjump(ctx, *DESTINATIONS[n]), ALL_ABOARD_TEXT) for n in names] + [None]
    menu = choice_menu(sec, "Conductor\n“Where are you headed?”", names + ["Nowhere, thanks."], jumps, face=True)
    sec.insert_before(sec.entry[ent][1], menu, retarget=False)
    sec.entry[ent][1] = menu[0]
    # The line at the train door ('border1') boarded the story train; switch it off.
    linon = [o for o in sec.script_ops(sec.entity_index("border1"), 0) if o.op == 0xD1]
    assert linon and linon[0].raw[1] == 1, "expected LINON 01 in border1 init"
    linon[0].raw[1] = 0
    ctx.field("mds7st3").sections[0] = sec.build()


def _conductors(ctx):
    from ff7.walkmesh import Walkmesh
    for name, (field, x, y, tri, _d) in DESTINATIONS.items():
        assert Walkmesh(ctx.field(field).section("walkmesh")).contains(tri, x, y), (field, x, y, tri)
        model = copy_model(ctx, field, *CONDUCTOR_MODEL)
        pos = beside(ctx, field, x, y, tri)
        if name in CONDUCTOR_AT:
            mesh = Walkmesh(ctx.field(field).section("walkmesh"))
            cx, cy = CONDUCTOR_AT[name]
            ct = mesh.find(cx, cy)
            assert ct is not None, (name, cx, cy)
            pos = (cx, cy, mesh.height(ct, cx, cy), ct)

        def talk(sec):
            back = _depart(sec, mapjump(ctx, START_FIELD, START_X, START_Y, START_TRIANGLE))
            return choice_menu(sec, "Conductor\n“Heading back to Sector 7?”",
                               ["Yes, take me back to Sector 7.", "Not yet."], [back, None], face=True)
        add_npc(ctx, field, "conduct", model, pos, 0x80, talk)


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


def _guard_scorpion(ctx):
    field = GUARD_SCORPION_FIELD
    # Disable the scene: the main loop compares Cloud's triangle with var[6][7]
    # (set to 2 in the init); no triangle is 255.
    sec = Script.parse(ctx.field(field).sections[0])
    init = sec.script_ops(sec.entity_index("dir"), 0)
    target = next(o for o in init if o.op == 0x81 and o.raw[1] == 0x60 and o.raw[2] == 7)  # var[6][7] = 2
    assert target.raw[3] == 2, target.raw.hex()
    target.raw[3] = 255
    ctx.field(field).sections[0] = sec.build()

    def fight(sec):
        done = asm.ret()
        return [asm.if_byte(FLAGS, "bit_off", FLAG_GUARD_SCORPION, done),   # skip once beaten
                asm.biton(FLAGS, FLAG_GUARD_SCORPION),
                asm.battle(GUARD_SCORPION_FORMATION),
                done]
    add_line(ctx, field, "gscorp", *GUARD_SCORPION_LINE, fight)


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


REACTOR1_STATION, REACTOR1_MUSIC_INDEX = "md1stin", 2


def _reactor1_music(ctx):
    sec = Script.parse(ctx.field(REACTOR1_STATION).sections[0])
    init = sec.script_ops(sec.entity_index("dir"), 0)
    music = [o for o in init[:init.index(next(o for o in init if o.op == 0x00))] if bytes(o.raw) == b"\xf0\x00"]
    assert len(music) == 1, music                                   # MUSIC 00 (skipped by the exe here)
    play = Op(bytes([0xF2, 0, 0, 0, 0x10, REACTOR1_MUSIC_INDEX]) + bytes(8))   # AKAO 10: play music index
    sec.insert_after(music[0], [play])          # inside its "progress > 0" block: not on the new-game pass
    ctx.field(REACTOR1_STATION).sections[0] = sec.build()


def _reactor5_door(ctx):
    """smkin_1's three-button door (two door models, entities 4/5, slid open by OFST at
    progress >= 128) still read as shut in game (user: no way to Air Buster): the two
    door models are hidden and non-solid in their init."""
    f = ctx.field("smkin_1")
    sec = Script.parse(f.sections[0])
    done = 0
    for ent in range(len(sec.entry)):
        init = sec.script_ops(ent, 0)
        if init and init[0].op == 0xA1 and init[0].raw[1] in (3, 4):          # CHAR 3 / 4: the door halves
            ret = next(o for o in init if o.op == 0x00)
            sec.insert_before(ret, hide(), retarget=True)
            done += 1
    assert done == 2, done
    f.sections[0] = sec.build()


def apply(ctx):
    _reactor1_music(ctx)
    _reactor5_door(ctx)
    _train_menu(ctx)
    _conductors(ctx)
    _reactor1_doors(ctx)
    _reactor5_bridge(ctx)
    _guard_scorpion(ctx)
    _boss(ctx, **AIR_BUSTER)

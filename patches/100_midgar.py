"""Midgar in its early disc 1 state (before the Sector 7 plate falls).

Each field is detached from the global story-progress value
(see DESIGN.md §2 and docs/midgar_plan.md):
  - PINNED fields always behave as at one story moment, chosen between the
    story events so that no cutscene in the field fires.
  - REGION fields share a private progress variable (none in Midgar now).
Wall Market is pinned after the dress-up step, so the dress-up sequence and
Corneo's mansion events never play. Shinra HQ is pinned per floor to its
infiltration state without the capture/escape events, and the new game holds
every keycard (010_new_game.py), so it can be explored freely with its
infiltration random encounters. Trains and disc 2 Midgar are not handled yet.
"""
from _config import REGION_VARS

from ff7.patch import localise_progress
from ff7.script import Op, Script

PINNED = {
    # Sector 1 and No.1 Reactor: after entering (>=15), before the bomb (27).
    20: ["md1_1", "md1_2", "nrthmk", "nmkin_1", "nmkin_2", "nmkin_3", "nmkin_4",
         "nmkin_5", "elevtr1"],
    # Sector 8 streets: after the reactor 1 escape scenes (33-45).
    46: ["md8_1", "md8_2", "md8_3", "md8_4", "md8brdg"],
    # Sector 4 tunnels and No.5 Reactor: before the reactor 5 events (120+).
    112: ["tunnel_1", "tunnel_2", "tunnel_3", "smkin_2", "smkin_3",
          "smkin_4", "smkin_5", "southmk1", "southmk2"],
    # No.5 Reactor exit room: after the three-button door (127), door open.
    129: ["smkin_1"],
    # Sector 7 slums, station, Train Graveyard, pillar: after AVALANCHE's
    # morning scenes (108), before the plate events (212+).
    110: ["mds7st1", "mds7st2", "mds7st3", "mds7st32", "mds7_w1", "mds7_w2", "mds7_w3",
          "mds7", "mds7_im", "min71", "mds7pb_1", "mds7pb_2", "mds7plr1", "mds7plr2",
          "pillar_1", "pillar_2", "pillar_3"],
    # Sector 5 slums, church, Aerith's house: after her house scenes (170/173).
    177: ["mds5_1", "mds5_2", "mds5_3", "mds5_4", "mds5_dk", "mds5_w", "mds5_i",
          "mds5_m", "min51_1", "min51_2", "church", "chrin_1a", "chrin_1b", "chrin_2",
          "chrin_3a", "chrin_3b", "eals_1", "ealin_1", "ealin_12", "ealin_2"],
    # Sector 6: after the park scene with Aerith (176-185).
    186: ["mds6_1", "mds6_2", "mds6_22", "mds6_3"],
    # Slum outskirts (exit to the world map): after the party-gathering scene (335/336).
    342: ["mds5_5"],
    # Wall Market, Honey Bee Inn, Corneo's mansion and sewers: just after the
    # dress-up step (192), before the mansion events (197+). No cutscenes.
    193: ["mrkt1", "mrkt2", "mrkt3", "mkt_w", "mkt_mens", "mkt_ia", "mktinn",
          "mkt_m", "mkt_s1", "mkt_s2", "mkt_s3", "mktpb", "onna_2", "onna_4", "onna_5",
          "onna_52", "colne_1", "colne_2", "colne_3", "colne_4", "colne_5", "colne_6",
          "colne_b1", "colne_b3"],
    # Wall Market, back street with the wire up to the plate: the climb line
    # and the cable only exist from 257 (after the plate falls).
    258: ["mrkt4"],
}

# Shinra HQ, per floor: each field's moment sits between its own events
# (infiltration runs 257-326; 1008+ is disc 2).
SHINRA_HQ = {
    "md0": 263, "sinbil_1": 263, "sinbil_2": 263, "blinst_1": 263, "blinst_2": 263,
    "blinst_3": 263,
    "blin1": 261, "blin2": 261, "blin2_i": 261, "blin3_1": 261,
    "blin59": 263, "blinele": 263, "eleout": 263,
    "blin60_1": 263, "blin60_2": 263, "blin61": 263, "blin62_1": 263, "blin62_2": 263,
    "blin62_3": 263, "blin63_1": 263, "blin63_t": 263, "blin64": 263, "blin65_1": 263,
    "blin65_2": 263,
    "blin66_1": 271, "blin66_2": 271, "blin66_3": 271, "blin66_4": 271, "blin66_5": 271,
    "blin67_1": 281, "blin671b": 281, "blin67_3": 281, "blin673b": 281, "blin67_4": 281,
    "blin67_2": 297,
    "blin68_1": 285, "blin68_2": 285,
    "blin69_1": 303, "blin70_1": 303, "blin70_2": 303, "blin70_3": 303,
}
for _field, _moment in SHINRA_HQ.items():
    PINNED.setdefault(_moment, []).append(_field)

REGIONS = {}


def _edit(ctx, field, **kw):
    script = Script.parse(ctx.field(field).sections[0])
    stats = localise_progress(script, **kw)
    ctx.field(field).sections[0] = script.build()
    return stats


SLUMS_THEME = 35  # music id of the Sector 7 slums theme (the only track in mds7)


def _slums_music(ctx):
    """Play the slums theme at the Sector 7 station (the new-game start, silent
    in the original at this point) and in the slums entrance (mds7plr1), which
    switches to another track after story moment 108."""
    slums = Script.parse(ctx.field("mds7").sections[0])
    theme = slums.akao_block(slums.akao_ids().index(SLUMS_THEME))

    station = Script.parse(ctx.field("mds7st3").sections[0])
    track = station.add_akao(theme)
    produce = station.entity_index("produce")
    init_ret = next(o for o in station.script_ops(produce, 0) if o.op == 0x00)
    station.insert_before(init_ret, [Op(bytes([0xF0, track]))], retarget=False)  # MUSIC
    ctx.field("mds7st3").sections[0] = station.build()

    entrance = Script.parse(ctx.field("mds7plr1").sections[0])
    track = entrance.akao_ids().index(SLUMS_THEME)
    for op in entrance.script_ops(entrance.entity_index("produce"), 0):
        if op.op == 0xF0:
            op.raw[1] = track
    ctx.field("mds7plr1").sections[0] = entrance.build()


TRAINS_MOVED = 0x07   # var[1][164] bits 0-2: the three movable graveyard trains


def _train_graveyard(ctx):
    """Train Graveyard: keep the movable trains in their moved positions so the
    graveyard can be crossed both ways, and drop the Aerith scene that played
    when climbing the ladder out (it also reset the trains)."""
    from ff7 import asm
    sec = Script.parse(ctx.field("mds7st2").sections[0])
    init = sec.script_ops(sec.entity_index("init"), 0)
    end = next(o for o in init if o.op == 0x00)
    main_first = init[init.index(end) + 1]
    sec.insert_before(main_first, [asm.setbyte((1, 164), TRAINS_MOVED)])
    ctx.field("mds7st2").sections[0] = sec.build()

    sec = Script.parse(ctx.field("mds7st1").sections[0])
    for op in sec.script_ops(sec.entity_index("cloud"), 3):
        # pinned: `if not (110 < 212) goto normal_ladder` -> always take the normal ladder
        if op.op in (0x16, 0x17, 0x18, 0x19) and op.raw[1] == 0 and op.raw[4] | op.raw[5] << 8 == 212:
            sec.replace(op, [asm.goto(op.target)])
            break
    else:
        raise RuntimeError("graveyard ladder scene check not found")
    ctx.field("mds7st1").sections[0] = sec.build()


def apply(ctx):
    _slums_music(ctx)
    total = 0
    for moment, fields in PINNED.items():
        for field in fields:
            total += _edit(ctx, field, const=moment)["reads"]
    for region, fields in REGIONS.items():
        var = REGION_VARS[region][0]
        for field in fields:
            total += _edit(ctx, field, var=var)["reads"]
    _train_graveyard(ctx)   # after pinning: it looks for the pinned check
    print("  midgar: %d story checks localised in %d fields" %
          (total, sum(map(len, PINNED.values())) + sum(map(len, REGIONS.values()))))

"""Midgar in its early disc 1 state (before the Sector 7 plate falls).

Each field is detached from the global story-progress value
(see DESIGN.md §2 and docs/midgar_plan.md):
  - PINNED fields always behave as at one story moment, chosen between the
    story events so that no cutscene in the field fires.
  - REGION fields share a private progress variable so a multi-step side
    quest (Wall Market / Corneo) still plays out.
Shinra HQ, the trains and the disc 2 Midgar areas are not handled yet.
"""
from _config import REGION_VARS

from ff7.patch import localise_progress
from ff7.script import Script

PINNED = {
    # Sector 1 and No.1 Reactor: after entering (>=15), before the bomb (27).
    20: ["md1_1", "md1_2", "nrthmk", "nmkin_1", "nmkin_2", "nmkin_3", "nmkin_4",
         "nmkin_5", "elevtr1"],
    # Sector 8 streets: after the reactor 1 escape scenes (33-45).
    46: ["md8_1", "md8_2", "md8_3", "md8_4", "md8brdg"],
    # Sector 4 tunnels and No.5 Reactor: before the reactor 5 events (120+).
    112: ["tunnel_1", "tunnel_2", "tunnel_3", "smkin_1", "smkin_2", "smkin_3",
          "smkin_4", "smkin_5", "southmk1", "southmk2"],
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
}

REGIONS = {
    "wall_market": ["mrkt1", "mrkt2", "mrkt3", "mrkt4", "mkt_w", "mkt_mens", "mkt_ia",
                    "mktinn", "mkt_m", "mkt_s1", "mkt_s2", "mkt_s3", "mktpb", "onna_2",
                    "onna_4", "onna_5", "onna_52", "colne_1", "colne_2", "colne_3",
                    "colne_4", "colne_5", "colne_6", "colne_b1", "colne_b3"],
}


def _edit(ctx, field, **kw):
    script = Script.parse(ctx.field(field).sections[0])
    stats = localise_progress(script, **kw)
    ctx.field(field).sections[0] = script.build()
    return stats


def apply(ctx):
    total = 0
    for moment, fields in PINNED.items():
        for field in fields:
            total += _edit(ctx, field, const=moment)["reads"]
    for region, fields in REGIONS.items():
        var = REGION_VARS[region][0]
        for field in fields:
            total += _edit(ctx, field, var=var)["reads"]
    print("  midgar: %d story checks localised in %d fields" %
          (total, sum(map(len, PINNED.values())) + sum(map(len, REGIONS.values()))))

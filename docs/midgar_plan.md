# Midgar plan (for review)

How each Midgar field is detached from the global story value. Generated from
`patches/100_midgar.py` and `docs/inventory/fields.csv`.

- **Pinned M**: the field always behaves as at story moment M. M is chosen between
  story events, so the field's cutscenes do not fire.
- **Region**: the field shares a private progress variable with its region so a
  multi-step side quest still works.

| Field | Location | Method | Story checks in field | Notes |
|---|---|---|---|---|
| `md1_1` | Sector 1 Station | Pinned 20 | 7–7 (1) |  |
| `md1_2` | Sector 1 | Pinned 20 | 8–8 (1) |  |
| `nrthmk` | No.1 Reactor | Pinned 20 | 10–27 (2) |  |
| `nmkin_1` | No.1 Reactor | Pinned 20 | 10–27 (3) |  |
| `nmkin_2` | No.5 Reactor / No.1 Reactor | Pinned 20 | 13–27 (2) |  |
| `nmkin_3` | No.5 Reactor / No.1 Reactor | Pinned 20 | 14–27 (2) |  |
| `nmkin_4` | No.5 Reactor / No.1 Reactor | Pinned 20 | 27–27 (1) |  |
| `nmkin_5` | No.5 Reactor / No.1 Reactor | Pinned 20 | 15–123 (5) | Guard Scorpion room. The bomb/timer events (27+) will not fire; boss handled by the boss system later. |
| `elevtr1` | No.5 Reactor / No.1 Reactor | Pinned 20 | 12–33 (3) |  |
| `md8_1` | Sector 8 | Pinned 46 | 33–45 (2) |  |
| `md8_2` | — | Pinned 46 | 36–39 (2) |  |
| `md8_3` | — | Pinned 46 | — |  |
| `md8_4` | — | Pinned 46 | 33–33 (1) |  |
| `md8brdg` | Sector 8 | Pinned 46 | 39–39 (1) |  |
| `tunnel_1` | Winding Tunnel | Pinned 112 | — |  |
| `tunnel_2` | Winding Tunnel | Pinned 112 | — |  |
| `tunnel_3` | Winding Tunnel | Pinned 112 | — |  |
| `smkin_1` | — | Pinned 112 | 127–128 (2) |  |
| `smkin_2` | No.5 Reactor | Pinned 112 | — |  |
| `smkin_3` | No.5 Reactor | Pinned 112 | — |  |
| `smkin_4` | No.5 Reactor / No.1 Reactor | Pinned 112 | 27–27 (1) |  |
| `smkin_5` | No.5 Reactor | Pinned 112 | 15–123 (5) | Reactor 5 bomb room; Air Buster is in southmk2. |
| `southmk1` | No.5 Reactor | Pinned 112 | — |  |
| `southmk2` | — | Pinned 112 | — |  |
| `mds7st1` | Train Graveyard | Pinned 110 | 212–212 (1) |  |
| `mds7st2` | Train Graveyard | Pinned 110 | 69–212 (2) |  |
| `mds7st3` | Sector 7 Station | Pinned 110 | 63–251 (5) |  |
| `mds7st32` | — | Pinned 110 | 251–251 (1) |  |
| `mds7_w1` | Sector 7 Weapon Shop | Pinned 110 | 108–108 (1) | Sector 7 weapon shop. Barret recruitment NPC to be added here. |
| `mds7_w2` | Beginner's Hall / Sector 7 Slums | Pinned 110 | 108–108 (1) |  |
| `mds7_w3` | Sector 7 Slums | Pinned 110 | 69–212 (3) |  |
| `mds7` | Sector 7 Slums | Pinned 110 | 63–108 (6) |  |
| `mds7_im` | Sector 7 Item Store | Pinned 110 | — |  |
| `min71` | Johnny's Home | Pinned 110 | 90–108 (2) |  |
| `mds7pb_1` | 7th Heaven | Pinned 110 | 69–105 (8) | 7th Heaven. At 110 Tifa has left with the party in the original; Tifa recruitment NPC to be added here. |
| `mds7pb_2` | AVALANCHE Hideout | Pinned 110 | — |  |
| `mds7plr1` | Sector 7 Slums | Pinned 110 | 63–221 (6) | Pillar base. Plate-fall events (212+) will not fire. |
| `mds7plr2` | Sector 7 Mechanized Tower | Pinned 110 | 215–215 (1) |  |
| `pillar_1` | — | Pinned 110 | — |  |
| `pillar_2` | — | Pinned 110 | — |  |
| `pillar_3` | — | Pinned 110 | — | Pillar top, Reno fight (boss system later). |
| `mds5_1` | Sector 5 Slum | Pinned 177 | 173–1008 (5) |  |
| `mds5_2` | Sector 5 Slum | Pinned 177 | 158–1008 (5) |  |
| `mds5_3` | Sector 5 Slum | Pinned 177 | 173–173 (1) |  |
| `mds5_4` | Sector 5 Slum | Pinned 177 | — |  |
| `mds5_dk` | Earthen Pipe | Pinned 177 | 236–305 (2) | Earthen pipe. Checks >=236 / >305; at 177 it is in its early state. Needs testing. |
| `mds5_w` | Weapon Store | Pinned 177 | 173–1008 (4) |  |
| `mds5_i` | Item Store | Pinned 177 | 236–236 (1) |  |
| `mds5_m` | Materia store | Pinned 177 | 236–1008 (2) |  |
| `min51_1` | House 1f. | Pinned 177 | 185–1008 (6) |  |
| `min51_2` | House 2f. | Pinned 177 | 236–1008 (2) |  |
| `church` | Church | Pinned 177 | 155–155 (1) |  |
| `chrin_1a` | church in the slums | Pinned 177 | 158–673 (2) | Church interior. Aerith recruitment NPC to be added here. |
| `chrin_1b` | church in the slums | Pinned 177 | — |  |
| `chrin_2` | Inside the Church | Pinned 177 | 152–155 (2) |  |
| `chrin_3a` | Church Roof | Pinned 177 | — |  |
| `chrin_3b` | Church Roof | Pinned 177 | — |  |
| `eals_1` | {AERIS}'s House | Pinned 177 | 170–385 (5) |  |
| `ealin_1` | {AERIS}'s House | Pinned 177 | 158–1008 (10) | Aerith's house. Elmyra scenes at 158-170 will not fire. |
| `ealin_12` | — | Pinned 177 | 158–1008 (8) |  |
| `ealin_2` | {AERIS}'s House | Pinned 177 | 164–257 (5) |  |
| `mds6_1` | Sector 6 | Pinned 186 | 236–245 (3) |  |
| `mds6_2` | Sector 6 park | Pinned 186 | 176–176 (1) | Sector 6 park (Aerith/Cloud scene 176-185 will not fire). |
| `mds6_22` | Sector 6 park | Pinned 186 | 236–341 (2) |  |
| `mds6_3` | Sector 6 | Pinned 186 | 236–236 (1) |  |
| `mds5_5` | Slum Outskirts | Pinned 342 | 335–1195 (4) | Exit to the world map (gateway to wm0). Party-gathering scene (335/336) will not fire. |
| `mrkt1` | Wall Market | Region `wall_market` (starts 188) | 192–257 (3) |  |
| `mrkt2` | Wall Market | Region `wall_market` (starts 188) | 188–999 (5) |  |
| `mrkt3` | Honey Bee Inn | Region `wall_market` (starts 188) | 188–1008 (5) |  |
| `mrkt4` | Wall Market | Region `wall_market` (starts 188) | 192–999 (4) |  |
| `mkt_w` | Weapon Store | Region `wall_market` (starts 188) | 192–999 (3) |  |
| `mkt_mens` | Men's Hall | Region `wall_market` (starts 188) | 192–999 (3) |  |
| `mkt_ia` | Item Store | Region `wall_market` (starts 188) | 192–999 (2) |  |
| `mktinn` | Inn | Region `wall_market` (starts 188) | 192–999 (3) |  |
| `mkt_m` | Materia Store | Region `wall_market` (starts 188) | 191–239 (3) |  |
| `mkt_s1` | Boutique | Region `wall_market` (starts 188) | 191–192 (2) |  |
| `mkt_s2` | Diner | Region `wall_market` (starts 188) | 192–236 (2) |  |
| `mkt_s3` | Pharmacy | Region `wall_market` (starts 188) | 192–236 (2) |  |
| `mktpb` | Bar | Region `wall_market` (starts 188) | 192–236 (2) |  |
| `onna_2` | Honey Bee Inn | Region `wall_market` (starts 188) | — |  |
| `onna_4` | Honey Bee Inn | Region `wall_market` (starts 188) | — |  |
| `onna_5` | Honey Bee Inn | Region `wall_market` (starts 188) | — |  |
| `onna_52` | Honey Bee Inn | Region `wall_market` (starts 188) | — |  |
| `colne_1` | Corneo Hall | Region `wall_market` (starts 188) | 190–192 (2) |  |
| `colne_2` | Corneo Hall,1f. | Region `wall_market` (starts 188) | 192–197 (2) |  |
| `colne_3` | Corneo Hall,2f. | Region `wall_market` (starts 188) | — |  |
| `colne_4` | Torture Room | Region `wall_market` (starts 188) | — |  |
| `colne_5` | Corneo Hall,2f. | Region `wall_market` (starts 188) | — |  |
| `colne_6` | Corneo Hall,2f. | Region `wall_market` (starts 188) | — |  |
| `colne_b1` | Sewer | Region `wall_market` (starts 188) | 206–209 (2) |  |
| `colne_b3` | Sewer | Region `wall_market` (starts 188) | — |  |

## Not handled yet

| Area | Fields | Why |
|---|---|---|
| Sector 1 platform | `md1stin` | Holds the new-game handler; left on the global value (100), which is past its events. |
| Shinra HQ | `blin*`, `blinst_*`, `blinele`, `eleout`, `md0`, `sinbil_*` | The infiltration (257–326) is built around the full party (captures, escape). Needs its own design: an explorable state, keycards, Red XIII in the lab. |
| Trains | `tin_*`, `cargoin`, `rootmap` | Story-only vehicle scenes. Decide whether trains become transport between sectors. |
| Sector 4 plate interior | `sbwy4_*`, `wcrimb_*` | No story checks; reachable only through story routes. Check access in testing. |
| Highway | `roadend`, motorcycle chase | Motorcycle chase becomes a repeatable minigame (Shinra HQ showroom). |
| Disc 2 Midgar | `md8_5`, `md8_6`, `md8_b*`, `md8brdg2`, `md8_32`, `md8_52`, `canon_*`, `tunnel_4`–`tunnel_6`, `sbwy4_22` | Sister Ray assault areas; Proud Clod and Hojo. Later pass. |

## Known risks to check in testing

- **Story barriers that are not progress checks** (guards, locked doors, "can't go back" lines) still exist. They need finding in testing and removing one by one.
- **Party members drawn by scripts**: some fields show Barret/Tifa/Aerith models depending on the story moment. At the chosen moments most of these are gone, but recruitment NPCs are not added yet.
- **Wall Market quest** still assumes Aerith and Tifa (dress-up, Corneo). Playable as in the original for now; reworking it for whoever is in the party is a separate task.
- **Train Graveyard and sewers** link Wall Market, the pillar and Sector 7; they are pinned to 110 / in the Wall Market region respectively.

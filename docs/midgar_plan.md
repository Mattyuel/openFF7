# Midgar plan (for review)

How each Midgar field is detached from the global story value (generated from
`patches/100_midgar.py` and `docs/inventory/fields.csv`). **Pinned M**: the field
always behaves as at story moment M, chosen between its story events so its
cutscenes do not fire.

Wall Market is fixed just after the dress-up step, so the dress-up sequence never
plays. Shinra HQ floors are fixed in their infiltration state without the capture
and escape events; the new game holds all keycards (60, 62, 65, 66, 68) and the
top elevator access, so every floor can be reached. Random encounters are the
original infiltration ones (the building is reached through the Wall Market wire
climb -> Sector 0 -> HQ entrance).

| Field | Location | Moment | Story checks in field | Notes |
|---|---|---|---|---|
| `md1_1` | Sector 1 Station | 20 | 7–7 (1) |  |
| `md1_2` | Sector 1 | 20 | 8–8 (1) |  |
| `nrthmk` | No.1 Reactor | 20 | 10–27 (2) |  |
| `nmkin_1` | No.1 Reactor | 20 | 10–27 (3) |  |
| `nmkin_2` | No.5 Reactor / No.1 Reactor | 20 | 13–27 (2) |  |
| `nmkin_3` | No.5 Reactor / No.1 Reactor | 20 | 14–27 (2) |  |
| `nmkin_4` | No.5 Reactor / No.1 Reactor | 20 | 27–27 (1) |  |
| `nmkin_5` | No.5 Reactor / No.1 Reactor | 20 | 15–123 (5) | Guard Scorpion room. Bomb/timer events (27+) do not fire; boss added later. |
| `elevtr1` | No.5 Reactor / No.1 Reactor | 20 | 12–33 (3) |  |
| `md8_1` | Sector 8 | 46 | 33–45 (2) |  |
| `md8_2` | — | 46 | 36–39 (2) |  |
| `md8_3` | — | 46 | — |  |
| `md8_4` | — | 46 | 33–33 (1) |  |
| `md8brdg` | Sector 8 | 46 | 39–39 (1) |  |
| `tunnel_1` | Winding Tunnel | 112 | — |  |
| `tunnel_2` | Winding Tunnel | 112 | — |  |
| `tunnel_3` | Winding Tunnel | 112 | — |  |
| `smkin_1` | — | 112 | 127–128 (2) |  |
| `smkin_2` | No.5 Reactor | 112 | — |  |
| `smkin_3` | No.5 Reactor | 112 | — |  |
| `smkin_4` | No.5 Reactor / No.1 Reactor | 112 | 27–27 (1) |  |
| `smkin_5` | No.5 Reactor | 112 | 15–123 (5) |  |
| `southmk1` | No.5 Reactor | 112 | — |  |
| `southmk2` | — | 112 | — |  |
| `mds7st1` | Train Graveyard | 110 | 212–212 (1) |  |
| `mds7st2` | Train Graveyard | 110 | 69–212 (2) |  |
| `mds7st3` | Sector 7 Station | 110 | 63–251 (5) |  |
| `mds7st32` | — | 110 | 251–251 (1) |  |
| `mds7_w1` | Sector 7 Weapon Shop | 110 | 108–108 (1) | Sector 7 weapon shop. Barret recruitment to be added here. |
| `mds7_w2` | Beginner's Hall / Sector 7 Slums | 110 | 108–108 (1) |  |
| `mds7_w3` | Sector 7 Slums | 110 | 69–212 (3) |  |
| `mds7` | Sector 7 Slums | 110 | 63–108 (6) |  |
| `mds7_im` | Sector 7 Item Store | 110 | — |  |
| `min71` | Johnny's Home | 110 | 90–108 (2) |  |
| `mds7pb_1` | 7th Heaven | 110 | 69–105 (8) | 7th Heaven. Tifa recruitment to be added here. |
| `mds7pb_2` | AVALANCHE Hideout | 110 | — |  |
| `mds7plr1` | Sector 7 Slums | 110 | 63–221 (6) | Pillar base. Plate-fall events (212+) do not fire. |
| `mds7plr2` | Sector 7 Mechanized Tower | 110 | 215–215 (1) |  |
| `pillar_1` | — | 110 | — |  |
| `pillar_2` | — | 110 | — |  |
| `pillar_3` | — | 110 | — | Pillar top, Reno fight (boss added later). |
| `mds5_1` | Sector 5 Slum | 177 | 173–1008 (5) |  |
| `mds5_2` | Sector 5 Slum | 177 | 158–1008 (5) |  |
| `mds5_3` | Sector 5 Slum | 177 | 173–173 (1) |  |
| `mds5_4` | Sector 5 Slum | 177 | — |  |
| `mds5_dk` | Earthen Pipe | 177 | 236–305 (2) | Earthen pipe; early state at 177. Needs testing. |
| `mds5_w` | Weapon Store | 177 | 173–1008 (4) |  |
| `mds5_i` | Item Store | 177 | 236–236 (1) |  |
| `mds5_m` | Materia store | 177 | 236–1008 (2) |  |
| `min51_1` | House 1f. | 177 | 185–1008 (6) |  |
| `min51_2` | House 2f. | 177 | 236–1008 (2) |  |
| `church` | Church | 177 | 155–155 (1) |  |
| `chrin_1a` | church in the slums | 177 | 158–673 (2) | Church interior. Aerith recruitment to be added here. |
| `chrin_1b` | church in the slums | 177 | — |  |
| `chrin_2` | Inside the Church | 177 | 152–155 (2) |  |
| `chrin_3a` | Church Roof | 177 | — |  |
| `chrin_3b` | Church Roof | 177 | — |  |
| `eals_1` | {AERIS}'s House | 177 | 170–385 (5) |  |
| `ealin_1` | {AERIS}'s House | 177 | 158–1008 (10) | Aerith's house. Elmyra scenes (158-170) do not fire. |
| `ealin_12` | — | 177 | 158–1008 (8) |  |
| `ealin_2` | {AERIS}'s House | 177 | 164–257 (5) |  |
| `mds6_1` | Sector 6 | 186 | 236–245 (3) |  |
| `mds6_2` | Sector 6 park | 186 | 176–176 (1) | Sector 6 park scene (176-185) does not fire. |
| `mds6_22` | Sector 6 park | 186 | 236–341 (2) |  |
| `mds6_3` | Sector 6 | 186 | 236–236 (1) |  |
| `mds5_5` | Slum Outskirts | 342 | 335–1195 (4) | Exit to the world map. Party-gathering scene (335/336) does not fire. |
| `mrkt1` | Wall Market | 193 | 192–257 (3) |  |
| `mrkt2` | Wall Market | 193 | 188–999 (5) | Wall Market. Dress-up (192) and arrival (188) scenes do not fire. |
| `mrkt3` | Honey Bee Inn | 193 | 188–1008 (5) |  |
| `mrkt4` | Wall Market | 193 | 192–999 (4) |  |
| `mkt_w` | Weapon Store | 193 | 192–999 (3) |  |
| `mkt_mens` | Men's Hall | 193 | 192–999 (3) |  |
| `mkt_ia` | Item Store | 193 | 192–999 (2) |  |
| `mktinn` | Inn | 193 | 192–999 (3) |  |
| `mkt_m` | Materia Store | 193 | 191–239 (3) |  |
| `mkt_s1` | Boutique | 193 | 191–192 (2) |  |
| `mkt_s2` | Diner | 193 | 192–236 (2) |  |
| `mkt_s3` | Pharmacy | 193 | 192–236 (2) |  |
| `mktpb` | Bar | 193 | 192–236 (2) |  |
| `onna_2` | Honey Bee Inn | 193 | — |  |
| `onna_4` | Honey Bee Inn | 193 | — |  |
| `onna_5` | Honey Bee Inn | 193 | — |  |
| `onna_52` | Honey Bee Inn | 193 | — |  |
| `colne_1` | Corneo Hall | 193 | 190–192 (2) | Corneo's mansion. Dress-up/audition events do not fire; Corneo is on the bed in his bedroom (`colne_6`, see `patches/110_corneo.py`); the 2f hall copy of him is hidden. |
| `colne_2` | Corneo Hall,1f. | 193 | 192–197 (2) |  |
| `colne_3` | Corneo Hall,2f. | 193 | — |  |
| `colne_4` | Torture Room | 193 | — |  |
| `colne_5` | Corneo Hall,2f. | 193 | — |  |
| `colne_6` | Corneo Hall,2f. | 193 | — |  |
| `colne_b1` | Sewer | 193 | 206–209 (2) | Sewer, Aps fight (boss added later). |
| `colne_b3` | Sewer | 193 | — |  |
| `md0` | sector 0 | 263 | 1008–1008 (1) | Sector 0: route from the Wall Market wire climb to the HQ entrance. |
| `sinbil_1` | Shinra Bldg. | 263 | 1008–1008 (1) |  |
| `sinbil_2` | Shinra Bldg. | 263 | — |  |
| `blinst_1` | Shinra Bldg. Stairs | 263 | 1008–1008 (1) |  |
| `blinst_2` | Shinra Bldg. Stairs | 263 | 1008–1008 (1) |  |
| `blinst_3` | Shinra Bldg. Stairs | 263 | — |  |
| `blin59` | Shinra Bldg. 59f. | 263 | 260–263 (2) | Keycard 60 pickup event does not fire (all keycards given at new game). |
| `blinele` | Elevator | 263 | 263–263 (1) |  |
| `eleout` | Outside Elevator | 263 | 263–311 (3) |  |
| `blin60_1` | Shinra Bldg. 60f. | 263 | 1008–1008 (1) |  |
| `blin60_2` | Shinra Bldg. 60f. | 263 | — |  |
| `blin61` | Shinra Bldg. 61f. | 263 | 1008–1008 (1) |  |
| `blin62_1` | Shinra Bldg. 62f. | 263 | 1008–1008 (1) |  |
| `blin62_2` | Shinra Bldg. 62f. | 263 | — |  |
| `blin62_3` | — | 263 | — |  |
| `blin63_1` | Shinra Bldg. 63f. | 263 | 1008–1008 (1) |  |
| `blin63_t` | Shinra Bldg. 63f. | 263 | 1008–1008 (1) |  |
| `blin64` | Shinra Bldg. 64f. | 263 | 1008–1008 (1) |  |
| `blin65_1` | Shinra Bldg. 65f. | 263 | 1008–1008 (1) |  |
| `blin65_2` | Shinra Bldg. 65f. | 263 | 1008–1008 (1) |  |
| `blin1` | Shinra Bldg. 1f. lobby | 261 | 257–326 (3) | Lobby. Arrival (257) and escape (326) events do not fire. |
| `blin2` | Shinra Bldg. 2f. Lobby | 261 | 326–326 (1) |  |
| `blin2_i` | Shinra Bldg. 2f. Shop | 261 | 326–1008 (2) |  |
| `blin3_1` | Shinra Bldg. 3f. Lobby | 261 | 326–326 (1) |  |
| `blin66_1` | — | 271 | 264–302 (5) | Meeting eavesdrop (264-270) does not fire. |
| `blin66_2` | — | 271 | 266–269 (2) |  |
| `blin66_3` | — | 271 | — |  |
| `blin66_4` | — | 271 | 267–267 (1) |  |
| `blin66_5` | — | 271 | 266–267 (2) |  |
| `blin67_1` | — | 281 | 271–302 (6) | Hojo's lab. Specimen/Aerith events do not fire. Red XIII recruitment to be added. |
| `blin671b` | — | 281 | 272–335 (3) |  |
| `blin67_3` | — | 281 | 273–284 (3) |  |
| `blin673b` | — | 281 | 335–335 (1) |  |
| `blin67_4` | — | 281 | — |  |
| `blin67_2` | — | 297 | 293–305 (4) |  |
| `blin68_1` | — | 285 | 278–1008 (4) |  |
| `blin68_2` | — | 285 | 278–302 (3) | Sample:H0512 fight (boss added later). |
| `blin69_1` | Shinra Bldg. 69f. | 303 | 284–1008 (8) | Capture/prison events (284-326) do not fire. |
| `blin70_1` | Shinra Bldg. 70f. | 303 | 203–320 (5) |  |
| `blin70_2` | Shinra Bldg. 70f. | 303 | 203–341 (5) |  |
| `blin70_3` | Shinra Bldg. 70f. | 303 | 305–320 (3) | Roof, Rufus fight (boss added later). |

## Not handled yet

| Area | Fields | Why |
|---|---|---|
| Sector 1 platform | `md1stin` | Holds the new-game handler; on the global value (100), past its events. |
| Trains | `tin_*`, `cargoin`, `rootmap` | Story-only scenes. Decide whether trains become transport between sectors. |
| Sector 4 plate interior | `sbwy4_*`, `wcrimb_*` | No story checks; check access in testing. |
| Highway | `roadend`, motorcycle chase | Becomes a repeatable minigame (Shinra HQ showroom). |
| Shinra HQ, later discs | `blin66_6`, `blin70_4` | Disc 2/3 versions of rooms; not part of the explorable building. |
| Disc 2 Midgar | `md8_5`, `md8_6`, `md8_b*`, `md8brdg2`, `md8_32`, `md8_52`, `canon_*`, `tunnel_4`–`tunnel_6`, `sbwy4_22` | Sister Ray assault areas; Proud Clod and Hojo. Later pass. |

## Known risks to check in testing

- **Story barriers that are not progress checks** (guards, locked doors, "can't go back" lines) still exist. They need finding in testing and removing one by one.
- **Shinra HQ moments are per floor** and chosen from the data only; some floors may show leftover infiltration NPCs or block a door that expects an earlier event.
- **Party members drawn by scripts**: some rooms show Barret/Tifa/Aerith models depending on the moment. Recruitment NPCs are not added yet.

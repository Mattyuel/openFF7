# One-off story scenes outside Midgar (audit)

Static reading + `ff7tool.py scenes`-style simulation (new-game flags, every
enabled LINE's scripts run once). Nothing tested in game. Applied fixes are in
`patches/_config.py` (`INITIAL_EVENT_FLAGS`) and `patches/world_overrides.json`.

## Applied
| Scene | Where / trigger | Fix |
|---|---|---|
| Midgar Zolom impaled ("Did Sephiroth… do this?") | wm0 map cell 0xAA23 (next to the mine entrance 0xAA24): if bit 0xE7B clear and on foot / wild chocobo, `enter_field 0x20` -> field `sichi` (scene in its init, unconditional; its exit LINEs set the bit). Snake is part of sichi's background. | (3,207,3) |
| Buggy breakdown (wm messages 34-36) | wm0 cell 0xADA0 near Cosmo Canyon: buggy fn 0x4612 if 0xE79 clear; while 0xE79 set and 0xE7A clear it stays broken (fn 0x4604). cos_btm2 sets both after the repair. | (3,207,1) + (3,207,2) |
| Nibelheim arrival | nivl_3 LINE F_NIVL script 2, gated by (3,20,2) | (3,20,2) |
| Barret's North Corel flashback | ropest LINE evline2, gated by (1,128,0) | (1,128,0) |
| Mideel arrival (Tifa) | itown1a LINE line01 script 5, (15,177) bit 1 | (15,177,1) |
| Gongaga "A ruined reactor." | gongaga LINE line5 (3,132,2); gnmk LINE line1 (3,129,4) | both |
| Icicle Inn Elena ambush | snow LINE snowbd, (1,130,0); (1,130,7) releases guards/locked triangles | both (medium confidence) |
| Nibelheim area pinned to the flashback | niv_cl, mtnvl2-4, nvdun2, nvdun31, mtnvl6, mtnvl6b, nvmkin1/21/22, sinin2_1, sininb31/41/51 were pinned <= 384 (flashback: flashback encounters, hidden chests, exits to the flashback town `nivl`) | pinned to 678 (present day) |

World map bit b = savemap 0x0BA4 + b//8, bit b%8: 0xE78+n = bank 2 offset 207 bit n.
`docs/inventory/worldmap.md`'s "Called from" column is off by one: `enter_field N`
= field.tbl entry N-1 (same numbering as `push_special 6`); e.g. 0xAA24 = wm3 psdun_2,
0xAC54 = wm4 psdun_1, 0xAA23 = wm31 sichi.

## Applied after review (user decisions)
- Mideel: always the disc 3 version (wm0 cell 0xB7A4 picks itown1b; `410_world_fixes`).
- Yuffie's house: flag (3,190,2) set (also shows Yuffie in yufy2).
- Cargo ship: (3,185,1) set; shpin_3 ELINE (Jenova BIRTH) turned off in code.
- Corel Prison: jail1 pinned 464 (exits need >= 454).
- Junon: the `aho` line always takes you up the elevator (junin7).
- Gate of Naught: always open (cosin2 opening runs on entry).

## Not applied (need a decision or more checking)
- `ithos` (Mideel clinic): still has its disc-2 scene but is no longer reached
  (the world map sends you to the disc 3 Mideel, itown1b).
- Optional world-map tutorials: buggy (13,133,5), Tiny Bronco (13,134,0), chocobo (13,134,2).
- Not covered: talk-triggered scenes, triangle checks in loops, party other than Cloud,
  Highwind fields, fields only reachable via story jumps.

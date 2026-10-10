# Testing a build

The build runs on any machine with Python 3 (no extra packages).

## 1. Build

From the repo folder:

```
python tools/ff7tool.py build
```

This writes `build/openFF7/` (a full copy of the game folder with the patched
files). The build prints which game files changed; right now that is only
`data/field/flevel.lgp`. (If you copied a `KERNEL.BIN` from an earlier build,
restore the original; it is no longer changed.)

## 2. Install the changed file into Steam (for now)

The separate `build/openFF7` folder has not been tested to start on its own
(see `docs/exe_notes.md`), so for now test inside the Steam install:

1. In the Steam folder (`...\steamapps\common\FINAL FANTASY VII\`), for each
   changed file: rename the original (e.g. `data\field\flevel.lgp` ->
   `flevel.lgp.original`, `data\lang-en\kernel\KERNEL.BIN` ->
   `KERNEL.BIN.original`) and copy the built one from `build\openFF7\` there.
2. Start the game from Steam and choose **New Game**.

To undo: delete the copied files and rename the `.original` files back.
Steam's "Verify integrity of game files" also restores it.

Existing saves load, but they keep their own story progress; use a new game.

## 3. What to check (current build)

- New game skips the opening and starts with Cloud alone at street level in
  front of the Sector 7 station with the slums theme playing; menu (including
  PHS) is available. Walking up to the train should no longer board it.
- Entering the Sector 7 slums should no longer play the AVALANCHE / Barret /
  Tifa arrival scene, and Barret should not be on the station platform.
- **Recruit Tifa** in 7th Heaven: talk to her, choose "Come with me, Tifa."
  She should join the party, appear in the PHS and leave the bar. Choosing
  "Not right now." leaves her there. Check her level after joining.
- **Recruit Aerith** in the Sector 5 church: she is at the flower bed. Same
  as Tifa. Check her position and pose look right.
- Cloud's name should be "Cloud" (not "Ex-SOLDIER") from the very start, and Key Items / Items
  should include three **Batteries**.
- **Corneo's mansion**: the doorman is gone and you can walk in. On the
  ground floor the office door (upstairs) and the dungeon door are open. No
  scenes should play anywhere in the mansion: right-hand room (lackey
  fight), dungeon (Tifa/Aerith, Kotch chase), office door (Aerith "No!"),
  upstairs office (bride choice) or bedroom. Corneo is not in the mansion.
- **Wire climb to Shinra HQ**: in Wall Market's back street (where the wire
  hangs from the plate) you can now start climbing. Use the batteries on the
  way up; at the top (Plate Section -> Sector 0 -> Shinra HQ) no cutscenes
  should play.
- **Sector 7 <-> Sector 6 gate**: on the Sector 7 screen with the two guards
  (in front of the pillar), the guards now stand either side of the passage.
  Walk down the passage to reach the Sector 6 playground. There the giant
  gate is open; walk through it to come back to the guard screen. Check the
  gate halves look open (not floating or clipping) and nothing blocks you.
- **Shinra HQ 2f shop**: the two treasure boxes can be opened (Pile Bunker
  and the other item); the assistant no longer stops you.
- **Recruit Barret** on Mt. Corel, on the railway screen just after the
  Corel Reactor (needs the world map to get there). Check his model and that
  he stands on the tracks, not in the air or inside the rails.
- **Kalm**: entering the town, the inn and the houses should play no
  arrival scene, flashback or story dialogue.
- **Rest of the world** (first automatic pass, `docs/world_plan.md`): every
  town and dungeon should be in a quiet, after-the-story state. Expect some
  leftovers; report the location and what played.
- **Train Graveyard**: the three movable trains start in their moved
  positions every time you enter, so you can cross the graveyard in both
  directions. Climbing the ladder out should play no Aerith scene. If the
  way is still blocked, say which screen and where.
- If Tifa (7th Heaven) or Aerith (church) are missing, start a **new game**:
  a save made with the build from two updates ago carries flags that hid
  them.
- **Train travel**: at the Sector 7 station walk into the train door: a menu
  offers Upper Midgar (Sector 8 bridge), No. 1 Reactor (Sector 1 platform)
  and No. 5 Reactor (the tunnel after jumping off the train). At each
  destination a Train Attendant stands next to where you arrive and takes
  you back to Sector 7.
- **No. 1 Reactor**: walk from the platform through Sector 1 into the
  reactor; all gates/doors should be open with no scenes. Guard Scorpion
  (a stand-in robot) waits at the core: talk to it to fight. After winning
  it is gone. The reactor entrance also leads out to Upper Midgar.
- **No. 5 Reactor**: tunnel -> plate interior -> reactor; the three-button
  door is already open. On the bridge outside, Air Buster (same stand-in
  robot) waits: talk to it to fight.
- Known still to do: the
  Sector 6 sewer (Aps), the Reno pillar fight.
- Walk around Sector 7 slums, 7th Heaven, the weapon/item shops, Train
  Graveyard, the pillar, Sector 6, Wall Market, Sector 5, the church and
  Aerith's house. Note anywhere you are blocked, a cutscene plays, or the game
  freezes or crashes, with the location name and what you did just before.
- Wall Market (incl. Honey Bee Inn and Corneo's mansion) should have no
  dress-up or other cutscenes.
- Corneo's mansion: walk to his bedroom (2f, through the hall). He should be on
  the bed; talking to him shows "A man!? What's goin' on?", then he runs toward
  the door and vanishes. Re-enter the room: he should stay gone. Note if he
  glides instead of running, faces the wrong way, or runs somewhere odd.
- Shinra HQ: reach it via the Wall Market wire climb -> Sector 0 -> HQ entrance.
  You hold all keycards (check Key Items); every floor should be reachable by
  stairs/elevator, with infiltration random encounters and no capture/escape
  scenes.
- Leave Midgar through the Sector 5 church exterior -> Slum Outskirts -> the
  gate (now unlocked; you also hold the Key to Sector 5) -> world map.
  Walking back to the gate from the world map re-enters Midgar.

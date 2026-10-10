# Testing a build

The build runs on any machine with Python 3 (no extra packages).

## 1. Build

From the repo folder:

```
python tools/ff7tool.py build
```

This writes `build/openFF7/` (a full copy of the game folder with the patched
files). Right now only `data/field/flevel.lgp` changes.

## 2. Install the changed file into Steam (for now)

The separate `build/openFF7` folder has not been tested to start on its own
(see `docs/exe_notes.md`), so for now test inside the Steam install:

1. In the Steam folder (`...\steamapps\common\FINAL FANTASY VII\data\field\`),
   rename `flevel.lgp` to `flevel.lgp.original`.
2. Copy `build\openFF7\data\field\flevel.lgp` there.
3. Start the game from Steam and choose **New Game**.

To undo: delete the copied `flevel.lgp` and rename `flevel.lgp.original` back.
Steam's "Verify integrity of game files" also restores it.

Existing saves load, but they keep their own story progress; use a new game.

## 3. What to check (current build)

- New game skips the opening and starts with Cloud alone at street level in
  front of the Sector 7 station with the slums theme playing; menu (including
  PHS) is available. Walking up to the train should no longer board it.
- Entering the Sector 7 slums should no longer play the AVALANCHE / Barret /
  Tifa arrival scene. Known still to do: Tifa and Barret in 7th Heaven (to be
  replaced by Tifa's recruitment), the church (Aerith), Air Buster's reactor
  entrance, the Sector 6 sewer (Aps), the Reno pillar fight.
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
- Leave Midgar through the Sector 5 church exterior -> Slum Outskirts -> world map.

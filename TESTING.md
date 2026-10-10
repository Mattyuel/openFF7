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

- New game skips the opening and starts with Cloud alone on the Sector 7
  station platform; menu (including PHS) is available.
- Walk around Sector 7 slums, 7th Heaven, the weapon/item shops, Train
  Graveyard, the pillar, Sector 6, Wall Market, Sector 5, the church and
  Aerith's house. Note anywhere you are blocked, a cutscene plays, or the game
  freezes or crashes, with the location name and what you did just before.
- Leave Midgar through the Sector 5 church exterior -> Slum Outskirts -> world map.

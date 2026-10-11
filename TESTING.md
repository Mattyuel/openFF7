# Testing a build

The build runs on any machine with Python 3 (no extra packages).

## 1. Build

From the repo folder:

```
python tools/ff7tool.py build
```

This writes `build/openFF7/` (a full copy of the game folder with the patched
files). The build prints which game files changed and their sizes; right now
that is `data/field/flevel.lgp`, `data/lang-en/kernel/KERNEL.BIN`,
`data/lang-en/kernel/kernel2.bin`, `data/wm/world_us.lgp` and `ff7_en.exe`
(whichever the build lists). Copy all of them, and
check the sizes in the Steam folder match what the build printed (Steam can
silently restore original files; the original flevel.lgp is 128,204,987 bytes).

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
- Cloud starts at **level 1** (Str 14, Vit 11, Mag 13, Spr 11, Dex 6, Luck 15,
  HP 219, MP 18, EXP 0) and should reach level 2 after a few battles.
- If a new game goes to a **black screen**, try again with the original
  `KERNEL.BIN` (keep the new `flevel.lgp`) and say whether that fixes it.
- **PHS**: the menu entry is hidden until you have recruited two others
  (3 characters), then it appears and works at save points. (The game won't
  let you leave the PHS with fewer than 3 in the party.) Needs a new game.
- **Sector 4 duct** (end of the train tunnel to No.5): pressing [OK] at the
  duct gives "Go down." / "Not now." with no Barret/Tifa. In the next room,
  climb the ladder into the vent; at its far end (or walking onto that spot)
  choose "Drop down." (onward) or "Climb back to the train tunnel." Note if
  the vent menu pops up repeatedly while you stand there.
- **Chocobo rides**: on the Midgar slum outskirts screen (where you enter
  from the world map) Choco Billy and a chocobo stand next to you; same on the
  first Mythril Mine screen (entrance from the marsh side, psdun_1). Talk to
  either: "Ride a chocobo? 100 gil." With under 100 gil Billy says so; with
  enough, 100 gil is taken and you should be on the world map riding a
  (yellow) chocobo, as after catching one in battle. Dismount: it should run
  away. You should now appear outside Midgar / the Mythril Mine on the
  chocobo (before, you appeared in the sea at the top-left corner).
- No "Saving on the World Map" window on first entering the world map, and no
  submarine tutorial window (new game).
- Cloud always leads (he can't be moved in the PHS; needs a new game).
- If you installed the Tame test files earlier: put back the original
  `data\lang-en\kernel\kernel2.bin` (the build no longer changes it).
  `ff7_en.exe` is built again (quest kill counting): copy the new one.
- **World quests** (new game; untested): a quest giver with an orb in Kalm,
  the Chocobo Farm, Mythril Mine (first screen), Fort Condor, the beach
  under Junon, Costa del Sol, Mt. Corel (first screen), North Corel inn,
  Gold Saucer gate, Corel Prison, Gongaga, Cosmo Canyon (house), Nibelheim,
  Rocket Town, Wutai, Temple of the Ancients (entrance), Bone Village,
  Forgotten City, Icicle Inn (inn), Mideel (disc 3) and the foot of Gaea's
  Cliff. Quests use local enemies and drops; some chains end in a boss:
  Bottomswell (Junon beach), Dyne (prison junkyard), Reno & Rude (Gongaga
  jungle path), Materia Keeper (Mt. Nibel caves), Palmer (Rocket Town launch
  pad), Rapps (Da-chao), Red Dragon and Demons Gate (temple), Jenova-LIFE
  (Forgotten City altar). Once the boss quest is accepted, walking to the
  boss's spot starts the fight; leaving and re-entering the screen allows
  another fight. Report givers in awkward spots, boss lines that don't
  trigger or trigger in the wrong place, and any crash on a boss fight.
- **Fixes from the last test** (new game recommended):
  Andrea stands; Gwen (Potions) and Zhije (Hedgehog Pies) swapped places;
  Ms Folia is on the garden screen next to Aerith's house; the Old Man is on
  the church screen; Sam stands left of Bessie; the quest list shows 8 rows;
  the Honey Bee Inn door is no longer blocked; a ghost stands left of where
  you enter the playground from Sector 7; Cloud should arrive at the right
  spot on the Junon airstrip.
- **Cargo ship**: no party members to swap on the upper deck; the First
  Mate (upper deck, second screen) offers to put you ashore at Costa del
  Sol; Deckhand Moe's quests end with Jenova BIRTH, fought by walking to the
  dead guard in the engine room (once per visit, also before/after the quest).
- **Every quest reward** now includes Sources (1 in Midgar).
- openFF7's own flags moved to new save bytes: start a new game (old saves
  lose recruit/boss flags).
- **Fewer story scenes** (new game): no Midgar Zolom scene approaching the
  Mythril Mine; the buggy never breaks down near Cosmo Canyon; no arrival
  scenes in Nibelheim, Mideel, the Gold Saucer ropeway (Barret flashback),
  Gongaga's reactor; no Elena ambush at Icicle Inn. Nibelheim's surroundings
  (Mt. Nibel, reactor, mansion basement) should be the present day, not the
  flashback (no flashback battles, chests visible, Mt. Nibel leads to the
  real Nibelheim).
- **Opened up**: Mideel is the disc 3 (ruined) version; the cargo ship has no
  stowaway or Jenova scene; Corel Prison's exits let you out without Barret;
  the Junon elevator line takes you up instead of a guard blocking it; the
  Gate of Naught (Cosmo Canyon) is open. Yuffie's "Follow me" scene in Wutai
  is skipped (she may be visible in the next house).
- **Choco Billy** outside Midgar stands a little lower, faces down, and he and
  his chocobo turn to you when talked to.
- **Sounds**: quest rewards play the item chime (materia rewards the materia
  chime); recruiting Tifa/Aerith/Barret plays the materia chime.
- **Quests** (new game needed for clean quest state). A spinning materia orb
  should float above each quest giver: yellow = a quest to offer, blue =
  ready to hand in, none otherwise. Givers turn to face you when talked to.
  Orbs were lowered (too high before): report if they now sit in the head.
  - *Middle Manager* (Upper Midgar, a few steps from the train
    arrival): accept, then win battles in No.1 Reactor against Grunts,
    Sweepers, 1st Rays or Mono Drives (8 in total; enemies that escape or
    battles you flee don't count). His orb turns blue at 8; hand in for
    500 gil + 3 Hi-Potions. Then he offers the No.5 Reactor job (Smoggers,
    Blood Tastes, Proto Machineguns, 8): 1000 gil, 2 Ethers, Steal materia.
    Kills before accepting don't count.
  - *Betty* (Sector 6 playground with the big gate, a little girl, moved up
    out of the path): beat 2 Hell Houses (next screen
    towards Sector 5): 37 gil + an Elixir.
  - *Gwen* (Sector 5 slums, near the tunnel to Sector 6): bring 3 Potions
    (they're taken): HP Plus materia. Talking to her with fewer gives a
    reminder; her orb turns blue while you carry 3 or more.
  - After all quests each giver has a closing line.
  - **New quest givers** (each with an orb; dialogue is meant to be silly):
    | Who | Where | Quest |
    |---|---|---|
    | Madam M | Wall Market, Honey Bee Inn street | bring 2 Ethers |
    | Leslie | Wall Market, street with Corneo's mansion | bring 3 Tranquilizers |
    | Sam (+ chocobo Bessie) | Sector 6 road to Wall Market | bring 3 Loco Weed |
    | Ronnie | Wall Market gym | bring 4 Graviballs |
    | Andrea | Wall Market boutique | 2 each Ceasar, Blugu, Blood Taste, Chuse Tank |
    | Billy Bob | Sector 7 slums street | 5 MP + 4 Grenade Combatants |
    | Scared Man | Train Graveyard (screen next to the station) | 8 Ghosts, then Eligor |
    | Gwen | Sector 7 pillar screen | bring 8 Grenades |
    | Wymer | Sector 7 station | 8 Mighty Grunts |
    | Old Man | Sector 5, in front of the church | 10 Whole Eaters |
    | Ms Folia | Aerith's house (garden screen) | 3 Vices, then bring 1 X-Potion |
    | Zhije | Sector 5 slum town | 10 Hedgehog Pies |
    Check each stands somewhere sensible (not in a doorway or path, not
    hidden behind scenery). Multi-target quests show one "Name: x/y" per
    target in the Quests menu (two per line). With more than 8 quests
    accepted the list should scroll.
  - **Quests menu** (new `ff7_en.exe`): the main menu has a 12th row
    "Quests" above Quit (check the menu window is tall enough and nothing
    overlaps the time/gil box). It lists accepted quests (green = ready to
    hand in); Up/Down select, the bottom window shows title, giver, where,
    a description and progress like "Defeated: 3/8" / "Potions: 1/3".
    Cancel returns to the menu with the cursor on Quests. With none accepted
    it says "No quests in progress." Note any crash, wrong colours or text
    drawn outside the windows.
- **No.5 Reactor elevator** should go to No.5's rooms, and No.1's to No.1's.
- Conductors should now be the same size as other characters; on Upper
  Midgar you and he start mid-screen.
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
  Walk down the passage to reach the Sector 6 playground; the exit line is
  now higher up and wider, so you shouldn't need to hunt for it. There the giant
  gate is open; walk through it to come back to the guard screen. Check the
  gate halves look open (not floating or clipping) and nothing blocks you.
- **Shinra HQ 2f shop**: the two treasure boxes can be opened (Pile Bunker
  and the other item); the assistant no longer stops you.
- **Recruit Barret** on Mt. Corel, on the railway screen just after the
  Corel Reactor (needs the world map to get there). Check his model and that
  he stands on the tracks, not in the air or inside the rails.
- **Recruit Red XIII** (Shinra HQ 67F, by the stairs up from 66F), **Cid**
  (Rocket Town launch pad, by the rocket) and **Cait Sith** (Gold Saucer,
  Wonder Square, where he first appears; joining opens his name entry).
  Each should stand on the floor facing you, join on "yes" and vanish.
  Check Cait Sith's status screen (level/stats, not Young Cloud's).
- **Yuffie**: random fights in world map forests (from new game) can be the
  Mystery Ninja; at Cloud level < 20 she is level 17. Beat her, pass the
  original scene and she should join the party (not only the PHS).
- **Vincent**: Shinra Mansion safe (Lost Number) -> basement key -> coffin,
  answer "Who are you?", then on the way out he catches up. He should join
  the party directly; the PHS should not open.
- **Buggy**: at Costa del Sol's town exit, the salesman sells it for 1000
  gil (try with less too). Buying puts you on the world map outside town,
  in the buggy; get out, re-enter, save/load: it should stay.
- **Kalm**: entering the town, the inn and the houses should play no
  arrival scene, flashback or story dialogue. Walking in with Tifa / Aerith
  in the party should no longer play "everyone's waiting at the inn" or
  remove them (needs a new game).
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
- **Train travel**: at the Sector 7 station talk to the conductor: a menu
  offers Upper Midgar (Sector 8 bridge), No. 1 Reactor (Sector 1 platform)
  and No. 5 Reactor (the tunnel after jumping off the train). At each
  destination a conductor (same model as the station one) stands right next
  to where you arrive, on the floor; talk to him and choose "Yes, take me
  back to Sector 7." You should be able to move as soon as you arrive. Picking a destination shows “ALL ABOARD!” and plays
  the train sound before the jump. Walking into the train itself does nothing.
- **No. 1 Reactor**: walk from the platform through Sector 1 into the
  reactor; all gates/doors should be open with no scenes. At the core there
  is no robot and no Barret/bomb conversation: walking onto the platform at
  the end of the walkway starts the Guard Scorpion fight. After winning it
  doesn't happen again. The reactor entrance also leads out to Upper Midgar.
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

## Modified exe test (does Steam accept an exe with a new code section?)

```
python tools/ff7tool.py exe-test      # -> build/exe_test/ff7_en.exe (patches your own copy)
```

1. In the Steam folder rename `ff7_en.exe` to `ff7_en.exe.original` and copy
   `build\exe_test\ff7_en.exe` in.
2. Start the game from Steam, load any save (or new game) and open the menu.
   - Menu shows **CAVE** (instead of Item) and **QUIT**: an added code section
     works. This is what Tame/Call/Bestiary need.
   - Shows "Item" but **QUIT**: the exe loads but code in the new section
     didn't run (tell me).
   - Error / crash / nothing starts: Steam's DRM rejects an exe with an extra
     section; we'd need another place for the new code.
3. Undo: delete the copied exe and rename `ff7_en.exe.original` back.

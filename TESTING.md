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
  climb the ladder into the vent; its second ladder (far end) now climbs
  down straight away as in the original, no menu. Way back: the first
  ladder, then run left in the corridor.
- **Chocobo rides**: on the Midgar slum outskirts screen (where you enter
  from the world map) Choco Billy and a chocobo stand next to you; same on the
  first Mythril Mine screen (entrance from the marsh side, psdun_1). Talk to
  either: "Ride a chocobo? 100 gil." With under 100 gil Billy says so; with
  enough, 100 gil is taken and you should be on the world map riding a
  (yellow) chocobo, as after catching one in battle. Dismount: it should run
  away. You should now appear outside Midgar / the Mythril Mine on the
  chocobo (before, you appeared in the sea at the top-left corner).
  Midgar's Billy also has "To Wall Market." (100 gil): you should arrive
  just below Sam and Bessie on the road to Wall Market, facing up. Once
  Sam's Loco Weed quest is done, talking to Sam ends with "Need a lift to
  the outskirts?": "Giddy-up!" (free) puts you back on the outskirts screen
  where you arrive from the world map. (Untested in-game.)
- No "Saving on the World Map" window on first entering the world map, and no
  submarine tutorial window (new game).
- Cloud always leads (he can't be moved in the PHS; needs a new game).
- `data\lang-en\kernel\kernel2.bin` is built again (the Honey Bee gift
  key items' names): copy the new one with KERNEL.BIN.
  `ff7_en.exe` is built again (quest kill counting): copy the new one.
- **World quests** (new game; untested): a quest giver with a marker in Kalm,
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
- **Quests** (new game needed for clean quest state; **copy the new
  `data/field/char.lgp` too**, 49 MB). The first sprite build crashed on
  every giver screen; the model files were rebuilt in the exact layout of
  existing field models. If it still crashes, set `QUEST_MARKERS = "orbs"`
  in `patches/_config.py` and rebuild (the old orbs, no char.lgp needed). A star sprite (S-Guard's) floats above
  each giver with a quest to offer; once accepted it becomes a heart until you
  hand the quest in; nothing otherwise. Report the size/height, whether black
  edges show, and whether several givers on one screen (Upper Midgar) all show
  their markers. Cait Sith's beach (del3) has room for the star only.
  Givers turn to face you when talked to.
  - *Middle Manager* (Upper Midgar, a few steps from the train
    arrival): accept, then win battles in No.1 Reactor against Grunts,
    Sweepers, 1st Rays or Mono Drives (8 in total; enemies that escape or
    battles you flee don't count). Hand in at 8 for
    500 gil + 3 Hi-Potions. Then he offers the No.5 Reactor job (Smoggers,
    Blood Tastes, Proto Machineguns, 8): 1000 gil, 2 Ethers, Steal materia.
    Kills before accepting don't count.
  - *Betty* (Sector 6 playground with the big gate, a little girl, moved up
    out of the path): beat 2 Hell Houses (next screen
    towards Sector 5): 37 gil + an Elixir.
  - *Gwen* (Sector 5 slums, near the tunnel to Sector 6): bring 3 Potions
    (they're taken): HP Plus materia. Talking to her with fewer gives a
    reminder; hand in while you carry 3 or more.
  - After all quests each giver has a closing line.
  - **New quest givers** (each with a marker; dialogue is meant to be silly):
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
- **Disc 2 Midgar**: at the Upper Midgar train stop (Sector 8 walkway, the
  conductor's screen) run right: 8th Street (where the party lands in disc 2),
  arriving on its left. Its left end leads back. Its exit on the right leads
  to the hatch screen (hatch open, nobody there). Down the ladder:
  underground, tunnels, Sector 8 bridge, Mako Cannon, Shinra HQ front (md0),
  with no scenes; enemies are disc 2 level. The Shinra Deserter near that right-hand
  exit gives Turks (tunnel below), Proud Clod (Sector 8 bridge) and
  Hojo (top of the cannon) quests; each fight starts by walking over its spot.
- **Shinra HQ**: no forced battles or scenes anywhere; the lobby lifts and
  the elevator work, every elevator floor (incl. 69) is selectable, all
  doors open. Red XIII is no longer in the 67F tank (his recruit NPC is on
  67F). On the roof Rufus stands on the helipad: walking towards him starts
  the fight (once per visit; leave and come back to fight again).
- **Moved NPCs**: Prospector Dunn (Mythril Mine, the room north of the
  entrance), Choco Billy and his chocobo swapped (Mythril Mine), Condor
  Watcher (Fort Condor entrance, 1/3 from right / 1/3 up), Deckhand Moe (cargo
  ship deck with the save point, middle), Sunbather Sal (Costa del Sol beach,
  middle), Stargazer Ina (Cosmo Canyon, ~8 steps back). Recruits: Barret on the
  No.1 Reactor platform (up-left of the conductor), Cid on the Junon airstrip,
  Yuffie at the Chocobo Ranch by the left pen, Vincent in the Honey Bee Inn
  dancers' room (far left; name entry on joining), Cait Sith on the Costa del Sol
  beach far right (name entry on joining). Yuffie's random ninja fights are off.
- **Costa del Sol harbour**: walking into town plays no Rufus/helicopter scene.
- **Mt. Corel**: the man by the tracks just says "It's dangerous up ahead".
- **Corel Prison**: drive the buggy into the Gold Saucer on the world map: the
  prison desert screen; its bottom/left edges lead into the prison. A convict
  near where you arrive in the prison drives you back out (in the buggy).
- **No.5 corridor (Ether)**: running left from where you land crosses a line
  back to the tunnel.
- **Highwind**: Junon airport, press the button, ride the lift, run right to
  the runway with the Highwind, then keep running up the screen (towards the
  far end): you appear on the world map beside Junon flying the Highwind. It
  stays yours (land and re-board). [Menu] while flying does nothing (no
  interior; the main menu can't be opened in the air, land first).
- **Gate of Naught** (Cosmo Canyon): the cave behind the open door can be entered.
- **Recruits**: every recruit turns to face you when talked to. Cait Sith
  and Vincent join without a naming screen (default names, level 1).
- **Start point**: a new game starts on the Sector 7 station's upper platform,
  just below the conductor.
- **Shinra HQ 69F elevator**: [OK] at an elevator door: ride / fight / leave.
  Fight = Hundred Gunner then Heli Gunner (once per visit).
- **Middle Manager** (Upper Midgar walkway) has 4 more quests after his No.5
  one: HQ SOLDIERs/Moth Slashers, 2 Deadly Waste, the elevator boss, Rufus.
- **Sewer**: Train Graveyard -> ladder -> sewer -> at the west dead end (below
  the drop) walk on to go back up into the landing room. No fall scene there;
  its ladder out works. Scared Man's 3rd quest: Aps, by walking into the
  landing room.
- **Honey Bee Girls** (new game; untested in-game): a Manager stands in the
  Honey Bee Inn lobby. Accept his job; then 20 women around the world talk
  to you (before the job they only say a line). Offer the job and answer her
  questions (1-5 by her stars; all are asked, and only at the end does she say whether any were wrong = try again later). Hired girls show
  in the Manager's "Visit" list, best first; visiting plays her scene in the
  "&" room, then the fade line, then you're back beside the Manager.
  Where: Bambi (Upper Midgar, one screen up from the train stop), Gloria (Wall Market materia store), Dot
  (Sector 6), Peggy (Fort Condor base), Candy (Junon, Shinra Member's Bar),
  Rhonda (Nibelheim Inn), Lulu (Junon inn, 3 steps left of before), Raven
  (Ghost Hotel lobby), Elena (Shinra Mansion 1F), Marisol (Costa del Sol
  harbour), Ruby (Gold Saucer Building 1F), Holly (Icicle Inn, left of the Snowboard Instructor),
  Sakura (Wutai shop), Mags (Rocket Town weapon store), Celeste (Gongaga
  jungle), Aurora (Cosmo Canyon observatory), Tifa (her house, upstairs in
  her room), Aerith (Temple of the Ancients, top of the steps by the door
  where the key goes), Scarlet (Shinra HQ 66F Conference Room: the corridor's
  bottom door now leads into it), Velvet (Gold Saucer Battle Square, first screen, near the bottom right of
  the tube platform).
  Models where they stand: Bambi = Shinra secretary, Marisol = Costa del Sol
  bar girl, Lulu = Gold Saucer attendant (all Honey Bees in the scenes). Report girls standing off screen or in the way, and
  how the scenes look (animations were picked without seeing them).
  **Earnings**: the Manager's "Collect the girls' earnings." pays 2 gil per
  star of every hired girl per minute of play since you last collected (or
  took the job), counting at most 4.5 hours; the amount shows in his line.
  Check the number matches the gil you get.
- **Honey Bee lounges** (new; untested in-game): in the Honey Bee Inn lobby
  walk straight through any of the four side doors (no room menu). Left
  doors = the original bedroom, right doors = a NEW mirrored copy of it (the
  bed, door and bath swapped sides; check the picture, the walls you can't
  walk through and what's drawn in front of you all match). Upper-left:
  Bambi, Gloria, Dot, Peggy, Candy; lower-left: Rhonda, Lulu, Raven, Elena,
  Marisol; upper-right: Ruby, Holly, Sakura, Mags, Celeste; lower-right:
  Aurora, Tifa, Aerith, Scarlet, Velvet. Only hired girls appear (as Honey
  Bees): one lying on the bed, one sitting on it, one sitting, two standing;
  the sitting and standing ones play random animations of their kind with
  pauses in between (sitting ones stay seated); talk to each (the bed girls from beside the bed). They never block
  you. The menu works in there; the door line takes you back out by the door
  you used. If the mirrored room crashes or looks broken, say so: it is the
  first new field the mod adds.
- **Debug build** (for testing; untested in-game): `python3 tools/ff7tool.py
  build --debug` writes `build/openFF7_debug/` (same files to copy, plus the
  debug menu; build normally again to get rid of it). In almost any field
  hold **L1 + R1** (on keyboard: whatever keys you mapped to L1/R1): a DEBUG
  menu opens: Travel (Midgar / World 1 / World 2: 23 towns and test spots,
  incl. Wall Market, Honey Bee Inn, 7th Heaven, Kalm, Junon, Costa del Sol,
  Corel ropeway, Gold Saucer, Cosmo Canyon, Nibelheim, Rocket Town, Wutai,
  Icicle Inn, Mideel), Gil +100,000, Encounters OFF / ON (fields and world
  map; stays set in your save until you turn it back on), Honey Bee /
  Hunter: job + all girls hired, all affection 0 / 10 / 20, all 12 gifts,
  all 20 kids, Hunter points +50. Not available in ~40 fields whose text tables are full
  (Kalm bar, disc 2 Midgar, a few dungeons). Opening it during a cutscene
  can leave the scene without player control; use it while walking around.
- **Honey Bee positions** (new; untested in-game): every affection-20
  scene now has the girl walk in behind Cloud in part one (none start on the
  bed any more; the affection-10 Bambi scene too), and part two starts in one
  of five positions: mission (Tifa, Marisol, Bambi), cowgirl (Velvet, Ruby,
  Peggy), ontop = cowgirl facing the other way (Aerith, Celeste, Holly, Lulu,
  Gloria), dog (Scarlet, Mags, Elena, Rhonda, Dot), head (Sakura, Aurora,
  Candy, Raven). Starting points, to tweak: head = Cloud sitting on the bed
  edge 15 right / 15 nearer the camera than before, she at his x, 35 nearer
  the camera, 60 lower than the bed sitter, turned round; cowgirl/ontop = she
  is 14 higher than in Velvet's old scene; mission = Tifa's with Cloud's new
  zcta animation; dog = she starts on all fours, Cloud starts knelt (HBGC),
  10 left / 15 nearer the camera than the old 'beside' spot. Report what's
  off per position (field units: a body is ~90, a head ~14).
- **Honey Bee kids** (new; untested in-game): after a girl's affection-20
  scene (onna_6), go to where you hired her: a kid stands beside her (Rhonda's
  outside the Nibelheim inn door, Velvet's next to her in the Battle Square
  entrance) and says one line. Before the scene the kid isn't there. Debug
  menu: Honey Bee / Hunter -> All 20 kids. Kids: Bambi std girl (white blouse),
  Gloria goggles boy, Dot Midgar boy, Peggy cowboy-hat boy, Candy dark red
  dress girl, Rhonda Nibelheim boy, Lulu swimsuit girl, Raven grey-hood girl,
  Elena red-pigtails girl, Marisol snorkel boy, Ruby Costa sun-dress girl,
  Holly snow kid, Sakura Wutai kimono girl, Mags red-cap boy, Celeste
  Gongaga boy, Aurora Cosmo boy, Tifa red-pigtails girl, Aerith white-blouse
  girl, Scarlet Midgar boy, Velvet Gongaga girl. Report a kid off screen,
  stuck in a wall or overlapping her.
- **Honey Bee gifts and affection** (new; untested in-game; needs the new
  flevel.lgp, kernel2.bin AND KERNEL.BIN). A Gift Merchant (a woman from the
  Wall Market boutique) stands in Wall Market (main street, left side, above
  the item shop), Costa del Sol (the square between the bar and the inn),
  Cosmo Canyon (item store, left hut) and Wutai (the path by the save point).
  Each sells 3 gifts (4,000 to 30,000 gil); a gift is a new KEY ITEM (check
  the Key Items list shows its name and description), one of each at a time
  ("You already have one"). In a lounge, talking to a hired girl shows her
  line with "(Affection N/20)", then "Give her a gift?" if you hold any:
  two pages of 6 gifts. Giving one takes it and raises her affection by 2,
  1 or 0 depending on her taste (shared reaction lines); at 20 she says you
  don't need gifts anymore. Visiting her through the manager then plays a
  closer scene at 10-19 and the most intimate one at 20: these play in two
  NEW copies of the bedroom (new fields, like the mirrored room). Check: the
  number shown (not "0" every time), the key item vanishing when given, the
  three scene tiers, and that every scene's room loads.
- **Bounties: Scoop, roving reporter** (new game; untested in-game; needs the
  new ff7_en.exe AND flevel.lgp). Scoop (a Junon parade reporter) sits in 8
  bars: 7th Heaven (Midgar), Kalm bar (Midgar plains to the Zolom marsh),
  Junon bar (Junon area, Mythril Mine, cargo ship), Costa del Sol bar (Corel
  area, Mt. Corel), Pub Starlet in Cosmo Canyon (canyon lands, Cave of the
  Gi), Nibelheim Inn (Nibel area, Mt. Nibel), Turtle's Paradise (Wutai),
  Icicle Inn bar (snowfields, Great Glacier,
  Gaea's Cliff, Forgotten Capital; 16 enemies). Talk: the spiel names one of
  the region's rarer enemies, how many, 30 minutes of play, the gil; "Deal."
  starts it. The Quests screen should list it first as "(Bounty) <enemy>"
  with the kills and "Time left: N min". Kill them, come back to the same
  Scoop in time: gil. Talking while hunting = a reminder. Time out = it
  disappears from the list and Scoop offers a new one. One per region; the 8
  are independent. Saving and loading (or a new game) drops every bounty.
  Check: the list row and time, kills counting, the payout, a time-out, and
  that loading a save clears them. Each payout shows "Hunter points: T" (+1 Midgar, 2
  Kalm, 3 Junon, 4 Costa, 6 Cosmo, 8 Nibelheim, 11 Wutai, 15 Icicle) and a
  rank-up line at 10, 30, 60, 100, 160, 250 points; points survive saving.
  Each region stops adding points at its ceiling (Midgar stops at 29 =
  Tracker, Kalm at 59 = Hunter, ...) and Scoop says "Bigger game out there". The Quests screen shows
  "Hunter: <rank> (<points>)" in cyan at the top right of the lower window
  (check it doesn't overlap a long quest title).
- **Hunt Quartermaster** (new; untested in-game): Reeve's model at the
  Sector 7 station (lower platform, right), Upper Junon first street
  (between the item and materia shops), North Corel ropeway station (gondola
  platform), Rocket Town in front of Cid's house. Under Tracker he sends you
  away; otherwise a tier menu, a locked tier says "not for your rank", a page
  lists items with prices; buying with too little gil = "You're short",
  enough = gil taken, item in the inventory, back to the menu. Check the
  windows fit (8 items + Back) and that equipment actually arrives. Scoop's spots were picked by a script:
  report any that stand somewhere odd.
- **Round of fixes (new game; untested in-game):**
  - Pillar: the gate at the bottom should now *look* open. At the top of the
    stairs, a few steps right starts Reno (every visit, no quest needed).
  - 7th Heaven arcade lift: the basement plays no wake-up scene and no talk
    when you walk in.
  - Sector 7 item store (the "closed today" door) is open.
  - Music starts again at the end of the motorbike ride; the No.1 Reactor
    station plays the Bombing Mission theme when the train drops you off.
  - 8th Street: you arrive on screen near the left; the way back is at the
    visible left edge.
  - Conductors turn to you. Quest list: finished quests stay at the bottom,
    yellow = ready to hand in, green = handed in.
  - Several givers on one screen (Upper Midgar): each shows its own marker.
  - Sector 5 vent: the far ladder just climbs down (no menu).
  - Junon beach (dolphin area): running down towards the water starts
    Bottomswell, every visit. Rocket Town: out the back of Cid's house,
    running right starts Palmer, every visit.
  - Highwind (Junon airstrip take-off) should now be visible. The submarine
    should sit by Junon (new game only); report if it floats/sinks oddly
    (its height is a guess).
  - Icicle Inn snowboard giver: at the foot of the stairs. Balloon quest:
    30, every colour counts.
- **Sector 7 pillar**: the gate is open both ways; no scenes, random battles
  on the stairs; Biggs, Jessie and Barret aren't there. Gwen (by the pillar)
  has 2 more quests: 8 Aero Combatants, then Reno, who appears when you walk
  towards the middle of the roof.
- **Motorbike**: a Shinra Biker on the right in front of Shinra HQ offers the
  bike ride; afterwards you're at the end of the highway, nobody there, no
  scene. Walking up the road: Motor Ball (once per visit); down: back to the
  front of HQ. The Middle Manager's last quest counts bikes you destroy (12).
- **Snowboard**: the Instructor's 3rd quest counts balloons popped on the run
  to the glacier (15, can take several runs). Needs the board + map from town.
- **Great Glacier**: 6 new quest givers (snowboard landing, north landing,
  Frostbite Cave, deep snowfield, wide slope, hot spring), incl. a survey-flag
  quest (walk to 3 spots), a message to deliver to Holzoff's cabin, and the
  Snow Woman as a boss by her cave. Watch the cold timer.
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
  offers Upper Midgar (Sector 8 bridge), Shinra Tower (the plaza in front
  of HQ), No. 1 Reactor (Sector 1 platform) and No. 5 Reactor (the tunnel
  screen with the duct down; the repeating tunnel screen before it no
  longer has a conductor). At each
  destination a conductor (same model as the station one) stands right next
  to where you arrive, on the floor; talk to him and choose "Yes, take me
  back to Sector 7." You should be able to move as soon as you arrive. Picking a destination shows “ALL ABOARD!” and plays
  the train sound before the jump. Walking into the train itself does nothing.
- **No. 1 Reactor**: walk from the platform through Sector 1 into the
  reactor; all gates/doors should be open with no scenes. At the core there
  is no robot and no Barret/bomb conversation: walking onto the platform at
  the end of the walkway starts the Guard Scorpion fight. After winning it
  doesn't happen again. The reactor entrance also leads out to Upper Midgar.
- **Below the duct** (the screen you drop into from the tunnel): walking to
  the left, just past where you land, takes you back up to the tunnel
  beside the duct.
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

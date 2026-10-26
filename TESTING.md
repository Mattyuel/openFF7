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

- **Tickets, please!** (685): the Director's film menu, third choice. On the
  train: Tifa and Jessie sitting on the near left bench, Cloud walks down the
  aisle, the ticket banter, the fade to Cloud undressed, the fade to the
  position (both across the bench: Tifa on all fours, Jessie on her back with
  her head over the edge and her legs up the window). Same play as Going up
  ("My turn!" calls; Jessie's HOLD lasts until she taps out). Check the girls
  sit on the bench (not floating / sunk), the train's lights and straps move,
  Cloud lines up with each of them, and the low squat at Jessie's head.
  Since the feedback: Jessie lies under Tifa (her head between Tifa's thighs,
  only her head bobs), Cloud's member stays level behind Tifa, and Cloud
  walks in twice as fast (Going up too).
- **Going up** (684): the Director's film menu, "Going up.". The glass
  elevator: the intro (Elena walks in, Cloud tries the console, the stuck
  door, Elena undresses, covers up, crawls over; Cloud walks behind her),
  then the prompts. Besides the button prompts: HOLD prompts (keep the
  button held until the window closes) and Tifa's "Switch!" ([MENU] in
  time). Check the car and its glass look right (the background's layers),
  the switching between Elena and Tifa, the car moving at the end, the pay.
  Since the variety update: a hit plays the squat sound; lines after misses
  and every few reps; Cloud's pose alternates every 6 reps (behind Elena his
  near knee comes up instead of the far one; before Tifa his hands go behind
  his head). With Tifa a HOLD lasts until she taps out (her squirm + a line
  in the top window): let go then. Letting go early is a miss; holding on
  ~1 s after she taps out makes her mad (pay off, slow again); the third
  time she climbs out and the shoot ends. Say if the tap-out is hard to
  notice or the window to let go feels too short.
  Since the feedback: half as long, styles change every 3 reps; Elena
  crawls properly; while Tifa has Cloud, Elena shakes her hips and looks to
  her right now and then; while Elena has him, Tifa looks at the camera and
  tilts her head. Cloud should never play a behind-Elena move at Tifa.
- **Sector 7 Workout** (683): talk to the Director (the cameraman) at the
  Sector 7 station: his first question offers "Shoot Sector 7 Workout.".
  In the gym: the intro talk, then squats. A button name pops up each rep
  ([SWITCH], [CANCEL] or [OK]); pressing it in time keeps the pace building,
  a miss slows it right back down. Check: the prompts register (all three
  buttons), the pace changes are visible, the lines at each new pace, Tifa's
  spandex and tied-up hair, the fade to part two, the pay at the end and the
  trip back to the station. Say if a button never counts, or if anything
  stalls. Since the tweaks: each step up should look about 10% faster
  (8 steps), a hit plays the squat contest's squat sound, a miss always gets
  a line, someone chats every few reps, and the undressed part's later steps
  rock back and forth. Say if the speed still never changes.
  Since the variety update: the pose changes every 6 reps (clothed: a wide
  sumo squat, hands behind her head; undressed: Cloud cocks his near leg up,
  then she folds over to her toes). From the third step some prompts read
  HOLD: press and keep holding while she stays down, then let go when she
  calls it in the top window (late = she's mad; three times = she walks out).

- **No random battles** (950_no_combat): walk around fields that used to
  have encounters (Train Graveyard, the Sector 7 pillar's stairs, Shinra HQ
  stairs, the sewers) and the world map: no battle should start. Scripted
  fights (boss lines, the Honey Bee thugs) still happen. If a field still
  rolls battles, say which.

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
  her room), Aerith (Temple of the Ancients, inside the door, left of the keystone altar
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
- **Dates with Tifa** (new; untested in-game): talk to Tifa in her house in Nibelheim ->
  "Ask her on a date." -> Gold Saucer gondola / space capsule / Junon cannon. The date depends on
  her affection (0-9 / 10-19 / 20: debug Honey Bee -> All affection 0/10/20); questions (right =
  +1 affection, chime); third date with every answer right -> "Give into your desires." / "Leave
  it be." -> part two test scene: fade, then bare Cloud standing and thrusting with Tifa
  (her own undressed copy) koala-hugging him, bouncing; her lines; closing line. Afterwards you're back beside her. Check: the
  view (gondola: Gold Saucer at night with no cabin; capsule: stars in the round window; cannon:
  the top of the Junon cannon where Tifa and Scarlet had their slap fight, the sea animating),
  where the two sit and face (cannon: both standing, Cloud in Tifa's slap spot, she in Scarlet's),
  sitting poses, text, music. Part two/three on the cannon use the same poses.
- **Dates with Aerith** (new; untested in-game): talk to Aerith (Temple of the Ancients,
  by the altar) -> "Ask her on a date." -> any of the three places. Same flow as Tifa's; her
  third date is playfully submissive ("Sir."). Part two = the head scene in her own model:
  she kneels before bare Cloud (muffled lines), he stops and asks if she's okay, she demands
  more, then both go twice as fast. Check her kneeling height/distance, the stop, the speed-up.
- **Dates with Scarlet** (new; untested in-game): talk to Scarlet (Shinra HQ 66F
  conference room) -> "Ask her on a date." First and second dates seated (our sitting
  poses for her); third date: she stands and slaps Cloud before each of three questions
  (slap animation + sound from her Junon catfight). Part two: her skirtless model against a
  wall in front of standing Cloud; she stops him ("put it THERE?"), allows it, he goes
  faster. Check the slaps (pose pops while seated?), her sitting, the wall pose.
- **Dates with Elena** (new; untested in-game): talk to Elena (Shinra Mansion, Nibelheim)
  -> "Ask her on a date." Third date: she doubts herself and begs to be punished. Part two
  (user, since: standing, in every place): she on all fours (her new model: thighs bare), bare
  Cloud beside her hips, a little behind, on one knee (user, since: back knee down, front knee up),
  spanking with his right hand (user, since: arm kept straight, swung from out at the shoulder
  quickly in onto her; the old bent elbow went the wrong way)
  (one swing + the slap sound per spank, in rounds of 1, 2, 3); she asks for more; fade to part
  three: Tifa's koala hug ("holding") on Elena, a slap sound every 0.5 s (it stayed black there:
  fixed, the slaps now run from Cloud's own loop). Both on the left of the
  screen (at her seat), turned as before (DIR -21 from "the other way"). Elena sits on the left
  gondola seat in part one. In the capsule part two/three are now further from the camera (the far
  end of her floor strip; they were off the bottom of the screen). Check: his hand meeting her
  behind at the slap, the two not overlapping (her hips 7 ahead, and to his right as far as his
  straight arm reaches), her all-fours on the floor. Since (user): gondola part two/three further
  from the camera and a bit right, Cloud's head turned to his right there; in part one of the
  gondola and capsule Elena sits half a body width further left (in the gondola just past the
  floor's edge: check she still sits on the seat). Since (user): Cloud kneels upright, so she is a little closer
  to him (part two, every place).
- **Skye's legs, both bare models' arms** (new; untested in-game, user): Skye's legs remade as
  smooth limbs (thigh tops narrower, rounded knees with no gap, slimmer ankles); Skye's and bare
  Cloud's arms keep their shape but are rounder (6 sides instead of 4; Cloud's shoulder pad and
  bracer kept). Both seats 30% longer, tapering in (dog pose); the open bottom of Skye's pelvis is
  closed; Cloud's pelvis lines up with his torso's bottom edge (it sat forward). Check knees /
  elbows when bent, hands and feet still meeting. Since (user): Skye's forearms straight from the elbow (as wide
  as the upper arm) and widening only near the hand, overlapping the upper arm at the elbow; her
  shoulders reach into the arms; a small belly pooch; a bigger bust.
- **Aerith undressed in her date's part two** (new; untested in-game, user): the standard body
  with her own head, braid and boots, kneeling as before. In the capsule an undressed copy now uses
  an unused party model's slot (the field is at 16 models): check the capsule loads.
- **Honey Bee devoted scenes, undressed girls** (new; untested in-game, user): at the fade to the
  bed the girl is swapped for an undressed copy (the standard body, her dancer head and shoes), as
  Cloud already is. Check the swap is hidden by the fade, she plays every position, and the room
  doesn't crash (onna_6 now 14 models).
- **Standard female body on Ruby, Elena, Scarlet, Tifa** (new; untested in-game, user): their
  undressed models (movie, dates) now use Skye's body with their own heads, feet and face skin
  tones; Scarlet keeps her stockings. Check their poses still line up (Elena's head sits lower),
  no shin through the shoes.
- **Sculpted buttocks** (new; untested in-game, user): Skye's pelvis now has a rounded seat
  (two cheeks, a cleft, tucked under) and bare Cloud's pelvis too (smaller). Since (user): both
  fuller (more pronounced, chibi-style) and covering the thigh tops (Cloud's thigh tops slimmed). Check from behind and
  the side in the movie / dates / Honey Bee scenes: no holes, no gap at the waist or the thigh tops.
- **Skye's body** (new; untested in-game, user): in the movie minigame Skye's bare torso and pelvis
  are remade (narrower waist, wider hips, bust, rounded seat; twice the triangles at most). Check
  she shows with no holes or see-through patches (inside-out faces) and no gap at the waist when she bends.
- **Bare Cloud's box** (new; untested in-game, user): every undressed Cloud (Honey Bee devoted
  rooms, dates part two/three, the movie) now has a simple skin-coloured box at the crotch. Check it
  shows (not invisible / see-through: if it is inside-out, the triangle winding needs flipping) and
  that nothing crashes when he appears.
- **Honey Bee rescue** (new; untested in-game): with at least one girl hired, entering Wall
  Market by the Honey Bee Inn has a 1 in 5 chance of a customer slapping one of your girls (never
  Tifa, Aerith, Elena or Scarlet; a
  Honey Bee dancer, named in the dialogue) cowering on the ground below the hearts, left of the inn's door (debug
  build: Honey Bee / Hunter -> "Rescue scene: always"). One of four customers, at random (user): a
  drunk sailor (gives a Speed Drink), a Shinra soldier (battle: a Grunt), a mohawk punk (battle:
  three of Corneo's lackeys) or a grey-suited manager (a 500 gil bribe). Talk to him: "Leave her
  alone!"; fights have no escape and losing doesn't end the game. Done: her affection +1, her thanks,
  fade, both gone. Since (user): Madam M back in the lower right; the customer stands further from
  the girl, is Cloud's height, and slaps by swinging his raised arm out then quickly in. Since (user): both moved left and down
  (left of the pillar by the door) and closer together. Since (user): he faces down-right (45 to
  his left), she sits 2 paces further right, her arms forward with the hands in front of her face;
  the first choice "Leave her alone!" now interferes and "Walk away." walks (they were swapped).
  Since (user): he faces screen-right, his upper body bent 20 forward (standing and slapping).
  Check the slap timing/sound, that the door path stays clear, talking to him, the battle and the fade.
- **Honey Bee devoted scenes** (user, since): in "head" the girl kneels 3/4 of a head further from
  Cloud; in "dog" Cloud uses the movie's dog (his hips thrust, upper body steady). Since (user):
  "head" uses the movie's head too (Cloud upright, left leg cocked forward, a bigger thrust) and
  she kneels a little closer again; in Tifa's "edge" Cloud's left thigh is raised 100 and turned
  10 out with the shin straight down, the foot against the bed's end and staying there while his
  hips thrust and his upper body leans back to take it (it used to stick out level). Check the
  foot looks planted and doesn't vanish into the bed.
- **Head and edge** (Honey Bee and movie; new, untested in-game, user): in "head" Cloud's knees bend
  until his pelvis is a third lower, thrusting from there, both hands on the sides of her head
  (Honey Bee: she kneels where the movie has her, 35 from him and 6 to his right; since (user): Cloud
  a little higher, torso tilted back 5, elbows further out, she 3 further away); in "edge" (Tifa)
  Cloud stands 3 further back and his hands stay on her behind as he thrusts. Check the hands touch
  her head (other co-stars' heads differ in size), and that nothing clips.
- **Honey Bee manager's visit menu** (new; untested in-game, user): "Next page." is now the first row;
  a girl whose devoted scene you've seen shows a "*" after her name (written into the menu text in
  memory by a new field opcode, 0x1D: check it appears/disappears correctly and nothing else in the
  text changes).
- **Special scenes** (new; untested in-game, user): after a full group shoot (or debug "Star rank +1" once
  more past the group), picking a single co-star makes the cameraman ask "Normal scene." / "Special scene.".
  Special: Don Corneo's bedroom (check the room looks right: bed, lights, disco ball), the two clothed in
  front of the bed role-playing (Ruby: detective/thief; Skye: lifeguard; Elena: Turks field exam; Scarlet:
  professor/extra credit; Tifa: Zangan's secret technique; Aerith: evening class), then three positions of
  a minute each: "insert" on the bed (she face down, hips up; Cloud squatting over her, hands on his
  knees, lowering into her; the stroke speeds up every 15 s: 4 s, 3 s, 2 s, 0.5 s), "head" on the floor
  in front of the bed, "finisher" (Cloud on his back, still; she astride facing his feet, leaning back on
  straight arms, bouncing). Check: placement on the bed (does the bed's background draw over them?), her
  pose, his hips meeting hers, the gauge's size and spot in this room, the pay and the return.
- **Special scenes: staged intro** (new; untested in-game, user): the clothed role-play now moves: Cloud
  walks in or paces, the girl crosses to the bed posts, both turn to each other, and each line comes
  with a gesture (Cloud: point, nod, shake head, formal, lean in, stretch...; her: bow, present, twirl,
  check sides, shocked, spin...); Skye starts lying on the floor and gets up; a short pause between
  lines. The cameraman stands still in this part (no animation) and films from the first position.
  Check: the girls' gestures (Elena / Scarlet / Tifa / Aerith get the Honey Bee dancer's gestures copied
  onto their skeletons: watch for odd hands or hair), nobody overlapping (since: no walks, see below).
- **Special scenes, mission, pauses** (new; untested in-game, user): the special insert lines now go
  "there" in the role-play, with a little pain at first; insert: Cloud lower and leaning further forward;
  finisher: Cloud thrusts (on his back), she rides his hips with her shins flat on the bed. Mission (every
  mission girl: Honey Bee, lounges, movie): legs in a V, knees up, feet flat on the bed. Pauses: each head /
  head reverse / 69 position (and each group turn) has a 50% chance of one pause, somewhere in its middle.
- **Kids removed** (user): no kid NPC appears next to any girl any more (coloss's arena kid and nivl_3's
  cloaked man are back as in the game). Seeing a girl's final scene still counts for the movie unlock.
- **Candy and Elena moved** (user): Candy is in North Corel (town, right of centre); Elena is in Junon's
  Shinra Member's Bar where Candy stood. Check both can be talked to, hired and (Elena) dated, and that
  dates bring you back beside Elena in the bar.
- **Date quests** (new; untested in-game, user): Tifa, Aerith, Scarlet and Elena each have a star where you
  meet them; asking her on a date accepts "A Date with <name>" (heart), and the date's end completes it
  (500 gil + Sources). Check the Quests screen lists them.
- **Affection list on Square** (new; untested in-game, user): in any field where Triangle would open the
  menu, Square shows a two-page box: "Name (personality): N/20" for each Honey Bee girl, "????" for one
  you haven't hired or dated. Check: it doesn't open during scenes / conversations, the menu still opens on
  Triangle, the numbers match the lounges, and it never shows in the movie sets (Square is the prompt there).
- **Quest markers, several at once** (fix; untested in-game, user): every quest giver has their own star /
  heart. In the Sector 7 station (Wymer + the cameraman) and Upper Midgar's station (Station Manager +
  Shinra Deserter) both givers' markers should show together. Check nothing else in those two fields
  changed (they reuse the hidden party-member entities).
- **Movie unlock via dates** (new; untested in-game, user): Tifa, Aerith, Elena and Scarlet count for the
  movie unlock once you've seen their final scene on a date (part two) or in the Honey Bee Inn; the other
  16 still need their Honey Bee devoted scene. A date's part two also makes her Honey Bee kid appear.
- **Honey Bee devoted positions by personality** (new; untested in-game, user): Elena now mission (face to
  face, her rules), Scarlet on top (she sets the pace), Tifa cowgirl, Aurora mission; their devoted scenes
  rewritten. Check those four scenes' bed layouts and that nothing else changed.
- **Dates: one position per place + the beach** (new; untested in-game, user): every girl's part two now
  happens in the place's position: space capsule = behind, gondola = head, Junon cannon = holding (Tifa's
  old hug), beach = the special shoot's finisher. "Where to?" has a fourth place, "The beach at Costa del
  Sol.": the empty beach (no tourists), both lounging on the two loungers left of the umbrellas with the
  table between, Costa del Sol's music; part two on Cloud's lounger. The third dates, their lead-in and
  every part two are rewritten to fit each girl (Aerith no longer "sir"; Elena sets ground rules instead of
  asking to be punished; Scarlet's control slips when he's sure of himself). Check: each place shows the
  right pose for all four girls (head: she kneels in front of him, not inside him or too far), the beach
  loungers line up (models on the chairs, legs towards the sea), the sea still animates, and arriving at
  the beach puts Cloud on his lounger.
  (new) On the beach the girl in the finisher sits 8 units higher, and the date's text shows at the bottom of
  the screen: check she isn't floating and the text doesn't cover them.
- **Special shoots: "there" prompt** (new; untested in-game, user): in parts one (insert) and three
  (finisher) the Square icon shows twice a part (first 5-19 s in, the second 20-34 s later); Square in it =
  Cloud tries the back door, and she reacts by her profile: Skye always yes, Ruby usually (3 in 4), Tifa
  50/50, Aerith never (she mocks the try), Scarlet no the first time, yes the second, refuses from the third
  ("don't push your luck"), Elena by the rules she asks for before the first position (Backdoor is
  wide-open = yes, but then she refuses holds; Front door wide-open = holds only; No funny stuff = neither).
  Yes pays her gil a press x 10, no costs x 5-10 and annoys her (two annoyances, hold or there, and she
  walks off: a CUT). Check the icon shows only in parts one and three, twice each, and the head part's
  hold icon still works.
- **Tifa's undressed head** (fix; untested in-game, user): her head now sits 0.8 lower, on the
  shoulders with its own short neck; the thin neck bar under it is gone. Check her in her shoot, the
  group and her date's part two: no gap at the neck when she tilts her head, nothing poking out.
- **Group shoot broke at its start** (fix; untested in-game, user): its models now carry only the
  animations the group plays (26-36 each instead of 63-71). Check the group shoot starts and every part
  (head, head reverse, end) shows the right poses.
- **Lesson** (new; untested in-game, user): in every position with the hold (solo, group, special head, Blast-off's
  first two), after she stops, breaks free at a hold's end, or refuses a hold, the Square icon shows for a second.
  Square: Cloud swings at once (a short wind-up, then down and in to her face, once, straight back to the
  pulled-back pose), the slap sound as the swing starts, then her reaction
  (Skye and Scarlet like it, Tifa and Aerith don't: a strike towards leaving; Ruby 50/50; Elena fine unless
  "No funny stuff"). Check it can't be interrupted and the shoot carries on after.
- **Prompt sounds** (new, untested): a refused hold / "there" / lesson plays the greyed-PHS buzz (assumed sound id 3:
  tell me if it's a different sound), a successful one the materia sound.
- - **Walk-offs and affection** (new): a girl (Elena, Scarlet, Tifa, Aerith) who walks off a shoot loses 1 affection.
  In the cameraman's co-star list her name is then grey (so is any of them below 20, and "Everyone" while any
  is below 20); picking a grey name gets "She won't work with you right now" and the list again. Check the
  grey colour shows on the menu rows (it is poked into the text at runtime).
- **Date revelation** (new): at affection 20, after a video with her has been paid out by the cameraman, her next
  date (any place) opens with a scene about how it felt, with Tifa's Theme, one choice for Cloud, and then the
  date ends (no intimacy). Once per girl.
- **Cloud and Cid** (new): after any Blast-off, a hang-out with Cid at affection 20 opens with him asking what's
  eating Cloud. "Tell him." plays their talk (Cid's Theme) with one more choice; "It's nothing." asks again next time.
- **Group shoot conflicts** (new): one more argument in each part, at the fourth turn: Scarlet grabs Tifa's neck
  (part one), Scarlet needles Elena about stopping while Ruby wants her place (part two), Aerith and Tifa turn
  on each other (part three). Each has Cloud's three-way call. The sideline comments are 5 a set now.
  (new) All six arguments are now staged: fade out, everyone placed (the arguing girls in front, Cloud to the
  side, the others watching), fade in, the talk, a beat (turns, Tifa getting up, ...), Cloud's call, a reaction,
  then a fade back into the shoot. Check the cursor still follows the meter in the group (it is computed now).
- **Hidden histories** (new): small hints now show as extra pages after the first and second dates' closing
  lines, after her last line in each date's intimate scene, and after her movie aftermath; the revelations are
  much longer. Check the extra pages show the right speaker name and fit their windows.
- **Blast-off lesson / Twin Jets** (new): the benches no longer draw over the three in Twin Jets (they now draw
  behind everyone in the set). Lesson swing: Cid swings in Rocketman; in Twin Jets whoever she is facing swings.
- **Rocketman** (new): her torso 10 degrees more upright, Cid raised (floats ~4 units) and turned a little towards
  the camera, Cloud thrusts only his hips. The cameraman stands still through the Blast-off intro.
**Members** (new): Cloud's and Cid's are smooth rounded tubes now; Cid's 30% shorter. Check Cid's still reaches
  in Rocketman / Twin Jets / Exhaust.
- **Blast-off** (new; untested in-game, user): the cameraman now always asks Normal / Special / Blast-off after
  picking a single co-star (???? while locked; picking ???? asks again). Blast-off needs Cid at 20 affection
  (debug: Honey Bee page "All affection 20" sets his too). It plays in the space capsule with the rocket launch music (Launching a Dream into Space):
  Rocketman (Cloud on the left bench, she in his lap bent forward to Cid; Cid's hold prompts), Twin Jets (she
  kneels between them and turns to the other man every 10 s; one hold prompt per man, his own lines), Exhaust
  (the carry, Cid behind her; "there" twice). A minute each, pay doubled. Check the placements, her turn,
  the hold speakers, the meter and the cut afterwards.
- **Members** (tweak; untested in-game, user): Cloud's angled up 30 degrees, 30% longer and 30% thinner; Cid's 70%
  longer than Cloud's and half its first girth, straight.
- **Cid as a friend** (new; untested in-game, user): on the launch pad north of Rocket Town, Cid stands by the
  fuel tank at the rocket's foot with a quest star. Talk: he introduces himself once, then Just chat (his
  affection shows) / Hang out (gondola, capsule, cannon or beach: he sits / lounges / stands like the girls and
  has three conversations by affection, questions +1; no intimacy) / Give him something (gifts: practical +2,
  beautiful +1, sweet 0). The first hang-out completes "Hanging Out with Cid" (500 gil). He appears in the
  Square affection list as "Cid (friend)" once you've met him. Check his spot, the hang-outs in all four
  places (seated pose, back by the rocket afterwards) and the gift menu.
- **Longer hold** (tweak; untested in-game, user): a hold now lasts 9 s (was 7). After her first muffled line she
  squirms twice more (hips wriggling, then a desperate struggle pushing at him) with another muffled line and a
  more desperate one, then pulls away as before. In every shoot with the hold (solo, group, special).
- **Head reverse Cloud's arms** (tweak; untested in-game, user): in the movie's head reverse (solo and group)
  Cloud's arms are straight out in front at 90 degrees to his torso (angled down with his lean), turned in
  halfway at the shoulders, and stay steady while he thrusts, as if holding her back.
- **Group part one, left line** (tweak; untested in-game, user): the three girls on the screen-left side of
  the middle bed kneel a pace further back (x -40, was -20), near its edge; their Cloud moves with them.
- **Girls' personalities in the shoots** (new; untested in-game, user; profiles in
  `patches/_movie_profiles.py`): the Square hold now depends on who you hold, in every shoot (one girl,
  group, special): Ruby always plays along; Skye usually (1 in 4 she changes her mind); Scarlet the first
  time (bigger bonus), then she refuses; Aerith 50/50; Tifa never; Elena only once the rules are agreed
  (in one-girl and special shoots the briefing counts, so she plays along). A refusal: she pulls straight
  off with her line, you lose gil (shown under it; never more than you have), and she's annoyed. Two
  annoyances and she walks off: a one-girl or special shoot ends as a CUT ("She walked off my set?!");
  in the group she's hidden for the rest of it, her turns are skipped, the others don't mention her.
  Group only: an intro conversation before the cameraman's rules, ending in Elena's question (agree
  rules / no rules); one argument per part, at the start of its second turn (everyone freezes, then a
  3-way choice with gil / annoyance / rules / Elena sitting out); Elena and Tifa are uneasy: a stop 3 s
  into each of their turns with "Check she's okay." / "Keep going." (checking: Tifa goes on, Elena goes on
  only with the rules agreed, else she sits her turn out; keep going: she stops anyway, gil lost,
  annoyed, turn over); at the end the girls' banter + a 1,400 gil bonus if nobody walked off, else the
  cameraman's remark; everyone gone = a CUT. Check: the choices appear and can be picked, refusing girls
  really pull off, a girl who walked off stays hidden through part changes, the finisher still comes in
  the last turn when girls have left, gil never goes wrong.
- **Group part three "end"** (new; work in progress, untested in-game, user): after head reverse, six more turns:
  she lies on her back on the bed (knees flapping, head tilted forward and bobbing), Cloud over her shoulders
  facing the bed's end, holding her head. Hold / pause / slap prompts work there too.
- **Insert rocking** (new; untested in-game, user): in the special scenes' insert the girl's pelvis now rocks
  gently with Cloud's strokes (her waist dips back to meet him), at every stroke speed.
- **Slap prompts, hold timing** (new; untested in-game, user): the Square icon now stays 1 s. When a girl's
  line says slap / spank / smack, the icon flashes with it (no automatic slap sound any more): Square plays
  the slap and pays the same bonus as a hold. Hold: stern reminder at 3 s, muffled line at 5 s, her
  struggle at 6 s, pull away at 7 s.
- **Hold button, hand, thrust** (new; untested in-game, user): in head / head reverse / 69 (one-girl
  shoots, the group, the special head) a pink Square icon flashes below the gauge for half a second,
  first somewhere in each position's first 15 s, then about every 15 s. Press Square while it shows:
  the materia sound, Cloud holds deep (bonus on the spot: gil per press x 10, shown in his line), at
  2 s he sternly tells her to hold, at 4 s she tries to pull back and can't (muffled), at 7 s she pulls
  away, gasps and says to continue. The random "hold it" stop and the head turned aside are gone (the
  50% gag pause stays). Check: the icon's spot and size, Square registering (keyboard: the Square /
  Switch key), the window timings. Cloud's thrust in those positions: sharper slow-down halfway and a
  tiny pause at full depth. Cloud's hand: the bracer's top cap now faces outwards (it was culled).
- **Group part one seats** (new; untested in-game, user): Skye and Scarlet have swapped places on the
  middle bed in part one.
- **Hold it, no walks, group fix, poses** (new; untested in-game, user): head / head reverse / 69 (and each
  group turn, and the special head) now have a second, separate 50% chance of a "hold it" stop: Cloud
  pushes in deep and holds, says his line, ~3 s later she pulls away, gasps, clears her throat and says to
  continue. When she has pulled away (both stops) her head is turned to the side. The group shoot no longer
  gets stuck on the last girl of part one (the pause rolls overwrote its turn counter). Special intros:
  nobody walks any more; they start a step apart and only turn and gesture. Finisher (special): her legs
  up, knees bent, feet planted on the bed, spread in a V. Cloud: shorter member (30%, same girth), no hole
  at the top of the hand (the bracer's open top is closed), head / head reverse / 69 thrusts push in fast,
  slow suddenly halfway, then ease out; mission: more pelvic thrust, a bit to the right, legs apart; prone:
  higher off the bed.
- **Instant pose changes** (new; untested in-game, user): every movie shoot (one girl, group, special)
  ends the current animation (ANIMB) before starting the next pose. In the group shoot the engaged girl
  should switch together with Cloud, and in part two the girls should be lying in place by the fade-in.
  (Cause, from the exe: a new animation waited for the previous one-shot animation to finish; the
  girls' waiting animations are ~8 s long.)
- **Switch speed, head reverse, size** (new; untested in-game, user): the switch between positions (every
  shoot) uses faster fades and places everyone at once; head reverse (and behind, and the dates' standing
  part twos, which share the pose): only Cloud's hips thrust, his upper body still, feet flat; Cloud's
  member 50% bigger everywhere.
- **Cameraman moved + three new quests** (new; untested in-game, user): the cameraman and his
  co-star (Ruby, later Skye) now stand in the **Sector 7 station, lower platform, centre** (no longer
  in Wall Market); after a shoot you land just below him. A star shows over him from the start:
  **"Late Night Viewing"**: he sells a video tape for 20 gil (refuses if you have less; the tape is
  key item "Video Tape"). Watch it on the **Item Store terminal in Wall Market** (where the gun used to
  fire: the gun is gone; without the tape the terminal just has a slot): "Insert the tape." shows six
  narration pages. Back to him: "What did you think?" (three answers, his reply), 100 gil + a Source.
  Only then (and with all 20 kids) does he offer the shoot: **"Lights, Camera..."** is offered (star)
  then, starts when you accept, and counts on the return (a CUT counts too); his next talk hands it in
  (1,000 gil + a Source; your cut comes on a later talk as before). **"Talent Scout"**: taking the
  Honey Bee manager's job starts it, hiring the first girl completes it, the manager hands it in
  (500 gil + a Source); an old save that already has the job gets it on the next talk (done at once
  if a girl is hired). Check the star/heart over each of them, the Quests list, the tape in Key
  Items, and the terminal.
- **Group switch + head pose** (new; untested in-game, user): in the group shoot each girl's 15 s now
  count from the fade-in (the switch no longer eats her time; same for the one-girl shoot's
  positions) and the switch is quicker (everyone placed at once). Head (Honey Bee, minigame, group):
  only Cloud's pelvis thrusts; his chest swings back about it so his shoulders, head and hands stay
  still (checked offline: head and hands move < 0.5 model units per stroke, the pelvis 3).
  (User, since) his feet held flat on the floor. Pauses (head / head reverse / 69) come about twice
  as often and her line shows the moment it happens. Elena's head reverse: Cloud 8 units further
  back (solo and group).
- **Minigame pauses** (new; untested in-game, user): in head, head reverse and 69 (and the group shoot)
  there's a small chance (~once every 25 s) the girl stops: both pull back and hold, she says a line
  (catching her breath / a reflex, urging him on), then they carry on. The meter is frozen meanwhile
  and the position's time isn't used up.
- **Head and mission** (Honey Bee + minigame; untested in-game, user): in head Cloud's legs are turned
  45 out, he stands a little to his right so his pelvis is on her face, and his hands hold the
  outside of her head; in mission her legs are turned 45 out at the hips (knees open, feet planted).
- **Minigame group shoot** (new; untested in-game, user): after Aerith's wrap the co-star list starts
  with "Everyone": all six girls on one set. Part one on the middle bed: two lines of three kneeling
  girls facing each other, Cloud between them going through each girl in a random order, 15 s each;
  part two: two girls lying across the end of each bed, the same. Idle girls turn their heads now
  and then; the others comment while the engaged girl mumbles. Pays 70 gil a press. Check the bed
  placements (especially the right bed's end, which has little floor) and that every girl gets one turn.
- **Minigame intro** (new; untested in-game, user): the shoot opens with Cloud and the girl standing at
  the foot of the left bed, the cameraman beside them; before "...And... ACTION!" the screen fades out
  and back in on the first position. Check each co-star stands (her model's first animation).
- **Batch** (new; untested in-game, user): the minigame meter goes back to the middle at every
  position change; mission (everywhere): her legs wider apart and her knees straighter again
  (bent ~39); Tifa's and Scarlet's breasts 50% bigger, Aerith's 50% smaller (undressed models:
  dates, movie; check the nipples still sit on them).
- **Movie minigame, poses and co-stars** (new; untested in-game, user): head: she kneels a touch
  closer; behind: her hands planted on the bed, feet on the floor, only her hips moving with
  Cloud (her back pivots, arms bend); mission: Cloud's shins stay flat and still, his pelvis
  thrusting; head reverse: her hanging head rocks back and forth; mission everywhere (Honey Bee,
  movie, the lounges' lying girls): her knees straighter. **Co-stars now come one at a time**:
  each wrap (a full shoot) brings the next (Ruby, Skye, Elena, Scarlet, Tifa, Aerith; no affection
  needed), and (user) every girl unlocked so far stays on the co-star list, newest first; back in
  Wall Market the cameraman explains where the last one went (and that the old girls still take a
  callback). Debug
  "Star rank +1" raises the rank one step and he tells the news on your next Wall Market visit (the
  old menu's Skye check was inverted: every other pick shot with Skye). Check every girl's set
  starts, her pay rate, and each news line.
- **Movie minigame: Bio sound** (new; untested in-game, user): reaching the right red zone (a CUT,
  or the finisher in the last 5 s) plays the Bio spell's sound (id 0x3F, read from the exe: check
  it's the one you mean).
- **Nipples** (new; untested in-game, user): every undressed girl (Ruby, Skye, Elena, Scarlet,
  Tifa, Aerith, the Honey Bee girls) has small pink nipples on the bust. Check they sit on the
  skin (not floating, not sunk) and their size.
- **Movie minigame, four more co-stars** (new; untested in-game, user): after the first wrap the
  co-star menu lists Skye, Ruby, Elena, Scarlet, Tifa, Aerith; the four need full affection (20),
  else the cameraman says so. Each shoots on her own copy of the set with her own lines and pays 10
  gil a press more (Elena 30 .. Aerith 60; finisher x100). Check her poses (copied from Ruby's onto
  her skeleton: hands/knees may sit a little off; hair keeps its standing shape; Tifa's head tilts
  forward on all fours so her hair clears her back), her lines, the pay.
- **Movie minigame** (new; untested in-game): the cameraman now stands in Wall Market from the
  start (user), still, camera at his side (user, since: still there, filming again in the shoot); before all 20 Honey Bee kids he only asks whether you know a man with a way with
  the ladies. The shoot needs all 20 kids (debug menu: Honey Bee / Hunter -> All 20 kids). Wall Market main street, right of the item shop: a
  cameraman (the Junon reporter with the camera) and Ruby (red hair, black jacket). Talk to
  him -> "Lights, camera, action!" -> the Sector 7 room with three beds. Press OK
  (confirm button) repeatedly: the gauge at the top (red | green | red; was off the bottom of the screen) and the cursor
  above it; pressing pushes it right, stopping lets it drift left, it has momentum and runs
  away from the middle. Red at either end = "CUT!" and back to Wall Market; he still sells what was shot (user: a
  low score, presses so far x 10 gil, same 30-minute wait), but only a full shoot raises the star
  rank (unlocks Skye). Ten
  positions, 30 s each, moving between the beds (mission left bed, cowgirl middle bed,
  dog right bed, edge and head reverse at the left bed's foot, head on the floor, then "behind"
  (Scarlet's date pose) at the left bed's foot by the wall, "holding" (Tifa's koala hug) at the right
  bed's end, "69" on the middle bed and "prone" on the right bed); the thrust
  speed follows how fast you press (4 steps). Each position change fades out and in, and the
  position only changes once the screen is black (user). The cursor is half its old size and the
  push is now timed by frames (it couldn't be pushed up before): ~2.5 presses/s holds it, faster
  rises. Ruby says a line (window at the bottom; 8 per
  position, e.g. 'Pull my hair!') every ~2.5 s that closes by
  itself (~2 s; muffled during head / head reverse / 69). Costa del Sol music. After five minutes:
  "That's a wrap", back in Wall Market, he says to come back in half an hour. The first full shoot
  unlocks Skye (blue hair; her bare model: bikini skin-coloured, the yellow streamers removed): she
  stands where Ruby was, the cameraman says once that Ruby just turned 19 and retired, and after accepting he asks
  "Skye" / "Ruby". Skye plays the same positions with her own, dirtier lines. After 30 play
  minutes his talk pays presses x 10 gil (x 20 for a shoot with Skye: user). Check: does every OK press register now (held-state polling; the 'just pressed' check missed some)? the gauge
  and cursor visible and on screen at each bed? the self-closing lines? the bed positions on
  the right beds? Ruby's bare model (skin legs/skirt/upper arms/feet, coat kept).
  Finisher (user, new): 5 s before the end of the last position the cameraman shouts (top window,
  closes itself) "Go all out, star! Give me a FINISHER!"; hitting the right red then plays the
  victory fanfare, "WOW! What a FINISHER!", pays 1,000 gil on the spot (Skye 2,000) and ends the
  shoot as a wrap; then the girl comments on it. The left red still cuts. Head is now the last
  position (the finisher), prone takes its old place (6th). Check the shout window doesn't cover the gauge.
  Since (user): the shoot opens on black and fades in once everyone is placed (no visible model
  moves at the first position); back in Wall Market Cloud lands 4 paces further down (he was stuck
  beside the cameraman); Skye stands (her donor's default pose was sitting); "head": Ruby's head
  tilted ~20 back, Cloud's left leg cocked ~20 forward with the foot planted and a stronger
  thrust (ZCTQ); "dog": Cloud's hips thrust while his upper body stays put (ZCTN); "prone": Cloud
  on his stomach on her, torso up 30, head a little down, upper arms down and forearms forward with
  the hands flat on the bed, hips thrusting up with the knees bending and back (ZCTO). Check his
  height on her in prone (PRONE_UP). Debug menu (Honey Bee / Hunter): "Star rank +1" (unlocks Skye),
  "Time +30 min" (the movie cut and the Honey Bee takings wait 30 minutes less; bounties not).
  After Aerith's date Cloud now lands to her left on screen (was stuck beside her).
  A slap sound now follows every minigame line about slapping/spanking (Ruby's and Skye's), and
  Scarlet's "WRONG! *slap*" Honey Bee line. Check when it sounds: the minigame's windows can't be
  closed, so if their MESSAGE waits for the window, the slap comes as the line closes (~2 s later).
- **Honey Bee visit menu** (new; untested in-game): "Visit one of the girls" opens
  One Star Girls (Next page / Never mind), then Two .. Five Star Girls (Next /
  Previous / Never mind; no Next on Five). Girls not hired show as ???? and
  picking one just shows the page again.
- **Faster positions + fanfare** (new; untested in-game): in affection-20
  part twos everything moves at 0.5 s per stroke with more bounce: mission
  (Cloud's thrust, the girl bouncing on the mattress), cowgirl/ontop (girl
  bouncing higher; Cloud on his back thrusting up, head up looking at her,
  arms a little raised). Dog unchanged. From the fade to the bed the victory
  fanfare plays (dog: the chocobo fanfare). Tifa's and Aerith's lines are now
  jokey. Report if the music doesn't start or keeps playing in the lobby. Own tracks: Candy Fiddle de Chocobo, Scarlet Rufus' Welcoming Ceremony, Mags Steal the Tiny Bronco! (track picked from memory: say if it's another song), Elena Crazy Motorcycle, Aerith Interrupted by Fireworks, Tifa Debut. Every scene's closing text (all affection levels) plays the inn tune Good Night, Until Tomorrow!.
- **Honey Bee positions** (new; untested in-game): every affection-20
  scene now has the girl walk in behind Cloud in part one (none start on the
  bed any more; the affection-10 Bambi scene too), and part two starts in one
  of seven positions: edge (Tifa), mission (Marisol, Bambi), cowgirl (Velvet, Ruby,
  Peggy), ontop = cowgirl facing the other way (Aerith, Holly, Lulu,
  Gloria), dog (Scarlet, Mags, Rhonda, Dot), head reverse (Elena, Celeste), head (Sakura, Aurora,
  Candy, Raven). (User, since: in head Cloud's knees are bent much more, pelvis low, and he stands
  a little closer to her.) Starting points, to tweak: head (new version) = both on the
  floor left of the bed, bare-legged Cloud standing facing left (knees bent,
  leaning forward, thrusting, arms swinging in and out), she kneels a step to
  his left facing him, rocking, her head kept upright (both 0.5 s); edge (Tifa only, new) = she stands
  just left of the bed's left end facing right, bent over 90 at the hips with her
  arms stretched out over the bed, rocking; Cloud stands behind her facing the
  bed in the same thrusting pose (since changed: she's 7 further right (the floor
  ends there, not a full half step), Cloud 22 right, his arms further forward and
  his left leg raised; her head tipped back and turned right, arms angled down
  and dipping as she rocks forward; after "Faster!" both move twice as fast); head reverse (Elena only, new) = she lies on
  her back along the bed, head at its left end tipped back over the edge, arms
  up past her head, bouncing with her knees opening and closing; Cloud as in
  edge (since: Celeste too; Cloud a step further right; her head hangs straight
  down, hips held up and bouncing). Cowgirl: she's slightly left, arms and head
  dip as she rises. Head's Cloud: right arm up ~70, left ~30, both bent in.
  Edge: her head further back, hands stay put while she rocks (elbows bend);
  after "Faster!" her torso is a bit more upright and arms lower. Head / head reverse girls now only manage muffled "Mmf!" lines in part
  two; cowgirl/ontop = she
  is 14 higher than in Velvet's old scene; mission = Tifa's with Cloud's new
  zcta animation; dog = she starts on all fours, Cloud starts knelt (HBGC),
  10 left / 15 nearer the camera than the old 'beside' spot. Report what's
  off per position (field units: a body is ~90, a head ~14).
- **Temple of the Ancients way out** (new; untested in-game): inside (after
  the altar warp) a Temple Guide stands right beside where you arrive; talk
  to him -> "Take me outside." puts you in front of the temple door. The
  quest giver outside now stands just right of the path to the exit.
- **Dim visit rooms** (new; untested in-game): the three Honey Bee visit
  rooms (all scenes, not the lounges) are drawn at half brightness: the room
  picture and the characters' lighting. Say if it's too dark / too light.
- **Bare-legged Cloud** (new; untested in-game): in affection-20 scenes,
  after the fade to the bed Cloud is a second model with skin-coloured legs
  (no pants) and slimmer knees; part one is the normal Cloud. Report a
  missing/odd model, a Cloud still standing where he was, or both Clouds showing.
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

- **Gold Saucer stage show** (new, untested): after a full group shoot and Cid at affection 20, the cameraman (Sector 7
  station) gives the quest **Top of the Bill**: the Gold Saucer wants the troupe live. Before that the Booker turns you
  away. Then the Booker (the play's King) by the aisle in Event Square welcomes you, pays the quest (2,000 gil) and
  offers a live show. Check: the cameraman's star appears once both conditions hold, his reminder line while it's
  open, the heart goes once the Booker hands it in. Four acts on the play's stage: a clothed scene in costume with a
  conflict and Cloud's choice, then a fade into the undressed minigame (tavern: Tifa holding; lair: Scarlet cowgirl;
  cave: Aerith Twin Jets with Cid; castle: Exhaust with Cid and the bride you chose), a finisher in the finale, pay on
  the spot, back to the Booker. Check: everyone appears (clothed models, the Dragon costume, undressed), the meter
  works on the stage, Aerith turns between the men, nothing hangs between acts.

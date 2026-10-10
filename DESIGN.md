# openFF7 — Design Document

An open-world rework of Final Fantasy VII (Steam PC version). The linear story is
removed. Every area is reachable, characters are recruited in the world, and
bosses are optional encounters.

This document records decisions as they are made. Items under **Open questions**
are still undecided.

---

## 1. Distribution format

- **Standalone build, not a 7th Heaven mod.** A build script takes the user's own
  Steam install as input. It writes a separate, self-contained game folder with
  patched data files (`flevel.lgp`, `world_us.lgp`, `scene.bin`, `kernel.bin`,
  text, etc.). The user's Steam install is left untouched.
- **Source of truth in the repo:** tooling, extracted/decompiled scripts as text,
  and patch definitions. Original game data must stay in a **private** repo or
  out of git. GitHub rejects files over 100 MB, so the large `.lgp` archives
  and movies need Git LFS or a local-only path.
- **Note:** the Steam exe normally starts through its launcher, and Steam must be
  running. Making the output folder launch on its own may need an open-source
  game driver such as FFNx. This is to be verified once the files are in the repo.

## 2. Core technical approach

The original game gates almost everything on one story-progress variable (the
"Game Moment", `var[2][0]`, values 0–1999). 391 of the 702 fields compare
against it. openFF7 replaces that with **per-location state**:

1. **Pin each field to a story moment.** `tools/ff7/patch.py: localise_progress`
   rewrites every `if (var[2][0] <op> N)` in a field into `if (M <op> N)` where
   `M` is the moment chosen for that location (§4), and removes writes to the
   story value. The field then always looks and behaves as it did at moment
   `M`. `M` is picked between the field's story events so its cutscenes don't
   fire.
2. **Regions with their own story line.** Where a side quest is built on the
   story value (e.g. Wall Market / Corneo), the region's fields read and write
   a private variable instead, so the quest still plays out on its own.
3. **Remove remaining story barriers** (guards, locked doors, lines) per field,
   found by testing.
4. **New per-feature flags** (recruitment, transport unlocks, boss defeats,
   Corneo's move, region progress) use save variables bank 4, offsets 224–255,
   which no original script uses.
5. **Build.** Patches live in `patches/*.py` and are applied by
   `tools/ff7tool.py build`, which writes a separate game folder
   (`build/openFF7/`) and leaves the original data untouched.

The global story value is set to 100 at new game (`patches/_config.py`).
The `.exe` itself only compares story progress against 1000/1200/1580/1620 (world
map setup), and the world map script has ~25 checks, so 100 keeps the world map
in its disc 1 state until it is opened up. See `docs/exe_notes.md`.

Midgar per-field choices: `docs/midgar_plan.md`.

## 3. Decisions so far

### Party
- A new game starts with **Cloud only**.
- Other characters are recruited by meeting them in the world, with new
  recruitment dialogue.
- **Aerith is permanent.** Her death and all related content are removed.
- The PHS (party switching) is available from the start.
- **Starting point:** Cloud starts at the **Sector 7 train station**.

#### Recruitment locations

| Character | Where | How |
|---|---|---|
| Aerith | Sector 5 church | New recruitment dialogue |
| Tifa | Seventh Heaven bar, Sector 7 | New recruitment dialogue |
| Barret | Sector 7 weapon shop | New recruitment dialogue |
| Red XIII | Shinra HQ lab (specimen area) | New recruitment dialogue |
| Cait Sith | Gold Saucer, Wonder Square arcade (fortune reading) | Adapted from the original recruitment |
| Cid | Rocket Town, near the rocket | New recruitment dialogue |
| Vincent | Shinra Mansion basement | As in the original (Basement Key from the safe) |
| Yuffie | Random forest encounters | As in the original |

#### Party leader
- **Any recruited character can be party leader.**
- The leader is the character the player controls when walking around.
- Many field files only define a walking model for Cloud. Every playable
  character's entity is added to those fields.
- The world map only ships walking models for Cloud, Tifa and Cid. **World map
  models and animations for the other characters are converted from their
  field models.**

### Enemies and bosses
- **Regular enemies are unchanged** (stats, levels, encounter areas).
- **Bosses are visible in the world.** Each story boss appears as a model in or
  near its original location. Touching it starts the fight.
- After a boss is defeated once, its battle formation is **added to that zone's
  encounter table as a rare encounter**.
- **Drops and steals repeat** on every rare-encounter fight, not just the first kill.
- **Jenova and Sephiroth fights stay.** They are reached from the bottom of the
  spiral section of the Northern Crater. The game **continues afterwards**:
  no game-ending sequence, and the player returns to the world.

### NPCs that move
- **Don Corneo** starts in Wall Market. After he is beaten there, he moves to
  Wutai, where Yuffie's Wutai quest picks him up.

### Midgar
- Midgar is in its **early disc 1 state**: the Sector 7 plate is intact and the
  bombing story events are gone.
- **No invisible walls** or story barriers. Every area that is reachable at any
  point in the story is reachable.
- Midgar connects to the world map **the way it does on disc 3: past the church
  in Sector 5, using the key**.

### Travel
- **On foot / chocobo:** as in the original.
- **Ferry:** the Junon ⇄ Costa del Sol cargo ship works as a regular ferry.
- **Submarine:** available **from the start**.
- **Buggy:** unlocked the **first time the player leaves Costa del Sol**.
- **Airship (Highwind):** unlocked by **visiting the landing strip at Junon**.
- **Tiny Bronco:** available **from the start**, moored in the water near Gongaga.

### Minigames
- Minigames outside the story stay (Gold Saucer, chocobo racing/breeding, etc.).
- **Story-tied minigames become repeatable activities** started by talking to an
  NPC in the associated town:
  - Fort Condor battles: Fort Condor
  - Corel train chase: North Corel
  - Submarine chase: Junon
  - Junon parade: Junon
  - Motorcycle chase: Midgar, by interacting with the motorbike on display in
    the Shinra HQ lobby showroom

### Story-locked items and places
- **Temple of the Ancients is open from the start.** No Keystone is needed.
- **The Huge Materia is already in Cosmo Canyon** (Bugenhagen's observatory) and
  can be interacted with from the start. The resulting materia (e.g. Bahamut
  ZERO) being available early is intended: it still has to be levelled against
  strong enemies.
- **Fort Condor, Corel train and submarine minigames** award a **1/35 soldier**
  key item instead of Huge Materia (once per minigame, on the first win).
- **Shop stock scales with the highest character level.** Shops keep their
  original item lists. Where a shop's stock changes with story progress in the
  original, each tier is unlocked when the highest-level character in the roster
  reaches a threshold. Thresholds are set per shop, based on the typical party
  level at that point in the original story.

### Locations restored
- Areas that become inaccessible later in the original (e.g. Cave of the Gi in
  Cosmo Canyon, parts of Midgar) are made accessible again in the open world.

---

## 4. Location state table

One canonical state per location. The full generated list, with the story-moment
range each field checks and sets, is in `docs/inventory/locations.md`. Moments
below are the `var[2][0]` values observed in the scripts.

| Location | Original versions | Chosen state | Notes |
|---|---|---|---|
| Midgar (all sectors) | Pre-plate-fall / post-fall / Sister Ray assault | Pre-plate-fall (disc 1) | Exit via Sector 5 past the church. Sector 7 fields check moments 63–221; the start station `mds7st3` sets 63 |
| Shinra HQ | Infiltration / later visits | TBD | Floor access, keycards, guards |
| Temple of the Ancients | Intact / shrunk into the Black Materia | Intact (proposed) | |
| Mideel | Intact / destroyed | Intact (proposed) | |
| Junon | Parade / underwater reactor / cannon removed | TBD | Landing strip unlocks the airship |
| Nibelheim | Flashback / replica town | Replica town (proposed) | Shinra Mansion for Vincent |
| Cosmo Canyon, Cave of the Gi | Restricted later | Accessible | |
| Northern Crater | Barrier / open | TBD | |
| World map | Meteor, Weapons, Junon cannon | TBD | |

## 5. Boss placement (from the data)

Every fixed battle started from a field script is listed in
`docs/inventory/scripted_battles.csv`. The main story bosses and where they are
fought in the original (field file) are below. Each becomes a visible, touchable
boss in that room and then a rare encounter in the same area.

| Boss (formation) | Original field | Area |
|---|---|---|
| Guard Scorpion (324) | `nmkin_5`, `smkin_5` | Sector 1 Reactor |
| Air Buster (364) | `southmk2` | Sector 5 Reactor |
| Aps (386) | `colne_b1` | Sector 6 sewers |
| Reno + Pyramid (412) | `pillar_3` | Sector 7 pillar |
| Hundred Gunner (460) | `eleout` | Shinra HQ elevator |
| Sample:H0512 (456) | `blin68_2` | Shinra HQ 68f |
| Rufus + Dark Nation (464) | `blin70_3` | Shinra HQ roof |
| Motor Ball (468) | `blackbg9`, `blackbgb` | Midgar highway |
| Bottomswell (480) | `ujunon2` | Junon |
| Jenova·BIRTH (488) | `shpin_3` | Cargo ship |
| Dyne (527) | `dyne` | Corel Prison |
| Reno + Rude (539) | `gonjun2` | Gongaga |
| Gi Nattak (555) | `gidun_3` | Cave of the Gi |
| Lost Number (576) | `sinin2_1` | Shinra Mansion |
| Materia Keeper (595) | `nvdun1` | Mt. Nibel |
| Palmer (600) | `rckt32` | Rocket Town |
| Rapps (619) | `datiao_6` | Wutai, Da-chao |
| Godo (628) | `tower5` | Wutai, Pagoda |
| Red Dragon (652) | `kuro_82` | Temple of the Ancients |
| Demons Gate (644) | `kuro_12` | Temple of the Ancients |
| Jenova·LIFE (671) | `ancnt3` | Forgotten City |
| Schizo (740) | `gaiin_6` | Gaea's Cliff |
| Jenova·DEATH (743) | `trnad_4` | Whirlwind Maze |
| Carry Armor (780) | `semkin_5` | Underwater Reactor |
| Reno + Rude (807) | `qb` | (to check) |
| Turks trio (840) | `tunnel_6` | Midgar tunnels |
| Proud Clod (844) | `md8brdg2` | Midgar Sector 8 |
| Hojo (856) | `canon_2` | Sister Ray |
| Diamond Weapon (980) | `fr_e` | Midgar outskirts |
| Ultimate Weapon (280) | `itown2` | Mideel |
| Jenova·SYNTHESIS (908) | `las4_4` | Northern Crater bottom |
| Bizarro·Sephiroth (912–936) | `lastmap` | Northern Crater bottom |
| Safer·Sephiroth (924) | `lastmap`, `blackbge` | Northern Crater bottom |

Bosses with special rules still need checking one by one: multi-party
Bizarro·Sephiroth, Cloud-only fights, and battles whose AI ends the fight early.

---|---|---|---|
| Guard Scorpion | Sector 1 Reactor | Sector 1 Reactor | — |
| Air Buster | Sector 5 Reactor | Sector 5 Reactor | — |
| Aps | Sector 6 sewers | Sewers | — |
| Reno | Sector 7 pillar | Sector 7 pillar | Check battle script for story-specific end conditions |

(The full list is generated from `scene.bin` boss formations once the data is in the repo.)

---

## Open questions

None at the moment.

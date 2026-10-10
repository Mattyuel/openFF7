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
"Game Moment"). openFF7 replaces that with **per-location state**:

1. The new game sets the story-progress value to a fixed baseline.
2. Field and world map scripts that branch on story progress are rewritten to
   use the chosen state for each location (see §4) plus new per-feature flags
   (recruitment, transport unlocks, boss defeats).
3. All changes are made as text diffs against decompiled scripts, then reassembled
   by the build.

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
- Technical note: many field files only define a walking model for Cloud, and
  the world map only ships walking models for Cloud, Tifa and Cid. Other
  leaders need entities/models added. See open questions.

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
  can be interacted with from the start.
- **Shop stock scales with the highest character level.** Shops keep their
  original item lists. Where a shop's stock changes with story progress in the
  original, each tier is unlocked when the highest-level character in the roster
  reaches a threshold. Thresholds are set per shop, based on the typical party
  level at that point in the original story.

### Locations restored
- Areas that become inaccessible later in the original (e.g. Cave of the Gi in
  Cosmo Canyon, parts of Midgar) are made accessible again in the open world.

---

## 4. Location state table (to be filled in)

One canonical state per location. Generated from the field inventory once the
game data is in the repo.

| Location | Original versions | Chosen state | Notes |
|---|---|---|---|
| Midgar (all sectors) | Pre-plate-fall / post-fall / Sister Ray assault | Pre-plate-fall (disc 1) | Exit via Sector 5 past the church |
| Shinra HQ | Infiltration / later visits | TBD | Floor access, keycards, guards |
| Temple of the Ancients | Intact / shrunk into the Black Materia | Intact (proposed) | |
| Mideel | Intact / destroyed | Intact (proposed) | |
| Junon | Parade / underwater reactor / cannon removed | TBD | Landing strip unlocks the airship |
| Nibelheim | Flashback / replica town | Replica town (proposed) | Shinra Mansion for Vincent |
| Cosmo Canyon, Cave of the Gi | Restricted later | Accessible | |
| Northern Crater | Barrier / open | TBD | |
| World map | Meteor, Weapons, Junon cannon | TBD | |

## 5. Boss placement (draft — to be checked against the data)

Bosses with special battle rules need individual handling. Examples: fights
that end on a timer or turn count (the Turks), solo or forced-party fights
(Rufus, Hojo), multi-party fights (Bizarro Sephiroth), and the Jenova/Sephiroth
fights tied to story scripts.

| Boss | World location (proposed) | Rare-encounter zone | Special handling |
|---|---|---|---|
| Guard Scorpion | Sector 1 Reactor | Sector 1 Reactor | — |
| Air Buster | Sector 5 Reactor | Sector 5 Reactor | — |
| Aps | Sector 6 sewers | Sewers | — |
| Reno | Sector 7 pillar | Sector 7 pillar | Check battle script for story-specific end conditions |

(The full list is generated from `scene.bin` boss formations once the data is in the repo.)

---

## Open questions

1. **Non-Cloud leaders outside Midgar** — on the world map, only Cloud, Tifa and
   Cid have walking models. Options: (a) convert field models for the others,
   (b) world map always shows Cloud/Tifa/Cid as a stand-in. Needs a look at the
   data before deciding.
2. **Huge Materia balance** — touching the Huge Materia gives very strong
   materia (e.g. Bahamut ZERO) from the very start. Intended?
3. **Fort Condor / train / submarine rewards** — those minigames originally
   award Huge Materia. What should they award now?

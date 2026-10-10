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
- The PHS (party switching) must be usable from the start or from the first
  recruit (see open questions).

### Enemies and bosses
- **Regular enemies are unchanged** (stats, levels, encounter areas).
- **Bosses are visible in the world.** Each story boss appears as a model in or
  near its original location. Touching it starts the fight.
- After a boss is defeated once, its battle formation is **added to that zone's
  encounter table as a rare encounter**.

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

### Minigames
- Minigames outside the story stay (Gold Saucer, chocobo racing/breeding, etc.).

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

1. **Midgar key** — in the open world, where is the key to the Sector 5 exit
   obtained? Or is the exit simply open?
2. **Starting location** — where does Cloud start (e.g. Sector 7 slums, the
   Sector 1 station, near the church)?
3. **Party leader and PHS** — is Cloud always the party leader? Can anyone
   be swapped in at a save point from the first recruit onward?
4. **Boss rewards on repeat** — should boss drops and steals repeat on the
   rare-encounter version, or only on the first kill?
5. **Unique-story bosses** — Jenova forms, Sephiroth forms, Rufus, Hojo,
   Bizarro/Safer Sephiroth: placed in the world like the others, or excluded?
6. **End goal** — is there a final challenge (e.g. Northern Crater capstone),
   or is the game fully open-ended?
7. **Story-tied minigames** — Fort Condor, Corel train, submarine Huge
   Materia chase, Junon parade, motorcycle chase, Shinra HQ stair race: keep
   as repeatable activities?
8. **Story-locked rewards** — where do the Huge Materia items, the Ancient
   Key, the Keystone, the Black Materia temple rewards, etc. come from now?
9. **Tiny Bronco** — include it, given the ferry, submarine and airship?
10. **Characters appearing in two places** — e.g. Don Corneo in Wall Market
    (disc 1) and in Wutai (Yuffie quest). Which appearances survive?
11. **Recruitment locations** for each character.
12. **Shop inventories** — one fixed inventory per shop, or unlocked by
    condition?

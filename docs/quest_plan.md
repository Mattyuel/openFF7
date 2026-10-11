# Quest system — plan

Status: first version built (`patches/600_quests.py`, untested in game):
Middle Manager (md8brdg, kill x2 chained), Betty (mds6_2, kill Hell House),
Gwen (mds5_3, deliver Potions); orb markers; kills counted by an exe hook on
the victory reward loop (not enemy AI). Not yet: courier kind, EXP/AP reward
battles, "!" model, quest board. Original plan below. Requested: NPCs with "!" over their heads
offer quests; talking to them again once the requirement is met completes the
quest and gives a reward; some quests are gated behind others. Types for now:
kill X of an enemy, deliver X of an item, carry an item to another NPC.

## 1. Data-driven: one quest table, one patch

Quests are written as data (`patches/quests.py`, plain Python dicts), and a
patch (`600_quests.py`) generates the scripts. Adding a quest = adding an
entry, no new code. Sketch:

```python
QUESTS = {
  "kalm_wolves": dict(
      giver=dict(field="elm", npc="new", model=("elmin1_1", 3), at=(x, y)),  # or an existing entity name
      kind="kill", enemy=17, count=5,                 # enemy id from scene.bin
      requires=[],                                    # quest ids that must be done first
      offer="Wolves keep raiding the farm...\nCan you thin them out? (5)",
      progress="Still {n} to go.",                    # {n} filled from the counter
      done="Thanks! Take this.",
      reward=dict(gil=500, items=[(3, 2)], materia=[]),
  ),
  "junon_letter": dict(kind="courier", key_item=..., to=dict(field="ujunon1", npc="new", ...)),
  "cosmo_ore":    dict(kind="deliver", item=..., count=3),
}
```

## 2. Quest state (save data)

- 1 byte per quest: 0 locked / 1 offered (not accepted) / 2 accepted /
  3 ready to hand in (kill/courier) / 4 done. A byte also leaves room for
  repeatable quests later.
- Kill quests: +1 byte counter each (more than 255 isn't needed).
- Space: bank 3 offsets 192-255 (savemap 0x0E64-0x0EA3, field nibble 11) are
  unused by field and world map scripts and the exe (research_battle.md;
  originally earmarked for Tame, now shelved). 64 bytes covers ~40 quests with
  kill counters. Bank 4 224-231 stay for openFF7's flags (232-255 are wiped by
  the world map; see CLAUDE.md). If we outgrow it, quest bytes can be packed
  (2 bits per finished quest) or moved to more verified-free space.
- "Locked" vs "offered" isn't stored: it's computed from `requires` each time
  (a quest whose prerequisites are all state 4 is available).

## 3. NPC dialogue (field scripts; all existing building blocks)

Talk script of a quest giver, generated per quest (or chained if one NPC has
several quests, in order):

| State | Behaviour |
|---|---|
| prerequisites not done | normal line (or nothing / the NPC's own talk) |
| available | offer text + choice "Accept / Not now" -> state 2 |
| accepted, not met | progress line ("Still 3 to go", "Bring me 2 more X") |
| met | completion text, take items (DLITM) if a delivery, give reward, state 4 |
| done | thank-you line |

Requirement checks per type:
- **deliver X items**: `CKITM item -> var`, compare with X; on hand-in `DLITM item X`.
- **courier**: on accept, the giver hands over a key item (key items are bits,
  BITON) or a normal item (STITM). The target NPC (another screen) checks it,
  takes it (BITOFF / DLITM), says its line and sets the quest to 3; the giver
  then completes it. (Option: target NPC gives the reward directly.)
- **kill X**: compare the quest's counter (see 5) with X.
- Rewards: gil `GOLDU`, items `STITM`, materia `SMTRA`, key items `BITON`.
  No field opcode gives EXP/AP directly (could hand out items like Sources).

All of this is the same machinery as the recruit/conductor/Choco Billy NPCs
(`_recruit.say`, `_travel.choice_menu`, `add_npc`, `asm.if_*`). New givers
are added NPCs (copied models, like Choco Billy); existing NPCs can be
converted by replacing their talk script (`Script.replace_script`).

## 4. The "!" marker — the open question

FF7's field engine has no icon-over-head feature. Options:

| Option | How | Cost / risk |
|---|---|---|
| **A. Floating marker model (recommended first)** | An extra entity per giver using an existing small model, e.g. the materia orb (`fieldbg_mtra3`), placed above the NPC's head, tinted with KAWAI 06 (yellow = available, blue = ready to hand in) and hidden (VISI 00) otherwise. | Data-only, quick. Uses 1 of the 16 models per screen (the cap that bit us before; the build enforces it). Looks like a glowing orb, not a "!". |
| B. Real "!" model | Author a tiny 3D "!" as a field model (HRC + RSD + P polygon file + texture) and add it to char.lgp; use it like A. | Needs a writer for the .p/.hrc/.rsd/.tex formats (new tooling), then the same as A. Best look, data-only. |
| C. Drawn in the background | Paint "!" into the screen's background tiles. | Static (can't hide when done); background format work. No. |
| D. Engine sprite | exe patch: draw a 2D "!" above flagged entities each frame. | Most flexible, deepest exe work. Not worth it now. |

Recommendation: A to build and test the system, then B to replace the orb
with a proper "!" using the same entity logic.

Marker updates: each marker's main script loops (check state, VISI on/off,
tint, WAIT ~10 frames), so it reacts right after accepting/completing and
after battles (the field isn't re-initialised after a battle).

## 5. Kill counting — needs one research step

Field scripts can't see battle results, so the counter has to be bumped from
battle. Two routes:

| Route | How | Notes |
|---|---|---|
| **Enemy AI (recommended)** | In scene.bin, add to the target enemy's AI "death" script: if its quest is accepted, +1 its counter (and set state 3 at X). Only quest targets are edited; every formation with that enemy shares its record. | Needs a scene.bin AI read/write tool (new: we only read formations now) and confirmation that AI scripts can write save variables. I believe they can (Ultimate Weapon keeps its HP between fights), but **unverified**; that's step 1. Ships `data/lang-en/battle/scene.bin`. |
| exe hook | Hook the reward loop (0x431481, where each defeated enemy is credited) to bump a per-enemy-id counter. | Counts everything with one hook, no per-enemy edits; exe work (proven possible). Fallback if AI writes don't work. |

## 6. Gating

`requires=[...]` → the offer branch is only reachable when every listed quest
is done (state 4); otherwise the NPC says its normal line and its marker stays
hidden. Chains can cross screens (quest B's giver elsewhere).

## 7. Nice-to-haves (later)

- Quest log: a "Quest board" NPC (inns/save points) listing accepted quests and
  progress. A real menu entry needs the exe menu work researched in
  research_menu.md (same path as the shelved Bestiary).
- Repeatable quests (state back to 1 with a cooldown), timed quests, escort...

## 8. Build order

1. **Research (small):** confirm enemy AI can write save vars; read the AI
   script format; pick 3-4 test quests with you.
2. **Framework + delivery types:** quest table, state bytes, giver/target NPC
   scripts, rewards, gating; markers as orbs (option A). Testable on its own.
3. **Kill quests:** scene.bin AI tool + death-script counters (or the exe hook).
4. **"!" model** (option B) replacing the orb.
5. Quest board / log.

## Decisions needed from you

- Marker look: OK to start with a floating orb (A), moving to a real "!" (B)?
- Who writes the quests: do you want to give me a list (giver, place, type,
  target, count, reward, prerequisites, lines), or should I draft a starter set?
- Should completing a quest also be possible when the target NPC is reached
  (courier) or always back at the giver?
- Rewards: gil/items/materia are easy; EXP/AP would need items or exe work.

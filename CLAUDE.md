# openFF7 — working notes for Claude

Open-world, story-free rebuild of FF7 (Steam PC). Game data is in
`FINAL FANTASY VII/` (Git LFS, read-only input); everything we ship is produced
by `tools/ff7tool.py build` applying `patches/*.py` to it. Python 3 stdlib only.

Read this file first. It holds what has been verified the hard way; check here
before re-deriving a fact from the game data. **Update it** when you verify
something new, hit a trap, or a feature's status changes.

## Where things are

| Need | Look in |
|---|---|
| What the user wants (decisions, recruit spots, travel rules) | `DESIGN.md` |
| Every function/class signature, one line each | `docs/api_index.md` (generated) |
| What to test in-game, install steps | `TESTING.md` |
| Midgar / rest-of-world pinning plans | `docs/midgar_plan.md`, `docs/world_plan.md` |
| Fields, locations, exits, battles, world map | `docs/inventory/` |
| .exe findings | `docs/exe_notes.md` |
| Shared constants (start point, flags, own vars) | `patches/_config.py` |
| Script dumps of the original game | `work/scripts/<field>.txt` (`ff7tool.py dump --all`) |
| Script dumps of the last build | `work/scripts_built/` (`ff7tool.py dump --built FIELD...`) |

## Commands

```
python3 tools/ff7tool.py build              # -> build/openFF7/, prints changed files (~2-4 min, run in background)
python3 tools/tests/test_formats.py         # all tests (~2 min), includes test_api_index_current
python3 tools/ff7tool.py api-index          # regenerate docs/api_index.md after code changes
python3 tools/ff7tool.py dump FIELD         # original script -> work/scripts/
python3 tools/ff7tool.py dump --built FIELD # built script -> work/scripts_built/
python3 tools/ff7tool.py scenes FIELD...    # simulate entering built fields, flag likely cutscenes
python3 tools/ff7tool.py reach FIELD...     # walkmesh entrance->exit reachability
python3 tools/ff7tool.py quiet-flags        # search 'seen' flags (slow, >10 min; background)
```

Shipped files: `data/field/flevel.lgp` and `data/lang-en/kernel/KERNEL.BIN`.
The user tests by copying them into the Steam install (see `TESTING.md`).

## Workflow rules

- Branch `claude/zen-bohr-fl1xp8`; commit + push when a change is done. No PRs unless asked.
- The user can't run anything here; they build and play on their PC. Say what
  is verified offline vs. untested in-game. Don't claim a fix works in-game.
- Patches are applied in file-name order; later patches see earlier edits
  (e.g. pinning in `100_midgar.py` rewrites IFs a later patch may look for).
- Find ops structurally (opcode + operands) and `assert` what you expect, so a
  wrong assumption fails the build instead of shipping silently.

## Patch map (`patches/`)

| File | Does |
|---|---|
| `010_new_game.py` | md1stin new-game block: SPCNM "Cloud", menu masks, party = Cloud, keycards, `INITIAL_EVENT_FLAGS` + `world_flags.json`, batteries, progress = 100, jump to start. KERNEL: Cloud level 1. |
| `100_midgar.py` | Pins Midgar fields to moments (`PINNED`), slums music, Train Graveyard trains moved. |
| `110_corneo.py` | Corneo's mansion open, Corneo removed. |
| `120_sector6_gate.py` | Sector 7<->6 gate both ways (guards moved, exit line widened, new gateway back). |
| `130_shinra_hq.py` | HQ 2F boxes openable. |
| `200`/`210`/`220_recruit_*.py` | Tifa (7th Heaven), Aerith (church), Barret (Mt. Corel mtcrl_3). |
| `250_train_destinations.py` | Station conductor menu, conductors at destinations, reactor doors, Guard Scorpion line, Air Buster NPC. |
| `300_kalm.py` | Kalm fields pinned at 400. |
| `400_world.py` | Everything else pinned via `world_moments.json` + `world_overrides.json`. |
| `900_phs.py` | Clears the PHS bit wherever a field writes the menu lock mask. |
| `_recruit.py`, `_travel.py` | Helpers: window/say/hide, recruit NPCs, choice menus, add_npc, add_line, beside, copy_model. |

## Core approach

- Story progress ("game moment") is `var[2][0]`; held globally at 100.
  Each field is **pinned**: `ff7.patch.localise_progress(script, const=M)` replaces
  its progress reads with the constant M (IFs, SETWORD, arithmetic, copies).
- "Seen" flags for scenes not keyed on progress are set at new game
  (`INITIAL_EVENT_FLAGS`, `world_flags.json`). `quiet-flags` only finds scenes
  that play **on field entry**; scenes triggered by LINE crossings or triangle
  checks (e.g. Kalm arrival) must be found by reading the script.
- openFF7's own save vars: bank 4 offsets 224-255 (nibble 13 = 8-bit), unused
  by the original scripts. `FLAGS` = (13,240) bits: 1 Guard Scorpion, 2 Air Buster.
  `RECRUITED` = (13,241) bit per character id. Temp vars (5,240),(5,241) for menus.

## Verified facts: field scripts

- Var nibbles: 1/2 = bank 1, 3/4 = bank 2, 11/12 = bank 3, 13/14 = bank 4,
  7/15 = bank 5, 5/6 = temp. 16-bit nibbles: 2,4,6,12,14,15. 16-bit vars use
  **byte** addressing (var[2][28] = savemap 0x0BC0). Bank 1 starts at savemap 0x0BA4;
  field vars can't reach past 0x10A4 (so not the config block / battle speed).
- Entity script 0 = init up to the first RET, then main. The engine runs all
  inits before any main. Script 1 = talk. LINE entities: script 2 runs when the
  player crosses the line.
- `IF*` = "if not (a op b) goto"; cmp 9 = bit_on, 10 = bit_off. So
  `asm.if_byte(v, "bit_off", b, skip)` skips when the bit is **set**.
- `BITON [banks][addr][bit]` (dst bank high nibble). INC ops: bank in the low nibble.
- REQ/REQSW/REQEW = [entity][priority<<5 | script].
- IDLCK [tri u16][on] locks walkmesh triangles. LINON 00/01 turns a LINE off/on.
- ASK [0x48][bank][window][text][first][last][var]; first/last are absolute
  line numbers including the speaker line.
- MAPJUMP [field u16][x][y][triangle][dir]; the (x, y) **must lie in** that
  triangle (some original arrivals are wrong because a scene repositions Cloud;
  tunnel_1 train-jump said tri 48, real is 205). Check with `Walkmesh.contains`.
- **UC 01 (player control off) persists across MAPJUMP.** Always UC 00 before
  jumping away from a menu, or fields that don't reset it freeze the player.
- **Script header byte 3 = model count** and must equal the model loader's
  count (true for all 702 fields). `BuildContext.save()` now syncs it. When it
  was wrong, added NPCs were visible but could not be talked to.
- TALKR is 0xC5 [bank][radius]; the station conductor uses 0x46.
- Menu visibility mask var[2][28] (0xFFFF = all), menu lock mask var[2][30]
  (set bit = greyed; 0x0100 PHS, 0x0200 Save). Early Midgar save points set the PHS lock.
- SPCNM (0F FD char text) sets a name. The .exe forces "Ex-SOLDIER" at new
  game, so the name is set in the script, not KERNEL.BIN.
- **Do not use SPECIAL GMSPD (0F F7)**: never used by the game; adding it to
  the new game caused a black screen. SMSPD is `0F F8 00 speed`.
- Triggers section: gateways at 0x38, 12 x 24 bytes, unused field id 0x7FFF.
- Model names include the source field prefix; copying a model between fields
  via `ModelLoader.add` works.

## Verified facts: KERNEL.BIN

- 27 gzip sections. Section 3 = new-game savemap data (9 x 132-byte character
  records, party, items, materia...). Section 2 = growth data.
- Growth: per character 0x38 bytes; first 9 bytes are curve ids (Str, Vit,
  Mag, Spr, Dex, Lck, HP, MP, EXP). Curves at 0x21C, 16 bytes = 8 brackets of
  (gradient u8, base s8); bracket = (level-2)//10.
  Primary = base + g*L//100; HP = base*40 + g*L; MP = base*2 + g*L//10;
  EXP to reach L = sum over 2..L of g*l*l//10. These reproduce every
  character's original starting record (`ff7.kernel.baseline`, `exp_for_level`).
- Character record: 0x01 level, 0x02-0x07 stats, 0x21 level bar, 0x2C cur/base
  HP, 0x30 cur/base MP, 0x3C EXP u32, 0x80 EXP-to-next u32 (meaning not fully confirmed).

## Field notes (things that bit us)

- mds7st3 (Sector 7 station): `border1` LINE boards the story train; kept off.
  Conductor = entity `guard` (model 6, shinra_guard).
- mds7plr1: gateway slot 2 is the exit to Sector 6 (mds6_2).
- nmkin_5 (No.1 Reactor core): bomb scene fires when entity `cl` is on
  triangle var[6][7] (init sets 2); we set 255. Shared with the No.5 visit (progress 120).
- elm (Kalm): arrival line checks (3,128,1) only — no progress check.
- Some fields have script sections the parser rejects (unused fields); catch
  `ValueError` when iterating every field.

## Status

Done (awaiting in-game confirmation where noted): new game start, Midgar
pinning, Tifa/Aerith/Barret recruitment, Corneo removed, Wall Market/HQ open,
wire climb, Sector 6 gate, train menu + conductors (untested), reactor doors,
Guard Scorpion line (untested), Air Buster NPC (untested), PHS unlock
(untested), Cloud level 1 (untested), Kalm arrival flag (untested).

Not done: battle speed default (needs .exe patch), other recruits (Red XIII,
Cait Sith, Cid, Vincent, Yuffie), remaining bosses as world NPCs + rare
encounters, vehicles (buggy, Tiny Bronco, airship, submarine), world-map
models for other leaders, minigame NPCs, shop scaling, crater bosses.

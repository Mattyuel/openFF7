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
| .exe findings | `docs/exe_notes.md`, `docs/research_menu.md`, `docs/research_battle.md` |
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

Shipped files: `data/field/flevel.lgp`, `data/lang-en/kernel/KERNEL.BIN`,
`data/wm/world_us.lgp`, `ff7_en.exe` (600_quests' kill hook) (plus
`kernel2.bin` only when a patch edits it; none does now). The build prints the list.
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
| `260_reactor_elevator.py` | Shared reactor elevator goes to the reactor you came from. |
| `270_sector4_duct.py` | Tunnel duct = plain choice; vent end offers drop / back to tunnel. |
| `280_chocobo_rides.py` | Choco Billy + chocobo by the world map exits of mds5_5 and psdun_1: ride out on a wild chocobo. |
| `300_kalm.py` | Kalm fields pinned at 400. |
| `400_world.py` | Everything else pinned via `world_moments.json` + `world_overrides.json`. |
| `600_quests.py` | Quest framework: givers + orb markers, kill/deliver quests (multi-target), "Quests" main-menu row + screen and the battle kill hook (both in `patches/asm/quest_menu.asm`, prebuilt `.bin` committed; reassemble with nasm after editing, `test_asm_bins_current` checks; `tools/tests/emu_quest_menu.py` runs it in unicorn if installed). Quest data (15 givers, 18 quests): `_quest_data.py`. Plan: `docs/quest_plan.md`. |
| `900_phs.py` | Clears the PHS bit wherever a field writes the menu lock mask. |
| `shelved/` | Not built: `500_tame.py` (Tame milestone 1), `950_leader_entities.py` (any leader). See `patches/shelved/README.md`. |
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
  by the original scripts. `FLAGS` = (13,224) bits: 1 Guard Scorpion, 2 Air Buster, 3 in No.5 Reactor.
  `RECRUITED` = (13,225) bit per character id, `RECRUIT_COUNT` (13,226).
  **Bank 4 offsets 232-255 are NOT free**: the exe's world map zeroes 232-243
  on entry and stores world map object data in 244-255; only 224-231 are safe.
  Bank 3 offsets 192-255 (nibble 11, savemap 0x0E64, memory 0xDC0B9C) look
  unused: quest bytes (`600_quests._allocate`: per quest a state byte + one
  counter per kill target, in GIVERS order; 192-224 used). Append new quests at
  the end of a giver or new givers at the end, or old saves' bytes shift.
  Temp vars (5,232)-(5,234) used by quest givers/markers. Temp vars (5,240),(5,241) for menus.

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
- **Unused script slots often point at a used script's code** (e.g. a LINE's
  slots 1-3 sharing one script, an NPC's 5..31 sharing 6). Replacing only
  `entry[ent][k]` leaves the others running the old code: use
  `Script.replace_script(ent, k, ops)`, which redirects every slot that shared it.
- Model loader entries carry their own scale (ASCII, e.g. "650"); fields use
  512 or 650 etc. Copy models with `ModelLoader.add_from(donor, i)`, which
  rescales to the target field (a 650 model in a 512 field looked too big).
- Menu visibility mask var[2][28] (0xFFFF = all), menu lock mask var[2][30]
  (set bit = greyed; 0x0100 PHS, 0x0200 Save). Early Midgar save points set the PHS lock.
- **PHS exit rule** (ff7_en.exe 0x700c22): opened from the menu, the PHS can
  only be left with exactly 3 in the party (opened by a field with a count
  param, that count). So the PHS entry is hidden until 3 are recruited
  (`RECRUIT_COUNT` (13,226), `_recruit.count_recruit`). Savemap 0x10A4 = PHS
  lock mask, 0x10A6 = PHS available mask (MMBUD). Party = savemap 0x04F8 (0xDC0230).
- SPCNM (0F FD char text) sets a name. The .exe forces "Ex-SOLDIER" at new
  game, so the name is set in the script, not KERNEL.BIN.
- **Do not use SPECIAL GMSPD (0F F7)**: never used by the game; adding it to
  the new game caused a black screen. SMSPD is `0F F8 00 speed`.
- **The PC opcode reads the field party copy** var[3][9..11] (savemap
  0x0CAD-0x0CAF), not the real party (savemap 0x04F8) that the PHS edits;
  party opcodes write the copy and sync it, the world map copies real -> copy.
  After a PHS swap the copy is stale, so `950_leader_entities` refreshes it with
  GETPC (reads the real party) at the start of every playable field.
  Original scripts test the leader as `var[3][9] == <char>`.
- **Party leader in fields**: the engine controls the entity whose `PC <char>`
  matches party slot 0 and hides other party members' PC entities (no VISI
  needed: see blue_2, which has all nine). PC entities used as NPCs (Tifa in
  7th Heaven, Aerith in the church) show themselves with VISI 01.
  `950_leader_entities.py` adds `CHAR m; PC c` entities so all 663 playable
  fields cover all nine characters (models from blue_2: stand/walk/run only).
  Interactions scripted on Cloud's entity (ladders, jumps) don't move another
  leader yet.
- **Max 16 models per field**: the engine's model table is a static array
  (0xCC1670, 0x88 each, next variable at 0xCC1EF0). Exceeding it corrupted
  memory (md1stin at 18 models played the opening FMV on new game, leader
  swap failed). The build refuses > 16; `950_leader_entities` fills only the
  room left, in priority order, and falls back to Cloud for a leader without
  an entity there.
- **Leader interactions:** ladders/jumps (e.g. mds7 border1/border2 ->
  REQSW to entity `cloud` script 12: MOVE/LADER/JUMP) run on Cloud's entity;
  with another leader the player gets stuck. Needs redirecting per field.
- Cutscene copies of party members hide themselves on field load (VISI 00
  in their script 0; 147 fields). When that character leads they'd be an
  invisible player, so `950` guards each such VISI 00 with `var[3][9] != char`.
- `CHAR` indices always follow entity order and the CHAR count equals the
  model count in every field: append models and CHAR entities together.
- GETPC `[0x74][dst bank][party slot][var]`: slot 0 = leader (`_recruit.get_leader`).
- **Riding a chocobo onto the world map:** savemap bank 1 byte 126 (var[1][126]):
  bit 0 = wild chocobo (world map model 4, runs off when dismounted), bit 1 =
  stable chocobo, bits 2-6 = its colour (model 0x13); set the bits then
  MAPJUMP to a `wmN` field id with x = y = 0 (as frcyo's Choco Billy does).
  World map entries: mds5_5 -> wm0, psdun_1 -> wm4, psdun_2 -> wm3.
  **The bit alone doesn't mount you**: wm0.ev function 1 dispatches on
  `push_special 6` (= the wmN field id you arrived by) and only the farm branch
  (== 3) checks the bits and runs `op_300 <model>; op_30C` (mount). 280 appends
  a mount block for its own exits (`ff7.worldmap.EvPatcher`: wm*.ev are fixed
  0x7000 bytes with zero padding; append + repoint a goto, nothing moves).
  **Mount before placing**: the mount must run before the branch's op_308/op_309
  placement (as in the farm branch); mounting after it left the chocobo at the
  map origin (top-left, in the sea). 280 redirects the branch start to
  [mount block + copy of the branch body].
  World map tutorials are messages in world_us.lgp `mes` (53 world map save,
  57 buggy, 58 Tiny Bronco, 59 chocobo, 61 submarine) gated by bits; world map
  bit address b = savemap 0x0BA4 + b//8, bit b%8 (e.g. 0x1C2B = bank 4 off 133
  bit 3). Shown by `op_324` (window) + `op_325 <msg>`.
- Chocobo field models (`AQGC.HRC`) aren't yellow by themselves: scripts tint
  them with KAWAI 06 (fship_5/frcyo: yellow = `1e 00 0f 00 c4 ff`).
- Cloud is locked as leader (MMBLK 00 at new game); leader swapping shelved.
- **Screen position of a field point**: `ff7.camera.Camera(section 1).project(x, y, z)`
  (GTE: zoom * (R.v/4096 + T), y down, relative to the background centre);
  scroll limits = triggers header +12 (`screen_range`). Checked on md8brdg only.
- **DIR / facing**: direction d (0-255) faces field vector (sin a, -cos a),
  a = d*2pi/256 (fitted on 116 gateway arrivals; 0x40 looked right at mds5_5
  in game). `ff7.camera.facing_screen(cam, x, y, z, (0, 1))` = DIR facing down
  the screen. NPCs turn to the player on talk with `PTURA 00 08 02` (+ WAIT).
- Sounds (SOUND F1 00 <u16 id> 40): item received 0x168, materia 0x1EA (as
  the original scripts use them); `_recruit.sound`, `SOUND_*`.
- Triggers section: gateways at 0x38, 12 x 24 bytes, unused field id 0x7FFF.
- Model names include the source field prefix; copying a model between fields
  via `ModelLoader.add` works.

## Verified facts: ff7_en.exe (static reading, capstone)

- Field opcode handler table: 0x9055A0 (256 dwords). Current entity 0xCC0964,
  script positions 0xCC0CF8 (u16 per entity), model structs at [0xCC0B60]
  (0x88 bytes each; entity -> model 0xCBFB70), field header ptr 0xCBF9D8
  (+0x10 = field scale).
- MSPED (0x618369) writes model+0x76 = speed*scale>>9; default at field load
  = 0x400 equivalent; scripted MOVE runs when speed > 0x600. **Player-controlled
  walking does not read +0x76**, so MSPED can't speed up the player: player
  speed is hard-coded elsewhere (not found yet).
- World map models are field-style files in world_us.lgp (.hrc/.rsd/.p/.tex/.a);
  the exe holds per-map-variant .hrc name tables (~0x56B289 in the file). The
  leader -> world map model choice is in the exe (not in wm*.ev); not found yet.
- **New code section works** (user-confirmed: code in an added `.openff7`
  section runs). Build it with `ctx.exe()` (`ff7/exebuild.py`: `alloc`,
  `place_at`, `patch`, `patch_u32`); the build writes `ff7_en.exe`.
- Per-command action info: table 0x7B7510 (4 bytes x 0x26 commands: action
  animation -> ctx+0x1C, byte -> ctx+0x20, u16 damage formula -> ctx+0x40;
  read at 0x435FF5-0x436029). A new command needs an entry (all-zero = hang).
- kernel2.bin and KERNEL.BIN (sections 9-26) both hold the text; the build
  mirrors every kernel2 edit into KERNEL.BIN (names showed blank otherwise).
- Battle command routine sequences: table 0x7B75A8 (segments per command,
  0x1F-separated), readers 0x43656A/0x436B6A (disp32 +2), bound imm8 at
  0x436B44. kernel2.bin text via `ctx.kernel2()` (`ff7/kernel2.py`, keeps
  sections byte-exact, appends changed strings; pool limit 0x6C00).
- Party slots: 0xDC0230 (savemap 0x04F8). PHS exit check: 0x700C22.
  Savemap base in memory = 0xDBFD38; field var bank 1 = 0xDC08DC.
- **Victory reward loop** 0x431481: slot [ebp-4] 0..5, enemy type [ebp-0x20]
  (word 0x9A8794+slot*16), record 0x9A8E9C+type*0xB8; enemy id = word
  0x9A8748+type*2 (3 types; also read at 0x5D0816). Skipped when fled
  ([0x9AE11C]&0xDE). A defeated, not-removed enemy reaches 0x431536
  (`8B45FC 83C004`), hooked by 600_quests to count kills.
- Main menu labels (FF7 text, 20-byte slots) at VA 0x91A8C0 (Item, Magic,
  Materia, Equip, Status, Order, Limit, Config, PHS, Save, Quit, then unused
  "Beginner"). Menu framework: `docs/research_menu.md`. **Menu id 11 is an empty
  stub** (init 0x6FEB00 / update 0x6FEB0F) and row 10's row->id byte is already
  0x0B, so a row before Quit opening id 11 needs no title/cursor-return change:
  600_quests' `MENU_PATCHES` (row count 11->12, heights +0x1A, masks, labels,
  12-entry confirm table). `.openff7` layout: quest data block at 0xFD5000
  (12 KB max), quest code at 0xFD8000, then the confirm table. Submenu API used by quest_menu.asm (text colours:
  0 grey, 4 green, 5 cyan, 6 yellow, 7 white; smaller z = in front).
- exe patching: `ff7/exepatch.py` (expected-bytes checks + PE checksum, which
  reproduces the original's). `ff7tool.py exe-test` makes a harmless test exe;
  **Confirmed by the user: a modified exe (.data and .text changes, checksum
  fixed) runs fine through Steam.** So exe patching is a viable route.
- Field opcode handlers: PC 0x61BCD7 (compares char with the field party copy
  0xDC09E5; leader -> field header+0x2A = player model index), GETPC 0x61F238
  (reads real party 0xDC0230), PRTYP 0x61BE95, IFKEY 0x61220D, MSPED 0x618369.
- Input: global button mask 0x9A85D4 (read by 0x7186B9); each frame 0x75EF46
  copies it into the field header +0x68 (held) / +0x70 (newly pressed) and
  +0x78/+0x80. IFKEY tests header +0x68.
- Player-controlled movement code: not found yet (doesn't read model+0x76
  directly; no field code reads the global input mask).

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
- Reactors: No.1 rooms nmkin_1-5, No.5 rooms smkin_1-5; only the elevator
  elevtr1 is shared and chose by progress (< 33 = No.1). `260_reactor_elevator.py`
  uses FLAG_IN_REACTOR5 (13,224 bit 3), set in smkin_1/2, cleared in nmkin_1/2.
- tunnel_2 duct = entity `cloud` script 4 (Barret/Tifa scene); sbwy4_1 ladder ->
  sbwy4_4 vent; vent end line1 drops to sbwy4_5 (onward to No.5).
- md8brdg: md8_3's arrival (-422,1387) is at the top of the screen; train uses (-420,100,tri 33).
- nmkin_5 (No.1 Reactor core): bomb scene fires when entity `cl` is on
  triangle var[6][7] (init sets 2); we set 255. Shared with the No.5 visit (progress 120).
- elm (Kalm): arrival line checks (3,128,1) only — no progress check.
- Some fields have script sections the parser rejects (unused fields); catch
  `ValueError` when iterating every field.

## Status

Done (awaiting in-game confirmation where noted): new game start, Midgar
pinning, Tifa/Aerith/Barret recruitment, Corneo removed, Wall Market/HQ open,
wire climb, Sector 6 gate, train menu + conductors (untested), reactor doors,
reactor elevator (untested), duct/vent (untested), PHS hidden until 3 recruits (untested),
field leader entities (untested),
Guard Scorpion line (untested), Air Buster NPC (untested), PHS unlock
(untested), Cloud level 1 (untested), Kalm arrival flag (untested).

Quests (600): first 3 givers user-confirmed working (orbs, menu, kill counting).
12 more givers / 15 quests added from the user's list (untested): multi-target
kill quests, quest log scrolling (8 rows visible), Sam's chocobo companion.

Not done: world map leader models + new models (needs .exe work), player
leader-aware interactions (ladders etc.),
battle speed default (needs .exe patch), other recruits (Red XIII,
Cait Sith, Cid, Vincent, Yuffie), remaining bosses as world NPCs + rare
encounters, vehicles (buggy, Tiny Bronco, airship, submarine), world-map
models for other leaders, minigame NPCs, shop scaling, crater bosses.

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
| Dates with the girls (gondola / space capsule): plan, decisions, FMV facts | `docs/dates_plan.md` |
| Fields, locations, exits, battles, world map | `docs/inventory/` |
| .exe findings | `docs/exe_notes.md`, `docs/research_menu.md`, `docs/research_battle.md` |
| One-off story scenes outside Midgar (applied / open) | `docs/research_story_scenes.md` |
| Shared constants (start point, flags, own vars) | `patches/_config.py` |
| Field animations: names, what they look like, our own poses, limits | `docs/animations.md` (keep it current) |
| Script dumps of the original game | `work/scripts/<field>.txt` (`ff7tool.py dump --all`) |
| Script dumps of the last build | `work/scripts_built/` (`ff7tool.py dump --built FIELD...`) |

## Commands

```
python3 tools/ff7tool.py build              # -> build/openFF7/, prints changed files (~2 min first time, ~12 s after: build/cache)
python3 tools/ff7tool.py build --debug      # + patches/debug/ (L1+R1 debug menu) -> build/openFF7_debug/
python3 tools/tests/test_formats.py         # all tests (~2 min), includes test_api_index_current
python3 tools/ff7tool.py api-index          # regenerate docs/api_index.md after code changes
python3 tools/ff7tool.py dump FIELD         # original script -> work/scripts/
python3 tools/ff7tool.py dump --built FIELD # built script -> work/scripts_built/
python3 tools/ff7tool.py scenes FIELD...    # simulate entering built fields, flag likely cutscenes
python3 tools/ff7tool.py reach FIELD...     # walkmesh entrance->exit reachability
python3 tools/ff7tool.py quiet-flags        # search 'seen' flags (slow, >10 min; background)
```

Shipped files: `data/field/flevel.lgp`, `data/lang-en/kernel/KERNEL.BIN`,
`data/wm/world_us.lgp`, `ff7_en.exe` (600_quests' kill hook),
`data/field/char.lgp` (quest marker models, `_marker_models.py`),
`data/lang-en/kernel/kernel2.bin` (625's gift key item names). The build prints the list.
The user tests by copying them into the Steam install (see `TESTING.md`).

Build speed: LZSS (pure Python) was ~95% of a build. Original fields are
decompressed once into `build/cache/raw` and changed fields' compressed form is
cached by content in `build/cache/lzss` (compressed on all cores when missing),
so later builds only recompress fields that changed. Output is byte-identical;
delete `build/cache` (~350 MB) any time.

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
| `130_shinra_hq.py` | HQ after the infiltration: 2F boxes openable, access level 69 kept (var[1][224] lowering writes removed in blin59/61/62_1/65_1/67_1/68_1), flags (3,168,1) 59F guards, (3,172,3) 60F sneaking, (1,226,5) 68F scientist; blin67_3 pinned 285; roof (blin70_3) Rufus on the pad + line -> formation 464 once per visit; 69F (blin69_1) elevator doors: ride / fight (formation 460 -> 461 Hundred/Heli Gunner, FLAG_ELEVATOR_FOUGHT). |
| `150_midgar_fixes.py` | Sector 7 item store open (mds7 doorway IDLCK 0x11 + closed-sign gate removed; flag (3,213,6) can't be used: hides Barret/Tifa); Honey Bee Inn door unblocked (mrkt3 lackey/passer-by moves removed); ghost NPC on the playground (mds6_2). |
| `160_midgar_disc2.py` | Gateway md8brdg right end <-> md8_5 left end (8th Street; its own exit leads to md8_6, the hatch); disc 2 route state via bank 5 offset 128/135 new-game flags; canon_2 pinned 1604. Turks/Proud Clod/Hojo = Shinra Deserter quest bosses (md8brdg; disc 2 fields have ~254 texts, no room). md8_5: ff7.camera's screen x is right but every floor point projects to one band in y; the floor's -x end is off screen (x < -1100), so the line back is at x -1100. |
| `170_pillar_sewer.py` | Sector 7 pillar gate open both ways (mds7plr1 tobira BG state 1, BGanim main REQSW tobira 2 -> 1 (it re-closed the picture on load), stagedr IDLCK 0x104 removed); Reno boss line right of the stairs' top (pillar_2 x -100, always); Biggs/Jessie/Barret story copies on pillar_1/2 hidden (pillar_3 cutscene field unreachable; pillar text tables are FULL); colne_b3 west dead end line back up to colne_b1 (pinned 209). |
| `180_motorbike.py` | Biker NPC in front of HQ (sinbil_1): MINIGAME 0x20 game 0 (story mode var[3][115]=0) returning to roadend; roadend scene/party copies off, line up (x 700) = Motor Ball 468 once per visit, line down (x -2150) -> sinbil_1; roadend init redoes blackbgb's sound reset (AKAO b8/c1/a0-a3 7f; the bike exit leaves channel volume 0) + AKAO 10 21 (play id 34). MINIGAME op = 20 [field u16][x][y][tri u16][param][game]; games: 0 bike, 1 chocobo, 2 snowboard (Icicle), 3 Condor, 4 sub, 5 Speed Square, 6 snowboard (GS). |
| `200`/`210`/`220_recruit_*.py` | Tifa (7th Heaven), Aerith (church), Barret (No.1 Reactor platform md1stin). |
| `230_recruit_more.py` | Recruit NPCs: Red XIII (blin67_1), Cid (junair airstrip), Cait Sith (del3 beach), Yuffie (frcyo by the left pen, yougan2 model anim 6), Vincent (onna_2 dancers' room); KERNEL new-game records 6/7 = the exe's Cait Sith / Vincent templates with default names (no naming screen). Original Yuffie/Vincent joins count only if not already recruited. All recruit talks start with PTURA (face the player). |
| `250_train_destinations.py` | Station conductor menu (Upper Midgar md8brdg, Shinra Tower sinbil_1, No.1 md1stin, No.5 tunnel_2 — not tunnel_1, which loops onto itself), conductors at destinations (`CONDUCTOR_AT` overrides; Upper Midgar (-240,100)), reactor doors (smkin_1's three-button door models CHAR 3/4 hidden: it read as shut), Guard Scorpion line, Air Buster NPC (southmk1 has no PC op: model 0 = player by default). |
| `260_reactor_elevator.py` | Shared reactor elevator goes to the reactor you came from. |
| `270_sector4_duct.py` | Tunnel duct = plain choice; line below the duct (sbwy4_1, left of the landing) back to tunnel_2; vent (sbwy4_4) left original (a menu on its far ladder line reopened while standing on it). |
| `280_chocobo_rides.py` | Choco Billy + chocobo by the world map exits of mds5_5 and psdun_1: ride out on a wild chocobo. mds5_5's Billy also rides to mds6_3 (Sam, `TOWN_RIDES`); Sam rides back after his quest (giver `ride=` in `_quest_data`, handled by 600 `_ride`). |
| `300_kalm.py` | Kalm fields pinned at 400. |
| `400_world.py` | Everything else pinned via `world_moments.json` + `world_overrides.json`. |
| `410_world_fixes.py` | Mideel always disc 3 (wm0), shpin_3 Jenova line off, Junon elevator line open, Gate of Naught open (cosin2: door opening on every entry, cave floor lock IDLCK 0x29 + "only Bugenhagen" line removed). |
| `415_temple.py` | Temple of the Ancients open as if explored up to the Demon Wall: every temple field pinned 631 (kuro_82 627: at 631 it fell into the Red Dragon arrival scene), 'done' flags (3,234)/(3,233) in INITIAL_EVENT_FLAGS (treasure bits bank 5 112-113 left); jtmpin1's altar (border1 OK -> cloud script 6, only acted at 604) now jumps to the warp (cloud script 11) with UC 00 before MAPJUMP kuro_1 at (66,156,tri 297) (the original (0,0) tri 0 relied on the arrival scene); way out = kuro_12's exit line (open with (3,233) bit 4), and a Temple Guide in kuro_1 beside the arrival (takes over the unused PC entity `vince`, kuro_1 at 16 models; model rckt:8) whose talk MAPJUMPs to jtempl (509,760 tri 40) before the door. Ancient Dragon still fights on every kuro_5 entry (original). Quest giver archaeo at jtempl (640,-1400), right of the path to the exit. |
| `430_buggy.py` | Buggy salesman (Dio model) at Costa del Sol's town exit (del2): 1000 gil, sets (1,127) bits 0+1 and MAPJUMPs to wm12; wm0's Costa del Sol branch already mounts the buggy (asserted). |
| `440_corel_prison.py` | Buggy into the world map Gold Saucer -> desert2 (vanilla wm0 0xA964); desert2's bottom/left lines now go to jail1/jail3; convict in jail1 drives you out (buggy bits + MAPJUMP wm15). |
| `450_highwind.py` | junair2 runway line (y -2400) -> Highwind owned/aboard (bank 1 byte 127 bits 4/5 = wm 0x3FC/0x3FD) + MAPJUMP wm40 (wm0 mounts model 3 near Junon); wm0 system function 6 ([Menu] in the air -> fship interior, exe 0x74F676) starts with `return`. |
| `420_cargo_ship.py` | Upper deck party-change copies hidden (ship_1); First Mate (ship_2) takes you ashore at Costa del Sol. Jenova BIRTH = quest boss line (600). |
| `600_quests.py` | Quest framework: givers + sprite markers (star = offer, heart = accepted until hand-in; models QSTA/QHTA built into char.lgp by `_marker_models.py` from magic.lgp s_guard.tex / heart01.tex on the gujc.hrc skeleton; one star + one heart entity per *field* (`_add_markers`), each with its own model, moving to the first giver it applies to; star only where 16 models don't allow both. Never let two entities share a model: md8brdg's two givers once shared the star/heart models (18 CHARs, 16 models) and crashed on arrival intermittently), kill/deliver quests (multi-target), "Quests" main-menu row + screen and the battle kill hook (both in `patches/asm/quest_menu.asm`, prebuilt `.bin` committed; reassemble with nasm after editing, `test_asm_bins_current` checks; `tools/tests/emu_quest_menu.py` runs it in unicorn if installed). Quest data: `_quest_data.py` (Midgar + cargo ship) and `_quest_data_world.py` (21 givers outside Midgar); 44 givers, 87 quests, 16 boss lines; follow-ups on early givers use late=True (allocated after every other quest). Kinds: kill, deliver, count (counter bumped by `count_ops`/exe), visit (`spots`: lines that tick when crossed), courier (`target` NPC elsewhere); kill-table fake ids BIKE 0xFFFE / BALLOON 0xFFFD are counted by exe hooks in the bike game (0x6566B9) and snowboard (0x737D45 before the balloon-type switch, so all colours and the special types 3/4 count, and 0x73C52A; Icicle mode only). Every reward adds Sources (`source_count(level)`: 1 at Midgar levels, 8 at level 50). Plan: `docs/quest_plan.md`. |
| `620_honey_bee.py` | Honey Bee Girl recruitment (data `_honey_bee_data.py`, 20 adult girls, stars 1-5 = questions): manager NPC in onna_4 (Scotch's model, colne_3 model 4 market_youjin_r; a Honey Bee girl either side; job bit HB_JOB, visit menu = one page per star rating (One Star Girls .. Five Star Girls: 4 rows 'Name (tag)' or '????' if not hired (picking it re-shows the page), Next page / Previous page / Never mind; one ASK text per page per hired combination = 80 texts, onna_4 at 137/255) -> visit); girls `hbNN` in 20 fields (talk: stranger / pitch + questions, all asked, a wrong one flagged in temp (5,246) and judged at the end / idle); visit = MAPJUMP onna_52 (at the bed (211,102): onna_4's own arrival is on the girl's path and she ran into Cloud forever) with HB_VISIT = i+1: produce main + border1 LINE guarded off, produce init plays block 0 (id 68, the lobby's Honey Bee theme; else (3,220) bit 0 off gave the dream music), Cloud SOLID 01 + walks to STAGE (0,150, mid-room) first; girl appears just inside the door (263,163) with the door opening (door scripts 1/2, sounds 0x7A/0x11D) and walks only (WALK 0x0400; 0x0800 ran; runs/loops got stuck); scenes in `_honey_bee_scenes.py` (≤7 texts each, onna_52 at 220/255); dancer animation meanings from the user in 620's DANCER comment; director entity `hbscene` REQEWs beats added in free script slots of girl2 (8+) and one Cloud dispatcher slot (24+; the director sets temp ACT (5,250) then REQEWs it; Cloud gets 19 extra anims, `CLOUD_EXTRA`, user-chosen, plus `CLOUD_BED` poses incl. our own zcta.a / zctb.a / zctc.a / zctd.a / zcte.a (`_cloud_thrust` mission, `_cloud_pound` dog, `_cloud_spread` (unused now), `_cloud_buck` cowgirl/ontop, `_cloud_stand` head: both on the floor left of the bed, Cloud standing at `HEAD_STAND` (-20,-180) facing screen-left, the girl kneeling `HEAD_GAP` 30 further left facing him, DZBK rocking; `edge` (Tifa): the girl standing bent over the bed's left end at `EDGE_GIRL_MOVED` (-5,-180: the floor ends at x -5 there) facing screen-right (dzbg.a, `_bend`), Cloud at `EDGE_CLOUD` (-16,-180) in zctf (zcte with arms 60 and the left leg raised: hip 100, knee 10), facing the bed; after Tifa's "Faster!" both switch to 8-frame copies (dzbi / zctg: beats `bendf` / `standlf`); `headrev` (Elena): she lies on her back along the bed (dzbh.a, `_on_back` with `HEADREV_*`), XYZI `HEADREV_GIRL` (94,-180) = by her feet (her head top is ~94 field units along her: 27 model units x ~3.4), DIR 0x40 so her head points screen-left with the neck at the bed's left edge; Cloud in zcte at `HEADREV_CLOUD` (-8,-180); Celeste too; her hips held `HEADREV_LIFT` up and her head hanging straight down (`head_down`); `HEADREV_GIRL` now (88,-180); cowgirl's girl `COWGIRL_LEFT` 8 left with her own dzbl.a (arms/head rock); head/headrev girls' devoted lines are muffled (user); all strokes 0.5 s = 15 frames (user); devoted part two plays `PART2_MUSIC` from the bed fade: AKAO 10 index 5 FANFARE, 46 FAN2 for dog, `PART2_MUSIC_GIRL` per girl (FIDDLE 8, PARADE 16, CHASE 38, DATE 49, GEKI 62, SID2 72 = Steal the Tiny Bronco? unconfirmed); every visit's closing text plays `END_MUSIC` 57 YADO (inn); music name table 0x9684C8 is a pointer table, 99 names; docs/animations.md); avoid BICA fall / EACF arms up), fade, final line, back in the lobby at BACK_AT (0,-250: centre, near the entrance). A scene starting `("start", "bed")` (Bambi) places the girl on the bed (136,-199, DIR 0x40, DZBA) in girl2's init and Cloud's intro is `intobed` (stops at (220,161), level with the bed on screen, TURA girl; walking further down hit the bed). girl2's model gets all 22 Honey Bee dancer anims (`ModelLoader.with_anims`). Income: manager "Collect" pays HB_RATE (2) gil x total stars x minutes since the last collection (cap HB_CAP 270) via GOLDU var + MPRA2/{VAR}; minutes come from the exe play clock hook (0x40ABF0 -> quest_menu.asm q_clock writes var[2][247]). Save: bank 1 247-255 (`_config.HB_*`). A girl with `reuse="entity"` (Velvet in coloss, 16 models) takes over an entity the pinned moment hides (`_reuse_entity`: its model entry becomes hers, its init's CHAR is replaced in place + jump over the rest, so no second CHAR). Lounge rooms (`_lounge`): onna_4's four side doors (border1/2 left -> rooms 1/2 in onna_52, border3/4 right -> rooms 3/4 in `FLIPPED` = new field onna_1; produce init's IDLCK 0x13/0x1C/0x1E/0x04 removed, border5-8 room-choice talk -> RET) set HB_VISIT = 100 + room; 5 girls per room (room r: girls 5(r-1)..+4) on 5 of onna_52's 10 extras zax/muki1-9 (models 2-11 -> the dancer with 22 anims, only used by the disabled original scenes), shown only if hired, SOLID 01, `LOUNGE_SPOTS` (kinds lie / sit / stand: sit and stand girls loop `_idle_loop` = RANDOM pause from `PAUSES` then a RANDOM anim from `SIT_ANIMS` (held) / `STAND_ANIMS` (once, back to idle), each girl with her own temp var (5,200+k); the bed is a separate walkmesh piece at z 76: bed girls within ~40 of the floor, TALKR 0x60), talk = `_honey_bee_data.LOUNGE` (lie girl: no PTURA, TALKR 0x70; sit girl drawn SIT_DROP 25 below the bed (floated); per-spot DIR offsets); produce init turns the menu back on, border1 LINE moved to `EXIT_LINE` (across the way in, before the door: the original was past it), lobby arrival `ROOM_ARRIVAL` (215,120) clear of it; crossing it plays the door (sound 0x7A + door script 1) and returns to the lobby door you came by (ROOM_EXITS), clearing HB_VISIT; the visit director ignores >= 100. **FLIPPED room**: `ctx.new_field(name, raw)` adds a field under an unused maplist name (onna_1/onna_3/onna_6 have no file); built from onna_52 after the lounge edits: `ff7.background` (PC section 8 parse/build, byte-exact on all 702 fields; `flip_horizontal` mirrors tile dst x and flips each texture area once; layer 1 tiles store size 0 = 16), `walkmesh.flip_x` (x negated, vertices (v0,v2,v1), access reversed), `camera.flip_x` (every 38-byte block: row 0 / column 0 negated except [0][0], pos x negated), scroll range mirrored, exit LINE mirrored; spots mirrored (x -> -x, DIR from the flipped camera); `test_mirror` checks it. **Affection + gifts** (`_honey_bee_gifts.py`): `_config.HB_AFFECTION[i]` (bank 1 188-196, 200-207, 210-212), 0-20; lounge talk shows it (SETWORD temp word (6,222) + MPRA2) and REQEWs entity `hbgift` script 1 with GIFT_GIRL (5,220) (hbgift needs its own `[RET, RET]` script 0: with only slot 1 set, `add_entity`'s shared empty RET made the routine its *main*, which opened the gift menu on entering the room): nothing at 20 or with no gift held, else each held gift in turn (one ASK text per gift: Give it / Next gift / Not now; gifts not held are skipped), BITOFF the key bit, PLUS by `PREFS` (L 2 / I 1 / H 0, capped 20), shared reaction texts (onna_52/onna_1 at 132/255). Visit routing in the manager: affection >= 20 -> `DEVOTED_ROOM` onna_6, >= 10 -> `CLOSE_ROOM` onna_3, else `BASIC_ROOM` convil_3 (onna_52 itself keeps only the lounges: `_room` with empty scenes, 132 texts); all three are new fields copied from onna_52 *before* `_room`'s edits, each built by `_room(ctx, back, field, scenes, final)` with `_honey_bee_scenes_more.CLOSE` / `DEVOTED` (198 / 196 texts). A scene starting on the bed may not use walking girl beats (asserted; the bed is a separate walkmesh piece); only basic Bambi still starts there (user: girls walk in). Devoted part twos start in one of the user's positions (`BED_LAYOUTS` mission / cowgirl / ontop / dog / head, offsets `RIDE_RAISE`, `HEAD_*`, `DOG_CLOUD`; `LAYOUT_BEATS` = beats allowed after each, asserted). Devoted room part two uses entity `cloudb` (model 12: Cloud's entry with every anim, `ModelLoader.with_hrc` -> zcla.hrc from `_bare_cloud`: pants colour (B,G,R 119,73,97) -> the arms' skin (135,167,248) on pelvis/thighs/upper shins, knee rings (thigh z -5.08, shin z 0) shrunk to the thigh's hip-ring radius ~1.58 around the knee-tip vertex's axis, the tip cone shortened by the same factor (else a forward spike); new rsd ZCLB-F -> .p ZCMB-F); the bed step REQEWs cloud's 'hide_<layout beat>' (VISI 00 + XYZI to the bare Cloud's spot: the camera follows the player entity) and cloudb's dispatcher (slot 2, same ACT numbering, VISI 01 first). Visit rooms (convil_3 / onna_3 / onna_6) are dimmed to `ROOM_LIGHT` 0.5 by `_dim`: background palette colours (15-bit, 0 -> 0x8000 so nothing turns transparent) and each model loader entry's light block (+2+name+2+8+4+2: 3 x (RGB + s16 dir x3), then ambient RGB) scaled. Scarlet's spot: blin66_1 gateway 2 (to blin66_2) now goes to blin66_6 (same layout/arrival tri 169); blin66_6's scarlet/hyde/leave are unplaced but visible at 998, hidden; its drctr main's `REQ cloud script 3` (VISI 00) removed (player was invisible). |
| `622_hb_kids.py` | Honey Bee kids: 620's devoted-room director BITONs `_config.HB_KID[i]` (bank 1 214-216) at the end of girl i's scene; each girl field gets a kid NPC (`KIDS`: donor model + one line) placed ~20 screen px beside her (`_beside`, camera-projected), hidden in its init (TLKON/SOLID/VISI) while the bit is off. coloss (16 models): Velvet's kid takes over hidden arena kid `gaki2` (gon_girl) via `reuse_npc` + the hide guard; nivinn_1 (16 models, nothing hidden: Zangan, innkeeper, party) -> Rhonda's kid in nivl_3 by the inn door (`ELSEWHERE`; takes over hidden cloaked man `mant2`, nivl_3 at 16 models). **nivl is the flashback Nibelheim; the present-day town (world map, inn exit) is nivl_3.** `KID_OFFSET` (screen px behind the girl) / `KID_AT` place kids that blocked paths (user). Child models (rendered and checked): std_girl2 mds7st3:11, std_girl3 frcyo:3, std_boy2 elm:12 (red cap), std_boy3 mrkt1:8 (goggles), midgal_child mds7:9, farm_boy frcyo:4 (cowboy hat), nible_boy niv_ti3:6 = gon_boy games:7, nible_girl nvmin1_1:10 = gon_girl games:8, cosmo_girl cosmo:3, cosmo_boy cosmin3:5, kosta_rgirl del2:9, kosta_sboy del2:11 (snorkel), kosta_sgirl del2:12 (swimsuit), snow_child snow:10, utai_child uutai1:11; gold_cgirl (crcin_1:4) is an adult. |
| `625_gift_shops.py` | Gift Merchant (del2 model 9 kosta_rgirl; the HQ 60F woman looked odd) in mrkt2, del2, cosmin7 (left hut), uutai1 (`_honey_bee_gifts.SHOPS`, spots picked on rendered backgrounds): 3 gifts each = key items 51-62 (names/descriptions written to kernel2 sections 15/7; blank in the original), CHGLD/GOLDD as 640, BITON the key bit, refuses a gift already held. |
| `630_bounties.py` | Bounties: reporter Scoop (junbin4 model 8, junon_report1) in 8 bars (`REGIONS`: mds7pb_1, elmpb, junpb_3, delpb, cos_btm (bottom level by the bar door; takes over hidden prop PROPED via `_travel.reuse_npc`: 16 models), nivinn_1 (+ rktinn1 via `also`), utapb, sninn_b1), one bounty per region, pools = each region's rarest random enemies (enc_w.bin region tables + dungeon fields ranked by encounter share), 30 min, gil = kills x level x 75. Hunter points `_config.HUNTER_PTS` (bank 1 245-246, saved, lifetime; taken off the last quest area) += region `points` (1 2 3 4 6 8 11 15, Midgar .. Icicle) per claim, clamped to the region's `cap` rank (Midgar Tracker, Kalm Hunter, Junon/Costa Veteran, Cosmo/Nibel Elite, Wutai Master, Icicle Legend: `cap_points` = next threshold - 1; at the cap Scoop says so), shown with MPRA2 in the payout line; rank = `RANKS` threshold (Rookie 0 .. Legend 250), rank-up line when one is crossed. elmpb at 252 texts (Devil Ride dropped from Kalm's pool to fit). State only in exe memory (quest_menu.asm `b_state`, never saved; cleared when the play clock jumps = load/new game; expired ones dropped on the clock tick and on every command). Field opcode 0x1C BOUNTY `1C [dst bank<<4][dst][cmd][region]` (cmd 0 status 0/1/2, 1 offer, 2 accept, 3 claim, 4 active; table entry 0x9055A0+0x1C*4 -> CODE+35). Quests screen lists active bounties first (q_list 0x80+region -> fake records `b_recs`, part kind 2 = bounty kills, desc line 3 = "Time left: N min"). BDATA at 0xFE0000 (after the quest code): header (+12 rank table ptr), region table at +16, rank table, pools, texts. The Quests screen shows "Hunter: <rank> (<points>)" at x 430, top of the details window (b_ranktext, cyan). `tools/tests/emu_quest_menu.py` covers it (unicorn). |
| `640_hunt_quartermaster.py` | Hunt Quartermaster (Reeve: blin66_6 model 4 `sub_leave`; sized `HEIGHT` 1.05 x Cloud's height in each map via `fieldanim.height` (skeleton span in the first anim frame) x entry scale: hand factors were off) in mds7st3 (lower platform right), junonr1 (between item/materia shops; junin1 enters here), ropest (gondola platform), rckt + rckt2 (by Cid's house; the world map enters either). Tier menu -> page (`PAGES`: Tracker common gear, Hunter common + 2 rarity pages, Veteran, Elite, Master, Legend), tier locked below its `RANKS` points; buy = CHGLD 32-bit compare, GOLDD, STITM (inventory index: weapons 128+, armor 256+, accessories 288+; names asserted against kernel2 sections 10-13). IF ops only jump forward: back-jumps go via a local label + JMPB. |
| `660_dates.py` | Dates (plan `docs/dates_plan.md`, data `_dates_data.py`; Tifa, Aerith, Scarlet and Elena, one group (the capsule copy is now at 16 models: further girls need a second group); Elena: bare zela.hrc (thighs skin, x0.85), sits zdbe/zdle; (user, since) Scarlet's third date starts with her standing close to Cloud (`STAND_ON_THIRD`, init branch on affection; `_near`), Aerith's third date has no actions (stays seated), Aerith's head closer (KNEEL_FACE 6) and looking straight again at double speed, Elena's lap pose straighter torso / hips angled more / arms straight down / `LAP_RIGHT` to his right, Cloud's spanking hand placed on her by two-bone IK (`_cloud_seated`: wrist `HAND_UP` above her behind, asserted within 1.0), part three she faces him (yawed 180 inside the anim, thighs spread round his hips); part two over bare Cloud's lap (seated ZDBC-based ZCTL spank / ZCTM thrust+slap, `_cloud_seated`; her zdea/zdeb from `_lap`), PART2 'once' (cloudb 24+k: pose once with SOUND 0x76 at its middle), 'switch' (fade + both change pose: part three), 'sounds', 'cloud_still'; tier steps may be ('A', act) = her `GIRL_EXTRA` actions: look (TURA Cloud), stand (stand up, walk over, face him), slap (Scarlet: junone7's FDID 0-0x1D + SOUND 0x76 + 0x1D-0x31), kneel (Aerith: zdkd bow); her slots 9 stand, 10 slap, 11 kneel, 12 look; Scarlet sits with our bench/ledge poses zdbs/zdls (`BENCH`, `_ledge(bench=True)`); her own seat `GIRL_SEAT` in the gondola and capsule (left, nearer the camera: user); her 'stand' action walks her over to Cloud (`WALK_TO` 0.35 of the way from him; MOVE only when the straight line is all floor, else XYZI: the capsule's gangway isn't walkable and a blocked MOVE would never end) and turns her to him; her part two at her seat (`at_her_seat`: left of the screen, user; cloudb slot 20+n places him there); her own seat `GIRL_SEAT` in the gondola and capsule (left, nearer the camera: user); her 'stand' action walks her over to Cloud (`WALK_TO` 0.35 of the way from him; MOVE only when the straight line is all floor, else XYZI: the capsule's gangway isn't walkable and a blocked MOVE would never end) and turns her to him; her part two: skirtless zsca standing in front of Cloud facing the same way (`same_way`), zdsw/zdsx from `_wall` (leaning, arms out to a wall, right knee up, head to her left, pelvis following his ZCTE / ZCTI pelvis by pivoting on her left ankle); acts stop / go / fast and per-girl `PART2[...]['acts']` (Aerith 'look' -> zdkc); the capsule's near background tiles (ids 52-87) pushed back to 4093 (`TILES_BACK`: they drew over the characters, user); a base field lacking a girl's model gets it from `GIRL_DONOR` with a new entity; part two per girl `PART2` (undressed copy or her own model, her poses, Cloud's pose from `CLOUD_PART2` = 620 CLOUD_BED standk/stand/standf; bare Cloud slots 3 show, 4+k loop pose k, 12+k hold; her slot 4 place+first pose, 5.. loops, 8 hold; data `part2` steps ('act','stop'|'fast') between lines). Scarlet without her skirt `SCARLET_BARE` zsca.hrc (`_scarlet_bare`: AMCC with the 8 skirt parts, both tiers f/r s1/s2 each side, dropped; not used yet). Aerith's part two = "head" in her own model: zdka/zdkb (`_kneel`: sitting back on her heels `KNEEL_SIT`, face `KNEEL_FACE` before his pelvis, rocking, head upright; 15 / 8 frames), Cloud ZCTE then ZCTI (x2): her world talk asks "Just chat." / "Ask her on a date." -> "Where to?" gondola / space capsule / water tower -> `DATE_GIRL` (bank 1 217) = i+1, MAPJUMP into that place's date field for her group (`FIELDS`: blackbga = bwhlin copy (still Gold Saucer view, no FMV, user), blackbgf = rcktin7 copy (BGON 1 / BGOFF 2: stars through the round window), blackbgg = nivl_e1 copy (the promise water tower)). Date fields get a blank script (`_clear_texts` first, then `_blank`: every entity keeps only its CHAR, entity 0 = director). Tier by HB_AFFECTION (< 10 / < 20 / 20), same conversation in every place (user); questions +1 affection (cap 20), WRONG (5,246); third date with no wrong answer -> "Give into your desires." / "Leave it be." -> part two (user's test scene): fade, cloud/girl slot 3 hide, entities `cloudb` (bare Cloud zcla.hrc + ZCTH: ZCTE leaning back, arms bent in round her) and `<girl>b` (Tifa: new ztfa.hrc, her white top (ztfb/ztgb) and skirt (ztfc/ztgc: skin colour, the flared rings and the ring under the waist pulled in, `SKIRT_RINGS`) in skin colour, thighs (ztfd/ztfe -> ztgd/ztge) in her body's skin tone, hip end ring x `THIGH_TOP` 1.3; her own AAGB untouched) shown at Cloud's seat, she koala-hugging him (zdkt.a from `_koala`, built on ZCTH's frames: same XYZI, DIR + 128, his point (x,y,z) = her (-x,y,-z)), `part2` lines, closing narration. Gondola Cloud DIR 0x00 (GDAB faces backwards); tower scaled 0.85, Tifa moved/raised, Cloud facing her direction mirrored. Seats `SEATS` (gondola: the original date's XYZIs + gondola sitting anims GDAB/GDEE; capsule: floor before the benches facing each other; tower: where young Cloud/Tifa sit, our ledge poses zdlc/zdlt from `_ledge` (models face -z)). Back beside her (`_return_spot`). |
| `670_movie.py` | Movie minigame (user's design): with all 20 `HB_KID` bits a cameraman (junone2 model 6 junon_report2; FDCB idle, FFBC filming) and Ruby (jun_i2 model 6 midgal_woman, CBFE = the Honey Bee dancer's skeleton, so the dancer poses play on her) stand in mrkt2 right of the item shop (`filmman`/`ruby`; mrkt2 already has an entity `camera`); accept -> new field `whitebg1` (mds7_w3 copy, blank script): bare Cloud + bare Ruby (`_bare_ruby` ZRHA.HRC) through all 6 positions, 1 minute (1800 frames) each, between the 3 beds (mission left, cowgirl middle, dog right, edge/headrev left bed's foot, head floor; bed pieces z 54/100/125), cameraman filming beside. Entities: `keys` (IFKEYON 0x220 once a frame: presses PR/TOT, frames FR), director (entity 0: tick = WAIT 4 + ~6 turns: VEL = VEL*5/6 + P*5 - 6 + (POS-500)/50 (offset 1000, clamped +-45), POS += VEL, < 100 or > 900 = CUT, no pay), `cursor` (bucket POS/50 -> binary tree of XYZIs per position), `gauge` (sprite bar), `voice` (a Ruby line every 75 frames in a window the player can't close: WMODE 01 00 01, as bigwheel's GP window; `hush` WCLSE 01 60 frames later; head/headrev muffled), speed step from RATE = RATE*3/4 + P*16 (thresholds 30/60/95) -> anims ZM/ZN<pos><step> (15-frame poses resampled to 20/15/11/8). Gauge/cursor = sprite models (`_marker_models.mesh(half=)`, own 64x64 textures QGAD/QCUD), placed per position by un-projecting a screen spot (GAUGE_Y -80 = near the top of the view centred on the hidden player; +88 was off the bottom in-game, clamped to the scroll range) at 0.8 x the nearest floor depth; DIR so the quad's x projects horizontal. Music AKAO 10 index 35 COSTA (user; Turks' Theme = RHYTHM 45). Wrap -> `MOVIE_STATE` 2 (bank 1 218), presses (2,219), minute (2,221); mrkt2 main says "come back in half an hour" -> 1; talk after 30 play minutes pays presses x 10 (GOLDU). Placement checked on offline renders only (scratch scene renderer). |
| `650_world_vehicles.py` | World map variant 0 (progress < 1000) model table + highwind/sbmrn/tail (Highwind was invisible: row 0x96DF10 had 0xFF for models 3/13; then still invisible with only its shadow because every model 3 object gets the static child 0xE39AE0 = model 9 'tail' (0x7619D2) and the draw pass 0x76328F skips an object whose child's model isn't loaded; row 0 now maps 9 too); submarine slot 4 parked by Junon at new game (`_config.SUBMARINE_SLOT`). |
| `900_phs.py` | Clears the PHS bit wherever a field writes the menu lock mask. |
| `debug/990_debug.py` | Only with `build --debug`. Entity `dbgmenu` (no model) appended to every field with text room (<= 250 texts, < 48 entities; 663 fields, not elmpb / most disc 2 Midgar): main loop holds BTLON 01 while DEBUG_FLAGS (1,213) bit 0 is set; `ARRIVE_AT` hand arrivals (games: gldgate's drop; Nibelheim = nivl_3). L1+R1 held (IFKEY 0x04 then 0x08; IFKEY's jump is 1 byte, so it hops via a goto) opens travel pages (arrival = a gateway into the field, else a script MAPJUMP to it, from `docs/inventory/field_links.csv`), gil +100,000, encounters off/on, Honey Bee/Hunter shortcuts. World map: call 0x76760B -> stub returning -1 (no battle) while the bit is set. A normal build is byte-identical without it. |
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
  World-map scenes are in wm0.ev map-cell functions (e.g. the Zolom: cell 0xAA23
  -> field `sichi`; buggy breakdown: cell 0xADA0); wm bit 0xE78+n = (3,207,n).
  `docs/inventory/worldmap.md` "Called from" is off by one (enter_field N = entry N-1).
- openFF7's own save vars: bank 3 offsets 96-105 (nibble 11): `FLAGS` = (11,96)
  bits: 1 Guard Scorpion, 2 Air Buster, 3 in No.5 Reactor; `RECRUITED` = (11,97)
  bit per character id; `RECRUIT_COUNT` (11,98); boss "fought this visit" bits
  (11,99-101). **Bank 4 224-255 is NOT free**: 184-231 is the exe's world map
  object slot table (0x76609E writes, 0x76616A reads; slot 5 = 224-231), 232-243
  zeroed on world map entry. Quest bytes: `_config.QUEST_AREAS` (bank 3 192-255,
  160-183, bank 5 181-223, bank 2 27-63; all checked free in field/world map
  scripts and exe absolute refs, zero at new game); `600_quests._allocate` hands
  them out in GIVERS order (state byte + one counter per kill target), so append
  new quests at the end of a giver or new givers at the end (or mark them
  late=True). 15 quest bytes left (bank 1 136-159 / 236-255 added: unused by every script, no exe absolute refs). Quest data block 20691 of 32768 bytes. Bank 3 128-159 is used by
  original scripts (not free).
  Temp var (5,232) used by quest giver talk (CKITM count); markers use no temp vars. Temp vars (5,240),(5,241) for menus.

## Verified facts: field scripts

- Var nibbles: 1/2 = bank 1, 3/4 = bank 2, 11/12 = bank 3, 13/14 = bank 4,
  7/15 = bank 5, 5/6 = temp. 16-bit nibbles: 2,4,6,12,14,15. 16-bit vars use
  **byte** addressing (var[2][28] = savemap 0x0BC0). Bank 1 starts at savemap 0x0BA4;
  field vars can't reach past 0x10A4 (so not the config block / battle speed).
- **The engine runs each entity for at most 8 opcodes per turn** (0x60CD77,
  `[ebp-0x1c] = 8`), then moves to the next entity: scripts interleave mid
  computation. Never share a temp var between entities' *concurrent* scripts
  (mains/loops): quest markers kept their mode in one temp var and the star /
  heart scripts overwrote it between computing and testing (stars vanished;
  two givers' markers fought). Branch directly instead.
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
- **The player's facing on arrival = the MAPJUMP's direction byte**, even over a DIR in the player entity's init (dates: Cloud set DIR 0x80 in init, the jump said 0, he faced 0: user saw him the wrong way). Give the jump the facing you want (inferred from the user's report; fix awaiting confirmation).
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
- **Music:** MUSIC n plays the field's music block entry n (id); the exe
  plays name-table index id-1 (0x9684C8). Checks: del2 plays id 36 = COSTA (35), onna_4 id 68 = BEE (67),
  bwhlin id 50 = DATE (49). Turks' Theme = RHYTHM (45): gonjun2 and utapb switch to it
  when the Turks appear. The MUSIC handler (0x613AC8) skips
  field 116 = md1stin and anything while MULCK is set; `AKAO 10 <index>`
  (F2 00 00 00 10 idx + 8 zero bytes) plays a track without those checks
  (250 md1stin, 180 roadend; untested in-game). Sound dispatcher 0x740D80.
  7th Heaven basement (mds7pb_2) scenes: (3,214) bits 6 (wake-up on entry)
  and 0-2 (border2 line talk), set at new game.
- **World map models / object slots:** see `650_world_vehicles.py` (model set
  per progress variant; 6 save slots at bank 4 184-231 by model, Highwind and
  buggy share slot 3).
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
  model count in every field: append models and CHAR entities together. The
  build refuses a changed field whose CHAR indices aren't exactly 0..models-1
  (`_check_chars`); a shared model crashed md8brdg.
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
- **Play time** = savemap 0x0B80 (0xDC08B8) u32 seconds, incremented at
  0x40ABF0 (frame accumulator 0xDC08C0 += 0x444). Field scripts can't reach
  it (bank 1 starts at 0x0BA4); q_clock copies minutes to var[2][247].
- Numbers in dialogue: `MPRA2 [src bank][window][slot][u16 var]` after the
  WINDOW op, text `{VAR}` (FE E1, no operand) shows it. GOLDU/GOLDD
  `[bank<<4][u32]`: bank 6 + offset = add/remove a temp word var of gil.
- **No waiting animation op in an init**: ANIME1 (0xA3) and ANIM!1 (0xAF) yield
  until the animation ends (handlers 0x61484A / 0x6149A5); ANIME1 of a 60-frame
  loop in girl2's init left Tifa's/Velvet's devoted room on a black screen
  (user). ANIME2 (0xAE, same handler) doesn't wait: 620's `_loop(i, wait=False)`.
  (ANIM!1 of a lounge sitter's pose in an init does work.)
- Text: `{NEW}` (0xE8) is a new page *and* line; `encode` swallows a "\n"
  right after it (decode writes "{NEW}\n").
- Model loader animation lists: `ModelLoader.anims` / `with_anims` (append
  same-skeleton anims; e.g. onna_52's dancer has 22). Honey Bee dancer
  (BADD.HRC) anims: stand BAJB/DXID, walk BCCC/DXHF, run BCCD/DXIA, dances
  DXHE DXIB DXIF DXJA DXJB BAJF BBAA BAJD BAJC, DXJC/DXJD (receptionist), BYAD,
  AVJE, DXIC, DZBA (1-frame pose), DIEF, DXIE/BAJE. Cloud in onna_52: AQAA
  frames 0-1D sit on the bed / 1D-2C stand up.
- **Texture palette alpha 0xFE** = PSX semi-transparency: the star sprite
  (s_guard) had it on every colour and showed for a moment, then vanished;
  marker palettes are forced to 0xFF. The "crash on every quest-giver screen"
  was most likely char.lgp not copied (user), not the files.
- **Field model files:** new files now copy known-good
  layouts exactly: `.p` = the donor's structure (4 vertices, 5 edges; only
  positions/UVs/extra reversed triangles changed), `.tex` = a field texture's
  0xEC-byte header (aabb.tex: 4-bit, 16 colours, colour key) with our size,
  `.hrc` TOC check byte 11 (all original .hrc; other files 14).
  `_config.QUEST_MARKERS = "orbs"` falls back to the old tinted orb.
- **Key items**: bits at bank 1 offset 64 + id//8 (savemap 0x0BE4, 64 bits);
  the Key Items menu builds its list over all 64 bits (exe 0x714FC1 `cmp 0x40`),
  names = kernel2 section 15, descriptions section 7. Ids 51-63 are blank and
  unused by any script: 51-62 are openFF7's gifts (63 free). kernel2 text pool
  now 27,490 of 27,648 bytes (158 left).
- **Bank 1 188-223**: no exe absolute refs, no world map use; original field
  scripts use 197-199 and 208-209. 188-196/200-207/210-212 = HB_AFFECTION;
  213 = debug flags (debug builds only); 214-216 = HB_KID (622); 217 = DATE_GIRL (660); 218 = MOVIE_STATE, 219-220 MOVIE_PRESSES, 221-222 MOVIE_AT (670); 223 still free.
- **Background tile depth**: tile +24 u16 id = draw depth (smaller = nearer; layer 1 4095), +38 u32 = the PC's finer depth (larger = further). (Tried moving onna_52's bed tiles back so girls on the bed draw over it: then the bed covered nobody, including people behind it; reverted at the user's request.) Tile id = view z / 4 (GTE SZ/4: onna_52's bed parts 140-175 where the bed is 560-700 deep); +38 = 1e7 - K/(id + d), K ~1.19e8, d ~-4.7 (fitted per room): a z-buffer-style value, so the PC most likely depth-tests per pixel. 620 `_bed_depth` gives each bed tile the depth of what it shows (ray-cast on the walkmesh bed box + headboard plane; every tile showing the bed box at the mattress's far-edge depth + 8, headboard tiles their own depth + 16). User: with true mattress depths a tile row still covered the mission girl's lower half, so a character seems to be sorted by one depth (its position), not per pixel.
- **FMV with field models (research, not yet used):** gondola date = bwhlin (gold7 PMVIE 0x30,
  dialogue, gold7_2 0x31; normal ride gold2-6 via bwhlin2), escape pod = rcktin7. Movies with a
  .cam in data/cd/moviecam.lgp drive the field camera while MOVIE runs, so models placed with XYZI
  are drawn over the movie; helpers time things with MVIEF 06 xx frame polls. Movie name table
  exe 0x7BAE80 (105 pointers, disc 1). Free maplist names for new fields: see docs/dates_plan.md.
- New field models can be added to char.lgp (`ctx.char_file(name, data)`;
  .hrc/.rsd text, .p, .tex). magic.lgp has directory entries `ff7.lgp`
  can't parse: `_marker_models.magic_file` scans its TOC by hand.

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
  (32 KB max; 15.5 KB with 66 quests), quest code at 0xFDD000, then the
  confirm table. Submenu API used by quest_menu.asm (text colours:
  0 grey, 4 green, 5 cyan, 6 yellow, 7 white; smaller z = in front).
- exe patching: `ff7/exepatch.py` (expected-bytes checks + PE checksum, which
  reproduces the original's). `ff7tool.py exe-test` makes a harmless test exe;
  **Confirmed by the user: a modified exe (.data and .text changes, checksum
  fixed) runs fine through Steam.** So exe patching is a viable route.
- **Field opcode handlers** (table 0x9055A0): cdecl, no args; read operands
  at [0xCBF5E8] (script base) + word [0xCC0CF8 + entity*2] (entity = byte
  0xCC0964) or through the getter 0x60F750(nibble sel, operand offset); write
  vars with 0x60FA7D(nibble sel, operand offset, value) (sel 1 = high nibble
  of byte 1); advance the position themselves; return 0 to continue.
  Unused opcodes (0C 0D 1A-1F 44 46 4C 4E BE) share 0x6107E1 (`return 1`):
  0x1C is openFF7's BOUNTY (630). Our script tools need the length in
  `ff7/opcodes.py`.
- Field opcode handlers: PC 0x61BCD7 (compares char with the field party copy
  0xDC09E5; leader -> field header+0x2A = player model index), GETPC 0x61F238
  (reads real party 0xDC0230), PRTYP 0x61BE95, IFKEY 0x61220D, MSPED 0x618369.
- Input: global button mask 0x9A85D4 (read by 0x7186B9); each frame 0x75EF46
  copies it into the field header +0x68 (held) / +0x70 (newly pressed) and
  +0x78/+0x80. IFKEY tests header +0x68. **IFKEYON (0x61225D) reads +0x80 when its mask has
  bit 0x200, else +0x70; IFKEYOFF likewise.** Every original OK check is `keys=544` (0x220 = OK
  0x20 + that selector); 0x20 alone never fired in the movie minigame (user). Use 0x220.
- Player-controlled movement code: not found yet (doesn't read model+0x76
  directly; no field code reads the global input mask).

## Verified facts: characters / recruits

- Character records (9 x 0x84 at savemap 0x54) are found by their id byte
  (+0); menu/field map id -> record via exe table 0x919928 (`0..8,6,7`: id 9
  Young Cloud and 10 Sephiroth share records 6/7). New game: record 6 = id 9,
  record 7 = id 10. **Cait Sith / Vincent only get their record from the name
  entry** (MENU 00 06 6/7, exe 0x718ADA copies the exe template 0x921EF8 +
  id*0x84 over it). 230 instead copies those templates into KERNEL section 3
  records 6/7 (Young Cloud / Sephiroth are never used), so no naming screen.
- PRTYP (0x61BE95): no-op if already in the party, else first empty slot, else
  overwrites slot 2; also sets the PHS-available bit. A field-opened PHS
  (MENU 00 07 00) needs exactly 3 in the party to leave: never use it in joins.
- Yuffie encounters: exe 0x767641, gated only by (3,133) bit 0; formation by
  Cloud's level (< 20 = 268, Mystery Ninja level 17). Join = yougan2 YUFI
  script 9. Wutai theft trigger (wm0) needs 0xE7E (3,207,6) clear; set at new game.
- Vincent: sinin2_1 safe (needs progress > 385; Lost Number 576) -> basement
  key (1,232,1); sininb2 coffin talk sets (1,231,7); join LINE in sininb1
  sets (13,80,2).
- New-character research (Sephiroth/Turks): `docs/research_new_characters.md`.

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
  Its walkmesh runs past the background on the right (user: "you can run out of
  bounds"; floor to screen x ~300, view ends ~160): things placed there are
  invisible. Keep NPCs/lines at screen |x| <= ~150 (projected with ff7.camera).
- nmkin_5 (No.1 Reactor core): bomb scene fires when entity `cl` is on
  triangle var[6][7] (init sets 2); we set 255. Shared with the No.5 visit (progress 120).
- elm (Kalm): arrival line checks (3,128,1) only — no progress check.
- **Text ids are 8-bit** (MESSAGE/ASK): fields with ~254 texts (all disc 2 Midgar
  fields share one big table) can't take new dialogue; put NPCs next door.
- Disc 2 Midgar tunnels (tunnel_4/5/6) are one looping maze positioned by the
  counter var[15][129] (sbwy4_22 sets 4 on entry); bank 5 offset 131 bits 4-6
  are transient 'arrived by ladder' markers, don't set them.
- Check init IDLCKs before placing a line or NPC: locked triangles are in the
  walkmesh but can't be walked on (sbwy4_1 locks tris 2 and 5; a line there was unreachable).
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

All recruits (230) and the buggy purchase (430) built, untested in-game.

Quests (600): first 3 givers user-confirmed working (orbs, menu, kill counting);
the 12 from the user's list tested (fixes applied: positions, Andrea standing,
8 visible rows). Untested: cargo ship giver, 21 world givers (Kalm to Gaea's
Cliff), 10 boss lines (Jenova BIRTH always on; Bottomswell, Dyne, Reno+Rude,
Materia Keeper, Palmer, Rapps, Red Dragon, Demons Gate, Jenova LIFE once their
quest is accepted; once per visit), Sources in every reward. Boss lines:
`boss=dict(field, line|at, formation[, always])` on a kill quest; `at` uses
`_travel.line_across` (narrowest crossing of the floor at that point).

Not done: world map leader models + new models (needs .exe work), player
leader-aware interactions (ladders etc.),
battle speed default (needs .exe patch), remaining bosses as world NPCs + rare
encounters, vehicles (Tiny Bronco, submarine), world-map
models for other leaders, minigame NPCs, shop scaling, crater bosses.

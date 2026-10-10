# Battle: Tame / Call (research notes)

Static reading of `ff7_en.exe`, KERNEL.BIN, kernel2.bin, scene.bin and
battle.lgp by a research agent; nothing tested in game. "Inferred" marks
claims not verified in code/data.

## KERNEL / kernel2
- Section memory: commands 0xDB9590 (32 x 8), attacks 0xDB9690 (128 x 28),
  growth 0x99CE10, init 0xDBFD8C, items 0xDBD160, weapons 0xDBE730, armor
  0xDBCCE0, accessories 0xDBCAE0, materia 0xDBDF60 (96 x 20).
- **Text shown in game comes from kernel2.bin** (LZSS; 18 x [u32 len + data],
  = KERNEL sections 9..26: 0 cmd desc, 1 magic desc, 2 item desc, 3 weapon,
  4 armor, 5 accessory, 6 materia desc, 7 key item desc, 8 cmd names, 9 magic
  names, 10 item names, 11 weapon, 12 armor, 13 accessory, 14 materia names,
  15 key item names, 16 battle text, 17 summon names). Text pool 0x9A13C8,
  0x6C00 bytes, ~736 bytes free, no bounds check.
- Command record (8 bytes): menu type (0 target directly, 1 Magic, ... 0x0B
  Coin), target flags, FFFF, u16 single/multi camera. Manipulate =
  `00 1F FF FF C2 00 C3 00`. Free command ids 0x1C-0x1F (max 0x1F).
- Materia record (20 bytes): AP thresholds u16[4] (x100), equip effect,
  status, element, type (+0xD, low nibble -> handler, switch 0x5CD141 / table
  0x5CD244: 2 replace Attack, 3 replace command, 6 add command 0x5CEBE5,
  7 E.Skill, 8 Master Command, 9 magic, A Master Magic, B summon; D-F unused),
  attributes[6] (+0xE). Command materia: `attr[level-1]` -> add_command
  (0x5CECE9, temp list 0xC06920; final in battle record 0xDBA498+slot*0x440
  +0x4C). One materia = one command; two needs a stub at 0x5CEC60 (if cmd
  0x1C also add 0x1D) or a new type nibble.
- Free materia ids: 22, 38, 45-47, 63, 66-67, 91-95. 38 (0x26) is already a
  type-0x16 command materia: best template.

## Command dispatch
- Action context 0x99E308 ([0x99CE0C]): +0x00 attacker, +0x0C command, +0x10
  sub-index, +0x2C attack id, +0x40 damage formula, +0x80 status, +0xE4 fail
  message, +0x208 target.
- Setup ~0x4361A0-0x436A39: `seq = 0x9AE9C8[cmd]`, routines from byte table
  0x7B75A8 (0x6D bytes; refs 0x43656C, 0x436B6C, bound 0x436B41) via routine
  table 0x8FEE48 (31 entries; calls 0x43658D, 0x4365AD); 0x1F terminates.
  Attack [14,9]; Magic [0,12,9]; Steal [30,9]; Sense [10,22,9]; Morph
  [14,28,9]; Manip [26,9]; enemy attack [7,12,9]; 0x1C-0x1F none.
  Routine 9 = 0x5D9940 execute/damage.
- Manipulate roll 0x5DE0D0 (formula-9 pre-routine): ~ level + 50 - target
  level; on success writes target to 0x9A8DBE + slot*0x34, message 0x5A.
  Manipulated mask 0x9AAD22. Enemy menu lists built at 0x9AC114 + slot*0x60
  from enemy record +0x94 (around 0x5D0A48).
- Morph 0x5CAC5C-0x5CAD6B: item from record +0xA0, message 0x56, sets bit
  0x10 at 0x9A8B39+target*0x44 (suppresses drop).
- Battle menu confirm 0x6D956D: switch on [0xDC3C74], cases 0-0x0B, table
  0x6D97F7 (a Call list needs a new case). Blank battle-text slots 12-15, 65-79.

## scene.bin (`data/lang-en/battle/scene.bin`)
- 256 scenes x 0x1E80; formation = scene*4+slot. 0x000 enemy ids (3 u16),
  0x008 setups, 0x058 cameras, 0x118 formations, 0x298 enemy records
  (3 x 184), 0x4C0 attacks (32 x 28), 0x840 attack ids, 0x880 attack names,
  0xC80 formation AI, 0xE80 enemy AI.
- In memory: ids 0x9A8748, setup 0x9A8750, formation 0x9A8794, records
  0x9A8E9C + type*0xB8, attacks 0x9A90C4, attack ids 0x9A9444, names 0x9A9484.
- Enemy record (184): 0x00 name, 0x20 level, 0x21-0x27 speed/luck/evade/str/
  def/mag/mdef, 0x38 anim index per attack x16, 0x48 attack ids x16, 0x88/0x8C
  drop rates/items, **0x94 manipulate attack ids x3**, 0x9C MP, 0x9E AP, 0xA0
  morph item, 0xA4 HP u32, 0xA8 EXP, 0xAC gil, 0xB0 status immunity (inverted;
  bit 22 Manipulate, bit 0 Death).
- 352 distinct enemy ids (335 named). 176 have a manipulate list, 140 of those
  not immune. No boss flag (132 named enemies Death-immune; curate a list).

## Models / mid-battle swap
- Battle models by PSX name -> battle.lgp prefix (0x5E2460, table 0x8FF2F0):
  ENEMYnnn -> id nnn; party CLOUD rt, TIFA ru, EARITH rv, RED13 rw, YUFI rx,
  KETCY ry, CID1 rz, BARRETT sb.., VINSENT sf.., GALL sj, DEATHGIG sk,
  HELLMASK sl, CHAOS sm.
- Vincent's swap: anim-script ops 0xAC (form index -> 0x9ADED8) and 0xA2
  (`0x42A330(0, isBeast, actor, 0x7C1098[form])`: frees 0xBFB2B8[actor], loads
  new model 0x5E1AD2; resets actor state 0xBE1190+actor*0x1AEC). Swapping a
  party actor to an enemy model works mechanically this way.
- Hard parts: routine 12 (0x5C9898) only uses enemy animation indices for
  actors >= 4 (party gets 0x34); the creature's record and attacks belong to
  another scene and must be loaded into spare slots; scale/position differ.

## Victory / rewards (0x431481-0x43165E)
- Enemy actor k+4 counts as defeated if status u32 at 0x9AB0DC+actor*0x68 has
  0x4001 (Death/Petrify) and its bit is clear in 0x9AAD24 (removed/escaped
  mask, set by the Remove effect). EXP/gil/AP accumulate; drop rolled unless
  0x9A8B39+actor*0x44 has 0x11. => **Tame should kill via the normal Death
  path** (not Remove) to give EXP/AP/gil/drop.

## Save space
- Bank 4 offsets 232-255 are written by the world map (zeroed on entry at
  0x766C7A / 0x766E19, object data written at 0x766FD9); only 224-231 safe.
- Bank 3 offsets 192-255 (savemap 0x0E64-0x0EA3, nibble 11): unused by field
  and world map scripts, no absolute exe reference -> tamed bits (352 bits).

## Recommended approach
- Tame (moderate): command 0x1C (copy Manipulate's record; text in kernel2
  sections 0/8/16), relocated sequence [T, 9] with a new routine T modelled
  on 0x5DE0D0 (chance from HP%, /4 for bosses; on success set tamed bit and
  force a kill; on failure a new message), materia 38 + stub at 0x5CEC60
  adding 0x1D (Call).
- Call (large): new battle menu case listing tamed ids; load the creature's
  scene record into a free slot; swap model via 0x42A330 + the 0xA2 reset;
  commands from +0x94 (+ fallback for enemies without a list) plus Dismiss;
  hook routine 12 for animation indices; restore character on KO/Dismiss.
- Risk: code space (.text has ~459 bytes free; expect a new PE section, to be
  tested with Steam first).

# Adding new playable characters (Sephiroth, Rufus, Rude, Reno, Elena, Palmer)

Static research only (game files + ff7_en.exe disassembly); nothing tested
in-game. V = verified in data/exe, I = inferred.

## Records and ids
- 9 character records (0x84 bytes) at savemap 0x54 (memory 0xDBFD8C); byte +0
  is the char id. Battle init (0x5CF712) and write-back (0x5C6C5C) scan the 9
  records for the id byte, so any record can hold any id. (V)
- Menu/field map id -> record via 0x919928 (11 dwords `0,1,2,3,4,5,6,7,8,6,7`,
  116 code refs). 0x919954-0x91995F are 3 unreferenced zero dwords: ids
  11-13 could be pointed at any record there; 14+ hits other data. (V)
- New-game data (KERNEL section 3): record 6 = id 9 (Young Cloud), record 7 =
  id 10 (Sephiroth, level 50). Name entry (MENU 00 06 c, init 0x71894B)
  copies the exe template 0x921EF8 + id*0x84 over record 6/7 for Cait Sith /
  Vincent (0x718ADA). Default names 0x921CB8 (12 bytes each). (V)
- Item 0x67 used from the Item menu (0x716658) rewrites record 6/7 id bytes
  to 6/7 (debug leftover?). (V)
- Limits / level-up gated to ids < 9: 0x5CFA56, 0x5C8684, 0x5C70EA/0x5C7187,
  0x5C735E, 0x5C6EAE. **Growth pointer 0x5C76DF (0x99CE10 + id*0x38) is not
  bounds-checked**: id 10 levelling up reads garbage. (V)
- The savemap can't grow (0x10F4 bytes, 1633 absolute refs). More than 9
  characters at once needs a "bench" system in exe code. (V/I)

## Battle
- Model choice 0x5BE20B: party char id at 0x9A87F4 + slot*16; model index =
  id (Barret/Vincent weapon variants 11-15, HICLOUD 16). Names 0x7C27B8 (17):
  ... 9 CLOUD.DAT, 10 SEFIROS, ... New ids need a hook at 0x5BE382. (V)
- battle.lgp prefixes: table 0x8FF2F0 (23 x 24 bytes, count at 0x5E292D);
  SEFIROS = `sa`, enemies n = (n/26, n%26). (V)
- Party model: `aa` header (field 0 = 2 party / 0 enemy), `ab` 74 script slots
  (enemy: 32), `ck`-`cz` 16 weapons, `da` animations (body + weapon).
  Kalm Sephiroth (`sa`) is a complete party model. (V)
- Turks/Rufus/Palmer are enemy-format (no weapons, 32-slot `ab`):
  Reno 48 `bw`, Rude 128 `ey`, Rufus 68 `cq`, Palmer 164 `gi`, Elena 296 `lk`.
  Converting needs new `aa`/`da`/74-slot `ab` (Cloud's scripts remapped) and
  dummy weapons; no victory/limit/run animations. (V data, I conversion)
- Character AI: KERNEL section 2 at 0x61C, 12 u16 slots by id (lookup
  0x5C88C7); Sephiroth (10) has a main script, likely auto-acting: clear it. (V/I)
- Table 0x8FEE38 (12 bytes by id, written 0x5C8B65): ids >= 12 overwrite
  function pointers at 0x8FEE48. (V)
- Limits: names kernel2 sec 9 entries 128-199; effects = exe code (handlers
  0x8FE4B0) + skeleton-specific LIMxx animations. Very hard. (V)

## KERNEL, menu, field
- Growth: section 2, 9 x 0x38 (curves, join flag, limits, thresholds). (V)
- Equip masks u16 by id: Masamune = bit 10; accessories 0x1FF (ids 9/10
  can't equip them). (V)
- Portraits: menu_us.lgp has 12 incl. `pcefi` (Sephiroth); exe table
  0x919C18 (12 by id). PHS roster ids 0-8 only (`cmp 9` at 0x700B97). (V)
- Field: PC/CHAR take any id; MMBUD/MMBLK masks are u16 (ids 0-15). Field
  opcodes 0xCA PRTYE, 0xCB IFPRTYQ, 0xCC IFMEMBQ, 0xCD MMBUD, 0xCE MMBLK,
  0xCF MMBUK. Field models: sub_n_sefiro, sub_lufas, shinra_lude,
  shinra_reno, shinra_irena, sub_palmer. (V)
- World map player model chooser 0x76736E (Cloud 0, Tifa 1, Cid 2). (V)

## Plan
1. Sephiroth as id 10 in record 7 (data only: re-level record 7, clear AI
   entry 10, equip masks, recruit NPC with MMBUD/PRTYP 10). Can't coexist
   with Vincent unless moved to another record via table entry 10.
2. Exe: growth hook at 0x5C76D2/0x5C76DF for ids >= 9; PHS bound 9 -> 11.
3. Converter for one Turk (Rude), tested by replacing an original's files.
4. Decide which originals to drop, or build a bench system.
5. Limits last, or never.

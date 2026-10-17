# Main menu: adding "Bestiary" (research notes)

Static reading of `ff7_en.exe` (capstone) by a research agent; nothing tested
in game. VAs; file offset = VA - 0x400C00 (.text), VA - 0x401600 (.data).

## Menu framework
- Current menu id `[0xDC12EC]`, previous `[0xDC12E8]`; setter `0x6C6AEE(id)`.
- Init table `0x91AB40`, update table `0x91AB98` (22 entries each, id 21 NULL).
  Ids: 0 main 0x6CA165/0x6CA346, 1 Item, 2 Magic, 3 Materia, 4 Equip,
  5 Status 0x703760/0x703ABD, **6 = dead code** (0x703610/0x703676: title box,
  two windows, one string, cursor, Cancel exits; free id + template),
  7 Limit, 8 Config 0x6C1F60/0x6C2025, 9 PHS, 10 Save, 11, 12.
- Driver `0x6CB56A` calls `upd[id](frame)`.

## Main menu update `0x6CA346`
- Masks (0x6CA38C..0x6CA42F, 0xA3 bytes): copies savemap visibility mask
  `0xDC08F8` -> `[0xDC111C]` (forces Quit 0x0400 visible) and lock mask
  `0xDC08FA` -> `[0xDC1130]`; if `[0xDC0B4B]&1` also locks 0x41.
- Cursor struct `0xDC1150` (0x38 bytes; row at `[0xDC1154]`); init pushes
  `0xB` (view rows, max rows) at 0x6CA174 and 0x6CA17C.
- Confirm at 0x6CA4A9: `cmp [ebp-0x488],0xA` at 0x6CA4F9, `jmp [edx*4+0x6CB53E]`
  (11 entries, no slack). Rows 1-4,6 -> char select 0x6CA513; 5 (Order) swap
  0x6CA526; 0,7,8,9 -> submenu 0x6CA52F (PHS sound via `sub eax,8` at
  0x6CA534); 10 Quit 0x6CA584.
- Row -> menu id byte table `0x91AAF8` (file 0x5194F8): `01..0B 00`.
- Hand cursor `0x6EB3B8(x=0x1C6, y=row*0x1A+0x12, z)`.

## Main draw `0x6C98A6`
- State switch on `[0xDC1294]`. Idle: height `[0xDC1280]=0x138`; loop
  `cmp eax,0xB` at 0x6C9AC6; text `0x6F5B03(0x1FC, 13+row*0x1A,
  0x91A8C0+row*20, colour locked?0:7, 0.001f)`; window `0x6E7BA1(&rect, 0x1DC,
  y, 0xA4, h)` + `0x6E7D20(&rect, z)`.
- Animations: open h = 0x33 + cnt*0x11E/16 (0x6C9987); return 0x105 (0x6C9C51);
  initial 0x138 at 0x6CB5DE (low-res `and dl,0x64` at 0x6CB5DB).
- Title/label index `[0xDC1208]` = id-1 set by `0x6C9812(state,id)`; cursor
  return assumes row == id-1.
- A 12th row fits: 13+12*26+13 = 0x152 < time/gil box at 0x15C.
- Low-res path (`[0xDC130C]==1`) 0x6C9D07: `cmp 0xB` 0x6C9F27, h 0x9C at
  0x6C9EE5, 0x82 at 0x6CA0B2.

## Plan for Bestiary between Status and Order (menu id 6)
Rows: Item 0, Magic 1, Materia 2, Equip 3, Status 4, Bestiary 5, Order 6,
Limit 7, Config 8, PHS 9, Save 10, Quit 11. Keep savemap masks in original bit
order; remap to row order where copied.
1. Rewrite 0x6CA38C..0x6CA42F: same mask logic, then
   `row = (m&0x1F) | ((m&0x7E0)<<1) | ((m&0x800)>>6)`; Bestiary visible.
2. Item menu reads Save lock: 0x7150EB `and ecx,0x200` -> 0x400 (file 0x3144EB).
3. Labels 0x91A8C0 in row order (Quit moves over "Beginner", slot 11).
4. Byte table 0x91AAF8: `01 02 03 04 05 06 06 07 08 09 0A 0B`.
5. Row counts: 0x6CA174, 0x6CA17C `push 0xB` -> 0xC; 0x6C9AC6 (and 0x6C9F27) -> 0xC.
6. Dispatch: 0x6CA4F9 imm 0x0A -> 0x0B; new 12-entry jump table in a cave
   (`52F,513,513,513,513,52F,526,513,52F,52F,52F,584`, all 0x6CA5xx), patch
   disp32 at 0x6CA50F; 0x6CA534 `sub eax,8` -> 9.
7. Heights: 0x6C9A84 0x138->0x152; 0x6CB5DE 0x138->0x152 (+0x6CB5DB 0x64->0x57);
   0x6C9C51 0x105->0x11F; 0x6C9987 0x11E->0x11F; low-res 0x9C->0xA9, 0x82->0x8F.
8. Rewrite 0x6C9816..0x6C983C (label/cursor return via a ROWOF table).
9. Point id-6 handlers (0x91AB58 init, 0x91ABB0 update) at the Bestiary code.

## Sub-menu API
- init(0); update(frame) each frame (immediate-mode drawing). Title box:
  `push [0xDC1210]; call 0x6C98A6`. Input only if `0x6C9808()==0`.
- Text `0x6F5B03(x, y, ff7str, colour, float z)`; width `0x6F54A2`; numbers
  `0x6F9739(x,y,value,digits,colour,z)`; char `0x6F5C0C`.
- Window `0x6E7BA1(short rect[4]*, x,y,w,h)` + `0x6E7D20(rect*, z)`.
- Cursor `0x6F4D30(...)` setup, `0x6F4DB2(struct*)` move, hand `0x6EB3B8`.
- Buttons: `0x41AB74(mask)` newly pressed; 0x20 OK, 0x40 Cancel, 0x1000 Up
  (L1/R1/other directions assumed PSX layout, unverified).
- Sound `0x74580A(id)`: 1 OK, 3 buzz, 4 cancel. Exit: sound 4,
  `0x6C9812(5,0)`, `0x6C6AEE(0)`.

## Enemy names
scene.bin (`data/lang-en/battle/scene.bin`): 352 unique enemy ids, names
<= 19 chars (~3.9 KB). Build a name table at build time and embed it.

## Free space
- .text: no long 0xCC runs; raw tail 0x7B5635-0x7B5800 (0x1CB bytes); dead id-6
  code 0x703610-0x70375D (0x14E bytes).
- New PE section feasible on paper: header room for 9 more section headers;
  SizeOfImage 0xBD5000 -> new VA 0xFD5000; Authenticode blob at file
  0x61DCB8 (0x20A8 bytes) must move or be dropped (already invalid after any
  edit). **Untested whether SteamStub accepts a new section** — test first.

Unknown: menu id 12's purpose, colour palette, z ordering, L1/R1 bits, text
budget per frame.

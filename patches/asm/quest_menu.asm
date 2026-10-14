; openFF7 quests: the "Quests" main-menu screen (menu id 11, an empty stub in
; the original) and the battle kill counter.
; Assembled with: nasm -f bin quest_menu.asm -o quest_menu.bin
; 600_quests.py places the binary at CODE and the data block at DATA (both
; asserted there). Entry points (5-byte jmp stubs): CODE+0 menu init(int),
; CODE+5 menu update(frame), CODE+10 kill hook (jumped to from 0x431536), CODE+15 motorbike
; destroyed (bike minigame, from 0x6566B9), CODE+20 / CODE+25 balloon popped
; (snowboard minigame, from 0x737D45 / 0x73C52A), CODE+30 play clock tick
; (from 0x40ABF0: keeps the play time in minutes in field var bank 1 247-248,
; for the Honey Bee Inn income, 620_honey_bee.py), CODE+35 field opcode 0x1C
; BOUNTY (630_bounties.py points the opcode table at it), CODE+40 field opcode 0x1D TXPOKE
; `1D [text id][u16 offset][byte]`: writes the byte into that text of the loaded field
; (FIELD_TEXTS: u16 count, u16 offsets, as MESSAGE/ASK read it, 0x6316E6), so a menu can
; change a character before it opens (620_honey_bee.py: the "*" of a girl whose devoted scene
; was seen). The bike and balloon hooks
; count made-up enemy ids (BIKE_ID, BALLOON_ID) through the same kill table,
; so those quests are ordinary kill quests in 600_quests.py.
;
; DATA (built by 600_quests.py):
;   +0  u32 quest count   +4 ptr "No quests" text   +8 ptr "ready" text
;   +12 ptr kill table: {u16 enemy id, u16 state var, u16 counter var,
;       u8 count, pad} ..., u16 0xFFFF
;   +16 quest records, REC bytes each:
;       +0 u16 state var  +2 u8 part count (1..4)  +3 pad
;       +4 name  +8 giver line  +12 where line  +16/+20/+24 description
;       +28 parts[4], 8 bytes each: +0 label ptr, +4 u16 source (kill:
;           counter var; deliver: item id), +6 u8 count,
;           +7 u8 kind (0 kill, 1 deliver)
;   Texts are FF7 text, 0xFF-terminated. A "var" is a byte index from the
;   start of the field variables (savemap bank 1, 0xDC08DC): (bank-1)*256+offset.
;
; Bounties (630_bounties.py): one active bounty per region, kept only in this
; section's memory (never saved; cleared when the play clock jumps, i.e. a
; game was loaded or started). BDATA (built by 630_bounties.py):
;   +0 u32 region count  +4 ptr "Time left: "  +8 ptr " min"
;   +12 ptr rank table: u32 count, then {u16 points needed, pad, ptr name}...
;       (ascending; the Quests screen shows "Hunter: <name> (<points>)")
;   +16 regions, 8 bytes each: +0 ptr pool, +4 u8 pool size
;   pool entries, BENT bytes: +0 u16 enemy id, +2 u16 second id (0xFFFF none),
;       +4 u8 kills, +5 u8 minutes, +8 title, +12 giver line, +16 where line,
;       +20 / +24 description lines, +28 enemy label
; Field opcode 1C [dst bank << 4][dst][cmd][region] (5 bytes) puts its result
; in the variable: cmd 0 status (0 none, 1 hunting, 2 ready to claim),
; 1 offer (the bounty on offer, picked once), 2 accept (starts the offered
; one: kills 0, deadline = now + its minutes), 3 claim (ready: ends it, gives
; its index; else 0xFF), 4 active index (0xFF none). A bounty past its
; deadline is dropped (the clock tick and every command check).

bits 32
CODE      equ 0xFDD000
DATA      equ 0xFD5000
REC       equ 60
PARTS     equ 28
VIEW      equ 8               ; rows visible in the list window
MAXLIST   equ 128             ; every quest fits (record index is a byte)
VARS      equ 0xDC08DC        ; field var bank 1, offset 0 (banks 1-5 follow)
INVENTORY equ 0xDC0234        ; savemap 0x04FC: 320 x u16 (id 9 bits, qty 7 bits)
BDATA     equ 0xFE0000        ; bounty data (630_bounties.py places it here)
BENT      equ 32
REGIONS   equ BDATA + 16
HUNTER_PTS equ VARS + 245     ; u16 field var[2][245] (630_bounties.py, saved)
RANK_X    equ 430
BREGIONS  equ 8               ; at most
NONE      equ 0xFF
KIND_BOUNTY equ 2             ; part kind: kills of bounty region (source)
ACCEPTED  equ 2
DONE      equ 4
Z_TEXT    equ 0x3dcccccd      ; 0.1f
Z_WIN     equ 0x3e4ccccd      ; 0.2f
LIST_H    equ 0xE4            ; list window height = details top (fits VIEW rows)
TEXT_X    equ 0x40

; exe functions (cdecl)
MENU_DRAW     equ 0x6C98A6    ; (state): main menu side panel / title box
MENU_DRAW_LR  equ 0x6C9D07    ; low-res variant
MENU_STATE    equ 0x6C9808    ; () -> 0 when idle in a submenu
MENU_GO       equ 0x6C9812    ; (state, id)
MENU_SET      equ 0x6C6AEE    ; (id)
DRAW_TEXT     equ 0x6F5B03    ; (x, y, text, colour, float z)
WIN_RECT      equ 0x6E7BA1    ; (short rect[4]*, x, y, w, h)
WIN_DRAW      equ 0x6E7D20    ; (rect*, float z)
HAND          equ 0x6EB3B8    ; (x, y, float z)
KEY_REPEAT    equ 0x6F53B2    ; (mask, 1) -> pressed or repeating
KEY_NEW       equ 0x41AB74    ; (mask) -> newly pressed
SOUND         equ 0x74580A    ; (id)

; battle reward loop (kill hook)
ENEMY_IDS     equ 0x9A8748    ; u16 enemy id per enemy type (3)
HOOK_BACK     equ 0x43153C

; field script engine (bounty opcode)
CUR_ENTITY    equ 0xCC0964        ; u8 current entity
SCRIPT_POS    equ 0xCC0CF8        ; u16 per entity: script offset
SCRIPT_BASE   equ 0xCBF5E8        ; ptr: script section
FIELD_TEXTS   equ 0xCC08E8        ; ptr: the field's text table (u16 count, u16 offsets from it)
SET_VAR_BYTE  equ 0x60FA7D        ; (nibble 1 = high nibble of byte 1, operand offset, value)

; minigame hooks
BIKE_ID       equ 0xFFFE          ; "Shinra motorbike" in the kill table
BALLOON_ID    equ 0xFFFD          ; "balloon" (Icicle Inn snowboard run)
BIKE_SCORE    equ 0xD85990        ; bike game score (the replaced load)
BIKE_BACK     equ 0x6566BF
SNOW_MODE     equ 0xDD865C        ; snowboard game: 1 = Icicle Inn run, 0 = Gold Saucer
SNOW_A_BACK   equ 0x737D4B
SNOW_B_BACK   equ 0x73C530
PLAY_SECONDS  equ 0xDC08B8        ; savemap 0x0B80: play time in seconds
CLOCK_BACK    equ 0x40ABFD
CLOCK_MINUTES equ VARS + 247      ; field var[2][247] (bank 1, u16)

org CODE

entry_init:   jmp near q_init
entry_update: jmp near q_update
entry_kill:   jmp near q_kill
entry_bike:   jmp near q_bike
entry_snow_a: jmp near q_snow_a
entry_snow_b: jmp near q_snow_b
entry_clock:  jmp near q_clock
entry_bounty: jmp near b_op
entry_txpoke: jmp near t_op

%macro TEXT 4                 ; x, y, text ptr, colour
    push Z_TEXT
    push %4
    push %3
    push %2
    push %1
    call DRAW_TEXT
    add esp, 20
%endmacro

%macro WINDOW 5               ; rect, x, y, w, h
    push %5
    push %4
    push %3
    push %2
    push %1
    call WIN_RECT
    add esp, 20
    push Z_WIN
    push %1
    call WIN_DRAW
    add esp, 8
%endmacro

; ---- kill hook: an enemy in formation slot [ebp-4] was defeated ---------
; Replaces `mov eax,[ebp-4]; add eax,4` at 0x431536.
q_kill:
    pushad
    mov eax, [ebp - 0x20]               ; enemy type
    movzx eax, word [ENEMY_IDS + eax*2]
    push eax
    call q_count
    pop eax
    call b_count
    popad
    mov eax, [ebp - 4]
    add eax, 4
    jmp HOOK_BACK

; ---- motorbike destroyed (bike minigame hit routine, kill path) ----------
; Replaces `mov edx,[BIKE_SCORE]` at 0x6566B9. [ebp-8] = the bike's state
; block (+0 state: 2 = already destroyed; Cloud's attack doesn't check).
q_bike:
    pushad
    mov eax, [ebp - 8]
    cmp dword [eax], 2
    je .skip
    mov eax, BIKE_ID
    call q_count
.skip:
    popad
    mov edx, [BIKE_SCORE]
    jmp BIKE_BACK

; ---- balloon popped (snowboard minigame, two pop handlers) ---------------
; Replace `mov eax,[ebp+8]; mov ecx,[eax+0x3c]` at 0x737D45 (handler A, before
; its switch on the balloon type: 0-2 = the coloured balloons worth 1/3/5
; points, 3/4 = the special ones) and at 0x73C52A (handler B). Icicle Inn run only.
q_snow_a:
    pushad
    call q_balloon
    popad
    mov eax, [ebp + 8]
    mov ecx, [eax + 0x3c]
    jmp SNOW_A_BACK

q_snow_b:
    pushad
    call q_balloon
    popad
    mov eax, [ebp + 8]
    mov ecx, [eax + 0x3c]
    jmp SNOW_B_BACK

; ---- play clock: one more second (replaces the 13-byte increment at 0x40ABF0)
q_clock:
    mov eax, [PLAY_SECONDS]
    cmp eax, [b_last]                   ; not the second we counted last: a
    je .same                            ; game was loaded (or started): no bounties
    pushad
    call b_reset
    popad
.same:
    add eax, 1
    mov [PLAY_SECONDS], eax
    mov [b_last], eax
    xor edx, edx
    mov ecx, 60
    div ecx
    cmp eax, 0xFFFF
    jbe .store
    mov eax, 0xFFFF
.store:
    mov [CLOCK_MINUTES], ax
    pushad
    call b_expire_all
    popad
    jmp CLOCK_BACK

q_balloon:
    cmp dword [SNOW_MODE], 1
    jne .no
    mov eax, BALLOON_ID
    call q_count
.no:
    ret

; ---- count one kill of enemy id eax for every accepted quest that wants it
; (clobbers eax, ecx, edx, esi, ebx; callers pushad)
q_count:
    mov esi, [DATA + 12]
.loop:
    movzx edx, word [esi]
    cmp edx, 0xFFFF
    je .done
    cmp edx, eax
    jne .next
    movzx ecx, word [esi + 2]
    cmp byte [VARS + ecx], ACCEPTED
    jne .next
    movzx ecx, word [esi + 4]
    mov bl, [VARS + ecx]
    cmp bl, [esi + 6]
    jae .next
    inc byte [VARS + ecx]
.next:
    add esi, 8
    jmp .loop
.done:
    ret

; ---- init(int): list the accepted quests, then the handed-in ones ---------
q_init:
    push ebx
    xor ecx, ecx                    ; list length
    call b_rows
    mov dl, ACCEPTED
    call q_collect
    mov dl, DONE
    call q_collect
    mov [q_n], ecx
    xor eax, eax
    mov [q_row], eax
    mov [q_top], eax
    pop ebx
    ret

; append to q_list every record whose state is dl (ecx = list length)
q_collect:
    xor ebx, ebx                    ; record index
.loop:
    cmp ebx, [DATA]
    jge .done
    cmp ecx, MAXLIST
    jge .done
    imul eax, ebx, REC
    movzx eax, word [DATA + 16 + eax]
    cmp byte [VARS + eax], dl
    jne .next
    mov [q_list + ecx], bl
    inc ecx
.next:
    inc ebx
    jmp .loop
.done:
    ret

; esi = record; ZF set if it was handed in
q_isdone:
    movzx eax, word [esi]
    cmp eax, 0xFFFF                 ; a bounty: never "handed in"
    jne .quest
    test esi, esi                   ; ZF clear
    ret
.quest:
    cmp byte [VARS + eax], DONE
    ret

; ---- helpers --------------------------------------------------------------
; edi = part; eax = progress, capped at its count (the full count once the
; quest was handed in: [q_done])
q_have:
    cmp byte [q_done], 0
    jne .full
    movzx edx, word [edi + 4]
    cmp byte [edi + 7], KIND_BOUNTY
    je .bounty
    cmp byte [edi + 7], 0
    jne .items
    movzx eax, byte [VARS + edx]
    jmp .cap
.items:
    push ebx
    push ecx
    xor eax, eax
    xor ecx, ecx
.scan:
    movzx ebx, word [INVENTORY + ecx*2]
    cmp ebx, 0xFFFF
    je .skip
    push ebx
    and ebx, 0x1FF
    cmp ebx, edx
    pop ebx
    jne .skip
    shr ebx, 9
    add eax, ebx
.skip:
    inc ecx
    cmp ecx, 320
    jl .scan
    pop ecx
    pop ebx
.cap:
    movzx edx, byte [edi + 6]
    jmp .capped
.bounty:
    movzx eax, byte [b_state + edx*8 + 2]
    jmp .cap
.capped:
    cmp eax, edx
    jbe .ret
.full:
    movzx eax, byte [edi + 6]
.ret:
    ret

; esi = record; eax = 1 if every part is complete
q_ready:
    push edi
    push ecx
    movzx ecx, byte [esi + 2]
    lea edi, [esi + PARTS]
.part:
    call q_have
    movzx edx, byte [edi + 6]
    cmp eax, edx
    jb .no
    add edi, 8
    loop .part
    mov eax, 1
    jmp .out
.no:
    xor eax, eax
.out:
    pop ecx
    pop edi
    ret

; eax = value (0..999), edi = dst; edi advanced
q_putnum:
    push ebx
    push ecx
    mov ebx, 10
    xor ecx, ecx
.div:
    xor edx, edx
    div ebx
    push edx
    inc ecx
    test eax, eax
    jnz .div
.out:
    pop eax
    add al, 0x10                    ; FF7 text '0'
    stosb
    loop .out
    pop ecx
    pop ebx
    ret

; ebx = part, edi = dst: "<label>: have/count"
q_parttext:
    push esi
    mov esi, [ebx]
.copy:
    lodsb
    cmp al, 0xFF
    je .num
    stosb
    jmp .copy
.num:
    mov ax, 0x001A                  ; ':' ' '
    stosw
    push edi
    mov edi, ebx
    call q_have
    pop edi
    call q_putnum
    mov al, 0x0F                    ; '/'
    stosb
    movzx eax, byte [ebx + 6]
    call q_putnum
    mov al, 0xFF
    stosb
    pop esi
    ret

; esi = record for list index eax
%macro RECORD 1
    mov eax, %1
    call q_rec
%endmacro

; esi = record for list index eax (0x80 + region: that region's bounty)
q_rec:
    movzx esi, byte [q_list + eax]
    test esi, 0x80
    jnz .bounty
    imul esi, esi, REC
    add esi, DATA + 16
    ret
.bounty:
    and esi, 0x7F
    imul esi, esi, REC
    add esi, b_recs
    ret

; ---- update(frame) ------------------------------------------------------
q_update:
    push ebp
    mov ebp, esp
    push ebx
    push esi
    push edi

    push dword [0xDC1210]
    cmp dword [0xDC130C], 1
    je .lowres
    call MENU_DRAW
    jmp .titled
.lowres:
    call MENU_DRAW_LR
.titled:
    add esp, 4

    cmp dword [q_n], 0
    jne .list
    TEXT TEXT_X, 13, dword [DATA + 4], 7
    jmp .windows

.list:
    mov ebx, [q_top]
.row:
    cmp ebx, [q_n]
    jge .rows_done
    mov eax, [q_top]
    add eax, VIEW
    cmp ebx, eax
    jge .rows_done
    RECORD ebx
    mov edi, 4                      ; green: handed in
    call q_isdone
    je .coloured
    mov byte [q_done], 0
    call q_ready                    ; yellow: ready to hand in, else white
    mov edi, 7
    test eax, eax
    jz .coloured
    mov edi, 6
.coloured:
    mov eax, ebx
    sub eax, [q_top]
    imul eax, eax, 26
    add eax, 13
    TEXT TEXT_X, eax, dword [esi + 4], edi
    inc ebx
    jmp .row
.rows_done:
    push Z_TEXT
    mov eax, [q_row]
    sub eax, [q_top]
    imul eax, eax, 26
    add eax, 0x12
    push eax
    push TEXT_X - 0x36
    call HAND
    add esp, 12

    mov eax, [q_row]
    RECORD eax
    cmp word [esi], 0xFFFF
    jne .not_bounty
    movzx eax, word [esi + PARTS + 4]   ; region
    call b_timetext
.not_bounty:
    call q_isdone
    sete [q_done]
    TEXT 24, LIST_H + 13, dword [esi + 4], 6
    TEXT 24, LIST_H + 39, dword [esi + 8], 7
    TEXT 24, LIST_H + 65, dword [esi + 12], 7
    TEXT 24, LIST_H + 91, dword [esi + 16], 7
    TEXT 24, LIST_H + 117, dword [esi + 20], 7
    TEXT 24, LIST_H + 143, dword [esi + 24], 7
    xor ecx, ecx                    ; part index
.part:
    movzx eax, byte [esi + 2]
    cmp ecx, eax
    jge .parts_done
    push ecx
    lea ebx, [esi + PARTS + ecx*8]
    mov edi, ecx
    shl edi, 6
    add edi, q_buf
    push edi
    call q_parttext
    pop edi
    mov ecx, [esp]
    mov eax, ecx                    ; x = 24 + (i & 1) * 300
    and eax, 1
    imul eax, eax, 300
    add eax, 24
    mov edx, ecx                    ; y = top + 169 + (i >> 1) * 26
    shr edx, 1
    imul edx, edx, 26
    add edx, LIST_H + 169
    TEXT eax, edx, edi, 7
    pop ecx
    inc ecx
    jmp .part
.parts_done:
    cmp byte [q_done], 0
    jne .handed_in
    call q_ready
    test eax, eax
    jz .windows
    TEXT 24, LIST_H + 225, dword [DATA + 8], 6
.handed_in:
    mov byte [q_done], 0

.windows:
    call b_ranktext
    TEXT RANK_X, LIST_H + 13, b_rbuf, 5
    WINDOW q_rect1, 0, 0, 0x1DC, LIST_H
    WINDOW q_rect2, 0, LIST_H, 0x280, 480 - LIST_H

    call MENU_STATE
    test eax, eax
    jnz .out
    mov ecx, [q_n]
    test ecx, ecx
    jz .cancel
    push 1
    push 0x1000                     ; up
    call KEY_REPEAT
    add esp, 8
    test eax, eax
    jz .down
    mov eax, [q_row]
    dec eax
    jns .set
    mov eax, [q_n]
    dec eax
    jmp .set
.down:
    push 1
    push 0x4000                     ; down
    call KEY_REPEAT
    add esp, 8
    test eax, eax
    jz .cancel
    mov eax, [q_row]
    inc eax
    cmp eax, [q_n]
    jl .set
    xor eax, eax
.set:
    cmp eax, [q_row]
    je .cancel
    mov [q_row], eax
    cmp eax, [q_top]                ; keep the row in view
    jge .below
    mov [q_top], eax
.below:
    sub eax, VIEW - 1
    cmp eax, [q_top]
    jle .sound
    mov [q_top], eax
.sound:
    push 1
    call SOUND
    add esp, 4
.cancel:
    push 0x40
    call KEY_NEW
    add esp, 4
    test eax, eax
    jz .out
    push 4
    call SOUND
    add esp, 4
    push 0
    push 5
    call MENU_GO
    add esp, 8
    push 0
    call MENU_SET
    add esp, 4
.out:
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret

; ---- bounties ------------------------------------------------------------
; ebx = region -> esi = its state (8 bytes: +0 offered, +1 active, +2 kills,
; +3 last claimed, +4 u16 deadline minute), edi = its pool
b_region:
    lea esi, [b_state + ebx*8]
    mov edi, [REGIONS + ebx*8]
    ret

; esi state, edi pool -> edx = active entry (or 0 when none: ZF set)
b_active:
    movzx edx, byte [esi + 1]
    cmp edx, NONE
    je .none
    imul edx, edx, BENT
    add edx, edi
    ret
.none:
    xor edx, edx
    ret

; drop region ebx's bounty if its time is up
b_expire:
    call b_region
    cmp byte [esi + 1], NONE
    je .ok
    mov ax, [CLOCK_MINUTES]
    cmp ax, [esi + 4]
    jbe .ok
    mov byte [esi + 1], NONE
.ok:
    ret

b_expire_all:
    xor ebx, ebx
.next:
    cmp ebx, [BDATA]
    jae .done
    call b_expire
    inc ebx
    jmp .next
.done:
    ret

b_reset:
    mov ecx, BREGIONS * 8
    mov edi, b_state
.fill:
    mov byte [edi], NONE
    inc edi
    loop .fill
    ret

; count a kill of enemy id eax for every region hunting it
b_count:
    xor ebx, ebx
.next:
    cmp ebx, [BDATA]
    jae .done
    push eax
    call b_region
    call b_active
    pop eax
    test edx, edx
    jz .skip
    cmp ax, [edx]
    je .hit
    cmp ax, [edx + 2]
    jne .skip
.hit:
    mov cl, [esi + 2]
    cmp cl, [edx + 4]
    jae .skip
    inc byte [esi + 2]
.skip:
    inc ebx
    jmp .next
.done:
    ret

; field opcode 1C [dst bank << 4][dst][cmd][region]
t_op:
    movzx eax, byte [CUR_ENTITY]
    movzx ecx, word [SCRIPT_POS + eax*2]
    mov edx, [SCRIPT_BASE]
    add edx, ecx                        ; edx = the op
    movzx eax, byte [edx + 1]           ; text id
    mov ecx, [FIELD_TEXTS]
    movzx eax, word [ecx + eax*2 + 2]
    add ecx, eax                        ; the text
    movzx eax, word [edx + 2]           ; offset in it
    mov dl, [edx + 4]
    mov [ecx + eax], dl
    movzx eax, byte [CUR_ENTITY]
    add word [SCRIPT_POS + eax*2], 5
    xor eax, eax
    ret

b_op:
    push ebp
    mov ebp, esp
    push ebx
    push esi
    push edi
    movzx eax, byte [CUR_ENTITY]
    movzx ecx, word [SCRIPT_POS + eax*2]
    mov edx, [SCRIPT_BASE]
    add edx, ecx
    movzx ebx, byte [edx + 4]           ; region
    movzx eax, byte [edx + 3]           ; command
    call b_cmd
    push eax
    push 2
    push 1
    call SET_VAR_BYTE
    add esp, 12
    movzx eax, byte [CUR_ENTITY]
    add word [SCRIPT_POS + eax*2], 5
    xor eax, eax
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret

; eax = command, ebx = region -> eax = result
b_cmd:
    cmp ebx, [BDATA]
    jae .bad
    push eax
    call b_expire
    pop eax
    cmp eax, 0
    je .status
    cmp eax, 1
    je .offer
    cmp eax, 2
    je .accept
    cmp eax, 3
    je .claim
    cmp eax, 4
    je .active
.bad:
    mov eax, NONE
    ret
.status:
    call b_active
    xor eax, eax
    test edx, edx
    jz .ret
    mov eax, 1
    mov cl, [esi + 2]
    cmp cl, [edx + 4]
    jb .ret
    mov eax, 2
.ret:
    ret
.offer:
    movzx eax, byte [esi]
    cmp eax, NONE
    jne .ret
    movzx ecx, byte [REGIONS + 4 + ebx*8]   ; pool size
    mov eax, [PLAY_SECONDS]
    add eax, [b_seed]
    add dword [b_seed], 7
    xor edx, edx
    div ecx
    mov eax, edx
    cmp ecx, 1
    je .picked
    cmp al, [esi + 3]                   ; not the one just claimed
    jne .picked
    inc eax
    cmp eax, ecx
    jb .picked
    xor eax, eax
.picked:
    mov [esi], al
    ret
.accept:
    call .offer
    mov byte [esi], NONE
    mov [esi + 1], al
    mov byte [esi + 2], 0
    push eax
    call b_active
    movzx ecx, byte [edx + 5]
    add cx, [CLOCK_MINUTES]
    mov [esi + 4], cx
    pop eax
    ret
.claim:
    call .status
    cmp eax, 2
    jne .bad
    movzx eax, byte [esi + 1]
    mov [esi + 3], al
    mov byte [esi + 1], NONE
    ret
.active:
    movzx eax, byte [esi + 1]
    ret

; quest list rows for the active bounties (ecx = list length, advanced)
b_rows:
    push esi
    push edi
    xor ebx, ebx
.next:
    cmp ebx, [BDATA]
    jae .done
    call b_region
    call b_active
    test edx, edx
    jz .skip
    imul eax, ebx, REC
    add eax, b_recs
    mov word [eax], 0xFFFF
    mov byte [eax + 2], 1               ; one part
    mov esi, [edx + 8]
    mov [eax + 4], esi                  ; title
    mov esi, [edx + 12]
    mov [eax + 8], esi                  ; giver
    mov esi, [edx + 16]
    mov [eax + 12], esi                 ; where
    mov esi, [edx + 20]
    mov [eax + 16], esi
    mov esi, [edx + 24]
    mov [eax + 20], esi
    mov dword [eax + 24], b_tbuf        ; time left (b_timetext)
    mov esi, [edx + 28]
    mov [eax + PARTS], esi              ; label
    mov [eax + PARTS + 4], bx           ; source: region
    mov dl, [edx + 4]
    mov [eax + PARTS + 6], dl           ; kills needed
    mov byte [eax + PARTS + 7], KIND_BOUNTY
    cmp ecx, MAXLIST
    jge .skip
    mov al, bl
    or al, 0x80
    mov [q_list + ecx], al
    inc ecx
.skip:
    inc ebx
    jmp .next
.done:
    pop edi
    pop esi
    ret

; b_tbuf = "Time left: N min" for region eax
b_timetext:
    push esi
    push edi
    push ebx
    mov ebx, eax
    mov edi, b_tbuf
    mov esi, [BDATA + 4]
    call b_copy
    movzx eax, word [b_state + ebx*8 + 4]
    movzx edx, word [CLOCK_MINUTES]
    sub eax, edx
    jns .pos
    xor eax, eax
.pos:
    cmp eax, 999
    jbe .num
    mov eax, 999
.num:
    call q_putnum
    mov esi, [BDATA + 8]
    call b_copy
    mov byte [edi], 0xFF
    pop ebx
    pop edi
    pop esi
    ret

; b_rbuf = "Hunter: <rank> (<points>)"
b_ranktext:
    push esi
    push edi
    push ebx
    mov edi, b_rbuf
    mov esi, [BDATA + 12]
    mov ecx, [esi]                      ; ranks
    lea ebx, [esi + 4]
    mov edx, [ebx + 4]                  ; the first (0 points)
    movzx eax, word [HUNTER_PTS]
.find:
    cmp ax, [ebx]
    jb .found
    mov edx, [ebx + 4]
    add ebx, 8
    loop .find
.found:
    push eax
    mov esi, b_hunter
    call b_copy
    mov esi, edx
    call b_copy
    mov ax, 0x0800                      ; ' ' '('
    stosw
    pop eax
    cmp eax, 999
    jbe .num
    mov eax, 999
.num:
    call q_putnum
    mov ax, 0xFF09                      ; ')' end
    stosw
    pop ebx
    pop edi
    pop esi
    ret

; copy FF7 text esi (0xFF-terminated, without it) to edi
b_copy:
    lodsb
    cmp al, 0xFF
    je .done
    stosb
    jmp b_copy
.done:
    ret

; ---- variables -----------------------------------------------------------
align 4
q_n:     dd 0
q_done:  db 0, 0, 0, 0
q_row:   dd 0
q_top:   dd 0
q_rect1: dw 0, 0, 0, 0
q_rect2: dw 0, 0, 0, 0
q_list:  times MAXLIST db 0
q_buf:   times 4 * 64 db 0xFF
b_last:  dd 0xFFFFFFFF
b_seed:  dd 0
b_state: times BREGIONS * 8 db NONE
b_tbuf:  times 32 db 0xFF
b_rbuf:  times 40 db 0xFF
b_hunter: db 0x28, 0x55, 0x4E, 0x54, 0x45, 0x52, 0x1A, 0x00, 0xFF   ; "Hunter: " 
b_recs:  times BREGIONS * REC db 0

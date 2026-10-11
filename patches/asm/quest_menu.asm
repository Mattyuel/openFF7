; openFF7 quests: the "Quests" main-menu screen (menu id 11, an empty stub in
; the original) and the battle kill counter.
; Assembled with: nasm -f bin quest_menu.asm -o quest_menu.bin
; 600_quests.py places the binary at CODE and the data block at DATA (both
; asserted there). Entry points (5-byte jmp stubs): CODE+0 menu init(int),
; CODE+5 menu update(frame), CODE+10 kill hook (jumped to from 0x431536).
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

bits 32
CODE      equ 0xFD8000
DATA      equ 0xFD5000
REC       equ 60
PARTS     equ 28
VIEW      equ 8               ; rows visible in the list window
MAXLIST   equ 32
VARS      equ 0xDC08DC        ; field var bank 1, offset 0 (banks 1-5 follow)
INVENTORY equ 0xDC0234        ; savemap 0x04FC: 320 x u16 (id 9 bits, qty 7 bits)
ACCEPTED  equ 2
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

org CODE

entry_init:   jmp near q_init
entry_update: jmp near q_update
entry_kill:   jmp near q_kill

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
    popad
    mov eax, [ebp - 4]
    add eax, 4
    jmp HOOK_BACK

; ---- init(int): list the accepted quests --------------------------------
q_init:
    push ebx
    xor ecx, ecx                    ; list length
    xor ebx, ebx                    ; record index
.loop:
    cmp ebx, [DATA]
    jge .done
    imul eax, ebx, REC
    movzx eax, word [DATA + 16 + eax]
    cmp byte [VARS + eax], ACCEPTED
    jne .next
    mov [q_list + ecx], bl
    inc ecx
    cmp ecx, MAXLIST
    jge .done
.next:
    inc ebx
    jmp .loop
.done:
    mov [q_n], ecx
    xor eax, eax
    mov [q_row], eax
    mov [q_top], eax
    pop ebx
    ret

; ---- helpers --------------------------------------------------------------
; edi = part; eax = progress, capped at its count
q_have:
    movzx edx, word [edi + 4]
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
    cmp eax, edx
    jbe .ret
    mov eax, edx
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
    movzx esi, byte [q_list + %1]
    imul esi, esi, REC
    add esi, DATA + 16
%endmacro

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
    call q_ready                    ; green when ready to hand in
    mov edi, 7
    test eax, eax
    jz .white
    mov edi, 4
.white:
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
    call q_ready
    test eax, eax
    jz .windows
    TEXT 24, LIST_H + 225, dword [DATA + 8], 4

.windows:
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

; ---- variables -----------------------------------------------------------
align 4
q_n:     dd 0
q_row:   dd 0
q_top:   dd 0
q_rect1: dw 0, 0, 0, 0
q_rect2: dw 0, 0, 0, 0
q_list:  times MAXLIST db 0
q_buf:   times 4 * 64 db 0xFF

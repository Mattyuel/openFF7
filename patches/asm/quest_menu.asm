; openFF7: "Quests" main-menu screen (menu id 11, an empty stub in the original).
; Assembled with: nasm -f bin quest_menu.asm -o quest_menu.bin
; The build (patches/600_quests.py) places the binary at CODE and writes the
; quest records at DATA; both addresses are asserted there. Entry points:
; CODE+0 = init(int), CODE+INIT_SIZE... see the jump stubs below.
;
; DATA layout (built by 600_quests.py):
;   +0  u32 record count     +4 ptr "No quests" text    +8 ptr "ready" text
;   +12 records, REC bytes each:
;       +0 u8 state offset (bank 3)  +1 u8 kind (0 kill, 1 deliver)
;       +2 u8 count  +3 pad  +4 u16 item  +6 pad
;       +8 name  +12 giver line  +16 where line  +20/+24/+28 description
;       +32 progress label           (all pointers to FF7 text, 0xFF-ended)

bits 32
CODE      equ 0xFD6000
DATA      equ 0xFD5800
REC       equ 36
MAXLIST   equ 8
BANK3     equ 0xDC0ADC        ; field var bank 3, offset 0
INVENTORY equ 0xDC0234        ; savemap 0x04FC: 320 x u16 (id 9 bits, qty 7 bits)
ACCEPTED  equ 2
Z_TEXT    equ 0x3dcccccd      ; 0.1f
Z_WIN     equ 0x3e4ccccd      ; 0.2f
LIST_H    equ 0xD8            ; list window height = details top
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

org CODE

entry_init:   jmp near q_init
entry_update: jmp q_update

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

; ---- init(int): list the accepted quests --------------------------------
q_init:
    push ebx
    xor ecx, ecx                    ; list length
    xor ebx, ebx                    ; record index
.loop:
    cmp ebx, [DATA]
    jge .done
    imul eax, ebx, REC
    movzx eax, byte [DATA + 12 + eax]
    cmp byte [BANK3 + eax], ACCEPTED
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
    mov dword [q_row], 0
    pop ebx
    ret

; ---- record helpers (esi = record) -----------------------------------------
; eax = progress so far, capped at the count
q_have:
    movzx eax, byte [esi]
    cmp byte [esi + 1], 0
    jne .items
    movzx eax, byte [BANK3 + eax + 1]   ; kill counter
    jmp .cap
.items:
    push ebx
    push ecx
    xor eax, eax
    xor ecx, ecx
.scan:
    movzx edx, word [INVENTORY + ecx*2]
    cmp edx, 0xFFFF
    je .skip
    mov ebx, edx
    and ebx, 0x1FF
    cmp bx, [esi + 4]
    jne .skip
    shr edx, 9
    add eax, edx
.skip:
    inc ecx
    cmp ecx, 320
    jl .scan
    pop ecx
    pop ebx
.cap:
    movzx edx, byte [esi + 2]
    cmp eax, edx
    jbe .ret
    mov eax, edx
.ret:
    ret

; edi = dst; eax = value (0..999); edi advanced
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

; q_buf = "<label>: have/count"; returns eax = 1 if complete
q_progress:
    push edi
    push esi
    mov edi, q_buf
    mov edx, [esi + 32]
.copy:
    mov al, [edx]
    cmp al, 0xFF
    je .num
    stosb
    inc edx
    jmp .copy
.num:
    mov ax, 0x001A                  ; ':' ' '
    stosw
    call q_have
    push eax
    call q_putnum
    mov al, 0x0F                    ; '/'
    stosb
    movzx eax, byte [esi + 2]
    call q_putnum
    mov al, 0xFF
    stosb
    pop eax
    movzx edx, byte [esi + 2]
    cmp eax, edx
    setae al
    movzx eax, al
    pop esi
    pop edi
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
    xor ebx, ebx
.row:
    cmp ebx, [q_n]
    jge .rows_done
    movzx esi, byte [q_list + ebx]
    imul esi, esi, REC
    add esi, DATA + 12
    call q_progress                 ; green when ready to hand in
    mov edi, 7
    test eax, eax
    jz .white
    mov edi, 4
.white:
    imul eax, ebx, 26
    add eax, 13
    TEXT TEXT_X, eax, dword [esi + 8], edi
    inc ebx
    jmp .row
.rows_done:
    push Z_TEXT
    imul eax, [q_row], 26
    add eax, 0x12
    push eax
    push TEXT_X - 0x36
    call HAND
    add esp, 12

    mov eax, [q_row]
    movzx esi, byte [q_list + eax]
    imul esi, esi, REC
    add esi, DATA + 12
    TEXT 24, LIST_H + 13, dword [esi + 8], 6
    TEXT 24, LIST_H + 39, dword [esi + 12], 7
    TEXT 24, LIST_H + 65, dword [esi + 16], 7
    TEXT 24, LIST_H + 99, dword [esi + 20], 7
    TEXT 24, LIST_H + 125, dword [esi + 24], 7
    TEXT 24, LIST_H + 151, dword [esi + 28], 7
    call q_progress
    mov ebx, eax
    TEXT 24, LIST_H + 185, q_buf, 7
    test ebx, ebx
    jz .windows
    TEXT 24, LIST_H + 211, dword [DATA + 8], 4

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
q_rect1: dw 0, 0, 0, 0
q_rect2: dw 0, 0, 0, 0
q_list:  times MAXLIST db 0
q_buf:   times 64 db 0xFF

"""Quests: new NPCs ("givers") offer quests; talking to them again once the
requirement is met completes the quest and gives the reward. A floating
materia orb over a giver marks it: yellow = a quest to offer, blue = one ready
to hand in, hidden otherwise. Givers turn to face the player when talked to.

Kinds:
  kill    defeat `count` enemies whose ids are in `enemies` (any mix).
  deliver bring `count` of item `item`; they are taken on hand-in.

Each giver's quests run in order: the next is offered once the previous is
done (that's how the Manager's No.5 job is gated behind the No.1 job).

Save data (see CLAUDE.md, bank 3 offsets 192-255 are free): each quest has a
state byte (0 new, 2 accepted, 4 done) and kill quests a counter byte right
after it.

Kill counting is an exe hook: the victory reward loop (0x431481) walks the
formation's six enemy slots; for each one that died it reaches 0x431536
(`mov eax,[ebp-4]; add eax,4`, 6 bytes), which is replaced with a jump to the
code below (in the exe's new .openff7 section). It looks the enemy id up
(word [0x9A8748 + type*2], type = [ebp-0x20]) in a table of
{u16 enemy id, u8 quest offset, u8 count} and, if that quest is accepted and
its counter is below the count, increments the counter. Then it replays the
6 replaced bytes and jumps back to 0x43153C. Source (nasm, org = code VA):

    pushad
    mov eax, [ebp-0x20]
    movzx eax, word [0x9A8748 + eax*2]
    mov esi, TABLE
  .loop:
    movzx edx, word [esi]
    cmp edx, 0xFFFF
    je .done
    cmp edx, eax
    jne .next
    movzx ecx, byte [esi+2]
    cmp byte [ecx + BANK3], 2           ; accepted?
    jne .next
    mov bl, [ecx + BANK3 + 1]
    cmp bl, [esi+3]
    jae .next
    inc byte [ecx + BANK3 + 1]
  .next:
    add esi, 4
    jmp .loop
  .done:
    popad
    mov eax, [ebp-4]
    add eax, 4
    jmp 0x43153C
"""
import os
import struct

from _recruit import say, xyzi
from _travel import add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

BANK = 11                      # field var nibble for bank 3 (8-bit)
BANK3_MEM = 0xDC0ADC           # bank 3 offset 0 in memory (savemap 0x0DA4)
NEW, ACCEPTED, DONE = 0, 2, 4
ITEM_COUNT = (5, 232)          # temp var: CKITM result
MODE, SHOWN = (5, 233), (5, 234)   # temp vars: marker mode wanted / applied

ORB_MODEL = ("nmkin_5", 3)     # fieldbg_mtra3: the materia orb
ORB_HEIGHT = 160               # above the giver's feet (200 was too high in game)
ORB_TINT = {1: (120, 100, -120),   # yellow: quest to offer
            2: (-80, -20, 140)}    # blue: ready to hand in

HOOK_VA, HOOK_OLD = 0x431536, bytes.fromhex("8b45fc83c004")
HOOK_BACK = 0x43153C
ENEMY_IDS = 0x9A8748           # loaded scene's enemy ids (u16 x 3)

GIL_TEXT = "%d gil"
ITEMS = {0: "Potion", 1: "Hi-Potion", 3: "Ether", 5: "Elixir"}
MATERIA = {1: "HP Plus", 36: "Steal"}

Q = {}   # quest id -> state offset in bank 3 (counter = offset + 1)
Q["manager_n1"], Q["manager_n5"], Q["betty"], Q["gwen"] = 192, 194, 196, 198


def M(speaker, *lines):
    """One message page: speaker line + quoted lines (keep each <= 38 chars)."""
    body = "\n ".join(lines)
    text = "%s\n“%s”" % (speaker, body)
    for line in text.split("\n"):
        assert len(line) <= 38, line
    return text


MGR, BETTY, GWEN = "Middle Manager", "Betty", "Gwen"

GIVERS = [
    dict(field="md8brdg", name="manager", model=("blin1", 9), at=(-620, 250), dir=0x40,
         who=MGR, where="Upper Midgar, Sector 8 walkway",
         quests=[
             dict(id="manager_n1", kind="kill", enemies=[19, 20, 18, 21], count=8,
                  title="Pest Control: No.1 Reactor", label="Defeated",
                  desc=["Scrap 8 Grunts, Sweepers, 1st Rays or",
                        "Mono Drives in No.1 Reactor so the Middle",
                        "Manager can close his ticket."],
                  offer=[M(MGR, "Ah, a contractor! Excellent.",
                           "No.1 Reactor is overrun with...",
                           "let's call them 'unpaid interns'."),
                         M(MGR, "Grunts, Sweepers, 1st Rays,",
                           "Mono Drives. Scrap 8 of them and",
                           "I can finally close this ticket.")],
                  ask=M(MGR, "Do we have a deal?"),
                  choices=["Consider it done.", "I don't do tickets."],
                  accept=M(MGR, "Splendid. I'll file you under",
                           "'miscellaneous expenses'."),
                  decline=M(MGR, "Let's circle back. Forever."),
                  progress=M(MGR, "My spreadsheet says the No.1",
                             "Reactor still has pests. I need 8",
                             "scrapped. Think synergy!"),
                  done=[M(MGR, "8 confirmed! I'll take full credit",
                          "at the quarterly review, naturally.",
                          "Here's your... honorarium.")],
                  reward=dict(gil=500, items=[(1, 3)])),
             dict(id="manager_n5", kind="kill", enemies=[32, 29, 31], count=8,
                  title="Pest Control: No.5 Reactor", label="Defeated",
                  desc=["Scrap 8 Smoggers, Blood Tastes or Proto",
                        "Machineguns in No.5 Reactor. His bonus",
                        "depends on it."],
                  offer=[M(MGR, "Great news! Your work was so",
                           "adequate, you've been promoted",
                           "to No.5 Reactor. Same pay."),
                         M(MGR, "Smoggers, Blood Tastes, Proto",
                           "Machineguns. 8 of them. My bonus",
                           "depends on it. Er, the company's.")],
                  ask=M(MGR, "Shall I pencil you in?"),
                  choices=["Fine.", "I want a raise."],
                  accept=M(MGR, "Wonderful. Remember: there's no",
                           "'I' in 'hazard pay'."),
                  decline=M(MGR, "A raise? Ha! Ha ha. No."),
                  progress=M(MGR, "No.5 Reactor, 8 pests. The board",
                             "meets soon and I'd rather not be",
                             "reassigned to the Mako pipes."),
                  done=[M(MGR, "Outstanding! That's a corner",
                          "office for me and... this for you.",
                          "Don't tell accounting.")],
                  reward=dict(gil=1000, items=[(3, 2)], materia=[36])),
         ],
         all_done=M(MGR, "I'm Upper Middle Manager now.",
                    "Same desk, but the chair spins.")),

    # Model std_girl3 (Chole at the chocobo farm). At (440, -860) she blocked
    # the path; moved straight up the screen by ~4x her on-screen height
    # (ff7.camera: screen (-47, 173) -> (-47, -5)).
    dict(field="mds6_2", name="betty", model=("frcyo", 3), at=(-120, -280), dir=0x40,
         who=BETTY, where="Sector 6 playground",
         quests=[
             dict(id="betty", kind="kill", enemies=[44, 45], count=2,
                  title="The Bullies", label="Hell Houses beaten",
                  desc=["Beat up 2 Hell Houses so Betty can play",
                        "in the street. They're mean on the",
                        "inside too."],
                  offer=[M(BETTY, "Hey mister! There's big mean",
                           "HOUSES out there and they won't",
                           "let me play in the street!"),
                         M(BETTY, "They just stand there being",
                           "houses AT people. Beat up 2 of",
                           "them! I'll give you my allowance!")],
                  ask=M(BETTY, "Pleeeease?"),
                  choices=["Sure, kid.", "Houses can't move."],
                  accept=M(BETTY, "Yay! Get those Hell Houses!",
                           "They're mean on the inside too!"),
                  decline=M(BETTY, "That's what they WANT you",
                            "to think!"),
                  progress=M(BETTY, "Did you beat up 2 Hell Houses?",
                             "I can hear them being houses",
                             "from here."),
                  done=[M(BETTY, "You did it! The street is SAFE!",
                          "Here's my whole allowance. And",
                          "a bottle from Daddy's cabinet.")],
                  reward=dict(gil=37, items=[(5, 1)])),
         ],
         all_done=M(BETTY, "Mom STILL says I can't play there.",
                    "'Monsters', she says. Grown-ups",
                    "are so weird.")),

    dict(field="mds5_3", name="gwen", model=("mds5_1", 5), at=(-280, -100), dir=0xC0,
         who=GWEN, where="Sector 5 slums, by the tunnel",
         quests=[
             dict(id="gwen", kind="deliver", item=0, count=3,
                  title="A Dare Too Far", label="Potions",
                  desc=["Bring Gwen 3 Potions for her neighbour",
                        "Rufus, who licked a Mako pipe on a dare.",
                        "Again."],
                  offer=[M(GWEN, "Oh, thank goodness, a person!",
                           "My neighbour Rufus (not THAT",
                           "Rufus) is sick as a dog."),
                         M(GWEN, "He licked a Mako pipe on a dare.",
                           "Again. 3 Potions should sort him",
                           "out. Could you find some?")],
                  ask=M(GWEN, "Will you help?"),
                  choices=["I'll bring 3.", "Sounds like a him problem."],
                  accept=M(GWEN, "Bless you! 3 Potions. He's",
                           "glowing a bit, so do hurry."),
                  decline=M(GWEN, "Fair. He did lick it twice."),
                  progress=M(GWEN, "3 Potions, love. He's started",
                             "humming like a reactor."),
                  done=[M(GWEN, "3 Potions! That'll stop the",
                          "glowing. Mostly. He wants you",
                          "to have his old materia.")],
                  reward=dict(materia=[1])),
         ],
         all_done=M(GWEN, "Rufus is right as rain! He's",
                    "already eyeing the next pipe.")),
]

_NOT = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}


def jump_if(a, cmp, b, target):
    """if (a cmp b) goto target."""
    return asm.if_byte(a, _NOT[cmp], b, target)


def state(q):
    return (BANK, Q[q["id"]])


def counter(q):
    return (BANK, Q[q["id"]] + 1)


def _not_met(q, target):
    """Ops: goto target unless the quest's requirement is met."""
    if q["kind"] == "kill":
        return [jump_if(counter(q), "<", q["count"], target)]
    return [Op(bytes([0x5A, ITEM_COUNT[0]]) + struct.pack("<H", q["item"]) + bytes([ITEM_COUNT[1]])),  # CKITM
            jump_if(ITEM_COUNT, "<", q["count"], target)]


def _reward(sec, q):
    r = q["reward"]
    ops, got = [], []
    if r.get("gil"):
        ops.append(Op(bytes([0x39, 0]) + struct.pack("<I", r["gil"])))           # GOLDU
        got.append(GIL_TEXT % r["gil"])
    for item, qty in r.get("items", []):
        ops.append(asm.add_item(item, qty))                                        # STITM
        got.append("%d %s%s" % (qty, ITEMS[item], "s" if qty > 1 else ""))
    for m in r.get("materia", []):
        ops.append(Op(bytes([0x5B, 0, 0, m, 0, 0, 0])))                           # SMTRA, 0 AP
        got.append("“%s” Materia" % MATERIA[m])
    return ops + say(sec, "Received " + ",\n".join(got) + "!")


def _talk(giver):
    def build(sec):
        end = [Op(b"\x33\x00"), asm.ret()]                                         # UC 00
        ops = [Op(b"\x33\x01"),                                                    # UC 01
               Op(b"\x35\x00\x08\x02"),                                            # PTURA: face the leader
               Op(b"\x24\x08\x00")]                                                # WAIT 8 (turning)
        for q in giver["quests"]:
            nxt, active, progress = asm.nop(), asm.nop(), asm.nop()
            ops += [jump_if(state(q), "==", DONE, nxt),
                    jump_if(state(q), "==", ACCEPTED, active)]
            for page in q["offer"]:
                ops += say(sec, page)
            accept = [asm.setbyte(state(q), ACCEPTED)]
            if q["kind"] == "kill":
                accept.append(asm.setbyte(counter(q), 0))
            accept += say(sec, q["accept"])
            ops += choice_menu(sec, q["ask"], q["choices"], [accept, say(sec, q["decline"])])
            ops += [active] + _not_met(q, progress)
            if q["kind"] == "deliver":
                ops.append(Op(bytes([0x59, 0]) + struct.pack("<H", q["item"]) + bytes([q["count"]])))  # DLITM
            for page in q["done"]:
                ops += say(sec, page)
            ops += _reward(sec, q) + [asm.setbyte(state(q), DONE)] + end
            ops += [progress] + say(sec, q["progress"]) + end
            ops.append(nxt)
        return ops + say(sec, giver["all_done"]) + end
    return build


def _marker_mode(giver):
    """Ops: MODE = 1 (offer), 2 (ready to hand in) or 0 for the giver's
    first quest that isn't done."""
    out = asm.nop()
    ops = [asm.setbyte(MODE, 0)]
    for q in giver["quests"]:
        nxt, offer = asm.nop(), asm.nop()
        ops += [jump_if(state(q), "==", DONE, nxt),
                jump_if(state(q), "==", NEW, offer)]
        ops += _not_met(q, out)
        ops += [asm.setbyte(MODE, 2), asm.goto(out),
                offer, asm.setbyte(MODE, 1), asm.goto(out), nxt]
    return ops + [out]


def _tint(rgb):
    col = struct.pack("<3h", *rgb) * 2
    return [Op(bytes([0x28, 0x18, 0x06, 0x00, 0x00]) + col + bytes.fromhex("01000100010001")),  # KAWAI 06 colour
            Op(b"\x24\x01\x00"),                                                   # WAIT 1
            Op(b"\x28\x04\x06\x01"),                                               # KAWAI 06 apply
            Op(b"\x29")]                                                           # KAWIW


def _marker_main(giver):
    """Main loop: every 10 frames recompute the mode; on a change show/hide
    and retint. (The field isn't re-initialised after a battle.)"""
    top, wait, shown = asm.nop(), asm.nop(), asm.nop()
    ops = [top] + _marker_mode(giver)
    ops += [jump_if(MODE, "==", SHOWN, wait), asm.setbyte(SHOWN, MODE),
            jump_if(MODE, "!=", 0, shown), Op(b"\xA4\x00"), asm.goto(wait),        # VISI 00
            shown, Op(b"\xA4\x01")]                                                # VISI 01
    for mode, rgb in ORB_TINT.items():
        skip = asm.nop()
        ops += [jump_if(MODE, "!=", mode, skip)] + _tint(rgb) + [skip]
    return ops + [wait, Op(b"\x24\x0A\x00"), asm.goto_back(top)]                  # WAIT 10


def _spot(ctx, field, x, y):
    mesh = Walkmesh(ctx.field(field).section("walkmesh"))
    tri = mesh.find(x, y)
    assert tri is not None, "%s: (%d, %d) is not on the walkmesh" % (field, x, y)
    return x, y, mesh.height(tri, x, y), tri


def _add_marker(ctx, giver, pos):
    field = giver["field"]
    model = copy_model(ctx, field, *ORB_MODEL)
    x, y, z, tri = pos
    sec = Script.parse(ctx.field(field).sections[0])
    init = [Op(bytes([0xA1, model])), xyzi(x, y, z + ORB_HEIGHT, tri),
            Op(b"\x7E\x01"), Op(b"\xC7\x01"), Op(b"\xA4\x00"),                   # TLKON 01, SOLID 01, VISI 00
            asm.setbyte(SHOWN, 0), asm.ret()]
    sec.add_entity(giver["name"][:6] + "_q", {0: init + _marker_main(giver) + [asm.ret()]})
    ctx.field(field).sections[0] = sec.build()


def _kill_hook(ctx):
    rows = b""
    for g in GIVERS:
        for q in g["quests"]:
            if q["kind"] != "kill":
                continue
            assert q["count"] < 256
            for e in q["enemies"]:
                rows += struct.pack("<HBB", e, Q[q["id"]], q["count"])
    exe = ctx.exe()
    table = exe.alloc(rows + b"\xff\xff\0\0", "quest_kills")
    code_va = exe.cursor + (-exe.cursor % 16)
    b3 = BANK3_MEM
    code = (b"\x60" + b"\x8b\x45\xe0"
            + b"\x0f\xb7\x84\x00" + struct.pack("<I", ENEMY_IDS)
            + b"\xbe" + struct.pack("<I", table)
            + b"\x0f\xb7\x16" + b"\x81\xfa\xff\xff\x00\x00" + b"\x74\x27"
            + b"\x39\xc2" + b"\x75\x1e"
            + b"\x0f\xb6\x4e\x02"
            + b"\x80\xb9" + struct.pack("<I", b3) + bytes([ACCEPTED]) + b"\x75\x11"
            + b"\x8a\x99" + struct.pack("<I", b3 + 1)
            + b"\x3a\x5e\x03" + b"\x73\x06"
            + b"\xfe\x81" + struct.pack("<I", b3 + 1)
            + b"\x83\xc6\x04" + b"\xeb\xce"
            + b"\x61" + HOOK_OLD + b"\xe9")
    code += struct.pack("<i", HOOK_BACK - (code_va + len(code) + 4))
    assert len(code) == 0x4F
    exe.place_at(code_va, code, "quest_kill_hook")
    jmp = b"\xe9" + struct.pack("<i", code_va - (HOOK_VA + 5)) + b"\x90"
    exe.patch(HOOK_VA, HOOK_OLD, jmp, "reward loop -> quest kill counter")


# ---- Quests main-menu entry ------------------------------------------------
# A 12th main-menu row "Quests" above Quit, opening menu id 11 (an empty stub
# in the original: init 0x6FEB00 / update 0x6FEB0F). Row 10's row->id byte
# (0x91AAF8) is already 0x0B and the title/cursor-return code uses id-1 = row,
# so only counts, heights, masks, labels and the confirm jump table change.
# The screen itself is patches/asm/quest_menu.asm (prebuilt .bin committed).
SECTION_VA = 0xFD5000
MENU_DATA_VA, MENU_CODE_VA = 0xFD5800, 0xFD6000   # = DATA / CODE in quest_menu.asm
MENU_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asm", "quest_menu.bin")
QUESTS_ID = 11
LABELS, ROW_TO_ID = 0x91A8C0, 0x91AAF8
MENU_INIT, MENU_UPDATE = 0x91AB40, 0x91AB98
CONFIRM_TABLE, ROW_SUBMENU, ROW_QUIT = 0x6CB53E, 0x6CA52F, 0x6CA584
REC_SIZE = 36

# (va, old bytes, new bytes, what)
MENU_PATCHES = [
    (0x6CA3BC, "80cc04", "80cc0c", "visible mask: force Quests + Quit rows (bits 10, 11)"),
    (0x6CA3F5, "6681e1fffb", "6681e1fff3", "lock mask: never lock rows 10, 11"),
    (0x6CA174, "6a0b", "6a0c", "main cursor: 12 view rows"),
    (0x6CA17C, "6a0b", "6a0c", "main cursor: 12 rows"),
    (0x6C9AC6, "83f80b", "83f80c", "draw 12 labels"),
    (0x6C9F27, "83f80b", "83f80c", "draw 12 labels (low-res)"),
    (0x6CA4F9, "83bd78fbffff0a", "83bd78fbffff0b", "confirm: rows 0..11"),
    (0x6C9A84, "c7058012dc0038010000", "c7058012dc0052010000", "window height 0x138 -> 0x152"),
    (0x6C9987, "69c01e010000", "69c038010000", "opening animation height"),
    (0x6C9C51, "69c005010000", "69c01f010000", "returning animation height"),
    (0x6CB5DB, "80e264", "80e257", "initial height (low-res 0x9C -> 0xA9)"),
    (0x6CB5DE, "81c238010000", "81c252010000", "initial height 0x138 -> 0x152"),
    (0x6C9EE5, "c7058012dc009c000000", "c7058012dc00a9000000", "low-res window height"),
    (0x6C9DE8, "69c08f000000", "69c09c000000", "low-res opening animation"),
    (0x6CA0B2, "69c082000000", "69c08f000000", "low-res returning animation"),
]


def _quest_log_data(base):
    """DATA block for quest_menu.asm: header, records, then the strings."""
    quests = [(g, q) for g in GIVERS for q in g["quests"]]
    head = 12 + REC_SIZE * len(quests)
    pool = bytearray()

    def text(t):
        va = base + head + len(pool)
        pool.extend(encode(t))
        return va
    none, ready = text("No quests in progress."), text("Done! Report back to the quest giver.")
    recs = b""
    for g, q in quests:
        ptrs = [text(q["title"]), text("From: " + g["who"]), text("Where: " + g["where"])]
        ptrs += [text(line) for line in q["desc"]] + [text(q["label"])]
        assert len(q["desc"]) == 3 and all(len(l) <= 46 for l in q["desc"]), q["id"]
        recs += struct.pack("<BBBxHxx7I", Q[q["id"]], 0 if q["kind"] == "kill" else 1,
                            q["count"], q.get("item", 0), *ptrs)
    assert len(recs) == REC_SIZE * len(quests)
    return struct.pack("<3I", len(quests), none, ready) + recs + bytes(pool)


def _quest_menu(ctx):
    exe = ctx.exe()
    assert exe.section_va == SECTION_VA, hex(exe.section_va)
    data = _quest_log_data(MENU_DATA_VA)
    assert len(data) <= MENU_CODE_VA - MENU_DATA_VA, len(data)
    exe.place_at(MENU_DATA_VA, data, "quest_log_data")
    code = open(MENU_BIN, "rb").read()
    exe.place_at(MENU_CODE_VA, code, "quest_menu")
    init_va, update_va = MENU_CODE_VA, MENU_CODE_VA + 5      # jmp near stubs at the start
    assert code[0] == 0xE9 and code[5] == 0xE9

    for va, old, new, what in MENU_PATCHES:
        exe.patch(va, bytes.fromhex(old), bytes.fromhex(new), what)
    old_table = struct.unpack("<11I", exe.read(CONFIRM_TABLE, 44))
    assert old_table[10] == ROW_QUIT, old_table
    table = exe.alloc(struct.pack("<12I", *old_table[:10], ROW_SUBMENU, ROW_QUIT), "confirm_table")
    exe.patch_u32(0x6CA50F, CONFIRM_TABLE, table, "confirm jump table (12 rows)")
    assert exe.read(ROW_TO_ID + 10, 1)[0] == QUESTS_ID
    quit_label = exe.read(LABELS + 10 * 20, 20)
    assert quit_label.startswith(encode("Quit")), quit_label.hex()
    exe.patch(LABELS + 10 * 20, quit_label, encode("Quests").ljust(20, b"\0"), "row 10 label")
    exe.patch(LABELS + 11 * 20, exe.read(LABELS + 11 * 20, 20), quit_label, "row 11 label = Quit")
    exe.patch_u32(MENU_INIT + 4 * QUESTS_ID, 0x6FEB00, init_va, "menu 11 init")
    exe.patch_u32(MENU_UPDATE + 4 * QUESTS_ID, 0x6FEB0F, update_va, "menu 11 update")


def apply(ctx):
    offsets = sorted(Q.values())
    assert all(192 <= o and o + 1 <= 255 for o in offsets) and len(set(offsets)) == len(offsets)
    for g in GIVERS:
        for q in g["quests"]:
            if q["kind"] == "kill":
                assert Q[q["id"]] + 1 not in Q.values(), q["id"]   # counter byte is free
        field = g["field"]
        pos = _spot(ctx, field, *g["at"])
        model = copy_model(ctx, field, *g["model"])
        add_npc(ctx, field, g["name"], model, pos, g["dir"], _talk(g))
        _add_marker(ctx, g, pos)
    _kill_hook(ctx)
    _quest_menu(ctx)

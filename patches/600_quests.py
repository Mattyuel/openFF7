"""Quests: new NPCs ("givers") offer quests; talking to them again once the
requirement is met completes the quest and gives the reward. A floating
materia orb over a giver marks it: yellow = a quest to offer, blue = one ready
to hand in, hidden otherwise. Givers turn to face the player when talked to.
The quests themselves are data: `_quest_data.py`.

Kinds:
  kill    defeat enemies: one or more targets (label, enemy ids, count),
          each with its own counter.
  deliver bring items (label, item id, count); they are taken on hand-in.

Each giver's quests run in order: the next is offered once the previous is
done (that's how the Manager's No.5 job is gated behind the No.1 job).

Save data (see CLAUDE.md, bank 3 offsets 192-255 are free): per quest a state
byte (0 new, 2 accepted, 4 done) followed by one counter byte per kill target,
allocated in GIVERS order (`_allocate`).

Kill counting is an exe hook: the victory reward loop (0x431481) walks the
formation's six enemy slots; for each one that died it reaches 0x431536
(`mov eax,[ebp-4]; add eax,4`, 6 bytes), which is replaced with a jump to
`q_kill` in patches/asm/quest_menu.asm. It looks the enemy id up in the kill
table (built here, pointed to from the menu data block) and bumps the counter
of an accepted quest's target below its count.

The Quests main-menu screen is in the same asm file (see `_quest_menu`).
"""
import os
import struct

from _recruit import SOUND_ITEM, SOUND_MATERIA, say, sound, xyzi
from _config import OPEN_VAR_BANK8, QUEST_AREAS
from _travel import CHOCOBO_YELLOW, add_line, add_npc, choice_menu, copy_model, line_across

from ff7 import asm
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

from _quest_data import GIVERS, ITEMS, MATERIA, SOURCES, source_count

BANK_OF = {1: 1, 3: 2, 11: 3, 13: 4, 7: 5}   # 8-bit field var nibble -> bank
NIBBLE_OF = {b: n for n, b in BANK_OF.items()}
# Boss "fought this visit" bits: bank 3 offsets 99-101 (openFF7 area), one
# bit per boss, cleared when its field is entered.
BOSS_FOUGHT_FIRST, BOSS_FOUGHT_BYTES = 99, 3
NEW, ACCEPTED, DONE = 0, 2, 4
ITEM_COUNT = (5, 232)          # temp var: CKITM result
MODE, SHOWN = (5, 233), (5, 234)   # temp vars: marker mode wanted / applied

ORB_MODEL = ("nmkin_5", 3)     # fieldbg_mtra3: the materia orb
ORB_HEIGHT = 160               # above the giver's feet (200 was too high in game)
ORB_TINT = {1: (120, 100, -120),   # yellow: quest to offer
            2: (-80, -20, 140)}    # blue: ready to hand in

HOOK_VA, HOOK_OLD = 0x431536, bytes.fromhex("8b45fc83c004")

GIL_TEXT = "%d gil"


def parts(q):
    """[(label, source, count)]: enemy id lists for kill quests, item ids for
    deliveries."""
    if q["kind"] == "kill":
        return q.get("targets") or [(q["label"], q["enemies"], q["count"])]
    return q.get("items") or [(q["label"], q["item"], q["count"])]


def _save_bytes():
    """Quest save bytes as var indices ((bank-1)*256 + offset), in order."""
    for nibble, first, last in QUEST_AREAS:
        for off in range(first, last + 1):
            yield (BANK_OF[nibble] - 1) * 256 + off


def _allocate():
    """Q[id] = state var; CTR[id] = [counter var per kill target]. Handed out
    in GIVERS order from QUEST_AREAS (the first quests keep the bytes they
    shipped with: manager_n1 bank 3 192/193, betty 196/197, gwen 198)."""
    q_off, ctr, free = {}, {}, _save_bytes()
    try:
        for g in GIVERS:
            for q in g["quests"]:
                assert q["id"] not in q_off, q["id"]
                assert 1 <= len(parts(q)) <= 4, q["id"]
                q_off[q["id"]] = next(free)
                if q["kind"] == "kill":
                    ctr[q["id"]] = [next(free) for _ in parts(q)]
    except StopIteration:
        raise AssertionError("quest save bytes exhausted: add an area to _config.QUEST_AREAS")
    b3 = 2 * 256
    assert (q_off["manager_n1"], q_off["betty"], q_off["gwen"]) == (b3 + 192, b3 + 196, b3 + 198)
    return q_off, ctr


def var(index):
    """Field var (nibble, offset) for a var index."""
    return NIBBLE_OF[index // 256 + 1], index % 256


Q, CTR = _allocate()


_NOT = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}


def jump_if(a, cmp, b, target):
    """if (a cmp b) goto target."""
    return asm.if_byte(a, _NOT[cmp], b, target)


def state(q):
    return var(Q[q["id"]])


def counters(q):
    return [var(c) for c in CTR.get(q["id"], [])]


QUEST_INDEX = {q["id"]: i for i, q in enumerate(q for g in GIVERS for q in g["quests"])}


def sources(giver, q):
    """(item, count): every quest also gives Sources, by area level."""
    return SOURCES[QUEST_INDEX[q["id"]] % len(SOURCES)], source_count(q.get("level", giver["level"]))


def _not_met(q, target):
    """Ops: goto target unless every target/item of the quest is complete."""
    ops = []
    if q["kind"] == "kill":
        for ctr, (_, _, count) in zip(counters(q), parts(q)):
            ops.append(jump_if(ctr, "<", count, target))
        return ops
    for _, item, count in parts(q):
        ops += [Op(bytes([0x5A, ITEM_COUNT[0]]) + struct.pack("<H", item) + bytes([ITEM_COUNT[1]])),  # CKITM
                jump_if(ITEM_COUNT, "<", count, target)]
    return ops


def _reward(sec, giver, q):
    r = dict(q["reward"])
    r["items"] = list(r.get("items", [])) + [sources(giver, q)]
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
    chime = SOUND_MATERIA if r.get("materia") else SOUND_ITEM
    return ops + [sound(chime)] + say(sec, "Received " + ",\n".join(got) + "!")


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
            accept = [asm.setbyte(state(q), ACCEPTED)] + [asm.setbyte(c, 0) for c in counters(q)]
            accept += say(sec, q["accept"])
            ops += choice_menu(sec, q["ask"], q["choices"], [accept, say(sec, q["decline"])])
            ops += [active] + _not_met(q, progress)
            if q["kind"] == "deliver":
                ops += [Op(bytes([0x59, 0]) + struct.pack("<H", item) + bytes([count]))  # DLITM
                        for _, item, count in parts(q)]
            for page in q["done"]:
                ops += say(sec, page)
            ops += _reward(sec, giver, q) + [asm.setbyte(state(q), DONE)] + end
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


# ---- Quests main-menu entry ------------------------------------------------
# A 12th main-menu row "Quests" above Quit, opening menu id 11 (an empty stub
# in the original: init 0x6FEB00 / update 0x6FEB0F). Row 10's row->id byte
# (0x91AAF8) is already 0x0B and the title/cursor-return code uses id-1 = row,
# so only counts, heights, masks, labels and the confirm jump table change.
# The screen itself is patches/asm/quest_menu.asm (prebuilt .bin committed).
SECTION_VA = 0xFD5000
MENU_DATA_VA, MENU_CODE_VA = 0xFD5000, 0xFDD000   # = DATA / CODE in quest_menu.asm
MENU_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asm", "quest_menu.bin")
QUESTS_ID = 11
LABELS, ROW_TO_ID = 0x91A8C0, 0x91AAF8
MENU_INIT, MENU_UPDATE = 0x91AB40, 0x91AB98
CONFIRM_TABLE, ROW_SUBMENU, ROW_QUIT = 0x6CB53E, 0x6CA52F, 0x6CA584
REC_SIZE, PART_SIZE = 60, 8
KILL_ENTRY = 10                 # CODE+10: jmp to the kill hook in quest_menu.asm

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


def _kill_table():
    """{u16 enemy id, u16 state var, u16 counter var, u8 count, pad}..., 0xFFFF."""
    rows = b""
    for g in GIVERS:
        for q in g["quests"]:
            if q["kind"] == "kill":
                for ctr, (_, enemies, count) in zip(CTR[q["id"]], parts(q)):
                    assert count < 256
                    rows += b"".join(struct.pack("<HHHBx", e, Q[q["id"]], ctr, count)
                                     for e in enemies)
    return rows + b"\xff\xff"


def _quest_log_data(base):
    """DATA block for quest_menu.asm (layout documented there)."""
    quests = [(g, q) for g in GIVERS for q in g["quests"]]
    head = 16 + REC_SIZE * len(quests)
    pool = bytearray()

    def blob(raw, align=1):
        while len(pool) % align:
            pool.append(0)
        va = base + head + len(pool)
        pool.extend(raw)
        return va

    def text(t):
        return blob(encode(t))
    none, ready = text("No quests in progress."), text("Done! Report back to the quest giver.")
    kills = blob(_kill_table(), align=4)
    recs = b""
    for g, q in quests:
        assert len(q["desc"]) == 3 and all(len(l) <= 46 for l in q["desc"]), q["id"]
        ptrs = [text(q["title"]), text("From: " + g["who"]), text("Where: " + g["where"])]
        ptrs += [text(line) for line in q["desc"]]
        rec = struct.pack("<HBx6I", Q[q["id"]], len(parts(q)), *ptrs)
        for i, (label, src, count) in enumerate(parts(q)):
            src = CTR[q["id"]][i] if q["kind"] == "kill" else src
            rec += struct.pack("<IHBB", text(label), src, count, 0 if q["kind"] == "kill" else 1)
        recs += rec.ljust(REC_SIZE, b"\0")
    assert len(recs) == REC_SIZE * len(quests)
    return struct.pack("<4I", len(quests), none, ready, kills) + recs + bytes(pool)


def _quest_menu(ctx):
    exe = ctx.exe()
    assert exe.section_va == SECTION_VA, hex(exe.section_va)
    data = _quest_log_data(MENU_DATA_VA)
    assert len(data) <= MENU_CODE_VA - MENU_DATA_VA, len(data)
    exe.place_at(MENU_DATA_VA, data, "quest_log_data")
    code = open(MENU_BIN, "rb").read()
    exe.place_at(MENU_CODE_VA, code, "quest_menu")
    init_va, update_va = MENU_CODE_VA, MENU_CODE_VA + 5      # jmp near stubs at the start
    assert code[0] == code[5] == code[KILL_ENTRY] == 0xE9
    hook = b"\xe9" + struct.pack("<i", MENU_CODE_VA + KILL_ENTRY - (HOOK_VA + 5)) + b"\x90"
    exe.patch(HOOK_VA, HOOK_OLD, hook, "reward loop -> quest kill counter")

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


def _add_companion(ctx, giver):
    c = giver["companion"]
    field = giver["field"]
    model = copy_model(ctx, field, *c["model"])
    main = [Op(b) for b in CHOCOBO_YELLOW] if c.get("chocobo") else []

    def talk(sec):
        return [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02")] + say(sec, c["talk"]) + [Op(b"\x33\x00"), asm.ret()]
    add_npc(ctx, field, c["name"], model, _spot(ctx, field, *c["at"]), giver["dir"], talk, main=main)


def _add_boss(ctx, q, slot):
    """Repeatable boss fight (like the Guard Scorpion line): crossing the
    quest's boss line fights its formation once per visit, from when the
    quest is accepted on (also after it's done; always, with always=True). The "fought" bit is set by
    the fight and cleared when the field is entered."""
    b = q["boss"]
    assert slot < 8 * BOSS_FOUGHT_BYTES, "more bosses than BOSS_FOUGHT bits"
    fought = (OPEN_VAR_BANK8, BOSS_FOUGHT_FIRST + slot // 8)
    bit = slot % 8

    def fight(sec):
        done = asm.ret()
        gate = [] if b.get("always") else [jump_if(state(q), "<", ACCEPTED, done)]  # not accepted yet
        return gate + [
                asm.if_byte(fought, "bit_off", bit, done),       # skip if fought this visit
                asm.biton(fought, bit),
                asm.battle(b["formation"]),
                done]
    line = b.get("line") or line_across(ctx, b["field"], *b["at"])
    add_line(ctx, b["field"], "boss%02d" % slot, *line, fight,
             init_extra=[asm.bitoff(fought, bit)])


def apply(ctx):
    for slot, q in enumerate(q for g in GIVERS for q in g["quests"] if "boss" in q):
        _add_boss(ctx, q, slot)
    for g in GIVERS:
        field = g["field"]
        assert len(g["name"]) <= 8, g["name"]
        pos = _spot(ctx, field, *g["at"])
        model = copy_model(ctx, field, *g["model"])
        add_npc(ctx, field, g["name"], model, pos, g["dir"], _talk(g))
        _add_marker(ctx, g, pos)
        if "companion" in g:
            _add_companion(ctx, g)
    _quest_menu(ctx)

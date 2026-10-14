"""Debug tools (built only by `ff7tool.py build --debug`; a normal build never
reads this folder). Self-contained: one model-less entity `dbgmenu` appended
to every field, one saved flag byte, one world map hook.

In any field, hold L1 + R1: the DEBUG menu opens.
  Travel: Midgar / World 1 / World 2 pages of towns (arrival = a gateway
          into that field from a neighbouring one).
  Gil +100,000.
  Encounters off / on: DEBUG_FLAGS bit 0. Fields: the entity's loop keeps
          BTLON 01 (the field's 'no random battles' flag, field header +0x3B,
          reset on every field load) while it's set. World map: the encounter
          roll's call (0x76760B -> 0x767641, returns a formation or -1) goes
          through a stub returning -1 while the bit is set.
  Honey Bee / Hunter: job + all 20 girls hired, every girl's affection set
          to 0 / 10 / 20, all 12 gifts, Hunter points +50, movie star rank +1
          (unlocks Skye), time +30 min (the movie cut / Honey Bee takings
          wait 30 minutes less).

Fields left out: text tables within 5 of the 255 limit, 48+ entities (the
most any original field has), scripts the parser rejects.
"""
import csv
import os
import struct

from _config import HB_AFFECTION, HB_HIRED, HB_KID, HB_JOB, HB_LAST, HB_VISIT, HUNTER_PTS, MOVIE_AT, MOVIE_GIRL
from _recruit import sound
from _travel import CHOICE, window
import _honey_bee_gifts as gifts

from ff7 import asm, triggers
from ff7.script import Op, Script
from ff7.text import encode
from ff7.walkmesh import Walkmesh

DEBUG_FLAGS = (1, 213)                  # bit 0: random encounters off; bit 1: 626's rescue scene always (bank 1 213-223 free, see CLAUDE.md)
FLAGS_VA = 0xDC08DC + DEBUG_FLAGS[1]    # field var bank 1 base in memory
WM_ROLL_CALL, WM_ROLL = 0x76760B, 0x767641
L1, R1 = 0x0004, 0x0008
TEXTS_NEEDED, MAX_ENTITIES = 5, 48

PAGES = [
    ("Midgar", [("Sector 7 Station", "mds7st3"), ("7th Heaven", "mds7pb_1"), ("Sector 6 Park", "mds6_1"),
                ("Wall Market", "mrkt2"), ("Honey Bee Inn", "onna_4"), ("Upper Midgar", "md8_3"),
                ("Shinra HQ 66F", "blin66_1")]),
    ("World 1", [("Kalm", "elm"), ("Chocobo Ranch", "frcyo"), ("Fort Condor", "condor1"),
                 ("Upper Junon", "junonr1"), ("Costa del Sol", "del2"), ("Corel ropeway", "ropest"),
                 ("Gold Saucer", "games"), ("Gongaga", "gongaga")]),
    ("World 2", [("Cosmo Canyon", "cos_btm"), ("Nibelheim", "nivl_3"), ("Shinra Mansion", "sinin1_1"),
                 ("Rocket Town", "rckt"), ("Wutai", "uutai1"), ("Temple of Ancients", "jtempl"),
                 ("Icicle Inn", "snow"), ("Mideel", "itown1a")]),
]


# Arrivals picked by hand where the first link found was poor (user): Gold Saucer
# = where the entrance gate (gldgate) drops you; Nibelheim = the present-day town
# (nivl_3; nivl is the flashback copy, where the player was invisible beside a
# scene Cloud), in front of the inn as its exit leaves you.
ARRIVE_AT = {"games": (191, -1053, 99, 112), "nivl_3": (-98, -347, 17, 60)}


def _arrival(ctx, target, links):
    """(x, y, tri, dir) of a gateway into `target` from a field that links to it."""
    mesh = Walkmesh(ctx.field(target).section("walkmesh"))
    if target in ARRIVE_AT:
        x, y, tri, d = ARRIVE_AT[target]
        assert mesh.contains(tri, x, y), target
        return x, y, tri, d
    tid = ctx.maplist.index(target)
    for src in links.get(target, []):
        if src not in ctx.flevel:
            continue
        for g in triggers.gateways(ctx.field(src).section("triggers")):
            if g["field"] == tid and mesh.contains(g["dest_triangle"], g["dest_x"], g["dest_y"]):
                return g["dest_x"], g["dest_y"], g["dest_triangle"], g["dir"]
    for src in links.get(target, []) + links.get("@" + target, []):     # entered by a script MAPJUMP
        if src not in ctx.flevel:
            continue
        try:
            sec = Script.parse(ctx.field(src).sections[0])
        except ValueError:
            continue
        for o in sec.ops:
            if o.op == 0x60:
                fid, x, y, tri, d = struct.unpack_from("<HhhHB", bytes(o.raw), 1)
                if fid == tid and mesh.contains(tri, x, y):
                    return x, y, tri, d
    raise AssertionError("no arrival into " + target)


def _links():
    out = {}
    path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "inventory", "field_links.csv")
    with open(path) as fh:
        for row in csv.DictReader(fh):
            key = row["to"] if row["kind"] == "gateway" else "@" + row["to"]
            out.setdefault(key, []).append(row["from"])
    return out


def _ask(sec, prompt, options):
    text = prompt + "".join("\n{CHOICE}" + o for o in options)
    tid = sec.add_string(encode(text))
    return [window(text), asm.setbyte(CHOICE, 0xFF), asm.ask(0, tid, 1, len(options), CHOICE)]


def _menu(sec, dests):
    """The loop: L1+R1 held -> menus; encounter flag kept applied."""
    top, idle, close, main = asm.nop(), asm.nop(), asm.nop(), asm.nop()
    ops = [top]
    keep = asm.nop()
    ops += [asm.if_byte(DEBUG_FLAGS, "bit_on", 0, keep), asm.battles_enabled(False), keep]
    near, opened = asm.nop(), asm.nop()                 # IFKEY's jump is one byte: hop via a goto
    ops += [Op(bytes([0x30, L1, 0, 0]), target=near), Op(bytes([0x30, R1, 0, 0]), target=near),
            asm.goto(opened), near, asm.goto(idle), opened, Op(b"\x33\x01"), main]
    ops += _ask(sec, "DEBUG", ["Travel: " + p[0] for p in PAGES] +
                ["Gil +100,000", "Encounters OFF", "Encounters ON", "Honey Bee / Hunter", "Close"])
    acts = [asm.nop() for _ in range(len(PAGES) + 4)]
    for k, label in enumerate(acts):
        ops += [asm.if_byte(CHOICE, "!=", 1 + k, label)]
    ops += [asm.goto(close)]
    done = asm.nop()                                     # after an action: chime, back to the menu
    # travel pages
    for (title, places), label in zip(PAGES, acts):
        ops += [label] + _ask(sec, "Travel: " + title, [p[0] for p in places] + ["Back"])
        for k, (_, field) in enumerate(places):
            nxt = asm.nop()
            x, y, tri, d = dests[field]
            ops += [asm.if_byte(CHOICE, "==", 1 + k, nxt), asm.setbyte(HB_VISIT, 0), Op(b"\x33\x00"),
                    asm.mapjump(dests["_ids"][field], x, y, tri, d), asm.ret(), nxt]
        ops += [asm.goto_back(main)]
    gil, off, on, hb = acts[len(PAGES):]
    ops += [gil, Op(bytes([0x39, 0x00]) + struct.pack("<I", 100000)), asm.goto(done)]
    ops += [off, asm.biton(DEBUG_FLAGS, 0), asm.battles_enabled(False), asm.goto(done)]
    ops += [on, asm.bitoff(DEBUG_FLAGS, 0), asm.battles_enabled(True), asm.goto(done)]
    ops += [hb] + _ask(sec, "Honey Bee / Hunter", ["Job + hire all 20 girls", "All affection 0",
                                                   "All affection 10", "All affection 20", "All 12 gifts",
                                                   "All 20 kids", "Hunter points +50", "Star rank +1",
                                                   "Time +30 min", "Rescue scene: always", "Back"])
    hb_acts = [asm.nop() for _ in range(10)]
    for k, label in enumerate(hb_acts):
        ops += [asm.if_byte(CHOICE, "!=", 1 + k, label)]
    ops += [asm.goto_back(main)]
    hire, a0, a10, a20, allg, kids, hunt, star, later, rescue = hb_acts
    hv = HB_HIRED
    ops += [hire, asm.biton(*HB_JOB), asm.setbyte(hv, 0xFF), asm.setbyte((hv[0], hv[1] + 1), 0xFF),
            asm.setbyte((hv[0], hv[1] + 2), 0x0F), asm.goto(done)]
    for label, value in ((a0, 0), (a10, gifts.CLOSE), (a20, gifts.DEVOTED)):
        ops += [label] + [asm.setbyte(v, value) for v in HB_AFFECTION] + [asm.goto(done)]
    ops.append(allg)
    for j in range(len(gifts.GIFTS)):
        k = gifts.FIRST_KEY_ITEM + j
        ops.append(asm.biton((1, 64 + k // 8), k % 8))
    ops += [asm.goto(done)]
    ops += [kids] + [asm.biton(*k) for k in HB_KID] + [asm.goto(done)]
    ops += [hunt, Op(bytes([0x86, HUNTER_PTS[0] << 4, HUNTER_PTS[1]]) + struct.pack("<H", 50)), asm.goto(done)]
    # the movie's star rank (670: a girl retires -> the next co-star): rank 1 = Skye
    ops += [star, asm.biton(MOVIE_GIRL, 0), asm.goto(done)]
    # +30 minutes: the play clock can't be reached from a field, so the times waited from move back
    # 30 (wrapping: the elapsed difference still comes out +30): the movie cut and the Honey Bee takings
    ops += [later] + [Op(bytes([0x88, v[0] << 4, v[1]]) + struct.pack("<H", 30)) for v in (MOVIE_AT, HB_LAST)]
    ops += [asm.goto(done)]
    # 626's Wall Market rescue scene on every entry to mrkt3 (DEBUG_FLAGS bit 1)
    ops += [rescue, asm.biton(DEBUG_FLAGS, 1), asm.goto(done)]
    ops += [done, sound(0x168), asm.goto_back(main)]
    # close: control back, wait for the buttons to be let go
    release = asm.nop()
    ops += [close, Op(b"\x33\x00"), release,
            Op(bytes([0x30, L1 | R1, 0, 0]), target=idle), Op(b"\x24\x01\x00"), asm.goto_back(release)]
    ops += [idle, Op(b"\x24\x01\x00"), asm.goto_back(top)]
    return ops


def _wm_hook(ctx):
    exe = ctx.exe()
    stub_va = exe.cursor + (-exe.cursor % 4)
    stub = (bytes([0xF6, 0x05]) + struct.pack("<I", FLAGS_VA) + b"\x01"   # test byte [flags], 1
            + b"\x74\x06"                                                 # jz roll
            + b"\xB8\xFF\xFF\xFF\xFF\xC3")                               # mov eax, -1; ret
    stub += b"\xE9" + struct.pack("<i", WM_ROLL - (stub_va + len(stub) + 5))   # roll: jmp 0x767641
    assert exe.alloc(stub, "debug_wm_roll") == stub_va
    rel = lambda dst: struct.pack("<i", dst - (WM_ROLL_CALL + 5))
    exe.patch(WM_ROLL_CALL, b"\xE8" + rel(WM_ROLL), b"\xE8" + rel(stub_va), "debug: world map encounter roll")


def apply(ctx):
    links = _links()
    dests = {"_ids": {}}
    for _, places in PAGES:
        for _, field in places:
            dests[field] = _arrival(ctx, field, links)
            dests["_ids"][field] = ctx.maplist.index(field)
    added, skipped = 0, []
    names = [n for n in ctx.maplist if n in ctx.flevel or n in ctx._fields]
    for name in names:
        f = ctx.field(name)
        try:
            sec = Script.parse(f.sections[0])
        except ValueError:
            skipped.append(name)
            continue
        n_text = struct.unpack_from("<H", sec.tail, 0)[0]
        if n_text > 255 - TEXTS_NEEDED or len(sec.entry) >= MAX_ENTITIES:
            skipped.append(name)
            continue
        sec.add_entity("dbgmenu", {0: [asm.ret()] + _menu(sec, dests)})
        try:
            data = sec.build()
        except (ValueError, struct.error):
            skipped.append(name)
            continue
        f.sections[0] = data
        added += 1
    _wm_hook(ctx)
    print("  debug menu in %d fields (%d left out: %s ...)" % (added, len(skipped), " ".join(skipped)))

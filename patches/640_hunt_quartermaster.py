"""The Hunt Quartermaster (Reeve's model): sells rare equipment for gil, each
tier unlocked by the Hunter rank (630_bounties: HUNTER_PTS / RANKS). Secretive
about where the goods come from; no questions.

Found at the Sector 7 station (lower platform, right), Upper Junon's first
street (by the shops), the North Corel ropeway station (by the gondola) and
Rocket Town by Cid's house (both versions of the town: the world map enters
either).

Talk: a tier menu (all tiers listed; one above your rank = "not for you"),
then that tier's page: item + price; buying checks the gil (CHGLD, a 32-bit
compare), takes it (GOLDD), gives the item (STITM: the 0-319 inventory index,
weapons 128+, armor 256+, accessories 288+) and goes back to the tier menu.
"""
import importlib
import struct

from _config import HUNTER_PTS
from _recruit import SOUND_ITEM, say, sound
from _travel import CHOICE, add_npc, copy_model, window

from ff7 import asm, fieldanim
from ff7.models import ModelLoader
from ff7.script import Op
from ff7.text import decode, encode
from ff7.walkmesh import Walkmesh

RANKS = importlib.import_module("630_bounties").RANKS
NAME = "Hunt Quartermaster"
MODEL = ("blin66_6", 4)              # sub_leave: Reeve
GIL_LO, GIL_HI = (6, 0xF8), (6, 0xFA)  # temp words for CHGLD (as 280)

SPOTS = [  # field, (x, y), facing (down the screen)
    ("mds7st3", (-2000, 2700), 10),          # Sector 7 station: lower platform, right
    ("junonr1", (-400, -100), 216),          # Upper Junon: between the item and materia shops
    ("ropest", (328, -36), 20),              # North Corel ropeway: the gondola platform (4 right, 2 up: user)
    ("rckt", (200, 1100), 0),                # Rocket Town: in front of Cid's house
    ("rckt2", (200, 1100), 0),
]
# His size in each map: HEIGHT x Cloud's height there (model skeleton height in its
# first animation x the loader entry's scale). Hand factors per map were off (user:
# Sector 7 too big at 1.39 x Cloud, Junon too small at 0.81, Rocket Town 0.97; the
# ropeway's 1.04 looked right).
HEIGHT = 1.05

# (page title, rank needed, [(item index, name as the game spells it, gil)])
PAGES = [
    ("Tracker goods", "Tracker", [
        (261, "Silver Armlet", 4000), (258, "Titan Bangle", 4000), (288, "Power Wrist", 5000),
        (291, "Talisman", 5000), (290, "Earring", 5000), (298, "Star Pendant", 6000),
        (300, "Headband", 6000), (299, "Silver Glasses", 6000)]),
    ("Hunter goods", "Hunter", [
        (263, "Diamond Bangle", 12000), (301, "Fairy Ring", 12000), (302, "Jem Ring", 15000),
        (303, "White Cape", 15000), (312, "Fury Ring", 18000), (305, "Peace Ring", 18000)]),
    ("Hunter rarities", "Hunter", [
        (260, "Carbon Bangle", 15000), (275, "Shinra Beta", 15000), (130, "Hardedge", 18000),
        (147, "Grand Glove", 20000), (163, "Atomic Scissors", 20000), (177, "Diamond Pin", 20000),
        (193, "Striking Staff", 22000)]),
    ("More rarities", "Hunter", [
        (216, "Boomerang", 22000), (265, "Platinum Bangle", 25000), (262, "Gold Armlet", 28000),
        (269, "Adaman Bangle", 30000), (317, "Water Ring", 30000), (297, "Circlet", 35000)]),
    ("Veteran goods", "Veteran", [
        (276, "Shinra Alpha", 45000), (268, "Wizard Bracelet", 55000), (270, "Gigas Armlet", 55000),
        (296, "Tough Ring", 60000), (314, "Protect Ring", 65000), (285, "Ziedrich", 75000)]),
    ("Elite goods", "Elite", [
        (168, "W Machine Gun", 80000), (274, "Warrior Bangle", 85000), (281, "Dragon Armlet", 90000),
        (282, "Minerva Band", 95000), (316, "Reflect Ring", 110000)]),
    ("Master goods", "Master", [
        (278, "Fire Armlet", 120000), (279, "Aurora Armlet", 120000), (280, "Bolt Armlet", 120000),
        (313, "Curse Ring", 140000)]),
    ("Legend goods", "Legend", [
        (226, "Rising Sun", 200000)]),
]


def _rank_points(rank):
    return dict(RANKS)[rank]


def _check_names(ctx):
    """Every item index must be the item the page names (kernel2 sections 10-13)."""
    k2 = ctx.kernel2()
    for _, _, items in PAGES:
        for idx, name, _ in items:
            sec, i = ((10, idx) if idx < 128 else (11, idx - 128) if idx < 256
                      else (12, idx - 256) if idx < 288 else (13, idx - 288))
            got = decode(k2.get(sec, i)).strip()
            assert got == name, (idx, name, got)


def _menu(sec, prompt, options):
    """(ops, first): WINDOW + ASK; CHOICE = first + the option picked."""
    text = prompt + "".join("\n{CHOICE}" + o for o in options)
    first = len(prompt.split("\n"))
    tid = sec.add_string(encode(text))
    return [window(text), asm.ask(0, tid, first, first + len(options) - 1, CHOICE)], first


def _gil(n):
    return "{:,}".format(n)


def _build_talk(sec):
    """The whole talk script (tier menu, a locked-tier answer, the pages)."""
    end = [Op(b"\x33\x00"), asm.ret()]
    ops = [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]     # UC 01, face Cloud
    rookie = asm.nop()
    ops += [asm.if_word(HUNTER_PTS, ">=", _rank_points("Tracker"), rookie)]
    ops += say(sec, NAME + "\n“Hunters only. Come back when people\n know your name.”") + end
    ops += [rookie]
    ops += say(sec, NAME + "\n“Rare gear. Where it came from is my\n business. No questions, no refunds.”")
    top, locked = asm.nop(), asm.nop()
    ops.append(top)
    menu, first = _menu(sec, NAME + "\n“What'll it be?”", [p[0] for p in PAGES] + ["Nothing."])
    ops += menu
    page_labels = []
    for k, (title, rank, items) in enumerate(PAGES):
        nxt, page = asm.nop(), asm.nop()
        ops += [asm.if_byte(CHOICE, "==", first + k, nxt),
                asm.if_word(HUNTER_PTS, ">=", _rank_points(rank), locked),
                asm.goto(page), nxt]
        page_labels.append(page)
    ops += end
    ops += [locked] + say(sec, NAME + "\n“That's not for your rank. Hunt more.”") + [asm.goto_back(top)]
    bought, short = asm.nop(), asm.nop()                 # shared answers (before the pages: jumps back)
    ops += [bought] + say(sec, NAME + "\n“Pleasure. And you didn't get it\n from me.”") + [asm.goto_back(top)]
    ops += [short] + say(sec, NAME + "\n“You're short. I don't do credit.”") + [asm.goto_back(top)]
    for page, (title, rank, items) in zip(page_labels, PAGES):
        ops.append(page)
        menu, pfirst = _menu(sec, NAME + "  -  " + title,
                             ["%s  %s gil" % (name, _gil(price)) for _, name, price in items] + ["Back."])
        ops += menu
        for j, (idx, name, price) in enumerate(items):
            nxt, ok, lshort = asm.nop(), asm.nop(), asm.nop()   # IFs jump forward only: lshort hops back
            hi, lo = price >> 16, price & 0xFFFF
            ops += [asm.if_byte(CHOICE, "==", pfirst + j, nxt),
                    Op(bytes([0x3B, 0x66, GIL_LO[1], GIL_HI[1]])),                  # CHGLD lo, hi
                    asm.if_word(GIL_HI, "<=", hi, ok),                               # more than hi:16 -> ok
                    asm.if_word(GIL_HI, "==", hi, lshort),                           # less -> short
                    asm.if_word(GIL_LO, ">=", lo, lshort),
                    ok,
                    Op(bytes([0x3A, 0x00]) + struct.pack("<I", price)),             # GOLDD
                    asm.add_item(idx, 1), sound(SOUND_ITEM), asm.goto_back(bought),
                    lshort, asm.goto_back(short), nxt]
        ops += [asm.goto_back(top)]
    return ops


def apply(ctx):
    _check_names(ctx)
    for field, (x, y), facing in SPOTS:
        mesh = Walkmesh(ctx.field(field).section("walkmesh"))
        tri = mesh.find(x, y)
        assert tri is not None, (field, x, y)
        model = copy_model(ctx, field, *MODEL)
        loader = ModelLoader(ctx.field(field).section("models"))
        cloud, entry = loader.models[0], loader.models[model]
        assert loader.name(cloud).endswith("main_n_cloud.char"), loader.name(cloud)
        tall = lambda e: fieldanim.height(ctx.char_file(loader.hrc(e).lower()).decode("latin-1"),
                                          ctx.char_file(loader.anims(e)[0].split(".")[0].lower() + ".a"))
        scale = round(HEIGHT * tall(cloud) * loader.entry_scale(cloud) / tall(entry))
        loader.models[model] = loader.with_scale(entry, scale)
        ctx.field(field).set_section("models", loader.build())
        add_npc(ctx, field, "hunterqm", model, (x, y, mesh.height(tri, x, y), tri), facing, _build_talk)

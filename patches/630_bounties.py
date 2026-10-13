"""Bounties: Scoop, a roving reporter, sits in a bar in each of 8 regions and
pays for "stories": hunt N of one of the region's rarer enemies within a time
limit, then come back to Scoop (in that region's bar) to collect.

- One bounty per region at a time. Talking to Scoop: nothing running = the
  same spiel with the region's current offer (picked at random from its pool,
  not the one just claimed), accept to start; running = a reminder; enough
  kills = the gil. Past the time limit the bounty is simply dropped and Scoop
  offers a new one.
- Nothing is saved: the state lives in the exe's .openff7 section
  (quest_menu.asm, b_state) and is cleared when a game is loaded or started
  (the play clock jumps). Field scripts reach it through field opcode 0x1C
  BOUNTY (unused in the game; its table entry 0x9055A0 + 0x1C*4 is pointed at
  quest_menu.asm's handler): 1C [dst bank << 4][dst][cmd][region].
- The Quests screen lists the active bounties first, as "(Bounty) <enemy>"
  with the kill count and the time left; kills are counted by the battle kill
  hook like quest kills.
- Pools: each region's rarest random-battle enemies (world map enc_w.bin
  region tables + the region's dungeon fields, ranked by their share of the
  encounter tables; see the comments in REGIONS).
"""
import struct

from _recruit import SOUND_ITEM, say, sound
from _travel import add_npc, choice_menu, copy_model

from ff7 import asm
from ff7.script import Op
from ff7.text import encode
from ff7.walkmesh import Walkmesh

BDATA = 0xFE0000                     # = BDATA in quest_menu.asm
CODE = 0xFDD000
BOUNTY_ENTRY = 35                    # CODE+35: jmp b_op
OPCODE = 0x1C
OP_TABLE = 0x9055A0
UNUSED_HANDLER = 0x6107E1            # opcodes 0C 0D 1A-1F 44 46 4C 4E BE: return 1
BENT = 32
MODEL = ("junbin4", 8)               # junon_report1: a Junon parade reporter
NAME = "Scoop"
STATUS, OFFER, ACCEPT, CLAIM, ACTIVE = range(5)
RESULT, INDEX = (5, 237), (5, 238)   # temp vars (talk script only)
MINUTES = 30
GIL_PER_LEVEL = 75                   # reward = kills * level * this, rounded to 50

# region: bar field, Scoop's spot, facing, bar name (quest list), where the
# hunting is (spiel), pool [(enemy, ids, level, kills, found at)]
REGIONS = [
    dict(key="midgar", field="mds7pb_1", at=(-115, 148), dir=32, bar="7th Heaven, Sector 7 Slums",
         area="Midgar", pool=[
             ("Cripshay", [42], 8, 2, "the Train Graveyard"),
             ("Eligor", [40], 12, 2, "the Train Graveyard"),
             ("Ghost", [41], 10, 2, "the Train Graveyard"),
             ("Hell House", [44, 45], 11, 2, "Sector 6"),
             ("Vice", [34], 7, 2, "the Sector 5 slums"),
             ("Sword Dance", [55], 11, 2, "the Shinra Building"),
         ]),
    dict(key="kalm", field="elmpb", at=(267, -58), dir=220, bar="Kalm bar",
         area="the plains past Midgar", pool=[
             ("Mu", [77], 12, 3, "the grasslands"),
             ("Mandragora", [79], 10, 3, "the grasslands"),
             ("Custom Sweeper", [73], 15, 3, "the plains outside Midgar"),
             ("Elfadunk", [76], 14, 3, "the grasslands"),
             ("Devil Ride", [72], 13, 3, "the plains outside Midgar"),
         ]),
    dict(key="junon", field="junpb_3", at=(100, 78), dir=22, bar="Junon bar",
         area="the Junon area", pool=[
             ("Hell Rider VR2", [88], 18, 2, "the Junon coast"),
             ("Scrutin Eye", [93], 15, 3, "the cargo ship"),
             ("Zemzelett", [86], 17, 3, "the Junon coast"),
             ("Formula", [89], 16, 3, "the Junon coast"),
             ("Ark Dragon", [84], 18, 3, "the Mythril Mine"),
             ("Capparwire", [90], 15, 3, "the Junon coast"),
         ]),
    dict(key="costa", field="delpb", at=(127, 346), dir=4, bar="Costa del Sol bar",
         area="the Corel area", pool=[
             ("Beachplug", [99], 16, 3, "the beaches"),
             ("Bloatfloat", [102], 18, 3, "Mt. Corel"),
             ("Bomb", [105], 18, 3, "Mt. Corel"),
             ("Grangalan", [96], 16, 3, "the Corel area"),
             ("Cokatolis", [104], 17, 3, "Mt. Corel"),
         ]),
    dict(key="cosmo", field="cosin3", at=(115, 240), dir=30, bar="Pub Starlet, Cosmo Canyon",
         area="the canyon lands", pool=[
             ("Golem", [131], 24, 2, "the canyon lands"),
             ("Gi Spector", [134], 23, 2, "the Cave of the Gi"),
             ("Gagighandi", [118], 19, 3, "the canyon lands"),
             ("Bagrisk", [132], 19, 3, "the canyon lands"),
             ("Skeeskee", [129], 20, 3, "the canyon lands"),
             ("Griffin", [130], 21, 3, "the canyon lands"),
         ]),
    dict(key="nibel", field="nivinn_1", at=(-14, -340), dir=233, bar="Nibelheim Inn",
         area="the Nibel area", pool=[
             ("Bahba Velamyu", [142], 23, 2, "the Nibel area"),
             ("Screamer", [162], 26, 2, "Mt. Nibel"),
             ("Battery Cap", [144], 24, 2, "the Nibel area"),
             ("Dragon", [157], 32, 2, "Mt. Nibel"),
             ("Nibel Wolf", [140], 23, 2, "the Nibel area"),
             ("Zuu", [160], 27, 2, "Mt. Nibel"),
         ]),
    dict(key="wutai", field="utapb", at=(0, -232), dir=222, bar="Turtle's Paradise, Wutai",
         area="the Wutai area", pool=[
             ("Edgehead", [169], 27, 2, "the Wutai area"),
             ("Thunderbird", [167], 28, 3, "the Wutai area"),
             ("Razor Weed", [168], 27, 3, "Da-chao"),
             ("Adamantaimai", [172], 30, 3, "the Wutai beaches"),
             ("Tail Vault", [171], 28, 3, "the Wutai area"),
         ]),
    dict(key="icicle", field="sninn_b1", at=(169, 479), dir=22, bar="Icicle Inn bar",
         area="the northern snowfields", pool=[
             ("Vlakorados", [197], 33, 2, "the snowfields"),
             ("Trickplay", [198], 24, 2, "the snowfields"),
             ("Hungry", [203], 33, 2, "the Frostbite Cave"),
             ("Jumping", [209], 24, 2, "the snowfields"),
             ("Tonadu", [188], 30, 2, "the snowfields"),
             ("Magnade", [212], 35, 3, "the Great Glacier"),
         ]),
]


def gil(level, kills):
    return round(kills * level * GIL_PER_LEVEL / 50) * 50


def bounty_op(cmd, region, dst=RESULT):
    return Op(bytes([OPCODE, dst[0] << 4, dst[1], cmd, region]))


def _text(s):
    return encode(s) + b"\xFF"


def _data():
    """The BDATA block: header, region table, pools, texts (absolute pointers)."""
    texts = bytearray()
    text_base = BDATA + 12 + 8 * len(REGIONS) + BENT * sum(len(r["pool"]) for r in REGIONS)

    def put(s):
        va = text_base + len(texts)
        texts.extend(_text(s))
        return va

    head = struct.pack("<III", len(REGIONS), put("Time left: "), put(" min"))
    table, pools = bytearray(), bytearray()
    pool_va = BDATA + 12 + 8 * len(REGIONS)
    for r in REGIONS:
        table += struct.pack("<IB3x", pool_va + len(pools), len(r["pool"]))
        for name, ids, level, kills, found in r["pool"]:
            ids = (ids + [0xFFFF])[:2]
            pools += struct.pack("<HHBB2x6I", ids[0], ids[1], kills, MINUTES,
                                 put("(Bounty) " + name), put(NAME + ", roving reporter"),
                                 put("Report back: " + r["bar"]),
                                 put("Hunt %d %s around %s." % (kills, name, found)),
                                 put("Reward: %d gil" % gil(level, kills)), put(name))
    blob = head + table + pools
    assert BDATA + len(blob) == text_base
    return blob + texts


def _talk(i, r):
    def build(sec):
        end = [Op(b"\x33\x00"), asm.ret()]                                   # UC 00
        ops = [Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00"),  # UC 01, face Cloud
               bounty_op(STATUS, i)]
        # status 2 = claim, 1 = reminder, 0 = offer (if_byte jumps when the test fails)
        remind = asm.nop()
        ops += [asm.if_byte(RESULT, "==", 2, remind)]
        # ---- claim
        ops += [bounty_op(CLAIM, i, INDEX)]
        for k, (name, ids, level, kills, found) in enumerate(r["pool"]):
            nxt = asm.nop()
            g = gil(level, kills)
            ops += [asm.if_byte(INDEX, "==", k, nxt)]
            ops += [Op(bytes([0x39, 0]) + struct.pack("<I", g)), sound(SOUND_ITEM)]      # GOLDU
            ops += say(sec, NAME + "\n“%s, down! Front page stuff.\n Here's your %d gil.”" % (name, g))
            ops += end + [nxt]
        ops += end
        # ---- reminder
        offer = asm.nop()
        ops += [remind, asm.if_byte(RESULT, "==", 1, offer), bounty_op(ACTIVE, i, INDEX)]
        for k, (name, ids, level, kills, found) in enumerate(r["pool"]):
            nxt = asm.nop()
            ops += [asm.if_byte(INDEX, "==", k, nxt)]
            ops += say(sec, NAME + "\n“Still waiting on those %s.\n The clock's ticking, friend!”" % name)
            ops += end + [nxt]
        ops += end
        # ---- offer: the same spiel, the region's current bounty
        ops += [offer, bounty_op(OFFER, i, INDEX)]
        ops += say(sec, NAME + "\n“Psst. Scoop, roving reporter.\n I pay for stories. Got one for you.”")
        ask = asm.nop()
        for k, (name, ids, level, kills, found) in enumerate(r["pool"]):
            nxt = asm.nop()
            ops += [asm.if_byte(INDEX, "==", k, nxt)]
            ops += say(sec, NAME + "\n“Word is, %s have been\n seen around %s.”" % (name, found))
            ops += say(sec, NAME + "\n“Bring down %d of them within %d\n minutes, come back here, and the\n story's worth %d gil.”"
                       % (kills, MINUTES, gil(level, kills)))
            ops += [asm.goto(ask), nxt]
        ops += end
        accept = [bounty_op(ACCEPT, i, INDEX)]
        accept += say(sec, NAME + "\n“Clock starts now. Don't make\n me write about your failure.”")
        decline = say(sec, NAME + "\n“Your loss. Somebody else'll\n get the scoop.”")
        return ops + [ask] + choice_menu(sec, NAME + "\n“Deal?”", ["Deal.", "Not now."], [accept, decline])
    return build


def apply(ctx):
    exe = ctx.exe()
    assert exe.cursor <= BDATA, "quest code ran into the bounty data: 0x%X" % exe.cursor
    exe.place_at(BDATA, _data(), "bounty_data")
    stub = exe.payload[CODE + BOUNTY_ENTRY - exe.section_va]
    assert stub == 0xE9, stub                          # jmp b_op in quest_menu.bin
    exe.patch_u32(OP_TABLE + OPCODE * 4, UNUSED_HANDLER, CODE + BOUNTY_ENTRY, "field opcode 1C: BOUNTY")
    for i, r in enumerate(REGIONS):
        f = r["field"]
        mesh = Walkmesh(ctx.field(f).section("walkmesh"))
        x, y = r["at"]
        tri = mesh.find(x, y)
        assert tri is not None, (f, x, y)
        model = copy_model(ctx, f, *MODEL)
        add_npc(ctx, f, "scoop", model, (x, y, mesh.height(tri, x, y), tri), r["dir"], _talk(i, r))

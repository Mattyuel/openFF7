"""Honey Bee kids: after a girl's devoted (affection 20) scene, a child stands
next to her where she is found in the world (Rhonda: outside her inn) (a little joke, never spelled out).

The scene sets `_config.HB_KID[i]` (620, devoted room only); each girl field
gets a kid NPC beside her that hides itself in its init while the bit is off.
Kids are matched to the girl's place (`KIDS`: the swimsuit boy in Costa del
Sol, the boy with the red cap in Rocket Town...). Velvet's coloss is at 16
models: her kid takes over the hidden arena kid `gaki2` (gon_girl), model and all.
"""
import math

from _config import HB_KID
from _honey_bee_data import GIRLS
from _recruit import hide, say
from _travel import add_npc, copy_model, reuse_npc

from ff7 import asm
from ff7.camera import Camera
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

# kid models (donor field, model index), looked at in a render of each
STD_GIRL2 = ("mds7st3", 11)     # white blouse, red skirt
STD_GIRL3 = ("frcyo", 3)        # dark red dress
STD_BOY2 = ("elm", 12)          # red cap, grey T-shirt
STD_BOY3 = ("mrkt1", 8)         # goggles, green overalls
MIDGAL = ("mds7", 9)            # spiky brown hair, blue shorts
FARM_BOY = ("frcyo", 4)         # cowboy hat with a feather
NIBLE_BOY = ("niv_ti3", 6)      # brown hair, blue overalls
NIBLE_GIRL = ("nvmin1_1", 10)   # red pigtails
GON_BOY = ("games", 7)          # as nible_boy
GON_GIRL = ("games", 8)         # as nible_girl
COSMO_GIRL = ("cosmo", 3)       # grey hood
COSMO_BOY = ("cosmin3", 5)      # headband, tribal
KOSTA_RGIRL = ("del2", 9)       # tanned, sun dress (looked like an adult in game: not used)
KOSTA_SBOY = ("del2", 11)       # snorkel and swim trunks
KOSTA_SGIRL = ("del2", 12)      # swimsuit
SNOW = ("snow", 10)             # pink hood
UTAI = ("uutai1", 11)           # orange kimono
# (gold_cgirl in crcin_1 is a grown woman in a swimsuit, not a kid)

NAME = "Kid"
KIDS = {   # girl -> (model, line)
    "Bambi": (STD_GIRL2, "“Mom naps all day. I don't.\n She says I get that from my dad.”"),
    "Gloria": (STD_BOY3, "“What are YOU looking at, spiky?\n …Huh. Your hair's like mine.”"),
    "Dot": (MIDGAL, "“Mom says my dad was a big hero!\n Or a cloud. She wasn't sure.”"),
    "Peggy": (FARM_BOY, "“I fell over three times today!\n Mom says it's part of the act.”"),
    "Candy": (STD_GIRL3, "“Mom knows EVERYONE'S secrets.\n Except who my dad is. Funny, huh?”"),
    "Rhonda": (NIBLE_BOY, "“Mom says not to get my hopes up.\n About anything. Ever.”"),
    "Lulu": (KOSTA_SGIRL, "“Mom cries at EVERYTHING.\n She cried when she saw you. Again.”"),
    "Raven": (COSMO_GIRL, "“Mom says I'm a child of darkness.\n I think she means I like the dark.”"),
    "Elena": (GON_GIRL, "“My mom's a Turk! Turk rule one:\n never trust spiky-haired men.\n …She broke that one.”"),
    "Marisol": (KOSTA_SBOY, "“Wanna build a sandcastle?\n Mom says my dad never stays\n long enough to help.”"),
    "Ruby": (STD_GIRL3, "“Mom says I was a lucky bet.\n Double or nothing!”"),
    "Holly": (SNOW, "“Mom's cold to everybody.\n Except you, I guess. Weird.”"),
    "Sakura": (UTAI, "“Mother is teaching me to bow.\n Bow to the spiky man, she said.”"),
    "Mags": (STD_BOY2, "“I fixed the toaster! Mom says\n I've got her hands and somebody\n else's hair.”"),
    "Celeste": (GON_BOY, "“Mom says I came from the stars.\n Or the Honey Bee Inn. One of those.”"),
    "Aurora": (COSMO_BOY, "“See that star? Mom named it after\n my dad. It's the spiky one.”"),
    "Tifa": (NIBLE_GIRL, "“Mom makes the best drinks!\n I'm not allowed any. Yet.”"),
    "Aerith": (STD_GIRL2, "“Want a flower? Mom says you\n owe her about a hundred.”"),
    "Scarlet": (MIDGAL, "“Kya ha ha! …That's how Mom\n laughs. I'm still practising.”"),
    "Velvet": (GON_GIRL, "“Mom's a superstar! She says I'm\n her best encore.”"),
}
REUSE = {"Velvet": "gaki2",      # coloss: 16 models
         "Rhonda": "mant2"}      # nivl_3: 16 models; a cloaked man hidden at its moment (678 > 677)
# the inn (nivinn_1) is at 16 models with nothing hidden to take over (Zangan, the
# innkeeper, the party): Rhonda's kid waits outside the inn door (nivl_3, the present-day town the inn exits to; nivl is the flashback copy)
ELSEWHERE = {"Rhonda": ("nivl_3", (-98, -347), 56)}
GAP = 20       # screen pixels between her and the kid, side by side
# Kids that blocked a path or the girl (user): placed by screen offset from her
# (dx, dy pixels, y down: negative dy = behind her) or at a fixed field point.
KID_OFFSET = {"Bambi": (-12, -14), "Peggy": (8, -14), "Candy": (0, -16)}
KID_AT = {"Scarlet": (-128, -239)}      # lower left of the conference room (Scarlet lower right)


def _at_screen(ctx, field, x, y, dx, dy):
    """Floor (x, y, z, tri) near (x, y) whose screen position is (dx, dy) pixels from it."""
    f = ctx.field(field)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    tri = mesh.find(x, y)
    near = mesh.nearby(tri, 8)
    sx, sy = cam.project(x, y, mesh.height(tri, x, y))
    best, cx, cy = None, int(x), int(y)
    for radius, step in ((1500, 30), (60, 3), (6, 1)):          # coarse to fine (fields differ in scale)
        for px in range(cx - radius, cx + radius + 1, step):
            for py in range(cy - radius, cy + radius + 1, step):
                t = next((t for t in near if mesh.contains(t, px, py)), None)
                if t is None:
                    continue
                pz = mesh.height(t, px, py)
                qx, qy = cam.project(px, py, pz)
                e = (qx - sx - dx) ** 2 + (qy - sy - dy) ** 2
                if best is None or e < best[0]:
                    best = (e, (px, py, pz, t))
        cx, cy = best[1][0], best[1][1]
    assert best and best[0] < 100, (field, x, y, dx, dy, best)   # within 10 px (floor edges)
    return best[1]


def _beside(ctx, field, x, y):
    """Floor (x, y, z, tri) next to (x, y) as seen on screen: about GAP pixels
    to her side, the nearest such spot on floor connected to hers."""
    f = ctx.field(field)
    mesh, cam = Walkmesh(f.section("walkmesh")), Camera(f.sections[1])
    tri = mesh.find(x, y)
    assert tri is not None, (field, x, y)
    near = mesh.nearby(tri, 6)
    sx, sy = cam.project(x, y, mesh.height(tri, x, y))
    best = None
    for k in range(32):
        a = 2 * math.pi * k / 32
        for d in range(20, 200, 5):
            px, py = round(x + d * math.cos(a)), round(y + d * math.sin(a))
            t = next((t for t in near if mesh.contains(t, px, py)), None)
            if t is None:
                break
            pz = mesh.height(t, px, py)
            qx, qy = cam.project(px, py, pz)
            if abs(qx - sx) >= GAP:
                if abs(qy - sy) <= abs(qx - sx) / 2 and (best is None or (d, qx < sx) < best[0]):
                    best = ((d, qx < sx), (px, py, pz, t))
                break
    assert best, (field, x, y)
    return best[1]


def _talk(line):
    def talk(sec):
        return ([Op(b"\x33\x01"), Op(b"\x35\x00\x08\x02"), Op(b"\x24\x08\x00")]   # UC 01, face Cloud
                + say(sec, NAME + "\n" + line) + [Op(b"\x33\x00"), asm.ret()])
    return talk


def _hidden_unless(i):
    var, bit = HB_KID[i]
    shown = asm.nop()
    return [asm.if_byte(var, "bit_off", bit, shown)] + hide() + [shown]    # bit set: skip the hide


def apply(ctx):
    assert set(KIDS) == {g["name"] for g in GIRLS}
    for i, g in enumerate(GIRLS):
        model, line = KIDS[g["name"]]
        f, (x, y), d = ELSEWHERE.get(g["name"], (g["field"], g["at"], g["dir"]))
        name = g["name"]
        if name in KID_AT:
            kx, ky = KID_AT[name]
            kt = Walkmesh(ctx.field(f).section("walkmesh")).find(kx, ky)
            assert kt is not None, (name, kx, ky)
            pos = (kx, ky, Walkmesh(ctx.field(f).section("walkmesh")).height(kt, kx, ky), kt)
        elif name in KID_OFFSET:
            pos = _at_screen(ctx, f, x, y, *KID_OFFSET[name])
        else:
            pos = _beside(ctx, f, x, y)
        if g["name"] in REUSE:
            reuse_npc(ctx, f, REUSE[g["name"]], model, pos, d, _talk(line))
            sec = Script.parse(ctx.field(f).sections[0])
            init = sec.script_ops(sec.entity_index(REUSE[g["name"]]), 0)
            ret = next(o for o in init if o.op == 0x00)
            sec.insert_before(ret, _hidden_unless(i), retarget=True)
            ctx.field(f).sections[0] = sec.build()
            continue
        idx = copy_model(ctx, f, *model)
        add_npc(ctx, f, "hbkid%02d" % i, idx, pos, d, _talk(line), init_extra=_hidden_unless(i))

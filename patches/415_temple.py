"""Temple of the Ancients, open as if explored up to the Demon Wall (pins in
world_overrides.json: every temple field at 631; the 'done' flags are in
_config.INITIAL_EVENT_FLAGS).

The way in: jtempl's door is a gateway to jtmpin1, whose altar (border1,
press OK) only did something at progress 604 (Tseng's Keystone scene ->
jtmpin2 -> back at 609 -> warp). Now the altar always runs the warp (cloud
script 11: the light, then MAPJUMP kuro_1), with player control back on
before the jump (UC persists across MAPJUMP and kuro_1's arrival scene, which
used to give it back, is marked done) and a real arrival point (the original
jump said (0, 0) tri 0; the arrival scene placed the party). The way out is
kuro_12's exit line to the temple top (open once the Demon Wall is beaten),
and (user: no way out once inside) a Temple Guide beside the arrival in kuro_1
who takes you back outside, to jtempl in front of the temple door. kuro_1 is at
16 models: he takes over Vincent's party entity (Cloud is locked as leader, so
the other PC entities only served the original scenes).
"""
from _travel import choice_menu, reuse_npc

from ff7 import asm
from ff7.camera import Camera, facing_screen
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

ENTRY, INSIDE = "jtmpin1", "kuro_1"
ARRIVE = (66, 156, 0x80)       # kuro_1: where its arrival scene left Cloud (SPLIT)
GUIDE = ("vince", ("rckt", 8), (38, 128))   # entity taken over, model (the archaeologist's), spot
OUTSIDE = ("jtempl", 509, 760, 40, 0)       # jtmpin1's own exit into jtempl: before the temple door


def _guide(ctx):
    name, model, (gx, gy) = GUIDE
    mesh = Walkmesh(ctx.field(INSIDE).section("walkmesh"))
    tri, arrive = mesh.find(gx, gy), mesh.find(*ARRIVE[:2])
    assert tri is not None and abs(mesh.height(tri, gx, gy) - mesh.height(arrive, *ARRIVE[:2])) < 5, (gx, gy)
    z = mesh.height(tri, gx, gy)
    out, ox, oy, otri, odir = OUTSIDE
    assert Walkmesh(ctx.field(out).section("walkmesh")).contains(otri, ox, oy), OUTSIDE
    leave = [Op(b"\x33\x00"), asm.mapjump(ctx.maplist.index(out), ox, oy, otri, odir), asm.ret()]
    talk = lambda sec: choice_menu(sec, "Temple Guide\n“Had enough of the maze?\n I can lead you back outside.”",
                                   ["Take me outside.", "Not yet."], [leave, None], face=True)
    reuse_npc(ctx, INSIDE, name, model, (gx, gy, z, tri),
              facing_screen(Camera(ctx.field(INSIDE).sections[1]), gx, gy, z, (0, 1)), talk)


def apply(ctx):
    mesh = Walkmesh(ctx.field(INSIDE).section("walkmesh"))
    x, y, d = ARRIVE
    tri = mesh.find(x, y)
    assert tri is not None, ARRIVE
    f = ctx.field(ENTRY)
    sec = Script.parse(f.sections[0])
    cloud = sec.entity_index("cloud")
    altar, warp = sec.script_ops(cloud, 6), sec.script_ops(cloud, 11)
    inside = ctx.maplist.index(INSIDE)
    jumps = [o for o in warp if o.op == 0x60]
    assert len(jumps) == 1 and int.from_bytes(bytes(jumps[0].raw[1:3]), "little") == inside, jumps
    assert any(o.op == 0x60 for o in altar), "altar script changed"
    sec.replace(jumps[0], [Op(b"\x33\x00"), asm.mapjump(inside, x, y, tri, d)])     # UC 00, then in
    sec.insert_before(altar[0], [asm.goto(warp[0])], retarget=True)                # the altar always warps
    f.sections[0] = sec.build()
    _guide(ctx)

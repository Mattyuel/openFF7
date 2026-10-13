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
kuro_12's exit line to the temple top (open once the Demon Wall is beaten).
"""
from ff7 import asm
from ff7.script import Op, Script
from ff7.walkmesh import Walkmesh

ENTRY, INSIDE = "jtmpin1", "kuro_1"
ARRIVE = (66, 156, 0x80)       # kuro_1: where its arrival scene left Cloud (SPLIT)


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

"""Shinra HQ in its after-the-infiltration state, plus the Rufus fight.

- 2f shop (blin2_i): the two treasure boxes only open from disc 2 (story value
  1008+); before that the shop assistant stops you ("You opened up all those
  things without asking..."). Remove that check from the two boxes only.
- Access level: all keycards and access 69 are given at new game (_config
  HQ_KEYCARD_BITS / HQ_ACCESS_LEVEL). Scripts that lower var[1][224] (59F
  guards, 61F, Domino's password on 62F, the 65F model chest, 67F, 68F) have
  those writes removed, so every elevator stop and door stays open.
- New-game flags (_config): 59F guards gone, 60F sneaking done, 68F scientist
  done. 67F (blin67_3) is pinned past Red XIII's specimen tank (100_midgar).
- 69F (blin69_1): [OK] at either elevator door asks "ride / fight": the fight
  is the original elevator boss (formation 460 Hundred Gunner, chaining to
  461 Heli Gunner; the story ran it from eleout at progress 311), once per
  visit (FLAG_ELEVATOR_FOUGHT).
- Roof (blin70_3): Rufus stands on the helipad (his original spot at the
  fight, progress 314); walking towards him (a line across the way onto the
  pad) starts formation 464, once per visit (FLAG_RUFUS_FOUGHT).
"""
from _config import FLAG_ELEVATOR_FOUGHT, FLAG_RUFUS_FOUGHT, FLAGS
from _travel import add_line, choice_menu

from ff7 import asm
from ff7.script import Op, Script

DISC2 = 1008
ACCESS = (0x10, 224)        # SETBYTE dst bank 1, offset 224
LOWERING = ["blin59", "blin61", "blin62_1", "blin65_1", "blin67_1", "blin68_1"]
ROOF = "blin70_3"
RUFUS_FORMATION = 464
RUFUS_LINE = ((-244, 1560, 182), (790, 1850, 182))   # across the only way onto the pad
RUFUS_FIGHT_MOMENT = 314
TOP_FLOOR, ELEVATOR_DOORS = "blin69_1", ("elel", "eler")
ELEVATOR_FORMATION = 460                # Hundred Gunner -> 461 Heli Gunner
ACCESS_69 = bytes.fromhex("1410e0450426")   # IFUB var[1][224] >= 69 (the door's card check)


def _shop_boxes(ctx):
    sec = Script.parse(ctx.field("blin2_i").sections[0])
    for name in ("TAKARAA", "TAKARAB"):
        ent = sec.entity_index(name)
        for op in sec.script_ops(ent, 1):
            # pinned fields compare a literal: IFSW/IFUW with left bank 0 and b == 1008
            if op.op in (0x16, 0x17, 0x18, 0x19) and op.raw[1] >> 4 == 0 \
                    and (op.raw[4] | op.raw[5] << 8) == DISC2:
                sec.remove(op)
                break
        else:
            raise RuntimeError("disc 2 check not found in %s" % name)
    ctx.field("blin2_i").sections[0] = sec.build()


def _keep_access(ctx):
    total = 0
    for field in LOWERING:
        sec = Script.parse(ctx.field(field).sections[0])
        writes = [o for o in sec.ops if o.op == 0x80 and (o.raw[1] & 0xF0, o.raw[2]) == ACCESS]
        assert writes, "%s: no access-level write found" % field
        for o in writes:
            sec.remove(o)
        total += len(writes)
        ctx.field(field).sections[0] = sec.build()
    return total


def _rufus(ctx):
    sec = Script.parse(ctx.field(ROOF).sections[0])
    lu = sec.entity_index("lu")
    # Pinned: "if not (303 == 314) goto skip" around his placement on the pad.
    gate = [o for o in sec.script_ops(lu, 0) if o.op in (0x16, 0x17, 0x18, 0x19)
            and o.raw[1] == 0 and (o.raw[4] | o.raw[5] << 8) == RUFUS_FIGHT_MOMENT]
    assert len(gate) == 1, gate
    sec.remove(gate[0])
    ctx.field(ROOF).sections[0] = sec.build()

    def fight(sec):
        done = asm.ret()
        return [asm.if_byte(FLAGS, "bit_off", FLAG_RUFUS_FOUGHT, done),   # once per visit
                asm.biton(FLAGS, FLAG_RUFUS_FOUGHT),
                Op(b"\x33\x01"),                                         # UC 01
                Op(b"\xFC\x02"),                                         # FMUSC 02 (as the original fight)
                asm.battle(RUFUS_FORMATION),
                Op(bytes([0x01, lu, 0xCB])),                             # REQ lu script 11: hide him
                Op(b"\x33\x00"),                                         # UC 00
                done]
    add_line(ctx, ROOF, "rufus", *RUFUS_LINE, fight,
             init_extra=[asm.bitoff(FLAGS, FLAG_RUFUS_FOUGHT)])


def _elevator_boss(ctx):
    sec = Script.parse(ctx.field(TOP_FLOOR).sections[0])
    for name in ELEVATOR_DOORS:
        ent = sec.entity_index(name)
        ops = sec.script_ops(ent, 4)
        i = next(k for k, o in enumerate(ops) if bytes(o.raw[:6]) == ACCESS_69)
        ride = ops[i + 1]
        assert bytes(ride.raw) == b"\x33\x01", ride.raw.hex()       # UC 01: the original ride
        assert sum(1 for o in ops if o.op == 0x60 and o.raw[1:3] == b"\xe9\x00") == 1  # MAPJUMP eleout
        done = asm.nop()
        fight = [asm.if_byte(FLAGS, "bit_off", FLAG_ELEVATOR_FOUGHT, done),
                 asm.biton(FLAGS, FLAG_ELEVATOR_FOUGHT),
                 asm.battle(ELEVATOR_FORMATION), done]
        menu = choice_menu(sec, "Elevator\n(Something heavy is grinding\n up the shaft...)",
                           ["Ride the elevator.", "Wait for it and fight.", "Leave it."],
                           [[asm.goto(ride)], fight, None])
        sec.insert_before(ride, menu, retarget=False)
    init = sec.script_ops(sec.entity_index(ELEVATOR_DOORS[0]), 0)
    ret = next(o for o in init if o.op == 0x00)
    sec.insert_before(ret, [asm.bitoff(FLAGS, FLAG_ELEVATOR_FOUGHT)])
    ctx.field(TOP_FLOOR).sections[0] = sec.build()


def apply(ctx):
    _shop_boxes(ctx)
    _elevator_boss(ctx)
    _keep_access(ctx)
    _rufus(ctx)

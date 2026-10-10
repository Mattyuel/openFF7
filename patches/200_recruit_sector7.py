"""Recruit Tifa in 7th Heaven and Barret in the Sector 7 weapon shop."""
from _config import BARRET, TIFA
from _recruit import hide, hide_if_recruited, recruit_talk

from ff7 import asm
from ff7.models import ModelLoader
from ff7.script import Op, Script

TIFA_LINES = dict(
    question="{TIFA}\n“{CLOUD}! I was hoping you'd stop by.\n Are you heading out somewhere?”",
    choices=("Come with me, Tifa.", "Not right now."),
    yes_reply="{TIFA}\n“Just try and stop me!\n Let me grab my gloves.”",
    no_reply="{TIFA}\n“Okay. You know where to find me.”",
    joined="{TIFA} joined the party!",
)
BARRET_LINES = dict(
    question="{BARRET}\n“Yo, {CLOUD}! You lookin' for some muscle?”",
    choices=("Yeah. Let's go.", "Not now."),
    yes_reply="{BARRET}\n“Hah! Now you're talkin'!”",
    no_reply="{BARRET}\n“Suit yourself. I ain't goin' nowhere.”",
    joined="{BARRET} joined the party!",
)

# Barret in the weapon shop: walkmesh triangle 6, left of the counter area.
BARRET_POS = (-144, 26, 0, 6)
BARRET_DIR = 0x40


def _seventh_heaven(ctx):
    sec = Script.parse(ctx.field("mds7pb_1").sections[0])
    tifa = sec.entity_index("tifa")
    # Talk script becomes the recruitment.
    talk = recruit_talk(sec, TIFA, **TIFA_LINES)
    old = sec.entry[tifa][1]
    sec.insert_before(old, talk, retarget=False)
    sec.entry[tifa][1] = talk[0]
    # Hidden once recruited (end of her init).
    init_ret = next(o for o in sec.script_ops(tifa, 0) if o.op == 0x00)
    sec.insert_before(init_ret, hide_if_recruited(TIFA), retarget=False)
    # Barret is recruited at the weapon shop, not here: the bar setup script
    # (stagedr -> ballet script 9) always hides him.
    barret = sec.entity_index("ballet")
    first = sec.entry[barret][9]
    sec.insert_before(first, hide() + [asm.ret()])
    ctx.field("mds7pb_1").sections[0] = sec.build()


def _weapon_shop(ctx):
    # Barret's model, copied from the Beginner's Hall (mds7_w2), where entity
    # 'ballet' uses model 1.
    donor = ModelLoader(ctx.field("mds7_w2").section("models"))
    loader = ModelLoader(ctx.field("mds7_w1").section("models"))
    model = loader.add(donor.models[1])
    ctx.field("mds7_w1").set_section("models", loader.build())

    sec = Script.parse(ctx.field("mds7_w1").sections[0])
    x, y, z, tri = BARRET_POS
    init = [Op(bytes([0xA1, model])),                                       # CHAR
            Op(bytes([0xA5, 0, 0]) + x.to_bytes(2, "little", signed=True)
               + y.to_bytes(2, "little", signed=True) + z.to_bytes(2, "little", signed=True)
               + tri.to_bytes(2, "little")),                                # XYZI
            Op(bytes([0xB3, 0x00, BARRET_DIR]))]                            # DIR
    init += hide_if_recruited(BARRET) + [asm.ret(), asm.ret()]
    ent = sec.add_entity("barret", {0: init})
    talk = recruit_talk(sec, BARRET, **BARRET_LINES)
    sec.ops.extend(talk)
    sec.entry[ent][1] = talk[0]
    ctx.field("mds7_w1").sections[0] = sec.build()


def _station(ctx):
    """The Sector 7 station shows Barret on the platform; he is now recruited
    in the weapon shop, so hide him there."""
    sec = Script.parse(ctx.field("mds7st3").sections[0])
    barret = sec.entity_index("ballet")
    init_ret = next(o for o in sec.script_ops(barret, 0) if o.op == 0x00)
    sec.insert_before(init_ret, hide(), retarget=False)
    ctx.field("mds7st3").sections[0] = sec.build()


def apply(ctx):
    _station(ctx)
    _seventh_heaven(ctx)
    _weapon_shop(ctx)

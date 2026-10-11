"""Shared helpers for character recruitment scenes.

A recruitment talk script asks whether the character should join. On "yes":
the character becomes available in the PHS, joins the active party if there is
room, a recruited flag is set and the NPC disappears. On "no": a short reply.
"""
from _config import MENU_PHS, PHS_MIN_PARTY, RECRUIT_COUNT, RECRUITED

from ff7 import asm
from ff7.script import Op
from ff7.text import encode

ANSWER = (5, 240)  # temporary field variable for the choice
# Sound effects as the original scripts use them next to STITM / SMTRA.
SOUND_ITEM, SOUND_MATERIA = 0x168, 0x1EA
SOUND_RECRUIT = SOUND_MATERIA      # no "joined" jingle in the game; the materia chime


def window(text, win=0, x=8, y=8):
    """WINDOW sized for `text` (ff7 windows: 16 px per line + 9)."""
    lines = text.split("\n")
    widest = max(len(l.replace("{CHOICE}", "     ").replace("{CLOUD}", "Cloud ")
                     .replace("{BARRET}", "Barret").replace("{TIFA}", "Tifa"))
                 for l in lines)
    w = min(310, widest * 7 + 24)
    h = 16 * len(lines) + 9
    return Op(bytes([0x50, win]) + x.to_bytes(2, "little") + y.to_bytes(2, "little")
              + w.to_bytes(2, "little") + h.to_bytes(2, "little"))


def say(script, text, win=0):
    """WINDOW + MESSAGE ops for a new line of dialogue."""
    tid = script.add_string(encode(text))
    return [window(text, win), asm.message(win, tid)]


def sound(sound_id, pan=0x40):
    """SOUND [banks][u16 id][pan]."""
    return Op(bytes([0xF1, 0x00]) + sound_id.to_bytes(2, "little") + bytes([pan]))


def hide():
    return [Op(b"\x7E\x01"), Op(b"\xC7\x01"), Op(b"\xA4\x00")]  # TLKON 01, SOLID 01, VISI 00


LEADER = (5, 242)  # temporary field variable: party leader's character id


def get_leader():
    """GETPC: LEADER = character id in party slot 0."""
    return Op(bytes([0x74, LEADER[0], 0, LEADER[1]]))


def hide_if_recruited(char, pc_entity=False):
    """Ops for an init script: hide this NPC once `char` has been recruited.
    For a PC entity (CHAR + PC char) it is also the character's own entity
    when they lead the party, so it is not hidden then."""
    end = asm.nop()
    ops = [asm.if_byte(RECRUITED, "bit_on", char, end)]
    if pc_entity:
        ops += [get_leader(), asm.if_byte(LEADER, "!=", char, end)]
    return ops + hide() + [end]


def recruit_talk(script, char, question, choices, yes_reply, no_reply, joined):
    """Build the talk script. `question` is the dialogue before the choices
    (its own lines), `choices` = (yes text, no text)."""
    text = question + "\n{CHOICE}" + choices[0] + "\n{CHOICE}" + choices[1]
    yes_line = len(question.split("\n"))
    tid = script.add_string(encode(text))
    decline = say(script, no_reply)
    end_decline = [Op(b"\x33\x00"), asm.ret()]
    ops = [Op(b"\x33\x01"),                                  # UC 01
           window(text),
           asm.ask(0, tid, yes_line, yes_line + 1, ANSWER),
           asm.if_byte(ANSWER, "==", yes_line, decline[0])]
    ops += say(script, yes_reply)
    ops += [Op(bytes([0xCD, 0x01, char])),                   # MMBUD: available in PHS
            Op(bytes([0xC8, char])),                         # PRTYP: join active party
            asm.biton(RECRUITED, char)]
    ops += count_recruit()
    ops += [sound(SOUND_RECRUIT)] + say(script, joined)
    ops += hide() + [Op(b"\x33\x00"), asm.ret()]
    return ops + decline + end_decline


def count_recruit():
    """Ops: one more character recruited; show the PHS once there are enough
    to fill the party (the PHS can't be left with fewer than 3 in it)."""
    shown = asm.nop()
    return [Op(bytes([0x95, RECRUIT_COUNT[0], RECRUIT_COUNT[1]])),      # INC
            asm.if_byte(RECRUIT_COUNT, ">=", PHS_MIN_PARTY, shown),
            Op(bytes([0x92, 0x20, 28]) + MENU_PHS.to_bytes(2, "little")),  # OR2 var[2][28] |= PHS
            shown]


def xyzi(x, y, z, tri):
    return Op(bytes([0xA5, 0, 0]) + x.to_bytes(2, "little", signed=True)
              + y.to_bytes(2, "little", signed=True) + z.to_bytes(2, "little", signed=True)
              + tri.to_bytes(2, "little"))


def add_recruit_npc(ctx, field, donor_field, donor_model, name, char, pos, direction, lines):
    """Add a new NPC for `char` to `field`, with the model copied from
    `donor_field` (model index `donor_model`), standing at pos (x, y, z,
    triangle), whose talk script is the recruitment. Hidden once recruited."""
    from ff7.models import ModelLoader
    from ff7.script import Script
    donor = ModelLoader(ctx.field(donor_field).section("models"))
    loader = ModelLoader(ctx.field(field).section("models"))
    model = loader.add_from(donor, donor_model)
    ctx.field(field).set_section("models", loader.build())

    sec = Script.parse(ctx.field(field).sections[0])
    init = [Op(bytes([0xA1, model])), xyzi(*pos), Op(bytes([0xB3, 0x00, direction]))]
    init += hide_if_recruited(char) + [asm.ret(), asm.ret()]
    ent = sec.add_entity(name, {0: init})
    talk = recruit_talk(sec, char, **lines)
    sec.ops.extend(talk)
    sec.entry[ent][1] = talk[0]
    ctx.field(field).sections[0] = sec.build()

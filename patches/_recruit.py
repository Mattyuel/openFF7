"""Shared helpers for character recruitment scenes.

A recruitment talk script asks whether the character should join. On "yes":
the character becomes available in the PHS, joins the active party if there is
room, a recruited flag is set and the NPC disappears. On "no": a short reply.
"""
from _config import RECRUITED

from ff7 import asm
from ff7.script import Op
from ff7.text import encode

ANSWER = (5, 240)  # temporary field variable for the choice


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


def hide():
    return [Op(b"\x7E\x01"), Op(b"\xC7\x01"), Op(b"\xA4\x00")]  # TLKON 01, SOLID 01, VISI 00


def hide_if_recruited(char):
    """Ops for an init script: hide this NPC once `char` has been recruited."""
    end = asm.nop()
    return [asm.if_byte(RECRUITED, "bit_on", char, end)] + hide() + [end]


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
    ops += say(script, joined)
    ops += hide() + [Op(b"\x33\x00"), asm.ret()]
    return ops + decline + end_decline

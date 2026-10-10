"""FF7 field/kernel text encoding (English) -> readable string."""

_CHARS = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~ "
    "ÄÅÇÉÑÖÜáàâäãåçéèêëíìîïñóòôöõúùûü"
    "⌘°¢£ÙÛ¶ß®©™´¨≠ÆØ∞±≤≥¥µ∂ΣΠπ⌡ªºΩæø"
    "¿¡¬√ƒ≈∆«»… ÀÃÕŒœ–—“”‘’÷◊ÿŸ⁄¤‹›ﬁﬂ■‧‚„‰ÂÊÁËÈÍÎÏÌÓÔ ÒÚÛ"
)

NAMES = {
    0xEA: "{CLOUD}", 0xEB: "{BARRET}", 0xEC: "{TIFA}", 0xED: "{AERIS}",
    0xEE: "{RED XIII}", 0xEF: "{YUFFIE}", 0xF0: "{CAIT SITH}", 0xF1: "{VINCENT}",
    0xF2: "{CID}", 0xF3: "{PARTY #1}", 0xF4: "{PARTY #2}", 0xF5: "{PARTY #3}",
    0xF6: "{CIRCLE}", 0xF7: "{TRIANGLE}", 0xF8: "{SQUARE}", 0xF9: "{CROSS}",
}
SPECIAL = {0xE0: "{CHOICE}", 0xE1: "\t", 0xE2: ", ", 0xE3: '."', 0xE4: '…"',
           0xE7: "\n", 0xE8: "{NEW}\n"}
COLORS = {0xD2: "{GRAY}", 0xD3: "{BLUE}", 0xD4: "{RED}", 0xD5: "{PURPLE}",
          0xD6: "{GREEN}", 0xD7: "{CYAN}", 0xD8: "{YELLOW}", 0xD9: "{WHITE}",
          0xDA: "{BLINK}", 0xDB: "{MULTICOLOUR}", 0xDC: "{PAUSE}"}


def decode(raw):
    out = []
    i = 0
    while i < len(raw):
        b = raw[i]
        i += 1
        if b == 0xFF:
            break
        if b == 0xFE and i < len(raw):
            c = raw[i]
            i += 1
            if c in COLORS:
                out.append(COLORS[c])
            elif c == 0xDD:
                out.append("{WAIT %d}" % (raw[i] | raw[i + 1] << 8))
                i += 2
            elif c in (0xDE, 0xDF, 0xE1):
                out.append("{VAR}")
                i += 4
            elif c == 0xE2:
                out.append("{VAR}")
                i += 4
            else:
                out.append("{FE%02X}" % c)
        elif b in NAMES:
            out.append(NAMES[b])
        elif b in SPECIAL:
            out.append(SPECIAL[b])
        elif b < len(_CHARS):
            out.append(_CHARS[b])
        else:
            out.append("{%02X}" % b)
    return "".join(out)


_ENCODE = {}
for _i, _c in enumerate(_CHARS):
    _ENCODE.setdefault(_c, _i)
_TOKENS = {v: k for k, v in NAMES.items()}
_TOKENS.update({"{CHOICE}": 0xE0, "{NEW}": 0xE8})
_COLOR_TOKENS = {v: k for k, v in COLORS.items()}


def encode(text):
    """Readable text -> FF7 bytes (ends with 0xFF). Supports the {TOKENS} that
    decode() produces for names, choices, colours and {NEW}; newline = new line."""
    out = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "{":
            j = text.index("}", i)
            tok = text[i:j + 1]
            if tok in _TOKENS:
                out.append(_TOKENS[tok])
            elif tok in _COLOR_TOKENS:
                out += bytes([0xFE, _COLOR_TOKENS[tok]])
            else:
                raise ValueError("unknown text token %s" % tok)
            i = j + 1
            continue
        c = text[i]
        if c == "\n":
            out.append(0xE7)
        elif c == "\t":
            out.append(0xE1)
        elif c in _ENCODE:
            out.append(_ENCODE[c])
        else:
            raise ValueError("character not in the FF7 font: %r" % c)
        i += 1
    out.append(0xFF)
    return bytes(out)

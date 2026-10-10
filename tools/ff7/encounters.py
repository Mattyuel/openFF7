"""Field encounter section (section 6): two tables of 24 bytes each.

Table: u8 enabled, u8 rate, u16 normal[6], u16 special[4] (back attack 1,
back attack 2, side attack, pincer), u16 pad. Each u16 = prob << 10 | formation.
"""
import struct

SPECIAL_KINDS = ["back_attack_1", "back_attack_2", "side_attack", "pincer"]


def _entry(v):
    return {"formation": v & 0x3FF, "prob": v >> 10}


def parse(section):
    tables = []
    for t in range(len(section) // 24):
        o = t * 24
        enabled, rate = section[o], section[o + 1]
        vals = struct.unpack_from("<10H", section, o + 2)
        tables.append({
            "enabled": enabled, "rate": rate,
            "normal": [_entry(v) for v in vals[:6] if v],
            "special": {k: _entry(v) for k, v in zip(SPECIAL_KINDS, vals[6:]) if v},
        })
    return tables

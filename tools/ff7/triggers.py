"""Field triggers section (section 7, 740 bytes on PC).

  0x00 char name[9]; u8 control; s16 focus_height; s16 camera_range[4]
  0x14 ... background layer info ... (to 0x38)
  0x38 gateways[12]   24 bytes: s16 p1[3], s16 p2[3], s16 dest[3] (x, y, triangle),
                      u16 field_id (0x7FFF = unused), u8 dir, u8 unknown[3]
  0x158 triggers[12]  16 bytes: s16 p1[3], s16 p2[3], u8 bg_group, u8 on, u8 off, u8 sound
  0x218 u8 show_arrow[12]
  0x224 arrows[12]    16 bytes: s32 x, y, z, type
"""
import struct

GATEWAYS = 0x38
UNUSED = 0x7FFF


def gateways(section):
    out = []
    for i in range(12):
        o = GATEWAYS + i * 24
        p1 = struct.unpack_from("<3h", section, o)
        p2 = struct.unpack_from("<3h", section, o + 6)
        dest = struct.unpack_from("<3h", section, o + 12)
        field, = struct.unpack_from("<H", section, o + 18)
        if field == UNUSED:
            continue
        out.append({"slot": i, "p1": p1, "p2": p2, "dest_x": dest[0], "dest_y": dest[1],
                    "dest_triangle": dest[2], "field": field, "dir": section[o + 20]})
    return out


def set_gateway_field(section, slot, field_id):
    """Return a copy of the section with gateway `slot` leading to `field_id`."""
    data = bytearray(section)
    struct.pack_into("<H", data, GATEWAYS + slot * 24 + 18, field_id)
    return bytes(data)


def free_slot(section):
    for i in range(12):
        field, = struct.unpack_from("<H", section, GATEWAYS + i * 24 + 18)
        if field == UNUSED:
            return i
    raise ValueError("no free gateway slot")


def set_gateway(section, slot, p1, p2, dest, field_id, direction, template_slot=0):
    """Return a copy of the section with gateway `slot` set: walking over the
    line p1-p2 (x, y, z) jumps to field_id at dest (x, y, triangle).
    The 3 trailing unknown bytes are copied from `template_slot`."""
    data = bytearray(section)
    o = GATEWAYS + slot * 24
    tail = bytes(data[GATEWAYS + template_slot * 24 + 21:GATEWAYS + template_slot * 24 + 24])
    struct.pack_into("<3h3h3hHB", data, o, *p1, *p2, *dest, field_id, direction)
    data[o + 21:o + 24] = tail
    return bytes(data)

"""scene.bin: 32 blocks of 0x2000 bytes, each holding up to 16 gzip'd scenes.

Each scene (7808 bytes) defines 3 enemies and 4 battle formations.
Formation id = scene_index * 4 + slot.
"""
import gzip
import struct
import zlib

from .text import decode

BLOCK = 0x2000
SCENE_SIZE = 7808


def read_scenes(buf):
    scenes = []
    for b in range(len(buf) // BLOCK):
        blk = buf[b * BLOCK:(b + 1) * BLOCK]
        ptrs = [p for p in struct.unpack_from("<16I", blk, 0) if p != 0xFFFFFFFF]
        for i, p in enumerate(ptrs):
            start = p * 4
            end = ptrs[i + 1] * 4 if i + 1 < len(ptrs) else BLOCK
            data = blk[start:end]
            d = zlib.decompressobj(16 + zlib.MAX_WBITS)
            scenes.append(d.decompress(data))
    return scenes


def parse_scene(s):
    enemy_ids = struct.unpack_from("<3H", s, 0)
    setups = []
    for f in range(4):
        o = 0x0008 + f * 20
        loc, nxt, esc_counter = struct.unpack_from("<HHH", s, o)
        flags, = struct.unpack_from("<H", s, o + 16)
        setups.append({"location": loc, "next_formation": nxt, "escape_counter": esc_counter,
                       "flags": flags, "layout": s[o + 18]})
    formations = []
    for f in range(4):
        members = []
        for m in range(6):
            o = 0x0118 + f * 96 + m * 16
            eid, = struct.unpack_from("<H", s, o)
            if eid != 0xFFFF:
                members.append(eid)
        formations.append(members)
    names = {}
    for e in range(3):
        o = 0x0298 + e * 184
        if enemy_ids[e] != 0xFFFF:
            names[enemy_ids[e]] = decode(s[o:o + 32]).strip()
    level = {}
    for e in range(3):
        if enemy_ids[e] != 0xFFFF:
            level[enemy_ids[e]] = s[0x0298 + e * 184 + 32]
    return {"enemy_ids": enemy_ids, "names": names, "levels": level,
            "setups": setups, "formations": formations}


def formations(buf):
    """Return {formation_id: {"enemies": [names], "setup": {...}}}."""
    out = {}
    for si, raw in enumerate(read_scenes(buf)):
        sc = parse_scene(raw)
        for f in range(4):
            members = sc["formations"][f]
            if not members:
                continue
            out[si * 4 + f] = {
                "enemies": [sc["names"].get(e, "#%d" % e) for e in members],
                "levels": [sc["levels"].get(e, 0) for e in members],
                "setup": sc["setups"][f],
            }
    return out

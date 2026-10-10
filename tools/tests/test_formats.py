#!/usr/bin/env python3
"""Sanity checks for the format tools against the real game data.

Run: python3 tools/tests/test_formats.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ff7 import lzss, scene  # noqa: E402
from ff7.disasm import disassemble  # noqa: E402
from ff7.field import FieldFile, ScriptSection  # noqa: E402
from ff7.lgp import LGP  # noqa: E402
from ff7.script import Script  # noqa: E402
from ff7 import asm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "FINAL FANTASY VII", "data")


def test_lgp_roundtrip():
    for rel in ["field/flevel.lgp", "field/char.lgp", "wm/world_us.lgp", "battle/battle.lgp"]:
        orig = open(os.path.join(DATA, rel), "rb").read()
        assert LGP.parse(orig).build() == orig, rel


def _jump_signature(sc):
    """Non-NOP ops with jump targets resolved past NOPs (long/short forms unified)."""
    short = {0x11: 0x10, 0x13: 0x12, 0x15: 0x14, 0x17: 0x16, 0x19: 0x18}
    real = [o for o in sc.ops if o.raw != b"\x5f"]
    index = {id(o): i for i, o in enumerate(real)}

    def resolve(t):
        if t not in sc.ops:
            return "END"
        j = sc.index(t)
        while j < len(sc.ops) and sc.ops[j].raw == b"\x5f":
            j += 1
        return index[id(sc.ops[j])] if j < len(sc.ops) else "END"

    return [(short.get(o.raw[0], o.raw[0]), resolve(o.target) if o.target is not None else None)
            for o in real]


def test_fields():
    archive = LGP.read(os.path.join(DATA, "field", "flevel.lgp"))
    names = [n for n in archive.names() if "." not in n and n != "maplist"]
    sample = set(random.Random(7).sample(names, 5))
    jumps = 0
    for name in names:
        raw = lzss.decompress(archive[name])
        ff = FieldFile(raw)
        assert ff.build() == raw, name
        if name in sample:
            assert lzss.decompress(lzss.compress(raw)) == raw, name
        sec = ScriptSection(ff.sections[0])
        if sec.broken:
            continue
        editable = Script.parse(ff.sections[0])
        assert editable.build() == ff.sections[0], name
        if name in sample:
            # Insert NOPs everywhere; every jump must still reach the same instruction.
            before = _jump_signature(editable)
            for o in list(editable.ops)[::3]:
                editable.insert_before(o, [asm.nop()], retarget=False)
            assert _jump_signature(Script.parse(editable.build())) == before, name
        code = disassemble(sec.data, min(sec.script_bounds()), sec.string_offset)
        starts = {i.pos for i in code} | {sec.string_offset}
        assert all(p in starts for p in sec.script_bounds()), name
        for ins in code:
            if ins.target is not None:
                jumps += 1
                assert ins.target in starts, (name, ins)
    assert jumps > 30000


def test_scene():
    forms = scene.formations(open(os.path.join(DATA, "lang-en", "battle", "scene.bin"), "rb").read())
    assert forms[324]["enemies"] == ["Guard Scorpion"]


if __name__ == "__main__":
    for fn in [test_lgp_roundtrip, test_fields, test_scene]:
        fn()
        print("ok", fn.__name__)

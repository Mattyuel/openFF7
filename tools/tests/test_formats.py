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


def test_open_vars_unused():
    """openFF7's own save variables (bank 4, 224-255) are unused by the original scripts."""
    from ff7 import varscan
    archive = LGP.read(os.path.join(DATA, "field", "flevel.lgp"))
    secs = [ScriptSection(FieldFile(lzss.decompress(archive[n])).sections[0])
            for n in archive.names() if "." not in n and n != "maplist"]
    used = varscan.field_usage(secs)
    assert not used[4] & set(range(224, 256))
    wm = LGP.read(os.path.join(DATA, "wm", "world_us.lgp"))
    for ev in ("wm0.ev", "wm2.ev", "wm3.ev"):
        offsets = varscan.worldmap_usage(wm[ev])
        assert not offsets & set(range(0x300 + 224, 0x300 + 256)), ev


def test_patches():
    """Apply patches/ in memory; patched fields must parse and lose all story-progress refs."""
    import importlib.util
    sys.path.insert(0, os.path.join(ROOT, "patches"))
    spec = importlib.util.spec_from_file_location("ff7tool", os.path.join(ROOT, "tools", "ff7tool.py"))
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    if not os.path.isdir(tool.FIELD_DIR):
        tool.extract()
    ctx = tool.BuildContext()
    midgar = None
    for path in sorted(os.listdir(os.path.join(ROOT, "patches"))):
        if path[0].isdigit() and path.endswith(".py"):
            spec = importlib.util.spec_from_file_location(path[:-3], os.path.join(ROOT, "patches", path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.apply(ctx)
            if path.endswith("_midgar.py"):
                midgar = mod
    from ff7.disasm import PROGRESS_VAR
    fields = [f for v in midgar.PINNED.values() for f in v] + [f for v in midgar.REGIONS.values() for f in v]
    for f in fields:
        sec = ScriptSection(FieldFile(ctx.field(f).build()).sections[0])
        for ins in disassemble(sec.data, min(sec.script_bounds()), sec.string_offset):
            if ins.op in (0x16, 0x17, 0x18, 0x19):
                assert (ins.args["bank_a"], ins.args["a"]) != PROGRESS_VAR, f
            if ins.op == 0x81:
                assert (ins.args["bank_d"], ins.args["dst"]) != PROGRESS_VAR, f


if __name__ == "__main__":
    for fn in [test_lgp_roundtrip, test_fields, test_scene, test_open_vars_unused, test_patches]:
        fn()
        print("ok", fn.__name__)

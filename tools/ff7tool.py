#!/usr/bin/env python3
"""openFF7 command-line tool.

  ff7tool.py extract            Decompress all field files into work/field/
  ff7tool.py dump FIELD...      Write readable script dumps to work/scripts/FIELD.txt
  ff7tool.py dump --all
  ff7tool.py wmdump             Write world map script dumps to work/worldmap/
  ff7tool.py inventory          Write the field/boss inventory to docs/inventory/
  ff7tool.py build [--out DIR]  Apply patches/*.py and write a standalone game folder
  ff7tool.py scenes FIELD...    Simulate entering patched fields; list likely cutscenes
  ff7tool.py plan-world         Propose a story moment for every unhandled field
  ff7tool.py quiet-flags        Search new-game flags that silence entry scenes (after build)
"""
import argparse
import collections
import csv
import glob
import json
import importlib.util
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff7 import encounters, lzss, scene, triggers  # noqa: E402
from ff7.disasm import PROGRESS_VAR, disassemble, format_instruction  # noqa: E402
from ff7.field import FieldFile, ScriptSection  # noqa: E402
from ff7.lgp import LGP  # noqa: E402
from ff7.text import decode  # noqa: E402
from ff7.worldmap import EvScript, field_table  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "FINAL FANTASY VII", "data")
WORK = os.path.join(ROOT, "work")
FIELD_DIR = os.path.join(WORK, "field")
INV_DIR = os.path.join(ROOT, "docs", "inventory")


def extract(_args=None):
    os.makedirs(FIELD_DIR, exist_ok=True)
    archive = LGP.read(os.path.join(GAME, "field", "flevel.lgp"))
    for name in archive.names():
        if "." in name or name == "maplist":
            with open(os.path.join(FIELD_DIR, name), "wb") as fh:
                fh.write(archive[name])
            continue
        out = os.path.join(FIELD_DIR, name + ".dec")
        if not os.path.exists(out):
            with open(out, "wb") as fh:
                fh.write(lzss.decompress(archive[name]))
    print("extracted %d entries to %s" % (len(archive.names()), FIELD_DIR))


def maplist():
    raw = open(os.path.join(FIELD_DIR, "maplist"), "rb").read()
    n = raw[0] | raw[1] << 8
    return [raw[2 + i * 32:2 + i * 32 + 32].split(b"\0")[0].decode() for i in range(n)]


def load_field(name):
    ff = FieldFile(open(os.path.join(FIELD_DIR, name + ".dec"), "rb").read())
    return ff, ScriptSection(ff.sections[0])


def field_scripts(sec):
    """Yield (entity_index, script_index, [instructions]) for each distinct script."""
    if sec.broken:
        return
    starts = sec.script_bounds() + [sec.string_offset]
    seen = set()
    for e, ptrs in enumerate(sec.scripts):
        for si, p in enumerate(ptrs):
            if p in seen:
                continue
            seen.add(p)
            nxt = min((x for x in starts if x > p), default=p)
            yield e, si, disassemble(sec.data, p, nxt)


def dump(args):
    """Readable script dumps -> work/scripts/ (original game), or with --built
    from the last build's flevel.lgp -> work/scripts_built/."""
    built = None
    if getattr(args, "built", False):
        built = LGP.read(os.path.join(ROOT, "build", "openFF7", "data", "field", "flevel.lgp"))
    elif not os.path.isdir(FIELD_DIR):
        extract()
    names = maplist()[1:] if args.all else args.fields
    out_dir = os.path.join(WORK, "scripts_built" if built else "scripts")
    os.makedirs(out_dir, exist_ok=True)
    ids = {n: i for i, n in enumerate(maplist())}
    for name in names:
        if built is not None:
            if not name or name not in built:
                continue
            sec = ScriptSection(FieldFile(lzss.decompress(built[name])).sections[0])
            if sec.broken:
                continue
        else:
            if not name or not os.path.exists(os.path.join(FIELD_DIR, name + ".dec")):
                continue
            _, sec = load_field(name)
        lines = ["# field %s (id %s)" % (name, ids.get(name)), ""]
        for e, si, code in field_scripts(sec):
            lines.append("## entity %d '%s' script %d" % (e, sec.entity_names[e], si))
            targets = {i.target for i in code if i.target is not None}
            for ins in code:
                if ins.pos in targets:
                    lines.append("L%04X:" % ins.pos)
                text = format_instruction(ins, lambda t: "L%04X" % t)
                if ins.op == 0x60:
                    text += "    ; -> %s" % (maplist()[ins.args["field"]] if ins.args["field"] < len(maplist()) else "?")
                if ins.op in (0x40, 0x48, 0x43) and ins.args.get("text", 999) < len(sec.string_offsets):
                    text += "    ; \"%s\"" % decode(sec.raw_string(ins.args["text"])).replace("\n", " / ")[:100]
                lines.append("  " + text)
            lines.append("")
        lines.append("## strings")
        for i in range(len(sec.string_offsets)):
            lines.append("%3d: %s" % (i, decode(sec.raw_string(i)).replace("\n", " / ")))
        with open(os.path.join(out_dir, name + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    print("wrote %d dumps to %s" % (len(names), out_dir))


def wmdump(_args):
    archive = LGP.read(os.path.join(GAME, "wm", "world_us.lgp"))
    out_dir = os.path.join(WORK, "worldmap")
    os.makedirs(out_dir, exist_ok=True)
    for name in ("wm0.ev", "wm2.ev", "wm3.ev"):
        with open(os.path.join(out_dir, name + ".txt"), "w") as fh:
            fh.write(EvScript(archive[name]).dump())
    print("wrote world map dumps to", out_dir)


def inventory(_args):
    if not os.path.isdir(FIELD_DIR):
        extract()
    os.makedirs(INV_DIR, exist_ok=True)
    names = maplist()
    forms = scene.formations(open(os.path.join(GAME, "lang-en", "battle", "scene.bin"), "rb").read())

    def enemies(fid):
        f = forms.get(fid)
        return " + ".join(sorted(set(f["enemies"]))) if f else "?"

    rows = []
    scripted = collections.defaultdict(set)
    links = []
    for fid, name in enumerate(names):
        if fid == 0 or not os.path.exists(os.path.join(FIELD_DIR, name + ".dec")):
            continue
        ff, sec = load_field(name)
        progress_values = set()
        progress_writes = set()
        jumps, battles, loc_names = set(), set(), []
        for _e, _si, code in field_scripts(sec):
            for ins in code:
                a = ins.args
                if ins.op in (0x16, 0x17, 0x18, 0x19):
                    if (a["bank_a"], a["a"]) == PROGRESS_VAR and a["bank_b"] == 0:
                        progress_values.add(a["b"])
                if ins.op == 0x81 and (a["bank_d"], a["dst"]) == PROGRESS_VAR and a["bank_s"] == 0:
                    progress_writes.add(a["val"])
                if ins.op == 0x60:
                    jumps.add(a["field"])
                if ins.op == 0x70 and a["bank"] == 0:
                    battles.add(a["formation"])
                    scripted[a["formation"]].add(name)
                if ins.op == 0x43 and a["text"] < len(sec.string_offsets):
                    nm = decode(sec.raw_string(a["text"])).strip()
                    if nm and nm not in loc_names:
                        loc_names.append(nm)
        enc = encounters.parse(ff.section("encounter"))
        random_forms = sorted({e["formation"] for t in enc if t["enabled"] for e in t["normal"]})
        gates = triggers.gateways(ff.section("triggers")) if len(ff.section("triggers")) >= 0x158 else []
        for g in gates:
            links.append((name, names[g["field"]] if g["field"] < len(names) else "#%d" % g["field"],
                          "gateway", g["slot"]))
        for j in sorted(jumps):
            links.append((name, names[j] if j < len(names) else "#%d" % j, "script", ""))
        rows.append({
            "id": fid, "field": name, "location": " / ".join(loc_names),
            "entities": sec.n_entities, "texts": len(sec.string_offsets),
            "progress_checks": len(progress_values),
            "progress_min": min(progress_values) if progress_values else "",
            "progress_max": max(progress_values) if progress_values else "",
            "progress_sets": " ".join(str(v) for v in sorted(progress_writes)),
            "gateways": " ".join(names[g["field"]] if g["field"] < len(names) else "#%d" % g["field"]
                                 for g in gates),
            "exits": " ".join(names[j] if j < len(names) else "#%d" % j for j in sorted(jumps)),
            "scripted_battles": " ".join("%d:%s" % (b, enemies(b)) for b in sorted(battles)),
            "random_battles": " ".join("%d:%s" % (b, enemies(b)) for b in random_forms),
        })

    with open(os.path.join(INV_DIR, "fields.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(INV_DIR, "field_links.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["from", "to", "kind", "gateway_slot"])
        w.writerows(links)
    with open(os.path.join(INV_DIR, "scripted_battles.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["formation", "enemies", "max_level", "no_escape", "fields"])
        for fid in sorted(scripted):
            f = forms.get(fid)
            no_escape = f and not (f["setup"]["flags"] & 0x0004)
            w.writerow([fid, enemies(fid), max(f["levels"]) if f else "",
                        "yes" if no_escape else "", " ".join(sorted(scripted[fid]))])
    with open(os.path.join(INV_DIR, "formations.json"), "w", encoding="utf-8") as fh:
        json.dump(forms, fh, indent=1)
    write_locations(rows)
    write_worldmap(names)
    print("inventory: %d fields, %d scripted battle formations, %d links" %
          (len(rows), len(scripted), len(links)))


def write_locations(rows):
    """Group fields by their in-game location name (from MPNAM) into a Markdown table."""
    groups = collections.OrderedDict()
    for r in rows:
        loc = r["location"].split(" / ")[0] or "(no location name)"
        groups.setdefault(loc, []).append(r)
    lines = [
        "# Locations (generated)",
        "",
        "Generated by `tools/ff7tool.py inventory`. Fields are grouped by the location",
        "name the game displays. *Story checks* is the range of story-progress values",
        "(var[2][0]) the field's scripts compare against; *story sets* lists the values",
        "the field writes, i.e. the story moments that happen there.",
        "",
        "| Location | Field | Story checks | Story sets | Scripted battles |",
        "|---|---|---|---|---|",
    ]
    for loc, rs in sorted(groups.items(), key=lambda kv: kv[0].lower()):
        for r in rs:
            checks = "%s–%s (%s)" % (r["progress_min"], r["progress_max"], r["progress_checks"]) \
                if r["progress_checks"] else ""
            sets = r["progress_sets"]
            if len(sets) > 40:
                vals = sets.split()
                sets = "%s … %s (%d)" % (vals[0], vals[-1], len(vals))
            battles = r["scripted_battles"]
            if len(battles) > 80:
                battles = battles[:77] + "..."
            lines.append("| %s | `%s` | %s | %s | %s |" % (loc.replace("|", "/"), r["field"], checks, sets,
                                                         battles.replace("|", "/")))
    with open(os.path.join(INV_DIR, "locations.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


class BuildContext:
    """Handed to each patch module's apply(ctx). Tracks modified field files."""

    def __init__(self):
        self.flevel = LGP.read(os.path.join(GAME, "field", "flevel.lgp"))
        self.maplist = maplist()
        self._fields = {}
        self._kernel = None

    def field(self, name):
        """Return a mutable FieldFile for `name` (cached; saved at the end of the build)."""
        if name not in self._fields:
            self._fields[name] = FieldFile(lzss.decompress(self.flevel[name]))
        return self._fields[name]

    def script(self, name):
        return ScriptSection(self.field(name).sections[0])

    def set_script(self, name, data):
        self.field(name).sections[0] = bytes(data)

    def kernel_init(self):
        """Editable new-game data (KERNEL.BIN section 3); written by the build."""
        if self._kernel is None:
            from ff7.kernel import InitData, read_sections
            path = os.path.join(GAME, "lang-en", "kernel", "KERNEL.BIN")
            self._kernel_sections, self._kernel_tail = read_sections(open(path, "rb").read())
            self._kernel = InitData(self._kernel_sections[3]["data"])
        return self._kernel

    def kernel_growth(self):
        """KERNEL.BIN section 2 (battle and growth data), read-only."""
        self.kernel_init()
        return self._kernel_sections[2]["data"]

    def kernel_section(self, index):
        """Mutable bytearray of KERNEL.BIN section `index` (0 commands,
        1 attacks, 4 items, 8 materia, ...); written by the build."""
        self.kernel_init()
        if index == 3:
            return self._kernel.data
        self._kernel_edits = getattr(self, "_kernel_edits", {})
        if index not in self._kernel_edits:
            self._kernel_edits[index] = bytearray(self._kernel_sections[index]["data"])
        return self._kernel_edits[index]

    def kernel2(self):
        """Editable kernel2.bin (the text the game shows); written by the build."""
        if getattr(self, "_kernel2", None) is None:
            from ff7.kernel2 import Kernel2
            path = os.path.join(GAME, "lang-en", "kernel", "kernel2.bin")
            self._kernel2 = Kernel2(open(path, "rb").read())
        return self._kernel2

    def wm_file(self, name):
        """Mutable bytearray of a file in data/wm/world_us.lgp (e.g. "wm0.ev");
        the build writes world_us.lgp when any is touched."""
        if getattr(self, "_wm", None) is None:
            self._wm_lgp = LGP.read(os.path.join(GAME, "wm", "world_us.lgp"))
            self._wm = {}
        if name not in self._wm:
            self._wm[name] = bytearray(self._wm_lgp[name])
        return self._wm[name]

    def char_file(self, name, data=None):
        """data/field/char.lgp (field models): returns the file `name`; with
        `data`, adds or replaces it. The build writes char.lgp when any is set."""
        if getattr(self, "_char", None) is None:
            self._char_lgp = LGP.read(os.path.join(GAME, "field", "char.lgp"))
            self._char = {}
        if data is not None:
            self._char[name] = bytes(data)
        return self._char.get(name) or self._char_lgp[name]

    def exe(self):
        """ExeBuilder for ff7_en.exe (byte patches + the .openff7 section)."""
        if getattr(self, "_exe", None) is None:
            from ff7.exebuild import ExeBuilder
            self._exe = ExeBuilder(open(os.path.join(os.path.dirname(GAME), "ff7_en.exe"), "rb").read())
        return self._exe

    def save_extra(self, out_dir):
        """Write kernel2.bin and ff7_en.exe if patches touched them; returns paths."""
        out = []
        if getattr(self, "_kernel2", None) is not None:
            rel = "data/lang-en/kernel/kernel2.bin"
            with open(os.path.join(out_dir, rel), "wb") as fh:
                fh.write(self._kernel2.build())
            out.append(rel)
        if getattr(self, "_wm", None):
            for name, data in self._wm.items():
                self._wm_lgp[name] = bytes(data)
            rel = "data/wm/world_us.lgp"
            self._wm_lgp.write(os.path.join(out_dir, rel))
            out.append(rel)
        if getattr(self, "_char", None):
            for name, data in self._char.items():
                self._char_lgp[name] = data
            rel = "data/field/char.lgp"
            self._char_lgp.write(os.path.join(out_dir, rel))
            out.append(rel)
        if getattr(self, "_exe", None) is not None:
            rel = "ff7_en.exe"
            with open(os.path.join(out_dir, rel), "wb") as fh:
                fh.write(self._exe.build())
            out.append(rel)
        return out

    def save_kernel(self, out_dir):
        k2 = getattr(self, "_kernel2", None)
        if k2 is not None and k2.edits:
            # KERNEL.BIN keeps its own copy of the text (sections 9-26); mirror
            # every kernel2 edit there too, whichever copy the game shows.
            from ff7.kernel2 import Kernel2
            self.kernel_init()
            mirror = Kernel2.from_sections([self._kernel_sections[9 + i]["data"] for i in range(18)])
            for section, index, text in k2.edits:
                mirror.set(section, index, text)
            for i in range(18):
                self._kernel_edits = getattr(self, "_kernel_edits", {})
                self._kernel_edits[9 + i] = mirror.sections[i]
        if self._kernel is None:
            return False
        from ff7.kernel import build_sections
        self._kernel_sections[3]["data"] = bytes(self._kernel.data)
        for index, data in getattr(self, "_kernel_edits", {}).items():
            self._kernel_sections[index]["data"] = bytes(data)
        path = os.path.join(out_dir, "data", "lang-en", "kernel", "KERNEL.BIN")
        with open(path, "wb") as fh:
            fh.write(build_sections(self._kernel_sections, self._kernel_tail))
        return True

    def save(self):
        from ff7.models import ModelLoader
        for name, ff in self._fields.items():
            # The script header's model count (byte 3) must match the model
            # loader, or added NPCs get no proper actor (can't be talked to).
            n = len(ModelLoader(ff.section("models")).models)
            if n > 16:   # the engine's field model table (0xCC1670) holds 16
                raise SystemExit("BUILD CHECK FAILED: %s has %d models (max 16)" % (name, n))
            if ff.sections[0][3] != n:
                head = bytearray(ff.sections[0])
                head[3] = n
                ff.sections[0] = bytes(head)
            raw = ff.build()
            if raw != lzss.decompress(self.flevel[name]):
                self.flevel[name] = lzss.compress(raw)
        return [n for n in self._fields]


def exe_test(args):
    """Write build/exe_test/ff7_en.exe: the Steam exe with a new code section
    (exepatch.section_test) to test whether Steam accepts an added section."""
    from ff7 import exepatch
    src = os.path.join(os.path.dirname(GAME), "ff7_en.exe")
    out_dir = os.path.join(ROOT, "build", "exe_test")
    os.makedirs(out_dir, exist_ok=True)
    data = exepatch.section_test(open(src, "rb").read())
    out = os.path.join(out_dir, "ff7_en.exe")
    with open(out, "wb") as fh:
        fh.write(data)
    print("  Quit -> QUIT (static); new section .openff7 whose code turns Item into CAVE")
    print("wrote", out)


def api_index(args):
    """Regenerate docs/api_index.md (signatures + docstring summaries)."""
    from ff7 import apiindex
    with open(apiindex.path(), "w", encoding="utf-8") as fh:
        fh.write(apiindex.generate())
    print("wrote", apiindex.path())


def _verify_build(flevel_path):
    """Re-read the written flevel.lgp and check the new game is patched."""
    built = LGP.read(flevel_path)
    script = FieldFile(lzss.decompress(built["md1stin"])).sections[0]
    jump = bytes([0x60]) + maplist().index("mds7st3").to_bytes(2, "little")
    if jump not in script or b"\x0f\xfd" not in script:
        raise SystemExit("BUILD CHECK FAILED: md1stin has no openFF7 new-game block")
    print("check: md1stin new-game block present (SPCNM + jump to mds7st3)")


def build(args):
    """Apply patches/ and write the game folder to build/openFF7. All or nothing:
    patches run first, the folder is only replaced once everything succeeded
    (a failed build used to leave the original game files there)."""
    if not os.path.isdir(FIELD_DIR):
        extract()
    out = os.path.abspath(args.out)
    src = os.path.dirname(GAME)
    ctx = BuildContext()
    patch_dir = os.path.join(ROOT, "patches")
    sys.path.insert(0, patch_dir)  # lets patches `import _config`
    for path in sorted(glob.glob(os.path.join(patch_dir, "[0-9]*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("applying", os.path.basename(path))
        mod.apply(ctx)
    touched = ctx.save()
    tmp = out + ".partial"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    flevel = os.path.join(tmp, "data", "field", "flevel.lgp")
    ctx.flevel.write(flevel)
    changed = ["data/field/flevel.lgp"]
    if ctx.save_kernel(tmp):
        changed.append("data/lang-en/kernel/KERNEL.BIN")
    changed += ctx.save_extra(tmp)
    _verify_build(flevel)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.rename(tmp, out)
    print("built %s (%d field files touched)" % (out, len(touched)))
    print("changed game files (copy these into the game folder):")
    for path in changed:
        full = os.path.join(out, path)
        print("    %-35s %d bytes" % (path, os.path.getsize(full)))


WM_MODELS = {  # world map model ids (function id 0x4000 | model << 8 | n). UNVERIFIED: from community docs, some look wrong
    0: "Cloud", 1: "Tifa", 2: "Cid", 3: "Highwind", 4: "Wild chocobo", 5: "Tiny Bronco",
    6: "Buggy", 7: "Junon cannon", 8: "Cargo ship", 9: "Highwind propellers",
    10: "Diamond Weapon", 11: "Ultimate Weapon", 12: "Fort Condor", 13: "Submarine",
    14: "Gold Saucer", 15: "Rocket Town rocket", 16: "Rocket launch pad",
    17: "Sunken Gelnika", 18: "Underwater reactor", 19: "Chocobo", 20: "Midgar cannon",
    24: "Northern Crater barrier", 25: "Ancient Forest", 26: "Key of the Ancients",
    28: "Red submarine", 29: "Ruby Weapon", 30: "Emerald Weapon",
}


def _wm_function_name(fid):
    if fid < 0x4000:
        return "system %d" % fid
    if fid < 0x8000:
        model = (fid >> 8) & 0x3F
        return "model %d (%s) fn %d" % (model, WM_MODELS.get(model, "?"), fid & 0xFF)
    return "map cell 0x%04X" % fid


def write_worldmap(names):
    archive = LGP.read(os.path.join(GAME, "wm", "world_us.lgp"))
    table = field_table(archive["field.tbl"])
    lines = ["# World map (generated)", "",
             "Generated by `tools/ff7tool.py inventory` from `world_us.lgp`.", "",
             "## Entrances (field.tbl)", "",
             "Each world map location has entry A and B; the script picks one.",
             "Model names in the last column come from community docs and are not verified.", "",
             "| Entry | A | B | Called from (wm0.ev) |", "|---|---|---|---|"]
    ev = EvScript(archive["wm0.ev"])
    code = ev.disassemble()
    func_at = sorted((off, fid) for _i, fid, off in ev.functions() if fid != 0xFFFF)

    def func_of(pos):
        cur = None
        for off, fid in func_at:
            if off <= pos:
                cur = fid
        return cur

    callers = collections.defaultdict(set)
    for k, c in enumerate(code):
        if c.op == 0x318 and k >= 2 and code[k - 2].op == 0x110:
            callers[code[k - 2].arg].add(_wm_function_name(func_of(c.pos)))
    for i, (a, b) in enumerate(table):
        fa = names[a["field"]] if a["field"] < len(names) else a["field"]
        fb = names[b["field"]] if b["field"] < len(names) else b["field"]
        lines.append("| wm%d | `%s` | `%s` | %s |" % (i, fa, fb, "; ".join(sorted(callers.get(i, []))) or "—"))
    lines += ["", "## Story-progress checks in wm0.ev", "",
              "| Function | Check |", "|---|---|"]
    ops = {0x60: "<", 0x61: ">", 0x62: "<=", 0x63: ">=", 0x70: "==", 0x71: "!=", 0xE0: "= (write)"}
    for k, c in enumerate(code):
        if c.op == 0x11C and c.arg == 0 and k + 2 < len(code) and code[k + 1].op == 0x110:
            lines.append("| %s | progress %s %d |" % (_wm_function_name(func_of(c.pos)),
                                                     ops.get(code[k + 2].op, "?"), code[k + 1].arg))
    with open(os.path.join(INV_DIR, "worldmap.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def scenes(args):
    """Simulate entering each field of the last build (new-game state) and list
    signs of a cutscene. Approximate: see tools/ff7/simulate.py."""
    from ff7.simulate import State, simulate
    sys.path.insert(0, os.path.join(ROOT, "patches"))
    import _config
    built = LGP.read(os.path.join(ROOT, "build", "openFF7", "data", "field", "flevel.lgp"))
    state = State()
    for nibble, addr, bit in getattr(_config, "INITIAL_EVENT_FLAGS", []):
        state.bit(nibble, addr, bit, True)
    names = args.fields or [n for n in maplist()[1:] if n in built]
    for name in names:
        sec = FieldFile(lzss.decompress(built[name])).sections[0]
        if ScriptSection(sec).broken:
            continue
        rep = simulate(sec, state.copy())
        found = sorted(set(x for x in rep.summary() if "control locked" not in x))
        if found:
            print("%-10s %s" % (name, "; ".join(found[:5])))


DISC2 = 999  # story values from here on are disc 2/3; the open world uses disc 1 states


def plan_world(args):
    """Write patches/world_moments.json: a story moment for every field that has
    story checks and is not handled by a specific patch. Rule: just after the
    field's last disc 1 story event (or its highest disc 1 check), never equal
    to a value the field tests with ==. Overrides: patches/world_overrides.json."""
    import importlib.util
    rows = {r["field"]: r for r in csv.DictReader(open(os.path.join(INV_DIR, "fields.csv")))}
    handled = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "patches", "[0-9]*.py"))):
        spec = importlib.util.spec_from_file_location("p", path)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.join(ROOT, "patches"))
        spec.loader.exec_module(mod)
        for moment_fields in getattr(mod, "PINNED", {}).values():
            handled.update(moment_fields)
        handled.update(getattr(mod, "FIELDS", []))
    handled.update(["md1stin", "startmap"])
    plan = {}
    for name, r in rows.items():
        if name in handled or r["progress_checks"] == "0" or name.startswith("blackbg"):
            continue
        _, sec = load_field(name)
        checks, eq = set(), set()
        for _e, _si, code in field_scripts(sec):
            for ins in code:
                a = ins.args
                if ins.op in (0x16, 0x17, 0x18, 0x19) and (a["bank_a"], a["a"]) == PROGRESS_VAR \
                        and a["bank_b"] == 0:
                    checks.add(a["b"])
                    if a["cmp"] == 0:
                        eq.add(a["b"])
        sets = [int(v) for v in r["progress_sets"].split()]
        early_sets = [v for v in sets if v < DISC2]
        early_checks = [v for v in checks if v < DISC2]
        if early_sets:
            moment, why = max(early_sets) + 1, "after its last disc 1 event (%d)" % max(early_sets)
        elif early_checks:
            moment, why = max(early_checks) + 1, "after its highest disc 1 check (%d)" % max(early_checks)
        else:
            moment, why = DISC2 - 1, "disc 1 state (all its checks are disc 2+)"
        while moment in eq:
            moment += 1
        plan[name] = {"moment": moment, "location": r["location"].split(" / ")[0], "why": why}
    out = os.path.join(ROOT, "patches", "world_moments.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(plan, fh, indent=1, sort_keys=True)
    print("planned %d fields -> %s" % (len(plan), out))


def _with(base, bits):
    st = base.copy()
    for b in bits:
        st.bit(*b, True)
    return st


def quiet_flags(args):
    """Search 'seen' flags that silence entry scenes in every field of the last
    build, keep those that make no field worse, write patches/world_flags.json."""
    from ff7.simulate import State, find_quiet_flags, simulate
    sys.path.insert(0, os.path.join(ROOT, "patches"))
    import _config
    built = LGP.read(os.path.join(ROOT, "build", "openFF7", "data", "field", "flevel.lgp"))
    base = State()
    for n, a, b in _config.INITIAL_EVENT_FLAGS:
        base.bit(n, a, b, True)
    names = [n for n in maplist()[1:] if n in built and not n.startswith("blackbg")]
    secs = {n: FieldFile(lzss.decompress(built[n])).sections[0] for n in names}
    secs = {n: d for n, d in secs.items() if not ScriptSection(d).broken}
    names = [n for n in names if n in secs]

    def real(rep):
        return [x for x in rep.summary() if "control locked" not in x]

    # Characters with a recruitment talk script (MMBUD 01 in script 1) must stay visible.
    from ff7.script import Script as _Script
    recruits = {}
    for n in names:
        sc = _Script.parse(secs[n])
        for e, raw_name in enumerate(sc.entity_names):
            if any(o.op == 0xCD and o.raw[1] == 1 for o in sc.script_ops(e, 1)):
                recruits.setdefault(n, []).append(raw_name.split(b"\0")[0].decode("latin-1"))

    def hides_recruit(n, state):
        if n not in recruits:
            return False
        vis = simulate(secs[n], state.copy()).final_visible
        return any(not vis.get(r, True) for r in recruits[n])

    before = {n: len(real(simulate(secs[n], base.copy()))) for n in names}
    found = []
    for n in names:
        if not before[n]:
            continue
        bits, _b, after = find_quiet_flags(secs[n], base.copy())
        if bits and len(real(after)) < before[n]:
            found.extend(b for b in bits if b not in found)
    # Keep only flags that, all together, make no field worse.
    while True:
        st = base.copy()
        for b in found:
            st.bit(*b, True)
        worse = [n for n in names if len(real(simulate(secs[n], st.copy()))) > before[n]]
        hidden = [n for n in recruits if hides_recruit(n, st)]
        if hidden:
            # drop the flags that hide a recruit, one field at a time
            n = hidden[0]
            culprits = [b for b in found if hides_recruit(n, _with(base, [b]))]
            found = [b for b in found if b not in culprits] if culprits else found[:-1]
            continue
        if not worse:
            break
        # drop flags tested by the first worsened field and retry
        rep = simulate(secs[worse[0]], st.copy())
        tested = {(t[0], t[1], t[2]) for t in rep.tested_flags if t[2] >= 0}
        drop = [b for b in found if b in tested] or found[-1:]
        found = [b for b in found if b not in drop]
    after = sum(len(real(simulate(secs[n], st.copy()))) for n in names)
    out = os.path.join(ROOT, "patches", "world_flags.json")
    with open(out, "w") as fh:
        json.dump(sorted(found), fh, indent=0)
    print("%d flags; scene signals %d -> %d; wrote %s" % (len(found), sum(before.values()), after, out))


def reach(args):
    """For each given field of the last build: can each entrance reach each exit,
    with the triangles that are locked after entering (new-game state)?"""
    from ff7 import reach as rc, triggers as tg
    from ff7.simulate import State, simulate
    sys.path.insert(0, os.path.join(ROOT, "patches"))
    import _config
    import importlib
    built = LGP.read(os.path.join(ROOT, "build", "openFF7", "data", "field", "flevel.lgp"))
    names = maplist()
    state = State()
    flags = list(_config.INITIAL_EVENT_FLAGS)
    wf = os.path.join(ROOT, "patches", "world_flags.json")
    if os.path.exists(wf):
        flags += [tuple(b) for b in json.load(open(wf))]
    for n, a, b in flags:
        state.bit(n, a, b, True)
    # entrances: gateway destinations and map jumps from every field into the target
    into = collections.defaultdict(list)
    for src in names[1:]:
        if src not in built:
            continue
        ff = FieldFile(lzss.decompress(built[src]))
        for g in tg.gateways(ff.section("triggers")):
            if g["field"] < len(names):
                into[names[g["field"]]].append(("from " + src, g["dest_triangle"]))
    for field in args.fields:
        raw = lzss.decompress(built[field])
        rep = simulate(FieldFile(raw).sections[0], state.copy())
        res = rc.check(raw, rep.locked, into.get(field, []), names)
        bad = sorted({(e, x) for (e, x), ok in res.items() if not ok})
        print("%-9s locked %-28s %s" % (field, sorted(rep.locked)[:8],
              "all exits reachable" if not bad else "BLOCKED: " + "; ".join("%s -> %s" % b for b in bad[:6])))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("extract").set_defaults(func=extract)
    sub.add_parser("api-index").set_defaults(func=api_index)
    sub.add_parser("exe-test").set_defaults(func=exe_test)
    d = sub.add_parser("dump")
    d.add_argument("fields", nargs="*")
    d.add_argument("--all", action="store_true")
    d.add_argument("--built", action="store_true", help="dump the last build instead of the original")
    d.set_defaults(func=dump)
    sub.add_parser("inventory").set_defaults(func=inventory)
    sub.add_parser("wmdump").set_defaults(func=wmdump)
    rp = sub.add_parser("reach")
    rp.add_argument("fields", nargs="+")
    rp.set_defaults(func=reach)
    sub.add_parser("plan-world").set_defaults(func=plan_world)
    sub.add_parser("quiet-flags").set_defaults(func=quiet_flags)
    sc = sub.add_parser("scenes")
    sc.add_argument("fields", nargs="*")
    sc.set_defaults(func=scenes)
    b = sub.add_parser("build")
    b.add_argument("--out", default=os.path.join(ROOT, "build", "openFF7"))
    b.set_defaults(func=build)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

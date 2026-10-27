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
        self._orig_raw = {}
        self._kernel = None

    def field(self, name):
        """Return a mutable FieldFile for `name` (cached; saved at the end of the build)."""
        if name not in self._fields:
            raw = cached_decompress(self.flevel[name])
            self._orig_raw[name] = raw          # to tell changed fields apart at save time
            self._fields[name] = FieldFile(raw)
        return self._fields[name]

    def new_field(self, name, raw):
        """Add a field under `name` (a maplist name with no file in
        flevel.lgp, e.g. onna_1): it is written to flevel.lgp at save."""
        assert name in self.maplist and name not in self.flevel, name
        self._orig_raw[name] = None
        self._fields[name] = FieldFile(raw)
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
                if name not in self._char_lgp and name.endswith(".hrc"):
                    self._char_lgp.check[name] = 11      # every .hrc in char.lgp has TOC check 11 (others 14)
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
        changed = {}
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
            if raw != self._orig_raw[name]:
                changed[name] = raw
                _check_chars(name, ff.sections[0], n)
        for name, packed in compress_all(changed).items():
            self.flevel[name] = packed
        return [n for n in self._fields]


def _check_chars(name, script, models):
    """Every model is used by exactly one CHAR (true for all original fields):
    two entities sharing one (md8brdg's quest markers, 18 CHARs for 16
    models) crashed the game on arrival."""
    from ff7.script import Script
    try:
        sec = Script.parse(script)
    except ValueError:
        return
    chars = sorted(o.raw[1] for o in sec.ops if o.op == 0xA1)
    if chars != list(range(models)):
        raise SystemExit("BUILD CHECK FAILED: %s: CHAR models %s, %d models" % (name, chars, models))
    # (user: the workout's bench showed two Clouds) the engine hands out models in the order entities run their
    # CHAR, whatever its operand: entity k's CHAR must be the k-th model (true for all original fields)
    order = []
    for e in range(len(sec.entry)):
        try:
            ops = sec.script_ops(e, 0)
        except Exception:
            continue
        order += [o.raw[1] for o in ops if o.op == 0xA1][:1]
    if order != sorted(order):
        raise SystemExit("BUILD CHECK FAILED: %s: CHAR models out of entity order %s" % (name, order))


LZSS_CACHE = os.path.join(ROOT, "build", "cache", "lzss")
RAW_CACHE = os.path.join(ROOT, "build", "cache", "raw")


def cached_decompress(packed):
    """lzss.decompress of an original game file, cached on disk by content
    (the originals never change: every build after the first reads them back)."""
    import hashlib
    path = os.path.join(RAW_CACHE, hashlib.sha1(packed).hexdigest())
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        raw = lzss.decompress(packed)
        os.makedirs(RAW_CACHE, exist_ok=True)
        with open(path + ".tmp", "wb") as fh:
            fh.write(raw)
        os.replace(path + ".tmp", path)
        return raw


def compress_all(raws):
    """{name: raw} -> {name: LZSS bytes}. Compression is the slow part of a
    build (pure Python), so results are cached by content in build/cache/lzss
    (a field that didn't change since the last build costs nothing) and the
    rest are compressed on all CPU cores. Output is identical either way."""
    import hashlib
    os.makedirs(LZSS_CACHE, exist_ok=True)
    out, todo = {}, {}
    for name, raw in raws.items():
        path = os.path.join(LZSS_CACHE, hashlib.sha1(raw).hexdigest())
        if os.path.exists(path):
            with open(path, "rb") as fh:
                out[name] = fh.read()
        else:
            todo[name] = (raw, path)
    if todo:
        names = list(todo)
        jobs = [todo[n][0] for n in names]
        workers = min(len(jobs), os.cpu_count() or 1)
        if workers > 1:
            import multiprocessing
            with multiprocessing.Pool(workers) as pool:
                packed = pool.map(lzss.compress, jobs, chunksize=1)
        else:
            packed = [lzss.compress(j) for j in jobs]
        for name, data in zip(names, packed):
            with open(todo[name][1] + ".tmp", "wb") as fh:
                fh.write(data)
            os.replace(todo[name][1] + ".tmp", todo[name][1])
            out[name] = data
        print("compressed %d fields (%d from cache)" % (len(todo), len(raws) - len(todo)))
    return out


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
    out = os.path.abspath(args.out or os.path.join(ROOT, "build", "openFF7_debug" if args.debug else "openFF7"))
    src = os.path.dirname(GAME)
    ctx = BuildContext()
    patch_dir = os.path.join(ROOT, "patches")
    sys.path.insert(0, patch_dir)  # lets patches `import _config`
    paths = sorted(glob.glob(os.path.join(patch_dir, "[0-9]*.py")))
    if args.debug:   # patches/debug/: test tools, never in a normal build
        paths += sorted(glob.glob(os.path.join(patch_dir, "debug", "[0-9]*.py")))
    import time
    took, t_start = [], time.time()
    for path in paths:
        t0 = time.time()
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("applying", os.path.basename(path))
        mod.apply(ctx)
        took.append((time.time() - t0, os.path.basename(path)))
    t0 = time.time()
    touched = ctx.save()
    took.append((time.time() - t0, "(saving fields)"))
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
    print("built %s (%d field files touched) in %.0f s; slowest steps: %s" % (
        out, len(touched), time.time() - t_start, ", ".join("%s %.1f s" % (n, t) for t, n in sorted(took)[::-1][:6])))
    print("changed game files (copy these into the game folder):")
    for path in changed:
        full = os.path.join(out, path)
        print("    %-35s %d bytes" % (path, os.path.getsize(full)))
    if not args.no_install:
        install(out, changed)


GUARD = "FINAL FANTASY VII-openff7"     # (user) a folder of this name beside the game folder = don't install


def _steam_game_dirs():
    """Candidate Steam installs of the game: OPENFF7_GAME, install_path.txt (repo root), Steam's
    default libraries and the ones its libraryfolders.vdf lists."""
    out = []
    if os.environ.get("OPENFF7_GAME"):
        out.append(os.environ["OPENFF7_GAME"])
    cfg = os.path.join(ROOT, "install_path.txt")
    if os.path.exists(cfg):
        out += [l.strip() for l in open(cfg, encoding="utf-8") if l.strip() and not l.startswith("#")]
    steams = [os.path.expandvars(r"%ProgramFiles(x86)%\Steam"), os.path.expandvars(r"%ProgramFiles%\Steam"),
              r"C:\Program Files (x86)\Steam", os.path.expanduser("~/.steam/steam"),
              os.path.expanduser("~/.local/share/Steam")]
    libs = []
    for st in steams:
        libs.append(st)
        vdf = os.path.join(st, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            for line in open(vdf, encoding="utf-8", errors="replace"):
                w = line.strip().split('"')
                if len(w) >= 4 and w[1] == "path":
                    libs.append(w[3].replace("\\\\", "\\"))
    out += [os.path.join(lib, "steamapps", "common", "FINAL FANTASY VII") for lib in libs]
    return out


def install(out, changed):
    """(user) Copy the changed game files into the Steam game folder, unless a folder named GUARD sits
    beside it. Never into this repo's own game data (the build's read-only input)."""
    own = os.path.realpath(os.path.dirname(GAME))
    target = None
    for d in _steam_game_dirs():
        if os.path.isfile(os.path.join(d, "ff7_en.exe")) and os.path.realpath(d) != own:
            target = d
            break
    if target is None:
        print("install: no Steam game folder found (set OPENFF7_GAME or write its path in install_path.txt); "
              "not installed")
        return
    guard = os.path.join(os.path.dirname(os.path.abspath(target)), GUARD)
    if os.path.exists(guard):
        print("install: %s exists; not installed" % guard)
        return
    for path in changed:
        dst = os.path.join(target, *path.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(out, path), dst)
    print("installed %d file(s) into %s" % (len(changed), target))


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


def _same_model_file(name, a, b):
    """True if two char.lgp files hold the same model data, even when a model tool re-saved them with
    other bytes: .hrc / .rsd text compared line by line (stripped, case-blind, blank and # lines
    ignored), .a frames and .p vertices / colours / triangles compared with a small tolerance."""
    import math
    import struct
    from ff7 import fieldanim as fa
    if a == b:
        return True
    ext = name.lower().rsplit(".", 1)[-1]
    try:
        if ext in ("hrc", "rsd"):
            norm = lambda d: [l.strip().lower() for l in d.decode("latin-1").splitlines()
                              if l.strip() and not l.strip().startswith("#")]
            return norm(a) == norm(b)
        if ext == "a":
            fa_, fb_ = fa.Anim(a), fa.Anim(b)
            if (fa_.nframes, fa_.nbones) != (fb_.nframes, fb_.nbones):
                return False
            ang = lambda x, y: abs((x - y + 180) % 360 - 180) < 0.05
            for (r1, p1, b1), (r2, p2, b2) in zip(fa_.frames, fb_.frames):
                if not all(math.isclose(x, y, abs_tol=1e-3) for x, y in zip(p1, p2)):
                    return False
                if not all(ang(x, y) for u, v in zip([r1] + b1, [r2] + b2) for x, y in zip(u, v)):
                    return False
            return True
        if ext == "p":
            def parts(d):
                h = struct.unpack_from("<16I", d, 0)
                nv, nn, nu, nt, nc, ne, npoly = h[3], h[4], h[5], h[6], h[7], h[8], h[9]
                V = struct.unpack_from("<%df" % (3 * nv), d, 128)
                oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
                C = d[oc:oc + 4 * nc]
                op = oc + 4 * nc + 4 * npoly + 4 * ne
                P = [struct.unpack_from("<12H", d, op + 24 * j)[1:4] for j in range(npoly)]
                T = struct.unpack_from("<%df" % (2 * nt), d, 128 + 12 * nv + 12 * nn + 12 * nu)
                return (nv, nt, nc, npoly), V, T, bytes(C[k] for k in range(len(C)) if k % 4 != 3), P
            (ha, va, ta, ca, pa), (hb, vb, tb, cb, pb) = parts(a), parts(b)
            return (ha == hb and ca == cb and pa == pb
                    and all(math.isclose(x, y, abs_tol=1e-4) for x, y in zip(va + ta, vb + tb)))
    except (struct.error, ValueError, IndexError, UnicodeDecodeError):
        return False
    return False


def char_overrides(args):
    """Every file of an edited char.lgp (e.g. build/openFF7's, changed in a model tool) whose model data
    differs from the last build's (or isn't in it) -> patches/char_overrides/, which 990_char_overrides
    writes into char.lgp last on every build. Files a tool merely re-saved count as unchanged
    (`_same_model_file`). --only limits it to names matching the given patterns. Run `build` first so the
    comparison is with the current build."""
    import fnmatch
    mine = LGP.read(args.lgp)
    built = LGP.read(os.path.join(ROOT, "build", "openFF7", "data", "field", "char.lgp"))
    have = {n.lower(): n for n in built.names()}
    out = os.path.join(ROOT, "patches", "char_overrides")
    changed, new, resaved = [], [], 0
    for n in mine.names():
        low = n.lower()
        if args.only and not any(fnmatch.fnmatch(low, p.lower()) for p in args.only):
            continue
        data = mine[n]
        if low in have:
            old = built[have[low]]
            if old == data:
                continue
            if _same_model_file(low, old, data):
                resaved += 1
                continue
            changed.append(low)
        else:
            new.append(low)
        if not args.dry_run:
            with open(os.path.join(out, low), "wb") as fh:
                fh.write(data)
    by_ext = collections.Counter(n.rsplit(".", 1)[-1] for n in changed + new)
    print("%d changed, %d new, %d only re-saved by the tool (skipped)%s" % (
        len(changed), len(new), resaved, "; not written (--dry-run)" if args.dry_run else
        "; written to patches/char_overrides/"))
    if by_ext:
        print("by type: " + ", ".join("%s %d" % kv for kv in sorted(by_ext.items())))
    names = changed + new
    print(", ".join(names[:200]) + (" ... (%d more)" % (len(names) - 200) if len(names) > 200 else ""))


def lgp_pack(args):
    """(user) Pack loose model files (e.g. a 7th Heaven mod's unpacked `char` folder) over a base .lgp
    (default the original char.lgp) into a new .lgp, so a model tool that opens .lgp files sees them.
    Names are lower-cased as the game's; files with a base name replace it, others are added."""
    base = LGP.read(args.base or os.path.join(GAME, "field", "char.lgp"))
    have = {n.lower(): n for n in base.names()}
    files = sorted(f for f in os.listdir(args.folder) if os.path.isfile(os.path.join(args.folder, f)))
    if not files:
        subs = [d for d in os.listdir(args.folder) if os.path.isdir(os.path.join(args.folder, d))]
        sys.exit("no files in %s; point it at the folder holding the .hrc/.p/.tex files%s" % (
            args.folder, " (subfolders: %s)" % ", ".join(subs) if subs else ""))
    replaced, added = [], []
    for f in files:
        low = f.lower()
        if len(low.encode("ascii", "replace")) > 20:
            print("skipped (name over 20 characters): %s" % f)
            continue
        with open(os.path.join(args.folder, f), "rb") as fh:
            data = fh.read()
        if low in have:
            base[have[low]] = data
            replaced.append(low)
        else:
            if low.endswith(".hrc"):
                base.check[low] = 11      # every .hrc in char.lgp has TOC check 11 (others 14)
            base[low] = data
            added.append(low)
    base.write(args.out)
    print("%s: %d replaced, %d added" % (args.out, len(replaced), len(added)))
    if added:
        print("added: " + ", ".join(added[:100]) + (" ..." if len(added) > 100 else ""))


def save_usage(args):
    """Savemap banks 1-4: what the original game and the build use, what is free
    (whole bytes and spare bits), what the open world freed. -> work/save_usage.txt"""
    import hashlib
    from ff7 import saveuse
    sys.path.insert(0, os.path.join(ROOT, "patches"))
    import _config
    built_dir = os.path.join(ROOT, "build", "openFF7")
    paths = [os.path.join(built_dir, "data", "field", "flevel.lgp"),
             os.path.join(built_dir, "data", "wm", "world_us.lgp"), os.path.join(built_dir, "ff7_en.exe")]
    if not all(os.path.exists(p) for p in paths):
        sys.exit("no build in build/openFF7: run 'ff7tool.py build --no-install' first")

    def built_decompress(packed):          # unchanged fields come from the originals' cache
        path = os.path.join(RAW_CACHE, hashlib.sha1(packed).hexdigest())
        if os.path.exists(path):
            return open(path, "rb").read()
        return lzss.decompress(packed)

    print("scanning the original game ...")
    orig = saveuse.usage(LGP.read(os.path.join(GAME, "field", "flevel.lgp")),
                         LGP.read(os.path.join(GAME, "wm", "world_us.lgp")),
                         open(os.path.join(os.path.dirname(GAME), "ff7_en.exe"), "rb").read(),
                         cached_decompress)
    print("scanning the build ...")
    built = saveuse.usage(LGP.read(paths[0]), LGP.read(paths[1]), open(paths[2], "rb").read(),
                          built_decompress)
    nib = {1: 1, 3: 2, 11: 3, 13: 4}
    reserved = {(nib[n], o) for n, a, b in _config.QUEST_AREAS if n in nib for o in range(a, b + 1)}
    nibbles = {1: "1/2", 2: "3/4", 3: "11/12", 4: "13/14"}

    def who(e):
        parts = []
        for k, label in (("r", "read"), ("w", "write")):
            if e[k]:
                names = sorted(e[k])
                parts.append("%s %d (%s%s)" % (label, len(names), " ".join(names[:4]),
                                                " ..." if len(names) > 4 else ""))
        if e["wm"]:
            parts.append("world map %d" % e["wm"])
        if e["exe"]:
            parts.append("exe %s" % " ".join("%X" % v for v in e["exe"][:3]))
        if not e["whole"] and not e["wm"] and not e["exe"] and e["bits"]:
            parts.append("bits %s" % "".join(str(b) for b in sorted(e["bits"])))
        return "; ".join(parts)

    lines, summary = [], []
    for bank in (1, 2, 3, 4):
        lines.append("== savemap bank %d (field var nibbles %s; savemap 0x%04X) ==" % (
            bank, nibbles[bank], saveuse.BANK1 + 256 * (bank - 1)))
        counts = collections.Counter()
        free_runs, run = [], None
        for off in range(256):
            e = built.bytes[bank].get(off)
            used = built.used(bank, off)
            was = orig.used(bank, off)
            near = [o for o in range(max(0, off - saveuse.NEAR_EXE), off)
                    if (built.bytes[bank].get(o) or {}).get("exe")]
            if saveuse.known(bank, off):
                status = "used (known): " + saveuse.known(bank, off)
                counts["used"] += 1
                used = True
            elif (bank, off) in reserved:
                status = "reserved (_config.QUEST_AREAS)" + ("" if used else ", unused yet")
                counts["reserved"] += 1
            elif not used and near:
                status = "check: free in the scripts, %d bytes after an exe reference (a table?)" % (
                    off - near[-1])
                counts["check"] += 1
                used = True
            elif not used:
                status = "FREED (the original used it)" if was else "free"
                counts["freed" if was else "free"] += 1
            elif not e["r"] and not e["wm"] and not e["exe"]:
                status = "write-only: " + who(e)
                counts["write-only"] += 1
            else:
                spare = built.free_bits(bank, off)
                status = ("bits %s free: " % "".join(map(str, sorted(spare))) if spare else "used: ") + who(e)
                counts["part" if spare else "used"] += 1
            if not used and (bank, off) not in reserved:
                run = run or [off, off]
                run[1] = off
            elif run:
                free_runs.append(run)
                run = None
            lines.append("%3d  %s" % (off, status))
        if run:
            free_runs.append(run)
        lines.append("")
        summary.append("bank %d (nibbles %s): %d free (%d freed by the open world), %d write-only, "
                       "%d with spare bits, %d used, %d reserved, %d to check (after an exe reference)" % (
                           bank, nibbles[bank], counts["free"] + counts["freed"], counts["freed"],
                           counts["write-only"], counts["part"], counts["used"], counts["reserved"],
                           counts["check"]))
        summary.append("   free runs: " + ", ".join(
            "%d" % a if a == b else "%d-%d" % (a, b) for a, b in free_runs))
    if built.indirect:
        ind = collections.Counter(built.indirect)
        summary.append("indirect (SETX/GETX/SEARCHX index a bank at run time; check by hand): " + ", ".join(
            "%s %s bank %d x%d" % (f, o, b, n) for (f, o, b), n in sorted(ind.items())))
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, "save_usage.txt")
    with open(out, "w") as fh:
        fh.write("\n".join(summary) + "\n\n" + "\n".join(lines))
    print("\n".join(summary))
    print("wrote", out)


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
    co = sub.add_parser("char-overrides", help="save the files you changed in a char.lgp as overrides")
    co.add_argument("lgp", help="your edited char.lgp")
    co.add_argument("--dry-run", action="store_true", help="only list the changed files")
    co.add_argument("--only", nargs="+", metavar="PATTERN", help="only these names, e.g. zxtb.p 'zc*.p'")
    co.set_defaults(func=char_overrides)
    lp = sub.add_parser("lgp-pack", help="pack loose model files (a mod's char folder) over char.lgp")
    lp.add_argument("folder", help="the folder holding the files, e.g. an unpacked mod's char folder")
    lp.add_argument("out", help="the .lgp to write")
    lp.add_argument("--base", help="the .lgp to start from (default the original char.lgp)")
    lp.set_defaults(func=lgp_pack)
    sub.add_parser("save-usage", help="savemap bytes used / free in the original and the build").set_defaults(
        func=save_usage)
    b = sub.add_parser("build")
    b.add_argument("--out", help="default build/openFF7 (build/openFF7_debug with --debug)")
    b.add_argument("--no-install", action="store_true", help="don't copy the changed files into the Steam game folder")
    b.add_argument("--debug", action="store_true",
                   help="also apply patches/debug/ (L1+R1 debug menu in every field); writes build/openFF7_debug")
    b.set_defaults(func=build)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

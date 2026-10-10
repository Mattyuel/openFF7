#!/usr/bin/env python3
"""openFF7 command-line tool.

  ff7tool.py extract            Decompress all field files into work/field/
  ff7tool.py dump FIELD...      Write readable script dumps to work/scripts/FIELD.txt
  ff7tool.py dump --all
  ff7tool.py inventory          Write the field/boss inventory to docs/inventory/
  ff7tool.py build [--out DIR]  Apply patches/*.py and write a standalone game folder
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
    if not os.path.isdir(FIELD_DIR):
        extract()
    names = maplist()[1:] if args.all else args.fields
    out_dir = os.path.join(WORK, "scripts")
    os.makedirs(out_dir, exist_ok=True)
    ids = {n: i for i, n in enumerate(maplist())}
    for name in names:
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

    def field(self, name):
        """Return a mutable FieldFile for `name` (cached; saved at the end of the build)."""
        if name not in self._fields:
            self._fields[name] = FieldFile(lzss.decompress(self.flevel[name]))
        return self._fields[name]

    def script(self, name):
        return ScriptSection(self.field(name).sections[0])

    def set_script(self, name, data):
        self.field(name).sections[0] = bytes(data)

    def save(self):
        for name, ff in self._fields.items():
            raw = ff.build()
            if raw != lzss.decompress(self.flevel[name]):
                self.flevel[name] = lzss.compress(raw)
        return [n for n in self._fields]


def build(args):
    if not os.path.isdir(FIELD_DIR):
        extract()
    out = os.path.abspath(args.out)
    src = os.path.dirname(GAME)
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(src, out)
    ctx = BuildContext()
    patch_dir = os.path.join(ROOT, "patches")
    for path in sorted(glob.glob(os.path.join(patch_dir, "*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("applying", os.path.basename(path))
        mod.apply(ctx)
    touched = ctx.save()
    ctx.flevel.write(os.path.join(out, "data", "field", "flevel.lgp"))
    print("built %s (%d field files touched)" % (out, len(touched)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("extract").set_defaults(func=extract)
    d = sub.add_parser("dump")
    d.add_argument("fields", nargs="*")
    d.add_argument("--all", action="store_true")
    d.set_defaults(func=dump)
    sub.add_parser("inventory").set_defaults(func=inventory)
    b = sub.add_parser("build")
    b.add_argument("--out", default=os.path.join(ROOT, "build", "openFF7"))
    b.set_defaults(func=build)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

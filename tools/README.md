# openFF7 tools

Python 3 tools for reading and rebuilding the Steam PC version of Final Fantasy VII.
Game data is read from `FINAL FANTASY VII/data/` in the repo root. Nothing is
installed; standard library only.

```
python3 tools/ff7tool.py extract          # decompress all field files to work/field/
python3 tools/ff7tool.py dump md1stin     # readable script dump -> work/scripts/md1stin.txt
python3 tools/ff7tool.py dump --all       # dump every field
python3 tools/ff7tool.py dump --built F   # dump a field from the last build -> work/scripts_built/
python3 tools/ff7tool.py api-index        # regenerate docs/api_index.md (tests check it is current)
python3 tools/ff7tool.py inventory        # regenerate docs/inventory/
python3 tools/ff7tool.py wmdump           # world map script dumps -> work/worldmap/
python3 tools/ff7tool.py build            # apply patches/*.py -> build/openFF7/
python3 tools/ff7tool.py scenes FIELD...  # simulate entering built fields, list likely cutscenes
python3 tools/ff7tool.py reach FIELD...   # can each entrance walk to each exit (locked floor)?
python3 tools/tests/test_formats.py       # format round-trip checks (~1 min)
```

`work/` and `build/` are generated and git-ignored.

## Modules (`tools/ff7/`)

| Module | Format |
|---|---|
| `lgp.py` | LGP archives (`flevel.lgp`, `char.lgp`, `world_us.lgp`, ...). Rebuilds unmodified archives byte-identically. Archives with directory entries (`magic.lgp`) are not supported yet. |
| `lzss.py` | FF7 LZSS compression used by field files. |
| `field.py` | Field file sections and the script/dialogue section header. |
| `opcodes.py` | Field script opcode table (validated: all 699 scripted fields disassemble exactly, all 38,046 jumps land on instructions). |
| `disasm.py` | Disassembler with decoded operands for conditions, variables, map jumps, battles, items, messages. |
| `text.py` | FF7 text encoding: `decode` to readable text, `encode` back (names, choices, colours). |
| `encounters.py` | Field random encounter tables. |
| `scene.py` | `scene.bin` battle formations and enemy names. |
| `script.py` | Editable script model and assembler: insert/remove/replace instructions (jumps and entry points are relocated), add entities, dialogue strings and music blocks. |
| `asm.py` | Constructors for new instructions (variables, conditions, map jumps, party, items, battles). |
| `triggers.py` | Walk-off gateways (room exits): read, add or change them. |
| `walkmesh.py` | Walkable floor triangles: find the triangle at a point, boundary edges. |
| `worldmap.py` | World map scripts (`.ev`) and the world map -> field entrance table (`field.tbl`). |
| `patch.py` | Patch helpers: `localise_progress` pins a field to a story moment or moves it to a region variable (see `DESIGN.md` §2). |
| `kernel.py` | `KERNEL.BIN` sections and the new-game data (characters, party, items). |
| `models.py` | Field model loader (which character models a field loads); copy a model between fields. |
| `simulate.py` | Rough simulation of entering a field (init + main scripts, REQ calls) to detect entry cutscenes, and `find_quiet_flags` to search for event flags that suppress them. |
| `reach.py` | Walkmesh reachability between a field's entrances and exits, given locked triangles. |
| `varscan.py` | Which save variables the original scripts use. |
| `apiindex.py` | Generates `docs/api_index.md` (signatures + docstring summaries). |

## Variables

Script variables are shown as `var[bank][address]` using the bank nibble from the
opcode. `var[2][0]` is the main story-progress value (the "Game Moment"); 391 of
the 702 fields compare against it.

## Not covered yet

Editing world map scripts (reading works), battle AI scripts, model
conversion, and checking that the built folder starts outside the Steam
install (see `docs/exe_notes.md`).

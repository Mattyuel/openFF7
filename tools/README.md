# openFF7 tools

Python 3 tools for reading and rebuilding the Steam PC version of Final Fantasy VII.
Game data is read from `FINAL FANTASY VII/data/` in the repo root. Nothing is
installed; standard library only.

```
python3 tools/ff7tool.py extract          # decompress all field files to work/field/
python3 tools/ff7tool.py dump md1stin     # readable script dump -> work/scripts/md1stin.txt
python3 tools/ff7tool.py dump --all       # dump every field
python3 tools/ff7tool.py inventory        # regenerate docs/inventory/
python3 tools/ff7tool.py wmdump           # world map script dumps -> work/worldmap/
python3 tools/ff7tool.py build            # apply patches/*.py -> build/openFF7/
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
| `text.py` | FF7 text encoding -> readable text. |
| `encounters.py` | Field random encounter tables. |
| `scene.py` | `scene.bin` battle formations and enemy names. |
| `script.py` | Editable script model and assembler: insert/remove/replace instructions; jumps and entry points are relocated automatically. |
| `asm.py` | Constructors for new instructions (variables, conditions, map jumps, party, items, battles). |
| `triggers.py` | Walk-off gateways (room exits). |
| `worldmap.py` | World map scripts (`.ev`) and the world map -> field entrance table (`field.tbl`). |
| `patch.py` | Patch helpers, e.g. `pin_progress` (see `DESIGN.md` §2). |

## Variables

Script variables are shown as `var[bank][address]` using the bank nibble from the
opcode. `var[2][0]` is the main story-progress value (the "Game Moment"); 391 of
the 702 fields compare against it.

## Not covered yet

Editing world map scripts (reading works), kernel/new-game data, battle AI
scripts, model conversion, and checking that the built `.exe` starts without the
Steam launcher.

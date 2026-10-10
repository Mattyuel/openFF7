# Patches

Each `*.py` file here is applied in name order by `tools/ff7tool.py build`.
A patch module defines `apply(ctx)`; `ctx` is a `BuildContext` (see `tools/ff7tool.py`):

- `ctx.script(name)` returns a parsed `ScriptSection` for a field
- `ctx.set_script(name, data)` replaces a field's script section
- `ctx.field(name)` returns the mutable `FieldFile`

Number files to control order, e.g. `010_new_game.py`, `100_midgar.py`.

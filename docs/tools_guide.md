# Using the openFF7 tools

This guide covers what each tool does, when to use it, and the everyday ways they fit together.
Everything runs from the repo folder with plain Python 3. Nothing needs installing.

## The big picture

```
 FINAL FANTASY VII/          patches/*.py              build/openFF7/
 (the original game,   -->   (our changes, applied --> (the files you copy
  never edited)               in file-name order)       into Steam)
```

You never edit game files by hand. Every change is a small Python file in `patches/`. The build
starts from the untouched game each time and replays every patch on top. So a bad change is
undone by deleting or fixing its patch and building again.

`work/` and `build/` are scratch output. They are safe to delete at any time.

## The everyday loop

```
python3 tools/ff7tool.py build          # 1. build (about 12 s once the cache is warm)
#   copy the listed files into Steam    # 2. install (TESTING.md section 2)
#   play, note what's wrong             # 3. test
python3 tools/tests/test_formats.py     # 4. before committing: every check passes
```

The build prints which game files changed and their sizes. Copy exactly those files.

## The commands

### `build`: make the game files

```
python3 tools/ff7tool.py build            # -> build/openFF7/
python3 tools/ff7tool.py build --debug    # -> build/openFF7_debug/, with the debug menu
```

- The first build takes about 2 minutes, while it decompresses every field into
  `build/cache/`. Later builds take about 12 s.
- **`--debug`** adds an L1+R1 menu to almost every field. It has fast travel, +100,000 gil,
  encounters off/on and feature shortcuts. Use it to reach the thing you're testing without
  replaying the game. A normal build never contains it.
- If a patch's `assert` fails, the build stops with that message. That is deliberate: it means
  an assumption about the game data was wrong, and the build stops instead of shipping something
  broken.

### `dump`: read a field's script as text

```
python3 tools/ff7tool.py dump elm            # the original  -> work/scripts/elm.txt
python3 tools/ff7tool.py dump --built elm    # after our patches -> work/scripts_built/elm.txt
python3 tools/ff7tool.py dump --all          # every field (takes a while)
```

This is the most useful tool for understanding the game. Each field's entities and their scripts
come out as readable opcodes, with dialogue shown next to the line that shows it:

```
## entity 0 'tobira1' script 0
  BGON 00 01 00
  ...
  MAPJUMP field=340 x=50 y=-83 triangle=6 dir=0    ; -> elmtow
  MESSAGE window=1 text=21    ; "{BARRET} / “This is Kalm.”"
```

**Tip:** dump the original and the built version of the same field, then diff them to see exactly
what our patches changed there:

```
diff work/scripts/elm.txt work/scripts_built/elm.txt
```

### `scenes`: will a cutscene play when I walk in?

```
python3 tools/ff7tool.py scenes elm mds7 md1stin
```

This simulates entering each built field and flags scripts that look like story scenes. Run it
after pinning a field to a story moment, to check you didn't land on an arrival scene.

It only catches scenes that play **on entry**. A scene started by walking over a line (Kalm's
arrival is one) has to be found by reading the dump.

### `reach`: can the player walk from each entrance to each exit?

```
python3 tools/ff7tool.py reach elm sbwy4_1
elm       locked []                           all exits reachable
```

Some scripts lock patches of floor (IDLCK). Run this after moving an exit or an NPC to check
nothing became unreachable.

### `inventory` and `docs/inventory/`: where is everything?

`python3 tools/ff7tool.py inventory` regenerates the reference tables. Most of the time you just
**read** them:

| File | Answers |
|---|---|
| `fields.csv` | every field: id, location name, entity and text counts, story-moment range, exits, battles |
| `field_links.csv` | which field leads to which (gateways and scripted jumps) |
| `locations.md` | fields grouped by place |
| `scripted_battles.csv` | fixed battles: formation, enemies, where they happen |
| `worldmap.md` | world map entrances |

Use it to answer things like "what's Kalm's inn called internally?" (grep `fields.csv` for
`Kalm`) or "how full is this field's text table?" (the `texts` column; the limit is 255).

### `wmdump`: world map scripts

`python3 tools/ff7tool.py wmdump` writes the world map's scripts to `work/worldmap/`. Read these
when a change involves vehicles, chocobos or entering fields from the world map.

### `quiet-flags` and `plan-world`: research helpers

- `quiet-flags`: searches for new-game flags that silence entry scenes. It is slow (over
  10 minutes), so run it in the background.
- `plan-world`: proposes a story moment for every field not yet pinned.

You rarely need either now. They were used to set up the open world.

### `api-index`: the list of every helper

`python3 tools/ff7tool.py api-index` regenerates `docs/api_index.md`, one line per function and
class in `tools/ff7/` and `patches/`. **Search this first** when you want to do something: there
is usually a helper already. The tests fail if it's out of date, so run it after changing code.

### `exe-test`

Writes a harmless test copy of `ff7_en.exe` to `build/exe_test/`. It was used once to prove that a
modified exe runs through Steam. You won't normally need it.

### The tests

```
python3 tools/tests/test_formats.py     # about 2 minutes
```

The tests check that every file format round-trips byte for byte, that the field limits hold
(16 models, 255 texts and so on), and that the API index is current. Run them before every commit.

`tools/tests/emu_quest_menu.py` runs the custom exe code (the Quests menu, bounties) in an
emulator. It only works if the `unicorn` package is installed.

## Writing a patch: a worked example

This file, saved as `patches/995_hello_kalm.py`, adds an old man to Kalm's square who says one
line. (It was run against the game data while this guide was written.)

```python
"""Example: an old man in Kalm's square who says one line."""
from _recruit import say
from _travel import add_npc
from ff7 import asm
from ff7.camera import Camera, facing_screen
from ff7.models import ModelLoader
from ff7.walkmesh import Walkmesh

FIELD = "elm"            # Kalm's square (look names up in docs/inventory/fields.csv)
AT = (-305, 760)         # a floor point, in field units


def apply(ctx):
    f = ctx.field(FIELD)
    mesh = Walkmesh(f.section("walkmesh"))
    x, y = AT
    tri = mesh.find(x, y)                                   # which floor triangle is this?
    assert tri is not None, ("not on the floor", x, y)      # fail the build, don't guess
    pos = (x, y, round(mesh.height(tri, x, y)), tri)
    loader = ModelLoader(f.section("models"))
    model = 1                                               # reuse a model the field already loads
    face = facing_screen(Camera(f.sections[1]), *pos[:3], (0, 1))   # face the camera
    talk = lambda sec: say(sec, "Old man\n“Welcome to Kalm, young man.”") + [asm.ret()]
    add_npc(ctx, FIELD, "hello", model, pos, face, talk)
    print("  995: hello NPC in %s at %s (%d models)" % (FIELD, pos, len(loader.models)))
```

Things to notice:

- **`apply(ctx)`** is the only thing a patch must have. `ctx.field(name)` gives the field to edit.
  The build saves every field you touched.
- **The number in the file name sets the order.** Later patches see earlier patches' edits. Pick a
  number after anything your patch depends on.
- **Assert what you expect.** The first spot tried for this example, (0, 0), wasn't floor in Kalm.
  The assert stopped the build instead of putting an NPC in a wall.
- **Print a line.** The build output then shows your patch ran, and with what.
- Then run `build`, then `dump --built elm`, and look for the new entity `hello` at the end.

### The helpers you'll use most

| To... | Use |
|---|---|
| add an NPC with a talk script | `_travel.add_npc` (or `reuse_npc` in a field already at 16 models) |
| show a line of dialogue | `_recruit.say(sec, text)` |
| offer a choice menu | `620_honey_bee._ask`, or the recruit/travel menus in `_travel` |
| add a walk-over line (a trigger) | `_travel.add_line`, `_travel.line_across` |
| stand something beside a point | `_travel.beside` |
| test or set save variables | `ff7.asm.if_byte`, `setbyte`, `biton`, `bitoff` |
| jump to another field | `ff7.asm.mapjump` (the point must be inside the triangle you name) |
| pin a field to a story moment | `ff7.patch.localise_progress(sec, const=M)` (see `300_kalm.py`) |
| copy a model from another field | `ModelLoader.add_from(donor, i)` (it rescales for you) |
| find a floor point or its height | `Walkmesh.find`, `Walkmesh.height` |
| see where a point lands on screen | `ff7.camera.Camera(...).project(x, y, z)` |

`300_kalm.py` is the smallest real patch. It is 15 lines and a good first read.

## Recipes

**"I want to change what an NPC says."**
`dump` the field and find the `MESSAGE` with the text. Note its `text=` id. Write a patch that
replaces that string in the field's text table, or swaps the MESSAGE for a `say(...)` of your own.

**"Something in-game is wrong and I don't know which patch did it."**
Diff `work/scripts/FIELD.txt` against `work/scripts_built/FIELD.txt`. Every changed line came from
a patch. Then grep `patches/` for the field name.

**"Where should I put a new NPC?"**
Find the field in `fields.csv`. Check its model count (16 is the hard limit) and its text count
(255 is the limit). Pick a floor point with `Walkmesh.find`. Check it's on screen with
`Camera.project`: some floors run past the visible background.

**"I want to start a fresh test quickly."**
Build with `--debug`, start a new game, and use L1+R1 to jump straight to the field you're
testing.

**"The build is slow or acting strange."**
Delete `build/cache/` (about 350 MB). The next build recreates it, with byte-identical output.

## Limits to keep in mind

These come up constantly. CLAUDE.md has the details.

- **16 models per field.** More corrupts memory. The build refuses it.
- **255 texts per field.** Text ids are one byte. Fields near the limit need NPCs placed next door.
- **64 KB of script per field.**
- **47 animations per model** at most, the most the original game ever uses.
- **A MAPJUMP's point must lie in the triangle it names.** Check with `Walkmesh.contains`.
- **Put `UC 00` (give back control) before any jump out of a menu,** or the next field can freeze
  the player.

## Where to look next

| For | Read |
|---|---|
| what's been verified the hard way, and every trap | `CLAUDE.md` |
| what each patch does | the patch map in `CLAUDE.md` |
| every function's signature | `docs/api_index.md` |
| what to test in-game, and how to install | `TESTING.md` |
| the file formats and modules | `tools/README.md` |

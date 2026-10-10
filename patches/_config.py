"""Shared openFF7 settings used by the patch modules."""

# Story-progress value (var[2][0]) held globally during open-world play.
# Fields are pinned to their own moments (see 100_midgar.py), so this mainly
# affects the world map and fields not yet pinned. Revisit when the world map
# is opened up.
OPEN_WORLD_PROGRESS = 100

# Menu visibility mask (var[2][28]). Original new game: 763; Seventh Heaven
# later sets 0xFEFF (everything except PHS); Kalm adds 0x0100 (PHS).
MENU_ALL = 0xFFFF

# Character ids used by party/PHS opcodes.
CLOUD, BARRET, TIFA, AERITH, RED_XIII, YUFFIE, CAIT_SITH, VINCENT, CID = range(9)

# New game start: Sector 7 station, street level in front of the platform
# (walkmesh triangle 23). The original train arrival spot (triangle 26) is on
# the train-door trigger line and made Cloud board the train.
START_FIELD = "mds7st3"
START_X, START_Y, START_TRIANGLE, START_DIR = -2940, 2562, 23, 0

# ---------------------------------------------------------------------------
# openFF7 save variables. Bank 4 (opcode nibbles 13 = 8-bit, 14 = 16-bit),
# offsets 224-255 (savemap 0x0F84-0x0FA3), are not used by any field or world
# map script in the original game (checked by tools/tests/test_formats.py).
# Whether the .exe uses them is not yet verified.
OPEN_VAR_BANK8, OPEN_VAR_BANK16 = 13, 14
OPEN_VARS_FIRST = 224

# Regions that keep their own story line in a private 16-bit variable
# (reads/writes of story progress in their fields are redirected to it).
# name -> (variable, initial value at new game)
REGION_VARS = {}

# Shinra HQ keycards, all given at new game so the building can be explored
# freely. Elevator access level is var[1][224]; the cards are key-item bits.
HQ_ACCESS_LEVEL = ((1, 224), 68)
HQ_KEYCARD_BITS = [((1, 67), 6),   # Keycard 60
                   ((1, 67), 7),   # Keycard 62
                   ((1, 68), 0),   # Keycard 65
                   ((1, 68), 1),   # Keycard 66
                   ((1, 68), 2)]   # Keycard 68

# openFF7 event flags: one byte of bits at bank 4 offset 240 (8-bit nibble 13).
FLAGS = (OPEN_VAR_BANK8, 240)
FLAG_CORNEO_FLED = 0  # Corneo ran from his bedroom; he appears in Wutai instead

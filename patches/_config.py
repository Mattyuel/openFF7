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

# Event flags set at new game so rooms behave as if their story scenes were
# already seen (found with tools/ff7/simulate.py: find_quiet_flags, then
# checked together across every pinned Midgar field). (nibble, addr, bit).
INITIAL_EVENT_FLAGS = [
    (3, 208, 0),   # mds7plr1: Sector 7 slums entrance - AVALANCHE run-in seen
    (3, 214, 5),   # mds7pb_2: AVALANCHE hideout entry scene seen
    (3, 211, 2),   # mds7pb_1: 7th Heaven - Marlene greeting seen
    (3, 129, 7),   # tunnel_1: Sector 4 tunnel - Barret/Tifa scene seen
    (3, 128, 0),   # tunnel_2: tunnel - Cloud scene seen
    (3, 220, 6),   # onna_4: Honey Bee Inn room scene seen
    (3, 163, 0),   # colne_5: Corneo's hall audition done (hall Corneo hidden)
    (3, 168, 5),   # md0: Sector 0 arrival scene seen
    (3, 168, 6),   # sinbil_1: Shinra HQ entrance scene seen
    (3, 163, 4),   # blinst_1: HQ stairs start scene seen
    (3, 163, 5),   # blinst_2/3: HQ stairs climbing scenes seen
    (3, 172, 4),   # blin60_1: HQ 60f sneaking scene seen
    (3, 181, 0),   # blin65_2: HQ 65f model room scene seen
    (1, 226, 7),   # blin671b/673b: HQ 67f Red XIII state
    (3, 18, 6),    # chrin_1a: church - flower kids scene seen
    (3, 18, 7),    # chrin_1a: church - Aerith flower-bed scene seen
]

# Batteries for the Wall Market wire climb: item 85 x3, plus the three
# "battery held" bits the Wall Market weapon store sets when you buy them.
BATTERIES_ITEM, BATTERIES_QTY = 85, 3
BATTERY_BITS = [((1, 165), 5), ((1, 165), 6), ((1, 165), 7)]

# Recruited characters: one bit per character id in this byte (8-bit, bank 4).
RECRUITED = (OPEN_VAR_BANK8, 241)

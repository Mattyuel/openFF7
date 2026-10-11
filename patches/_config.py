"""Shared openFF7 settings used by the patch modules."""

# Story-progress value (var[2][0]) held globally during open-world play.
# Fields are pinned to their own moments (see 100_midgar.py), so this mainly
# affects the world map and fields not yet pinned. Revisit when the world map
# is opened up.
OPEN_WORLD_PROGRESS = 100

# Menu visibility mask (var[2][28]). Original new game: 763; Seventh Heaven
# later sets 0xFEFF (everything except PHS); Kalm adds 0x0100 (PHS).
MENU_ALL = 0xFFFF
MENU_PHS = 0x0100
# The PHS can only be left with exactly 3 in the party (ff7_en.exe 0x700c22),
# so its menu entry stays hidden until 3 characters are recruited (counted in
# RECRUIT_COUNT, shown by recruit_talk); fields that show it are neutralised.
MENU_START = MENU_ALL & ~MENU_PHS
# Menu locking mask (var[2][30]): a set bit greys an entry out. 0x0100 is PHS,
# 0x0200 Save. Midgar's save points set 0x0100 (no PHS yet); 900_phs.py clears it.
MENU_LOCK = (2, 30)
PHS_LOCK_BIT = 0x0100

# Cloud's starting level (stats recomputed from the game's growth curves).
CLOUD_START_LEVEL = 1

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
# BUT the exe's world map code zeroes savemap 0x0F8C-0x0F97 (offsets 232-243)
# on world map entry (0x766C7A) and writes world map object data to 244-255,
# so only offsets 224-231 are safe for openFF7 (no exe reference found).
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

# openFF7 event flags: one byte of bits at bank 4 offset 224 (8-bit nibble 13).
FLAGS = (OPEN_VAR_BANK8, 224)
FLAG_GUARD_SCORPION = 1   # Guard Scorpion beaten (No.1 Reactor core)
FLAG_AIR_BUSTER = 2       # Air Buster beaten (No.5 Reactor bridge)
FLAG_IN_REACTOR5 = 3      # last reactor room entered was No.5's (the elevator is shared)
FLAG_TAME_MATERIA = 4     # Tame materia picked up (Sector 6 playground)

# Event flags set at new game so rooms behave as if their story scenes were
# already seen (found with tools/ff7/simulate.py: find_quiet_flags, then
# checked together across every pinned Midgar field). (nibble, addr, bit).
INITIAL_EVENT_FLAGS = [
    (3, 208, 0),   # mds7plr1: Sector 7 slums entrance - AVALANCHE run-in seen
    (3, 214, 5),   # mds7pb_2: AVALANCHE hideout entry scene seen
    (3, 211, 2),   # mds7pb_1: 7th Heaven - Marlene greeting seen
    (3, 129, 7),   # tunnel_1: Sector 4 tunnel - Barret/Tifa scene seen
    (3, 128, 0),   # tunnel_2: tunnel - Cloud scene seen
    (3, 128, 1),   # elm: Kalm arrival ("everyone's waiting at the inn", party leaves) seen
    (13, 133, 3),  # world map: "Saving on the World Map" tutorial seen (wm0.ev bit 0x1C2B)
    (1, 122, 2),   # world map: submarine tutorial seen (wm0.ev bit 0x3D2)
    (13, 134, 1),  # world map: submarine tutorial (second copy) seen (wm0.ev bit 0x1C31)
    (3, 220, 6),   # onna_4: Honey Bee Inn room scene seen
    (3, 163, 0),   # colne_5: Corneo's hall audition done (hall Corneo hidden)
    (3, 162, 3),   # colne_4: dungeon - Tifa/Aerith meeting done (lines off, Tifa gone)
    (3, 163, 3),   # colne_3: right-hand room - lackey fight done
    (3, 163, 1),   # colne_6: Corneo's bedroom scene done - Corneo, dressed
                   #   Aerith/Tifa and disguised Cloud all gone from the mansion
    (3, 162, 7),   # colne_2/colne_4: escape done - no Aerith "No---!! Help!!"
                   #   scene at the office door, no Kotch chase line in the dungeon
    (3, 163, 2),   # colne_4: Kotch gone from the dungeon
    (15, 38, 3),   # mds5_5: Sector 5 gate opened with the key (Midgar exit unlocked)
    (1, 67, 5),    # Key item: Key to Sector 5
    (1, 225, 3),   # nmkin_1: No.1 Reactor gate opened (Biggs' code)
    (1, 225, 4),   # nmkin_1: No.1 Reactor second door opened
    (1, 226, 1),   # nmkin_1: No.1 Reactor button door - Barret's lines seen
    (3, 168, 5),   # md0: Sector 0 arrival scene seen
    (3, 168, 6),   # sinbil_1: Shinra HQ entrance scene seen
    (3, 163, 4),   # blinst_1: HQ stairs start scene seen
    (3, 163, 5),   # blinst_2/3: HQ stairs climbing scenes seen
    (3, 172, 4),   # blin60_1: HQ 60f sneaking scene seen
    (3, 181, 0),   # blin65_2: HQ 65f model room scene seen
    (1, 226, 7),   # blin671b/673b: HQ 67f Red XIII state
    (3, 18, 6),    # chrin_1a: church - flower kids scene seen
    (3, 18, 7),    # chrin_1a: church - Aerith flower-bed scene seen
    # One-off scenes outside Midgar not keyed on story progress (audit of LINE /
    # world map triggers; wm bit 0xE78+n = bank 2 offset 207 bit n):
    (3, 207, 3),   # wm0 map cell 0xAA23 -> sichi: Midgar Zolom impaled scene seen
    (3, 207, 1),   # wm0: buggy broke down near Cosmo Canyon (0xE79) ...
    (3, 207, 2),   #   ... and was repaired (0xE7A); bit 1 alone = buggy stays broken
    (3, 20, 2),    # nivl_3: Nibelheim arrival scene (LINE F_NIVL) seen
    (1, 128, 0),   # ropest: Barret's North Corel flashback (LINE evline2) seen
    (15, 177, 1),  # itown1a: Mideel arrival line (Tifa) off
    (3, 132, 2),   # gongaga: "A ruined reactor." pan seen
    (3, 129, 4),   # gnmk: Gongaga reactor line seen
    (1, 130, 0),   # snow: Icicle Inn Elena ambush (LINE snowbd) done ...
    (1, 130, 7),   #   ... and its aftermath (guards / locked triangles released)
    (3, 185, 1),   # ship_1: cargo ship stowaway scene (LINE LINEEA) seen
    (3, 190, 2),   # yufy1: Yuffie's "Follow me" scene in her house seen (user's call:
                   #   also makes Yuffie visible in yufy2)
]

# Batteries for the Wall Market wire climb: item 85 x3, plus the three
# "battery held" bits the Wall Market weapon store sets when you buy them.
BATTERIES_ITEM, BATTERIES_QTY = 85, 3
BATTERY_BITS = [((1, 165), 5), ((1, 165), 6), ((1, 165), 7)]

# Recruited characters: one bit per character id in this byte (8-bit, bank 4).
RECRUITED = (OPEN_VAR_BANK8, 225)
# Characters recruited so far, Cloud included (set to 1 at new game).
RECRUIT_COUNT = (OPEN_VAR_BANK8, 226)
PHS_MIN_PARTY = 3

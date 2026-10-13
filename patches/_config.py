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
START_X, START_Y, START_TRIANGLE, START_DIR = -2749, 3074, 9, 0   # ~2 steps below the conductor (-2777, 3160), upper platform

# ---------------------------------------------------------------------------
# openFF7 save variables. Bank 3 (opcode nibbles 11 = 8-bit, 12 = 16-bit),
# offsets 96-105, plus the quest areas below: unused by every original field
# script, the world map scripts and (absolute references) the exe, and zeroed
# at new game (exe 0x60BB9B clears banks 1-5). Checked by test_open_vars_unused.
# (These used to be bank 4 224-226, which is world map object slot 5 in the
# exe (0x76609E writes / 0x76616A reads): not safe.)
OPEN_VAR_BANK8, OPEN_VAR_BANK16 = 11, 12
OPEN_VARS_FIRST = 96

# Quest save bytes (600_quests allocates in this order; the first area keeps
# the offsets quests shipped with): (8-bit nibble, first offset, last offset).
QUEST_AREAS = [(11, 192, 255), (11, 160, 183), (7, 181, 223), (3, 27, 63),
               # bank 1 runs unused by every field/world map script and with no exe
               # absolute reference (scan of 2026-10; bank 1 = plain field flags)
               (1, 136, 159), (1, 236, 244)]

# Hunter points (630_bounties.py): u16 at bank 1 245-246 (taken off the end of
# the last quest area, unused and zero at new game). Lifetime total, never
# spent; the Hunter rank is derived from it (630 RANKS).
HUNTER_PTS = (2, 245)

# Quest giver markers (600_quests): "sprites" = the S-Guard star (offer) and
# heart (accepted) models built into char.lgp; "orbs" = the old tinted materia
# orb (yellow offer, blue accepted), no char.lgp needed. Fallback if the
# sprites misbehave in game.
QUEST_MARKERS = "sprites"

# Honey Bee Girl recruitment (620_honey_bee.py): bank 1 251-255, taken off the
# end of the last quest area (free, zero at new game).
HB_JOB = ((1, 251), 0)            # bit: the Honey Bee Inn manager's job accepted
HB_HIRED = (1, 252)               # bits 0-19 over bytes 252-254: girl i hired
HB_VISIT = (1, 255)               # girl index + 1 being visited (0 = none)
# Honey Bee Inn income (bank 1 247-250, 16-bit nibble 2): the exe's play clock
# writes the play time in minutes to HB_MINUTES every second (quest_menu.asm
# q_clock); HB_LAST = HB_MINUTES at the last collection.
HB_MINUTES, HB_LAST = (2, 247), (2, 249)
# Affection 0-20 per girl (Honey Bee gifts), one byte each, girl i ->
# HB_AFFECTION[i]. Bank 1 188-223 has no exe absolute refs and no world map
# use; original field scripts use 197-199 and 208-209, so those are skipped.
HB_AFFECTION = [(1, b) for b in list(range(188, 197)) + list(range(200, 208)) + list(range(210, 213))]
# bit per girl: her devoted (affection 20) scene was seen -> a kid stands next
# to her (622_hb_kids). Bank 1 214-216.
HB_KID = [((1, 214 + i // 8), i % 8) for i in range(20)]
DATE_GIRL = (1, 217)               # girl index + 1 on a date (660_dates; 0 = none)
HB_RATE = 2                     # gil per star per minute
HB_CAP = 270                      # minutes counted at most (60 stars: 32400 gil, fits a signed word)

# Regions that keep their own story line in a private 16-bit variable
# (reads/writes of story progress in their fields are redirected to it).
# name -> (variable, initial value at new game)
REGION_VARS = {}

# Shinra HQ keycards, all given at new game so the building can be explored
# freely. Elevator access level is var[1][224]; the cards are key-item bits.
# World map object slot 4 (submarine; bank 4 offsets 216-223, 16-bit var
# nibble 14): x | model 13 << 19 | direction << 24, then z | height << 18.
# wm0's own sub arrival spot by Junon (650_world_vehicles.py).
SUBMARINE_SLOT = [((14, 216), 0x8FE1), ((14, 218), 0xC06A), ((14, 220), 0x3880), ((14, 222), 0x0002)]
HQ_ACCESS_LEVEL = ((1, 224), 69)   # 69: every elevator stop and the 69F doors (130 removes lowering writes)
HQ_KEYCARD_BITS = [((1, 67), 6),   # Keycard 60
                   ((1, 67), 7),   # Keycard 62
                   ((1, 68), 0),   # Keycard 65
                   ((1, 68), 1),   # Keycard 66
                   ((1, 68), 2)]   # Keycard 68

# openFF7 event flags: one byte of bits (bank 3 offset 96).
FLAGS = (OPEN_VAR_BANK8, 96)
FLAG_GUARD_SCORPION = 1   # Guard Scorpion beaten (No.1 Reactor core)
FLAG_AIR_BUSTER = 2       # Air Buster beaten (No.5 Reactor bridge)
FLAG_IN_REACTOR5 = 3      # last reactor room entered was No.5's (the elevator is shared)
FLAG_TAME_MATERIA = 4     # Tame materia picked up (Sector 6 playground)
FLAG_RUFUS_FOUGHT = 5     # Rufus fought this visit (Shinra HQ roof; cleared on entering it)
FLAG_ELEVATOR_FOUGHT = 6  # HQ elevator gunships fought this visit (69F; cleared on entering it)
FLAG_MOTORBALL_FOUGHT = 7 # Motor Ball fought this visit (end of the highway, roadend)

# Event flags set at new game so rooms behave as if their story scenes were
# already seen (found with tools/ff7/simulate.py: find_quiet_flags, then
# checked together across every pinned Midgar field). (nibble, addr, bit).
INITIAL_EVENT_FLAGS = [
    (3, 208, 0),   # mds7plr1: Sector 7 slums entrance - AVALANCHE run-in seen
    (3, 214, 5),   # mds7pb_2: AVALANCHE hideout entry scene seen
    (3, 214, 6),   # mds7pb_2: morning wake-up scene done (entry = plain lift ride down)
    (3, 214, 0), (3, 214, 1), (3, 214, 2),   # mds7pb_2: border2 line scenes (Barret's SOLDIER talk, Tifa's "Wait") done
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
    (1, 226, 6),   # junair: airport lift state; clear = Cloud drawn 624 units up on
                   #   arrival (OFST in his init) - spawned in the wrong spot
    (1, 232, 5),   # nvdun1: Materia Keeper beaten (hides the original; it's a quest boss line)
    (3, 207, 6),   # Wutai done (0xE7E): wm0 never starts the materia theft (yougan, Yuffie
                   #   leaves); only datiao_* read it (hide Da-chao's quest NPCs)
    (3, 224, 0),   # del1: Rufus/helicopter scene (del12) seen; its line before the exit to town is off
    (3, 222, 1),   # mtcrl_0: the man's 'black-caped guy' scene done (he just says 'dangerous up ahead')
    # Shinra HQ after the infiltration (130_shinra_hq):
    (3, 168, 1),   # blin59: guards gone (no forced battle 422), lobby lifts to the elevator work
    (3, 172, 3),   # blin60_1: sneaking minigame done (guards parked, battle-423 lines off)
    (1, 226, 5),   # blin68_1: scientist who sets access to 68 talked to (hidden)
    # Disc 2 Midgar (reached from md8_2, 160_midgar_disc2): bank 5 offset 128 bits =
    # scenes done: 0 Cait Sith at the tower (md8_32), 1 hatch opened (md8_6: open,
    # party copies hidden), 2 Turks (tunnel_6), 3 Proud Clod (md8brdg2), 4 Hojo
    # (canon_2: hidden); 7 + offset 135 bits 0-3: party copies in the tunnels hidden.
    (15, 128, 0), (15, 128, 1), (15, 128, 2), (15, 128, 3), (15, 128, 4), (15, 128, 7),
    (15, 135, 0), (15, 135, 1), (15, 135, 2), (15, 135, 3),
    # Temple of the Ancients as if explored up to the Demon Wall (415_temple; all its
    # fields pinned at 631): (3,234) bits 2 Tseng/Keystone scene (jtmpin1), 3 arrival
    # scene (kuro_1), 1 the running Ancient at his shop (kuro_1; not 6 = gone), 4 "Sealed"
    # line, 5 entrance camera pan (jtempl), 7 kuro_2 scene; (3,233) bits 1 Ancient
    # Dragon intro (kuro_5; the fight on entry stays, as in the game), 2-3 the
    # key-guard puzzle seen + solved (kuro_7), 4 Demon Wall beaten (kuro_12: its exit
    # line to the temple top is open; the quest boss line still fights it), 5 Time
    # Guardian intro (kuro_4), 6-7 entrance scenes (jtempl). Treasure bits (bank 5
    # 112-113) are left for the player.
    (3, 234, 1), (3, 234, 2), (3, 234, 3), (3, 234, 4), (3, 234, 5), (3, 234, 7),
    (3, 233, 1), (3, 233, 2), (3, 233, 3), (3, 233, 4), (3, 233, 5), (3, 233, 6), (3, 233, 7),
]

# Batteries for the Wall Market wire climb: item 85 x3, plus the three
# "battery held" bits the Wall Market weapon store sets when you buy them.
BATTERIES_ITEM, BATTERIES_QTY = 85, 3
BATTERY_BITS = [((1, 165), 5), ((1, 165), 6), ((1, 165), 7)]

# Recruited characters: one bit per character id in this byte (8-bit, bank 3).
RECRUITED = (OPEN_VAR_BANK8, 97)
# Characters recruited so far, Cloud included (set to 1 at new game).
RECRUIT_COUNT = (OPEN_VAR_BANK8, 98)
PHS_MIN_PARTY = 3

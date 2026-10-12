"""World map vehicles that the early-game world map can't show.

- Highwind / submarine models: the world map loads a model set chosen by
  story progress (0x766B9F: < 1000 = variant 0). Variant 0's table (0x96A910,
  10 entries: choko, tybrco, buggy, barrier, condor, rocket, rocketbase,
  goldsaucer, canon, rock) has no highwind or sbmrn, and its row of the
  model id -> loaded entry map (0x96DF10 + variant*32, value = entry + 1,
  0xFF = none; read at 0x768A37) has 0xFF for model 3 (Highwind) and 13
  (submarine): op_300 3 made a working but invisible Highwind. A 12-entry
  copy of the table with variant 1's highwind and sbmrn entries appended
  (0x96AAF0 entries 2 and 3) replaces it, and row 0 maps 3 -> 11, 13 -> 12
  (variants 1-4 already load 13 entries, so 12 fit).
- The submarine's parked position: world map objects are saved in six 8-byte
  slots at savemap 0x0F5C (bank 4 offset 184; written 0x76609E, restored
  0x76616A by matching model bits); slot 4 (bank 4 216-223) is the
  submarine's. It was empty, so the sub stood at (0, 0), the map's top-left
  corner. The new game writes it with wm0's own sub arrival (field id 54
  branch): mesh (20, 17) + (0xFE1, 0x1880) = x 167905, z 145536, direction
  0xC0, by Junon. Height 0 (sea level) is a guess. See _config.SUBMARINE_SLOT.
"""
import struct

VARIANT0_TABLE, VARIANT0_COUNT = 0x96A910, 10
VARIANT1_TABLE = 0x96AAF0
ENTRY = 20
EXTRA = [2, 3]                       # variant 1 table: highwind, sbmrn
SET_TABLE = 0x75948D                 # mov [0xE2BBD0], imm32 (variant 0 case)
SET_COUNT = 0x759497                 # mov [0xE2BBD4], imm32
MODEL_MAP_ROW0 = 0x96DF10
HIGHWIND, SUBMARINE = 3, 13


def apply(ctx):
    exe = ctx.exe()
    entries = [exe.read(VARIANT0_TABLE + ENTRY * i, ENTRY) for i in range(VARIANT0_COUNT)]
    for i in EXTRA:
        entries.append(exe.read(VARIANT1_TABLE + ENTRY * i, ENTRY))

    def name(entry):
        va = struct.unpack_from("<I", entry)[0]
        return exe.read(va, 12).split(b"\0")[0]
    assert [name(e) for e in entries[-2:]] == [b"highwind", b"sbmrn"], [name(e) for e in entries]
    table = exe.alloc(b"".join(entries), "world_models_variant0")
    exe.patch_u32(SET_TABLE, VARIANT0_TABLE, table, "world map variant 0: model table + highwind, sbmrn")
    exe.patch_u32(SET_COUNT, VARIANT0_COUNT, len(entries), "world map variant 0: model count")
    exe.patch(MODEL_MAP_ROW0 + HIGHWIND, b"\xff", bytes([VARIANT0_COUNT + 1]), "variant 0: Highwind model")
    exe.patch(MODEL_MAP_ROW0 + SUBMARINE, b"\xff", bytes([VARIANT0_COUNT + 2]), "variant 0: submarine model")

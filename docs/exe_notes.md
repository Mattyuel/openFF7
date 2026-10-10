# ff7_en.exe notes (Steam version)

Findings from reading the executable with a disassembler (capstone). No code
has been changed.

## Steam DRM

- The executable has a `.bind` section and its entry point (RVA `0xB6F2D0`) is
  inside it. That is Steam's SteamStub DRM wrapper. The game code in `.text` is
  **not** encrypted.
- Practical effect: the exe needs the Steam client running and may hand off to
  Steam on start. A copy in another folder may be relaunched from the Steam
  install instead. **Untested.** Until it is, test builds by copying the changed
  data files into the Steam install (see `TESTING.md`).
- The Steam install starts the game via `FF7_Launcher.exe`, which then runs
  `ff7_en.exe`.

## Story progress in the exe

The savemap is at `0x00DBFD38` (as in the 1998 release); story progress is at
`0x00DC08DC` (savemap `0x0BA4`). There are 83 references to that address:

- 79 are indexed accesses (`[reg + 0xDC08DC]`): the generic variable read/write
  code used by field and world map scripts for savemap bank 1. These are not
  story checks in themselves.
- 4 direct comparisons, all in one routine around `0x766BA8`–`0x766C4A`:
  progress against **1000, 1200, 1580 and 1620**. The world map script uses
  the same thresholds, so this is most likely world map setup (map variant /
  sky state). With openFF7's global value of 100, the world map is in its
  disc 1 state.

## Not yet checked

- PHS / save-point restrictions and anything else keyed on flags rather than
  story progress.
- Where Cait Sith's and Vincent's character records are initialised when they
  join (slots 6 and 7 hold Young Cloud and Sephiroth at new game).

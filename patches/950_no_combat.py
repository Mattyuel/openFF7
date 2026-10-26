"""(user) No combat (docs/gym_plan.md): no random battles anywhere while
`_config.COMBAT` is False.

Fields: both encounter tables (section 6, `ff7.encounters`) get enabled = 0.
Done last so fields other patches copied from originals (new sets) are covered.
World map: the encounter roll's call (0x76760B -> 0x767641, returns a formation
or -1; Yuffie's encounter is in it too) becomes `or eax, -1` (the debug build's
toggle stub patches the same call, so it stands aside when combat is off).

Scripted battles (BATTLE ops: our boss lines, 626's thugs, the original story
fights still reachable) are not touched here. Untested in-game: that a table
with enabled 0 rolls no battle is the community's reading of the format.
"""
from _config import COMBAT

WM_ROLL_CALL, WM_ROLL = 0x76760B, 0x767641
TABLES = (0, 24)


def apply(ctx):
    if COMBAT:
        return
    names = [n for n in ctx.maplist if n in ctx.flevel or n in ctx._fields]
    off = 0
    for name in names:
        ff = ctx.field(name)
        sec = bytearray(ff.section("encounter"))
        if not any(sec[t] for t in TABLES if t < len(sec)):
            continue
        for t in TABLES:
            if t < len(sec):
                sec[t] = 0
        ff.set_section("encounter", bytes(sec))
        off += 1
    rel = (WM_ROLL - (WM_ROLL_CALL + 5)).to_bytes(4, "little", signed=True)
    ctx.exe().patch(WM_ROLL_CALL, b"\xE8" + rel, b"\x83\xC8\xFF\x90\x90",   # or eax, -1
                    "no combat: world map encounter roll")
    print("  950: random battles off in %d fields and on the world map" % off)

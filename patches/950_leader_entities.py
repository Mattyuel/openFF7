"""Any character can lead the party in the field.

The engine gives control to the entity whose `PC <char>` matches the party
leader (party slot 0) and hides the other party members' PC entities; the
original fields include such entities for whoever could lead there (disc 2
fields have Tifa and Cid, a few have everyone, e.g. blue_2). A field without
one for the current leader leaves you with no one to control.

The PC opcode (ff7_en.exe 0x61BCD7) compares against the *field party copy*
at savemap 0x0CAD-0x0CAF (var[3][9..11]), not the real party (0x04F8) that
the PHS edits; the copy is only refreshed by party opcodes and the world map.
So each playable field first copies the real party into it (GETPC, which reads
the real party), before any PC opcode runs (entity 0's init runs first).

Every field that has at least one PC entity also gets an entity
`CHAR <model>; PC <char>` for each character it lacks. Models come from blue_2,
whose entries for all nine characters load just stand/walk/run, rescaled to
the target field (ModelLoader.add_from).

Known limits (see CLAUDE.md): field interactions scripted on Cloud's entity
(ladders, jumps, climbs) still move Cloud's hidden entity, not another
leader; and the model count per field rises up to 24 (original max 16).
Runs last so it sees every other patch's entities.
"""
from ff7.models import ModelLoader
from ff7.script import Op, Script

DONOR = "blue_2"
FIELD_PARTY = (3, 9)  # var[3][9..11]: the party copy the PC opcode reads
LEADERS = range(9)  # character ids; 6/7 are Cait Sith/Vincent (Young Cloud/Sephiroth in flashbacks)


def _pc_chars(sec):
    return {o.raw[1] for o in sec.ops if o.op == 0xA0}


def _donor_models(ctx):
    """char id -> model index in the donor field's loader."""
    sec = Script.parse(ctx.field(DONOR).sections[0])
    out = {}
    for ent in range(len(sec.entry)):
        init = sec.script_ops(ent, 0)
        char = next((o.raw[1] for o in init if o.op == 0xA1), None)
        pc = next((o.raw[1] for o in init if o.op == 0xA0), None)
        if char is not None and pc is not None:
            out[pc] = char
    assert set(LEADERS) <= set(out), "donor %s lacks %s" % (DONOR, set(LEADERS) - set(out))
    return out


def _sync_party(sec):
    """At the very start of entity 0's init: field party copy = real party."""
    bank, addr = FIELD_PARTY
    ops = [Op(bytes([0x74, bank, slot, addr + slot])) for slot in range(3)]   # GETPC
    sec.insert_before(sec.entry[0][0], ops, retarget=False)
    sec.entry[0][0] = ops[0]


def apply(ctx):
    donor_models = _donor_models(ctx)
    donor = ModelLoader(ctx.field(DONOR).section("models"))
    added = 0
    for name in ctx.maplist:
        if name not in ctx.flevel:
            continue
        try:
            sec = Script.parse(ctx.field(name).sections[0])
        except ValueError:
            continue
        present = _pc_chars(sec)
        if not present:
            continue          # no playable entity: menus, movies, cutscene-only fields
        field = ctx.field(name)
        _sync_party(sec)
        missing = [c for c in LEADERS if c not in present]
        if not missing:
            field.sections[0] = sec.build()
            continue
        loader = ModelLoader(field.section("models"))
        for char in missing:
            model = loader.add_from(donor, donor_models[char])
            sec.add_entity("pc%d" % char, {0: [Op(bytes([0xA1, model])),    # CHAR
                                               Op(bytes([0xA0, char])),     # PC
                                               Op(b"\x00"), Op(b"\x00")]})
            added += 1
        field.set_section("models", loader.build())
        field.sections[0] = sec.build()
    print("  leader entities: %d added" % added)

"""Rough simulation of what happens when a field is entered.

Runs every entity's script 0 (init, then one pass of main) against a given
variable state, following REQ/REQSW/REQEW calls synchronously, and records
signs of a cutscene: player control locked, dialogue, map jumps, battles,
movies, and party-member models (PC != Cloud) left visible.

It is an approximation (no timing, no movement, loops capped) meant to find
entry cutscenes and the event flags that suppress them, not a full engine.
"""
import struct

from .script import End, Script

# opcode bank nibble -> (memory bank key, width)
BANKS = {1: (1, 8), 2: (1, 16), 3: (2, 8), 4: (2, 16), 11: (3, 8), 12: (3, 16),
         13: (4, 8), 14: (4, 16), 7: (5, 8), 15: (5, 16), 5: ("t", 8), 6: ("t", 16)}
SAVE_BANKS = {1, 2, 3, 4, 5}


class State:
    def __init__(self, mem=None, party=(0,)):
        self.mem = {k: bytearray(256) for k in (1, 2, 3, 4, 5, "t")}
        if mem:
            for k, v in mem.items():
                self.mem[k][:] = v
        self.party = set(party)

    def copy(self):
        s = State(party=self.party)
        for k, v in self.mem.items():
            s.mem[k][:] = v
        return s

    def get(self, nibble, addr):
        if nibble == 0:
            return addr
        bank, width = BANKS.get(nibble, ("t", 8))
        m = self.mem[bank]
        if width == 8:
            return m[addr & 0xFF]
        return m[addr & 0xFF] | m[(addr + 1) & 0xFF] << 8

    def set(self, nibble, addr, value):
        if nibble == 0:
            return
        bank, width = BANKS.get(nibble, ("t", 8))
        m = self.mem[bank]
        m[addr & 0xFF] = value & 0xFF
        if width == 16:
            m[(addr + 1) & 0xFF] = (value >> 8) & 0xFF

    def bit(self, nibble, addr, bit, on):
        bank, _ = BANKS.get(nibble, ("t", 8))
        a = (addr + bit // 8) & 0xFF
        if on:
            self.mem[bank][a] |= 1 << (bit % 8)
        else:
            self.mem[bank][a] &= ~(1 << (bit % 8)) & 0xFF


def _cmp(a, b, c):
    return [a == b, a != b, a > b, a < b, a >= b, a <= b, (a & b) != 0, (a ^ b) != 0,
            (a | b) != 0, bool(a & (1 << b)) if 0 <= b < 32 else False,
            not (a & (1 << b)) if 0 <= b < 32 else True][c] if c < 11 else False


class Report:
    def __init__(self):
        self.signals = []        # (entity, script, what)
        self.tested_flags = set()  # (nibble, addr, bit) tested via bit_on/bit_off/&
        self.visible_party = []    # (entity name, char)
        self.final_visible = {}    # entity name -> visible after entering (model entities)
        self.locked = set()        # walkmesh triangles locked (IDLCK) after entering

    @property
    def cutscene(self):
        return bool(self.signals or self.visible_party)

    def summary(self):
        out = ["%s s%d: %s" % s for s in self.signals[:8]]
        out += ["party member visible: %s (char %d)" % v for v in self.visible_party]
        return out


def simulate(script_section, state, max_steps=20000):
    sc = Script.parse(script_section)
    names = [n.split(b"\0")[0].decode("latin-1") for n in sc.entity_names]
    index = {id(o): i for i, o in enumerate(sc.ops)}
    rep = Report()
    pc_char = {}
    visible = {}
    has_model = set()
    shown = set()
    steps = [0]

    def run(ent, start_i, depth, stop_at_ret=True):
        i = start_i
        visits = {}
        while 0 <= i < len(sc.ops) and steps[0] < max_steps:
            steps[0] += 1
            o = sc.ops[i]
            r, op = o.raw, o.op
            visits[i] = visits.get(i, 0) + 1
            if visits[i] > 3:
                return
            nxt = i + 1
            if op == 0x00:  # RET
                return
            elif op in (0x14, 0x15):
                a = state.get(r[1] >> 4, r[2])
                b = state.get(r[1] & 15, r[3])
                if r[4] in (6, 9, 10) and (r[1] >> 4) in BANKS and (r[1] & 15) == 0:
                    rep.tested_flags.add((r[1] >> 4, r[2], r[3] if r[4] != 6 else -r[3]))
                if not _cmp(a, b, r[4]):
                    nxt = _target(o)
            elif op in (0x16, 0x17, 0x18, 0x19):
                av, bv = struct.unpack_from("<HH", r, 2)
                a = state.get(r[1] >> 4, av)
                b = state.get(r[1] & 15, bv)
                if op in (0x16, 0x17):
                    a = a - 0x10000 if a >= 0x8000 else a
                    b = b - 0x10000 if b >= 0x8000 else b
                if r[6] in (6, 9, 10) and (r[1] >> 4) in BANKS and (r[1] & 15) == 0:
                    rep.tested_flags.add((r[1] >> 4, av, bv if r[6] != 6 else -bv))
                if not _cmp(a, b, r[6]):
                    nxt = _target(o)
            elif op in (0xCB, 0xCC):  # IFPRTYQ / IFMEMBQ
                if r[1] not in state.party:
                    nxt = _target(o)
            elif op in (0x30, 0x31, 0x32):  # IFKEY*: no key pressed
                nxt = _target(o)
            elif op in (0x10, 0x11, 0x12, 0x13):
                nxt = _target(o)
            elif op in (0x01, 0x02, 0x03):  # REQ family
                tgt_ent, scr = r[1], r[2] & 0x1F
                if depth < 6 and tgt_ent < len(sc.entry):
                    t = sc.entry[tgt_ent][scr]
                    if not isinstance(t, End):
                        run(tgt_ent, index[id(t)], depth + 1)
            elif op == 0x80:
                state.set(r[1] >> 4, r[2], state.get(r[1] & 15, r[3]))
            elif op == 0x81:
                state.set(r[1] >> 4, r[2], state.get(r[1] & 15, struct.unpack_from("<H", r, 3)[0]))
            elif op == 0x82:
                state.bit(r[1] >> 4, r[2], state.get(r[1] & 15, r[3]), True)
            elif op == 0x83:
                state.bit(r[1] >> 4, r[2], state.get(r[1] & 15, r[3]), False)
            elif op == 0x6D:  # IDLCK triangle u16, on
                tri = r[1] | r[2] << 8
                if r[3]:
                    rep.locked.add(tri)
                else:
                    rep.locked.discard(tri)
            elif op == 0x33:  # UC
                if r[1] == 1:
                    rep.signals.append((names[ent], 0, "player control locked"))
            elif op in (0x40, 0x48):
                rep.signals.append((names[ent], 0, "dialogue (text %d)" % (r[2] if op == 0x40 else r[3])))
            elif op == 0x60:
                rep.signals.append((names[ent], 0, "map jump"))
            elif op == 0x70:
                rep.signals.append((names[ent], 0, "battle"))
            elif op in (0xF9, 0xF8):
                rep.signals.append((names[ent], 0, "movie"))
            elif op == 0xA1:
                has_model.add(ent)
                visible.setdefault(ent, True)
            elif op == 0xA0:
                pc_char[ent] = r[1]
            elif op == 0xA4:
                visible[ent] = bool(r[1])
                if r[1]:
                    shown.add(ent)
                if r[1] and depth > 0 and pc_char.get(ent, 0) != 0:
                    rep.signals.append((names[ent], 0, "party member shown"))
            elif op in (0xA8, 0xA9, 0xAD, 0xC0) and depth > 0 and pc_char.get(ent, 0) != 0 \
                    and visible.get(ent, False):
                rep.signals.append((names[ent], 0, "party member moves"))
            i = nxt

    def _target(o):
        if isinstance(o.target, End):
            return len(sc.ops)
        return index[id(o.target)]

    # The engine runs every entity's init (script 0 up to its first RET) before
    # any main part (the rest of script 0).
    mains = []
    for ent in range(len(sc.entry)):
        start = sc.entry[ent][0]
        if isinstance(start, End):
            continue
        i = index[id(start)]
        run(ent, i, 0)
        j = i
        while j < len(sc.ops) and sc.ops[j].op != 0x00:
            j += 1
        if j + 1 < len(sc.ops) and not any(sc.ops[j + 1] is e[0] for e in sc.entry):
            mains.append((ent, j + 1))
    for ent, i in mains:
        run(ent, i, 0)

    # The engine draws only the party leader's PC entity by default; other
    # party-member entities appear when a script shows them (VISI 01).
    for ent in has_model:
        rep.final_visible[names[ent]] = visible.get(ent, ent not in pc_char)
    for ent in has_model:
        ch = pc_char.get(ent)
        if ch is not None and ch != 0 and visible.get(ent, False) and ent in shown:
            rep.visible_party.append((names[ent], ch))
    return rep


# openFF7's own save variables (bank 4, 224-255): never chosen as "seen" flags.
OWN_VARS = (4, range(224, 256))


def _flag_bits(tested):
    """Normalise tested flags to (nibble, addr, bit) bits that could be set."""
    out = set()
    for nib, addr, v in tested:
        if nib not in BANKS or BANKS[nib][0] not in SAVE_BANKS:
            continue
        if BANKS[nib][0] == OWN_VARS[0] and addr in OWN_VARS[1]:
            continue
        if v < 0:  # '&' mask
            m = -v
            out.update((nib, addr, b) for b in range(16) if m & (1 << b))
        else:
            out.add((nib, addr, v))
    return out


def find_quiet_flags(script_section, base_state, max_rounds=8):
    """Greedily choose event-flag bits to set so that entering the field shows
    no cutscene. Returns (bits, report_before, report_after)."""
    def score(rep):
        return len(rep.signals) + 2 * len(rep.visible_party)

    chosen = []
    before = simulate(script_section, base_state.copy())
    best = before
    for _ in range(max_rounds):
        if not best.cutscene:
            break
        improved = None
        for bit in sorted(_flag_bits(best.tested_flags)):
            if bit in chosen:
                continue
            st = base_state.copy()
            for b in chosen + [bit]:
                st.bit(b[0], b[1], b[2], True)
            rep = simulate(script_section, st)
            if score(rep) < score(best) and (improved is None or score(rep) < score(improved[1])):
                improved = (bit, rep)
        if not improved:
            break
        chosen.append(improved[0])
        best = improved[1]
    return chosen, before, best

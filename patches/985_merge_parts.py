"""(user) Cloud's / Cid's member and the girls' nipples merged into the part they sit on (the pelvis /
torso .p), so editing that one part in a model tool shows them too ("They should really be part of the
pelvis/torso"). Each was a second part on the same bone (an .hrc bone line "2 ZCLB ZCLP"); now the
first part on the bone (pelvis / torso) holds the extras in its .p (vertices, triangles, normals and
colours as they were: the bone's frame is shared, so nothing moves). The extra parts' own files stay in char.lgp (672 /
673 read the member's ends from zcmp.p / zcjp.p before this) but no .hrc uses them. Runs before
990_char_overrides: a hand-edited pelvis / torso .p there replaces the merged one."""
import re
import struct

EXTRA = re.compile(r"^(ZCLP|ZCIP|ZK[A-Z][LR])$")      # member (Cloud, Cid), nipples (ZK<tag>L/R)


def _read(d):
    """(vertices, triangles as stored, per-vertex normals, per-vertex colours) of a one-group untextured .p."""
    h = struct.unpack_from("<16I", d, 0)
    nv, nn, nu, nt, nc, ne, npoly = h[3], h[4], h[5], h[6], h[7], h[8], h[9]
    assert nt == 0 and nc == nv, ("not an untextured part", h[:10])
    V = [list(struct.unpack_from("<3f", d, 128 + 12 * i)) for i in range(nv)]
    N = [list(struct.unpack_from("<3f", d, 128 + 12 * nv + 12 * i)) for i in range(nn)]
    oc = 128 + 12 * nv + 12 * nn + 12 * nu + 8 * nt
    C = [tuple(d[oc + 4 * i:oc + 4 * i + 3]) for i in range(nc)]
    op = oc + 4 * nc + 4 * npoly + 4 * ne
    P, VN = [], [None] * nv
    for j in range(npoly):
        p = struct.unpack_from("<12H", d, op + 24 * j)
        P.append(p[1:4])
        for v, n in zip(p[1:4], p[4:7]):
            VN[v] = VN[v] or N[n]
    return V, P, [n or [0.0, -1.0, 0.0] for n in VN], C, d[64:128], struct.unpack_from("<12H", d, op)[10:12]


def _ply(ctx, rsd):
    text = ctx.char_file(rsd.lower() + ".rsd").decode("latin-1")
    return text.split("PLY=")[1].split(".")[0].lower() + ".p"


def apply(ctx):
    import importlib
    hb = importlib.import_module("620_honey_bee")
    hrcs = {n: ctx.char_file(n).decode("latin-1") for n in sorted(ctx._char) if n.endswith(".hrc")}
    uses = {}
    for n, text in hrcs.items():
        for line in text.splitlines():
            w = line.split()
            if len(w) > 1 and w[0].isdigit() and int(w[0]) == len(w) - 1:
                for r in w[1:]:
                    uses.setdefault(r, set()).add(n)
    done = []
    for n, text in hrcs.items():
        lines = text.splitlines(True)
        changed = False
        for k, line in enumerate(lines):
            w = line.split()
            if not (len(w) > 2 and w[0].isdigit() and int(w[0]) == len(w) - 1):
                continue
            extra = [r for r in w[1:] if EXTRA.match(r)]
            keep = [r for r in w[1:] if not EXTRA.match(r)]
            if not extra:
                continue
            base = keep[0]                                  # (the torso, before its neck bar)
            assert uses[base] == {n}, ("part shared by other models: merging would change them", base, uses[base])
            V, P, N, C, tail, ptail = _read(ctx.char_file(_ply(ctx, base)))
            for r in extra:
                v2, p2, n2, c2, _, _ = _read(ctx.char_file(_ply(ctx, r)))
                P += [tuple(i + len(V) for i in t) for t in p2]
                V, N, C = V + v2, N + n2, C + c2
            ctx.char_file(_ply(ctx, base), hb._p_file(V, P, C, tail, ptail, normals=N, wound=True))
            lines[k] = line.replace(line.strip(), " ".join([str(len(keep))] + keep))
            changed = True
            done.append("%s %s+%s" % (n, base, "+".join(extra)))
        if changed:
            ctx.char_file(n, "".join(lines).encode("latin-1"))
    assert any(d.startswith("zcla.hrc") for d in done), "Cloud's member not found"
    print("  985: merged %d part(s): %s" % (len(done), ", ".join(done)))

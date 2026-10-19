"""Can the player walk from a field's entrances to its exits?

Uses the walkmesh (triangle adjacency), triangles locked after entering
(simulate.Report.locked), gateway lines (exits) and the arrival triangles of
gateways/map jumps that lead into the field (entrances)."""
from .field import FieldFile
from .triggers import gateways
from .walkmesh import Walkmesh


def _components(mesh, locked):
    comp = {}
    for start in range(len(mesh.tris)):
        if start in comp or start in locked:
            continue
        stack = [start]
        comp[start] = start
        while stack:
            t = stack.pop()
            for n in mesh.access[t]:
                if n >= 0 and n not in comp and n not in locked and n < len(mesh.tris):
                    comp[n] = start
                    stack.append(n)
    return comp


def exit_triangles(mesh, gw):
    """Triangles touching a gateway line (sampled along the line)."""
    (x1, y1, _), (x2, y2, _) = gw["p1"], gw["p2"]
    out = set()
    for k in range(11):
        x = x1 + (x2 - x1) * k / 10.0
        y = y1 + (y2 - y1) * k / 10.0
        for dx, dy in ((0, 0), (20, 0), (-20, 0), (0, 20), (0, -20)):
            t = mesh.find(x + dx, y + dy)
            if t is not None:
                out.add(t)
    return out


def check(field_bytes, locked, entrances, names):
    """entrances: [(label, triangle)]. Returns {(entrance label, exit field): reachable}."""
    ff = FieldFile(field_bytes)
    mesh = Walkmesh(ff.section("walkmesh"))
    comp = _components(mesh, set(locked))
    result = {}
    for gw in gateways(ff.section("triggers")):
        tris = exit_triangles(mesh, gw)
        target = names[gw["field"]] if gw["field"] < len(names) else gw["field"]
        for label, tri in entrances:
            if tri is None or tri >= len(mesh.tris):
                continue
            ok = tri in comp and any(t in comp and comp[t] == comp[tri] for t in tris)
            result[(label, target)] = ok
    return result

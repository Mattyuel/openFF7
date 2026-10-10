"""Field walkmesh (section 4): triangles the player can walk on.

  u32 count; count * (3 vertices * (s16 x, y, z, pad)); count * (3 s16 access)
Access entry k is the neighbouring triangle across edge k (vertex k -> k+1),
or -1 at the mesh boundary.
"""
import struct


class Walkmesh:
    def __init__(self, data):
        n, = struct.unpack_from("<I", data, 0)
        self.tris = [[struct.unpack_from("<hhh", data, 4 + i * 24 + k * 8) for k in range(3)]
                     for i in range(n)]
        base = 4 + n * 24
        self.access = [list(struct.unpack_from("<3h", data, base + i * 6)) for i in range(n)]

    def center(self, i):
        v = self.tris[i]
        return tuple(round(sum(p[k] for p in v) / 3) for k in range(3))

    def contains(self, i, x, y):
        (x1, y1, _), (x2, y2, _), (x3, y3, _) = self.tris[i]

        def side(ax, ay, bx, by):
            return (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        d1, d2, d3 = side(x1, y1, x2, y2), side(x2, y2, x3, y3), side(x3, y3, x1, y1)
        neg = d1 < 0 or d2 < 0 or d3 < 0
        pos = d1 > 0 or d2 > 0 or d3 > 0
        return not (neg and pos)

    def find(self, x, y):
        """Triangle containing (x, y), or None."""
        for i in range(len(self.tris)):
            if self.contains(i, x, y):
                return i
        return None

    def boundary_edges(self, i):
        """Edges of triangle i on the mesh boundary: [(p1, p2)]."""
        v = self.tris[i]
        return [(v[k], v[(k + 1) % 3]) for k in range(3) if self.access[i][k] == -1]

    def height(self, i, x, y):
        """z of the point (x, y) on triangle i's plane."""
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = self.tris[i]
        det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if det == 0:
            return round((z1 + z2 + z3) / 3)
        a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
        b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
        return round(a * z1 + b * z2 + (1 - a - b) * z3)

    def nearby(self, i, depth=4):
        """Triangles reachable from i within `depth` steps (i first)."""
        seen, frontier = [i], [i]
        for _ in range(depth):
            frontier = [n for t in frontier for n in self.access[t] if n >= 0 and n not in seen]
            frontier = list(dict.fromkeys(frontier))
            seen += frontier
        return seen

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

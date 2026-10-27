"""Scripted walks without MOVE (user: MOVE got stuck on walkmesh piece edges and on other entities: the bar
shift's Cloud along the counter, the Honey Bee shift's Cloud behind the customer): the entity's position stepped
by XYZI from two temp words each frame, along straight legs between waypoints, its walk anim looping, facing each
leg, landing exactly on every waypoint, then its stand anim. Check each leg is floor before using it (`floor_leg`)."""
import math
import struct

from ff7 import asm
from ff7.script import Op


def floor_leg(mesh, a, b, level=3):
    """The straight line a -> b stays on the floor (walkmesh, z within `level` of 0: no stool / counter tops)."""
    for k in range(41):
        x, y = a[0] + (b[0] - a[0]) * k / 40, a[1] + (b[1] - a[1]) * k / 40
        t = mesh.find(round(x), round(y))
        if t is None or abs(mesh.tris[t][0][2]) > level:
            return False
    return True


def walk(hb, animb, path, wx, wy, n_, walk_anim, stand_anim, to, step, wz=None):
    """Ops: walk along `path` ((x, y, z, tri) points) on temp words wx / wy (counter byte n_), anims by index;
    `to`(a, b) -> DIR; `step` field units a frame. `wz`: a third temp word stepping z too (a sloped floor, e.g.
    onna_52's), else each leg at its start's z."""
    ops = [animb(), Op(bytes([0xA2, walk_anim, 1])), Op(bytes([0xAE, walk_anim, 1]))]
    for a, b in zip(path, path[1:]):
        n = max(1, round(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        dx, dy = round((b[0] - a[0]) / n), round((b[1] - a[1]) / n)
        top, done = hb._w(1), asm.nop()
        ops += [Op(bytes([0xB3, 0, to(a, b) % 256])), asm.setword(wx, a[0] & 0xFFFF), asm.setword(wy, a[1] & 0xFFFF),
                asm.setbyte(n_, 0)]
        if wz is not None:
            dz = round((b[2] - a[2]) / n)
            ops += [asm.setword(wz, a[2] & 0xFFFF), top, hb._arith(0x86, wz, dz & 0xFFFF)]
            place = Op(bytes([0xA5, 0x66, 0x60]) + struct.pack("<HHHH", wx[1], wy[1], wz[1], a[3]))
        else:
            ops += [top]
            place = Op(bytes([0xA5, 0x66, 0x00]) + struct.pack("<HHhH", wx[1], wy[1], a[2], a[3]))
        ops += [hb._arith(0x86, wx, dx & 0xFFFF), hb._arith(0x86, wy, dy & 0xFFFF), place,
                Op(bytes([0x95, n_[0], n_[1]])), asm.if_byte(n_, "<", n, done), asm.goto_back(top), done,
                hb._xyzi(*b[:4])]
    return ops + [animb(), Op(bytes([0xA2, stand_anim, 1])), Op(bytes([0xAE, stand_anim, 1]))]

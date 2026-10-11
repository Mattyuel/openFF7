"""Field camera (section 1): project field coordinates to screen pixels.

  s16 axis[3][3] (rows = camera x, y, z axes, 4096 = 1.0), s16 pad,
  s32 position[3] (already in camera space), s32 pad, u16 zoom.
Screen = zoom * (R.v / 4096 + T) projected (GTE style): x right, y down,
relative to the background centre. Checked against md8brdg: md8_3's arrival
(-422, 1387) lands near the top of the screen and the train arrival
(-420, 100) a little below the middle, as seen in game. The scroll limits in
the triggers header (`screen_range`) are in the same pixel units.
"""
import math
import struct


class Camera:
    def __init__(self, data):
        v = struct.unpack_from("<9h", data, 0)
        self.axes = [v[0:3], v[3:6], v[6:9]]
        self.pos = struct.unpack_from("<3i", data, 20)
        self.zoom = struct.unpack_from("<H", data, 36)[0]

    def project(self, x, y, z):
        sv = [sum(a * c for a, c in zip(axis, (x, y, z))) / 4096 + t
              for axis, t in zip(self.axes, self.pos)]
        return self.zoom * sv[0] / sv[2], self.zoom * sv[1] / sv[2]


def facing_vector(direction):
    """Field (x, y) unit vector an entity with DIR `direction` (0-255) faces:
    (sin a, -cos a), a = direction * 2pi / 256. Fitted on 116 gateway
    arrivals (each faces away from the exit it came through) and matches
    0x40 = facing right at mds5_5 (seen in game)."""
    a = direction * 2 * math.pi / 256
    return math.sin(a), -math.cos(a)


def facing_screen(cam, x, y, z, screen_dir):
    """DIR value whose facing looks most like `screen_dir` (dx, dy) on screen
    (y down), e.g. (0, 1) = facing down the screen."""
    sx, sy = cam.project(x, y, z)

    def miss(d):
        fx, fy = facing_vector(d)
        px, py = cam.project(x + fx * 100, y + fy * 100, z)
        dx, dy = px - sx, py - sy
        return -(dx * screen_dir[0] + dy * screen_dir[1]) / (math.hypot(dx, dy) or 1)
    return min(range(256), key=miss)


def screen_range(triggers):
    """(left, top, right, bottom) camera scroll limits from the triggers header."""
    return struct.unpack_from("<4h", triggers, 12)

"""Field animations (.a in char.lgp) and forward kinematics for field skeletons (.hrc).

.a: u32 version (1), u32 frames, u32 bones, u8 rotation order[3] (1 0 2 =
Y X Z), u8 pad, u32 runtime[5]; then per frame: root rotation (3 f32,
degrees), root translation (3 f32), bones x rotation (3 f32, degrees).
A bone's rotation is relative to its parent's end; the bone runs along its
own -z for its length (.hrc). Rotation matrix = Ry . Rx . Rz (z innermost),
which matches how the lying pose DZBA differs from the standing BAJB.
"""
import math
import struct

HEADER = 36


class Anim:
    def __init__(self, data):
        self.head = bytearray(data[:HEADER])
        _, self.nframes, self.nbones = struct.unpack_from("<III", data, 0)
        self.frames = []
        o = HEADER
        fmt = struct.Struct("<%df" % (6 + 3 * self.nbones))
        for _ in range(self.nframes):
            v = fmt.unpack_from(data, o)
            self.frames.append((list(v[0:3]), list(v[3:6]), [list(v[6 + 3 * i:9 + 3 * i]) for i in range(self.nbones)]))
            o += 24 + 12 * self.nbones

    def build(self):
        out = bytearray(self.head)
        struct.pack_into("<I", out, 4, len(self.frames))
        for root_rot, root_pos, bones in self.frames:
            out += struct.pack("<3f", *root_rot) + struct.pack("<3f", *root_pos)
            for b in bones:
                out += struct.pack("<3f", *b)
        return bytes(out)


def skeleton(hrc_text):
    """[(name, parent name, length)] from an .hrc file's text."""
    lines = [l.strip() for l in hrc_text.splitlines()]
    out, i = [], lines.index(next(l for l in lines if l.startswith(":BONES"))) + 1
    while i < len(lines):
        if not lines[i]:
            i += 1
            continue
        out.append((lines[i], lines[i + 1], float(lines[i + 2])))
        i += 4
    return out


# ---- 3x3 matrices (row-major lists) -------------------------------------------
# (unrolled for speed: these run hundreds of millions of times in a build. Plain left-to-right sums: sum() of
# floats is compensated from Python 3.12, so results differ from it in the last bit, but no longer by version)
def _mul(a, b):
    (a00, a01, a02), (a10, a11, a12), (a20, a21, a22) = a
    (b00, b01, b02), (b10, b11, b12), (b20, b21, b22) = b
    return [[a00 * b00 + a01 * b10 + a02 * b20, a00 * b01 + a01 * b11 + a02 * b21,
             a00 * b02 + a01 * b12 + a02 * b22],
            [a10 * b00 + a11 * b10 + a12 * b20, a10 * b01 + a11 * b11 + a12 * b21,
             a10 * b02 + a11 * b12 + a12 * b22],
            [a20 * b00 + a21 * b10 + a22 * b20, a20 * b01 + a21 * b11 + a22 * b21,
             a20 * b02 + a21 * b12 + a22 * b22]]


def _vec(m, v):
    x, y, z = v
    (a00, a01, a02), (a10, a11, a12), (a20, a21, a22) = m
    return [a00 * x + a01 * y + a02 * z, a10 * x + a11 * y + a12 * z, a20 * x + a21 * y + a22 * z]


def _t(m):
    return [[m[c][r] for c in range(3)] for r in range(3)]


def _rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def _rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def euler_matrix(x, y, z):
    """Ry(y) . Rx(x) . Rz(z), written out (hot in builds)."""
    rx, ry, rz = math.radians(x), math.radians(y), math.radians(z)
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return [[cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx],
            [cx * sz, cx * cz, -sx],
            [-sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx]]


def matrix_euler(m):
    """(x, y, z) degrees with euler_matrix(x, y, z) == m (Ry Rx Rz)."""
    sx = max(-1.0, min(1.0, -m[1][2]))
    x = math.asin(sx)
    if abs(math.cos(x)) > 1e-6:
        y = math.atan2(m[0][2], m[2][2])
        z = math.atan2(m[1][0], m[1][1])
    else:                                   # gimbal lock: put it all in y
        y = math.atan2(-m[2][0], m[0][0])
        z = 0.0
    return [math.degrees(a) % 360 for a in (x, y, z)]


def axis_angle(axis, d):
    x, y, z = axis
    n = math.sqrt(x * x + y * y + z * z)
    x, y, z = x / n, y / n, z / n
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    t = 1 - c
    return [[t * x * x + c, t * x * y - s * z, t * x * z + s * y],
            [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
            [t * x * z - s * y, t * y * z + s * x, t * z * z + c]]


def forward(bones, root_rot, root_pos, rotations):
    """World (matrix, start, end) per bone for one frame."""
    names = [b[0] for b in bones]
    base = euler_matrix(*root_rot)
    out = []
    for i, (name, parent, length) in enumerate(bones):
        if parent in names:
            pm, _, pend = out[names.index(parent)]
        else:
            pm, pend = base, list(root_pos)
        m = _mul(pm, euler_matrix(*rotations[i]))
        d = _vec(m, [0, 0, -length])
        out.append((m, pend, [pend[k] + d[k] for k in range(3)]))
    return out


def height(hrc_text, anim_bytes):
    """Height (skeleton units) of a model in the first frame of an animation:
    the vertical span of its joints (its standing height for a stand anim)."""
    bones = skeleton(hrc_text)
    rr, rp, rots = Anim(anim_bytes).frames[0]
    ys = [p[1] for _, s, e in forward(bones, rr, rp, rots) for p in (s, e)]
    return max(ys) - min(ys)


def local_rotations(bones, root_rot, worlds):
    """Per-bone (x, y, z) giving the world matrices `worlds` (parent-relative)."""
    names = [b[0] for b in bones]
    base = euler_matrix(*root_rot)
    out = []
    for i, (name, parent, length) in enumerate(bones):
        pm = worlds[names.index(parent)] if parent in names else base
        out.append(matrix_euler(_mul(_t(pm), worlds[i])))
    return out

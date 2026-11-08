"""The intros' cameras: a flight over each race's home, written as the game's cinematic cameras
are (Cameras\\Flyby<Race>.m2 and its 00.skin, 3.3.5's model format 264, laid out as the game's own
flybys: one camera of type -1 whose position and target are Bezier tracks of one sequence, a bone
and a skin with nothing in them). The world server reads the same file to follow the camera
(M2Stores.cpp, from its data folder's Cameras), so the creatures along the flight are sent to the
game; the game reads it from the patch.

The keys are world positions (map 1); the camera's row in CinematicCamera names the origin they're
written from (its facing 0: a key is its offset from the origin, as the core's TranslateLocation
reads it)."""
import struct

FLT_MAX = 3.4028234663852886e+38


class Writer:
    def __init__(self):
        self.data = bytearray()

    def at(self):
        return len(self.data)

    def add(self, raw, align=16):
        while len(self.data) % align:
            self.data.append(0)
        start = len(self.data)
        self.data += raw
        return start


def track_header(count_offset_times, count_offset_values, interpolation=2):
    (tn, to), (vn, vo) = count_offset_times, count_offset_values
    return struct.pack("<HhIIII", interpolation, -1, tn, to, vn, vo)


def bezier_keys(points):
    """Each key with its control points (in, out): the curve through the keys, its tangent at a key
    the line from the key before to the key after (Catmull-Rom's, as Bezier control points)."""
    out = []
    n = len(points)
    for i, p in enumerate(points):
        prev = points[max(0, i - 1)]
        nxt = points[min(n - 1, i + 1)]
        d = [(nxt[k] - prev[k]) / 6.0 for k in range(3)]
        if i == 0 or i == n - 1:
            d = [0.0, 0.0, 0.0]
        out.append((tuple(p), tuple(p[k] - d[k] for k in range(3)), tuple(p[k] + d[k] for k in range(3))))
    return out


def write(name, keys, origin, fov=0.7853982):
    """[keys]: (milliseconds, (x, y, z) of the camera, (x, y, z) it looks at), in time order.
    Returns (the .m2, the 00.skin)."""
    ox, oy, oz = origin
    times = [int(k[0]) for k in keys]
    assert times == sorted(times) and times[0] == 0, times
    pos = bezier_keys([(k[1][0] - ox, k[1][1] - oy, k[1][2] - oz) for k in keys])
    tgt = bezier_keys([(k[2][0] - ox, k[2][1] - oy, k[2][2] - oz) for k in keys])
    length = times[-1]

    w = Writer()
    w.add(b"\0" * 0x130, 1)                             # the header, filled in last
    name_at = w.add(name.encode() + b"\0")
    seq = struct.pack("<HHIfIhHIII", 0, 0, length, 0.0, 0x21, 0x7FFF, 0, 0, 0, 150)
    seq += struct.pack("<6f", FLT_MAX, FLT_MAX, FLT_MAX, -FLT_MAX, -FLT_MAX, -FLT_MAX) + struct.pack("<fhH", 0.0, -1, 0)
    assert len(seq) == 64
    seq_at = w.add(seq)
    empty_track = struct.pack("<HhIIII", 0, -1, 0, 0, 0, 0)
    bone = struct.pack("<iIhHI", -1, 0, -1, 0, 0) + empty_track * 3 + struct.pack("<3f", 0, 0, 0)
    assert len(bone) == 88
    bone_at = w.add(bone)
    keybone_at = w.add(struct.pack("<h", -1))

    def keyed(values):
        times_at = w.add(struct.pack(f"<{len(times)}I", *times))
        values_at = w.add(b"".join(struct.pack("<9f", *p, *a, *b) for p, a, b in values))
        return w.add(struct.pack("<II", len(times), times_at)), w.add(struct.pack("<II", len(values), values_at))

    pos_t, pos_v = keyed(pos)
    tgt_t, tgt_v = keyed(tgt)
    roll_times = w.add(struct.pack("<2I", 0, length))
    roll_values = w.add(struct.pack("<6f", 0, 0, 0, 0, 0, 0))
    roll_t = w.add(struct.pack("<II", 2, roll_times))
    roll_v = w.add(struct.pack("<II", 2, roll_values))
    camera = struct.pack("<Ifff", 0xFFFFFFFF, fov, 27.777779, 0.22222222)
    camera += track_header((1, pos_t), (1, pos_v)) + struct.pack("<3f", 0, 0, 0)
    camera += track_header((1, tgt_t), (1, tgt_v)) + struct.pack("<3f", 0, 0, 0)
    camera += track_header((1, roll_t), (1, roll_v))
    assert len(camera) == 100
    camera_at = w.add(camera)
    lookup_at = w.add(struct.pack("<h", -1))
    while len(w.data) % 16:
        w.data.append(0)

    h = bytearray(0x130)
    struct.pack_into("<4sI", h, 0, b"MD20", 264)
    struct.pack_into("<II", h, 0x08, len(name) + 1, name_at)
    struct.pack_into("<II", h, 0x1C, 1, seq_at)
    struct.pack_into("<II", h, 0x2C, 1, bone_at)
    struct.pack_into("<II", h, 0x34, 1, keybone_at)
    struct.pack_into("<I", h, 0x44, 1)                  # one skin (Flyby<Race>00.skin)
    struct.pack_into("<6f", h, 0xA0, FLT_MAX, FLT_MAX, FLT_MAX, -FLT_MAX, -FLT_MAX, -FLT_MAX)
    struct.pack_into("<II", h, 0x110, 1, camera_at)
    struct.pack_into("<II", h, 0x118, 1, lookup_at)
    w.data[0:0x130] = h
    skin = b"SKIN" + struct.pack("<10I", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) + struct.pack("<I", 21)
    return bytes(w.data), skin


def read_positions(m2, origin=(0.0, 0.0, 0.0), facing=0.0):
    """The camera's keys as the world server reads them (M2Stores.cpp: the first point of each
    key, from the camera's position base, turned by the origin's facing): [(ms, (x, y, z))] for
    the position and for the target. For the tests."""
    import math

    def u32(at):
        return struct.unpack_from("<I", m2, at)[0]

    cam = u32(0x114)
    out = []
    for track, base in ((cam + 16, cam + 36), (cam + 48, cam + 68)):
        bx, by, bz = struct.unpack_from("<3f", m2, base)
        tn, to = struct.unpack_from("<II", m2, track + 4)
        vn, vo = struct.unpack_from("<II", m2, track + 12)
        kn, ko = struct.unpack_from("<II", m2, to)
        dn, do = struct.unpack_from("<II", m2, vo)
        keys = []
        for i in range(kn):
            t = u32(ko + i * 4)
            x, y, z = struct.unpack_from("<3f", m2, do + i * 36)
            x, y, z = bx + x, by + y, bz + z
            d = math.hypot(x, y)
            a = math.atan2(x, y) - facing
            keys.append((t, (origin[0] + d * math.sin(a), origin[1] + d * math.cos(a), origin[2] + z)))
        out.append(keys)
    return out

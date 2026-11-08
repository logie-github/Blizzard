"""The ground's height at a point, from the server data's map files (maps/MMMXXYY.map), as the core
reads it (src/server/game/Grids/GridTerrainData.cpp: the height map's two grids, v9 corners and v8
centres, four triangles to a square; holes aren't looked at)."""
import os
import struct

SIZE_OF_GRIDS = 533.3333
MAP_RESOLUTION = 128
FLAG_NO_HEIGHT, FLAG_INT16, FLAG_INT8 = 1, 2, 4


class Terrain:
    def __init__(self, maps_dir):
        self.dir = maps_dir
        self.grids = {}

    def grid(self, map_id, gx, gy):
        key = (map_id, gx, gy)
        if key not in self.grids:
            self.grids[key] = None
            path = os.path.join(self.dir, "%03d%02d%02d.map" % key)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = f.read()
                header = struct.unpack_from("<4s10I", data, 0)
                offset = header[5]
                magic, flags, base, top = struct.unpack_from("<4sIff", data, offset)
                at = offset + 16
                if magic == b"MHGT":
                    if flags & FLAG_NO_HEIGHT:
                        self.grids[key] = ("flat", base, None, None, 0)
                    elif flags & FLAG_INT16:
                        v9 = struct.unpack_from("<%dH" % (129 * 129), data, at)
                        v8 = struct.unpack_from("<%dH" % (128 * 128), data, at + 129 * 129 * 2)
                        self.grids[key] = ("int", base, v9, v8, (top - base) / 65535)
                    elif flags & FLAG_INT8:
                        v9 = struct.unpack_from("<%dB" % (129 * 129), data, at)
                        v8 = struct.unpack_from("<%dB" % (128 * 128), data, at + 129 * 129)
                        self.grids[key] = ("int", base, v9, v8, (top - base) / 255)
                    else:
                        v9 = struct.unpack_from("<%df" % (129 * 129), data, at)
                        v8 = struct.unpack_from("<%df" % (128 * 128), data, at + 129 * 129 * 4)
                        self.grids[key] = ("float", base, v9, v8, 1)
        return self.grids[key]

    def height(self, map_id, x, y):
        """The ground's height at (x, y), or None where the data has none."""
        gx, gy = max(0, int(32 - x / SIZE_OF_GRIDS)), max(0, int(32 - y / SIZE_OF_GRIDS))
        g = self.grid(map_id, gx, gy)
        if not g:
            return None
        kind, base, v9, v8, scale = g
        if kind == "flat":
            return base
        x = MAP_RESOLUTION * (32 - x / SIZE_OF_GRIDS)
        y = MAP_RESOLUTION * (32 - y / SIZE_OF_GRIDS)
        xi, yi = int(x), int(y)
        x -= xi
        y -= yi
        xi &= MAP_RESOLUTION - 1
        yi &= MAP_RESOLUTION - 1
        h1 = v9[xi * 129 + yi]
        h2 = v9[(xi + 1) * 129 + yi]
        h3 = v9[xi * 129 + yi + 1]
        h4 = v9[(xi + 1) * 129 + yi + 1]
        h5 = 2 * v8[xi * 128 + yi]
        if x + y < 1:
            if x > y:
                a, b, c = h2 - h1, h5 - h1 - h2, h1
            else:
                a, b, c = h5 - h1 - h3, h3 - h1, h1
        else:
            if x > y:
                a, b, c = h2 + h4 - h5, h4 - h2, h5 - h4
            else:
                a, b, c = h4 - h3, h3 + h4 - h5, h5 - h4
        value = a * x + b * y + c
        return value if kind == "float" else value * scale + base

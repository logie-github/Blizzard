"""soft_weights.py: the map in the repository, and a small model given its soft bones."""
import json
import os
import struct
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import soft_weights  # noqa: E402
import sl_parts  # noqa: E402

sys.path.insert(0, os.path.join(HERE, "body_shapes"))
import refine  # noqa: E402


def small_model(folder, regions):
    """A model of seven bones and, for each (uv, y, x, z) of [regions], six vertices there, all in one section drawn with
    the body's texture; every vertex on the root (bone 0) and the chest (bone 1), half each."""
    bones = [(-1, -1, (0, 0, 0)), (53, 0, (0, 0, 1.3)), (51, 0, (0, 0, 1.0)), (55, 2, (0, -0.1, 0.95)), (56, 2, (0, 0.1, 0.95)),
             (57, 3, (0, -0.1, 0.5)), (58, 4, (0, 0.1, 0.5))]
    m = bytearray(0x138)
    m[:4] = b"MD20"

    def put(off, count, payload):
        while len(m) % 16:
            m.append(0)
        struct.pack_into("<II", m, off, count, len(m))
        m.extend(payload)
    put(0x2C, len(bones), b"".join(struct.pack("<iIhHI", k, 0, p, 0, 0) + struct.pack("<hhIIII", 0, -1, 0, 0, 0, 0) * 3 + struct.pack("<3f", *pv) for k, p, pv in bones))
    verts = []
    for uv, y, x, z in regions:
        for i in range(6):
            verts.append(struct.pack("<3f", x, y, z + 0.001 * i) + bytes([128, 127, 0, 0, 0, 1, 0, 0]) + struct.pack("<3f", 1, 0, 0) + struct.pack("<4f", uv[0], uv[1], 0, 0))
    put(0x3C, len(verts), b"".join(verts))
    put(0x50, 1, struct.pack("<IIII", 1, 0, 0, 0))
    put(0x78, 2, struct.pack("<2H", 0, 1))
    put(0x80, 1, struct.pack("<H", 0))
    n = len(verts)
    sec = [0, 0, 0, n, 0, 3, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1.0]
    props = np.tile(np.array([0, 1, 0, 0], np.uint8), (n, 1))
    batch = struct.pack("<BbHHHHHHHHHHH", 16, 0, 0, 0, 0, 0xFFFF, 0, 0, 1, 0, 0, 0, 0)
    path = os.path.join(folder, "XFemale.m2")
    with open(path, "wb") as f:
        f.write(bytes(m))
    with open(path[:-3] + "00.skin", "wb") as f:
        f.write(refine.write_skin(list(range(n)), [0, 1, 2], props, [sec], batch, 1, 2))
    return path


class SoftWeights(unittest.TestCase):
    def setUp(self):
        self.doc = json.load(open(soft_weights.MAP))
        self.map = soft_weights.Map()

    def best(self, side, name):
        i, v = max(self.doc["sides"][side][name]["cells"], key=lambda c: c[1])
        n = self.doc["size"]
        return ((i % n + 0.5) / n, (i // n + 0.5) / n), v / 255.0

    def test_the_map_weighs_the_bottom_of_the_curve_most(self):
        self.assertEqual(self.doc["size"], soft_weights.GRID)
        self.assertEqual(len(self.doc["sides"]), 2)
        for side in self.doc["sides"]:
            for name in ("chest", "seat"):
                self.assertGreater(len(side[name]["cells"]), 100)
                self.assertGreater(max(v for _, v in side[name]["cells"]), 200)
                # (the curve itself: its top at h 0.45, between the fold and the tip, where it is about a third)
        curve = dict((round(h, 2), g) for h, g in self.doc["curve"])
        self.assertEqual(curve[0.45], 1.0)
        self.assertLess(curve[1.0], 0.4)
        # a place of the texture is one side's and one region's: her left chest's best cell is nothing of the others
        uv, w = self.best(0, "chest")
        got = self.map.at(np.array([uv]), np.array([0.05]))[0]
        self.assertAlmostEqual(got[0], w, delta=0.02)
        self.assertEqual((got[1], got[3]), (0, 0))
        self.assertEqual(self.map.at(np.array([uv]), np.array([-0.05]))[0][0], 0)

    def test_a_model_gets_four_bones_weighted_by_the_map(self):
        places = [(self.best(0, "chest")[0], 0.08, 0.1, 1.4), (self.best(1, "chest")[0], -0.08, 0.1, 1.4),
                  (self.best(0, "seat")[0], 0.07, -0.12, 0.98), (self.best(1, "seat")[0], -0.07, -0.12, 0.98)]
        with tempfile.TemporaryDirectory() as d:
            path = small_model(d, places)
            soft = soft_weights.soften(path, self.map)
            m = open(path, "rb").read()
            skin = open(path[:-3] + "00.skin", "rb").read()
        self.assertEqual((soft["count"], soft["parent"], [b[0] for b in soft["bones"]]), (11, 1, [7, 8]))
        self.assertEqual((soft["seat"]["parent"], [b[0] for b in soft["seat"]["bones"]]), (2, [9, 10]))
        self.assertAlmostEqual(soft["bones"][0][2], 0.08, places=4)            # each bone at the middle of what it weighs
        self.assertAlmostEqual(soft["seat"]["bones"][1][2], -0.07, places=4)
        nb, ob = struct.unpack_from("<II", m, 0x2C)
        self.assertEqual(nb, 11)
        self.assertEqual([struct.unpack_from("<ih", m, ob + i * 88 + (0 if j == 0 else 8))[0 if j == 0 else 0] for i in (7, 9) for j in (0,)], [-1, -1])
        self.assertEqual([struct.unpack_from("<h", m, ob + i * 88 + 8)[0] for i in (7, 8, 9, 10)], [1, 1, 2, 2])
        nv, ov = struct.unpack_from("<II", m, 0x3C)
        verts, idx, props, secs, batches, bn, mx = refine.read_skin(skin)
        nc, oc = struct.unpack_from("<II", m, 0x78)
        combos = struct.unpack_from("<%dH" % nc, m, oc)
        palette = combos[secs[0][7]:secs[0][7] + secs[0][6]]
        self.assertEqual(list(palette), [0, 1, 7, 8, 9, 10])
        self.assertEqual(secs[0][8], 3)
        for v in range(nv):
            r = m[ov + v * 48: ov + v * 48 + 48]
            w, b = list(r[12:16]), list(r[16:20])
            self.assertEqual(sum(w), 255)
            self.assertEqual(b[2], 7 + v // 6)                                # her region's bone, after the two of before
            self.assertGreater(w[2], 200)
            self.assertEqual([palette[props[v][j]] for j in range(3)], b[:3])
        # a man's model, or one whose texture places are nowhere on the map: nothing, and the files as they were
        with tempfile.TemporaryDirectory() as d:
            path = small_model(d, [((0.01, 0.99), 0.05, 0.1, 1.4)])
            before = open(path, "rb").read()
            self.assertIsNone(soft_weights.soften(path, self.map))
            self.assertEqual(open(path, "rb").read(), before)

    def test_the_parts_table_has_the_seat(self):
        model = {"name": "HumanFemale", "folder": "Character\\Human\\Female", "overlays": [],
                 "soft": {"count": 205, "parent": 16, "bones": [[201, 0.1, 0.08, 1.41, []], [202, 0.1, -0.08, 1.41, []]],
                          "seat": {"parent": 2, "bones": [[203, -0.1, 0.07, 1.02, []], [204, -0.1, -0.07, 1.02, []]]}}}
        with tempfile.TemporaryDirectory() as out:
            path = sl_parts.write_parts_table({"races": {"1": {"race": 1, "models": {"1": model}}}}, out, {})
            lines = [l.split("\t") for l in open(path, encoding="utf-8").read().splitlines() if not l.startswith("#")]
        self.assertEqual(lines, [
            ["B", "1", "1", "205", "16", "201", "0.10000", "0.08000", "1.41000", "", "202", "0.10000", "-0.08000", "1.41000", "", "HumanFemale"],
            ["S", "1", "1", "205", "2", "203", "-0.10000", "0.07000", "1.02000", "", "204", "-0.10000", "-0.07000", "1.02000", "", "HumanFemale"]])


if __name__ == "__main__":
    unittest.main()

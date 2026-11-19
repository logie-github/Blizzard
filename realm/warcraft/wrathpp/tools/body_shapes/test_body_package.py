"""What CI's body options package is made with (.github/workflows/wrathpp-body.yml): the designs drawn by code, the
shapes' field in the repository, the release's list. python3 -m unittest -q test_body_package"""
import json
import os
import tempfile
import unittest
import zipfile

import numpy as np
from PIL import Image

import designs
import manifest
import masks
import shapes

HERE = os.path.dirname(os.path.abspath(__file__))


class Designs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        designs.main(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_style_of_both_factions_has_a_map(self):
        for faction in ("alliance", "horde"):
            names = masks.styles(faction)
            self.assertEqual(len(names), 16)
            for name in names:
                a = np.asarray(Image.open(os.path.join(self.tmp.name, name + ".png")))
                self.assertEqual(a.shape, (200, 200, 4), name)
                self.assertGreater(int((a[..., 3] > 128).sum()), 150, name)             # something is drawn
                self.assertEqual(int(a[0, :, 3].max()), 0, name)                          # and not to the frame's edge
                ys, xs = np.where(a[..., 3] > 128)
                self.assertLess(abs(float(xs.mean()) - designs.CX), 10.0, name)         # about the middle of the body (a crescent leans)

    def test_the_full_design_is_the_width_the_layer_is_laid_out_by(self):
        index = masks.index_of(self.tmp.name)
        self.assertAlmostEqual(masks.reference_width(self.tmp.name, index), 76.0, delta=6.0)

    def test_a_design_becomes_a_texture_at_each_density(self):
        index = masks.index_of(self.tmp.name)
        covered = []
        for density in masks.DENSITIES:
            t = masks.texture(self.tmp.name, index, "heart", density)
            self.assertEqual(t.shape, (masks.SIZE, masks.SIZE, 4))
            covered.append(int(t[..., 3].astype(np.int64).sum()))
        self.assertTrue(all(a < b for a, b in zip(covered, covered[1:])), covered)       # denser, more of it
        self.assertGreater(covered[0], 0)

    def test_the_same_maps_every_time(self):
        with tempfile.TemporaryDirectory() as again:
            designs.main(again)
            for name in designs.SHAPES:
                a = np.asarray(Image.open(os.path.join(self.tmp.name, name + ".png")))
                b = np.asarray(Image.open(os.path.join(again, name + ".png")))
                self.assertTrue((a == b).all(), name)


class Field(unittest.TestCase):
    def test_the_shapes_field_in_the_repository_is_the_three_shapes(self):
        f = shapes.Field(os.path.join(HERE, "data", "human_shapes.npz"))
        n = len(f.P)
        self.assertGreater(n, 4000)
        self.assertEqual(f.D.shape, (n, 3, 3))
        self.assertEqual(f.dUV.shape, (n, 3, 2))
        reach = np.linalg.norm(f.D, axis=2).max(0)                                      # metres, per shape
        self.assertTrue((reach > 0.02).all() and (reach < 0.12).all(), reach)
        self.assertGreater(reach[2], reach[0])                                           # Voluptuous moves more than Petite


class Manifest(unittest.TestCase):
    def test_the_list_names_the_zip_its_models_and_what_it_was_made_from(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "wrathpp-body.zip")
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("wrathpp-body.json", json.dumps({"kind": "wrathpp-body", "format": 2, "models": [{}] * 88, "races": [{}] * 23}))
            m = manifest.manifest(p, "a" * 64, "b" * 64, "c0ffee")
            self.assertEqual((m["models"], m["races"], m["looks"], m["inputs"], m["format"]), (88, 23, "a" * 64, "b" * 64, 2))
            self.assertEqual(m["size"], os.path.getsize(p))
            self.assertRegex(m["sha256"], "^[0-9a-f]{64}$")
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("wrathpp-body.json", json.dumps({"kind": "wrathpp-body", "format": 1, "models": [{}]}))
            with self.assertRaises(SystemExit):
                manifest.manifest(p, "a", "b", "c")


if __name__ == "__main__":
    unittest.main()

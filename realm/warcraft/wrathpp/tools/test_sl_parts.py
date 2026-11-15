"""sl_parts.py: the pictures over the head (the head's half of a whole-skin layer, a multiplied layer made a blended one) and the parts
table the add-on reads (slots, paints with their styles, the style's choice in the colour column)."""
import json
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sl_parts  # noqa: E402

LAYOUT = {"box": (0.5, 0.0, 1.0, 1.0), "rotate": False}      # the head: the right half of the skin, all of its height


class PartsTest(unittest.TestCase):
    def test_a_whole_skin_layer_gives_its_right_half(self):
        whole = np.zeros((512, 1024, 4), np.uint8)
        whole[:, :512] = (255, 0, 0, 255)       # the body half: red (the multiply rule would also apply here: it is cut away first)
        whole[:, 512:, :3] = (0, 255, 0)
        whole[:, 512:, 3] = 128                 # the head half: green, half transparent
        out = sl_parts.overlay_picture(whole, LAYOUT)
        self.assertEqual(out.shape, (128, 256, 4))
        self.assertTrue((out[:, :, 1] > 200).all() and (out[:, :, 0] < 30).all())
        self.assertTrue((abs(out[:, :, 3].astype(int) - 128) <= 2).all())

    def test_a_layer_opaque_everywhere_is_made_a_darkening_picture(self):
        grey = np.full((512, 512, 4), 255, np.uint8)       # white (no change under multiply) with one black stroke
        grey[100:110, :, :3] = 0
        out = sl_parts.overlay_picture(grey, {"box": (0.5, 0.0, 1.0, 1.0), "rotate": False})
        self.assertTrue(out[:, :, :3].max() == 0)           # black
        self.assertEqual(int(out[:, :, 3].min()), 0)       # white: nothing
        self.assertGreater(int(out[:, :, 3].max()), 200)   # the stroke: dark

    def test_a_grey_layer_is_laid_over_not_multiplied(self):
        layer = np.full((512, 512, 4), 128, np.uint8)      # mid grey: nothing, with one dark and one light stroke
        layer[:, :, 3] = 255
        layer[100:140, :, :3] = 20
        layer[300:340, :, :3] = 240
        out = sl_parts.overlay_picture(layer, {"box": (0.5, 0.0, 1.0, 1.0), "rotate": False})
        self.assertLess(int(out[:, :, 3].min()), 4)                                  # the grey: nothing
        dark = out[(120 * 128) // 512]
        light = out[(320 * 128) // 512]
        self.assertTrue((dark[:, 3] > 150).all() and (dark[:, :3] <= 5).all())      # darkens
        self.assertTrue((light[:, 3] > 150).all() and (light[:, :3] >= 250).all())  # lightens

    def test_a_body_picture_is_the_left_half_or_the_whole_section(self):
        whole = np.zeros((512, 1024, 4), np.uint8)
        whole[:, :512] = (200, 30, 30, 160)       # the body half: red, part transparent
        whole[:, 512:] = (0, 255, 0, 255)         # the head half
        out = sl_parts.body_picture(whole)
        self.assertEqual(out.shape, (512, 512, 4))
        self.assertTrue((out[:, :, 0] > 150).all() and (abs(out[:, :, 3].astype(int) - 160) <= 2).all())
        section = np.zeros((512, 512, 4), np.uint8)
        section[:, :, 3] = 90
        self.assertEqual(sl_parts.body_picture(section).shape, (512, 512, 4))

    def test_parts_table_gives_the_body_its_own_slot(self):
        model = {"name": "TaurenMale", "folder": "Character\\Tauren\\Male", "overlays": [
            {"name": "Tattoo", "choices": [{"id": "1", "name": "None", "files": {}}, {"id": "2", "name": "Cut", "files": {"*": 5}, "body": {"*": 6}}]}]}
        looks = {"races": {"6": {"race": 6, "models": {"0": model}}}}
        with tempfile.TemporaryDirectory() as out:
            path = sl_parts.write_parts_table(looks, out, {"6_0:Tattoo": 1300})
            with open(path, encoding="utf-8") as f:
                lines = [l.split("\t") for l in f.read().splitlines() if not l.startswith("#")]
        self.assertEqual([l[0] for l in lines], ["S", "C", "T", "D"])
        self.assertTrue(lines[2][5].endswith("TaurenMaleBody.m2") and lines[2][3] == "2")
        self.assertTrue(lines[3][6].endswith("TaurenMaleBo6.blp"))

    def test_parts_table_pairs_a_paint_with_its_style(self):
        model = {"name": "OrcMale", "folder": "Character\\Orc\\Male", "overlays": [
            {"name": "Scars", "choices": [{"id": "1", "name": "None", "files": {}}, {"id": "2", "name": "Cut", "files": {"*": 77}}]},
            {"name": "War Paint Color", "depends": ["War Paint"], "choices": [{"id": "10", "name": "", "files": {"r21": 88, "r22": 99}}]},
            {"name": "War Paint", "style": True, "choices": [{"id": "20", "name": "None", "files": {}}, {"id": "21", "name": "Ghost", "files": {}}, {"id": "22", "name": "Beast", "files": {}}]}]}
        looks = {"races": {"2": {"race": 2, "models": {"0": model}}}}
        ids = {"2_0:Scars": 1210, "2_0:War Paint Color": 1211, "2_0:War Paint": 1212}
        with tempfile.TemporaryDirectory() as out:
            path = sl_parts.write_parts_table(looks, out, ids)
            lines = [l.split("\t") for l in open(path, encoding="utf-8").read().splitlines() if not l.startswith("#")]
        kinds = [l[0] for l in lines]
        self.assertEqual(kinds.count("S"), 1)
        self.assertEqual(kinds.count("P"), 1)                                   # the style takes no slot of its own
        self.assertEqual([l[1:6] for l in lines if l[0] == "P"], [["2", "0", "2", "1211", "1212"]])    # slot 2 (after the scars), colour category, style category
        colours = sorted((l[5], l[6]) for l in lines if l[0] == "C" and l[3] == "1211")
        self.assertEqual([c[0] for c in colours], ["s2", "s3"])                 # the style's choices by number: Ghost 2, Beast 3


if __name__ == "__main__":
    unittest.main()

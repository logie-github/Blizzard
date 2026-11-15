"""Tests of tools/undead_pack.py on pictures made here: a model's skin folders in their order, each skin's body half
made the 3.3.5 skin and its face cut as the model's head lies, the names of their own, the swatch, the underwear note.
Run by protocol/tests/run.sh (python3 -I; skipped where numpy or Pillow isn't installed)."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import numpy as np
    from PIL import Image
    import undead_pack
    import blp
except ImportError as missing:                  # CI's protocol job has no numpy: the looks' job runs the real thing
    np = None
    REASON = str(missing)

MODEL = {"name": "HumanFemale", "folder": "Character\\Human\\Female"}
HEAD = {"box": [0.5, 0.25, 1.0, 0.75], "rotate": False}      # the head: the face texture's middle half


@unittest.skipIf(np is None, "numpy / Pillow not installed")
class UndeadPackTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = os.path.join(self.dir.name, "HumanFemale")
        for name, colour in (("2_Ash", (150, 150, 150)), ("1_Grave Blue", (90, 110, 160)), ("notes", None)):
            os.makedirs(os.path.join(d, name))
            if colour is None:
                continue
            body = np.zeros((512, 1024, 3), np.uint8)
            body[:, :512] = colour                                  # the body's half; the right half (the head's) black
            Image.fromarray(body).save(os.path.join(d, name, "body.png"))
            face = np.zeros((512, 512, 3), np.uint8)
            face[128:384] = (200, 40, 40)                           # the head's part red, the rest black
            Image.fromarray(face).save(os.path.join(d, name, "face.png"))
        self.model_dir = d

    def tearDown(self):
        self.dir.cleanup()

    def test_skins_in_their_order_with_names_of_their_own(self):
        item, files = undead_pack.pack_model(MODEL, HEAD, self.model_dir)
        self.assertEqual([s["name"] for s in item["skins"]], ["Grave Blue", "Ash"])     # by their numbers; the folder without pictures left out
        self.assertEqual(item["skins"][0]["skin"], "Character\\Human\\Female\\HumanFemaleSkinUndead00_00.blp")
        self.assertEqual(item["skins"][1]["face"], "Character\\Human\\Female\\HumanFemaleFaceLowerUndead01.blp")
        self.assertEqual(item["underwear"], "race")
        self.assertEqual(sorted(files), sorted(s[k] for s in item["skins"] for k in ("skin", "face")))
        self.assertEqual(item["skins"][0]["swatch"], (90 << 16) | (110 << 8) | 160)

    def test_the_textures_are_what_the_models_draw(self):
        item, files = undead_pack.pack_model(MODEL, HEAD, self.model_dir)
        skin = blp.read(files[item["skins"][0]["skin"]])
        self.assertEqual(skin.shape[:2], (512, 512))                                    # the body's half, square
        self.assertTrue((abs(skin[256, 256, :3].astype(int) - (90, 110, 160)) <= 8).all())
        face = blp.read(files[item["skins"][0]["face"]])
        self.assertEqual(face.shape[:2], (128, 256))                                    # FaceLower
        self.assertTrue((abs(face[:, :, :3].astype(int) - (200, 40, 40)) <= 8).all())    # the head's part alone, none of the black round it

    def test_underwear_note(self):
        with open(os.path.join(self.model_dir, "underwear.txt"), "w") as f:
            f.write("none\n")
        self.assertEqual(undead_pack.pack_model(MODEL, HEAD, self.model_dir)[0]["underwear"], "none")
        with open(os.path.join(self.model_dir, "underwear.txt"), "w") as f:
            f.write("lace")
        with self.assertRaises(ValueError):
            undead_pack.pack_model(MODEL, HEAD, self.model_dir)


if __name__ == "__main__":
    unittest.main()

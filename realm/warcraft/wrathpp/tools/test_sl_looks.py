"""Tests of tools/sl_looks.py's character tables: a WDBC table read and written back byte for byte, and the ten races'
rows replaced by the looks' while every other race's stay (the night elves' eye glow column kept). Run by
protocol/tests/run.sh (python3 -I)."""
import os
import struct
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_looks  # noqa: E402


def wdbc(kinds, rows):
    t = sl_looks.Dbc.__new__(sl_looks.Dbc)
    t.kinds, t.rows = kinds, rows
    return t.write()


def model(name, folder):
    return {"name": name, "folder": folder, "skins": [{"index": 0, "base": 0, "pelvis": 9, "torso": 0}],
            "faces": [{"textures": {"0": 77}}], "eyes": [{"index": 0}, {"index": 1}],
            "hair": [{"variation": 0, "geoset": 1}, {"variation": 1, "geoset": 2}], "hair_colors": [{"index": 0}],
            "features": [{"variation": 0, "geosets": [1, 0, 0, 0, 2]}, {"variation": 1, "geosets": [2, 1, 0, 0, 2]}]}


LOOKS = {"races": {"4": {"race": 4, "models": {"0": model("NightElfMale", "Character\\NightElf\\Male")}}}}


class LooksTablesTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = self.dir.name
        old = [[1, 4, 0, 0, "Old\\NightElf.blp", "", "", 17, 0, 0], [2, 2, 0, 0, "Character\\Orc\\Male\\Skin.blp", "", "", 17, 0, 0],
               [3, 4, 1, 0, "Stock\\NightElfFemale.blp", "", "", 17, 0, 0]]
        with open(os.path.join(d, "CharSections.dbc"), "wb") as f:
            f.write(wdbc("iiiisssiii", old))
        with open(os.path.join(d, "CharHairGeosets.dbc"), "wb") as f:
            f.write(wdbc("iiiiii", [[5, 4, 0, 0, 1, 0], [6, 2, 0, 0, 3, 0]]))
        with open(os.path.join(d, "CharacterFacialHairStyles.dbc"), "wb") as f:
            f.write(wdbc("iiiiiiii", [[4, 0, 0, 1, 1, 1, 0, 2], [2, 0, 0, 1, 1, 1, 0, 0]]))

    def tearDown(self):
        self.dir.cleanup()

    def test_round_trip(self):
        path = os.path.join(self.dir.name, "CharSections.dbc")
        data = open(path, "rb").read()
        self.assertEqual(sl_looks.Dbc(data, "iiiisssiii").write(), data)
        self.assertEqual(data[:4], b"WDBC")
        self.assertEqual(struct.unpack_from("<4I", data, 4)[:3], (3, 10, 40))

    def test_ten_races_replaced_others_kept(self):
        t = sl_looks.tables_for(LOOKS, self.dir.name)
        sections = t["CharSections"].rows
        self.assertIn([2, 2, 0, 0, "Character\\Orc\\Male\\Skin.blp", "", "", 17, 0, 0], sections)
        self.assertNotIn("Old\\NightElf.blp", [r[4] for r in sections])
        # a sex the looks have no model for keeps the game's own rows
        self.assertIn([3, 4, 1, 0, "Stock\\NightElfFemale.blp", "", "", 17, 0, 0], sections)
        elf = [r for r in sections if r[1] == 4]
        self.assertEqual(sorted({r[3] for r in elf}), [0, 1, 3, 4])                  # skin, face, hair, underwear
        self.assertEqual(len([r for r in elf if r[3] == 1]), 2)                        # one face x two eyes
        self.assertEqual(len([r for r in elf if r[3] == 3]), 2)                        # two styles x one colour
        self.assertEqual(len({r[0] for r in sections}), len(sections))                 # ids unique
        hair = t["CharHairGeosets"].rows
        self.assertEqual([r[3:5] for r in hair if r[1] == 4], [[0, 1], [1, 2]])
        self.assertIn([6, 2, 0, 0, 3, 0], hair)
        facial = t["CharacterFacialHairStyles"].rows
        self.assertEqual([r for r in facial if r[0] == 4], [[4, 0, 0, 1, 0, 0, 0, 2], [4, 0, 1, 2, 1, 0, 0, 2]])
        self.assertIn([2, 0, 0, 1, 1, 1, 0, 0], facial)
        # and they write as the game reads them
        for name, kinds in sl_looks.TABLE_KINDS.items():
            blob = t[name].write()
            self.assertEqual(sl_looks.Dbc(blob, kinds).rows, t[name].rows)


if __name__ == "__main__":
    unittest.main()

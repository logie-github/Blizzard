"""Tests of tools/sl_looks.py's change files: the ten races' rows of CharSections, CharHairGeosets and the facial table as
change files (drop their race and sex, put theirs) applied by tools/apply_client.py to tables with other races' rows and a
race and sex the looks have no model for; and the merge of change files. Run by protocol/tests/run.sh (python3 -I)."""
import os
import struct
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_client as A  # noqa: E402
import sl_looks  # noqa: E402


def wdbc(kinds, rows):
    text = bytearray(b"\0")
    recs = []
    for r in rows:
        rec = bytearray()
        for k, v in zip(kinds, r):
            if k == "s":
                rec += struct.pack("<I", len(text)); text += v.encode() + b"\0"
            else:
                rec += struct.pack("<I", v)
        recs.append(bytes(rec))
    n = len(kinds)
    return struct.pack("<4s4I", b"WDBC", len(recs), n, n * 4, len(text)) + b"".join(recs) + bytes(text)


def model(name, folder):
    return {"name": name, "folder": folder, "skins": [{"index": 0, "base": 0, "pelvis": 9, "torso": 0}],
            "faces": [{"textures": {"0": 77}}], "eyes": [{"index": 0}, {"index": 1}],
            "hair": [{"variation": 0, "geoset": 1}, {"variation": 1, "geoset": 2}], "hair_colors": [{"index": 0}],
            "features": [{"variation": 0, "geosets": [1, 0, 0, 0, 2]}, {"variation": 1, "geosets": [2, 1, 0, 0, 2]}]}


LOOKS = {"races": {"4": {"race": 4, "replace_rows": True, "models": {"0": model("NightElfMale", "Character\\NightElf\\Male")}},
                   "29": {"race": 29, "models": {"0": model("VoidElfMale", "Character\\VoidElf\\Male")}}}}


class ChangesTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = self.dir.name
        with open(os.path.join(d, "CharacterFacialHairStyles.dbc"), "wb") as f:
            f.write(wdbc("iiiiiiii", [[4, 0, 0, 1, 1, 1, 0, 2], [2, 0, 0, 1, 1, 1, 0, 0]]))

    def tearDown(self):
        self.dir.cleanup()

    def table(self, kinds, rows):
        return A.Table(wdbc(kinds, rows))

    def test_ten_races_replaced_others_kept(self):
        ch = sl_looks.looks_changes(LOOKS, self.dir.name)
        self.assertEqual(sorted(ch), ["CharHairGeosets", "CharSections", "CharacterFacialHairStyles"])
        t = self.table("iiiisssiii", [[1, 4, 0, 0, "Old\\NightElf.blp", "", "", 17, 0, 0], [2, 2, 0, 0, "Orc.blp", "", "", 17, 0, 0],
                                      [3, 4, 1, 0, "Stock\\NightElfFemale.blp", "", "", 17, 0, 0]])
        A.apply(t, ch["CharSections"])
        names = []
        for i in range(len(t.records)):
            o = t.get(i, 4)
            names.append(bytes(t.text[o:t.text.index(b"\0", o)]).decode())
        self.assertNotIn("Old\\NightElf.blp", names)
        self.assertIn("Orc.blp", names)
        self.assertIn("Stock\\NightElfFemale.blp", names)            # a sex the looks have no model for keeps the game's own rows
        elf = [i for i in range(len(t.records)) if t.get(i, 1) == 4 and t.get(i, 2) == 0]
        self.assertEqual(sorted({t.get(i, 3) for i in elf}), [0, 1, 3, 4])      # skin, face, hair, underwear
        self.assertEqual(len([i for i in elf if t.get(i, 3) == 1]), 2)         # one face x two eyes
        self.assertEqual(len({t.get(i, 0) for i in range(len(t.records))}), len(t.records))
        h = self.table("iiiiii", [[5, 4, 0, 0, 1, 0], [6, 2, 0, 0, 3, 0]])
        A.apply(h, ch["CharHairGeosets"])
        self.assertEqual(sorted((h.get(i, 1), h.get(i, 3), h.get(i, 4)) for i in range(len(h.records))), [(2, 0, 3), (4, 0, 1), (4, 1, 2)])
        f = A.Table(open(os.path.join(self.dir.name, "CharacterFacialHairStyles.dbc"), "rb").read())
        A.apply(f, ch["CharacterFacialHairStyles"])
        rows = [[f.get(i, k) for k in range(8)] for i in range(len(f.records))]
        self.assertIn([2, 0, 0, 1, 1, 1, 0, 0], rows)
        self.assertEqual([r for r in rows if r[0] == 4], [[4, 0, 0, 1, 0, 0, 0, 2], [4, 0, 1, 2, 1, 0, 0, 2]])   # the glow column kept

    def test_a_race_without_replace_rows_has_no_changes(self):
        self.assertEqual(sl_looks.looks_changes({"races": {"29": LOOKS["races"]["29"]}}, self.dir.name), {})

    def test_merge(self):
        a, b, out = (os.path.join(self.dir.name, n) for n in ("a", "b", "out"))
        os.makedirs(a); os.makedirs(b)
        open(os.path.join(a, "T.txt"), "w").write("types\tii\nput\t1\t2\n")
        open(os.path.join(b, "T.txt"), "w").write("put\t3\t4\n")
        open(os.path.join(b, "U.txt"), "w").write("put\t5\t6\n")
        self.assertEqual(sl_looks.merge_changes(out, a, b, os.path.join(self.dir.name, "none")), ["T.txt", "U.txt"])
        self.assertEqual(open(os.path.join(out, "T.txt")).read(), "types\tii\nput\t1\t2\nput\t3\t4\n")


if __name__ == "__main__":
    unittest.main()

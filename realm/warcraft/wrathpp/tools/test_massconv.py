"""massconv.py: a tiny package (one race, both models, tables) audited clean, then with each fault put in."""
import json
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import massconv  # noqa: E402


def write_dbc(path, rows, fields=None, strings=b"\0", byte_rows=False):
    if byte_rows:
        body = b"".join(bytes(r) for r in rows)
        head = struct.pack("<4sIIII", b"WDBC", len(rows), len(rows[0]), len(rows[0]), len(strings))
    else:
        body = b"".join(struct.pack("<%dI" % len(r), *r) for r in rows)
        head = struct.pack("<4sIIII", b"WDBC", len(rows), len(rows[0]), len(rows[0]) * 4, len(strings))
    with open(path, "wb") as f:
        f.write(head + body + strings)


class MassconvTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.looks = self.dir.name
        os.makedirs(os.path.join(self.looks, "dbc"))
        self.model_dir = os.path.join(self.looks, "client", "Character", "Worgen", "Male")
        os.makedirs(self.model_dir)

    def tearDown(self):
        self.dir.cleanup()

    def package(self, with_model=True, with_skin=True, outfit=True):
        d = os.path.join(self.looks, "dbc")
        strings = b"\0Character\\Worgen\\Male\\WorgenMale.mdx\0"
        write_dbc(os.path.join(d, "ChrRaces.dbc"), [(12, 0, 0, 0, 100, 100)])
        write_dbc(os.path.join(d, "CreatureDisplayInfo.dbc"), [(100, 200)])
        write_dbc(os.path.join(d, "CreatureModelData.dbc"), [(200, 0, 1)], strings=strings)
        write_dbc(os.path.join(d, "CharSections.dbc"), [(1, 12, 0, 0, 0, 0, 0, 1, 0, 0), (2, 12, 0, 1, 0, 0, 0, 1, 0, 0), (3, 12, 0, 3, 0, 0, 0, 1, 0, 0)])
        write_dbc(os.path.join(d, "CharBaseInfo.dbc"), [(12, 1)], byte_rows=True)
        write_dbc(os.path.join(d, "CharStartOutfit.dbc"), [(1, 12 | (1 << 8) | (0 << 16)) + (0,)] if outfit else [(1, 99)])
        if with_model:
            open(os.path.join(self.model_dir, "WorgenMale.m2"), "wb").write(b"MD20" + struct.pack("<I", 264) + b"\0" * 400)
        if with_skin:
            open(os.path.join(self.model_dir, "WorgenMale00.skin"), "wb").write(b"SKIN")

    def audit(self, **race):
        manifest = {"races": [dict({"id": 12, "name": "Worgen", "token": "Worgen", "needs": {}}, **race)]}
        path = os.path.join(self.looks, "m.json")
        json.dump(manifest, open(path, "w"))
        problems = []
        tables = massconv.load_tables(self.looks)
        massconv.audit_race(self.looks, manifest["races"][0], tables, [], problems)
        return [t for _, t in problems]

    def test_a_complete_race_is_clean_apart_from_the_models_structure(self):
        self.package()
        found = self.audit()
        self.assertFalse([t for t in found if "not in the package" in t or "no 00.skin" in t], found)

    def test_a_missing_model_file_is_named(self):
        self.package(with_model=False)
        self.assertTrue(any("WorgenMale.mdx" in t and "not in the package" in t for t in self.audit()))

    def test_a_missing_skin_is_named(self):
        self.package(with_skin=False)
        self.assertTrue(any("no 00.skin" in t for t in self.audit()))

    def test_a_race_without_a_display_row_is_named(self):
        self.package()
        write_dbc(os.path.join(self.looks, "dbc", "CreatureDisplayInfo.dbc"), [(999, 200)])
        self.assertTrue(any("CreatureDisplayInfo has no such row" in t for t in self.audit()))

    def test_a_class_without_its_outfit_is_named(self):
        self.package(outfit=False)
        self.assertTrue(any("CharStartOutfit has no row" in t for t in self.audit()))

    def test_the_creators_not_drawn_options_are_named(self):
        self.package()
        problems = []
        massconv.audit_race(self.looks, {"id": 12, "name": "Worgen", "token": "Worgen", "needs": {}}, massconv.load_tables(self.looks),
                            ["WorgenMale: 4 options drawn (Face); not drawn yet: Fur Color, Ears"], problems)
        self.assertTrue(any("not drawn yet: Fur Color, Ears" in t for _, t in problems))

    def test_a_zone_tile_that_is_listed_and_missing_is_named(self):
        maps = os.path.join(self.looks, "World", "Maps", "Z")
        os.makedirs(maps)
        main = bytearray(64 * 64 * 8)
        struct.pack_into("<I", main, 0, 1)
        open(os.path.join(maps, "Z.wdt"), "wb").write(b"NIAM" + struct.pack("<I", len(main)) + bytes(main))
        problems = []
        massconv.audit_zone(self.looks, {"name": "Z", "map": "Z"}, problems)
        self.assertTrue(any("tile 0_0 is listed" in t for _, t in problems), problems)


if __name__ == "__main__":
    unittest.main()

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
            "hair": [{"variation": 0, "geoset": 1, "scalp": {"0": 555}}, {"variation": 1, "geoset": 2, "scalp": {"*": 556}}],
            "hair_colors": [{"index": 0}],
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

    def test_hair_rows_carry_the_scalp(self):
        """a hair row's second texture is the style's scalp for its colour (or for any colour), a style with none has none"""
        t = sl_looks.tables_for(LOOKS, self.dir.name)
        hair = {r[8]: r for r in t["CharSections"].rows if r[1] == 4 and r[3] == 3}
        self.assertEqual(hair[0][5], "Character\\NightElf\\Male\\NightElfMaleScalp555.blp")
        self.assertEqual(hair[1][5], "Character\\NightElf\\Male\\NightElfMaleScalp556.blp")
        self.assertEqual(hair[0][4], hair[1][4])                                           # the hair texture itself is the colour's

    def test_overlays_of_takes_the_head_pictures_of_an_option(self):
        """an option whose pictures hang on its choices (for any colour, or for a hair colour's index) and lie over the head is an
        overlay; one whose layer is the body's, or that a slider carries, is not"""
        class Stub:
            layers = [{"CharComponentTextureLayoutsID": "7", "ChrModelTextureTargetID_0": "29", "TextureType": "1", "TextureSectionTypeBitMask": "512"},
                      {"CharComponentTextureLayoutsID": "7", "ChrModelTextureTargetID_0": "8", "TextureType": "1", "TextureSectionTypeBitMask": "512"},
                      {"CharComponentTextureLayoutsID": "7", "ChrModelTextureTargetID_0": "13", "TextureType": "1", "TextureSectionTypeBitMask": "32"}]
            chr_models = {"2": {"CharComponentTextureLayoutID": "7"}}
            options = {"1": {"ID": "1", "ChrModelID": "2", "Name_lang": "Makeup", "OrderIndex": "1"},
                       "2": {"ID": "2", "ChrModelID": "2", "Name_lang": "Eyebrows", "OrderIndex": "2"},
                       "3": {"ID": "3", "ChrModelID": "2", "Name_lang": "Underwear", "OrderIndex": "3"},
                       "4": {"ID": "4", "ChrModelID": "2", "Name_lang": "Hair Style", "OrderIndex": "4"}}
            choice = {"1": [{"ID": "10", "Name_lang": "None"}, {"ID": "11", "Name_lang": "Smokey"}],
                      "2": [{"ID": "20", "Name_lang": "Soft"}], "3": [{"ID": "30", "Name_lang": "Lace"}]}
            elements = {"11": [{"ChrCustomizationMaterialID": "m1", "RelatedChrCustomizationChoiceID": "0"}],
                        "20": [{"ChrCustomizationMaterialID": "m2", "RelatedChrCustomizationChoiceID": "c5"}],
                        "30": [{"ChrCustomizationMaterialID": "m3", "RelatedChrCustomizationChoiceID": "0"}]}
            materials = {"m1": ("29", [111]), "m2": ("8", [222]), "m3": ("13", [333])}

            choices = type("C", (dict,), {"__missing__": lambda self, k: []})(choice)

            def option_choices(self, chr_model, name, only_available=True):
                key = {"Makeup": "1", "Eyebrows": "2", "Underwear": "3"}.get(name)
                return self.choice.get(key, [])

            def available(self, choice):
                return True

            def material_files(self, element):
                return self.materials[element["ChrCustomizationMaterialID"]]
        Stub.elements = type("E", (dict,), {"__missing__": lambda self, k: []})(Stub.elements)
        model = {"hair_colors": [{"index": 3, "choice": "c5"}], "feature_options": []}
        out = sl_looks.overlays_of(Stub(), 2, model)
        self.assertEqual([o["name"] for o in out], ["Makeup", "Eyebrows"])                   # the body's (mask 32) is not one
        self.assertEqual(out[0]["choices"][1]["files"], {"*": 111})
        self.assertEqual(out[1]["choices"][0]["files"], {"3": 222})                           # the hair colour's index
        self.assertEqual(out[0]["target"], "29")

    def test_overlays_of_pairs_a_paint_with_its_style(self):
        """a paint's colour whose pictures name the style's choices is an overlay that depends on the style; the style (no picture of its
        own) is listed beside it, kept; a layer of another texture type (a horn's colour) is none"""
        class Stub:
            layers = [{"CharComponentTextureLayoutsID": "7", "ChrModelTextureTargetID_0": "17", "TextureType": "1", "TextureSectionTypeBitMask": "-1"},
                      {"CharComponentTextureLayoutsID": "7", "ChrModelTextureTargetID_0": "40", "TextureType": "10", "TextureSectionTypeBitMask": "-1"}]
            chr_models = {"2": {"CharComponentTextureLayoutID": "7"}}
            options = {"1": {"ID": "1", "ChrModelID": "2", "Name_lang": "War Paint Color", "OrderIndex": "2"},
                       "2": {"ID": "2", "ChrModelID": "2", "Name_lang": "War Paint", "OrderIndex": "1"},
                       "3": {"ID": "3", "ChrModelID": "2", "Name_lang": "Horn Color", "OrderIndex": "3"}}
            choices = {"1": [{"ID": "10", "Name_lang": "", "OrderIndex": "0", "ChrCustomizationReqID": "0"}],
                       "2": [{"ID": "20", "Name_lang": "None", "OrderIndex": "0", "ChrCustomizationReqID": "0"},
                             {"ID": "21", "Name_lang": "Ghost", "OrderIndex": "1", "ChrCustomizationReqID": "0"}],
                       "3": [{"ID": "30", "Name_lang": "Red", "OrderIndex": "0", "ChrCustomizationReqID": "0"}]}
            elements = {"10": [{"ChrCustomizationMaterialID": "m1", "RelatedChrCustomizationChoiceID": "21"}],
                        "30": [{"ChrCustomizationMaterialID": "m2", "RelatedChrCustomizationChoiceID": "0"}]}
            materials = {"m1": ("17", [555]), "m2": ("40", [666])}
            reqs = {}

            def option_choices(self, chr_model, name, only_available=True):
                key = {"War Paint Color": "1", "War Paint": "2", "Horn Color": "3"}[name]
                return self.choices[key]

            def available(self, choice):
                return True

            def material_files(self, element):
                return self.materials[element["ChrCustomizationMaterialID"]]
        Stub.elements = type("E", (dict,), {"__missing__": lambda self, k: []})(Stub.elements)
        Stub.choices = type("C", (dict,), {"__missing__": lambda self, k: []})(Stub.choices)
        out = sl_looks.overlays_of(Stub(), 2, {"hair_colors": [], "feature_options": []})
        self.assertEqual([(o["name"], o.get("depends"), o.get("style")) for o in out], [("War Paint Color", ["War Paint"], None), ("War Paint", None, True)])
        self.assertEqual(out[0]["choices"][0]["files"], {"r21": 555})
        self.assertEqual([c["id"] for c in out[1]["choices"]], ["20", "21"])

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

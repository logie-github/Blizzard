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
            "hair": [{"variation": 0, "geoset": 1, "scalp": {"0": 555}}, {"variation": 1, "geoset": 2, "scalp": {"*": 556}}],
            "hair_colors": [{"index": 0}],
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

    def test_hair_rows_carry_the_scalp(self):
        """a hair row's second texture is the style's scalp for its colour (or for any colour), a style with none has none"""
        ch = sl_looks.looks_changes(LOOKS, self.dir.name)
        t = self.table("iiiisssiii", [])
        A.apply(t, ch["CharSections"])
        def text(i, f):
            o = t.get(i, f)
            return bytes(t.text[o:t.text.index(b"\0", o)]).decode()
        hair = {t.get(i, 9): (text(i, 4), text(i, 5)) for i in range(len(t.records)) if t.get(i, 1) == 4 and t.get(i, 3) == 3 and t.get(i, 8) == 0}
        by_style = {t.get(i, 8): (text(i, 4), text(i, 5)) for i in range(len(t.records)) if t.get(i, 1) == 4 and t.get(i, 3) == 3}
        self.assertEqual(by_style[0][1], "Character\\NightElf\\Male\\NightElfMaleScalp555.blp")
        self.assertEqual(by_style[1][1], "Character\\NightElf\\Male\\NightElfMaleScalp556.blp")
        self.assertEqual(by_style[0][0], by_style[1][0])                                   # the hair texture itself is the colour's

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

    def test_the_dark_troll_is_the_trolls_look_under_its_own_name(self):
        troll = {"race": 8, "name": "Troll", "replace_rows": True,
                 "models": {"0": {"folder": "Character\\Troll\\Male", "name": "TrollMale", "skins": [{"index": 0}, {"index": 1}], "faces": [], "hair": []}}}
        dt = sl_looks.dark_troll(troll)
        self.assertEqual(dt["alias_of"], "8")
        self.assertEqual(dt["name"], "DarkTroll")
        self.assertFalse(dt["replace_rows"])
        self.assertEqual(dt["models"]["0"]["model_path"], "Character\\Troll\\Male\\TrollMale.mdx")
        self.assertEqual(dt["models"]["0"]["skins"], troll["models"]["0"]["skins"])
        self.assertNotIn("model_path", troll["models"]["0"])                       # (the Troll's own entry is left alone)

    def test_an_alias_finds_its_target_among_the_ten_beside_the_file(self):
        import json, tempfile, os
        d = tempfile.mkdtemp()
        json.dump({"build": "x", "races": {"8": {"race": 8, "models": {"0": {"part_types": {"Horns": [1, 2]}}}}}}, open(os.path.join(d, "looks.json"), "w"))
        races = os.path.join(d, "races.json")
        json.dump({"darktroll": {"alias_of": "8", "models": {"0": {}}}}, open(races, "w"))
        looks = sl_looks.load_looks(races)
        target = sl_looks.alias_target(looks, races, looks["races"]["darktroll"])
        self.assertEqual(target["models"]["0"]["part_types"], {"Horns": [1, 2]})
        self.assertIsNone(sl_looks.alias_target(looks, races, {"alias_of": "99"}))
        self.assertIsNone(sl_looks.alias_target(looks, races, {}))

    def test_load_looks_takes_both_shapes(self):
        a = os.path.join(self.dir.name, "a.json"); b = os.path.join(self.dir.name, "b.json")
        import json
        json.dump({"build": "x", "races": {"4": {"race": 4}}}, open(a, "w"))
        json.dump({"voidelf": {"race": 29, "models": {}}}, open(b, "w"))
        self.assertEqual(list(sl_looks.load_looks(a)["races"]), ["4"])
        self.assertEqual(list(sl_looks.load_looks(b)["races"]), ["voidelf"])

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

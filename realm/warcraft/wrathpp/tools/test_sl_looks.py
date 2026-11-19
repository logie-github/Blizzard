"""Tests of tools/sl_looks.py's change files: the ten races' rows of CharSections, CharHairGeosets and the facial table as
change files (drop their race and sex, put theirs) applied by tools/apply_client.py to tables with other races' rows and a
race and sex the looks have no model for; and the merge of change files. Run by protocol/tests/run.sh (python3 -I)."""
import os
import struct
import sys
import tempfile
import unittest
from unittest import mock

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


class FurTest(unittest.TestCase):
    """a race whose model has fur (today's texture type 8) and no hair colours: the Worgen"""

    def test_a_skin_with_an_extra_names_it_and_a_race_without_hair_colours_has_a_hair_row_a_style(self):
        m = model("WorgenFemale", "Character\\Worgen\\Female")
        m["skins"] = [{"index": 0, "base": 0, "pelvis": 9, "torso": 0, "extra": 3057320}, {"index": 1, "base": 1, "pelvis": 0, "torso": 0}]
        m["hair_colors"] = []
        sections, hair, facial = sl_looks.table_rows({"races": {"12": {"race": 12, "models": {"1": m}}}})
        skins = [r for r in sections if r[2] == 0]
        self.assertEqual([r[4] for r in skins], ["Character\\Worgen\\Female\\WorgenFemaleSkin00_00_Extra.blp", ""])
        rows = [r for r in sections if r[2] == 3]
        self.assertEqual([(r[3], r[4], r[7], r[8]) for r in rows], [("", "", 0, 0), ("", "", 1, 0)])      # every style, colour 0, no texture
        self.assertEqual(len(hair), 2)

    def test_the_worgen_s_ears_are_on_the_feature_slider(self):
        self.assertEqual(sl_looks.FEATURES[(12, 0)][0], ["Ears", "Facial Hair"])
        self.assertEqual(sl_looks.FEATURES[(12, 1)][0], ["Ears"])


class LooksLastTest(unittest.TestCase):
    def test_the_looks_character_rows_go_after_a_module_s(self):
        """the first dir's CharSections (the looks' drop and put of a race) after the other dirs', so a module's rows of that race are
        dropped; its other tables in the dirs' order"""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            looks, module, out = (os.path.join(d, x) for x in ("looks", "module", "out"))
            for where, text in ((looks, "looks"), (module, "module")):
                os.makedirs(where)
                for name in ("CharSections.txt", "ChrRaces.txt"):
                    with open(os.path.join(where, name), "w") as f:
                        f.write(text + "\n")
            sl_looks.merge_changes(out, looks, module)
            self.assertEqual(open(os.path.join(out, "CharSections.txt")).read(), "module\nlooks\n")
            self.assertEqual(open(os.path.join(out, "ChrRaces.txt")).read(), "looks\nmodule\n")


def npc_model():
    """A model as the looks have one: 3.3.5's 4 skins were choices 100 to 103 (102 a creature's own, left out), a new one 900; 2 faces
    of 3.3.5's and a death knight's two (left out), 3 eye colours; 3 hair styles, 2 colours; a feature slider of two options (3 x 2)."""
    return {"name": "TestMale", "folder": "Character\\Test\\Male",
            "skins": [{"index": 0, "choice": "100"}, {"index": 1, "choice": "101"}, {"index": 2, "choice": "103"}, {"index": 3, "choice": "900"}],
            "faces": [{"choice": "200"}, {"choice": "201"}], "eyes": [{"index": 0}, {"index": 1}, {"index": 2}],
            "hair": [{"variation": 0, "choice": "300", "geoset": 0}, {"variation": 1, "choice": "301", "geoset": 2}, {"variation": 2, "choice": "302", "geoset": 3}],
            "hair_colors": [{"index": 0, "choice": "400"}, {"index": 1, "choice": "401"}],
            "feature_options": ["Beard", "Mustache"], "feature_sizes": [3, 2],
            "features": [{"variation": 0, "geosets": [0, 0, 0, 0, 2]}, {"variation": 1, "geosets": [0, 2, 0, 0, 2]}, {"variation": 2, "geosets": [2, 0, 0, 0, 2]},
                         {"variation": 3, "geosets": [2, 2, 0, 0, 2]}, {"variation": 4, "geosets": [3, 0, 0, 0, 2]}, {"variation": 5, "geosets": [3, 2, 0, 0, 2]}]}


class NpcTest(unittest.TestCase):
    """The creatures' looks: 3.3.5's five numbers made the looks' (npc_numbers), the rule for CreatureDisplayInfoExtra (npc_changes)."""
    CLASSIC = {"skins": 4, "faces": 4, "hair": 3, "colours": 2, "facial": {0: (1, 1, 1), 1: (3, 2, 1), 2: (2, 1, 1)}}

    def test_numbers_by_the_choices_in_a_row(self):
        n = sl_looks.npc_numbers(npc_model(), 50, 0, self.CLASSIC)
        # skins: 3.3.5's 0, 1 and 3 are the looks' 0, 1, 2; its 2 (a creature's own: the looks haven't it) takes 0's place (two back: the
        # looks' first run is two long), and a number 3.3.5 hasn't the same way; never the looks' new skin by its place
        self.assertEqual([n["skin"][i] for i in range(6)], [0, 1, 0, 2, 0, 1])
        # a face is the face with the first eye colour (3 eye colours); a death knight's face (2, 3) its own face
        self.assertEqual([n["face"][i] for i in range(4)], [0, 3, 0, 3])
        self.assertEqual([n["hair"][i] for i in range(4)], [0, 1, 2, 0])
        self.assertEqual([n["colour"][i] for i in range(3)], [0, 1, 0])
        # the feature slider by 3.3.5's geosets (its "none" is geoset 1, today's 0): (1,1,1) nothing, (3,2,1) beard 3 moustache 2
        self.assertEqual([n["facial"][(0, i)] for i in range(4)], [0, 5, 2, 0])
        self.assertFalse(n["hair_in_features"])

    def test_a_race_3_3_5_hasnt_takes_every_choice_in_the_run(self):
        n = sl_looks.npc_numbers(npc_model(), 50, 0, None)
        self.assertEqual([n["skin"][i] for i in range(5)], [0, 1, 0, 2, 0])
        self.assertEqual([n["facial"][(0, i)] for i in range(3)], [0, 0, 0])

    def test_the_feature_slider_by_one_option_and_the_hair_gone_into_it(self):
        m = npc_model()
        m["feature_options"] = ["Horn Style", "Facial Hair"]
        n = sl_looks.npc_numbers(m, 6, 0, self.CLASSIC)       # (the Tauren men: CLASSIC_HAIR and CLASSIC_FEATURE)
        self.assertTrue(n["hair_in_features"])
        self.assertEqual(n["facial"][(0, 0)], 0)
        self.assertEqual(n["facial"][(2, 1)], 2 * 2 + 1)      # horns 2, facial hair 1
        self.assertEqual(n["facial"][(4, 3)], 1 * 2 + 1)      # past the options' choices: around again
        self.assertEqual(set(n["hair"].values()), {0})
        m["feature_sizes"] = [9, 9]                           # digits that don't make the features: the first feature
        self.assertEqual(set(sl_looks.npc_numbers(m, 6, 0, self.CLASSIC)["facial"].values()), {0})

    def test_the_rule_on_a_table(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "CharSections.dbc"), "wb") as f:      # 3.3.5's race 50: 4 skins, 4 faces, 3 hair styles x 2 colours
                rows = [[i + 1, 50, 0, 0, "", "", "", 1, 0, i] for i in range(4)] + [[10 + i, 50, 0, 1, "", "", "", 1, i, 0] for i in range(4)]
                rows += [[20 + v * 2 + c, 50, 0, 3, "", "", "", 1, v, c] for v in range(3) for c in range(2)]
                f.write(wdbc("iiiisssiii", rows))
            with open(os.path.join(d, "CharacterFacialHairStyles.dbc"), "wb") as f:
                f.write(wdbc("iiiiiiii", [[50, 0, 0, 1, 1, 1, 0, 0], [50, 0, 1, 3, 2, 1, 0, 0]]))
            looks = {"races": {"50": {"race": 50, "replace_rows": True, "models": {"0": npc_model()}},
                               "29": {"race": 29, "models": {"0": npc_model()}}}}
            text = sl_looks.npc_changes(looks, d)
            self.assertEqual(sl_looks.npc_changes({"races": {"29": looks["races"]["29"]}}, d), "")
        self.assertNotIn("=29", text)
        self.assertFalse([l for l in text.split("\n") if l.endswith("\t")])    # (a rule with nothing listed: its default alone)
        # id race sex skin face hair colour facial 11 items flags bake: a creature of the race, one of its women, one of another race
        extra = [[1, 50, 0, 3, 1, 2, 1, 1] + [0] * 12 + ["a.blp"], [2, 50, 1, 3, 1, 2, 1, 1] + [0] * 12 + ["b.blp"],
                 [3, 7, 0, 3, 1, 2, 1, 1] + [0] * 12 + ["c.blp"], [4, 50, 0, 2, 3, 200, 9, 77] + [5] * 12 + ["d.blp"]]
        t = A.Table(wdbc(sl_looks.EXTRA_KINDS, extra))
        A.apply(t, text)
        got = [[t.get(i, f) for f in range(8)] for i in range(4)]
        self.assertEqual(got[0], [1, 50, 0, 2, 3, 2, 1, 5])
        self.assertEqual(got[1], [2, 50, 1, 3, 1, 2, 1, 1])                 # (the looks have no woman of it: left)
        self.assertEqual(got[2], [3, 7, 0, 3, 1, 2, 1, 1])
        self.assertEqual(got[3], [4, 50, 0, 0, 3, 0, 1, 0])                 # a creature's own skin, a death knight's face, numbers past the list
        self.assertEqual([t.get(3, f) for f in range(8, 20)], [5] * 12)     # its items as they were
        with self.assertRaises(ValueError):                                 # another table: refused by its shape
            A.apply(A.Table(wdbc("iiii", [[1, 50, 0, 3]])), text)

    def test_the_list_for_the_native_mod(self):
        with tempfile.TemporaryDirectory() as d:
            sl_looks.write_npc_list({"races": {"4": {"race": 4, "models": {"0": {}, "1": {}}}, "11": {"race": 11, "models": {"1": {}}}}}, d)
            sl_looks.write_npc_list({"races": {"x": {"race": 15, "models": {"0": {}}}, "4": {"race": 4, "models": {"0": {}}}}}, d)   # the allied races' run
            with open(os.path.join(d, "Wrathpp", "npc.txt"), encoding="utf-8") as f:
                lines = [l.rstrip("\n") for l in f]
        self.assertTrue(lines[0].startswith("#"))
        self.assertEqual(lines[1:], ["4\t0", "4\t1", "11\t1", "15\t0"])

    def test_the_whole_skins_list_for_the_native_mod(self):
        with tempfile.TemporaryDirectory() as d:
            folder = os.path.join(d, "Character", "Human", "Female")
            os.makedirs(folder)
            os.makedirs(os.path.join(d, "Character", "Orc", "Male"))
            head = bytearray(304)
            struct.pack_into("<I", head, 60, 33953)
            for name, data in (("HumanFemale.m2", bytes(head) + bytes(96)), ("HumanFemale00.skin", b"SKIN"), ("HumanFemale00w.skin", b"SKIN")):
                with open(os.path.join(folder, name), "wb") as f:
                    f.write(data)
            for name in ("OrcMale.m2", "OrcMale00.skin"):                    # a model nothing was cut of: no whole skin, not listed
                with open(os.path.join(d, "Character", "Orc", "Male", name), "wb") as f:
                    f.write(bytes(head))
            self.assertEqual(sl_looks.write_wide_list(d), 1)
            with open(os.path.join(d, "Wrathpp", "wide.txt"), encoding="utf-8") as f:
                lines = [l.rstrip("\n") for l in f]
            self.assertTrue(lines[0].startswith("#"))
            self.assertEqual(lines[1:], ["Character\\Human\\Female\\HumanFemale\t33953\t400"])
            os.remove(os.path.join(folder, "HumanFemale00.skin"))            # a whole skin with no skin of its own beside it: refused
            with self.assertRaises(ValueError):
                sl_looks.write_wide_list(d)

    def test_the_rule_goes_after_the_other_dirs(self):
        self.assertIn("CreatureDisplayInfoExtra.txt", sl_looks.LOOKS_LAST)


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
        self.assertEqual(sorted(ch), ["CharHairGeosets", "CharSections", "CharacterFacialHairStyles", "CreatureDisplayInfoExtra"])
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

    def test_an_alias_finds_its_target_among_the_ten_beside_the_file(self):
        import json, tempfile, os
        patch = mock.patch.object(sl_looks, "BASE_ONLY", False)       # (today's pieces: a part_types to find)
        patch.start()
        self.addCleanup(patch.stop)
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


def tables(options, choices, elements, geosets):
    """sl_looks' Tables over a few rows (no CSVs): options {id: (model, name)}, choices {option: [choice ids]}, elements {choice: [geoset
    row ids]}, geosets {row id: (type, id)}."""
    t = sl_looks.Tables.__new__(sl_looks.Tables)
    t.aliases, t.only_available, t.unlocked, t.reqs, t.cond_models, t.model_data, t.skinned, t.layers = {}, {}, set(), {}, {}, {}, {}, []
    t.options = {o: {"ID": o, "ChrModelID": m, "Name_lang": n, "OrderIndex": str(i)} for i, (o, (m, n)) in enumerate(options.items())}
    t.choices = {o: [{"ID": c, "Name_lang": "", "OrderIndex": str(i), "ChrCustomizationReqID": "0"} for i, c in enumerate(cs)] for o, cs in choices.items()}
    t.elements = type("E", (dict,), {"__missing__": lambda self, k: []})(
        {c: [{"ChrCustomizationGeosetID": g, "ChrCustomizationMaterialID": "0", "ChrCustomizationSkinnedModelID": "0",
              "RelatedChrCustomizationChoiceID": "0"} for g in gs] for c, gs in elements.items()})
    t.geosets = {g: {"ID": g, "GeosetType": str(a), "GeosetID": str(b)} for g, (a, b) in geosets.items()}
    t.chr_models = {"53": {"CharComponentTextureLayoutID": "1"}}
    return t


class BaseOnlyTest(unittest.TestCase):
    """The single switch (sl_looks.BASE_ONLY): off, the looks keep every piece as before; on, a looks file's models lose them."""
    def spec(self):
        return {"build": "x", "races": {"2": {"race": 2, "replace_rows": True, "models": {"0": {
            "name": "OrcMale", "folder": "Character\\Orc\\Male", "skins": [{"index": 0}], "base_skins": 1,
            "overlays": [{"name": "Eyebrows", "choices": [{"id": "1", "files": {"*": 3}}]}],
            "variants": [{"name": "Upright", "choices": [{"file": 1}, {"file": 2}]}],
            "parts": [{"name": "Tusks", "choices": [{"geosets": [[1, 2]]}]}],
            "pickers": [{"name": "Tusk Color", "type": 10, "choices": []}],
            "part_types": {"Tusks": [11]}, "soft": {"count": 1, "parent": 2, "bones": [[3, 0.1, 0.2, 0.3, [4]], [5, 0.1, 0.2, 0.3, [6]]]}}}}}}

    def test_on_strips_the_extended_options_and_keeps_the_rest(self):
        with mock.patch.object(sl_looks, "BASE_ONLY", True):
            looks = sl_looks.strip_extras(self.spec())
        m = looks["races"]["2"]["models"]["0"]
        for k in ("overlays", "variants", "parts", "pickers"):
            self.assertEqual(m[k], [])
        self.assertNotIn("part_types", m)
        self.assertEqual((m["name"], m["soft"]["count"]), ("OrcMale", 1))

    def test_on_strips_the_allied_races_keyed_by_name_too(self):
        allied = {"maghar": {"race": 36, "models": {"0": {"name": "MagharMale", "variants": [{"name": "Hunched"}], "parts": [{"name": "Horns"}]}}}}
        with mock.patch.object(sl_looks, "BASE_ONLY", True):
            sl_looks.strip_extras(allied)
        self.assertEqual(allied["maghar"]["models"]["0"]["variants"], [])
        self.assertEqual(allied["maghar"]["models"]["0"]["parts"], [])

    def test_off_changes_nothing(self):
        with mock.patch.object(sl_looks, "BASE_ONLY", False):
            looks = sl_looks.strip_extras(self.spec())
        self.assertEqual(looks, self.spec())

    def test_load_looks_follows_the_switch(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "looks.json")
            json.dump(self.spec(), open(path, "w"))
            with mock.patch.object(sl_looks, "BASE_ONLY", True):
                self.assertEqual(sl_looks.load_looks(path)["races"]["2"]["models"]["0"]["parts"], [])
            with mock.patch.object(sl_looks, "BASE_ONLY", False):
                self.assertEqual(len(sl_looks.load_looks(path)["races"]["2"]["models"]["0"]["parts"]), 1)

    def test_the_parts_table_then_holds_no_piece_picture_or_variant_line(self):
        import sl_parts
        ids = {"2_0:Eyebrows": 1400, "2_0:Upright": 1500, "2_0:Tusks": 1401}
        with mock.patch.object(sl_looks, "BASE_ONLY", True):
            looks = sl_looks.drawn_looks(sl_looks.strip_extras(self.spec()))
        with tempfile.TemporaryDirectory() as out:
            path = sl_parts.write_parts_table(looks, out, ids)
            kinds = {l.split("\t")[0] for l in open(path) if l.strip() and not l.startswith("#")}
        self.assertEqual(kinds, {"B"})              # (the soft body, which the five numbers do not touch, is all that is left)
        with mock.patch.object(sl_looks, "BASE_ONLY", False):
            looks = sl_looks.drawn_looks(sl_looks.strip_extras(self.spec()))
        with tempfile.TemporaryDirectory() as out:
            path = sl_parts.write_parts_table(looks, out, ids)
            kinds = {l.split("\t")[0] for l in open(path) if l.strip() and not l.startswith("#")}
        self.assertTrue({"V", "H", "G"} <= kinds, kinds)


class AlwaysOnTest(unittest.TestCase):
    """The Mechagnome's limbs: the first choices of its Arm Upgrade and Leg Upgrade, one model of the game's, with the first picture of the
    replaceable type 8 (the Paint's)."""
    class Tables:
        chr_models = {"73": {"CharComponentTextureLayoutID": "149"}}
        layers = [{"CharComponentTextureLayoutsID": "149", "ChrModelTextureTargetID_0": "1", "TextureType": "1"},
                  {"CharComponentTextureLayoutsID": "149", "ChrModelTextureTargetID_0": "2", "TextureType": "8"}]
        options = {"1": {"ID": "1", "ChrModelID": "73", "Name_lang": "Skin Color", "OrderIndex": "1"},
                   "2": {"ID": "2", "ChrModelID": "73", "Name_lang": "Arm Upgrade", "OrderIndex": "2"},
                   "3": {"ID": "3", "ChrModelID": "73", "Name_lang": "Leg Upgrade", "OrderIndex": "3"},
                   "4": {"ID": "4", "ChrModelID": "73", "Name_lang": "Paint", "OrderIndex": "4"}}
        choice = lambda self, i, o, ui: {"ID": str(i), "ChrCustomizationOptionID": o, "UiOrderIndex": str(ui), "OrderIndex": str(ui)}
        elements = {"10": [{"ChrCustomizationMaterialID": "5", "ChrCustomizationSkinnedModelID": "0"}],
                    "20": [{"ChrCustomizationMaterialID": "0", "ChrCustomizationSkinnedModelID": "100"}],
                    "21": [{"ChrCustomizationMaterialID": "0", "ChrCustomizationSkinnedModelID": "101"}],
                    "30": [{"ChrCustomizationMaterialID": "0", "ChrCustomizationSkinnedModelID": "102"},
                           {"ChrCustomizationMaterialID": "0", "ChrCustomizationSkinnedModelID": "103"}],
                    "40": [{"ChrCustomizationMaterialID": "6", "ChrCustomizationSkinnedModelID": "0"}],
                    "41": [{"ChrCustomizationMaterialID": "7", "ChrCustomizationSkinnedModelID": "0"}]}
        skinned = {"100": {"CollectionsFileDataID": "555", "GeosetType": "29", "GeosetID": "1"},
                   "101": {"CollectionsFileDataID": "555", "GeosetType": "29", "GeosetID": "2"},
                   "102": {"CollectionsFileDataID": "555", "GeosetType": "31", "GeosetID": "1"},
                   "103": {"CollectionsFileDataID": "555", "GeosetType": "30", "GeosetID": "1"}}
        materials = {"5": {"ChrModelTextureTargetID": "1", "MaterialResourcesID": "a"}, "6": {"ChrModelTextureTargetID": "2", "MaterialResourcesID": "b"},
                     "7": {"ChrModelTextureTargetID": "2", "MaterialResourcesID": "c"}}
        textures = {"a": [9], "b": [8888], "c": [9999]}

        def option_choices(self, model, name, only_available=True):
            by = {"Skin Color": [("10", "1", 1)], "Arm Upgrade": [("21", "2", 2), ("20", "2", 1)], "Leg Upgrade": [("30", "3", 1)],
                  "Paint": [("41", "4", 2), ("40", "4", 1)]}
            return [self.choice(i, o, ui) for i, o, ui in by[name]]

        def available(self, c):
            return True

        def material_files(self, e):
            m = self.materials[e["ChrCustomizationMaterialID"]]
            return m["ChrModelTextureTargetID"], self.textures[m["MaterialResourcesID"]]

    def test_the_first_choices_of_the_limbs_in_one_merge_with_the_first_paint(self):
        out = sl_looks.always_on_of(self.Tables(), 73, {"name": "MechagnomeMale"})
        self.assertEqual(out, [{"options": ["Arm Upgrade", "Leg Upgrade"], "model": 555, "sections": [2901, 3101, 3001], "texture": 8888}])

    def test_other_races_have_none(self):
        self.assertEqual(sl_looks.always_on_of(self.Tables(), 73, {"name": "GnomeMale"}), [])


class HeadGeosetsTest(unittest.TestCase):
    """9.2.7's rows of the head's group against the models' numbering (the newest files: the mouth 3201, the heads from 3202)."""

    def setUp(self):
        self.t = tables({"1530": ("53", "Eyes"), "1532": ("53", "Eyebrows"), "1534": ("53", "Face Jewelry")},
                        {"1530": ["e1", "e2"], "1532": ["b1", "b2"], "1534": ["j0", "j1"]},
                        {"e1": ["2083"], "e2": ["2084"], "b1": ["300"], "b2": ["301"], "j0": ["400"], "j1": ["401"]},
                        {"2083": (32, 1), "2084": (32, 2), "300": (34, 1), "301": (34, 2), "400": (16, 0), "401": (16, 1)})

    def test_a_head_row_of_9_2_7_is_the_models_next_geoset(self):
        self.assertEqual(sl_looks.BUILD, "9.2.7.45745")                      # (a newer build's table has the models' numbers: HEAD_SHIFT)
        self.assertEqual([self.t.choice_geosets(c) for c in self.t.choices["1530"]], [[3202], [3203]])
        self.assertEqual([self.t.choice_geosets(c) for c in self.t.choices["1532"]], [[3401], [3402]])       # the other groups as they are
        self.assertEqual([self.t.choice_geosets(c) for c in self.t.choices["1534"]], [[], [1601]])

    def test_the_nightbornes_eyes_are_models_of_their_own_not_a_piece(self):
        """two heads of the model itself: a variant (a model a choice), the first the model as it is; never a piece laid over the head"""
        model = {"model": 1, "name": "NightborneMale", "feature_options": [], "overlays": [], "hair_colors": []}
        model["variants"] = sl_looks.variants_of(self.t, 53, model)
        self.assertEqual([(v["name"], v.get("geoset"), [c["geosets"] for c in v["choices"]]) for v in model["variants"]],
                         [("Eyes", True, [[3202], [3203]])])
        parts, pickers = sl_looks.parts_of(self.t, 53, model)
        self.assertEqual([p["name"] for p in parts], ["Eyebrows", "Face Jewelry"])


class BlueEyesTest(unittest.TestCase):
    def test_irises_turn_blue_and_the_green_cast_goes_back_to_skin(self):
        import numpy as np
        icon = np.zeros((64, 64, 4), dtype=np.uint8)
        icon[..., 3] = 255
        icon[21, 34] = (0x40, 0xd0, 0x40, 255)       # an iris
        icon[25, 36] = (0x60, 0x70, 0x30, 255)       # olive cast beside the eye
        icon[50, 30] = (0x89, 0x6a, 0x3a, 255)       # olive brown on the lower face
        icon[5, 5] = (0xe0, 0xc0, 0x60, 255)         # blond hair
        icon[50, 55] = (0x89, 0x6a, 0x3a, 255)       # the same brown in the hair, outside the face's box
        out = sl_looks.blue_eyes(icon)
        r, g, b, a = (int(v) for v in out[21, 34])
        self.assertTrue(b > g and b > r and a == 255)
        for xy in ((25, 36), (50, 30)):
            r, g, b, a = (int(v) for v in out[xy])
            self.assertTrue(r > g > b, xy)
        self.assertEqual(tuple(out[5, 5]), (0xe0, 0xc0, 0x60, 255))
        self.assertEqual(tuple(out[50, 55]), (0x89, 0x6a, 0x3a, 255))
        self.assertEqual(sl_looks.RACE_ICONS["HIGHELF"], 131152)


class AnimationFallbackGuard(unittest.TestCase):
    """The CI guard on sequences drawn as another animation (m2.convert's files that fit none of the skeletons)."""

    def test_counts_only_ids_the_game_knows(self):
        fallbacks = {"A": [(67, 0), (500, 0), (900, 0)], "B": [], "C": [(97, 0)]}
        self.assertEqual(sl_looks.fallback_counts(fallbacks, {67, 97, 500}), {"A": 2, "B": 0, "C": 1})
        self.assertEqual(sl_looks.fallback_counts(fallbacks, None)["A"], 3)

    def test_guard_fails_when_a_count_rises(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, "base.json")
            with open(base, "w") as f:
                f.write('{"A": 2}')
            quiet = lambda *a: None
            sl_looks.check_fallbacks({"A": [(1, 0), (2, 0)], "B": []}, tmp, tmp, quiet, base)       # no AnimationData.dbc: all ids count
            self.assertTrue(os.path.exists(os.path.join(tmp, "anim_fallbacks.json")))
            with self.assertRaises(ValueError) as caught:
                sl_looks.check_fallbacks({"A": [(1, 0), (2, 0), (3, 0)]}, tmp, tmp, quiet, base)
            self.assertIn("A: 3 (baseline 2", str(caught.exception))
            with self.assertRaises(ValueError):                                                      # a model with no baseline starts at 0
                sl_looks.check_fallbacks({"New": [(1, 0)]}, tmp, tmp, quiet, base)

    def test_reads_the_ids_of_animation_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [(0, 1), (4, 2), (67, 3)]
            with open(os.path.join(tmp, "AnimationData.dbc"), "wb") as f:
                f.write(b"WDBC" + struct.pack("<4I", len(rows), 2, 8, 1) + b"".join(struct.pack("<2I", *r) for r in rows) + b"\0")
            self.assertEqual(sl_looks.game_animations(tmp), {0, 4, 67})
            self.assertIsNone(sl_looks.game_animations(os.path.join(tmp, "none")))


if __name__ == "__main__":
    unittest.main()

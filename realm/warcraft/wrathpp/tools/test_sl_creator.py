"""Tests of tools/sl_creator.py on tables made here: the creator's options in Shadowlands' order under its categories,
their choices in the order shown with names, swatches and class rules, and each choice's place in the number 3.3.5
keeps (a face and an eye colour in one, a tattoo and a skin colour in one, the feature options in one). Run by
protocol/tests/run.sh (python3 -I)."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_creator  # noqa: E402

DK, DH = 1 << 5, 1 << 11


class Tables:
    """What sl_creator asks of sl_looks.Tables, over rows given here."""

    def __init__(self, options, choices, reqs, files):
        self.options = {o["ID"]: o for o in options}
        self.choices = {}
        for c in choices:
            self.choices.setdefault(c["ChrCustomizationOptionID"], []).append(c)
        for cs in self.choices.values():
            cs.sort(key=lambda c: int(c["OrderIndex"]))
        self.reqs = {r["ID"]: r for r in reqs}
        self.files = files                      # choice id -> {target: [file ids]}
        self.aliases, self.only_available, self.unlocked = {}, {}, set()

    def unlock(self, model_id, achievements):
        pass

    def available(self, choice):
        req = self.reqs.get(choice["ChrCustomizationReqID"])
        return req is None or req["ReqType"] == "3"

    def option_choices(self, model_id, name, only_available=True):
        name = self.aliases.get((str(model_id), name), name)
        for o in self.options.values():
            if o["ChrModelID"] == str(model_id) and o["Name_lang"] == name:
                return [c for c in self.choices.get(o["ID"], []) if not only_available or self.available(c)]
        return []

    def choice_materials(self, choice, target=None):
        return [("0", files) for t, files in self.files.get(choice["ID"], {}).items() if target is None or t == target]


def option(i, name, order, category=2, kind=0):
    return {"ID": str(i), "Name_lang": name, "ChrModelID": "2", "OrderIndex": str(order), "ChrCustomizationCategoryID": str(category), "OptionType": str(kind)}


def choice(i, option_id, order, name="", ui=None, req="0", s0=0, s1=0):
    return {"ID": str(i), "ChrCustomizationOptionID": str(option_id), "OrderIndex": str(order), "UiOrderIndex": str(order if ui is None else ui),
            "Name_lang": name, "ChrCustomizationReqID": req, "SwatchColor_0": str(s0), "SwatchColor_1": str(s1), "Flags": "0"}


OPTIONS = [option(10, "Face", 1), option(11, "Skin Color", 2), option(12, "Hair Style", 3), option(13, "Hair Color", 4),
           option(14, "Eye Color", 11, category=3), option(15, "Necklace", 22, category=3), option(16, "Piercings", 21, category=3),
           option(17, "Makeup", 20, category=3), option(18, "Tattoo", 30, category=5), option(19, "Bear Form", 50, category=6),
           option(20, "Flower", 23, category=3, kind=1)]
CHOICES = [choice(100, 10, 0), choice(101, 10, 1),
           choice(110, 11, 0, ui=2, s0=-0x216A90), choice(111, 11, 1, ui=1, s0=-0x113A58), choice(112, 11, 2, ui=70, req="2", s0=-0x42517C),
           choice(120, 12, 0, "Bald"), choice(121, 12, 1, "Bun"), choice(122, 12, 2, "Braid"),
           choice(130, 13, 0, s0=0x111111), choice(131, 13, 1, s0=0x222222), choice(132, 13, 2, req="4"),
           choice(140, 14, 0, s0=-0xB600C8), choice(141, 14, 1, s0=-0xB600C8, s1=0x8C8E8C),
           choice(150, 15, 0, "None"), choice(151, 15, 1, "Pearls"), choice(152, 15, 2, "Chain"),
           choice(160, 16, 0, "None"), choice(161, 16, 1, "Studs"),
           choice(170, 17, 0, "None"), choice(171, 17, 1, "Smoky"), choice(172, 17, 2, "Pride", req="4"),
           choice(180, 18, 0, "None"), choice(181, 18, 1, "Wolf"), choice(182, 18, 2, "No Texture"),
           choice(190, 19, 0, "Bear"), choice(191, 19, 1, "Brown Bear"),
           choice(200, 20, 0, "None"), choice(201, 20, 1, "Rose")]
REQS = [{"ID": "2", "ReqType": "3", "ClassMask": str(DK), "ReqAchievementID": "0"},
        {"ID": "3", "ReqType": "3", "ClassMask": str(DH), "ReqAchievementID": "0"},
        {"ID": "4", "ReqType": "2", "ClassMask": "0", "ReqAchievementID": "0"}]
FILES = {"130": {"10": [1]}, "131": {"10": [2]}, "181": {"16": [9]}}
CATEGORIES = {"2": {"ID": "2", "CategoryName_lang": "Face", "OrderIndex": "1", "CameraZoomLevel": "100", "SpellShapeshiftFormID": "0"},
              "3": {"ID": "3", "CategoryName_lang": "Accessories (Tauren)", "OrderIndex": "3", "CameraZoomLevel": "100", "SpellShapeshiftFormID": "0"},
              "5": {"ID": "5", "CategoryName_lang": "Markings", "OrderIndex": "5", "CameraZoomLevel": "65", "SpellShapeshiftFormID": "0"},
              "6": {"ID": "6", "CategoryName_lang": "Bear Form", "OrderIndex": "6", "CameraZoomLevel": "0", "SpellShapeshiftFormID": "5"}}
# the looks sl_looks.py makes of those tables: two tattoos x three skins, two faces x two eyes, necklace x piercings
MODEL = {"name": "HumanFemale", "chr_model": 2, "tattoos": ["None", "Wolf"], "base_skins": 3,
         "skins": [{"choice": c, "base": b, "index": t * 3 + b} for t in range(2) for b, c in enumerate(("110", "111", "112"))],
         "faces": [{"choice": "100"}, {"choice": "101"}], "eyes": [{"choice": "140", "index": 0}, {"choice": "141", "index": 1}],
         "hair": [{"choice": "120", "variation": 0}, {"choice": "121", "variation": 1}, {"choice": "122", "variation": 2}],
         "hair_colors": [{"index": 0}, {"index": 1}], "feature_options": ["Necklace", "Piercings"],
         "features": [{"variation": i} for i in range(6)]}


class CreatorDataTest(unittest.TestCase):
    def setUp(self):
        self.m = sl_creator.build_model(Tables(OPTIONS, CHOICES, REQS, FILES), CATEGORIES, 1, 1, MODEL)
        self.by = {o["name"]: o for o in self.m["options"]}

    def test_options_in_the_games_order_under_its_categories(self):
        self.assertEqual([o["name"] for o in self.m["options"]],
                         ["Face", "Skin Color", "Hair Style", "Hair Color", "Eye Color", "Makeup", "Piercings", "Necklace", "Flower", "Tattoo"])
        self.assertEqual([(c["name"], c["order"], c["zoom"]) for c in self.m["categories"]], [("Face", 1, 100), ("Accessories", 3, 100), ("Markings", 5, 65)])
        self.assertNotIn("Bear Form", self.by)                              # a druid's forms are left out
        self.assertEqual(self.by["Flower"]["type"], 1)                      # a switch

    def test_the_parts_of_a_number(self):
        self.assertEqual(self.m["fields"], {"skin": [2, 3], "face": [2, 2], "hair": [3], "haircolor": [2], "feature": [3, 2]})
        self.assertEqual((self.by["Tattoo"]["field"], self.by["Tattoo"]["part"]), ("skin", 1))
        self.assertEqual((self.by["Skin Color"]["field"], self.by["Skin Color"]["part"]), ("skin", 2))
        self.assertEqual((self.by["Face"]["field"], self.by["Face"]["part"]), ("face", 1))
        self.assertEqual((self.by["Eye Color"]["field"], self.by["Eye Color"]["part"]), ("face", 2))
        self.assertEqual((self.by["Necklace"]["part"], self.by["Piercings"]["part"]), (1, 2))   # the looks' order, not the screen's
        self.assertEqual([c["v"] for c in self.by["Tattoo"]["choices"]], [0, 1])               # the tattoo without a texture isn't in the looks

    def test_choices_as_shown(self):
        skin = self.by["Skin Color"]["choices"]
        self.assertEqual([c["v"] for c in skin], [1, 0, 2])                                     # the screen's order (UiOrderIndex)
        self.assertEqual(skin[0]["s"], 0xEEC5A8)                                                # -0x113A58 as RRGGBB
        self.assertEqual(skin[2].get("c"), "dk")                                                # a death knight's alone
        self.assertNotIn("c", skin[0])
        self.assertEqual(self.by["Eye Color"]["choices"][1]["s2"], 0x8C8E8C)                    # a second swatch (one blind eye)
        self.assertEqual([c["n"] for c in self.by["Hair Style"]["choices"]], ["Bald", "Bun", "Braid"])
        self.assertEqual(len(self.by["Hair Color"]["choices"]), 2)                              # the locked colour isn't in the looks

    def test_an_option_nothing_draws_yet(self):
        makeup = self.by["Makeup"]
        self.assertNotIn("field", makeup)
        self.assertEqual([c["n"] for c in makeup["choices"]], ["None", "Smoky"])                # the choices a player may pick

    def test_lua(self):
        text = sl_creator.lua({"build": "9.2.7.45745", "models": {"1_1": self.m}})
        self.assertIn('["1_1"] = {', text)
        self.assertIn('face = { 2, 2 }', text)
        self.assertIn('{ v = 1, n = "", s = 15648168 }', text)
        self.assertTrue(text.startswith("-- Wrath++'s creator"))

    def test_parts_must_make_the_looks_count(self):
        bad = dict(MODEL, features=[{"variation": i} for i in range(5)])
        with self.assertRaises(ValueError):
            sl_creator.build_model(Tables(OPTIONS, CHOICES, REQS, FILES), CATEGORIES, 1, 1, bad)


if __name__ == "__main__":
    unittest.main()

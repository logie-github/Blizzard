"""Tests of tools/sl_inventory.py on tables made here (the game's columns, a few rows): options in the game's
order per race and sex, choices in theirs, what draws each, and which choices 3.3.5's classes may pick.
Run by protocol/tests/run.sh (python3 -I)."""
import csv
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_inventory  # noqa: E402

DK, DH, DRUID = 1 << 5, 1 << 11, 1 << 10
ALL_BUT_DK = sum(1 << (c - 1) for c in sl_inventory.CLASSES) & ~DK
TABLES = {
    "ChrRaceXChrModel": [{"ChrRacesID": 10, "ChrModelID": 20}, {"ChrRacesID": 10, "ChrModelID": 19}, {"ChrRacesID": 29, "ChrModelID": 57}],
    "ChrModel": [{"ID": 19, "Sex": 0}, {"ID": 20, "Sex": 1}, {"ID": 57, "Sex": 0}],
    "ChrCustomizationCategory": [{"ID": 1, "CategoryName_lang": "Face"}],
    "ChrCustomizationOption": [
        {"ID": 300, "Name_lang": "Horns", "ChrModelID": 19, "OrderIndex": 2, "ChrCustomizationCategoryID": 1},
        {"ID": 301, "Name_lang": "Eye Color", "ChrModelID": 19, "OrderIndex": 1, "ChrCustomizationCategoryID": 1},
        {"ID": 302, "Name_lang": "Earrings", "ChrModelID": 20, "OrderIndex": 0, "ChrCustomizationCategoryID": 1},
        {"ID": 303, "Name_lang": "Void", "ChrModelID": 57, "OrderIndex": 0, "ChrCustomizationCategoryID": 1}],
    "ChrCustomizationChoice": [
        {"ID": 1, "ChrCustomizationOptionID": 300, "Name_lang": "None", "OrderIndex": 0, "ChrCustomizationReqID": 0},
        {"ID": 2, "ChrCustomizationOptionID": 300, "Name_lang": "Horns 1", "OrderIndex": 1, "ChrCustomizationReqID": 2},
        {"ID": 3, "ChrCustomizationOptionID": 301, "Name_lang": "Green", "OrderIndex": 0, "ChrCustomizationReqID": 1},
        {"ID": 4, "ChrCustomizationOptionID": 301, "Name_lang": "Blue", "OrderIndex": 1, "ChrCustomizationReqID": 3},
        {"ID": 5, "ChrCustomizationOptionID": 301, "Name_lang": "Pride", "OrderIndex": 2, "ChrCustomizationReqID": 4},
        {"ID": 6, "ChrCustomizationOptionID": 302, "Name_lang": "Hoops", "OrderIndex": 1, "ChrCustomizationReqID": 0},
        {"ID": 7, "ChrCustomizationOptionID": 302, "Name_lang": "None", "OrderIndex": 0, "ChrCustomizationReqID": 0}],
    "ChrCustomizationReq": [
        {"ID": 1, "ReqType": 3, "ClassMask": ALL_BUT_DK, "ReqAchievementID": 0},
        {"ID": 2, "ReqType": 3, "ClassMask": DH, "ReqAchievementID": 0},
        {"ID": 3, "ReqType": 3, "ClassMask": DK, "ReqAchievementID": 0},
        {"ID": 4, "ReqType": 2, "ClassMask": 0, "ReqAchievementID": 0}],
    "ChrCustomizationElement": [
        {"ChrCustomizationChoiceID": 2, "ChrCustomizationGeosetID": 0, "ChrCustomizationMaterialID": 0, "ChrCustomizationSkinnedModelID": 9, "RelatedChrCustomizationChoiceID": 0},
        {"ChrCustomizationChoiceID": 3, "ChrCustomizationGeosetID": 0, "ChrCustomizationMaterialID": 8, "ChrCustomizationSkinnedModelID": 0, "RelatedChrCustomizationChoiceID": 0},
        {"ChrCustomizationChoiceID": 6, "ChrCustomizationGeosetID": 7, "ChrCustomizationMaterialID": 0, "ChrCustomizationSkinnedModelID": 0, "RelatedChrCustomizationChoiceID": 0}],
    "ChrCustomizationGeoset": [{"ID": 7, "GeosetType": 35, "GeosetID": 2}],
    "ChrCustomizationMaterial": [{"ID": 8, "ChrModelTextureTargetID": 25, "MaterialResourcesID": 4242}],
    "ChrCustomizationSkinnedModel": [{"ID": 9, "CollectionsFileDataID": 1234, "GeosetType": 24, "GeosetID": 1}],
}


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        for table, rows in TABLES.items():
            with open(os.path.join(self.dir.name, table + ".csv"), "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
        self.inv = sl_inventory.build(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_races_and_order(self):
        self.assertEqual([(r["race_name"], r["sex"]) for r in self.inv["races"]], [("BloodElf", "male"), ("BloodElf", "female")])
        male = self.inv["races"][0]
        self.assertEqual([o["name"] for o in male["options"]], ["Eye Color", "Horns"])
        self.assertEqual([c["name"] for c in self.inv["races"][1]["options"][0]["choices"]], ["None", "Hoops"])

    def test_what_draws(self):
        male, female = self.inv["races"]
        self.assertEqual(male["options"][1]["choices"][1]["models"], [{"file": 1234, "geoset": 2401, "with": 0}])
        self.assertEqual(male["options"][1]["kinds"], ["model"])
        self.assertEqual(male["options"][0]["choices"][0]["materials"], [{"target": 25, "resources": 4242, "with": 0}])
        self.assertEqual(female["options"][0]["choices"][1]["geosets"], [{"geoset": 3502, "with": 0}])

    def test_restrictions(self):
        eyes = self.inv["races"][0]["options"][0]["choices"]
        r = [sl_inventory.restriction(c["requires"]) for c in eyes]
        self.assertEqual(r[0], "Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior")
        self.assertEqual(r[1], "DeathKnight")
        self.assertEqual(r[2], "unlock 2")
        horns = self.inv["races"][0]["options"][1]["choices"]
        self.assertIsNone(sl_inventory.restriction(horns[0]["requires"]))
        self.assertEqual(sl_inventory.restriction(horns[1]["requires"]), "none of 3.3.5's")

    def test_markdown(self):
        md = sl_inventory.markdown(self.inv)
        self.assertIn("### BloodElf male (ChrModel 19)", md)
        self.assertIn("| 2 | Horns | 2 | model | 1 none of 3.3.5's |  |", md)


if __name__ == "__main__":
    unittest.main()

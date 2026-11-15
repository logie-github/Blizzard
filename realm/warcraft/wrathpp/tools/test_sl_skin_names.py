"""Tests of tools/sl_skin_names.py with a stand-in for wago.tools' search: each skin named by its file's id, tattooed
skins and unnamed files left out, a failed search costing only its model. Run by protocol/tests/run.sh (python3 -I)."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_skin_names  # noqa: E402

LOOKS = {"build": "9.2.7.45745", "races": {
    "1": {"race": 1, "models": {"1": {"name": "HumanFemale", "folder": "Character\\Human\\Female", "skins": [
        {"index": 0, "body": 100, "tattoo": []}, {"index": 1, "body": 101, "tattoo": []}, {"index": 2, "body": 102, "tattoo": []},
        {"index": 3, "body": 100, "tattoo": [900]}]}}},
    "2": {"race": 2, "models": {"0": {"name": "OrcMale", "folder": "Character\\Orc\\Male", "skins": [{"index": 0, "body": 200, "tattoo": []}]}}}}}


def search(word):
    if word.startswith("orcmale"):
        raise OSError("timed out")
    return {"100": "character/human/female/humanfemaleskin00_00_hd.blp", "101": "Character\\Human\\Female\\HumanFemaleSkin00_07_HD.blp", "555": "other.blp"}


class SkinNamesTest(unittest.TestCase):
    def test_fetch_and_list(self):
        said, saves = [], []
        known = sl_skin_names.fetch(LOOKS, {}, search, said.append, lambda: saves.append(1))
        self.assertEqual(known, {"100": "humanfemaleskin00_00_hd.blp", "101": "humanfemaleskin00_07_hd.blp"})   # the names alone, lower case
        self.assertTrue(any("OrcMale: no answer" in line for line in said))       # a search that failed costs its model alone
        self.assertEqual(len(saves), 2)                                           # kept after every model
        data = sl_skin_names.build(LOOKS, known, said.append)
        self.assertEqual(list(data["models"]), ["1_1"])
        skins = data["models"]["1_1"]["skins"]
        self.assertEqual([(s["index"], s["retail"]) for s in skins], [(0, "humanfemaleskin00_00_hd.blp"), (1, "humanfemaleskin00_07_hd.blp")])   # the tattooed and the unnamed left out
        self.assertEqual(skins[1]["path"], "Character\\Human\\Female\\HumanFemaleSkin00_01.blp")
        # what is known already isn't asked for again
        asked = []
        sl_skin_names.fetch({"races": {"1": LOOKS["races"]["1"]}}, {"100": "a", "101": "b", "102": "c"}, lambda w: asked.append(w) or {}, said.append)
        self.assertEqual(asked, [])


if __name__ == "__main__":
    unittest.main()

"""Tests of tools/sl_coverage.py on rows made here: whose a choice is, what Shadowlands offers, which mechanism a creator's option
has, the slots the creator's options take, and a retail model's geosets read from its files."""
import os
import struct
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_coverage  # noqa: E402

DK, DH = 1 << 5, 1 << 11


class Reqs:
    def __init__(self, reqs):
        self.reqs = reqs


def req(kind, mask=-1, achievement=0):
    return {"ReqType": str(kind), "ClassMask": str(mask), "ReqAchievementID": str(achievement)}


class Coverage(unittest.TestCase):
    def test_whose_a_choice_is(self):
        self.assertEqual(sl_coverage.class_kind(-1), "all")
        self.assertEqual(sl_coverage.class_kind(0), "all")
        self.assertEqual(sl_coverage.class_kind(DK), "dk")
        self.assertEqual(sl_coverage.class_kind(DK | DH), "dk")
        self.assertEqual(sl_coverage.class_kind(4095 & ~DK), "nodk")
        self.assertEqual(sl_coverage.class_kind(2015), "nodk")          # every class but a death knight and a demon hunter
        self.assertEqual(sl_coverage.class_kind(DH), "dh")
        self.assertEqual(sl_coverage.class_kind(4096), "dh")            # a later class's alone: none of 3.3.5's
        self.assertEqual(sl_coverage.class_kind(2047), "all")           # every class but a demon hunter: all of 3.3.5's
        self.assertEqual(sl_coverage.class_kind(-4064), "dk")           # (negative masks: the bits above 3.3.5's classes set)

    def test_what_shadowlands_offers(self):
        tables = Reqs({"1": req(3), "2": req(3, DK), "3": req(2, 0), "4": req(4, 0), "5": req(3, DH), "6": req(3, 2015, 15579), "7": req(1, 1024, 14653)})
        choices = [{"ChrCustomizationReqID": str(i)} for i in (1, 1, 2, 3, 4, 5, 6, 7)] + [{"ChrCustomizationReqID": "0"}]
        counts = sl_coverage.sl_counts(tables, choices)
        self.assertEqual(counts["rows"], 9)
        self.assertEqual(counts["offered"], 6)                          # type 3, and a choice with no requirement
        self.assertEqual((counts["all"], counts["dk"], counts["dh"], counts["nodk"]), (3, 1, 1, 1))
        self.assertEqual((counts["npc"], counts["hidden"], counts["unlock"], counts["achievement"]), (1, 1, 1, 1))

    def test_the_mechanism_of_a_creator_option(self):
        m = sl_coverage.mechanism
        self.assertEqual(m(None)[0], "absent")
        self.assertEqual(m({"field": "face", "part": 2})[0], "number")
        self.assertIn("piece over it", m({"field": "feature", "part": 1, "geoset": "x.m2"})[1])
        self.assertEqual(m({"style": True})[0], "style")
        self.assertEqual(m({"overlay": "x.m2", "bodyoverlay": "y.m2", "depends": ["Tattoo"]}), ("overlay", "a picture on the head and body shells (follows Tattoo)"))
        self.assertEqual(m({"geoset": "x.m2"})[0], "piece")
        self.assertEqual(m({"texture": True})[0], "picker")
        self.assertEqual(m({"variant": True})[0], "variant")
        self.assertEqual(m({"choices": []})[0], "none")                 # listed, greyed "Not drawn yet"

    def test_the_slots_follow_the_creators_order(self):
        cm = {"options": [{"name": "Scars", "overlay": "f", "bodyoverlay": "b"}, {"name": "Ears", "geoset": "e"}, {"name": "Makeup", "overlay": "f"},
                          {"name": "Earrings", "field": "feature", "part": 1, "geoset": "p"}, {"name": "Hair", "field": "hair", "part": 1}]}
        self.assertEqual(sl_coverage.slots(cm), 5)
        by = {o["name"]: o.get("slot") for o in cm["options"]}
        # the head shells (Scars 1, Makeup 2), the body shells (Scars 3), then the pieces in the options' order
        self.assertEqual(by, {"Scars": 3, "Makeup": 2, "Ears": 4, "Earrings": 5, "Hair": None})

    def test_a_retail_models_geosets_and_their_texture_types(self):
        # a model of three textures (types 1, 8, 20), a lookup, and a skin of three sections: 0 (body), 5 (fur), 3501 (jewellery and body)
        md = bytearray(0x130)
        textures = b"".join(struct.pack("<IIII", t, 0, 0, 0) for t in (1, 8, 20))
        look = struct.pack("<3h", 0, 1, 2)
        struct.pack_into("<II", md, 0x50, 3, len(md))
        md += textures
        struct.pack_into("<II", md, 0x80, 3, len(md))
        md += look
        model = b"MD21" + struct.pack("<I", len(md)) + bytes(md) + b"SFID" + struct.pack("<II", 4, 77)
        skin = bytearray(64)
        skin[:4] = b"SKIN"
        sections = b"".join(struct.pack("<HHHHHH", sid, 0, 0, 0, 0, 0) + bytes(36) for sid in (0, 5, 3501))

        def batch(section, first):
            return struct.pack("<BbHHHhHHHHHHH", 0, 0, 0, section, 0, 0, 0, 0, 1, first, 0, 0, 0)
        batches = batch(0, 0) + batch(1, 1) + batch(2, 2) + batch(2, 0)
        struct.pack_into("<II", skin, 28, 3, len(skin))
        skin += sections
        struct.pack_into("<II", skin, 36, 4, len(skin))
        skin += batches
        files = {1: model, 77: bytes(skin)}
        self.assertEqual(sl_coverage.model_geosets(files.__getitem__, 1), {"0": [1], "5": [8], "3501": [1, 20]})


if __name__ == "__main__":
    unittest.main()

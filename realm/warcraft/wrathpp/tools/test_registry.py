"""Tests of tools/registry.py: the shipped registry is valid, decodes to what it encodes, and every
broken registry is refused. Run by protocol/tests/run.sh (python3 -I, so the tool is imported by path)."""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import registry  # noqa: E402


class RegistryTest(unittest.TestCase):
    def setUp(self):
        with open(registry.DEFAULT, encoding="utf-8") as f:
            self.doc = json.load(f)

    def build(self, doc):
        return registry.encode(*registry.normalize(doc))

    def test_shipped_registry_round_trips(self):
        blob = self.build(self.doc)
        decoded = registry.decode(blob)
        self.assertEqual(decoded["version"], self.doc["version"])
        self.assertEqual([c["id"] for c in decoded["categories"]], sorted(c["id"] for c in self.doc["categories"]))

    def test_order_does_not_change_bytes(self):
        shuffled = copy.deepcopy(self.doc)
        shuffled["categories"].reverse()
        for c in shuffled["categories"]:
            c["options"].reverse()
        self.assertEqual(self.build(shuffled), self.build(self.doc))

    def test_shipped_registry_is_honest(self):
        # Until the inventory has run, every Legion category says it is unverified; Wrath++'s own say what they are.
        for c in self.doc["categories"]:
            if "origin" in c:
                self.assertTrue(c["origin"].startswith("Wrath++'s own"))
                continue
            self.assertIn("legion", c)
            self.assertIn("verified", c["legion"])

    def test_body_options(self):
        # Shape, Style and Density: every woman of the ten races, none of the men; the values the realm's module reads.
        cats = {c["id"]: c for c in self.doc["categories"]}
        races = {1, 2, 3, 4, 5, 6, 7, 8, 10, 11}
        for cid, values in ((1101, range(4)), (1102, range(17)), (1103, range(5))):
            c = cats[cid]
            self.assertEqual({e["race"] for e in c["eligibility"]}, races)
            self.assertTrue(all(e["sexes"] == ["female"] for e in c["eligibility"]))
            self.assertEqual(sorted(o["value"] for o in c["options"]), list(values))
            self.assertEqual(next(o for o in c["options"] if o["id"] == c["default"])["value"], 4 if cid == 1103 else 0)

    def broken(self, mutate):
        doc = copy.deepcopy(self.doc)
        mutate(doc)
        with self.assertRaises((registry.RegistryError, KeyError, ValueError)):
            self.build(doc)

    def test_refusals(self):
        self.broken(lambda d: d["categories"].append(copy.deepcopy(d["categories"][0])))       # repeated id
        self.broken(lambda d: d["categories"][0].update(default=99))                          # default not an option
        self.broken(lambda d: d["categories"][0]["options"].append({"id": 1, "value": 4, "name": "x"}))
        self.broken(lambda d: d["categories"][0]["options"][0].update(value=100))             # geoset value
        self.broken(lambda d: d["categories"][0].update(kind="decal"))
        self.broken(lambda d: d["categories"][0].update(eligibility=[]))
        self.broken(lambda d: d["categories"][0].update(options=[]))
        self.broken(lambda d: d["categories"][0].update(name="x" * 49))
        self.broken(lambda d: d["categories"][0]["eligibility"][0].update(sexes=[]))
        self.broken(lambda d: d["categories"][0].update(geoset_group=0))
        self.broken(lambda d: d.update(schema=2))
        self.broken(lambda d: d["categories"][0]["eligibility"][0].update(classes=["monk"]))

    def test_trailing_bytes_refused(self):
        with self.assertRaises(registry.RegistryError):
            registry.decode(self.build(self.doc) + b"\0")


if __name__ == "__main__":
    unittest.main(verbosity=1)

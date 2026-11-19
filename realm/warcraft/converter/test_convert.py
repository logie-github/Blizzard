"""convert.py: the driver over the catabackport tool, with a fake tool: which maps an expansion takes, the progress file, failures."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert  # noqa: E402

MAPS = [
    {"id": 1, "dir": "A", "expansion": 3, "origin": "new", "status": "planned"},
    {"id": 2, "dir": "Azeroth", "expansion": 0, "origin": "revamped", "status": "planned"},
    {"id": 3, "dir": "B", "expansion": 4, "origin": "new", "status": "planned"},
    {"id": 4, "dir": "C", "expansion": 3, "origin": "stock", "status": "same_as_stock"},
    {"id": 5, "dir": "D", "expansion": 6, "origin": "new", "status": "planned"},
]


class Fake:
    """Stands in for subprocess.run over the tool: writes what each command would."""

    def __init__(self, work_status=None):
        self.calls, self.status = [], work_status or {}

    def __call__(self, cmd, cwd=None, stdout=None, stderr=None):
        args = cmd[cmd.index("catabackport") + 1:]
        self.calls.append(args)
        sub = args[0]
        work = args[args.index("--work") + 1] if "--work" in args else None
        if sub == "inventory":
            pins = json.load(open(args[args.index("--pins") + 1]))
            json.dump({"maps": MAPS, "pins_seen": pins}, open(os.path.join(work, "manifest.json"), "w"))
        elif sub == "plan":
            ids = [int(i) for i in args[args.index("--maps") + 1].split(",")]
            json.dump({"units": [{"unit": "u%d" % i} for i in ids]}, open(os.path.join(work, "plan.json"), "w"))
        elif sub == "run":
            unit = args[args.index("--only") + 1]
            return subprocess.CompletedProcess(cmd, self.status.get(unit, 0))
        return subprocess.CompletedProcess(cmd, 0)


class ConvertTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.tool = os.path.join(self.dir.name, "tools")
        os.makedirs(os.path.join(self.tool, "catabackport"))
        json.dump({"build": "4.4.2.60895", "max_expansion": 3}, open(os.path.join(self.tool, "catabackport", "pins.json"), "w"))
        self.root = os.path.join(self.dir.name, "out")

    def tearDown(self):
        self.dir.cleanup()

    def progress(self, key):
        return convert.load_progress(os.path.join(self.root, key, "progress.json"))

    def test_an_expansion_takes_its_own_maps_and_cataclysm_the_revamped_ones(self):
        cata = convert.select_maps({"maps": MAPS}, convert.expansion("cataclysm"))
        self.assertEqual([m["id"] for m in cata], [1, 2])                      # not the stock one, not another expansion's
        self.assertEqual([m["id"] for m in convert.select_maps({"maps": MAPS}, convert.expansion("mop"))], [3])
        self.assertEqual([m["id"] for m in convert.select_maps({"maps": MAPS}, convert.expansion("legion"))], [5])

    def test_the_pins_carry_the_expansions_build_and_id(self):
        pins = convert.pins_for({"build": "x", "max_expansion": 3, "other": 1}, convert.expansion("legion"))
        self.assertEqual((pins["build"], pins["max_expansion"], pins["other"]), ("7.3.5.26972", 6, 1))

    def test_a_run_converts_every_unit_and_says_so(self):
        fake = Fake()
        status = convert.run("cataclysm", self.root, tool=self.tool, python="python3", runner=fake)
        self.assertEqual(status, 0)
        p = self.progress("cataclysm")
        self.assertEqual((p["state"], p["done"], p["total"]), ("done", 2, 2))
        self.assertEqual({k: v["state"] for k, v in p["units"].items()}, {"u1": "done", "u2": "done"})
        stages = [a[a.index("--stages") + 1] for a in fake.calls if a[0] == "run"]
        self.assertEqual(stages, ["fetch,convert,tables,validate,pack"] * 2)    # no extract and no world: nothing native, no database
        self.assertEqual(fake.calls[-1][0], "assemble")
        self.assertTrue(os.path.isfile(os.path.join(self.root, "cataclysm", "convert.log")))

    def test_a_second_run_does_not_ask_the_source_for_the_inventory_again(self):
        convert.run("mop", self.root, tool=self.tool, python="python3", runner=Fake())
        again = Fake()
        convert.run("mop", self.root, tool=self.tool, python="python3", runner=again)
        self.assertNotIn("inventory", [a[0] for a in again.calls])

    def test_a_failed_unit_is_partial_and_all_failed_is_an_error(self):
        status = convert.run("cataclysm", self.root, tool=self.tool, python="python3", runner=Fake({"u1": 1}))
        self.assertEqual((status, self.progress("cataclysm")["state"]), (0, "partial"))
        status = convert.run("legion", self.root, tool=self.tool, python="python3", runner=Fake({"u5": 1}))
        self.assertEqual((status, self.progress("legion")["state"]), (3, "partial"))

    def test_a_source_that_is_down_defers_the_run(self):
        status = convert.run("cataclysm", self.root, tool=self.tool, python="python3", runner=Fake({"u1": 75, "u2": 75}))
        self.assertEqual((status, self.progress("cataclysm")["state"]), (75, "deferred"))

    def test_the_inventory_failing_stops_before_any_unit(self):
        class Bad(Fake):
            def __call__(self, cmd, cwd=None, stdout=None, stderr=None):
                return subprocess.CompletedProcess(cmd, 1)
        self.assertEqual(convert.run("mop", self.root, tool=self.tool, python="python3", runner=Bad()), 3)
        self.assertEqual(self.progress("mop")["state"], "failed")


if __name__ == "__main__":
    unittest.main()

"""Tests of catabackport on a tiny synthetic build (tests/fixture.py): no network, no game files, no Converter (a stand-in copies).

Run: cd realm/warcraft/tools && python3 -m unittest discover -s catabackport/tests -t . -v
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from catabackport import cli, ids, inventory, pack, plan, source as src, util, validate, world  # noqa: E402
from catabackport.tests import fixture  # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


class Resp:
    def __init__(self, data, length=None):
        self.data = data
        self.headers = {"Content-Length": str(len(data) if length is None else length)}

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class SourceTests(unittest.TestCase):
    def make(self, script, tries=4, budget=None):
        calls = []

        def urlopen(req, timeout=0):
            calls.append(req.full_url)
            r = script[min(len(calls) - 1, len(script) - 1)]
            if isinstance(r, Exception):
                raise r
            return r

        sleeps = []
        return src.HttpSource("4.4.2.60895", tries=tries, budget=budget, sleep=sleeps.append, urlopen=urlopen), calls, sleeps

    def test_retries_then_succeeds(self):
        s, calls, sleeps = self.make([urllib.error.HTTPError("u", 500, "err", {}, None), IOError("reset"), Resp(b"data")])
        self.assertEqual(s.file(5), b"data")
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(sleeps), 2)
        self.assertIn("/api/casc/5?download&version=4.4.2.60895", calls[0])

    def test_404_is_missing_not_retried(self):
        s, calls, _ = self.make([urllib.error.HTTPError("u", 404, "nf", {}, None)])
        with self.assertRaises(src.Missing):
            s.file(5)
        self.assertEqual(len(calls), 1)

    def test_down_for_good_is_source_down(self):
        s, calls, _ = self.make([urllib.error.HTTPError("u", 500, "err", {}, None)], tries=3)
        with self.assertRaises(src.SourceDown):
            s.table("Map")
        self.assertEqual(len(calls), 3)

    def test_html_error_page_for_a_table_is_retried(self):
        s, calls, _ = self.make([Resp(b"<!DOCTYPE html><html>Server Error"), Resp(b"ID\n1\n")])
        self.assertEqual(s.table("Map"), "ID\n1\n")
        self.assertEqual(len(calls), 2)

    def test_truncated_body_is_retried(self):
        s, calls, _ = self.make([Resp(b"abc", length=10), Resp(b"abcdefghij")])
        self.assertEqual(s.file(1), b"abcdefghij")

    def test_budget_ends_the_waiting(self):
        t = [0.0]
        budget = src.Budget(10, clock=lambda: t[0])
        s, calls, sleeps = self.make([IOError("down")], tries=50, budget=budget)
        s.sleep = lambda w: t.__setitem__(0, t[0] + 6)
        with self.assertRaises(src.SourceDown):
            s.file(1)
        self.assertLess(len(calls), 5)

    def test_chain_and_cache(self):
        with tempfile.TemporaryDirectory() as d:
            fixture.build(os.path.join(d, "fx"))
            down = self.make([IOError("x")], tries=1)[0]
            chain = src.ChainSource([down, src.DirSource(os.path.join(d, "fx"))])
            cached = src.CachedSource(chain, os.path.join(d, "cache"))
            self.assertTrue(cached.file(5000).startswith(b"\x52\x45\x56\x4d"))     # REVM
            shutil.rmtree(os.path.join(d, "fx"))                                    # the source gone: the cache answers
            self.assertTrue(cached.file(5000))
            with self.assertRaises(src.SourceDown):              # (the first source is down: "not in the build" can't be said)
                cached.file(424242)
            only = src.CachedSource(src.DirSource(os.path.join(d, "none")), os.path.join(d, "cache2"))
            with self.assertRaises(src.Missing):
                only.file(424242)
            with self.assertRaises(src.Missing):                  # (and the miss is kept)
                only.file(424242)


class IdTests(unittest.TestCase):
    def test_map_ids_keep_or_move(self):
        got = ids.alloc_map_ids([36, 900, 902], {36, 1}, set(), {})
        self.assertEqual(got, {36: 5036, 900: 900, 902: 902})

    def test_area_ids_and_bits(self):
        self.assertEqual(ids.alloc_area_ids([3000, 4000], {3000}), {3000: ids.AREA_BASE, 4000: 4000})
        bits, none = ids.alloc_explore_bits({1: 10, 2: 4090, 3: 5000}, {10})
        self.assertEqual(bits[2], 4090)           # free and under 4096: kept
        self.assertEqual(bits[1], 3618)           # 10 is taken: the first free bit past 3.3.5a's
        self.assertEqual(bits[3], 3619)           # 5000 does not fit the character's 4096 bits
        self.assertEqual(none, [])

    def test_bits_exhausted_are_reported(self):
        areas = {i: 1 for i in range(1, 600)}
        bits, none = ids.alloc_explore_bits(areas, {1})
        self.assertEqual(len(none), 599 - len(ids.FREE_BITS))
        self.assertTrue(all(bits[a] == 0 for a in none))


class InventoryPlanTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.lf = fixture.build(self.d)
        self.pins = util.pins()
        self.manifest = inventory.run(src.DirSource(self.d), self.pins, os.path.join(self.d, "work"), self.lf)

    def tearDown(self):
        shutil.rmtree(self.d)

    def by(self):
        return {m["id"]: m for m in self.manifest["maps"]}

    def test_maps_taken_and_not(self):
        b = self.by()
        self.assertEqual(sorted(b), [36, 900, 901, 902])
        report = open(os.path.join(self.d, "work", "inventory-report.txt")).read()
        self.assertIn("expansion 4 is past Cataclysm", report)
        self.assertIn("no directory", report)

    def test_swap_group_ids_tiles(self):
        b = self.by()
        self.assertEqual(b[901]["swap_of"], 900)
        self.assertEqual(b[901]["group"], "swap")
        self.assertEqual(b[900]["group"], "dungeon")
        self.assertEqual(b[36]["new_id"], 5036)
        self.assertEqual(b[36]["new_dir"], "DeadminesInstanceCata")
        self.assertEqual(b[900]["n_tiles"], 2)
        self.assertEqual(b[900]["tiles_from"], "wdt")
        self.assertEqual(self.manifest["proof"], 36 if b[36]["n_tiles"] < b[900]["n_tiles"] else 900)

    def test_inventory_deterministic(self):
        again = inventory.run(src.DirSource(self.d), self.pins, os.path.join(self.d, "work2"), self.lf)
        self.assertEqual(json.dumps(again, sort_keys=True), json.dumps(self.manifest, sort_keys=True))

    def test_plan_selects_and_splits(self):
        p = plan.make(self.manifest, "all", shards=2, max_tiles=8)
        names = [u["unit"] for u in p["units"]]
        self.assertIn("bigworld-r0", names)
        self.assertEqual(sum(1 for n in names if n.startswith("bigworld-r")), 2)      # (whole rows: 10 tiles each, past 8)
        self.assertEqual(sorted(u["part"] for u in p["units"] if u["map"] == 902), [0, 1])
        swap = next(u for u in p["units"] if u["map"] == 901)
        base = next(u for u in p["units"] if u["map"] == 900)
        self.assertEqual(swap["shard"], base["shard"])
        self.assertEqual(swap["base"], "tinydungeon")
        self.assertLess(p["units"].index(base), p["units"].index(swap))
        self.assertEqual(json.dumps(p, sort_keys=True), json.dumps(plan.make(self.manifest, "all", shards=2, max_tiles=8), sort_keys=True))

    def test_plan_specs_and_matrix(self):
        self.assertEqual([u["map"] for u in plan.make(self.manifest, "tinydungeon")["units"]], [900])
        self.assertEqual({u["map"] for u in plan.make(self.manifest, "group:dungeon")["units"]}, {36, 900})
        with self.assertRaises(SystemExit):
            plan.make(self.manifest, "nothing-like-this")
        p = plan.make(self.manifest, "all", shards=3)
        mx = plan.matrix(p)
        self.assertLessEqual(len(mx["include"]), 3)
        self.assertEqual(plan.for_shard(p, "all"), p["units"])
        self.assertEqual(sum(len(plan.for_shard(p, f"{i}/{p['shards']}")) for i in range(p["shards"])), len(p["units"]))

    def test_skip_done(self):
        p = plan.make(self.manifest, "all")
        done = {u["unit"]: u["input_hash"] for u in p["units"] if u["map"] == 900}
        p2 = plan.make(self.manifest, "all", done_hashes=done)
        self.assertNotIn("tinydungeon", [u["unit"] for u in p2["units"]])
        self.assertIn("tinydungeon", p2["skipped"])
        self.assertTrue(any("tinydungeonphase1" in s for s in p2["skipped"]))      # (its base is not in the plan)


class ValidateTests(unittest.TestCase):
    def test_checks(self):
        self.assertIsNone(validate.check_adt(fixture.adt()))
        self.assertIn("MCIN", validate.check_adt(fixture.chunk(b"MVER", b"\x12\0\0\0")))
        self.assertIsNone(validate.check_wdt(fixture.wdt([(0, 0)])))
        self.assertIsNotNone(validate.check_m2(b"MD21xxxx"))
        self.assertIsNone(validate.check_blp(fixture.blp()))
        self.assertIsNotNone(validate.check_blp(fixture.blp(9999, 4)))

    def test_run_drops_bad_files_and_counts_unresolved(self):
        with tempfile.TemporaryDirectory() as d:
            files = os.path.join(d, "files")
            os.makedirs(os.path.join(files, "world", "maps", "x"))
            open(os.path.join(files, "world", "maps", "x", "x_0_0.adt"), "wb").write(fixture.adt(["tileset/missing.blp"]))
            open(os.path.join(files, "bad.m2"), "wb").write(b"MD21 nonsense")
            r = validate.run(files)
            self.assertEqual(r["status"], "partial")
            self.assertEqual(r["dropped"], 1)
            self.assertFalse(os.path.exists(os.path.join(files, "bad.m2")))
            self.assertEqual(r["unresolved"]["count"], 1)
            open(os.path.join(files, "world", "maps", "x", "x_0_0.adt"), "wb").write(b"junk")
            self.assertEqual(validate.run(files)["status"], "failed")


class WorldTests(unittest.TestCase):
    CPP = """CREATE TABLE `creature` (\n  `guid` int unsigned NOT NULL,\n  `id` int NOT NULL,\n  `map` smallint NOT NULL,\n  `phaseMask` int,\n  `npcflag` int,\n  `curmana` int,\n  PRIMARY KEY (`guid`)\n) ENGINE=InnoDB;\n"""
    AC = """CREATE TABLE `creature` (\n  `guid` int unsigned NOT NULL,\n  `id` int NOT NULL,\n  `map` smallint NOT NULL,\n  `phaseMask` int,\n  `npcflag` int,\n  `Comment` text,\n  PRIMARY KEY (`guid`)\n) ENGINE=InnoDB;\n"""

    def test_schema_and_sql(self):
        cpp, ac = world.parse_schema(self.CPP), world.parse_schema(self.AC)
        self.assertEqual(cpp["creature"], ["guid", "id", "map", "phaseMask", "npcflag", "curmana"])
        m = {"id": 654, "new_id": 5654, "dir": "X", "name": "X"}
        sql, off, rep = world.generate(m, cpp, ac, 2000, 1000)
        self.assertIn("INSERT IGNORE INTO ac_world.`creature` (`guid`, `id`, `map`, `phaseMask`, `npcflag`)", sql)
        self.assertIn("`id` + 6000000", sql)
        self.assertIn("5654", sql)
        self.assertIn("`npcflag` & 67108863", sql)
        self.assertIn("ROW_NUMBER() OVER (ORDER BY `guid`)", sql)
        step = next(s for s in rep["steps"] if s["table"] == "creature")
        self.assertEqual(step["dropped"], ["curmana"])
        self.assertEqual(step["defaulted"], ["Comment"])
        self.assertTrue(any("creature_template" in s for s in rep["skipped"]))
        self.assertIn("smart_scripts", rep["not_built"])
        self.assertIn("`guid` >= 10002000 AND `guid` < 10003000", off)

    def test_guid_blocks(self):
        bases, spans = world.guid_bases({10: 2500, 5: 10})
        self.assertEqual((bases[5], spans[5], bases[10], spans[10]), (0, 1000, 1000, 3000))
        with self.assertRaises(ValueError):
            world.guid_bases({1: 20_000_000})


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.lf = fixture.build(self.d)
        open(os.path.join(self.d, "fake_conv.py"), "w").write(fixture.FAKE_CONVERTER)
        self.work = os.path.join(self.d, "work")
        self.common = ["--work", self.work, "--source", f"dir:{self.d}", "--listfile", self.lf]

    def tearDown(self):
        shutil.rmtree(self.d)

    def run_cli(self, *argv):
        out = io.StringIO()
        old = sys.stdout
        sys.stdout = out
        try:
            code = cli.main(list(argv))
        finally:
            sys.stdout = old
        return code, out.getvalue()

    def run_all(self, release, maps="tinydungeon,tinydungeonphase1", extra=()):
        self.assertEqual(self.run_cli("inventory", *self.common)[0], 0)
        self.assertEqual(self.run_cli("plan", "--work", self.work, "--maps", maps)[0], 0)
        return self.run_cli("run", *self.common, "--release", release, "--converter", f"{sys.executable} {self.d}/fake_conv.py",
                            "--dbd", os.path.join(self.d, "dbd"), *extra)

    def test_whole_run_and_resume_and_determinism(self):
        release = os.path.join(self.d, "release")
        code, out = self.run_all(release)
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.exists(os.path.join(release, "cata-tinydungeon.tar.xz")), out)
        self.assertTrue(os.path.exists(os.path.join(release, "cata-tinydungeonphase1.tar.xz")), out)
        # the pack's layout is the zones package's
        import lzma
        import tarfile
        with tarfile.open(fileobj=io.BytesIO(lzma.decompress(open(os.path.join(release, "cata-tinydungeon.tar.xz"), "rb").read()))) as t:
            names = t.getnames()
        for want in ("TAG", "pack.json", "client/files.txt", "client/same.txt", "client/minimap.txt", "client/dbc/Map.txt",
                     "client/dbc/AreaTable.txt", "client/files/world/maps/tinydungeon/tinydungeon.wdt",
                     "client/files/world/maps/tinydungeon/tinydungeon_0_0.adt", "client/files/tileset/test/ground.blp"):
            self.assertIn(want, names)
        self.assertFalse(any("_tex1" in n for n in names))
        # a terrain swap is made whole from its base: tiles (0,0) from the base, (1,0) its own
        with tarfile.open(fileobj=io.BytesIO(lzma.decompress(open(os.path.join(release, "cata-tinydungeonphase1.tar.xz"), "rb").read()))) as t:
            swap_names = t.getnames()
        self.assertIn("client/files/world/maps/tinydungeonphase1/tinydungeonphase1_0_0.adt", swap_names)
        self.assertIn("client/files/world/maps/tinydungeonphase1/tinydungeonphase1_1_0.adt", swap_names)
        # (a pack without server data is `partial`, said in its notes: the client half is good)
        idx0 = json.load(open(os.path.join(release, "cata-tinydungeon.json")))
        self.assertEqual(idx0["status"], "partial")
        self.assertTrue(any("not made" in p for p in idx0["report"]["problems"]))
        self.assertEqual(self.run_cli("assemble", "--release", release)[0], 0)
        idx = json.load(open(os.path.join(release, "index.json")))
        by = {p["unit"]: p for p in idx["packs"]}
        self.assertEqual(by["tinydungeonphase1"]["requires"], ["tinydungeon"])
        self.assertTrue(open(os.path.join(release, "summary.txt")).read().startswith("Cataclysm backport"))
        first = {n: sha(os.path.join(release, n)) for n in os.listdir(release) if n.endswith(".tar.xz")}
        # run again: resumes, and the packs are byte for byte the same
        code, out = self.run_cli("run", *self.common, "--release", release, "--converter", f"{sys.executable} {self.d}/fake_conv.py",
                                 "--dbd", os.path.join(self.d, "dbd"))
        self.assertEqual(code, 0, out)
        self.assertIn("fetch already done", out)
        self.assertEqual(first, {n: sha(os.path.join(release, n)) for n in os.listdir(release) if n.endswith(".tar.xz")})
        # and from scratch (--no-resume, a new work folder's worth of redone stages): the same bytes again
        code, out = self.run_cli("run", *self.common, "--release", release, "--no-resume", "--converter",
                                 f"{sys.executable} {self.d}/fake_conv.py", "--dbd", os.path.join(self.d, "dbd"))
        self.assertEqual(first, {n: sha(os.path.join(release, n)) for n in os.listdir(release) if n.endswith(".tar.xz")})

    def test_tables_rows(self):
        release = os.path.join(self.d, "release")
        self.run_all(release, maps="tinydungeon")
        text = open(os.path.join(self.work, "tinydungeon", "out", "client", "dbc", "AreaTable.txt")).read().split("\n")
        self.assertTrue(text[0].startswith("types\t"))
        rows = {l.split("\t")[1]: l.split("\t") for l in text if l.startswith("put")}
        self.assertEqual(set(rows), {"9000", str(ids.AREA_BASE)})       # the area id 3.3.5a has moved, the free one kept
        self.assertEqual(rows["9000"][2:5], ["900", str(ids.AREA_BASE), "4090"])   # (ID, ContinentID, Parent moved with it, AreaBit)
        self.assertEqual(int(rows["9000"][5]) & 0x400, 0)                  # (the expansion-only flying flag dropped)
        self.assertEqual(rows[str(ids.AREA_BASE)][4], "3618")              # (bit 10 was 3.3.5a's: the first free one past it)
        mp = open(os.path.join(self.work, "tinydungeon", "out", "client", "dbc", "Map.txt")).read().split("\n")
        self.assertTrue(any(l.startswith("put\t900\tTinyDungeon\t") for l in mp))

    def test_dry_run_touches_nothing(self):
        self.assertEqual(self.run_cli("inventory", *self.common)[0], 0)
        self.run_cli("plan", "--work", self.work, "--maps", "tinydungeon")
        code, out = self.run_cli("run", *self.common, "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("would run fetch", out)
        self.assertFalse(os.path.exists(os.path.join(self.work, "tinydungeon", "stage")))

    def test_source_down_defers_not_fails(self):
        self.assertEqual(self.run_cli("inventory", *self.common)[0], 0)
        self.run_cli("plan", "--work", self.work, "--maps", "tinydungeon")
        cache = os.path.join(self.d, "emptycache")
        # a source that is down: a url source on a closed port with no retries to wait on
        code, out = self.run_cli("run", "--work", self.work, "--source", "url:http://127.0.0.1:9", "--cache", cache,
                                 "--listfile", self.lf, "--stage-budget", "0", "--stages", "fetch")
        self.assertEqual(code, cli.EX_DEFERRED, out)
        self.assertIn("deferred", out)
        state = json.load(open(os.path.join(self.work, "status-allofall.json".replace("allofall", "all"))))
        self.assertEqual(state["results"][0]["status"], "deferred")

    def test_inventory_with_source_down_exits_75(self):
        code, out = self.run_cli("inventory", "--work", self.work, "--source", "url:http://127.0.0.1:9", "--stage-budget", "0")
        self.assertEqual(code, cli.EX_DEFERRED, out)
        self.assertFalse(os.path.exists(os.path.join(self.work, "manifest.json")))


if __name__ == "__main__":
    unittest.main()

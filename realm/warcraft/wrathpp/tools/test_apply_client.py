"""Tests of tools/apply_client.py: the allied races' change files on a small table (put replaces a row of the same id, adds
otherwise; strings; floats; putraw; appendraw once; copyrow; remapfield; or and set; drop; map), and a whole run on the stock tables
(ChrRaces gets the new races' rows; the creatures' race moves). Run by protocol/tests/run.sh (python3 -I)."""
import os
import struct
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_client as A  # noqa: E402


def table(rows, kinds="iisf"):
    text = bytearray(b"\0")
    recs = []
    for r in rows:
        rec = bytearray()
        for k, v in zip(kinds, r):
            if k == "s":
                rec += struct.pack("<I", len(text)); text += v.encode() + b"\0"
            elif k == "f":
                rec += struct.pack("<f", v)
            else:
                rec += struct.pack("<I", v)
        recs.append(bytes(rec))
    n = len(kinds)
    return A.Table(struct.pack("<4s4I", b"WDBC", len(recs), n, n * 4, len(text)) + b"".join(recs) + bytes(text))


def rows(t, kinds="iisf"):
    out = []
    for i in range(len(t.records)):
        r = []
        for f, k in enumerate(kinds):
            v = t.get(i, f)
            if k == "s":
                end = t.text.index(b"\0", v); r.append(bytes(t.text[v:end]).decode())
            elif k == "f":
                r.append(round(struct.unpack("<f", struct.pack("<I", v))[0], 3))
            else:
                r.append(v)
        out.append(r)
    return out


class ApplyTest(unittest.TestCase):
    def test_char_sections_sorted_in_runs_keeping_the_order_within_a_group(self):
        # id race sex section tex1 tex2 tex3 flags variation colour: race 5's variation 0 split over two runs by a later row
        rows = [(1, 5, 0, 0, 0, 0, 0, 1, 0, 0), (2, 5, 0, 0, 0, 0, 0, 1, 1, 0), (3, 4, 0, 0, 0, 0, 0, 1, 0, 0), (4, 5, 0, 0, 0, 0, 0, 4, 0, 1),
                (5, 4, 1, 0, 0, 0, 0, 1, 0, 0), (6, 5, 0, 0, 0, 0, 0, 1, 1, 1)]
        t = table(rows, "i" * 10)
        A.sort_char_sections(t)
        got = [struct.unpack_from("<I", r, 0)[0] for r in t.records]
        self.assertEqual(got, [3, 5, 1, 4, 2, 6])
    def test_round_trip(self):
        t = table([[1, 2, "Orc", 1.5], [2, 3, "Human\\Male", 2.0]])
        self.assertEqual(rows(A.Table(t.write())), rows(t))

    def test_put_copy_remap_or_set(self):
        t = table([[1, 10, "a", 1.0], [2, 10, "b", 2.0], [3, 7, "c", 3.0]])
        A.apply(t, "# x\ntypes\tiisf\nput\t2\t99\tnew\\\\name\t4.5\nput\t4\t5\tfour\t0.25\ncopyrow\t1\t9\ncopyrow\t1\t2\n"
                   "remapfield\t1\t10\t11\nor\t3\t1\t8\nset\t4\t1\t77\nor\t55\t1\t1\n")
        self.assertEqual(rows(t), [[1, 11, "a", 1.0], [2, 99, "new\\name", 4.5], [3, 15, "c", 3.0], [4, 77, "four", 0.25], [9, 11, "a", 1.0]])

    def test_drop(self):
        t = table([[1, 10, "a", 1.0], [2, 10, "b", 2.0], [3, 7, "c", 3.0]])
        A.apply(t, "types\tiisf\ndrop\t1\t10\t0\t2\nput\t2\t1\tz\t0.0\n")
        self.assertEqual([r[0] for r in rows(t)], [1, 3, 2])
        with self.assertRaises(ValueError):
            A.apply(t, "drop\t1\n")

    def test_map_is_a_rule_over_the_rows_a_condition_chooses(self):
        # id race sex number: the rows of race 4 sex 1 get field 3 looked up, each once (2 becomes 3, not 7), the unlisted the default
        t = table([[1, 4, 1, 2], [2, 4, 1, 3], [3, 4, 0, 2], [4, 5, 1, 9], [5, 4, 1, 40]], "iiii")
        A.apply(t, "map\t1=4,2=1\t3\t3\t0\t2=3\t3=7\n")
        self.assertEqual(rows(t, "iiii"), [[1, 4, 1, 3], [2, 4, 1, 7], [3, 4, 0, 2], [4, 5, 1, 9], [5, 4, 1, 0]])
        # no default: an unlisted row is left; a key of two fields; every row ("-"); the fields read as the line finds them
        A.apply(t, "map\t-\t1,2\t3\t-\t4,0=11\t5,1=12\nmap\t1=4\t3\t2\t-\t11=6\n")
        self.assertEqual(rows(t, "iiii"), [[1, 4, 1, 3], [2, 4, 1, 7], [3, 4, 6, 11], [4, 5, 1, 12], [5, 4, 1, 0]])
        # the id field: a row put after it replaces the row that now has the id
        A.apply(t, "types\tiiii\nmap\t-\t0\t0\t-\t5=50\nput\t50\t1\t1\t1\n")
        self.assertEqual(rows(t, "iiii")[-1], [50, 1, 1, 1])
        self.assertEqual(len(t.records), 5)

    def test_map_errors(self):
        t = table([[1, 4, 1, 2]], "iiii")
        for bad in ("map\t-\t3\n", "map\t-\t9\t3\t0\n", "map\t-\t3\t9\t0\n", "map\t9=1\t3\t3\t0\n", "map\t1\t3\t3\t0\n",
                    "map\t-\t1,2\t3\t0\t4=1\n", "map\t-\t3\t3\tx\n", "map\t-\t3\t3\t0\t2\n", "map\t-\t-1\t3\t0\n"):
            with self.assertRaises(ValueError, msg=bad):
                A.apply(t, bad)
        self.assertEqual(rows(t, "iiii"), [[1, 4, 1, 2]])

    def test_appendraw_once_and_errors(self):
        t = table([[1, 1, "", 0.0]])
        raw = struct.pack("<IIIf", 5, 6, 0, 1.0).hex()
        A.apply(t, "appendraw\t%s\nappendraw\t%s\n" % (raw, raw))
        self.assertEqual(len(t.records), 2)
        with self.assertRaises(ValueError):
            A.apply(t, "types\tii\n")                       # not this table
        with self.assertRaises(ValueError):
            A.apply(t, "types\tiisf\nput\t1\t2\n")           # a short row
        with self.assertRaises(ValueError):
            A.apply(t, "frobnicate\t1\n")

    def test_stock_run(self):
        stock = os.environ.get("WRATHPP_TEST_DBC")
        changes = os.environ.get("WRATHPP_TEST_CHANGES")
        if not (stock and changes and os.path.isdir(stock) and os.path.isdir(changes)):
            self.skipTest("WRATHPP_TEST_DBC and WRATHPP_TEST_CHANGES name the stock tables and the generated changes")
        with open(os.path.join(stock, "ChrRaces.dbc"), "rb") as f:
            t = A.Table(f.read())
        before = len(t.records)
        with open(os.path.join(changes, "ChrRaces.txt"), encoding="utf-8") as f:
            A.apply(t, f.read())
        ids = [t.get(i, 0) for i in range(len(t.records))]
        self.assertEqual(sorted(set(range(22, 32)) & set(ids)), list(range(22, 32)))
        self.assertIn(32, ids)                                # the Fel Orcs' row moved
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(t.records), before + 11)


if __name__ == "__main__":
    unittest.main()

import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_looks  # noqa: E402,F401  (puts the allied races' tools on the path)
import extra_skins  # noqa: E402


def model():
    skin = lambda i: {"base": i, "body": 100 + i, "choice": str(10 + i), "index": i, "order": i, "pelvis": 200, "torso": 201, "tattoo": [], "tattoo_name": "None"}
    return {"name": "HumanFemale", "folder": "Character\\Human\\Female", "sex": 1, "tattoos": ["None"], "base_skins": 2, "skins": [skin(0), skin(1)],
            "faces": [{"choice": "50", "skins": [0, 1], "textures": {"0": 300, "1": 301}}], "eyes": [{"index": 0, "file": 400}, {"index": 1, "file": 401}],
            "hair": [{"variation": 0, "geoset": 1}], "hair_colors": [{"index": 0, "file": 500, "choice": "60"}], "features": []}


def looks():
    return {"build": "x", "races": {"1": {"race": 1, "name": "Human", "models": {"1": model(), "0": model()}}}}


SPEC = {"race": 1, "sex": 1, "name": "Ash", "file": 201749, "swatch": (26, 26, 24), "build": None}


class ExtraSkinTest(unittest.TestCase):
    def test_the_skin_is_the_next_colour_of_its_model_only(self):
        d = extra_skins.extend(looks(), [SPEC])
        m, other = d["races"]["1"]["models"]["1"], d["races"]["1"]["models"]["0"]
        self.assertEqual((m["base_skins"], len(m["skins"])), (3, 3))
        s = m["skins"][2]
        self.assertEqual((s["index"], s["base"], s["choice"], s["pelvis"], s["torso"], s["bare"]), (2, 2, "extra:ash", 0, 0, True))
        self.assertEqual(m["faces"][0]["skins"], [0, 1, 2])
        self.assertEqual(m["extra_files"], {str(s["body"]): {"file": 201749, "build": None}})
        row = m["extra_choices"]["Skin Color"][0]
        self.assertEqual((row["ID"], row["Name_lang"], row["SwatchColor_0"], row["keep"]), ("extra:ash", "Ash", str(26 << 16 | 26 << 8 | 24), True))
        self.assertEqual(len(other["skins"]), 2)                               # the man is not touched

    def test_done_once_and_refused_on_tattoo_blocks(self):
        d = extra_skins.extend(extra_skins.extend(looks(), [SPEC]), [SPEC])
        self.assertEqual(len(d["races"]["1"]["models"]["1"]["skins"]), 3)
        bad = looks()
        bad["races"]["1"]["models"]["1"]["tattoos"] = ["None", "Dots"]
        with self.assertRaises(ValueError):
            extra_skins.extend(bad, [SPEC])

    def test_a_race_the_looks_lack_is_passed_by(self):
        d = extra_skins.extend(looks(), [dict(SPEC, race=7)])
        self.assertEqual(len(d["races"]["1"]["models"]["1"]["skins"]), 2)

    def test_the_rows_exist_with_no_textures_for_the_painted_in_parts(self):
        d = extra_skins.extend(looks(), [SPEC])
        sections, _, _ = sl_looks.table_rows({"races": {"1": dict(d["races"]["1"], models={"1": d["races"]["1"]["models"]["1"]})}})
        new = [r for r in sections if r[8] == 2 and r[2] in (0, 1, 4)]
        kinds = sorted(r[2] for r in new)
        self.assertEqual(kinds, [0, 1, 1, 4])                                  # the skin, a row a face x eye colour, the underwear
        self.assertTrue(new[0][3].endswith("HumanFemaleSkin00_02.blp"))
        for r in new:
            if r[2] != 0:
                self.assertEqual((r[3], r[4]), ("", ""))                        # no look-up misses a row; the picture has them painted in
        old = [r for r in sections if r[8] == 1 and r[2] == 1]
        self.assertTrue(all(r[3] for r in old))                                # the other skins' faces as they were
        self.assertEqual(sorted(r[7] for r in new if r[2] == 1), [0, 1])       # the faces' numbers as for any skin

    def test_the_reader_makes_the_body_twice_as_wide(self):
        import numpy as np
        import blp
        picture = np.zeros((8, 8, 4), dtype=np.uint8)
        picture[:, :, 0], picture[:, :, 3] = 200, 255
        seen = []
        read = lambda fid: (seen.append(fid), blp.write_dxt(picture, alpha=False))[1]
        got = blp.read(extra_skins.Reader(read, {str(extra_skins.EXTRA_BASE): {"file": 7, "build": None}}, None)(extra_skins.EXTRA_BASE))
        self.assertEqual((got.shape[0], got.shape[1]), (8, 16))
        self.assertEqual(seen, [7])
        self.assertEqual(extra_skins.Reader(read, {}, None)(9), blp.write_dxt(picture, alpha=False))      # any other file as it is


if __name__ == "__main__":
    unittest.main()

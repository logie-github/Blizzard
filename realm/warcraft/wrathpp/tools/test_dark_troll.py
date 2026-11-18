"""Tests of tools/dark_troll.py: the Night Elf's and the dark trolls' own colours added to a (made-up) Troll's skins and hair, the made-up
files' textures tinted to the wanted mean colour from the Troll's nearest. Run by protocol/tests/run.sh (python3 -I)."""
import copy
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools"))
import blp  # noqa: E402
import dark_troll as D  # noqa: E402


def solid(rgb, w=16, h=16):
    a = np.zeros((h, w, 4), dtype=np.uint8)
    a[:, :] = list(rgb) + [255]
    a[::2, ::2, :3] = np.clip(np.array(rgb) * 0.8, 0, 255)       # (some detail to keep)
    return blp.write_dxt(a, alpha=True)


def model():
    return {"name": "DarkTrollMale", "base_skins": 2, "tattoos": 1,
            "skins": [{"choice": "t1", "index": 0, "base": 0, "body": 11, "pelvis": 12, "torso": 13, "tattoo": [], "tattoo_name": "None"},
                      {"choice": "t2", "index": 1, "base": 1, "body": 21, "pelvis": 22, "torso": 23, "tattoo": [], "tattoo_name": "None"}],
            "faces": [{"choice": "f1", "textures": {"0": 14, "1": 24}, "skins": [0, 1]}],
            "hair": [{"variation": 0, "scalp": {"0": 301, "1": 302}}], "hair_colors": [{"index": 0, "file": 31, "choice": "h1"}, {"index": 1, "file": 32, "choice": "h2"}]}


def ne():
    return {"base_skins": 1, "skins": [{"choice": "n1", "body": 51, "pelvis": 52, "torso": 53}],
            "hair_colors": [{"index": 0, "file": 61, "choice": "nh1"}]}


FILES = {11: (200, 40, 40), 12: (200, 40, 40), 13: (200, 40, 40), 14: (200, 40, 40), 21: (40, 40, 200), 22: (40, 40, 200), 23: (40, 40, 200),
         24: (40, 40, 200), 31: (90, 60, 30), 32: (30, 30, 30), 301: (90, 60, 30), 302: (30, 30, 30), 51: (60, 60, 160), 52: (60, 60, 160),
         53: (60, 60, 160), 61: (30, 120, 60)}


def read(fid):
    return solid(FILES[fid])


class DarkTroll(unittest.TestCase):
    def test_extended(self):
        m = model()
        specs, extra = D.extend(m, ne())
        self.assertEqual(m["base_skins"], 2 + 1 + len(D.OWN_SKINS))
        self.assertEqual(len(m["skins"]), m["base_skins"])
        self.assertEqual([s["index"] for s in m["skins"]], list(range(m["base_skins"])))
        self.assertEqual(m["skins"][2]["base"], 2)
        self.assertIn("2", m["faces"][0]["textures"])
        self.assertTrue(set(m["faces"][0]["skins"]) >= {0, 1, 2})
        self.assertEqual(len(m["hair_colors"]), 3)
        self.assertEqual(m["hair_colors"][2]["choice"], "nh1")
        self.assertIn("2", m["hair"][0]["scalp"])
        self.assertEqual([r["ID"] for r in extra["Skin Color"]][0], "n1")
        self.assertEqual(len(extra["Skin Color"]), 1 + len(D.OWN_SKINS))
        self.assertEqual([r["ID"] for r in extra["Hair Color"]], ["nh1"])
        self.assertTrue(all(int(k) >= D.SYNTH for k in specs))

    def test_the_made_up_files_are_the_nearest_trolls_tinted_to_the_wanted_mean(self):
        m = model()
        specs, _ = D.extend(m, ne())
        r = D.Resolver(read, specs)
        body = blp.read(r(m["skins"][2]["body"]))          # wants the night elf's blue (60, 60, 160): nearest is the troll's blue skin
        mean = D.mean_rgb(body)
        self.assertLess(abs(mean[2] - 160), 25)
        self.assertLess(abs(mean[0] - 60), 25)
        # the underwear and the face of that skin are of the same troll skin and factor
        face = blp.read(r(m["faces"][0]["textures"]["2"]))
        self.assertGreater(D.mean_rgb(face)[2], D.mean_rgb(face)[0])
        grey = blp.read(r(m["skins"][3]["body"]))          # Ash Grey (152, 152, 162)
        self.assertLess(abs(D.mean_rgb(grey)[0] - 152), 30)
        hair = blp.read(r(m["hair_colors"][2]["file"]))    # the night elf's green hair
        self.assertGreater(D.mean_rgb(hair)[1], D.mean_rgb(hair)[0])
        # a file id of today's passes through
        self.assertEqual(r(11), read(11))

    def test_a_recolour_keeps_the_shading_and_leaves_what_is_not_skin(self):
        base = np.zeros((4, 4, 4), dtype=np.uint8)
        base[..., 3] = 255
        base[0, 0] = (40, 100, 200, 255)      # blue skin, shaded
        base[0, 1] = (20, 50, 100, 255)       # the same skin in shadow
        base[1, 0] = (235, 228, 210, 255)     # a tusk (not the skin's hue)
        base[1, 1] = (250, 250, 250, 255)     # an eye's white
        ref = D.skin_reference(base)
        out = D.recolored(base, (60, 60, 70), ref)
        lit, dark = out[0, 0, :3].astype(int), out[0, 1, :3].astype(int)
        self.assertLess(abs(int(lit[0]) - int(lit[2])), 40)             # no longer blue: near the grey wanted
        self.assertGreater(lit.sum(), dark.sum() * 1.5)                # the shading kept
        self.assertEqual(tuple(out[1, 0]), (235, 228, 210, 255))        # tusk and eye white as they were
        self.assertEqual(tuple(out[1, 1]), (250, 250, 250, 255))

    def test_the_entry_has_its_own_name_specs_and_extra_choices(self):
        import sl_looks
        troll = {"race": 8, "name": "Troll", "replace_rows": True, "models": {"0": model()}}
        night = {"race": 4, "name": "NightElf", "models": {"0": ne()}}
        rows = {"n1": {"ID": "n1", "SwatchColor_0": "8421631", "SwatchColor_1": "0"}}
        dt = sl_looks.dark_troll_entry(troll, night, rows)
        m = dt["models"]["0"]
        self.assertEqual(dt["name"], "DarkTroll")
        self.assertFalse(dt["replace_rows"])
        self.assertTrue(m["synth"])
        self.assertEqual(m["extra_choices"]["Skin Color"][0]["SwatchColor_0"], "8421631")
        self.assertEqual(int(m["extra_choices"]["Skin Color"][-1]["SwatchColor_0"]), 112 << 16 | 74 << 8 | 150)
        self.assertEqual(troll["models"]["0"]["base_skins"], 2)                    # (the Troll's own entry is left alone)

    def test_the_sexes_made_up_ids_never_meet(self):
        import sl_looks
        troll = {"race": 8, "name": "Troll", "replace_rows": True, "models": {"0": model(), "1": model()}}
        night = {"race": 4, "name": "NightElf", "models": {"0": ne(), "1": ne()}}
        dt = sl_looks.dark_troll_entry(troll, night, {})
        man, woman = dt["models"]["0"]["synth"], dt["models"]["1"]["synth"]
        # (package() merges the sexes' specs by id: one id for two specs made the man's skins from the woman's, a face for a body)
        self.assertTrue(man and woman)
        self.assertFalse(set(man) & set(woman))

    def test_extend_leaves_the_night_elf_alone(self):
        n = ne(); before = copy.deepcopy(n)
        D.extend(model(), n)
        self.assertEqual(n, before)


if __name__ == "__main__":
    unittest.main()

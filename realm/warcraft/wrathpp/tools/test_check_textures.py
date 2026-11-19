"""Tests of tools/check_textures.py: palettized, power-of-two, whole mip chain textures of a section's sizes pass; DXT ones, odd sizes,
wrong sizes and a cut mip chain are named. Run by protocol/tests/run.sh (python3 -I)."""
import os
import struct
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools"))
import blp  # noqa: E402
import check_textures as C  # noqa: E402


def rgba(w, h):
    return np.random.RandomState(1).randint(0, 255, (h, w, 4), dtype=np.uint8)


class CheckTextures(unittest.TestCase):
    def folder(self, files, rows):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "changes")); 
        for name, data in files.items():
            p = os.path.join(d, "client", *name.split("\\"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(data)
        lines = ["types\tiiiisssiii"]
        for i, (section, tex) in enumerate(rows):
            lines.append("\t".join(["put", str(i), "12", "0", str(section), tex, "", "", "0", "0", "0"]))
        open(os.path.join(d, "changes", "CharSections.txt"), "w").write("\n".join(lines) + "\n")
        return d

    def run_check(self, d):
        import io, contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = C.main(d)
        return code, out.getvalue()

    def test_good(self):
        d = self.folder({"Character\\A\\skin.blp": blp.write_palette(rgba(512, 512)), "Character\\A\\face.blp": blp.write_palette(rgba(256, 128)),
                         "Character\\A\\under.blp": blp.write_palette(rgba(256, 128), alpha=True)},
                        [(0, "Character\\A\\skin.blp"), (1, "Character\\A\\face.blp"), (4, "Character\\A\\under.blp")])
        code, out = self.run_check(d)
        self.assertEqual(code, 0, out)

    def test_bad(self):
        d = self.folder({"Character\\A\\dxt.blp": blp.write_dxt(rgba(512, 512)), "Character\\A\\big.blp": blp.write_palette(rgba(1024, 512)),
                         "Character\\A\\odd.blp": blp.write_palette(rgba(256, 256))},
                        [(0, "Character\\A\\dxt.blp"), (0, "Character\\A\\big.blp"), (1, "Character\\A\\odd.blp")])
        code, out = self.run_check(d)
        self.assertEqual(code, 1)
        self.assertIn("not palettized", out)
        self.assertIn("at most 512", out)

    def test_cut_mip_chain(self):
        data = bytearray(blp.write_palette(rgba(256, 128)))
        struct.pack_into("<I", data, 20 + 4 * 5, 0)          # mip 5's offset gone
        d = self.folder({"Character\\A\\cut.blp": bytes(data)}, [(1, "Character\\A\\cut.blp")])
        code, out = self.run_check(d)
        self.assertEqual(code, 1, out)
        self.assertIn("mip levels", out)

    def test_a_skins_extra_texture_is_not_pasted(self):
        d = self.folder({"Character\\A\\skin.blp": blp.write_palette(rgba(512, 512)), "Character\\A\\extra.blp": blp.write_dxt(rgba(1024, 512))}, [])
        lines = open(os.path.join(d, "changes", "CharSections.txt")).read()
        lines += "\t".join(["put", "9", "12", "0", "0", "Character\\A\\skin.blp", "Character\\A\\extra.blp", "", "0", "0", "0"]) + "\n"
        open(os.path.join(d, "changes", "CharSections.txt"), "w").write(lines)
        code, out = self.run_check(d)
        self.assertEqual(code, 0, out)

    def test_the_games_own_are_not_missing_problems(self):
        d = self.folder({}, [(0, "Character\\Human\\Male\\HumanMaleSkin00_00.blp")])
        code, out = self.run_check(d)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()

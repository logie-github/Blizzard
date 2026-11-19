#!/usr/bin/env python3
"""Shadowlands' character creator's own art for Wrath++'s creator on the 3.3.5 screen: the pieces Shadowlands draws its
creation screens from (the user, 12 November 2026: "why not just use the EXACT ASSETS from wago tools"), cut out of the
game's interface sheets pixel for pixel.

    python3 tools/sl_ui_art.py fetch CSV_DIR                 the atlas tables (wago.tools' CSVs at 9.2.7.45745)
    python3 tools/sl_ui_art.py package CSV_DIR CACHE OUT     OUT/client/Interface/Wrathpp/Creator/*.blp,
                                                             OUT/client/Interface/GlueXML/WrathppAtlas.lua, OUT/art.txt

Shadowlands draws from atlases: a sheet (a BLP of plain 32-bit colour) and a table saying where each named piece is on
it (UiTextureAtlas, UiTextureAtlasMember, UiTextureAtlasElement). 3.3.5 has no atlases, and its picture loader works in
a 1024 buffer where the creator's sheet is 2048 wide with no smaller levels, so every piece becomes a file of its own:

  * the piece's pixels as they are, in the middle of a canvas whose sides are powers of two, the rest of the canvas the
    piece's own edge carried outwards (what is drawn beside an edge is the edge, not a neighbour or a dark rim);
  * plain 32-bit colour as the sheet is (the 3.3.5 client reads the kind: CBLPFile::Lock2, COLOR_RAW), with smaller
    levels, so a 256 icon drawn 24 wide is not picked out of every tenth pixel;
  * WrathppAtlas.lua: name -> file, the piece's width and height, and where it is in its file (SetTexCoord's four).

Shadowlands trims its round buttons' pictures with a mask texture (CharCustomizeMaskedButtonTemplate's CircleMask:
Interface\\CharacterFrame\\TempPortraitAlphaMask, set in from the button's edge), which 3.3.5 cannot do. The trimmed
picture is made here instead: the same mask at the same place for each kind of button, as "<name>.<kind>".

Nothing of the game's is in the repository: the sheets are fetched when the package is made (CI), by file id."""
import csv
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ALLIED = os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools")
sys.path.insert(0, os.path.abspath(ALLIED))

BUILD = "9.2.7.45745"
USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"
TABLES = ("UiTextureAtlas", "UiTextureAtlasMember", "UiTextureAtlasElement", "ManifestInterfaceData")
FOLDER = "Interface\\Wrathpp\\Creator"

# The pieces Shadowlands' two creation screens are drawn from (Blizzard_CharacterCreate, Blizzard_CharacterCustomize
# and the shared templates they inherit: SelectionPopout*, CharCustomizeSmallButton, ThreeSliceButton "128-RedButton",
# SharedEditBox, the nine-slice "CharacterCreateDropdown"), by the start of their names.
WANTED = ("charactercreate-", "raceicon128-", "classicon-", "common-icon-", "common-button-square-gray-",
          "common-gray-button-entrybox-", "charactercreatedropdown-nineslice-", "_charactercreatedropdown-nineslice-",
          "!charactercreatedropdown-nineslice-", "common-radiobutton-", "128-redbutton-", "_128-redbutton-",
          "_charactercreate-")
# (the starting zones' paintings are 27 pictures of 1022 x 664: 100 MB as they are; the druid forms are not on 3.3.5's screen)
LEFT_OUT = ("charactercreate-startingzone-", "charactercreate-druidform-")

MASK = ("Interface\\CharacterFrame\\", "TempPortraitAlphaMask.blp")
# Shadowlands' round buttons: the button's size and how far its mask is set in from its edge (circleMaskSizeOffset),
# and whose pictures they show.
MASKED = {
    "category": (104, 105, 2, lambda n: n.startswith("charactercreate-icon-customize-")),
    "race": (79, 79, 2, lambda n: n.startswith("raceicon128-")),
    "class": (67, 67, 2, lambda n: n.startswith("classicon-")),
    "sex": (46, 46, -5, lambda n: n.startswith("charactercreate-gendericon-")),
}


def fetch(csv_dir):
    import urllib.request
    os.makedirs(csv_dir, exist_ok=True)
    for t in TABLES:
        url = "https://wago.tools/db2/%s/csv?build=%s" % (t, BUILD)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=300) as r:
            data = r.read()
        with open(os.path.join(csv_dir, t + ".csv"), "wb") as f:
            f.write(data)
        print("%s: %d bytes" % (t, len(data)))


def wago(file_id):
    """A file of the game at Shadowlands' last build (not today's: a sheet is repacked from build to build, and the
    table read here says where the pieces were in 9.2.7's)."""
    import time
    import urllib.request
    for attempt in range(4):
        try:
            url = "https://wago.tools/api/casc/%d?download&version=%s" % (file_id, BUILD)
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=300) as r:
                return r.read()
        except Exception as error:
            print("sl_ui_art: file %d: %s" % (file_id, error), file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("file %d couldn't be fetched" % file_id)


def cached(cache):
    os.makedirs(cache, exist_ok=True)

    def read(file_id):
        path = os.path.join(cache, "%d-%s" % (file_id, BUILD))
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            data = wago(file_id)
            with open(path + ".part", "wb") as out:
                out.write(data)
            os.replace(path + ".part", path)
        with open(path, "rb") as f:
            return f.read()
    return read


def rows(csv_dir, table):
    with open(os.path.join(csv_dir, table + ".csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def members(csv_dir):
    """Every piece wanted: name (the element's, which is what the interface asks an atlas for) -> sheet's file id, the
    sheet's size, the piece's rectangle (left, top, right, bottom)."""
    sheets = {r["ID"]: r for r in rows(csv_dir, "UiTextureAtlas")}
    elements = {r["ID"]: r["Name"] for r in rows(csv_dir, "UiTextureAtlasElement")}
    out = {}
    for m in rows(csv_dir, "UiTextureAtlasMember"):
        name = (elements.get(m["UiTextureAtlasElementID"]) or m["CommittedName"]).lower()
        if not name.startswith(WANTED) or name.startswith(LEFT_OUT):
            continue
        sheet = sheets[m["UiTextureAtlasID"]]
        box = tuple(int(m[k]) for k in ("CommittedLeft", "CommittedTop", "CommittedRight", "CommittedBottom"))
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        # the size the interface gives the piece where it asks for "the atlas's size": the table's own where it names
        # one (a 256 icon meant to be drawn 25 wide), the piece's pixels otherwise
        size = (int(m["OverrideWidth"]) or box[2] - box[0], int(m["OverrideHeight"]) or box[3] - box[1])
        out[name] = {"sheet": int(sheet["FileDataID"]), "sheet_size": (int(sheet["AtlasWidth"]), int(sheet["AtlasHeight"])), "box": box, "size": size}
    return out


def mask_id(csv_dir):
    for r in rows(csv_dir, "ManifestInterfaceData"):
        if r["FilePath"].lower() == MASK[0].lower() and r["FileName"].lower() == MASK[1].lower():
            return int(r["ID"])
    raise RuntimeError("the round mask (%s%s) is not in the game's list of interface files" % MASK)


def pow2(n):
    p = 1
    while p < n:
        p *= 2
    return p


# The 3.3.5 client draws no texture smaller than 8 on a side: "Texture size must be at least 8x8", and a solid green
# square in its place (Texture.cpp, CreateBlpTexture). Build 241's screen-edge shading (pieces 1 unit thick) covered
# the phone's screen in green.
MIN_SIDE = 8


def canvas(piece):
    """The piece in the middle of a canvas whose sides are powers of two and at least MIN_SIDE, its edges carried
    outwards over the rest. Returns the canvas and the piece's place in it (left, top)."""
    import numpy as np
    h, w = piece.shape[:2]
    cw, ch = max(MIN_SIDE, pow2(w)), max(MIN_SIDE, pow2(h))
    left, top = (cw - w) // 2, (ch - h) // 2
    ys = np.clip(np.arange(ch) - top, 0, h - 1)
    xs = np.clip(np.arange(cw) - left, 0, w - 1)
    return np.ascontiguousarray(piece[ys][:, xs]), left, top


def file_name(name):
    """A file's name for a piece: letters, digits, - and _ (a name may begin with _ or !, the game's marks for a piece
    that repeats along or down: h_ and v_ here)."""
    lead = {"_": "h_", "!": "v_"}.get(name[0], "")
    # (no dot: the client finds a texture's file by cutting its name at the last dot and adding .BLP
    # (TexturePickAlternateFilename), so "raceicon128-human-female.race" was "raceicon128-human-female.blp", the
    # untrimmed portrait, square on the phone in builds 241 to 246)
    return lead + re.sub(r"[^a-z0-9_-]", "-", (name[1:] if lead else name).replace(".", "_"))


def masked(piece, mask, width, height, inset):
    """The picture of a round button as Shadowlands shows it: the piece stretched over the button (width x height), its
    alpha multiplied by the mask laid over the button set in by [inset] on every side (nothing outside the mask)."""
    import numpy as np
    from PIL import Image
    h, w = piece.shape[:2]
    # the mask's rectangle on the button, in the piece's own pixels
    sx, sy = w / float(width), h / float(height)
    box = (inset * sx, inset * sy, (width - inset) * sx, (height - inset) * sy)
    mw, mh = max(1, int(round(box[2] - box[0]))), max(1, int(round(box[3] - box[1])))
    scaled = np.asarray(Image.fromarray(mask[:, :, 3], "L").resize((mw, mh), Image.Resampling.BICUBIC)).astype(np.float32) / 255.0
    over = np.zeros((h, w), dtype=np.float32)
    x0, y0 = int(round(box[0])), int(round(box[1]))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    cw, ch = min(mw - sx0, w - dx0), min(mh - sy0, h - dy0)
    if cw > 0 and ch > 0:
        over[dy0:dy0 + ch, dx0:dx0 + cw] = scaled[sy0:sy0 + ch, sx0:sx0 + cw]
    out = piece.copy()
    out[:, :, 3] = (piece[:, :, 3].astype(np.float32) * over).round().astype(np.uint8)
    return out


def write_raw(blp, rgba):
    """A BLP2 of plain 32-bit colour (the game's own kind 3: no palette, no compression, every pixel as it is) with smaller
    levels. Its header is the one Shadowlands' interface sheets carry (alpha 8 bits, no preferred format); the 3.3.5
    client reads the kind too (CBLPFile::Lock2, COLOR_RAW)."""
    import numpy as np
    from PIL import Image
    height, width = rgba.shape[:2]
    levels = []
    w, h = width, height
    # a smaller level is made of colour weighed by its alpha, or a clear pixel's colour would darken what is beside it
    premultiplied = Image.fromarray((rgba[:, :, :3].astype(np.float32) * (rgba[:, :, 3:4].astype(np.float32) / 255.0)).round().astype(np.uint8), "RGB")
    alpha = Image.fromarray(np.ascontiguousarray(rgba[:, :, 3]), "L")
    while True:
        if (w, h) == (width, height):
            level = rgba
        else:
            a = np.asarray(alpha.resize((w, h), Image.Resampling.BOX)).astype(np.float32)
            c = np.asarray(premultiplied.resize((w, h), Image.Resampling.BOX)).astype(np.float32)
            colour = np.where(a[:, :, None] > 0, c * 255.0 / np.maximum(a[:, :, None], 1.0), 0.0)
            level = np.dstack([np.clip(colour, 0, 255).round().astype(np.uint8), a.round().astype(np.uint8)])
        levels.append(np.ascontiguousarray(level[:, :, [2, 1, 0, 3]]).tobytes())      # RGBA -> BGRA
        if (w == 1 and h == 1) or len(levels) == 16:
            break
        w, h = max(1, w // 2), max(1, h // 2)
    return blp._blp(3, 8, 8, width, height, np.zeros((256, 4), dtype=np.uint8), levels, True)


def package(csv_dir, cache, out_dir):
    import blp
    read = cached(cache)
    wanted = members(csv_dir)
    art = os.path.join(out_dir, "client", *FOLDER.split("\\"))
    glue = os.path.join(out_dir, "client", "Interface", "GlueXML")
    os.makedirs(art, exist_ok=True)
    os.makedirs(glue, exist_ok=True)
    sheets = {}

    def sheet(file_id, size):
        if file_id not in sheets:
            pixels = blp.read(read(file_id))
            if (pixels.shape[1], pixels.shape[0]) != size:
                raise RuntimeError("sheet %d is %d x %d and the table of %s says %d x %d: not that build's file" % (
                    file_id, pixels.shape[1], pixels.shape[0], BUILD, size[0], size[1]))
            sheets[file_id] = pixels
        return sheets[file_id]

    mask = blp.read(read(mask_id(csv_dir)))
    entries, total = {}, 0

    def put(name, piece, size):
        nonlocal total
        made, left, top = canvas(piece)
        h, w = piece.shape[:2]
        ch, cw = made.shape[:2]
        data = write_raw(blp, made)
        fname = file_name(name)
        with open(os.path.join(art, fname + ".blp"), "wb") as f:
            f.write(data)
        total += len(data)
        entries[name] = (fname, size[0], size[1], left / float(cw), (left + w) / float(cw), top / float(ch), (top + h) / float(ch), cw, ch, w, h)

    for name in sorted(wanted):
        m = wanted[name]
        left, top, right, bottom = m["box"]
        piece = sheet(m["sheet"], m["sheet_size"])[top:bottom, left:right]
        put(name, piece, m["size"])
        for kind, (bw, bh, inset, mine) in MASKED.items():
            if mine(name):
                put(name + "." + kind, masked(piece, mask, bw, bh, inset), m["size"])

    # the Body tab's own picture, a woman's torso on the Face picture's disc (body_icon.py), chosen and not
    import body_icon
    for state in ("", "-selected"):
        head = "charactercreate-icon-customize-head" + state
        if head in wanted:
            m = wanted[head]
            left, top, right, bottom = m["box"]
            piece = body_icon.figure_piece(sheet(m["sheet"], m["sheet_size"])[top:bottom, left:right], state == "-selected")
            name = "charactercreate-icon-customize-figure" + state
            put(name, piece, m["size"])
            put(name + ".category", masked(piece, mask, *MASKED["category"][:3]), m["size"])

    with open(os.path.join(glue, "WrathppAtlas.lua"), "w", encoding="utf-8", newline="\n") as f:
        f.write("-- Shadowlands' creation screens' art (build %s), cut out of the game's sheets by tools/sl_ui_art.py:\n" % BUILD)
        f.write("-- name = { file, the width and height Shadowlands draws the piece at where it asks for the atlas's own size (in\n")
        f.write("-- its units: the screen 1080 high), and where the piece is in its file (left, right, top, bottom) }.\n")
        f.write("-- \"<name>.<kind>\" is a round button's picture with Shadowlands' mask already on it (category, race, class, sex).\n")
        f.write("WrathppAtlas = {\n")
        for name in sorted(entries):
            fname, w, h, l, r, t, b, cw, ch, pw, ph = entries[name]
            f.write('\t["%s"] = { "%s\\\\%s", %d, %d, %.6f, %.6f, %.6f, %.6f },\n' % (name, FOLDER.replace("\\", "\\\\"), fname, w, h, l, r, t, b))
        f.write("}\n")
    with open(os.path.join(out_dir, "art.txt"), "w", encoding="utf-8", newline="\n") as f:
        for name in sorted(entries):
            fname, w, h, l, r, t, b, cw, ch, pw, ph = entries[name]
            f.write("%s\t%s\\%s.blp\t%d x %d (drawn %d x %d) in %d x %d\n" % (name, FOLDER, fname, pw, ph, w, h, cw, ch))
    print("%d pieces (%d with a round button's mask) from %d sheets, %.1f MB" % (
        len(entries), sum(1 for n in entries if "." in n), len(sheets), total / 1048576.0))
    return entries


def main(argv):
    if len(argv) == 3 and argv[1] == "fetch":
        fetch(argv[2])
        return 0
    if len(argv) == 5 and argv[1] == "package":
        package(argv[2], argv[3], argv[4])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

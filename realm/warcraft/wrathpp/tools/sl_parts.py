"""Parts a mod hangs on a character (wxl.m2): models of their own, posed by the character's bones every frame
(WXL_M2_ATTACH_FOLLOW_BONES), for the Shadowlands options a 3.3.5 skin has no room for: a skin holds 65535 indices and
the character's hair and gear already fill them.

  head_shell(read, model, out_dir, log)   a shell over the character's head (today's head geosets, group 32, lifted 0.4 mm),
                                           drawn with a picture of its own (texture type 11, alpha blended): the
                                           options painted on the face (eyebrows, makeup, scars, paints) go on it
  overlay_picture(rgba, layout)           one such picture (a layer of the head, as today's game composes it) as the shell
                                           draws it: the face's place of the skin, 256 x 128, its alpha kept

How a part is made: m2.convert with the policy's `stand_only` (the model has its bones and the one sequence Stand and
nothing else: the character's bones pose it) and a geoset policy that keeps only the part's geosets; the shell then has its
vertices lifted out along their normals, its texture coordinates made the picture's own (the face's place of the skin
mapped onto the whole 256 x 128), its texture the replaceable type 11 and its material alpha blended. Nothing of the
game's is in the repository: the files are made by the looks' workflow (CI) from wago.tools' files."""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools")))

LIFT = 0.0004
HEAD_GROUP = 32
SHELL_TEXTURE = 11
VERTICES, TEXTURES, REPLACEABLE, MATERIALS = 0x3C, 0x50, 0x68, 0x70


def array(m, off):
    return struct.unpack_from("<II", m, off)


def patch_shell(m2b):
    """The converted head model made a shell: vertices out along their normals, texture coordinates the picture's, the
    texture replaceable type 11 and the materials alpha blended."""
    m = bytearray(m2b)
    n, o = array(m, VERTICES)
    for i in range(n):
        at = o + i * 48
        p = np.array(struct.unpack_from("<3f", m, at), np.float64)
        nrm = np.array(struct.unpack_from("<3f", m, at + 20), np.float64)
        struct.pack_into("<3f", m, at, *(p + nrm * LIFT))
        u, v = struct.unpack_from("<ff", m, at + 32)
        # the head's place in the composed skin: x 0 to 0.5, y 0.75 to 1; the picture is that place alone
        struct.pack_into("<ff", m, at + 32, min(1.0, max(0.0, u * 2.0)), min(1.0, max(0.0, (v - 0.75) * 4.0)))
    n, o = array(m, TEXTURES)
    body = [i for i in range(n) if struct.unpack_from("<I", m, o + i * 16)[0] == 1]
    if not body:
        raise ValueError("the shell has no body texture to make the picture's")
    for i in body:
        struct.pack_into("<I", m, o + i * 16, SHELL_TEXTURE)
    n, o = array(m, REPLACEABLE)
    table = list(struct.unpack_from("<%dh" % n, m, o))
    if len(table) <= SHELL_TEXTURE or table[SHELL_TEXTURE] != body[0]:
        if len(table) <= SHELL_TEXTURE:
            raise ValueError("the shell's replaceable table is too short (%d) to carry type %d" % (len(table), SHELL_TEXTURE))
        table[SHELL_TEXTURE] = body[0]
        struct.pack_into("<%dh" % n, m, o, *table)
    n, o = array(m, MATERIALS)
    for i in range(n):
        struct.pack_into("<HH", m, o + i * 4, 0, 2)
    return bytes(m)


def head_shell(read, model, out_dir, log=print):
    """Writes the model's head shell ("<Model>Face") into [out_dir]; the files written (the game's paths), or none for a
    model without a head geoset."""
    import m2
    import check_m2
    geosets = sorted(int(g) for g in model["geoset_policy"] if int(g) // 100 == HEAD_GROUP and int(g) % 100)
    if not geosets:
        log("%s: no head geoset: no shell" % model["name"])
        return []
    part = dict(model, name=model["name"] + "Face", geosets=None, stand_only=True,
                geoset_policy={str(g): [1 + i] for i, g in enumerate(geosets)}, drop_groups=list(range(0, 100)))
    written = m2.convert(read, part, out_dir, lambda *a: None)
    path = os.path.join(out_dir, model["folder"].replace("\\", "/"), part["name"] + ".m2")
    with open(path, "rb") as f:
        shell = patch_shell(f.read())
    with open(path, "wb") as f:
        f.write(shell)
    # (the check knows a character's texture types: a shell draws a picture of its own as type 11, as the body layer does)
    problems = [x for x in check_m2.check(path) if "type %d" % SHELL_TEXTURE not in x]
    if problems:
        raise ValueError("%s: %s" % (part["name"], "; ".join(problems[:10])))
    log("%s: head shell of %d geosets" % (part["name"], len(geosets)))
    return written


def resized_over(rgba, size):
    """[rgba] a picture with an alpha channel at another size, the colour weighed by the alpha (textures.resized_over)."""
    import textures
    return textures.resized_over(rgba, size)


def overlay_picture(rgba, layout):
    """A layer of the head as the shell draws it: the face's place of the skin, 256 x 128, the alpha kept. [rgba] is the head's
    own section (512 x 512, today's place of the head in its texture) or the whole skin's layer (1024 x 512: the head its right
    half). A layer opaque everywhere is one today's game blends into the skin by a mode of its own (scars and grime: laid over, mid
    grey changing nothing; a tattoo: multiplied, white changing nothing): the shell is alpha blended, so such a layer is made a
    black or white picture whose alpha is how far it is from the unchanging grey or white (the skin darkened or lightened by
    about as much)."""
    import textures
    h, w = rgba.shape[:2]
    if w == 2 * h:
        rgba = np.ascontiguousarray(rgba[:, w // 2:])
    if rgba[:, :, 3].min() == 255:
        grey = rgba[:, :, :3].astype(np.float32).mean(axis=2)
        out = np.zeros(rgba.shape, np.uint8)
        if np.median(grey) > 192:
            out[:, :, 3] = np.clip(255.0 - grey, 0, 255).astype(np.uint8)            # multiplied: white changes nothing, dark darkens
        else:
            # laid over (overlay/soft light: mid grey changes nothing, darker darkens, lighter lightens): black or white by how far from grey
            out[:, :, :3] = np.where(grey[:, :, None] > 127.5, 255, 0).astype(np.uint8)
            out[:, :, 3] = np.clip(np.abs(grey - 127.5) * 2.0, 0, 255).astype(np.uint8)
        rgba = out
    return textures.scalp_cut(rgba, layout)


def write_overlays(read, model, layout, out_dir, log=print):
    """Writes the pictures of the model's head overlays (model["overlays"]) into [out_dir]; the files written. [layout]: the
    model's own (m2.convert's: where its head went)."""
    import blp
    import names
    written, done = [], set()
    for option in model.get("overlays", []):
        for choice in option["choices"]:
            for fid in choice["files"].values():
                path = names.overlay(model, fid)
                if fid in done:
                    continue
                done.add(fid)
                full = os.path.join(out_dir, path.replace("\\", "/"))
                os.makedirs(os.path.dirname(full), exist_ok=True)
                picture = blp.read(read(fid))
                with open(full, "wb") as f:
                    f.write(blp.write_palette(np.ascontiguousarray(overlay_picture(picture, layout["head"])), alpha=True))
                written.append(path)
    if written:
        log("%s: %d overlay pictures" % (model["name"], len(written)))
    return written


def write_parts_table(looks, out_dir, ids):
    """Wrathpp/parts.txt in [out_dir] (the game's patch): what the add-on needs to draw a character's parts from the
    registry's choices, tab separated:

        S race sex slot category shell                            a picture over the head: the option (its registry category)
                                                                  and the shell it is drawn on, in slot `slot` of the character
        P race sex slot category style_category shell             the same for a paint whose picture follows another option's
                                                                  choice (its colour): `category` the colour's, `style_category` the style's
        C race sex category option colour picture                 the picture of a choice (1 from the first): `colour` is `*` for
                                                                  any, a hair colour's index, or `s<number>` for the style's choice

    [ids]: registry/parts_ids.json's keys. The path of the file written."""
    import names
    lines = []
    for entry in sorted(looks["races"].values(), key=lambda e: e["race"]):
        for sex, model in sorted(entry["models"].items()):
            slot = 0
            overlays = model.get("overlays", [])
            number = {}                                  # the style options' choice ids -> their numbers
            for option in overlays:
                if option.get("style"):
                    number[option["name"]] = {c["id"]: k for k, c in enumerate(option["choices"], 1)}
            for option in overlays:
                category = ids.get("%d_%d:%s" % (entry["race"], int(sex), option["name"]))
                if not category or option.get("style"):
                    continue
                slot += 1
                depends = option.get("depends")
                if depends:
                    style = ids.get("%d_%d:%s" % (entry["race"], int(sex), depends[0]))
                    lines.append("P\t%d\t%d\t%d\t%d\t%d\t%s" % (entry["race"], int(sex), slot, category, style or 0, names.shell(model)))
                else:
                    lines.append("S\t%d\t%d\t%d\t%d\t%s" % (entry["race"], int(sex), slot, category, names.shell(model)))
                for k, choice in enumerate(option["choices"], 1):
                    for colour, fid in sorted(choice["files"].items()):
                        if colour.startswith("r"):
                            hit = [number[d][colour[1:]] for d in (depends or []) if d in number and colour[1:] in number[d]]
                            if not hit:
                                continue
                            colour = "s%d" % hit[0]
                        lines.append("C\t%d\t%d\t%d\t%d\t%s\t%s" % (entry["race"], int(sex), category, k, colour, names.overlay(model, fid)))
    path = os.path.join(out_dir, "Wrathpp", "parts.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Wrath++'s parts (sl_parts.py): S/P race sex slot category [style category] shell; C race sex category option colour picture\n")
        f.write("".join(line + "\n" for line in lines))
    return path

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


def lift_vertices(m2b):
    """The model with every vertex out along its normal by LIFT."""
    m = bytearray(m2b)
    n, o = array(m, VERTICES)
    for i in range(n):
        at = o + i * 48
        p = np.array(struct.unpack_from("<3f", m, at), np.float64)
        nrm = np.array(struct.unpack_from("<3f", m, at + 20), np.float64)
        struct.pack_into("<3f", m, at, *(p + nrm * LIFT))
    return bytes(m)


def patch_shell(m2b, head=True):
    """The converted head model made a shell: vertices out along their normals, texture coordinates the picture's, the
    texture replaceable type 11 and the materials alpha blended."""
    m = bytearray(m2b)
    n, o = array(m, VERTICES)
    for i in range(n):
        at = o + i * 48
        p = np.array(struct.unpack_from("<3f", m, at), np.float64)
        nrm = np.array(struct.unpack_from("<3f", m, at + 20), np.float64)
        struct.pack_into("<3f", m, at, *(p + nrm * LIFT))
        if head:
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


BODY_GEOSETS = (0, 401, 501)       # the bare body, hands and feet: the geosets drawn with the skin's own texture


def body_shell(read, model, out_dir, log=print):
    """Writes the model's body shell ("<Model>Body") into [out_dir]: the bare body's geosets (the base, the hands, the feet) lifted
    0.4 mm, their texture the replaceable type 11 laid over the skin, alpha blended. Its coordinates are the skin's own (the
    picture is the whole 512 x 512 skin's). The files written."""
    import m2
    import check_m2
    present = [g for g in BODY_GEOSETS if str(g) in model["geoset_policy"] or g // 100 not in (0,) or g == 0]
    part = dict(model, name=model["name"] + "Body", geosets=None, stand_only=True,
                geoset_policy={str(g): [1 + i] for i, g in enumerate(present)}, drop_groups=list(range(0, 100)))
    written = m2.convert(read, part, out_dir, lambda *a: None)
    path = os.path.join(out_dir, model["folder"].replace("\\", "/"), part["name"] + ".m2")
    with open(path, "rb") as f:
        shell = patch_shell(f.read(), head=False)
    with open(path, "wb") as f:
        f.write(shell)
    problems = [x for x in check_m2.check(path) if "type %d" % SHELL_TEXTURE not in x]
    if problems:
        raise ValueError("%s: %s" % (part["name"], "; ".join(problems[:10])))
    log("%s: body shell" % part["name"])
    return written


TYPE_SLOTS = {1: 11, 8: 11, 6: 12, 10: 13, 20: 13}     # today's texture type of a part's batch -> the replaceable type wxl.m2 puts a picture on


def patch_part_textures(m2b):
    """A model piece's textures made the replaceable types a mod's model takes (TYPE_SLOTS): the skin's 11, the hair's 12, a
    customization's 13; the fixed textures (type 0) stay. Returns (the model, the set of the types it has)."""
    m = bytearray(m2b)
    n, o = array(m, TEXTURES)
    wanted = {}
    for i in range(n):
        t = struct.unpack_from("<I", m, o + i * 16)[0]
        if t in TYPE_SLOTS:
            struct.pack_into("<I", m, o + i * 16, TYPE_SLOTS[t])
            wanted.setdefault(TYPE_SLOTS[t], i)
    rn, ro = array(m, REPLACEABLE)
    table = list(struct.unpack_from("<%dh" % rn, m, ro))
    for slot, index in wanted.items():
        if len(table) <= slot:
            table += [-1] * (slot + 1 - len(table))             # (a model with a short table: it grows, at the file's end)
        table[slot] = index
    if wanted:
        if len(table) != rn:
            while len(m) % 16:
                m.append(0)
            at = len(m)
            m += struct.pack("<%dh" % len(table), *table)
            struct.pack_into("<II", m, REPLACEABLE, len(table), at)
        else:
            struct.pack_into("<%dh" % rn, m, ro, *table)
    return bytes(m), set(wanted)


def used_types(m2b, skin_bytes):
    """The texture types (today's, before TYPE_SLOTS or after) the batches of a model and its skin draw with."""
    tc, to = array(m2b, TEXTURES)
    types = [struct.unpack_from("<I", m2b, to + i * 16)[0] for i in range(tc)]
    lc, lo = array(m2b, 128)
    look = struct.unpack_from("<%dh" % lc, m2b, lo)
    bn, bo = struct.unpack_from("<II", skin_bytes, 36)
    used = set()
    for i in range(bn):
        first, count = struct.unpack_from("<HH", skin_bytes, bo + i * 24 + 16)[0], struct.unpack_from("<H", skin_bytes, bo + i * 24 + 14)[0]
        for k in range(max(count, 1)):
            if first + k < len(look) and 0 <= look[first + k] < len(types):
                used.add(types[look[first + k]])
    return used


HELM = 11


def helm_point(read, model):
    """Where the character's head attachment point (the helm's, 11) is in its bind pose: [x, y, z] in the model's own coordinates."""
    import m2
    data = read(model["model"])
    chunks = m2.chunks_of(data)
    child = m2.Skeleton(read(struct.unpack_from("<I", chunks["SKID"])[0])) if "SKID" in chunks else m2.OwnSkeleton(data)
    for head, _track in child.attachments:
        if struct.unpack_from("<I", head, 0)[0] == HELM:
            return struct.unpack_from("<3f", head, 8)
    raise ValueError("%s has no attachment point %d" % (model["name"], HELM))


def move_to_origin(m2b, point):
    """The model with every vertex moved by minus [point], and its bounds with them."""
    m = bytearray(m2b)
    n, o = array(m, VERTICES)
    lo = np.full(3, np.inf)
    hi = np.full(3, -np.inf)
    for i in range(n):
        at = o + i * 48
        p = np.array(struct.unpack_from("<3f", m, at), np.float64) - np.array(point, np.float64)
        struct.pack_into("<3f", m, at, *p)
        lo, hi = np.minimum(lo, p), np.maximum(hi, p)
    if n:
        struct.pack_into("<6f", m, 160, *lo, *hi)
        struct.pack_into("<f", m, 184, float(np.linalg.norm(np.maximum(abs(lo), abs(hi)))))
    return bytes(m)


def variant_model_name(model, k):
    return "%sV%d" % (model["name"], k)


def variant_model_path(model, k):
    return "%s\\%s.m2" % (model["folder"], variant_model_name(model, k))


def variant_model(read, model, variant, k, choice, out_dir, log=print):
    """Writes the character's model as the choice [k] of [variant] has it (the Orc man's Upright: another model of the game's, its own
    skin, bones and sequences; the textures, hair and features are the character's: the game composes them by race and sex) as
    "<Model>V<k>.m2" into [out_dir]. The files written."""
    import m2
    import check_m2
    name = variant_model_name(model, k)
    spec = dict(model, name=name, geosets=None)
    if choice["file"]:
        spec["model"] = choice["file"]
    else:
        # geosets of the model itself: this choice's on (as the policy has them), the variant's others off
        policy = {k_: list(v) for k_, v in model["geoset_policy"].items()}
        every = {g for c in variant["choices"] for g in c.get("geosets", [])}
        for g in every:
            policy[str(g)] = list(model["geoset_policy"].get(str(g), [g])) if g in choice.get("geosets", []) else []
        spec["geoset_policy"] = policy
    written = m2.convert(read, spec, out_dir, lambda *a: None)
    path = os.path.join(out_dir, model["folder"].replace("\\", "/"), name + ".m2")
    layout = path[:-3] + ".layout.json"
    if os.path.exists(layout):
        os.remove(layout)
    problems = check_m2.check(path)
    if problems:
        raise ValueError("%s: %s" % (name, "; ".join(problems[:10])))
    log("%s: the model of choice %d of %s" % (name, k, variant["name"]))
    return [w for w in written if not w.endswith(".layout.json")]


def soft_body(m2_path):
    """Where a woman's soft body (the native mod's springs, wxl.m2's bone watcher) hangs on a converted model: {"count": bones,
    "parent": the bone they hang on, "bones": [[bone, pivot x, y, z, [the bones below it]], ...]}, or None for a model without a pair
    of breast bones (the men's). The breast bones are the two with no key id, the same parent and mirrored pivots, forward of the
    spine (x over 0.04), 0.04 to 0.14 to each side and at the chest's height (0.6 to 0.8 of the model's, its head's bone at the top):
    the retail skeletons' L_Breast and R_Breast, which the converter keeps without a key id."""
    with open(m2_path, "rb") as f:
        m = f.read()
    n, o = struct.unpack_from("<II", m, 44)
    rows = []
    for i in range(n):
        key, flags, parent, sub, unk = struct.unpack_from("<iIhHI", m, o + i * 88)
        rows.append((key, parent, struct.unpack_from("<3f", m, o + i * 88 + 76)))
    top = max((r[2][2] for r in rows if r[0] == 22), default=0.0)       # key 22: the breath bone, at the head's top
    if top <= 0:
        return None
    best = None
    for i, a in enumerate(rows):
        for j in range(i + 1, n):
            c = rows[j]
            if a[0] != -1 or c[0] != -1 or a[1] != c[1] or a[1] < 0:
                continue
            (ax, ay, az), (cx, cy, cz) = a[2], c[2]
            if (abs(ax - cx) < 0.01 and abs(ay + cy) < 0.01 and abs(az - cz) < 0.01 and ax > 0.04 and 0.04 < abs(ay) < 0.14
                    and 0.6 * top < az < 0.8 * top):
                if best is None or abs(ay) < best[0]:
                    best = (abs(ay), i, j)
    if best is None:
        return None

    def below(b):
        out, grew = set(), True
        while grew:
            grew = False
            for i, r in enumerate(rows):
                if i not in out and (r[1] == b or r[1] in out):
                    out.add(i)
                    grew = True
        return sorted(out)

    _, i, j = best
    return {"count": n, "parent": rows[i][1], "bones": [[b, *[round(x, 5) for x in rows[b][2]], below(b)] for b in (i, j)]}


def part_model_name(model, part):
    import re
    return model["name"] + "P" + re.sub(r"[^A-Za-z0-9]", "", part["name"])


def geoset_part(read, model, part, out_dir, log=print):
    """Writes the model piece of [part] (looks' parts_of: an option's choices and their geosets) into [out_dir]: one model with every
    choice's geosets, the choice number k's under the ids k * 100 + 1 and up (wxl.m2's SetGeosets shows the chosen one's), its
    textures the replaceable types of TYPE_SLOTS. Returns (the files written, the replaceable types it takes)."""
    import m2
    import check_m2
    policy = {}
    for k, choice in enumerate(part["choices"], 1):
        for j, g in enumerate(choice["geosets"]):
            policy.setdefault(str(g), []).append(k * 100 + j + 1)
    if not policy:
        return [], set()
    name = part_model_name(model, part)
    spec = dict(model, name=name, geosets=None, stand_only=True, geoset_policy=policy, drop_groups=list(range(0, 100)), keep_types=[8, 10, 20])
    if part.get("skinned"):
        spec["model"] = part["skinned"]                 # a collection's model (today's horns, blindfolds), in the character's bind pose
    written = m2.convert(read, spec, out_dir, lambda *a: None)
    path = os.path.join(out_dir, model["folder"].replace("\\", "/"), name + ".m2")
    with open(path, "rb") as f:
        raw = f.read()
    if part.get("skinned"):
        # Hung on the head's attachment point (the helm's, 11), not on the bones: the model's own bones aren't the character's. Its
        # vertices move so that the point is their origin.
        raw = move_to_origin(raw, helm_point(read, model))
        with open(path, "wb") as f:
            f.write(raw)
    with open(path[:-3] + "00.skin", "rb") as f:
        used = used_types(raw, f.read())
    if part.get("feature"):
        raw = lift_vertices(raw)                        # over the model's own copy of it (the same geosets): 0.4 mm out, so that it shows
    patched, _ = patch_part_textures(raw)
    types = {TYPE_SLOTS[t] for t in used if t in TYPE_SLOTS}
    with open(path, "wb") as f:
        f.write(patched)
    problems = [x for x in check_m2.check(path) if not any("type %d" % t in x for t in (11, 12, 13))]
    if problems:
        raise ValueError("%s: %s" % (name, "; ".join(problems[:10])))
    log("%s: part of %d choices, textures %s" % (name, len(part["choices"]), sorted(types) or "fixed"))
    return written, types


def write_pickers(read, model, out_dir, log=print):
    """Copies the textures the model's pickers name (a jewellery's, a vine's colour) into [out_dir] as the files the game reads (today's
    own, BLP): the files written."""
    import names
    written, done = [], set()
    for picker in model.get("pickers", []):
        for choice in picker["choices"]:
            fid = choice["file"]
            if not fid or fid in done:
                continue
            done.add(fid)
            path = names.picker(model, fid)
            full = os.path.join(out_dir, path.replace("\\", "/"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(read(fid))
            written.append(path)
    if written:
        log("%s: %d picker textures" % (model["name"], len(written)))
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


def layer_to_alpha(rgba):
    """A layer opaque everywhere (today's game blends it by a mode of its own) as the alpha blended picture a shell draws."""
    if rgba[:, :, 3].min() != 255:
        return rgba
    grey = rgba[:, :, :3].astype(np.float32).mean(axis=2)
    out = np.zeros(rgba.shape, np.uint8)
    if np.median(grey) > 192:
        out[:, :, 3] = np.clip(255.0 - grey, 0, 255).astype(np.uint8)
    else:
        out[:, :, :3] = np.where(grey[:, :, None] > 127.5, 255, 0).astype(np.uint8)
        out[:, :, 3] = np.clip(np.abs(grey - 127.5) * 2.0, 0, 255).astype(np.uint8)
    return out


def body_picture(rgba):
    """A layer of the body as the body shell draws it: the skin's 512 x 512, the alpha kept. [rgba] is the body's own section
    (512 x 512) or the whole skin's layer (1024 x 512: the body its left half)."""
    import textures
    h, w = rgba.shape[:2]
    if w == 2 * h:
        rgba = np.ascontiguousarray(rgba[:, :w // 2])
    rgba = layer_to_alpha(rgba)
    if rgba.shape[:2] != (512, 512):
        rgba = textures.resized_over(rgba, (512, 512))
    return rgba


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
    done_body = set()
    for option in model.get("overlays", []):
        for choice in option["choices"]:
            for fid in choice.get("body", {}).values():
                path = names.body_overlay(model, fid)
                if fid in done_body:
                    continue
                done_body.add(fid)
                full = os.path.join(out_dir, path.replace("\\", "/"))
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as f:
                    f.write(blp.write_palette(np.ascontiguousarray(body_picture(blp.read(read(fid)))), alpha=True))
                written.append(path)
    if written:
        log("%s: %d overlay pictures" % (model["name"], len(written)))
    return written


def part_model_path(model, part):
    return "%s\\%s.m2" % (model["folder"], part_model_name(model, part))


def sl_parts_model(model, part):
    return "%s\\%s.m2" % (model["folder"], part_model_name(model, part))


def write_parts_table(looks, out_dir, ids):
    """Wrathpp/parts.txt in [out_dir] (the game's patch): what the add-on needs to draw a character's parts from the
    registry's choices, tab separated:

        S race sex slot category shell                            a picture over the head: the option (its registry category)
                                                                  and the shell it is drawn on, in slot `slot` of the character
        P race sex slot category style_category shell             the same for a paint whose picture follows another option's
                                                                  choice (its colour): `category` the colour's, `style_category` the style's
        T / U race sex slot category [style_category] shell       the same for the body shell (a slot of its own); D race sex category option
                                                                  colour picture are its pictures
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
                def colour_of(colour):
                    if colour.startswith("r"):
                        hit = [number[d][colour[1:]] for d in (depends or []) if d in number and colour[1:] in number[d]]
                        return "s%d" % hit[0] if hit else None
                    return colour
                for k, choice in enumerate(option["choices"], 1):
                    for colour, fid in sorted(choice["files"].items()):
                        colour = colour_of(colour)
                        if colour is not None:
                            lines.append("C\t%d\t%d\t%d\t%d\t%s\t%s" % (entry["race"], int(sex), category, k, colour, names.overlay(model, fid)))
                if any(c.get("body") for c in option["choices"]):
                    slot += 1
                    if depends:
                        lines.append("U\t%d\t%d\t%d\t%d\t%d\t%s" % (entry["race"], int(sex), slot, category, style or 0, names.body_shell(model)))
                    else:
                        lines.append("T\t%d\t%d\t%d\t%d\t%s" % (entry["race"], int(sex), slot, category, names.body_shell(model)))
                    for k, choice in enumerate(option["choices"], 1):
                        for colour, fid in sorted(choice.get("body", {}).items()):
                            colour = colour_of(colour)
                            if colour is not None:
                                lines.append("D\t%d\t%d\t%d\t%d\t%s\t%s" % (entry["race"], int(sex), category, k, colour, names.body_overlay(model, fid)))
        # the model pieces (geosets: ears, headdresses, vines, tails...): a slot of their own each, the textures they take by type
        for sex, model in sorted(entry["models"].items()):
            parts = model.get("parts", [])
            if not parts:
                continue
            race = entry["race"]
            slot = sum(1 for l in lines if l.split("\t")[0] in ("S", "P", "T", "U") and l.split("\t")[1:3] == [str(race), str(int(sex))])
            lines.append("H\t%d\t%d\t%s" % (race, int(sex), names.hair_template(model)))
            for digit, s in enumerate(model["skins"][:model["base_skins"]]):
                lines.append("K\t%d\t%d\t%d\t%s" % (race, int(sex), digit + 1, names.skin(model, s["index"])))
            pickers = {p["type"]: p for p in model.get("pickers", [])}
            for picker in model.get("pickers", []):
                category = ids.get("%d_%d:%s" % (race, int(sex), picker["name"]))
                if not category:
                    continue
                for k, choice in enumerate(picker["choices"], 1):
                    if choice["file"]:
                        lines.append("Z\t%d\t%d\t%d\t%d\t%s" % (race, int(sex), category, k, names.picker(model, choice["file"])))
            for part in parts:
                category = ids.get("%d_%d:%s" % (race, int(sex), part["name"]))
                types = model.get("part_types", {}).get(part["name"], [])
                if not category or not any(c["geosets"] for c in part["choices"]):
                    continue
                slot += 1
                # (a picker of the texture type the part takes: types 13 are the customization's: 10 or 20 today)
                picker = next(iter(pickers.values()), None) if 13 in types else None
                picker_category = ids.get("%d_%d:%s" % (race, int(sex), picker["name"])) if picker else 0
                lines.append("G\t%d\t%d\t%d\t%d\t%s\t%s\t%d" % (race, int(sex), slot, category, sl_parts_model(model, part), ",".join(str(t) for t in types), picker_category or 0) + ("\t%d" % HELM if part.get("skinned") else "\t0"))
    for entry in sorted(looks["races"].values(), key=lambda e: e["race"]):
        for sex, model in sorted(entry["models"].items()):
            soft = model.get("soft")
            if soft:
                # a woman's breast bones (the native mod's soft body): B race sex bone count, the bone they hang on, then each: bone, pivot, the bones below
                lines.append("\t".join(["B", str(entry["race"]), str(int(sex)), str(soft["count"]), str(soft["parent"])] +
                                        sum(([str(b[0]), "%.5f" % b[1], "%.5f" % b[2], "%.5f" % b[3], ",".join(str(x) for x in b[4])] for b in soft["bones"]), [])))
            for variant in model.get("variants", []):
                category = ids.get("%d_%d:%s" % (entry["race"], int(sex), variant["name"]))
                if not category:
                    continue
                for k, choice in enumerate(variant["choices"], 1):
                    if (choice["file"] or choice.get("geosets")) and not (k == 1 and variant.get("geoset")):
                        lines.append("V\t%d\t%d\t%d\t%d\t%s" % (entry["race"], int(sex), category, k, variant_model_path(model, k)))
    path = os.path.join(out_dir, "Wrathpp", "parts.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Wrath++'s parts (sl_parts.py): S/P race sex slot category [style category] shell; C race sex category option colour picture\n")
        f.write("".join(line + "\n" for line in lines))
    return path

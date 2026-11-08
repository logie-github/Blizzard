#!/usr/bin/env python3
"""Eternus's own shape: her dragon as Blizzard's game has it (display 106055, the bronze-and-infinite
dragon of Thaldraszus and both Remixes: model file 4500511), made a model the 3.3.5 game draws.

    python3 tools/models.py fetch DIR          fetches her files from wago.tools by their ids and writes
                                               the 3.3.5 model into DIR (Creature/Eternus/...)
    python3 tools/models.py convert SRC DIR    the same from files already fetched (named by their ids)

Her files are the game's, so they are never in this repository: the server package fetches and
converts them (scripts/package-azerothcore.sh) into the module's data/models, where the world server
finds them (ClientPatch.cpp puts them in the game's patch with their CreatureModelData and
CreatureDisplayInfo rows; RemixModels.cpp gives Eternus the shape once they're there). Without them
she keeps the infinite dragonspawn's.

What changes from the game's (format 274) to 3.3.5's (264): the chunked wrapper goes (the model is
the MD20 inside it), its textures get names in place of file ids, its mesh sections are split so
none has more than 64 bones (3.3.5 draws a section with at most that many), each drawn with her
skin alone (the newer shaders don't exist in 3.3.5), only the geosets her display shows are kept,
her cameras are written in 3.3.5's layout, her particles (a newer layout) are left out, her
animations with newer ids (aliases of older ones) take ids 3.3.5 has that a creature never plays,
the animation lookup is a table by id, and her
animations kept in their own files are written as 3.3.5 .anim files (the same data without its
chunk header). Everything else (vertices, bones, animation tracks, attachments, events) is the
same in both.
"""
import os
import struct
import sys
import time
import urllib.request

USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"   # (wago.tools turns away Python's own)

MODEL = 4500511                     # creature/<her dragon>.m2 (CreatureModelData 13291)
SKIN_TEXTURE = 4500601              # her display's skin (both of its texture variations)
SHOWN_GEOSETS = {0, 101, 202, 402}  # her display's geosets (CreatureDisplayInfoGeosetData of 106055)
NAME = "Eternus"
FOLDER = "Creature/Eternus"
MANIFEST = "eternus.files"
MAX_BONES = 64

# the 3.3.5 header: name, then each array's place (count, offset)
H_NAME, H_FLAGS, H_SEQS, H_SEQ_LOOKUP, H_BONES, H_VERTS, H_VIEWS = 8, 16, 28, 36, 44, 60, 68
H_TEXTURES, H_TEX_TRANSFORMS, H_BONE_LOOKUP, H_TEX_LOOKUP, H_TEX_UNIT_LOOKUP = 80, 96, 120, 128, 136
H_TRANSFORM_LOOKUP = 152
H_LIGHTS, H_CAMERAS, H_RIBBONS, H_PARTICLES = 264, 272, 288, 296
TEXTURE_SKIN = 11                   # a creature's first replaceable texture
LAST_ANIMATION = 505                # 3.3.5's AnimationData ends here
# The newer animations (in her model all aliases of older ones, with no data of their own) given
# ids 3.3.5 has that no creature is ever asked to play: jousting, the stocks, a two-handed carry.
SPARE_ANIMATIONS = [476, 477, 478, 479, 480, 481, 482, 483, 490, 491, 502, 503, 504, 505]


def chunks_of(data):
    out = {}
    at = 0
    while at + 8 <= len(data):
        cid = data[at:at + 4].decode("latin1")
        size = struct.unpack_from("<I", data, at + 4)[0]
        out[cid] = data[at + 8:at + 8 + size]
        at += 8 + size
    return out


class Blob:
    """The model's data, growing at its end (3.3.5's offsets are from its start, as the game's)."""

    def __init__(self, data):
        self.data = bytearray(data)

    def array(self, at):
        return struct.unpack_from("<II", self.data, at)

    def set_array(self, at, count, offset):
        struct.pack_into("<II", self.data, at, count, offset)

    def append(self, payload):
        while len(self.data) % 16:
            self.data.append(0)
        offset = len(self.data)
        self.data += payload
        return offset


def fix_sequences(blob):
    """Her sequences with ids 3.3.5 has, and their lookup as a table by id (an id's first
    sequence at its own place, which reads the same whether the game indexes it or hashes it).
    Returns the ids given in place of the newer ones."""
    count, offset = blob.array(H_SEQS)
    ids = [struct.unpack_from("<H", blob.data, offset + i * 64)[0] for i in range(count)]
    spare = [a for a in SPARE_ANIMATIONS if a not in ids]
    renamed = {}
    for i, sid in enumerate(ids):
        if sid > LAST_ANIMATION:
            if sid not in renamed:
                if not spare:
                    raise ValueError("no spare animation id for %d" % sid)
                renamed[sid] = spare.pop(0)
            ids[i] = renamed[sid]
            struct.pack_into("<H", blob.data, offset + i * 64, ids[i])
    table = [-1] * (max(ids) + 1)
    for i, sid in enumerate(ids):
        if table[sid] < 0:
            table[sid] = i
    blob.set_array(H_SEQ_LOOKUP, len(table), blob.append(struct.pack("<%dh" % len(table), *table)))
    return renamed


def texture_name(index):
    return "%s\\%s%d.blp" % (FOLDER.replace("/", "\\"), NAME, index)


def convert_model(m2, skin):
    """The 3.3.5 model and skin, the textures each hard-coded texture needs (file id -> name),
    and the external animations' names."""
    chunks = chunks_of(m2)
    md20 = chunks["MD21"]
    if md20[:4] != b"MD20":
        raise ValueError("not a model")
    blob = Blob(md20)
    struct.pack_into("<I", blob.data, 4, 264)
    struct.pack_into("<I", blob.data, H_FLAGS, struct.unpack_from("<I", blob.data, H_FLAGS)[0] & 0x3)
    name = NAME.encode() + b"\0"
    blob.set_array(H_NAME, len(name), blob.append(name))
    renamed = fix_sequences(blob)

    # a texture animation's lookup naming one the model hasn't: none
    transforms = blob.array(H_TEX_TRANSFORMS)[0]
    count, offset = blob.array(H_TRANSFORM_LOOKUP)
    for i in range(count):
        if struct.unpack_from("<h", blob.data, offset + i * 2)[0] >= transforms:
            struct.pack_into("<h", blob.data, offset + i * 2, -1)

    # textures: names for the hard-coded ones (their file ids are in TXID)
    file_ids = struct.unpack("<%dI" % (len(chunks["TXID"]) // 4), chunks["TXID"])
    count, offset = blob.array(H_TEXTURES)
    needed = {}
    skin_texture = None
    for i in range(count):
        kind = struct.unpack_from("<I", blob.data, offset + i * 16)[0]
        if kind == 0 and i < len(file_ids) and file_ids[i]:
            path = texture_name(i).encode() + b"\0"
            struct.pack_into("<II", blob.data, offset + i * 16 + 8, len(path), blob.append(path))
            needed[file_ids[i]] = texture_name(i)
        if kind == TEXTURE_SKIN and skin_texture is None:
            skin_texture = i
    if skin_texture is None:
        raise ValueError("no skin texture")
    lookup_count, lookup_offset = blob.array(H_TEX_LOOKUP)
    lookups = struct.unpack_from("<%dh" % lookup_count, blob.data, lookup_offset)
    skin_combo = lookups.index(skin_texture)

    # every batch takes its coordinates from the first UV set (3.3.5 looks this up; the newer
    # models leave it empty)
    blob.set_array(H_TEX_UNIT_LOOKUP, 1, blob.append(struct.pack("<hh", 0, 0)))

    # nothing 3.3.5 reads differently: particles, ribbons, lights
    for field in (H_PARTICLES, H_RIBBONS, H_LIGHTS):
        blob.set_array(field, 0, 0)

    # cameras: 3.3.5's field of view is a number after the type, where the newer one is a track
    # at the end (its first key's value taken)
    count, offset = blob.array(H_CAMERAS)
    cameras = bytearray()
    for i in range(count):
        at = offset + i * 116
        kind, far, near = struct.unpack_from("<Iff", blob.data, at)
        fov = 0.95
        fov_track = at + 96
        n_seq, seq_at = struct.unpack_from("<II", blob.data, fov_track + 12)
        for s in range(n_seq):
            n_keys, keys_at = struct.unpack_from("<II", blob.data, seq_at + s * 8)
            if n_keys and keys_at + 4 > len(md20):
                break                                   # (a sequence kept in its own .anim)
            if n_keys:
                value = struct.unpack_from("<f", blob.data, keys_at)[0]
                if 0.1 < value < 3.0:
                    fov = value
                break
        cameras += struct.pack("<Ifff", kind, fov, far, near)
        cameras += blob.data[at + 12:at + 96]           # positions, base, targets, base, roll
    if count:
        blob.set_array(H_CAMERAS, count, blob.append(bytes(cameras)))

    new_skin, bone_lookup = convert_skin(skin, blob, skin_combo)
    blob.set_array(H_BONE_LOOKUP, len(bone_lookup), blob.append(struct.pack("<%dH" % len(bone_lookup), *bone_lookup)))
    struct.pack_into("<I", blob.data, H_VIEWS, 1)

    anims = {}
    if "AFID" in chunks:
        raw = chunks["AFID"]
        for i in range(0, len(raw), 8):
            anim, sub, file_id = struct.unpack_from("<HHI", raw, i)
            anim = renamed.get(anim, anim)
            if file_id:
                anims[file_id] = "%s/%s%04d-%02d.anim" % (FOLDER, NAME, anim, sub)
    return bytes(blob.data), new_skin, needed, anims


def convert_skin(skin, blob, skin_combo):
    """3.3.5's skin: the shown sections, split so each has at most MAX_BONES bones, with the new
    bone lookup their palettes make."""
    if skin[:4] != b"SKIN":
        raise ValueError("not a skin")
    sv_n, sv_o = struct.unpack_from("<II", skin, 4)
    ix_n, ix_o = struct.unpack_from("<II", skin, 12)
    pr_n, pr_o = struct.unpack_from("<II", skin, 20)
    se_n, se_o = struct.unpack_from("<II", skin, 28)
    ba_n, ba_o = struct.unpack_from("<II", skin, 36)
    skin_vertices = struct.unpack_from("<%dH" % sv_n, skin, sv_o)
    indices = struct.unpack_from("<%dH" % ix_n, skin, ix_o)
    properties = [skin[pr_o + i * 4:pr_o + i * 4 + 4] for i in range(pr_n)]
    vcount, voff = blob.array(H_VERTS)
    lookup_count, lookup_offset = blob.array(H_BONE_LOOKUP)
    lookup = struct.unpack_from("<%dH" % lookup_count, blob.data, lookup_offset)
    batches = {}
    for i in range(ba_n):
        b = struct.unpack_from("<BbHHHhHHHHHHH", skin, ba_o + i * 24)
        batches.setdefault(b[3], b)

    out_vertices, out_props, out_indices, out_sections, out_batches, out_lookup = [], [], [], [], [], []
    for s in range(se_n):
        sec = struct.unpack_from("<10H7f", skin, se_o + s * 48)
        if sec[0] not in SHOWN_GEOSETS or s not in batches:
            continue
        level, v_start, i_start, i_count, combo = sec[1], sec[2], sec[4], sec[5], sec[7]
        first_index = i_start + level * 65536
        bones_of = {}       # skin vertex -> [(bone, weight)]
        for k in set(indices[first_index:first_index + i_count]):
            g = skin_vertices[k]
            weights = blob.data[voff + g * 48 + 12:voff + g * 48 + 16]
            bones_of[k] = [(lookup[combo + properties[k][j]], weights[j]) for j in range(4) if weights[j]]
        groups = []         # [palette (list of bones), triangles]
        for t in range(first_index, first_index + i_count, 3):
            tri = indices[t:t + 3]
            used = {b for k in tri for b, _ in bones_of[k]}
            if not groups or len(set(groups[-1][0]) | used) > MAX_BONES:
                groups.append([[], []])
            palette = groups[-1][0]
            for b in sorted(used):
                if b not in palette:
                    palette.append(b)
            groups[-1][1].append(tri)
        for palette, triangles in groups:
            place = {}
            vertex_start, index_start = len(out_vertices), len(out_indices)
            influences = 0
            for tri in triangles:
                for k in tri:
                    if k not in place:
                        place[k] = len(out_vertices)
                        out_vertices.append(skin_vertices[k])
                        prop = [0, 0, 0, 0]
                        bones = bones_of[k]
                        influences = max(influences, len(bones))
                        for j, (b, _) in enumerate(bones):
                            prop[j] = palette.index(b)
                        # (the weights keep their slots: the vertex's own, in the model)
                        weights = blob.data[voff + skin_vertices[k] * 48 + 12:voff + skin_vertices[k] * 48 + 16]
                        slot = [0, 0, 0, 0]
                        n = 0
                        for j in range(4):
                            if weights[j]:
                                slot[j] = prop[n]
                                n += 1
                        out_props.append(bytes(slot))
                    out_indices.append(place[k])
            combo_index = len(out_lookup)
            out_lookup.extend(palette)
            out_sections.append(struct.pack("<10H7f", 0, (index_start >> 16), vertex_start & 0xFFFF, len(place),
                                            index_start & 0xFFFF, len(triangles) * 3, len(palette), combo_index,
                                            max(1, influences), sec[9], *sec[10:17]))
            b = batches[s]
            # flags 16 (as 3.3.5's own), shader 0 with one texture: her skin
            out_batches.append(struct.pack("<BbHHHhHHHHHHH", 16, 0, 0, len(out_sections) - 1, len(out_sections) - 1,
                                           -1, b[6], 0, 1, skin_combo, 0, b[11], b[12]))
    if len(out_vertices) > 65535:
        raise ValueError("too many vertices for one skin")
    if max(out_lookup, default=0) >= struct.unpack_from("<I", blob.data, H_BONES)[0]:
        raise ValueError("a bone that isn't there")

    header = 48
    body = bytearray()

    def place(payload):
        while (header + len(body)) % 16:
            body.append(0)
        at = header + len(body)
        body.extend(payload)
        return at

    parts = [
        (len(out_vertices), place(struct.pack("<%dH" % len(out_vertices), *out_vertices))),
        (len(out_indices), place(struct.pack("<%dH" % len(out_indices), *out_indices))),
        (len(out_props), place(b"".join(out_props))),
        (len(out_sections), place(b"".join(out_sections))),
        (len(out_batches), place(b"".join(out_batches))),
    ]
    head = bytearray(b"SKIN")
    for count, offset in parts:
        head += struct.pack("<II", count, offset)
    head += struct.pack("<I", MAX_BONES)
    return bytes(head) + bytes(body), out_lookup


def anim_payload(data):
    """A newer .anim's data: what its AFM2 chunk holds, as 3.3.5's .anim files are."""
    chunks = chunks_of(data)
    if "AFM2" in chunks:
        return chunks["AFM2"]
    return data


def convert(fetch_file, folder):
    """Writes her model into [folder]; [fetch_file] gives a file's bytes by its id."""
    m2 = fetch_file(MODEL)
    chunks = chunks_of(m2)
    sfid = struct.unpack("<%dI" % (len(chunks["SFID"]) // 4), chunks["SFID"])
    model, skin, textures, anims = convert_model(m2, fetch_file(sfid[0]))
    files = {
        "%s/%s.m2" % (FOLDER, NAME): model,
        "%s/%s00.skin" % (FOLDER, NAME): skin,
        "%s/%sSkin.blp" % (FOLDER, NAME): fetch_file(SKIN_TEXTURE),
    }
    for file_id, name in textures.items():
        files[name.replace("\\", "/")] = fetch_file(file_id)
    for file_id, name in anims.items():
        files[name] = anim_payload(fetch_file(file_id))
    for name, data in files.items():
        if name.endswith(".blp") and data[:4] != b"BLP2":
            raise ValueError("%s isn't a BLP2 texture" % name)
    for name, data in files.items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as out:
            out.write(data)
    # the list of her files, written last: the world server takes her shape only when it's there
    # and every file it names is (ClientPatch.cpp, RemixModels.cpp)
    with open(os.path.join(folder, MANIFEST), "w") as out:
        out.write("".join(name + "\n" for name in sorted(files)))
    print("models: Eternus's dragon, %d files in %s" % (len(files), folder))


def wago(file_id):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://wago.tools/api/casc/%d?download" % file_id,
                                        headers={"User-Agent": USER_AGENT}), timeout=60) as response:
                return response.read()
        except Exception as error:  # a network hiccup: once more, a little later
            print("models: file %d: %s" % (file_id, error), file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("file %d couldn't be fetched" % file_id)


def local(source):
    def read(file_id):
        for name in (str(file_id), "%d.m2" % file_id):
            path = os.path.join(source, name)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read()
        raise FileNotFoundError(file_id)
    return read


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "fetch":
        convert(wago, sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "convert":
        convert(local(sys.argv[2]), sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)

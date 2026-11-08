#!/usr/bin/env python3
"""Checks a 3.3.5 model (format 264) and its skin the way the game would trip over them: every
array inside the file, every track with an entry a sequence (or one for a global sequence, or
none), every section with at most 64 bones and every bone it names in the model, every index in
the skin's vertices, every sequence kept outside the file having its file, every track's entry for
such a sequence within that file, a global sequence's track's times within its loop, every bone's translations and scales real floats within 100
yards (what tools/m2.py keeps).

    python3 tools/check_m2.py DIR/Character/Race/Sex/Name.m2 [--verbose]
"""
import math
import os
import struct
import sys

FAR = 100.0                          # tools/m2.py leaves out translations and scales beyond this


def check(path, verbose=False):
    m = open(path, "rb").read()
    problems = []
    say = problems.append
    if m[:4] != b"MD20" or struct.unpack_from("<I", m, 4)[0] != 264:
        say("not a 3.3.5 model")
        return problems

    def arr(at, size=1):
        count, offset = struct.unpack_from("<II", m, at)
        if count and (offset < 304 or offset + count * size > len(m)):
            say("array at %d (%d x %d at %d) is outside the file" % (at, count, size, offset))
        return count, offset

    n_loops, loops_at = arr(20, 4)
    n_seqs, seqs_at = arr(28, 64)
    n_lookup, lookup_at = arr(36, 2)
    n_bones, bones_at = arr(44, 88)
    n_keys, _ = arr(52, 2)
    n_verts, verts_at = arr(60, 48)
    views = struct.unpack_from("<I", m, 68)[0]
    n_colors, colors_at = arr(72, 40)
    n_tex, tex_at = arr(80, 16)
    n_weights, weights_at = arr(88, 20)
    n_transforms, transforms_at = arr(96, 60)
    n_repl, _ = arr(104, 2)
    n_mats, _ = arr(112, 4)
    n_bone_lookup, bone_lookup_at = arr(120, 2)
    n_tex_lookup, tex_lookup_at = arr(128, 2)
    n_unit, _ = arr(136, 2)
    n_transp, transp_at = arr(144, 2)
    n_tf_lookup, tf_lookup_at = arr(152, 2)
    n_ctris, _ = arr(216, 2)
    n_cverts, _ = arr(224, 12)
    n_cnorms, _ = arr(232, 12)
    n_attach, attach_at = arr(240, 40)
    n_attach_lookup, _ = arr(248, 2)
    n_events, events_at = arr(256, 36)
    n_lights, _ = arr(264, 156)
    n_cams, cams_at = arr(272, 100)
    n_cam_lookup, _ = arr(280, 2)
    n_ribbons, _ = arr(288, 176)
    n_particles, _ = arr(296, 492)
    loops = struct.unpack_from("<%dI" % n_loops, m, loops_at) if n_loops and loops_at + n_loops * 4 <= len(m) else ()
    name_n, name_at = arr(8, 1)
    name = m[name_at:name_at + name_n - 1].decode("latin1")
    seqs = [struct.unpack_from("<HHIfIHHIIIfffffffHH", m, seqs_at + i * 64) for i in range(n_seqs)]
    in_file = [bool(s[4] & 0x20) for s in seqs]
    # the sequences kept outside the file: their own files (.anim), which their tracks' entries point into
    folder = os.path.dirname(path)
    anims, missing = {}, 0
    for i, sq in enumerate(seqs):
        if not in_file[i]:
            anim = os.path.join(folder, "%s%04d-%02d.anim" % (name, sq[0], sq[1]))
            if os.path.exists(anim):
                with open(anim, "rb") as f:
                    anims[i] = f.read()
            else:
                missing += 1
    if missing:
        say("%d sequences kept outside the file have no .anim file" % missing)
    lookup = struct.unpack_from("<%dh" % n_lookup, m, lookup_at)
    for idx in lookup:
        if idx >= n_seqs:
            say("sequence lookup names sequence %d of %d" % (idx, n_seqs))
    # the lookup as the game reads it: a hash table probed from id % size to an empty slot
    for sid in sorted(set(s[0] for s in seqs)):
        i = sid % n_lookup
        steps = 0
        while lookup[i] >= 0 and seqs[lookup[i]][0] != sid and steps < n_lookup:
            i = (i + 1) % n_lookup
            steps += 1
        if lookup[i] < 0 or steps >= n_lookup:
            say("sequence id %d isn't found through the lookup" % sid)
    if -1 not in lookup:
        say("the sequence lookup has no empty slot: a probe for a missing id never ends")
    for i, s in enumerate(seqs):
        for field in (s[-2], s[-1]):
            if field != 0xFFFF and field >= n_seqs:
                say("sequence %d links to sequence %d of %d" % (i, field, n_seqs))

    def track(at, value_size, what, base_only=False, floats=False):
        interp, gseq, tc, to = struct.unpack_from("<hhII", m, at)
        if gseq >= n_loops:
            say("%s: global sequence %d of %d" % (what, gseq, n_loops))
        expect = (1,) if gseq >= 0 else (n_seqs,)
        if tc not in expect and tc != 0:
            say("%s: %d timestamp entries, not %s" % (what, tc, expect))
        if tc and (to + tc * 8 > len(m)):
            say("%s: timestamps outside the file" % what)
        entries = [struct.unpack_from("<II", m, to + k * 8) for k in range(tc)] if tc else []
        vc = vo = 0
        if not base_only:
            vc, vo = struct.unpack_from("<II", m, at + 12)
            if vc != tc:
                say("%s: %d value entries for %d timestamp entries" % (what, vc, tc))
        ventries = [struct.unpack_from("<II", m, vo + k * 8) for k in range(vc)] if vc else []
        for k, (count, offset) in enumerate(entries):
            seq = k if gseq < 0 else None
            external = seq is not None and seq < n_seqs and not in_file[seq]
            if external and seq not in anims:
                continue                            # (no file: said above)
            data, where = (anims[seq], "its .anim file") if external else (m, "the file")
            if count and offset + count * 4 > len(data):
                say("%s: sequence %d's timestamps outside %s" % (what, k, where))
            elif count and gseq >= 0 and gseq < len(loops):
                times = struct.unpack_from("<%dI" % count, data, offset)
                if any(t > loops[gseq] + 1 for t in times) or any(a > b for a, b in zip(times, times[1:])):
                    say("%s: its global sequence's times aren't within the loop (%d ms)" % (what, loops[gseq]))
            if k < len(ventries):
                vcount, voffset = ventries[k]
                if vcount != count:
                    say("%s: sequence %d has %d timestamps and %d values" % (what, k, count, vcount))
                if vcount and voffset + vcount * value_size > len(data):
                    say("%s: sequence %d's values outside %s" % (what, k, where))
                elif vcount and floats:
                    values = struct.unpack_from("<%df" % (vcount * value_size // 4), data, voffset)
                    if not all(math.isfinite(v) and abs(v) <= FAR for v in values):
                        say("%s: sequence %d's values aren't real floats within %d yards" % (what, k, FAR))

    for b in range(n_bones):
        at = bones_at + b * 88
        key, flags, parent = struct.unpack_from("<iIh", m, at)
        if parent >= n_bones or parent < -1:
            say("bone %d: parent %d" % (b, parent))
        for k, (off, size) in enumerate(((16, 12), (36, 8), (56, 12))):
            track(at + off, size, "bone %d track %d" % (b, k), floats=k != 1)
    for i in range(n_weights):
        track(weights_at + i * 20, 2, "texture weight %d" % i)
    for i in range(n_transforms):
        for k, (off, size) in enumerate(((0, 12), (20, 16), (40, 12))):
            track(transforms_at + i * 60 + off, size, "texture transform %d track %d" % (i, k))
    for i in range(n_attach):
        bone = struct.unpack_from("<H", m, attach_at + i * 40 + 4)[0]
        if bone >= n_bones:
            say("attachment %d: bone %d of %d" % (i, bone, n_bones))
        track(attach_at + i * 40 + 20, 1, "attachment %d" % i)
    for i in range(n_events):
        track(events_at + i * 36 + 24, 4, "event %d" % i, base_only=True)
    for i in range(n_cams):
        at = cams_at + i * 100
        fov = struct.unpack_from("<f", m, at + 4)[0]
        if not 0.05 < fov < 3.2:
            say("camera %d: field of view %f" % (i, fov))
        track(at + 16, 36, "camera %d positions" % i)
        track(at + 48, 36, "camera %d targets" % i)
        track(at + 80, 12, "camera %d roll" % i)
    textures = [struct.unpack_from("<IIII", m, tex_at + i * 16) for i in range(n_tex)]
    for i, (kind, flags, nl, no) in enumerate(textures):
        if kind == 0 and nl < 2:
            say("texture %d: a fixed texture without a name" % i)
        if kind not in (0, 1, 2, 6, 8):
            say("texture %d: type %d, which 3.3.5 doesn't know for a character" % (i, kind))
    tex_lookup = struct.unpack_from("<%dh" % n_tex_lookup, m, tex_lookup_at)
    for i, t in enumerate(tex_lookup):
        if t >= n_tex:
            say("texture lookup %d names texture %d of %d" % (i, t, n_tex))
    bone_lookup = struct.unpack_from("<%dH" % n_bone_lookup, m, bone_lookup_at)
    for i, b in enumerate(bone_lookup):
        if b >= n_bones:
            say("bone lookup %d names bone %d of %d" % (i, b, n_bones))
    tf_lookup = struct.unpack_from("<%dh" % n_tf_lookup, m, tf_lookup_at)
    for i, t in enumerate(tf_lookup):
        if t >= n_transforms:
            say("texture transform lookup %d names transform %d of %d" % (i, t, n_transforms))
    if n_lights or n_ribbons or n_particles:
        say("lights, ribbons or particles are in the model")

    # The skin.
    skin_path = os.path.join(folder, name + "00.skin")
    if not os.path.exists(skin_path):
        say("no skin " + skin_path)
        return problems
    s = open(skin_path, "rb").read()
    vn, vo, ixn, ixo, pn, po, sn, so, bn, bo, max_bones = struct.unpack_from("<11I", s, 4)
    if max_bones > 64:
        say("skin: %d bones a section" % max_bones)
    vertices = struct.unpack_from("<%dH" % vn, s, vo)
    indices = struct.unpack_from("<%dH" % ixn, s, ixo)
    if vn != pn:
        say("skin: %d vertices, %d bone property entries" % (vn, pn))
    for v in vertices:
        if v >= n_verts:
            say("skin: vertex %d of the model's %d" % (v, n_verts))
            break
    sections = [struct.unpack_from("<10H7f", s, so + i * 48) for i in range(sn)]
    for i, sec in enumerate(sections):
        level, vstart, vcount, istart, icount, bcount, bcombo, binfl = sec[1:9]
        first = istart + level * 65536
        if first + icount > ixn:
            say("section %d (geoset %d): indices beyond the skin's" % (i, sec[0]))
        if level or istart + icount > 65535:
            say("section %d (geoset %d): triangles start at %d: the game reads 16-bit starts, every section within 65535 indices" % (i, sec[0], first))
        if bcount > 64:
            say("section %d (geoset %d): %d bones" % (i, sec[0], bcount))
        if bcombo + bcount > n_bone_lookup:
            say("section %d (geoset %d): bone combo beyond the lookup" % (i, sec[0]))
        for k in indices[first:first + icount]:
            if not vstart <= k < vstart + vcount:
                say("section %d (geoset %d): index %d outside its vertices %d..%d" % (i, sec[0], k, vstart, vstart + vcount))
                break
        # Each vertex's bone slots name bones of the section's combo, and through the model's bone
        # lookup the very bones the vertex itself names (the game draws with the combo: a slot
        # naming another bone puts the vertex on it).
        bone_lookup = struct.unpack_from("<%dH" % n_bone_lookup, m, bone_lookup_at)
        wrong = 0
        for k in range(vstart, min(vstart + vcount, pn)):
            v = vertices[k]
            for j in range(4):
                if v < n_verts and m[verts_at + v * 48 + 12 + j]:
                    slot = s[po + k * 4 + j]
                    if slot >= bcount or bone_lookup[bcombo + slot] != m[verts_at + v * 48 + 16 + j]:
                        wrong += 1
        if wrong:
            say("section %d (geoset %d): %d vertex bone slots name other bones than the vertices" % (i, sec[0], wrong))
    batches = [struct.unpack_from("<BbHHHhHHHHHHH", s, bo + i * 24) for i in range(bn)]
    for i, b in enumerate(batches):
        if b[3] >= sn:
            say("batch %d: section %d of %d" % (i, b[3], sn))
        if b[6] >= n_mats:
            say("batch %d: material %d of %d" % (i, b[6], n_mats))
        if b[8] != 1:
            say("batch %d: %d textures" % (i, b[8]))
        if b[9] + b[8] > n_tex_lookup:
            say("batch %d: texture combo beyond the lookup" % i)
        if b[10] >= n_unit:
            say("batch %d: texture unit %d of %d" % (i, b[10], n_unit))
        if b[11] >= n_transp:
            say("batch %d: transparency %d of %d" % (i, b[11], n_transp))
        if b[12] >= n_tf_lookup:
            say("batch %d: texture transform %d of %d" % (i, b[12], n_tf_lookup))
    if verbose:
        import collections
        print("%s: %d sequences, %d bones, %d vertices (%d in the skin), %d sections, %d batches, %d textures, %d events, %d cameras" % (
            name, n_seqs, n_bones, n_verts, vn, sn, bn, n_tex, n_events, n_cams))
        print(" geosets:", sorted(collections.Counter(sec[0] for sec in sections).items()))
        print(" textures:", [(t[0], m[t[3]:t[3] + t[2] - 1].decode("latin1")) for t in textures])
    return problems


if __name__ == "__main__":
    problems = check(sys.argv[1], "--verbose" in sys.argv)
    for p in problems[:50]:
        print("  " + p)
    print("%s: %s" % (sys.argv[1], "ok" if not problems else "%d problems" % len(problems)))
    sys.exit(1 if problems else 0)

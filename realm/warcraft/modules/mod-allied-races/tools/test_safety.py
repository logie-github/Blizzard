#!/usr/bin/env python3
"""What the game would trip over, checked without the game's files: a global sequence's track read
from the model even where the first sequence is kept in a file of its own, and merged from the
track whose loop it is; tools/check_m2.py finding a track's entry past the end of its sequence's
.anim file and translations that aren't real floats; the narrations' sound rows playing their own
file alone. Needs numpy (tools/m2.py).

    python3 tools/test_safety.py
"""
import os
import struct
import sys
import tempfile
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_data   # noqa: E402
import check_m2     # noqa: E402
import m2           # noqa: E402

failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


# A global sequence's track (gseq 0) whose one entry is in the model, sequence 0 kept outside it.
blob = bytearray(64)
struct.pack_into("<hhIIII", blob, 0, 1, 0, 1, 20, 1, 28)
struct.pack_into("<II", blob, 20, 1, 36)
struct.pack_into("<II", blob, 28, 1, 40)
struct.pack_into("<If", blob, 36, 7, 0.5)
outside = lambda i: False
track = m2.Track.read(blob, 0, 4, outside)
check(track.timestamps == [struct.pack("<I", 7)] and track.values == [struct.pack("<f", 0.5)],
      "a global sequence's track is read from the model, not from sequence 0's file")
check(m2.Track.read_base(blob, 0, outside).timestamps == track.timestamps, "the same for a timestamps-only track")


# Merged: the parent's two sequences, then the child's own; the child's track is a global sequence's,
# the parent's isn't. The merged track is the child's loop's entry, not the parent's first sequence's.
def key(seqs):
    return lambda i: struct.unpack_from("<HH", seqs[i], 0)


parent_seqs = [bytearray(struct.pack("<HH", 0, 0) + bytes(60)), bytearray(struct.pack("<HH", 4, 0) + bytes(60))]
child_seqs = [bytearray(struct.pack("<HH", 900, 0) + bytes(60))]
parent = SimpleNamespace(seqs=parent_seqs, loops=[], key=key(parent_seqs), in_file=[True, True], anim_files={})
child = SimpleNamespace(seqs=child_seqs, loops=[1000], key=key(child_seqs), in_file=[True], anim_files={})
merged = m2.Merged(child, parent)
child_track = m2.Track(1, 0, [struct.pack("<I", 7)], [struct.pack("<3f", 1, 2, 3)])
parent_track = m2.Track(1, -1, [struct.pack("<I", 1), struct.pack("<I", 2)], [struct.pack("<3f", 9, 9, 9)] * 2)
result = merged.merge_tracks(child_track, parent_track)
check(result.gseq == merged.child_loop(0) and result.timestamps == child_track.timestamps and result.values == child_track.values,
      "a merged global sequence's track is its own loop's entry (not the parent's first sequence's)")


def model(folder, name, values):
    """A one-bone, one-sequence model whose sequence is kept in its .anim file ([values]: that
    file's bytes after a timestamp), as tools/m2.py writes them."""
    b = m2.Blob()
    b.data[:4] = b"MD20"
    struct.pack_into("<I", b.data, 4, 264)
    b.array(8, len(name) + 1, name.encode() + b"\0")
    sequence = bytearray(64)
    struct.pack_into("<HH", sequence, 60, 0xFFFF, 0xFFFF)
    b.array(28, 1, bytes(sequence))
    b.array(36, 2, struct.pack("<2h", 0, -1))
    bone = struct.pack("<iIhHI", -1, 0, -1, 0, 0)
    bone += m2.write_track(b, m2.with_value_size(m2.Track(1, -1, [("ext", 1, 0)], [("ext", 1, 4)]), 12))
    empty = lambda size: m2.write_track(b, m2.with_value_size(m2.Track(0, -1, [], []), size))
    bone += empty(8) + empty(12) + bytes(12)
    b.array(44, 1, bone)
    with open(os.path.join(folder, name + ".m2"), "wb") as f:
        f.write(b.data)
    with open(os.path.join(folder, name + "00.skin"), "wb") as f:
        f.write(b"SKIN" + bytes(44))
    with open(os.path.join(folder, name + "0000-00.anim"), "wb") as f:
        f.write(struct.pack("<I", 7) + values)
    return os.path.join(folder, name + ".m2")


with tempfile.TemporaryDirectory() as folder:
    for name in ("VoidElfMale", "NightborneFemale", "LightforgedDraeneiMale", "ZandalariTrollFemale"):
        good = check_m2.check(model(folder, name, struct.pack("<3f", 1, 2, 3)))
        short = check_m2.check(model(folder, name, b"x"))
        unreal = check_m2.check(model(folder, name, struct.pack("<3f", float("nan"), 1, 1)))
        far = check_m2.check(model(folder, name, struct.pack("<3f", 1, 1000.0, 1)))
        check(good == [] and any("outside its .anim file" in p for p in short) and any("real floats" in p for p in unreal)
              and any("real floats" in p for p in far),
              "%s: check_m2 takes a whole .anim, finds an entry past its end and translations that aren't real floats within 100 yards (%s)"
              % (name, good + short + unreal + far))


# The narrations: their own file alone, whatever the game's row they're made from has.
template = [0] * 30
template[3:13] = ["other.mp3"] * 10
template[13:23] = [1] * 10
ok = True
for race in build_data.RACE_IDS:
    row = build_data.narration_sound(template, race)
    ok = ok and row[3:13] == [build_data.NARRATION[race]] + [""] * 9 and row[13:23] == [1] + [0] * 9 and row[0] == build_data.ID_NARRATION[race]
check(ok and template[3] == "other.mp3", "a narration's sound row has its file alone, the others' places empty and unweighted")

dbc = os.path.join(build_data.MODULE, "data", "client", "dbc")


def rows(name):
    with open(os.path.join(dbc, name + ".txt")) as f:
        return {int(v[1]): v[1:] for v in (line.rstrip("\n").split("\t") for line in f) if v[0] == "put"}


races, sequences, cameras, sounds = (rows(n) for n in ("ChrRaces", "CinematicSequences", "CinematicCamera", "SoundEntries"))
for race in build_data.RACE_IDS:
    sound = sounds[int(cameras[int(sequences[int(races[race][12])][2])][2])]
    check(sound[3] == build_data.NARRATION[race] and sound[4:13] == [""] * 9 and sound[13:23] == ["1"] + ["0"] * 9,
          "race %d: its intro's camera plays %s alone" % (race, build_data.NARRATION[race]))

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)

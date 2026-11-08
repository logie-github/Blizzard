#!/usr/bin/env python3
"""The voices made by tools/package.py with the real ffmpeg, from a tone: the MP3 plays the tone,
in the game's MP3 format (MPEG-1 Layer III, 44.1 kHz, no ID3 tag, no Xing/VBR header); one an
earlier run left empty or cut short is made again from the game's file; a file ffmpeg can't read
whole stops the package with no voice left behind, and a package that stops leaves no list of files
(so the world server doesn't take the races into the game from part of them). Needs ffmpeg and numpy.

    python3 tools/test_voices.py
"""
import io
import json
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import package  # noqa: E402

failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


def tone():
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes(b"".join(struct.pack("<h", int(10000 * math.sin(2 * math.pi * 440 * i / 22050))) for i in range(11025)))
    return out.getvalue()


def audible(path):
    """Whether the MP3 decodes whole to the tone (half a second, loud)."""
    result = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", "22050",
                             "-f", "s16le", "-"], capture_output=True)
    samples = struct.unpack("<%dh" % (len(result.stdout) // 2), result.stdout)
    return result.returncode == 0 and len(samples) > 10000 and max(abs(s) for s in samples) > 5000


def game_format(data):
    """MPEG-1 Layer III at 44.1 kHz from the first byte (no ID3v2 tag), no Xing/Info header."""
    if len(data) < 4 or data[:3] == b"ID3":
        return False
    h = struct.unpack(">I", data[:4])[0]
    sync, version, layer, rate = h >> 21, (h >> 19) & 3, (h >> 17) & 3, (h >> 10) & 3
    return sync == 0x7FF and version == 3 and layer == 1 and rate == 0 and b"Xing" not in data[:200] and b"Info" not in data[:200]


RACE = {"name": "VoiceTest", "models": {}, "voices": {"vocal": [{"kits": [{"id": 123, "files": [456]}]}], "emotes": []}}
VOICE = os.path.join("Sound", "Character", "VoiceTest", "VoiceTest_123_1.mp3")
quiet = lambda _: None

with tempfile.TemporaryDirectory() as folder:
    written = package.voice_files(RACE, lambda fid: tone(), folder, quiet)
    path = os.path.join(folder, VOICE)
    with open(path, "rb") as f:
        made = f.read()
    check(written == [VOICE.replace(os.sep, "\\")] and audible(path) and game_format(made), "a voice made plays its sound, in the game's MP3 format")
    again = True
    for damaged in (b"", made[:len(made) // 2]):
        with open(path, "wb") as f:
            f.write(damaged)
        package.voice_files(RACE, lambda fid: tone(), folder, quiet)
        with open(path, "rb") as f:
            again = again and f.read() == made
    check(again and audible(path), "a voice an earlier run left empty or cut short is made again whole")

for what, source in (("a file that isn't a sound", b"not a sound"), ("a sound cut short", tone()[:-101])):
    with tempfile.TemporaryDirectory() as folder:
        try:
            package.voice_files(RACE, lambda fid: source, folder, quiet)
            stopped = False
        except RuntimeError as error:
            stopped = "voice 456 (kit 123)" in str(error)
        left = [os.path.join(d, f) for d, _, fs in os.walk(folder) for f in fs]
        check(stopped and not left, "%s stops the voices, none left behind (%s)" % (what, left))

with tempfile.TemporaryDirectory() as folder:
    races = os.path.join(folder, "races.json")
    with open(races, "w") as f:
        json.dump({"voicetest": RACE}, f)
    out = os.path.join(folder, "package")
    os.makedirs(out)
    with open(os.path.join(out, package.MANIFEST), "w") as f:
        f.write("an earlier run's files\n")
    package.RACES = races
    try:
        package.build(lambda fid: b"not a sound", out, quiet)
        stopped = False
    except RuntimeError:
        stopped = True
    check(stopped and not os.path.exists(os.path.join(out, package.MANIFEST)), "a package that stops leaves no list of files (an earlier run's taken out)")

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)

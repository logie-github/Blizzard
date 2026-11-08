#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's story's Warcraft III voices (tools/naga/sounds.py) as 3.3.5 sounds: each file fetched,
checked against the SHA-1 and size the table pins, and written as the game's own voices are (RIFF
WAVE, 16-bit PCM, mono, 22,050 Hz; ffmpeg converts any that aren't).

    python3 tools/naga_voices.py fetch DIR          fetches them and writes DIR/Sound/Creature/WC3Voices/
                                                     <name>.wav, then DIR/nagavoices.files (the list)
    python3 tools/naga_voices.py convert SRC DIR     the same from files already fetched (SRC/<name>.wav)

Where they come from: warcraft.wiki.gg's file store (https://warcraft.wiki.gg/images/<name>.wav: its
robots.txt allows /images/), and, for a file that doesn't come from there, Wowpedia's copy of the same
file (static.wikia.nocookie.net/wowpedia/images/<a>/<ab>/<name>.wav, MediaWiki's hashed path; the
same SHA-1). Plain requests with the repository's User-Agent, one at a time; nothing else (a page that
isn't the file, such as a challenge, fails the SHA-1 and isn't used). MURLOC_CACHE keeps what was
fetched (CI caches it with the allied races' files).

They are Blizzard's files, so they are never in this repository: the server package makes them
(scripts/package-azerothcore.sh) into the module's data/files; the world server puts them in the
game's patch-<locale>-T beside their SoundEntries rows (src/MurlocNagaPatch.cpp). The list is written
last, naming the files there; a voice that couldn't be had is left out of it and its line shows as
text alone. Exit status 1 when any is missing.
"""
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from naga import sounds as S  # noqa: E402

USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"
RATE, CHANNELS, BITS = 22050, 1, 16                 # the game's own voices (COIL_LadyVashj_*.wav)


def sources(name):
    md5 = hashlib.md5((name + ".wav").encode()).hexdigest()
    return ["https://warcraft.wiki.gg/images/%s.wav" % name,
            "https://static.wikia.nocookie.net/wowpedia/images/%s/%s/%s.wav" % (md5[0], md5[:2], name)]


def checked(data, sha1, size):
    return len(data) == size and hashlib.sha1(data).hexdigest() == sha1


def download(name, sha1, size, dead):
    """The file's bytes from the first source that gives the pinned file, or None. [dead]: sources
    that answered nothing at all this run (not tried again)."""
    for n, url in enumerate(sources(name)):
        if n in dead:
            continue
        for attempt in range(3):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=30) as response:
                    data = response.read(size + 1)
                if checked(data, sha1, size):
                    return data
                print("voices: %s from %s isn't the file (%d bytes)" % (name, url.split("/")[2], len(data)), file=sys.stderr)
                break                                      # (an answer, but not the file: the next source)
            except Exception as error:                     # a network hiccup: once more, a little later
                print("voices: %s from %s: %s" % (name, url.split("/")[2], error), file=sys.stderr)
                if attempt == 2:
                    dead.add(n)
                time.sleep(1 + attempt)
        time.sleep(0.2)
    return None


def wave_chunks(data):
    """A RIFF WAVE's chunks {id: bytes} (the first of each), or None."""
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return None
    out, at = {}, 12
    while at + 8 <= len(data):
        cid, size = data[at:at + 4], struct.unpack_from("<I", data, at + 4)[0]
        if at + 8 + size > len(data):
            return None                                     # (a chunk past the file's end)
        out.setdefault(cid, data[at + 8:at + 8 + size])
        at += 8 + size + (size & 1)
    return out


def wave_format(data):
    """(format tag, channels, rate, bits) of a RIFF WAVE, or None."""
    chunks = wave_chunks(data)
    if not chunks or len(chunks.get(b"fmt ", b"")) < 16:
        return None
    tag, channels, rate, _, _, bits = struct.unpack_from("<HHIIHH", chunks[b"fmt "], 0)
    return tag, channels, rate, bits


def plain_wave(fmt, sound):
    """A RIFF WAVE of its format chunk and its sound alone."""
    body = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(sound)) + sound
    return b"RIFF" + struct.pack("<I", len(body)) + body + (b"\0" if len(sound) & 1 else b"")


def game_wave(data):
    """[data] as the game's own voices are: 16-bit PCM, mono, 22,050 Hz, nothing but the sound in the
    file (a file of that format rewritten without its other chunks, the wiki's tags; anything else
    through ffmpeg)."""
    if wave_format(data) == (1, CHANNELS, RATE, BITS):
        chunks = wave_chunks(data)
        if b"data" in chunks:
            return plain_wave(chunks[b"fmt "][:16], chunks[b"data"])
    with tempfile.TemporaryDirectory() as folder:
        src, dst = os.path.join(folder, "in.wav"), os.path.join(folder, "out.wav")
        with open(src, "wb") as f:
            f.write(data)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", str(CHANNELS), "-ar", str(RATE),
                        "-c:a", "pcm_s16le", "-map_metadata", "-1", "-bitexact", dst], check=True)
        out = open(dst, "rb").read()
    if wave_format(out) != (1, CHANNELS, RATE, BITS):
        raise ValueError("ffmpeg's output isn't the game's format")
    return out


def make(read, folder):
    """Writes every voice [read] gives (name -> the wiki's file, or None) into [folder], then the
    list. Returns how many are there."""
    written = []
    for name, sha1, size, _, _ in S.VOICES:
        data = read(name, sha1, size)
        if data is None:
            continue
        try:
            wav = game_wave(data)
        except Exception as error:
            print("voices: %s couldn't be made the game's: %s" % (name, error), file=sys.stderr)
            continue
        path = os.path.join(folder, *S.packaged_path(name).split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".part", "wb") as out:
            out.write(wav)
        os.replace(path + ".part", path)
        written.append(S.packaged_path(name))
    with open(os.path.join(folder, S.MANIFEST), "w", newline="\n") as out:
        out.write("".join(name + "\n" for name in sorted(written)))
    print("voices: %d of %d of the naga's story's voices in %s" % (len(written), len(S.VOICES), folder))
    return len(written)


def fetcher(cache):
    dead = set()

    def read(name, sha1, size):
        path = os.path.join(cache, "wc3", name + ".wav") if cache else None
        if path and os.path.exists(path):
            data = open(path, "rb").read()
            if checked(data, sha1, size):
                return data
        data = download(name, sha1, size, dead)
        if data is not None and path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path + ".part", "wb") as f:
                f.write(data)
            os.replace(path + ".part", path)
        return data
    return read


def local(source):
    def read(name, sha1, size):
        path = os.path.join(source, name + ".wav")
        if os.path.exists(path):
            data = open(path, "rb").read()
            if checked(data, sha1, size):
                return data
            print("voices: %s isn't the wiki's file" % path, file=sys.stderr)
        return None
    return read


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "fetch":
        sys.exit(0 if make(fetcher(os.environ.get("MURLOC_CACHE")), sys.argv[2]) == len(S.VOICES) else 1)
    elif len(sys.argv) == 4 and sys.argv[1] == "convert":
        sys.exit(0 if make(local(sys.argv[2]), sys.argv[3]) == len(S.VOICES) else 1)
    else:
        print(__doc__)
        sys.exit(2)

# SPDX-License-Identifier: GPL-3.0-or-later
"""Nerglish: English as Blizzard's own translator made it murloc (the Nerglish Translator, April 1,
2019, news.blizzard.com/en-us/blizzard/22940237: its script, assets.webn.mobi/nerglish/nerglish.js,
"King Mrgl-Mrgl sends his regards!"), word for word the same.

Its rules: every run of letters (a-z, A-Z, A-ring to y-umlaut) is a word, everything else (spaces,
digits, punctuation, apostrophes) stays as it is. A word Blizzard knows the murloc for is that word
(DICTIONARY); any other is made by a Mersenne Twister (random-js's MT19937) seeded by the word's hash
(Java's String.hashCode, 32 bits): a length between one less (two at least) and two more than the
word's, the first letter from a list, each after it from the letter before's list (CHAIN). The same
word is always the same murloc; a capitalized word starts with a capital.

    python3 tools/nerglish.py "Hello, friend! The naga are coming."
"""
import re
import sys

DICTIONARY = {
    "feral": "furl", "move": "flllurlog", "walk": "flllurlog", "fisherman": "fllurlokkr", "net": "mgrrrl",
    "gordunni": "grrundee", "clan": "klun", "guild": "klun", "thirsty": "mllgggrrrr", "with": "mmgr",
    "tasty": "mmm", "yummy": "mmm", "good": "mmmm", "great": "mmmmm", "right": "mmmml", "correct": "mmmml",
    "aunt": "mmmrrggllm", "uncle": "mmmrrrggglm", "friend": "mmmrrglllm", "friends": "mmmrrglllm",
    "murloc": "mmmurlok", "yes": "mrgle", "ok": "mrgle", "magic": "mrrrggk", "sorry": "mrrrgll", "and": "n",
    "no": "nk", "ogre": "rrrgrrr", "sing": "shng", "scar": "skr", "spring": "srng", "honor": "uuua",
    "battlecry": "mrglllll", "charge": "flllurllg", "beast": "flrrgmmrk", "king": "kklun", "crush": "kllrrug",
    "taunt": "murrgl", "agent": "fllrrgmgr", "combo": "flrrkgr", "blizzard": "blrrgrk",
    "battle": "aaaaaaaaugurgble", "nerglish": "mmmurlokmurg", "translate": "mmmurglurk", "mrgl": "mrgl",
}
CHAIN = {
    "": "mmmmmmmmmmmmmmmmmmmmmmmmmmgggggnnrrrrbbaaaaksuhhfffffffff",
    "m": "mmmmmmuurrrrrrrrrrrn", "g": "lllllllllllrrmmkksf", "l": "mmmmmmmgggkrlluuu",
    "r": "rrmmnkkfflllllggggggggggggg", "k": "mmmnllu", "s": "hhhruk", "h": "ummr",
    "u": "uamgggrrrrrrrf", "a": "aaaauuummmggkfs", "n": "ngla", "f": "rrrrrullllfff", "b": "brrlmu",
}
WORD = re.compile("[a-zA-ZÀ-ÿ]+")
M32 = 0xFFFFFFFF


def _int32(v):
    v &= M32
    return v - (1 << 32) if v & 0x80000000 else v


class _Twister:
    """random-js's MT19937 (seeded by one number) and its integer(min, max)."""

    def __init__(self, seed):
        self.data = [0] * 624
        t = self.data[0] = seed & M32
        for i in range(1, 624):
            t = self.data[i] = ((((t ^ (t >> 30)) * 1812433253) & M32) + i) & M32
        self.index = 624

    def _twist(self):
        d = self.data
        for t in range(624):
            n = (d[t] & 0x80000000) | (d[(t + 1) % 624] & 0x7FFFFFFF)
            d[t] = d[(t + 397) % 624] ^ (n >> 1) ^ (0x9908B0DF if n & 1 else 0)

    def next(self):
        if self.index >= 624:
            self._twist()
            self.index = 0
        e = self.data[self.index]
        self.index += 1
        e ^= e >> 11
        e ^= (e << 7) & 0x9D2C5680
        e ^= (e << 15) & 0xEFC60000
        e ^= e >> 18
        return e & M32                     # (as unsigned: the script's >>> 0, or & a mask)

    def integer(self, low, high):
        span = high - low
        if span <= 0:
            return low
        if (span + 1) & span == 0:         # a power of two, less one: a mask
            return low + (self.next() & span)
        size = span + 1
        limit = size * (4294967296 // size)
        while True:
            r = self.next()
            if r < limit:
                return low + r % size


def _hash(word):
    n = 0
    for ch in word:
        n = _int32((n << 5) - n + ord(ch))
    return n


def word(english):
    """One word (letters only) in Nerglish."""
    known = DICTIONARY.get(english.lower())
    capital = english[0] == english[0].upper()
    if known:
        return known[0].upper() + known[1:] if capital else known
    rng = _Twister(_hash(english))

    def after(letter):
        choices = CHAIN.get(letter, " ")
        return choices[rng.integer(0, len(choices) - 1)] or " "
    length = rng.integer(max(len(english) - 1, 2), len(english) + 2)
    letter = after("")
    out = letter.upper() if capital else letter
    for _ in range(1, length):
        letter = after(letter)
        out += letter
    return out


def translate(text):
    """[text] in Nerglish: its words murloc, the rest as it is. A game escape (|cff..., |r, $N, $B,
    <...>) is kept: tools translate only what a player reads."""
    out, at = [], 0
    for keep in re.finditer(r"\|c[0-9a-fA-F]{8}|\|r|\|n|\$[A-Za-z][A-Za-z]*:[^;]*;|\$[A-Za-z]|<[^>]*>", text):
        out.append(WORD.sub(lambda m: word(m.group(0)), text[at:keep.start()]))
        out.append(keep.group(0))
        at = keep.end()
    out.append(WORD.sub(lambda m: word(m.group(0)), text[at:]))
    return "".join(out)


if __name__ == "__main__":
    print(translate(" ".join(sys.argv[1:]) or sys.stdin.read()))

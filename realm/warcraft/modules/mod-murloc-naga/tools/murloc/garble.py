# SPDX-License-Identifier: GPL-3.0-or-later
"""What a murloc reads of another race's words: each word one of the language's own (the game's
LanguageWords table) of the same length, the same word always the same, its capital and the marks
around it kept. The game does this itself with what people say aloud; quest and gossip windows show
their text as written, so the compiler garbles those for the murlocs' questline."""
import re
import zlib

WORD = re.compile("[A-Za-zÀ-ÿ']+")
KEEP = re.compile(r"\|c[0-9a-fA-F]{8}|\|r|\|n|\$[A-Za-z][A-Za-z]*:[^;]*;|\$[A-Za-z]|<[^>]*>")


class Garbler:
    def __init__(self, language_words):
        """[language_words]: (language id, word) pairs (LanguageWords.dbc)."""
        self.words = {}
        for lang, word in language_words:
            self.words.setdefault(lang, {}).setdefault(len(word), []).append(word)

    def word(self, english, lang):
        by_length = self.words.get(lang)
        if not by_length:
            return english
        n = len(english)
        length = n if n in by_length else min(by_length, key=lambda k: (abs(k - n), k))
        choices = by_length[length]
        out = choices[zlib.crc32(english.lower().encode()) % len(choices)]
        if english[0].isupper():
            out = out[0].upper() + out[1:]
        return out

    def text(self, text, lang):
        out, at = [], 0
        for keep in KEEP.finditer(text):
            out.append(WORD.sub(lambda m: self.word(m.group(0), lang), text[at:keep.start()]))
            out.append(keep.group(0))
            at = keep.end()
        out.append(WORD.sub(lambda m: self.word(m.group(0), lang), text[at:]))
        return "".join(out)

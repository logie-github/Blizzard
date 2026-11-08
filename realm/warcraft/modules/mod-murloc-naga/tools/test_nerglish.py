#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tools/nerglish.py (Blizzard's 2019 Nerglish translator, ported) checked: its random numbers are the
Mersenne Twister's (MT19937, seeded as random-js seeds it: init_genrand), its seed Java's
String.hashCode, Blizzard's own words as Blizzard has them, the rest kept as the translator keeps it.

    python3 tools/test_nerglish.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nerglish as N  # noqa: E402

failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


# MT19937's reference: seeded 5489, its first number is 3499211612 (and its 10000th 4123659995).
t = N._Twister(5489)
first = t.next()
for _ in range(9998):
    t.next()
check(first == 3499211612 and t.next() == 4123659995, "the Mersenne Twister is MT19937 (seed 5489: 3499211612, ..., 4123659995)")
check(N._hash("Hello") == 69609650 and N._hash("") == 0 and N._hash("murloc") == -1062834378, "the seed is Java's String.hashCode")
check(N.word("murloc") == "mmmurlok" and N.word("Murloc") == "Mmmurlok" and N.word("friend") == "mmmrrglllm", "Blizzard's own words")
check(N.translate("Yes, and no.") == "Mrgle, n nk.", "its punctuation kept")
words = [N.word(w) for w in ("naga", "tyranny", "escape", "Stormwind", "fish")]
check(all(w and set(w.lower()) <= set("mgnrbaksuhfl") for w in words), f"words of murloc letters alone ({words})")
check(N.word("Stormwind")[0].isupper() and not N.word("stormwind")[0].isupper(), "a capital kept")
check(N.word("escape") == N.word("escape"), "the same word, the same murloc")
for w in ("a", "it", "naga", "escapes", "Supercalifragilistic"):
    n = len(N.word(w))
    check(max(len(w) - 1, 2) <= n <= len(w) + 2, f"{w!r}: {n} letters (its length's, one less to two more)")
check(N.translate("Thank you, $N.$B$BGo north.") .count("$N") == 1 and "$B$B" in N.translate("Go.$B$BNow."),
      "the game's escapes ($N, $B) kept")
check(N.translate("It's done.") == N.word("It") + "'" + N.word("s") + " " + N.word("done") + ".", "an apostrophe splits a word")

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)

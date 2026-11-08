# SPDX-License-Identifier: GPL-3.0-or-later
"""The models tools/naga_emotes.py takes the naga's emotes from (wago.tools file ids; their animations'
files are the ones these models name). With tools/naga/looks.py and tools/naga/sounds.py, what the
naga's story's packaging fetches: CI's cache of fetched files is keyed on them."""

NAGA_MODELS = {"Male": 120294, "Female": 120263}         # character/naga_/<sex>/naga_<sex>.m2: skeletons, kneel and point
NIGHT_ELF_MODELS = {"Male": 120791, "Female": 120590}    # character/nightelf/<sex>/nightelf<sex>.m2: every emote

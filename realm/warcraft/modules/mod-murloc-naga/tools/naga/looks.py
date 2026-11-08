# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's story's looks the 3.3.5 game hasn't (the bible's 6.3 and 18.6): CreatureDisplayInfo ids
the chapters give their people (creature_template_model), made by tools/naga_assets.py:

    LOOKS["serena"]  -> 40000

  - three of today's models made 3.3.5's (tools/naga_models.py, fetched and converted as the server is
    packaged): Serena Scarscale's sea witch, Maiev's Watchers (Legion's warden, four skins), Queen
    Azshara as a night elf;
  - looks made of the game's own parts (CreatureDisplayInfoExtra rows: a race's character model, its
    skin, face, hair and the game's items): Grand Marshal Garithos, Handmaiden Vashj and the Highborne
    court, Taelon Emberveil, Shaelyn Harborsong.

EMOTES says which emotes each look plays (the animations its model has). A look made of the game's
parts plays everything its race's character model does (every emote, sitting, kneeling, mounted).

Without the converted models (the server package couldn't make them) their looks draw nothing:
FALLBACK names a look of the game's to give those people instead (the chapters' choice; the module
logs which models are missing).

Ids: CreatureModelData 3800 to 3849, CreatureDisplayInfo 40000 to 40299, CreatureDisplayInfoExtra
25000 to 25099 (clear of the game's, an HD look's and the other modules').
"""

MODEL_DATA_FIRST, MODEL_DATA_LAST = 3800, 3849
DISPLAY_FIRST, DISPLAY_LAST = 40000, 40299
EXTRA_FIRST, EXTRA_LAST = 25000, 25099

# Today's models made 3.3.5's. model: the file id on wago.tools; model_data: its CreatureModelData id;
# template: the game's CreatureModelData row it's copied from (its size, footprints, blood) with
# [sound] its creature sounds (CreatureSoundData: wounds, deaths, attacks) and the model's own box
# (today's CreatureModelData's GeoBox); skins: the textures its looks name (file ids).
CREATURES = [
    {"name": "SeaWitch", "folder": "Creature/SeaWitch", "model": 1530843, "model_data": 3800,
     "template": 2535, "sound": 2282,                              # Lady Vashj's size; the naga women's sounds
     "box": (-1.80637729168, -0.99034464359, -0.01818263531, 0.55956739187, 0.95761823654, 2.32695269585),
     "skins": {"SeaWitchSkin": 1531400, "SeaWitchSkin2": 1531401}},
    {"name": "Warden", "folder": "Creature/Warden", "model": 1133752, "model_data": 3801,
     "template": 2529, "sound": 56,                                # Maiev's size; the night elf women's sounds
     "box": (-0.54519271851, -0.58281576633, -0.00023166277, 0.46552929282, 0.61970698833, 2.24232578278),
     "skins": {"WardenSkin1": 1133887, "WardenSkin2": 1272371, "WardenSkin3": 1272372, "WardenSkin4": 1272373}},
    {"name": "QueenAzshara", "folder": "Creature/QueenAzshara", "model": 535719, "model_data": 3802,
     "template": 2529, "sound": 56,
     "box": (-0.3893429935, -0.36408901215, 0.00231999997, 0.30982899666, 0.42888599634, 2.25829005241),
     "skins": {}},
]

# Their looks: display id -> (model data id, the game's display it's copied from (its sounds, blood),
# scale, its textures (the creature's skins, by name)).
CREATURE_LOOKS = {
    40000: (3800, 20748, 1.0, ("SeaWitchSkin", "SeaWitchSkin2", "")),
    40001: (3801, 20628, 1.0, ("WardenSkin1", "", "")),
    40002: (3801, 20628, 1.0, ("WardenSkin2", "", "")),
    40003: (3801, 20628, 1.0, ("WardenSkin3", "", "")),
    40004: (3801, 20628, 1.0, ("WardenSkin4", "", "")),
    40005: (3802, 20628, 1.0, ("", "", "")),
}

# Looks of the game's parts: display id -> (extra id, the game's display it's copied from (its
# character model, sounds, scale), race, sex, skin, face, hair style, hair colour, facial features,
# items: helm, shoulders, shirt, chest, belt, legs, boots, wrists, gloves, tabard, cape (the game's
# ItemDisplayInfo ids)). Copied from the game's people who wear them; the colours weren't seen here.
PARTS_LOOKS = {
    # Grand Marshal Garithos (no model in any World of Warcraft): a human in Lordaeron's plate, blue
    # and silver (the Lordaeron Commander of Old Hillsbrad's), a closed helm (the Lordaeron Soldier's)
    # and the Alliance's blue tabard.
    40010: (25000, 17144, 1, 0, 1, 8, 1, 4, 1, (15334, 9497, 36531, 13380, 0, 13382, 19719, 0, 19717, 31254, 0)),
    # Handmaiden Vashj: a night elf woman, the palest skin, in the Highborne's robes (the Highborne
    # Summoners' of Dire Maul: cyan and gold, the robed shoulders), no ghost.
    40011: (25001, 11208, 4, 1, 0, 0, 5, 0, 0, (0, 15375, 0, 7853, 0, 7855, 24438, 0, 16027, 0, 0)),
    # The Highborne court (M0): night elves in the same robes, two women and two men.
    40012: (25002, 11208, 4, 1, 3, 2, 4, 2, 4, (0, 15375, 0, 7853, 0, 7855, 24438, 0, 16027, 0, 0)),
    40013: (25003, 11207, 4, 0, 3, 7, 4, 2, 2, (0, 15375, 24437, 7853, 0, 7855, 24438, 0, 16027, 0, 0)),
    40014: (25004, 11208, 4, 1, 6, 4, 4, 0, 7, (0, 15375, 0, 7853, 0, 7855, 24438, 0, 16027, 0, 0)),
    40015: (25005, 11207, 4, 0, 5, 8, 5, 0, 1, (0, 15375, 0, 7853, 0, 7855, 24438, 0, 16027, 0, 0)),
    # Taelon Emberveil, a spell breaker of Silvermoon: a blood elf man in red and gold (Arcanist
    # Helion's robes, a magister's shoulders).
    40016: (25006, 15528, 10, 0, 2, 4, 10, 2, 0, (0, 33358, 0, 33387, 33388, 33389, 33386, 0, 0, 0, 0)),
    # Shaelyn Harborsong, the last of Nendis: an old night elf woman in a hunter's green leathers
    # (Nessa Shadowsong's). Her bow is her creature_equip_template's (the chapter's).
    40017: (25007, 9344, 4, 1, 2, 5, 3, 6, 5, (0, 0, 0, 22019, 4102, 13048, 7029, 0, 11414, 0, 0)),
}

LOOKS = {
    "serena": 40000,                       # Serena Scarscale (today's sea witch)
    "warden": 40001, "warden_2": 40002, "warden_3": 40003, "warden_4": 40004,   # Maiev's Watchers
    "azshara": 40005,                      # Queen Azshara, a night elf (M0's balcony)
    "garithos": 40010,
    "handmaiden_vashj": 40011,
    "highborne_1": 40012, "highborne_2": 40013, "highborne_3": 40014, "highborne_4": 40015,
    "taelon": 40016,
    "shaelyn": 40017,
}

# Without the converted models: a look of the game's for the same people (the bible's own choices).
FALLBACK = {"serena": 22870, "warden": 2306, "warden_2": 4841, "warden_3": 4842, "warden_4": 4843, "azshara": 11208}

# The emotes each look plays (3.3.5's AnimationData names; the converted models' own animations, checked
# by tools/test_data.py against what tools/naga_models.py kept). "all": a race's character model's.
SEA_WITCH_EMOTES = ["EmoteTalk", "EmoteWork", "EmoteRoar", "BattleRoar", "ChannelCastDirected", "ChannelCastOmni",
                    "ReadyBow", "LoadBow", "HoldBow", "AttackBow", "SpellCastDirected", "SpellCastOmni", "Stun", "Drown", "Drowned"]
NIGHT_ELF_EMOTES = ["EmoteTalk", "EmoteTalkExclamation", "EmoteTalkQuestion", "EmoteBow", "EmoteWave", "EmoteCheer",
                    "EmoteApplaud", "EmoteBeg", "EmoteChicken", "EmoteCry", "EmoteDance", "EmoteEat", "EmoteFlex",
                    "EmoteKiss", "EmoteKneel", "EmoteLaugh", "EmotePoint", "EmoteRoar", "EmoteRude", "EmoteSalute",
                    "EmoteShout", "EmoteShy", "EmoteTrain", "EmoteYes", "EmoteNo", "EmoteWork", "EmoteUseStanding",
                    "SitGround", "SitGroundDown", "SitGroundUp", "SitChairLow", "SitChairMed", "SitChairHigh",
                    "Sleep", "SleepDown", "SleepUp", "KneelStart", "KneelLoop", "KneelEnd", "Mount", "StealthStand"]
EMOTES = {
    "serena": SEA_WITCH_EMOTES,
    "warden": NIGHT_ELF_EMOTES, "warden_2": NIGHT_ELF_EMOTES, "warden_3": NIGHT_ELF_EMOTES, "warden_4": NIGHT_ELF_EMOTES,
    "azshara": NIGHT_ELF_EMOTES,
    "garithos": "all", "handmaiden_vashj": "all", "highborne_1": "all", "highborne_2": "all", "highborne_3": "all",
    "highborne_4": "all", "taelon": "all", "shaelyn": "all",
}

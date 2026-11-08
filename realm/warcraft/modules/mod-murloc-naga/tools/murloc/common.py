# SPDX-License-Identifier: GPL-3.0-or-later
"""The murlocs' questline: ids, and the names a chapter may use for looks, models, icons, emotes,
sounds, spell visuals and languages (tools/murloc/SCHEMA.md). Data only."""

MURLOC_RACE, MURLOC_BIT = 19, 1 << 18
MAP_KALIMDOR, MAP_EASTERN = 1, 0

# Ids: creatures 976000-977999, objects 978000-978499, quests 978500-978999, items 979000-979799;
# gossip menus and texts 976000 on (their own tables); spawns 9760000 on, objects' 9790000 on;
# object looks (GameObjectDisplayInfo) 9800-9999; story phases' spells 979800-979899; trainers 976000 on.
NPC_BASE, NPC_END = 976000, 977999
GO_BASE, GO_END = 1976000, 1977999             # (was 978000-978499: too few; a scene list's id is
OLD_GO_BASE, OLD_GO_END = 978000, 978499        #  an object's entry * 1000 + n, so it stays under 2^31)
QUEST_BASE, QUEST_END = 978500, 978999
ITEM_BASE, ITEM_END = 979000, 979799
TEXT_BASE = 976000
SPAWN_BASE, SPAWN_END = 9760000, 9789999
GO_SPAWN_BASE, GO_SPAWN_END = 9790000, 9799999
GO_DISPLAY_BASE, GO_DISPLAY_END = 9800, 9999
PHASE_SPELL_BASE = 979600                       # 979600-979899: the story's phases (300)
SPELL_BASE, SPELL_END = 979900, 979999          # the story's auras (AURAS)
TRAINER_BASE = 976000
GRAVEYARD_BASE, GRAVEYARD_END = 9760, 9799      # game_graveyard ids (GRAVEYARDS)
SPIRIT_HEALER = 6491                            # the game's spirit healer, at each of the tribe's graveyards
LOOT_COMMENT = "mod-murloc-naga: story"         # creature_loot_template rows of the story's (its own to take out)
CAMP_NPC_BASE, CAMP_NPC_END = 975000, 975099     # the naga camp's creatures (tools/content.py): their loot isn't the story's

# The race's own phase (the world's and theirs): spell_area puts it on a murloc in every zone the
# story goes to. Story phases (an NPC there from a quest on, until one, or while one's in the log)
# take bits of their own, zone by zone.
RACE_PHASE = 1024
STORY_PHASE_BITS = [1 << b for b in range(12, 31) if (1 << b) not in (32768, 65536, 131072)]
STORY_PHASE_MASK = sum(STORY_PHASE_BITS)
# A bit no player ever has, on every story-phased person and thing: none of it is seen by more players for
# it, but the story's people all share it, so a scene finds whoever it hands beats to whatever their phases.
SCENE_BIT = 1 << 31

# Who people are to a murloc: FactionTemplate ids.
SIDES = {
    "tribe": 35,        # friendly to everyone (the tribe's phase is murlocs' alone)
    "naga": 74,         # the naga (hostile)
    "hostile": 14,      # monsters
    "neutral": 7,       # creatures, yellow
}

# Looks (CreatureDisplayInfo ids) by name.
LOOKS = {
    # murlocs
    "oracle": 4920, "tidehunter": 478, "seer": 3940, "coastrunner": 3619, "netter": 2597,
    "warrior": 540, "hunter": 652, "raider": 346, "flagglemurk": 1305, "murkdeep": 1079,
    "fry_green": 15394, "fry_blue": 15393, "fry_pink": 15396, "fry_purple": 15397,
    # naga
    "naga_male": 4036, "siren": 4980, "sorceress": 4973, "naga_warrior": 11269, "naga_lord": 4762,
    "sea_witch": 4981, "myrmidon": 6747,
    # others
    "troll_scout": 31737, "trigger": 11686,
}
# The tribe's people: murloc2 (the race's own murloc) with emotes, in each skin (tools/build_data.py's
# ID_TRIBE_DISPLAY on): talk, point, cheer, bow, cry, wave, laugh, beg, applaud... all play on them.
TRIBE_SKINS = ["grey", "blue", "green", "pale", "orange", "gold", "fel", "red", "purple", "slate", "abyssal", "bronze", "ice"]
LOOKS.update({f"murloc_{name}": 33103 + n for n, name in enumerate(TRIBE_SKINS)})

# Object models: a GameObjectDisplayInfo id, or a game model path (a look of its own is made).
MODELS = {
    "murloc_hut": "World\\AZEROTH\\SWAMPOSORROW\\PASSIVEDOODADS\\WATERHUTS\\WaterHut01.mdx",
    "murloc_hut2": "World\\AZEROTH\\SWAMPOSORROW\\PASSIVEDOODADS\\WATERHUTS\\WaterHut02.mdx",
    "great_pearl": "World\\GENERIC\\Murloc\\Passive Doodads\\Pearl\\GreatPearl_01.mdx",
    "murloc_altar": "World\\GENERIC\\Murloc\\Passive Doodads\\Altars\\MurlocAltar_01.mdx",
    "naga_pagoda": "World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Pagoda\\NagaPagodaHut01.mdx",
    "naga_banner": "World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Banner\\NA_Banner01.mdx",
    "naga_torch": "World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\TORCH\\NA_Torch01.mdx",
    "naga_crate": "World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Crates\\NA_Crate01.mdx",
    "naga_weapons": "World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\WeaponStacks\\NA_WeaponStack01.mdx",
    "naga_jar": "World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Jars\\NA_Jar01.mdx",
    # the game's object looks (GameObjectDisplayInfo)
    "crate": 275, "crate_grain": 347, "chest": 10, "treasure_chest": 259, "barrel": 32, "barrel_broken": 9,
    "basket": 468, "crab_basket": 7759, "kelp": 6322, "seaweed": 6316, "clam": 261, "coral": 887, "coral_small": 2251,
    "sack": 5511, "cage": 6858, "cage_hanging": 7982, "bonfire": 200, "campfire": 192, "driftwood": 627,
    "fishing_pole": 6324, "bottle": 225, "mailbox": 7815,
}

# Item icons (ItemDisplayInfo ids, or "item:<entry>" for an item of the game's look).
ICONS = {
    "kelp": 18089, "coral": 6652, "pearl": 12310, "mussel": 22193, "trinket": 12410, "bread": 21203,
    "letter": 3093, "scroll": 3093, "trident": 8747, "lures": 7914, "fish": 24702, "shell": 22193,
    "key": 7737, "bones": 7140, "eye": 7140, "orders": 3093, "spear": 8747,
}

# Emotes (Emotes.dbc): one-off by name.
EMOTES = {
    "talk": 1, "bow": 2, "wave": 3, "dance": 94, "work": 467, "cheer": 4, "exclamation": 5, "question": 6, "eat": 7, "laugh": 11,
    "rude": 14, "roar": 15, "kneel": 16, "kiss": 17, "cry": 18, "chicken": 19, "beg": 20, "applaud": 21,
    "shout": 22, "flex": 23, "shy": 24, "point": 25, "wound": 33, "attack": 36, "attack2h": 37,
    "parry": 39, "spell": 51, "battle_roar": 53, "kick": 60, "throw": 61, "salute": 66, "yes": 273,
    "no": 274, "train": 275, "laugh_nosheathe": 153, "eat_nosheathe": 92, "point_nosheathe": 29,
    # (what the naga's models play besides talk, roar, battle roar, casts and work: bible 4.2)
    "omnicast": 463, "drown": 387, "stun": 462, "ready1h": 45, "ready_bow": 48,
}
# The player's own emotes (EmotesText.dbc), for objectives: /wave at someone (a quest's `emotes`).
TEXT_EMOTES = {
    "wave": 101, "bow": 17, "dance": 34, "roar": 75, "cheer": 21, "hug": 56, "kiss": 58, "salute": 78, "cry": 31,
    "laugh": 60, "beg": 8, "point": 72, "flex": 41, "chicken": 22, "applaud": 5, "greet": 48, "hello": 55, "thank": 97,
    "shy": 84, "tickle": 142, "pat": 364, "love": 225, "kneel": 59, "sit": 86, "sleep": 87, "rude": 77, "glare": 46,
    "cower": 28, "pray": 74, "sing": 433, "clap": 24, "hungry": 57, "fart": 39, "train": 264, "burp": 18, "drink": 35,
    "eat": 37, "plead": 71, "surrender": 92, "comfort": 110, "soothe": 134, "cuddle": 111, "nod": 67, "no": 66,
    "flee": 306, "charge": 305, "victory": 100, "brandish": 370, "threaten": 98, "follow": 324,
}
# States (Emotes.dbc's EMOTE_STATE_*): kept until changed.
STATES = {
    "none": 0, "dance": 10, "sleep": 12, "sit": 13, "stun": 64, "dead": 65, "kneel": 68,
    "use": 69, "work": 173, "ready": 27, "mine": 233, "chop": 234, "fish": 379, "cower": 431,
    "read": 69, "eat": 418, "talk": 378, "laugh": 392,     # (no reading pose in 3.3.5: a standing use)
    # (a naga's: singing, praying and remembering a channel; lying still the drowned; a trident shouldered)
    "channel": 468, "channel_directed": 469, "drowned": 383, "swim_idle": 437, "ready_thrown": 465, "ready_bow": 376,
    "ready_spell": 474, "roar": 391,
}

# Sounds (SoundEntries ids) by name (more, with every id: the research's effects.md; any id works).
SOUNDS = {
    # murlocs
    "murloc_aggro": 416, "murloc_alert": 1109, "murloc_fidget": 414, "murloc_fidget2": 415, "murloc_attack": 417,
    "murloc_wound": 418, "murloc_wound_crit": 419, "murloc_death": 420, "murloc_aggro_old": 11802, "murloc_preaggro": 15995,
    "baby_murloc": 8475, "baby_murloc_dance": 8485, "marine_murloc_click": 15933,
    # naga
    "naga_attack": 3433, "naga_wound": 3434, "naga_death": 3436, "naga_aggro": 3438, "naga_hiss": 3437,
    "siren_attack": 4020, "siren_death": 4023, "siren_aggro": 4025, "siren_hiss": 4024,
    "naga_lord_aggro": 11695, "naga_lord_hiss": 11694, "naga_lord_death": 11693,
    # water
    "splash_small": 1090, "splash": 1096, "splash_big": 1097, "thud_water": 1267, "drowning": 5736,
    "pickup_water": 1197, "water_elemental": 10012,
    # places
    "ocean": 1114, "beach_day": 4164, "beach_night": 4165, "ship": 4215, "ship_docked": 5154, "sail": 5454,
    "dock_bell": 5495, "underwater": 4123, "waterfall": 3791, "stormwind": 4198, "swamp": 4200, "westfall": 4207,
    "tavern": 4394, "tavern_crowded": 7359, "campfire": 3240,
    # guards' voices (hello, goodbye, annoyed)
    "human_guard_pissed": 5973, "human_guard_hello": 5971, "dwarf_guard_pissed": 5912, "sentinel_pissed": 6007,
    "goblin_guard_pissed": 5963, "orc_guard_pissed": 6020, "undead_guard_pissed": 6041, "tauren_guard_pissed": 6010,
}

# Spells for looks alone (cosmetic), by name.
VISUALS = {}

# Languages (Languages.dbc).
LANGUAGES = {
    "universal": 0, "orcish": 1, "darnassian": 2, "taurahe": 3, "dwarvish": 6, "common": 7, "demonic": 8,
    "titan": 9, "thalassian": 10, "draconic": 11, "kalimag": 12, "gnomish": 13, "troll": 14,
    "gutterspeak": 33, "draenei": 35, "naga": 7,
}
# The murlocs' own: the game's Titan, "Nerglish" in the patch (no player race speaks it).
NERGLISH_LANGUAGE = 9

# Creature types (CreatureType.dbc), for `type` (a beast can be tamed with `tameable`, and skinned).
TYPES = {"beast": 1, "dragonkin": 2, "demon": 3, "elemental": 4, "giant": 5, "undead": 6, "humanoid": 7, "critter": 8,
         "mechanical": 9, "unknown": 10}

CLASSES = {"warrior": 1, "paladin": 2, "hunter": 3, "rogue": 4, "priest": 5, "shaman": 7, "mage": 8, "warlock": 9, "druid": 11}
SKILLS = {
    "first_aid": 129, "cooking": 185, "fishing": 356, "skinning": 393, "mining": 186, "herbalism": 182,
    "leatherworking": 165, "tailoring": 197, "blacksmithing": 164, "alchemy": 171, "engineering": 202,
    "enchanting": 333, "jewelcrafting": 755, "inscription": 773,
}

# Food, drink and bags (ITEMS kinds food, drink, bag) are made like the game's of their level: these.
FOOD = [(1, 787), (5, 4592), (15, 4593), (25, 4594), (35, 6887), (45, 8957)]
DRINK = [(1, 159), (5, 1179), (15, 1205), (25, 1708), (35, 1645), (45, 8766)]
BAGS = [(6, 4496), (8, 4498), (10, 4497), (12, 4499), (14, 4245), (16, 1725)]

# What a vendor sells by default (the game's items): the murlocs' food and drink.
VENDOR_FOOD = [787, 4592, 4593, 4594, 8957, 21552, 159, 1179, 1205, 1708, 1645, 8766]

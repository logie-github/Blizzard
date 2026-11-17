# Wrath++'s races for the allied races module's build_data.py (docs/wrathpp/ALLIED_RACES.md): this file is run in
# build_data's names (BUILD_PROFILE=<this file> WRATHPP_RACES_JSON=<races data from sl_looks.py data> ...), so what it assigns
# is what build_data uses: the ten allied races and the Alliance's High Elf, none of the allied races module's own racials
# (RACIALS: Wrath++'s are made apart) and none of WoW: Forever's changes to the old races (OLD_RACIALS).
import json
import os

RACES = json.load(open(os.environ["WRATHPP_RACES_JSON"]))
WPP_OUT = os.environ.get("WRATHPP_OUT", "")
RACIALS = True          # the Void Elves', Nightborne's, Lightforged's and Zandalari's own (the module's spells and C++ scripts)
OLD_RACIALS = False
if WPP_OUT:
    SQL_OUT = os.path.join(WPP_OUT, "sql", "wrathpp_races_world.sql")
    CLIENT_OUT = os.path.join(WPP_OUT, "client")
CLIENT_NOTE = "Wrath++'s allied races' changes"
SQL_NOTE = "Wrath++'s allied races (the ten, and the High Elf), made by realm/warcraft/wrathpp/tools/races_profile.py"

# Ids: ALL BELOW 22. The client keeps each race's saved choices in CCharacterCreation::m_charPreferences[22][2] (0x00B6B0D0, 176 bytes,
# m_raceIndex right after it): a race id from 22 up writes past it into the client's other statics (the crash of issue 281, at
# SetSelectedRace). So, as mod-allied-races does, the new races take the ids of the game's creatures-only races, which move up:
# the Goblins' row 9 and the creatures' 12 to 21 go to 22 to 32 (MOVED: their rows, looks, hair, features and voices), and the High Elf
# takes 9, the ten allied races 12 to 21. The Worgen and Goblins (mod-worgen-goblin, ids 12 and 9) need that array enlarged first.
VOIDELF, NIGHTBORNE, LIGHTFORGED, ZANDALARI, HIGHMOUNTAIN, DARKIRON, VULPERA, MAGHAR, MECHAGNOME = range(12, 21)   # (21 is free)
HIGHELF = 9
RACE_IDS = (VOIDELF, NIGHTBORNE, LIGHTFORGED, ZANDALARI, HIGHMOUNTAIN, DARKIRON, VULPERA, MAGHAR, MECHAGNOME, HIGHELF)
ALLIANCE_RACES = (VOIDELF, LIGHTFORGED, DARKIRON, MECHAGNOME, HIGHELF)
HORDE_RACES = (NIGHTBORNE, ZANDALARI, HIGHMOUNTAIN, VULPERA, MAGHAR)
FOLDED = {}
# A death knight's face rows need the flag its skins have (0x10; the client's GetSelectionFromContext asks for 0x1 and 0x14), as the ten
# races' do: 17, not the module's 1 (with 1 a death knight of these races has no valid face: the rig's failures, issue 294's neighbours).
FACE_ROW_FLAGS = 17
MOVED = {9: 32, **{old: old + 10 for old in range(12, 22)}}
# ChrRaces' file string, the name the creation screen (its texts, scenes, pictures, Shadowlands' art) knows a race by: today's own
# (the models' folders are another matter; the High Elf's files are the Void Elf's)
CLIENT_FILE_STRING = {12: "VoidElf", 13: "Nightborne", 14: "LightforgedDraenei", 15: "ZandalariTroll", 16: "HighmountainTauren",
                      17: "DarkIronDwarf", 18: "Vulpera", 19: "MagharOrc", 20: "Mechagnome", 9: "HighElf"}
KEY = {VOIDELF: "voidelf", NIGHTBORNE: "nightborne", LIGHTFORGED: "lightforged", ZANDALARI: "zandalari", HIGHMOUNTAIN: "highmountain",
       DARKIRON: "darkiron", VULPERA: "vulpera", MAGHAR: "maghar", MECHAGNOME: "mechagnome", HIGHELF: "highelf"}
BIT = {r: 1 << (r - 1) for r in RACE_IDS}
ALLIANCE_BITS = sum(BIT[r] for r in ALLIANCE_RACES)
HORDE_BITS = sum(BIT[r] for r in HORDE_RACES)

# Where they begin, whose quests, standing, gear and intro camera they have: the closest 3.3.5 race (the user: "draenei to
# draenei and orc to orc").
START = {VOIDELF: DRAENEI, LIGHTFORGED: DRAENEI, DARKIRON: DWARF, MECHAGNOME: GNOME, HIGHELF: NIGHTELF,
         NIGHTBORNE: BLOODELF, ZANDALARI: TROLL, HIGHMOUNTAIN: TAUREN, VULPERA: ORC, MAGHAR: ORC}
# The classes of today's races that 3.3.5 has.
_BLOODELF_CLASSES = (PALADIN, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK)   # (3.3.5's Blood Elves have no warriors)
CLASSES_OF = {
    VOIDELF: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK),
    NIGHTBORNE: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK),
    LIGHTFORGED: (WARRIOR, PALADIN, HUNTER, PRIEST, DK, MAGE),
    ZANDALARI: (WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE, DRUID),
    HIGHMOUNTAIN: (WARRIOR, HUNTER, DK, SHAMAN, DRUID),
    DARKIRON: (WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK, SHAMAN),
    VULPERA: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK, SHAMAN),
    MAGHAR: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK, SHAMAN),
    MECHAGNOME: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK),
    HIGHELF: (WARRIOR,) + _BLOODELF_CLASSES,
}
# The races of 3.3.5 that have each class, by side (3.3.5's own: playercreateinfo): where a class's gear, action bar and
# skills come from when the start race hasn't it: the start race's if it has, else the first of the side's that does.
_HAS = {HUMAN: (WARRIOR, PALADIN, ROGUE, PRIEST, DK, MAGE, WARLOCK), DWARF: (WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK),
        NIGHTELF: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, DRUID), GNOME: (WARRIOR, ROGUE, MAGE, WARLOCK, DK),
        DRAENEI: (WARRIOR, PALADIN, HUNTER, PRIEST, DK, SHAMAN, MAGE),
        ORC: (WARRIOR, HUNTER, ROGUE, DK, SHAMAN, WARLOCK), UNDEAD: (WARRIOR, ROGUE, PRIEST, DK, MAGE, WARLOCK),
        TAUREN: (WARRIOR, HUNTER, DK, SHAMAN, DRUID), TROLL: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE),
        BLOODELF: _BLOODELF_CLASSES}
_ALLIANCE_ORDER, _HORDE_ORDER = (HUMAN, DRAENEI, NIGHTELF, DWARF, GNOME), (ORC, TROLL, BLOODELF, UNDEAD, TAUREN)
TEMPLATE = {}
for _race in RACE_IDS:
    _order = [START[_race]] + [r for r in (_ALLIANCE_ORDER if _race in ALLIANCE_RACES else _HORDE_ORDER) if r != START[_race]]
    TEMPLATE[_race] = {c: next(r for r in _order if c in _HAS[r]) for c in CLASSES_OF[_race]}
EXTRA_CLASSES = {}
STATS_FROM = {VOIDELF: BLOODELF, NIGHTBORNE: NIGHTELF, LIGHTFORGED: DRAENEI, ZANDALARI: TROLL, HIGHMOUNTAIN: TAUREN,
              DARKIRON: DWARF, VULPERA: GNOME, MAGHAR: ORC, MECHAGNOME: GNOME, HIGHELF: BLOODELF}
MODEL_FROM = dict(STATS_FROM)                          # whose model rows (scale, collision, sounds) theirs are copied from
PREFIX = {VOIDELF: "Ve", NIGHTBORNE: "Nb", LIGHTFORGED: "Ld", ZANDALARI: "Za", HIGHMOUNTAIN: "Ht", DARKIRON: "Di",
          VULPERA: "Vu", MAGHAR: "Mo", MECHAGNOME: "Mg", HIGHELF: "He"}
NAME = {VOIDELF: "Void Elf", NIGHTBORNE: "Nightborne", LIGHTFORGED: "Lightforged Draenei", ZANDALARI: "Zandalari Troll",
        HIGHMOUNTAIN: "Highmountain Tauren", DARKIRON: "Dark Iron Dwarf", VULPERA: "Vulpera",
        MAGHAR: "Mag'har Orc", MECHAGNOME: "Mechagnome", HIGHELF: "High Elf"}
# The intro's narration: the user's own MP3s for the four of Legion's and BfA's the allied races module has, wago.tools' music of
# the Highmountain's flythrough for theirs (sound/music/legion/mus_735_ar_rtc_highmountaintauren_flythrough.mp3); the rest
# have the start race's flight without a voice.
NARRATION = {VOIDELF: "VoidElfNarration.mp3", NIGHTBORNE: "NightborneNarration.mp3", LIGHTFORGED: "LightforgedDraeneiNarration.mp3",
             ZANDALARI: "ZandalariTrollNarration.mp3", HIGHMOUNTAIN: "HighmountainTaurenNarration.mp3"}
FEATURE_LABELS = {VOIDELF: ("FEATURES", "FEATURES", "NORMAL"), NIGHTBORNE: ("FEATURES", "FEATURES", "NORMAL"),
                  LIGHTFORGED: ("FEATURES", "HORNS", "NORMAL"), ZANDALARI: ("TUSKS", "TUSKS", "NORMAL"),
                  HIGHMOUNTAIN: ("HORNS", "HORNS", "NORMAL"),
                  DARKIRON: ("FEATURES", "FEATURES", "NORMAL"), VULPERA: ("FEATURES", "FEATURES", "NORMAL"),
                  MAGHAR: ("FEATURES", "FEATURES", "NORMAL"), MECHAGNOME: ("FEATURES", "FEATURES", "NORMAL"),
                  HIGHELF: ("FEATURES", "FEATURES", "NORMAL")}
CLONED = {}
# New rows' ids: Wrath++ has none of the other modules' rows, and eleven races' looks are many.
ID_SECTIONS_END = 1999999
_n = len(RACE_IDS)
ID_SEQUENCE = {r: 9011 + i for i, r in enumerate(RACE_IDS)}
ID_CAMERA = dict(ID_SEQUENCE)
ID_NARRATION = {r: 910001 + i for i, r in enumerate(RACE_IDS)}
ID_DISPLAY = {r: (33001 + 2 * i, 33002 + 2 * i) for i, r in enumerate(RACE_IDS)}
ID_MODEL = {r: (3601 + 2 * i, 3602 + 2 * i) for i, r in enumerate(RACE_IDS)}


# --- the new races' racials (3.3.5's auras: the retail ones as near as they come; docs/wrathpp/ALLIED_RACES.md) ------------------
# Ids clear of the module's own (98711 to 98734) and Forever's (98800 on).
NEW = dict(ancestral_call=98760, brawn=98761, forged_in_flames=98762, fireblood=98763, mountaineer=98764, bull_rush=98765,
           brush_it_off=98766, haymaker=98767, bag_of_tricks=98768, nose_for_trouble=98769, rummaging=98770,
           combat_analysis=98771, skillful_scavenger=98772)
_WARRIOR, _PALADIN, _HUNTER, _ROGUE, _PRIEST, _DKM, _SHAMAN, _MAGE, _WARLOCK, _DRUID = 1, 2, 4, 8, 16, 32, 64, 128, 256, 1024
_MANA = _PALADIN | _HUNTER | _PRIEST | _MAGE | _WARLOCK
# What each learns at creation: the new spells above and the game's own racials that fit (Hardiness 20573, Command 20576,
# Diplomacy 20599, Underwater Breathing 5227, Endurance 20550, Escape Artist 20589, Engineering Specialization 20593, the
# Blood Elves' Arcane Torrent by class, Magic Resistance 822 and Arcane Affinity 28877).
RACIAL_LEARN = [
    (BIT[MAGHAR], NEW["ancestral_call"], "Mag'har Orc - Ancestral Call"), (BIT[MAGHAR], NEW["brawn"], "Mag'har Orc - Brawn"),
    (BIT[MAGHAR], 20573, "Mag'har Orc - Hardiness"), (BIT[MAGHAR], 20576, "Mag'har Orc - Command"),
    (BIT[DARKIRON], NEW["fireblood"], "Dark Iron Dwarf - Fireblood"), (BIT[DARKIRON], NEW["forged_in_flames"], "Dark Iron Dwarf - Forged in Flames"),
    (BIT[HIGHMOUNTAIN], NEW["mountaineer"], "Highmountain Tauren - Mountaineer"), (BIT[HIGHMOUNTAIN], NEW["bull_rush"], "Highmountain Tauren - Bull Rush"),
    (BIT[HIGHMOUNTAIN], 20550, "Highmountain Tauren - Endurance"),
    (BIT[VULPERA], NEW["bag_of_tricks"], "Vulpera - Bag of Tricks"), (BIT[VULPERA], NEW["nose_for_trouble"], "Vulpera - Nose for Trouble"),
    (BIT[VULPERA], NEW["rummaging"], "Vulpera - Rummaging"), (BIT[VULPERA], 20589, "Vulpera - Escape Artist"),
    (BIT[MECHAGNOME], NEW["combat_analysis"], "Mechagnome - Combat Analysis"), (BIT[MECHAGNOME], NEW["skillful_scavenger"], "Mechagnome - Skillful Scavenger"),
    (BIT[MECHAGNOME], 20589, "Mechagnome - Escape Artist"), (BIT[MECHAGNOME], 20593, "Mechagnome - Engineering Specialization"),
    (BIT[HIGHELF], 822, "High Elf - Magic Resistance"), (BIT[HIGHELF], 28877, "High Elf - Arcane Affinity"),
    (BIT[HIGHELF], 28730, "High Elf - Arcane Torrent (mana)", _MANA), (BIT[HIGHELF], 25046, "High Elf - Arcane Torrent (energy)", _ROGUE),
    (BIT[HIGHELF], 50613, "High Elf - Arcane Torrent (runic power)", _DKM),
]


def RACIAL_HOOK(spell, no_cost, sql, client, columns, by_id, schools):
    """The new races' spells' rows (spell() makes a row from a game spell: 130 an instant self spell, 20557 a passive, 20549 War
    Stomp, 20594 Stoneform) and what the server needs to run them (none of them has a script: auras and the game's own effects)."""
    N = NEW
    passive = dict(RecoveryTime=0)
    rows = [
        spell(130, N["ancestral_call"], "Ancestral Call", "Racial",
              "Invoke the strength of your ancestors, increasing damage done by 10% for 12 sec. 2 min cooldown.", "Damage done increased by 10%.",
              SpellIconID=1119, Effect_1=6, EffectAura_1=79, EffectBasePoints_1=9, EffectDieSides_1=1, EffectMiscValue_1=127,
              DurationIndex=29, RecoveryTime=120000, **dict(no_cost, Attributes=0x10)),
        spell(20557, N["brawn"], "Brawn", "Racial Passive", "Critical strikes deal 2% more damage and healing.", "",
              SpellIconID=2178, EffectAura_1=163, EffectBasePoints_1=1, EffectDieSides_1=1, EffectMiscValue_1=127),
        spell(20557, N["forged_in_flames"], "Forged in Flames", "Racial Passive", "Fire damage taken reduced by 10%.", "",
              SpellIconID=1218, EffectAura_1=87, EffectBasePoints_1=-11, EffectDieSides_1=1, EffectMiscValue_1=4),
        spell(20594, N["fireblood"], "Fireblood", "Racial",
              "Removes all poison, disease, curse, magic and bleed effects and reduces all damage taken by 10% for 8 sec. 3 min cooldown.", "",
              SpellIconID=1618),
        spell(20557, N["mountaineer"], "Mountaineer", "Racial Passive", "Stamina increased by 3%.", "",
              SpellIconID=2290, EffectAura_1=137, EffectBasePoints_1=2, EffectDieSides_1=1, EffectMiscValue_1=2),
        spell(130, N["bull_rush"], "Bull Rush", "Racial", "Charge ahead, increasing run speed by 30% for 3 sec. 3 min cooldown.", "Run speed increased by 30%.",
              SpellIconID=1337, Effect_1=6, EffectAura_1=31, EffectBasePoints_1=29, EffectDieSides_1=1,
              DurationIndex=27, RecoveryTime=180000, **dict(no_cost, Attributes=0x10)),
        spell(20549, N["bag_of_tricks"], "Bag of Tricks", "Racial",
              "Throw a bag of tricks that bursts over nearby enemies, dealing Physical damage to those within 8 yards. 3 min cooldown.", "",
              SpellIconID=2018, Effect_1=2, EffectAura_1=0, EffectBasePoints_1=29, EffectDieSides_1=1, EffectRealPointsPerLevel_1=3.0,
              ImplicitTargetA_1=22, ImplicitTargetB_1=15, EffectRadiusIndex_1=14, EffectMechanic_1=0, Mechanic=0,
              Effect_2=0, EffectAura_2=0, EffectBasePoints_2=0, EffectDieSides_2=0, EffectTriggerSpell_2=0, ImplicitTargetA_2=0, ImplicitTargetB_2=0,
              RecoveryTime=180000, DurationIndex=0, SchoolMask=1, DispelType=0, CastingTimeIndex=1, StartRecoveryCategory=133,
              StartRecoveryTime=1500, Attributes=0x10),
        spell(20557, N["nose_for_trouble"], "Nose for Trouble", "Racial Passive", "Stealth detection increased.", "",
              SpellIconID=1666, EffectAura_1=30, EffectBasePoints_1=9, EffectDieSides_1=1, EffectMiscValue_1=0),
        spell(20557, N["rummaging"], "Rummaging", "Racial Passive", "Skinning skill increased by 10.", "",
              SpellIconID=2301, EffectAura_1=98, EffectBasePoints_1=9, EffectDieSides_1=1, EffectMiscValue_1=393),
        spell(20557, N["combat_analysis"], "Combat Analysis", "Racial Passive", "Critical strike chance increased by 2%.", "",
              SpellIconID=2128, EffectAura_1=52, EffectBasePoints_1=1, EffectDieSides_1=1, EffectMiscValue_1=0,
              Effect_2=6, EffectAura_2=57, EffectBasePoints_2=1, EffectDieSides_2=1, ImplicitTargetA_2=1),
        spell(20557, N["skillful_scavenger"], "Skillful Scavenger", "Racial Passive", "Engineering skill increased by 15.", "",
              SpellIconID=2065, EffectAura_1=98, EffectBasePoints_1=14, EffectDieSides_1=1, EffectMiscValue_1=202),
    ]
    sql.comment("Their racials, the new races' (Wrath++, docs/wrathpp/ALLIED_RACES.md): Ancestral Call, Brawn; Fireblood, Forged in Flames;\n"
                "Mountaineer, Bull Rush; Bag of Tricks, Nose for Trouble, Rummaging; Combat Analysis, Skillful Scavenger.")
    return rows

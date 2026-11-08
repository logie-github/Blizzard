# SPDX-License-Identifier: GPL-3.0-or-later
"""The stories tools/murloc/compile.py makes, a race's profile each: its race and phases, its chapters'
folder, its ids, the tables its SQL fills, how its people's words read, the looks and sounds its
chapters may name. Data only.

  MURLOC: the murlocs' story (tools/murloc/ch*.py): race 19, phase 1024, ids 976000-979999.
  NAGA:   the naga's story (tools/naga/ch*.py): race 20, phase 2048, ids 990000-995199 (tools/naga/SCHEMA.md).

The two stories share Azshara (the murlocs' chapter 10 and all of the naga's), so their phases must
never cross there: each story's people carry its own race phase and its own story bits only, and the
naga's compile is given the murlocs' bits zone by zone and takes others (compile.check_apart checks
both stories' rows)."""
import importlib.util
import os

import common as K

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)


def _names(path, name):
    """The dict [name] of the Python file [path] (tools/naga/sounds.py's SOUNDS...), or {} without it."""
    if not os.path.exists(path):
        return {}
    spec = importlib.util.spec_from_file_location("story_names_" + os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(getattr(mod, name, {}))


class Profile:
    def __init__(self, **values):
        self.__dict__.update(values)

    def __repr__(self):
        return f"Profile({self.key})"


MURLOC = Profile(
    key="murloc", who="the murlocs", race=19, RACE_BIT=K.MURLOC_BIT, RACE_PHASE=K.RACE_PHASE,
    folder=HERE, sql_file="murloc_story.sql", steps_file="murloc_naga_murloc.steps",
    title="The murlocs' questline (mod-murloc-naga): made by tools/murloc/compile.py from tools/murloc/ch*.py; edit those.",
    NPC_BASE=K.NPC_BASE, NPC_END=K.NPC_END, GO_BASE=K.GO_BASE, GO_END=K.GO_END,
    OLD_GO_BASE=K.OLD_GO_BASE, OLD_GO_END=K.OLD_GO_END,
    QUEST_BASE=K.QUEST_BASE, QUEST_END=K.QUEST_END, ITEM_BASE=K.ITEM_BASE, ITEM_END=K.ITEM_END,
    SPAWN_BASE=K.SPAWN_BASE, SPAWN_END=K.SPAWN_END, GO_SPAWN_BASE=K.GO_SPAWN_BASE, GO_SPAWN_END=K.GO_SPAWN_END,
    GO_DISPLAY_BASE=K.GO_DISPLAY_BASE, GO_DISPLAY_END=K.GO_DISPLAY_END,
    PHASE_SPELL_BASE=K.PHASE_SPELL_BASE, PHASE_SPELL_END=K.SPELL_BASE - 1, SPELL_BASE=K.SPELL_BASE, SPELL_END=K.SPELL_END,
    TRAINER_BASE=K.TRAINER_BASE, GRAVEYARD_BASE=K.GRAVEYARD_BASE, GRAVEYARD_END=K.GRAVEYARD_END,
    DISPLAY_BASE=None, DISPLAY_END=None, EXTRA_BASE=None, EXTRA_END=None,      # (no new looks of its own)
    KEPT_ENTRIES={},
    LOOT_COMMENT=K.LOOT_COMMENT, COMMENT="mod-murloc-naga",
    CAMP_NPC_BASE=K.CAMP_NPC_BASE, CAMP_NPC_END=K.CAMP_NPC_END,
    tables=dict(story="murloc_naga_story", learn="murloc_naga_story_learn", graveyards="murloc_naga_graveyards",
                carry="murloc_naga_story_carry", memories=None),
    # Their words: Nerglish (Blizzard's translator), the readable ones none; another race's garbled.
    own_language="nerglish", readable=set(), translate=True,
    PHASE_BITS=list(K.STORY_PHASE_BITS), ZONE_BITS={}, MEMORY_BITS={},
    race_spells=None, race_phase_spell=98880,   # (its race phase: tools/build_data.py's phase_murloc, Murloc Kinship)
    world_areas=[], world_owned_areas=(148, 331),
    LOOKS=dict(K.LOOKS), SOUNDS=dict(K.SOUNDS), SIDES=dict(K.SIDES),
    looks_own_range=None, sounds_own_range=None,
    phase_spell_name="Murloc Tidings",
    strict=False,                      # (its chapters were written before looks and sounds were checked)
)


# The naga's own: tools/naga/looks.py and tools/naga/sounds.py (the naga's assets: their converted models'
# looks, CreatureDisplayInfo 40000-40199; the sounds fetched from warcraft.wiki.gg, SoundEntries 995000-995199).
NAGA_LOOKS = {
    # the game's naga (CreatureDisplayInfo; the scale is the look's own: a size= on someone says how big they are)
    "naga_male": 4036, "siren": 4980, "sorceress": 4973, "naga_warrior": 11269, "naga_lord": 4762, "sea_witch": 4981,
    "myrmidon": 6747, "spitelash_warrior": 6747, "spitelash_siren": 11266, "spitelash_myrmidon": 11265,
    "spitelash_battlemaster": 11271, "spitelash_screamer": 11268, "spitelash_serpent_guard": 11267,
    "spitelash_enchantress": 11261, "spitelash_raider": 11257,
    "coilfang_siren": 18392, "coilfang_myrmidon": 18389, "darkspine_siren": 22870, "vashjir_guard": 20200,
    "naga_player_male": 17402, "naga_player_female": 17403,
    # Warcraft III's people as the 3.3.5 client has them (bible 18.6)
    "vashj": 20748, "vashj_tall": 29545, "illidan": 21135, "maiev": 20628, "kaelthas": 20023, "akama": 20681,
    "malfurion": 15399, "tyrande": 7274, "magtheridon": 18527, "kiljaeden": 23200, "arthas": 22235,
    "anubarak": 27856, "guldan": 16642, "dragon_turtle": 21457,
    "felguard": 14255, "highborne_apparition": 10702, "highborne_lichling": 10700, "makrinni": 2600,
}
NAGA_LOOKS.update(_names(os.path.join(TOOLS, "naga", "looks.py"), "LOOKS"))
NAGA_SOUNDS = {
    # Lady Vashj's Serpentshrine lines, the 3.3.5 client's own (bible 5.3)
    "vashj_intro": 11531, "vashj_aggro1": 11532, "vashj_aggro2": 11533, "vashj_aggro3": 11534, "vashj_aggro4": 11535,
    "vashj_bowshot1": 11536, "vashj_bowshot2": 11537, "vashj_phase1": 11538, "vashj_phase2": 11539, "vashj_phase3": 11540,
    "vashj_slay1": 11541, "vashj_slay2": 11542, "vashj_slay3": 11543, "vashj_death": 11544,
    "vashj_attack": 11616, "vashj_wound": 11617, "vashj_wound_crit": 11618,
}
NAGA_SOUNDS.update(_names(os.path.join(TOOLS, "naga", "sounds.py"), "SOUNDS"))

NAGA = Profile(
    key="naga", who="the naga", race=20, RACE_BIT=1 << 19, RACE_PHASE=2048,
    folder=os.path.join(TOOLS, "naga"), sql_file="naga_story.sql", steps_file="murloc_naga_naga.steps",
    title="The naga's questline (mod-murloc-naga): made by tools/murloc/compile.py from tools/naga/ch*.py; edit those.",
    # Ids (checked free across every module, the core and the client): creatures, gossip menus, texts and
    # trainers 990000-991999 (the last 400: unseen helpers, quiz menus); objects 1990000-1991999 (a scene
    # list's id is an object's entry * 1000 + n, under 2^31); quests 992000-992599; items 993000-993799;
    # spells 994000-994399; spawns 9900000-9929999, objects' 9930000-9939999; graveyards 9900-9939; object
    # looks 10400-10599; new looks (display_extra) CreatureDisplayInfo 40200-40299 and
    # CreatureDisplayInfoExtra 25000-25099 (40000-40199 are tools/naga/looks.py's, the assets'); SoundEntries
    # 995000-995199 are tools/naga/sounds.py's (the assets').
    NPC_BASE=990000, NPC_END=991999, GO_BASE=1990000, GO_END=1991999, OLD_GO_BASE=None, OLD_GO_END=None,
    QUEST_BASE=992000, QUEST_END=992599, ITEM_BASE=993000, ITEM_END=993799,
    SPAWN_BASE=9900000, SPAWN_END=9929999, GO_SPAWN_BASE=9930000, GO_SPAWN_END=9939999,
    GO_DISPLAY_BASE=10400, GO_DISPLAY_END=10599,
    PHASE_SPELL_BASE=994010, PHASE_SPELL_END=994199, SPELL_BASE=994200, SPELL_END=994399,
    TRAINER_BASE=990000, GRAVEYARD_BASE=9900, GRAVEYARD_END=9939,
    DISPLAY_BASE=40200, DISPLAY_END=40299, EXTRA_BASE=25000, EXTRA_END=25099,
    # The retired Darkshore camp's people who are the story's (their creature entries kept: tools/content.py).
    KEPT_ENTRIES={"szaria": 975017, "ssaveth": 975018, "vyssa": 975019},
    LOOT_COMMENT="mod-murloc-naga: naga story", COMMENT="mod-murloc-naga: naga story",
    CAMP_NPC_BASE=None, CAMP_NPC_END=None,
    tables=dict(story="naga_story", learn="naga_story_learn", graveyards="naga_story_graveyards", carry="naga_story_carry",
                memories="naga_story_memories"),
    # Their words are readable (bible 4.1): their own tongue, Nazja (the game's Universal), the memories'
    # (Universal: a memory is understood) and Orcish (they speak it); other races' garbled as the game does.
    own_language="nazja", readable={"nazja", "naga", "universal", "orcish"}, translate=False,
    # Story bits: the murlocs' sixteen, less those the murlocs use in a zone (given to the compile); in
    # Azshara also the game's 16 to 512 (nothing of the game's uses them there: no spawn, no spell_area) and
    # the bits other modules use only in their own towns (Brill's 32768 to 131072, Wrath Remix's 32768 on its
    # own realm). compile.py checks the game's world for each one it gives.
    PHASE_BITS=list(K.STORY_PHASE_BITS), ZONE_BITS={16: [16, 32, 64, 128, 256, 512, 32768, 65536, 131072]},
    # The memories' three bits (bible 18.2): the game's 2, 4 and 8, never the murlocs' (their bits are 4096 up).
    MEMORY_BITS={"A": 2, "B": 4, "C": 8},
    # Their race phases (spell_area, by zone): Azshara alone (the naga's phase, no world) until a chapter's
    # alone_until quest; then the world's and theirs. The marker is the module's while reliving a memory (every
    # phase row of theirs needs it absent); the fade, a screen going dark as one goes in or out.
    race_spells=dict(alone=994000, world=994001, marker=994002, fade=994003),
    race_phase_spell=0,
    world_areas=[1237],                # Valormok: the world and theirs from the first login (bible 18.2)
    world_owned_areas=(),
    LOOKS=dict(K.LOOKS, **NAGA_LOOKS), SOUNDS=dict(K.SOUNDS, **NAGA_SOUNDS),
    # (ally: the Horde's own, friendly to a naga and hostile to monsters and the Alliance: turrets, allies in a fight)
    SIDES=dict(K.SIDES, ally=1619),
    looks_own_range=(40000, 40299), sounds_own_range=(995000, 995199),
    phase_spell_name="Naga Tidings",
    # ScreenEffect.dbc: the game's own flashback look (Haunting Memories, 50153: "Arthas Memory Events"), and
    # the dark of a transition (Ebon Hold's): a memory's screen, and the fade in and out.
    MEMORY_SCREEN=21, FADE_SCREEN=201,
    strict=True,                       # every look and sound named must be the game's (or the assets' ranges)
)

PROFILES = {"murloc": MURLOC, "naga": NAGA}

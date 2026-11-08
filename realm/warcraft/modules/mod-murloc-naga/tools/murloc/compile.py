# SPDX-License-Identifier: GPL-3.0-or-later
"""A race's questline, compiled: the murlocs' (tools/murloc/ch*.py) or the naga's (tools/naga/ch*.py), written
as tools/murloc/SCHEMA.md (and tools/naga/SCHEMA.md) says, made the world database's rows and the game's
table rows, checked as it goes. A story is a race's profile (tools/murloc/profiles.py: its race, phases, ids,
tables and words).

    import compile as S
    story = S.Story(S.load(), world, dbc, ground)    # world(table) -> rows of the core's dumps,
    tables, client = story.build()                   # dbc(name) -> a DBC, ground(map, x, y) -> z
    sql = S.sql(tables)                              # the SQL (every row the module's own, replaced)
    naga = S.Story(S.load(NAGA.folder, prefix="naga"), world, dbc, ground, profile=NAGA,
                   reserved=S.bits_by_zone(story))   # the naga's, clear of the murlocs' bits
    S.check_apart([story, naga], area)               # neither story's people seen by the other race

Words: a murloc's are run through Blizzard's Nerglish translator (tools/nerglish.py); a naga's are
readable (their own tongue, the memories', Orcish); another race's are garbled as the game garbles a
language one doesn't know (garble.py), as quest and gossip windows show text as it's written. The goal
line of each quest stays English.

What the scenes do (SCHEMA.md's beats) is SmartAI: a beat list is a timed action list of the creature
it's said by; a beat by someone else is that one's own list, started by data the first sets on it."""
import glob
import importlib.util
import math
import os
import re
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import common as K  # noqa: E402
import nerglish  # noqa: E402
from garble import Garbler  # noqa: E402
from profiles import MURLOC, NAGA, PROFILES  # noqa: E402,F401


class StoryError(Exception):
    pass


def load(folder=HERE, upto=None, prefix="murloc"):
    """The chapters, in order (ch1_*.py, ch2_*.py ...): each a dict of its file's names; [upto]: the last
    chapter released (the ones after it are still being written)."""
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "ch*.py")), key=lambda p: int(re.match(r"ch(\d+)", os.path.basename(p)).group(1))):
        if upto is not None and int(re.match(r"ch(\d+)", os.path.basename(path)).group(1)) > upto:
            continue
        spec = importlib.util.spec_from_file_location(f"{prefix}_" + os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out.append({k: getattr(mod, k) for k in ("CHAPTER", "PLACES", "NPCS", "OBJECTS", "ITEMS", "QUESTS", "TOWNS", "AURAS",
                                                  "SPAWNS", "GRAVEYARDS", "MEMORIES") if hasattr(mod, k)})
    return out


# SmartAI's ids (the core's SmartScriptMgr.h)
EV_UPDATE_OOC, EV_OOC_LOS, EV_ACCEPTED_QUEST, EV_REWARD_QUEST, EV_DATA_SET, EV_GOSSIP_SELECT = 1, 10, 19, 20, 38, 62
EV_UPDATE_IC, EV_RECEIVE_EMOTE, EV_GOSSIP_HELLO, EV_RESET = 0, 22, 64, 25
A_REMOVE_AURA, A_SUMMON_GO, A_ADD_AURA = 28, 50, 75
A_SET_FACTION, A_EVADE, EV_HEALTH_PCT = 2, 24, 2
A_TALK, A_SOUND, A_EMOTE, A_CAST, A_SUMMON, A_AREA_EXPLORED, A_EMOTE_STATE, A_FOLLOW = 1, 4, 5, 11, 12, 15, 17, 29
A_KILLED_MONSTER, A_DESPAWN, A_SET_DATA, A_ADD_ITEM, A_REMOVE_ITEM, A_SET_RUN, A_TELEPORT = 33, 41, 45, 56, 57, 59, 62
A_ORIENTATION, A_MOVE_TO, A_CLOSE_GOSSIP, A_ACTIONLIST, A_JUMP, A_MUSIC = 66, 69, 72, 80, 97, 216
T_SELF, T_INVOKER, T_POSITION, T_CLOSEST_CREATURE = 1, 7, 8, 19
A_MORPH, A_SET_COUNTER, A_ALLOW_COMBAT_MOVE, A_SEND_GOSSIP_MENU, A_SET_SCALE, A_SET_HOVER = 3, 63, 21, 98, 227, 207
EV_MOVEMENT_INFORM, EV_JUST_SUMMONED, EV_COUNTER_SET, EV_SUMMONED_UNIT_DIES, POINT_MOTION = 34, 54, 77, 82, 8
T_PLAYER_RANGE = 17
A_CROSS_CAST, A_INVOKER_CAST = 86, 134         # (another casts on their own; the invoker casts)
T_CLOSEST_PLAYER = 21                       # (target_param1: the farthest, yards)
# Unit flags: not attackable, immune to players and to creatures (an "untouchable" canon figure: bible 18.3)
UNTOUCHABLE = 0x2 | 0x100 | 0x200
CHAT = {"say": 12, "yell": 14, "whisper": 15, "emote_text": 16}
# Quest statuses as bits (spell_area's quest_start_status / quest_end_status: the core gives the spell
# while the quest's status is one of them, for the end quest too: SpellArea::IsFitToRequirements)
REWARDED, IN_LOG = 1 << 6, (1 << 1) | (1 << 3)
NOT_REWARDED = (1 << 6) - 1             # none, complete, unavailable, incomplete, available, failed

NPCFLAG = {"gossip": 1, "quest": 2, "trainer": 16, "class_trainer": 32, "profession_trainer": 64, "vendor": 128,
           "repair": 4096, "innkeeper": 65536, "banker": 131072, "auctioneer": 2097152, "stable": 4194304}
# Gossip options of a role: (option type, npc flag, icon, what the player says)
ROLE_OPTIONS = {"banker": (9, 131072, 6, "I want to look in the log."), "auctioneer": (13, 2097152, 6, "Show me what's for sale."),
                "stable": (14, 4194304, 0, "Look after my animals.")}
# The story's auras (AURAS): their kinds, as SPELL_AURA_* (tools/build_data.py makes the spells)
AURA_KINDS = {"mark": 4, "disguise": 56, "slow": 33, "stun": 12, "root": 26, "speed": 31, "sleep": 12, "stats": 137, "screen": 260}
SPELL_AURA_PHASE, SPELL_AURA_SCREEN_EFFECT, SPELL_AURA_DUMMY = 261, 260, 4
# What the naga's models can play (bible 4.2, their sequence lists: Lady Vashj's, the classic naga's, the naga
# lord's, the sirens' and the playable naga's); any other emote falls back to standing still (AnimationData).
NAGA_EMOTES = {"talk", "roar", "battle_roar", "spell", "omnicast", "work", "attack", "attack2h", "wound", "throw", "drown",
               "stun", "ready1h", "ready_bow"}
NAGA_STATES = {"none", "work", "stun", "dead", "channel", "channel_directed", "drowned", "swim_idle", "ready_thrown",
               "ready_bow", "talk", "roar"}
# What the playable naga's two models play besides (tools/naga_emotes.py merges them in as the patch is made): the
# player's naga, and the game's naga people drawn with them (the Coilfang's sirens and myrmidons, every look of
# CreatureModelData 2353 and 2354).
PLAYABLE_NAGA_EMOTES = NAGA_EMOTES | {"bow", "wave", "cheer", "exclamation", "question", "applaud", "beg", "chicken", "flex",
                                      "kiss", "laugh", "laugh_nosheathe", "shout", "cry", "shy", "dance", "salute", "eat",
                                      "eat_nosheathe", "rude", "train", "yes", "no", "kneel", "point", "point_nosheathe"}
PLAYABLE_NAGA_STATES = NAGA_STATES | {"sit", "kneel", "sleep", "dance", "eat", "laugh"}
STAT = {"agi": 3, "str": 4, "int": 5, "spi": 6, "sta": 7, "def": 12, "dodge": 13, "parry": 14, "hit": 31, "crit": 32,
        "ap": 38, "sp": 45, "mp5": 43, "haste": 36, "expertise": 37, "armor_pen": 44}
WEAPONS = {  # kind: (subclass, inventory type)
    "axe": (0, 13), "axe2h": (1, 17), "bow": (2, 15), "gun": (3, 26), "mace": (4, 13), "mace2h": (5, 17),
    "polearm": (6, 17), "spear": (6, 17), "sword": (7, 13), "sword2h": (8, 17), "staff": (10, 17), "fist": (13, 13),
    "dagger": (15, 13), "thrown": (16, 25), "crossbow": (18, 26), "wand": (19, 26), "fishing_pole": (20, 17),
}
SLOTS = {"head": 1, "shoulder": 3, "chest": 5, "waist": 6, "legs": 7, "feet": 8, "wrist": 9, "hands": 10, "back": 16}
MATERIALS = {"cloth": 1, "leather": 2, "mail": 3, "plate": 4}


def _poly(x, y, r, n=8):
    return [(round(x + r * math.cos(2 * math.pi * i / n)), round(y + r * math.sin(2 * math.pi * i / n))) for i in range(n)]


class Story:
    def __init__(self, chapters, world, dbc, ground, race_phase_spell=0, area=None, profile=MURLOC, reserved=None, water=None):
        self.chapters = chapters
        self.W = world
        self.D = dbc
        self.ground = ground
        self.water = water              # water(map, x, y) -> the water's height or None (a sky placement over the sea)
        self.area = area                # area(map, x, y) -> AreaTable id (the zone a phase is given in)
        self.race_phase_spell = race_phase_spell or profile.race_phase_spell
        self.P = profile
        # {zone: bits} another story's people carry there (the murlocs', for the naga's compile): never ours too
        self.reserved = {z: set(b) for z, b in (reserved or {}).items()}
        self.errors = []
        lw = self.D("LanguageWords")
        self.garbler = Garbler([(r[1], lw.s(r[2])) for r in lw.rows])
        self.tables = {}
        self.client = {}
        self.next_option = {}
        self.equipped = set()          # creatures with creature_equip_template rows (their spawns hold them)

    # -- small things --------------------------------------------------------------------------
    def err(self, where, what):
        self.errors.append(f"{where}: {what}")

    def row(self, table, **values):
        self.tables.setdefault(table, []).append(values)

    def option_words(self, text, language):
        """A gossip option's words: what the player says or does, so readable in a story whose people's words are
        (the naga's: whoever they're speaking to); in the murlocs', in the person's language as it's shown."""
        return self.words(text, language if self.P.translate else self.P.own_language)

    def words(self, text, language):
        """[text] as one of the story's race reads it, said in [language]: a murloc's own (Nerglish) translated,
        a naga's own (and the memories', and Orcish) as written, another race's garbled."""
        if not text:
            return ""
        if language is None:
            language = self.P.own_language
        if language == "nerglish" and self.P.translate:
            return nerglish.translate(text)
        if language in self.P.readable:
            return text
        lang = K.LANGUAGES.get(language)
        if lang is None:
            raise StoryError(f"no language {language!r}")
        return self.garbler.text(text, lang)

    # -- names ---------------------------------------------------------------------------------
    def qualify(self, chapter, key):
        if isinstance(key, int) or key is None:
            return key
        return key if ":" in key else f"{chapter}:{key}"

    def index(self):
        self.places, self.npcs, self.objects, self.items, self.quests = {}, {}, {}, {}, {}
        self.auras, self.extra_spawns, self.graveyards, self.memories = {}, [], [], {}
        self.chapter_of = {}
        for ch in self.chapters:
            c = ch["CHAPTER"]["key"]
            m = ch["CHAPTER"].get("map", K.MAP_KALIMDOR)
            for k, v in ch.get("PLACES", {}).items():
                self.places[f"{c}:{k}"] = (m, v)
            for d in ch.get("SPAWNS", []):
                self.extra_spawns.append(dict(d, chapter=c))
            for d in ch.get("GRAVEYARDS", []):
                self.graveyards.append(dict(d, chapter=c))
            for kind, store in (("NPCS", self.npcs), ("OBJECTS", self.objects), ("ITEMS", self.items), ("QUESTS", self.quests),
                                ("AURAS", self.auras), ("MEMORIES", self.memories)):
                for d in ch.get(kind, []):
                    key = f"{c}:{d['key']}"
                    if key in store:
                        self.err(key, f"two {kind.lower()} with the key {d['key']!r}")
                    store[key] = dict(d, key=key, chapter=c)
                    self.chapter_of[key] = ch["CHAPTER"]

    def assign(self):
        P = self.P

        def ids(store, base, end, what):
            out = {}
            for n, key in enumerate(store):
                if base + n > end:
                    raise StoryError(f"too many {what} ({len(store)})")
                out[key] = base + n
            return out
        # (a person of the story who has an entry already: one of the retired Darkshore camp's, P.KEPT_ENTRIES)
        kept = {k: d["entry"] for k, d in self.npcs.items() if d.get("entry")}
        for k, e in kept.items():
            if e not in P.KEPT_ENTRIES.values():
                self.err(k, f"its entry {e} isn't one this story keeps ({sorted(P.KEPT_ENTRIES.values())})")
        if len(set(kept.values())) != len(kept):
            self.err("the story", "two people with one entry")
        self.npc_id = ids([k for k in self.npcs if k not in kept], P.NPC_BASE, P.NPC_END - 400, "creatures")  # (the last 400: triggers)
        self.npc_id.update(kept)
        self.go_id = ids(self.objects, P.GO_BASE, P.GO_END, "objects")
        self.quest_id = ids(self.quests, P.QUEST_BASE, P.QUEST_END, "quests")
        self.item_id = ids(self.items, P.ITEM_BASE, P.ITEM_END, "items")
        self.aura_id = ids(list(self.auras) + list(self.memories), P.SPELL_BASE, P.SPELL_END, "auras")
        self.memory_spell = {k: self.aura_id.pop(k) for k in self.memories}
        self.next_trigger = P.NPC_END - 400 + 1
        self.next_spawn = P.SPAWN_BASE
        self.next_go_spawn = P.GO_SPAWN_BASE
        self.next_display = P.GO_DISPLAY_BASE
        self.next_trainer = P.TRAINER_BASE
        self.next_look = P.DISPLAY_BASE
        self.next_extra = P.EXTRA_BASE
        self.lists = {}                 # entry -> number of timed action lists made
        self.go_entries = set()         # objects with scenes (their lists' owners)
        self.data_fields = {}           # entry -> next data value
        self.script_rows = {}           # (entry, source type) -> next id
        self.texts = {}                 # entry -> next creature_text group

    # -- places --------------------------------------------------------------------------------
    def point(self, ref, chapter, where):
        """(map, x, y, z) of a place key, an (x, y) or an (x, y, z)."""
        if isinstance(ref, str):
            key = self.qualify(chapter, ref)
            if key not in self.places:
                self.err(where, f"no place {ref!r}")
                return (K.MAP_KALIMDOR, 0.0, 0.0, 0.0)
            m, v = self.places[key]
        else:
            m, v = self.chapter_of_key(chapter).get("map", K.MAP_KALIMDOR), ref
        if len(v) == 3:
            return (m, float(v[0]), float(v[1]), float(v[2]))
        z = self.ground(m, v[0], v[1])
        if z is None:
            self.err(where, f"no ground at {v}")
            z = 0.0
        return (m, float(v[0]), float(v[1]), float(z))

    def chapter_of_key(self, chapter):
        return next(ch["CHAPTER"] for ch in self.chapters if ch["CHAPTER"]["key"] == chapter)

    def points(self, ref, chapter, where):
        refs = ref if isinstance(ref, list) else [ref]
        return [self.point(r, chapter, where) for r in refs]

    # -- references ----------------------------------------------------------------------------
    def creature(self, ref, chapter, where):
        """A creature entry: an NPC key of the story's, or the game's entry."""
        if isinstance(ref, int):
            if ref not in self.world_creatures:
                self.err(where, f"no creature {ref} in the game")
            return ref
        key = self.qualify(chapter, ref)
        if key not in self.npc_id:
            self.err(where, f"no NPC {ref!r}")
            return 0
        return self.npc_id[key]

    def item(self, ref, chapter, where):
        if isinstance(ref, int):
            if ref not in self.world_items:
                self.err(where, f"no item {ref} in the game")
            return ref
        key = self.qualify(chapter, ref)
        if key not in self.item_id:
            self.err(where, f"no item {ref!r}")
            return 0
        return self.item_id[key]

    def quest(self, ref, chapter, where):
        key = self.qualify(chapter, ref)
        if key not in self.quest_id and key.split(":")[0] not in {ch["CHAPTER"]["key"] for ch in self.chapters}:
            # (a later chapter's, not released yet: a quest no one has done, so "until" it is for now)
            self.unwritten = True
            return self.P.QUEST_END
        if key not in self.quest_id:
            self.err(where, f"no quest {ref!r}")
            return 0
        return self.quest_id[key]

    # -- the build -----------------------------------------------------------------------------
    def build(self):
        W = self.W
        self.world_creatures = {int(r["entry"]): r for r in W("creature_template")}
        self.world_items = {int(r["entry"]): r for r in W("item_template")}
        self.index()
        self.assign()
        self.phase_bits = {}            # (zone, rule) -> bit
        self.phase_spells = []          # (spell, bit, rule, zones)
        self.memory_spawns = {}         # memory key -> [(who, point)]: its stage's people and things
        self.flyers = {}                # creature entry -> height: those who float (sky)
        self.movement = {}              # creature entry -> creature_template_movement values
        self.zones = set()
        for ch in self.chapters:
            self.zones.update(ch["CHAPTER"].get("zones", []))
        self.spells = []                # the story's auras: dicts for tools/build_data.py to make spells of
        self.build_race_spells()
        for key, d in self.memories.items():
            self.build_memory_spell(key, d)
        for key, d in self.auras.items():
            self.build_aura(key, d)
        for key, d in self.items.items():
            self.build_item(key, d)
        # (those one talks to or gives something to for a quest: a gossip menu each)
        self.talkers = set()
        for q in self.quests.values():
            for target, _ in q.get("interact", []):
                self.talkers.add(self.qualify(q["chapter"], target))
            for _, target, *_ in q.get("use", []):
                if isinstance(target, str) and self.qualify(q["chapter"], target) in self.npcs:
                    self.talkers.add(self.qualify(q["chapter"], target))
            for z in q.get("quiz", []):
                self.talkers.add(self.qualify(q["chapter"], z.get("npc", "")))
        for m in self.memories.values():
            if m.get("singer"):
                self.talkers.add(self.qualify(m["chapter"], m["singer"]))
        for key, d in self.npcs.items():
            self.build_npc(key, d)
        for key, d in self.objects.items():
            self.build_object(key, d)
        for key, d in self.quests.items():
            self.build_quest(key, d)
        for d in self.extra_spawns:
            self.build_spawn(d)
        self.build_graveyards()
        self.build_start()
        self.build_memories()
        self.build_phases()
        for entry, values in sorted(self.movement.items()):
            self.row("creature_template_movement", CreatureId=entry, **values)
        known = {int(r["DisplayID"]) for r in self.W("creature_model_info")}
        known |= {d for d, _ in self.tables.get("_new_looks", [])}
        self.tables["_model_info"] = sorted({r["CreatureDisplayID"] for r in self.tables.get("creature_template_model", [])
                                             if r["CreatureDisplayID"] not in known})
        scripted = {r["entryorguid"] for r in self.tables.get("smart_scripts", []) if r["source_type"] == 0}
        # (and those handed a scene's beats: a list of theirs another starts on them runs only on a SmartAI; one with no
        # event of its own gets a quiet one, facing where it stands after a fight, which the core wants a SmartAI to have)
        handed = {r["entryorguid"] // 1000 for r in self.tables.get("smart_scripts", []) if r["source_type"] == 9}
        creatures = {r["entry"] for r in self.tables.get("creature_template", [])}
        for entry in sorted((handed & creatures) - scripted - self.go_entries):
            self.smart(entry, 0, EV_RESET, (), [(A_ORIENTATION, (), (T_SELF,))])
        scripted |= handed
        looted = {r["Entry"] for r in self.tables.get("creature_loot_template", [])}
        for r in self.tables.get("creature_template", []):
            if r["AIName"] == "SmartAI" and r["entry"] not in scripted:
                r["AIName"] = ""
            if r["lootid"] and r["lootid"] not in looted:
                r["lootid"] = 0
        finals = [k for k, q in self.quests.items() if q.get("final")]
        if len(finals) > 1:
            self.err("the story", f"more than one final quest: {finals}")
        # (no last quest yet, the story released only so far: one no one can take, so the gate stays shut)
        self.tables["_story"] = {"final_quest": self.quest_id[finals[0]] if finals else self.P.QUEST_END, "first_quest": self.P.QUEST_BASE,
                                 "last_quest": self.P.QUEST_END}
        if not finals or getattr(self, "unwritten", False):
            # A quest of the story's last id that no one gives (a chapter not written yet stands for it): the server
            # takes conditions and phase rows that name a quest only if it exists.
            if self.P.QUEST_END in self.quest_id.values():
                self.err("the story", f"its last quest id {self.P.QUEST_END} is kept for the quests not written yet")
            self.row("quest_template", ID=self.P.QUEST_END, QuestType=2, QuestLevel=1, MinLevel=1, QuestSortID=0, Flags=0,
                     RewardXPDifficulty=0, RewardMoney=0, AllowableRaces=self.P.RACE_BIT, LogTitle="(a quest not written yet)",
                     LogDescription="", QuestDescription="", AreaDescription="", QuestCompletionLog="", StartItem=0, TimeAllowed=0)
        if self.P.race_spells:                  # (what the module reads of the naga's: the memories' marker and fade)
            self.tables["_story"].update({"marker_spell": self.P.race_spells["marker"], "fade_spell": self.P.race_spells["fade"]})
        if self.errors:
            raise StoryError(f"{self.P.who}' story has problems:\n  " + "\n  ".join(self.errors))
        return self.tables, self.client

    # -- auras ---------------------------------------------------------------------------------
    def build_aura(self, key, d):
        """An aura of the story's (a spell tools/build_data.py makes): a mark on the player's bar (a buff with a
        name and a line of text), a disguise (another look), a slow, a stun, a root, a speed."""
        kind = d.get("kind", "mark")
        if kind not in AURA_KINDS:
            self.err(key, f"no aura kind {kind!r}")
            return
        misc, amount = 0, 0
        if kind == "disguise":
            misc = self.hidden_creature(d["name"], self.look(d.get("look", "trigger"), key), scale=d.get("scale", 1.0))
        elif kind in ("slow", "speed"):
            amount = -abs(d.get("percent", 40)) if kind == "slow" else abs(d.get("percent", 30))
        elif kind == "stats":                   # every stat up by a share (a small blessing)
            misc, amount = -1, abs(d.get("percent", 1))
        elif kind == "screen":                  # the screen looks otherwise (ScreenEffect.dbc: a vision, a fog, a dark)
            misc = d.get("screen", 0)
            if not self.screen_known(misc):
                self.err(key, f"no screen effect {misc!r} in the game (ScreenEffect.dbc)")
        self.spells.append(dict(id=self.aura_id[key], name=d["name"], aura=AURA_KINDS[kind], misc=misc, amount=amount,
                                seconds=d.get("seconds", 0), text=d.get("text", ""), icon=d.get("icon", 0),
                                visual=d.get("visual", 0), kind=kind))

    def screen_known(self, sid):
        if not hasattr(self, "_screens"):
            self._screens = {r[0] for r in self.D("ScreenEffect").rows}
        return sid in self._screens

    def build_race_spells(self):
        """The naga's own spells for the module's memories (tools/murloc/profiles.py race_spells): the marker the
        module puts on while one relives (every phase row of theirs needs it absent), and the fade (the screen
        going dark a moment, in and out). Their race phases are made with the story's phases (build_phases)."""
        rs = self.P.race_spells
        if not rs:
            return
        self.spells.append(dict(id=rs["marker"], name="Reliving", aura=SPELL_AURA_DUMMY, misc=0, amount=0, seconds=0, text="",
                                icon=0, visual=0, kind="marker", hidden=True, keep=True))
        self.spells.append(dict(id=rs["fade"], name="Fading", aura=SPELL_AURA_SCREEN_EFFECT, misc=self.P.FADE_SCREEN, amount=0,
                                seconds=3, text="", icon=0, visual=0, kind="screen", hidden=True))
        if not self.screen_known(self.P.FADE_SCREEN) or not self.screen_known(self.P.MEMORY_SCREEN):
            self.err("the profile", "its fade or memory screen effect isn't in the game's ScreenEffect.dbc")

    def build_memory_spell(self, key, d):
        """A memory's aura (MEMORIES): "Reliving: <its name>" on the bar with whose memory it is, its phase bit
        alone (the module takes every other phase of the player's away while it's on) and the game's flashback
        look on the screen; kept through death (the module wakes the player at the pool)."""
        if not self.P.MEMORY_BITS:
            self.err(key, f"{self.P.who}' story has no memories (a profile with MEMORY_BITS has)")
            return
        bit = self.memory_bit(key)
        screen = d.get("screen", self.P.MEMORY_SCREEN)
        if not self.screen_known(screen):
            self.err(key, f"no screen effect {screen!r} in the game (ScreenEffect.dbc)")
        text = d.get("text") or (f"{d['whose']}'s memory." if d.get("whose") else "A memory.")
        self.spells.append(dict(id=self.memory_spell[key], name=f"Reliving: {d['name']}", aura=SPELL_AURA_PHASE, misc=bit, amount=0,
                                seconds=0, text=text, icon=d.get("icon", 50153), visual=d.get("visual", 0), kind="memory", keep=True,
                                effects=[(SPELL_AURA_PHASE, bit, 0), (SPELL_AURA_SCREEN_EFFECT, screen, 0)]))

    def aura(self, ref, chapter, where):
        if isinstance(ref, int):
            return ref
        key = self.qualify(chapter, ref)
        if key not in self.aura_id:
            self.err(where, f"no aura {ref!r}")
            return 0
        return self.aura_id[key]

    def hidden_creature(self, name, display, scale=1.0, smart=False):
        """A creature of the story's own that nobody sees as one: an explored place's watcher, a disguise's look."""
        entry = self.next_trigger
        self.next_trigger += 1
        if entry > self.P.NPC_END:
            raise StoryError("too many triggers")
        self.row("creature_template", entry=entry, name=name, subname="", gossip_menu_id=0, minlevel=1, maxlevel=1,
                 faction=35, npcflag=0, speed_walk=1.0, speed_run=1.14286, unit_class=1, unit_flags=0x02000000 | 0x200,
                 type=10, flags_extra=128 if smart else 0, rank=0, HealthModifier=1.0, ManaModifier=1.0, ArmorModifier=1.0,
                 DamageModifier=1.0, BaseAttackTime=2000, RangeAttackTime=2000, lootid=0, mingold=0, maxgold=0,
                 AIName="SmartAI" if smart else "", ScriptName="", detection_range=20.0)
        self.row("creature_template_model", CreatureID=entry, Idx=0, CreatureDisplayID=display, DisplayScale=scale, Probability=1)
        return entry

    def resolve(self, text):
        """[text] with each {chN:key} the id the story gave it (a person's, an object's, a quest's or an
        item's): the server test's steps (tools/murloc/test.steps) written with the story's names."""
        def one(m):
            key = m.group(1)
            for store in (self.npc_id, self.go_id, self.quest_id, self.item_id, self.aura_id):
                if key in store:
                    return str(store[key])
            raise StoryError(f"the test steps name {key}, which the story hasn't")
        def height(m):                          # {z:chN:place}: the ground's height there (a GM's .go to it)
            key = m.group(1)
            if key not in self.places:
                raise StoryError(f"the test steps name the place {key}, which the story hasn't")
            return f"{self.point(key, key.split(':')[0], 'the test steps')[3] + 1.0:.1f}"
        text = re.sub(r"\{z:(ch\d+:[A-Za-z0-9_]+)\}", height, text)

        def place(m):                           # {xyz:chN:place}: the place itself (a GM's .go there)
            key = m.group(1)
            if key not in self.places:
                raise StoryError(f"the test steps name the place {key}, which the story hasn't")
            _, x, y, z = self.point(key, key.split(":")[0], "the test steps")
            return f"{x:.1f} {y:.1f} {z + 1.0:.1f}"
        text = re.sub(r"\{xyz:(ch\d+:[A-Za-z0-9_]+)\}", place, text)
        return re.sub(r"\{(ch\d+:[A-Za-z0-9_]+)\}", one, text)

    # -- items ---------------------------------------------------------------------------------
    def icon(self, ref, where):
        if isinstance(ref, int):
            return ref
        if isinstance(ref, str) and ref.startswith("item:"):
            r = self.world_items.get(int(ref[5:]))
            if not r:
                self.err(where, f"no item {ref}")
                return 0
            return int(r["displayid"])
        if ref in K.ICONS:
            return K.ICONS[ref]
        self.err(where, f"no icon {ref!r}")
        return 0

    def template_item(self, cls, sub, inv, level, quality, name):
        """An item of the game's like the one wanted (its look, damage, armour, speed)."""
        key = (cls, sub, inv)
        if not hasattr(self, "_by_kind"):
            self._by_kind = {}
            for r in self.world_items.values():
                if int(r["Quality"]) in (1, 2, 3) and int(r["ItemLevel"]) > 0 and int(r["displayid"]) > 0:
                    self._by_kind.setdefault((int(r["class"]), int(r["subclass"]), int(r["InventoryType"])), []).append(r)
        pool = self._by_kind.get(key, [])
        if not pool and inv == 13:
            pool = self._by_kind.get((cls, sub, 21), [])
        if not pool:
            return None
        best = sorted(pool, key=lambda r: (abs(int(r["ItemLevel"]) - level), abs(int(r["Quality"]) - quality), int(r["entry"])))
        near = [r for r in best if abs(int(r["ItemLevel"]) - level) <= abs(int(best[0]["ItemLevel"]) - level) + 3][:12]
        return near[zlib.crc32(name.encode()) % len(near)]

    def build_item(self, key, d):
        iid = self.item_id[key]
        kind = d.get("kind")
        name = d["name"]
        row = dict(entry=iid, name=name, Quality=d.get("quality", 1), bonding=4, stackable=d.get("stack", 1),
                   maxcount=d.get("stack", 1) if not kind else 0, InventoryType=0, ItemLevel=d.get("level", 1),
                   RequiredLevel=0, Material=-1, description=d.get("description", ""), displayid=0, armor=0, dmg_min1=0,
                   dmg_max1=0, delay=0, sheath=0)
        stats = []
        if not kind:
            row.update({"class": 12, "subclass": 0, "displayid": self.icon(d.get("icon", "letter"), key)})
        else:
            level = d.get("level", 10)
            quality = d.get("quality", 2)
            part = kind.split(":")
            if part[0] == "weapon":
                sub, inv = WEAPONS[part[1]]
                cls = 2
            elif part[0] == "armor":
                mat, slot = part[1], part[2]
                cls, sub = 4, MATERIALS[mat] if slot != "back" else 1
                inv = SLOTS[slot]
            elif part[0] == "tabard":
                cls, sub, inv = 4, 0, 19
            elif part[0] in ("ring", "neck", "trinket"):
                cls, sub, inv = 4, 0, {"ring": 11, "neck": 2, "trinket": 12}[part[0]]
            elif part[0] == "shield":
                cls, sub, inv = 4, 6, 14
            elif part[0] == "offhand":
                cls, sub, inv = 4, 0, 23
            elif part[0] in ("food", "drink", "bag"):
                self.consumable_item(row, d, part[0], key)
                self.row("item_template", **row)
                self.item_dbc(iid, row)
                return
            else:
                self.err(key, f"no item kind {kind!r}")
                return
            t = self.template_item(cls, sub, inv, level, quality, name)
            if t is None:
                self.err(key, f"no item of the game's like {kind}")
                return
            row.update({"class": cls, "subclass": sub, "InventoryType": inv, "displayid": int(t["displayid"]),
                        "Quality": quality, "bonding": 1, "stackable": 1, "maxcount": 0, "ItemLevel": level,
                        "RequiredLevel": max(1, level - 5), "Material": int(t["Material"]), "armor": int(t["armor"]),
                        "dmg_min1": float(t["dmg_min1"]), "dmg_max1": float(t["dmg_max1"]), "dmg_type1": int(t["dmg_type1"]),
                        "delay": int(t["delay"]), "sheath": int(t["sheath"]), "MaxDurability": int(t["MaxDurability"]),
                        "SellPrice": int(t["SellPrice"]), "BuyPrice": int(t["BuyPrice"]), "block": int(t["block"]),
                        "ammo_type": int(t["ammo_type"]), "RangedModRange": float(t["RangedModRange"])})
            for s, v in d.get("stats", []):
                if s == "armor":
                    row["armor"] += v
                elif s in STAT:
                    stats.append((STAT[s], v))
                else:
                    self.err(key, f"no stat {s!r}")
        for i, (t_, v) in enumerate(stats[:10], start=1):
            row[f"stat_type{i}"], row[f"stat_value{i}"] = t_, v
        if d.get("aura"):                       # used: the aura on the player
            row.update(spellid_1=self.aura(d["aura"], d["chapter"], key), spelltrigger_1=0,
                       spellcharges_1=-1 if d.get("consumed") else 0, spellcooldown_1=-1, spellcategorycooldown_1=-1)
        if d.get("carry"):                      # while it's in the bags, the aura's on the player (the module)
            self.tables.setdefault("_carry", []).append((iid, self.aura(d["carry"], d["chapter"], key)))
        self.row("item_template", **row)
        self.item_dbc(iid, row)

    def item_dbc(self, iid, row):
        """The item in the game's Item table: the client's (the patch) and the server's (item_dbc: SmartAI's
        giving and taking check it)."""
        values = [iid, row["class"], row["subclass"], -1, row["Material"], row["displayid"], row["InventoryType"], row["sheath"]]
        self.client.setdefault("Item", []).append(values)
        self.row("item_dbc", ID=iid, ClassID=values[1], SubclassID=values[2], Sound_Override_Subclassid=-1, Material=values[4],
                 DisplayInfoID=values[5], InventoryType=values[6], SheatheType=values[7])

    def consumable_item(self, row, d, kind, key):
        """Food, drink or a bag: like the game's of its level (its spell, its price; a bag its slots)."""
        level = d.get("level", 10)
        if kind == "bag":
            slots = d.get("slots", 8)
            src = self.world_items[min(K.BAGS, key=lambda b: abs(b[0] - slots))[1]]
            row.update({"class": 1, "subclass": 0, "InventoryType": 18, "ContainerSlots": slots, "bonding": 0,
                        "stackable": 1, "maxcount": 0, "Quality": d.get("quality", 1)})
        else:
            table = K.FOOD if kind == "food" else K.DRINK
            src = self.world_items[max((t for t in table if t[0] <= max(level, 1)), key=lambda t: t[0])[1]]
            row.update({"class": 0, "subclass": 5, "InventoryType": 0, "bonding": 0, "stackable": 20, "maxcount": 0,
                        "Quality": d.get("quality", 1), "RequiredLevel": int(src["RequiredLevel"])})
            for c in ("spellid_1", "spelltrigger_1", "spellcharges_1", "spellcooldown_1", "spellcategory_1",
                      "spellcategorycooldown_1"):
                row[c] = int(src[c])
        row.update({"displayid": self.icon(d["icon"], key) if d.get("icon") else int(src["displayid"]),
                    "BuyPrice": int(src["BuyPrice"]), "SellPrice": int(src["SellPrice"]), "Material": int(src["Material"])})

    # -- creatures -----------------------------------------------------------------------------
    def look(self, ref, where):
        if isinstance(ref, int):
            display = ref
        elif ref in self.P.LOOKS:
            display = self.P.LOOKS[ref]
        else:
            self.err(where, f"no look {ref!r}")
            return self.P.LOOKS["warrior"]
        if self.P.strict and not self.display_known(display):
            self.err(where, f"look {ref!r} ({display}) isn't in the game's CreatureDisplayInfo, nor the story's own range")
        return display

    def display_known(self, display):
        if not hasattr(self, "_displays_known"):
            self._displays_known = {r[0] for r in self.D("CreatureDisplayInfo").rows}
        lo, hi = self.P.looks_own_range or (0, -1)
        # (the murlocs' looks the patch makes: the race's and the tribe's people, tools/build_data.py's)
        return display in self._displays_known or lo <= display <= hi or 33101 <= display <= 33115

    def sound_known(self, sid):
        if not hasattr(self, "_sounds_known"):
            self._sounds_known = {r[0] for r in self.D("SoundEntries").rows}
        lo, hi = self.P.sounds_own_range or (0, -1)
        return sid in self._sounds_known or lo <= sid <= hi

    def fly(self, entry):
        """[entry] floats (creature_template_movement: no gravity): a sky placement's."""
        self.movement.setdefault(entry, {})["Flight"] = 1

    def above(self, pt, height, ref, where):
        """[pt] raised [height] yards above the ground, or the water over it (a sky placement)."""
        m, x, y, z = pt
        if not isinstance(height, (int, float)) or not 2 <= height <= 300:
            self.err(where, f"sky {height!r}: 2 to 300 yards above the ground (or the water)")
            return pt
        water = self.water(m, x, y) if self.water else None
        return (m, x, y, (max(z, water) if water is not None else z) + height)

    def npc_look(self, key, d):
        """Someone's look: a LOOKS name or a CreatureDisplayInfo id, or a new one (display_extra: a person of a
        playable race drawn as the game draws its people, with a skin, face, hair and gear)."""
        if d.get("display_extra"):
            if d.get("look") is not None:
                self.err(key, "both look= and display_extra=")
            return self.display_extra(key, d["display_extra"])
        return self.look(d.get("look", "warrior"), key)

    def npc_scale(self, key, d, display):
        """The model scale of someone's look: scale= as it is (on top of the look's own), or size= (how big they
        are: the look's own scale taken out, so size=1.4 is 1.4 times a scale-1 model whatever the look)."""
        if "size" in d and "scale" in d:
            self.err(key, "both scale= and size=")
        if "size" in d:
            own = self.display_scale(display)
            return round(d["size"] / own, 4) if own else d["size"]
        scale = d.get("scale", 1.0)
        if not isinstance(scale, (int, float)) or not 0.05 <= scale <= 20:
            self.err(key, f"scale {scale!r}: 0.05 to 20")
        return scale

    def display_scale(self, display):
        if not hasattr(self, "_display_scale"):
            import struct
            dt = self.D("CreatureDisplayInfo")
            self._display_scale = {r[0]: struct.unpack("<f", struct.pack("<I", r[4]))[0] for r in dt.rows}
        return self._display_scale.get(display, 1.0)

    RACE_IDS = {"human": 1, "orc": 2, "dwarf": 3, "nightelf": 4, "undead": 5, "tauren": 6, "gnome": 7, "troll": 8,
                "bloodelf": 10, "draenei": 11}
    GEAR_SLOTS = ["head", "shoulder", "shirt", "chest", "waist", "legs", "feet", "wrist", "hands", "tabard", "back"]

    def display_extra(self, key, x):
        """A new look of a playable race's person (bible 18.6: Garithos, the Highborne court...): a
        CreatureDisplayInfoExtra row (race, sex, skin, face, hair, hair colour, facial hair, gear) and a
        CreatureDisplayInfo row drawing it, for the game (the patch) and the server; checked against the game's
        CharSections (the skin, face and hair it names must be the race's)."""
        P = self.P
        if P.DISPLAY_BASE is None:
            self.err(key, f"{P.who}' story has no looks of its own (display_extra)")
            return K.LOOKS["warrior"]
        race = self.RACE_IDS.get(x.get("race"))
        sex = {"male": 0, "female": 1}.get(x.get("sex"))
        if race is None or sex is None:
            self.err(key, f"display_extra needs race= ({', '.join(self.RACE_IDS)}) and sex= (male, female)")
            return K.LOOKS["warrior"]
        if not hasattr(self, "_sections"):
            cs = self.D("CharSections")
            self._sections = {(r[1], r[2], r[3], r[8], r[9]) for r in cs.rows}       # race, sex, kind, variation, colour
        skin, face, hair, hair_colour, facial = (x.get(k, 0) for k in ("skin", "face", "hair", "hair_color", "facial"))
        for kind, variation, colour, what in ((0, 0, skin, "skin"), (1, face, skin, "face"), (3, hair, hair_colour, "hair"),
                                              (2, facial, hair_colour, "facial hair")):
            if (kind == 2 and not facial) or (kind == 3 and not hair and (race, sex, 3, 0, hair_colour) not in self._sections):
                continue
            if (race, sex, kind, variation, colour) not in self._sections:
                self.err(key, f"display_extra: the {x['race']} {x['sex']}s have no {what} {variation} in colour {colour} (CharSections)")
        gear = [0] * 11
        for slot, ref in x.get("gear", {}).items():
            if slot not in self.GEAR_SLOTS:
                self.err(key, f"display_extra: no gear slot {slot!r} ({', '.join(self.GEAR_SLOTS)})")
                continue
            gear[self.GEAR_SLOTS.index(slot)] = self.icon(ref, key) if not isinstance(ref, int) else ref
        extra, display = self.next_extra, self.next_look
        self.next_extra += 1
        self.next_look += 1
        if extra > P.EXTRA_END or display > P.DISPLAY_END:
            raise StoryError("too many new looks (display_extra)")
        # the game's own look of a person of that race and sex: its model, sounds and the rest
        if not hasattr(self, "_extra_template"):
            dbc_extra = self.D("CreatureDisplayInfoExtra")
            ex = {r[0]: (r[1], r[2]) for r in dbc_extra.rows}
            self._extra_template = {}
            dt = self.D("CreatureDisplayInfo")
            for r in dt.rows:
                if r[3] in ex and ex[r[3]] not in self._extra_template:
                    self._extra_template[ex[r[3]]] = r
            self._display_dbc = dt
        tpl = self._extra_template.get((race, sex))
        if tpl is None:
            self.err(key, f"display_extra: no look of the game's of a {x['race']} {x['sex']} to draw it with")
            return K.LOOKS["warrior"]
        import struct
        dt = self._display_dbc
        values = [display, tpl[1], tpl[2], extra, struct.unpack("<f", struct.pack("<I", tpl[4]))[0], tpl[5],
                  dt.s(tpl[6]), dt.s(tpl[7]), dt.s(tpl[8]), dt.s(tpl[9]), tpl[10], tpl[11], tpl[12], tpl[13], tpl[14], tpl[15]]
        values[4] = 1.0
        self.client.setdefault("CreatureDisplayInfo", []).append(values)
        extra_values = [extra, race, sex, skin, face, hair, hair_colour, facial] + gear + [x.get("flags", 0), x.get("bake", "")]
        self.client.setdefault("CreatureDisplayInfoExtra", []).append(extra_values)
        self.row("creaturedisplayinfo_dbc", ID=display, ModelID=values[1], SoundID=values[2], ExtendedDisplayInfoID=extra,
                 CreatureModelScale=1.0, CreatureModelAlpha=values[5], TextureVariation_1="", TextureVariation_2="",
                 TextureVariation_3="", PortraitTextureName=values[9], BloodLevel=values[10], BloodID=values[11],
                 NPCSoundID=values[12], ParticleColorID=values[13], CreatureGeosetData=values[14], ObjectEffectPackageID=values[15])
        self.row("creaturedisplayinfoextra_dbc", ID=extra, DisplayRaceID=race, DisplaySexID=sex, SkinID=skin, FaceID=face,
                 HairStyleID=hair, HairColorID=hair_colour, FacialHairID=facial,
                 **{f"NPCItemDisplay{i + 1}": g for i, g in enumerate(gear)}, Flags=x.get("flags", 0), BakeName=x.get("bake", ""))
        self.tables.setdefault("_new_looks", []).append((display, tpl[0]))
        return display

    def side(self, d):
        s = d.get("side", "tribe")
        if isinstance(s, int):
            return s
        if s.startswith("faction:"):
            return self.faction_template(int(s.split(":")[1]), d["key"])
        if s not in self.P.SIDES:
            self.err(d["key"], f"no side {s!r}")
            return self.P.SIDES["tribe"]
        return self.P.SIDES[s]

    def faction_template(self, faction, where):
        """The FactionTemplate of a reputation faction's own people (the first of the game's)."""
        ft = self.D("FactionTemplate")
        for r in ft.rows:
            if r[1] == faction:
                return r[0]
        self.err(where, f"no FactionTemplate for Faction {faction}")
        return 35

    def language(self, d):
        if d.get("language"):
            return d["language"]
        if not self.P.translate:                # (a naga's people all speak readably unless they're given a language)
            return self.P.own_language
        return "nerglish" if d.get("side", "tribe") in ("tribe",) or d.get("murloc") else "common"

    def spawn(self, entry, pts, facing, phase, wander=0.0, respawn=300, comment=""):
        for i, (m, x, y, z) in enumerate(pts):
            guid = self.next_spawn
            self.next_spawn += 1
            if guid > self.P.SPAWN_END:
                raise StoryError("too many spawns")
            o = facing if facing is not None else (i * 1.37) % 6.28
            extra = dict(equipment_id=1) if entry in self.equipped else {}
            self.row("creature", guid=guid, id=entry, map=m, zoneId=0, areaId=0, spawnMask=1, phaseMask=phase,
                     position_x=round(x, 2), position_y=round(y, 2), position_z=round(z, 2), orientation=round(o, 3),
                     spawntimesecs=respawn, wander_distance=wander, MovementType=1 if wander else 0, Comment=comment, **extra)
            yield guid

    def zone_of(self, m, x, y):
        """The zone a place is in (its area's parent, AreaTable), or None (no map data)."""
        if not self.area:
            return None
        if not hasattr(self, "_area_parent"):
            self._area_parent = {r[0]: r[2] for r in self.D("AreaTable").rows}
        a = self.area(m, x, y)
        while a and self._area_parent.get(a):
            a = self._area_parent[a]
        return a or None

    def phase_of(self, d, chapter, pts=()):
        """The phase mask of someone (or something) at [pts]: the race's own when always there (and the scene
        bit, which no player has, so the story's people find each other for their scenes), a story phase's
        bit, given in the zones the points are in, or a memory's (("memory", key): its bit alone, put on the
        player by the module while reliving it). Never another story's bits: a murloc's people aren't a naga's."""
        p = d.get("phase", "always")
        zones = sorted({z for z in (self.zone_of(m, x, y) for m, x, y, _ in pts) if z}) or self.chapter_of_key(chapter).get("zones", [])
        if p == "always":
            self.zones.update(zones)            # (the race's own phase given there too)
            return self.P.RACE_PHASE | K.SCENE_BIT
        if p[0] == "memory":                    # ("memory", "<memory key>"): its stage's people and things
            key = self.qualify(chapter, p[1])
            if key not in self.memories:
                self.err(d["key"], f"no memory {p[1]!r}")
                return K.SCENE_BIT
            self.memory_spawns.setdefault(key, []).extend((d["key"], pt) for pt in pts)
            return self.memory_bit(key) | K.SCENE_BIT
        self.zones.update(zones)
        if p[0] == "between":                   # ("between", from quest, until quest)
            _, a, b = p
            return self.phase_bit(zones, "between", (self.quest(a, chapter, d["key"]), self.quest(b, chapter, d["key"]))) | K.SCENE_BIT
        kind, quest = p
        if kind not in ("from", "until", "during"):
            self.err(d["key"], f"no phase rule {kind!r} (from, until, during, between, memory)")
            return K.SCENE_BIT
        return self.phase_bit(zones, kind, self.quest(quest, chapter, d["key"])) | K.SCENE_BIT

    def pool_of(self, zones):
        """The bits a story phase in [zones] may take: the profile's story bits, and in a zone where it has more
        (the naga's in Azshara) those too; less another story's bits there and the memories'."""
        pool = list(self.P.PHASE_BITS)
        extra = [set(self.P.ZONE_BITS.get(z, [])) for z in zones]
        if extra and all(extra):
            common = set.intersection(*extra)
            pool += [b for b in self.P.ZONE_BITS[zones[0]] if b in common]
        taken = set(self.P.MEMORY_BITS.values())
        for z in zones:
            taken |= self.reserved.get(z, set())
        return [b for b in pool if b not in taken]

    def phase_bit(self, zones, kind, quest):
        zones = tuple(zones)
        self.zones.update(zones)
        rule = (kind, quest)
        for (zs, r), bit in self.phase_bits.items():
            if r == rule and zs == zones:
                return bit
        used = {bit for (zs, _), bit in self.phase_bits.items() if set(zs) & set(zones)}
        free = [b for b in self.pool_of(zones) if b not in used]
        if not free:
            raise StoryError(f"{self.P.who}: no phase bit left in zones {zones} ({len(used)} story phases there, "
                             f"{sum(len(self.reserved.get(z, ())) for z in zones)} bits another story's)")
        self.phase_bits[(zones, rule)] = free[0]
        return free[0]

    def memory_bit(self, key):
        bit = self.memories[key].get("bit")
        if bit not in self.P.MEMORY_BITS:
            self.err(key, f"a memory's bit is one of {sorted(self.P.MEMORY_BITS)}, not {bit!r}")
            return K.SCENE_BIT
        return self.P.MEMORY_BITS[bit]

    def build_npc(self, key, d):
        entry = self.npc_id[key]
        chapter = d["chapter"]
        roles = d.get("role", "ambient")
        roles = roles.split("+") if isinstance(roles, str) else list(roles)
        role = next((r for r in roles if r.startswith(("trainer:", "profession:"))), roles[0])
        lo, hi = d["level"] if isinstance(d.get("level"), (tuple, list)) else (d.get("level", 10), d.get("level", 10))
        flags = 0
        menu = 0
        lang = self.language(d)
        if set(roles) & ({"quest", "vendor", "innkeeper", "repair", "travel"} | set(ROLE_OPTIONS)) \
                or role.startswith(("trainer:", "profession:")) or d.get("gossip") or key in self.talkers:
            flags |= NPCFLAG["gossip"]
            menu = entry
        if "quest" in roles or self.gives_quests(key):
            flags |= NPCFLAG["quest"]
        options = []
        if set(roles) & {"vendor", "innkeeper", "repair"}:
            flags |= NPCFLAG["vendor"]
            options.append((3, NPCFLAG["vendor"], "Let me see what you have."))
            for slot, item in enumerate(d.get("sells", K.VENDOR_FOOD)):
                self.row("npc_vendor", entry=entry, slot=slot, item=self.item(item, chapter, key))
        if "repair" in roles:
            flags |= NPCFLAG["repair"]
        for r in roles:
            if r in ROLE_OPTIONS:
                kind, nf, icon, text = ROLE_OPTIONS[r]
                flags |= nf
                options.append((kind, nf, text))
        if "innkeeper" in roles:
            flags |= NPCFLAG["innkeeper"]
            options.insert(0, (8, NPCFLAG["innkeeper"], "Make this place your home."))
        if role.startswith(("trainer:", "profession:")):
            what = role.split(":")[1]
            flags |= NPCFLAG["trainer"]
            if role.startswith("trainer:"):
                flags |= NPCFLAG["class_trainer"]
                if what not in K.CLASSES:
                    self.err(key, f"no class {what!r}")
                    return
                self.trainer(entry, 0, K.CLASSES[what], key, lang)
                mask = 1 << (K.CLASSES[what] - 1)
                options.append((5, NPCFLAG["trainer"], "Teach me.", mask))
                options.append((16, NPCFLAG["trainer"], "Make me forget what I learned.", mask))
            else:
                flags |= NPCFLAG["profession_trainer"]
                if what not in K.SKILLS:
                    self.err(key, f"no profession {what!r}")
                    return
                self.trainer(entry, 2, K.SKILLS[what], key, lang, requirement=0)
                options.append((5, NPCFLAG["trainer"], "Teach me your trade."))
        if "travel" in roles:
            released = {ch["CHAPTER"]["key"] for ch in self.chapters}
            for n, spec in enumerate(d.get("travel", [])):
                dest, needs = spec[:2]
                if isinstance(dest, str) and ":" in dest and dest.split(":")[0] not in released:
                    continue                    # (a hub of a chapter not released yet)
                words = spec[2] if len(spec) > 2 else "Take me to the other place."
                m, x, y, z = self.point(dest, chapter, key)
                options.append(("travel", 1, words, (m, x, y, z), needs))
        if d.get("turret") and "side" not in d:
            d = dict(d, side="ally" if "ally" in self.P.SIDES else "tribe")
        side = self.side(d)
        enemy = "enemy" in roles or d.get("side") in ("naga", "hostile")
        unit_class = d.get("class", 2 if d.get("caster") else 1)
        unit_flags = d.get("unit_flags", 0)
        if d.get("untouchable"):                # (a canon figure: never attacked, never killed; still clicked for its quests)
            unit_flags |= UNTOUCHABLE
            if enemy:
                self.err(key, "untouchable, and an enemy: nobody could fight it")
        if d.get("turret"):                     # (rooted, shooting what comes near: its abilities, a ranged spell)
            self.movement.setdefault(entry, {})["Rooted"] = 1
            if not d.get("abilities"):
                self.err(key, "a turret with no abilities (abilities=[(spell id, every ms)]: what it shoots)")
        if d.get("sky"):
            self.fly(entry)
        look = self.npc_look(key, d)
        speed = d.get("speed", 1.0)
        if d.get("equip"):                      # what they hold: (main hand, off hand, ranged), the game's item ids
            held = list(d["equip"]) + [0] * (3 - len(d["equip"]))
            if len(held) > 3 or not all(isinstance(i, int) and i >= 0 for i in held):
                self.err(key, "equip=(main hand, off hand, ranged): the game's item ids, 0 for none")
            else:
                self.row("creature_equip_template", CreatureID=entry, ID=1, ItemID1=held[0], ItemID2=held[1], ItemID3=held[2])
                self.equipped.add(entry)
        self.row("creature_template", entry=entry, name=d["name"], subname=d.get("subname") or "", gossip_menu_id=menu,
                 minlevel=lo, maxlevel=hi, faction=side, npcflag=flags, speed_walk=speed, speed_run=round(1.14286 * speed, 5),
                 unit_class=unit_class,
                 unit_flags=unit_flags, type=K.TYPES.get(d.get("type", "humanoid"), 7),
                 type_flags=1 if d.get("tameable") else 0, flags_extra=d.get("flags_extra", 0), rank=d.get("rank", 0),
                 HealthModifier=d.get("health", 1.0), ManaModifier=1.0, ArmorModifier=1.0, DamageModifier=d.get("damage", 1.0),
                 BaseAttackTime=2000, RangeAttackTime=2000, lootid=entry if enemy else 0,
                 mingold=lo * 8 if enemy else 0, maxgold=hi * 20 if enemy else 0, AIName="SmartAI", ScriptName="",
                 detection_range=d.get("detection", 20.0))
        self.row("creature_template_model", CreatureID=entry, Idx=0, CreatureDisplayID=look,
                 DisplayScale=self.npc_scale(key, d, look), Probability=1)
        if len(d.get("looks", [])) > 3:
            self.err(key, "more than three more looks (the database takes four in all)")
        for i, extra in enumerate(d.get("looks", [])[:3], start=1):
            other = self.look(extra, key)
            self.row("creature_template_model", CreatureID=entry, Idx=i, CreatureDisplayID=other,
                     DisplayScale=self.npc_scale(key, d, other), Probability=1)
        # gossip: the greeting, and what it offers
        if menu:
            greeting = d.get("gossip") or d.get("greeting") or "Hello. What do you want?"
            self.row("npc_text", ID=entry, text0_0=self.words(greeting, lang), text0_1=self.words(greeting, lang), lang0=0,
                     Probability0=1, em0_0=0, em0_1=1)
            self.row("gossip_menu", MenuID=menu, TextID=entry)
            for n, opt in enumerate(options):
                if opt[0] == "travel":
                    _, icon, text, (m, x, y, z), needs = opt
                    self.row("gossip_menu_option", MenuID=menu, OptionID=n, OptionIcon=2, OptionText=self.option_words(text, lang),
                             OptionType=1, OptionNpcFlag=1)
                    self.smart(entry, 0, EV_GOSSIP_SELECT, (menu, n), [(A_CLOSE_GOSSIP, (), (T_INVOKER,)),
                                                                     (A_TELEPORT, (m,), (T_INVOKER, 0, 0, 0, x, y, z, 0))])
                    if needs:
                        self.condition(15, menu, n, 8, self.quest(needs, chapter, key))
                    continue
                kind, nf, text = opt[:3]
                self.row("gossip_menu_option", MenuID=menu, OptionID=n, OptionIcon={3: 1, 5: 3, 8: 5, 9: 6, 13: 6, 16: 3}.get(kind, 0),
                         OptionText=self.option_words(text, lang), OptionType=kind, OptionNpcFlag=nf)
                if len(opt) > 3:                # (a class trainer's: only to their class, as the game's own)
                    self.condition(15, menu, n, 15, opt[3])
            self.next_option[entry] = len(options)
        # where
        if d.get("at") is not None and not d.get("summoned"):
            pts = self.points(d["at"], chapter, key)
            phase = self.phase_of(d, chapter, pts)
            if d.get("sky"):                    # (that high above the ground, or the water, floating)
                pts = [self.above(pt, d["sky"], d["at"] if not isinstance(d["at"], list) else None, key) for pt in pts]
            list(self.spawn(entry, pts, d.get("facing"), phase, d.get("wander", 0.0),
                            d.get("respawn", 60 if enemy else 120), f"mod-murloc-naga: {d['name']}"))
        state = next((b[2] for b in d.get("idle", []) if b[0] == "state" and b[1] == "self"), None)
        if state is not None:                   # (every one of it, summoned ones too; a spawn may have its own)
            self.row("creature_template_addon", entry=entry, emote=K.STATES.get(state, state) if isinstance(state, str) else state)
        # idle
        for beat in d.get("idle", []):
            if beat[0] == "every":
                _, period, beats = beat[:3]
                timing = (period // 2, period, period, period + period // 2)
                first = self.script_rows.get((entry, 0), 0)
                if all(b[0] != "wait" and (len(b) < 2 or b[1] in ("self", None)) for b in beats):
                    acts = [a for b in beats for a in self.beat(entry, b, chapter, key)]
                    # (an idle has no one who started it: a line is said to no one, anything else aimed at "the
                    # player" (a look, a cast) at the nearest one within 30 yards)
                    acts = [(t, p, ((T_SELF,) if t == A_TALK else (T_CLOSEST_PLAYER, 30)) if tg == (T_INVOKER,) else tg)
                            for t, p, tg in acts]
                    if not acts:
                        continue
                    self.smart(entry, 0, EV_UPDATE_OOC, timing, acts)  # (plain actions: no list held, nothing a scene waits for)
                else:
                    lid = self.actionlist(entry, beats, chapter, key)
                    self.smart(entry, 0, EV_UPDATE_OOC, timing, [(A_ACTIONLIST, (lid, 0, 0), (T_SELF,))])
                if len(beat) > 3:               # only where it stands in that phase (its chapter 1 spawns, say)
                    pts = self.points(d["at"], chapter, key) if d.get("at") is not None else []
                    bit = self.phase_of(dict(d, phase=beat[3]), chapter, pts) & ~K.SCENE_BIT & ~self.P.RACE_PHASE
                    self.condition(22, first + 1, entry, 26, bit, target=1)
        if d.get("at_health"):                  # hurt to a share of its health in a fight: its scene (a duel's end)
            pct, beats = d["at_health"][:2]
            lid = self.actionlist(entry, beats, chapter, key + " (hurt)")
            self.smart(entry, 0, EV_HEALTH_PCT, (0, int(pct), 30000, 30000), [(A_ACTIONLIST, (lid, 0, 1), (T_SELF,))])
        if d.get("watch"):                      # someone coming near: their scene (a guard's warning, a slave's look)
            radius, beats = d["watch"][:2]
            cooldown = d["watch"][2] if len(d["watch"]) > 2 else 15000
            lid = self.actionlist(entry, beats, chapter, key + " (watch)")
            self.smart(entry, 0, EV_OOC_LOS, (2, int(radius), cooldown, cooldown, 1), [(A_ACTIONLIST, (lid, 0, 1), (T_SELF,))])
        for spell, every in d.get("abilities", []):
            self.smart(entry, 0, EV_UPDATE_IC, (2000, 5000, every, every + 3000), [(A_CAST, (spell, 0), (2,))])

    def gives_quests(self, key):
        """Whether [key] gives or ends any quest (either needs the quest giver's flag)."""
        return any(self.qualify(q["chapter"], who) == key for q in self.quests.values()
                   for who in (q.get("giver"), q.get("ender")) if isinstance(who, str) and not who.startswith("object:"))

    def trainer(self, entry, kind, teaches, key, lang, requirement=None):
        """A trainer of the story's own (its greeting murloc), teaching what the game's best trainer of
        the class or the profession teaches."""
        tid = self.next_trainer
        self.next_trainer += 1
        best = self.best_trainer(kind, teaches)
        if not best:
            self.err(key, f"no trainer of the game's for {kind}:{teaches}")
            return
        self.row("trainer", Id=tid, Type=kind, Requirement=teaches if requirement is None else requirement,
                 Greeting=self.words("Learn, little one.", lang))
        self.tables.setdefault("_trainer_copy", []).append((tid, best))
        self.row("creature_default_trainer", CreatureId=entry, TrainerId=tid)

    def best_trainer(self, kind, requirement):
        """The game's trainer teaching the most of a class (kind 0, [requirement] the class) or a
        profession (kind 2, [requirement] its skill line: the one most of its spells need), up to
        Artisan (no Grand Master: Northrend's)."""
        if not hasattr(self, "_trainers"):
            spells = {}
            for r in self.W("trainer_spell"):
                spells.setdefault(int(r["TrainerId"]), []).append(r)
            self._trainers = {}
            for r in self.W("trainer"):
                tid, ttype = int(r["Id"]), int(r["Type"])
                rows = spells.get(tid, [])
                if ttype == 0:
                    key = (0, int(r["Requirement"]))
                elif ttype == 2:
                    lines = [int(s["ReqSkillLine"]) for s in rows if int(s["ReqSkillLine"])]
                    if not lines:
                        continue
                    key = (2, max(set(lines), key=lines.count))
                else:
                    continue
                self._trainers.setdefault(key, []).append((len(rows), tid, rows))
        cands = self._trainers.get((kind, requirement), [])
        if kind == 2:
            cands = [c for c in cands if all(int(s["ReqLevel"]) <= 65 for s in c[2])] or cands
        return max(cands)[1] if cands else None

    # -- objects -------------------------------------------------------------------------------
    def display(self, ref, where):
        if isinstance(ref, int):
            return ref
        m = K.MODELS.get(ref, ref)
        if isinstance(m, int):
            return m
        if not hasattr(self, "_displays"):
            gd = self.D("GameObjectDisplayInfo")
            self._displays = {gd.s(r[1]).lower(): r[0] for r in gd.rows}
            self._new_displays = {}
        path = m
        if path.lower() in self._displays:
            return self._displays[path.lower()]
        if path.lower().endswith(".mdx") and path.lower()[:-4] + ".m2" in self._displays:
            return self._displays[path.lower()[:-4] + ".m2"]
        if path not in self._new_displays:
            did = self.next_display
            self.next_display += 1
            if did > self.P.GO_DISPLAY_END:
                raise StoryError("too many object looks")
            self._new_displays[path] = did
            self.client.setdefault("GameObjectDisplayInfo", []).append([did, path] + [0] * 10 + [-1.0, -1.0, 0.0, 1.0, 1.0, 3.0, 0])
        return self._new_displays[path]

    def build_object(self, key, d):
        entry = self.go_id[key]
        chapter = d["chapter"]
        kind = d.get("kind", "doodad")
        data = [0] * 24
        quest = self.quest(d["quest"], chapter, key) if d.get("quest") else 0
        if kind == "doodad":
            gtype = 5
        elif kind == "loot":
            gtype = 3
            data[0], data[1], data[3], data[8] = 43 if d.get("open") else 0, entry, 1, quest  # lock, loot, respawn, quest
            data[2] = 0
            for item, lo, hi in d.get("loot", []):
                self.row("gameobject_loot_template", Entry=entry, Item=self.item(item, chapter, key), Reference=0,
                         Chance=100, QuestRequired=1 if quest else 0, LootMode=1, GroupId=0, MinCount=lo, MaxCount=hi,
                         Comment="mod-murloc-naga")
        elif kind == "use":
            gtype = 10
            data[1], data[3], data[4] = quest, 3000, 0
            if d.get("consumable", True):
                data[5] = 1
        elif kind == "chair":
            gtype, data[0], data[1] = 7, 1, 1
        elif kind == "questgiver":              # (gives or ends quests: giver="object:<key>")
            gtype = 2
        elif kind == "mailbox":
            gtype = 19
        else:
            self.err(key, f"no object kind {kind!r}")
            return
        self.row("gameobject_template", entry=entry, type=gtype, displayId=self.display(d.get("model", "crate"), key),
                 name=self.words(d["name"], self.P.own_language) if d.get("murloc_name") else d["name"], size=d.get("scale", 1.0),
                 AIName="SmartGameObjectAI" if d.get("beats") else "", **{f"Data{i}": v for i, v in enumerate(data)})
        if d.get("beats"):                      # used: a scene (the object's own list; others' by data)
            if kind != "use":
                self.err(key, "beats on an object that isn't used (kind 'use')")
            self.go_entries.add(entry)
            lid = self.actionlist(entry, d["beats"], chapter, key)
            self.smart(entry, 1, EV_GOSSIP_HELLO, (1,), [(A_ACTIONLIST, (lid, 0, 1), (T_SELF,))])
        if d.get("at") is not None:
            pts = self.points(d["at"], chapter, key)
            phase = self.phase_of(d, chapter, pts)
            for i, pt in enumerate(pts):
                self.object_row(entry, pt, d.get("facing", (i * 1.1) % 6.28), phase,
                                d.get("respawn", 30 if kind in ("loot", "use") else 0), d["name"])

    # -- SmartAI -------------------------------------------------------------------------------
    def smart(self, entry, source, event, eparams, actions, chance=100, flags=0):
        """Rows of one event and its actions (linked): actions are (type, params, target)."""
        k = (entry, source)
        first = self.script_rows.get(k, 0)
        for n, (atype, aparams, target) in enumerate(actions):
            sid = first + n
            ev = (event, eparams) if n == 0 else (61, ())     # (the rest: linked)
            ep = list(ev[1]) + [0] * (6 - len(ev[1]))
            ap = list(aparams) + [0] * (6 - len(aparams))
            tp = list(target) + [0] * (9 - len(target))
            self.row("smart_scripts", entryorguid=entry, source_type=source, id=sid,
                     link=sid + 1 if n + 1 < len(actions) else 0, event_type=ev[0], event_phase_mask=0,
                     event_chance=chance if n == 0 else 100, event_flags=flags,
                     **{f"event_param{i + 1}": ep[i] for i in range(6)}, action_type=atype,
                     **{f"action_param{i + 1}": ap[i] for i in range(6)}, target_type=tp[0],
                     target_param1=tp[1], target_param2=tp[2], target_param3=tp[3], target_param4=0,
                     target_x=tp[4], target_y=tp[5], target_z=tp[6], target_o=tp[7], comment="mod-murloc-naga")
        self.script_rows[k] = first + len(actions)

    def text_group(self, entry, text, chat, lang, emote, sound):
        g = self.texts.get(entry, 0)
        self.texts[entry] = g + 1
        self.row("creature_text", CreatureID=entry, GroupID=g, ID=0, Text=text, Type=chat, Language=lang, Probability=100,
                 Emote=emote, Duration=0, Sound=sound, BroadcastTextId=0, TextRange=0, comment="mod-murloc-naga")
        return g

    def emote_id(self, name, where):
        if isinstance(name, int):
            return name
        if name in K.EMOTES:
            return K.EMOTES[name]
        self.err(where, f"no emote {name!r}")
        return 0

    def sound_id(self, name, where):
        if isinstance(name, int):
            sid = name
        elif name in self.P.SOUNDS:
            sid = self.P.SOUNDS[name]
        else:
            self.err(where, f"no sound {name!r}")
            return 0
        if self.P.strict and not self.sound_known(sid):
            self.err(where, f"sound {name!r} ({sid}) isn't in the game's SoundEntries, nor the story's own range")
        return sid

    def visual_id(self, name, where):
        if isinstance(name, int):
            return name
        if name in K.VISUALS:
            return K.VISUALS[name]
        self.err(where, f"no visual {name!r}")
        return 0

    def actor(self, who, owner, chapter, where):
        """(entry, target) of a beat's doer as the list's owner sees it: itself, or the nearest of them."""
        if who in ("self", None):
            return owner, (T_SELF,)
        if who == "player":
            return None, (T_INVOKER,)
        e = self.creature(who, chapter, where)
        return e, (T_CLOSEST_CREATURE, e, 80, 0)

    def actionlist(self, owner, beats, chapter, where):
        """A timed action list of [owner]'s doing [beats] (others' beats: their own lists, started by data)."""
        n = self.lists.get(owner, 0)
        self.lists[owner] = n + 1
        if n >= 1000:
            raise StoryError(f"{where}: more than 1000 scenes for one creature")
        lid = owner * 1000 + n
        rows = []                       # (delay, action, params, target)
        delay = 0
        for beat in beats:
            kind = beat[0]
            if kind == "wait":
                delay += beat[1]
                continue
            got = self.beat(owner, beat, chapter, where)
            for a in got:
                rows.append((delay,) + a)
                delay = 0
        if delay and rows:
            pass
        sid = 0
        for d, atype, aparams, target in rows:
            ap = list(aparams) + [0] * (6 - len(aparams))
            tp = list(target) + [0] * (9 - len(target))
            self.row("smart_scripts", entryorguid=lid, source_type=9, id=sid, link=0, event_type=0, event_phase_mask=0,
                     event_chance=100, event_flags=0, event_param1=d, event_param2=d, event_param3=0, event_param4=0,
                     event_param5=0, event_param6=0, action_type=atype, **{f"action_param{i + 1}": ap[i] for i in range(6)},
                     target_type=tp[0], target_param1=tp[1], target_param2=tp[2], target_param3=tp[3], target_param4=0,
                     target_x=tp[4], target_y=tp[5], target_z=tp[6], target_o=tp[7], comment="mod-murloc-naga")
            sid += 1
        return lid

    def by_other(self, owner, other_entry, beat, chapter, where):
        """A beat another creature does itself: a list of its own, started on it (the nearest of them) by the
        scene's owner, the player still its invoker (its "player")."""
        lid = self.actionlist(other_entry, [beat[:1] + ("self",) + beat[2:]], chapter, where)
        return [(A_ACTIONLIST, (lid, 0, 1), (T_CLOSEST_CREATURE, other_entry, 80, 0))]

    def beat(self, owner, beat, chapter, where):
        kind = beat[0]
        who = beat[1] if len(beat) > 1 else None
        if owner in self.go_entries and who in ("self", None) and kind in ("say", "yell", "whisper", "emote", "state", "move",
                                                                           "jump", "face", "follow", "cast", "visual", "sound",
                                                                           "morph", "scale"):
            self.err(where, f"an object can't {kind} (a beat of the object's own scene: give it to someone)")
            return []
        if kind in ("relive", "wake"):          # ("relive", "<memory>"): into a memory; ("wake", "<memory>"): out of it
            key = self.qualify(chapter, beat[1]) if len(beat) > 1 and isinstance(beat[1], str) else None
            if key not in self.memories:
                self.err(where, f"{kind}: no memory {beat[1] if len(beat) > 1 else None!r}")
                return []
            if kind == "relive":
                return [(A_ADD_AURA, (self.memory_spell[key],), (T_INVOKER,))]
            return [(A_REMOVE_AURA, (self.memory_spell[key], 0), (T_INVOKER,))]
        if kind == "morph":                     # ("morph", who, look): another look until they respawn (None: their own)
            e, target = self.actor(who, owner, chapter, where)
            if e is None:
                self.err(where, "the player isn't morphed (a disguise aura is: AURAS kind disguise)")
                return []
            look = beat[2] if len(beat) > 2 else None
            return [(A_MORPH, (0, self.look(look, where) if look is not None else 0), target)]
        if kind == "scale":                     # ("scale", who, 1.4): bigger or smaller until they respawn
            e, target = self.actor(who, owner, chapter, where)
            value = beat[2] if len(beat) > 2 else 1.0
            if not isinstance(value, (int, float)) or not 0.05 <= value <= 20:
                self.err(where, f"scale {value!r}: a size from 0.05 to 20")
                return []
            return [(A_SET_SCALE, (int(round(value * 100)),), target)]
        if kind == "sky":                       # ("sky", "<npc>", "<place>", height, seconds): appears that high, floating
            e = self.creature(beat[1], chapter, where)
            m, x, y, z = self.point(beat[2], chapter, where)
            height = beat[3] if len(beat) > 3 else 20
            secs = beat[4] if len(beat) > 4 else 60
            if not isinstance(height, (int, float)) or not 2 <= height <= 300:
                self.err(where, f"sky height {height!r}: 2 to 300 yards above the ground (or the water)")
                return []
            water = self.water(m, x, y) if self.water and not (isinstance(beat[2], (tuple, list)) and len(beat[2]) == 3) else None
            base = max(z, water) if water is not None else z
            self.fly(e)
            return [(A_SUMMON, (e, 3, secs * 1000), (T_POSITION, 0, 0, 0, x, y, base + height, 0))]
        if kind == "teleport":
            if who != "player":
                self.err(where, "only the player is teleported")
                return []
            m, x, y, z = self.point(beat[2], chapter, where)
            o = beat[3] if len(beat) > 3 else 0.0
            return [(A_TELEPORT, (m,), (T_INVOKER, 0, 0, 0, x, y, z, o))]
        if kind in ("aura", "unaura"):
            e, target = self.actor(who, owner, chapter, where)
            spell = self.aura(beat[2], chapter, where)
            if kind == "aura":
                return [(A_ADD_AURA, (spell,), target)]
            return [(A_REMOVE_AURA, (spell, 0), target)]
        if kind == "faction":                   # ("faction", who, side): whose side they're on now (until they respawn)
            e, target = self.actor(who, owner, chapter, where)
            side = beat[2]
            fid = side if isinstance(side, int) else self.P.SIDES.get(side)
            if fid is None:
                self.err(where, f"no side {side!r}")
                return []
            return [(A_SET_FACTION, (fid,), target)]
        if kind == "evade":                     # ("evade", "self"): stops fighting and goes home
            e, target = self.actor(who, owner, chapter, where)
            return [(A_EVADE, (), target)]
        if kind == "object":
            ok = self.qualify(chapter, beat[1])
            if ok not in self.go_id:
                self.err(where, f"no object {beat[1]!r}")
                return []
            m, x, y, z = self.point(beat[2], chapter, where)
            secs = beat[3] if len(beat) > 3 else 60
            return [(A_SUMMON_GO, (self.go_id[ok], secs, 0, 1), (T_POSITION, 0, 0, 0, x, y, z, beat[4] if len(beat) > 4 else 0.0))]
        if kind in ("say", "yell", "whisper"):
            _, who, text = beat[:3]
            emote = self.emote_id(beat[3], where) if len(beat) > 3 and beat[3] else 0
            sound = self.sound_id(beat[4], where) if len(beat) > 4 and beat[4] else 0
            e, target = self.actor(who, owner, chapter, where)
            if e is None:
                self.err(where, "the player can't speak")
                return []
            d = self.npcs.get(next((k for k, v in self.npc_id.items() if v == e), None), {})
            lang = self.language(d) if d else self.P.own_language
            words = self.words(text, lang)
            g = self.text_group(e, words, CHAT[kind], 0, emote, sound)
            if e == owner:
                return [(A_TALK, (g, 0, 0), (T_INVOKER,))]
            return [(A_TALK, (g, 0, 0), target)]
        if kind == "emote":
            e, target = self.actor(who, owner, chapter, where)
            return [(A_EMOTE, (self.emote_id(beat[2], where),), target)]
        if kind == "state":
            e, target = self.actor(who, owner, chapter, where)
            s = beat[2]
            sid = K.STATES.get(s, s) if isinstance(s, str) else s
            if isinstance(sid, str):
                self.err(where, f"no state {s!r}")
                sid = 0
            return [(A_EMOTE_STATE, (sid,), target)]
        if kind == "sound":
            e, target = self.actor(who, owner, chapter, where)
            return [(A_SOUND, (self.sound_id(beat[2], where), 0), target)]
        if kind == "music":
            return [(216, (self.sound_id(beat[1], where), 0, 0), (T_INVOKER,))]
        if kind == "visual":
            # (a look spell lands on whoever casts it, as nearly all of them target their caster: the one it's
            # for casts it on themselves: the player (the invoker's cast), another (a cross cast, their own
            # scene left running), or the owner)
            e, target = self.actor(who, owner, chapter, where)
            spell = self.visual_id(beat[2], where)
            if e is None:
                return [(A_INVOKER_CAST, (spell, 2), (T_INVOKER,))]
            if e != owner:
                return [(A_CROSS_CAST, (spell, 2, T_CLOSEST_CREATURE, e, 80), (T_CLOSEST_CREATURE, e, 80, 0))]
            return [(A_CAST, (spell, 2), (T_SELF,))]
        if kind == "cast":
            e, _ = self.actor(who, owner, chapter, where)
            spell = self.visual_id(beat[2], where) if not isinstance(beat[2], int) else beat[2]
            tgt = beat[3] if len(beat) > 3 else "player"
            _, ttarget = self.actor(tgt, owner, chapter, where)
            if e != owner:
                return self.by_other(owner, e, ("cast", "self", spell, tgt), chapter, where)
            return [(A_CAST, (spell, 2), ttarget)]
        if kind in ("move", "jump", "face", "despawn"):
            e, _ = self.actor(who, owner, chapter, where)
            if e is None:
                self.err(where, f"the player can't be made to {kind}")
                return []
            if e != owner:
                return self.by_other(owner, e, beat, chapter, where)
            if kind == "move":
                m, x, y, z = self.point(beat[2], chapter, where)
                run = len(beat) > 3 and beat[3] == "run"
                return [(A_SET_RUN, (1 if run else 0,), (T_SELF,)), (A_MOVE_TO, (0, 0, 0, 0), (T_POSITION, 0, 0, 0, x, y, z, 0))]
            if kind == "jump":
                m, x, y, z = self.point(beat[2], chapter, where)
                return [(A_JUMP, (10, 10), (T_POSITION, 0, 0, 0, x, y, z, 0))]
            if kind == "face":
                if beat[2] == "player":
                    return [(A_ORIENTATION, (), (T_INVOKER,))]
                m, x, y, z = self.point(beat[2], chapter, where)
                return [(A_ORIENTATION, (), (T_POSITION, 0, 0, 0, x, y, z, 0))]
            return [(A_DESPAWN, (500,), (T_SELF,))]
        if kind == "give":
            return [(A_ADD_ITEM, (self.item(beat[1], chapter, where), beat[2] if len(beat) > 2 else 1), (T_INVOKER,))]
        if kind == "take":
            return [(A_REMOVE_ITEM, (self.item(beat[1], chapter, where), beat[2] if len(beat) > 2 else 1), (T_INVOKER,))]
        if kind == "summon":
            e = self.creature(beat[1], chapter, where)
            m, x, y, z = self.point(beat[2], chapter, where)
            secs = beat[3] if len(beat) > 3 else 60
            return [(A_SUMMON, (e, 3, secs * 1000), (T_POSITION, 0, 0, 0, x, y, z, 0))]
        if kind == "credit":
            return [(A_AREA_EXPLORED, (self.quest(beat[1], chapter, where),), (T_INVOKER,))]
        if kind == "follow":
            e, _ = self.actor(who, owner, chapter, where)
            if e is not None and e != owner:
                return self.by_other(owner, e, beat, chapter, where)
            return [(A_FOLLOW, (2, 0), (T_INVOKER,))]
        self.err(where, f"no beat {kind!r}")
        return []

    def condition(self, source, group, entry, ctype, value, negative=0, else_group=0, value2=0, target=0, source_id=0):
        self.row("conditions", SourceTypeOrReferenceId=source, SourceGroup=group, SourceEntry=entry, SourceId=source_id,
                 ElseGroup=else_group, ConditionTypeOrReference=ctype, ConditionTarget=target, ConditionValue1=value,
                 ConditionValue2=value2, ConditionValue3=0, NegativeCondition=negative, ErrorType=0, ErrorTextId=0,
                 ScriptName="", Comment=self.P.COMMENT)

    # -- quests --------------------------------------------------------------------------------
    def trigger(self, place_pt, radius, quest, name):
        """An unseen creature at a place: whoever comes within [radius] on [quest] has explored it."""
        entry = self.hidden_creature(name, self.P.LOOKS["trigger"], smart=True)
        list(self.spawn(entry, [place_pt], 0.0, self.P.RACE_PHASE | sum(set(self.P.MEMORY_BITS.values())), comment=f"mod-murloc-naga: {name}"))
        self.smart(entry, 0, EV_OOC_LOS, (2, int(radius), 1000, 1000, 1), [(A_AREA_EXPLORED, (quest,), (T_INVOKER,))])
        return entry

    def build_quest(self, key, d):
        chapter = d["chapter"]
        ch = self.chapter_of_key(chapter)
        qid = self.quest_id[key]
        where = key
        giver = d["giver"]
        ender = d.get("ender", giver)
        giver_npc = self.npcs.get(self.qualify(chapter, giver)) if isinstance(giver, str) else None
        ender_npc = self.npcs.get(self.qualify(chapter, ender)) if isinstance(ender, str) else None
        lang_give = self.language(giver_npc) if giver_npc else self.P.own_language
        lang_end = self.language(ender_npc) if ender_npc else lang_give
        if not self.P.translate:
            # (a quest's own words are always readable in a story whose people's are (the naga's, bible 4.1): the
            # giver's tongue is heard in what they say aloud, never in the quest window)
            lang_give = lang_end = self.P.own_language
        level = d["level"]
        req_npc, req_items, objective_text = [], [], []
        special = 0
        for target, count in d.get("kill", []):
            req_npc.append((self.creature(target, chapter, where), count))
            objective_text.append("")
        for target, text in d.get("interact", []):
            e = self.creature(target, chapter, where)
            npc_key = self.qualify(chapter, target)
            req_npc.append((e, 1))
            objective_text.append(d.get("interact_goal", ""))
            self.interaction(e, npc_key, qid, text, d.get("interact_beats", []), chapter, where)
        for spec in d.get("use", []):
            item, target, count = spec[:3]
            self.use(qid, item, target, count, req_npc, objective_text, chapter, where, spec[3] if len(spec) > 3 else [])
        for spec in d.get("emotes", []):
            self.emote_credit(qid, spec, req_npc, objective_text, chapter, where)
        for ref, count in d.get("objects", []):       # objects of the story's to use (kind "use", quest this one)
            ok = self.qualify(chapter, ref)
            if ok not in self.go_id:
                self.err(where, f"no object {ref!r}")
                continue
            obj = self.objects[ok]
            if obj.get("kind") != "use" or self.qualify(obj["chapter"], obj.get("quest")) != key:
                self.err(where, f"the object {ref!r} isn't one to use for this quest (kind \"use\", quest {key.split(':')[1]!r})")
            req_npc.append((-self.go_id[ok], count))
            objective_text.append(obj.get("goal", ""))
        for spec in d.get("quiz", []):
            self.quiz(qid, spec, req_npc, objective_text, chapter, where)
        for spec in d.get("turrets", []):
            self.turrets(qid, spec, req_npc, objective_text, chapter, where)
        if d.get("tug"):
            special |= 2
            self.tug(qid, d, chapter, where)
        if d.get("explore"):
            special |= 2
            pt = self.point(d["explore"], chapter, where)
            self.trigger(pt, d.get("radius", 15), qid, f"{d['title']} (where)")
        if d.get("event"):
            special |= 2
        if d.get("escort"):
            special |= 2
            who, path = d["escort"]
            e = self.creature(who, chapter, where)
            pt = self.point(path[-1], chapter, where)
            self.trigger(pt, d.get("radius", 12), qid, f"{d['title']} (the end of the way)")
            d.setdefault("accept", []).insert(0, ("follow", who))
        for item, count in d.get("items", []):
            req_items.append((self.item(item, chapter, where), count))
        for item, sources in d.get("drops", {}).items():
            iid = self.item(item, chapter, where)
            for src, chance in sources:
                e = self.creature(src, chapter, where)
                lootid = e
                if isinstance(src, int):
                    r = self.world_creatures.get(src)
                    lootid = int(r["lootid"]) if r and int(r["lootid"]) else src
                    if r and not int(r["lootid"]):
                        self.tables.setdefault("_lootid", set()).add(src)
                if not hasattr(self, "_game_loot"):
                    self._game_loot = {(int(r["Entry"]), int(r["Item"])) for r in self.W("creature_loot_template")}
                    self._our_loot = set()
                if (lootid, iid) in self._game_loot or (lootid, iid) in self._our_loot:
                    continue                    # (the game drops it already, or another of the story's quests asked)
                self._our_loot.add((lootid, iid))
                self.row("creature_loot_template", Entry=lootid, Item=iid, Reference=0, Chance=chance, QuestRequired=1,
                         LootMode=1, GroupId=0, MinCount=1, MaxCount=1, Comment=self.P.LOOT_COMMENT)
        if len(req_npc) > 4 or len(req_items) > 6:
            self.err(where, "too many objectives")
        rewards = [self.item(i, chapter, where) for i in d.get("rewards", [])]
        choice = [self.item(i, chapter, where) for i in d.get("choice", [])]
        rep = d.get("rep", [])
        row = dict(ID=qid, QuestType=2, QuestLevel=level, MinLevel=d.get("min", max(1, level - 2)), QuestSortID=ch.get("zones", [0])[0],
                   Flags=8, RewardXPDifficulty=d.get("xp", 7), RewardMoney=d.get("money", 75 * level),
                   AllowableRaces=self.P.RACE_BIT, LogTitle=self.words(d["title"], lang_give),
                   LogDescription=d["goal"], QuestDescription=self.words(d["text"], lang_give), AreaDescription="",
                   QuestCompletionLog=self.completion_log(ender, chapter, where),
                   StartItem=self.item(d["source"], chapter, where) if d.get("source") else 0, TimeAllowed=d.get("time", 0))
        for i, (e, n) in enumerate(req_npc[:4], start=1):
            row[f"RequiredNpcOrGo{i}"], row[f"RequiredNpcOrGoCount{i}"] = e, n
            if objective_text[i - 1]:
                row[f"ObjectiveText{i}"] = objective_text[i - 1]
        for i, (e, n) in enumerate(req_items[:6], start=1):
            row[f"RequiredItemId{i}"], row[f"RequiredItemCount{i}"] = e, n
        for i, e in enumerate(rewards[:4], start=1):
            row[f"RewardItem{i}"], row[f"RewardAmount{i}"] = e, 1
        for i, e in enumerate(choice[:6], start=1):
            row[f"RewardChoiceItemID{i}"], row[f"RewardChoiceItemQuantity{i}"] = e, 1
        for i, (f, v) in enumerate(rep[:5], start=1):
            row[f"RewardFactionID{i}"], row[f"RewardFactionOverride{i}"] = f, v * 100
        if d.get("source"):
            row["ItemDrop1"], row["ItemDropQuantity1"] = self.item(d["source"], chapter, where), 1
        if d.get("reward_spell"):               # cast on the player as it's handed in
            row["RewardSpell"] = d["reward_spell"]
        for spell in d.get("learn", []):        # learned as it's handed in (the module teaches them)
            self.tables.setdefault("_learn", []).append((qid, spell))
        self.row("quest_template", **row)
        prev = d.get("prev")
        prevs = prev if isinstance(prev, list) else ([prev] if prev else [])
        excl = d.get("exclusive", 0)
        classes = 0
        for c in d.get("classes", []):
            if c not in K.CLASSES:
                self.err(where, f"no class {c!r}")
            else:
                classes |= 1 << (K.CLASSES[c] - 1)
        if d.get("repeatable"):
            special |= 1
        self.row("quest_template_addon", ID=qid, PrevQuestID=self.quest(prevs[0], chapter, where) if len(prevs) == 1 else 0,
                 SpecialFlags=special, ProvidedItemCount=1 if d.get("source") else 0, ExclusiveGroup=excl and (self.P.QUEST_BASE + 100 * int(chapter[2:]) + excl),
                 AllowableClasses=classes)
        anyof = d.get("prev_any", [])
        alls = prevs if len(prevs) > 1 or anyof else []
        for n, p in enumerate(anyof or [None]):           # (each way in: all of prev, and one of prev_any)
            for a in alls:
                self.condition(19, 0, qid, 8, self.quest(a, chapter, where), else_group=n)
            if p is not None:
                self.condition(19, 0, qid, 8, self.quest(p, chapter, where), else_group=n)
        ends = [self.emote_id(e, where) for e in d.get("reward_emotes", ["talk"])][:4]
        self.row("quest_offer_reward", ID=qid, **{f"Emote{i + 1}": e for i, e in enumerate(ends)},
                 RewardText=d.get("reward", "") if d.get("plain_reward") else self.words(d.get("reward", ""), lang_end))
        if d.get("progress"):
            self.row("quest_request_items", ID=qid, EmoteOnComplete=1, EmoteOnIncomplete=6,
                     CompletionText=self.words(d["progress"], lang_end))
        details = [self.emote_id(e, where) for e in d.get("details", ["talk"])][:4]
        self.row("quest_details", ID=qid, **{f"Emote{i + 1}": e for i, e in enumerate(details)})
        # who gives it, who ends it
        for kind, who in (("starter", giver), ("ender", ender)):
            if isinstance(who, str) and who.startswith("object:"):
                ok = self.qualify(chapter, who[7:])
                if ok not in self.go_id:
                    self.err(where, f"no object {who}")
                    continue
                self.row(f"gameobject_quest{kind}", id=self.go_id[ok], quest=qid)
            else:
                self.row(f"creature_quest{kind}", id=self.creature(who, chapter, where), quest=qid)
        # scenes
        g_entry = self.creature(giver, chapter, where) if not (isinstance(giver, str) and giver.startswith("object:")) else 0
        e_entry = self.creature(ender, chapter, where) if not (isinstance(ender, str) and ender.startswith("object:")) else 0
        if d.get("accept") and g_entry:
            lid = self.actionlist(g_entry, d["accept"], chapter, where + " (accept)")
            self.smart(g_entry, 0, EV_ACCEPTED_QUEST, (qid,), [(A_ACTIONLIST, (lid, 0, 1), (T_SELF,))])
        if d.get("complete") and e_entry:
            lid = self.actionlist(e_entry, d["complete"], chapter, where + " (reward)")
            self.smart(e_entry, 0, EV_REWARD_QUEST, (qid,), [(A_ACTIONLIST, (lid, 0, 1), (T_SELF,))])
        # where the map marks it
        self.pois(qid, d, req_npc, chapter, where)

    def completion_log(self, ender, chapter, where):
        if isinstance(ender, int):
            r = self.world_creatures.get(ender)
            return f"Return to {r['name']}." if r else ""
        if isinstance(ender, str) and ender.startswith("object:"):
            return ""
        d = self.npcs.get(self.qualify(chapter, ender))
        return f"Return to {d['name']}." if d else ""

    def interaction(self, entry, npc_key, qid, text, beats, chapter, where):
        """A gossip option on the NPC while [qid] is in the log: choosing it is the objective's credit."""
        d = self.npcs.get(npc_key)
        if d is None:
            self.err(where, f"no NPC {npc_key} to talk to")
            return
        menu = entry
        opt = self.next_option.get(entry, 0)
        self.next_option[entry] = opt + 1
        self.row("gossip_menu_option", MenuID=menu, OptionID=opt, OptionIcon=0, OptionText=self.option_words(text, self.language(d)),
                 OptionType=1, OptionNpcFlag=1)
        self.condition(15, menu, opt, 9, qid)
        self.condition(15, menu, opt, 28, qid, negative=1)
        actions = [(A_CLOSE_GOSSIP, (), (T_INVOKER,)), (A_KILLED_MONSTER, (entry,), (T_INVOKER,))]
        if beats:
            actions.append((A_ACTIONLIST, (self.actionlist(entry, beats, chapter, where), 0, 1), (T_SELF,)))
        self.smart(entry, 0, EV_GOSSIP_SELECT, (menu, opt), actions)

    def helper_id(self, what):
        """An id of the story's last 400 creature ids for something no one sees (a quiz's menu and text)."""
        entry = self.next_trigger
        self.next_trigger += 1
        if entry > self.P.NPC_END:
            raise StoryError(f"too many helpers ({what})")
        return entry

    def quiz(self, qid, spec, req_npc, objective_text, chapter, where):
        """A question someone asks (bible 18.4, 9.22): while the quest is in the log, unfinished, their gossip offers
        [ask]; it opens [question] with the answers; the right one is the objective's credit (and its beats), a
        wrong one its beats and the question again."""
        npc_key = self.qualify(chapter, spec.get("npc", ""))
        if npc_key not in self.npc_id:
            self.err(where, f"quiz: no NPC {spec.get('npc')!r}")
            return
        e, d = self.npc_id[npc_key], self.npcs[npc_key]
        lang = self.language(d)
        answers = spec.get("answers", [])
        if not spec.get("question") or not 2 <= len(answers) <= 8 or sum(1 for a in answers if len(a) > 1 and a[1]) != 1:
            self.err(where, "a quiz has a question= and 2 to 8 answers=[(text, right, beats)], one of them right")
            return
        credit = self.hidden_creature(f"{d['name']}'s question", self.P.LOOKS["trigger"])
        menu = self.helper_id("a quiz's menu")
        question = self.words(spec["question"], lang)
        self.row("npc_text", ID=menu, text0_0=question, text0_1=question, lang0=0, Probability0=1, em0_0=0, em0_1=1)
        self.row("gossip_menu", MenuID=menu, TextID=menu)
        opt = self.next_option.get(e, 0)
        self.next_option[e] = opt + 1
        self.row("gossip_menu_option", MenuID=e, OptionID=opt, OptionIcon=0, OptionText=self.option_words(spec.get("ask", "Ask me."), lang),
                 OptionType=1, OptionNpcFlag=1)
        self.condition(15, e, opt, 9, qid)
        self.condition(15, e, opt, 28, qid, negative=1)
        self.smart(e, 0, EV_GOSSIP_SELECT, (e, opt), [(A_SEND_GOSSIP_MENU, (menu, menu), (T_INVOKER,))])
        for n, answer in enumerate(answers):
            text, right = answer[:2]
            beats = answer[2] if len(answer) > 2 else []
            self.row("gossip_menu_option", MenuID=menu, OptionID=n, OptionIcon=0, OptionText=self.option_words(text, lang),
                     OptionType=1, OptionNpcFlag=1)
            scene = [(A_ACTIONLIST, (self.actionlist(e, beats, chapter, where + " (quiz)"), 0, 1), (T_SELF,))] if beats else []
            if right:
                actions = [(A_CLOSE_GOSSIP, (), (T_INVOKER,)), (A_KILLED_MONSTER, (credit,), (T_INVOKER,))] + scene
            else:
                actions = scene + [(A_SEND_GOSSIP_MENU, (menu, menu), (T_INVOKER,))]
            self.smart(e, 0, EV_GOSSIP_SELECT, (menu, n), actions)
        req_npc.append((credit, 1))
        objective_text.append(spec.get("goal", f"{d['name']}'s question answered"))

    def turrets(self, qid, spec, req_npc, objective_text, chapter, where):
        """Plots where a turret is set up (bible 18.4, 6.23): a thing at each plot, used while the quest is in the
        log (each use the objective's credit), that puts the turret there for a while: someone rooted who shoots
        what comes near (an NPC with turret=True and its abilities)."""
        npc_key = self.qualify(chapter, spec.get("npc", ""))
        if npc_key not in self.npc_id or not self.npcs[npc_key].get("turret"):
            self.err(where, f"turrets: {spec.get('npc')!r} isn't one of the story's people with turret=True")
            return
        pts = self.points(spec.get("at", []), chapter, where)
        if not pts:
            self.err(where, "turrets: no plots (at=)")
            return
        entry = self.P.GO_BASE + len(self.go_id) + len(self.tables.get("_use_gos", []))
        if entry > self.P.GO_END:
            raise StoryError("too many objects")
        self.tables.setdefault("_use_gos", []).append(entry)
        data = [0] * 24
        data[1], data[3] = qid, 3000
        self.row("gameobject_template", entry=entry, type=10, displayId=self.display(spec.get("model", "crate"), where),
                 name=spec.get("name", "Plot"), size=spec.get("scale", 1.0), AIName="SmartGameObjectAI",
                 **{f"Data{i}": v for i, v in enumerate(data)})
        self.go_entries.add(entry)
        self.smart(entry, 1, EV_GOSSIP_HELLO, (1,), [(A_SUMMON, (self.npc_id[npc_key], 3, spec.get("seconds", 120) * 1000), (T_SELF,))])
        for i, pt in enumerate(pts):
            self.object_row(entry, pt, spec.get("facing", 0.0), self.P.RACE_PHASE | sum(set(self.P.MEMORY_BITS.values())),
                            spec.get("respawn", 30), spec.get("name", "Plot"))
        req_npc.append((-entry, spec.get("count", len(pts))))
        objective_text.append(spec.get("goal", ""))

    def tug(self, qid, d, chapter, where):
        """The tug escort (bible 18.4, 7.09, 7.14): taking the quest calls the cart (summoned at the way's first
        place); it rolls along the way; at the midpoint the enemy takes it (they appear, and it rolls back toward
        the start); once they're all dead it turns and goes on; at the end everyone of the race near it on the
        quest has it done."""
        t = d["tug"]
        cart_key = self.qualify(chapter, t.get("cart", ""))
        if cart_key not in self.npc_id:
            self.err(where, f"tug: no cart {t.get('cart')!r}")
            return
        cart = self.npc_id[cart_key]
        if cart in getattr(self, "_tug_carts", set()):
            self.err(where, f"tug: the cart {t['cart']!r} serves another tug quest already (a cart a quest)")
            return
        self._tug_carts = getattr(self, "_tug_carts", set()) | {cart}
        path = [self.point(p, chapter, where) for p in t.get("path", [])]
        mid = t.get("midpoint")
        mi = t["path"].index(mid) if isinstance(mid, str) and mid in t.get("path", []) else mid
        if len(path) < 3 or not isinstance(mi, int) or not 0 < mi < len(path) - 1:
            self.err(where, "tug: a path of 3 places at least, and a midpoint= (one of them, not the first or the last)")
            return
        enemies = t.get("enemies", [])
        if not enemies:
            self.err(where, "tug: enemies=[(npc, place)] who take the cart at the midpoint")
            return
        back = self.point(t.get("back", t["path"][0]), chapter, where)

        def move(pid, pt):
            return [(A_SET_RUN, (1 if t.get("run") else 0,), (T_SELF,)), (A_MOVE_TO, (pid, 0, 0, 0), (T_POSITION, 0, 0, 0, pt[1], pt[2], pt[3], 0))]
        self.smart(cart, 0, EV_JUST_SUMMONED, (), move(1, path[1]))
        for k in range(1, len(path) - 1):
            if k == mi:
                acts = [(A_SET_COUNTER, (1, 0, 1), (T_SELF,))]
                for ref, place in enemies:
                    e = self.creature(ref, chapter, where)
                    m, x, y, z = self.point(place, chapter, where)
                    acts.append((A_SUMMON, (e, 1, t.get("enemy_seconds", 180) * 1000), (T_POSITION, 0, 0, 0, x, y, z, 0)))
                if t.get("taken"):
                    acts.append((A_ACTIONLIST, (self.actionlist(cart, t["taken"], chapter, where + " (taken)"), 0, 1), (T_SELF,)))
                acts += move(100, back)
                self.smart(cart, 0, EV_MOVEMENT_INFORM, (POINT_MOTION, k), acts)
            else:
                self.smart(cart, 0, EV_MOVEMENT_INFORM, (POINT_MOTION, k), move(k + 1, path[k + 1]))
        self.smart(cart, 0, EV_SUMMONED_UNIT_DIES, (0, 0, 0), [(A_SET_COUNTER, (1, 1, 0), (T_SELF,))])
        acts = [(A_ACTIONLIST, (self.actionlist(cart, t["retaken"], chapter, where + " (retaken)"), 0, 1), (T_SELF,))] if t.get("retaken") else []
        self.smart(cart, 0, EV_COUNTER_SET, (1, len(enemies), 0, 0), acts + move(mi + 1, path[mi + 1]))
        self.smart(cart, 0, EV_MOVEMENT_INFORM, (POINT_MOTION, len(path) - 1),
                   [(A_AREA_EXPLORED, (qid,), (T_PLAYER_RANGE, 0, t.get("radius", 40))), (A_DESPAWN, (5000,), (T_SELF,))])
        d.setdefault("accept", []).insert(0, ("summon", t["cart"], t["path"][0], t.get("seconds", 600)))

    def emote_credit(self, qid, spec, req_npc, objective_text, chapter, where):
        """The player's own emote at someone (/wave at a slave) as an objective: each of them answers it once
        every few seconds (SmartAI's receive-emote), while the quest's in the log and unfinished."""
        target, emote, count = spec[:3]
        beats = spec[3] if len(spec) > 3 else []
        if not isinstance(target, str):
            self.err(where, "an emote's objective needs one of the story's people, not the game's")
            return
        if emote not in K.TEXT_EMOTES:
            self.err(where, f"no player emote {emote!r} (common.py TEXT_EMOTES)")
            return
        e = self.creature(target, chapter, where)
        actions = [(A_KILLED_MONSTER, (e,), (T_INVOKER,))]
        if beats:
            actions.append((A_ACTIONLIST, (self.actionlist(e, beats, chapter, where), 0, 1), (T_SELF,)))
        first = self.script_rows.get((e, 0), 0)
        self.smart(e, 0, EV_RECEIVE_EMOTE, (K.TEXT_EMOTES[emote], 6000, 6000), actions)
        self.condition(22, first + 1, e, 9, qid)
        self.condition(22, first + 1, e, 28, qid, negative=1)
        req_npc.append((e, count))
        npc = self.npcs.get(self.qualify(chapter, target), {})
        objective_text.append(f"/{emote} at {npc.get('plural') or npc.get('name', 'them')}")

    def use(self, qid, item, target, count, req_npc, objective_text, chapter, where, beats=()):
        """Using a quest item: on someone (a gossip option while you carry it), or at a place (a thing there
        to use)."""
        iid = self.item(item, chapter, where)
        if isinstance(target, str) and self.qualify(chapter, target) in self.npc_id:
            e = self.npc_id[self.qualify(chapter, target)]
            d = self.npcs[self.qualify(chapter, target)]
            menu = e
            opt = self.next_option.get(e, 0)
            self.next_option[e] = opt + 1
            self.row("gossip_menu_option", MenuID=menu, OptionID=opt, OptionIcon=0,
                     OptionText=self.option_words("Give it to them.", self.language(d)), OptionType=1, OptionNpcFlag=1)
            self.condition(15, menu, opt, 9, qid)
            self.condition(15, menu, opt, 2, iid, value2=1)
            actions = [(A_CLOSE_GOSSIP, (), (T_INVOKER,)), (A_REMOVE_ITEM, (iid, 1), (T_INVOKER,)), (A_KILLED_MONSTER, (e,), (T_INVOKER,))]
            if beats:                           # (their reaction: their own beats)
                actions.append((A_ACTIONLIST, (self.actionlist(e, list(beats), chapter, where), 0, 1), (T_SELF,)))
            self.smart(e, 0, EV_GOSSIP_SELECT, (menu, opt), actions)
            req_npc.append((e, count))
            item_name = self.items.get(self.qualify(chapter, item), {}).get("name") if isinstance(item, str) else None
            objective_text.append(f"{item_name or 'It'} given to {d['plural'] if count > 1 and d.get('plural') else d['name']}")
            return
        # at a place: a thing there to use while carrying the item (on the quest): the item spent, the credit an
        # unseen watcher's, the beats played (the object's own list)
        pt = self.point(target, chapter, where)
        entry = self.P.GO_BASE + len(self.go_id) + len(self.tables.get("_use_gos", []))
        if entry > self.P.GO_END:
            raise StoryError("too many objects")
        self.tables.setdefault("_use_gos", []).append(entry)
        item_name = self.items.get(self.qualify(chapter, item), {}).get("name") if isinstance(item, str) else None
        data = [0] * 24
        data[3] = 3000
        self.row("gameobject_template", entry=entry, type=10, displayId=self.display("sack", where), name=item_name or "",
                 size=0.6, AIName="SmartGameObjectAI", **{f"Data{i}": v for i, v in enumerate(data)})
        credit = self.hidden_creature(f"{item_name or 'It'} used", self.P.LOOKS["trigger"])
        self.go_entries.add(entry)
        actions = [(A_REMOVE_ITEM, (iid, 1), (T_INVOKER,)), (A_KILLED_MONSTER, (credit,), (T_INVOKER,))]
        if beats:
            actions.append((A_ACTIONLIST, (self.actionlist(entry, list(beats), chapter, where), 0, 1), (T_SELF,)))
        first = self.script_rows.get((entry, 1), 0)
        self.smart(entry, 1, EV_GOSSIP_HELLO, (1,), actions)
        self.condition(22, first + 1, entry, 9, qid, source_id=1)                   # (the quest in the log)
        self.condition(22, first + 1, entry, 2, iid, value2=1, source_id=1)         # (the item carried)
        guid = self.next_go_spawn
        self.next_go_spawn += 1
        m, x, y, z = pt
        self.row("gameobject", guid=guid, id=entry, map=m, zoneId=0, areaId=0, spawnMask=1,
                 phaseMask=self.P.RACE_PHASE | sum(set(self.P.MEMORY_BITS.values())) | K.SCENE_BIT,
                 position_x=round(x, 2), position_y=round(y, 2), position_z=round(z, 2), orientation=0, rotation0=0, rotation1=0,
                 rotation2=0, rotation3=1, spawntimesecs=10, animprogress=100, state=1, Comment="mod-murloc-naga: a quest's place")
        req_npc.append((credit, count))
        objective_text.append(f"{item_name or 'It'} used")

    def pois(self, qid, d, req_npc, chapter, where):
        ch = self.chapter_of_key(chapter)
        marks = []
        for n, ref in enumerate(d.get("poi", [])):
            m, x, y, z = self.point(ref, chapter, where)
            marks.append((n if n < len(req_npc) else 0, m, x, y, d.get("poi_radius", 25)))
        if not marks:
            for n, (e, _) in enumerate(req_npc):
                if e > 0 and e not in self.npc_id.values():
                    pts = self.world_spawns(e, ch.get("map", K.MAP_KALIMDOR), ch.get("zones", []))
                    if pts:
                        x = sum(p[0] for p in pts) / len(pts)
                        y = sum(p[1] for p in pts) / len(pts)
                        r = max(20, min(120, max(math.hypot(p[0] - x, p[1] - y) for p in pts)))
                        marks.append((n, ch.get("map", K.MAP_KALIMDOR), x, y, r))
        for i, (obj, m, x, y, r) in enumerate(marks):
            # (the map of the zone the mark is in: Stormwind's for a canal, not Westfall's)
            wma = self.world_map_area(self.zone_of(m, x, y) or ch.get("zones", [0])[0]) or self.world_map_area(ch.get("zones", [0])[0])
            if not wma:
                continue
            self.row("quest_poi", QuestID=qid, id=i, ObjectiveIndex=obj, MapID=m, WorldMapAreaId=wma, Floor=0, Priority=0, Flags=3)
            for j, (px, py) in enumerate(_poly(x, y, r)):
                self.row("quest_poi_points", QuestID=qid, Idx1=i, Idx2=j, X=px, Y=py)

    def world_map_area(self, zone):
        if not hasattr(self, "_wma"):
            self._wma = {r[2]: r[0] for r in self.D("WorldMapArea").rows}
        return self._wma.get(zone, 0)

    def world_spawns(self, entry, mapid, zones):
        if not hasattr(self, "_spawns"):
            self._spawns = {}
            for r in self.W("creature"):
                self._spawns.setdefault(int(r["id1"]), []).append((float(r["position_x"]), float(r["position_y"]), int(r["map"]), int(r["zoneId"])))
        pts = [p for p in self._spawns.get(entry, []) if p[2] == mapid and (not zones or p[3] in zones or p[3] == 0)]
        return pts

    # -- spawns, graveyards, the start -----------------------------------------------------------
    def build_spawn(self, d):
        """More of someone already made (SPAWNS): a chapter's people at another chapter's hub, or the game's
        creatures in the murlocs' phase."""
        if "object" in d:
            return self.build_object_spawn(d)
        chapter, ref = d["chapter"], d["npc"]
        where = f"{chapter}: a spawn of {ref}"
        entry = self.creature(ref, chapter, where)
        if not entry:
            return
        npc = self.npcs.get(self.qualify(chapter, ref)) if isinstance(ref, str) else None
        name = npc["name"] if npc else self.world_creatures.get(ref, {}).get("name", str(ref))
        pts = self.points(d["at"], chapter, where)
        phase = self.phase_of(dict(d, key=where), chapter, pts)
        guids = list(self.spawn(entry, pts, d.get("facing"), phase, d.get("wander", 0.0),
                                d.get("respawn", 120), f"mod-murloc-naga: {name}"))
        state = d.get("state")
        if state is None and npc:
            state = next((b[2] for b in npc.get("idle", []) if b[0] == "state" and b[1] == "self"), None)
        if state is not None:
            sid = K.STATES.get(state, state) if isinstance(state, str) else state
            if isinstance(sid, str):
                self.err(where, f"no state {state!r}")
                return
            for g in guids:
                self.row("creature_addon", guid=g, emote=sid)

    def build_object_spawn(self, d):
        chapter, ref = d["chapter"], d["object"]
        where = f"{chapter}: a spawn of {ref}"
        key = self.qualify(chapter, ref)
        if key not in self.go_id:
            self.err(where, f"no object {ref!r}")
            return
        obj = self.objects[key]
        kind = obj.get("kind", "doodad")
        pts = self.points(d["at"], chapter, where)
        phase = self.phase_of(dict(d, key=where), chapter, pts)
        for i, (m, x, y, z) in enumerate(pts):
            self.object_row(self.go_id[key], (m, x, y, z), d.get("facing", (i * 1.1) % 6.28), phase,
                            d.get("respawn", 30 if kind in ("loot", "use") else 0), obj["name"])

    def object_row(self, entry, pt, o, phase, respawn, name):
        m, x, y, z = pt
        guid = self.next_go_spawn
        self.next_go_spawn += 1
        if guid > self.P.GO_SPAWN_END:
            raise StoryError("too many object spawns")
        self.row("gameobject", guid=guid, id=entry, map=m, zoneId=0, areaId=0, spawnMask=1, phaseMask=phase,
                 position_x=round(x, 2), position_y=round(y, 2), position_z=round(z, 2), orientation=round(o, 3),
                 rotation0=0, rotation1=0, rotation2=round(math.sin(o / 2), 8), rotation3=round(math.cos(o / 2), 8),
                 spawntimesecs=respawn, animprogress=100, state=1, Comment=f"mod-murloc-naga: {name}")

    def build_graveyards(self):
        """The tribe's graveyards (GRAVEYARDS): where a murloc whose story isn't done wakes as a ghost (the
        nearest on its map whose phase rule holds: src/MurlocNaga.cpp), each with the game's spirit healer."""
        out = []
        for n, d in enumerate(self.graveyards):
            gid = self.P.GRAVEYARD_BASE + n
            if gid > self.P.GRAVEYARD_END:
                raise StoryError("too many graveyards")
            chapter = d["chapter"]
            where = f"{chapter}: graveyard {n + 1}"
            m, x, y, z = self.point(d["at"], chapter, where)
            self.row("game_graveyard", ID=gid, Map=m, x=round(x, 2), y=round(y, 2), z=round(z + 0.5, 2),
                     Comment=f"mod-murloc-naga: {d.get('name', 'the tribe')}")
            rule, frm, until = d.get("phase", "always"), 0, 0
            if rule != "always":
                kind, quest = rule[:2]
                qid = self.quest(quest, chapter, where)
                if kind == "from":
                    frm = qid
                elif kind == "until":
                    until = qid
                elif kind == "between":
                    frm, until = qid, self.quest(rule[2], chapter, where)
                else:
                    self.err(where, f"a graveyard's phase is from, until or between quests, not {kind!r}")
            out.append(dict(id=gid, map=m, x=round(x, 2), y=round(y, 2), z=round(z + 0.5, 2), from_quest=frm, until_quest=until))
            pts = self.points(d.get("healer", d["at"]), chapter, where)
            phase = self.phase_of(dict(d, key=where), chapter, pts)
            list(self.spawn(K.SPIRIT_HEALER, pts, d.get("facing", 0.0), phase,
                            comment="mod-murloc-naga: the tribe's spirit healer"))
        self.tables["_graveyards"] = out

    def build_start(self):
        """Where a murloc starts (the first chapter's `start`), and the chapters whose zones show the murlocs'
        phase alone (no world: `alone_until` a quest's reward)."""
        for ch in self.chapters:
            c = ch["CHAPTER"]
            if c.get("start") and "_start" not in self.tables:
                m, x, y, z = self.point(c["start"], c["key"], "the start")
                self.tables["_start"] = dict(map=m, zone=c.get("zones", [0])[0], x=round(x, 2), y=round(y, 2),
                                             z=round(z + 0.5, 2), o=c.get("start_facing", 0.0))
            if c.get("alone_until"):
                self.tables.setdefault("_alone", []).append((tuple(c.get("zones", [])), self.quest(c["alone_until"], c["key"], c["key"])))

    def alone_quest(self, zone):
        return next((q for zones, q in self.tables.get("_alone", []) if zone in zones), 0)

    # -- memories (the naga's: bible 2.2, 18.3) ------------------------------------------------------
    def build_memories(self):
        """Each memory (MEMORIES): its stage (where one arrives, the ground it covers), the pool one wakes at,
        its quests (those with memory="<key>"), what the module reads of them (naga_story_memories), and the
        singer's way back in. Checked: its people and things on its stage, memories sharing a bit far apart,
        no choices in a memory's quests (history doesn't change)."""
        quests_of = {}
        for qk, q in self.quests.items():
            if not q.get("memory"):
                if q.get("wake"):
                    self.err(qk, "wake=True on a quest that isn't a memory's (memory=\"<key>\")")
                continue
            mk = self.qualify(q["chapter"], q["memory"])
            if mk not in self.memories:
                self.err(qk, f"no memory {q['memory']!r}")
                continue
            quests_of.setdefault(mk, []).append(qk)
            if q.get("path") or q.get("exclusive") or q.get("prev_any"):
                self.err(qk, "a memory's quest has no choices (no path, exclusive or prev_any: history doesn't change)")
        out, stages = [], []
        for key, d in self.memories.items():
            ch, where = d["chapter"], key
            for need in ("name", "stage", "pool", "bit"):
                if not d.get(need):
                    self.err(where, f"a memory needs {need}=")
            if not all(d.get(n) for n in ("name", "stage", "pool", "bit")):
                continue
            m, x, y, z = self.point(d["stage"], ch, where)
            cm, cx, cy, _ = self.point(d.get("centre", d["stage"]), ch, where)
            pm, px, py, pz = self.point(d["pool"], ch, where)
            radius = d.get("radius", 120)
            if cm != m or math.hypot(x - cx, y - cy) > radius:
                self.err(where, "its stage (where one arrives) is outside its own ground (centre, radius)")
            if pm == cm and math.hypot(px - cx, py - cy) <= radius:
                self.err(where, "its pool is on its own ground: one who wakes there would be inside it")
            for who, (sm, sx, sy, _) in self.memory_spawns.get(key, []):
                if sm != cm or math.hypot(sx - cx, sy - cy) > radius - 5:
                    self.err(who, f"stands in memory {key} but off its ground ({radius} yards around its centre): "
                                  "reaching it would wake the player")
            qs = quests_of.get(key, [])
            if not qs:
                self.err(where, "a memory with no quests (memory=\"<key>\" on the quests lived inside it)")
            stages.append((key, d.get("bit"), cm, cx, cy))
            out.append(dict(spell=self.memory_spell[key], bit=self.memory_bit(key), map=m, x=round(x, 2), y=round(y, 2),
                            z=round(z + 0.5, 2), o=d.get("facing", 0.0), cx=round(cx, 2), cy=round(cy, 2), radius=radius,
                            pool_map=pm, px=round(px, 2), py=round(py, 2), pz=round(pz + 0.5, 2), po=d.get("pool_facing", 0.0),
                            quests=",".join(str(self.quest_id[q]) for q in qs),
                            wakes=",".join(str(self.quest_id[q]) for q in qs if self.quests[q].get("wake"))))
            if d.get("singer"):                 # back in, while one of its quests is in the log (a waking one unfinished)
                sk = self.qualify(ch, d["singer"])
                if sk not in self.npc_id:
                    self.err(where, f"no singer {d['singer']!r}")
                    continue
                e = self.npc_id[sk]
                opt = self.next_option.get(e, 0)
                self.next_option[e] = opt + 1
                self.row("gossip_menu_option", MenuID=e, OptionID=opt, OptionIcon=0,
                         OptionText=self.option_words(d.get("again", "Sing it again. Let me go back."), self.language(self.npcs[sk])),
                         OptionType=1, OptionNpcFlag=1)
                for n, q in enumerate(qs):
                    # (one done inside but not handed in, its ender in the memory, needs the way back in too; one that
                    # wakes the player when it's done is handed in in the present)
                    self.condition(15, e, opt, 9, self.quest_id[q], else_group=n)
                    if self.quests[q].get("wake"):
                        self.condition(15, e, opt, 28, self.quest_id[q], negative=1, else_group=n)
                self.smart(e, 0, EV_GOSSIP_SELECT, (e, opt), [(A_CLOSE_GOSSIP, (), (T_INVOKER,)),
                                                             (A_ADD_AURA, (self.memory_spell[key],), (T_INVOKER,))])
        for i, (ka, ba, ma, xa, ya) in enumerate(stages):
            for kb, bb, mb, xb, yb in stages[i + 1:]:
                if ba == bb and ma == mb and math.hypot(xa - xb, ya - yb) < 500:
                    self.err(ka, f"shares bit {ba} with memory {kb} {math.hypot(xa - xb, ya - yb):.0f} yards away "
                                 "(memories sharing a bit stand 500 yards apart at least: one would be seen from the other)")
        self.tables["_memories"] = out

    # -- phases --------------------------------------------------------------------------------
    def build_phases(self):
        """A story phase is a spell whose aura is its bit, on one of the race in the chapter's zones by the quest
        rule it was made for (spell_area); while reliving a memory (the naga's), none of them (the marker)."""
        P = self.P
        spell = P.PHASE_SPELL_BASE
        if len(self.phase_bits) > P.PHASE_SPELL_END - P.PHASE_SPELL_BASE + 1:
            raise StoryError(f"{len(self.phase_bits)} story phases: more than the {P.PHASE_SPELL_END - P.PHASE_SPELL_BASE + 1} spells kept for them")
        marker = -P.race_spells["marker"] if P.race_spells else 0
        for (zones, (kind, quest)), bit in sorted(self.phase_bits.items(), key=lambda kv: kv[1]):
            self.phase_spells.append((spell, bit))
            for zone in zones:
                if kind == "from":
                    self.row("spell_area", spell=spell, area=zone, quest_start=quest, quest_end=0, aura_spell=marker,
                             racemask=P.RACE_BIT, gender=2, autocast=1, quest_start_status=REWARDED, quest_end_status=0)
                elif kind == "until":
                    self.row("spell_area", spell=spell, area=zone, quest_start=0, quest_end=quest, aura_spell=marker,
                             racemask=P.RACE_BIT, gender=2, autocast=1, quest_start_status=0, quest_end_status=NOT_REWARDED)
                elif kind == "between":
                    self.row("spell_area", spell=spell, area=zone, quest_start=quest[0], quest_end=quest[1], aura_spell=marker,
                             racemask=P.RACE_BIT, gender=2, autocast=1, quest_start_status=REWARDED, quest_end_status=NOT_REWARDED)
                elif kind == "during":
                    self.row("spell_area", spell=spell, area=zone, quest_start=quest, quest_end=0, aura_spell=marker,
                             racemask=P.RACE_BIT, gender=2, autocast=1, quest_start_status=IN_LOG, quest_end_status=0)
                else:
                    raise StoryError(f"no phase rule {kind!r}")
            spell += 1
        if P.race_spells:
            self.build_race_phases(marker)
        elif self.race_phase_spell:
            for zone in sorted(self.zones - set(P.world_owned_areas)):        # (those: tools/build_data.py's)
                self.row("spell_area", spell=self.race_phase_spell, area=zone, quest_start=self.alone_quest(zone), quest_end=0,
                         aura_spell=0, racemask=P.RACE_BIT, gender=2, autocast=1, quest_start_status=64, quest_end_status=11)

    def build_race_phases(self, marker):
        """The naga's own phase in their story's zones (bible 18.2): alone (theirs, no world) where a chapter says
        so until its alone_until quest's reward, the world's and theirs after it (and anywhere else); the world's and
        theirs in the profile's world areas from the first login (Valormok). None of it while reliving a memory."""
        P, rs = self.P, self.P.race_spells
        self.phase_spells.append((rs["alone"], P.RACE_PHASE))
        self.phase_spells.append((rs["world"], 1 | P.RACE_PHASE))

        def row(spell, area, start=0, start_status=0, end=0, end_status=0):
            self.row("spell_area", spell=spell, area=area, quest_start=start, quest_end=end, aura_spell=marker, racemask=P.RACE_BIT,
                     gender=2, autocast=1, quest_start_status=start_status, quest_end_status=end_status)
        for zone in sorted(self.zones):
            q = self.alone_quest(zone)
            if q:
                row(rs["alone"], zone, end=q, end_status=NOT_REWARDED)
                row(rs["world"], zone, start=q, start_status=REWARDED)
            else:
                row(rs["world"], zone)
        parent = {r[0]: r[2] for r in self.D("AreaTable").rows}
        for area in P.world_areas:
            if parent.get(area) in self.zones:
                row(rs["world"], area)


# -- two stories, one world ---------------------------------------------------------------------------

def bits_by_zone(story):
    """{zone: bits} a story's people carry there for its story phases: what another story's compile must keep
    clear of (Story(reserved=...))."""
    out = {}
    for (zones, _), bit in story.phase_bits.items():
        for z in zones:
            out.setdefault(z, set()).add(bit)
    return out


def check_apart(stories, reach=100):
    """Neither story's people and things are seen by the other's race (the murlocs' chapter 10 and the naga's
    whole story share Azshara): for every spawn of each story, in every zone within [reach] yards of it (seen across
    a border too), no bit a player of another story's race can hold there (the world's, its race phase, its story
    phases there, its memories'). [] when apart, else what isn't."""
    seen = {}

    def zones_near(st, m, x, y):
        k = (m, int(x // 25), int(y // 25))
        if k not in seen:
            pts = [(x, y)] + [(x + reach * math.cos(i * math.pi / 4), y + reach * math.sin(i * math.pi / 4)) for i in range(8)]
            seen[k] = {z for z in (st.zone_of(m, px, py) for px, py in pts) if z}
        return seen[k]
    holdable = []
    for st in stories:
        by_zone = {}
        for (zones, _), bit in st.phase_bits.items():
            for z in zones:
                by_zone.setdefault(z, set()).add(bit)
        mem_zones = set()
        for mem in st.tables.get("_memories", []):
            mem_zones |= zones_near(st, mem["map"], mem["cx"], mem["cy"])
        holdable.append((by_zone, mem_zones, 1 | st.P.RACE_PHASE, sum(set(st.P.MEMORY_BITS.values()))))
    problems = []
    for i, st in enumerate(stories):
        for j, other in enumerate(stories):
            if i == j:
                continue
            by_zone, mem_zones, base, memory = holdable[j]
            for table in ("creature", "gameobject"):
                for r in st.tables.get(table, []):
                    for z in zones_near(st, r["map"], r["position_x"], r["position_y"]):
                        mask = base | sum(by_zone.get(z, ())) | (memory if z in mem_zones else 0)
                        if r["phaseMask"] & mask:
                            problems.append(f"{st.P.who}' {table} {r['guid']} ({r.get('Comment', '')}) carries phase "
                                            f"{r['phaseMask'] & mask} that {other.P.who} hold in zone {z}")
    return problems


# -- lint ---------------------------------------------------------------------------------------------

ACTING = {"say", "yell", "whisper", "emote", "state", "move", "jump", "give", "take", "summon", "visual", "cast", "sound", "music",
          "aura", "unaura", "teleport", "object", "follow", "face", "relive", "wake", "morph", "scale", "sky"}


def model_of(story, display):
    """The model path a look draws (CreatureDisplayInfo -> CreatureModelData), lower case, or ""."""
    if not hasattr(story, "_model_paths"):
        md = story.D("CreatureModelData")
        paths = {r[0]: md.s(r[2]).lower() for r in md.rows}
        story._model_paths = {r[0]: paths.get(r[1], "") for r in story.D("CreatureDisplayInfo").rows}
    return story._model_paths.get(display, "")


def is_naga_model(path):
    return any(w in path for w in ("\\naga", "ladyvashj", "\\siren"))


def lint(story):
    """What a chapter does that the story's rules frown on (show, don't tell; the right looks for
    acting), as warnings: [(where, what)]."""
    out = []
    emoting = {f"murloc_{n}" for n in K.TRIBE_SKINS}
    no_emote_murlocs = {"oracle", "tidehunter", "seer", "coastrunner", "netter", "warrior", "hunter", "raider",
                        "flagglemurk", "murkdeep", "fry_green", "fry_blue", "fry_pink", "fry_purple"}
    actors = set()
    for key, q in story.quests.items():
        for kind in ("accept", "complete"):
            beats = q.get(kind, [])
            acts = [b for b in beats if b[0] in ACTING]
            if len(acts) < 2:
                out.append((key, f"its {kind} scene does little ({len(acts)} beats that show something)"))
            for b in beats:
                if b[0] in ("say", "yell", "emote", "state") and len(b) > 1 and b[1] not in ("self", "player"):
                    actors.add(story.qualify(q["chapter"], b[1]))
            if any(b[0] in ("emote", "state") or (b[0] in ("say", "yell") and len(b) > 3 and b[3]) for b in beats):
                for who in (q.get("giver"), q.get("ender", q.get("giver"))):
                    if isinstance(who, str) and not who.startswith("object:"):
                        actors.add(story.qualify(q["chapter"], who))
        if not q.get("poi") and not q.get("kill") and (q.get("items") or q.get("explore") or q.get("use")):
            out.append((key, "no map marker (poi) for what it asks"))
        if len(q.get("text", "")) < 60:
            out.append((key, "a short quest text"))
    for key in actors:
        d = story.npcs.get(key)
        if d and isinstance(d.get("look"), str) and d["look"] in no_emote_murlocs and d.get("look") not in emoting:
            out.append((key, f"acts, but its look ({d['look']}) plays no emotes: a murloc_<skin> look does"))
    for ch in story.chapters:
        lo, hi = ch["CHAPTER"].get("levels", (1, 80))
        for q in ch.get("QUESTS", []):
            if not lo <= q["level"] <= hi + 1:
                out.append((f"{ch['CHAPTER']['key']}:{q['key']}", f"level {q['level']} outside the chapter's {lo}-{hi}"))
    out += lint_naga_models(story)
    out += lint_lasting_looks(story)
    if not story.P.translate:
        out += lint_languages(story)
    return out


def scenes(story):
    """[(where, owner key, beats)]: every scene of the story's, with whose it is (a quest's giver or ender, an
    NPC's idle, watch and at_health, an object's), for the lints."""
    out = []
    for key, q in story.quests.items():
        for kind, who in (("accept", q.get("giver")), ("complete", q.get("ender", q.get("giver"))),
                          ("interact_beats", (q.get("interact") or [[None]])[0][0])):
            if q.get(kind):
                out.append((f"{key} ({kind})", story.qualify(q["chapter"], who) if isinstance(who, str) else None, q[kind]))
        for z in q.get("quiz", []):
            for a in z.get("answers", []):
                if len(a) > 2:
                    out.append((f"{key} (quiz)", story.qualify(q["chapter"], z.get("npc", "")), a[2]))
    for key, d in story.npcs.items():
        idle = [b for b in d.get("idle", []) if b[0] != "every"]
        idle += [x for b in d.get("idle", []) if b[0] == "every" for x in b[2]]
        for beats in (idle, (d.get("watch") or (0, []))[1], (d.get("at_health") or (0, []))[1]):
            if beats:
                out.append((key, key, beats))
    return out


def lint_naga_models(story):
    """A naga plays only what its model has (bible 4.2): an emote or a pose it hasn't is no gesture at all."""
    out = []
    for where, owner, beats in scenes(story):
        for b in beats:
            if b[0] not in ("emote", "state", "say", "yell", "whisper") or len(b) < 3:
                continue
            who = owner if b[1] in ("self", None) else story.qualify(where.split(":")[0], b[1]) if isinstance(b[1], str) else None
            d = story.npcs.get(who) if who else None
            if not d or d.get("display_extra"):
                continue
            look = d.get("look", "warrior")
            display = story.P.LOOKS.get(look) if isinstance(look, str) else look
            if not display or not is_naga_model(model_of(story, display)):
                continue
            name = b[2] if b[0] in ("emote", "state") else (b[3] if len(b) > 3 else None)
            if not name or not isinstance(name, str):
                continue
            playable = "\\naga_\\" in model_of(story, display) and "character\\" in model_of(story, display)
            allowed = ((PLAYABLE_NAGA_STATES if playable else NAGA_STATES) if b[0] == "state"
                       else (PLAYABLE_NAGA_EMOTES if playable else NAGA_EMOTES))
            if name not in allowed:
                out.append((where, f"{d['name']} (a naga model) can't {b[0]} {name!r}: it stands still (it plays "
                                   f"{', '.join(sorted(allowed))})"))
    return out


def lint_lasting_looks(story):
    """A look put on the player that lasts until it's taken off (the Glowy spells): the player keeps it after the scene
    unless the same scene takes it off again ("unaura")."""
    if not hasattr(story, "_lasting"):
        spells, durations = story.D("Spell"), story.D("SpellDuration")
        forever = {r[0] for r in durations.rows if r[1] in (-1, 4294967295)}
        story._lasting = {r[0] for r in spells.rows if r[40] in forever}
    out = []
    for where, owner, beats in scenes(story):
        for i, b in enumerate(beats):
            if b[0] == "visual" and len(b) > 2 and b[1] == "player" and isinstance(b[2], int) and b[2] in story._lasting:
                if not any(x[0] == "unaura" and len(x) > 2 and x[1] == "player" and x[2] == b[2] for x in beats[i + 1:]):
                    out.append((where, f"the visual {b[2]} lasts until it's taken off: the player keeps it (a later "
                                       f"(\"unaura\", \"player\", {b[2]}) in the scene, or a look that ends)"))
    return out


def lint_languages(story):
    """In a story whose people speak readably (the naga's), a land-walker given no language speaks Nazja: a night
    elf, a goblin or a blood elf must say which tongue (bible 4.1; a memory's people are understood anyway)."""
    out = []
    for key, d in story.npcs.items():
        if d.get("language") or (isinstance(d.get("phase"), tuple) and d["phase"][0] == "memory"):
            continue
        look = d.get("look", "warrior")
        display = story.P.LOOKS.get(look) if isinstance(look, str) else look
        path = model_of(story, display) if display else ""
        if d.get("display_extra") or (path.startswith("character\\") and "naga_" not in path):
            out.append((key, f"{d['name']} looks like one of a playable race but has no language= (it speaks Nazja, readable)"))
    return out


# -- SQL ---------------------------------------------------------------------------------------------

def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"
    if isinstance(v, float):
        return repr(round(v, 6))
    return str(v)


def deletes(P=MURLOC):
    """[(table, where)]: every row of the story's ranges (and only its own: the other story's, the world SQL's and
    other modules' stay), taken out before its rows go in."""
    kept = sorted(P.KEPT_ENTRIES.values())

    def entries(col, base=P.NPC_BASE, end=P.NPC_END):
        out = f"`{col}` BETWEEN {base} AND {end}"
        return out + (f" OR `{col}` IN ({', '.join(map(str, kept))})" if kept else "")
    lists = f" OR (`source_type` = 9 AND `entryorguid` BETWEEN {P.NPC_BASE * 1000} AND {P.NPC_END * 1000 + 999})"
    lists += f" OR (`source_type` = 9 AND `entryorguid` BETWEEN {P.GO_BASE * 1000} AND {P.GO_END * 1000 + 999})"
    lists += "".join(f" OR (`source_type` = 9 AND `entryorguid` BETWEEN {e * 1000} AND {e * 1000 + 999})" for e in kept)
    smart = f"(`source_type` = 0 AND ({entries('entryorguid')})) OR (`source_type` = 1 AND `entryorguid` BETWEEN {P.GO_BASE} AND {P.GO_END})"
    gos = f"`entry` BETWEEN {P.GO_BASE} AND {P.GO_END}"
    go_loot = f"`Entry` BETWEEN {P.GO_BASE} AND {P.GO_END}"
    loot = f"`Comment` = '{P.LOOT_COMMENT}'"
    if P.OLD_GO_BASE is not None:               # (the murlocs' objects' first range, and their timed lists' first ids)
        smart = (f"(`source_type` = 0 AND `entryorguid` BETWEEN {P.NPC_BASE} AND {P.NPC_END}) OR (`source_type` = 1 AND `entryorguid` "
                 f"BETWEEN {P.GO_BASE} AND {P.GO_END}) OR (`source_type` = 1 AND `entryorguid` BETWEEN {P.OLD_GO_BASE} AND {P.OLD_GO_END})"
                 f" OR (`source_type` = 9 AND `entryorguid` BETWEEN {P.NPC_BASE * 100} AND {P.OLD_GO_END * 100 + 99})")
        lists += f" OR (`source_type` = 9 AND `entryorguid` BETWEEN {P.OLD_GO_BASE * 1000} AND {P.OLD_GO_END * 1000 + 999})"
        gos += f" OR `entry` BETWEEN {P.OLD_GO_BASE} AND {P.OLD_GO_END}"
        go_loot += f" OR `Entry` BETWEEN {P.OLD_GO_BASE} AND {P.OLD_GO_END}"
    if P.CAMP_NPC_BASE is not None:             # ("mod-murloc-naga" alone was the naga camp's too, tools/build_data.py's)
        loot += f" OR (`Comment` = 'mod-murloc-naga' AND `Entry` NOT BETWEEN {P.CAMP_NPC_BASE} AND {P.CAMP_NPC_END})"
    if P.race_spells:
        spell_area = f"`spell` BETWEEN {min(P.race_spells.values())} AND {P.PHASE_SPELL_END}"
    else:                                       # (its race phase's rows outside the world SQL's areas: tools/build_data.py's)
        spell_area = (f"`spell` BETWEEN {P.PHASE_SPELL_BASE} AND {P.PHASE_SPELL_END} OR (`spell` = {P.race_phase_spell} AND `area` "
                      f"NOT IN ({', '.join(map(str, P.world_owned_areas))}))")
    out = [
        ("creature_template", entries("entry")),
        ("creature_template_model", entries("CreatureID")),
        ("creature_equip_template", entries("CreatureID")),
        ("creature_template_movement", entries("CreatureId")),
        ("creature_text", entries("CreatureID")),
        ("creature_addon", f"`guid` BETWEEN {P.SPAWN_BASE} AND {P.SPAWN_END}"),
        ("creature", f"`guid` BETWEEN {P.SPAWN_BASE} AND {P.SPAWN_END}"),
        ("smart_scripts", smart + lists),
        ("creature_template_addon", entries("entry")),
        ("game_graveyard", f"`ID` BETWEEN {P.GRAVEYARD_BASE} AND {P.GRAVEYARD_END}"),
        ("npc_text", entries("ID")),
        ("gossip_menu", entries("MenuID")),
        ("gossip_menu_option", entries("MenuID")),
        ("npc_vendor", entries("entry")),
        ("trainer_spell", f"`TrainerId` BETWEEN {P.TRAINER_BASE} AND {P.TRAINER_BASE + 999}"),
        ("trainer", f"`Id` BETWEEN {P.TRAINER_BASE} AND {P.TRAINER_BASE + 999}"),
        ("creature_default_trainer", entries("CreatureId")),
        ("gameobject_template", gos),
        ("gameobject", f"`guid` BETWEEN {P.GO_SPAWN_BASE} AND {P.GO_SPAWN_END}"),
        ("gameobject_loot_template", go_loot),
        ("creature_loot_template", loot),
        ("item_template", f"`entry` BETWEEN {P.ITEM_BASE} AND {P.ITEM_END}"),
        ("item_dbc", f"`ID` BETWEEN {P.ITEM_BASE} AND {P.ITEM_END}"),
        ("quest_template", f"`ID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("quest_template_addon", f"`ID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("quest_offer_reward", f"`ID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("quest_request_items", f"`ID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("quest_details", f"`ID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("creature_queststarter", f"`quest` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("creature_questender", f"`quest` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("gameobject_queststarter", f"`quest` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("gameobject_questender", f"`quest` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("quest_poi", f"`QuestID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("quest_poi_points", f"`QuestID` BETWEEN {P.QUEST_BASE} AND {P.QUEST_END}"),
        ("conditions", f"`Comment` = '{P.COMMENT}'"),
        ("spell_area", spell_area),
    ]
    if P.DISPLAY_BASE is not None:              # (its new looks: display_extra)
        out += [("creature_model_info", f"`DisplayID` BETWEEN {P.DISPLAY_BASE} AND {P.DISPLAY_END}"),
                ("creaturedisplayinfo_dbc", f"`ID` BETWEEN {P.DISPLAY_BASE} AND {P.DISPLAY_END}"),
                ("creaturedisplayinfoextra_dbc", f"`ID` BETWEEN {P.EXTRA_BASE} AND {P.EXTRA_END}")]
    return out


def sql(tables, phase_spells_sql="", P=MURLOC):
    """The SQL of [tables]: every row of the story's ranges taken out first, then put in."""
    T = P.tables
    out = [f"-- {P.title}",
           "-- Safe to run again: every row of its ranges is taken out first."]
    for table, where in deletes(P):
        out.append(f"DELETE FROM `{table}` WHERE {where};")
    for src in sorted(tables.get("_lootid", [])):
        out.append(f"UPDATE `creature_template` SET `lootid` = `entry` WHERE `entry` = {src} AND `lootid` = 0;")
    for tid, best in tables.get("_trainer_copy", []):
        out.append(f"INSERT INTO `trainer_spell` (`TrainerId`, `SpellId`, `MoneyCost`, `ReqSkillLine`, `ReqSkillRank`, `ReqAbility1`, "
                   f"`ReqAbility2`, `ReqAbility3`, `ReqLevel`) SELECT {tid}, `SpellId`, `MoneyCost`, `ReqSkillLine`, `ReqSkillRank`, "
                   f"`ReqAbility1`, `ReqAbility2`, `ReqAbility3`, `ReqLevel` FROM `trainer_spell` WHERE `TrainerId` = {best};")
    for table, rows in tables.items():
        if table.startswith("_") or not rows:
            continue
        cols = []
        for r in rows:
            for c in r:
                if c not in cols:
                    cols.append(c)
        for i in range(0, len(rows), 300):
            body = ",\n".join("(" + ", ".join(q(r.get(c, DEFAULTS.get((table, c), 0))) for c in cols) + ")" for r in rows[i:i + 300])
            out.append(f"INSERT INTO `{table}` ({', '.join(f'`{c}`' for c in cols)}) VALUES\n{body};")
    if phase_spells_sql:
        out.append(phase_spells_sql)
    if tables.get("_new_looks"):
        out.append("-- Its new looks' sizes: those of the game's look of a person of the same race and sex.")
        for display, template in tables["_new_looks"]:
            out.append(f"REPLACE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) "
                       f"SELECT {display}, `BoundingRadius`, `CombatReach`, `Gender`, 0 FROM `creature_model_info` WHERE `DisplayID` = {template};")
    if tables.get("_model_info"):
        out.append("-- Looks the game has no size for (a rowboat's): a size, so the server knows them.")
        out.append("INSERT IGNORE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES "
                   + ", ".join(f"({d}, 1.0, 1.5, 2)" for d in tables["_model_info"]) + ";")
    out.append("-- Spells the story's quests teach (the module, src/MurlocNaga.cpp, teaches them as each is handed in).")
    out.append(f"CREATE TABLE IF NOT EXISTS `{T['learn']}` (`quest` INT UNSIGNED NOT NULL, `spell` INT UNSIGNED NOT NULL, "
               "PRIMARY KEY (`quest`, `spell`));")
    out.append(f"DELETE FROM `{T['learn']}`;")
    if tables.get("_learn"):
        out.append(f"INSERT INTO `{T['learn']}` (`quest`, `spell`) VALUES "
                   + ", ".join(f"({qq}, {sp})" for qq, sp in tables["_learn"]) + ";")
    out.append(f"-- The story's graveyards, as the module (src/MurlocNaga.cpp) chooses them for {P.who} whose story isn't done.")
    out.append(f"CREATE TABLE IF NOT EXISTS `{T['graveyards']}` (`id` INT UNSIGNED NOT NULL PRIMARY KEY, `map` INT UNSIGNED NOT NULL, "
               "`x` FLOAT NOT NULL, `y` FLOAT NOT NULL, `z` FLOAT NOT NULL, `from_quest` INT UNSIGNED NOT NULL, `until_quest` INT UNSIGNED NOT NULL);")
    out.append(f"DELETE FROM `{T['graveyards']}`;")
    if tables.get("_graveyards"):
        out.append(f"INSERT INTO `{T['graveyards']}` (`id`, `map`, `x`, `y`, `z`, `from_quest`, `until_quest`) VALUES "
                   + ", ".join(f"({g['id']}, {g['map']}, {g['x']}, {g['y']}, {g['z']}, {g['from_quest']}, {g['until_quest']})"
                               for g in tables["_graveyards"]) + ";")
    out.append("-- What one carries puts an aura on (the module, every second): an item in the bags, its aura.")
    out.append(f"CREATE TABLE IF NOT EXISTS `{T['carry']}` (`item` INT UNSIGNED NOT NULL, `aura` INT UNSIGNED NOT NULL, "
               "PRIMARY KEY (`item`, `aura`));")
    out.append(f"DELETE FROM `{T['carry']}`;")
    if tables.get("_carry"):
        out.append(f"INSERT INTO `{T['carry']}` (`item`, `aura`) VALUES " + ", ".join(f"({i}, {a})" for i, a in tables["_carry"]) + ";")
    if T.get("memories"):
        out.append("-- The memories (the module: going in and out, death and logout inside, leaving their ground): each its aura, its\n"
                   "-- phase bit, where one arrives, its ground (a centre and a radius), the pool one wakes at, its quests (the\n"
                   "-- current one's objectives start again after a death inside) and those whose completion wakes one.")
        out.append(f"CREATE TABLE IF NOT EXISTS `{T['memories']}` (`spell` INT UNSIGNED NOT NULL PRIMARY KEY, `bit` INT UNSIGNED NOT NULL, "
                   "`map` INT UNSIGNED NOT NULL, `x` FLOAT NOT NULL, `y` FLOAT NOT NULL, `z` FLOAT NOT NULL, `o` FLOAT NOT NULL, "
                   "`cx` FLOAT NOT NULL, `cy` FLOAT NOT NULL, `radius` FLOAT NOT NULL, `pool_map` INT UNSIGNED NOT NULL, "
                   "`px` FLOAT NOT NULL, `py` FLOAT NOT NULL, `pz` FLOAT NOT NULL, `po` FLOAT NOT NULL, "
                   "`quests` VARCHAR(255) NOT NULL, `wakes` VARCHAR(255) NOT NULL);")
        out.append(f"DELETE FROM `{T['memories']}`;")
        if tables.get("_memories"):
            out.append(f"INSERT INTO `{T['memories']}` (`spell`, `bit`, `map`, `x`, `y`, `z`, `o`, `cx`, `cy`, `radius`, `pool_map`, `px`, `py`, "
                       "`pz`, `po`, `quests`, `wakes`) VALUES\n"
                       + ",\n".join(f"({m['spell']}, {m['bit']}, {m['map']}, {m['x']}, {m['y']}, {m['z']}, {m['o']}, {m['cx']}, {m['cy']}, "
                                    f"{m['radius']}, {m['pool_map']}, {m['px']}, {m['py']}, {m['pz']}, {m['po']}, {q(m['quests'])}, {q(m['wakes'])})"
                                    for m in tables["_memories"]) + ";")
    story = tables.get("_story")
    if story:
        out.append(f"-- What the module (src/MurlocNaga.cpp) reads of the story: its quests' range, and the last quest, which opens\n"
                   f"-- the other quests to {P.who}" + (" (and the memories' marker and fade spells)." if P.race_spells else "."))
        out.append(f"CREATE TABLE IF NOT EXISTS `{T['story']}` (`name` VARCHAR(32) NOT NULL PRIMARY KEY, `value` INT UNSIGNED NOT NULL);")
        out.append(f"REPLACE INTO `{T['story']}` (`name`, `value`) VALUES "
                   + ", ".join(f"({q(k)}, {v})" for k, v in sorted(story.items())) + ";")
    return "\n".join(out) + "\n"


DEFAULTS = {
    ("creature_template", "subname"): "", ("creature_template", "ScriptName"): "", ("creature_template", "AIName"): "",
    ("item_template", "description"): "", ("quest_template", "ObjectiveText1"): "", ("quest_template", "ObjectiveText2"): "",
    ("quest_template", "ObjectiveText3"): "", ("quest_template", "ObjectiveText4"): "", ("creature", "Comment"): "",
    ("gameobject", "Comment"): "", ("gameobject_template", "name"): "", ("npc_text", "text0_0"): "", ("npc_text", "text0_1"): "",
    ("gameobject_template", "AIName"): "", ("creature_template", "AIName"): "",
    ("item_template", "spellcooldown_1"): -1, ("item_template", "spellcategorycooldown_1"): -1,
    **{("creature_template_movement", c): None for c in ("Ground", "Swim", "Flight", "Rooted", "Chase", "Random", "InteractionPauseTimer")},
}
